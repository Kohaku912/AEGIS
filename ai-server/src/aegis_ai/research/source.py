"""Source Note — metadata about a researched source."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class SourceNote:
    """A single researched source with extracted metadata and content."""

    source_id: str = ""
    url: str = ""
    title: str = ""
    accessed_at_ms: int = 0

    # Extracted content
    extracted_text_summary: str = ""     # First ~500 chars of extracted text
    full_text_length: int = 0
    key_points: list[str] = field(default_factory=list)

    # Reliability assessment
    reliability_hint: str = "unknown"    # "high", "medium", "low", "unverified", "unknown"
    domain_category: str = "unknown"     # "official", "documentation", "news", "blog", "forum"

    # Citation
    citation_label: str = ""             # e.g. "[1]", "[2]"

    # Metadata
    status: str = "pending"              # "pending", "collected", "failed"
    error_message: str = ""
    collected_at_ms: int = 0

    def mark_collected(self) -> None:
        self.status = "collected"
        self.collected_at_ms = int(time.time() * 1000)

    def mark_failed(self, error: str) -> None:
        self.status = "failed"
        self.error_message = error
