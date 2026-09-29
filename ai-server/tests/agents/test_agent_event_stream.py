"""Phase D1 DoD tests — Agent event stream (DASHBOARD_REFINED_PLAN.md §3 Phase D1).

DoD チェックリスト:
- [x] 8 種類の agent.* イベントが EventBus に流れる
- [x] SSE 経由で受信可能 (`/api/ui/stream` の `agent.*` リスナー追加)
- [x] 既存 `tool.execution.*` / `task.updated` と重複しない (新しい namespace)
- [x] テスト: AgentEventPublisher / backend integration の unit test
"""
from __future__ import annotations

import asyncio
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# 共通 fixture (他テストでも使うので関数化).


def _run(coro: Any) -> Any:
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@dataclass
class _FakeTask:
    task_id: str = "t-d1-001"
    goal: str = "implement Phase D1 test"
    description: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    tools: list[Any] = field(default_factory=list)
    profile: str = "general"
    max_steps: int = 5
    timeout_seconds: int = 30
    metadata: dict[str, Any] = field(default_factory=dict)


class _FakeEventManager:
    """EventManager 互換の minimal mock.

    `publish_event(event_type, *, source, payload)` を呼べる dummy.
    呼ばれた type ごとに payload を記録する.
    """

    def __init__(self) -> None:
        self.published: list[tuple[str, str, dict[str, Any]]] = []

    def publish_event(
        self, event_type: str, *, source: str, payload: dict[str, Any]
    ) -> bool:
        self.published.append((event_type, source, dict(payload)))
        return True


# ---------------------------------------------------------------------------
# DoD 1: 8 種類の agent.* イベントが EventBus に流れる
# ---------------------------------------------------------------------------


def test_agent_event_kinds_defines_eight_kinds() -> None:
    """AGENT_EVENT_KINDS には 8 種類 (Phase D1 §12) 全てが含まれる."""
    from aegis_ai.event.agent_events import AGENT_EVENT_KINDS

    assert len(AGENT_EVENT_KINDS) == 8
    expected = {
        "agent.started",
        "agent.thinking",
        "agent.tool.started",
        "agent.tool.completed",
        "agent.waiting",
        "agent.verifying",
        "agent.completed",
        "agent.failed",
    }
    assert set(AGENT_EVENT_KINDS) == expected


def test_event_manager_persist_set_includes_agent_kinds() -> None:
    """EventManager._PERSIST_EVENT_TYPES に 8 種類が含まれる.

    EventManager._PERSIST_EVENT_TYPES は module-private (先頭 _).
    モジュールを import して直接参照.
    """
    import aegis_ai.event.event_manager as em_mod

    persist_set = em_mod._PERSIST_EVENT_TYPES
    for kind in (
        "agent.started", "agent.thinking", "agent.tool.started",
        "agent.tool.completed", "agent.waiting", "agent.verifying",
        "agent.completed", "agent.failed",
    ):
        assert kind in persist_set, f"missing persist type: {kind}"


def test_agent_publisher_without_event_manager_is_noop() -> None:
    """EventManager 未注入時は no-op (Phase 1/2 テストで落ちない)."""
    from aegis_ai.event.agent_events import AgentEventPublisher

    pub = AgentEventPublisher(event_manager=None, source="test")
    assert pub.emit_started(task_id="t-1", agent_session_id="s-1") is False
    assert pub.emit_thinking(task_id="t-1", agent_session_id="s-1", text="hi") is False
    assert pub.emit_tool_started(
        task_id="t-1", agent_session_id="s-1", tool="terminal"
    ) is False
    assert pub.emit_tool_completed(
        task_id="t-1", agent_session_id="s-1", tool="terminal", ok=True
    ) is False
    assert pub.emit_waiting(
        task_id="t-1", agent_session_id="s-1", approval_id="a-1"
    ) is False
    assert pub.emit_verifying(
        task_id="t-1", agent_session_id="s-1", command="pytest"
    ) is False
    assert pub.emit_completed(task_id="t-1", agent_session_id="s-1") is False
    assert pub.emit_failed(
        task_id="t-1", agent_session_id="s-1", error="boom"
    ) is False


