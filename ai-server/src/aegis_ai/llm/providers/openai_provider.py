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

logger = logging.getLogger("aegis_ai.llm.providers.openai")


@dataclass
class LLMResponse:
    """Response from the LLM."""
    content: str = ""
    model_used: str = ""
    provider_used: str = ""
    tokens_used: int = 0
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

        if not self._api_key:
            logger.warning("No API key set. Set LLM_API_KEY environment variable.")

        client_kwargs: dict[str, Any] = {"api_key": self._api_key}
        if self._base_url:
            client_kwargs["base_url"] = self._base_url

        self._client = OpenAI(**client_kwargs)

    def _supports_vision(self) -> bool:
        """Return True when the configured backend is likely to accept image inputs."""
        model = self._model.lower()
        base_url = self._base_url.lower()
        if "deepseek" in base_url or model.startswith("deepseek"):
            return False
        return True

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
            tokens = response.usage.total_tokens if response.usage else 0
            duration_ms = (time.time() - start) * 1000

            logger.info(
                "LLM call success: model=%s tokens=%d duration=%.1fms",
                self._model, tokens, duration_ms,
            )

            self._audit_log(
                action="llm_call",
                decision="success",
                detail={
                    "model": self._model,
                    "prompt_preview": prompt,
                    "response_preview": content,
                    "tokens": tokens,
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
                cost_estimate=tokens * 0.000002,
                success=True,
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            logger.error("OpenAI API call failed: %s", e)
            self._audit_log(
                action="llm_call",
                decision="error",
                detail={
                    "model": self._model,
                    "prompt_preview": prompt,
                    "error": str(e),
                    "duration_ms": round(duration_ms, 1),
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
            tokens = response.usage.total_tokens if response.usage else 0
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

            self._audit_log(
                action="llm_tool_call",
                decision="success",
                detail={
                    "model": self._model,
                    "prompt_preview": prompt,
                    "response_preview": content,
                    "tool_calls": tool_calls,
                    "tokens": tokens,
                    "duration_ms": round(duration_ms, 1),
                    **(context_meta or {}),
                },
            )

            return LLMResponse(
                content=content,
                model_used=self._model,
                provider_used="openai",
                tokens_used=tokens,
                cost_estimate=tokens * 0.000002,
                success=True,
                tool_calls=tool_calls,
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            logger.error("OpenAI tool call failed: %s", e)
            self._audit_log(
                action="llm_tool_call",
                decision="error",
                detail={
                    "model": self._model,
                    "prompt_preview": prompt,
                    "error": str(e),
                    "duration_ms": round(duration_ms, 1),
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
                "Model/backend does not support vision payloads; falling back to text-only summary: model=%s",
                self._model,
            )
            fallback_prompt = (
                f"{prompt}\n\n"
                f"The {media_kind} itself could not be sent to this model. "
                "Summarize the likely state from the available task context and mention that vision was unavailable."
            )
            return self.generate(
                prompt=fallback_prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                context_meta={
                    **(context_meta or {}),
                    "vision_fallback": True,
                    "vision_supported": False,
                    "vision_detail": detail,
                    "media_kind": media_kind,
                    "media_count": len([item for item in image_base64s if item]),
                },
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
            tokens = response.usage.total_tokens if response.usage else 0
            duration_ms = (time.time() - start) * 1000

            action = "llm_vision_call" if len([item for item in image_base64s if item]) <= 1 else "llm_media_call"
            self._audit_log(
                action=action,
                decision="success",
                detail={
                    "model": self._model,
                    "prompt_preview": prompt,
                    "response_preview": content,
                    "tokens": tokens,
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
                cost_estimate=tokens * 0.000002,
                success=True,
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            logger.error("OpenAI media API call failed: %s", e)
            error_text = str(e).lower()
            if "image_url" in error_text or "invalid_request_error" in error_text or "messages[1]" in error_text:
                logger.warning("Retrying as text-only media fallback for model=%s", self._model)
                return self.generate(
                    prompt=(
                        f"{prompt}\n\n"
                        f"The provided {media_kind} input could not be attached to the model. "
                        "Provide the best possible actionable observation from the task context alone."
                    ),
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    context_meta={
                        **(context_meta or {}),
                        "vision_fallback": True,
                        "vision_supported": True,
                        "vision_detail": detail,
                        "vision_error": str(e),
                        "media_kind": media_kind,
                        "media_count": len([item for item in image_base64s if item]),
                    },
                )
            self._audit_log(
                action="llm_media_call",
                decision="error",
                detail={
                    "model": self._model,
                    "prompt_preview": prompt,
                    "error": str(e),
                    "duration_ms": round(duration_ms, 1),
                    "media_kind": media_kind,
                    "media_count": len([item for item in image_base64s if item]),
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
