"""LLM Provider Factory — creates LLM providers based on configuration.

Automatically selects the right provider based on environment variables:
- LLM_API_KEY + LLM_BASE_URL → DeepSeek/OpenAI provider
- No key → Mock provider

Usage:
    provider = create_llm_provider()
    response = provider.generate(prompt="Hello")
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.llm.factory")

# Load .env file from project root
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent.parent.parent.parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass

# Default endpoint used when a cloud provider is requested without an explicit base_url.
_DEFAULT_CLOUD_BASE_URL = "https://api.openai.com"
# Local Ollama endpoint.
_OLLAMA_BASE_URL = "http://localhost:11434/v1"


def egress_allows_llm(base_url: str | None, *, component: str = "llm.factory") -> bool:
    """Return True when the egress gate permits an LLM call to ``base_url``.

    An empty ``base_url`` with a cloud provider means the SDK default endpoint
    (``api.openai.com``), which is external — so it is checked as such.
    """
    from aegis_ai.egress import EgressRequest, get_egress_gate

    destination = base_url or _DEFAULT_CLOUD_BASE_URL
    return get_egress_gate().allow(
        EgressRequest(
            destination=destination,
            purpose="llm.chat",
            component=component,
            data_summary="LLM prompt and memory context",
        )
    )


def _is_reachable(base_url: str, timeout: float = 0.5) -> bool:
    """Best-effort check that a local endpoint is listening. Never raises."""
    import socket
    from urllib.parse import urlsplit

    try:
        parts = urlsplit(base_url if "://" in base_url else f"http://{base_url}")
        host = parts.hostname or "localhost"
        port = parts.port or (443 if parts.scheme == "https" else 80)
    except Exception:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _local_or_mock(
    audit_log: Any = None,
    model: str | None = None,
    base_url: str | None = None,
) -> Any:
    """Return the local LLM provider when reachable, else a Mock provider.

    Used whenever a cloud provider is refused (by the egress gate or by settings)
    **and** whenever a local endpoint was requested but is not listening.
    **Cloud is never returned.**

    The reachability probe matters: constructing an OpenAI-compatible client for a
    dead endpoint does not fail at construction — it fails at call time after the
    SDK's retry/backoff cycle, which stalls the pipeline and emits error events.
    Probing first keeps the degradation deterministic and fast.

    The local path must be functional (Phase 1-4); Mock is the last-resort fallback
    so AEGIS degrades rather than transmits.
    """
    from aegis_ai.llm.providers.mock import MockLLMProvider
    from aegis_ai.llm.providers.openai_provider import OpenAIProvider

    resolved_base_url = base_url or os.getenv("LLM_LOCAL_BASE_URL", _OLLAMA_BASE_URL)
    local_model = model or os.getenv("LLM_LOCAL_MODEL_NAME", "qwen2.5:3b")

    if _is_reachable(resolved_base_url):
        logger.info("Using local LLM at %s (model=%s)", resolved_base_url, local_model)
        return OpenAIProvider(
            model=local_model,
            api_key="ollama",
            base_url=resolved_base_url,
            audit_log=audit_log,
        )

    logger.warning(
        "Local LLM fallback at %s is not listening — falling back to Mock. "
        "Start Ollama (or set LLM_LOCAL_BASE_URL) for a working local model. "
        "An external provider is used only when the egress gate permits its host "
        "(privacy.egress_allowed_hosts in settings.json), so a refused cloud profile "
        "degrades here rather than transmitting.",
        resolved_base_url,
    )
    return MockLLMProvider()


def create_llm_provider(
    provider_name: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    audit_log: Any = None,
    timeout_seconds: int | None = None,
) -> Any:
    """Create an LLM provider based on configuration.

    Args:
        provider_name: "openai", "deepseek", "mock", or None (auto-detect)
        model: Model name (e.g., "deepseek-v4-flash", "gpt-4o-mini")
        api_key: API key (or reads from OPENAI_API_KEY env)
        base_url: Base URL (or reads from OPENAI_BASE_URL env)
        timeout_seconds: Per-request timeout for providers that take one. Omit to keep
            the provider's own default — but do **not** leave it unset for a profile that
            declares one, or the same profile times out differently depending on which
            path built the provider (2026-10-02 §5.2).

    Returns:
        LLM provider instance
    """
    api_key = api_key or os.getenv("LLM_API_KEY", "")
    base_url = base_url or os.getenv("LLM_BASE_URL", "")
    model_name = model or os.getenv("LLM_MODEL_NAME", "")

    # Detect Ollama local LLM. Reachability is probed so a dead endpoint degrades
    # to Mock instead of stalling on SDK retries (see _local_or_mock).
    if base_url and ("localhost:11434" in base_url or "127.0.0.1:11434" in base_url):
        return _local_or_mock(
            audit_log=audit_log,
            model=model_name or "qwen2.5:7b",
            base_url=base_url,
        )

    # Auto-detect provider
    if provider_name is None:
        if api_key:
            if "deepseek" in (base_url or "").lower():
                provider_name = "deepseek"
            else:
                provider_name = "openai"
        else:
            provider_name = "mock"

    # ── Egress gate: the single constraint ──────────────────────────────────
    # A cloud provider is constructed only for a destination the gate **permits** — the
    # constraint was re-scoped 2026-09-30 to "**unpermitted** user information must never
    # leave the local environment", with outbound connections and user-permitted disclosure
    # allowed. The permission wiring is live: `egress_allows_llm` consults the real gate,
    # which reads `privacy.egress_allowed_hosts` (or a recorded user grant) through the
    # settings store. So this is not a deny-all check, and it still cannot be bypassed by a
    # settings flag alone.
    if provider_name != "mock" and not egress_allows_llm(base_url, component="llm.factory"):
        return _local_or_mock(audit_log=audit_log, model=model_name)

    # Create provider
    if provider_name == "typesafe":
        from aegis_ai.llm.providers.typesafe_provider import TypeSafeProvider

        # Thread `timeout_seconds` through instead of letting the class default win:
        # omitting it made the same profile time out at 30s via this path and at the
        # profile's own value via `gateway._get_provider_for_profile()` (2026-10-02 §5.2).
        kwargs: dict[str, Any] = {}
        if timeout_seconds is not None:
            kwargs["timeout_seconds"] = timeout_seconds
        return TypeSafeProvider(
            model=model_name or model or "jev-latest",
            api_key=api_key or os.getenv("TYPESAFE_API_KEY", ""),
            base_url=base_url or "https://api.typesafe.ai/v1/systemone",
            audit_log=audit_log,
            **kwargs,
        )
    if provider_name in ("openai", "deepseek"):
        from aegis_ai.llm.providers.openai_provider import OpenAIProvider

        default_model = "deepseek-v4-flash" if provider_name == "deepseek" else "gpt-4o-mini"
        return OpenAIProvider(
            model=model_name or default_model,
            api_key=api_key,
            base_url=base_url if base_url else None,
            audit_log=audit_log,
        )
    else:
        from aegis_ai.llm.providers.mock import MockLLMProvider

        return MockLLMProvider()


def create_multimodal_llm_provider(
    provider_name: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    audit_log: Any = None,
    settings_resolver: Any = None,
) -> Any:
    """Create an LLM provider optimized for image/video understanding.

    Resolution order:
    1. Explicit api_key/model/base_url arguments
    2. vision_observation profile from llm.yaml (via settings_resolver)
    3. LLM_VISION_* environment variables
    4. LLM_* environment variables
    5. Mock provider
    """
    profile_api_key = ""
    profile_base_url = ""
    profile_model = ""

    if settings_resolver is not None:
        try:
            vs = settings_resolver.resolve(profile_id="vision_observation")
            profile_api_key = os.getenv(vs.api_key_env, "") if vs.api_key_env else ""
            profile_base_url = vs.base_url or ""
            profile_model = vs.model or ""
        except (KeyError, Exception):
            pass

    api_key = api_key or profile_api_key or os.getenv("LLM_VISION_API_KEY") or os.getenv("LLM_API_KEY", "")
    base_url = base_url or profile_base_url or os.getenv("LLM_VISION_BASE_URL") or os.getenv("LLM_BASE_URL", "")
    model_name = model or profile_model or os.getenv("LLM_VISION_MODEL_NAME", "qwen3-vl-flash")

    if provider_name is None:
        if api_key:
            provider_name = "openai"
        else:
            provider_name = "mock"

    # ── Egress gate: the single constraint ──────────────────────────────────
    if provider_name != "mock" and not egress_allows_llm(base_url, component="llm.factory.multimodal"):
        return _local_or_mock(audit_log=audit_log, model=model_name)

    if provider_name == "openai":
        from aegis_ai.llm.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(
            model=model_name,
            api_key=api_key,
            base_url=base_url if base_url else None,
            audit_log=audit_log,
        )

    from aegis_ai.llm.providers.mock import MockLLMProvider

    return MockLLMProvider()


def create_llm_provider_from_settings(settings_store: Any = None, audit_log: Any = None) -> Any:
    """Create LLM provider from settings store.

    When the gate does not permit the configured destination, the local provider is
    returned so AEGIS degrades rather than transmitting; if no local endpoint is
    listening that degrades once more to Mock (see `_local_or_mock`). The shipped
    `settings.json` permits exactly one destination (`api.typesafe.ai`), so every other
    configured profile falls back here.

    Args:
        settings_store: SettingsStore instance

    Returns:
        LLM provider instance
    """
    if settings_store:
        settings = settings_store.get()
        if settings.privacy.external_llm_allowed and egress_allows_llm(
            os.getenv("LLM_BASE_URL", ""), component="llm.factory.from_settings"
        ):
            return create_llm_provider(audit_log=audit_log)
        # Local only.
        return _local_or_mock(audit_log=audit_log)
    return create_llm_provider()
