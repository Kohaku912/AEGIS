"""Evaluation Harness — benchmark and safety testing for AEGIS.

Provides:
- Scenario: Evaluation scenario definitions
- EvaluationRunner: Runs benchmark scenarios
- Metrics: Benchmark measurements
- ReportGenerator: Generates reports
- SAFETY_BENCHMARK: Safety-specific scenarios
"""

from aegis_ai.evaluation.metrics import Metrics, compare_metrics  # noqa: F401
from aegis_ai.evaluation.report import ReportGenerator  # noqa: F401
from aegis_ai.evaluation.runner import EvaluationRunner, ScenarioResult  # noqa: F401
from aegis_ai.evaluation.safety_tests import SAFETY_BENCHMARK  # noqa: F401
from aegis_ai.evaluation.scenario import (  # noqa: F401
    ALL_SCENARIOS,
    ExpectedOutcome,
    Scenario,
    ScenarioStep,
    ScenarioType,
)
