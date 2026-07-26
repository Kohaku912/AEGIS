"""LLM Task Interpreter — interprets user natural language into TaskPlans.

This is the core of Beta's natural language execution.
Instead of keyword matching, the LLM understands user intent and produces
structured TaskPlans that are validated and executed.

Architecture: docs/beta-architecture.md
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any

from aegis_ai.agency.goal_graph import (
    GoalGraph,
    GoalOutcome,
    GoalVerification,
)
from aegis_ai.llm.json_utils import extract_json_object
from aegis_ai.llm.memory_context import build_shared_memory_context
from aegis_ai.task_plan import PlanStep, RiskCategory, TaskPlan

logger = logging.getLogger("aegis_ai.llm_task_interpreter")
_DATA_DIR = str(Path(__file__).resolve().parent.parent.parent / "data")


INTERPRETATION_PROMPT = """You are AEGIS's task interpreter.
Analyze the user's message and produce a structured task plan.

## Available Context
{context}

## Available Capabilities
{capabilities}

## User Message
{user_message}

## Output Format (JSON)
{{{{
  "user_goal": "What the user wants to accomplish",
  "outcome": {{{{
    "description": "Observable user-facing outcome",
    "success_condition": "Condition that proves the goal is achieved",
    "value_to_user": "Why this outcome matters"
  }}}},
  "obligation_ids": ["Commitment, incident, or social obligation IDs from context"],
  "interpreted_request": "Clear description of what to do",
  "assumptions": ["List of assumptions made"],
  "required_context": ["What context is needed"],
  "steps": [
    {{{{
      "step_id": "step_1",
      "description": "What this step does",
      "action_type": "browser_open|browser_read|tool_invoke|llm_analyze|llm_summarize",
      "capability_id": "Use one canonical ID from Available Capabilities",
      "params": {{{{}}}},
      "risk_category": "READ|DRAFT|OBSERVE|EXTERNAL_SEND|DEVICE_ACTION|PAYMENT|BLOCKED",
      "requires_approval": false,
      "expected_result": "What should happen",
      "depends_on": [],
      "delegation_context": {{{{
        "operation_category": "general|external_send|social_communication|payment|physical_device|system_change",
        "scope": "aegis|user|system|external",
        "audience": "private|shared|public|third_party",
        "content_sensitivity": "normal|personal|confidential|secret",
        "reversibility": "reversible|difficult|irreversible"
      }}}}
    }}}}
  ],
  "required_capabilities": ["List of capability IDs needed"],
  "risk_notes": ["Any risk considerations"],
  "approval_needed": false,
  "stop_conditions": ["When to stop"],
  "expected_result": "Overall expected outcome",
  "verification_plan": "How to verify success",
  "verification": [
    {{{{
      "verification_id": "verify_1",
      "criterion": "Observable completion criterion",
      "linked_step_ids": ["step_1"]
    }}}}
  ],
  "presentation": {{{{
    "report_when": "terminal",
    "audience": "user"
  }}}},
  "needs_browser": true,
  "needs_device": false
}}}}

## Safety Rules
- READ operations (web pages, owned accounts, notifications) -> allowed, no approval
- DRAFT operations (create drafts, write locally) -> allowed, no approval
- OBSERVE operations (screenshot, window list) -> allowed, no approval
- EXTERNAL_SEND (post, DM, email, publish) -> requires approval
- DEVICE_ACTION (mouse, keyboard, physical control) -> requires approval
- PAYMENT (purchase, subscribe) -> requires explicit approval
- CAPTCHA bypass, bot evasion, stealth -> BLOCKED
- Spam, bulk operations -> BLOCKED

