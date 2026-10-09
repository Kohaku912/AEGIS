"""The real composition root supplies the surface the L1 -> L2 dispatch reads.

``tests/test_l1_reaches_the_l2_boundary.py`` pins the dispatch *rules*, but it drives them with a
``SimpleNamespace`` runtime that hands the dispatch everything it asks for. That proves the rules,
not that production supplies their inputs -- and every input is read through
``getattr(rt, name, None)``, so a missing one is a **silent skip**, not an error. A rule can be
green while the real runtime never reaches it.

Measured 2026-10-09 (cycle 117) by booting ``get_runtime()`` and reading the four names
``_run_l1_immediate_pipeline`` uses:

====================  =====================  ============================================
name                  real value             note
====================  =====================  ============================================
``l1_router``         ``L1Router``           present
``initiative_engine`` ``InitiativeEngine``   present, and **unguarded** (see below)
``l2_mind``           ``L2AutonomousMind``   present -- this is what makes the hand-off fire
``autonomous_loop``   ``None``               absent in a bare ``get_runtime()``
====================  =====================  ============================================

``autonomous_loop`` is the one absence and it is **not** a defect. The loop is created lazily by
``AegisRuntime.start_autonomous_if_enabled``, which the *entry points* call (``dashboard.py``,
``docker_entrypoint.py``, ``web/dashboard_legacy.py``) -- not ``_build_runtime``.
``autonomous_loop_enabled`` defaults to **True** (``settings/models.py``), so production has the
loop; a bare ``get_runtime()`` (as in tests) does not. The dispatch's ``if loop is not None``
guard then skips that notification, which is consistent: a loop that was never created is not
running either. The trap is to read the test harness's ``None`` as a production fact.

The asymmetry worth pinning: ``l2_mind`` and ``autonomous_loop`` are each checked with
``is not None``, so a missing one skips a step -- but ``initiative_engine.record_trigger(...)`` is
called **unguarded**. If the composition root ever stopped supplying it, the dispatch would raise
and the outer ``except Exception`` would log and abandon the event. Its presence is load-bearing
rather than optional, which is why it is asserted here.
"""

from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

_SERVER = Path(__file__).resolve().parents[1]
_RUNTIME_PY = _SERVER / "src" / "aegis_ai" / "runtime.py"

#: The names ``_run_l1_immediate_pipeline`` reads off the runtime.
_DISPATCH_SURFACE = ("l1_router", "initiative_engine", "autonomous_loop", "l2_mind")

#: The subset the L2 hand-off needs to be reachable (measured present in the composition root).
_HAND_OFF_SURFACE = ("l1_router", "initiative_engine", "l2_mind")

_EVENT_TYPE = "pc.user_activity.snapshot"


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    """Boot the real runtime, but never leave it running.

    Same reason as ``test_runtime_singleton.py``: ``get_runtime()`` starts a ``status-check``
    daemon that probes the real LAN and writes the result into the endpoint resolver's
    process-global cache. Tests here boot the runtime, so ``stop()`` has to be reached.
    """
    yield

    from aegis_ai.runtime import reset_runtime_for_tests

    reset_runtime_for_tests()


@pytest.fixture
def real_runtime(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))

    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    reset_runtime_for_tests()
    return get_runtime()


def _runtime_tree() -> ast.Module:
    return ast.parse(_RUNTIME_PY.read_text(encoding="utf-8"), filename=str(_RUNTIME_PY))


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} is no longer defined in runtime.py")


def _event() -> SimpleNamespace:
    return SimpleNamespace(
        event_id="evt-117",
        event_type=_EVENT_TYPE,
        payload_json='{"app":"vscode"}',
        timestamp_ms=1,
        source_server_id="pc-server",
        source_server_type=SimpleNamespace(name="PC"),
    )


def _install_escalating_router(runtime: Any) -> None:
    """Make the *real* ``L1Router`` observe -> decide -> escalate without an LLM round-trip."""
    from aegis_ai.intake.l1_models import (
        L1Action,
        L1ActionType,
        L1Decision,
        L1Observation,
        RequiredIntelligence,
    )

    def observe(event: Any, *, event_id: str = "", context_capsule: Any = None) -> Any:
        return L1Observation(
            event_id=event_id,
            meaning="user switched to the editor",
            value=0.6,
            priority=0.5,
            required_intelligence=RequiredIntelligence.HIGH,
            confidence=0.7,
            raw={"summary_bucket": "foreground", "observed_action": "switch_app"},
        )

    def decide(observation: Any) -> Any:
        return L1Decision(
            event_id=str(getattr(observation, "event_id", "") or ""),
            action=L1Action(type=L1ActionType.ESCALATE, reason="needs L2"),
            reasoning="because",
            observation=observation,
        )

    def escalate(observation: Any, *, reason: str = "") -> Any:
        return SimpleNamespace(
            to_payload=lambda: {"event_id": "evt-117", "reason": reason, "layer": "L1"}
        )

    runtime.l1_router.observe = observe
    runtime.l1_router.decide = decide
    runtime.l1_router.escalate = escalate


# ── Control: the names are declared, so a rename cannot masquerade as the lazy absence ──


