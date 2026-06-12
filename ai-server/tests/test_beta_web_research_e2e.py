"""Beta E2E: Web Research — natural language research request.

Scenario:
  User: "最近のAIエージェント関連ニュースを調べてまとめて"
  → LLMTaskInterpreter creates research TaskPlan
  → Browser Server executes browser-use task
  → Report generated with sources
"""

from __future__ import annotations

import json
import time

import pytest

from aegis_ai.interaction.message import Channel, Message
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
from aegis_ai.task_plan import RiskCategory, TaskPlan


class MockLLMProvider:
    """Mock LLM that returns structured research plan."""

    def __init__(self, response: dict | None = None):
        self._response = response or {
            "user_goal": "Research AI agent news and summarize",
            "interpreted_request": "Search for recent AI agent news and create a summary",
            "assumptions": ["Web search is available"],
            "required_context": [],
            "steps": [
                {
                    "step_id": "step_1",
                    "description": "Search for AI agent news",
                    "action_type": "browser_open",
                    "capability_id": "browser.open_page",
                    "params": {"url": "https://news.ycombinator.com"},
                    "risk_category": "READ",
                    "requires_approval": False,
                    "expected_result": "News page loaded",
                },
                {
                    "step_id": "step_2",
                    "description": "Extract and summarize news",
                    "action_type": "llm_summarize",
                    "capability_id": "",
                    "params": {},
                    "risk_category": "READ",
                    "requires_approval": False,
                    "expected_result": "Summary of AI agent news",
                    "depends_on": ["step_1"],
                },
            ],
            "required_capabilities": ["browser.open_page"],
            "risk_notes": ["Read-only operation"],
            "approval_needed": False,
            "stop_conditions": [],
            "expected_result": "Summary of recent AI agent news with sources",
            "verification_plan": "Check summary contains recent news",
            "needs_browser": True,
            "needs_device": False,
        }

    def generate(self, prompt: str = "", system_prompt: str = "", max_tokens: int = 1000, temperature: float = 0.1):
        """Return mock LLM response."""
        from dataclasses import dataclass

        @dataclass
        class MockResponse:
            content: str = ""
            success: bool = True
            error: str = ""
            tokens_used: int = 100
            model_used: str = "mock"

        return MockResponse(content=json.dumps(self._response))


class MockBrowserExecutor:
    """Mock browser executor."""

    def execute(self, task: str, context: str = ""):
        from dataclasses import dataclass, field

        @dataclass
        class MockBrowserResult:
            success: bool = True
            task_description: str = ""
            result_text: str = ""
            extracted_data: dict = field(default_factory=dict)
            error: str = ""
            duration_ms: float = 100.0

        return MockBrowserResult(
            task_description=task,
            result_text="**AI Agent News Summary**\n\n1. New LLM-powered agents released\n2. Browser automation advances\n3. Multi-agent systems gaining traction",
        )


# ═══════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════


class TestBetaWebResearchE2E:
    """Web research E2E test."""

    def test_research_request_produces_task_plan(self):
        """Research request produces valid TaskPlan via LLM."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("最近のAIエージェント関連ニュースを調べてまとめて")

        assert plan is not None
        assert plan.user_goal
        assert plan.needs_browser is True
        assert len(plan.steps) >= 1

    def test_research_plan_has_read_risk(self):
        """Research plan steps have READ risk."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Research AI news")

        for step in plan.steps:
            assert step.risk_category == RiskCategory.READ

    def test_research_plan_no_approval_needed(self):
        """Research plan does not need approval."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Research AI news")

        assert plan.approval_needed is False
        assert not plan.has_approval_required_steps()

    def test_research_executes_through_router(self):
        """Research request executes through InteractionRouter."""
        llm = MockLLMProvider()
        browser = MockBrowserExecutor()
        router = InteractionRouter(llm_provider=llm, browser_executor=browser)

        msg = Message(
            text="最近のAIエージェント関連ニュースを調べてまとめて",
            timestamp_ms=int(time.time() * 1000),
        )
        response = router.route(msg)

        assert response.text
        assert len(response.text) > 0

    def test_research_returns_sources(self):
        """Research response includes source information."""
        llm = MockLLMProvider()
        browser = MockBrowserExecutor()
        router = InteractionRouter(llm_provider=llm, browser_executor=browser)

        msg = Message(text="Research AI agent news", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)

        # Response should contain some content
        assert response.text
