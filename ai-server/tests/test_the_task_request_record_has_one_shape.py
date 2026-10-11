"""The ``TaskRequest`` record: 12 fields, **three** writers that do not agree, and **five** fields no reader reads.

``TaskRequest`` (``trigger_engine.py``) is the Autonomous Loop's event-driven work item. Its consumers are
the L2 wake (``DELEGATION.md`` section 4 items 24/108) and the dashboard view
(``observability/event_view.py::get_pending_tasks``). Measured 2026-10-11 (cycle 156):

  * the record declares **12** fields;
  * it is built in **three** places, and their emitted key sets are **all different**:
      - ``src/trigger_engine.py::_create_task`` (the engine) — all **12**;
      - ``autonomous_controller.py::build_task_request_from_intrinsic_task`` (intrinsic) — **10**
        (omits ``source_server_type``, ``source_server_id``);
      - ``autonomous_controller.py::_build_task_request`` (external-task branch) — **5**
        (omits 7: the two source fields, the three ``triggered_by_*``, ``payload_snapshot``,
        ``cooldown_until_ms``);
  * the union of every reader's requested keys is exactly the **7** the view renders, so **5** fields
    are written but never read: ``triggered_by_event_id``, ``payload_snapshot``, ``source_server_type``,
    ``source_server_id``, ``cooldown_until_ms``.

This is the item-107 shape generalised: a record whose *field* is written by one producer and never
consumed, and whose producers disagree about which fields exist. The defaults are silent
(``""`` / ``UNSPECIFIED`` / ``0``), so a reader added later gets the engine's value but the *other*
writers' defaults — with no error. The 5 unread fields are a **latent** hazard, not a live one: nothing
reads them today, which is why this pin *records* the census rather than changing behaviour.

⚠️ Cycle 154 fixed ``cooldown_until_ms``'s clock (the field is still unread); cycle 155 showed the L2
gate drops a trigger's reason. This pin is the record those two cycles were missing.
"""

from __future__ import annotations

import ast
import dataclasses
import pathlib
from typing import Any

import pytest

from trigger_engine import TaskRequest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"

_FIELDS = (
    "task_id",
    "action_type",
    "triggered_by_event_id",
    "triggered_by_event_type",
    "triggered_by_rule_id",
    "source_server_type",
    "source_server_id",
    "context_summary",
    "payload_snapshot",
    "priority",
    "created_at_ms",
    "cooldown_until_ms",
)

# (module basename, enclosing function) -> the exact keyword set its TaskRequest(...) emits
_WRITERS: dict[tuple[str, str], set[str]] = {
    ("trigger_engine.py", "_create_task"): set(_FIELDS),
    ("autonomous_controller.py", "build_task_request_from_intrinsic_task"): set(_FIELDS)
    - {"source_server_type", "source_server_id"},
    ("autonomous_controller.py", "_build_task_request"): {
        "task_id",
        "action_type",
        "context_summary",
        "priority",
        "created_at_ms",
    },
}

# The keys the dashboard view renders (one dict literal in get_pending_tasks)
_VIEW_KEYS = {
    "task_id",
    "action_type",
    "triggered_by_event_type",
    "triggered_by_rule_id",
    "priority",
    "created_at_ms",
    "context_summary",
}

# Every reader site we know of, and the fields it requests off a TaskRequest.
_READER_SITES = (
    ("event_view.py", "get_pending_tasks"),
    ("autonomous_loop.py", "_drain_trigger_tasks"),
    ("autonomous_loop.py", "_trigger_label"),
    ("autonomous_controller.py", "_record_audit"),
    ("runtime.py", "_create_autonomous_loop"),
)

_UNREAD = {
    "triggered_by_event_id",
    "payload_snapshot",
    "source_server_type",
    "source_server_id",
    "cooldown_until_ms",
}

_TASK_NAMES = {"t", "task", "task_request", "request"}
_MODULES = {
    "trigger_engine.py": _SRC / "trigger_engine.py",
    "event_view.py": _SRC / "aegis_ai" / "observability" / "event_view.py",
    "autonomous_loop.py": _SRC / "aegis_ai" / "autonomous" / "autonomous_loop.py",
    "autonomous_controller.py": _SRC / "aegis_ai" / "autonomous" / "autonomous_controller.py",
    "runtime.py": _SRC / "aegis_ai" / "runtime.py",
}


# ── AST helpers ───────────────────────────────────────────────

def _parse(name: str) -> ast.Module:
    return ast.parse(_MODULES[name].read_text(encoding="utf-8"))


