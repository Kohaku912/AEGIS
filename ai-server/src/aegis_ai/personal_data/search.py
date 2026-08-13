"""Temporal + FTS5 + Chroma (hash embedding) search."""

from __future__ import annotations

import hashlib
import logging
import math
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.personal_data.search")

_TOKEN_RE = re.compile(r"[\w.-]+", re.UNICODE)
_DIM = 128


def hash_embedding(text: str) -> list[float]:
    vec = [0.0] * _DIM
    for token in _TOKEN_RE.findall((text or "").lower()):
        digest = hashlib.blake2s(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:2], "little") % _DIM
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vec[index] += sign
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class VectorIndex:
    def __init__(self, data_dir: str | Path) -> None:
        self._path = str(Path(data_dir) / "chroma" / "personal_data")
        self._collection = None
        try:
            import chromadb
            from aegis_ai.capability_index import _HashEmbeddingFunction

            Path(self._path).mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=self._path)
            self._collection = client.get_or_create_collection(
                name="personal_data",
                embedding_function=_HashEmbeddingFunction(),
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            logger.debug("Chroma personal_data collection unavailable; FTS only", exc_info=True)

    def upsert(self, event_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        if self._collection is None or not text.strip():
            return
        try:
            self._collection.upsert(
                ids=[event_id],
                documents=[text],
                metadatas=[metadata or {"event_id": event_id}],
            )
        except Exception:
            logger.debug("Chroma upsert failed", exc_info=True)

    def query(self, text: str, *, limit: int = 20) -> list[str]:
        if self._collection is None or not text.strip():
            return []
        try:
            result = self._collection.query(query_texts=[text], n_results=limit)
            return list((result.get("ids") or [[]])[0])
        except Exception:
            logger.debug("Chroma query failed", exc_info=True)
            return []


def merge_search(
    *,
    fts_hits: list[dict[str, Any]],
    vector_ids: list[str],
    lookup,
    limit: int,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in fts_hits:
        event_id = str(item.get("id") or "")
        if event_id and event_id not in seen:
            seen.add(event_id)
            item = dict(item)
            item["match"] = "keyword"
            out.append(item)
        if len(out) >= limit:
            return out
    for event_id in vector_ids:
        if event_id in seen:
            continue
        item = lookup(event_id)
        if not item:
            continue
        seen.add(event_id)
        item = dict(item)
        item["match"] = "semantic"
        out.append(item)
        if len(out) >= limit:
            break
    return out
