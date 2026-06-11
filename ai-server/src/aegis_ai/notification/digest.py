"""Digest — batches and summarizes deferred notifications."""

from __future__ import annotations

from typing import Any

from aegis_ai.notification.models import Notification


class NotificationDigest:
    """Batches deferred notifications for periodic delivery.

    Usage:
        digest = NotificationDigest()
        digest.defer(notification)
        summary = digest.generate_summary()
    """

    def __init__(self) -> None:
        self._deferred: list[Notification] = []

    def defer(self, notification: Notification) -> None:
        """Defer a notification for digest delivery."""
        self._deferred.append(notification)

    def generate_summary(self) -> dict[str, Any]:
        """Generate a digest summary of deferred notifications."""
        if not self._deferred:
            return {"count": 0, "summary": "No deferred notifications."}

        by_type: dict[str, int] = {}
        for n in self._deferred:
            type_name = n.type.name
            by_type[type_name] = by_type.get(type_name, 0) + 1

        lines = [f"{name}: {count}" for name, count in by_type.items()]
        return {
            "count": len(self._deferred),
            "by_type": by_type,
            "summary": f"Deferred notifications: {', '.join(lines)}",
        }

    def drain(self) -> list[Notification]:
        """Drain and return all deferred notifications."""
        items = list(self._deferred)
        self._deferred.clear()
        return items

    def count(self) -> int:
        """Number of deferred notifications."""
        return len(self._deferred)
