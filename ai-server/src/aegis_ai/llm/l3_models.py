"""L3 Deep Reasoner data models — DASHBOARD_V3_PLAN.md Phase L5.

instruction.md v3 で定義された L3 (深層推論) 層の構造化入出力データモデル。

- L3Problem:  L2 から渡される問題定義 (problem / context / l1_observations / constraints)
- L3Plan:     L3 が生成する推論プラン (steps / assumptions / risks / recommendations)
- L3Result:   L3 の最終結果 (plan / confidence / reasoning_summary)
- L3Action:   L3 が L2 に対して推奨する行動 (TASK / OBSERVE / ABORT)
- L3Step:     プラン内の個別ステップ (capability_id / args / read_only / reason)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class L3Action(str, Enum):
    """L3 → L2 推奨行動.

    - TASK: 具体的タスクを実行 (L2 経由で Capability 起動)
    - OBSERVE: 更に情報を集める (L1 を追加 escalation)
    - ABORT: 中止 (危険 / 解決不能)
    """

    TASK = "task"
    OBSERVE = "observe"
    ABORT = "abort"


@dataclass
class L3Step:
    """L3 プラン内の 1 ステップ.

    Attributes:
        order: ステップの順序
        capability_id: 実行する capability (None の場合は情報収取のみ)
        args: capability 引数
        read_only: 読み取り系 capability か (Phase L5 ルール)
        reason: ステップの理由 (1 行)
        depends_on: 依存する先行ステップの order 一覧
    """

    order: int
    capability_id: str = ""
    args: dict[str, Any] = field(default_factory=dict)
    read_only: bool = True
    reason: str = ""
    depends_on: list[int] = field(default_factory=list)


@dataclass
class L3Problem:
    """L2 → L3 の問題定義.

    Attributes:
        problem: 解決したい問題 (1-2 文)
        context: 関連 context
        l1_observations: 関連する L1 observation
        constraints: 制約条件 (cost / time / safety)
        reason: escalation 理由
    """

    problem: str
    context: dict[str, Any] = field(default_factory=dict)
    l1_observations: list[dict[str, Any]] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    reason: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "problem": self.problem,
            "context": self.context,
            "l1_observations": self.l1_observations,
            "constraints": self.constraints,
            "reason": self.reason,
        }


@dataclass
class L3Plan:
    """L3 が生成する推論プラン.

    Attributes:
        steps: 実行ステップ (順序付き)
        assumptions: プランの前提
        risks: 想定リスク
        recommendations: 推奨事項
        read_only_plan: プラン全体が読み取り系のみで構成されるか
    """

    steps: list[L3Step] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def read_only_plan(self) -> bool:
        """全ステップが読み取り系のみで構成されるか (Phase L5 ルール)."""
        return all(step.read_only for step in self.steps)

    def to_payload(self) -> dict[str, Any]:
        return {
            "steps": [
                {
                    "order": s.order,
                    "capability_id": s.capability_id,
                    "args": s.args,
                    "read_only": s.read_only,
                    "reason": s.reason,
                    "depends_on": s.depends_on,
                }
                for s in self.steps
            ],
            "assumptions": list(self.assumptions),
            "risks": list(self.risks),
            "recommendations": list(self.recommendations),
            "read_only_plan": self.read_only_plan,
        }


@dataclass
class L3Result:
    """L3 の最終結果 — DASHBOARD_V3_PLAN.md Phase L5.

    Attributes:
        problem: 元の L3Problem (参照)
        plan: L3 が生成したプラン
        recommended_action: L3 → L2 推奨行動
        confidence: 0.0-1.0
        reasoning_summary: 推論要約 (1-3 文)
        raw: LLM 生出力
    """

    problem: L3Problem
    plan: L3Plan
    recommended_action: L3Action = L3Action.TASK
    confidence: float = 0.0
    reasoning_summary: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "problem": self.problem.to_payload(),
            "plan": self.plan.to_payload(),
            "recommended_action": self.recommended_action.value,
            "confidence": self.confidence,
            "reasoning_summary": self.reasoning_summary,
        }


__all__ = [
    "L3Action",
    "L3Plan",
    "L3Problem",
    "L3Result",
    "L3Step",
]
