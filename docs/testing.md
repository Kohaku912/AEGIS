# Testing Guide

> **Status**: Active (2026-06-11)
> **Related**: `AGENTS.md` §Testing Policy

## Quick Reference

```bash
# AI Server — all tests
cd ai-server && pytest

# AI Server — Android E2E (CI-safe, mock provider)
cd ai-server && pytest tests/test_android_observe_e2e.py -v

# AI Server — Android local (real ADB device)
cd ai-server && pytest -m android_local -v

# AI Server — PC E2E (CI-safe, mock provider)
cd ai-server && pytest tests/test_pc_observe_e2e.py -v

# AI Server — PC local (real screenshot, real window)
cd ai-server && pytest -m pc_local -v

# AI Server — Room E2E (CI-safe, mock provider)
cd ai-server && pytest tests/test_room_observe_e2e.py -v

# AI Server — lint
cd ai-server && ruff check .

# AI Server — format
cd ai-server && ruff format .

# Android Server — Kotlin unit tests
cd android-server && ./gradlew test
```

## Test Categories

### Unit Tests

Test individual modules in isolation. No external dependencies.

- `test_event_bus.py` — EventBus publish/subscribe, dedup, priority queue
- `test_trigger_engine.py` — TriggerRule matching, cooldown, TaskRequest generation
- `test_policy_engine.py` — PolicyEngine safety levels, deny/approval patterns
- `test_approval.py` — ApprovalStore lifecycle (create, approve, reject, expire)
- `test_tool_registry.py` — ToolRegistry server/capability CRUD
- `test_tool_broker.py` — ToolBroker invocation with policy enforcement
- `test_audit.py` — AuditLog append/read
- `test_capability_schema.py` — Pydantic model validation

### E2E Integration Tests

Test full stack wiring with mock providers.

- `test_android_observe_e2e.py` — Android Server → EventBus → TriggerEngine → ContextBuilder
  - Capability registration
  - Notification redaction (OTP, cards, emails, phones, passwords)
  - Allowlist / denylist filtering
  - Sensitive app detection (redacted-only storage)
  - EventBus push and deduplication
  - TriggerEngine cooldown and rule matching
  - ContextBuilder integration
  - PolicyEngine read-only allow
  - AuditLog recording
  - Graceful failure (device down, not registered)
  - Retry/backoff
- `test_pc_observe_e2e.py` — PC Server → EventBus → TriggerEngine → ContextBuilder
- `test_room_observe_e2e.py` — Room Server → EventBus → TriggerEngine → ContextBuilder
  - Health check, capability registration
  - Mock sensor read (temperature, humidity, brightness, motion)
  - Environment aggregation, threshold detection
  - Dedupe, cooldown, EventBus push
  - Provider unavailable graceful failure
  - PolicyEngine read-only allow
  - AuditLog, retry/backoff
- `test_research_e2e.py` — Research Agent full pipeline
- `test_research_approval_e2e.py` — Level 2/3 operations blocked in research

### Local-Only Tests (require real device)

Skipped in CI. Run manually with marker flags.

- `test_android_local.py` — ADB provider with real Android device
  - Requires: ADB installed, device connected, USB debugging enabled
  - Run: `pytest -m android_local -v`
- `test_pc_observe_e2e.py` (marked `pc_local`) — Real screenshot, real active window
  - Run: `pytest -m pc_local -v`

### Kotlin Unit Tests

```bash
cd android-server
./gradlew test
```

## CI Configuration

### pytest markers

Defined in `ai-server/pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "e2e: End-to-end integration tests (approval flow, autonomous loop)",
    "pc_local: PC Server local-only tests (real screenshot, real active window)",
    "android_local: Android Server local-only tests (real ADB device)",
    "room_local: Room Server local-only tests (real sensor hardware)",
]
```

### CI pipeline (planned)

1. `pytest` — all tests except `*_local` markers
2. `ruff check .` — lint
3. `ruff format --check .` — format check
4. Kotlin: `./gradlew test` — Android Server unit tests

## Test Coverage Targets

| Module | Target | Notes |
|--------|--------|-------|
| Schema models | >90% | Validation is critical |
| Policy Engine | >90% | Safety is critical |
| EventBus | >85% | Core event flow |
| TriggerEngine | >85% | Rule matching + cooldown |
| ToolBroker | >85% | Invocation + policy enforcement |
| Android E2E | >80% | Full integration coverage |
| Room E2E | >80% | Full integration coverage |

## Writing New Tests

### Python style

- Use `pytest` (not `unittest`)
- Test classes: `TestXxx` with `test_xxx` methods
- Helpers: module-level `_make_xxx()` functions
- Fixtures: prefer inline setup over `conftest.py` for simple cases
- Assertions: `assert x == y` (not `self.assertEqual`)

### Android E2E pattern

```python
def _setup_full_stack():
    """Wire up the full AEGIS Core stack for E2E testing."""
    bus = EventBus()
    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)
    registry = ToolRegistry()
    policy = create_default_policy_engine()
    broker = ToolBroker(registry, policy)
    audit = AuditLog(path="data/test_audit.jsonl")
    builder = ContextBuilder(event_bus=bus, tool_broker=broker)
    provider = MockAndroidProvider()
    client = AndroidServerClient(bus, registry, provider)
    bus.subscribe(engine.on_event)
    return bus, engine, registry, policy, broker, builder, audit, client
```
