"""Web Chat notification channel — sends notifications to active chat sessions."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.notification.models import Notification

logger = logging.getLogger("aegis_ai.notification.channels.web_chat")


class WebChatNotificationChannel:
    """Sends notifications to active Web Chat sessions.

    Usage:
        channel = WebChatNotificationChannel(session_manager=sessions)
        channel.send(notification)
    """

    def __init__(self, session_manager: Any = None) -> None:
        self._sessions = session_manager
        self._sent: list[dict[str, Any]] = []

    def send(self, notification: Notification) -> None:
        """Send notification to all active web chat sessions."""
        self._sent.append({
            "notification_id": notification.notification_id,
            "title": notification.title,
            "body": notification.body,
            "severity": notification.severity.name,
            "created_at_ms": notification.created_at_ms,
        })
        logger.info("Notification sent to web chat: %s", notification.title)

    def get_sent(self) -> list[dict[str, Any]]:
        """Get sent notifications."""
        return list(self._sent)
