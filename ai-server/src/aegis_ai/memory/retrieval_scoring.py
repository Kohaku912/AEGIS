"""Shared lightweight retrieval scoring helpers for memory backends."""

from __future__ import annotations

import re
import time
from typing import Iterable

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_\u3040-\u30ff\u3400-\u9fff]{2,}")


def query_tokens(query: str) -> set[str]:
    return {token for token in _TOKEN_RE.findall((query or "").lower())}


def _ngrams(text: str, size: int = 3) -> set[str]:
    normalized = re.sub(r"\s+", " ", (text or "").lower()).strip()
    if len(normalized) < size:
        return {normalized} if normalized else set()
    return {normalized[index : index + size] for index in range(len(normalized) - size + 1)}


def text_relevance_score(query: str, *texts: str) -> float:
    """Compute a lightweight fuzzy relevance score without external dependencies."""
    normalized_query = (query or "").lower().strip()
    if not normalized_query:
        return 0.0
    blob = " ".join(texts).lower()
    if not blob.strip():
        return 0.0

    tokens = query_tokens(normalized_query)
    blob_tokens = query_tokens(blob)
    token_overlap = len(tokens & blob_tokens) / max(1, len(tokens)) if tokens else 0.0
    exact_bonus = 1.0 if normalized_query in blob else 0.0
    blob_ngrams = _ngrams(blob)
    query_ngrams = _ngrams(normalized_query)
    ngram_overlap = (
        len(query_ngrams & blob_ngrams) / max(1, len(query_ngrams))
        if query_ngrams
        else 0.0
    )
    prefix_bonus = 0.2 if any(token.startswith(normalized_query) for token in blob_tokens) else 0.0
    return exact_bonus * 1.5 + token_overlap * 1.2 + ngram_overlap * 0.8 + prefix_bonus


def recency_bonus(timestamp_ms: int, *, half_life_hours: float = 168.0) -> float:
    if timestamp_ms <= 0:
        return 0.0
    age_hours = max(0.0, (time.time() * 1000 - timestamp_ms) / 3_600_000)
    return max(0.0, 1.0 - age_hours / max(1.0, half_life_hours))


def combined_text_score(
    query: str,
    *,
    texts: Iterable[str],
    importance: float = 0.0,
    confidence: float = 0.0,
    timestamp_ms: int = 0,
) -> float:
    relevance = text_relevance_score(query, *texts)
    if relevance <= 0:
        return 0.0
    return relevance + max(0.0, importance) * 0.25 + max(0.0, confidence) * 0.15 + recency_bonus(timestamp_ms) * 0.2
