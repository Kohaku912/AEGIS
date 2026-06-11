"""LINE integration stub — no real implementation.

Real LINE Bot implementation requires user confirmation.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.integrations.line_stub")


class LINEStub:
    """LINE integration stub.

    Does NOT send real messages. Returns mock responses only.
    Real implementation requires user confirmation.
    """

    def __init__(self) -> None:
        self._sent: list[dict[str, Any]] = []

    def send_message(self, user_id: str, text: str) -> dict[str, Any]:
        """Stub: does not send real messages."""
        logger.info("LINE STUB: Would send to %s: %s", user_id, text[:50])
        self._sent.append({"user_id": user_id, "text": text[:100]})
        return {
            "success": False,
            "reason": "LINE integration is stub only — real implementation not available",
            "stub": True,
        }

    def get_sent(self) -> list[dict[str, Any]]:
        """Get stub-sent messages (for testing)."""
        return list(self._sent)
