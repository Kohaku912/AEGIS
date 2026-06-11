"""Tests for Cost Tracker — usage tracking and budget enforcement."""

from __future__ import annotations

import os
import tempfile

from aegis_ai.llm.cost_tracker import CostTracker


def _make_tracker(daily: float = 10.0, monthly: float = 100.0) -> CostTracker:
    """Create a CostTracker with a unique temp file."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    # Remove the file so we start fresh
    os.unlink(path)
    return CostTracker(daily_budget=daily, monthly_budget=monthly, path=path)


class TestCostTracker:
    """Cost tracker manages LLM usage and budgets."""

    def test_can_afford_within_budget(self):
        """can_afford returns True when within budget."""
        tracker = _make_tracker()
        assert tracker.can_afford(100) is True

    def test_record_usage(self):
        """record_usage records usage correctly."""
        tracker = _make_tracker()
        tracker.record_usage("mock", "mock-model", 100, 0.001)
        summary = tracker.get_usage_summary()
        assert summary["total_requests"] == 1

    def test_daily_cost(self):
        """Daily cost is calculated correctly."""
        tracker = _make_tracker()
        tracker.record_usage("mock", "mock-model", 100, 1.0)
        tracker.record_usage("mock", "mock-model", 100, 2.0)
        assert tracker.get_daily_cost() == 3.0

    def test_budget_exceeded(self):
        """can_afford returns False when budget exceeded."""
        tracker = _make_tracker(daily=1.0)
        tracker.record_usage("mock", "mock-model", 100000, 2.0)
        assert tracker.can_afford(100) is False

    def test_monthly_budget(self):
        """Monthly budget is tracked."""
        tracker = _make_tracker(daily=100.0, monthly=5.0)
        tracker.record_usage("mock", "mock-model", 100000, 6.0)
        assert tracker.can_afford(100) is False

    def test_usage_summary(self):
        """Usage summary includes all fields."""
        tracker = _make_tracker()
        tracker.record_usage("mock", "mock-model", 100, 0.5)
        summary = tracker.get_usage_summary()
        assert "daily_cost" in summary
        assert "monthly_cost" in summary
        assert "daily_budget" in summary
        assert "monthly_budget" in summary
        assert "daily_remaining" in summary
        assert "monthly_remaining" in summary
        assert "total_requests" in summary

    def test_zero_cost_mock(self):
        """Mock provider has zero cost."""
        tracker = _make_tracker()
        tracker.record_usage("mock", "mock-model", 100, 0.0)
        assert tracker.get_daily_cost() == 0.0
        assert tracker.can_afford(100) is True
