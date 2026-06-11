"""CLI notification channel — displays notifications in CLI."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.notification.models import Notification

logger = logging.getLogger("aegis_ai.notification.channels.cli")


class CLINotificationChannel:
    """Displays notifications in the CLI.

    Usage:
        channel = CLINotificationChannel()
        channel.send(notification)
    """

    def __init__(self) -> None:
        self._sent: list[dict[str, Any]] = []

    def send(self, notification: Notification) -> None:
        """Display notification in CLI."""
        self._sent.append({
            "notification_id": notification.notification_id,
            "title": notification.title,
            "severity": notification.severity.name,
        })
        # Print to stderr for visibility
        import sys
        print(f"\n[AEGIS Notification] {notification.severity.name}: {notification.title}", file=sys.stderr)
        if notification.body:
            print(f"  {notification.body}", file=sys.stderr)

    def get_sent(self) -> list[dict[str, Any]]:
        """Get sent notifications."""
        return list(self._sent)
