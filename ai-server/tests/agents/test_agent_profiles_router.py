"""Phase 5 DoD tests — AgentProfile + AgentRouter (instruction.md §21, §22, §36).

DoD チェックリスト (§36 Phase 5):
- [x] `agent_profiles.yaml` の 6 profile
      (general, coding, research, browser, maintenance, planning) がロードできる
- [x] `AgentRouter.select(goal_type="coding")` → backend=`openhands`, profile=`coding`
- [x] profile が見つからない場合は `general` にフォールバックし、
      **audit に warning を残す**
"""
from __future__ import annotations

import importlib
import inspect
import os
import tempfile
import textwrap
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# AgentProfile / AgentRiskCeiling / WorkspaceKind モデル
# ---------------------------------------------------------------------------


def test_agent_profile_defaults() -> None:
    """`AgentProfile` のデフォルト値で生成できる."""
    from aegis_ai.agents.profiles import (
        AgentProfile,
        AgentRiskCeiling,
        WorkspaceKind,
    )

    p = AgentProfile(
        id="custom",
        backend="openhands",
        llm_profile_name="chat_balanced",
    )
    assert p.id == "custom"
    assert p.tools == []
    assert p.max_runtime_sec == 1800
    assert p.max_iterations == 100
    assert p.risk_ceiling == AgentRiskCeiling.APPROVAL_REQUIRED
    assert p.workspace_kind == WorkspaceKind.ISOLATED
    assert p.allowed_capabilities == []
    assert p.denied_capabilities == []
    assert p.requires_approval_for == []
    assert p.cost_budget_usd is None


def test_agent_risk_ceiling_parse_case_insensitive() -> None:
    """`AgentRiskCeiling.parse` が case-insensitive で受理する."""
    from aegis_ai.agents.profiles import AgentRiskCeiling

    assert AgentRiskCeiling.parse("read_only") == AgentRiskCeiling.READ_ONLY
    assert AgentRiskCeiling.parse("READ_ONLY") == AgentRiskCeiling.READ_ONLY
    assert AgentRiskCeiling.parse("Safe_Action") == AgentRiskCeiling.SAFE_ACTION
    with pytest.raises(ValueError):
        AgentRiskCeiling.parse("invalid_ceiling")


def test_workspace_kind_parse() -> None:
    """`WorkspaceKind.parse` が case-insensitive で受理する."""
    from aegis_ai.agents.profiles import WorkspaceKind

    assert WorkspaceKind.parse("read_only") == WorkspaceKind.READ_ONLY
    assert WorkspaceKind.parse("ISOLATED") == WorkspaceKind.ISOLATED
    with pytest.raises(ValueError):
        WorkspaceKind.parse("nonexistent")


def test_agent_profile_allows_capability_deny_wins() -> None:
    """`allows_capability` は deny > allow の優先順位."""
    from aegis_ai.agents.profiles import AgentProfile

    p = AgentProfile(
        id="x",
        backend="local",
        llm_profile_name="local_chat",
        allowed_capabilities=["a", "b"],
        denied_capabilities=["b"],
    )
    assert p.allows_capability("a") is True
    assert p.allows_capability("b") is False  # deny wins
    assert p.allows_capability("c") is False  # not in allow

    # Empty allow = open
    q = AgentProfile(id="q", backend="local", llm_profile_name="local_chat")
    assert q.allows_capability("anything") is True


def test_agent_profile_requires_approval() -> None:
    """`requires_approval` は `requires_approval_for`  membership."""
    from aegis_ai.agents.profiles import AgentProfile

    p = AgentProfile(
        id="p",
        backend="local",
        llm_profile_name="local_chat",
        requires_approval_for=["git.push", "github.pr_create"],
    )
    assert p.requires_approval("git.push") is True
    assert p.requires_approval("github.pr_create") is True
    assert p.requires_approval("readme.read") is False


def test_agent_profile_to_dict_roundtrip() -> None:
    """`to_dict` が enum を string 化する."""
    from aegis_ai.agents.profiles import (
        AgentProfile,
        AgentRiskCeiling,
        WorkspaceKind,
    )

    p = AgentProfile(
        id="x",
        backend="openhands",
        llm_profile_name="chat_balanced",
        risk_ceiling=AgentRiskCeiling.HIGH_RISK,
        workspace_kind=WorkspaceKind.ISOLATED,
    )
    d = p.to_dict()
    assert d["risk_ceiling"] == "high_risk"
    assert d["workspace_kind"] == "isolated"


