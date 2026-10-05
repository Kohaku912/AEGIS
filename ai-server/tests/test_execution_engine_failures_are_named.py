"""The task execution engine names its failures.

Two units, because they are two different claims
------------------------------------------------
1. **A call site.** ``TaskExecutionEngine.apply_task_state`` calls
   ``self._task_manager.pause_task(task_id)`` **three** times. The third site (the
   "unverified goal" branch) already named its failure with
   ``logger.debug(..., exc_info=True)``; the first two (``HAS_REQUIRES_OBSERVATION``
   and ``HAS_WAITING_DEPENDENCY``) swallowed it with a handler that caught both
   ``AttributeError`` and ``Exception`` and did nothing. Measured 2026-10-06.

   That is a defect: a pause that fails leaves the task **unpaused** while the
   engine believes it paused it, and with no record a debugging session cannot see
   it -- the "a silent failure is worse than a loud one" family. The
   ``AttributeError`` arm was also redundant: that tuple is exactly ``Exception``.

2. **The module.** Following the family convention (cycle 13's
   ``test_mind_persistence_failures_are_named`` / cycle 16's
   ``test_spontaneous_observation_failures_are_named``), **every** ``except``
   handler must either call the logger or be a documented deliberate
   non-logger. Measured 2026-10-06: 18 handlers. Four legitimately do not log
   (they surface the failure in a value, are control flow, or guard an optional
   import) and are named in ``_ALLOWED_NON_LOGGING`` with their reason; the rest
   log. One handler, ``_attach_manifest_completion``'s, was a seventh silent
   swallow -- ``catalog.resolve`` returns ``None`` for an unknown id, so its
   ``except Exception`` could only be hiding an *unexpected* error -- and was
   fixed in this cycle.

   Cycle 55 update: ``_get_system_prompt``'s and ``_resolve_settings``'s
   ``except KeyError`` handlers were allow-listed here as "expected absence" and
   are now **named**. Their two entries were removed rather than kept: a DEBUG
   record makes a *substituted default* readable at no cost, and "expected
   absence" is the reason the family rejects, not accepts. The allow-list went
   from six entries to four.

Scope note: this pin walks the **parse tree**, not the text. A docstring or comment
that merely *names* ``pause_task`` is not a call site, and a name inside a string is
not a handler -- which is why the scan is AST-based.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from aegis_ai.task.execution_engine import TaskExecutionEngine, TaskFinalState

_ENGINE = (
    Path(__file__).resolve().parents[2]
    / "ai-server"
    / "src"
    / "aegis_ai"
    / "task"
    / "execution_engine.py"
)
_LOGGER = "aegis_ai.task.execution_engine"

# Handlers that deliberately do not log, keyed by (enclosing function, except-type).
# Keyed by name (not line) so an edit above them does not rot the pin; the reasons
# are the record, and `test_the_allow_list_is_not_vacuous` fails if one disappears.
_ALLOWED_NON_LOGGING: dict[tuple[str, str], str] = {
    ("_execute_agent_step", "Exception"): (
        "surfaces the failure downstream (step.status = FAILED, step.error = ...)"
    ),
    ("_execute_agent_step", "RuntimeError"): (
        "control flow: get_running_loop() raising means 'no loop running'"
    ),
    ("_execute_llm_step", "Exception"): (
        "surfaces the failure in the return value ('[ERROR] LLM step: {e}')"
    ),
    ("_present_task_completion", "Exception"): (
        "optional import guard; an absent presentation stack is not a failure"
    ),
}

# The three pause_task call sites recorded in the docstring (non-vacuity floor).
_RECORDED_PAUSE_SITES = 3


def _tree() -> ast.Module:
    assert _ENGINE.is_file(), f"{_ENGINE} is missing -- the scan would pass vacuously"
    return ast.parse(_ENGINE.read_text(encoding="utf-8", errors="replace"))


def _parent_map(tree: ast.Module) -> dict[ast.AST, ast.AST]:
    parents: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def _enclosing_function(tree: ast.Module) -> dict[int, str]:
    owner: dict[int, str] = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(fn):
                owner.setdefault(id(node), fn.name)
    return owner


def _logs(handler: ast.ExceptHandler) -> bool:
    return any(
        isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name)
        and n.func.value.id == "logger"
        for n in ast.walk(handler)
    )


# ── unit 1: every pause_task call site names its failure ────────────────────


def _pause_calls(tree: ast.Module) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "pause_task"
    ]


def test_every_pause_task_call_site_names_its_failure() -> None:
    tree = _tree()
    parents = _parent_map(tree)
    calls = _pause_calls(tree)
    assert len(calls) >= _RECORDED_PAUSE_SITES, (
        f"expected at least {_RECORDED_PAUSE_SITES} pause_task call sites in "
        f"apply_task_state, found {len(calls)} -- the scan is measuring the wrong thing"
    )
    silent: list[int] = []
    for call in calls:
        node: ast.AST | None = call
        while node is not None and not isinstance(node, ast.Try):
            node = parents.get(node)
        assert node is not None, f"pause_task call at line {call.lineno} is not inside a try"
        for handler in node.handlers:
            if not _logs(handler):
                silent.append(call.lineno)
    assert silent == [], f"pause_task failures are swallowed silently at line(s) {sorted(set(silent))}"


def test_the_scan_finds_the_named_sites_it_is_meant_to_protect() -> None:
    """Non-vacuity: the AST scan must actually see the three calls and the logger calls."""
    tree = _tree()
    calls = _pause_calls(tree)
    assert len(calls) == _RECORDED_PAUSE_SITES, f"recorded {_RECORDED_PAUSE_SITES} pause_task call sites, found {len(calls)}"
    assert any(_logs(h) for h in ast.walk(tree) if isinstance(h, ast.ExceptHandler)), (
        "no handler calls the logger -- the naming instrument is dead"
    )


# ── unit 2: the module has no undocumented silent handler ───────────────────


def _non_logging_handlers() -> list[tuple[str, str, int]]:
    """Return ``(function, except-type, line)`` for every handler that does not log."""
    tree = _tree()
    owner = _enclosing_function(tree)
    found: list[tuple[str, str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler) or _logs(node):
            continue
        exc = ast.unparse(node.type) if node.type else "<bare>"
        found.append((owner.get(id(node), "<module>"), exc, node.lineno))
    return found


def test_every_handler_either_logs_or_is_a_documented_absence() -> None:
    handlers = _non_logging_handlers()
    unexpected = [
        f"{fn}:{line} (except {exc})"
        for fn, exc, line in handlers
        if (fn, exc) not in _ALLOWED_NON_LOGGING
    ]
    assert unexpected == [], (
        f"handler(s) swallow a failure without a record: {unexpected}"
    )


def test_the_allow_list_is_not_vacuous() -> None:
    """Every allow-listed entry must really describe a live non-logging handler."""
    found = {(fn, exc) for fn, exc, _line in _non_logging_handlers()}
    missing = set(_ALLOWED_NON_LOGGING) - found
    assert not missing, (
        f"allow-listed handler(s) no longer exist: {sorted(missing)} "
        "-- the allow-list is stale, not the code"
    )


def test_the_module_scan_is_not_vacuous() -> None:
    """Control: the walk must find the whole handler population, not a slice."""
    tree = _tree()
    handlers = [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]
    assert len(handlers) >= 15, f"only {len(handlers)} handlers found -- the walk is broken"
    logging = [h for h in handlers if _logs(h)]
    assert len(logging) >= 10, f"only {len(logging)} handlers log -- the scan is off"


# ── behavioural half: the failure really reaches a record ───────────────────


class _TaskManager:
    """Matches production: ``get_task`` returns a dict, ``pause_task`` may raise."""

    def __init__(self, status: str, *, pause_raises: bool) -> None:
        self._status = status
        self._pause_raises = pause_raises

    def get_task(self, task_id: str) -> dict[str, Any]:
        return {"status": self._status}

    def pause_task(self, task_id: str) -> None:
        if self._pause_raises:
            raise RuntimeError("task manager unavailable")


class _EngineStub:
    """Only the surface ``apply_task_state`` touches, plus a fixed plan state."""

    def __init__(self, state: TaskFinalState, task_manager: _TaskManager) -> None:
        self._state = state
        self._task_manager = task_manager

    def evaluate_plan_state(self, plan: Any) -> TaskFinalState:
        return self._state


@pytest.mark.parametrize(
    "state",
    [TaskFinalState.HAS_REQUIRES_OBSERVATION, TaskFinalState.HAS_WAITING_DEPENDENCY],
    ids=["requires_observation", "waiting_dependency"],
)
def test_a_failing_pause_is_named(state: TaskFinalState, caplog) -> None:
    engine = _EngineStub(state, _TaskManager("running", pause_raises=True))
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        TaskExecutionEngine.apply_task_state(engine, "t-1", None)  # type: ignore[arg-type]

    messages = [r.getMessage() for r in caplog.records if r.name == _LOGGER]
    assert any("t-1" in m for m in messages), (
        f"{state.name}: the failed pause left no record naming the task; got {messages}"
    )


@pytest.mark.parametrize(
    "state",
    [TaskFinalState.HAS_REQUIRES_OBSERVATION, TaskFinalState.HAS_WAITING_DEPENDENCY],
    ids=["requires_observation", "waiting_dependency"],
)
def test_a_successful_pause_stays_silent(state: TaskFinalState, caplog) -> None:
    """Control: a pause that succeeds must not warn."""
    engine = _EngineStub(state, _TaskManager("running", pause_raises=False))
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        TaskExecutionEngine.apply_task_state(engine, "t-1", None)  # type: ignore[arg-type]

    assert [r for r in caplog.records if r.name == _LOGGER] == []


class _RaisingCatalog:
    def resolve(self, cap_id: str) -> None:
        raise RuntimeError("catalog reload failed")


class _BrokerStub:
    _catalog = _RaisingCatalog()


class _EngineWithBroker:
    _tool_broker = _BrokerStub()


def test_a_failed_manifest_resolution_is_named(caplog) -> None:
    """`resolve` returns None for an unknown id, so a raise here is unexpected -- name it."""
    request = SimpleNamespace(capability_id="cap.x")
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        TaskExecutionEngine._attach_manifest_completion(
            _EngineWithBroker(), request, SimpleNamespace()
        )

    messages = [r.getMessage() for r in caplog.records if r.name == _LOGGER]
    assert any("cap.x" in m for m in messages), (
        f"the failed manifest resolution left no record naming the capability; got {messages}"
    )


def test_a_resolved_manifest_is_silent(caplog) -> None:
    """Control: a successful resolution must not log."""
    class _OkCatalog:
        def resolve(self, cap_id: str) -> None:
            return None

    class _OkBroker:
        _catalog = _OkCatalog()

    class _OkEngine:
        _tool_broker = _OkBroker()

    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        TaskExecutionEngine._attach_manifest_completion(
            _OkEngine(), SimpleNamespace(capability_id="cap.x"), SimpleNamespace()
        )

    assert [r for r in caplog.records if r.name == _LOGGER] == []
