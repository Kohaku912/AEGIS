#!/usr/bin/env python
"""Verify that AEGIS's L1/L2/L3 layers actually run on the models they declare.

A layer profile whose ``base_url`` is not named in ``privacy.egress_allowed_hosts``
(``config/settings.json``) is **denied by the egress gate and silently degrades to Mock**
— ``gateway._get_provider_for_profile`` consults the gate before constructing a cloud
provider, and ``_local_or_mock`` never returns a cloud provider. So *declared* and
*resolves* are two different claims, and only the second one means AEGIS works.

This drives the real artefacts — the real settings store, the real gate, the real
``llm.yaml`` resolver and the real provider factory — and reports what each layer
*resolved to*, not what it asked for.

Usage (from ``ai-server/``)::

    PYTHONPATH=src python scripts/verify_llm_layers.py            # config + resolution
    PYTHONPATH=src python scripts/verify_llm_layers.py --live     # + one real call per layer

Exit code is 0 only when every layer resolves to a permitted, non-Mock provider (and, with
``--live``, when every live call succeeds).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

AI_SERVER = Path(__file__).resolve().parents[1]
REPO_ROOT = AI_SERVER.parent
sys.path.insert(0, str(AI_SERVER / "src"))

# The layer profiles, discovered from the package rather than hardcoded.
from aegis_ai.llm.layer_profiles import LAYER_L1, LAYER_L2, LAYER_L3, layer_to_profile  # noqa: E402


def _load_env() -> None:
    """Load the repo-root .env, where the API keys live (never committed)."""
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover - dotenv is an install-time dependency
        print("python-dotenv is not installed; relying on the ambient environment", file=sys.stderr)
        return
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)
    else:
        print(f"note: {env_path} does not exist; relying on the ambient environment", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="make one real LLM call per layer")
    args = parser.parse_args()

    _load_env()

    from aegis_ai.egress import EgressDecision, EgressRequest, configure_egress_gate, verify_egress_configuration
    from aegis_ai.llm.gateway import LLMGateway
    from aegis_ai.llm.router import LLMRouter
    from aegis_ai.llm.settings_resolver import LLMSettingsResolver
    from aegis_ai.settings.store import SettingsStore

    settings_path = AI_SERVER / "config" / "settings.json"
    llm_config = AI_SERVER / "config" / "llm.yaml"
    audit_path = AI_SERVER / "data" / "settings_audit.jsonl"

    # ── The egress permission, which is what makes a cloud profile reachable ──
    store = SettingsStore(path=str(settings_path), audit_path=str(audit_path))
    gate = configure_egress_gate(settings_store=store)
    status = verify_egress_configuration(gate, llm_config_path=llm_config)
    print(f"egress configuration : ok={status.ok} violations={status.violations or '[]'}")
    print(f"permitted hosts      : {sorted(gate.allowed_hosts)}")
    reachable = status.summary.get("reachable_destinations") or {}
    for host, ok in sorted(reachable.items()):
        print(f"  {'ALLOW' if ok else 'DENY ':4s} {host}")

    resolver = LLMSettingsResolver(str(llm_config))
    router = LLMRouter(settings_store=store, audit_log=None)
    gateway = LLMGateway(router=router, settings_resolver=resolver, prompt_registry=None, audit_log=None)

    failures: list[str] = []
    for layer in (LAYER_L1, LAYER_L2, LAYER_L3):
        profile_id = layer_to_profile(layer)
        settings = resolver.resolve(profile_id=profile_id)
        decision = gate.check(
            EgressRequest(destination=settings.base_url, purpose="llm.chat", component="verify_llm_layers")
        )
        key = os.getenv(settings.api_key_env, "") if settings.api_key_env else ""
        provider = gateway._get_provider_for_profile(settings)  # the same call the public path makes
        provider_name = type(provider).__name__

        print(
            f"\n{layer}: profile={profile_id} provider={settings.provider} model={settings.model}\n"
            f"    base_url={settings.base_url}\n"
            f"    api_key_env={settings.api_key_env} key_present={bool(key)}\n"
            f"    gate={decision.value} resolved_provider={provider_name}"
        )

        if decision is not EgressDecision.ALLOW:
            failures.append(f"{layer}: {settings.base_url} is not permitted by the egress allowlist")
        if provider_name == "MockLLMProvider":
            failures.append(f"{layer}: resolved to MockLLMProvider — the profile is declared and inert")

        if args.live:
            response = gateway.request(layer, "Reply with exactly: OK", max_tokens=32)
            print(
                f"    live: success={response.success} content={response.content!r} "
                f"used={response.provider_used}/{response.model_used}"
            )
            if not response.success or response.provider_used == "mock":
                failures.append(f"{layer}: live call did not come from a real provider ({response.error!r})")

    print()
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print(f"OK: every layer resolves to a permitted, non-Mock provider{' and answered live' if args.live else ''}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
