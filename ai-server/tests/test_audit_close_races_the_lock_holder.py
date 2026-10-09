"""Cycle 137 pin: ``AuditLog.close()`` takes no lock -- so it races an in-flight ``append()``.

Measured 2026-10-10 (HEAD 67b8676). ``AuditLog`` guards its writes with ``self._lock``
(``audit_log.py``): ``append`` enters ``with self._lock:`` before it touches the SQLite
connection. ``close`` does **not** -- its body opens with ``if self._conn is not None:`` and
never mentions the lock. So a caller that closes the log from another thread can pull the
connection out from under a writer that is mid-``execute``.

That is not hypothetical: ``runtime.stop()`` calls ``self.audit_log.close()``
(``runtime.py:225``) while an L2 worker may still be running -- ``stop()`` shuts the
background executors down with ``wait=False`` (``runtime.py:170`` / ``:179``) and therefore
does **not** wait for in-flight work before closing the audit log. Reproduced as a Windows
access violation (``0xC0000005``, exit 139) about 1 run in 5 while probing a published event
that booted a real L2 worker (recorded as ``DELEGATION.md`` section 4 item 97).

This pin makes the race **deterministic** by measuring the resource directly: hold
``log._lock`` in this thread, then call ``close()`` from another thread and observe that it
returns *anyway*; the control is ``append()``, which blocks until the lock is released. No
sleeps, no retries -- the asymmetry is a property of the code, not of timing.

This pin records the defect; it does **not** fix it. The fix branch (lock ``close()`` /
``shutdown(wait=True)`` / both / leave) is an owner decision, named in ``DELEGATION.md``
section 4 item 97 -- and this pin measures the premise of one branch: **branch 1 (guard
``close()``) deadlocks.** ``append()`` calls ``self.close()`` while holding the lock, and
``__init__`` calls ``close()``, so a bare guard makes construction leave the lock held and
the first ``append()`` hang (mutation M1 -> ``Timeout``; measured: ``log._lock.locked() is
True`` after construction and a threaded ``append()`` never returns).
"""

from __future__ import annotations

import ast
import threading
from pathlib import Path

import aegis_ai.audit.audit_log as audit_log_module
import aegis_ai.runtime as runtime_module
from aegis_ai.audit.audit_log import AuditEntry, AuditLog

_LOCK_TIMEOUT_S = 1.0


def _log(tmp_path: Path) -> AuditLog:
    return AuditLog(path=str(tmp_path / "audit.jsonl"))


def _entry() -> AuditEntry:
    return AuditEntry(action="c137.probe", entry_id="c137", reason="c137")


# --------------------------------------------------------------- the asymmetry (driven)
def test_close_returns_while_the_lock_is_held(tmp_path: Path) -> None:
    """The defect: ``close()`` does not synchronize, so it runs through a held lock."""
    log = _log(tmp_path)
    returned = threading.Event()

    def _close() -> None:
        log.close()
        returned.set()

    with log._lock:
        worker = threading.Thread(target=_close, daemon=True)
        worker.start()
        got_through = returned.wait(timeout=_LOCK_TIMEOUT_S)
        worker.join(timeout=_LOCK_TIMEOUT_S)

    assert got_through, (
        "close() blocked on the held lock -- it now synchronizes, and this pin records the "
        "opposite; re-measure before changing it"
    )
    assert log._conn is None


def test_append_waits_for_the_lock(tmp_path: Path) -> None:
    """The control: the *same* held lock does stop ``append()`` until it is released."""
    log = _log(tmp_path)
    returned = threading.Event()

    def _append() -> None:
        log.append(_entry())
        returned.set()

    with log._lock:
        worker = threading.Thread(target=_append, daemon=True)
        worker.start()
        got_through_early = returned.wait(timeout=_LOCK_TIMEOUT_S)
        worker.join(timeout=_LOCK_TIMEOUT_S)

    assert not got_through_early, "append() did not block on the held lock -- it is unguarded"
    assert returned.wait(timeout=2.0), "append() never completed after the lock was released"


