"""Cycle 58 pin: an `Exception` swallow is named only where the handler can actually run.

Why reachability is the criterion
---------------------------------
Cycle 17 established it for `context_builder.py` (`test_context_builder_failures_are_named.py`):
the composition root wires **7 of the ~20** backends the builder accepts, so a handler behind
`if self._backend:` cannot run, and naming it would add a record to code that cannot run.

Cycle 58 started from the *consequence* instead -- "a failed section build silently omits a line
from the LLM's context" -- and named **ten** such handlers across three modules.  Then it measured
the premise, and **nine of the ten were unreachable**:

  * `context_builder.py` (5): the five section builders sit behind `if self._user_state_manager:`
    / `_delegation_policy` / `_commitment_manager` / `_user_understanding_service` / `_agent_state`,
    and `runtime.py` passes none of them.  The section is omitted by the **guard**, not by the
    handler, so a record inside the handler changes nothing in production.
  * `briefing/provider.py` (3): `DailyBriefingProvider` has **no producer anywhere in `src/`**
    (only a docstring example and tests).  A dead class's handlers cannot run either.
  * `llm_task_interpreter.py` (1 of 2): `router.__init__` defaults `capability_registry=None` and
    the composition root does not pass it, so the registry fallback is unreachable.  The
    **catalog** fallback *is* reachable (it is passed) and stays named.

Why the nine were reverted rather than kept
-------------------------------------------
A record that cannot fire does not make a failure louder -- and it *lowers the census*, so the
codebase looks safer than it is.  So the criterion applied here is cycle 17's: **name a swallow
when the handler is reachable from the composition root.**  Each exclusion is pinned *with its
reason*, and each reason is pinned against the wiring that makes it true, so that wiring a
backend goes red here instead of silently rotting into an allow-list.
"""
from __future__ import annotations

import ast
import logging
from pathlib import Path

import pytest

from aegis_ai.llm_task_interpreter import LLMTaskInterpreter

_AI_SERVER = Path(__file__).resolve().parents[1]
_SRC = _AI_SERVER / "src"
_RUNTIME = _SRC / "aegis_ai" / "runtime.py"

_LOGGER = "aegis_ai.llm_task_interpreter"
_FAMILY_TYPE = "Exception"

# The one reachable site: relpath -> a phrase only that site's record contains.
_NAMED: dict[str, str] = {
    "aegis_ai/llm_task_interpreter.py": "Could not list capabilities from the catalog",
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
_BACKLOG = 26

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


# -- the named site ------------------------------------------------------------


def test_the_capability_catalog_failure_is_named(caplog) -> None:
    """The catalog is the fallback when the retriever fails, and its failure is invisible."""
    system = _interpreter(_retriever=_RaisingRetriever(), _catalog=_RaisingCatalog())
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        result = system._build_capability_list("hello")

    messages = [r.getMessage() for r in caplog.records if r.name == _LOGGER]
    assert any(_NAMED["aegis_ai/llm_task_interpreter.py"] in m for m in messages), (
        f"the catalog failure left no record naming its consequence; got {messages}"
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
    assert [r.getMessage() for r in caplog.records if r.name == _LOGGER] == []


# -- the exclusions, each with its reason --------------------------------------


def test_the_exception_family_is_one_named_plus_nine_excluded_plus_a_backlog() -> None:
    """The census is an equation, so neither a new silent handler nor a named one can hide."""
    named = len(_NAMED)
    excluded = sum(count for count, _reason in _EXCLUDED.values())
    measured = sum(len(_bare_exception_handlers(path)) for path in _src_files())
    assert measured == named + excluded + _BACKLOG, (
        f"bare `{_FAMILY_TYPE}` handlers changed: measured {measured}, "
        f"named {named} + excluded {excluded} + backlog {_BACKLOG}"
    )


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
