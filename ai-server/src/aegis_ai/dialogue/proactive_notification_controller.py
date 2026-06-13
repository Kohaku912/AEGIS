"""Proactive Notification Controller — controls when AEGIS initiates contact."""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.dialogue.notification")


class NotificationCategory(Enum):
    APPROVAL_REQUIRED = "approval_required"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    VERIFICATION_FAILED = "verification_failed"
    RECOVERY_NEEDS_USER = "recovery_needs_user"
    SAFETY_WARNING = "safety_warning"
    SELF_DEVELOPMENT_REVIEW = "self_development_review"
    DAILY_SUMMARY = "daily_summary"
    MAINTENANCE_SUGGESTION = "maintenance_suggestion"
    LEARNING_REPORT = "learning_report"
    SOCIAL_CHECK_IN = "social_check_in"
    CURIOSITY_SUGGESTION = "curiosity_suggestion"


class UserResponse(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IGNORED = "ignored"
    MODIFIED = "modified"
    UNKNOWN = "unknown"


@dataclass
class NotificationRecord:
    notification_id: str = ""
    category: str = ""
    task_id: str = ""
    source: str = ""
    source_desire: str = ""
    frustration: float = 0.0
    urgency: str = "normal"
    message_summary: str = ""
    channel: str = "chat"
    decision: str = ""
    sent_at: int = 0
    user_response: str = "unknown"
    response_at: int = 0
    cooldown_until: int = 0
    annoyance_delta: float = 0.0
    trust_delta: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "notification_id": self.notification_id,
            "category": self.category,
            "task_id": self.task_id,
            "source": self.source,
            "source_desire": self.source_desire,
            "frustration": self.frustration,
            "urgency": self.urgency,
            "message_summary": self.message_summary[:200],
            "channel": self.channel,
            "decision": self.decision,
            "sent_at": self.sent_at,
            "user_response": self.user_response,
            "response_at": self.response_at,
            "cooldown_until": self.cooldown_until,
        }


_CATEGORY_COOLDOWN_SECONDS: dict[str, int] = {
    "approval_required": 60,
    "task_completed": 600,
    "task_failed": 300,
    "verification_failed": 300,
    "recovery_needs_user": 120,
    "safety_warning": 0,
    "self_development_review": 1800,
    "daily_summary": 3600,
    "maintenance_suggestion": 7200,
    "learning_report": 3600,
    "social_check_in": 14400,
    "curiosity_suggestion": 7200,
}


class ProactiveNotificationController:
    """Controls when AEGIS can proactively contact the user."""

    def __init__(self, data_dir: str = "data/notifications") -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._records: list[NotificationRecord] = []
        self._cooldowns: dict[str, int] = {}
        self._load()

    def should_notify(
        self,
        category: str,
        source: str = "system",
        source_desire: str = "",
        urgency: str = "normal",
    ) -> tuple[bool, str]:
        now = int(time.time() * 1000)

        if category == "safety_warning":
            return True, "Safety warnings always pass."

        cd_until = self._cooldowns.get(category, 0)
        if now < cd_until:
            return False, f"Cooldown until {cd_until}."

        if category == "social_check_in":
            recent = self._count_recent(category, 14400)
            if recent > 0:
                return False, "Social check-in already sent recently."
            if source_desire == "social_connection":
                self._cooldowns[category] = now + _CATEGORY_COOLDOWN_SECONDS[category] * 1000
                return True, "Social connection desire — but with strong cooldown."

        recent = self._count_recent(category, 300)
        if recent > 3:
            return False, "Too many recent notifications in this category."

        return True, "OK"

    def record_notification(self, record: NotificationRecord) -> None:
        if not record.notification_id:
            record.notification_id = f"notif_{uuid.uuid4().hex[:8]}"
        if not record.sent_at:
            record.sent_at = int(time.time() * 1000)
        self._records.append(record)
        base_cd = _CATEGORY_COOLDOWN_SECONDS.get(record.category, 300)
        self._cooldowns[record.category] = record.sent_at + base_cd * 1000
        self._save()

    def record_user_response(
        self,
        notification_id: str,
        response: str,
    ) -> None:
        now = int(time.time() * 1000)
        for rec in self._records:
            if rec.notification_id == notification_id:
                rec.user_response = response
                rec.response_at = now
                if response == "rejected":
                    base_cd = _CATEGORY_COOLDOWN_SECONDS.get(rec.category, 300)
                    rec.cooldown_until = now + base_cd * 3 * 1000
                    self._cooldowns[rec.category] = rec.cooldown_until
                elif response == "ignored":
                    base_cd = _CATEGORY_COOLDOWN_SECONDS.get(rec.category, 300)
                    rec.cooldown_until = now + base_cd * 2 * 1000
                    self._cooldowns[rec.category] = rec.cooldown_until
                self._save()
                return

    def get_recent_records(self, limit: int = 20) -> list[NotificationRecord]:
        return self._records[-limit:]

    def _count_recent(self, category: str, window_seconds: int) -> int:
        cutoff = int(time.time() * 1000) - window_seconds * 1000
        return sum(
            1 for r in self._records
            if r.category == category and r.sent_at > cutoff
        )

    def _state_path(self) -> Path:
        return self._data_dir / "notifications.json"

    def _save(self) -> None:
        data = {
            "records": [r.to_dict() for r in self._records[-200:]],
            "cooldowns": self._cooldowns,
        }
        try:
            with open(self._state_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("Failed to save notifications: %s", exc)

    def _load(self) -> None:
        path = self._state_path()
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for d in data.get("records", []):
                self._records.append(NotificationRecord(**d))
            self._cooldowns = data.get("cooldowns", {})
            logger.info("Loaded %d notification records", len(self._records))
        except Exception as exc:
            logger.warning("Failed to load notifications: %s", exc)
