"""Research Agent — autonomous deep-dive information gathering.

STATUS: Skeleton — not yet integrated with Browser Server or LLM.
"""

from __future__ import annotations


class ResearchAgent:
    """Gathers information from multiple sources.

    Architecture reference: docs/architecture.md §5.5
    Currently a skeleton.
    """

    def __init__(self) -> None:
        pass

    def research(self, topic: str) -> dict:
        """Research a topic. Returns structured findings.

        TODO: Integrate with ToolBroker → Browser Server capabilities.
        """
        return {
            "topic": topic,
            "status": "skeleton — not yet implemented",
            "sources": [],
            "summary": "",
        }
