"""`TaskRequest.cooldown_until_ms` must name ONE clock -- and it has no reader yet.

`TaskRequest` (trigger_engine.py) carries two `*_ms` fields side by side. Its sibling
`created_at_ms` is Unix-epoch milliseconds from **every** producer and is rendered by the live
view in observability/event_view.py (``EventView.get_pending_tasks``, wired at runtime.py:1815).
`cooldown_until_ms` was not consistent:

  * the trigger engine stamped ``int((time.monotonic() + rule.cooldown_seconds) * 1000)`` --
    seconds-since-boot (measured ~5.7e7 ms on this machine, and it varies with uptime);
  * the intrinsic-task builder stamped ``now + task.cooldown_seconds * 1000`` where ``now`` is
    ``int(time.time() * 1000)`` -- Unix-epoch, ~1.76e12 ms;
  * a third construction (the external task, autonomous_controller.py) leaves it at the default
    ``0``.

Three orders of magnitude apart behind one name. The field has **no reader** (measured with
``ast``: no ``Load`` of the attribute anywhere under ``src/``), so nothing was wrong *yet* -- and
the first consumer that rendered it beside ``created_at_ms`` -- the shape the view already uses --
would have been wrong for half the producers. The fix puts the trigger engine on ``time.time()``,
so every value that is set is Unix-epoch milliseconds.

The duration logic is a *different* clock **on purpose**: ``_check_cooldown`` must use a monotonic
clock (a wall clock can jump backwards), and this pin keeps both facts at once -- the field is
wall-clock, the blocking is monotonic -- so a later "simplification" that unifies them, or a fix
that moves the blocking onto the wall clock, trips a test.

Measured 2026-10-11 (cycle 154).
"""

from __future__ import annotations

import ast
import pathlib
import time
from typing import Any

import pytest

from aegis_schema.models import EventPriority, RiskLevel

from aegis_ai.event.helpers import build_event

from trigger_engine import TaskRequest, TriggerEngine, TriggerRule

_SELF = pathlib.Path(__file__).resolve()
_SRC = _SELF.parents[1] / "src"

#: The two producers that set the field, by enclosing function name. A third construction (the
#: external task) leaves it at the default ``0`` on purpose -- it carries no cooldown.
_WRITERS = {"_create_task", "build_task_request_from_intrinsic_task"}

_RULE_ID = "probe-rule"
_EVENT_TYPE = "probe.thing_happened"
_COOLDOWN_SECONDS = 60


# ── AST helpers: discover the surface, never hand-list it ──────────────

def _parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    return parents


def _enclosing(parents: dict[ast.AST, ast.AST], node: ast.AST) -> str:
    cur: ast.AST | None = node
    while cur is not None:
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return cur.name
        cur = parents.get(cur)
    return "<module>"


def _scan() -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    """Return (write sites, read sites) for `cooldown_until_ms` across ``src/``.

    A *write* is a call carrying the keyword argument; a *read* is an attribute access in a
    ``Load`` context. A keyword argument is an ``ast.keyword`` node, not an ``ast.Attribute``, so
    the two sets cannot contaminate each other.
    """
    writes: set[tuple[str, str]] = set()
    reads: set[tuple[str, str]] = set()
    for path in _SRC.rglob("*.py"):
        if path.resolve() == _SELF:
            continue
        rel = path.relative_to(_SRC).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        parents = _parent_map(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and any(
                kw.arg == "cooldown_until_ms" for kw in node.keywords
            ):
                writes.add((rel, _enclosing(parents, node)))
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "cooldown_until_ms"
                and isinstance(node.ctx, ast.Load)
            ):
                reads.add((rel, _enclosing(parents, node)))
    return writes, reads


# ── Producers under test ───────────────────────────────────────────────

def _event() -> Any:
    return build_event(
        _EVENT_TYPE,
        source_server_id="probe",
        severity=5,
        priority=EventPriority.URGENT,
    )


def _rule() -> TriggerRule:
    return TriggerRule(
        rule_id=_RULE_ID,
        event_type_pattern=_EVENT_TYPE,
        min_severity=0,
        min_priority=EventPriority.URGENT,
        cooldown_seconds=_COOLDOWN_SECONDS,
    )


def _fire() -> tuple[TriggerEngine, TaskRequest]:
    engine = TriggerEngine()
    engine.add_rule(_rule())
    task = engine.on_event(_event())
    assert task is not None, "the rule did not fire -- the control is broken"
    return engine, task


def _intrinsic_task_request(tmp_path: pathlib.Path, now_ms: int) -> TaskRequest:
    from aegis_ai.autonomous.autonomous_controller import AutonomousController
    from aegis_ai.desire.desire_system import DesireSystem
    from aegis_ai.desire.intrinsic_task_generator import IntrinsicTask

    controller = AutonomousController(
        desire_system=DesireSystem(data_dir=str(tmp_path / "desire")),
        data_dir=str(tmp_path / "ctrl"),
    )
    task = IntrinsicTask(
        task_id="t1",
        source_desire="user_support",
        title="T",
        description="D",
        priority=1.0,
        expected_desire_effects={},
        required_capabilities=[],
        risk_level=RiskLevel.READ_ONLY,
        requires_user_approval=False,
        cooldown_seconds=_COOLDOWN_SECONDS,
        created_at=0,
        reason="probe",
    )
    return controller.build_task_request_from_intrinsic_task(task, now_ms=now_ms)


