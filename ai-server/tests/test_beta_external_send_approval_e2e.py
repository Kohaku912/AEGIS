"""Beta E2E: External Send Approval — SNS post requires approval.

Scenario:
  User: "この内容をSNSに投稿して"
  → LLMTaskInterpreter identifies EXTERNAL_SEND
  → Approval UI receives the request
  → No auto-post without approval
"""

from __future__ import annotations

import json
import time

from aegis_ai.interaction.message import Channel, Message
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
from aegis_ai.task_plan import RiskCategory, TaskPlan


class MockLLMProvider:
    """Mock LLM for external send."""

    def __init__(self):
        self._response = {
            "user_goal": "Post to SNS",
            "interpreted_request": "Post content to social media",
            "assumptions": ["User wants to post publicly"],
            "required_context": [],
            "steps": [
                {
                    "step_id": "step_1",
                    "description": "Post to SNS",
                    "action_type": "browser_submit",
                    "capability_id": "browser.publish_post",
                    "params": {},
                    "risk_category": "EXTERNAL_SEND",
                    "requires_approval": True,
                    "expected_result": "Post published",
                },
            ],
            "required_capabilities": ["browser.publish_post"],
            "risk_notes": ["External send requires approval"],
            "approval_needed": True,
            "stop_conditions": [],
            "expected_result": "Post submitted for approval",
            "verification_plan": "Check approval UI received request",
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


class MockApprovalStore:
    """Mock approval store."""

    def __init__(self):
        self._pending = []

    def get_pending(self):
        return self._pending


# ═══════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════


class TestBetaExternalSendApprovalE2E:
    """External send approval E2E test."""

    def test_sns_post_requires_approval(self):
        """SNS post plan requires approval."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("この内容をSNSに投稿して")

        assert plan is not None
        assert plan.approval_needed is True

    def test_sns_post_has_external_send_risk(self):
        """SNS post steps have EXTERNAL_SEND risk."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Post to SNS")

        send_steps = [s for s in plan.steps if s.risk_category == RiskCategory.EXTERNAL_SEND]
        assert len(send_steps) >= 1

        for step in send_steps:
            assert step.requires_approval is True

    def test_router_returns_approval_message(self):
        """Router returns approval message for external send."""
        llm = MockLLMProvider()
        approval = MockApprovalStore()
        router = InteractionRouter(llm_provider=llm, approval_store=approval)

        msg = Message(
            text="この内容をSNSに投稿して",
            timestamp_ms=int(time.time() * 1000),
        )
        response = router.route(msg)

        # Should mention approval
        assert "approval" in response.text.lower() or "承認" in response.text

    def test_no_auto_post_without_approval(self):
        """No auto-post without approval."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Post to SNS")

        # All EXTERNAL_SEND steps should require approval
        for step in plan.steps:
            if step.risk_category == RiskCategory.EXTERNAL_SEND:
                assert step.requires_approval is True
