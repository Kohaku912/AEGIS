"""Cycle 110 pin: the audit JSONL is a read-only legacy source, and two live reads fall back to it.

Measured 2026-10-09 (HEAD e80a64a). ``AuditLog.__init__`` sets ``_path`` (a JSONL file, default
``data/audit.jsonl``) and ``_db_path`` (``<same stem>.db``). Writes go to **SQLite**; the JSONL is
only *read*, once, by ``_migrate_jsonl_if_needed`` (a one-shot import), and is **never written again**
by anything under ``src/``. ``AuditManager`` captures ``audit_log._path`` as ``self._audit_path``
(``audit_manager.py:69``) and uses it in exactly three places:

* ``rotate()`` -- as its **only** source. ``_read_tail(10000)`` therefore always returns fewer than
  10000 entries (the file is absent on the shipped deployment), so ``len(entries) < 10000`` is always
  true and ``rotate()`` **always returns 0**. It also has **0 call sites** under ``src/`` (``ast``),
  so the breakage is currently *latent*: a future wiring would silently add a no-op rotation.
* ``_read_recent_entries`` -- as a **fallback** when ``self._log.read_page`` raises.
* ``_read_recent_entries_filtered`` -- as a **fallback** when the filtered SQLite query raises.

On the shipped deployment ``data/audit.jsonl`` does not exist, so ``_read_tail`` returns ``[]`` and a
SQLite failure makes a dashboard read an **empty** audit history -- indistinguishable from "there are
no entries". That is the "an unreadable source looks like an empty source" family (DELEGATION.md
section 4 items 37/38/66/67), one level below the naming already pinned by
``test_audit_failures_are_named.py`` (the handler *names itself* at DEBUG, but the caller still cannot
tell "empty" from "unreadable").

This file pins the **facts** (no behaviour change): the JSONL has no writer under ``src/``, ``rotate``
is unreachable, and the reachable fallback degrades to ``[]``. Whether to remove the fallback, make it
carry its cause, or wire rotation is an owner decision (DELEGATION.md section 4 item 77).
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from aegis_ai.audit.audit_log import AuditLog
from aegis_ai.audit.audit_manager import AuditManager

_SERVER = Path(__file__).resolve().parents[1]
_SRC = _SERVER / "src"
_AUDIT_PKG = _SRC / "aegis_ai" / "audit"
_MANAGER = _AUDIT_PKG / "audit_manager.py"

_MIN_SRC_FILES = 380  # measured 391 (2026-10-09)

_WRITE_MODES = {"w", "a", "x", "w+", "a+", "x+", "wb", "ab", "xb"}


def _src_files() -> list[Path]:
    return sorted(_SRC.rglob("*.py"))


def _open_calls(tree: ast.AST) -> list[ast.Call]:
    return [
        n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "open"
    ]


def _mode_of(call: ast.Call) -> str:
    for kw in call.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            return kw.value.value
    if len(call.args) >= 2 and isinstance(call.args[1], ast.Constant) and isinstance(call.args[1].value, str):
        return call.args[1].value
    return "r"


def _target_text(call: ast.Call) -> str:
    return ast.unparse(call.args[0]) if call.args else ""


def _rotate_call_sites() -> list[str]:
    sites: list[str] = []
    for p in _src_files():
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "rotate":
                sites.append(f"{p.relative_to(_SERVER).as_posix()}:{node.lineno}")
    return sites


# ── the scan actually reaches the surface ──────────────────────────────────


def test_the_scan_reads_the_shipped_tree() -> None:
    files = _src_files()
    assert len(files) >= _MIN_SRC_FILES, f"only {len(files)} modules scanned; the walk is not reaching src/"
    assert _MANAGER.is_file(), "audit_manager.py is not where the pin expects it"


# ── the JSONL has no writer ────────────────────────────────────────────────


def test_no_module_in_the_audit_package_writes_the_jsonl_path() -> None:
    """``self._path`` is opened for reading (the one-shot migration) and nothing else."""
    offenders: list[str] = []
    for p in sorted(_AUDIT_PKG.rglob("*.py")):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for call in _open_calls(tree):
            if "_path" in _target_text(call) and _mode_of(call) in _WRITE_MODES:
                offenders.append(f"{p.name}:{call.lineno} opens {_target_text(call)} in {_mode_of(call)!r}")
    assert offenders == [], f"the audit JSONL is now written: {offenders}"


def test_no_module_under_src_opens_the_audit_jsonl_literal_for_writing() -> None:
    """The literal ``audit.jsonl`` (but not ``settings_audit.jsonl``) is never opened in a write mode."""
    offenders: list[str] = []
    for p in _src_files():
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for call in _open_calls(tree):
            target = _target_text(call)
            if "audit.jsonl" in target and "settings_audit" not in target and _mode_of(call) in _WRITE_MODES:
                offenders.append(f"{p.relative_to(_SERVER).as_posix()}:{call.lineno} opens {target!r}")
    assert offenders == [], f"something now writes the audit JSONL: {offenders}"


def test_the_audit_path_is_assigned_once_from_the_log() -> None:
    """``_audit_path`` is a copy of ``audit_log._path`` and is never reassigned."""
    tree = ast.parse(_MANAGER.read_text(encoding="utf-8"))
    assigned: list[tuple[ast.expr, ast.expr]] = []  # (target, value)
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Attribute) and t.attr == "_audit_path":
                    assigned.append((t, n.value))
        elif isinstance(n, ast.AnnAssign):
            t = n.target
            if isinstance(t, ast.Attribute) and t.attr == "_audit_path" and n.value is not None:
                assigned.append((t, n.value))
    assert len(assigned) == 1, f"expected exactly one assignment to _audit_path, found {len(assigned)}"
    assert "_path" in ast.unparse(assigned[0][1]), (
        f"_audit_path must come from audit_log._path, got {ast.unparse(assigned[0][1])!r}"
    )


# ── rotate() is unreachable and cannot rotate ──────────────────────────────


def test_rotate_has_no_call_site_under_src() -> None:
    sites = _rotate_call_sites()
    assert sites == [], f"rotate() is now reachable -- it is broken and returns 0 unconditionally: {sites}"


def test_rotate_reads_the_jsonl_and_not_the_database() -> None:
    """``rotate``'s only source is the JSONL path; it never touches the SQLite log."""
    tree = ast.parse(_MANAGER.read_text(encoding="utf-8"))
    rotate = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "rotate")
    body = ast.unparse(rotate)
    assert "_read_tail" in body, "rotate no longer reads the JSONL tail"
    assert "read_page" not in body and "_db_path" not in body, "rotate now reads SQLite; re-measure the finding"


