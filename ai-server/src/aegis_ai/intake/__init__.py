"""Intake — Phase 4 (instruction.md §36).

全 Event をそのまま Agent (OpenHands) に投げず、小型 LLM で
→「Agent 不要」を早期判定する。

DASHBOARD_V3_PLAN.md Phase L2 で L1 (常時稼働 / 知覚 / ルーティング) 層を
`L1Router` / `L1Observation` / `L1Decision` / `L1Escalation` として追加。
DASHBOARD_V3_PLAN.md Phase L3 で L1 → Capability 直接実行を担う
`L1Executor` / `L1ActionResult` を追加。

import 境界の不変条件 (instruction.md §8):
- `aegis_ai/intake/` は OpenHands SDK に直接依存しない。
- 既存 `LLMSettingsResolver` と `LLMRouter` 経由で LLM 呼び出しを行う。
- 結果として返る `IntakeResult` は AEGIS 内部表現のみで構成される。
"""
from __future__ import annotations

from aegis_ai.intake.classifier import IntakeClassifier  # noqa: F401
from aegis_ai.intake.deduplicator import IntakeDeduplicator  # noqa: F401
from aegis_ai.intake.l1_executor import L1Executor  # noqa: F401
from aegis_ai.intake.l1_models import (  # noqa: F401
    L1Action,
    L1ActionResult,
    L1ActionType,
    L1Decision,
    L1Escalation,
    L1Observation,
    RequiredIntelligence,
)
from aegis_ai.intake.l1_router import L1Router  # noqa: F401
from aegis_ai.intake.models import (  # noqa: F401
    IntakeDecision,
    IntakeResult,
    IntakeRoute,
    RoutingDecision,
)
from aegis_ai.intake.router import IntakeRouter  # noqa: F401

__all__ = [
    "IntakeClassifier",
    "IntakeDeduplicator",
    "IntakeResult",
    "IntakeDecision",
    "IntakeRoute",
    "RoutingDecision",
    "IntakeRouter",
    "L1Action",
    "L1ActionResult",
    "L1ActionType",
    "L1Decision",
    "L1Escalation",
    "L1Executor",
    "L1Observation",
    "L1Router",
    "RequiredIntelligence",
]
