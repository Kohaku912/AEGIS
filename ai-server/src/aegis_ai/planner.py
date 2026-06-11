"""Planner — task decomposition and prioritization.

Decomposes high-level intents into executable Step lists.
Each step has a capability_id, params, expected_result, and risk estimate.
All execution goes through ToolBroker → PolicyEngine.

Architecture reference: docs/architecture.md §5.4
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from aegis_ai.llm.client import LLMClient, LLMPlanOutput, LLMThought, MockLLMClient


class TaskStatus(Enum):
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class PlannedStep:
    """A single executable step in a plan."""
    step_id: str = ""
    description: str = ""
    capability_id: str = ""             # Which capability to invoke
    params: dict[str, Any] = field(default_factory=dict)
    expected_result: str = ""           # What should happen
    risk_level: str = "LEVEL_0_READ"    # Estimated risk
    depends_on: list[str] = field(default_factory=list)  # Step IDs
    priority: int = 5                   # 1=highest, 10=lowest
    status: TaskStatus = TaskStatus.PENDING
    fallback_step_id: str = ""          # Alternative if this step fails


@dataclass
class Plan:
    """A plan composed of ordered steps."""
    plan_id: str = ""
    goal: str = ""
    steps: list[PlannedStep] = field(default_factory=list)
    fallback_steps: list[PlannedStep] = field(default_factory=list)
    risk_assessment: str = ""
    created_at_ms: int = 0


class Planner:
    """Decomposes high-level goals into executable steps.

    Uses LLMClient.generate_plan() for decomposition.
    Does NOT execute steps — that's the AutonomousLoop's job.
    Does NOT enforce safety — that's PolicyEngine's job.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or MockLLMClient()

    def create_plan(self, goal: str) -> Plan:
        """Create a basic plan for a goal (without LLM)."""
        return Plan(
            plan_id=f"plan_{int(time.time() * 1000)}",
            goal=goal,
            created_at_ms=int(time.time() * 1000),
        )

    def create_plan_from_thought(
        self, thought: LLMThought, context_str: str,
    ) -> Plan | None:
        """Create a plan using LLM decomposition of a thought."""
        llm_output: LLMPlanOutput = self._llm.generate_plan(thought, context_str)

        if not llm_output.steps:
            # Fallback: create a minimal plan from the thought
            return self._fallback_plan(thought)

        steps = []
        for i, step_data in enumerate(llm_output.steps):
            step = PlannedStep(
                step_id=f"step_{i+1}",
                description=step_data.get("description", ""),
                capability_id=step_data.get("capability_id", ""),
                params=step_data.get("params", {}),
                expected_result=step_data.get("expected_result", ""),
                risk_level=step_data.get("risk", "LEVEL_1_SAFE_ACT"),
                priority=5,
            )
            if i > 0:
                step.depends_on = [f"step_{i}"]
            steps.append(step)

        # Fallback steps
        fallbacks = []
        for i, fb_data in enumerate(llm_output.fallback_steps):
            fb = PlannedStep(
                step_id=f"fallback_{i+1}",
                description=fb_data.get("description", ""),
                capability_id=fb_data.get("capability_id", ""),
                params=fb_data.get("params", {}),
                expected_result=fb_data.get("expected_result", "Fallback execution"),
                risk_level=fb_data.get("risk", "LEVEL_1_SAFE_ACT"),
                priority=8,
            )
            fallbacks.append(fb)

        return Plan(
            plan_id=f"plan_{int(time.time() * 1000)}",
            goal=llm_output.goal or thought.recommended_action,
            steps=steps,
            fallback_steps=fallbacks,
            risk_assessment=llm_output.risk_assessment or "Unknown",
            created_at_ms=int(time.time() * 1000),
        )

    def _fallback_plan(self, thought: LLMThought) -> Plan | None:
        """Create a minimal plan when LLM returns no steps."""
        return Plan(
            plan_id=f"plan_{int(time.time() * 1000)}",
            goal=thought.recommended_action,
            steps=[PlannedStep(
                step_id="step_1",
                description=thought.recommended_action,
                capability_id="",
                expected_result="Observation complete",
                risk_level="LEVEL_0_READ",
            )],
            risk_assessment="Low risk — observation only",
            created_at_ms=int(time.time() * 1000),
        )

    def next_step(self, plan: Plan) -> PlannedStep | None:
        """Get the next ready step (dependencies satisfied)."""
        completed = {s.step_id for s in plan.steps if s.status == TaskStatus.COMPLETED}
        for step in plan.steps:
            if step.status != TaskStatus.PENDING:
                continue
            if all(dep in completed for dep in step.depends_on):
                return step
        return None
