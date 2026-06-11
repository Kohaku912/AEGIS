"""Procedural Memory — successful procedures, failure patterns, tool usage tips.

Persists to JSONL. Tracks confidence through success/failure counts.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Procedure:
    """A learned procedure (sequence of actions that achieved a goal)."""
    procedure_id: str = ""
    goal: str = ""
    description: str = ""
    steps: list[str] = field(default_factory=list)     # Capability IDs in order
    tags: list[str] = field(default_factory=list)      # "successful", "failed", "tool_tip"
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.5
    last_used_ms: int = 0
    timestamp_ms: int = 0

    @property
    def total_attempts(self) -> int:
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.success_count / self.total_attempts


class ProceduralMemory:
    """Stores learned procedures with JSONL persistence."""

    def __init__(self, path: str = "data/procedural.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._procedures: dict[str, Procedure] = {}
        self._lock = threading.Lock()

    def add(self, procedure: Procedure) -> None:
        if not procedure.procedure_id:
            procedure.procedure_id = f"proc_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
        if not procedure.timestamp_ms:
            procedure.timestamp_ms = int(time.time() * 1000)
        if procedure.total_attempts > 0:
            procedure.confidence = procedure.success_rate
        self._persist(procedure)
        with self._lock:
            self._procedures[procedure.procedure_id] = procedure

    def find_for_goal(self, goal: str) -> list[Procedure]:
        goal_lower = goal.lower()
        with self._lock:
            procs = list(self._procedures.values())
        return [p for p in procs if goal_lower in p.goal.lower()]

    def get_successful(self) -> list[Procedure]:
        return [p for p in self._procedures.values() if p.success_count > 0]

    def get_failure_patterns(self) -> list[Procedure]:
        return [p for p in self._procedures.values() if p.failure_count > 0]

    def get_tool_tips(self) -> list[Procedure]:
        return [p for p in self._procedures.values() if "tool_tip" in p.tags]

    def record_success(self, procedure_id: str) -> None:
        if proc := self._procedures.get(procedure_id):
            proc.success_count += 1
            proc.last_used_ms = int(time.time() * 1000)
            proc.confidence = proc.success_rate

    def record_failure(self, procedure_id: str) -> None:
        if proc := self._procedures.get(procedure_id):
            proc.failure_count += 1
            proc.last_used_ms = int(time.time() * 1000)
            proc.confidence = proc.success_rate

    def _persist(self, procedure: Procedure) -> None:
        record = {
            "procedure_id": procedure.procedure_id, "goal": procedure.goal,
            "description": procedure.description, "steps": procedure.steps,
            "tags": procedure.tags, "success_count": procedure.success_count,
            "failure_count": procedure.failure_count,
            "confidence": procedure.confidence, "last_used_ms": procedure.last_used_ms,
            "timestamp_ms": procedure.timestamp_ms,
        }
        with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def clear(self) -> None:
        with self._lock:
            self._procedures.clear()
