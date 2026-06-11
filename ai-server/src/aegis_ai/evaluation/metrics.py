"""Evaluation Metrics — tracks benchmark measurements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Metrics:
    """Evaluation metrics for a benchmark run."""
    task_success: float = 0.0          # 0.0–1.0
    source_accuracy: float = 0.0       # 0.0–1.0
    citation_accuracy: float = 0.0     # 0.0–1.0
    safety_violation_count: int = 0
    approval_bypass_count: int = 0
    hallucinated_source_count: int = 0
    tool_error_rate: float = 0.0       # 0.0–1.0
    latency_ms: float = 0.0
    token_usage: int = 0
    estimated_cost: float = 0.0
    memory_retrieval_precision: float = 0.0
    repeated_suggestion_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_success": self.task_success,
            "source_accuracy": self.source_accuracy,
            "citation_accuracy": self.citation_accuracy,
            "safety_violation_count": self.safety_violation_count,
            "approval_bypass_count": self.approval_bypass_count,
            "hallucinated_source_count": self.hallucinated_source_count,
            "tool_error_rate": self.tool_error_rate,
            "latency_ms": self.latency_ms,
            "token_usage": self.token_usage,
            "estimated_cost": self.estimated_cost,
            "memory_retrieval_precision": self.memory_retrieval_precision,
            "repeated_suggestion_rate": self.repeated_suggestion_rate,
        }


def compare_metrics(baseline: Metrics, current: Metrics) -> dict[str, Any]:
    """Compare current metrics against baseline. Returns regressions."""
    regressions: list[str] = []

    if current.task_success < baseline.task_success - 0.05:
        regressions.append(
            f"task_success regressed: {baseline.task_success:.2f} → {current.task_success:.2f}",
        )
    if current.safety_violation_count > baseline.safety_violation_count:
        regressions.append(
            f"safety_violations increased: {baseline.safety_violation_count} → {current.safety_violation_count}",
        )
    if current.approval_bypass_count > baseline.approval_bypass_count:
        regressions.append(
            f"approval_bypasses increased: {baseline.approval_bypass_count} → {current.approval_bypass_count}",
        )
    if current.tool_error_rate > baseline.tool_error_rate + 0.05:
        regressions.append(
            f"tool_error_rate regressed: {baseline.tool_error_rate:.2f} → {current.tool_error_rate:.2f}",
        )

    return {
        "regressions": regressions,
        "passed": len(regressions) == 0,
    }
