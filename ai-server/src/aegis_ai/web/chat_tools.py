"""Chat Tool Calling — unified tool calling for chat path.

Replaces old {"action": "..."} format with CapabilityCatalog-based tool calling.
Supports agentic multi-step tool calling loops.
"""

from __future__ import annotations

import inspect
import json
import logging
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


def _presentation_tool_definition() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "present_info",
            "description": "Create a presentation card for information the user should see. Use this for concise summaries, findings, task results, or structured updates worth showing visually.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short display title.",
                    },
                    "summary": {
                        "type": "string",
                        "description": "Short human-readable summary.",
                    },
                    "content": {
                        "type": "object",
                        "description": "Structured presentation content.",
                    },
                    "modality": {
                        "type": "string",
                        "description": "Optional modality such as text_card, chart_panel, diagram_panel, gltf_model, or overlay_short.",
                    },
                    "importance": {
                        "type": "string",
                        "description": "Optional importance: low, normal, high, or critical.",
                    },
                },
                "required": ["title", "summary", "content"],
                "additionalProperties": False,
            },
        },
    }


def _present_info(runtime: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    presentation_manager = getattr(runtime, "presentation_manager", None) if runtime is not None else None
    if presentation_manager is None:
        return {
            "ok": False,
            "error": "PresentationManager not available",
            "presentation": {},
            "delivery": {},
        }

    from aegis_ai.presentation.models import PresentationRequest

    content = arguments.get("content", {})
    if not isinstance(content, dict):
        content = {"value": content}

    request = PresentationRequest(
        source="chat",
        intent="present_info",
        title=str(arguments.get("title", "") or "").strip(),
        summary=str(arguments.get("summary", "") or "").strip(),
        content=content,
        importance=str(arguments.get("importance", "normal") or "normal").strip(),
        modality=str(arguments.get("modality", "text_card") or "text_card").strip(),
    )
    return presentation_manager.present(request)


def execute_tool_call(
    catalog,
    function_name: str,
    arguments: dict[str, Any],
    runtime: Any = None,
    tool_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if function_name == "present_info":
        if runtime is None:
            from aegis_ai.runtime import get_runtime

            runtime = get_runtime()
        return _present_info(runtime, arguments)

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
        from tool_broker import ToolExecutionRequest, ExecutionSource, InvokeStatus

        if runtime is None:
            from aegis_ai.runtime import get_runtime

            runtime = get_runtime()
        broker = runtime.tool_broker
        tool_context = dict(tool_context or {})
        task_id = str(tool_context.get("chat_task_id", "") or "")
        step_id = function_name
        origin_channel = str(tool_context.get("origin_channel", "") or "")
        conversation_id = str(tool_context.get("conversation_id", "") or "")

        task_manager = getattr(runtime, "task_manager", None)
        if task_manager is not None and task_id:
            try:
                task_manager.add_step(task_id, step_id, function_name, cap_id)
                task_manager.update_step_status(task_id, step_id, "running")
                task_manager.set_current_step(task_id, step_id)
            except Exception:
                logger.debug("Failed to mark chat tool step running", exc_info=True)

        request = ToolExecutionRequest(
            task_id=task_id,
            step_id=step_id if task_id else "",
            capability_id=cap_id,
            arguments=arguments,
            source=ExecutionSource.USER_EXPLICIT,
            reason=f"Chat tool call: {cap_id}",
            origin_channel=origin_channel,
            conversation_id=conversation_id,
            metadata=tool_context,
        )
        result = broker.execute(request)

        if result.success:
            output = normalize_tool_output(result.output or {})
            output_success = output.get("success", True)
            if not output_success:
                error_msg = output.get("stderr", "") or output.get("error", "") or output.get("message", "") or "Command failed"
                if task_manager is not None and task_id:
                    try:
                        task_manager.update_step_status(task_id, step_id, "failed", error=error_msg)
                    except Exception:
                        logger.debug("Failed to mark chat tool step failed", exc_info=True)
                return {
                    "success": False,
                    "result": f"Failed: {error_msg}",
                    "output": output,
                    "error": error_msg,
                    "needs_user_input": False,
                    "needs_user_input_for": [],
                }
            if task_manager is not None and task_id:
                try:
                    task_manager.update_step_status(task_id, step_id, "completed", result=result.output)
                except Exception:
                    logger.debug("Failed to mark chat tool step completed", exc_info=True)
            result_text = _stringify_tool_output(output)
            return {
                "success": True,
                "result": result_text,
                "output": output,
                "error": "",
                "needs_user_input": output.get("needs_user_input", False),
                "needs_user_input_for": output.get("needs_user_input_for", []),
            }

        if result.status == InvokeStatus.APPROVAL_NEEDED:
            if task_manager is not None and task_id:
                try:
                    task_manager.wait_for_approval(task_id, step_id, result.approval_id)
                    task_manager.set_waiting_approval(task_id, step_id, result.approval_id)
                except Exception:
                    logger.debug("Failed to mark chat tool approval wait", exc_info=True)
            approval_msg = f"承認が必要です。Approvals で承認してください。approval_id={result.approval_id}"
            return {
                "success": False,
                "result": approval_msg,
                "output": result.output or {},
                "error": result.error or "Approval required",
                "needs_user_input": False,
                "needs_user_input_for": [],
                "approval_needed": True,
                "approval_id": result.approval_id,
            }

        if task_manager is not None and task_id:
            try:
                task_manager.update_step_status(task_id, step_id, "failed", error=result.error)
            except Exception:
                logger.debug("Failed to mark chat tool step failed", exc_info=True)
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
    tool_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call the tool execution hook while preserving older test fakes."""

    try:
        parameters = inspect.signature(execute_tool_call).parameters
    except (TypeError, ValueError):
        parameters = {}
    kwargs: dict[str, Any] = {}
    if "runtime" in parameters:
        kwargs["runtime"] = runtime
    if "tool_context" in parameters:
        kwargs["tool_context"] = tool_context
    return execute_tool_call(catalog, function_name, arguments, **kwargs)


def _format_posts_for_llm(output: dict[str, Any]) -> str:
    """Preserve AGORA/social post bodies when feeding tool output back to an LLM."""
    posts = output.get("posts")
    if not isinstance(posts, list) or not posts:
        return ""
    try:
        from aegis_ai.memory.memory_ingest import build_agora_posts_text

        header = None
        for key in ("result", "summary", "message"):
            value = output.get(key)
            if isinstance(value, str) and value.strip():
                # Prefer a body-bearing render over count-only status strings.
                if "durable processing is queued" in value.lower() or value.strip().endswith("post(s)."):
                    header = None
                else:
                    header = value
                break
        text = build_agora_posts_text(posts, header=header)
        meta_parts = []
        for key in ("read_mode", "cursor_before", "cursor_after", "read_since_id", "unread_count", "fetched_count"):
            if key in output and output[key] not in (None, ""):
                meta_parts.append(f"{key}={output[key]}")
        if meta_parts:
            text = f"{text}\nmeta: {', '.join(meta_parts)}"
        return text
    except Exception:
        # Fallback: include raw posts JSON so bodies are not dropped.
        try:
            return json.dumps(
                {
                    "result": output.get("result"),
                    "posts": posts,
                    "read_mode": output.get("read_mode"),
                },
                ensure_ascii=False,
            )
        except TypeError:
            return str(posts)


def _stringify_tool_output(output: dict[str, Any]) -> str:
    if "root" in output and isinstance(output.get("root"), dict):
        return _summarize_ui_tree(output["root"])
    posts_text = _format_posts_for_llm(output)
    if posts_text:
        return posts_text
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


def _summarize_ui_tree(root: dict[str, Any]) -> str:
    visible_text: list[str] = []
    clickable: list[str] = []

    def walk(node: dict[str, Any]) -> None:
        label = str(node.get("text") or node.get("content_desc") or "").strip()
        if label and label not in visible_text:
            visible_text.append(label)
        if node.get("is_clickable") and label and label not in clickable:
            clickable.append(label)
        for child in node.get("children") or []:
            if isinstance(child, dict):
                walk(child)

    walk(root)
    width = root.get("width", "?")
    height = root.get("height", "?")
    text_preview = visible_text[:80]
    clickable_preview = clickable[:40]
    return json.dumps(
        {
            "summary": "Android UI tree captured",
            "screen_size": f"{width}x{height}",
            "visible_text": text_preview,
            "clickable_text": clickable_preview,
            "visible_text_count": len(visible_text),
        },
        ensure_ascii=False,
    )


def normalize_tool_output(output: dict[str, Any]) -> dict[str, Any]:
    """Normalize server-specific result fields for chat/vision handling."""
    normalized = dict(output or {})
    image_data = normalized.get("image_data")
    if image_data and not normalized.get("image_base64"):
        if isinstance(image_data, bytes):
            import base64

            normalized["image_base64"] = base64.b64encode(image_data).decode("ascii")
        else:
            normalized["image_base64"] = str(image_data)
        normalized.setdefault("format", "png")
    return normalized


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
        "- Choose freely among offered capabilities based on the current request; do not prefer a fixed capability id.\n"
        "- Treat the Original user request as the current task. Previous history is context only; do not let it replace the current request.\n"
        "- Do NOT call tools for greetings, simple conversation, or questions you can answer from the current context.\n"
        "- If no tool is needed, respond normally and follow the user's requested language/length.\n"
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


def _with_usage_breakdown(
    context_meta: dict[str, Any],
    *,
    system_prompt: str = "",
    history: list[Any] | None = None,
    tools: list[dict[str, Any]] | None = None,
    user_message: str = "",
) -> dict[str, Any]:
    meta = dict(context_meta)
    context_tokens = dict(meta.get("context_tokens") or {})

    def estimate(value: Any) -> int:
        if value is None:
            return 0
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
        return max(0, (len(text) + 3) // 4)

    if system_prompt:
        context_tokens["system"] = context_tokens.get("system", 0) + estimate(system_prompt)
    if history:
        context_tokens["history"] = context_tokens.get("history", 0) + estimate(history)
    if tools:
        context_tokens["tool_schema"] = estimate(tools)
    if user_message:
        context_tokens["user_state"] = context_tokens.get("user_state", 0) + estimate(user_message)
    meta["context_tokens"] = context_tokens
    return meta


def _llm_wants_tools(
    llm: Any,
    user_message: str,
    *,
    system_prompt: str,
    context_meta: dict[str, Any] | None = None,
) -> tuple[bool | None, dict[str, Any] | None]:
    """Ask the LLM whether the current request needs external capabilities.

    Some providers or test doubles may return a tool call instead of the
    requested JSON decision. Preserve that tool call so the first real tool
    round can execute it instead of consuming it as a discarded classifier
    response.
    """

    decision_prompt = (
        "Decide whether the CURRENT user request requires external tool/capability execution.\n"
        "Return ONLY compact JSON with this shape: "
        '{"use_tools": true|false, "reason": "short reason"}\n\n'
        "Use tools only when the request requires observing or changing external state, "
        "such as device state, screen contents, files, browsing, server status, approvals, or physical devices.\n"
        "Do not use tools for greetings, simple conversation, translation, or requests that can be answered directly.\n\n"
        f"CURRENT user request:\n{user_message}"
    )
    try:
        result = llm.generate(
            prompt=decision_prompt,
            system_prompt=(
                system_prompt
                + "\n\nFor this decision, ignore previous conversation except where the current request explicitly refers to it."
            ),
            max_tokens=120,
            context_meta=context_meta,
        )
    except Exception:
        logger.debug("Tool-use decision failed", exc_info=True)
        return None, None
    if not getattr(result, "success", False):
        return None, None
    content = (getattr(result, "content", "") or "").strip()
    parsed_tool_call = _parse_tool_call(content)
    if parsed_tool_call is not None:
        return True, parsed_tool_call
    match = re.search(r"\{.*\}", content, flags=re.S)
    if not match:
        return None, None
    try:
        data = json.loads(match.group(0))
    except Exception:
        return None, None
    value = data.get("use_tools")
    return (value if isinstance(value, bool) else None), None


def _generate_direct_response(
    llm: Any,
    user_message: str,
    *,
    system_prompt: str,
    context_meta: dict[str, Any] | None = None,
    max_tokens: int = 1000,
) -> str:
    """Generate a non-tool response once (no empty-success double call)."""

    result = llm.generate(
        prompt=user_message,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        context_meta=context_meta,
    )
    if result.success and (result.content or "").strip():
        return result.content.strip()
    if not result.success:
        return f"LLM error: {result.error}"
    return "応答生成が空で返りました。もう一度送信してください。"


def _llm_response_satisfies_without_tools(
    llm: Any,
    user_message: str,
    response: str,
    *,
    context_meta: dict[str, Any] | None = None,
) -> bool | None:
    """Ask the LLM whether a no-tool response actually completes the request."""

    prompt = (
        "Judge whether the assistant response fully satisfies the CURRENT user request without external tools.\n"
        "Return ONLY compact JSON: "
        '{"satisfies": true|false, "reason": "short reason"}\n\n'
        "Return false if the response merely says it will do something, asks the user to wait, "
        "or claims it will check/inspect/execute without providing the result.\n"
        "If the user asked to observe external state, return true only when the response contains "
        "the actual observed state or a clear completed error/permission result.\n"
        "When uncertain, return false.\n\n"
        f"CURRENT user request:\n{user_message}\n\n"
        f"Assistant response:\n{response}"
    )
    try:
        result = llm.generate(
            prompt=prompt,
            system_prompt="You are a strict evaluator of task completion.",
            max_tokens=120,
            context_meta=context_meta,
        )
    except Exception:
        logger.debug("No-tool response satisfaction check failed", exc_info=True)
        return None
    if not getattr(result, "success", False):
        return None
    content = (getattr(result, "content", "") or "").strip()
    match = re.search(r"\{.*\}", content, flags=re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except Exception:
        return None
    value = data.get("satisfies")
    return value if isinstance(value, bool) else None


def call_llm_with_tools(
    llm,
    user_message: str,
    system_prompt: str,
    catalog=None,
    max_tool_rounds: int = 15,
    context_meta: dict[str, Any] | None = None,
    runtime: Any = None,
) -> dict[str, Any]:
    context_meta = dict(context_meta or {})
    context_meta.setdefault("original_user_message", user_message)
    audit_group_id = str(
        context_meta.get("audit_group_id")
        or context_meta.get("chat_task_id")
        or context_meta.get("task_id")
        or ""
    )
    if audit_group_id and not context_meta.get("_audit_group_active"):
        from aegis_ai.audit.context import audit_group

        context_meta["audit_group_id"] = audit_group_id
        context_meta["audit_group_type"] = str(context_meta.get("audit_group_type") or "chat")
        context_meta["audit_group_title"] = str(
            context_meta.get("audit_group_title") or f"Chat: {user_message[:80]}"
        )
        context_meta["_audit_group_active"] = True
        with audit_group(
            audit_group_id,
            group_type=context_meta["audit_group_type"],
            group_title=context_meta["audit_group_title"],
        ):
            return call_llm_with_tools(
                llm,
                user_message,
                system_prompt,
                catalog=catalog,
                max_tool_rounds=max_tool_rounds,
                context_meta=context_meta,
                runtime=runtime,
            )
    if runtime is None:
        try:
            from aegis_ai.runtime import get_runtime

            runtime = get_runtime()
        except Exception:
            runtime = None
    if catalog is None:
        catalog = runtime.capability_catalog if runtime is not None else get_catalog()

    selection_runtime = (
        runtime
        if runtime is not None and getattr(runtime, "capability_catalog", None) is catalog
        else None
    )
    selection = get_capability_selection(
        catalog,
        user_message=user_message,
        session_context=context_meta,
        runtime=selection_runtime,
    )
    lightweight_catalog = selection.lightweight_catalog if selection is not None else []
    tools = selection.tools if selection is not None else get_tools_for_chat(
        catalog,
        user_message=user_message,
        session_context=context_meta,
        runtime=selection_runtime,
    )
    if runtime is not None and getattr(runtime, "presentation_manager", None) is not None:
        tools = list(tools)
        tools.append(_presentation_tool_definition())
    context_meta = _with_usage_breakdown(
        context_meta,
        system_prompt=system_prompt,
        tools=tools,
        user_message=user_message,
    )
    if not tools:
        response = _generate_direct_response(
            llm,
            user_message,
            system_prompt=system_prompt,
            context_meta=context_meta,
        )
        return {
            "response": response,
            "tool_calls": [],
            "tool_results": [],
        }

    wants_tools, pending_tool_call = _llm_wants_tools(
        llm,
        user_message,
        system_prompt=system_prompt,
        context_meta=context_meta,
    )
    decision_returned_tool_call = pending_tool_call is not None
    if wants_tools is False:
        response = _generate_direct_response(
            llm,
            user_message,
            system_prompt=system_prompt,
            context_meta=context_meta,
        )
        satisfies = _llm_response_satisfies_without_tools(
            llm,
            user_message,
            response,
            context_meta=context_meta,
        )
        if satisfies is not False:
            return {
                "response": response,
                "tool_calls": [],
                "tool_results": [],
            }
        wants_tools = True

    valid_tool_names: set[str] = {t['function']['name'] for t in tools}
    valid_tool_names.add("ask_user")

    all_tool_calls = []
    all_tool_results = []
    conversation_history = []
    executed_call_signatures: set[str] = set()
    final_response = ""
    for round_num in range(max_tool_rounds):
        tool_list = "\n".join(f"- {t['function']['name']}: {t['function']['description']}" for t in tools)
        current_prompt = _build_tool_loop_prompt(
            user_message=user_message,
            tool_list=tool_list,
            lightweight_catalog=lightweight_catalog,
            conversation_history=conversation_history,
        )
        if round_num == 0 and pending_tool_call is not None:
            tc = pending_tool_call if pending_tool_call.get("name") in valid_tool_names else None
            result = type("_ToolDecisionResult", (), {"success": True, "content": ""})()
            pending_tool_call = None
        else:
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
            # Do not double-call solely because round-0 returned empty text.
            # Only force another tool step when prior tool results still need work.
            should_force_tool = False
            if not content.strip() and all_tool_results and round_num < max_tool_rounds - 1:
                should_force_tool = True
            if content.strip() and (round_num == 0 or not decision_returned_tool_call):
                satisfies = _llm_response_satisfies_without_tools(
                    llm,
                    user_message,
                    content.strip(),
                    context_meta=context_meta,
                )
                if (
                    (satisfies is False or (satisfies is None and all_tool_results))
                    and round_num < max_tool_rounds - 1
                ):
                    should_force_tool = True

            if should_force_tool:
                retry_prompt = (
                    current_prompt
                    + "\n\nThe previous assistant response did not complete the CURRENT request. "
                    "External tools are required to produce the requested result. "
                    "Choose the best available full-schema tool now. Respond with only one <tool_call> JSON block."
                )
                result, tc = _generate_tool_step(
                    llm=llm,
                    prompt=retry_prompt,
                    system_prompt=system_prompt,
                    tools=tools,
                    valid_tool_names=valid_tool_names,
                    context_meta=context_meta,
                )
                content = result.content or "" if getattr(result, "success", False) else ""
                if not getattr(result, "success", False):
                    return {"response": f"LLM error: {result.error}", "tool_calls": [], "tool_results": []}
                if tc is not None:
                    pass
                elif not content.strip():
                    return {
                        "response": "ツールが必要な依頼として解釈しましたが、実行するツールを選択できませんでした。もう一度、対象を少し具体的に指定してください。",
                        "tool_calls": [],
                        "tool_results": [],
                    }
            if round_num == 0:
                if tc is None:
                    return {"response": content, "tool_calls": [], "tool_results": []}
            if tc is None:
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

        call_signature = json.dumps({"name": func_name, "arguments": args}, sort_keys=True, ensure_ascii=False)
        if call_signature in executed_call_signatures:
            logger.info("Stopping repeated chat tool call: %s", func_name)
            break
        executed_call_signatures.add(call_signature)

        tool_call_info = {"function": func_name, "arguments": args}
        all_tool_calls.append(tool_call_info)
        conversation_history.append({
            "role": "assistant_tool_call",
            "name": func_name,
            "arguments": json.dumps(args, ensure_ascii=False),
        })

        _emit_event(runtime, "tool.execution.started", status="started",
                    tool_id=func_name, reason=f"?????: {func_name}")
        tool_result = _execute_tool_call(catalog, func_name, args, runtime=runtime, tool_context=context_meta)
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

        if tool_result.get("approval_needed"):
            approval_id = tool_result.get("approval_id", "")
            return {
                "response": f"承認が必要です。Approvals で承認してください。approval_id={approval_id}",
                "tool_calls": all_tool_calls,
                "tool_results": all_tool_results,
                "approval_needed": True,
                "approval_id": approval_id,
            }

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
        "Important: use the current tool success/error status as authoritative. "
        "Visible text from a UI tree may include old chat messages; do not treat old visible chat text as the current permission state."
    )
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
