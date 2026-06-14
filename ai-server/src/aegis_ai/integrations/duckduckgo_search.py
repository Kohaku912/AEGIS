"""DuckDuckGo Search — web search integration for AEGIS."""

from __future__ import annotations

import logging
import re
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger("aegis_ai.integrations.duckduckgo")


@dataclass
class SearchResult:
    """A single search result."""
    title: str = ""
    url: str = ""
    snippet: str = ""
    source: str = ""


@dataclass
class SearchResponse:
    """Response from a search query."""
    query: str = ""
    results: list[SearchResult] = field(default_factory=list)
    success: bool = True
    error: str = ""

    def to_context_string(self, max_chars: int = 1000) -> str:
        if not self.results:
            return f"No results for: {self.query}"
        lines = [f"Search results for '{self.query}':"]
        for r in self.results[:5]:
            lines.append(f"- {r.title}: {r.snippet[:100]}")
            lines.append(f"  {r.url}")
        return "\n".join(lines)[:max_chars]


class DuckDuckGoSearch:
    """Web search using DuckDuckGo."""

    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout

    def search(self, query: str, max_results: int = 5) -> SearchResponse:
        try:
            from ddgs import DDGS
        except ImportError:
            return SearchResponse(
                query=query,
                success=False,
                error="ddgs package not installed. Run: pip install ddgs",
            )

        response = SearchResponse(query=query)
        try:
            with DDGS(timeout=self._timeout) as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                for r in results:
                    response.results.append(SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                    ))
        except Exception as e:
            response.success = False
            response.error = str(e)
            logger.warning("DuckDuckGo search failed: %s", e)

        return response

    def news(self, query: str, max_results: int = 5) -> SearchResponse:
        try:
            from ddgs import DDGS
        except ImportError:
            return SearchResponse(
                query=query,
                success=False,
                error="ddgs package not installed.",
            )

        response = SearchResponse(query=query)
        try:
            with DDGS(timeout=self._timeout) as ddgs:
                results = list(ddgs.news(query, max_results=max_results))
                for r in results:
                    response.results.append(SearchResult(
                        title=r.get("title", ""),
                        url=r.get("url", ""),
                        snippet=r.get("body", ""),
                        source=r.get("source", ""),
                    ))
        except Exception as e:
            response.success = False
            response.error = str(e)
            logger.warning("DuckDuckGo news search failed: %s", e)

        return response
