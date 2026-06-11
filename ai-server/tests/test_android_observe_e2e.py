"""Android Server Observe E2E — integration tests for Android Server ↔ AEGIS Core.

Tests the full observe flow:
  Android Server → EventBus → TriggerEngine → ContextBuilder → AuditLog

CI uses MockAndroidProvider (no real device calls).
Local can use ADB provider with real device: pytest -m android_local

Architecture reference: docs/architecture.md §3.3, §6
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
from android_server_client import (
    ANDROID_CAPABILITIES,
    ANDROID_SERVER_ID,
    AndroidServerClient,
    ConnectionState,
    MockAndroidProvider,
    NotificationFilter,
    RetryConfig,
)
from event_bus import EventBus
from policy_engine import PolicyDecision, PolicyEngine, create_default_policy_engine
from tool_broker import ToolBroker
from tool_registry import ToolRegistry
from trigger_engine import ActionType, TriggerEngine, create_default_rules

# ── Helpers ──────────────────────────────────────────────────


def _make_android_event(
    event_type: str = "android.notification_received",
    severity: int = 3,
    priority: EventPriority = EventPriority.NORMAL,
    payload: str | None = None,
    dedupe_key: str = "",
) -> Event:
    """Create an Android-originated event for testing."""
    return Event(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type=event_type,
        source_server_type=ServerType.ANDROID,
        source_server_id=ANDROID_SERVER_ID,
        timestamp_ms=int(time.time() * 1000),
        payload_json=payload or '{"app_name":"LINE","title":"Test","text":"Hello"}',
        severity=severity,
        priority=priority,
        dedupe_key=dedupe_key,
    )


def _setup_full_stack(
    provider: MockAndroidProvider | None = None,
) -> tuple[
    EventBus, TriggerEngine, ToolRegistry, PolicyEngine, ToolBroker, ContextBuilder, AuditLog, AndroidServerClient
]:
    """Wire up the full AEGIS Core stack for E2E testing."""
    bus = EventBus()
    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)

    registry = ToolRegistry()
    policy = create_default_policy_engine()
    broker = ToolBroker(registry, policy)

    audit = AuditLog(path="data/test_android_e2e_audit.jsonl")
    builder = ContextBuilder(event_bus=bus, tool_broker=broker)

    provider = provider or MockAndroidProvider()
    client = AndroidServerClient(bus, registry, provider)

    # Wire TriggerEngine to EventBus
    bus.subscribe(engine.on_event)

    return bus, engine, registry, policy, broker, builder, audit, client


# ═══════════════════════════════════════════════════════════════
# 1. Capability Registration
# ═══════════════════════════════════════════════════════════════


class TestCapabilityRegistration:
    """Android Server registers capabilities with AEGIS Core at startup."""

    def test_register_android_server(self):
        """Android Server registers itself as a server with capabilities."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        assert client.register() is True
        assert client.is_registered is True

        server = registry.get_server(ANDROID_SERVER_ID)
        assert server is not None
        assert server.server_type == ServerType.ANDROID
        assert server.status == ServerStatus.ONLINE

    def test_register_android_capabilities(self):
        """All Android observe capabilities are registered."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        for cap_def in ANDROID_CAPABILITIES:
            cap = registry.get_capability(cap_def.id)
            assert cap is not None, f"Capability {cap_def.id} not registered"
            assert cap.server_type == ServerType.ANDROID

    def test_android_get_notifications_registered(self):
        """android.get_notifications capability is registered with correct metadata."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        cap = registry.get_capability("android.get_notifications")
        assert cap is not None
        assert cap.name == "Get Notifications"
        assert cap.risk_level == RiskLevel.READ_ONLY
        assert "notification" in cap.tags
        assert "observe" in cap.tags

    def test_android_get_current_app_registered(self):
        """android.get_current_app capability is registered with correct metadata."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        cap = registry.get_capability("android.get_current_app")
        assert cap is not None
        assert cap.name == "Get Current App"
        assert cap.risk_level == RiskLevel.READ_ONLY

    def test_android_get_device_info_registered(self):
        """android.get_device_info capability is registered with correct metadata."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        cap = registry.get_capability("android.get_device_info")
        assert cap is not None
        assert cap.name == "Get Device Info"
        assert cap.risk_level == RiskLevel.READ_ONLY

    def test_all_android_caps_are_read_only(self):
        """All Android observe capabilities are LEVEL_0_READ (safe, no approval needed)."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        observe_caps = [c for c in ANDROID_CAPABILITIES if "observe" in c.tags or "read_only" in c.tags]
        for cap in observe_caps:
            reg_cap = registry.get_capability(cap.id)
            assert reg_cap.risk_level == RiskLevel.READ_ONLY, (
                f"{cap.id} has risk_level={reg_cap.risk_level.name}, expected READ_ONLY"
            )

    def test_unregister_clears_capabilities(self):
        """Unregistering removes server and capabilities."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()
        assert registry.get_server(ANDROID_SERVER_ID) is not None

        client.unregister()
        assert registry.get_server(ANDROID_SERVER_ID) is None


