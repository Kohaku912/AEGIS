"""The memory/ package names its failures.

Measured 2026-10-06 (cycle 47)
-----------------------------
Five handlers under ``memory/`` had a body that was exactly ``pass``, in three modules
that **already had a logger** -- so unlike ``personal_ai/`` (cycle 45) nothing had to be
imported; the silence was a choice, not a missing facility.

Three of the five are on *live* paths:

- ``MemoryManager._publish_event`` (``memory_manager.py:592``) -- the memory manager's
  only outward event. A publish that failed left the rest of the system believing the
  memory event had been emitted.
- ``SleepManager._publish_event`` / ``_record_audit`` (``sleep.py:217`` / ``:231``) --
  the consolidation summary's event and its audit row. ``SleepManager.__init__`` takes
  both managers as optional parameters, so the early ``None`` return is a *deliberate*
  non-logging path; the failure of a *present* manager was not.
- ``MemoryManager.classify_memory_type`` (``memory_manager.py:362``) -- the LLM
  classifier's failure fell through to the hard-coded default ``"episodic"``. That
  default is unchanged; the failure is now attributable.

The fifth is the one that changed a **reported value**:

- ``ChromaSemanticMemory.get_stats`` (``chroma_semantic.py:214``) -- ``count()`` failing
  left ``chroma_count`` at ``0``, so *"the vector index could not be read"* and *"the
  index is empty"* were the same answer. The value is still ``0`` (behaviour preserved);
  the difference is that the reason is now in the log.

**The intended form already existed in this repo.** ``presentation/manager.py:456``
``_publish_event`` logs ``"Failed to publish event %s"`` at DEBUG, and
``autonomous/autonomous_controller.py:320`` / ``integrations/webhook_sender.py:163``
``_record_audit`` log at WARNING -- the silent copies were not a module-wide convention
but the residue of a copy.

Scope
-----
Cycle 16's unit, applied to a package: **no handler under ``memory/`` has a body that is
exactly ``pass``**. Handlers that *produce* a value the caller receives stay out (a
different, milder class); the ``None``-guard early returns are not handlers at all.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from aegis_ai.memory.action_trace import ActionTraceMemory
from aegis_ai.memory.chroma_semantic import ChromaSemanticMemory
from aegis_ai.memory.experiential import ExperientialMemory
from aegis_ai.memory.memory_manager import MemoryManager
from aegis_ai.memory.sleep import SleepManager

_PKG = Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "memory"

_SLEEP = "aegis_ai.memory.sleep"
_MEMORY_MANAGER = "aegis_ai.memory.memory_manager"
_CHROMA = "aegis_ai.memory.chroma_semantic"
_ACTION_TRACE = "aegis_ai.memory.action_trace"
_EXPERIENTIAL = "aegis_ai.memory.experiential"

# (module stem, enclosing function) -> the logger that must name the failure.
# The five cycle-47 sites, plus the two cycle-52 sites whose bodies were a bare
# `continue` (invisible to the `pass`-keyed census the pin used until then).
_NAMED_SITES = {
    ("chroma_semantic", "get_stats"): _CHROMA,
    ("memory_manager", "classify_memory_type"): _MEMORY_MANAGER,
    ("memory_manager", "_publish_event"): _MEMORY_MANAGER,
    ("sleep", "_publish_event"): _SLEEP,
    ("sleep", "_record_audit"): _SLEEP,
    ("action_trace", "_load"): _ACTION_TRACE,
    ("experiential", "_load"): _EXPERIENTIAL,
}


# ── helpers ────────────────────────────────────────────────────────────────


def _modules() -> list[Path]:
    return sorted(_PKG.rglob("*.py"))


def _handlers_from_tree(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            yield tree, node


def _handlers(path: Path):
    yield from _handlers_from_tree(ast.parse(path.read_text(encoding="utf-8")))


def _body_without_docstring(handler: ast.ExceptHandler) -> list[ast.stmt]:
    return [
        s
        for s in handler.body
        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
                and isinstance(s.value.value, str))
    ]


def _is_bare_discard(handler: ast.ExceptHandler) -> str | None:
    """``"pass"`` / ``"continue"`` / ``"break"`` when the body is exactly that one statement.

    Cycle 52 widened the rule from ``pass`` to every single-statement discard. A bare
    ``continue`` drops the failure exactly as ``pass`` does, and it was invisible to the
    census the pin used until then: ``action_trace._load`` and ``experiential._load``
    both swallowed ``except Exception`` that way (measured 2026-10-06).
    """
    body = _body_without_docstring(handler)
    if len(body) != 1:
        return None
    stmt = body[0]
    if isinstance(stmt, ast.Pass):
        return "pass"
    if isinstance(stmt, ast.Continue):
        return "continue"
    if isinstance(stmt, ast.Break):
        return "break"
    return None


def _enclosing_function(tree: ast.AST, target: ast.AST) -> str:
    best = "<module>"
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                if sub is target:
                    best = node.name
    return best


def _names_a_logger(handler: ast.ExceptHandler) -> bool:
    for stmt in _body_without_docstring(handler):
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.Attribute) and sub.attr in (
                "debug", "info", "warning", "error", "exception", "critical", "log",
            ):
                if isinstance(sub.value, ast.Name) and "log" in sub.value.id:
                    return True
    return False


# ── structural: no bare `pass` survives in the package ─────────────────────


def test_no_handler_in_memory_is_a_bare_discard():
    """Cycle 16's rule, package-wide and widened in cycle 52: every handler names its failure."""
    offenders = []
    for path in _modules():
        for _tree, handler in _handlers(path):
            shape = _is_bare_discard(handler)
            if shape is not None:
                offenders.append(f"{path.name}:{handler.lineno} [{shape}]")
    assert offenders == [], f"single-statement discards remain in memory/: {offenders}"


