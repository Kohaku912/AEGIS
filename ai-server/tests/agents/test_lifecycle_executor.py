"""Phase 3 DoD tests — AgentTask ↔ AEGIS Task 双方向変換 (instruction.md §36).

DoD チェックリスト (§36):
- [x] AEGIS の TaskStatus 9 状態 と Agent 状態を相互変換できる
- [x] `TaskManager.complete_task_with_agent_result()` で AgentResult を埋め込める
- [x] `TaskExecutionEngine._execute_step()` が `ai-server.agent.*` capability を
      AgentBackend にルーティングする
- [x] `lifecycle.py` / `executor.py` は OpenHands SDK を import しない
      (§6 import 境界ルール) → 静的検査
"""
from __future__ import annotations

import asyncio
import inspect
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest


def _run(coro: Any) -> Any:
    # Python 3.12+ requires creating a new event loop when none exists.
    # Same pattern as test_agent_runtime.py / test_openhands_backend.py.
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# PlanStep / TaskPlan の最小スタブ (テストで完結させるため).
# ---------------------------------------------------------------------------


@dataclass
class _StubPlan:
    """`build_agent_task()` が参照する user_goal / plan_id のスタブ."""

    plan_id: str = "plan-test"
    user_goal: str = "fallback plan goal"


# ---------------------------------------------------------------------------
# TaskStatus ↔ backend status 変換
# ---------------------------------------------------------------------------


def test_backend_status_to_task_all_known_statuses() -> None:
    """`backend_status_to_task()`: 全状態を正しく変換する."""
    from aegis_ai.agents.runtime.lifecycle import backend_status_to_task
    from aegis_ai.task.task_manager import TaskStatus

    pairs = {
        "created": TaskStatus.CREATED,
        "planning": TaskStatus.PLANNING,
        "running": TaskStatus.RUNNING,
        # approval is no longer a constraint: a backend asking for a decision
        # is mapped to PAUSED (surfaced as REQUIRES_OBSERVATION).
        "waiting_approval": TaskStatus.PAUSED,
        "paused": TaskStatus.PAUSED,
        "completed": TaskStatus.COMPLETED,
        "failed": TaskStatus.FAILED,
        "cancelled": TaskStatus.CANCELLED,
        "expired": TaskStatus.EXPIRED,
    }
    for s, expected in pairs.items():
        assert backend_status_to_task(s) == expected


def test_backend_status_to_task_accepts_enum() -> None:
    """TaskStatus enum を渡すとそのまま返る (idempotent)."""
    from aegis_ai.agents.runtime.lifecycle import backend_status_to_task
    from aegis_ai.task.task_manager import TaskStatus

    assert backend_status_to_task(TaskStatus.RUNNING) == TaskStatus.RUNNING
    assert backend_status_to_task(TaskStatus.COMPLETED) == TaskStatus.COMPLETED


def test_backend_status_to_task_none_defaults_to_running() -> None:
    """None は RUNNING にデフォルト (実行中扱い)."""
    from aegis_ai.agents.runtime.lifecycle import backend_status_to_task
    from aegis_ai.task.task_manager import TaskStatus

    assert backend_status_to_task(None) == TaskStatus.RUNNING


def test_backend_status_to_task_unknown_defaults_to_failed() -> None:
    """未知の status は FAILED にマップ (フェイルセーフ)."""
    from aegis_ai.agents.runtime.lifecycle import backend_status_to_task
    from aegis_ai.task.task_manager import TaskStatus

    assert backend_status_to_task("mystery") == TaskStatus.FAILED
    assert backend_status_to_task("") == TaskStatus.FAILED


def test_task_status_to_backend_all_known_statuses() -> None:
    """`task_status_to_backend()`: 全状態を正しく逆変換する."""
    from aegis_ai.agents.runtime.lifecycle import task_status_to_backend
    from aegis_ai.task.task_manager import TaskStatus

    pairs = {
        TaskStatus.CREATED: "created",
        TaskStatus.PLANNING: "planning",
        TaskStatus.RUNNING: "running",
        TaskStatus.PAUSED: "paused",
        TaskStatus.COMPLETED: "completed",
        TaskStatus.FAILED: "failed",
        TaskStatus.CANCELLED: "cancelled",
        TaskStatus.EXPIRED: "expired",
    }
    for status, expected in pairs.items():
        assert task_status_to_backend(status) == expected


