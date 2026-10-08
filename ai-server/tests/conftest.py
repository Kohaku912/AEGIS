"""Shared pytest fixtures for the ai-server test suite.

The LLM provider balance circuit breaker lives in a process-global registry
(``aegis_ai.llm.provider_circuit.PROVIDER_CIRCUITS``). Without isolation, a
single test that trips the circuit (e.g. by simulating/observing a 402 billing
error) leaves it open for every subsequent test in the same process, producing
cascading, order-dependent failures that have nothing to do with the code under
test. Reset it around every test so each test starts from a clean slate.

This module also implements the **``--fail-on-empty`` discipline** for the egress
suite — see ``--require-egress-tests`` below.
"""

from __future__ import annotations

import os
import threading

import pytest

# Tests must not touch the LAN. ``StatusManager`` starts a background thread that
# re-resolves pc-server / room-server, and the resolver's LAN discovery pings and
# port-scans the whole /24 - real network traffic, tens of seconds per sweep, from a
# unit test run. It also writes the discovered address into the resolver's
# process-global cache, which is what made ``test_endpoint_resolver.py`` fail
# intermittently. ``AEGIS_LAN_SCAN_ENABLED`` is the documented switch for this; the
# suite turns it off for every test, so scanning is opt-in per test via
# ``monkeypatch.setenv`` plus an explicit ``allow_lan_scan=`` argument.
os.environ["AEGIS_LAN_SCAN_ENABLED"] = "0"


@pytest.fixture(autouse=True)
def _isolate_provider_circuit():
    from aegis_ai.llm.provider_circuit import PROVIDER_CIRCUITS

    PROVIDER_CIRCUITS.reset()
    yield
    PROVIDER_CIRCUITS.reset()


# ── Leaked background-thread guard ────────────────────────────────────────────
#
# ``AegisRuntime._build_runtime`` calls ``status_manager.start_background_checks()``,
# which starts a daemon thread named ``status-check``. That thread is not an idle
# poller: ``_run_checks`` re-resolves ``pc-server`` / ``room-server``, so it probes the
# network and records the result in the endpoint resolver's process-global ``_MEMORY``
# *and* in ``data/endpoint_cache.json``.
#
# A test that boots the real runtime used to leave that thread running for the rest of
# the session. It then overwrote the resolver cache underneath
# ``tests/test_endpoint_resolver.py::test_resolve_tcp_endpoint_tries_candidates_and_caches``,
# which asserts the *first* probed candidate is the host it just cached — a rare,
# order-dependent failure roughly ninety files away from the actual leak. The chain was:
# ``AegisRuntime.stop()`` never stopped the status manager at all; then
# ``stop_background_checks()`` joined with a 5s timeout while the loop slept out a 60s
# interval; and even then, a sweep already in flight takes tens of seconds because it
# touches the network. All three are fixed.
#
# The guard below is the tripwire that found this and keeps it found. Same principle as
# ``--require-egress-tests``: an unenforced invariant is not an invariant.

_STATUS_THREAD_NAME = "status-check"


def _status_threads() -> list[threading.Thread]:
    return [
        thread
        for thread in threading.enumerate()
        if thread.name == _STATUS_THREAD_NAME and thread.is_alive()
    ]


@pytest.fixture(autouse=True)
def _no_leaked_status_thread():
    """Stop the runtime singleton after every test, then fail if a status thread survived.

    ``AegisRuntime._build_runtime`` starts a ``status-check`` daemon thread, and any test
    whose code path lazily calls ``get_runtime()`` builds a full runtime without asking for
    one. Left alone, that thread outlives the test and mutates process-global state — which
    is how ``test_endpoint_resolver.py`` came to fail intermittently, roughly ninety files
    away from the test that actually leaked.

    So this fixture does two things:

    1. **Stop the runtime singleton.** That is the cleanup the leaking test should have
       done; doing it here keeps one leak from cascading into every later test.
    2. **Fail if a live ``status-check`` thread remains.** Detection is a diff against the
       threads present at setup, so a thread leaked by an earlier test is not re-blamed on
       every test that follows it. Whatever survives step 1 is a thread the runtime does
       not own — a ``StatusManager`` that a test built and started itself.

    The per-module ``reset_runtime_for_tests()`` fixtures in the modules that reach the
    runtime are kept deliberately: they document *which* call paths do so, and they keep a
    single module run in isolation clean as well.
    """
    before = {id(thread) for thread in _status_threads()}

    yield

    try:
        from aegis_ai.runtime import reset_runtime_for_tests

        reset_runtime_for_tests()
    except Exception:  # pragma: no cover - teardown must never mask the real failure
        pass

    appeared = [thread for thread in _status_threads() if id(thread) not in before]
    if appeared:
        pytest.fail(
            f"this test left {len(appeared)} live '{_STATUS_THREAD_NAME}' thread(s) "
            f"(ident={[thread.ident for thread in appeared]}), and stopping the runtime "
            "singleton did not end them. That thread mutates process-global state and "
            "corrupts unrelated tests that run later. If the test starts a StatusManager "
            "directly, end it with `StatusManager.stop_background_checks()`."
        )


