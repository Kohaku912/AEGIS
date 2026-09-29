"""Intake router — Phase 4 (instruction.md §11, §36).

`IntakeClassifier` と `IntakeDeduplicator` を束ねて、`RoutingDecision` を返す。

DoD:
- 1000 event のうち Agent delegate に進むのは **10% 以下** (本テストでは再現性
  確保のため mock classifier で検証).
- `IntakeSettings.enabled=False` のときは classifier も dedup もスキップし、
  既存挙動を保つ.
- `requires_agent_score >= requires_agent_threshold` のときだけ AGENT_DELEGATE.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from aegis_ai.intake.classifier import IntakeClassifier
from aegis_ai.intake.deduplicator import IntakeDeduplicator
from aegis_ai.intake.models import (
    IntakeDecision,
    IntakeResult,
    IntakeRoute,
    RoutingDecision,
)

logger = logging.getLogger("aegis_ai.intake.router")


@dataclass
class IntakeRouter:
    """classifier + dedup を束ねるルータ.

    Attributes:
        classifier: `IntakeClassifier` インスタンス.
        deduplicator: `IntakeDeduplicator` インスタンス.
        enabled: master switch. False のときは classifier も dedup もスキップ.
        requires_agent_threshold: `requires_agent_score` がこの値以上なら
            Agent delegate 経路に進む.
    """

    classifier: IntakeClassifier = field(default_factory=IntakeClassifier)
    deduplicator: IntakeDeduplicator = field(default_factory=IntakeDeduplicator)
    enabled: bool = True
    requires_agent_threshold: float = 0.5

    def route(self, event: dict[str, Any], *, event_id: str = "") -> RoutingDecision:
        """event 1 個に対して routing 判定を返す.

        `enabled=False` のときは `IntakeResult(decision=LOCAL_INTERPRET)` を
        そのまま返す (既存挙動と等価).
        """
        eid = event_id or str(event.get("id") or event.get("event_id") or "ev")

        if not self.enabled:
            return RoutingDecision(
                route=IntakeRoute.SKIP,
                intake_result=IntakeResult(
                    event_id=eid,
                    decision=IntakeDecision.LOCAL_INTERPRET,
                    reason="intake_disabled",
                ),
                reason="intake_disabled",
            )

        # 1. dedup を先に評価 (LLM 呼び出し節約)
        if self.deduplicator.has_seen(event):
            intake_result = IntakeResult(
                event_id=eid,
                decision=IntakeDecision.DUPLICATE,
                novelty=0.0,
                reason="fingerprint_already_seen",
            )
            return RoutingDecision(
                route=IntakeRoute.DUPLICATE,
                intake_result=intake_result,
                reason="dedup_fingerprint_match",
            )

        # 2. classifier で判定
        intake_result = self.classifier.classify(event, event_id=eid)

        # 3. dedup を novelty でもう一度判定
        if self.deduplicator.is_duplicate(event, novelty=intake_result.novelty):
            intake_result.decision = IntakeDecision.DUPLICATE
            return RoutingDecision(
                route=IntakeRoute.DUPLICATE,
                intake_result=intake_result,
                reason="dedup_novelty_below_threshold",
            )

        # 4. routing 判定
        if (
            intake_result.decision == IntakeDecision.REQUIRES_AGENT
            and intake_result.requires_agent_score >= self.requires_agent_threshold
        ):
            self.deduplicator.record(event)
            return RoutingDecision(
                route=IntakeRoute.AGENT_DELEGATE,
                intake_result=intake_result,
                reason=intake_result.reason or "requires_agent",
            )

        if intake_result.decision == IntakeDecision.DEFER:
            return RoutingDecision(
                route=IntakeRoute.DEFER,
                intake_result=intake_result,
                reason="classifier_defer",
            )

        # LOCAL_INTERPRET or DUPLICATE
        self.deduplicator.record(event)
        return RoutingDecision(
            route=IntakeRoute.SKIP,
            intake_result=intake_result,
            reason=(
                intake_result.reason
                or f"requires_agent_score<{self.requires_agent_threshold}"
            ),
        )

    def stats(self) -> dict[str, Any]:
        return {
            "dedup": self.deduplicator.stats(),
            "enabled": self.enabled,
            "requires_agent_threshold": self.requires_agent_threshold,
        }


__all__ = ["IntakeRouter"]
