"""Planner — task decomposition and prioritization.

STATUS: Skeleton — not yet integrated with LLM or ToolBroker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class TaskStatus(Enum):
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class PlannedTask:
    """A single task decomposed by the Planner."""
    task_id: str = ""
    description: str = ""
    capability_id: str = ""             # Which capability to use
    params: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)  # Task IDs
    priority: int = 5                    # 1=highest, 10=lowest
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class Plan:
    """A plan composed of ordered tasks."""
    plan_id: str = ""
    goal: str = ""
    tasks: list[PlannedTask] = field(default_factory=list)
    created_at_ms: int = 0


class Planner:
    """Decomposes high-level goals into executable steps.

    Architecture reference: docs/architecture.md §5.4
    Currently a skeleton.
    """

    def create_plan(self, goal: str) -> Plan:
        """Create a plan for a given goal.

        TODO: LLM-driven decomposition with ToolBroker capability search.
        """
        import time

        return Plan(
            plan_id=f"plan_{int(time.time() * 1000)}",
            goal=goal,
            created_at_ms=int(time.time() * 1000),
        )

    def next_task(self, plan: Plan) -> PlannedTask | None:
        """Get the next ready task (dependencies satisfied)."""
        completed = {t.task_id for t in plan.tasks if t.status == TaskStatus.COMPLETED}
        for task in plan.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            if all(dep in completed for dep in task.depends_on):
                return task
        return None
