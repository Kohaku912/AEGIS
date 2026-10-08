"""The inert chat SSE surface is gone — pin the deletion, not the fact that it was dead.

Why this file exists
--------------------
``GET /api/chat/events`` was registered and returned ``text/event-stream``, so it *looked*
live. It was dead on **both** ends (measured 2026-10-03), which is two independent facts:

* **No publisher.** ``dashboard_legacy.py`` kept ``_chat_event_clients``, but the map was
  only ever *written*: ``_register_chat_client`` inserted a fresh ``queue.Queue`` and
  ``_unregister_chat_client`` popped it. Nothing ever put into a queue, so a connected
  client received heartbeats and nothing else, forever.
* **No subscriber.** The path string occurred in exactly **one** file — the definition.
  The repo's only ``EventSource`` targets a **different** channel (``/api/ui/stream``,
  ``web-ui/src/api/useOverviewStream.ts:24``).

The owner **deleted** the surface (2026-10-08, ``DELEGATION.md`` §4 item 23) rather than
wiring it: wiring would have meant inventing a producer for a channel nobody consumes.

This file replaces ``test_chat_sse_route_stays_dead.py``, which pinned the *fact* that the
route was inert. Once the surface is deleted that pin has no subject, and its "not wired"
direction has no counterpart — so the pin is **inverted**: it now asserts the absence, with
non-vacuity controls so a scan that stops reading the tree fails rather than passing.

How it checks
-------------
1. the **sibling** chat routes are still registered, compared for **equality** — a parser
   that stops matching empties the set and fails here rather than below;
2. the deleted path is not among them;
3. the scans still read the tree — a floor on the file count, plus a **control identifier**
   (unrelated to this deletion) that must still be found, so "found nothing" cannot pass
   for "nothing is there";
4. no source file under ``ai-server/src`` names the removed registry, its lock, or the two
   helpers.

**This file will fail the day someone re-adds the channel.** That is the point: the pin and
the record must move together, deliberately.
"""

from __future__ import annotations

import ast
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]

_SRC = _REPO / "ai-server" / "src"
_ROUTE_FILE = _SRC / "aegis_ai" / "web" / "routes" / "chat.py"
_REGISTRY_FILE = _SRC / "aegis_ai" / "web" / "dashboard_legacy.py"

#: The path that was deleted.
_DELETED_PATH = "/api/chat/events"

#: The chat blueprint's remaining routes. **Equality**, so a parser that stops matching —
#: or a route that silently disappears — is a failure rather than a smaller set.
_REMAINING_ROUTES = frozenset({
    "/api/chat/history",
    "/api/chat/clear",
    "/api/chat/send",
    "/api/chat/respond",
})

#: Every name the deletion removed from ``dashboard_legacy.py``.
_REMOVED_NAMES = (
    "_chat_event_clients",
    "_chat_event_lock",
    "_register_chat_client",
    "_unregister_chat_client",
)

#: A name that must still be present — it is unrelated to this deletion, so its absence
#: means the AST scan is broken, not that the code is clean.
_CONTROL_NAME = "_chat_history_path"

#: A floor, so an empty walk cannot make the absence checks pass vacuously.
_MIN_SOURCE_FILES = 200


def _sources() -> list[Path]:
    return [
        p
        for p in _SRC.rglob("*.py")
        if "__pycache__" not in p.parts and ".venv" not in p.parts
    ]


def _names_in(path: Path) -> set[str]:
    """Every attribute name and function name the module mentions."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names


def _route_paths() -> set[str]:
    """Every path a ``@bp.route(...)`` decorator in the chat blueprint registers."""
    tree = ast.parse(_ROUTE_FILE.read_text(encoding="utf-8"), filename=str(_ROUTE_FILE))
    paths: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "route"):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                paths.add(arg.value)
    return paths


# ── Non-vacuity: the blueprint still exists, and the scans still read ─────────


def test_the_sibling_chat_routes_are_still_registered() -> None:
    paths = _route_paths()
    assert paths == _REMAINING_ROUTES, (
        f"{_ROUTE_FILE} registers {sorted(paths)}, expected {sorted(_REMAINING_ROUTES)}.\n"
        "  - an *extra* path means a route was added — is the SSE channel back?\n"
        "  - a *missing* path means either a route was deleted or the parser stopped "
        "matching; both must be resolved deliberately, never by loosening this set"
    )


def test_the_scans_actually_read_the_tree() -> None:
    files = _sources()
    assert len(files) >= _MIN_SOURCE_FILES, (
        f"only {len(files)} source files found (floor {_MIN_SOURCE_FILES}); a root moved "
        "and the absence checks below would pass vacuously"
    )
    assert _CONTROL_NAME in _names_in(_REGISTRY_FILE), (
        f"the control name {_CONTROL_NAME!r} was not found in {_REGISTRY_FILE}. That name is "
        "unrelated to this deletion, so its absence means the AST scan is broken — not that "
        "the code is clean."
    )


# ── The deletion ─────────────────────────────────────────────────────────────


def test_the_deleted_path_is_not_registered() -> None:
    assert _DELETED_PATH not in _route_paths(), (
        f"{_ROUTE_FILE} registers {_DELETED_PATH} again. The surface was deleted 2026-10-08 "
        "(`DELEGATION.md` §4 item 23) because it was inert on both ends; re-adding it means "
        "either a producer or a consumer now exists — re-measure and update this pin."
    )


def test_no_source_file_names_the_removed_registry_or_helpers() -> None:
    found: dict[str, list[str]] = {}
    for path in _sources():
        hits = sorted(n for n in _REMOVED_NAMES if n in _names_in(path))
        if hits:
            found[path.relative_to(_REPO).as_posix()] = hits
    assert found == {}, (
        f"the deleted chat-event registry is still named: {found}.\n"
        "  These four names were removed together with the inert SSE route (2026-10-08). A "
        "new mention is either a re-introduction (which needs a publisher *and* a "
        "subscriber) or a leftover reference to a name that no longer exists."
    )
