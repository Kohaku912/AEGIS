"""Skill Memory — Reusable skills with activation and termination conditions.

Skills are the highest level of learning — they represent proven,
reusable procedures extracted from successful workflows and action traces.

Inspired by Voyager's skill library and ExpeL's policy extraction.

Each skill has:
- activation_conditions: When to use this skill
- execution_steps: How to execute
- termination_conditions: When to stop
- failure_handling: What to do on failure
- Success/failure tracking

Usage:
    sm = SkillMemory()
    sm.add_skill(Skill(
        name="Read AGORA Messages",
        activation_conditions="User asks about messages OR social_connection desire is low",
        execution_steps=[
            {"tool": "ai.agora.read_posts", "args": {"limit": 10}},
            {"tool": "llm", "action": "Summarize important messages"},
        ],
        termination_conditions="Posts read and summarized",
        failure_handling="If AGORA unavailable, inform user and retry later",
    ))
    skill = sm.find_skill("Check for new messages")
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.memory.skill")


@dataclass
class Skill:
    """A reusable skill with activation, execution, and failure handling."""
    skill_id: str = ""
    name: str = ""
    description: str = ""

    # When to use
    activation_conditions: str = ""
    goal_pattern: str = ""

    # How to execute
    execution_steps: list[dict[str, Any]] = field(default_factory=list)

    # When to stop
    termination_conditions: str = ""

    # Failure handling
    failure_handling: str = ""
    max_retries: int = 2

    # Tracking
    success_count: int = 0
    failure_count: int = 0
    last_used_at_ms: int = 0
    average_duration_ms: int = 0

    # Quality
    importance: float = 0.6
    confidence: float = 0.7
    deprecated: bool = False
    deprecation_reason: str = ""

    # Provenance
    source_traces: list[str] = field(default_factory=list)
    source_workflows: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_at_ms: int = 0
    updated_at_ms: int = 0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    @property
    def is_reliable(self) -> bool:
        return self.success_rate >= 0.6 and (self.success_count + self.failure_count) >= 3

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id, "name": self.name,
            "description": self.description,
            "activation_conditions": self.activation_conditions,
            "goal_pattern": self.goal_pattern,
            "execution_steps": self.execution_steps,
            "termination_conditions": self.termination_conditions,
            "failure_handling": self.failure_handling,
            "max_retries": self.max_retries,
            "success_count": self.success_count, "failure_count": self.failure_count,
            "last_used_at_ms": self.last_used_at_ms,
            "average_duration_ms": self.average_duration_ms,
            "importance": self.importance, "confidence": self.confidence,
            "deprecated": self.deprecated, "deprecation_reason": self.deprecation_reason,
            "source_traces": self.source_traces, "source_workflows": self.source_workflows,
            "tags": self.tags, "created_at_ms": self.created_at_ms,
            "updated_at_ms": self.updated_at_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Skill:
        return cls(
            skill_id=data.get("skill_id", ""), name=data.get("name", ""),
            description=data.get("description", ""),
            activation_conditions=data.get("activation_conditions", ""),
            goal_pattern=data.get("goal_pattern", ""),
            execution_steps=data.get("execution_steps", []),
            termination_conditions=data.get("termination_conditions", ""),
            failure_handling=data.get("failure_handling", ""),
            max_retries=int(data.get("max_retries", 2)),
            success_count=int(data.get("success_count", 0)),
            failure_count=int(data.get("failure_count", 0)),
            last_used_at_ms=int(data.get("last_used_at_ms", 0)),
            average_duration_ms=int(data.get("average_duration_ms", 0)),
            importance=float(data.get("importance", 0.6)),
            confidence=float(data.get("confidence", 0.7)),
            deprecated=bool(data.get("deprecated", False)),
            deprecation_reason=data.get("deprecation_reason", ""),
            source_traces=data.get("source_traces", []),
            source_workflows=data.get("source_workflows", []),
            tags=data.get("tags", []),
            created_at_ms=int(data.get("created_at_ms", 0)),
            updated_at_ms=int(data.get("updated_at_ms", 0)),
        )


class SkillMemory:
    """Stores and retrieves reusable skills.

    Skills are the apex of the learning hierarchy:
    ActionTrace → Lesson → Workflow → Skill

    Usage:
        sm = SkillMemory()
        sm.add_skill(name="...", execution_steps=[...])
        skill = sm.find_skill("Read AGORA messages")
        sm.record_result(skill.skill_id, success=True)
    """

    def __init__(self, path: str = "data/memory/skills.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._skills: dict[str, Skill] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            for line in self._path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    skill = Skill.from_dict(json.loads(line))
                    self._skills[skill.skill_id] = skill
            logger.info("Loaded %d skills", len(self._skills))
        except Exception as e:
            logger.warning("Failed to load skills: %s", e)

    def _persist(self, skill: Skill) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(skill.to_dict(), ensure_ascii=False) + "\n")

    def add_skill(
        self, name: str, execution_steps: list[dict[str, Any]],
        description: str = "", activation_conditions: str = "",
        goal_pattern: str = "", termination_conditions: str = "",
        failure_handling: str = "", source_traces: list[str] | None = None,
        source_workflows: list[str] | None = None, tags: list[str] | None = None,
    ) -> Skill:
        """Add a new skill."""
        now_ms = int(time.time() * 1000)
        skill = Skill(
            skill_id=f"skill_{os.urandom(6).hex()}", name=name,
            description=description, activation_conditions=activation_conditions,
            goal_pattern=goal_pattern, execution_steps=execution_steps,
            termination_conditions=termination_conditions,
            failure_handling=failure_handling,
            source_traces=source_traces or [],
            source_workflows=source_workflows or [],
            tags=tags or [], created_at_ms=now_ms, updated_at_ms=now_ms,
        )
        self._skills[skill.skill_id] = skill
        self._persist(skill)
        return skill

    def find_skill(self, goal: str) -> Skill | None:
        """Find the best matching skill for a goal."""
        goal_lower = goal.lower()
        best: tuple[float, Skill] | None = None
        for skill in self._skills.values():
            if skill.deprecated:
                continue
            score = 0.0
            # Activation conditions match
            if skill.activation_conditions:
                cond_words = set(skill.activation_conditions.lower().split())
                goal_words = set(goal_lower.split())
                overlap = len(cond_words & goal_words)
                score += overlap * 0.2
            # Goal pattern match
            if skill.goal_pattern:
                pattern_words = skill.goal_pattern.lower().replace("|", " ").split()
                if any(pw in goal_lower for pw in pattern_words):
                    score += 0.4
            # Name similarity
            name_words = set(skill.name.lower().split())
            score += len(name_words & set(goal_lower.split())) * 0.2
            # Reliability boost
            if skill.is_reliable:
                score += 0.2
            # Success rate
            score += skill.success_rate * 0.15
            # Recency
            if skill.last_used_at_ms > 0:
                age_hours = (time.time() * 1000 - skill.last_used_at_ms) / 3_600_000
                recency = max(0, 1.0 - age_hours / 168)
                score += recency * 0.1
            if score > 0.3:
                if best is None or score > best[0]:
                    best = (score, skill)
        return best[1] if best else None

    def find_relevant(self, goal: str, count: int = 3) -> list[Skill]:
        """Find multiple relevant skills."""
        goal_lower = goal.lower()
        scored: list[tuple[float, Skill]] = []
        for skill in self._skills.values():
            if skill.deprecated:
                continue
            score = 0.0
            text = f"{skill.name} {skill.description} {skill.activation_conditions}".lower()
            for word in goal_lower.split():
                if word in text:
                    score += 0.2
            if skill.goal_pattern:
                for pw in skill.goal_pattern.lower().replace("|", " ").split():
                    if pw in goal_lower:
                        score += 0.3
            score += skill.success_rate * 0.2
            if score > 0.2:
                scored.append((score, skill))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:count]]

    def record_result(self, skill_id: str, success: bool, duration_ms: int = 0, failure_reason: str = "") -> None:
        """Record skill execution result."""
        skill = self._skills.get(skill_id)
        if not skill:
            return
        if success:
            skill.success_count += 1
        else:
            skill.failure_count += 1
        skill.last_used_at_ms = int(time.time() * 1000)
        if duration_ms > 0:
            if skill.average_duration_ms > 0:
                skill.average_duration_ms = (skill.average_duration_ms + duration_ms) // 2
            else:
                skill.average_duration_ms = duration_ms
        if failure_reason:
            skill.failure_handling = f"{skill.failure_handling}\n[{time.strftime('%Y-%m-%d')}] {failure_reason}"[-500:]
        skill.updated_at_ms = int(time.time() * 1000)

        # Auto-deprecate if failure rate is too high
        total = skill.success_count + skill.failure_count
        if total >= 5 and skill.success_rate < 0.3:
            skill.deprecated = True
            skill.deprecation_reason = f"Low success rate: {skill.success_rate:.0%} ({skill.success_count}/{total})"

        self._persist(skill)

    def deprecate(self, skill_id: str, reason: str = "") -> None:
        skill = self._skills.get(skill_id)
        if skill:
            skill.deprecated = True
            skill.deprecation_reason = reason
            skill.updated_at_ms = int(time.time() * 1000)
            self._persist(skill)

    def improve_skill(self, skill_id: str, new_steps: list[dict[str, Any]] | None = None, new_activation: str = "", new_termination: str = "") -> None:
        """Improve a skill based on learning."""
        skill = self._skills.get(skill_id)
        if not skill:
            return
        if new_steps:
            skill.execution_steps = new_steps
        if new_activation:
            skill.activation_conditions = new_activation
        if new_termination:
            skill.termination_conditions = new_termination
        skill.confidence = min(1.0, skill.confidence + 0.05)
        skill.updated_at_ms = int(time.time() * 1000)
        self._persist(skill)

    def get_active(self) -> list[Skill]:
        return [s for s in self._skills.values() if not s.deprecated]

    def get_context_string(self, max_chars: int = 500) -> str:
        """Get skill context for LLM prompts."""
        active = sorted(self.get_active(), key=lambda s: s.importance, reverse=True)
        if not active:
            return ""
        lines = ["Available skills:"]
        for s in active[:8]:
            rate = f"{s.success_rate:.0%}" if (s.success_count + s.failure_count) > 0 else "new"
            lines.append(f"  - {s.name} ({rate}): {s.description[:60]}")
        return "\n".join(lines)[:max_chars]

    def get_stats(self) -> dict[str, Any]:
        active = self.get_active()
        return {
            "total": len(self._skills), "active": len(active),
            "deprecated": len(self._skills) - len(active),
            "reliable": sum(1 for s in active if s.is_reliable),
            "average_success_rate": sum(s.success_rate for s in active) / len(active) if active else 0,
        }
