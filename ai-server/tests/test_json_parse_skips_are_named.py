"""Cycle 54 pin: a JSON-parse failure is never skipped in silence.

Measured 2026-10-06 (HEAD 122b0fa). The unit is again a *family defined by its exception
type* — the same boundary cycles 43-53 used: **a handler whose whole body is ``pass``,
``continue`` or ``break`` and whose except-type contains ``json.JSONDecodeError``**. Repo-wide
there were **4 such handlers in 3 modules**, and three of them silently changed a *result*:

* ``agents/runtime/session_store.SessionStore._summary_for`` — a corrupt line is dropped from
  the session summary, so ``event_count`` **and** the time span are under-reported. A session
  that looks shorter than it was is indistinguishable from one that really is short.
* ``llm/prompt_registry.PromptRegistry.list_versions`` — a dropped revision is missing from
  the version list, so a **rollback target can appear not to exist** (``rollback_prompt``
  looks the revision up in exactly this list and raises ``KeyError`` when it is absent).
* ``web/chat_tools._parse_tool_call`` — **two** handlers. The ``continue`` in the match loop
  drops a candidate the model emitted, so a tool call the LLM *did* produce is never run; the
  ``pass`` in the fallback branch drops a brace-delimited block. This second one is why the
  cycle exists: a **``pass``-census scoped per-package cannot see a ``pass`` that sits in the
  same function as a ``continue``** — the earlier ``web/`` scans keyed on ``continue``, and the
  ``audit/``/``memory/`` scans never looked in ``web/``. The two live five lines apart.

The discriminator is *structural*, not textual: a discard **inside an except-handler** swallows
a failure; a ``continue`` beside it (``if valid_tool_names and tag_name not in valid_tool_names:
continue``) is an ordinary filter and is deliberately **not** touched. The rule below therefore
keys on the *handler*, never on the statement.

A legitimate neighbour is left alone on purpose: ``operations/store.OperationStore._load``
catches ``json.JSONDecodeError`` and *counts* the drop (``dropped += 1``) before ``continue``,
then reports the total once (``logger.warning("Skipped %d unreadable line(s)…")``). That body is
**not** a bare discard, so the rule does not fire — and the drop is loud, aggregately. The
aggregate form is pinned by behaviour below so a future edit cannot quietly delete the warning.

Behaviour is unchanged — each site gains one DEBUG record with ``exc_info``.
"""

from __future__ import annotations

import ast
import importlib
import json
import logging
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"

_SESSION_STORE = "aegis_ai.agents.runtime.session_store"
_PROMPT_REGISTRY = "aegis_ai.llm.prompt_registry"
_CHAT_TOOLS = "aegis_ai.web.chat_tools"
_OPERATIONS = "aegis_ai.operations.store"

# The family type. ``json.JSONDecodeError`` subclasses ``ValueError``, so a handler written as
# a tuple containing it (``except (json.JSONDecodeError, ValueError)``) is in the family too.
FAMILY_TYPE = "json.JSONDecodeError"

