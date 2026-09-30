"""Voice I/O Gate — safe gateway for voice input/output.

Default disabled, and **fail-closed**: with no settings store every check returns
False. The engines behind it are real — local faster-whisper STT and a
local-or-permission-gated TTS (``integrations/stt_service.py``,
``integrations/tts_service.py``). This gate is what decides whether they may run.

Safety — ``tests/test_voice_io.py`` pins which of these are *enforced* and which are only *true*:
- No external STT/TTS by default — **enforced** (``is_stt_allowed`` / ``is_tts_allowed``, called)
- No always-listening — **not enforced**; true only because no wake-word path exists, and
  ``is_wake_word_enabled``, which would gate it, has no caller
- No audio storage by default — **not enforced**; true only because nothing stores audio, and
  ``record_audio`` / ``voice_data_retention_hours`` have no live reader
- Push-to-talk only — **not enforced** (a settings default)
- Voice approval requires additional auth — **not implemented**
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.voice.gate")


class VoiceGate:
    """Controls voice I/O access based on settings.

    Usage:
        gate = VoiceGate(settings_store=store)
        if gate.is_voice_enabled():
            # Process voice input
    """

    def __init__(self, settings_store: Any = None) -> None:
        self._settings = settings_store

    def is_voice_enabled(self) -> bool:
        """Check if voice I/O is enabled."""
        if not self._settings:
            return False
        try:
            settings = self._settings.get()
            return settings.voice.voice_enabled
        except Exception:
            return False

    def is_stt_allowed(self) -> bool:
        """Check if STT is allowed."""
        if not self._settings:
            return False
        try:
            settings = self._settings.get()
            if not settings.voice.voice_enabled:
                return False
            if settings.voice.stt_provider == "none":
                return False
            if settings.voice.stt_provider == "cloud" and not settings.voice.external_voice_api_allowed:
                return False
            return True
        except Exception:
            return False

    def is_tts_allowed(self) -> bool:
        """Check if TTS is allowed."""
        if not self._settings:
            return False
        try:
            settings = self._settings.get()
            if not settings.voice.voice_enabled:
                return False
            if settings.voice.tts_provider == "none":
                return False
            if settings.voice.tts_provider == "cloud" and not settings.voice.external_voice_api_allowed:
                return False
            return True
        except Exception:
            return False

    def is_audio_recording_allowed(self) -> bool:
        """Check if audio recording is allowed."""
        if not self._settings:
            return False
        try:
            settings = self._settings.get()
            return settings.voice.record_audio
        except Exception:
            return False

    def is_wake_word_enabled(self) -> bool:
        """Check if wake word detection is enabled."""
        if not self._settings:
            return False
        try:
            settings = self._settings.get()
            return settings.voice.wake_word_enabled
        except Exception:
            return False

    def check_voice_input(self) -> dict[str, Any]:
        """Check if voice input is allowed. Returns {allowed, reason}."""
        if not self.is_voice_enabled():
            return {"allowed": False, "reason": "Voice I/O is disabled in settings"}

        if not self.is_stt_allowed():
            return {"allowed": False, "reason": "STT provider not configured or not allowed"}

        return {"allowed": True, "reason": "Voice input allowed"}

    def check_voice_output(self) -> dict[str, Any]:
        """Check if voice output is allowed. Returns {allowed, reason}."""
        if not self.is_voice_enabled():
            return {"allowed": False, "reason": "Voice I/O is disabled in settings"}

        if not self.is_tts_allowed():
            return {"allowed": False, "reason": "TTS provider not configured or not allowed"}

        return {"allowed": True, "reason": "Voice output allowed"}
