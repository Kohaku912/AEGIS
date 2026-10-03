"""No registered view function is shadowed — the two legacy copies are gone.

Why this file exists
--------------------
The dashboard app used to register **192 rules**, and two ``(method, path)`` pairs were
registered **twice**. Werkzeug matches the first rule for a path, so the second handler was
unreachable. Measured 2026-10-03 on the production app (``AEGIS_UI_VERSION=v2``):

=================  =================================  ==================================
pair               winner (reachable)                 shadowed (never ran)
=================  =================================  ==================================
``GET /api/servers``          ``dashboard_server_status.api_servers``   ``api_servers`` — ``dashboard_legacy.py``
``POST /api/memory/reload``   ``dashboard_memory.memory_reload``        ``api_memory_reload`` — ``dashboard_legacy.py``
=================  =================================  ==================================

Both losers were **legacy closure handlers** left behind when the route was migrated to a
blueprint; the blueprint registers first, so the legacy copy was **dead code** — not a broken
endpoint, because the winner serves correctly. They were **removed 2026-10-03**
(``DELEGATION.md`` §4 item 28); the only observable change is the rule count.

**This pin asserts the invariant, not the defect** — it is the inverse of the pin that first
recorded the shadowing. Back then the file asserted *exactly these two* endpoints were
unreachable and *exactly these two* pairs were duplicated; now it asserts both sets are
**empty**. A regression — a new duplicate pair, a converter stealing another route, or the
legacy copy being re-added — fails here.

It also settles a stale number. The §3.2 route row recorded "**98** unreferenced (method,
path) pairs". The **distinct** count was **96** — ``96 + 2 = 98`` because the two shadowed
pairs were unreferenced *and* registered twice, i.e. counted once per registration. With the
duplicates gone, multiplicity and distinctness now coincide, which is pinned below.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from test_documented_routes_are_registered import _app

#: Recorded 2026-10-03 — the endpoints that **were** shadowed and have now been removed:
#: endpoint → (method, path, the endpoint that actually serves it).
_REMOVED_SHADOWED: dict[str, tuple[str, str, str]] = {
    "api_servers": ("GET", "/api/servers", "dashboard_server_status.api_servers"),
    "api_memory_reload": ("POST", "/api/memory/reload", "dashboard_memory.memory_reload"),
}

#: The module the removed copies lived in. A shadowed handler elsewhere is a different
#: story and needs its own reading.
_LEGACY_MODULE = "dashboard_legacy.py"

#: Floor: the app must register at least this many rules, or the build is not the app.
_MIN_RULES = 150

#: Floor for the source scan: the legacy module must still define this many functions, or
#: the file moved and the "the closures are gone" check would pass vacuously.
_MIN_LEGACY_FUNCTIONS = 20

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


def _legacy_source() -> str:
    return (
        Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "web" / _LEGACY_MODULE
    ).read_text(encoding="utf-8")


# ── Non-vacuity: the app builds and the subjects exist ───────────────────────


def test_the_app_registers_the_surface_and_the_paths_are_still_served(
    tmp_path: Any, monkeypatch: Any
) -> None:
    app = _app(tmp_path, monkeypatch)
    rules = list(app.url_map.iter_rules())
    assert len(rules) >= _MIN_RULES, (
        f"the app registered only {len(rules)} rules (floor {_MIN_RULES}); the build is "
        "not the production surface and the scans would pass vacuously"
    )
    registered = {r.rule for r in rules}
    for _ep, (_m, path, _w) in _REMOVED_SHADOWED.items():
        assert path in registered, (
            f"{path} is no longer registered at all — the *winner* was removed too, not "
            "just the shadowed copy; re-measure and update DELEGATION.md §4 and this pin "
            "together."
        )
    for endpoint in _REMOVED_SHADOWED:
        assert endpoint not in app.view_functions, (
            f"{endpoint} is registered again — the legacy copy was re-added and is now "
            "shadowing the blueprint; re-measure and update DELEGATION.md §4 and this pin "
            "together."
        )


def test_the_legacy_module_no_longer_defines_the_removed_handlers() -> None:
    """A **source** check: the closures are gone, not merely unreachable."""
    tree = ast.parse(_legacy_source())
    defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert len(defined) >= _MIN_LEGACY_FUNCTIONS, (
        f"{_LEGACY_MODULE} defines only {len(defined)} functions (floor "
        f"{_MIN_LEGACY_FUNCTIONS}); the module moved and this check would pass vacuously"
    )
    still_there = sorted(defined & set(_REMOVED_SHADOWED))
    assert still_there == [], (
        f"{_LEGACY_MODULE} defines {still_there} again — the shadowed closures are back; "
        "re-measure and update DELEGATION.md §4 and this pin together."
    )


# ── The invariant: every endpoint is reachable, and no pair is registered twice ──


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


def test_no_registered_endpoint_is_unreachable(tmp_path: Any, monkeypatch: Any) -> None:
    app = _app(tmp_path, monkeypatch)
    reachable, _dupes = _reachability(app)
    unreachable = sorted(set(app.view_functions) - reachable)
    assert unreachable == [], (
        f"these endpoints are registered but no rule can reach them: {unreachable}. A new "
        "entry is a new shadow (two rules for one path, or a converter stealing another's "
        "route); re-measure and update DELEGATION.md §4 and this pin together."
    )


def test_no_pair_is_registered_twice(tmp_path: Any, monkeypatch: Any) -> None:
    app = _app(tmp_path, monkeypatch)
    _reachable, dupes = _reachability(app)
    assert dupes == [], (
        f"these (method, path) pairs are registered twice: {dupes} — Werkzeug matches the "
        "first rule for a path, so the second handler can never run. Remove the shadowing "
        "copy (or re-point it) and move this pin together."
    )


def test_each_removed_path_is_still_served_by_its_modular_endpoint(
    tmp_path: Any, monkeypatch: Any
) -> None:
    """The deletion must not have removed the *route* — only the dead copy."""
    app = _app(tmp_path, monkeypatch)
    adapter = app.url_map.bind("localhost")
    for endpoint, (method, path, winner) in sorted(_REMOVED_SHADOWED.items()):
        got, _args = adapter.match(path, method=method)
        assert got == winner, (
            f"{method} {path} now resolves to {got!r}, not {winner!r} — the route the "
            "legacy copy used to shadow is broken; re-measure and update this pin."
        )
        assert got != endpoint
        winner_file = app.view_functions[winner].__code__.co_filename.replace("\\", "/")
        assert _LEGACY_MODULE not in winner_file, (
            f"the winner {winner} now lives in {_LEGACY_MODULE} — a legacy copy replaced "
            "the modular route; re-measure and update this pin."
        )


def test_multiplicity_equals_distinctness(tmp_path: Any, monkeypatch: Any) -> None:
    """The stale-number arithmetic, settled: with no duplicates the two counts coincide."""
    app = _app(tmp_path, monkeypatch)
    pairs: list[tuple[str, str]] = []
    for rule in app.url_map.iter_rules():
        for method in _methods(rule):
            pairs.append((method, rule.rule))
    assert len(pairs) == len(set(pairs)), (
        f"{len(pairs)} pairs, {len(set(pairs))} distinct — a duplicate pair is back, so a "
        "multiplicity count would double-count it again (the §3.2 '98 vs 96' shape)."
    )