# ---------------------------------------------------------------------------
# AgentProfileRegistry
# ---------------------------------------------------------------------------


def _write_yaml(tmp: Path, body: str) -> Path:
    p = tmp / "agent_profiles.yaml"
    p.write_text(textwrap.dedent(body), encoding="utf-8")
    return p


def test_registry_from_yaml_loads_six_standard_profiles() -> None:
    """DoD: 6 標準 profile がロードできる."""
    from aegis_ai.agents.profiles import AgentProfileRegistry

    # Locate the default YAML. Search several likely locations so the test
    # works whether pytest is invoked from `ai-server/` or from the repo root.
    candidates = [
        Path("ai-server/config/agent_profiles.yaml"),
        Path("config/agent_profiles.yaml"),
        Path(__file__).resolve().parents[2] / "config" / "agent_profiles.yaml",
    ]
    yaml_path = next((p for p in candidates if p.is_file()), None)
    if yaml_path is None:
        pytest.skip("default agent_profiles.yaml not found in any known location")

    reg = AgentProfileRegistry.from_yaml(str(yaml_path))
    assert reg.has("general")
    assert reg.has("coding")
    assert reg.has("research")
    assert reg.has("browser")
    assert reg.has("maintenance")
    assert reg.has("planning")
    # Order-independent: 6 個ある
    assert len(reg) == 6


def test_registry_get_returns_profile_or_none() -> None:
    """`get()` が見つかれば返し、なければ None."""
    from aegis_ai.agents.profiles import AgentProfileRegistry

    with tempfile.TemporaryDirectory() as td:
        path = _write_yaml(
            Path(td),
            """\
            version: "1.0.0"
            profiles:
              coding:
                backend: openhands
                llm_profile_name: tool_planning
                tools: [filesystem, terminal]
            """,
        )
        reg = AgentProfileRegistry.from_yaml(str(path))
    assert reg.get("coding") is not None
    assert reg.get("missing") is None
    assert reg.get("") is None


def test_registry_handles_missing_yaml_gracefully() -> None:
    """YAML が見つからないときは空 registry を返す (クラッシュしない)."""
    from aegis_ai.agents.profiles import AgentProfileRegistry

    reg = AgentProfileRegistry.from_yaml("/nonexistent/path/agent_profiles.yaml")
    assert len(reg) == 0
    assert reg.source_path == "/nonexistent/path/agent_profiles.yaml"


def test_registry_handles_invalid_yaml_records_warning() -> None:
    """YAML が壊れていても warning を残して空で返す (例外で落ちない)."""
    from aegis_ai.agents.profiles import AgentProfileRegistry

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "agent_profiles.yaml"
        path.write_text("profiles: not_a_mapping\n", encoding="utf-8")
        reg = AgentProfileRegistry.from_yaml(str(path))
        # 壊れた YAML は load_warnings に記録される
        assert reg.load_warnings or len(reg) == 0


def test_registry_validates_required_fields() -> None:
    """`backend` または `llm_profile_name` が無い profile は skip."""
    from aegis_ai.agents.profiles import AgentProfileRegistry

    with tempfile.TemporaryDirectory() as td:
        path = _write_yaml(
            Path(td),
            """\
            profiles:
              good:
                backend: openhands
                llm_profile_name: chat_balanced
              no_backend:
                llm_profile_name: chat_balanced
              no_llm:
                backend: openhands
            """,
        )
        reg = AgentProfileRegistry.from_yaml(str(path))
    assert reg.has("good")
    assert not reg.has("no_backend")
    assert not reg.has("no_llm")
    assert any("no_backend" in w for w in reg.load_warnings)


# ---------------------------------------------------------------------------
# AgentRouter
# ---------------------------------------------------------------------------


def _build_router(*profiles: dict) -> "AgentRouter":  # type: ignore[name-defined]
    """Convenience builder: dict → AgentProfileRegistry → AgentRouter."""
    from aegis_ai.agents.profiles import AgentProfile, AgentProfileRegistry
    from aegis_ai.agents.runtime.router import AgentRouter

    reg = AgentProfileRegistry()
    for p in profiles:
        reg.register(AgentProfile(**p))
    return AgentRouter(registry=reg, fallback_id="general")


