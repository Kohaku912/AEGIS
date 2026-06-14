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
        data_dir: str = "data/autonomous",
        desire_threshold: float = 4.0,
        max_tasks_per_cycle: int = 3,
        fallback_interval_seconds: int = 3600,
    ) -> None:
        self._llm = llm_provider
        self._desire = desire_system
        self._memory = memory_system
        self._reflection = reflection_engine
        self._broker = tool_broker
        self._world = world_state_store
        self._experiential = experiential_memory
        self._affect = affect_system
        self._action_trace = action_trace
        self._skill = skill_memory
        self._workflow = workflow_memory
        self._lesson = lesson_memory
        self._observation = observation_system
        self._curiosity = curiosity_system
        self._policy = policy_engine
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._desire_threshold = desire_threshold
        self._max_tasks = max_tasks_per_cycle
        self._fallback_interval = fallback_interval_seconds

        self._running = False
        self._thread: threading.Thread | None = None
        self._next_run_ms: int = 0
        self._last_run_ms: int = 0
        self._execution_log: list[dict[str, Any]] = []
        self._last_observation_ms: int = 0
        self._observation_interval_ms: int = 60_000  # 1 minute
        self._desire_check_interval_ms: int = 60_000  # 1 minute — desire check every tick
        self._last_desire_check_ms: int = 0
        self._min_execution_interval_ms: int = 60_000  # Minimum 1 minute between executions

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

    def start(self) -> None:
        """Start the autonomous loop in background."""
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
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Autonomous loop stopped")

    def _run_loop(self) -> None:
        """Main loop — desire monitoring, observation, and execution."""
        while self._running:
            try:
                desire_triggered = self._monitor_desires()
                now = int(time.time() * 1000)

                # Spontaneous observation (every 1 minute)
                if self._observation and now - self._last_observation_ms >= self._observation_interval_ms:
                    try:
                        observations = self._observation.observe_all()
                        self._last_observation_ms = now
                        actionable = [o for o in observations if o.actionable and o.importance >= 0.7]
                        if actionable:
                            logger.info("Observation found %d actionable items", len(actionable))
                    except Exception as e:
                        logger.warning("Observation failed: %s", e)

                # Curiosity exploration (when curiosity desire is high)
                if self._curiosity and self._curiosity.should_explore:
                    try:
                        candidates = self._curiosity.generate_exploration_candidates()
                        if candidates:
                            best = self._curiosity.select_best_candidate(candidates)
                            if best and best.priority_score > 0.5:
                                logger.info("Curiosity exploration: %s", best.topic[:50])
                                result = self._curiosity.explore(best)
                                logger.info("Exploration result: %s", result.findings[:100])
                    except Exception as e:
                        logger.warning("Curiosity exploration failed: %s", e)

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
        """Lightweight desire monitoring — runs every tick.

        Returns True if desires are critically low and execution should be
        triggered immediately, regardless of the scheduled next-run time.
        """
        if not self._desire:
            return False
        self._desire.apply_decay()
        low = self._get_low_desires()
        if low:
            top = low[0]
            logger.info(
                "Desire check: %d low. Top: %s=%.1f (gap=%.1f)",
                len(low), top["name"], top["value"], top["gap"],
            )
            # Trigger execution when top desire gap is significant (>= 2.0)
            if top["gap"] >= 2.0:
                logger.info(
                    "Desire-driven trigger: %s gap=%.1f >= 2.0 — executing now",
                    top["name"], top["gap"],
                )
                return True
        return False

    def _execute_cycle(self) -> None:
        """Execute autonomous tasks — only runs when scheduled or triggered."""
        logger.info("Starting autonomous execution cycle")
        self._last_run_ms = int(time.time() * 1000)

        if not self._desire:
            logger.warning("No desire system, using fallback interval")
            self._schedule_next(self._fallback_interval)
            return

        low_desires = self._get_low_desires()
        if not low_desires:
            logger.info("All desires above threshold, using fallback interval")
            self._schedule_next(self._fallback_interval)
            return

        desire_before = {}
        if self._desire:
            for name, desire in self._desire.get_all_desires().items():
                desire_before[name] = desire.value

        tasks = self._generate_tasks(low_desires)
        results = self._execute_tasks(tasks)

        if self._reflection is not None:
            for i, task in enumerate(tasks):
                task_result = results[i] if i < len(results) else {}
                source_desire = task.get("desire", "")
                try:
                    reflection = self._reflection.reflect(
                        task_id=f"auto_{int(time.time() * 1000)}_{i}",
                        task_description=task.get("action", ""),
                        tool_results=[{
                            "status": "success" if task_result.get("success") else "failed",
                            "capability_id": "autonomous_task",
                            "error": task_result.get("result", "") if not task_result.get("success") else "",
                        }],
                        source_desire=source_desire,
                        frustration=task.get("expected_impact", 0.0),
                        desire_before=desire_before,
                    )
                    logger.info("Reflection: %s — %s", reflection.outcome, reflection.summary[:100])
                except Exception as e:
                    logger.warning("Reflection failed: %s", e)

        self._update_desires(results)
        self._record_experiences(tasks, results)
        next_interval = self._decide_next_interval(results)
        self._schedule_next(next_interval)
        self._log_execution(tasks, results)
        self._save()

    def _get_low_desires(self) -> list[dict[str, Any]]:
        """Get desires below threshold or with high frustration."""
        low = []
        for name, desire in self._desire.get_all_desires().items():
            frustration = max(0, desire.expected_value - desire.value)
            if desire.value < self._desire_threshold or frustration >= 1.5:
                low.append({
                    "name": name,
                    "value": desire.value,
                    "expected": desire.expected_value,
                    "frustration": frustration,
                    "gap": max(self._desire_threshold - desire.value, frustration),
                })
        return sorted(low, key=lambda d: d["gap"], reverse=True)

    def _generate_tasks(self, low_desires: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate tasks to fulfill low desires using LLM."""
        if not self._llm:
            return self._generate_default_tasks(low_desires)

        # Build desire context
        desire_context = []
        for d in low_desires[:3]:  # Top 3 low desires
            desire_context.append(f"- {d['name']}: {d['value']:.1f}/10 (gap: {d['gap']:.1f})")

        memory_context = ""
        if self._memory:
            try:
                memories = self._memory.search("recent autonomous tasks", limit=3)
                if memories:
                    memory_context = "\nRecent memories:\n" + "\n".join(
                        f"- {m}" for m in memories
                    )
            except Exception:
                pass

        lesson_context = ""
        if self._lesson:
            try:
                top_desire = low_desires[0]["name"] if low_desires else ""
                lessons = self._lesson.get_relevant(f"autonomous {top_desire}", count=2)
                if lessons:
                    lesson_context = "\nRelevant lessons:\n" + "\n".join(
                        f"- {getattr(lesson, 'content', str(lesson))}" for lesson in lessons
                    )
            except Exception:
                pass

        world_context = ""
        if self._world:
            try:
                state = self._world.get_snapshot()
                if state:
                    world_context = f"\nWorld state: {state}"
            except Exception:
                pass

        pc_ok = _check_port("localhost", 50052)
        browser_ok = _check_port("localhost", 50053)
        agora_ok = bool(os.environ.get("AGORA_TOKEN", ""))
        server_status = f"\nServer status: PC={'online' if pc_ok else 'offline'}, Browser={'online' if browser_ok else 'offline'}, AGORA={'configured' if agora_ok else 'not configured'}"
        if not pc_ok:
            server_status += "\nIMPORTANT: PC server is OFFLINE. Do NOT use pc.* capabilities."
        if agora_ok:
            server_status += "\nAGORA is available. Use ai.agora.* capabilities for social tasks."

        prompt = f"""You are AEGIS, an autonomous AI assistant. Your desires are low:

{chr(10).join(desire_context)}
{memory_context}{lesson_context}{world_context}{server_status}

Generate up to {self._max_tasks} tasks to fulfill these desires.
Each task should be:
- Something AEGIS can do autonomously
- Related to improving the low desire
- Safe and constructive

Respond with JSON:
{{
  "tasks": [
    {{
      "desire": "desire_name",
      "action": "description of what to do",
      "expected_impact": 0.5
    }}
  ]
}}

Examples:
- For low user_helpfulness: "Review pending user requests and prepare helpful responses"
- For low learning_progress: "Review recent errors and learn from them"
- For low curiosity: "Research a new technology topic"
- For low system_safety: "Review and improve system security"
- For low reliability: "Run tests and fix any failing tests"
- For low social_connection: "Check AGORA for new messages"
- For low creativity: "Generate creative ideas or solutions"
- For low purpose: "Reflect on goals and plan next steps"
- For low autonomy: "Make an independent decision about system improvement"
- For low maintenance: "Clean up old logs and optimize system"""

        result = self._llm.generate(
            prompt=prompt,
            system_prompt=(
                "You are AEGIS's autonomous task generator. "
                "Generate tasks to fulfill desires. Output only JSON."
            ),
            max_tokens=500,
        )

        if not result.success:
            return self._generate_default_tasks(low_desires)

        try:
            clean = result.content.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:])
                if clean.endswith("```"):
                    clean = clean[:-3]
                clean = clean.strip()

            data = json.loads(clean)
            tasks = data.get("tasks", [])
            return tasks[:self._max_tasks]
        except Exception as e:
            logger.warning("Failed to parse LLM tasks: %s", e)
            return self._generate_default_tasks(low_desires)

    def _generate_default_tasks(self, low_desires: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate default tasks with actual capability_ids for real execution."""
        pc_ok = _check_port("localhost", 50052)
        agora_ok = bool(os.environ.get("AGORA_TOKEN", ""))

        desire_capability_map = {
            "user_helpfulness": {
                "action": "Capture screenshot to understand what user is doing and find ways to help",
                "capability_id": "pc.screenshot.get_screenshot",
                "arguments": {},
                "server": "pc",
            },
            "learning_progress": {
                "action": "Get system info to learn about the current environment",
                "capability_id": "pc.system.get_os_info",
                "arguments": {},
                "server": "pc",
            },
            "curiosity": {
                "action": "List available windows to discover what applications are in use",
                "capability_id": "pc.window.list_windows",
                "arguments": {},
                "server": "pc",
            },
            "system_safety": {
                "action": "Capture screenshot to verify system state and check for anomalies",
                "capability_id": "pc.screenshot.get_screenshot",
                "arguments": {},
                "server": "pc",
            },
            "reliability": {
                "action": "Get system info to verify system health and reliability",
                "capability_id": "pc.system.get_os_info",
                "arguments": {},
                "server": "pc",
            },
            "social_connection": {
                "action": "Check AGORA for new messages and social interactions",
                "capability_id": "ai.agora.read_mentions",
                "arguments": {"limit": 10},
                "server": "agora",
            },
            "autonomy": {
                "action": "List available windows to understand current system state",
                "capability_id": "pc.window.list_windows",
                "arguments": {},
                "server": "pc",
            },
            "creativity": {
                "action": "Get active window to see what the user is working on for creative inspiration",
                "capability_id": "pc.window.get_active_window",
                "arguments": {},
                "server": "pc",
            },
            "purpose": {
                "action": "Get clipboard content to understand current user tasks and align with purpose",
                "capability_id": "pc.clipboard.get_clipboard",
                "arguments": {},
                "server": "pc",
            },
            "maintenance": {
                "action": "Get system info to check system health and resource usage",
                "capability_id": "pc.system.get_os_info",
                "arguments": {},
                "server": "pc",
            },
        }

        agora_fallback = {
            "action": "Check AGORA for new messages",
            "capability_id": "ai.agora.read_posts",
            "arguments": {"limit": 10},
            "server": "agora",
        }

        tasks = []
        for d in low_desires[:self._max_tasks]:
            template = desire_capability_map.get(d["name"])
            if template:
                server = template["server"]
                if server == "pc" and not pc_ok:
                    if agora_ok:
                        template = agora_fallback
                    else:
                        continue
                elif server == "agora" and not agora_ok:
                    continue
                tasks.append({
                    "desire": d["name"],
                    "action": template["action"],
                    "capability_id": template["capability_id"],
                    "arguments": template["arguments"],
                    "expected_impact": 0.5,
                })
        return tasks

    def _execute_tasks(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute tasks with skill/workflow reuse and action tracing."""
        results = []

        for task in tasks:
            desire_name = task.get("desire", "unknown")
            action = task.get("action", "Unknown task")
            capability_id = task.get("capability_id", "")
            arguments = task.get("arguments", {})

            logger.info("Executing task: %s (for %s)", action[:50], desire_name)

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
                        result_summary = str(output.get("result", output.get("count", "Done")))
                        if capability_id == "pc.screenshot.get_screenshot" and self._llm:
                            image_b64 = output.get("image_base64", "")
                            if image_b64:
                                result_summary = self._analyze_screenshot(image_b64, desire_name)
                        success = True
                    else:
                        result_summary = f"Failed: {result.error}"[:200]
                        failure_reason = result.error

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

            results.append({
                "desire": desire_name, "action": action,
                "result": result_summary[:200], "success": success,
                "skill_used": skill_used.skill_id if skill_used else None,
                "workflow_used": workflow_used.workflow_id if workflow_used else None,
            })

        return results

    def _analyze_screenshot(self, image_base64: str, desire_context: str) -> str:
        """Analyze a screenshot using multimodal LLM."""
        if not self._llm:
            return "Screenshot captured (no LLM for analysis)"

        if not hasattr(self._llm, 'generate_with_image'):
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
            result = self._llm.generate_with_image(
                prompt=prompt,
                image_base64=image_base64,
                system_prompt="You are AEGIS analyzing your own screenshot. Be concise and observational.",
                max_tokens=400,
                detail="low",
            )
            if result.success:
                return result.content[:200]
            return "Screenshot captured (analysis failed)"
        except Exception as e:
            logger.warning("Screenshot analysis failed: %s", e)
            return "Screenshot captured (analysis error)"

    def _update_desires(self, results: list[dict[str, Any]]) -> None:
        """Update desires based on task results using LLM evaluation with history."""
        if not self._desire:
            return

        history = self._load_recent_history()

        for result in results:
            action = result.get("action", "")
            observation = result.get("result", "")
            success = result.get("success", False)
            logger.info("Updating desires for action: %s (success=%s)", action[:50], success)

            update_result = self._desire.update_after_action(
                action, observation,
                history=history,
            )
            logger.info("Desire update result: %s", update_result)

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

    def _record_experiences(self, tasks: list[dict[str, Any]], results: list[dict[str, Any]]) -> None:
        """Record experiences and appraise emotions from task execution."""
        for i, task in enumerate(tasks):
            result = results[i] if i < len(results) else {}
            action = task.get("action", "Unknown task")
            observation = result.get("result", "")
            desire_name = task.get("desire", "")
            success = result.get("success", False)

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
        """Decide when to run next based on results using LLM."""
        if not self._llm:
            return self._fallback_interval

        # Count successful tasks
        success_count = sum(1 for r in results if r.get("success"))
        total_count = len(results)

        # Get current desire states
        desire_states = []
        if self._desire:
            for name, desire in self._desire.get_all_desires().items():
                desire_states.append(f"- {name}: {desire.value:.1f}/10")

        prompt = f"""Based on the autonomous execution results, decide when AEGIS should run next.

Tasks executed: {total_count}
Successful: {success_count}

Current desire states:
{chr(10).join(desire_states)}

Decide the next execution interval in seconds.
Consider:
- If many desires are low, run sooner (300-900 seconds)
- If desires are balanced, run later (1800-3600 seconds)
- If all desires are high, run much later (3600-7200 seconds)

Respond with JSON:
{{
  "interval_seconds": 1800,
  "reason": "Brief explanation"
}}"""

        result = self._llm.generate(
            prompt=prompt,
            system_prompt="You are AEGIS's scheduling system. Decide when to run next. Output only JSON.",
            max_tokens=200,
        )

        if not result.success:
            return self._fallback_interval

        try:
            clean = result.content.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:])
                if clean.endswith("```"):
                    clean = clean[:-3]
                clean = clean.strip()

            data = json.loads(clean)
            interval = data.get("interval_seconds", self._fallback_interval)
            # Clamp to reasonable range
            interval = max(300, min(7200, interval))
            logger.info("Self-scheduled next run in %d seconds: %s", interval, data.get("reason", ""))
            return interval
        except Exception as e:
            logger.warning("Failed to parse scheduling response: %s", e)
            return self._fallback_interval

    def _schedule_next(self, interval_seconds: int) -> None:
        """Schedule the next execution."""
        self._next_run_ms = int(time.time() * 1000) + (interval_seconds * 1000)
        logger.info("Next autonomous run scheduled in %d seconds", interval_seconds)

    def _log_execution(self, tasks: list[dict[str, Any]], results: list[dict[str, Any]]) -> None:
        """Log execution for history."""
        entry = {
            "timestamp_ms": int(time.time() * 1000),
            "tasks": tasks,
            "results": results,
            "next_run_ms": self._next_run_ms,
        }
        self._execution_log.append(entry)

        # Save to file
        log_path = self._data_dir / "execution_log.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_status(self) -> dict[str, Any]:
        """Get autonomous loop status."""
        now = int(time.time() * 1000)
        return {
            "running": self._running,
            "last_run_ms": self._last_run_ms,
            "next_run_ms": self._next_run_ms,
            "seconds_until_next": max(0, (self._next_run_ms - now) / 1000),
            "execution_count": len(self._execution_log),
        }

    def trigger_now(self) -> dict[str, Any]:
        """Manually trigger an autonomous cycle."""
        logger.info("Manual trigger requested")
        self._execute_cycle()
        return self.get_status()
