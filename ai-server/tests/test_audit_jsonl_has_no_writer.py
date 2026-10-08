"""``data/audit.jsonl`` has readers and **no writer** — pin the fact, not a fix.

Why this file exists
--------------------
Two things are named ``audit`` under ``aegis_ai``:

* ``aegis_ai/audit.py`` — a module whose ``AuditLog`` writes **JSONL**;
* ``aegis_ai/audit/`` — a **package** whose ``AuditLog`` writes **SQLite**.

The package wins (a directory with ``__init__.py`` shadows a sibling module of the
same name), so ``from aegis_ai.audit import AuditLog`` — the only import anyone
writes — yields the **SQLite** class, and the JSONL writer is unreachable.

That single collision has a consequence nobody recorded. ``runtime.py`` builds
``AuditLog(path=os.path.join(data_dir, "audit.jsonl"))``, but the reachable
``AuditLog.__init__`` opens with ``db_path = Path(path).with_suffix(".db")``, so the
path it is handed **becomes ``data/audit.db``**. The ``.jsonl`` name survives only as
a one-time *migration input* (``_migrate_jsonl_if_needed`` reads it when the DB is
empty). Nothing ever writes it.

Measured 2026-10-03:

* **No writer.** The only ``AuditLog(...)`` construction in ``src/`` is
  ``runtime.py``'s, and it redirects to ``.db``. The only write-mode ``open`` on an
  audit path in ``src/`` is ``settings/store.py`` — and that is
  ``settings_audit.jsonl``, a *different* file. (``AuditManager.rotate`` writes
  ``audit_archive/audit_YYYY-MM.jsonl``, also different — and it reads the never-written
  file first, so it can never rotate anything either.)
* **Readers.** Four sites poll the file and degrade silently when it is absent:
  ``GET /api/audit/stream`` (``dashboard_legacy.py``), a second route in the same file,
  and two in ``routes/autonomous.py``; plus ``AuditManager._read_tail`` /
  ``_read_by_id_reverse``, which are SQLite-failure fallbacks.

So ``GET /api/audit/stream`` is dead by a **third** mechanism — not a missing producer
(the chat-SSE shape, deleted 2026-10-08) and not merely "no client", but a **stale source**: it streams a
file that only ever existed as a migration input, so it can emit heartbeats and
nothing else. Rewiring the readers to SQLite, or deleting them, is an **owner
decision** (recorded in ``DELEGATION.md`` §4), so this pins the fact instead.

How it checks. Six properties, each with a non-vacuity half, so a scan that stops
reading the tree fails rather than passing silently:

1. the scan still reads the tree, and both ``audit`` surfaces still exist;
2. the **reachable** ``AuditLog`` redirects a ``.jsonl`` path to ``.db`` (behavioural);
3. the package really does shadow the module (``find_spec``), and the module is there;
4. **no source file opens an audit path in a write mode**, and the only ``AuditLog``
   construction is the redirecting one;
5. the set of files that name ``audit.jsonl`` equals the recorded set, so a new
   reader *or* writer is a failure;
6. the route is still registered and still has no subscriber.

**This file will fail the day someone fixes the collision or rewires the readers.**
That is the point: the pin and the record must move together, deliberately.
"""

from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "ai-server" / "src"
_AEGIS = _SRC / "aegis_ai"

#: The file that is read but never written. Match the **basename exactly**: a bare
#: substring test also matches ``settings_audit.jsonl`` and ``controller_audit.jsonl``,
#: which are different files — the first draft of this pin did exactly that.
_UNWRITTEN = "audit.jsonl"
_AUDIT_JSONL = re.compile(r"(?<![A-Za-z0-9_])audit\.jsonl")

#: The two surfaces whose collision is the root cause.
_SHADOWING_MODULE = _AEGIS / "audit.py"
_SHADOWING_PACKAGE_INIT = _AEGIS / "audit" / "__init__.py"

