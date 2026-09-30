# Plugin SDK — AEGIS Capability Developer Kit

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).


> **Status**: Implemented
> **Location**: `packages/aegis-sdk-python/`

## Overview

The AEGIS Plugin SDK provides tools for building capability servers that integrate
with AEGIS Core. It handles capability definition, safety validation, server
registration, event publishing, and testing.

## Quick Start

```python
from aegis_sdk import define_capability, RegistrationClient, EventClient
from aegis_schema.models import RiskLevel, ServerType

# Define a capability
cap = define_capability(
    server_prefix="room-server",
    action="weather.get_forecast",
    name="Get Weather Forecast",
    description="Retrieve weather forecast for a location.",
    risk_level=RiskLevel.READ_ONLY,
    tags=["weather", "observe"],
)

# Register with AEGIS Core
client = RegistrationClient(
    server_id="weather-server",
    server_type=ServerType.ROOM,
)
client.register_server(registry)
client.register_capability(registry, cap)

# Publish events
events = EventClient(ServerType.ROOM, "weather-server")
events.publish(event_bus, "weather.forecast_updated", {"temp_c": 25})
```

### What `server_prefix` may be

A capability id is namespaced by the AEGIS server that **hosts** the capability, and AEGIS's
roster of servers is fixed — so `server_prefix` must be one of `aegis_sdk.ALLOWED_SERVER_PREFIXES`
(`ai`, `ai-server`, `pc`, `pc-server`, `android`, `android-server`, `browser`, `browser-server`,
`room`, `room-server`, `dev`, `dev-server`).

**Your own prefix is refused, by name, at the call site.** `server_prefix="weather"` raises
`ValueError: ... 'weather' is not an AEGIS server ...` rather than surfacing a pydantic error
about a `server_type` you never chose — an id outside the roster cannot be registered or invoked
anyway, so the SDK says so immediately. Put your own namespace in `action`: the example above
builds `room-server.weather.get_forecast`, and `server_type` is derived from the prefix (you do
not pass it).

The canonical id shape is `{server_id}.{app_id}.{action}`, e.g.
`room-server.weather.get_forecast`; the short prefix (`room`) is an accepted alias.

## SDK Components

### define_capability (capability.py)

Safe capability definition with validation:
- Requires `risk_level` (UNSPECIFIED/FORBIDDEN rejected)
- Requires `description`
- Level 2+ requires `side_effects`
- Rejects forbidden patterns
- Auto-sets `requires_approval` for Level 2+

### RegistrationClient (registration.py)

Server and capability registration:
- `register_server()` — register with ToolRegistry
- `register_capability()` — register capability
- `heartbeat()` — update heartbeat timestamp
- `unregister()` — remove server and capabilities

### EventClient (events.py)

Event publishing with structured helpers:
- `publish()` — publish event to EventBus
- `publish_state_change()` — publish state change event
- `make_event()` — create structured event
- `make_dedupe_key()` — create deduplication key

### Safety Validator (safety.py)

Validates capability definitions:
- Rejects UNSPECIFIED/FORBIDDEN risk levels
- Rejects missing description
- Rejects forbidden patterns (send_sns, delete_file, etc.)
- Warns about dangerous names
- Requires side_effects for Level 2+

### Test Harness (testing.py)

Mock AEGIS Core for testing:
- `MockAEGISCore` — simulates ToolRegistry, EventBus, PolicyEngine
- `run_capability_registration_check()` — test registration flow
- `run_policy_flow_check()` — test policy enforcement
- `run_event_push_check()` — test event publishing

## Testing

```bash
cd packages/aegis-sdk-python
pytest tests/ -v
```

## Creating a New Capability Server

Use the scaffold generator. It reads the server roster from `aegis_schema` to derive the
capability prefix, so that must be importable — run it from the repo root with `ai-server/src`
on `PYTHONPATH`:

```bash
PYTHONPATH=ai-server/src python tools/create-capability-server/create_server.py \
    --name weather --type room --port 50060
```

`--type` selects which AEGIS server hosts the generated capabilities, so it is also the
`server_prefix` they are built with (`--type room` → `room-server.<name>.<action>`); an unknown
`--type` is refused rather than written into a file that will not import. `--name` only names
the server and its files.

This creates three files:
- `{name}_server.py` — server implementation with capability registration
- `tests/test_{name}_server.py` — test skeleton
- `README.md`
