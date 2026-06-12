"""Tests for Daily Briefing Provider."""

from __future__ import annotations

import pytest

from aegis_ai.briefing.provider import BriefingSection, DailyBriefing, DailyBriefingProvider


class TestDailyBriefingProvider:
    """Daily briefing provider tests."""

    def test_provider_creation(self):
        """Provider can be created."""
        provider = DailyBriefingProvider()
        assert provider is not None

    def test_generate_briefing(self):
        """Generates a briefing."""
        provider = DailyBriefingProvider()
        briefing = provider.generate_briefing()
        assert briefing is not None
        assert briefing.date
        assert len(briefing.sections) > 0

    def test_briefing_has_system_health(self):
        """Briefing includes system health."""
        provider = DailyBriefingProvider()
        briefing = provider.generate_briefing()
        health_sections = [s for s in briefing.sections if s.title == "System Health"]
        assert len(health_sections) == 1

    def test_briefing_has_summary(self):
        """Briefing has a summary."""
        provider = DailyBriefingProvider()
        briefing = provider.generate_briefing()
        assert briefing.summary

    def test_briefing_with_mock_llm(self):
        """Briefing uses LLM when available."""
        from aegis_ai.llm.providers.mock import MockLLMProvider

        provider = DailyBriefingProvider(llm_provider=MockLLMProvider())
        briefing = provider.generate_briefing()
        assert briefing.summary

    def test_briefing_section_creation(self):
        """BriefingSection can be created."""
        section = BriefingSection(title="Test", content="Content", priority="normal")
        assert section.title == "Test"

    def test_briefing_creation(self):
        """DailyBriefing can be created."""
        briefing = DailyBriefing(date="2026-01-01", sections=[], summary="Test")
        assert briefing.date == "2026-01-01"
