# -*- coding: utf-8 -*-
'''Task Execution Engine - canonical execution path.

Single source of truth for all step execution.
Completion is only allowed when ALL steps are in terminal state.
'''

from __future__ import annotations

import json
import logging
from enum import Enum
from typing import Any

from aegis_ai.task.task_manager import TaskManager
from aegis_ai.task_plan import PlanStep, StepStatus, TaskPlan

logger = logging.getLogger('aegis_ai.task.execution_engine')


class TaskFinalState(Enum):
    ALL_COMPLETED = 'all_completed'
    HAS_FAILED = 'has_failed'
    HAS_NEEDS_APPROVAL = 'has_needs_approval'
    HAS_PENDING = 'has_pending'
    HAS_RUNNING = 'has_running'
    HAS_WAITING_DEPENDENCY = 'has_waiting_dependency'
    EMPTY = 'empty'


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

    def evaluate_plan_state(self, plan: TaskPlan) -> TaskFinalState:
        if not plan.steps:
            return TaskFinalState.EMPTY
        for step in plan.steps:
            if step.status == StepStatus.NEEDS_APPROVAL:
                return TaskFinalState.HAS_NEEDS_APPROVAL
        for step in plan.steps:
            if step.status == StepStatus.FAILED:
                return TaskFinalState.HAS_FAILED
        for step in plan.steps:
            if step.status == StepStatus.RUNNING:
                return TaskFinalState.HAS_RUNNING
        for step in plan.steps:
            if step.status == StepStatus.PENDING:
                if step.depends_on:
                    deps_met = all(
                        any(s.step_id == dep and s.status == StepStatus.COMPLETED for s in plan.steps)
                        for dep in step.depends_on
                    )
                    if not deps_met:
                        return TaskFinalState.HAS_WAITING_DEPENDENCY
                return TaskFinalState.HAS_PENDING
        terminal = {StepStatus.COMPLETED, StepStatus.SKIPPED}
        all_done = all(s.status in terminal for s in plan.steps)
        if all_done:
            return TaskFinalState.ALL_COMPLETED
        return TaskFinalState.HAS_PENDING

    def can_complete_task(self, plan: TaskPlan) -> bool:
        return self.evaluate_plan_state(plan) == TaskFinalState.ALL_COMPLETED

    def has_pending_executable_steps(self, plan: TaskPlan) -> bool:
        for step in plan.steps:
            if step.status != StepStatus.PENDING:
                continue
            if not step.depends_on:
                return True
            deps_met = all(
                any(s.step_id == dep and s.status == StepStatus.COMPLETED for s in plan.steps)
                for dep in step.depends_on
            )
            if deps_met:
                return True
        return False

    def has_waiting_dependency_steps(self, plan: TaskPlan) -> bool:
        for step in plan.steps:
            if step.status != StepStatus.PENDING:
                continue
            if step.depends_on:
                deps_met = all(
                    any(s.step_id == dep and s.status == StepStatus.COMPLETED for s in plan.steps)
                    for dep in step.depends_on
                )
                if not deps_met:
                    return True
        return False

    def apply_task_state(self, task_id: str, plan: TaskPlan) -> None:
        state = self.evaluate_plan_state(plan)
        task = self._task_manager.get_task(task_id)
        if not task:
            return
        current = task['status']
        if state == TaskFinalState.HAS_NEEDS_APPROVAL:
            if current != 'waiting_approval':
                self._task_manager.wait_for_approval(task_id)
        elif state == TaskFinalState.HAS_FAILED:
            if current not in ('failed',):
                self._task_manager.fail_task(task_id, error='Step(s) failed')
        elif state == TaskFinalState.HAS_RUNNING:
            pass
        elif state == TaskFinalState.HAS_WAITING_DEPENDENCY:
            if current not in ('paused',):
                try:
                    self._task_manager.pause_task(task_id)
                except (AttributeError, Exception):
                    pass
        elif state == TaskFinalState.HAS_PENDING:
            pass
        elif state == TaskFinalState.ALL_COMPLETED:
            if current not in ('completed',):
                result_summary = self._build_task_result_summary(task_id, plan)
                self._task_manager.complete_task(task_id, result_summary=result_summary)
                self._present_task_completion(task_id)

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
                self.apply_task_state(task_id, plan)
                return ExecutionResponse(text='\n'.join(results), task_id=task_id)
            elif step.status == StepStatus.FAILED:
                self._task_manager.update_step_status(task_id, step.step_id, 'failed', error=step.error)
                self.apply_task_state(task_id, plan)
                return ExecutionResponse(text='\n'.join(results), task_id=task_id)
            elif step.status == StepStatus.COMPLETED:
                self._task_manager.update_step_status(task_id, step.step_id, 'completed', result=step.result)
        self._sync_plan_from_task_manager(task_id, plan)
        self.apply_task_state(task_id, plan)
        return ExecutionResponse(
            text='\n'.join(results) or plan.expected_result or 'No actions to execute.',
            task_id=task_id,
        )

    def _execute_step(self, task_id: str, step: PlanStep, plan: TaskPlan) -> str:
        if step.action_type.startswith('browser_'):
            return self._execute_tool_step(task_id, step, capability_override='browser-server.page.browse')
        if step.action_type == 'tool_invoke' and step.capability_id:
            return self._execute_tool_step(task_id, step)
        if step.action_type.startswith('llm_'):
            return self._execute_llm_step(task_id, step, plan)
        return f'[INFO] {step.description}'

    def _execute_tool_step(self, task_id: str, step: PlanStep, capability_override: str = '') -> str:
        from tool_broker import ExecutionSource, InvokeStatus, ToolExecutionRequest
        if not self._tool_broker:
            return f'[INFO] {step.description} (ToolBroker not available)'
        cap_id = capability_override or step.capability_id
        args = dict(step.params)
        if capability_override and step.params.get('url'):
            args = {'task': f'Go to {step.params["url"]} and {step.description}'}
        elif capability_override:
            args = {'task': step.description}
        request = ToolExecutionRequest(
            task_id=task_id,
            step_id=step.step_id,
            capability_id=cap_id,
            arguments=args,
            source=ExecutionSource.USER_EXPLICIT,
            reason=f'Step {step.step_id}: {step.description[:80]}',
        )
        result = self._tool_broker.execute(request)
        if result.success:
            if not self._completion_verified(result):
                step.status = StepStatus.FAILED
                step.error = self._completion_failure_message(result)
                return f'[VERIFY] {step.description}: {step.error}'
            step.status = StepStatus.COMPLETED
            step.result = self._tool_result_with_verification(result)
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
                if not self._completion_verified(result):
                    error = self._completion_failure_message(result)
                    self._task_manager.update_step_status(task_id, step_id, 'failed', error=error)
                    self._task_manager.fail_task(task_id, error=f'Step {step_id} failed verification: {error}')
                    return ExecutionResponse(text=f'[VERIFY] Step {step_id}: {error}', task_id=task_id)
                self._task_manager.resume_after_approval(task_id, step_id)
                self._task_manager.update_step_status(
                    task_id,
                    step_id,
                    'completed',
                    result=self._tool_result_with_verification(result),
                )
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
                self.apply_task_state(task_id, plan)
                return ExecutionResponse(text='\n'.join(results), task_id=task_id)
            elif step.status == StepStatus.FAILED:
                self._task_manager.update_step_status(task_id, step.step_id, 'failed', error=step.error)
                self.apply_task_state(task_id, plan)
                return ExecutionResponse(text='\n'.join(results), task_id=task_id)
            elif step.status == StepStatus.COMPLETED:
                self._task_manager.update_step_status(task_id, step.step_id, 'completed', result=step.result)
        self._sync_plan_from_task_manager(task_id, plan)
        self.apply_task_state(task_id, plan)
        return ExecutionResponse(text='\n'.join(results) or f'Step {completed_step_id} completed', task_id=task_id)

    def continue_task(self, task_id: str) -> ExecutionResponse:
        task = self._task_manager.get_task(task_id)
        if task is None:
            return ExecutionResponse(text=f'Task {task_id} not found')
        if task['status'] not in ('running', 'waiting_approval', 'paused'):
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
                    'pending': StepStatus.PENDING,
                }
                step.status = status_map.get(ts['status'], StepStatus.PENDING)
                if ts.get('result') is not None:
                    step.result = ts['result']
                if ts.get('error'):
                    step.error = ts['error']
        if self.has_pending_executable_steps(plan):
            last_completed = ''
            for step in reversed(plan.steps):
                if step.status == StepStatus.COMPLETED:
                    last_completed = step.step_id
                    break
            if last_completed:
                return self._continue_after_step(task_id, last_completed)
            return self.execute_task(task_id, plan)
        self.apply_task_state(task_id, plan)
        state = self.evaluate_plan_state(plan)
        return ExecutionResponse(text=f'Task state: {state.value}', task_id=task_id)

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
        plan = self._plans.get(task_id)
        if plan:
            for ps in plan.steps:
                if ps.step_id == step_id:
                    ps.status = StepStatus.PENDING
                    break
            return self.execute_task(task_id, plan)
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

    def _sync_plan_from_task_manager(self, task_id: str, plan: TaskPlan) -> None:
        for step in plan.steps:
            ts = self._task_manager.get_step(task_id, step.step_id)
            if ts:
                status_map = {
                    'completed': StepStatus.COMPLETED,
                    'failed': StepStatus.FAILED,
                    'needs_approval': StepStatus.NEEDS_APPROVAL,
                    'running': StepStatus.RUNNING,
                    'cancelled': StepStatus.SKIPPED,
                    'pending': StepStatus.PENDING,
                }
                step.status = status_map.get(ts['status'], step.status)
                if ts.get('result') is not None:
                    step.result = ts['result']
                if ts.get('error'):
                    step.error = ts['error']

    def _build_task_result_summary(self, task_id: str, plan: TaskPlan) -> str:
        task = self._task_manager.get_task(task_id) or {}
        summary = str(task.get('result_summary') or '').strip()
        if summary:
            return summary
        if plan.expected_result:
            return str(plan.expected_result).strip()
        return 'All steps completed'

    def _completion_verified(self, result: Any) -> bool:
        verification = getattr(result, "verification", None)
        status = str(
            getattr(verification, "status", "")
            or getattr(result, "verification_status", "")
            or ""
        ).lower()
        if status in {"", "pending", "skipped", "passed", "verified", "unverified"}:
            return True
        return status not in {"failed", "error", "requires_observation"}

    def _completion_failure_message(self, result: Any) -> str:
        verification = getattr(result, "verification", None)
        details = getattr(verification, "details", None) or getattr(verification, "evidence", None) or []
        reason = getattr(verification, "reason", "") or getattr(result, "error", "")
        repair = getattr(verification, "repair_hint", "") or getattr(verification, "suggested_recovery", "")
        parts = [str(reason).strip()] if reason else []
        if details:
            parts.append("; ".join(str(item) for item in details if item))
        if repair:
            parts.append(f"repair={repair}")
        return " / ".join(part for part in parts if part) or "Completion verification failed"

    def _tool_result_with_verification(self, result: Any) -> dict[str, Any]:
        output = dict(getattr(result, "output", {}) or {})
        verification = getattr(result, "verification", None)
        if verification is not None:
            try:
                status = str(getattr(verification, "status", "") or "")
                if status and "MagicMock" not in status:
                    output.setdefault("completion_verification", {
                        "status": status,
                        "checks_passed": int(getattr(verification, "checks_passed", 0) or 0),
                        "checks_failed": int(getattr(verification, "checks_failed", 0) or 0),
                        "details": list(getattr(verification, "details", []) or []),
                        "repair_hint": str(getattr(verification, "repair_hint", "") or ""),
                    })
            except Exception:
                logger.debug("Failed to attach completion verification payload", exc_info=True)
        return output

    def _present_task_completion(self, task_id: str) -> None:
        try:
            from aegis_ai.runtime import get_runtime
            from aegis_ai.presentation.models import PresentationRequest
        except Exception:
            return

        rt = get_runtime()
        presentation_manager = getattr(rt, 'presentation_manager', None) if rt is not None else None
        if not hasattr(rt, 'presentation_manager') or presentation_manager is None:
            return

        task = self._task_manager.get_task(task_id)
        if not task:
            return

        result_summary = str(task.get('result_summary') or '').strip()
        if not result_summary:
            return

        request = PresentationRequest(
            source='task_execution_engine',
            intent='task_completed',
            importance=self._importance_from_priority(int(task.get('priority', 0) or 0)),
            modality='text_card',
            title=str(task.get('title') or task_id),
            summary=result_summary,
            content={
                'task_id': task_id,
                'task_title': str(task.get('title') or ''),
                'result_summary': result_summary,
            },
        )
        try:
            presentation_manager.present(request)
        except Exception:
            logger.debug('Failed to present completed task %s', task_id, exc_info=True)

    def _importance_from_priority(self, priority: int) -> str:
        if priority >= 7:
            return 'critical'
        if priority >= 4:
            return 'high'
        if priority >= 2:
            return 'normal'
        return 'low'

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
