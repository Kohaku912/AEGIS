"""Tests for Voice I/O Gate — settings, gate, stubs, privacy."""

from __future__ import annotations

from aegis_ai.settings.store import SettingsStore
from aegis_ai.voice.gate import VoiceGate
from aegis_ai.voice.privacy import VoicePrivacy
from aegis_ai.voice.stt_stub import STTStub
from aegis_ai.voice.tts_stub import TTSStub
from aegis_ai.voice.wake_word_stub import WakeWordStub

# ── Helpers ──────────────────────────────────────────────────


def _make_settings(**voice_overrides) -> SettingsStore:
    """Create a SettingsStore with optional voice overrides."""
    import os
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(path)
    store = SettingsStore(path=path, audit_path=path + ".audit.jsonl")
    if voice_overrides:
        settings = store.get()
        for k, v in voice_overrides.items():
            setattr(settings.voice, k, v)
        store.update(settings)
    return store


# ═══════════════════════════════════════════════════════════════
# 1. Voice Gate
# ═══════════════════════════════════════════════════════════════


class TestVoiceGate:
    """Voice gate controls voice I/O access."""

    def test_voice_disabled_by_default(self):
        """Voice is disabled by default."""
        store = _make_settings()
        gate = VoiceGate(settings_store=store)
        assert gate.is_voice_enabled() is False

    def test_voice_enabled(self):
        """Voice can be enabled."""
        store = _make_settings(voice_enabled=True, stt_provider="faster-whisper", tts_provider="edge-tts")
        gate = VoiceGate(settings_store=store)
        assert gate.is_voice_enabled() is True

    def test_stt_disabled_by_default(self):
        """STT is disabled by default."""
        store = _make_settings()
        gate = VoiceGate(settings_store=store)
        assert gate.is_stt_allowed() is False

    def test_stt_enabled(self):
        """STT can be enabled."""
        store = _make_settings(voice_enabled=True, stt_provider="faster-whisper")
        gate = VoiceGate(settings_store=store)
        assert gate.is_stt_allowed() is True

    def test_stt_cloud_blocked_without_external(self):
        """Cloud STT blocked without external_voice_api_allowed."""
        store = _make_settings(voice_enabled=True, stt_provider="cloud", external_voice_api_allowed=False)
        gate = VoiceGate(settings_store=store)
        assert gate.is_stt_allowed() is False

    def test_stt_cloud_allowed_with_external(self):
        """Cloud STT allowed with external_voice_api_allowed."""
        store = _make_settings(voice_enabled=True, stt_provider="cloud", external_voice_api_allowed=True)
        gate = VoiceGate(settings_store=store)
        assert gate.is_stt_allowed() is True

    def test_tts_disabled_by_default(self):
        """TTS is disabled by default."""
        store = _make_settings()
        gate = VoiceGate(settings_store=store)
        assert gate.is_tts_allowed() is False

    def test_audio_recording_disabled_by_default(self):
        """Audio recording is disabled by default."""
        store = _make_settings()
        gate = VoiceGate(settings_store=store)
        assert gate.is_audio_recording_allowed() is False

    def test_wake_word_disabled_by_default(self):
        """Wake word is disabled by default."""
        store = _make_settings()
        gate = VoiceGate(settings_store=store)
        assert gate.is_wake_word_enabled() is False

    def test_check_voice_input_disabled(self):
        """check_voice_input returns denied when disabled."""
        store = _make_settings()
        gate = VoiceGate(settings_store=store)
        result = gate.check_voice_input()
        assert result["allowed"] is False

    def test_check_voice_input_enabled(self):
        """check_voice_input returns allowed when enabled."""
        store = _make_settings(voice_enabled=True, stt_provider="faster-whisper")
        gate = VoiceGate(settings_store=store)
        result = gate.check_voice_input()
        assert result["allowed"] is True

    def test_check_voice_output_disabled(self):
        """check_voice_output returns denied when disabled."""
        store = _make_settings()
        gate = VoiceGate(settings_store=store)
        result = gate.check_voice_output()
        assert result["allowed"] is False


# ═══════════════════════════════════════════════════════════════
# 2. STT Stub
# ═══════════════════════════════════════════════════════════════


