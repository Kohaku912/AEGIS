"""LLM Router — routes tasks to appropriate LLM models.

Routes based on:
- Task type (research, planning, code generation, etc.)
- Privacy requirements (local-only vs external allowed)
- Cost budget
- Model availability

Architecture reference: docs/architecture.md §5.3
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

logger = logging.getLogger("aegis_ai.llm.router")


class TaskType(Enum):
    """LLM task types for routing."""
    RESEARCH_SUMMARY = auto()
    PLANNING = auto()
    SUPPORT_SUGGESTION = auto()
    SELF_DEV_ANALYSIS = auto()
    CODE_GENERATION = auto()
    REFLECTION = auto()
    MEMORY_SUMMARIZATION = auto()
    CLASSIFICATION = auto()
    SMALL_FAST_TASK = auto()
    HIGH_REASONING_TASK = auto()


class PrivacyLevel(Enum):
    """Privacy level for LLM requests."""
    PUBLIC = auto()           # No sensitive data
    INTERNAL = auto()         # Internal AEGIS data, no secrets
    SENSITIVE = auto()        # May contain user data
    LOCAL_ONLY = auto()       # Must not leave local network


@dataclass
class LLMRequest:
    """A request to the LLM router."""
    task_type: TaskType
    prompt: str
    system_prompt: str = ""
    privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL
    max_tokens: int = 2000
    temperature: float = 0.7
    structured_output_schema: dict[str, Any] | None = None
    request_id: str = ""
    caller: str = ""  # Which agent is making the request
    context_meta: dict[str, Any] | None = None
    json_mode: bool = False


@dataclass
class LLMResponse:
    """Response from the LLM router."""
    content: str = ""
    model_used: str = ""
    provider_used: str = ""
    tokens_used: int = 0
    cost_estimate: float = 0.0
    request_id: str = ""
    success: bool = True
    error: str = ""
    tool_calls: list[dict[str, Any]] | None = None


class LLMRouter:
    """Routes LLM requests to appropriate providers and models.

    Usage:
        router = LLMRouter(settings_store=settings_store, cost_tracker=cost_tracker)
        router.register_provider("mock", MockLLMProvider())
        response = router.route(request)
    """

    def __init__(
        self,
        settings_store: Any = None,
        cost_tracker: Any = None,
        audit_log: Any = None,
    ) -> None:
        self._providers: dict[str, Any] = {}
        self._settings = settings_store
        self._cost_tracker = cost_tracker
        self._audit = audit_log
        self._default_provider = "mock"
        self._lock = threading.RLock()

    def register_provider(self, name: str, provider: Any) -> None:
        """Register an LLM provider."""
        with self._lock:
            self._providers[name] = provider
        logger.info("LLM provider '%s' registered", name)

    def set_default_provider(self, name: str) -> None:
        """Set the default provider."""
        with self._lock:
            self._default_provider = name

    def route(self, request: LLMRequest) -> LLMResponse:
        """Route an LLM request to the appropriate provider.

        Checks:
        1. Privacy level — local-only blocks external providers
        2. Cost budget — exceeded budget blocks/defers
        3. Task type — routes to configured model
        4. Provider availability — falls back to default
        """
        # Check privacy
        if request.privacy_level == PrivacyLevel.LOCAL_ONLY:
            # Only allow local/mock providers
            provider_name = self._find_local_provider()
            if not provider_name:
                return LLMResponse(
                    success=False,
                    error="No local LLM provider available for LOCAL_ONLY request",
                    request_id=request.request_id,
                )
        else:
            provider_name = self._select_provider(request.task_type)

        # Check cost budget
        if self._cost_tracker:
            if not self._cost_tracker.can_afford(request.max_tokens):
                return LLMResponse(
                    success=False,
                    error="LLM cost budget exceeded",
                    request_id=request.request_id,
                )

        # Get provider
        with self._lock:
            provider = self._providers.get(provider_name)
        if not provider:
            return LLMResponse(
                success=False,
                error=f"LLM provider '{provider_name}' not found",
                request_id=request.request_id,
            )

        # Execute
        try:
            response = provider.generate(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                context_meta=request.context_meta,
                json_mode=request.json_mode,
            )

            # Record cost
            if self._cost_tracker and response.tokens_used > 0:
                self._cost_tracker.record_usage(
                    provider=provider_name,
                    model=response.model_used,
                    tokens=response.tokens_used,
                    cost=response.cost_estimate,
                )

            # Audit
            if self._audit:
                self._audit.log_decision(
                    "llm_request", f"llm.{provider_name}", "EXECUTED",
                    detail={
                        "task_type": request.task_type.name,
                        "provider": provider_name,
                        "model": response.model_used,
                        "tokens": response.tokens_used,
                    },
                )

            return self._normalize_provider_response(response, provider_name, request.request_id)

        except Exception as e:
            logger.error("LLM request failed: %s", e)
            return LLMResponse(
                success=False,
                error=str(e),
                request_id=request.request_id,
            )

    def route_with_tools(
        self,
        request: LLMRequest,
        tools: list[dict[str, Any]],
    ) -> LLMResponse:
        """Route an LLM request that allows native tool calling."""
        provider_name = self._select_provider(request.task_type)
        if self._cost_tracker:
            if not self._cost_tracker.can_afford(request.max_tokens):
                return LLMResponse(
                    success=False,
                    error="LLM cost budget exceeded",
                    request_id=request.request_id,
                )

        with self._lock:
            provider = self._providers.get(provider_name)
        if not provider:
            return LLMResponse(
                success=False,
                error=f"LLM provider '{provider_name}' not found",
                request_id=request.request_id,
            )

        try:
            if hasattr(provider, "generate_with_tools"):
                response = provider.generate_with_tools(
                    prompt=request.prompt,
                    tools=tools,
                    system_prompt=request.system_prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    context_meta=request.context_meta,
                )
            else:
                response = provider.generate(
                    prompt=request.prompt,
                    system_prompt=request.system_prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    context_meta=request.context_meta,
                )

            if self._cost_tracker and response.tokens_used > 0:
                self._cost_tracker.record_usage(
                    provider=provider_name,
                    model=response.model_used,
                    tokens=response.tokens_used,
                    cost=response.cost_estimate,
                )

            if self._audit:
                self._audit.log_decision(
                    "llm_tool_request", f"llm.{provider_name}", "EXECUTED",
                    detail={
                        "task_type": request.task_type.name,
                        "provider": provider_name,
                        "model": response.model_used,
                        "tokens": response.tokens_used,
                        "caller": request.caller,
                        "route_type": "tools",
                    },
                )

            return self._normalize_provider_response(response, provider_name, request.request_id)
        except Exception as e:
            logger.error("LLM tool request failed: %s", e)
            return LLMResponse(success=False, error=str(e), request_id=request.request_id)

    def route_with_image(
        self,
        request: LLMRequest,
        image_base64: str,
        *,
        detail: str = "low",
    ) -> LLMResponse:
        """Route an LLM request with a single image input."""
        return self.route_with_media(request, [image_base64], detail=detail, media_kind="image")

    def route_with_media(
        self,
        request: LLMRequest,
        image_base64s: list[str],
        *,
        detail: str = "low",
        media_kind: str = "image",
    ) -> LLMResponse:
        """Route an LLM request with image or video frame inputs."""
        provider_name = self._select_provider(request.task_type)
        if self._cost_tracker:
            if not self._cost_tracker.can_afford(request.max_tokens):
                return LLMResponse(
                    success=False,
                    error="LLM cost budget exceeded",
                    request_id=request.request_id,
                )

        with self._lock:
            provider = self._providers.get(provider_name)
        if not provider:
            return LLMResponse(
                success=False,
                error=f"LLM provider '{provider_name}' not found",
                request_id=request.request_id,
            )

        try:
            if hasattr(provider, "generate_with_media"):
                response = provider.generate_with_media(
                    prompt=request.prompt,
                    image_base64s=image_base64s,
                    system_prompt=request.system_prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    detail=detail,
                    context_meta=request.context_meta,
                    media_kind=media_kind,
                )
            elif hasattr(provider, "generate_with_image") and image_base64s:
                response = provider.generate_with_image(
                    prompt=request.prompt,
                    image_base64=image_base64s[0],
                    system_prompt=request.system_prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    detail=detail,
                    context_meta=request.context_meta,
                )
            else:
                response = provider.generate(
                    prompt=request.prompt,
                    system_prompt=request.system_prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    context_meta=request.context_meta,
                )

            if self._cost_tracker and response.tokens_used > 0:
                self._cost_tracker.record_usage(
                    provider=provider_name,
                    model=response.model_used,
                    tokens=response.tokens_used,
                    cost=response.cost_estimate,
                )

            if self._audit:
                self._audit.log_decision(
                    "llm_tool_request", f"llm.{provider_name}", "EXECUTED",
                    detail={
                        "task_type": request.task_type.name,
                        "provider": provider_name,
                        "model": response.model_used,
                        "tokens": response.tokens_used,
                        "caller": request.caller,
                        "route_type": "media",
                    },
                )

            return self._normalize_provider_response(response, provider_name, request.request_id)
        except Exception as e:
            logger.error("LLM media request failed: %s", e)
            return LLMResponse(success=False, error=str(e), request_id=request.request_id)

    def _select_provider(self, task_type: TaskType) -> str:
        """Select provider based on task type and settings."""
        # Check settings for external LLM permission
        if self._settings:
            settings = self._settings.get()
            if not settings.privacy.external_llm_allowed:
                return self._find_local_provider() or self._default_provider

        return self._default_provider

    def _find_local_provider(self) -> str:
        """Find a local/mock provider."""
        with self._lock:
            names = list(self._providers)
        for name in names:
            if name == "ollama":
                return name
        for name in names:
            if name == "local":
                return name
        for name in names:
            if name == "mock":
                return name
        return ""

    @staticmethod
    def _normalize_provider_response(response: Any, provider_name: str, request_id: str) -> LLMResponse:
        if isinstance(response, LLMResponse):
            return response
        return LLMResponse(
            content=getattr(response, "content", ""),
            model_used=getattr(response, "model_used", ""),
            provider_used=getattr(response, "provider_used", provider_name),
            tokens_used=getattr(response, "tokens_used", 0),
            cost_estimate=getattr(response, "cost_estimate", 0.0),
            request_id=getattr(response, "request_id", request_id),
            success=getattr(response, "success", True),
            error=getattr(response, "error", ""),
            tool_calls=getattr(response, "tool_calls", None),
        )