# (path relative to src/, enclosing function) -> (logger name, handler count measured 2026-10-06)
_NAMED_SITES: dict[tuple[str, str], tuple[str, int]] = {
    ("aegis_ai/agents/runtime/session_store.py", "_summary_for"): (_SESSION_STORE, 1),
    ("aegis_ai/llm/prompt_registry.py", "list_versions"): (_PROMPT_REGISTRY, 1),
    ("aegis_ai/web/chat_tools.py", "_parse_tool_call"): (_CHAT_TOOLS, 2),
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
    """Return 'pass'/'continue'/'break' if the body is exactly one such statement."""
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
    """The cycle-54 family: a bare discard guarding a JSON-parse failure."""
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
    """Only DEBUG records on ``name``.

    ``prompt_registry`` also logs an INFO ``"Loaded %s prompts"`` on the same logger, so a
    level-blind filter would let an "is quiet" assertion pass for the wrong reason.
    """
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


def test_no_handler_skips_a_json_parse_failure_in_silence() -> None:
    offenders = _family_sites()
    assert offenders == [], (
        f"these handlers swallow a json.JSONDecodeError with a bare discard: {offenders} — name them with a logger call"
    )


def test_the_census_is_not_vacuous() -> None:
    """Floors are measurements, not round numbers (measured 2026-10-06: 406 files / 1121 handlers)."""
    files = _modules()
    total = sum(len(_handlers(ast.parse(p.read_text(encoding="utf-8")))) for p in files)
    assert len(files) >= 400, f"only {len(files)} modules scanned; the walk is not reaching src/"
    assert total >= 1100, f"only {total} handlers scanned; the walk is not reaching the handlers"


def test_the_detector_sees_the_family_and_not_its_siblings() -> None:
    """Detector self-test: the rule must fire on every discard shape and stay silent on neighbours."""
    tree = ast.parse(
        "def f():\n"
        "    for x in items:\n"
        "        try:\n"
        "            pass\n"
        "        except json.JSONDecodeError:\n"
        "            continue\n"  # in the family
        "        except json.JSONDecodeError:\n"
        "            pass\n"  # in the family (other shape)
        "        except json.JSONDecodeError:\n"
        "            break\n"  # in the family (other shape)
        "        except (json.JSONDecodeError, ValueError):\n"
        "            continue\n"  # in the family (tuple)
        "        except json.JSONDecodeError:\n"
        "            logger.debug('named', exc_info=True)\n"  # named
        "        except json.JSONDecodeError:\n"
        "            logger.debug('named', exc_info=True)\n"
        "            continue\n"  # named + discard
        "        except ValueError:\n"
        "            continue\n"  # different type
    )
    hits = [h.lineno for h in _handlers(tree) if _in_family(h)]
    assert len(hits) == 4, f"the family detector fired {len(hits)} times, expected 4: {hits}"


def test_the_discard_detector_sees_every_shape() -> None:
    """``_is_bare_discard`` must accept all three silent shapes and reject an action."""
    tree = ast.parse(
        "def f():\n"
        "    try:\n"
        "        pass\n"
        "    except Exception:\n"
        "        pass\n"
        "    except Exception:\n"
        "        continue\n"
        "    except Exception:\n"
        "        break\n"
        "    except Exception:\n"
        "        return 1\n"
        "    except Exception:\n"
        "        logger.debug('x')\n"
    )
    shapes = [_is_bare_discard(h) for h in _handlers(tree)]
    assert shapes == ["pass", "continue", "break", None, None], shapes


def test_the_three_sites_still_name_their_failures() -> None:
    by_file: dict[str, ast.AST] = {}
    for (rel, func), (logger_name, expected_count) in _NAMED_SITES.items():
        if rel not in by_file:
            by_file[rel] = ast.parse((_SRC / rel).read_text(encoding="utf-8"))
        handlers = _own_handlers(_function(by_file[rel], func))
        where = f"{rel}::{func}"
        assert len(handlers) == expected_count, (
            f"{where} now has {len(handlers)} handlers, expected {expected_count} — re-measure "
            "and update the pin rather than the count"
        )
        family = [h for h in handlers if FAMILY_TYPE in _except_types(h)]
        assert family, f"{where} no longer has a {FAMILY_TYPE} handler — re-measure"
        for handler in family:
            assert _names_a_logger(handler), f"{where}:{handler.lineno} swallows a {FAMILY_TYPE} without a logger call"
        # Measure the *resolved* logger name, not the literal: prompt_registry uses
        # ``logging.getLogger(__name__)``, so its name never appears as a string in the file.
        module = importlib.import_module(logger_name)
        resolved = getattr(module, "logger", None)
        assert resolved is not None, f"{rel} has no module-level `logger`"
        assert resolved.name == logger_name, (
            f"{rel}'s logger resolves to {resolved.name!r}, not {logger_name!r} — the records "
            "will land on a different channel than this pin filters for"
        )


def test_the_site_map_covers_exactly_four_handlers_in_three_modules() -> None:
    assert len(_NAMED_SITES) == 3
    assert sum(count for _logger, count in _NAMED_SITES.values()) == 4
    assert len({rel for rel, _fn in _NAMED_SITES}) == 3


def test_both_chat_tools_handlers_are_named() -> None:
    """The pin's reason for existing: the ``pass`` and the ``continue`` five lines apart."""
    tree = ast.parse((_SRC / "aegis_ai/web/chat_tools.py").read_text(encoding="utf-8"))
    handlers = [h for h in _own_handlers(_function(tree, "_parse_tool_call")) if FAMILY_TYPE in _except_types(h)]
    assert len(handlers) == 2, f"expected the two JSON handlers, found {len(handlers)} — re-measure"
    shapes = sorted(_is_bare_discard(h) or "named" for h in handlers)
    assert shapes == ["named", "named"], f"one of the two _parse_tool_call handlers is a bare discard again: {shapes}"


# ── the legitimate neighbour: an aggregate count is loud ───────────────────


def test_the_aggregate_sibling_is_left_alone() -> None:
    """``operations/store._load`` counts drops and reports the total — not a bare discard."""
    rel = "aegis_ai/operations/store.py"
    tree = ast.parse((_SRC / rel).read_text(encoding="utf-8"))
    handlers = [h for h in _own_handlers(_function(tree, "_load")) if FAMILY_TYPE in _except_types(h)]
    assert handlers, "operations/store._load no longer handles a JSON parse failure — re-measure"
    for handler in handlers:
        assert _is_bare_discard(handler) is None, (
            "the aggregate counter was replaced by a bare discard — the drop is now silent"
        )
    assert "Skipped %d unreadable line(s)" in (_SRC / rel).read_text(encoding="utf-8"), (
        "the aggregate warning that makes the drop loud was removed"
    )


def test_the_aggregate_sibling_still_reports_its_drops(tmp_path, caplog) -> None:
    from aegis_ai.operations.store import OperationStore

    (tmp_path / "operations").mkdir()
    (tmp_path / "operations" / "operations.jsonl").write_text('{"a": 1}\nnot json\n', encoding="utf-8")
    with caplog.at_level(logging.WARNING, logger=_OPERATIONS):
        OperationStore(tmp_path)
    warnings = [r for r in caplog.records if r.name == _OPERATIONS and r.levelno == logging.WARNING]
    assert len(warnings) == 1, f"the dropped line is silent again: {caplog.records}"
    assert "Skipped 1 unreadable line(s)" in warnings[0].getMessage()


# ── behavioural: session_store._summary_for ────────────────────────────────


def test_summary_for_names_a_session_event_it_could_not_parse(tmp_path, caplog) -> None:
    from aegis_ai.agents.runtime.session_store import SessionStore

    store = SessionStore(tmp_path)
    path = tmp_path / "s1.jsonl"
    path.write_text('{"ts_ms": 1000, "kind": "a"}\n{ not json\n{"ts_ms": 2000, "kind": "b"}\n', encoding="utf-8")
    with caplog.at_level(logging.DEBUG, logger=_SESSION_STORE):
        summary = store._summary_for(path)
    assert summary.event_count == 2, f"the corrupt line is no longer dropped: {summary.event_count}"
    assert summary.last_event_ms == 2000
    records = _debug_records(caplog, _SESSION_STORE)
    assert len(records) == 1, f"the dropped event is silent again: {caplog.records}"
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_summary_for_is_quiet_for_a_well_formed_file(tmp_path, caplog) -> None:
    from aegis_ai.agents.runtime.session_store import SessionStore

    store = SessionStore(tmp_path)
    path = tmp_path / "s2.jsonl"
    path.write_text('{"ts_ms": 1000, "kind": "a"}\n{"ts_ms": 2000, "kind": "b"}\n', encoding="utf-8")
    with caplog.at_level(logging.DEBUG, logger=_SESSION_STORE):
        summary = store._summary_for(path)
    assert summary.event_count == 2
    assert _debug_records(caplog, _SESSION_STORE) == [], "a healthy session file now logs"


# ── behavioural: prompt_registry.list_versions ─────────────────────────────


def _registry(tmp_path, prompt_id: str = "greeting"):
    from aegis_ai.llm.prompt_registry import PromptRegistry

    path = tmp_path / "prompts.yaml"
    path.write_text(
        'version: "1.0.0"\n'
        "prompts:\n"
        f"  {prompt_id}:\n"
        '    template: "Hello {{name}}"\n'
        '    version: "1"\n'
        "    editable: true\n"
        "    protected: false\n",
        encoding="utf-8",
    )
    return PromptRegistry(str(path))


def test_list_versions_names_a_revision_it_could_not_parse(tmp_path, caplog) -> None:
    registry = _registry(tmp_path)
    registry._history_path.write_text(
        json.dumps({"prompt_id": "greeting", "created_at": 1, "revision_id": "r1"}) + "\n"
        "{ not json\n" + json.dumps({"prompt_id": "greeting", "created_at": 2, "revision_id": "r2"}) + "\n",
        encoding="utf-8",
    )
    with caplog.at_level(logging.DEBUG, logger=_PROMPT_REGISTRY):
        versions = registry.list_versions("greeting")
    assert [v["revision_id"] for v in versions] == ["r2", "r1"], versions
    records = _debug_records(caplog, _PROMPT_REGISTRY)
    assert len(records) == 1, f"the dropped revision is silent again: {caplog.records}"
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_list_versions_is_quiet_for_a_well_formed_history(tmp_path, caplog) -> None:
    registry = _registry(tmp_path)
    registry._history_path.write_text(
        json.dumps({"prompt_id": "greeting", "created_at": 1, "revision_id": "r1"}) + "\n", encoding="utf-8"
    )
    with caplog.at_level(logging.DEBUG, logger=_PROMPT_REGISTRY):
        versions = registry.list_versions("greeting")
    assert [v["revision_id"] for v in versions] == ["r1"]
    assert _debug_records(caplog, _PROMPT_REGISTRY) == [], "a healthy history now logs"


# ── behavioural: chat_tools._parse_tool_call ───────────────────────────────


def test_parse_tool_call_names_a_block_it_could_not_parse(caplog) -> None:
    """The fallback branch (the ``pass`` at 694, invisible to every per-package census)."""
    from aegis_ai.web.chat_tools import _parse_tool_call

    with caplog.at_level(logging.DEBUG, logger=_CHAT_TOOLS):
        result = _parse_tool_call("{ not valid json")
    assert result is None, "a malformed brace-block is no longer rejected — re-measure"
    records = _debug_records(caplog, _CHAT_TOOLS)
    assert len(records) == 1, f"the malformed block is silent again: {caplog.records}"
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_parse_tool_call_names_a_match_it_could_not_parse(caplog) -> None:
    """The match loop (the ``continue`` at 709)."""
    from aegis_ai.web.chat_tools import _parse_tool_call

    with caplog.at_level(logging.DEBUG, logger=_CHAT_TOOLS):
        result = _parse_tool_call("<tool_call>not json</tool_call>")
    assert result is None, "a malformed tool_call block is no longer rejected — re-measure"
    records = _debug_records(caplog, _CHAT_TOOLS)
    assert len(records) == 1, f"the malformed match is silent again: {caplog.records}"
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_parse_tool_call_is_quiet_for_a_well_formed_call(caplog) -> None:
    from aegis_ai.web.chat_tools import _parse_tool_call

    content = '<tool_call>{"name": "ai-server__ping", "arguments": {"x": 1}}</tool_call>'
    with caplog.at_level(logging.DEBUG, logger=_CHAT_TOOLS):
        result = _parse_tool_call(content, {"ai-server__ping"})
    assert result == {"name": "ai-server__ping", "arguments": {"x": 1}}, result
    assert _debug_records(caplog, _CHAT_TOOLS) == [], "a healthy tool call now logs"


def test_the_record_detector_is_not_vacuous(caplog) -> None:
    caplog.set_level(logging.DEBUG, logger=_CHAT_TOOLS)
    logging.getLogger(_CHAT_TOOLS).debug("control")
    assert len(_debug_records(caplog, _CHAT_TOOLS)) == 1, (
        "the record detector is blind; every 'is quiet' assertion above proves nothing"
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