class TestSTTStub:
    """STT stub returns mock transcriptions."""

    def test_transcribe_returns_stub(self):
        """transcribe returns stub response."""
        stub = STTStub()
        result = stub.transcribe(text_hint="Hello")
        assert result["success"] is True
        assert result["stub"] is True
        assert result["text"] == "Hello"

    def test_transcribe_default_text(self):
        """transcribe returns default text if no hint."""
        stub = STTStub()
        result = stub.transcribe()
        assert "[MOCK" in result["text"]

    def test_transcriptions_logged(self):
        """Transcriptions are logged."""
        stub = STTStub()
        stub.transcribe(text_hint="Test")
        assert len(stub.get_transcriptions()) == 1


# ═══════════════════════════════════════════════════════════════
# 3. TTS Stub
# ═══════════════════════════════════════════════════════════════


class TestTTSStub:
    """TTS stub returns mock audio metadata."""

    def test_speak_returns_stub(self):
        """speak returns stub response."""
        stub = TTSStub()
        result = stub.speak("Hello AEGIS")
        assert result["success"] is True
        assert result["stub"] is True
        assert result["text"] == "Hello AEGIS"

    def test_outputs_logged(self):
        """Outputs are logged."""
        stub = TTSStub()
        stub.speak("Test")
        assert len(stub.get_outputs()) == 1


# ═══════════════════════════════════════════════════════════════
# 4. Wake Word Stub
# ═══════════════════════════════════════════════════════════════


class TestWakeWordStub:
    """Wake word stub returns mock detection."""

    def test_detect_no_simulate(self):
        """detect returns not detected by default."""
        stub = WakeWordStub()
        result = stub.detect()
        assert result["detected"] is False
        assert result["stub"] is True

    def test_detect_simulate(self):
        """detect returns detected when simulated."""
        stub = WakeWordStub()
        result = stub.detect(simulate=True)
        assert result["detected"] is True
        assert result["wake_word"] == "AEGIS"


# ═══════════════════════════════════════════════════════════════
# 5. Voice Privacy
# ═══════════════════════════════════════════════════════════════


class TestVoicePrivacy:
    """Voice privacy controls."""

    def test_no_audio_storage_by_default(self):
        """Audio storage disabled by default."""
        store = _make_settings()
        privacy = VoicePrivacy(settings_store=store)
        assert privacy.should_store_audio() is False

    def test_external_api_blocked_by_default(self):
        """External API blocked by default."""
        store = _make_settings()
        privacy = VoicePrivacy(settings_store=store)
        assert privacy.is_external_api_allowed() is False

    def test_redact_email(self):
        """Email is redacted."""
        privacy = VoicePrivacy()
        result = privacy.redact_sensitive_text("Contact test@example.com")
        assert "test@example.com" not in result
        assert "[EMAIL_REDACTED]" in result

    def test_redact_password(self):
        """Password is redacted."""
        privacy = VoicePrivacy()
        result = privacy.redact_sensitive_text("password: secret123")
        assert "secret123" not in result

    def test_redact_credit_card(self):
        """Credit card is redacted."""
        privacy = VoicePrivacy()
        result = privacy.redact_sensitive_text("Card 4111 1111 1111 1111")
        assert "4111" not in result


# ═══════════════════════════════════════════════════════════════
# 6. E2E Scenarios
# ═══════════════════════════════════════════════════════════════


class TestVoiceE2E:
    """End-to-end voice I/O scenarios."""

    def test_voice_disabled_rejects_input(self):
        """Voice disabled → input rejected."""
        store = _make_settings()
        gate = VoiceGate(settings_store=store)
        result = gate.check_voice_input()
        assert result["allowed"] is False

    def test_stub_voice_input_to_interaction_hub(self):
        """Stub voice input flows to Interaction Hub as message."""
        stub = STTStub()
        result = stub.transcribe(text_hint="research Python 3.12")
        assert result["success"] is True
        assert "research" in result["text"].lower()

    def test_stub_tts_to_notification_gateway(self):
        """Stub TTS output records to notification gateway."""
        stub = TTSStub()
        result = stub.speak("Temperature is 25 degrees")
        assert result["success"] is True
        assert len(stub.get_outputs()) == 1

    def test_external_stt_blocked(self):
        """External STT request denied unless enabled."""
        store = _make_settings(voice_enabled=True, stt_provider="cloud", external_voice_api_allowed=False)
        gate = VoiceGate(settings_store=store)
        assert gate.is_stt_allowed() is False

    def test_audio_storage_disabled(self):
        """Audio storage disabled → no storage."""
        store = _make_settings()
        privacy = VoicePrivacy(settings_store=store)
        assert privacy.should_store_audio() is False
