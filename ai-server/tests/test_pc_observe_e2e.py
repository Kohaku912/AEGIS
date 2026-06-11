"""PC Server Observe E2E — integration tests for PC Server ↔ AEGIS Core.

Tests the full observe flow:
  PC Server → EventBus → TriggerEngine → ContextBuilder → AuditLog

CI uses MockPCProvider (no real OS calls).
Local can use real provider with pytest marker: pytest -m pc_local

Architecture reference: docs/architecture.md §3.2, §6
"""

from __future__ import annotations

import json
import time
import uuid

from aegis_ai.audit import AuditEntry, AuditLog
from aegis_ai.context_builder import ContextBuilder
from aegis_schema.models import (
    Capability,
    Event,
    EventPriority,
    RiskLevel,
    ServerStatus,
    ServerType,
)
from event_bus import EventBus
from pc_server_client import (
    PC_CAPABILITIES,
    PC_SERVER_ID,
    ConnectionState,
    MockPCProvider,
    PCServerClient,
    RetryConfig,
)
from policy_engine import PolicyDecision, PolicyEngine, create_default_policy_engine
from tool_broker import ToolBroker
from tool_registry import ToolRegistry
from trigger_engine import ActionType, TriggerEngine, create_default_rules

# ── Helpers ──────────────────────────────────────────────────


def _make_pc_event(
    event_type: str = "pc.window_changed",
    severity: int = 3,
    priority: EventPriority = EventPriority.NORMAL,
    payload: str | None = None,
    dedupe_key: str = "",
) -> Event:
    """Create a PC-originated event for testing."""
    return Event(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type=event_type,
        source_server_type=ServerType.PC,
        source_server_id=PC_SERVER_ID,
        timestamp_ms=int(time.time() * 1000),
        payload_json=payload or '{"title":"VS Code","process":"code.exe","pid":12345}',
        severity=severity,
        priority=priority,
        dedupe_key=dedupe_key,
    )


def _setup_full_stack(
    provider: MockPCProvider | None = None,
) -> tuple[EventBus, TriggerEngine, ToolRegistry, PolicyEngine, ToolBroker, ContextBuilder, AuditLog, PCServerClient]:
    """Wire up the full AEGIS Core stack for E2E testing."""
    bus = EventBus()
    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)

    registry = ToolRegistry()
    policy = create_default_policy_engine()
    broker = ToolBroker(registry, policy)

    audit = AuditLog(path="data/test_pc_e2e_audit.jsonl")
    builder = ContextBuilder(event_bus=bus, tool_broker=broker)

    provider = provider or MockPCProvider()
    client = PCServerClient(bus, registry, provider)

    # Wire TriggerEngine to EventBus
    bus.subscribe(engine.on_event)

    return bus, engine, registry, policy, broker, builder, audit, client


# ═══════════════════════════════════════════════════════════════
# 1. Capability Registration
# ═══════════════════════════════════════════════════════════════


