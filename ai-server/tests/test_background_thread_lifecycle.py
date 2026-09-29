"""``AegisRuntime.stop()`` must stop the threads the runtime started.

``_build_runtime`` starts a daemon thread named ``status-check``. That thread is not
an idle poller: ``StatusManager._run_checks`` re-resolves ``pc-server`` /
``room-server``, so it probes the network and records the result in the endpoint
resolver's process-global ``_MEMORY`` *and* in ``data/endpoint_cache.json``.

Until this was pinned, ``AegisRuntime.stop()`` stopped the autonomous loop, the hook
engine, the user-state manager, the personal-data core, the sleep manager and the
audit log — but not the status manager. The daemon therefore outlived
``reset_runtime_for_tests()`` and kept running for the rest of the process, which is
how it came to overwrite the resolver cache underneath an unrelated test
(``test_endpoint_resolver.py``), producing a rare, order-dependent failure roughly
ninety files away from the leak.

A ``stop()`` that leaves a thread running is the same shape of defect as a settings
flag nothing reads: the method exists, is called, and does not do what its name says.

These tests assert on *the thread the object under test owns*, never on a global count.
Other tests in the suite may legitimately be holding a status thread at the same time,
and a global count would turn their leaks into failures here.
"""

from __future__ import annotations

import threading
import time
from typing import Any

import pytest

_THREAD_NAME = "status-check"

#: Every server the default StatusManager knows about. Disabling all of them keeps these
#: tests off the network: a disabled server is skipped before the endpoint resolver is
#: ever reached.
_ALL_SERVERS = "ai-server,pc-server,browser-server,android-server,room-server,dashboard"


def _status_threads() -> list[threading.Thread]:
    return [
        thread
        for thread in threading.enumerate()
        if thread.name == _THREAD_NAME and thread.is_alive()
    ]


def _wait_gone(thread: threading.Thread, timeout: float = 5.0) -> bool:
    thread.join(timeout=timeout)
    return not thread.is_alive()


def _manager(monkeypatch: pytest.MonkeyPatch) -> Any:
    """A StatusManager whose check body is a no-op, so only the thread is under test."""
    monkeypatch.setenv("AEGIS_DISABLED_SERVERS", _ALL_SERVERS)

    from aegis_ai.status.status_manager import StatusManager

    manager = StatusManager(check_interval=0.05, timeout=0.05)
    # ``_background_loop`` calls ``_run_checks(abort=...)``, so the stand-in has to accept
    # arguments; the point is that no real network check runs here.
    monkeypatch.setattr(manager, "_run_checks", lambda *_a, **_k: None)
    return manager


def test_the_probe_detects_a_running_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    """Guard the guard: if this can never pass, the rest of the module proves nothing."""
    manager = _manager(monkeypatch)
    try:
        manager.start_background_checks()
        thread = manager._check_thread
        assert thread is not None and thread.is_alive(), (
            "start_background_checks() did not leave a live thread, so the other tests in "
            "this module cannot fail and prove nothing"
        )
    finally:
        manager.stop_background_checks()


def test_start_background_checks_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = _manager(monkeypatch)
    try:
        manager.start_background_checks()
        first = manager._check_thread
        assert first is not None and first.is_alive()

        manager.start_background_checks()
        assert manager._check_thread is first, "a second start() replaced the thread"
        assert first.is_alive()
    finally:
        manager.stop_background_checks()


def test_stop_background_checks_ends_the_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = _manager(monkeypatch)
    manager.start_background_checks()
    thread = manager._check_thread
    assert thread is not None and thread.is_alive()

    manager.stop_background_checks()
    assert _wait_gone(thread), "stop_background_checks() left its own thread running"


def test_stop_background_checks_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = _manager(monkeypatch)
    manager.start_background_checks()
    thread = manager._check_thread
    assert thread is not None

    manager.stop_background_checks()
    manager.stop_background_checks()
    assert _wait_gone(thread)


def test_runtime_stop_ends_the_status_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    """The regression that mattered: ``reset_runtime_for_tests()`` must stop the thread."""
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")
    monkeypatch.setenv("AEGIS_DISABLED_SERVERS", _ALL_SERVERS)

    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    before = {id(thread) for thread in _status_threads()}

    reset_runtime_for_tests()
    try:
        get_runtime()
        started = [thread for thread in _status_threads() if id(thread) not in before]
        assert started, "get_runtime() did not start a status thread, so this test is vacuous"

        reset_runtime_for_tests()
        still_alive = [thread for thread in started if not _wait_gone(thread)]
        assert not still_alive, (
            f"AegisRuntime.stop() left {len(still_alive)} 'status-check' thread(s) running. "
            "That thread performs network discovery and mutates the endpoint resolver's "
            "process-global cache, so it corrupts unrelated tests for the rest of the session."
        )
    finally:
        reset_runtime_for_tests()
