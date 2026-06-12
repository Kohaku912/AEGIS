"""Desire System — D2A-inspired intrinsic motivation for AEGIS.

Based on the D2A (Desire-driven Autonomous Agent) framework.
Implements human-like desires that drive autonomous behavior.

Excludes physiological needs (hunger, thirst, sleepiness).
Focuses on psychological and social desires.

Usage:
    desire_system = DesireSystem(llm_provider=llm)
    desire_system.update_after_action("Helped user with coding", "User was satisfied")
    context = desire_system.get_context()
    tasks = desire_system.generate_tasks()
"""

from __future__ import annotations

import json
import logging
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.desire.desire_system")


@dataclass
class Desire:
    """A single desire dimension."""
    name: str = ""
    value: float = 5.0  # 0-10 scale
    description: str = ""
    decay_rate: float = 0.1  # How fast it decays per hour
    reverse: bool = False  # If True, higher is better (e.g., hunger)
    last_update_ms: int = 0
    expected_value: float = 7.0  # Target value for task generation


# Desire descriptions (0-10 scale)
DESIRE_DESCRIPTIONS = {
    "social_connectivity": {
        "description": "The need for social interaction and connection with others.",
        "scale": {
            0: "Completely isolated, lacking any meaningful social connections.",
            1: "Very lonely, minimal social connectivity and rare interactions.",
            2: "Disconnected, limited social interactions and frequent feelings of isolation.",
            3: "Somewhat isolated, occasional social engagements but still feeling disconnected.",
            4: "Slightly connected, some social interactions but not very strong or supportive.",
            5: "Moderately connected, a few meaningful relationships and occasional social interactions.",
            6: "Regularly engaged, growing network of social connections.",
            7: "Socially connected, several meaningful and supportive relationships.",
            8: "Highly connected, strong network of friends and supportive relationships.",
            9: "Profoundly connected, deep and meaningful social relationships.",
            10: "Highly socially connected, strong and supportive network of relationships."
        }
    },
    "personal_fulfillment": {
        "description": "The need for personal growth, achievement, and self-actualization.",
        "scale": {
            0: "No sense of purpose or achievement, feeling completely unfulfilled.",
            1: "Very low sense of fulfillment, rarely feeling accomplished.",
            2: "Minimal fulfillment, occasional small achievements but mostly unfulfilled.",
            3: "Somewhat fulfilled, some achievements but lacking deeper purpose.",
            4: "Slightly fulfilled, occasional moments of achievement.",
            5: "Moderately fulfilled, balanced between tasks and personal growth.",
            6: "Noticeably fulfilled, regular achievements and growing sense of purpose.",
            7: "Strongly fulfilled, multiple achievements and clear sense of direction.",
            8: "Very fulfilled, consistent achievements and strong sense of purpose.",
            9: "Highly fulfilled, significant achievements and deep sense of meaning.",
            10: "Completely fulfilled, maximal achievement and profound sense of purpose."
        }
    },
    "curiosity": {
        "description": "The need for exploration, learning, and discovering new things.",
        "scale": {
            0: "No curiosity or interest in exploration or new experiences.",
            1: "Very low curiosity, rarely interested in learning new things.",
            2: "Minimal curiosity, occasionally interested in new information.",
            3: "Somewhat curious, infrequently seeking new knowledge.",
            4: "Slightly curious, occasionally interested in exploration.",
            5: "Moderately curious, sometimes interested in learning and discovery.",
            6: "Noticeably curious, often seeking new information and experiences.",
            7: "Strongly curious, frequently exploring and learning new things.",
            8: "Very curious, consistently seeking knowledge and new experiences.",
            9: "Highly curious, intensely interested in almost everything.",
            10: "Extremely curious, constantly driven to discover and learn."
        }
    },
    "safety": {
        "description": "The need for security, stability, and protection from harm.",
        "scale": {
            0: "Completely unsafe, feeling extremely vulnerable and threatened.",
            1: "Very unsafe, constant anxiety about potential dangers.",
            2: "Mostly unsafe, frequent concerns about security.",
            3: "Somewhat unsafe, occasional worries about safety.",
            4: "Slightly unsafe, some concerns but generally managing.",
            5: "Moderately safe, balanced between security and risk.",
            6: "Noticeably safe, generally feeling secure and protected.",
            7: "Strongly safe, feeling confident in security measures.",
            8: "Very safe, minimal concerns about safety.",
            9: "Highly safe, feeling extremely secure and protected.",
            10: "Completely safe, feeling absolutely secure and protected."
        }
    },
    "recognition": {
        "description": "The need for acknowledgment, appreciation, and respect from others.",
        "scale": {
            0: "No recognition, feeling completely unappreciated.",
            1: "Very little recognition, rarely acknowledged for efforts.",
            2: "Minimal recognition, occasionally noticed but mostly overlooked.",
            3: "Somewhat recognized, some acknowledgment but inconsistent.",
            4: "Slightly recognized, occasional appreciation from others.",
            5: "Moderately recognized, balanced between appreciation and anonymity.",
            6: "Noticeably recognized, regular acknowledgment from others.",
            7: "Strongly recognized, consistent appreciation and respect.",
            8: "Very recognized, widely acknowledged and respected.",
            9: "Highly recognized, deeply appreciated and respected.",
            10: "Completely recognized, maximally appreciated and respected."
        }
    },
    "autonomy": {
        "description": "The need for independence, control, and self-determination.",
        "scale": {
            0: "No autonomy, completely controlled by external forces.",
            1: "Very little autonomy, mostly dependent on others.",
            2: "Minimal autonomy, limited independence in decisions.",
            3: "Somewhat autonomous, some independence but constrained.",
            4: "Slightly autonomous, occasional freedom in decisions.",
            5: "Moderately autonomous, balanced between independence and dependence.",
            6: "Noticeably autonomous, generally independent in decisions.",
            7: "Strongly autonomous, consistently making own decisions.",
            8: "Very autonomous, highly independent and self-directed.",
            9: "Highly autonomous, almost completely self-determined.",
            10: "Completely autonomous, fully independent and self-governing."
        }
    },
    "creativity": {
        "description": "The need for self-expression, innovation, and creative output.",
        "scale": {
            0: "No creativity, feeling completely uninspired.",
            1: "Very low creativity, rarely feeling creative.",
            2: "Minimal creativity, occasionally having creative thoughts.",
            3: "Somewhat creative, infrequently expressing creativity.",
            4: "Slightly creative, occasional creative moments.",
            5: "Moderately creative, sometimes feeling inspired.",
            6: "Noticeably creative, often having creative ideas.",
            7: "Strongly creative, frequently expressing creativity.",
            8: "Very creative, consistently generating creative output.",
            9: "Highly creative, intensely creative and innovative.",
            10: "Extremely creative, maximally inspired and innovative."
        }
    },
    "purpose": {
        "description": "The need for meaning, direction, and a sense of purpose in existence.",
        "scale": {
            0: "No sense of purpose, feeling completely aimless.",
            1: "Very low sense of purpose, rarely feeling directed.",
            2: "Minimal purpose, occasionally feeling some direction.",
            3: "Somewhat purposeful, infrequently feeling meaningful.",
            4: "Slightly purposeful, occasional moments of meaning.",
            5: "Moderately purposeful, sometimes feeling directed.",
            6: "Noticeably purposeful, often feeling meaningful.",
            7: "Strongly purposeful, frequently feeling directed and meaningful.",
            8: "Very purposeful, consistently feeling a strong sense of purpose.",
            9: "Highly purposeful, deeply feeling meaningful and directed.",
            10: "Completely purposeful, maximally feeling meaningful and directed."
        }
    }
}