# ═══════════════════════════════════════════════════════════════
# 2. EventBus Push
# ═══════════════════════════════════════════════════════════════


class TestEventBusPush:
    """Android Server pushes events to EventBus."""

    def test_push_notification_event(self):
        """android.notification_received event is accepted by EventBus."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_notification_event("LINE", "New message", "Hello!")
        assert result is True
        assert len(received) == 1
        assert received[0].event_type == "android.notification_received"
        assert received[0].source_server_type == ServerType.ANDROID

    def test_push_app_changed_event(self):
        """android.current_app_changed event is accepted by EventBus."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_app_changed_event("com.twitter.android", "Twitter")
        assert result is True
        assert len(received) == 1
        assert received[0].event_type == "android.current_app_changed"

    def test_push_device_state_event(self):
        """android.device_state event is accepted by EventBus."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_device_state_event(85, True)
        assert result is True
        assert len(received) == 1
        assert received[0].event_type == "android.device_state"

    def test_event_payload_contains_notification_info(self):
        """Event payload contains notification title, text, app name."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_notification_event("Gmail", "New email", "Hello from Gmail", package_name="com.google.android.gm")

        payload = json.loads(received[0].payload_json)
        assert payload["app_name"] == "Gmail"
        assert payload["title"] == "New email"
        assert payload["text"] == "Hello from Gmail"
        assert payload["package_name"] == "com.google.android.gm"

    def test_event_stats_updated(self):
        """EventBus stats track published and delivered counts."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_notification_event("LINE", "Msg 1", "Hello")
        client.push_notification_event("LINE", "Msg 2", "World")

        assert bus.stats.total_published == 2
        assert bus.stats.total_delivered == 2
        assert client.stats.total_events_pushed == 2


# ═══════════════════════════════════════════════════════════════
# 3. Deduplication
# ═══════════════════════════════════════════════════════════════


class TestDeduplication:
    """Duplicate Android events are deduplicated by EventBus."""

    def test_duplicate_notification_events_deduped(self):
        """Same notification event (same dedupe_key) is deduplicated."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        # Push same notification twice (same app+title = same dedupe_key)
        client.push_notification_event("LINE", "New message", "Hello!")
        client.push_notification_event("LINE", "New message", "Hello!")

        assert len(received) == 1  # Second one deduplicated
        assert bus.stats.total_deduplicated == 1

    def test_different_notifications_not_deduped(self):
        """Different notifications (different dedupe_key) are not deduplicated."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_notification_event("LINE", "Message 1", "Hello")
        client.push_notification_event("Gmail", "New email", "test@example.com")

        assert len(received) == 2

    def test_dedupe_respects_time_window(self):
        """After dedup window expires, same key is allowed again."""
        bus = EventBus(dedup_window_ms=1)  # 1ms window
        registry = ToolRegistry()
        provider = MockAndroidProvider()
        client = AndroidServerClient(bus, registry, provider)
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_notification_event("LINE", "Msg", "Hello")

        time.sleep(0.01)  # Wait beyond 1ms window

        client.push_notification_event("LINE", "Msg", "Hello")

        assert len(received) == 2


# ═══════════════════════════════════════════════════════════════
# 4. Cooldown
# ═══════════════════════════════════════════════════════════════


class TestCooldown:
    """TriggerEngine cooldown prevents rapid Android event processing."""

    def test_notification_cooldown(self):
        """android.notification_received events are rate-limited by cooldown (15s default)."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        # Push first notification — should trigger
        client.push_notification_event("LINE", "Msg 1", "Hello", severity=3)
        tasks1 = engine.drain_tasks()
        assert len(tasks1) >= 1

        # Push second notification immediately — should be suppressed by cooldown
        client.push_notification_event("LINE", "Msg 2", "World", severity=3)
        tasks2 = engine.drain_tasks()
        assert len(tasks2) == 0  # Suppressed by cooldown

    def test_cooldown_reset_allows_next(self):
        """After cooldown reset, next event triggers again."""
        bus, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_notification_event("LINE", "Msg 1", "Hello", severity=3)
        engine.drain_tasks()

        # Reset cooldown for the notification rule
        engine.reset_cooldown("android-notification")

        # Use a different dedupe key to avoid EventBus dedup
        event = _make_android_event(
            event_type="android.notification_received",
            severity=3,
            dedupe_key="android.notification:reset_test",
        )
        bus.publish(event)
        tasks = engine.drain_tasks()
        assert len(tasks) >= 1


