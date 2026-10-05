"""Cycle 51 pin: every failure handler under ``audit/`` now names itself.

Measured 2026-10-06 (HEAD 312f305). The unit is the one cycles 43-50 used — **a handler
whose entire body is a single statement that discards the failure** — extended here by one
shape, because ``audit/`` supplies the case that shows the shape matters:

* ``audit/context.py`` had **2** bare-``pass`` handlers (``:104`` inside
  ``_safe_reset_audit_group``, ``:140`` in ``clear_audit_group``) and **no logger at all**.
  Both are the "must never 500 a request" idiom, so the silence was deliberate — but a
  deliberate silence that is *unobservable* is indistinguishable from a bug. They now log
  at DEBUG with ``exc_info``.
* ``audit/audit_manager.py`` had **2** bare-``pass`` handlers (``:440``, ``:484``) in the two
  reverse-scan readers, **plus 2 bare-``continue`` handlers** (``:434``, ``:476``) in the loop
  bodies directly above them. The ``continue`` pair is the one that actually fires for the
  realistic corruption: a process killed mid-``append`` leaves a **truncated final line**,
  and that line is reached through ``lines[1:]`` — the in-loop handler — not through the
  post-loop ``remainder``. Measured before the fix: a truncated last line produced **no
  record at all**, while the post-loop ``pass`` fires only when the file's **first** line is
  corrupt. Naming only the ``pass`` would therefore have left the common case silent.
* ``audit/audit_log.py:288`` keeps its bare ``pass`` on purpose. It is **dead**:
  ``_insert_record`` issues ``INSERT OR IGNORE``, which absorbs the very
  ``sqlite3.IntegrityError`` the handler names. It is allow-listed below, keyed by
  ``(file, except-type)``, and pinned behaviourally by
  ``test_audit_duplicate_entry_ids_are_dropped_silently.py`` (whose M5 mutant survives by
  design). Naming it would *hide* the finding rather than fix it — the finding is that
  ``OR IGNORE`` makes the handler unreachable, and what to do about that is an owner
  decision (``DELEGATION.md`` §4 item 52).

Package census after the change: **4 files / 23 handlers**, of which exactly **one** is a
bare discard — the allow-listed dead one.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

import aegis_ai.audit as audit_pkg
from aegis_ai.audit import context
from aegis_ai.audit.audit_manager import AuditManager

PKG = Path(audit_pkg.__file__).parent

CONTEXT_LOGGER = "aegis_ai.audit.context"
MANAGER_LOGGER = "aegis_ai.audit.audit_manager"

# (file, except-type as written) -> why the bare discard is deliberate.
ALLOWED_DISCARDS: dict[tuple[str, str], str] = {
    ("audit_log.py", "sqlite3.IntegrityError"): (
        "dead while `INSERT OR IGNORE` absorbs the violation; pinned by "
        "test_audit_duplicate_entry_ids_are_dropped_silently.py (DELEGATION.md §4 item 52)"
    ),
}

# (file, function) -> handler count, measured 2026-10-06.
NAMED_SITES: dict[tuple[str, str], int] = {
    ("context.py", "_safe_reset_audit_group"): 2,
    ("context.py", "clear_audit_group"): 1,
    ("audit_manager.py", "_reverse_read"): 2,
    ("audit_manager.py", "_read_by_id_reverse"): 3,
}


# ------------------------------------------------------------------ ast helpers


def _handlers(tree: ast.AST) -> list[ast.ExceptHandler]:
    return [h for node in ast.walk(tree) if isinstance(node, ast.Try) for h in node.handlers]


def _own_handlers(fn: ast.AST) -> list[ast.ExceptHandler]:
    """Handlers belonging to ``fn`` itself, excluding nested function bodies."""
    out: list[ast.ExceptHandler] = []

    def visit(node: ast.AST) -> None:
        if node is not fn and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        if isinstance(node, ast.Try):
            out.extend(node.handlers)
        for child in ast.iter_child_nodes(node):
            visit(child)

    for child in ast.iter_child_nodes(fn):
        visit(child)
    return out


def _discard_shape(handler: ast.ExceptHandler) -> str | None:
    """``"pass"`` / ``"continue"`` / ``"break"`` when the body is exactly that one statement."""
    if len(handler.body) != 1:
        return None
    stmt = handler.body[0]
    if isinstance(stmt, ast.Pass):
        return "pass"
    if isinstance(stmt, ast.Continue):
        return "continue"
    if isinstance(stmt, ast.Break):
        return "break"
    return None


def _names_its_failure(handler: ast.ExceptHandler) -> bool:
    """True when the handler body calls ``logger.<level>(...)`` anywhere."""
    for node in ast.walk(handler):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and getattr(func.value, "id", "") == "logger":
                return True
    return False


def _except_type(handler: ast.ExceptHandler) -> str:
    return ast.unparse(handler.type) if handler.type is not None else "bare"


def _source(name: str) -> str:
    return (PKG / name).read_text(encoding="utf-8")


def _function(tree: ast.AST, name: str) -> ast.AST:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"{name} not found in the module — re-measure")


def _records(caplog, name: str) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == name]


# --------------------------------------------------- the package-wide rule


def _package_discards() -> dict[tuple[str, str], str]:
    """Every bare-discard handler under ``audit/``, keyed by ``(file, except-type)``."""
    found: dict[tuple[str, str], str] = {}
    for path in sorted(PKG.glob("*.py")):
        for handler in _handlers(ast.parse(path.read_text(encoding="utf-8"))):
            shape = _discard_shape(handler)
            if shape is not None:
                found[(path.name, _except_type(handler))] = shape
    return found


def test_no_handler_in_the_audit_package_discards_a_failure_in_silence() -> None:
    found = _package_discards()
    unnamed = {k: v for k, v in found.items() if k not in ALLOWED_DISCARDS}
    assert unnamed == {}, (
        "a handler under audit/ still swallows its failure with a bare "
        f"{unnamed} — name it with a logger call, or allow-list it with a reason"
    )


def test_the_allow_list_is_not_stale() -> None:
    """The other direction: every allow-listed entry must still be a real bare discard.

    Without this, "fix the dead handler" would leave a permanently-green pin that keeps
    blessing a site that no longer needs blessing.
    """
    found = _package_discards()
    stale = sorted(k for k in ALLOWED_DISCARDS if k not in found)
    assert stale == [], (
        f"allow-listed discards {stale} are no longer bare discards — delete the entry"
    )


def test_the_census_is_not_vacuous() -> None:
    """Floors are measurements, not round numbers (measured 2026-10-06: 4 files / 23)."""
    files = sorted(PKG.glob("*.py"))
    total = sum(len(_handlers(ast.parse(p.read_text(encoding="utf-8")))) for p in files)
    assert len(files) >= 4, f"only {len(files)} modules scanned; the walk is not reaching the package"
    assert total >= 20, f"only {total} handlers scanned; the walk is not reaching the handlers"


def test_the_shape_detector_sees_every_discard_shape() -> None:
    """Detector self-test: the rule above is only meaningful if the walker can see a discard."""
    tree = ast.parse(
        "def f():\n"
        "    try:\n"
        "        pass\n"
        "    except ValueError:\n"
        "        pass\n"
        "    except TypeError:\n"
        "        continue\n"
        "    except KeyError:\n"
        "        break\n"
        "    except OSError:\n"
        "        logger.debug('named', exc_info=True)\n"
    )
    shapes = [_discard_shape(h) for h in _handlers(tree)]
    assert shapes == ["pass", "continue", "break", None], shapes
    named = [h for h in _handlers(tree) if _names_its_failure(h)]
    assert len(named) == 1, "the named-handler detector is blind"


# --------------------------------------------------------- the four named sites


def test_the_four_named_sites_still_name_their_failures() -> None:
    by_file: dict[str, ast.AST] = {}
    for (file, func), expected_count in NAMED_SITES.items():
        if file not in by_file:
            by_file[file] = ast.parse(_source(file))
        handlers = _own_handlers(_function(by_file[file], func))
        where = f"{file}::{func}"
        assert len(handlers) == expected_count, (
            f"{where} now has {len(handlers)} handlers, expected {expected_count} — re-measure "
            "and update the pin rather than the count"
        )
        discards = [h.lineno for h in handlers if _discard_shape(h) is not None]
        assert discards == [], f"{where} still discards a failure silently at lines {discards}"
        assert any(_names_its_failure(h) for h in handlers), (
            f"{where} no longer names any failure through a logger call"
        )


def test_the_context_module_declares_its_own_logger() -> None:
    assert context.logger.name == CONTEXT_LOGGER, (
        "audit/context.py had no logger before cycle 51; a record from it must be "
        "attributable to the module that emitted it"
    )


# ------------------------------------------- _safe_reset_audit_group behaviour


class _ResetFailsVar:
    """Stands in for the ContextVar: ``reset`` always fails, ``set`` always succeeds."""

    def reset(self, token: object) -> None:
        raise ValueError("token was created in a different Context")

    def set(self, value: object) -> None:
        return None


class _BothFailVar:
    """``reset`` and the fallback ``set`` both fail — the double-failure path."""

    def reset(self, token: object) -> None:
        raise ValueError("token was created in a different Context")

    def set(self, value: object) -> None:
        raise RuntimeError("the context is gone")


def test_safe_reset_is_silent_on_the_clean_path(caplog) -> None:
    token = context._current_audit_group.set(context.AuditGroupContext(group_id="g"))
    with caplog.at_level(logging.DEBUG, logger=CONTEXT_LOGGER):
        context._safe_reset_audit_group(token)
    assert _records(caplog, CONTEXT_LOGGER) == [], "the healthy reset path now logs"


def test_safe_reset_is_silent_when_the_fallback_repairs_the_token(monkeypatch, caplog) -> None:
    """The subtle control: only the *outer* handler runs, so nothing should be recorded."""
    monkeypatch.setattr(context, "_current_audit_group", _ResetFailsVar())
    with caplog.at_level(logging.DEBUG, logger=CONTEXT_LOGGER):
        context._safe_reset_audit_group(object())
    assert _records(caplog, CONTEXT_LOGGER) == [], (
        "the repaired reset now logs; the record is supposed to mark the *double* failure"
    )


def test_safe_reset_names_the_double_fallback(monkeypatch, caplog) -> None:
    monkeypatch.setattr(context, "_current_audit_group", _BothFailVar())
    with caplog.at_level(logging.DEBUG, logger=CONTEXT_LOGGER):
        context._safe_reset_audit_group(object())
    records = _records(caplog, CONTEXT_LOGGER)
    assert len(records) == 1, f"the double failure is silent again: {records}"
    assert records[0].getMessage() == "Could not reset the audit group in this context"
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"
    assert records[0].levelno == logging.DEBUG


# ---------------------------------------------------- clear_audit_group behaviour


def test_clear_audit_group_is_silent_on_the_clean_path(caplog) -> None:
    context.bind_audit_group("g-clean")
    with caplog.at_level(logging.DEBUG, logger=CONTEXT_LOGGER):
        context.clear_audit_group()
    assert context.get_audit_group() is None
    assert _records(caplog, CONTEXT_LOGGER) == [], "the healthy clear path now logs"


def test_clear_audit_group_names_a_failure(monkeypatch, caplog) -> None:
    monkeypatch.setattr(context, "_current_audit_group", _BothFailVar())
    with caplog.at_level(logging.DEBUG, logger=CONTEXT_LOGGER):
        context.clear_audit_group()  # must not raise
    records = _records(caplog, CONTEXT_LOGGER)
    assert len(records) == 1, f"the clear failure is silent again: {records}"
    assert records[0].getMessage() == "Could not clear the audit group in this context"
    assert isinstance(records[0].exc_info, tuple)


# ------------------------------------------------------- reverse-read behaviour


def _manager() -> AuditManager:
    return object.__new__(AuditManager)


def _write(tmp_path: Path, content: bytes) -> Path:
    path = tmp_path / "audit.jsonl"
    path.write_bytes(content)
    return path


WELL_FORMED = b'{"entry_id": "a"}\n{"entry_id": "b"}\n'
# The realistic corruption: the process died mid-append, so the *last* line is truncated.
TRUNCATED_LAST = b'{"entry_id": "a"}\n{"entry_id"'
# A corrupt *first* line, which is what the post-loop `remainder` handler sees.
BAD_FIRST = b'{"entry_id"\n{"entry_id": "b"}\n'


def test_reverse_read_is_silent_on_a_well_formed_file(tmp_path, caplog) -> None:
    path = _write(tmp_path, WELL_FORMED)
    with caplog.at_level(logging.DEBUG, logger=MANAGER_LOGGER):
        entries = _manager()._reverse_read(path, 5)
    assert [e["entry_id"] for e in entries] == ["a", "b"]
    assert _records(caplog, MANAGER_LOGGER) == [], "the healthy reverse scan now logs"


def test_reverse_read_names_a_skipped_line(tmp_path, caplog) -> None:
    """A truncated final line: the case that was silent before cycle 51."""
    path = _write(tmp_path, TRUNCATED_LAST)
    with caplog.at_level(logging.DEBUG, logger=MANAGER_LOGGER):
        entries = _manager()._reverse_read(path, 5)
    assert [e["entry_id"] for e in entries] == ["a"], "the truncated line is no longer skipped"
    records = _records(caplog, MANAGER_LOGGER)
    assert [r.getMessage() for r in records] == ["Skipped an audit line that would not decode"]
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"
    assert records[0].levelno == logging.DEBUG


def test_reverse_read_names_the_leftover_line(tmp_path, caplog) -> None:
    """A corrupt *first* line, reached through the post-loop ``remainder``."""
    path = _write(tmp_path, BAD_FIRST)
    with caplog.at_level(logging.DEBUG, logger=MANAGER_LOGGER):
        entries = _manager()._reverse_read(path, 5)
    assert [e["entry_id"] for e in entries] == ["b"]
    records = _records(caplog, MANAGER_LOGGER)
    assert [r.getMessage() for r in records] == ["Dropped the leftover audit line that would not decode"]
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_read_by_id_reverse_is_silent_when_the_entry_is_found(tmp_path, caplog) -> None:
    path = _write(tmp_path, WELL_FORMED)
    manager = _manager()
    manager._audit_path = path
    with caplog.at_level(logging.DEBUG, logger=MANAGER_LOGGER):
        entry = manager._read_by_id_reverse("b")
    assert entry is not None and entry["entry_id"] == "b"
    assert _records(caplog, MANAGER_LOGGER) == [], "the healthy lookup now logs"


def test_read_by_id_reverse_names_a_skipped_line(tmp_path, caplog) -> None:
    """A corrupt line in the middle: the lookup misses, and now says why it might have."""
    path = _write(tmp_path, b'{"entry_id": "a"}\n{"entry_id"\n{"entry_id": "b"}\n')
    manager = _manager()
    manager._audit_path = path
    with caplog.at_level(logging.DEBUG, logger=MANAGER_LOGGER):
        entry = manager._read_by_id_reverse("z")
    assert entry is None
    records = _records(caplog, MANAGER_LOGGER)
    assert [r.getMessage() for r in records] == ["Skipped an audit line that would not decode"]
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_read_by_id_reverse_names_the_leftover_line(tmp_path, caplog) -> None:
    path = _write(tmp_path, BAD_FIRST)
    manager = _manager()
    manager._audit_path = path
    with caplog.at_level(logging.DEBUG, logger=MANAGER_LOGGER):
        entry = manager._read_by_id_reverse("z")
    assert entry is None
    records = _records(caplog, MANAGER_LOGGER)
    assert [r.getMessage() for r in records] == ["Dropped the leftover audit line that would not decode"]
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_the_named_records_stay_at_debug() -> None:
    """These are expected, recoverable conditions — announcing them at WARNING is noise.

    A level bump is a policy change, so it should be deliberate rather than silent.
    """
    by_file: dict[str, ast.AST] = {}
    checked = 0
    for file, func in NAMED_SITES:
        if file not in by_file:
            by_file[file] = ast.parse(_source(file))
        for handler in _own_handlers(_function(by_file[file], func)):
            for node in ast.walk(handler):
                if not isinstance(node, ast.Call):
                    continue
                callee = node.func
                if not (isinstance(callee, ast.Attribute) and getattr(callee.value, "id", "") == "logger"):
                    continue
                checked += 1
                assert callee.attr == "debug", (
                    f"{file}::{func} reports through logger.{callee.attr} at line "
                    f"{node.lineno}; cycle 51 named these at DEBUG"
                )
    assert checked >= 4, f"only {checked} logger calls inspected; the walk is not reaching the sites"


# --------------------------------------------------------------- non-vacuity


def test_the_debug_detector_is_not_vacuous(caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger=MANAGER_LOGGER):
        logging.getLogger(MANAGER_LOGGER).debug("control record")
    assert len(_records(caplog, MANAGER_LOGGER)) == 1, (
        "the record detector is blind; every 'is silent' assertion above proves nothing"
    )


# ------------------------------------------- the allow-list points at the dead handler


def test_the_allowlisted_handler_is_the_dead_integrity_error_one() -> None:
    tree = ast.parse(_source("audit_log.py"))
    discards = [h for h in _handlers(tree) if _discard_shape(h) is not None]
    assert len(discards) == 1, f"audit_log.py has {len(discards)} bare discards — re-measure"
    assert _except_type(discards[0]) == "sqlite3.IntegrityError"

    source = _source("audit_log.py")
    assert "INSERT OR IGNORE" in source, (
        "the allow-listed handler is only dead while `INSERT OR IGNORE` absorbs the "
        "violation; a plain INSERT would make it live and silent again"
    )
    assert (PKG.parent.parent.parent / "tests" / "test_audit_duplicate_entry_ids_are_dropped_silently.py").exists(), (
        "the behavioural pin for the dead handler is gone; the allow-list no longer has a contract"
    )
