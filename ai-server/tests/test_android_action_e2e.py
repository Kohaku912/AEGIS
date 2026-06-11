"""Android Server Action E2E — integration tests for Android Screenshot/UI/Overlay/Action.

Tests the full action flow:
  Android Action → ToolBroker → PolicyEngine → Approval UI (if needed) → Execute → EventBus → AuditLog

CI uses MockAndroidProvider (no real device calls).
Architecture reference: docs/architecture.md §3.3, §7
"""

from __future__ import annotations

import json

from aegis_ai.audit import AuditLog
from aegis_schema.models import (
    Capability,
    Event,
    EventPriority,
    RiskLevel,
    ServerType,
)
from android_server_client import (
    AndroidPermissions,
    AndroidServerClient,
    MockAndroidProvider,
    PermissionState,
    contains_password_field,
)
from approval import ApprovalStore, ApprovalType
from event_bus import EventBus
from policy_engine import PolicyDecision, PolicyEngine
from tool_broker import InvokeStatus, ToolBroker
from tool_registry import ToolRegistry
from trigger_engine import TriggerEngine, create_default_rules

# ── Helpers ──────────────────────────────────────────────────

# Type alias for the full stack tuple
FullStack = tuple[
    EventBus, TriggerEngine, ToolRegistry, PolicyEngine,
    ToolBroker, AuditLog, AndroidServerClient, ApprovalStore,
]


def _setup_full_stack(
    provider: MockAndroidProvider | None = None,
    permissions: AndroidPermissions | None = None,
) -> FullStack:
    """Wire up the full AEGIS Core stack for Android Action E2E testing."""
    bus = EventBus()
    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)

    registry = ToolRegistry()
    approval_store = ApprovalStore()
    policy = PolicyEngine(approval_store=approval_store)
    broker = ToolBroker(registry, policy)

    audit = AuditLog(path="data/test_android_action_audit.jsonl")

    provider = provider or MockAndroidProvider()
    perms = permissions or AndroidPermissions(
        notification_listener=PermissionState.GRANTED,
        media_projection=PermissionState.GRANTED,
        accessibility_service=PermissionState.GRANTED,
        overlay=PermissionState.GRANTED,
    )
    client = AndroidServerClient(bus, registry, provider, permissions=perms, tool_broker=broker)

    bus.subscribe(engine.on_event)

    return bus, engine, registry, policy, broker, audit, client, approval_store


# ═══════════════════════════════════════════════════════════════
# 1. Capability Registration
# ═══════════════════════════════════════════════════════════════


class TestCapabilityRegistration:
    """Android Server registers observe + action capabilities."""

    def test_action_capabilities_registered(self):
        """All Android action capabilities are registered."""
        _, _, registry, _, _, _, client, _ = _setup_full_stack()
        client.register()

        action_caps = [
            "android.get_screenshot",
            "android.get_ui_tree",
            "android.show_overlay",
            "android.hide_overlay",
            "android.open_app",
            "android.press_home",
            "android.tap",
            "android.swipe",
            "android.type_text",
        ]
        for cap_id in action_caps:
            cap = registry.get_capability(cap_id)
            assert cap is not None, f"Capability {cap_id} not registered"

    def test_observe_capabilities_still_registered(self):
        """Observe capabilities are still registered."""
        _, _, registry, _, _, _, client, _ = _setup_full_stack()
        client.register()

        for cap_id in ["android.get_notifications", "android.get_current_app", "android.get_device_info"]:
            assert registry.get_capability(cap_id) is not None

    def test_action_caps_have_correct_risk_levels(self):
        """Action capabilities have correct risk levels."""
        _, _, registry, _, _, _, client, _ = _setup_full_stack()
        client.register()

        # Level 0
        for cap_id in ["android.get_screenshot", "android.get_ui_tree"]:
            cap = registry.get_capability(cap_id)
            assert cap.risk_level == RiskLevel.READ_ONLY, f"{cap_id} should be READ_ONLY"

        # Level 1
        for cap_id in ["android.show_overlay", "android.hide_overlay", "android.open_app", "android.press_home"]:
            cap = registry.get_capability(cap_id)
            assert cap.risk_level == RiskLevel.SAFE_ACTION, f"{cap_id} should be SAFE_ACTION"

        # Level 2
        for cap_id in ["android.tap", "android.swipe", "android.type_text"]:
            cap = registry.get_capability(cap_id)
            assert cap.risk_level == RiskLevel.APPROVAL_REQUIRED, f"{cap_id} should be APPROVAL_REQUIRED"


