"""Tests for ApprovalStore — Phase 1.5 approval lifecycle."""

from __future__ import annotations

import time

from approval import ApprovalStatus, ApprovalStore, ApprovalType


class TestApprovalLifecycle:
    def test_create_approval_request(self):
        store = ApprovalStore()
        req = store.create_request("room.ir_send", tool_name="Send IR",
            requested_action="Send IR to TV", human_readable_summary="Send IR signal to the TV",
            risk_explanation="Controls physical device", payload_preview='{"device":"tv"}',
            risk_level=3)
        assert req.status == ApprovalStatus.PENDING
        assert req.approval_id.startswith("approval_")
        assert req.capability_id == "room.ir_send"
        assert req.expires_at_ms > req.created_at_ms

    def test_approve_once(self):
        store = ApprovalStore()
        req = store.create_request("pc.delete_file", risk_level=3)
        assert store.approve_once(req.approval_id) is True
        assert req.status == ApprovalStatus.APPROVED
        assert req.approved_type == ApprovalType.ONE_TIME

    def test_approve_for_session(self):
        store = ApprovalStore()
        req = store.create_request("pc.delete_file", risk_level=3)
        assert store.approve_for_session(req.approval_id) is True
        assert req.status == ApprovalStatus.APPROVED
        assert req.approved_type == ApprovalType.SESSION

    def test_reject(self):
        store = ApprovalStore()
        req = store.create_request("pc.test", risk_level=3)
        assert store.reject(req.approval_id) is True
        assert req.status == ApprovalStatus.REJECTED

    def test_reject_and_remember(self):
        store = ApprovalStore()
        req = store.create_request("pc.send_sns", risk_level=3)
        assert store.reject_and_remember(req.approval_id) is True
        assert req.status == ApprovalStatus.REJECTED
        assert store.is_permanently_denied("pc.send_sns") is True

    def test_reject_and_remember_blocks_future(self):
        store = ApprovalStore()
        # First: reject and remember
        req1 = store.create_request("room.robot_arm_move", risk_level=3)
        store.reject_and_remember(req1.approval_id)
        # Future approvals for same capability are auto-denied
        assert store.is_approved("room.robot_arm_move") is False
        # Even if we manually create and approve a new request
        req2 = store.create_request("room.robot_arm_move", risk_level=3)
        store.approve_once(req2.approval_id)
        assert store.is_approved("room.robot_arm_move") is False  # Still denied


class TestApprovalExpiry:
    def test_expired_approval_cannot_be_approved(self):
        store = ApprovalStore(request_timeout_ms=1)
        req = store.create_request("pc.test", risk_level=3)
        time.sleep(0.01)
        assert store.approve_once(req.approval_id) is False
        assert req.status == ApprovalStatus.EXPIRED

    def test_pending_requests_excludes_expired(self):
        store = ApprovalStore(request_timeout_ms=1)
        store.create_request("pc.a", risk_level=3)
        time.sleep(0.01)
        store.create_request("pc.b", risk_level=3)
        pending = store.get_pending()
        assert len(pending) == 1  # Only pc.b is still pending

    def test_get_pending_alias(self):
        store = ApprovalStore()
        store.create_request("pc.test", risk_level=3)
        assert len(store.get_pending()) == len(store.get_pending_requests())


class TestOneTimeConsumption:
    def test_one_time_approval_consumed(self):
        store = ApprovalStore()
        req = store.create_request("room.ir_send", risk_level=3)
        store.approve_once(req.approval_id)
        # First consume works
        assert store.consume_approval("room.ir_send") is not None
        # Second consume fails
        assert store.consume_approval("room.ir_send") is None

    def test_session_approval_not_consumed(self):
        store = ApprovalStore()
        req = store.create_request("room.ir_send", risk_level=3)
        store.approve_for_session(req.approval_id)
        # Can consume multiple times
        assert store.consume_approval("room.ir_send") is not None
        assert store.consume_approval("room.ir_send") is not None


class TestApprovalRequestFields:
    def test_payload_preview(self):
        store = ApprovalStore()
        req = store.create_request("pc.test", payload_preview='{"path":"/tmp/file.txt"}', risk_level=2)
        assert req.payload_preview == '{"path":"/tmp/file.txt"}'

    def test_human_readable_summary(self):
        store = ApprovalStore()
        req = store.create_request("pc.test", human_readable_summary="Delete temporary file", risk_level=2)
        assert req.human_readable_summary == "Delete temporary file"

    def test_expires_at_set(self):
        store = ApprovalStore(request_timeout_ms=30000)
        req = store.create_request("pc.test", risk_level=2)
        assert req.expires_at_ms == req.created_at_ms + 30000

    def test_forget_denial(self):
        store = ApprovalStore()
        req = store.create_request("pc.test", risk_level=3)
        store.reject_and_remember(req.approval_id)
        assert store.is_permanently_denied("pc.test")
        store.forget_denial("pc.test")
        assert not store.is_permanently_denied("pc.test")
