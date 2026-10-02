"""The chat SSE route is dead on **both** ends — pin the fact, not a fix.

Why this file exists
--------------------
``GET /api/chat/events`` is registered (``web/routes/chat.py``) and its generator loops
forever emitting a 15-second heartbeat. It *looks* live: the route returns
``text/event-stream``, and the handler genuinely registers a client queue.

Measured 2026-10-03 — it is dead on **both** ends, which is two independent facts:

* **No publisher.** ``dashboard_legacy.py`` keeps ``_chat_event_clients``, but the map is
  only ever *written*: ``_register_chat_client`` inserts a fresh ``queue.Queue`` and
  ``_unregister_chat_client`` pops it. Nothing ever puts into a queue, so a connected
  client receives heartbeats and nothing else, forever.
* **No subscriber.** The path string occurs in exactly **one** file — the definition —
  across every source tree in the repo. The repo's only ``EventSource`` targets a **different**
  channel (``/api/ui/stream``, ``web-ui/src/api/useOverviewStream.ts:24``), so "the UI streams"
  is satisfied by an unrelated route, not this one.

Neither scan alone is evidence: a route with a subscriber but no publisher is a broken
feature, and one with a publisher but no subscriber is an orphan. Together they say the
endpoint is *inert*. Wiring it or deleting it is an **owner decision** (recorded in
``DELEGATION.md`` §4), so this pins the fact instead.

How it checks. Three properties, each with a non-vacuity half, so a scan that stops
reading the tree fails rather than passing silently:

1. the route is still registered (the subject exists);
2. the registry is still *write-only* — the set of syntactic uses of
   ``_chat_event_clients`` equals the recorded set, so a new reader (a publisher) is a
   failure;
3. the path has no subscriber — the set of source files naming it equals
   ``{the definition}``.

**This file will fail the day someone wires it.** That is the point: the pin and the
record must move together, deliberately.
"""

from __future__ import annotations

import ast
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]

#: The definition, and the only source file allowed to name the path.
_ROUTE_FILE = _REPO / "ai-server" / "src" / "aegis_ai" / "web" / "routes" / "chat.py"
_ROUTE_PATH = "/api/chat/events"

#: Every source tree a subscriber could live in.
_SOURCE_ROOTS = (
    _REPO / "ai-server" / "src",
    _REPO / "web-ui" / "src",
    _REPO / "pc-server" / "src",
    _REPO / "browser-server" / "src",
    _REPO / "room-server",
    _REPO / "packages" / "aegis-sdk-python",
)

#: The registry's identifier, and the syntactic uses that are all accounted for:
#: the declaration, the insert, and the removal. A publisher adds a fourth.
_REGISTRY = "_chat_event_clients"
_REGISTRY_FILE = _REPO / "ai-server" / "src" / "aegis_ai" / "web" / "dashboard_legacy.py"
_RECORDED_USES = frozenset({"decl", "insert", "method:pop"})

#: A floor, so an empty walk cannot make the subscriber scan vacuously pass.
_MIN_SOURCE_FILES = 200


def _sources(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return [
        p
        for p in root.rglob("*.py")
        if "__pycache__" not in p.parts and ".venv" not in p.parts
    ] + [
        p
        for p in root.rglob("*.ts")
        if "node_modules" not in p.parts
    ] + [
        p
        for p in root.rglob("*.tsx")
        if "node_modules" not in p.parts
    ]


def _all_sources() -> list[Path]:
    seen: list[Path] = []
    for root in _SOURCE_ROOTS:
        seen.extend(_sources(root))
    return seen


def _parents(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    out: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            out[child] = node
    return out


def _registry_uses(tree: ast.AST) -> set[str]:
    """Classify every reference to the registry by *how* it is used."""
    parents = _parents(tree)
    uses: set[str] = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Attribute) and node.attr == _REGISTRY):
            continue
        parent = parents.get(node)
        if isinstance(parent, ast.AnnAssign):
            uses.add("decl")
        elif isinstance(parent, ast.Subscript) and isinstance(parent.ctx, ast.Store):
            uses.add("insert")
        elif isinstance(parent, ast.Attribute):
            uses.add(f"method:{parent.attr}")
        else:
            uses.add(f"other:{type(parent).__name__}")
    return uses


# ── Non-vacuity: the subject still exists, and the scans still read ───────────


def test_the_route_is_still_registered() -> None:
    text = _ROUTE_FILE.read_text(encoding="utf-8")
    assert f'"{_ROUTE_PATH}"' in text, (
        f"{_ROUTE_FILE} no longer registers {_ROUTE_PATH}. If the route was deleted, "
        "that was an owner decision — update DELEGATION.md §4 and this pin together."
    )


def test_the_scans_actually_read_the_tree() -> None:
    files = _all_sources()
    assert len(files) >= _MIN_SOURCE_FILES, (
        f"only {len(files)} source files found (floor {_MIN_SOURCE_FILES}); a root moved "
        "and the subscriber scan would pass vacuously"
    )


def test_the_registry_is_still_write_only() -> None:
    """A publisher would add a fourth use. Equality, so it cannot slip in quietly."""
    tree = ast.parse(
        _REGISTRY_FILE.read_text(encoding="utf-8"), filename=str(_REGISTRY_FILE)
    )
    uses = _registry_uses(tree)
    assert uses == _RECORDED_USES, (
        f"uses of {_REGISTRY} are {sorted(uses)}, expected {sorted(_RECORDED_USES)}.\n"
        "  - a new 'method:values'/'method:get'/'method:items' use means something now "
        "*reads* the queues -> a publisher exists -> the route is no longer dead\n"
        "  - a missing use means the registry was refactored -> re-measure and re-record"
    )


def test_no_queue_is_ever_written_to_in_the_registry_owner() -> None:
    """The second half of "no publisher", and the one the use-set cannot see.

    ``_registry_uses`` only classifies references to the *registry attribute*, so a
    publisher written against the local (``q.put(...)``, where ``q`` came out of
    ``_register_chat_client``) would slip past it. Measured 2026-10-03, the file's only
    queue is this registry's, so "no ``put`` anywhere in the file" is both true and
    exactly the property that makes the route inert.
    """
    tree = ast.parse(
        _REGISTRY_FILE.read_text(encoding="utf-8"), filename=str(_REGISTRY_FILE)
    )
    writers = [
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"put", "put_nowait"}
    ]
    assert writers == [], (
        f"{_REGISTRY_FILE} now calls {sorted(set(writers))} on a queue. The file's only "
        "queue is the chat-event registry, so this is a **publisher** — the SSE route is "
        "alive and both this pin and DELEGATION.md §4 are stale."
    )


def test_no_source_file_outside_the_definition_names_the_route() -> None:
    """No subscriber: the path occurs in exactly one file, the definition itself."""
    namers = {
        p
        for p in _all_sources()
        if _ROUTE_PATH in p.read_text(encoding="utf-8", errors="ignore")
    }
    assert namers == {_ROUTE_FILE}, (
        f"{_ROUTE_PATH} is named by {sorted(str(p) for p in namers)}; expected only "
        f"{_ROUTE_FILE}. A second file means a subscriber appeared — the route is alive "
        "and this pin (plus DELEGATION.md §4) is stale."
    )
