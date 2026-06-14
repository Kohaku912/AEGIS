"""Semantic Memory — Knowledge, preferences, and policies.

Organizes knowledge into categories:
- knowledge: facts about the world, technology, etc.
- preference: user preferences, AEGIS preferences
- policy: behavioral rules, guidelines
- project: project-specific knowledge
- skill: learned procedures and techniques

Supports consolidation: dedup, merge, summarization, importance update.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.memory.semantic_memory")


@dataclass
class SemanticEntry:
    """A single semantic memory entry."""
    entry_id: str = ""
    content: str = ""
    category: str = "knowledge"  # knowledge, preference, policy, project, skill
    source: str = ""             # user, conversation, inference, consolidation
    confidence: float = 1.0      # 0.0 to 1.0
    importance: float = 0.5      # 0.0 to 1.0
    tags: list[str] = field(default_factory=list)
    related_entries: list[str] = field(default_factory=list)
    created_at_ms: int = 0
    updated_at_ms: int = 0
    access_count: int = 0
    last_accessed_ms: int = 0
    superseded_by: str = ""      # If this entry was replaced
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "content": self.content,
            "category": self.category,
            "source": self.source,
            "confidence": self.confidence,
            "importance": self.importance,
            "tags": self.tags,
            "related_entries": self.related_entries,
            "created_at_ms": self.created_at_ms,
            "updated_at_ms": self.updated_at_ms,
            "access_count": self.access_count,
            "last_accessed_ms": self.last_accessed_ms,
            "superseded_by": self.superseded_by,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SemanticEntry:
        return cls(
            entry_id=data.get("entry_id", ""),
            content=data.get("content", ""),
            category=data.get("category", "knowledge"),
            source=data.get("source", ""),
            confidence=float(data.get("confidence", 1.0)),
            importance=float(data.get("importance", 0.5)),
            tags=data.get("tags", []),
            related_entries=data.get("related_entries", []),
            created_at_ms=int(data.get("created_at_ms", 0)),
            updated_at_ms=int(data.get("updated_at_ms", 0)),
            access_count=int(data.get("access_count", 0)),
            last_accessed_ms=int(data.get("last_accessed_ms", 0)),
            superseded_by=data.get("superseded_by", ""),
            active=bool(data.get("active", True)),
        )


class SemanticMemory:
    """Knowledge, preference, and policy memory.

    Stores and retrieves semantic knowledge with:
    - Category-based organization
    - Confidence and importance scoring
    - Deduplication and merging
    - Related entry linking

    Usage:
        sm = SemanticMemory()
        sm.add(SemanticEntry(content="User prefers dark mode", category="preference"))
        prefs = sm.get_by_category("preference")
    """

    def __init__(self, path: str = "data/memory/semantic.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: dict[str, SemanticEntry] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            for line in self._path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    data = json.loads(line)
                    entry = SemanticEntry.from_dict(data)
                    self._entries[entry.entry_id] = entry
            logger.info("Loaded %d semantic entries", len(self._entries))
        except Exception as e:
            logger.warning("Failed to load semantic memory: %s", e)

    def _persist(self, entry: SemanticEntry) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    def add(
        self,
        content: str,
        category: str = "knowledge",
        source: str = "",
        confidence: float = 1.0,
        importance: float = 0.5,
        tags: list[str] | None = None,
    ) -> SemanticEntry:
        """Add a new semantic entry."""
        now_ms = int(time.time() * 1000)
        entry = SemanticEntry(
            entry_id=f"sem_{os.urandom(6).hex()}",
            content=content,
            category=category,
            source=source,
            confidence=confidence,
            importance=importance,
            tags=tags or [],
            created_at_ms=now_ms,
            updated_at_ms=now_ms,
        )
        self._entries[entry.entry_id] = entry
        self._persist(entry)
        return entry

    def search(self, query: str, category: str | None = None, limit: int = 10) -> list[SemanticEntry]:
        """Search semantic entries."""
        q = query.lower()
        results = []
        for entry in self._entries.values():
            if not entry.active:
                continue
            text = f"{entry.content} {' '.join(entry.tags)}".lower()
            if q in text:
                if category is None or entry.category == category:
                    entry.access_count += 1
                    entry.last_accessed_ms = int(time.time() * 1000)
                    results.append(entry)
        results.sort(key=lambda e: e.importance, reverse=True)
        return results[:limit]

    def get_by_category(self, category: str) -> list[SemanticEntry]:
        """Get all active entries in a category."""
        return [e for e in self._entries.values() if e.active and e.category == category]

    def get_preferences(self) -> list[SemanticEntry]:
        return self.get_by_category("preference")

    def get_policies(self) -> list[SemanticEntry]:
        return self.get_by_category("policy")

    def get_knowledge(self) -> list[SemanticEntry]:
        return self.get_by_category("knowledge")

    def update_entry(self, entry_id: str, content: str = "", importance: float | None = None, tags: list[str] | None = None) -> None:
        """Update an existing entry."""
        entry = self._entries.get(entry_id)
        if entry:
            if content:
                entry.content = content
            if importance is not None:
                entry.importance = max(0.0, min(1.0, importance))
            if tags is not None:
                entry.tags = tags
            entry.updated_at_ms = int(time.time() * 1000)
            self._persist(entry)

    def supersede(self, old_id: str, new_content: str, source: str = "") -> SemanticEntry | None:
        """Replace an old entry with a new one."""
        old = self._entries.get(old_id)
        if not old:
            return None
        old.active = False
        old.superseded_by = f"sem_{os.urandom(6).hex()}"
        new = self.add(
            content=new_content,
            category=old.category,
            source=source or old.source,
            confidence=old.confidence,
            importance=old.importance,
            tags=old.tags,
        )
        old.superseded_by = new.entry_id
        return new

    def link_entries(self, id1: str, id2: str) -> None:
        """Create bidirectional link between entries."""
        e1 = self._entries.get(id1)
        e2 = self._entries.get(id2)
        if e1 and e2:
            if id2 not in e1.related_entries:
                e1.related_entries.append(id2)
            if id1 not in e2.related_entries:
                e2.related_entries.append(id1)

    def find_duplicates(self) -> list[tuple[SemanticEntry, SemanticEntry]]:
        """Find potential duplicate entries for consolidation."""
        active = [e for e in self._entries.values() if e.active]
        duplicates = []
        for i, e1 in enumerate(active):
            words1 = set(e1.content.lower().split())
            for e2 in active[i+1:]:
                if e1.category != e2.category:
                    continue
                words2 = set(e2.content.lower().split())
                overlap = len(words1 & words2) / max(len(words1 | words2), 1)
                if overlap > 0.7:
                    duplicates.append((e1, e2))
        return duplicates

    def get_context_string(self, max_chars: int = 800) -> str:
        """Get semantic context for LLM prompts."""
        lines = []
        for cat in ["policy", "preference", "knowledge"]:
            entries = self.get_by_category(cat)
            if entries:
                lines.append(f"{cat.title()}:")
                for e in sorted(entries, key=lambda x: x.importance, reverse=True)[:5]:
                    lines.append(f"  - {e.content[:100]}")
        return "\n".join(lines)[:max_chars]

    def get_stats(self) -> dict[str, Any]:
        active = [e for e in self._entries.values() if e.active]
        return {
            "total_entries": len(self._entries),
            "active": len(active),
            "categories": {cat: sum(1 for e in active if e.category == cat) for cat in set(e.category for e in active)},
        }
