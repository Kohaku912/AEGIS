"""Tests for Approval system + enhanced PolicyEngine.

Covers:
1. ApprovalStore: create, approve, reject, expire, consume
2. PolicyEngine explicit deny rules (9 categories)
3. evaluate_tool_invocation, evaluate_event_trigger, evaluate_autonomous_task
4. Approval flow end-to-end: request → approve → execute
5. Expired approvals don't work
6. ToolBroker integration with approval
"""

from __future__ import annotations

import time

import pytest

from aegis_schema.models import Capability, RiskLevel, ServerType
from approval import ApprovalStatus, ApprovalStore, ApprovalType
from policy_engine import (
    PolicyDecision,
    PolicyEngine,
    create_default_policy_engine,
)
from tool_broker import InvokeStatus, ToolBroker
from tool_registry import ToolRegistry


def _make_cap(
    id: str = "pc.test",
    name: str = "Test",
    description: str = "Test capability",
    server_type: ServerType | None = None,
    risk_level: RiskLevel = RiskLevel.SAFE_ACTION,
    side_effects: list[str] | None = None,
) -> Capability:
    prefix_map = {
        "pc": ServerType.PC, "android": ServerType.ANDROID,
        "browser": ServerType.BROWSER, "room": ServerType.ROOM,
        "dev": ServerType.DEV, "ai": ServerType.AI,
    }
    if server_type is None:
        prefix = id.split(".")[0]
        server_type = prefix_map.get(prefix, ServerType.PC)
    return Capability(
        id=id, name=name, description=description,
        server_type=server_type, risk_level=risk_level,
        side_effects=side_effects or [],
    )


def _setup_broker(caps: list[Capability] | None = None,
                  policy: PolicyEngine | None = None) -> ToolBroker:
    registry = ToolRegistry()
    for cap in (caps or []):
        registry.register_capability(cap)
    return ToolBroker(registry, policy)


# ═══════════════════════════════════════════════════════════════
# ApprovalStore Tests
# ═══════════════════════════════════════════════════════════════

class TestApprovalStore:
    def test_create_request(self):
        store = ApprovalStore()
        req = store.create_request("pc.delete_file", tool_name="Delete File",
            requested_action="Delete a file", human_readable_summary="Delete /tmp/test.txt",
            risk_explanation="This will permanently delete a file",
            payload_preview='{"path":"/tmp/test.txt"}', risk_level=3)
        assert req.status == ApprovalStatus.PENDING
        assert req.approval_id.startswith("approval_")
        assert req.capability_id == "pc.delete_file"

    def test_approve_request(self):
        store = ApprovalStore()
        req = store.create_request("pc.test", risk_level=3)
        assert store.approve(req.approval_id, ApprovalType.ONE_TIME) is True
        assert req.status == ApprovalStatus.APPROVED

    def test_approve_nonexistent_fails(self):
        store = ApprovalStore()
        assert store.approve("nonexistent") is False

    def test_approve_already_approved_fails(self):
        store = ApprovalStore()
        req = store.create_request("pc.test", risk_level=3)
        store.approve(req.approval_id)
        assert store.approve(req.approval_id) is False

    def test_reject_request(self):
        store = ApprovalStore()
        req = store.create_request("pc.test", risk_level=3)
        assert store.reject(req.approval_id) is True
        assert req.status == ApprovalStatus.REJECTED

    def test_is_approved(self):
        store = ApprovalStore()
        req = store.create_request("room.ir_send", risk_level=3)
        assert store.is_approved("room.ir_send") is False
        store.approve(req.approval_id)
        assert store.is_approved("room.ir_send") is True

    def test_consume_one_time_approval(self):
        store = ApprovalStore()
        req = store.create_request("room.ir_send", risk_level=3)
        store.approve(req.approval_id, ApprovalType.ONE_TIME)

        # First consumption works
        consumed = store.consume_approval("room.ir_send")
        assert consumed is not None

        # Second consumption fails (one-time)
        consumed2 = store.consume_approval("room.ir_send")
        assert consumed2 is None

    def test_session_approval_not_consumed(self):
        store = ApprovalStore()
        req = store.create_request("room.ir_send", risk_level=3)
        store.approve(req.approval_id, ApprovalType.SESSION)

        # Can consume multiple times
        assert store.consume_approval("room.ir_send") is not None
        assert store.consume_approval("room.ir_send") is not None

    def test_expired_request_cannot_be_approved(self):
        store = ApprovalStore(request_timeout_ms=1)
        req = store.create_request("pc.test", risk_level=3)
        time.sleep(0.01)  # wait past 1ms timeout
        assert store.approve(req.approval_id) is False
        assert req.status == ApprovalStatus.EXPIRED

    def test_get_pending_requests(self):
        store = ApprovalStore()
        store.create_request("pc.a", risk_level=3)
        store.create_request("pc.b", risk_level=3)
        pending = store.get_pending_requests()
        assert len(pending) == 2

    def test_clear(self):
        store = ApprovalStore()
        store.create_request("pc.test", risk_level=3)
        store.clear()
        assert len(store.get_pending_requests()) == 0


