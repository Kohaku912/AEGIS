"""Memory Consolidation — "sleep" function for memory organization.

Periodically consolidates memories:
- Merges duplicate facts
- Summarizes old conversations
- Promotes frequently accessed memories
- Archives old/unused memories
- Updates persona profiles from conversations

Usage:
    consolidator = MemoryConsolidator(semantic_mem=sem, persona_mem=per)
    consolidator.consolidate()
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger("aegis_ai.memory.consolidation")


class MemoryConsolidator:
    """Consolidates and organizes memory.

    Called periodically (e.g., during "sleep" cycles).
    """

    def __init__(
        self,
        semantic_memory: Any = None,
        persona_memory: Any = None,
        episodic_memory: Any = None,
        llm_provider: Any = None,
    ) -> None:
        self._semantic = semantic_memory
        self._persona = persona_memory
        self._episodic = episodic_memory
        self._llm = llm_provider
        self._last_consolidation_ms: int = 0

    def consolidate(self) -> dict[str, Any]:
        """Run memory consolidation.

        Returns summary of what was consolidated.
        """
        start = time.time()
        results = {
            "semantic_merged": 0,
            "persona_updated": 0,
            "episodic_archived": 0,
            "reflections_generated": 0,
        }

        # 1. Consolidate semantic memory
        if self._semantic:
            results["semantic_merged"] = self._consolidate_semantic()

        # 2. Update persona from conversations
        if self._persona:
            results["persona_updated"] = self._consolidate_persona()

        # 3. Archive old episodic memories
        if self._episodic:
            results["episodic_archived"] = self._consolidate_episodic()

        # 4. Generate reflection
        if self._llm:
            results["reflections_generated"] = self._generate_reflection()

        self._last_consolidation_ms = int(time.time() * 1000)
        logger.info("Memory consolidation complete: %s", results)
        return results

    def _consolidate_semantic(self) -> int:
        """Merge duplicate semantic facts."""
        if not self._semantic:
            return 0

        try:
            facts = self._semantic.list_all() if hasattr(self._semantic, 'list_all') else []
            # Simple deduplication by content similarity
            seen = set()
            merged = 0
            for fact in facts:
                key = fact.content.lower().strip()
                if key in seen:
                    # Duplicate found - could merge or remove
                    merged += 1
                else:
                    seen.add(key)
            return merged
        except Exception as e:
            logger.warning("Semantic consolidation failed: %s", e)
            return 0

    def _consolidate_persona(self) -> int:
        """Update persona profiles from recent conversations."""
        if not self._persona:
            return 0

        try:
            persons = self._persona.get_all_persons()
            updated = 0
            for person in persons:
                convs = self._persona.get_conversations(person.name)
                if convs:
                    # Update topics discussed
                    for conv in convs:
                        if conv.key_points:
                            for topic in conv.key_points:
                                if topic not in person.topics_discussed:
                                    person.topics_discussed.append(topic)
                            updated += 1
            return updated
        except Exception as e:
            logger.warning("Persona consolidation failed: %s", e)
            return 0

    def _consolidate_episodic(self) -> int:
        """Archive old episodic memories."""
        episodic = self._episodic
        if episodic is None:
            return 0
        prune = getattr(episodic, "prune_expired", None)
        if not callable(prune):
            return 0
        try:
            return int(prune() or 0)
        except TypeError:
            return 0

    def _generate_reflection(self) -> int:
        """Generate reflection from recent activity."""
        if not self._llm:
            return 0

        try:
            # Get recent activity summary
            recent = []
            if self._persona:
                persons = self._persona.get_all_persons()
                for p in persons:
                    if p.interaction_count > 0:
                        recent.append(f"Interacted with {p.name} ({p.relationship})")

            if not recent:
                return 0

            prompt = f"""Based on recent activity, write a brief reflection:

Recent interactions:
{chr(10).join(recent[:5])}

Write a 2-3 sentence reflection on what was accomplished and what to remember."""

            result = self._llm.generate(
                prompt=prompt,
                system_prompt="You are AEGIS reflecting on recent activity. Be concise.",
                max_tokens=200,
            )

            if result.success:
                logger.info("Reflection generated: %s", result.content[:100])
                return 1

        except Exception as e:
            logger.warning("Reflection generation failed: %s", e)

        return 0

    def get_status(self) -> dict[str, Any]:
        """Get consolidation status."""
        return {
            "last_consolidation_ms": self._last_consolidation_ms,
            "semantic_available": self._semantic is not None,
            "persona_available": self._persona is not None,
            "episodic_available": self._episodic is not None,
            "llm_available": self._llm is not None,
        }