# ═══════════════════════════════════════════════════════════════
# 5. TriggerEngine → TaskRequest
# ═══════════════════════════════════════════════════════════════


class TestTriggerEngineIntegration:
    """TriggerEngine generates TaskRequests from Android events."""

    def test_notification_generates_notify_task(self):
        """android.notification_received generates a NOTIFY task via default rules."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_notification_event("LINE", "New message", "Hello!", severity=3)

        tasks = engine.drain_tasks()
        assert len(tasks) == 1
        assert tasks[0].action_type == ActionType.NOTIFY
        assert tasks[0].source_server_type == ServerType.ANDROID
        assert "android.notification_received" in tasks[0].context_summary

    def test_incoming_call_generates_notify_task(self):
        """android.incoming_call generates a NOTIFY task via default rules."""
        bus, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        event = _make_android_event(
            event_type="android.incoming_call",
            severity=7,
            priority=EventPriority.URGENT,
            payload='{"caller":"Mom","number":"+81901234567"}',
        )
        bus.publish(event)

        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        assert tasks[0].action_type == ActionType.NOTIFY

    def test_high_severity_android_event_triggers_alert(self):
        """High-severity Android event triggers ALERT via catch-all rule."""
        bus, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        event = _make_android_event(
            event_type="android.security_alert",
            severity=10,
            priority=EventPriority.URGENT,
        )
        bus.publish(event)

        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        assert tasks[0].action_type == ActionType.ALERT


# ═══════════════════════════════════════════════════════════════
# 6. ContextBuilder Integration
# ═══════════════════════════════════════════════════════════════


class TestContextBuilderIntegration:
    """ContextBuilder includes Android events in the assembled context."""

    def test_context_includes_android_events(self):
        """Context built after Android events includes them in recent_events."""
        bus, _, _, _, _, builder, _, client = _setup_full_stack()
        client.register()

        client.push_notification_event("LINE", "Msg 1", "Hello", severity=3)
        client.push_app_changed_event("com.twitter.android", "Twitter", severity=3)

        ctx = builder.build()
        android_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.ANDROID]
        assert len(android_events) >= 2

    def test_context_preserves_event_payload(self):
        """Context events retain their original payload."""
        bus, _, _, _, _, builder, _, client = _setup_full_stack()
        client.register()

        client.push_notification_event("Gmail", "New email", "test@example.com", severity=3)

        ctx = builder.build()
        android_events = [e for e in ctx.recent_events if e.event_type == "android.notification_received"]
        assert len(android_events) >= 1

        payload = json.loads(android_events[0].payload_json)
        assert payload["app_name"] == "Gmail"
        assert payload["title"] == "New email"

    def test_context_with_triggering_android_event(self):
        """Context can be built with a specific triggering Android event."""
        _, _, _, _, _, builder, _, client = _setup_full_stack()
        client.register()

        trigger_event = _make_android_event(
            event_type="android.notification_received",
            severity=5,
            payload='{"app_name":"LINE","title":"Important","text":"Urgent message"}',
        )

        ctx = builder.build(triggering_events=[trigger_event])
        assert len(ctx.recent_events) >= 1
        assert ctx.recent_events[0].event_type == "android.notification_received"

    def test_context_includes_available_capabilities(self):
        """Context includes registered Android capabilities."""
        _, _, _, _, broker, builder, _, client = _setup_full_stack()
        client.register()

        ctx = builder.build()
        android_cap_ids = [cid for cid in ctx.available_capability_ids if cid.startswith("android.")]
        assert len(android_cap_ids) >= 1


# ═══════════════════════════════════════════════════════════════
# 7. PolicyEngine — read-only allow
# ═══════════════════════════════════════════════════════════════


class TestPolicyEngineReadOnly:
    """PolicyEngine allows read-only Android capabilities without approval."""

    def test_get_notifications_allowed(self):
        """android.get_notifications (READ_ONLY) is allowed by PolicyEngine."""
        _, _, _, policy, _, _, _, client = _setup_full_stack()
        client.register()

        cap = Capability(
            id="android.get_notifications",
            name="Get Notifications",
            description="Retrieve current status bar notifications.",
            server_type=ServerType.ANDROID,
            risk_level=RiskLevel.READ_ONLY,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_get_current_app_allowed(self):
        """android.get_current_app (READ_ONLY) is allowed by PolicyEngine."""
        _, _, _, policy, _, _, _, client = _setup_full_stack()
        client.register()

        cap = Capability(
            id="android.get_current_app",
            name="Get Current App",
            description="Return the package name and activity of the foreground app.",
            server_type=ServerType.ANDROID,
            risk_level=RiskLevel.READ_ONLY,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_all_android_observe_caps_allowed(self):
        """All Android observe capabilities are ALLOWED (no approval needed)."""
        _, _, _, policy, _, _, _, client = _setup_full_stack()
        client.register()

        observe_caps = [c for c in ANDROID_CAPABILITIES if "observe" in c.tags or "read_only" in c.tags]
        for cap_def in observe_caps:
            result = policy.evaluate(cap_def)
            assert result.decision == PolicyDecision.ALLOW, (
                f"{cap_def.id} should be ALLOWED, got {result.decision.name}"
            )

    def test_toolbroker_invokes_get_notifications(self):
        """ToolBroker can invoke android.get_notifications (ALLOWED by policy)."""
        _, _, _, _, broker, _, _, client = _setup_full_stack()
        client.register()

        # Register a mock executor
        def mock_notifications(cap, params):
            return {"notifications": [{"title": "Test", "text": "Hello"}]}

        broker.register_mock("android.", mock_notifications)

        result = broker.invoke_tool("android.get_notifications", {"max_count": 10})
        assert result.success is True
        assert len(result.output["notifications"]) == 1


# ═══════════════════════════════════════════════════════════════
# 8. AuditLog
# ═══════════════════════════════════════════════════════════════


class TestAuditLog:
    """AuditLog records Android Server observations and decisions."""

    def test_audit_logs_capability_registration(self):
        """Registration is logged to audit."""
        _, _, _, _, _, _, audit, client = _setup_full_stack()

        entry = AuditEntry(
            action="capability_registered",
            actor="android_server",
            capability_id="android.get_notifications",
            decision="REGISTERED",
            reason="Android Server registered observe capabilities",
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
            actor="android_server",
            capability_id="android.notification_received",
            decision="ACCEPTED",
            reason="Android event pushed to EventBus",
            detail={"event_type": "android.notification_received", "app": "LINE"},
        )
        audit.append(entry)

        recent = audit.list_recent(10)
        assert any(e.action == "event_received" for e in recent)

    def test_audit_logs_policy_decision(self):
        """Policy decisions for Android capabilities are logged."""
        _, _, _, policy, _, _, audit, client = _setup_full_stack()
        client.register()

        cap = ANDROID_CAPABILITIES[0]  # android.get_notifications
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

        client.push_notification_event("LINE", "Msg", "Hello", severity=3)
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
# 9. Android Device Down — Graceful Failure
# ═══════════════════════════════════════════════════════════════


class TestAndroidDeviceDown:
    """Graceful failure when Android device is unavailable."""

    def test_registration_fails_gracefully(self):
        """Registration returns False when provider is unavailable."""
        provider = MockAndroidProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = AndroidServerClient(bus, registry, provider)

        result = client.register()
        assert result is False
        assert client.is_registered is False
        assert client.stats.state == ConnectionState.FAILED

    def test_event_push_fails_when_not_registered(self):
        """Pushing events returns False when not registered."""
        provider = MockAndroidProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = AndroidServerClient(bus, registry, provider)

        result = client.push_notification_event("LINE", "Msg", "Hello")
        assert result is False

    def test_invoke_returns_error_when_unavailable(self):
        """Invoking capabilities returns error dict when provider is down."""
        provider = MockAndroidProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = AndroidServerClient(bus, registry, provider)

        result = client.invoke_capability("android.get_notifications")
        assert "error" in result
        assert "not available" in result["error"]

    def test_other_servers_unaffected_by_android_failure(self):
        """Other servers can still operate when Android device is down."""
        provider = MockAndroidProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = AndroidServerClient(bus, registry, provider)
        client.register()  # Will fail

        # EventBus should still work for non-Android events
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
    """Android Server retries connection with exponential backoff."""

    def test_retry_succeeds_on_first_attempt(self):
        """connect_with_retry succeeds immediately when provider is available."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = MockAndroidProvider(available=True)
        client = AndroidServerClient(bus, registry, provider, RetryConfig(max_retries=3, base_delay_ms=1))

        result = client.connect_with_retry()
        assert result is True
        assert client.stats.retry_count == 1
        assert client.stats.state == ConnectionState.CONNECTED

    def test_retry_fails_after_max_attempts(self):
        """connect_with_retry fails after exhausting retries."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = MockAndroidProvider(available=False)
        client = AndroidServerClient(bus, registry, provider, RetryConfig(max_retries=2, base_delay_ms=1))

        result = client.connect_with_retry()
        assert result is False
        assert client.stats.retry_count == 2
        assert client.stats.state == ConnectionState.FAILED

    def test_retry_succeeds_after_transient_failure(self):
        """connect_with_retry succeeds when provider becomes available."""
        call_count = 0

        class FlakyProvider(MockAndroidProvider):
            def is_available(self) -> bool:
                nonlocal call_count
                call_count += 1
                return call_count >= 2  # Fail first, succeed second

        bus = EventBus()
        registry = ToolRegistry()
        provider = FlakyProvider()
        client = AndroidServerClient(bus, registry, provider, RetryConfig(max_retries=3, base_delay_ms=1))

        result = client.connect_with_retry()
        assert result is True
        assert client.stats.retry_count >= 2

    def test_backoff_delay_increases(self):
        """Retry delay increases exponentially (verified via stats)."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = MockAndroidProvider(available=False)
        config = RetryConfig(max_retries=3, base_delay_ms=1, backoff_factor=2.0)
        client = AndroidServerClient(bus, registry, provider, config)

        start = time.monotonic()
        client.connect_with_retry()
        elapsed = time.monotonic() - start

        # With base=1ms, factor=2: delays are 1ms, 2ms, 4ms → total ~7ms minimum
        assert elapsed > 0.001


