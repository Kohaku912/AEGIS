"""Cycle 139 pin: the observation -> dict projection is hand-written FOUR times, uncompared.

``runtime.py`` builds the same projection of an L1 ``observation`` into a dict at four sites,
and **nothing compares them**:

1. ``_l1_observation_payload`` (``:408-420``) -- the ``l1.observation`` event payload;
2. ``_append_recent_l1_summary``'s inner dict (``:443-458``) -- the dashboard's recent list;
3. ``_run_l1_immediate_pipeline``'s ``detail["l1"]`` (``:900-916``) -- the immediate route;
4. ``_handle_background_l1_event``'s ``detail["l1"]`` (``:1763-1779``) -- the background route.

The five-field core -- ``meaning`` / ``value`` / ``priority`` / ``required_intelligence`` /
``confidence`` -- is written out verbatim at all four (measured: the ``confidence`` line
appears **4** times in the file); three of the four also carry the ``raw``-derived keys
``summary_bucket`` / ``observed_action`` / ``possible_intent`` (that line appears **3**
times). Rename a key at one site, or change a coercion (``float(...)`` -> ``str(...)``), and
only the consumer of that one site sees the change.

Measured 2026-10-10 (HEAD 1fb3669) by driving one ``observation`` through all four:

* ``_l1_observation_payload(event, observation)`` directly;
* ``_append_recent_l1_summary(runtime, event, observation, decision)`` -> the last element;
* a production publish on the immediate route -> ``_run_l2_pipeline(trigger, detail)``;
* a production publish on the background route -> ``_submit_background_l2(trigger, detail)``.

All four agree on the five shared fields (and the two ``detail["l1"]`` projections are
*exactly* equal, nine keys each). So the duplication is currently consistent; this pin turns
that into a **checked** property instead of a coincidence.

This pin records the duplication; it does not remove it. Consolidating the four sites into
one helper (and whether to) is an implementation decision, named in ``DELEGATION.md``
section 4 item 99.
"""

from __future__ import annotations

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

        monkeypatch.setattr(
            runtime_module, "_run_l1_pipeline_for_event", lambda r, e: self.decision
        )

        def fake_l2(runtime_: Any, *, trigger: str, detail: dict) -> dict:
            self.detail_immediate = dict(detail.get("l1", {}))
            return {"handled": False, "action_type": "noop"}

        def fake_submit_l2(runtime_: Any, *, trigger: str, detail: dict) -> None:
            self.detail_background = dict(detail.get("l1", {}))

        monkeypatch.setattr(runtime_module, "_run_l2_pipeline", fake_l2)
        monkeypatch.setattr(runtime_module, "_submit_background_l2", fake_submit_l2)

    def collect(self, runtime: Any) -> dict[str, dict]:
        from aegis_ai.event.helpers import build_event

        event = build_event(_IMMEDIATE_TYPE)
        payload = runtime_module._l1_observation_payload(event, self.observation)

        runtime_module._append_recent_l1_summary(runtime, event, self.observation, self.decision)
        recent = dict(runtime._recent_l1_summaries[-1])

        runtime.event_manager.publish(build_event(_IMMEDIATE_TYPE))
        executor = getattr(runtime, "_background_l1_executor", None)
        if executor is not None:
            executor.shutdown(wait=True)
        runtime.event_manager.publish(build_event(_BACKGROUND_TYPE))

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
