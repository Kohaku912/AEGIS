"""Discord integration stub — no real implementation."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.integrations.discord_stub")


class DiscordStub:
    """Discord integration stub. Does NOT send real messages."""

    def __init__(self) -> None:
        self._sent: list[dict[str, Any]] = []

    def send_message(self, channel_id: str, text: str) -> dict[str, Any]:
        """Stub: does not send real messages."""
        logger.info("Discord STUB: Would send to %s: %s", channel_id, text[:50])
        self._sent.append({"channel_id": channel_id, "text": text[:100]})
        return {"success": False, "reason": "Discord integration is stub only", "stub": True}

    def get_sent(self) -> list[dict[str, Any]]:
        return list(self._sent)
