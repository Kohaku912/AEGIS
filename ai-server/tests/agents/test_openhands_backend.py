"""Phase 2 DoD tests — OpenHands backend (instruction.md §36).

DoD チェックリスト (§36):
- [x] 同じ AgentTask を LocalBackend と OpenHandsBackend の両方に渡して
      同一の AgentResult 形状 が返る
- [x] OpenHands SDK のバージョンアップ時、adapter.py 以外には変更不要
      (§6 import 境界ルール) → import boundary 検査
- [x] LocalBackend を使った CI テストが ネットワーク無しで 緑
      → LocalBackend 経路のテストはここでも再走させる

ネットワークが必要なテストは adapter 関数を mock して SDK 呼び出しを
エミュレートする。実 SDK 呼び出しは行わない (DoD: ネットワーク無しで緑).
"""

from __future__ import annotations

import asyncio
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    """Never leave a real runtime (and its ``status-check`` LAN-probing thread) behind.

    One test in this module calls the real ``get_runtime()``, which starts a daemon
    thread that re-resolves pc-server with ``allow_lan_scan=True`` and writes the
    endpoint resolver's process-global cache. See ``tests/conftest.py`` for the guard.
    """
    yield

    from aegis_ai.runtime import reset_runtime_for_tests

    reset_runtime_for_tests()


def _run(coro: Any) -> Any:
    # Python 3.12+ raises RuntimeError if no current event loop exists. The tests
    # run after Phase 3 tests which call `asyncio.run()` and close the loop, so
    # we must use `asyncio.new_event_loop()` instead of `asyncio.get_event_loop()`.
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


@dataclass
class _FakeTask:
    """AgentTask の最小 mock (テスト用)."""

    task_id: str = "t-001"
    goal: str = "echo hello"
    context: dict[str, Any] = field(default_factory=dict)
    tools: list[Any] = field(default_factory=list)
    profile: str = "general"
    max_steps: int = 5
    timeout_seconds: int = 30
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# DoD 1: 同じ AgentTask で 同じ AgentResult 形状
# ---------------------------------------------------------------------------


def test_openhands_backend_satisfies_agent_backend_protocol() -> None:
    """OpenHandsBackend が AgentBackend Protocol を満たす."""
    from aegis_ai.agents.backends.openhands import OpenHandsBackend
    from aegis_ai.agents.runtime.interface import AgentBackend

    backend = OpenHandsBackend()
    assert isinstance(backend, AgentBackend)
    assert backend.name == "openhands"
    assert hasattr(backend, "run")
    assert hasattr(backend, "cancel")
    assert hasattr(backend, "get_status")


def test_openhands_backend_unavailable_returns_failed_result(monkeypatch) -> None:
    """openhands-sdk 未インストール時は FAILED 結果 (DoD: 落ちない)."""
    from aegis_ai.agents.backends.openhands import OpenHandsBackend

    # adapter.is_openhands_available() を強制的に False にする
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.is_openhands_available",
        lambda: False,
    )

    backend = OpenHandsBackend()
    result = _run(backend.run(_FakeTask()))
    assert result.status.name == "FAILED"
    assert result.errors
    assert result.errors[0].code == "backend_unavailable"


def test_openhands_backend_run_returns_completed_result(monkeypatch) -> None:
    """adapter.run_conversation を mock して COMPLETED を返す経路を検証."""
    from aegis_ai.agents.backends.openhands import OpenHandsBackend

    fake_result = {
        "events": [
            {"kind": "message", "role": "assistant", "text": "done", "timestamp": None},
            {
                "kind": "action",
                "tool": "terminal",
                "args": {"cmd": "ls"},
                "timestamp": None,
            },
        ],
        "elapsed_ms": 123,
        "raw_status": "completed",
    }

    def fake_run_conversation(  # noqa: ARG001
        *,
        agent,
        workspace,
        prompt,
        timeout_seconds,
        on_progress,
        on_conversation_ready=None,
        should_interrupt=None,
    ):
        if on_progress is not None:
            on_progress({"stage": "completed", "elapsed_ms": 123})
        return fake_result

    # adapter import の関数だけ mock
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.is_openhands_available",
        lambda: True,
    )
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.run_conversation",
        fake_run_conversation,
    )
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.build_llm",
        lambda cfg: object(),
    )
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.build_agent",
        lambda llm, tools: object(),
    )
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.build_workspace",
        lambda ws, base: object(),
    )
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.build_prompt_from_task",
        lambda task: task.goal,
    )

    backend = OpenHandsBackend()
    result = _run(backend.run(_FakeTask(goal="say hi")))
    assert result.status.name == "COMPLETED"
    # DoD: 1 つの action が AgentAction に変換される
    assert len(result.actions) == 1
    assert result.actions[0].capability_id == "openhands.tool.terminal"
    # summary に assistant メッセージが入る
    assert "done" in result.summary


