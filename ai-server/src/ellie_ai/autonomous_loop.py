"""Autonomous Loop — core observe→think→plan→act→verify→reflect cycle.

STATUS: Skeleton — the loop structure is defined but LLM/execution are not implemented.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto

from ellie_ai.context_builder import Context, ContextBuilder

logger = logging.getLogger("ellie_ai.autonomous_loop")


class LoopPhase(Enum):
    IDLE = auto()
    OBSERVE = auto()
    THINK = auto()
    PLAN = auto()
    ACT = auto()
    VERIFY = auto()
    REFLECT = auto()


@dataclass
class LoopResult:
    """Result of one autonomous loop iteration."""
    phase: LoopPhase = LoopPhase.IDLE
    actions_taken: int = 0
    errors: list[str] = field(default_factory=list)
    reflection: str = ""
    should_continue: bool = False


class AutonomousLoop:
    """Core decision loop for Ellie.

    Architecture reference: docs/architecture.md §5.3

    Full cycle (not yet implemented):
    Observe → Think → Plan → Act → Verify → Reflect
    """

    def __init__(self, context_builder: ContextBuilder | None = None) -> None:
        self._context_builder = context_builder or ContextBuilder()
        self._enabled = False
        self._last_result: LoopResult | None = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def iterate(self, context: Context | None = None) -> LoopResult:
        """Run one iteration of the autonomous loop.

        Currently a skeleton — returns IDLE without performing any actions.
        """
        if not self._enabled:
            return LoopResult(phase=LoopPhase.IDLE)

        ctx = context or self._context_builder.build()

        # TODO: Full loop implementation
        # 1. OBSERVE — already done by ContextBuilder
        # 2. THINK — LLM evaluates context against goals/identity
        # 3. PLAN — Planner decomposes intent into actions
        # 4. ACT — ToolBroker dispatches actions through PolicyEngine
        # 5. VERIFY — Check results against expected outcomes
        # 6. REFLECT — Write to Reflection Log

        result = LoopResult(phase=LoopPhase.IDLE)
        self._last_result = result
        return result

    @property
    def last_result(self) -> LoopResult | None:
        return self._last_result