def _functions(tree: ast.Module) -> list[tuple[str, ast.AST]]:
    """(qualname, node) for every function/lambda-carrying def, with the enclosing name."""
    out: list[tuple[str, ast.AST]] = []

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append((child.name, child))
                walk(child, child.name)
            else:
                walk(child, prefix)

    walk(tree, "")
    return out


def _enclosing_function(tree: ast.Module, target: ast.AST) -> str:
    """The name of the innermost def containing ``target`` (or '' at module level)."""
    best = ""
    for name, node in _functions(tree):
        for child in ast.walk(node):
            if child is target:
                best = name
    return best


def _task_request_calls(name: str) -> list[tuple[str, ast.Call]]:
    """Every ``TaskRequest(...)`` construction in a module, with its enclosing function."""
    tree = _parse(name)
    out = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "TaskRequest"
        ):
            out.append((_enclosing_function(tree, node), node))
    return out


def _reads_in(name: str, func: str) -> set[str]:
    """The TaskRequest fields read inside ``func`` in ``name``.

    A read is ``<task-binding>.<field>`` (the binding's last component is a task name) or
    ``getattr(<task-binding>, "<field>", ...)`` — the loop reads two fields that way.
    """
    tree = _parse(name)
    found: set[str] = set()
    for fname, node in _functions(tree):
        if fname != func:
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute) and child.attr in _FIELDS:
                recv = ast.unparse(child.value)
                if recv.split(".")[-1] in _TASK_NAMES:
                    found.add(child.attr)
            elif isinstance(child, ast.Call):
                f = child.func
                if isinstance(f, ast.Name) and f.id == "getattr" and len(child.args) >= 2:
                    lit = child.args[1]
                    if isinstance(lit, ast.Constant) and lit.value in _FIELDS:
                        recv = ast.unparse(child.args[0])
                        if recv.split(".")[-1] in _TASK_NAMES:
                            found.add(lit.value)
    return found


def _emitted_keys(call: ast.Call) -> set[str]:
    return {kw.arg for kw in call.keywords if kw.arg is not None}


def _all_writer_calls() -> dict[tuple[str, str], ast.Call]:
    """(module, enclosing function) -> the ``TaskRequest(...)`` call, over every writer module."""
    out: dict[tuple[str, str], ast.Call] = {}
    for module in ("trigger_engine.py", "autonomous_controller.py"):
        for func, call in _task_request_calls(module):
            out[(module, func)] = call
    return out


# ── The roster ────────────────────────────────────────────────

def test_the_record_roster_is_the_recorded_twelve() -> None:
    fields = tuple(f.name for f in dataclasses.fields(TaskRequest))
    assert fields == _FIELDS, (
        f"the record roster changed: {fields} -- update this record and re-measure the writers"
    )


# ── The writers ───────────────────────────────────────────────

def test_the_writers_are_the_recorded_three() -> None:
    found = set(_all_writer_calls())
    assert found == set(_WRITERS), (
        f"the writers changed: {sorted(found)} -- a new/removed TaskRequest(...) site means the "
        "field sets below are no longer the whole population"
    )


@pytest.mark.parametrize("writer,expected", list(_WRITERS.items()))
def test_each_writer_emits_the_recorded_key_set(writer: tuple[str, str], expected: set[str]) -> None:
    module, func = writer
    calls = [c for f, c in _task_request_calls(module) if f == func]
    assert len(calls) == 1, f"expected one TaskRequest(...) in {module}::{func}, found {len(calls)}"
    emitted = _emitted_keys(calls[0])
    assert emitted == expected, (
        f"{module}::{func} now emits {sorted(emitted)}; the record says {sorted(expected)}"
    )


def test_the_three_writers_disagree_and_the_divergence_is_recorded() -> None:
    """The record's core: the three *code* emitted sets are pairwise different, and each gap is named."""
    emitted = {key: _emitted_keys(call) for key, call in _all_writer_calls().items()}
    assert set(emitted) == set(_WRITERS), "the writer population changed"
    sets = list(emitted.values())
    assert len({frozenset(s) for s in sets}) == 3, "the writers now agree -- the record is stale"
    engine = emitted[("trigger_engine.py", "_create_task")]
    intrinsic = emitted[("autonomous_controller.py", "build_task_request_from_intrinsic_task")]
    external = emitted[("autonomous_controller.py", "_build_task_request")]
    assert set(_FIELDS) - engine == set(), "the engine is the full-shape writer"
    assert set(_FIELDS) - intrinsic == {"source_server_type", "source_server_id"}
    assert set(_FIELDS) - external == {
        "triggered_by_event_id",
        "triggered_by_event_type",
        "triggered_by_rule_id",
        "source_server_type",
        "source_server_id",
        "payload_snapshot",
        "cooldown_until_ms",
    }


