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
    ) -> None:
        self._model = model
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self._base_url = base_url or os.getenv("OPENAI_BASE_URL", "")

        if not self._api_key:
            logger.warning("No API key set. Set OPENAI_API_KEY environment variable.")

        client_kwargs: dict[str, Any] = {"api_key": self._api_key}
        if self._base_url:
            client_kwargs["base_url"] = self._base_url

        self._client = OpenAI(**client_kwargs)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

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

            self._audit_log(
                action="llm_call",
                decision="success",
                detail={
                    "model": self._model,
                    "prompt_preview": prompt[:200],
                    "response_preview": content[:200],
                    "tokens": tokens,
                    "duration_ms": round(duration_ms, 1),
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
                    "prompt_preview": prompt[:200],
                    "error": str(e)[:200],
                    "duration_ms": round(duration_ms, 1),
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
            from aegis_ai.audit import AuditEntry, AuditLog
            log = AuditLog()
            log.append(AuditEntry(
                action=action,
                actor="llm",
                capability_id=f"llm.{self._model}",
                decision=decision,
                detail=detail,
            ))
        except Exception:
            pass
