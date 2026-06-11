"""Priorities — dynamic priority calculation based on Mind state.

Combines identity, desire, emotion, and goals into priority scores.
Used by ContextBuilder and Scheduler to bias decision-making.
Does NOT override PolicyEngine safety decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PriorityScore:
    """A calculated priority score for a potential action."""
    action_type: str
    score: float  # 0.0 = lowest, 1.0 = highest
    reason: str = ""


class PriorityEngine:
    """Calculates priority scores based on Mind state.

    Used by ContextBuilder to bias which events/actions get attention.
    Never overrides PolicyEngine safety decisions.
    """

    def __init__(
        self,
        desire: Any = None,
        emotion: Any = None,
        goals: Any = None,
    ) -> None:
        self._desire = desire
        self._emotion = emotion
        self._goals = goals

    def score_action(self, action_type: str, context: dict[str, Any] | None = None) -> PriorityScore:
        """Calculate priority score for a potential action."""
        score = 0.5  # Base score
        reasons = []

        # Desire bias
        if self._desire:
            weight = self._desire.get_weight(action_type)
            if weight > 0:
                score += (weight - 0.5) * 0.3
                reasons.append(f"desire={weight:.2f}")

        # Emotion bias
        if self._emotion:
            if self._emotion.is_urgent():
                score += 0.2
                reasons.append("urgent")
            if self._emotion.is_fatigued():
                score -= 0.1
                reasons.append("fatigued")

        # Clamp
        score = max(0.0, min(1.0, score))

        return PriorityScore(
            action_type=action_type,
            score=score,
            reason=", ".join(reasons) if reasons else "baseline",
        )

    def should_defer(self, action_type: str) -> bool:
        """Check if an action should be deferred based on Mind state."""
        if self._emotion and self._emotion.is_fatigued():
            return True
        if self._desire:
            weight = self._desire.get_weight(action_type)
            if weight < 0.3:
                return True
        return False
