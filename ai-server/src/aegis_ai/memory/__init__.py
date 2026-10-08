"""Memory System — Episodic, Semantic, Procedural, Reflection, and Unified memory.

``SemanticMemory`` is re-exported from ``semantic_memory`` — the live backend. Until
2026-10-08 this package's root pointed at ``semantic.py``, an unrelated class that merely
shared the name (``DELEGATION.md`` §4 item 30).
"""

from aegis_ai.memory.episodic import EpisodicMemory  # noqa: F401
from aegis_ai.memory.memory_store import MemoryStore  # noqa: F401
from aegis_ai.memory.memory_types import (  # noqa: F401
    FailureType,
    MemoryRecord,
    MemorySource,
    MemoryType,
    ReflectionResult,
    Sensitivity,
    Visibility,
)
from aegis_ai.memory.procedural import ProceduralMemory  # noqa: F401
from aegis_ai.memory.reflection import ReflectionLog  # noqa: F401
from aegis_ai.memory.semantic_memory import SemanticMemory  # noqa: F401
