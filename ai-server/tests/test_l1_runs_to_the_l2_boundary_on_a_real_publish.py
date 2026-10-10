"""Cycle 138 pin: a production publish runs the *real* L1 pipeline to the L2 boundary.

The event-driven path had been pinned link by link -- which rules can fire (cycle 133),
the bus -> trigger engine delivery (134), the two L1 subscriptions and their filters (135)
-- but every one of those stopped at *delivery*. Cycle 135 deliberately spied the two
downstream entries (``_submit_background_l1`` / ``_run_l1_pipeline_for_event``), so it
measured that a publish *reaches* the route, not that L1 *runs*. The boundary pin
(``tests/test_l1_reaches_the_l2_boundary.py``) drives the decision, but on a **fake**
runtime with ``_run_l1_pipeline_for_event`` replaced.

Nothing joined the two: no test published through the production bus and let the real L1
pipeline run to the point where it hands off to L2. That is the property this file pins --
"L1 works, and reaches just before L2", through the composition root.

Measured 2026-10-10 (HEAD 1eac195), real ``get_runtime()`` with the empty-key provider
(``LLM_API_KEY=""``, so L1 decides from the Mock/local fallback):

* ``social.inbox.received`` (immediate route) -> L1 runs **off the publisher thread**
  (``_submit_background_l1`` -> a single worker) -> decision action ``observe`` -> the
  immediate route calls ``_run_l2_pipeline`` **once** with ``trigger="social.inbox.received"``
  and a ``detail["l1"]`` projection. This is the headline: L1 reached the L2 boundary.
* ``pc.metric.sampled`` (background route) -> L1 runs **inline** on the publisher thread
  (no ``_background_l1_executor`` is created) -> decision action ``ignore`` -> the
  background route's gate (``action_value in {"escalate", "observe"}``, ``runtime.py:1759``)
  **drops** it, so ``_submit_background_l2`` is not called.
* ``presentation.*`` / ``l1.*`` (excluded) -> L1 never runs at all (the filter gates).

⚠️ The two routes gate the L2 boundary **differently**: the immediate route forwards
everything except ``ignore`` / ``capability`` (``runtime.py:895-919``), while the background
route forwards only ``escalate`` / ``observe`` (``runtime.py:1759``). For the measured pair
(``observe`` vs ``ignore``) they agree; the asymmetry only shows for other action types, so
the background test asserts the *gate relation*, not the LLM's choice.

The probe replaces ``_run_l2_pipeline`` / ``_submit_background_l2`` / ``_run_l1_pipeline_for_event``
**by name**, so a rename turns ``test_the_probe_replaces_the_three_entries`` red instead of
silently making every assertion below vacuous.
"""

from __future__ import annotations

from typing import Any

import pytest

import aegis_ai.runtime as runtime_module

_IMMEDIATE_TYPE = "social.inbox.received"
_BACKGROUND_TYPE = "pc.metric.sampled"
_EXCLUDED_TYPES = ("l1.observation", "presentation.c138_probe")

#: The background route's boundary gate (``runtime.py:1759``).
_BACKGROUND_FORWARDS = {"escalate", "observe"}

_ALL_SERVERS = "ai-server,pc-server,browser-server,android-server,room-server,dashboard"


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    yield

    from aegis_ai.runtime import reset_runtime_for_tests

    reset_runtime_for_tests()


@pytest.fixture
def real_runtime(monkeypatch, tmp_path) -> Any:
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AEGIS_DISABLED_SERVERS", _ALL_SERVERS)

    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    reset_runtime_for_tests()
    return get_runtime()


def _drain_l1(runtime: Any) -> None:
    """Wait for the immediate route's single background worker to finish."""
    executor = getattr(runtime, "_background_l1_executor", None)
    if executor is not None:
        executor.shutdown(wait=True)


def _publish(runtime: Any, event_type: str) -> None:
    from aegis_ai.event.helpers import build_event

    runtime.event_manager.publish(build_event(event_type))


