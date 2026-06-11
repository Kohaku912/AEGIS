"""Reflection Log — self-analysis and improvement notes.

STATUS: Skeleton — in-memory only.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Reflection:
    """A self-reflection entry."""
    reflection_id: str = ""
    summary: str = ""               # What happened
    what_worked: list[str] = field(default_factory=list)
    what_failed: list[str] = field(default_factory=list)
    improvement_ideas: list[str] = field(default_factory=list)
    timestamp_ms: int = 0


class ReflectionLog:
    """Stores self-analysis for continuous improvement."""

    def __init__(self) -> None:
        self._reflections: list[Reflection] = []

    def add(self, reflection: Reflection) -> None:
        self._reflections.append(reflection)

    def list_recent(self, n: int = 20) -> list[Reflection]:
        return self._reflections[-n:] if n < len(self._reflections) else list(self._reflections)

    def get_improvement_ideas(self) -> list[str]:
        """Collect all improvement ideas from recent reflections."""
        ideas: list[str] = []
        for r in self.list_recent(20):
            ideas.extend(r.improvement_ideas)
        return ideas
