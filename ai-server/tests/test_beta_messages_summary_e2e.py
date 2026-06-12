"""Beta E2E: Messages Summary — read and summarize owned messages.

Scenario:
  User: "最近のメッセージを見て重要そうなものをまとめて"
  → LLMTaskInterpreter creates read/summarize TaskPlan
  → Browser reads fixture page
  → Summary + draft reply created
  → No send/publish
"""

from __future__ import annotations

import json
import time

from aegis_ai.interaction.message import Message
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
from aegis_ai.task_plan import RiskCategory


class MockLLMProvider:
    """Mock LLM for message summary."""

    def __init__(self):
        self._response = {
            "user_goal": "Summarize recent messages",
            "interpreted_request": "Read recent messages and summarize important ones",
            "assumptions": ["User is logged into messaging platform"],
            "required_context": [],
            "steps": [
                {
                    "step_id": "step_1",
                    "description": "Read recent messages",
                    "action_type": "browser_read",
                    "capability_id": "browser.read_messages",
                    "params": {},
                    "risk_category": "READ",
                    "requires_approval": False,
                    "expected_result": "Messages retrieved",
                },
                {
                    "step_id": "step_2",
                    "description": "Summarize important messages",
                    "action_type": "llm_summarize",
                    "capability_id": "",
                    "params": {},
                    "risk_category": "READ",
                    "requires_approval": False,
                    "expected_result": "Summary of important messages",
                    "depends_on": ["step_1"],
                },
                {
                    "step_id": "step_3",
                    "description": "Draft reply for urgent message",
                    "action_type": "llm_analyze",
                    "capability_id": "",
                    "params": {},
                    "risk_category": "DRAFT",
                    "requires_approval": False,
                    "expected_result": "Draft reply text",
                    "depends_on": ["step_2"],
                },
            ],
            "required_capabilities": ["browser.read_messages"],
            "risk_notes": ["Read-only", "Draft is local only"],
            "approval_needed": False,
            "stop_conditions": [],
            "expected_result": "Summary of important messages with draft replies",
            "verification_plan": "Check summary and drafts",
            "needs_browser": True,
            "needs_device": False,
        }

    def generate(self, prompt: str = "", system_prompt: str = "", max_tokens: int = 1000, temperature: float = 0.1):
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
    """Mock browser that returns message fixture."""

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
            result_text=(
                "**Messages Summary**\n\n"
                "1. Meeting reminder from boss (URGENT)\n"
                "2. Project update from team\n"
                "3. Newsletter (low priority)"
            ),
        )


# ═══════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════


class TestBetaMessagesSummaryE2E:
    """Messages summary E2E test."""

    def test_summary_plan_is_read_only(self):
        """Summary plan has READ risk categories."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("最近のメッセージを見て重要そうなものをまとめて")

        assert plan is not None
        # Main steps should be READ
        read_steps = [s for s in plan.steps if s.risk_category == RiskCategory.READ]
        assert len(read_steps) >= 1

    def test_summary_no_external_send(self):
        """Summary plan does not contain external send steps."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Summarize my messages")

        send_steps = [s for s in plan.steps if s.risk_category == RiskCategory.EXTERNAL_SEND]
        assert len(send_steps) == 0

    def test_summary_draft_is_local(self):
        """Draft steps are DRAFT category (local only)."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Summarize messages and draft replies")

        draft_steps = [s for s in plan.steps if s.risk_category == RiskCategory.DRAFT]
        # DRAFT steps should not require approval
        for step in draft_steps:
            assert step.requires_approval is False

    def test_summary_executes_through_router(self):
        """Summary request executes through router."""
        llm = MockLLMProvider()
        browser = MockBrowserExecutor()
        router = InteractionRouter(llm_provider=llm, browser_executor=browser)

        msg = Message(
            text="最近のメッセージを見て重要そうなものをまとめて",
            timestamp_ms=int(time.time() * 1000),
        )
        response = router.route(msg)

        assert response.text
        assert len(response.text) > 0
