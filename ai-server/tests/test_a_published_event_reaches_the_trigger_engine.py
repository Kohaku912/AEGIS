"""The trigger engine is subscribed to the bus -- but no test ever published to it.

Cycles 24, 132 and 133 each pinned one half of "event-driven", and each stopped short of the
link that actually carries an event to the engine:

* cycle 24 (``test_event_driven_core_is_constructed.py``) pins that the core is *constructed*
  and that the loop *reads* ``trigger_engine`` -- all ``ast``-level;
* cycle 132 (``test_the_autonomous_loop_is_actually_built.py``) runs the loop body and drains
  the engine, but queues the task by calling ``engine.on_event(event)`` **directly**;
* cycle 133 (``test_trigger_rules_name_produced_events.py``) pins which rules *can* fire.

None of them drove a real ``EventBus.publish(...)`` into the subscribed engine. That is the
exact shape of ``DELEGATION.md`` section 4 item 26: a subscriber whose handler signature did
not match how the bus calls it was **never invoked**, and the subscriber count still looked
right. A green construction pin and a green drain pin cannot see that -- only a real publish can.

Measured 2026-10-10 (cycle 134) on the real composition root: ``_build_runtime`` subscribes
``trigger_engine.on_event`` to the production ``event_manager``; ``EventManager.publish``
delegates to ``EventBus.publish``, which calls ``handler(event)`` -- one argument, matching
``TriggerEngine.on_event(self, event)``. Publishing through the real manager reaches the engine
and, for a matching rule, generates a task the loop can drain.

The delivery tests publish a **probe rule** on an L1-excluded event type, so the delivery is
observable without running the L1/L2 pipeline: ``_should_route_to_l1_background`` drops the
``l1.`` / ``l2.`` / ``l3.`` / ``presentation.`` prefixes, while the trigger engine is subscribed
with **no filter** and still receives them. The live rule's *match* is asserted separately and
purely, against the event ``pc_server_client.push_screen_changed_event`` actually builds -- so
the pin never needs an LLM round trip to prove the hand-off.
"""

from __future__ import annotations

from typing import Any

import pytest

#: A synthetic rule + an L1-excluded type: the engine sees it, the L1 routes do not.
_PROBE_RULE = "c134-probe"
_PROBE_TYPE = "presentation.c134_probe"
_PROBE_CONTROL = "presentation.c134_other"

#: The one default rule with a producer anywhere in the repo (cycle 133).
_LIVE_RULE = "pc-screen-change"
_LIVE_TYPE = "pc.screen_changed"


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    """Boot the real runtime, but never leave it running.

    Same reason as ``test_runtime_singleton.py``: ``get_runtime()`` starts a ``status-check``
    daemon that probes the real LAN and writes into the endpoint resolver's process-global cache.
    """
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


def _add_probe(engine) -> None:
    from trigger_engine import TriggerRule

    if engine.get_rule(_PROBE_RULE) is None:
        engine.add_rule(
            TriggerRule(rule_id=_PROBE_RULE, event_type_pattern=_PROBE_TYPE, cooldown_seconds=0.0)
        )


def test_the_runtime_records_a_subscription_for_the_engine(real_runtime) -> None:
    """Structural: the composition root holds a live subscription id for the engine."""
    assert real_runtime.trigger_engine is not None, "the runtime did not build the trigger engine"
    assert getattr(real_runtime, "_trigger_event_subscription", None), (
        "the runtime did not record a subscription id -- _build_runtime no longer subscribes "
        "trigger_engine.on_event to the bus"
    )


def test_a_published_event_reaches_the_engine(real_runtime) -> None:
    """The delivery: a real publish through the production bus is *received* by the engine.

    If the subscription were removed, or the bus called the handler with the wrong arity
    (section 4 item 26), the engine would never see the event and this counter would not move.
    """
    from aegis_ai.event.helpers import build_event

    engine = real_runtime.trigger_engine
    _add_probe(engine)
    before = engine.stats.events_received
    real_runtime.event_manager.publish(build_event(_PROBE_TYPE))
    assert engine.stats.events_received > before, (
        "a published event did not reach the trigger engine -- the subscription is dead"
    )


def test_a_matched_published_event_generates_a_drainable_task(real_runtime) -> None:
    """End to end: publish -> bus -> engine -> queue -> drain."""
    from aegis_ai.event.helpers import build_event

    engine = real_runtime.trigger_engine
    _add_probe(engine)
    engine.reset_all_cooldowns()
    engine.drain_tasks()
    before = engine.stats.tasks_generated
    real_runtime.event_manager.publish(build_event(_PROBE_TYPE))
    assert engine.stats.tasks_generated == before + 1, (
        "the probe rule did not fire from a *published* event"
    )
    assert [t.triggered_by_rule_id for t in engine.drain_tasks()] == [_PROBE_RULE], (
        "the drained task does not name the probe rule"
    )


def test_an_unmatched_published_event_generates_no_task(real_runtime) -> None:
    """Control: an event the probe rule does not name is still received, but makes no task."""
    from aegis_ai.event.helpers import build_event

    engine = real_runtime.trigger_engine
    _add_probe(engine)
    engine.reset_all_cooldowns()
    engine.drain_tasks()
    recv, gen = engine.stats.events_received, engine.stats.tasks_generated
    real_runtime.event_manager.publish(build_event(_PROBE_CONTROL))
    assert engine.stats.events_received > recv, (
        "the control event was not delivered -- the delivery test above is vacuous"
    )
    assert engine.stats.tasks_generated == gen, "an event no rule names still generated a task"


def test_the_one_live_rule_matches_the_production_shaped_event(real_runtime) -> None:
    """The finding, purely: exactly one default rule matches the event the PC client builds."""
    from aegis_ai.event.helpers import build_event
    from aegis_schema.models import EventPriority, ServerType

    event = build_event(
        _LIVE_TYPE,
        source_server_type=ServerType.PC,
        source_server_id="pc-server",
        severity=2,
        priority=EventPriority.NORMAL,
    )
    matched = [r.rule_id for r in real_runtime.trigger_engine.list_rules() if r.matches(event)]
    assert matched == [_LIVE_RULE], f"the live rule set moved: {matched}"
