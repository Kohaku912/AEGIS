"""Text-to-Speech integration — edge-tts based TTS."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("aegis_ai.integrations.tts")


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


class TextToSpeechService:
    """Text-to-speech using edge-tts."""

    def __init__(self, default_voice: str = "ja-JP-NanamiNeural") -> None:
        self._default_voice = default_voice

    @staticmethod
    def _egress_allows() -> bool:
        """Whether TTS text may be sent externally. Denied by default."""
        from aegis_ai.egress import EgressRequest, get_egress_gate

        return get_egress_gate().allow(
            EgressRequest(
                destination="https://speech.platform.bing.com",
                purpose="voice.tts",
                component="integrations.tts_service",
                data_summary="text to be spoken (may contain user content)",
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
            return TTSResult(
                tts_id=request.tts_id,
                success=False,
                error="No text provided.",
                created_at=int(time.time() * 1000),
            )

        # edge-tts sends the text to Microsoft's cloud service. The single constraint
        # forbids transmitting the user's data externally, so this is denied by default.
        if not self._egress_allows():
            logger.warning("TTS refused by the egress gate (text withheld)")
            return TTSResult(
                tts_id=request.tts_id,
                success=False,
                error=(
                    "Text-to-speech is disabled: edge-tts would send the text to an "
                    "external service (the single constraint). Configure a local TTS "
                    "provider instead."
                ),
                created_at=int(time.time() * 1000),
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
