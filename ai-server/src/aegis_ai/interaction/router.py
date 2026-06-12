"""Interaction Router — Beta version with LLM Task Interpreter.

Routes user messages through LLM Task Interpreter.
The LLM understands natural language and produces structured TaskPlans
that are validated by Planner and executed through ToolBroker.

Architecture: docs/beta-architecture.md
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from aegis_ai.interaction.message import Message, Response
from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
from aegis_ai.task_plan import RiskCategory, StepStatus, TaskPlan

logger = logging.getLogger("aegis_ai.interaction.router")


class InteractionRouter:
    """Routes user messages using LLM Task Interpreter.

    Flow:
    1. User message → LLM Task Interpreter → TaskPlan
    2. TaskPlan → Planner validation → PolicyEngine check
    3. Steps → ToolBroker execution (or Approval UI)
    4. Results → Response to user

    Usage:
        router = InteractionRouter(
            llm_provider=llm,
            context_builder=ctx,
            tool_broker=broker,
            approval_store=approvals,
        )
        response = router.route(message)
    """

    def __init__(
        self,
        llm_provider: Any = None,
        context_builder: Any = None,
        capability_registry: Any = None,
        tool_broker: Any = None,
        approval_store: Any = None,
        audit_log: Any = None,
        browser_executor: Any = None,
        research_agent: Any = None,
        support_agent: Any = None,
        self_dev_agent: Any = None,
        settings_store: Any = None,
    ) -> None:
        self._llm = llm_provider
        self._context = context_builder
        self._registry = capability_registry
        self._broker = tool_broker
        self._approval = approval_store
        self._audit = audit_log
        self._browser = browser_executor
        self._research = research_agent
        self._support = support_agent
        self._self_dev = self_dev_agent
        self._settings = settings_store

        # Lazy-init interpreter
        self._interpreter: LLMTaskInterpreter | None = None

    def _get_interpreter(self) -> LLMTaskInterpreter:
        """Get or create LLM Task Interpreter."""
        if self._interpreter is None:
            self._interpreter = LLMTaskInterpreter(
                llm_provider=self._llm,
                context_builder=self._context,
                capability_registry=self._registry,
            )
        return self._interpreter

    def route(self, message: Message) -> Response:
        """Route a user message through LLM Task Interpreter."""
        now_ms = int(time.time() * 1000)

        response = Response(
            response_id=f"resp_{uuid.uuid4().hex[:8]}",
            message_id=message.message_id,
            channel=message.channel,
            timestamp_ms=now_ms,
        )

        try:
            text_lower = message.text.lower().strip()

            # Handle system commands directly (no LLM needed)
            if any(kw in text_lower for kw in ["status", "health", "what's happening"]):
                return self._handle_status(response)
            elif any(kw in text_lower for kw in ["help", "what can you do", "how to"]):
                return self._handle_help(response)
            elif any(kw in text_lower for kw in ["settings", "config"]):
                return self._handle_settings(response)
            elif any(kw in text_lower for kw in ["approve", "reject", "pending"]):
                return self._handle_approval(message, response)
            elif any(kw in text_lower for kw in ["accept", "feedback", "thanks"]):
                return self._handle_support_feedback(message, response)
            else:
                # Main path: LLM Task Interpreter
                return self._handle_llm_interpreted(message, response)

        except Exception as e:
            logger.error("Interaction routing failed: %s", e)
            response.text = f"Sorry, something went wrong: {e}"

        # Audit
        if self._audit:
            self._audit.log_decision(
                "interaction", "route", "HANDLED",
                detail={"channel": message.channel.name, "text": message.text[:100]},
            )

        return response

    def _handle_llm_interpreted(self, message: Message, response: Response) -> Response:
        """Main handler: LLM interprets → TaskPlan → execute."""
        interpreter = self._get_interpreter()
        plan = interpreter.interpret(message.text)

        # Execute the plan
        return self._execute_plan(plan, response)

    def _execute_plan(self, plan: TaskPlan, response: Response) -> Response:
        """Execute a TaskPlan."""
        # Check if LLM failed
        if not plan.steps and not plan.interpreted_request:
            response.text = plan.expected_result or "I need an LLM provider to understand your request."
            return response

        # Check for blocked steps
        if plan.has_blocked_steps():
            blocked = [s for s in plan.steps if s.risk_category == RiskCategory.BLOCKED]
            reasons = [s.description for s in blocked]
            response.text = f"Some actions are blocked: {', '.join(reasons)}"
            return response

        # Check if approval needed
        if plan.has_approval_required_steps():
            approval_steps = [s for s in plan.steps if s.requires_approval]
            if self._approval:
                # Send to approval UI
                for step in approval_steps:
                    step.status = StepStatus.NEEDS_APPROVAL
                response.text = (
                    f"This requires approval for: {', '.join(s.description for s in approval_steps)}\n"
                    f"Approval UI: http://127.0.0.1:8080/approvals"
                )
                response.pending_approvals = [
                    {"step_id": s.step_id, "description": s.description}
                    for s in approval_steps
                ]
            else:
                response.text = "Approval required but approval system not available."
            return response

        # Execute steps
        results = []
        for step in plan.steps:
            if step.status != StepStatus.PENDING:
                continue

            # Check dependencies
            if step.depends_on:
                deps_met = all(
                    any(s.step_id == dep and s.status == StepStatus.COMPLETED for s in plan.steps)
                    for dep in step.depends_on
                )
                if not deps_met:
                    continue

            # Execute step
            step_result = self._execute_step(step, plan)
            results.append(step_result)

        # Build response
        if results:
            response.text = "\n".join(results)
        else:
            response.text = plan.expected_result or "No actions to execute."

        return response

    def _execute_step(self, step: Any, plan: TaskPlan) -> str:
        """Execute a single plan step."""
        # Browser operations
        if step.action_type.startswith("browser_"):
            return self._execute_browser_step(step)

        # Tool invocation
        if step.action_type == "tool_invoke" and step.capability_id:
            return self._execute_tool_step(step)

        # LLM operations (summarize, analyze, etc.)
        if step.action_type.startswith("llm_"):
            return self._execute_llm_step(step, plan)

        return f"[INFO] {step.description}"

    def _execute_browser_step(self, step: Any) -> str:
        """Execute a browser step."""
        if self._browser:
            try:
                task = step.description
                if step.params.get("url"):
                    task = f"Go to {step.params['url']} and {step.description}"

                result = self._browser.execute(task)
                if result.success:
                    step.status = StepStatus.COMPLETED
                    step.result = result.result_text
                    return result.result_text
                else:
                    step.status = StepStatus.FAILED
                    step.error = result.error
                    return f"[FAIL] {step.description}: {result.error}"
            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                return f"[ERROR] {step.description}: {e}"
        else:
            return self._execute_browser_fallback(step)

    def _execute_browser_fallback(self, step: Any) -> str:
        """Fallback browser execution using direct playwright."""
        import re

        url = step.params.get("url", "")
        if not url:
            url_match = re.search(r'https?://[^\s]+', step.description)
            url = url_match.group(0) if url_match else ""

        if not url:
            return f"[INFO] {step.description} (no URL found)"

        try:
            import asyncio
            from playwright.async_api import async_playwright

            async def browse():
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(url, timeout=30000)
                    title = await page.title()
                    text = await page.evaluate("document.body.innerText")
                    await browser.close()
                    return title, text[:2000]

            title, content = asyncio.run(browse())
            step.status = StepStatus.COMPLETED
            return f"**{title}**\n\n{content}"

        except Exception as e:
            step.status = StepStatus.FAILED
            return f"[ERROR] Browser: {e}"

    def _execute_tool_step(self, step: Any) -> str:
        """Execute a tool invocation step via ToolBroker."""
        if not self._broker:
            return f"[INFO] {step.description} (ToolBroker not available)"

        try:
            result = self._broker.invoke_tool(step.capability_id, step.params)
            if result.success:
                step.status = StepStatus.COMPLETED
                step.result = result.output
                return f"[OK] {step.description}"
            elif result.status.name == "APPROVAL_NEEDED":
                step.status = StepStatus.NEEDS_APPROVAL
                return f"[APPROVAL] {step.description} — needs approval"
            else:
                step.status = StepStatus.FAILED
                step.error = result.error
                return f"[FAIL] {step.description}: {result.error}"
        except Exception as e:
            step.status = StepStatus.FAILED
            return f"[ERROR] {step.description}: {e}"

    def _execute_llm_step(self, step: Any, plan: TaskPlan) -> str:
        """Execute an LLM-based step (summarize, analyze, etc.)."""
        if not self._llm:
            return f"[INFO] {step.description} (LLM not available)"

        try:
            # Build prompt from step description and context
            prompt = step.description
            if step.params.get("content"):
                prompt = f"{step.description}\n\nContent:\n{step.params['content']}"

            result = self._llm.generate(
                prompt=prompt,
                system_prompt="You are AEGIS. Perform the requested analysis concisely.",
                max_tokens=1000,
            )

            if result.success:
                step.status = StepStatus.COMPLETED
                step.result = result.content
                return result.content
            else:
                step.status = StepStatus.FAILED
                return f"[FAIL] {step.description}: {result.error}"

        except Exception as e:
            step.status = StepStatus.FAILED
            return f"[ERROR] {step.description}: {e}"

    def _handle_status(self, response: Response) -> Response:
        """Handle status check."""
        response.text = (
            "AEGIS is running. Use the Dashboard for detailed status:\n"
            "http://127.0.0.1:8090"
        )
        return response

    def _handle_help(self, response: Response) -> Response:
        """Handle help request."""
        response.text = (
            "I'm AEGIS, your autonomous AI assistant. I can:\n"
            "- Research topics and browse the web\n"
            "- Read and summarize your messages (SNS, email)\n"
            "- Create drafts for posts and replies\n"
            "- Control your PC, Android, and room devices\n\n"
            "Just tell me what you need in natural language!"
        )
        return response

    def _handle_settings(self, response: Response) -> Response:
        """Handle settings request."""
        if self._settings:
            settings = self._settings.get()
            response.text = (
                f"Settings:\n"
                f"- Dashboard: http://127.0.0.1:8090"
            )
        else:
            response.text = "Settings not available."
        return response

    def _handle_approval(self, message: Message, response: Response) -> Response:
        """Handle approval request."""
        if self._approval:
            pending = self._approval.get_pending()
            if pending:
                response.text = f"You have {len(pending)} pending approval(s).\nApproval UI: http://127.0.0.1:8080/approvals"
            else:
                response.text = "No pending approvals."
        else:
            response.text = "Approval system not available."
        return response

    def _handle_support_feedback(self, message: Message, response: Response) -> Response:
        """Handle support feedback."""
        text_lower = message.text.lower()
        if any(w in text_lower for w in ["accept", "yes", "ok", "thanks"]):
            response.text = "Thank you for the feedback!"
        elif any(w in text_lower for w in ["reject", "no"]):
            response.text = "Understood. I'll adjust."
        else:
            response.text = "Could you clarify your feedback?"
        return response
