"""Research Agent — autonomous deep-dive information gathering.

Integrates SourceCollector, TextExtractor, SourceRanker, CitationManager,
and ReportBuilder to research a topic from URL sources.

Architecture reference: docs/architecture.md §5.5
All browser operations go through ToolBroker → PolicyEngine.
"""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.research.citation import CitationManager
from aegis_ai.research.collector import SourceCollector
from aegis_ai.research.extractor import TextExtractor
from aegis_ai.research.ranker import SourceRanker
from aegis_ai.research.report import ReportBuilder
from aegis_ai.research.source import SourceNote

logger = logging.getLogger("aegis_ai.agents.research")


class ResearchAgent:
    """Gathers information from multiple sources via Browser Server.

    Does NOT execute browser operations directly — uses ToolBroker,
    which enforces PolicyEngine checks.

    Usage:
        agent = ResearchAgent(tool_broker=broker)
        report = agent.research_topic("Python 3.12 features", urls=[
            "https://docs.python.org/3/whatsnew/3.12.html",
            "https://realpython.com/python312-new-features/",
        ])
        print(report.summary)
    """

    def __init__(
        self,
        tool_broker: Any = None,
        collector: SourceCollector | None = None,
        extractor: TextExtractor | None = None,
        ranker: SourceRanker | None = None,
        citation: CitationManager | None = None,
        report_builder: ReportBuilder | None = None,
    ) -> None:
        self._tool_broker = tool_broker
        self._collector = collector or SourceCollector(tool_broker)
        self._extractor = extractor or TextExtractor()
        self._ranker = ranker or SourceRanker()
        self._citation = citation or CitationManager()
        self._report_builder = report_builder or ReportBuilder(self._ranker, self._citation)
        self._last_sources: list[SourceNote] = []
        self._last_report: Any = None

    # ── Public API ──────────────────────────────────────────

    def research_topic(self, topic: str, urls: list[str] | None = None) -> Any:
        """Research a topic by collecting sources and building a report.

        Args:
            topic: The research topic.
            urls: Optional list of URLs to research. If None, returns empty report.

        Returns:
            ResearchReport with summary, findings, and sources.
        """
        urls = urls or []

        # 1. Collect sources
        sources = self.collect_sources(urls)

        # 2. Build report
        report = self._report_builder.build(topic, sources)
        self._last_sources = sources
        self._last_report = report

        return report

    def collect_sources(self, urls: list[str]) -> list[SourceNote]:
        """Collect content from a list of URLs.

        Each URL is opened via Browser Server, text is extracted,
        and a SourceNote is created with metadata.
        """
        sources: list[SourceNote] = []
        for i, url in enumerate(urls):
            source_id = f"src_{i+1}"
            note = self._collector.collect(url, source_id)
            sources.append(note)
        self._last_sources = sources
        return sources

    def collect_local(self, html_fixtures: list[tuple[str, str, str]]) -> list[SourceNote]:
        """Collect from local HTML fixtures (for testing).

        Args:
            html_fixtures: List of (url, title, html_content) tuples.
        """
        sources: list[SourceNote] = []
        for i, (url, title, html) in enumerate(html_fixtures):
            note = self._collector.collect_local(url, html, title)
            note.source_id = f"src_{i+1}"
            sources.append(note)
        self._last_sources = sources
        return sources

    def get_last_sources(self) -> list[SourceNote]:
        return self._last_sources

    def get_last_report(self) -> Any:
        return self._last_report
