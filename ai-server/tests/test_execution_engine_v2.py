"""E2E tests for TaskExecutionEngine - multi-step approval flow."""

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


def _success_result():
    return MagicMock(
        success=True,
        status=InvokeStatus.SUCCESS,
        output={'result': 'ok'},
        error='',
        approval_id='',
        request_id='req_1',
    )


def _approval_result(approval_id='appr_test_1'):
    return MagicMock(
        success=False,
        status=InvokeStatus.APPROVAL_NEEDED,
        error='needs approval',
        approval_id=approval_id,
        request_id='req_1',
        output={},
    )


def _fail_result(error='tool failed'):
    return MagicMock(
        success=False,
        status=InvokeStatus.EXECUTION_ERROR,
        output={},
        error=error,
        approval_id='',
        request_id='req_1',
    )


class TestMultiStepApproval:
    def test_multi_step_with_approval(self, engine, task_manager, mock_broker, mock_approval_manager):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        approval_id = 'appr_multi_1'
        call_count = [0]
        def side_effect(request):
            call_count[0] += 1
            if call_count[0] == 1:
                return _success_result()
            elif call_count[0] == 2:
                return _approval_result(approval_id)
            else:
                return _success_result()
        mock_broker.execute.side_effect = side_effect
        task = task_manager.create_task(title='multi-step', source='test')
        task_id = task['task_id']
        task_manager.start_task(task_id)
        plan = TaskPlan(
            plan_id='plan_multi',
            interpreted_request='multi step test',
            steps=[
                PlanStep(step_id='s1', description='step 1', action_type='tool_invoke', capability_id='test.a'),
                PlanStep(step_id='s2', description='step 2', action_type='tool_invoke', capability_id='test.b'),
                PlanStep(step_id='s3', description='step 3', action_type='tool_invoke', capability_id='test.c'),
            ],
        )
        response = engine.execute_task(task_id, plan)
        assert 'APPROVAL' in response.text
        task_result = task_manager.get_task(task_id)
        assert task_result['status'] == 'waiting_approval'
        assert task_result['waiting_approval_step_id'] == 's2'
        assert task_result['waiting_approval_id'] == approval_id
        from aegis_ai.approval.approval_types import compute_args_hash
        mock_approval_manager.get.return_value = MagicMock(
            status='approved',
            task_id=task_id,
            step_id='s2',
            capability_id='test.b',
            arguments={'key': 'value'},
            tool_args_hash=compute_args_hash({'key': 'value'}),
        )
        mock_broker.execute_approved.return_value = _success_result()
        response = engine.resume_after_approval(approval_id)
        task_result = task_manager.get_task(task_id)
        assert task_result['status'] == 'completed'
        s1 = task_manager.get_step(task_id, 's1')
        s2 = task_manager.get_step(task_id, 's2')
        s3 = task_manager.get_step(task_id, 's3')
        assert s1['status'] == 'completed'
        assert s2['status'] == 'completed'
        assert s3['status'] == 'completed'

    def test_reject_cancels_task(self, engine, task_manager, mock_broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        mock_broker.execute.return_value = _approval_result('appr_reject')
        task = task_manager.create_task(title='reject test', source='test')
        task_id = task['task_id']
        task_manager.start_task(task_id)
        plan = TaskPlan(
            plan_id='plan_reject',
            interpreted_request='reject test',
            steps=[PlanStep(step_id='s1', description='step 1', action_type='tool_invoke', capability_id='test.a')],
        )
        engine.execute_task(task_id, plan)
        task_manager.fail_task(task_id, error='Approval rejected')
        task_result = task_manager.get_task(task_id)
        assert task_result['status'] == 'failed'


class TestTamperedArgs:
    def test_tampered_args_detected(self, engine, task_manager, mock_broker, mock_approval_manager):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        from aegis_ai.approval.approval_types import compute_args_hash
        mock_broker.execute.return_value = _approval_result('appr_tamper')
        task = task_manager.create_task(title='tamper test', source='test')
        task_id = task['task_id']
        task_manager.start_task(task_id)
        plan = TaskPlan(
            plan_id='plan_tamper',
            interpreted_request='tamper test',
            steps=[PlanStep(step_id='s1', description='step 1', action_type='tool_invoke', capability_id='test.a')],
        )
        engine.execute_task(task_id, plan)
        mock_approval_manager.get.return_value = MagicMock(
            status='approved',
            task_id=task_id,
            step_id='s1',
            capability_id='test.a',
            arguments={'key': 'tampered'},
            tool_args_hash=compute_args_hash({'key': 'original'}),
        )
        response = engine.resume_after_approval('appr_tamper')
        assert 'DENIED' in response.text or 'tampered' in response.text.lower()
        mock_broker.execute_approved.assert_not_called()


class TestPlanPersistence:
    def test_plan_saved_on_execute(self, engine, task_manager, mock_broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        mock_broker.execute.return_value = _success_result()
        task = task_manager.create_task(title='persist test', source='test')
        task_id = task['task_id']
        task_manager.start_task(task_id)
        plan = TaskPlan(
            plan_id='plan_persist',
            interpreted_request='persist test',
            steps=[PlanStep(step_id='s1', description='step 1', action_type='tool_invoke', capability_id='test.a')],
        )
        engine.execute_task(task_id, plan)
        plan_json = task_manager.get_plan_json(task_id)
        assert plan_json != ''
        data = json.loads(plan_json)
        assert data['plan_id'] == 'plan_persist'
        assert len(data['steps']) == 1


class TestContinueTask:
    def test_continue_after_approval(self, engine, task_manager, mock_broker, mock_approval_manager):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        from aegis_ai.approval.approval_types import compute_args_hash
        call_count = [0]
        def side_effect(request):
            call_count[0] += 1
            if call_count[0] == 1:
                return _success_result()
            elif call_count[0] == 2:
                return _approval_result('appr_cont')
            else:
                return _success_result()
        mock_broker.execute.side_effect = side_effect
        task = task_manager.create_task(title='continue test', source='test')
        task_id = task['task_id']
        task_manager.start_task(task_id)
        plan = TaskPlan(
            plan_id='plan_cont',
            interpreted_request='continue test',
            steps=[
                PlanStep(step_id='s1', description='step 1', action_type='tool_invoke', capability_id='test.a'),
                PlanStep(step_id='s2', description='step 2', action_type='tool_invoke', capability_id='test.b'),
                PlanStep(step_id='s3', description='step 3', action_type='tool_invoke', capability_id='test.c'),
            ],
        )
        engine.execute_task(task_id, plan)
        mock_approval_manager.get.return_value = MagicMock(
            status='approved',
            task_id=task_id,
            step_id='s2',
            capability_id='test.b',
            arguments={'key': 'value'},
            tool_args_hash=compute_args_hash({'key': 'value'}),
        )
        mock_broker.execute_approved.return_value = _success_result()
        engine.resume_after_approval('appr_cont')
        task_result = task_manager.get_task(task_id)
        assert task_result['status'] == 'completed'
        assert task_manager.get_step(task_id, 's3')['status'] == 'completed'