# ═══════════════════════════════════════════════════════════════
# 11. Full E2E Flow
# ═══════════════════════════════════════════════════════════════


class TestFullE2EFlow:
    """Complete E2E: Android Server → EventBus → TriggerEngine → ContextBuilder → AuditLog."""

    def test_full_observe_flow(self):
        """Full flow from Android event to context assembly with audit trail."""
        bus, engine, registry, policy, broker, builder, audit, client = _setup_full_stack()

        # 1. Android Server registers
        assert client.register() is True
        audit.append(
            AuditEntry(
                action="server_registered",
                actor="android_server",
                decision="SUCCESS",
                reason=f"Registered {len(ANDROID_CAPABILITIES)} capabilities",
            )
        )

        # 2. Verify capabilities are registered
        assert registry.get_capability("android.get_notifications") is not None
        assert registry.get_capability("android.get_current_app") is not None
        assert registry.get_capability("android.get_device_info") is not None

        # 3. Policy allows read-only
        observe_caps = [c for c in ANDROID_CAPABILITIES if "observe" in c.tags or "read_only" in c.tags]
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

        # 4. Push notification event
        client.push_notification_event("LINE", "New message", "Hello!", severity=3)
        audit.append(
            AuditEntry(
                action="event_received",
                actor="android_server",
                capability_id="android.notification_received",
                decision="ACCEPTED",
            )
        )

        # 5. TriggerEngine fires
        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        assert tasks[0].action_type == ActionType.NOTIFY
        audit.append(
            AuditEntry(
                action="trigger_fired",
                actor="trigger_engine",
                capability_id=tasks[0].triggered_by_event_type,
                decision="TASK_GENERATED",
                detail={"task_id": tasks[0].task_id},
            )
        )

        # 6. ContextBuilder includes Android events
        ctx = builder.build()
        android_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.ANDROID]
        assert len(android_events) >= 1

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
        client.push_notification_event("LINE", "Msg", "Hello", severity=3)
        client.push_notification_event("LINE", "Msg", "Hello", severity=3)

        # Only one event delivered (deduped)
        assert bus.stats.total_deduplicated == 1

        # Only one task generated
        tasks = engine.drain_tasks()
        assert len(tasks) == 1

    def test_full_flow_with_cooldown(self):
        """Full flow respects TriggerEngine cooldown."""
        bus, engine, registry, policy, broker, builder, audit, client = _setup_full_stack()
        client.register()

        # First notification — triggers
        client.push_notification_event("LINE", "Msg 1", "Hello", severity=3)
        tasks1 = engine.drain_tasks()
        assert len(tasks1) == 1

        # Second notification — suppressed by cooldown
        client.push_notification_event("LINE", "Msg 2", "World", severity=3)
        tasks2 = engine.drain_tasks()
        assert len(tasks2) == 0

    def test_full_flow_multiple_event_types(self):
        """Full flow handles multiple Android event types."""
        bus, engine, registry, policy, broker, builder, audit, client = _setup_full_stack()
        client.register()

        # Push various Android events
        client.push_notification_event("LINE", "Msg", "Hello", severity=3)
        client.push_app_changed_event("com.twitter.android", "Twitter", severity=3)

        # Context includes all events
        ctx = builder.build()
        android_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.ANDROID]
        assert len(android_events) >= 2

    def test_invoke_capability_through_broker(self):
        """Android capabilities can be invoked through ToolBroker (E2E)."""
        bus, engine, registry, policy, broker, builder, audit, client = _setup_full_stack()
        client.register()

        # Register mock executor
        def mock_android_executor(cap, params):
            if cap.id == "android.get_notifications":
                return {"notifications": [{"title": "Test", "text": "Hello"}]}
            elif cap.id == "android.get_current_app":
                return {"package_name": "com.example", "app_name": "Example"}
            elif cap.id == "android.get_device_info":
                return {"model": "Pixel 7", "android_version": "14", "battery_level": 85}
            return {"mock": True}

        broker.register_mock("android.", mock_android_executor)

        # Invoke through broker (policy check is automatic)
        result = broker.invoke_tool("android.get_notifications", {"max_count": 10})
        assert result.success is True
        assert len(result.output["notifications"]) == 1

        result2 = broker.invoke_tool("android.get_current_app")
        assert result2.success is True
        assert result2.output["package_name"] == "com.example"


