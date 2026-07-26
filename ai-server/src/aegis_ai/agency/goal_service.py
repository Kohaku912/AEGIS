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

    def create_chat_task(self, user_goal: str, *, source: str = "chat") -> dict[str, Any]:
        """Create a chat task with an explicit outcome and verification contract."""
        goal_id = f"goal_{uuid.uuid4().hex[:10]}"
        graph = GoalGraph(
            goal_id=goal_id,
            outcome=GoalOutcome(
                description=user_goal,
                success_condition=(
                    "The final response resolves the user's requested outcome, and every required tool action succeeds."
                ),
                value_to_user="The user's current request is resolved rather than merely answered.",
            ),
            source=source,
            verification=[
                GoalVerification(
                    verification_id=f"verify_{uuid.uuid4().hex[:8]}",
                    criterion="An LLM verifies the final result against the original user goal.",
                )
            ],
            presentation={"report_when": "terminal", "audience": "user"},
        )
        task = self._tasks.create_task(
            title=f"Chat: {user_goal[:50]}",
            goal=user_goal,
            source=source,
            goal_graph=graph.to_dict(),
        )
        self._tasks.start_task(task["task_id"])
        return task

    def finalize_chat_task(
        self,
        task_id: str,
        *,
        user_goal: str,
        response: str,
        tool_results: list[dict[str, Any]] | None = None,
    ) -> GoalEvaluation:
        """Evaluate user value and transition the owning task honestly."""
        evaluation = self.evaluate(
            user_goal=user_goal,
            response=response,
            tool_results=tool_results or [],
        )
        task = self._tasks.get_task(task_id)
        if task is None:
            return evaluation
        graph = GoalGraph.from_dict(dict(task.get("goal_graph") or {}))
        if graph.verification:
            check = graph.verification[0]
            check.evidence = list(evaluation.evidence)
            if evaluation.status == "achieved":
                check.status = VerificationStatus.PASSED
            elif evaluation.status == "failed":
                check.status = VerificationStatus.FAILED
            else:
                check.status = VerificationStatus.BLOCKED
        self._tasks.save_goal_graph(task_id, graph.to_dict())

        if evaluation.status == "achieved":
            self._tasks.complete_task(task_id, result_summary=response[:200])
        elif evaluation.status == "failed":
            self._tasks.fail_task(task_id, error=evaluation.reason)
        else:
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
