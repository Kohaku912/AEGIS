"""Memory Factory — creates memory providers based on configuration.

Automatically selects ChromaDB if available, falls back to JSONL.

Usage:
    semantic_mem = create_semantic_memory()
    episodic_mem = create_episodic_memory()
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("aegis_ai.memory.factory")


def create_semantic_memory(
    path: str = "data/semantic.jsonl",
    use_chroma: bool = True,
    chroma_path: str = "data/chroma",
    embedding_api_key: str | None = None,
) -> Any:
    """Create semantic memory provider.

    Args:
        path: JSONL file path for fallback
        use_chroma: Try ChromaDB first
        chroma_path: ChromaDB storage path
        embedding_api_key: OpenAI embedding API key

    Returns:
        SemanticMemory or ChromaSemanticMemory instance
    """
    if use_chroma:
        try:
            from aegis_ai.memory.chroma_semantic import ChromaSemanticMemory
            mem = ChromaSemanticMemory(
                path=path,
                chroma_path=chroma_path,
                embedding_api_key=embedding_api_key,
            )
            if mem._collection is not None:
                logger.info("Using ChromaDB for semantic memory")
                return mem
        except Exception as e:
            logger.warning("ChromaDB not available, falling back to JSONL: %s", e)

    from aegis_ai.memory.semantic import SemanticMemory
    logger.info("Using JSONL for semantic memory")
    return SemanticMemory(path=path)


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