def test_task_status_round_trip() -> None:
    """`backend_status_to_task(task_status_to_backend(x)) == x`."""
    from aegis_ai.agents.runtime.lifecycle import (
        backend_status_to_task,
        task_status_to_backend,
    )
    from aegis_ai.task.task_manager import TaskStatus

    for status in TaskStatus:
        assert backend_status_to_task(task_status_to_backend(status)) == status


# ---------------------------------------------------------------------------
# is_terminal / validate_transition
# ---------------------------------------------------------------------------


def test_is_terminal_returns_true_for_completed_failed_cancelled_expired() -> None:
    """terminal 4 状態判定 (instruction.md §9)."""
    from aegis_ai.agents.runtime.lifecycle import is_terminal
    from aegis_ai.task.task_manager import TaskStatus

    for s in (
        TaskStatus.COMPLETED,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
        TaskStatus.EXPIRED,
    ):
        assert is_terminal(s) is True, s


def test_is_terminal_returns_false_for_active_states() -> None:
    """active 5 状態は terminal ではない."""
    from aegis_ai.agents.runtime.lifecycle import is_terminal
    from aegis_ai.task.task_manager import TaskStatus

    for s in (
        TaskStatus.CREATED,
        TaskStatus.PLANNING,
        TaskStatus.RUNNING,
        TaskStatus.PAUSED,
    ):
        assert is_terminal(s) is False, s


def test_validate_transition_allows_valid_running_to_completed() -> None:
    """RUNNING → COMPLETED は許可."""
    from aegis_ai.agents.runtime.lifecycle import validate_transition
    from aegis_ai.task.task_manager import TaskStatus

    assert validate_transition(TaskStatus.RUNNING, TaskStatus.COMPLETED) is True


def test_validate_transition_rejects_completed_to_running() -> None:
    """terminal 状態からの遷移は不可."""
    from aegis_ai.agents.runtime.lifecycle import validate_transition
    from aegis_ai.task.task_manager import TaskStatus

    assert validate_transition(TaskStatus.COMPLETED, TaskStatus.RUNNING) is False
    assert validate_transition(TaskStatus.FAILED, TaskStatus.RUNNING) is False
    assert validate_transition(TaskStatus.CANCELLED, TaskStatus.RUNNING) is False
    assert validate_transition(TaskStatus.EXPIRED, TaskStatus.RUNNING) is False


def test_validate_transition_allows_idempotent_same_status() -> None:
    """同一 status への遷移は冪等として許可."""
    from aegis_ai.agents.runtime.lifecycle import validate_transition
    from aegis_ai.task.task_manager import TaskStatus

    assert validate_transition(TaskStatus.RUNNING, TaskStatus.RUNNING) is True
    assert validate_transition(TaskStatus.PAUSED, TaskStatus.PAUSED) is True


# ---------------------------------------------------------------------------
# AgentResult → summary / step results
# ---------------------------------------------------------------------------


def test_agent_result_to_task_summary_uses_summary_field() -> None:
    """`AgentResult.summary` をそのまま返す."""
    from aegis_ai.agents.runtime.lifecycle import agent_result_to_task_summary

    @dataclass
    class _R:
        summary: str = "ok"
        errors: list = field(default_factory=list)

    assert agent_result_to_task_summary(_R(summary="all green")) == "all green"


def test_agent_result_to_task_summary_falls_back_to_first_error() -> None:
    """summary が空のときは最初の error を使う."""
    from aegis_ai.agents.runtime.lifecycle import agent_result_to_task_summary

    @dataclass
    class _Err:
        code: str = "timeout"
        message: str = "exceeded 30s"

    @dataclass
    class _R:
        summary: str = ""
        errors: list = field(default_factory=list)

    s = agent_result_to_task_summary(_R(errors=[_Err()]))
    assert "timeout" in s and "exceeded 30s" in s


