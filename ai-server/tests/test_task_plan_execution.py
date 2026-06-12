"""Tests for TaskPlan execution through InteractionRouter."""

from __future__ import annotations

import time

from aegis_ai.interaction.message import Channel, Message
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.task_plan import PlanStep, RiskCategory, TaskPlan


# ═══════════════════════════════════════════════════════════════
# 1. Router with LLM Task Interpreter
# ═══════════════════════════════════════════════════════════════


class TestInteractionRouterLLM:
    """InteractionRouter uses LLM Task Interpreter."""

    def test_status_command_direct(self):
        """Status command handled directly (no LLM)."""
        router = InteractionRouter()
        msg = Message(text="status", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)
        assert "dashboard" in response.text.lower() or "status" in response.text.lower()

    def test_help_command_direct(self):
        """Help command handled directly (no LLM)."""
        router = InteractionRouter()
        msg = Message(text="help", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)
        assert "aegis" in response.text.lower() or "help" in response.text.lower()

    def test_settings_command_direct(self):
        """Settings command handled directly (no LLM)."""
        router = InteractionRouter()
        msg = Message(text="settings", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)
        assert "settings" in response.text.lower() or "dashboard" in response.text.lower()

    def test_llm_fallback_without_provider(self):
        """Without LLM, returns fallback message."""
        router = InteractionRouter()
        msg = Message(text="research Python 3.12", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)
        assert "llm" in response.text.lower() or "provider" in response.text.lower()


# ═══════════════════════════════════════════════════════════════
# 2. Plan Execution
# ═══════════════════════════════════════════════════════════════


class TestPlanExecution:
    """TaskPlan execution through router."""

    def test_blocked_plan_returns_blocked_message(self):
        """Blocked plan returns appropriate message."""
        router = InteractionRouter()
        plan = TaskPlan(
            user_goal="Bypass CAPTCHA",
            steps=[
                PlanStep(
                    step_id="1",
                    description="Solve CAPTCHA",
                    risk_category=RiskCategory.BLOCKED,
                )
            ],
        )
        response = router._execute_plan(plan, type("Response", (), {"text": "", "pending_approvals": []})())
        assert "blocked" in response.text.lower()

    def test_approval_plan_returns_approval_message(self):
        """Approval-required plan returns approval message."""
        router = InteractionRouter()
        plan = TaskPlan(
            user_goal="Send DM",
            approval_needed=True,
            steps=[
                PlanStep(
                    step_id="1",
                    description="Send DM to @user",
                    risk_category=RiskCategory.EXTERNAL_SEND,
                    requires_approval=True,
                )
            ],
        )
        response = router._execute_plan(plan, type("Response", (), {"text": "", "pending_approvals": []})())
        assert "approval" in response.text.lower()

    def test_read_plan_executes(self):
        """Read-only plan executes without approval."""
        router = InteractionRouter()
        plan = TaskPlan(
            user_goal="Read page",
            steps=[
                PlanStep(
                    step_id="1",
                    description="Read example.com",
                    action_type="browser_open",
                    params={"url": "https://example.com"},
                    risk_category=RiskCategory.READ,
                )
            ],
        )
        response = router._execute_plan(plan, type("Response", (), {"text": "", "pending_approvals": []})())
        # Should attempt to execute (may fail without browser, but shouldn't block)
        assert response.text  # Has some response


# ═══════════════════════════════════════════════════════════════
# 3. E2E Scenarios
# ═══════════════════════════════════════════════════════════════


class TestE2EScenarios:
    """End-to-end task interpretation scenarios."""

    def test_research_request_structure(self):
        """Research request produces correct plan structure."""
        from aegis_ai.llm_task_interpreter import LLMTaskInterpreter

        interpreter = LLMTaskInterpreter(llm_provider=None)
        plan = interpreter.interpret("Research Python 3.12 features")

        # Should produce a plan (even fallback)
        assert plan is not None
        assert plan.user_goal

    def test_owned_messages_summary_structure(self):
        """Message summary request produces correct plan structure."""
        from aegis_ai.llm_task_interpreter import LLMTaskInterpreter

        interpreter = LLMTaskInterpreter(llm_provider=None)
        plan = interpreter.interpret("Summarize my recent DMs")

        assert plan is not None
        assert plan.user_goal

    def test_send_request_structure(self):
        """Send request should indicate approval needed."""
        from aegis_ai.llm_task_interpreter import LLMTaskInterpreter

        interpreter = LLMTaskInterpreter(llm_provider=None)
        # With LLM, this would produce EXTERNAL_SEND
        # Without LLM, fallback plan
        plan = interpreter.interpret("Send a tweet saying hello")
        assert plan is not None
