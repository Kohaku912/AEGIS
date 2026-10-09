"""``EventView.get_pending_tasks`` calls itself a *view* -- and drains the trigger engine.

``EventView`` (``observability/event_view.py``) is documented as a "Read-only view of EventBus
for dashboard display". Three of its four accessors are read-only: ``get_recent_events`` and
``get_stats`` read the bus, ``get_trigger_stats`` reads ``engine.stats``. The fourth,
``get_pending_tasks``, is **destructive** -- it calls ``engine.drain_tasks()``, which clears the
queue (``trigger_engine.py``), and it never puts the tasks back, although its own comment says
"Re-add them since drain clears the queue".

The same queue has a second, *coordinated* consumer: ``AutonomousLoop._drain_trigger_tasks``
(``autonomous/autonomous_loop.py``) drains it once per cycle, and its docstring spells out why --
"``drain_tasks()`` clears the queue -- draining into a cycle that then does not execute would
discard the tasks without a trace". So the loop knows the read is destructive; the view does not.

Measured 2026-10-10 (cycle 136): one task queued -> ``view.get_pending_tasks()`` returns it ->
``engine.pending_task_count()`` is **0** and a following ``drain_tasks()`` returns ``[]``. The
loop would find nothing. The other three accessors leave the queue at **1**.

Nothing calls the method today (``EventView`` itself has no ``src/`` consumer -- pinned by
``test_event_driven_core_is_constructed.py``, cycle 69), so this is latent: the first dashboard
route wired to ``event_view.get_pending_tasks()`` would silently starve the autonomous loop.
This file fixes the **current** behaviour so changing it has to be deliberate; the owner decision
is recorded in ``DELEGATION.md`` section 4.

The production-shaped test publishes an **L1-excluded** probe type (as
``test_a_published_event_reaches_the_trigger_engine.py`` does): it reaches the trigger engine
(subscribed with no filter) without entering the L1/L2 pipeline, so the probe measures the
view/loop competition and nothing else. Publishing an L1-routed type here would instead start a
real L2 worker whose audit write races the runtime's shutdown -- a *different* defect, recorded
as ``DELEGATION.md`` section 4 item 96.
"""

from __future__ import annotations

from typing import Any

import pytest

#: A synthetic rule on an L1-excluded type: the engine sees it, the L1/L2 pipeline does not.
_PROBE_RULE = "c136-probe"
_PROBE_TYPE = "presentation.c136_probe"


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


def _queued_engine() -> Any:
    """A real engine with exactly one queued task, from a rule that cannot cooldown-suppress."""
    from aegis_ai.event.helpers import build_event
    from trigger_engine import TriggerEngine, TriggerRule

    engine = TriggerEngine()
    engine.add_rule(
        TriggerRule(rule_id=_PROBE_RULE, event_type_pattern=_PROBE_TYPE, cooldown_seconds=0.0)
    )
    engine.on_event(build_event(_PROBE_TYPE))
    return engine


def _view(engine: Any) -> Any:
    from aegis_ai.observability.event_view import EventView

    return EventView(event_bus=None, trigger_engine=engine)


# ── the finding ─────────────────────────────────────────────────────────────────────────


def test_get_pending_tasks_returns_the_queued_tasks() -> None:
    """Non-vacuity: the view does return the task, so the destructive assertion below has teeth."""
    engine = _queued_engine()
    assert engine.pending_task_count() == 1, "the probe did not queue a task"
    got = _view(engine).get_pending_tasks()
    assert [t["triggered_by_rule_id"] for t in got] == [_PROBE_RULE]


def test_get_pending_tasks_consumes_the_queue() -> None:
    """The finding: a "read" leaves the engine's queue empty."""
    engine = _queued_engine()
    _view(engine).get_pending_tasks()
    assert engine.pending_task_count() == 0, (
        "get_pending_tasks no longer drains the queue -- if the read was made non-destructive, "
        "update DELEGATION.md section 4 and this file together"
    )


def test_the_consumed_tasks_are_not_readded() -> None:
    """The comment's claim is false: nothing re-adds the drained tasks."""
    engine = _queued_engine()
    view = _view(engine)
    view.get_pending_tasks()
    assert view.get_pending_tasks() == [], "a second read returned tasks -- they were re-added"
    assert engine.drain_tasks() == [], "the loop's own drain found tasks -- they were re-added"


# ── controls ────────────────────────────────────────────────────────────────────────────


def test_the_other_accessors_and_a_bare_view_are_inert() -> None:
    """Control: the read-only accessors leave the queue, and a bare ``EventView()`` is safe.

    Without this, a class that drained on *every* accessor would look the same, and the bare
    view's ``if not self._engine`` guard (the only path any test used to exercise) would be
    unpinned.
    """
    from aegis_ai.observability.event_view import EventView

    engine = _queued_engine()
    view = _view(engine)
    view.get_stats()
    view.get_trigger_stats()
    view.get_recent_events()
    assert engine.pending_task_count() == 1, "a read-only accessor consumed the queue"

    assert EventView().get_pending_tasks() == [], "a bare EventView() is not inert"
    assert EventView().get_stats() == {}
    assert EventView().get_trigger_stats() == {}


# ── the production shape ────────────────────────────────────────────────────────────────


def test_a_published_event_is_consumed_by_the_view_not_the_loop(real_runtime) -> None:
    """End to end on the real runtime: the view holds the engine the loop drains, so it steals.

    The runtime builds one ``EventView`` over one ``TriggerEngine``, and the autonomous loop
    drains that same engine. A published event that matches a rule lands in the queue; reading it
    through the view empties the queue the loop would otherwise consume.
    """
    from aegis_ai.event.helpers import build_event
    from trigger_engine import TriggerRule

    engine = real_runtime.trigger_engine
    assert real_runtime.event_view is not None, "the runtime did not build an EventView"
    assert real_runtime.event_view._engine is engine, (
        "the runtime's EventView does not hold the engine the loop drains"
    )

    if engine.get_rule(_PROBE_RULE) is None:
        engine.add_rule(
            TriggerRule(rule_id=_PROBE_RULE, event_type_pattern=_PROBE_TYPE, cooldown_seconds=0.0)
        )
    engine.reset_all_cooldowns()
    engine.drain_tasks()

    real_runtime.event_manager.publish(build_event(_PROBE_TYPE))
    assert engine.pending_task_count() >= 1, "the publish queued no task"

    stolen = real_runtime.event_view.get_pending_tasks()
    assert [t["triggered_by_rule_id"] for t in stolen] == [_PROBE_RULE]
    assert engine.drain_tasks() == [], (
        "the loop's drain still found the task -- the view did not steal it"
    )
