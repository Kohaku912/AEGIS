"""Beta E2E: PC Screen Context — understand PC screen state.

Scenario:
  User: "今のPC画面を見て何をすればいいか教えて"
  → LLMTaskInterpreter creates observe TaskPlan
  → PC Server returns screenshot + active window
  → AEGIS explains situation
  → No PC actions taken
"""

from __future__ import annotations

import json

from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
from aegis_ai.task_plan import RiskCategory


class MockLLMProvider:
    """Mock LLM for PC screen context."""

    def __init__(self):
        self._response = {
            "user_goal": "Understand current PC screen state",
            "interpreted_request": "Take screenshot and analyze what's on screen",
            "assumptions": ["PC Server is connected"],
            "required_context": [],
            "steps": [
                {
                    "step_id": "step_1",
                    "description": "Get current screenshot",
                    "action_type": "tool_invoke",
                    "capability_id": "pc.get_screenshot",
                    "params": {},
                    "risk_category": "OBSERVE",
                    "requires_approval": False,
                    "expected_result": "Screenshot captured",
                },
                {
                    "step_id": "step_2",
                    "description": "Get active window info",
                    "action_type": "tool_invoke",
                    "capability_id": "pc.get_active_window",
                    "params": {},
                    "risk_category": "OBSERVE",
                    "requires_approval": False,
                    "expected_result": "Active window info",
                },
                {
                    "step_id": "step_3",
                    "description": "Analyze screen state",
                    "action_type": "llm_analyze",
                    "capability_id": "",
                    "params": {},
                    "risk_category": "READ",
                    "requires_approval": False,
                    "expected_result": "Analysis of current screen",
                    "depends_on": ["step_1", "step_2"],
                },
            ],
            "required_capabilities": ["pc.get_screenshot", "pc.get_active_window"],
            "risk_notes": ["Observe only", "No PC actions"],
            "approval_needed": False,
            "stop_conditions": [],
            "expected_result": "Description of current PC screen state",
            "verification_plan": "Check analysis describes screen",
            "needs_browser": False,
            "needs_device": True,
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


class MockToolBroker:
    """Mock tool broker for PC operations."""

    def invoke_tool(self, capability_id: str, params: dict = None):
        from dataclasses import dataclass, field
        from enum import Enum, auto

        class InvokeStatus(Enum):
            SUCCESS = auto()
            DENIED = auto()
            APPROVAL_NEEDED = auto()

        @dataclass
        class InvokeResult:
            status: InvokeStatus = InvokeStatus.SUCCESS
            capability_id: str = ""
            output: dict = field(default_factory=dict)
            error: str = ""
            success: bool = True

        if capability_id == "pc.get_screenshot":
            return InvokeResult(
                capability_id=capability_id,
                output={"image_base64": "mock_screenshot", "width": 1920, "height": 1080},
            )
        elif capability_id == "pc.get_active_window":
            return InvokeResult(
                capability_id=capability_id,
                output={"title": "VS Code - AEGIS", "process": "code.exe", "pid": 12345},
            )
        return InvokeResult(capability_id=capability_id)


# ═══════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════


class TestBetaPCScreenContextE2E:
    """PC screen context E2E test."""

    def test_screen_plan_is_observe(self):
        """Screen plan uses OBSERVE risk category."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("今のPC画面を見て何をすればいいか教えて")

        assert plan is not None
        observe_steps = [s for s in plan.steps if s.risk_category == RiskCategory.OBSERVE]
        assert len(observe_steps) >= 1

    def test_screen_plan_no_device_action(self):
        """Screen plan does not include device actions."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Look at PC screen")

        action_steps = [s for s in plan.steps if s.risk_category == RiskCategory.DEVICE_ACTION]
        assert len(action_steps) == 0

    def test_screen_plan_needs_device(self):
        """Screen plan indicates device is needed."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Look at PC screen")

        assert plan.needs_device is True

    def test_screen_plan_no_approval(self):
        """Screen plan does not need approval."""
        llm = MockLLMProvider()
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("Look at PC screen")

        assert plan.approval_needed is False
