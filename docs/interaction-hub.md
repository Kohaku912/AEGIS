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

Messages are classified by keywords:

| Intent | Keywords | Route |
|--------|----------|-------|
| `RESEARCH_REQUEST` | research, search, find, tell me about | Research Agent |
| `SUPPORT_FEEDBACK` | accept, reject, feedback, thanks | Support Agent |
| `SETTINGS_REQUEST` | settings, config, enable, disable | Settings |
| `APPROVAL_DECISION` | approve, reject, allow, deny | Approval UI |
| `SELF_DEV_REQUEST` | improve, fix, optimize, refactor | SelfDevAgent |
| `STATUS_CHECK` | status, health | Dashboard |
| `HELP_REQUEST` | help, what can you do | Help text |
| `TOOL_REQUEST` | screenshot, click, tap | Approval UI redirect |

## Safety

- Chat requests go through PolicyEngine (no bypass)
- User text is NOT treated as system prompt
- Tool requests redirect to Approval UI
- Web Chat is localhost only
- External channel approvals require additional auth

## Usage

### Web Chat

```bash
cd ai-server
python -c "
from aegis_ai.interaction import InteractionRouter, WebChatApp
router = InteractionRouter()
app = WebChatApp(router=router)
app.run(host='0.0.0.0', port=8091)
"
# Open http://0.0.0.0:8091/chat
```

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