#: The route that polls the file, and every source tree a subscriber could live in.
_ROUTE_PATH = "/api/audit/stream"
_ROUTE_FILE = _AEGIS / "web" / "dashboard_legacy.py"
_SOURCE_ROOTS = (
    _SRC,
    _REPO / "web-ui" / "src",
    _REPO / "pc-server" / "src",
    _REPO / "browser-server" / "src",
    _REPO / "room-server",
    _REPO / "packages" / "aegis-sdk-python",
)

#: Recorded, measured 2026-10-03: every source file that names ``audit.jsonl``.
#: **Equality** — a new entry is a new reader or a writer, and either moves the record.
_RECORDED_NAMERS = frozenset({
    "aegis_ai/audit/audit_log.py",  # default arg + migration reader
    "aegis_ai/audit.py",  # the shadowed module
    "aegis_ai/config.py",  # AEGIS_AUDIT_PATH default
    "aegis_ai/runtime.py",  # the one construction (redirects to .db)
    "aegis_ai/web/dashboard_legacy.py",  # two readers, one an SSE route
    "aegis_ai/web/routes/autonomous.py",  # two readers
})

#: Write modes. An ``open`` with none of these (or no mode at all) only reads.
_WRITE_MODES = frozenset("wax+")

#: A floor, so an empty walk cannot make the writer scan vacuously pass.
_MIN_SRC_FILES = 300


# ── Scans ────────────────────────────────────────────────────────────────────


def _src_files() -> list[Path]:
    return [
        p
        for p in _SRC.rglob("*.py")
        if "__pycache__" not in p.parts and ".venv" not in p.parts
    ]


def _all_sources() -> list[Path]:
    seen: list[Path] = []
    for root in _SOURCE_ROOTS:
        if not root.is_dir():
            continue
        seen.extend(
            p
            for p in root.rglob("*.py")
            if "__pycache__" not in p.parts and ".venv" not in p.parts
        )
        seen.extend(
            p
            for p in root.rglob("*.ts")
            if "node_modules" not in p.parts
        )
        seen.extend(
            p
            for p in root.rglob("*.tsx")
            if "node_modules" not in p.parts
        )
    return seen


def _rel(path: Path) -> str:
    return path.relative_to(_SRC).as_posix()


def _call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _text(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:  # noqa: BLE001 — an unparsable node is simply not a match
        return ""


def _audit_writers() -> list[str]:
    """Every write-mode ``open``/``write_text`` whose path names an audit file."""
    found: list[str] = []
    for path in _src_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node)
            args = list(node.args)
            kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
            if name == "open":
                target = _text(args[0]) if args else _text(kwargs.get("path"))
                mode_node = args[1] if len(args) > 1 else kwargs.get("mode")
                mode = _text(mode_node) or "'r'"
            elif name in {"write_text", "write_bytes"}:
                # The receiver *is* the path; the first argument is the data.
                target = _text(node.func.value)
                mode = "'w'"
            else:
                continue
            if _AUDIT_JSONL.search(target) and any(ch in mode for ch in _WRITE_MODES):
                found.append(f"{_rel(path)}:{node.lineno}  {name}({target}, {mode})")
    return found


def _audit_log_constructions() -> list[str]:
    """Every ``AuditLog(...)`` construction in ``src``, with its path argument."""
    found: list[str] = []
    for path in _src_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or _call_name(node) != "AuditLog":
                continue
            kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
            arg = _text(node.args[0]) if node.args else _text(kwargs.get("path"))
            found.append(f"{_rel(path)}:{node.lineno}  AuditLog(path={arg})")
    return found


def _namers() -> set[str]:
    return {
        _rel(p)
        for p in _src_files()
        if _AUDIT_JSONL.search(p.read_text(encoding="utf-8", errors="ignore"))
    }


# ── Non-vacuity: the subjects exist and the scans still read ─────────────────


