"""Tests for Approval Queue."""

from __future__ import annotations

import json
import shutil
import tempfile
import time

import pytest

from aegis_ai.approval import (
    ApprovalDecision,
    ApprovalQueue,
    ApprovalRequest,
    ApprovalStatus,
    DecisionType,
)
from aegis_ai.approval.approval_types import _mask_arguments, _summarize_arguments


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _make_tool_request(cap_id="room.ir_send", source="desire_driven", args=None):
    from tool_broker import ToolExecutionRequest, ExecutionSource
    return ToolExecutionRequest(
        request_id="r1",
        task_id="t1",
        capability_id=cap_id,
        tool_name="IR Send",
        arguments=args or {"device": "tv"},
        source=ExecutionSource(source) if source in [e.value for e in ExecutionSource] else ExecutionSource.DESIRE_DRIVEN,
        source_desire="curiosity",
        frustration=5.0,
    )


def _make_policy_result():
    from policy_engine import PolicyResult, PolicyDecision
    return PolicyResult(
        decision=PolicyDecision.ASK_APPROVAL,
        reason="Risk level HIGH_RISK — approval required.",
        capability_id="room.ir_send",
    )


class TestEnqueue:
    def test_enqueue_creates_request(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        assert req.approval_id.startswith("appr_")
        assert req.status == "pending"
        assert req.capability_id == "room.ir_send"

    def test_enqueue_persists(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        queue.enqueue(_make_tool_request(), _make_policy_result())
        queue2 = ApprovalQueue(data_dir=tmpdir)
        assert len(queue2.list_pending()) == 1

    def test_enqueue_has_user_facing_summary(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        assert "IR Send" in req.user_facing_summary
        assert "approval" in req.user_facing_summary.lower() or "承認" in req.user_facing_summary


class TestListPending:
    def test_list_pending_returns_only_pending(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        r1 = queue.enqueue(_make_tool_request(), _make_policy_result())
        r2 = queue.enqueue(_make_tool_request(cap_id="pc.click"), _make_policy_result())
        queue.reject(r1.approval_id, "not needed")
        pending = queue.list_pending()
        assert len(pending) == 1
        assert pending[0].approval_id == r2.approval_id

    def test_list_pending_excludes_expired(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        req.expires_at = int(time.time() * 1000) - 1000
        queue._save()
        pending = queue.list_pending()
        assert len(pending) == 0


class TestApprove:
    def test_approve_changes_status(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        result = queue.approve(req.approval_id, "OK from user")
        assert result.status == "approved"

    def test_approve_expired_returns_none(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        req.expires_at = int(time.time() * 1000) - 1000
        queue._save()
        result = queue.approve(req.approval_id)
        assert result is None

    def test_approve_nonexistent_returns_none(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        assert queue.approve("nonexistent") is None


class TestReject:
    def test_reject_changes_status(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        result = queue.reject(req.approval_id, "too risky")
        assert result.status == "rejected"


class TestModifyAndApprove:
    def test_modify_changes_arguments(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        new_args = {"device": "ac", "power": "on"}
        result = queue.modify_and_approve(req.approval_id, new_args, "changed device")
        assert result.status == "modified"
        assert result.arguments == new_args

    def test_modify_expired_returns_none(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        req.expires_at = int(time.time() * 1000) - 1000
        queue._save()
        result = queue.modify_and_approve(req.approval_id, {"x": 1})
        assert result is None


class TestCancel:
    def test_cancel_changes_status(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        result = queue.cancel(req.approval_id, "user cancelled")
        assert result.status == "cancelled"


class TestExpire:
    def test_expire_old_requests(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        req.expires_at = int(time.time() * 1000) - 1000
        queue._save()
        count = queue.expire_old_requests()
        assert count == 1
        assert queue.get(req.approval_id).status == "expired"


class TestMarkExecuted:
    def test_mark_executed(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        queue.approve(req.approval_id)
        queue.mark_executed(req.approval_id)
        assert queue.get(req.approval_id).status == "executed"
        assert queue.is_executed(req.approval_id)

    def test_double_execute_prevented(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        queue.approve(req.approval_id)
        queue.mark_executed(req.approval_id)
        assert queue.is_executed(req.approval_id)


class TestMarkFailed:
    def test_mark_failed(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        queue.approve(req.approval_id)
        queue.mark_failed(req.approval_id, "execution error")
        assert queue.get(req.approval_id).status == "failed"


class TestDesireDriven:
    def test_desire_driven_source_preserved(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        assert req.source == "desire_driven"
        assert req.source_desire == "curiosity"
        assert req.frustration == 5.0


class TestMasking:
    def test_mask_sensitive_keys(self):
        args = {"api_key": "secret123", "password": "mypass", "name": "test"}
        masked = _mask_arguments(args)
        assert masked["api_key"] == "***MASKED***"
        assert masked["password"] == "***MASKED***"
        assert masked["name"] == "test"

    def test_summarize_truncates(self):
        args = {"data": "x" * 500}
        summary = _summarize_arguments(args, max_len=100)
        assert len(summary) <= 110


class TestPersistence:
    def test_persistence_survives_reload(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        req = queue.enqueue(_make_tool_request(), _make_policy_result())
        aid = req.approval_id
        queue2 = ApprovalQueue(data_dir=tmpdir)
        loaded = queue2.get(aid)
        assert loaded is not None
        assert loaded.capability_id == "room.ir_send"


class TestFormatSummary:
    def test_format_pending_summary(self, tmpdir):
        queue = ApprovalQueue(data_dir=tmpdir)
        queue.enqueue(_make_tool_request(), _make_policy_result())
        summary = queue.format_pending_summary()
        assert "room.ir_send" in summary or "IR Send" in summary
