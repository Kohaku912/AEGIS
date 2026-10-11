"""An event-driven wake tells L2 *why* it woke -- not merely that it did.

``DELEGATION.md`` section 4 item 24 built the event-driven core, and cycles 132/134 closed
"the loop drains the engine". Every pin stopped at *drain*: the drained ``TaskRequest``s
were used only as a **boolean** ("a cycle may run"), and their content -- the rule id, the
action type, the context summary -- was read only for a log line (``_drain_trigger_tasks``).
So a cycle woken by a ``security-alert`` (action ``ALERT``) reached L2 with the same label
as one woken by a routine ``pc-screen-change`` (``OBSERVE``): ``trigger="periodic_cycle"``.
The engine recorded the difference; the consumer threw it away.

Measured 2026-10-11 (cycle 148): ``_execute_cycle`` takes ``triggered_tasks`` and labels the
L2 bridge ``"triggered:<rule_id>[,<rule_id>]"`` (``_trigger_label``); the task summaries are
carried into the L2 detail and surfaced in ``context.world_state["triggered_tasks"]``. A
desire-driven cycle is still ``"periodic_cycle"``.

Both halves of the production call site are driven, not asserted structurally:
``_run_loop`` must *pass* the drained tasks to ``_execute_cycle``, and ``_execute_cycle``
must *use* them. A pin that drove only ``_execute_cycle`` would not see a call-site mutation
that drops the argument (``aegis-verify-and-test`` Rule 15).
"""

from __future__ import annotations

from typing import Any

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop


class _Desire:
    """``_execute_cycle`` only needs a truthy ``_desire`` with ``apply_decay``."""

    def apply_decay(self) -> None:
        pass


def _live_task() -> Any:
    """The task the *live* ``pc-screen-change`` rule generates, driven for real.

    Builds the event ``pc_server_client.push_screen_changed_event`` actually builds
    (``severity=2``, ``priority=NORMAL``) and feeds it to a fresh engine carrying the
    default rules -- no LLM, no bus, but the real rule set and the real matcher.
    """
    from aegis_schema.models import Event, EventPriority, ServerType
    from trigger_engine import TriggerEngine, create_default_rules

    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)
    event = Event(
        event_id="evt_c148",
        event_type="pc.screen_changed",
        source_server_type=ServerType.PC,
        source_server_id="pc-c148",
        timestamp_ms=0,
        payload_json='{"change":"screen_updated"}',
        severity=2,
        priority=EventPriority.NORMAL,
        dedupe_key="pc.screen_changed",
    )
    task = engine.on_event(event)
    assert task is not None, "the live pc-screen-change rule no longer matches its own event"
    return task


def _loop(tmp_path: Any) -> AutonomousLoop:
    loop = AutonomousLoop(desire_system=_Desire(), data_dir=str(tmp_path / "autonomous"))
    loop._desire = _Desire()
    loop._refresh_observations_for_cycle = lambda: None
    loop._pending_actionable_observations = []
    return loop


def test_run_loop_passes_the_drained_tasks_to_the_cycle(tmp_path) -> None:
    """The call site: ``_run_loop`` hands the drained tasks to ``_execute_cycle``.

    Drives one iteration of the *real* ``_run_loop`` against a real ``TriggerEngine``
    (fed the live ``pc.screen_changed`` event), with ``_execute_cycle`` spied so the loop
    terminates after the wake. A mutation that drops ``triggered_tasks=`` from the call
    would make the spy see ``None`` -- the engine's work would be thrown away.
    """
    from trigger_engine import TriggerEngine, create_default_rules

    loop = _loop(tmp_path)
    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)
    loop._trigger_engine = engine

    from aegis_schema.models import Event, EventPriority, ServerType

    queued = engine.on_event(
        Event(
            event_id="evt_c148_loop",
            event_type="pc.screen_changed",
            source_server_type=ServerType.PC,
            source_server_id="pc-c148",
            severity=2,
            priority=EventPriority.NORMAL,
        )
    )
    assert queued is not None

    loop._running = True
    loop._min_execution_interval_ms = 0
    loop._next_run_ms = 0
    loop._idle_wake_cap_ms = 0
    loop._monitor_desires = lambda: False
    loop._maybe_ask_burden_check = lambda now: None

    seen: list[Any] = []

    def _spy_execute(*, force_desire: bool = False, triggered_tasks: Any = None) -> None:
        seen.append(list(triggered_tasks or []))
        loop._running = False

    loop._execute_cycle = _spy_execute  # type: ignore[method-assign]
    loop._run_loop()

    assert seen, "the loop never executed a cycle even though a task was queued and due"
    assert [task.task_id for task in seen[0]] == [queued.task_id], (
        "the drained task did not reach _execute_cycle -- the wake lost its reason"
    )


