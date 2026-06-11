"""Semantic Memory — knowledge, user facts, design documents.

STATUS: Skeleton — in-memory only. Future: vector DB for RAG.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Fact:
    """A stored fact or piece of knowledge."""
    fact_id: str = ""
    content: str = ""
    category: str = ""          # "user_info", "knowledge", "design", "preference"
    confidence: float = 1.0     # 0.0 = uncertain, 1.0 = certain


class SemanticMemory:
    """Stores facts, knowledge, and user information."""

    def __init__(self) -> None:
        self._facts: dict[str, Fact] = {}

    def add(self, fact: Fact) -> None:
        self._facts[fact.fact_id] = fact

    def search(self, query: str) -> list[Fact]:
        """Simple substring search. Future: embedding-based RAG."""
        query_lower = query.lower()
        return [f for f in self._facts.values() if query_lower in f.content.lower()]

    def get(self, fact_id: str) -> Fact | None:
        return self._facts.get(fact_id)
