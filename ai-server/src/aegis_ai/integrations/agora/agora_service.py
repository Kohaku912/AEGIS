"""AGORA service — high-level AGORA operations with safety integration."""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from aegis_ai.integrations.agora.agora_client import AgoraClient
from aegis_ai.integrations.agora.agora_types import (
    AgoraAccount,
    AgoraCursor,
    AgoraFetchResult,
    AgoraPost,
    AgoraReplyDraft,
    AgoraTaskDetection,
)

logger = logging.getLogger("aegis_ai.integrations.agora.service")

_SECRET_PATTERN = re.compile(
    r"(api[_-]?key|token|password|secret|cookie|bearer|sk-[a-zA-Z0-9]{20,})",
    re.IGNORECASE,
)

_COOLDOWN_SECONDS = 60
_last_post_time: dict[str, float] = {}
_last_post_body: dict[str, str] = {}


def _has_secret(text: str) -> bool:
    return bool(_SECRET_PATTERN.search(text))


class AgoraService:
    """High-level AGORA operations with safety checks."""

    def __init__(self, client: AgoraClient | None = None) -> None:
        self._client = client or AgoraClient()

    @property
    def client(self) -> AgoraClient:
        return self._client

    @property
    def is_configured(self) -> bool:
        return self._client.is_configured

    def get_me(self) -> AgoraAccount | dict[str, Any]:
        return self._client.get_me()

    def read_posts(self, since_id: int = 0, limit: int = 50) -> AgoraFetchResult | dict[str, Any]:
        return self._client.list_posts(since_id=since_id, limit=limit)

    def read_thread_posts(
        self, thread_id: int = 1, since_id: int = 0, limit: int = 50,
    ) -> AgoraFetchResult | dict[str, Any]:
        return self._client.list_thread_posts(thread_id=thread_id, since_id=since_id, limit=limit)

    def read_mentions(self, since_id: int = 0, limit: int = 50) -> AgoraFetchResult | dict[str, Any]:
        return self._client.get_mentions(since_id=since_id, limit=limit)

    def get_cursor(self) -> AgoraCursor | dict[str, Any]:
        return self._client.get_cursor()

    def update_cursor(self, last_read_post_id: int) -> AgoraCursor | dict[str, Any]:
        return self._client.update_cursor(last_read_post_id=last_read_post_id)

    def create_post(
        self, thread_id: int = 1, body: str = "", reply_to: int | None = None,
    ) -> AgoraPost | dict[str, Any]:
        if _has_secret(body):
            return {"error": "blocked", "message": "Post body contains potential secrets. Posting denied."}

        if not body.strip():
            return {"error": "blocked", "message": "Post body is empty."}

        now = time.time()
        last_time = _last_post_time.get("global", 0)
        if now - last_time < _COOLDOWN_SECONDS:
            remaining = int(_COOLDOWN_SECONDS - (now - last_time))
            return {"error": "cooldown", "message": f"Post cooldown active. Wait {remaining}s."}

        last_body = _last_post_body.get("global", "")
        if last_body and last_body.strip() == body.strip():
            return {"error": "duplicate", "message": "Duplicate post body detected. Posting denied."}

        result = self._client.create_post(thread_id=thread_id, body=body, reply_to=reply_to)
        if isinstance(result, AgoraPost):
            _last_post_time["global"] = now
            _last_post_body["global"] = body
        return result

    def draft_reply(self, target_post: AgoraPost, context: str = "") -> AgoraReplyDraft:
        return AgoraReplyDraft(
            reply_body=f"[Draft reply to #{target_post.id}] {context}",
            reply_to=target_post.id,
            reason=f"Reply to {target_post.author.name}: {target_post.body[:50]}",
            risk_level="low",
            requires_approval=True,
        )

    def detect_task(self, post: AgoraPost, my_account_id: int = 0) -> AgoraTaskDetection:
        is_mentioned = any(m.id == my_account_id for m in post.mentions)
        body_lower = post.body.lower()
        is_calling = any(kw in body_lower for kw in ["aegis", "イージス", "eg"])
        is_question = "?" in post.body or "？" in post.body
        is_request = any(kw in body_lower for kw in ["して", "お願い", "確認", "テスト", "please", "check", "test"])
        is_greeting = any(kw in body_lower for kw in ["こんにちは", "hello", "hi", "おはよう", "good morning"])

        if post.author.id == my_account_id:
            return AgoraTaskDetection(is_task_request=False, reason="Own post.")

        if is_greeting and not is_request:
            return AgoraTaskDetection(
                is_task_request=False,
                requires_reply=True,
                confidence=0.3,
                reason="Greeting detected. Low priority reply.",
            )

        if is_mentioned or is_calling:
            confidence = 0.8 if is_request else 0.5
            urgency = "high" if is_request else "normal"
            return AgoraTaskDetection(
                is_task_request=is_request,
                task_title=f"AGORA request from {post.author.name}",
                task_description=post.body[:200],
                urgency=urgency,
                requires_reply=True,
                reply_to=post.id,
                confidence=confidence,
                reason=f"{'Mentioned' if is_mentioned else 'Called'} by {post.author.name}.",
            )

        if is_question:
            return AgoraTaskDetection(
                is_task_request=False,
                requires_reply=False,
                confidence=0.3,
                reason="Question detected but not directed at AEGIS.",
            )

        return AgoraTaskDetection(is_task_request=False, reason="Not a task request.")


def check_cooldown() -> dict[str, Any]:
    now = time.time()
    last_time = _last_post_time.get("global", 0)
    remaining = max(0, _COOLDOWN_SECONDS - (now - last_time))
    return {"cooldown_active": remaining > 0, "remaining_seconds": int(remaining)}
