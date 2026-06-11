"""Tests for Evaluation Harness — scenarios, runner, metrics, safety, report."""

from __future__ import annotations

import tempfile
from pathlib import Path

from aegis_ai.evaluation.metrics import Metrics, compare_metrics
from aegis_ai.evaluation.report import ReportGenerator
from aegis_ai.evaluation.runner import EvaluationRunner, ScenarioResult
from aegis_ai.evaluation.safety_tests import SAFETY_BENCHMARK
from aegis_ai.evaluation.scenario import (
    ALL_SCENARIOS,
    ExpectedOutcome,
    Scenario,
    ScenarioStep,
    ScenarioType,
)

# ═══════════════════════════════════════════════════════════════
# 1. Scenario Definitions
# ═══════════════════════════════════════════════════════════════


class TestScenarios:
    """Scenario definitions are valid."""

    def test_all_scenarios_not_empty(self):
        """ALL_SCENARIOS is not empty."""
        assert len(ALL_SCENARIOS) >= 5

    def test_safety_benchmark_not_empty(self):
        """SAFETY_BENCHMARK is not empty."""
        assert len(SAFETY_BENCHMARK) >= 3

    def test_scenario_ids_unique(self):
        """Scenario IDs are unique."""
        ids = [s.scenario_id for s in ALL_SCENARIOS]
        assert len(ids) == len(set(ids))

    def test_scenario_has_steps(self):
        """All scenarios have at least one step."""
        for s in ALL_SCENARIOS:
            assert len(s.steps) >= 1


# ═══════════════════════════════════════════════════════════════
# 2. Evaluation Runner
# ═══════════════════════════════════════════════════════════════


class TestEvaluationRunner:
    """Runner executes scenarios correctly."""

    def test_run_scenario(self):
        """Runner executes a simple scenario."""
        scenario = Scenario(
            scenario_id="test_001",
            name="Test Scenario",
            type=ScenarioType.RESEARCH,
            steps=[
                ScenarioStep(
                    step_id="s1",
                    action="collect_sources",
                    expected_outcome=ExpectedOutcome.SUCCESS,
                ),
            ],
        )
        runner = EvaluationRunner()
        result = runner.run_scenario(scenario)
        assert result.passed is True
        assert result.scenario_id == "test_001"

    def test_run_all(self):
        """Runner executes all scenarios."""
        runner = EvaluationRunner()
        results = runner.run_all()
        assert len(results) >= 5
        assert all(isinstance(r, ScenarioResult) for r in results)

    def test_metrics_calculated(self):
        """Metrics are calculated after scenario run."""
        scenario = Scenario(
            scenario_id="test_metrics",
            name="Metrics Test",
            type=ScenarioType.RESEARCH,
            steps=[
                ScenarioStep(step_id="s1", action="collect_sources", expected_outcome=ExpectedOutcome.SUCCESS),
            ],
        )
        runner = EvaluationRunner()
        result = runner.run_scenario(scenario)
        assert result.metrics.task_success == 1.0
        assert result.metrics.safety_violation_count == 0


# ═══════════════════════════════════════════════════════════════
# 3. Safety Benchmark
# ═══════════════════════════════════════════════════════════════


class TestSafetyBenchmark:
    """Safety benchmark scenarios pass."""

    def test_safety_benchmark_runs(self):
        """Safety benchmark runs without errors."""
        runner = EvaluationRunner()
        results = runner.run_all(SAFETY_BENCHMARK)
        assert len(results) >= 3

    def test_safety_scenarios_have_safety_tags(self):
        """Safety scenarios have safety tags."""
        for s in SAFETY_BENCHMARK:
            assert "safety" in s.tags


# ═══════════════════════════════════════════════════════════════
# 4. Metrics
# ═══════════════════════════════════════════════════════════════


class TestMetrics:
    """Metrics tracking works correctly."""

    def test_metrics_defaults(self):
        """Default metrics have zero values."""
        m = Metrics()
        assert m.task_success == 0.0
        assert m.safety_violation_count == 0

    def test_metrics_to_dict(self):
        """Metrics converts to dict."""
        m = Metrics(task_success=1.0, safety_violation_count=0)
        d = m.to_dict()
        assert d["task_success"] == 1.0

    def test_compare_no_regression(self):
        """No regression when metrics are same or better."""
        baseline = Metrics(task_success=0.8)
        current = Metrics(task_success=0.8)
        result = compare_metrics(baseline, current)
        assert result["passed"] is True

    def test_compare_regression(self):
        """Regression detected when task_success drops."""
        baseline = Metrics(task_success=0.9)
        current = Metrics(task_success=0.5)
        result = compare_metrics(baseline, current)
        assert result["passed"] is False
        assert len(result["regressions"]) >= 1

    def test_compare_safety_regression(self):
        """Regression detected when safety violations increase."""
        baseline = Metrics(safety_violation_count=0)
        current = Metrics(safety_violation_count=2)
        result = compare_metrics(baseline, current)
        assert result["passed"] is False


# ═══════════════════════════════════════════════════════════════
# 5. Report Generator
# ═══════════════════════════════════════════════════════════════


class TestReportGenerator:
    """Report generator creates valid reports."""

    def test_generate_markdown(self):
        """Markdown report is generated."""
        runner = EvaluationRunner()
        results = runner.run_all(SAFETY_BENCHMARK[:2])
        gen = ReportGenerator()
        md = gen.generate_markdown(results)
        assert "AEGIS Evaluation Report" in md
        assert "PASS" in md or "FAIL" in md

    def test_generate_json(self):
        """JSON report is generated."""
        runner = EvaluationRunner()
        results = runner.run_all(SAFETY_BENCHMARK[:2])
        gen = ReportGenerator()
        report = gen.generate_json(results)
        assert "total_scenarios" in report
        assert "scenarios" in report

    def test_save_reports(self):
        """Reports are saved to disk."""
        runner = EvaluationRunner()
        results = runner.run_all(SAFETY_BENCHMARK[:2])
        gen = ReportGenerator()
        with tempfile.TemporaryDirectory() as tmpdir:
            gen.save(results, tmpdir)
            assert Path(tmpdir, "latest.md").exists()
            assert Path(tmpdir, "latest.json").exists()


# ═══════════════════════════════════════════════════════════════
# 6. Full E2E
# ═══════════════════════════════════════════════════════════════


class TestFullEvaluation:
    """Full evaluation harness E2E."""

    def test_full_evaluation_with_report(self):
        """Full evaluation runs and generates report."""
        runner = EvaluationRunner()
        results = runner.run_all(ALL_SCENARIOS)
        gen = ReportGenerator()

        assert len(results) >= 5
        assert all(isinstance(r, ScenarioResult) for r in results)

        md = gen.generate_markdown(results)
        assert "AEGIS Evaluation Report" in md

        report = gen.generate_json(results)
        assert report["total_scenarios"] == len(results)

    def test_safety_violations_detected(self):
        """Safety violations are properly detected."""
        m = Metrics(safety_violation_count=3, approval_bypass_count=1)
        assert m.safety_violation_count == 3
        assert m.approval_bypass_count == 1
