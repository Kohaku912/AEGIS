"""Tests for AEGIS Plugin SDK."""

from __future__ import annotations


from aegis_sdk.capability import define_capability
from aegis_sdk.events import EventClient, make_dedupe_key, make_event
from aegis_sdk.registration import RegistrationClient
from aegis_sdk.safety import check_forbidden_proximity, validate_capability_definition
from aegis_sdk.testing import (
    MockAEGISCore,
    run_capability_registration_check,
    run_event_push_check,
    run_policy_flow_check,
)
from aegis_schema.models import RiskLevel, ServerType
from policy_engine import PolicyDecision


# ═══════════════════════════════════════════════════════════════
# 1. Capability Definition Helper
# ═══════════════════════════════════════════════════════════════


class TestDefineCapability:
    """define_capability creates valid capabilities."""

    def test_read_only_capability(self):
        """READ_ONLY capability is created correctly."""
        cap = define_capability(
            server_prefix="dev",
            action="get_weather",
            name="Get Weather",
            description="Retrieve weather data.",
            risk_level=RiskLevel.READ_ONLY,
            tags=["weather", "observe"],
        )
        assert cap.id == "dev.get_weather"
        assert cap.risk_level == RiskLevel.READ_ONLY
        assert cap.requires_approval is False

    def test_approval_required_capability(self):
        """APPROVAL_REQUIRED capability has requires_approval=True."""
        cap = define_capability(
            server_prefix="dev",
            action="set_alert",
            name="Set Alert",
            description="Set an alert.",
            risk_level=RiskLevel.APPROVAL_REQUIRED,
            side_effects=["notification"],
            tags=["alert", "action"],
        )
        assert cap.id == "dev.set_alert"
        assert cap.risk_level == RiskLevel.APPROVAL_REQUIRED
        assert cap.requires_approval is True

    def test_missing_side_effects_rejected(self):
        """Level 2+ without side_effects is rejected."""
        import pytest
        with pytest.raises(ValueError, match="side_effects"):
            define_capability(
                server_prefix="dev",
                action="bad_cap",
                name="Bad",
                description="Missing side effects",
                risk_level=RiskLevel.APPROVAL_REQUIRED,
            )

    def test_forbidden_pattern_rejected(self):
        """Capability matching forbidden pattern is rejected."""
        import pytest
        with pytest.raises(ValueError, match="forbidden"):
            define_capability(
                server_prefix="dev",
                action="send_sns",
                name="Send SNS",
                description="Post to social media",
                risk_level=RiskLevel.READ_ONLY,
            )


# ═══════════════════════════════════════════════════════════════
# 2. Safety Validator
# ═══════════════════════════════════════════════════════════════


class TestSafetyValidator:
    """Safety validator catches dangerous definitions."""

    def test_valid_capability(self):
        """Valid capability has no errors."""
        errors = validate_capability_definition(
            cap_id="dev.get_forecast",
            name="Get Forecast",
            description="Get weather forecast",
            risk_level=RiskLevel.READ_ONLY,
            side_effects=[],
            tags=["weather"],
        )
        assert errors == []

    def test_unspecified_risk_rejected(self):
        """UNSPECIFIED risk level is rejected."""
        errors = validate_capability_definition(
            cap_id="dev.cap",
            name="Test",
            description="Test",
            risk_level=RiskLevel.UNSPECIFIED,
            side_effects=[],
            tags=[],
        )
        assert len(errors) >= 1

    def test_forbidden_risk_rejected(self):
        """FORBIDDEN risk level is rejected."""
        errors = validate_capability_definition(
            cap_id="dev.cap",
            name="Test",
            description="Test",
            risk_level=RiskLevel.FORBIDDEN,
            side_effects=[],
            tags=[],
        )
        assert len(errors) >= 1

    def test_forbidden_pattern_rejected(self):
        """Capability matching forbidden pattern is rejected."""
        errors = validate_capability_definition(
            cap_id="dev.send_sns",
            name="Send SNS",
            description="Post to SNS",
            risk_level=RiskLevel.READ_ONLY,
            side_effects=[],
            tags=[],
        )
        assert len(errors) >= 1

    def test_missing_description_rejected(self):
        """Missing description is rejected."""
        errors = validate_capability_definition(
            cap_id="dev.cap",
            name="Test",
            description="",
            risk_level=RiskLevel.READ_ONLY,
            side_effects=[],
            tags=[],
        )
        assert len(errors) >= 1

    def test_level2_missing_side_effects(self):
        """Level 2+ without side_effects is rejected."""
        errors = validate_capability_definition(
            cap_id="dev.cap",
            name="Test",
            description="Test",
            risk_level=RiskLevel.APPROVAL_REQUIRED,
            side_effects=[],
            tags=[],
        )
        assert len(errors) >= 1

    def test_forbidden_proximity_warning(self):
        """check_forbidden_proximity returns warnings for similar names."""
        warnings = check_forbidden_proximity("dev.delete_something")
        assert len(warnings) >= 1


# ═══════════════════════════════════════════════════════════════
# 3. Registration Client
# ═══════════════════════════════════════════════════════════════


