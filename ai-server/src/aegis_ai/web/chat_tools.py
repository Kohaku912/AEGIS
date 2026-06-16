"""Chat Tool Calling — unified tool calling for chat path.

Replaces old {"action": "..."} format with CapabilityCatalog-based tool calling.
Supports agentic multi-step tool calling loops.
"""

from __future__ import annotations

import inspect
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.web.chat_tools")

_DATA_DIR = str(Path(__file__).resolve().parent.parent.parent.parent / "data")


def get_catalog():
    try:
        from aegis_ai.runtime import get_runtime

        return get_runtime().capability_catalog
    except Exception:
        pass
    from aegis_ai.capability_catalog import CapabilityCatalog
    caps_dir = str(Path(_DATA_DIR).parent / "capabilities")
    apps_dir = str(Path(_DATA_DIR).parent / "apps")
    return CapabilityCatalog(capabilities_dir=caps_dir, apps_dir=apps_dir)


def get_tools_for_chat(catalog=None):
    if catalog is None:
        catalog = get_catalog()
    return catalog.list_for_tools()


def execute_tool_call(catalog, function_name: str, arguments: dict[str, Any], runtime: Any = None) -> dict[str, Any]:
    cap_id = catalog.tool_name_to_cap_id(function_name)
    if not catalog.resolve(cap_id):
        return {
            "success": False,
            "result": f"Failed: Capability '{cap_id}' is not registered.",
            "output": {},
            "error": f"Capability '{cap_id}' is not registered.",
            "needs_user_input": False,
            "needs_user_input_for": [],
        }

    try:
        from tool_broker import ToolExecutionRequest, ExecutionSource

        if runtime is None:
            from aegis_ai.runtime import get_runtime

            runtime = get_runtime()
        broker = runtime.tool_broker

        request = ToolExecutionRequest(
            capability_id=cap_id,
            arguments=arguments,
            source=ExecutionSource.USER_EXPLICIT,
            reason=f"Chat tool call: {cap_id}",
        )
        result = broker.execute(request)

        if result.success:
            output = result.output or {}
            output_success = output.get("success", True)
            if not output_success:
                error_msg = output.get("stderr", "") or output.get("error", "") or output.get("message", "") or "Command failed"
                return {
                    "success": False,
                    "result": f"Failed: {error_msg}",
                    "output": output,
                    "error": error_msg,
                    "needs_user_input": False,
                    "needs_user_input_for": [],
                }
            result_text = _stringify_tool_output(output)
            return {
                "success": True,
                "result": result_text,
                "output": output,
                "error": "",
                "needs_user_input": output.get("needs_user_input", False),
                "needs_user_input_for": output.get("needs_user_input_for", []),
            }
        else:
            output = result.output or {}
            error_msg = result.error or ""
            if not error_msg and isinstance(output, dict):
                error_msg = output.get("stderr", "") or output.get("error", "") or output.get("message", "")
            if not error_msg:
                error_msg = str(output) if output else "Unknown error"
            return {
                "success": False,
                "result": f"Failed: {error_msg}",
                "output": output,
                "error": error_msg,
                "needs_user_input": False,
                "needs_user_input_for": [],
            }
    except Exception as e:
        logger.error("Tool execution error for %s: %s", cap_id, e)
        return {
            "success": False,
            "result": f"Error: {e}",
            "output": {},
            "error": str(e),
        }


def _execute_tool_call(
    catalog,
    function_name: str,
    arguments: dict[str, Any],
    runtime: Any = None,
) -> dict[str, Any]:
    """Call the tool execution hook while preserving older test fakes."""

    try:
        parameters = inspect.signature(execute_tool_call).parameters
    except (TypeError, ValueError):
        parameters = {}
    if "runtime" in parameters:
        return execute_tool_call(catalog, function_name, arguments, runtime=runtime)
    return execute_tool_call(catalog, function_name, arguments)


def _stringify_tool_output(output: dict[str, Any]) -> str:
    if "result" in output and output["result"] not in (None, ""):
        return str(output["result"])
    if "content" in output and output["content"] not in (None, ""):
        return str(output["content"])
    if "value" in output and output["value"] not in (None, ""):
        return str(output["value"])
    if "cwd" in output and output["cwd"] not in (None, ""):
        return str(output["cwd"])
    if "image_base64" in output:
        width = output.get("width", "?")
        height = output.get("height", "?")
        return f"Screenshot captured ({width}x{height})."

    compact_output = {
        key: value
        for key, value in output.items()
        if key != "image_base64"
    }
    if compact_output:
        try:
            return json.dumps(compact_output, ensure_ascii=False)
        except TypeError:
            return str(compact_output)
    return "Done"


