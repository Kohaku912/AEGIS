"""Manifest-backed delivery adapters for SocialManager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from aegis_ai.social.models import SocialInboxItem


class SocialReplyAdapter(Protocol):
    """Translate a social draft to one canonical capability request."""

    channel: str
    available: bool

    def capability_id(self, item: SocialInboxItem) -> str: ...

    def build_arguments(self, item: SocialInboxItem) -> dict[str, Any]: ...

    def verified_delivery_id(self, output: dict[str, Any]) -> str: ...


@dataclass(frozen=True)
class AgoraReplyAdapter:
    channel: str = "agora"
    available: bool = True

    def capability_id(self, item: SocialInboxItem) -> str:
        del item
        return "ai-server.agora.post"

    def build_arguments(self, item: SocialInboxItem) -> dict[str, Any]:
        return {
            "body": item.draft_body,
            "reply_to": int(item.external_message_id),
            "thread_id": int(item.thread_id or 1),
        }

    def verified_delivery_id(self, output: dict[str, Any]) -> str:
        post = output.get("post") if isinstance(output.get("post"), dict) else {}
        return str(post.get("id") or output.get("post_id") or "")


@dataclass(frozen=True)
class UnavailableReplyAdapter:
    """Describe a production-disabled channel without pretending delivery works."""

    channel: str
    reason: str
    available: bool = False

    def capability_id(self, item: SocialInboxItem) -> str:
        del item
        return ""

    def build_arguments(self, item: SocialInboxItem) -> dict[str, Any]:
        del item
        return {}

    def verified_delivery_id(self, output: dict[str, Any]) -> str:
        del output
        return ""
