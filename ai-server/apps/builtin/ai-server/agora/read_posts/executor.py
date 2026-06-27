from __future__ import annotations

import json
import os
import sys
import time
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


def _fetch_all_posts(client: AgoraClient, since_id: int, max_posts: int) -> AgoraFetchResult | dict[str, Any]:
    all_posts = []
    current_since_id = since_id
    page_size = min(max_posts, 50)

    while len(all_posts) < max_posts:
        remaining = max_posts - len(all_posts)
        fetch_limit = min(page_size, remaining)

        result = client.list_posts(since_id=current_since_id, limit=fetch_limit)
        if isinstance(result, dict) and result.get("error"):
            return result

        posts = result.posts
        if not posts:
            break

        all_posts.extend(posts)
        current_since_id = max(p.id for p in posts)

        if len(posts) < fetch_limit:
            break

    max_id = max((p.id for p in all_posts), default=0)
    return AgoraFetchResult(
        posts=all_posts,
        max_post_id=max_id,
        has_new_posts=len(all_posts) > 0,
        fetched_at=int(time.time() * 1000),
    )


def _read_posts(client: AgoraClient, since_id: int, limit: int) -> tuple[AgoraFetchResult | dict[str, Any], dict[str, Any]]:
    cursor = client.get_cursor()
    if isinstance(cursor, dict) and cursor.get("error"):
        return cursor, {
            "cursor": 0,
            "read_since_id": since_id,
            "limit": limit,
            "fallback_recent": False,
            "read_mode": "history" if since_id > 0 else "unread",
        }
    remote_cursor = _cursor_value(cursor)
    read_since_id = since_id if since_id > 0 else remote_cursor

    meta: dict[str, Any] = {
        "cursor": remote_cursor,
        "read_since_id": read_since_id,
        "limit": limit,
        "fallback_recent": False,
        "read_mode": "history" if since_id > 0 else "unread",
    }

    result = _fetch_all_posts(client, read_since_id, limit)
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
    cursor_after = meta["cursor"]
    if since_id == 0 and posts and result.max_post_id > 0:
        updated_cursor = client.update_cursor(result.max_post_id)
        if isinstance(updated_cursor, dict) and updated_cursor.get("error"):
            return _error_payload(
                str(updated_cursor.get("message", updated_cursor.get("error", "AGORA cursor update failed"))),
                cursor_error=updated_cursor,
            )
        cursor_after = _cursor_value(updated_cursor) or result.max_post_id

    if posts:
        sync_result = sync_agora_posts_to_memory(
            posts=posts,
            data_dir=str(ROOT / "data"),
            self_author_ids={me.id} if isinstance(me, AgoraAccount) and me.id else set(),
            self_author_names={me.name} if isinstance(me, AgoraAccount) and me.name else set(),
        )
        payload_out = sync_result.to_dict()
    else:
        payload_out = {
            "ok": True,
            "message": "AGORA: No new posts.",
            "result": "AGORA: No new posts.",
            "summary": "AGORA: No new posts.",
            "posts": [],
        }

    payload_out.update({
        "account": {
            "id": me.id if isinstance(me, AgoraAccount) else 0,
            "name": me.name if isinstance(me, AgoraAccount) else "",
        },
        "cursor": meta["cursor"],
        "read_since_id": meta["read_since_id"],
        "limit": limit,
        "fallback_recent": meta["fallback_recent"],
        "read_mode": meta["read_mode"],
        "unread_count": len(posts) if meta["read_mode"] == "unread" else 0,
        "fetched_count": len(posts),
        "max_post_id": result.max_post_id,
        "cursor_after": cursor_after,
    })
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
