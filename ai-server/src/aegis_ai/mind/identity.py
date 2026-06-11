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
            f"Safety: {self._config.safety_policy}",
        ]
        return "\n".join(parts)

    def update_values(self, values: list[str]) -> None:
        """Update identity values (persisted)."""
        with self._lock:
            self._config.values = values
            self._persist()

    def _persist(self) -> None:
        record = {
            "name": self._config.name,
            "role": self._config.role,
            "values": self._config.values,
            "safety_policy": self._config.safety_policy,
            "self_improvement_policy": self._config.self_improvement_policy,
            "user_support_policy": self._config.user_support_policy,
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
                self._config.values = last.get("values", self._config.values)
                self._config.safety_policy = last.get("safety_policy", self._config.safety_policy)
                self._config.self_improvement_policy = last.get(
                    "self_improvement_policy", self._config.self_improvement_policy,
                )
                self._config.user_support_policy = last.get(
                    "user_support_policy", self._config.user_support_policy,
                )
        except (json.JSONDecodeError, OSError):
            pass
