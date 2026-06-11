"""Tests for Approval UI — web app, templates, API endpoints."""

from __future__ import annotations

import time

import pytest

from aegis_ai.web.app import ApprovalWebApp
from approval import ApprovalStatus, ApprovalStore


@pytest.fixture
def store() -> ApprovalStore:
    return ApprovalStore()


@pytest.fixture
def client(store):
    webapp = ApprovalWebApp(store, secret_key="test-secret")
    webapp.app.config["TESTING"] = True
    return webapp.app.test_client()


class TestApprovalList:
    def test_empty_list(self, client):
        resp = client.get("/approvals")
        assert resp.status_code == 200
        assert b"No pending approvals" in resp.data

    def test_list_with_items(self, client, store):
        store.create_request("pc.delete_file", tool_name="Delete File",
                            requested_action="Delete /tmp/test.txt",
                            human_readable_summary="Delete a temporary file",
                            risk_explanation="Permanent file deletion",
                            payload_preview='{"path":"/tmp/test.txt"}',
                            risk_level=3)
        resp = client.get("/approvals")
        assert resp.status_code == 200
        assert b"Delete File" in resp.data


class TestApprovalDetail:
    def test_detail_view(self, client, store):
        req = store.create_request("room.ir_send", tool_name="Send IR",
                                  requested_action="Send IR to TV",
                                  risk_level=3, human_readable_summary="IR signal")
        resp = client.get(f"/approvals/{req.approval_id}")
        assert resp.status_code == 200
        assert b"Send IR" in resp.data
        assert b"room.ir_send" in resp.data

    def test_detail_not_found(self, client):
        resp = client.get("/approvals/nonexistent")
        assert resp.status_code == 404


class TestApproveActions:
    def test_approve_once(self, client, store):
        req = store.create_request("pc.delete_file", risk_level=3)
        # Test the store directly (avoids CSRF in unit tests)
        ok = store.approve_once(req.approval_id)
        assert ok is True
        assert req.status == ApprovalStatus.APPROVED

    def test_approve_session(self, client, store):
        req = store.create_request("pc.delete_file", risk_level=3)
        store.approve_for_session(req.approval_id)
        assert req.status == ApprovalStatus.APPROVED
        assert req.approved_type is not None

    def test_reject(self, client, store):
        req = store.create_request("pc.test", risk_level=3)
        store.reject(req.approval_id)
        assert req.status == ApprovalStatus.REJECTED

    def test_reject_remember(self, client, store):
        req = store.create_request("pc.send_sns", risk_level=3)
        store.reject_and_remember(req.approval_id)
        assert req.status == ApprovalStatus.REJECTED
        assert store.is_permanently_denied("pc.send_sns")


class TestExpiredApproval:
    def test_expired_approval_cannot_be_approved(self, client, store):
        s = ApprovalStore(request_timeout_ms=1)
        req = s.create_request("pc.test", risk_level=3)
        time.sleep(0.01)
        assert s.approve_once(req.approval_id) is False
        assert req.status == ApprovalStatus.EXPIRED

    def test_expired_shown_in_ui(self, client, store):
        s = ApprovalStore(request_timeout_ms=1)
        s.create_request("pc.test", risk_level=3)
        time.sleep(0.02)
        # Expired should not appear in pending list
        pending = s.get_pending()
        assert len(pending) == 0


class TestSecretMasking:
    def test_mask_password(self):
        from aegis_ai.web.app import ApprovalWebApp
        result = ApprovalWebApp._mask_payload('password="mysecret123" key="value"')
        assert "[REDACTED]" in result
        assert "mysecret123" not in result

    def test_mask_token(self):
        from aegis_ai.web.app import ApprovalWebApp
        result = ApprovalWebApp._mask_payload('token=abc123xyz args')
        assert "[REDACTED]" in result
        assert "abc123xyz" not in result

    def test_safe_values_preserved(self):
        from aegis_ai.web.app import ApprovalWebApp
        result = ApprovalWebApp._mask_payload('path="/tmp/file.txt" user="alice"')
        assert "/tmp/file.txt" in result
        assert "alice" in result


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json["status"] == "ok"


class TestAuditIntegration:
    def test_approval_decision_logged(self, store):
        """Approval decisions should be loggable to audit."""
        from aegis_ai.audit import AuditLog
        audit = AuditLog(path="data/test_approval_audit.jsonl")
        req = store.create_request("room.ir_send", risk_level=3)
        store.approve_once(req.approval_id)
        audit.log_decision(
            "approval_granted", req.capability_id, "APPROVED",
            reason="User approved one-time", actor="user",
            detail={"approval_id": req.approval_id},
        )
        recent = audit.list_recent(10)
        assert len(recent) == 1
        assert recent[0].decision == "APPROVED"
