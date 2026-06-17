# Approval UI — Design & Usage

> **Status**: Implemented — ApprovalManager + Fanout (2026-06-17)  
> **Related**: [`architecture.md`](architecture.md) §7.4, [`AGENTS.md`](../AGENTS.md) Security Policy

## Overview

The Approval system handles Level 2/3 operations through a unified lifecycle:

1. **ApprovalManager** (`approval/approval_manager.py`) — Central lifecycle management
2. **ApprovalFanout** (`approval/fanout.py`) — Multi-channel delivery to users
3. **Approval channels** — Dashboard SSE, PC overlay, Android notification, Room display

When AEGIS attempts a Level 2/3 operation, the PolicyEngine creates an `ApprovalRequest`.
The ApprovalManager routes it through the Fanout to all configured channels.

## Architecture

```
PolicyEngine → ApprovalManager → ApprovalFanout
                                    ├── DashboardChannel (SSE to web UI)
                                    ├── PCOverlayChannel (overlay on PC screen)
                                    ├── AndroidChannel (Android notification)
                                    └── RoomChannel (Room Server display + TTS)
```

## Endpoints

### Approval Web UI

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/approvals` | List all pending approvals |
| GET | `/approvals/{id}` | Detail view for one approval |
| POST | `/approvals/{id}/approve-once` | Approve for single execution |
| POST | `/approvals/{id}/approve-session` | Approve for session duration |
| POST | `/approvals/{id}/reject` | Deny this request |
| POST | `/approvals/{id}/reject-remember` | Deny + permanently block capability |
| GET | `/health` | Health check |

### Dashboard SSE Approval

Approval requests are pushed to the dashboard via Server-Sent Events.
Users can approve/reject directly from the dashboard UI.

### PC Server Overlay

Custom click-through overlay windows with keyboard-only interaction (Y/N/ESC).
Uses `WS_EX_TOPMOST | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW`
with `GetAsyncKeyState` for global keyboard capture.

## Running

```bash
cd ai-server
python -c "
from aegis_ai.web.app import ApprovalWebApp
from approval import ApprovalStore
store = ApprovalStore()
app = ApprovalWebApp(store)
app.run(host='0.0.0.0', port=8080)
"
```

## Security

| Concern | Mitigation |
|---------|-----------|
| CSRF | Per-request CSRF tokens in POST forms |
| Approval ID guessing | UUID-based (64-bit entropy) |
| Secret exposure | Payload preview masks password/token/secret values |
| External access | Default `0.0.0.0` only |
| Expired approvals | `is_expired()` check before any action; UI disables buttons |
| Permanent denial | `reject_and_remember` blocks capability permanently |

## What the AI Cannot Do

- The AI has NO access to the Approval UI endpoints
- `ToolBroker.invoke_tool_approved()` requires a valid approval in the store
- The AI cannot create fake approval records
- `PolicyEngine` controls are structural, not prompt-based
- Support Agent does NOT bypass PolicyEngine / Approval UI