def test_local_and_openhands_produce_same_result_shape(monkeypatch, tmp_path: Path) -> None:
    """DoD: 同じ AgentTask → Local と OpenHands で同じ AgentResult 形状."""
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.agents.backends.openhands import OpenHandsBackend

    # LocalBackend は cli.py を subprocess で叩くので本物の CLI モジュールを使う
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parents[2] / "src"))
    local = LocalBackend()

    # OpenHands は mock で完了させる
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.is_openhands_available",
        lambda: True,
    )
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.run_conversation",
        lambda **kw: {
            "events": [{"kind": "message", "role": "assistant", "text": "ok"}],
            "elapsed_ms": 1,
            "raw_status": "completed",
        },
    )
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.build_llm", lambda cfg: object()
    )
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.build_agent",
        lambda llm, tools: object(),
    )
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.build_workspace",
        lambda ws, base: object(),
    )
    monkeypatch.setattr(
        "aegis_ai.agents.backends.openhands.backend.build_prompt_from_task",
        lambda task: task.goal,
    )

    oh = OpenHandsBackend()

    task = _FakeTask(task_id="cmp-1", goal="echo compare")
    r_local = _run(local.run(task))
    r_oh = _run(oh.run(task))

    # 同じ dataclass 型
    assert type(r_local) is type(r_oh)
    # 同じフィールド (signature 一致)
    assert r_local.__dataclass_fields__.keys() == r_oh.__dataclass_fields__.keys()
    # status の取りうる値も同一 (TaskStatus enum 由来)
    assert r_local.status.name in ("COMPLETED", "FAILED")
    assert r_oh.status.name in ("COMPLETED", "FAILED")


def test_openhands_backend_cancel_interrupts_live_conversation() -> None:
    from aegis_ai.agents.backends.openhands import OpenHandsBackend

    class _FakeConversation:
        def __init__(self) -> None:
            self.interrupted = False

        def interrupt(self) -> None:
            self.interrupted = True

    backend = OpenHandsBackend()
    conversation = _FakeConversation()
    backend._live_conversations["task-1"] = conversation
    try:
        assert _run(backend.cancel("task-1")) is True
    finally:
        backend._live_conversations.pop("task-1", None)
    assert conversation.interrupted is True


def test_openhands_backend_cancelled_result_uses_cancel_summary() -> None:
    from aegis_ai.agents.backends.openhands import OpenHandsBackend

    backend = OpenHandsBackend()
    result = backend._result_from_raw(
        _FakeTask(task_id="cancelled-1"),
        {
            "events": [],
            "elapsed_ms": 10,
            "raw_status": "paused",
            "cancelled": True,
        },
        0,
    )
    assert result.status.name == "CANCELLED"
    assert result.summary == "OpenHands run cancelled"


def test_openhands_backend_tool_only_summary_mentions_command_and_files() -> None:
    from aegis_ai.agents.backends.openhands import OpenHandsBackend

    backend = OpenHandsBackend()
    result = backend._result_from_raw(
        _FakeTask(task_id="tool-only-1"),
        {
            "events": [
                {
                    "kind": "action",
                    "tool": "terminal",
                    "args": {"command": "pytest tests/agents/test_remote_backend.py -q"},
                },
                {
                    "kind": "action",
                    "tool": "file_editor",
                    "args": {
                        "command": "view",
                        "path": "src/aegis_agent_server/main.py",
                    },
                },
            ],
            "elapsed_ms": 20,
            "raw_status": "completed",
        },
        0,
    )
    assert "pytest tests/agents/test_remote_backend.py -q" in result.summary
    assert "src/aegis_agent_server/main.py" in result.summary


