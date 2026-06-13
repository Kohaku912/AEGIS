# Operations Dashboard

> **Status**: Implemented (2026-06-13)
> **Related**: `docs/architecture.md`, `docs/settings.md`, `docs/permissions.md`

## Overview

The Operations Dashboard provides a web-based view of AEGIS's internal state.
Features streaming chat, memory integration, and desire context.

## Screens

### Home (`/`)
- AEGIS Core status
- Connected servers count
- Recent errors
- Autonomous mode status
- Memory summary
- Desire states

### Servers (`/dashboard/servers`)
- PC / Android / Browser / Room server status
- Last heartbeat
- Registered capabilities count

### Capabilities (`/dashboard/capabilities`)
- Capability list with usage stats
- Safety level
- Success/failure count

### Events (`/dashboard/events`)
- EventBus recent events
- Source, type, severity, priority

### Tasks (`/dashboard/tasks`)
- Pending TaskRequests
- Trigger stats
- Scheduled tasks

### Support (`/dashboard/support`)
- Pending suggestions
- Accepted/rejected history

### Memory (`/dashboard/memory`)
- Episodic recent
- Semantic facts
- PersonaMemory (persons, conversations)
- ChromaSemanticMemory (vector DB)

### Audit (`/dashboard/audit`)
- Policy decisions
- Approval requests
- Safety events

### Errors (`/dashboard/errors`)
- Error log
- Stack traces

## Chat API

### Streaming Chat

**Endpoint**: `POST /api/chat/stream`

**Request**:
```json
{"text": "What is Python?"}
```

**Response** (Server-Sent Events):
```
data: {"type": "text", "content": "Python is"}
data: {"type": "text", "content": " a programming"}
data: {"type": "text", "content": " language..."}
data: {"type": "done"}
```

### Non-Streaming Chat

**Endpoint**: `POST /api/chat/send`

**Request**:
```json
{"text": "Take a screenshot"}
```

**Response**:
```json
{
  "response": "Here's your current screen:",
  "image": "base64...",
  "image_width": 1920,
  "image_height": 1080
}
```

### Chat History

**Endpoint**: `GET /api/chat/history`

**Response**: Array of chat entries

**Endpoint**: `POST /api/chat/clear`

**Response**: `{"status": "cleared"}`

## Autonomous API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/autonomous/status` | GET | Get loop status |
| `/api/autonomous/trigger` | POST | Manual trigger |
| `/api/autonomous/start` | POST | Start loop |
| `/api/autonomous/stop` | POST | Stop loop |
| `/api/desires` | GET | Get desire states |

## Design Decisions

1. **Streaming chat**: Real-time LLM response display
2. **Memory integration**: AdvancedMemory context in LLM prompts
3. **Desire context**: Current desire states in LLM prompts
4. **All actions through LLM**: Every result passes through LLM
5. **No keyword matching**: All decisions by LLM