def test_the_dispatch_surface_is_declared_on_the_runtime_type() -> None:
    """Control: the names the dispatch reads are dataclass fields.

    Without this, a *rename* would make ``getattr(rt, name, None)`` return ``None`` and look
    exactly like the lazily-created ``autonomous_loop`` -- the assertion below would pass for the
    wrong reason.
    """
    from aegis_ai.runtime import AegisRuntime

    declared = {f.name for f in fields(AegisRuntime)}
    missing = [n for n in _DISPATCH_SURFACE if n not in declared]
    assert not missing, (
        f"{missing} are not fields of AegisRuntime -- the dispatch reads them by name, so a "
        "rename turns every `getattr(rt, name, None)` guard into a silent None"
    )


# ── The claim: the composition root supplies what the hand-off needs ──


def test_the_real_runtime_supplies_the_hand_off_surface(real_runtime) -> None:
    """The composition root supplies what "L1 reaches just before L2" needs."""
    absent = [n for n in _HAND_OFF_SURFACE if getattr(real_runtime, n, None) is None]
    assert not absent, (
        f"{absent} are None on the runtime `get_runtime()` builds -- the dispatch reads them "
        "through `getattr(..., None)` guards, so each absence is a *silent skip* rather than an "
        "error, and the boundary test's fake runtime would be describing a configuration "
        "production does not have"
    )


def test_the_hand_off_actually_fires_through_the_real_runtime(real_runtime, monkeypatch) -> None:
    """Behavioural: drive the dispatch on the real runtime and watch ``_run_l2_pipeline`` fire.

    This is the half ``test_l1_reaches_the_l2_boundary.py`` cannot show -- it replaces the runtime
    with a ``SimpleNamespace``, so it proves the rules and not that the composition root satisfies
    them. Here the runtime is the real one; only the L1 router and the L2 pipeline are doubled.
    """
    import aegis_ai.runtime as runtime_module

    reached: list[str] = []

    def fake_l2(runtime: Any, *, trigger: str, detail: dict[str, Any]) -> dict[str, Any]:
        reached.append(trigger)
        return {"handled": True, "action_type": "act"}

    monkeypatch.setattr(runtime_module, "_run_l2_pipeline", fake_l2)
    _install_escalating_router(real_runtime)

    runtime_module._run_l1_immediate_pipeline(real_runtime, _event())

    assert reached == [_EVENT_TYPE], (
        "an escalating L1 decision on the real runtime did not reach the L2 hand-off "
        f"(reached={reached!r}) -- 'L1 reaches just before L2' is not true of production"
    )

    # Negative control: remove the one input the hand-off is guarded on and the same drive must
    # not reach L2 -- otherwise `reached` is non-empty for some reason other than the hand-off.
    real_runtime.l2_mind = None
    reached.clear()
    runtime_module._run_l1_immediate_pipeline(real_runtime, _event())
    assert reached == [], (
        "the L2 hand-off fired with l2_mind=None -- this probe is not measuring the guard it "
        "claims to"
    )


# ── The two halves of the asymmetry, pinned structurally ──


def test_the_initiative_engine_is_load_bearing_not_optional() -> None:
    """``record_trigger`` is called **unguarded**, unlike the two ``is not None`` guards.

    ``l2_mind`` and ``autonomous_loop`` are each read with ``getattr(rt, ..., None)`` and checked,
    so a missing one skips a step. ``initiative_engine`` is read the same way but then used
    directly -- if the composition root stopped supplying it, the dispatch would raise and the
    outer ``except Exception`` would log and abandon the event. Pinned so the asymmetry stays
    deliberate rather than accidental.
    """
    dispatch = _function(_runtime_tree(), "_run_l1_immediate_pipeline")

    guards = [
        node
        for node in ast.walk(dispatch)
        if isinstance(node, ast.If) and "initiative_engine" in ast.dump(node.test)
    ]
    assert not guards, (
        "the dispatch now guards `initiative_engine` -- if that guard was added because the "
        "composition root stopped supplying it, the missing input is the defect, not the guard"
    )

    calls = [
        node
        for node in ast.walk(dispatch)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "record_trigger"
    ]
    assert calls, (
        "the dispatch no longer calls `record_trigger` -- this pin is measuring nothing, and the "
        "trigger would stop being recorded"
    )


def test_the_autonomous_loop_is_created_by_the_entry_point_not_the_composition_root() -> None:
    """The one absent input, and where it comes from.

    ``get_runtime()`` alone leaves ``autonomous_loop`` None: the loop is created by
    ``start_autonomous_if_enabled``, and the *entry points* call it. Pinned structurally so the
    fact survives a rename of either half -- and so the test harness's ``None`` is not misread as
    a production fact (``autonomous_loop_enabled`` defaults to True).
    """
    starter = _function(_runtime_tree(), "start_autonomous_if_enabled")

    gate = [
        node
        for node in ast.walk(starter)
        if isinstance(node, ast.If) and "autonomous_loop_enabled" in ast.dump(node.test)
    ]
    assert gate, (
        "start_autonomous_if_enabled no longer gates on `autonomous_loop_enabled` -- the "
        "'created by the entry point, gated on the flag' record is stale"
    )

    creation = [
        node
        for node in ast.walk(starter)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_create_autonomous_loop"
    ]
    assert creation, (
        "the loop creation left `start_autonomous_if_enabled` -- the lazy-creation record moved, "
        "and this file's header has to move with it"
    )
