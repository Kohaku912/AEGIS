# -*- coding: utf-8 -*-
'''Completion condition and execution path tests for TaskExecutionEngine.'''

from __future__ import annotations

import json
import tempfile
from unittest.mock import MagicMock

import pytest
from tool_broker import InvokeStatus


@pytest.fixture
def tm():
    from aegis_ai.task.task_manager import TaskManager
    return TaskManager(data_dir=tempfile.mkdtemp())


@pytest.fixture
def broker():
    return MagicMock()


@pytest.fixture
def am():
    return MagicMock()


@pytest.fixture
def engine(tm, broker, am):
    from aegis_ai.task.execution_engine import TaskExecutionEngine
    return TaskExecutionEngine(task_manager=tm, tool_broker=broker, approval_manager=am)


def _ok():
    return MagicMock(success=True, status=InvokeStatus.SUCCESS, output={'r': 'ok'}, error='', approval_id='', request_id='r1')


def _appr(aid='appr_1'):
    return MagicMock(success=False, status=InvokeStatus.APPROVAL_NEEDED, error='needs approval', approval_id=aid, request_id='r1', output={})


def _fail(msg='fail'):
    return MagicMock(success=False, status=InvokeStatus.EXECUTION_ERROR, output={}, error=msg, approval_id='', request_id='r1')


class TestCompletionConditions:
    def test_all_completed_only(self, engine, tm, broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        broker.execute.return_value = _ok()
        t = tm.create_task(title='t', source='test')
        tid = t['task_id']
        tm.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='d', action_type='tool_invoke', capability_id='a.b'),
            PlanStep(step_id='s2', description='d', action_type='tool_invoke', capability_id='a.c'),
        ])
        engine.execute_task(tid, plan)
        assert tm.get_task(tid)['status'] == 'completed'

    def test_approval_not_completed(self, engine, tm, broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        broker.execute.side_effect = [_ok(), _appr('appr_x')]
        t = tm.create_task(title='t', source='test')
        tid = t['task_id']
        tm.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='d', action_type='tool_invoke', capability_id='a.b'),
            PlanStep(step_id='s2', description='d', action_type='tool_invoke', capability_id='a.c'),
            PlanStep(step_id='s3', description='d', action_type='tool_invoke', capability_id='a.d'),
        ])
        engine.execute_task(tid, plan)
        assert tm.get_task(tid)['status'] == 'waiting_approval'

    def test_pending_not_completed(self, engine, tm, broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        broker.execute.return_value = _ok()
        t = tm.create_task(title='t', source='test')
        tid = t['task_id']
        tm.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='d', action_type='tool_invoke', capability_id='a.b'),
            PlanStep(step_id='s2', description='d', action_type='info'),
        ])
        engine.execute_task(tid, plan)
        task = tm.get_task(tid)
        assert task['status'] != 'completed'

    def test_failed_goes_failed(self, engine, tm, broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        broker.execute.side_effect = [_ok(), _fail('err')]
        t = tm.create_task(title='t', source='test')
        tid = t['task_id']
        tm.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='d', action_type='tool_invoke', capability_id='a.b'),
            PlanStep(step_id='s2', description='d', action_type='tool_invoke', capability_id='a.c'),
        ])
        engine.execute_task(tid, plan)
        assert tm.get_task(tid)['status'] == 'failed'

    def test_dependency_not_completed(self, engine, tm, broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        broker.execute.return_value = _ok()
        t = tm.create_task(title='t', source='test')
        tid = t['task_id']
        tm.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='d', action_type='info'),
            PlanStep(step_id='s2', description='d', action_type='tool_invoke', capability_id='a.b', depends_on=['s1']),
        ])
        engine.execute_task(tid, plan)
        task = tm.get_task(tid)
        assert task['status'] != 'completed'


class TestApprovalResumeContinuation:
    def test_resume_then_continue_all(self, engine, tm, broker, am):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        from aegis_ai.approval.approval_types import compute_args_hash
        broker.execute.side_effect = [_ok(), _appr('appr_y'), _ok()]
        t = tm.create_task(title='t', source='test')
        tid = t['task_id']
        tm.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='d', action_type='tool_invoke', capability_id='a.b'),
            PlanStep(step_id='s2', description='d', action_type='tool_invoke', capability_id='a.c'),
            PlanStep(step_id='s3', description='d', action_type='tool_invoke', capability_id='a.d'),
        ])
        engine.execute_task(tid, plan)
        args = {'key': 'value'}
        am.get.return_value = MagicMock(
            status='approved', task_id=tid, step_id='s2', capability_id='a.c',
            arguments=args, tool_args_hash=compute_args_hash(args),
        )
        broker.execute_approved.return_value = _ok()
        engine.resume_after_approval('appr_y')
        assert tm.get_task(tid)['status'] == 'completed'
        assert tm.get_step(tid, 's3')['status'] == 'completed'


