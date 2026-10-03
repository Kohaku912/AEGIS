"""Two registered view functions can never run — the legacy copies are shadowed.

Why this file exists
--------------------
The dashboard app registers **192 rules**; two ``(method, path)`` pairs are registered
**twice**, and Werkzeug matches the first rule for a path, so the second handler is
unreachable. Measured 2026-10-03 on the production app (``AEGIS_UI_VERSION=v2``):

===============  ===========================  ==========================================
pair             winner (reachable)           shadowed (never runs)
===============  ===========================  ==========================================
``GET /api/servers``          ``dashboard_server_status.api_servers``   ``api_servers`` — ``dashboard_legacy.py:1159``
``POST /api/memory/reload``   ``dashboard_memory.memory_reload``        ``api_memory_reload`` — ``dashboard_legacy.py:1372``
===============  ===========================  ==========================================

Both losers are **legacy closure handlers** left behind when the route was migrated to a
blueprint; the blueprint is registered first, so the legacy copy is dead. Measured by
*driving the adapter*, not by reading the file: of **186 endpoints**, **exactly these two**
are unreachable when each rule is matched against its own path.

This also settles a stale number. The §3.2 route row recorded "**98** unreferenced
(method, path) pairs". Re-measured with the recorded rule (client source contains the
literal path or the static prefix up to the first ``<``), the **distinct** count is
**96** — and ``96 + 2 = 98`` because the two shadowed pairs are themselves unreferenced
and were counted **twice**, once per registration. The honest denominator is the
**distinct** count; a multiplicity count double-counts a shadowed route.

Impact is **dead code, not a broken endpoint**: the winner serves the request correctly.
Fixing it (delete the two legacy handlers) or keeping them is an **owner decision** —
``dashboard_legacy.py`` is the legacy surface and other copies there may be deliberate —
so this pins the fact instead.

**This file will fail the day either legacy handler is removed** (or a new shadow appears).
That is the point: the pin and the record must move together, deliberately.
"""

from __future__ import annotations

import re
from typing import Any

from test_documented_routes_are_registered import _app

#: Recorded 2026-10-03 — shadowed endpoint → (method, path, the endpoint that wins).
#: **Equality**: a third shadow fails, and so does removing one (the record would be stale).
_RECORDED_SHADOWED: dict[str, tuple[str, str, str]] = {
    "api_servers": ("GET", "/api/servers", "dashboard_server_status.api_servers"),
    "api_memory_reload": ("POST", "/api/memory/reload", "dashboard_memory.memory_reload"),
}

#: The pairs that are registered twice. Kept separately so the duplicate test can fail
#: with its own message when a *new* collision appears.
_RECORDED_DUPLICATE_PAIRS = frozenset(
    {(m, p) for m, p, _w in _RECORDED_SHADOWED.values()}
)

#: Both losers live in the legacy surface. A shadowed handler elsewhere is a different
#: story and needs its own reading.
_LEGACY_MODULE = "dashboard_legacy.py"

#: Floor: the app must register at least this many rules, or the build is not the app.
_MIN_RULES = 150

#: Dummy values for Flask converters, so a rule's own template can be matched back.
_DUMMY = {
    "int": "1",
    "float": "1.0",
    "path": "x",
    "uuid": "00000000-0000-0000-0000-000000000000",
    "any": "x",
    "string": "x",
}


def _concretise(template: str) -> str:
    """Replace ``<conv:name>`` / ``<name>`` with a dummy that satisfies the converter."""

    def replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        converter = inner.split(":", 1)[0] if ":" in inner else "string"
        return _DUMMY.get(converter, "x")

    return re.sub(r"<([^>]+)>", replace, template)


def _methods(rule: Any) -> list[str]:
    return sorted(rule.methods - {"HEAD", "OPTIONS"}) or ["GET"]


# ── Non-vacuity: the app builds and the subjects exist ───────────────────────


def test_the_app_registers_the_surface_and_the_subjects_exist(tmp_path: Any, monkeypatch: Any) -> None:
    app = _app(tmp_path, monkeypatch)
    rules = list(app.url_map.iter_rules())
    assert len(rules) >= _MIN_RULES, (
        f"the app registered only {len(rules)} rules (floor {_MIN_RULES}); the build is "
        "not the production surface and the scans would pass vacuously"
    )
    registered = {r.rule for r in rules}
    for _ep, (_m, path, _w) in _RECORDED_SHADOWED.items():
        assert path in registered, (
            f"{path} is no longer registered — if the route was deleted, the shadow is "
            "gone; re-measure and update DELEGATION.md §4 and this pin together."
        )
    assert "api_servers" in app.view_functions, "the recorded shadowed endpoint is gone"


# ── The invariant: every endpoint is reachable by matching its own rule ──────


