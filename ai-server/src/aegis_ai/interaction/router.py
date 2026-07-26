# -*- coding: utf-8 -*-
'''Interaction Router - LLM Task Interpreter + TaskExecutionEngine.

Routes user messages through LLM Task Interpreter.
All step execution is delegated to TaskExecutionEngine.
'''

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from aegis_ai.interaction.message import Message, Response
from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
from aegis_ai.task_plan import RiskCategory, TaskPlan

logger = logging.getLogger("aegis_ai.interaction.router")


class InteractionRouter:
    '''Routes user messages using LLM Task Interpreter.

    Responsibilities (thin router):
    1. LLM interprets user message -> TaskPlan
    2. Task creation via TaskManager
    3. Delegation to TaskExecutionEngine for step execution
    4. Response formatting

    Does NOT execute steps directly.
    '''

    def __init__(
        self,
        llm_provider: Any = None,
        context_builder: Any = None,
        capability_registry: Any = None,
        capability_catalog: Any = None,
        capability_retriever: Any = None,
        tool_broker: Any = None,
        approval_store: Any = None,
        audit_log: Any = None,
        browser_executor: Any = None,
        research_agent: Any = None,
        support_agent: Any = None,
        self_dev_agent: Any = None,
        settings_store: Any = None,
        task_manager: Any = None,
        execution_engine: Any = None,
    ) -> None:
        self._llm = llm_provider
        self._context = context_builder
        self._registry = capability_registry
        self._catalog = capability_catalog
        self._retriever = capability_retriever
        self._broker = tool_broker
        self._approval = approval_store
        self._audit = audit_log
        self._browser = browser_executor
        self._research = research_agent
        self._support = support_agent
        self._self_dev = self_dev_agent
        self._settings = settings_store
        self._task_manager = task_manager
        self._execution_engine = execution_engine
        self._interpreter: LLMTaskInterpreter | None = None

    def _get_interpreter(self) -> LLMTaskInterpreter:
        if self._interpreter is None:
            self._interpreter = LLMTaskInterpreter(
                llm_provider=self._llm,
                context_builder=self._context,
                capability_registry=self._registry,
                capability_catalog=self._catalog,
                capability_retriever=self._retriever,
            )
        return self._interpreter

    def route(self, message: Message) -> Response:
        now_ms = int(time.time() * 1000)
        response = Response(
            response_id=f'resp_{uuid.uuid4().hex[:8]}',
            message_id=message.message_id,
            channel=message.channel,
            timestamp_ms=now_ms,
        )
        try:
            return self._handle_llm_interpreted(message, response)
        except Exception as e:
            logger.error("Interaction routing failed: %s", e)
            response.text = f'Sorry, something went wrong: {e}'
        if self._audit:
            self._audit.log_decision(
                "interaction", "route", "HANDLED",
                detail={"channel": message.channel.name, "text": message.text[:100]},
            )
        return response

    def _handle_llm_interpreted(self, message: Message, response: Response) -> Response:
        interpreter = self._get_interpreter()
        plan = interpreter.interpret(message.text)
        return self._execute_plan(plan, response)

    def _execute_plan(self, plan: TaskPlan, response: Response) -> Response:
        task_id = None
        try:
            if self._task_manager:
                task = self._task_manager.create_task(
                    title=f'Router: {plan.interpreted_request[:50]}',
                    source="router",
                    goal=plan.interpreted_request,
                    goal_graph=plan.goal_graph.to_dict() if plan.goal_graph else None,
                )
                task_id = task["task_id"]
                self._task_manager.start_task(task_id)
            if not plan.steps and not plan.interpreted_request:
                response.text = plan.expected_result or "I need an LLM provider to understand your request."
                if task_id:
                    self._task_manager.fail_task(task_id, error="LLM provider not available")
                return response
            if plan.has_blocked_steps():
                blocked = [s for s in plan.steps if s.risk_category == RiskCategory.BLOCKED]
                reasons = [s.description for s in blocked]
                response.text = "Some actions are blocked: " + ", ".join(reasons)
                if task_id:
                    self._task_manager.fail_task(task_id, error="Blocked: " + ", ".join(reasons))
                return response
            if not self._execution_engine:
                response.text = "Execution engine not available."
                if task_id:
                    self._task_manager.fail_task(task_id, error="Execution engine not available")
                return response
            exec_response = self._execution_engine.execute_task(task_id, plan)
            response.text = exec_response.text
            return response
        except Exception as e:
            logger.error("Plan execution failed: %s", e)
            response.text = f'Sorry, plan execution failed: {e}'
            if task_id:
                self._task_manager.fail_task(task_id, error=str(e))
            return response

    def _handle_status(self, response: Response) -> Response:
        response.text = "AEGIS is running. Use the Dashboard for detailed status:\nhttp://0.0.0.0:8090"
        return response

    def _handle_help(self, response: Response) -> Response:
        response.text = (
            "I am AEGIS, your autonomous AI assistant. I can:\n"
            "- Research topics and browse the web\n"
            "- Read and summarize your messages (SNS, email)\n"
            "- Create drafts for posts and replies\n"
            "- Control your PC, Android, and room devices\n\n"
            "Just tell me what you need in natural language!"
        )
        return response

    def _handle_settings(self, response: Response) -> Response:
        if self._settings:
            response.text = "Settings:\n- Dashboard: http://0.0.0.0:8090"
        else:
            response.text = "Settings not available."
        return response

    def _handle_approval(self, message: Message, response: Response) -> Response:
        if self._approval:
            pending = self._approval.get_pending()
            if pending:
                response.text = f"You have {len(pending)} pending approval(s).\nApproval UI: http://0.0.0.0:8080/approvals"
            else:
                response.text = "No pending approvals."
        else:
            response.text = "Approval system not available."
        return response

    def _handle_support_feedback(self, message: Message, response: Response) -> Response:
        text_lower = message.text.lower()
        if any(w in text_lower for w in ["accept", "yes", "ok", "thanks"]):
            response.text = "Thank you for the feedback!"
        elif any(w in text_lower for w in ["reject", "no"]):
            response.text = "Understood. I will adjust."
        else:
            response.text = "Could you clarify your feedback?"
        return response
