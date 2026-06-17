"""Notification Manager — centralized non-approval notification management.

Wraps NotificationRouter. Adds state tracking, fanout, read/dismiss.
NOT for approval notifications (those go through ApprovalManager).
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from enum import Enum
from typing import Any

logger = logging.getLogger("aegis_ai.notification.notification_manager")


class NotificationStatus(Enum):
    CREATED = "created"
    SENT = "sent"
    PARTIALLY_SENT = "partially_sent"
    FAILED = "failed"
    READ = "read"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class NotificationManager:
    """Centralized notification management for non-approval notifications.

    Parameters
    ----------
    notification_router:
        The underlying NotificationRouter for delivery.
    event_manager:
        Optional EventManager for publishing notification events.
    """

    def __init__(
        self,
        notification_router: Any = None,
        event_manager: Any = None,
    ) -> None:
        self._router = notification_router
        self._event_manager = event_manager
        self._notifications: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_notification(
        self,
        title: str,
        body: str,
        severity: str = "info",
        category: str = "general",
        channels: list[str] | None = None,
        related_task_id: str = "",
        related_event_id: str = "",
        expires_in_ms: int = 3_600_000,
    ) -> dict[str, Any]:
        """Create a notification."""
        notif_id = f"notif_{uuid.uuid4().hex[:10]}"
        now_ms = int(time.time() * 1000)
        notification = {
            "notification_id": notif_id,
            "title": title,
            "body": body,
            "severity": severity,
            "category": category,
            "channels": channels or ["dashboard"],
            "created_at": now_ms,
            "expires_at": now_ms + expires_in_ms,
            "related_task_id": related_task_id,
            "related_event_id": related_event_id,
            "status": NotificationStatus.CREATED.value,
            "delivery_status": {},
            "read_by": [],
        }
        with self._lock:
            self._notifications[notif_id] = notification
        return notification

    def send(self, notification_id: str) -> dict[str, Any] | None:
        """Send a notification via NotificationRouter."""
        with self._lock:
            notif = self._notifications.get(notification_id)
            if notif is None:
                return None

        if self._router is not None:
            try:
                from aegis_ai.notification.models import Notification, NotificationSeverity
                severity_map = {
                    "info": NotificationSeverity.LOW,
                    "warning": NotificationSeverity.MEDIUM,
                    "error": NotificationSeverity.HIGH,
                    "critical": NotificationSeverity.CRITICAL,
                }
                n = Notification(
                    title=notif["title"],
                    body=notif["body"],
                    severity=severity_map.get(notif["severity"], NotificationSeverity.LOW),
                )
                success = self._router.send(n)
                notif["status"] = NotificationStatus.SENT.value if success else NotificationStatus.FAILED.value
                notif["delivery_status"]["router"] = success
            except Exception:
                notif["status"] = NotificationStatus.FAILED.value
                logger.exception("Notification send failed")
        else:
            notif["status"] = NotificationStatus.SENT.value

        if self._event_manager is not None:
            try:
                from aegis_schema.models import Event
                self._event_manager.publish(Event(
                    event_type="notification.sent",
                    source="notification_manager",
                    payload={"notification_id": notification_id, "title": notif["title"]},
                ))
            except Exception:
                pass

        return notif

    def mark_read(self, notification_id: str, user: str = "user") -> dict[str, Any] | None:
        """Mark a notification as read."""
        with self._lock:
            notif = self._notifications.get(notification_id)
            if notif is None:
                return None
            if user not in notif["read_by"]:
                notif["read_by"].append(user)
            notif["status"] = NotificationStatus.READ.value
            return notif

    def dismiss(self, notification_id: str) -> dict[str, Any] | None:
        """Dismiss a notification."""
        with self._lock:
            notif = self._notifications.get(notification_id)
            if notif is None:
                return None
            notif["status"] = NotificationStatus.DISMISSED.value
            return notif

    def expire(self, notification_id: str) -> dict[str, Any] | None:
        """Expire a notification."""
        with self._lock:
            notif = self._notifications.get(notification_id)
            if notif is None:
                return None
            notif["status"] = NotificationStatus.EXPIRED.value
            return notif

    def list_unread(self, limit: int = 50) -> list[dict[str, Any]]:
        """List unread notifications."""
        with self._lock:
            unread = [
                n for n in self._notifications.values()
                if n["status"] not in (NotificationStatus.READ.value, NotificationStatus.DISMISSED.value, NotificationStatus.EXPIRED.value)
            ]
        unread.sort(key=lambda n: n.get("created_at", 0), reverse=True)
        return unread[:limit]

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        """List recent notifications."""
        with self._lock:
            notifs = list(self._notifications.values())
        notifs.sort(key=lambda n: n.get("created_at", 0), reverse=True)
        return notifs[:limit]

    def get_notification(self, notification_id: str) -> dict[str, Any] | None:
        """Get a notification by ID."""
        with self._lock:
            return self._notifications.get(notification_id)
