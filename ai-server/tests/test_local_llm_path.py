"""The local LLM path completes — and nothing leaves without permission.

Completion criterion ② of the goal-change plan. The owner's decision was to drop
the local-LLM *feature* (no Ollama requirement) while keeping ``llm.yaml`` in
``mode: local``.

**Re-scoped 2026-10-03** (owner: "JEV only, no local"). That earlier decision was
reversed: the shipped config is now ``mode: cloud`` so that ``l1_default`` actually
reaches TypeSafe JEV, because ``settings_resolver._LOCAL_PROFILE_MAP`` remaps
``l1_default`` to Ollama in local mode and the JEV declaration was therefore dead
(measured 2026-10-02). "No local LLM" is a standing decision about *which* model runs
(``docs/GOAL-CHANGE.md``), so ``local`` was the wrong value for the shipped file.

What survives, and what this module now pins:

1. **local mode** never resolves to a cloud destination — a property of the *resolver*,
   tested against a local-mode config rather than whichever mode is shipped;
2. a dead local endpoint degrades to Mock rather than stalling or reaching out;
3. the generation path completes **and the gate allows no external destination that is
   not permitted** — the re-scoped form of "it sent nothing". L1 legitimately consults
   the gate about JEV, so the invariant is about *permission*, not about silence.
"""

from __future__ import annotations

import tempfile
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


def _local_mode_config_path() -> Path:
    """The shipped config with ``mode: local``, written to a temp file.

    The resolver's local-mode behaviour must be tested against a *local-mode* config.
    Reading the shipped file directly would couple the resolver's contract to whichever
    mode happens to be shipped — measured 2026-10-03, when moving the shipped config to
    ``cloud`` broke every local-mode assertion here for a reason that had nothing to do
    with the resolver.
    """
    data = _config()
    data["mode"] = "local"
    path = Path(tempfile.mkdtemp(prefix="aegis-llm-local-")) / "llm.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def _resolver(path: Path | None = None):
    from aegis_ai.llm.settings_resolver import LLMSettingsResolver

    return LLMSettingsResolver(str(path or _LLM_YAML))


class _RecordingAudit:
    """Stands in for the AuditManager: records what the gate was asked to do."""

    def __init__(self) -> None:
        self.entries: list[Any] = []

    def append(self, entry: Any) -> None:
        self.entries.append(entry)


def _gateway(monkeypatch, *, reachable: bool, audit: Any = None, config_path: Path | None = None):
    """Build the real L1/L2/L3 gateway against the shipped (or a local-mode) llm.yaml.

    ``configure_egress_gate(audit=...)`` with no settings store leaves every lock on
    its closed default, which is the conservative state: nothing external is permitted.
    """
    from aegis_ai.egress import configure_egress_gate
    from aegis_ai.llm import factory
    from aegis_ai.llm.gateway import LLMGateway

    monkeypatch.setattr(factory, "_is_reachable", lambda *_args, **_kwargs: reachable)
    configure_egress_gate(audit=audit)
    return LLMGateway(router=None, settings_resolver=_resolver(config_path))


# ── The shipped configuration ─────────────────────────────────────────────────


def test_the_shipped_llm_config_runs_l1_on_jev():
    """The shipped config must reach JEV — that is what `mode: cloud` is for.

    In ``mode: local`` the resolver remaps ``l1_default`` to ``local_decision``
    (Ollama), so the JEV declaration below is never used. Measured 2026-10-02: the file
    said ``provider: typesafe`` while every L1 call ran on ``qwen2.5:3b``.
    """
    config = _config()
    assert config.get("mode") == "cloud", (
        "in local mode `l1_default` is remapped to Ollama, so JEV is never reached"
    )

    l1 = config["profiles"]["l1_default"]
    assert l1["provider"] == "typesafe"
    assert l1["model"] == "jev-latest"

    # The local profiles stay declared: local mode is still a supported configuration,
    # and the remap that uses them is pinned below.
    assert "local_vision" in config["profiles"]


