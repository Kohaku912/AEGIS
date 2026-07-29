"""OpenAI-compatible LLM provider.

Works with OpenAI, DeepSeek, and any OpenAI-compatible API.
Set OPENAI_API_KEY and optionally OPENAI_BASE_URL.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from aegis_ai.llm.provider_circuit import PROVIDER_CIRCUITS

logger = logging.getLogger("aegis_ai.llm.providers.openai")

_AUDIT_PREVIEW_CHARS = int(os.getenv("AEGIS_LLM_AUDIT_PREVIEW_CHARS", "500"))
_MAX_PROMPT_CHARS = int(os.getenv("AEGIS_MAX_PROMPT_CHARS", "48000"))


@dataclass
class LLMResponse:
    """Response from the LLM."""
    content: str = ""
    model_used: str = ""
    provider_used: str = ""
    tokens_used: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    input_cache_hit_tokens: int = 0
    input_cache_miss_tokens: int = 0
    provider_reported_cost: float = 0.0
    cost_estimate: float = 0.0
    success: bool = True
    error: str = ""
    tool_calls: list[dict[str, Any]] | None = None


class OpenAIProvider:
    """OpenAI-compatible LLM provider.

    Works with:
    - OpenAI (default)
    - DeepSeek (set base_url to https://api.deepseek.com)
    - Any OpenAI-compatible API

    Usage:
        provider = OpenAIProvider(model="deepseek-v4-flash")
        response = provider.generate(prompt="Hello")
    """

    def __init__(
        self,
        model: str = "deepseek-v4-flash",
        api_key: str | None = None,
        base_url: str | None = None,
        audit_log: Any = None,
    ) -> None:
        self._model = model
        self._api_key = api_key or os.getenv("LLM_API_KEY", "")
        self._base_url = base_url or os.getenv("LLM_BASE_URL", "")
        self._audit = audit_log
        self._circuit = PROVIDER_CIRCUITS.get(self._base_url)

        if not self._api_key:
            logger.warning("No API key set. Set LLM_API_KEY environment variable.")

        client_kwargs: dict[str, Any] = {"api_key": self._api_key}
        if self._base_url:
            client_kwargs["base_url"] = self._base_url

        self._client = OpenAI(**client_kwargs)

    @staticmethod
    def _preview_text(text: str, limit: int = _AUDIT_PREVIEW_CHARS) -> str:
        value = str(text or "")
        if len(value) <= limit:
            return value
        return value[: max(0, limit - 3)] + "..."

    def _clamp_prompt(self, prompt: str) -> str:
        value = str(prompt or "")
        if len(value) <= _MAX_PROMPT_CHARS:
            return value
        logger.warning(
            "Truncating oversized LLM prompt: %d -> %d chars",
            len(value),
            _MAX_PROMPT_CHARS,
        )
        return value[: max(0, _MAX_PROMPT_CHARS - 3)] + "..."

    def _supports_vision(self) -> bool:
        """Return True when the configured backend is likely to accept image inputs."""
        model = self._model.lower()
        base_url = self._base_url.lower()
        if "deepseek" in base_url or model.startswith("deepseek"):
            return False
        return True

    @staticmethod
    def _usage_detail(response: Any) -> dict[str, Any]:
        usage = getattr(response, "usage", None)
        if usage is None:
            return {
                "tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "input_cache_hit_tokens": 0,
                "input_cache_miss_tokens": 0,
                "provider_reported_cost": 0.0,
            }

        def get_value(obj: Any, key: str, default: Any = 0) -> Any:
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        input_tokens = int(get_value(usage, "prompt_tokens", 0) or 0)
        output_tokens = int(get_value(usage, "completion_tokens", 0) or 0)
        total_tokens = int(get_value(usage, "total_tokens", input_tokens + output_tokens) or 0)
        prompt_details = get_value(usage, "prompt_tokens_details", {}) or {}
        cached_tokens = int(get_value(prompt_details, "cached_tokens", 0) or 0)
        miss_tokens = max(0, input_tokens - cached_tokens)
        reported_cost = float(get_value(usage, "cost", get_value(usage, "total_cost", 0.0)) or 0.0)
        return {
            "tokens": total_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cache_hit_tokens": cached_tokens,
            "input_cache_miss_tokens": miss_tokens,
            "provider_reported_cost": reported_cost,
            "prompt_tokens_details": prompt_details if isinstance(prompt_details, dict) else {},
        }

    def _circuit_blocked_response(self) -> LLMResponse | None:
        if self._circuit.allow_request():
            return None
        remaining = self._circuit.remaining_ms()
        status = self._circuit.status()
        return LLMResponse(
            success=False,
            error=(
                f"LLM provider circuit open "
                f"(balance/billing; {remaining // 1000}s remaining): "
                f"{status.get('last_error', '')}"
            ),
            model_used=self._model,
            provider_used="openai",
        )

    def _record_provider_outcome(self, error: Any | None = None) -> None:
        if error is None:
            self._circuit.record_success()
            return
        self._circuit.record_error(error)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        context_meta: dict[str, Any] | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        blocked = self._circuit_blocked_response()
        if blocked is not None:
            return blocked
        prompt = self._clamp_prompt(prompt)
        logger.info("LLM call: model=%s max_tokens=%d prompt_len=%d", self._model, max_tokens, len(prompt))
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start = time.time()
        try:
            request_kwargs: dict[str, Any] = {
                "model": self._model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if json_mode:
                request_kwargs["response_format"] = {"type": "json_object"}

            try:
                response = self._client.chat.completions.create(**request_kwargs)
            except Exception:
                if not json_mode:
                    raise
                logger.warning("LLM JSON mode was rejected; retrying without response_format", exc_info=True)
                request_kwargs.pop("response_format", None)
                response = self._client.chat.completions.create(**request_kwargs)

            content = response.choices[0].message.content or ""
            usage_detail = self._usage_detail(response)
            tokens = usage_detail["tokens"]
            duration_ms = (time.time() - start) * 1000

            logger.info(
                "LLM call success: model=%s tokens=%d duration=%.1fms",
                self._model, tokens, duration_ms,
            )

            self._record_provider_outcome()
            self._audit_log(
                action="llm_call",
                decision="success",
                detail={
                    "model": self._model,
                    "prompt_preview": self._preview_text(prompt),
                    "prompt_chars": len(prompt),
                    "response_preview": self._preview_text(content),
                    "tokens": tokens,
                    **usage_detail,
                    "duration_ms": round(duration_ms, 1),
                    "json_mode": json_mode,
                    **(context_meta or {}),
                },
            )

            return LLMResponse(
                content=content,
                model_used=self._model,
                provider_used="openai",
                tokens_used=tokens,
                input_tokens=usage_detail["input_tokens"],
                output_tokens=usage_detail["output_tokens"],
                input_cache_hit_tokens=usage_detail["input_cache_hit_tokens"],
                input_cache_miss_tokens=usage_detail["input_cache_miss_tokens"],
                provider_reported_cost=usage_detail["provider_reported_cost"],
                cost_estimate=tokens * 0.000002,
                success=True,
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            logger.error("OpenAI API call failed: %s", e)
            self._record_provider_outcome(e)
            self._audit_log(
                action="llm_call",
                decision="error",
                detail={
                    "model": self._model,
                    "prompt_preview": self._preview_text(prompt),
                    "prompt_chars": len(prompt),
                    "error": str(e),
                    "duration_ms": round(duration_ms, 1),
                    "circuit": self._circuit.status(),
                    **(context_meta or {}),
                },
            )
            return LLMResponse(
                success=False,
                error=str(e),
                model_used=self._model,
                provider_used="openai",
            )

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.3,
        context_meta: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Generate a response using OpenAI tool calling.

        Args:
            prompt: User prompt
            tools: OpenAI tool definitions (list of function schemas)
            system_prompt: Optional system prompt
            max_tokens: Max response tokens
            temperature: Sampling temperature

        Returns:
            LLMResponse with tool_calls populated if the model chose tools
        """
        blocked = self._circuit_blocked_response()
        if blocked is not None:
            return blocked
        prompt = self._clamp_prompt(prompt)
        logger.info("LLM tool call: model=%s tools=%d prompt_len=%d", self._model, len(tools), len(prompt))
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start = time.time()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=max_tokens,
                temperature=temperature,
            )

            choice = response.choices[0]
            content = choice.message.content or ""
            usage_detail = self._usage_detail(response)
            tokens = usage_detail["tokens"]
            duration_ms = (time.time() - start) * 1000

            tool_calls = None
            if choice.message.tool_calls:
                tool_calls = []
                for tc in choice.message.tool_calls:
                    import json as _json
                    try:
                        args = _json.loads(tc.function.arguments)
                    except Exception:
                        args = {}
                    tool_calls.append({
                        "id": tc.id,
                        "function": tc.function.name,
                        "arguments": args,
                    })

            logger.info(
                "LLM tool call success: model=%s tokens=%d duration=%.1fms tool_calls=%d",
                self._model, tokens, duration_ms, len(tool_calls) if tool_calls else 0,
            )

            self._record_provider_outcome()
            self._audit_log(
                action="llm_tool_call",
                decision="success",
                detail={
                    "model": self._model,
                    "prompt_preview": self._preview_text(prompt),
                    "prompt_chars": len(prompt),
                    "response_preview": self._preview_text(content),
                    "tool_calls": tool_calls,
                    "tool_count": len(tools),
                    "tokens": tokens,
                    **usage_detail,
                    "duration_ms": round(duration_ms, 1),
                    **(context_meta or {}),
                },
            )

            return LLMResponse(
                content=content,
                model_used=self._model,
                provider_used="openai",
                tokens_used=tokens,
                input_tokens=usage_detail["input_tokens"],
                output_tokens=usage_detail["output_tokens"],
                input_cache_hit_tokens=usage_detail["input_cache_hit_tokens"],
                input_cache_miss_tokens=usage_detail["input_cache_miss_tokens"],
                provider_reported_cost=usage_detail["provider_reported_cost"],
                cost_estimate=tokens * 0.000002,
                success=True,
                tool_calls=tool_calls,
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            logger.error("OpenAI tool call failed: %s", e)
            self._record_provider_outcome(e)
            self._audit_log(
                action="llm_tool_call",
                decision="error",
                detail={
                    "model": self._model,
                    "prompt_preview": self._preview_text(prompt),
                    "prompt_chars": len(prompt),
                    "error": str(e),
                    "duration_ms": round(duration_ms, 1),
                    "circuit": self._circuit.status(),
                    **(context_meta or {}),
                },
            )
            return LLMResponse(
                success=False,
                error=str(e),
                model_used=self._model,
                provider_used="openai",
            )

    def generate_with_image(
        self,
        prompt: str,
        image_base64: str,
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        detail: str = "low",
        context_meta: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Generate a response from the LLM with an image (multimodal).

        Args:
            prompt: Text prompt about the image
            image_base64: Base64-encoded image data (PNG/JPEG)
            system_prompt: Optional system prompt
            max_tokens: Max response tokens
            temperature: Sampling temperature
            detail: Image detail level ("low", "high", or "auto")

        Returns:
            LLMResponse with the model's description/analysis of the image
        """
        return self.generate_with_media(
            prompt=prompt,
            image_base64s=[image_base64],
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            detail=detail,
            context_meta=context_meta,
            media_kind="image",
        )

    def generate_with_media(
        self,
        prompt: str,
        image_base64s: list[str],
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        detail: str = "low",
        context_meta: dict[str, Any] | None = None,
        media_kind: str = "image",
    ) -> LLMResponse:
        """Generate a response from the LLM with one or more visual inputs."""
        blocked = self._circuit_blocked_response()
        if blocked is not None:
            return blocked
        logger.info(
            "LLM media call: model=%s max_tokens=%d detail=%s media_kind=%s count=%d",
            self._model,
            max_tokens,
            detail,
            media_kind,
            len([item for item in image_base64s if item]),
        )

        if not self._supports_vision():
            logger.warning(
                "Model does not support vision payloads: model=%s base_url=%s",
                self._model,
                self._base_url,
            )
            return LLMResponse(
                success=False,
                error=f"Model {self._model} does not support vision. Configure a vision-capable model in llm.yaml vision_observation profile.",
                model_used=self._model,
                provider_used="openai",
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        user_content = [{"type": "text", "text": prompt}]
        for image_base64 in image_base64s:
            if not image_base64:
                continue
            data_uri = image_base64
            if not data_uri.startswith("data:"):
                data_uri = f"data:image/png;base64,{image_base64}"
            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_uri,
                        "detail": detail,
                    },
                }
            )
        messages.append({"role": "user", "content": user_content})

        start = time.time()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            content = response.choices[0].message.content or ""
            usage_detail = self._usage_detail(response)
            tokens = usage_detail["tokens"]
            duration_ms = (time.time() - start) * 1000

            action = "llm_vision_call" if len([item for item in image_base64s if item]) <= 1 else "llm_media_call"
            self._record_provider_outcome()
            self._audit_log(
                action=action,
                decision="success",
                detail={
                    "model": self._model,
                    "prompt_preview": self._preview_text(prompt),
                    "prompt_chars": len(prompt),
                    "response_preview": self._preview_text(content),
                    "tokens": tokens,
                    **usage_detail,
                    "duration_ms": round(duration_ms, 1),
                    "media_kind": media_kind,
                    "media_count": len([item for item in image_base64s if item]),
                    **(context_meta or {}),
                },
            )

            return LLMResponse(
                content=content,
                model_used=self._model,
                provider_used="openai",
                tokens_used=tokens,
                input_tokens=usage_detail["input_tokens"],
                output_tokens=usage_detail["output_tokens"],
                input_cache_hit_tokens=usage_detail["input_cache_hit_tokens"],
                input_cache_miss_tokens=usage_detail["input_cache_miss_tokens"],
                provider_reported_cost=usage_detail["provider_reported_cost"],
                cost_estimate=tokens * 0.000002,
                success=True,
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            logger.error("OpenAI media API call failed: %s", e)
            self._record_provider_outcome(e)
            error_text = str(e).lower()
            if "image_url" in error_text or "invalid_request_error" in error_text or "messages[1]" in error_text:
                logger.error("Vision API error for model=%s: %s", self._model, e)
                duration_ms = int((time.monotonic() - start) * 1000)
                self._audit_log(
                    action="llm_media_call",
                    decision="vision_error",
                    detail={"model": self._model, "error": str(e), "duration_ms": round(duration_ms, 1)},
                )
                return LLMResponse(
                    success=False,
                    error=f"Vision API error: {e}. Configure a vision-capable model in llm.yaml vision_observation profile.",
                    model_used=self._model,
                    provider_used="openai",
                )
            self._audit_log(
                action="llm_media_call",
                decision="error",
                detail={
                    "model": self._model,
                    "prompt_preview": self._preview_text(prompt),
                    "prompt_chars": len(prompt),
                    "error": str(e),
                    "duration_ms": round(duration_ms, 1),
                    "media_kind": media_kind,
                    "media_count": len([item for item in image_base64s if item]),
                    "circuit": self._circuit.status(),
                    **(context_meta or {}),
                },
            )
            return LLMResponse(
                success=False,
                error=str(e),
                model_used=self._model,
                provider_used="openai",
            )

    def _audit_log(self, action: str, decision: str, detail: dict) -> None:
        try:
            if self._audit is not None:
                from aegis_ai.audit import AuditEntry
                self._audit.append(AuditEntry(
                    action=action,
                    actor="llm",
                    capability_id=f"llm.{self._model}",
                    decision=decision,
                    detail=detail,
                ))
        except Exception:
            pass
