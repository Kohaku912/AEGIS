"""Tests for ToolBroker + PolicyEngine integration.

Key test scenarios:
1. Basic invocation of registered capabilities
2. Policy enforcement — denied capabilities are blocked
3. Approval-required flow
4. Mock executor registration and execution
5. Structural enforcement — no bypass possible
"""

from __future__ import annotations

from typing import Any

import pytest

from aegis_schema.models import Capability, RiskLevel, ServerInfo, ServerType
from policy_engine import (
    PolicyDecision,
    PolicyEngine,
    PolicyResult,
    create_default_policy_engine,
)
from tool_broker import InvokeStatus, ToolBroker
from tool_registry import ToolRegistry

# ── Helpers ───────────────────────────────────────────────────

_ID_TO_SERVER: dict[str, ServerType] = {
    "pc": ServerType.PC,
    "android": ServerType.ANDROID,
    "browser": ServerType.BROWSER,
    "room": ServerType.ROOM,
    "dev": ServerType.DEV,
    "ai": ServerType.AI,
}


def _make_cap(
    id: str = "pc.test",
    name: str = "Test",
    description: str = "Test capability",
    server_type: ServerType | None = None,
    risk_level: RiskLevel = RiskLevel.SAFE_ACTION,
) -> Capability:
    """Create a Capability for testing. Auto-detects server_type from ID prefix."""
    if server_type is None:
        prefix = id.split(".")[0]
        server_type = _ID_TO_SERVER.get(prefix, ServerType.PC)
    return Capability(
        id=id,
        name=name,
        description=description,
        server_type=server_type,
        risk_level=risk_level,
    )


def _setup_broker(
    caps: list[Capability] | None = None,
    policy: PolicyEngine | None = None,
) -> ToolBroker:
    """Create a ToolBroker with a fresh registry and given capabilities."""
    registry = ToolRegistry()
    for cap in (caps or []):
        registry.register_capability(cap)
    return ToolBroker(registry, policy)


# ═══════════════════════════════════════════════════════════════
# Basic Invocation Tests
# ═══════════════════════════════════════════════════════════════

class TestBasicInvocation:
    def test_invoke_read_only_succeeds(self):
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap])
        result = broker.invoke_tool("pc.screenshot", {"display": 0})
        assert result.success
        assert result.status == InvokeStatus.SUCCESS
        assert result.output["mock"] is True

    def test_invoke_safe_action_succeeds(self):
        cap = _make_cap("pc.launch_app", risk_level=RiskLevel.SAFE_ACTION)
        broker = _setup_broker([cap])
        result = broker.invoke_tool("pc.launch_app", {"app_path": "notepad.exe"})
        assert result.success

    def test_invoke_nonexistent_fails(self):
        broker = _setup_broker([])
        result = broker.invoke_tool("nonexistent.cap", {})
        assert result.status == InvokeStatus.NOT_FOUND
        assert "not registered" in result.error.lower()

    def test_invoke_returns_params_in_output(self):
        cap = _make_cap("pc.test", risk_level=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap])
        result = broker.invoke_tool("pc.test", {"key": "value"})
        assert result.output["params_received"] == {"key": "value"}

    def test_invoke_returns_invocation_id(self):
        cap = _make_cap("pc.test", risk_level=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap])
        result = broker.invoke_tool("pc.test", {})
        assert result.invocation_id != ""

    def test_invoke_returns_duration(self):
        cap = _make_cap("pc.test", risk_level=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap])
        result = broker.invoke_tool("pc.test", {})
        assert result.duration_ms >= 0


# ═══════════════════════════════════════════════════════════════
# Policy Enforcement Tests
# ═══════════════════════════════════════════════════════════════

