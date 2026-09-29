"""The local LLM path completes — and transmits nothing while doing so.

Completion criterion ② of the goal-change plan. The owner's decision was to drop
the local-LLM *feature* (no Ollama requirement) while keeping ``llm.yaml`` in
``mode: local``. So the contract under test is **not** "Ollama is installed". It is:

1. local mode never resolves to a cloud destination;
2. a dead local endpoint degrades to Mock rather than stalling or reaching out;
3. the generation path (the L1/L2/L3 route) completes and records **zero** external
   egress attempts.

Point 3 is the one that matters for the single constraint: "it works" is only
acceptable in combination with "it sent nothing".
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

# Every test in this module guards the single constraint. The marker is counted by
# --require-egress-tests (see conftest.py) so this suite can never silently run empty.
pytestmark = pytest.mark.egress

_LLM_YAML = Path(__file__).resolve().parents[1] / "config" / "llm.yaml"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _config() -> dict[str, Any]:
    return yaml.safe_load(_LLM_YAML.read_text(encoding="utf-8"))


def _profiles() -> dict[str, dict[str, Any]]:
    return _config()["profiles"]


def _profile_names() -> list[str]:
    return sorted(_profiles())


def _resolver():
    from aegis_ai.llm.settings_resolver import LLMSettingsResolver

    return LLMSettingsResolver(str(_LLM_YAML))


class _RecordingAudit:
    """Stands in for the AuditManager: records what the gate was asked to do."""

    def __init__(self) -> None:
        self.entries: list[Any] = []

    def append(self, entry: Any) -> None:
        self.entries.append(entry)


def _gateway(monkeypatch, *, reachable: bool, audit: Any = None):
    """Build the real L1/L2/L3 gateway against the shipped llm.yaml.

    ``configure_egress_gate(audit=...)`` with no settings store leaves every lock on
    its closed default, which is the shipped state.
    """
    from aegis_ai.egress import configure_egress_gate
    from aegis_ai.llm import factory
    from aegis_ai.llm.gateway import LLMGateway

    monkeypatch.setattr(factory, "_is_reachable", lambda *_args, **_kwargs: reachable)
    configure_egress_gate(audit=audit)
    return LLMGateway(router=None, settings_resolver=_resolver())


# ── The shipped configuration ─────────────────────────────────────────────────


def test_the_shipped_llm_config_is_local_mode():
    assert _config().get("mode") == "local"


@pytest.mark.parametrize("profile_name", _profile_names())
def test_local_mode_never_resolves_to_a_cloud_destination(profile_name: str):
    """Every declared profile must resolve inside the environment in local mode."""
    from aegis_ai.egress import is_local_destination

    settings = _resolver().resolve(profile_id=profile_name)

    assert settings.base_url, f"profile '{profile_name}' resolved to an empty base_url"
    assert is_local_destination(settings.base_url), (
        f"profile '{profile_name}' resolves to {settings.base_url!r}, which is outside "
        f"the local environment. Add it to LLMSettingsResolver._LOCAL_PROFILE_MAP."
    )


def test_every_cloud_profile_is_covered_by_the_local_remap():
    """Drift guard for the invariant above.

    Adding a cloud profile to llm.yaml without adding it to the remap would make the
    parametrized test fail — this test says *why*, and catches the case where the new
    profile happens to be unreachable through ``resolve()`` in some other way.
    """
    from aegis_ai.egress import is_local_destination
    from aegis_ai.llm.settings_resolver import LLMSettingsResolver

    remap = LLMSettingsResolver._LOCAL_PROFILE_MAP
    uncovered = [
        name
        for name, profile in _profiles().items()
        if not is_local_destination(str(profile.get("base_url", "")))
        and name not in remap
    ]

    assert uncovered == [], (
        f"{uncovered} declare an external base_url but are not in _LOCAL_PROFILE_MAP, "
        f"so in local mode they resolve to a cloud host."
    )


def test_the_default_profile_resolves_locally():
    """A bare ``resolve()`` is the fallback for every caller that omits a profile."""
    from aegis_ai.egress import is_local_destination

    assert is_local_destination(_resolver().resolve().base_url)


# ── The generation path ───────────────────────────────────────────────────────


def test_generation_completes_when_the_local_endpoint_is_down(monkeypatch):
    """No Ollama running must not break the pipeline — it degrades to Mock."""
    gateway = _gateway(monkeypatch, reachable=False)

    response = gateway.generate("Hello, are you there?", profile="chat_balanced")

    assert response is not None
    assert response.success is True, f"the local path failed instead of degrading: {response.error}"
    assert response.content


def test_generation_uses_the_local_endpoint_when_it_is_up(monkeypatch):
    """Guard the guard: the Mock fallback above must not be unconditional."""
    gateway = _gateway(monkeypatch, reachable=True)

    from aegis_ai.llm.settings_resolver import LLMSettingsResolver

    settings = LLMSettingsResolver(str(_LLM_YAML)).resolve(profile_id="chat_balanced")
    provider = gateway._get_provider_for_profile(settings)

    assert provider is not None
    assert type(provider).__name__ != "MockLLMProvider"
    base_url = str(getattr(provider, "_base_url", None) or getattr(provider, "base_url", ""))
    assert "localhost:11434" in base_url or "127.0.0.1:11434" in base_url


def test_generation_attempts_no_external_destination(monkeypatch):
    """The whole point: the path works *and* sends nothing outside the environment.

    Every destination the gate was consulted about is inspected. A Mock response is
    not by itself proof of safety — a provider could have been built for a cloud host
    and only failed later — so this asserts on the gate traffic, not the response.
    """
    from aegis_ai.egress import is_local_destination

    attempts = _RecordingAudit()
    gateway = _gateway(monkeypatch, reachable=False, audit=attempts)

    response = gateway.generate("Summarise my private notes", profile="chat_balanced")
    assert response.success is True

    # Non-empty proves the gate was actually consulted; otherwise `external == []`
    # below would be vacuously true and this test would guard nothing.
    assert attempts.entries, "the generation path never consulted the egress gate"

    destinations = [
        str(entry.detail.get("destination", ""))
        for entry in attempts.entries
        if getattr(entry, "detail", None)
    ]
    external = [destination for destination in destinations if not is_local_destination(destination)]

    assert external == [], f"the local path consulted the gate about external hosts: {external}"


def test_generation_attempts_no_external_destination_across_every_profile(monkeypatch):
    """Same guarantee for each profile the L1/L2/L3 layers actually use."""
    from aegis_ai.egress import is_local_destination

    for profile_name in ("l1_default", "l2_default", "l3_default", "tool_planning", "vision_observation"):
        attempts = _RecordingAudit()
        gateway = _gateway(monkeypatch, reachable=False, audit=attempts)

        response = gateway.generate("ping", profile=profile_name)
        assert response.success is True, f"{profile_name}: {response.error}"

        external = [
            str(entry.detail.get("destination", ""))
            for entry in attempts.entries
            if getattr(entry, "detail", None)
            and not is_local_destination(str(entry.detail.get("destination", "")))
        ]
        assert external == [], f"{profile_name} consulted the gate about external hosts: {external}"
