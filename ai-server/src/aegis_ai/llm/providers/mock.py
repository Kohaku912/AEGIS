"""Mock LLM Provider — deterministic responses for testing.

Does NOT make real LLM calls. Returns predictable outputs.
"""

from __future__ import annotations

from typing import Any

from aegis_ai.llm.router import LLMResponse


class MockLLMProvider:
    """Mock LLM provider for testing and CI.

    Returns deterministic responses based on prompt keywords.
    """

    def __init__(self) -> None:
        self.call_log: list[dict[str, Any]] = []

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        context_meta: dict[str, Any] | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate a mock response."""
        self.call_log.append({
            "prompt": prompt[:100],
            "system_prompt": system_prompt[:100],
            "max_tokens": max_tokens,
            "json_mode": json_mode,
        })

        prompt_lower = prompt.lower()

        if "research" in prompt_lower or "summarize" in prompt_lower:
            content = "Based on the available information, here is a summary of the key findings."
        elif "plan" in prompt_lower:
            content = '{"goal": "Complete the task", "steps": [{"description": "Step 1"}]}'
        elif "reflect" in prompt_lower:
            content = "The operation completed successfully. Key learnings: check thresholds."
        elif "suggest" in prompt_lower:
            content = "I suggest checking the temperature settings."
        else:
            content = "Understood. Processing your request."

        return LLMResponse(
            content=content,
            model_used="mock-model",
            provider_used="mock",
            tokens_used=len(content.split()),
            cost_estimate=0.0,
            success=True,
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
        """Generate a mock response for image input."""
        self.call_log.append({
            "prompt": prompt[:100],
            "has_image": True,
            "system_prompt": system_prompt[:100],
        })
        content = "I can see the image. It shows a desktop environment with various application windows and system elements."
        return LLMResponse(
            content=content,
            model_used="mock-model",
            provider_used="mock",
            tokens_used=len(content.split()),
            cost_estimate=0.0,
            success=True,
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
        """Generate a mock response for image or video input."""
        self.call_log.append({
            "prompt": prompt[:100],
            "has_media": True,
            "media_kind": media_kind,
            "media_count": len([item for item in image_base64s if item]),
            "system_prompt": system_prompt[:100],
        })
        if media_kind == "video":
            content = "The video shows a changing screen or scene across the provided keyframes."
        else:
            content = "I can see the image. It shows a desktop environment with various application windows and system elements."
        return LLMResponse(
            content=content,
            model_used="mock-model",
            provider_used="mock",
            tokens_used=len(content.split()),
            cost_estimate=0.0,
            success=True,
        )
