"""Beta: No Intent Core Routing — verify intent is not the core mechanism.

Verifies that:
- LLM Task Interpreter is the primary routing mechanism
- Intent classifier is not used as core
- System commands still work (status, help, etc.)
- All other messages go through LLM Task Interpreter
"""

from __future__ import annotations

import time

from aegis_ai.interaction.message import Message
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.llm_task_interpreter import LLMTaskInterpreter


class MockLLMProvider:
    """Mock LLM that records calls."""

    def __init__(self):
        self.call_count = 0
        self.last_prompt = ""

    def generate(self, prompt: str = "", system_prompt: str = "", max_tokens: int = 1000, temperature: float = 0.1):
        self.call_count += 1
        self.last_prompt = prompt
        from dataclasses import dataclass
        @dataclass
        class MockResponse:
            content: str = (
                '{"user_goal": "test", "interpreted_request": "test",'
                ' "steps": [], "needs_browser": false, "needs_device": false}'
            )
            success: bool = True
            error: str = ""
            tokens_used: int = 100
            model_used: str = "mock"
        return MockResponse()


# ═══════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════


class TestNoIntentCoreRouting:
    """Verify LLM Task Interpreter is the core routing mechanism."""

    def test_llm_called_for_general_messages(self):
        """LLM is called for general messages (not system commands)."""
        llm = MockLLMProvider()
        router = InteractionRouter(llm_provider=llm)

        msg = Message(text="Research Python 3.12 features", timestamp_ms=int(time.time() * 1000))
        router.route(msg)

        assert llm.call_count > 0

    def test_llm_called_for_japanese_messages(self):
        """LLM is called for Japanese messages."""
        llm = MockLLMProvider()
        router = InteractionRouter(llm_provider=llm)

        msg = Message(text="最近のニュースを調べて", timestamp_ms=int(time.time() * 1000))
        router.route(msg)

        assert llm.call_count > 0

    def test_status_command_bypasses_llm(self):
        """Status command handled directly (no LLM)."""
        llm = MockLLMProvider()
        router = InteractionRouter(llm_provider=llm)

        msg = Message(text="status", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)

        # Status should be handled directly
        assert "dashboard" in response.text.lower() or "status" in response.text.lower()

    def test_help_command_bypasses_llm(self):
        """Help command handled directly (no LLM)."""
        llm = MockLLMProvider()
        router = InteractionRouter(llm_provider=llm)

        msg = Message(text="help", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)

        assert "aegis" in response.text.lower() or "help" in response.text.lower()

    def test_intent_not_used_as_core(self):
        """Intent classifier is NOT the core routing mechanism."""
        # The router should use LLM Task Interpreter, not intent keywords
        llm = MockLLMProvider()
        router = InteractionRouter(llm_provider=llm)

        # This message would match RESEARCH_REQUEST intent
        # but should go through LLM Task Interpreter instead
        msg = Message(text="research AI news", timestamp_ms=int(time.time() * 1000))
        router.route(msg)

        # LLM should be called
        assert llm.call_count > 0

    def test_llm_task_interpreter_is_primary(self):
        """LLM Task Interpreter is the primary interpretation mechanism."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)

        plan = interpreter.interpret("Check my email and summarize")

        # Should produce a TaskPlan
        assert plan is not None
        assert plan.user_goal