class TestPolicyEnforcement:
    def test_forbidden_capability_denied(self):
        """FORBIDDEN capabilities are denied even if registered."""
        # Can't register FORBIDDEN, but PolicyEngine can block after registration
        cap = _make_cap("pc.sensitive", risk_level=RiskLevel.READ_ONLY)
        policy = create_default_policy_engine()
        policy.block_capability("pc.sensitive")
        broker = _setup_broker([cap], policy)
        result = broker.invoke_tool("pc.sensitive", {})
        assert result.status == InvokeStatus.DENIED

    def test_high_risk_requires_approval(self):
        cap = _make_cap("pc.dangerous", risk_level=RiskLevel.HIGH_RISK)
        broker = _setup_broker([cap])
        result = broker.invoke_tool("pc.dangerous", {})
        assert result.status == InvokeStatus.APPROVAL_NEEDED
        assert result.policy_result is not None
        assert result.policy_result.decision == PolicyDecision.ASK_APPROVAL

    def test_approval_required_asks_approval(self):
        cap = _make_cap("room.ir_send", risk_level=RiskLevel.APPROVAL_REQUIRED)
        broker = _setup_broker([cap])
        result = broker.invoke_tool("room.ir_send", {})
        assert result.status == InvokeStatus.APPROVAL_NEEDED
        assert result.policy_result is not None
        assert result.policy_result.decision == PolicyDecision.ASK_APPROVAL

    def test_blocked_pattern_denied(self):
        cap = _make_cap("pc.delete_all", risk_level=RiskLevel.SAFE_ACTION)
        policy = create_default_policy_engine()
        # Default policy blocks *.delete_all
        broker = _setup_broker([cap], policy)
        result = broker.invoke_tool("pc.delete_all", {})
        assert result.status == InvokeStatus.DENIED

    def test_custom_rule_can_allow(self):
        cap = _make_cap("pc.special", risk_level=RiskLevel.APPROVAL_REQUIRED)
        policy = create_default_policy_engine()

        # Add a rule that allows this specific capability
        def allow_special(c: Capability, p: dict[str, Any]) -> PolicyResult | None:
            if c.id == "pc.special" and p.get("token") == "allow-me":
                return PolicyResult(
                    decision=PolicyDecision.ALLOW,
                    reason="Custom rule allowed it.",
                    capability_id=c.id,
                    risk_level=c.risk_level,
                )
            return None

        policy.add_rule("pc.special", allow_special)
        broker = _setup_broker([cap], policy)

        # Without the magic token — approval needed
        result1 = broker.invoke_tool("pc.special", {})
        assert result1.status == InvokeStatus.APPROVAL_NEEDED

        # With the magic token — allowed
        result2 = broker.invoke_tool("pc.special", {"token": "allow-me"})
        assert result2.status == InvokeStatus.SUCCESS

    def test_risk_override(self):
        """Risk override can raise (but not lower) risk level."""
        cap = _make_cap("pc.test", risk_level=RiskLevel.READ_ONLY)
        policy = create_default_policy_engine()
        # Override to higher risk
        policy.set_risk_override("pc.test", RiskLevel.APPROVAL_REQUIRED)
        broker = _setup_broker([cap], policy)
        result = broker.invoke_tool("pc.test", {})
        assert result.status == InvokeStatus.APPROVAL_NEEDED


# ═══════════════════════════════════════════════════════════════
# Mock Executor Tests
# ═══════════════════════════════════════════════════════════════

class TestMockExecutor:
    def test_custom_mock_executor(self):
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap])

        def screenshot_mock(c: Capability, p: dict[str, Any]) -> dict[str, Any]:
            return {"image_base64": "fake-base64-data", "width": 1920, "height": 1080}

        broker.register_mock("pc.screenshot", screenshot_mock)
        result = broker.invoke_tool("pc.screenshot", {})
        assert result.success
        assert result.output["image_base64"] == "fake-base64-data"
        assert result.output["width"] == 1920

    def test_mock_by_prefix(self):
        caps = [
            _make_cap("pc.action1", risk_level=RiskLevel.SAFE_ACTION),
            _make_cap("pc.action2", risk_level=RiskLevel.SAFE_ACTION),
        ]
        broker = _setup_broker(caps)

        call_count = {"count": 0}

        def pc_executor(c: Capability, p: dict[str, Any]) -> dict[str, Any]:
            call_count["count"] += 1
            return {"executed": c.id}

        broker.register_mock("pc.", pc_executor)

        r1 = broker.invoke_tool("pc.action1", {})
        r2 = broker.invoke_tool("pc.action2", {})
        assert r1.success and r2.success
        assert call_count["count"] == 2
        assert r1.output["executed"] == "pc.action1"

    def test_default_mock_fallback(self):
        cap = _make_cap("pc.unknown", risk_level=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap])
        result = broker.invoke_tool("pc.unknown", {})
        assert result.success
        assert result.output["mock"] is True
        assert "Mock execution" in result.output["message"]

    def test_mock_executor_error_caught(self):
        cap = _make_cap("pc.broken", risk_level=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap])

        def broken_executor(c: Capability, p: dict[str, Any]) -> dict[str, Any]:
            raise RuntimeError("Simulated executor failure")

        broker.register_mock("pc.broken", broken_executor)
        result = broker.invoke_tool("pc.broken", {})
        assert result.status == InvokeStatus.EXECUTION_ERROR
        assert "Simulated executor failure" in result.error


