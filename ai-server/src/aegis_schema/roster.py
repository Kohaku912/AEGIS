"""The canonical AEGIS server roster (B-15).

Every "which servers are there, and what is each one called" question resolves here, so the
answer exists once. Before this module the same fact was re-declared in **15 literals across 11
modules** in five value shapes (``ServerType``, short prefix, enabled flag, id prefix, host:port)
— including **five** copies of ``server_id -> ServerType``, two of which had already drifted
apart — and five of the literals still named ``dev-server``, deleted in Phase 9.

Why a module of its own rather than a constant in ``models.py``: ``tests/
test_schema_mirrors_the_protobuf_schema.py`` asserts that **every top-level class** in
``models.py`` mirrors a ``message``/``enum`` under ``protos/aegis/``, and a roster is not a
schema type. ``ServerType`` is imported from there, so ``models.py`` reaches back into this
module with a **function-level** import inside its validator — the same pattern
``tool_broker.execute()`` uses to break its own cycle.

The retired server lives here too, and *only* here. ``ServerType.DEV`` is not in
``SERVER_ROSTER`` — the roster is what exists, ``RETIRED_SERVER_ROSTER`` is what has been
withdrawn but is still reachable — but a site that answers for it now imports the entry instead
of spelling ``"dev-server"`` itself. Three sites used to spell it; three copies of a dead
server's name is the same defect as three copies of a live one's.

Three of the literals the drift detector counts are deliberately **not** expressed here. They
look like the roster because they share its *keys*, but their codomain is something else, and
deriving them from this roster would change what they mean rather than deduplicate them:

* ``personal_ai/situation.py`` — the **situation-source** vocabulary. It maps ``ai-server`` to
  ``"webhook"``, not ``"ai"``, and its event-prefix tuple also carries ``"status."``, which is
  not a server at all.
* ``health/alert_manager.py`` — four servers, because **a server cannot health-check itself**.
  ``ai-server`` is absent by design, not by omission.
* ``settings/permissions.py`` — the *values* are settings reads; only its key set is
  roster-shaped.

The same three are also why ``_MIN_ROSTER_SIZE`` exists in the detector: ``situation.py``'s
source map names four servers without being a roster, so "names several servers" is a
*heuristic* for finding candidates, never a verdict. Every candidate is classified by hand
below, and the classification is equality-checked.
"""

from __future__ import annotations

from aegis_schema.models import ServerType

#: ``(server_type, canonical id, short prefix)``. A plain tuple rather than a dataclass so that
#: nothing here looks like a schema type; the positions are named by the derivations below.
ServerRecord = tuple[ServerType, str, str]
Roster = tuple[ServerRecord, ...]

#: The live servers, in ``ServerType`` order.
SERVER_ROSTER: Roster = (
    (ServerType.AI, "ai-server", "ai"),
    (ServerType.PC, "pc-server", "pc"),
    (ServerType.ANDROID, "android-server", "android"),
    (ServerType.BROWSER, "browser-server", "browser"),
    (ServerType.ROOM, "room-server", "room"),
)

#: Servers that no longer exist but that live entries still answer for. Kept separate so that
#: "is this server live?" is ``in SERVER_ROSTER``, not a second hand-maintained list — and so
#: that the debt is one record here rather than one string at each of the sites that owe it.
RETIRED_SERVER_ROSTER: Roster = (
    (ServerType.DEV, "dev-server", "dev"),
)


def _ids(roster: Roster) -> tuple[str, ...]:
    """Canonical server ids, e.g. ``"pc-server"`` — the first segment of a capability id."""
    return tuple(record[1] for record in roster)


def _short_prefixes(roster: Roster) -> tuple[str, ...]:
    """Short prefixes, e.g. ``"pc"`` — the alias form ``CapabilityCatalog`` derives."""
    return tuple(record[2] for record in roster)


def _server_type_by_id(roster: Roster) -> dict[str, ServerType]:
    """``server_id -> ServerType``: the direction the tool broker and the dashboard need."""
    return {record[1]: record[0] for record in roster}


def _prefix_by_id(roster: Roster) -> dict[str, str]:
    """``server_id -> short prefix``: the direction the capability-id alias map needs."""
    return {record[1]: record[2] for record in roster}


def _prefixes_by_type(roster: Roster) -> dict[ServerType, tuple[str, ...]]:
    """``ServerType -> (short prefix, canonical id)``: the direction the id validator needs."""
    return {record[0]: (record[2], record[1]) for record in roster}


def _server_type_by_dotted_id(roster: Roster) -> dict[str, ServerType]:
    """``"<server_id>." -> ServerType``: the direction a capability-id *prefix* match needs."""
    return {f"{record[1]}.": record[0] for record in roster}


SERVER_IDS: tuple[str, ...] = _ids(SERVER_ROSTER)
SHORT_PREFIXES: tuple[str, ...] = _short_prefixes(SERVER_ROSTER)
SERVER_TYPE_BY_ID: dict[str, ServerType] = _server_type_by_id(SERVER_ROSTER)
PREFIX_BY_ID: dict[str, str] = _prefix_by_id(SERVER_ROSTER)
PREFIXES_BY_TYPE: dict[ServerType, tuple[str, ...]] = _prefixes_by_type(SERVER_ROSTER)
SERVER_TYPE_BY_DOTTED_ID: dict[str, ServerType] = _server_type_by_dotted_id(SERVER_ROSTER)

RETIRED_SERVER_IDS: tuple[str, ...] = _ids(RETIRED_SERVER_ROSTER)
RETIRED_PREFIX_BY_ID: dict[str, str] = _prefix_by_id(RETIRED_SERVER_ROSTER)
RETIRED_SERVER_TYPE_BY_ID: dict[str, ServerType] = _server_type_by_id(RETIRED_SERVER_ROSTER)

#: The retired entries folded into the live ones, for the sites that must answer for both.
#: Spelled as ``**`` spreads so that the retired name appears exactly once in the source tree.
PREFIX_BY_ID_WITH_RETIRED: dict[str, str] = {**PREFIX_BY_ID, **RETIRED_PREFIX_BY_ID}
SERVER_TYPE_BY_ID_WITH_RETIRED: dict[str, ServerType] = {
    **SERVER_TYPE_BY_ID,
    **RETIRED_SERVER_TYPE_BY_ID,
}
PREFIXES_BY_TYPE_WITH_RETIRED: dict[ServerType, tuple[str, ...]] = {
    **PREFIXES_BY_TYPE,
    **_prefixes_by_type(RETIRED_SERVER_ROSTER),
}
