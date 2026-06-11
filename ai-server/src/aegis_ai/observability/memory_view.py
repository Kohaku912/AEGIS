"""Memory View — provides memory system overview for dashboard display."""

from __future__ import annotations

from typing import Any


class MemoryView:
    """Read-only view of memory systems for dashboard display."""

    def __init__(
        self,
        episodic_memory: Any = None,
        semantic_memory: Any = None,
        procedural_memory: Any = None,
        reflection_log: Any = None,
    ) -> None:
        self._episodic = episodic_memory
        self._semantic = semantic_memory
        self._procedural = procedural_memory
        self._reflection = reflection_log

    def get_episodic_recent(self, n: int = 20) -> list[dict[str, Any]]:
        """Get recent episodic memories."""
        if not self._episodic:
            return []
        episodes = self._episodic.list_recent(n)
        return [
            {
                "episode_id": e.episode_id,
                "summary": e.summary,
                "category": e.category,
                "timestamp_ms": e.timestamp_ms,
            }
            for e in episodes
        ]

    def get_semantic_facts(self, n: int = 20) -> list[dict[str, Any]]:
        """Get recent semantic facts."""
        if not self._semantic:
            return []
        facts = self._semantic.list_recent(n)
        return [
            {
                "fact_id": f.fact_id,
                "content": f.content,
                "category": f.category,
                "source": f.source,
                "confidence": f.confidence,
            }
            for f in facts
        ]

    def get_procedural_memories(self, n: int = 20) -> list[dict[str, Any]]:
        """Get procedural memories."""
        if not self._procedural:
            return []
        procs = self._procedural.list_recent(n)
        return [
            {
                "procedure_id": p.procedure_id,
                "goal": p.goal,
                "steps": p.steps,
                "confidence": p.confidence,
                "success_count": p.success_count,
                "failure_count": p.failure_count,
            }
            for p in procs
        ]

    def get_reflections(self, n: int = 20) -> list[dict[str, Any]]:
        """Get recent reflections."""
        if not self._reflection:
            return []
        refs = self._reflection.list_recent(n)
        return [
            {
                "reflection_id": r.reflection_id,
                "summary": r.summary,
                "what_worked": r.what_worked,
                "what_failed": r.what_failed,
                "improvement_ideas": r.improvement_ideas,
                "timestamp_ms": r.timestamp_ms,
            }
            for r in refs
        ]

    def get_summary(self) -> dict[str, Any]:
        """Get memory system summary."""
        return {
            "episodic_count": len(self._episodic.list_recent(10000)) if self._episodic else 0,
            "semantic_count": len(self._semantic.list_recent(10000)) if self._semantic else 0,
            "procedural_count": len(self._procedural.list_recent(10000)) if self._procedural else 0,
            "reflection_count": len(self._reflection.list_recent(10000)) if self._reflection else 0,
        }
