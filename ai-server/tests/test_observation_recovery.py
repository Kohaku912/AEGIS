"""Tests for Observation and Recovery modules."""

from __future__ import annotations

import shutil
import tempfile

import pytest

from aegis_ai.observation.multimodal_state_analyzer import (
    MultimodalStateAnalyzer,
    StateAnalysisResult,
)
from aegis_ai.observation.observation_service import MultimodalObservationService
from aegis_ai.observation.observation_types import (
    DetectedElement,
    ElementKind,
    ElementSource,
    ObservationPurpose,
    ObservationRequest,
    ObservationResult,
    ObservationStatus,
    ObservationTarget,
)
from aegis_ai.recovery.recovery_planner import (
    FailureType,
    RecoveryAction,
    RecoveryPlanner,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestObservationTypes:
    def test_observation_request_creation(self):
        req = ObservationRequest(
            observation_id="obs1",
            task_id="t1",
            target=ObservationTarget.BROWSER,
            purpose=ObservationPurpose.POST_ACTION,
        )
        assert req.observation_id == "obs1"
        assert req.target == ObservationTarget.BROWSER
        assert req.purpose == ObservationPurpose.POST_ACTION

    def test_observation_request_to_dict(self):
        req = ObservationRequest(
            observation_id="obs1",
            task_id="t1",
            target=ObservationTarget.PC,
            purpose=ObservationPurpose.PRE_ACTION,
        )
        d = req.to_dict()
        assert d["observation_id"] == "obs1"
        assert d["target"] == "pc"
        assert d["purpose"] == "pre_action"

    def test_observation_result_creation(self):
        result = ObservationResult(
            observation_id="obs1",
            target=ObservationTarget.BROWSER,
            status=ObservationStatus.SUCCESS,
            current_url="https://example.com",
            page_title="Example",
        )
        assert result.observation_id == "obs1"
        assert result.status == ObservationStatus.SUCCESS

    def test_observation_result_to_dict_masks_secrets(self):
        result = ObservationResult(
            observation_id="obs1",
            visible_text_summary="api_key=sk-abcdef1234567890abcdef1234567890",
        )
        d = result.to_dict()
        assert "sk-***" in d["visible_text_summary"] or "***MASKED***" in d["visible_text_summary"]

    def test_observation_result_to_context_string(self):
        result = ObservationResult(
            observation_id="obs1",
            target=ObservationTarget.BROWSER,
            status=ObservationStatus.SUCCESS,
            current_url="https://example.com",
            page_title="Example",
            detected_elements=[
                DetectedElement(element_id="btn1", kind=ElementKind.BUTTON, label="Submit", clickable=True),
                DetectedElement(element_id="err1", kind=ElementKind.ERROR_MESSAGE, text="Invalid input"),
            ],
        )
        ctx = result.to_context_string()
        assert "browser" in ctx
        assert "example.com" in ctx
        assert "Submit" in ctx

    def test_detected_element_creation(self):
        elem = DetectedElement(
            element_id="btn1",
            kind=ElementKind.BUTTON,
            label="Click me",
            text="Click me",
            confidence=0.95,
            source=ElementSource.DOM,
            clickable=True,
        )
        assert elem.element_id == "btn1"
        assert elem.kind == ElementKind.BUTTON
        assert elem.clickable is True

    def test_detected_element_to_dict(self):
        elem = DetectedElement(
            element_id="btn1",
            kind=ElementKind.BUTTON,
            label="Submit",
        )
        d = elem.to_dict()
        assert d["element_id"] == "btn1"
        assert d["kind"] == "button"


class TestObservationService:
    def test_observe_browser_no_client(self):
        svc = MultimodalObservationService(browser_client=None)
        req = ObservationRequest(
            target=ObservationTarget.BROWSER,
            purpose=ObservationPurpose.POST_ACTION,
        )
        result = svc.observe(req)
        assert result.status == ObservationStatus.UNAVAILABLE

    def test_observe_pc_no_client(self):
        svc = MultimodalObservationService(pc_client=None)
        req = ObservationRequest(
            target=ObservationTarget.PC,
            purpose=ObservationPurpose.POST_ACTION,
        )
        result = svc.observe(req)
        assert result.status == ObservationStatus.UNAVAILABLE

    def test_observe_android_no_client(self):
        svc = MultimodalObservationService(android_client=None)
        req = ObservationRequest(
            target=ObservationTarget.ANDROID,
            purpose=ObservationPurpose.POST_ACTION,
        )
        result = svc.observe(req)
        assert result.status == ObservationStatus.UNAVAILABLE

    def test_observe_generates_id(self):
        svc = MultimodalObservationService()
        req = ObservationRequest(target=ObservationTarget.PC)
        result = svc.observe(req)
        assert result.observation_id

    def test_summarize(self):
        svc = MultimodalObservationService()
        result = ObservationResult(
            target=ObservationTarget.BROWSER,
            status=ObservationStatus.SUCCESS,
            current_url="https://example.com",
        )
        summary = svc.summarize(result)
        assert "example.com" in summary

    def test_diff_detects_url_change(self):
        svc = MultimodalObservationService()
        before = ObservationResult(
            observation_id="obs1",
            current_url="https://old.com",
        )
        after = ObservationResult(
            observation_id="obs2",
            current_url="https://new.com",
        )
        diff = svc.diff(before, after)
        assert diff.url_changed is True
        assert diff.changed is True

    def test_diff_detects_no_change(self):
        svc = MultimodalObservationService()
        result = ObservationResult(
            observation_id="obs1",
            current_url="https://example.com",
            visible_text_summary="hello",
        )
        diff = svc.diff(result, result)
        assert diff.changed is False

    def test_diff_detects_new_errors(self):
        svc = MultimodalObservationService()
        before = ObservationResult(observation_id="obs1")
        after = ObservationResult(
            observation_id="obs2",
            detected_elements=[
                DetectedElement(element_id="err1", kind=ElementKind.ERROR_MESSAGE, text="Something broke"),
            ],
        )
        diff = svc.diff(before, after)
        assert "Something broke" in diff.new_error_messages

    def test_redact_sensitive(self):
        svc = MultimodalObservationService()
        result = ObservationResult(
            observation_id="obs1",
            visible_text_summary="password=secret123 api_key=sk-abcdef1234567890abcdef1234567890",
            dom_summary="<input type='password' value='secret'>",
        )
        redacted = svc.redact_sensitive(result)
        assert "secret123" not in redacted.visible_text_summary
        assert len(redacted.redactions) > 0

    def test_build_multimodal_context(self):
        svc = MultimodalObservationService()
        result = ObservationResult(
            observation_id="obs1",
            target=ObservationTarget.BROWSER,
            status=ObservationStatus.SUCCESS,
            current_url="https://example.com",
            page_title="Example",
            visible_text_summary="Hello world",
            detected_elements=[
                DetectedElement(element_id="btn1", kind=ElementKind.BUTTON, label="Submit", clickable=True),
            ],
        )
        ctx = svc.build_multimodal_context(result)
        assert "example.com" in ctx
        assert "Submit" in ctx

    def test_observe_with_mock_browser_client(self):
        class MockBrowserClient:
            def get_current_url(self):
                return "https://example.com"
            def get_page_title(self):
                return "Example"
            def get_page_text(self):
                return "Hello world"

        svc = MultimodalObservationService(browser_client=MockBrowserClient())
        req = ObservationRequest(target=ObservationTarget.BROWSER)
        result = svc.observe(req)
        assert result.status == ObservationStatus.SUCCESS
        assert result.current_url == "https://example.com"
        assert result.page_title == "Example"


class TestMultimodalStateAnalyzer:
    def test_fallback_analysis_without_llm(self):
        analyzer = MultimodalStateAnalyzer(llm_client=None)
        result = analyzer.analyze(
            observation_summary="Page shows a form with submit button",
            action_goal="Submit the form",
        )
        assert result.analysis_id
        assert result.confidence < 0.5
        assert "form" in result.state_summary.lower() or "submit" in result.state_summary.lower()

    def test_analysis_result_to_dict(self):
        result = StateAnalysisResult(
            analysis_id="sa1",
            state_summary="Form visible",
            success_signals=["success message"],
            failure_signals=["error dialog"],
            confidence=0.8,
        )
        d = result.to_dict()
        assert d["analysis_id"] == "sa1"
        assert d["confidence"] == 0.8

    def test_build_context_for_recovery(self):
        analyzer = MultimodalStateAnalyzer()
        analysis = StateAnalysisResult(
            state_summary="Error dialog visible",
            failure_signals=["timeout error"],
            blocking_issues=["modal dialog"],
            next_safe_actions=["close dialog"],
        )
        ctx = analyzer.build_context_for_recovery(analysis)
        assert "timeout" in ctx or "dialog" in ctx

    def test_analysis_with_mock_llm(self):
        mock_json = (
            '{"state_summary": "Login form visible", '
            '"task_relevant_elements": ["username", "password"], '
            '"current_progress": "At login", "success_signals": [], '
            '"failure_signals": ["login required"], '
            '"blocking_issues": ["authentication"], '
            '"next_safe_actions": ["ask user to login"], '
            '"requires_user_help": true, "sensitivity_flags": [], '
            '"confidence": 0.85}'
        )

        class MockLLM:
            class Result:
                success = True
                content = mock_json

            def generate(self, **kwargs):
                return self.Result()

        analyzer = MultimodalStateAnalyzer(llm_client=MockLLM())
        result = analyzer.analyze(
            observation_summary="Login form visible",
            action_goal="Navigate to dashboard",
        )
        assert result.state_summary == "Login form visible"
        assert result.requires_user_help is True
        assert result.confidence == 0.85

    def test_analysis_with_failed_llm(self):
        class FailingLLM:
            class Result:
                success = False
                error = "API error"
            def generate(self, **kwargs):
                return self.Result()

        analyzer = MultimodalStateAnalyzer(llm_client=FailingLLM())
        result = analyzer.analyze(observation_summary="Something")
        assert result.confidence < 0.5


class TestRecoveryPlanner:
    def test_element_not_found_recovery(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="browser.click",
            failure_type="element_not_found",
        )
        assert plan.failure_type == FailureType.ELEMENT_NOT_FOUND
        assert plan.should_retry is True
        assert len(plan.safe_recovery_steps) > 0

    def test_login_required_recovery(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="browser.navigate",
            failure_type="login_required",
        )
        assert plan.failure_type == FailureType.LOGIN_REQUIRED
        assert plan.requires_user_help is True
        assert plan.should_retry is False

    def test_captcha_blocked_recovery(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="browser.submit",
            failure_type="captcha_blocked",
        )
        assert plan.failure_type == FailureType.CAPTCHA_BLOCKED
        assert plan.requires_user_help is True
        assert plan.should_retry is False

    def test_send_failed_no_auto_retry(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="browser.send_message",
            failure_type="send_failed",
        )
        assert plan.should_retry is False
        assert plan.requires_user_help is True

    def test_timeout_recovery(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="pc.click",
            failure_type="timeout",
        )
        assert plan.failure_type == FailureType.TIMEOUT
        assert plan.should_retry is True

    def test_risky_operation_requires_approval(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="browser.submit_payment",
            failure_type="element_not_found",
        )
        assert plan.requires_approval is True

    def test_exceeded_retry_limit(self):
        planner = RecoveryPlanner(max_retries=2)
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="pc.click",
            failure_type="element_not_found",
            retry_count=5,
        )
        assert plan.should_retry is False

    def test_recovery_plan_to_dict(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="browser.click",
            failure_type="element_not_found",
        )
        d = plan.to_dict()
        assert d["task_id"] == "t1"
        assert d["failure_type"] == "element_not_found"

    def test_unknown_failure_stops(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="unknown.cap",
            failure_type="totally_unknown",
        )
        assert plan.failure_type == FailureType.UNKNOWN
        assert plan.should_retry is False
        assert plan.requires_user_help is True

    def test_permission_denied_recovery(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="pc.write_file",
            failure_type="permission_denied",
        )
        assert plan.failure_type == FailureType.PERMISSION_DENIED
        assert plan.requires_approval is True
        assert plan.should_retry is False

    def test_app_not_running_recovery(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="android.tap",
            failure_type="app_not_running",
        )
        assert plan.failure_type == FailureType.APP_NOT_RUNNING
        assert plan.should_retry is True

    def test_error_dialog_recovery(self):
        planner = RecoveryPlanner()
        plan = planner.plan_recovery(
            task_id="t1",
            request_id="r1",
            capability_id="pc.click",
            failure_type="error_dialog",
            error_message="Application error occurred",
        )
        assert plan.failure_type == FailureType.ERROR_DIALOG
        assert any(s.action == RecoveryAction.CLOSE_DIALOG for s in plan.safe_recovery_steps)
