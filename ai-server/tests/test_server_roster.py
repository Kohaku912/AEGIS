"""The server roster has no single definition (B-15).

"dev-server remnants" read like a handful of forgotten strings. Measured, they are one symptom
of a structural fact: the roster of AEGIS servers was re-declared in **15 literals across 11
modules**, in five different value shapes (``ServerType``, short prefix, enabled flag, id prefix,
host:port). The dev-server was deleted in Phase 9 and five of those literals still named it.

**A-3 gave the fact one home** — ``aegis_schema/roster.py`` — and this file moved with it. What
the migration changed, measured rather than assumed:

* 15 literals → **10**, across 11 modules → **7**. Five sites now *import* the roster:
  ``capability_catalog.py`` (twice), ``prompt_regression.py``, ``dashboard_legacy.py``,
  ``models.py``, ``tool_broker.py``.
* Recorded drift 5 sites → **2**: ``settings/permissions.py`` and ``web/ui_overview.py``. The
  three retired-server copies that were drift (both in ``capability_catalog.py``, one in
  ``models.py``) are gone, because the retired entry now lives once, in the roster.
* The canonical roster became a *site*: ``aegis_schema/roster.py`` is scanned like any other,
  and the residue is recorded below so it cannot grow back silently.

This module is the detector, in the same shape as the other drift guards here: discover rather
than list, then assert the observed set *equals* the recorded set.

* Roster literals are discovered with AST, so prose and comments cannot satisfy it.
* The **live** servers are discovered from the capability catalog, so a server added tomorrow is
  accepted without editing anything in this file.
* The **retired** servers cannot be discovered — a server that no longer exists leaves no
  artefact to find it by — so that set is the one hand-written thing here, and it can only grow
  by a deliberate decision to retire a server. It is asserted equal to the roster's own retired
  record, so the two cannot drift.

Why a detector and not a cleanup. Deleting a dead entry is not always a no-op:

* ``Capability.id_server_type_consistency`` (``aegis_schema/models.py``) does
  ``prefix_map.get(self.server_type)`` and then ``if expected_prefixes and ...`` — a missing key
  returns ``None`` and the id-prefix check is **skipped**. The map covers six of the seven
  ``ServerType`` members; the one it omits is ``UNSPECIFIED``, so a capability declaring that —
  with any id that satisfies the pattern — is never checked against its own server type. (An
  earlier version of this paragraph named ``DEV``; that was wrong, and wrong in the way this
  file exists to catch. ``DEV`` *is* mapped, and a ``DEV`` capability carrying a ``room-server.*``
  id is correctly rejected. Only ``UNSPECIFIED`` bypasses.)
* ``aegis_ai/settings/permissions.py`` does ``server_enabled_map.get(server_prefix, True)`` — a
  missing key means **enabled**.

Both are **asserted** at the bottom of this file, not merely described here. Prose in a detector
is still prose — the paragraph above carried a wrong member name until the behavioural tests were
written, which is the whole argument for writing them.

So the entries are unreachable today and *fail-open tomorrow*. Removing them is an owner decision
about what should happen if such a server ever reappears, not a mechanical delete. This file
records the drift so it cannot grow silently in the meantime.

Line numbers are deliberately **not** cited in this docstring. They rot, and a rotted line number
in a detector is indistinguishable from a live one — which is the same defect as the stale member
name above. The code below addresses sites by symbol, or discovers them.
"""

from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

import pytest

from aegis_ai.capability_catalog import _PREFIX_MAP, CapabilityCatalog
from aegis_schema.models import Capability, RiskLevel, ServerType

_SRC = Path(__file__).resolve().parents[1] / "src"

#: Servers that were deleted from the ecosystem. The only hand-written list here: see the module
#: docstring for why this one cannot be discovered. Asserted equal to the roster's own retired
#: record below, so a retirement recorded in one place and not the other fails loudly.
_RETIRED_SERVERS: frozenset[str] = frozenset({"dev", "dev-server"})

#: A roster literal must name at least this many distinct servers to count. Two or three is
#: usually an incidental pair (e.g. a `{"android", "android-server"}` check for one server's two
#: spellings), not a roster. This is a *heuristic for finding candidates* — never a verdict, and
#: never a reason to stop looking: see `_RECORDED_DEV_SERVER_SPELLINGS` for the sites it cannot
#: see.
_MIN_ROSTER_SIZE = 4

