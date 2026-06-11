"""Scheduler — interval-based scheduled task execution with LangGraph.

Manages recurring tasks like daily briefing, periodic research,
reflection intervals, and memory summarization.

Safety: All scheduled tasks are read-only or generate proposals.
Level 2+ actions require approval through normal PolicyEngine flow.

Architecture reference: docs/architecture.md §5.11
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

logger = logging.getLogger("aegis_ai.scheduler")


class TaskType(Enum):
    """Types of scheduled tasks."""
    DAILY_BRIEFING = auto()
    PERIODIC_RESEARCH = auto()
    REFLECTION = auto()
    SUPPORT_SUGGESTION = auto()
    MEMORY_SUMMARIZE = auto()
    SELF_DEV_SCAN = auto()
    HEALTH_CHECK = auto()


class TaskStatus(Enum):
    """Status of a scheduled task."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class ScheduledTask:
    """A task scheduled for recurring execution."""
    task_id: str = ""
    name: str = ""
    task_type: TaskType = TaskType.DAILY_BRIEFING
    description: str = ""
    interval_seconds: int = 3600  # Default: 1 hour
    enabled: bool = True
    last_run_ms: int = 0
    next_run_ms: int = 0
    run_count: int = 0
    status: TaskStatus = TaskStatus.PENDING
    params: dict[str, Any] = field(default_factory=dict)
    cooldown_seconds: int = 300  # Min seconds between runs
    daily_budget: int = 10  # Max runs per day
    daily_run_count: int = 0
    daily_reset_ms: int = 0


class Scheduler:
    """Manages scheduled (interval-based) tasks.

    Features:
    - Interval-based scheduling (not cron — simpler, more predictable)
    - Cooldown per task to prevent high-frequency LLM calls
    - Daily budget to limit total runs
    - Task type classification
    - Integration with TriggerEngine for task execution

    Usage:
        scheduler = Scheduler()
        scheduler.add_task(ScheduledTask(
            task_id="daily-briefing",
            name="Daily Briefing",
            task_type=TaskType.DAILY_BRIEFING,
            interval_seconds=86400,  # 24 hours
        ))
        due = scheduler.get_due_tasks()
    """

    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._default_tasks_created = False

    def add_task(self, task: ScheduledTask) -> None:
        """Add a scheduled task."""
        if not task.next_run_ms:
            task.next_run_ms = int(time.time() * 1000) + task.interval_seconds * 1000
        self._tasks[task.task_id] = task

    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task. Returns True if found."""
        return self._tasks.pop(task_id, None) is not None

    def list_tasks(self) -> list[ScheduledTask]:
        """List all scheduled tasks."""
        return list(self._tasks.values())

    def get_task(self, task_id: str) -> ScheduledTask | None:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def get_due_tasks(self) -> list[ScheduledTask]:
        """Return tasks that are due to run.

        A task is due if:
        - enabled is True
        - current time >= next_run_ms
        - cooldown has elapsed since last run
        - daily budget not exceeded
        """
        now_ms = int(time.time() * 1000)
        now_s = time.time()
        due: list[ScheduledTask] = []

        for task in self._tasks.values():
            if not task.enabled:
                continue
            if task.status == TaskStatus.RUNNING:
                continue

            # Check daily budget
            if task.daily_run_count >= task.daily_budget:
                # Reset daily count if a day has passed
                if now_s > task.daily_reset_ms / 1000 + 86400:
                    task.daily_run_count = 0
                    task.daily_reset_ms = now_ms
                else:
                    continue

            # Check cooldown
            if task.last_run_ms > 0:
                elapsed_s = (now_ms - task.last_run_ms) / 1000
                if elapsed_s < task.cooldown_seconds:
                    continue

            # Check interval
            if now_ms >= task.next_run_ms:
                due.append(task)

        return due

    def mark_started(self, task_id: str) -> None:
        """Mark a task as running."""
        if task := self._tasks.get(task_id):
            task.status = TaskStatus.RUNNING

    def mark_completed(self, task_id: str) -> None:
        """Mark a task as completed and schedule next run."""
        now_ms = int(time.time() * 1000)
        if task := self._tasks.get(task_id):
            task.status = TaskStatus.COMPLETED
            task.last_run_ms = now_ms
            task.next_run_ms = now_ms + task.interval_seconds * 1000
            task.run_count += 1
            task.daily_run_count += 1

    def mark_failed(self, task_id: str) -> None:
        """Mark a task as failed."""
        if task := self._tasks.get(task_id):
            task.status = TaskStatus.FAILED
            task.last_run_ms = int(time.time() * 1000)

    def create_default_tasks(self) -> None:
        """Create default scheduled tasks."""
        if self._default_tasks_created:
            return
        self._default_tasks_created = True

        defaults = [
            ScheduledTask(
                task_id="daily-briefing",
                name="Daily Briefing",
                task_type=TaskType.DAILY_BRIEFING,
                description="Prepare a daily briefing for the user",
                interval_seconds=86400,  # 24 hours
                cooldown_seconds=3600,
                daily_budget=1,
            ),
            ScheduledTask(
                task_id="periodic-research",
                name="Periodic Research Watch",
                task_type=TaskType.PERIODIC_RESEARCH,
                description="Check for updates on topics of interest",
                interval_seconds=3600,  # 1 hour
                cooldown_seconds=1800,
                daily_budget=12,
            ),
            ScheduledTask(
                task_id="reflection-interval",
                name="Reflection Interval",
                task_type=TaskType.REFLECTION,
                description="Run reflection on recent actions and events",
                interval_seconds=1800,  # 30 minutes
                cooldown_seconds=900,
                daily_budget=24,
            ),
            ScheduledTask(
                task_id="memory-summarize",
                name="Memory Summarization",
                task_type=TaskType.MEMORY_SUMMARIZE,
                description="Summarize and consolidate memories",
                interval_seconds=7200,  # 2 hours
                cooldown_seconds=3600,
                daily_budget=6,
            ),
            ScheduledTask(
                task_id="self-dev-scan",
                name="Self-Development Scan",
                task_type=TaskType.SELF_DEV_SCAN,
                description="Scan reflection log for improvement opportunities",
                interval_seconds=14400,  # 4 hours
                cooldown_seconds=7200,
                daily_budget=4,
            ),
        ]

        for task in defaults:
            self.add_task(task)
