"""Email integration stub — no real implementation."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.integrations.email_stub")


class EmailStub:
    """Email integration stub. Does NOT send real emails."""

    def __init__(self) -> None:
        self._sent: list[dict[str, Any]] = []

    def send_email(self, to: str, subject: str, body: str) -> dict[str, Any]:
        """Stub: does not send real emails."""
        logger.info("Email STUB: Would send to %s: %s", to, subject[:50])
        self._sent.append({"to": to, "subject": subject, "body": body[:100]})
        return {"success": False, "reason": "Email integration is stub only", "stub": True}

    def get_sent(self) -> list[dict[str, Any]]:
        return list(self._sent)
