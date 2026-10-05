"""Cycles 58-59 pin: a swallow is named only where the handler can actually run, and the
readers that drop one corrupt line say so.

Cycle 58 -- reachability is the criterion
-----------------------------------------
Cycle 17 established it for `context_builder.py`: the composition root wires 7 of the ~20
backends the builder accepts, so a handler behind `if self._backend:` cannot run and naming it
would add a record to code that cannot run. Cycle 58 started from the *consequence* instead
("a failed section build silently omits a line from the LLM's context"), named **ten** such
handlers, and then measured the premise: **nine of the ten were unreachable**:

  * `context_builder.py` (5) -- behind `if self._user_state_manager:` and friends, none of which
    `runtime.py` passes. The section is omitted by the *guard*, not the handler.
  * `briefing/provider.py` (3) -- `DailyBriefingProvider` has no producer anywhere in `src/`.
  * `llm_task_interpreter.py` (1) -- the registry fallback: `capability_registry` defaults to
    `None` and the root never passes it.

Only the interpreter's *catalog* fallback is reachable, and it is the one that stays named.
A record that cannot fire does not make a failure louder -- it only *lowers the census*.

Cycle 59 -- the line-skip readers
---------------------------------
The unit here is cycle 51's: `continue` in a loop body *is* the handler that fires for the
realistic corruption (a process killed mid-append leaves a truncated final line). Five more
reachable sites of that shape now name what they skipped:

  * `journal/journal_store.py` -- `_load_last_sequence` and `list_recent`.
  * `user_state/manager.py` -- `TimelineStore.query_recent` and `ArchiveManager.list_archives`.
  * `web/chat_history.py` -- `ChatHistoryStore.load` (the module had **no logger**; one was added).

Each is reachable because its producer exists: `runtime.py` builds the `JournalStore` and the
`UserStateManager`, and `web/routes/chat.py` calls `ChatHistoryStore(...).load()`. That is
pinned below, so if a producer disappears the record becomes dead and must be re-adjudicated.

Cycle 59 also corrected this pin's own census equation: it read `named + excluded + backlog`,
which is *numerically* self-consistent only if the backlog is understated by the number of named
sites. The census counts **bare** handlers, so the decomposition is `bare == excluded + backlog`.
"""
from __future__ import annotations

import ast
import logging
from pathlib import Path

import pytest

from aegis_ai.journal.journal_store import JournalStore
from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
from aegis_ai.user_state.manager import ArchiveManager, TimelineStore
from aegis_ai.web.chat_history import ChatHistoryStore

_AI_SERVER = Path(__file__).resolve().parents[1]
_SRC = _AI_SERVER / "src"
_RUNTIME = _SRC / "aegis_ai" / "runtime.py"

_LOGGER = "aegis_ai.llm_task_interpreter"
_FAMILY_TYPE = "Exception"

# relpath -> a phrase only that site's record contains (one phrase per named site).
_NAMED: dict[str, list[str]] = {
    "aegis_ai/llm_task_interpreter.py": ["Could not list capabilities from the catalog"],
    "aegis_ai/journal/journal_store.py": [
        "Skipped a journal line that would not parse while reading the last sequence",
        "Skipped a journal line that would not parse; it is missing from the result",
    ],
    "aegis_ai/user_state/manager.py": [
        "Skipped a user-state event that would not parse; it is missing from the recent list",
        "Skipped an archive index line that would not parse; the archive is missing from the list",
    ],
    "aegis_ai/web/chat_history.py": [
        "Skipped a chat-history line that would not parse; it is missing from the history",
    ],
}

# relpath -> (bare handlers still expected, why they are *not* named).
_EXCLUDED: dict[str, tuple[int, str]] = {
    "aegis_ai/context_builder.py": (
        5,
        "the five section builders sit behind `if self._backend:` and the composition root wires "
        "none of those backends (cycle 17's measurement, re-pinned below)",
    ),
    "aegis_ai/briefing/provider.py": (
        3,
        "DailyBriefingProvider has no producer anywhere in src/ -- a dead class's handlers cannot run",
    ),
    "aegis_ai/llm_task_interpreter.py": (
        1,
        "the registry fallback: `capability_registry` defaults to None and the root does not pass it",
    ),
}