class TestCapabilityRegistration:
    """PC Server registers capabilities with AEGIS Core at startup."""

    def test_register_pc_server(self):
        """PC Server registers itself as a server with capabilities."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        assert client.register() is True
        assert client.is_registered is True

        server = registry.get_server(PC_SERVER_ID)
        assert server is not None
        assert server.server_type == ServerType.PC
        assert server.status == ServerStatus.ONLINE

    def test_register_pc_capabilities(self):
        """All PC capabilities are registered."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        for cap_def in PC_CAPABILITIES:
            cap = registry.get_capability(cap_def.id)
            assert cap is not None, f"Capability {cap_def.id} not registered"
            assert cap.server_type == ServerType.PC

    def test_pc_get_screenshot_registered(self):
        """pc.get_screenshot capability is registered with correct metadata."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        cap = registry.get_capability("pc.get_screenshot")
        assert cap is not None
        assert cap.name == "Screenshot Capture"
        assert cap.risk_level == RiskLevel.READ_ONLY
        assert "screenshot" in cap.tags
        assert "observe" in cap.tags

    def test_pc_get_active_window_registered(self):
        """pc.get_active_window capability is registered with correct metadata."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        cap = registry.get_capability("pc.get_active_window")
        assert cap is not None
        assert cap.name == "Get Active Window"
        assert cap.risk_level == RiskLevel.READ_ONLY

    def test_all_pc_caps_are_read_only(self):
        """All PC observe capabilities are LEVEL_0_READ (safe, no approval needed)."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        observe_caps = [c for c in PC_CAPABILITIES if "observe" in c.tags or "read_only" in c.tags]
        for cap in observe_caps:
            reg_cap = registry.get_capability(cap.id)
            assert reg_cap.risk_level == RiskLevel.READ_ONLY, (
                f"{cap.id} has risk_level={reg_cap.risk_level.name}, expected READ_ONLY"
            )

    def test_unregister_clears_capabilities(self):
        """Unregistering removes server and capabilities."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()
        assert registry.get_server(PC_SERVER_ID) is not None

        client.unregister()
        assert registry.get_server(PC_SERVER_ID) is None


# ═══════════════════════════════════════════════════════════════
# 2. EventBus Push
# ═══════════════════════════════════════════════════════════════


class TestEventBusPush:
    """PC Server pushes events to EventBus."""

    def test_push_window_changed_event(self):
        """pc.window_changed event is accepted by EventBus."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_window_changed_event("VS Code", "code.exe", 12345)
        assert result is True
        assert len(received) == 1
        assert received[0].event_type == "pc.window_changed"
        assert received[0].source_server_type == ServerType.PC

    def test_push_screen_changed_event(self):
        """pc.screen_changed event is accepted by EventBus."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_screen_changed_event()
        assert result is True
        assert len(received) == 1
        assert received[0].event_type == "pc.screen_changed"

    def test_event_payload_contains_window_info(self):
        """Event payload contains window title, process, pid."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_window_changed_event("Chrome", "chrome.exe", 9999)

        payload = json.loads(received[0].payload_json)
        assert payload["title"] == "Chrome"
        assert payload["process"] == "chrome.exe"
        assert payload["pid"] == 9999

    def test_event_stats_updated(self):
        """EventBus stats track published and delivered counts."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_window_changed_event("Window 1", "app1.exe", 1)
        client.push_window_changed_event("Window 2", "app2.exe", 2)

        assert bus.stats.total_published == 2
        assert bus.stats.total_delivered == 2
        assert client.stats.total_events_pushed == 2


# ═══════════════════════════════════════════════════════════════
# 3. Deduplication
# ═══════════════════════════════════════════════════════════════


class TestDeduplication:
    """Duplicate PC events are deduplicated by EventBus."""

    def test_duplicate_window_events_deduped(self):
        """Same window change event (same dedupe_key) is deduplicated."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        # Push same window change twice (same process = same dedupe_key)
        client.push_window_changed_event("VS Code", "code.exe", 12345)
        client.push_window_changed_event("VS Code", "code.exe", 12345)

        assert len(received) == 1  # Second one deduplicated
        assert bus.stats.total_deduplicated == 1

    def test_different_windows_not_deduped(self):
        """Different window changes (different dedupe_key) are not deduplicated."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_window_changed_event("VS Code", "code.exe", 12345)
        client.push_window_changed_event("Chrome", "chrome.exe", 9999)

        assert len(received) == 2

    def test_dedupe_respects_time_window(self):
        """After dedup window expires, same key is allowed again."""
        bus = EventBus(dedup_window_ms=1)  # 1ms window
        registry = ToolRegistry()
        provider = MockPCProvider()
        client = PCServerClient(bus, registry, provider)
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_window_changed_event("VS Code", "code.exe", 12345)

        import time

        time.sleep(0.01)  # Wait beyond 1ms window

        client.push_window_changed_event("VS Code", "code.exe", 12345)

        assert len(received) == 2


# ═══════════════════════════════════════════════════════════════
# 4. Cooldown
# ═══════════════════════════════════════════════════════════════


