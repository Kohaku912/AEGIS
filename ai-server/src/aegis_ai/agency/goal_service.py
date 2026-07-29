"""Goal lifecycle service for chat and other non-TaskPlan entry points."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any

from aegis_ai.agency.goal_graph import (
    GoalGraph,
    GoalOutcome,
    GoalVerification,
    VerificationStatus,
)
from aegis_ai.agency.mission import DEFAULT_MISSION_CONTRACT
from aegis_ai.llm.json_utils import extract_json_object


@dataclass
class GoalEvaluation:
    """LLM judgment about whether a user outcome was actually reached."""

    status: str
    reason: str
    evidence: list[str]


class GoalLifecycleService:
    """Create and close Goal graphs consistently outside TaskExecutionEngine."""

    def __init__(self, *, task_manager: Any, llm_gateway: Any) -> None:
        self._tasks = task_manager
        self._llm = llm_gateway

    def create_goal_task(
        self,
        user_goal: str,
        *,
        source: str,
        title: str = "",
        success_condition: str = "",
        value_to_user: str = "",
        obligation_ids: list[str] | None = None,
        presentation: dict[str, Any] | None = None,
        verification_criterion: str = "",
        priority: int = 0,
    ) -> dict[str, Any]:
        """Create a Task owned by an explicit outcome and verification contract."""
        goal_id = f"goal_{uuid.uuid4().hex[:10]}"
        graph = GoalGraph(
            goal_id=goal_id,
            outcome=GoalOutcome(
                description=user_goal,
                success_condition=success_condition
                or "The reported evidence demonstrates that the requested outcome exists.",
                value_to_user=value_to_user
                or "The requested outcome is resolved rather than merely attempted.",
            ),
            source=source,
            priority=priority,
            obligation_ids=list(obligation_ids or []),
            verification=[
                GoalVerification(
                    verification_id=f"verify_{uuid.uuid4().hex[:8]}",
                    criterion=verification_criterion
                    or "Independent evidence verifies the final result against the intended outcome.",
                )
            ],
            presentation=dict(
                presentation or {"report_when": "terminal", "audience": "user"}
            ),
        )
        task = self._tasks.create_task(
            title=title or f"Goal: {user_goal[:50]}",
            goal=user_goal,
            source=source,
            priority=priority,
            goal_graph=graph.to_dict(),
        )
        self._tasks.start_task(task["task_id"])
        return task

    def create_chat_task(self, user_goal: str, *, source: str = "chat") -> dict[str, Any]:
        """Create a chat task with an explicit outcome and verification contract."""
        return self.create_goal_task(
            user_goal,
            source=source,
            title=f"Chat: {user_goal[:50]}",
            success_condition=(
                "The final response resolves the user's requested outcome, and every required tool action succeeds."
            ),
            value_to_user="The user's current request is resolved rather than merely answered.",
            verification_criterion=(
                "An LLM verifies the final result against the original user goal."
            ),
        )

    def finalize_chat_task(
        self,
        task_id: str,
        *,
        user_goal: str,
        response: str,
        tool_results: list[dict[str, Any]] | None = None,
    ) -> GoalEvaluation:
        """Evaluate user value and transition the owning task honestly."""
        return self.finalize_task(
            task_id,
            user_goal=user_goal,
            response=response,
            tool_results=tool_results,
        )

    def finalize_task(
        self,
        task_id: str,
        *,
        user_goal: str,
        response: str,
        tool_results: list[dict[str, Any]] | None = None,
    ) -> GoalEvaluation:
        """Verify and transition any Goal-owned Task."""
        evaluation = self.evaluate(
            user_goal=user_goal,
            response=response,
            tool_results=tool_results or [],
        )
        return self.finalize_with_evaluation(task_id, evaluation, response=response)

    def finalize_with_evaluation(
        self,
        task_id: str,
        evaluation: GoalEvaluation,
        *,
        response: str = "",
    ) -> GoalEvaluation:
        """Persist independent evidence and transition a Goal-owned Task."""
        task = self._tasks.get_task(task_id)
        if task is None:
            return evaluation
        graph = GoalGraph.from_dict(dict(task.get("goal_graph") or {}))
        violations = DEFAULT_MISSION_CONTRACT.validate_goal_graph(graph)
        if violations:
            evaluation = GoalEvaluation(
                status="failed",
                reason="Mission contract violation: " + "; ".join(violations),
                evidence=list(evaluation.evidence),
            )
        for check in graph.verification:
            check.evidence = list(evaluation.evidence)
            if evaluation.status == "achieved":
                check.status = VerificationStatus.PASSED
            elif evaluation.status == "failed":
                check.status = VerificationStatus.FAILED
            else:
                # needs_followup is retryable, not a permanent blocked stall.
                check.status = VerificationStatus.PENDING
        self._tasks.save_goal_graph(task_id, graph.to_dict())

        current_status = str(task.get("status") or "")
        if evaluation.status == "achieved" and current_status not in {
            "completed",
            "failed",
            "cancelled",
            "expired",
        }:
            if current_status == "paused":
                self._tasks.start_task(task_id)
            self._tasks.complete_task(task_id, result_summary=response[:200])
        elif evaluation.status == "failed" and current_status not in {
            "completed",
            "failed",
            "cancelled",
            "expired",
        }:
            self._tasks.fail_task(task_id, error=evaluation.reason)
        elif evaluation.status == "needs_followup" and current_status == "running":
            # Keep the task open for a later cycle without marking verification blocked.
            self._tasks.pause_task(task_id)
        return evaluation

    def evaluate(
        self,
        *,
        user_goal: str,
        response: str,
        tool_results: list[dict[str, Any]],
    ) -> GoalEvaluation:
        """Ask the LLM to evaluate outcome evidence instead of keyword rules."""
        if self._llm is None:
            return GoalEvaluation(
                status="needs_followup",
                reason="Goal verification is unavailable because no LLM is configured.",
                evidence=[],
            )
        prompt = f"""Evaluate whether this AEGIS interaction achieved the user's goal.
Judge the outcome, not response fluency or whether a tool merely ran.
Tool success is supporting evidence only and is never sufficient by itself.
Return JSON only.

User goal:
{user_goal}

Final response:
{response}

Tool results:
{json.dumps(tool_results, ensure_ascii=False, default=str)}

Return:
{{
  "status": "achieved|needs_followup|failed",
  "reason": "specific outcome-based reason",
  "evidence": ["observable evidence used for the judgment"]
}}"""
        try:
            result = self._llm.generate(
                prompt=prompt,
                system_prompt=(
                    "You are AEGIS's goal verifier. Do not infer success from activity alone. Output JSON only."
                ),
                max_tokens=400,
                temperature=0.0,
                json_mode=True,
                context_meta={"purpose": "goal_verification"},
            )
            if not getattr(result, "success", False):
                raise RuntimeError(str(getattr(result, "error", "verification failed")))
            data = extract_json_object(str(result.content))
            status = str(data.get("status") or "needs_followup")
            if status not in {"achieved", "needs_followup", "failed"}:
                status = "needs_followup"
            return GoalEvaluation(
                status=status,
                reason=str(data.get("reason") or "No verification reason supplied."),
                evidence=[str(item) for item in data.get("evidence", []) if item],
            )
        except Exception as exc:
            return GoalEvaluation(
                status="needs_followup",
                reason=f"Goal verification could not be completed: {exc}",
                evidence=[],
            )
