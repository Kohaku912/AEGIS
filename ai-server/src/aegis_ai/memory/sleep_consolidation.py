"""Sleep Consolidation System — Memory organization during "sleep".

Periodically (or manually) consolidates short-term memories into
long-term organized memory. Inspired by how human sleep organizes
memories from the day.

Operations during sleep:
1. Summarize recent episodes
2. Update person records from interactions
3. Convert episodes to semantic knowledge
4. Create association links between related memories
5. Extract lessons for future use
6. Log consolidation results

Usage:
    sleep = SleepConsolidationSystem(
        episodic=ep, semantic=sem, person=pm, association=am, llm=llm
    )
    result = sleep.consolidate()  # Manual trigger
    # Or: sleep.start_auto(interval_hours=6)  # Automatic
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.memory.sleep_consolidation")


class SleepConsolidationSystem:
    """Memory consolidation system that organizes memories during 'sleep'.

    Consolidates:
    - Episodes → summarized, tagged, linked
    - Person records → updated from interactions
    - Semantic memory → knowledge derived from episodes
    - Associations → links between related memories
    - Lessons → extracted for future reference
    """

    def __init__(
        self,
        episodic: Any = None,
        semantic: Any = None,
        person: Any = None,
        association: Any = None,
        experiential: Any = None,
        affect: Any = None,
        action_trace: Any = None,
        lesson: Any = None,
        workflow: Any = None,
        skill: Any = None,
        llm: Any = None,
        data_dir: str = "data/memory",
        auto_interval_hours: float = 6.0,
    ) -> None:
        self._episodic = episodic
        self._semantic = semantic
        self._person = person
        self._association = association
        self._experiential = experiential
        self._affect = affect
        self._action_trace = action_trace
        self._lesson = lesson
        self._workflow = workflow
        self._skill = skill
        self._llm = llm
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = self._data_dir / "consolidation_log.jsonl"

        self._auto_interval_ms = int(auto_interval_hours * 3_600_000)
        self._last_consolidation_ms: int = 0
        self._running = False
        self._thread: threading.Thread | None = None
        self._consolidation_count: int = 0

    def start_auto(self, interval_hours: float | None = None) -> None:
        """Start automatic consolidation in background."""
        if self._running:
            return
        if interval_hours is not None:
            self._auto_interval_ms = int(interval_hours * 3_600_000)
        self._running = True
        self._thread = threading.Thread(target=self._auto_loop, daemon=True)
        self._thread.start()
        logger.info("Auto-consolidation started (interval=%dh)", self._auto_interval_ms // 3_600_000)

    def stop_auto(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _auto_loop(self) -> None:
        while self._running:
            now_ms = int(time.time() * 1000)
            if now_ms - self._last_consolidation_ms >= self._auto_interval_ms:
                try:
                    self.consolidate()
                except Exception as e:
                    logger.error("Auto-consolidation error: %s", e)
            time.sleep(60)

    def consolidate(self) -> dict[str, Any]:
        """Run full memory consolidation cycle.

        Returns summary of consolidation results.
        """
        start = time.time()
        results: dict[str, Any] = {
            "timestamp_ms": int(start * 1000),
            "episodes_summarized": 0,
            "persons_updated": 0,
            "knowledge_extracted": 0,
            "associations_created": 0,
            "lessons_extracted": 0,
            "duplicates_merged": 0,
            "action_traces_consolidated": 0,
            "lessons_from_traces": 0,
            "workflows_promoted": 0,
            "skills_promoted": 0,
        }

        logger.info("Starting memory consolidation...")

        # 1. Summarize recent episodes
        if self._episodic:
            results["episodes_summarized"] = self._summarize_episodes()

        # 2. Update person records from interactions
        if self._person and self._episodic:
            results["persons_updated"] = self._update_persons()

        # 3. Extract knowledge from episodes → semantic
        if self._semantic and self._episodic:
            results["knowledge_extracted"] = self._extract_knowledge()

        # 4. Create associations
        if self._association:
            results["associations_created"] = self._create_associations()

        # 5. Extract lessons
        if self._semantic and self._episodic:
            results["lessons_extracted"] = self._extract_lessons()

        # 6. Merge duplicates in semantic memory
        if self._semantic:
            results["duplicates_merged"] = self._merge_duplicates()

        # 7. Affect consolidation
        if self._affect:
            self._consolidate_affect()

        # 8. Consolidate ActionTraces → Lessons
        if self._action_trace and self._lesson:
            results["lessons_from_traces"] = self._traces_to_lessons()

        # 9. Promote repeated patterns → Workflows
        if self._action_trace and self._workflow:
            results["workflows_promoted"] = self._traces_to_workflows()

        # 10. Promote reliable workflows → Skills
        if self._workflow and self._skill:
            results["skills_promoted"] = self._workflows_to_skills()

        self._last_consolidation_ms = int(time.time() * 1000)
        self._consolidation_count += 1

        # Log results
        self._log_consolidation(results)

        duration = time.time() - start
        logger.info("Consolidation complete in %.1fs: %s", duration, results)
        return results

    def _summarize_episodes(self) -> int:
        """Summarize unconsolidated episodes using LLM."""
        if not self._episodic or not self._llm:
            return 0

        unconsolidated = self._episodic.get_unconsolidated(max_count=30)
        if not unconsolidated:
            return 0

        count = 0
        # Group by category
        by_category: dict[str, list] = {}
        for ep in unconsolidated:
            by_category.setdefault(ep.category, []).append(ep)

        for category, episodes in by_category.items():
            # Build prompt for summarization
            ep_texts = []
            for ep in episodes[:10]:
                ep_texts.append(f"- [{ep.emotion_tag}] {ep.action}: {ep.observation[:80]}")

            prompt = f"""Summarize these {category} episodes into 2-3 concise sentences:

