"""A memory line that cannot be parsed must be *named*, not silently truncated.

``AdvancedMemory._load`` reads three JSONL stores (entities / facts / conversations).
A line it could not parse was dropped with a bare ``except Exception: pass``, so the
store simply came back **short** — and the only other signal, ``get_stats()``, reports
*counts*. A store that failed to parse and a store that was never written therefore
produce the same kind of answer: **a smaller number**, with no way to attribute it.

The asymmetry is *inside one class*: the same class already warns when its LLM
extraction fails (``logger.warning("LLM extraction failed: %s", e)``), so the silence on
load was not a module-wide convention.

⚠️ **Measurement found a second silent layer, and refuted a first assumption.** The
conversation store does not go through ``_load``'s own loop — it goes through the shared
``aegis_ai.jsonl_tail.read_jsonl_tail``, which swallowed a malformed line *itself*
(``except Exception: continue``, no count, no log). So counting drops in ``_load`` alone
left the conversation path un-reported: the first version of this pin failed on exactly
that case. The helper now reports its own drops, and the whole-read failure it used to
swallow at **DEBUG** — returning ``[]``, which is indistinguishable from "no records in
the window" — is reported too.

This matters more than a display bug: the store is the agent's picture of the user, so a
dropped fact is indistinguishable from a fact never recorded.

Measured 2026-10-04 by driving the classes, not by reading them.
"""

from __future__ import annotations

import contextlib
import json
import logging
from pathlib import Path

import pytest

from aegis_ai.jsonl_tail import read_jsonl_tail
from aegis_ai.memory.advanced import AdvancedMemory

_ADVANCED = "aegis_ai.memory.advanced"
_TAIL = "aegis_ai.jsonl_tail"
_LOGGERS = (_ADVANCED, _TAIL)


def _write(data_dir: Path, name: str, lines: list[str]) -> Path:
    path = data_dir / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _entity(eid: str) -> str:
    return json.dumps({"entity_id": eid, "name": eid.upper()})


def _fact(fid: str) -> str:
    return json.dumps({"fact_id": fid, "content": f"fact {fid}"})


def _conv(cid: str) -> str:
    return json.dumps({"entry_id": cid, "user_msg": "hi", "bot_msg": "hello"})


def _load(data_dir: Path, caplog, level: int = logging.WARNING) -> AdvancedMemory:
    with contextlib.ExitStack() as stack:
        for name in _LOGGERS:
            stack.enter_context(caplog.at_level(level, logger=name))
        return AdvancedMemory(data_dir=str(data_dir))


def _warnings(caplog) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name in _LOGGERS and r.levelno == logging.WARNING]


def _messages(caplog) -> list[str]:
    return [r.getMessage() for r in _warnings(caplog)]


# ---------------------------------------------------------------------------------------
# Control first: a clean store loads fully and says nothing.
# ---------------------------------------------------------------------------------------


def test_a_clean_store_loads_fully_and_stays_silent(tmp_path, caplog) -> None:
    data_dir = tmp_path / "memory"
    data_dir.mkdir()
    _write(data_dir, "entities.jsonl", [_entity("e1"), _entity("e2")])
    _write(data_dir, "facts.jsonl", [_fact("f1")])
    _write(data_dir, "conversations.jsonl", [_conv("c1")])

    memory = _load(data_dir, caplog)

    assert _messages(caplog) == []
    assert memory.get_stats() == {
        "entities": 2,
        "facts": 1,
        "conversations": 1,
        "valid_facts": 1,
    }


def test_missing_stores_stay_silent(tmp_path, caplog) -> None:
    # Non-vacuity control: if "absent" also warned, a fresh install would log on every
    # start and the real warning would drown.
    data_dir = tmp_path / "memory"
    data_dir.mkdir()

    memory = _load(data_dir, caplog)

    assert _messages(caplog) == []
    assert memory.get_stats()["entities"] == 0


# ---------------------------------------------------------------------------------------
# A dropped line is named — and the resulting shortfall is measured.
# ---------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "good", "key"),
    [
        ("entities.jsonl", _entity, "entities"),
        ("facts.jsonl", _fact, "facts"),
        ("conversations.jsonl", _conv, "conversations"),
    ],
)
def test_a_corrupt_line_is_reported_with_its_file(tmp_path, caplog, name, good, key) -> None:
    data_dir = tmp_path / "memory"
    data_dir.mkdir()
    path = _write(data_dir, name, [good("ok"), "{ not json"])

    memory = _load(data_dir, caplog)

    warnings = _messages(caplog)
    assert len(warnings) == 1, warnings
    assert str(path) in warnings[0], warnings[0]
    assert "1" in warnings[0], warnings[0]
    # The good line still loads — naming the failure must not turn a skip into a stop.
    assert memory.get_stats()[key] == 1


def test_the_corrupt_line_shrinks_the_count_it_would_have_contributed_to(tmp_path, caplog) -> None:
    # The whole point: the only observable is a *smaller number*, which is exactly what a
    # store that was never written looks like. Measured both ways in one test.
    good_dir = tmp_path / "good"
    good_dir.mkdir()
    _write(good_dir, "entities.jsonl", [_entity("e1"), _entity("e2")])
    bad_dir = tmp_path / "bad"
    bad_dir.mkdir()
    _write(bad_dir, "entities.jsonl", [_entity("e1"), _entity("e2"), "{ not json"])

    good = _load(good_dir, caplog)
    assert good.get_stats()["entities"] == 2
    assert _messages(caplog) == []

    caplog.clear()
    bad = _load(bad_dir, caplog)

    assert bad.get_stats()["entities"] == 2  # same count…
    assert len(_messages(caplog)) == 1  # …but now attributable


