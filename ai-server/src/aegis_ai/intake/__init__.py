"""Intake — the L1 (always-on) layer: perception → routing → direct execution.

`L1Router` / `L1Observation` / `L1Decision` / `L1Escalation` (DASHBOARD_V3_PLAN.md
Phase L2) route every event with a small LLM instead of handing it straight to the
Agent; `L1Executor` / `L1ActionResult` (Phase L3) run a Capability directly when the
decision says so.

Phase 4's v1 intake path — `IntakeRouter` / `IntakeClassifier` / `IntakeDeduplicator`
and the data models in `intake/models.py` — was **deleted 2026-10-08**
(DELEGATION.md §4 item 47). `L1Router` replaced `IntakeRouter` on the live path
(`runtime.py` builds `L1Router(llm_gateway=...)`), so the v1 classes were constructed
nowhere in `src/` and the v1 data models had no live importer; the re-exports below
were the only thing keeping the names alive. Their absence is pinned by
`ai-server/tests/test_intake_v1_surface_is_gone.py`.

import 境界の不変条件 (instruction.md §8):
- `aegis_ai/intake/` は OpenHands SDK に直接依存しない。
- 既存 `LLMSettingsResolver` と `LLMRouter` 経由で LLM 呼び出しを行う。
- 結果として返る `L1Decision` は AEGIS 内部表現のみで構成される。
"""
from __future__ import annotations

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

__all__ = [
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
