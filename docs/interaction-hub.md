# Interaction Hub — User Interaction Entry Points

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).


> **Status**: Implemented
> **Related**: `docs/chat-ui.md`, `docs/architecture.md`

## Overview

The Interaction Hub provides unified user interaction across multiple channels:
- **Web Chat** — browser-based chat interface
- **CLI** — command-line interface
- **LINE / Discord** — no **inbound** channel: nothing receives external messages or routes them
  into the hub. **Outbound** sending is implemented behind the egress gate
  (`docs/external-integrations.md`); v1 scope as of 2026-09-30
- **Voice** — local STT/TTS engines exist (`docs/voice-io.md`), but **no hub channel is wired**

## Architecture

```
User Input (Web Chat / CLI / Future)
  ↓
InteractionRouter (intent classification)
  ├── RESEARCH_REQUEST → Research Agent
  ├── SUPPORT_FEEDBACK → Support Agent
  ├── SETTINGS_REQUEST → Settings
  ├── APPROVAL_DECISION → Approval UI
  ├── SELF_DEV_REQUEST → SelfDevAgent
  ├── STATUS_CHECK → Dashboard
  ├── HELP_REQUEST → Help text
  ├── TOOL_REQUEST → Approval UI redirect
  └── UNKNOWN → Clarification
  ↓
Response → User
```

## Channels

| Channel | Status | Description |
|---------|--------|-------------|
| Web Chat | ✅ Implemented | Flask-based chat UI at `/chat` |
| CLI | ✅ Implemented | Interactive command-line interface |
| LINE | Inbound not implemented | Outbound sending is implemented, gate-refused until permitted |
| Discord | Inbound not implemented | Outbound sending is implemented, gate-refused until permitted |
| Voice | Engines only | Local STT/TTS exist (`docs/voice-io.md`); no hub channel is wired |

## Cross-device context

The chat history is **one local file** shared by every surface (`data/chat_history.jsonl`, via
`web/chat_history.py`), and each entry records the `source` that wrote it. The assistant's prompt is
therefore scoped to the **conversation**, not to the device:

- Every turn of the conversation is included, whichever device produced it, each labelled with that
  device — so the model can see the user moved from the dashboard to the phone mid-conversation.
- Turns of a **different** conversation are never included.
- An entry with **no** `conversation_id` is never matched. It cannot be attributed to a conversation,
  and folding it into one would invent a continuity the record does not support.
- With no `conversation_id` at all, the previous behaviour is kept: a recent-turns excerpt framed as
  background only.

A client joins a conversation by sending its id (`conversation_id` in `POST /api/chat/send`); the
server echoes the id it actually used, so a client that sent none can keep it and continue from
another device. Nothing here leaves the local environment.

**Device-offline degradation is deliberately out of v1** — see `DECISION_DRAFTS.md` C-2.

## Intent Classification

**All intent classification is LLM-driven** — no keyword matching, no regex patterns.
The LLM interprets the user's message and routes it to the appropriate agent or action.
Code NEVER inspects user text for keywords.

| Possible Route | Description |
|--------|----------|
| Research Agent | Deep information gathering |
| Support Agent | Proactive user assistance |
| SelfDev Agent | Self-improvement workflows |
| Settings | Configuration changes |
| Approval UI | Approval decisions |
| Dashboard | Status checks |
| Help | Capability descriptions |

## Safety

- Chat requests go through PolicyEngine (no bypass)
- User text is NOT treated as system prompt
- Tool requests redirect to Approval UI
- Chat is served by the Dashboard SPA at `/chat`
- External channel approvals require additional auth

## Usage

### Web Chat

Open `http://localhost:8090/chat` on the Dashboard. The standalone WebChatApp on port 8091 has been removed.

### CLI

```bash
cd ai-server
python -c "
from aegis_ai.interaction import InteractionRouter, CLIChannel
router = InteractionRouter()
cli = CLIChannel(router=router)
cli.run()
"
```
