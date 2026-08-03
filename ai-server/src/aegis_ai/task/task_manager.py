"""Task Manager — centralized execution unit tracking.

Tracks all execution units: user requests, autonomous tasks,
scheduler tasks, multi-step tool executions, approval-waiting tasks.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.task.task_manager")


class TaskStatus(Enum):
    CREATED = "created"
    PLANNING = "planning"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class TaskSource(Enum):
    USER = "user"
    AUTONOMOUS = "autonomous"
    SCHEDULER = "scheduler"
    EVENT = "event"
    SYSTEM = "system"


def _incident_fingerprint(task: dict[str, Any]) -> str:
    """Normalize a failed task into a collapse key for duplicate incident cleanup."""
    error = str(task.get("error") or task.get("goal") or task.get("title") or "").strip().lower()
    capability = ""
    steps = task.get("steps") if isinstance(task.get("steps"), list) else []
    for step in steps:
        if isinstance(step, dict) and step.get("capability_id"):
            capability = str(step.get("capability_id"))
            break
    if not capability:
        capability = str(task.get("capability_id") or task.get("source") or "task")
    # Stabilize noisy prefixes while keeping distinct failure families separate.
    for marker in (
        "browserstartevent",
        "completion verification failed",
        "http execution error: timed out",
        "invalid json from pc server",
        "interrupted by an ai server restart",
        "dev server grpc error: unavailable",
        "no space left on device",
        "failed to establish cdp connection",
        "path must stay inside the aegis workspace",
        "network_error",
        "remote end closed connection",
    ):
        if marker in error:
            return f"{capability}:{marker}"
    compact = " ".join(error.split())[:160]
    return f"{capability}:{compact or 'unknown'}"


def _is_unrecoverable_incident(error: str) -> bool:
    """Return True when retrying the same failure cannot make progress without external change."""
    text = (error or "").strip().lower()
    if not text:
        return False
    markers = (
        "browserstartevent",
        "interrupted by an ai server restart",
        "dev server grpc error: unavailable",
        "errors resolving dev-server",
        "no space left on device",
        "invalid json from pc server",
        "failed to establish cdp connection",
        "path must stay inside the aegis workspace",
        "android server is unavailable",
        "connection refused",
    )
    return any(marker in text for marker in markers)


_VALID_TRANSITIONS: dict[str, set[str]] = {
    "created": {"planning", "running", "cancelled", "expired"},
    "planning": {"running", "cancelled", "failed"},
    "running": {"waiting_approval", "paused", "completed", "failed", "cancelled"},
    "waiting_approval": {"running", "cancelled", "failed", "expired"},
    "paused": {"running", "cancelled", "failed"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
    "expired": set(),
}

_VALID_STEP_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"running", "needs_approval", "cancelled"},
    "running": {"completed", "failed", "requires_observation", "needs_approval", "cancelled"},
    "needs_approval": {"running", "cancelled", "failed"},
    "requires_observation": {"pending", "running", "failed", "cancelled"},
    "completed": set(),
    "failed": {"pending"},
    "cancelled": set(),
}


class TaskManager:
    """Centralized task lifecycle management.

    Tracks all execution units with explicit state transitions.
    Publishes task.* events and records audit on state changes.

    Parameters
    ----------
    event_manager:
        Optional EventManager for publishing task events.
    audit_manager:
        Optional AuditManager for recording task audit entries.
    data_dir:
        Directory for persistence.
    """

    def __init__(
        self,
        event_manager: Any = None,
        audit_manager: Any = None,
        data_dir: str = "data",
    ) -> None:
        self._event_manager = event_manager
        self._audit_manager = audit_manager
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._persist_path = self._data_dir / "tasks" / "task_manager.jsonl"
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)

        self._tasks: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._load()
        self._recover_interrupted_tasks()

    # ── Public API ────────────────────────────────────────────

    def create_task(
        self,
        title: str,
        goal: str = "",
        source: str = "system",
        priority: int = 0,
        parent_task_id: str = "",
        goal_graph: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new task."""
        task_id = f"task_{uuid.uuid4().hex[:10]}"
        now_ms = int(time.time() * 1000)
        task = {
            "task_id": task_id,
            "source": source,
            "title": title,
            "goal": goal,
            "goal_graph": dict(goal_graph or {}),
            "status": TaskStatus.CREATED.value,
            "created_at": now_ms,
            "updated_at": now_ms,
            "completed_at": 0,
            "current_step": 0,
            "steps": [],
            "related_approval_id": "",
            "related_llm_request_id": "",
            "related_event_ids": [],
            "error": "",
            "result_summary": "",
            "parent_task_id": parent_task_id,
            "child_task_ids": [],
            "retry_count": 0,
            "incident_status": "",
            "priority": priority,
            "plan_json": "",
            "current_step_id": "",
            "waiting_approval_step_id": "",
            "waiting_approval_id": "",
        }
        with self._lock:
            self._tasks[task_id] = task
            self._save()
        self._notify(task, "created")
        return task

    def start_task(self, task_id: str) -> dict[str, Any] | None:
        """Transition task to running."""
        return self._transition(task_id, TaskStatus.RUNNING)

    def update_step(self, task_id: str, step: int, step_name: str = "") -> dict[str, Any] | None:
        """Update current step."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            task["current_step"] = step
            task["updated_at"] = int(time.time() * 1000)
            if step_name:
                task["steps"].append({"step": step, "name": step_name, "timestamp": int(time.time() * 1000)})
            self._save()
        return task

    def wait_for_approval(self, task_id: str, step_id: str = "", approval_id: str = "") -> dict[str, Any] | None:
        """Transition to waiting_approval and link approval.

        If step_id is provided, also marks that step as needs_approval.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            task["related_approval_id"] = approval_id
            if step_id:
                step = self._find_step(task, step_id)
                if step is not None:
                    step["status"] = "needs_approval"
                    step["approval_id"] = approval_id
        return self._transition(task_id, TaskStatus.WAITING_APPROVAL)

    def resume_after_approval(self, task_id: str, step_id: str = "") -> dict[str, Any] | None:
        """Resume task after approval granted.

        If step_id is provided, also marks that step as running.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is not None and step_id:
                step = self._find_step(task, step_id)
                if step is not None:
                    step["status"] = "running"
                    self._save()
        return self._transition(task_id, TaskStatus.RUNNING)

    def complete_task(self, task_id: str, result_summary: str = "") -> dict[str, Any] | None:
        """Complete a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            task["result_summary"] = result_summary
            task["completed_at"] = int(time.time() * 1000)
            task["incident_status"] = "resolved"
        return self._transition(task_id, TaskStatus.COMPLETED)

    def save_goal_graph(self, task_id: str, goal_graph: dict[str, Any]) -> bool:
        """Persist the outcome contract that owns a task's execution."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            task["goal_graph"] = dict(goal_graph)
            task["updated_at"] = int(time.time() * 1000)
            self._save()
        return True

    def fail_task(self, task_id: str, error: str = "") -> dict[str, Any] | None:
        """Fail a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            task["error"] = error
            task["incident_status"] = "open"
        return self._transition(task_id, TaskStatus.FAILED)

    def cancel_task(self, task_id: str, reason: str = "") -> dict[str, Any] | None:
        """Cancel a task."""
        return self._transition(task_id, TaskStatus.CANCELLED)

    def pause_task(self, task_id: str) -> dict[str, Any] | None:
        """Pause a task (e.g., waiting for dependencies)."""
        return self._transition(task_id, TaskStatus.PAUSED)

    def resolve_incident(self, task_id: str, resolution: str = "") -> bool:
        """Mark a failed-task incident resolved after repair or explicit handling."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            task["incident_status"] = "resolved"
            if resolution:
                task["incident_resolution"] = resolution
            task["updated_at"] = int(time.time() * 1000)
            self._save()
        return True

    def list_open_incidents(self, *, limit: int = 5000) -> list[dict[str, Any]]:
        """Return failed tasks that still carry an open incident."""
        with self._lock:
            items = [
                dict(task)
                for task in self._tasks.values()
                if str(task.get("status") or "") == TaskStatus.FAILED.value
                and str(task.get("incident_status") or "") == "open"
            ]
        items.sort(key=lambda task: int(task.get("updated_at") or task.get("created_at") or 0), reverse=True)
        return items[: max(1, limit)]

    def sweep_stale_incidents(
        self,
        *,
        now_ms: int | None = None,
        max_age_ms: int = 24 * 60 * 60 * 1000,
        keep_per_fingerprint: int = 1,
    ) -> dict[str, Any]:
        """Auto-resolve duplicate / unrecoverable / aged failed-task incidents.

        Keeps at most ``keep_per_fingerprint`` newest open incidents per normalized
        error signature so AgentState obligations cannot be flooded by historical
        BrowserStart / timeout ghosts.
        """
        now = int(now_ms or time.time() * 1000)
        resolved: list[dict[str, str]] = []
        kept = 0
        by_fingerprint: dict[str, list[dict[str, Any]]] = {}

        with self._lock:
            open_items = [
                task
                for task in self._tasks.values()
                if str(task.get("status") or "") == TaskStatus.FAILED.value
                and str(task.get("incident_status") or "") == "open"
            ]
            for task in open_items:
                fingerprint = _incident_fingerprint(task)
                by_fingerprint.setdefault(fingerprint, []).append(task)

            for fingerprint, group in by_fingerprint.items():
                group.sort(
                    key=lambda task: int(task.get("updated_at") or task.get("created_at") or 0),
                    reverse=True,
                )
                for index, task in enumerate(group):
                    task_id = str(task.get("task_id") or "")
                    error = str(task.get("error") or task.get("goal") or "")
                    updated_at = int(task.get("updated_at") or task.get("created_at") or 0)
                    reason = ""
                    if _is_unrecoverable_incident(error):
                        reason = "auto_resolved_unrecoverable"
                    elif updated_at and now - updated_at > max_age_ms:
                        reason = "auto_resolved_stale_age"
                    elif index >= max(1, keep_per_fingerprint):
                        reason = "auto_resolved_duplicate"
                    if not reason:
                        kept += 1
                        continue
                    task["incident_status"] = "resolved"
                    task["incident_resolution"] = reason
                    task["updated_at"] = now
                    resolved.append({"task_id": task_id, "reason": reason, "fingerprint": fingerprint[:120]})
            if resolved:
                self._save()

        if resolved:
            logger.info(
                "Swept %d stale task incident(s); %d open incident(s) remain",
                len(resolved),
                kept,
            )
        return {
            "resolved_count": len(resolved),
            "kept_open": kept,
            "resolved": resolved[:50],
        }

    def list_tasks(self, status: str | None = None, source: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """List tasks with optional filters."""
        with self._lock:
            tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        if source:
            tasks = [t for t in tasks if t["source"] == source]
        tasks.sort(key=lambda t: t.get("created_at", 0), reverse=True)
        return tasks[:limit]

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Get a task by ID."""
        with self._lock:
            return self._tasks.get(task_id)

    def list_running(self) -> list[dict[str, Any]]:
        """List running tasks."""
        return self.list_tasks(status=TaskStatus.RUNNING.value)

    def list_waiting_approval(self) -> list[dict[str, Any]]:
        """List tasks waiting for approval."""
        return self.list_tasks(status=TaskStatus.WAITING_APPROVAL.value)

    # ── Step-level API ─────────────────────────────────────────

    def add_step(
        self,
        task_id: str,
        step_id: str,
        step_name: str = "",
        capability_id: str = "",
    ) -> dict[str, Any] | None:
        """Add a step to a task's step list.

        Returns the created step dict, or None if task not found.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            if self._find_step(task, step_id) is not None:
                return self._find_step(task, step_id)
            step = {
                "step_id": step_id,
                "name": step_name,
                "capability_id": capability_id,
                "status": "pending",
                "result": None,
                "error": "",
                "approval_id": "",
                "created_at": int(time.time() * 1000),
                "updated_at": int(time.time() * 1000),
            }
            task["steps"].append(step)
            self._save()
        return step

    def update_step_status(
        self,
        task_id: str,
        step_id: str,
        status: str,
        result: Any = None,
        error: str = "",
    ) -> dict[str, Any] | None:
        """Update a step's status within a task.

        Returns the updated step dict, or None if not found.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            step = self._find_step(task, step_id)
            if step is None:
                return None
            current = step["status"]
            if status not in _VALID_STEP_TRANSITIONS.get(current, set()):
                logger.warning("Invalid step transition: %s -> %s", current, status)
                return None
            step["status"] = status
            step["updated_at"] = int(time.time() * 1000)
            if result is not None:
                step["result"] = result
            if error:
                step["error"] = error
            self._save()
        return step

    def get_step(self, task_id: str, step_id: str) -> dict[str, Any] | None:
        """Get a specific step from a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            return self._find_step(task, step_id)

    def save_plan(self, task_id: str, plan_json: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            task["plan_json"] = plan_json
            self._save()
        return True

    def get_plan_json(self, task_id: str) -> str:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return ""
            return task.get("plan_json", "")

    def set_waiting_approval(self, task_id: str, step_id: str, approval_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            task["waiting_approval_step_id"] = step_id
            task["waiting_approval_id"] = approval_id
            task["current_step_id"] = step_id
            self._save()
        return True

    def get_waiting_approval_info(self, task_id: str) -> dict[str, str]:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return {}
            return {
                "step_id": task.get("waiting_approval_step_id", ""),
                "approval_id": task.get("waiting_approval_id", ""),
            }

    def set_current_step(self, task_id: str, step_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            task["current_step_id"] = step_id
            self._save()
        return True

    # ── Internal ──────────────────────────────────────────────

    def _find_step(self, task: dict[str, Any], step_id: str) -> dict[str, Any] | None:
        for step in task.get("steps", []):
            if step.get("step_id") == step_id:
                return step
        return None

    def _transition(self, task_id: str, new_status: TaskStatus) -> dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            current = task["status"]
            if new_status.value not in _VALID_TRANSITIONS.get(current, set()):
                logger.warning("Invalid task transition: %s -> %s", current, new_status.value)
                return None
            task["status"] = new_status.value
            task["updated_at"] = int(time.time() * 1000)
            self._save()
        self._notify(task, new_status.value)
        return task

    def _notify(self, task: dict[str, Any], event_type: str) -> None:
        if self._event_manager is not None:
            try:
                from aegis_schema.models import Event, EventPriority
                event = Event(
                    event_type=f"task.{event_type}",
                    source="task_manager",
                    priority=EventPriority.NORMAL,
                    payload={"task_id": task["task_id"], "title": task["title"], "status": task["status"]},
                )
                self._event_manager.publish(event)
            except Exception:
                logger.debug("Failed to publish task event", exc_info=True)

        if self._audit_manager is not None:
            try:
                from aegis_ai.audit import AuditEntry
                self._audit_manager.append(AuditEntry(
                    action=f"task_{event_type}",
                    actor="task_manager",
                    detail={"task_id": task["task_id"], "title": task["title"], "status": task["status"]},
                ))
            except Exception:
                logger.debug("Failed to record task audit", exc_info=True)

    def _save(self) -> None:
        try:
            with open(self._persist_path, "w", encoding="utf-8") as f:
                for task in self._tasks.values():
                    f.write(json.dumps(task, ensure_ascii=False) + "\n")
        except Exception:
            logger.debug("Failed to save tasks", exc_info=True)

    def _load(self) -> None:
        if not self._persist_path.exists():
            return
        try:
            with open(self._persist_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        task = json.loads(line)
                        task.setdefault(
                            "incident_status",
                            "open"
                            if task.get("status") == TaskStatus.FAILED.value
                            else "",
                        )
                        self._tasks[task["task_id"]] = task
        except Exception:
            logger.debug("Failed to load tasks", exc_info=True)

    def _recover_interrupted_tasks(self) -> None:
        """Move non-resumable persisted work to an honest terminal state."""
        recovered: list[tuple[dict[str, Any], str]] = []
        now_ms = int(time.time() * 1000)
        with self._lock:
            for task in self._tasks.values():
                if task.get("status") not in {
                    TaskStatus.PLANNING.value,
                    TaskStatus.RUNNING.value,
                }:
                    continue
                steps = task.get("steps") or []
                step_statuses = {str(step.get("status") or "") for step in steps}
                goal_checks = list(
                    dict(task.get("goal_graph") or {}).get("verification") or []
                )
                goal_verified = bool(goal_checks) and all(
                    str(item.get("status") or "") == "passed"
                    for item in goal_checks
                )
                if (
                    steps
                    and step_statuses.issubset({"completed", "skipped"})
                    and (not task.get("goal_graph") or goal_verified)
                ):
                    task["status"] = TaskStatus.COMPLETED.value
                    task["result_summary"] = task.get("result_summary") or (
                        "Recovered completed steps after AI Server restart."
                    )
                    task["incident_status"] = "resolved"
                    event_type = TaskStatus.COMPLETED.value
                else:
                    task["status"] = TaskStatus.FAILED.value
                    task["error"] = task.get("error") or (
                        "Execution was interrupted by an AI Server restart. Retry the task."
                    )
                    task["incident_status"] = "open"
                    for step in steps:
                        if step.get("status") == "running":
                            step["status"] = "failed"
                            step["error"] = step.get("error") or task["error"]
                            step["updated_at"] = now_ms
                    event_type = TaskStatus.FAILED.value
                task["updated_at"] = now_ms
                task["completed_at"] = now_ms
                recovered.append((task, event_type))
            if recovered:
                self._save()
        for task, event_type in recovered:
            self._notify(task, event_type)
