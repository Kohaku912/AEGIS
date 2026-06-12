"""Tests for LLM Task Interpreter — Beta architecture."""

from __future__ import annotations

from aegis_ai.browser_use.executor import BrowserUseSafetyBoundary
from aegis_ai.interaction.task_interpreter import (
    LLMTaskInterpreter,
    RiskLevel,
    TaskAction,
    TaskPlan,
    TaskType,
)

# ═══════════════════════════════════════════════════════════════
# 1. Task Interpreter
# ═══════════════════════════════════════════════════════════════


class TestLLMTaskInterpreter:
    """LLM Task Interpreter produces valid TaskPlans."""

    def test_fallback_without_llm(self):
        """Without LLM, returns fallback plan."""
        interpreter = LLMTaskInterpreter(llm_provider=None)
        plan = interpreter.interpret("Hello")
        assert plan.task_type == TaskType.CONVERSATION
        assert "LLM" in plan.response_text

    def test_parse_json_response(self):
        """Parses valid JSON response into TaskPlan."""
        interpreter = LLMTaskInterpreter(llm_provider=None)
        json_str = '''
        {
            "goal": "Read example.com",
            "task_type": "BROWSE",
            "actions": [
                {
                    "action_type": "browser_open",
                    "description": "Open example.com",
                    "params": {"url": "https://example.com"},
                    "risk_level": "READ",
                    "capability_id": "browser.open_page"
                }
            ],
            "constraints": [],
            "risk_summary": "Low risk",
            "needs_browser": true,
            "needs_device": false,
            "approval_required": false,
            "response_text": null
        }
        '''
        plan = interpreter._parse_response(json_str, "Read example.com")
        assert plan.task_type == TaskType.BROWSE
        assert plan.needs_browser is True
        assert len(plan.actions) == 1
        assert plan.actions[0].risk_level == RiskLevel.READ

    def test_blocked_action_detected(self):
        """CAPTCHA bypass is detected as blocked."""
        interpreter = LLMTaskInterpreter(llm_provider=None)
        json_str = '''
        {
            "goal": "Bypass CAPTCHA",
            "task_type": "BROWSE_AND_ACT",
            "actions": [
                {
                    "action_type": "browser_solve_captcha",
                    "description": "Solve CAPTCHA on page",
                    "params": {},
                    "risk_level": "READ"
                }
            ],
            "needs_browser": true,
            "approval_required": false,
            "response_text": null
        }
        '''
        plan = interpreter._parse_response(json_str, "Bypass CAPTCHA")
        # Safety validation should mark as blocked
        assert plan.actions[0].risk_level == RiskLevel.BLOCKED


# ═══════════════════════════════════════════════════════════════
# 2. Browser-Use Safety Boundary
# ═══════════════════════════════════════════════════════════════


class TestBrowserUseSafetyBoundary:
    """Safety boundary checks work correctly."""

    def test_read_task_allowed(self):
        """Read tasks are allowed."""
        safety = BrowserUseSafetyBoundary()
        check = safety.check_task("Go to example.com and read the text")
        assert check["allowed"] is True
        assert check["risk"] == "READ"

    def test_captcha_blocked(self):
        """CAPTCHA tasks are blocked."""
        safety = BrowserUseSafetyBoundary()
        check = safety.check_task("Solve the CAPTCHA on this page")
        assert check["allowed"] is False
        assert check["risk"] == "BLOCKED"

    def test_purchase_blocked(self):
        """Purchase tasks are blocked."""
        safety = BrowserUseSafetyBoundary()
        check = safety.check_task("Purchase this item on Amazon")
        assert check["allowed"] is False
        assert check["risk"] == "BLOCKED"

    def test_send_requires_approval(self):
        """Send tasks require approval."""
        safety = BrowserUseSafetyBoundary()
        check = safety.check_task("Send a DM to @user on Twitter")
        assert check["allowed"] is True
        assert check["risk"] == "APPROVAL_REQUIRED"

    def test_post_requires_approval(self):
        """Post tasks require approval."""
        safety = BrowserUseSafetyBoundary()
        check = safety.check_task("Post a tweet saying hello")
        assert check["allowed"] is True
        assert check["risk"] == "APPROVAL_REQUIRED"

    def test_spam_blocked(self):
        """Spam tasks are blocked."""
        safety = BrowserUseSafetyBoundary()
        check = safety.check_task("Send bulk DMs to all followers")
        assert check["allowed"] is False
        assert check["risk"] == "BLOCKED"


# ═══════════════════════════════════════════════════════════════
# 3. Task Plan
# ═══════════════════════════════════════════════════════════════


class TestTaskPlan:
    """TaskPlan data structure works correctly."""

    def test_task_plan_creation(self):
        """TaskPlan can be created."""
        plan = TaskPlan(
            goal="Read example.com",
            task_type=TaskType.BROWSE,
            needs_browser=True,
        )
        assert plan.goal == "Read example.com"
        assert plan.task_type == TaskType.BROWSE

    def test_task_action_creation(self):
        """TaskAction can be created."""
        action = TaskAction(
            action_type="browser_open",
            description="Open example.com",
            risk_level=RiskLevel.READ,
        )
        assert action.risk_level == RiskLevel.READ
        assert action.requires_approval is False

    def test_external_send_action_needs_approval(self):
        """EXTERNAL_SEND actions should require approval."""
        action = TaskAction(
            action_type="browser_submit",
            description="Submit form",
            risk_level=RiskLevel.EXTERNAL_SEND,
            requires_approval=True,
        )
        assert action.requires_approval is True