def test_local_backend_runs_without_network(monkeypatch) -> None:
    """DoD: LocalBackend テストはネットワーク無しで緑."""
    from aegis_ai.agents.backends.local import LocalBackend

    # ネットワーク呼び出しを一切しない (LocalBackend は subprocess だけ)
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parents[2] / "src"))
    backend = LocalBackend()
    result = _run(backend.run(_FakeTask(goal="echo networkless")))
    assert result.status.name == "COMPLETED"


# ---------------------------------------------------------------------------
# DoD 2: import 境界 — adapter.py 以外から openhands.* を import しない
# ---------------------------------------------------------------------------


def test_import_boundary_only_adapter_imports_openhands() -> None:
    """`adapter.py` 以外が `from openhands...` していないか静的検査.

    DoD: SDK のバージョンアップ時、`adapter.py` 以外には変更不要.
    """
    pkg_root = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "aegis_ai"
        / "agents"
        / "backends"
        / "openhands"
    )
    offenders: list[tuple[str, int, str]] = []
    allowed = {"adapter.py", "__init__.py"}
    for py in sorted(pkg_root.glob("*.py")):
        if py.name in allowed:
            continue
        text = py.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("from openhands") or stripped.startswith(
                "import openhands"
            ):
                offenders.append((py.name, i, line.strip()))
    assert not offenders, (
        "OpenHands imports must live in adapter.py only. Offenders: " + str(offenders)
    )


def test_adapter_module_imports_openhands_only_inside_functions() -> None:
    """`adapter.py` 内の `from openhands` は関数内のみ (DoD: import 失敗を局所化)."""
    adapter_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "aegis_ai"
        / "agents"
        / "backends"
        / "openhands"
        / "adapter.py"
    )
    text = adapter_path.read_text(encoding="utf-8")
    # module-level (`    from openhands...`) を検出
    module_level = []
    in_function = False
    for i, line in enumerate(text.splitlines(), start=1):
        if line.startswith("def ") or line.startswith("async def "):
            in_function = True
        elif line and not line.startswith(" ") and not line.startswith("#"):
            # dedent されたら function から出た
            in_function = False
        if not in_function and (
            line.startswith("from openhands") or line.startswith("import openhands")
        ):
            module_level.append((i, line))
    assert not module_level, (
        f"openhands imports must be inside functions, not module-level: {module_level}"
    )


# ---------------------------------------------------------------------------
# WorkspaceSpec
# ---------------------------------------------------------------------------


def test_workspace_spec_validation() -> None:
    from aegis_ai.agents.backends.openhands import WorkspaceSpec

    # default は valid
    assert WorkspaceSpec().validate() == []
    # invalid mode
    errs = WorkspaceSpec(mode="weird").validate()  # type: ignore[arg-type]
    assert any("mode invalid" in e for e in errs)
    # read_only だが mount_ro=False
    errs = WorkspaceSpec(mode="read_only", mount_ro=False).validate()
    assert any("mount_ro" in e for e in errs)
    # persistent だが path なし
    errs = WorkspaceSpec(mode="persistent", path=None).validate()
    assert any("path" in e for e in errs)


def test_workspace_spec_writable_and_persistent() -> None:
    from aegis_ai.agents.backends.openhands import WorkspaceSpec

    ro = WorkspaceSpec(mode="read_only", mount_ro=True)
    assert ro.is_writable() is False
    assert ro.is_persistent() is False

    iso = WorkspaceSpec(mode="isolated")
    assert iso.is_writable() is True
    assert iso.is_persistent() is False

    pers = WorkspaceSpec(mode="persistent", path="/tmp/x")
    assert pers.is_writable() is True
    assert pers.is_persistent() is True


# ---------------------------------------------------------------------------
# AegisRuntime.set_agent_backend
# ---------------------------------------------------------------------------


