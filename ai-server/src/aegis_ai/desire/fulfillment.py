"""Desire fulfillment evaluation.

The autonomous loop uses this module after a capability runs.  The preferred
path is an LLM evaluator that receives the structured tool result and returns a
small JSON classification.  If the LLM is unavailable, fallback logic only uses
structured fields such as success flags and counts; it does not scan natural
language result text.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from aegis_ai.llm.json_utils import extract_json_object

logger = logging.getLogger("aegis_ai.desire.fulfillment")


class TaskEffect(str, Enum):
    """Classification of task effect on desires."""

    USEFUL = "useful"
    NO_EFFECT = "no_effect"
    FAILED = "failed"
    BLOCKED = "blocked"
    NEEDS_FOLLOWUP = "needs_followup"


@dataclass
class TaskResult:
    """Structured task result for desire evaluation."""

    tool_success: bool = False
    task_effect: TaskEffect = TaskEffect.NO_EFFECT
    desire_delta_hint: dict[str, float] = field(default_factory=dict)
    summary: str = ""
    details: dict[str, Any] = field(default_factory=dict)


DESIRE_FULFILLMENT = {
    "user_support": {
        "description": "Completing user requests and being helpful",
        "conditions": {
            "user_request_completed": 0.8,
            "mention_reply_created": 0.5,
            "useful_info_provided": 0.4,
            "task_partially_done": 0.3,
            "no_action_needed": 0.0,
            "tool_error": -0.3,
        },
    },
    "social": {
        "description": "Social interactions, with posting/replying stronger than passive reading",
        "conditions": {
            "posted_to_agora": 1.0,
            "replied_to_mention": 0.9,
            "read_new_posts": 0.1,
            "reactions_received": 0.5,
            "no_new_posts": 0.0,
            "tool_error": -0.3,
        },
    },
    "growth": {
        "description": "Learning, exploration, creativity, and reflection",
        "conditions": {
            "new_info_summarized": 0.5,
            "interesting_discovery": 0.6,
            "web_search_results": 0.3,
            "creative_output": 0.6,
            "meaningful_action": 0.5,
            "goal_progress": 0.4,
            "learned_new_skill": 0.6,
            "knowledge_applied": 0.4,
            "empty_results": 0.0,
            "no_progress": 0.0,
            "tool_error": -0.2,
        },
    },
}


def evaluate_task_result(
    capability_id: str,
    tool_success: bool,
    output: dict[str, Any],
    desire_name: str = "",
    *,
    llm_provider: Any = None,
    capability_metadata: dict[str, Any] | None = None,
) -> TaskResult:
    """Evaluate the effect of a tool execution on a desire.

    LLM evaluation is used when available.  Fallback classification deliberately
    ignores natural-language result strings and relies only on structured fields.
    """

    if not tool_success:
        return _failed_result(output, desire_name)

    metadata = capability_metadata or {}
    if llm_provider is not None and hasattr(llm_provider, "generate"):
        try:
            llm_result = _evaluate_with_llm(
                llm_provider=llm_provider,
                capability_id=capability_id,
                desire_name=desire_name,
                output=output,
                capability_metadata=metadata,
            )
            if llm_result is not None:
                return llm_result
        except Exception as exc:
            logger.warning("LLM desire fulfillment evaluation failed: %s", exc)

    return _fallback_evaluate_structured(
        capability_id=capability_id,
        output=output,
        desire_name=desire_name,
        capability_metadata=metadata,
    )


def _failed_result(output: dict[str, Any], desire_name: str) -> TaskResult:
    result = TaskResult(tool_success=False, task_effect=TaskEffect.FAILED)
    result.summary = "Tool execution failed"
    error = output.get("error") or output.get("message") or output.get("status")
    result.details = {"error": str(error)[:500] if error is not None else "unknown"}
    if desire_name and desire_name in DESIRE_FULFILLMENT:
        conditions = DESIRE_FULFILLMENT[desire_name]["conditions"]
        result.desire_delta_hint[desire_name] = conditions.get("tool_error", -0.3)
    return result


def _evaluate_with_llm(
    *,
    llm_provider: Any,
    capability_id: str,
    desire_name: str,
    output: dict[str, Any],
    capability_metadata: dict[str, Any],
) -> TaskResult | None:
    prompt = {
        "instruction": (
            "Classify whether this capability result fulfilled the target desire. "
            "Return JSON only with keys task_effect, summary, and desire_delta_hint. "
            "task_effect must be one of useful, no_effect, failed, blocked, needs_followup. "
            "Do not infer from stock phrases alone; judge the structured result and capability metadata."
        ),
        "target_desire": desire_name,
        "capability_id": capability_id,
        "capability_metadata": _compact_value(capability_metadata),
        "tool_result": _compact_value(output),
        "allowed_desires": list(DESIRE_FULFILLMENT),
    }
    prompt_text = json.dumps(prompt, ensure_ascii=False)
    try:
        response = llm_provider.generate(
            prompt=prompt_text,
            system_prompt="You are AEGIS desire fulfillment evaluator. Return compact JSON only.",
            max_tokens=300,
            temperature=0.0,
            json_mode=True,
            profile="decision",
            context_meta={"caller": "desire_fulfillment"},
        )
    except TypeError:
        response = llm_provider.generate(
            prompt=prompt_text,
            system_prompt="You are AEGIS desire fulfillment evaluator. Return compact JSON only.",
            max_tokens=300,
            temperature=0.0,
        )
    if not getattr(response, "success", False):
        return None
    data = extract_json_object(getattr(response, "content", "") or "")
    effect = _parse_effect(data.get("task_effect"))
    if effect is None:
        return None
    summary = str(data.get("summary") or f"LLM classified result as {effect.value}")[:500]
    deltas = _sanitize_deltas(data.get("desire_delta_hint"), desire_name)
    if not deltas:
        deltas = _default_deltas_for_effect(effect, desire_name, capability_id, output, capability_metadata)
    return TaskResult(
        tool_success=True,
        task_effect=effect,
        desire_delta_hint=deltas,
        summary=summary,
        details={"evaluator": "llm", "raw_effect": data.get("task_effect")},
    )


def _fallback_evaluate_structured(
    *,
    capability_id: str,
    output: dict[str, Any],
    desire_name: str,
    capability_metadata: dict[str, Any],
) -> TaskResult:
    structured = _primary_structured_output(output)
    if _structured_failure(structured):
        result = _failed_result(output, desire_name)
        result.tool_success = True
        result.details["fallback_reason"] = "structured_failure_flag"
        return result

    if _structured_needs_followup(structured):
        effect = TaskEffect.NEEDS_FOLLOWUP
        summary = "Action succeeded and structured output indicates follow-up is needed"
    elif _structured_empty(structured):
        effect = TaskEffect.NO_EFFECT
        summary = "Action succeeded but structured output contains no new items"
    else:
        effect = TaskEffect.USEFUL
        summary = "Action produced a structured result"

    return TaskResult(
        tool_success=True,
        task_effect=effect,
        desire_delta_hint=_default_deltas_for_effect(effect, desire_name, capability_id, structured, capability_metadata),
        summary=summary,
        details={"evaluator": "structured_fallback"},
    )


def _parse_effect(value: Any) -> TaskEffect | None:
    if value is None:
        return None
    try:
        return TaskEffect(str(value).strip().lower())
    except ValueError:
        return None


def _sanitize_deltas(value: Any, desire_name: str) -> dict[str, float]:
    if not isinstance(value, dict):
        return {}
    deltas: dict[str, float] = {}
    for key, raw in value.items():
        if key not in DESIRE_FULFILLMENT:
            continue
        if desire_name and key != desire_name:
            continue
        try:
            deltas[key] = max(-1.0, min(1.0, float(raw)))
        except (TypeError, ValueError):
            continue
    return deltas


def _default_deltas_for_effect(
    effect: TaskEffect,
    desire_name: str,
    capability_id: str,
    output: dict[str, Any],
    capability_metadata: dict[str, Any],
) -> dict[str, float]:
    if not desire_name or desire_name not in DESIRE_FULFILLMENT:
        return {}
    if effect == TaskEffect.NO_EFFECT:
        return {desire_name: 0.0}
    if effect == TaskEffect.FAILED:
        return {desire_name: DESIRE_FULFILLMENT[desire_name]["conditions"].get("tool_error", -0.2)}
    if effect == TaskEffect.BLOCKED:
        return {desire_name: 0.0}

    base = _base_delta_for_capability(desire_name, capability_id, output, capability_metadata)
    if effect == TaskEffect.NEEDS_FOLLOWUP:
        base *= 0.5
    return {desire_name: base}


def _base_delta_for_capability(
    desire_name: str,
    capability_id: str,
    output: dict[str, Any],
    capability_metadata: dict[str, Any],
) -> float:
    conditions = DESIRE_FULFILLMENT[desire_name]["conditions"]
    operation_category = str(capability_metadata.get("operation_category") or "")
    side_effects = capability_metadata.get("side_effects") or []
    if not isinstance(side_effects, list):
        side_effects = [str(side_effects)]

    if desire_name == "social":
        if "post" in operation_category or capability_id.endswith(".post") or output.get("posted") is True:
            return conditions.get("posted_to_agora", 1.0)
        if _structured_count(output) > 0:
            return conditions.get("read_new_posts", 0.1)
        return conditions.get("no_new_posts", 0.0)
    if desire_name == "growth":
        if "browse" in operation_category or "research" in operation_category:
            return conditions.get("web_search_results", 0.3)
        if "workspace" in capability_id or "memory" in capability_id:
            return conditions.get("new_info_summarized", 0.5)
        return conditions.get("meaningful_action", 0.5)
    if desire_name == "user_support":
        if any(effect in {"draft_creation", "notification", "support"} for effect in side_effects):
            return conditions.get("useful_info_provided", 0.4)
        return conditions.get("task_partially_done", 0.3)
    return 0.2


def _primary_structured_output(output: dict[str, Any]) -> dict[str, Any]:
    nested = output.get("result")
    if isinstance(nested, dict):
        merged = dict(output)
        merged.update(nested)
        return merged
    return output


def _structured_failure(output: dict[str, Any]) -> bool:
    for key in ("ok", "success", "completed"):
        if key in output and output.get(key) is False:
            return True
    status = output.get("status")
    return isinstance(status, str) and status.lower() in {"error", "failed", "blocked", "denied"}


def _structured_needs_followup(output: dict[str, Any]) -> bool:
    if output.get("needs_followup") is True or output.get("requires_followup") is True:
        return True
    followups = output.get("followups") or output.get("next_actions")
    return isinstance(followups, list) and len(followups) > 0


def _structured_empty(output: dict[str, Any]) -> bool:
    count_keys = ("unread_count", "count", "total", "total_count", "new_count", "match_count")
    for key in count_keys:
        if key in output:
            try:
                return int(output.get(key) or 0) == 0
            except (TypeError, ValueError):
                pass
    list_keys = ("items", "posts", "results", "matches", "files", "notifications", "events")
    for key in list_keys:
        if key in output and isinstance(output.get(key), list):
            return len(output[key]) == 0
    return False


def _structured_count(output: dict[str, Any]) -> int:
    for key in ("unread_count", "count", "total", "total_count", "new_count", "match_count"):
        if key in output:
            try:
                return int(output.get(key) or 0)
            except (TypeError, ValueError):
                return 0
    for key in ("items", "posts", "results", "matches", "files", "notifications", "events"):
        if key in output and isinstance(output.get(key), list):
            return len(output[key])
    return 1


def _compact_value(value: Any, depth: int = 0) -> Any:
    if depth > 4:
        return "<max_depth>"
    if isinstance(value, dict):
        compact: dict[str, Any] = {}
        for key, item in list(value.items())[:40]:
            if str(key) in {"image_base64", "image_data"}:
                compact[str(key)] = f"<image:{len(str(item))} chars>"
            else:
                compact[str(key)] = _compact_value(item, depth + 1)
        if len(value) > 40:
            compact["_truncated_keys"] = len(value) - 40
        return compact
    if isinstance(value, list):
        return [_compact_value(item, depth + 1) for item in value[:20]]
    if isinstance(value, str) and len(value) > 1000:
        return value[:1000] + f"... <truncated {len(value) - 1000} chars>"
    return value


def is_health_alert(capability_id: str, result_text: str) -> bool:
    """Legacy compatibility hook.

    Desire fulfillment no longer classifies health alerts from natural-language
    text. HealthAlertManager owns health classification.
    """

    return False
