"""The operation timeline's silent read failures must announce themselves.

`ui_overview._operations` merges three sources and each one is wrapped in a handler
that yields an *absence* on failure.  Two of those absences are legitimate (nothing
has been recorded yet); the rest are failures wearing the same costume, and because
the audit-group and autonomous-cycle fallbacks still render, the timeline shows a
plausible result either way.  `OperationStore._load` has the same shape one layer
down: an unreadable file leaves an empty cache, and a dropped line is simply not
there.

Each test below pins one announcement.  The controls pin the other half — a
legitimately absent source (no loop, no log file, no store, no records) must stay
**silent**, or the warnings are noise and the assertions are vacuous.

Recorded but deliberately *not* fixed here (see `DELEGATION.md` §4): a single
unparsable line in `execution_log.jsonl` discards the whole cycle history rather
than that one line.  `test_one_corrupt_line_discards_the_whole_cycle_history`
pins the current behaviour so that changing it has to be deliberate.
"""

from __future__ import annotations

import json
import logging

from aegis_ai.operations import OperationStore
from aegis_ai.operations.store import OperationRecord
from aegis_ai.web.ui_overview import _autonomous_logs, _operations

_STORE_LOGGER = "aegis_ai.operations.store"
_UI_LOGGER = "aegis_ai.web.ui_overview"


class _Runtime:
    """Stand-in exposing only the attributes the functions under test read."""

    def __init__(self, **attrs: object) -> None:
        self.__dict__.update(attrs)


class _RaisingStore:
    def list_recent(self, *, limit: int = 50):
        raise OSError("disk detached")


class _RaisingAudit:
    def list_groups(self, **kwargs: object):
        raise RuntimeError("audit index corrupt")


def _warnings(caplog, logger_name: str) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == logger_name and r.levelno >= logging.WARNING]


def _messages(caplog, logger_name: str) -> str:
    return " ".join(r.getMessage() for r in _warnings(caplog, logger_name))


def _cycle_entry(timestamp_ms: int, decision: str) -> str:
    return json.dumps(
        {
            "timestamp_ms": timestamp_ms,
            "last_decision": decision,
            "tasks": [],
            "results": [],
        }
    )


# --------------------------------------------------------------------------- #
# OperationStore._load — one layer down from the timeline
# --------------------------------------------------------------------------- #


def test_an_unreadable_store_file_is_named(tmp_path, caplog) -> None:
    """A file that cannot be read leaves an empty cache — say so."""
    operations_dir = tmp_path / "operations"
    operations_dir.mkdir()
    # A directory where the store expects a file: opening it raises OSError
    # (IsADirectoryError on POSIX, PermissionError on Windows).
    (operations_dir / "operations.jsonl").mkdir()

    with caplog.at_level(logging.WARNING, logger=_STORE_LOGGER):
        store = OperationStore(data_dir=tmp_path)

    assert store.list_recent(limit=10) == []
    assert _warnings(caplog, _STORE_LOGGER), (
        "an unreadable store file left the cache empty without a word"
    )
    assert "operations.jsonl" in _messages(caplog, _STORE_LOGGER)


def test_a_missing_store_file_stays_silent(tmp_path, caplog) -> None:
    """Control: the ordinary first-run case is not a failure and must not warn."""
    with caplog.at_level(logging.WARNING, logger=_STORE_LOGGER):
        store = OperationStore(data_dir=tmp_path)

    assert store.list_recent(limit=10) == []
    assert _warnings(caplog, _STORE_LOGGER) == [], (
        "a store that simply has no file yet was reported as a failure"
    )


def test_dropped_lines_are_counted_and_named(tmp_path, caplog) -> None:
    """A line that cannot be parsed is dropped silently unless it is counted."""
    operations_dir = tmp_path / "operations"
    operations_dir.mkdir()
    kept = [
        OperationRecord(action_summary="kept one"),
        OperationRecord(action_summary="kept two"),
    ]
    (operations_dir / "operations.jsonl").write_text(
        "\n".join([json.dumps(kept[0].to_dict()), "{not json", json.dumps(kept[1].to_dict())])
        + "\n",
        encoding="utf-8",
    )

    with caplog.at_level(logging.WARNING, logger=_STORE_LOGGER):
        store = OperationStore(data_dir=tmp_path)

    assert len(store.list_recent(limit=10)) == 2, "the readable lines should still load"
    message = _messages(caplog, _STORE_LOGGER)
    assert "1" in message, f"the dropped-line count was not reported: {message!r}"
    assert "operations.jsonl" in message


def test_a_fully_readable_store_file_stays_silent(tmp_path, caplog) -> None:
    """Control: the happy path must not emit the dropped-line warning."""
    operations_dir = tmp_path / "operations"
    operations_dir.mkdir()
    (operations_dir / "operations.jsonl").write_text(
        json.dumps(OperationRecord(action_summary="ok").to_dict()) + "\n", encoding="utf-8"
    )

    with caplog.at_level(logging.WARNING, logger=_STORE_LOGGER):
        store = OperationStore(data_dir=tmp_path)

    assert len(store.list_recent(limit=10)) == 1
    assert _warnings(caplog, _STORE_LOGGER) == []