# Sites neither named nor excluded -- a *budget*, so it cannot rot into an allow-list.
_BACKLOG = 22

# relpath of a named module -> bare handlers measured *after* cycle 59.
# journal_store keeps one: `append`'s `JournalEvent.model_validate` fallback, which produces a
# value (the unvalidated record) -- a different shape from a skipped line.
_BARE_AFTER: dict[str, int] = {
    "aegis_ai/journal/journal_store.py": 1,
    "aegis_ai/user_state/manager.py": 0,
    "aegis_ai/web/chat_history.py": 0,
}

# named module -> (file that produces it, needle) -- the reason the record can ever fire.
_PRODUCERS: dict[str, tuple[str, str]] = {
    "aegis_ai/journal/journal_store.py": ("aegis_ai/runtime.py", "JournalStore("),
    "aegis_ai/user_state/manager.py": ("aegis_ai/runtime.py", "UserStateManager("),
    "aegis_ai/web/chat_history.py": ("aegis_ai/web/routes/chat.py", "ChatHistoryStore("),
}

# Cycle 17's measurement, re-pinned here because it is the *reason* for the five exclusions.
_CONTEXT_BUILDER_WIRED = {
    "event_bus",
    "tool_broker",
    "multimodal_llm",
    "capability_retriever",
    "settings_resolver",
    "user_model_store",
    "identity",
}


# -- detector ------------------------------------------------------------------


def _type_names(node: ast.ExceptHandler) -> set[str]:
    """Flatten the handler's type into a name set (a tuple is not a single name)."""
    if node.type is None:
        return {"<bare>"}
    names: set[str] = set()
    stack: list[ast.expr] = [node.type]
    while stack:
        cur = stack.pop()
        if isinstance(cur, ast.Tuple):
            stack.extend(cur.elts)
        elif isinstance(cur, ast.Name):
            names.add(cur.id)
        elif isinstance(cur, ast.Attribute):
            names.add(ast.unparse(cur))
    return names


def _is_bare_discard(handler: ast.ExceptHandler) -> bool:
    """True when the handler's whole body is one `pass` / `continue` / `break`."""
    body = [
        s
        for s in handler.body
        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
    ]
    return len(body) == 1 and isinstance(body[0], (ast.Pass, ast.Continue, ast.Break))


def _bare_handlers_in(source: str) -> list[ast.ExceptHandler]:
    tree = ast.parse(source)
    return [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler) and _is_bare_discard(n)]


def _bare_handlers(path: Path) -> list[ast.ExceptHandler]:
    return _bare_handlers_in(path.read_text(encoding="utf-8"))


def _bare_exception_handlers(path: Path) -> list[ast.ExceptHandler]:
    return [h for h in _bare_handlers(path) if _FAMILY_TYPE in _type_names(h)]


def _src_files() -> list[Path]:
    return sorted(_SRC.rglob("*.py"))


# -- doubles -------------------------------------------------------------------


class _RaisingRetriever:
    def select_for_request(self, *_a, **_k):
        raise RuntimeError("retriever unavailable")


class _RaisingCatalog:
    def list_for_llm(self):
        raise RuntimeError("catalog unreadable")


class _OkCatalog:
    def list_for_llm(self):
        return [{"id": "cap.one", "title": "One", "description": "a description"}]


def _interpreter(**attrs) -> LLMTaskInterpreter:
    system = object.__new__(LLMTaskInterpreter)
    system._retriever = None
    system._catalog = None
    system._registry = None
    for key, value in attrs.items():
        setattr(system, key, value)
    return system


# The realistic corruption: the process died mid-append, so the *last* line is truncated.
_CORRUPT = '{"sequence": 2, "event_type": "journal.appended"'


def _records(caplog, logger_name: str) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.name == logger_name]


# -- cycle 58: the one reachable site of the assembled-context cluster ---------