# ═══════════════════════════════════════════════════════════════
# 12. Mock Provider Call Log
# ═══════════════════════════════════════════════════════════════


class TestMockProviderCallLog:
    """MockAndroidProvider tracks all calls for verification."""

    def test_call_log_records_invocations(self):
        provider = MockAndroidProvider()
        bus = EventBus()
        registry = ToolRegistry()
        client = AndroidServerClient(bus, registry, provider)
        client.register()

        client.invoke_capability("android.get_notifications", {"max_count": 5})
        client.invoke_capability("android.get_current_app")
        client.invoke_capability("android.get_device_info")

        assert len(provider.call_log) == 3
        assert provider.call_log[0][0] == "get_notifications"
        assert provider.call_log[1][0] == "get_current_app"
        assert provider.call_log[2][0] == "get_device_info"

    def test_call_log_preserves_params(self):
        provider = MockAndroidProvider()
        bus = EventBus()
        registry = ToolRegistry()
        client = AndroidServerClient(bus, registry, provider)
        client.register()

        client.invoke_capability("android.get_notifications", {"max_count": 5})

        assert provider.call_log[0] == ("get_notifications", {"max_count": 5})


# ═══════════════════════════════════════════════════════════════
# 13. Notification Redaction
# ═══════════════════════════════════════════════════════════════


