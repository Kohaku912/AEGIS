"""Reflection Log — self-analysis and improvement notes.

Persists to JSONL. Linked to episodes/actions for traceability.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Reflection:
    """A self-reflection entry linked to specific events/actions."""
    reflection_id: str = ""
    summary: str = ""                      # What happened
    what_worked: list[str] = field(default_factory=list)
    what_failed: list[str] = field(default_factory=list)
    improvement_ideas: list[str] = field(default_factory=list)
    next_experiment: str = ""              # What to try next
    linked_event_ids: list[str] = field(default_factory=list)
    linked_action_id: str = ""
    timestamp_ms: int = 0


class ReflectionLog:
    """Stores self-analysis with JSONL persistence."""

    def __init__(self, path: str = "data/reflection.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._reflections: list[Reflection] = []
        self._lock = threading.Lock()

    def add(self, reflection: Reflection) -> None:
        if not reflection.reflection_id:
            reflection.reflection_id = f"refl_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
        if not reflection.timestamp_ms:
            reflection.timestamp_ms = int(time.time() * 1000)
        record = {
            "reflection_id": reflection.reflection_id, "summary": reflection.summary,
            "what_worked": reflection.what_worked, "what_failed": reflection.what_failed,
            "improvement_ideas": reflection.improvement_ideas,
            "next_experiment": reflection.next_experiment,
            "linked_event_ids": reflection.linked_event_ids,
            "linked_action_id": reflection.linked_action_id,
            "timestamp_ms": reflection.timestamp_ms,
        }
        with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._reflections.append(reflection)

    def list_recent(self, n: int = 20) -> list[Reflection]:
        with self._lock:
            refs = list(self._reflections)
        return refs[-n:] if n < len(refs) else refs

    def get_improvement_ideas(self) -> list[str]:
        ideas: list[str] = []
        for r in self.list_recent(20):
            ideas.extend(r.improvement_ideas)
        return ideas

    def find_by_event(self, event_id: str) -> list[Reflection]:
        return [r for r in self._reflections if event_id in r.linked_event_ids]

    def clear(self) -> None:
        with self._lock:
            self._reflections.clear()
