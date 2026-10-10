"""Cycle 139 pin: the observation -> dict projection is built at four sites; they must agree.

⚠️ **Updated in cycle 142**: the four sites no longer *hand-write* the five-field core -- they
now spread one helper, ``_l1_observation_core`` (``runtime.py``). The pin is unchanged in
purpose (it drives one ``observation`` through all four sites and compares them); it is now
the **regression net for the consolidation** (``DELEGATION.md`` §4 item 99, taken in cycle 142):
if a site stops spreading the helper, its dict stops matching the others and this file goes red.
The core's own *defaults* (the absent-attribute cases) are pinned separately below, because
comparing the four sites to each other cannot see a change to the shared source.

``runtime.py`` builds the same projection of an L1 ``observation`` into a dict at four sites:

1. ``_l1_observation_payload`` -- the ``l1.observation`` event payload;
2. ``_append_recent_l1_summary``'s inner dict -- the dashboard's recent list;
3. ``_run_l1_immediate_pipeline``'s ``detail["l1"]`` -- the immediate route;
4. ``_handle_background_l1_event``'s ``detail["l1"]`` -- the background route.

As first measured (cycle 139) the five-field core -- ``meaning`` / ``value`` / ``priority`` /
``required_intelligence`` / ``confidence`` -- was written out verbatim at all four (the
``confidence`` line appeared **4** times); three of the four also carried the ``raw``-derived
keys ``summary_bucket`` / ``observed_action`` / ``possible_intent``.

Measured 2026-10-10 (HEAD 1fb3669) by driving one ``observation`` through all four:

* ``_l1_observation_payload(event, observation)`` directly;
* ``_append_recent_l1_summary(runtime, event, observation, decision)`` -> the last element;
* a production publish on the immediate route -> ``_run_l2_pipeline(trigger, detail)``;
* a production publish on the background route -> ``_submit_background_l2(trigger, detail)``.

All four agree on the five shared fields (and the two ``detail["l1"]`` projections are
*exactly* equal, nine keys each).
"""

from __future__ import annotations

import threading
from types import SimpleNamespace
from typing import Any

import pytest

import aegis_ai.runtime as runtime_module

_IMMEDIATE_TYPE = "social.inbox.received"
_BACKGROUND_TYPE = "pc.metric.sampled"
_ALL_SERVERS = "ai-server,pc-server,browser-server,android-server,room-server,dashboard"

#: The five-field core written out at every site (measured 2026-10-10).
_SHARED_FIELDS = ("meaning", "value", "priority", "required_intelligence", "confidence")

#: The two ``detail["l1"]`` sites additionally carry these (nine keys total).
_DETAIL_KEYS = frozenset(
    {
        "meaning",
        "value",
        "priority",
        "required_intelligence",
        "confidence",
        "action_type",
        "summary_bucket",
        "observed_action",
        "possible_intent",
    }
)

_FORWARDED_ACTION = "escalate"


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


def _observation(meaning: str = "c139") -> Any:
    return SimpleNamespace(
        event_id="c139",
        meaning=meaning,
        value=0.5,
        priority=0.7,
        confidence=0.9,
        required_intelligence=SimpleNamespace(value="high"),
        raw={
            "summary_bucket": "immediate",
            "observed_action": "act",
            "possible_intent": "intent",
        },
    )


def _decision(observation: Any) -> Any:
    return SimpleNamespace(
        action=SimpleNamespace(type=SimpleNamespace(value=_FORWARDED_ACTION)),
        observation=observation,
    )


