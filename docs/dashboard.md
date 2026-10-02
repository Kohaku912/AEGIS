# Operations Dashboard

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).


> **Status**: Implemented (verified against current code snapshot)
> **Related**: `docs/architecture.md`, `docs/settings.md`, `docs/permissions.md`

## Overview

The Operations Dashboard provides a web-based view of AEGIS's internal state.
Features chat with tool calling, memory integration, desire context,
and Manager API routes.

## Screens

### Home (`/`)
- AEGIS Core status
- Connected servers count (via StatusManager.get_snapshot())
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

### Chat With Tool Calling

**Send**: `POST /api/chat/send` — an ordinary JSON request. There is **no** `POST /api/chat/stream`.
```json
{"text": "What is Python?", "conversation_id": "optional-shared-id"}
```
The reply is JSON: `{"response": "...", "request_id": ..., "conversation_id": ...}` (plus `tool_results` when tools ran). When a tool pauses for input the body is `{"needs_user_input": true, "question": "...", "options": [...], "pending_context": {...}}` — answer it with `POST /api/chat/respond`. Errors: `400 invalid_request`; `409 request_in_progress` (the same `request_id` is de-duplicated for 15 minutes).

**Receive**: `GET /api/chat/events` — the Server-Sent Events channel (`text/event-stream`).
```
data: {"type":"heartbeat"}
```
⚠️ The route is **dead on both ends** (measured 2026-10-03). **No producer publishes to it** — the client queue is only ever created and removed (`dashboard_legacy.py:1135-1143`), and nothing calls `put` anywhere in that file, so a connected client receives **only** the 15-second `heartbeat` frames. **And no client subscribes** — the path string occurs in exactly one file (its own definition) and no `EventSource` is constructed anywhere in the repo. Pinned by `ai-server/tests/test_chat_sse_route_stays_dead.py`; wiring it or deleting it is an owner decision (`DELEGATION.md` §4 item 23).

The chat system supports **recursive multi-step tool calling** (up to **15** rounds — the `call_llm_with_tools` default; `LLMSettings.max_tool_rounds = 5` is *displayed* in the settings UI but never passed by any caller):
1. LLM receives user message and available tools (from CapabilityCatalog)
2. LLM calls a tool (or responds directly if no tool needed)
3. Tool executes and returns result
4. Result is fed back to the LLM
5. LLM decides: call another tool OR respond with summary

A screenshot request returns a JSON body that may carry an image:
```json
{"response": "Here's your current screen:", "image": "base64...", "image_width": 1920, "image_height": 1080}
```

### Chat History

**Endpoint**: `GET /api/chat/history`

**Response**: Array of chat entries

**Endpoint**: `POST /api/chat/clear`

**Response**: `{"status": "cleared"}`

## Manager API Routes

Registered via `init_manager_routes(app, runtime)` in `DashboardApp.__init__()`.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tasks` | GET | List tasks (TaskManager) |
| `/api/tasks/<id>` | GET | Get task detail |
| `/api/events` | GET | List events (EventManager) |
| `/api/events/cursor` | GET | Cursor-based event pagination |
| `/api/audit` | GET | List audit entries (AuditManager) |
| `/api/audit/cursor` | GET | Cursor-based audit pagination |
| `/api/audit/search` | GET | Search audit entries |
| `/api/status` | GET | Server status snapshot (StatusManager) |
| `/api/notifications` | GET | List notifications (NotificationManager) |
| `/api/notifications/<id>/read` | POST | Mark notification read |
| `/api/memory/<backend>` | GET | Get memory backend data (MemoryManager) |
| `/api/memory/<backend>/search` | POST | Search memory backend |
| `/api/sleep/status` | GET | Sleep consolidation status (SleepManager) |
| `/api/sleep/trigger` | POST | Trigger manual consolidation |
| `/api/user-state` | GET | User state snapshot |
| `/api/hooks` | GET | Hook events |
| `/api/commitments` | GET | Commitment tracking |
| `/api/delegation` | GET | Delegation tracking |
| `/api/situation` | GET | Situation overview |

## Autonomous API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/autonomous/status` | GET | Get loop status |
| `/api/autonomous/trigger` | POST | Manual trigger |
| `/api/autonomous/start` | POST | Start loop |
| `/api/autonomous/stop` | POST | Stop loop |
| `/api/desires` | GET | Get desire states |

## Design Decisions

1. **Chat**: LLM response display with tool calling
2. **Memory integration**: AdvancedMemory context in LLM prompts via MemoryManager
3. **Desire context**: Current desire states in LLM prompts
4. **All actions through LLM**: Every result passes through LLM
5. **No keyword matching**: All decisions by LLM
6. **Manager routes**: All 19 routes use runtime.*_manager for data access
7. **StatusManager for server status**: No `_check_port()` in routes — use `runtime.status_manager.get_snapshot()`

## Current Audit And Chat Behavior

- `/dashboard/audit` defaults to grouped operations. One chat turn, autonomous cycle, task, or approval continuation appears as one group card.
- Raw audit entries are still retained and visible from the same page for debugging.
- Audit grouping uses `audit_group_id`, `audit_group_type`, and `audit_group_title`; old entries fall back to `task_id`, `request_id`, `approval_id`, or `entry_id`.
- Dashboard chat, Web Chat, and Android Home chat share `data/chat_history.jsonl`.
- Approval requests created by chat preserve audit/chat metadata so approved actions execute once and post a follow-up message back to chat.
