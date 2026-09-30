"""Egress gate tests — regression protection for AEGIS's single constraint.

The only constraint is user-information egress — **re-scoped 2026-09-30**: *unpermitted*
disclosure is forbidden, outbound connections are allowed, and disclosure the user permits
is allowed. These tests exist so that no future change can silently bypass the check —
today the gate still enforces the pre-re-scope deny-all form.

They also cover the *"ineffective flag"* class of bug: a settings flag that exists
but is never read (the same shape as the retired ``web_search_allowed``).
"""

from __future__ import annotations

from typing import Any

import pytest

from aegis_ai.egress import (
    EgressConfigurationError,
    EgressDecision,
    EgressDenied,
    EgressGate,
    EgressRequest,
    classify_destination,
    is_local_destination,
    verify_egress_configuration,
)
from aegis_ai.settings.models import AEGISSettings, PrivacySettings, VoiceSettings

# Every test in this module guards the single constraint. The marker is counted by
# --require-egress-tests (see conftest.py) so this suite can never silently run empty.
pytestmark = pytest.mark.egress


class _FakeStore:
    """Minimal SettingsStore stand-in returning a fixed AEGISSettings."""

    def __init__(self, **privacy_overrides) -> None:
        self._settings = AEGISSettings(privacy=PrivacySettings(**privacy_overrides))

    def get(self) -> AEGISSettings:
        return self._settings


class _FakeAudit:
    def __init__(self) -> None:
        self.entries: list[Any] = []

    def append(self, entry: Any) -> None:
        self.entries.append(entry)


# ── Defaults ──────────────────────────────────────────────────────────────────


def test_privacy_defaults_are_closed():
    """Every egress-related flag must default to closed."""
    privacy = PrivacySettings()
    assert privacy.external_egress_allowed is False
    assert privacy.external_llm_allowed is False
    assert privacy.web_search_allowed is False
    assert privacy.egress_allowed_hosts == []


def test_voice_external_default_is_closed():
    assert VoiceSettings().external_voice_api_allowed is False


# ── Destination classification ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "destination",
    [
        "http://localhost:11434/v1",
        "http://127.0.0.1:50051",
        "http://[::1]:8090",
        "http://192.168.1.10:50052",
        "http://10.0.0.5",
        "http://172.16.4.2:50055",
        "http://100.101.102.103",  # Tailscale CGNAT
        "http://[fd7a:115c:a1e0::1]:50051",  # IPv6 ULA
        "orangepi",  # single-label LAN host
        "room-server.local",
        "/var/run/aegis.sock",
        "unix:/tmp/aegis.sock",
    ],
)
def test_local_destinations_are_local(destination):
    assert is_local_destination(destination) is True
    assert classify_destination(destination) == "local"


@pytest.mark.parametrize(
    "destination",
    [
        "https://api.deepseek.com",
        "https://api.deepseek.com/v1/chat/completions",
        "https://api.openai.com/v1",
        "https://ws-nuimlupsvbr9m8x1.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1",
        "https://api.typesafe.ai/v1/systemone",
        "duckduckgo.com",
        "https://api.telegram.org/bot123/sendMessage",
        "8.8.8.8",
    ],
)
def test_external_destinations_are_external(destination):
    assert is_local_destination(destination) is False
    assert classify_destination(destination) == "external"


def test_empty_destination_is_unknown():
    assert classify_destination("") == "unknown"
    assert classify_destination("   ") == "unknown"


@pytest.mark.parametrize("destination", ["not a url", "ftp://weird!!host"])
def test_malformed_destination_fails_closed(destination):
    """Malformed input must not be mistaken for a single-label LAN hostname.

    A single-label host is local by design (it cannot be public DNS). That rule
    must not swallow garbage, or a typo'd destination would be *allowed*.
    """
    assert classify_destination(destination) == "external"
    gate = EgressGate(settings_store=_FakeStore())
    assert gate.allow(EgressRequest(destination, purpose="llm.chat", component="t")) is False