def test_agent_result_to_step_results_extracts_actions() -> None:
    """`AgentResult.actions` を dict 形式に変換する."""
    from aegis_ai.agents.runtime.lifecycle import agent_result_to_step_results
    from aegis_ai.agents.runtime.models import AgentAction

    actions = [
        AgentAction(
            step_id="s1",
            capability_id="ai-server.agent.delegate",
            arguments={"goal": "x"},
            arguments_hash="h1",
            result={"ok": True},
            error="",
            duration_ms=42,
        )
    ]

    @dataclass
    class _R:
        actions: list = field(default_factory=list)

    out = agent_result_to_step_results(_R(actions=actions))
    assert len(out) == 1
    assert out[0]["step_id"] == "s1"
    assert out[0]["capability_id"] == "ai-server.agent.delegate"
    assert out[0]["result"] == {"ok": True}
    assert out[0]["duration_ms"] == 42


# ---------------------------------------------------------------------------
# is_agent_capability / build_agent_task
# ---------------------------------------------------------------------------


def test_is_agent_capability_matches_canonical_prefix() -> None:
    """`ai-server.agent.*` を真と判定."""
    from aegis_ai.agents.runtime.executor import is_agent_capability

    assert is_agent_capability("ai-server.agent.delegate") is True
    assert is_agent_capability("ai-server.agent.coding") is True
    assert is_agent_capability("ai-server.agent.foo.bar") is True
    assert is_agent_capability("pc-server.screenshot.get_screenshot") is False
    assert is_agent_capability("browser-server.page.open") is False
    assert is_agent_capability("") is False


def test_build_agent_task_uses_step_params_goal() -> None:
    """`step.params["goal"]` が AgentTask.goal になる."""
    from aegis_ai.agents.runtime.executor import build_agent_task
    from aegis_ai.task_plan import PlanStep

    step = PlanStep(
        step_id="s1",
        description="desc",
        capability_id="ai-server.agent.delegate",
        params={"goal": "explicit goal", "max_steps": 3, "timeout_seconds": 60},
    )
    plan = _StubPlan()
    task = build_agent_task(step=step, plan=plan)
    assert task.goal == "explicit goal"
    assert task.max_steps == 3
    assert task.timeout_seconds == 60
    assert task.metadata["step_id"] == "s1"
    assert task.metadata["capability_id"] == "ai-server.agent.delegate"


def test_build_agent_task_falls_back_to_description() -> None:
    """goal が無いときは step.description を使う."""
    from aegis_ai.agents.runtime.executor import build_agent_task
    from aegis_ai.task_plan import PlanStep

    step = PlanStep(
        step_id="s1",
        description="fallback desc",
        capability_id="ai-server.agent.delegate",
    )
    plan = _StubPlan()
    task = build_agent_task(step=step, plan=plan)
    assert task.goal == "fallback desc"


def test_build_agent_task_falls_back_to_plan_user_goal() -> None:
    """description も無いときは plan.user_goal を使う."""
    from aegis_ai.agents.runtime.executor import build_agent_task
    from aegis_ai.task_plan import PlanStep

    step = PlanStep(
        step_id="s1",
        capability_id="ai-server.agent.delegate",
    )
    plan = _StubPlan(user_goal="plan-level goal")
    task = build_agent_task(step=step, plan=plan)
    assert task.goal == "plan-level goal"


def test_build_agent_task_includes_expected_result_in_context() -> None:
    """expected_result は context にも入れる."""
    from aegis_ai.agents.runtime.executor import build_agent_task
    from aegis_ai.task_plan import PlanStep

    step = PlanStep(
        step_id="s1",
        description="d",
        capability_id="ai-server.agent.delegate",
        params={"goal": "g"},
        expected_result="hello world",
    )
    plan = _StubPlan()
    task = build_agent_task(step=step, plan=plan)
    assert task.context.get("expected_result") == "hello world"
    # goal は context には入れない (重複回避)
    assert "goal" not in task.context


