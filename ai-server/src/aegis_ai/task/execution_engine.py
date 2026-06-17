# -*- coding: utf-8 -*-
'''Task Execution Engine - canonical execution path.

Single source of truth for all step execution.
Approval-aware with continuation support.
'''

from __future__ import annotations

import json
import logging
from typing import Any

from aegis_ai.task.task_manager import TaskManager
from aegis_ai.task_plan import PlanStep, StepStatus, TaskPlan

logger = logging.getLogger('aegis_ai.task.execution_engine')


_COMPLETE_STEP_STATUSES = frozenset({'completed', 'skipped', 'cancelled'})
_BLOCKING_STEP_STATUSES = frozenset({'pending', 'running', 'needs_approval', 'waiting_dependency'})


class ExecutionResponse:
    def __init__(self, text: str = '', task_id: str = '') -> None:
        self.text = text
        self.task_id = task_id


class TaskExecutionEngine:
    def __init__(
        self,
        task_manager: TaskManager,
        tool_broker: Any = None,
        approval_manager: Any = None,
        llm_gateway: Any = None,
        prompt_registry: Any = None,
        settings_resolver: Any = None,
    ) -> None:
        self._task_manager = task_manager
        self._tool_broker = tool_broker
        self._approval_manager = approval_manager
        self._llm_gateway = llm_gateway
        self._prompt_registry = prompt_registry
        self._settings_resolver = settings_resolver
        self._plans: dict[str, TaskPlan] = {}

    def execute_task(self, task_id: str, plan: TaskPlan) -> ExecutionResponse:
        self._plans[task_id] = plan
        plan_json = json.dumps(plan.to_dict(), ensure_ascii=False)
        self._task_manager.save_plan(task_id, plan_json)
        results: list[str] = []

        for step in plan.steps:
            if step.status not in (StepStatus.PENDING, StepStatus.APPROVED):
                continue
            if step.depends_on:
                deps_met = all(
                    any(s.step_id == dep and s.status == StepStatus.COMPLETED for s in plan.steps)
                    for dep in step.depends_on
                )
                if not deps_met:
                    continue
            self._task_manager.add_step(task_id, step.step_id, step.description[:50], step.capability_id)
            self._task_manager.update_step_status(task_id, step.step_id, 'running')
            self._task_manager.set_current_step(task_id, step.step_id)
            step_result = self._execute_step(task_id, step, plan)
            results.append(step_result)
            if step.status == StepStatus.NEEDS_APPROVAL:
                return ExecutionResponse(text='\n'.join(results), task_id=task_id)
            elif step.status == StepStatus.FAILED:
                self._task_manager.update_step_status(task_id, step.step_id, 'failed', error=step.error)
                self._task_manager.fail_task(task_id, error='Step ' + step.step_id + ' failed')
                return ExecutionResponse(text='\n'.join(results), task_id=task_id)
            elif step.status == StepStatus.COMPLETED:
                self._task_manager.update_step_status(task_id, step.step_id, 'completed', result=step.result)
        self._try_complete_task(task_id)
        return ExecutionResponse(
            text='\n'.join(results) or plan.expected_result or 'No actions to execute.',
            task_id=task_id,
        )

    def _try_complete_task(self, task_id: str) -> None:
        task = self._task_manager.get_task(task_id)
        if not task:
            return
        if task['status'] == 'waiting_approval':
            return
        steps = task.get('steps', [])
        if not steps:
            return
        has_blocking = any(s.get('status') in _BLOCKING_STEP_STATUSES for s in steps)
        if has_blocking:
            return
        has_failed = any(s.get('status') == 'failed' for s in steps)
        if has_failed:
            self._task_manager.fail_task(task_id, error='Some steps failed')
            return
        all_terminal = all(s.get('status') in _COMPLETE_STEP_STATUSES | {'failed'} for s in steps)
        if all_terminal and not has_failed:
            self._task_manager.complete_task(task_id, result_summary='All steps completed')

    def _execute_step(self, task_id: str, step: PlanStep, plan: TaskPlan) -> str:
        if step.action_type.startswith('browser_'):
            return self._execute_browser_step(task_id, step)
        if step.action_type == 'tool_invoke' and step.capability_id:
            return self._execute_tool_step(task_id, step)
        if step.action_type.startswith('llm_'):
            return self._execute_llm_step(task_id, step, plan)
        return f'[INFO] {step.description}'

    def _execute_tool_step(self, task_id: str, step: PlanStep) -> str:
        from tool_broker import ExecutionSource, InvokeStatus, ToolExecutionRequest
        if not self._tool_broker:
            return f'[INFO] {step.description} (ToolBroker not available)'
        request = ToolExecutionRequest(
            task_id=task_id,
            capability_id=step.capability_id,
            arguments=step.params,
            source=ExecutionSource.USER_EXPLICIT,
            reason=f'Step {step.step_id}: {step.description[:80]}',
            step_id=step.step_id,
        )
        result = self._tool_broker.execute(request)
        if result.success:
            step.status = StepStatus.COMPLETED
            step.result = result.output
            return f'[OK] {step.description}'
        elif result.status == InvokeStatus.APPROVAL_NEEDED:
            step.status = StepStatus.NEEDS_APPROVAL
            approval_id = result.approval_id
            self._task_manager.wait_for_approval(task_id, step.step_id, approval_id)
            self._task_manager.set_waiting_approval(task_id, step.step_id, approval_id)
            return f'[APPROVAL] {step.description} -- approval_id={approval_id}'
        else:
            step.status = StepStatus.FAILED
            step.error = result.error
            return f'[FAIL] {step.description}: {result.error}'

    def _execute_browser_step(self, task_id: str, step: PlanStep) -> str:
        if not self._tool_broker:
            return f'[INFO] {step.description} (ToolBroker not available)'
        try:
            task_desc = step.description
            if step.params.get('url'):
                task_desc = f'Go to {step.params["url"]} and {step.description}'
            result = self._tool_broker.invoke_tool(
                'browser-server.page.browse', {'task': task_desc}, caller='execution-engine',
            )
            if result.success:
                step.status = StepStatus.COMPLETED
                step.result = result.output
                output = result.output or {}
                return str(output.get('result') or output.get('content') or output)
            elif result.status.name == 'APPROVAL_NEEDED':
                step.status = StepStatus.NEEDS_APPROVAL
                return f'[APPROVAL] {step.description} -- needs approval'
            step.status = StepStatus.FAILED
            step.error = result.error
            return f'[FAIL] {step.description}: {result.error}'
        except Exception as e:
            step.status = StepStatus.FAILED
            return f'[ERROR] Browser: {e}'

    def _execute_llm_step(self, task_id: str, step: PlanStep, plan: TaskPlan) -> str:
        if not self._llm_gateway:
            return f'[INFO] {step.description} (LLM not available)'
        try:
            system_prompt = self._get_system_prompt('interaction.llm_step', 'You are AEGIS. Perform the requested analysis concisely.')
            prompt = step.description
            if step.params.get('content'):
                prompt = f'{step.description}\n\nContent:\n{step.params["content"]}'
            settings = self._resolve_settings('task_analysis')
            response = self._llm_gateway.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
            )
            if hasattr(response, 'success') and response.success:
                step.status = StepStatus.COMPLETED
                step.result = response.content
                return response.content
            elif hasattr(response, 'content'):
                step.status = StepStatus.COMPLETED
                step.result = response.content
                return response.content
            else:
                step.status = StepStatus.FAILED
                error = getattr(response, 'error', 'Unknown LLM error')
                return f'[FAIL] {step.description}: {error}'
        except Exception as e:
            step.status = StepStatus.FAILED
            return f'[ERROR] LLM step: {e}'

    def pause_for_approval(self, task_id: str, step_id: str, approval_id: str) -> dict[str, Any] | None:
        return self._task_manager.wait_for_approval(task_id, step_id, approval_id)

    def resume_after_approval(self, approval_id: str) -> ExecutionResponse:
        if not self._approval_manager:
            return ExecutionResponse(text='ApprovalManager not available')
        request = self._approval_manager.get(approval_id)
        if request is None:
            return ExecutionResponse(text=f'Approval {approval_id} not found')
        if request.status not in ('approved', 'modified'):
            return ExecutionResponse(text=f'Approval {approval_id} not approved (status={request.status})')
        task_id = request.task_id
        step_id = request.step_id
        if not self._tool_broker:
            return ExecutionResponse(text='ToolBroker not available', task_id=task_id)
        if request.tool_args_hash and request.arguments:
            from aegis_ai.approval.approval_types import compute_args_hash
            current_hash = compute_args_hash(request.arguments)
            if current_hash != request.tool_args_hash:
                self._approval_manager.mark_failed(approval_id, 'Arguments tampered after approval')
                if task_id:
                    self._task_manager.fail_task(task_id, error='Approval arguments tampered')
                return ExecutionResponse(text=f'[DENIED] Approval {approval_id}: arguments were tampered', task_id=task_id)
        result = self._tool_broker.execute_approved(approval_id)
        if task_id and step_id:
            if result.success:
                self._task_manager.resume_after_approval(task_id, step_id)
                self._task_manager.update_step_status(task_id, step_id, 'completed', result=result.output)
                self._task_manager.set_waiting_approval(task_id, '', '')
                return self._continue_after_step(task_id, step_id)
            else:
                self._task_manager.update_step_status(task_id, step_id, 'failed', error=result.error)
                self._task_manager.fail_task(task_id, error=f'Step {step_id} failed after approval: {result.error}')
                return ExecutionResponse(text=f'[FAIL] Step {step_id} failed: {result.error}', task_id=task_id)
        return ExecutionResponse(text=f'[OK] Approval {approval_id} executed', task_id=task_id)

    def _continue_after_step(self, task_id: str, completed_step_id: str) -> ExecutionResponse:
        plan = self._plans.get(task_id)
        if plan is None:
            self._try_complete_task(task_id)
            return ExecutionResponse(text=f'[OK] Step {completed_step_id} completed', task_id=task_id)
        results: list[str] = []
        found_completed = False
        for step in plan.steps:
            if step.step_id == completed_step_id:
                found_completed = True
                continue
            if not found_completed:
                continue
            if step.status not in (StepStatus.PENDING,):
                continue
            if step.depends_on:
                deps_met = all(
                    any(s.step_id == dep and s.status == StepStatus.COMPLETED for s in plan.steps)
                    for dep in step.depends_on
                )
                if not deps_met:
                    continue
            self._task_manager.add_step(task_id, step.step_id, step.description[:50], step.capability_id)
            self._task_manager.update_step_status(task_id, step.step_id, 'running')
            self._task_manager.set_current_step(task_id, step.step_id)
            step_result = self._execute_step(task_id, step, plan)
            results.append(step_result)
            if step.status == StepStatus.NEEDS_APPROVAL:
                return ExecutionResponse(text='\n'.join(results), task_id=task_id)
            elif step.status == StepStatus.FAILED:
                self._task_manager.update_step_status(task_id, step.step_id, 'failed', error=step.error)
                self._task_manager.fail_task(task_id, error=f'Step {step.step_id} failed')
                return ExecutionResponse(text='\n'.join(results), task_id=task_id)
            elif step.status == StepStatus.COMPLETED:
                self._task_manager.update_step_status(task_id, step.step_id, 'completed', result=step.result)
        self._try_complete_task(task_id)
        return ExecutionResponse(text='\n'.join(results) or f'Step {completed_step_id} completed', task_id=task_id)

    def continue_task(self, task_id: str) -> ExecutionResponse:
        task = self._task_manager.get_task(task_id)
        if task is None:
            return ExecutionResponse(text=f'Task {task_id} not found')
        if task['status'] not in ('running', 'waiting_approval'):
            return ExecutionResponse(text=f'Task {task_id} not in executable state (status={task["status"]})')
        plan = self._plans.get(task_id)
        if plan is None:
            plan_json = self._task_manager.get_plan_json(task_id)
            if plan_json:
                data = json.loads(plan_json)
                plan = TaskPlan.from_dict(data)
                self._plans[task_id] = plan
        if plan is None:
            return ExecutionResponse(text='No plan found for task')
        for step in plan.steps:
            ts = self._task_manager.get_step(task_id, step.step_id)
            if ts:
                status_map = {
                    'completed': StepStatus.COMPLETED,
                    'failed': StepStatus.FAILED,
                    'needs_approval': StepStatus.NEEDS_APPROVAL,
                    'running': StepStatus.RUNNING,
                    'cancelled': StepStatus.SKIPPED,
                }
                step.status = status_map.get(ts['status'], StepStatus.PENDING)
        last_completed = ''
        for step in reversed(plan.steps):
            if step.status == StepStatus.COMPLETED:
                last_completed = step.step_id
                break
        if last_completed:
            return self._continue_after_step(task_id, last_completed)
        return self.execute_task(task_id, plan)

    def cancel_task(self, task_id: str, reason: str = '') -> dict[str, Any] | None:
        task = self._task_manager.get_task(task_id)
        if task:
            for step in task.get('steps', []):
                if step.get('status') in ('running', 'pending', 'needs_approval'):
                    self._task_manager.update_step_status(task_id, step['step_id'], 'cancelled')
        return self._task_manager.cancel_task(task_id, reason)

    def retry_step(self, task_id: str, step_id: str) -> str:
        step = self._task_manager.get_step(task_id, step_id)
        if step is None:
            return f'Step {step_id} not found'
        if step.get('status') != 'failed':
            return f'Step {step_id} is not in failed state (status={step.get("status")})'
        self._task_manager.update_step_status(task_id, step_id, 'pending')
        plan_step = PlanStep(
            step_id=step_id,
            description=step.get('name', ''),
            capability_id=step.get('capability_id', ''),
            action_type='tool_invoke' if step.get('capability_id') else 'info',
        )
        result = self._execute_step(task_id, plan_step, TaskPlan(steps=[plan_step]))
        if plan_step.status == StepStatus.COMPLETED:
            self._task_manager.update_step_status(task_id, step_id, 'completed', result=plan_step.result)
        elif plan_step.status == StepStatus.FAILED:
            self._task_manager.update_step_status(task_id, step_id, 'failed', error=plan_step.error)
        return result

    def _get_system_prompt(self, prompt_id: str, default: str = '') -> str:
        if self._prompt_registry:
            try:
                return self._prompt_registry.render(prompt_id)
            except KeyError:
                pass
        return default

    def _resolve_settings(self, profile: str) -> Any:
        if self._settings_resolver:
            try:
                return self._settings_resolver.resolve(profile_id=profile)
            except KeyError:
                pass
        class _Defaults:
            max_tokens = 2048
            temperature = 0.3
        return _Defaults()
