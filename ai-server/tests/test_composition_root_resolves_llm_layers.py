"""The composition root's gateway must resolve every layer to its declared host.

`tests/test_egress_gate.py` pins the shipped *allowlist*, and `scripts/verify_llm_layers.py`
builds its own gateway. Neither can see a divergence inside `runtime._build_runtime` — the
one place where the shipped `settings.json`, the shipped `llm.yaml` and the gateway are
actually joined. Measured 2026-10-06: the composition root *does* resolve correctly
(`gateway._settings_resolver is runtime.settings_resolver`), but **nothing failed if it
stopped**: `configure_egress_gate(settings_store=...)` could be left to the built-in
defaults — which differ from the shipped file in exactly three keys, all egress
permissions — and every cloud profile would degrade to Mock, with the gate logging a
warning and no test reddening.

So this boots the real `get_runtime()` and measures the **resolved provider** per layer:
a provider is built for a layer's declared host exactly when the gate permits it. That is
the property the user-visible claim ("L2 runs on `deepseek-v4-flash`") actually rests on.
"""

from __future__ import annotations

import pytest

from aegis_ai.egress import is_local_destination
from aegis_ai.llm.factory import egress_allows_llm
from aegis_ai.llm.layer_profiles import LAYER_L1, LAYER_L2, LAYER_L3, layer_to_profile

pytestmark = pytest.mark.egress


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    """Boot the real runtime, but never leave its ``status-check`` thread running.

    Same shape as ``test_runtime_singleton.py``'s fixture, and for the same reason: the
    thread re-resolves the LAN endpoints into a process-global cache and would corrupt
    ``test_endpoint_resolver.py`` roughly ninety files away.
    """
    yield

    from aegis_ai.runtime import reset_runtime_for_tests

    reset_runtime_for_tests()


def _resolved_host(provider) -> str | None:
    """The host a provider was actually built for, or ``None`` when it has none.

    Both cloud providers store ``self._base_url``; ``MockLLMProvider`` has no such
    attribute, and the degraded local path builds an ``OpenAIProvider`` for the *local*
    endpoint — so the class alone cannot tell "resolved the declared host" from
    "degraded". The attribute can. Reading a private attribute is deliberate: there is no
    accessor, and renaming it makes this pin fail **loudly** rather than pass vacuously.
    """
    return getattr(provider, "_base_url", None)


def test_the_composition_root_resolves_every_layer_to_its_declared_host(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))

    from aegis_ai.runtime import get_runtime

    runtime = get_runtime()
    resolver = runtime.settings_resolver
    gateway = runtime.llm_gateway
    assert gateway is not None, "the composition root built no LLM gateway"

    for layer in (LAYER_L1, LAYER_L2, LAYER_L3):
        settings = resolver.resolve(profile_id=layer_to_profile(layer))
        assert settings.base_url, f"{layer} declares no base_url"
        assert egress_allows_llm(settings.base_url), (
            f"{layer} -> {settings.base_url!r} is not permitted by the shipped allowlist, "
            "so the layer is declared and inert (the gateway degrades it to Mock)"
        )

        # The gateway resolves profiles through *its own* resolver, and `_resolve` falls
        # back to a bare `LLMSettings()` when it has none — a silent "every layer runs on
        # defaults" with no error anywhere. So a dropped `settings_resolver=` must redden
        # here, not merely be caught by reading the constructor.
        via_gateway = gateway._resolve(layer_to_profile(layer))
        assert via_gateway.base_url == settings.base_url, (
            f"{layer}: the gateway resolved its own profile to base_url="
            f"{via_gateway.base_url!r}, not {settings.base_url!r} — the composition root did "
            "not hand its gateway the resolver it built"
        )

        provider = gateway._get_provider_for_profile(settings)
        assert provider is not None, f"{layer} resolved to no provider at all"
        assert _resolved_host(provider) == settings.base_url.strip(), (
            f"{layer} resolved to {type(provider).__name__} built for "
            f"{_resolved_host(provider)!r}, not {settings.base_url!r} — the composition "
            "root's gateway is not receiving its settings resolver, or the egress gate is "
            "not reading the shipped settings.json"
        )


def test_the_composition_root_gateway_builds_no_provider_for_a_denied_host(monkeypatch, tmp_path) -> None:
    """Negative control: the gateway really consults the gate.

    Without this, the test above would pass even if ``_get_provider_for_profile`` never
    asked the gate at all. The denied profile is **discovered** rather than named, so
    permitting its host later cannot leave this control passing vacuously — it would
    simply move to whichever external profile is denied next.
    """
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))

    from aegis_ai.runtime import get_runtime

    runtime = get_runtime()
    resolver = runtime.settings_resolver

    denied = [
        profile_id
        for profile_id in resolver.list_profile_ids()
        if (settings := resolver.resolve(profile_id=profile_id)).base_url
        and not is_local_destination(settings.base_url)
        and not egress_allows_llm(settings.base_url)
    ]
    assert denied, (
        "no declared profile points at a denied external host, so this control is vacuous "
        "and proves nothing about whether the gateway consults the gate"
    )

    for profile_id in denied:
        settings = resolver.resolve(profile_id=profile_id)
        provider = runtime.llm_gateway._get_provider_for_profile(settings)
        assert _resolved_host(provider) != settings.base_url.strip(), (
            f"{profile_id} is denied by the gate ({settings.base_url!r}) yet the gateway "
            f"built a {type(provider).__name__} for that host"
        )
