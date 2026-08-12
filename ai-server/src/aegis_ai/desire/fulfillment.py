"""Desire fulfillment evaluation.

Prefer an LLM evaluator; on parse failure retry once, then fall back to
structured fields only (tool_success / error / empty counts) — never
keyword-match user text.
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
            "read_new_posts": 0.0,
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
    desire_goal: str = "",
) -> TaskResult:
    """Evaluate the effect of a tool execution on a desire."""

    metadata = capability_metadata or {}
    if llm_provider is not None and hasattr(llm_provider, "generate"):
        try:
            llm_result = _evaluate_with_llm(
                llm_provider=llm_provider,
                capability_id=capability_id,
                tool_success=tool_success,
                desire_name=desire_name,
                desire_goal=desire_goal,
                output=output,
                capability_metadata=metadata,
                retry_on_parse_error=True,
            )
            if llm_result is not None:
                return llm_result
        except Exception as exc:
            logger.warning("LLM desire fulfillment evaluation failed: %s", exc)

    structural = _structural_fallback(
        capability_id=capability_id,
        tool_success=tool_success,
        output=output if isinstance(output, dict) else {},
        desire_name=desire_name,
    )
    if structural is not None:
        return structural

    return _unavailable_result(tool_success=tool_success, reason="evaluator_unavailable")


def _evaluate_with_llm(
    *,
    llm_provider: Any,
    capability_id: str,
    tool_success: bool,
    desire_name: str,
    desire_goal: str,
    output: dict[str, Any],
    capability_metadata: dict[str, Any],
    retry_on_parse_error: bool = False,
) -> TaskResult | None:
    desire_rubric = DESIRE_FULFILLMENT.get(desire_name, {})
    prompt = {
        "instruction": (
            "Judge whether this action would feel meaningfully fulfilling to a human "
            "for the target desire — not whether the tool merely succeeded. "
            "Return JSON only with keys task_effect, fulfillment_score, pressure_reduction, "
            "desire_delta_hint, summary, and confidence. "
            "task_effect must be one of useful, no_effect, failed, blocked, needs_followup. "
            "fulfillment_score, pressure_reduction, and confidence must be numbers from 0.0 to 1.0. "
            "Rules: "
            "(1) tool_success=true alone is NEVER enough for useful or for pressure_reduction>0. "
            "(2) Passive inventory/list/read/check that finds nothing new, nothing actionable, or only "
            "already-known state → task_effect=no_effect, pressure_reduction=0. "
            "(3) useful only when there is human-felt value: new useful information, a real reply "
            "to someone, progress on a user request/commitment, a lasting learning, or a creative "
            "output that advances the desire goal. "
            "(4) If the result only enables a later decision, use needs_followup with "
            "pressure_reduction=0. "
            "Do not classify by capability ID text. Judge the structured result, desire goal, "
            "and capability metadata."
        ),
        "target_desire": desire_name,
        "desire_goal": desire_goal,
        "desire_rubric": desire_rubric,
        "capability_id": capability_id,
        "tool_success": bool(tool_success),
        "capability_metadata": _compact_value(capability_metadata),
        "tool_result": _compact_value(output),
        "allowed_desires": list(DESIRE_FULFILLMENT),
    }
    prompt_text = json.dumps(prompt, ensure_ascii=False)

    def _call(text: str, caller: str) -> Any:
        try:
            return llm_provider.generate(
                prompt=text,
                system_prompt=(
                    "You are AEGIS desire fulfillment evaluator. "
                    "Judge human-felt value, not tool success. Return compact JSON only."
                ),
                max_tokens=2048,
                temperature=0.0,
                json_mode=True,
                profile="decision",
                context_meta={"caller": caller},
            )
        except TypeError:
            return llm_provider.generate(
                prompt=text,
                system_prompt=(
                    "You are AEGIS desire fulfillment evaluator. "
                    "Judge human-felt value, not tool success. Return compact JSON only."
                ),
                max_tokens=2048,
                temperature=0.0,
            )

    response = _call(prompt_text, "desire_fulfillment")
    if not getattr(response, "success", False):
        return None
    content = getattr(response, "content", "") or ""
    if not str(content).strip():
        # Reasoning-only / empty completions are common; fall through to structural
        # without treating empty output as a hard JSON error.
        logger.warning(
            "LLM desire fulfillment returned empty content (finish_reason=%s); using structural fallback",
            getattr(response, "finish_reason", ""),
        )
        return None
    try:
        data = extract_json_object(content)
    except Exception as exc:
        logger.warning("LLM desire fulfillment returned non-JSON: %s | content: %s", exc, content[:500])
        if not retry_on_parse_error:
            return None
        repair = (
            prompt_text
            + "\n\nPrevious response was not valid JSON. Reply with a single JSON object only. "
            "No prose, no markdown fences."
        )
        try:
            response = _call(repair, "desire_fulfillment_retry")
            if not getattr(response, "success", False):
                return None
            retry_content = getattr(response, "content", "") or ""
            if not str(retry_content).strip():
                logger.warning("Fulfillment JSON retry returned empty content")
                return None
            data = extract_json_object(retry_content)
        except Exception as retry_exc:
            logger.warning("Fulfillment JSON retry failed: %s", retry_exc)
            return None

    effect = _parse_effect(data.get("task_effect"))
    if effect is None:
        logger.warning(
            "LLM desire fulfillment returned invalid task_effect: %s | data: %s",
            data.get("task_effect"),
            data,
        )
        return None
    summary = str(data.get("summary") or f"LLM classified result as {effect.value}")[:500]
    deltas = _sanitize_deltas(data.get("desire_delta_hint"), desire_name)
    pressure_reduction = _bounded_float(data.get("pressure_reduction"), default=0.0)
    fulfillment_score = _bounded_float(data.get("fulfillment_score"), default=0.0)
    confidence = _bounded_float(data.get("confidence"), default=0.0)
    # Only confident useful outcomes may drain pressure. Weak "useful" labels on
    # re-reads / empty inventories are coerced to no_effect.
    if effect == TaskEffect.USEFUL and fulfillment_score < 0.5:
        effect = TaskEffect.NO_EFFECT
        pressure_reduction = 0.0
        summary = (
            f"Downgraded weak useful (score={fulfillment_score:.2f}) to no_effect: {summary}"
        )[:500]
        fulfillment_score = min(fulfillment_score, 0.49)
    elif effect != TaskEffect.USEFUL:
        pressure_reduction = 0.0
        fulfillment_score = min(fulfillment_score, 0.49)
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
            "desire_goal": desire_goal,
        },
    )


def _structural_fallback(
    *,
    capability_id: str,
    tool_success: bool,
    output: dict[str, Any],
    desire_name: str,
) -> TaskResult | None:
    """Classify from structured fields only — never claim fulfillment without LLM judgment.

    Structural paths may fail/block/flag follow-up, but pressure_reduction is always 0.0.
    Only the LLM evaluator may mark USEFUL and drain desire pressure.
    """
    error = output.get("error")
    if not tool_success or error:
        return TaskResult(
            tool_success=False,
            task_effect=TaskEffect.FAILED,
            fulfillment_score=0.0,
            pressure_reduction=0.0,
            desire_delta_hint={desire_name: -0.1} if desire_name else {},
            summary=f"Tool failed for {capability_id}",
            confidence=0.4,
            details={"evaluator": "structural", "reason": "tool_error"},
        )

    count = output.get("count")
    if count == 0:
        return _empty_structural_result(capability_id=capability_id, desire_name=desire_name)
    for key in ("unread_count", "batched_count", "due_count"):
        if output.get(key) == 0:
            return _empty_structural_result(capability_id=capability_id, desire_name=desire_name)
    for key in ("items", "posts", "commitments", "results", "batched", "files"):
        val = output.get(key)
        if val == [] or val == ():
            return _empty_structural_result(capability_id=capability_id, desire_name=desire_name)
    nested = output.get("result")
    if isinstance(nested, dict) and _is_structurally_empty(nested):
        return _empty_structural_result(capability_id=capability_id, desire_name=desire_name)

    if output.get("action_state") == "awaiting_approval":
        return TaskResult(
            tool_success=bool(tool_success),
            task_effect=TaskEffect.BLOCKED,
            fulfillment_score=0.0,
            pressure_reduction=0.0,
            desire_delta_hint={},
            summary="Awaiting approval — desire not fulfilled yet",
            confidence=0.7,
            details={"evaluator": "structural", "reason": "awaiting_approval"},
        )

    if tool_success and output:
        return TaskResult(
            tool_success=True,
            task_effect=TaskEffect.NEEDS_FOLLOWUP,
            fulfillment_score=0.0,
            pressure_reduction=0.0,
            desire_delta_hint={},
            summary="Structural success without LLM judgement; desire not reduced",
            confidence=0.3,
            details={"evaluator": "structural", "reason": "tool_success_fallback"},
        )
    return None


def _is_structurally_empty(output: dict[str, Any]) -> bool:
    for key in ("count", "unread_count", "batched_count", "due_count"):
        if output.get(key) == 0:
            return True
    for key in ("items", "posts", "commitments", "results", "batched", "files"):
        val = output.get(key)
        if val == [] or val == ():
            return True
    nested = output.get("result")
    return isinstance(nested, dict) and _is_structurally_empty(nested)


def _empty_structural_result(*, capability_id: str, desire_name: str) -> TaskResult:
    return TaskResult(
        tool_success=True,
        task_effect=TaskEffect.NO_EFFECT,
        fulfillment_score=0.0,
        pressure_reduction=0.0,
        desire_delta_hint={},
        summary="Structured empty result — no human-felt fulfillment",
        confidence=0.45,
        details={"evaluator": "structural", "reason": "empty_result", "capability_id": capability_id},
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