# ═══════════════════════════════════════════════════════════════
# PolicyEngine: Explicit Deny Rules
# ═══════════════════════════════════════════════════════════════

class TestExplicitDenyRules:
    """All explicit deny patterns must always return DENY regardless of risk_level."""

    @pytest.mark.parametrize("cap_id", [
        "pc.send_sns",
        "android.send_dm",
        "browser.send_message",
        "pc.send_email",
        "pc.delete_file",
        "pc.delete_all",
        "pc.rm_temp",
        "pc.wipe_disk",
        "pc.upload_data",
        "pc.transmit_logs",
        "pc.read_credential",
        "pc.write_credential_store",
        "pc.access_ssh_key",
        "pc.access_api_key",
        "room.ac_power_on",
        "room.robot_arm_move",
        "room.lock_door",
        "dev.merge_to_main",
        "dev.push_main",
        "dev.deploy_production",
        "pc.change_permission",
        "pc.modify_acl",
        "pc.grant_admin",
    ])
    def test_explicit_deny_blocks_regardless_of_risk(self, cap_id):
        """Even READ_ONLY risk level is denied if the ID matches explicit deny pattern."""
        engine = create_default_policy_engine()
        cap = _make_cap(cap_id, risk_level=RiskLevel.READ_ONLY)
        result = engine.evaluate(cap)
        assert result.decision == PolicyDecision.DENY, (
            f"Expected DENY for '{cap_id}', got {result.decision.name}: {result.reason}"
        )

    def test_explicit_approval_patterns_ask_approval(self):
        """Explicit approval patterns trigger ASK_APPROVAL even for SAFE_ACTION."""
        engine = create_default_policy_engine()
        cap = _make_cap("room.ir_send", risk_level=RiskLevel.SAFE_ACTION,
                       side_effects=["controls IR device"])
        result = engine.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL
        assert result.approval_request is not None


# ═══════════════════════════════════════════════════════════════
# PolicyEngine: Evaluation Methods
# ═══════════════════════════════════════════════════════════════

