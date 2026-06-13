"""Multimodal State Analyzer — LLM-based screen/DOM/UI state analysis."""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("aegis_ai.observation.multimodal_state_analyzer")

_SENSITIVE_KEYS = {"password", "token", "secret", "api_key", "cookie", "auth", "credential"}

_SENSITIVE_PATTERNS = [
    re.compile(r"(api[_-]?key|token|password|secret|cookie|auth)[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"Bearer\s+\S+", re.IGNORECASE),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
]


def _mask_text(text: str) -> str:
    for pat in _SENSITIVE_PATTERNS:
        text = pat.sub("***MASKED***", text)
    return text


@dataclass
class StateAnalysisResult:
    analysis_id: str = ""
    state_summary: str = ""
    task_relevant_elements: list[str] = field(default_factory=list)
    current_progress: str = ""
    success_signals: list[str] = field(default_factory=list)
    failure_signals: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    next_safe_actions: list[str] = field(default_factory=list)
    requires_user_help: bool = False
    sensitivity_flags: list[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "state_summary": self.state_summary[:300],
            "task_relevant_elements": self.task_relevant_elements[:10],
            "current_progress": self.current_progress[:200],
            "success_signals": self.success_signals[:5],
            "failure_signals": self.failure_signals[:5],
            "blocking_issues": self.blocking_issues[:5],
            "next_safe_actions": self.next_safe_actions[:5],
            "requires_user_help": self.requires_user_help,
            "sensitivity_flags": self.sensitivity_flags,
            "confidence": self.confidence,
            "created_at": self.created_at,
        }


_ANALYSIS_PROMPT_TEMPLATE = """You are AEGIS's multimodal state analyzer.
Analyze the current screen/DOM/UI state and return ONLY valid JSON.

## Current State
{state_context}

## Task Goal
{action_goal}

## Expected Outcome
{expected_outcome}

## Previous State Summary
{previous_summary}

## Recent Actions
{recent_actions}

## Required JSON Output
{{
  "state_summary": "Brief description of current state",
  "task_relevant_elements": ["list", "of", "relevant", "elements"],
  "current_progress": "How far along is the task",
  "success_signals": ["list", "of", "success", "indicators"],
  "failure_signals": ["list", "of", "failure", "indicators"],
  "blocking_issues": ["list", "of", "blocking", "issues"],
  "next_safe_actions": ["list", "of", "suggested", "actions"],
  "requires_user_help": false,
  "sensitivity_flags": ["list", "of", "sensitivity", "flags"],
  "confidence": 0.8
}}

IMPORTANT: Output ONLY the JSON object. No markdown, no explanation."""


class MultimodalStateAnalyzer:
    """Analyzes screen/DOM/UI state using LLM for task-relevant understanding."""

    def __init__(self, llm_client: Any = None) -> None:
        self._llm = llm_client

    def analyze(
        self,
        observation_summary: str = "",
        action_goal: str = "",
        expected_outcome: str = "",
        previous_summary: str = "",
        recent_actions: list[str] | None = None,
    ) -> StateAnalysisResult:
        masked_summary = _mask_text(observation_summary)
        masked_previous = _mask_text(previous_summary)
        recent = recent_actions or []

        if not self._llm:
            return self._fallback_analysis(masked_summary, action_goal)

        prompt = _ANALYSIS_PROMPT_TEMPLATE.format(
            state_context=masked_summary[:2000],
            action_goal=action_goal[:500],
            expected_outcome=expected_outcome[:500],
            previous_summary=masked_previous[:500] if masked_previous else "None",
            recent_actions="\n".join(f"- {a}" for a in recent[-5:]) if recent else "None",
        )

        try:
            result = self._llm.generate(
                prompt=prompt,
                system_prompt="You are a screen state analyzer. Output only JSON.",
                max_tokens=800,
            )
            if not result.success:
                logger.warning("LLM analysis failed: %s", result.error if hasattr(result, "error") else "unknown")
                return self._fallback_analysis(masked_summary, action_goal)

            parsed = self._parse_llm_output(result.content)
            return StateAnalysisResult(
                analysis_id=f"sa_{uuid.uuid4().hex[:10]}",
                state_summary=parsed.get("state_summary", ""),
                task_relevant_elements=parsed.get("task_relevant_elements", []),
                current_progress=parsed.get("current_progress", ""),
                success_signals=parsed.get("success_signals", []),
                failure_signals=parsed.get("failure_signals", []),
                blocking_issues=parsed.get("blocking_issues", []),
                next_safe_actions=parsed.get("next_safe_actions", []),
                requires_user_help=parsed.get("requires_user_help", False),
                sensitivity_flags=parsed.get("sensitivity_flags", []),
                confidence=min(1.0, max(0.0, parsed.get("confidence", 0.5))),
                created_at=int(time.time() * 1000),
            )
        except Exception as exc:
            logger.error("State analysis error: %s", exc)
            return self._fallback_analysis(masked_summary, action_goal)

    def build_context_for_recovery(
        self,
        analysis: StateAnalysisResult,
        max_chars: int = 1000,
    ) -> str:
        parts = [
            f"State: {analysis.state_summary}",
            f"Progress: {analysis.current_progress}",
        ]
        if analysis.success_signals:
            parts.append(f"Success signals: {', '.join(analysis.success_signals[:3])}")
        if analysis.failure_signals:
            parts.append(f"Failure signals: {', '.join(analysis.failure_signals[:3])}")
        if analysis.blocking_issues:
            parts.append(f"Blocking: {', '.join(analysis.blocking_issues[:3])}")
        if analysis.next_safe_actions:
            parts.append(f"Next actions: {', '.join(analysis.next_safe_actions[:3])}")
        text = "\n".join(parts)
        return text[:max_chars]

    def _parse_llm_output(self, content: str) -> dict[str, Any]:
        clean = content.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            clean = "\n".join(lines[1:])
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()

        json_match = re.search(r"\{.*\}", clean, re.DOTALL)
        if json_match:
            clean = json_match.group(0)

        return json.loads(clean)

    def _fallback_analysis(
        self,
        state_summary: str,
        action_goal: str,
    ) -> StateAnalysisResult:
        return StateAnalysisResult(
            analysis_id=f"sa_{uuid.uuid4().hex[:10]}",
            state_summary=state_summary[:300] if state_summary else "No state available",
            current_progress="Unable to determine without LLM",
            confidence=0.1,
            created_at=int(time.time() * 1000),
        )