# ── The readers ───────────────────────────────────────────────

def test_the_view_renders_exactly_the_recorded_keys() -> None:
    tree = _parse("event_view.py")
    literal = None
    for name, node in _functions(tree):
        if name == "get_pending_tasks":
            for child in ast.walk(node):
                if isinstance(child, ast.Dict) and any(
                    isinstance(k, ast.Constant) and k.value == "task_id" for k in child.keys
                ):
                    literal = child
    assert literal is not None, "get_pending_tasks no longer builds a task dict"
    keys = {k.value for k in literal.keys if isinstance(k, ast.Constant)}
    assert keys == _VIEW_KEYS, f"the view now renders {sorted(keys)}"
    assert keys <= set(_FIELDS), "the view renders a key the record does not declare"


def test_the_reader_union_leaves_exactly_the_recorded_unread_set() -> None:
    """The 5 write-only fields, established by the *readers* rather than by a name grep."""
    union: set[str] = set()
    for module, func in _READER_SITES:
        union |= _reads_in(module, func)
    assert union == _VIEW_KEYS, (
        f"the reader union changed: {sorted(union)} -- re-measure which fields are unread"
    )
    unread = set(_FIELDS) - union
    assert unread == _UNREAD, f"the unread set changed: {sorted(unread)}"
    # non-vacuous: a proper, non-empty subset
    assert unread and unread < set(_FIELDS)


# ── Behaviour: the engine writer, driven for real ─────────────

def _driven_task() -> tuple[Any, Any]:
    from aegis_schema.models import Event, EventPriority, ServerType

    from trigger_engine import ActionType, TriggerEngine, TriggerRule

    engine = TriggerEngine()
    engine.add_rule(
        TriggerRule(
            rule_id="probe-rule",
            event_type_pattern="probe.thing",
            min_severity=0,
            min_priority=EventPriority.URGENT,
            action_type=ActionType.ALERT,
            cooldown_seconds=60,
        )
    )
    event = Event(
        event_id="evt_c156",
        event_type="probe.thing",
        source_server_type=ServerType.PC,
        source_server_id="pc-c156",
        severity=5,
        priority=EventPriority.URGENT,
        payload_json='{"probe": true}',
    )
    task = engine.on_event(event)
    assert task is not None, "the probe rule did not fire -- the fixture is broken"
    return engine, task


def test_every_field_the_engine_writes_carries_the_event_s_own_value() -> None:
    """Provenance, not mere non-defaultness: each field equals what it was built from."""
    from aegis_schema.models import EventPriority, ServerType

    from trigger_engine import ActionType

    _engine, task = _driven_task()
    assert task.task_id.startswith("task_") and len(task.task_id) > len("task_")
    assert task.action_type is ActionType.ALERT
    assert task.triggered_by_event_id == "evt_c156"
    assert task.triggered_by_event_type == "probe.thing"
    assert task.triggered_by_rule_id == "probe-rule"
    assert task.source_server_type is ServerType.PC
    assert task.source_server_id == "pc-c156"
    assert task.priority is EventPriority.URGENT
    assert task.payload_snapshot == '{"probe": true}'
    assert task.context_summary, "the engine left the context summary empty"
    assert task.created_at_ms > 0
    assert task.cooldown_until_ms > task.created_at_ms


def test_the_view_shows_the_engine_s_task_with_no_silent_defaults() -> None:
    """The 7 rendered fields are all the engine's own values -- a rename would show here."""
    from aegis_ai.observability.event_view import EventView

    engine, task = _driven_task()
    rows = EventView(trigger_engine=engine).get_pending_tasks()
    assert len(rows) == 1, f"the view did not see the queued task: {rows}"
    row = rows[0]
    assert set(row) == _VIEW_KEYS
    assert row["task_id"] == task.task_id
    assert row["action_type"] == "ALERT"
    assert row["triggered_by_event_type"] == "probe.thing"
    assert row["triggered_by_rule_id"] == "probe-rule"
    assert row["priority"] == "URGENT"
    assert row["created_at_ms"] == task.created_at_ms
    assert row["context_summary"] == task.context_summary
