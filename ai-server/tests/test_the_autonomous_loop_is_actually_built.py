"""The autonomous loop the entry points start is *built* and *wired* -- not just declared.

``_create_autonomous_loop`` (``runtime.py``) is the composition root's second half: it turns a
built runtime into a running loop and hands that loop every collaborator the L1 -> L2 hand-off
reads -- the ``TriggerEngine`` (DELEGATION.md section 4 item 24), the L2 bridge handlers, the
memory manager, the capability retriever, the burden metric, the confirmation store.

Until this module, **no test executed its body**. The function is called only by
``AegisRuntime.start_autonomous_if_enabled``, and every test that reaches the starter passes
``start_autonomous_if_enabled=lambda: None`` (``test_dashboard_routes.py``,
``test_e2e_integration.py``), so the body never ran. The suite pinned the *lines* structurally
(``test_event_driven_core_is_constructed.py``,
``test_l1_dispatch_surface_is_present_in_the_real_runtime.py``) and re-ran *two* of them in
isolation (``test_burden_check_is_asked_by_the_loop.py::test_the_wiring_lines_actually_run``),
but a wiring mistake anywhere else in the ~170-line body is invisible to the suite.

That is not hypothetical. ``PROJECT_STATUS_REVIEW.md`` section 3.1 records a self-inflicted bug
in this exact function -- ``confirmation_store`` was referenced out of scope -- and
**the whole suite stayed green**; only ruff's ``F821`` caught it, and CI does not run ruff.

This module drives the *production* entry (``start_autonomous_if_enabled``) on the real
composition root, so the whole body runs, and asserts the loop it returns is wired for the
hand-off. ``AutonomousLoop.start`` is stubbed to a no-op so no background thread is spawned:
the subject is the *wiring*, not the loop's cadence (``test_autonomous_loop_behavior.py``).

What this does **not** cover: that the loop, once started, actually drains the engine on its
first cycle. That is the cadence, pinned elsewhere; here we prove the loop is *handed* the
engine and *reads it* when asked.
"""

from __future__ import annotations

from typing import Any

import pytest

#: The attributes ``_create_autonomous_loop`` wires from the runtime, and the runtime attribute
#: each must be *identical to*. Identity, not equality: a copy would still leave the loop reading
#: a stale engine/store.
_WIRED_IDENTITIES = (
    ("_trigger_engine", "trigger_engine"),
    ("_confirmations", "confirmation_store"),
    ("_memory_manager", "memory_manager"),
    ("_capability_retriever", "capability_retriever"),
    ("_initiative_engine", "initiative_engine"),
    ("_operation_store", "operation_store"),
    ("_sleep_manager", "sleep_manager"),
    ("_continuation_manager", "continuation_manager"),
    ("_goal_service", "goal_service"),
    ("_user_understanding_service", "user_understanding_service"),
    ("_social_manager", "social_manager"),
)

#: The loop attributes that must be *callable* for the L1 -> L2 bridge to fire at all.
_L2_BRIDGE_CALLABLES = ("_l2_reasoning_handler", "_l2_should_run_cycle", "_l2_event_handler")


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
def real_runtime(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))

    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    reset_runtime_for_tests()
    return get_runtime()


@pytest.fixture
def started_loop(real_runtime, monkeypatch) -> Any:
    """Run the production starter with ``start`` stubbed, and return the built loop.

    Stubbing ``AutonomousLoop.start`` keeps the test off a background thread; the point is that
    ``_create_autonomous_loop`` ran, not that the thread spun up.
    """
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop

    monkeypatch.setattr(AutonomousLoop, "start", lambda self: None)

    real_runtime.start_autonomous_if_enabled()
    loop = real_runtime.autonomous_loop
    assert loop is not None, (
        "start_autonomous_if_enabled did not build the loop even though "
        "settings.autonomous.autonomous_loop_enabled defaults to True -- the gate or the "
        "lazy creation changed"
    )
    return loop