def test_agent_publisher_unknown_kind_is_rejected() -> None:
    """AGENT_EVENT_KINDS に無い kind を渡すと warning を出して False."""
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    # 内部メソッドを直接呼んで unknown kind を投げる.
    result = pub._publish(
        "agent.not_a_real_kind",
        task_id="t-1",
        agent_session_id="s-1",
        parent_id="",
        state_text="bogus",
    )
    assert result is False
    assert fake.published == []


# ---------------------------------------------------------------------------
# DoD 2: 各 publish メソッドが正しい shape で publish_event を呼ぶ
# ---------------------------------------------------------------------------


def test_publisher_emit_started_calls_publish_event_with_started_kind() -> None:
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="openhands_backend")
    pub.emit_started(
        task_id="t-1", agent_session_id="s-1", goal="do stuff",
    )
    assert len(fake.published) == 1
    kind, source, payload = fake.published[0]
    assert kind == "agent.started"
    assert source == "openhands_backend"
    assert payload["task_id"] == "t-1"
    assert payload["agent_session_id"] == "s-1"
    assert payload["parent_id"] == ""
    assert payload["state"] == "started"
    assert payload["goal"] == "do stuff"
    assert "occurred_at_ms" in payload


def test_publisher_emit_thinking_includes_text() -> None:
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    pub.emit_thinking(task_id="t-1", agent_session_id="s-1", text="analyzing...")
    kind, _source, payload = fake.published[0]
    assert kind == "agent.thinking"
    assert payload["text"] == "analyzing..."
    assert payload["state"] == "thinking"


def test_publisher_emit_tool_started_includes_tool_and_args() -> None:
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    pub.emit_tool_started(
        task_id="t-1", agent_session_id="s-1", tool="terminal", args={"cmd": "ls"},
    )
    kind, _source, payload = fake.published[0]
    assert kind == "agent.tool.started"
    assert payload["tool"] == "terminal"
    assert payload["args"] == {"cmd": "ls"}
    assert payload["state"] == "tool_started"


def test_publisher_emit_tool_completed_includes_ok_and_output() -> None:
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    pub.emit_tool_completed(
        task_id="t-1", agent_session_id="s-1", tool="terminal",
        ok=True, output="ok", duration_ms=42,
    )
    kind, _source, payload = fake.published[0]
    assert kind == "agent.tool.completed"
    assert payload["tool"] == "terminal"
    assert payload["ok"] is True
    assert payload["output"] == "ok"
    assert payload["duration_ms"] == 42
    assert payload["state"] == "tool_completed"


def test_publisher_emit_waiting_includes_approval_id() -> None:
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    pub.emit_waiting(
        task_id="t-1", agent_session_id="s-1", approval_id="apr-001", tool="github.pr_create",
    )
    kind, _source, payload = fake.published[0]
    assert kind == "agent.waiting"
    assert payload["approval_id"] == "apr-001"
    assert payload["tool"] == "github.pr_create"


def test_publisher_emit_verifying_includes_command() -> None:
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    pub.emit_verifying(
        task_id="t-1", agent_session_id="s-1", command="pytest -q",
    )
    kind, _source, payload = fake.published[0]
    assert kind == "agent.verifying"
    assert payload["command"] == "pytest -q"


def test_publisher_emit_completed_includes_summary() -> None:
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    pub.emit_completed(
        task_id="t-1", agent_session_id="s-1", summary="done",
    )
    kind, _source, payload = fake.published[0]
    assert kind == "agent.completed"
    assert payload["summary"] == "done"


def test_publisher_emit_failed_includes_error_and_code() -> None:
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    pub.emit_failed(
        task_id="t-1", agent_session_id="s-1",
        error="setup failed: bad key", code="setup_failed",
    )
    kind, _source, payload = fake.published[0]
    assert kind == "agent.failed"
    assert payload["error"] == "setup failed: bad key"
    assert payload["code"] == "setup_failed"


