"""/api/presentations/stream: a *live* SSE route that is also *sound* and *consumed*.

Why this file exists
--------------------
``manager_routes.presentation_stream`` was measured 2026-10-03 to be broken in **three**
independent ways, none of them visible from outside the route:

1. **The handler could never run.** ``EventBus._notify_subscribers`` calls
   ``sub.handler(event)`` with **one** argument (``event_bus.py:241``), but the route
   registered ``_on_event(event_type, payload)`` — **two**. The ``TypeError`` was caught by
   the notify loop and routed to the dead-letter handler (``:243-246``), so the subscriber
   was registered, counted, and **never fired**.
2. **The subscription was never released.** ``subscribe`` was called at route-function scope
   and its **return value discarded**, and the module contained **no ``unsubscribe`` call at
   all** — so every request retained one subscriber for ever (measured **1 -> 1** on
   disconnect; the sibling ``routes/ui.py`` measures **1 -> 0**).
3. **The queue was unbounded** (``queue.Queue()``), so a disconnected client left a handler
   appending to a buffer that nothing drained.

**Why one pin and not three files.** (1) and (2) are one defect seen from two ends: the route
subscribed a handler it could neither call nor remove. (3) is what made the leak silent. And
fixing only the leak — the shape the first record described — would have left the route
**dead**: a route that is *live* (registered, and it does subscribe) is not therefore *sound*
(the subscriber works) or *consumed* (someone drains it). **live / unconsumed / sound are
three axes, not one count.**

This pin asserts the **fix**, and each assertion has the regression it exists to catch:

* the handler is called the way the bus calls it (**one** argument) and the payload
  **arrives** -> catches a return to the two-argument shape, which is silent;
* a non-``presentation.*`` event is **filtered out** -> catches the filter being dropped;
* the subscriber count goes **1 -> 0** on disconnect -> catches the leak returning;
* the handler takes **exactly one** parameter, read statically -> catches the arity contract
  drifting without needing a driver at all;
* ``subscribe``'s return value is **assigned** and ``unsubscribe`` runs in the generator's
  ``finally`` -> catches "subscribed, but not removable";
* the queue is **bounded** -> catches the silent-buffer half.

The sibling routes are the **positive controls** — ``routes/ui.py`` keeps the id and releases
in a ``finally`` with ``maxsize=200``; ``routes/approval.py`` keeps the remover from
``store.add_listener``. They are asserted *alongside*, so a harness bug that made "release"
undetectable could not let the assertions above pass vacuously.
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from aegis_ai.web import manager_routes
from aegis_schema.models import Event, ServerType

_REPO = Path(__file__).resolve().parents[2]
_WEB = _REPO / "ai-server" / "src" / "aegis_ai" / "web"

_PRESENTATIONS = _WEB / "manager_routes.py"
_UI = _WEB / "routes" / "ui.py"
_APPROVAL = _WEB / "routes" / "approval.py"

_ROUTE_PATH = "/api/presentations/stream"

#: The route function, the generator it returns, and the handler it registers with the bus.
_ROUTE_FUNCTION = "presentation_stream"
_GENERATOR_FUNCTION = "generate"
_HANDLER_FUNCTION = "_on_event"

#: Recorded 2026-10-03: web-package files that construct an **unbounded** queue.
#: ``manager_routes.py`` was removed from this set on 2026-10-03 — its SSE queue is now
#: bounded (``_PRESENTATION_QUEUE_SIZE``), which is half of this fix.
#: **Equality** — a new entry is a new unbounded buffer; a missing one means a queue was
#: bounded (good). Either way, re-measure and re-record.
_RECORDED_UNBOUNDED_QUEUES = frozenset({"dashboard_legacy.py"})

_MIN_SRC_FILES = 300


# ── Scans ────────────────────────────────────────────────────────────────────


def _src_files() -> list[Path]:
    root = _REPO / "ai-server" / "src"
    return [
        p
        for p in root.rglob("*.py")
        if "__pycache__" not in p.parts and ".venv" not in p.parts
    ]


def _parsed(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _parents(tree: ast.Module) -> dict[int, ast.AST]:
    out: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            out[id(child)] = node
    return out


def _enclosing(tree: ast.Module, lineno: int) -> str:
    """Innermost enclosing function name for a line, else ``"<module>"``."""
    best: tuple[int, str] | None = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= lineno <= (node.end_lineno or node.lineno):
                if best is None or node.lineno > best[0]:
                    best = (node.lineno, node.name)
    return best[1] if best else "<module>"


def _call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _calls(tree: ast.Module, name: str) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and _call_name(node) == name
    ]


def _function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _in_finally(tree: ast.Module, call: ast.Call) -> bool:
    """Whether ``call`` sits inside the ``finally`` block of some enclosing ``try``."""
    parents = _parents(tree)
    node: ast.AST = call
    while id(node) in parents:
        node = parents[id(node)]
        if isinstance(node, ast.Try):
            if any(any(x is call for x in ast.walk(stmt)) for stmt in node.finalbody):
                return True
    return False


def _unbounded_queue_files() -> set[str]:
    """Web-package files that build a ``queue.Queue`` with no ``maxsize``."""
    found: set[str] = set()
    for path in _src_files():
        if _WEB not in path.parents and path != _WEB:
            continue
        for node in _calls(_parsed(path), "Queue"):
            has_maxsize = any(kw.arg == "maxsize" for kw in node.keywords) or len(node.args) >= 1
            if not has_maxsize:
                found.add(path.name)
    return found


def _event(event_type: str, payload_json: str) -> Event:
    """A real ``Event`` — so the handler's field names are checked against the model."""
    return Event(
        event_id=f"e-{event_type}",
        event_type=event_type,
        source_server_type=ServerType.AI,
        source_server_id="test",
        payload_json=payload_json,
    )


