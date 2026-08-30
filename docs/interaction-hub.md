# Interaction Hub — User Interaction Entry Points

> **Status**: Implemented
> **Related**: `docs/chat-ui.md`, `docs/architecture.md`

## Overview

The Interaction Hub provides unified user interaction across multiple channels:
- **Web Chat** — browser-based chat interface
- **CLI** — command-line interface
- **LINE / Discord / Voice** — stubs only (requires user confirmation)

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
| LINE | Stub only | Requires user confirmation |
| Discord | Stub only | Requires user confirmation |
| Voice | Stub only | Requires user confirmation |

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