#: The drift that exists today, keyed by ``"<path>::<retired ids, sorted, + joined>"``.
#:
#: Keyed by path *and* the retired ids present rather than by line number, so the entry survives
#: unrelated edits above it but breaks the moment the drift itself changes — which is the point.
#: This is an inventory of debt, not an approval.
#:
#: A-3 removed three entries from this map. They are *recorded as removed*, not silently dropped:
#: the retired entry used to be spelled at ``capability_catalog.py`` (twice) and ``models.py``,
#: and now lives once in ``aegis_schema/roster.py``. Removing a site from here without that
#: move would have been the bug this map exists to prevent.
_RECORDED_DRIFT: dict[str, str] = {
    "aegis_ai/settings/permissions.py::dev+dev-server": (
        "`server_enabled_map` still answers for dev/dev-server. Deleting these keys flips the "
        "fallback from `settings.servers.dev_server_enabled` to the literal `True` in "
        "`.get(..., True)`, i.e. fail-open. Owner decision."
    ),
    "aegis_ai/web/ui_overview.py::dev-server": (
        "The prefix set used to decide which prefixes are server-like. Harmless while no dev id "
        "exists, and it is the reason a dev id would still be rendered as a server if one ever "
        "appeared."
    ),
}

#: Modules that still declare a roster inline, with the number of literals each contributes.
#:
#: Equality-checked in both directions. `len(ROSTERS) >= N` would *not* have caught a new inline
#: roster — that raises the count, and a floor cannot see growth. This can: a module that gains a
#: roster literal fails here, and so does one that is cleaned up, so the inventory cannot go
#: stale and start describing a state that no longer exists.
#:
#: The last six are the same three literals the roster module's docstring declines to express,
#: plus three that were never candidates for it. "Shares the keys" is not "is the roster".
_RECORDED_INLINE_ROSTERS: dict[str, tuple[int, str]] = {
    "aegis_ai/grpc_server.py": (1, "the gRPC service-address table, not a server roster"),
    "aegis_ai/health/alert_manager.py": (
        2,
        "four servers, not five — a server cannot health-check itself",
    ),
    "aegis_ai/personal_ai/situation.py": (
        3,
        "the situation-*source* vocabulary: `ai-server` maps to 'webhook', and its event-prefix "
        "tuple also carries 'status.', which is not a server",
    ),
    "aegis_ai/settings/permissions.py": (1, "values are settings reads; only the key set is roster-shaped"),
    "aegis_ai/status/status_manager.py": (1, "the status aggregation table"),
    "aegis_ai/web/ui_overview.py": (1, "the prefix set used to decide what is server-like"),
    "aegis_schema/roster.py": (1, "the canonical roster itself — the one copy that is the fact"),
}

#: Modules under ``src/`` that spell the retired server's id as a string constant.
#:
#: A literal naming *one* server is below ``_MIN_ROSTER_SIZE``, so ``_roster_literals()`` is
#: blind to it — and A-3 is exactly the change that put single-name literals in new places. This
#: pins the scan's own blind spot directly instead of trusting the floor to cover it. The two
#: non-roster entries are the two recorded drift sites above, which is not a coincidence: a site
#: that spells a dead server's name is a site that owes the debt.
_RECORDED_DEV_SERVER_SPELLINGS: frozenset[str] = frozenset(
    {
        "aegis_ai/settings/permissions.py",
        "aegis_ai/web/ui_overview.py",
        "aegis_schema/roster.py",
    }
)


def _live_servers() -> set[str]:
    """Server ids that actually have capabilities, discovered from the catalog."""
    catalog = CapabilityCatalog(capabilities_dir="capabilities", apps_dir="apps")
    return {manifest.server_id for manifest in catalog.list_all()}


def _short_of(live: set[str]) -> set[str]:
    """The short spellings of live servers, taken from the catalog's own alias map."""
    return {_PREFIX_MAP[s] for s in live if s in _PREFIX_MAP}


def _candidate_strings() -> set[str]:
    """Every string that could be a server name in a roster literal."""
    live = _live_servers()
    return live | _short_of(live) | set(_RETIRED_SERVERS)


def _string_constants(node: ast.AST) -> list[str]:
    return [
        sub.value.rstrip(".")
        for sub in ast.walk(node)
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str)
    ]


