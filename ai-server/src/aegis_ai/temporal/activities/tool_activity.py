"""ToolBroker activity for Temporal workflows."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.temporal.activities.tool")

_ACTIVITY_CONTEXT: dict[str, Any] = {}


def configure_activity_context(**deps: Any) -> None:
    """Inject runtime dependencies for worker activities."""
    _ACTIVITY_CONTEXT.update(deps)


try:
    from temporalio import activity as _activity
except Exception:  # pragma: no cover - optional dependency
    _activity = None


def _execute_tool_step(payload: dict[str, Any]) -> dict[str, Any]:
    broker = _ACTIVITY_CONTEXT.get("tool_broker")
    if broker is None:
        return {"success": False, "error": "tool_broker unavailable"}

    from tool_broker import ExecutionSource, ToolExecutionRequest

    request = ToolExecutionRequest(
        capability_id=str(payload.get("capability_id") or ""),
        arguments=dict(payload.get("arguments") or {}),
        source=ExecutionSource.SYSTEM,
        task_id=str(payload.get("task_id") or ""),
        reason=str(payload.get("reason") or "Temporal activity"),
        idempotency_key=str(payload.get("idempotency_key") or ""),
    )
    result = broker.execute(request)
    journal = _ACTIVITY_CONTEXT.get("journal_store")
    if journal is not None:
        try:
            journal.append(
                event_type="task.step.executed",
                aggregate_type="task",
                aggregate_id=request.task_id,
                payload={
                    "step_id": payload.get("step_id"),
                    "capability_id": request.capability_id,
                    "status": result.status.value,
                    "success": result.success,
                },
                correlation_id=request.task_id,
            )
        except Exception:
            logger.debug("Journal append from tool activity failed", exc_info=True)
    return {
        "success": result.success,
        "status": result.status.value,
        "output": result.output,
        "error": result.error,
        "policy_decision": result.policy_decision,
        "needs_approval": result.status.value == "needs_approval",
        "approval_id": getattr(result, "approval_id", ""),
    }


if _activity is not None:

    @_activity.defn(name="execute_tool_step_activity")
    def execute_tool_step_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return _execute_tool_step(payload)

else:

    def execute_tool_step_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return _execute_tool_step(payload)
