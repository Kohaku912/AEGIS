"""Room Server Action E2E — integration tests for Room Physical Action capabilities.

Tests the full action flow:
  Room Action → ToolBroker → PolicyEngine → Approval UI (if needed) → Execute → EventBus → AuditLog

CI uses MockSensorProvider + MockActuatorProvider (no real hardware).
Architecture reference: docs/architecture.md §3.5, §7
"""

from __future__ import annotations

import json

from aegis_ai.audit import AuditLog
from aegis_schema.models import (
    Capability,
    Event,
    RiskLevel,
    ServerType,
)
from approval import ApprovalStore, ApprovalType
from event_bus import EventBus
from policy_engine import PolicyDecision, PolicyEngine
from room_server_client import (
    ALLOWED_IR_COMMANDS,
    MockActuatorProvider,
    MockSensorProvider,
    RoomServerClient,
)
from tool_broker import InvokeStatus, ToolBroker
from tool_registry import ToolRegistry
from trigger_engine import TriggerEngine, create_default_rules

# ── Helpers ──────────────────────────────────────────────────

FullStack = tuple[
    EventBus,
    TriggerEngine,
    ToolRegistry,
    PolicyEngine,
    ToolBroker,
    AuditLog,
    RoomServerClient,
    ApprovalStore,
]


def _setup_full_stack(
    sensor_provider: MockSensorProvider | None = None,
    actuator_provider: MockActuatorProvider | None = None,
) -> FullStack:
    """Wire up the full AEGIS Core stack for Room Action E2E testing."""
    bus = EventBus()
    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)

    registry = ToolRegistry()
    approval_store = ApprovalStore()
    policy = PolicyEngine(approval_store=approval_store)
    broker = ToolBroker(registry, policy)

    audit = AuditLog(path="data/test_room_action_audit.jsonl")

    sp = sensor_provider or MockSensorProvider()
    ap = actuator_provider or MockActuatorProvider()
    client = RoomServerClient(
        bus,
        registry,
        sensor_provider=sp,
        actuator_provider=ap,
        tool_broker=broker,
    )

    bus.subscribe(engine.on_event)

    return bus, engine, registry, policy, broker, audit, client, approval_store


# ═══════════════════════════════════════════════════════════════
# 1. Capability Registration
# ═══════════════════════════════════════════════════════════════


class TestCapabilityRegistration:
    """Room Server registers observe + action capabilities."""

    def test_action_capabilities_registered(self):
        """All Room action capabilities are registered."""
        _, _, registry, _, _, _, client, _ = _setup_full_stack()
        client.register()

        action_caps = [
            "room.set_light",
            "room.set_air_conditioner",
            "room.send_ir_command",
            "room.set_smart_plug",
            "room.get_camera_snapshot",
            "room.stop_robot_arm",
            "room.emergency_stop_robot_arm",
        ]
        for cap_id in action_caps:
            cap = registry.get_capability(cap_id)
            assert cap is not None, f"Capability {cap_id} not registered"

    def test_observe_capabilities_still_registered(self):
        """Observe capabilities are still registered."""
        _, _, registry, _, _, _, client, _ = _setup_full_stack()
        client.register()

        for cap_id in ["room.get_environment", "room.get_temperature", "room.get_motion_status"]:
            assert registry.get_capability(cap_id) is not None

    def test_action_caps_have_correct_risk_levels(self):
        """Action capabilities have correct risk levels."""
        _, _, registry, _, _, _, client, _ = _setup_full_stack()
        client.register()

        # Level 1
        for cap_id in ["room.stop_robot_arm", "room.emergency_stop_robot_arm"]:
            cap = registry.get_capability(cap_id)
            assert cap.risk_level == RiskLevel.SAFE_ACTION, f"{cap_id} should be SAFE_ACTION"

        # Level 2
        for cap_id in [
            "room.set_light",
            "room.set_air_conditioner",
            "room.send_ir_command",
            "room.set_smart_plug",
            "room.get_camera_snapshot",
        ]:
            cap = registry.get_capability(cap_id)
            assert cap.risk_level == RiskLevel.APPROVAL_REQUIRED, f"{cap_id} should be APPROVAL_REQUIRED"


