"""Scheduler — cron-like scheduled task execution.

STATUS: Skeleton — not yet integrated with Autonomous Loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScheduledTask:
    """A task scheduled for recurring execution."""
    task_id: str = ""
    name: str = ""
    description: str = ""
    cron_expression: str = ""          # e.g. "0 9 * * *" for 9 AM daily
    action: str = ""                   # What to trigger (NOTIFY, RESEARCH, etc.)
    params: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    last_run_ms: int = 0
    run_count: int = 0


class Scheduler:
    """Manages scheduled (cron-like) tasks.

    Currently a skeleton. When implemented, this will:
    - Parse cron expressions
    - Trigger Autonomous Loop with TaskRequests
    - Track last run times
    """

    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}

    def add_task(self, task: ScheduledTask) -> None:
        self._tasks[task.task_id] = task

    def remove_task(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def list_tasks(self) -> list[ScheduledTask]:
        return list(self._tasks.values())

    def get_due_tasks(self) -> list[ScheduledTask]:
        """Return tasks that are due to run.

        TODO: Implement cron expression evaluation.
        """
        import time

        now_ms = int(time.time() * 1000)
        due: list[ScheduledTask] = []
        for task in self._tasks.values():
            if not task.enabled:
                continue
            # Placeholder: run if never run before
            if task.last_run_ms == 0:
                due.append(task)
        return due
