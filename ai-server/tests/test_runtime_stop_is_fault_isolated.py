"""Cycle 140 pin: ``AegisRuntime.stop()`` is fault-isolated -- every present step runs
even when an earlier step raises an ordinary ``Exception``.

Why this property and not another
---------------------------------
``stop()`` (``runtime.py:151``) drives six components on a bare composition root
(``status_manager`` / ``hook_engine`` / ``user_state_manager`` / ``personal_data_core``
/ ``sleep_manager`` / ``audit_log``) plus two event subscriptions.  Every single call
sits inside its own ``try: ... except Exception:`` with a ``logger.debug(...)`` -- that
is the *declared* intent: one component failing to shut down must not prevent the
others from shutting down, because a leaked thread or an unclosed audit log is exactly
the kind of failure that outlives the runtime (the ``status_manager`` comment at
``runtime.py:190-195`` records a real instance of this).

Nothing validated that intent.  A refactor that drops one ``try`` -- or moves a call
out of its guard -- would silently make ``stop()`` abort at the first failure, and the
suite would stay green.

⚠️ Measurement correction (this cycle).  An earlier probe reported
``later steps still ran: False`` after a raising ``hook_engine.stop``.  That was an
**instrument defect, not a code defect**: the probe appended the raising step and the
spies to two *different* lists, then tested containment against the list that could
never contain them.  The measurement below replaces it.

Measured 2026-10-10 (HEAD ``441dfff``), real ``get_runtime()`` with the empty-key
provider and every server disabled:

* All six present steps run, in declaration order.
* ``_background_l1_executor`` / ``_background_l2_executor`` / ``autonomous_loop`` are
  ``None`` on a bare composition root (each is created lazily), so ``stop()`` skips them
  without raising.
* ``event_manager.unsubscribe`` is called with **both** subscription ids
  (``_l1_event_subscription`` and ``_initiative_event_subscription``).
* A step raising an ordinary ``Exception`` does **not** stop the later steps, and the
  exception does **not** propagate out of ``stop()``.
* A step raising a ``BaseException`` (modelled with a private subclass, to avoid
  disturbing pytest's own ``KeyboardInterrupt`` handling) **does** propagate and does
  abort the later steps -- which is correct: ``except Exception`` must not swallow
  ``KeyboardInterrupt`` / ``SystemExit`` during shutdown.
"""

from __future__ import annotations

from typing import Any

import pytest

import aegis_ai.runtime as runtime_module

_ALL_SERVERS = "ai-server,pc-server,browser-server,android-server,room-server,dashboard"

#: ``(holder attribute, method name)`` for every step ``stop()`` drives on a bare
#: composition root.  The three lazily-created components are asserted ``None`` below.
_STEPS: tuple[tuple[str, str], ...] = (
    ("status_manager", "stop_background_checks"),
    ("hook_engine", "stop"),
    ("user_state_manager", "stop"),
    ("personal_data_core", "stop"),
    ("sleep_manager", "close"),
    ("audit_log", "close"),
)

#: Created lazily, so absent on a runtime that never routed an event / started the loop.
_LAZY_HOLDERS = ("_background_l1_executor", "_background_l2_executor", "autonomous_loop")


class _NotAnException(BaseException):
    """A ``BaseException`` that is deliberately not an ``Exception``.

    Stands in for ``KeyboardInterrupt`` / ``SystemExit`` without hijacking pytest's
    own handling of those two (an escaping ``KeyboardInterrupt`` aborts the session
    instead of reporting a normal failure).
    """


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    yield

    from aegis_ai.runtime import reset_runtime_for_tests

    reset_runtime_for_tests()


@pytest.fixture
def real_runtime(monkeypatch, tmp_path) -> Any:
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AEGIS_DISABLED_SERVERS", _ALL_SERVERS)

    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    reset_runtime_for_tests()
    return get_runtime()