def _reachability(app: Any) -> tuple[set[str], list[tuple[str, str]]]:
    """(endpoints reachable by matching their own rule, duplicated pairs)."""
    adapter = app.url_map.bind("localhost")
    pairs: list[tuple[str, str]] = []
    reachable: set[str] = set()
    for rule in app.url_map.iter_rules():
        for method in _methods(rule):
            pairs.append((method, rule.rule))
        try:
            endpoint, _args = adapter.match(_concretise(rule.rule), method=_methods(rule)[0])
            reachable.add(endpoint)
        except Exception:  # noqa: BLE001 — an unmatchable rule is simply not reachable
            pass
    return reachable, sorted({p for p in pairs if pairs.count(p) > 1})


def test_every_registered_endpoint_is_reachable_except_the_recorded_shadows(
    tmp_path: Any, monkeypatch: Any
) -> None:
    app = _app(tmp_path, monkeypatch)
    reachable, _dupes = _reachability(app)
    unreachable = sorted(set(app.view_functions) - reachable)
    assert unreachable == sorted(_RECORDED_SHADOWED), (
        f"the set of endpoints no rule can reach changed: {unreachable} != "
        f"{sorted(_RECORDED_SHADOWED)}. A *new* entry is a new shadow (two rules for one "
        "path, or a converter stealing another's route); an *empty* set means the legacy "
        "copies were deleted — either way this pin and DELEGATION.md §4 must move together."
    )


def test_no_pair_is_registered_twice_except_the_recorded_ones(
    tmp_path: Any, monkeypatch: Any
) -> None:
    app = _app(tmp_path, monkeypatch)
    _reachable, dupes = _reachability(app)
    assert set(dupes) == set(_RECORDED_DUPLICATE_PAIRS), (
        f"the duplicated (method, path) pairs changed: {dupes} != "
        f"{sorted(_RECORDED_DUPLICATE_PAIRS)}"
    )


def test_each_shadowed_handler_is_the_legacy_copy(tmp_path: Any, monkeypatch: Any) -> None:
    """The mechanism: a legacy closure shadowed by the blueprint that replaced it.

    **Both sides**: the loser is legacy *and* the winner is not — so reversing the
    registration order (which would make the legacy copy win) fails here too.
    """
    app = _app(tmp_path, monkeypatch)
    for endpoint, (_m, _p, winner) in sorted(_RECORDED_SHADOWED.items()):
        loser_file = app.view_functions[endpoint].__code__.co_filename.replace("\\", "/")
        assert _LEGACY_MODULE in loser_file, (
            f"{endpoint} is no longer defined in {_LEGACY_MODULE} ({loser_file}); "
            "re-measure and update DELEGATION.md §4"
        )
        winner_file = app.view_functions[winner].__code__.co_filename.replace("\\", "/")
        assert _LEGACY_MODULE not in winner_file, (
            f"the winner {winner} now lives in {_LEGACY_MODULE} — the registration order "
            "reversed, so the legacy copy wins; re-measure and update DELEGATION.md §4 and "
            "this pin together."
        )


def test_the_winner_is_the_modular_endpoint_for_each_shadowed_path(
    tmp_path: Any, monkeypatch: Any
) -> None:
    """The other half of the mechanism: the blueprint wins, so the legacy copy loses."""
    app = _app(tmp_path, monkeypatch)
    adapter = app.url_map.bind("localhost")
    for endpoint, (method, path, winner) in sorted(_RECORDED_SHADOWED.items()):
        got, _args = adapter.match(path, method=method)
        assert got == winner, (
            f"{method} {path} now resolves to {got!r}, not {winner!r} — the registration "
            "order changed; re-measure and update DELEGATION.md §4 and this pin together."
        )
        assert got != endpoint, f"{method} {path} is no longer shadowing {endpoint}"


def test_the_recorded_count_double_counts_the_shadowed_pairs(tmp_path: Any, monkeypatch: Any) -> None:
    """The stale-number arithmetic: multiplicity = distinct + duplicates."""
    app = _app(tmp_path, monkeypatch)
    adapter = app.url_map.bind("localhost")
    pairs: list[tuple[str, str]] = []
    for rule in app.url_map.iter_rules():
        for method in _methods(rule):
            pairs.append((method, rule.rule))
    distinct = set(pairs)
    assert len(pairs) - len(distinct) == len(_RECORDED_DUPLICATE_PAIRS), (
        f"{len(pairs)} pairs, {len(distinct)} distinct — the difference must equal the "
        f"{len(_RECORDED_DUPLICATE_PAIRS)} recorded shadowed pair(s). The §3.2 route row's "
        "denominator must be the *distinct* count."
    )
    assert adapter is not None  # the adapter is the subject, not a stub
