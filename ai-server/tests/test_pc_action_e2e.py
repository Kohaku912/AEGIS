"""PC Server Action E2E — integration tests for PC Action capabilities.

Tests the full action flow:
  PC Action → ToolBroker → PolicyEngine → Approval UI (if needed) → Execute → EventBus → AuditLog

CI uses MockPCProvider (no real OS calls).
Architecture reference: docs/architecture.md §3.2, §7
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
from pc_server_client import (
    MockPCProvider,
    PCServerClient,
    is_path_allowed,
    is_path_denied,
)
from policy_engine import PolicyDecision, PolicyEngine
from tool_broker import InvokeStatus, ToolBroker
from tool_registry import ToolRegistry
from trigger_engine import TriggerEngine, create_default_rules

# ── Helpers ──────────────────────────────────────────────────


def _setup_full_stack(
    provider: MockPCProvider | None = None,
) -> tuple[EventBus, TriggerEngine, ToolRegistry, PolicyEngine, ToolBroker, AuditLog, PCServerClient, ApprovalStore]:
    """Wire up the full AEGIS Core stack for PC Action E2E testing."""
    bus = EventBus()
    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)

    registry = ToolRegistry()
    approval_store = ApprovalStore()
    policy = PolicyEngine(approval_store=approval_store)
    broker = ToolBroker(registry, policy)

    audit = AuditLog(path="data/test_pc_action_audit.jsonl")

    provider = provider or MockPCProvider()
    client = PCServerClient(bus, registry, provider, tool_broker=broker)

    bus.subscribe(engine.on_event)

    return bus, engine, registry, policy, broker, audit, client, approval_store


# ═══════════════════════════════════════════════════════════════
# 1. Capability Registration
# ═══════════════════════════════════════════════════════════════


class TestCapabilityRegistration:
    """PC Server registers both observe and action capabilities."""

    def test_action_capabilities_registered(self):
        """All PC action capabilities are registered."""
        _, _, registry, _, _, _, client, _ = _setup_full_stack()
        client.register()

        action_caps = [
            "pc.mouse_move",
            "pc.mouse_click",
            "pc.keyboard_type",
            "pc.press_hotkey",
            "pc.launch_app",
            "pc.close_window",
            "pc.focus_window",
            "pc.move_window",
            "pc.resize_window",
            "pc.show_overlay",
            "pc.hide_overlay",
            "pc.write_clipboard",
            "pc.read_file",
            "pc.write_file",
        ]
        for cap_id in action_caps:
            cap = registry.get_capability(cap_id)
            assert cap is not None, f"Capability {cap_id} not registered"

    def test_observe_capabilities_still_registered(self):
        """Observe capabilities are still registered."""
        _, _, registry, _, _, _, client, _ = _setup_full_stack()
        client.register()

        for cap_id in ["pc.get_screenshot", "pc.get_active_window", "pc.list_windows"]:
            assert registry.get_capability(cap_id) is not None

    def test_action_caps_have_correct_risk_levels(self):
        """Action capabilities have correct risk levels."""
        _, _, registry, _, _, _, client, _ = _setup_full_stack()
        client.register()

        # Level 1 (SAFE_ACTION)
        for cap_id in [
            "pc.mouse_move",
            "pc.launch_app",
            "pc.focus_window",
            "pc.move_window",
            "pc.resize_window",
            "pc.show_overlay",
            "pc.hide_overlay",
        ]:
            cap = registry.get_capability(cap_id)
            assert cap.risk_level == RiskLevel.SAFE_ACTION, f"{cap_id} should be SAFE_ACTION"

        # Level 2 (APPROVAL_REQUIRED)
        for cap_id in [
            "pc.mouse_click",
            "pc.keyboard_type",
            "pc.press_hotkey",
            "pc.close_window",
            "pc.write_clipboard",
            "pc.write_file",
        ]:
            cap = registry.get_capability(cap_id)
            assert cap.risk_level == RiskLevel.APPROVAL_REQUIRED, f"{cap_id} should be APPROVAL_REQUIRED"

    def test_read_file_is_read_only(self):
        """pc.read_file is Level 0 READ_ONLY."""
        _, _, registry, _, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = registry.get_capability("pc.read_file")
        assert cap.risk_level == RiskLevel.READ_ONLY


# ═══════════════════════════════════════════════════════════════
# 2. Level 1 — Launch App (auto-allowed)
# ═══════════════════════════════════════════════════════════════


class TestLaunchApp:
    """pc.launch_app — Level 1, auto-allowed without approval."""

    def test_launch_app_allowed(self):
        """Launch app is allowed without approval (Level 1)."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("pc.launch_app")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_launch_app_via_broker(self):
        """Launch app via ToolBroker succeeds."""
        _, _, _, _, broker, _, client, _ = _setup_full_stack()
        client.register()

        def mock_launch(cap, params):
            return {"success": True, "pid": 12345, "app_path": params.get("app_path", "")}

        broker.register_mock("pc.launch_app", mock_launch)

        result = broker.invoke_tool("pc.launch_app", {"app_path": "notepad.exe"})
        assert result.success is True
        assert result.output["pid"] == 12345

    def test_launch_app_pushes_event(self):
        """Launch app pushes action result event to EventBus."""
        bus, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        output = client.invoke_capability("pc.launch_app", {"app_path": "notepad.exe"})
        assert output["success"] is True

        client.push_action_result_event("pc.launch_app", True, output)

        action_events = [e for e in received if e.event_type == "pc.action_result"]
        assert len(action_events) >= 1