@pytest.mark.parametrize("profile_name", _profile_names())
def test_local_mode_never_resolves_to_a_cloud_destination(profile_name: str):
    """Every declared profile must resolve inside the environment in local mode."""
    from aegis_ai.egress import is_local_destination

    settings = _resolver(_local_mode_config_path()).resolve(profile_id=profile_name)

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

    assert is_local_destination(_resolver(_local_mode_config_path()).resolve().base_url)


# ── The generation path ───────────────────────────────────────────────────────


def test_generation_completes_when_the_local_endpoint_is_down(monkeypatch):
    """No Ollama running must not break the pipeline — it degrades to Mock."""
    gateway = _gateway(monkeypatch, reachable=False, config_path=_local_mode_config_path())

    response = gateway.generate("Hello, are you there?", profile="chat_balanced")

    assert response is not None
    assert response.success is True, f"the local path failed instead of degrading: {response.error}"
    assert response.content


def test_generation_uses_the_local_endpoint_when_it_is_up(monkeypatch):
    """Guard the guard: the Mock fallback above must not be unconditional."""
    from aegis_ai.llm.settings_resolver import LLMSettingsResolver

    config_path = _local_mode_config_path()
    gateway = _gateway(monkeypatch, reachable=True, config_path=config_path)

    settings = LLMSettingsResolver(str(config_path)).resolve(profile_id="chat_balanced")
    provider = gateway._get_provider_for_profile(settings)

    assert provider is not None
    assert type(provider).__name__ != "MockLLMProvider"
    base_url = str(getattr(provider, "_base_url", None) or getattr(provider, "base_url", ""))
    assert "localhost:11434" in base_url or "127.0.0.1:11434" in base_url


def test_generation_allows_no_unpermitted_external_destination(monkeypatch):
    """The whole point: the path works *and* nothing leaves without permission.

    Re-scoped 2026-09-30. This used to assert that the gate was never consulted about an
    external host at all. That is no longer the contract — L1 legitimately consults the
    gate about ``api.typesafe.ai``, which is permitted. The invariant is now about
    **permission**: with a closed gate (no settings store) nothing external may be
    *allowed*. Asserting on the gate's decisions rather than the response keeps this
    honest — a Mock response is not by itself proof that nothing was permitted.
    """
    from aegis_ai.egress import is_local_destination

    attempts = _RecordingAudit()
    gateway = _gateway(monkeypatch, reachable=False, audit=attempts)

    response = gateway.generate("Summarise my private notes", profile="chat_balanced")
    assert response.success is True

    # Non-empty proves the gate was actually consulted; otherwise the assertion below
    # would be vacuously true and this test would guard nothing.
    assert attempts.entries, "the generation path never consulted the egress gate"

    allowed_external = [
        str(entry.detail.get("destination", ""))
        for entry in attempts.entries
        if getattr(entry, "detail", None)
        and str(getattr(entry, "decision", "")) == "allow"
        and not is_local_destination(str(entry.detail.get("destination", "")))
    ]

    assert allowed_external == [], f"the gate allowed external hosts: {allowed_external}"


def test_generation_allows_no_unpermitted_external_destination_across_every_profile(monkeypatch):
    """Same guarantee for each profile the L1/L2/L3 layers actually use."""
    from aegis_ai.egress import is_local_destination

    for profile_name in ("l1_default", "l2_default", "l3_default", "tool_planning", "vision_observation"):
        attempts = _RecordingAudit()
        gateway = _gateway(monkeypatch, reachable=False, audit=attempts)

        response = gateway.generate("ping", profile=profile_name)
        assert response.success is True, f"{profile_name}: {response.error}"

        allowed_external = [
            str(entry.detail.get("destination", ""))
            for entry in attempts.entries
            if getattr(entry, "detail", None)
            and str(getattr(entry, "decision", "")) == "allow"
            and not is_local_destination(str(entry.detail.get("destination", "")))
        ]
        assert allowed_external == [], f"{profile_name}: the gate allowed {allowed_external}"
