"""Curiosity-Driven Exploration System — Autonomous learning through exploration.

When curiosity desire is high, AEGIS autonomously explores:
- Current goals and recent events
- Unknown concepts and technologies
- Unresolved questions from memory
- Interesting patterns in data
- Potential improvements to its own systems

Generates exploration candidates, prioritizes them by:
- Importance: How relevant to current goals
- Novelty: How new/unknown
- Usefulness: How much it could help
- Interest: How engaging (curiosity factor)
- Risk: How safe the exploration is

All exploration is read-only or goes through PolicyEngine for side effects.

Inspired by:
- Voyager (open-ended exploration in Minecraft)
- Curiosity-driven reinforcement learning
- Intrinsic motivation in cognitive science

Usage:
    cdem = CuriosityDrivenExplorationSystem(llm=llm, curiosity_level=0.8)
    candidates = cdem.generate_exploration_candidates()
    best = cdem.select_best_candidate(candidates)
    result = cdem.explore(best)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.llm.json_utils import extract_json_object

logger = logging.getLogger("aegis_ai.autonomous.curiosity_exploration")


@dataclass
class ExplorationCandidate:
    """A potential exploration target."""
    candidate_id: str = ""
    topic: str = ""
    description: str = ""
    source: str = ""              # goal, memory, concept, question, pattern, improvement
    importance: float = 0.5       # 0.0 to 1.0
    novelty: float = 0.5          # 0.0 (known) to 1.0 (completely unknown)
    usefulness: float = 0.5       # 0.0 (useless) to 1.0 (very useful)
    interest: float = 0.5         # 0.0 (boring) to 1.0 (fascinating)
    risk: float = 0.1             # 0.0 (safe) to 1.0 (risky)
    related_desire: str = ""
    tags: list[str] = field(default_factory=list)
    grounding: dict[str, Any] = field(default_factory=dict)
    agenda_id: str = ""

    @property
    def priority_score(self) -> float:
        """Composite priority score."""
        return (
            self.importance * 0.3 +
            self.novelty * 0.25 +
            self.usefulness * 0.2 +
            self.interest * 0.2 -
            self.risk * 0.1
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id, "topic": self.topic,
            "description": self.description, "source": self.source,
            "importance": self.importance, "novelty": self.novelty,
            "usefulness": self.usefulness, "interest": self.interest,
            "risk": self.risk, "related_desire": self.related_desire,
            "tags": self.tags, "priority_score": self.priority_score,
            "grounding": self.grounding, "agenda_id": self.agenda_id,
        }


@dataclass
class ExplorationResult:
    """Result of an exploration."""
    result_id: str = ""
    candidate_id: str = ""
    topic: str = ""
    findings: str = ""
    new_questions: list[str] = field(default_factory=list)
    new_knowledge: list[str] = field(default_factory=list)
    success: bool = True
    duration_ms: int = 0
    tags: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    stop_reason: str = ""
    verification: dict[str, Any] = field(default_factory=dict)
    handoff: dict[str, Any] = field(default_factory=dict)
    source_quality: dict[str, Any] = field(default_factory=dict)
    budgets: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id, "candidate_id": self.candidate_id,
            "topic": self.topic, "findings": self.findings[:500],
            "new_questions": self.new_questions, "new_knowledge": self.new_knowledge,
            "success": self.success, "duration_ms": self.duration_ms, "tags": self.tags,
            "sources": self.sources,
            "stop_reason": self.stop_reason,
            "verification": self.verification,
            "handoff": self.handoff,
            "source_quality": self.source_quality,
            "budgets": self.budgets,
        }


class CuriosityDrivenExplorationSystem:
    """Autonomous exploration driven by curiosity.

    When curiosity desire is high:
    1. Generates exploration candidates from various sources
    2. Prioritizes by importance, novelty, usefulness, interest
    3. Explores the best candidate
    4. Records findings to memory systems

    Safety: All exploration is read-only. Side effects require approval.
    """

    def __init__(
        self,
        llm: Any = None,
        desire_system: Any = None,
        episodic_memory: Any = None,
        semantic_memory: Any = None,
        association_memory: Any = None,
        action_trace: Any = None,
        person_memory: Any = None,
        tool_broker: Any = None,
        curiosity_threshold: float = 6.0,
        data_dir: str = "data/autonomous",
    ) -> None:
        self._llm = llm
        self._desire = desire_system
        self._episodic = episodic_memory
        self._semantic = semantic_memory
        self._association = association_memory
        self._action_trace = action_trace
        self._person = person_memory
        self._broker = tool_broker
        self._curiosity_threshold = curiosity_threshold
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._exploration_history: list[dict[str, Any]] = []
        self._agenda: Any = None

    @property
    def curiosity_level(self) -> float:
        """Current curiosity desire level."""
        if not self._desire:
            return 0.0
        desire = self._desire.get_desire("curiosity")
        return desire.value if desire else 0.0

    @property
    def should_explore(self) -> bool:
        """Whether curiosity is high enough to trigger exploration."""
        return self.curiosity_level >= self._curiosity_threshold

    def generate_exploration_candidates(self) -> list[ExplorationCandidate]:
        """Generate exploration candidates from various sources."""
        candidates: list[ExplorationCandidate] = []

        # 1. From unresolved questions in memory
        candidates.extend(self._candidates_from_questions())

        # 2. From recent failures (what went wrong?)
        candidates.extend(self._candidates_from_failures())

        # 3. From unknown concepts
        candidates.extend(self._candidates_from_unknown())

        # 4. From system improvement opportunities
        candidates.extend(self._candidates_from_improvements())

        # 5. From LLM-suggested explorations
        if self._llm:
            candidates.extend(self._candidates_from_llm())

        # Deduplicate by topic
        seen_topics: set[str] = set()
        unique: list[ExplorationCandidate] = []
        for c in candidates:
            key = c.topic.lower().strip()
            if key not in seen_topics:
                seen_topics.add(key)
                unique.append(c)

        # Sort by priority
        unique.sort(key=lambda c: c.priority_score, reverse=True)
        self._sync_agenda(unique)
        return unique[:10]

    def _candidates_from_questions(self) -> list[ExplorationCandidate]:
        """Generate candidates from unresolved questions."""
        candidates: list[ExplorationCandidate] = []

        # Search semantic memory for questions
        if self._semantic:
            try:
                entries = self._semantic.get_by_category("question")
                for entry in entries[:3]:
                    candidates.append(ExplorationCandidate(
                        candidate_id=f"cand_{os.urandom(4).hex()}",
                        topic=entry.content[:60],
                        description=f"Unresolved question: {entry.content[:100]}",
                        source="question", importance=entry.importance,
                        novelty=0.7, usefulness=0.6, interest=0.7,
                        tags=["question", "knowledge"],
                        grounding={"question": entry.content},
                    ))
            except Exception:
                pass

        # Search episodic memory for open questions
        if self._episodic:
            try:
                recent = self._episodic.recall_recent(20)
                for ep in recent:
                    if "open_question" in ep.tags:
                        candidates.append(ExplorationCandidate(
                            candidate_id=f"cand_{os.urandom(4).hex()}",
                            topic=ep.action[:60],
                            description=f"Open question from episode: {ep.observation[:100]}",
                            source="episode", importance=ep.importance,
                            novelty=0.6, usefulness=0.5, interest=0.6,
                            tags=["question", "episode"],
                            grounding={"related_conversation": ep.episode_id, "question": ep.observation},
                        ))
            except Exception:
                pass

        return candidates

    def _candidates_from_failures(self) -> list[ExplorationCandidate]:
        """Generate candidates from recent failures."""
        candidates: list[ExplorationCandidate] = []
        if not self._action_trace:
            return candidates

        try:
            failed = self._action_trace.get_failed(count=10)
            for trace in failed[:3]:
                candidates.append(ExplorationCandidate(
                    candidate_id=f"cand_{os.urandom(4).hex()}",
                    topic=f"Why did '{trace.goal[:40]}' fail?",
                    description=f"Failure analysis: {trace.failure_reason[:100]}",
                    source="failure", importance=0.7,
                    novelty=0.5, usefulness=0.8, interest=0.5,
                    tags=["failure", "analysis"],
                    grounding={"related_failure": trace.trace_id},
                ))
        except Exception:
            pass

        return candidates

    def _candidates_from_unknown(self) -> list[ExplorationCandidate]:
        """Generate candidates from unknown concepts."""
        candidates: list[ExplorationCandidate] = []

        # Look for topics mentioned but not fully understood
        if self._semantic:
            try:
                knowledge = self._semantic.get_knowledge()
                partial = [k for k in knowledge if len(k.content) < 50 and k.confidence < 0.7]
                for entry in partial[:3]:
                    candidates.append(ExplorationCandidate(
                        candidate_id=f"cand_{os.urandom(4).hex()}",
                        topic=entry.content[:60],
                        description=f"Partially understood concept: {entry.content[:100]}",
                        source="concept", importance=0.5,
                        novelty=0.8, usefulness=0.5, interest=0.7,
                        tags=["concept", "unknown"],
                        grounding={"question": f"What evidence would raise confidence in {entry.content[:60]}?"},
                    ))
            except Exception:
                pass

        return candidates

    def _candidates_from_improvements(self) -> list[ExplorationCandidate]:
        """Generate candidates from improvement opportunities."""
        candidates: list[ExplorationCandidate] = []

        # Check skill memory for underperforming skills
        try:
            from aegis_ai.memory.skill_memory import SkillMemory
            sm = SkillMemory(path=str(self._data_dir.parent / "memory" / "skills.jsonl"))
            for skill in sm.get_active():
                if skill.success_rate < 0.6 and (skill.success_count + skill.failure_count) >= 3:
                    candidates.append(ExplorationCandidate(
                        candidate_id=f"cand_{os.urandom(4).hex()}",
                        topic=f"Improve skill: {skill.name}",
                        description=f"Skill '{skill.name}' has low success rate: {skill.success_rate:.0%}",
                        source="improvement", importance=0.6,
                        novelty=0.4, usefulness=0.8, interest=0.5,
                        tags=["improvement", "skill"],
                        grounding={"related_failure": skill.skill_id},
                    ))
        except Exception:
            pass

        return candidates

    def _candidates_from_llm(self) -> list[ExplorationCandidate]:
        """Use LLM to suggest exploration topics."""
        if not self._llm:
            return []

        # Build context about current state
        context_parts = []
        if self._desire:
            try:
                context_parts.append(self._desire.to_context_string())
            except Exception:
                pass
        if self._episodic:
            try:
                recent = self._episodic.recall_recent(5)
                if recent:
                    context_parts.append("Recent events: " + "; ".join(ep.action[:30] for ep in recent))
            except Exception:
                pass

        context = "\n".join(context_parts) if context_parts else "No context available"

        prompt = f"""You are AEGIS's curiosity system. Based on current state, suggest 2-3 exploration topics.

