# Testing Guide

> **Status**: Active (verified against current code snapshot)
> **Related**: `AGENTS.md` §Testing Policy
> **Total Tests**: 157 passed, 0 failed

## Quick Reference

```bash
# AI Server — all tests
cd ai-server && uv run python -m pytest ../tests/ -v --tb=short

# AI Server — lint
cd ai-server && ruff check .

# AI Server — format
cd ai-server && ruff format .

# PC Server — Rust unit tests
cd pc-server && cargo test && cargo clippy
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
- `test_pc_observe_e2e.py` — PC Server → EventBus → TriggerEngine → ContextBuilder
- `test_room_observe_e2e.py` — Room Server → EventBus → TriggerEngine → ContextBuilder
- `test_research_e2e.py` — Research Agent full pipeline
- `test_research_approval_e2e.py` — Level 2/3 operations blocked in research
- `test_autonomous_loop_e2e.py` — AutonomousLoop desire-driven scheduling, Planner task generation, CuriosityDrivenExploration
- `test_learning_pipeline_e2e.py` — ActionTrace → Lesson → Workflow → Skill pipeline
- `test_sleep_consolidation_e2e.py` — SleepConsolidation memory maintenance

### E2E Lifecycle Tests (Runtime Stabilization)

- `test_e2e_lifecycle.py` — 8 tests covering:
  - Full approval lifecycle: create → start → wait_approval → approve → resume → complete
  - Concurrent approval tasks
  - All manager integrations (TaskManager, MemoryManager, EventManager, AuditManager, StatusManager, NotificationManager, SleepManager)
  - Uses `SimpleNamespace`-based mock runtime with real Manager instances

### Local-Only Tests (require real device)

Skipped in CI. Run manually with marker flags.

- `test_android_local.py` — ADB provider with real Android device
  - Requires: ADB installed, device connected, USB debugging enabled
- `test_pc_observe_e2e.py` (marked `pc_local`) — Real screenshot, real active window

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

## Current Test Commands

Use a workspace basetemp on Windows to avoid temp permission problems:

```powershell
cd ai-server
.\.venv\Scripts\python.exe -m pytest --basetemp .tmp-pytest -p no:cacheprovider
```

Focused checks for audit/chat/autonomous changes:

```powershell
cd ai-server
.\.venv\Scripts\python.exe -m pytest --basetemp .tmp-pytest-audit -p no:cacheprovider tests\test_dashboard_routes.py tests\test_chat_tools.py tests\test_approval_redesign.py tests\test_autonomous_loop_behavior.py
.\.venv\Scripts\python.exe -m pytest --basetemp .tmp-pytest-audit -p no:cacheprovider tests\test_runtime_singleton.py tests\test_e2e_lifecycle.py
```

Generated pytest directories such as `.pytest-tmp/` and `.tmp-pytest-*` are not source files and should not be committed.
```
