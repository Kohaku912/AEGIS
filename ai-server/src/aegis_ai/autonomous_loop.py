"""Autonomous Loop — core observe→think→plan→act→verify→reflect cycle.

Architecture reference: docs/architecture.md §5.3

The loop is NOT an infinite daemon. It runs ONE cycle per invocation (run_once).
The Trigger Engine calls run_once when an event triggers a rule.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from aegis_ai.audit import AuditLog
from aegis_ai.context_builder import ContextBuilder
from aegis_ai.llm.client import LLMClient, MockLLMClient
from aegis_ai.planner import Plan, Planner

logger = logging.getLogger("aegis_ai.autonomous_loop")


class LoopPhase(Enum):
    IDLE = auto()
    OBSERVE = auto()
    THINK = auto()
    PLAN = auto()
    ACT = auto()
    VERIFY = auto()
    REFLECT = auto()
    FAILED = auto()


@dataclass
class LoopResult:
    """Result of one autonomous loop iteration."""
    phase: LoopPhase = LoopPhase.IDLE
    plan: Plan | None = None
    actions_taken: int = 0
    action_results: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    reflection: str = ""
    should_continue: bool = False
    duration_ms: float = 0.0


class AutonomousLoop:
    """Core decision loop.

    Runs one cycle:
    Observe → Think → Plan → Act → Verify → Reflect

    Safety: ALL actions go through ToolBroker.invoke_tool(),
    which ALWAYS calls PolicyEngine.evaluate() first.
    The AutonomousLoop has NO direct access to execution.
    """

    def __init__(
        self,
        context_builder: ContextBuilder | None = None,
        llm_client: LLMClient | None = None,
        planner: Planner | None = None,
        tool_broker: Any = None,
        audit_log: AuditLog | None = None,
        reflection_log: Any = None,
    ) -> None:
        self._context_builder = context_builder or ContextBuilder()
        self._llm = llm_client or MockLLMClient()
        self._planner = planner or Planner()
        self._tool_broker = tool_broker
        self._audit = audit_log or AuditLog()
        self._reflection = reflection_log
        self._enabled = False
        self._last_result: LoopResult | None = None
        self._iteration_count: int = 0
        self._max_iterations: int = 10   # Safety: limit cycles

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def run_once(self, task_request: Any | None = None) -> LoopResult:
        """Run one complete cycle of the autonomous loop.

        Args:
            task_request: Optional TaskRequest from TriggerEngine.

        Returns:
            LoopResult with phase, actions, errors, and reflection.
        """
        if not self._enabled:
            return LoopResult(phase=LoopPhase.IDLE)

        if self._iteration_count >= self._max_iterations:
            return LoopResult(
                phase=LoopPhase.IDLE,
                errors=[f"Max iterations ({self._max_iterations}) reached"],
            )

        self._iteration_count += 1
        start = time.perf_counter()
        result = LoopResult()

        try:
            # ── 1. OBSERVE ──────────────────────────────────
            result.phase = LoopPhase.OBSERVE
            query = getattr(task_request, "context_summary", "") if task_request else ""
            ctx = self._context_builder.build(triggering_query=query)
            self._audit.log_decision(
                "loop_observe", "autonomous_loop", "OBSERVE",
                detail={"context_id": ctx.context_id},
            )

            # ── 2. THINK ─────────────────────────────────────
            result.phase = LoopPhase.THINK
            context_str = self._context_to_string(ctx)
            thought = self._llm.generate_thought(context_str)
            self._audit.log_decision(
                "loop_think", "autonomous_loop", "THINK",
                detail={"assessment": thought.assessment[:200]},
            )

            # ── 3. PLAN ──────────────────────────────────────
            result.phase = LoopPhase.PLAN
            plan = self._planner.create_plan_from_thought(thought, context_str)
            if plan is None:
                result.phase = LoopPhase.IDLE
                result.errors.append("Planner returned no plan")
                return result
            result.plan = plan
            self._audit.log_decision(
                "loop_plan", "autonomous_loop", "PLAN",
                detail={"plan_id": plan.plan_id, "steps": len(plan.steps)},
            )

            # ── 4. ACT ───────────────────────────────────────
            result.phase = LoopPhase.ACT
            for step in plan.steps:
                if step.status.value in ("COMPLETED", "FAILED"):
                    continue
                cap_id = step.capability_id
                if not cap_id:
                    continue

                # Delegate to ToolBroker (which enforces PolicyEngine)
                if self._tool_broker:
                    invoke_result = self._tool_broker.invoke_tool(cap_id, step.params)
                    result.actions_taken += 1
                    result.action_results.append({
                        "capability_id": cap_id,
                        "success": invoke_result.success,
                        "status": invoke_result.status.name,
                        "output": invoke_result.output,
                        "error": invoke_result.error,
                    })
                    self._audit.log_decision(
                        "loop_act", cap_id, invoke_result.status.name,
                        reason=invoke_result.error[:200] if invoke_result.error else "",
                    )
                else:
                    # No ToolBroker — simulate for testing
                    result.actions_taken += 1
                    result.action_results.append({
                        "capability_id": cap_id,
                        "success": True,
                        "status": "SUCCESS",
                        "output": {"mock": True},
                        "error": "",
                    })
                    self._audit.log_decision(
                        "loop_act", cap_id, "SUCCESS",
                        reason="Mock execution (no ToolBroker)",
                    )

            # ── 5. VERIFY ────────────────────────────────────
            result.phase = LoopPhase.VERIFY
            summary = self._llm.summarize_result(result.action_results, plan.goal)
            self._audit.log_decision(
                "loop_verify", "autonomous_loop", "VERIFY",
                detail={"summary": summary[:200]},
            )

            # ── 6. REFLECT ───────────────────────────────────
            result.phase = LoopPhase.REFLECT
            errors_str = "; ".join(result.errors) if result.errors else "none"
            if self._reflection:
                from aegis_ai.memory.reflection import Reflection
                self._reflection.add(Reflection(
                    summary=f"Cycle {self._iteration_count}: {plan.goal}",
                    what_worked=[r["capability_id"] for r in result.action_results if r["success"]],
                    what_failed=[r["capability_id"] for r in result.action_results if not r["success"]],
                    improvement_ideas=[],
                    linked_action_id=plan.plan_id,
                ))
            result.reflection = summary
            self._audit.log_decision(
                "loop_reflect", "autonomous_loop", "REFLECT",
                detail={"errors": errors_str},
            )

        except Exception as e:
            logger.exception("AutonomousLoop cycle failed")
            result.phase = LoopPhase.FAILED
            result.errors.append(str(e))
            self._audit.log_decision(
                "loop_error", "autonomous_loop", "FAILED",
                reason=str(e)[:500],
            )

        result.duration_ms = (time.perf_counter() - start) * 1000
        self._last_result = result
        return result

    def _context_to_string(self, ctx) -> str:
        """Convert Context to a string for the LLM."""
        parts = [
            f"Identity: {ctx.identity}",
            f"Goals: {', '.join(ctx.current_goals) if ctx.current_goals else 'none'}",
        ]
        if ctx.recent_events:
            parts.append(f"Recent events ({len(ctx.recent_events)}): " +
                        ", ".join(str(e.event_type) for e in ctx.recent_events[:5]))
        if ctx.recent_episodes:
            parts.append(f"Recent episodes: {'; '.join(ctx.recent_episodes[:3])}")
        if ctx.relevant_facts:
            parts.append(f"Relevant facts: {'; '.join(ctx.relevant_facts[:3])}")
        if ctx.relevant_procedures:
            parts.append(f"Relevant procedures: {'; '.join(ctx.relevant_procedures[:2])}")
        if ctx.available_capability_ids:
            parts.append(f"Available capabilities ({len(ctx.available_capability_ids)}): " +
                        ", ".join(ctx.available_capability_ids[:10]))
        return "\n".join(parts)

    @property
    def last_result(self) -> LoopResult | None:
        return self._last_result