Current state:
{context}

Return a topics array. Each topic needs topic, reason, importance, novelty,
usefulness, and interest fields.

Topics should be:
- Specific and actionable
- Related to current goals or recent events
- Something new to learn or investigate
- Safe to explore (read-only observation)"""

        try:
            result = self._llm.generate(
                prompt=prompt,
                system_prompt="Suggest exploration topics. Output only JSON.",
                max_tokens=300,
            )
            if result.success:
                data = extract_json_object(result.content)
                if data:
                    candidates = []
                    for t in data.get("topics", []):
                        candidates.append(ExplorationCandidate(
                            candidate_id=f"cand_{os.urandom(4).hex()}",
                            topic=t.get("topic", ""),
                            description=t.get("reason", ""),
                            source="llm_suggestion",
                            importance=float(t.get("importance", 0.5)),
                            novelty=float(t.get("novelty", 0.5)),
                            usefulness=float(t.get("usefulness", 0.5)),
                            interest=float(t.get("interest", 0.5)),
                            tags=["llm_suggested"],
                        ))
                    return candidates
        except Exception as e:
            logger.warning("LLM suggestion failed: %s", e)

        return []

    def select_best_candidate(self, candidates: list[ExplorationCandidate]) -> ExplorationCandidate | None:
        """Select the best candidate for exploration."""
        if not candidates:
            return None
        return max(candidates, key=lambda c: c.priority_score)

    def explore(self, candidate: ExplorationCandidate) -> ExplorationResult:
        """Explore a candidate topic.

        This is the main exploration method. It uses LLM to investigate
        the topic and generate findings.

        Safety: All exploration is read-only. No side effects.
        """
        start_time = int(time.time() * 1000)
        result = ExplorationResult(
            result_id=f"explore_{os.urandom(6).hex()}",
            candidate_id=candidate.candidate_id,
            topic=candidate.topic,
            tags=candidate.tags,
        )

        if not self._llm:
            result.findings = "Cannot explore without LLM provider"
            result.success = False
            return result

        browser_evidence = self._collect_browser_evidence(candidate)
        if candidate.agenda_id and browser_evidence is None:
            result.findings = "Browser research capability is unavailable; no source comparison was claimed."
            result.success = False
            result.stop_reason = "browser_unavailable"
            result.verification = {"passed": False, "reason": result.findings}
            result.duration_ms = int(time.time() * 1000) - start_time
            self._record_agenda_result(candidate, result)
            self._save_exploration_result(candidate, result)
            self._exploration_history.append(result.to_dict())
            return result
        if browser_evidence is not None:
            result.sources = browser_evidence["sources"]
            result.stop_reason = browser_evidence["stop_reason"]
            result.verification = browser_evidence["verification"]
            result.handoff = browser_evidence["handoff"]
            result.source_quality = browser_evidence["source_quality"]
            result.budgets = browser_evidence["budgets"]
            if not result.verification.get("passed"):
                result.findings = str(result.verification.get("reason") or "Browser evidence was insufficient.")
                result.success = False
                result.duration_ms = int(time.time() * 1000) - start_time
                self._record_agenda_result(candidate, result)
                self._save_exploration_result(candidate, result)
                self._exploration_history.append(result.to_dict())
                return result

        # Build exploration prompt
        context = self._build_exploration_context(candidate)

        prompt = f"""You are AEGIS, exploring a topic out of curiosity.