# ═══════════════════════════════════════════════════════════════
# 3. Level 1 — Overlay Display
# ═══════════════════════════════════════════════════════════════


class TestOverlay:
    """pc.show_overlay / pc.hide_overlay — Level 1, auto-allowed."""

    def test_show_overlay_allowed(self):
        """Show overlay is allowed without approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("pc.show_overlay")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_show_overlay_via_broker(self):
        """Show overlay via ToolBroker succeeds."""
        _, _, _, _, broker, _, client, _ = _setup_full_stack()
        client.register()

        def mock_show(cap, params):
            return {"success": True, "overlay_id": "mock_overlay_001"}

        broker.register_mock("pc.show_overlay", mock_show)

        result = broker.invoke_tool("pc.show_overlay", {"text": "Hello from AEGIS"})
        assert result.success is True

    def test_hide_overlay_allowed(self):
        """Hide overlay is allowed without approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("pc.hide_overlay")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_overlay_invoke_capability(self):
        """Overlay invoke through client works."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        show_result = client.invoke_capability("pc.show_overlay", {"text": "Test"})
        assert show_result["success"] is True

        hide_result = client.invoke_capability("pc.hide_overlay", {"overlay_id": "mock_overlay_001"})
        assert hide_result["success"] is True


# ═══════════════════════════════════════════════════════════════
# 4. Level 2 — Mouse Click (approval required)
# ═══════════════════════════════════════════════════════════════


class TestMouseClick:
    """pc.mouse_click — Level 2, requires approval."""

    def test_mouse_click_requires_approval(self):
        """Mouse click requires approval (Level 2)."""
        _, _, _, policy, _, _, client, approval_store = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("pc.mouse_click")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_mouse_click_blocked_without_approval(self):
        """Mouse click via ToolBroker is blocked without approval."""
        _, _, _, _, broker, _, client, _ = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("pc.mouse_click", {"x": 500, "y": 300})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

    def test_mouse_click_works_after_approval(self):
        """Mouse click works after user approval."""
        _, _, _, _, broker, _, client, approval_store = _setup_full_stack()
        client.register()

        # First attempt — needs approval
        result = broker.invoke_tool("pc.mouse_click", {"x": 500, "y": 300})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        # Approve
        approval_req = result.policy_result.approval_request
        assert approval_req is not None
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        # Register mock executor
        def mock_click(cap, params):
            return {"success": True, "x": params.get("x"), "y": params.get("y")}

        broker.register_mock("pc.mouse_click", mock_click)

        # Second attempt — approved
        result2 = broker.invoke_tool_approved("pc.mouse_click", {"x": 500, "y": 300})
        assert result2.success is True


# ═══════════════════════════════════════════════════════════════
# 5. Level 2 — Keyboard Type (approval required)
# ═══════════════════════════════════════════════════════════════


class TestKeyboardType:
    """pc.keyboard_type — Level 2, requires approval."""

    def test_keyboard_type_requires_approval(self):
        """Keyboard type requires approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("pc.keyboard_type")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_keyboard_type_blocked_without_approval(self):
        """Keyboard type is blocked without approval."""
        _, _, _, _, broker, _, client, _ = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("pc.keyboard_type", {"text": "Hello World"})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

    def test_keyboard_type_works_after_approval(self):
        """Keyboard type works after approval."""
        _, _, _, _, broker, _, client, approval_store = _setup_full_stack()
        client.register()

        result = broker.invoke_tool("pc.keyboard_type", {"text": "Hello"})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_type(cap, params):
            return {"success": True, "characters_typed": len(params.get("text", ""))}

        broker.register_mock("pc.keyboard_type", mock_type)

        result2 = broker.invoke_tool_approved("pc.keyboard_type", {"text": "Hello"})
        assert result2.success is True