def test_the_capability_catalog_failure_is_named(caplog) -> None:
    """The catalog is the fallback when the retriever fails, and its failure is invisible."""
    system = _interpreter(_retriever=_RaisingRetriever(), _catalog=_RaisingCatalog())
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        result = system._build_capability_list("hello")

    assert any(_NAMED["aegis_ai/llm_task_interpreter.py"][0] in m for m in _records(caplog, _LOGGER)), (
        f"the catalog failure left no record naming its consequence; got {_records(caplog, _LOGGER)}"
    )
    assert result == "No capability registry available", (
        "the degraded value changed; the record's claim about the consequence must be re-measured"
    )


def test_the_named_record_carries_a_traceback(caplog) -> None:
    system = _interpreter(_catalog=_RaisingCatalog())
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        system._build_capability_list("hello")

    records = [r for r in caplog.records if r.name == _LOGGER]
    assert records, "no record at all"
    assert any(isinstance(r.exc_info, tuple) for r in records), (
        "the record does not carry the traceback (`exc_info=False` is not None but is not a tuple)"
    )


def test_a_healthy_catalog_is_quiet(caplog) -> None:
    """Control: the record appears because of the failure, not because of the call."""
    system = _interpreter(_catalog=_OkCatalog())
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        result = system._build_capability_list("hello")

    assert "cap.one" in result
    assert _records(caplog, _LOGGER) == []


# -- cycle 59: the three reachable readers ------------------------------------


def test_a_journal_line_that_would_not_parse_is_named(tmp_path, caplog) -> None:
    store = JournalStore(data_dir=str(tmp_path))
    path = tmp_path / "journal" / "events.jsonl"
    path.write_text('{"sequence": 1, "event_type": "journal.appended"}\n' + _CORRUPT + "\n", encoding="utf-8")

    with caplog.at_level(logging.DEBUG, logger="aegis_ai.journal.journal_store"):
        rows = store.list_recent(limit=10)
        sequence = store._load_last_sequence()

    messages = _records(caplog, "aegis_ai.journal.journal_store")
    for phrase in _NAMED["aegis_ai/journal/journal_store.py"]:
        assert any(phrase in m for m in messages), f"{phrase!r} left no record; got {messages}"
    assert [r["sequence"] for r in rows] == [1], "the truncated line is no longer skipped"
    assert sequence == 1, "the last sequence must come from the readable line"


def test_a_clean_journal_stays_quiet(tmp_path, caplog) -> None:
    """Control: a file that parses must not warn."""
    store = JournalStore(data_dir=str(tmp_path))
    path = tmp_path / "journal" / "events.jsonl"
    path.write_text('{"sequence": 1, "event_type": "journal.appended"}\n', encoding="utf-8")

    with caplog.at_level(logging.DEBUG, logger="aegis_ai.journal.journal_store"):
        assert store.list_recent(limit=10)
        assert store._load_last_sequence() == 1

    assert _records(caplog, "aegis_ai.journal.journal_store") == []


def test_a_user_state_line_that_would_not_parse_is_named(tmp_path, caplog) -> None:
    timeline = TimelineStore(tmp_path)
    (tmp_path / "timeline" / "2026-10-06.jsonl").write_text(
        '{"timestamp_ms": 1, "source": "pc"}\n' + _CORRUPT + "\n", encoding="utf-8"
    )
    archive = object.__new__(ArchiveManager)  # skip `_load_key`; only `_index` is needed
    archive._index = tmp_path / "archive" / "index.jsonl"
    archive._index.parent.mkdir(parents=True, exist_ok=True)
    archive._index.write_text('{"day": "2026-10-05"}\n' + _CORRUPT + "\n", encoding="utf-8")

    with caplog.at_level(logging.DEBUG, logger="aegis_ai.user_state.manager"):
        events = timeline.query_recent(limit=10)
        rows = archive.list_archives()

    messages = _records(caplog, "aegis_ai.user_state.manager")
    for phrase in _NAMED["aegis_ai/user_state/manager.py"]:
        assert any(phrase in m for m in messages), f"{phrase!r} left no record; got {messages}"
    assert [e["source"] for e in events] == ["pc"], "the truncated event is no longer skipped"
    assert [r["day"] for r in rows] == ["2026-10-05"], "the truncated index line is no longer skipped"


