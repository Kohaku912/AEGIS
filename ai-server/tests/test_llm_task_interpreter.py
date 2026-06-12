"""Tests for LLM Task Interpreter — Beta architecture."""

from __future__ import annotations

import json

from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
from aegis_ai.task_plan import PlanStep, RiskCategory, StepStatus, TaskPlan

# ═══════════════════════════════════════════════════════════════
# 1. TaskPlan Structure
# ═══════════════════════════════════════════════════════════════


class TestTaskPlan:
    """TaskPlan data structure works correctly."""

    def test_task_plan_creation(self):
        """TaskPlan can be created with all fields."""
        plan = TaskPlan(
            plan_id="test_001",
            user_goal="Check Twitter notifications",
            interpreted_request="Read and summarize Twitter notifications",
            assumptions=["User is logged in"],
            risk_notes=["Read-only operation"],
            expected_result="Summary of notifications",
        )
        assert plan.plan_id == "test_001"
        assert plan.user_goal == "Check Twitter notifications"

    def test_plan_step_creation(self):
        """PlanStep can be created."""
        step = PlanStep(
            step_id="step_1",
            description="Open Twitter",
            action_type="browser_open",
            capability_id="browser.open_page",
            risk_category=RiskCategory.READ,
        )
        assert step.risk_category == RiskCategory.READ
        assert step.requires_approval is False

    def test_has_approval_required_steps(self):
        """Detects approval-required steps."""
        plan = TaskPlan(steps=[
            PlanStep(step_id="1", risk_category=RiskCategory.READ),
            PlanStep(step_id="2", risk_category=RiskCategory.EXTERNAL_SEND, requires_approval=True),
        ])
        assert plan.has_approval_required_steps() is True

    def test_has_blocked_steps(self):
        """Detects blocked steps."""
        plan = TaskPlan(steps=[
            PlanStep(step_id="1", risk_category=RiskCategory.READ),
            PlanStep(step_id="2", risk_category=RiskCategory.BLOCKED),
        ])
        assert plan.has_blocked_steps() is True

    def test_mark_step_complete(self):
        """Can mark step as completed."""
        plan = TaskPlan(steps=[
            PlanStep(step_id="step_1", description="Test"),
        ])
        plan.mark_step_complete("step_1", result="Done")
        assert plan.steps[0].status == StepStatus.COMPLETED
        assert plan.steps[0].result == "Done"

    def test_mark_step_failed(self):
        """Can mark step as failed."""
        plan = TaskPlan(steps=[
            PlanStep(step_id="step_1", description="Test"),
        ])
        plan.mark_step_failed("step_1", error="Network error")
        assert plan.steps[0].status == StepStatus.FAILED
        assert plan.steps[0].error == "Network error"

    def test_to_dict(self):
        """Can convert to dictionary."""
        plan = TaskPlan(
            plan_id="test",
            user_goal="Test goal",
            steps=[PlanStep(step_id="1", description="Step 1")],
        )
        d = plan.to_dict()
        assert d["plan_id"] == "test"
        assert len(d["steps"]) == 1


# ═══════════════════════════════════════════════════════════════
# 2. LLM Task Interpreter
# ═══════════════════════════════════════════════════════════════


class TestLLMTaskInterpreter:
    """LLM Task Interpreter produces valid TaskPlans."""

    def test_fallback_without_llm(self):
        """Without LLM, returns fallback plan."""
        interpreter = LLMTaskInterpreter(llm_provider=None)
        plan = interpreter.interpret("Hello")
        assert "LLM" in plan.expected_result or "llm" in plan.expected_result.lower()

    def test_parse_valid_json(self):
        """Parses valid JSON response."""
        interpreter = LLMTaskInterpreter(llm_provider=None)
        json_str = json.dumps({
            "user_goal": "Read example.com",
            "interpreted_request": "Navigate to example.com and extract text",
            "assumptions": ["Site is accessible"],
            "required_context": [],
            "steps": [
                {
                    "step_id": "step_1",
                    "description": "Open example.com",
                    "action_type": "browser_open",
                    "capability_id": "browser.open_page",
                    "params": {"url": "https://example.com"},
                    "risk_category": "READ",
                    "requires_approval": False,
                    "expected_result": "Page loaded",
                    "depends_on": [],
                }
            ],
            "required_capabilities": ["browser.open_page"],
            "risk_notes": [],
            "approval_needed": False,
            "stop_conditions": [],
            "expected_result": "Text from example.com",
            "verification_plan": "Check text is extracted",
            "needs_browser": True,
            "needs_device": False,
        })

        plan = interpreter._parse_response(json_str, "Read example.com")
        assert plan is not None
        assert plan.user_goal == "Read example.com"
        assert len(plan.steps) == 1
        assert plan.steps[0].risk_category == RiskCategory.READ

    def test_blocked_action_detected(self):
        """CAPTCHA bypass is detected as blocked."""
        interpreter = LLMTaskInterpreter(llm_provider=None)
        json_str = json.dumps({
            "user_goal": "Bypass CAPTCHA",
            "interpreted_request": "Solve CAPTCHA",
            "steps": [
                {
                    "step_id": "step_1",
                    "description": "Solve CAPTCHA",
                    "action_type": "browser_solve",
                    "risk_category": "READ",
                }
            ],
            "needs_browser": True,
        })

        plan = interpreter._parse_response(json_str, "Bypass CAPTCHA")
        assert plan is not None
        # Run safety validation
        interpreter._validate_safety(plan)
        assert plan.steps[0].risk_category == RiskCategory.BLOCKED

    def test_external_send_needs_approval(self):
        """External send operations need approval."""
        interpreter = LLMTaskInterpreter(llm_provider=None)
        json_str = json.dumps({
            "user_goal": "Send DM",
            "interpreted_request": "Send a DM on Twitter",
            "steps": [
                {
                    "step_id": "step_1",
                    "description": "Send DM",
                    "action_type": "browser_send",
                    "risk_category": "EXTERNAL_SEND",
                }
            ],
            "needs_browser": True,
        })

        plan = interpreter._parse_response(json_str, "Send DM")
        assert plan is not None
        # Run safety validation
        interpreter._validate_safety(plan)
        assert plan.steps[0].requires_approval is True
        assert plan.approval_needed is True

    def test_invalid_json_returns_none(self):
        """Invalid JSON returns None."""
        interpreter = LLMTaskInterpreter(llm_provider=None)
        result = interpreter._parse_response("not json", "test")
        assert result is None


# ═══════════════════════════════════════════════════════════════
# 3. Risk Categories
# ═══════════════════════════════════════════════════════════════


class TestRiskCategories:
    """Risk category handling works correctly."""

    def test_read_is_safe(self):
        """READ category is safe."""
        step = PlanStep(risk_category=RiskCategory.READ)
        assert step.requires_approval is False

    def test_draft_is_safe(self):
        """DRAFT category is safe."""
        step = PlanStep(risk_category=RiskCategory.DRAFT)
        assert step.requires_approval is False

    def test_external_send_needs_approval(self):
        """EXTERNAL_SEND needs approval."""
        step = PlanStep(risk_category=RiskCategory.EXTERNAL_SEND, requires_approval=True)
        assert step.requires_approval is True

    def test_blocked_is_blocked(self):
        """BLOCKED category is blocked."""
        step = PlanStep(risk_category=RiskCategory.BLOCKED)
        assert step.risk_category == RiskCategory.BLOCKED
