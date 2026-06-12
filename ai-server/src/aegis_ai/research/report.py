"""Research Report — compiles source notes into a structured report."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from aegis_ai.research.citation import CitationManager
from aegis_ai.research.ranker import SourceRanker
from aegis_ai.research.source import SourceNote


@dataclass
class ResearchReport:
    """A compiled research report with summary, findings, and sources."""

    report_id: str = ""
    topic: str = ""
    summary: str = ""

    # Findings
    key_findings: list[str] = field(default_factory=list)
    conflicting_info: list[str] = field(default_factory=list)  # Points of disagreement
    uncertain_points: list[str] = field(default_factory=list)   # Things that couldn't be verified

    # Sources
    sources: list[SourceNote] = field(default_factory=list)
    reference_list: str = ""

    # Metadata
    created_at_ms: int = 0
    sources_collected: int = 0
    sources_failed: int = 0


class ReportBuilder:
    """Builds a ResearchReport from collected SourceNotes."""

    def __init__(self, ranker: SourceRanker | None = None, citation: CitationManager | None = None) -> None:
        self._ranker = ranker or SourceRanker()
        self._citation = citation or CitationManager()

    def build(self, topic: str, sources: list[SourceNote]) -> ResearchReport:
        """Build a report from collected sources."""
        import uuid

        report = ResearchReport(
            report_id=f"report_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}",
            topic=topic,
            created_at_ms=int(time.time() * 1000),
        )

        # Categorize sources
        collected = [s for s in sources if s.status == "collected"]
        failed = [s for s in sources if s.status == "failed"]
        report.sources_collected = len(collected)
        report.sources_failed = len(failed)

        if not collected:
            report.summary = f"No sources could be collected for topic: {topic}"
            return report

        # Assign citations
        for source in collected:
            source.citation_label = self._citation.assign_label(source.source_id)

        # Rank sources
        ranked = self._ranker.rank(collected)
        report.sources = [r.source for r in ranked]

        # Extract key findings from all sources
        all_points: list[str] = []
        for source in collected:
            all_points.extend(source.key_points)
        report.key_findings = all_points[:10]

        # Generate summary
        report.summary = self._generate_summary(topic, collected)

        # Detect conflicting info (simple heuristic)
        report.conflicting_info = self._detect_conflicts(collected)
        report.uncertain_points = [
            f"Source '{s.title}' has reliability '{s.reliability_hint}'"
            for s in collected
            if s.reliability_hint in ("low", "unverified")
        ]

        # Build reference list
        refs = [(s.source_id, s.title or s.url, s.url) for s in collected]
        report.reference_list = self._citation.format_reference_list(refs)

        return report

    def _generate_summary(self, topic: str, sources: list[SourceNote]) -> str:
        """Generate a summary from collected sources."""
        if not sources:
            return f"No sources available for topic: {topic}"

        parts = [f"Research summary for: {topic}", f"Sources consulted: {len(sources)}"]

        # Collect reliability info
        high = sum(1 for s in sources if s.reliability_hint == "high")
        if high > 0:
            parts.append(f"High-reliability sources: {high}")

        # Include top key points
        key_points = []
        for s in sources[:3]:
            key_points.extend(s.key_points[:2])
        if key_points:
            parts.append("Key points:")
            parts.extend(f"  • {p}" for p in key_points[:5])

        return "\n".join(parts)

    def _detect_conflicts(self, sources: list[SourceNote]) -> list[str]:
        """Detect potentially conflicting information across sources (simple heuristic)."""
        conflicts: list[str] = []
        # Compare reliability hints — if we have both "high" and "low" on same topic, flag it
        reliabilities = {s.reliability_hint for s in sources}
        if "high" in reliabilities and ("low" in reliabilities or "unverified" in reliabilities):
            conflicts.append("Sources have mixed reliability — some claims may be unverified.")
        return conflicts
