"""Cycle 14 pin: the four swallowed failures in ``AutonomousLoop`` are named.

Measured 2026-10-04 (HEAD 3a25495). The class turned four *failures* into an *absence*
or a *default*, none of them logged, so each one was indistinguishable from a positive
fact:

- ``_priority_obligations``  -> ``[]``   : reads as "every duty is already resolved"
- ``_current_interruption_cost`` -> ``0.15`` : the *same* value as the "no AgentState"
  default, so "read failed" and "no state wired" were one value
- ``_manifest_for``          -> ``None`` : reads as "capability absent"
- ``_load_recent_history``   -> ``[]``   : the caller renders this as the literal string
  ``"Autonomous execution history: no actions executed yet. First run."`` and injects it
  into the planning LLM's context; ``_burden_activity`` reports the period as empty and
  ``_recent_capability_ids`` reports no recent capabilities

The *return values are unchanged* by the fix -- this pin therefore fixes behaviour that
already existed and may not move. Two sibling handlers stay silent on purpose and are
allow-listed below: ``_call_propose_candidates_llm`` degrades malformed LLM JSON to
``{"candidates": [], "no_action_reason": <raw content>}`` (the reason is preserved, so it
is not silent) and ``_sanitize_for_execution_log`` is a masking layer, not a data read.
"""

from __future__ import annotations

import ast
import logging
import types
from pathlib import Path

import pytest

_AI_SERVER = Path(__file__).resolve().parents[1]
_MODULE = _AI_SERVER / "src" / "aegis_ai" / "autonomous" / "autonomous_loop.py"
_LOGGER = "aegis_ai.autonomous.autonomous_loop"

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop

# Handlers that are a single bare `return <constant/empty>` or `pass` and are *intentional*.
_ALLOWED_SILENT = {"_call_propose_candidates_llm", "_sanitize_for_execution_log"}

# The four sites this cycle named: method -> a distinctive phrase from its record.
_NAMED = {
    "_priority_obligations": "treats every duty as already resolved",
    "_current_interruption_cost": "assumed mid-range rather than unknown",
    "_manifest_for": "_is_inventory_capability -> False",
    "_load_recent_history": "no recent capabilities",
}


class _RaisingState:
    """An AgentState whose every read fails."""

    def snapshot(self, *_a, **_k):
        raise RuntimeError("agent state unavailable")


class _RaisingCatalog:
    """A capability catalog whose every resolve fails."""

    def resolve(self, *_a, **_k):
        raise RuntimeError("catalog unavailable")


def _bare() -> AutonomousLoop:
    """An instance without running the heavy ``__init__`` (the sites need 1-2 attributes)."""
    return object.__new__(AutonomousLoop)


def _warnings(caplog) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == _LOGGER and r.levelno >= logging.WARNING]


# --------------------------------------------------------------------------- run pins


@pytest.mark.parametrize("label", sorted(_NAMED))
def test_a_swallowed_failure_is_named(label: str, caplog, tmp_path) -> None:
    loop = _bare()
    if label == "_priority_obligations":
        loop._agent_state = _RaisingState()
        with caplog.at_level(logging.WARNING, logger=_LOGGER):
            result = loop._priority_obligations()
        assert result == []  # the pre-existing return value must not move
    elif label == "_current_interruption_cost":
        loop._agent_state = _RaisingState()
        with caplog.at_level(logging.WARNING, logger=_LOGGER):
            result = loop._current_interruption_cost()
        assert result == 0.15
    elif label == "_manifest_for":
        loop._broker = types.SimpleNamespace(_catalog=_RaisingCatalog())
        with caplog.at_level(logging.WARNING, logger=_LOGGER):
            result = loop._manifest_for("capability.that.does.not.matter")
        assert result is None
    else:
        loop._data_dir = tmp_path
        (tmp_path / "execution_log.jsonl").write_text("{not json}\n", encoding="utf-8")
        with caplog.at_level(logging.WARNING, logger=_LOGGER):
            result = loop._load_recent_history()
        assert result == []

    records = _warnings(caplog)
    assert records, f"{label}: a swallowed failure emitted no warning"
    assert any(_NAMED[label] in r.getMessage() for r in records), (
        f"{label}: no record carried the consequence phrase {_NAMED[label]!r}; got "
        f"{[r.getMessage() for r in records]}"
    )
    assert any(
        "RuntimeError" in r.getMessage() or "JSONDecodeError" in r.getMessage() for r in records
    ), f"{label}: no record named the exception type; got {[r.getMessage() for r in records]}"


def test_a_legitimate_absence_stays_silent(caplog, tmp_path) -> None:
    """The control: absence of *input* is not a failure and must not warn."""
    loop = _bare()
    # ``_capability_catalog`` reads ``self._broker`` directly (no ``getattr`` default),
    # so a real instance always carries these two attributes -- match production.
    loop._agent_state = None
    loop._broker = None
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        assert loop._priority_obligations() == []  # no AgentState wired at all
        assert loop._current_interruption_cost() == 0.15  # ditto
        assert loop._manifest_for("x") is None  # no broker at all
        loop._data_dir = tmp_path  # the log file was never written
        assert loop._load_recent_history() == []
    assert not _warnings(caplog), [r.getMessage() for r in _warnings(caplog)]


# ---------------------------------------------------------------------- structural pin


def _handlers_by_method() -> dict[str, list[ast.ExceptHandler]]:
    tree = ast.parse(_MODULE.read_text(encoding="utf-8"))
    cls = next(
        n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "AutonomousLoop"
    )
    out: dict[str, list[ast.ExceptHandler]] = {}
    for fn in cls.body:
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        hs = [h for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler)]
        if hs:
            out[fn.name] = hs
    return out


def test_no_silent_handler_remains_outside_the_allow_list() -> None:
    found: set[str] = set()
    total = 0
    for method, handlers in _handlers_by_method().items():
        for handler in handlers:
            body = handler.body
            if len(body) != 1:
                continue
            stmt = body[0]
            silent = isinstance(stmt, ast.Pass) or (
                isinstance(stmt, ast.Return)
                and isinstance(stmt.value, (ast.Constant, ast.List, ast.Dict, ast.Tuple))
            )
            if silent:
                found.add(method)
                total += 1
    # Non-vacuity: the scan must be finding the handlers it knows about.
    assert total >= 3, f"the scan found only {total} silent handlers; it is not measuring"
    assert found == _ALLOWED_SILENT, (
        f"a swallowed failure is silent again: {sorted(found - _ALLOWED_SILENT)}"
    )


def test_the_four_named_sites_do_warn() -> None:
    """Guards against the cycle-13 self-error: a bare ``logger.warning(...)`` *is* an
    ``ast.Expr``, so filtering ``ast.Expr`` out before asking 'is this body silent?'
    reports every named handler as silent."""
    handlers = _handlers_by_method()
    for method in _NAMED:
        assert method in handlers, f"{method}: no except handler found at all"
        for handler in handlers[method]:
            warns = [
                s
                for s in handler.body
                if isinstance(s, ast.Expr)
                and isinstance(s.value, ast.Call)
                and getattr(s.value.func, "attr", "") == "warning"
            ]
            assert warns, f"{method}: an except handler still has no logger.warning"
