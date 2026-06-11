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
    ) -> LLMResponse:
        """Generate a mock response."""
        self.call_log.append({
            "prompt": prompt[:100],
            "system_prompt": system_prompt[:100],
            "max_tokens": max_tokens,
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
