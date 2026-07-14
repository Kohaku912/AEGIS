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

import base64
import io
import json
import logging
import os
import re
import threading
import time
from pathlib import Path
from typing import Any

from aegis_ai.llm.json_utils import extract_json_object
from aegis_ai.llm.memory_context import build_shared_memory_context

logger = logging.getLogger("aegis_ai.autonomous.autonomous_loop")

_LOG_TEXT_LIMIT = 2000
_LOG_LIST_LIMIT = 20
_LOG_DICT_LIMIT = 80
_SENSITIVE_KEY_RE = re.compile(r"(token|secret|password|cookie|api[_-]?key|authorization|credential)", re.I)
_SECRET_TEXT_RE = re.compile(
    r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{16,}|(sk-[A-Za-z0-9_-]{20,})|"
    r"((?:token|secret|password|api[_-]?key)\s*[:=]\s*)\S+"
)
_TRIVIAL_RESULTS = frozenset(
    {"no new posts", "done", "no memory found", "ok", "no new messages", "no drafts", "no new data"}
)


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
        status_manager: Any = None,
        settings_resolver: Any = None,
        data_dir: str = "data/autonomous",
        desire_threshold: float = 4.0,
        max_tasks_per_cycle: int = 3,
        fallback_interval_seconds: int = 1800,
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
        self._status_manager = status_manager
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._artifact_dir = self._data_dir / "artifacts"
        self._artifact_dir.mkdir(parents=True, exist_ok=True)

        self._desire_threshold = desire_threshold
        self._max_tasks = max_tasks_per_cycle
        self._fallback_interval = fallback_interval_seconds
        self._frustration_threshold = frustration_threshold
        self._pressure_threshold = 5.0  # Pressure-based trigger threshold

        self._running = False
        self._thread: threading.Thread | None = None
        self._next_run_ms: int = 0
        self._last_run_ms: int = 0
        self._execution_log: list[dict[str, Any]] = []
        self._pending_actionable_observations: list[dict[str, Any]] = []
        self._last_observation_ms: int = 0
        self._observation_interval_ms: int = 60_000  # 1 minute
        self._desire_check_interval_ms: int = 60_000  # 1 minute
        self._last_desire_check_ms: int = 0
        self._last_desire_signature: str = ""
        self._last_pressure_signature: str = ""
        self._min_execution_interval_ms: int = 60_000  # Minimum 1 minute between executions
        self._min_llm_interval_ms: int = int(os.environ.get("AEGIS_MIN_LLM_INTERVAL_MS", 1_800_000))
        self._llm_usage_window_ms: int = int(os.environ.get("AEGIS_AUTONOMOUS_LLM_USAGE_WINDOW_MS", 3_600_000))
        self._llm_usage_token_limit: int = int(os.environ.get("AEGIS_AUTONOMOUS_LLM_USAGE_TOKEN_LIMIT", 80_000))
        self._last_llm_call_ms: int = 0
        self._last_decision: str = ""
        self._last_decision_ms: int = 0
        self._last_action_ms: int = 0
        self._available_capability_count: int = 0
        self._selected_tool_count: int = 0
        self._last_no_action_reason: str = ""
        self._last_candidate_capability_ids: list[str] = []
        self._last_decision_axes: dict[str, float] = {
            "user_commitment": 0.0,
            "system_health": 0.0,
            "learning": 0.0,
            "curiosity": 0.0,
        }
        self._consecutive_no_action: int = 0
        self._health_alert_manager: Any = None
        self._last_health_check_ms: int = 0
        self._health_check_interval_ms: int = 300_000  # 5 minutes
        self._last_skip_reason: str = ""
        self._lock = threading.RLock()
        self._capability_metadata_cache: dict[str, dict[str, Any]] = {}

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
                self._last_llm_call_ms = data.get("last_llm_call_ms", 0)
                self._last_pressure_signature = data.get("last_pressure_signature", "")
                self._last_skip_reason = data.get("last_skip_reason", "")
                self._last_decision = data.get("last_decision", "")
                self._last_decision_ms = data.get("last_decision_ms", 0)
                self._last_action_ms = data.get("last_action_ms", 0)
                self._available_capability_count = data.get("available_capability_count", 0)
                self._selected_tool_count = data.get("selected_tool_count", 0)
                self._last_no_action_reason = data.get("last_no_action_reason", "")
                self._last_candidate_capability_ids = data.get("last_candidate_capability_ids", [])
                self._last_decision_axes = data.get("last_decision_axes", self._last_decision_axes)
                self._consecutive_no_action = data.get("consecutive_no_action", 0)
                logger.info("Loaded autonomous loop state")
            except Exception as e:
                logger.warning("Failed to load loop state: %s", e)

    def _save(self) -> None:
        """Save autonomous loop state."""
        state_path = self._data_dir / "loop_state.json"
        data = {
            "next_run_ms": self._next_run_ms,
            "last_run_ms": self._last_run_ms,
            "last_llm_call_ms": self._last_llm_call_ms,
            "last_pressure_signature": self._last_pressure_signature,
            "last_skip_reason": self._last_skip_reason,
            "last_decision": self._last_decision,
            "last_decision_ms": self._last_decision_ms,
            "last_action_ms": self._last_action_ms,
            "available_capability_count": self._available_capability_count,
            "selected_tool_count": self._selected_tool_count,
            "last_no_action_reason": self._last_no_action_reason,
            "last_candidate_capability_ids": self._last_candidate_capability_ids[-30:],
            "last_decision_axes": self._last_decision_axes,
            "consecutive_no_action": self._consecutive_no_action,
            "timestamp_ms": int(time.time() * 1000),
        }
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _is_pressure_above_threshold(self) -> bool:
        """Check if any desire pressure exceeds the threshold."""
        if not self._desire:
            return False
        for desire in self._desire.get_all_desires().values():
            if desire.hidden:
                continue
            if desire.pressure >= self._pressure_threshold:
                return True
        return False

    def get_threshold(self) -> float:
        """Get current pressure threshold."""
        with self._lock:
            return self._pressure_threshold

    def set_threshold(self, value: float) -> None:
        """Set pressure threshold (0.0-10.0)."""
        with self._lock:
            self._pressure_threshold = max(0.0, min(10.0, value))
            current = self._pressure_threshold
        logger.info("Pressure threshold set to %.1f", current)

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

    def set_health_alert_manager(self, health_alert_manager: Any) -> None:
        """Set the health alert manager for periodic health checks."""
        self._health_alert_manager = health_alert_manager

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

                # Health check cycle (every 5 minutes)
                if self._health_alert_manager and now - self._last_health_check_ms >= self._health_check_interval_ms:
                    try:
                        new_alerts = self._health_alert_manager.check_system_health()
                        if new_alerts:
                            logger.info("Health check: %d new alerts", len(new_alerts))
                    except Exception as e:
                        logger.warning("Health check failed: %s", e)
                    finally:
                        self._last_health_check_ms = now

                # Spontaneous observation (every 1 minute)
                if self._observation and now - self._last_observation_ms >= self._observation_interval_ms:
                    try:
                        observations = self._observation.observe()
                        actionable = [o for o in observations if o.actionable and o.importance >= 0.7]
                        if actionable:
                            logger.info("Observation found %d actionable items", len(actionable))
                            self._pending_actionable_observations = [o.to_dict() for o in actionable[:5]]
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

        Returns True if any desire pressure exceeds the threshold,
        triggering execution. No LLM call — pressure-based only.
        """
        if not self._desire:
            return False
        self._desire.apply_decay()

        # Check pressure-based trigger
        pressured: list[dict[str, Any]] = []
        for name, desire in self._desire.get_all_desires().items():
            if desire.hidden:
                continue
            if desire.pressure >= self._pressure_threshold:
                pressured.append({
                    "name": name,
                    "value": desire.value,
                    "pressure": desire.pressure,
                    "drift_rate": desire.drift_rate,
                })

        if pressured:
            pressured.sort(key=lambda d: d["pressure"], reverse=True)
            top = pressured[0]
            logger.info(
                "Pressure check: %d pressured. Top: %s=%.1f (pressure=%.1f, threshold=%.1f)",
                len(pressured), top["name"], top["value"], top["pressure"], self._pressure_threshold,
            )
            return True

        # Log skip reason (rate-limited to once per minute)
        now_ms = int(time.time() * 1000)
        if now_ms - self._last_desire_check_ms >= self._desire_check_interval_ms:
            self._last_skip_reason = "all_pressure_below_threshold"
            self._last_desire_check_ms = now_ms
            logger.debug("All desires below pressure threshold %.1f", self._pressure_threshold)
        return False

    def _llm_evaluate_desires(self, low_desires: list[dict[str, Any]]) -> None:
        """Log desire states — no LLM call, just audit logging."""
        summary = ", ".join(f"{d['name']}={d.get('value', 0):.1f}" for d in low_desires[:3])
        logger.info("Desire evaluation (no LLM): %d — %s", len(low_desires), summary)

    def _preflight_check(self) -> tuple[bool, str]:
        """Gate before LLM calls. Returns (should_proceed, reason)."""
        if not self._desire:
            return False, "no_desire_system"

        self._desire.apply_decay()
        pressure_state = self._desire.get_pressure_state()
        max_pressure = max((d["pressure"] for d in pressure_state.values()), default=0.0)

        if max_pressure < self._pressure_threshold:
            return False, f"all_pressure_below_threshold (max={max_pressure:.1f} < {self._pressure_threshold:.1f})"

        if not self._llm:
            return False, "provider_unavailable"

        high_usage, usage_reason = self._llm_usage_high()
        if high_usage:
            return False, usage_reason

        return True, "ok"

    def _llm_usage_high(self) -> tuple[bool, str]:
        if self._llm_usage_token_limit <= 0 or self._audit_log is None:
            return False, ""
        try:
            from aegis_ai.observability.llm_usage.audit_extractor import extract_traces

            if hasattr(self._audit_log, "read_all"):
                entries = self._audit_log.read_all()[-5000:]
            elif hasattr(self._audit_log, "list_recent"):
                raw_entries = self._audit_log.list_recent(5000)
                entries = [getattr(entry, "__dict__", entry) for entry in raw_entries]
            else:
                return False, ""
            now_ms = int(time.time() * 1000)
            cutoff = now_ms - self._llm_usage_window_ms
            traces = [trace for trace in extract_traces(entries) if trace.timestamp_ms >= cutoff]
            total_tokens = sum(trace.tokens_used for trace in traces)
            if total_tokens >= self._llm_usage_token_limit:
                return True, (
                    "llm_usage_high "
                    f"(tokens={total_tokens} >= limit={self._llm_usage_token_limit}, "
                    f"window_ms={self._llm_usage_window_ms})"
                )
        except Exception:
            logger.debug("Autonomous LLM usage preflight failed", exc_info=True)
        return False, ""

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
                system_prompt=(
                    "You are AEGIS's repetition checker. Review tasks for semantic duplication. "
                    "Output only JSON."
                ),
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
        if not getattr(self, "_audit_group_active", False):
            from aegis_ai.audit.context import audit_group

            group_id = f"autonomous_{int(time.time() * 1000)}"
            with audit_group(group_id, group_type="autonomous", group_title="Autonomous execution cycle"):
                self._audit_group_active = True
                try:
                    return self._execute_cycle()
                finally:
                    self._audit_group_active = False
        logger.info("Starting autonomous execution cycle")
        with self._lock:
            self._last_run_ms = int(time.time() * 1000)

        if not self._desire:
            logger.warning("No desire system, using fallback interval")
            self._schedule_next(self._fallback_interval)
            self._save()
            return

        should_proceed, preflight_reason = self._preflight_check()
        if not should_proceed:
            logger.info("Preflight blocked: %s", preflight_reason)
            self._last_skip_reason = preflight_reason
            # Skip audit log for routine pressure checks
            if not preflight_reason.startswith("all_pressure_below_threshold"):
                self._log_audit_event(
                    action="autonomous_preflight",
                    capability_id="none",
                    decision="SKIP",
                    reason=preflight_reason,
                    detail={"source": "preflight_check"},
                )
            next_interval = self._fallback_interval
            if not preflight_reason.startswith("all_pressure_below_threshold"):
                next_interval = 60
            self._schedule_next(next_interval)
            self._save()
            return

        low_desires = self._get_low_desires()
        if not low_desires:
            if self._pending_actionable_observations:
                low_desires = [{
                    "name": "user_support",
                    "value": 0.0,
                    "expected": 1.0,
                    "pressure": 5.0,
                    "gap": 1.0,
                }]
            else:
                logger.info("All desires above threshold, scheduling normal interval")
                self._schedule_next(self._fallback_interval)
                self._save()
                return

        now_llm = int(time.time() * 1000)
        if now_llm - self._last_llm_call_ms < self._min_llm_interval_ms:
            remaining = (self._min_llm_interval_ms - (now_llm - self._last_llm_call_ms)) // 1000
            logger.info("LLM interval gate: %ds remaining until next LLM call", remaining)
            self._last_skip_reason = f"llm_interval_gate ({remaining}s remaining)"
            self._schedule_next(max(1, min(60, remaining)))
            self._save()
            return

        self._last_pressure_signature = self._desire.get_pressure_signature()

        desire_before = {}
        if self._desire:
            for name, desire in self._desire.get_all_desires().items():
                desire_before[name] = desire.value

        tasks = self._generate_tasks(low_desires)
        results = self._execute_tasks(tasks)

        if results:
            follow_up_results = self._self_regressive_loop(tasks, results, max_iterations=2)
            results.extend(follow_up_results)
        else:
            logger.info("Skipping follow-up: no task results")

        if tasks:
            self._last_action_ms = int(time.time() * 1000)
            self._last_skip_reason = ""

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
            if desire.hidden:
                continue
            if desire.pressure >= self._pressure_threshold:
                low.append({
                    "name": name,
                    "value": desire.value,
                    "expected": desire.expected_value,
                    "pressure": desire.pressure,
                    "drift_rate": desire.drift_rate,
                    "gap": desire.pressure,
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
        has_social_actions: bool = True,
    ) -> tuple[str, dict[str, Any]]:
        memory_context = build_shared_memory_context(
            query=query,
            data_dir=str(self._memory_root()),
            profile=profile,
            has_social_actions=has_social_actions,
        )
        if memory_context.text:
            prompt = f"Shared memory context:\n{memory_context.text}\n\n{base_prompt}"
        else:
            prompt = base_prompt
        return prompt, memory_context.audit_detail()

    def _has_social_actions(self, valid_cap_ids: set[str]) -> bool:
        return any(
            cap_id.startswith("ai-server.agora.") or cap_id == "ai-server.social.list_drafts"
            for cap_id in valid_cap_ids
        )

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

    def _desire_action_guides(self, low_desires: list[dict[str, Any]]) -> list[dict[str, Any]]:
        guide_map = {
            "user_support": {
                "goal": "Find unfinished user requests, pending commitments, approval waits, or useful local context.",
                "preferred_capabilities": [
                    "ai-server.commitment.list",
                    "ai-server.memory.search",
                    "ai-server.situation.get",
                    "pc-server.screenshot.get_screenshot",
                ],
            },
            "social": {
                "goal": "Check unread social context and decide whether a draft or approved social action is needed.",
                "preferred_capabilities": [
                    "ai-server.agora.read_posts",
                    "ai-server.social.list_drafts",
                    "ai-server.memory.search",
                ],
            },
            "growth": {
                "goal": "Learn from recent state, failures, project context, or stored workspace information.",
                "preferred_capabilities": [
                    "ai-server.memory.search",
                    "ai-server.workspace.list_files",
                    "dev-server.repo.status",
                    "browser-server.page.browse",
                ],
            },
        }
        guides: list[dict[str, Any]] = []
        for desire in low_desires:
            name = str(desire.get("name", ""))
            meta = guide_map.get(name)
            if not meta:
                continue
            guides.append({
                "desire": name,
                "pressure": desire.get("pressure", 0.0),
                "goal": meta["goal"],
                "preferred_capabilities": list(meta["preferred_capabilities"]),
            })
        return guides

    def _build_decision_axes(self, low_desires: list[dict[str, Any]]) -> dict[str, float]:
        """Summarize operational priorities without adding desire dimensions."""
        axes = {
            "user_commitment": 0.0,
            "system_health": 0.0,
            "learning": 0.0,
            "curiosity": 0.0,
        }
        desire_to_axis = {
            "user_support": "user_commitment",
            "social": "user_commitment",
            "growth": "learning",
        }
        for desire in low_desires:
            axis = desire_to_axis.get(str(desire.get("name", "")))
            if axis:
                pressure = float(desire.get("pressure", desire.get("gap", 0.0)) or 0.0)
                axes[axis] = max(axes[axis], pressure)

        if self._pending_actionable_observations:
            axes["system_health"] = 1.0
        if self._status_manager is not None:
            try:
                snapshot = self._status_manager.get_snapshot()
                statuses = snapshot.values() if isinstance(snapshot, dict) else snapshot
                unhealthy = sum(
                    1
                    for item in statuses
                    if str(
                        item.get("status", "")
                        if isinstance(item, dict)
                        else getattr(item, "status", "")
                    ).lower()
                    not in {"online", "healthy", "ok", "disabled", "unconfigured"}
                )
                axes["system_health"] = max(axes["system_health"], float(unhealthy))
            except Exception:
                logger.debug("Unable to summarize system health decision axis", exc_info=True)
        if self._curiosity is not None:
            axes["curiosity"] = 1.0
        return axes

    def _intrinsic_task_hints(self, valid_cap_ids: set[str]) -> list[dict[str, Any]]:
        if not self._desire:
            return []
        try:
            from aegis_ai.desire.intrinsic_task_generator import IntrinsicTaskGenerator

            generator = IntrinsicTaskGenerator(
                pressure_threshold=self._pressure_threshold,
                available_capabilities=valid_cap_ids,
            )
            hints = []
            for task in generator.generate(self._desire.create_snapshot())[:8]:
                hints.append({
                    "desire": task.source_desire,
                    "title": task.title,
                    "description": task.description,
                    "required_capabilities": [
                        cap_id for cap_id in task.required_capabilities if cap_id in valid_cap_ids
                    ],
                    "expected_desire_effects": task.expected_desire_effects,
                })
            return hints
        except Exception:
            logger.debug("Failed to build intrinsic task hints", exc_info=True)
            return []

    def _representative_capability_ids(
        self,
        low_desires: list[dict[str, Any]],
        valid_cap_ids: set[str],
        intrinsic_hints: list[dict[str, Any]],
    ) -> set[str]:
        representatives: set[str] = set()
        for guide in self._desire_action_guides(low_desires):
            for cap_id in guide.get("preferred_capabilities", []):
                if cap_id in valid_cap_ids:
                    representatives.add(cap_id)
        for hint in intrinsic_hints:
            for cap_id in hint.get("required_capabilities", []):
                if cap_id in valid_cap_ids:
                    representatives.add(cap_id)
        return representatives

    def _merge_tool_sets(self, catalog: Any, tools: list[dict[str, Any]], cap_ids: set[str]) -> list[dict[str, Any]]:
        if not cap_ids:
            return tools
        merged = list(tools)
        seen = {tool.get("function", {}).get("name") for tool in merged}
        for tool in catalog.list_for_tools(cap_ids):
            name = tool.get("function", {}).get("name")
            if name and name not in seen:
                merged.append(tool)
                seen.add(name)
        return merged

    def _call_task_generation_llm(
        self,
        *,
        prompt: str,
        tools: list[dict[str, Any]],
        memory_meta: dict[str, Any],
        retry: bool = False,
    ) -> Any:
        system_prompt = (
            "You are AEGIS autonomous agent. Desire pressure is above threshold, so you must choose "
            "at least one safe/read-only tool when any useful action is available. "
            "Use the provided function calling mechanism. Do not answer with plain text instead of acting. "
            "Do not use side-effectful actions unless the existing approval system requires approval."
        )
        if retry:
            system_prompt += (
                " Your previous response did not call a tool. This is a retry: select one concrete "
                "tool now, preferring the lowest-risk read-only action that can reduce the pressured desire."
            )
        return self._llm.generate_with_tools(
            prompt=prompt,
            tools=tools,
            system_prompt=system_prompt,
            max_tokens=600,
            context_meta=memory_meta,
        )

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

        valid_cap_ids = self._available_safe_capability_ids()

        if not valid_cap_ids:
            logger.error("No valid capabilities available — cannot generate tasks")
            return []

        catalog = None
        if self._broker and hasattr(self._broker, '_catalog') and self._broker._catalog:
            catalog = self._broker._catalog

        if not catalog:
            logger.error("No capability catalog available — cannot generate tasks")
            return []

        desire_guides = self._desire_action_guides(low_desires[:self._max_tasks])
        decision_axes = self._build_decision_axes(low_desires[:self._max_tasks])
        self._last_decision_axes = decision_axes
        intrinsic_hints = self._intrinsic_task_hints(valid_cap_ids)
        representative_ids = self._representative_capability_ids(
            low_desires[:self._max_tasks],
            valid_cap_ids,
            intrinsic_hints,
        )

        query_parts = []
        for guide in desire_guides:
            query_parts.append(f"{guide['desire']}: {guide['goal']}")
            query_parts.extend(guide.get("preferred_capabilities", []))
        for hint in intrinsic_hints:
            query_parts.append(f"{hint['title']}: {hint['description']}")
            query_parts.extend(hint.get("required_capabilities", []))
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
            candidate_ids = list(getattr(selection, "all_candidate_ids", []))
        else:
            tools = catalog.list_for_tools(valid_cap_ids)
            candidate_ids = list(valid_cap_ids)
        tools = self._merge_tool_sets(catalog, tools, representative_ids)
        candidate_ids = list(dict.fromkeys([*representative_ids, *candidate_ids]))[:10]
        self._last_candidate_capability_ids = candidate_ids
        if not tools:
            logger.error("No tools generated from catalog")
            return []
        valid_tool_names = {tool["function"]["name"] for tool in tools}

        low_list = ", ".join(desire_context)
        prompt = f"""Low desires: {low_list}

