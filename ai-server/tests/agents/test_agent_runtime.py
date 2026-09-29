"""Phase 1 DoD tests for the OpenHands agent runtime (instruction.md §36).

These tests intentionally avoid `_build_runtime` / `get_runtime()` for the
subprocess-based LocalBackend so they run quickly and do not require any
LLM provider. The `AegisRuntime.agent_backend` integration is exercised
through a lightweight stub in `test_aegis_runtime_bootstrap_*`.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# LocalBackend (subprocess) — read-only DoD
# ---------------------------------------------------------------------------


def _run(coro):
    # Python 3.12+ requires creating a new event loop when none exists.
    # The same pattern is used in `test_openhands_backend.py` for consistency.
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def test_local_backend_run_returns_completed_result() -> None:
    """Phase 1 DoD: LocalBackend.run(AgentTask(goal='echo hello')) → COMPLETED."""
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.agents.runtime.models import AgentTask
    from aegis_ai.task.task_manager import TaskStatus

    backend = LocalBackend()
    task = AgentTask(task_id="t-echo-1", goal="echo hello")
    result = _run(backend.run(task))

    assert result.status == TaskStatus.COMPLETED
    assert "echo" in result.summary.lower()
    assert len(result.actions) == 1
    action = result.actions[0]
    assert action.step_id == "t-echo-1-step-1"
    assert action.capability_id == "ai-server.agent.task.echo"
    assert action.result == {"echoed": "echo hello"}
    assert action.error == ""


def test_local_backend_satisfies_agent_backend_protocol() -> None:
    """Phase 1 DoD: LocalBackend は AgentBackend Protocol を満たす."""
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.agents.runtime.interface import AgentBackend

    backend = LocalBackend()
    assert isinstance(backend, AgentBackend)
    assert backend.name == "local"


def test_local_backend_cancel_is_noop_in_phase1() -> None:
    """Phase 1: cancel は no-op. False を返す."""
    from aegis_ai.agents.backends.local import LocalBackend

    backend = LocalBackend()
    cancelled = _run(backend.cancel("any-id"))
    assert cancelled is False


def test_local_backend_get_status_completed() -> None:
    """Phase 1: 状態を持たない. COMPLETED を返す."""
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.task.task_manager import TaskStatus

    backend = LocalBackend()
    assert _run(backend.get_status("any-id")) == TaskStatus.COMPLETED


def test_local_backend_progress_callback_is_invoked() -> None:
    """on_progress callback が 'started' と 'finished' の 2 回呼ばれる."""
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.agents.runtime.models import AgentTask

    backend = LocalBackend()
    seen: list[str] = []

    async def on_progress(progress):  # type: ignore[no-untyped-def]
        seen.append(progress.stage)

    task = AgentTask(task_id="t-progress-1", goal="echo progress")
    _run(backend.run(task, on_progress=on_progress))
    assert seen == ["started", "finished"]


def test_local_backend_arguments_hash_matches_approval_manager() -> None:
    """arguments_hash は ApprovalManager.compute_args_hash() と同じ SHA-256."""
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.agents.runtime.models import AgentTask

    backend = LocalBackend()
    task = AgentTask(task_id="t-hash-1", goal="hash me")
    result = _run(backend.run(task))
    action = result.actions[0]
    expected = hashlib.sha256(
        json.dumps(
            {"echo": "hash me"},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    assert action.arguments_hash == expected


def test_local_backend_timeout_returns_failed() -> None:
    """timeout_seconds=0 で即時 timeout する CLI 呼び出しは FAILED."""
    from aegis_ai.agents.backends.local import LocalBackend
    from aegis_ai.agents.runtime.models import AgentTask
    from aegis_ai.task.task_manager import TaskStatus

    backend = LocalBackend()
    task = AgentTask(task_id="t-timeout-1", goal="echo timeout", timeout_seconds=0)
    result = _run(backend.run(task))
    assert result.status == TaskStatus.FAILED
    assert any(e["code"] == "timeout" for e in result.errors)


# ---------------------------------------------------------------------------
# Dataclass models — 型と import 境界
# ---------------------------------------------------------------------------


def test_agent_models_fields_present() -> None:
    """AgentResult / AgentTask の必須フィールドが存在する (instruction.md §5)."""
    from aegis_ai.agents.runtime.models import (
        AgentAction,
        AgentError,
        AgentResult,
        AgentTask,
        Artifact,
        MemoryCandidate,
        UsageMetrics,
    )

    task = AgentTask(task_id="x", goal="g")
    assert task.task_id == "x"
    assert task.profile == "general"

    usage = UsageMetrics(input_tokens=1, output_tokens=2, model="m", provider="p")
    assert usage.cost_usd == 0.0
    assert usage.tool_call_count == 0

    result = AgentResult(
        task_id="x",
        status="completed",  # type: ignore[arg-type]
        summary="ok",
        usage=usage,
    )
    assert result.actions == []
    assert result.artifacts == []
    assert result.errors == []

    art = Artifact(kind="file", uri="/tmp/x", summary="s")
    err = AgentError(code="x", message="y", recoverable=False)
    mem = MemoryCandidate(type="semantic", content="c", confidence=0.5, importance=0.5)
    action = AgentAction(
        step_id="s",
        capability_id="c",
        arguments={},
        arguments_hash="h",
    )
    assert art.kind == "file"
    assert err.recoverable is False
    assert mem.tags == []
    assert action.duration_ms == 0


# ---------------------------------------------------------------------------
# Settings — agents.enabled default OFF (safe rollout)
# ---------------------------------------------------------------------------


def test_settings_default_agents_disabled() -> None:
    """AEGISSettings() の default は agents.enabled=False (Phase 1 safe default)."""
    from aegis_ai.settings.models import AEGISSettings

    s = AEGISSettings()
    assert s.agents.enabled is False
    assert s.agents.backend == "local"
    assert s.agents.default_profile == "general"
    assert s.agents.timeout_seconds == 600


# ---------------------------------------------------------------------------
# Capability manifest — feature flag 連動
# ---------------------------------------------------------------------------


def test_capability_manifest_has_requires_feature_field() -> None:
    """CapabilityManifest.requires_feature フィールドが dataclass に存在する."""
    from aegis_ai.folder_registry import CapabilityManifest

    m = CapabilityManifest(capability_id="x", requires_feature="agents")
    assert m.requires_feature == "agents"
    m2 = CapabilityManifest(capability_id="y")
    assert m2.requires_feature == ""


def test_list_for_llm_filters_by_feature_flag(tmp_path: Path) -> None:
    """`requires_feature: "agents"` の manifest は feature_flags に依存して filter される."""
    from aegis_ai.capability_catalog import CapabilityCatalog

    builtin = tmp_path / "capabilities" / "builtin"
    (builtin / "ai-server" / "agent").mkdir(parents=True)
    (builtin / "pc-server" / "screenshot").mkdir(parents=True)

    (builtin / "ai-server" / "agent" / "delegate.json").write_text(
        json.dumps(
            {
                "title": "delegate",
                "description": "delegate to agent",
                "server_id": "ai-server",
                "app_id": "agent",
                "action": "delegate",
                "operation_category": "read_only",
                "requires_feature": "agents",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (builtin / "pc-server" / "screenshot" / "get_screenshot.json").write_text(
        json.dumps(
            {
                "title": "screenshot",
                "description": "always on",
                "server_id": "pc-server",
                "app_id": "screenshot",
                "action": "get_screenshot",
                "operation_category": "read_only",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    catalog = CapabilityCatalog(capabilities_dir=str(tmp_path / "capabilities"))

    all_ids = {m["id"] for m in catalog.list_for_llm()}
    assert "pc-server.screenshot.get_screenshot" in all_ids
    assert "ai-server.agent.delegate" in all_ids  # default: no filter

    filtered_off = {m["id"] for m in catalog.list_for_llm(feature_flags=set())}
    assert "pc-server.screenshot.get_screenshot" in filtered_off
    assert "ai-server.agent.delegate" not in filtered_off  # agents feature OFF

    filtered_on = {m["id"] for m in catalog.list_for_llm(feature_flags={"agents"})}
    assert "ai-server.agent.delegate" in filtered_on
    assert "pc-server.screenshot.get_screenshot" in filtered_on


def test_delegate_manifest_present_in_repo() -> None:
    """`ai-server.agent.delegate` manifest が repository 内に存在し requires_feature=agents."""
    repo_root = Path(__file__).resolve().parents[2]
    manifest_path = (
        repo_root
        / "capabilities"
        / "builtin"
        / "ai-server"
        / "agent"
        / "delegate.json"
    )
    assert manifest_path.exists(), f"missing manifest: {manifest_path}"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["requires_feature"] == "agents"
    assert data["operation_category"] == "read_only"
    assert data["risk"]["level"] == "low"
    assert data["input_schema"]["required"] == ["goal"]


# ---------------------------------------------------------------------------
# import 境界 — OpenHands 未インストールでも import エラーなし
# ---------------------------------------------------------------------------


def test_import_agents_package_does_not_require_openhands() -> None:
    """OpenHands SDK が無くても aegis_ai.agents が import できる (Phase 1)."""
    import aegis_ai.agents  # noqa: F401
    from aegis_ai.agents import (  # noqa: F401
        AgentAction,
        AgentBackend,
        AgentError,
        AgentProgress,
        AgentResult,
        AgentTask,
        Artifact,
        MemoryCandidate,
        UsageMetrics,
    )
    from aegis_ai.agents.backends import (  # noqa: F401
        get_backend,
        list_backends,
        register_backend,
    )
    from aegis_ai.agents.backends.local import LocalBackend  # noqa: F401
    from aegis_ai.agents.runtime.interface import AgentBackend as RuntimeAgentBackend  # noqa: F401
    from aegis_ai.agents.runtime.models import AgentResult as RuntimeAgentResult  # noqa: F401

    assert RuntimeAgentBackend is AgentBackend
    assert RuntimeAgentResult is AgentResult


def test_runtime_models_do_not_import_openhands() -> None:
    """aegis_ai.agents.runtime.models は openhands を import していない."""
    import aegis_ai.agents.runtime.models as models_mod
    import aegis_ai.agents.runtime.interface as iface_mod

    for name in ("openhands", "openhands_sdk", "openhands_tools", "openhands_workspace"):
        assert name not in dir(models_mod)
        assert name not in dir(iface_mod)


# ---------------------------------------------------------------------------
# AegisRuntime.agent_backend フィールド — 後方互換
# ---------------------------------------------------------------------------


def test_aegis_runtime_dataclass_has_agent_backend_field() -> None:
    """AegisRuntime dataclass に `agent_backend` フィールドが追加されている (default None)."""
    from aegis_ai.runtime import AegisRuntime

    annotations = AegisRuntime.__dataclass_fields__
    assert "agent_backend" in annotations
    # default が None であること (後方互換)
    assert annotations["agent_backend"].default is None


# ---------------------------------------------------------------------------
# Agent 登録 registry
# ---------------------------------------------------------------------------


def test_agent_backend_registry_register_and_resolve() -> None:
    """register_backend / get_backend / list_backends が name ベースで動く."""
    from aegis_ai.agents.backends import (
        clear_backends,
        get_backend,
        list_backends,
        register_backend,
    )
    from aegis_ai.agents.backends.local import LocalBackend

    clear_backends()
    try:
        register_backend(LocalBackend())
        assert "local" in list_backends()
        assert get_backend("local") is not None
        assert get_backend("does-not-exist") is None
    finally:
        clear_backends()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
