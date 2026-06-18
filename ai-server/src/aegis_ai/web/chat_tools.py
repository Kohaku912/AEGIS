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


def _emit_event(
    runtime: Any,
    event_type: str,
    *,
    status: str = "completed",
    profile: str = "",
    model: str = "",
    tool_id: str = "",
    duration_ms: int = 0,
    result_preview: str = "",
    error: str = "",
    reason: str = "",
) -> None:
    """Emit a structured event for LLM/tool/vision operations."""
    if runtime is None:
        return
    try:
        audit_log = getattr(runtime, "audit_log", None) or getattr(runtime, "audit_manager", None)
        if audit_log and hasattr(audit_log, "log_decision"):
            audit_log.log_decision(
                event_type,
                tool_id or "llm",
                "EXECUTED" if status in ("completed", "started") else "FAILED",
                reason=reason or event_type,
                actor="chat_tools",
                detail={
                    "status": status,
                    "profile": profile,
                    "model": model,
                    "tool_id": tool_id,
                    "duration_ms": duration_ms,
                    "result_preview": result_preview[:200] if result_preview else "",
                    "error": error[:200] if error else "",
                },
            )
        else:
            logger.info("Event: %s status=%s tool=%s profile=%s", event_type, status, tool_id, profile)
    except Exception:
        logger.debug("Failed to emit event: %s", event_type, exc_info=True)


def get_catalog():
    from aegis_ai.runtime import get_runtime

    return get_runtime().capability_catalog


def get_tools_for_chat(
    catalog=None,
    user_message: str = "",
    session_context: dict[str, Any] | None = None,
    runtime: Any = None,
):
    if catalog is None:
        catalog = get_catalog()
    retriever = getattr(runtime, "capability_retriever", None) if runtime is not None else None
    if retriever is not None:
        selection = retriever.select_for_request(
            user_message,
            session_context or {},
            top_k_schema=8,
            top_k_summary=50,
        )
        return selection.tools
    return catalog.list_for_tools()


def get_capability_selection(
    catalog=None,
    user_message: str = "",
    session_context: dict[str, Any] | None = None,
    runtime: Any = None,
):
    retriever = getattr(runtime, "capability_retriever", None) if runtime is not None else None
    if retriever is None:
        return None
    return retriever.select_for_request(
        user_message,
        session_context or {},
        top_k_schema=8,
        top_k_summary=50,
    )


def execute_tool_call(catalog, function_name: str, arguments: dict[str, Any], runtime: Any = None) -> dict[str, Any]:
    if function_name in {"capability__search", "capability__describe"}:
        return _execute_meta_tool(function_name, arguments, runtime=runtime, catalog=catalog)

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


