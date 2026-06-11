"""STT Stub — speech-to-text stub. No real audio processing."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.voice.stt_stub")


class STTStub:
    """Speech-to-text stub. Does NOT process real audio.

    Returns mock transcription for testing.
    Real implementation requires user confirmation.
    """

    def __init__(self) -> None:
        self._transcriptions: list[dict[str, Any]] = []

    def transcribe(self, audio_data: bytes | None = None, text_hint: str = "") -> dict[str, Any]:
        """Stub: returns mock transcription."""
        logger.info("STT STUB: Would transcribe audio")
        mock_text = text_hint or "[MOCK TRANSCRIPTION]"
        self._transcriptions.append({"text": mock_text, "stub": True})
        return {
            "success": True,
            "text": mock_text,
            "confidence": 0.0,
            "stub": True,
            "provider": "stub",
        }

    def get_transcriptions(self) -> list[dict[str, Any]]:
        """Get mock transcriptions."""
        return list(self._transcriptions)
