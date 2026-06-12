"""Source Collector — collects sources from URLs via Browser Server.

Uses ToolBroker to invoke browser capabilities for text extraction.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from aegis_ai.research.source import SourceNote

logger = logging.getLogger("aegis_ai.research.collector")


class SourceCollector:
    """Collects source content from URLs using Browser Server capabilities.

    Does NOT execute browser operations directly — goes through ToolBroker,
    which enforces PolicyEngine checks.
    """

    def __init__(self, tool_broker: Any = None) -> None:
        self._tool_broker = tool_broker

    def collect(self, url: str, source_id: str = "") -> SourceNote:
        """Collect content from a single URL.

        Returns a SourceNote with status "collected" or "failed".
        """
        note = SourceNote(
            source_id=source_id or f"src_{int(time.time() * 1000)}",
            url=url,
            accessed_at_ms=int(time.time() * 1000),
        )

        if self._tool_broker is None:
            return self._collect_local(url, note)

        # 1. Open the page
        open_result = self._tool_broker.invoke_tool(
            "browser.open_page", {"url": url, "wait_until": "networkidle"}
        )
        if not open_result.success:
            note.mark_failed(f"Failed to open page: {open_result.error}")
            return note

        note.title = open_result.output.get("title", "Untitled")

        # 2. Extract text
        extract_result = self._tool_broker.invoke_tool(
            "browser.extract_page_text", {"max_length": 10000}
        )
        if extract_result.success:
            text = extract_result.output.get("text", "")
            note.extracted_text_summary = text[:500]
            note.full_text_length = len(text)
            note.key_points = self._extract_key_points(text)
        else:
            note.extracted_text_summary = f"[Extraction failed: {extract_result.error}]"

        note.reliability_hint = self._assess_reliability(url)
        note.domain_category = self._categorize_domain(url)
        note.mark_collected()
        return note

    def collect_local(self, url: str, html_content: str, title: str = "Local") -> SourceNote:
        """Collect from local HTML content (for testing)."""
        note = SourceNote(
            source_id=f"local_{int(time.time() * 1000)}",
            url=url,
            title=title,
            accessed_at_ms=int(time.time() * 1000),
        )
        # Extract text from HTML
        text = self._strip_html(html_content)
        note.extracted_text_summary = text[:500]
        note.full_text_length = len(text)
        note.key_points = self._extract_key_points(text)
        note.reliability_hint = "unverified"
        note.domain_category = "local"
        note.mark_collected()
        return note

    def _collect_local(self, url: str, note: SourceNote) -> SourceNote:
        """Mock collection for testing when no ToolBroker is available."""
        note.title = f"Mock page: {url}"
        note.extracted_text_summary = f"Mock extracted text for {url}. This is a simulated result."
        note.full_text_length = len(note.extracted_text_summary)
        note.key_points = ["Mock point 1", "Mock point 2"]
        note.reliability_hint = "unverified"
        note.domain_category = "mock"
        note.mark_collected()
        return note

    # ── Helpers ──────────────────────────────────────────────

    def _extract_key_points(self, text: str) -> list[str]:
        """Extract key points from text (simple heuristic)."""
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 30]
        return lines[:5]

    def _assess_reliability(self, url: str) -> str:
        """Simple reliability assessment based on domain."""
        url_lower = url.lower()
        if any(d in url_lower for d in [".gov", ".edu", "docs.python.org", "github.com"]):
            return "high"
        if any(d in url_lower for d in ["wikipedia.org", "stackoverflow.com", "medium.com"]):
            return "medium"
        if any(d in url_lower for d in ["reddit.com", "twitter.com", "x.com"]):
            return "low"
        return "unknown"

    def _categorize_domain(self, url: str) -> str:
        """Categorize domain type."""
        url_lower = url.lower()
        if "docs." in url_lower or "documentation" in url_lower or "readthedocs" in url_lower:
            return "documentation"
        if "github.com" in url_lower or "gitlab.com" in url_lower:
            return "official"
        if "news." in url_lower or "blog." in url_lower:
            return "blog"
        if "stackoverflow" in url_lower or "forum" in url_lower:
            return "forum"
        return "unknown"

    def _strip_html(self, html: str) -> str:
        """Simple HTML tag stripper."""
        import re
        # Remove script and style
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        # Remove tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text