{chr(10).join(ep_texts)}

Focus on patterns, key events, and important outcomes. Be concise."""

            try:
                result = self._llm.generate(
                    prompt=prompt,
                    system_prompt="You are a memory consolidation system. Summarize episodes concisely.",
                    max_tokens=200,
                )
                if result.success:
                    summary = result.content.strip()
                    for ep in episodes:
                        self._episodic.mark_consolidated(ep.episode_id, summary)
                        count += 1
            except Exception as e:
                logger.warning("Episode summarization failed: %s", e)

        return count

    def _update_persons(self) -> int:
        """Update person records from recent episodes."""
        if not self._episodic or not self._person:
            return 0

        count = 0
        recent = self._episodic.recall_recent(50)
        for ep in recent:
            for person_name in ep.persons:
                person = self._person.resolve(person_name)
                if person:
                    # Update topics from episode tags
                    new_topics = [t for t in ep.tags if t not in person.topics]
                    if new_topics:
                        person.topics.extend(new_topics)
                        person.topics = person.topics[-30:]
                    self._person.record_interaction(person.person_id, ep.action[:100])
                    count += 1
                else:
                    # Create new person record
                    self._person.upsert(
                        self._person._persons.get(person_name) or
                        type('PersonRecord', (), {
                            'person_id': '',
                            'name': person_name,
                            'role': 'user',
                            'authority_level': 50,
                            'trust_level': 0.5,
                            'relationship': '',
                            'notes': f'First seen in episode: {ep.action[:50]}',
                        })()
                    )
        return count

    def _extract_knowledge(self) -> int:
        """Extract semantic knowledge from episodes."""
        if not self._episodic or not self._semantic or not self._llm:
            return 0

        unconsolidated = [ep for ep in self._episodic.get_unconsolidated(20) if ep.lesson]
        if not unconsolidated:
            return 0

        count = 0
        for ep in unconsolidated:
            if ep.lesson and len(ep.lesson) > 10:
                # Determine category
                category = "knowledge"
                if "prefer" in ep.lesson.lower() or "like" in ep.lesson.lower():
                    category = "preference"
                elif "should" in ep.lesson.lower() or "must" in ep.lesson.lower():
                    category = "policy"
                elif "how to" in ep.lesson.lower():
                    category = "skill"

                self._semantic.add(
                    content=ep.lesson,
                    category=category,
                    source="consolidation",
                    confidence=0.7,
                    importance=ep.importance,
                    tags=ep.tags,
                )
                count += 1

        return count

    def _create_associations(self) -> int:
        """Create associations between related memories."""
        if not self._association or not self._episodic:
            return 0

        count = 0
        recent = self._episodic.recall_recent(30)

        # Link episodes with same persons
        person_episodes: dict[str, list] = {}
        for ep in recent:
            for p in ep.persons:
                person_episodes.setdefault(p, []).append(ep.episode_id)

        for person, ep_ids in person_episodes.items():
            for i, id1 in enumerate(ep_ids):
                for id2 in ep_ids[i+1:]:
                    self._association.link(
                        source_id=id1, source_type="episode",
                        target_id=id2, target_type="episode",
                        relation="related", strength=0.4,
                        context=f"Both involve {person}",
                    )
                    count += 1

        # Link episodes with same tags
        tag_episodes: dict[str, list] = {}
        for ep in recent:
            for t in ep.tags:
                tag_episodes.setdefault(t.lower(), []).append(ep.episode_id)

        for tag, ep_ids in tag_episodes.items():
            if len(ep_ids) >= 2:
                for i in range(len(ep_ids) - 1):
                    self._association.link(
                        source_id=ep_ids[i], source_type="episode",
                        target_id=ep_ids[i+1], target_type="episode",
                        relation="temporal", strength=0.3,
                        context=f"Same tag: {tag}",
                    )
                    count += 1

        # Link temporally close episodes
        for i in range(len(recent) - 1):
            time_diff = recent[i+1].timestamp_ms - recent[i].timestamp_ms
            if time_diff < 300_000:  # Within 5 minutes
                self._association.link(
                    source_id=recent[i].episode_id, source_type="episode",
                    target_id=recent[i+1].episode_id, target_type="episode",
                    relation="temporal", strength=0.5,
                    context="Close in time",
                )
                count += 1

        return count

    def _extract_lessons(self) -> int:
        """Extract lessons from failed or significant episodes."""
        if not self._episodic or not self._semantic:
            return 0

        count = 0
        # Find episodes with negative valence (failures)
        failures = [ep for ep in self._episodic.recall_recent(50) if ep.valence < -0.3 and not ep.lesson]

        for ep in failures:
            lesson = f"When '{ep.action[:50]}' resulted in: {ep.observation[:80]}. Consider alternative approaches."
            self._semantic.add(
                content=lesson,
                category="knowledge",
                source="failure_analysis",
                confidence=0.8,
                importance=max(0.6, ep.importance),
                tags=ep.tags + ["lesson", "failure"],
            )
            ep.lesson = lesson
            count += 1

        return count

    def _merge_duplicates(self) -> int:
        """Find and merge duplicate semantic entries."""
        if not self._semantic:
            return 0

        duplicates = self._semantic.find_duplicates()
        count = 0
        for e1, e2 in duplicates:
            # Keep the more important one, supersede the other
            if e1.importance >= e2.importance:
                self._semantic.supersede(e2.entry_id, e1.content, "dedup")
            else:
                self._semantic.supersede(e1.entry_id, e2.content, "dedup")
            count += 1

        return count

    def _consolidate_affect(self) -> None:
        """Consolidate affect state (personality drift from experiences)."""
        if not self._affect or not self._episodic:
            return

        # Check recent emotional patterns
        recent = self._episodic.recall_recent(20)
        if not recent:
            return

        # Count emotion patterns
        positive = sum(1 for ep in recent if ep.valence > 0.3)
        negative = sum(1 for ep in recent if ep.valence < -0.3)

        # If strongly positive/negative pattern, nudge personality slightly
        if positive > negative * 2 and positive > 5:
            # Very positive experiences → slight increase in extraversion
            self._affect.personality.update_trait("extraversion", 0.01, "Positive experience pattern")
        elif negative > positive * 2 and negative > 5:
            # Very negative experiences → slight increase in neuroticism
            self._affect.personality.update_trait("neuroticism", 0.01, "Negative experience pattern")

    # ═══════════════════════════════════════════════════════════════
    # ActionTrace → Lesson → Workflow → Skill promotion pipeline
    # ═══════════════════════════════════════════════════════════════

    def _traces_to_lessons(self) -> int:
        """Extract lessons from unconsolidated ActionTraces."""
        if not self._action_trace or not self._lesson:
            return 0

        unconsolidated = self._action_trace.get_unconsolidated(max_count=30)
        if not unconsolidated:
            return 0

        count = 0
        for trace in unconsolidated:
            if not self._llm:
                # Without LLM, extract simple lessons from failures
                if not trace.success and trace.failure_reason:
                    self._lesson.add(
                        content=f"Failed to '{trace.goal[:60]}': {trace.failure_reason[:100]}",
                        lesson_type="failure_analysis",
                        source_trace_id=trace.trace_id,
                        source_goal=trace.goal,
                        tags=trace.tags,
                    )
                    trace.lessons_extracted = True
                    count += 1
                continue

            # Use LLM to extract lessons
            steps_text = "\n".join(
                f"  {s.step_number}. {s.description} → {'OK' if s.success else f'FAIL: {s.error[:50]}'}"
                for s in trace.steps[:10]
            )
            prompt = f"""Analyze this action trace and extract lessons.

