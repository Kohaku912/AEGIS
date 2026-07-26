"""Shared chat execution helpers for dashboard and mobile clients."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from aegis_ai.web.chat_tools import call_llm_with_tools
from aegis_ai.web.dashboard_routes import _build_chat_system_prompt, _call_llm_with_runtime

logger = logging.getLogger("aegis_ai.web.chat_service")


def execute_chat_message(
    runtime: Any,
    text: str,
    *,
    origin_channel: str,
    conversation_id: str = "",
    device_id: str = "",
    context: dict[str, str] | None = None,
    task_source: str = "chat",
) -> dict[str, Any]:
    """Execute one chat turn through the same tool loop used by dashboard chat."""
    clean_text = text.strip()
    if not clean_text:
        return {
            "response": "No text provided",
            "tool_results": [],
            "tool_calls": [],
            "error": "No text provided",
        }

    conversation_id = conversation_id or f"chat_{int(time.time() * 1000)}"
    task_id = ""
    task_manager = getattr(runtime, "task_manager", None)
    goal_service = getattr(runtime, "goal_service", None)
    if task_manager is not None:
        try:
            if goal_service is not None:
                task = goal_service.create_chat_task(clean_text, source=task_source)
            else:
                task = task_manager.create_task(
                    title=f"Chat: {clean_text[:50]}",
                    goal=clean_text,
                    source=task_source,
                )
                task_manager.start_task(task["task_id"])
            task_id = task.get("task_id") if isinstance(task, dict) else str(task)
        except Exception:
            logger.debug("Failed to create chat task", exc_info=True)

    try:
        system_prompt, memory_meta, _ = _build_chat_system_prompt(clean_text)
        memory_meta = dict(memory_meta)
        memory_meta.update(
            {
                "origin_channel": origin_channel,
                "conversation_id": conversation_id,
                "original_message": clean_text,
            }
        )
        if device_id:
            memory_meta["device_id"] = device_id
        if task_id:
            memory_meta["chat_task_id"] = task_id
        for key, value in (context or {}).items():
            memory_meta[f"client_{key}"] = value

        result = _call_llm_with_runtime(
            call_llm_with_tools,
            runtime.llm_gateway,
            clean_text,
            system_prompt,
            catalog=runtime.tool_broker._catalog,
            context_meta=memory_meta,
            runtime=runtime,
        )
        response_text = result.get("response", "")
        if task_id and not result.get("approval_needed") and not result.get("needs_user_input"):
            if goal_service is not None:
                evaluation = goal_service.finalize_chat_task(
                    task_id,
                    user_goal=clean_text,
                    response=response_text,
                    tool_results=list(result.get("tool_results") or []),
                )
                result["goal_status"] = evaluation.status
                result["goal_reason"] = evaluation.reason
            else:
                task_manager.complete_task(task_id, result_summary=response_text[:200])
        return {
            **result,
            "conversation_id": conversation_id,
            "task_id": task_id,
        }
    except Exception as exc:
        if task_id:
            try:
                task_manager.fail_task(task_id, error=str(exc))
            except Exception:
                logger.debug("Failed to fail chat task", exc_info=True)
        return {
            "response": f"Error: {exc}",
            "tool_results": [],
            "tool_calls": [],
            "conversation_id": conversation_id,
            "task_id": task_id,
            "error": str(exc),
        }


def tool_results_json(result: dict[str, Any]) -> str:
    """Serialize compact tool results for mobile gRPC responses."""
    tool_results = result.get("tool_results") or []
    try:
        return json.dumps(tool_results, ensure_ascii=False)
    except TypeError:
        return json.dumps([str(item) for item in tool_results], ensure_ascii=False)