# ═══════════════════════════════════════════════════════════════
# Structural Enforcement Tests
# ═══════════════════════════════════════════════════════════════

class TestStructuralEnforcement:
    """Ensure ToolBroker cannot be bypassed."""

    def test_invoke_tool_always_checks_policy(self):
        """Even safe capabilities go through policy evaluation."""
        cap = _make_cap("pc.test", risk_level=RiskLevel.READ_ONLY)
        evaluation_log = []

        class LoggingPolicy(PolicyEngine):
            def evaluate(self, capability, params=None):
                evaluation_log.append(capability.id)
                return super().evaluate(capability, params)

        policy = LoggingPolicy()
        broker = _setup_broker([cap], policy)
        broker.invoke_tool("pc.test", {})
        assert "pc.test" in evaluation_log

    def test_invoke_tool_approved_still_checks_policy(self):
        """Even invoke_tool_approved re-evaluates policy after approval check."""
        cap = _make_cap("pc.test", risk_level=RiskLevel.READ_ONLY)
        evaluation_log = []

        class LoggingPolicy(PolicyEngine):
            def evaluate(self, capability, params=None):
                evaluation_log.append(("approved_path", capability.id))
                return super().evaluate(capability, params)

        policy = LoggingPolicy()
        broker = _setup_broker([cap], policy)

        # Set up approval so the flow reaches policy evaluation
        policy.approval_store.create_request("pc.test", risk_level=1)
        pending = policy.approval_store.get_pending_requests()
        policy.approval_store.approve(pending[0].approval_id)

        broker.invoke_tool_approved("pc.test", {})
        assert len(evaluation_log) == 1
        assert evaluation_log[0] == ("approved_path", "pc.test")

    def test_no_public_executor_access(self):
        """ToolBroker._invoke_internal and _mock_executors are private."""
        broker = _setup_broker([])
        # Verify no public method exists to execute without policy check
        # Note: 'execute' is the new primary entry point that always calls PolicyEngine
        public_methods = [m for m in dir(broker) if not m.startswith("_")]
        execution_methods = [m for m in public_methods if "execut" in m.lower()]
        # Allow 'execute' as it's the new primary entry point with mandatory policy check
        allowed_methods = {"execute", "execute_approved"}
        forbidden_methods = [m for m in execution_methods if m not in allowed_methods]
        assert forbidden_methods == [], (
            f"Found forbidden execution methods: {forbidden_methods}. "
            "All execution must go through execute, invoke_tool, or invoke_tool_approved."
        )

    def test_direct_registry_access_does_not_execute(self):
        """ToolRegistry only stores data — it cannot execute."""
        reg = ToolRegistry()
        cap = _make_cap("pc.test", risk_level=RiskLevel.READ_ONLY)
        reg.register_capability(cap)

        # Registry exposes data, not execution
        assert reg.get_capability("pc.test") is not None
        assert not hasattr(reg, "execute")
        assert not hasattr(reg, "invoke")


# ═══════════════════════════════════════════════════════════════
# Search via Broker Tests
# ═══════════════════════════════════════════════════════════════

class TestSearchViaBroker:
    @pytest.fixture
    def broker(self) -> ToolBroker:
        caps = [
            _make_cap("pc.screenshot", "Screenshot", "Take display screenshot", ServerType.PC, RiskLevel.READ_ONLY),
            _make_cap("pc.launch_app", "Launch App", "Launch application", ServerType.PC, RiskLevel.SAFE_ACTION),
            _make_cap("browser.open_page", "Open Page", "Navigate to URL", ServerType.BROWSER, RiskLevel.SAFE_ACTION),
            _make_cap("room.get_env", "Get Environment", "Read sensors", ServerType.ROOM, RiskLevel.READ_ONLY),
        ]
        return _setup_broker(caps)

    def test_search_finds_capabilities(self, broker):
        results = broker.search_capabilities("screenshot")
        assert len(results) == 1
        assert results[0].id == "pc.screenshot"

    def test_list_safe_capabilities(self, broker):
        safe = broker.list_safe_capabilities()
        # 2 READ_ONLY (pc.screenshot, room.get_env) + 2 SAFE_ACTION (pc.mouse_click, browser.open_page)
        assert len(safe) == 4

    def test_find_capability_does_not_execute(self, broker):
        """find_capability returns data, does not invoke."""
        cap = broker.find_capability("pc.screenshot")
        assert cap is not None
        assert isinstance(cap, Capability)
        # This is a lookup, not an invocation — no policy check occurs


