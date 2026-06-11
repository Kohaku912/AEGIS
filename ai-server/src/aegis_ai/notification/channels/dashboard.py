"""Dashboard notification channel — stores notifications for Dashboard display."""

from __future__ import annotations

from typing import Any

from aegis_ai.notification.models import Notification


class DashboardNotificationChannel:
    """Stores notifications for display on the Dashboard.

    Usage:
        channel = DashboardNotificationChannel()
        channel.send(notification)
        recent = channel.get_recent(20)
    """

    def __init__(self) -> None:
        self._notifications: list[dict[str, Any]] = []

    def send(self, notification: Notification) -> None:
        """Store a notification for Dashboard display."""
        self._notifications.append({
            "notification_id": notification.notification_id,
            "type": notification.type.name,
            "title": notification.title,
            "body": notification.body,
            "severity": notification.severity.name,
            "source": notification.source,
            "related_approval_id": notification.related_approval_id,
            "requires_user_action": notification.requires_user_action,
            "created_at_ms": notification.created_at_ms,
        })

    def get_recent(self, n: int = 20) -> list[dict[str, Any]]:
        """Get recent notifications."""
        return self._notifications[-n:]

    def get_all(self) -> list[dict[str, Any]]:
        """Get all notifications."""
        return list(self._notifications)

    def clear(self) -> None:
        """Clear all notifications."""
        self._notifications.clear()