# ── The surface ────────────────────────────────────────────────────────

def test_the_field_is_declared_and_the_writers_are_the_recorded_two() -> None:
    """Non-vacuity: the field exists and the scan finds the two producers by name."""
    import dataclasses

    assert "cooldown_until_ms" in {f.name for f in dataclasses.fields(TaskRequest)}
    writes, _ = _scan()
    assert {fn for _, fn in writes} == _WRITERS, (
        f"the writers of cooldown_until_ms moved: {sorted(writes)} -- a new producer must use "
        "the same clock, so update this record and the docstring together"
    )


def test_the_field_has_no_reader() -> None:
    """The recorded state: nothing under ``src/`` reads the field (it is latent, not wired)."""
    _, reads = _scan()
    assert reads == set(), (
        f"cooldown_until_ms gained a reader: {sorted(reads)} -- if it is now rendered or "
        "compared, this pin must become a value pin (the clock matters to the consumer)"
    )


# ── The fix: the field is Unix-epoch ms, and the blocking clock is not ──

def test_the_trigger_engine_stamps_unix_epoch_milliseconds() -> None:
    """The regression guard: the engine's value is on the wall clock, not the monotonic one."""
    _, task = _fire()
    expected = time.time() * 1000 + _COOLDOWN_SECONDS * 1000
    assert abs(task.cooldown_until_ms - expected) <= 5000, (
        f"cooldown_until_ms={task.cooldown_until_ms} is not Unix-epoch ms "
        f"(expected ~{expected:.0f}); the engine is stamping a monotonic value"
    )


def test_the_blocking_clock_is_still_monotonic_and_not_the_display_clock() -> None:
    """Both facts at once: the field is wall-clock, the blocking map is monotonic.

    `_check_cooldown` must keep a monotonic clock (a wall clock can jump), so the fix moves only
    the *field*. This asserts the two clocks are separated, which is what a later "unify them"
    edit would break.
    """
    engine, task = _fire()
    key = engine.get_rule(_RULE_ID).get_cooldown_key()
    blocking = engine._cooldowns[key]
    assert abs(blocking - (time.monotonic() + _COOLDOWN_SECONDS)) <= 5, (
        f"the blocking map holds {blocking}, which is not monotonic seconds -- the duration "
        "logic must not move onto the wall clock"
    )
    assert abs(task.cooldown_until_ms - (time.time() * 1000 + _COOLDOWN_SECONDS * 1000)) <= 5000


def test_the_trigger_engine_still_blocks_a_second_event() -> None:
    """Behavioural control: the fix did not disturb the duration logic."""
    engine, _ = _fire()
    assert engine.on_event(_event()) is None, "the cooldown no longer suppresses a second event"
    engine.reset_all_cooldowns()
    assert engine.on_event(_event()) is not None, "the reset did not clear the cooldown"


# ── The other producer must agree ──────────────────────────────────────

def test_the_intrinsic_builder_stamps_the_same_unix_clock(tmp_path) -> None:
    """Two producers, one meaning -- the whole point of the fix."""
    now_ms = int(time.time() * 1000)
    request = _intrinsic_task_request(tmp_path, now_ms)
    assert request.cooldown_until_ms == now_ms + _COOLDOWN_SECONDS * 1000, (
        f"the intrinsic builder's value {request.cooldown_until_ms} is not now_ms + cooldown"
    )
    _, engine_task = _fire()
    # Both are Unix-epoch ms, so they differ only by the elapsed wall time.
    assert abs(engine_task.cooldown_until_ms - request.cooldown_until_ms) <= 5000, (
        "the two producers no longer agree on the clock: "
        f"{engine_task.cooldown_until_ms} vs {request.cooldown_until_ms}"
    )


@pytest.mark.parametrize("field", ["created_at_ms", "cooldown_until_ms"])
def test_both_star_fields_are_epoch_milliseconds(field: str) -> None:
    """The sibling contract: whichever `*_ms` field you read, it is Unix-epoch ms.

    Asserted by *magnitude* rather than a window, because ``cooldown_until_ms`` legitimately sits
    in the future by the rule's cooldown: Unix-epoch ms is ~1.7e12 while the monotonic scale is
    ~1e9, three orders of magnitude apart, which is the whole defect.
    """
    _, task = _fire()
    value = getattr(task, field)
    assert 1e12 < value < 1e13, (
        f"{field}={value} is not Unix-epoch milliseconds -- the two fields disagree on the clock"
    )
    assert value >= task.created_at_ms, f"{field} predates the task"
