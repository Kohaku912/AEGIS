"""LLM Client interface and mock implementation.

The LLMClient defines the contract for AI decision-making.
MockLLMClient provides deterministic responses for testing.

LLM is NOT used for safety decisions — PolicyEngine handles that.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMThought:
    """Result of the Think phase."""
    summary: str = ""
    assessment: str = ""            # What's happening, what's important
    recommended_action: str = ""    # What the AI thinks should happen next
    confidence: float = 0.5
    risks_identified: list[str] = field(default_factory=list)


@dataclass
class LLMPlanOutput:
    """Result of the Plan phase."""
    goal: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    fallback_steps: list[dict[str, Any]] = field(default_factory=list)
    risk_assessment: str = ""


class LLMClient(ABC):
    """Abstract interface for LLM integration.

    Concrete implementations (OpenAI, local LLM, etc.) must implement
    these methods. The LLM is used for reasoning only — never for safety.
    """

    @abstractmethod
    def generate_thought(self, context: str) -> LLMThought:
        """Evaluate the current situation and recommend next action."""

    @abstractmethod
    def generate_plan(self, thought: LLMThought, context: str) -> LLMPlanOutput:
        """Decompose the recommended action into executable steps."""

    @abstractmethod
    def summarize_result(self, results: list[dict[str, Any]], goal: str) -> str:
        """Summarize action results for the Verify/Reflect phases."""


class MockLLMClient(LLMClient):
    """Deterministic mock LLM for testing.

    Returns predictable outputs based on the intent described in context.
    Does NOT make real LLM calls.
    """

    def generate_thought(self, context: str) -> LLMThought:
        ctx_lower = context.lower()

        if "screenshot" in ctx_lower or "screen" in ctx_lower:
            return LLMThought(
                summary="User wants to see what's on screen",
                assessment="Low risk observation task",
                recommended_action="Take a screenshot using pc-server.screenshot.get_screenshot",
                confidence=0.9,
                risks_identified=[],
            )
        elif "test" in ctx_lower and ("fail" in ctx_lower or "error" in ctx_lower):
            return LLMThought(
                summary="Test failure detected",
                assessment="Need to investigate the failing test",
                recommended_action="Run dev.run_tests to verify",
                confidence=0.8,
                risks_identified=["May take time", "Could reveal more failures"],
            )
        elif "weather" in ctx_lower or "research" in ctx_lower:
            return LLMThought(
                summary="Research request",
                assessment="Information gathering task",
                recommended_action="Search the web using browser.open_page and extract text",
                confidence=0.7,
                risks_identified=["External network access"],
            )
        elif "delete" in ctx_lower or "remove" in ctx_lower:
            return LLMThought(
                summary="File deletion requested",
                assessment="HIGH RISK — requires approval",
                recommended_action="Delete file using pc-server.file.delete",
                confidence=0.6,
                risks_identified=["Permanent data loss", "Requires user approval"],
            )
        else:
            return LLMThought(
                summary="General request",
                assessment="Standard observation task",
                recommended_action="Observe current state using pc-server.screenshot.get_screenshot",
                confidence=0.5,
                risks_identified=[],
            )

    def generate_plan(self, thought: LLMThought, context: str) -> LLMPlanOutput:
        rec = thought.recommended_action.lower()

        if "screenshot" in rec and "pc-server.screenshot" in rec:
            return LLMPlanOutput(
                goal="Take a screenshot",
                steps=[{
                    "description": "Capture the current display",
                    "capability_id": "pc-server.screenshot.get_screenshot",
                    "params": {"display_id": 0},
                    "expected_result": "PNG image of the screen",
                    "risk": "LEVEL_0_READ",
                }],
                fallback_steps=[],
                risk_assessment="No risk — read-only operation",
            )
        elif "test" in rec:
            return LLMPlanOutput(
                goal="Run test suite",
                steps=[{
                    "description": "Execute the project test suite",
                    "capability_id": "dev-server.test.run_tests",
                    "params": {"target": "all"},
                    "expected_result": "Test results with pass/fail counts",
                    "risk": "LEVEL_1_SAFE_ACT",
                }],
                fallback_steps=[{
                    "description": "Check individual test file",
                    "capability_id": "dev-server.test.run_tests",
                    "params": {"target": "ai-server"},
                }],
                risk_assessment="Low risk — sandboxed execution",
            )
        elif "delete" in rec:
            return LLMPlanOutput(
                goal="Delete file",
                steps=[{
                    "description": "Delete the specified file",
                    "capability_id": "pc-server.file.delete",
                    "params": {"path": "/tmp/test.txt"},
                    "expected_result": "File deleted",
                    "risk": "LEVEL_2_APPROVAL",
                }],
                fallback_steps=[{
                    "description": "Move to trash instead",
                    "capability_id": "pc-server.file.delete",
                    "params": {"path": "/tmp/test.txt", "permanent": False},
                }],
                risk_assessment="HIGH RISK — requires user approval",
            )
        else:
            return LLMPlanOutput(
                goal=thought.recommended_action,
                steps=[{
                    "description": "Observe current state",
                    "capability_id": "pc-server.screenshot.get_screenshot",
                    "params": {},
                    "expected_result": "Screenshot of current display",
                    "risk": "LEVEL_0_READ",
                }],
                fallback_steps=[],
                risk_assessment="Low risk",
            )

    def summarize_result(self, results: list[dict[str, Any]], goal: str) -> str:
        if not results:
            return f"No results for goal: {goal}"
        successes = sum(1 for r in results if r.get("success", False))
        failures = len(results) - successes
        return (
            f"Goal '{goal}': {successes} succeeded, {failures} failed. "
            f"{'All steps completed.' if failures == 0 else 'Some steps failed.'}"
        )
