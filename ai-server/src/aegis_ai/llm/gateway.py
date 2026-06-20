"""LLM Gateway — unified entry point for all LLM calls.

Routes through LLMRouter with profile-based settings from LLMSettingsResolver,
prompt templates from PromptRegistry, and audit logging.

Extracted from runtime.py to enable config-driven LLM management.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from aegis_ai.llm.router import LLMRequest, LLMResponse, LLMRouter, PrivacyLevel, TaskType
from aegis_ai.llm.settings_resolver import LLMSettingsResolver, LLMSettings
from aegis_ai.llm.prompt_registry import PromptRegistry

logger = logging.getLogger("aegis_ai.llm.gateway")


class LLMGateway:
    """Unified LLM entry point with profile-based config and audit logging.

    Usage:
        gateway = LLMGateway(router, settings_resolver, prompt_registry, audit_log)
        response = gateway.generate("chat_balanced", "Hello!")
        response = gateway.generate_with_tools("tool_planning", "Do X", tools=[...])
    """

    def __init__(
        self,
        router: LLMRouter,
        settings_resolver: LLMSettingsResolver | None = None,
        prompt_registry: PromptRegistry | None = None,
        audit_log: Any = None,
    ) -> None:
        self._router = router
        self._settings_resolver = settings_resolver
        self._prompt_registry = prompt_registry
        self._audit = audit_log
        self._profile_providers: dict[str, Any] = {}

    def _resolve(self, profile: str | None) -> LLMSettings:
        """Resolve LLM settings from profile. Falls back to llm.yaml default."""
        if self._settings_resolver is not None:
            if profile:
                try:
                    return self._settings_resolver.resolve(profile_id=profile)
                except KeyError:
                    logger.warning("Profile '%s' not found, using default", profile)
            return self._settings_resolver.resolve()
        return LLMSettings()

    def _get_provider_for_profile(self, settings: LLMSettings) -> Any | None:
        """Get or create a provider for a profile based on api_key_env and base_url."""
        import os
        try:
            from dotenv import load_dotenv
            from pathlib import Path
            env_path = Path(__file__).resolve().parents[4] / ".env"
            if env_path.exists():
                load_dotenv(env_path, override=False)
        except ImportError:
            pass
        if not settings.api_key_env and not settings.base_url:
            return None
        cache_key = f"{settings.api_key_env}:{settings.base_url}:{settings.provider}"
        if cache_key in self._profile_providers:
            return self._profile_providers[cache_key]
        api_key = os.getenv(settings.api_key_env, "") if settings.api_key_env else ""
        base_url = settings.base_url or ""
        if not api_key and not base_url:
            return None
        if not api_key and base_url and ("localhost:11434" in base_url or "127.0.0.1:11434" in base_url):
            api_key = "ollama"
        from aegis_ai.llm.providers.openai_provider import OpenAIProvider
        provider = OpenAIProvider(
            model=settings.model,
            api_key=api_key or "dummy",
            base_url=base_url or None,
            audit_log=self._audit,
        )
        self._profile_providers[cache_key] = provider
        logger.info("Created provider for profile: env=%s base_url=%s model=%s",
                     settings.api_key_env, base_url, settings.model)
        return provider

    def _get_system_prompt(self, prompt_id: str | None, default: str = "") -> str:
        """Get system prompt from registry or use default."""
        if prompt_id and self._prompt_registry:
            try:
                return self._prompt_registry.render(prompt_id)
            except KeyError:
                logger.warning("Prompt '%s' not found, using default", prompt_id)
        return default

    def _audit_call(
        self,
        *,
        profile: str,
        prompt_id: str | None,
        settings: LLMSettings,
        response: LLMResponse,
        duration_ms: int,
    ) -> None:
        """Log LLM call to audit log."""
        if self._audit is None:
            return
        try:
            from aegis_ai.audit import AuditEntry

            metadata = {}
            if prompt_id and self._prompt_registry:
                try:
                    metadata = self._prompt_registry.get_metadata(prompt_id)
                except KeyError:
                    pass

            self._audit.append(AuditEntry(
                action="llm_call",
                actor="gateway",
                capability_id=f"llm.{settings.provider}",
                decision="EXECUTED",
                reason=f"profile={profile}",
                detail={"success": response.success},
                profile_id=profile,
                prompt_id=prompt_id or "",
                prompt_version=metadata.get("version", ""),
                prompt_hash=metadata.get("hash", ""),
                model=settings.model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                reasoning_level=settings.reasoning_level,
                provider=settings.provider,
                tokens_used=response.tokens_used,
                duration_ms=duration_ms,
            ))
        except Exception:
            logger.debug("Failed to write LLM audit entry", exc_info=True)

    def _make_request(
        self,
        *,
        prompt: str,
        system_prompt: str,
        settings: LLMSettings,
        context_meta: dict[str, Any] | None = None,
        json_mode: bool = False,
    ) -> LLMRequest:
        """Build an LLMRequest from settings."""
        meta = context_meta or {}
        return LLMRequest(
            task_type=TaskType.HIGH_REASONING_TASK if json_mode else TaskType.SMALL_FAST_TASK,
            prompt=prompt,
            system_prompt=system_prompt,
            privacy_level=PrivacyLevel.INTERNAL,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            caller=str(meta.get("caller", "gateway")),
            request_id=str(meta.get("request_id", "")),
            context_meta=context_meta,
            json_mode=json_mode,
        )

    # ── Public API ────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int | None = None,
        temperature: float | None = None,
        context_meta: dict[str, Any] | None = None,
        json_mode: bool = False,
        profile: str | None = None,
    ) -> LLMResponse:
        """Generate a response. Profile overrides max_tokens/temperature defaults."""
        settings = self._resolve(profile)
        if max_tokens is not None:
            settings.max_tokens = max_tokens
        if temperature is not None:
            settings.temperature = temperature

        provider = self._get_provider_for_profile(settings)

        start = time.monotonic()
        if provider is not None:
            response = provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
            )
        else:
            request = self._make_request(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings,
                context_meta=context_meta,
                json_mode=json_mode,
            )
            response = self._router.route(request)
        duration_ms = int((time.monotonic() - start) * 1000)

        self._audit_call(
            profile=profile or "default",
            prompt_id=None,
            settings=settings,
            response=response,
            duration_ms=duration_ms,
        )
        return response

    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int | None = None,
        temperature: float | None = None,
        context_meta: dict[str, Any] | None = None,
        profile: str | None = None,
    ) -> dict[str, Any]:
        """Generate a JSON response. Returns parsed dict."""
        response = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            context_meta=context_meta,
            json_mode=True,
            profile=profile,
        )
        import json
        if response.success and response.content:
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response")
                return {"error": "json_parse_failed", "raw": response.content}
        return {"error": response.error or "generation_failed"}

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_prompt: str = "",
        max_tokens: int | None = None,
        temperature: float | None = None,
        context_meta: dict[str, Any] | None = None,
        profile: str | None = None,
    ) -> LLMResponse:
        """Generate with tool calling support."""
        settings = self._resolve(profile)
        if max_tokens is not None:
            settings.max_tokens = max_tokens
        if temperature is not None:
            settings.temperature = temperature

        start = time.monotonic()
        provider = self._get_provider_for_profile(settings)

        if provider is not None and hasattr(provider, "generate_with_tools"):
            response = provider.generate_with_tools(
                prompt=prompt,
                tools=tools,
                system_prompt=system_prompt,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                context_meta=context_meta,
            )
        else:
            request = self._make_request(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings,
                context_meta=context_meta,
            )
            response = self._router.route_with_tools(request, tools)
        duration_ms = int((time.monotonic() - start) * 1000)

        self._audit_call(
            profile=profile or "default",
            prompt_id=None,
            settings=settings,
            response=response,
            duration_ms=duration_ms,
        )
        return response

    def generate_with_image(
        self,
        prompt: str,
        image_base64: str,
        system_prompt: str = "",
        max_tokens: int | None = None,
        temperature: float | None = None,
        detail: str = "low",
        context_meta: dict[str, Any] | None = None,
        profile: str | None = None,
    ) -> LLMResponse:
        """Generate with image input (vision)."""
        settings = self._resolve(profile)
        if max_tokens is not None:
            settings.max_tokens = max_tokens
        if temperature is not None:
            settings.temperature = temperature

        provider = self._get_provider_for_profile(settings)

        start = time.monotonic()
        if provider is not None and hasattr(provider, "generate_with_image"):
            response = provider.generate_with_image(
                prompt=prompt,
                image_base64=image_base64,
                system_prompt=system_prompt,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                detail=detail,
                context_meta=context_meta,
            )
        else:
            request = self._make_request(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings,
                context_meta=context_meta,
            )
            response = self._router.route_with_image(request, image_base64, detail=detail)
        duration_ms = int((time.monotonic() - start) * 1000)

        self._audit_call(
            profile=profile or "default",
            prompt_id=None,
            settings=settings,
            response=response,
            duration_ms=duration_ms,
        )
        return response

    def generate_with_media(
        self,
        prompt: str,
        image_base64s: list[str],
        system_prompt: str = "",
        max_tokens: int | None = None,
        temperature: float | None = None,
        detail: str = "low",
        context_meta: dict[str, Any] | None = None,
        media_kind: str = "image",
        profile: str | None = None,
    ) -> LLMResponse:
        """Generate with multiple media inputs."""
        settings = self._resolve(profile)
        if max_tokens is not None:
            settings.max_tokens = max_tokens
        if temperature is not None:
            settings.temperature = temperature

        request = self._make_request(
            prompt=prompt,
            system_prompt=system_prompt,
            settings=settings,
            context_meta=context_meta,
        )

        start = time.monotonic()
        response = self._router.route_with_media(
            request, image_base64s, detail=detail, media_kind=media_kind,
        )
        duration_ms = int((time.monotonic() - start) * 1000)

        self._audit_call(
            profile=profile or "default",
            prompt_id=None,
            settings=settings,
            response=response,
            duration_ms=duration_ms,
        )
        return response


__all__ = ["LLMGateway"]