# ── Gate decisions ────────────────────────────────────────────────────────────


def test_external_is_denied_with_default_settings():
    gate = EgressGate(settings_store=_FakeStore())
    decision = gate.check(
        EgressRequest("https://api.deepseek.com", purpose="llm.chat", component="test")
    )
    assert decision is EgressDecision.DENY


def test_local_is_allowed_even_when_closed():
    gate = EgressGate(settings_store=_FakeStore())
    decision = gate.check(
        EgressRequest("http://localhost:11434/v1", purpose="llm.chat", component="test")
    )
    assert decision is EgressDecision.ALLOW


def test_unknown_destination_fails_closed():
    gate = EgressGate(settings_store=_FakeStore())
    decision = gate.check(EgressRequest("", purpose="llm.chat", component="test"))
    assert decision is EgressDecision.DENY


def test_flag_alone_does_not_open_egress():
    """A feature flag without an allowlist must not permit external egress."""
    gate = EgressGate(settings_store=_FakeStore(external_llm_allowed=True))
    decision = gate.check(
        EgressRequest("https://api.deepseek.com", purpose="llm.chat", component="test")
    )
    assert decision is EgressDecision.DENY


def test_allowlist_alone_does_not_open_egress():
    """An allowlist without the master switch must not permit external egress."""
    gate = EgressGate(
        settings_store=_FakeStore(),
        allowed_hosts=["api.deepseek.com"],
    )
    decision = gate.check(
        EgressRequest("https://api.deepseek.com", purpose="llm.chat", component="test")
    )
    assert decision is EgressDecision.DENY


def test_all_locks_open_permits_external():
    """Master switch + feature flag + allowlist together permit egress."""
    gate = EgressGate(
        settings_store=_FakeStore(
            external_egress_allowed=True,
            external_llm_allowed=True,
        ),
        allowed_hosts=["api.deepseek.com"],
    )
    decision = gate.check(
        EgressRequest("https://api.deepseek.com", purpose="llm.chat", component="test")
    )
    assert decision is EgressDecision.ALLOW


def test_require_raises_egress_denied():
    gate = EgressGate(settings_store=_FakeStore())
    with pytest.raises(EgressDenied) as excinfo:
        gate.require(
            EgressRequest("https://api.deepseek.com", purpose="llm.chat", component="test")
        )
    assert "api.deepseek.com" in str(excinfo.value)


# ── "Ineffective flag" detector ───────────────────────────────────────────────


def test_web_search_flag_is_actually_read():
    """``web_search_allowed`` must influence the decision for web purposes.

    This is the detector for the retired "flag exists but is never read" bug.
    """
    closed = EgressGate(settings_store=_FakeStore())
    opened = EgressGate(
        settings_store=_FakeStore(external_egress_allowed=True, web_search_allowed=True),
        allowed_hosts=["duckduckgo.com"],
    )
    request = EgressRequest("https://duckduckgo.com", purpose="web.search", component="test")

    assert closed.check(request) is EgressDecision.DENY
    assert opened.check(request) is EgressDecision.ALLOW

    # With the flag off, even an allowlisted host is refused.
    flag_off = EgressGate(
        settings_store=_FakeStore(external_egress_allowed=True, web_search_allowed=False),
        allowed_hosts=["duckduckgo.com"],
    )
    assert flag_off.check(request) is EgressDecision.DENY


def test_unknown_purpose_is_denied_when_open():
    """An unmapped purpose must never be permitted, even with the master switch on."""
    gate = EgressGate(
        settings_store=_FakeStore(external_egress_allowed=True),
        allowed_hosts=["example.com"],
    )
    decision = gate.check(
        EgressRequest("https://example.com", purpose="something.unmapped", component="test")
    )
    assert decision is EgressDecision.DENY


# ── Audit ─────────────────────────────────────────────────────────────────────