def _parseable_sources():
    """Every ``*.py`` under ``src/`` that parses, as ``(relative path, tree)``."""
    for path in sorted(_SRC.rglob("*.py")):
        if "generated" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover - a syntax error fails elsewhere
            continue
        yield path.relative_to(_SRC).as_posix(), tree


def _roster_literals() -> list[tuple[str, int, list[str]]]:
    """Every literal that names ``_MIN_ROSTER_SIZE`` or more distinct servers.

    Returns ``(relative path, line, distinct server ids)``.
    """
    candidates = _candidate_strings()
    found: list[tuple[str, int, list[str]]] = []
    for rel, tree in _parseable_sources():
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Dict, ast.Set, ast.List, ast.Tuple)):
                continue
            named = sorted({s for s in _string_constants(node) if s in candidates})
            if len(named) >= _MIN_ROSTER_SIZE:
                found.append((rel, node.lineno, named))
    return found


def _dev_server_spellings() -> set[str]:
    """Modules that spell the retired server's id as a string constant, however few names."""
    return {
        rel
        for rel, tree in _parseable_sources()
        if any(
            isinstance(node, ast.Constant) and node.value == "dev-server"
            for node in ast.walk(tree)
        )
    }


def _drift_key(path: str, named: list[str]) -> str:
    retired = sorted(set(named) & set(_RETIRED_SERVERS))
    return f"{path}::{'+'.join(retired)}"


ROSTERS = _roster_literals()
DRIFT = [(p, ln, named) for p, ln, named in ROSTERS if set(named) & set(_RETIRED_SERVERS)]


def _ids(roster: tuple[str, int, list[str]]) -> str:
    return f"{roster[0]}:{roster[1]}"


# ── Guards on the detector itself ─────────────────────────────────────────────


def test_the_scan_actually_covers_the_roster() -> None:
    """A truncated scan would pass every other test in this file vacuously."""
    live = _live_servers()
    assert len(live) >= 5, f"only {len(live)} live servers discovered: {sorted(live)}"
    assert any(p == "aegis_schema/roster.py" for p, _, _ in ROSTERS), (
        "the scan does not see the canonical roster itself, so it is not reading src/ — "
        f"discovered {sorted({p for p, _, _ in ROSTERS})}"
    )


def test_the_live_server_set_matches_the_capability_tree() -> None:
    """Two independent discoveries of the same fact: catalog vs directory names."""
    from_tree = {
        p.name for p in (Path(__file__).resolve().parents[1] / "capabilities" / "builtin").iterdir()
        if p.is_dir()
    }
    assert _live_servers() == from_tree


# ── The canonical roster (B-15's actual deliverable) ──────────────────────────


def test_the_canonical_roster_is_the_capability_tree() -> None:
    """The roster is where the server set is declared; the catalog must agree with it.

    Two directions of one fact, discovered independently: the roster is source, the capability
    tree is what is on disk. Nothing compared them before A-3, so a server present in one and
    absent from the other was invisible — which is how five copies of this map drifted apart.

    Note what is **not** asserted here. An earlier draft of this test compared ``PREFIX_BY_ID``
    against ``{s: _PREFIX_MAP[s] for s in SERVER_IDS}``, which looks like a check and is not one:
    ``_PREFIX_MAP`` is *derived from* ``PREFIX_BY_ID``, so a wrong short prefix moves both sides
    together and the assertion can never fail. It was caught by mutation (changing ``room`` to
    ``rm`` left it green). The short prefixes are pinned instead against the id allowlist in
    ``test_the_id_pattern_admits_exactly_the_roster_prefixes``, which is a separate declaration.
    """
    from aegis_schema.roster import SERVER_IDS

    live = _live_servers()
    assert set(SERVER_IDS) == live, (
        "the canonical roster and the capability tree disagree.\n"
        f"  only in roster: {sorted(set(SERVER_IDS) - live)}\n"
        f"  only in tree  : {sorted(live - set(SERVER_IDS))}\n"
        "Add the server to aegis_schema/roster.py — not to a new local literal."
    )


