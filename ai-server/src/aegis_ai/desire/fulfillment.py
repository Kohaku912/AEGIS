"""Desire fulfillment evaluation.

The autonomous loop uses this module after a capability runs. Fulfillment is
always judged by an LLM evaluator. If the evaluator is unavailable, the result
is intentionally left unjudged so desire values and pressure are not reduced by
local heuristics.
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
    fulfillment_score: float = 0.0
    pressure_reduction: float = 0.0
    desire_delta_hint: dict[str, float] = field(default_factory=dict)
    summary: str = ""
    confidence: float = 0.0
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

    LLM evaluation is mandatory. If no evaluator can provide a valid judgement,
    return a blocked result with zero pressure/desire changes.
    """

    metadata = capability_metadata or {}
    if llm_provider is not None and hasattr(llm_provider, "generate"):
        try:
            llm_result = _evaluate_with_llm(
                llm_provider=llm_provider,
                capability_id=capability_id,
                tool_success=tool_success,
                desire_name=desire_name,
                output=output,
                capability_metadata=metadata,
            )
            if llm_result is not None:
                return llm_result
        except Exception as exc:
            logger.warning("LLM desire fulfillment evaluation failed: %s", exc)

    return _unavailable_result(tool_success=tool_success, reason="evaluator_unavailable")


def _evaluate_with_llm(
    *,
    llm_provider: Any,
    capability_id: str,
    tool_success: bool,
    desire_name: str,
    output: dict[str, Any],
    capability_metadata: dict[str, Any],
) -> TaskResult | None:
    prompt = {
        "instruction": (
            "Classify whether this capability result fulfilled the target desire. "
            "Return JSON only with keys task_effect, fulfillment_score, pressure_reduction, "
            "desire_delta_hint, summary, and confidence. "
            "task_effect must be one of useful, no_effect, failed, blocked, needs_followup. "
            "fulfillment_score, pressure_reduction, and confidence must be numbers from 0.0 to 1.0. "
            "Do not infer from stock phrases alone. Judge the structured result, target desire, "
            "and capability metadata. Capability ID is only an identifier; do not classify by its text."
        ),
        "target_desire": desire_name,
        "capability_id": capability_id,
        "tool_success": bool(tool_success),
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
    pressure_reduction = _bounded_float(data.get("pressure_reduction"), default=0.0)
    fulfillment_score = _bounded_float(data.get("fulfillment_score"), default=0.0)
    confidence = _bounded_float(data.get("confidence"), default=0.0)
    return TaskResult(
        tool_success=bool(tool_success),
        task_effect=effect,
        fulfillment_score=fulfillment_score,
        pressure_reduction=pressure_reduction,
        desire_delta_hint=deltas,
        summary=summary,
        confidence=confidence,
        details={
            "evaluator": "llm",
            "raw_effect": data.get("task_effect"),
            "raw_pressure_reduction": data.get("pressure_reduction"),
            "raw_fulfillment_score": data.get("fulfillment_score"),
            "raw_confidence": data.get("confidence"),
        },
    )


def _unavailable_result(*, tool_success: bool, reason: str) -> TaskResult:
    return TaskResult(
        tool_success=tool_success,
        task_effect=TaskEffect.BLOCKED,
        fulfillment_score=0.0,
        pressure_reduction=0.0,
        desire_delta_hint={},
        summary="Desire fulfillment was not judged because the LLM evaluator was unavailable.",
        confidence=0.0,
        details={"evaluator": "unavailable", "reason": reason},
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


def _bounded_float(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


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
