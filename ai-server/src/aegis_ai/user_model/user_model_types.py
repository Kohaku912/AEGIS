"""User Model types — user preferences and interaction patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DetailLevel(Enum):
    BRIEF = "brief"
    NORMAL = "normal"
    DETAILED = "detailed"


class AutonomyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NotificationPreference(Enum):
    MINIMAL = "minimal"
    NORMAL = "normal"
    PROACTIVE = "proactive"


class ApprovalStrictness(Enum):
    STRICT = "strict"
    NORMAL = "normal"
    RELAXED = "relaxed"


@dataclass
class QuietHours:
    enabled: bool = False
    start_hour: int = 22
    end_hour: int = 8
    timezone: str = "Asia/Tokyo"


@dataclass
class UserModel:
    user_id: str = "default"
    preferred_language: str = "ja"
    preferred_tone: str = "polite"
    detail_level: DetailLevel = DetailLevel.NORMAL
    autonomy_level: AutonomyLevel = AutonomyLevel.MEDIUM
    notification_preference: NotificationPreference = NotificationPreference.NORMAL
    approval_strictness: ApprovalStrictness = ApprovalStrictness.NORMAL
    quiet_hours: QuietHours = field(default_factory=QuietHours)
    focus_mode: bool = False
    allowed_proactive_categories: list[str] = field(default_factory=lambda: [
        "approval_required", "task_failed", "safety_warning", "recovery_needs_user",
    ])
    disallowed_proactive_categories: list[str] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)
    work_patterns: dict[str, Any] = field(default_factory=dict)
    permission_scopes: dict[str, Any] = field(default_factory=dict)
    common_apps: list[str] = field(default_factory=list)
    notification_conditions: dict[str, Any] = field(default_factory=dict)
    writing_style: dict[str, Any] = field(default_factory=dict)
    long_term_goals: list[dict[str, Any]] = field(default_factory=list)
    preferred_report_format: str = "text"
    last_interaction_at: int = 0
    last_user_feedback: str = ""
    trust_score: float = 0.5
    annoyance_score: float = 0.0
    created_at: int = 0
    updated_at: int = 0

    def is_quiet_now(self, now_hour: int) -> bool:
        if not self.quiet_hours.enabled:
            return False
        start = self.quiet_hours.start_hour
        end = self.quiet_hours.end_hour
        if start > end:
            return now_hour >= start or now_hour < end
        return start <= now_hour < end

    def allows_proactive(self, category: str) -> bool:
        if category in self.disallowed_proactive_categories:
            return False
        if self.notification_preference == NotificationPreference.MINIMAL:
            return category in ("approval_required", "safety_warning")
        if category in self.allowed_proactive_categories:
            return True
        return self.notification_preference == NotificationPreference.PROACTIVE

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "preferred_language": self.preferred_language,
            "preferred_tone": self.preferred_tone,
            "detail_level": self.detail_level.value,
            "autonomy_level": self.autonomy_level.value,
            "notification_preference": self.notification_preference.value,
            "approval_strictness": self.approval_strictness.value,
            "quiet_hours": {
                "enabled": self.quiet_hours.enabled,
                "start_hour": self.quiet_hours.start_hour,
                "end_hour": self.quiet_hours.end_hour,
            },
            "focus_mode": self.focus_mode,
            "allowed_proactive_categories": self.allowed_proactive_categories,
            "disallowed_proactive_categories": self.disallowed_proactive_categories,
            "preferences": self.preferences,
            "work_patterns": self.work_patterns,
            "permission_scopes": self.permission_scopes,
            "common_apps": self.common_apps,
            "notification_conditions": self.notification_conditions,
            "writing_style": self.writing_style,
            "long_term_goals": self.long_term_goals,
            "preferred_report_format": self.preferred_report_format,
            "trust_score": self.trust_score,
            "annoyance_score": self.annoyance_score,
        }