def test_the_id_pattern_admits_exactly_the_roster_prefixes() -> None:
    """Two independent declarations of one fact: the pydantic id allowlist and the roster.

    ``Capability.id``'s pattern is an alternation that enumerates every accepted prefix — it is
    the lock that excludes third-party servers (B-14). The roster enumerates every server. The
    two must agree, or one of them is a stale copy.

    This is also what makes the roster's *short* prefixes load-bearing: they cannot be checked
    against anything the roster itself derives, but they can be checked against this pattern.
    """
    from aegis_schema.roster import PREFIXES_BY_TYPE_WITH_RETIRED

    pattern = Capability.model_fields["id"].metadata[0].pattern
    assert isinstance(pattern, str) and pattern.startswith("^("), (
        f"the id pattern is no longer a leading alternation, so it cannot be read: {pattern!r}"
    )
    admitted = set(pattern[2 : pattern.index(")")].split("|"))
    from_roster = {
        prefix for prefixes in PREFIXES_BY_TYPE_WITH_RETIRED.values() for prefix in prefixes
    }
    assert admitted == from_roster, (
        "the id allowlist and the roster disagree.\n"
        f"  admitted by the pattern, absent from the roster: {sorted(admitted - from_roster)}\n"
        f"  in the roster, rejected by the pattern       : {sorted(from_roster - admitted)}\n"
        "Both are copies of one fact — fix whichever is stale, in aegis_schema/roster.py."
    )


# ── A check that was written here and withdrawn ───────────────────────────────
#
# The draft was: "every manifest's ``capability_id`` prefix matches its ``server_id``". It was
# mutation-proved by flipping ``server_id`` in a real manifest — and it did **not** fail, for two
# independent reasons:
#
# * ``folder_registry._derive_ids`` takes ``server_id`` from the **path**, then builds
#   ``capability_id = f"{server_id}.{app_id}.{action}"`` from the same dict. The first segment of
#   an id *is* its server_id by construction, so the loop can never observe a disagreement.
# * ``folder_registry._validate`` compares the JSON's ``server_id`` against the path's, and a
#   disagreement makes the manifest **rejected** — it never reaches ``list_all()`` at all.
#
# The real invariant is therefore "nothing was rejected", and it is already pinned by
# ``tests/test_manifest_schemas.py::test_all_builtin_manifests_load_without_registry_errors``.
# A manifest that disagrees with its own path is silently *dropped*, which is worse than being
# wrong: the capability vanishes from the agent's reach with no error at the point of use.
#
# Withdrawn rather than kept as a redundant second copy — a test that cannot fail is a liability,
# and this file exists precisely because a description of a check is not a check. If the
# registry's path/JSON validation is ever relaxed, the assertion to add goes back here, and it is
# the *rejection* it should watch, not the surviving manifests.


def test_the_hand_written_retired_set_matches_the_roster() -> None:
    """The one hand-written list here, tied to the roster so the two cannot drift.

    ``_RETIRED_SERVERS`` cannot be discovered — a deleted server leaves no artefact. The roster
    *can* say what has been retired, so the hand list is checked against it rather than trusted.
    """
    from aegis_schema.roster import RETIRED_SERVER_ROSTER

    from_roster = {record[1] for record in RETIRED_SERVER_ROSTER} | {
        record[2] for record in RETIRED_SERVER_ROSTER
    }
    assert from_roster == set(_RETIRED_SERVERS), (
        f"the hand-written retired set is {sorted(_RETIRED_SERVERS)} but the roster retires "
        f"{sorted(from_roster)}. A retirement recorded in one place and not the other is how a "
        "dead server's name survives in a live code path."
    )


def test_the_retired_server_is_not_in_the_live_roster() -> None:
    """``SERVER_ROSTER`` is what exists. The retired record is separate, and that separation is
    what makes "is this server live?" answerable without a second hand-maintained list."""
    from aegis_schema.roster import RETIRED_SERVER_IDS, SERVER_ROSTER

    live_types = {record[0] for record in SERVER_ROSTER}
    assert ServerType.DEV not in live_types
    assert set(RETIRED_SERVER_IDS).isdisjoint(record[1] for record in SERVER_ROSTER)


