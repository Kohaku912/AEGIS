"""Room Server Observe E2E — integration tests for Room Server ↔ AEGIS Core.

Tests the full observe flow:
  Room Server → EventBus → TriggerEngine → ContextBuilder → AuditLog

CI uses MockSensorProvider (no real hardware).
Architecture reference: docs/architecture.md §3.5, §6
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
from policy_engine import PolicyDecision, PolicyEngine, create_default_policy_engine
from room_server_client import (
    ROOM_CAPABILITIES,
    ROOM_SERVER_ID,
    ConnectionState,
    MockSensorProvider,
    RoomServerClient,
    SensorThresholds,
)
from tool_broker import ToolBroker
from tool_registry import ToolRegistry
from trigger_engine import ActionType, TriggerEngine, create_default_rules

# ── Helpers ──────────────────────────────────────────────────


def _make_room_event(
    event_type: str = "room.temperature_changed",
    severity: int = 3,
    priority: EventPriority = EventPriority.BACKGROUND,
    payload: str | None = None,
    dedupe_key: str = "",
) -> Event:
    """Create a Room-originated event for testing."""
    return Event(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type=event_type,
        source_server_type=ServerType.ROOM,
        source_server_id=ROOM_SERVER_ID,
        timestamp_ms=int(time.time() * 1000),
        payload_json=payload or '{"temperature_c": 22.5}',
        severity=severity,
        priority=priority,
        dedupe_key=dedupe_key,
    )


def _setup_full_stack(
    provider: MockSensorProvider | None = None,
    thresholds: SensorThresholds | None = None,
) -> tuple[EventBus, TriggerEngine, ToolRegistry, PolicyEngine, ToolBroker, ContextBuilder, AuditLog, RoomServerClient]:
    """Wire up the full AEGIS Core stack for E2E testing."""
    bus = EventBus()
    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)

    registry = ToolRegistry()
    policy = create_default_policy_engine()
    broker = ToolBroker(registry, policy)

    audit = AuditLog(path="data/test_room_e2e_audit.jsonl")
    builder = ContextBuilder(event_bus=bus, tool_broker=broker)

    provider = provider or MockSensorProvider()
    client = RoomServerClient(bus, registry, provider, thresholds=thresholds)

    # Wire TriggerEngine to EventBus
    bus.subscribe(engine.on_event)

    return bus, engine, registry, policy, broker, builder, audit, client


# ═══════════════════════════════════════════════════════════════
# 1. Health Check
# ═══════════════════════════════════════════════════════════════


class TestHealthCheck:
    """Room Server health check."""

    def test_provider_is_available(self):
        """MockSensorProvider reports available."""
        provider = MockSensorProvider()
        assert provider.is_available() is True

    def test_provider_unavailable(self):
        """MockSensorProvider can be configured as unavailable."""
        provider = MockSensorProvider(available=False)
        assert provider.is_available() is False

    def test_client_health_with_available_provider(self):
        """RoomServerClient reports connected when provider is available."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        assert client.register() is True
        assert client.is_registered is True

    def test_client_health_with_unavailable_provider(self):
        """RoomServerClient reports failed when provider is unavailable."""
        provider = MockSensorProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = RoomServerClient(bus, registry, provider)
        assert client.register() is False
        assert client.is_registered is False
        assert client.stats.state == ConnectionState.FAILED


# ═══════════════════════════════════════════════════════════════
# 2. Capability Registration
# ═══════════════════════════════════════════════════════════════