class _FourSites:
    """Collects the projection from all four hand-written sites, for one observation."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, observation: Any) -> None:
        self.observation = observation
        self.decision = _decision(observation)
        self.detail_immediate: dict | None = None
        self.detail_background: dict | None = None
        # The immediate route runs on a background pool (item 48), so the write into
        # ``detail_immediate`` happens on another thread. Waiting on the executor's
        # ``shutdown`` is *not* sufficient -- if the pool was never created (or a prior
        # test's pool was the one drained) the read races the write. Signal on the write
        # itself and wait on the event: this is measured, not assumed.
        self._immediate_seen = threading.Event()
        self._background_seen = threading.Event()

        monkeypatch.setattr(
            runtime_module, "_run_l1_pipeline_for_event", lambda r, e: self.decision
        )

        def fake_l2(runtime_: Any, *, trigger: str, detail: dict) -> dict:
            self.detail_immediate = dict(detail.get("l1", {}))
            self._immediate_seen.set()
            return {"handled": False, "action_type": "noop"}

        def fake_submit_l2(runtime_: Any, *, trigger: str, detail: dict) -> None:
            self.detail_background = dict(detail.get("l1", {}))
            self._background_seen.set()

        monkeypatch.setattr(runtime_module, "_run_l2_pipeline", fake_l2)
        monkeypatch.setattr(runtime_module, "_submit_background_l2", fake_submit_l2)

    def collect(self, runtime: Any) -> dict[str, dict]:
        from aegis_ai.event.helpers import build_event

        event = build_event(_IMMEDIATE_TYPE)
        payload = runtime_module._l1_observation_payload(event, self.observation)

        runtime_module._append_recent_l1_summary(runtime, event, self.observation, self.decision)
        recent = dict(runtime._recent_l1_summaries[-1])

        runtime.event_manager.publish(build_event(_IMMEDIATE_TYPE))
        # Drain the pool if it exists (belt), then wait on the write's own event
        # (braces) so the read below cannot race the worker thread.
        executor = getattr(runtime, "_background_l1_executor", None)
        if executor is not None:
            executor.shutdown(wait=True)
        assert self._immediate_seen.wait(timeout=30), (
            "the immediate route never reached _run_l2_pipeline -- the publish was filtered, "
            "deduplicated, or the subscriber was not wired (the probe would read {} and lie)"
        )

        runtime.event_manager.publish(build_event(_BACKGROUND_TYPE))
        assert self._background_seen.wait(timeout=30), (
            "the background route never reached _submit_background_l2 -- see above"
        )

        return {
            "observation_payload": payload,
            "recent_summary": recent,
            "immediate": self.detail_immediate or {},
            "background": self.detail_background or {},
        }

    @staticmethod
    def shared(projection: dict) -> dict:
        return {k: projection.get(k) for k in _SHARED_FIELDS}


def test_all_four_hand_written_projections_agree(real_runtime, monkeypatch) -> None:
    """The headline: one observation, four sites, one five-field projection."""
    sites = _FourSites(monkeypatch, _observation()).collect(real_runtime)

    base = _FourSites.shared(sites["observation_payload"])
    for name, projection in sites.items():
        assert projection, f"site {name!r} produced nothing -- the probe is vacuous there"
        assert _FourSites.shared(projection) == base, (
            f"site {name!r} now disagrees with the others on the shared observation fields "
            f"({_SHARED_FIELDS}):\n  {_FourSites.shared(projection)}\n  {base}"
        )


def test_the_two_detail_projections_are_exactly_equal(real_runtime, monkeypatch) -> None:
    """The two ``detail['l1']`` sites are not just compatible -- they are identical."""
    sites = _FourSites(monkeypatch, _observation()).collect(real_runtime)

    assert sites["immediate"] == sites["background"], (
        "the two L1 routes build different detail['l1'] projections:\n"
        f"  immediate: {sites['immediate']}\n  background: {sites['background']}"
    )
    assert set(sites["immediate"]) == _DETAIL_KEYS, (
        f"the detail projection's key set changed: {sorted(sites['immediate'])}"
    )


def test_every_site_carries_the_five_shared_fields(real_runtime, monkeypatch) -> None:
    """Key presence at every site -- so a field dropped from one site is caught."""
    sites = _FourSites(monkeypatch, _observation()).collect(real_runtime)

    for name, projection in sites.items():
        missing = [k for k in _SHARED_FIELDS if k not in projection]
        assert not missing, f"site {name!r} dropped the shared field(s) {missing}"


def test_the_shared_fields_track_the_observation(real_runtime, monkeypatch) -> None:
    """The mapping: each shared field is fed from the observation, not a constant."""
    sites = _FourSites(monkeypatch, _observation(meaning="carried")).collect(real_runtime)

    for name, projection in sites.items():
        assert projection["meaning"] == "carried", f"{name} lost the observation's meaning"
        assert projection["value"] == 0.5, f"{name} lost the observation's value"
        assert projection["priority"] == 0.7, f"{name} lost the observation's priority"
        assert projection["confidence"] == 0.9, f"{name} lost the observation's confidence"
        assert projection["required_intelligence"] == "high", f"{name} lost required_intelligence"


def test_a_missing_observation_keeps_them_agreeing(real_runtime, monkeypatch) -> None:
    """The default path: with ``observation=None``, every site still projects the same fields."""
    sites = _FourSites(monkeypatch, None).collect(real_runtime)

    base = _FourSites.shared(sites["observation_payload"])
    for name, projection in sites.items():
        assert _FourSites.shared(projection) == base, f"site {name!r} diverged on the default path"


def test_the_control_a_changed_observation_moves_every_site(real_runtime, monkeypatch) -> None:
    """Control: the agreement is not vacuous -- a different observation moves every site."""
    sites = _FourSites(monkeypatch, _observation(meaning="moved")).collect(real_runtime)

    for name, projection in sites.items():
        assert projection.get("meaning") == "moved", (
            f"site {name!r} ignored the observation -- the agreement is between constants"
        )


# --- added in cycle 142: the core's own defaults (the consolidation's blind spot) ---


def test_the_core_defaults_are_pinned_when_required_intelligence_is_absent(real_runtime, monkeypatch) -> None:
    """Comparing the four sites to each other cannot see a change to the *shared* source.

    After the cycle-142 consolidation all four sites spread ``_l1_observation_core``, so a
    mutation to the core's ``required_intelligence`` default moves **all four together** and
    the agreement tests stay green. This test pins the default itself by driving the
    production path with an observation that has **no** ``required_intelligence`` attribute.
    """
    obs = _observation()
    del obs.required_intelligence

    sites = _FourSites(monkeypatch, obs).collect(real_runtime)
    for name, projection in sites.items():
        assert projection["required_intelligence"] == "low", (
            f"site {name!r} changed the absent-attribute default -- it must stay 'low'"
        )


def test_the_core_passes_through_a_plain_string_required_intelligence(real_runtime, monkeypatch) -> None:
    """The other half: a plain string (no ``.value``) is stringified as-is."""
    obs = _observation()
    obs.required_intelligence = "medium"

    sites = _FourSites(monkeypatch, obs).collect(real_runtime)
    for name, projection in sites.items():
        assert projection["required_intelligence"] == "medium", (
            f"site {name!r} mishandled a plain-string required_intelligence"
        )
