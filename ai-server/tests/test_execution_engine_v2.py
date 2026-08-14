# -*- coding: utf-8 -*-
'''E2E tests for TaskExecutionEngine - multi-step approval flow.'''

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
    from aegis_ai.agency.goal_service import GoalLifecycleService
    from aegis_ai.task.execution_engine import TaskExecutionEngine
    verifier = MagicMock()
    verifier.generate.return_value = MagicMock(
        success=True,
        content=json.dumps({
            "status": "achieved",
            "reason": "Independent test evidence confirms the outcome.",
            "evidence": ["all planned steps produced successful results"],
        }),
    )
    return TaskExecutionEngine(
        task_manager=task_manager,
        tool_broker=mock_broker,
        approval_manager=mock_approval_manager,
        goal_service=GoalLifecycleService(
            task_manager=task_manager,
            llm_gateway=verifier,
        ),
    )


def _success():
    return MagicMock(success=True, status=InvokeStatus.SUCCESS, output={'r': 'ok'}, error='', approval_id='', request_id='r1')


def _approval(aid='appr_1'):
    return MagicMock(success=False, status=InvokeStatus.APPROVAL_NEEDED, error='needs approval', approval_id=aid, request_id='r1', output={})


def _fail(msg='fail'):
    return MagicMock(success=False, status=InvokeStatus.EXECUTION_ERROR, output={}, error=msg, approval_id='', request_id='r1')


class TestMultiStepApproval:
    def test_approval_not_completed(self, engine, task_manager, mock_broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        mock_broker.execute.side_effect = [_success(), _approval('appr_x')]
        task = task_manager.create_task(title='t', source='test')
        tid = task['task_id']
        task_manager.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='s1', action_type='tool_invoke', capability_id='a.b'),
            PlanStep(step_id='s2', description='s2', action_type='tool_invoke', capability_id='a.c'),
            PlanStep(step_id='s3', description='s3', action_type='tool_invoke', capability_id='a.d'),
        ])
        engine.execute_task(tid, plan)
        t = task_manager.get_task(tid)
        assert t['status'] == 'waiting_approval'
        assert t['waiting_approval_step_id'] == 's2'
        assert t['waiting_approval_id'] == 'appr_x'

    def test_resume_then_continue(self, engine, task_manager, mock_broker, mock_approval_manager):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        from aegis_ai.approval.approval_types import compute_args_hash
        mock_broker.execute.side_effect = [_success(), _approval('appr_y'), _success()]
        task = task_manager.create_task(title='t', source='test')
        tid = task['task_id']
        task_manager.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='s1', action_type='tool_invoke', capability_id='a.b'),
            PlanStep(step_id='s2', description='s2', action_type='tool_invoke', capability_id='a.c'),
            PlanStep(step_id='s3', description='s3', action_type='tool_invoke', capability_id='a.d'),
        ])
        engine.execute_task(tid, plan)
        args = {'key': 'value'}
        mock_approval_manager.get.return_value = MagicMock(
            status='approved', task_id=tid, step_id='s2', capability_id='a.c',
            arguments=args, tool_args_hash=compute_args_hash(args),
        )
        mock_broker.execute_approved.return_value = _success()
        engine.resume_after_approval('appr_y')
        t = task_manager.get_task(tid)
        assert t['status'] == 'completed'
        assert task_manager.get_step(tid, 's1')['status'] == 'completed'
        assert task_manager.get_step(tid, 's2')['status'] == 'completed'
        assert task_manager.get_step(tid, 's3')['status'] == 'completed'

    def test_reject_fails_task(self, engine, task_manager, mock_broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        mock_broker.execute.return_value = _approval('appr_z')
        task = task_manager.create_task(title='t', source='test')
        tid = task['task_id']
        task_manager.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='s1', action_type='tool_invoke', capability_id='a.b'),
        ])
        engine.execute_task(tid, plan)
        task_manager.fail_task(tid, error='rejected')
        assert task_manager.get_task(tid)['status'] == 'failed'


class TestTamperedArgs:
    def test_tampered_args_denied(self, engine, task_manager, mock_broker, mock_approval_manager):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        from aegis_ai.approval.approval_types import compute_args_hash
        mock_broker.execute.return_value = _approval('appr_t')
        task = task_manager.create_task(title='t', source='test')
        tid = task['task_id']
        task_manager.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='s1', action_type='tool_invoke', capability_id='a.b'),
        ])
        engine.execute_task(tid, plan)
        mock_approval_manager.get.return_value = MagicMock(
            status='approved', task_id=tid, step_id='s1', capability_id='a.b',
            arguments={'k': 'tampered'}, tool_args_hash=compute_args_hash({'k': 'original'}),
        )
        resp = engine.resume_after_approval('appr_t')
        assert 'DENIED' in resp.text or 'tampered' in resp.text.lower()
        mock_broker.execute_approved.assert_not_called()


class TestPlanPersistence:
    def test_from_dict_roundtrip(self):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        plan = TaskPlan(plan_id='p1', interpreted_request='test', expected_result='ok', steps=[
            PlanStep(step_id='s1', description='desc', action_type='tool_invoke', capability_id='a.b',
                     params={'x': 1}, depends_on=['s0'], expected_result='r1'),
        ])
        d = plan.to_dict()
        plan2 = TaskPlan.from_dict(d)
        assert plan2.plan_id == 'p1'
        assert plan2.interpreted_request == 'test'
        assert plan2.expected_result == 'ok'
        assert len(plan2.steps) == 1
        s = plan2.steps[0]
        assert s.step_id == 's1'
        assert s.params == {'x': 1}
        assert s.depends_on == ['s0']
        assert s.expected_result == 'r1'
        assert s.action_type == 'tool_invoke'

    def test_plan_saved_and_restored(self, engine, task_manager, mock_broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        mock_broker.execute.return_value = _success()
        task = task_manager.create_task(title='t', source='test')
        tid = task['task_id']
        task_manager.start_task(tid)
        plan = TaskPlan(plan_id='p_rest', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='d1', action_type='tool_invoke', capability_id='a.b', params={'k': 'v'}, depends_on=[]),
        ])
        engine.execute_task(tid, plan)
        pj = task_manager.get_plan_json(tid)
        assert pj != ''
        data = json.loads(pj)
        restored = TaskPlan.from_dict(data)
        assert restored.steps[0].params == {'k': 'v'}
        assert restored.steps[0].depends_on == []

