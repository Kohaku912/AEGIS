"""E2E tests for TaskExecutionEngine — step execution after approval removal.

Approval is no longer a constraint (2026-09-27). These tests used to cover
"tool approval needed → task waiting_approval → approve → resume". They now
cover the replacement behaviour:

1. every step goes straight through ToolBroker (the egress gate is the boundary)
2. a step that pauses (requires observation) does not complete the task
3. an execution error fails the task
4. the engine exposes no approval surface at all
"""

from __future__ import annotations

import json
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
def engine(task_manager, mock_broker):
    from aegis_ai.agency.goal_service import GoalLifecycleService
    from aegis_ai.task.execution_engine import TaskExecutionEngine

    verifier = MagicMock()
    verifier.generate.return_value = MagicMock(
        success=True,
        content=json.dumps(
            {
                "status": "achieved",
                "reason": "Independent test evidence confirms the outcome.",
                "evidence": ["all planned steps produced successful results"],
            }
        ),
    )
    return TaskExecutionEngine(
        task_manager=task_manager,
        tool_broker=mock_broker,
        goal_service=GoalLifecycleService(
            task_manager=task_manager,
            llm_gateway=verifier,
        ),
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
        request_id="req_1",
    )


class TestApprovalIsGone:
    """Regression guards for the Phase 2 approval removal."""

    def test_engine_has_no_approval_surface(self):
        from aegis_ai.task.execution_engine import TaskExecutionEngine

        for name in (
            "resume_after_approval",
            "pause_for_approval",
            "_tool_request_from_approval",
            "_find_plan_step",
        ):
            assert not hasattr(TaskExecutionEngine, name), name

    def test_engine_constructor_rejects_approval_manager(self):
        from aegis_ai.task.execution_engine import TaskExecutionEngine

        with pytest.raises(TypeError):
            TaskExecutionEngine(task_manager=MagicMock(), approval_manager=MagicMock())

    def test_final_state_has_no_approval_member(self):
        from aegis_ai.task.execution_engine import TaskFinalState

        assert not hasattr(TaskFinalState, "HAS_NEEDS_APPROVAL")

    def test_step_status_has_no_approval_members(self):
        from aegis_ai.task_plan import StepStatus

        assert not hasattr(StepStatus, "NEEDS_APPROVAL")
        assert not hasattr(StepStatus, "APPROVED")

    def test_task_status_has_no_waiting_approval(self):
        from aegis_ai.task.task_manager import TaskStatus

        assert not hasattr(TaskStatus, "WAITING_APPROVAL")


class TestStepTransitions:
    def test_requires_observation_blocks_completion(self, task_manager):
        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        task_manager.add_step(task_id, "s1", "test step")
        task_manager.update_step_status(task_id, "s1", "running")
        task_manager.update_step_status(task_id, "s1", "requires_observation")

        result = task_manager.update_step_status(task_id, "s1", "completed")
        assert result is None

        step = task_manager.get_step(task_id, "s1")
        assert step["status"] == "requires_observation"


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

        engine.execute_task(task_id, plan)
        task_result = task_manager.get_task(task_id)
        assert task_result["status"] == "completed"
        assert mock_broker.execute.call_count == 2

    def test_failed_step_fails_task(self, engine, task_manager, mock_broker):
        mock_broker.execute.return_value = MagicMock(
            success=False,
            status=InvokeStatus.EXECUTION_ERROR,
            output={},
            error="tool failed",
            request_id="req_1",
        )

        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        plan = _make_plan()
        engine.execute_task(task_id, plan)

        task_result = task_manager.get_task(task_id)
        assert task_result["status"] == "failed"

    def test_cancel_task(self, engine, task_manager):
        task = task_manager.create_task(title="test", source="test")
        task_id = task["task_id"]
        task_manager.start_task(task_id)

        engine.cancel_task(task_id, reason="user cancelled")
        task_result = task_manager.get_task(task_id)
        assert task_result["status"] == "cancelled"
