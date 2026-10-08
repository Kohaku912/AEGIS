"""Memory Factory — creates memory providers based on configuration.

The ChromaDB-selecting semantic factory was deleted 2026-10-08
(``DELEGATION.md`` §4 item 29): nothing called it, and the vector branch it
selected was itself unreachable. The three helpers below build the JSONL stores.

Usage:
    episodic_mem = create_episodic_memory()
    procedural_mem = create_procedural_memory()
    reflection_log = create_reflection_log()
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.memory.factory")


def create_episodic_memory(path: str = "data/episodic.jsonl") -> Any:
    """Create episodic memory provider."""
    from aegis_ai.memory.episodic import EpisodicMemory
    return EpisodicMemory(path=path)


def create_procedural_memory(path: str = "data/procedural.jsonl") -> Any:
    """Create procedural memory provider."""
    from aegis_ai.memory.procedural import ProceduralMemory
    return ProceduralMemory(path=path)


def create_reflection_log(path: str = "data/reflection.jsonl") -> Any:
    """Create reflection log."""
    from aegis_ai.memory.reflection import ReflectionLog
    return ReflectionLog(path=path)
