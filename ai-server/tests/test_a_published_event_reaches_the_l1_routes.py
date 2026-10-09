"""The L1 routes are subscribed to the bus -- but no test ever published to them.

Cycle 134 pinned the trigger engine's *delivery* (a real ``event_manager.publish`` reaching a
subscriber). The other two subscriptions on the same bus -- the L1 routes -- were left in the
same shape they had been all along: the pins reach the handler and call it **directly**.

* ``tests/test_background_l1_dispatch_reaches_or_stops_before_l2.py`` (cycle 123) finds
  ``_handle_background_l1_event`` by walking ``runtime.event_manager._bus._subscriptions`` and
  then calls ``self.handler(_event())`` -- it never publishes;
* ``tests/test_l1_runs_off_the_publisher_thread.py`` is ``ast``-level, plus one direct call to
  ``_submit_background_l1`` with a fake runtime;
* ``tests/test_l1_reaches_the_l2_boundary.py`` drives ``_run_l1_immediate_pipeline`` directly.

So the *filter* half of these two subscriptions was never exercised. The bus applies each
subscription's filter before calling its handler (``event_bus.py`` ``_notify_subscribers``:
``if sub.event_filter is None or sub.event_filter(event): sub.handler(event)``). A handler
reached by name and called directly sees neither the filter nor the bus's notify path -- if the
filter lambda were dropped from the ``subscribe`` call, the L1 routes would receive *every*
event (including their own ``l1.*`` output and the ``presentation.*`` stream), and every
existing pin would stay green.

Measured 2026-10-10 (cycle 135) on the real composition root: publishing through
``event_manager`` routes each event to exactly one L1 route --

    social.inbox.received   -> the immediate route only (``_submit_background_l1``)
    pc.metric.sampled       -> the background route only (``_run_l1_pipeline_for_event``)
    presentation.* / l1.*   -> neither (the filter blocks them)

The spies replace the two downstream calls so neither route runs its LLM pipeline; the probe
therefore measures *delivery and gating*, not the L1 decision.
"""

from __future__ import annotations

from typing import Any

import pytest

import aegis_ai.runtime as runtime_module

#: An immediate-routed type -- ``_L1_IMMEDIATE_EVENT_TYPES``' only member with a producer
#: (``social.inbox.received``; the count and partition are pinned by
#: ``tests/test_l1_immediate_triggers_have_producers.py``).
_IMMEDIATE_TYPE = "social.inbox.received"

#: A background-routed type (not in the immediate set, no excluded prefix).
_BACKGROUND_TYPE = "pc.metric.sampled"

#: Excluded by prefix: an L1 pipeline output, and the presentation stream.
_EXCLUDED_TYPES = ("l1.observation", "presentation.c135_probe")


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    """Boot the real runtime, but never leave it running (same reason as ``test_runtime_singleton``)."""
    yield

    from aegis_ai.runtime import reset_runtime_for_tests

    reset_runtime_for_tests()


@pytest.fixture
def real_runtime(monkeypatch, tmp_path) -> Any:
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))

    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    reset_runtime_for_tests()
    return get_runtime()


class _Routes:
    """Spies on the two L1 route entries, so a publish's delivery is observable."""

    def __init__(self, monkeypatch: Any) -> None:
        self.immediate: list[str] = []
        self.background: list[str] = []

        def fake_submit(runtime_: Any, *, event: Any) -> None:
            self.immediate.append(str(getattr(event, "event_type", "")))

        def fake_pipeline(runtime_: Any, event: Any) -> None:
            self.background.append(str(getattr(event, "event_type", "")))
            return None

        monkeypatch.setattr(runtime_module, "_submit_background_l1", fake_submit)
        monkeypatch.setattr(runtime_module, "_run_l1_pipeline_for_event", fake_pipeline)

    def publish(self, runtime: Any, event_type: str) -> None:
        from aegis_ai.event.helpers import build_event

        runtime.event_manager.publish(build_event(event_type))


def test_the_runtime_records_both_l1_subscriptions(real_runtime) -> None:
    """Structural: the composition root holds a live subscription id for each L1 route."""
    assert getattr(real_runtime, "_l1_event_subscription", None), (
        "the runtime did not record the background L1 subscription -- _build_runtime no longer "
        "subscribes _handle_background_l1_event to the bus"
    )
    assert getattr(real_runtime, "_initiative_event_subscription", None), (
        "the runtime did not record the immediate L1 subscription -- _build_runtime no longer "
        "subscribes _evaluate_immediate_event to the bus"
    )


def test_a_published_immediate_event_reaches_the_immediate_route(real_runtime, monkeypatch) -> None:
    """A real publish of an immediate type is delivered to the immediate route, and only it."""
    routes = _Routes(monkeypatch)
    routes.publish(real_runtime, _IMMEDIATE_TYPE)
    assert routes.immediate == [_IMMEDIATE_TYPE], (
        "a published immediate event did not reach _evaluate_immediate_event -- the subscription "
        "or its filter is dead"
    )
    assert routes.background == [], (
        "an immediate type also reached the background route -- the partition leaked"
    )


def test_a_published_background_event_reaches_the_background_route(real_runtime, monkeypatch) -> None:
    """A real publish of a background type is delivered to the background route, and only it."""
    routes = _Routes(monkeypatch)
    routes.publish(real_runtime, _BACKGROUND_TYPE)
    assert routes.background == [_BACKGROUND_TYPE], (
        "a published background event did not reach _handle_background_l1_event -- the "
        "subscription or its filter is dead"
    )
    assert routes.immediate == [], (
        "a background type also reached the immediate route -- the partition leaked"
    )


def test_an_excluded_event_reaches_neither_route(real_runtime, monkeypatch) -> None:
    """Control: the filter *gates* delivery -- an excluded prefix reaches no L1 route.

    Without this, a bus that called every handler regardless of its filter would look identical
    to a correctly wired one (every positive assertion above would still pass).
    """
    routes = _Routes(monkeypatch)
    for event_type in _EXCLUDED_TYPES:
        routes.publish(real_runtime, event_type)
    assert routes.immediate == [], (
        f"an excluded type reached the immediate route: {routes.immediate!r}"
    )
    assert routes.background == [], (
        f"an excluded type reached the background route: {routes.background!r}"
    )


def test_the_probe_types_partition_as_the_filters_say() -> None:
    """The finding, purely: the three probe types route exactly as the predicates claim."""
    immediate, background = runtime_module._should_route_to_l1_immediate, runtime_module._should_route_to_l1_background

    assert _IMMEDIATE_TYPE in runtime_module._L1_IMMEDIATE_EVENT_TYPES, (
        f"{_IMMEDIATE_TYPE!r} left the immediate vocabulary -- pick a live immediate type"
    )
    assert immediate(_IMMEDIATE_TYPE) and not background(_IMMEDIATE_TYPE)
    assert background(_BACKGROUND_TYPE) and not immediate(_BACKGROUND_TYPE)
    for event_type in _EXCLUDED_TYPES:
        assert not immediate(event_type) and not background(event_type), (
            f"{event_type!r} is excluded by prefix but a predicate admitted it"
        )
