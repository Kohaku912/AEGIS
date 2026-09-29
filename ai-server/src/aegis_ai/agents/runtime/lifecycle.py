"""Agent Lifecycle — TaskStatus ↔ AgentBackend status 変換 (Phase 3).

Agent は独自の「内部状態」を持つが、AEGIS の TaskStatus 9 状態
(既存 enum) と整合させて管理する。`TaskManager._transition()` の
バリデーションがそのまま Agent にも適用される (instruction.md §9).

このファイルは AEGIS 側のみで完結し、OpenHands SDK 等に依存しない。
"""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.task.task_manager import TaskStatus

logger = logging.getLogger("aegis_ai.agents.runtime.lifecycle")


# ---------------------------------------------------------------------------
# Status mapping
# ---------------------------------------------------------------------------


# AgentBackend → AEGIS TaskStatus のマッピング
# (instruction.md §9 状態遷移図と一致)
_BACKEND_STATUS_TO_TASK: dict[str, TaskStatus] = {
    "pending": TaskStatus.PENDING,
    "created": TaskStatus.CREATED,
    "planning": TaskStatus.PLANNING,
    "running": TaskStatus.RUNNING,
    # Approval is no longer a constraint (2026-09-27): a backend that asks for a
    # decision is treated as paused and surfaced as REQUIRES_OBSERVATION.
    "waiting_approval": TaskStatus.PAUSED,
    "paused": TaskStatus.PAUSED,
    "blocked": TaskStatus.BLOCKED,
    "completed": TaskStatus.COMPLETED,
    "failed": TaskStatus.FAILED,
    "cancelled": TaskStatus.CANCELLED,
    "expired": TaskStatus.EXPIRED,
}


def backend_status_to_task(status: str | TaskStatus | None) -> TaskStatus:
    """`AgentBackend.get_status()` の戻り値 → AEGIS `TaskStatus`.

    文字列 / enum / None を受け取り、必ず `TaskStatus` を返す。
    未知の status は `FAILED` にマップ (フェイルセーフ).
    """
    if status is None:
        return TaskStatus.RUNNING
    if isinstance(status, TaskStatus):
        return status
    normalized = str(status).strip().lower()
    mapped = _BACKEND_STATUS_TO_TASK.get(normalized)
    if mapped is None:
        logger.warning("Unknown backend status %r; defaulting to FAILED", status)
        return TaskStatus.FAILED
    return mapped


def task_status_to_backend(task_status: TaskStatus) -> str:
    """`TaskStatus` → Agent backend 内部 status 文字列.

    逆方向: AEGIS → Agent へ状態を伝えるときに使う。
    """
    mapping = {
        TaskStatus.PENDING: "pending",
        TaskStatus.CREATED: "created",
        TaskStatus.PLANNING: "planning",
        TaskStatus.RUNNING: "running",
        TaskStatus.PAUSED: "paused",
        TaskStatus.BLOCKED: "blocked",
        TaskStatus.COMPLETED: "completed",
        TaskStatus.FAILED: "failed",
        TaskStatus.CANCELLED: "cancelled",
        TaskStatus.EXPIRED: "expired",
    }
    return mapping.get(task_status, "unknown")


def is_terminal(task_status: TaskStatus) -> bool:
    """`TaskStatus` が terminal か (instruction.md §9)."""
    return task_status in (
        TaskStatus.COMPLETED,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
        TaskStatus.EXPIRED,
    )


# ---------------------------------------------------------------------------
# TaskStatus transition validation
# ---------------------------------------------------------------------------


# `_VALID_TRANSITIONS` の fallback (TaskManager から import できないとき用).
# 仕様は `task_manager._VALID_TRANSITIONS` と同一 (instruction.md §9 状態遷移図).
_VALID_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.CREATED: {TaskStatus.PLANNING, TaskStatus.CANCELLED, TaskStatus.EXPIRED},
    TaskStatus.PLANNING: {
        TaskStatus.RUNNING,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
    },
    TaskStatus.RUNNING: {
        TaskStatus.PAUSED,
        TaskStatus.COMPLETED,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
    },
    TaskStatus.PAUSED: {
        TaskStatus.RUNNING,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
        TaskStatus.EXPIRED,
    },
    TaskStatus.COMPLETED: set(),
    TaskStatus.FAILED: set(),
    TaskStatus.CANCELLED: set(),
    TaskStatus.EXPIRED: set(),
}


def validate_transition(
    from_status: TaskStatus,
    to_status: TaskStatus,
    *,
    valid_transitions: dict[TaskStatus, set[TaskStatus]] | None = None,
) -> bool:
    """AEGIS 側での status 遷移を検証する (TaskManager._transition と同じ)."""
    table = valid_transitions or _VALID_TRANSITIONS
    allowed = table.get(from_status, set())
    if to_status in allowed:
        return True
    if from_status == to_status:
        # 同一 status への遷移は冪等として許可 (apply_task_state の冪等性)
        return True
    return False


# ---------------------------------------------------------------------------
# AgentResult → TaskManager 接続
# ---------------------------------------------------------------------------


def agent_result_to_task_summary(result: Any) -> str:
    """`AgentResult` → `TaskManager.complete_task(result_summary=)` 用文字列.

    §5 マッピング表の "summary" カラム.
    """
    summary = getattr(result, "summary", None) or ""
    if not summary:
        # 空のときはエラーがあればそれを入れる
        errors = getattr(result, "errors", None) or []
        if errors:
            first = errors[0]
            summary = f"[{getattr(first, 'code', 'error')}] {getattr(first, 'message', '')}"
        else:
            summary = "(no summary)"
    return summary


def agent_result_to_step_results(result: Any) -> list[dict[str, Any]]:
    """`AgentResult.actions` → PlanStep の result 形式.

    各 AgentAction を `{step_id, capability_id, result, error}` の dict に
    変換する。`TaskExecutionEngine._sync_plan_from_task_manager` 側で
    step の result / error にマージされる。
    """
    actions = getattr(result, "actions", None) or []
    out: list[dict[str, Any]] = []
    for act in actions:
        out.append(
            {
                "step_id": getattr(act, "step_id", ""),
                "capability_id": getattr(act, "capability_id", ""),
                "result": getattr(act, "result", None),
                "error": getattr(act, "error", None) or "",
                "duration_ms": getattr(act, "duration_ms", 0),
            }
        )
    return out
