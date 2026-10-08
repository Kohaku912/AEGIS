"""Cycle 55 pin: a KeyError fallback that substitutes a default is never silent.

Measured 2026-10-06 (HEAD a3b47d2). The unit is again a family defined by its exception type --
cycle 55's is ``KeyError`` -- and the body shape is a bare discard (``pass``/``continue``/``break``).
Repo-wide there were **4 such handlers in 4 functions**, and three of them silently substituted a
*different value*:

* ``task/execution_engine.TaskExecutionEngine._get_system_prompt`` -- an unknown prompt id falls through
  to ``default`` (``""``), so a **typo'd prompt id is indistinguishable from an intentionally absent
  one**: the task runs with an empty system prompt.
* ``task/execution_engine.TaskExecutionEngine._resolve_settings`` -- an unknown profile falls through to
  a hard-coded ``_Defaults`` (``max_tokens=2048, temperature=0.3``). Per the standing rule "a silent
  fallback can change a security-relevant value -- measure the *diff*": the built-in defaults are
  **not** the shipped config, so a **typo'd profile silently runs on different settings**.
* ``web/llm_config_routes.get_profiles`` -- a profile in the enumeration list that is not configured
  is omitted from the response, so the operator sees fewer profiles with no reason given.
* ``presentation/manager.PresentationManager.update`` -- an ``importance`` value that is not in the
  ``Importance`` enum leaves the field at its **previous** value, yet the response still says
  ``{"ok": True}``: a **partial patch reported as a success**.

Why this cycle exists (and the cycle-54 lesson, re-demonstrated by my own tooling): the site in
``PresentationManager.update`` is spelled ``except (ValueError, KeyError)``. The scoping census that
found the other three compared the unparsed except-type against the **string** ``"KeyError"``, so it
could not see a **tuple** that merely *contains* the family type -- and it reported "3 sites". The
rule below tests membership in a **set**, which finds 4. The tuple-spelling test in this file pins
that difference so the mistake cannot recur.

Behaviour is unchanged -- each site gains one DEBUG record with ``exc_info``.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Any

from aegis_ai.presentation.manager import PresentationManager
from aegis_ai.task.execution_engine import TaskExecutionEngine

_SRC = Path(__file__).resolve().parents[1] / "src"

_ENGINE = "aegis_ai.task.execution_engine"
_LLM_CONFIG = "aegis_ai.web.llm_config"
_PRESENTATION = "aegis_ai.presentation.manager"

FAMILY_TYPE = "KeyError"

# (path relative to src/, enclosing function) -> (logger name, handler count measured 2026-10-06)
_NAMED_SITES: dict[tuple[str, str], tuple[str, int]] = {
    ("aegis_ai/task/execution_engine.py", "_get_system_prompt"): (_ENGINE, 1),
    ("aegis_ai/task/execution_engine.py", "_resolve_settings"): (_ENGINE, 1),
    ("aegis_ai/web/llm_config_routes.py", "get_profiles"): (_LLM_CONFIG, 2),
    ("aegis_ai/presentation/manager.py", "update"): (_PRESENTATION, 1),
}


# ── ast helpers ────────────────────────────────────────────────────────────


def _modules() -> list[Path]:
    return sorted(_SRC.rglob("*.py"))


def _handlers(tree: ast.AST) -> list[ast.ExceptHandler]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]


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


def _except_types(handler: ast.ExceptHandler) -> set[str]:
    """The except-clause's type names, unwrapping a tuple into its elements."""
    t = handler.type
    if t is None:
        return {"bare"}
    if isinstance(t, ast.Tuple):
        return {ast.unparse(e) for e in t.elts}
    return {ast.unparse(t)}


def _is_bare_discard(handler: ast.ExceptHandler) -> str | None:
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


def _in_family(handler: ast.ExceptHandler) -> bool:
    """The cycle-55 family: a bare discard guarding a KeyError."""
    return _is_bare_discard(handler) is not None and FAMILY_TYPE in _except_types(handler)


def _names_a_logger(handler: ast.ExceptHandler) -> bool:
    for node in ast.walk(handler):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and getattr(func.value, "id", "") == "logger":
                return True
    return False


def _function(tree: ast.AST, name: str) -> ast.AST:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"{name} not found — re-measure")


def _debug_records(caplog, name: str) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == name and r.levelno == logging.DEBUG]


# ── the family rule ────────────────────────────────────────────────────────


def _family_sites() -> list[str]:
    found = []
    for path in _modules():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover - not expected in src/
            continue
        for handler in _handlers(tree):
            if _in_family(handler):
                found.append(f"{path.relative_to(_SRC).as_posix()}:{handler.lineno}")
    return found


def test_no_handler_skips_a_keyerror_in_silence() -> None:
    offenders = _family_sites()
    assert offenders == [], f"these handlers swallow a KeyError with a bare discard: {offenders} — name them"


