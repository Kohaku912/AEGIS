"""Read-only AGORA connectivity and verified-reply evidence probe."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _reply_evidence(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"available": False, "verified_reply_count": 0, "latest_reply_id": ""}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        items = payload.get("items", []) if isinstance(payload, dict) else []
        verified = [
            item
            for item in items
            if isinstance(item, dict)
            and item.get("channel") == "agora"
            and item.get("status") == "replied"
            and str(item.get("reply_id") or "")
        ]
        verified.sort(key=lambda item: int(item.get("updated_at", 0) or 0), reverse=True)
        return {
            "available": True,
            "verified_reply_count": len(verified),
            "latest_reply_id": str(verified[0].get("reply_id") or "") if verified else "",
        }
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return {
            "available": False,
            "verified_reply_count": 0,
            "latest_reply_id": "",
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--report", required=True)
    parser.add_argument("--social-inbox", default="ai-server/data/social/social_inbox.json")
    parser.add_argument("--require-reply-id", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    _load_env((root / args.env_file).resolve())
    sys.path[:0] = [str(root / "ai-server" / "src"), str(root / "shared" / "python")]

    from aegis_ai.integrations.agora.agora_client import AgoraClient
    from aegis_ai.integrations.agora.agora_types import AgoraAccount, AgoraFetchResult

    started = time.monotonic()
    client = AgoraClient(timeout=15)
    account = client.get_me()
    mentions = client.get_mentions(limit=5)
    account_ok = isinstance(account, AgoraAccount)
    mentions_ok = isinstance(mentions, AgoraFetchResult)
    evidence = _reply_evidence((root / args.social_inbox).resolve())
    reply_ok = evidence["verified_reply_count"] > 0

    checks = [
        {
            "id": "agora_credentials",
            "status": "pass" if client.is_configured and account_ok else "fail",
            "evidence": {"configured": client.is_configured, "account_verified": account_ok},
            "error": account.get("error", "") if isinstance(account, dict) else "",
        },
        {
            "id": "agora_mentions_read",
            "status": "pass" if mentions_ok else "fail",
            "evidence": {
                "mention_count": len(mentions.posts) if mentions_ok else 0,
                "transport": "real_http",
            },
            "error": mentions.get("error", "") if isinstance(mentions, dict) else "",
        },
        {
            "id": "agora_verified_reply_id",
            "status": "pass" if reply_ok else "pending",
            "evidence": evidence,
            "error": "An explicitly approved AGORA reply has not produced a persisted post ID." if not reply_ok else "",
        },
    ]
    transport_ok = account_ok and mentions_ok
    if not transport_ok:
        status = "fail"
    elif args.require_reply_id and not reply_ok:
        status = "fail"
    elif reply_ok:
        status = "pass"
    else:
        status = "partial"
    report = {
        "id": "agora_real",
        "name": "AGORA real transport and reply evidence",
        "status": status,
        "generated_at": int(time.time() * 1000),
        "duration_ms": int((time.monotonic() - started) * 1000),
        "checks": checks,
        "safety": "Read-only probe. It never creates or approves a social post.",
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 1 if status == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