# ═══════════════════════════════════════════════════════════════
# 2. Light Control (Level 2 — approval required)
# ═══════════════════════════════════════════════════════════════


class TestLightControl:
    """room.set_light — Level 2, requires approval."""

    def test_light_requires_approval(self):
        """Light control requires approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("room.set_light")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_light_blocked_without_approval(self):
        """Light is blocked without approval."""
        _, _, _, _, broker, _, client, _ = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("room.set_light", {"device_id": "light-001", "power_on": True})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

    def test_light_works_after_approval(self):
        """Light works after user approval."""
        _, _, _, _, broker, _, client, approval_store = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("room.set_light", {"device_id": "light-001", "power_on": True})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_light(cap, params):
            return {"success": True, "device_id": params.get("device_id")}

        broker.register_mock("room.set_light", mock_light)

        result2 = broker.invoke_tool_approved("room.set_light", {"device_id": "light-001", "power_on": True})
        assert result2.success is True


# ═══════════════════════════════════════════════════════════════
# 3. AC Control (Level 2 — temperature range validation)
# ═══════════════════════════════════════════════════════════════


class TestACControl:
    """room.set_air_conditioner — Level 2, temperature range validation."""

    def test_ac_requires_approval(self):
        """AC control requires approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("room.set_air_conditioner")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_ac_temperature_in_range(self):
        """AC with valid temperature is accepted."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "room.set_air_conditioner",
            {
                "device_id": "ac-001",
                "power_on": True,
                "target_temperature_c": 24.0,
                "mode": "cool",
            },
        )
        assert result["success"] is True

    def test_ac_temperature_too_low(self):
        """AC with temperature below range is denied."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "room.set_air_conditioner",
            {
                "device_id": "ac-001",
                "power_on": True,
                "target_temperature_c": 10.0,
            },
        )
        assert "error" in result
        assert "out of range" in result["error"]

    def test_ac_temperature_too_high(self):
        """AC with temperature above range is denied."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "room.set_air_conditioner",
            {
                "device_id": "ac-001",
                "power_on": True,
                "target_temperature_c": 40.0,
            },
        )
        assert "error" in result
        assert "out of range" in result["error"]

    def test_ac_invalid_mode(self):
        """AC with invalid mode is denied."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "room.set_air_conditioner",
            {
                "device_id": "ac-001",
                "power_on": True,
                "mode": "turbo",
            },
        )
        assert "error" in result
        assert "Invalid AC mode" in result["error"]

    def test_ac_valid_modes(self):
        """AC accepts all valid modes."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        for mode in ["cool", "heat", "dry", "fan", "auto"]:
            result = client.invoke_capability(
                "room.set_air_conditioner",
                {
                    "device_id": "ac-001",
                    "power_on": True,
                    "mode": mode,
                },
            )
            assert result.get("success") is True, f"Mode '{mode}' should be valid"


# ═══════════════════════════════════════════════════════════════
# 4. IR Command (allowlisted commands only)
# ═══════════════════════════════════════════════════════════════


class TestIRCommand:
    """room.send_ir_command — allowlisted commands only."""

    def test_ir_requires_approval(self):
        """IR command requires approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("room.send_ir_command")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_ir_allowlisted_command(self):
        """Allowlisted IR command is accepted."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "room.send_ir_command",
            {
                "device_type": "tv",
                "ir_code": "tv_power",
            },
        )
        assert result["success"] is True

    def test_ir_unknown_command_denied(self):
        """Unknown IR command is denied."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "room.send_ir_command",
            {
                "device_type": "tv",
                "ir_code": "unknown_hack_code",
            },
        )
        assert "error" in result
        assert "not in allowlist" in result["error"]

    def test_ir_allowlist_contents(self):
        """IR allowlist contains expected commands."""
        assert "tv_power" in ALLOWED_IR_COMMANDS
        assert "ac_power" in ALLOWED_IR_COMMANDS
        assert "light_power" in ALLOWED_IR_COMMANDS


