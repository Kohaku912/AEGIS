"""Wake Word Stub — wake word detection stub. No real audio monitoring."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.voice.wake_word_stub")


class WakeWordStub:
    """Wake word detection stub. Does NOT monitor audio.

    Returns mock detection for testing.
    Real implementation requires user confirmation.
    """

    def __init__(self) -> None:
        self._detections: list[dict[str, Any]] = []

    def detect(self, audio_data: bytes | None = None, simulate: bool = False) -> dict[str, Any]:
        """Stub: returns mock detection result."""
        logger.info("Wake word STUB: Would check for wake word")
        detected = simulate  # Only "detect" if explicitly simulated
        self._detections.append({"detected": detected, "stub": True})
        return {
            "success": True,
            "detected": detected,
            "wake_word": "AEGIS" if detected else "",
            "stub": True,
        }

    def get_detections(self) -> list[dict[str, Any]]:
        """Get mock detections."""
        return list(self._detections)