# ---------------------------------------------------------------------------
# apply_result_to_step
# ---------------------------------------------------------------------------


def _step() -> Any:
    from aegis_ai.task_plan import PlanStep

    return PlanStep(
        step_id="s1",
        description="d",
        capability_id="ai-server.agent.delegate",
    )


def test_apply_result_to_step_completed() -> None:
    """`AgentResult(status=COMPLETED)` → `StepStatus.COMPLETED` + summary が result."""
    from aegis_ai.agents.runtime.executor import apply_result_to_step
    from aegis_ai.agents.runtime.models import AgentResult
    from aegis_ai.task.task_manager import TaskStatus
    from aegis_ai.task_plan import StepStatus

    step = _step()
    result = AgentResult(task_id="t1", status=TaskStatus.COMPLETED, summary="done")
    apply_result_to_step(step, result)
    assert step.status == StepStatus.COMPLETED
    assert step.result == "done"
    assert step.error == ""


def test_apply_result_to_step_failed_with_errors() -> None:
    """FAILED + errors → StepStatus.FAILED + first error code+message."""
    from aegis_ai.agents.runtime.executor import apply_result_to_step
    from aegis_ai.agents.runtime.models import AgentError, AgentResult
    from aegis_ai.task.task_manager import TaskStatus
    from aegis_ai.task_plan import StepStatus

    step = _step()
    result = AgentResult(
        task_id="t1",
        status=TaskStatus.FAILED,
        summary="",
        errors=[AgentError(code="timeout", message="30s exceeded")],
    )
    apply_result_to_step(step, result)
    assert step.status == StepStatus.FAILED
    assert "timeout" in step.error
    assert "30s exceeded" in step.error


def test_apply_result_to_step_failed_without_errors() -> None:
    """FAILED + errors 空 → StepStatus.FAILED + プレースホルダエラー."""
    from aegis_ai.agents.runtime.executor import apply_result_to_step
    from aegis_ai.agents.runtime.models import AgentResult
    from aegis_ai.task.task_manager import TaskStatus
    from aegis_ai.task_plan import StepStatus

    step = _step()
    result = AgentResult(task_id="t1", status=TaskStatus.FAILED, summary="")
    apply_result_to_step(step, result)
    assert step.status == StepStatus.FAILED
    assert step.error == "agent failed without error details"


def test_backend_waiting_approval_maps_to_paused() -> None:
    """A backend that reports waiting_approval is treated as PAUSED.

    Approval is no longer a constraint (2026-09-27), so there is no consent
    gate left to wait on; such a step surfaces as REQUIRES_OBSERVATION.
    """
    from aegis_ai.agents.runtime.executor import apply_result_to_step
    from aegis_ai.agents.runtime.lifecycle import backend_status_to_task
    from aegis_ai.agents.runtime.models import AgentResult
    from aegis_ai.task.task_manager import TaskStatus
    from aegis_ai.task_plan import StepStatus

    assert backend_status_to_task("waiting_approval") == TaskStatus.PAUSED

    step = _step()
    result = AgentResult(task_id="t1", status=TaskStatus.PAUSED, summary="")
    apply_result_to_step(step, result)
    assert step.status == StepStatus.REQUIRES_OBSERVATION
    assert "observation" in step.error.lower()


def test_apply_result_to_step_paused_becomes_requires_observation() -> None:
    """PAUSED → REQUIRES_OBSERVATION."""
    from aegis_ai.agents.runtime.executor import apply_result_to_step
    from aegis_ai.agents.runtime.models import AgentResult
    from aegis_ai.task.task_manager import TaskStatus
    from aegis_ai.task_plan import StepStatus

    step = _step()
    result = AgentResult(task_id="t1", status=TaskStatus.PAUSED, summary="")
    apply_result_to_step(step, result)
    assert step.status == StepStatus.REQUIRES_OBSERVATION
    assert "observation" in step.error.lower()