def test_decisions_are_audited():
    audit = _FakeAudit()
    gate = EgressGate(settings_store=_FakeStore(), audit=audit)
    gate.check(EgressRequest("https://api.deepseek.com", purpose="llm.chat", component="c1"))
    gate.check(EgressRequest("http://localhost:11434/v1", purpose="llm.chat", component="c2"))

    assert len(audit.entries) == 2
    denied, allowed = audit.entries
    # Entries are AuditEntry instances (the contract AuditLog/AuditManager expect).
    assert denied.action == "egress_decision"
    assert denied.decision == "deny"
    assert denied.detail["destination"] == "https://api.deepseek.com"
    assert allowed.decision == "allow"
    assert allowed.detail["destination"] == "http://localhost:11434/v1"


# ── Startup assertion ─────────────────────────────────────────────────────────


def test_status_ok_when_closed():
    gate = EgressGate(settings_store=_FakeStore())
    status = gate.status()
    assert status.ok is True
    assert status.violations == []


def test_status_reports_violations_when_open():
    gate = EgressGate(
        settings_store=_FakeStore(
            external_egress_allowed=True,
            external_llm_allowed=True,
            web_search_allowed=True,
        ),
        allowed_hosts=["api.deepseek.com"],
    )
    status = gate.status()
    assert status.ok is False
    assert any("external_egress_allowed" in v for v in status.violations)
    assert any("external_llm_allowed" in v for v in status.violations)
    assert any("web_search_allowed" in v for v in status.violations)
    assert any("allowlist" in v for v in status.violations)


def test_verify_passes_when_closed():
    gate = EgressGate(settings_store=_FakeStore())
    status = verify_egress_configuration(gate, mode="fail")
    assert status.ok is True


def test_verify_fails_closed_in_fail_mode():
    gate = EgressGate(settings_store=_FakeStore(external_llm_allowed=True))
    with pytest.raises(EgressConfigurationError):
        verify_egress_configuration(gate, mode="fail")


def test_verify_warns_in_warn_mode():
    gate = EgressGate(settings_store=_FakeStore(external_llm_allowed=True))
    status = verify_egress_configuration(gate, mode="warn")
    assert status.ok is False
    assert status.violations


# ── LLM factory integration ───────────────────────────────────────────────────


def _provider_base_url(provider) -> str:
    """Read the base URL from a provider regardless of public/private naming."""
    return str(getattr(provider, "_base_url", None) or getattr(provider, "base_url", "") or "")


def test_llm_factory_refuses_cloud_when_closed(monkeypatch):
    """A cloud base_url must never produce a cloud provider while egress is closed."""
    from aegis_ai.egress import configure_egress_gate
    from aegis_ai.llm import factory

    configure_egress_gate(settings_store=_FakeStore())
    monkeypatch.setenv("LLM_API_KEY", "fake-key")

    provider = factory.create_llm_provider(
        provider_name="deepseek",
        base_url="https://api.deepseek.com",
    )

    base_url = _provider_base_url(provider)
    assert "api.deepseek.com" not in base_url
    # It must degrade to a local endpoint or a Mock, never to the cloud.
    assert base_url.startswith("http://localhost") or type(provider).__name__ == "MockLLMProvider"


def test_llm_factory_allows_local_ollama_when_closed(monkeypatch):
    """A reachable local Ollama endpoint is permitted — it is inside the environment."""
    from aegis_ai.egress import configure_egress_gate
    from aegis_ai.llm import factory

    configure_egress_gate(settings_store=_FakeStore())
    monkeypatch.setenv("LLM_API_KEY", "fake-key")
    # Deterministic: pretend the local endpoint is listening, so the factory must
    # hand back a provider bound to it rather than degrading to Mock.
    monkeypatch.setattr(factory, "_is_reachable", lambda *_a, **_k: True)

    provider = factory.create_llm_provider(
        provider_name="openai",
        base_url="http://localhost:11434/v1",
        model="qwen2.5:3b",
    )
    assert _provider_base_url(provider) == "http://localhost:11434/v1"


