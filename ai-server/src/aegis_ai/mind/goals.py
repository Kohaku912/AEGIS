"""Goal Manager — short-term, long-term, recurring, and paused goals.

Persists to JSONL for cross-session continuity.
Tracks progress and status for each goal.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path


class GoalStatus(Enum):
    ACTIVE = auto()
    COMPLETED = auto()
    ABANDONED = auto()
    PAUSED = auto()


class GoalType(Enum):
    SHORT_TERM = auto()
    LONG_TERM = auto()
    RECURRING = auto()


@dataclass
class Goal:
    """A goal tracked by AEGIS."""
    goal_id: str = ""
    description: str = ""
    goal_type: GoalType = GoalType.SHORT_TERM
    priority: int = 5           # 1=highest, 10=lowest
    status: GoalStatus = GoalStatus.ACTIVE
    progress: float = 0.0       # 0.0 = not started, 1.0 = complete
    tags: list[str] = field(default_factory=list)
    created_at_ms: int = 0
    updated_at_ms: int = 0
    completed_at_ms: int = 0
    notes: str = ""


class GoalManager:
    """Tracks goals with JSONL persistence."""

    def __init__(self, path: str = "data/mind_goals.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._goals: dict[str, Goal] = {}
        self._lock = threading.Lock()
        self._load()

    def add(self, goal: Goal) -> None:
        """Add a new goal (persisted)."""
        if not goal.goal_id:
            goal.goal_id = f"goal_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
        if not goal.created_at_ms:
            goal.created_at_ms = int(time.time() * 1000)
        goal.updated_at_ms = goal.created_at_ms
        with self._lock:
            self._goals[goal.goal_id] = goal
            self._persist()

    def update_progress(self, goal_id: str, progress: float, notes: str = "") -> None:
        """Update goal progress (persisted)."""
        with self._lock:
            if g := self._goals.get(goal_id):
                g.progress = max(0.0, min(1.0, progress))
                g.updated_at_ms = int(time.time() * 1000)
                if notes:
                    g.notes = notes
                if progress >= 1.0:
                    g.status = GoalStatus.COMPLETED
                    g.completed_at_ms = int(time.time() * 1000)
                self._persist()

    def complete(self, goal_id: str) -> None:
        """Mark a goal as completed."""
        self.update_progress(goal_id, 1.0)

    def pause(self, goal_id: str) -> None:
        """Pause a goal."""
        with self._lock:
            if g := self._goals.get(goal_id):
                g.status = GoalStatus.PAUSED
                g.updated_at_ms = int(time.time() * 1000)
                self._persist()

    def abandon(self, goal_id: str) -> None:
        """Abandon a goal."""
        with self._lock:
            if g := self._goals.get(goal_id):
                g.status = GoalStatus.ABANDONED
                g.updated_at_ms = int(time.time() * 1000)
                self._persist()

    def list_active(self) -> list[Goal]:
        """List active goals, sorted by priority."""
        return sorted(
            [g for g in self._goals.values() if g.status == GoalStatus.ACTIVE],
            key=lambda g: g.priority,
        )

    def list_all(self) -> list[Goal]:
        return list(self._goals.values())

    def get(self, goal_id: str) -> Goal | None:
        return self._goals.get(goal_id)

    def to_context_string(self) -> str:
        """Return active goals as a string for ContextBuilder."""
        active = self.list_active()
        if not active:
            return "Goals: none"
        lines = ["Goals:"]
        for g in active[:5]:
            lines.append(f"  [{g.priority}] {g.description} (progress={g.progress:.0%})")
        return "\n".join(lines)

    def _persist(self) -> None:
        record = {
            "goals": [
                {
                    "goal_id": g.goal_id, "description": g.description,
                    "goal_type": g.goal_type.name, "priority": g.priority,
                    "status": g.status.name, "progress": g.progress,
                    "tags": g.tags, "notes": g.notes,
                    "created_at_ms": g.created_at_ms, "updated_at_ms": g.updated_at_ms,
                    "completed_at_ms": g.completed_at_ms,
                }
                for g in self._goals.values()
            ],
            "timestamp_ms": int(time.time() * 1000),
        }
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                last = json.loads(lines[-1])
                for g in last.get("goals", []):
                    goal = Goal(
                        goal_id=g["goal_id"], description=g["description"],
                        goal_type=GoalType[g.get("goal_type", "SHORT_TERM")],
                        priority=g.get("priority", 5),
                        status=GoalStatus[g.get("status", "ACTIVE")],
                        progress=g.get("progress", 0.0),
                        tags=g.get("tags", []), notes=g.get("notes", ""),
                        created_at_ms=g.get("created_at_ms", 0),
                        updated_at_ms=g.get("updated_at_ms", 0),
                        completed_at_ms=g.get("completed_at_ms", 0),
                    )
                    self._goals[goal.goal_id] = goal
        except (json.JSONDecodeError, OSError, KeyError):
            pass