def test_apply_result_to_step_cancelled_becomes_skipped() -> None:
    """CANCELLED → SKIPPED."""
    from aegis_ai.agents.runtime.executor import apply_result_to_step
    from aegis_ai.agents.runtime.models import AgentResult
    from aegis_ai.task.task_manager import TaskStatus
    from aegis_ai.task_plan import StepStatus

    step = _step()
    result = AgentResult(task_id="t1", status=TaskStatus.CANCELLED, summary="")
    apply_result_to_step(step, result)
    assert step.status == StepStatus.SKIPPED


def test_apply_result_to_step_expired_becomes_failed() -> None:
    """EXPIRED → FAILED."""
    from aegis_ai.agents.runtime.executor import apply_result_to_step
    from aegis_ai.agents.runtime.models import AgentResult
    from aegis_ai.task.task_manager import TaskStatus
    from aegis_ai.task_plan import StepStatus

    step = _step()
    result = AgentResult(task_id="t1", status=TaskStatus.EXPIRED, summary="")
    apply_result_to_step(step, result)
    assert step.status == StepStatus.FAILED
    assert "expired" in step.error.lower()


# ---------------------------------------------------------------------------
# run_agent_step — LocalBackend 統合
# ---------------------------------------------------------------------------


def test_run_agent_step_with_local_backend_completes() -> None:
    """LocalBackend 経由で step を実行し、COMPLETED 結果を得る."""
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.agents.runtime.executor import run_agent_step
    from aegis_ai.task_plan import PlanStep, StepStatus

    backend = LocalBackend()
    step = PlanStep(
        step_id="s1",
        description="echo integration",
        capability_id="ai-server.agent.delegate",
        params={"goal": "echo integration"},
    )
    plan = _StubPlan()
    msg = _run(run_agent_step(step, plan, backend=backend))
    assert msg.startswith("[OK]")
    assert step.status == StepStatus.COMPLETED
    # step.result には summary と agent_actions が dict で入る
    assert isinstance(step.result, dict)
    assert "summary" in step.result
    assert "agent_actions" in step.result


def test_run_agent_step_rejects_non_agent_backend() -> None:
    """AgentBackend Protocol を満たさない backend は step を FAILED にする."""
    from aegis_ai.agents.runtime.executor import run_agent_step
    from aegis_ai.task_plan import PlanStep, StepStatus

    step = PlanStep(
        step_id="s1",
        description="d",
        capability_id="ai-server.agent.delegate",
    )

    class _NotABackend:
        pass

    plan = _StubPlan()
    msg = _run(run_agent_step(step, plan, backend=_NotABackend()))  # type: ignore[arg-type]
    assert "[FAIL]" in msg
    assert step.status == StepStatus.FAILED


# ---------------------------------------------------------------------------
# complete_task_with_agent_result — TaskManager 統合
# ---------------------------------------------------------------------------


def test_complete_task_with_agent_result_embeds_metadata(tmp_path: Path) -> None:
    """`complete_task_with_agent_result()` が `metadata["agent_result"]` に dict を保存し
    タスクを COMPLETED に遷移させる."""
    from aegis_ai.agents.runtime.models import (
        AgentAction,
        AgentError,
        AgentResult,
        Artifact,
        UsageMetrics,
    )
    from aegis_ai.task.task_manager import TaskManager, TaskStatus

    mgr = TaskManager(event_manager=None, audit_manager=None, data_dir=str(tmp_path))
    task = mgr.create_task(title="t", goal="g")
    task_id = task["task_id"]
    # start_task で CREATED → RUNNING に遷移してから complete
    started = mgr.start_task(task_id)
    assert started is not None
    assert started["status"] == TaskStatus.RUNNING.value

    result = AgentResult(
        task_id="agent-1",
        status=TaskStatus.COMPLETED,
        summary="agent completed",
        actions=[
            AgentAction(
                step_id="s1",
                capability_id="ai-server.agent.delegate",
                arguments={"goal": "x"},
                arguments_hash="abc",
                result={"ok": True},
            )
        ],
        artifacts=[Artifact(kind="file", uri="/tmp/out.txt", summary="result file")],
        errors=[AgentError(code="minor", message="ignored", recoverable=True)],
        suggested_follow_ups=["next step"],
        usage=UsageMetrics(
            input_tokens=10,
            output_tokens=20,
            cost_usd=0.0001,
            model="qwen2.5:7b",
            provider="ollama",
            tool_call_count=1,
            duration_ms=42,
        ),
    )

    out = mgr.complete_task_with_agent_result(task_id, result)
    assert out is not None
    assert out["status"] == TaskStatus.COMPLETED.value
    assert out["result_summary"] == "agent completed"
    assert "metadata" in out
    ar = out["metadata"]["agent_result"]
    assert ar["status"] == str(TaskStatus.COMPLETED)
    assert ar["action_count"] == 1
    assert ar["artifact_count"] == 1
    assert ar["error_count"] == 1
    assert ar["follow_ups"] == ["next step"]
    assert ar["usage"]["input_tokens"] == 10
    assert ar["usage"]["model"] == "qwen2.5:7b"
    assert ar["usage"]["provider"] == "ollama"


