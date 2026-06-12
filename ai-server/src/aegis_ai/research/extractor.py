"""Text Extractor — processes extracted text into structured key points."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ExtractedContent:
    """Structured content extracted from a page."""
    raw_text: str = ""
    cleaned_text: str = ""
    key_points: list[str] = field(default_factory=list)
    word_count: int = 0
    entities: dict[str, list[str]] = field(default_factory=dict)  # entity_type → values


class TextExtractor:
    """Processes raw text into structured, clean content."""

    def extract(self, raw_text: str) -> ExtractedContent:
        """Extract structured content from raw page text."""
        cleaned = self._clean_text(raw_text)
        return ExtractedContent(
            raw_text=raw_text,
            cleaned_text=cleaned,
            key_points=self._identify_key_points(cleaned),
            word_count=len(cleaned.split()),
            entities=self._extract_entities(cleaned),
        )

    def _clean_text(self, text: str) -> str:
        """Clean extracted text: normalize whitespace, remove boilerplate."""
        # Remove excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove common boilerplate patterns
        text = re.sub(r"Cookie[ -]?(Consent|Notice|Policy).*?(?=\n\n|\Z)", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"Accept (all )?cookies.*?(?=\n\n|\Z)", "", text, flags=re.DOTALL | re.IGNORECASE)
        return text.strip()

    def _identify_key_points(self, text: str) -> list[str]:
        """Identify key points from cleaned text."""
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 40]
        # Score lines by length and keyword presence
        scored = []
        for line in lines:
            score = min(len(line) / 200, 1.0)
            if any(kw in line.lower() for kw in ["important", "key", "critical", "essential", "note:", "warning"]):
                score += 0.5
            scored.append((score, line))
        scored.sort(reverse=True)
        return [line for _, line in scored[:5]]

    def _extract_entities(self, text: str) -> dict[str, list[str]]:
        """Extract simple entities (emails, URLs, dates)."""
        entities: dict[str, list[str]] = {}
        # Emails
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        if emails:
            entities["emails"] = emails[:5]
        # URLs
        urls = re.findall(r"https?://[^\s]+", text)
        if urls:
            entities["urls"] = urls[:10]
        # Dates (YYYY-MM-DD)
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)
        if dates:
            entities["dates"] = dates[:10]
        return entities
