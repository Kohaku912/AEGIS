"""L1 now runs off the publisher's thread, mirroring L2 (DELEGATION.md section 4 item 48).

Measured 2026-10-05 (the record). L2 had been moved onto a dedicated single worker
by E-2 (``_submit_background_l2``) while L1 still ran inline:
``_evaluate_immediate_event`` called ``_run_l1_pipeline_for_event`` directly, and that
awaits ``router.observe(...)`` -- the L1 LLM round-trip. Since
``EventBus._notify_subscribers`` (``src/event_bus.py:234``) calls handlers on the
publisher's thread, and one publisher is the gRPC ``PushEvent`` handler, a remote push
occupied a request thread for the whole L1 call.

Item 48 option (1) was selected: give L1 the same shape as L2. This file used to pin the
*asymmetry* (``test_l1_has_no_background_submitter``); it is **inverted**, not deleted.
It now pins the symmetry and fails in both directions -- removing
``_submit_background_l1`` or putting the inline call back turns it red.

**What this file does not claim.** The *background* route
(``_handle_background_l1_event``) still runs its L1 call inline; item 48 was scoped to the
immediate route. The last test pins that boundary so widening it has to be deliberate.
Nor does it claim a capacity: there is no load test here, only thread affinity.
"""

from __future__ import annotations

import ast
import threading
import time
from pathlib import Path
from typing import Any

import aegis_ai.runtime as runtime_module
from aegis_schema.models import Event, EventPriority, ServerType

SRC = Path(__file__).resolve().parents[1] / "src"
_RUNTIME = SRC / "aegis_ai" / "runtime.py"

_IMMEDIATE_HANDLER = "_evaluate_immediate_event"
_BACKGROUND_HANDLER = "_handle_background_l1_event"
_L1_PIPELINE = "_run_l1_pipeline_for_event"
_L1_SUBMITTER = "_submit_background_l1"
_L1_WORKER = "_run_l1_immediate_pipeline"

_PROBE_TIMEOUT_S = 5.0


