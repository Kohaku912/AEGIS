"""Cycle 61 pin: a duplicate ``entry_id`` is dropped from the table — and now announced.

Measured 2026-10-06 (HEAD d0ecc27). ``AuditLog._insert_record`` issues
``INSERT OR IGNORE INTO audit``. ``OR IGNORE`` absorbs the very constraint violation that the
``except sqlite3.IntegrityError: pass`` beneath it names, so a second record whose
``entry_id`` is already in the table produces **no row** and **no exception**. Measured:

* ``cursor.rowcount`` is the detector — ``1`` for an inserted row, **``0``** when the INSERT
  was ignored. ``lastrowid`` does *not* discriminate: it keeps its previous value;
* the handler never fires for that case, so it is *dead* while ``OR IGNORE`` stands and
  becomes live the moment someone writes a plain ``INSERT`` — measured with a line tracer,
  with a plain ``INSERT`` into the same-shaped table as the control that the exception is real;
* ``append`` adds to ``self._entries`` **unconditionally**, so the in-memory reader
  ``list_recent()`` keeps reporting the dropped record while the database readers
  ``count()`` / ``read_all()`` deny it — two readers of the same audit log disagree. That
  asymmetry is **still present**; this pin records it, it does not fix it.

**Changed 2026-10-06 (cycle 61, ``DELEGATION.md`` section 4 item 52 branch ②,
owner-selected).** The drop used to be silent and is now announced with ``logger.warning``
naming the ``entry_id``. ``OR IGNORE`` is deliberately kept, so the row is still dropped and
the two readers still disagree — branch ③ (align the memory reader) was *not* taken.

This pin was written to catch exactly this change: its assertion message already read "the
dropped record is now announced; the silence this pin records is gone", and this file is that
branch. It fails in both directions — restoring the silence reddens the announcement
assertion, and dropping ``OR IGNORE`` reddens the "handler never runs" case.

The route is reachable from outside the process: the gRPC ``WriteAuditLog``
(``grpc_server.py:402``) passes the **client-supplied** ``record_id`` straight into
``entry_id`` and returns ``code=0 "ok"`` either way (measured: two calls with the same
``record_id`` both return ok, and the table gains exactly one row).
"""

from __future__ import annotations

import ast
import logging
import sqlite3
import sys
import types
from pathlib import Path

from aegis_ai.audit.audit_log import AuditEntry, AuditLog

_LOGGER = "aegis_ai.audit.audit_log"


def _warnings(caplog) -> list[logging.LogRecord]:
    return [
        r for r in caplog.records if r.name == _LOGGER and r.levelno >= logging.WARNING
    ]


def _log(tmp_path: Path) -> AuditLog:
    return AuditLog(path=str(tmp_path / "audit.jsonl"))


def _entry(action: str, entry_id: str) -> AuditEntry:
    return AuditEntry(action=action, entry_id=entry_id, reason=action)


# --------------------------------------------------- the drop, now announced
def test_a_duplicate_entry_id_is_dropped_from_the_table_but_announced(tmp_path, caplog) -> None:
    """The finding, as of cycle 61: the record is gone from the table — and something says so."""
    log = _log(tmp_path)

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        log.append(_entry("capability.run", "dup"))
        log.append(_entry("egress.send", "dup"))

    assert log.count() == 1, "the duplicate was no longer dropped — re-measure and re-record"
    warnings = _warnings(caplog)
    assert len(warnings) == 1, (
        "the dropped record is silent again; the announcement this pin records is gone: "
        f"{[r.getMessage() for r in warnings]}"
    )
    assert "dup" in warnings[0].getMessage(), (
        f"the announcement does not name the dropped entry_id: {warnings[0].getMessage()!r}"
    )


def test_a_distinct_entry_id_is_kept(tmp_path, caplog) -> None:
    """Control: the *legitimate* case must not warn, and must not lose a row."""
    log = _log(tmp_path)

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        log.append(_entry("capability.run", "one"))
        log.append(_entry("egress.send", "two"))

    assert log.count() == 2
    assert _warnings(caplog) == []


def test_the_warning_detector_is_not_vacuous(caplog) -> None:
    """Non-vacuity control: ``_warnings`` can see a record when one exists."""
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        logging.getLogger(_LOGGER).warning("control record")
    assert len(_warnings(caplog)) == 1, "the warning detector is blind; the two cases above prove nothing"


# ------------------------------------------------- the handler is dead while OR IGNORE stands