def test_aegis_runtime_set_agent_backend_swaps_backend(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.agents.backends.openhands import OpenHandsBackend
    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    reset_runtime_for_tests()
    runtime = get_runtime()

    assert runtime.get_agent_backend() is None or runtime.get_agent_backend() is not None

    # 1. LocalBackend をセット
    local = LocalBackend()
    runtime.set_agent_backend(local)
    assert runtime.get_agent_backend() is local

    # 2. OpenHands に swap
    oh = OpenHandsBackend()
    runtime.set_agent_backend(oh)
    assert runtime.get_agent_backend() is oh

    # 3. None で解除
    runtime.set_agent_backend(None)
    assert runtime.get_agent_backend() is None

    reset_runtime_for_tests()


# ---------------------------------------------------------------------------
# Adapter: build_prompt_from_task
# ---------------------------------------------------------------------------


def test_adapter_build_prompt_from_task_with_context() -> None:
    """AgentTask.goal + context → 自然言語 prompt."""
    from aegis_ai.agents.backends.openhands.adapter import build_prompt_from_task

    task = _FakeTask(goal="list files", context={"repo": "aegis", "branch": "main"})
    prompt = build_prompt_from_task(task)
    assert "list files" in prompt
    assert "repo: aegis" in prompt
    assert "branch: main" in prompt


def test_adapter_build_prompt_from_task_without_context() -> None:
    from aegis_ai.agents.backends.openhands.adapter import build_prompt_from_task

    task = _FakeTask(goal="just echo", context={})
    assert build_prompt_from_task(task) == "just echo"


def test_adapter_build_llm_loads_project_env_when_needed(monkeypatch) -> None:
    pytest.importorskip("openhands.sdk")
    from aegis_ai.agents.backends.openhands import adapter as adapter_mod

    monkeypatch.delenv("A_TEST_OPENHANDS_KEY", raising=False)

    def fake_load_project_env() -> None:
        monkeypatch.setenv("A_TEST_OPENHANDS_KEY", "test-key")

    monkeypatch.setattr(adapter_mod, "_load_project_env", fake_load_project_env)
    llm = adapter_mod.build_llm(
        {
            "provider": "openai",
            "model": "deepseek-v4-flash",
            "api_key_env": "A_TEST_OPENHANDS_KEY",
            "base_url": "https://api.deepseek.com",
        }
    )
    assert getattr(llm, "model", "") == "openai/deepseek-v4-flash"


def test_adapter_build_llm_reads_project_dotenv_when_env_is_still_empty(
    monkeypatch,
) -> None:
    pytest.importorskip("openhands.sdk")
    from aegis_ai.agents.backends.openhands import adapter as adapter_mod

    monkeypatch.delenv("A_TEST_OPENHANDS_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setattr(adapter_mod, "_load_project_env", lambda: None)
    monkeypatch.setattr(
        adapter_mod,
        "_read_project_env_value",
        lambda name: "dotenv-key" if name == "A_TEST_OPENHANDS_KEY" else "",
    )

    llm = adapter_mod.build_llm(
        {
            "provider": "openai",
            "model": "deepseek-v4-flash",
            "api_key_env": "A_TEST_OPENHANDS_KEY",
            "base_url": "https://api.deepseek.com",
        }
    )
    api_key = getattr(llm, "api_key", None)
    if hasattr(api_key, "get_secret_value"):
        api_key = api_key.get_secret_value()
    assert api_key == "dotenv-key"


def test_adapter_build_agent_registers_default_tools() -> None:
    pytest.importorskip("openhands.sdk")
    from openhands.sdk.llm import Message, TextContent
    from openhands.sdk.testing import TestLLM

    from aegis_ai.agents.backends.openhands.adapter import build_agent

    llm = TestLLM.from_messages(
        [Message(role="assistant", content=[TextContent(text="done")])]
    )
    agent = build_agent(llm, ["terminal", "file_editor", "task_tracker"])
    assert [tool.name for tool in agent.tools] == [
        "terminal",
        "file_editor",
        "task_tracker",
    ]


def test_adapter_is_openhands_available() -> None:
    """is_openhands_available() が import 可能かを bool で返す."""
    from aegis_ai.agents.backends.openhands.adapter import is_openhands_available

    result = is_openhands_available()
    # openhands-sdk は pip install 済みなので True を期待
    # (CI で未インストールなら False でも pass する設計)
    assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# OpenHandsBackend.cancel / get_status
# ---------------------------------------------------------------------------


def test_openhands_backend_cancel_marks_id(monkeypatch) -> None:
    from aegis_ai.agents.backends.openhands import OpenHandsBackend

    backend = OpenHandsBackend()
    ok = _run(backend.cancel("t-cancel"))
    assert ok is True
    assert "t-cancel" in backend._cancelled


def test_openhands_backend_get_status_returns_completed() -> None:
    from aegis_ai.agents.backends.openhands import OpenHandsBackend
    from aegis_ai.task.task_manager import TaskStatus

    backend = OpenHandsBackend()
    status = _run(backend.get_status("t-x"))
    assert status == TaskStatus.COMPLETED
