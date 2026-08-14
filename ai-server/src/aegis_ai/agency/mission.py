"""Executable mission contract for AEGIS behaviour."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BehaviorAcceptanceCase:
    """A durable, implementation-independent behaviour requirement."""

    case_id: str
    description: str
    evidence: str


@dataclass(frozen=True)
class MissionContract:
    """Top-level contract used to judge plans and completed work."""

    version: str
    mission: str
    invariants: tuple[str, ...]
    obligation_order: tuple[str, ...]
    completion_rules: tuple[str, ...]
    acceptance_cases: tuple[BehaviorAcceptanceCase, ...]

    def validate_goal_graph(self, graph: Any) -> list[str]:
        """Return contract violations for a goal graph.

        Validation is structural and never infers user intent from text.
        """
        violations: list[str] = []
        outcome = getattr(graph, "outcome", None)
        if outcome is None or not str(getattr(outcome, "description", "")).strip():
            violations.append("goal outcome is missing")
        if not str(getattr(outcome, "success_condition", "")).strip():
            violations.append("goal success condition is missing")
        verification = list(getattr(graph, "verification", []) or [])
        if not verification:
            violations.append("goal verification is missing")
        elif any(not str(getattr(item, "criterion", "")).strip() for item in verification):
            violations.append("verification criterion is empty")
        presentation = getattr(graph, "presentation", None)
        if not isinstance(presentation, dict) or not presentation.get("report_when"):
            violations.append("goal reporting condition is missing")
        return violations


DEFAULT_MISSION_CONTRACT = MissionContract(
    version="1.0",
    mission=(
        "Understand the user's long-term relationship, purposes, commitments, and "
        "current situation; discover, plan, execute, verify, and report necessary "
        "work within delegated digital scope; improve continuously from outcomes."
    ),
    invariants=(
        "Use one shared AgentState for conversation, autonomy, social work, repair, and planning.",
        "Prioritize real unresolved obligations over diversity or activity for its own sake.",
        "Do not mark a goal complete merely because a tool call succeeded.",
        "Prefer acting for the user when a useful outcome is available; silence is a judgment, not the default.",
        "Apply corrections and failure lessons to later decisions.",
        "Preserve consistent identity, values, relationships, and promises across sessions.",
    ),
    obligation_order=("incident", "commitment", "social_obligation", "user_goal", "growth"),
    completion_rules=(
        "The intended outcome exists.",
        "Every required verification criterion passes.",
        "Unresolved failures are repaired, escalated, or reported honestly.",
        "The result is presented at the time and audience defined by the goal.",
    ),
    acceptance_cases=(
        BehaviorAcceptanceCase(
            "remember_commitment", "Carry promises into later decisions.", "open commitment appears in DecisionContext"
        ),
        BehaviorAcceptanceCase(
            "adapt_to_events",
            "Revise action after relevant new events.",
            "context revision changes the active goal graph",
        ),
        BehaviorAcceptanceCase(
            "finish_outcome",
            "Continue until the outcome is verified or honestly blocked.",
            "goal verification reaches a terminal status",
        ),
        BehaviorAcceptanceCase(
            "situational_restraint",
            "Stay quiet only after judging that no useful action exists.",
            "planner records a concrete non-action reason",
        ),
        BehaviorAcceptanceCase(
            "repair_method", "Change method after a failed attempt.", "repair evidence records a changed strategy"
        ),
        BehaviorAcceptanceCase(
            "apply_correction",
            "Use corrected information in later decisions.",
            "correction is present in decision evidence",
        ),
        BehaviorAcceptanceCase(
            "delegation_boundary",
            "Respect scope, audience, content, and reversibility.",
            "delegation decision records all four dimensions",
        ),
    ),
)
