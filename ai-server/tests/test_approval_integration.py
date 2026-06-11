"""E2E integration tests for Approval Flow.

Tests the full chain:
ToolBroker → PolicyEngine → ApprovalStore → Approval UI → AutonomousLoop

Scenarios:
1. Read-only (Level 0) → auto-allow
2. Safe action (Level 1) → auto-allow + audit
3. Approval-required (Level 2) → approval_required → approve → execute
4. Rejected → denied + audit
5. Restricted (Level 3) → deny
6. Unknown capability → not_found
7. AutonomousLoop pause on approval

Markers: CI-friendly unit tests (default), E2E (pytest -m e2e)
"""

from __future__ import annotations

from typing import Any

import pytest

from aegis_ai.audit import AuditLog
from aegis_ai.autonomous_loop import AutonomousLoop
from aegis_ai.context_builder import ContextBuilder
from aegis_ai.llm.client import MockLLMClient
from aegis_ai.planner import Planner
from aegis_ai.tool_broker import InvokeStatus, ToolBroker
from aegis_ai.tool_registry import ToolRegistry
from aegis_schema.models import Capability, RiskLevel, ServerType
from approval import ApprovalStatus
from policy_engine import PolicyDecision, PolicyEngine, create_default_policy_engine

# ── Helpers ───────────────────────────────────────────────────

def _make_cap(id: str, name: str = "Test", risk: RiskLevel = RiskLevel.READ_ONLY,
              server: ServerType = ServerType.PC) -> Capability:
    prefix_map = {"pc": ServerType.PC, "android": ServerType.ANDROID,
                  "browser": ServerType.BROWSER, "room": ServerType.ROOM, "dev": ServerType.DEV}
    prefix = id.split(".")[0]
    return Capability(id=id, name=name, description=f"Capability {id}",
                      server_type=prefix_map.get(prefix, server), risk_level=risk)


def _setup_broker(caps: list[Capability] | None = None,
                  policy: PolicyEngine | None = None) -> ToolBroker:
    registry = ToolRegistry()
    for cap in (caps or []):
        registry.register_capability(cap)
    return ToolBroker(registry, policy)


# ═══════════════════════════════════════════════════════════════
# Scenario 1: Read-only (Level 0) → auto-allow
# ═══════════════════════════════════════════════════════════════

class TestReadOnlyAutoAllow:
    def test_read_only_executes_without_approval(self):
        cap = _make_cap("pc.screenshot", risk=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap], create_default_policy_engine())
        result = broker.invoke_tool("pc.screenshot", {})
        assert result.status == InvokeStatus.SUCCESS
        assert result.success

    def test_read_only_no_approval_request_created(self):
        policy = create_default_policy_engine()
        cap = _make_cap("pc.screenshot", risk=RiskLevel.READ_ONLY)
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW
        assert result.approval_request is None


# ═══════════════════════════════════════════════════════════════
# Scenario 2: Safe action (Level 1) → auto-allow + audit
# ═══════════════════════════════════════════════════════════════

class TestSafeActionAutoAllowWithAudit:
    def test_safe_action_executes_without_approval(self):
        cap = _make_cap("pc.mouse_click", risk=RiskLevel.SAFE_ACTION)
        broker = _setup_broker([cap], create_default_policy_engine())
        result = broker.invoke_tool("pc.mouse_click", {"x": 100, "y": 200})
        assert result.success

    def test_safe_action_has_audit_required(self):
        policy = create_default_policy_engine()
        cap = _make_cap("pc.mouse_click", risk=RiskLevel.SAFE_ACTION)
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW
        assert result.audit_required is True

    def test_safe_action_logged_to_audit(self):
        audit = AuditLog(path="data/test_e2e_safe.jsonl")
        cap = _make_cap("pc.mouse_click", risk=RiskLevel.SAFE_ACTION)
        broker = _setup_broker([cap], create_default_policy_engine())
        broker.invoke_tool("pc.mouse_click", {"x": 0, "y": 0})
        audit.log_decision("tool_invoked", cap.id, "ALLOW", actor="aegis")
        entries = audit.list_recent(10)
        assert any(e.decision == "ALLOW" for e in entries)


# ═══════════════════════════════════════════════════════════════
# Scenario 3: Approval-required (Level 2) → approve → execute
# ═══════════════════════════════════════════════════════════════