def _install_spies(
    runtime: Any,
    seq: list[str],
    raising: str | None = None,
    exc_factory: Any = RuntimeError,
) -> list[tuple[Any, str, Any]]:
    """Replace each *present* step with a recorder; ``raising`` also raises.

    Returns ``(obj, method, original)`` triples so the caller can restore them:
    ``reset_runtime_for_tests()`` itself calls ``stop()``, so a spy left installed
    would re-run during teardown (and a raising spy would break teardown).
    """
    saved: list[tuple[Any, str, Any]] = []
    for holder, method in _STEPS:
        obj = getattr(runtime, holder, None)
        if obj is None or not hasattr(obj, method):
            continue
        original = getattr(obj, method)
        saved.append((obj, method, original))

        if holder == raising:

            def _raise(*_a: Any, _h: str = holder, **_k: Any) -> None:
                seq.append(_h)
                raise exc_factory()

            setattr(obj, method, _raise)
        else:

            def _spy(*_a: Any, _h: str = holder, **_k: Any) -> None:
                seq.append(_h)

            setattr(obj, method, _spy)
    return saved


def _restore(saved: list[tuple[Any, str, Any]]) -> None:
    for obj, method, original in saved:
        setattr(obj, method, original)


def _present_holders(runtime: Any) -> set[str]:
    return {
        holder
        for holder, method in _STEPS
        if getattr(runtime, holder, None) is not None and hasattr(getattr(runtime, holder), method)
    }


def test_every_present_step_runs_on_a_real_runtime(real_runtime: Any) -> None:
    present = _present_holders(real_runtime)
    assert present == {holder for holder, _ in _STEPS}, (
        f"the composition root no longer provides the expected six components: "
        f"present={sorted(present)}"
    )

    seq: list[str] = []
    saved = _install_spies(real_runtime, seq)
    try:
        real_runtime.stop()
    finally:
        _restore(saved)

    assert seq == [holder for holder, _ in _STEPS], (
        f"stop() did not drive every present step in order: {seq}"
    )


def test_the_lazy_components_are_absent_and_skipped(real_runtime: Any) -> None:
    for holder in _LAZY_HOLDERS:
        assert getattr(real_runtime, holder, None) is None, (
            f"{holder} was expected to be created lazily; a bare composition root "
            f"should not have it"
        )

    # stop() must tolerate their absence (it reads them with getattr(..., None)).
    real_runtime.stop()


def test_both_subscriptions_are_unsubscribed(real_runtime: Any) -> None:
    seen: list[str] = []
    original = real_runtime.event_manager.unsubscribe

    def _record(sid: str) -> None:
        seen.append(sid)

    real_runtime.event_manager.unsubscribe = _record
    try:
        real_runtime.stop()
    finally:
        real_runtime.event_manager.unsubscribe = original

    expected = {
        real_runtime._l1_event_subscription,
        real_runtime._initiative_event_subscription,
    }
    assert expected <= set(seen), f"stop() unsubscribed {seen}, expected both of {expected}"


@pytest.mark.parametrize("failing", [holder for holder, _ in _STEPS])
def test_a_failure_in_any_step_does_not_abort_the_rest(real_runtime: Any, failing: str) -> None:
    seq: list[str] = []
    saved = _install_spies(real_runtime, seq, raising=failing, exc_factory=RuntimeError)
    try:
        real_runtime.stop()  # must not raise
    finally:
        _restore(saved)

    assert failing in seq, f"the injected failure in {failing} never fired"
    others = {holder for holder, _ in _STEPS} - {failing}
    assert others <= set(seq), (
        f"a raising {failing} skipped {sorted(others - set(seq))}; stop() is not "
        f"fault-isolated for an ordinary Exception"
    )


def test_a_base_exception_is_not_swallowed(real_runtime: Any) -> None:
    """Control: the guard is ``except Exception``, so ``BaseException`` must escape.

    This is the boundary the fault isolation stops at -- swallowing
    ``KeyboardInterrupt`` / ``SystemExit`` during shutdown would be wrong.
    """
    seq: list[str] = []
    saved = _install_spies(
        real_runtime, seq, raising="hook_engine", exc_factory=_NotAnException
    )
    try:
        with pytest.raises(_NotAnException):
            real_runtime.stop()
    finally:
        _restore(saved)

    later = {"user_state_manager", "personal_data_core", "sleep_manager", "audit_log"}
    assert later.isdisjoint(seq), (
        f"a BaseException should have aborted the later steps, but they ran: {seq}"
    )
