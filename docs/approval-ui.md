# Approval UI — Design & Usage

> **Status**: Phase 3.4 — Minimal implementation (2026-06-11)  
> **Related**: [`architecture.md`](architecture.md) §7.4, [`AGENTS.md`](../AGENTS.md) Security Policy

## Overview

The Approval UI is a Flask-based web application that presents pending approval requests to the user. When AEGIS attempts a Level 2/3 operation, the PolicyEngine creates an `ApprovalRequest` in the `ApprovalStore`. The user can view, approve, or reject these requests.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/approvals` | List all pending approvals |
| GET | `/approvals/{id}` | Detail view for one approval |
| POST | `/approvals/{id}/approve-once` | Approve for single execution |
| POST | `/approvals/{id}/approve-session` | Approve for session duration |
| POST | `/approvals/{id}/reject` | Deny this request |
| POST | `/approvals/{id}/reject-remember` | Deny + permanently block capability |
| GET | `/health` | Health check |

## Running

```bash
cd ai-server
python -c "
from aegis_ai.web.app import ApprovalWebApp
from approval import ApprovalStore
store = ApprovalStore()
app = ApprovalWebApp(store)
app.run(host='127.0.0.1', port=8080)
"
```

## Security

| Concern | Mitigation |
|---------|-----------|
| CSRF | Per-request CSRF tokens in POST forms |
| Approval ID guessing | UUID-based (64-bit entropy) |
| Secret exposure | Payload preview masks password/token/secret values |
| External access | Default `127.0.0.1` only |
| Expired approvals | `is_expired()` check before any action; UI disables buttons |
| Permanent denial | `reject_and_remember` blocks capability permanently |

## What the AI Cannot Do

- The AI has NO access to the Approval UI endpoints
- `ToolBroker.invoke_tool_approved()` requires a valid approval in the store
- The AI cannot create fake approval records
- `PolicyEngine` controls are structural, not prompt-based