# ═══════════════════════════════════════════════════════════════
# 2. Screenshot Observe (Level 0)
# ═══════════════════════════════════════════════════════════════


class TestScreenshot:
    """android.get_screenshot — Level 0, auto-allowed."""

    def test_screenshot_allowed(self):
        """Screenshot is allowed without approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("android.get_screenshot")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_screenshot_via_invoke(self):
        """Screenshot via invoke_capability works."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("android.get_screenshot", {"quality": 80})
        assert result["success"] is True
        assert result["image_base64"] == "[MOCK_SCREENSHOT]"
        assert result["width"] == 1080

    def test_screenshot_via_broker(self):
        """Screenshot via ToolBroker succeeds."""
        _, _, _, _, broker, _, client, _ = _setup_full_stack()
        client.register()

        def mock_screenshot(cap, params):
            return {"success": True, "image_base64": "[MOCK]", "width": 1080, "height": 2400}

        broker.register_mock("android.get_screenshot", mock_screenshot)

        result = broker.invoke_tool("android.get_screenshot", {"quality": 80})
        assert result.success is True


# ═══════════════════════════════════════════════════════════════
# 3. UI Tree Observe (Level 0)
# ═══════════════════════════════════════════════════════════════


class TestUITree:
    """android.get_ui_tree — Level 0, auto-allowed."""

    def test_ui_tree_allowed(self):
        """UI tree is allowed without approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("android.get_ui_tree")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_ui_tree_via_invoke(self):
        """UI tree via invoke_capability works."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("android.get_ui_tree")
        assert result["success"] is True
        assert "root" in result
        assert result["root"]["class_name"] == "android.widget.FrameLayout"

    def test_ui_tree_contains_password_field(self):
        """Mock UI tree contains a password field."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("android.get_ui_tree")
        assert contains_password_field(result["root"]) is True

    def test_ui_tree_children(self):
        """UI tree has expected children."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("android.get_ui_tree")
        children = result["root"]["children"]
        assert len(children) == 3
        assert children[0]["text"] == "Hello World"
        assert children[1]["text"] == "Submit"
        assert children[2]["is_password"] is True


# ═══════════════════════════════════════════════════════════════
# 4. Overlay (Level 1)
# ═══════════════════════════════════════════════════════════════


class TestOverlay:
    """android.show_overlay / android.hide_overlay — Level 1, auto-allowed."""

    def test_show_overlay_allowed(self):
        """Show overlay is allowed without approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("android.show_overlay")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_show_overlay_via_invoke(self):
        """Show overlay via invoke_capability works."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("android.show_overlay", {"text": "Hello from AEGIS"})
        assert result["success"] is True
        assert result["overlay_id"] == "mock_overlay_001"

    def test_hide_overlay_via_invoke(self):
        """Hide overlay via invoke_capability works."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("android.hide_overlay", {"overlay_id": "mock_overlay_001"})
        assert result["success"] is True


# ═══════════════════════════════════════════════════════════════
# 5. Tap (Level 2 — approval required)
# ═══════════════════════════════════════════════════════════════


class TestTap:
    """android.tap — Level 2, requires approval."""

    def test_tap_requires_approval(self):
        """Tap requires approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("android.tap")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_tap_blocked_without_approval(self):
        """Tap is blocked without approval."""
        _, _, _, _, broker, _, client, _ = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("android.tap", {"x": 500, "y": 300})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

    def test_tap_works_after_approval(self):
        """Tap works after user approval."""
        _, _, _, _, broker, _, client, approval_store = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("android.tap", {"x": 500, "y": 300})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_tap(cap, params):
            return {"success": True, "x": params.get("x"), "y": params.get("y")}

        broker.register_mock("android.tap", mock_tap)

        result2 = broker.invoke_tool_approved("android.tap", {"x": 500, "y": 300})
        assert result2.success is True


# ═══════════════════════════════════════════════════════════════
# 6. Type Text (Level 2 — approval required, password denied)
# ═══════════════════════════════════════════════════════════════