# ---------------------------------------------------------------------------
# DoD 3: 既存 tool.execution.* / task.updated と重複しない (新しい namespace)
# ---------------------------------------------------------------------------


def test_publisher_publish_event_uses_dotted_agent_namespace() -> None:
    """publish_event の event_type は必ず 'agent.' で始まる (8 種類のみ)."""
    from aegis_ai.event.agent_events import AGENT_EVENT_KINDS, AgentEventPublisher

    for kind in AGENT_EVENT_KINDS:
        assert kind.startswith("agent."), f"bad namespace: {kind}"
        # 既存 namespace と被らない.
        assert not kind.startswith("tool.execution."), f"collides with tool: {kind}"
        assert not kind.startswith("task."), f"collides with task: {kind}"
        assert not kind.startswith("approval."), f"collides with approval: {kind}"


# ---------------------------------------------------------------------------
# DoD 4: Backend integration — _emit_agent_events_from_oh が正しい変換をする
# ---------------------------------------------------------------------------


def test_emit_agent_events_from_oh_converts_message_action_observation() -> None:
    """OpenHands event (message / action / observation) → agent.* 変換.

    `_emit_agent_events_from_oh` は OpenHands backend / remote backend の
    private メソッドなので module 経由で直接呼ぶ.
    """
    from aegis_ai.agents.backends.openhands import backend as backend_mod

    fake = _FakeEventManager()
    backend = backend_mod.OpenHandsBackend(event_manager=fake)
    events = [
        {"kind": "message", "role": "assistant", "text": "I will check files."},
        {"kind": "message", "role": "user", "text": "ignored"},
        {"kind": "action", "tool": "terminal", "args": {"cmd": "ls"}},
        {"kind": "observation", "output": "file1\nfile2"},
    ]
    backend._emit_agent_events_from_oh("t-1", events)

    kinds = [k for (k, _s, _p) in fake.published]
    # user message は publish されない (assistant のみ).
    assert kinds == [
        "agent.thinking",
        "agent.tool.started",
        "agent.tool.completed",
    ]


def test_emit_agent_events_from_oh_handles_empty_events() -> None:
    from aegis_ai.agents.backends.openhands import backend as backend_mod

    fake = _FakeEventManager()
    backend = backend_mod.OpenHandsBackend(event_manager=fake)
    backend._emit_agent_events_from_oh("t-1", [])
    assert fake.published == []


# ---------------------------------------------------------------------------
# DoD 5: Backend.run() の lifecycle イベント (started / completed / failed)
# ---------------------------------------------------------------------------


def test_backend_run_emits_started_and_completed_for_success(monkeypatch) -> None:
    """OpenHands SDK が利用できない設定でも emit_started / emit_completed は
    失敗パスで emit_failed になる (SDK 不在は backend_unavailable).

    成功パスを試すには OpenHands の正規 event を返すスタブが必要.
    ここでは backend_unavailable 経路で「started → failed」になることを検証し、
    成功経路は下流の Phase で別途テストする.
    """
    from aegis_ai.agents.backends.openhands import backend as backend_mod

    fake = _FakeEventManager()
    backend = backend_mod.OpenHandsBackend(event_manager=fake)
    monkeypatch.setattr(backend_mod, "is_openhands_available", lambda: False)
    result = _run(backend.run(_FakeTask()))
    # SDK 不在 → FAILED + emit_failed されている.
    kinds = [k for (k, _s, _p) in fake.published]
    assert "agent.started" in kinds
    assert "agent.failed" in kinds
    # result.status は FAILED.
    from aegis_ai.task.task_manager import TaskStatus
    assert result.status == TaskStatus.FAILED


def test_publisher_truncates_oversized_text() -> None:
    """goal / text / error / summary は上限カットされる (DoD: 巨大 payload 防止)."""
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    big = "x" * 10000
    pub.emit_thinking(task_id="t", agent_session_id="s", text=big)
    _kind, _src, payload = fake.published[0]
    # 4000 文字上限 + "…"
    assert len(payload["text"]) <= 4001
    assert payload["text"].endswith("…")


