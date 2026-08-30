"""Tests for the Approval System Redesign.

Covers:
- ApprovalManager lifecycle (create, approve, reject, modify, cancel, expire, execute, fail)
- ApprovalFanout (channel registration, parallel delivery, failure handling)
- PolicyEngine decoupling (ASK_APPROVAL without ApprovalRequest creation)
- ToolBroker integration (approval_manager.create_request, execute_approved)
- Double-execution prevention
- Audit logging
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import threading
import time
from unittest.mock import MagicMock

import pytest

# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def audit_log(tmp_dir):
    from aegis_ai.audit import AuditLog
    return AuditLog(path=os.path.join(tmp_dir, "audit.jsonl"))


@pytest.fixture
def approval_queue(tmp_dir, audit_log):
    from aegis_ai.approval.approval_queue import ApprovalQueue
    return ApprovalQueue(data_dir=os.path.join(tmp_dir, "approvals"), audit_log=audit_log)


@pytest.fixture
def approval_manager(approval_queue, audit_log):
    from aegis_ai.approval.approval_manager import ApprovalManager
    return ApprovalManager(approval_queue=approval_queue, audit_log=audit_log)


def _make_tool_request(cap_id="pc-server.screenshot.get_screenshot", risk=None):
    from tool_broker import ToolExecutionRequest, ExecutionSource
    return ToolExecutionRequest(
        request_id="req_test_001",
        task_id="task_001",
        source=ExecutionSource.USER_EXPLICIT,
        capability_id=cap_id,
        arguments={"delay": 0},
        source_desire="user_helpfulness",
        frustration=0.5,
    )


def _make_policy_result(decision="ASK_APPROVAL", reason="test"):
    from policy_engine import PolicyResult, PolicyDecision
    from aegis_schema.models import RiskLevel
    return PolicyResult(
        decision=PolicyDecision.ASK_APPROVAL,
        reason=reason,
        capability_id="pc-server.screenshot.get_screenshot",
        risk_level=RiskLevel.APPROVAL_REQUIRED,
    )


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ── Task 1: ApprovalManager ──────────────────────────────────

class TestApprovalManager:

    def test_create_request(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        assert req.approval_id.startswith("appr_")
        assert req.status == "pending"
        assert req.capability_id == "pc-server.screenshot.get_screenshot"

    def test_list_pending(self, approval_manager):
        approval_manager.create_request(_make_tool_request(), _make_policy_result())
        pending = approval_manager.list_pending()
        assert len(pending) == 1
        assert pending[0].status == "pending"

    def test_approve(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        result = approval_manager.approve(req.approval_id, channel="dashboard", user="test_user")
        assert result is not None
        assert result.status == "approved"
        assert result.approved_by_channel == "dashboard"
        assert result.approved_by_user == "test_user"

    def test_double_approve_is_idempotent(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        approval_manager.approve(req.approval_id, channel="dashboard")
        result = approval_manager.approve(req.approval_id, channel="dashboard")
        assert result is None

    def test_reject(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        result = approval_manager.reject(req.approval_id, channel="pc_overlay", reason="too risky")
        assert result is not None
        assert result.status == "pending"
        assert result.surface_decisions["pc_overlay"]["decision"] == "rejected"

    def test_global_reject(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        result = approval_manager.global_reject(req.approval_id, channel="pc_overlay", reason="too risky")
        assert result is not None
        assert result.status == "rejected"

    def test_modify_and_approve(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        result = approval_manager.modify_and_approve(
            req.approval_id, {"delay": 5}, channel="dashboard", user="user"
        )
        assert result is not None
        assert result.status == "modified"
        assert result.arguments == {"delay": 5}

    def test_cancel(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        result = approval_manager.cancel(req.approval_id, reason="user cancelled")
        assert result is not None
        assert result.status == "cancelled"

    def test_mark_executed(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        approval_manager.approve(req.approval_id)
        approval_manager.mark_executed(req.approval_id, result={"status": "ok"})
        updated = approval_manager.get(req.approval_id)
        assert updated.status == "executed"

    def test_mark_failed(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        approval_manager.approve(req.approval_id)
        approval_manager.mark_failed(req.approval_id, error="timeout")
        updated = approval_manager.get(req.approval_id)
        assert updated.status == "failed"

    def test_is_executed(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        approval_manager.approve(req.approval_id)
        assert not approval_manager.is_executed(req.approval_id)
        approval_manager.mark_executed(req.approval_id)
        assert approval_manager.is_executed(req.approval_id)

    def test_is_approved(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        assert not approval_manager.is_approved(req.approval_id)
        approval_manager.approve(req.approval_id)
        assert approval_manager.is_approved(req.approval_id)

    def test_on_state_change_callback(self, approval_manager):
        events = []
        approval_manager.on_state_change(lambda e: events.append(e))
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        assert len(events) == 1
        assert events[0]["event_type"] == "created"
        approval_manager.approve(req.approval_id)
        assert len(events) == 2
        assert events[1]["event_type"] == "approved"

    def test_callback_failure_does_not_break_others(self, approval_manager):
        def bad_callback(event):
            raise RuntimeError("boom")

        good_events = []
        approval_manager.on_state_change(bad_callback)
        approval_manager.on_state_change(lambda e: good_events.append(e))
        approval_manager.create_request(_make_tool_request(), _make_policy_result())
        assert len(good_events) == 1


# ── Task 2: ApprovalFanout ───────────────────────────────────

class MockChannel:
    def __init__(self, channel_id, fail=False):
        self._id = channel_id
        self._fail = fail
        self.delivered = []
        self.updated = []

    @property
    def channel_id(self):
        return self._id

    async def deliver(self, event):
        if self._fail:
            raise RuntimeError("channel failed")
        self.delivered.append(event)
        return not self._fail

    async def update(self, event):
        if self._fail:
            raise RuntimeError("channel failed")
        self.updated.append(event)
        return not self._fail

    async def health_check(self):
        return not self._fail


class TestApprovalFanout:

    def test_register_channel(self):
        from aegis_ai.approval.fanout import ApprovalFanout
        fanout = ApprovalFanout()
        ch = MockChannel("test")
        fanout.register_channel(ch)
        assert len(fanout.get_channels()) == 1

    def test_unregister_channel(self):
        from aegis_ai.approval.fanout import ApprovalFanout
        fanout = ApprovalFanout()
        ch = MockChannel("test")
        fanout.register_channel(ch)
        fanout.unregister_channel("test")
        assert len(fanout.get_channels()) == 0

    def test_fanout_delivers_to_all_channels(self):
        from aegis_ai.approval.fanout import ApprovalFanout, ApprovalEvent
        fanout = ApprovalFanout()
        ch_a = MockChannel("a")
        ch_b = MockChannel("b")
        fanout.register_channel(ch_a)
        fanout.register_channel(ch_b)
        event = ApprovalEvent(approval_id="appr_001", event_type="created")
        results = _run_async(fanout.fanout(event))
        assert results["a"] is True
        assert results["b"] is True
        assert len(ch_a.delivered) == 1
        assert len(ch_b.delivered) == 1

    def test_channel_failure_does_not_block(self):
        from aegis_ai.approval.fanout import ApprovalFanout, ApprovalEvent
        fanout = ApprovalFanout()
        good = MockChannel("good")
        bad = MockChannel("bad", fail=True)
        fanout.register_channel(good)
        fanout.register_channel(bad)
        event = ApprovalEvent(approval_id="appr_001", event_type="created")
        results = _run_async(fanout.fanout(event))
        assert results["good"] is True
        assert results["bad"] is False
        assert len(good.delivered) == 1

    def test_mask_approval_request(self):
        from aegis_ai.approval.fanout import build_approval_display_payload, mask_approval_request
        req = MagicMock()
        req.to_dict.return_value = {
            "approval_id": "appr_001",
            "capability_id": "pc-server.screenshot.get_screenshot",
            "tool_name": "Screenshot",
            "risk_level": "medium",
            "approval_reason": "test",
            "user_facing_summary": "take screenshot",
            "arguments_summary": "{'delay': 0}",
            "expected_outcome": "capture screen",
            "possible_side_effects": "screen contents are observed",
            "status": "pending",
            "created_at": 1000,
            "expires_at": 2000,
            "secret_field": "should_not_appear",
        }
        masked = mask_approval_request(req)
        assert "secret_field" not in masked
        assert masked["approval_id"] == "appr_001"
        assert masked["approval_reason"] == "test"
        assert masked["user_facing_summary"] == "take screenshot"
        assert masked["expected_outcome"] == "capture screen"
        payload = build_approval_display_payload(req)
        assert "test" in payload["body"]
        assert "take screenshot" in payload["body"]

    def test_pc_overlay_channel_uses_action_and_reason(self):
        from aegis_ai.approval.channels.pc_overlay import PcOverlayApprovalChannel
        from aegis_ai.approval.fanout import ApprovalEvent

        executor = MagicMock()
        executor.execute_capability.return_value = {
            "ok": True,
            "approved": True,
            "request_id": "req_1",
            "response": "Approved with Y key",
        }
        manager = MagicMock()
        channel = PcOverlayApprovalChannel(server_executor=executor, approval_manager=manager)
        event = ApprovalEvent(
            approval_id="appr_001",
            event_type="created",
            request_summary={
                "title": "Approval required: Discord voice",
                "body": "Reason: joining voice changes Discord state",
                "approval_reason": "joining voice changes Discord state",
                "risk_level": "medium",
            },
            state="pending",
        )

        assert _run_async(channel.deliver(event)) is True
        executor.execute_capability.assert_called_once()
        capability_id, args = executor.execute_capability.call_args.args
        assert capability_id == "pc-server.approval.overlay"
        assert "action" in args
        assert "joining voice changes Discord state" in args["action"]
        manager.approve.assert_called_once_with("appr_001", channel="pc_overlay", user="pc_user")

    def test_android_channel_sends_body_with_reason(self):
        from aegis_ai.approval.channels.android import AndroidApprovalChannel
        from aegis_ai.approval.fanout import ApprovalEvent

        manager = MagicMock()
        manager.send_approval_to_android.return_value = True
        channel = AndroidApprovalChannel(android_manager=manager)
        event = ApprovalEvent(
            approval_id="appr_002",
            event_type="created",
            request_summary={
                "title": "Approval required: Android tap",
                "body": "Reason: tapping changes the phone UI",
                "approval_reason": "tapping changes the phone UI",
            },
            state="pending",
        )

        assert _run_async(channel.deliver(event)) is True
        kwargs = manager.send_approval_to_android.call_args.kwargs
        assert kwargs["approval_id"] == "appr_002"
        assert "tapping changes the phone UI" in kwargs["body"]

    def test_chat_approval_continuation_uses_llm_followup(self, tmp_path):
        from types import SimpleNamespace
        from tool_broker import InvokeStatus, ToolExecutionResult
        from aegis_ai.web.dashboard_routes import DashboardApp

        class FakeLlm:
            def __init__(self):
                self.prompts = []

            def generate(self, **kwargs):
                self.prompts.append(kwargs["prompt"])
                return SimpleNamespace(success=True, content="Discordの通話へ参加しました。", error="")

        result = ToolExecutionResult(
            request_id="req_1",
            status=InvokeStatus.SUCCESS,
            output={"success": True, "message": "joined voice"},
        )
        runtime = SimpleNamespace(
            llm_gateway=FakeLlm(),
            tool_broker=SimpleNamespace(execute_approved=MagicMock(return_value=result)),
            task_manager=MagicMock(),
            android_manager=None,
        )
        routes = DashboardApp.__new__(DashboardApp)
        routes._runtime = runtime
        routes._chat_history_path = tmp_path / "chat_history.jsonl"
        routes._chat_event_clients = {}
        routes._chat_event_lock = threading.Lock()
        request = SimpleNamespace(
            approval_id="appr_003",
            capability_id="pc-server.discord.join_voice_by_name",
            tool_name="Discord voice join",
            approval_reason="Discord voice state changes",
            task_id="task_1",
            step_id="step_1",
            conversation_id="conv_1",
            metadata={
                "original_user_message": "memoサーバーの通話に入って",
                "audit_group_id": "task_1",
                "audit_group_type": "chat",
                "audit_group_title": "Chat: memo",
            },
        )

        assert routes._continue_chat_approval_with_audit(request, "appr_003") is True
        runtime.tool_broker.execute_approved.assert_called_once_with("appr_003")
        saved = routes._chat_history_path.read_text(encoding="utf-8")
        assert "Discordの通話へ参加しました。" in saved
        assert "Approved action completed" not in saved
        assert "joined voice" in runtime.llm_gateway.prompts[0]


# ── Task 3: PolicyEngine Decoupling ──────────────────────────

class TestPolicyEngineDecoupling:

    def test_non_monetary_action_executes_without_approval_request(self):
        from policy_engine import PolicyEngine, PolicyDecision
        from aegis_schema.models import Capability, RiskLevel, ServerType
        engine = PolicyEngine()
        cap = Capability(
            id="pc-server.mouse.mouse_click",
            name="Mouse Click",
            description="Click at coordinates",
            server_type=ServerType.PC,
            risk_level=RiskLevel.APPROVAL_REQUIRED,
        )
        result = engine.evaluate(cap, {"x": 100, "y": 200})
        assert result.decision == PolicyDecision.ALLOW_WITH_AUDIT
        assert result.approval_request is None

    def test_no_approval_store_still_works(self):
        from policy_engine import PolicyEngine, PolicyDecision
        from aegis_schema.models import Capability, RiskLevel, ServerType
        engine = PolicyEngine(approval_store=None)
        cap = Capability(
            id="pc-server.mouse.mouse_click",
            name="Mouse Click",
            description="Click at coordinates",
            server_type=ServerType.PC,
            risk_level=RiskLevel.APPROVAL_REQUIRED,
        )
        result = engine.evaluate(cap, {"x": 100, "y": 200})
        assert result.decision == PolicyDecision.ALLOW_WITH_AUDIT

    def test_deny_patterns_unchanged(self):
        from policy_engine import PolicyEngine, PolicyDecision
        from aegis_schema.models import Capability, RiskLevel, ServerType
        engine = PolicyEngine()
        cap = Capability(
            id="browser-server.checkout.purchase",
            name="Purchase",
            description="Buy something",
            server_type=ServerType.BROWSER,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = engine.evaluate(cap, {"item": "test"})
        assert result.decision == PolicyDecision.DENY


# ── Task 4: ToolBroker Integration ───────────────────────────

class TestToolBrokerApproval:

    def test_execute_bypasses_approval_manager_for_non_monetary_action(
        self, approval_manager, audit_log, tmp_dir
    ):
        from tool_broker import ToolBroker, ToolExecutionRequest, ExecutionSource, InvokeStatus
        from policy_engine import PolicyDecision, PolicyEngine
        from tool_registry import ToolRegistry
        from aegis_schema.models import RiskLevel

        policy = PolicyEngine()
        registry = ToolRegistry()
        broker = ToolBroker(
            registry=registry,
            policy_engine=policy,
            audit_log=audit_log,
            approval_manager=approval_manager,
            server_executor=MagicMock(),
        )
        broker._server_executor.execute.return_value = {"ok": True}

        manifest = MagicMock()
        manifest.capability_id = "pc-server.mouse.mouse_click"
        manifest.title = "Mouse Click"
        manifest.description = "Click"
        manifest.risk_level = "medium"
        manifest.tags = []
        manifest.side_effects = []
        manifest.requires_approval = True
        manifest.enabled = True
        manifest.server_id = "pc-server"
        manifest.app_id = "mouse"
        manifest.action = "mouse_click"
        manifest.input_schema = {"type": "object", "properties": {"x": {"type": "number"}, "y": {"type": "number"}}}

        broker._catalog = MagicMock()
        broker._catalog.resolve.return_value = manifest
        broker._folder_registry = MagicMock()
        broker._folder_registry.get.return_value = manifest

        cap = MagicMock()
        cap.id = "pc-server.mouse.mouse_click"
        cap.risk_level = RiskLevel.APPROVAL_REQUIRED
        cap.name = "Mouse Click"
        cap.description = "Click"
        cap.side_effects = []
        broker._registry.get_capability = MagicMock(return_value=cap)

        request = ToolExecutionRequest(
            capability_id="pc-server.mouse.mouse_click",
            arguments={"x": 100, "y": 200},
            source=ExecutionSource.USER_EXPLICIT,
        )
        result = broker.execute(request)
        assert result.status == InvokeStatus.SUCCESS
        assert result.policy_result.decision == PolicyDecision.ALLOW_WITH_AUDIT
        assert approval_manager.list_pending() == []

    def test_execute_approved_prevents_double_execution(self, approval_manager, audit_log, tmp_dir):
        from tool_broker import ToolBroker, InvokeStatus
        from policy_engine import PolicyEngine
        from tool_registry import ToolRegistry

        policy = PolicyEngine()
        registry = ToolRegistry()
        broker = ToolBroker(
            registry=registry,
            policy_engine=policy,
            audit_log=audit_log,
            approval_manager=approval_manager,
        )

        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        approval_manager.approve(req.approval_id)
        approval_manager.mark_executed(req.approval_id)

        result = broker.execute_approved(req.approval_id)
        assert result.status == InvokeStatus.DENIED
        assert "already executed" in result.error


# ── Task 10: Audit Logging ───────────────────────────────────

class TestApprovalAudit:

    def test_approval_lifecycle_audited(self, approval_manager, audit_log, tmp_dir):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        approval_manager.approve(req.approval_id, channel="dashboard", user="user")
        approval_manager.mark_executed(req.approval_id)

        entries = audit_log.read_all()
        actions = [e["action"] for e in entries]
        assert "approval_created" in actions
        assert "approval_approved" in actions
        assert "approval_executed" in actions

    def test_audit_records_channel_and_user(self, approval_manager, audit_log, tmp_dir):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        approval_manager.approve(req.approval_id, channel="pc_overlay", user="owner")

        entries = audit_log.read_all()
        approved = [e for e in entries if e["action"] == "approval_approved"]
        assert len(approved) == 1
        assert approved[0]["approval_channel"] == "pc_overlay"
        assert approved[0]["approval_user"] == "owner"


# ── Expired approval tests ───────────────────────────────────

class TestExpiredApproval:

    def test_expired_approval_cannot_be_approved(self, approval_queue, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        req.status = "expired"
        req.expires_at = int(time.time() * 1000) - 1000
        approval_queue._requests[req.approval_id] = req
        approval_queue._save()

        result = approval_manager.approve(req.approval_id)
        assert result is None

    def test_cancelled_approval_cannot_be_executed(self, approval_manager):
        req = approval_manager.create_request(_make_tool_request(), _make_policy_result())
        approval_manager.cancel(req.approval_id)
        assert approval_manager.is_executed(req.approval_id) is False
        assert approval_manager.is_approved(req.approval_id) is False