def test_many_bad_lines_produce_one_warning_with_the_count(tmp_path, caplog) -> None:
    # Per-line warnings would flood the log on a badly corrupted file; the count is the
    # information that matters.
    data_dir = tmp_path / "memory"
    data_dir.mkdir()
    _write(data_dir, "facts.jsonl", [_fact("f1"), "{bad", "{bad", "{bad"])

    memory = _load(data_dir, caplog)

    warnings = _messages(caplog)
    assert len(warnings) == 1, warnings
    assert "3" in warnings[0], warnings[0]
    assert memory.get_stats()["facts"] == 1


def test_each_store_reports_separately(tmp_path, caplog) -> None:
    # One corrupt store must not mask another; the counts are per file.
    data_dir = tmp_path / "memory"
    data_dir.mkdir()
    _write(data_dir, "entities.jsonl", [_entity("e1"), "{bad"])
    _write(data_dir, "facts.jsonl", [_fact("f1"), "{bad", "{bad"])

    _load(data_dir, caplog)

    warnings = _messages(caplog)
    assert len(warnings) == 2, warnings
    joined = " || ".join(warnings)
    assert "entities.jsonl" in joined, joined
    assert "facts.jsonl" in joined, joined


# ---------------------------------------------------------------------------------------
# The conversation path is a *second* layer — the tail reader reports it, not ``_load``.
# ---------------------------------------------------------------------------------------


def test_the_conversation_window_is_reported_by_the_tail_reader(tmp_path, caplog) -> None:
    # Guards the finding: counting drops in ``_load`` alone does NOT cover conversations,
    # because ``read_jsonl_tail`` consumed the malformed line before ``_load`` saw it.
    data_dir = tmp_path / "memory"
    data_dir.mkdir()
    _write(data_dir, "conversations.jsonl", [_conv("c1"), "{ not json"])

    memory = _load(data_dir, caplog)

    assert memory.get_stats()["conversations"] == 1
    records = _warnings(caplog)
    assert len(records) == 1, _messages(caplog)
    assert records[0].name == _TAIL, records[0].name


# ---------------------------------------------------------------------------------------
# ``read_jsonl_tail`` directly: its two absences.
# ---------------------------------------------------------------------------------------


def test_the_tail_reader_reports_a_malformed_line(tmp_path, caplog) -> None:
    path = _write(tmp_path, "rows.jsonl", ['{"a": 1}', "{ not json", '{"b": 2}'])

    with caplog.at_level(logging.WARNING, logger=_TAIL):
        rows = read_jsonl_tail(path, 10)

    # The good rows still come back…
    assert rows == [{"a": 1}, {"b": 2}]
    # …and the drop is named, not silent.
    assert len(_messages(caplog)) == 1, _messages(caplog)
    assert "rows.jsonl" in _messages(caplog)[0]


def test_a_failed_tail_read_is_not_reported_as_an_empty_file(tmp_path, caplog) -> None:
    # A *directory* exists and has a size, but cannot be opened — the outer handler. It
    # used to log at DEBUG and return [], which is exactly what an empty window returns.
    target = tmp_path / "not_a_file"
    target.mkdir()

    with caplog.at_level(logging.WARNING, logger=_TAIL):
        rows = read_jsonl_tail(target, 10)

    assert rows == []
    records = _warnings(caplog)
    assert len(records) == 1, _messages(caplog)
    assert "empty window" in records[0].getMessage(), records[0].getMessage()


def test_a_missing_file_is_still_silent(tmp_path, caplog) -> None:
    # Control for the above: "no file" is a legitimate empty and must not warn.
    with caplog.at_level(logging.WARNING, logger=_TAIL):
        rows = read_jsonl_tail(tmp_path / "absent.jsonl", 10)

    assert rows == []
    assert _messages(caplog) == []


# ---------------------------------------------------------------------------------------
# ``_load``'s own fallback branch is not a loss, so it must not warn.
# ---------------------------------------------------------------------------------------


def test_the_tail_reader_fallback_does_not_warn(tmp_path, caplog, monkeypatch) -> None:
    # NOTE: the *real* ``read_jsonl_tail`` returns [] instead of raising, so this branch
    # guards an import error or an unexpected raise — it is exercised here by making the
    # reader raise. Taking the branch drops nothing, so a WARNING would be a false alarm.
    import aegis_ai.jsonl_tail as jsonl_tail

    data_dir = tmp_path / "memory"
    data_dir.mkdir()
    _write(data_dir, "conversations.jsonl", [_conv("c1"), _conv("c2")])

    def _boom(*_args, **_kwargs):
        raise RuntimeError("tail reader unavailable")

    monkeypatch.setattr(jsonl_tail, "read_jsonl_tail", _boom)

    with caplog.at_level(logging.DEBUG, logger=_ADVANCED):
        memory = AdvancedMemory(data_dir=str(data_dir))

    # The fallback recovered the data…
    assert memory.get_stats()["conversations"] == 2
    # …so nothing is reported as lost…
    assert _messages(caplog) == []
    # …and the fallback itself is still traceable.
    assert any("Falling back" in r.getMessage() for r in caplog.records if r.name == _ADVANCED)