def test_complete_task_with_agent_result_unknown_task_returns_none(tmp_path: Path) -> None:
    """存在しない task_id は None."""
    from aegis_ai.agents.runtime.models import AgentResult
    from aegis_ai.task.task_manager import TaskManager, TaskStatus
    from aegis_ai.task.execution_engine import TaskExecutionEngine  # noqa: F401

    mgr = TaskManager(event_manager=None, audit_manager=None, data_dir=str(tmp_path))
    result = AgentResult(task_id="t", status=TaskStatus.COMPLETED, summary="x")
    assert mgr.complete_task_with_agent_result("no-such-task", result) is None


# ---------------------------------------------------------------------------
# TaskExecutionEngine 統合 — _execute_step の agent_delegate ルート
# ---------------------------------------------------------------------------


def _build_engine_with_tmpdir(monkeypatch, fake_runtime_get_backend):
    """TaskExecutionEngine + tmpdir + mock された runtime を一括構築する."""
    from aegis_ai.task.execution_engine import TaskExecutionEngine
    from aegis_ai.task.task_manager import TaskManager

    class _FakeRuntime:
        def get_agent_backend(self_inner):
            return fake_runtime_get_backend()

    monkeypatch.setattr("aegis_ai.runtime.get_runtime", lambda: _FakeRuntime())
    import tempfile

    td = tempfile.mkdtemp(prefix="aegis-engine-")
    mgr = TaskManager(event_manager=None, audit_manager=None, data_dir=td)
    return TaskExecutionEngine(task_manager=mgr)


def test_execution_engine_routes_agent_capability_to_agent_backend(monkeypatch) -> None:
    """`step.action_type == "agent_delegate"` のとき backend.run 経由で
    step が COMPLETED になる."""
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.task_plan import PlanStep, StepStatus, TaskPlan

    def _backend():
        return LocalBackend()

    engine = _build_engine_with_tmpdir(monkeypatch, _backend)
    plan = TaskPlan(plan_id="p1", user_goal="g1")
    step = PlanStep(
        step_id="s1",
        description="delegate to agent",
        action_type="agent_delegate",
        capability_id="ai-server.agent.delegate",
        params={"goal": "echo engine"},
    )
    plan.steps.append(step)

    msg = engine._execute_step("task-1", step, plan)
    assert msg.startswith("[OK]")
    assert step.status == StepStatus.COMPLETED


def test_execution_engine_routes_by_capability_id_prefix(monkeypatch) -> None:
    """`action_type != agent_delegate` でも capability_id が `ai-server.agent.*` なら
    エージェント経路に流れる."""
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.task_plan import PlanStep, StepStatus, TaskPlan

    def _backend():
        return LocalBackend()

    engine = _build_engine_with_tmpdir(monkeypatch, _backend)
    plan = TaskPlan(plan_id="p1", user_goal="g1")
    step = PlanStep(
        step_id="s1",
        description="capability-only route",
        action_type="custom",
        capability_id="ai-server.agent.coding",
        params={"goal": "echo by prefix"},
    )
    plan.steps.append(step)

    msg = engine._execute_step("task-1", step, plan)
    assert msg.startswith("[OK]")
    assert step.status == StepStatus.COMPLETED


