"""Persistent social inbox contracts shared by channel adapters."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class SocialInboxStatus(StrEnum):
    UNTRIAGED = "untriaged"
    NEEDS_REPLY = "needs_reply"
    DRAFTED = "drafted"
    AWAITING_APPROVAL = "awaiting_approval"
    REPLIED = "replied"
    ACKNOWLEDGED = "acknowledged"
    SKIPPED = "skipped"
    FAILED = "failed"


TERMINAL_SOCIAL_STATUSES = {
    SocialInboxStatus.REPLIED,
    SocialInboxStatus.ACKNOWLEDGED,
    SocialInboxStatus.SKIPPED,
    SocialInboxStatus.FAILED,
}


@dataclass
class SocialInboxItem:
    item_id: str
    channel: str
    external_message_id: str
    thread_id: str = ""
    author: str = ""
    body: str = ""
    received_at: int = 0
    relationship: dict[str, Any] = field(default_factory=dict)
    directed_to_aegis: bool = False
    mentions_user: bool = False
    question_detected: bool = False
    reply_expected: bool = False
    relevance: float = 0.0
    urgency: float = 0.0
    sentiment: str = ""
    conversation_context: dict[str, Any] = field(default_factory=dict)
    status: SocialInboxStatus = SocialInboxStatus.UNTRIAGED
    decision: str = ""
    decision_reason: str = ""
    draft_id: str = ""
    draft_body: str = ""
    approval_id: str = ""
    reply_id: str = ""
    updated_at: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SocialInboxItem:
        payload = dict(data)
        try:
            payload["status"] = SocialInboxStatus(str(payload.get("status") or "untriaged"))
        except ValueError:
            payload["status"] = SocialInboxStatus.FAILED
        known = cls.__dataclass_fields__
        return cls(**{key: value for key, value in payload.items() if key in known})
