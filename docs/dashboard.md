# Operations Dashboard

> **Status**: Implemented
> **Related**: `docs/architecture.md`, `docs/settings.md`, `docs/permissions.md`

## Overview

The Operations Dashboard provides a web-based view of AEGIS's internal state.
It is read-only and cannot bypass any safety mechanisms.

## Screens

### Home (`/`)
- AEGIS Core status
- Connected servers count
- Pending approvals
- Recent errors
- Autonomous mode status
- Memory summary

### Servers (`/dashboard/servers`)
- PC / Android / Browser / Room / Dev server status
- Last heartbeat
- Registered capabilities count
- Version and host info

### Capabilities (`/dashboard/capabilities`)
- Capability list with usage stats
- Safety level
- Success/failure count
- Average latency

### Events (`/dashboard/events`)
- EventBus recent events
- Source, type, severity, priority
- Deduplication stats
- Queue size

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
- Procedural memories
- Reflections

### Audit (`/dashboard/audit`)
- Policy decisions
- Approvals
- Tool invocations
- Settings changes

### Errors (`/dashboard/errors`)
- Structured error list
- Recent denials and failures

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard/overview` | GET | JSON overview of all systems |
| `/api/dashboard/events` | GET | Recent events as JSON |
| `/api/dashboard/capabilities` | GET | Capability list as JSON |
| `/health` | GET | Dashboard health check |

## Security

- **localhost only** — dashboard runs on 127.0.0.1:8090
- **No external exposure** by default
- **Sensitive payload redaction** — passwords, tokens, secrets are masked
- **Read-only** — dashboard cannot execute actions
- **Cannot bypass approval** — all actions still go through PolicyEngine
- **Audit trail** — all dashboard access is logged

## Running

```bash
cd ai-server
python -c "
from aegis_ai.web.dashboard_routes import DashboardApp
app = DashboardApp()
app.run(host='127.0.0.1', port=8090)
"
```

Or integrate with main AEGIS startup.
