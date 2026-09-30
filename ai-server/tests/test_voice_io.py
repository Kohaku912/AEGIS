"""Voice I/O — the local engines, the provider dispatch, and the two gates.

**Why this file exists.** Measured 2026-09-30: `VoiceGate` and `VoicePrivacy` were
constructed by **nobody** outside their own package `__init__`, and `SpeechToTextService` /
`TextToSpeechService` were called by **nobody in `src/`**. The whole voice safety layer was
dead code, and `TextToSpeechService` had exactly one engine — `edge-tts`, a *cloud* service
— so the constraint refused TTS by default and the refusal told the operator to "configure
a local TTS provider instead", naming a provider that did not exist. Voice I/O was on the
v1 list with no implementation behind it.

**The rule that matters most.** A request for a *local* engine must never be served by the
*external* one. If `voice.tts_provider` names something local that is unavailable or
unimplemented, the answer is a refusal — never a fallback to the cloud, because that would
send the user's text out at the exact moment the user asked for it not to be. That is what
``test_an_unimplemented_local_provider_is_never_served_by_the_cloud_engine`` pins, and it
is the reason the dispatch is explicit rather than "try each provider until one works".

This module carries the ``egress`` marker: the external TTS path is a guarded egress point,
so the mutation roster in ``scripts/verify_egress_tests_catch_regression.py`` must list it
(``test_egress_closure.py::test_the_mutation_roster_covers_every_marked_file`` enforces that).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

from aegis_ai.egress import configure_egress_gate
from aegis_ai.integrations import local_tts
from aegis_ai.integrations.stt_service import SpeechToTextService, STTRequest
from aegis_ai.integrations.tts_service import TextToSpeechService, TTSRequest
from aegis_ai.settings.models import AEGISSettings, PrivacySettings, VoiceSettings
from aegis_ai.voice import VoiceGate, VoicePrivacy

pytestmark = pytest.mark.egress


class _Store:
    """Minimal SettingsStore stand-in. Privacy defaults are closed, as in production."""

    def __init__(self, **voice: Any) -> None:
        self._settings = AEGISSettings(voice=VoiceSettings(**voice), privacy=PrivacySettings())

    def get(self) -> AEGISSettings:
        return self._settings


class _BrokenStore:
    def get(self) -> Any:
        raise RuntimeError("settings unavailable")


@pytest.fixture(autouse=True)
def _closed_egress():
    """Every test starts with the gate closed, and leaves it closed."""
    configure_egress_gate()
    yield
    configure_egress_gate()


def _tts(**voice: Any) -> TextToSpeechService:
    return TextToSpeechService(settings_store=_Store(**voice))


# ── The rule: a local request is never served by the cloud engine ─────────────


def test_an_unimplemented_local_provider_is_never_served_by_the_cloud_engine(monkeypatch):
    """**The load-bearing test.** `piper` is advertised by the settings and implemented
    nowhere. Asking for it must refuse, not quietly fall through to Microsoft.
    """
    reached = []

    def _record(*args, **kwargs):
        reached.append(True)
        raise AssertionError("the external engine was reached for a local provider request")

    monkeypatch.setattr(TextToSpeechService, "_synthesize_async", _record)
    monkeypatch.setattr(TextToSpeechService, "_egress_allows", staticmethod(lambda: True))

    result = _tts(tts_provider="piper", voice_enabled=True).synthesize(TTSRequest(text="secret"))

    assert result.success is False
    assert "not implemented" in result.error
    assert reached == [], "an unimplemented local provider fell through to the external engine"


def test_an_unknown_provider_is_refused_rather_than_defaulted(monkeypatch):
    """An unrecognised provider is not permission to use any particular engine."""
    monkeypatch.setattr(TextToSpeechService, "_egress_allows", staticmethod(lambda: True))
    result = _tts(tts_provider="whisper-9000", voice_enabled=True).synthesize(TTSRequest(text="x"))
    assert result.success is False
    assert "unknown provider" in result.error


def test_a_local_provider_never_consults_the_egress_gate(monkeypatch, tmp_path):
    """Local synthesis needs no permission — and must not *ask* for one.

    If the local path consulted the gate, a user with egress closed could not use the
    local engine at all, which inverts the point of having one.
    """
    calls = []

    def _record(request):
        calls.append(request)
        return False

    monkeypatch.setattr("aegis_ai.egress.get_egress_gate", lambda: type("G", (), {"allow": staticmethod(_record)})())
    monkeypatch.setattr(
        local_tts,
        "synthesize_to_file",
        lambda *, text, output_path, rate_percent=0: (Path(output_path).write_bytes(b"RIFFfake"), (True, ""))[1],
    )

    result = _tts(tts_provider="os-tts", voice_enabled=True).synthesize(
        TTSRequest(text="local only", output_path=str(tmp_path / "a.wav"))
    )

    assert result.success is True
    assert calls == [], "the local synthesis path consulted the egress gate"


# ── Fail closed ───────────────────────────────────────────────────────────────


def test_no_provider_configured_refuses():
    result = _tts(tts_provider="none").synthesize(TTSRequest(text="x"))
    assert result.success is False
    assert "no TTS provider is configured" in result.error


def test_unreadable_settings_refuse_rather_than_defaulting_to_the_cloud():
    """'We could not read what you asked for' is not permission to send your text out."""
    service = TextToSpeechService(settings_store=_BrokenStore())
    assert service.configured_provider() == "none"
    result = service.synthesize(TTSRequest(text="x"))
    assert result.success is False


def test_the_voice_gate_refuses_when_voice_is_disabled(monkeypatch):
    monkeypatch.setattr(TextToSpeechService, "_egress_allows", staticmethod(lambda: True))
    result = _tts(tts_provider="os-tts", voice_enabled=False).synthesize(TTSRequest(text="x"))
    assert result.success is False
    assert "Voice I/O is disabled" in result.error


def test_empty_text_is_refused():
    assert _tts(tts_provider="os-tts", voice_enabled=True).synthesize(TTSRequest(text="")).success is False


# ── The external path still goes through the gate ─────────────────────────────


def test_the_external_engine_is_refused_while_egress_is_closed(monkeypatch):
    """The pre-existing contract, kept: the cloud engine needs permission."""
    monkeypatch.setattr(
        TextToSpeechService,
        "_synthesize_async",
        lambda *a, **k: pytest.fail("the external path ran while egress was closed"),
    )
    result = _tts(tts_provider="edge-tts", voice_enabled=True).synthesize(TTSRequest(text="my notes"))
    assert result.success is False
    assert "single constraint" in result.error


def test_a_storeless_service_keeps_the_historical_default(monkeypatch):
    """Backward compatibility, pinned deliberately: callers predating provider selection
    get the cloud engine — and therefore the egress refusal — not a silent 'none'.
    """
    service = TextToSpeechService()
    assert service.configured_provider() == "edge-tts"
    assert service.synthesize(TTSRequest(text="x")).success is False


# ── The local engine, for real ────────────────────────────────────────────────


def test_the_local_engine_is_reported_or_the_refusal_names_what_to_install():
    """Non-vacuous on both platforms: either an engine exists, or the message says how."""
    engine = local_tts.available_engine()
    if engine:
        assert engine in {"sapi", "say", "espeak-ng", "espeak"}
    else:
        ok, error = local_tts.synthesize_to_file(text="x", output_path="unused.wav")
        assert ok is False
        assert "install" in error


@pytest.mark.skipif(not local_tts.available_engine(), reason="no local speech engine on this machine")
def test_the_local_engine_writes_real_audio_including_non_ascii(tmp_path):
    """Non-ASCII text must survive: the text travels through a UTF-8 file, never argv.

    Passing voice text as a command-line argument is how a "local" path silently mangles
    the very text it is meant to speak — the encoding would follow the console code page.
    """
    target = tmp_path / "out.wav"
    ok, error = local_tts.synthesize_to_file(text="こんにちは、AEGIS です。", output_path=str(target))

    assert ok is True, error
    assert target.exists() and target.stat().st_size > 1000, "the engine produced no usable audio"


@pytest.mark.skipif(not local_tts.available_engine(), reason="no local speech engine on this machine")
def test_the_local_engine_does_not_stage_the_text_as_an_argument(tmp_path):
    """The staged text file must not outlive the call, and must not be the output."""
    target = tmp_path / "out.wav"
    ok, _ = local_tts.synthesize_to_file(text="hello", output_path=str(target))
    assert ok is True
    leftovers = [p for p in tmp_path.iterdir() if p.suffix == ".txt"]
    assert leftovers == [], f"the staged text file was left behind: {leftovers}"


def test_a_missing_engine_is_reported_not_faked(monkeypatch, tmp_path):
    """A zero-length 'success' would make the caller believe the user had been spoken to."""
    monkeypatch.setattr(local_tts, "available_engine", lambda: "")
    ok, error = local_tts.synthesize_to_file(text="x", output_path=str(tmp_path / "x.wav"))
    assert ok is False
    assert "no local speech engine" in error


# ── STT: the gate and the redaction are wired ─────────────────────────────────


def test_stt_refuses_without_a_settings_store():
    """Fail closed: without a store the gate cannot authorise input."""
    result = SpeechToTextService().transcribe(STTRequest(audio_path="whatever.wav"))
    assert result.success is False
    assert "cannot be authorised" in result.error


def test_stt_refuses_when_voice_is_disabled():
    service = SpeechToTextService(settings_store=_Store(voice_enabled=False, stt_provider="faster-whisper"))
    result = service.transcribe(STTRequest(audio_path="whatever.wav"))
    assert result.success is False
    assert "disabled" in result.error


def test_stt_refuses_when_the_provider_is_none():
    service = SpeechToTextService(settings_store=_Store(voice_enabled=True, stt_provider="none"))
    assert service.transcribe(STTRequest(audio_path="whatever.wav")).success is False


def test_stt_passes_the_gate_when_voice_and_a_local_provider_are_enabled():
    """The gate is passed, so the *next* failure is the missing audio file — which proves
    the refusal above came from the gate rather than from a broken service.
    """
    service = SpeechToTextService(settings_store=_Store(voice_enabled=True, stt_provider="faster-whisper"))
    result = service.transcribe(STTRequest(audio_path="definitely-missing.wav"))
    assert result.success is False
    assert result.error == "Audio file not found."


@pytest.mark.parametrize(
    "spoken,scrubbed",
    [
        ("my password= hunter2 ok", "[REDACTED]"),
        ("mail me at a.b@example.com", "[EMAIL_REDACTED]"),
        ("card 4111 1111 1111 1111", "[CARD_REDACTED]"),
    ],
)
def test_stt_redacts_the_transcript(spoken: str, scrubbed: str):
    """A transcript is the user's own speech — exactly what the privacy layer scrubs."""
    service = SpeechToTextService(settings_store=_Store(voice_enabled=True, stt_provider="faster-whisper"))
    redacted = service._redact(spoken)
    assert scrubbed in redacted, f"{spoken!r} -> {redacted!r}"