# ═══════════════════════════════════════════════════════════════
# 6. Level 2 — File Write (approval + allowlist/denylist)
# ═══════════════════════════════════════════════════════════════


class TestFileWrite:
    """pc.write_file — Level 2, requires approval, path safety checks."""

    def test_write_file_requires_approval(self):
        """File write requires approval."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("pc.write_file")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_write_file_denylist_sensitive_path(self):
        """File write to sensitive path is denied by client."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "pc.write_file",
            {
                "path": "C:\\Users\\test\\.ssh\\authorized_keys",
                "content": "malicious key",
            },
        )
        assert "error" in result
        assert "denied" in result["error"].lower()

    def test_write_file_denylist_env(self):
        """File write to .env is denied."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "pc.write_file",
            {
                "path": "C:\\Users\\test\\.env",
                "content": "SECRET=abc123",
            },
        )
        assert "error" in result

    def test_write_file_denylist_pem(self):
        """File write to .pem is denied."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "pc.write_file",
            {
                "path": "C:\\Users\\test\\server.pem",
                "content": "-----BEGIN CERTIFICATE-----",
            },
        )
        assert "error" in result

    def test_write_file_allowlist_path(self):
        """File write to allowlist path is allowed (with approval)."""
        _, _, _, _, broker, _, client, approval_store = _setup_full_stack()
        client.register()

        # First attempt — needs approval
        result = broker.invoke_tool(
            "pc.write_file",
            {
                "path": "C:\\Users\\test\\workspace\\output.txt",
                "content": "Hello AEGIS",
            },
        )
        assert result.status == InvokeStatus.APPROVAL_NEEDED

    def test_write_file_works_after_approval(self):
        """File write works after approval for allowed path."""
        _, _, _, _, broker, _, client, approval_store = _setup_full_stack()
        client.register()

        result = broker.invoke_tool(
            "pc.write_file",
            {
                "path": "C:\\Users\\test\\workspace\\output.txt",
                "content": "Hello AEGIS",
            },
        )
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_write(cap, params):
            return {"success": True, "path": params.get("path"), "bytes_written": len(params.get("content", ""))}

        broker.register_mock("pc.write_file", mock_write)

        result2 = broker.invoke_tool_approved(
            "pc.write_file",
            {
                "path": "C:\\Users\\test\\workspace\\output.txt",
                "content": "Hello AEGIS",
            },
        )
        assert result2.success is True


# ═══════════════════════════════════════════════════════════════
# 7. File Read — Path Safety
# ═══════════════════════════════════════════════════════════════


