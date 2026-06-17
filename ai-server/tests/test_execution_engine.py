"""E2E tests for TaskExecutionEngine — approval-aware step execution.

Tests cover:
1. user request → task created → tool approval needed → task waiting_approval
2. approve → same step resumes → task completed
3. reject → task failed
4. approval waiting task not accidentally completed
5. tampered tool args detected after approval
"""

from __future__ import annotations

import tempfile
from unittest.mock import MagicMock

import pytest

from tool_broker import InvokeStatus


@pytest.fixture
def task_manager():
    from aegis_ai.task.task_manager import TaskManager
    return TaskManager(data_dir=tempfile.mkdtemp())


@pytest.fixture
def mock_broker():
    return MagicMock()


@pytest.fixture
def mock_approval_manager():
    return MagicMock()


@pytest.fixture
def engine(task_manager, mock_broker, mock_approval_manager):
    from aegis_ai.task.execution_engine import TaskExecutionEngine
    return TaskExecutionEngine(
        task_manager=task_manager,
        tool_broker=mock_broker,
        approval_manager=mock_approval_manager,
    )


def _make_plan(capability_id="test.cap", action_type="tool_invoke"):
    from aegis_ai.task_plan import PlanStep, TaskPlan
    return TaskPlan(
        plan_id="plan_1",
        interpreted_request="test request",
        steps=[
            PlanStep(
                step_id="s1",
                description="test step",
                action_type=action_type,
                capability_id=capability_id,
                params={"key": "value"},
            ),
        ],
    )


def _success_result():
    return MagicMock(
        success=True,
        status=InvokeStatus.SUCCESS,
        output={"result": "ok"},
        error="",
        approval_id="",
        request_id="req_1",
    )


def _approval_result(approval_id="appr_test_1"):
    return MagicMock(
        success=False,
        status=InvokeStatus.APPROVAL_NEEDED,
        error="needs approval",
        approval_id=approval_id,
        request_id="req_1",
        output={},
    )


class TestApprovalFlow:
    def test_approval_needed_task_waiting(self, engine, task_manager, mock_broker):
        mock_broker.execute.return_value = _approval_result()
        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        plan = _make_plan()
        response = engine.execute_task(task_id, plan)

        task_result = task_manager.get_task(task_id)
        assert task_result["status"] == "waiting_approval"
        assert "APPROVAL" in response.text

    def test_approve_then_complete(self, engine, task_manager, mock_broker, mock_approval_manager):
        approval_id = "appr_resume_1"
        mock_broker.execute.return_value = _approval_result(approval_id)

        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        plan = _make_plan()
        engine.execute_task(task_id, plan)

        mock_approval_manager.get.return_value = MagicMock(
            status="approved",
            task_id=task_id,
            step_id="s1",
            capability_id="test.cap",
            arguments={"key": "value"},
            tool_args_hash="abc123",
        )
        mock_broker.execute_approved.return_value = _success_result()

        from aegis_ai.approval.approval_types import compute_args_hash
        mock_approval_manager.get.return_value.tool_args_hash = compute_args_hash({"key": "value"})

        response = engine.resume_after_approval(approval_id)

        task_result = task_manager.get_task(task_id)
        assert task_result["status"] == "completed"
        assert "completed" in response.text.lower() or "ok" in response.text.lower()

    def test_reject_task_failed(self, engine, task_manager, mock_broker, mock_approval_manager):
        approval_id = "appr_reject_1"
        mock_broker.execute.return_value = _approval_result(approval_id)

        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        plan = _make_plan()
        engine.execute_task(task_id, plan)

        task_manager.fail_task(task_id, error="Approval rejected")
        task_result = task_manager.get_task(task_id)
        assert task_result["status"] == "failed"


class TestApprovalNotCompleted:
    def test_waiting_approval_cannot_complete(self, task_manager):
        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)
        task_manager.wait_for_approval(task_id, "s1", "appr_1")

        result = task_manager.complete_task(task_id)
        assert result is None
        task_result = task_manager.get_task(task_id)
        assert task_result["status"] == "waiting_approval"

    def test_step_transitions_enforced(self, task_manager):
        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        task_manager.add_step(task_id, "s1", "test step")
        task_manager.update_step_status(task_id, "s1", "running")
        task_manager.update_step_status(task_id, "s1", "needs_approval")

        result = task_manager.update_step_status(task_id, "s1", "completed")
        assert result is None

        step = task_manager.get_step(task_id, "s1")
        assert step["status"] == "needs_approval"


class TestTamperedArgs:
    def test_tampered_args_detected(self, engine, task_manager, mock_broker, mock_approval_manager):
        approval_id = "appr_tamper_1"
        mock_broker.execute.return_value = _approval_result(approval_id)

        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        plan = _make_plan()
        engine.execute_task(task_id, plan)

        from aegis_ai.approval.approval_types import compute_args_hash
        mock_approval_manager.get.return_value = MagicMock(
            status="approved",
            task_id=task_id,
            step_id="s1",
            capability_id="test.cap",
            arguments={"key": "tampered_value"},
            tool_args_hash=compute_args_hash({"key": "original_value"}),
        )

        response = engine.resume_after_approval(approval_id)

        assert "DENIED" in response.text or "tampered" in response.text.lower()
        mock_broker.execute_approved.assert_not_called()


class TestTaskExecution:
    def test_all_steps_complete_task_completed(self, engine, task_manager, mock_broker):
        mock_broker.execute.return_value = _success_result()

        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        from aegis_ai.task_plan import PlanStep, TaskPlan
        plan = TaskPlan(
            plan_id="plan_1",
            interpreted_request="test",
            steps=[
                PlanStep(step_id="s1", description="step 1", action_type="tool_invoke", capability_id="test.a"),
                PlanStep(step_id="s2", description="step 2", action_type="tool_invoke", capability_id="test.b"),
            ],
        )

        response = engine.execute_task(task_id, plan)
        task_result = task_manager.get_task(task_id)
        assert task_result["status"] == "completed"
        assert mock_broker.execute.call_count == 2

    def test_failed_step_fails_task(self, engine, task_manager, mock_broker):
        mock_broker.execute.return_value = MagicMock(
            success=False,
            status=InvokeStatus.EXECUTION_ERROR,
            output={},
            error="tool failed",
            approval_id="",
            request_id="req_1",
        )

        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        plan = _make_plan()
        response = engine.execute_task(task_id, plan)

        task_result = task_manager.get_task(task_id)
        assert task_result["status"] == "failed"

    def test_cancel_task(self, engine, task_manager, mock_broker):
        mock_broker.execute.return_value = _approval_result()

        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        plan = _make_plan()
        engine.execute_task(task_id, plan)

        engine.cancel_task(task_id, reason="user cancelled")
        task_result = task_manager.get_task(task_id)
        assert task_result["status"] == "cancelled"
