"""LLM Task Interpreter — interprets user natural language into TaskPlans.

This is the core of Beta's natural language execution.
Instead of keyword matching, the LLM understands user intent and produces
structured TaskPlans that are validated and executed.

Architecture: docs/beta-architecture.md
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

from aegis_ai.task_plan import PlanStep, RiskCategory, StepStatus, TaskPlan

logger = logging.getLogger("aegis_ai.llm_task_interpreter")


INTERPRETATION_PROMPT = """You are AEGIS's task interpreter. Analyze the user's message and produce a structured task plan.

## Available Context
{context}

## Available Capabilities
{capabilities}

## User Message
{user_message}

## Output Format (JSON)
{{
  "user_goal": "What the user wants to accomplish",
  "interpreted_request": "Clear description of what to do",
  "assumptions": ["List of assumptions made"],
  "required_context": ["What context is needed"],
  "steps": [
    {{
      "step_id": "step_1",
      "description": "What this step does",
      "action_type": "browser_open|browser_read|browser_navigate|tool_invoke|llm_analyze|llm_summarize",
      "capability_id": "browser.open_page|browser.read_owned_account_page|...",
      "params": {{"url": "...", "query": "..."}},
      "risk_category": "READ|DRAFT|OBSERVE|EXTERNAL_SEND|DEVICE_ACTION|PAYMENT|BLOCKED",
      "requires_approval": false,
      "expected_result": "What should happen",
      "depends_on": []
    }}
  ],
  "required_capabilities": ["List of capability IDs needed"],
  "risk_notes": ["Any risk considerations"],
  "approval_needed": false,
  "stop_conditions": ["When to stop"],
  "expected_result": "Overall expected outcome",
  "verification_plan": "How to verify success",
  "needs_browser": true,
  "needs_device": false
}}

## Safety Rules
- READ operations (web pages, owned accounts, notifications) → allowed, no approval
- DRAFT operations (create drafts, write locally) → allowed, no approval  
- OBSERVE operations (screenshot, window list) → allowed, no approval
- EXTERNAL_SEND (post, DM, email, publish) → requires approval
- DEVICE_ACTION (mouse, keyboard, physical control) → requires approval
- PAYMENT (purchase, subscribe) → blocked or requires approval
- CAPTCHA bypass, bot evasion, stealth → BLOCKED
- Spam, bulk operations → BLOCKED