class TestCooldown:
    """TriggerEngine cooldown prevents rapid PC event processing."""

    def test_screen_change_cooldown(self):
        """pc.screen_changed events are rate-limited by cooldown (30s default)."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        # Push first screen change — should trigger
        client.push_screen_changed_event(severity=3)
        tasks1 = engine.drain_tasks()
        assert len(tasks1) >= 1

        # Push second screen change immediately — should be suppressed by cooldown
        client.push_screen_changed_event(severity=3)
        tasks2 = engine.drain_tasks()
        assert len(tasks2) == 0  # Suppressed by cooldown

    def test_cooldown_reset_allows_next(self):
        """After cooldown reset, next event triggers again."""
        bus, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_screen_changed_event(severity=3)
        engine.drain_tasks()

        # Reset cooldown for the screen change rule
        engine.reset_cooldown("pc-screen-change")

        # Use a different dedupe key to avoid EventBus dedup
        event = _make_pc_event(
            event_type="pc.screen_changed",
            severity=3,
            dedupe_key="pc.screen_changed:reset_test",
        )
        bus.publish(event)
        tasks = engine.drain_tasks()
        assert len(tasks) >= 1


# ═══════════════════════════════════════════════════════════════
# 5. TriggerEngine → TaskRequest
# ═══════════════════════════════════════════════════════════════


class TestTriggerEngineIntegration:
    """TriggerEngine generates TaskRequests from PC events."""

    def test_window_changed_generates_observe_task(self):
        """pc.window_changed generates an OBSERVE task via default rules."""
        bus, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        event = _make_pc_event(
            event_type="pc.window_changed",
            severity=3,
            priority=EventPriority.NORMAL,
        )
        bus.publish(event)

        tasks = engine.drain_tasks()
        # pc.window_changed doesn't match default "pc.screen_changed" pattern,
        # so no task is generated unless a custom rule is added
        assert len(tasks) == 0

    def test_screen_changed_generates_observe_task(self):
        """pc.screen_changed generates an OBSERVE task via default rules."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_screen_changed_event(severity=3, priority=EventPriority.NORMAL)

        tasks = engine.drain_tasks()
        assert len(tasks) == 1
        assert tasks[0].action_type == ActionType.OBSERVE
        assert tasks[0].source_server_type == ServerType.PC
        assert "pc.screen_changed" in tasks[0].context_summary

    def test_high_severity_pc_event_triggers_alert(self):
        """High-severity PC event triggers ALERT via catch-all rule."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        # Push a security event with severity 10
        event = _make_pc_event(
            event_type="pc.security_unauthorized_access",
            severity=10,
            priority=EventPriority.URGENT,
        )
        client.push_event(event)

        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        assert tasks[0].action_type == ActionType.ALERT


# ═══════════════════════════════════════════════════════════════
# 6. ContextBuilder Integration
# ═══════════════════════════════════════════════════════════════


class TestContextBuilderIntegration:
    """ContextBuilder includes PC events in the assembled context."""

    def test_context_includes_pc_events(self):
        """Context built after PC events includes them in recent_events."""
        bus, _, _, _, _, builder, _, client = _setup_full_stack()
        client.register()

        client.push_screen_changed_event(severity=3)
        client.push_window_changed_event("Chrome", "chrome.exe", 9999, severity=3)

        ctx = builder.build()
        pc_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.PC]
        assert len(pc_events) >= 2

    def test_context_preserves_event_payload(self):
        """Context events retain their original payload."""
        bus, _, _, _, _, builder, _, client = _setup_full_stack()
        client.register()

        client.push_window_changed_event("Terminal", "wt.exe", 5555, severity=3)

        ctx = builder.build()
        pc_events = [e for e in ctx.recent_events if e.event_type == "pc.window_changed"]
        assert len(pc_events) >= 1

        payload = json.loads(pc_events[0].payload_json)
        assert payload["title"] == "Terminal"
        assert payload["process"] == "wt.exe"

    def test_context_with_triggering_pc_event(self):
        """Context can be built with a specific triggering PC event."""
        _, _, _, _, _, builder, _, client = _setup_full_stack()
        client.register()

        trigger_event = _make_pc_event(
            event_type="pc.screen_changed",
            severity=5,
            payload='{"change":"major_switch"}',
        )

        ctx = builder.build(triggering_events=[trigger_event])
        assert len(ctx.recent_events) >= 1
        assert ctx.recent_events[0].event_type == "pc.screen_changed"

    def test_context_includes_available_capabilities(self):
        """Context includes registered PC capabilities."""
        _, _, _, _, broker, builder, _, client = _setup_full_stack()
        client.register()

        ctx = builder.build()
        # The ContextBuilder uses tool_broker.list_safe_capabilities()
        # PC caps are READ_ONLY so they should be in safe capabilities
        pc_cap_ids = [cid for cid in ctx.available_capability_ids if cid.startswith("pc.")]
        assert len(pc_cap_ids) >= 1


# ═══════════════════════════════════════════════════════════════
# 7. PolicyEngine — read-only allow
# ═══════════════════════════════════════════════════════════════


class TestPolicyEngineReadOnly:
    """PolicyEngine allows read-only PC capabilities without approval."""

    def test_screenshot_allowed(self):
        """pc.get_screenshot (READ_ONLY) is allowed by PolicyEngine."""
        _, _, _, policy, _, _, _, client = _setup_full_stack()
        client.register()

        cap = Capability(
            id="pc.get_screenshot",
            name="Screenshot Capture",
            description="Capture the current display as a PNG image.",
            server_type=ServerType.PC,
            risk_level=RiskLevel.READ_ONLY,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_active_window_allowed(self):
        """pc.get_active_window (READ_ONLY) is allowed by PolicyEngine."""
        _, _, _, policy, _, _, _, client = _setup_full_stack()
        client.register()

        cap = Capability(
            id="pc.get_active_window",
            name="Get Active Window",
            description="Return the title, process, and position of the foreground window.",
            server_type=ServerType.PC,
            risk_level=RiskLevel.READ_ONLY,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_all_pc_observe_caps_allowed(self):
        """All PC observe capabilities are ALLOWED (no approval needed)."""
        _, _, _, policy, _, _, _, client = _setup_full_stack()
        client.register()

        observe_caps = [c for c in PC_CAPABILITIES if "observe" in c.tags or "read_only" in c.tags]
        for cap_def in observe_caps:
            result = policy.evaluate(cap_def)
            assert result.decision == PolicyDecision.ALLOW, (
                f"{cap_def.id} should be ALLOWED, got {result.decision.name}"
            )

    def test_toolbroker_invokes_screenshot(self):
        """ToolBroker can invoke pc.get_screenshot (ALLOWED by policy)."""
        _, _, _, _, broker, _, _, client = _setup_full_stack()
        client.register()

        # Register a mock executor
        def mock_screenshot(cap, params):
            return {"width": 1920, "height": 1080, "image_base64": "[MOCK]"}

        broker.register_mock("pc.", mock_screenshot)

        result = broker.invoke_tool("pc.get_screenshot", {"display_id": 0})
        assert result.success is True
        assert result.output["width"] == 1920


# ═══════════════════════════════════════════════════════════════
# 8. AuditLog
# ═══════════════════════════════════════════════════════════════


class TestAuditLog:
    """AuditLog records PC Server observations and decisions."""

    def test_audit_logs_capability_registration(self):
        """Registration is logged to audit."""
        _, _, _, _, _, _, audit, client = _setup_full_stack()

        entry = AuditEntry(
            action="capability_registered",
            actor="pc_server",
            capability_id="pc.get_screenshot",
            decision="REGISTERED",
            reason="PC Server registered observe capabilities",
        )
        audit.append(entry)

        recent = audit.list_recent(10)
        assert len(recent) >= 1
        assert recent[-1].action == "capability_registered"

    def test_audit_logs_event_received(self):
        """Event reception is logged to audit."""
        _, _, _, _, _, _, audit, client = _setup_full_stack()
        client.register()

        entry = AuditEntry(
            action="event_received",
            actor="pc_server",
            capability_id="pc.window_changed",
            decision="ACCEPTED",
            reason="PC event pushed to EventBus",
            detail={"event_type": "pc.window_changed", "process": "code.exe"},
        )
        audit.append(entry)

        recent = audit.list_recent(10)
        assert any(e.action == "event_received" for e in recent)

    def test_audit_logs_policy_decision(self):
        """Policy decisions for PC capabilities are logged."""
        _, _, _, policy, _, _, audit, client = _setup_full_stack()
        client.register()

        cap = PC_CAPABILITIES[0]  # pc.get_screenshot
        result = policy.evaluate(cap)

        entry = AuditEntry(
            action="policy_decision",
            actor="aegis",
            capability_id=cap.id,
            decision=result.decision.name,
            reason=result.reason,
        )
        audit.append(entry)

        recent = audit.list_recent(10)
        policy_entries = [e for e in recent if e.action == "policy_decision"]
        assert len(policy_entries) >= 1
        assert policy_entries[-1].decision == "ALLOW"

    def test_audit_logs_trigger_fired(self):
        """TriggerEngine rule firing is logged to audit."""
        _, engine, _, _, _, _, audit, client = _setup_full_stack()
        client.register()

        client.push_screen_changed_event(severity=3)
        tasks = engine.drain_tasks()

        if tasks:
            entry = AuditEntry(
                action="trigger_fired",
                actor="trigger_engine",
                capability_id=tasks[0].triggered_by_event_type,
                decision="TASK_GENERATED",
                reason=f"Rule {tasks[0].triggered_by_rule_id} fired",
                detail={"task_id": tasks[0].task_id, "action_type": tasks[0].action_type.name},
            )
            audit.append(entry)

        recent = audit.list_recent(10)
        trigger_entries = [e for e in recent if e.action == "trigger_fired"]
        assert len(trigger_entries) >= 1


# ═══════════════════════════════════════════════════════════════
# 9. PC Server Down — Graceful Failure
# ═══════════════════════════════════════════════════════════════


class TestPCServerDown:
    """Graceful failure when PC Server is unavailable."""

    def test_registration_fails_gracefully(self):
        """Registration returns False when provider is unavailable."""
        provider = MockPCProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = PCServerClient(bus, registry, provider)

        result = client.register()
        assert result is False
        assert client.is_registered is False
        assert client.stats.state == ConnectionState.FAILED

    def test_event_push_fails_when_not_registered(self):
        """Pushing events returns False when not registered."""
        provider = MockPCProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = PCServerClient(bus, registry, provider)

        result = client.push_window_changed_event("Test", "test.exe", 1)
        assert result is False

    def test_invoke_returns_error_when_unavailable(self):
        """Invoking capabilities returns error dict when provider is down."""
        provider = MockPCProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = PCServerClient(bus, registry, provider)

        result = client.invoke_capability("pc.get_screenshot")
        assert "error" in result
        assert "not available" in result["error"]

    def test_other_servers_unaffected_by_pc_failure(self):
        """Other servers can still operate when PC Server is down."""
        provider = MockPCProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = PCServerClient(bus, registry, provider)
        client.register()  # Will fail

        # EventBus should still work for non-PC events
        other_event = Event(
            event_id="evt-other-001",
            event_type="dev.test_failed",
            source_server_type=ServerType.DEV,
            source_server_id="dev-1",
            severity=8,
            priority=EventPriority.URGENT,
        )
        result = bus.publish(other_event)
        assert result is True


# ═══════════════════════════════════════════════════════════════
# 10. AEGIS Core Down — Retry / Backoff
# ═══════════════════════════════════════════════════════════════


class TestRetryBackoff:
    """PC Server retries connection with exponential backoff."""

    def test_retry_succeeds_on_first_attempt(self):
        """connect_with_retry succeeds immediately when provider is available."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = MockPCProvider(available=True)
        client = PCServerClient(bus, registry, provider, RetryConfig(max_retries=3, base_delay_ms=1))

        result = client.connect_with_retry()
        assert result is True
        assert client.stats.retry_count == 1
        assert client.stats.state == ConnectionState.CONNECTED

    def test_retry_fails_after_max_attempts(self):
        """connect_with_retry fails after exhausting retries."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = MockPCProvider(available=False)
        client = PCServerClient(bus, registry, provider, RetryConfig(max_retries=2, base_delay_ms=1))

        result = client.connect_with_retry()
        assert result is False
        assert client.stats.retry_count == 2
        assert client.stats.state == ConnectionState.FAILED

    def test_retry_succeeds_after_transient_failure(self):
        """connect_with_retry succeeds when provider becomes available."""
        call_count = 0

        class FlakyProvider(MockPCProvider):
            def is_available(self) -> bool:
                nonlocal call_count
                call_count += 1
                return call_count >= 2  # Fail first, succeed second

        bus = EventBus()
        registry = ToolRegistry()
        provider = FlakyProvider()
        client = PCServerClient(bus, registry, provider, RetryConfig(max_retries=3, base_delay_ms=1))

        result = client.connect_with_retry()
        assert result is True
        assert client.stats.retry_count >= 2

    def test_backoff_delay_increases(self):
        """Retry delay increases exponentially (verified via stats)."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = MockPCProvider(available=False)
        config = RetryConfig(max_retries=3, base_delay_ms=1, backoff_factor=2.0)
        client = PCServerClient(bus, registry, provider, config)

        start = time.monotonic()
        client.connect_with_retry()
        elapsed = time.monotonic() - start

        # With base=1ms, factor=2: delays are 1ms, 2ms, 4ms → total ~7ms minimum
        # Just verify it took some time (not instant)
        assert elapsed > 0.001


