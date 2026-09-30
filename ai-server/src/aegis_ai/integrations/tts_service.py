"""Text-to-Speech integration — provider-dispatched, local by preference.

Two engines exist and they are **not** interchangeable:

* ``os-tts`` — the operating system's own speech engine (see
  :mod:`aegis_ai.integrations.local_tts`). Nothing leaves the process, so it needs no
  egress permission.
* ``edge-tts`` / ``cloud`` — Microsoft's service. The text **is** user content, so it goes
  through the egress gate and is refused unless the user has permitted that destination.

**A local request is never served by the cloud engine.** If ``voice.tts_provider`` names a
local engine that is unavailable or unimplemented, the request is refused — falling back to
the cloud would send the user's text externally at the exact moment the user asked for it
not to be. That is the failure this module exists to prevent, and it is pinned by
``tests/test_voice_io.py``.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.integrations.tts")

#: Providers that synthesise inside this process — no egress, no permission needed.
_LOCAL_TTS_PROVIDERS = frozenset({"os-tts"})

#: Providers that send the text to a remote service — always through the egress gate.
_EXTERNAL_TTS_PROVIDERS = frozenset({"edge-tts", "cloud"})

#: Providers the settings advertise but that this module does not implement. Refused
#: rather than silently served by an external engine.
_UNIMPLEMENTED_TTS_PROVIDERS = frozenset({"piper"})


@dataclass
class TTSRequest:
    tts_id: str = ""
    text: str = ""
    voice: str = "ja-JP-NanamiNeural"
    output_path: str = ""
    rate: str = "+0%"
    volume: str = "+0%"
    created_at: int = 0


@dataclass
class TTSResult:
    tts_id: str = ""
    success: bool = False
    output_path: str = ""
    duration_ms: float = 0.0
    error: str = ""
    created_at: int = 0


def _rate_to_percent(rate: str) -> int:
    """Convert edge-tts's ``"+20%"`` / ``"-10%"`` form to an integer percentage.

    The local engines take a signed percentage too, but in different units, so the
    conversion happens once here rather than inside each engine branch. An unreadable rate
    is ``0`` (the engine's normal speed) rather than a guess.
    """
    try:
        return int(str(rate).strip().rstrip("%") or 0)
    except (TypeError, ValueError):
        return 0


class TextToSpeechService:
    """Text-to-speech, dispatching on the configured provider.

    Args:
        default_voice: Voice id for the external engine.
        settings_store: Optional SettingsStore. Supplies ``voice.tts_provider`` and the
            voice gate. **Without it there is no configured choice**, so the historical
            default (``edge-tts``) stands — which is what keeps the egress refusal below
            meaningful for callers that predate provider selection.
    """

    def __init__(self, default_voice: str = "ja-JP-NanamiNeural", settings_store: Any = None) -> None:
        self._default_voice = default_voice
        self._settings_store = settings_store

    def configured_provider(self) -> str:
        """The provider to use, or ``"none"`` when it cannot be read.

        Unreadable settings read as ``"none"`` (refuse), **never** as the cloud default:
        "we could not tell what you asked for" is not permission to send your text to
        Microsoft.
        """
        if self._settings_store is None:
            return "edge-tts"
        try:
            return str(self._settings_store.get().voice.tts_provider or "none")
        except Exception:
            return "none"

    def _voice_gate_refusal(self) -> str:
        """Why the voice gate refuses output, or ``""`` when it allows it."""
        if self._settings_store is None:
            return ""
        from aegis_ai.voice import VoiceGate

        check = VoiceGate(self._settings_store).check_voice_output()
        return "" if check.get("allowed") else str(check.get("reason") or "voice output is not allowed")

    @staticmethod
    def _egress_allows() -> bool:
        """Whether TTS text may be sent externally. Denied unless the user permits it."""
        from aegis_ai.egress import EgressRequest, get_egress_gate

        return get_egress_gate().allow(
            EgressRequest(
                destination="https://speech.platform.bing.com",
                purpose="voice.tts",
                component="integrations.tts_service",
                data_summary="text to be spoken (may contain user content)",
                carries_user_information=True,
            )
        )

    def synthesize(self, request: TTSRequest) -> TTSResult:
        if not request.tts_id:
            request.tts_id = f"tts_{uuid.uuid4().hex[:10]}"
        if not request.created_at:
            request.created_at = int(time.time() * 1000)
        if not request.voice:
            request.voice = self._default_voice

        if not request.text:
            return self._fail(request, "No text provided.")

        provider = self.configured_provider()

        if provider == "none":
            return self._fail(
                request,
                "Text-to-speech is disabled: no TTS provider is configured "
                "(voice.tts_provider is 'none'). Set it to 'os-tts' for local synthesis.",
            )

        refusal = self._voice_gate_refusal()
        if refusal:
            return self._fail(request, f"Text-to-speech is disabled: {refusal}.")

        if provider in _UNIMPLEMENTED_TTS_PROVIDERS:
            # Refused, NOT served by the external engine — see the module docstring.
            return self._fail(
                request,
                f"Text-to-speech is disabled: the provider '{provider}' is not implemented. "
                "Use 'os-tts' (local) or 'edge-tts'/'cloud' (external, through the egress gate).",
            )

        if provider in _LOCAL_TTS_PROVIDERS:
            return self._synthesize_locally(request, provider)

        if provider not in _EXTERNAL_TTS_PROVIDERS:
            return self._fail(
                request,
                f"Text-to-speech is disabled: unknown provider '{provider}'. "
                "Use 'os-tts' (local) or 'edge-tts'/'cloud' (external).",
            )

        # External: the text is user content, so it goes through the egress gate.
        if not self._egress_allows():
            logger.warning("TTS refused by the egress gate (text withheld)")
            return self._fail(
                request,
                "Text-to-speech is disabled: edge-tts would send the text to an external "
                "service (the single constraint), and the user has not permitted that "
                "destination. Configure the local provider ('os-tts') instead.",
            )

        if not request.output_path:
            request.output_path = f"data/tts/{request.tts_id}.mp3"

        Path(request.output_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            return asyncio.get_event_loop().run_until_complete(
                self._synthesize_async(request)
            )
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self._synthesize_async(request))
            finally:
                loop.close()

    @staticmethod
    def _fail(request: TTSRequest, error: str) -> TTSResult:
        return TTSResult(
            tts_id=request.tts_id,
            success=False,
            error=error,
            created_at=int(time.time() * 1000),
        )

    def _synthesize_locally(self, request: TTSRequest, provider: str) -> TTSResult:
        """Synthesise with the OS engine. No egress, so no permission is involved."""
        from aegis_ai.integrations import local_tts

        if not request.output_path:
            request.output_path = f"data/tts/{request.tts_id}.wav"

        started = time.perf_counter()
        ok, error = local_tts.synthesize_to_file(
            text=request.text,
            output_path=request.output_path,
            rate_percent=_rate_to_percent(request.rate),
        )
        duration = (time.perf_counter() - started) * 1000.0
        if not ok:
            return self._fail(request, f"Local text-to-speech ({provider}) failed: {error}")
        return TTSResult(
            tts_id=request.tts_id,
            success=True,
            output_path=request.output_path,
            duration_ms=duration,
            created_at=int(time.time() * 1000),
        )

    async def _synthesize_async(self, request: TTSRequest) -> TTSResult:
        try:
            import edge_tts

            start = time.perf_counter()
            communicate = edge_tts.Communicate(
                text=request.text,
                voice=request.voice,
                rate=request.rate,
                volume=request.volume,
            )
            await communicate.save(request.output_path)
            duration = (time.perf_counter() - start) * 1000

            if Path(request.output_path).exists():
                return TTSResult(
                    tts_id=request.tts_id,
                    success=True,
                    output_path=request.output_path,
                    duration_ms=duration,
                    created_at=int(time.time() * 1000),
                )
            return TTSResult(
                tts_id=request.tts_id,
                success=False,
                error="Output file not created.",
                created_at=int(time.time() * 1000),
            )
        except ImportError:
            return TTSResult(
                tts_id=request.tts_id,
                success=False,
                error="edge-tts not installed.",
                created_at=int(time.time() * 1000),
            )
        except Exception as exc:
            logger.error("TTS error: %s", exc)
            return TTSResult(
                tts_id=request.tts_id,
                success=False,
                error=str(exc)[:500],
                created_at=int(time.time() * 1000),
            )
