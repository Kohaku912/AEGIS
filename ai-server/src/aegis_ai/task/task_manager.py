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
    "running": {"completed", "failed", "needs_approval", "cancelled"},
    "needs_approval": {"running", "cancelled", "failed"},
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

    # ── Public API ────────────────────────────────────────────

    def create_task(
        self,
        title: str,
        goal: str = "",
        source: str = "system",
        priority: int = 0,
        parent_task_id: str = "",
    ) -> dict[str, Any]:
        """Create a new task."""
        task_id = f"task_{uuid.uuid4().hex[:10]}"
        now_ms = int(time.time() * 1000)
        task = {
            "task_id": task_id,
            "source": source,
            "title": title,
            "goal": goal,
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
        return self._transition(task_id, TaskStatus.COMPLETED)

    def fail_task(self, task_id: str, error: str = "") -> dict[str, Any] | None:
        """Fail a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            task["error"] = error
        return self._transition(task_id, TaskStatus.FAILED)

    def cancel_task(self, task_id: str, reason: str = "") -> dict[str, Any] | None:
        """Cancel a task."""
        return self._transition(task_id, TaskStatus.CANCELLED)

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
                        self._tasks[task["task_id"]] = task
        except Exception:
            logger.debug("Failed to load tasks", exc_info=True)