class _FakeEventManager:
    """A counting stand-in: `subscribe` registers, `unsubscribe` removes."""

    def __init__(self) -> None:
        self.handlers: dict[str, object] = {}
        self._n = 0

    def subscribe(self, handler: object, event_filter: object = None) -> str:
        self._n += 1
        sid = f"s{self._n}"
        self.handlers[sid] = handler
        return sid

    def unsubscribe(self, sid: str) -> bool:
        return self.handlers.pop(sid, None) is not None


def _route_with(monkeypatch: pytest.MonkeyPatch) -> tuple[object, _FakeEventManager]:
    em = _FakeEventManager()
    monkeypatch.setattr(
        manager_routes, "_get_runtime", lambda: SimpleNamespace(event_manager=em)
    )
    return manager_routes.presentation_stream(), em


# ── Non-vacuity: the subject exists and the scans still read ─────────────────


def test_the_scan_reads_the_tree_and_the_route_exists() -> None:
    files = _src_files()
    assert len(files) >= _MIN_SRC_FILES, (
        f"only {len(files)} source files found (floor {_MIN_SRC_FILES}); a root moved "
        "and the scans would pass vacuously"
    )
    for path in (_PRESENTATIONS, _UI, _APPROVAL):
        assert path.exists(), f"{path} is gone; re-measure and update DELEGATION.md §4"
    assert f'"{_ROUTE_PATH}"' in _PRESENTATIONS.read_text(encoding="utf-8"), (
        f"{_PRESENTATIONS} no longer registers {_ROUTE_PATH}. If the route was deleted, "
        "that was an owner decision — update DELEGATION.md §4 and this pin together."
    )


# ── The fix, measured by driving the route ───────────────────────────────────


