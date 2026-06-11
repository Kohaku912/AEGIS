"""Notification Preferences — user-configurable notification settings."""

from __future__ import annotations

from typing import Any

from aegis_ai.notification.models import NotificationType


class NotificationPreferences:
    """Manages notification preferences.

    Usage:
        prefs = NotificationPreferences(settings_store=store)
        prefs.is_type_enabled(NotificationType.APPROVAL_REQUIRED)
    """

    # Default: all notification types enabled
    DEFAULT_ENABLED: dict[NotificationType, bool] = {
        NotificationType.APPROVAL_REQUIRED: True,
        NotificationType.SUPPORT_SUGGESTION: True,
        NotificationType.RESEARCH_COMPLETED: True,
        NotificationType.RESEARCH_FAILED: True,
        NotificationType.SERVER_DISCONNECTED: True,
        NotificationType.PERMISSION_MISSING: True,
        NotificationType.SELF_DEV_PROPOSAL: True,
        NotificationType.SELF_DEV_TEST_FAILED: True,
        NotificationType.ROOM_ALERT: True,
        NotificationType.SECURITY_ALERT: True,
        NotificationType.DAILY_BRIEFING: True,
        NotificationType.BUDGET_WARNING: True,
    }

    def __init__(self, settings_store: Any = None) -> None:
        self._settings = settings_store
        self._enabled: dict[str, bool] = {
            k.name: v for k, v in self.DEFAULT_ENABLED.items()
        }
        self._load_from_settings()

    def is_type_enabled(self, notification_type: NotificationType) -> bool:
        """Check if a notification type is enabled."""
        return self._enabled.get(notification_type.name, True)

    def set_enabled(self, notification_type: NotificationType, enabled: bool) -> None:
        """Enable or disable a notification type."""
        self._enabled[notification_type.name] = enabled

    def _load_from_settings(self) -> None:
        """Load preferences from settings store."""
        if not self._settings:
            return
        try:
            settings = self._settings.get()
            # Map settings to notification types
            if not settings.notifications.approval_notification_enabled:
                self._enabled[NotificationType.APPROVAL_REQUIRED.name] = False
            if not settings.notifications.support_suggestions_enabled:
                self._enabled[NotificationType.SUPPORT_SUGGESTION.name] = False
            if not settings.notifications.daily_briefing_notification:
                self._enabled[NotificationType.DAILY_BRIEFING.name] = False
            if not settings.notifications.error_notification:
                self._enabled[NotificationType.SERVER_DISCONNECTED.name] = False
                self._enabled[NotificationType.RESEARCH_FAILED.name] = False
                self._enabled[NotificationType.SELF_DEV_TEST_FAILED.name] = False
        except Exception:
            pass