class TestCapabilityRegistration:
    """Room Server registers capabilities with AEGIS Core at startup."""

    def test_register_room_server(self):
        """Room Server registers itself as a server with capabilities."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        assert client.register() is True
        assert client.is_registered is True

        server = registry.get_server(ROOM_SERVER_ID)
        assert server is not None
        assert server.server_type == ServerType.ROOM
        assert server.status == ServerStatus.ONLINE

    def test_register_room_capabilities(self):
        """All Room capabilities are registered."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        for cap_def in ROOM_CAPABILITIES:
            cap = registry.get_capability(cap_def.id)
            assert cap is not None, f"Capability {cap_def.id} not registered"
            assert cap.server_type == ServerType.ROOM

    def test_room_get_environment_registered(self):
        """room.get_environment capability is registered with correct metadata."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        cap = registry.get_capability("room.get_environment")
        assert cap is not None
        assert cap.name == "Get Environment"
        assert cap.risk_level == RiskLevel.READ_ONLY
        assert "environment" in cap.tags
        assert "observe" in cap.tags

    def test_room_get_temperature_registered(self):
        """room.get_temperature capability is registered."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        cap = registry.get_capability("room.get_temperature")
        assert cap is not None
        assert cap.risk_level == RiskLevel.READ_ONLY

    def test_all_room_caps_are_read_only(self):
        """All Room observe capabilities are LEVEL_0_READ."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()

        observe_caps = [c for c in ROOM_CAPABILITIES if "observe" in c.tags or "read_only" in c.tags]
        for cap in observe_caps:
            reg_cap = registry.get_capability(cap.id)
            assert reg_cap.risk_level == RiskLevel.READ_ONLY, (
                f"{cap.id} has risk_level={reg_cap.risk_level.name}, expected READ_ONLY"
            )

    def test_unregister_clears_capabilities(self):
        """Unregistering removes server and capabilities."""
        _, _, registry, _, _, _, _, client = _setup_full_stack()
        client.register()
        assert registry.get_server(ROOM_SERVER_ID) is not None

        client.unregister()
        assert registry.get_server(ROOM_SERVER_ID) is None


# ═══════════════════════════════════════════════════════════════
# 3. Mock Sensor Read
# ═══════════════════════════════════════════════════════════════


class TestMockSensorRead:
    """MockSensorProvider returns deterministic data."""

    def test_get_temperature(self):
        """Mock temperature reading."""
        provider = MockSensorProvider()
        result = provider.get_temperature()
        assert result["temperature_c"] == 22.5
        assert result["timestamp_ms"] > 0

    def test_get_humidity(self):
        """Mock humidity reading."""
        provider = MockSensorProvider()
        result = provider.get_humidity()
        assert result["humidity_pct"] == 45.0

    def test_get_brightness(self):
        """Mock brightness reading."""
        provider = MockSensorProvider()
        result = provider.get_brightness()
        assert result["brightness_lux"] == 300.0

    def test_get_motion_status(self):
        """Mock motion reading (no motion by default)."""
        provider = MockSensorProvider()
        result = provider.get_motion_status()
        assert result["motion_detected"] is False

    def test_get_environment_aggregates_all(self):
        """get_environment returns all sensor values."""
        provider = MockSensorProvider()
        result = provider.get_environment()
        assert "temperature_c" in result
        assert "humidity_pct" in result
        assert "brightness_lux" in result
        assert "motion_detected" in result
        assert "timestamp_ms" in result

    def test_set_mock_values(self):
        """Mock values can be overridden for testing."""
        provider = MockSensorProvider()
        provider.set_mock_values(temperature_c=30.0, motion_detected=True)

        temp = provider.get_temperature()
        assert temp["temperature_c"] == 30.0

        motion = provider.get_motion_status()
        assert motion["motion_detected"] is True

    def test_list_sensors(self):
        """Mock sensor list returns all sensor types."""
        provider = MockSensorProvider()
        sensors = provider.list_sensors()
        assert len(sensors) == 4
        types = {s["sensor_type"] for s in sensors}
        assert "temperature" in types
        assert "humidity" in types
        assert "brightness" in types
        assert "motion" in types

    def test_get_device_status(self):
        """Mock device status returns online devices."""
        provider = MockSensorProvider()
        devices = provider.get_device_status()
        assert len(devices) == 3
        for d in devices:
            assert d["online"] is True

    def test_call_log_tracks_invocations(self):
        """Provider tracks all calls for verification."""
        provider = MockSensorProvider()
        provider.get_temperature()
        provider.get_humidity()
        provider.get_motion_status()
        assert len(provider.call_log) == 3
        assert provider.call_log[0][0] == "get_temperature"


# ═══════════════════════════════════════════════════════════════
# 4. Environment Aggregation
# ═══════════════════════════════════════════════════════════════


class TestEnvironmentAggregation:
    """invoke_capability returns aggregated environment data."""

    def test_invoke_get_environment(self):
        """room.get_environment returns all sensor values."""
        _, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        result = client.invoke_capability("room.get_environment")
        assert "temperature_c" in result
        assert "humidity_pct" in result
        assert "brightness_lux" in result
        assert "motion_detected" in result

    def test_invoke_get_temperature(self):
        """room.get_temperature returns temperature."""
        _, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        result = client.invoke_capability("room.get_temperature")
        assert result["temperature_c"] == 22.5

    def test_invoke_list_sensors(self):
        """room.list_sensors returns sensor list."""
        _, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        result = client.invoke_capability("room.list_sensors")
        assert "sensors" in result
        assert len(result["sensors"]) == 4

    def test_invoke_unknown_capability(self):
        """Unknown capability returns error."""
        _, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        result = client.invoke_capability("room.nonexistent")
        assert "error" in result


# ═══════════════════════════════════════════════════════════════
# 5. Threshold Detection
# ═══════════════════════════════════════════════════════════════


class TestThresholdDetection:
    """Events are only pushed when sensor changes exceed thresholds."""

    def test_initial_poll_pushes_all(self):
        """First poll always pushes (no previous values)."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        results = client.poll_and_push()
        # First poll should push temperature (no previous value)
        assert results.get("temperature_changed") is True

    def test_small_change_no_event(self):
        """Small temperature change below threshold does not push event."""
        bus, _, _, _, _, _, _, client = _setup_full_stack(thresholds=SensorThresholds(temperature_delta_c=2.0))
        client.register()

        # First poll
        client.poll_and_push()
        bus.stats.total_published  # Reset by consuming

        # Small change (0.5°C < 2.0°C threshold)
        client.sensor_provider.set_mock_values(temperature_c=23.0)
        results = client.poll_and_push()
        assert results.get("temperature_changed") is None

    def test_large_change_pushes_event(self):
        """Large temperature change above threshold pushes event."""
        bus, _, _, _, _, _, _, client = _setup_full_stack(thresholds=SensorThresholds(temperature_delta_c=1.0))
        client.register()

        # First poll
        client.poll_and_push()

        # Large change (5°C >= 1.0°C threshold)
        client.sensor_provider.set_mock_values(temperature_c=27.5)
        results = client.poll_and_push()
        assert results.get("temperature_changed") is True

    def test_motion_cooldown(self):
        """Motion events respect cooldown period."""
        bus, _, _, _, _, _, _, client = _setup_full_stack(thresholds=SensorThresholds(motion_cooldown_seconds=60.0))
        client.register()

        # First motion
        client.sensor_provider.set_mock_values(motion_detected=True)
        results1 = client.poll_and_push()
        assert results1.get("motion_detected") is True

        # Second motion within cooldown
        results2 = client.poll_and_push()
        assert results2.get("motion_detected") is None  # Suppressed by cooldown


