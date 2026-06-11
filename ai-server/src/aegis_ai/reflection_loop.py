"""Reflection Loop — autonomous self-analysis and improvement cycle.

Periodically analyzes recent actions, events, and outcomes to:
- Identify what worked and what failed
- Generate improvement ideas
- Update Mind state (confidence, fatigue)
- Feed findings to SelfDevAgent proposals

Safety: Read-only analysis. Does not execute any actions.
All improvement proposals go through normal PolicyEngine flow.

Architecture reference: docs/architecture.md §5.7
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from aegis_ai.memory.reflection import Reflection, ReflectionLog
from aegis_ai.mind.emotion import Emotion
from aegis_ai.mind.goals import GoalManager

logger = logging.getLogger("aegis_ai.reflection_loop")


@dataclass
class ReflectionResult:
    """Result of one reflection cycle."""
    reflection_id: str = ""
    summary: str = ""
    what_worked: list[str] = field(default_factory=list)
    what_failed: list[str] = field(default_factory=list)
    improvement_ideas: list[str] = field(default_factory=list)
    confidence_change: float = 0.0
    urgency_change: int = 0
    duration_ms: float = 0.0


class ReflectionLoop:
    """Autonomous self-analysis loop.

    Runs periodically (triggered by Scheduler) to analyze recent
    actions and events, update Mind state, and generate improvement ideas.

    Safety: This is a READ-ONLY analysis module. It does NOT:
    - Execute any actions
    - Modify PolicyEngine
    - Send messages
    - Access secrets
    """

    def __init__(
        self,
        reflection_log: ReflectionLog | None = None,
        emotion: Emotion | None = None,
        goal_manager: GoalManager | None = None,
        episodic_memory: Any = None,
    ) -> None:
        self._reflection = reflection_log or ReflectionLog()
        self._emotion = emotion
        self._goals = goal_manager
        self._episodic = episodic_memory
        self._last_result: ReflectionResult | None = None

    @property
    def last_result(self) -> ReflectionResult | None:
        return self._last_result

    def run(self) -> ReflectionResult:
        """Run one reflection cycle.

        Analyzes recent events and actions, updates Mind state,
        and writes reflection to ReflectionLog.
        """
        start = time.perf_counter()
        result = ReflectionResult(
            reflection_id=f"refl_{int(time.time() * 1000)}",
        )

        try:
            # 1. Gather recent data
            recent_episodes = []
            if self._episodic:
                recent_episodes = self._episodic.list_recent(20)

            # 2. Analyze what worked and what failed
            worked = []
            failed = []
            for ep in recent_episodes:
                if ep.category == "action_result":
                    detail = ep.detail
                    if detail.get("success"):
                        worked.append(ep.summary)
                    else:
                        failed.append(ep.summary)

            result.what_worked = worked
            result.what_failed = failed

            # 3. Generate improvement ideas
            ideas = []
            if failed:
                ideas.append(f"Investigate recurring failure: {failed[0][:100]}")
            if len(failed) > len(worked) and len(failed) > 3:
                ideas.append("High failure rate — review recent changes")
            result.improvement_ideas = ideas

            # 4. Update Mind state
            if self._emotion:
                if len(failed) > len(worked):
                    # More failures → lower confidence
                    result.confidence_change = -0.1
                    self._emotion.update(
                        confidence=max(0.0, self._emotion.confidence - 0.1),
                    )
                elif len(worked) > len(failed) and len(worked) > 3:
                    # More successes → higher confidence
                    result.confidence_change = 0.05
                    self._emotion.update(
                        confidence=min(1.0, self._emotion.confidence + 0.05),
                    )

            # 5. Write reflection
            summary = (
                f"Reflection: {len(worked)} succeeded, {len(failed)} failed. "
                f"Ideas: {len(ideas)}"
            )
            result.summary = summary

            self._reflection.add(Reflection(
                summary=summary,
                what_worked=worked[:5],
                what_failed=failed[:5],
                improvement_ideas=ideas,
            ))

        except Exception as e:
            logger.exception("Reflection loop failed")
            result.summary = f"Reflection failed: {e}"

        result.duration_ms = (time.perf_counter() - start) * 1000
        self._last_result = result
        return result
