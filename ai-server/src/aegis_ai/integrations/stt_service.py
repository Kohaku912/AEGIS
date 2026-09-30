"""Speech-to-Text integration — faster-whisper based STT."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.integrations.stt")


@dataclass
class STTRequest:
    stt_id: str = ""
    audio_path: str = ""
    language: str = "ja"
    model_size: str = "base"
    created_at: int = 0


@dataclass
class STTResult:
    stt_id: str = ""
    success: bool = False
    text: str = ""
    language: str = ""
    confidence: float = 0.0
    segments: list[dict[str, Any]] = field(default_factory=list)
    duration_ms: float = 0.0
    error: str = ""
    created_at: int = 0


class SpeechToTextService:
    """Speech-to-text using faster-whisper, which runs **locally** — no egress involved.

    Two gates decide whether a transcription may happen at all, and neither was consulted
    before: ``voice.voice_enabled`` / ``voice.stt_provider`` (through ``VoiceGate``) and the
    privacy layer's redaction of the transcript. Both are wired here, because a safety
    class that nothing calls is not a control.

    Args:
        model_size: faster-whisper model size.
        settings_store: Optional SettingsStore. Without it the gate cannot be consulted, so
            transcription is **refused** rather than allowed — the same fail-closed
            direction as everywhere else.
    """

    def __init__(self, model_size: str = "base", settings_store: Any = None) -> None:
        self._model_size = model_size
        self._model: Any = None
        self._settings_store = settings_store

    def _gate_refusal(self) -> str:
        """Why the voice gate refuses input, or ``""`` when it allows it."""
        if self._settings_store is None:
            return "no settings store is configured, so voice input cannot be authorised"
        from aegis_ai.voice import VoiceGate

        check = VoiceGate(self._settings_store).check_voice_input()
        return "" if check.get("allowed") else str(check.get("reason") or "voice input is not allowed")

    def _redact(self, text: str) -> str:
        """Apply the privacy layer's redaction to a transcript.

        A transcript is the user's own speech, which is exactly the content the privacy
        layer exists to scrub before it is stored or forwarded.
        """
        if self._settings_store is None:
            return text
        from aegis_ai.voice import VoicePrivacy

        return VoicePrivacy(self._settings_store).redact_sensitive_text(text)

    def transcribe(self, request: STTRequest) -> STTResult:
        if not request.stt_id:
            request.stt_id = f"stt_{uuid.uuid4().hex[:10]}"
        if not request.created_at:
            request.created_at = int(time.time() * 1000)

        refusal = self._gate_refusal()
        if refusal:
            return STTResult(
                stt_id=request.stt_id,
                success=False,
                error=f"Speech-to-text is disabled: {refusal}.",
                created_at=int(time.time() * 1000),
            )

        if not request.audio_path or not Path(request.audio_path).exists():
            return STTResult(
                stt_id=request.stt_id,
                success=False,
                error="Audio file not found.",
                created_at=int(time.time() * 1000),
            )

        try:
            from faster_whisper import WhisperModel

            model_size = request.model_size or self._model_size
            if self._model is None:
                self._model = WhisperModel(model_size, device="cpu", compute_type="int8")

            start = time.perf_counter()
            segments_raw, info = self._model.transcribe(
                request.audio_path,
                language=request.language if request.language != "auto" else None,
                beam_size=5,
            )

            segments = []
            full_text_parts = []
            for seg in segments_raw:
                # Redact per segment, then build the joined text from the redacted pieces —
                # otherwise the whole-transcript field and the per-segment fields could
                # disagree about what was scrubbed.
                piece = self._redact(seg.text.strip())
                segments.append({
                    "start": seg.start,
                    "end": seg.end,
                    "text": piece,
                    "confidence": seg.avg_logprob,
                })
                full_text_parts.append(piece)

            duration = (time.perf_counter() - start) * 1000
            full_text = " ".join(full_text_parts)
            avg_conf = sum(s["confidence"] for s in segments) / len(segments) if segments else 0.0

            return STTResult(
                stt_id=request.stt_id,
                success=True,
                text=full_text,
                language=info.language if hasattr(info, "language") else request.language,
                confidence=min(1.0, max(0.0, (avg_conf + 1.0) / 2.0)),
                segments=segments[:50],
                duration_ms=duration,
                created_at=int(time.time() * 1000),
            )
        except ImportError:
            return STTResult(
                stt_id=request.stt_id,
                success=False,
                error="faster-whisper not installed.",
                created_at=int(time.time() * 1000),
            )
        except Exception as exc:
            logger.error("STT error: %s", exc)
            return STTResult(
                stt_id=request.stt_id,
                success=False,
                error=str(exc)[:500],
                created_at=int(time.time() * 1000),
            )