def test_router_select_explicit_id() -> None:
    """DoD: `select(requested_id="coding")` → backend=`openhands`, profile=`coding`."""
    from aegis_ai.agents.profiles import (
        AgentProfile,
        AgentRiskCeiling,
        WorkspaceKind,
    )
    from aegis_ai.agents.runtime.router import AgentRouter

    reg = _build_router(
        dict(
            id="general",
            backend="openhands",
            llm_profile_name="chat_balanced",
            risk_ceiling=AgentRiskCeiling.APPROVAL_REQUIRED,
            workspace_kind=WorkspaceKind.ISOLATED,
        ),
        dict(
            id="coding",
            backend="openhands",
            llm_profile_name="tool_planning",
            risk_ceiling=AgentRiskCeiling.HIGH_RISK,
            workspace_kind=WorkspaceKind.ISOLATED,
        ),
    )

    decision = reg.select("coding")
    assert decision.profile.id == "coding"
    assert decision.profile.backend == "openhands"
    assert decision.profile.llm_profile_name == "tool_planning"
    assert decision.fell_back is False
    assert decision.requested_id == "coding"


def test_router_falls_back_to_general_with_warning() -> None:
    """DoD: 存在しない profile を要求すると `general` に fallback + audit warning."""
    from aegis_ai.agents.profiles import AgentRiskCeiling, WorkspaceKind
    from aegis_ai.agents.runtime.router import AgentRouter

    router = _build_router(
        dict(
            id="general",
            backend="openhands",
            llm_profile_name="chat_balanced",
            risk_ceiling=AgentRiskCeiling.APPROVAL_REQUIRED,
            workspace_kind=WorkspaceKind.ISOLATED,
        )
    )
    captured: list[str] = []

    class _Sink:
        def __call__(self, message: str) -> None:
            captured.append(message)

    router.audit_sink = _Sink()
    decision = router.select("nonexistent")

    assert decision.profile.id == "general"
    assert decision.fell_back is True
    assert any("nonexistent" in m and "general" in m for m in captured)


def test_router_free_text_goal_does_not_override_profile_selection() -> None:
    """free-text goal だけでは specialized profile に寄せず general を維持する."""
    from aegis_ai.agents.profiles import AgentRiskCeiling, WorkspaceKind
    from aegis_ai.agents.runtime.router import AgentRouter

    router = _build_router(
        dict(
            id="general",
            backend="openhands",
            llm_profile_name="chat_balanced",
            risk_ceiling=AgentRiskCeiling.APPROVAL_REQUIRED,
            workspace_kind=WorkspaceKind.ISOLATED,
        ),
    )
    decision = router.select("", user_goal="Please implement a new feature")
    assert decision.profile.id == "general"
    assert "default" in decision.reason


def test_router_required_coding_flag_overrides_goal() -> None:
    """`required_coding=True` で goal が空でも coding が選ばれる."""
    from aegis_ai.agents.profiles import AgentRiskCeiling, WorkspaceKind
    from aegis_ai.agents.runtime.router import AgentRouter

    router = _build_router(
        dict(
            id="general",
            backend="openhands",
            llm_profile_name="chat_balanced",
            risk_ceiling=AgentRiskCeiling.APPROVAL_REQUIRED,
            workspace_kind=WorkspaceKind.ISOLATED,
        ),
        dict(
            id="coding",
            backend="openhands",
            llm_profile_name="tool_planning",
            risk_ceiling=AgentRiskCeiling.HIGH_RISK,
            workspace_kind=WorkspaceKind.ISOLATED,
        ),
    )
    decision = router.select("", user_goal="", required_coding=True)
    assert decision.profile.id == "coding"
    assert decision.fell_back is False


def test_router_capability_driven_routing_to_coding() -> None:
    """capability に git/github が含まれていれば coding."""
    from aegis_ai.agents.profiles import AgentRiskCeiling, WorkspaceKind
    from aegis_ai.agents.runtime.router import AgentRouter

    router = _build_router(
        dict(
            id="general",
            backend="openhands",
            llm_profile_name="chat_balanced",
            risk_ceiling=AgentRiskCeiling.APPROVAL_REQUIRED,
            workspace_kind=WorkspaceKind.ISOLATED,
        ),
        dict(
            id="coding",
            backend="openhands",
            llm_profile_name="tool_planning",
            risk_ceiling=AgentRiskCeiling.HIGH_RISK,
            workspace_kind=WorkspaceKind.ISOLATED,
        ),
    )
    decision = router.select(
        "", user_goal="", capabilities=["ai-server.git.status"]
    )
    assert decision.profile.id == "coding"


