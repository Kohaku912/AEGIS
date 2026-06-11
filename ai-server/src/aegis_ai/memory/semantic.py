"""Semantic Memory — knowledge, user facts, design documents.

Persists to JSONL. Future: vector DB for RAG.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Fact:
    """A stored fact or piece of knowledge."""
    fact_id: str = ""
    content: str = ""
    category: str = "general"      # "user_info", "knowledge", "design", "preference", "project"
    source: str = ""               # Where this fact came from ("user", "conversation", "inference")
    confidence: float = 1.0        # 0.0 = uncertain, 1.0 = certain
    tags: list[str] = field(default_factory=list)
    timestamp_ms: int = 0


class SemanticMemory:
    """Stores facts and knowledge with JSONL persistence."""

    def __init__(self, path: str = "data/semantic.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._facts: dict[str, Fact] = {}
        self._lock = threading.Lock()

    def add(self, fact: Fact) -> None:
        if not fact.fact_id:
            fact.fact_id = f"fact_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
        if not fact.timestamp_ms:
            fact.timestamp_ms = int(time.time() * 1000)
        record = {
            "fact_id": fact.fact_id, "content": fact.content,
            "category": fact.category, "source": fact.source,
            "confidence": fact.confidence, "tags": fact.tags,
            "timestamp_ms": fact.timestamp_ms,
        }
        with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._facts[fact.fact_id] = fact

    def search(self, query: str, category: str | None = None) -> list[Fact]:
        query_lower = query.lower()
        with self._lock:
            facts = list(self._facts.values())
        results = [f for f in facts if query_lower in f.content.lower() or query_lower in " ".join(f.tags).lower()]
        if category:
            results = [f for f in results if f.category == category]
        return results

    def get(self, fact_id: str) -> Fact | None:
        return self._facts.get(fact_id)

    def list_by_category(self, category: str) -> list[Fact]:
        return [f for f in self._facts.values() if f.category == category]

    def clear(self) -> None:
        with self._lock:
            self._facts.clear()