def _insert_site() -> tuple[int, int]:
    """``(execute_line, handler_body_line)`` of the ``except sqlite3.IntegrityError`` try."""
    import aegis_ai.audit.audit_log as module

    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        for handler in node.handlers:
            if handler.type is not None and ast.unparse(handler.type) == "sqlite3.IntegrityError":
                return node.body[0].lineno, handler.body[0].lineno
    raise AssertionError("no `except sqlite3.IntegrityError` handler found — re-measure")


def _executed_lines(during) -> set[int]:
    """Line numbers executed inside ``audit_log.py`` while ``during()`` runs."""
    import aegis_ai.audit.audit_log as module

    target = str(module.__file__)
    seen: set[int] = set()

    def tracer(frame, event, _arg):
        if frame.f_code.co_filename != target:
            return None
        if event == "line":
            seen.add(frame.f_lineno)
        return tracer

    sys.settrace(tracer)
    try:
        during()
    finally:
        sys.settrace(None)
    return seen


def test_the_integrity_error_handler_never_runs(tmp_path) -> None:
    """Measured with a line tracer — the only instrument that separates the two worlds.

    "``append`` did not raise" is satisfied both by ``OR IGNORE`` absorbing the violation
    *and* by the swallowing handler eating it; the surviving M1 mutant proves the weaker
    assertion cannot tell them apart. This one can.
    """
    log = _log(tmp_path)
    log.append(_entry("capability.run", "dup"))
    execute_line, handler_line = _insert_site()

    executed = _executed_lines(lambda: log.append(_entry("egress.send", "dup")))

    assert execute_line in executed, (
        "the tracer never saw the INSERT run; it is not measuring this call"
    )
    assert handler_line not in executed, (
        "the `except sqlite3.IntegrityError` handler now runs on a duplicate key: "
        "`INSERT OR IGNORE` no longer absorbs the violation, so the silent drop is one "
        "edit away from turning into a visible failure"
    )


def test_a_plain_insert_does_raise_integrity_error(tmp_path) -> None:
    """Control for the above: the exception exists and the instrument can see it.

    Without this, ``raised is None`` would also hold if ``sqlite3`` simply never raised —
    the control shows the same shape of table *does* raise on a duplicate key.
    """
    conn = sqlite3.connect(str(tmp_path / "plain.db"))
    try:
        conn.execute("CREATE TABLE t (entry_id TEXT UNIQUE NOT NULL, action TEXT)")
        conn.execute("INSERT INTO t VALUES ('dup', 'a')")
        try:
            conn.execute("INSERT INTO t VALUES ('dup', 'b')")
        except sqlite3.IntegrityError as exc:
            assert "UNIQUE constraint failed" in str(exc), exc
        else:  # pragma: no cover - only reached if sqlite stops enforcing UNIQUE
            raise AssertionError("a plain INSERT no longer raises on a duplicate key")
    finally:
        conn.close()


# ------------------------------------------------------- the two readers disagree


def test_the_in_memory_reader_keeps_what_the_database_dropped(tmp_path) -> None:
    log = _log(tmp_path)
    log.append(_entry("capability.run", "dup"))
    log.append(_entry("egress.send", "dup"))

    memory = [e.action for e in log.list_recent(50)]
    stored = [r["action"] for r in log.read_all()]

    assert memory == ["capability.run", "egress.send"], memory
    assert stored == ["capability.run"], stored
    assert log.count() == len(stored) == 1
    assert len(memory) != log.count(), (
        "the in-memory list and the database now agree — the divergence this pin records "
        "is gone"
    )


# ------------------------------------------------- the route is reachable from outside


def test_the_grpc_write_route_reports_ok_while_dropping_the_row(tmp_path) -> None:
    """``WriteAuditLog`` takes ``record_id`` from the caller and returns ok either way."""
    from generated.aegis import common_pb2

    from aegis_ai.grpc_server import AegisAIServicer

    log = _log(tmp_path)
    runtime = types.SimpleNamespace(config=types.SimpleNamespace(), audit_log=log)
    servicer = AegisAIServicer(runtime)

    def _record(action: int) -> common_pb2.AuditRecord:
        return common_pb2.AuditRecord(
            record_id="client-supplied-id",
            action=action,
            actor="android",
            capability_id="cap.x",
            detail_json="{}",
            timestamp_ms=1,
        )

    first = servicer.WriteAuditLog(_record(common_pb2.AUDIT_ACTION_POLICY_DECISION), None)
    second = servicer.WriteAuditLog(_record(common_pb2.AUDIT_ACTION_TOOL_DENIED), None)

    assert first.code == 0 and second.code == 0, (first, second)
    assert log.count() == 1, (
        "the second record reached the table; the silent drop this pin records is gone"
    )
    assert len(log.list_recent(50)) == 2, (
        "the in-memory list no longer holds the dropped record — re-measure"
    )