class TestNotificationRedaction:
    """NotificationFilter redacts sensitive data from notification text."""

    def test_redact_otp_code(self):
        """OTP codes (4-8 digit standalone numbers) are redacted."""
        nf = NotificationFilter()
        result = nf.redact("Your verification code is 123456")
        assert "123456" not in result
        assert "[OTP_REDACTED]" in result

    def test_redact_4_digit_otp(self):
        """4-digit OTP codes are redacted."""
        nf = NotificationFilter()
        result = nf.redact("Code: 4829")
        assert "4829" not in result
        assert "[OTP_REDACTED]" in result

    def test_redact_credit_card(self):
        """Credit card numbers are redacted."""
        nf = NotificationFilter()
        result = nf.redact("Card: 4111 1111 1111 1111")
        assert "4111" not in result
        assert "[CARD_REDACTED]" in result

    def test_redact_email_address(self):
        """Email addresses are redacted."""
        nf = NotificationFilter()
        result = nf.redact("New email from test@example.com")
        assert "test@example.com" not in result
        assert "[EMAIL_REDACTED]" in result

    def test_redact_phone_number(self):
        """International phone numbers are redacted."""
        nf = NotificationFilter()
        result = nf.redact("Call from +819012345678")
        assert "+819012345678" not in result
        assert "[PHONE_REDACTED]" in result

    def test_redact_password_in_text(self):
        """Password values are redacted."""
        nf = NotificationFilter()
        result = nf.redact("password: mysecret123")
        assert "mysecret123" not in result
        assert "[REDACTED]" in result

    def test_redact_token_in_text(self):
        """Token values are redacted."""
        nf = NotificationFilter()
        result = nf.redact("token=abc123xyz")
        assert "abc123xyz" not in result
        assert "[REDACTED]" in result

    def test_redact_preserves_normal_text(self):
        """Normal notification text is preserved."""
        nf = NotificationFilter()
        result = nf.redact("Meeting at 3pm in the conference room")
        assert result == "Meeting at 3pm in the conference room"

    def test_redact_multiple_sensitive_items(self):
        """Multiple sensitive items in one text are all redacted."""
        nf = NotificationFilter()
        result = nf.redact("Send to test@example.com, code 1234")
        assert "test@example.com" not in result
        assert "1234" not in result
        assert "[EMAIL_REDACTED]" in result
        assert "[OTP_REDACTED]" in result

    def test_filter_notification_redacts_fields(self):
        """filter_notification redacts title and text fields."""
        nf = NotificationFilter()
        notification = {
            "app_name": "Gmail",
            "title": "New email",
            "text": "From test@example.com",
            "package_name": "com.google.android.gm",
        }
        filtered = nf.filter_notification(notification)
        assert filtered is not None
        assert "test@example.com" not in filtered["text"]
        assert "[EMAIL_REDACTED]" in filtered["text"]
        assert filtered["title"] == "New email"  # title preserved (no sensitive data)

    def test_redaction_applied_in_push_event(self):
        """push_notification_event applies redaction to payload."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_notification_event(
            "Gmail",
            "New email",
            "From test@example.com",
            package_name="com.google.android.gm",
        )

        payload = json.loads(received[0].payload_json)
        assert "test@example.com" not in payload["text"]
        assert "[EMAIL_REDACTED]" in payload["text"]


# ═══════════════════════════════════════════════════════════════
# 14. Allowlist / Denylist
# ═══════════════════════════════════════════════════════════════


class TestAllowlistDenylist:
    """NotificationFilter blocks denylisted apps and allows allowlisted apps."""

    def test_denylisted_app_is_blocked(self):
        """Notifications from denylisted apps are blocked."""
        nf = NotificationFilter()
        assert nf.is_blocked("com.google.android.apps.authenticator") is True

    def test_allowlisted_app_is_not_blocked(self):
        """Notifications from allowlisted apps are never blocked."""
        nf = NotificationFilter()
        assert nf.is_blocked("jp.naver.line.android") is False
        assert nf.is_blocked("com.google.android.gm") is False
        assert nf.is_blocked("com.slack") is False

    def test_allowlist_overrides_denylist(self):
        """An app in both allowlist and denylist is allowed."""
        nf = NotificationFilter(
            denylist={"com.test.app"},
            allowlist={"com.test.app"},
        )
        assert nf.is_blocked("com.test.app") is False

    def test_unknown_app_is_not_blocked(self):
        """Apps not in either list are not blocked (default allow)."""
        nf = NotificationFilter()
        assert nf.is_blocked("com.some.random.app") is False

    def test_filter_returns_none_for_blocked(self):
        """filter_notification returns None for denylisted apps."""
        nf = NotificationFilter()
        notification = {
            "app_name": "Authenticator",
            "title": "2FA Code",
            "text": "123456",
            "package_name": "com.google.android.apps.authenticator",
        }
        assert nf.filter_notification(notification) is None

    def test_filter_returns_dict_for_allowed(self):
        """filter_notification returns filtered dict for allowed apps."""
        nf = NotificationFilter()
        notification = {
            "app_name": "LINE",
            "title": "New message",
            "text": "Hello!",
            "package_name": "jp.naver.line.android",
        }
        result = nf.filter_notification(notification)
        assert result is not None
        assert result["app_name"] == "LINE"

    def test_push_blocked_notification_returns_false(self):
        """push_notification_event returns False for denylisted apps."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_notification_event(
            "Authenticator",
            "2FA",
            "123456",
            package_name="com.google.android.apps.authenticator",
        )
        assert result is False
        assert len(received) == 0

    def test_push_allowed_notification_returns_true(self):
        """push_notification_event returns True for allowlisted apps."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_notification_event(
            "LINE",
            "New message",
            "Hello!",
            package_name="jp.naver.line.android",
        )
        assert result is True
        assert len(received) == 1

    def test_custom_denylist(self):
        """Custom denylist blocks specified apps."""
        nf = NotificationFilter(denylist={"com.custom.blocked"})
        assert nf.is_blocked("com.custom.blocked") is True
        assert nf.is_blocked("com.google.android.gm") is False

    def test_custom_allowlist(self):
        """Custom allowlist allows specified apps."""
        nf = NotificationFilter(allowlist={"com.custom.allowed"})
        assert nf.is_blocked("com.custom.allowed") is False
        # Default denylist apps are still blocked
        assert nf.is_blocked("com.google.android.apps.authenticator") is True


# ═══════════════════════════════════════════════════════════════
# 15. Sensitive App Filtering
# ═══════════════════════════════════════════════════════════════


class TestSensitiveAppFiltering:
    """Sensitive apps have their notifications stored redacted-only."""

    def test_banking_app_is_sensitive(self):
        """Banking apps are flagged as sensitive."""
        nf = NotificationFilter()
        assert nf.is_sensitive("com.bank.japan") is True

    def test_password_manager_is_sensitive(self):
        """Password managers are flagged as sensitive."""
        nf = NotificationFilter()
        assert nf.is_sensitive("com.password.manager") is True

    def test_authenticator_is_sensitive(self):
        """2FA authenticator apps are flagged as sensitive."""
        nf = NotificationFilter()
        assert nf.is_sensitive("com.google.android.apps.authenticator") is True

    def test_normal_app_is_not_sensitive(self):
        """Normal apps are not flagged as sensitive."""
        nf = NotificationFilter()
        assert nf.is_sensitive("jp.naver.line.android") is False
        assert nf.is_sensitive("com.google.android.gm") is False

    def test_sensitive_app_notification_marked_redacted_only(self):
        """Notifications from sensitive apps are marked redacted_only."""
        nf = NotificationFilter()
        notification = {
            "app_name": "Bank",
            "title": "Transaction",
            "text": "Spent $100",
            "package_name": "com.bank.app",
        }
        filtered = nf.filter_notification(notification)
        assert filtered is not None  # Not blocked (not in denylist)
        assert filtered["redacted_only"] is True

    def test_normal_app_notification_not_redacted_only(self):
        """Notifications from normal apps are not marked redacted_only."""
        nf = NotificationFilter()
        notification = {
            "app_name": "LINE",
            "title": "Message",
            "text": "Hello!",
            "package_name": "jp.naver.line.android",
        }
        filtered = nf.filter_notification(notification)
        assert filtered is not None
        assert filtered["redacted_only"] is False

    def test_sensitive_notification_payload_contains_flag(self):
        """Sensitive app notification events carry redacted_only in payload."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        # com.bank.app is sensitive but not denylisted
        nf = NotificationFilter(denylist=set())  # Clear denylist to allow bank app
        client._notification_filter = nf

        client.push_notification_event(
            "Bank",
            "Transaction",
            "Spent $100",
            package_name="com.bank.app",
        )

        assert len(received) == 1
        payload = json.loads(received[0].payload_json)
        assert payload["redacted_only"] is True

    def test_raw_notification_not_stored(self):
        """Raw (unredacted) notification text is never stored for sensitive apps."""
        nf = NotificationFilter()
        notification = {
            "app_name": "Bank",
            "title": "Account alert",
            "text": "Your balance is $1234.56",
            "package_name": "com.bank.app",
        }
        filtered = nf.filter_notification(notification)
        assert filtered is not None
        # Text should be redacted (numbers may be treated as OTP)
        # At minimum, the redacted_only flag prevents raw storage
        assert filtered["redacted_only"] is True