# --------------------------------------------------------- the asymmetry (source facts)
def _function_source(module, qualname: str) -> str:
    """The source of ``Class.method`` as a string, via the module's own file."""
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    cls_name, func_name = qualname.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == func_name:
                    return ast.get_source_segment(Path(module.__file__).read_text(encoding="utf-8"), child) or ""
    raise AssertionError(f"{qualname} not found in {module.__file__}")


def test_close_takes_no_lock_in_source() -> None:
    """The structural claim behind the behaviour: ``close``'s body never touches the lock."""
    src = _function_source(audit_log_module, "AuditLog.close")
    assert "_lock" not in src, "AuditLog.close now references the lock; re-measure the race"


def test_append_takes_the_lock_in_source() -> None:
    """The asymmetry partner: ``append`` does guard its body with the lock."""
    src = _function_source(audit_log_module, "AuditLog.append")
    assert "with self._lock:" in src, "AuditLog.append no longer guards its writes with the lock"


def test_the_naive_fix_would_deadlock(tmp_path: Path) -> None:
    """Why branch 1 (lock ``close()``) is *not* viable -- measured, not assumed.

    ``append()`` calls ``self.close()`` **while holding** the lock, and ``__init__`` calls
    ``close()`` too. The lock is a plain (non-reentrant) ``threading.Lock``, so a guard in
    ``close()`` makes construction leave the lock held and the **first** ``append()`` hang
    (measured 2026-10-10: after construction with a guarded ``close()``,
    ``log._lock.locked() is True`` and a threaded ``append()`` never returns). So a fix for
    item 97 has to be ``shutdown(wait=True)``, an ``RLock``, or dropping the ``append`` ->
    ``close`` self-call -- never a bare guard.
    """
    log = _log(tmp_path)
    assert isinstance(log._lock, type(threading.Lock())), "the write lock changed type"
    assert not isinstance(log._lock, type(threading.RLock())), (
        "the lock became reentrant -- re-measure the branch-1 deadlock analysis for item 97"
    )
    append_src = _function_source(audit_log_module, "AuditLog.append")
    assert "self.close()" in append_src, (
        "append no longer closes the connection under the lock -- branch 1 may be viable now"
    )
    init_src = _function_source(audit_log_module, "AuditLog.__init__")
    assert "self.close()" in init_src, (
        "__init__ no longer calls close() -- re-measure the branch-1 deadlock analysis"
    )



# ------------------------------------------------- reachability: the ordering in stop()
def _stop_call_linenos() -> tuple[list[int], list[int], bool]:
    """Return (shutdown linenos, audit-close linenos, every shutdown used wait=False)."""
    src = Path(runtime_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    shutdowns: list[int] = []
    closes: list[int] = []
    all_wait_false = True
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AegisRuntime":
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "stop":
                    for call in ast.walk(child):
                        if not isinstance(call, ast.Call):
                            continue
                        func = call.func
                        if isinstance(func, ast.Attribute) and func.attr == "shutdown":
                            shutdowns.append(call.lineno)
                            waits = [
                                kw for kw in call.keywords if kw.arg == "wait"
                            ]
                            if not waits or not (
                                isinstance(waits[0].value, ast.Constant)
                                and waits[0].value.value is False
                            ):
                                all_wait_false = False
                        if (
                            isinstance(func, ast.Attribute)
                            and func.attr == "close"
                            and isinstance(func.value, ast.Attribute)
                            and func.value.attr == "audit_log"
                        ):
                            closes.append(call.lineno)
    return shutdowns, closes, all_wait_false


def test_stop_shuts_down_executors_before_closing_the_audit_log() -> None:
    """The race is reachable: ``stop()`` does not wait, then closes the log."""
    shutdowns, closes, all_wait_false = _stop_call_linenos()

    assert shutdowns, "AegisRuntime.stop no longer shuts down a background executor"
    assert closes, "AegisRuntime.stop no longer closes the audit log"
    assert all_wait_false, (
        "a shutdown in AegisRuntime.stop now uses wait=True -- the in-flight window changed; "
        "re-measure item 97"
    )
    assert min(closes) > max(shutdowns), (
        "AegisRuntime.stop closes the audit log before shutting down its executors -- the "
        "ordering this pin records is gone; re-measure item 97"
    )
