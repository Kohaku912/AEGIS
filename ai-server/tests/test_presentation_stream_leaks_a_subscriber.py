"""``/api/presentations/stream`` retains an event-bus subscriber per request.

Why this file exists
--------------------
``manager_routes.presentation_stream`` is a registered SSE route. Measured 2026-10-03,
it leaks one event-bus subscriber **per request**, permanently:

* ``rt.event_manager.subscribe(_on_event)`` is called at **route-function scope**
  (``manager_routes.py:917``), i.e. once per request, *before* the generator is even
  started — and its **return value is discarded**, so the subscriber id cannot be
  released later.
* The generator's only cleanup is ``except GeneratorExit: pass``. There is **no
  ``unsubscribe`` call anywhere in the module**.
* The queue is built **unbounded** (``queue.Queue()``), so the retained handler keeps
  appending every ``presentation.*`` payload to a queue that nothing drains once the
  client is gone.

Measured by driving the route, not by reading it — with a fake event manager:

* after the route function runs: **1** subscriber;
* after firing an event, advancing the generator, and closing it (the client
  disconnects): **still 1**. The subscriber is retained.

The sibling push routes are the **positive control** — same package, same idea, done
right: ``routes/ui.py`` keeps the id from ``subscribe`` and calls ``unsubscribe`` in a
``finally`` (measured: **1 → 0**), and ``routes/approval.py`` keeps the remover returned
by ``store.add_listener`` and calls it in a ``finally``. Both bound their queue
(``maxsize=200`` / ``_CLIENT_QUEUE_SIZE``). So this is not "the codebase does not know
how to do it" — it is one route that does not.

Impact is **latent**: no client subscribes today (the path is named in exactly one file,
its own definition), so the leak cannot fire in production yet — but it fires on the
**first** connection, and compounds per connection. Fixing it (move ``subscribe`` inside
the generator, bound the queue, release in ``finally``) or deleting the route is an
**owner decision** (recorded in ``DELEGATION.md`` §4), so this pins the fact instead.

**This file will fail the day someone fixes the leak.** That is the point: the pin and
the record must move together, deliberately.
"""

from __future__ import annotations

import ast
import queue
from pathlib import Path
from types import SimpleNamespace

import pytest

from aegis_ai.web import manager_routes

_REPO = Path(__file__).resolve().parents[2]
_WEB = _REPO / "ai-server" / "src" / "aegis_ai" / "web"

_PRESENTATIONS = _WEB / "manager_routes.py"
_UI = _WEB / "routes" / "ui.py"
_APPROVAL = _WEB / "routes" / "approval.py"

_ROUTE_PATH = "/api/presentations/stream"

#: The route function that subscribes, and the generator it returns. The *enclosing
#: function* of the ``subscribe`` call is the defect: inside the generator would be fine.
_ROUTE_FUNCTION = "presentation_stream"
_GENERATOR_FUNCTION = "generate"

#: Recorded 2026-10-03: the web-package files that construct an **unbounded** queue.
#: **Equality** — a new one is a new unbounded buffer, and either moves the record.
_RECORDED_UNBOUNDED_QUEUES = frozenset({"manager_routes.py", "dashboard_legacy.py"})

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


# ── The defect, measured by driving the route ────────────────────────────────


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


def test_the_route_retains_its_subscriber_after_the_client_disconnects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Open the route, advance the generator, disconnect: the subscriber stays."""
    em = _FakeEventManager()
    monkeypatch.setattr(
        manager_routes, "_get_runtime", lambda: SimpleNamespace(event_manager=em)
    )

    response = manager_routes.presentation_stream()
    assert len(em.handlers) == 1, (
        "the route function did not subscribe at all — the harness is wrong, or the "
        "route was rewritten"
    )

    iterator = iter(response.response)
    for handler in list(em.handlers.values()):
        handler("presentation.created", {"id": "probe"})  # type: ignore[operator]
    next(iterator)  # start the generator, so close() is meaningful
    iterator.close()  # the client disconnects

    assert len(em.handlers) == 1, (
        "the subscriber was released on disconnect — the leak is fixed. Re-measure and "
        "update DELEGATION.md §4 and this pin together."
    )


# ── The mechanism, measured statically (tool-free) ───────────────────────────


def test_the_subscribe_call_is_not_inside_the_generator() -> None:
    tree = _parsed(_PRESENTATIONS)
    calls = _calls(tree, "subscribe")
    assert len(calls) == 1, (
        f"expected exactly one subscribe call in {_PRESENTATIONS.name}, found "
        f"{len(calls)}; re-measure"
    )
    where = _enclosing(tree, calls[0].lineno)
    assert where == _ROUTE_FUNCTION, (
        f"the subscribe call is now inside {where!r} (expected {_ROUTE_FUNCTION!r}). "
        "Moving it into the generator is the fix — if that is deliberate, this pin and "
        "DELEGATION.md §4 must move together."
    )
    assert where != _GENERATOR_FUNCTION, "the subscribe call moved into the generator"


def test_the_presentations_module_never_unsubscribes() -> None:
    """The positive control: the sibling routes *do* release, this one does not."""
    tree = _parsed(_PRESENTATIONS)
    unsubscribes = _calls(tree, "unsubscribe")
    assert unsubscribes == [], (
        f"{_PRESENTATIONS.name} now calls unsubscribe at line(s) "
        f"{[c.lineno for c in unsubscribes]} — the leak is being fixed; re-measure and "
        "update DELEGATION.md §4 and this pin together."
    )

    ui_tree = _parsed(_UI)
    assert _calls(ui_tree, "unsubscribe"), (
        f"{_UI.name} no longer calls unsubscribe; the control that proves a release is "
        "detectable is gone, so the assertion above would pass vacuously"
    )
    approval_src = _APPROVAL.read_text(encoding="utf-8")
    assert "add_listener" in approval_src and "unsubscribe()" in approval_src, (
        f"{_APPROVAL.name} no longer keeps the remover returned by add_listener; the "
        "second control is gone"
    )


def test_the_presentations_queue_is_unbounded() -> None:
    assert _unbounded_queue_files() == _RECORDED_UNBOUNDED_QUEUES, (
        "the set of web-package files building an unbounded queue changed: "
        f"{sorted(_unbounded_queue_files())} != {sorted(_RECORDED_UNBOUNDED_QUEUES)}. "
        "A *new* entry is a new unbounded buffer; a *missing* one means a queue was "
        "bounded (good) — re-measure and re-record."
    )
    assert queue.Queue is not None  # the import is the subject, not a stub
