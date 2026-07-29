"""One-shot hygiene for polluted autonomous goals and E2E leftovers."""

from __future__ import annotations

from typing import Any


_INFRA_GOAL_MARKERS = (
    "browserstartevent",
    "timed out after",
    "timeout error",
    "traceback",
    "connection refused",
    "unavailable",
)
_E2E_MARKERS = (
    "android-production-e2e",
    "android-e2e",
    "manager_e2e",
    "production-e2e",
)


def _text_blob(task: dict[str, Any]) -> str:
    parts = [
        str(task.get("goal") or ""),
        str(task.get("title") or ""),
        str(task.get("error") or ""),
        str(task.get("result_summary") or ""),
    ]
    graph = task.get("goal_graph") or {}
    if isinstance(graph, dict):
        outcome = graph.get("outcome") or {}
        if isinstance(outcome, dict):
            parts.append(str(outcome.get("description") or ""))
        for check in graph.get("verification") or []:
            if isinstance(check, dict):
                parts.append(str(check.get("status") or ""))
                parts.extend(str(e) for e in (check.get("evidence") or [])[:3])
    return " ".join(parts).lower()


def is_polluted_autonomous_goal(task: dict[str, Any]) -> bool:
    """Return True when an autonomous task is infra noise or stalled observe-advance."""
    if str(task.get("source") or "") != "autonomous":
        return False
    status = str(task.get("status") or "")
    if status not in {"paused", "failed", "running"}:
        return False
    blob = _text_blob(task)
    title = str(task.get("title") or "")
    if title.startswith("Advance goal with"):
        return True
    if any(marker in blob for marker in _INFRA_GOAL_MARKERS):
        return True
    graph = task.get("goal_graph") or {}
    if isinstance(graph, dict):
        checks = graph.get("verification") or []
        if checks and all(
            str((c or {}).get("status") or "") == "blocked" for c in checks if isinstance(c, dict)
        ):
            return True
    return False


def is_e2e_continuation(record: dict[str, Any]) -> bool:
    blob = " ".join(
        str(record.get(key) or "")
        for key in ("goal", "trigger", "purpose", "rationale", "capability_id", "conversation_id")
    ).lower()
    return any(marker in blob for marker in _E2E_MARKERS)


def sweep_pollution(
    *,
    task_manager: Any,
    continuation_manager: Any | None = None,
    repair_manager: Any | None = None,
    dry_run: bool = True,
    task_limit: int = 500,
) -> dict[str, Any]:
    """Cancel polluted autonomous goals, close E2E continuations, dismiss infra repairs."""
    cancelled_tasks: list[str] = []
    resolved_incidents: list[str] = []
    closed_continuations: list[str] = []

    tasks = []
    if task_manager is not None and hasattr(task_manager, "list_tasks"):
        tasks = list(task_manager.list_tasks(limit=task_limit) or [])

    for task in tasks:
        if not is_polluted_autonomous_goal(task):
            continue
        task_id = str(task.get("task_id") or "")
        if not task_id:
            continue
        cancelled_tasks.append(task_id)
        if dry_run:
            continue
        status = str(task.get("status") or "")
        if status not in {"completed", "cancelled", "expired"}:
            task_manager.cancel_task(task_id, reason="goal_hygiene: polluted autonomous goal")
        if str(task.get("incident_status") or "") == "open" and hasattr(task_manager, "resolve_incident"):
            task_manager.resolve_incident(task_id, resolution="goal_hygiene")
            resolved_incidents.append(task_id)

    if continuation_manager is not None and hasattr(continuation_manager, "list_open"):
        for raw in list(continuation_manager.list_open() or []):
            if not is_e2e_continuation(raw):
                continue
            cont_id = str(raw.get("continuation_id") or "")
            if not cont_id:
                continue
            closed_continuations.append(cont_id)
            if dry_run:
                continue
            continuation_manager.advance(
                cont_id,
                stage="hygiene",
                state="cancelled",
                reason="goal_hygiene: stale e2e continuation",
            )

    repair_stats: dict[str, Any] = {"matched": 0, "dry_run": dry_run}
    if repair_manager is not None and hasattr(repair_manager, "dismiss_matching"):
        repair_stats = repair_manager.dismiss_matching(dry_run=dry_run)

    return {
        "dry_run": dry_run,
        "cancelled_tasks": cancelled_tasks,
        "resolved_incidents": resolved_incidents,
        "closed_continuations": closed_continuations,
        "repairs": repair_stats,
        "counts": {
            "cancelled_tasks": len(cancelled_tasks),
            "closed_continuations": len(closed_continuations),
            "repairs": int(repair_stats.get("matched") or 0),
        },
    }