def test_llm_factory_degrades_to_mock_when_local_endpoint_is_down(monkeypatch):
    """A dead local endpoint must degrade to Mock — never to a cloud provider.

    Constructing an OpenAI-compatible client for a dead endpoint does not fail at
    construction; it fails at call time after SDK retries, which stalls the pipeline
    and emits error events. The factory must probe reachability first.
    """
    from aegis_ai.egress import configure_egress_gate
    from aegis_ai.llm import factory

    configure_egress_gate(settings_store=_FakeStore())
    monkeypatch.setattr(factory, "_is_reachable", lambda *_a, **_k: False)

    provider = factory.create_llm_provider(
        provider_name="openai",
        base_url="http://localhost:11434/v1",
        model="qwen2.5:3b",
    )
    assert type(provider).__name__ == "MockLLMProvider"
    # And it must not have quietly fallen back to the cloud.
    assert "api.openai.com" not in _provider_base_url(provider)


# ── LLM gateway (the main L1/L2/L3 path) ──────────────────────────────────────


def _gateway_profile(**overrides):
    from aegis_ai.llm.settings_resolver import LLMSettings

    base = {
        "provider": "openai",
        "model": "deepseek-v4-flash",
        "api_key_env": "LLM_API_KEY",
        "base_url": "https://api.deepseek.com",
    }
    base.update(overrides)
    return LLMSettings(**base)


def test_llm_gateway_denies_cloud_profile_destination(monkeypatch):
    """The gateway builds providers itself, so it must consult the gate itself.

    Regression: before this was wired, a profile pointing at a cloud host was
    constructed and called directly, bypassing the egress gate entirely.
    """
    from aegis_ai.egress import configure_egress_gate
    from aegis_ai.llm import factory
    from aegis_ai.llm.gateway import LLMGateway

    configure_egress_gate(settings_store=_FakeStore())  # external egress closed
    monkeypatch.setenv("LLM_API_KEY", "fake-key")
    monkeypatch.setattr(factory, "_is_reachable", lambda *_a, **_k: False)

    gateway = LLMGateway(router=None)
    provider = gateway._get_provider_for_profile(_gateway_profile())

    assert provider is not None
    assert type(provider).__name__ == "MockLLMProvider"
    assert "api.deepseek.com" not in _provider_base_url(provider)


def test_llm_gateway_denies_typesafe_cloud_profile(monkeypatch):
    """A cloud 'typesafe' profile must not produce a TypeSafeProvider when closed."""
    from aegis_ai.egress import configure_egress_gate
    from aegis_ai.llm import factory
    from aegis_ai.llm.gateway import LLMGateway

    configure_egress_gate(settings_store=_FakeStore())
    monkeypatch.setattr(factory, "_is_reachable", lambda *_a, **_k: False)

    gateway = LLMGateway(router=None)
    provider = gateway._get_provider_for_profile(
        _gateway_profile(
            provider="typesafe",
            model="jev-latest",
            api_key_env="TYPESAFE_API_KEY",
            base_url="https://api.typesafe.ai/v1/systemone",
        )
    )
    assert type(provider).__name__ != "TypeSafeProvider"


def test_llm_gateway_degrades_dead_local_endpoint_to_mock(monkeypatch):
    """A permitted-but-dead local endpoint degrades to Mock instead of stalling."""
    from aegis_ai.egress import configure_egress_gate
    from aegis_ai.llm import factory
    from aegis_ai.llm.gateway import LLMGateway

    configure_egress_gate(settings_store=_FakeStore())
    monkeypatch.setattr(factory, "_is_reachable", lambda *_a, **_k: False)

    gateway = LLMGateway(router=None)
    provider = gateway._get_provider_for_profile(
        _gateway_profile(base_url="http://localhost:11434/v1", model="qwen2.5:3b")
    )
    assert type(provider).__name__ == "MockLLMProvider"