class _Boundary:
    """Spies on the L2 boundary and on every *real* L1 run, so a publish is fully observable."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.l1_runs: list[tuple[str, str]] = []  # (event_type, action) per real L1 run
        self.l2_direct: list[tuple[str, bool]] = []  # _run_l2_pipeline (immediate route)
        self.l2_submitted: list[str] = []  # _submit_background_l2 (background route)

        original = runtime_module._run_l1_pipeline_for_event

        def wrap(runtime_: Any, event: Any) -> Any:
            decision = original(runtime_, event)
            action = getattr(getattr(decision, "action", None), "type", "")
            self.l1_runs.append(
                (str(getattr(event, "event_type", "") or ""), str(getattr(action, "value", action)))
            )
            return decision

        def fake_l2(runtime_: Any, *, trigger: str, detail: dict) -> dict:
            self.l2_direct.append((trigger, "l1" in detail))
            return {"handled": False, "action_type": "noop"}

        def fake_submit_l2(runtime_: Any, *, trigger: str, detail: dict) -> None:
            self.l2_submitted.append(trigger)

        monkeypatch.setattr(runtime_module, "_run_l1_pipeline_for_event", wrap)
        monkeypatch.setattr(runtime_module, "_run_l2_pipeline", fake_l2)
        monkeypatch.setattr(runtime_module, "_submit_background_l2", fake_submit_l2)

    def action(self, event_type: str) -> str:
        return {t: a for t, a in self.l1_runs}[event_type]


def test_the_probe_replaces_the_three_entries(monkeypatch) -> None:
    """Guard the guard: the probe must be attached to the module the pipeline reads."""
    _Boundary(monkeypatch)
    assert runtime_module._run_l1_pipeline_for_event is not _Boundary  # sanity
    assert runtime_module._run_l1_pipeline_for_event.__name__ == "wrap", (
        "the L1 pipeline was not replaced -- the boundary assertions below would be vacuous"
    )


def test_the_real_runtime_has_the_l2_boundary(real_runtime) -> None:
    """Non-vacuity: without both halves, the immediate route cannot reach L2 at all."""
    assert real_runtime.l2_mind is not None, (
        "the real runtime has no l2_mind -- the immediate route's boundary call can never run"
    )
    assert real_runtime.initiative_engine is not None, (
        "the real runtime has no initiative_engine -- the route's notifications are unreachable"
    )


def test_a_published_immediate_event_runs_l1_and_reaches_the_l2_boundary(
    real_runtime, monkeypatch
) -> None:
    """The headline: a production publish runs the real L1 pipeline up to the L2 hand-off."""
    boundary = _Boundary(monkeypatch)
    _publish(real_runtime, _IMMEDIATE_TYPE)
    _drain_l1(real_runtime)

    assert [t for t, _ in boundary.l1_runs] == [_IMMEDIATE_TYPE], (
        "a published immediate event did not run the L1 pipeline -- the route, its worker or "
        "the bus is dead"
    )
    assert boundary.l2_direct == [(_IMMEDIATE_TYPE, True)], (
        "L1 ran but did not reach the L2 boundary with detail['l1'] -- "
        f"got {boundary.l2_direct!r}"
    )


def test_the_immediate_run_is_off_the_publisher_thread(real_runtime, monkeypatch) -> None:
    """Item 48: the immediate route hands L1 to a single background worker, not the publisher."""
    boundary = _Boundary(monkeypatch)
    _publish(real_runtime, _IMMEDIATE_TYPE)

    assert getattr(real_runtime, "_background_l1_executor", None) is not None, (
        "the immediate route did not create the background L1 worker -- it ran L1 inline on "
        "the publisher's thread (item 48 regressed)"
    )
    _drain_l1(real_runtime)
    assert [t for t, _ in boundary.l1_runs] == [_IMMEDIATE_TYPE]


def test_a_published_background_event_runs_l1_inline_and_gates_the_boundary(
    real_runtime, monkeypatch
) -> None:
    """The background route is a *different* shape: inline L1, and a narrower boundary gate."""
    boundary = _Boundary(monkeypatch)
    _publish(real_runtime, _BACKGROUND_TYPE)
    _drain_l1(real_runtime)

    assert [t for t, _ in boundary.l1_runs] == [_BACKGROUND_TYPE], (
        "a published background event did not run the L1 pipeline"
    )
    assert getattr(real_runtime, "_background_l1_executor", None) is None, (
        "the background route created the immediate route's worker -- the two routes are not "
        "distinct"
    )
    action = boundary.action(_BACKGROUND_TYPE)
    if action in _BACKGROUND_FORWARDS:
        assert boundary.l2_submitted == [_BACKGROUND_TYPE], (
            f"L1 decided {action!r} but the background route did not hand off to L2"
        )
    else:
        assert boundary.l2_submitted == [], (
            f"L1 decided {action!r} but the background route still handed off to L2"
        )


def test_an_excluded_event_never_runs_l1(real_runtime, monkeypatch) -> None:
    """Control: an excluded prefix never reaches L1, so the positives are not noise."""
    boundary = _Boundary(monkeypatch)
    for event_type in _EXCLUDED_TYPES:
        _publish(real_runtime, event_type)
    _drain_l1(real_runtime)

    assert boundary.l1_runs == [], f"an excluded type ran the L1 pipeline: {boundary.l1_runs!r}"
    assert boundary.l2_direct == [], f"an excluded type reached L2 directly: {boundary.l2_direct!r}"
    assert boundary.l2_submitted == [], (
        f"an excluded type reached L2 via the background route: {boundary.l2_submitted!r}"
    )


def test_the_excluded_probe_types_stay_excluded() -> None:
    """The finding, purely: the probe types route exactly as the predicates claim."""
    for event_type in _EXCLUDED_TYPES:
        assert not runtime_module._should_route_to_l1_immediate(event_type)
        assert not runtime_module._should_route_to_l1_background(event_type)
    assert _IMMEDIATE_TYPE in runtime_module._L1_IMMEDIATE_EVENT_TYPES
    assert runtime_module._should_route_to_l1_background(_BACKGROUND_TYPE)
