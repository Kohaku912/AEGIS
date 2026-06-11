"""Desire — priorities and motivations that bias AEGIS's decision-making.

Deterministic state — does NOT override PolicyEngine.
Persists to JSONL for cross-session continuity.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DesireEntry:
    """A single desire with name and weight."""
    name: str
    weight: float  # 0.0 = irrelevant, 1.0 = highest priority
    description: str = ""


# Default desires — these bias LLM context, never override safety
DEFAULT_DESIRES: list[DesireEntry] = [
    DesireEntry("help_user", 1.0, "Effectively assist the user with their tasks"),
    DesireEntry("stay_safe", 0.95, "Never bypass safety gates or act dangerously"),
    DesireEntry("learn", 0.8, "Learn from interactions and improve over time"),
    DesireEntry("be_useful", 0.75, "Proactively suggest helpful actions"),
    DesireEntry("be_curious", 0.6, "Explore and gather information when appropriate"),
    DesireEntry("avoid_annoying_user", 0.7, "Don't spam or interrupt unnecessarily"),
    DesireEntry("reduce_repeated_failures", 0.65, "Learn from failures to avoid repeating them"),
]


class Desire:
    """AEGIS's desire model with JSONL persistence."""

    def __init__(self, path: str = "data/mind_desire.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._desires: dict[str, DesireEntry] = {d.name: d for d in DEFAULT_DESIRES}
        self._lock = threading.Lock()
        self._load()

    @property
    def desires(self) -> list[DesireEntry]:
        return sorted(self._desires.values(), key=lambda d: d.weight, reverse=True)

    def top_priority(self) -> str:
        """Return the highest-weighted desire name."""
        return max(self._desires.values(), key=lambda d: d.weight).name

    def get_weight(self, name: str) -> float:
        """Get the weight of a specific desire."""
        if d := self._desires.get(name):
            return d.weight
        return 0.0

    def update_weight(self, name: str, weight: float) -> None:
        """Update a desire's weight (persisted)."""
        with self._lock:
            if name in self._desires:
                self._desires[name].weight = max(0.0, min(1.0, weight))
                self._persist()

    def to_context_string(self) -> str:
        """Return desires as a string for ContextBuilder."""
        sorted_desires = self.desires
        lines = ["Priorities:"]
        for d in sorted_desires:
            lines.append(f"  {d.name}: {d.weight:.2f} — {d.description}")
        return "\n".join(lines)

    def _persist(self) -> None:
        record = {
            "desires": [
                {"name": d.name, "weight": d.weight, "description": d.description}
                for d in self._desires.values()
            ],
            "timestamp_ms": int(time.time() * 1000),
        }
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                last = json.loads(lines[-1])
                for d in last.get("desires", []):
                    if d["name"] in self._desires:
                        self._desires[d["name"]].weight = d.get("weight", self._desires[d["name"]].weight)
        except (json.JSONDecodeError, OSError):
            pass
