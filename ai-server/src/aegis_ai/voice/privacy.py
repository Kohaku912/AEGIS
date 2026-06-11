"""Voice Privacy — privacy controls for voice I/O."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.voice.privacy")


class VoicePrivacy:
    """Privacy controls for voice I/O.

    Ensures:
    - No always-listening
    - No audio storage by default
    - No external STT/TTS by default
    - Sensitive conversation redaction
    """

    def __init__(self, settings_store: Any = None) -> None:
        self._settings = settings_store

    def should_store_audio(self) -> bool:
        """Check if audio should be stored."""
        if not self._settings:
            return False
        try:
            settings = self._settings.get()
            return settings.voice.record_audio and settings.voice.voice_data_retention_hours > 0
        except Exception:
            return False

    def is_external_api_allowed(self) -> bool:
        """Check if external voice API is allowed."""
        if not self._settings:
            return False
        try:
            settings = self._settings.get()
            return settings.voice.external_voice_api_allowed
        except Exception:
            return False

    def redact_sensitive_text(self, text: str) -> str:
        """Redact sensitive information from voice transcriptions."""
        import re
        # Redact common sensitive patterns
        patterns = [
            (r'(?i)(password|passwd|secret|token|api_key)\s*[=:]\s*\S+', r'\1=[REDACTED]'),
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL_REDACTED]'),
            (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD_REDACTED]'),
        ]
        result = text
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        return result
