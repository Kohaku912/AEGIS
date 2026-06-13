"""Reflection Engine — post-task analysis and lesson extraction."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from aegis_ai.memory.memory_types import (
    FailureType,
    MemoryRecord,
    MemorySource,
    MemoryType,
    ReflectionResult,
    Sensitivity,
    Visibility,
)

logger = logging.getLogger("aegis_ai.reflection.reflection_engine")


_OUTCOME_SUCCESS = "success"
_OUTCOME_PARTIAL = "partial_success"
_OUTCOME_FAILURE = "failure"
_OUTCOME_DENIED = "denied"
_OUTCOME_REJECTED = "rejected"
_OUTCOME_UNVERIFIED = "unverified"


class ReflectionEngine:
    """Analyzes task outcomes and produces ReflectionResult with lessons."""

    def __init__(self, memory_store: Any = None) -> None:
        self._memory_store = memory_store

    def reflect(
        self,
        task_id: str,
        task_description: str = "",
        tool_results: list[dict[str, Any]] | None = None,
        verification_results: list[dict[str, Any]] | None = None,
        approval_decisions: list[dict[str, Any]] | None = None,
        desire_before: dict[str, float] | None = None,
        desire_after: dict[str, float] | None = None,
        user_feedback: str = "",
        source_desire: str = "",
        frustration: float = 0.0,
    ) -> ReflectionResult:
        now_ms = int(time.time() * 1000)
        tool_results = tool_results or []
        verification_results = verification_results or []
        approval_decisions = approval_decisions or []

        outcome = self._classify_outcome(tool_results, verification_results, approval_decisions)
        root_cause = self._identify_root_cause(tool_results, verification_results, approval_decisions)
        what_worked, what_failed = self._analyze_results(tool_results, verification_results)
        lessons = self._extract_lessons(outcome, root_cause, what_failed)
        failure_type = self._classify_failure(root_cause, tool_results, approval_decisions)

        memory_records: list[MemoryRecord] = []

        memory_records.append(MemoryRecord(
            memory_type=MemoryType.EPISODIC.value,
            title=f"Task {task_id}: {outcome}",
            content=f"Task: {task_description}\nOutcome: {outcome}\nRoot cause: {root_cause}",
            source=MemorySource.REFLECTION.value,
            related_task_id=task_id,
            related_desire=source_desire,
            confidence=0.8 if outcome == _OUTCOME_SUCCESS else 0.6,
            importance=0.7 if outcome == _OUTCOME_FAILURE else 0.5,
            visibility=Visibility.LLM_VISIBLE.value,
            sensitivity=Sensitivity.NORMAL.value,
        ))

        if outcome == _OUTCOME_FAILURE and failure_type:
            memory_records.append(MemoryRecord(
                memory_type=MemoryType.FAILURE_LESSON.value,
                title=f"Failure: {failure_type.value}",
                content=f"Failed task {task_id}: {root_cause}. Avoid: {', '.join(what_failed)}",
                source=MemorySource.REFLECTION.value,
                related_task_id=task_id,
                structured_data={"failure_type": failure_type.value},
                confidence=0.8,
                importance=0.8,
                visibility=Visibility.LLM_VISIBLE.value,
                sensitivity=Sensitivity.NORMAL.value,
            ))

        for dec in approval_decisions:
            if dec.get("status") == "rejected":
                memory_records.append(MemoryRecord(
                    memory_type=MemoryType.APPROVAL_LESSON.value,
                    title=f"Approval rejected: {dec.get('capability_id', '')}",
                    content=f"User rejected: {dec.get('reason', 'no reason')}",
                    source=MemorySource.APPROVAL_DECISION.value,
                    related_approval_id=dec.get("approval_id", ""),
                    related_task_id=task_id,
                    confidence=0.9,
                    importance=0.8,
                    visibility=Visibility.LLM_VISIBLE.value,
                    sensitivity=Sensitivity.NORMAL.value,
                ))

        if source_desire and (desire_before or desire_after):
            before_val = (desire_before or {}).get(source_desire, 5.0)
            after_val = (desire_after or {}).get(source_desire, 5.0)
            delta = after_val - before_val
            delta_label = "improved" if delta > 0 else "unchanged" if delta == 0 else "worsened"
            memory_records.append(MemoryRecord(
                memory_type=MemoryType.DESIRE_LESSON.value,
                title=f"Desire {source_desire}: {delta_label}",
                content=(
                    f"Task {task_id} for {source_desire} "
                    f"(frustration={frustration:.1f}): "
                    f"{before_val:.1f} -> {after_val:.1f}"
                ),
                source=MemorySource.DESIRE_UPDATE.value,
                related_desire=source_desire,
                related_task_id=task_id,
                structured_data={"before": before_val, "after": after_val, "delta": delta},
                confidence=0.7,
                importance=0.6,
                visibility=Visibility.LLM_VISIBLE.value,
                sensitivity=Sensitivity.NORMAL.value,
            ))

        planner_hints: list[str] = []
        if outcome == _OUTCOME_FAILURE:
            planner_hints.append(f"Avoid repeating: {root_cause}")
            if failure_type == FailureType.VERIFICATION_FAILED:
                planner_hints.append("Add observation step before retry")
            if failure_type == FailureType.AUTHENTICATION_REQUIRED:
                planner_hints.append("Request user login before proceeding")

        policy_hints: list[str] = []
        if failure_type in (FailureType.POLICY_DENIED, FailureType.APPROVAL_REJECTED):
            policy_hints.append(f"Similar task was {failure_type.value}: {root_cause}")

        desire_update_hints: dict[str, float] = {}
        if source_desire and outcome == _OUTCOME_SUCCESS:
            desire_update_hints[source_desire] = 1.0
        elif source_desire and outcome == _OUTCOME_FAILURE:
            desire_update_hints[source_desire] = -0.5

        result = ReflectionResult(
            reflection_id=f"refl_{uuid.uuid4().hex[:10]}",
            task_id=task_id,
            summary=f"Task {task_id}: {outcome} — {root_cause[:100]}",
            outcome=outcome,
            root_cause=root_cause,
            what_worked=what_worked,
            what_failed=what_failed,
            lessons=lessons,
            memory_records_to_store=memory_records,
            planner_hints=planner_hints,
            policy_hints=policy_hints,
            desire_update_hints=desire_update_hints,
            should_retry=outcome == _OUTCOME_FAILURE and failure_type not in (
                FailureType.POLICY_DENIED, FailureType.APPROVAL_REJECTED, FailureType.PERMISSION_DENIED,
            ),
            retry_strategy="observe_and_retry" if failure_type == FailureType.VERIFICATION_FAILED else "replan",
            should_suppress_similar_task=failure_type == FailureType.REPEATED_LOOP,
            created_at=now_ms,
        )

        if self._memory_store is not None:
            for rec in memory_records:
                self._memory_store.add_memory(rec)

        return result

    def _classify_outcome(
        self,
        tool_results: list[dict[str, Any]],
        verification_results: list[dict[str, Any]],
        approval_decisions: list[dict[str, Any]],
    ) -> str:
        if any(d.get("status") == "rejected" for d in approval_decisions):
            return _OUTCOME_REJECTED
        if any(d.get("status") == "denied" for d in tool_results):
            return _OUTCOME_DENIED
        if not tool_results:
            return _OUTCOME_UNVERIFIED
        all_success = all(r.get("status") == "success" for r in tool_results)
        any_success = any(r.get("status") == "success" for r in tool_results)
        if all_success:
            return _OUTCOME_SUCCESS
        if any_success:
            return _OUTCOME_PARTIAL
        return _OUTCOME_FAILURE

    def _identify_root_cause(
        self,
        tool_results: list[dict[str, Any]],
        verification_results: list[dict[str, Any]],
        approval_decisions: list[dict[str, Any]],
    ) -> str:
        for d in approval_decisions:
            if d.get("status") == "rejected":
                return f"Approval rejected: {d.get('reason', 'no reason')}"
        for r in tool_results:
            if r.get("status") == "denied":
                return f"Policy denied: {r.get('error', 'unknown')}"
            if r.get("status") == "failed":
                return f"Execution failed: {r.get('error', 'unknown')}"
        for v in verification_results:
            if v.get("status") == "failed":
                return f"Verification failed: {v.get('reason', 'unknown')}"
        return "No obvious root cause"

    def _analyze_results(
        self,
        tool_results: list[dict[str, Any]],
        verification_results: list[dict[str, Any]],
    ) -> tuple[list[str], list[str]]:
        worked: list[str] = []
        failed: list[str] = []
        for r in tool_results:
            if r.get("status") == "success":
                worked.append(f"Tool {r.get('capability_id', 'unknown')} succeeded")
            else:
                failed.append(f"Tool {r.get('capability_id', 'unknown')}: {r.get('error', 'unknown error')}")
        for v in verification_results:
            if v.get("status") == "verified":
                worked.append(f"Verification {v.get('strategy', '')} passed")
            elif v.get("status") == "failed":
                failed.append(f"Verification {v.get('strategy', '')} failed: {v.get('reason', '')}")
        return worked, failed

    def _extract_lessons(self, outcome: str, root_cause: str, what_failed: list[str]) -> list[str]:
        lessons: list[str] = []
        if outcome == _OUTCOME_FAILURE:
            lessons.append(f"Root cause: {root_cause}")
            for f in what_failed[:3]:
                lessons.append(f"Avoid: {f}")
        if outcome == _OUTCOME_SUCCESS:
            lessons.append("Approach worked — consider as procedural memory")
        return lessons

    def _classify_failure(
        self,
        root_cause: str,
        tool_results: list[dict[str, Any]],
        approval_decisions: list[dict[str, Any]],
    ) -> FailureType | None:
        rc = root_cause.lower()
        if "approval rejected" in rc:
            return FailureType.APPROVAL_REJECTED
        if "policy denied" in rc:
            return FailureType.POLICY_DENIED
        if "timeout" in rc:
            return FailureType.TIMEOUT
        if "verification failed" in rc:
            return FailureType.VERIFICATION_FAILED
        if "authentication" in rc or "login" in rc:
            return FailureType.AUTHENTICATION_REQUIRED
        if "permission" in rc:
            return FailureType.PERMISSION_DENIED
        if "capability" in rc and "not found" in rc:
            return FailureType.CAPABILITY_MISSING
        if "unavailable" in rc:
            return FailureType.TOOL_UNAVAILABLE
        if "repeated loop" in rc:
            return FailureType.REPEATED_LOOP
        for r in tool_results:
            if r.get("status") == "failed":
                err = r.get("error", "").lower()
                if "timeout" in err:
                    return FailureType.TIMEOUT
                if "invalid" in err:
                    return FailureType.INVALID_ARGUMENTS
        return FailureType.UNKNOWN if any(r.get("status") == "failed" for r in tool_results) else None
