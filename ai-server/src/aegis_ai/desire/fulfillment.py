"""Desire Fulfillment Rules — defines how actions fulfill desires.

Each desire has specific conditions that determine how much it was fulfilled.
Used by the autonomous loop and chat path to evaluate task results.

3 desires: user_support, social, growth.
Health-related conditions (reliability, maintenance, system_safety) are now
handled by HealthAlertManager, not desire fulfillment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskEffect(str, Enum):
    """Classification of task effect on desires."""
    USEFUL = "useful"           # Action produced useful result
    NO_EFFECT = "no_effect"     # Action succeeded but no meaningful effect
    FAILED = "failed"           # Action failed (tool error)
    BLOCKED = "blocked"         # Action blocked by policy
    NEEDS_FOLLOWUP = "needs_followup"  # Action succeeded but needs follow-up


@dataclass
class TaskResult:
    """Structured task result for desire evaluation."""
    tool_success: bool = False
    task_effect: TaskEffect = TaskEffect.NO_EFFECT
    desire_delta_hint: dict[str, float] = field(default_factory=dict)
    summary: str = ""
    details: dict[str, Any] = field(default_factory=dict)


# Desire fulfillment conditions per desire type (3 consolidated desires)
DESIRE_FULFILLMENT = {
    "user_support": {
        "description": "Fulfilled by completing user requests and being helpful",
        "conditions": {
            "user_request_completed": 0.8,      # User's explicit request actually completed
            "mention_reply_created": 0.5,        # Created reply to mention
            "useful_info_provided": 0.4,         # Provided useful information
            "task_partially_done": 0.3,          # Task partially completed
            "no_action_needed": 0.0,             # No action was needed
            "tool_error": -0.3,                  # Tool execution failed
        },
    },
    "social": {
        "description": "Fulfilled by social interactions (posting is primary, reading barely satisfies)",
        "conditions": {
            "posted_to_agora": 1.0,              # Actually posted to AGORA (maximum satisfaction)
            "replied_to_mention": 0.9,           # Replied to someone who mentioned AEGIS
            "read_new_posts": 0.1,               # Read new posts (passive, barely satisfies)
            "reactions_received": 0.5,           # Got reactions on posts (meaningful but less than posting)
            "no_new_posts": 0.0,                 # No new posts
            "tool_error": -0.3,                  # Tool error
        },
    },
    "growth": {
        "description": "Fulfilled by learning, exploration, creativity, and reflection",
        "conditions": {
            "new_info_summarized": 0.5,          # Got new info, summarized and saved
            "interesting_discovery": 0.6,        # Found something genuinely interesting
            "web_search_results": 0.3,           # Got useful web search results
            "creative_output": 0.6,              # Produced creative content
            "meaningful_action": 0.5,            # Took meaningful action
            "goal_progress": 0.4,                # Made progress toward a goal
            "learned_new_skill": 0.6,            # Learned something new
            "knowledge_applied": 0.4,            # Applied existing knowledge
            "empty_results": 0.0,                # Search returned nothing useful
            "no_progress": 0.0,                  # No progress made
            "tool_error": -0.2,                  # Tool error
        },
    },
}


def evaluate_task_result(
    capability_id: str,
    tool_success: bool,
    output: dict[str, Any],
    desire_name: str = "",
) -> TaskResult:
    """Evaluate a task result and determine its effect on desires.

    Args:
        capability_id: The capability that was executed
        tool_success: Whether the tool execution succeeded
        output: The tool output
        desire_name: The desire this task was targeting

    Returns:
        TaskResult with tool_success, task_effect, and desire_delta_hint
    """
    result = TaskResult(tool_success=tool_success)

    if not tool_success:
        result.task_effect = TaskEffect.FAILED
        result.summary = f"Tool execution failed: {output.get('error', 'unknown')}"
        if desire_name and desire_name in DESIRE_FULFILLMENT:
            conditions = DESIRE_FULFILLMENT[desire_name]["conditions"]
            result.desire_delta_hint[desire_name] = conditions.get("tool_error", -0.3)
        return result

    # Tool succeeded - classify the effect
    result_text = str(output.get("result", "")).lower()

    # Check for empty/no-effect results
    if _is_no_effect(result_text, capability_id):
        result.task_effect = TaskEffect.NO_EFFECT
        result.summary = "Action succeeded but had no meaningful effect"
        result.desire_delta_hint = _get_no_effect_deltas(desire_name)
        return result

    # Check for useful results
    if _is_useful(result_text, capability_id, output):
        result.task_effect = TaskEffect.USEFUL
        result.summary = "Action produced useful result"
        result.desire_delta_hint = _get_useful_deltas(desire_name, capability_id, output)
        return result

    # Check if needs follow-up
    if _needs_followup(result_text, capability_id):
        result.task_effect = TaskEffect.NEEDS_FOLLOWUP
        result.summary = "Action succeeded but needs follow-up"
        result.desire_delta_hint = _get_useful_deltas(desire_name, capability_id, output)
        return result

    # Default: useful but minor
    result.task_effect = TaskEffect.USEFUL
    result.summary = "Action completed"
    result.desire_delta_hint = _get_useful_deltas(desire_name, capability_id, output)
    return result


def _is_no_effect(result_text: str, capability_id: str) -> bool:
    """Check if the result indicates no meaningful effect."""
    no_effect_indicators = [
        "no new posts",
        "no posts",
        "no results",
        "no memory found",
        "no mentions",
        "empty",
        "nothing found",
        "no data",
    ]
    for indicator in no_effect_indicators:
        if indicator in result_text:
            return True
    return False


def _is_useful(result_text: str, capability_id: str, output: dict[str, Any]) -> bool:
    """Check if the result is useful."""
    useful_indicators = [
        "found",
        "results",
        "posted",
        "replied",
        "saved",
        "captured",
        "executed successfully",
        "completed",
    ]
    for indicator in useful_indicators:
        if indicator in result_text:
            return True
    # Check for non-empty results
    if output.get("result") and len(str(output.get("result", ""))) > 50:
        return True
    return False


def _needs_followup(result_text: str, capability_id: str) -> bool:
    """Check if the result needs follow-up."""
    followup_indicators = [
        "mentions",
        "directed at",
        "reply",
        "question",
        "request",
    ]
    for indicator in followup_indicators:
        if indicator in result_text:
            return True
    return False


def _get_no_effect_deltas(desire_name: str) -> dict[str, float]:
    """Get deltas for no-effect results. These should NOT decrease desires."""
    deltas: dict[str, float] = {}
    if desire_name and desire_name in DESIRE_FULFILLMENT:
        deltas[desire_name] = 0.0
    return deltas


def _get_useful_deltas(desire_name: str, capability_id: str, output: dict[str, Any]) -> dict[str, float]:
    """Get deltas for useful results based on desire fulfillment conditions."""
    deltas: dict[str, float] = {}

    if not desire_name or desire_name not in DESIRE_FULFILLMENT:
        return deltas

    conditions = DESIRE_FULFILLMENT[desire_name]["conditions"]
    result_text = str(output.get("result", "")).lower()

    # Match conditions based on capability and result
    if "agora" in capability_id:
        if "posted" in result_text or "post" in capability_id:
            deltas[desire_name] = conditions.get("posted_to_agora", 0.5)
        elif "read" in capability_id:
            if "no new" in result_text or "no posts" in result_text:
                # AGORA no-new-posts: delta = 0.0 (do NOT increase social pressure)
                deltas[desire_name] = 0.0
            else:
                deltas[desire_name] = conditions.get("read_new_posts", 0.1)
    elif "search" in capability_id:
        if "no results" in result_text:
            deltas[desire_name] = conditions.get("empty_results", 0.0)
        else:
            deltas[desire_name] = conditions.get("web_search_results", 0.3)
    elif "memory" in capability_id:
        if "no memory" in result_text:
            deltas[desire_name] = conditions.get("empty_results", 0.0)
        else:
            deltas[desire_name] = conditions.get("new_info_summarized", 0.3)
    elif "screenshot" in capability_id:
        deltas[desire_name] = conditions.get("meaningful_action", 0.2)
    else:
        deltas[desire_name] = conditions.get("meaningful_action", 0.2)

    return deltas


def is_health_alert(capability_id: str, result_text: str) -> bool:
    """Check if this result should be a health alert instead of a desire update.

    Health-related conditions are handled by HealthAlertManager, not desires.
    """
    health_indicators = [
        "disk space",
        "disk usage",
        "unreachable",
        "no executor",
        "connection refused",
        "timed out",
        "provider unavailable",
    ]
    text = result_text.lower()
    for indicator in health_indicators:
        if indicator in text:
            return True
    return False