# ── Shared test doubles for the egress suites ─────────────────────────────────


class _StaticSettingsStore:
    """A settings store that returns a fixed ``AEGISSettings``.

    The egress gate reads settings through a ``.get() -> AEGISSettings`` seam, so
    tests can drive it without touching the real settings files.

    Keyword arguments other than ``voice`` are privacy-section overrides, so the
    common case reads naturally::

        _StaticSettingsStore(external_llm_allowed=True)

    The voice section is passed explicitly because its flag names do not collide
    with the privacy ones::

        _StaticSettingsStore(voice={"external_voice_api_allowed": True})
    """

    def __init__(self, *, voice: dict | None = None, **privacy_overrides) -> None:
        from aegis_ai.settings.models import AEGISSettings, PrivacySettings, VoiceSettings

        sections: dict = {"privacy": PrivacySettings(**privacy_overrides)}
        if voice is not None:
            sections["voice"] = VoiceSettings(**voice)
        self._settings = AEGISSettings(**sections)

    def get(self):
        return self._settings


@pytest.fixture
def settings_store_factory():
    """Factory for an egress settings store. No overrides means every lock closed.

    Usage::

        settings_store_factory()                            # shipped default: all closed
        settings_store_factory(external_llm_allowed=True)   # one flag flipped
        settings_store_factory(voice={"external_voice_api_allowed": True})
    """
    return _StaticSettingsStore


@pytest.fixture
def closed_egress_gate():
    """Install a process-wide egress gate with every lock closed, and restore after.

    ``configure_egress_gate`` mutates a module global, so a test that opens the
    locks would otherwise leak that state into every later test in the process.
    """
    from aegis_ai.egress import configure_egress_gate

    configure_egress_gate(settings_store=_StaticSettingsStore())
    yield
    configure_egress_gate(settings_store=_StaticSettingsStore())


# ── The --fail-on-empty discipline for the egress suite ───────────────────────
#
# AEGIS has exactly one constraint: user-information egress — re-scoped 2026-09-30 so
# that *unpermitted* disclosure is forbidden while outbound connections, and disclosure
# the user permits, are allowed. The egress tests are the regression protection for it.
#
# The failure mode this guards against is not "a test fails" but "no test runs".
# A rename, a moved directory, a marker typo, or a narrowed ``-k`` expression can
# leave the egress selection empty — and pytest reports the rest of the suite as
# passing, so the constraint silently stops being checked. That is the same shape
# as the retired "declared but ineffective" bugs: the protection exists on paper
# and does nothing in practice.
#
# CI therefore passes an explicit floor::
#
#     pytest -m egress --require-egress-tests=85
#
# and the run fails if fewer than that many egress-marked tests were collected.
# The floor is a *minimum*, so growing the suite never requires a CI change; only
# deliberately shrinking it does — which is exactly when a human should look.


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("aegis")
    group.addoption(
        "--require-egress-tests",
        action="store",
        type=int,
        default=0,
        metavar="N",
        dest="require_egress_tests",
        help=(
            "Fail the run unless at least N tests marked 'egress' were collected. "
            "Implements the --fail-on-empty discipline: the egress suite must never "
            "silently run zero tests. Default 0 (check disabled)."
        ),
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    floor = int(config.getoption("require_egress_tests") or 0)
    if floor <= 0:
        return

    collected = sum(1 for item in items if item.get_closest_marker("egress") is not None)
    if collected < floor:
        # UsageError (not a bare assertion) so the message is reported cleanly as
        # `ERROR: ...` with a non-zero exit code, rather than being rendered as an
        # internal pytest error.
        raise pytest.UsageError(
            f"--require-egress-tests={floor}, but only {collected} egress-marked test(s) "
            f"were collected. The egress suite has shrunk: the single constraint is no "
            f"longer covered by as much testing as CI expects. "
            f"Inspect the selection (pytest -m egress --collect-only) before lowering the floor."
        )
