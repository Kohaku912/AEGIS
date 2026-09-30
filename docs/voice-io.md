# Voice I/O — Design & Gate

> ⚠️ **Goal change (2026-09-27)**: the only constraint is now **"the user's information must never
> leave the local environment."** Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).


> **Status**: Implemented — the local STT/TTS engines are real; push-to-talk enforcement and
> wake word are **not** implemented
> **Related**: `docs/architecture.md`, `docs/settings.md`, `docs/egress-gate.md`

## Overview

Voice I/O is **in scope for v1** (owner, 2026-09-30 — see [`GOAL-CHANGE.md`](GOAL-CHANGE.md)).
It was previously declared out of scope with "stubs only", and **both halves of that have changed**:

- The engines are **real**, not stubs. `integrations/stt_service.py` transcribes locally with
  faster-whisper; `integrations/tts_service.py` dispatches between a local OS engine and a
  permission-gated external one.
- `VoiceGate` and `VoicePrivacy` are now **called**. Before this, nothing in `src/` constructed
  them, so every voice setting was textually "read" but behaviourally dead.

> The previous version of this file listed `STTStub`, `TTSStub`, and `WakeWordStub` classes. Those
> **never existed anywhere in the tree** — this table was the only place they were ever named.

### What is wired

| Piece | Where | State |
|-------|-------|-------|
| `VoiceGate` — settings check, fail-closed | `voice/gate.py` | Wired; called by both services |
| `VoicePrivacy` — transcript redaction | `voice/privacy.py` | Wired, **per segment**, so the segment and joined text cannot disagree |
| STT | `integrations/stt_service.py` | Wired; needs the `faster-whisper` package (**not installed in this environment**) |
| TTS, local | `integrations/local_tts.py` | Wired and **verified on Windows (`sapi`)** |
| TTS, external | `integrations/tts_service.py` | Wired through the egress gate and `voice.external_voice_api_allowed` |

## Design Options

### STT (Speech-to-Text)

| Provider | Type | Status |
|----------|------|--------|
| faster-whisper | Local | **Implemented** (`stt_service.py`); the package is not installed in this environment |
| whisper.cpp | Local | Not implemented |
| OS Speech API | Local | Not implemented |
| Cloud STT | External | Not implemented |

### TTS (Text-to-Speech)

| Provider | Type | Status |
|----------|------|--------|
| `os-tts` (SAPI / `say` / espeak) | Local | **Implemented and verified** (`local_tts.py`) |
| `edge-tts` | External | Implemented code path; needs the package and an egress permission |
| `cloud` | External | Implemented code path; needs an egress permission |
| Piper | Local | **Declared but unimplemented** — refused, never silently served by the cloud engine |
| VOICEVOX | Local | Not implemented |

> `edge-tts` was previously listed here as "Local/Cloud". It calls Microsoft's service, so it is
> **external**, and the gate treats it that way.

### Wake Word

| Approach | Status |
|----------|--------|
| Push-to-talk | **Not enforced** — `voice.push_to_talk_only` is read by nothing (`tests/test_ineffective_flags.py`) |
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
| `push_to_talk_only` | true | Push-to-talk only (**not enforced**) |
| `wake_word_enabled` | false | Wake word detection |
| `voice_data_retention_hours` | 0 | Audio retention (0=never) |

## Safety

- Default disabled, and the gate is **fail-closed**: with no settings store every check returns False
- No always-listening
- No audio storage by default
- No external STT/TTS by default; the external TTS path also goes through the egress gate
- **A local provider is never served by the cloud engine.** If a local engine is named but is
  unavailable or unimplemented, the request is **refused** — falling back would send the user's text
  out at the exact moment they asked it not to. Pinned by `tests/test_voice_io.py`.
- Push-to-talk is a settings default only; nothing enforces it
- Voice approval requires additional auth (not implemented)

## Next Steps

1. Install and verify `faster-whisper` for local STT
2. Enforce `push_to_talk_only` in the capture path, or delete the field
3. Implement the wake-word path
4. Integrate with Interaction Hub