def _get_vision_llm(llm: Any) -> Any:
    if llm and hasattr(llm, "generate_with_image"):
        if not hasattr(llm, "_supports_vision"):
            return llm
        if getattr(llm, "_supports_vision")():
            return llm
    try:
        from aegis_ai.llm.factory import create_multimodal_llm_provider

        return create_multimodal_llm_provider()
    except Exception:
        return llm


def _summarize_observation_with_llm(llm: Any, tool_result: dict[str, Any]) -> str:
    output = tool_result.get("output", {})
    if not isinstance(output, dict):
        return tool_result.get("result", "Done")

    image_base64 = output.get("image_base64")
    vision_llm = _get_vision_llm(llm)
    if image_base64 and hasattr(vision_llm, "generate_with_image"):
        try:
            result = vision_llm.generate_with_image(
                prompt=(
                    "Summarize this screenshot as an actionable observation for the next tool decision. "
                    "Describe the visible page, app state, forms, dialogs, or errors in under 120 words."
                ),
                image_base64=image_base64,
                system_prompt="You convert screenshots into concise tool-planning observations.",
                max_tokens=200,
                detail="low",
            )
            if result.success and result.content:
                return result.content.strip()
        except Exception:
            logger.debug("Vision summarization failed", exc_info=True)

    return tool_result.get("result", "Done")


def _parse_tool_call(content: str, valid_tool_names: set[str] | None = None) -> dict | None:
    """Extract a single tool call from LLM content. Returns None if no tool call found.
    
    Args:
        content: LLM response content to parse
        valid_tool_names: Optional set of valid tool names for validation.
                         If provided, only tool calls with names in this set are returned.
    """

    matches = re.findall(r'<tool_call>(.*?)</tool_call>', content, re.DOTALL)

    if not matches:
        dsml_pattern = r'<\｜\｜DSML\｜\｜invoke name="([^"]+)">(.*?)(?:<\｜\｜DSML\｜\｜/invoke>|$)'
        dsml_matches = re.findall(dsml_pattern, content, re.DOTALL)
        for func_name, params_block in dsml_matches:
            args = {}
            param_pattern = r'<\｜\｜DSML\｜\｜parameter name="([^"]+)"[^>]*>([^<]*)'
            for param_name, param_value in re.findall(param_pattern, params_block):
                args[param_name] = param_value.strip()
            matches.append(json.dumps({"name": func_name, "arguments": args}))

    if not matches:
        xml_tag_pattern = r'<((?:pc|browser|android|room|ai)-server__[a-zA-Z0-9_]+)(?:\s[^>]*)?>(.*?)</\1>'
        xml_matches = re.findall(xml_tag_pattern, content, re.DOTALL)
        for tag_name, inner in xml_matches:
            # Validate against known tool names if provided
            if valid_tool_names and tag_name not in valid_tool_names:
                continue
            args = {}
            arg_pattern = r'<(\w+)(?:\s[^>]*)?>([^<]*)</\1>'
            for arg_name, arg_value in re.findall(arg_pattern, inner):
                args[arg_name] = arg_value.strip()
            if not args:
                attr_pattern = r'(\w+)="([^"]*)"'
                for attr_name, attr_value in re.findall(attr_pattern, inner):
                    args[attr_name] = attr_value.strip()
            if args:
                matches.append(json.dumps({"name": tag_name, "arguments": args}))

    if not matches:
        try:
            clean = content.strip()
            if clean.startswith("{"):
                parsed = json.loads(clean)
                if "name" in parsed and "arguments" in parsed:
                    matches.append(clean)
        except json.JSONDecodeError:
            pass

    if not matches:
        return None

    for match in matches:
        try:
            parsed = json.loads(match.strip())
            # Validate tool name if valid set provided
            if valid_tool_names and parsed.get("name") not in valid_tool_names:
                continue
            return parsed
        except json.JSONDecodeError:
            continue

    return None


