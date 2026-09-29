"""Lesson Memory — Extracted lessons from action traces.

Lessons are extracted during consolidation from successful and failed
action traces. They represent reusable knowledge about what works
and what doesn't.

Inspired by Reflexion and ExpeL.

Usage:
    lm = LessonMemory()
    lm.add(Lesson(
        content="AGORA API requires authentication before reading posts",
        lesson_type="failure_analysis",
        source_trace_id="trace_abc",
        applicability="agora.*",
    ))
    relevant = lm.get_relevant("Read AGORA posts")
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.memory.retrieval_scoring import combined_text_score

logger = logging.getLogger("aegis_ai.memory.lesson")


@dataclass
class Lesson:
    """A lesson extracted from action traces."""
    lesson_id: str = ""
    content: str = ""
    lesson_type: str = "general"  # success_pattern, failure_analysis, optimization, warning
    source_trace_id: str = ""
    source_goal: str = ""
    applicability: str = ""       # Regex or keyword pattern for when this applies
    importance: float = 0.6
    confidence: float = 0.7
    times_applied: int = 0
    times_helpful: int = 0
    tags: list[str] = field(default_factory=list)
    created_at_ms: int = 0
    last_applied_ms: int = 0
    active: bool = True

    @property
    def helpfulness_rate(self) -> float:
        return self.times_helpful / self.times_applied if self.times_applied > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id, "content": self.content,
            "lesson_type": self.lesson_type, "source_trace_id": self.source_trace_id,
            "source_goal": self.source_goal, "applicability": self.applicability,
            "importance": self.importance, "confidence": self.confidence,
            "times_applied": self.times_applied, "times_helpful": self.times_helpful,
            "tags": self.tags, "created_at_ms": self.created_at_ms,
            "last_applied_ms": self.last_applied_ms, "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Lesson:
        return cls(
            lesson_id=data.get("lesson_id", ""), content=data.get("content", ""),
            lesson_type=data.get("lesson_type", "general"),
            source_trace_id=data.get("source_trace_id", ""),
            source_goal=data.get("source_goal", ""),
            applicability=data.get("applicability", ""),
            importance=float(data.get("importance", 0.6)),
            confidence=float(data.get("confidence", 0.7)),
            times_applied=int(data.get("times_applied", 0)),
            times_helpful=int(data.get("times_helpful", 0)),
            tags=data.get("tags", []),
            created_at_ms=int(data.get("created_at_ms", 0)),
            last_applied_ms=int(data.get("last_applied_ms", 0)),
            active=bool(data.get("active", True)),
        )


class LessonMemory:
    """Stores and retrieves lessons from action traces.

    Usage:
        lm = LessonMemory()
        lm.add(Lesson(content="...", lesson_type="failure_analysis"))
        relevant = lm.get_relevant("AGORA authentication")
    """

    def __init__(self, path: str = "data/memory/lessons.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lessons: dict[str, Lesson] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            for line in self._path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    lesson = Lesson.from_dict(json.loads(line))
                    self._lessons[lesson.lesson_id] = lesson
            logger.info("Loaded %d lessons", len(self._lessons))
        except Exception as e:
            logger.warning("Failed to load lessons: %s", e)

    def _persist(self, lesson: Lesson) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(lesson.to_dict(), ensure_ascii=False) + "\n")

    def add(self, content: str, lesson_type: str = "general", source_trace_id: str = "", source_goal: str = "", applicability: str = "", importance: float = 0.6, tags: list[str] | None = None) -> Lesson:
        """Add a new lesson."""
        lesson = Lesson(
            lesson_id=f"lesson_{os.urandom(6).hex()}",
            content=content, lesson_type=lesson_type,
            source_trace_id=source_trace_id, source_goal=source_goal,
            applicability=applicability, importance=importance,
            tags=tags or [], created_at_ms=int(time.time() * 1000),
        )
        self._lessons[lesson.lesson_id] = lesson
        self._persist(lesson)
        return lesson

    def _score_lesson(self, goal: str, lesson: Lesson) -> float:
        score = combined_text_score(
            goal,
            texts=[
                lesson.content,
                lesson.lesson_type,
                lesson.source_goal,
                lesson.applicability.replace("|", " "),
                " ".join(lesson.tags),
            ],
            importance=lesson.importance + lesson.helpfulness_rate * 0.25,
            confidence=lesson.confidence,
            timestamp_ms=lesson.last_applied_ms or lesson.created_at_ms,
        )
        if score <= 0:
            return 0.0
        return score + lesson.helpfulness_rate * 0.2

    def get_relevant(self, goal: str, count: int = 5) -> list[Lesson]:
        """Get lessons relevant to a goal."""
        scored: list[tuple[float, Lesson]] = []
        for lesson in self._lessons.values():
            if not lesson.active:
                continue
            score = self._score_lesson(goal, lesson)
            if score > 0.1:
                scored.append((score, lesson))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [l for _, l in scored[:count]]

    def record_application(self, lesson_id: str, helpful: bool) -> None:
        """Record that a lesson was applied and whether it was helpful."""
        lesson = self._lessons.get(lesson_id)
        if lesson:
            lesson.times_applied += 1
            if helpful:
                lesson.times_helpful += 1
            lesson.last_applied_ms = int(time.time() * 1000)

    def get_by_type(self, lesson_type: str) -> list[Lesson]:
        return [l for l in self._lessons.values() if l.active and l.lesson_type == lesson_type]

    def get_stats(self) -> dict[str, Any]:
        active = [l for l in self._lessons.values() if l.active]
        return {
            "total": len(self._lessons), "active": len(active),
            "types": {t: sum(1 for l in active if l.lesson_type == t) for t in set(l.lesson_type for l in active)},
        }
