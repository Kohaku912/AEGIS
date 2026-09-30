"""Phase 1 DoD tests for the OpenHands agent runtime (instruction.md §36).

These tests intentionally avoid `_build_runtime` / `get_runtime()` for the
subprocess-based LocalBackend so they run quickly and do not require any
LLM provider. The `AegisRuntime.agent_backend` integration is exercised
through a lightweight stub in `test_aegis_runtime_bootstrap_*`.
"""
from __future__ import annotations

import ast
import asyncio
import hashlib
import inspect
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
    assert s.agents.timeout_seconds == 600


# ---------------------------------------------------------------------------
# Capability manifest — the feature-flag mechanism was removed (A-12 ②)
# ---------------------------------------------------------------------------


def test_capability_manifest_has_no_feature_flag_field() -> None:
    """The manifest dataclass no longer carries a feature-flag field (A-12 ②)."""
    from aegis_ai.folder_registry import CapabilityManifest

    assert "requires_feature" not in CapabilityManifest.__dataclass_fields__


def test_a_manifest_still_declaring_the_retired_key_is_inert(tmp_path: Path) -> None:
    """The loader no longer reads `requires_feature`, so the key cannot gate anything.

    This is the *data* half of the removal: even if a manifest JSON keeps the
    key, the capability loads and stays visible. A partial revert that restored
    the field would have to fail here.
    """
    from aegis_ai.capability_catalog import CapabilityCatalog

    builtin = tmp_path / "capabilities" / "builtin"
    (builtin / "ai-server" / "agent").mkdir(parents=True)
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

    catalog = CapabilityCatalog(capabilities_dir=str(tmp_path / "capabilities"))
    assert "ai-server.agent.delegate" in {m["id"] for m in catalog.list_for_llm()}

    manifest = catalog.resolve("ai-server.agent.delegate")
    assert manifest is not None
    assert not hasattr(manifest, "requires_feature"), (
        "the manifest dataclass grew the retired field back — see register A-12"
    )


def test_delegate_manifest_present_in_repo() -> None:
    """`ai-server.agent.delegate` manifest が repository 内に存在する."""
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
    assert "requires_feature" not in data
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
    import aegis_ai.agents.runtime.interface as iface_mod
    import aegis_ai.agents.runtime.models as models_mod

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


# ---------------------------------------------------------------------------
# A-12 (option ②) — the `requires_feature` mechanism was deleted
# ---------------------------------------------------------------------------
#
# The mechanism was declared, documented and tested, and no caller under `src/`
# ever supplied a flag set — so the filter never ran on the live path and
# `ai-server.agent.delegate` stayed visible to the LLM even though
# `settings.agents.enabled` defaults to `False`. A gate that cannot close is
# worse than no gate: it reads as a control while hiding nothing, so option ②
# deleted it outright rather than wiring it (PROJECT_STATUS_REVIEW.md row A-12).
#
# These tests record the **removal**, not the defect. Each fails if any part of
# the mechanism returns: a parameter on an entry point, a field on either
# manifest type, a key in a shipped manifest, or the identifier itself anywhere
# under `src/`.
#
# On the identifier scan below: it is safe to keep because its expected count is
# **zero**, so it needs no exclusion list — and a hand-maintained exclusion list
# is itself the defect this project warns about. History belongs in the register
# and in this file, not in `src/` prose. If a future feature genuinely needs a
# manifest-declared gate, this file fails first and the register gets a new row.

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"

#: The retired parameter and the retired manifest key. Both must be absent.
_RETIRED_FLAG_PARAMETER = "feature_flags"
_RETIRED_MANIFEST_KEY = "requires_feature"

#: The four entry points that used to accept a flag set. Listed so the scan can
#: be shown to still find them — a rename must not silently empty the scan.
_RETIRED_FLAG_ENTRY_POINTS: tuple[tuple[str, str], ...] = (
    ("aegis_ai/capability_catalog.py", "list_for_llm"),
    ("aegis_ai/capability_catalog.py", "list_for_agent"),
    ("aegis_ai/capability_catalog.py", "mcp_tool_schemas"),
    ("aegis_ai/tools/mcp_gateway.py", "list_tools_for_agent"),
)


def _functions_declaring(name: str) -> list[str]:
    """Every `src/` function whose signature has a parameter called ``name``."""
    found: list[str] = []
    for path in sorted(_SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = node.args
                params = {
                    a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)
                }
                if name in params:
                    found.append(
                        f"{path.relative_to(_SRC_ROOT).as_posix()}:{node.name}"
                    )
    return sorted(found)