def _build_tool_loop_prompt(
    *,
    user_message: str,
    tool_list: str,
    conversation_history: list[dict[str, str]],
) -> str:
    """Build a prompt that preserves the original goal across tool rounds."""

    history_lines: list[str] = []
    for item in conversation_history:
        role = item.get("role", "")
        if role == "assistant_tool_call":
            history_lines.append(
                f"Assistant chose tool: {item.get('name', '')}\n"
                f"Arguments: {item.get('arguments', '{}')}"
            )
        elif role == "tool":
            history_lines.append(
                f"Tool result from {item.get('name', '')}:\n"
                f"{item.get('result', '')}"
            )

    history_block = "\n\nPrevious tool activity:\n" + "\n\n".join(history_lines) if history_lines else ""

    return (
        f"Original user request:\n{user_message}\n"
        f"{history_block}\n\n"
        f"Available tools:\n{tool_list}\n\n"
        "- ask_user: Ask the user a question with options\n\n"
        "INSTRUCTIONS:\n"
        "- To use a tool, respond with ONLY:\n"
        '<tool_call>{"name": "tool_name", "arguments": {"key": "value"}}</tool_call>\n'
        "- To ask the user a question, use ask_user tool:\n"
        '<tool_call>{"name": "ask_user", "arguments": {"question": "Your question?", "options": ["option1", "option2"]}}</tool_call>\n'
        "- For text input: {\"name\": \"ask_user\", \"arguments\": {\"question\": \"...\", \"options\": []}}\n"
        "- ONLY use tools listed above. Do NOT invent tool names.\n"
        "- For normal text file saves, prefer pc-server__file__write instead of shell commands.\n"
        "- Use shell tools only when a dedicated capability cannot perform the task.\n"
        "- If no tool is needed, respond normally.\n"
        "- NEVER mix tool calls with text responses.\n"
        "- Keep working toward the original user request until it is complete.\n"
        "- When the user asks for their input, preferences, or choices, ALWAYS use ask_user tool.\n"
        "- You can call multiple tools in sequence. After each tool result, decide whether another tool is needed.\n"
        "- When the task is fully complete, respond with a natural summary (no tool call)."
    )


def _generate_tool_step(
    llm: Any,
    prompt: str,
    system_prompt: str,
    tools: list[dict[str, Any]],
    valid_tool_names: set[str],
    context_meta: dict[str, Any] | None = None,
) -> tuple[Any, dict[str, Any] | None]:
    """Get the next LLM step, preferring native tool calling when available."""

    if hasattr(llm, "generate_with_tools"):
        try:
            tool_result = llm.generate_with_tools(
                prompt=prompt,
                tools=tools,
                system_prompt=system_prompt,
                max_tokens=1000,
                context_meta=context_meta,
            )
            if tool_result.success:
                if tool_result.tool_calls:
                    first_call = tool_result.tool_calls[0]
                    if first_call.get("function") in valid_tool_names:
                        return tool_result, {
                            "name": first_call.get("function", ""),
                            "arguments": first_call.get("arguments", {}),
                        }
                return tool_result, None
        except Exception:
            logger.debug("Native tool calling failed; falling back to text parsing", exc_info=True)

    result = llm.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=1000,
        context_meta=context_meta,
    )
    if not result.success:
        return result, None
    return result, _parse_tool_call(result.content or "", valid_tool_names=valid_tool_names)