Recent: {action_history}

Select up to {self._max_tasks} capabilities to address the low desires.
Do NOT repeat recent actions by purpose.
Pressure is above threshold, so choose at least one safe/read-only action if any listed tool can help.

Desire action guides:
{json.dumps(desire_guides, ensure_ascii=False)}

Intrinsic task candidates:
{json.dumps(intrinsic_hints, ensure_ascii=False)}

Candidate capability ids:
{json.dumps(candidate_ids, ensure_ascii=False)}

Operational decision axes (prioritization only; not additional desires):
{json.dumps(decision_axes, ensure_ascii=False)}"""

        prompt, memory_meta = self._build_shared_llm_prompt(
            query=retrieval_query,
            base_prompt=prompt,
            profile="decision",
            has_social_actions=self._has_social_actions(valid_cap_ids),
        )

        self._last_llm_call_ms = int(time.time() * 1000)
        self._last_decision_ms = self._last_llm_call_ms
        self._last_decision = "llm_requested"
        result = self._call_task_generation_llm(
            prompt=prompt,
            tools=tools,
            memory_meta=memory_meta,
        )

        if not result.success:
            logger.error("LLM task generation failed: %s", getattr(result, "error", "unknown"))
            self._last_decision = "llm_error"
            self._last_skip_reason = f"llm_error: {getattr(result, 'error', 'unknown')}"
            return []

        if not result.tool_calls:
            reason = result.content[:200] if result.content else "LLM returned no tool calls"
            self._log_audit_event(
                action="autonomous_llm_retry",
                capability_id="none",
                decision="RETRY",
                reason=reason,
                detail={
                    "source": "task_generation",
                    "candidate_capability_ids": candidate_ids[:50],
                    "desire_guides": desire_guides,
                    "decision_axes": decision_axes,
                    "intrinsic_hints": intrinsic_hints,
                },
            )
            result = self._call_task_generation_llm(
                prompt=prompt,
                tools=tools,
                memory_meta=memory_meta,
                retry=True,
            )

        if not result.success:
            logger.error("LLM task generation retry failed: %s", getattr(result, "error", "unknown"))
            self._last_decision = "llm_error"
            self._last_skip_reason = f"llm_error: {getattr(result, 'error', 'unknown')}"
            return []

        if not result.tool_calls:
            reason = "LLM chose not to act"
            if result.content:
                reason = result.content[:200]
            logger.info("LLM no_action: %s", reason)
            self._last_decision = "no_action"
            self._last_skip_reason = f"no_action: {reason}"
            self._last_no_action_reason = reason
            self._selected_tool_count = 0
            self._consecutive_no_action += 1
            self._log_audit_event(
                action="autonomous_no_action",
                capability_id="none",
                decision="FAIL",
                reason=reason,
                detail={
                    "source": "task_generation",
                    "llm_reason": reason,
                    "candidate_capability_ids": candidate_ids[:50],
                },
            )
            self._record_failure_lesson(
                title="Autonomous LLM returned no action",
                content=(
                    "Desire pressure was above threshold, but the LLM returned no executable tool "
                    f"after retry. Reason: {reason}"
                ),
                related_desire=low_desires[0]["name"] if low_desires else "",
                failure_type="llm_no_action",
            )
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
            self._last_decision = "no_valid_tasks"
            self._last_skip_reason = "no_valid_tasks"
            self._last_no_action_reason = "LLM returned tool calls that could not be normalized into executable tasks"
            self._selected_tool_count = 0
            self._consecutive_no_action += 1
        else:
            self._last_decision = "action_selected"
            self._last_skip_reason = ""
            self._last_no_action_reason = ""
            self._selected_tool_count = len(valid_tasks)
            self._consecutive_no_action = 0
            self._log_audit_event(
                action="autonomous_action_selected",
                capability_id=",".join(task["capability_id"] for task in valid_tasks),
                decision="ALLOW",
                reason="LLM selected autonomous actions for pressured desires",
                detail={
                    "selected_capability_ids": [task["capability_id"] for task in valid_tasks],
                    "candidate_capability_ids": candidate_ids[:50],
                    "desire_guides": desire_guides,
                    "intrinsic_hints": intrinsic_hints,
                },
            )
        return valid_tasks

    def _available_safe_capability_ids(self) -> set[str]:
        """Return safe capabilities whose owning server is currently usable."""
        if not self._broker:
            self._available_capability_count = 0
            return set()

        try:
            capabilities = self._broker.list_safe_capabilities() or []
        except Exception as exc:
            logger.warning("Failed to list safe capabilities: %s", exc)
            self._available_capability_count = 0
            return set()

        snapshot: dict[str, dict[str, Any]] | None = None
        if self._status_manager is not None:
            try:
                snapshot = self._status_manager.get_snapshot()
            except Exception as exc:
                logger.warning("Failed to read server status snapshot: %s", exc)

        catalog = getattr(self._broker, "_catalog", None)
        available: set[str] = set()
        for capability in capabilities:
            manifest = catalog.resolve(capability.id) if catalog is not None else None
            server_id = getattr(manifest, "server_id", "") or capability.id.split(".", 1)[0]
            if server_id == "ai-server" or snapshot is None:
                available.add(capability.id)
                continue
            status = str(snapshot.get(server_id, {}).get("status", "unknown")).lower()
            if status in {"online", "degraded"}:
                available.add(capability.id)

        self._available_capability_count = len(available)
        return available

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

            if skill_used and trace:
                self._action_trace.add_step(
                    trace,
                    description=f"Using skill: {skill_used.name}",
                    tool_call="skill_reuse",
                )
            elif workflow_used and trace:
                self._action_trace.add_step(
                    trace,
                    description=f"Using workflow: {workflow_used.name}",
                    tool_call="workflow_reuse",
                )

            # Execute
            start_time = int(time.time() * 1000)
            success = False
            result_summary = ""
            failure_reason = ""
            full_output = {}

            if capability_id and self._broker:
                try:
                    from tool_broker import ExecutionSource, ToolExecutionRequest
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
                        if self._llm:
                            image_b64 = output.get("image_base64") or output.get("image_data") or ""
                            if image_b64:
                                result_summary = self._analyze_screenshot(image_b64, desire_name)
                        success = True
                    else:
                        error_details = result.output or {}
                        error_payload = error_details.get("error")
                        stderr = (
                            error_payload.get("details", {}).get("stderr", "")
                            if isinstance(error_payload, dict)
                            else ""
                        )
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

            result_record = {
                "desire": desire_name, "action": action,
                "capability_id": capability_id,
                "result": result_summary[:200], "success": success,
                "full_output": full_output,
                "skill_used": skill_used.skill_id if skill_used else None,
                "workflow_used": workflow_used.workflow_id if workflow_used else None,
            }
            results.append(result_record)

            if self._should_present_autonomous_result(result_record):
                self._present_autonomous_result(task, result_record)

            result_text = str(result_record.get("result", "")).lower().strip()
            if result_text in _TRIVIAL_RESULTS or (len(result_text) < 20 and result_record.get("success", False)):
                continue

            # Execute post_action if defined
            post_action = task.get("post_action")
            if post_action and success and self._broker:
                post_cap_id = post_action.get("capability_id", "")
                post_args = post_action.get("arguments", {})
                if post_cap_id:
                    try:
                        from tool_broker import ExecutionSource, ToolExecutionRequest
                        post_request = ToolExecutionRequest(
                            capability_id=post_cap_id, arguments=post_args,
                            source=ExecutionSource.AUTONOMOUS,
                            reason=f"Post-action for {desire_name}",
                        )
                        post_result = self._broker.execute(post_request)
                        logger.info(
                            "Post-action %s: %s",
                            post_cap_id,
                            "OK" if post_result.success else post_result.error,
                        )
                    except Exception as e:
                        logger.warning("Post-action failed: %s", e)

        return results

    def _should_present_autonomous_result(self, result_record: dict[str, Any]) -> bool:
        if not result_record.get("success", False):
            return False
        result_text = str(result_record.get("result", "")).lower().strip()
        if result_text in _TRIVIAL_RESULTS or (len(result_text) < 20 and result_record.get("success", False)):
            return False
        return True

    def _present_autonomous_result(self, task: dict[str, Any], result_record: dict[str, Any]) -> None:
        try:
            from aegis_ai.presentation.models import PresentationRequest
            from aegis_ai.runtime import get_runtime
        except Exception:
            return

        rt = get_runtime()
        presentation_manager = getattr(rt, "presentation_manager", None) if rt is not None else None
        if not hasattr(rt, "presentation_manager") or presentation_manager is None:
            return

        output = result_record.get("full_output", {})
        modality = "text_card"
        if isinstance(output, dict):
            if output.get("image_base64") or output.get("image_data"):
                modality = "diagram_panel"
            elif any(key in output for key in ("chart", "chart_type", "series", "points", "labels")):
                modality = "chart_panel"
            elif any(key in output for key in ("diagram", "graph", "tree", "topology")):
                modality = "diagram_panel"

        summary = str(result_record.get("result", "") or "").strip()
        if not summary:
            return

        request = PresentationRequest(
            source="autonomous_loop",
            intent=f"autonomous_{str(task.get('desire', 'task') or 'task')}",
            importance="high",
            modality=modality,
            title=str(task.get("action") or task.get("capability_id") or "Autonomous result"),
            summary=summary,
            content={
                "desire": task.get("desire", ""),
                "action": task.get("action", ""),
                "capability_id": task.get("capability_id", ""),
                "result": summary,
                "output": output,
            },
        )
        try:
            presentation_manager.present(request)
        except Exception:
            logger.debug("Failed to present autonomous result", exc_info=True)

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
        # Skip follow-up when all tasks succeeded with trivial results
        if len(previous_tasks) == len(previous_results):
            all_trivial = all(
                r.get("success", False) and
                (str(r.get("result", "")).lower().strip() in _TRIVIAL_RESULTS or len(str(r.get("result", ""))) < 20)
                for r in previous_results
            )
            if all_trivial:
                return []

        context_parts = []
        for i, (task, result) in enumerate(zip(previous_tasks, previous_results)):
            structured_output = json.dumps(
                result.get("full_output", {}), ensure_ascii=False, default=str
            )[:1500]
            context_parts.append(
                f"Task {i+1}: {task.get('action', '')[:100]}\n"
                f"Result: {result.get('result', '')[:200]}\n"
                f"Structured result: {structured_output}\n"
                f"Success: {result.get('success', False)}\n"
                f"Desire: {task.get('desire', '')}"
            )

        catalog = None
        if self._broker and hasattr(self._broker, '_catalog') and self._broker._catalog:
            catalog = self._broker._catalog

        if not catalog:
            return []

        valid_cap_ids = self._available_safe_capability_ids()

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
- Use the provided tools to execute any follow-up actions
- Decide from the structured result whether another action is genuinely needed
- For social tasks, prefer replying only when the result shows a message directed at AEGIS
- For research tasks, save only genuinely useful new information
- For system tasks, investigate only meaningful anomalies
- If no follow-up is needed, do not call any tools
- Do not repeat a successful read-only capability unless the result explicitly shows more unread or paginated data
- Do not repeat invalid or previously failed tool choices unless memory indicates a new reason they should work now"""

        try:
            result = self._llm.generate_with_tools(
                prompt=prompt,
                tools=tools,
                system_prompt=(
                    "You are AEGIS deciding follow-up actions. "
                    "You MUST use the provided tools to execute actions. "
                    "Call tools directly using the function calling mechanism. "
                    "Do NOT respond with text when a tool call is appropriate. "
                    "If no follow-up is needed, simply respond with a brief explanation without calling any tools."
                ),
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

        from aegis_ai.desire.fulfillment import TaskEffect, evaluate_task_result

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

            capability_metadata = self._resolve_capability_metadata(capability_id)

            task_result = evaluate_task_result(
                capability_id=capability_id,
                tool_success=success,
                output=output,
                desire_name=desire_name,
                llm_provider=self._llm,
                capability_metadata=capability_metadata,
            )

            logger.info(
                "Task evaluation: cap=%s effect=%s deltas=%s",
                capability_id, task_result.task_effect.value, task_result.desire_delta_hint,
            )
            self._log_audit_event(
                action="autonomous_fulfillment_evaluated",
                capability_id=capability_id,
                decision=task_result.task_effect.value.upper(),
                reason=task_result.summary,
                detail={
                    "desire": desire_name,
                    "tool_success": success,
                    "fulfillment_score": task_result.fulfillment_score,
                    "pressure_reduction": task_result.pressure_reduction,
                    "confidence": task_result.confidence,
                    "desire_delta_hint": task_result.desire_delta_hint,
                    "details": task_result.details,
                    "capability_metadata": capability_metadata,
                },
            )

            if success and task_result.pressure_reduction > 0.0:
                self._desire.reduce_pressure(desire_name, task_result.pressure_reduction)

            if task_result.task_effect == TaskEffect.NO_EFFECT:
                continue

            for d_name, delta in task_result.desire_delta_hint.items():
                if delta != 0.0:
                    current = self._desire.get_desire(d_name)
                    if current:
                        old_val = current.value
                        new_val = max(0.0, min(10.0, old_val + delta))
                        self._desire.update_value(
                            d_name, new_val,
                            reason=f"{task_result.summary} ({capability_id})",
                        )
                        logger.info("Desire %s: %.1f -> %.1f (delta=%.1f)", d_name, old_val, new_val, delta)

        self._desire.save()

    def _resolve_capability_metadata(self, capability_id: str) -> dict[str, Any]:
        if capability_id in self._capability_metadata_cache:
            return self._capability_metadata_cache[capability_id]

        catalog = getattr(self._broker, "_catalog", None) if self._broker is not None else None
        if catalog is None or not capability_id:
            return {}
        try:
            manifest = catalog.resolve(capability_id)
            if manifest is None:
                return {}
            metadata = {
                "operation_category": getattr(manifest, "operation_category", ""),
                "risk_level": getattr(manifest, "risk_level", ""),
                "side_effects": getattr(manifest, "side_effects", []),
                "title": getattr(manifest, "title", ""),
                "description": getattr(manifest, "description", ""),
                "server_id": getattr(manifest, "server_id", ""),
            }
            self._capability_metadata_cache[capability_id] = metadata
            return metadata
        except Exception:
            logger.debug("Failed to resolve manifest metadata", exc_info=True)
            return {}

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
            return "Autonomous execution history: no actions executed yet. First run."

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
        metadata = task.get("capability_metadata") or self._resolve_capability_metadata(cap_id)
        title = str(metadata.get("title") or metadata.get("description") or "").strip()
        args = task.get("arguments", {})
        if title:
            return f"Executed capability: {title[:120]}"
        if isinstance(args, dict) and args.get("command"):
            return f"Executed command-like capability: {str(args['command'])[:80]}"
        return action or cap_id or "Unknown action"

    def _summarize_state_change(self, task: dict[str, Any], result: dict[str, Any]) -> str:
        """Summarize what state change occurred."""
        if not result.get("success"):
            return "No state change because the action failed."
        cap_id = task.get("capability_id", "")
        metadata = task.get("capability_metadata") or self._resolve_capability_metadata(cap_id)
        output = result.get("full_output", {})
        if isinstance(output, dict) and (output.get("image_base64") or output.get("image_data")):
            return "Captured a visual observation artifact."
        side_effects = metadata.get("side_effects") or []
        if not isinstance(side_effects, list):
            side_effects = [str(side_effects)]
        operation_category = str(metadata.get("operation_category") or "")
        if side_effects:
            return f"Applied side effects: {', '.join(str(item) for item in side_effects[:4])}"
        if operation_category:
            return f"Observed or processed state for category: {operation_category}"
        return "Executed the operation and recorded the result."

    def _determine_repeat_condition(self, task: dict[str, Any], result: dict[str, Any]) -> str:
        """Determine under what condition this action should be repeated."""
        if not result.get("success"):
            return "Retry only if the underlying problem is still relevant."
        cap_id = task.get("capability_id", "")
        metadata = task.get("capability_metadata") or self._resolve_capability_metadata(cap_id)
        output = result.get("full_output", {})
        if isinstance(output, dict) and (output.get("image_base64") or output.get("image_data")):
            return "Repeat only when the observed visual state may have changed."
        side_effects = metadata.get("side_effects") or []
        if side_effects:
            return "Repeat only when the same side effect is still intentionally desired."
        operation_category = str(metadata.get("operation_category") or "")
        if operation_category:
            return f"Repeat when new information is expected for category: {operation_category}"
        return "Repeat only when new information or state change is expected."

    def _record_experiences(self, tasks: list[dict[str, Any]], results: list[dict[str, Any]]) -> None:
        for i, task in enumerate(tasks):
            result = results[i] if i < len(results) else {}
            success = result.get("success", False)

            if not success:
                continue

            action = task.get("action", "Unknown task")
            capability_id = task.get("capability_id", result.get("capability_id", ""))
            observation = result.get("result", "")
            result_text = str(result.get("result", "")).lower().strip()
            if result_text in _TRIVIAL_RESULTS or (len(result_text) < 20 and result.get("success", False)):
                continue
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
        """Decide when to run next using pressure-based logic (no LLM)."""
        if not self._desire:
            logger.info("No desire — using fallback interval %ds", self._fallback_interval)
            return self._fallback_interval

        desires = self._desire.get_all_desires()
        high_pressure_count = 0
        total_pressure = 0.0
        for desire in desires.values():
            if desire.hidden:
                continue
            if desire.pressure >= self._pressure_threshold:
                high_pressure_count += 1
            total_pressure += desire.pressure

        success_count = sum(1 for r in results if r.get("success"))
        total_count = len(results)
        fail_count = total_count - success_count

        if high_pressure_count == 0:
            interval = self._fallback_interval
            reason = "all pressures below threshold"
        elif high_pressure_count >= 3:
            interval = 60
            reason = f"{high_pressure_count} desires critically pressured"
        elif fail_count > success_count and total_count > 0:
            interval = 900
            reason = f"{fail_count}/{total_count} tasks failed, backing off"
        elif total_count == 0:
            interval = 60
            reason = "no tasks executed while pressure remains high"
        else:
            interval = max(60, int(self._fallback_interval * (1.0 - total_pressure / 30.0)))
            reason = f"{high_pressure_count} pressured desires, managed"

        interval = max(60, min(3600, interval))
        logger.info("Next autonomous run in %d seconds: %s", interval, reason)
        return interval

    def _schedule_next(self, interval_seconds: int) -> None:
        """Schedule the next execution."""
        with self._lock:
            self._next_run_ms = int(time.time() * 1000) + (interval_seconds * 1000)
        logger.info("Next autonomous run scheduled in %d seconds", interval_seconds)

    def _store_image_artifact(self, image_base64: str, *, mime: str = "", hint: str = "image") -> dict[str, Any]:
        raw = base64.b64decode(image_base64, validate=False)
        timestamp = int(time.time() * 1000)
        safe_hint = re.sub(r"[^A-Za-z0-9_.-]+", "_", hint)[:40] or "image"
        ext = ".png"
        if mime == "image/jpeg":
            ext = ".jpg"
        elif mime == "image/webp":
            ext = ".webp"
        elif mime == "image/gif":
            ext = ".gif"
        elif raw.startswith(b"BM"):
            ext = ".bmp"

        try:
            from PIL import Image  # type: ignore

            with Image.open(io.BytesIO(raw)) as img:
                if img.mode in {"RGBA", "LA"} or "transparency" in img.info:
                    out_path = self._artifact_dir / f"{timestamp}_{safe_hint}.png"
                    img.save(out_path, format="PNG", optimize=True)
                    out_mime = "image/png"
                else:
                    out_path = self._artifact_dir / f"{timestamp}_{safe_hint}.jpg"
                    img.convert("RGB").save(out_path, format="JPEG", quality=72, optimize=True)
                    out_mime = "image/jpeg"
                return {
                    "artifact_path": str(out_path),
                    "mime": out_mime,
                    "size_bytes": out_path.stat().st_size,
                    "original_size_bytes": len(raw),
                }
        except Exception:
            pass

        out_path = self._artifact_dir / f"{timestamp}_{safe_hint}{ext}"
        out_path.write_bytes(raw)
        return {
            "artifact_path": str(out_path),
            "mime": mime or "application/octet-stream",
            "size_bytes": out_path.stat().st_size,
            "original_size_bytes": len(raw),
        }

    def _sanitize_for_execution_log(self, value: Any, *, key: str = "", depth: int = 0) -> Any:
        if depth > 8:
            return "<max_depth>"
        if _SENSITIVE_KEY_RE.search(key):
            return "***MASKED***"
        if key in {"image_base64", "image_data"} and isinstance(value, str) and value:
            try:
                return self._store_image_artifact(value, hint=key)
            except Exception as exc:
                return {"artifact_error": str(exc), "original_length": len(value)}
        if isinstance(value, dict):
            mime = str(value.get("image_mime") or value.get("mime") or "")
            if isinstance(value.get("image_base64"), str):
                try:
                    compact = {
                        str(k): self._sanitize_for_execution_log(v, key=str(k), depth=depth + 1)
                        for k, v in value.items()
                        if k != "image_base64"
                    }
                    compact["image_artifact"] = self._store_image_artifact(
                        str(value["image_base64"]),
                        mime=mime,
                        hint=key or "image",
                    )
                    return compact
                except Exception:
                    pass
            items = list(value.items())[:_LOG_DICT_LIMIT]
            compact = {
                str(k): self._sanitize_for_execution_log(v, key=str(k), depth=depth + 1)
                for k, v in items
            }
            if len(value) > _LOG_DICT_LIMIT:
                compact["_truncated_keys"] = len(value) - _LOG_DICT_LIMIT
            return compact
        if isinstance(value, list):
            compact_list = [self._sanitize_for_execution_log(v, depth=depth + 1) for v in value[:_LOG_LIST_LIMIT]]
            if len(value) > _LOG_LIST_LIMIT:
                compact_list.append({"_truncated_items": len(value) - _LOG_LIST_LIMIT})
            return compact_list
        if isinstance(value, str):
            masked = _SECRET_TEXT_RE.sub(lambda m: (m.group(1) or m.group(3) or "") + "***MASKED***", value)
            if len(masked) > _LOG_TEXT_LIMIT:
                return masked[:_LOG_TEXT_LIMIT] + f"... <truncated {len(masked) - _LOG_TEXT_LIMIT} chars>"
            return masked
        return value

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
            "tasks": self._sanitize_for_execution_log(semantic_tasks, key="tasks"),
            "results": self._sanitize_for_execution_log(results, key="results"),
            "next_run_ms": self._next_run_ms,
            "candidate_capability_ids": self._last_candidate_capability_ids[-50:],
            "decision_axes": dict(self._last_decision_axes),
            "selected_tool_count": self._selected_tool_count,
            "last_decision": self._last_decision,
            "last_no_action_reason": self._last_no_action_reason,
        }
        with self._lock:
            self._execution_log.append(entry)

        log_path = self._data_dir / "execution_log.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_status(self) -> dict[str, Any]:
        """Get autonomous loop status."""
        now = int(time.time() * 1000)
        next_llm_allowed_ms = self._last_llm_call_ms + self._min_llm_interval_ms if self._last_llm_call_ms else 0
        with self._lock:
            return {
                "running": self._running,
                "last_run_ms": self._last_run_ms,
                "next_run_ms": self._next_run_ms,
                "seconds_until_next": max(0, (self._next_run_ms - now) / 1000),
                "execution_count": len(self._execution_log),
                "pressure_threshold": self._pressure_threshold,
                "min_llm_interval_ms": self._min_llm_interval_ms,
                "llm_interval_ms": self._min_llm_interval_ms,
                "last_llm_call_ms": self._last_llm_call_ms,
                "next_llm_allowed_ms": next_llm_allowed_ms,
                "seconds_until_next_llm": max(0, (next_llm_allowed_ms - now) / 1000) if next_llm_allowed_ms else 0,
                "last_decision": self._last_decision,
                "last_decision_ms": self._last_decision_ms,
                "last_action_ms": self._last_action_ms,
                "available_capability_count": self._available_capability_count,
                "selected_tool_count": self._selected_tool_count,
                "last_no_action_reason": self._last_no_action_reason,
                "candidate_capability_ids": self._last_candidate_capability_ids[-50:],
                "decision_axes": dict(self._last_decision_axes),
                "consecutive_no_action": self._consecutive_no_action,
                "last_skip_reason": self._last_skip_reason,
            }

    def trigger_now(self) -> dict[str, Any]:
        """Manually trigger an autonomous cycle."""
        logger.info("Manual trigger requested")
        self._execute_cycle()
        return self.get_status()

    def trigger(self, reason: str = "", context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Trigger an autonomous cycle from HookEngine or another manager."""
        self._pending_actionable_observations.append({
            "source": "self_call",
            "reason": reason,
            "context": context or {},
            "created_at_ms": int(time.time() * 1000),
        })
        logger.info("Self-call trigger requested: %s", reason)
        self._execute_cycle()
        return self.get_status()