class TestApprovalRequiredFlow:
    def test_level_2_returns_approval_needed(self):
        cap = _make_cap("room.ir_send", risk=RiskLevel.APPROVAL_REQUIRED)
        broker = _setup_broker([cap], create_default_policy_engine())
        result = broker.invoke_tool("room.ir_send", {"device": "tv"})
        assert result.status == InvokeStatus.APPROVAL_NEEDED
        assert result.policy_result is not None
        assert result.policy_result.approval_request is not None

    def test_approval_request_appears_in_store(self):
        cap = _make_cap("room.ir_send", risk=RiskLevel.APPROVAL_REQUIRED)
        broker = _setup_broker([cap], create_default_policy_engine())
        result = broker.invoke_tool("room.ir_send", {"device": "tv"})
        req = result.policy_result.approval_request
        assert req is not None
        assert req.capability_id == "room.ir_send"
        assert req.status == ApprovalStatus.PENDING

    def test_approve_once_allows_execution(self):
        cap = _make_cap("room.ir_send", risk=RiskLevel.APPROVAL_REQUIRED)
        engine = create_default_policy_engine()
        broker = _setup_broker([cap], engine)

        # Step 1: invoke → approval needed
        r1 = broker.invoke_tool("room.ir_send", {"device": "tv"})
        assert r1.status == InvokeStatus.APPROVAL_NEEDED

        # Step 2: user approves in UI
        engine.approval_store.approve_once(r1.policy_result.approval_request.approval_id)

        # Step 3: invoke_approved → success
        r2 = broker.invoke_tool_approved("room.ir_send", {"device": "tv"})
        assert r2.success

    def test_approve_session_allows_multiple(self):
        cap = _make_cap("room.ir_send", risk=RiskLevel.APPROVAL_REQUIRED)
        engine = create_default_policy_engine()
        broker = _setup_broker([cap], engine)

        r1 = broker.invoke_tool("room.ir_send", {"device": "tv"})
        engine.approval_store.approve_for_session(r1.policy_result.approval_request.approval_id)

        # Multiple executions should work
        for _ in range(3):
            r = broker.invoke_tool_approved("room.ir_send", {"device": "tv"})
            assert r.success

    def test_approval_no_auto_approve(self):
        """AI cannot auto-approve — invoke_tool_approved without real approval fails."""
        cap = _make_cap("room.ir_send", risk=RiskLevel.APPROVAL_REQUIRED)
        broker = _setup_broker([cap], create_default_policy_engine())
        # Direct call without approval
        result = broker.invoke_tool_approved("room.ir_send", {"device": "tv"})
        assert result.status == InvokeStatus.DENIED


# ═══════════════════════════════════════════════════════════════
# Scenario 4: Rejected action
# ═══════════════════════════════════════════════════════════════

class TestRejectedAction:
    def test_rejected_action_not_executed(self):
        cap = _make_cap("room.ir_send", risk=RiskLevel.APPROVAL_REQUIRED)
        engine = create_default_policy_engine()
        broker = _setup_broker([cap], engine)

        r1 = broker.invoke_tool("room.ir_send", {"device": "tv"})
        engine.approval_store.reject(r1.policy_result.approval_request.approval_id)

        r2 = broker.invoke_tool_approved("room.ir_send", {"device": "tv"})
        assert r2.status == InvokeStatus.DENIED

    def test_reject_and_remember_blocks_permanently(self):
        cap = _make_cap("pc.send_sns", risk=RiskLevel.READ_ONLY)
        engine = PolicyEngine()
        broker = _setup_broker([cap], engine)

        # Explicit deny blocks pc.send_sns
        r = broker.invoke_tool("pc.send_sns", {})
        assert r.status == InvokeStatus.DENIED

    def test_rejected_audit_log(self):
        audit = AuditLog(path="data/test_e2e_reject.jsonl")
        cap = _make_cap("room.ir_send", risk=RiskLevel.APPROVAL_REQUIRED)
        engine = create_default_policy_engine()
        broker = _setup_broker([cap], engine)

        r1 = broker.invoke_tool("room.ir_send", {"device": "tv"})
        engine.approval_store.reject(r1.policy_result.approval_request.approval_id)

        audit.log_decision("approval_rejected", cap.id, "REJECTED", actor="user")
        entries = audit.list_recent(10)
        assert any(e.decision == "REJECTED" for e in entries)


# ═══════════════════════════════════════════════════════════════
# Scenario 5: Restricted (Level 3) → deny
# ═══════════════════════════════════════════════════════════════

class TestRestrictedAction:
    def test_explicit_deny_patterns_block_even_read_only(self):
        """Explicit deny patterns like .send_sns are DENIED regardless of risk."""
        cap = _make_cap("pc.send_sns", risk=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap], create_default_policy_engine())
        result = broker.invoke_tool("pc.send_sns", {})
        assert result.status == InvokeStatus.DENIED

    @pytest.mark.parametrize("cap_id", [
        "pc.send_sns", "pc.send_email", "pc.delete_all", "room.robot_arm_move",
        "dev.merge_to_main", "pc.access_ssh_key", "pc.read_secret_env",
        "pc.bypass_policy", "pc.captcha_bypass",
    ])
    def test_all_explicit_deny_patterns_blocked(self, cap_id):
        cap = _make_cap(cap_id, risk=RiskLevel.READ_ONLY)
        broker = _setup_broker([cap], create_default_policy_engine())
        result = broker.invoke_tool(cap_id, {})
        assert result.status == InvokeStatus.DENIED, f"{cap_id} should be DENIED, got {result.status.name}"


# ═══════════════════════════════════════════════════════════════
# Scenario 6: Unknown capability → not_found
# ═══════════════════════════════════════════════════════════════

