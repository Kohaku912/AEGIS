"""Webhook integration stub — no real implementation."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.integrations.webhook_stub")


class WebhookStub:
    """Webhook integration stub. Does NOT send real webhooks."""

    def __init__(self) -> None:
        self._sent: list[dict[str, Any]] = []

    def send_webhook(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Stub: does not send real webhooks."""
        logger.info("Webhook STUB: Would send to %s", url[:50])
        self._sent.append({"url": url, "payload": payload})
        return {"success": False, "reason": "Webhook integration is stub only", "stub": True}

    def get_sent(self) -> list[dict[str, Any]]:
        return list(self._sent)