class TestPlanRoundTrip:
    def test_from_dict_preserves_all_fields(self):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        plan = TaskPlan(plan_id='p1', user_goal='goal', interpreted_request='req', assumptions=['a1'], steps=[
            PlanStep(step_id='s1', description='d', action_type='tool_invoke', capability_id='a.b',
                     params={'x': 1}, depends_on=['s0'], expected_result='r1', requires_approval=True),
        ], risk_notes=['r1'], approval_needed=True, stop_conditions=['s1'],
           expected_result='er', verification_plan='vp', needs_browser=True)
        d = plan.to_dict()
        p2 = TaskPlan.from_dict(d)
        assert p2.plan_id == 'p1'
        assert p2.user_goal == 'goal'
        assert p2.assumptions == ['a1']
        assert p2.risk_notes == ['r1']
        assert p2.needs_browser is True
        s = p2.steps[0]
        assert s.params == {'x': 1}
        assert s.depends_on == ['s0']
        assert s.expected_result == 'r1'
        assert s.requires_approval is True

    def test_step_to_dict_from_dict_roundtrip(self):
        from aegis_ai.task_plan import PlanStep
        s = PlanStep(step_id='s1', description='d', action_type='tool_invoke', capability_id='a.b',
                     params={'k': 'v'}, depends_on=['s0'], expected_result='er',
                     status=PlanStep.__class__.__mro__[0], error='err')
        from aegis_ai.task_plan import StepStatus
        s.status = StepStatus.COMPLETED
        s.result = {'out': 'val'}
        s.error = 'some_error'
        d = s.to_dict()
        s2 = PlanStep.from_dict(d)
        assert s2.step_id == 's1'
        assert s2.params == {'k': 'v'}
        assert s2.depends_on == ['s0']
        assert s2.status == StepStatus.COMPLETED
        assert s2.result == {'out': 'val'}
        assert s2.error == 'some_error'


class TestBrowserStepUnified:
    def test_browser_uses_execute(self, engine, tm, broker):
        from aegis_ai.task_plan import PlanStep, TaskPlan
        broker.execute.return_value = _ok()
        t = tm.create_task(title='t', source='test')
        tid = t['task_id']
        tm.start_task(tid)
        plan = TaskPlan(plan_id='p', interpreted_request='test', steps=[
            PlanStep(step_id='s1', description='browse', action_type='browser_open', capability_id='browser-server.page.browse', params={'url': 'http://example.com'}),
        ])
        engine.execute_task(tid, plan)
        broker.execute.assert_called_once()
        call_args = broker.execute.call_args[0][0]
        assert call_args.task_id == tid
        assert call_args.step_id == 's1'
        assert call_args.capability_id == 'browser-server.page.browse'


class TestArchitectureGuard:
    def test_no_invoke_tool_in_engine(self):
        import inspect
        from aegis_ai.task.execution_engine import TaskExecutionEngine
        src = inspect.getsource(TaskExecutionEngine)
        assert 'invoke_tool(' not in src, 'invoke_tool() found in TaskExecutionEngine'
        assert '.invoke_tool(' not in src, '.invoke_tool() found in TaskExecutionEngine'

    def test_no_manual_planstep_in_continue(self):
        import inspect
        from aegis_ai.task.execution_engine import TaskExecutionEngine
        src = inspect.getsource(TaskExecutionEngine.continue_task)
        assert 'PlanStep(' not in src, 'Manual PlanStep construction in continue_task'
        assert 'from_dict' in src, 'from_dict not used in continue_task'

    def test_completion_uses_apply_task_state(self):
        import inspect
        from aegis_ai.task.execution_engine import TaskExecutionEngine
        src = inspect.getsource(TaskExecutionEngine.execute_task)
        assert 'apply_task_state' in src, 'execute_task does not use apply_task_state'
        assert 'has_failures' not in src, 'execute_task uses old has_failures logic'
