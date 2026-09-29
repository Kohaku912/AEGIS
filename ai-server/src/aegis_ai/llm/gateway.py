"""LLM Gateway — unified entry point for all LLM calls.

Routes through LLMRouter with profile-based settings from LLMSettingsResolver,
prompt templates from PromptRegistry, and audit logging.

Extracted from runtime.py to enable config-driven LLM management.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from aegis_ai.llm.layer_profiles import (
    LLMLayer,
    is_valid_layer,
    layer_description,
    layer_to_profile,
)
from aegis_ai.llm.prompt_registry import PromptRegistry
from aegis_ai.llm.router import (
    LLMRequest,
    LLMResponse,
    LLMRouter,
    PrivacyLevel,
    TaskType,
    accepts_kwarg,
)
from aegis_ai.llm.settings_resolver import LLMSettings, LLMSettingsResolver

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
        """Resolve LLM settings from profile."""
        if self._settings_resolver is not None:
            if profile:
                return self._settings_resolver.resolve(profile_id=profile)
            return self._settings_resolver.resolve()
        return LLMSettings()

    def _profile_resolution_failure(
        self,
        *,
        profile: str | None,
        error: Exception,
        context_meta: dict[str, Any] | None = None,
    ) -> LLMResponse:
        message = str(error)
        logger.error("Failed to resolve LLM profile '%s': %s", profile or "default", message)
        if self._audit is not None:
            try:
                from aegis_ai.audit import AuditEntry

                self._audit.append(
                    AuditEntry(
                        action="llm_profile_resolution",
                        actor="gateway",
                        capability_id="llm.profile_resolution",
                        decision="FAILED",
                        reason=f"profile={profile or 'default'}",
                        detail={
                            "error": message,
                            **dict(context_meta or {}),
                        },
                        profile_id=profile or "",
                        request_id=str((context_meta or {}).get("request_id", "")),
                        task_id=str(
                            (context_meta or {}).get("task_id")
                            or (context_meta or {}).get("chat_task_id")
                            or ""
                        ),
                    )
                )
            except Exception:
                logger.debug("Failed to audit LLM profile resolution failure", exc_info=True)
        return LLMResponse(
            success=False,
            error=message,
            provider_used="gateway",
        )

    def _get_provider_for_profile(self, settings: LLMSettings) -> Any | None:
        """Get or create a provider for a profile based on api_key_env and base_url."""
        import os
        try:
            from pathlib import Path

            from dotenv import load_dotenv
            for env_path in (
                Path(__file__).resolve().parents[4] / ".env",
                Path(__file__).resolve().parents[3] / ".env",
            ):
                if env_path.exists():
                    load_dotenv(env_path, override=False)
        except ImportError:
            pass
        if not settings.api_key_env and not settings.base_url:
            return None
        cache_key = (
            f"{settings.provider}:{settings.api_key_env}:{settings.base_url}:"
            f"{settings.model}"
        )
        if cache_key in self._profile_providers:
            return self._profile_providers[cache_key]
        api_key = os.getenv(settings.api_key_env, "") if settings.api_key_env else ""
        base_url = settings.base_url or ""
        if not api_key and not base_url:
            return None

        # ── Egress gate (the single constraint) ────────────────────────────────
        # This gateway is the main L1/L2/L3 LLM path and constructs providers
        # directly, so it must consult the gate itself. Without this, a profile
        # pointing at a cloud host would transmit regardless of the gate.
        from aegis_ai.llm.factory import _DEFAULT_CLOUD_BASE_URL, _is_reachable, _local_or_mock, egress_allows_llm

        if not egress_allows_llm(base_url or _DEFAULT_CLOUD_BASE_URL, component="llm.gateway"):
            # Never transmit. Degrade to the local model, else Mock.
            provider = _local_or_mock(audit_log=self._audit)
            self._profile_providers[cache_key] = provider
            logger.warning(
                "Egress gate denied profile destination %s — degraded to %s",
                base_url or _DEFAULT_CLOUD_BASE_URL,
                type(provider).__name__,
            )
            return provider

        is_local_ollama = "localhost:11434" in base_url or "127.0.0.1:11434" in base_url
        if is_local_ollama and not _is_reachable(base_url):
            # Permitted destination, but nothing is listening. Degrade deterministically
            # instead of stalling on SDK retries against a dead endpoint.
            provider = _local_or_mock(audit_log=self._audit, base_url=base_url)
            self._profile_providers[cache_key] = provider
            logger.warning("Local LLM at %s is not reachable — degraded to %s", base_url, type(provider).__name__)
            return provider

        if not api_key and is_local_ollama:
            api_key = "ollama"
        if settings.provider == "typesafe":
            from aegis_ai.llm.providers.typesafe_provider import TypeSafeProvider

            provider = TypeSafeProvider(
                model=settings.model,
                api_key=api_key,
                base_url=base_url or None,
                audit_log=self._audit,
                timeout_seconds=settings.timeout_seconds,
            )
        else:
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

    def _enrich_context_meta(
        self,
        context_meta: dict[str, Any] | None,
        *,
        profile: str,
        settings: LLMSettings,
    ) -> dict[str, Any]:
        """Attach stable observability fields before routing to a provider."""
        meta = dict(context_meta or {})
        meta.setdefault("profile_id", profile)
        meta.setdefault("profile", profile)
        meta.setdefault("provider", settings.provider)
        meta.setdefault("model", settings.model)
        return meta

    def _audit_call(
        self,
        *,
        profile: str,
        prompt_id: str | None,
        settings: LLMSettings,
        response: LLMResponse,
        duration_ms: int,
        context_meta: dict[str, Any] | None = None,
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

            meta_detail = dict(context_meta or {})
            meta_detail.update({
                "success": response.success,
                "input_tokens": getattr(response, "input_tokens", 0),
                "output_tokens": getattr(response, "output_tokens", 0),
                "input_cache_hit_tokens": getattr(response, "input_cache_hit_tokens", 0),
                "input_cache_miss_tokens": getattr(response, "input_cache_miss_tokens", 0),
                "provider_reported_cost": getattr(response, "provider_reported_cost", 0.0),
            })

            self._audit.append(AuditEntry(
                action="llm_call",
                actor="gateway",
                capability_id=f"llm.{settings.provider}",
                decision="EXECUTED",
                reason=f"profile={profile}",
                detail=meta_detail,
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
                request_id=str((context_meta or {}).get("request_id", "")),
                task_id=str((context_meta or {}).get("task_id") or (context_meta or {}).get("chat_task_id") or ""),
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
            reasoning_level=settings.reasoning_level,
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
        try:
            settings = self._resolve(profile)
        except (KeyError, ValueError) as exc:
            return self._profile_resolution_failure(
                profile=profile,
                error=exc,
                context_meta=context_meta,
            )
        resolved_profile = profile or "default"
        if max_tokens is not None:
            settings.max_tokens = max_tokens
        if temperature is not None:
            settings.temperature = temperature

        provider = self._get_provider_for_profile(settings)
        provider_meta = self._enrich_context_meta(
            context_meta,
            profile=resolved_profile,
            settings=settings,
        )

        from aegis_ai.observability.otel_tracing import start_span
        span_attrs = {
            "llm.profile": str(resolved_profile),
            "llm.model": str(settings.model),
        }
        if provider_meta:
            span_attrs["request_id"] = str(provider_meta.get("request_id") or "")
            if provider_meta.get("task_id"):
                span_attrs["task_id"] = str(provider_meta.get("task_id") or "")

        start = time.monotonic()
        with start_span("aegis.llm.generate", **span_attrs):
            if provider is not None and hasattr(provider, "generate"):
                response = provider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=settings.max_tokens,
                    temperature=settings.temperature,
                    context_meta=provider_meta,
                    json_mode=json_mode,
                )
            else:
                request = self._make_request(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    settings=settings,
                    context_meta=provider_meta,
                    json_mode=json_mode,
                )
                response = self._router.route(request)
        duration_ms = int((time.monotonic() - start) * 1000)
        self._audit_call(
            profile=resolved_profile,
            prompt_id=None,
            settings=settings,
            response=response,
            duration_ms=duration_ms,
            context_meta=provider_meta,
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
        try:
            settings = self._resolve(profile)
        except (KeyError, ValueError) as exc:
            return self._profile_resolution_failure(
                profile=profile,
                error=exc,
                context_meta=context_meta,
            )
        resolved_profile = profile or "default"
        if max_tokens is not None:
            settings.max_tokens = max_tokens
        if temperature is not None:
            settings.temperature = temperature

        provider_meta = self._enrich_context_meta(
            context_meta,
            profile=resolved_profile,
            settings=settings,
        )
        provider = self._get_provider_for_profile(settings)

        span_attrs = {
            "llm.profile": str(resolved_profile),
            "llm.model": str(settings.model),
        }
        if provider_meta:
            span_attrs["request_id"] = str(provider_meta.get("request_id") or "")
            if provider_meta.get("task_id"):
                span_attrs["task_id"] = str(provider_meta.get("task_id") or "")

        from aegis_ai.observability.otel_tracing import start_span

        start = time.monotonic()
        with start_span("aegis.llm.generate_with_tools", **span_attrs):
            if provider is not None and hasattr(provider, "generate_with_tools"):
                call_kwargs: dict[str, Any] = {
                    "prompt": prompt,
                    "tools": tools,
                    "system_prompt": system_prompt,
                    "context_meta": provider_meta,
                    "max_tokens": settings.max_tokens,
                    "temperature": settings.temperature,
                }
                if accepts_kwarg(provider.generate_with_tools, "reasoning_level"):
                    call_kwargs["reasoning_level"] = settings.reasoning_level
                response = provider.generate_with_tools(**call_kwargs)
            else:
                request = self._make_request(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    settings=settings,
                    context_meta=provider_meta,
                )
                response = self._router.route_with_tools(request, tools)
        duration_ms = int((time.monotonic() - start) * 1000)

        self._audit_call(
            profile=resolved_profile,
            prompt_id=None,
            settings=settings,
            response=response,
            duration_ms=duration_ms,
            context_meta=provider_meta,
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
        try:
            settings = self._resolve(profile)
        except (KeyError, ValueError) as exc:
            return self._profile_resolution_failure(
                profile=profile,
                error=exc,
                context_meta=context_meta,
            )
        resolved_profile = profile or "default"
        if max_tokens is not None:
            settings.max_tokens = max_tokens
        if temperature is not None:
            settings.temperature = temperature

        provider = self._get_provider_for_profile(settings)
        provider_meta = self._enrich_context_meta(
            context_meta,
            profile=resolved_profile,
            settings=settings,
        )

        start = time.monotonic()
        if provider is not None and hasattr(provider, "generate_with_image"):
            response = provider.generate_with_image(
                prompt=prompt,
                image_base64=image_base64,
                system_prompt=system_prompt,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                detail=detail,
                context_meta=provider_meta,
            )
        else:
            request = self._make_request(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings,
                context_meta=provider_meta,
            )
            response = self._router.route_with_image(request, image_base64, detail=detail)
        duration_ms = int((time.monotonic() - start) * 1000)

        self._audit_call(
            profile=resolved_profile,
            prompt_id=None,
            settings=settings,
            response=response,
            duration_ms=duration_ms,
            context_meta=provider_meta,
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
        try:
            settings = self._resolve(profile)
        except (KeyError, ValueError) as exc:
            return self._profile_resolution_failure(
                profile=profile,
                error=exc,
                context_meta=context_meta,
            )
        resolved_profile = profile or "default"
        if max_tokens is not None:
            settings.max_tokens = max_tokens
        if temperature is not None:
            settings.temperature = temperature

        provider_meta = self._enrich_context_meta(
            context_meta,
            profile=resolved_profile,
            settings=settings,
        )
        request = self._make_request(
            prompt=prompt,
            system_prompt=system_prompt,
            settings=settings,
            context_meta=provider_meta,
        )

        start = time.monotonic()
        response = self._router.route_with_media(
            request, image_base64s, detail=detail, media_kind=media_kind,
        )
        duration_ms = int((time.monotonic() - start) * 1000)

        self._audit_call(
            profile=resolved_profile,
            prompt_id=None,
            settings=settings,
            response=response,
            duration_ms=duration_ms,
            context_meta=provider_meta,
        )
        return response

    # ── L1/L2/L3 Layer API (DASHBOARD_V3_PLAN.md Phase L1) ───

    def request(
        self,
        layer: str,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int | None = None,
        temperature: float | None = None,
        tools: list[dict[str, Any]] | None = None,
        json_mode: bool = False,
        context_meta: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Layer ベースで LLM を呼び出す (instruction.md v3 L1/L2/L3).

        Args:
            layer: "L1" | "L2" | "L3"
            prompt: 入力プロンプト
            system_prompt: システムプロンプト
            max_tokens: 出力最大トークン (profile の値を上書き)
            temperature: temperature (profile の値を上書き)
            tools: tool definitions (L1/L2 で利用、L3 では未使用想定)
            json_mode: JSON 出力モード (L1 で構造化出力を行うときに利用)
            context_meta: 追加 metadata (task_id, request_id など)

        Returns:
            LLMResponse

        Raises:
            ValueError: layer が "L1" / "L2" / "L3" 以外
        """
        if not is_valid_layer(layer):
            raise ValueError(
                f"Invalid LLM layer '{layer}'. Expected one of: L1, L2, L3"
            )

        profile_id = layer_to_profile(layer)
        meta = dict(context_meta or {})
        # layer 情報を context_meta に自動付与 (Audit / Trace で利用)
        meta.setdefault("layer", layer)
        meta.setdefault("caller", f"gateway.{layer}")
        meta.setdefault("llm_layer_description", layer_description(layer))

        logger.debug(
            "LLMGateway.request layer=%s profile=%s has_tools=%s json_mode=%s",
            layer, profile_id, bool(tools), json_mode,
        )

        if tools:
            return self.generate_with_tools(
                prompt=prompt,
                tools=tools,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                context_meta=meta,
                profile=profile_id,
            )
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            context_meta=meta,
            json_mode=json_mode,
            profile=profile_id,
        )

    def request_json(
        self,
        layer: str,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int | None = None,
        temperature: float | None = None,
        context_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Layer ベースで LLM を呼び出し、JSON として parse する convenience.

        L1 の構造化出力 (L1Observation / L1Decision / L1Escalation 等) で利用。
        """
        response = self.request(
            layer=layer,
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=None,
            json_mode=True,
            context_meta=context_meta,
        )
        import json
        if response.success and response.content:
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                logger.warning(
                    "LLMGateway.request_json layer=%s failed to parse JSON", layer
                )
                return {"error": "json_parse_failed", "raw": response.content}
        return {"error": response.error or "generation_failed"}


__all__ = ["LLMGateway", "LLMLayer"]
