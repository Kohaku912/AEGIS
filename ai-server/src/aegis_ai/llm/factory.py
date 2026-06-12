"""LLM Provider Factory — creates LLM providers based on configuration.

Automatically selects the right provider based on environment variables:
- OPENAI_API_KEY + OPENAI_BASE_URL → DeepSeek/OpenAI provider
- No key → Mock provider

Usage:
    provider = create_llm_provider()
    response = provider.generate(prompt="Hello")
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("aegis_ai.llm.factory")


def create_llm_provider(
    provider_name: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> Any:
    """Create an LLM provider based on configuration.

    Args:
        provider_name: "openai", "deepseek", "mock", or None (auto-detect)
        model: Model name (e.g., "deepseek-chat", "gpt-4o-mini")
        api_key: API key (or reads from OPENAI_API_KEY env)
        base_url: Base URL (or reads from OPENAI_BASE_URL env)

    Returns:
        LLM provider instance
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY", "")
    base_url = base_url or os.getenv("OPENAI_BASE_URL", "")

    # Auto-detect provider
    if provider_name is None:
        if api_key:
            if "deepseek" in (base_url or "").lower():
                provider_name = "deepseek"
            else:
                provider_name = "openai"
        else:
            provider_name = "mock"

    # Create provider
    if provider_name in ("openai", "deepseek"):
        from aegis_ai.llm.providers.openai_provider import OpenAIProvider

        default_model = "deepseek-chat" if provider_name == "deepseek" else "gpt-4o-mini"
        return OpenAIProvider(
            model=model or default_model,
            api_key=api_key,
            base_url=base_url if base_url else None,
        )
    else:
        from aegis_ai.llm.providers.mock import MockLLMProvider

        return MockLLMProvider()


def create_llm_provider_from_settings(settings_store: Any = None) -> Any:
    """Create LLM provider from settings store.

    Args:
        settings_store: SettingsStore instance

    Returns:
        LLM provider instance
    """
    if settings_store:
        settings = settings_store.get()
        if settings.privacy.external_llm_allowed:
            return create_llm_provider()
        else:
            # Local only - use mock
            from aegis_ai.llm.providers.mock import MockLLMProvider
            return MockLLMProvider()
    return create_llm_provider()
