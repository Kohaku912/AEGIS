"""Citation Manager — assigns citation labels to sources."""

from __future__ import annotations


class CitationManager:
    """Manages citation labels for research sources.

    Assigns sequential citation labels: [1], [2], [3], etc.
    Provides formatting for inline citations and reference lists.
    """

    def __init__(self) -> None:
        self._counter: int = 0
        self._labels: dict[str, str] = {}  # source_id → label

    def assign_label(self, source_id: str) -> str:
        """Assign a citation label to a source."""
        self._counter += 1
        label = f"[{self._counter}]"
        self._labels[source_id] = label
        return label

    def get_label(self, source_id: str) -> str:
        """Get an existing citation label."""
        return self._labels.get(source_id, "")

    def format_inline(self, source_id: str, page: str = "") -> str:
        """Format an inline citation."""
        label = self._labels.get(source_id, "[?]")
        return f"{label}(p.{page})" if page else label

    def format_reference(self, source_id: str, title: str, url: str) -> str:
        """Format a reference list entry."""
        label = self._labels.get(source_id, "[?]")
        return f"{label} {title} — {url}"

    def format_reference_list(self, sources: list[tuple[str, str, str]]) -> str:
        """Format a full reference list.

        Args:
            sources: List of (source_id, title, url) tuples.
        """
        lines = []
        for source_id, title, url in sources:
            lines.append(self.format_reference(source_id, title, url))
        return "\n".join(lines)