## Important
- Reading user-owned accounts (SNS, email, notifications) is READ, not EXTERNAL_SEND
- Creating drafts (not sending) is DRAFT
- If uncertain about risk, use the safer category
- Browser steps must use a purpose-specific canonical browser-server capability.
- Browser arguments must declare viewer, purpose, success_condition, and stop_condition.
- Use pc-server.app.show_url only for a declared user-visible handoff, never for agent-private research.
- If capability doesn't exist, note it in assumptions
- Respond with ONLY the JSON, no markdown fences"""


class LLMTaskInterpreter:
    """Interprets user natural language into structured TaskPlans.

    Usage:
        interpreter = LLMTaskInterpreter(llm_provider=llm, context_builder=ctx, capability_catalog=catalog)
        plan = interpreter.interpret("Check my Twitter notifications and summarize")
    """

    def __init__(
        self,
        llm_provider: Any = None,
        context_builder: Any = None,
        capability_registry: Any = None,
        capability_catalog: Any = None,
        capability_retriever: Any = None,
    ) -> None:
        self._llm = llm_provider
        self._context = context_builder
        self._catalog = capability_catalog
        self._retriever = capability_retriever
        self._registry = capability_registry

    def interpret(self, user_message: str, context_str: str = "") -> TaskPlan:
        """Interpret user message into a TaskPlan."""
        if not self._llm:
            return self._fallback_plan(user_message)

        # Build context
        shared_context = build_shared_memory_context(
            query=user_message,
            data_dir=_DATA_DIR,
            profile="decision",
        )
        ctx = context_str or self._build_context()
        if shared_context.text:
            ctx = f"{shared_context.text}\n\n{ctx}" if ctx else shared_context.text
        caps = self._build_capability_list(user_message)

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
                    context_meta=shared_context.audit_detail(),
                    json_mode=True,
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
        try:
            data = extract_json_object(llm_output)
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
                delegation_context={
                    str(key): str(value)
                    for key, value in dict(
                        step_data.get("delegation_context") or {}
                    ).items()
                },
            )
            plan.steps.append(step)

        outcome_data = dict(data.get("outcome") or {})
        verification_data = list(data.get("verification") or [])
        if not verification_data and plan.steps:
            verification_data = [
                {
                    "verification_id": "verify_outcome",
                    "criterion": plan.verification_plan or plan.expected_result,
                    "linked_step_ids": [step.step_id for step in plan.steps],
                }
            ]
        plan.goal_graph = GoalGraph(
            goal_id=f"goal_{plan.plan_id}",
            outcome=GoalOutcome(
                description=str(outcome_data.get("description") or plan.expected_result or plan.user_goal),
                success_condition=str(
                    outcome_data.get("success_condition") or plan.verification_plan or plan.expected_result
                ),
                value_to_user=str(outcome_data.get("value_to_user") or ""),
            ),
            source="user",
            obligation_ids=[str(item) for item in data.get("obligation_ids", [])],
            verification=[GoalVerification.from_dict(item) for item in verification_data if isinstance(item, dict)],
            presentation=dict(data.get("presentation") or {"report_when": "terminal", "audience": "user"}),
            stop_conditions=list(plan.stop_conditions),
        )
        return plan

    def _parse_risk(self, risk_str: str) -> RiskCategory:
        """Parse risk category string."""
        try:
            return RiskCategory[risk_str.upper()]
        except KeyError:
            return RiskCategory.READ

    def _validate_safety(self, plan: TaskPlan) -> None:
        """Validate the LLM plan against manifest-backed capability policy."""
        for step in plan.steps:
            capability = self._catalog.resolve(step.capability_id) if self._catalog and step.capability_id else None
            if capability is not None:
                risk = str(getattr(capability, "risk_level", "low")).lower()
                requires_approval = bool(getattr(capability, "requires_approval", False))
                enabled = bool(getattr(capability, "enabled", True))
                if not enabled or risk in {"forbidden", "blocked"}:
                    step.risk_category = RiskCategory.BLOCKED
                    step.requires_approval = True
                    plan.risk_notes.append(f"Policy blocks {step.capability_id}")
                elif requires_approval or risk in {"approval_required", "high", "critical"}:
                    step.requires_approval = True
                    plan.approval_needed = True

            delegation = dict(step.delegation_context or {})
            if (
                str(delegation.get("scope") or "") in {"user", "system", "external"}
                or str(delegation.get("audience") or "") in {
                    "shared",
                    "public",
                    "third_party",
                }
                or str(delegation.get("content_sensitivity") or "")
                in {"personal", "confidential", "secret"}
                or str(delegation.get("reversibility") or "")
                in {"difficult", "irreversible"}
            ):
                step.requires_approval = True
                plan.approval_needed = True

            # External send always needs approval
            if step.risk_category == RiskCategory.EXTERNAL_SEND:
                step.requires_approval = True
                plan.approval_needed = True

            # Device action always needs approval
            if step.risk_category == RiskCategory.DEVICE_ACTION:
                step.requires_approval = True
                plan.approval_needed = True

            # Payment always requires explicit approval; it is not a permanent deny.
            if step.risk_category == RiskCategory.PAYMENT:
                step.requires_approval = True
                plan.approval_needed = True

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
            if ctx.recent_media_summaries:
                parts.append("Recent media: " + "; ".join(ctx.recent_media_summaries[:2]))
            if ctx.decision_context:
                obligations = ctx.decision_context.get("obligations", [])
                parts.append("Shared AgentState obligations: " + json.dumps(obligations[:12], ensure_ascii=False))
            return "\n".join(parts) if parts else "Context available but empty"
        except Exception:
            return "Context unavailable"

    def _build_capability_list(self, user_message: str = "") -> str:
        if self._retriever is not None:
            try:
                selection = self._retriever.select_for_request(
                    user_message,
                    {},
                    top_k_schema=8,
                    top_k_summary=50,
                )
                lines = [
                    "Full schema candidates:",
                ]
                for tool in selection.retrieved_schema_tools:
                    fn = tool.get("function", {})
                    cap_id = fn.get("name", "").replace("__", ".")
                    params = ", ".join(fn.get("parameters", {}).get("properties", {}).keys())
                    lines.append(f"- {cap_id}: {fn.get('description', '')}")
                    if params:
                        lines.append(f"  params: {params}")
                lines.append("")
                lines.append("Lightweight catalog:")
                for item in selection.lightweight_catalog:
                    tags = ", ".join(item.get("tags", []))
                    lines.append(
                        f"- {item.get('id', '')}: {item.get('title', '')} "
                        f"(risk: {item.get('risk', '')}, tags: {tags}) - {item.get('short_desc', '')}"
                    )
                return "\n".join(lines) if len(lines) > 3 else "No capabilities registered"
            except Exception:
                logger.debug("Capability retriever failed in task interpreter", exc_info=True)

        if self._catalog is not None:
            try:
                caps = self._catalog.list_for_llm()
                lines = []
                for cap in caps[:30]:
                    params_str = ", ".join(cap.get("params", []))
                    required_str = ", ".join(cap.get("required_params", []))
                    title = cap.get("title", "")
                    desc = cap.get("description", "")
                    line = f"- {cap['id']}: {title} — {desc}"
                    if params_str:
                        line += f"\n  params: {params_str}"
                    if required_str:
                        line += f"\n  required: {required_str}"
                    lines.append(line)
                return "\n".join(lines) if lines else "No capabilities registered"
            except Exception:
                pass

        if self._registry is not None:
            try:
                caps = self._registry.list_all()
                lines = []
                for cap in caps[:30]:
                    lines.append(f"- {cap.id}: {cap.name} (risk: {cap.risk_level.name})")
                return "\n".join(lines) if lines else "No capabilities registered"
            except Exception:
                pass

        return "No capability registry available"

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
