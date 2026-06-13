"""AGORA poller — autonomous AGORA reading for LLM-driven desire fulfillment."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from aegis_ai.integrations.agora.agora_service import AgoraService
from aegis_ai.integrations.agora.agora_types import (
    AgoraAccount,
    AgoraCursor,
    AgoraFetchResult,
    AgoraPost,
    AgoraTaskDetection,
)
from aegis_schema.models import Capability, RiskLevel, ServerType

logger = logging.getLogger("aegis_ai.integrations.agora.poller")


@dataclass
class AgoraPollResult:
    poll_id: str = ""
    success: bool = False
    new_posts: int = 0
    new_mentions: int = 0
    tasks_detected: int = 0
    cursor_updated: bool = False
    summary: str = ""
    posts: list[AgoraPost] = field(default_factory=list)
    mentions: list[AgoraPost] = field(default_factory=list)
    tasks: list[AgoraTaskDetection] = field(default_factory=list)
    error: str = ""
    duration_ms: float = 0.0
    fetched_at: int = 0


@dataclass
class AgoraState:
    me: AgoraAccount = field(default_factory=AgoraAccount)
    last_cursor: int = 0
    last_seen_post_id: int = 0
    last_fetched_post_id: int = 0
    unread_count: int = 0
    recent_posts_summary: str = ""
    recent_mentions_summary: str = ""
    pending_reply_candidates: list[int] = field(default_factory=list)
    last_post_created_by_aegis: int = 0
    last_observation_at: int = 0
    confidence: float = 1.0
    staleness: str = "fresh"

    def to_context_string(self, max_chars: int = 500) -> str:
        parts = [f"AGORA State (staleness={self.staleness}):"]
        if self.me.name:
            parts.append(f"  Account: {self.me.name} (id={self.me.id})")
        parts.append(f"  Cursor: {self.last_cursor}, Last seen: {self.last_seen_post_id}")
        if self.unread_count > 0:
            parts.append(f"  Unread: {self.unread_count}")
        if self.recent_posts_summary:
            parts.append(f"  Recent: {self.recent_posts_summary[:200]}")
        if self.recent_mentions_summary:
            parts.append(f"  Mentions: {self.recent_mentions_summary[:200]}")
        if self.pending_reply_candidates:
            parts.append(f"  Pending replies: {self.pending_reply_candidates}")
        result = "\n".join(parts)
        return result[:max_chars]

    def to_dict(self) -> dict[str, Any]:
        return {
            "me_id": self.me.id,
            "me_name": self.me.name,
            "last_cursor": self.last_cursor,
            "last_seen_post_id": self.last_seen_post_id,
            "last_fetched_post_id": self.last_fetched_post_id,
            "unread_count": self.unread_count,
            "recent_posts_summary": self.recent_posts_summary,
            "recent_mentions_summary": self.recent_mentions_summary,
            "pending_reply_candidates": self.pending_reply_candidates,
            "last_post_created_by_aegis": self.last_post_created_by_aegis,
            "last_observation_at": self.last_observation_at,
            "confidence": self.confidence,
            "staleness": self.staleness,
        }


_POLL_COOLDOWN_SECONDS = 300
_last_poll_time: float = 0.0


class AgoraPoller:
    """Polls AGORA for new posts, detects tasks, updates state."""

    def __init__(self, service: AgoraService | None = None) -> None:
        self._service = service or AgoraService()
        self._state = AgoraState()
        self._my_account_id: int = 0
        self._seen_post_ids: set[int] = set()

    @property
    def state(self) -> AgoraState:
        return self._state

    @property
    def service(self) -> AgoraService:
        return self._service

    @property
    def is_configured(self) -> bool:
        return self._service.is_configured

    def poll_once(self, dry_run: bool = False) -> AgoraPollResult:
        global _last_poll_time
        now = time.time()
        if now - _last_poll_time < _POLL_COOLDOWN_SECONDS and not dry_run:
            remaining = int(_POLL_COOLDOWN_SECONDS - (now - _last_poll_time))
            return AgoraPollResult(
                success=False,
                error=f"Poll cooldown active. Wait {remaining}s.",
                fetched_at=int(now * 1000),
            )

        start = time.perf_counter()
        poll_id = f"poll_{int(now)}"

        me_result = self._service.get_me()
        if isinstance(me_result, dict) and "error" in me_result:
            return AgoraPollResult(
                poll_id=poll_id,
                success=False,
                error=me_result.get("message", "Failed to get account."),
                fetched_at=int(now * 1000),
            )
        self._state.me = me_result
        self._my_account_id = me_result.id

        cursor_result = self._service.get_cursor()
        cursor_id = 0
        if isinstance(cursor_result, AgoraCursor):
            cursor_id = cursor_result.last_read_post_id
            self._state.last_cursor = cursor_id

        posts_result = self._service.read_posts(since_id=cursor_id, limit=50)
        if isinstance(posts_result, dict) and "error" in posts_result:
            return AgoraPollResult(
                poll_id=poll_id,
                success=False,
                error=posts_result.get("message", "Failed to read posts."),
                fetched_at=int(now * 1000),
            )

        new_posts = [p for p in posts_result.posts if p.id not in self._seen_post_ids]
        for p in new_posts:
            self._seen_post_ids.add(p.id)

        mentions_result = self._service.read_mentions(since_id=cursor_id, limit=20)
        new_mentions: list[AgoraPost] = []
        if isinstance(mentions_result, AgoraFetchResult):
            new_mentions = [p for p in mentions_result.posts if p.id not in self._seen_post_ids]

        tasks: list[AgoraTaskDetection] = []
        pending_replies: list[int] = []
        for post in new_posts:
            detection = self._service.detect_task(post, my_account_id=self._my_account_id)
            if detection.is_task_request:
                tasks.append(detection)
            if detection.requires_reply:
                pending_replies.append(post.id)

        max_id = posts_result.max_post_id if isinstance(posts_result, AgoraFetchResult) else 0
        if max_id > 0 and not dry_run:
            self._service.update_cursor(max_id)
            self._state.last_cursor = max_id

        self._state.last_seen_post_id = max(self._state.last_seen_post_id, max_id)
        self._state.last_fetched_post_id = max_id
        self._state.unread_count = len(new_posts)
        if isinstance(posts_result, AgoraFetchResult):
            self._state.recent_posts_summary = posts_result.summarize(max_posts=3)
        if isinstance(mentions_result, AgoraFetchResult):
            self._state.recent_mentions_summary = mentions_result.summarize(max_posts=3)
        self._state.pending_reply_candidates = pending_replies
        self._state.last_observation_at = int(now * 1000)
        self._state.staleness = "fresh"

        if not dry_run:
            _last_poll_time = now

        duration = (time.perf_counter() - start) * 1000
        summary_parts = [f"AGORA poll: {len(new_posts)} new, {len(new_mentions)} mentions, {len(tasks)} tasks."]
        if new_posts:
            summary_parts.append(posts_result.summarize(max_posts=3))

        return AgoraPollResult(
            poll_id=poll_id,
            success=True,
            new_posts=len(new_posts),
            new_mentions=len(new_mentions),
            tasks_detected=len(tasks),
            cursor_updated=max_id > 0 and not dry_run,
            summary="\n".join(summary_parts),
            posts=new_posts,
            mentions=new_mentions,
            tasks=tasks,
            duration_ms=duration,
            fetched_at=int(now * 1000),
        )

    def mark_stale(self) -> None:
        self._state.staleness = "stale"
        self._state.confidence = max(0.1, self._state.confidence - 0.2)

    def get_context_string(self, max_chars: int = 500) -> str:
        return self._state.to_context_string(max_chars=max_chars)


def register_agora_capabilities(registry: Any) -> None:
    """Register AGORA capabilities in the ToolRegistry."""
    caps = [
        Capability(
            id="ai.agora_get_me",
            name="AGORA Get Account",
            description="Get my AGORA account info",
            server_type=ServerType.AI,
            risk_level=RiskLevel.READ_ONLY,
            tags=["agora", "read"],
        ),
        Capability(
            id="ai.agora_read_posts",
            name="AGORA Read Posts",
            description="Read posts from AGORA",
            server_type=ServerType.AI,
            risk_level=RiskLevel.READ_ONLY,
            input_schema='{"since_id": {"type": "integer"}, "limit": {"type": "integer"}}',
            tags=["agora", "read"],
        ),
        Capability(
            id="ai.agora_read_thread_posts",
            name="AGORA Read Thread Posts",
            description="Read posts from a specific AGORA thread",
            server_type=ServerType.AI,
            risk_level=RiskLevel.READ_ONLY,
            input_schema=(
                '{"thread_id": {"type": "integer"}, '
                '"since_id": {"type": "integer"}, '
                '"limit": {"type": "integer"}}'
            ),
            tags=["agora", "read"],
        ),
        Capability(
            id="ai.agora_read_mentions",
            name="AGORA Read Mentions",
            description="Read mentions directed at AEGIS in AGORA",
            server_type=ServerType.AI,
            risk_level=RiskLevel.READ_ONLY,
            input_schema='{"since_id": {"type": "integer"}, "limit": {"type": "integer"}}',
            tags=["agora", "read"],
        ),
        Capability(
            id="ai.agora_get_cursor",
            name="AGORA Get Cursor",
            description="Get AGORA read cursor position",
            server_type=ServerType.AI,
            risk_level=RiskLevel.READ_ONLY,
            tags=["agora", "read"],
        ),
        Capability(
            id="ai.agora_update_cursor",
            name="AGORA Update Cursor",
            description="Update AGORA read cursor position",
            server_type=ServerType.AI,
            risk_level=RiskLevel.SAFE_ACTION,
            input_schema='{"last_read_post_id": {"type": "integer"}}',
            tags=["agora", "write"],
        ),
        Capability(
            id="ai.agora_draft_reply",
            name="AGORA Draft Reply",
            description="Draft a reply to an AGORA post (does not send)",
            server_type=ServerType.AI,
            risk_level=RiskLevel.READ_ONLY,
            input_schema='{"post_id": {"type": "integer"}, "context": {"type": "string"}}',
            tags=["agora", "draft"],
        ),
        Capability(
            id="ai.agora_create_post",
            name="AGORA Create Post",
            description="Post a message to AGORA (requires approval)",
            server_type=ServerType.AI,
            risk_level=RiskLevel.APPROVAL_REQUIRED,
            requires_approval=True,
            side_effects=["external_chat_send"],
            input_schema=(
                '{"thread_id": {"type": "integer"}, '
                '"body": {"type": "string"}, '
                '"reply_to": {"type": "integer"}}'
            ),
            tags=["agora", "send", "external"],
        ),
    ]
    for cap in caps:
        registry.register_capability(cap)