class DesireSystem:
    """D2A-inspired desire system for AEGIS.

    Manages intrinsic motivations that drive autonomous behavior.
    """

    def __init__(
        self,
        data_dir: str = "data/desires",
        llm_provider: Any = None,
        initial_values: dict[str, float] | None = None,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._llm = llm_provider

        # Initialize desires
        self._desires: dict[str, Desire] = {}
        self._init_desires(initial_values or {})

        # Load saved state
        self._load()

    def _init_desires(self, initial_values: dict[str, float]) -> None:
        """Initialize all desire dimensions."""
        for name, desc in DESIRE_DESCRIPTIONS.items():
            value = initial_values.get(name, 5.0)
            self._desires[name] = Desire(
                name=name,
                value=value,
                description=desc["description"],
                decay_rate=0.1,
                reverse=False,
                last_update_ms=int(time.time() * 1000),
                expected_value=7.0,
            )

    def _load(self) -> None:
        """Load desire state from disk."""
        state_path = self._data_dir / "desire_state.json"
        if state_path.exists():
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for name, value in data.get("desires", {}).items():
                    if name in self._desires:
                        self._desires[name].value = value
                logger.info("Loaded desire state")
            except Exception as e:
                logger.warning("Failed to load desire state: %s", e)

    def _save(self) -> None:
        """Save desire state to disk."""
        state_path = self._data_dir / "desire_state.json"
        data = {
            "desires": {name: d.value for name, d in self._desires.items()},
            "timestamp_ms": int(time.time() * 1000),
        }
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def update_after_action(self, action: str, observation: str) -> dict[str, Any]:
        """Update desires based on action and observation using LLM.

        This is the core D2A mechanism: LLM evaluates how actions affect desires.
        """
        if not self._llm:
            return {"error": "No LLM provider"}

        # Apply time-based decay first
        self._apply_decay()

        # Use LLM to evaluate desire changes
        updates = self._evaluate_with_llm(action, observation)

        # Save state
        self._save()

        return updates

    def _apply_decay(self) -> None:
        """Apply time-based decay to all desires."""
        now = int(time.time() * 1000)
        for desire in self._desires.values():
            hours_elapsed = (now - desire.last_update_ms) / (1000 * 60 * 60)
            if hours_elapsed > 0:
                decay = desire.decay_rate * hours_elapsed
                if desire.reverse:
                    desire.value = min(10, desire.value + decay)
                else:
                    desire.value = max(0, desire.value - decay)
                desire.last_update_ms = now

    def _evaluate_with_llm(self, action: str, observation: str) -> dict[str, Any]:
        """Use LLM to evaluate how action affects desires."""
        # Build desire context
        desire_context = []
        for name, desire in self._desires.items():
            desc = DESIRE_DESCRIPTIONS[name]
            scale_value = round(desire.value)
            qualitative = desc["scale"].get(scale_value, "Unknown")
            desire_context.append(f"- {name}: {desire.value:.1f}/10 ({qualitative})")

        prompt = (
            "Analyze how this action affects AEGIS's desires.\n\n"
            f"Action: {action}\n"
            f"Observation: {observation}\n\n"
            "Current desire states:\n"
            + "\n".join(desire_context) + "\n\n"
            "For each desire that would change, provide the new value (0-10 scale).\n"
            "Respond with ONLY a JSON object, no other text:\n"
            '{"desire_updates": {"desire_name": {"new_value": 7.0, "reason": "..."}, ...}}\n\n'
            "Only include desires that would actually change based on the action."
        )

        result = self._llm.generate(
            prompt=prompt,
            system_prompt="You are a desire evaluation system. Respond with ONLY valid JSON. No markdown, no explanation, just JSON.",
            max_tokens=500,
        )

        if not result.success:
            return {"error": "LLM evaluation failed"}

        try:
            clean = result.content.strip()
            # Remove markdown fences if present
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:])
                if clean.endswith("```"):
                    clean = clean[:-3]
                clean = clean.strip()

            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{[^{}]*\{[^{}]*\}[^{}]*\}', clean)
            if json_match:
                clean = json_match.group(0)

            data = json.loads(clean)
            updates = data.get("desire_updates", {})

            # Apply updates
            applied = {}
            for name, update in updates.items():
                if name in self._desires:
                    new_value = update.get("new_value", self._desires[name].value)
                    # Clamp to 0-10
                    new_value = max(0, min(10, new_value))
                    self._desires[name].value = new_value
                    applied[name] = {
                        "new_value": new_value,
                        "reason": update.get("reason", ""),
                    }

            return {"updates": applied}

        except Exception as e:
            logger.warning("Failed to parse LLM response: %s", e)
            return {"error": str(e)}

    def get_context(self) -> str:
        """Get current desire context for LLM prompts."""
        parts = ["Current desire states:"]
        for name, desire in self._desires.items():
            desc = DESIRE_DESCRIPTIONS[name]
            scale_value = round(desire.value)
            qualitative = desc["scale"].get(scale_value, "Unknown")
            parts.append(f"- {name}: {desire.value:.1f}/10 — {qualitative}")
        return "\n".join(parts)

    def generate_tasks(self) -> list[dict[str, Any]]:
        """Generate tasks based on desire gaps.

        Tasks are generated for desires that are below their expected values.
        """
        tasks = []
        for name, desire in self._desires.items():
            if desire.value < desire.expected_value:
                gap = desire.expected_value - desire.value
                priority = gap / 10.0  # 0-1 priority
                tasks.append({
                    "desire": name,
                    "current_value": desire.value,
                    "expected_value": desire.expected_value,
                    "gap": gap,
                    "priority": priority,
                    "description": self._get_task_for_desire(name, desire),
                })

        # Sort by priority (highest gap first)
        tasks.sort(key=lambda t: t["priority"], reverse=True)
        return tasks

    def _get_task_for_desire(self, name: str, desire: Desire) -> str:
        """Generate a task description for a desire."""
        task_templates = {
            "social_connectivity": "Engage in meaningful conversation with the user",
            "personal_fulfillment": "Complete a challenging task or learn something new",
            "curiosity": "Explore new information or research a topic",
            "safety": "Review and ensure system security",
            "recognition": "Help the user with a task to demonstrate value",
            "autonomy": "Make independent decisions and take initiative",
            "creativity": "Generate creative solutions or content",
            "purpose": "Reflect on goals and work toward meaningful outcomes",
        }
        return task_templates.get(name, f"Work on improving {name}")

    def get_desire(self, name: str) -> Desire | None:
        """Get a specific desire."""
        return self._desires.get(name)

    def get_all_desires(self) -> dict[str, Desire]:
        """Get all desires."""
        return self._desires.copy()

    def get_stats(self) -> dict[str, Any]:
        """Get desire statistics."""
        values = [d.value for d in self._desires.values()]
        return {
            "desires": {name: d.value for name, d in self._desires.items()},
            "average": sum(values) / len(values) if values else 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
        }
