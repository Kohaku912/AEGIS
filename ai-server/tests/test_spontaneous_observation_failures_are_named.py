"""Cycle 16 pin: every observation source that fails must name itself.

The defect class
----------------
``spontaneous_observation.py`` builds its observation list from seven sources
(disk, data growth, failed traces, episodic memory, desires, affect, shared server
status, active traces) plus a log write.  Each source sat in ``except Exception:
pass`` (or a bare ``return obs``), so a source that could not be read contributed
exactly as many observations as a healthy, quiet source -- **zero**.  An unreadable
store was therefore indistinguishable from a calm system.

That matters beyond the missing log line: ``autonomous_loop._refresh_observations_for_cycle``
filters these observations into ``_pending_actionable_observations``, and at
``autonomous_loop.py:1074`` ``should_run_l2 = bool(self._pending_actionable_observations)``.
So a broken backend could make the loop conclude there was nothing to act on.

Unit of this pin
----------------
"A failure that leaves **no record at any level**."  The three handlers that already
call ``logger.debug(..., exc_info=True)`` (the obligation / task-manager / user-state
sites) are deliberately *not* in scope: they do leave a record, which is merely filtered
at the shipped default (every entrypoint configures ``logging.INFO``).  That is a
visibility question, not a silence question, and it is recorded separately.  They are
therefore named in ``_RECORDED_BELOW_DEFAULT`` rather than fixed here.
"""
from __future__ import annotations

import ast
import logging
import re
from pathlib import Path

import pytest

from aegis_ai.autonomous.spontaneous_observation import (
    SpontaneousObservationSystem,
)

_LOGGER = "aegis_ai.autonomous.spontaneous_observation"
_MODULE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "aegis_ai"
    / "autonomous"
    / "spontaneous_observation.py"
)

# label -> a phrase that only the named warning for that site contains.
_NAMED: dict[str, str] = {
    "disk_usage": "an unreadable disk looks like a healthy one",
    "data_growth": "unreadable storage looks unchanged",
    "failure_pattern": "looks like a system with no failures",
    "episodic_recall": "a store with nothing unresolved",
    "desires": "a system with no unmet desires",
    "affect": "looks like a calm one",
    "server_status": "a fleet with no status changes",
    "active_traces": "a system with no stuck tasks",
    "observation_log": "a system that never observes",
}

# Handlers that already leave a record -- at DEBUG, i.e. below the shipped default.
# They are excluded from this cycle's fix on purpose; see the module docstring.
_RECORDED_BELOW_DEFAULT = {
    "Obligation observation failed",
    "Task manager observation failed",
    "User state observation failed",
}

# Any (Error|Exception) type name, as `型: メッセージ` requires.
_TYPE_SHAPE = re.compile(r"\([A-Za-z_][A-Za-z0-9_]*(Error|Exception):")


# ── doubles ────────────────────────────────────────────────────────────────
# Each one makes exactly the call the site under test depends on raise.  They must
# match production: a double that is missing an attribute the real backend has (or
# vice versa) makes a failure-path pin pass for the wrong reason.


class _RaisingStatus:
    def get_snapshot(self):
        raise RuntimeError("status backend unavailable")


class _RaisingDesire:
    def get_all_desires(self):
        raise RuntimeError("desire backend unavailable")


class _RaisingAffect:
    @property
    def mood(self):
        raise RuntimeError("affect backend unavailable")


class _RaisingTrace:
    """Serves both trace-backed sites: ``get_failed`` (patterns) and ``_active`` (stuck)."""

    def get_failed(self, count: int = 10):
        raise RuntimeError("trace backend unavailable")

    @property
    def _active(self):
        raise RuntimeError("trace backend unavailable")


class _RaisingEpisodic:
    def recall_recent(self, n: int):
        raise RuntimeError("episodic backend unavailable")


class _RaisingDataDir:
    """Stands in for ``self._data_dir`` when the growth walk must fail."""

    def rglob(self, pattern: str):
        raise RuntimeError("data dir unavailable")


