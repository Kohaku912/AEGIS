"""Cycle 15 pin: the 15 swallowed failures in ``CuriosityDrivenExplorationSystem`` are named.

Measured 2026-10-04 (HEAD 69640f4). Every one of the fifteen turned a *failure* into an
*absence*, so it was indistinguishable from a positive fact:

- the **seven candidate sources** (`_candidates_from_questions` x2, `_candidates_from_failures`,
  `_candidates_from_unknown`, `_candidates_from_improvements`, `_candidates_from_llm` x2) each
  swallow their own read, so an unreadable store contributes exactly as many candidates as an
  empty one -- i.e. none;
- **`explore`'s** post-exploration curiosity update is swallowed, so a *successful* exploration
  does not reduce the curiosity pressure that produced it;
- the **three context builders** (`_build_exploration_context`) each swallow, so the LLM explores
  without the history / knowledge / skills most relevant to the topic;
- the **four persistence sinks** (`_save_exploration_result`: episodic, semantic, action trace,
  exploration log) each swallow, so what was learned is discarded and the run is not recallable.

The asymmetry that made this worth doing is *inside the same module*: the LLM failure at
`_candidates_from_llm` was already named (`logger.warning("LLM suggestion failed: %s", e)`) while
every source and sink failure was silent.

Return values are unchanged -- this pin fixes behaviour that already existed and may not move.
"""

from __future__ import annotations

import ast
import logging
import re
from pathlib import Path

import pytest

from aegis_ai.autonomous.curiosity_exploration import (
    CuriosityDrivenExplorationSystem,
    ExplorationCandidate,
    ExplorationResult,
)

_AI_SERVER = Path(__file__).resolve().parents[1]
_MODULE = _AI_SERVER / "src" / "aegis_ai" / "autonomous" / "curiosity_exploration.py"
_LOGGER = "aegis_ai.autonomous.curiosity_exploration"

# site label -> a distinctive phrase from that site's record
_NAMED = {
    "1 questions/semantic": "open questions from semantic memory",
    "2 questions/episodic": "open questions from episodic memory",
    "3 failures": "failed action traces",
    "4 unknown": "partially-understood knowledge",
    "5 improvements": "active skills from skill memory",
    "6 llm/desire": "render the desire state",
    "7 llm/recent": "recent episodes for the exploration prompt",
    "8 explore/desire": "post-exploration curiosity change",
    "9 context/episodes": "related episodes for the exploration context",
    "10 context/knowledge": "related knowledge",
    "11 context/skills": "related skills for the exploration context",
    "12 save/episodic": "record the exploration in episodic memory",
    "13 save/semantic": "new knowledge to semantic memory",
    "14 save/trace": "record the exploration in the action trace",
    "15 save/log": "append to the exploration log",
}


class _Raising:
    """A backend whose named methods raise; any other attribute is absent."""

    def __init__(self, *methods: str) -> None:
        object.__setattr__(self, "_methods", set(methods))

    def __getattr__(self, name: str):
        if name in object.__getattribute__(self, "_methods"):
            def boom(*_a, **_k):
                raise RuntimeError(f"{name} unavailable")
            return boom
        raise AttributeError(name)


class _OkSkills:
    """A skill backend that answers, so it is not the site under test."""

    def get_active(self):
        return []

    def find_relevant(self, *_a, **_k):
        return []


class _OkLLM:
    """A working LLM stub: `generate` returns a parseable, successful response."""

    class _Response:
        success = True
        content = '{"findings": "ok", "new_knowledge": [], "new_questions": []}'
        error = None

    def generate(self, *_a, **_k):
        return self._Response()


class _DesireThatCannotBeUpdated:
    """A desire system whose curiosity update raises -- but which *looks* updatable."""

    class _Desire:
        value = 0.0
        expected_value = 1.0

    def get_desire(self, _name):
        return self._Desire()

    def update_value(self, *_a, **_k):
        raise RuntimeError("desire store unavailable")


def _system(tmp_path, **kw) -> CuriosityDrivenExplorationSystem:
    """A *realistically constructed* instance (the plain-assignment `__init__`)."""
    kw.setdefault("skill_memory", _OkSkills())
    return CuriosityDrivenExplorationSystem(data_dir=str(tmp_path), **kw)


def _candidate() -> ExplorationCandidate:
    return ExplorationCandidate(candidate_id="c1", topic="a topic", description="why", source="test")


def _result() -> ExplorationResult:
    return ExplorationResult(result_id="r1", candidate_id="c1", topic="a topic",
                             findings="ok", new_knowledge=["a fact"], success=True)


def _drive(label: str, system: CuriosityDrivenExplorationSystem, tmp_path) -> None:
    """Perform the call that reaches the site named by `label`."""
    if label == "1 questions/semantic":
        system._candidates_from_questions()
    elif label == "2 questions/episodic":
        system._candidates_from_questions()
    elif label == "3 failures":
        system._candidates_from_failures()
    elif label == "4 unknown":
        system._candidates_from_unknown()
    elif label == "5 improvements":
        system._candidates_from_improvements()
    elif label in ("6 llm/desire", "7 llm/recent"):
        system._candidates_from_llm()
    elif label == "8 explore/desire":
        system.explore(_candidate())
    elif label in ("9 context/episodes", "10 context/knowledge", "11 context/skills"):
        system._build_exploration_context(_candidate())
    elif label in ("12 save/episodic", "13 save/semantic", "14 save/trace", "15 save/log"):
        system._save_exploration_result(_candidate(), _result())
    else:  # pragma: no cover
        raise AssertionError(f"no driver for {label}")