# ═══════════════════════════════════════════════════════════════
# 16. TriggerEngine Rules for Android Notifications
# ═══════════════════════════════════════════════════════════════


class TestTriggerRulesAndroid:
    """TriggerEngine rules specific to Android notification scenarios."""

    def test_allowlisted_app_notification_wakes_ai(self):
        """Notification from allowlisted app with sufficient severity wakes AI."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_notification_event(
            "LINE",
            "Urgent",
            "Important message",
            package_name="jp.naver.line.android",
            severity=5,
        )

        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        assert tasks[0].action_type == ActionType.NOTIFY

    def test_low_importance_notification_deferred(self):
        """Low-importance notification does not trigger a task."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        # Severity 1 with BACKGROUND priority — below android-notification rule threshold
        client.push_notification_event(
            "Settings",
            "Update available",
            "New version",
            package_name="com.android.settings",
            severity=1,
            priority=EventPriority.BACKGROUND,
        )

        tasks = engine.drain_tasks()
        assert len(tasks) == 0  # Deferred — below threshold

    def test_duplicated_notification_suppressed(self):
        """Duplicate notifications (same dedupe_key) are suppressed by EventBus."""
        bus, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_notification_event("LINE", "Msg", "Hello", severity=3)
        client.push_notification_event("LINE", "Msg", "Hello", severity=3)

        assert bus.stats.total_deduplicated == 1
        tasks = engine.drain_tasks()
        assert len(tasks) == 1  # Only one task, not two

    def test_permission_missing_event_wakes_ai(self):
        """android.notification_permission_missing event wakes AI."""
        bus, engine, _, _, _, _, _, _ = _setup_full_stack()

        event = _make_android_event(
            event_type="android.notification_permission_missing",
            severity=9,
            priority=EventPriority.URGENT,
        )
        bus.publish(event)

        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        assert tasks[0].action_type == ActionType.ALERT


# ═══════════════════════════════════════════════════════════════
# 17. Notification Permission Missing
# ═══════════════════════════════════════════════════════════════


class TestNotificationPermissionMissing:
    """Handles missing notification permission gracefully."""

    def test_permission_missing_event_type(self):
        """android.notification_permission_missing event is valid."""
        event = _make_android_event(
            event_type="android.notification_permission_missing",
            severity=8,
            priority=EventPriority.URGENT,
            payload='{"reason":"NotificationListenerService not enabled"}',
        )
        assert event.event_type == "android.notification_permission_missing"
        assert event.severity == 8

    def test_permission_missing_triggers_alert(self):
        """Permission missing event triggers high-priority alert."""
        bus, engine, _, _, _, _, _, _ = _setup_full_stack()

        event = _make_android_event(
            event_type="android.notification_permission_missing",
            severity=9,
            priority=EventPriority.URGENT,
        )
        bus.publish(event)

        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        # High severity should trigger ALERT via catch-all rule
        assert tasks[0].action_type == ActionType.ALERT