def test_a_clean_user_state_index_stays_quiet(tmp_path, caplog) -> None:
    """Control: parseable input must not warn."""
    archive = object.__new__(ArchiveManager)
    archive._index = tmp_path / "archive" / "index.jsonl"
    archive._index.parent.mkdir(parents=True, exist_ok=True)
    archive._index.write_text('{"day": "2026-10-05"}\n', encoding="utf-8")
    timeline = TimelineStore(tmp_path)
    (tmp_path / "timeline" / "2026-10-06.jsonl").write_text('{"timestamp_ms": 1, "source": "pc"}\n', encoding="utf-8")

    with caplog.at_level(logging.DEBUG, logger="aegis_ai.user_state.manager"):
        assert timeline.query_recent(limit=10)
        assert archive.list_archives()

    assert _records(caplog, "aegis_ai.user_state.manager") == []


def test_a_chat_history_line_that_would_not_parse_is_named(tmp_path, caplog) -> None:
    store = ChatHistoryStore(tmp_path / "chat_history.jsonl")
    store.path.write_text('{"timestamp_ms": 1, "user": "hi"}\n' + _CORRUPT + "\n", encoding="utf-8")

    with caplog.at_level(logging.DEBUG, logger="aegis_ai.web.chat_history"):
        entries = store.load()

    messages = _records(caplog, "aegis_ai.web.chat_history")
    assert any(_NAMED["aegis_ai/web/chat_history.py"][0] in m for m in messages), (
        f"the truncated chat-history line left no record; got {messages}"
    )
    assert [e["user"] for e in entries] == ["hi"], "the truncated line is no longer skipped"


def test_a_clean_chat_history_stays_quiet(tmp_path, caplog) -> None:
    """Control: a parseable history must not warn."""
    store = ChatHistoryStore(tmp_path / "chat_history.jsonl")
    store.path.write_text('{"timestamp_ms": 1, "user": "hi"}\n', encoding="utf-8")

    with caplog.at_level(logging.DEBUG, logger="aegis_ai.web.chat_history"):
        assert store.load()

    assert _records(caplog, "aegis_ai.web.chat_history") == []


def test_the_cycle_59_records_carry_a_traceback(tmp_path, caplog) -> None:
    """A record without the traceback is a message, not a diagnosis (cycles 54-58 pinned this)."""
    journal = JournalStore(data_dir=str(tmp_path / "j"))
    (tmp_path / "j" / "journal" / "events.jsonl").write_text(_CORRUPT + "\n", encoding="utf-8")
    history = ChatHistoryStore(tmp_path / "chat_history.jsonl")
    history.path.write_text(_CORRUPT + "\n", encoding="utf-8")
    archive = object.__new__(ArchiveManager)
    archive._index = tmp_path / "index.jsonl"
    archive._index.write_text(_CORRUPT + "\n", encoding="utf-8")

    with caplog.at_level(logging.DEBUG):
        journal.list_recent(limit=10)
        history.load()
        archive.list_archives()

    for logger_name in ("aegis_ai.journal.journal_store", "aegis_ai.web.chat_history", "aegis_ai.user_state.manager"):
        records = [r for r in caplog.records if r.name == logger_name]
        assert records, f"{logger_name} produced no record"
        assert any(isinstance(r.exc_info, tuple) for r in records), (
            f"{logger_name}: the record carries no traceback (`exc_info=False` is not None but is not a tuple)"
        )


def test_the_named_sites_have_a_producer() -> None:
    """The *reason* these records can fire: a producer exists. Lose it and the record is dead."""
    for relpath, (producer, needle) in sorted(_PRODUCERS.items()):
        text = (_SRC / producer).read_text(encoding="utf-8")
        assert needle in text, (
            f"{relpath} is named because {producer} produces it, but {needle!r} is gone -- "
            "the record is now dead and the naming must be re-adjudicated"
        )


# -- the exclusions, each with its reason --------------------------------------


