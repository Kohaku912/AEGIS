"""Goal Manager — short-term and long-term goals.

STATUS: Skeleton.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class GoalStatus(Enum):
    ACTIVE = auto()
    COMPLETED = auto()
    ABANDONED = auto()
    WAITING = auto()


@dataclass
class Goal:
    """A goal tracked by Ellie."""
    goal_id: str = ""
    description: str = ""
    priority: int = 5           # 1=highest, 10=lowest
    status: GoalStatus = GoalStatus.ACTIVE
    created_at_ms: int = 0


class GoalManager:
    """Tracks short-term and long-term goals."""

    def __init__(self) -> None:
        self._goals: dict[str, Goal] = {}

    def add(self, goal: Goal) -> None:
        self._goals[goal.goal_id] = goal

    def list_active(self) -> list[Goal]:
        return [g for g in self._goals.values() if g.status == GoalStatus.ACTIVE]

    def complete(self, goal_id: str) -> None:
        if g := self._goals.get(goal_id):
            g.status = GoalStatus.COMPLETED
