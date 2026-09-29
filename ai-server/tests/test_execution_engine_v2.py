# -*- coding: utf-8 -*-
'''E2E tests for TaskExecutionEngine - multi-step execution + plan persistence.

Approval is no longer a constraint (2026-09-27); the old approval/resume and
args-tamper tests are gone with the machinery they exercised.
'''

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
        content=json.dumps({
            "status": "achieved",
            "reason": "Independent test evidence confirms the outcome.",
            "evidence": ["all planned steps produced successful results"],
        }),
    )
    return TaskExecutionEngine(
        task_manager=task_manager,
        tool_broker=mock_broker,
        goal_service=GoalLifecycleService(
            task_manager=task_manager,
            llm_gateway=verifier,
        ),
    )


def _success():
    return MagicMock(success=True, status=InvokeStatus.SUCCESS, output={'r': 'ok'}, error='', request_id='r1')


def _fail(msg='fail'):
    return MagicMock(success=False, status=InvokeStatus.EXECUTION_ERROR, output={}, error=msg, request_id='r1')


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

