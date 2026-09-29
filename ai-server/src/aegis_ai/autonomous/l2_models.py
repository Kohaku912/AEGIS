"""L2 Autonomous Mind data models — DASHBOARD_V3_PLAN.md Phase L4.

instruction.md v3 で定義された L2 (自律思考) 層の構造化出力データモデル。

- L2Context:  L2 思考のための統合 context (world state + memory + desire + task + l1)
- L2ActionType: L2 が取り得る行動 (task / escalate_l3 / observe / noop)
- L2Action:   行動の実体 (TASK のとき task_spec / ESCALATE_L3 のとき l3_problem)
- L2Decision: L2 が L2Context から下した判断
- L2Escalation: L2 → L3 への escalation (Phase L5 で利用)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class L2ActionType(str, Enum):
    """L2 Decision の行動タイプ.

    - TASK: 具体的なタスクを生成 (TaskManager に登録)
    - ESCALATE_L3: L3 Deep Reasoner へ escalation (Phase L5)
    - OBSERVE: 観測のみ (後で再評価)
    - NOOP: 何もしない (desire 充足済 / 抑制期間)
    """

    TASK = "task"
    ESCALATE_L3 = "escalate_l3"
    OBSERVE = "observe"
    NOOP = "noop"


@dataclass
class L2Context:
    """L2 思考のための統合 context.

    Attributes:
        world_state: システム状態 (active task 数 / desire 概要 / 時刻など)
        memory_summary: 重要 memory の要約 (短文)
        desire_snapshot: 3 desire の現スナップショット (user_support / social / growth)
        task_state: アクティブ task の一覧
        l1_summaries: 直近 L1 observation の要約 (escalations 含む)
        pending_obligations: ユーザ向け未処理 obligation
        recent_failures: 直近の失敗履歴
        raw: LLM 入力前の元 context
    """

    world_state: dict[str, Any] = field(default_factory=dict)
    memory_summary: str = ""
    desire_snapshot: dict[str, float] = field(default_factory=dict)
    task_state: list[dict[str, Any]] = field(default_factory=list)
    l1_summaries: list[dict[str, Any]] = field(default_factory=list)
    pending_obligations: list[dict[str, Any]] = field(default_factory=list)
    recent_failures: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_prompt(self) -> str:
        """LLM 入力用の短文プロンプトへ整形."""
        def _short(value: Any, limit: int = 140) -> str:
            text = str(value or "").strip()
            if len(text) <= limit:
                return text
            return text[: max(0, limit - 3)] + "..."

        lines: list[str] = []
        if self.desire_snapshot:
            desire_str = ", ".join(
                f"{k}={v:.1f}" for k, v in sorted(self.desire_snapshot.items())
            )
            lines.append(f"Desires: {desire_str}")
        if self.world_state:
            ws_keys = sorted(self.world_state.keys())[:8]
            ws_str = ", ".join(f"{k}={self.world_state[k]}" for k in ws_keys)
            lines.append(f"World: {ws_str}")
        if self.memory_summary:
            lines.append(f"Memory: {self.memory_summary[:300]}")
        if self.task_state:
            lines.append(f"Active tasks: {len(self.task_state)}")
            for item in self.task_state[:3]:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    "- task: "
                    + _short(
                        item.get("title")
                        or item.get("summary")
                        or item.get("description")
                        or item.get("task_id")
                        or item.get("id")
                    )
                )
        if self.l1_summaries:
            lines.append(f"L1 summaries: {len(self.l1_summaries)}")
            for item in self.l1_summaries[:3]:
                if not isinstance(item, dict):
                    continue
                bucket = str(item.get("summary_bucket") or "background")
                action_type = str(item.get("action_type") or "")
                meaning = _short(
                    item.get("meaning") or item.get("observed_action") or item.get("possible_intent"),
                    limit=140,
                )
                lines.append(
                    f"- l1[{bucket}/{action_type or 'observe'}]: {meaning}"
                )
        if self.pending_obligations:
            lines.append(f"Pending obligations: {len(self.pending_obligations)}")
            for item in self.pending_obligations[:3]:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    "- obligation: "
                    + _short(item.get("summary") or item.get("title") or item.get("content"))
                )
        if self.recent_failures:
            lines.append(f"Recent failures: {len(self.recent_failures)}")
            for item in self.recent_failures[:3]:
                lines.append(f"- failure: {_short(item)}")
        return "\n".join(lines) or "(empty context)"


@dataclass
class L2Action:
    """L2 が実行する行動.

    Attributes:
        type: 行動タイプ
        task_spec: TASK のときの task 仕様
        l3_problem: ESCALATE_L3 のときの L3 問題定義
        reason: 行動理由 (1 行)
    """

    type: L2ActionType
    task_spec: dict[str, Any] = field(default_factory=dict)
    l3_problem: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class L2Decision:
    """L2 が L2Context から下した判断.

    Attributes:
        action: 取る行動
        plan: 行動の具体的プラン (1-3 文)
        confidence: L2 の confidence (0.0-1.0)
        escalate_to_l3: L3 へ escalation するか (Phase L5 で利用)
        context: 元の L2Context への参照
    """

    action: L2Action
    plan: str = ""
    confidence: float = 0.0
    escalate_to_l3: bool = False
    context: L2Context | None = None

    def to_payload(self) -> dict[str, Any]:
        """EventBus publish 用 payload."""
        return {
            "action_type": self.action.type.value,
            "task_spec": self.action.task_spec,
            "l3_problem": self.action.l3_problem,
            "reason": self.action.reason,
            "plan": self.plan,
            "confidence": self.confidence,
            "escalate_to_l3": self.escalate_to_l3,
        }


@dataclass
class L2Escalation:
    """L2 → L3 escalation — DASHBOARD_V3_PLAN.md Phase L4 / L5.

    `L2Decision.escalate_to_l3` が True のときに生成され、Phase L5 で
    `L3Reasoner` に渡される。Phase L4 では構造体のみ提供し、実フローは
    Phase L5 で組み込む。

    Attributes:
        problem: L3 に渡したい問題 (1-2 文)
        context_summary: L2 context の要約
        l1_observations: 関連する L1 observation
        reason: escalation 理由
    """

    problem: str
    context_summary: str = ""
    l1_observations: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "problem": self.problem,
            "context_summary": self.context_summary,
            "l1_observations": self.l1_observations,
            "reason": self.reason,
        }


__all__ = [
    "L2Action",
    "L2ActionType",
    "L2Context",
    "L2Decision",
    "L2Escalation",
]
