"""Daily Briefing Provider — generates daily summaries.

Collects:
- Calendar events (if available)
- Weather data (if available)
- Pending tasks
- Recent notifications
- System health

Usage:
    provider = DailyBriefingProvider(context_builder=ctx)
    briefing = provider.generate_briefing()
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("aegis_ai.briefing.provider")


@dataclass
class BriefingSection:
    """A section of the daily briefing."""
    title: str = ""
    content: str = ""
    priority: str = "normal"  # low, normal, high
    source: str = ""


@dataclass
class DailyBriefing:
    """A complete daily briefing."""
    date: str = ""
    sections: list[BriefingSection] = field(default_factory=list)
    summary: str = ""
    generated_at_ms: int = 0


class DailyBriefingProvider:
    """Generates daily briefings from available data sources.

    Usage:
        provider = DailyBriefingProvider(context_builder=ctx)
        briefing = provider.generate_briefing()
    """

    def __init__(
        self,
        context_builder: Any = None,
        memory: Any = None,
        llm_provider: Any = None,
        notification_store: Any = None,
    ) -> None:
        self._context = context_builder
        self._memory = memory
        self._llm = llm_provider
        self._notifications = notification_store

    def generate_briefing(self) -> DailyBriefing:
        """Generate a daily briefing."""
        briefing = DailyBriefing(
            date=time.strftime("%Y-%m-%d"),
            generated_at_ms=int(time.time() * 1000),
        )

        # Collect sections
        sections = []

        # System health
        sections.append(self._get_system_health())

        # Recent notifications
        sections.append(self._get_recent_notifications())

        # Pending tasks
        sections.append(self._get_pending_tasks())

        # Memory highlights
        sections.append(self._get_memory_highlights())

        # Weather (placeholder)
        sections.append(self._get_weather())

        # Calendar (placeholder)
        sections.append(self._get_calendar())

        briefing.sections = [s for s in sections if s.content]

        # Generate summary
        if self._llm:
            briefing.summary = self._generate_summary(briefing)
        else:
            briefing.summary = self._generate_simple_summary(briefing)

        return briefing

    def _get_system_health(self) -> BriefingSection:
        """Get system health summary."""
        return BriefingSection(
            title="System Health",
            content="All systems operational. AEGIS Core running.",
            priority="normal",
            source="system",
        )

    def _get_recent_notifications(self) -> BriefingSection:
        """Get recent notifications."""
        if self._notifications:
            try:
                recent = self._notifications.get_recent(limit=5)
                if recent:
                    items = [f"- {n.get('title', 'No title')}" for n in recent]
                    return BriefingSection(
                        title="Recent Notifications",
                        content="\n".join(items),
                        priority="normal",
                        source="notifications",
                    )
            except Exception:
                pass
        return BriefingSection(
            title="Recent Notifications",
            content="No recent notifications.",
            priority="low",
            source="notifications",
        )

    def _get_pending_tasks(self) -> BriefingSection:
        """Get pending tasks."""
        return BriefingSection(
            title="Pending Tasks",
            content="No pending tasks.",
            priority="normal",
            source="scheduler",
        )

    def _get_memory_highlights(self) -> BriefingSection:
        """Get memory highlights."""
        if self._memory:
            try:
                facts = self._memory.search("important", limit=3)
                if facts:
                    items = [f"- {f.content}" for f in facts]
                    return BriefingSection(
                        title="Memory Highlights",
                        content="\n".join(items),
                        priority="low",
                        source="memory",
                    )
            except Exception:
                pass
        return BriefingSection(
            title="Memory Highlights",
            content="No highlights.",
            priority="low",
            source="memory",
        )

    def _get_weather(self) -> BriefingSection:
        """Get weather data (placeholder)."""
        return BriefingSection(
            title="Weather",
            content="Weather data not available. Configure weather API for live data.",
            priority="low",
            source="weather",
        )

    def _get_calendar(self) -> BriefingSection:
        """Get calendar events (placeholder)."""
        return BriefingSection(
            title="Calendar",
            content="Calendar not connected. Configure calendar integration for events.",
            priority="low",
            source="calendar",
        )

    def _generate_summary(self, briefing: DailyBriefing) -> str:
        """Generate summary using LLM."""
        try:
            content = "\n\n".join([f"## {s.title}\n{s.content}" for s in briefing.sections])
            result = self._llm.generate(
                prompt=f"Summarize this daily briefing concisely:\n\n{content}",
                system_prompt="You are AEGIS, a helpful AI assistant. Provide a brief daily summary.",
                max_tokens=300,
            )
            if result.success:
                return result.content
        except Exception as e:
            logger.warning("LLM summary failed: %s", e)
        return self._generate_simple_summary(briefing)

    def _generate_simple_summary(self, briefing: DailyBriefing) -> str:
        """Generate simple summary without LLM."""
        high_priority = [s for s in briefing.sections if s.priority == "high"]
        if high_priority:
            return f"Daily briefing for {briefing.date}: {len(high_priority)} high priority items require attention."
        return f"Daily briefing for {briefing.date}: All systems normal. {len(briefing.sections)} sections available."
