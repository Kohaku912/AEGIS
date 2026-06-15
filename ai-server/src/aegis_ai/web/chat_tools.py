"""Chat Tool Calling — unified tool calling for chat path.

Replaces old {"action": "..."} format with CapabilityCatalog-based tool calling.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.web.chat_tools")

_DATA_DIR = str(Path(__file__).resolve().parent.parent.parent.parent / "data")


def get_catalog():
    """Get CapabilityCatalog instance."""
    from aegis_ai.capability_catalog import CapabilityCatalog
    caps_dir = str(Path(_DATA_DIR).parent / "capabilities")
    apps_dir = str(Path(_DATA_DIR).parent / "apps")
    return CapabilityCatalog(capabilities_dir=caps_dir, apps_dir=apps_dir)


def get_tools_for_chat(catalog=None):
    """Get OpenAI tool definitions for chat."""
    if catalog is None:
        catalog = get_catalog()
    return catalog.list_for_tools()


def execute_tool_call(catalog, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool call from the LLM.

    Returns:
        {"success": bool, "result": str, "output": dict, "error": str}
    """
    cap_id = catalog.tool_name_to_cap_id(function_name)

    try:
        from tool_broker import ToolBroker, ToolExecutionRequest, ExecutionSource
        from tool_registry import ToolRegistry
        from aegis_ai.audit import AuditLog

        audit_log = AuditLog(path=os.path.join(_DATA_DIR, "audit.jsonl"))

        registry = ToolRegistry()
        for cap in catalog.to_tool_registry_capabilities():
            registry.register_capability(cap)

        broker = ToolBroker(registry=registry, audit_log=audit_log, catalog=catalog)

        request = ToolExecutionRequest(
            capability_id=cap_id,
            arguments=arguments,
            source=ExecutionSource.USER_EXPLICIT,
            reason=f"Chat tool call: {cap_id}",
        )
        result = broker.execute(request)

        if result.success:
            output = result.output or {}
            result_text = str(output.get("result", "Done"))
            return {
                "success": True,
                "result": result_text,
                "output": output,
                "error": "",
            }
        else:
            return {
                "success": False,
                "result": f"Failed: {result.error}",
                "output": result.output or {},
                "error": result.error,
            }
    except Exception as e:
        logger.error("Tool execution error for %s: %s", cap_id, e)
        return {
            "success": False,
            "result": f"Error: {e}",
            "output": {},
            "error": str(e),
        }


def call_llm_with_tools(
    llm,
    user_message: str,
    system_prompt: str,
    catalog=None,
    max_tool_rounds: int = 3,
) -> dict[str, Any]:
    """Call LLM with tool calling support.

    Returns:
        {"response": str, "tool_calls": list, "tool_results": list}
    """
    if catalog is None:
        catalog = get_catalog()

    tools = get_tools_for_chat(catalog)
    if not tools:
        result = llm.generate(prompt=user_message, system_prompt=system_prompt, max_tokens=1000)
        return {
            "response": result.content if result.success else f"LLM error: {result.error}",
            "tool_calls": [],
            "tool_results": [],
        }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})

    all_tool_calls = []
    all_tool_results = []

    for round_num in range(max_tool_rounds):
        try:
            response = llm._client.chat.completions.create(
                model=llm._model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=1000,
                temperature=0.3,
            )
        except Exception as e:
            logger.error("LLM tool call error: %s", e)
            break

        choice = response.choices[0]
        content = choice.message.content or ""

        if not choice.message.tool_calls:
            return {
                "response": content,
                "tool_calls": all_tool_calls,
                "tool_results": all_tool_results,
            }

        messages.append(choice.message)

        for tc in choice.message.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}

            tool_call_info = {
                "id": tc.id,
                "function": tc.function.name,
                "arguments": args,
            }
            all_tool_calls.append(tool_call_info)

            tool_result = execute_tool_call(catalog, tc.function.name, args)
            all_tool_results.append({
                "function": tc.function.name,
                "cap_id": catalog.tool_name_to_cap_id(tc.function.name),
                **tool_result,
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_result["result"],
            })

    try:
        response = llm._client.chat.completions.create(
            model=llm._model,
            messages=messages,
            max_tokens=1000,
            temperature=0.3,
        )
        content = response.choices[0].message.content or ""
        return {
            "response": content,
            "tool_calls": all_tool_calls,
            "tool_results": all_tool_results,
        }
    except Exception as e:
        logger.error("LLM final response error: %s", e)
        return {
            "response": "Tool execution completed.",
            "tool_calls": all_tool_calls,
            "tool_results": all_tool_results,
        }