def test_the_retired_id_is_spelled_in_exactly_the_recorded_modules() -> None:
    """Pin the scan's own blind spot: a single-name literal is below the roster floor.

    A-3 is the change that put ``dev-server`` into ``**``-spreads, where it is invisible to
    ``_roster_literals()``. Without this test, moving the entry back out of the roster into a new
    module would pass everything else here.
    """
    observed = _dev_server_spellings()
    assert observed == set(_RECORDED_DEV_SERVER_SPELLINGS), (
        "the modules that spell 'dev-server' changed.\n"
        f"  newly spelling it: {sorted(observed - _RECORDED_DEV_SERVER_SPELLINGS)}\n"
        f"  no longer spelling: {sorted(_RECORDED_DEV_SERVER_SPELLINGS - observed)}\n"
        "Spell the retired server once, in aegis_schema/roster.py, and import it."
    )


# ── The invariant ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("roster", ROSTERS, ids=_ids)
def test_no_roster_names_a_server_that_does_not_exist(
    roster: tuple[str, int, list[str]],
) -> None:
    """Every server named in a roster is live — or recorded drift with a reason."""
    path, line, named = roster
    live = _live_servers()
    acceptable = live | _short_of(live)
    unknown = sorted(set(named) - acceptable)
    if not unknown:
        return
    key = _drift_key(path, named)
    assert key in _RECORDED_DRIFT, (
        f"{path}:{line} names {unknown}, which is not a live server "
        f"(live: {sorted(live)}). If this is a newly retired server, add it to "
        f"_RETIRED_SERVERS and record the site in _RECORDED_DRIFT with a reason."
    )


def test_the_recorded_drift_is_exactly_the_observed_drift() -> None:
    """Equality in both directions, so the count cannot drift silently.

    Adding a roster that names a dead server fails here even if the parametrized test above were
    somehow skipped; *removing* one also fails, so the inventory cannot go stale and start
    describing a state that no longer exists.
    """
    observed = Counter(_drift_key(p, named) for p, _, named in DRIFT)
    recorded = Counter(_RECORDED_DRIFT.keys())
    assert observed == recorded, (
        "the recorded roster drift no longer matches the observed drift.\n"
        f"  newly drifted : {sorted(observed - recorded)}\n"
        f"  now clean     : {sorted(recorded - observed)}\n"
        "Update _RECORDED_DRIFT — and if a site became clean, say so in the commit message "
        "rather than silently dropping the entry."
    )


def test_the_inline_roster_residue_is_exactly_the_recorded_one() -> None:
    """Equality, so a module cannot *gain* a roster literal unnoticed.

    This is the assertion a ``len(ROSTERS) >= N`` floor cannot make: growth passes a floor.
    """
    observed = Counter(path for path, _, _ in ROSTERS)
    recorded = Counter({path: count for path, (count, _) in _RECORDED_INLINE_ROSTERS.items()})
    assert observed == recorded, (
        "the modules that still declare a roster inline changed.\n"
        f"  newly inline : {sorted(observed - recorded)}\n"
        f"  now clean    : {sorted(recorded - observed)}\n"
        "A new site should import aegis_schema.roster instead. A site that became clean must be "
        "removed from _RECORDED_INLINE_ROSTERS in the same commit."
    )


# ── Why the drift is recorded rather than deleted ─────────────────────────────


def test_a_dev_capability_is_still_constructible_so_the_enum_member_is_live() -> None:
    """The DEV path is reachable, which is what makes the dead entries load-bearing.

    If ``ServerType.DEV`` could not appear on a capability at all, the entries above would be
    unambiguously deletable. It can.
    """
    cap = Capability(
        id="dev.thing",
        name="Thing",
        description="A dev capability, used only to pin reachability.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.READ_ONLY,
    )
    assert cap.server_type is ServerType.DEV


def test_the_id_prefix_allowlist_is_a_closed_set() -> None:
    """B-14: the id prefix is an allowlist, and it is what locks out third parties.

    This pins the lock so that widening it is a visible decision rather than an accident.
    The SDK used to promise the opposite — ``define_capability(server_prefix="weather", ...)``
    was its own documented example, and it could not construct a ``Capability``. Since
    2026-09-29 (register A-2 ②) the SDK refuses such a prefix itself, by name, before pydantic
    sees the id, so the lock and the promise now agree; the SDK side is pinned by
    ``packages/aegis-sdk-python/tests/test_capability_id_contract.py``. Widening this pattern
    still turns both red.
    """
    with pytest.raises(Exception) as excinfo:
        Capability(
            id="weather.get_forecast",
            name="Get Weather Forecast",
            description="Retrieve a weather forecast for a location.",
            server_type=ServerType.DEV,
            risk_level=RiskLevel.READ_ONLY,
        )
    assert "pattern" in str(excinfo.value).lower() or "string_pattern" in str(excinfo.value)