def test_the_scan_reads_the_tree_and_both_audit_surfaces_exist() -> None:
    files = _src_files()
    assert len(files) >= _MIN_SRC_FILES, (
        f"only {len(files)} source files found (floor {_MIN_SRC_FILES}); a root moved "
        "and the writer scan would pass vacuously"
    )
    assert _SHADOWING_MODULE.exists(), (
        f"{_SHADOWING_MODULE} is gone. If the module was deleted, the collision is "
        "resolved — re-measure and update DELEGATION.md §4 and this pin together."
    )
    assert _SHADOWING_PACKAGE_INIT.exists(), (
        f"{_SHADOWING_PACKAGE_INIT} is gone; the package no longer shadows the module "
        "and the JSONL writer may now be reachable"
    )


def test_the_reachable_audit_log_redirects_jsonl_to_sqlite(tmp_path: Path) -> None:
    """The mechanism, measured by running it: a ``.jsonl`` path becomes ``.db``."""
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
        f"{jsonl.name} was created by the reachable AuditLog. The class no longer "
        "redirects .jsonl to .db — either the collision was fixed (the JSONL writer is "
        "now reachable) or the sink moved. Re-measure and re-record."
    )


def test_the_package_shadows_the_module() -> None:
    """The root cause, measured by the import system itself, not by reasoning."""
    spec = importlib.util.find_spec("aegis_ai.audit")
    assert spec is not None and spec.origin is not None, "aegis_ai.audit is not importable"
    assert Path(spec.origin).resolve() == _SHADOWING_PACKAGE_INIT.resolve(), (
        f"aegis_ai.audit now resolves to {spec.origin}, not the package "
        f"({_SHADOWING_PACKAGE_INIT}). If the module now wins, the JSONL writer is "
        "reachable and this pin plus DELEGATION.md §4 are stale."
    )
    assert spec.submodule_search_locations is not None, (
        "aegis_ai.audit resolved to a module, not a package — the collision is gone"
    )


# ── The invariant: nothing writes the file, and the readers are the recorded ones ─


def test_no_source_file_writes_an_audit_path() -> None:
    writers = _audit_writers()
    assert writers == [], (
        "a source file now opens an audit path for writing:\n  "
        + "\n  ".join(writers)
        + f"\nIf it writes {_UNWRITTEN}, the file is no longer reader-only — the route "
        "is alive and this pin plus DELEGATION.md §4 are stale."
    )


def test_the_only_audit_log_construction_is_the_redirecting_one() -> None:
    constructions = _audit_log_constructions()
    assert len(constructions) == 1, (
        "expected exactly one AuditLog(...) construction in src/ (runtime.py's, which "
        f"redirects to .db); found {len(constructions)}:\n  " + "\n  ".join(constructions)
    )
    assert "runtime.py" in constructions[0], (
        f"the single AuditLog construction moved: {constructions[0]}"
    )
    assert _UNWRITTEN in constructions[0], (
        f"the construction no longer names {_UNWRITTEN}, so this pin's premise is "
        f"stale: {constructions[0]}"
    )


def test_the_recorded_namers_are_unchanged() -> None:
    namers = _namers()
    assert namers == _RECORDED_NAMERS, (
        "the set of source files naming audit.jsonl changed.\n"
        f"  added:   {sorted(namers - _RECORDED_NAMERS)}\n"
        f"  removed: {sorted(_RECORDED_NAMERS - namers)}\n"
        "An *added* file is a new reader (fine, record it) or a **writer** (the file is "
        "no longer reader-only). A *removed* file means a reader was dropped — re-measure."
    )


# ── The consequence: the route is registered and has no subscriber ───────────


def test_the_audit_stream_route_is_still_registered() -> None:
    text = _ROUTE_FILE.read_text(encoding="utf-8")
    assert f'"{_ROUTE_PATH}"' in text, (
        f"{_ROUTE_FILE} no longer registers {_ROUTE_PATH}. If the route was deleted, "
        "that was an owner decision — update DELEGATION.md §4 and this pin together."
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
