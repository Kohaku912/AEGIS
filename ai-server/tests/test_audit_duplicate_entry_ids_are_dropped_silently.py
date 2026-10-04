"""Cycle 23 pin: a duplicate ``entry_id`` is dropped from the audit sink in silence.

Measured 2026-10-05 (HEAD c0e1d8c). ``AuditLog._insert_record`` (``audit/audit_log.py:245``)
issues ``INSERT OR IGNORE INTO audit``. ``OR IGNORE`` already absorbs the very constraint
violation that the ``except sqlite3.IntegrityError: pass`` beneath it names, so:

* a second record whose ``entry_id`` is already in the table produces **no row**, **no
  exception** and **no log line** — the audit trail simply holds one fewer record than was
  submitted (measured: ``count() == 1`` after two appends of the same id);
* the handler at ``:288`` therefore never fires for that case. Asserting only "``append``
  does not raise" would **not** establish this: a plain ``INSERT`` with the swallowing
  handler still present looks identical from the outside (that mutant survives every other
  case in this file). The handler's execution is therefore measured directly with a line
  tracer, and a plain ``INSERT`` into the same-shaped table is used as the control that the
  exception itself is real;
* ``append`` (``:316``) adds to ``self._entries`` **unconditionally**, so the in-memory
  reader ``list_recent()`` keeps reporting the dropped record while the database readers
  ``count()`` / ``read_all()`` deny it — two readers of the same audit log disagree.

The route is reachable from outside the process: the gRPC ``WriteAuditLog``
(``grpc_server.py:402``) passes the **client-supplied** ``record_id`` straight into
``entry_id`` and returns ``code=0 "ok"`` either way (measured: two calls with the same
``record_id`` both return ok, and the table gains exactly one row).

Behaviour is **not** changed here — whether the second record should be rejected, merged or
announced is an owner decision (``DELEGATION.md`` §4 item 52). This pin fixes the current
state so that changing it is deliberate. Note the asymmetry: the ``except`` clause is dead
*while* ``OR IGNORE`` stands, and becomes live the moment someone writes a plain ``INSERT``
— which is exactly the change this pin will catch.
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


# --------------------------------------------------------------- the silent drop


def test_a_duplicate_entry_id_leaves_no_row_and_no_record(tmp_path, caplog) -> None:
    """The finding: the record is gone and nothing anywhere says so."""
    log = _log(tmp_path)

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        log.append(_entry("capability.run", "dup"))
        log.append(_entry("egress.send", "dup"))

    assert log.count() == 1, "the duplicate was no longer dropped — re-measure and re-record"
    assert _warnings(caplog) == [], (
        "the dropped record is now announced; the silence this pin records is gone: "
        f"{[r.getMessage() for r in _warnings(caplog)]}"
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