# ═══════════════════════════════════════════════════════════════
# 5. Camera Snapshot (Level 2 — approval required)
# ═══════════════════════════════════════════════════════════════


class TestCameraSnapshot:
    """room.get_camera_snapshot — Level 2, requires approval."""

    def test_camera_requires_approval(self):
        """Camera snapshot requires approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("room.get_camera_snapshot")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_camera_blocked_without_approval(self):
        """Camera is blocked without approval."""
        _, _, _, _, broker, _, client, _ = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("room.get_camera_snapshot", {"camera_id": "cam-001"})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

    def test_camera_works_after_approval(self):
        """Camera works after approval."""
        _, _, _, _, broker, _, client, approval_store = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("room.get_camera_snapshot", {"camera_id": "cam-001"})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_camera(cap, params):
            return {"success": True, "image_base64": "[MOCK]", "width": 640, "height": 480}

        broker.register_mock("room.get_camera_snapshot", mock_camera)

        result2 = broker.invoke_tool_approved("room.get_camera_snapshot", {"camera_id": "cam-001"})
        assert result2.success is True


# ═══════════════════════════════════════════════════════════════
# 6. Robot Arm (Level 3 deny / Level 1 stop)
# ═══════════════════════════════════════════════════════════════


class TestRobotArm:
    """Robot arm — move is Level 3 (denied), stop/emergency is Level 1."""

    def test_move_robot_arm_denied(self):
        """room.move_robot_arm is explicitly denied (Level 3)."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="room.move_robot_arm",
            name="Move Robot Arm",
            description="Move robot arm to position.",
            server_type=ServerType.ROOM,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_move_robot_arm_denied_by_client(self):
        """room.move_robot_arm is denied at client level."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "room.move_robot_arm",
            {
                "arm_id": "arm-001",
                "target_position_json": '{"x":100}',
            },
        )
        assert "error" in result
        assert "denied" in result["error"].lower()

    def test_stop_robot_arm_allowed(self):
        """room.stop_robot_arm is Level 1 (auto-allowed)."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("room.stop_robot_arm")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_emergency_stop_allowed(self):
        """room.emergency_stop_robot_arm is Level 1 (auto-allowed)."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("room.emergency_stop_robot_arm")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_stop_robot_arm_via_invoke(self):
        """Stop robot arm via invoke_capability works."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("room.stop_robot_arm", {"arm_id": "arm-001"})
        assert result["success"] is True
        assert "arm-001" in result["stopped_arms"]

    def test_emergency_stop_via_invoke(self):
        """Emergency stop via invoke_capability works."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("room.emergency_stop_robot_arm")
        assert result["success"] is True


# ═══════════════════════════════════════════════════════════════
# 7. Smart Plug (Level 2 — approval required)
# ═══════════════════════════════════════════════════════════════


class TestSmartPlug:
    """room.set_smart_plug — Level 2, requires approval."""

    def test_plug_requires_approval(self):
        """Smart plug requires approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("room.set_smart_plug")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_plug_works_after_approval(self):
        """Smart plug works after approval."""
        _, _, _, _, broker, _, client, approval_store = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("room.set_smart_plug", {"device_id": "plug-001", "power_on": True})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_plug(cap, params):
            return {"success": True, "device_id": params.get("device_id")}

        broker.register_mock("room.set_smart_plug", mock_plug)

        result2 = broker.invoke_tool_approved("room.set_smart_plug", {"device_id": "plug-001", "power_on": True})
        assert result2.success is True


# ═══════════════════════════════════════════════════════════════
# 8. Dangerous Actions — Deny
# ═══════════════════════════════════════════════════════════════


