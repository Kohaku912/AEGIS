# Plugin SDK — AEGIS Capability Developer Kit

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
    server_prefix="weather",
    action="get_forecast",
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

Use the scaffold generator:

```bash
cd tools/create-capability-server
python create_server.py --name weather --type room --port 50060
```

This creates:
- Server implementation with capability registration
- Test skeleton
- README