Goal: {trace.goal}
Outcome: {'SUCCESS' if trace.success else 'FAILURE'}
Steps:
{steps_text}
{f'Failure reason: {trace.failure_reason}' if trace.failure_reason else ''}

Extract 1-3 concise lessons in JSON:
{{"lessons": [{{"content": "...", "type": "success_pattern|failure_analysis|optimization|warning", "applicability": "keyword pattern"}}]]}}"""

            try:
                result = self._llm.generate(prompt=prompt, system_prompt="Extract lessons from action traces. Output only JSON.", max_tokens=300)
                if result.success:
                    import re
                    clean = result.content.strip()
                    if clean.startswith("```"):
                        lines = clean.split("\n")
                        clean = "\n".join(lines[1:])
                        if clean.endswith("```"):
                            clean = clean[:-3]
                        clean = clean.strip()
                    match = re.search(r'\{.*\}', clean, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        for l in data.get("lessons", []):
                            self._lesson.add(
                                content=l.get("content", ""),
                                lesson_type=l.get("type", "general"),
                                source_trace_id=trace.trace_id,
                                source_goal=trace.goal,
                                applicability=l.get("applicability", ""),
                                tags=trace.tags,
                            )
                            count += 1
            except Exception as e:
                logger.warning("Lesson extraction failed: %s", e)
                # Fallback simple extraction
                if not trace.success and trace.failure_reason:
                    self._lesson.add(
                        content=f"Failed: {trace.failure_reason[:100]}",
                        lesson_type="failure_analysis",
                        source_trace_id=trace.trace_id,
                        source_goal=trace.goal,
                    )
                    count += 1

            trace.lessons_extracted = True
            trace.consolidated = True

        return count

    def _traces_to_workflows(self) -> int:
        """Find repeated successful action patterns and promote to workflows."""
        if not self._action_trace or not self._workflow:
            return 0

        successful = self._action_trace.get_successful(count=50)
        if len(successful) < 3:
            return 0

        # Group traces by similar goals
        goal_groups: dict[str, list] = {}
        for trace in successful:
            key_words = " ".join(sorted(trace.goal.lower().split()[:3]))
            goal_groups.setdefault(key_words, []).append(trace)

        count = 0
        for key, traces in goal_groups.items():
            if len(traces) < 2:
                continue

            # Check if workflow already exists for this pattern
            existing = self._workflow.find_matching(traces[0].goal)
            if existing:
                # Update source traces
                for t in traces:
                    if t.trace_id not in existing.source_trace_ids:
                        existing.source_trace_ids.append(t.trace_id)
                continue

            # Extract common steps
            common_steps = self._extract_common_steps(traces)
            if len(common_steps) < 2:
                continue

            # Create workflow from most recent trace
            best = max(traces, key=lambda t: t.completed_at_ms)
            self._workflow.add(
                name=best.goal[:60],
                steps=common_steps,
                goal_pattern=key,
                description=f"Workflow from {len(traces)} successful traces",
                source_trace_ids=[t.trace_id for t in traces],
                tags=best.tags,
            )
            count += 1

        return count

    def _extract_common_steps(self, traces: list) -> list[dict[str, Any]]:
        """Extract common execution steps from multiple traces."""
        if not traces:
            return []

        # Use the trace with median step count as reference
        sorted_traces = sorted(traces, key=lambda t: len(t.steps))
        reference = sorted_traces[len(sorted_traces) // 2]

        steps = []
        for step in reference.steps:
            if step.success:
                steps.append({
                    "description": step.description,
                    "tool_call": step.tool_call,
                    "tool_args": step.tool_args,
                })
        return steps

    def _workflows_to_skills(self) -> int:
        """Promote reliable workflows to skills."""
        if not self._workflow or not self._skill:
            return 0

        active_workflows = self._workflow.get_active()
        count = 0

        for wf in active_workflows:
            total_uses = wf.success_count + wf.failure_count
            if total_uses < 3 or wf.success_rate < 0.7:
                continue

            # Check if skill already exists
            existing = self._skill.find_skill(wf.name)
            if existing:
                continue

            # Convert workflow steps to skill steps
            skill_steps = []
            for ws in wf.steps:
                skill_steps.append({
                    "description": ws.description,
                    "tool_call": ws.tool_call,
                    "tool_args": ws.tool_args,
                })

            self._skill.add_skill(
                name=wf.name,
                execution_steps=skill_steps,
                description=wf.description or f"Skill promoted from workflow {wf.workflow_id}",
                activation_conditions=f"Goal similar to: {wf.name}",
                goal_pattern=wf.goal_pattern,
                termination_conditions="All steps completed successfully",
                failure_handling="Retry once, then report failure",
                source_traces=wf.source_trace_ids,
                source_workflows=[wf.workflow_id],
                tags=wf.tags,
            )
            count += 1
            logger.info("Promoted workflow '%s' to skill (success_rate=%.0f%%)", wf.name, wf.success_rate * 100)

        return count

    def _log_consolidation(self, results: dict[str, Any]) -> None:
        """Log consolidation results."""
        try:
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(results, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning("Failed to log consolidation: %s", e)

    def get_status(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "last_consolidation_ms": self._last_consolidation_ms,
            "consolidation_count": self._consolidation_count,
            "auto_interval_hours": self._auto_interval_ms / 3_600_000,
        }
