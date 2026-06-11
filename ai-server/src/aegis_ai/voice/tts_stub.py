"""TTS Stub — text-to-speech stub. No real audio output."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.voice.tts_stub")


class TTSStub:
    """Text-to-speech stub. Does NOT produce real audio.

    Returns mock audio metadata for testing.
    Real implementation requires user confirmation.
    """

    def __init__(self) -> None:
        self._outputs: list[dict[str, Any]] = []

    def speak(self, text: str) -> dict[str, Any]:
        """Stub: returns mock audio metadata."""
        logger.info("TTS STUB: Would speak: %s", text[:50])
        self._outputs.append({"text": text, "stub": True})
        return {
            "success": True,
            "text": text,
            "duration_ms": len(text) * 50,  # Mock estimate
            "stub": True,
            "provider": "stub",
        }

    def get_outputs(self) -> list[dict[str, Any]]:
        """Get mock TTS outputs."""
        return list(self._outputs)
