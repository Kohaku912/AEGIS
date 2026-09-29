"""Autonomous Loop package.

AEGIS の自律実行レイヤ。

DASHBOARD_V3_PLAN.md Phase L4 で L2 (自律思考) 層を
`L2AutonomousMind` / `L2Context` / `L2Decision` として追加。
既存 `AutonomousLoop` には触らず、L2Mind は独立した薄いラッパーとして提供。

import 境界の不変条件 (instruction.md §8):
- `aegis_ai.autonomous.l2_mind` は OpenHands SDK に直接依存しない。
- LLM 呼び出しは既存 `LLMGateway.request(layer="L2", ...)` を必ず経由。
"""
from __future__ import annotations

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop  # noqa: F401
from aegis_ai.autonomous.l2_mind import L2AutonomousMind  # noqa: F401
from aegis_ai.autonomous.l2_models import (  # noqa: F401
    L2Action,
    L2ActionType,
    L2Context,
    L2Decision,
    L2Escalation,
)

__all__ = [
    "AutonomousLoop",
    "L2Action",
    "L2ActionType",
    "L2Context",
    "L2Decision",
    "L2AutonomousMind",
    "L2Escalation",
]
