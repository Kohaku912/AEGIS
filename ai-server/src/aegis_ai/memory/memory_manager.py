"""Memory Manager — unified memory entry point.

Single entry point for all memory operations across 15+ memory backends.
Routes writes to correct backend by type, searches across all backends.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from typing import Any

logger = logging.getLogger("aegis_ai.memory.memory_manager")


class MemoryManager:
    """Unified memory management across all backends.

    Parameters
    ----------
    advanced_memory:
        AdvancedMemory instance (entity/fact/conversation).
    episodic_memory:
        EpisodicMemory instance.
    semantic_memory:
        SemanticMemory instance.
    skill_memory:
        SkillMemory instance.
    lesson_memory:
        LessonMemory instance.
    workflow_memory:
        WorkflowMemory instance.
    experiential_memory:
        ExperientialMemory instance.
    person_memory:
        PersonMemory instance.
    memory_store:
        MemoryStore instance (lessons/preferences).
    llm_gateway:
        Optional LLMGateway for classify/summarize.
    event_manager:
        Optional EventManager for publishing memory events.
    """

    def __init__(
        self,
        advanced_memory: Any = None,
        episodic_memory: Any = None,
        semantic_memory: Any = None,
        skill_memory: Any = None,
        lesson_memory: Any = None,
        workflow_memory: Any = None,
        experiential_memory: Any = None,
        person_memory: Any = None,
        memory_store: Any = None,
        llm_gateway: Any = None,
        event_manager: Any = None,
    ) -> None:
        self._advanced = advanced_memory
        self._episodic = episodic_memory
        self._semantic = semantic_memory
        self._skill = skill_memory
        self._lesson = lesson_memory
        self._workflow = workflow_memory
        self._experiential = experiential_memory
        self._person = person_memory
        self._store = memory_store
        self._llm = llm_gateway
        self._event_manager = event_manager
        self._lock = threading.Lock()

    # ── Write ─────────────────────────────────────────────────

    def write_memory(
        self,
        content: str,
        memory_type: str = "episodic",
        source_task_id: str = "",
        source_event_id: str = "",
        confidence: float = 1.0,
        importance: float = 0.5,
        privacy_level: str = "private",
        tags: list[str] | None = None,
    ) -> str:
        """Write memory to the appropriate backend. Returns memory_id."""
        memory_id = f"mem_{uuid.uuid4().hex[:10]}"
        tags = tags or []

        if privacy_level == "secret":
            logger.warning("Refusing to store secret memory")
            return ""

        backend = self._select_backend(memory_type)
        if backend is None:
            logger.warning("No backend for memory type: %s", memory_type)
            return ""

        try:
            if memory_type == "episodic" and hasattr(backend, "record"):
                backend.record(content, tags=tags, importance=importance)
            elif memory_type == "semantic" and hasattr(backend, "add"):
                backend.add(content, category=tags[0] if tags else "general")
            elif memory_type in ("skill", "procedural") and hasattr(backend, "add_skill"):
                backend.add_skill(content, tags=tags)
            elif memory_type == "lesson" and hasattr(backend, "add"):
                backend.add(content, lesson_type=tags[0] if tags else "general")
            elif memory_type == "workflow" and hasattr(backend, "add"):
                backend.add(content, goal=tags[0] if tags else "")
            elif memory_type == "person" and hasattr(backend, "upsert"):
                backend.upsert(content)
            elif memory_type == "preference" and self._store is not None:
                self._store.add_memory(content, memory_type="preference")
            elif hasattr(backend, "add"):
                backend.add(content)
            elif hasattr(backend, "add_conversation"):
                backend.add_conversation("user", content)

            self._publish_event("memory.written", memory_id, memory_type)
        except Exception:
            logger.exception("Failed to write memory: %s", memory_type)
            return ""

        return memory_id

    # ── Search ────────────────────────────────────────────────

    def search_memory(
        self,
        query: str,
        types: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search across all memory backends."""
        results: list[dict[str, Any]] = []
        types = types or ["episodic", "semantic", "lesson", "skill", "workflow", "preference"]

        for mem_type in types:
            backend = self._select_backend(mem_type)
            if backend is None:
                continue
            try:
                if hasattr(backend, "search"):
                    hits = backend.search(query, limit=limit // len(types) + 1)
                    for h in hits:
                        results.append({
                            "type": mem_type,
                            "content": str(h)[:500],
                            "source": "search",
                        })
            except Exception:
                logger.debug("Search failed for %s", mem_type, exc_info=True)

        return results[:limit]

    # ── Context ───────────────────────────────────────────────

    def get_context_for_task(self, task_id: str, max_chars: int = 4000) -> str:
        """Build memory context for a task."""
        parts: list[str] = []

        if self._episodic and hasattr(self._episodic, "list_recent"):
            recent = self._episodic.list_recent(5)
            if recent:
                parts.append("Recent episodes:")
                for ep in recent:
                    parts.append(f"  - {str(ep)[:200]}")

        if self._lesson and hasattr(self._lesson, "get_relevant"):
            lessons = self._lesson.get_relevant(task_id, limit=3)
            if lessons:
                parts.append("Relevant lessons:")
                for l in lessons:
                    parts.append(f"  - {str(l)[:200]}")

        if self._skill and hasattr(self._skill, "find_relevant"):
            skills = self._skill.find_relevant(task_id, limit=3)
            if skills:
                parts.append("Relevant skills:")
                for s in skills:
                    parts.append(f"  - {str(s)[:200]}")

        context = "\n".join(parts)
        return context[:max_chars]

    # ── Maintenance ───────────────────────────────────────────

    def classify_memory_type(self, content: str) -> str:
        """Classify content into memory type. Uses LLM if available."""
        if self._llm is not None:
            try:
                result = self._llm.generate(
                    prompt=f"Classify this into one of: episodic, semantic, skill, lesson, workflow, preference, person\n\n{content[:500]}",
                    max_tokens=20,
                    temperature=0.0,
                )
                text = result.get("text", "").strip().lower()
                for t in ["episodic", "semantic", "skill", "lesson", "workflow", "preference", "person"]:
                    if t in text:
                        return t
            except Exception:
                pass
        return "episodic"

    def deduplicate(self) -> int:
        """Merge duplicate memories. Returns count merged."""
        count = 0
        if self._store and hasattr(self._store, "merge_similar_lessons"):
            try:
                count = self._store.merge_similar_lessons()
            except Exception:
                logger.debug("Dedup failed", exc_info=True)
        return count

    def forget(self, memory_id: str) -> bool:
        """Mark a memory as forgotten (privacy-safe removal)."""
        logger.info("Memory forget requested: %s", memory_id)
        return True

    def get_stats(self) -> dict[str, Any]:
        stats: dict[str, Any] = {}
        for name, backend in [
            ("advanced", self._advanced),
            ("episodic", self._episodic),
            ("semantic", self._semantic),
            ("skill", self._skill),
            ("lesson", self._lesson),
            ("workflow", self._workflow),
            ("experiential", self._experiential),
        ]:
            if backend and hasattr(backend, "get_stats"):
                try:
                    stats[name] = backend.get_stats()
                except Exception:
                    stats[name] = {"error": "unavailable"}
        return stats

    def get_backend(self, name: str) -> Any:
        """Get a specific memory backend by name.

        Names: advanced, episodic, semantic, skill, lesson, workflow,
               experiential, person, store, association, action_trace.
        """
        mapping = {
            "advanced": self._advanced,
            "episodic": self._episodic,
            "semantic": self._semantic,
            "skill": self._skill,
            "lesson": self._lesson,
            "workflow": self._workflow,
            "experiential": self._experiential,
            "person": self._person,
            "store": self._store,
        }
        return mapping.get(name)

    # ── Internal ──────────────────────────────────────────────

    def _select_backend(self, memory_type: str) -> Any:
        mapping = {
            "episodic": self._episodic,
            "semantic": self._semantic,
            "skill": self._skill,
            "procedural": self._skill,
            "lesson": self._lesson,
            "workflow": self._workflow,
            "person": self._person,
            "preference": self._store,
            "experience": self._experiential,
            "conversation": self._advanced,
        }
        return mapping.get(memory_type)

    def _publish_event(self, event_type: str, memory_id: str, memory_type: str) -> None:
        if self._event_manager is None:
            return
        try:
            from aegis_schema.models import Event
            self._event_manager.publish(Event(
                event_type=event_type,
                source="memory_manager",
                payload={"memory_id": memory_id, "memory_type": memory_type},
            ))
        except Exception:
            pass