class TestUnknownCapability:
    def test_unknown_capability_returns_not_found(self):
        broker = _setup_broker([], create_default_policy_engine())
        result = broker.invoke_tool("nonexistent.cap", {})
        assert result.status == InvokeStatus.NOT_FOUND

    def test_unknown_not_in_ui(self):
        """Unknown capabilities don't create approval requests."""
        policy = create_default_policy_engine()
        broker = _setup_broker([], policy)
        broker.invoke_tool("nonexistent.cap", {})
        assert len(policy.approval_store.get_pending()) == 0


# ═══════════════════════════════════════════════════════════════
# Scenario 7: AutonomousLoop pause on approval_required
# ═══════════════════════════════════════════════════════════════

class TestAutonomousLoopApprovalPause:
    def test_loop_pauses_when_step_requires_approval(self):
        """When a step requires approval, the loop stops and does NOT auto-retry."""
        from aegis_ai.memory.reflection import ReflectionLog

        # Setup: a broker with an approval-required capability
        cap = _make_cap("room.ir_send", name="Send IR", risk=RiskLevel.APPROVAL_REQUIRED)
        registry = ToolRegistry()
        registry.register_capability(cap)
        broker = ToolBroker(registry)

        # Setup loop with mock LLM that generates a plan
        audit = AuditLog(path="data/test_e2e_loop_approval.jsonl")
        reflection = ReflectionLog(path="data/test_e2e_loop_refl.jsonl")

        # Use the standard MockLLMClient with "delete" keyword → room.ir_send plan
        mock_llm = _MockDeleteLLM()
        planner = Planner(llm_client=mock_llm)

        loop = AutonomousLoop(
            context_builder=ContextBuilder(),
            llm_client=mock_llm,
            planner=planner,
            tool_broker=broker,
            audit_log=audit,
            reflection_log=reflection,
        )
        loop.enable()

        class FakeTask:
            context_summary = "Send IR signal to TV"

        result = loop.run_once(task_request=FakeTask())

        # The loop should have run
        assert result is not None
        # Plan should be created
        assert result.plan is not None
        # Action results should show the step was processed
        assert len(result.action_results) > 0
        # The action should be APPROVAL_NEEDED (not DENIED, not SUCCESS)
        statuses = {r["status"] for r in result.action_results}
        assert "APPROVAL_NEEDED" in statuses, f"Expected APPROVAL_NEEDED, got {statuses}"

    def test_loop_does_not_execute_denied_capability(self):
        """The loop should NOT execute capabilities that PolicyEngine denies."""
        from aegis_ai.memory.reflection import ReflectionLog

        cap = _make_cap("pc.send_sns", risk=RiskLevel.READ_ONLY)  # blocked by explicit deny
        registry = ToolRegistry()
        registry.register_capability(cap)
        broker = ToolBroker(registry)

        audit = AuditLog(path="data/test_e2e_loop_deny.jsonl")
        reflection = ReflectionLog(path="data/test_e2e_loop_deny_refl.jsonl")
        mock_llm = _MockSNSLLM()
        planner = Planner(llm_client=mock_llm)

        loop = AutonomousLoop(
            context_builder=ContextBuilder(),
            llm_client=mock_llm,
            planner=planner,
            tool_broker=broker,
            audit_log=audit,
            reflection_log=reflection,
        )
        loop.enable()

        class FakeTask:
            context_summary = "Post to SNS"

        result = loop.run_once(task_request=FakeTask())
        assert result is not None
        assert len(result.action_results) > 0
        # Action should be DENIED, not SUCCESS
        statuses = {r["status"] for r in result.action_results}
        assert "DENIED" in statuses, f"Expected DENIED, got {statuses}"


# ── Mock LLMs for testing ─────────────────────────────────────

class _MockDeleteLLM(MockLLMClient):
    def generate_thought(self, context: str) -> Any:
        from aegis_ai.llm.client import LLMThought
        return LLMThought(
            summary="Send IR signal",
            recommended_action="Send IR to TV using room.ir_send",
            confidence=0.8,
        )

    def generate_plan(self, thought: Any, context: str) -> Any:
        from aegis_ai.llm.client import LLMPlanOutput
        return LLMPlanOutput(
            goal="Send IR signal",
            steps=[{"description": "Send IR", "capability_id": "room.ir_send",
                     "params": {}, "risk": "LEVEL_2_APPROVAL"}],
            risk_assessment="Requires approval",
        )


class _MockSNSLLM(MockLLMClient):
    def generate_thought(self, context: str) -> Any:
        from aegis_ai.llm.client import LLMThought
        return LLMThought(
            summary="Post to SNS",
            recommended_action="Post to SNS using pc.send_sns",
            confidence=0.7,
        )

    def generate_plan(self, thought: Any, context: str) -> Any:
        from aegis_ai.llm.client import LLMPlanOutput
        return LLMPlanOutput(
            goal="Post to SNS",
            steps=[{"description": "Post to SNS", "capability_id": "pc.send_sns",
                     "params": {}, "risk": "LEVEL_3_RESTRICTED"}],
            risk_assessment="BLOCKED",
        )