def test_execution_engine_agent_step_without_runtime_fails_gracefully(monkeypatch) -> None:
    """`AegisRuntime.get_runtime()` が None を返す環境では step を FAILED にする."""
    from aegis_ai.task.execution_engine import TaskExecutionEngine
    from aegis_ai.task.task_manager import TaskManager
    from aegis_ai.task_plan import PlanStep, StepStatus, TaskPlan
    import tempfile

    monkeypatch.setattr("aegis_ai.runtime.get_runtime", lambda: None)
    td = tempfile.mkdtemp(prefix="aegis-engine-")
    mgr = TaskManager(event_manager=None, audit_manager=None, data_dir=td)
    engine = TaskExecutionEngine(task_manager=mgr)
    plan = TaskPlan(plan_id="p1", user_goal="g1")
    step = PlanStep(
        step_id="s1",
        description="no runtime",
        action_type="agent_delegate",
        capability_id="ai-server.agent.delegate",
    )
    plan.steps.append(step)

    msg = engine._execute_step("task-1", step, plan)
    assert "[FAIL]" in msg
    assert step.status == StepStatus.FAILED
    assert "agent backend is not registered" in step.error


def test_execution_engine_agent_step_without_capability_id_fails() -> None:
    """`action_type == "agent_delegate"` だが capability_id が無い step は FAILED."""
    from aegis_ai.task.execution_engine import TaskExecutionEngine
    from aegis_ai.task.task_manager import TaskManager
    from aegis_ai.task_plan import PlanStep, StepStatus, TaskPlan
    import tempfile

    td = tempfile.mkdtemp(prefix="aegis-engine-")
    mgr = TaskManager(event_manager=None, audit_manager=None, data_dir=td)
    engine = TaskExecutionEngine(task_manager=mgr)
    plan = TaskPlan(plan_id="p1", user_goal="g1")
    step = PlanStep(
        step_id="s1",
        description="no cap",
        action_type="agent_delegate",
        capability_id="",
    )
    plan.steps.append(step)

    msg = engine._execute_step("task-1", step, plan)
    assert "[FAIL]" in msg
    assert step.status == StepStatus.FAILED


# ---------------------------------------------------------------------------
# import 境界 — lifecycle.py / executor.py は openhands を import しない
# ---------------------------------------------------------------------------


def _module_source(module_name: str) -> str:
    import importlib

    mod = importlib.import_module(module_name)
    return inspect.getsource(mod)


def test_lifecycle_does_not_import_openhands() -> None:
    """lifecycle.py は openhands を import しない (§6 import 境界)."""
    src = _module_source("aegis_ai.agents.runtime.lifecycle")
    assert "openhands" not in src, src


def test_executor_does_not_import_openhands() -> None:
    """executor.py は openhands を import しない (§6 import 境界)."""
    src = _module_source("aegis_ai.agents.runtime.executor")
    assert "openhands" not in src, src


def test_lifecycle_imports_only_aegis_modules() -> None:
    """lifecycle.py の import 文を静的検査し、外部 SDK 依存ゼロを確認."""
    from aegis_ai.agents.runtime import lifecycle

    src = textwrap.dedent(inspect.getsource(lifecycle))
    # 'import openhands' / 'from openhands' がないこと
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            assert "openhands" not in stripped, f"forbidden import: {stripped}"
            # 他の外部 SDK (anthropic, openai, ...) も入っていないこと
            for forbidden in ("anthropic", "openai", "langchain", "llama_index"):
                assert forbidden not in stripped, f"forbidden import: {stripped}"


def test_executor_imports_only_aegis_modules() -> None:
    """executor.py の import 文を静的検査し、外部 SDK 依存ゼロを確認."""
    from aegis_ai.agents.runtime import executor

    src = textwrap.dedent(inspect.getsource(executor))
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            assert "openhands" not in stripped, f"forbidden import: {stripped}"
            for forbidden in ("anthropic", "openai", "langchain", "llama_index"):
                assert forbidden not in stripped, f"forbidden import: {stripped}"