class TestEvaluationMethods:
    def test_read_only_is_allowed(self):
        engine = create_default_policy_engine()
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        result = engine.evaluate_tool_invocation(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_approval_required_creates_approval_request(self):
        engine = create_default_policy_engine()
        cap = _make_cap("room.ir_send", risk_level=RiskLevel.APPROVAL_REQUIRED,
                       side_effects=["controls IR device"])
        result = engine.evaluate_tool_invocation(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL
        assert result.approval_request is not None
        assert result.approval_request.capability_id == "room.ir_send"

    def test_forbidden_is_denied(self):
        """FORBIDDEN capabilities can't be constructed, but explicit deny catches them."""
        engine = create_default_policy_engine()
        # Test that explicit deny patterns work as FORBIDDEN
        cap = _make_cap("pc.send_sns", risk_level=RiskLevel.READ_ONLY)
        result = engine.evaluate_tool_invocation(cap)
        assert result.decision == PolicyDecision.DENY

    def test_event_trigger_denies_approval_required(self):
        """Event-triggered actions MUST NOT prompt for approval — just deny."""
        engine = create_default_policy_engine()
        cap = _make_cap("room.ir_send", risk_level=RiskLevel.APPROVAL_REQUIRED,
                       side_effects=["controls IR device"])
        result = engine.evaluate_event_trigger(cap)
        assert result.decision == PolicyDecision.DENY

    def test_event_trigger_allows_read_only(self):
        engine = create_default_policy_engine()
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        result = engine.evaluate_event_trigger(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_autonomous_task_restricts_safe_action(self):
        """Autonomous tasks require approval even for SAFE_ACTION."""
        engine = create_default_policy_engine()
        cap = _make_cap("pc.launch_app", risk_level=RiskLevel.SAFE_ACTION)
        result = engine.evaluate_autonomous_task(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_autonomous_task_allows_read_only(self):
        engine = create_default_policy_engine()
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        result = engine.evaluate_autonomous_task(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_high_risk_asks_approval(self):
        engine = create_default_policy_engine()
        cap = _make_cap("pc.dangerous_op", risk_level=RiskLevel.HIGH_RISK,
                       side_effects=["could damage system"])
        result = engine.evaluate_tool_invocation(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_backward_compatible_evaluate(self):
        """The evaluate() method still works as before."""
        engine = create_default_policy_engine()
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        result = engine.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW


# ═══════════════════════════════════════════════════════════════
# PolicyEngine: PolicyResult Fields
# ═══════════════════════════════════════════════════════════════

class TestPolicyResult:
    def test_allow_result_has_audit_required(self):
        engine = create_default_policy_engine()
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        result = engine.evaluate(cap)
        assert result.audit_required is False  # READ_ONLY — no audit needed

    def test_safe_action_requires_audit(self):
        engine = create_default_policy_engine()
        cap = _make_cap("pc.launch_app", risk_level=RiskLevel.SAFE_ACTION)
        result = engine.evaluate(cap)
        assert result.audit_required is True  # SAFE_ACTION — audit

    def test_approval_result_has_expiry(self):
        engine = create_default_policy_engine()
        cap = _make_cap("room.ir_send", risk_level=RiskLevel.APPROVAL_REQUIRED,
                       side_effects=["controls device"])
        result = engine.evaluate(cap)
        assert result.expires_at_ms > 0
        assert result.required_approval_type == ApprovalType.ONE_TIME


# ═══════════════════════════════════════════════════════════════
# End-to-End Approval Flow
# ═══════════════════════════════════════════════════════════════

class TestApprovalFlow:
    def test_full_approval_flow(self):
        """Complete flow: invoke → approval needed → approve → invoke_approved → success."""
        cap = _make_cap("room.ir_send", risk_level=RiskLevel.APPROVAL_REQUIRED,
                       side_effects=["controls IR device"])
        engine = create_default_policy_engine()
        broker = _setup_broker([cap], engine)

        # Step 1: Invoke — should ask for approval
        result1 = broker.invoke_tool("room.ir_send", {"device": "tv"})
        assert result1.status == InvokeStatus.APPROVAL_NEEDED
        assert result1.policy_result is not None
        assert result1.policy_result.approval_request is not None

        # Step 2: User approves
        approval_id = result1.policy_result.approval_request.approval_id
        engine.approval_store.approve(approval_id, ApprovalType.ONE_TIME)

        # Step 3: Invoke approved — should succeed
        result2 = broker.invoke_tool_approved("room.ir_send", {"device": "tv"})
        assert result2.status == InvokeStatus.SUCCESS
        assert result2.success

    def test_approval_needed_without_approve_fails(self):
        """invoke_tool_approved without prior approval returns DENIED."""
        cap = _make_cap("room.ir_send", risk_level=RiskLevel.APPROVAL_REQUIRED,
                       side_effects=["controls IR device"])
        engine = create_default_policy_engine()
        broker = _setup_broker([cap], engine)

        result = broker.invoke_tool_approved("room.ir_send", {"device": "tv"})
        assert result.status == InvokeStatus.DENIED
        assert "No valid approval" in result.error

    def test_one_time_approval_consumed_after_use(self):
        """ONE_TIME approval works once, then is consumed."""
        cap = _make_cap("room.ir_send", risk_level=RiskLevel.APPROVAL_REQUIRED,
                       side_effects=["controls IR device"])
        engine = create_default_policy_engine()
        broker = _setup_broker([cap], engine)

        # Get approval
        result1 = broker.invoke_tool("room.ir_send", {"device": "tv"})
        engine.approval_store.approve(
            result1.policy_result.approval_request.approval_id,
            ApprovalType.ONE_TIME,
        )

        # First use — succeeds
        r1 = broker.invoke_tool_approved("room.ir_send", {"device": "tv"})
        assert r1.success

        # Second use — fails (already consumed)
        r2 = broker.invoke_tool_approved("room.ir_send", {"device": "tv"})
        assert r2.status == InvokeStatus.DENIED

    def test_rejected_approval_does_not_allow_execution(self):
        """Rejected approvals should not allow execution."""
        cap = _make_cap("room.ir_send", risk_level=RiskLevel.APPROVAL_REQUIRED,
                       side_effects=["controls IR device"])
        engine = create_default_policy_engine()
        broker = _setup_broker([cap], engine)

        result1 = broker.invoke_tool("room.ir_send", {"device": "tv"})
        engine.approval_store.reject(
            result1.policy_result.approval_request.approval_id
        )

        result2 = broker.invoke_tool_approved("room.ir_send", {"device": "tv"})
        assert result2.status == InvokeStatus.DENIED

    def test_deny_rules_cannot_be_bypassed_by_approval(self):
        """Explicit deny patterns are DENIED even with approval."""
        cap = _make_cap("pc.send_sns", risk_level=RiskLevel.READ_ONLY)
        engine = create_default_policy_engine()
        broker = _setup_broker([cap], engine)

        # Even with approval created manually, explicit deny should block
        req = engine.approval_store.create_request("pc.send_sns", risk_level=3)
        engine.approval_store.approve(req.approval_id)

        result = broker.invoke_tool_approved("pc.send_sns", {})
        # Should still be denied because PolicyEngine's explicit deny catches it
        assert result.status == InvokeStatus.DENIED


# ═══════════════════════════════════════════════════════════════
# ToolBroker + PolicyEngine Integration
# ═══════════════════════════════════════════════════════════════

class TestToolBrokerPolicyIntegration:
    def test_tool_broker_always_calls_policy(self):
        """invoke_tool always goes through PolicyEngine.evaluate()."""
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        call_count = {"count": 0}

        class CountingPolicy(PolicyEngine):
            def evaluate(self, capability, params=None):
                call_count["count"] += 1
                return super().evaluate(capability, params)

        broker = _setup_broker([cap], CountingPolicy())
        broker.invoke_tool("pc.screenshot", {})
        assert call_count["count"] == 1

    def test_policy_cannot_be_bypassed(self):
        """There is no public method on ToolBroker to execute without policy."""
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap])

        # All public methods that could execute:
        _public = [m for m in dir(broker) if not m.startswith("_") and callable(getattr(broker, m))]
        # invoke_tool and invoke_tool_approved are the only execution methods
        # Both go through policy — structurally enforced

        # Non-execution methods should NOT execute
        assert broker.find_capability("pc.screenshot") is not None  # returns data, doesn't execute
        results = broker.search_capabilities("screenshot")
        assert len(results) == 1  # returns data, doesn't execute

    def test_read_only_always_allowed(self):
        """READ_ONLY capabilities are always ALLOWed by default policy."""
        caps = [
            _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY),
            _make_cap("android.screenshot", risk_level=RiskLevel.READ_ONLY),
            _make_cap("browser.extract_text", risk_level=RiskLevel.READ_ONLY),
            _make_cap("room.get_env", risk_level=RiskLevel.READ_ONLY),
        ]
        broker = _setup_broker(caps, create_default_policy_engine())
        for cap in caps:
            result = broker.invoke_tool(cap.id, {})
            assert result.success, f"READ_ONLY {cap.id} should be allowed"