## Important
- Reading user-owned accounts (SNS, email, notifications) is READ, not EXTERNAL_SEND
- Creating drafts (not sending) is DRAFT
- If uncertain about risk, use the safer category
- If capability doesn't exist, note it in assumptions
- Respond with ONLY the JSON, no markdown fences"""


class LLMTaskInterpreter:
    """Interprets user natural language into structured TaskPlans.

    Usage:
        interpreter = LLMTaskInterpreter(llm_provider=llm, context_builder=ctx)
        plan = interpreter.interpret("Check my Twitter notifications and summarize")
    """

    def __init__(
        self,
        llm_provider: Any = None,
        context_builder: Any = None,
        capability_registry: Any = None,
    ) -> None:
        self._llm = llm_provider
        self._context = context_builder
        self._registry = capability_registry

    def interpret(self, user_message: str, context_str: str = "") -> TaskPlan:
        """Interpret user message into a TaskPlan."""
        if not self._llm:
            return self._fallback_plan(user_message)

        # Build context
        ctx = context_str or self._build_context()
        caps = self._build_capability_list()

        # Format prompt
        prompt = INTERPRETATION_PROMPT.format(
            context=ctx,
            capabilities=caps,
            user_message=user_message,
        )

        # Call LLM with retry
        for attempt in range(2):
            try:
                result = self._llm.generate(
                    prompt=prompt,
                    system_prompt="You are a task interpreter. Output only valid JSON.",
                    max_tokens=2000,
                    temperature=0.1,
                )

                if not result.success:
                    logger.warning("LLM interpretation failed (attempt %d): %s", attempt + 1, result.error)
                    continue

                plan = self._parse_response(result.content, user_message)
                if plan:
                    # Validate safety
                    self._validate_safety(plan)
                    return plan

            except Exception as e:
                logger.warning("LLM interpretation error (attempt %d): %s", attempt + 1, e)

        # All attempts failed - use fallback
        return self._fallback_plan(user_message)

    def _parse_response(self, llm_output: str, user_message: str) -> TaskPlan | None:
        """Parse LLM JSON response into TaskPlan."""
        text = llm_output.strip()

        # Remove markdown fences
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:] if lines[0].startswith("```") else lines)
            if text.endswith("```"):
                text = text[:-3].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON")
            return None

        plan = TaskPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            user_goal=data.get("user_goal", user_message),
            interpreted_request=data.get("interpreted_request", ""),
            assumptions=data.get("assumptions", []),
            required_context=data.get("required_context", []),
            risk_notes=data.get("risk_notes", []),
            approval_needed=data.get("approval_needed", False),
            stop_conditions=data.get("stop_conditions", []),
            expected_result=data.get("expected_result", ""),
            verification_plan=data.get("verification_plan", ""),
            needs_browser=data.get("needs_browser", False),
            needs_device=data.get("needs_device", False),
            required_capabilities=data.get("required_capabilities", []),
            raw_llm_response=llm_output,
        )

        # Parse steps
        for step_data in data.get("steps", []):
            step = PlanStep(
                step_id=step_data.get("step_id", f"step_{len(plan.steps) + 1}"),
                description=step_data.get("description", ""),
                action_type=step_data.get("action_type", ""),
                capability_id=step_data.get("capability_id", ""),
                params=step_data.get("params", {}),
                risk_category=self._parse_risk(step_data.get("risk_category", "READ")),
                requires_approval=step_data.get("requires_approval", False),
                expected_result=step_data.get("expected_result", ""),
                depends_on=step_data.get("depends_on", []),
            )
            plan.steps.append(step)

        return plan

    def _parse_risk(self, risk_str: str) -> RiskCategory:
        """Parse risk category string."""
        try:
            return RiskCategory[risk_str.upper()]
        except KeyError:
            return RiskCategory.READ

    def _validate_safety(self, plan: TaskPlan) -> None:
        """Validate and adjust safety classifications."""
        blocked_patterns = ["captcha", "bypass", "stealth", "proxy", "purchase", "pay"]

        for step in plan.steps:
            check_text = f"{step.description} {step.action_type} {step.capability_id}".lower()

            # Check for blocked patterns
            for pattern in blocked_patterns:
                if pattern in check_text:
                    step.risk_category = RiskCategory.BLOCKED
                    step.requires_approval = True
                    plan.risk_notes.append(f"Blocked: {pattern} detected in step {step.step_id}")
                    break

            # External send always needs approval
            if step.risk_category == RiskCategory.EXTERNAL_SEND:
                step.requires_approval = True
                plan.approval_needed = True

            # Device action always needs approval
            if step.risk_category == RiskCategory.DEVICE_ACTION:
                step.requires_approval = True
                plan.approval_needed = True

            # Payment is blocked
            if step.risk_category == RiskCategory.PAYMENT:
                step.risk_category = RiskCategory.BLOCKED
                step.requires_approval = True

    def _build_context(self) -> str:
        """Build context string from ContextBuilder."""
        if not self._context:
            return "No context available"

        try:
            ctx = self._context.build()
            parts = []
            if ctx.identity:
                parts.append(f"Identity: {ctx.identity}")
            if ctx.current_goals:
                parts.append(f"Goals: {', '.join(ctx.current_goals[:3])}")
            if ctx.recent_events:
                parts.append(f"Recent events: {len(ctx.recent_events)} events")
            return "\n".join(parts) if parts else "Context available but empty"
        except Exception:
            return "Context unavailable"

    def _build_capability_list(self) -> str:
        """Build capability list from registry."""
        if not self._registry:
            return "No capability registry available"

        try:
            caps = self._registry.list_all()
            lines = []
            for cap in caps[:30]:
                lines.append(f"- {cap.id}: {cap.name} (risk: {cap.risk_level.name})")
            return "\n".join(lines) if lines else "No capabilities registered"
        except Exception:
            return "Capabilities unavailable"

    def _fallback_plan(self, user_message: str) -> TaskPlan:
        """Create fallback plan when LLM is not available."""
        return TaskPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            user_goal=user_message,
            interpreted_request="LLM not available for interpretation",
            assumptions=["LLM provider not configured"],
            risk_notes=["Cannot assess risk without LLM"],
            expected_result="Need LLM provider to process this request",
            raw_llm_response="",
        )
