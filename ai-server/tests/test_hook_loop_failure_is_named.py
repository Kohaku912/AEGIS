"""The hook loop's backstop must name the exception *type*.

``HookEngine._loop`` wraps ``run_due_once()`` in a ``try``. ``run_due_once`` is
not expected to raise, so that ``except`` is the backstop -- and its record is
the *only* signal: ``audit_decision`` writes at **DEBUG** and returns silently
when there is no audit manager. Before cycle 120 it recorded ``str(exc)``, so
``ValueError("boom")`` and ``KeyError("boom")`` left the identical record.

This is the same defect class cycle 119 fixed in ``EventBus._notify_subscribers``
(the background L1 route's only failure signal), found by censusing the
``str(exc)`` sites for ones that are a *failure record* rather than an API
payload.

These tests drive the real ``_loop`` on its own thread. The fake ``run_due_once``
raises once and sets ``_stop``, so the loop exits after exactly one tick.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

_LOGGER = "aegis_ai.personal_ai.hooks"


class _Recorder:
    """Stands in for ``AuditManager``; captures what the engine audits."""

    def __init__(self) -> None:
        self.actions: list[tuple[str, dict[str, Any]]] = []

    def log_decision(self, **kwargs: Any) -> None:
        self.actions.append((str(kwargs.get("action", "")), dict(kwargs.get("detail") or {})))


def _drive(data_dir: Path, recorder: _Recorder, exc: BaseException) -> None:
    """Run one tick of the real hook loop with ``run_due_once`` raising ``exc``."""
    from aegis_ai.personal_ai.hooks import HookEngine

    os.makedirs(data_dir, exist_ok=True)
    engine = HookEngine(
        data_dir=str(data_dir), audit_manager=recorder, poll_interval_seconds=1
    )

    def _boom() -> None:
        engine._stop.set()  # exit the loop after this one tick
        raise exc

    setattr(engine, "run_due_once", _boom)
    engine.start()
    engine._thread.join(timeout=5)
    assert not engine._thread.is_alive(), "the hook loop did not exit"


def test_the_backstop_record_carries_the_exception_type(tmp_path: Path) -> None:
    recorder = _Recorder()
    _drive(tmp_path, recorder, ValueError("hook payload malformed"))

    assert recorder.actions, "the backstop recorded nothing"
    action, detail = recorder.actions[-1]
    assert action == "hook_tick_failed", action
    assert "ValueError" in detail["error"], detail
    assert "hook payload malformed" in detail["error"], detail


def test_two_exception_types_leave_two_different_records(tmp_path: Path) -> None:
    """Control: the record depends on the *type*, so it is not a fixed string."""
    key_recorder, value_recorder = _Recorder(), _Recorder()
    _drive(tmp_path / "key", key_recorder, KeyError("payload"))
    _drive(tmp_path / "value", value_recorder, ValueError("payload"))

    key = key_recorder.actions[-1][1]["error"]
    value = value_recorder.actions[-1][1]["error"]
    assert key != value, (key, value)
    assert "KeyError" in key, key
    assert "ValueError" in value, value


def test_the_backstop_failure_is_logged_at_error_with_a_traceback(
    tmp_path: Path, caplog: Any
) -> None:
    recorder = _Recorder()
    with caplog.at_level(logging.ERROR, logger=_LOGGER):
        _drive(tmp_path, recorder, RuntimeError("kaboom"))

    errors = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert errors, caplog.records
    assert "RuntimeError" in errors[0].getMessage(), errors[0].getMessage()
    # ``LogRecord.exc_info`` is ``False`` -- not ``None`` -- when ``exc_info`` is
    # off, so the check must be truthiness (cycle 119's harness lesson).
    assert errors[0].exc_info, "the traceback must be attached"
    assert errors[0].exc_info[0] is RuntimeError


def test_the_engine_still_runs_its_loop() -> None:
    """Control for the harness: the loop is reachable, not a no-op."""
    from aegis_ai.personal_ai.hooks import HookEngine

    assert isinstance(getattr(HookEngine, "_loop"), Callable)
    assert "run_due_once" in HookEngine._loop.__code__.co_names
