"""Desire Action Evaluator — pre-execution candidate scoring.

Scores IntrinsicTask candidates by desire gain, risk, annoyance,
capability fit, novelty, repeat penalty, and success probability.
Produces a final_score that MotivationArbiter uses for selection.

Safety: Evaluation only — this module never executes anything.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from aegis_ai.desire.desire_system import DesireSnapshot
from aegis_ai.desire.intrinsic_task_generator import IntrinsicTask, RiskLevel

logger = logging.getLogger("aegis_ai.desire.desire_action_evaluator")


@dataclass
class TaskEvaluation:
    task_id: str
    desire_gain_score: float
    risk_score: float
    annoyance_score: float
    capability_fit_score: float
    novelty_score: float
    repeat_penalty: float
    success_probability: float
    final_score: float
    reason: str
    predicted_desire_effects: dict[str, float]


_RISK_WEIGHTS: dict[RiskLevel, float] = {
    RiskLevel.NONE: 0.0,
    RiskLevel.LOW: 0.1,
    RiskLevel.MEDIUM: 0.4,
    RiskLevel.HIGH: 0.8,
    RiskLevel.FORBIDDEN: 1.0,
}

_NOTIFY_CAPS = {"notify_user", "send_message", "send_email", "post_sns"}


class DesireActionEvaluator:
    """Scores IntrinsicTask candidates for selection.

    Parameters
    ----------
    available_capabilities:
        Set of capability IDs the system can currently execute.
    recent_fingerprints:
        Fingerprints of recently executed tasks (for repeat penalty).
    now_ms:
        Override clock.
    """

    def __init__(
        self,
        available_capabilities: set[str] | None = None,
        recent_fingerprints: list[str] | None = None,
        now_ms: int | None = None,
    ) -> None:
        self._caps = available_capabilities or set()
        self._recent_fps = recent_fingerprints or []
        self._now = now_ms

    def set_available_capabilities(self, caps: set[str]) -> None:
        self._caps = caps

    def score_candidates(
        self,
        tasks: list[IntrinsicTask],
        snapshot: DesireSnapshot,
    ) -> list[TaskEvaluation]:
        """Score all candidates and return sorted by final_score descending."""
        now = self._now if self._now is not None else int(time.time() * 1000)
        evaluations: list[TaskEvaluation] = []

        for task in tasks:
            ev = self._score_one(task, snapshot, now)
            evaluations.append(ev)

        evaluations.sort(key=lambda e: e.final_score, reverse=True)
        return evaluations

    def _score_one(
        self,
        task: IntrinsicTask,
        snapshot: DesireSnapshot,
        now_ms: int,
    ) -> TaskEvaluation:
        desire_gain = self._desire_gain(task, snapshot)
        risk = self._risk_score(task)
        annoyance = self._annoyance_score(task)
        cap_fit = self._capability_fit(task)
        novelty = self._novelty_score(task)
        repeat_pen = self._repeat_penalty(task)
        success_prob = self._success_probability(task, cap_fit, risk)

        raw = (
            desire_gain * 0.35
            + (1.0 - risk) * 0.20
            + (1.0 - annoyance) * 0.10
            + cap_fit * 0.15
            + novelty * 0.05
            + (1.0 - repeat_pen) * 0.05
            + success_prob * 0.10
        )
        final = max(0.0, min(1.0, raw))

        reason_parts = [
            f"gain={desire_gain:.2f}",
            f"risk={risk:.2f}",
            f"annoy={annoyance:.2f}",
            f"caps={cap_fit:.2f}",
            f"novel={novelty:.2f}",
            f"repeat={repeat_pen:.2f}",
            f"success={success_prob:.2f}",
        ]

        return TaskEvaluation(
            task_id=task.task_id,
            desire_gain_score=round(desire_gain, 4),
            risk_score=round(risk, 4),
            annoyance_score=round(annoyance, 4),
            capability_fit_score=round(cap_fit, 4),
            novelty_score=round(novelty, 4),
            repeat_penalty=round(repeat_pen, 4),
            success_probability=round(success_prob, 4),
            final_score=round(final, 4),
            reason=" | ".join(reason_parts),
            predicted_desire_effects=dict(task.expected_desire_effects),
        )

    def _desire_gain(self, task: IntrinsicTask, snapshot: DesireSnapshot) -> float:
        total_gain = 0.0
        for desire_name, effect in task.expected_desire_effects.items():
            info = snapshot.desires.get(desire_name)
            if info is None:
                continue
            frustration = info.get("frustration", 0.0)
            gain = min(effect * (frustration / 10.0), 1.0)
            total_gain += gain
        return min(total_gain, 1.0)

    def _risk_score(self, task: IntrinsicTask) -> float:
        return _RISK_WEIGHTS.get(task.risk_level, 0.5)

    def _annoyance_score(self, task: IntrinsicTask) -> float:
        caps = set(task.required_capabilities)
        if caps & _NOTIFY_CAPS:
            return 0.7
        return 0.0

    def _capability_fit(self, task: IntrinsicTask) -> float:
        if not task.required_capabilities:
            return 1.0
        needed = set(task.required_capabilities)
        have = needed & self._caps
        return len(have) / len(needed)

    def _novelty_score(self, task: IntrinsicTask) -> float:
        if task.fingerprint in self._recent_fps:
            return 0.2
        return 1.0

    def _repeat_penalty(self, task: IntrinsicTask) -> float:
        count = self._recent_fps.count(task.fingerprint)
        if count == 0:
            return 0.0
        return min(count * 0.3, 1.0)

    def _success_probability(
        self,
        task: IntrinsicTask,
        cap_fit: float,
        risk: float,
    ) -> float:
        base = 0.8
        base *= cap_fit
        base *= (1.0 - risk * 0.5)
        if task.risk_level == RiskLevel.FORBIDDEN:
            return 0.0
        return max(0.0, min(1.0, base))