def test_the_census_is_not_vacuous() -> None:
    """Floors are measurements, not round numbers.

    Re-measured 2026-10-08: 399 files / 1117 handlers (was 406 / 1121 on
    2026-10-06 -- the fall is the dead surfaces deleted by cycles 101-102).
    """
    files = _modules()
    total = sum(len(_handlers(ast.parse(p.read_text(encoding="utf-8")))) for p in files)
    assert len(files) >= 390, f"only {len(files)} modules scanned; the walk is not reaching src/"
    assert total >= 1100, f"only {total} handlers scanned; the walk is not reaching the handlers"


def test_the_detector_sees_the_family_and_not_its_siblings() -> None:
    """Detector self-test: fires on every discard shape and the tuple form, silent on neighbours."""
    tree = ast.parse(
        "def f():\n"
        "    for x in items:\n"
        "        try:\n"
        "            pass\n"
        "        except KeyError:\n"
        "            continue\n"  # in the family
        "        except KeyError:\n"
        "            pass\n"  # in the family (other shape)
        "        except (KeyError, ValueError):\n"
        "            pass\n"  # in the family (tuple)
        "        except KeyError:\n"
        "            logger.debug('named', exc_info=True)\n"  # named
        "        except KeyError:\n"
        "            logger.debug('named', exc_info=True)\n"
        "            pass\n"  # named + discard
        "        except ValueError:\n"
        "            pass\n"  # different type
    )
    hits = [h.lineno for h in _handlers(tree) if _in_family(h)]
    assert len(hits) == 3, f"the family detector fired {len(hits)} times, expected 3: {hits}"


def test_the_four_sites_still_name_their_failures() -> None:
    by_file: dict[str, ast.AST] = {}
    for (rel, func), (logger_name, expected_count) in _NAMED_SITES.items():
        if rel not in by_file:
            by_file[rel] = ast.parse((_SRC / rel).read_text(encoding="utf-8"))
        handlers = _own_handlers(_function(by_file[rel], func))
        where = f"{rel}::{func}"
        assert len(handlers) == expected_count, (
            f"{where} now has {len(handlers)} handlers, expected {expected_count} — re-measure"
        )
        family = [h for h in handlers if FAMILY_TYPE in _except_types(h)]
        assert family, f"{where} no longer has a {FAMILY_TYPE} handler — re-measure"
        for handler in family:
            assert _names_a_logger(handler), f"{where}:{handler.lineno} swallows a {FAMILY_TYPE} without a logger call"
        import importlib

        # The module is derived from the *path*; the logger name is independent of it
        # (`llm_config_routes.py` names its logger `aegis_ai.web.llm_config`).
        module_name = rel.removesuffix(".py").replace("/", ".")
        module = importlib.import_module(module_name)
        resolved = getattr(module, "logger", None)
        assert resolved is not None, f"{rel} has no module-level `logger`"
        assert resolved.name == logger_name, f"{rel}'s logger resolves to {resolved.name!r}"


def test_the_site_map_covers_four_functions_and_five_handlers() -> None:
    assert len(_NAMED_SITES) == 4
    assert sum(count for _logger, count in _NAMED_SITES.values()) == 5
    assert len({rel for rel, _fn in _NAMED_SITES}) == 3


def test_the_tuple_spelling_would_be_missed_by_a_single_name_compare() -> None:
    """The cycle-54 lesson, pinned where it bit: a tuple that *contains* the family type.

    ``PresentationManager.update`` is spelled ``except (ValueError, KeyError)``. A census that
    compared ``ast.unparse(handler.type) == "KeyError"`` reported 3 sites and never saw this one;
    the set-membership rule finds 4.
    """
    tree = ast.parse((_SRC / "aegis_ai/presentation/manager.py").read_text(encoding="utf-8"))
    handlers = [h for h in _own_handlers(_function(tree, "update")) if FAMILY_TYPE in _except_types(h)]
    assert len(handlers) == 1, f"expected the one importance handler, found {len(handlers)}"
    handler = handlers[0]
    assert _except_types(handler) == {"ValueError", "KeyError"}, _except_types(handler)
    assert ast.unparse(handler.type) != FAMILY_TYPE, (
        "the handler is no longer spelled as a tuple — this test no longer demonstrates the point"
    )
    assert _is_bare_discard(handler) is None, "the tuple handler is a bare discard again"
    assert _names_a_logger(handler), "the tuple handler stopped naming its failure"


# ── behavioural: TaskExecutionEngine._get_system_prompt ────────────────────────


class _RaisingRegistry:
    def render(self, prompt_id: str) -> str:
        raise KeyError(prompt_id)


class _OkRegistry:
    def render(self, prompt_id: str) -> str:
        return "SYSTEM"