class TestDangerousActions:
    """Dangerous Room actions are explicitly denied."""

    def test_lock_denied(self):
        """room.lock_door is explicitly denied."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="room.lock_door",
            name="Lock Door",
            description="Lock a door.",
            server_type=ServerType.ROOM,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY


# ═══════════════════════════════════════════════════════════════
# 9. EventBus — Action Result Events
# ═══════════════════════════════════════════════════════════════


class TestActionResultEvents:
    """Room action results are pushed to EventBus."""

    def test_action_completed_event(self):
        """Successful action pushes room.action_completed."""
        bus, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_action_result_event("room.set_light", True, {"device_id": "light-001"})

        events = [e for e in received if e.event_type == "room.action_completed"]
        assert len(events) == 1

        payload = json.loads(events[0].payload_json)
        assert payload["success"] is True
        assert payload["capability_id"] == "room.set_light"

    def test_action_failed_event(self):
        """Failed action pushes room.action_failed."""
        bus, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_action_result_event("room.set_light", False, error="Approval denied")

        events = [e for e in received if e.event_type == "room.action_failed"]
        assert len(events) == 1

        payload = json.loads(events[0].payload_json)
        assert payload["success"] is False


# ═══════════════════════════════════════════════════════════════
# 10. Full E2E Flow
# ═══════════════════════════════════════════════════════════════


class TestFullE2EFlow:
    """Complete E2E: Room Action → ToolBroker → PolicyEngine → EventBus → AuditLog."""

    def test_full_flow_light_with_approval(self):
        """Full flow for light control (Level 2 with approval)."""
        bus, engine, registry, policy, broker, audit, client, approval_store = _setup_full_stack()
        client.register()

        # Level 2 — needs approval
        result = broker.invoke_tool("room.set_light", {"device_id": "light-001", "power_on": True})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        # Approve
        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_light(cap, params):
            return {"success": True, "device_id": params.get("device_id")}

        broker.register_mock("room.set_light", mock_light)

        result2 = broker.invoke_tool_approved("room.set_light", {"device_id": "light-001", "power_on": True})
        assert result2.success is True

        # Push event
        client.push_action_result_event("room.set_light", True, result2.output)

        # Audit
        audit.log_decision("room_action", "room.set_light", "APPROVED_AND_EXECUTED")

        recent = audit.list_recent(10)
        assert any(e.action == "room_action" for e in recent)

    def test_full_flow_emergency_stop(self):
        """Full flow for emergency stop (Level 1, auto-allowed)."""
        bus, engine, registry, policy, broker, audit, client, _ = _setup_full_stack()
        client.register()

        cap = registry.get_capability("room.emergency_stop_robot_arm")
        policy_result = policy.evaluate(cap)
        assert policy_result.decision == PolicyDecision.ALLOW

        result = client.invoke_capability("room.emergency_stop_robot_arm")
        assert result["success"] is True

        client.push_action_result_event("room.emergency_stop_robot_arm", True, result)
        audit.log_decision("room_action", "room.emergency_stop_robot_arm", "SUCCESS")

        recent = audit.list_recent(10)
        assert any(e.action == "room_action" for e in recent)

    def test_full_flow_ac_temperature_validation(self):
        """Full flow for AC with temperature validation."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        # Valid temperature
        result = client.invoke_capability(
            "room.set_air_conditioner",
            {
                "device_id": "ac-001",
                "power_on": True,
                "target_temperature_c": 24.0,
            },
        )
        assert result["success"] is True

        # Invalid temperature
        result2 = client.invoke_capability(
            "room.set_air_conditioner",
            {
                "device_id": "ac-001",
                "power_on": True,
                "target_temperature_c": 5.0,
            },
        )
        assert "error" in result2

    def test_full_flow_ir_allowlist(self):
        """Full flow for IR command with allowlist check."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        # Allowed command
        result = client.invoke_capability(
            "room.send_ir_command",
            {
                "device_type": "tv",
                "ir_code": "tv_power",
            },
        )
        assert result["success"] is True

        # Unknown command
        result2 = client.invoke_capability(
            "room.send_ir_command",
            {
                "device_type": "tv",
                "ir_code": "hack_code",
            },
        )
        assert "error" in result2