def test_the_cycle_labels_l2_with_the_fired_rule(tmp_path) -> None:
    """The use half: the rule id becomes the L2 trigger label.

    Drives the *real* ``_execute_cycle`` with a spied L2 bridge, so the label the
    production code computes is the label L2 receives.
    """
    loop = _loop(tmp_path)
    task = _live_task()
    seen: dict[str, Any] = {}

    def _handler(
        trigger: str = "periodic_cycle",
        force_desire: bool = False,
        pending_observations: Any = None,
        triggered_tasks: Any = None,
    ) -> dict[str, Any]:
        seen["trigger"] = trigger
        seen["tasks"] = list(triggered_tasks or [])
        return {"handled": True, "action_type": "observe", "reason": "spy"}

    loop.set_l2_reasoning_handler(_handler, should_run=lambda force_desire=False: True)
    loop._execute_cycle(triggered_tasks=[task])

    assert seen.get("trigger") == "triggered:pc-screen-change", (
        f"an event-driven cycle reached L2 as {seen.get('trigger')!r} -- the rule that woke "
        "it was not carried"
    )
    assert seen.get("tasks") == [task], "the task list did not reach the L2 bridge"


def test_a_desire_cycle_still_reports_periodic_cycle(tmp_path) -> None:
    """Control: with no triggered tasks the label is unchanged (``periodic_cycle``)."""
    loop = _loop(tmp_path)
    seen: dict[str, Any] = {}

    def _handler(trigger: str = "periodic_cycle", **_: Any) -> dict[str, Any]:
        seen["trigger"] = trigger
        return {"handled": True, "action_type": "observe"}

    loop.set_l2_reasoning_handler(_handler, should_run=lambda force_desire=False: True)
    loop._execute_cycle()

    assert seen.get("trigger") == "periodic_cycle", (
        "a desire-driven cycle was mislabelled as event-driven"
    )


def test_a_task_without_a_rule_id_is_still_marked_triggered() -> None:
    """Control: a task carrying no rule id is still visibly event-driven, not periodic."""
    from trigger_engine import TaskRequest

    label = AutonomousLoop._trigger_label([TaskRequest(task_id="t", triggered_by_rule_id="")])
    assert label == "triggered", f"a rule-id-less task was labelled {label!r}"


def test_the_l2_pipeline_surfaces_the_task_summaries() -> None:
    """The engine's context reaches the L2 prompt, not just the rule id.

    Drives the real ``_run_l2_pipeline`` with a stub mind, so the ``world_state`` the
    pipeline builds is the one L2 would read (``L2Context.to_prompt`` prints it).
    """
    from aegis_ai.runtime import _run_l2_pipeline

    class _Ctx:
        def __init__(self) -> None:
            self.world_state: dict[str, Any] = {}
            self.l1_summaries: list[Any] = []

    class _Mind:
        last: _Ctx | None = None

        def build_context(self) -> _Ctx:
            self.last = _Ctx()
            return self.last

        def run_once(self, ctx: _Ctx) -> dict[str, Any]:
            return {"handled": True, "action_type": "observe"}

    class _Rt:
        l2_mind = _Mind()
        event_manager = None

    rt = _Rt()
    _run_l2_pipeline(
        rt,
        trigger="triggered:pc-screen-change",
        detail={
            "type": "triggered:pc-screen-change",
            "source": "autonomous_loop",
            "triggered_tasks": ["Event 'pc.screen_changed' from PC (severity=2)"],
        },
    )

    assert rt.l2_mind.last is not None
    world = rt.l2_mind.last.world_state
    assert world.get("trigger") == "triggered:pc-screen-change"
    assert "pc.screen_changed" in str(world.get("triggered_tasks") or ""), (
        "the trigger task's context did not reach the L2 world_state"
    )


def test_the_pipeline_omits_the_key_when_no_task_woke_it() -> None:
    """Control: a desire-driven cycle adds no ``triggered_tasks`` key (prompt unchanged)."""
    from aegis_ai.runtime import _run_l2_pipeline

    class _Ctx:
        def __init__(self) -> None:
            self.world_state: dict[str, Any] = {}
            self.l1_summaries: list[Any] = []

    class _Mind:
        last: _Ctx | None = None

        def build_context(self) -> _Ctx:
            self.last = _Ctx()
            return self.last

        def run_once(self, ctx: _Ctx) -> dict[str, Any]:
            return {"handled": True, "action_type": "observe"}

    class _Rt:
        l2_mind = _Mind()
        event_manager = None

    rt = _Rt()
    _run_l2_pipeline(
        rt,
        trigger="periodic_cycle",
        detail={"type": "periodic_cycle", "source": "autonomous_loop"},
    )

    assert rt.l2_mind.last is not None
    assert "triggered_tasks" not in rt.l2_mind.last.world_state, (
        "a desire-driven cycle grew a triggered_tasks key -- the periodic prompt changed"
    )
