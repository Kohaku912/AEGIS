"""``EventView.get_pending_tasks`` is a *view* -- and it no longer drains the trigger engine.

``EventView`` (``observability/event_view.py``) is documented as a "Read-only view of EventBus
for dashboard display". Three of its four accessors were already read-only; the fourth,
``get_pending_tasks``, **was destructive** -- it called ``engine.drain_tasks()``, which clears
the queue, and never put the tasks back, although its own comment claimed "Re-add them since
drain clears the queue" (measured 2026-10-10, cycle 136: one task queued -> the read left
``pending_task_count()`` at **0**, and the loop's own ``drain_tasks()`` returned ``[]``).

The same queue has a second, *coordinated* consumer: ``AutonomousLoop._drain_trigger_tasks``
drains it once per cycle, and its docstring spells out why -- "``drain_tasks()`` clears the
queue -- draining into a cycle that then does not execute would discard the tasks without a
trace". So the loop knows the read is destructive; the view did not.

Item 96 fixed (branch 1 = make the view read-only). ``TriggerEngine`` gains
``snapshot_tasks()`` -- a copy of the queue that does **not** clear it -- and
``get_pending_tasks`` calls that instead of ``drain_tasks()``. The pre-fix pin
(``test_the_event_view_read_is_destructive.py``) recorded the defect; this one measures the
fix, so the destructive read cannot come back unnoticed.

Nothing calls the method today (``EventView`` has no ``src/`` consumer -- pinned by
``test_event_driven_core_is_constructed.py``, cycle 69), so the fix changes no live behaviour:
it removes the latent hazard that the first dashboard route wired to
``event_view.get_pending_tasks()`` would silently starve the autonomous loop.

The production-shaped test publishes an **L1-excluded** probe type (as
``test_a_published_event_reaches_the_trigger_engine.py`` does): it reaches the trigger engine
(subscribed with no filter) without entering the L1/L2 pipeline, so the probe measures the
view/loop competition and nothing else. Publishing an L1-routed type here would instead start a
real L2 worker whose audit write races the runtime's shutdown -- a *different* defect, recorded
as ``DELEGATION.md`` section 4 item 97.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

import trigger_engine as trigger_engine_module

#: A synthetic rule on an L1-excluded type: the engine sees it, the L1/L2 pipeline does not.
_PROBE_RULE = "c146-probe"
_PROBE_TYPE = "presentation.c146_probe"


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


# ── the fixed property (driven) ───────────────────────────────────────────────────────────


def test_get_pending_tasks_returns_the_queued_tasks() -> None:
    """Non-vacuity: the view still returns the task, so the non-destructive claim has teeth."""
    engine = _queued_engine()
    assert engine.pending_task_count() == 1, "the probe did not queue a task"
    got = _view(engine).get_pending_tasks()
    assert [t["triggered_by_rule_id"] for t in got] == [_PROBE_RULE]


def test_get_pending_tasks_does_not_consume_the_queue() -> None:
    """The fix: a "read" leaves the engine's queue intact -- the opposite of the old pin."""
    engine = _queued_engine()
    _view(engine).get_pending_tasks()
    assert engine.pending_task_count() == 1, (
        "get_pending_tasks drained the queue -- the item-96 starvation is back; re-measure "
        "before changing this"
    )


def test_a_second_read_returns_the_same_tasks() -> None:
    """A snapshot is idempotent: reading twice yields the same task (it was never removed)."""
    engine = _queued_engine()
    view = _view(engine)
    first = view.get_pending_tasks()
    second = view.get_pending_tasks()
    assert [t["task_id"] for t in first] == [t["task_id"] for t in second]
    assert engine.pending_task_count() == 1


def test_the_loop_can_still_drain_after_a_view_read() -> None:
    """The whole point: the coordinated consumer (the loop) still finds the task."""
    engine = _queued_engine()
    _view(engine).get_pending_tasks()
    drained = engine.drain_tasks()
    assert [t.triggered_by_rule_id for t in drained] == [_PROBE_RULE], (
        "the loop's drain found nothing after a view read -- the view stole the task"
    )


# ── controls ──────────────────────────────────────────────────────────────────────────────


def test_drain_tasks_still_drains() -> None:
    """Control: the *destructive* accessor is unchanged -- it still empties the queue."""
    engine = _queued_engine()
    assert len(engine.drain_tasks()) == 1
    assert engine.pending_task_count() == 0
    assert engine.drain_tasks() == []


def test_the_other_accessors_and_a_bare_view_are_inert() -> None:
    """Control: the read-only accessors leave the queue, and a bare ``EventView()`` is safe."""
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


# ── the source facts (structural) ────────────────────────────────────────────────────────


def _function_source(module: Any, qualname: str) -> str:
    """The source of ``Class.method`` as a string, via the module's own file."""
    text = Path(module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(text)
    cls_name, func_name = qualname.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == func_name:
                    return ast.get_source_segment(text, child) or ""
    raise AssertionError(f"{qualname} not found in {module.__file__}")


def _called_attrs(module: Any, qualname: str) -> set[str]:
    """The attribute names actually **called** (``x.foo()``) inside ``Class.method``.

    A *call*, not a substring: the docstring of ``get_pending_tasks`` names
    ``drain_tasks()`` in prose, so a plain ``in`` scan would flag the fix as the defect.
    """
    text = Path(module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(text)
    cls_name, func_name = qualname.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == func_name:
                    return {
                        c.func.attr
                        for c in ast.walk(child)
                        if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                    }
    raise AssertionError(f"{qualname} not found in {module.__file__}")


def test_get_pending_tasks_takes_a_snapshot_in_source() -> None:
    """The structural claim: ``get_pending_tasks`` *calls* snapshot, not drain."""
    import aegis_ai.observability.event_view as event_view_module

    called = _called_attrs(event_view_module, "EventView.get_pending_tasks")
    assert "snapshot_tasks" in called, "get_pending_tasks no longer takes a snapshot"
    assert "drain_tasks" not in called, (
        "get_pending_tasks drains the queue again -- the item-96 starvation is back"
    )


def test_snapshot_tasks_does_not_clear_in_source() -> None:
    """The partner fact: ``snapshot_tasks`` copies without clearing (and ``drain_tasks`` does)."""
    assert "clear" not in _called_attrs(trigger_engine_module, "TriggerEngine.snapshot_tasks"), (
        "snapshot_tasks clears the queue -- it is a drain again"
    )
    assert "list(self._task_queue)" in _function_source(
        trigger_engine_module, "TriggerEngine.snapshot_tasks"
    ), "snapshot_tasks no longer copies the queue"
    assert "clear" in _called_attrs(trigger_engine_module, "TriggerEngine.drain_tasks"), (
        "drain_tasks no longer clears -- the control is gone; re-measure which accessor is which"
    )


# ── the production shape ────────────────────────────────────────────────────────────────


def test_a_published_event_survives_a_view_read_on_the_real_runtime(real_runtime) -> None:
    """End to end on the real runtime: the view holds the engine the loop drains, and no longer steals.

    The runtime builds one ``EventView`` over one ``TriggerEngine``, and the autonomous loop
    drains that same engine. A published event that matches a rule lands in the queue; reading
    it through the view must leave it for the loop.
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

    seen = real_runtime.event_view.get_pending_tasks()
    assert [t["triggered_by_rule_id"] for t in seen] == [_PROBE_RULE]
    assert [t.triggered_by_rule_id for t in engine.drain_tasks()] == [_PROBE_RULE], (
        "the loop's drain found nothing -- the view stole the task again (item 96)"
    )
