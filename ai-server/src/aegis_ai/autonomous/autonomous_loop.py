"""Autonomous Loop — Desire-driven autonomous execution with self-scheduling.

Features:
- Desire-driven task execution: When desires are low, execute tasks to fulfill them
- Self-scheduling: AI decides when to be called next
- Fallback loop: Runs every 1 hour if not called
- LLM-based task selection and execution

Usage:
    loop = AutonomousLoop(llm_provider=llm, desire_system=desire, memory_system=memory)
    loop.start()
    loop.stop()
"""

from __future__ import annotations

import json
import logging
import os
import socket
import threading
import time
from pathlib import Path
from typing import Any

from aegis_ai.llm.json_utils import extract_json_object
from aegis_ai.llm.memory_context import build_shared_memory_context

logger = logging.getLogger("aegis_ai.autonomous.autonomous_loop")


def _check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False


class AutonomousLoop:
    """Desire-driven autonomous execution loop.

    The loop:
    1. Checks desire states
    2. If any desire is below threshold, generates and executes tasks
    3. After execution, updates desires
    4. Decides when to run next (self-scheduling)
    5. Falls back to 1-hour interval if no self-schedule
    """

    def __init__(
        self,
        llm_provider: Any = None,
        desire_system: Any = None,
        memory_system: Any = None,
        reflection_engine: Any = None,
        tool_broker: Any = None,
        world_state_store: Any = None,
        experiential_memory: Any = None,
        affect_system: Any = None,
        action_trace: Any = None,
        skill_memory: Any = None,
        workflow_memory: Any = None,
        lesson_memory: Any = None,
        observation_system: Any = None,
        curiosity_system: Any = None,
        policy_engine: Any = None,
        audit_log: Any = None,
        task_manager: Any = None,
        settings_resolver: Any = None,
        data_dir: str = "data/autonomous",
        desire_threshold: float = 4.0,
        max_tasks_per_cycle: int = 3,
        fallback_interval_seconds: int = 3600,
        frustration_threshold: float = 2.0,
    ) -> None:
        self._llm = llm_provider
        self._desire = desire_system
        self._memory = memory_system
        self._reflection = reflection_engine
        self._broker = tool_broker
        self._world = world_state_store
        self._settings_resolver = settings_resolver
        self._experiential = experiential_memory
        self._affect = affect_system
        self._action_trace = action_trace
        self._skill = skill_memory
        self._workflow = workflow_memory
        self._lesson = lesson_memory
        self._observation = observation_system
        self._curiosity = curiosity_system
        self._policy = policy_engine
        self._capability_retriever = None
        self._audit_log = audit_log
        self._task_manager = task_manager
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._desire_threshold = desire_threshold
        self._max_tasks = max_tasks_per_cycle
        self._fallback_interval = fallback_interval_seconds
        self._frustration_threshold = frustration_threshold

        self._running = False
        self._thread: threading.Thread | None = None
        self._next_run_ms: int = 0
        self._last_run_ms: int = 0
        self._execution_log: list[dict[str, Any]] = []
        self._pending_actionable_observations: list[dict[str, Any]] = []
        self._last_observation_ms: int = 0
        self._observation_interval_ms: int = 60_000  # 1 minute
        self._desire_check_interval_ms: int = 60_000  # 1 minute — desire check every tick
        self._last_desire_check_ms: int = 0
        self._last_desire_signature: str = ""
        self._min_execution_interval_ms: int = 60_000  # Minimum 1 minute between executions
        self._lock = threading.RLock()

        # Load state
        self._load()

    def _load(self) -> None:
        """Load autonomous loop state."""
        state_path = self._data_dir / "loop_state.json"
        if state_path.exists():
            try:
                with open(state_path, encoding="utf-8") as f:
                    data = json.load(f)
                self._next_run_ms = data.get("next_run_ms", 0)
                self._last_run_ms = data.get("last_run_ms", 0)
                logger.info("Loaded autonomous loop state")
            except Exception as e:
                logger.warning("Failed to load loop state: %s", e)

    def _save(self) -> None:
        """Save autonomous loop state."""
        state_path = self._data_dir / "loop_state.json"
        data = {
            "next_run_ms": self._next_run_ms,
            "last_run_ms": self._last_run_ms,
            "timestamp_ms": int(time.time() * 1000),
        }
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _is_frustration_above_threshold(self) -> bool:
        """Check if any desire frustration exceeds the threshold."""
        if not self._desire:
            return False
        for desire in self._desire.get_all_desires().values():
            if desire.hidden:
                continue
            frustration = max(0, desire.expected_value - desire.value)
            if frustration >= self._frustration_threshold:
                return True
        return False

    def get_threshold(self) -> float:
        """Get current frustration threshold."""
        with self._lock:
            return self._frustration_threshold

    def set_threshold(self, value: float) -> None:
        """Set frustration threshold (0.0-10.0)."""
        with self._lock:
            self._frustration_threshold = max(0.0, min(10.0, value))
            current = self._frustration_threshold
        logger.info("Frustration threshold set to %.1f", current)

    def start(self) -> None:
        """Start the autonomous loop in background."""
        with self._lock:
            if self._running:
                return

            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
        logger.info("Autonomous loop started")

    def set_observation_system(self, obs_system: Any) -> None:
        """Set the spontaneous observation system."""
        self._observation = obs_system

    def set_curiosity_system(self, curiosity_system: Any) -> None:
        """Set the curiosity-driven exploration system."""
        self._curiosity = curiosity_system

    def stop(self) -> None:
        """Stop the autonomous loop."""
        with self._lock:
            self._running = False
            thread = self._thread
        if thread:
            thread.join(timeout=5)
        logger.info("Autonomous loop stopped")

    def _run_loop(self) -> None:
        """Main loop — desire monitoring, observation, and execution."""
        while True:
            with self._lock:
                running = self._running
            if not running:
                break
            try:
                desire_triggered = self._monitor_desires()
                now = int(time.time() * 1000)

                # Spontaneous observation (every 1 minute)
                if self._observation and now - self._last_observation_ms >= self._observation_interval_ms:
                    try:
                        observations = self._observation.observe()
                        actionable = [o for o in observations if o.actionable and o.importance >= 0.7]
                        if actionable:
                            logger.info("Observation found %d actionable items", len(actionable))
                            self._pending_actionable_observations = [o.to_dict() for o in actionable[:5]]
                            desire_triggered = True
                    except Exception as e:
                        logger.warning("Observation failed: %s", e)
                    finally:
                        self._last_observation_ms = now

                # Check minimum interval since last execution
                time_since_last_run = now - self._last_run_ms
                can_execute = time_since_last_run >= self._min_execution_interval_ms

                if can_execute and (desire_triggered or now >= self._next_run_ms):
                    self._execute_cycle()
                else:
                    # Sleep until next event: next_run, observation, or 60s
                    sleep_ms = self._next_run_ms - now
                    if self._observation:
                        next_obs = self._last_observation_ms + self._observation_interval_ms - now
                        sleep_ms = min(sleep_ms, next_obs)
                    sleep_ms = max(sleep_ms, 1000)  # At least 1 second
                    time.sleep(min(sleep_ms / 1000, 60))
            except Exception as e:
                logger.error("Autonomous loop error: %s", e)
                time.sleep(60)

    def _monitor_desires(self) -> bool:
        """Desire monitoring — runs every tick.

        Returns True if any desire frustration exceeds the threshold,
        triggering immediate execution via LLM.
        """
        if not self._desire:
            return False
        self._desire.apply_decay()

        # Check frustration directly (same logic as _is_frustration_above_threshold)
        frustrated: list[dict[str, Any]] = []
        for name, desire in self._desire.get_all_desires().items():
            if desire.hidden:
                continue
            frustration = max(0, desire.expected_value - desire.value)
            if frustration >= self._frustration_threshold:
                frustrated.append({
                    "name": name,
                    "value": desire.value,
                    "expected": desire.expected_value,
                    "frustration": frustration,
                    "gap": frustration,
                })

        if frustrated:
            frustrated.sort(key=lambda d: d["gap"], reverse=True)
            top = frustrated[0]
            logger.info(
                "Desire check: %d frustrated. Top: %s=%.1f (frustration=%.1f, threshold=%.1f)",
                len(frustrated), top["name"], top["value"], top["frustration"], self._frustration_threshold,
            )
            signature = "|".join(
                f"{d['name']}:{round(float(d['frustration']), 1)}"
                for d in frustrated[:3]
            )
            now_ms = int(time.time() * 1000)
            should_evaluate = (
                signature != self._last_desire_signature
                or now_ms - self._last_desire_check_ms >= self._desire_check_interval_ms
            )
            if should_evaluate:
                self._llm_evaluate_desires(frustrated)
                self._last_desire_signature = signature
                self._last_desire_check_ms = now_ms
            return True
        return False

    def _llm_evaluate_desires(self, low_desires: list[dict[str, Any]]) -> None:
        """Log low desire states without LLM call."""
        summary = ", ".join(f"{d['name']}={d['value']:.1f}" for d in low_desires[:3])
        logger.info("Desire evaluation (no LLM): %d low — %s", len(low_desires), summary)
        self._log_audit_event(
            action="desire_evaluation",
            capability_id="none",
            decision="SKIP",
            reason=f"Desires already identified as low: {summary}. No LLM evaluation needed.",
            detail={"low_desires": [d["name"] for d in low_desires]},
        )

    def _check_repetition(self, tasks: list[dict[str, Any]], action_history: str) -> list[dict[str, Any]]:
        """Ask LLM to self-review tasks for semantic repetition before execution."""
        if not self._llm or not tasks:
            return tasks

        task_descriptions = []
        for i, t in enumerate(tasks):
            task_descriptions.append(
                f"Task {i+1}: {t.get('action', '')} (capability: {t.get('capability_id', '')})\n"
                f"  Purpose: {t.get('desire', '')} desire\n"
                f"  Args: {json.dumps(t.get('arguments', {}), ensure_ascii=False)[:100]}"
            )

        prompt = f"""You are reviewing autonomous tasks BEFORE execution to prevent repetition.

=== Recent Action History ===
{action_history}

=== Tasks Proposed for Execution ===
{chr(10).join(task_descriptions)}

For each task, determine:
1. Is this semantically similar to a recent action? (same purpose/target, even if different tool)
2. If similar, has enough changed to justify re-execution?
3. Should this task be executed, skipped, or replaced?

Respond with JSON:
{{
  "reviews": [
    {{
      "task_index": 1,
      "decision": "execute" | "skip" | "replace",
      "reason": "...",
      "similar_recent_action": "description of similar recent action, or empty",
      "why_not_duplicate": "why this is justified despite similarity, or why skipped"
    }}
  ]
}}"""

        try:
            result = self._llm.generate(
                prompt=prompt,
                system_prompt="You are AEGIS's repetition checker. Review tasks for semantic duplication. Output only JSON.",
                max_tokens=800,
                json_mode=True,
            )
            if not result.success:
                logger.warning("Repetition check failed, proceeding with all tasks")
                return tasks

            data = extract_json_object(result.content)
            reviews = data.get("reviews", [])

            approved_tasks = []
            for review in reviews:
                idx = review.get("task_index", 1) - 1
                decision = review.get("decision", "execute")
                reason = review.get("reason", "")
                similar = review.get("similar_recent_action", "")
                why_not = review.get("why_not_duplicate", "")

                if idx < 0 or idx >= len(tasks):
                    continue

                task = tasks[idx]
                task["repetition_check"] = {
                    "decision": decision,
                    "reason": reason,
                    "similar_recent_action": similar,
                    "why_not_duplicate": why_not,
                }
                task["why_this_is_not_repeating"] = why_not

                if decision == "execute":
                    approved_tasks.append(task)
                elif decision == "skip":
                    logger.info("Skipping task %s (repetition): %s", task.get("capability_id"), reason)
                    self._log_audit_event(
                        action="autonomous_repetition_skip",
                        capability_id=task.get("capability_id", ""),
                        decision="SKIP",
                        reason=reason,
                        detail={"similar_recent": similar, "desire": task.get("desire", "")},
                    )
                elif decision == "replace":
                    task["replaced_original"] = True
                    approved_tasks.append(task)

            return approved_tasks if approved_tasks else tasks
        except Exception as e:
            logger.warning("Repetition check error: %s", e)
            return tasks

    def _execute_cycle(self) -> None:
        """Execute autonomous tasks — only runs when scheduled or triggered."""
        logger.info("Starting autonomous execution cycle")
        with self._lock:
            self._last_run_ms = int(time.time() * 1000)

        if not self._desire:
            logger.warning("No desire system, using fallback interval")
            self._schedule_next(self._fallback_interval)
            return

        low_desires = self._get_low_desires()
        if not low_desires:
            if self._pending_actionable_observations:
                low_desires = [{
                    "name": "maintenance",
                    "value": 0.0,
                    "expected": 1.0,
                    "frustration": 1.0,
                    "gap": 1.0,
                }]
            else:
                logger.info("All desires above threshold, scheduling normal interval")
                self._schedule_next(self._fallback_interval)
                return

        desire_before = {}
        if self._desire:
            for name, desire in self._desire.get_all_desires().items():
                desire_before[name] = desire.value

        tasks = self._generate_tasks(low_desires)
        results = self._execute_tasks(tasks)

        needs_follow_up = any(
            not r.get("success") or "mention" in str(r.get("result", "")).lower()
            for r in results
        )
        if needs_follow_up:
            follow_up_results = self._self_regressive_loop(tasks, results, max_iterations=2)
            results.extend(follow_up_results)
        else:
            logger.info("Skipping follow-up: all tasks succeeded or no actionable results")

        if self._reflection is not None:
            failed_tasks = [(i, t, results[i]) for i, t in enumerate(tasks)
                           if i < len(results) and not results[i].get("success")]
            for i, task, task_result in failed_tasks[:2]:
                try:
                    reflection = self._reflection.reflect(
                        task_id=f"auto_{int(time.time() * 1000)}_{i}",
                        task_description=task.get("action", ""),
                        tool_results=[{
                            "status": "failed",
                            "capability_id": "autonomous_task",
                            "error": task_result.get("result", "")[:200],
                        }],
                        source_desire=task.get("desire", ""),
                        frustration=task.get("expected_impact", 0.0),
                        desire_before=desire_before,
                    )
                    logger.info("Reflection (failed only): %s — %s", reflection.outcome, reflection.summary[:100])
                except Exception as e:
                    logger.warning("Reflection failed: %s", e)

        self._update_desires(results)
        self._record_experiences(tasks, results)
        next_interval = self._decide_next_interval(results)
        self._schedule_next(next_interval)
        self._log_execution(tasks, results)
        self._save()

    def _get_low_desires(self) -> list[dict[str, Any]]:
        low = []
        for name, desire in self._desire.get_all_desires().items():
            frustration = max(0, desire.expected_value - desire.value)
            if frustration >= self._frustration_threshold:
                low.append({
                    "name": name,
                    "value": desire.value,
                    "expected": desire.expected_value,
                    "frustration": frustration,
                    "gap": frustration,
                })
        return sorted(low, key=lambda d: d["gap"], reverse=True)

    def _memory_root(self) -> Path:
        return self._data_dir.parent

    def _build_shared_llm_prompt(
        self,
        *,
        query: str,
        base_prompt: str,
        profile: str = "decision",
    ) -> tuple[str, dict[str, Any]]:
        memory_context = build_shared_memory_context(
            query=query,
            data_dir=str(self._memory_root()),
            profile=profile,
        )
        if memory_context.text:
            prompt = f"Shared memory context:\n{memory_context.text}\n\n{base_prompt}"
        else:
            prompt = base_prompt
        return prompt, memory_context.audit_detail()

    def _log_audit_event(
        self,
        *,
        action: str,
        capability_id: str,
        decision: str,
        reason: str,
        detail: dict[str, Any] | None = None,
    ) -> None:
        try:
            if self._audit_log is None:
                return
            self._audit_log.log_decision(
                action=action,
                capability_id=capability_id,
                decision=decision,
                reason=reason,
                actor="autonomous",
                detail=detail or {},
            )
        except Exception:
            logger.debug("Failed to write autonomous audit event", exc_info=True)

    def _record_failure_lesson(
        self,
        *,
        title: str,
        content: str,
        related_desire: str = "",
        related_task_id: str = "",
        failure_type: str = "",
    ) -> None:
        try:
            from aegis_ai.memory.memory_store import MemoryStore
            from aegis_ai.memory.memory_types import MemoryRecord, MemorySource, MemoryType, Sensitivity, Visibility

            store = MemoryStore(data_dir=str(self._memory_root() / "memory_store"))
            store.add_memory(MemoryRecord(
                memory_type=MemoryType.FAILURE_LESSON.value,
                title=title[:120],
                content=content[:500],
                source=MemorySource.SYSTEM_OBSERVATION.value,
                related_task_id=related_task_id,
                related_desire=related_desire,
                structured_data={"failure_type": failure_type} if failure_type else {},
                confidence=0.8,
                importance=0.8,
                visibility=Visibility.LLM_VISIBLE.value,
                sensitivity=Sensitivity.NORMAL.value,
            ))
        except Exception:
            logger.debug("Failed to record autonomous failure lesson", exc_info=True)

    def _recent_failure_penalty(self, source_desire: str) -> tuple[float, str]:
        if not source_desire:
            return 0.0, ""
        try:
            from aegis_ai.memory.memory_store import MemoryStore

            store = MemoryStore(data_dir=str(self._memory_root() / "memory_store"))
            failure_lessons = store.search_memories(
                memory_type="failure_lesson",
                related_desire=source_desire,
                min_importance=0.5,
                limit=3,
            )
            approval_lessons = store.search_memories(
                memory_type="approval_lesson",
                related_desire=source_desire,
                min_importance=0.5,
                limit=3,
            )
        except Exception:
            logger.debug("Failed to load memory penalties", exc_info=True)
            return 0.0, ""

        penalty = 0.0
        reasons: list[str] = []
        if failure_lessons:
            penalty += 0.3 * len(failure_lessons)
            reasons.append(f"{len(failure_lessons)} past failure lesson(s) for {source_desire}")
        rejected = [record for record in approval_lessons if "rejected" in record.content.lower()]
        if rejected:
            penalty += 0.2 * len(rejected)
            reasons.append(f"{len(rejected)} approval rejection lesson(s) for {source_desire}")
        return penalty, "; ".join(reasons)

    def _normalize_tool_call(
        self,
        *,
        catalog: Any,
        tool_call: dict[str, Any],
        valid_tool_names: set[str],
        source: str,
        related_desire: str,
    ) -> tuple[str, dict[str, Any], Any] | None:
        function_name = tool_call.get("function", "")
        arguments = tool_call.get("arguments", {})
        if function_name not in valid_tool_names:
            reason = f"LLM selected an unregistered tool name: {function_name or '<empty>'}"
            logger.warning("%s (%s)", reason, source)
            self._log_audit_event(
                action="autonomous_tool_selection",
                capability_id=function_name or "unknown",
                decision="REJECT",
                reason=reason,
                detail={"source": source, "tool_call": tool_call},
            )
            self._record_failure_lesson(
                title=f"Invalid autonomous tool: {function_name or 'unknown'}",
                content=reason,
                related_desire=related_desire,
                failure_type="capability_missing",
            )
            return None

        cap_id = catalog.tool_name_to_cap_id(function_name)
        manifest = catalog.resolve(cap_id)
        if manifest is None:
            reason = f"LLM selected a capability that is not in the catalog: {cap_id}"
            logger.warning("%s (%s)", reason, source)
            self._log_audit_event(
                action="autonomous_tool_selection",
                capability_id=cap_id,
                decision="REJECT",
                reason=reason,
                detail={"source": source, "tool_call": tool_call},
            )
            self._record_failure_lesson(
                title=f"Missing autonomous capability: {cap_id}",
                content=reason,
                related_desire=related_desire,
                failure_type="capability_missing",
            )
            return None

        return cap_id, arguments, manifest

    def _generate_tasks(self, low_desires: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self._llm:
            logger.error("No LLM provider — cannot generate tasks")
            return []

        desire_context = []
        for d in low_desires[:self._max_tasks]:
            desire_context.append(f"{d['name']}:gap={d['gap']:.1f}")
        pending_observations = list(self._pending_actionable_observations[:5])
        if pending_observations:
            desire_context.append("\nActionable observations:")
            for obs in pending_observations:
                desire_context.append(
                    f"- {obs.get('source', 'system')}: {obs.get('description', '')} "
                    f"(suggested: {obs.get('suggested_action', '')})"
                )
            self._pending_actionable_observations = []

        valid_cap_ids: set[str] = set()
        if self._broker:
            try:
                pc_ok = _check_port("localhost", 50052)
                room_ok = _check_port("localhost", 50055)
                browser_ok = _check_port("localhost", 50053)
                android_ok = _check_port("localhost", 50054)

                caps = self._broker.list_safe_capabilities()
                if caps:
                    for c in caps:
                        cap_id = c.id
                        if cap_id.startswith("pc-server.") and not pc_ok:
                            continue
                        if cap_id.startswith("android-server.") and not android_ok:
                            continue
                        if cap_id.startswith("browser-server.") and not browser_ok:
                            continue
                        if cap_id.startswith("room-server.") and not room_ok:
                            continue
                        valid_cap_ids.add(cap_id)
            except Exception:
                pass

        if not valid_cap_ids:
            logger.error("No valid capabilities available — cannot generate tasks")
            return []

        catalog = None
        if self._broker and hasattr(self._broker, '_catalog') and self._broker._catalog:
            catalog = self._broker._catalog

        if not catalog:
            logger.error("No capability catalog available — cannot generate tasks")
            return []

        query_parts = [d["name"] for d in low_desires[:self._max_tasks]]
        query_parts.extend(
            obs.get("description", "")
            for obs in pending_observations
            if obs.get("description")
        )
        retrieval_query = "; ".join(part for part in query_parts if part)

        action_history = self._build_action_history_summary(max_entries=10)

        if self._capability_retriever is not None:
            selection = self._capability_retriever.select_for_request(
                retrieval_query,
                {},
                top_k_schema=max(8, self._max_tasks * 2),
                top_k_summary=50,
                allowed_ids=valid_cap_ids,
            )
            tools = selection.retrieved_schema_tools
        else:
            tools = catalog.list_for_tools(valid_cap_ids)
        if not tools:
            logger.error("No tools generated from catalog")
            return []
        valid_tool_names = {tool["function"]["name"] for tool in tools}

        low_list = ", ".join(desire_context)
        prompt = f"""Low desires: {low_list}
        
        Recent: {action_history}
        
        Select up to {self._max_tasks} capabilities. Do NOT repeat recent actions by purpose.
        If no action needed, {{"no_action":true,"reason":"..."}}"""

        prompt, memory_meta = self._build_shared_llm_prompt(
            query=retrieval_query,
            base_prompt=prompt,
            profile="decision",
        )

        result = self._llm.generate_with_tools(
            prompt=prompt,
            tools=tools,
            system_prompt=(
                "Select tools for low desires. Do NOT repeat recent actions. "
                "If no action needed, respond with {\"no_action\":true}."
            ),
            max_tokens=600,
            context_meta=memory_meta,
        )

        if not result.success:
            logger.error("LLM task generation failed: %s", getattr(result, "error", "unknown"))
            return []

        if not result.tool_calls:
            if result.content:
                try:
                    no_action_data = extract_json_object(result.content)
                    if no_action_data.get("no_action"):
                        reason = no_action_data.get("reason", "LLM chose not to act")
                        logger.info("LLM chose no_action: %s", reason)
                        self._log_audit_event(
                            action="autonomous_no_action",
                            capability_id="none",
                            decision="SKIP",
                            reason=reason,
                            detail={"source": "task_generation", "llm_reason": reason},
                        )
                        return []
                except Exception:
                    pass
            logger.warning("LLM returned no tool calls")
            return []

        valid_tasks = []
        top_desire = low_desires[0]["name"] if low_desires else ""
        for i, tc in enumerate(result.tool_calls[:self._max_tasks]):
            desire = low_desires[i]["name"] if i < len(low_desires) else top_desire
            normalized = self._normalize_tool_call(
                catalog=catalog,
                tool_call=tc,
                valid_tool_names=valid_tool_names,
                source="task_generation",
                related_desire=desire,
            )
            if normalized is None:
                continue
            cap_id, args, manifest = normalized
            schema = manifest.input_schema or {}
            required = schema.get("required", [])
            missing = [r for r in required if r not in args or not args[r]]
            if missing:
                logger.warning("LLM task missing required args for %s: %s", cap_id, missing)
                continue
            penalty, penalty_reason = self._recent_failure_penalty(desire)
            if penalty >= 1.0:
                logger.info("Skipping %s due to memory penalty: %s", cap_id, penalty_reason)
                self._log_audit_event(
                    action="autonomous_task_penalty",
                    capability_id=cap_id,
                    decision="SKIP",
                    reason=penalty_reason or "memory penalty",
                    detail={"source": "task_generation", "desire": desire, "penalty": penalty},
                )
                continue
            valid_tasks.append({
                "desire": desire,
                "action": f"Execute {cap_id}",
                "capability_id": cap_id,
                "arguments": args,
                "expected_impact": max(0.1, 0.5 - min(penalty, 0.4)),
                "memory_penalty": penalty,
                "memory_penalty_reason": penalty_reason,
                "why_this_is_not_repeating": "",
            })

        if not valid_tasks:
            logger.warning("LLM returned no valid tasks")
        return valid_tasks

    def _execute_tasks(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute tasks with skill/workflow reuse and action tracing."""
        results = []

        for task in tasks:
            desire_name = task.get("desire", "unknown")
            action = task.get("action", "Unknown task")
            capability_id = task.get("capability_id", "")
            arguments = task.get("arguments", {})

            logger.info("Executing task: %s (for %s)", action[:50], desire_name)

            # Create task in TaskManager
            task_id = ""
            if self._task_manager:
                try:
                    task_obj = self._task_manager.create_task(
                        title=action[:100],
                        goal=action,
                        source="autonomous",
                        priority=0,
                    )
                    task_id = task_obj.get("task_id", "")
                    self._task_manager.start_task(task_id)
                except Exception:
                    pass

            # Begin action trace
            trace = None
            if self._action_trace:
                trace = self._action_trace.begin_trace(
                    goal=action, context=f"desire:{desire_name}",
                    desire_name=desire_name,
                )

            # Search for reusable skill
            skill_used = None
            if self._skill:
                skill_used = self._skill.find_skill(action)

            # Search for reusable workflow
            workflow_used = None
            if self._workflow and not skill_used:
                workflow_used = self._workflow.find_matching(action)

            # Search for relevant lessons
            relevant_lessons = []
            if self._lesson:
                relevant_lessons = self._lesson.get_relevant(action, count=3)

            if skill_used and trace:
                self._action_trace.add_step(trace, description=f"Using skill: {skill_used.name}", tool_call="skill_reuse")
            elif workflow_used and trace:
                self._action_trace.add_step(trace, description=f"Using workflow: {workflow_used.name}", tool_call="workflow_reuse")

            # Execute
            start_time = int(time.time() * 1000)
            success = False
            result_summary = ""
            failure_reason = ""
            full_output = {}

            if capability_id and self._broker:
                try:
                    from tool_broker import ToolExecutionRequest, ExecutionSource
                    request = ToolExecutionRequest(
                        capability_id=capability_id, arguments=arguments,
                        source=ExecutionSource.AUTONOMOUS,
                        reason=f"Autonomous desire-driven task: {desire_name}",
                    )
                    result = self._broker.execute(request)

                    if result.success:
                        output = result.output or {}
                        full_output = output
                        result_summary = str(output.get("result", output.get("count", "Done")))
                        if capability_id == "pc-server.screenshot.get_screenshot" and self._llm:
                            image_b64 = output.get("image_base64", "")
                            if image_b64:
                                result_summary = self._analyze_screenshot(image_b64, desire_name)
                        success = True
                    else:
                        error_details = result.output or {}
                        stderr = error_details.get("error", {}).get("details", {}).get("stderr", "") if isinstance(error_details.get("error"), dict) else ""
                        result_summary = f"Failed: {result.error}"
                        if stderr:
                            result_summary += f"\nstderr: {stderr}"
                        failure_reason = result.error
                        full_output = error_details

                    if trace:
                        self._action_trace.add_step(trace, description=action, tool_call=capability_id,
                                                     tool_args=arguments, tool_result=result_summary[:200],
                                                     success=success, error=failure_reason)
                except Exception as e:
                    result_summary = f"Error: {str(e)}"[:200]
                    failure_reason = str(e)
                    if trace:
                        self._action_trace.add_step(trace, description=action, tool_call=capability_id,
                                                     success=False, error=failure_reason)
            else:
                from aegis_ai.autonomous.planner import AutonomousPlanner
                planner = AutonomousPlanner(
                    llm_provider=self._llm, tool_broker=self._broker,
                    world_state_store=self._world, memory_store=self._memory,
                    policy_engine=self._policy,
                    data_dir=str(self._data_dir / "plans"),
                )
                plan = planner.plan(action, context=f"Desire: {desire_name}")
                if plan.status.value == "cancelled":
                    result_summary = plan.result_summary
                    failure_reason = "Cancelled by planner"
                else:
                    plan = planner.execute_plan(plan)
                    success = plan.status.value == "completed"
                    result_summary = plan.result_summary or f"Plan {plan.status.value}"
                    if not success:
                        failure_reason = plan.result_summary

            duration_ms = int(time.time() * 1000) - start_time

            # Record to skill/workflow memory
            if skill_used:
                self._skill.record_result(skill_used.skill_id, success, duration_ms, failure_reason)
            if workflow_used:
                self._workflow.record_result(workflow_used.workflow_id, success, duration_ms)

            # Complete action trace
            if trace:
                self._action_trace.complete_trace(
                    trace, success=success, result_summary=result_summary[:200],
                    failure_reason=failure_reason[:200],
                )

            if task_id and self._task_manager:
                try:
                    if success:
                        self._task_manager.complete_task(task_id, result_summary=result_summary[:200])
                    else:
                        self._task_manager.fail_task(task_id, error=failure_reason[:200])
                except Exception:
                    pass

            results.append({
                "desire": desire_name, "action": action,
                "capability_id": capability_id,
                "result": result_summary[:200], "success": success,
                "full_output": full_output,
                "skill_used": skill_used.skill_id if skill_used else None,
                "workflow_used": workflow_used.workflow_id if workflow_used else None,
            })

            # Execute post_action if defined
            post_action = task.get("post_action")
            if post_action and success and self._broker:
                post_cap_id = post_action.get("capability_id", "")
                post_args = post_action.get("arguments", {})
                if post_cap_id:
                    try:
                        from tool_broker import ToolExecutionRequest, ExecutionSource
                        post_request = ToolExecutionRequest(
                            capability_id=post_cap_id, arguments=post_args,
                            source=ExecutionSource.AUTONOMOUS,
                            reason=f"Post-action for {desire_name}",
                        )
                        post_result = self._broker.execute(post_request)
                        logger.info("Post-action %s: %s", post_cap_id, "OK" if post_result.success else post_result.error)
                    except Exception as e:
                        logger.warning("Post-action failed: %s", e)

        return results

    def _self_regressive_loop(
        self,
        initial_tasks: list[dict[str, Any]],
        initial_results: list[dict[str, Any]],
        max_iterations: int = 3,
    ) -> list[dict[str, Any]]:
        if not self._llm or not self._broker:
            return []
        if not initial_tasks or not initial_results:
            return []
        all_success = all(r.get("success") for r in initial_results)
        if all_success:
            has_mentions = any("mention" in str(r.get("result", "")).lower() for r in initial_results)
            if not has_mentions:
                logger.info("Skipping follow-up: all tasks succeeded, no actionable results")
                return []

        all_follow_ups: list[dict[str, Any]] = []
        current_tasks = initial_tasks
        current_results = initial_results
        for iteration in range(max_iterations):
            follow_up_tasks = self._generate_follow_up_tasks(current_tasks, current_results)
            if not follow_up_tasks:
                break

            logger.info("Self-regressive iteration %d: %d follow-up tasks", iteration + 1, len(follow_up_tasks))
            follow_up_results = self._execute_tasks(follow_up_tasks)
            all_follow_ups.extend(follow_up_results)

            current_tasks = follow_up_tasks
            current_results = follow_up_results

        return all_follow_ups

    def _generate_follow_up_tasks(
        self,
        previous_tasks: list[dict[str, Any]],
        previous_results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not self._llm:
            return []
        if not previous_tasks or not previous_results:
            return []

        known_failure_patterns = [
            "no executor", "unreachable", "connection refused",
            "timed out", "not found", "not available",
        ]
        has_actionable = False
        for result in previous_results:
            if not result.get("success"):
                err = str(result.get("result", "")).lower()
                is_known = any(p in err for p in known_failure_patterns)
                if not is_known:
                    has_actionable = True
                    break
            result_text = str(result.get("result", "")).lower()
            if "mention" in result_text or "directed at" in result_text:
                has_actionable = True
                break
        if not has_actionable:
            logger.info("Skipping follow-up: no actionable results")
            return []

        context_parts = []
        for i, (task, result) in enumerate(zip(previous_tasks, previous_results)):
            context_parts.append(
                f"Task {i+1}: {task.get('action', '')[:100]}\n"
                f"Result: {result.get('result', '')[:200]}\n"
                f"Success: {result.get('success', False)}\n"
                f"Desire: {task.get('desire', '')}"
            )

        catalog = None
        if self._broker and hasattr(self._broker, '_catalog') and self._broker._catalog:
            catalog = self._broker._catalog

        if not catalog:
            return []

        valid_cap_ids: set[str] = set()
        if self._broker:
            try:
                caps = self._broker.list_safe_capabilities()
                if caps:
                    for c in caps:
                        valid_cap_ids.add(c.id)
            except Exception:
                pass

        follow_up_query = "; ".join(
            part
            for part in [
                *(task.get("capability_id", "") for task in previous_tasks),
                *(task.get("action", "") for task in previous_tasks),
                *(result.get("result", "")[:120] for result in previous_results),
            ]
            if part
        )
        if self._capability_retriever is not None:
            selection = self._capability_retriever.select_for_request(
                follow_up_query,
                {},
                top_k_schema=8,
                top_k_summary=50,
                allowed_ids=valid_cap_ids or None,
            )
            tools = selection.retrieved_schema_tools
        else:
            tools = catalog.list_for_tools(valid_cap_ids)
        if not tools:
            return []
        valid_tool_names = {tool["function"]["name"] for tool in tools}

        prompt = f"""Based on the following task results, determine if any follow-up actions are needed.

Previous tasks:
{chr(10).join(context_parts)}

Rules:
- Only call a function if the result contains actionable information
- For social tasks: if there are mentions/messages directed at AEGIS, suggest replying
- For search tasks: if results are interesting, suggest saving to memory
- For system tasks: if anomalies detected, suggest investigation
- If no follow-up needed, do not call any function
- Do not repeat invalid or previously failed tool choices unless memory indicates a new reason they should work now"""

        try:
            result = self._llm.generate_with_tools(
                prompt=prompt,
                tools=tools,
                system_prompt="You are AEGIS deciding follow-up actions. Only call functions if follow-up is needed.",
                max_tokens=400,
                context_meta=None,
            )

            if not result.success or not result.tool_calls:
                return []

            valid_tasks = []
            for tc in result.tool_calls[:2]:
                desire = previous_tasks[0].get("desire", "") if previous_tasks else ""
                normalized = self._normalize_tool_call(
                    catalog=catalog,
                    tool_call=tc,
                    valid_tool_names=valid_tool_names,
                    source="follow_up_generation",
                    related_desire=desire,
                )
                if normalized is None:
                    continue
                cap_id, args, manifest = normalized
                schema = manifest.input_schema or {}
                required = schema.get("required", [])
                missing = [r for r in required if r not in args or not args[r]]
                if missing:
                    logger.warning("Follow-up task missing required args for %s: %s", cap_id, missing)
                    continue
                penalty, penalty_reason = self._recent_failure_penalty(desire)
                if penalty >= 1.0:
                    logger.info("Skipping follow-up %s due to memory penalty: %s", cap_id, penalty_reason)
                    self._log_audit_event(
                        action="autonomous_task_penalty",
                        capability_id=cap_id,
                        decision="SKIP",
                        reason=penalty_reason or "memory penalty",
                        detail={"source": "follow_up_generation", "desire": desire, "penalty": penalty},
                    )
                    continue
                valid_tasks.append({
                    "desire": desire,
                    "action": f"Follow-up: {cap_id}",
                    "capability_id": cap_id,
                    "arguments": args,
                    "expected_impact": max(0.1, 0.3 - min(penalty, 0.2)),
                    "memory_penalty": penalty,
                    "memory_penalty_reason": penalty_reason,
                })
            return valid_tasks
        except Exception as e:
            logger.debug("Follow-up generation failed: %s", e)
            return []

    def _analyze_screenshot(self, image_base64: str, desire_context: str) -> str:
        """Analyze a screenshot using multimodal LLM."""
        if not self._llm:
            return "Screenshot captured (no LLM for analysis)"

        vision_llm = self._llm
        if hasattr(self._llm, "_supports_vision") and not self._llm._supports_vision():
            try:
                from aegis_ai.llm.factory import create_multimodal_llm_provider

                vision_llm = create_multimodal_llm_provider(
                    settings_resolver=getattr(self, "_settings_resolver", None),
                )
            except Exception:
                vision_llm = self._llm

        if not hasattr(vision_llm, 'generate_with_image'):
            return "Screenshot captured (LLM does not support vision)"

        try:
            prompt = (
                f"You are AEGIS, an autonomous AI assistant. You just took a screenshot "
                f"while working on fulfilling your '{desire_context}' desire.\n\n"
                "Describe what you see in this screenshot concisely. Focus on:\n"
                "1. What applications/windows are open\n"
                "2. What the user appears to be doing\n"
                "3. Any interesting or notable elements\n"
                "4. Any opportunities to be helpful\n\n"
                "Keep your response under 200 words."
            )
            result = vision_llm.generate_with_image(
                prompt=prompt,
                image_base64=image_base64,
                system_prompt="You are AEGIS analyzing your own screenshot. Be concise and observational.",
                max_tokens=400,
                detail="low",
                profile="vision_observation",
            )
            if result.success:
                return result.content[:200]
            return "Screenshot captured (analysis failed)"
        except Exception as e:
            logger.warning("Screenshot analysis failed: %s", e)
            return "Screenshot captured (analysis error)"

    def _update_desires(self, results: list[dict[str, Any]]) -> None:
        """Update desires based on task results using fulfillment rules."""
        if not self._desire:
            return

        self._desire.apply_decay()

        from aegis_ai.desire.fulfillment import evaluate_task_result, TaskEffect

        for result in results:
            desire_name = result.get("desire", "")
            capability_id = result.get("capability_id", "")
            success = result.get("success", False)
            output = result.get("full_output", {})

            if not desire_name:
                continue

            desire = self._desire.get_desire(desire_name)
            if not desire:
                continue

            if desire.value >= desire.expected_value * 0.9:
                continue

            task_result = evaluate_task_result(
                capability_id=capability_id,
                tool_success=success,
                output=output,
                desire_name=desire_name,
            )

            logger.info(
                "Task evaluation: cap=%s effect=%s deltas=%s",
                capability_id, task_result.task_effect.value, task_result.desire_delta_hint,
            )

            if task_result.task_effect == TaskEffect.NO_EFFECT:
                continue

            for d_name, delta in task_result.desire_delta_hint.items():
                if delta != 0.0:
                    current = self._desire.get_desire(d_name)
                    if current:
                        new_val = max(0.0, min(10.0, current.value + delta))
                        self._desire.update_value(
                            d_name, new_val,
                            reason=f"{task_result.summary} ({capability_id})",
                        )
                        logger.info("Desire %s: %.1f -> %.1f (delta=%.1f)", d_name, current.value, new_val, delta)

        self._desire.save()

    def _load_recent_history(self, max_entries: int = 5) -> list[dict[str, Any]]:
        log_path = self._data_dir / "execution_log.jsonl"
        if not log_path.exists():
            return []
        try:
            lines = log_path.read_text(encoding="utf-8").strip().split("\n")
            entries = []
            import json as _json
            for line in lines[-max_entries:]:
                if line.strip():
                    entries.append(_json.loads(line))
            return entries
        except Exception:
            return []

    def _build_action_history_summary(self, max_entries: int = 20) -> str:
        """Build a human-readable summary of recent autonomous actions for LLM context."""
        history = self._load_recent_history(max_entries=max_entries)
        if not history:
            return "No recent autonomous actions."

        now_ms = int(time.time() * 1000)
        lines = []
        for entry in history:
            ts = entry.get("timestamp_ms", 0)
            age_min = max(0, (now_ms - ts) // 60_000)
            age_str = f"{age_min}分前" if age_min < 60 else f"{age_min // 60}時間前"

            for i, task in enumerate(entry.get("tasks", [])):
                result = entry.get("results", [])[i] if i < len(entry.get("results", [])) else {}
                desire = task.get("desire", "")
                action_goal = task.get("action_goal", task.get("action", ""))
                what_was_done = task.get("what_was_done", task.get("capability_id", ""))
                result_summary = result.get("result_summary", result.get("result", ""))
                success = result.get("success", False)
                changed_state = task.get("changed_state", "状態変化なし")
                not_repeat_unless = task.get("not_repeat_unless", "")

                status = "成功" if success else "失敗"
                line = (
                    f"- [{age_str}] {desire}目的: {action_goal}\n"
                    f"  実行内容: {what_was_done}\n"
                    f"  結果: {status} — {result_summary[:150]}\n"
                    f"  状態変化: {changed_state}"
                )
                if not_repeat_unless:
                    line += f"\n  再実行条件: {not_repeat_unless}"
                lines.append(line)

        if not lines:
            return "No recent autonomous actions."

        return "Recent autonomous actions (newest first):\n" + "\n".join(lines[-20:])

    def _summarize_action(self, task: dict[str, Any], result: dict[str, Any]) -> str:
        """Generate a natural language description of what was done."""
        cap_id = task.get("capability_id", "")
        action = task.get("action", "")

        action_descriptions = {
            "pc-server.system.get_os_info": "OS情報を確認した",
            "pc-server.system.get_screen_size": "画面サイズを確認した",
            "pc-server.screenshot.get_screenshot": "スクリーンショットを取得し画面内容を確認した",
            "pc-server.window.get_active_window": "アクティブウィンドウを確認した",
            "ai-server.memory.search": "メモリを検索した",
            "ai-server.memory.save": "メモリに保存した",
            "ai-server.agora.read_posts": "AGORAの投稿を確認した",
            "browser-server.page.browse": f"ブラウザで操作した: {task.get('arguments', {}).get('task', '')[:80]}",
        }

        if cap_id in action_descriptions:
            return action_descriptions[cap_id]

        args = task.get("arguments", {})
        if "shell" in cap_id and "command" in args:
            return f"シェルコマンドを実行した: {str(args['command'])[:80]}"
        return action or cap_id or "不明な操作"

    def _summarize_state_change(self, task: dict[str, Any], result: dict[str, Any]) -> str:
        """Summarize what state change occurred."""
        if not result.get("success"):
            return "失敗のため状態変化なし"
        cap_id = task.get("capability_id", "")
        if "screenshot" in cap_id:
            return "スクリーンショットを取得し、画面状態を把握した"
        if "memory" in cap_id and "save" in cap_id:
            return "メモリに新しい情報を保存した"
        if "agora" in cap_id:
            return "AGORAの状態を確認した"
        return "操作を実行し結果を確認した"

    def _determine_repeat_condition(self, task: dict[str, Any], result: dict[str, Any]) -> str:
        """Determine under what condition this action should be repeated."""
        if not result.get("success"):
            return "問題が解決していない場合は再試行可能"
        cap_id = task.get("capability_id", "")
        if "screenshot" in cap_id:
            return "ユーザーの指示があるか、画面に変化があった場合のみ再実行"
        if "system.get_os_info" in cap_id or "system.get_screen_size" in cap_id:
            return "システム設定を変更した後のみ再確認"
        if "agora" in cap_id:
            return "新しい投稿がある可能性がある場合（時間経過後）"
        if "memory.search" in cap_id:
            return "新しい情報が必要な場合"
        return "新しい情報や状態変化がある場合のみ再実行"

    def _record_experiences(self, tasks: list[dict[str, Any]], results: list[dict[str, Any]]) -> None:
        for i, task in enumerate(tasks):
            result = results[i] if i < len(results) else {}
            success = result.get("success", False)

            if not success:
                continue

            action = task.get("action", "Unknown task")
            capability_id = task.get("capability_id", result.get("capability_id", ""))
            observation = result.get("result", "")
            full_output = result.get("full_output", {})
            desire_name = task.get("desire", "")

            if self._experiential:
                try:
                    self._experiential.record_experience(
                        action=action,
                        observation=observation,
                        context=f"autonomous_{desire_name}",
                        related_desire=desire_name,
                        outcome_success=success,
                    )
                except Exception as e:
                    logger.warning("Failed to record experience: %s", e)

            if self._memory and hasattr(self._memory, 'add_conversation'):
                try:
                    user_msg = f"[Autonomous] {action}"
                    detail = f"Capability: {capability_id}, Result: {observation[:100]}"
                    bot_msg = f"{detail}. Success: {success}"
                    self._memory.add_conversation(user_msg, bot_msg)
                except Exception as e:
                    logger.warning("Failed to record to AdvancedMemory: %s", e)

            if self._action_trace:
                try:
                    trace = self._action_trace.begin_trace(
                        goal=action, context=f"autonomous_record:{desire_name}",
                        desire_name=desire_name,
                    )
                    self._action_trace.add_step(
                        trace, description=action,
                        tool_call="autonomous_task",
                        tool_result=observation[:200],
                        success=success,
                    )
                    self._action_trace.complete_trace(
                        trace, success=success,
                        result_summary=observation[:200],
                    )
                except Exception as e:
                    logger.warning("Failed to record action trace: %s", e)

            if self._affect:
                try:
                    self._affect.appraise_from_experience(
                        action=action,
                        observation=observation,
                        success=success,
                        desire_name=desire_name,
                    )
                except Exception as e:
                    logger.warning("Failed to appraise emotion: %s", e)

    def _decide_next_interval(self, results: list[dict[str, Any]]) -> int:
        """Decide when to run next using lightweight program logic (no LLM)."""
        if not self._desire:
            logger.info("No desire — using fallback interval %ds", self._fallback_interval)
            return self._fallback_interval

        desires = self._desire.get_all_desires()
        low_count = 0
        total_gap = 0.0
        for desire in desires.values():
            if desire.hidden:
                continue
            gap = max(0, desire.expected_value - desire.value)
            if gap >= self._frustration_threshold:
                low_count += 1
            total_gap += gap

        success_count = sum(1 for r in results if r.get("success"))
        total_count = len(results)
        fail_count = total_count - success_count

        if low_count == 0:
            interval = self._fallback_interval * 2
            reason = "all desires healthy"
        elif low_count >= 3:
            interval = 300
            reason = f"{low_count} desires critically low"
        elif fail_count > success_count and total_count > 0:
            interval = 900
            reason = f"{fail_count}/{total_count} tasks failed, backing off"
        elif total_count == 0:
            interval = self._fallback_interval
            reason = "no tasks executed"
        else:
            interval = max(600, int(self._fallback_interval * (1.0 - total_gap / 30.0)))
            reason = f"{low_count} low desires, gap managed"

        interval = max(300, min(7200, interval))
        logger.info("Next autonomous run in %d seconds: %s", interval, reason)
        return interval

    def _schedule_next(self, interval_seconds: int) -> None:
        """Schedule the next execution."""
        with self._lock:
            self._next_run_ms = int(time.time() * 1000) + (interval_seconds * 1000)
        logger.info("Next autonomous run scheduled in %d seconds", interval_seconds)

    def _log_execution(self, tasks: list[dict[str, Any]], results: list[dict[str, Any]]) -> None:
        """Log execution for history with semantic summaries."""
        semantic_tasks = []
        for i, task in enumerate(tasks):
            result = results[i] if i < len(results) else {}
            semantic_task = {
                **task,
                "action_goal": task.get("action", ""),
                "what_was_done": self._summarize_action(task, result),
                "result_summary": result.get("result", "")[:200],
                "changed_state": self._summarize_state_change(task, result),
                "not_repeat_unless": self._determine_repeat_condition(task, result),
            }
            semantic_tasks.append(semantic_task)

        entry = {
            "timestamp_ms": int(time.time() * 1000),
            "tasks": semantic_tasks,
            "results": results,
            "next_run_ms": self._next_run_ms,
        }
        with self._lock:
            self._execution_log.append(entry)

        log_path = self._data_dir / "execution_log.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_status(self) -> dict[str, Any]:
        """Get autonomous loop status."""
        now = int(time.time() * 1000)
        with self._lock:
            return {
                "running": self._running,
                "last_run_ms": self._last_run_ms,
                "next_run_ms": self._next_run_ms,
                "seconds_until_next": max(0, (self._next_run_ms - now) / 1000),
                "execution_count": len(self._execution_log),
                "frustration_threshold": self._frustration_threshold,
            }

    def trigger_now(self) -> dict[str, Any]:
        """Manually trigger an autonomous cycle."""
        logger.info("Manual trigger requested")
        self._execute_cycle()
        return self.get_status()