# ── The two fail-opens, asserted rather than described ────────────────────────
#
# The module docstring has always *described* these. Describing them is not the same as pinning
# them: nothing failed if either fallback flipped, and the description itself named the wrong
# enum member for years. These tests exist so the prose is backed by something that runs.


def _build(cap_id: str, server_type: ServerType) -> Capability:
    return Capability(
        id=cap_id,
        name="Thing",
        description="Used only to pin the id/server-type contract.",
        server_type=server_type,
        risk_level=RiskLevel.READ_ONLY,
    )


def _validator_body() -> ast.FunctionDef:
    """``Capability.id_server_type_consistency``, found by name."""
    source = (_SRC / "aegis_schema" / "models.py").read_text(encoding="utf-8")
    validators = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == "id_server_type_consistency"
    ]
    assert len(validators) == 1, (
        f"expected exactly one id_server_type_consistency, found {len(validators)}"
    )
    return validators[0]


def _id_consistency_map() -> dict[str, tuple[str, ...]]:
    """The ``server_type -> id prefixes`` map the validator actually consults.

    This used to be read out of the validator's AST, because the map was a local inside
    ``Capability.id_server_type_consistency`` and there was nothing to import. B-15 moved the
    fact into ``aegis_schema.roster``, so the discovery moved with it — and moving it is the
    point, not a convenience: a helper that kept reading the old local would have gone on passing
    against a copy nothing consults, which is the failure mode this whole file is about. The
    delegation itself is asserted by ``test_the_validator_names_no_server_of_its_own``.
    """
    from aegis_schema.roster import PREFIXES_BY_TYPE_WITH_RETIRED

    return {
        server_type.name: tuple(prefixes)
        for server_type, prefixes in PREFIXES_BY_TYPE_WITH_RETIRED.items()
    }


_ID_MAP = _id_consistency_map()

#: ``ServerType`` members the map omits. A member listed here has its id-prefix check
#: **skipped**, so this tuple *is* the fail-open surface — it may only change by a deliberate
#: decision, and the reason belongs in the commit message.
_RECORDED_UNMAPPED_SERVER_TYPES: tuple[str, ...] = ("UNSPECIFIED",)


def test_the_discovery_actually_sees_the_map() -> None:
    """Guard the guard: an empty or truncated map would make the tests below vacuous."""
    assert len(_ID_MAP) >= 6, f"only {len(_ID_MAP)} mapped server types: {sorted(_ID_MAP)}"
    assert len(list(ServerType)) >= 7, "ServerType shrank; revisit this file's assumptions"
    assert any("server" in p for prefixes in _ID_MAP.values() for p in prefixes), (
        "no long-form prefix discovered — the map may not be the one being read"
    )


def test_the_validator_names_no_server_of_its_own() -> None:
    """The map must be *consulted*, not re-spelled.

    The guard that used to stand here was "the validator holds exactly one dict literal". That
    was a guard on the AST read, and it vanished with the AST read — replaced by the invariant it
    was protecting. Any string constant in the validator's body that names a server, live or
    retired, is a second copy of the roster; importing one is the fix.
    """
    candidates = _candidate_strings()
    named = sorted({s for s in _string_constants(_validator_body()) if s in candidates})
    assert named == [], (
        f"Capability.id_server_type_consistency names {named} inline. The roster is the one place "
        "a server may be spelled (B-15) — import it from aegis_schema.roster instead."
    )


def test_only_the_recorded_server_types_skip_the_id_prefix_check() -> None:
    """Equality, so the bypass set cannot grow (or shrink) silently."""
    unmapped = tuple(sorted(m.name for m in ServerType if m.name not in _ID_MAP))
    assert unmapped == _RECORDED_UNMAPPED_SERVER_TYPES, (
        "the set of ServerType members whose id-prefix check is skipped changed.\n"
        f"  observed: {unmapped}\n"
        f"  recorded: {_RECORDED_UNMAPPED_SERVER_TYPES}\n"
        "A member appearing here means declaring it now *disables* validation. If that is "
        "intended, record it above with the reason; if not, give it a prefix entry."
    )