def test_the_starter_actually_builds_the_loop(started_loop, real_runtime) -> None:
    """The production entry point reaches ``_create_autonomous_loop`` and stores the result.

    Every other test stubs the starter away, so this is the only place the body runs. If the
    body raised -- the exact failure mode section 3.1 records -- this test is where it shows.
    """
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop

    assert isinstance(started_loop, AutonomousLoop), (
        "start_autonomous_if_enabled stored something other than an AutonomousLoop"
    )
    assert real_runtime.autonomous_loop is started_loop, (
        "the built loop was not stored on the runtime, so nothing would ever drain the engine"
    )


def test_the_built_loop_shares_the_runtime_collaborators(started_loop, real_runtime) -> None:
    """Each collaborator the hand-off reads is the runtime's own object -- by identity.

    ``_trigger_engine`` is the load-bearing one (section 4 item 24): ``_drain_trigger_tasks``
    reads it and returns ``[]`` when it is ``None``, so an unwired engine is a *silent* skip --
    the L1 escalation would queue tasks that nobody drains, with no error anywhere.
    """
    missing = []
    for loop_attr, runtime_attr in _WIRED_IDENTITIES:
        expected = getattr(real_runtime, runtime_attr, None)
        actual = getattr(started_loop, loop_attr, None)
        if expected is None:
            missing.append(f"runtime.{runtime_attr} is None (fixture, not the wiring)")
        elif actual is not expected:
            missing.append(f"{loop_attr} is not runtime.{runtime_attr}")
    assert not missing, "the built loop is not wired to the runtime: " + "; ".join(missing)


def test_the_l2_bridge_is_registered(started_loop) -> None:
    """The three callables that carry the loop into L2 must be present and callable.

    ``_l2_reasoning_handler`` / ``_l2_event_handler`` route the loop back into
    ``_run_l2_pipeline``; ``_l2_should_run_cycle`` gates it. They are set only when the runtime
    supplies ``l2_mind`` -- which the real composition root does -- so their absence here would
    mean the L1 -> L2 hand-off lost its return path.
    """
    for name in _L2_BRIDGE_CALLABLES:
        handler = getattr(started_loop, name, None)
        assert callable(handler), f"{name} is not callable on the built loop: {handler!r}"


def test_the_loop_drains_the_engine_the_runtime_built(started_loop, real_runtime) -> None:
    """A task queued on the runtime's engine is the task the loop's consumer returns.

    Identity (above) proves the loop *holds* the engine; this proves it *reads* it. Together
    they close section 4 item 24's consumption half for the real composition root, executed
    rather than scanned.
    """
    from aegis_schema.models import Event, EventPriority, ServerType
    from trigger_engine import TriggerRule

    engine = real_runtime.trigger_engine
    # Clear anything the composition root queued at build time so the assertion is about ours.
    started_loop._drain_trigger_tasks()

    engine.add_rule(
        TriggerRule(
            rule_id="c132-probe",
            event_type_pattern="*",
            cooldown_seconds=0.0,
        )
    )
    event = Event(
        event_id="evt-c132",
        event_type="dev.c132_probe",
        source_server_type=ServerType.PC,
        source_server_id="pc-c132",
        severity=9,
        priority=EventPriority.URGENT,
    )
    generated = engine.on_event(event)
    assert generated is not None, "the probe rule did not match its own event"

    drained = started_loop._drain_trigger_tasks()
    assert generated.task_id in {task.task_id for task in drained}, (
        "the loop's consumer did not return the task the runtime's engine queued -- the loop "
        "and the runtime are not reading the same queue"
    )
    assert engine.pending_task_count() == 0, "the loop did not drain the engine"


def test_the_gate_skips_building_when_the_setting_is_off(real_runtime, monkeypatch) -> None:
    """Control: with the setting off the starter returns early and no loop is built.

    Proves the identity/callable assertions above are not vacuous -- they pass only because the
    starter ran the body, and the body is reachable only through the gate.
    """
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop

    monkeypatch.setattr(AutonomousLoop, "start", lambda self: None)

    settings = real_runtime.settings_store.get()
    settings.autonomous.autonomous_loop_enabled = False
    monkeypatch.setattr(real_runtime.settings_store, "get", lambda: settings)

    real_runtime.start_autonomous_if_enabled()

    assert real_runtime.autonomous_loop is None, (
        "the gate did not stop the loop from being built, so the setting is not read where "
        "the starter reads it"
    )