class TestTypeText:
    """android.type_text — Level 2, requires approval, password fields denied."""

    def test_type_text_requires_approval(self):
        """Type text requires approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("android.type_text")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_type_text_blocked_without_approval(self):
        """Type text is blocked without approval."""
        _, _, _, _, broker, _, client, _ = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("android.type_text", {"text": "Hello"})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

    def test_type_text_password_field_denied(self):
        """Type text into password field is denied."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "android.type_text",
            {
                "text": "mypassword",
                "is_password_field": True,
            },
        )
        assert "error" in result
        assert "password" in result["error"].lower()

    def test_type_text_works_after_approval(self):
        """Type text works after approval for non-password field."""
        _, _, _, _, broker, _, client, approval_store = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("android.type_text", {"text": "Hello"})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_type(cap, params):
            return {"success": True, "characters_typed": len(params.get("text", ""))}

        broker.register_mock("android.type_text", mock_type)

        result2 = broker.invoke_tool_approved("android.type_text", {"text": "Hello"})
        assert result2.success is True


# ═══════════════════════════════════════════════════════════════
# 7. Dangerous Actions — Deny
# ═══════════════════════════════════════════════════════════════


class TestDangerousActions:
    """Dangerous Android actions are explicitly denied."""

    def test_send_sms_denied(self):
        """android.send_sms is explicitly denied."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="android.send_sms",
            name="Send SMS",
            description="Send an SMS message.",
            server_type=ServerType.ANDROID,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_send_dm_denied(self):
        """android.send_dm is explicitly denied."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="android.send_dm",
            name="Send DM",
            description="Send a direct message.",
            server_type=ServerType.ANDROID,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_access_contacts_denied(self):
        """android.access_contacts is explicitly denied."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="android.access_contacts",
            name="Access Contacts",
            description="Read contacts.",
            server_type=ServerType.ANDROID,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_type_password_denied(self):
        """android.type_password is explicitly denied."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="android.type_password",
            name="Type Password",
            description="Automatically type a password.",
            server_type=ServerType.ANDROID,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY


# ═══════════════════════════════════════════════════════════════
# 8. Permission State
# ═══════════════════════════════════════════════════════════════


class TestPermissionState:
    """Permission state tracking and missing permission events."""

    def test_permissions_granted(self):
        """All permissions granted by default in test."""
        perms = AndroidPermissions(
            notification_listener=PermissionState.GRANTED,
            media_projection=PermissionState.GRANTED,
            accessibility_service=PermissionState.GRANTED,
            overlay=PermissionState.GRANTED,
        )
        assert perms.is_granted("notification_listener") is True
        assert perms.is_granted("media_projection") is True
        assert perms.get_missing_permissions() == []

    def test_missing_permissions_detected(self):
        """Missing permissions are detected."""
        perms = AndroidPermissions(
            notification_listener=PermissionState.GRANTED,
            media_projection=PermissionState.DENIED,
            accessibility_service=PermissionState.NOT_REQUESTED,
            overlay=PermissionState.GRANTED,
        )
        missing = perms.get_missing_permissions()
        assert "media_projection" in missing
        assert "accessibility_service" in missing
        assert "notification_listener" not in missing

    def test_permission_missing_event_pushed(self):
        """Permission missing event is pushed to EventBus."""
        bus, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_permission_missing_event("media_projection")

        events = [e for e in received if e.event_type == "android.permission_missing"]
        assert len(events) == 1
        assert events[0].priority == EventPriority.URGENT

        payload = json.loads(events[0].payload_json)
        assert payload["permission"] == "media_projection"


# ═══════════════════════════════════════════════════════════════
# 9. EventBus — Action Result Events
# ═══════════════════════════════════════════════════════════════


class TestActionResultEvents:
    """Android action results are pushed to EventBus."""

    def test_action_completed_event(self):
        """Successful action pushes android.action_completed."""
        bus, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_action_result_event("android.tap", True, {"x": 500, "y": 300})

        events = [e for e in received if e.event_type == "android.action_completed"]
        assert len(events) == 1

        payload = json.loads(events[0].payload_json)
        assert payload["success"] is True
        assert payload["capability_id"] == "android.tap"

    def test_action_failed_event(self):
        """Failed action pushes android.action_failed."""
        bus, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_action_result_event("android.tap", False, error="Approval denied")

        events = [e for e in received if e.event_type == "android.action_failed"]
        assert len(events) == 1

        payload = json.loads(events[0].payload_json)
        assert payload["success"] is False


