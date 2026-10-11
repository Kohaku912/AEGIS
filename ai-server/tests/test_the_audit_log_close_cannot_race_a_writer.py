"""Cycle 145 pin: ``AuditLog.close()`` is guarded, so it cannot race an in-flight ``append()``.

Item 97 fixed (branch 1 = guard ``close()``). Before this cycle (HEAD 509ee0e), ``close()`` took no
lock while ``append()`` held ``self._lock`` across ``_insert_record`` and ``conn.commit``,
and ``AegisRuntime.stop()`` shut the background executors down with ``wait=False`` before
calling ``audit_log.close()``. So ``stop()`` could close the SQLite connection out from
under an L2 worker that was mid-``execute`` -- reproduced as a Windows access violation
(``0xC0000005``, exit 139) about 1 run in 5. That directly defeats continuous operation:
the process dies while stopping.

The fix is **one half**: ``audit_log.py``'s write lock becomes a ``threading.RLock`` and
``close()`` takes it, so ``close`` *waits* for an in-flight ``append`` (which holds the lock
across the SQLite write) instead of closing the connection under it. The lock must be
reentrant because ``append()`` calls ``self.close()`` **while holding it**, and ``__init__``
calls ``close()`` too -- a plain ``Lock`` would deadlock (measured 2026-10-10, pinned by the
pin this one replaces).

The other half of the naive fix -- ``shutdown(wait=True)`` in ``stop()`` -- was **measured
and rejected (2026-10-11)**: a background worker blocked in a *real* LLM call (the captured
span showed a live ``deepseek-v4-flash`` request) makes ``wait=True`` hang ``stop()``, and
``conftest``'s ``reset_runtime_for_tests()`` -> ``stop()`` then times the whole suite out.
So ``stop()`` keeps ``wait=False``; guarding ``close()`` closes the race without waiting for
the LLM call, because ``close`` blocks only for the SQLite write.

This pin measures the *fixed* property deterministically (hold the lock, call ``close()``
from another thread, observe it blocks -- the opposite of the pre-fix pin), plus the source
facts and the ``stop()`` ordering (shutdown before close, ``wait=False``). No sleeps.
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
    return AuditEntry(action="c145.probe", entry_id="c145", reason="c145")


# --------------------------------------------------------------- the fixed property (driven)
def test_close_waits_while_the_lock_is_held(tmp_path: Path) -> None:
    """The fix: ``close()`` synchronizes, so it blocks until a held lock is released."""
    log = _log(tmp_path)
    returned = threading.Event()

    def _close() -> None:
        log.close()
        returned.set()

    with log._lock:
        worker = threading.Thread(target=_close, daemon=True)
        worker.start()
        got_through_early = returned.wait(timeout=_LOCK_TIMEOUT_S)
        worker.join(timeout=_LOCK_TIMEOUT_S)

    assert not got_through_early, (
        "close() ran through the held lock -- it is unguarded again, and the item-97 race "
        "is back; re-measure before changing this"
    )
    assert returned.wait(timeout=2.0), "close() never completed after the lock was released"


def test_append_still_waits_for_the_lock(tmp_path: Path) -> None:
    """The control: the *same* held lock stops ``append()`` until it is released."""
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


def test_close_is_not_a_noop(tmp_path: Path) -> None:
    """Negative control: a guarded ``close()`` must still actually close the connection."""
    log = _log(tmp_path)
    conn = log._get_conn()
    assert log._conn is conn
    log.close()
    assert log._conn is None, "close() no longer clears the connection -- the guard broke it"
    log.close()  # idempotent: a second close on a closed log must not raise
    assert log._conn is None


# --------------------------------------------------------------- the source facts (structural)
def _function_source(module, qualname: str) -> str:
    """The source of ``Class.method`` as a string, via the module's own file."""
    text = Path(module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(text)
    cls_name, func_name = qualname.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == func_name:
                    return ast.get_source_segment(text, child) or ""
    raise AssertionError(f"{qualname} not found in {module.__file__}")


def test_close_takes_the_lock_in_source() -> None:
    """The structural claim behind the behaviour: ``close``'s body takes the write lock."""
    src = _function_source(audit_log_module, "AuditLog.close")
    assert "with self._lock:" in src, "AuditLog.close no longer guards its body with the lock"


def test_append_still_takes_the_lock_in_source() -> None:
    """The partner fact: ``append`` still guards its writes with the same lock."""
    src = _function_source(audit_log_module, "AuditLog.append")
    assert "with self._lock:" in src, "AuditLog.append no longer guards its writes with the lock"


def test_the_write_lock_is_reentrant(tmp_path: Path) -> None:
    """The lock must be an ``RLock``: ``append`` re-enters it via ``self.close()``.

    A plain (non-reentrant) ``Lock`` makes the guarded ``close()`` deadlock the first
    ``append()`` (measured 2026-10-10). So the type is load-bearing, not cosmetic.
    """
    log = _log(tmp_path)
    assert isinstance(log._lock, type(threading.RLock())), (
        "the write lock is no longer an RLock -- the guarded close() will deadlock on "
        "append's nested close() call (item 97)"
    )
    assert not isinstance(log._lock, type(threading.Lock())), "the lock reverted to a plain Lock"
    append_src = _function_source(audit_log_module, "AuditLog.append")
    assert "self.close()" in append_src, (
        "append no longer calls self.close() -- re-measure whether the lock still needs to "
        "be reentrant (item 97)"
    )
    init_src = _function_source(audit_log_module, "AuditLog.__init__")
    assert "self.close()" in init_src, "__init__ no longer calls close() -- re-measure item 97"


# ------------------------------------------------- reachability: the ordering in stop()
def _stop_calls() -> tuple[list[int], list[int], bool]:
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
                            waits = [kw for kw in call.keywords if kw.arg == "wait"]
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
    """``stop()`` still closes the log *after* its executors, and still does not wait.

    ``wait=True`` is deliberately **not** used: it hangs when a worker is blocked in a real
    LLM call (measured 2026-10-11). The race is closed by ``close()`` taking the lock, not
    by waiting for the worker.
    """
    shutdowns, closes, all_wait_false = _stop_calls()

    assert shutdowns, "AegisRuntime.stop no longer shuts down a background executor"
    assert closes, "AegisRuntime.stop no longer closes the audit log"
    assert all_wait_false, (
        "a shutdown in AegisRuntime.stop uses wait=True -- that hangs on a worker blocked "
        "in a real LLM call (measured 2026-10-11); re-measure item 97"
    )
    assert min(closes) > max(shutdowns), (
        "AegisRuntime.stop closes the audit log before shutting down its executors -- "
        "re-measure item 97"
    )
