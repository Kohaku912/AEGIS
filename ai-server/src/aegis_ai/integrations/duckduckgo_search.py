"""DuckDuckGo Search — web search integration for AEGIS."""

from __future__ import annotations

import html
import logging
import re
import urllib.parse
import urllib.request
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
    """Web search using DuckDuckGo (ddgs package, legacy package, or HTML fallback)."""

    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout

    def search(self, query: str, max_results: int = 5) -> SearchResponse:
        query = str(query or "").strip()
        if not query:
            return SearchResponse(query=query, success=False, error="query is required")

        for backend in (self._search_ddgs, self._search_legacy_package, self._search_html):
            response = backend(query, max_results)
            if response.success and response.results:
                return response
            if response.success and not response.results:
                # Empty success is still usable; prefer later backends only when prior failed.
                continue
            logger.debug("Search backend %s failed: %s", backend.__name__, response.error)

        # Return last failure or empty success
        html_response = self._search_html(query, max_results)
        if html_response.success:
            return html_response
        return SearchResponse(
            query=query,
            success=False,
            error=html_response.error or "All DuckDuckGo search backends failed",
        )

    def news(self, query: str, max_results: int = 5) -> SearchResponse:
        query = str(query or "").strip()
        if not query:
            return SearchResponse(query=query, success=False, error="query is required")

        response = self._news_ddgs(query, max_results)
        if response.success:
            return response
        # Fall back to text search for news-like queries
        return self.search(f"{query} news", max_results=max_results)

    def _search_ddgs(self, query: str, max_results: int) -> SearchResponse:
        try:
            from ddgs import DDGS
        except ImportError:
            return SearchResponse(query=query, success=False, error="ddgs package not installed")

        response = SearchResponse(query=query)
        try:
            with DDGS(timeout=self._timeout) as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                for r in results:
                    response.results.append(
                        SearchResult(
                            title=str(r.get("title") or ""),
                            url=str(r.get("href") or r.get("link") or ""),
                            snippet=str(r.get("body") or r.get("snippet") or ""),
                        )
                    )
        except Exception as e:
            response.success = False
            response.error = str(e)
            logger.warning("DuckDuckGo ddgs search failed: %s", e)
        return response

    def _news_ddgs(self, query: str, max_results: int) -> SearchResponse:
        try:
            from ddgs import DDGS
        except ImportError:
            return SearchResponse(query=query, success=False, error="ddgs package not installed")

        response = SearchResponse(query=query)
        try:
            with DDGS(timeout=self._timeout) as ddgs:
                results = list(ddgs.news(query, max_results=max_results))
                for r in results:
                    response.results.append(
                        SearchResult(
                            title=str(r.get("title") or ""),
                            url=str(r.get("url") or ""),
                            snippet=str(r.get("body") or ""),
                            source=str(r.get("source") or ""),
                        )
                    )
        except Exception as e:
            response.success = False
            response.error = str(e)
            logger.warning("DuckDuckGo ddgs news failed: %s", e)
        return response

    def _search_legacy_package(self, query: str, max_results: int) -> SearchResponse:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return SearchResponse(
                query=query,
                success=False,
                error="duckduckgo_search package not installed",
            )

        response = SearchResponse(query=query)
        try:
            with DDGS(timeout=self._timeout) as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                for r in results:
                    response.results.append(
                        SearchResult(
                            title=str(r.get("title") or ""),
                            url=str(r.get("href") or r.get("link") or ""),
                            snippet=str(r.get("body") or r.get("snippet") or ""),
                        )
                    )
        except Exception as e:
            response.success = False
            response.error = str(e)
            logger.warning("DuckDuckGo legacy package search failed: %s", e)
        return response

    def _search_html(self, query: str, max_results: int) -> SearchResponse:
        """Dependency-free HTML endpoint fallback."""
        response = SearchResponse(query=query)
        url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; AEGIS/1.0; +https://localhost) "
                        "AppleWebKit/537.36 (KHTML, like Gecko)"
                    )
                },
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            response.success = False
            response.error = f"HTML search failed: {e}"
            logger.warning("DuckDuckGo HTML search failed: %s", e)
            return response

        # Result blocks: <a class="result__a" href="...">title</a> and snippet in result__snippet
        link_pattern = re.compile(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )
        snippet_pattern = re.compile(
            r'class="result__snippet[^"]*"[^>]*>(.*?)</(?:a|td|div)>',
            re.IGNORECASE | re.DOTALL,
        )
        titles_urls = link_pattern.findall(body)
        snippets = snippet_pattern.findall(body)
        for index, (href, title_html) in enumerate(titles_urls[:max_results]):
            title = re.sub(r"<[^>]+>", "", title_html)
            title = html.unescape(re.sub(r"\s+", " ", title)).strip()
            snippet = ""
            if index < len(snippets):
                snippet = re.sub(r"<[^>]+>", "", snippets[index])
                snippet = html.unescape(re.sub(r"\s+", " ", snippet)).strip()
            resolved = self._unwrap_ddg_redirect(html.unescape(href))
            if not title and not resolved:
                continue
            response.results.append(SearchResult(title=title, url=resolved, snippet=snippet))

        if not response.results:
            response.success = False
            response.error = "HTML search returned no parseable results"
        return response

    @staticmethod
    def _unwrap_ddg_redirect(href: str) -> str:
        parsed = urllib.parse.urlparse(href)
        if "duckduckgo.com" in (parsed.netloc or "") and parsed.path.startswith("/l/"):
            qs = urllib.parse.parse_qs(parsed.query)
            uddg = qs.get("uddg") or qs.get("u")
            if uddg:
                return urllib.parse.unquote(uddg[0])
        return href