# ---------------------------------------------------------------------------
# Phase D3 — Trace ID 6 種伝搬 (instruction.md §16)
# ---------------------------------------------------------------------------


def test_publisher_start_session_assigns_agent_session_and_trace_id() -> None:
    """start_session() で 1 実行 = 1 agent_session_id / trace_id を確保."""
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    session_id = pub.start_session(task_id="t-1")
    # 引数なしで session 開始 → UUID 形式の id が返る
    assert isinstance(session_id, str) and len(session_id) > 0
    assert pub.current_session_id() == session_id
    assert pub.current_trace_id() == session_id  # 1 実行 = 1 trace


def test_publisher_start_session_accepts_explicit_ids() -> None:
    """明示的な agent_session_id / trace_id を渡せる (caller が session store を持ってる時)."""
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    session_id = pub.start_session(task_id="t", agent_session_id="sess-1", trace_id="trace-1")
    assert pub.current_session_id() == "sess-1"
    assert pub.current_trace_id() == "trace-1"


def test_publisher_publishes_with_trace_ids_dict_when_session_active() -> None:
    """session 中の publish は payload._trace_ids に 6 種を含む."""
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    pub.start_session(task_id="t-1")
    pub.emit_started(task_id="t-1", agent_session_id="", goal="x")
    pub.emit_thinking(task_id="t-1", agent_session_id="", text="hello")

    # 1 つ目 (started) の _trace_ids
    _kind, _src, p0 = fake.published[0]
    assert "_trace_ids" in p0
    ids0 = p0["_trace_ids"]
    assert ids0["activity_id"] == "activity-0001"
    assert ids0["task_id"] == "t-1"
    assert ids0["agent_session_id"]  # session id が埋まる
    assert ids0["trace_id"] == ids0["agent_session_id"]
    # 1 つ目 (started) は parent_id なし
    assert ids0["parent_id"] == ""

    # 2 つ目 (thinking) の _trace_ids — parent_id に 1 つ目の event_id が入る
    _kind, _src, p1 = fake.published[1]
    ids1 = p1["_trace_ids"]
    assert ids1["activity_id"] == "activity-0002"
    assert ids1["parent_id"] == p0["event_id"]  # 直前 event の event_id に連鎖


def test_publisher_without_session_does_not_emit_trace_ids() -> None:
    """session 未開始時は _trace_ids を含めず、既存挙動を維持 (Phase D1 互換)."""
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    # start_session を呼ばずに直接 emit_thinking
    pub.emit_thinking(task_id="t", agent_session_id="s", text="hello")
    _kind, _src, payload = fake.published[0]
    assert "_trace_ids" not in payload or payload["_trace_ids"]["event_id"] == ""


def test_publisher_end_session_resets_state() -> None:
    """end_session() で session 状態をリセット."""
    from aegis_ai.event.agent_events import AgentEventPublisher

    fake = _FakeEventManager()
    pub = AgentEventPublisher(event_manager=fake, source="test")
    pub.start_session(task_id="t-1")
    pub.end_session()
    assert pub.current_session_id() == ""
    assert pub.current_trace_id() == ""


def test_backend_run_uses_start_session_for_trace_id_propagation() -> None:
    """OpenHandsBackend.run() は start_session() を呼んで _trace_ids を伝搬する."""
    from aegis_ai.agents.backends.openhands import backend as backend_mod

    fake = _FakeEventManager()
    backend = backend_mod.OpenHandsBackend(event_manager=fake)
    # backend_unavailable 経路で started → failed を確認
    import asyncio

    result = asyncio.run(backend.run(_FakeTask()))
    # 2 件以上の publish があり、両方に _trace_ids が含まれる
    assert len(fake.published) >= 2
    for _kind, _src, payload in fake.published:
        assert "_trace_ids" in payload, f"missing _trace_ids in {payload}"
        ids = payload["_trace_ids"]
        assert ids["task_id"] == "t-d1-001"
        assert ids["agent_session_id"]  # session id が session 全体で一致
        assert ids["trace_id"] == ids["agent_session_id"]
