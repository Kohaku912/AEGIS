"""Intake data models — Phase 4 (instruction.md §11, §36).

`IntakeResult` は intake classifier の出力型。`LLMResponse.context_meta` に
入れる運用も可能だが、AEGIS 側では **明示的な dataclass** として受け取って
後段の router / AutonomousLoop に渡す。

新規 dataclass を乱立させず、`IntakeDecision` / `IntakeRoute` / `RoutingDecision`
で最小セットに絞る。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IntakeDecision(str, Enum):
    """Intake の判定結果 (classifier 出力)."""

    REQUIRES_AGENT = "requires_agent"
    LOCAL_INTERPRET = "local_interpret"  # 既存 LLMTaskInterpreter 経路で十分
    DEFER = "defer"  # 後で再評価
    DUPLICATE = "duplicate"  # 既出


class IntakeRoute(str, Enum):
    """Intake router の最終経路 (DoD 用)."""

    SKIP = "skip"  # Agent 不要 (LLMTaskInterpreter 既存経路)
    DEFER = "defer"  # 後で再評価
    DUPLICATE = "duplicate"  # 既存と重複
    AGENT_DELEGATE = "agent_delegate"  # Agent 起動


@dataclass
class IntakeResult:
    """1 つの event に対する intake classifier 出力."""

    event_id: str  # もとの event の識別子 (deduplicator で使用)
    decision: IntakeDecision
    requires_agent_score: float = 0.0  # 0.0-1.0
    importance: float = 0.0  # 0.0-1.0 (memory gate 用)
    novelty: float = 1.0  # 0.0-1.0 (dedup 用、低いほど既出に近い)
    task_type: str = ""  # research_summary / code_generation / classification / ...
    capabilities: list[str] = field(default_factory=list)  # 必要な capability_id
    stop_conditions: list[str] = field(default_factory=list)
    reason: str = ""  # LLM の 1 行理由
    confidence: float = 0.0  # 0.0-1.0
    raw: dict[str, Any] = field(default_factory=dict)  # LLMResponse.context_meta


@dataclass
class RoutingDecision:
    """`IntakeRouter.route()` の戻り値. 既存経路への引き渡しに使う."""

    route: IntakeRoute
    intake_result: IntakeResult
    reason: str = ""

    @property
    def should_delegate_to_agent(self) -> bool:
        return self.route == IntakeRoute.AGENT_DELEGATE


__all__ = ["IntakeDecision", "IntakeRoute", "IntakeResult", "RoutingDecision"]