# ── Other guarded egress points ───────────────────────────────────────────────


def test_weather_fetch_is_denied_when_closed():
    """Weather requests carry the user's coordinates — they must be gated."""
    from aegis_ai.briefing.provider import _weather_egress_allowed
    from aegis_ai.egress import configure_egress_gate

    configure_egress_gate(settings_store=_FakeStore())
    assert _weather_egress_allowed("https://api.open-meteo.com/v1/forecast") is False


def test_openhands_remote_call_is_denied_when_closed():
    """The OpenHands remote backend posts task context — it must be gated."""
    from aegis_ai.agents.backends.openhands.workspace import RemoteAPIError, _default_http_post
    from aegis_ai.egress import configure_egress_gate

    configure_egress_gate(settings_store=_FakeStore())
    with pytest.raises(RemoteAPIError) as excinfo:
        _default_http_post("https://agent.example.com/api", payload={"task": "x"})
    assert "Egress denied" in str(excinfo.value)


def test_openhands_remote_call_is_permitted_to_local_agent_server(monkeypatch):
    """A local agent server is inside the environment and stays permitted."""
    from aegis_ai.agents.backends.openhands import workspace as ws
    from aegis_ai.egress import configure_egress_gate

    configure_egress_gate(settings_store=_FakeStore())

    calls = []

    def _fake_urlopen(req, timeout=None):
        calls.append(req.full_url)
        raise OSError("stop here — we only care that egress allowed the call")

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)
    with pytest.raises(Exception):
        ws._default_http_post("http://localhost:50060/api", payload={"task": "x"})
    assert calls == ["http://localhost:50060/api"]


# ── Shipped configuration ─────────────────────────────────────────────────────


def _llm_yaml_path():
    from pathlib import Path

    return Path(__file__).resolve().parents[1] / "config" / "llm.yaml"


def test_shipped_llm_config_is_local_only():
    """The shipped llm.yaml must be local-mode with a local vision profile."""
    import yaml

    data = yaml.safe_load(_llm_yaml_path().read_text(encoding="utf-8"))
    assert data.get("mode") == "local"

    resolver_map = data["profiles"]
    assert "local_vision" in resolver_map
    vision = resolver_map["local_vision"]
    assert "localhost" in vision["base_url"] or "127.0.0.1" in vision["base_url"]


def test_startup_assertion_passes_with_shipped_config():
    """The real llm.yaml must satisfy the startup readiness check."""
    from aegis_ai.egress import EgressGate, verify_egress_configuration

    gate = EgressGate(settings_store=_FakeStore())
    status = verify_egress_configuration(
        gate, llm_config_path=_llm_yaml_path(), mode="fail"
    )
    assert status.ok is True
    assert status.summary["local_llm_readiness"] == "ok"


def test_vision_profile_resolves_to_local_in_local_mode():
    """vision_observation must map to a local profile — images may not go to the cloud."""
    from aegis_ai.llm.settings_resolver import LLMSettingsResolver

    assert LLMSettingsResolver._LOCAL_PROFILE_MAP.get("vision_observation") == "local_vision"

    resolver = LLMSettingsResolver(str(_llm_yaml_path()))
    resolved = resolver.resolve(profile_id="vision_observation")
    assert "localhost" in resolved.base_url or "127.0.0.1" in resolved.base_url


def test_shipped_settings_json_is_closed():
    """config/settings.json must ship with every egress flag closed."""
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "config" / "settings.json"
    privacy = json.loads(path.read_text(encoding="utf-8"))["privacy"]

    assert privacy["external_egress_allowed"] is False
    assert privacy["external_llm_allowed"] is False
    assert privacy["web_search_allowed"] is False
    assert privacy["egress_allowed_hosts"] == []
