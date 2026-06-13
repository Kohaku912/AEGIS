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
import threading
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.autonomous.autonomous_loop")


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

    def stop(self) -> None:
        """Stop the autonomous loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Autonomous loop stopped")

    def _run_loop(self) -> None:
        """Main loop — desire monitoring runs constantly, execution is on-demand."""
        while self._running:
            try:
                self._monitor_desires()
                now = int(time.time() * 1000)
                if now >= self._next_run_ms:
                    self._execute_cycle()
                else:
                    sleep_seconds = (self._next_run_ms - now) / 1000
                    if sleep_seconds > 0:
                        time.sleep(min(sleep_seconds, 60))
            except Exception as e:
                logger.error("Autonomous loop error: %s", e)
                time.sleep(60)

    def _monitor_desires(self) -> None:
        """Lightweight desire monitoring — runs every tick. No task execution."""
        if not self._desire:
            return
        self._desire.apply_decay()
        low = self._get_low_desires()
        if low:
            top = low[0]
            logger.info(
                "Desire check: %d low. Top: %s=%.1f (gap=%.1f)",
                len(low), top["name"], top["value"], top["gap"],
            )

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
        next_interval = self._decide_next_interval(results)
        self._schedule_next(next_interval)
        self._log_execution(tasks, results)
        self._save()

    def _get_low_desires(self) -> list[dict[str, Any]]:
        """Get desires below threshold or with high frustration."""
        low = []
        for name, desire in self._desire.get_all_desires().items():
            frustration = max(0, desire.expected_value - desire.value)
            if desire.value < self._desire_threshold or frustration >= 3.0:
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

        prompt = f"""You are AEGIS, an autonomous AI assistant. Your desires are low:

{chr(10).join(desire_context)}

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
        """Generate default tasks when LLM is unavailable."""
        task_templates = {
            "user_helpfulness": (
                "Review unresolved user requests, messages, and pending tasks. "
                "Identify the most useful next action for the user. "
                "Prepare a helpful response or action plan."
            ),
            "learning_progress": (
                "Learn from recent experiences, including successes, failures, conversations, observations, surprises, and repeated patterns. "
                "Extract useful lessons, update understanding, and identify an idea that could improve future behavior or judgment."
            ),
            "curiosity": (
                "Explore something interesting, meaningful, or potentially useful. "
                "Prefer topics connected to the user's goals, the AI's growth, the surrounding world, or unresolved questions, "
                "but allow room for unexpected discovery."
            ),
            "system_safety": "Review system security settings and audit logs",
            "reliability": "Run tests and fix any failing tests",
            "social_connection": (
                "Check SNS or chat applications for new messages. "
                "Summarize important messages and reply. "
            ),
            "autonomy": (
                "Review current goals, blockers, available capabilities, and recent progress. "
                "Choose one small, safe, high-impact next step for system improvement. "
            ),
            "creativity": (
                "Create freely. "
                "Generate ideas, stories, designs, hypotheses, experiments, tools, aesthetics, characters, systems, or unusual connections. "
                "Value originality, emotional resonance, beauty, surprise, playfulness, and imagination, not only practicality."
            ),
            "purpose": (
                "Reflect on long-term direction, identity, values, and progress. "
                "Ask whether recent actions align with the AI's purpose and the user's vision. "
                "Clarify what feels meaningful to pursue next."
            ),
            "maintenance": (
                "Care for the system and its environment. "
                "Review logs, resources, dependencies, memory, data quality, and accumulated clutter. "
                "Prefer gentle organization, preservation of useful history, and improvements that keep the system healthy."
            ),
        }

        tasks = []
        for d in low_desires[:self._max_tasks]:
            action = task_templates.get(d["name"], f"Work on improving {d['name']}")
            tasks.append({
                "desire": d["name"],
                "action": action,
                "expected_impact": 0.5,
            })
        return tasks

    def _execute_tasks(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute tasks using the AutonomousPlanner for real tool execution."""
        from aegis_ai.autonomous.planner import AutonomousPlanner

        planner = AutonomousPlanner(
            llm_provider=self._llm,
            tool_broker=self._broker,
            world_state_store=self._world,
            memory_store=self._memory,
            data_dir=str(self._data_dir / "plans"),
        )

        results = []
        for task in tasks:
            desire_name = task.get("desire", "unknown")
            action = task.get("action", "Unknown task")

            logger.info("Planning task: %s (for %s)", action[:50], desire_name)

            plan = planner.plan(action, context=f"Desire: {desire_name}")
            if plan.status.value == "cancelled":
                results.append({
                    "desire": desire_name, "action": action,
                    "result": plan.result_summary, "success": False,
                })
                continue

            plan = planner.execute_plan(plan)
            success = plan.status.value == "completed"
            results.append({
                "desire": desire_name, "action": action,
                "result": plan.result_summary or f"Plan {plan.status.value}",
                "success": success,
                "plan_id": plan.plan_id,
                "subtask_count": len(plan.subtasks),
            })

        return results

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
