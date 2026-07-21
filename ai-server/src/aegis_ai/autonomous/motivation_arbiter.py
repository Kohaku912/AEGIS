"""Motivation Arbiter — selects the single task to execute next.

Receives candidates from multiple sources (user, schedule, events, desires)
and picks exactly one, respecting safety, cooldowns, and priority ordering.

This module does NOT replace PolicyEngine.  It only decides *which* task
to submit; the actual allow/approve/deny decision stays in PolicyEngine.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from aegis_ai.desire.desire_action_evaluator import DesireActionEvaluator
from aegis_ai.desire.intrinsic_task_generator import IntrinsicTask, RiskLevel

logger = logging.getLogger("aegis_ai.autonomous.motivation_arbiter")


class DecisionType(Enum):
    USER_EXPLICIT = auto()
    SAFETY_URGENT = auto()
    SCHEDULED = auto()
    EVENT_DRIVEN = auto()
    DESIRE_DRIVEN = auto()
    SKIP = auto()


@dataclass
class ExternalTask:
    task_id: str
    title: str
    source: str
    priority: float
    risk_level: RiskLevel
    requires_approval: bool
    required_capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MotivationDecision:
    selected_task: ExternalTask | IntrinsicTask | None
    decision_type: DecisionType
    score: float
    reason: str
    skipped_tasks: list[dict[str, Any]]
    risk_level: RiskLevel
    requires_approval: bool
    created_at: int


@dataclass
class _ArbiterContext:
    available_capabilities: set[str]
    recent_task_ids: list[str]
    recent_failures: list[str]
    cooldown_fingerprints: set[str]
    can_notify_user: bool
    now_ms: int


def _score_task(
    task: ExternalTask | IntrinsicTask,
    ctx: _ArbiterContext,
    base_priority: float,
) -> tuple[float, str]:
    if isinstance(task, IntrinsicTask):
        tid = task.task_id
        risk = task.risk_level
        caps = set(task.required_capabilities)
    else:
        tid = task.task_id
        risk = task.risk_level
        caps = set(task.required_capabilities)

    if tid in ctx.recent_failures:
        return -1.0, "recent_failure"

    if risk == RiskLevel.FORBIDDEN:
        return -1.0, "forbidden"

    missing = caps - ctx.available_capabilities
    if missing and caps:
        return -1.0, f"missing_capabilities:{','.join(sorted(missing))}"

    return base_priority, "ok"


class MotivationArbiter:
    """Selects a single task to execute from multiple sources.

    Priority order:
    1. User explicit tasks
    2. Safety / reliability urgent tasks
    3. Scheduled tasks
    4. Event-driven tasks
    5. Desire-driven tasks

    Parameters
    ----------
    available_capabilities:
        Set of capability IDs the system can currently execute.
    recent_task_ids:
        IDs of tasks executed in the current cycle (for dedup).
    recent_failures:
        IDs of tasks that recently failed (suppressed).
    cooldown_fingerprints:
        Fingerprints of desire-driven tasks currently in cooldown.
    can_notify_user:
        Whether user notification is currently allowed.
    now_ms:
        Override clock.
    evaluator:
        Optional desire action evaluator for scoring candidates.
    memory_store:
        Optional memory store for consulting past failures and preferences.
    """

    def __init__(
        self,
        available_capabilities: set[str] | None = None,
        recent_task_ids: list[str] | None = None,
        recent_failures: list[str] | None = None,
        cooldown_fingerprints: set[str] | None = None,
        can_notify_user: bool = True,
        now_ms: int | None = None,
        evaluator: DesireActionEvaluator | None = None,
        memory_store: Any = None,
    ) -> None:
        self._caps = available_capabilities or set()
        self._recent_ids = recent_task_ids or []
        self._failures = recent_failures or []
        self._cooldown_fps = cooldown_fingerprints or set()
        self._can_notify = can_notify_user
        self._now = now_ms
        self._evaluator = evaluator
        self._memory_store = memory_store

    def _check_memory_penalties(self, task_id: str, source_desire: str = "") -> tuple[float, str]:
        """Check memory for past failures/approval rejections that should penalize this task."""
        if self._memory_store is None:
            return 0.0, ""

        penalty = 0.0
        reasons: list[str] = []

        failure_lessons = self._memory_store.search_memories(
            memory_type="failure_lesson",
            related_desire=source_desire,
            min_importance=0.5,
            limit=3,
        )
        if failure_lessons:
            penalty += 0.3 * len(failure_lessons)
            reasons.append(f"{len(failure_lessons)} past failures for {source_desire}")

        approval_lessons = self._memory_store.search_memories(
            memory_type="approval_lesson",
            related_desire=source_desire,
            min_importance=0.5,
            limit=3,
        )
        rejected = [
            record
            for record in approval_lessons
            if str(record.structured_data.get("decision") or "") == "rejected"
        ]
        if rejected:
            penalty += 0.2 * len(rejected)
            reasons.append(f"{len(rejected)} past rejections for {source_desire}")

        return penalty, "; ".join(reasons)

    def decide(
        self,
        user_tasks: list[ExternalTask] | None = None,
        scheduled_tasks: list[ExternalTask] | None = None,
        event_tasks: list[ExternalTask] | None = None,
        desire_tasks: list[IntrinsicTask] | None = None,
    ) -> MotivationDecision:
        now = self._now if self._now is not None else int(time.time() * 1000)
        ctx = _ArbiterContext(
            available_capabilities=self._caps,
            recent_task_ids=list(self._recent_ids),
            recent_failures=list(self._failures),
            cooldown_fingerprints=set(self._cooldown_fps),
            can_notify_user=self._can_notify,
            now_ms=now,
        )

        skipped: list[dict[str, Any]] = []

        # ── 1. User explicit ────────────────────────────────────────────
        for t in user_tasks or []:
            if t.task_id in ctx.recent_task_ids:
                skipped.append({"task_id": t.task_id, "reason": "already_executed"})
                continue
            score, reason = _score_task(t, ctx, t.priority + 100.0)
            if score < 0:
                skipped.append({"task_id": t.task_id, "reason": reason})
                continue
            return MotivationDecision(
                selected_task=t,
                decision_type=DecisionType.USER_EXPLICIT,
                score=score,
                reason="User explicit task takes highest priority.",
                skipped_tasks=skipped,
                risk_level=t.risk_level,
                requires_approval=t.requires_approval,
                created_at=now,
            )

        # ── 2. Scheduled ────────────────────────────────────────────────
        for t in scheduled_tasks or []:
            if t.task_id in ctx.recent_task_ids:
                skipped.append({"task_id": t.task_id, "reason": "already_executed"})
                continue
            score, reason = _score_task(t, ctx, t.priority + 30.0)
            if score < 0:
                skipped.append({"task_id": t.task_id, "reason": reason})
                continue
            return MotivationDecision(
                selected_task=t,
                decision_type=DecisionType.SCHEDULED,
                score=score,
                reason="Scheduled task.",
                skipped_tasks=skipped,
                risk_level=t.risk_level,
                requires_approval=t.requires_approval,
                created_at=now,
            )

        # ── 4. Event-driven ─────────────────────────────────────────────
        for t in event_tasks or []:
            if t.task_id in ctx.recent_task_ids:
                skipped.append({"task_id": t.task_id, "reason": "already_executed"})
                continue
            score, reason = _score_task(t, ctx, t.priority + 20.0)
            if score < 0:
                skipped.append({"task_id": t.task_id, "reason": reason})
                continue
            return MotivationDecision(
                selected_task=t,
                decision_type=DecisionType.EVENT_DRIVEN,
                score=score,
                reason="Event-driven task.",
                skipped_tasks=skipped,
                risk_level=t.risk_level,
                requires_approval=t.requires_approval,
                created_at=now,
            )

        # ── 5. Desire-driven ────────────────────────────────────────────
        eligible_desire: list[IntrinsicTask] = []
        for t in desire_tasks or []:
            fp = t.fingerprint
            if fp in ctx.cooldown_fingerprints:
                skipped.append({"task_id": t.task_id, "reason": "cooldown"})
                continue
            if t.task_id in ctx.recent_task_ids:
                skipped.append({"task_id": t.task_id, "reason": "already_executed"})
                continue

            is_notify = "notify_user" in t.required_capabilities
            if is_notify and not ctx.can_notify_user:
                skipped.append({"task_id": t.task_id, "reason": "notify_suppressed"})
                continue

            score, reason = _score_task(t, ctx, t.priority)
            if score < 0:
                skipped.append({"task_id": t.task_id, "reason": reason})
                continue

            mem_penalty, mem_reason = self._check_memory_penalties(
                t.task_id, t.source_desire,
            )
            if mem_penalty > 0:
                score -= mem_penalty
                reason += f" [memory penalty: {mem_reason}]"

            if score <= 0:
                skipped.append({"task_id": t.task_id, "reason": f"memory_penalty: {mem_reason}"})
                continue

            eligible_desire.append(t)

        if eligible_desire:
            if self._evaluator is not None:
                from aegis_ai.desire.desire_system import DesireSnapshot

                snap = DesireSnapshot(
                    timestamp=now,
                    average_frustration=0.0,
                    max_frustration=0.0,
                    top_unsatisfied_desires=[],
                    desires={},
                )
                evaluations = self._evaluator.score_candidates(eligible_desire, snap)
                best_eval = evaluations[0] if evaluations else None
                best_task = None
                for t in eligible_desire:
                    if best_eval and t.task_id == best_eval.task_id:
                        best_task = t
                        break
                if best_task is None:
                    best_task = eligible_desire[0]
                final_score = best_eval.final_score if best_eval else best_task.priority
                reason_str = best_eval.reason if best_eval else f"Desire-driven: {best_task.reason}"
            else:
                best_task = max(eligible_desire, key=lambda t: t.priority)
                final_score = best_task.priority
                reason_str = f"Desire-driven: {best_task.reason}"

            return MotivationDecision(
                selected_task=best_task,
                decision_type=DecisionType.DESIRE_DRIVEN,
                score=final_score,
                reason=reason_str,
                skipped_tasks=skipped,
                risk_level=best_task.risk_level,
                requires_approval=best_task.requires_user_approval,
                created_at=now,
            )

        # ── Nothing selected ────────────────────────────────────────────
        return MotivationDecision(
            selected_task=None,
            decision_type=DecisionType.SKIP,
            score=0.0,
            reason="No eligible task found.",
            skipped_tasks=skipped,
            risk_level=RiskLevel.NONE,
            requires_approval=False,
            created_at=now,
        )
