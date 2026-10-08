"""The dead ``audit.jsonl`` reading surface is gone — pin the *absence*.

Why this file exists
--------------------
``aegis_ai/audit.py`` (a module whose ``AuditLog`` wrote **JSONL**) and ``aegis_ai/audit/``
(a **package** whose ``AuditLog`` writes **SQLite**) collided; the package wins, so the
JSONL writer was unreachable and the file had **no writer**. Four sites still *read* it,
so ``GET /api/audit/stream`` streamed a file that only ever existed as a migration input,
``GET /api/autonomous/skip-reasons`` could only ever return ``[]``, and
``_load_audit_entries`` was never called at all.

That was **recorded, not fixed** (``DELEGATION.md`` §4 item 25, pinned by the since-retired
``test_audit_jsonl_has_no_writer.py``). It was executed on 2026-10-08 (cycle 104) under the
owner's decision to **delete**:

* ``aegis_ai/audit.py`` — the shadowed module;
* ``GET /api/audit/stream`` and ``GET /api/autonomous/skip-reasons`` — the two dead routes;
* ``_load_audit_entries`` — the dead helper, plus its ``dashboard_routes`` facade entries;
* the JSONL fallback inside ``GET /api/audit/grouped``.

⚠️ **Two of the row's premises were refuted by measurement**, and this pin encodes the
correction rather than the row:

1. The row says "**four routes**". Two are routes; one is a **helper** with no call site;
   and one is a **dead branch inside a live route** — ``/api/audit/grouped`` has a client
   (``web-ui/src/api/client.ts``) and its main path *always* runs, because the runtime
   always carries an ``AuditManager`` with ``list_groups``. Deleting that route would have
   broken a live endpoint, so only its fallback was removed.
2. The row names the route ``/api/audit/groups``; nothing registers that path — the real
   one is ``/api/audit/grouped``.

Scope — and what deliberately **stays**:

* ``AuditManager._read_tail`` / ``_read_by_id_reverse`` remain. They are the SQLite-failure
  fallbacks, they are *inert* (they read the never-written file and degrade to "no
  entries"), and ``_read_by_id_reverse`` is named by ``test_audit_failures_are_named.py``'s
  census — removing them would move an unrelated pin for no behavioural gain.
* ``AuditManager.rotate()`` still reads the JSONL tail (the wrong file) and so always
  returns 0; it also has **no caller**. Recorded, not fixed: the repair is a behaviour
  change (read SQLite), not a deletion.
* ``dashboard_legacy.py``'s ``_build_audit_timeline`` (and its only callee
  ``_is_error_audit_entry``) and ``_load_error_log_entries`` are dead but do **not** read
  this file; out of item 25's scope, recorded in the daily log.

How it checks. Each property has a non-vacuity half, so a scan that stops reading the tree
fails rather than passing silently:

1. the scan still reads the tree; the package exists, the shadowed module does not, and the
   same scanner still finds a token that *is* present;
2. the shadowed module is gone;
3. the package still resolves as the import target and still redirects ``.jsonl`` to
   ``.db`` (behavioural — run it, do not reason about it);
4. no source file names a removed route or the removed helper, while the surviving route is
   named by exactly its own file;
5. the set of files naming ``audit.jsonl`` is **exactly** the writer's own plumbing, so a
   new reader *or* writer is a failure;
6. driving the real app: the two dead routes are not registered and the live one still is;
7. the deliberately-kept SQLite-failure fallbacks still exist, so the deletion cannot be
   widened by accident.

**This file will fail the day someone re-adds the surface, or removes the kept fallbacks.**
That is the point: the pin and the record must move together, deliberately.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_dashboard_routes import _runtime

from aegis_ai.web import dashboard_routes

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "ai-server" / "src"
_AEGIS = _SRC / "aegis_ai"

#: The collision's two halves: the module is gone, the package stays.
_REMOVED_MODULE = _AEGIS / "audit.py"
_PACKAGE_INIT = _AEGIS / "audit" / "__init__.py"

#: What was removed (item 25) and what must survive it.
_REMOVED_ROUTES = ("/api/audit/stream", "/api/autonomous/skip-reasons")
_REMOVED_HELPER = "_load_audit_entries"
_SURVIVING_ROUTE = "/api/audit/grouped"
_SURVIVING_ROUTE_FILE = _AEGIS / "web" / "routes" / "autonomous.py"

#: Match the **basename exactly**: a bare substring also matches ``settings_audit.jsonl``
#: and ``controller_audit.jsonl``, which are different files.
_AUDIT_JSONL = re.compile(r"(?<![A-Za-z0-9_])audit\.jsonl")

#: Recorded, measured 2026-10-08 (cycle 104, after the deletion). **Equality** — the only
#: files that may name the file are the *writer's* own plumbing: its default/migration
#: reader, the config default, and the one construction (which redirects to ``.db``). A new
#: entry is a new reader or a writer, and either moves the record.
_RECORDED_NAMERS = frozenset({
    "aegis_ai/audit/audit_log.py",  # default arg + the one-time migration reader
    "aegis_ai/config.py",  # the env-var default
    "aegis_ai/runtime.py",  # the one construction (redirects to .db)
})

#: The SQLite-failure fallbacks that were deliberately kept.
_KEPT_FALLBACKS = ("_read_tail", "_read_by_id_reverse")

#: A floor, so an empty walk cannot make the absence scan vacuously pass.
_MIN_SRC_FILES = 380


# ── Scans ────────────────────────────────────────────────────────────────────


def _src_files() -> list[Path]:
    return [
        p
        for p in _SRC.rglob("*.py")
        if "__pycache__" not in p.parts and ".venv" not in p.parts
    ]


def _rel(path: Path) -> str:
    return path.relative_to(_SRC).as_posix()


def _namers() -> set[str]:
    return {
        _rel(p)
        for p in _src_files()
        if _AUDIT_JSONL.search(p.read_text(encoding="utf-8", errors="ignore"))
    }


def _token_hits(token: str) -> set[str]:
    return {
        _rel(p)
        for p in _src_files()
        if token in p.read_text(encoding="utf-8", errors="ignore")
    }


# ── Non-vacuity: the subjects exist and the scans still read ─────────────────


def test_the_scan_reads_the_tree_and_the_survivors_exist() -> None:
    files = _src_files()
    assert len(files) >= _MIN_SRC_FILES, (
        f"only {len(files)} source files found (floor {_MIN_SRC_FILES}); a root moved "
        "and the absence scan would pass vacuously"
    )
    assert _PACKAGE_INIT.exists(), (
        f"{_PACKAGE_INIT} is gone; the package is the surviving audit surface"
    )
    # The same scanner must still find something that *is* present, or "not found" means
    # "the walk is broken" rather than "it was removed".
    assert _token_hits("_read_by_id_reverse") == {"aegis_ai/audit/audit_manager.py"}, (
        "the absence scan found nothing even for a token that still exists — the walk is "
        "not reading the tree"
    )


def test_the_shadowing_module_is_gone() -> None:
    assert not _REMOVED_MODULE.exists(), (
        f"{_REMOVED_MODULE} is back. It is unreachable by construction (the package wins "
        "the name), so it can only shadow or confuse — see DELEGATION.md item 25."
    )


# ── The mechanism, measured by running it ────────────────────────────────────


def test_the_package_still_resolves_and_redirects_to_sqlite(tmp_path: Path) -> None:
    """The root cause and the sink, both measured rather than reasoned about."""
    spec = importlib.util.find_spec("aegis_ai.audit")
    assert spec is not None and spec.origin is not None, "aegis_ai.audit is not importable"
    assert Path(spec.origin).resolve() == _PACKAGE_INIT.resolve(), (
        f"aegis_ai.audit now resolves to {spec.origin}, not the package "
        f"({_PACKAGE_INIT}) — the audit sink moved"
    )

    from aegis_ai.audit import AuditLog

    jsonl = tmp_path / "audit.jsonl"
    db = tmp_path / "audit.db"
    log = AuditLog(path=str(jsonl))
    log.log_decision(
        action="pin_probe", capability_id="probe", decision="allow", reason="measurement"
    )
    log.close()

    assert db.exists(), "the reachable AuditLog no longer writes SQLite"
    assert not jsonl.exists(), (
        f"{jsonl.name} was created by the reachable AuditLog. The sink no longer redirects "
        ".jsonl to .db — the surface may be live again. Re-measure and re-record."
    )


# ── The invariant: the readers are gone, the writer's plumbing is all that names it ──


def test_no_source_file_names_a_removed_route_or_helper() -> None:
    for token in (*_REMOVED_ROUTES, _REMOVED_HELPER):
        hits = _token_hits(token)
        assert hits == set(), f"{token} is back in {sorted(hits)} (DELEGATION.md item 25)"
    # Control: the surviving route must still be named — by exactly its own file.
    assert _token_hits(_SURVIVING_ROUTE) == {_rel(_SURVIVING_ROUTE_FILE)}, (
        f"{_SURVIVING_ROUTE} is named by {sorted(_token_hits(_SURVIVING_ROUTE))}; expected "
        f"only {_rel(_SURVIVING_ROUTE_FILE)}. The live route must not have been deleted."
    )


def test_the_recorded_namers_are_unchanged() -> None:
    namers = _namers()
    assert namers == _RECORDED_NAMERS, (
        "the set of source files naming audit.jsonl changed.\n"
        f"  added:   {sorted(namers - _RECORDED_NAMERS)}\n"
        f"  removed: {sorted(_RECORDED_NAMERS - namers)}\n"
        "An *added* file is a new reader (the surface is coming back) or a **writer** (the "
        "file is no longer writer-less). A *removed* file means the sink's plumbing moved — "
        "re-measure and re-record."
    )


# ── The consequence: driving the real app ────────────────────────────────────


@pytest.fixture
def _app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> object:
    """The real dashboard app, built the way the route-surface tests build it."""
    monkeypatch.setenv("AEGIS_RUNTIME_MODE", "production")
    monkeypatch.setenv("AEGIS_SESSION_SECRET", "x" * 64)
    monkeypatch.setenv("AEGIS_UI_VERSION", "v2")
    for name in (
        "AEGIS_AUTH_MODE",
        "AEGIS_DASHBOARD_ACCESS_TOKEN",
        "AEGIS_DISPLAY_TOKEN",
        "AEGIS_DISPLAY_READ_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(dashboard_routes, "_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(dashboard_routes.DashboardApp, "_start_autonomous_loop", lambda self: None)
    runtime = _runtime(tmp_path)
    runtime.presentation_manager = SimpleNamespace(
        list_active=lambda limit=20: [], get_status=lambda: {}
    )
    app = dashboard_routes.DashboardApp(runtime=runtime).app
    app.config.update(TESTING=True)
    return app


def test_the_dead_routes_are_not_registered_and_the_live_one_is(_app: object) -> None:
    pairs = {
        (method, str(rule))
        for rule in _app.url_map.iter_rules()  # type: ignore[attr-defined]
        for method in rule.methods
        if method not in {"HEAD", "OPTIONS"}
    }
    for path in _REMOVED_ROUTES:
        assert ("GET", path) not in pairs, f"{path} is registered again (item 25)"
    assert ("GET", _SURVIVING_ROUTE) in pairs, (
        f"{_SURVIVING_ROUTE} is not registered — a *live* route was deleted with the dead ones"
    )


# ── The deliberate survivors: the deletion must not be widened ───────────────


def test_the_kept_sqlite_failure_fallbacks_still_exist() -> None:
    text = (_AEGIS / "audit" / "audit_manager.py").read_text(encoding="utf-8")
    for name in _KEPT_FALLBACKS:
        assert f"def {name}(" in text, (
            f"{name} was removed from audit_manager.py. It is the SQLite-failure fallback "
            "and is named by test_audit_failures_are_named.py's census — removing it is a "
            "different decision (see DELEGATION.md item 25's scope note)."
        )