Topic: {candidate.topic}
Reason: {candidate.description}
Source: {candidate.source}

Context:
{context}

Verified browser evidence:
{json.dumps(browser_evidence or {}, ensure_ascii=False, default=str)[:6000]}

Investigate this topic by:
1. Analyzing what you already know
2. Identifying gaps in understanding
3. Generating hypotheses
4. Suggesting concrete next steps

Respond with JSON:
{{
  "findings": "What you discovered or concluded",
  "new_knowledge": ["fact 1", "fact 2"],
  "new_questions": ["question 1", "question 2"],
  "confidence": 0.7
}}

Be specific and actionable. Focus on what's useful to remember."""

        try:
            llm_result = self._llm.generate(
                prompt=prompt,
                system_prompt="You are AEGIS exploring out of curiosity. Be thorough but concise. Output only JSON.",
                max_tokens=500,
            )
            if llm_result.success:
                data = extract_json_object(llm_result.content)
                if data:
                    result.findings = data.get("findings", "")
                    result.new_knowledge = data.get("new_knowledge", [])
                    result.new_questions = data.get("new_questions", [])
                    result.success = True
                else:
                    result.findings = llm_result.content[:300]
                    result.success = True
            else:
                result.findings = f"LLM exploration failed: {llm_result.error}"
                result.success = False
        except Exception as e:
            result.findings = f"Exploration error: {str(e)}"
            result.success = False

        result.duration_ms = int(time.time() * 1000) - start_time

        self._record_agenda_result(candidate, result)

        # Save results to memory systems
        self._save_exploration_result(candidate, result)

        # Update curiosity desire
        if self._desire and result.success:
            try:
                curiosity = self._desire.get_desire("curiosity")
                if curiosity and curiosity.value < curiosity.expected_value:
                    self._desire.update_value(
                        "curiosity",
                        min(10.0, curiosity.value + 0.5),
                        reason=f"Explored: {candidate.topic[:50]}",
                    )
                    self._desire.save()
            except Exception:
                pass

        self._exploration_history.append(result.to_dict())
        return result

    def _collect_browser_evidence(
        self,
        candidate: ExplorationCandidate,
    ) -> dict[str, Any] | None:
        if self._broker is None:
            return None
        catalog = getattr(self._broker, "_catalog", None)
        if catalog is None:
            return None
        manifests = [
            manifest
            for manifest in catalog.list_all()
            if manifest.server_id == "browser-server"
            and manifest.app_id == "search"
            and manifest.enabled
            and not manifest.side_effects
        ]
        if not manifests:
            return None
        manifest = sorted(manifests, key=lambda item: item.capability_id)[0]

        from tool_broker import ExecutionSource, ToolExecutionRequest

        max_steps = 12
        request = ToolExecutionRequest(
            capability_id=manifest.capability_id,
            arguments={
                "task": (
                    f"Investigate this grounded question and compare independent sources: "
                    f"{candidate.topic}"
                ),
                "viewer": "agent_private",
                "purpose": "research",
                "success_condition": "Two to five independent source records with findings are returned",
                "stop_condition": "Stop after five sources or when evidence repeats",
                "max_steps": max_steps,
            },
            source=ExecutionSource.AUTONOMOUS,
            reason=f"Grounded exploration agenda: {candidate.agenda_id or candidate.candidate_id}",
            source_desire="growth",
            metadata={
                "agenda_id": candidate.agenda_id,
                "viewer": "agent_private",
                "purpose": "research",
            },
        )
        started = int(time.time() * 1000)
        execution = self._broker.execute(request)
        output = dict(getattr(execution, "output", {}) or {})
        data = output.get("data") if isinstance(output.get("data"), dict) else {}
        raw_sources = data.get("sources") or output.get("sources") or []
        sources: list[str] = []
        if isinstance(raw_sources, list):
            for raw in raw_sources:
                source = (
                    str(raw.get("url") or raw.get("source") or raw.get("id") or "")
                    if isinstance(raw, dict)
                    else str(raw)
                )
                if source and source not in sources:
                    sources.append(source)
        sources = sources[:5]
        passed = bool(getattr(execution, "success", False)) and 2 <= len(sources) <= 5
        reason = (
            "Browser returned two to five independently identifiable sources."
            if passed
            else "Browser research did not return two independently identifiable sources."
        )
        return {
            "sources": sources,
            "source_quality": data.get("source_quality", {}),
            "findings": data.get("findings", output.get("result", "")),
            "stop_reason": str(
                data.get("stop_reason")
                or ("success_condition_met" if passed else "insufficient_sources")
            ),
            "verification": {
                "passed": passed,
                "reason": reason,
                "verification_status": str(getattr(execution, "verification_status", "")),
            },
            "handoff": dict(output.get("handoff") or {}),
            "budgets": {
                "max_steps": max_steps,
                "duration_ms": int(time.time() * 1000) - started,
                "source_limit": 5,
            },
        }

    def _record_agenda_result(
        self,
        candidate: ExplorationCandidate,
        result: ExplorationResult,
    ) -> None:
        if self._agenda is None or not candidate.agenda_id:
            return
        try:
            if result.success and result.verification.get("passed") and 2 <= len(result.sources) <= 5:
                self._agenda.record_result(
                    candidate.agenda_id,
                    sources=result.sources,
                    what_was_learned=result.findings,
                    source_quality=result.source_quality,
                    what_changed=result.findings,
                    next_question=result.new_questions[0] if result.new_questions else "",
                    stop_reason=result.stop_reason,
                    verification=result.verification,
                    budgets=result.budgets,
                    handoff=result.handoff or None,
                )
            else:
                self._agenda.record_attempt(
                    candidate.agenda_id,
                    sources=result.sources,
                    stop_reason=result.stop_reason,
                    verification=result.verification,
                    budgets=result.budgets,
                    handoff=result.handoff or None,
                )
        except (KeyError, ValueError):
            logger.debug("Unable to persist exploration agenda result", exc_info=True)

    def _sync_agenda(self, candidates: list[ExplorationCandidate]) -> None:
        if self._agenda is None:
            return
        source_map = {
            "question": "question",
            "episode": "conversation",
            "failure": "failure",
            "concept": "prior_finding",
            "improvement": "capability_improvement",
        }
        for candidate in candidates:
            source = source_map.get(candidate.source)
            if not source or not candidate.grounding:
                continue
            try:
                item = self._agenda.add(
                    candidate.topic,
                    source,
                    expected_value=candidate.usefulness,
                    novelty=candidate.novelty,
                    why_now=candidate.description,
                    what_was_unknown=candidate.topic,
                    **candidate.grounding,
                )
                candidate.agenda_id = item.agenda_id
            except ValueError:
                continue

    def _build_exploration_context(self, candidate: ExplorationCandidate) -> str:
        """Build context for exploration."""
        parts = []

        # Related memories
        if self._episodic:
            try:
                related = self._episodic.recall_similar(candidate.topic, count=3)
                if related:
                    parts.append("Related episodes: " + "; ".join(ep.summary[:40] or ep.action[:40] for ep in related))
            except Exception:
                pass

        # Related knowledge
        if self._semantic:
            try:
                knowledge = self._semantic.search(candidate.topic, limit=3)
                if knowledge:
                    parts.append("Related knowledge: " + "; ".join(k.content[:60] for k in knowledge))
            except Exception:
                pass

        # Related skills
        try:
            from aegis_ai.memory.skill_memory import SkillMemory
            sm = SkillMemory(path=str(self._data_dir.parent / "memory" / "skills.jsonl"))
            related_skills = sm.find_relevant(candidate.topic, count=2)
            if related_skills:
                parts.append("Related skills: " + "; ".join(s.name for s in related_skills))
        except Exception:
            pass

        return "\n".join(parts) if parts else "No related context found"

    def _save_exploration_result(self, candidate: ExplorationCandidate, result: ExplorationResult) -> None:
        """Save exploration results to memory systems."""
        # Save to episodic memory
        if self._episodic and result.success:
            try:
                self._episodic.record(
                    action=f"Explored: {candidate.topic}",
                    observation=result.findings[:200],
                    category="exploration",
                    emotion_tag="curious",
                    valence=0.4,
                    lesson=result.new_knowledge[0] if result.new_knowledge else "",
                    importance=candidate.importance,
                    tags=candidate.tags + ["exploration", "curiosity"],
                )
            except Exception:
                pass

        # Save new knowledge to semantic memory
        if self._semantic and result.new_knowledge:
            try:
                for knowledge in result.new_knowledge[:3]:
                    self._semantic.add(
                        content=knowledge,
                        category="knowledge",
                        source="exploration",
                        confidence=0.6,
                        importance=candidate.importance * 0.8,
                        tags=candidate.tags + ["explored"],
                    )
            except Exception:
                pass

        # Save to action trace
        if self._action_trace:
            try:
                trace = self._action_trace.begin_trace(
                    goal=f"Explore: {candidate.topic}",
                    context=f"curiosity_exploration (level={self.curiosity_level:.1f})",
                    desire_name="curiosity",
                    tags=candidate.tags,
                )
                self._action_trace.add_step(
                    trace, description="Exploration",
                    tool_call="llm", tool_result=result.findings[:200],
                    success=result.success,
                )
                self._action_trace.complete_trace(
                    trace, success=result.success,
                    result_summary=result.findings[:200],
                )
            except Exception:
                pass

        # Log exploration
        log_path = self._data_dir / "exploration_log.jsonl"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                entry = {
                    "timestamp_ms": int(time.time() * 1000),
                    "candidate": candidate.to_dict(),
                    "result": result.to_dict(),
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def get_exploration_stats(self) -> dict[str, Any]:
        stats = {
            "total_explorations": len(self._exploration_history),
            "curiosity_level": self.curiosity_level,
            "should_explore": self.should_explore,
        }
        if self._agenda is not None:
            stats["agenda"] = self._agenda.diagnostics()
        return stats