# ═══════════════════════════════════════════════════════════════
# Integration: Registry + Broker + Policy
# ═══════════════════════════════════════════════════════════════

class TestIntegration:
    def test_full_flow_register_and_invoke(self):
        """End-to-end: register capability, invoke, get result."""
        registry = ToolRegistry()
        policy = create_default_policy_engine()
        broker = ToolBroker(registry, policy)

        # Server comes online
        server = ServerInfo(
            server_id="pc-main",
            server_type=ServerType.PC,
            capability_ids=["pc.screenshot", "pc.mouse_click"],
        )
        registry.register_server(server)

        # Server registers capabilities
        registry.register_capability(
            Capability(
                id="pc.screenshot",
                name="Screenshot",
                description="Take a screenshot",
                server_type=ServerType.PC,
                risk_level=RiskLevel.READ_ONLY,
                tags=["observe", "risk:read_only"],
            )
        )
        registry.register_capability(
            Capability(
                id="pc.mouse_click",
                name="Mouse Click",
                description="Click at coordinates",
                server_type=ServerType.PC,
                risk_level=RiskLevel.SAFE_ACTION,
                tags=["input", "risk:safe_action"],
            )
        )

        # Planner searches for screenshot tools
        tools = registry.search("screenshot")
        assert len(tools) == 1

        # Invoke the tool
        result = broker.invoke_tool("pc.screenshot", {"display": 0})
        assert result.success
        assert result.output["mock"] is True

    def test_approval_required_tool_blocked_until_approved(self):
        """APPROVAL_REQUIRED tool returns ASK_APPROVAL, not SUCCESS.

        invoke_tool_approved re-evaluates policy — without policy state change,
        it still returns APPROVAL_NEEDED (correct behavior: mere method call
        doesn't bypass the PolicyEngine).
        """
        registry = ToolRegistry()
        policy = create_default_policy_engine()
        broker = ToolBroker(registry, policy)

        cap = Capability(
            id="room.ir_send",
            name="Send IR",
            description="Send infrared signal",
            server_type=ServerType.ROOM,
            risk_level=RiskLevel.APPROVAL_REQUIRED,
            requires_approval=True,
            side_effects=["controls physical device"],
            tags=["ir", "risk:approval_required"],
        )
        registry.register_capability(cap)

        # Without approval — approval needed
        result1 = broker.invoke_tool("room.ir_send", {"device": "tv"})
        assert result1.status == InvokeStatus.APPROVAL_NEEDED
        assert not result1.success

        # invoke_tool_approved also goes through policy — still denied
        # (policy state hasn't changed — this is correct structural enforcement)
        result2 = broker.invoke_tool_approved("room.ir_send", {"device": "tv"})
        assert result2.status == InvokeStatus.DENIED
        # Correct: invoke_tool_approved requires prior policy state change;
        # a mere method call doesn't bypass the PolicyEngine.

    def test_multiple_server_types(self):
        """Capabilities from different servers coexist."""
        registry = ToolRegistry()
        policy = create_default_policy_engine()
        broker = ToolBroker(registry, policy)

        for cap_data in [
            ("pc.screenshot", ServerType.PC, RiskLevel.READ_ONLY),
            ("android.screenshot", ServerType.ANDROID, RiskLevel.READ_ONLY),
            ("browser.open_page", ServerType.BROWSER, RiskLevel.SAFE_ACTION),
            ("room.get_env", ServerType.ROOM, RiskLevel.READ_ONLY),
            ("dev.run_tests", ServerType.DEV, RiskLevel.SAFE_ACTION),
        ]:
            registry.register_capability(Capability(
                id=cap_data[0],
                name=cap_data[0],
                description=f"Capability {cap_data[0]}",
                server_type=cap_data[1],
                risk_level=cap_data[2],
            ))

        # Each should be invocable
        for cap_id in ["pc.screenshot", "android.screenshot", "browser.open_page", "room.get_env", "dev.run_tests"]:
            result = broker.invoke_tool(cap_id, {})
            assert result.success, f"Failed to invoke {cap_id}: {result.error}"

    def test_policy_engine_is_conservative_by_default(self):
        """Default policy: HIGH_RISK and APPROVAL_REQUIRED need approval, FORBIDDEN is denied."""
        registry = ToolRegistry()
        policy = create_default_policy_engine()
        broker = ToolBroker(registry, policy)

        for risk, expected_status in [
            (RiskLevel.READ_ONLY, InvokeStatus.SUCCESS),
            (RiskLevel.SAFE_ACTION, InvokeStatus.SUCCESS),
            (RiskLevel.APPROVAL_REQUIRED, InvokeStatus.APPROVAL_NEEDED),
            (RiskLevel.HIGH_RISK, InvokeStatus.APPROVAL_NEEDED),
        ]:
            cap = Capability(
                id=f"pc.test_{risk.name.lower()}",
                name=f"Test {risk.name}",
                description=f"Capability at {risk.name}",
                server_type=ServerType.PC,
                risk_level=risk,
            )
            registry.register_capability(cap)
            result = broker.invoke_tool(cap.id, {})
            assert result.status == expected_status, (
                f"Expected {expected_status} for {risk.name}, got {result.status}: {result.error}"
            )


