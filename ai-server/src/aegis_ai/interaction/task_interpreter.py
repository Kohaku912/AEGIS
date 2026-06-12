"""LLM Task Interpreter — replaces intent classifier with LLM-based understanding.

The LLM interprets user messages and produces structured TaskPlans.
No keyword matching — the LLM understands natural language.

Safety: TaskPlans are validated by PolicyEngine before execution.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

logger = logging.getLogger("aegis_ai.interaction.task_interpreter")


class TaskType(Enum):
    """High-level task categories."""
    RESEARCH = auto()          # Web research, information gathering
    BROWSE = auto()            # Browser navigation and reading
    BROWSE_AND_ACT = auto()    # Browser with form filling, clicking
    DRAFT = auto()             # Create drafts (posts, replies, emails)
    STATUS = auto()            # System status check
    SETTINGS = auto()          # Settings query/change
    HELP = auto()              # Help and documentation
    APPROVAL = auto()          # Approval decisions
    CONVERSATION = auto()      # General conversation
    DEVICE_CONTROL = auto()    # PC/Android/Room control


class RiskLevel(Enum):
    """Risk level for task actions."""
    READ = auto()              # Read-only, no side effects
    DRAFT = auto()             # Create content locally, no external send
    EXTERNAL_SEND = auto()     # Send/post/publish externally (needs approval)
    PAYMENT = auto()           # Financial operations (blocked or approval)
    BLOCKED = auto()           # Always blocked (CAPTCHA bypass, etc.)


@dataclass
class TaskAction:
    """A single action within a task plan."""
    action_type: str = ""      # "browser_open", "browser_read", "browser_fill", etc.
    description: str = ""      # Human-readable description
    params: dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.READ
    requires_approval: bool = False
    capability_id: str = ""    # For ToolBroker integration


@dataclass
class TaskPlan:
    """Structured task plan produced by LLM Task Interpreter."""
    goal: str = ""                      # What the user wants
    task_type: TaskType = TaskType.CONVERSATION
    actions: list[TaskAction] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)   # Safety constraints
    risk_summary: str = ""              # Overall risk assessment
    needs_browser: bool = False
    needs_device: bool = False          # PC/Android/Room
    approval_required: bool = False     # Any action needs approval
    response_text: str = ""             # Direct response if no actions needed
    raw_llm_response: str = ""          # For debugging


class LLMTaskInterpreter:
    """Interprets user messages using LLM to produce TaskPlans.

    Usage:
        interpreter = LLMTaskInterpreter(llm_provider=llm)
        plan = interpreter.interpret("research Python 3.12 features")
    """

    SYSTEM_PROMPT = """You are AEGIS's task interpreter. Analyze the user's message and produce a structured task plan.

Output JSON with this structure:
{
  "goal": "What the user wants to accomplish",
  "task_type": "RESEARCH|BROWSE|BROWSE_AND_ACT|DRAFT|STATUS|SETTINGS|HELP|APPROVAL|CONVERSATION|DEVICE_CONTROL",
  "actions": [
    {
      "action_type": "browser_open|browser_read|browser_fill|browser_click|browser_submit|draft_create|device_execute|llm_respond",
      "description": "What this action does",
      "params": {},
      "risk_level": "READ|DRAFT|EXTERNAL_SEND|PAYMENT|BLOCKED",
      "capability_id": "browser.open_page|browser.read_owned_account_page|..."
    }
  ],
  "constraints": ["List of safety constraints"],
  "risk_summary": "Overall risk assessment",
  "needs_browser": true/false,
  "needs_device": true/false,
  "approval_required": true/false,
  "response_text": "Direct text response if no actions needed (null if actions exist)"
}

Safety rules (ALWAYS apply):
- CAPTCHA bypass, bot evasion, stealth, proxy abuse → BLOCKED
- Spam, bulk signup, bulk DM → BLOCKED
- Payment, purchase, paid subscription → BLOCKED or requires approval
- Password/2FA entry → requires user action or explicit approval
- SNS post, DM send, email send, blog publish → requires approval (EXTERNAL_SEND)
- Reading user-owned accounts (SNS, email, notifications) → READ (allowed)
- Creating drafts (not sending) → DRAFT (allowed)
- Low-risk form filling (free, no payment) → READ or DRAFT

Respond with ONLY the JSON object, no markdown fences."""

    def __init__(self, llm_provider: Any = None) -> None:
        self._llm = llm_provider

    def interpret(self, user_message: str, context: str = "") -> TaskPlan:
        """Interpret a user message and produce a TaskPlan."""
        if not self._llm:
            return self._fallback_plan(user_message)

        prompt = user_message
        if context:
            prompt = f"Context: {context}\n\nUser message: {user_message}"

        try:
            result = self._llm.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                max_tokens=1000,
                temperature=0.1,
            )

            if not result.success:
                logger.error("LLM interpretation failed: %s", result.error)
                return self._fallback_plan(user_message)

            return self._parse_response(result.content, user_message)

        except Exception as e:
            logger.error("LLM interpretation error: %s", e)
            return self._fallback_plan(user_message)

    def _parse_response(self, llm_output: str, user_message: str) -> TaskPlan:
        """Parse LLM JSON response into TaskPlan."""
        # Try to extract JSON from response
        text = llm_output.strip()

        # Remove markdown fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            text = text.strip()
            if text.endswith("```"):
                text = text[:-3].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON, using fallback")
            return self._fallback_plan(user_message)

        plan = TaskPlan(
            goal=data.get("goal", user_message),
            task_type=TaskType[data.get("task_type", "CONVERSATION")],
            needs_browser=data.get("needs_browser", False),
            needs_device=data.get("needs_device", False),
            approval_required=data.get("approval_required", False),
            risk_summary=data.get("risk_summary", ""),
            constraints=data.get("constraints", []),
            response_text=data.get("response_text", ""),
            raw_llm_response=llm_output,
        )

        for action_data in data.get("actions", []):
            action = TaskAction(
                action_type=action_data.get("action_type", ""),
                description=action_data.get("description", ""),
                params=action_data.get("params", {}),
                risk_level=RiskLevel[action_data.get("risk_level", "READ")],
                capability_id=action_data.get("capability_id", ""),
            )
            # Mark approval if risk is high
            if action.risk_level in (RiskLevel.EXTERNAL_SEND, RiskLevel.PAYMENT):
                action.requires_approval = True
            plan.actions.append(action)

        # Validate safety
        self._validate_safety(plan)

        return plan

    def _validate_safety(self, plan: TaskPlan) -> None:
        """Validate that the plan doesn't violate safety rules."""
        blocked_patterns = ["captcha", "bypass", "stealth", "proxy", "purchase"]

        for action in plan.actions:
            action_lower = action.description.lower() + " " + action.action_type.lower()
            for pattern in blocked_patterns:
                if pattern in action_lower:
                    action.risk_level = RiskLevel.BLOCKED
                    action.requires_approval = True
                    logger.warning("Blocked action detected: %s", action.description)

    def _fallback_plan(self, user_message: str) -> TaskPlan:
        """Create a fallback plan when LLM is not available."""
        return TaskPlan(
            goal=user_message,
            task_type=TaskType.CONVERSATION,
            response_text="I need an LLM provider to understand your request. Please configure OPENAI_API_KEY.",
        )