def test_the_handler_delivers_a_presentation_event_and_filters_the_rest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The bus calls ``handler(event)`` with ONE argument; the payload must arrive."""
    response, em = _route_with(monkeypatch)
    assert len(em.handlers) == 1, (
        "the route function did not subscribe at all — the harness is wrong, or the route "
        "was rewritten"
    )

    for handler in list(em.handlers.values()):
        # A non-presentation event first: it must NOT reach the client.
        try:
            handler(_event("pc.screen_change", '{"id": "noise"}'))  # type: ignore[operator]
            handler(_event("presentation.created", '{"id": "probe"}'))  # type: ignore[operator]
        except TypeError as exc:
            pytest.fail(
                "the registered handler is not callable with the bus's ONE-argument shape "
                f"({exc}). `EventBus._notify_subscribers` calls `sub.handler(event)`, and a "
                "raise is dead-lettered — so a two-argument handler never runs at all."
            )

    line = next(iter(response.response))  # type: ignore[attr-defined]
    assert "presentation.created" in line and "probe" in line, (
        f"the presentation event never reached the stream (got {line!r}) — the handler is "
        "registered but not delivering"
    )
    assert "noise" not in line, (
        f"a non-presentation event reached the stream (got {line!r}) — the event_type filter "
        "is gone"
    )


def test_the_route_releases_its_subscriber_after_the_client_disconnects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """1 -> 0 on disconnect. This is the leak, and it must stay fixed."""
    response, em = _route_with(monkeypatch)
    assert len(em.handlers) == 1

    # Fire one event so the generator's `q.get()` returns at once instead of blocking.
    for handler in list(em.handlers.values()):
        handler(_event("presentation.created", '{"id": "probe"}'))  # type: ignore[operator]

    iterator = iter(response.response)  # type: ignore[attr-defined]
    next(iterator)  # start the generator, so close() is meaningful
    iterator.close()  # the client disconnects

    assert em.handlers == {}, (
        "the subscriber was retained on disconnect — the leak is back. The release belongs "
        "in the generator's `finally` (see routes/ui.py for the shape)."
    )


# ── The mechanism, measured statically (tool-free) ───────────────────────────


def test_the_handler_takes_exactly_one_argument() -> None:
    """The arity contract with the bus, pinned without needing a driver."""
    tree = _parsed(_PRESENTATIONS)
    fn = _function(tree, _HANDLER_FUNCTION)
    assert fn is not None, (
        f"{_HANDLER_FUNCTION} is gone from {_PRESENTATIONS.name}; re-measure and update "
        "DELEGATION.md §4 and this pin together"
    )
    args = fn.args
    assert args.vararg is None and args.kwarg is None, (
        f"{_HANDLER_FUNCTION} takes *args/**kwargs; the bus passes exactly ONE argument"
    )
    n = len(args.posonlyargs) + len(args.args)
    assert n == 1, (
        f"{_HANDLER_FUNCTION} takes {n} parameters. `EventBus._notify_subscribers` calls "
        "`sub.handler(event)` with ONE (event_bus.py:241) and routes a raise to the "
        "dead-letter handler (:243-246) — so a mismatch means the handler NEVER RUNS, "
        "silently, while the subscriber count still looks correct."
    )


def test_the_subscribe_return_value_is_kept_and_released_in_a_finally() -> None:
    tree = _parsed(_PRESENTATIONS)
    calls = _calls(tree, "subscribe")
    assert len(calls) == 1, (
        f"expected exactly one subscribe call in {_PRESENTATIONS.name}, found {len(calls)}; "
        "re-measure"
    )
    registered = calls[0].args[0] if calls[0].args else None
    assert isinstance(registered, ast.Name) and registered.id == _HANDLER_FUNCTION, (
        f"the route no longer registers {_HANDLER_FUNCTION}; re-measure and update this pin"
    )
    assert isinstance(_parents(tree).get(id(calls[0])), ast.Assign), (
        "the subscribe return value is discarded, so the subscriber id can never be "
        "released — assign it and call unsubscribe in the generator's `finally`"
    )

    unsubscribes = _calls(tree, "unsubscribe")
    assert unsubscribes, (
        f"{_PRESENTATIONS.name} never calls unsubscribe; the subscription cannot be released"
    )
    where = {_enclosing(tree, c.lineno) for c in unsubscribes}
    assert where == {_GENERATOR_FUNCTION}, (
        f"unsubscribe is called from {sorted(where)}, expected only "
        f"{_GENERATOR_FUNCTION!r} — releasing at route-function scope cannot work, because "
        "the generator is what outlives the request"
    )
    for call in unsubscribes:
        assert _in_finally(tree, call), (
            f"the unsubscribe at line {call.lineno} is not in a `finally`; a client that "
            "vanishes mid-stream (GeneratorExit) would skip it and leak the subscriber"
        )


def test_the_presentations_queue_is_bounded() -> None:
    tree = _parsed(_PRESENTATIONS)
    queues = _calls(tree, "Queue")
    assert queues, f"no queue.Queue construction found in {_PRESENTATIONS.name}"
    for node in queues:
        bounded = any(kw.arg == "maxsize" for kw in node.keywords) or len(node.args) >= 1
        assert bounded, (
            f"line {node.lineno}: manager_routes.py builds an UNBOUNDED queue. A client that "
            "disconnected cannot drain it, so it grows without limit."
        )

    assert _unbounded_queue_files() == _RECORDED_UNBOUNDED_QUEUES, (
        "the set of web-package files building an unbounded queue changed: "
        f"{sorted(_unbounded_queue_files())} != {sorted(_RECORDED_UNBOUNDED_QUEUES)}. "
        "A *new* entry is a new unbounded buffer; a *missing* one means a queue was bounded "
        "(good) — re-measure and re-record."
    )


def test_the_sibling_routes_still_release() -> None:
    """The positive controls: if these stop releasing, the assertions above go vacuous."""
    ui_tree = _parsed(_UI)
    ui_unsub = _calls(ui_tree, "unsubscribe")
    assert ui_unsub, (
        f"{_UI.name} no longer calls unsubscribe; the control that proves a release is "
        "detectable is gone"
    )
    assert all(_in_finally(ui_tree, c) for c in ui_unsub), (
        f"{_UI.name} calls unsubscribe outside a `finally`; it is no longer the model this "
        "pin cites"
    )
    approval_src = _APPROVAL.read_text(encoding="utf-8")
    assert "add_listener" in approval_src and "unsubscribe()" in approval_src, (
        f"{_APPROVAL.name} no longer keeps the remover returned by add_listener; the second "
        "control is gone"
    )
