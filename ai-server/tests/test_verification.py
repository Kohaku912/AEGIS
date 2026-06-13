"""Tests for Verification module."""

from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path

import pytest

from aegis_ai.verification import (
    VerificationRequest,
    VerificationResult,
    VerificationService,
    VerificationStatus,
    VerificationStrategy,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestVerificationStrategySelection:
    def test_file_write_selects_file_exists(self):
        svc = VerificationService()
        strategy = svc.select_strategy("pc.write_file", "WriteFile", {"path": "/tmp/test"})
        assert strategy == VerificationStrategy.FILE_EXISTS

    def test_file_delete_selects_file_not_exists(self):
        svc = VerificationService()
        strategy = svc.select_strategy("pc.delete_file", "DeleteFile", {"path": "/tmp/test"})
        assert strategy == VerificationStrategy.FILE_NOT_EXISTS

    def test_http_selects_http_status(self):
        svc = VerificationService()
        strategy = svc.select_strategy("browser.http_request", "HttpRequest", {})
        assert strategy == VerificationStrategy.HTTP_STATUS

    def test_browser_selects_browser_url(self):
        svc = VerificationService()
        strategy = svc.select_strategy("browser.navigate", "Navigate", {"url": "https://example.com"})
        assert strategy == VerificationStrategy.BROWSER_URL

    def test_pc_selects_screen_observation(self):
        svc = VerificationService()
        strategy = svc.select_strategy("pc.screenshot", "Screenshot", {})
        assert strategy == VerificationStrategy.PC_SCREEN_OBSERVATION

    def test_android_selects_screen_observation(self):
        svc = VerificationService()
        strategy = svc.select_strategy("android.screenshot", "Screenshot", {})
        assert strategy == VerificationStrategy.ANDROID_SCREEN_OBSERVATION

    def test_command_selects_exit_code(self):
        svc = VerificationService()
        strategy = svc.select_strategy("run_command", "RunCommand", {})
        assert strategy == VerificationStrategy.COMMAND_EXIT_CODE

    def test_unknown_selects_none(self):
        svc = VerificationService()
        strategy = svc.select_strategy("unknown.cap", "Unknown", {})
        assert strategy == VerificationStrategy.NONE


class TestFileVerification:
    def test_file_exists_verified(self, tmpdir):
        path = Path(tmpdir) / "test.txt"
        path.write_text("hello")
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="pc.write_file",
            arguments={"path": str(path)},
            verification_strategy=VerificationStrategy.FILE_EXISTS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.VERIFIED
        assert result.confidence > 0.5

    def test_file_not_exists_failed(self, tmpdir):
        path = Path(tmpdir) / "nonexistent.txt"
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="pc.write_file",
            arguments={"path": str(path)},
            verification_strategy=VerificationStrategy.FILE_EXISTS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.FAILED
        assert result.failure_type == "file_missing"

    def test_file_delete_verified(self, tmpdir):
        path = Path(tmpdir) / "deleted.txt"
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="pc.delete_file",
            arguments={"path": str(path)},
            verification_strategy=VerificationStrategy.FILE_NOT_EXISTS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.VERIFIED

    def test_file_delete_failed_still_exists(self, tmpdir):
        path = Path(tmpdir) / "still_here.txt"
        path.write_text("still here")
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="pc.delete_file",
            arguments={"path": str(path)},
            verification_strategy=VerificationStrategy.FILE_NOT_EXISTS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.FAILED
        assert result.failure_type == "file_not_deleted"

    def test_directory_exists_verified(self, tmpdir):
        path = Path(tmpdir) / "subdir"
        path.mkdir()
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="pc.create_directory",
            arguments={"path": str(path)},
            verification_strategy=VerificationStrategy.DIRECTORY_EXISTS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.VERIFIED

    def test_file_content_contains(self, tmpdir):
        path = Path(tmpdir) / "content.txt"
        path.write_text("hello world foo bar")
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="pc.write_file",
            arguments={"path": str(path), "expected_content": "world"},
            verification_strategy=VerificationStrategy.FILE_CONTENT_CONTAINS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.VERIFIED

    def test_file_content_not_contains(self, tmpdir):
        path = Path(tmpdir) / "content.txt"
        path.write_text("hello world")
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="pc.write_file",
            arguments={"path": str(path), "expected_content": "xyz"},
            verification_strategy=VerificationStrategy.FILE_CONTENT_CONTAINS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.FAILED


class TestHttpVerification:
    def test_http_2xx_verified(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="browser.http_request",
            execution_output={"status_code": 200},
            verification_strategy=VerificationStrategy.HTTP_STATUS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.VERIFIED

    def test_http_4xx_failed(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="browser.http_request",
            execution_output={"status_code": 404},
            verification_strategy=VerificationStrategy.HTTP_STATUS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.FAILED
        assert result.failure_type == "client_error"

    def test_http_5xx_failed(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="browser.http_request",
            execution_output={"status_code": 500},
            verification_strategy=VerificationStrategy.HTTP_STATUS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.FAILED
        assert result.failure_type == "server_error"

    def test_http_no_status_unverified(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="browser.http_request",
            execution_output={},
            verification_strategy=VerificationStrategy.HTTP_STATUS,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.UNVERIFIED


class TestCommandVerification:
    def test_exit_code_0_verified(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="run_command",
            execution_output={"exit_code": 0},
            verification_strategy=VerificationStrategy.COMMAND_EXIT_CODE,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.VERIFIED

    def test_exit_code_non0_failed(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="run_command",
            execution_output={"exit_code": 1, "stderr": "error"},
            verification_strategy=VerificationStrategy.COMMAND_EXIT_CODE,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.FAILED
        assert result.failure_type == "command_failed"


class TestBrowserVerification:
    def test_browser_no_client_requires_observation(self):
        svc = VerificationService(browser_client=None)
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="browser.navigate",
            verification_strategy=VerificationStrategy.BROWSER_URL,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.REQUIRES_OBSERVATION


class TestScreenObservation:
    def test_pc_no_client_requires_observation(self):
        svc = VerificationService(pc_client=None)
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="pc.screenshot",
            verification_strategy=VerificationStrategy.PC_SCREEN_OBSERVATION,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.REQUIRES_OBSERVATION

    def test_android_no_client_requires_observation(self):
        svc = VerificationService(android_client=None)
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="android.screenshot",
            verification_strategy=VerificationStrategy.ANDROID_SCREEN_OBSERVATION,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.REQUIRES_OBSERVATION


class TestNoneVerification:
    def test_none_strategy_skipped(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1",
            request_id="r1",
            capability_id="unknown.cap",
            verification_strategy=VerificationStrategy.NONE,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.SKIPPED


class TestBuildRequest:
    def test_build_request_from_tool_data(self):
        svc = VerificationService()
        tool_req = type("ToolRequest", (), {
            "request_id": "r1",
            "task_id": "t1",
            "source": "desire_driven",
            "capability_id": "pc.write_file",
            "tool_name": "WriteFile",
            "arguments": {"path": "/tmp/test"},
        })()
        tool_result = type("ToolResult", (), {
            "output": {"path": "/tmp/test"},
        })()
        vr = svc.build_request(tool_req, tool_result)
        assert vr.request_id == "r1"
        assert vr.task_id == "t1"
        assert vr.verification_strategy == VerificationStrategy.FILE_EXISTS


class TestVerificationResult:
    def test_is_verified(self):
        r = VerificationResult(status=VerificationStatus.VERIFIED)
        assert r.is_verified is True
        assert r.is_failed is False
        assert r.needs_attention is False

    def test_is_failed(self):
        r = VerificationResult(status=VerificationStatus.FAILED)
        assert r.is_failed is True
        assert r.needs_attention is True

    def test_needs_attention(self):
        for status in [
            VerificationStatus.FAILED,
            VerificationStatus.UNVERIFIED,
            VerificationStatus.REQUIRES_OBSERVATION,
            VerificationStatus.ERROR,
        ]:
            r = VerificationResult(status=status)
            assert r.needs_attention is True

    def test_verified_fields(self):
        r = VerificationResult(
            verification_id="v1",
            request_id="r1",
            status=VerificationStatus.VERIFIED,
            confidence=0.9,
            reason="File exists",
            evidence=["exists=True"],
        )
        assert r.verification_id == "v1"
        assert r.confidence == 0.9
        assert len(r.evidence) == 1


class TestApiResponseSchema:
    def test_2xx_verified(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1", request_id="r1",
            capability_id="browser.api_call",
            execution_output={"status_code": 200, "data": {"id": 1}},
            verification_strategy=VerificationStrategy.API_RESPONSE_SCHEMA,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.VERIFIED

    def test_4xx_failed(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1", request_id="r1",
            capability_id="browser.api_call",
            execution_output={"status_code": 404},
            verification_strategy=VerificationStrategy.API_RESPONSE_SCHEMA,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.FAILED
        assert result.failure_type == "api_error"

    def test_error_in_body_failed(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1", request_id="r1",
            capability_id="browser.api_call",
            execution_output={"status_code": 200, "error": "something broke"},
            verification_strategy=VerificationStrategy.API_RESPONSE_SCHEMA,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.FAILED
        assert result.failure_type == "api_error_in_body"

    def test_missing_expected_keys_failed(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1", request_id="r1",
            capability_id="browser.api_call",
            arguments={"expected_keys": ["id", "name"]},
            execution_output={"status_code": 200, "id": 1},
            verification_strategy=VerificationStrategy.API_RESPONSE_SCHEMA,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.FAILED
        assert result.failure_type == "schema_mismatch"


class TestProcessRunning:
    def test_requires_observation(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1", request_id="r1",
            capability_id="pc.launch_app",
            verification_strategy=VerificationStrategy.PROCESS_RUNNING,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.REQUIRES_OBSERVATION


class TestStateDiff:
    def test_no_observation_requires_observation(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1", request_id="r1",
            capability_id="pc.click",
            verification_strategy=VerificationStrategy.STATE_DIFF,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.REQUIRES_OBSERVATION

    def test_changed_state_verified(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1", request_id="r1",
            capability_id="pc.click",
            pre_observation={"window": "Chrome", "title": "Google"},
            post_observation={"window": "Chrome", "title": "Search Results"},
            verification_strategy=VerificationStrategy.STATE_DIFF,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.VERIFIED
        assert "title" in result.evidence[0]

    def test_unchanged_state_failed(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1", request_id="r1",
            capability_id="pc.click",
            pre_observation={"window": "Chrome", "title": "Google"},
            post_observation={"window": "Chrome", "title": "Google"},
            verification_strategy=VerificationStrategy.STATE_DIFF,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.FAILED
        assert result.failure_type == "no_state_change"


class TestCustom:
    def test_custom_unverified(self):
        svc = VerificationService()
        req = VerificationRequest(
            verification_id="v1", request_id="r1",
            capability_id="custom.action",
            verification_strategy=VerificationStrategy.CUSTOM,
        )
        result = svc.verify(req)
        assert result.status == VerificationStatus.UNVERIFIED


class TestToolBrokerIntegration:
    def test_verification_status_in_result(self):
        from aegis_schema.models import Capability, RiskLevel, ServerType
        from tool_broker import ToolBroker, ExecutionSource, ToolExecutionRequest
        from tool_registry import ToolRegistry
        from policy_engine import create_default_policy_engine

        reg = ToolRegistry()
        reg.register_capability(Capability(
            id="pc.test", name="Test", description="Test",
            server_type=ServerType.PC, risk_level=RiskLevel.READ_ONLY,
        ))
        svc = VerificationService()
        broker = ToolBroker(reg, create_default_policy_engine(), verification_service=svc)
        req = ToolExecutionRequest(
            capability_id="pc.test", source=ExecutionSource.USER_EXPLICIT,
        )
        result = broker.execute(req)
        assert result.verification_status in ("skipped", "verified", "unverified", "pending")

    def test_desire_driven_audit_has_source_desire(self):
        from aegis_ai.audit import AuditLog
        from aegis_schema.models import Capability, RiskLevel, ServerType
        from tool_broker import ToolBroker, ExecutionSource, ToolExecutionRequest
        from tool_registry import ToolRegistry
        from policy_engine import create_default_policy_engine

        audit = AuditLog(path="data/test_v_audit.jsonl")
        reg = ToolRegistry()
        reg.register_capability(Capability(
            id="pc.test", name="Test", description="Test",
            server_type=ServerType.PC, risk_level=RiskLevel.READ_ONLY,
        ))
        broker = ToolBroker(reg, create_default_policy_engine(), audit_log=audit)
        req = ToolExecutionRequest(
            capability_id="pc.test",
            source=ExecutionSource.DESIRE_DRIVEN,
            source_desire="curiosity",
            frustration=5.0,
        )
        broker.execute(req)
        recent = audit.list_recent(5)
        found = [e for e in recent if e.detail.get("source_desire") == "curiosity"]
        assert len(found) >= 1
        assert found[0].detail.get("frustration") == 5.0


class TestAutonomousControllerVerification:
    def test_tick_verification_status_pending(self):
        from aegis_ai.autonomous.autonomous_controller import AutonomousController
        from aegis_ai.desire.desire_system import DesireSystem
        from aegis_ai.desire.intrinsic_task_generator import IntrinsicTaskGenerator
        from aegis_ai.autonomous.motivation_arbiter import MotivationArbiter

        d = tempfile.mkdtemp()
        try:
            desire = DesireSystem(data_dir=f"{d}/desires", initial_values={"curiosity": 0.0})
            gen = IntrinsicTaskGenerator(frustration_threshold=2.0, available_capabilities={"read_file"})
            arbiter = MotivationArbiter(available_capabilities={"read_file"})
            ctrl = AutonomousController(
                desire_system=desire, task_generator=gen, arbiter=arbiter,
                data_dir=f"{d}/ctrl",
            )
            result = ctrl.tick(now_ms=int(time.time() * 1000))
            if result.executed:
                assert result.verification_status == "pending"
            elif result.decision and result.decision.requires_approval:
                assert result.verification_status == "approval_required"
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_handle_verification_result_updates_desire(self):
        from aegis_ai.autonomous.autonomous_controller import AutonomousController
        from aegis_ai.desire.desire_system import DesireSystem
        from aegis_ai.desire.intrinsic_task_generator import IntrinsicTask

        d = tempfile.mkdtemp()
        try:
            desire = DesireSystem(data_dir=f"{d}/desires", initial_values={"reliability": 5.0})
            ctrl = AutonomousController(desire_system=desire, data_dir=f"{d}/ctrl")
            now = int(time.time() * 1000)
            task = IntrinsicTask(
                task_id="t1", source_desire="reliability", title="Test",
                description="", priority=0.5, expected_desire_effects={"reliability": 2.0},
                required_capabilities=[], risk_level=None,
                requires_user_approval=False, cooldown_seconds=0,
                created_at=now, reason="", fingerprint="fp-t1",
            )
            initial = desire.get_desire("reliability").value
            ctrl.handle_verification_result(task, "verified", "all good")
            assert desire.get_desire("reliability").value > initial
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_handle_verification_failed_decreases_desire(self):
        from aegis_ai.autonomous.autonomous_controller import AutonomousController
        from aegis_ai.desire.desire_system import DesireSystem
        from aegis_ai.desire.intrinsic_task_generator import IntrinsicTask

        d = tempfile.mkdtemp()
        try:
            desire = DesireSystem(data_dir=f"{d}/desires", initial_values={"reliability": 5.0})
            ctrl = AutonomousController(desire_system=desire, data_dir=f"{d}/ctrl")
            now = int(time.time() * 1000)
            task = IntrinsicTask(
                task_id="t1", source_desire="reliability", title="Test",
                description="", priority=0.5, expected_desire_effects={"reliability": 2.0},
                required_capabilities=[], risk_level=None,
                requires_user_approval=False, cooldown_seconds=0,
                created_at=now, reason="", fingerprint="fp-t1",
            )
            initial = desire.get_desire("reliability").value
            ctrl.handle_verification_result(task, "failed", "broken")
            assert desire.get_desire("reliability").value < initial
            assert "t1" in ctrl._recent_failures
        finally:
            shutil.rmtree(d, ignore_errors=True)