def test_the_discard_detector_sees_every_shape():
    """Detector self-test: widening the rule is only meaningful if the walker sees all three."""
    tree = ast.parse(
        "def f():\n"
        "    for _ in items:\n"
        "        try:\n"
        "            pass\n"
        "        except ValueError:\n"
        "            pass\n"
        "        except TypeError:\n"
        "            continue\n"
        "        except KeyError:\n"
        "            break\n"
        "        except OSError:\n"
        "            logger.debug('named', exc_info=True)\n"
    )
    shapes = [s for _t, h in _handlers_from_tree(tree) if (s := _is_bare_discard(h)) is not None]
    assert shapes == ["pass", "continue", "break"], shapes


def test_the_census_is_not_vacuous():
    """The rule above is only meaningful if the scanner actually sees handlers.

    Without this control, a rename of the package directory would make the rule
    pass by scanning nothing.
    """
    files = _modules()
    total = sum(1 for path in files for _ in _handlers(path))
    assert len(files) >= 25, f"only {len(files)} files under memory/ -- wrong root?"
    assert total >= 55, f"only {total} handlers found -- the scanner is not seeing them"


def test_each_named_site_calls_a_logger():
    """The five sites are named *structurally*, so a future edit cannot re-silence one."""
    seen = {}
    for path in _modules():
        for tree, handler in _handlers(path):
            key = (path.stem, _enclosing_function(tree, handler))
            if key in _NAMED_SITES:
                seen[key] = _names_a_logger(handler)
    assert set(seen) == set(_NAMED_SITES), (
        f"missing sites: {sorted(set(_NAMED_SITES) - set(seen))}"
    )
    unnamed = sorted(k for k, ok in seen.items() if not ok)
    assert unnamed == [], f"these sites no longer log their failure: {unnamed}"


def test_the_five_modules_have_their_loggers():
    for name, path in (
        (_SLEEP, _PKG / "sleep.py"),
        (_MEMORY_MANAGER, _PKG / "memory_manager.py"),
        (_CHROMA, _PKG / "chroma_semantic.py"),
        (_ACTION_TRACE, _PKG / "action_trace.py"),
        (_EXPERIENTIAL, _PKG / "experiential.py"),
    ):
        text = path.read_text(encoding="utf-8")
        assert f'getLogger("{name}")' in text, f"{path.name} lost its logger {name}"


# ── behavioural: a failing publish is named, a working one is quiet ────────


class _RaisingEventManager:
    def publish(self, *_a, **_kw):
        raise RuntimeError("event bus down")

    def publish_event(self, *_a, **_kw):
        raise RuntimeError("event bus down")


class _RaisingAuditManager:
    def append(self, *_a, **_kw):
        raise RuntimeError("audit sink down")

    def log_decision(self, *_a, **_kw):
        raise RuntimeError("audit sink down")


class _RaisingLLM:
    def generate(self, *_a, **_kw):
        raise RuntimeError("no provider")


class _WorkingEventManager:
    def __init__(self):
        self.published = []

    def publish(self, event):
        self.published.append(event)

    def publish_event(self, **_kw):
        self.published.append(_kw)


def test_sleep_publish_failure_is_named(caplog):
    manager = SleepManager(event_manager=_RaisingEventManager())
    with caplog.at_level(logging.DEBUG, logger=_SLEEP):
        manager._publish_event("memory.sleep.completed", {"ok": True})
    assert any("Failed to publish event" in r.getMessage() for r in caplog.records), (
        "a failing publish left no record"
    )
    assert all(r.name == _SLEEP for r in caplog.records)
    assert any(r.exc_info for r in caplog.records), "the traceback was not attached"


