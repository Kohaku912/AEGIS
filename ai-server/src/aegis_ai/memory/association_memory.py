"""Association Memory — Links between memories across systems.

Creates and manages associations between:
- Episodes ↔ Episodes (temporal, causal)
- Episodes ↔ Semantic entries (knowledge derivation)
- Episodes ↔ Persons (involvement)
- Semantic ↔ Semantic (related knowledge)
- Any ↔ Any (cross-system links)

Association types:
- temporal: happened around the same time
- causal: one caused the other
- similar: similar content or pattern
- related: topically related
- derived: one was derived from the other
- contradicts: entries that conflict
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.memory.association")


@dataclass
class Association:
    """A link between two memory entries."""
    association_id: str = ""
    source_id: str = ""           # ID of source memory
    source_type: str = ""         # episode, semantic, person, experiential
    target_id: str = ""           # ID of target memory
    target_type: str = ""         # episode, semantic, person, experiential
    relation: str = "related"     # temporal, causal, similar, related, derived, contradicts
    strength: float = 0.5         # 0.0 (weak) to 1.0 (strong)
    context: str = ""             # Why this association exists
    created_at_ms: int = 0
    last_accessed_ms: int = 0
    access_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "association_id": self.association_id,
            "source_id": self.source_id,
            "source_type": self.source_type,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "relation": self.relation,
            "strength": self.strength,
            "context": self.context,
            "created_at_ms": self.created_at_ms,
            "last_accessed_ms": self.last_accessed_ms,
            "access_count": self.access_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Association:
        return cls(
            association_id=data.get("association_id", ""),
            source_id=data.get("source_id", ""),
            source_type=data.get("source_type", ""),
            target_id=data.get("target_id", ""),
            target_type=data.get("target_type", ""),
            relation=data.get("relation", "related"),
            strength=float(data.get("strength", 0.5)),
            context=data.get("context", ""),
            created_at_ms=int(data.get("created_at_ms", 0)),
            last_accessed_ms=int(data.get("last_accessed_ms", 0)),
            access_count=int(data.get("access_count", 0)),
        )


class AssociationMemory:
    """Manages associations between memories across systems.

    Usage:
        am = AssociationMemory()
        am.link(source_id="ep_abc", source_type="episode",
                target_id="sem_def", target_type="semantic",
                relation="derived", context="Learned from this episode")
        related = am.get_related("ep_abc")
    """

    def __init__(self, path: str = "data/memory/associations.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._associations: dict[str, Association] = {}
        self._source_index: dict[str, list[str]] = {}  # source_id → [association_ids]
        self._target_index: dict[str, list[str]] = {}  # target_id → [association_ids]
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            for line in self._path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    data = json.loads(line)
                    assoc = Association.from_dict(data)
                    self._associations[assoc.association_id] = assoc
                    self._source_index.setdefault(assoc.source_id, []).append(assoc.association_id)
                    self._target_index.setdefault(assoc.target_id, []).append(assoc.association_id)
            logger.info("Loaded %d associations", len(self._associations))
        except Exception as e:
            logger.warning("Failed to load associations: %s", e)

    def _persist(self, assoc: Association) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(assoc.to_dict(), ensure_ascii=False) + "\n")

    def link(
        self,
        source_id: str,
        source_type: str,
        target_id: str,
        target_type: str,
        relation: str = "related",
        strength: float = 0.5,
        context: str = "",
    ) -> Association:
        """Create a link between two memories."""
        # Check for existing link
        existing = self.find_link(source_id, target_id)
        if existing:
            # Strengthen existing link
            existing.strength = min(1.0, existing.strength + 0.1)
            existing.access_count += 1
            existing.last_accessed_ms = int(time.time() * 1000)
            return existing

        assoc = Association(
            association_id=f"assoc_{os.urandom(6).hex()}",
            source_id=source_id,
            source_type=source_type,
            target_id=target_id,
            target_type=target_type,
            relation=relation,
            strength=strength,
            context=context,
            created_at_ms=int(time.time() * 1000),
            last_accessed_ms=int(time.time() * 1000),
        )
        self._associations[assoc.association_id] = assoc
        self._source_index.setdefault(source_id, []).append(assoc.association_id)
        self._target_index.setdefault(target_id, []).append(assoc.association_id)
        self._persist(assoc)
        return assoc

    def find_link(self, source_id: str, target_id: str) -> Association | None:
        """Find an existing link between two memories."""
        for aid in self._source_index.get(source_id, []):
            assoc = self._associations.get(aid)
            if assoc and assoc.target_id == target_id:
                return assoc
        for aid in self._source_index.get(target_id, []):
            assoc = self._associations.get(aid)
            if assoc and assoc.target_id == source_id:
                return assoc
        return None

    def get_related(self, memory_id: str, relation: str | None = None) -> list[Association]:
        """Get all memories related to a given memory."""
        results = []
        for aid in self._source_index.get(memory_id, []):
            assoc = self._associations.get(aid)
            if assoc and (relation is None or assoc.relation == relation):
                assoc.access_count += 1
                assoc.last_accessed_ms = int(time.time() * 1000)
                results.append(assoc)
        for aid in self._target_index.get(memory_id, []):
            assoc = self._associations.get(aid)
            if assoc and (relation is None or assoc.relation == relation):
                assoc.access_count += 1
                assoc.last_accessed_ms = int(time.time() * 1000)
                results.append(assoc)
        return sorted(results, key=lambda a: a.strength, reverse=True)

    def get_related_ids(self, memory_id: str, relation: str | None = None) -> list[str]:
        """Get IDs of all related memories."""
        assocs = self.get_related(memory_id, relation)
        ids = []
        for a in assocs:
            if a.source_id == memory_id:
                ids.append(a.target_id)
            else:
                ids.append(a.source_id)
        return ids

    def strengthen(self, association_id: str, delta: float = 0.1) -> None:
        """Strengthen an association."""
        assoc = self._associations.get(association_id)
        if assoc:
            assoc.strength = min(1.0, assoc.strength + delta)

    def weaken(self, association_id: str, delta: float = 0.1) -> None:
        """Weaken an association."""
        assoc = self._associations.get(association_id)
        if assoc:
            assoc.strength = max(0.0, assoc.strength - delta)

    def find_paths(self, start_id: str, end_id: str, max_depth: int = 3) -> list[list[str]]:
        """Find paths between two memories (BFS)."""
        if start_id == end_id:
            return [[start_id]]

        visited = {start_id}
        queue: list[tuple[str, list[str]]] = [(start_id, [start_id])]
        paths = []

        while queue and len(paths) < 5:
            current, path = queue.pop(0)
            if len(path) > max_depth:
                continue

            related = self.get_related_ids(current)
            for rid in related:
                if rid == end_id:
                    paths.append(path + [rid])
                elif rid not in visited:
                    visited.add(rid)
                    queue.append((rid, path + [rid]))

        return paths

    def get_stats(self) -> dict[str, Any]:
        relations = {}
        for a in self._associations.values():
            relations[a.relation] = relations.get(a.relation, 0) + 1
        return {
            "total_associations": len(self._associations),
            "relations": relations,
            "average_strength": sum(a.strength for a in self._associations.values()) / len(self._associations) if self._associations else 0,
        }