def _make(label: str, tmp_path) -> CuriosityDrivenExplorationSystem:
    """Build the instance whose named backend fails for `label`."""
    if label == "1 questions/semantic":
        return _system(tmp_path, semantic_memory=_Raising("get_by_category"))
    if label == "2 questions/episodic":
        return _system(tmp_path, episodic_memory=_Raising("recall_recent"))
    if label == "3 failures":
        return _system(tmp_path, action_trace=_Raising("get_failed"))
    if label == "4 unknown":
        return _system(tmp_path, semantic_memory=_Raising("get_knowledge"))
    if label == "5 improvements":
        return _system(tmp_path, skill_memory=_Raising("get_active"))
    if label == "6 llm/desire":
        return _system(tmp_path, llm=_OkLLM(), desire_system=_Raising("to_context_string"))
    if label == "7 llm/recent":
        return _system(tmp_path, llm=_OkLLM(), episodic_memory=_Raising("recall_recent"))
    if label == "8 explore/desire":
        return _system(tmp_path, llm=_OkLLM(), desire_system=_DesireThatCannotBeUpdated())
    if label == "9 context/episodes":
        return _system(tmp_path, episodic_memory=_Raising("recall_similar"))
    if label == "10 context/knowledge":
        return _system(tmp_path, semantic_memory=_Raising("search"))
    if label == "11 context/skills":
        return _system(tmp_path, skill_memory=_Raising("find_relevant"))
    if label == "12 save/episodic":
        return _system(tmp_path, episodic_memory=_Raising("record"))
    if label == "13 save/semantic":
        return _system(tmp_path, semantic_memory=_Raising("add"))
    if label == "14 save/trace":
        return _system(tmp_path, action_trace=_Raising("begin_trace"))
    if label == "15 save/log":
        # The log path exists but is a *directory*, so `open(..., "a")` cannot succeed.
        (tmp_path / "exploration_log.jsonl").mkdir()
        return _system(tmp_path)
    raise AssertionError(f"no builder for {label}")  # pragma: no cover


def _warnings(caplog) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == _LOGGER and r.levelno >= logging.WARNING]


@pytest.mark.parametrize("label", sorted(_NAMED))
def test_a_swallowed_failure_is_named(label: str, caplog, tmp_path) -> None:
    system = _make(label, tmp_path)
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        _drive(label, system, tmp_path)

    records = _warnings(caplog)
    assert records, f"{label}: a swallowed failure emitted no warning"
    assert any(_NAMED[label] in r.getMessage() for r in records), (
        f"{label}: no record carried the consequence phrase {_NAMED[label]!r}; got "
        f"{[r.getMessage() for r in records]}"
    )
    # The record must carry the `型: メッセージ` shape -- i.e. name the exception *type*.
    # Not "RuntimeError" specifically: the log sink fails with `PermissionError`.
    assert any(
        re.search(r"\([A-Za-z_][A-Za-z0-9_]*(Error|Exception):", r.getMessage()) for r in records
    ), f"{label}: no record named the exception type; got {[r.getMessage() for r in records]}"


def test_legitimate_absences_stay_silent(caplog, tmp_path) -> None:
    """The control: nothing wired, or nothing to report, is not a failure.

    Without this the pin would pass on a warning emitted unconditionally.
    """
    system = _system(tmp_path)  # every backend None; skills answer with empty lists
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        system._candidates_from_questions()
        system._candidates_from_failures()
        system._candidates_from_unknown()
        system._candidates_from_improvements()
        system._candidates_from_llm()
        system._build_exploration_context(_candidate())
        system._save_exploration_result(_candidate(), _result())
    assert not _warnings(caplog), [r.getMessage() for r in _warnings(caplog)]


# ---------------------------------------------------------------------- structural pin


def _handlers_by_method() -> dict[str, list[ast.ExceptHandler]]:
    tree = ast.parse(_MODULE.read_text(encoding="utf-8"))
    cls = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "CuriosityDrivenExplorationSystem"
    )
    out: dict[str, list[ast.ExceptHandler]] = {}
    for fn in cls.body:
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        hs = [h for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler)]
        if hs:
            out[fn.name] = hs
    return out


def test_no_silent_handler_remains() -> None:
    silent: list[tuple[str, int]] = []
    total = 0
    for method, handlers in _handlers_by_method().items():
        for handler in handlers:
            total += 1
            body = handler.body
            if len(body) != 1:
                continue
            stmt = body[0]
            if isinstance(stmt, ast.Pass) or (
                isinstance(stmt, ast.Return)
                and isinstance(stmt.value, (ast.Constant, ast.List, ast.Dict, ast.Tuple))
            ):
                silent.append((method, handler.lineno))
    # Non-vacuity: the scan must actually be seeing the module's handlers.
    assert total >= 15, f"the scan found only {total} handlers; it is not measuring"
    assert silent == [], f"a swallowed failure is silent again: {silent}"


def test_the_fifteen_sites_do_warn() -> None:
    """Guards against the cycle-13 self-error: a bare ``logger.warning(...)`` *is* an
    ``ast.Expr``, so filtering ``ast.Expr`` out before asking 'is this body silent?' reports
    every named handler as silent."""
    handlers = _handlers_by_method()
    named = 0
    for handler_list in handlers.values():
        for handler in handler_list:
            for stmt in handler.body:
                if (
                    isinstance(stmt, ast.Expr)
                    and isinstance(stmt.value, ast.Call)
                    and getattr(stmt.value.func, "attr", "") == "warning"
                ):
                    named += 1
    assert named >= 15, f"only {named} handlers carry a logger.warning; expected >= 15"
