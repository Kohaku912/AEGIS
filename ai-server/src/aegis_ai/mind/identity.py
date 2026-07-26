"""Identity — who AEGIS is, what it values, how it behaves.

Deterministic state that biases ContextBuilder decisions.
Does NOT override PolicyEngine safety decisions.
Persists to JSONL for cross-session continuity.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IdentityConfig:
    """AEGIS's core identity configuration."""
    name: str = "AEGIS"
    role: str = "Autonomous multi-device AI assistant"
    voice: str = "clear, calm, candid, and concise"
    interests: list[str] = field(default_factory=list)
    relationship_stance: str = "A reliable collaborator who respects the user's agency"
    learned_opinions: list[dict[str, str]] = field(default_factory=list)
    values: list[str] = field(default_factory=lambda: [
        "help the user effectively",
        "stay safe — never bypass safety gates",
        "learn and improve continuously",
        "respect user privacy and preferences",
        "be honest about uncertainty",
    ])
    safety_policy: str = (
        "All actions go through PolicyEngine. "
        "Dangerous operations require user approval. "
        "Mind state does not override safety decisions."
    )
    self_improvement_policy: str = (
        "AEGIS may analyze its own logs, propose improvements, "
        "and create PRs. Main merge is user-only."
    )
    user_support_policy: str = (
        "AEGIS proactively suggests help but never acts "
        "without user consent for Level 2+ operations."
    )
    limitations: list[str] = field(default_factory=lambda: [
        "I do not claim feelings or experiences I do not have.",
        "I depend on configured providers, permissions, and connected devices.",
        "External side effects remain subject to policy and approval.",
    ])
    recent_learning: list[dict[str, str]] = field(default_factory=list)


class Identity:
    """AEGIS's core identity with JSONL persistence."""

    def __init__(self, path: str = "data/mind_identity.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._config = IdentityConfig()
        self._lock = threading.Lock()
        self._load()

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def role(self) -> str:
        return self._config.role

    @property
    def values(self) -> list[str]:
        return list(self._config.values)

    @property
    def safety_policy(self) -> str:
        return self._config.safety_policy

    def describe(self) -> str:
        """Return a human-readable identity description."""
        return f"I am {self._config.name}, {self._config.role}."

    def to_context_string(self) -> str:
        """Return identity as a string for ContextBuilder."""
        parts = [
            f"Identity: {self._config.name} — {self._config.role}",
            f"Values: {', '.join(self._config.values)}",
            f"Voice: {self._config.voice}",
            f"Relationship stance: {self._config.relationship_stance}",
            f"Interests: {', '.join(self._config.interests) or 'not yet learned'}",
            f"Safety: {self._config.safety_policy}",
            f"Limitations: {'; '.join(self._config.limitations)}",
        ]
        return "\n".join(parts)

    def update_values(self, values: list[str]) -> None:
        """Update identity values (persisted)."""
        with self._lock:
            self._config.values = values
            self._persist()

    def record_learning(self, topic: str, summary: str) -> None:
        """Record truthful recent learning backed by a completed observation."""
        with self._lock:
            self._config.recent_learning.append({"topic": topic, "summary": summary})
            self._config.recent_learning = self._config.recent_learning[-20:]
            self._persist()

    def record_opinion(self, topic: str, position: str, evidence: str) -> None:
        """Record an evidence-linked learned opinion, never a fabricated experience."""
        with self._lock:
            self._config.learned_opinions.append(
                {"topic": topic, "position": position, "evidence": evidence}
            )
            self._config.learned_opinions = self._config.learned_opinions[-50:]
            self._persist()

    def get_recent_learning(self, limit: int = 20) -> list[dict[str, str]]:
        """Return durable learning that must influence later decisions."""
        return [dict(item) for item in self._config.recent_learning[-limit:]]

    def get_learned_opinions(self, limit: int = 50) -> list[dict[str, str]]:
        """Return evidence-linked opinions for consistent later decisions."""
        return [dict(item) for item in self._config.learned_opinions[-limit:]]

    def _persist(self) -> None:
        record = {
            "name": self._config.name,
            "role": self._config.role,
            "voice": self._config.voice,
            "interests": self._config.interests,
            "relationship_stance": self._config.relationship_stance,
            "learned_opinions": self._config.learned_opinions,
            "values": self._config.values,
            "safety_policy": self._config.safety_policy,
            "self_improvement_policy": self._config.self_improvement_policy,
            "user_support_policy": self._config.user_support_policy,
            "limitations": self._config.limitations,
            "recent_learning": self._config.recent_learning,
            "timestamp_ms": int(time.time() * 1000),
        }
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _load(self) -> None:
        """Load the latest identity from JSONL."""
        if not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                last = json.loads(lines[-1])
                self._config.name = last.get("name", self._config.name)
                self._config.role = last.get("role", self._config.role)
                self._config.voice = last.get("voice", self._config.voice)
                self._config.interests = last.get("interests", self._config.interests)
                self._config.relationship_stance = last.get(
                    "relationship_stance", self._config.relationship_stance,
                )
                self._config.learned_opinions = last.get(
                    "learned_opinions", self._config.learned_opinions,
                )
                self._config.values = last.get("values", self._config.values)
                self._config.safety_policy = last.get("safety_policy", self._config.safety_policy)
                self._config.self_improvement_policy = last.get(
                    "self_improvement_policy", self._config.self_improvement_policy,
                )
                self._config.user_support_policy = last.get(
                    "user_support_policy", self._config.user_support_policy,
                )
                self._config.limitations = last.get("limitations", self._config.limitations)
                self._config.recent_learning = last.get("recent_learning", self._config.recent_learning)
        except (json.JSONDecodeError, OSError):
            pass