# ═══════════════════════════════════════════════════════════════
# 10. AuditLog
# ═══════════════════════════════════════════════════════════════


class TestAuditLog:
    """Android actions are recorded in AuditLog."""

    def test_action_recorded_in_audit(self):
        """Action execution is recorded in AuditLog."""
        _, _, _, _, _, audit, client, _ = _setup_full_stack()
        client.register()

        output = client.invoke_capability("android.show_overlay", {"text": "Test"})

        audit.log_decision(
            "android_action_executed",
            "android.show_overlay",
            "SUCCESS",
            detail={"output": output},
        )

        recent = audit.list_recent(10)
        action_entries = [e for e in recent if e.action == "android_action_executed"]
        assert len(action_entries) >= 1


# ═══════════════════════════════════════════════════════════════
# 11. Provider Unavailable
# ═══════════════════════════════════════════════════════════════


class TestProviderUnavailable:
    """Graceful failure when Android provider is unavailable."""

    def test_action_fails_when_unavailable(self):
        """Action returns error when provider is down."""
        provider = MockAndroidProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = AndroidServerClient(bus, registry, provider)

        result = client.invoke_capability("android.get_screenshot")
        assert "error" in result
        assert "not available" in result["error"]


# ═══════════════════════════════════════════════════════════════
# 12. Full E2E Flow
# ═══════════════════════════════════════════════════════════════


class TestFullE2EFlow:
    """Complete E2E: Android Action → ToolBroker → PolicyEngine → EventBus → AuditLog."""

    def test_full_flow_screenshot_observe(self):
        """Full flow for screenshot observe (Level 0)."""
        bus, engine, registry, policy, broker, audit, client, _ = _setup_full_stack()
        client.register()

        cap = registry.get_capability("android.get_screenshot")
        policy_result = policy.evaluate(cap)
        assert policy_result.decision == PolicyDecision.ALLOW

        def mock_screenshot(cap, params):
            return {"success": True, "image_base64": "[MOCK]", "width": 1080, "height": 2400}

        broker.register_mock("android.get_screenshot", mock_screenshot)
        invoke_result = broker.invoke_tool("android.get_screenshot", {"quality": 80})
        assert invoke_result.success is True

        client.push_action_result_event("android.get_screenshot", True, invoke_result.output)
        audit.log_decision("android_action", "android.get_screenshot", "SUCCESS")

        recent = audit.list_recent(10)
        assert any(e.action == "android_action" for e in recent)

    def test_full_flow_tap_with_approval(self):
        """Full flow for tap (Level 2 with approval)."""
        bus, engine, registry, policy, broker, audit, client, approval_store = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("android.tap", {"x": 500, "y": 300})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_tap(cap, params):
            return {"success": True, "x": params.get("x"), "y": params.get("y")}

        broker.register_mock("android.tap", mock_tap)

        result2 = broker.invoke_tool_approved("android.tap", {"x": 500, "y": 300})
        assert result2.success is True

        client.push_action_result_event("android.tap", True, result2.output)
        audit.log_decision("android_action", "android.tap", "APPROVED_AND_EXECUTED")

    def test_full_flow_deny_dangerous(self):
        """Full flow for dangerous action (denied)."""
        bus, engine, registry, policy, broker, audit, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="android.send_sms",
            name="Send SMS",
            description="Send SMS.",
            server_type=ServerType.ANDROID,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

        audit.log_decision("android_action_denied", "android.send_sms", "DENY", reason=result.reason)

        recent = audit.list_recent(10)
        assert any(e.action == "android_action_denied" for e in recent)

    def test_full_flow_permission_missing(self):
        """Full flow for permission missing scenario."""
        bus, _, _, _, _, _, client, _ = _setup_full_stack(
            permissions=AndroidPermissions(
                notification_listener=PermissionState.GRANTED,
                media_projection=PermissionState.DENIED,
                accessibility_service=PermissionState.NOT_REQUESTED,
                overlay=PermissionState.GRANTED,
            ),
        )
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        missing = client.permissions.get_missing_permissions()
        for perm in missing:
            client.push_permission_missing_event(perm)

        permission_events = [e for e in received if e.event_type == "android.permission_missing"]
        assert len(permission_events) == 2