def test_sleep_publish_success_is_quiet(caplog):
    """Control: the record must come from the *failure*, not from the call."""
    bus = _WorkingEventManager()
    manager = SleepManager(event_manager=bus)
    with caplog.at_level(logging.DEBUG, logger=_SLEEP):
        manager._publish_event("memory.sleep.completed", {"ok": True})
    assert bus.published, "the control did not actually publish"
    assert [r for r in caplog.records if r.name == _SLEEP] == []


def test_sleep_audit_failure_is_named(caplog):
    manager = SleepManager(audit_manager=_RaisingAuditManager())
    with caplog.at_level(logging.DEBUG, logger=_SLEEP):
        manager._record_audit("sleep_completed", completed_ms=1)
    assert any("Failed to record sleep audit" in r.getMessage() for r in caplog.records)


def test_sleep_audit_absent_manager_is_quiet(caplog):
    """Control: the early ``None`` return is a deliberate non-logging path.

    ``audit_manager`` is an optional constructor parameter, so its absence must stay
    silent -- only a *present* manager's failure is a defect.
    """
    manager = SleepManager(audit_manager=None)
    with caplog.at_level(logging.DEBUG, logger=_SLEEP):
        manager._record_audit("sleep_completed", completed_ms=1)
    assert [r for r in caplog.records if r.name == _SLEEP] == []


def test_memory_manager_publish_failure_is_named(caplog):
    manager = MemoryManager(event_manager=_RaisingEventManager())
    with caplog.at_level(logging.DEBUG, logger=_MEMORY_MANAGER):
        manager._publish_event("memory.conversation_encoded", "conversation", "conversation")
    assert any("Failed to publish event" in r.getMessage() for r in caplog.records)


def test_memory_manager_publish_absent_manager_is_quiet(caplog):
    manager = MemoryManager(event_manager=None)
    with caplog.at_level(logging.DEBUG, logger=_MEMORY_MANAGER):
        manager._publish_event("memory.conversation_encoded", "conversation", "conversation")
    assert [r for r in caplog.records if r.name == _MEMORY_MANAGER] == []


def test_classify_failure_is_named_and_the_default_is_unchanged(caplog):
    """The fallback value must not move: only the attribution is new."""
    manager = MemoryManager(llm_gateway=_RaisingLLM())
    with caplog.at_level(logging.DEBUG, logger=_MEMORY_MANAGER):
        got = manager.classify_memory_type("the user prefers tea")
    assert got == "episodic", "the fallback classification changed"
    assert any("Failed to classify memory type" in r.getMessage() for r in caplog.records)


def test_classify_without_llm_is_quiet(caplog):
    """Control: no LLM configured is not a failure."""
    manager = MemoryManager(llm_gateway=None)
    with caplog.at_level(logging.DEBUG, logger=_MEMORY_MANAGER):
        got = manager.classify_memory_type("anything")
    assert got == "episodic"
    assert [r for r in caplog.records if r.name == _MEMORY_MANAGER] == []


# ── behavioural: the reported value stays 0, but the reason is named ───────


class _RaisingCollection:
    def count(self):
        raise RuntimeError("chroma index unreadable")


def _chroma_without_touching_disk() -> ChromaSemanticMemory:
    """``__init__`` builds a PersistentClient under ``data/chroma`` -- do not run it."""
    obj = object.__new__(ChromaSemanticMemory)
    obj._facts = {}
    obj._collection = None
    return obj


def test_chroma_get_stats_names_a_failed_count(caplog):
    memory = _chroma_without_touching_disk()
    memory._collection = _RaisingCollection()
    with caplog.at_level(logging.DEBUG, logger=_CHROMA):
        stats = memory.get_stats()
    assert stats["chroma_count"] == 0, "the reported value moved"
    assert stats["chroma_available"] is True
    assert any("count() failed" in r.getMessage() for r in caplog.records), (
        "an unreadable index is still indistinguishable from an empty one"
    )


def test_chroma_get_stats_without_a_collection_is_quiet(caplog):
    """Control: no collection configured is not a failure."""
    memory = _chroma_without_touching_disk()
    memory._collection = None
    with caplog.at_level(logging.DEBUG, logger=_CHROMA):
        stats = memory.get_stats()
    assert stats == {"jsonl_facts": 0, "chroma_available": False, "chroma_count": 0}
    assert [r for r in caplog.records if r.name == _CHROMA] == []