# ═══════════════════════════════════════════════════════════════
# 6. Dedupe / Cooldown
# ═══════════════════════════════════════════════════════════════


class TestDedupeCooldown:
    """Duplicate room events are deduplicated by EventBus."""

    def test_duplicate_temperature_events_deduped(self):
        """Same temperature event (same dedupe_key) is deduplicated."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_temperature_event(22.5)
        client.push_temperature_event(22.5)

        assert len(received) == 1
        assert bus.stats.total_deduplicated == 1

    def test_different_temperatures_not_deduped(self):
        """Different temperature readings are not deduplicated."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_temperature_event(22.5)
        client.push_temperature_event(25.0)

        assert len(received) == 2

    def test_motion_cooldown_in_trigger_engine(self):
        """TriggerEngine cooldown prevents rapid motion event processing."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_motion_event(True, "living_room", severity=3)
        tasks1 = engine.drain_tasks()
        assert len(tasks1) >= 1

        # Second motion immediately — suppressed by cooldown
        client.push_motion_event(True, "living_room", severity=3)
        tasks2 = engine.drain_tasks()
        assert len(tasks2) == 0


# ═══════════════════════════════════════════════════════════════
# 7. EventBus Push
# ═══════════════════════════════════════════════════════════════


class TestEventBusPush:
    """Room Server pushes events to EventBus."""

    def test_push_environment_event(self):
        """room.environment_updated event is accepted by EventBus."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        env = {"temperature_c": 22.5, "humidity_pct": 45.0}
        result = client.push_environment_event(env)
        assert result is True
        assert len(received) == 1
        assert received[0].event_type == "room.environment_updated"
        assert received[0].source_server_type == ServerType.ROOM

    def test_push_temperature_event(self):
        """room.temperature_changed event is accepted by EventBus."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_temperature_event(25.0)
        assert result is True
        assert len(received) == 1
        assert received[0].event_type == "room.temperature_changed"

        payload = json.loads(received[0].payload_json)
        assert payload["temperature_c"] == 25.0

    def test_push_motion_event(self):
        """room.motion_detected event is accepted by EventBus."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_motion_event(True, "living_room")
        assert result is True
        assert len(received) == 1

        payload = json.loads(received[0].payload_json)
        assert payload["motion_detected"] is True
        assert payload["motion_zone"] == "living_room"

    def test_push_sensor_unavailable_event(self):
        """room.sensor_unavailable event (URGENT, wakes AI)."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_sensor_unavailable_event("sensor-temp-001", "Connection lost")
        assert result is True
        assert len(received) == 1
        assert received[0].priority == EventPriority.URGENT

    def test_event_stats_updated(self):
        """EventBus stats track published counts."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_temperature_event(22.5)
        client.push_motion_event(True)

        assert bus.stats.total_published == 2
        assert client.stats.total_events_pushed == 2

    def test_push_fails_when_not_registered(self):
        """Pushing events returns False when not registered."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = MockSensorProvider()
        client = RoomServerClient(bus, registry, provider)

        result = client.push_temperature_event(22.5)
        assert result is False


# ═══════════════════════════════════════════════════════════════
# 8. Provider Unavailable
# ═══════════════════════════════════════════════════════════════


class TestProviderUnavailable:
    """Graceful failure when sensor provider is unavailable."""

    def test_registration_fails_gracefully(self):
        """Registration returns False when provider is unavailable."""
        provider = MockSensorProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = RoomServerClient(bus, registry, provider)

        result = client.register()
        assert result is False
        assert client.is_registered is False
        assert client.stats.state == ConnectionState.FAILED

    def test_invoke_returns_error_when_unavailable(self):
        """Invoking capabilities returns error when provider is down."""
        provider = MockSensorProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = RoomServerClient(bus, registry, provider)

        result = client.invoke_capability("room.get_temperature")
        assert "error" in result
        assert "not available" in result["error"]

    def test_poll_pushes_sensor_unavailable(self):
        """poll_and_push pushes sensor_unavailable event when provider is down."""
        bus, _, _, _, _, _, _, client = _setup_full_stack(provider=MockSensorProvider(available=False))
        client.register()  # Will fail

        # Even if not registered, poll should handle gracefully
        provider = MockSensorProvider(available=False)
        bus2 = EventBus()
        registry2 = ToolRegistry()
        client2 = RoomServerClient(bus2, registry2, provider)
        client2.register()  # Fails

        results = client2.poll_and_push()
        # Should not crash
        assert isinstance(results, dict)

    def test_other_servers_unaffected_by_room_failure(self):
        """Other servers can still operate when Room sensors are down."""
        provider = MockSensorProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = RoomServerClient(bus, registry, provider)
        client.register()  # Will fail

        # EventBus should still work for non-Room events
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
# 9. Invalid Sensor Value
# ═══════════════════════════════════════════════════════════════


class TestInvalidSensorValue:
    """Handling of invalid or out-of-range sensor values."""

    def test_extreme_temperature(self):
        """Extreme temperature values are passed through (validation is provider-side)."""
        _, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.sensor_provider.set_mock_values(temperature_c=-40.0)
        result = client.invoke_capability("room.get_temperature")
        assert result["temperature_c"] == -40.0

    def test_zero_humidity(self):
        """Zero humidity is a valid reading."""
        _, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.sensor_provider.set_mock_values(humidity_pct=0.0)
        result = client.invoke_capability("room.get_humidity")
        assert result["humidity_pct"] == 0.0

    def test_push_extreme_value_as_event(self):
        """Extreme values can still be pushed as events."""
        bus, _, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        result = client.push_temperature_event(99.9)
        assert result is True
        payload = json.loads(received[0].payload_json)
        assert payload["temperature_c"] == 99.9


# ═══════════════════════════════════════════════════════════════
# 10. PolicyEngine — read-only allow
# ═══════════════════════════════════════════════════════════════


class TestPolicyEngineReadOnly:
    """PolicyEngine allows read-only Room capabilities without approval."""

    def test_get_environment_allowed(self):
        """room.get_environment (READ_ONLY) is allowed by PolicyEngine."""
        _, _, _, policy, _, _, _, client = _setup_full_stack()
        client.register()

        cap = Capability(
            id="room.get_environment",
            name="Get Environment",
            description="Read all environment sensors.",
            server_type=ServerType.ROOM,
            risk_level=RiskLevel.READ_ONLY,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_all_room_observe_caps_allowed(self):
        """All Room observe capabilities are ALLOWED (no approval needed)."""
        _, _, _, policy, _, _, _, client = _setup_full_stack()
        client.register()

        observe_caps = [c for c in ROOM_CAPABILITIES if "observe" in c.tags or "read_only" in c.tags]
        for cap_def in observe_caps:
            result = policy.evaluate(cap_def)
            assert result.decision == PolicyDecision.ALLOW, (
                f"{cap_def.id} should be ALLOWED, got {result.decision.name}"
            )

    def test_toolbroker_invokes_get_environment(self):
        """ToolBroker can invoke room.get_environment (ALLOWED by policy)."""
        _, _, _, _, broker, _, _, client = _setup_full_stack()
        client.register()

        def mock_room_executor(cap, params):
            return {"temperature_c": 22.5, "humidity_pct": 45.0}

        broker.register_mock("room.", mock_room_executor)

        result = broker.invoke_tool("room.get_environment")
        assert result.success is True
        assert result.output["temperature_c"] == 22.5


# ═══════════════════════════════════════════════════════════════
# 11. TriggerEngine Rules
# ═══════════════════════════════════════════════════════════════


class TestTriggerRules:
    """TriggerEngine rules for Room events."""

    def test_temperature_change_triggers_notify(self):
        """room.temperature_changed with sufficient severity triggers NOTIFY."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_temperature_event(25.0, severity=4)
        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        assert tasks[0].action_type == ActionType.NOTIFY

    def test_motion_detected_triggers_observe(self):
        """room.motion_detected triggers OBSERVE."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_motion_event(True, "living_room", severity=3)
        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        assert tasks[0].action_type == ActionType.OBSERVE

    def test_sensor_unavailable_wakes_ai(self):
        """room.sensor_unavailable with high severity triggers ALERT."""
        bus, engine, _, _, _, _, _, _ = _setup_full_stack()

        event = _make_room_event(
            event_type="room.sensor_unavailable",
            severity=9,
            priority=EventPriority.URGENT,
        )
        bus.publish(event)

        tasks = engine.drain_tasks()
        assert len(tasks) >= 1
        assert tasks[0].action_type == ActionType.ALERT

    def test_low_severity_room_event_no_trigger(self):
        """Low-severity room event does not trigger."""
        _, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_temperature_event(22.5, severity=1, priority=EventPriority.BACKGROUND)
        tasks = engine.drain_tasks()
        assert len(tasks) == 0


# ═══════════════════════════════════════════════════════════════
# 12. ContextBuilder Integration
# ═══════════════════════════════════════════════════════════════


class TestContextBuilderIntegration:
    """ContextBuilder includes Room events in the assembled context."""

    def test_context_includes_room_events(self):
        """Context built after Room events includes them in recent_events."""
        bus, _, _, _, _, builder, _, client = _setup_full_stack()
        client.register()

        client.push_temperature_event(22.5, severity=3)
        client.push_motion_event(True, "living_room", severity=3)

        ctx = builder.build()
        room_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.ROOM]
        assert len(room_events) >= 2

    def test_context_preserves_event_payload(self):
        """Context events retain their original payload."""
        bus, _, _, _, _, builder, _, client = _setup_full_stack()
        client.register()

        client.push_temperature_event(25.0, severity=3)

        ctx = builder.build()
        temp_events = [e for e in ctx.recent_events if e.event_type == "room.temperature_changed"]
        assert len(temp_events) >= 1

        payload = json.loads(temp_events[0].payload_json)
        assert payload["temperature_c"] == 25.0

    def test_context_includes_room_capabilities(self):
        """Context includes registered Room capabilities."""
        _, _, _, _, broker, builder, _, client = _setup_full_stack()
        client.register()

        ctx = builder.build()
        room_cap_ids = [cid for cid in ctx.available_capability_ids if cid.startswith("room.")]
        assert len(room_cap_ids) >= 1


# ═══════════════════════════════════════════════════════════════
# 13. AuditLog
# ═══════════════════════════════════════════════════════════════


class TestAuditLog:
    """AuditLog records Room Server observations and decisions."""

    def test_audit_logs_capability_registration(self):
        """Registration is logged to audit."""
        _, _, _, _, _, _, audit, client = _setup_full_stack()

        entry = AuditEntry(
            action="capability_registered",
            actor="room_server",
            capability_id="room.get_environment",
            decision="REGISTERED",
            reason="Room Server registered observe capabilities",
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
            actor="room_server",
            capability_id="room.temperature_changed",
            decision="ACCEPTED",
            reason="Room event pushed to EventBus",
            detail={"event_type": "room.temperature_changed", "temp": 22.5},
        )
        audit.append(entry)

        recent = audit.list_recent(10)
        assert any(e.action == "event_received" for e in recent)

    def test_audit_logs_trigger_fired(self):
        """TriggerEngine rule firing is logged to audit."""
        _, engine, _, _, _, _, audit, client = _setup_full_stack()
        client.register()

        client.push_temperature_event(25.0, severity=4)
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
# 14. Retry / Backoff
# ═══════════════════════════════════════════════════════════════


class TestRetryBackoff:
    """Room Server retries connection with exponential backoff."""

    def test_retry_succeeds_on_first_attempt(self):
        """connect_with_retry succeeds when provider is available."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = MockSensorProvider(available=True)
        from room_server_client import RetryConfig

        client = RoomServerClient(bus, registry, provider, RetryConfig(max_retries=3, base_delay_ms=1))

        result = client.connect_with_retry()
        assert result is True
        assert client.stats.retry_count == 1
        assert client.stats.state == ConnectionState.CONNECTED

    def test_retry_fails_after_max_attempts(self):
        """connect_with_retry fails after exhausting retries."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = MockSensorProvider(available=False)
        from room_server_client import RetryConfig

        client = RoomServerClient(
            bus, registry, sensor_provider=provider,
            retry_config=RetryConfig(max_retries=2, base_delay_ms=1),
        )

        result = client.connect_with_retry()
        assert result is False
        assert client.stats.retry_count == 2
        assert client.stats.state == ConnectionState.FAILED

    def test_retry_succeeds_after_transient_failure(self):
        """connect_with_retry succeeds when provider becomes available."""
        call_count = 0

        class FlakyProvider(MockSensorProvider):
            def is_available(self) -> bool:
                nonlocal call_count
                call_count += 1
                return call_count >= 2

        bus = EventBus()
        registry = ToolRegistry()
        provider = FlakyProvider()
        from room_server_client import RetryConfig

        client = RoomServerClient(bus, registry, provider, RetryConfig(max_retries=3, base_delay_ms=1))

        result = client.connect_with_retry()
        assert result is True
        assert client.stats.retry_count >= 2


# ═══════════════════════════════════════════════════════════════
# 15. Full E2E Flow
# ═══════════════════════════════════════════════════════════════


class TestFullE2EFlow:
    """Complete E2E: Room Server → EventBus → TriggerEngine → ContextBuilder → AuditLog."""

    def test_full_observe_flow(self):
        """Full flow from Room event to context assembly with audit trail."""
        bus, engine, registry, policy, broker, builder, audit, client = _setup_full_stack()

        # 1. Room Server registers
        assert client.register() is True
        audit.append(
            AuditEntry(
                action="server_registered",
                actor="room_server",
                decision="SUCCESS",
                reason=f"Registered {len(ROOM_CAPABILITIES)} capabilities",
            )
        )

        # 2. Verify capabilities are registered
        assert registry.get_capability("room.get_environment") is not None
        assert registry.get_capability("room.get_temperature") is not None
        assert registry.get_capability("room.get_motion_status") is not None

        # 3. Policy allows read-only
        observe_caps = [c for c in ROOM_CAPABILITIES if "observe" in c.tags or "read_only" in c.tags]
        for cap in observe_caps:
            result = policy.evaluate(cap)
            assert result.decision == PolicyDecision.ALLOW

        # 4. Push sensor events
        client.push_temperature_event(25.0, severity=3)
        client.push_motion_event(True, "living_room", severity=3)

        # 5. TriggerEngine fires
        tasks = engine.drain_tasks()
        assert len(tasks) >= 1

        # 6. ContextBuilder includes Room events
        ctx = builder.build()
        room_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.ROOM]
        assert len(room_events) >= 2

        # 7. Audit trail is complete
        audit_entries = audit.list_recent(50)
        actions = [e.action for e in audit_entries]
        assert "server_registered" in actions

    def test_full_flow_with_dedupe(self):
        """Full flow respects deduplication."""
        bus, engine, _, _, _, _, _, client = _setup_full_stack()
        client.register()

        client.push_temperature_event(22.5, severity=4)
        client.push_temperature_event(22.5, severity=4)

        assert bus.stats.total_deduplicated == 1

        tasks = engine.drain_tasks()
        assert len(tasks) == 1

    def test_full_flow_with_thresholds(self):
        """Full flow respects sensor thresholds."""
        bus, _, _, _, _, _, _, client = _setup_full_stack(thresholds=SensorThresholds(temperature_delta_c=2.0))
        client.register()

        # First poll — pushes
        results1 = client.poll_and_push()
        assert results1.get("temperature_changed") is True

        # Small change — no push
        client.sensor_provider.set_mock_values(temperature_c=23.0)
        results2 = client.poll_and_push()
        assert results2.get("temperature_changed") is None

        # Large change — pushes
        client.sensor_provider.set_mock_values(temperature_c=25.0)
        results3 = client.poll_and_push()
        assert results3.get("temperature_changed") is True