def _mismatched_id_for(member_name: str) -> str:
    """An id whose prefix belongs to a *different* mapped server type."""
    other = next(
        prefixes for name, prefixes in sorted(_ID_MAP.items()) if name != member_name
    )
    return f"{other[0]}.thing.do"


@pytest.mark.parametrize("member", list(ServerType), ids=lambda m: m.name)
def test_the_id_prefix_check_fires_for_mapped_types_and_not_for_unmapped(
    member: ServerType,
) -> None:
    """Behavioural proof, per member, of which side the missing key falls on.

    Mapped members must reject an id belonging to another server. The unmapped member is the
    recorded fail-open: ``prefix_map.get()`` returns ``None``, the ``if`` never runs, and the
    capability is accepted — so *declaring* ``UNSPECIFIED`` is what turns the check off.
    """
    cap_id = _mismatched_id_for(member.name)

    if member.name in _ID_MAP:
        with pytest.raises(Exception) as excinfo:
            _build(cap_id, member)
        assert "should start with" in str(excinfo.value), (
            f"{member.name} rejected '{cap_id}' for the wrong reason: {excinfo.value}"
        )
    else:
        built = _build(cap_id, member)
        assert built.id == cap_id, (
            f"{member.name} was expected to bypass the id check (recorded fail-open) "
            f"but '{cap_id}' did not survive construction"
        )


def _server_enabled_map_keys() -> set[str]:
    source = (_SRC / "aegis_ai" / "settings" / "permissions.py").read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "server_enabled_map" in names and isinstance(node.value, ast.Dict):
            return {k.value for k in node.value.keys if isinstance(k, ast.Constant)}
    raise AssertionError("server_enabled_map not found in settings/permissions.py")


def _server_enabled_default() -> str:
    """The literal second argument of ``server_enabled_map.get(prefix, default)``.

    ``server_enabled_map`` is the *receiver* of the call, so it lives on ``node.func.value`` —
    not in ``node.args``. Reading ``args[0]`` finds the prefix expression instead and matches
    nothing.
    """
    source = (_SRC / "aegis_ai" / "settings" / "permissions.py").read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "get" or len(node.args) != 2:
            continue
        receiver = node.func.value
        if isinstance(receiver, ast.Name) and receiver.id == "server_enabled_map":
            return ast.unparse(node.args[1])
    raise AssertionError("server_enabled_map.get(prefix, default) not found")


#: Which side the server-enabled gate falls on for an unrecognised prefix.
_RECORDED_GATE_DEFAULT = "True"


def test_the_server_enabled_gate_still_defaults_to_enabled() -> None:
    """The second fail-open: an unknown prefix reads as **enabled**.

    Fail-open is the wrong side for a gate, so this is recorded rather than left implicit. If it
    ever becomes fail-closed, that is an improvement — and it is also what finally makes the
    dev/dev-server keys in that map removable.
    """
    default = _server_enabled_default()
    assert default == _RECORDED_GATE_DEFAULT, (
        f"the server-enabled gate's fallback changed from {_RECORDED_GATE_DEFAULT} to "
        f"'{default}'. A fail-closed default is better — record it here and note that the "
        "retired-server keys in server_enabled_map are now safe to delete."
    )


def test_the_fail_open_default_is_unreachable_for_pattern_valid_ids() -> None:
    """Why this is recorded rather than fixed: today the fallback cannot fire.

    The id pattern admits a closed set of prefixes, and every one of them is a key in
    ``server_enabled_map``. So the ``True`` fallback is only reachable if the pattern is widened
    (B-14's third-party prefixes) or a key is dropped — which is precisely the change this test
    makes visible.
    """
    pattern = Capability.model_fields["id"].metadata[0].pattern
    assert isinstance(pattern, str) and pattern.startswith("^("), (
        f"the id pattern is no longer a leading alternation, so it cannot be read: {pattern!r}"
    )
    accepted = set(pattern[2 : pattern.index(")")].split("|"))
    assert len(accepted) >= 10, f"only {len(accepted)} prefixes parsed out of the pattern"

    missing = sorted(accepted - _server_enabled_map_keys())
    assert missing == [], (
        f"prefixes {missing} satisfy the id pattern but have no entry in server_enabled_map, so "
        "`.get(..., True)` treats their server as ENABLED. The recorded fail-open has become "
        "reachable — fix the default, not this test."
    )