def test_get_system_prompt_names_an_unknown_prompt(caplog) -> None:
    engine = object.__new__(TaskExecutionEngine)
    engine._prompt_registry = _RaisingRegistry()
    with caplog.at_level(logging.DEBUG, logger=_ENGINE):
        out = engine._get_system_prompt("typo'd-id", default="D")
    assert out == "D", "the unknown prompt no longer falls back to the default — re-measure"
    records = _debug_records(caplog, _ENGINE)
    assert len(records) == 1, f"the substituted default is silent again: {caplog.records}"
    assert "typo'd-id" in records[0].getMessage()
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_get_system_prompt_is_quiet_for_a_known_prompt(caplog) -> None:
    engine = object.__new__(TaskExecutionEngine)
    engine._prompt_registry = _OkRegistry()
    with caplog.at_level(logging.DEBUG, logger=_ENGINE):
        out = engine._get_system_prompt("known")
    assert out == "SYSTEM"
    assert _debug_records(caplog, _ENGINE) == [], "a resolvable prompt now logs"


# ── behavioural: TaskExecutionEngine._resolve_settings ─────────────────────────


class _RaisingResolver:
    def resolve(self, *, profile_id: str) -> Any:
        raise KeyError(profile_id)


class _OkResolver:
    def resolve(self, *, profile_id: str) -> Any:
        return type("S", (), {"max_tokens": 1, "temperature": 0.0})()


def test_resolve_settings_names_an_unknown_profile(caplog) -> None:
    engine = object.__new__(TaskExecutionEngine)
    engine._settings_resolver = _RaisingResolver()
    with caplog.at_level(logging.DEBUG, logger=_ENGINE):
        settings = engine._resolve_settings("typo'd-profile")
    assert settings.max_tokens == 2048, "the unknown profile no longer falls back — re-measure"
    records = _debug_records(caplog, _ENGINE)
    assert len(records) == 1, f"the built-in defaults are silent again: {caplog.records}"
    assert "typo'd-profile" in records[0].getMessage()
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_resolve_settings_is_quiet_for_a_known_profile(caplog) -> None:
    engine = object.__new__(TaskExecutionEngine)
    engine._settings_resolver = _OkResolver()
    with caplog.at_level(logging.DEBUG, logger=_ENGINE):
        settings = engine._resolve_settings("known")
    assert settings.max_tokens == 1
    assert _debug_records(caplog, _ENGINE) == [], "a resolvable profile now logs"


# ── behavioural: PresentationManager.update ────────────────────────────────


class _Spec:
    def __init__(self) -> None:
        self.title = "t"
        self.summary = "s"
        self.content = "c"
        self.importance = "NORMAL"
        self.revision = 0
        self.updated_at_ms = 0

    def to_dict(self) -> dict[str, Any]:
        return {"importance": self.importance, "revision": self.revision}


class _Store:
    def __init__(self, spec: _Spec) -> None:
        self._spec = spec

    def get(self, presentation_id: str) -> _Spec:
        return self._spec

    def put(self, spec: _Spec) -> None:
        pass


def _manager_with(spec: _Spec) -> PresentationManager:
    manager = object.__new__(PresentationManager)
    manager._store = _Store(spec)
    manager._publish_event = lambda *a, **k: None
    return manager


def test_update_names_an_invalid_importance(caplog) -> None:
    spec = _Spec()
    manager = _manager_with(spec)
    with caplog.at_level(logging.DEBUG, logger=_PRESENTATION):
        result = manager.update("p1", {"importance": "not-a-level"})
    assert result["ok"] is True, "the response no longer claims success — re-measure the premise"
    assert spec.importance == "NORMAL", "the invalid importance no longer leaves the field unchanged"
    records = _debug_records(caplog, _PRESENTATION)
    assert len(records) == 1, f"the ignored importance is silent again: {caplog.records}"
    assert "not-a-level" in records[0].getMessage()
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_update_is_quiet_for_a_valid_importance(caplog) -> None:
    spec = _Spec()
    manager = _manager_with(spec)
    with caplog.at_level(logging.DEBUG, logger=_PRESENTATION):
        result = manager.update("p1", {"importance": "high"})
    assert result["ok"] is True
    assert spec.importance is not None and str(spec.importance) != "NORMAL", (
        "a valid importance no longer replaces the field"
    )
    assert _debug_records(caplog, _PRESENTATION) == [], "a valid importance now logs"


def test_the_record_detector_is_not_vacuous(caplog) -> None:
    caplog.set_level(logging.DEBUG, logger=_ENGINE)
    logging.getLogger(_ENGINE).debug("control")
    assert len(_debug_records(caplog, _ENGINE)) == 1, (
        "the record detector is blind; every 'is quiet' assertion above proves nothing"
    )