def test_rotate_returns_zero_when_the_jsonl_is_absent(tmp_path) -> None:
    log = AuditLog(path=str(tmp_path / "audit.jsonl"))
    manager = AuditManager(log, data_dir=str(tmp_path))
    assert not (tmp_path / "audit.jsonl").exists(), "the probe assumed no JSONL"
    assert manager.rotate() == 0, "rotate() returned non-zero without a JSONL source"


# ── the live fallback degrades to an empty list, silently ──────────────────


def test_a_sqlite_read_failure_silently_yields_no_entries(tmp_path, caplog) -> None:
    log = AuditLog(path=str(tmp_path / "audit.jsonl"))
    manager = AuditManager(log, data_dir=str(tmp_path))

    def _boom(*_a, **_k):
        raise RuntimeError("sqlite is unreadable")

    manager._log.read_page = _boom  # type: ignore[method-assign]
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.audit.audit_manager"):
        result = manager._read_recent_entries(5)
    assert result == [], f"expected the silent-empty fallback, got {result!r}"
    named = [r for r in caplog.records if "SQLite audit page read failed" in r.getMessage()]
    assert named, "the fallback no longer names itself -- it would be silent in a different way"
    assert all(r.levelno == logging.DEBUG for r in named), "the fallback is no longer at DEBUG"


# ── the detector is not vacuous ────────────────────────────────────────────


def test_the_writer_detector_is_not_vacuous() -> None:
    """The write-mode detector must fire on a synthetic writer, or the absences prove nothing."""
    tree = ast.parse("open(self._path, 'a', encoding='utf-8')\n")
    calls = _open_calls(tree)
    assert calls, "the detector did not see a bare open()"
    assert _mode_of(calls[0]) == "a", f"the detector misread the mode as {_mode_of(calls[0])!r}"
    assert "_path" in _target_text(calls[0]), "the detector did not see the target"
