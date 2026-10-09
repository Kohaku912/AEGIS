"""The background L1 route's post-decide dispatch -- measured, and now pinned.

``tests/test_l1_reaches_the_l2_boundary.py`` pins the **immediate** route's dispatch
(``_run_l1_immediate_pipeline``) by driving it with a ``SimpleNamespace`` runtime. The
**background** route (``_handle_background_l1_event``, subscribed at ``runtime.py:1786``)
was never pinned at all: ``tests/test_l1_runs_off_the_publisher_thread.py`` pins only that
it still runs *inline* and *calls the pipeline* -- not what it does with the decision.

The handler is a closure inside ``_build_runtime``, so it cannot be imported. This file
reaches it the only honest way -- through the real bus the composition root wires it on --
and drives it with a scripted router, mirroring the immediate-route file.

Measured 2026-10-09 (cycle 123) on ``get_runtime()``. The rules the code implements:

  action ``escalate`` / ``observe``  -> ``_submit_background_l2`` **once**, carrying the
                                        event type and the ``detail["l1"]`` projection.
                                        The submit is **asynchronous** and its result is
                                        discarded (``_submit_background_l2``'s docstring);
                                        so this is the *decision* to hand off, measured by
                                        patching the submitter, not by watching L2 run.
  action ``ignore`` / ``capability`` / ``noop`` -> return: no L2 hand-off, nothing else.
  **any** action                     -> ``initiative_engine.record_trigger`` and
                                        ``autonomous_loop.evaluate_event`` are **never**
                                        called.

⚠️ The last line is the asymmetry worth knowing. The immediate route's terminal step is a
notification (``record_trigger`` for ``capability`` and for a handled L2 result, plus
``evaluate_event`` when unhandled); the background route notifies **nothing** -- it is
fire-and-forget. A ``capability`` decision therefore *executes the capability* on both
routes but reaches the initiative engine on only one. Recorded as ``DELEGATION.md``
section 4 item 85; the pin below fixes the **current** behaviour so changing it has to be
deliberate (if the record is closed one way, update this file with it).

Controls, so the "no L2" assertions cannot pass for the wrong reason:

* ``test_the_probe_replaces_the_l2_submitter`` -- the patch really landed (a rename of the
  submitter turns this red instead of making every assertion vacuous).
* ``test_the_non_vacuity_floor`` -- at least one branch must reach the submitter.
* ``test_the_event_type_routes_to_the_background_subscription`` -- the drive uses a type the
  real partition actually routes to the background route, not one the immediate route takes.
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import aegis_ai.runtime as runtime_module

_RUNTIME_PY = Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "runtime.py"

_SUBMITTER = "_submit_background_l2"
_BACKGROUND_HANDLER = "_handle_background_l1_event"
_IMMEDIATE_DISPATCH = "_run_l1_immediate_pipeline"

#: A type the partition routes to the *background* route (not in
#: ``_L1_IMMEDIATE_EVENT_TYPES``, no excluded prefix).
_EVENT_TYPE = "pc.metric.sampled"

#: The two action types the background route forwards; the other three stop it.
_FORWARDED = ("escalate", "observe")
_DROPPED = ("ignore", "capability", "noop")


# ── fixtures ──────────────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    """Boot the real runtime, but never leave it running (same reason as ``test_runtime_singleton``)."""
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


# ── the probe ─────────────────────────────────────────────────────────────────────────


class _Recorder:
    """A stand-in for the initiative engine / autonomous loop that records calls."""

    def __init__(self, calls: list[str]) -> None:
        self._calls = calls

    def record_trigger(self, event_type: str, detail: dict[str, Any] | None = None) -> None:
        self._calls.append(f"record_trigger:{event_type}")

    def evaluate_event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        self._calls.append(f"evaluate_event:{event_type}")


class _Probe:
    """Drives the *real* wired background handler and records what it did."""

    def __init__(self, runtime: Any, monkeypatch: Any) -> None:
        self.runtime = runtime
        self.l2_submits: list[dict[str, Any]] = []
        self.l2_inline: list[str] = []
        self.notices: list[str] = []

        def _fake_submit(runtime_: Any, *, trigger: str, detail: dict[str, Any]) -> None:
            self.l2_submits.append({"trigger": trigger, "detail": detail})

        def _fake_l2(runtime_: Any, *, trigger: str, detail: dict[str, Any]) -> dict[str, Any]:
            # The background route must NOT call the pipeline directly -- it submits.
            self.l2_inline.append(trigger)
            return {"handled": True, "action_type": "act"}

        monkeypatch.setattr(runtime_module, _SUBMITTER, _fake_submit)
        monkeypatch.setattr(runtime_module, "_run_l2_pipeline", _fake_l2)

        # The capability branch would otherwise *execute* a real capability (a network
        # round-trip); the decision under test is the dispatch, not the execution.
        runtime.l1_executor = None

        self._recorder = _Recorder(self.notices)
        runtime.initiative_engine = self._recorder
        runtime.autonomous_loop = self._recorder

        self.handler = self._find_background_handler(runtime)

    @staticmethod
    def _find_background_handler(runtime: Any) -> Any:
        subs = runtime.event_manager._bus._subscriptions
        for sub in subs:
            if getattr(sub.handler, "__name__", "") == _BACKGROUND_HANDLER:
                return sub.handler
        raise AssertionError(
            f"{_BACKGROUND_HANDLER} is not subscribed on the real bus -- the handler was "
            "renamed or the wiring moved; update DELEGATION.md section 4 item 48/85 and this file"
        )

    def _install_router(self, action_type: str) -> None:
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
                action=L1Action(
                    type=L1ActionType(action_type),
                    reason="scripted",
                    capability_id="pc-server.screenshot.get_screenshot",
                    args={"display": 0},
                ),
                reasoning="scripted",
                observation=observation,
            )

        def escalate(observation: Any, *, reason: str = "") -> Any:
            return SimpleNamespace(
                to_payload=lambda: {"event_id": "evt-bg-1", "reason": reason, "layer": "L1"}
            )

        self.runtime.l1_router.observe = observe
        self.runtime.l1_router.decide = decide
        self.runtime.l1_router.escalate = escalate

    def run(self, action_type: str) -> None:
        self.l2_submits.clear()
        self.l2_inline.clear()
        self.notices.clear()
        self._install_router(action_type)
        self.handler(_event())


def _event() -> SimpleNamespace:
    return SimpleNamespace(
        event_id="evt-bg-1",
        event_type=_EVENT_TYPE,
        payload_json='{"app":"vscode"}',
        timestamp_ms=1,
        source_server_id="pc-server",
        source_server_type=SimpleNamespace(name="PC"),
    )


# ── controls ──────────────────────────────────────────────────────────────────────────


def test_the_event_type_routes_to_the_background_subscription() -> None:
    """The drive uses a type the real partition sends to the background route."""
    assert runtime_module._should_route_to_l1_background(_EVENT_TYPE), (
        f"{_EVENT_TYPE!r} is not background-routed -- this file would drive the wrong route"
    )
    assert not runtime_module._should_route_to_l1_immediate(_EVENT_TYPE), (
        f"{_EVENT_TYPE!r} is on the immediate route -- the partition moved; pick a new type"
    )


def test_the_probe_replaces_the_l2_submitter(real_runtime, monkeypatch) -> None:
    """Control: if the submitter is renamed or moved, this fails instead of going quiet."""
    original = getattr(runtime_module, _SUBMITTER)
    _Probe(real_runtime, monkeypatch)
    assert getattr(runtime_module, _SUBMITTER) is not original, (
        f"the probe did not replace {_SUBMITTER} -- every L2 assertion in this file would be vacuous"
    )


def test_the_non_vacuity_floor(real_runtime, monkeypatch) -> None:
    """At least one branch must reach the submitter, or the "no L2" cases prove nothing."""
    probe = _Probe(real_runtime, monkeypatch)
    probe.run("escalate")
    assert len(probe.l2_submits) == 1, (
        "the escalate branch never reached the L2 submitter -- the probe is vacuous"
    )


# ── the dispatch table ────────────────────────────────────────────────────────────────


def test_the_background_dispatch_table(real_runtime, monkeypatch) -> None:
    """One boot, all five action types: the measured table, asserted row by row."""
    probe = _Probe(real_runtime, monkeypatch)

    for action in _FORWARDED:
        probe.run(action)
        assert len(probe.l2_submits) == 1, (
            f"action={action!r} must hand the event to L2 exactly once; got {probe.l2_submits!r}"
        )
        submit = probe.l2_submits[0]
        assert submit["trigger"] == _EVENT_TYPE, (
            f"the hand-off must carry the event type; got {submit['trigger']!r}"
        )
        assert submit["detail"]["l1"]["action_type"] == action, (
            "the detail handed to L2 must carry the L1 projection (action_type)"
        )
        assert submit["detail"]["l1"]["meaning"] == "user switched to the editor", (
            "the L1 projection must carry the observation's meaning, not just the action"
        )
        assert probe.l2_inline == [], (
            "the background route must *submit* to L2, not call the pipeline inline"
        )

    for action in _DROPPED:
        probe.run(action)
        assert probe.l2_submits == [], (
            f"action={action!r} must stop before L2; got {probe.l2_submits!r}"
        )
        assert probe.l2_inline == [], (
            f"action={action!r} must not call the L2 pipeline either; got {probe.l2_inline!r}"
        )


def test_the_background_route_notifies_neither_the_initiative_engine_nor_the_loop(
    real_runtime, monkeypatch
) -> None:
    """The asymmetry: unlike the immediate route, the background route notifies nothing.

    ``initiative_engine.record_trigger`` and ``autonomous_loop.evaluate_event`` are called
    only from ``_run_l1_immediate_pipeline`` (runtime.py:918/924/926/929). On the background
    route the whole dispatch is L1 -> (maybe) async L2 -> nothing, so a ``capability``
    decision executes the capability but reaches the initiative engine nowhere. Recorded as
    ``DELEGATION.md`` section 4 item 85; pinned here so a change is deliberate.
    """
    probe = _Probe(real_runtime, monkeypatch)
    for action in (*_FORWARDED, *_DROPPED):
        probe.run(action)
        assert probe.notices == [], (
            f"action={action!r} notified something; the background route is fire-and-forget "
            f"(observed {probe.notices!r}) -- if this is now intended, update item 85 and this file"
        )


# ── the asymmetry, structurally (no boot) ─────────────────────────────────────────────


def _function(name: str) -> ast.FunctionDef:
    tree = ast.parse(_RUNTIME_PY.read_text(encoding="utf-8"), filename=str(_RUNTIME_PY))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} is no longer defined in runtime.py")


def _called_attrs(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            names.add(n.func.attr)
    return names


def test_the_terminal_step_differs_between_the_two_routes() -> None:
    """Structural half: ``record_trigger`` is in the immediate dispatch, absent from the background handler.

    The behavioural test above needs a booted runtime; this one does not, so the asymmetry
    stays pinned even if the wiring is renamed. The first assertion is the control that the
    second is not vacuous.
    """
    immediate = _called_attrs(_function(_IMMEDIATE_DISPATCH))
    assert "record_trigger" in immediate, (
        "the immediate dispatch no longer calls `record_trigger` -- this pin is measuring nothing"
    )

    background = _called_attrs(_function(_BACKGROUND_HANDLER))
    assert "record_trigger" not in background, (
        "the background handler now calls `record_trigger` -- the asymmetry changed; update "
        "DELEGATION.md section 4 item 85 and the behavioural test above"
    )
    assert "evaluate_event" not in background, (
        "the background handler now calls `evaluate_event` -- update item 85 and this file"
    )
