"""Cycle 144 pin: the 29-key ``record`` that ``AuditLog.append`` hands to
``_insert_record`` must reach every SQLite column -- and a renamed field must be
*seen*, not silently defaulted.

Measured 2026-10-10 (cycle 144, HEAD ``f2111c9``).  ``AuditLog.append`` builds a
dict literal named ``record`` (``audit_log.py:310``) with **29** keys and passes it
to ``_insert_record`` (``audit_log.py:245``).  ``_insert_record`` reads every one of
those 29 keys through ``record.get(key, default)`` and binds them to the 29
non-``id`` columns of the ``audit`` table (``_CREATE_TABLE``, ``audit_log.py:125``).
The census (``census_writer_reader_contracts.py``) reports this site at **29/29** --
the highest coverage of any writer/reader pair in the tree.

The contract is therefore a three-way equality::

    writer keys  ==  reader keys  ==  schema columns \\ {id}

with one deliberate name bridge: the writer key ``detail`` becomes the column
``detail_json`` (``_insert_record`` reads ``record.get('detail', {})`` and
``json.dumps``es it).  The bridge is the only place the two names differ.

**Why this is worth a pin.**  The reader is key-name-driven and *silent*: every read
is ``.get(key, default)``, so a writer-side rename does not raise -- the column is
written with the reader's default and the audit trail quietly loses a field.  A
fixture that leaves the entry at its defaults **cannot see this**, because the
silent default (``''`` / ``0`` / ``0.0`` / ``{}``) equals the expected value.  So
the core test populates **every** field with a value distinct from its default and
asserts the exact round-trip through the real database
(``append`` -> ``_insert_record`` -> SQLite -> ``read_all`` / ``_row_to_dict``).

**Two writers, one reader.**  ``_insert_record`` has two callers: ``append`` (the
live writer) and ``_migrate_jsonl_if_needed`` (``audit_log.py:218``), which feeds it
records parsed from the legacy JSONL.  Both must supply the same 29 keys; the pin
records that census rather than assuming ``append`` is the only writer.

The pin does not change behaviour -- it records the contract and the silent failure
it guards.  ``DELEGATION.md`` section 4 item 104.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any

from aegis_ai.audit.audit_log import AuditEntry, AuditLog

#: The 29 keys ``append`` must emit and ``_insert_record`` must request.
_RECORD_KEYS = frozenset(
    {
        "entry_id",
        "timestamp_ms",
        "action",
        "actor",
        "capability_id",
        "decision",
        "reason",
        "detail",
        "profile_id",
        "prompt_id",
        "prompt_version",
        "prompt_hash",
        "model",
        "max_tokens",
        "temperature",
        "reasoning_level",
        "provider",
        "tokens_used",
        "duration_ms",
        "approval_id",
        "approval_channel",
        "approval_user",
        "request_id",
        "task_id",
        "source_desire",
        "risk_level",
        "audit_group_id",
        "audit_group_type",
        "audit_group_title",
    }
)

#: The single writer-key -> column-name bridge.
_DETAIL_KEY = "detail"
_DETAIL_COLUMN = "detail_json"

#: The one column the record never carries (the AUTOINCREMENT primary key).
_ID_COLUMN = "id"

#: The two known callers of ``_insert_record``.
_READER_CALLERS = frozenset({"append", "_migrate_jsonl_if_needed"})

#: What ``_insert_record`` writes for a record that is **missing every key**.
#: ``append`` always emits all 29 keys, so these per-key defaults are unreachable
#: through it -- they are only reached by the legacy JSONL migration, which feeds
#: ``_insert_record`` whatever the old format happened to carry.  ``risk_level`` is
#: security-relevant, so the default must be pinned, not assumed.
_DEFAULT_ROW: dict[str, Any] = {
    "entry_id": "",
    "timestamp_ms": 0,
    "action": "",
    "actor": "",
    "capability_id": "",
    "decision": "",
    "reason": "",
    "detail": {},
    "profile_id": "",
    "prompt_id": "",
    "prompt_version": "",
    "prompt_hash": "",
    "model": "",
    "max_tokens": 0,
    "temperature": 0.0,
    "reasoning_level": "",
    "provider": "",
    "tokens_used": 0,
    "duration_ms": 0,
    "approval_id": "",
    "approval_channel": "",
    "approval_user": "",
    "request_id": "",
    "task_id": "",
    "source_desire": "",
    "risk_level": "",
    "audit_group_id": "",
    "audit_group_type": "",
    "audit_group_title": "",
}


def _log(tmp_path: Path) -> AuditLog:
    return AuditLog(path=str(tmp_path / "audit.jsonl"))


def _full_entry() -> AuditEntry:
    """An ``AuditEntry`` whose every field differs from its dataclass default.

    The distinctness is load-bearing (see the control test): a fixture that left a
    field at its default could not tell a rename from an untouched field.
    """
    return AuditEntry(
        timestamp_ms=1_700_000_000_123,
        action="act_full",
        actor="actor_full",
        capability_id="cap_full",
        decision="dec_full",
        reason="reason_full",
        detail={"k_detail": "v_detail", "n": 7},
        entry_id="entry_full",
        profile_id="profile_full",
        prompt_id="prompt_full",
        prompt_version="v9",
        prompt_hash="hash_full",
        model="model_full",
        max_tokens=1234,
        temperature=0.75,
        reasoning_level="reasoning_full",
        provider="provider_full",
        tokens_used=4321,
        duration_ms=567,
        approval_id="approval_full",
        approval_channel="channel_full",
        approval_user="user_full",
        request_id="request_full",
        task_id="task_full",
        source_desire="desire_full",
        risk_level="risk_full",
        audit_group_id="group_full",
        audit_group_type="group_type_full",
        audit_group_title="group_title_full",
    )


def _sent_fields(entry: AuditEntry) -> dict[str, Any]:
    """The 29 ``record`` keys mapped to the value ``entry`` carries for each."""
    return {key: getattr(entry, key) for key in _RECORD_KEYS}


def _default_fields() -> dict[str, Any]:
    return _sent_fields(AuditEntry())


def _append_record_keys() -> set[str]:
    """Keys of the ``record`` dict literal inside ``AuditLog.append``."""
    src = inspect.getsource(AuditLog.append)
    tree = ast.parse(_dedent(src))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "record":
                    assert isinstance(node.value, ast.Dict), "record is no longer a dict literal"
                    return {
                        key.value
                        for key in node.value.keys
                        if isinstance(key, ast.Constant) and isinstance(key.value, str)
                    }
    raise AssertionError("no `record = {...}` assignment found in AuditLog.append")


def _insert_record_requested_keys() -> set[str]:
    """Keys ``_insert_record`` requests from ``record`` via ``record.get(key, ...)``."""
    src = inspect.getsource(AuditLog._insert_record)
    tree = ast.parse(_dedent(src))
    keys: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "record"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            keys.add(node.args[0].value)
    return keys


def _insert_record_callers() -> set[str]:
    """Names of every method that calls ``self._insert_record(...)``."""
    src = inspect.getsource(AuditLog)
    tree = ast.parse(_dedent(src))
    callers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for inner in ast.walk(node):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "_insert_record"
                ):
                    callers.add(node.name)
    return callers


def _schema_columns(log: AuditLog) -> set[str]:
    conn = log._get_conn()
    try:
        return {row[1] for row in conn.execute("PRAGMA table_info(audit)").fetchall()}
    finally:
        log.close()


def _dedent(src: str) -> str:
    import textwrap

    return textwrap.dedent(src)


# --------------------------------------------------------------------------- #
# static: writer, reader, and the reader's callers
# --------------------------------------------------------------------------- #


def test_the_writer_emits_exactly_the_declared_key_set() -> None:
    assert _append_record_keys() == set(_RECORD_KEYS)


def test_the_reader_requests_exactly_the_declared_key_set() -> None:
    assert _insert_record_requested_keys() == set(_RECORD_KEYS)


def test_the_reader_has_exactly_the_two_known_writers() -> None:
    assert _insert_record_callers() == set(_READER_CALLERS)


# --------------------------------------------------------------------------- #
# the schema agrees with the record, modulo the id column and the detail bridge
# --------------------------------------------------------------------------- #


def test_the_schema_columns_are_the_record_keys_plus_the_id_column(tmp_path: Path) -> None:
    log = _log(tmp_path)
    columns = _schema_columns(log)
    expected = (set(_RECORD_KEYS) - {_DETAIL_KEY}) | {_DETAIL_COLUMN, _ID_COLUMN}
    assert columns == expected


# --------------------------------------------------------------------------- #
# the core pin: every field round-trips through the real database
# --------------------------------------------------------------------------- #


def test_every_field_round_trips_through_the_database(tmp_path: Path) -> None:
    log = _log(tmp_path)
    entry = _full_entry()
    log.append(entry)

    rows = log.read_all()
    assert len(rows) == 1, "append produced no row"
    row = rows[0]

    sent = _sent_fields(entry)
    # The record key `detail` is the column `detail_json`; on read it comes back
    # as `detail` again (see _row_to_dict).
    assert set(row) == set(_RECORD_KEYS), "the read row is not the record key set"
    for key, value in sent.items():
        assert row[key] == value, f"field {key!r} did not round-trip"


def test_the_detail_bridge_is_load_bearing(tmp_path: Path) -> None:
    """`record['detail']` -> column `detail_json` -> `row['detail']`."""
    log = _log(tmp_path)
    entry = AuditEntry(action="a", detail={"sentinel": "kept", "n": 3})
    log.append(entry)

    row = log.read_all()[0]
    assert row[_DETAIL_KEY] == {"sentinel": "kept", "n": 3}
    assert _DETAIL_COLUMN not in row, "the raw column name leaked into the read row"


def test_the_defaults_round_trip_when_a_field_is_unset(tmp_path: Path) -> None:
    """An untouched entry stores the declared defaults, not None."""
    log = _log(tmp_path)
    log.append(AuditEntry(entry_id="e1"))

    row = log.read_all()[0]
    defaults = _default_fields()
    for key in _RECORD_KEYS - {"entry_id", "timestamp_ms"}:
        assert row[key] == defaults[key], f"default for {key!r} changed"
    assert row["entry_id"] == "e1"
    assert isinstance(row["timestamp_ms"], int) and row["timestamp_ms"] > 0


def test_the_reader_defaults_are_pinned_when_a_key_is_absent(tmp_path: Path) -> None:
    """A record missing a key falls back to the *declared* default, not an arbitrary one.

    This is the only route that reaches ``_insert_record``'s per-key defaults: the live
    writer ``append`` always supplies all 29 keys, so the defaults are exercised solely by
    the legacy JSONL migration.  A changed default (e.g. ``risk_level`` -> ``"high"``)
    would silently mislabel every legacy row.
    """
    assert set(_DEFAULT_ROW) == set(_RECORD_KEYS), "the default row is not the record key set"
    log = _log(tmp_path)
    conn = log._get_conn()
    log._insert_record(conn, {})  # a legacy record missing every key
    conn.commit()
    log.close()

    row = log.read_all()[0]
    assert row == _DEFAULT_ROW


# --------------------------------------------------------------------------- #
# controls: the fixture is sensitive, and the failure mode is real
# --------------------------------------------------------------------------- #


def test_the_control_the_fixture_values_are_distinct_from_the_defaults() -> None:
    """Guard against "fixing" a red round-trip by using default-valued fields.

    If a field in `_full_entry` equalled its default, the round-trip assertion for
    that field could pass even when the writer silently dropped it -- the silent
    default would masquerade as the sent value.
    """
    sent = _sent_fields(_full_entry())
    defaults = _default_fields()
    for key, value in sent.items():
        assert value != defaults[key], f"fixture value for {key!r} equals its default"


def test_the_control_a_renamed_field_silently_defaults(tmp_path: Path) -> None:
    """Driving `_insert_record` with a renamed key shows the failure is silent.

    This is the mechanism the round-trip test guards: rename a record key and the
    reader's `.get(..., default)` writes the default with no exception.
    """
    log = _log(tmp_path)
    entry = _full_entry()
    record = _sent_fields(entry)
    record.pop("audit_group_title")
    record["group_title"] = entry.audit_group_title  # the rename a refactor would make

    conn = log._get_conn()
    log._insert_record(conn, record)
    conn.commit()
    log.close()

    row = log.read_all()[0]
    assert row["audit_group_title"] == "", "the rename was not silently defaulted"
    assert "group_title" not in row, "the renamed key leaked into the row"


def test_the_control_an_undeclared_key_is_ignored(tmp_path: Path) -> None:
    """The reader is key-name-driven: an extra key reaches no column."""
    log = _log(tmp_path)
    record = _sent_fields(_full_entry())
    record["totally_undeclared"] = "ignored"

    conn = log._get_conn()
    log._insert_record(conn, record)
    conn.commit()
    log.close()

    row = log.read_all()[0]
    assert "totally_undeclared" not in row
    assert set(row) == set(_RECORD_KEYS)
