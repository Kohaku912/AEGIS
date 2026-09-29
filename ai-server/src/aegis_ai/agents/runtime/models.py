"""Dataclasses for AEGIS ↔ Agent boundary.

These types are the *only* payloads that cross the AEGIS / Agent boundary.
OpenHands SDK の型は AEGIS 側に持ち込まない (instruction.md §5, §8).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aegis_ai.task.task_manager import TaskStatus  # 既存 enum を再利用 (instruction.md §5, §9)


# ---------------------------------------------------------------------------
# Task (input to AgentBackend.run)
# ---------------------------------------------------------------------------


@dataclass
class AgentTask:
    """AEGIS から Agent へ渡す 1 つの実行依頼.

    `goal` だけが本質。`context` / `tools` は LLM 駆動のオプション。
    """

    task_id: str
    goal: str
    context: dict[str, Any] = field(default_factory=dict)
    tools: list[str] = field(default_factory=list)  # canonical capability_id のリスト
    profile: str = "general"  # Phase 5 で backend 選択に使用
    max_steps: int = 10
    timeout_seconds: int = 600
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Progress callback payload
# ---------------------------------------------------------------------------


@dataclass
class AgentProgress:
    """ストリーミング進捗通知 (`AgentBackend.run(on_progress=)` 経由)."""

    task_id: str
    stage: str  # "started" | "reasoning" | "tool_call" | "observation" | "finished"
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp_ms: int = 0


# ---------------------------------------------------------------------------
# Result components
# ---------------------------------------------------------------------------


@dataclass
class AgentAction:
    """1 つの capability 呼び出し (= AEGIS 側での 1 step に相当).

    instruction.md §5 仕様. `PlanStep.result` へマップされる.
    """

    step_id: str  # TaskPlan.PlanStep.step_id と一致
    capability_id: str  # canonical: server.app.action
    arguments: dict[str, Any]  # 実行時引数 (secrets は redact 済み)
    arguments_hash: str  # ApprovalManager.compute_args_hash() と同じ SHA-256
    result: Any | None = None
    error: str = ""
    duration_ms: int = 0


@dataclass
class Artifact:
    """Agent が生成・編集した成果物."""

    kind: str  # "file" | "diff" | "log" | "url" | "image" | "dataset"
    uri: str  # 取得元 (path, s3://, https://...)
    summary: str = ""


@dataclass
class AgentError:
    """Agent 実行時のエラー."""

    code: str  # "timeout" | "policy_denied" | "approval_rejected" | ...
    message: str
    recoverable: bool = True


@dataclass
class MemoryCandidate:
    """Agent が『覚えてほしい』と言ってきた候補. 最終保存は AEGIS 側 (§31)."""

    type: str  # MemoryManager の type に対応 (episodic/semantic/skill/...)
    content: str
    confidence: float
    importance: float
    tags: list[str] = field(default_factory=list)


@dataclass
class UsageMetrics:
    """LLM 呼び出しコスト・トークン使用量."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_hit_tokens: int = 0
    cost_usd: float = 0.0
    model: str = ""
    provider: str = ""
    tool_call_count: int = 0
    duration_ms: int = 0


@dataclass
class AgentResult:
    """AEGIS ↔ Agent 境界の正規化された最終結果.

    instruction.md §5 仕様. `TaskManager.complete_task(result_summary=)` および
    `PlanStep.result` にそのまま流し込める形.
    """

    task_id: str
    status: TaskStatus  # 既存 TaskStatus を流用
    summary: str  # TaskManager.complete_task(result_summary=) に渡す 1 行サマリ
    actions: list[AgentAction] = field(default_factory=list)  # → PlanStep.result
    artifacts: list[Artifact] = field(default_factory=list)  # → Memory 保存候補
    tool_calls: list[AgentAction] = field(default_factory=list)  # 監査用
    errors: list[AgentError] = field(default_factory=list)
    approvals_requested: list[str] = field(default_factory=list)  # approval_id のみ
    suggested_memory: list[MemoryCandidate] = field(default_factory=list)
    suggested_follow_ups: list[str] = field(default_factory=list)  # 自然文
    usage: UsageMetrics = field(default_factory=UsageMetrics)


__all__ = [
    "AgentTask",
    "AgentProgress",
    "AgentAction",
    "Artifact",
    "AgentError",
    "MemoryCandidate",
    "UsageMetrics",
    "AgentResult",
]
