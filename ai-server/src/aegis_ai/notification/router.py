"""Notification Router — routes notifications to appropriate channels."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from aegis_ai.notification.models import (
    DEFAULT_CHANNEL_MAP,
    Notification,
    NotificationChannel,
    NotificationSeverity,
    NotificationType,
)
from aegis_ai.notification.preferences import NotificationPreferences
from aegis_ai.notification.quiet_hours import QuietHoursManager

logger = logging.getLogger("aegis_ai.notification.router")


class NotificationRouter:
    """Routes notifications to appropriate channels.

    Usage:
        router = NotificationRouter(
            dashboard_channel=dashboard,
            web_chat_channel=web_chat,
            cli_channel=cli,
        )
        router.send(notification)
    """

    def __init__(
        self,
        dashboard_channel: Any = None,
        web_chat_channel: Any = None,
        cli_channel: Any = None,
        preferences: NotificationPreferences | None = None,
        quiet_hours: QuietHoursManager | None = None,
        audit_log: Any = None,
        digest: Any = None,
    ) -> None:
        self._channels: dict[NotificationChannel, Any] = {}
        if dashboard_channel:
            self._channels[NotificationChannel.DASHBOARD] = dashboard_channel
        if web_chat_channel:
            self._channels[NotificationChannel.WEB_CHAT] = web_chat_channel
        if cli_channel:
            self._channels[NotificationChannel.CLI] = cli_channel

        self._preferences = preferences or NotificationPreferences()
        self._quiet_hours = quiet_hours or QuietHoursManager()
        self._audit = audit_log
        self._digest = digest
        self._sent_count: dict[str, int] = {}  # type → count (spam prevention)

    def send(self, notification: Notification) -> bool:
        """Send a notification through appropriate channels.

        Returns True if at least one channel received the notification.
        """
        # Assign ID if not set
        if not notification.notification_id:
            notification.notification_id = f"notif_{uuid.uuid4().hex[:8]}"
        if not notification.created_at_ms:
            notification.created_at_ms = int(time.time() * 1000)

        # Check if notification type is enabled
        if not self._preferences.is_type_enabled(notification.type):
            logger.debug("Notification type %s disabled by preferences", notification.type.name)
            return False

        # Check quiet hours (only critical bypasses)
        if self._quiet_hours.is_quiet() and notification.severity != NotificationSeverity.CRITICAL:
            if self._digest:
                self._digest.defer(notification)
            logger.debug("Notification deferred (quiet hours): %s", notification.title)
            return False

        # Spam prevention
        type_key = notification.type.name
        if self._sent_count.get(type_key, 0) > 10:
            logger.warning("Notification spam detected for %s — suppressing", type_key)
            return False

        # Redact sensitive content for external channels
        notification = self._redact_if_needed(notification)

        # Route to channels
        channels = notification.channels or DEFAULT_CHANNEL_MAP.get(
            notification.severity, [NotificationChannel.DASHBOARD]
        )

        sent = False
        for channel in channels:
            handler = self._channels.get(channel)
            if handler:
                try:
                    handler.send(notification)
                    sent = True
                except Exception as e:
                    logger.error("Failed to send notification via %s: %s", channel.name, e)

        # Track count
        self._sent_count[type_key] = self._sent_count.get(type_key, 0) + 1

        # Audit
        if self._audit:
            self._audit.log_decision(
                "notification_sent", f"notification.{notification.type.name}", "SENT" if sent else "FAILED",
                detail={"title": notification.title, "severity": notification.severity.name},
            )

        return sent

    def _redact_if_needed(self, notification: Notification) -> Notification:
        """Redact sensitive content for external channels."""
        # For local channels, no redaction needed
        # For external channels (LINE, Discord, Email), redact
        external_channels = {NotificationChannel.LINE, NotificationChannel.DISCORD, NotificationChannel.EMAIL}
        if not any(ch in external_channels for ch in notification.channels):
            return notification

        # Redact body for external channels
        notification.body = "[REDACTED — sensitive content]"
        return notification

    def get_sent_count(self, notification_type: NotificationType) -> int:
        """Get sent count for a notification type."""
        return self._sent_count.get(notification_type.name, 0)

    def reset_counts(self) -> None:
        """Reset sent counts (e.g., daily reset)."""
        self._sent_count.clear()
