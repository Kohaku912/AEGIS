"""Source Ranker — ranks sources by reliability and relevance."""

from __future__ import annotations

from dataclasses import dataclass, field

from aegis_ai.research.source import SourceNote


@dataclass
class RankedSource:
    """A source with its rank score."""
    source: SourceNote
    score: float = 0.0
    rank: int = 0


class SourceRanker:
    """Ranks sources by reliability, relevance, and recency.

    Simple heuristic-based ranking. Future: ML-based relevance scoring.
    """

    # Domain priority: official > documentation > news > blog > forum > unknown
    DOMAIN_PRIORITY: dict[str, float] = {
        "official": 1.0,
        "documentation": 0.9,
        "news": 0.6,
        "blog": 0.4,
        "forum": 0.3,
        "unknown": 0.2,
    }

    # Reliability priority: high > medium > unknown > low > unverified
    RELIABILITY_PRIORITY: dict[str, float] = {
        "high": 1.0,
        "medium": 0.7,
        "unknown": 0.4,
        "low": 0.2,
        "unverified": 0.1,
    }

    def rank(self, sources: list[SourceNote]) -> list[RankedSource]:
        """Rank sources by composite score."""
        ranked = []
        for source in sources:
            domain_score = self.DOMAIN_PRIORITY.get(source.domain_category, 0.2)
            reliability_score = self.RELIABILITY_PRIORITY.get(source.reliability_hint, 0.1)
            # Content richness: more text = potentially more useful
            content_score = min(source.full_text_length / 5000, 1.0) if source.full_text_length > 0 else 0.1
            # Composite
            score = domain_score * 0.4 + reliability_score * 0.4 + content_score * 0.2
            ranked.append(RankedSource(source=source, score=score))

        ranked.sort(key=lambda r: r.score, reverse=True)
        for i, r in enumerate(ranked):
            r.rank = i + 1
        return ranked

    def get_top(self, sources: list[SourceNote], n: int = 3) -> list[SourceNote]:
        """Return top N sources by rank."""
        ranked = self.rank(sources)
        return [r.source for r in ranked[:n]]
