"""Agent Executor — TaskExecutionEngine ↔ AgentBackend 接続 (Phase 3).

`TaskExecutionEngine._execute_step()` から呼び出される薄いアダプタ。
`step.capability_id` が `ai-server.agent.*` 形式のとき、`AgentBackend.run()`
にルーティングして結果を PlanStep に書き戻す。

設計判断:
- TaskExecutionEngine 自体には **触らない** (§35.4 不変条件).
  `agent_delegate` の capability_id を見て `_execute_step` 内で分岐する
  既存パターン (`browser_` / `tool_invoke` / `llm_`) に倣う。
- ただし、`_execute_step` は TaskExecutionEngine 内なので、ここでは
  **`AgentExecutor` クラス**として独立に実装し、TaskExecutionEngine 側に
  1 行だけ追加する adapter を Phase 3 後半で入れる想定。
- 単体テストでは TaskExecutionEngine を経由せず、`run_agent_step()` を
  直接呼んで PlanStep の更新挙動を検証する。
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from aegis_ai.agents.runtime.interface import AgentBackend
from aegis_ai.agents.runtime.lifecycle import (
    agent_result_to_step_results,
    agent_result_to_task_summary,
)
from aegis_ai.agents.runtime.models import (
    AgentProgress,
    AgentTask,
)
from aegis_ai.task.task_manager import TaskStatus
from aegis_ai.task_plan import PlanStep, StepStatus

logger = logging.getLogger("aegis_ai.agents.runtime.executor")


# agent 系 capability_id の prefix (canonical)
AGENT_CAPABILITY_PREFIX = "ai-server.agent."


def is_agent_capability(capability_id: str) -> bool:
    """capability_id が Agent 経由 (Local / OpenHands) で実行されるか."""
    return capability_id.startswith(AGENT_CAPABILITY_PREFIX)


def build_agent_task(
    *,
    step: PlanStep,
    plan: Any,
    profile: str = "general",
    metadata: dict[str, Any] | None = None,
) -> AgentTask:
    """`PlanStep` → `AgentTask`.

    優先順位:
    1. `step.params["goal"]` を AgentTask.goal に
    2. `step.description` を fallback
    3. `plan.user_goal` をさらに fallback
    """
    goal = (
        step.params.get("goal")
        or step.description
        or getattr(plan, "user_goal", "")
        or ""
    )
    # context は step.params (goal 以外) を入れる
    context = {k: v for k, v in (step.params or {}).items() if k != "goal"}
    # expected_result は context にも入れる (Agent が最終 output に使える)
    if step.expected_result:
        context["expected_result"] = step.expected_result

    return AgentTask(
        task_id=f"{getattr(plan, 'plan_id', 'plan')}-{step.step_id}",
        goal=str(goal),
        context=context,
        profile=profile,
        max_steps=int(step.params.get("max_steps", 5)),
        timeout_seconds=int(step.params.get("timeout_seconds", 600)),
        metadata={
            "step_id": step.step_id,
            "capability_id": step.capability_id,
            **(metadata or {}),
        },
    )


def emit_progress(
    callback: Callable[[AgentProgress], None] | None,
    *,
    task_id: str,
    stage: str,
    message: str = "",
    data: dict[str, Any] | None = None,
) -> None:
    """`AgentProgress` を callback に流すヘルパ."""
    if callback is None:
        return
    try:
        import time as _time

        callback(
            AgentProgress(
                task_id=task_id,
                stage=stage,
                message=message,
                data=data or {},
                timestamp_ms=int(_time.time() * 1000),
            )
        )
    except Exception:  # noqa: BLE001
        logger.debug("progress callback raised", exc_info=True)


def apply_result_to_step(step: PlanStep, result: Any) -> None:
    """`AgentResult` → `PlanStep.status / result / error` 反映.

    mapping (instruction.md §5):
    - `result.status == TaskStatus.COMPLETED` → `StepStatus.COMPLETED`
    - `result.status == TaskStatus.FAILED`    → `StepStatus.FAILED`
    - `result.status == TaskStatus.PAUSED`    → `StepStatus.REQUIRES_OBSERVATION`
      (a backend that reports ``waiting_approval`` is mapped to PAUSED by
      ``lifecycle.backend_status_to_task`` — approval is no longer a constraint,
      so such a step needs observation rather than a consent gate)
    - その他                                 → `StepStatus.FAILED` (フェイルセーフ)
    """
    backend_status: TaskStatus = getattr(result, "status", TaskStatus.FAILED)

    if backend_status == TaskStatus.COMPLETED:
        step.status = StepStatus.COMPLETED
        step.result = getattr(result, "summary", "")
        step.error = ""
    elif backend_status in (TaskStatus.PAUSED, TaskStatus.PLANNING):
        step.status = StepStatus.REQUIRES_OBSERVATION
        step.error = "agent paused; observation required"
    elif backend_status == TaskStatus.CANCELLED:
        step.status = StepStatus.SKIPPED
        step.error = "agent cancelled"
    elif backend_status == TaskStatus.EXPIRED:
        step.status = StepStatus.FAILED
        step.error = "agent expired"
    else:  # FAILED or unknown
        step.status = StepStatus.FAILED
        errs = getattr(result, "errors", None) or []
        if errs:
            first = errs[0]
            step.error = f"[{getattr(first, 'code', 'error')}] {getattr(first, 'message', '')}"
        else:
            step.error = "agent failed without error details"


async def run_agent_step(
    step: PlanStep,
    plan: Any,
    *,
    backend: AgentBackend,
    profile: str = "general",
    on_progress: Callable[[AgentProgress], None] | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """1 つの PlanStep を AgentBackend で実行する.

    TaskExecutionEngine._execute_step() から `agent_*` capability を
    検出したときに呼ばれる。
    """
    if not isinstance(backend, AgentBackend):
        step.status = StepStatus.FAILED
        step.error = "agent_backend is not registered or not an AgentBackend"
        return f"[FAIL] {step.description}: {step.error}"

    task = build_agent_task(step=step, plan=plan, profile=profile, metadata=metadata)
    emit_progress(
        on_progress,
        task_id=task.task_id,
        stage="started",
        message=step.description,
        data={"step_id": step.step_id, "capability_id": step.capability_id},
    )
    try:
        result = await backend.run(task, on_progress=on_progress)
    except Exception as exc:  # noqa: BLE001
        step.status = StepStatus.FAILED
        step.error = f"backend raised: {exc!r}"
        logger.exception("Agent backend raised for step %s", step.step_id)
        return f"[FAIL] {step.description}: {step.error}"

    apply_result_to_step(step, result)
    emit_progress(
        on_progress,
        task_id=task.task_id,
        stage="finished",
        message=step.status.name,
        data={"step_id": step.step_id, "result_status": result.status.name},
    )

    # step.result に summary を入れる (apply_result_to_step で完了している)
    # 加えて agent_result_to_step_results から詳細も取り出す
    detail = agent_result_to_step_results(result)
    if detail:
        # step.result は文字列想定だが、必要なら dict にして残す
        existing = step.result
        step.result = {
            "summary": existing,
            "agent_actions": detail,
            "usage": getattr(getattr(result, "usage", None), "duration_ms", 0),
        }

    if step.status == StepStatus.COMPLETED:
        return f"[OK] {step.description}"
    if step.status == StepStatus.REQUIRES_OBSERVATION:
        return f"[OBSERVE] {step.description}: {step.error}"
    if step.status == StepStatus.SKIPPED:
        return f"[SKIP] {step.description}: {step.error}"
    return f"[FAIL] {step.description}: {step.error}"


# ---------------------------------------------------------------------------
# Summary helpers (re-export from lifecycle for convenience)
# ---------------------------------------------------------------------------


def build_task_result_summary(result: Any) -> str:
    """`AgentResult` → `TaskManager.complete_task(result_summary=)` 用."""
    return agent_result_to_task_summary(result)