# --------------------------------------------------------------------------- #
# ui_overview._operations — the two fallback sources
# --------------------------------------------------------------------------- #


def test_the_timeline_names_a_store_failure(caplog) -> None:
    runtime = _Runtime(operation_store=_RaisingStore())

    with caplog.at_level(logging.WARNING, logger=_UI_LOGGER):
        ops = _operations(runtime)

    assert ops == []
    assert _warnings(caplog, _UI_LOGGER), (
        "the store failed and the timeline silently degraded to its other sources"
    )
    assert "operation store" in _messages(caplog, _UI_LOGGER)


def test_the_timeline_names_an_audit_failure(caplog) -> None:
    runtime = _Runtime(audit_manager=_RaisingAudit())

    with caplog.at_level(logging.WARNING, logger=_UI_LOGGER):
        _operations(runtime)

    assert "audit groups" in _messages(caplog, _UI_LOGGER), (
        "audit groups failed and the timeline silently omitted them"
    )


def test_the_timeline_stays_silent_when_nothing_is_configured(caplog) -> None:
    """Control: an empty runtime is the ordinary case, not a failure."""
    with caplog.at_level(logging.WARNING, logger=_UI_LOGGER):
        ops = _operations(_Runtime())

    assert ops == []
    assert _warnings(caplog, _UI_LOGGER) == []


def test_the_timeline_stays_silent_on_the_happy_path(tmp_path, caplog) -> None:
    """Control: a working store must not trip either warning."""
    store = OperationStore(data_dir=tmp_path)
    store.upsert(OperationRecord(action_summary="did a thing", result_summary="done"))

    with caplog.at_level(logging.WARNING, logger=_UI_LOGGER):
        ops = _operations(_Runtime(operation_store=store))

    assert ops, "the store had one record and it should appear in the timeline"
    assert _warnings(caplog, _UI_LOGGER) == []


# --------------------------------------------------------------------------- #
# ui_overview._autonomous_logs — the third source
# --------------------------------------------------------------------------- #


def test_autonomous_logs_names_a_corrupt_log(tmp_path, caplog) -> None:
    (tmp_path / "execution_log.jsonl").write_text("{not json\n", encoding="utf-8")
    runtime = _Runtime(autonomous_loop=_Runtime(_data_dir=tmp_path))

    with caplog.at_level(logging.WARNING, logger=_UI_LOGGER):
        result = _autonomous_logs(runtime)

    assert result == {"cycles": [], "count": 0}
    assert "autonomous execution logs" in _messages(caplog, _UI_LOGGER), (
        "an unparsable execution log was reported as 'no cycles yet'"
    )


def test_a_missing_execution_log_stays_silent(tmp_path, caplog) -> None:
    """Control: no cycles have run yet is the ordinary case."""
    runtime = _Runtime(autonomous_loop=_Runtime(_data_dir=tmp_path))

    with caplog.at_level(logging.WARNING, logger=_UI_LOGGER):
        result = _autonomous_logs(runtime)

    assert result == {"cycles": [], "count": 0}
    assert _warnings(caplog, _UI_LOGGER) == []


def test_no_autonomous_loop_stays_silent(caplog) -> None:
    """Control: an unconfigured loop is not a read failure."""
    with caplog.at_level(logging.WARNING, logger=_UI_LOGGER):
        result = _autonomous_logs(_Runtime())

    assert result == {"cycles": [], "count": 0}
    assert _warnings(caplog, _UI_LOGGER) == []


def test_a_readable_execution_log_stays_silent(tmp_path, caplog) -> None:
    """Control: the parse path actually runs, and does not warn when it succeeds."""
    (tmp_path / "execution_log.jsonl").write_text(
        _cycle_entry(1_700_000_000_000, "review") + "\n", encoding="utf-8"
    )
    runtime = _Runtime(autonomous_loop=_Runtime(_data_dir=tmp_path))

    with caplog.at_level(logging.WARNING, logger=_UI_LOGGER):
        result = _autonomous_logs(runtime)

    assert result["count"] == 1
    assert _warnings(caplog, _UI_LOGGER) == []


def test_one_corrupt_line_discards_the_whole_cycle_history(tmp_path) -> None:
    """Documents current behaviour: the parse is not per-line, so one bad line wins.

    Recorded in `DELEGATION.md` §4 rather than fixed here — skipping the bad line
    would change what the timeline shows, which is a behaviour change, not a
    naming one.  This test exists so that fixing it is a deliberate act.
    """
    (tmp_path / "execution_log.jsonl").write_text(
        "\n".join([_cycle_entry(1, "a"), "{not json", _cycle_entry(2, "b")]) + "\n",
        encoding="utf-8",
    )
    runtime = _Runtime(autonomous_loop=_Runtime(_data_dir=tmp_path))

    assert _autonomous_logs(runtime) == {"cycles": [], "count": 0}