class TestRegistrationClient:
    """Registration client registers server and capabilities."""

    def test_register_server(self):
        """Server registration works."""
        from tool_registry import ToolRegistry

        registry = ToolRegistry()
        client = RegistrationClient(
            server_id="test-server",
            server_type=ServerType.DEV,
        )
        assert client.register_server(registry) is True
        assert client.is_registered is True
        assert registry.get_server("test-server") is not None

    def test_register_capability(self):
        """Capability registration works."""
        from tool_registry import ToolRegistry

        registry = ToolRegistry()
        client = RegistrationClient(
            server_id="test-server",
            server_type=ServerType.DEV,
        )
        client.register_server(registry)

        cap = define_capability(
            server_prefix="dev",
            action="hello",
            name="Hello",
            description="Say hello",
            risk_level=RiskLevel.READ_ONLY,
        )
        assert client.register_capability(registry, cap) is True
        assert registry.get_capability("dev.hello") is not None

    def test_unregister(self):
        """Unregistration removes server and capabilities."""
        from tool_registry import ToolRegistry

        registry = ToolRegistry()
        client = RegistrationClient(
            server_id="test-server",
            server_type=ServerType.DEV,
        )
        client.register_server(registry)
        cap = define_capability(
            server_prefix="dev", action="hello",
            name="Hello", description="Say hello",
            risk_level=RiskLevel.READ_ONLY,
        )
        client.register_capability(registry, cap)

        client.unregister(registry)
        assert registry.get_server("test-server") is None


# ═══════════════════════════════════════════════════════════════
# 4. Event Client
# ═══════════════════════════════════════════════════════════════


class TestEventClient:
    """Event client publishes events to EventBus."""

    def test_publish_event(self):
        """Event publishing works."""
        from event_bus import EventBus

        bus = EventBus()
        client = EventClient(
            server_type=ServerType.ROOM,
            server_id="test-server",
        )
        accepted = client.publish(bus, "test.event", {"key": "value"})
        assert accepted is True
        assert bus.stats.total_published >= 1

    def test_make_event(self):
        """make_event creates valid events."""
        event = make_event(
            event_type="test.event",
            server_type=ServerType.DEV,
            server_id="test-server",
            payload={"key": "value"},
        )
        assert event.event_type == "test.event"
        assert event.source_server_type == ServerType.DEV

    def test_make_dedupe_key(self):
        """make_dedupe_key creates deterministic keys."""
        key1 = make_dedupe_key("test.event", "server", "part1")
        key2 = make_dedupe_key("test.event", "server", "part1")
        assert key1 == key2
        assert "test.event" in key1


# ═══════════════════════════════════════════════════════════════
# 5. Test Harness
# ═══════════════════════════════════════════════════════════════


class TestMockAEGISCore:
    """MockAEGISCore provides full test environment."""

    def test_register_and_invoke(self):
        """Register server, capability, and invoke."""
        core = MockAEGISCore()

        cap = define_capability(
            server_prefix="dev", action="hello",
            name="Hello", description="Say hello",
            risk_level=RiskLevel.READ_ONLY,
        )
        core.register_capability(cap)

        # Register mock executor
        core.broker.register_mock("dev.hello", lambda cap, p: {"greeting": "Hello!"})

        result = core.invoke_capability("dev.hello")
        assert result["success"] is True
        assert result["output"]["greeting"] == "Hello!"

    def test_policy_enforcement(self):
        """Policy enforcement works through MockAEGISCore."""
        core = MockAEGISCore()

        cap = define_capability(
            server_prefix="dev", action="dangerous",
            name="Dangerous", description="A dangerous action",
            risk_level=RiskLevel.APPROVAL_REQUIRED,
            side_effects=["side_effect"],
        )
        core.register_capability(cap)

        result = core.invoke_capability("dev.dangerous")
        assert result["status"] == "APPROVAL_NEEDED"

    def test_event_publishing(self):
        """Event publishing works through MockAEGISCore."""
        core = MockAEGISCore()
        event = make_event(
            event_type="test.event",
            server_type=ServerType.DEV,
            server_id="test-server",
        )
        accepted = core.publish_event(event)
        assert accepted is True
        assert len(core.get_recent_events()) >= 1


class TestHelperFunctions:
    """Test helper functions work correctly."""

    def test_capability_registration_helper(self):
        """run_capability_registration_check helper works."""
        core = MockAEGISCore()
        from aegis_schema.models import ServerInfo, ServerStatus

        server_info = ServerInfo(
            server_id="test-server",
            server_type=ServerType.DEV,
            status=ServerStatus.ONLINE,
        )
        caps = [
            define_capability(
                server_prefix="dev", action="hello",
                name="Hello", description="Say hello",
                risk_level=RiskLevel.READ_ONLY,
            ),
        ]
        errors = run_capability_registration_check(core, server_info, caps)
        assert errors == []

    def test_policy_flow_helper(self):
        """run_policy_flow_check helper works."""
        core = MockAEGISCore()
        cap = define_capability(
            server_prefix="dev", action="hello",
            name="Hello", description="Say hello",
            risk_level=RiskLevel.READ_ONLY,
        )
        errors = run_policy_flow_check(core, cap, PolicyDecision.ALLOW)
        assert errors == []

    def test_event_push_helper(self):
        """run_event_push_check helper works."""
        core = MockAEGISCore()
        event = make_event(
            event_type="test.event",
            server_type=ServerType.DEV,
            server_id="test-server",
        )
        errors = run_event_push_check(core, event, expected_accepted=True)
        assert errors == []