def test_the_privacy_layer_is_what_does_the_redacting():
    """The service must not carry its own copy of the patterns."""
    store = _Store(voice_enabled=True, stt_provider="faster-whisper")
    expected = VoicePrivacy(store).redact_sensitive_text("token: abc123")
    actual = SpeechToTextService(settings_store=store)._redact("token: abc123")
    assert actual == expected


# ── The gate itself: the settings actually decide ─────────────────────────────


@pytest.mark.parametrize(
    "voice,expected",
    [
        ({"voice_enabled": False, "stt_provider": "faster-whisper"}, False),
        ({"voice_enabled": True, "stt_provider": "none"}, False),
        ({"voice_enabled": True, "stt_provider": "faster-whisper"}, True),
        ({"voice_enabled": True, "stt_provider": "cloud", "external_voice_api_allowed": False}, False),
        ({"voice_enabled": True, "stt_provider": "cloud", "external_voice_api_allowed": True}, True),
    ],
)
def test_the_voice_gate_follows_the_settings(voice: dict[str, Any], expected: bool):
    assert VoiceGate(_Store(**voice)).is_stt_allowed() is expected


def test_the_voice_gate_refuses_without_settings():
    assert VoiceGate(None).is_voice_enabled() is False
    assert VoiceGate(_BrokenStore()).is_tts_allowed() is False


def test_audio_is_not_stored_unless_both_switches_agree():
    """`record_audio` alone is not enough — a zero retention window means 'never store'."""
    assert VoicePrivacy(_Store(record_audio=True, voice_data_retention_hours=0)).should_store_audio() is False
    assert VoicePrivacy(_Store(record_audio=True, voice_data_retention_hours=24)).should_store_audio() is True
    assert VoicePrivacy(_Store(record_audio=False, voice_data_retention_hours=24)).should_store_audio() is False


def test_push_to_talk_is_the_default_and_wake_word_is_off():
    """No always-listening by default — a settings default, pinned so it cannot drift."""
    voice = VoiceSettings()
    assert voice.push_to_talk_only is True
    assert voice.wake_word_enabled is False
    assert voice.record_audio is False
    assert voice.external_voice_api_allowed is False
    assert voice.voice_enabled is False


def test_this_module_is_marked_egress():
    """Guard for the roster invariant: if this marker is dropped, the drift guard fires."""
    assert sys.modules[__name__].pytestmark.mark.name == "egress"