def _functions() -> dict[str, ast.AST]:
    tree = ast.parse(_RUNTIME.read_text(encoding="utf-8"), filename=str(_RUNTIME))
    return {
        n.name: n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _called_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            names.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", ""))
    return names


def _event() -> Event:
    return Event(
        event_id="evt-probe",
        event_type="probe.thread_affinity",
        source_server_type=ServerType.ANDROID,
        source_server_id="probe-server",
        timestamp_ms=1,
        payload_json="{}",
        priority=EventPriority.NORMAL,
    )


def test_l2_still_has_a_background_submitter() -> None:
    """Control: the scan sees the submitter that already existed."""
    assert "_submit_background_l2" in _functions()


def test_l1_has_a_background_submitter() -> None:
    functions = _functions()
    assert _L1_SUBMITTER in functions, (
        "L1 lost its background submitter -- if the offload was reverted, update "
        "DELEGATION.md section 4 item 48 (L1 runs inline again)"
    )


def test_the_immediate_handler_submits_instead_of_calling_the_pipeline() -> None:
    functions = _functions()
    assert _IMMEDIATE_HANDLER in functions, (
        f"{_IMMEDIATE_HANDLER} is gone from runtime.py -- the immediate path was renamed "
        "or moved; update DELEGATION.md section 4 item 48"
    )
    called = _called_names(functions[_IMMEDIATE_HANDLER])
    assert _L1_SUBMITTER in called, (
        f"{_IMMEDIATE_HANDLER} does not submit the L1 work -- the immediate route is back "
        "on the publisher's thread; update DELEGATION.md section 4 item 48"
    )
    assert _L1_PIPELINE not in called, (
        f"{_IMMEDIATE_HANDLER} calls {_L1_PIPELINE} inline again -- a handler runs on the "
        "publisher's thread, so the LLM round-trip blocks it (item 48)"
    )


def test_the_immediate_handler_passes_the_event_to_the_submitter() -> None:
    """A call that exists is not a call that carries the event (item 48's whole point).

    Without this, ``_submit_background_l1(rt, event=None)`` -- or submitting a different
    argument -- would keep every other assertion here green while the offload did nothing.
    """
    functions = _functions()
    calls = [
        n
        for n in ast.walk(functions[_IMMEDIATE_HANDLER])
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == _L1_SUBMITTER
    ]
    assert len(calls) == 1, (
        f"expected exactly one {_L1_SUBMITTER} call in {_IMMEDIATE_HANDLER}, found {len(calls)}"
    )
    passed = {kw.arg: kw.value for kw in calls[0].keywords}
    assert "event" in passed, (
        f"{_L1_SUBMITTER} must receive the event by keyword -- got keywords {sorted(passed)}"
    )
    assert isinstance(passed["event"], ast.Name) and passed["event"].id == "event", (
        f"{_L1_SUBMITTER}(..., event=...) must pass the handler's own event, "
        f"got {ast.dump(passed['event'])}"
    )


def test_the_background_l1_helper_runs_the_pipeline_off_the_calling_thread(monkeypatch) -> None:
    """The fix: the helper must not execute the L1 route on the thread that submitted it."""
    calls: list[str] = []

    def fake_pipeline(runtime: Any, event: Any) -> None:
        calls.append(threading.current_thread().name)

    monkeypatch.setattr(runtime_module, _L1_WORKER, fake_pipeline)

    class _FakeRuntime:
        """Bare object -- the helper only needs somewhere to hang its executor."""

    runtime = _FakeRuntime()
    caller_thread = threading.current_thread().name
    runtime_module._submit_background_l1(runtime, event=_event())

    deadline = time.monotonic() + _PROBE_TIMEOUT_S
    while not calls and time.monotonic() < deadline:
        time.sleep(0.01)

    executor = getattr(runtime, "_background_l1_executor", None)
    try:
        # Non-vacuity floor: weaker than the assertions below.
        assert calls, "the pipeline never ran -- the probe is vacuous"
        assert calls[0] != caller_thread, (
            "background L1 ran on the caller's thread; the offload is ineffective (item 48)"
        )
        assert calls[0].startswith("aegis-background-l1"), (
            f"background L1 ran on an unexpected thread: {calls[0]!r}"
        )
    finally:
        if executor is not None:
            executor.shutdown(wait=False)


def test_the_background_l1_worker_reports_its_own_failures() -> None:
    """The loudness half of item 48.

    On the publisher's thread an exception from a subscriber reaches
    ``EventBus._dead_letter_handler``. Once the work is handed to a worker, nothing above
    the callable can report it -- the future holds it -- so the logging has to live inside.
    Without this the offload would convert a loud failure into a silent one.
    """
    worker = _functions().get(_L1_WORKER)
    assert worker is not None, f"{_L1_WORKER} is gone -- update DELEGATION.md section 4 item 48"

    handlers = [
        handler
        for node in ast.walk(worker)
        if isinstance(node, ast.Try)
        for handler in node.handlers
    ]
    assert handlers, (
        f"{_L1_WORKER} has no try/except -- a failure on the worker thread would be silent"
    )

    logged = [
        node
        for handler in handlers
        for node in ast.walk(handler)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"exception", "error", "critical"}
    ]
    assert logged, (
        f"{_L1_WORKER} catches without logging -- the failure would be silent (item 48)"
    )


def test_the_background_route_is_still_inline() -> None:
    """Boundary: item 48 scoped the offload to the *immediate* route."""
    background = _functions().get(_BACKGROUND_HANDLER)
    assert background is not None, (
        f"{_BACKGROUND_HANDLER} is gone -- if the two routes were merged, update "
        "DELEGATION.md section 4 item 48"
    )
    called = _called_names(background)
    assert _L1_PIPELINE in called, (
        f"{_BACKGROUND_HANDLER} no longer calls {_L1_PIPELINE} inline -- if the background "
        "route was detached too, that widens item 48; update the record"
    )
    assert _L1_SUBMITTER not in called, (
        f"{_BACKGROUND_HANDLER} now submits to the same worker -- item 48 scoped the offload "
        "to the immediate route only; update DELEGATION.md section 4 item 48"
    )