class TestFileRead:
    """pc.read_file — Level 0, but path safety checks apply."""

    def test_read_file_allowed_for_normal_path(self):
        """Read file is allowed for normal paths."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("pc.read_file")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_read_file_denied_for_ssh(self):
        """Read file from .ssh is denied by client."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("pc.read_file", {"path": "C:\\Users\\test\\.ssh\\id_rsa"})
        assert "error" in result

    def test_read_file_denied_for_env(self):
        """Read file from .env is denied."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("pc.read_file", {"path": "C:\\Users\\test\\.env"})
        assert "error" in result

    def test_read_file_denied_for_credentials(self):
        """Read file from credentials.json is denied."""
        _, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("pc.read_file", {"path": "C:\\Users\\test\\credentials.json"})
        assert "error" in result


# ═══════════════════════════════════════════════════════════════
# 8. Dangerous Actions — Deny
# ═══════════════════════════════════════════════════════════════


class TestDangerousActions:
    """Dangerous PC actions are explicitly denied by PolicyEngine."""

    def test_delete_file_denied(self):
        """pc.delete_file is explicitly denied."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="pc.delete_file",
            name="Delete File",
            description="Delete a file permanently.",
            server_type=ServerType.PC,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_run_shell_denied(self):
        """pc.run_shell_command is explicitly denied."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="pc.run_shell_command",
            name="Run Shell",
            description="Execute arbitrary shell command.",
            server_type=ServerType.PC,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_type_password_denied(self):
        """pc.type_password is explicitly denied."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="pc.type_password",
            name="Type Password",
            description="Automatically type a password.",
            server_type=ServerType.PC,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_read_secret_file_denied(self):
        """pc.read_secret_file is explicitly denied."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="pc.read_secret_file",
            name="Read Secret",
            description="Read a secret file.",
            server_type=ServerType.PC,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_write_system_config_denied(self):
        """pc.write_system_config is explicitly denied."""
        _, _, _, policy, _, _, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="pc.write_system_config",
            name="Write System Config",
            description="Modify system configuration.",
            server_type=ServerType.PC,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY


# ═══════════════════════════════════════════════════════════════
# 9. Path Safety
# ═══════════════════════════════════════════════════════════════


class TestPathSafety:
    """File path allowlist/denylist checks."""

    def test_ssh_dir_denied(self):
        """Paths under .ssh are denied."""
        assert is_path_denied("C:\\Users\\test\\.ssh\\id_rsa") is True
        assert is_path_denied("/home/user/.ssh/authorized_keys") is True

    def test_aws_dir_denied(self):
        """Paths under .aws are denied."""
        assert is_path_denied("C:\\Users\\test\\.aws\\credentials") is True

    def test_env_file_denied(self):
        """Paths containing .env are denied."""
        assert is_path_denied("C:\\Users\\test\\.env") is True
        assert is_path_denied("C:\\Users\\test\\project\\.env") is True

    def test_pem_file_denied(self):
        """Paths containing .pem are denied."""
        assert is_path_denied("C:\\Users\\test\\server.pem") is True

    def test_credentials_json_denied(self):
        """Paths containing credentials are denied."""
        assert is_path_denied("C:\\Users\\test\\credentials.json") is True

    def test_normal_file_allowed(self):
        """Normal file paths are not denied."""
        assert is_path_denied("C:\\Users\\test\\workspace\\code.py") is False
        assert is_path_denied("C:\\Users\\test\\documents\\notes.txt") is False

    def test_workspace_in_allowlist(self):
        """Workspace paths are in allowlist."""
        assert is_path_allowed("C:\\Users\\test\\workspace\\code.py") is True
        assert is_path_allowed("C:\\Users\\test\\projects\\app\\main.py") is True

    def test_git_dir_denied(self):
        """Paths under .git are denied."""
        assert is_path_denied("C:\\Users\\test\\project\\.git\\config") is True


# ═══════════════════════════════════════════════════════════════
# 10. AuditLog
# ═══════════════════════════════════════════════════════════════


class TestAuditLog:
    """PC actions are recorded in AuditLog."""

    def test_action_recorded_in_audit(self):
        """Action execution is recorded in AuditLog."""
        _, _, _, _, _, audit, client, _ = _setup_full_stack()
        client.register()

        output = client.invoke_capability("pc.launch_app", {"app_path": "notepad.exe"})

        audit.log_decision(
            "pc_action_executed",
            "pc.launch_app",
            "SUCCESS",
            detail={"output": output},
        )

        recent = audit.list_recent(10)
        action_entries = [e for e in recent if e.action == "pc_action_executed"]
        assert len(action_entries) >= 1

    def test_denial_recorded_in_audit(self):
        """Policy denial is recorded in AuditLog."""
        _, _, _, policy, _, audit, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="pc.delete_file",
            name="Delete File",
            description="Delete a file.",
            server_type=ServerType.PC,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)

        audit.log_decision(
            "pc_action_denied",
            "pc.delete_file",
            result.decision.name,
            reason=result.reason,
        )

        recent = audit.list_recent(10)
        denied_entries = [e for e in recent if e.action == "pc_action_denied"]
        assert len(denied_entries) >= 1


# ═══════════════════════════════════════════════════════════════
# 11. EventBus — Action Result Events
# ═══════════════════════════════════════════════════════════════


class TestActionResultEvents:
    """PC action results are pushed to EventBus."""

    def test_action_result_event_pushed(self):
        """Successful action pushes result event."""
        bus, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        output = client.invoke_capability("pc.launch_app", {"app_path": "notepad.exe"})
        client.push_action_result_event("pc.launch_app", True, output)

        action_events = [e for e in received if e.event_type == "pc.action_result"]
        assert len(action_events) >= 1

        payload = json.loads(action_events[0].payload_json)
        assert payload["success"] is True
        assert payload["capability_id"] == "pc.launch_app"

    def test_failed_action_event_pushed(self):
        """Failed action pushes result event with error."""
        bus, _, _, _, _, _, client, _ = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_action_result_event("pc.mouse_click", False, error="Approval denied")

        action_events = [e for e in received if e.event_type == "pc.action_result"]
        assert len(action_events) >= 1

        payload = json.loads(action_events[0].payload_json)
        assert payload["success"] is False
        assert "denied" in payload["error"].lower()


# ═══════════════════════════════════════════════════════════════
# 12. Provider Unavailable
# ═══════════════════════════════════════════════════════════════


class TestProviderUnavailable:
    """Graceful failure when PC provider is unavailable."""

    def test_action_fails_when_unavailable(self):
        """Action returns error when provider is down."""
        provider = MockPCProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = PCServerClient(bus, registry, provider)

        result = client.invoke_capability("pc.launch_app", {"app_path": "notepad.exe"})
        assert "error" in result
        assert "not available" in result["error"]


# ═══════════════════════════════════════════════════════════════
# 13. Full E2E Flow
# ═══════════════════════════════════════════════════════════════


class TestFullE2EFlow:
    """Complete E2E: PC Action → ToolBroker → PolicyEngine → EventBus → AuditLog."""

    def test_full_flow_level1_action(self):
        """Full flow for Level 1 action (launch app)."""
        bus, engine, registry, policy, broker, audit, client, _ = _setup_full_stack()
        client.register()

        # Level 1 — auto-allowed
        cap = registry.get_capability("pc.launch_app")
        policy_result = policy.evaluate(cap)
        assert policy_result.decision == PolicyDecision.ALLOW

        # Execute
        def mock_launch(cap, params):
            return {"success": True, "pid": 12345}

        broker.register_mock("pc.launch_app", mock_launch)
        invoke_result = broker.invoke_tool("pc.launch_app", {"app_path": "notepad.exe"})
        assert invoke_result.success is True

        # Push event
        client.push_action_result_event("pc.launch_app", True, invoke_result.output)

        # Audit
        audit.log_decision("pc_action", "pc.launch_app", "SUCCESS")

        recent = audit.list_recent(10)
        assert any(e.action == "pc_action" for e in recent)

    def test_full_flow_level2_with_approval(self):
        """Full flow for Level 2 action (mouse click with approval)."""
        bus, engine, registry, policy, broker, audit, client, approval_store = _setup_full_stack()
        client.register()

        # Level 2 — needs approval
        result = broker.invoke_tool("pc.mouse_click", {"x": 500, "y": 300})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        # Approve
        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_click(cap, params):
            return {"success": True, "x": params.get("x"), "y": params.get("y")}

        broker.register_mock("pc.mouse_click", mock_click)

        result2 = broker.invoke_tool_approved("pc.mouse_click", {"x": 500, "y": 300})
        assert result2.success is True

        # Push event
        client.push_action_result_event("pc.mouse_click", True, result2.output)

        # Audit
        audit.log_decision("pc_action", "pc.mouse_click", "APPROVED_AND_EXECUTED")

    def test_full_flow_deny_dangerous(self):
        """Full flow for dangerous action (denied)."""
        bus, engine, registry, policy, broker, audit, client, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="pc.delete_file",
            name="Delete File",
            description="Delete a file.",
            server_type=ServerType.PC,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

        audit.log_decision("pc_action_denied", "pc.delete_file", "DENY", reason=result.reason)

        recent = audit.list_recent(10)
        assert any(e.action == "pc_action_denied" for e in recent)