def test_the_named_site_map_covers_exactly_seven_sites():
    """The map's size is part of the pin: dropping a site must not pass silently.

    ``test_each_named_site_calls_a_logger`` compares the map against what the scanner
    finds, so a *renamed* function makes ``seen`` smaller and fails. This asserts the
    denominator itself, so a future edit that quietly shrinks the map is visible.
    """
    assert len(_NAMED_SITES) == 7
    assert len({mod for mod, _fn in _NAMED_SITES}) == 5


# ── cycle 52: the two `continue` discards, which the `pass` census could not see ──
#
# Both load a JSONL store into a hot in-memory window. A row that cannot be
# reconstructed is skipped, so the window silently holds fewer entries than the file
# does. Both modules *do* log a "Loaded %d" line afterwards -- but that counts what
# *survived*, so a drop is only visible as a smaller number, never as a drop. The
# assertions below therefore discriminate by level: the skip record is DEBUG, the
# "Loaded" line is INFO.


def _debug_records(caplog, name: str) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == name and r.levelno == logging.DEBUG]


def test_action_trace_load_names_a_row_it_could_not_rebuild(tmp_path, caplog):
    path = tmp_path / "action_traces.jsonl"
    path.write_text(
        '{"trace_id": "good", "status": "running"}\n'
        '{"trace_id": "bad", "status": "not-a-status"}\n',
        encoding="utf-8",
    )
    with caplog.at_level(logging.DEBUG, logger=_ACTION_TRACE):
        memory = ActionTraceMemory(path=str(path))

    assert [t.trace_id for t in memory._traces.values()] == ["good"], (
        "the unloadable row is no longer skipped -- re-measure"
    )
    records = _debug_records(caplog, _ACTION_TRACE)
    assert [r.getMessage() for r in records] == ["Skipped an action-trace row that would not load"], (
        f"the skipped row is silent again: {[r.getMessage() for r in records]}"
    )
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_action_trace_load_is_quiet_on_a_clean_file(tmp_path, caplog):
    path = tmp_path / "action_traces.jsonl"
    path.write_text('{"trace_id": "good", "status": "running"}\n', encoding="utf-8")
    with caplog.at_level(logging.DEBUG, logger=_ACTION_TRACE):
        memory = ActionTraceMemory(path=str(path))
    assert [t.trace_id for t in memory._traces.values()] == ["good"]
    assert _debug_records(caplog, _ACTION_TRACE) == [], "the healthy load path now logs a failure"


def test_experiential_load_names_a_row_it_could_not_rebuild(tmp_path, caplog):
    data_dir = tmp_path / "memory"
    data_dir.mkdir()
    (data_dir / "experiences.jsonl").write_text(
        '{"experience_id": "good", "action": "did a thing"}\n'
        '{"not_a_field": 1}\n',
        encoding="utf-8",
    )
    with caplog.at_level(logging.DEBUG, logger=_EXPERIENTIAL):
        memory = ExperientialMemory(data_dir=str(data_dir))

    assert [e.experience_id for e in memory._experiences] == ["good"], (
        "the unloadable row is no longer skipped -- re-measure"
    )
    records = _debug_records(caplog, _EXPERIENTIAL)
    assert [r.getMessage() for r in records] == ["Skipped an experience row that would not load"], (
        f"the skipped row is silent again: {[r.getMessage() for r in records]}"
    )
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_experiential_load_is_quiet_on_a_clean_file(tmp_path, caplog):
    data_dir = tmp_path / "memory"
    data_dir.mkdir()
    (data_dir / "experiences.jsonl").write_text(
        '{"experience_id": "good", "action": "did a thing"}\n', encoding="utf-8"
    )
    with caplog.at_level(logging.DEBUG, logger=_EXPERIENTIAL):
        memory = ExperientialMemory(data_dir=str(data_dir))
    assert [e.experience_id for e in memory._experiences] == ["good"]
    assert _debug_records(caplog, _EXPERIENTIAL) == [], "the healthy load path now logs a failure"


def test_the_two_new_detectors_are_not_vacuous(caplog):
    caplog.set_level(logging.DEBUG, logger=_ACTION_TRACE)
    caplog.set_level(logging.DEBUG, logger=_EXPERIENTIAL)
    logging.getLogger(_ACTION_TRACE).debug("control")
    logging.getLogger(_EXPERIENTIAL).debug("control")
    assert len(_debug_records(caplog, _ACTION_TRACE)) == 1, (
        "the detector is blind; the 'is quiet' assertions above prove nothing"
    )
    assert len(_debug_records(caplog, _EXPERIENTIAL)) == 1, (
        "the detector is blind; the 'is quiet' assertions above prove nothing"
    )