# ═══════════════════════════════════════════════════════════════
# PolicyEngine Unit Tests
# ═══════════════════════════════════════════════════════════════

class TestPolicyEngine:
    def test_default_allow_read_only(self):
        engine = PolicyEngine()
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        result = engine.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_default_allow_safe_action(self):
        engine = PolicyEngine()
        cap = _make_cap("pc.launch_app", risk_level=RiskLevel.SAFE_ACTION)
        result = engine.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_default_ask_approval(self):
        engine = PolicyEngine()
        cap = _make_cap("pc.delete", risk_level=RiskLevel.APPROVAL_REQUIRED)
        result = engine.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_default_deny_forbidden(self):
        """FORBIDDEN capabilities cannot be constructed by Pydantic.
        This is the first line of defense — structural prevention."""
        with pytest.raises(ValueError, match="FORBIDDEN"):
            _make_cap("pc.purchase", risk_level=RiskLevel.FORBIDDEN)

    def test_default_deny_unspecified(self):
        """UNSPECIFIED capabilities cannot be constructed by Pydantic.
        This is the first line of defense — structural prevention."""
        with pytest.raises(ValueError, match="UNSPECIFIED"):
            _make_cap("pc.unknown", risk_level=RiskLevel.UNSPECIFIED)

    def test_blocked_capability_denied(self):
        engine = PolicyEngine()
        engine.block_capability("pc.screenshot")
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        result = engine.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_blocked_pattern_denied(self):
        engine = PolicyEngine()
        engine.block_pattern(r"pc\.delete.*")
        cap = _make_cap("pc.delete_temp", risk_level=RiskLevel.SAFE_ACTION)
        result = engine.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_global_rule(self):
        engine = PolicyEngine()

        def block_temp_files(c: Capability, p: dict[str, Any]) -> PolicyResult | None:
            if "temp" in c.id:
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason="No temp file operations allowed.",
                    capability_id=c.id,
                    risk_level=c.risk_level,
                )
            return None

        engine.add_global_rule(block_temp_files)
        cap = _make_cap("pc.temp_clean", risk_level=RiskLevel.SAFE_ACTION)
        result = engine.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_default_policy_blocks_dangerous_patterns(self):
        engine = create_default_policy_engine()

        dangerous_ids = [
            "pc.delete_all",
            "pc.rm_rf",
            "browser.purchase_item",
            "android.send_sns",
        ]
        for cap_id in dangerous_ids:
            cap = _make_cap(cap_id, risk_level=RiskLevel.READ_ONLY)  # even low risk
            result = engine.evaluate(cap)
            assert result.decision == PolicyDecision.DENY, (
                f"Expected DENY for '{cap_id}', got {result.decision.name}"
            )