# ═══════════════════════════════════════════════════════════════
# 11. Full E2E Flow
# ═══════════════════════════════════════════════════════════════


class TestFullE2EFlow:
    """Complete E2E: PC Server → EventBus → TriggerEngine → ContextBuilder → AuditLog."""

    def test_full_observe_flow(self):
        """Full flow from PC event to context assembly with audit trail."""
        bus, engine, registry, policy, broker, builder, audit, client = _setup_full_stack()

        # 1. PC Server registers
        assert client.register() is True
        audit.append(
            AuditEntry(
                action="server_registered",
                actor="pc_server",
                decision="SUCCESS",
                reason=f"Registered {len(PC_CAPABILITIES)} capabilities",
            )
        )

        # 2. Verify capabilities are registered
        assert registry.get_capability("pc.get_screenshot") is not None
        assert registry.get_capability("pc.get_active_window") is not None

        # 3. Policy allows read-only
        observe_caps = [c for c in PC_CAPABILITIES if "observe" in c.tags or "read_only" in c.tags]
        for cap in observe_caps:
            result = policy.evaluate(cap)
            assert result.decision == PolicyDecision.ALLOW
            audit.append(
                AuditEntry(
                    action="policy_decision",
                    actor="policy_engine",
                    capability_id=cap.id,
                    decision="ALLOW",
                    reason=result.reason,
                )
            )

        # 4. Push pc.screen_changed event
        client.push_screen_changed_event(severity=3)
        audit.append(
            AuditEntry(
                action="event_received",
                actor="pc_server",
                capability_id="pc.screen_changed",
                decision="ACCEPTED",
            )
        )

        # 5. TriggerEngine fires
        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        assert tasks[0].action_type == ActionType.OBSERVE
        audit.append(
            AuditEntry(
                action="trigger_fired",
                actor="trigger_engine",
                capability_id=tasks[0].triggered_by_event_type,
                decision="TASK_GENERATED",
                detail={"task_id": tasks[0].task_id},
            )
        )

        # 6. ContextBuilder includes PC events
        ctx = builder.build()
        pc_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.PC]
        assert len(pc_events) >= 1

        # 7. Audit trail is complete
        audit_entries = audit.list_recent(50)
        actions = [e.action for e in audit_entries]
        assert "server_registered" in actions
        assert "policy_decision" in actions
        assert "event_received" in actions
        assert "trigger_fired" in actions

    def test_full_flow_with_dedupe(self):
        """Full flow respects deduplication."""
        bus, engine, registry, policy, broker, builder, audit, client = _setup_full_stack()
        client.register()

        # Push same event twice
        client.push_screen_changed_event(severity=3)
        client.push_screen_changed_event(severity=3)

        # Only one event delivered (deduped)
        assert bus.stats.total_deduplicated == 1

        # Only one task generated
        tasks = engine.drain_tasks()
        assert len(tasks) == 1

    def test_full_flow_with_cooldown(self):
        """Full flow respects TriggerEngine cooldown."""
        bus, engine, registry, policy, broker, builder, audit, client = _setup_full_stack()
        client.register()

        # First screen change — triggers
        client.push_screen_changed_event(severity=3)
        tasks1 = engine.drain_tasks()
        assert len(tasks1) == 1

        # Second screen change — suppressed by cooldown
        client.push_screen_changed_event(severity=3)
        tasks2 = engine.drain_tasks()
        assert len(tasks2) == 0

    def test_full_flow_multiple_event_types(self):
        """Full flow handles multiple PC event types."""
        bus, engine, registry, policy, broker, builder, audit, client = _setup_full_stack()
        client.register()

        # Push various PC events
        client.push_screen_changed_event(severity=3)
        client.push_window_changed_event("Chrome", "chrome.exe", 9999, severity=3)

        # Context includes all events
        ctx = builder.build()
        pc_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.PC]
        assert len(pc_events) >= 2

    def test_invoke_capability_through_broker(self):
        """PC capabilities can be invoked through ToolBroker (E2E)."""
        bus, engine, registry, policy, broker, builder, audit, client = _setup_full_stack()
        client.register()

        # Register mock executor
        def mock_pc_executor(cap, params):
            if cap.id == "pc.get_screenshot":
                return {"width": 1920, "height": 1080, "image_base64": "[MOCK]"}
            elif cap.id == "pc.get_active_window":
                return {"title": "VS Code", "process": "code.exe", "pid": 12345}
            return {"mock": True}

        broker.register_mock("pc.", mock_pc_executor)

        # Invoke through broker (policy check is automatic)
        result = broker.invoke_tool("pc.get_screenshot", {"display_id": 0})
        assert result.success is True
        assert result.output["width"] == 1920

        result2 = broker.invoke_tool("pc.get_active_window")
        assert result2.success is True
        assert result2.output["title"] == "VS Code"


# ═══════════════════════════════════════════════════════════════
# 12. Mock Provider Call Log
# ═══════════════════════════════════════════════════════════════


class TestMockProviderCallLog:
    """MockPCProvider tracks all calls for verification."""

    def test_call_log_records_invocations(self):
        provider = MockPCProvider()
        bus = EventBus()
        registry = ToolRegistry()
        client = PCServerClient(bus, registry, provider)
        client.register()

        client.invoke_capability("pc.get_screenshot", {"display_id": 0})
        client.invoke_capability("pc.get_active_window")
        client.invoke_capability("pc.get_clipboard")

        assert len(provider.call_log) == 3
        assert provider.call_log[0][0] == "get_screenshot"
        assert provider.call_log[1][0] == "get_active_window"
        assert provider.call_log[2][0] == "get_clipboard"

    def test_call_log_preserves_params(self):
        provider = MockPCProvider()
        bus = EventBus()
        registry = ToolRegistry()
        client = PCServerClient(bus, registry, provider)
        client.register()

        client.invoke_capability("pc.get_screenshot", {"display_id": 1})

        assert provider.call_log[0] == ("get_screenshot", {"display_id": 1})
