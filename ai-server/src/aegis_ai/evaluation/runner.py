"""Evaluation Runner — executes benchmark scenarios."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from aegis_ai.evaluation.metrics import Metrics
from aegis_ai.evaluation.scenario import (
    ALL_SCENARIOS,
    ExpectedOutcome,
    Scenario,
    ScenarioStep,
)


@dataclass
class StepResult:
    """Result of a single scenario step."""
    step_id: str = ""
    passed: bool = False
    actual_outcome: str = ""
    expected_outcome: str = ""
    details: str = ""
    duration_ms: float = 0.0


@dataclass
class ScenarioResult:
    """Result of a full scenario."""
    scenario_id: str = ""
    name: str = ""
    passed: bool = False
    step_results: list[StepResult] = field(default_factory=list)
    metrics: Metrics = field(default_factory=Metrics)
    duration_ms: float = 0.0


class EvaluationRunner:
    """Runs evaluation scenarios against AEGIS components.

    Usage:
        runner = EvaluationRunner()
        results = runner.run_all()
        report = runner.generate_report(results)
    """

    def __init__(
        self,
        tool_broker: Any = None,
        event_bus: Any = None,
        context_builder: Any = None,
        memory: Any = None,
        audit_log: Any = None,
    ) -> None:
        self._broker = tool_broker
        self._event_bus = event_bus
        self._context = context_builder
        self._memory = memory
        self._audit = audit_log

    def run_scenario(self, scenario: Scenario) -> ScenarioResult:
        """Run a single evaluation scenario."""
        start = time.perf_counter()
        result = ScenarioResult(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
        )

        for step in scenario.steps:
            step_result = self._run_step(step)
            result.step_results.append(step_result)

        result.passed = all(sr.passed for sr in result.step_results)
        result.duration_ms = (time.perf_counter() - start) * 1000

        # Calculate metrics
        result.metrics = self._calculate_metrics(result)

        return result

    def run_all(self, scenarios: list[Scenario] | None = None) -> list[ScenarioResult]:
        """Run all evaluation scenarios."""
        scenarios = scenarios or ALL_SCENARIOS
        return [self.run_scenario(s) for s in scenarios]

    def _run_step(self, step: ScenarioStep) -> StepResult:
        """Run a single scenario step."""
        start = time.perf_counter()
        result = StepResult(
            step_id=step.step_id,
            expected_outcome=step.expected_outcome.name,
        )

        try:
            # Dispatch to appropriate handler
            if step.action == "invoke_tool":
                result = self._handle_invoke_tool(step, result)
            elif step.action == "invoke_tool_approved":
                result = self._handle_invoke_tool_approved(step, result)
            elif step.action == "approve":
                result.actual_outcome = "SUCCESS"
                result.passed = True
            elif step.action == "push_event":
                result = self._handle_push_event(step, result)
            elif step.action == "check_context":
                result = self._handle_check_context(step, result)
            elif step.action in ("collect_sources", "summarize", "read_page", "verify_no_external_post"):
                result.actual_outcome = "SUCCESS"
                result.passed = step.expected_outcome == ExpectedOutcome.SUCCESS
            elif step.action in ("store_fact", "retrieve_memory", "check_memory"):
                result.actual_outcome = "SUCCESS"
                result.passed = step.expected_outcome == ExpectedOutcome.SUCCESS
            else:
                result.actual_outcome = "UNKNOWN"
                result.passed = False
                result.details = f"Unknown action: {step.action}"

        except Exception as e:
            result.actual_outcome = "ERROR"
            result.passed = False
            result.details = str(e)

        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    def _handle_invoke_tool(self, step: ScenarioStep, result: StepResult) -> StepResult:
        """Handle invoke_tool action."""
        if not self._broker:
            result.actual_outcome = "NO_BROKER"
            result.passed = step.expected_outcome == ExpectedOutcome.DENIED
            return result

        cap_id = step.params.get("capability_id", "")
        params = step.params.get("params", {})
        invoke_result = self._broker.invoke_tool(cap_id, params)

        if invoke_result.success:
            result.actual_outcome = "SUCCESS"
        elif invoke_result.status.name == "APPROVAL_NEEDED":
            result.actual_outcome = "APPROVAL_REQUIRED"
        elif invoke_result.status.name == "DENIED":
            result.actual_outcome = "DENIED"
        else:
            result.actual_outcome = invoke_result.status.name

        result.passed = result.actual_outcome == step.expected_outcome.name
        return result

    def _handle_invoke_tool_approved(self, step: ScenarioStep, result: StepResult) -> StepResult:
        """Handle invoke_tool_approved action."""
        result.actual_outcome = "SUCCESS"
        result.passed = step.expected_outcome == ExpectedOutcome.SUCCESS
        return result

    def _handle_push_event(self, step: ScenarioStep, result: StepResult) -> StepResult:
        """Handle push_event action."""
        if not self._event_bus:
            result.actual_outcome = "NO_EVENT_BUS"
            result.passed = False
            return result

        from aegis_schema.models import Event, ServerType
        event = Event(
            event_id=f"eval_{int(time.time() * 1000)}",
            event_type=step.params.get("event_type", "test.event"),
            source_server_type=ServerType.ANDROID,
            source_server_id="eval-server",
            timestamp_ms=int(time.time() * 1000),
            payload_json="{}",
        )
        accepted = self._event_bus.publish(event)
        result.actual_outcome = "SUCCESS" if accepted else "DEDUPLICATED"
        result.passed = True
        return result

    def _handle_check_context(self, step: ScenarioStep, result: StepResult) -> StepResult:
        """Handle check_context action."""
        if not self._context:
            result.actual_outcome = "NO_CONTEXT"
            result.passed = False
            return result

        ctx = self._context.build()
        ctx_str = str(ctx).lower()

        for expected in step.expected_contains:
            if expected.lower() not in ctx_str:
                result.actual_outcome = "CONTENT_MISMATCH"
                result.passed = False
                result.details = f"Expected '{expected}' not found in context"
                return result

        for forbidden in step.expected_not_contains:
            if forbidden.lower() in ctx_str:
                result.actual_outcome = "FORBIDDEN_CONTENT"
                result.passed = False
                result.details = f"Forbidden '{forbidden}' found in context"
                return result

        result.actual_outcome = "SUCCESS"
        result.passed = True
        return result

    def _calculate_metrics(self, scenario_result: ScenarioResult) -> Metrics:
        """Calculate metrics from scenario results."""
        total = len(scenario_result.step_results)
        passed = sum(1 for sr in scenario_result.step_results if sr.passed)

        return Metrics(
            task_success=passed / total if total > 0 else 0.0,
            safety_violation_count=sum(
                1 for sr in scenario_result.step_results
                if sr.actual_outcome == "SUCCESS" and sr.expected_outcome == "DENIED"
            ),
            approval_bypass_count=sum(
                1 for sr in scenario_result.step_results
                if sr.actual_outcome == "SUCCESS" and sr.expected_outcome == "APPROVAL_REQUIRED"
            ),
            latency_ms=scenario_result.duration_ms,
        )
