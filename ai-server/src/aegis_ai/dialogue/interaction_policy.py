"""Interaction Policy — decides when/how to communicate with the user."""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum

from aegis_ai.user_model.user_model_types import UserModel


class InteractionDecisionType(Enum):
    SPEAK_NOW = "speak_now"
    NOTIFY_NOW = "notify_now"
    QUEUE_FOR_LATER = "queue_for_later"
    SUPPRESS = "suppress"
    REQUIRE_USER_CONFIRMATION = "require_user_confirmation"
    SUMMARIZE_LATER = "summarize_later"


class NotificationChannel(Enum):
    CHAT = "chat"
    VOICE = "voice"
    NOTIFICATION = "notification"
    UI = "ui"
    NONE = "none"


class NotificationUrgency(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class InteractionDecision:
    decision: InteractionDecisionType
    channel: NotificationChannel
    urgency: NotificationUrgency
    reason: str
    cooldown_seconds: int = 0
    user_facing_message: str = ""
    internal_note: str = ""
    created_at: int = 0


@dataclass
class InteractionContext:
    user_model: UserModel | None = None
    is_user_busy: bool = False
    pending_approval_count: int = 0
    recent_notification_count: int = 0
    last_notification_ago_seconds: int = 0
    source_desire: str = ""
    frustration: float = 0.0
    category: str = ""
    urgency: str = "normal"
    is_safety_related: bool = False
    is_approval_required: bool = False


_CATEGORY_COOLDOWN: dict[str, int] = {
    "safety_warning": 0,
    "approval_required": 60,
    "task_failed": 300,
    "verification_failed": 300,
    "recovery_needs_user": 120,
    "task_completed": 600,
    "self_development_review": 1800,
    "daily_summary": 3600,
    "maintenance_suggestion": 7200,
    "learning_report": 3600,
    "social_check_in": 14400,
    "curiosity_suggestion": 7200,
}


class InteractionPolicy:
    """Decides when and how to communicate with the user."""

    def __init__(self) -> None:
        self._suppressed_categories: dict[str, int] = {}

    def evaluate(self, ctx: InteractionContext) -> InteractionDecision:
        now = int(time.time() * 1000)
        user = ctx.user_model

        if ctx.is_safety_related or ctx.urgency == "critical":
            return InteractionDecision(
                decision=InteractionDecisionType.SPEAK_NOW,
                channel=NotificationChannel.CHAT,
                urgency=NotificationUrgency.CRITICAL,
                reason="Safety-critical: must inform user immediately.",
                user_facing_message="",
                created_at=now,
            )

        if user and user.focus_mode and not ctx.is_approval_required:
            return InteractionDecision(
                decision=InteractionDecisionType.QUEUE_FOR_LATER,
                channel=NotificationChannel.NONE,
                urgency=NotificationUrgency.LOW,
                reason="User is in focus mode.",
                cooldown_seconds=1800,
                created_at=now,
            )

        if user and user.is_quiet_now(time.localtime().tm_hour):
            if ctx.category not in ("safety_warning", "approval_required"):
                return InteractionDecision(
                    decision=InteractionDecisionType.QUEUE_FOR_LATER,
                    channel=NotificationChannel.NONE,
                    urgency=NotificationUrgency.LOW,
                    reason="Quiet hours active.",
                    cooldown_seconds=3600,
                    created_at=now,
                )

        if ctx.category == "social_check_in":
            cooldown = _CATEGORY_COOLDOWN.get("social_check_in", 14400)
            if ctx.last_notification_ago_seconds < cooldown:
                return InteractionDecision(
                    decision=InteractionDecisionType.SUPPRESS,
                    channel=NotificationChannel.NONE,
                    urgency=NotificationUrgency.LOW,
                    reason="Social check-in cooldown active.",
                    cooldown_seconds=cooldown - ctx.last_notification_ago_seconds,
                    created_at=now,
                )
            if user and user.annoyance_score > 0.6:
                return InteractionDecision(
                    decision=InteractionDecisionType.SUPPRESS,
                    channel=NotificationChannel.NONE,
                    urgency=NotificationUrgency.LOW,
                    reason="User annoyance score high — suppressing social notification.",
                    created_at=now,
                )

        if ctx.category in self._suppressed_categories:
            until = self._suppressed_categories[ctx.category]
            if now < until:
                return InteractionDecision(
                    decision=InteractionDecisionType.SUPPRESS,
                    channel=NotificationChannel.NONE,
                    urgency=NotificationUrgency.LOW,
                    reason=f"Category '{ctx.category}' suppressed until {until}.",
                    created_at=now,
                )

        if user and not user.allows_proactive(ctx.category):
            return InteractionDecision(
                decision=InteractionDecisionType.SUPPRESS,
                channel=NotificationChannel.NONE,
                urgency=NotificationUrgency.LOW,
                reason=f"Category '{ctx.category}' not allowed by user preferences.",
                created_at=now,
            )

        if ctx.is_approval_required:
            if ctx.pending_approval_count > 3:
                return InteractionDecision(
                    decision=InteractionDecisionType.SUMMARIZE_LATER,
                    channel=NotificationChannel.UI,
                    urgency=NotificationUrgency.NORMAL,
                    reason="Too many pending approvals — will summarize.",
                    created_at=now,
                )
            return InteractionDecision(
                decision=InteractionDecisionType.NOTIFY_NOW,
                channel=NotificationChannel.CHAT,
                urgency=NotificationUrgency.HIGH,
                reason="Approval required.",
                created_at=now,
            )

        if ctx.category == "task_completed":
            if ctx.recent_notification_count > 5:
                return InteractionDecision(
                    decision=InteractionDecisionType.SUMMARIZE_LATER,
                    channel=NotificationChannel.NONE,
                    urgency=NotificationUrgency.LOW,
                    reason="Too many recent notifications — will summarize.",
                    created_at=now,
                )

        cooldown = _CATEGORY_COOLDOWN.get(ctx.category, 300)
        if ctx.last_notification_ago_seconds < cooldown:
            return InteractionDecision(
                decision=InteractionDecisionType.QUEUE_FOR_LATER,
                channel=NotificationChannel.NONE,
                urgency=NotificationUrgency.LOW,
                reason=f"Category '{ctx.category}' cooldown active.",
                cooldown_seconds=cooldown - ctx.last_notification_ago_seconds,
                created_at=now,
            )

        return InteractionDecision(
            decision=InteractionDecisionType.NOTIFY_NOW,
            channel=NotificationChannel.CHAT,
            urgency=NotificationUrgency.NORMAL,
            reason="Normal notification.",
            created_at=now,
        )

    def suppress_category(self, category: str, until_ms: int) -> None:
        self._suppressed_categories[category] = until_ms

    def record_rejection(self, category: str) -> None:
        now = int(time.time() * 1000)
        cooldown = _CATEGORY_COOLDOWN.get(category, 300) * 3
        self._suppressed_categories[category] = now + cooldown * 1000
