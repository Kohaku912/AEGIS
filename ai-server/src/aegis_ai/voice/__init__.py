"""Voice I/O — voice input/output gateway (stubs only).

Provides:
- VoiceGate: Controls voice I/O access
- STTStub: Speech-to-text stub
- TTSStub: Text-to-speech stub
- WakeWordStub: Wake word detection stub
- VoicePrivacy: Privacy controls

All implementations are stubs. Real implementation requires user confirmation.
"""

from aegis_ai.voice.gate import VoiceGate  # noqa: F401
from aegis_ai.voice.privacy import VoicePrivacy  # noqa: F401
from aegis_ai.voice.stt_stub import STTStub  # noqa: F401
from aegis_ai.voice.tts_stub import TTSStub  # noqa: F401
from aegis_ai.voice.wake_word_stub import WakeWordStub  # noqa: F401
