"""Procedural Memory — successful procedures, failure patterns.

STATUS: Skeleton — in-memory only.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Procedure:
    """A learned procedure (sequence of actions that achieved a goal)."""
    procedure_id: str = ""
    goal: str = ""
    steps: list[str] = field(default_factory=list)     # Capability IDs in order
    success_count: int = 0
    failure_count: int = 0
    last_used_ms: int = 0


class ProceduralMemory:
    """Stores learned procedures and failure patterns."""

    def __init__(self) -> None:
        self._procedures: dict[str, Procedure] = {}

    def add(self, procedure: Procedure) -> None:
        self._procedures[procedure.procedure_id] = procedure

    def find_for_goal(self, goal: str) -> list[Procedure]:
        """Find procedures relevant to a goal."""
        goal_lower = goal.lower()
        return [p for p in self._procedures.values() if goal_lower in p.goal.lower()]

    def record_success(self, procedure_id: str) -> None:
        if proc := self._procedures.get(procedure_id):
            proc.success_count += 1

    def record_failure(self, procedure_id: str) -> None:
        if proc := self._procedures.get(procedure_id):
            proc.failure_count += 1