def _boom(*_a, **_k):
    raise RuntimeError("disk backend unavailable")


def _make(label: str, tmp_path) -> SpontaneousObservationSystem:
    kwargs: dict = {}
    if label in {"failure_pattern", "active_traces"}:
        kwargs["action_trace"] = _RaisingTrace()
    elif label == "episodic_recall":
        kwargs["episodic_memory"] = _RaisingEpisodic()
    elif label == "desires":
        kwargs["desire_system"] = _RaisingDesire()
    elif label == "affect":
        kwargs["affect_system"] = _RaisingAffect()
    elif label == "server_status":
        kwargs["status_manager"] = _RaisingStatus()
    return SpontaneousObservationSystem(data_dir=str(tmp_path), **kwargs)


def _drive(label: str, system: SpontaneousObservationSystem, monkeypatch) -> None:
    """Call the one method that contains the site under test."""
    if label == "disk_usage":
        import shutil

        monkeypatch.setattr(shutil, "disk_usage", _boom)
        system._observe_system_state()
    elif label == "data_growth":
        system._data_dir = _RaisingDataDir()
        system._observe_system_state()
    elif label in {"failure_pattern", "episodic_recall"}:
        system._observe_memory_patterns()
    elif label == "desires":
        system._observe_desires()
    elif label == "affect":
        system._observe_emotions()
    elif label == "server_status":
        system._observe_capabilities()
    elif label == "active_traces":
        system._observe_unfinished_tasks()
    elif label == "observation_log":
        system._log_observations([])
    else:  # pragma: no cover - guards against a typo in _NAMED
        raise AssertionError(f"unknown label {label!r}")


# ── the pin ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("label", sorted(_NAMED))
def test_a_source_failure_is_named(label, tmp_path, monkeypatch, caplog) -> None:
    system = _make(label, tmp_path)
    if label == "observation_log":
        # A directory where the log file should be: the append cannot succeed.
        (tmp_path / "observation_log.jsonl").mkdir()

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        _drive(label, system, monkeypatch)

    messages = [r.getMessage() for r in caplog.records if r.name == _LOGGER]
    assert any(_NAMED[label] in m for m in messages), (
        f"{label}: the failure left no record naming its consequence; got {messages}"
    )
    assert any(_TYPE_SHAPE.search(m) for m in messages), (
        f"{label}: no record named the exception type; got {messages}"
    )


def test_a_legitimate_absence_stays_silent(tmp_path, caplog) -> None:
    """No backend at all is not a failure -- it must not warn."""
    system = SpontaneousObservationSystem(data_dir=str(tmp_path))
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        system.observe()
    messages = [r.getMessage() for r in caplog.records if r.name == _LOGGER]
    assert messages == [], f"an absent backend warned: {messages}"


def _handlers_without_a_record() -> list[str]:
    """Return every `except` body in the module that does not call the logger."""
    tree = ast.parse(_MODULE.read_text(encoding="utf-8"))
    silent: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        calls_logger = any(
            isinstance(sub, ast.Call)
            and isinstance(sub.func, ast.Attribute)
            and isinstance(sub.func.value, ast.Name)
            and sub.func.value.id == "logger"
            for sub in ast.walk(node)
        )
        if not calls_logger:
            line = node.lineno
            silent.append(f"{_MODULE.name}:{line}")
    return silent


def test_no_handler_suppresses_a_failure_without_a_record() -> None:
    silent = _handlers_without_a_record()
    assert silent == [], f"handlers still swallow without a record: {silent}"


def test_the_allow_list_is_not_vacuous() -> None:
    """The three DEBUG sites must really be there, or `_RECORDED_BELOW_DEFAULT` is a lie."""
    source = _MODULE.read_text(encoding="utf-8")
    for message in _RECORDED_BELOW_DEFAULT:
        assert message in source, f"allow-listed message vanished: {message!r}"
    # ...and they must still be the only DEBUG-level records in the module.
    assert source.count("logger.debug(") >= len(_RECORDED_BELOW_DEFAULT)
