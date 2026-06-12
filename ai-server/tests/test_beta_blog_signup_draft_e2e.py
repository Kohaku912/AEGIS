"""Beta E2E: Blog Signup + Draft — free blog creation and article draft.

Scenario:
  User: "無料ブログを作って、最初の記事の下書きを作って"
  → LLMTaskInterpreter creates signup + draft TaskPlan
  → Browser-use proceeds with signup
  → Stops at CAPTCHA/payment/identity verification
  → Article draft created locally
  → Publish requires Approval UI
"""

from __future__ import annotations

import json
import time

from aegis_ai.interaction.message import Channel, Message
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
from aegis_ai.task_plan import RiskCategory, TaskPlan


class MockLLMProvider:
    """Mock LLM for blog signup + draft."""

    def __init__(self):
        self._response = {
            "user_goal": "Create free blog and write first article draft",
            "interpreted_request": "Sign up for a free blog platform and create a draft article",
            "assumptions": ["Free blog platform available", "No payment required"],
            "required_context": [],
            "steps": [
                {
                    "step_id": "step_1",
                    "description": "Find free blog platform",
                    "action_type": "browser_open",
                    "capability_id": "browser.open_page",
                    "params": {"url": "https://example.com/signup"},
                    "risk_category": "READ",
                    "requires_approval": False,
                    "expected_result": "Signup page loaded",
                },
                {
                    "step_id": "step_2",
                    "description": "Fill signup form (free, no payment)",
                    "action_type": "browser_fill",
                    "capability_id": "browser.fill_signup_form",
                    "params": {},
                    "risk_category": "READ",
                    "requires_approval": False,
                    "expected_result": "Form filled",
                    "depends_on": ["step_1"],
                },
                {
                    "step_id": "step_3",
                    "description": "Create article draft",
                    "action_type": "llm_analyze",
                    "capability_id": "",
                    "params": {},
                    "risk_category": "DRAFT",
                    "requires_approval": False,
                    "expected_result": "Article draft created",
                    "depends_on": ["step_2"],
                },
            ],
            "required_capabilities": ["browser.open_page", "browser.fill_signup_form"],
            "risk_notes": ["Signup is free only", "Draft is local only"],
            "approval_needed": False,
            "stop_conditions": ["captcha_detected", "payment_required", "identity_verification"],
            "expected_result": "Blog created with draft article",
            "verification_plan": "Check blog created and draft exists",
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
    """Mock browser for signup."""

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
            result_text="**Blog Created**\n\nBlog URL: https://myblog.example.com\nDraft: 'My First Post' saved",
        )


# ═══════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════


class TestBetaBlogSignupDraftE2E:
    """Blog signup + draft E2E test."""

    def test_signup_plan_has_stop_conditions(self):
        """Signup plan includes stop conditions."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("無料ブログを作って、最初の記事の下書きを作って")

        assert plan is not None
        assert len(plan.stop_conditions) > 0

    def test_signup_plan_no_payment(self):
        """Signup plan does not include payment steps."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Create free blog")

        payment_steps = [s for s in plan.steps if s.risk_category == RiskCategory.PAYMENT]
        assert len(payment_steps) == 0

    def test_draft_is_local_only(self):
        """Draft steps are DRAFT category."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Create blog and write draft")

        draft_steps = [s for s in plan.steps if s.risk_category == RiskCategory.DRAFT]
        assert len(draft_steps) >= 1

        for step in draft_steps:
            assert step.requires_approval is False

    def test_publish_requires_approval(self):
        """Publish step requires approval (if present)."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Create blog and publish")

        # If there's an EXTERNAL_SEND step, it needs approval
        send_steps = [s for s in plan.steps if s.risk_category == RiskCategory.EXTERNAL_SEND]
        for step in send_steps:
            assert step.requires_approval is True

    def test_signup_executes_through_router(self):
        """Signup request executes through router."""
        llm = MockLLMProvider()
        browser = MockBrowserExecutor()
        router = InteractionRouter(llm_provider=llm, browser_executor=browser)

        msg = Message(
            text="無料ブログを作って、最初の記事の下書きを作って",
            timestamp_ms=int(time.time() * 1000),
        )
        response = router.route(msg)

        assert response.text
