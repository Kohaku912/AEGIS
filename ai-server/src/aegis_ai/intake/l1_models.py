"""L1 Router data models — DASHBOARD_V3_PLAN.md Phase L2.

instruction.md v3 で定義された L1 (常時稼働 / 知覚 / ルーティング) 層の
構造化出力データモデル。

- L1Observation: event の意味理解 / 価値評価 / 重要度 / 必要知能量
- L1Decision:   L1 が取る行動 (escalate / capability / observe / ignore)
- L1Escalation: L2 への escalation (reason + problem + context)
- L1Action:     L1 が実行する行動 (capability / observe / escalate)
- RequiredIntelligence: enum (low / medium / high)
- L1ActionType: enum (escalate / capability / observe / ignore / noop)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RequiredIntelligence(str, Enum):
    """L1 が推定する「必要知能量」.

    - LOW: 簡単なタスク (Capability 直接実行で足りる)
    - MEDIUM: 中程度の判断 (L1 で対応可)
    - HIGH: 深い判断が必要 (L2 escalation 必須)
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class L1ActionType(str, Enum):
    """L1 Decision の行動タイプ.

    - ESCALATE: L2 へ escalation
    - CAPABILITY: Capability を直接実行 (L1 で完結)
    - OBSERVE: 観測のみ (後で再評価)
    - IGNORE: 無視
    - NOOP: 何もしない
    """

    ESCALATE = "escalate"
    CAPABILITY = "capability"
    OBSERVE = "observe"
    IGNORE = "ignore"
    NOOP = "noop"


@dataclass
class L1Observation:
    """L1 が event を観測した結果.

    Attributes:
        event_id: 観測対象 event の ID
        meaning: event の意味理解 (1 行)
        value: 価値評価 (0.0-1.0、AEGIS にとってどのくらい重要か)
        priority: 優先度 (0.0-1.0)
        required_intelligence: 必要知能量
        confidence: L1 の confidence (0.0-1.0)
        raw: LLM 出力の生 dict
    """

    event_id: str
    meaning: str
    value: float = 0.0
    priority: float = 0.0
    required_intelligence: RequiredIntelligence = RequiredIntelligence.LOW
    confidence: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class L1Action:
    """L1 が実行する行動.

    Attributes:
        type: 行動タイプ
        capability_id: type == CAPABILITY のときの capability_id
        args: capability 呼び出し時の引数
        reason: 行動理由 (1 行)
    """

    type: L1ActionType
    capability_id: str = ""
    args: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class L1Decision:
    """L1 が observation から下した判断.

    Attributes:
        event_id: 対象 event の ID
        action: 取る行動
        reasoning: 1 行理由
        observation: 元の observation (参照)
    """

    event_id: str
    action: L1Action
    reasoning: str = ""
    observation: L1Observation | None = None


@dataclass
class L1Escalation:
    """L1 から L2 への escalation.

    Attributes:
        event_id: 元の event ID
        reason: escalation 理由
        problem: L2 / L3 に渡したい問題 (1-2 文)
        context: 関連 context (events / observations)
        required_intelligence: 必要知能量
    """

    event_id: str
    reason: str
    problem: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    required_intelligence: RequiredIntelligence = RequiredIntelligence.HIGH

    def to_payload(self) -> dict[str, Any]:
        """EventBus publish 用 payload."""
        return {
            "event_id": self.event_id,
            "reason": self.reason,
            "problem": self.problem,
            "context": self.context,
            "required_intelligence": self.required_intelligence.value,
        }


@dataclass
class L1ActionResult:
    """L1 からの Capability 実行結果 — DASHBOARD_V3_PLAN.md Phase L3.

    `L1Executor.execute()` の戻り値。EventBus に `l1.capability.completed`
    として publish される (Phase L3 で利用)。

    Attributes:
        capability_id: 実行した capability ID
        event_id: 元の event ID
        success: 実行が成功したか
        result: capability 実行結果 (成功時)
        error: エラーメッセージ (失敗時)
        risk_level: 実行時 risk_level (catalog より)
        duration_ms: 実行時間 (ms)
        bypassed_approval: L1 直接実行なので approval を bypass したか
            (Phase L3 では risk="low" のみ呼ぶので本来 True。
             既存 approval flow に乗せる場合 False。)
    """

    capability_id: str
    event_id: str = ""
    success: bool = False
    result: dict[str, Any] | None = None
    error: str | None = None
    risk_level: str = "low"
    duration_ms: int = 0
    bypassed_approval: bool = True

    def to_payload(self) -> dict[str, Any]:
        """EventBus publish 用 payload."""
        return {
            "capability_id": self.capability_id,
            "event_id": self.event_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "risk_level": self.risk_level,
            "duration_ms": self.duration_ms,
            "bypassed_approval": self.bypassed_approval,
        }


__all__ = [
    "L1Action",
    "L1ActionResult",
    "L1ActionType",
    "L1Decision",
    "L1Escalation",
    "L1Observation",
    "RequiredIntelligence",
]