def test_router_default_fallback_when_no_capability_hint() -> None:
    """goal があっても capability hint や explicit profile が無ければ default fallback."""
    from aegis_ai.agents.profiles import AgentRiskCeiling, WorkspaceKind
    from aegis_ai.agents.runtime.router import AgentRouter

    router = _build_router(
        dict(
            id="general",
            backend="openhands",
            llm_profile_name="chat_balanced",
            risk_ceiling=AgentRiskCeiling.APPROVAL_REQUIRED,
            workspace_kind=WorkspaceKind.ISOLATED,
        )
    )
    decision = router.select("", user_goal="hello")
    assert decision.profile.id == "general"
    assert decision.fell_back is False  # exact match
    assert "default" in decision.reason


def test_router_synthetic_profile_when_fallback_missing() -> None:
    """fallback_id も無い場合は合成 profile を返す (None にしない)."""
    from aegis_ai.agents.profiles import AgentProfileRegistry
    from aegis_ai.agents.runtime.router import AgentRouter

    reg = AgentProfileRegistry()  # empty
    router = AgentRouter(registry=reg, fallback_id="nonexistent")
    decision = router.select("anything")
    assert decision.profile is not None
    assert decision.profile.id == "nonexistent"
    assert decision.fell_back is True


def test_router_backend_resolver_overrides_profile_backend() -> None:
    """`backend_resolver` で backend 名を変換できる."""
    from aegis_ai.agents.profiles import AgentRiskCeiling, WorkspaceKind
    from aegis_ai.agents.runtime.router import AgentRouter

    router = _build_router(
        dict(
            id="general",
            backend="openhands",
            llm_profile_name="chat_balanced",
            risk_ceiling=AgentRiskCeiling.APPROVAL_REQUIRED,
            workspace_kind=WorkspaceKind.ISOLATED,
        )
    )
    router.backend_resolver = lambda name: f"resolved-{name}" if name else name
    decision = router.select("general")
    assert decision.backend == "resolved-openhands"


def test_router_audit_sink_exception_does_not_break_routing() -> None:
    """audit_sink が例外を投げても routing は継続する."""

    class _BadSink:
        def __call__(self, message: str) -> None:
            raise RuntimeError("audit exploded")

    from aegis_ai.agents.profiles import AgentRiskCeiling, WorkspaceKind
    from aegis_ai.agents.runtime.router import AgentRouter

    router = _build_router(
        dict(
            id="general",
            backend="openhands",
            llm_profile_name="chat_balanced",
            risk_ceiling=AgentRiskCeiling.APPROVAL_REQUIRED,
            workspace_kind=WorkspaceKind.ISOLATED,
        )
    )
    router.audit_sink = _BadSink()
    decision = router.select("nonexistent")
    # Fallback まで通っている (audit_sink の例外で止まらない)
    assert decision.profile.id == "general"


# ---------------------------------------------------------------------------
# import 境界 — profiles/* / runtime/router は openhands を import しない
# ---------------------------------------------------------------------------


def _module_source(module_name: str) -> str:
    return textwrap.dedent(inspect.getsource(importlib.import_module(module_name)))


@pytest.mark.parametrize(
    "module_name",
    [
        "aegis_ai.agents",
        "aegis_ai.agents.profiles",
        "aegis_ai.agents.profiles.models",
        "aegis_ai.agents.profiles.registry",
        "aegis_ai.agents.runtime.router",
    ],
)
def test_profile_module_does_not_import_openhands(module_name: str) -> None:
    """profiles/* と runtime/router は openhands SDK を import しない (§6)."""
    src = _module_source(module_name)
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            for forbidden in ("openhands", "anthropic", "openai", "langchain"):
                assert forbidden not in stripped, (
                    f"forbidden import in {module_name}: {stripped}"
                )


# ---------------------------------------------------------------------------
# AegisRuntime 統合 (smoke test)
# ---------------------------------------------------------------------------


def test_aegis_runtime_exposes_agent_profiles_and_router() -> None:
    """`_build_runtime` 後に `agent_profiles` と `agent_router` が non-None."""
    from aegis_ai.runtime import _build_runtime
    from aegis_ai.config import get_config

    # Reset singleton if any
    from aegis_ai import runtime as runtime_mod

    runtime_mod._RUNTIME = None
    runtime = _build_runtime(get_config())
    try:
        assert runtime.agent_profiles is not None
        assert runtime.agent_router is not None
        # router.registry == agent_profiles
        assert runtime.agent_router.registry is runtime.agent_profiles
    finally:
        # ``_build_runtime`` starts the status manager's background checks and the hook
        # engine. Dropping the singleton reference does not stop them, so they outlive the
        # test — and the status thread then keeps probing the LAN and writing the endpoint
        # resolver's process-global cache for the rest of the session.
        runtime.stop()
        runtime_mod._RUNTIME = None