def test_the_exception_family_is_excluded_plus_backlog() -> None:
    """The census counts *bare* handlers, so the named sites must not appear on either side.

    (Cycle 58's version read `named + excluded + backlog`, which balances only if the backlog is
    understated by the number of named sites -- the same total, the wrong decomposition.)
    """
    measured = sum(len(_bare_exception_handlers(path)) for path in _src_files())
    excluded = sum(count for count, _reason in _EXCLUDED.values())
    assert measured == excluded + _BACKLOG, (
        f"bare `{_FAMILY_TYPE}` handlers changed: measured {measured}, excluded {excluded} + backlog {_BACKLOG}"
    )


@pytest.mark.parametrize("relpath", sorted(_BARE_AFTER))
def test_the_named_modules_have_no_bare_exception_discard_left(relpath) -> None:
    found = len(_bare_exception_handlers(_SRC / relpath))
    assert found == _BARE_AFTER[relpath], f"{relpath}: expected {_BARE_AFTER[relpath]} bare handlers, found {found}"


@pytest.mark.parametrize("relpath", sorted(_EXCLUDED))
def test_the_excluded_sites_are_still_bare(relpath) -> None:
    """An exclusion must not rot: if one is named, its reason must be re-measured."""
    count, reason = _EXCLUDED[relpath]
    found = len(_bare_exception_handlers(_SRC / relpath))
    assert found == count, f"{relpath}: expected {count} bare handlers, found {found} -- {reason}"


def test_the_context_builder_backends_are_unwired() -> None:
    """The reason for the five context_builder exclusions, pinned against the wiring itself."""
    tree = ast.parse(_RUNTIME.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "ContextBuilder":
            found = {kw.arg for kw in node.keywords if kw.arg}
    assert found == _CONTEXT_BUILDER_WIRED, (
        f"the composition root's ContextBuilder backends changed: {sorted(found)} -- "
        "the five exclusions in context_builder.py must be re-adjudicated"
    )


def test_the_router_gets_a_catalog_but_no_registry() -> None:
    """Half of this is the reason the catalog site is named; half, the registry site is not."""
    tree = ast.parse(_RUNTIME.read_text(encoding="utf-8"))
    kwargs: set[str] = set()
    calls = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "InteractionRouter":
            calls += 1
            kwargs = {kw.arg for kw in node.keywords if kw.arg}
    assert calls == 1, f"expected exactly one InteractionRouter call, found {calls}"
    assert "capability_catalog" in kwargs, (
        "the catalog is no longer wired, so the named site is unreachable and must be re-adjudicated"
    )
    assert "capability_registry" not in kwargs, (
        "a capability registry is now wired, so the interpreter's registry fallback IS reachable "
        "and must be named"
    )


def test_the_briefing_provider_has_no_producer() -> None:
    """The reason for the three provider exclusions: nothing in src/ constructs the class."""
    producers: list[str] = []
    for path in _src_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if name == "DailyBriefingProvider":
                producers.append(f"{path.name}:{node.lineno}")
    assert producers == [], (
        f"DailyBriefingProvider now has a producer ({producers}) -- its three exclusions must be "
        "re-adjudicated"
    )


# -- non-vacuity ---------------------------------------------------------------


def test_the_detector_reads_a_tuple_and_ignores_a_broader_base() -> None:
    source = (
        "try:\n    pass\n"
        "except Exception:\n    pass\n"
        "except (ValueError, KeyError):\n    continue\n"
        "except BaseException:\n    break\n"
        "except Exception as exc:\n    logger.debug('named %s', exc, exc_info=True)\n"
        "except Exception:\n    do_something()\n"
    )
    handlers = _bare_handlers_in(source)
    kinds = [tuple(sorted(_type_names(h))) for h in handlers]
    assert kinds == [("Exception",), ("KeyError", "ValueError"), ("BaseException",)], kinds
    assert [h for h in handlers if _FAMILY_TYPE in _type_names(h)] == [handlers[0]], (
        "a tuple member or a broader base was mis-attributed to the family"
    )


def test_the_detector_is_not_vacuous() -> None:
    """A detector that finds nothing would make the census above trivially true."""
    total = sum(len(_bare_handlers(path)) for path in _src_files())
    assert total > 20, f"the detector found only {total} bare discards; it is probably broken"
    assert len(_bare_exception_handlers(_SRC / "aegis_ai" / "context_builder.py")) == 5
