# Voice I/O — Design & Gate

> **Status**: Stub only (design gate)
> **Related**: `docs/architecture.md`, `docs/settings.md`

## Overview

Voice I/O is **out of scope for MVP**. This module provides the design gate
and stubs for future voice implementation.

## Design Options (requires user confirmation)

### STT (Speech-to-Text)

| Provider | Type | Status |
|----------|------|--------|
| faster-whisper | Local | Not implemented |
| whisper.cpp | Local | Not implemented |
| Cloud STT | External | Not implemented |
| OS Speech API | Local | Not implemented |

### TTS (Text-to-Speech)

| Provider | Type | Status |
|----------|------|--------|
| edge-tts | Local/Cloud | Not implemented |
| Piper | Local | Not implemented |
| VOICEVOX | Local | Not implemented |
| Cloud TTS | External | Not implemented |
| OS TTS | Local | Not implemented |

### Wake Word

| Approach | Status |
|----------|--------|
| Push-to-talk | Not implemented |
| Local wake word | Not implemented |
| Always listening | **Forbidden** |

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `voice_enabled` | false | Enable voice I/O |
| `stt_provider` | "none" | STT provider |
| `tts_provider` | "none" | TTS provider |
| `record_audio` | false | Record audio |
| `external_voice_api_allowed` | false | Allow external STT/TTS |
| `push_to_talk_only` | true | Push-to-talk only |
| `wake_word_enabled` | false | Wake word detection |
| `voice_data_retention_hours` | 0 | Audio retention (0=never) |

## Safety

- Default disabled
- No always-listening
- No audio storage by default
- No external STT/TTS by default
- Push-to-talk only
- Voice approval requires additional auth (not implemented)

## Stubs

| Stub | Purpose |
|------|---------|
| `STTStub` | Mock speech-to-text for testing |
| `TTSStub` | Mock text-to-speech for testing |
| `WakeWordStub` | Mock wake word detection |

## Next Steps (requires user confirmation)

1. Choose STT provider (faster-whisper recommended for local)
2. Choose TTS provider (edge-tts recommended for local)
3. Implement push-to-talk flow
4. Integrate with Interaction Hub
5. Privacy review
