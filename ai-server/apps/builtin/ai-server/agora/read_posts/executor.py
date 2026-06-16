from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from aegis_ai.integrations.agora.agora_types import AgoraAccount, AgoraCursor, AgoraFetchResult
from aegis_ai.integrations.agora.agora_client import AgoraClient
from aegis_ai.memory.memory_ingest import sync_agora_posts_to_memory


def _load_env_files() -> None:
    """Load AGORA_TOKEN from common local env files without printing secrets."""
    for path in (ROOT / ".env", ROOT.parent / ".env"):
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key and key not in os.environ:
                os.environ[key] = value.strip().strip('"').strip("'")


def _error_payload(message: str, **extra: Any) -> dict[str, Any]:
    payload = {"ok": False, "error": message}
    payload.update(extra)
    return payload


def _cursor_value(cursor: AgoraCursor | dict[str, Any]) -> int:
    if isinstance(cursor, AgoraCursor):
        return int(cursor.last_read_post_id)
    return 0


def _fetch_posts(client: AgoraClient, since_id: int, limit: int) -> AgoraFetchResult | dict[str, Any]:
    result = client.list_posts(since_id=since_id, limit=limit)
    if isinstance(result, dict) and result.get("error"):
        return result
    return result


def _read_posts(client: AgoraClient, since_id: int, limit: int) -> tuple[AgoraFetchResult | dict[str, Any], dict[str, Any]]:
    cursor = client.get_cursor()
    remote_cursor = _cursor_value(cursor)
    read_since_id = since_id if since_id > 0 else remote_cursor

    meta: dict[str, Any] = {
        "cursor": remote_cursor,
        "read_since_id": read_since_id,
        "limit": limit,
        "fallback_recent": False,
    }

    result = _fetch_posts(client, read_since_id, limit)
    if isinstance(result, dict):
        return result, meta

    # If the server cursor already points at the newest post, the normal unread
    # query is empty. In that case, return a recent window so "read posts" still
    # gives the LLM actual current AGORA context instead of a misleading blank.
    if since_id == 0 and not result.posts and remote_cursor > 0:
        fallback_since_id = max(0, remote_cursor - limit)
        fallback = _fetch_posts(client, fallback_since_id, limit)
        if isinstance(fallback, dict):
            return fallback, meta
        if fallback.posts:
            meta.update({
                "read_since_id": fallback_since_id,
                "fallback_recent": True,
                "fallback_reason": "No unread posts after cursor; returned recent posts near cursor.",
            })
            return fallback, meta

    return result, meta


def run(payload: dict[str, Any]) -> dict[str, Any]:
    _load_env_files()

    since_id = int(payload.get("since_id", 0) or 0)
    limit = int(payload.get("limit", 20) or 20)
    limit = max(1, min(limit, 200))

    if not os.environ.get("AGORA_TOKEN"):
        return _error_payload("AGORA_TOKEN not set")

    client = AgoraClient()
    me = client.get_me()
    if isinstance(me, dict) and me.get("error"):
        return _error_payload(str(me.get("message", me.get("error", "AGORA account error"))), account_error=me)

    result, meta = _read_posts(client, since_id, limit)
    if isinstance(result, dict):
        return _error_payload(str(result.get("message", result.get("error", "AGORA read failed"))), agora_error=result)

    posts = result.posts
    if posts and result.max_post_id > 0:
        # Cursor updates are monotonic on AGORA. This is safe for normal reads
        # and harmless for explicit historical reads when the cursor is already newer.
        client.update_cursor(result.max_post_id)

    sync_result = sync_agora_posts_to_memory(
        posts=posts,
        data_dir=str(ROOT / "data"),
        self_author_ids={me.id} if isinstance(me, AgoraAccount) and me.id else set(),
        self_author_names={me.name} if isinstance(me, AgoraAccount) and me.name else set(),
    )

    payload_out = sync_result.to_dict()
    payload_out.update({
        "account": {
            "id": me.id if isinstance(me, AgoraAccount) else 0,
            "name": me.name if isinstance(me, AgoraAccount) else "",
        },
        "cursor": meta["cursor"],
        "read_since_id": meta["read_since_id"],
        "limit": limit,
        "fallback_recent": meta["fallback_recent"],
        "fetched_count": len(posts),
        "max_post_id": result.max_post_id,
    })
    if meta.get("fallback_reason"):
        payload_out["fallback_reason"] = meta["fallback_reason"]
        if payload_out.get("message") == "AGORA: No new posts." and posts:
            payload_out["message"] = payload_out["summary"]
            payload_out["result"] = payload_out["summary"]
    return payload_out


def main() -> None:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        print(json.dumps(run(data), ensure_ascii=False))
    except Exception as exc:
        print(json.dumps(_error_payload(str(exc)), ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
