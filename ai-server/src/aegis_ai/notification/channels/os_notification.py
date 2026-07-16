"""OS notification channel — delivers via PC Server overlay when available."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.notification.models import Notification

logger = logging.getLogger("aegis_ai.notification.channels.os_notification")


class OSNotificationChannel:
    """Sends OS-level notifications via PC Server overlay or native toast."""

    def __init__(self, pc_server_client: Any = None) -> None:
        self._pc = pc_server_client

    def send(self, notification: Notification) -> None:
        title = notification.title or "AEGIS"
        body = notification.body or ""
        severity = notification.severity.name.lower()
        logger.info("OS notification [%s]: %s — %s", severity, title, body)

        if self._pc is not None:
            try:
                text = f"{title}: {body}" if body else title
                self._pc.show_overlay(text=text, duration_ms=10_000)
            except Exception as exc:
                logger.debug("PC overlay delivery failed: %s", exc)
