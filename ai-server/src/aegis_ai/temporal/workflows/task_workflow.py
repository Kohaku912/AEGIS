"""Durable multi-step task workflow."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from aegis_ai.temporal.activities.llm_activity import llm_generate_activity
    from aegis_ai.temporal.activities.tool_activity import execute_tool_step_activity


@workflow.defn
class TaskWorkflow:
    """Execute a persisted task plan with approval waits and retries."""

    def __init__(self) -> None:
        self._approval_granted = False
        self._approval_id = ""

    @workflow.run
    async def run(self, task_id: str, plan: dict[str, Any]) -> dict[str, Any]:
        steps = list(plan.get("steps") or [])
        results: list[dict[str, Any]] = []
        for index, step in enumerate(steps):
            step_id = str(step.get("step_id") or f"step_{index + 1}")
            capability_id = str(step.get("capability_id") or step.get("action") or "")
            arguments = dict(step.get("arguments") or {})
            idempotency_key = f"{task_id}:{step_id}"
            outcome = await workflow.execute_activity(
                execute_tool_step_activity,
                {
                    "task_id": task_id,
                    "step_id": step_id,
                    "capability_id": capability_id,
                    "arguments": arguments,
                    "idempotency_key": idempotency_key,
                },
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
            results.append({"step_id": step_id, **outcome})
            if outcome.get("needs_approval"):
                self._approval_id = str(outcome.get("approval_id") or "")
                self._approval_granted = False
                await workflow.wait_condition(lambda: self._approval_granted, timeout=timedelta(hours=24))
                retry = await workflow.execute_activity(
                    execute_tool_step_activity,
                    {
                        "task_id": task_id,
                        "step_id": step_id,
                        "capability_id": capability_id,
                        "arguments": arguments,
                        "idempotency_key": f"{idempotency_key}:approved",
                    },
                    start_to_close_timeout=timedelta(minutes=10),
                    retry_policy=RetryPolicy(maximum_attempts=2),
                )
                results[-1] = {"step_id": step_id, **retry}
                if not retry.get("success"):
                    return {"task_id": task_id, "status": "failed", "steps": results}
            elif not outcome.get("success"):
                return {"task_id": task_id, "status": "failed", "steps": results}

        if plan.get("llm_summary"):
            summary = await workflow.execute_activity(
                llm_generate_activity,
                {"prompt": str(plan.get("llm_summary")), "profile": "chat_balanced"},
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=2),
            )
            return {"task_id": task_id, "status": "completed", "steps": results, "summary": summary}
        return {"task_id": task_id, "status": "completed", "steps": results}

    @workflow.signal
    def approval_granted(self, approval_id: str = "") -> None:
        if approval_id and self._approval_id and approval_id != self._approval_id:
            return
        self._approval_granted = True