def _entry_points_present() -> set[tuple[str, str]]:
    """The subset of ``_RETIRED_FLAG_ENTRY_POINTS`` that still exists."""
    seen: set[tuple[str, str]] = set()
    for rel, func in _RETIRED_FLAG_ENTRY_POINTS:
        tree = ast.parse((_SRC_ROOT / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == func:
                    seen.add((rel, func))
    return seen


def test_no_function_under_src_declares_the_retired_flag_parameter() -> None:
    """Nothing under `src/` takes a feature-flag set any more."""
    found = _functions_declaring(_RETIRED_FLAG_PARAMETER)
    assert found == [], f"the retired parameter is back under src/: {found}"


def test_the_scan_has_a_subject() -> None:
    """Not-vacuous: the four entry points still exist, so the scan above is real.

    Without this, renaming `list_for_llm` would make the test above pass by
    scanning nothing at all.
    """
    assert _entry_points_present() == set(_RETIRED_FLAG_ENTRY_POINTS)


def test_the_entry_points_no_longer_accept_the_retired_parameter() -> None:
    """Signature-level check of the public surface, independent of the AST walk."""
    from aegis_ai.capability_catalog import CapabilityCatalog
    from aegis_ai.tools.mcp_gateway import list_tools_for_agent

    surfaces = {
        "CapabilityCatalog.list_for_llm": CapabilityCatalog.list_for_llm,
        "CapabilityCatalog.list_for_agent": CapabilityCatalog.list_for_agent,
        "CapabilityCatalog.mcp_tool_schemas": CapabilityCatalog.mcp_tool_schemas,
        "list_tools_for_agent": list_tools_for_agent,
    }
    for label, func in surfaces.items():
        params = inspect.signature(func).parameters
        assert _RETIRED_FLAG_PARAMETER not in params, f"{label} still accepts it"


def test_neither_manifest_type_has_the_retired_field() -> None:
    """The dataclass and the pydantic model both lost the field."""
    from aegis_ai.folder_registry import CapabilityManifest
    from aegis_ai.schema import CapabilityManifestModel

    assert _RETIRED_MANIFEST_KEY not in CapabilityManifest.__dataclass_fields__
    assert _RETIRED_MANIFEST_KEY not in CapabilityManifestModel.model_fields


def test_no_shipped_manifest_declares_the_retired_key() -> None:
    """Discovered, not listed: every manifest JSON shipped with the server."""
    caps = _SRC_ROOT.parent / "capabilities"
    manifests = sorted(caps.rglob("*.json"))
    assert manifests, f"no manifests found under {caps}"
    offenders: list[str] = []
    for path in manifests:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and _RETIRED_MANIFEST_KEY in data:
            offenders.append(path.relative_to(caps).as_posix())
    assert offenders == [], f"a manifest re-declares the retired key: {offenders}"


def test_the_retired_identifiers_appear_nowhere_under_src() -> None:
    """No parameter, field or prose mention survives anywhere under `src/`.

    A textual scan whose expected count is zero needs no exclusion list, so it
    cannot rot into a list nobody maintains. It is also the only mechanical guard
    against the original defect: prose promising a gate that does not exist.
    """
    hits: list[str] = []
    for path in sorted(_SRC_ROOT.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if _RETIRED_FLAG_PARAMETER in line or _RETIRED_MANIFEST_KEY in line:
                hits.append(f"{path.relative_to(_SRC_ROOT).as_posix()}:{lineno}")
    assert hits == [], f"the retired identifier survives under src/: {hits}"


def test_the_delegate_capability_is_visible_with_agents_disabled() -> None:
    """The consequence of the removal: visibility no longer depends on a switch."""
    from aegis_ai.capability_catalog import CapabilityCatalog
    from aegis_ai.settings.models import AgentSettings

    catalog = CapabilityCatalog(capabilities_dir=str(_SRC_ROOT.parent / "capabilities"))
    shown = {entry["id"] for entry in catalog.list_for_llm()}
    assert "ai-server.agent.delegate" in shown

    # The switch that used to be *claimed* to hide it is still off by default —
    # so if the capability were ever gated again it would have to be gated by
    # something else, and this test would have to be rewritten.
    assert AgentSettings().enabled is False


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