def _execute_meta_tool(
    function_name: str,
    arguments: dict[str, Any],
    *,
    runtime: Any = None,
    catalog: Any = None,
) -> dict[str, Any]:
    retriever = getattr(runtime, "capability_retriever", None) if runtime is not None else None
    if function_name == "capability__search":
        query = str(arguments.get("query", ""))
        top_k = int(arguments.get("top_k", 10) or 10)
        summaries = retriever.search_lightweight(query, top_k=top_k) if retriever else []
        return {
            "success": True,
            "result": json.dumps(summaries, ensure_ascii=False),
            "output": {"summaries": summaries},
            "error": "",
            "needs_user_input": False,
            "needs_user_input_for": [],
        }

    if function_name == "capability__describe":
        cap_id = str(arguments.get("capability_id", ""))
        detail = retriever.describe(cap_id) if retriever else None
        if detail is None and catalog is not None and hasattr(catalog, "describe"):
            detail = catalog.describe(cap_id)
        if detail is None:
            return {
                "success": False,
                "result": f"Capability '{cap_id}' not found.",
                "output": {},
                "error": f"Capability '{cap_id}' not found.",
                "needs_user_input": False,
                "needs_user_input_for": [],
            }
        return {
            "success": True,
            "result": json.dumps(detail, ensure_ascii=False),
            "output": {"detail": detail, "described_capability_id": detail.get("id", cap_id)},
            "error": "",
            "needs_user_input": False,
            "needs_user_input_for": [],
        }

    return {
        "success": False,
        "result": f"Unknown meta tool '{function_name}'.",
        "output": {},
        "error": f"Unknown meta tool '{function_name}'.",
        "needs_user_input": False,
        "needs_user_input_for": [],
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


def _get_vision_llm(llm: Any, *, runtime: Any = None) -> Any:
    """Resolve a vision LLM from llm.yaml ``vision_observation`` profile.

    Resolution: settings_resolver only. Raises ``RuntimeError`` when no vision provider can be created.
    """
    settings_resolver = getattr(runtime, "settings_resolver", None) if runtime else None

    if settings_resolver is not None:
        try:
            from aegis_ai.llm.factory import create_multimodal_llm_provider

            provider = create_multimodal_llm_provider(settings_resolver=settings_resolver)
            if provider is not None and hasattr(provider, "generate_with_image"):
                logger.info(
                    "Vision LLM resolved from settings_resolver: profile=vision_observation, model=%s base_url=%s api_key_env=%s",
                    getattr(provider, "_model", "unknown"),
                    getattr(provider, "_base_url", "unknown"),
                    "LLM_VISION_API_KEY",
                )
                return provider
        except Exception as exc:
            logger.error(
                "Failed to create vision LLM from settings_resolver: %s",
                exc,
                exc_info=True,
            )

    raise RuntimeError(
        "No vision-capable LLM provider available. "
        "Ensure llm.yaml has a 'vision_observation' profile with a valid api_key_env and base_url, "
        "and that LLM_VISION_API_KEY is set in the environment."
    )


def _summarize_observation_with_llm(
    llm: Any,
    tool_result: dict[str, Any],
    *,
    runtime: Any = None,
) -> str:
    """Summarize a screenshot observation using the vision_observation profile.

    Raises ``RuntimeError`` when vision summarization fails so the caller
    can surface a clear error instead of returning a misleading fixed string.
    """
    output = tool_result.get("output", {})
    if not isinstance(output, dict):
        return tool_result.get("result", "Done")

    image_base64 = output.get("image_base64")
    if not image_base64:
        return tool_result.get("result", "Done")

    _emit_event(runtime, "vision.summarization.started", status="started",
                profile="vision_observation", reason="????????????????")
    try:
        vision_llm = _get_vision_llm(llm, runtime=runtime)
    except RuntimeError:
        _emit_event(runtime, "vision.summarization.failed", status="failed",
                    profile="vision_observation", error="Vision LLM provider not available")
        raise
    except Exception as exc:
        _emit_event(runtime, "vision.summarization.failed", status="failed",
                    profile="vision_observation", error=str(exc))
        raise RuntimeError(f"Failed to resolve vision LLM: {exc}") from exc

    try:
        logger.info(
            "Calling vision LLM for screenshot summarization: "
            "provider=%s model=%s base_url=%s",
            type(vision_llm).__name__,
            getattr(vision_llm, "_model", "unknown"),
            getattr(vision_llm, "_base_url", "unknown"),
        )
        result = vision_llm.generate_with_image(
            prompt=(
                "このスクリーンショットの内容を日本語で簡潔に要約してください。"
                "画面上に見えるアプリ、ページ、フォーム、ダイアログ、エラーなどを120語以内で説明してください。"
            ),
            image_base64=image_base64,
            system_prompt="あなたはスクリーンショットを簡潔な要約に変換するアシスタントです。",
            max_tokens=200,
            detail="low",
        )
        if result.success and result.content:
            _emit_event(runtime, "vision.summarization.completed", status="completed",
                        profile="vision_observation",
                        model=getattr(vision_llm, "_model", "unknown"),
                        result_preview=result.content[:200] if result.content else "")
            return result.content.strip()

        error_detail = result.error or "empty response"
        _emit_event(runtime, "vision.summarization.failed", status="failed",
                    profile="vision_observation", error=str(error_detail))
        raise RuntimeError(
            f"Vision LLM returned failure: profile=vision_observation, "
            f"model={getattr(vision_llm, '_model', 'unknown')}, "
            f"base_url={getattr(vision_llm, '_base_url', 'unknown')}, "
            f"api_key_env=LLM_VISION_API_KEY, "
            f"provider={type(vision_llm).__name__}, "
            f"reason={error_detail}"
        )
    except RuntimeError:
        raise
    except Exception as exc:
        _emit_event(runtime, "vision.summarization.failed", status="failed",
                    profile="vision_observation", error=str(exc))
        raise RuntimeError(
            f"Vision LLM call failed: profile=vision_observation, "
            f"model={getattr(vision_llm, '_model', 'unknown')}, "
            f"base_url={getattr(vision_llm, '_base_url', 'unknown')}, "
            f"api_key_env=LLM_VISION_API_KEY, "
            f"provider={type(vision_llm).__name__}, "
            f"reason={exc}"
        ) from exc


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
    lightweight_catalog: list[dict[str, Any]] | None = None,
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

    catalog_lines = []
    for item in lightweight_catalog or []:
        tags = ", ".join(item.get("tags", []))
        catalog_lines.append(
            f"- {item.get('id', '')}: {item.get('title', '')} "
            f"(risk: {item.get('risk', '')}, tags: {tags}) - {item.get('short_desc', '')}"
        )
    catalog_block = "\n\nLightweight capability catalog:\n" + "\n".join(catalog_lines) if catalog_lines else ""

    return (
        f"Original user request:\n{user_message}\n"
        f"{history_block}\n\n"
        f"Available full-schema tools:\n{tool_list}\n"
        f"{catalog_block}\n\n"
        "INSTRUCTIONS:\n"
        "- To use a tool, respond with ONLY:\n"
        '<tool_call>{"name": "tool_name", "arguments": {"key": "value"}}</tool_call>\n'
        "- To ask the user a question, use ask_user tool:\n"
        '<tool_call>{"name": "ask_user", "arguments": {"question": "Your question?", "options": ["option1", "option2"]}}</tool_call>\n'
        "- For text input: {\"name\": \"ask_user\", \"arguments\": {\"question\": \"...\", \"options\": []}}\n"
        "- ONLY call full-schema tools listed above. Do NOT invent tool names.\n"
        "- Use capability__search to find more capability summaries.\n"
        "- Use capability__describe to fetch full schema before calling a capability that only appears in the lightweight catalog.\n"
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

    selection = get_capability_selection(
        catalog,
        user_message=user_message,
        session_context=context_meta,
        runtime=runtime,
    )
    lightweight_catalog = selection.lightweight_catalog if selection is not None else []
    tools = selection.tools if selection is not None else get_tools_for_chat(
        catalog,
        user_message=user_message,
        session_context=context_meta,
        runtime=runtime,
    )
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

    valid_tool_names: set[str] = {t['function']['name'] for t in tools}
    valid_tool_names.add("ask_user")

    all_tool_calls = []
    all_tool_results = []
    conversation_history = []
    final_response = ""
    for round_num in range(max_tool_rounds):
        tool_list = "\n".join(f"- {t['function']['name']}: {t['function']['description']}" for t in tools)
        current_prompt = _build_tool_loop_prompt(
            user_message=user_message,
            tool_list=tool_list,
            lightweight_catalog=lightweight_catalog,
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

        _emit_event(runtime, "tool.execution.started", status="started",
                    tool_id=func_name, reason=f"?????: {func_name}")
        tool_result = _execute_tool_call(catalog, func_name, args, runtime=runtime)
        _emit_event(runtime, "tool.execution.completed" if tool_result.get("success") else "tool.execution.failed",
                    status="completed" if tool_result.get("success") else "failed",
                    tool_id=catalog.tool_name_to_cap_id(func_name) if catalog else func_name,
                    result_preview=str(tool_result.get("result", ""))[:200],
                    error=str(tool_result.get("error", ""))[:200] if not tool_result.get("success") else "")
        described_cap_id = ""
        if func_name == "capability__describe" and tool_result.get("success"):
            output = tool_result.get("output", {})
            described_cap_id = output.get("described_capability_id", "")
            if described_cap_id:
                existing_names = {tool["function"]["name"] for tool in tools}
                for tool in catalog.list_for_tools({described_cap_id}):
                    name = tool["function"]["name"]
                    if name not in existing_names:
                        tools.append(tool)
                        valid_tool_names.add(name)
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

        vision_error = ""
        result_summary = ""
        try:
            result_summary = _summarize_observation_with_llm(
                llm, tool_result, runtime=runtime,
            )[:500]
        except RuntimeError as exc:
            vision_error = str(exc)
            logger.error("Vision summarization failed: %s", vision_error)
            result_summary = tool_result.get("result", "")
        conversation_history.append({
            "role": "tool",
            "name": func_name,
            "result": f"Success: {tool_result.get('success', False)}\n{result_summary}",
        })
        if vision_error:
            conversation_history[-1]["result"] += (
                f"\n[VISION_ERROR] スクリーンショット画像の要約に失敗しました: {vision_error}"
            )
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

    vision_errors = [
        tr for tr in all_tool_results
        if "[VISION_ERROR]" in tr.get("result", "")
    ]
    if vision_errors:
        error_detail = vision_errors[0]["result"]
        vision_part = error_detail.split("[VISION_ERROR]")[-1].strip() if "[VISION_ERROR]" in error_detail else error_detail
        return {
            "response": (
                f"スクリーンショットの取得は成功しましたが、画像要約LLMの呼び出しに失敗しました。\n\n"
                f"エラー詳細: {vision_part}"
            ),
            "tool_calls": all_tool_calls,
            "tool_results": all_tool_results,
            "vision_error": vision_part,
        }

    summary_lines = [
        f"ユーザーの元のリクエスト: {user_message}",
        "",
        "ツール実行結果:",
    ]
    for tr in all_tool_results:
        summary_lines.append(f"- {tr.get('function', '')}: {tr.get('result', '')[:300]}")
    summary_lines.append("")
    summary_lines.append(
        "上記のツール実行結果を踏まえて、ユーザーへの最終回答を自然な日本語で生成してください。"
        "ツール実行の技術的な詳細ではなく、ユーザーが知りたい情報を伝えてください。"
        "ツールは呼ばず、最終回答のみを生成してください。"
    )
    summary_round_prompt = "\n".join(summary_lines)

    summary_result, summary_tc = _generate_tool_step(
        llm=llm,
        prompt=summary_round_prompt,
        system_prompt="あなたはAEGISアシスタントです。ツール実行結果を元に、ユーザーに分かりやすい自然な日本語で回答してください。ツール呼び出しせず、最終回答のみを生成してください。",
        tools=tools,
        valid_tool_names=valid_tool_names,
        context_meta=context_meta,
    )
    if summary_result.success and summary_result.content and summary_tc is None:
        return {
            "response": summary_result.content.strip(),
            "tool_calls": all_tool_calls,
            "tool_results": all_tool_results,
        }
    if summary_result.success and summary_result.content:
        logger.warning("Summary round LLM attempted tool call instead of generating final response")

    tool_names = [tr.get("function", "unknown") for tr in all_tool_results]
    return {
        "response": (
            f"ツール実行は完了しましたが、最終応答の生成に失敗しました。"
            f"実行されたツール: {', '.join(tool_names)}"
        ),
        "tool_calls": all_tool_calls,
        "tool_results": all_tool_results,
    }
