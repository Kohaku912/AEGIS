"""Chroma Semantic Memory — vector DB backed semantic memory.

Uses ChromaDB for vector similarity search with OpenAI embeddings.
Falls back to JSONL if Chroma is unavailable.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from aegis_ai.memory.semantic import Fact, SemanticMemory

logger = logging.getLogger("aegis_ai.memory.chroma_semantic")


class ChromaSemanticMemory(SemanticMemory):
    """Semantic memory with ChromaDB vector search.

    Usage:
        mem = ChromaSemanticMemory(collection_name="aegis_facts")
        mem.add(Fact(content="User prefers dark mode", category="preference"))
        results = mem.search("dark mode")  # Vector similarity search
    """

    def __init__(
        self,
        path: str = "data/semantic.jsonl",
        collection_name: str = "aegis_facts",
        chroma_path: str = "data/chroma",
        embedding_api_key: str | None = None,
        embedding_model: str | None = None,
    ) -> None:
        super().__init__(path)
        self._collection_name = collection_name
        self._chroma_path = chroma_path
        self._embedding_api_key = embedding_api_key or os.getenv("OPENAI_API_KEY", "")
        self._embedding_model = embedding_model or os.getenv("OPENAI_API_MODEL", "text-embedding-3-small")
        self._client = None
        self._collection = None
        self._embedding_fn = None

        self._init_chroma()

    def _init_chroma(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb

            self._client = chromadb.PersistentClient(path=self._chroma_path)

            # Try OpenAI embedding, fall back to default
            try:
                if self._embedding_api_key:
                    from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
                    self._embedding_fn = OpenAIEmbeddingFunction(
                        api_key=self._embedding_api_key,
                        model_name=self._embedding_model,
                    )
            except Exception:
                self._embedding_fn = None

            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                embedding_function=self._embedding_fn,
                metadata={"hnsw:space": "cosine"},
            )

            logger.info(
                "ChromaDB initialized: collection=%s, count=%d",
                self._collection_name,
                self._collection.count(),
            )

        except Exception as e:
            logger.warning("ChromaDB initialization failed, falling back to JSONL: %s", e)
            self._client = None
            self._collection = None

    def add(self, fact: Fact) -> None:
        """Add a fact to both JSONL and ChromaDB."""
        # Always save to JSONL (fallback)
        super().add(fact)

        # Try to add to ChromaDB
        if self._collection is not None:
            try:
                self._collection.upsert(
                    ids=[fact.fact_id],
                    documents=[fact.content],
                    metadatas=[{
                        "category": fact.category,
                        "source": fact.source,
                        "confidence": fact.confidence,
                        "tags": ",".join(fact.tags),
                        "timestamp_ms": fact.timestamp_ms,
                    }],
                )
            except Exception as e:
                logger.warning("ChromaDB add failed: %s", e)

    def search(self, query: str, category: str | None = None, limit: int = 10) -> list[Fact]:
        """Search facts using vector similarity (ChromaDB) or keyword (JSONL fallback)."""
        if self._collection is not None and self._collection.count() > 0:
            try:
                where_filter = {"category": category} if category else None
                results = self._collection.query(
                    query_texts=[query],
                    n_results=min(limit, self._collection.count()),
                    where=where_filter,
                )

                facts = []
                if results and results["ids"] and results["ids"][0]:
                    for i, fact_id in enumerate(results["ids"][0]):
                        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                        fact = Fact(
                            fact_id=fact_id,
                            content=results["documents"][0][i] if results["documents"] else "",
                            category=metadata.get("category", "general"),
                            source=metadata.get("source", ""),
                            confidence=metadata.get("confidence", 1.0),
                            tags=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
                            timestamp_ms=metadata.get("timestamp_ms", 0),
                        )
                        facts.append(fact)
                return facts

            except Exception as e:
                logger.warning("ChromaDB search failed, falling back to JSONL: %s", e)

        # Fallback to keyword search
        return super().search(query, category)

    def search_similar(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search for similar facts with distance scores."""
        if self._collection is None or self._collection.count() == 0:
            return []

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(limit, self._collection.count()),
                include=["documents", "metadatas", "distances"],
            )

            similar = []
            if results and results["ids"] and results["ids"][0]:
                for i, fact_id in enumerate(results["ids"][0]):
                    similar.append({
                        "fact_id": fact_id,
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "distance": results["distances"][0][i] if results["distances"] else 0,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    })
            return similar

        except Exception as e:
            logger.warning("ChromaDB similar search failed: %s", e)
            return []

    def sync_from_advanced_memory(self, advanced_memory: Any) -> int:
        """Sync facts from AdvancedMemory into ChromaDB. Returns count synced."""
        if self._collection is None:
            return 0
        count = 0
        for fid, fact in advanced_memory._facts.items():
            if fact.invalid_at_ms != 0:
                continue
            try:
                self._collection.upsert(
                    ids=[fid],
                    documents=[fact.content],
                    metadatas=[{
                        "subject": fact.subject,
                        "predicate": fact.predicate,
                        "source": fact.source,
                        "confidence": fact.confidence,
                        "valid_at_ms": fact.valid_at_ms,
                    }],
                )
                count += 1
            except Exception as e:
                logger.warning("ChromaDB sync failed for %s: %s", fid, e)
        logger.info("Synced %d facts to ChromaDB", count)
        return count

    def get_all(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get all entries from ChromaDB."""
        if self._collection is None or self._collection.count() == 0:
            return []
        try:
            count = min(limit, self._collection.count())
            results = self._collection.get(limit=count, include=["documents", "metadatas"])
            entries = []
            if results and results["ids"]:
                for i, fid in enumerate(results["ids"]):
                    doc = results["documents"][i] if results["documents"] else ""
                    meta = results["metadatas"][i] if results["metadatas"] else {}
                    entries.append({
                        "fact_id": fid,
                        "content": doc[:200],
                        "subject": meta.get("subject", ""),
                        "predicate": meta.get("predicate", ""),
                        "source": meta.get("source", ""),
                        "confidence": meta.get("confidence", 1.0),
                    })
            return entries
        except Exception as e:
            logger.warning("ChromaDB get_all failed: %s", e)
            return []

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        stats = {
            "jsonl_facts": len(self._facts),
            "chroma_available": self._collection is not None,
            "chroma_count": 0,
        }
        if self._collection is not None:
            try:
                stats["chroma_count"] = self._collection.count()
            except Exception:
                pass
        return stats
