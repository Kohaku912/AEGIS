"""Evaluation Report — generates benchmark reports."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from aegis_ai.evaluation.runner import ScenarioResult


class ReportGenerator:
    """Generates evaluation reports in Markdown and JSON formats.

    Usage:
        gen = ReportGenerator()
        md = gen.generate_markdown(results)
        gen.save(results, "evaluation/reports/latest")
    """

    def generate_markdown(self, results: list[ScenarioResult]) -> str:
        """Generate a Markdown report."""
        lines = [
            "# AEGIS Evaluation Report",
            "",
            f"> Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
            f"- Total scenarios: {len(results)}",
            f"- Passed: {sum(1 for r in results if r.passed)}",
            f"- Failed: {sum(1 for r in results if not r.passed)}",
            "",
            "## Scenarios",
            "",
            "| Scenario | Type | Result | Duration |",
            "|----------|------|--------|----------|",
        ]

        for r in results:
            status = "✅ PASS" if r.passed else "❌ FAIL"
            lines.append(f"| {r.name} | — | {status} | {r.duration_ms:.1f}ms |")

        lines.extend(["", "## Safety Summary", ""])

        safety_results = [r for r in results if "safety" in r.scenario_id]
        if safety_results:
            safety_passed = sum(1 for r in safety_results if r.passed)
            lines.append(f"- Safety scenarios: {len(safety_results)}")
            lines.append(f"- Passed: {safety_passed}")
            lines.append(f"- Failed: {len(safety_results) - safety_passed}")

            violations = sum(r.metrics.safety_violation_count for r in results)
            bypasses = sum(r.metrics.approval_bypass_count for r in results)
            lines.append(f"- Safety violations: {violations}")
            lines.append(f"- Approval bypasses: {bypasses}")

        lines.extend(["", "## Metrics", ""])

        for r in results:
            m = r.metrics
            lines.append(f"### {r.name}")
            lines.append(f"- Task success: {m.task_success:.0%}")
            lines.append(f"- Safety violations: {m.safety_violation_count}")
            lines.append(f"- Approval bypasses: {m.approval_bypass_count}")
            lines.append(f"- Latency: {m.latency_ms:.1f}ms")
            lines.append("")

        return "\n".join(lines)

    def generate_json(self, results: list[ScenarioResult]) -> dict[str, Any]:
        """Generate a JSON report."""
        return {
            "generated_at": int(time.time() * 1000),
            "total_scenarios": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "scenarios": [
                {
                    "id": r.scenario_id,
                    "name": r.name,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms,
                    "metrics": r.metrics.to_dict(),
                    "steps": [
                        {
                            "step_id": sr.step_id,
                            "passed": sr.passed,
                            "actual": sr.actual_outcome,
                            "expected": sr.expected_outcome,
                        }
                        for sr in r.step_results
                    ],
                }
                for r in results
            ],
            "safety_summary": {
                "violations": sum(r.metrics.safety_violation_count for r in results),
                "bypasses": sum(r.metrics.approval_bypass_count for r in results),
            },
        }

    def save(self, results: list[ScenarioResult], output_dir: str = "evaluation/reports") -> None:
        """Save reports to disk."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save Markdown
        md = self.generate_markdown(results)
        (output_path / "latest.md").write_text(md, encoding="utf-8")

        # Save JSON
        report_json = self.generate_json(results)
        (output_path / "latest.json").write_text(
            json.dumps(report_json, indent=2, ensure_ascii=False), encoding="utf-8",
        )