def call_llm_with_tools(
    llm,
    user_message: str,
    system_prompt: str,
    catalog=None,
    max_tool_rounds: int = 15,
    context_meta: dict[str, Any] | None = None,
    runtime: Any = None,
) -> dict[str, Any]:
    if runtime is None:
        try:
            from aegis_ai.runtime import get_runtime

            runtime = get_runtime()
        except Exception:
            runtime = None
    if catalog is None:
        catalog = runtime.capability_catalog if runtime is not None else get_catalog()

    tools = get_tools_for_chat(catalog)
    if not tools:
        result = llm.generate(
            prompt=user_message,
            system_prompt=system_prompt,
            max_tokens=1000,
            context_meta=context_meta,
        )
        return {
            "response": result.content if result.success else f"LLM error: {result.error}",
            "tool_calls": [],
            "tool_results": [],
        }

    tool_list = "\n".join(f"- {t['function']['name']}: {t['function']['description']}" for t in tools)
    valid_tool_names: set[str] = {t['function']['name'] for t in tools}
    valid_tool_names.add("ask_user")

    all_tool_calls = []
    all_tool_results = []
    conversation_history = []
    final_response = ""
    for round_num in range(max_tool_rounds):
        current_prompt = _build_tool_loop_prompt(
            user_message=user_message,
            tool_list=tool_list,
            conversation_history=conversation_history,
        )
        result, tc = _generate_tool_step(
            llm=llm,
            prompt=current_prompt,
            system_prompt=system_prompt,
            tools=tools,
            valid_tool_names=valid_tool_names,
            context_meta=context_meta,
        )
        if not result.success:
            if round_num == 0:
                return {"response": f"LLM error: {result.error}", "tool_calls": [], "tool_results": []}
            break

        content = result.content or ""

        if tc is None:
            if round_num == 0:
                return {"response": content, "tool_calls": [], "tool_results": []}
            final_response = content
            break

        func_name = tc.get("name", "")
        args = tc.get("arguments", {})

        if not func_name:
            if round_num == 0:
                return {"response": content, "tool_calls": [], "tool_results": []}
            final_response = content
            break

        if func_name == "ask_user":
            return {
                "response": args.get("question", ""),
                "tool_calls": all_tool_calls + [{"function": "ask_user", "arguments": args}],
                "tool_results": all_tool_results,
                "needs_user_input": True,
                "question": args.get("question", ""),
                "options": args.get("options", []),
            }

        tool_call_info = {"function": func_name, "arguments": args}
        all_tool_calls.append(tool_call_info)
        conversation_history.append({
            "role": "assistant_tool_call",
            "name": func_name,
            "arguments": json.dumps(args, ensure_ascii=False),
        })

        tool_result = _execute_tool_call(catalog, func_name, args, runtime=runtime)
        all_tool_results.append({
            "function": func_name,
            "cap_id": catalog.tool_name_to_cap_id(func_name),
            **tool_result,
        })

        if tool_result.get("needs_user_input"):
            reasons = tool_result.get("needs_user_input_for", [])
            reason_text = reasons[0] if reasons else "ブラウザ操作の続きを実行する必要があります"
            return {
                "response": f"ユーザーの操作が必要です: {reason_text}",
                "tool_calls": all_tool_calls,
                "tool_results": all_tool_results,
                "needs_user_input": True,
                "question": f"ユーザーの操作が必要です: {reason_text}\n操作が完了したら「完了」と送信してください。",
                "options": ["完了", "キャンセル"],
                "pending_context": {
                    "original_message": user_message,
                    "system_prompt": system_prompt,
                    "browser_task": args.get("task", ""),
                },
            }

        result_summary = _summarize_observation_with_llm(llm, tool_result)[:500]
        conversation_history.append({
            "role": "tool",
            "name": func_name,
            "result": f"Success: {tool_result.get('success', False)}\n{result_summary}",
        })
        error_info = ""
        if not tool_result.get("success") and tool_result.get("error"):
            error_info = f"\nError: {tool_result['error'][:200]}"
        if error_info:
            conversation_history[-1]["result"] += error_info


    if all_tool_results:
        needs_input_results = [tr for tr in all_tool_results if tr.get("needs_user_input")]
        if needs_input_results:
            first = needs_input_results[0]
            reasons = first.get("needs_user_input_for", [])
            reason_text = reasons[0] if reasons else "ブラウザ操作の続きを実行する必要があります"
            return {
                "response": f"ブラウザ操作中にユーザーの操作が必要になりました: {reason_text}\n操作が完了したら教えてください。続きから再開します。",
                "tool_calls": all_tool_calls,
                "tool_results": all_tool_results,
                "needs_user_input": True,
                "question": f"ブラウザ操作中にユーザーの操作が必要です: {reason_text}\n操作が完了したら「完了」と送信してください。",
                "options": ["完了", "キャンセル"],
                "pending_context": {
                    "original_message": user_message,
                    "system_prompt": system_prompt,
                    "browser_task": all_tool_calls[0].get("arguments", {}).get("task", "") if all_tool_calls else "",
                },
            }

    if final_response:
        return {
            "response": final_response,
            "tool_calls": all_tool_calls,
            "tool_results": all_tool_results,
        }

    final_text = ""
    for tr in all_tool_results:
        if tr.get("result"):
            final_text += f"{tr['function']}: {tr['result'][:200]}\n"

    return {
        "response": final_text.strip() if final_text else "Tool execution completed.",
        "tool_calls": all_tool_calls,
        "tool_results": all_tool_results,
    }
