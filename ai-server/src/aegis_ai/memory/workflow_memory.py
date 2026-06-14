"""Workflow Memory — Repeated procedures extracted from action traces.

Workflows are sequences of steps that have been observed to work
for specific types of goals. Extracted from successful action traces
during consolidation.

Inspired by Agent Workflow Memory and Voyager.

Usage:
    wm = WorkflowMemory()
    wm.add(Workflow(
        name="Check AGORA for messages",
        goal_pattern="agora.*message|check.*agora",
        steps=[
            {"tool": "ai.agora.read_posts", "args": {"limit": 10}},
            {"tool": "llm", "action": "Summarize posts"},
        ],
    ))
    workflow = wm.find_matching("Check AGORA for new messages")
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.memory.workflow")


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    step_number: int = 0
    description: str = ""
    tool_call: str = ""       # capability_id or "llm" or "internal"
    tool_args: dict[str, Any] = field(default_factory=dict)
    expected_result: str = ""
    optional: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_number": self.step_number, "description": self.description,
            "tool_call": self.tool_call, "tool_args": self.tool_args,
            "expected_result": self.expected_result, "optional": self.optional,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowStep:
        return cls(
            step_number=int(data.get("step_number", 0)),
            description=data.get("description", ""),
            tool_call=data.get("tool_call", ""),
            tool_args=data.get("tool_args", {}),
            expected_result=data.get("expected_result", ""),
            optional=bool(data.get("optional", False)),
        )


@dataclass
class Workflow:
    """A reusable workflow extracted from successful action traces."""
    workflow_id: str = ""
    name: str = ""
    description: str = ""
    goal_pattern: str = ""       # Regex/keyword pattern for matching
    steps: list[WorkflowStep] = field(default_factory=list)
    source_trace_ids: list[str] = field(default_factory=list)

    # Usage stats
    success_count: int = 0
    failure_count: int = 0
    last_used_at_ms: int = 0
    average_duration_ms: int = 0

    # Quality
    importance: float = 0.5
    confidence: float = 0.6
    deprecated: bool = False
    tags: list[str] = field(default_factory=list)
    created_at_ms: int = 0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id, "name": self.name,
            "description": self.description, "goal_pattern": self.goal_pattern,
            "steps": [s.to_dict() for s in self.steps],
            "source_trace_ids": self.source_trace_ids,
            "success_count": self.success_count, "failure_count": self.failure_count,
            "last_used_at_ms": self.last_used_at_ms,
            "average_duration_ms": self.average_duration_ms,
            "importance": self.importance, "confidence": self.confidence,
            "deprecated": self.deprecated, "tags": self.tags,
            "created_at_ms": self.created_at_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Workflow:
        return cls(
            workflow_id=data.get("workflow_id", ""), name=data.get("name", ""),
            description=data.get("description", ""),
            goal_pattern=data.get("goal_pattern", ""),
            steps=[WorkflowStep.from_dict(s) for s in data.get("steps", [])],
            source_trace_ids=data.get("source_trace_ids", []),
            success_count=int(data.get("success_count", 0)),
            failure_count=int(data.get("failure_count", 0)),
            last_used_at_ms=int(data.get("last_used_at_ms", 0)),
            average_duration_ms=int(data.get("average_duration_ms", 0)),
            importance=float(data.get("importance", 0.5)),
            confidence=float(data.get("confidence", 0.6)),
            deprecated=bool(data.get("deprecated", False)),
            tags=data.get("tags", []),
            created_at_ms=int(data.get("created_at_ms", 0)),
        )


class WorkflowMemory:
    """Stores and retrieves reusable workflows.

    Usage:
        wm = WorkflowMemory()
        wm.add(Workflow(name="Check AGORA", steps=[...]))
        workflow = wm.find_matching("Check AGORA for messages")
    """

    def __init__(self, path: str = "data/memory/workflows.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._workflows: dict[str, Workflow] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            for line in self._path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    wf = Workflow.from_dict(json.loads(line))
                    self._workflows[wf.workflow_id] = wf
            logger.info("Loaded %d workflows", len(self._workflows))
        except Exception as e:
            logger.warning("Failed to load workflows: %s", e)

    def _persist(self, wf: Workflow) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(wf.to_dict(), ensure_ascii=False) + "\n")

    def add(self, name: str, steps: list[dict[str, Any]], goal_pattern: str = "", description: str = "", source_trace_ids: list[str] | None = None, tags: list[str] | None = None) -> Workflow:
        """Add a new workflow."""
        wf = Workflow(
            workflow_id=f"wf_{os.urandom(6).hex()}", name=name,
            description=description, goal_pattern=goal_pattern,
            steps=[WorkflowStep(step_number=i+1, **s) for i, s in enumerate(steps)],
            source_trace_ids=source_trace_ids or [], tags=tags or [],
            created_at_ms=int(time.time() * 1000),
        )
        self._workflows[wf.workflow_id] = wf
        self._persist(wf)
        return wf

    def find_matching(self, goal: str) -> Workflow | None:
        """Find the best matching workflow for a goal."""
        goal_lower = goal.lower()
        best: tuple[float, Workflow] | None = None
        for wf in self._workflows.values():
            if wf.deprecated:
                continue
            score = 0.0
            # Pattern match
            if wf.goal_pattern:
                pattern_words = wf.goal_pattern.lower().replace("|", " ").split()
                if any(pw in goal_lower for pw in pattern_words):
                    score += 0.5
            # Name similarity
            name_words = set(wf.name.lower().split())
            goal_words = set(goal_lower.split())
            overlap = len(name_words & goal_words)
            score += overlap * 0.3
            # Success rate boost
            score += wf.success_rate * 0.2
            if score > 0.3:
                if best is None or score > best[0]:
                    best = (score, wf)
        return best[1] if best else None

    def record_result(self, workflow_id: str, success: bool, duration_ms: int = 0) -> None:
        """Record workflow execution result."""
        wf = self._workflows.get(workflow_id)
        if wf:
            if success:
                wf.success_count += 1
            else:
                wf.failure_count += 1
            wf.last_used_at_ms = int(time.time() * 1000)
            if duration_ms > 0 and wf.average_duration_ms > 0:
                wf.average_duration_ms = (wf.average_duration_ms + duration_ms) // 2
            elif duration_ms > 0:
                wf.average_duration_ms = duration_ms

    def deprecate(self, workflow_id: str, reason: str = "") -> None:
        wf = self._workflows.get(workflow_id)
        if wf:
            wf.deprecated = True
            wf.tags.append(f"deprecated:{reason}")

    def get_active(self) -> list[Workflow]:
        return [wf for wf in self._workflows.values() if not wf.deprecated]

    def get_stats(self) -> dict[str, Any]:
        active = self.get_active()
        return {
            "total": len(self._workflows), "active": len(active),
            "deprecated": len(self._workflows) - len(active),
        }
