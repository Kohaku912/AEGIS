"""The ``Fact`` record type — knowledge, user facts, design documents.

The JSONL-backed ``SemanticMemory`` that used to live here was deleted 2026-10-08
(``DELEGATION.md`` §4 item 30). It was one of two unrelated classes that merely
shared the name; the runtime has always used the other one
(``memory/semantic_memory.py``), and the Chroma subclass that did extend this one
went with its own module (item 29). ``Fact`` stays because
``backup/import_restore.py`` builds one when it restores a semantic backup.
"""

from __future__ import annotations

from dataclasses import dataclass, field


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
