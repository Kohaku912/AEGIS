"""Configuration management for AEGIS Core.

Loads settings from environment variables with sensible defaults.
No secrets are read here — secrets are injected via environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """AEGIS Core configuration."""

    # ── gRPC Server ────────────────────────────────────────
    grpc_host: str = field(
        default_factory=lambda: os.getenv("ELLIE_GRPC_HOST", "0.0.0.0")
    )
    grpc_port: int = field(
        default_factory=lambda: int(os.getenv("ELLIE_GRPC_PORT", "50051"))
    )
    max_workers: int = field(
        default_factory=lambda: int(os.getenv("ELLIE_MAX_WORKERS", "10"))
    )

    # ── Event Bus ───────────────────────────────────────────
    dedup_window_ms: int = field(
        default_factory=lambda: int(os.getenv("ELLIE_DEDUP_WINDOW_MS", "30000"))
    )

    # ── Trigger Engine ──────────────────────────────────────
    trigger_enabled: bool = field(
        default_factory=lambda: os.getenv("ELLIE_TRIGGER_ENABLED", "true").lower() == "true"
    )

    # ── Policy Engine ───────────────────────────────────────
    policy_default_deny: bool = field(
        default_factory=lambda: os.getenv("ELLIE_POLICY_DEFAULT_DENY", "true").lower() == "true"
    )

    # ── Audit Log ───────────────────────────────────────────
    audit_path: str = field(
        default_factory=lambda: os.getenv("ELLIE_AUDIT_PATH", "data/audit.jsonl")
    )

    # ── Approval ────────────────────────────────────────────
    approval_timeout_ms: int = field(
        default_factory=lambda: int(os.getenv("ELLIE_APPROVAL_TIMEOUT_MS", "60000"))
    )
    approval_validity_ms: int = field(
        default_factory=lambda: int(os.getenv("ELLIE_APPROVAL_VALIDITY_MS", "300000"))
    )

    # ── LLM (未実装) ─────────────────────────────────────────
    llm_provider: str = field(
        default_factory=lambda: os.getenv("ELLIE_LLM_PROVIDER", "")
    )
    llm_model: str = field(
        default_factory=lambda: os.getenv("ELLIE_LLM_MODEL", "")
    )

    # ── Autonomous Loop ─────────────────────────────────────
    autonomous_loop_enabled: bool = field(
        default_factory=lambda: os.getenv("ELLIE_AUTONOMOUS_LOOP_ENABLED", "false").lower() == "true"
    )
    loop_cooldown_seconds: float = field(
        default_factory=lambda: float(os.getenv("ELLIE_LOOP_COOLDOWN_SECONDS", "5.0"))
    )


# Singleton instance
_config: Config | None = None


def get_config() -> Config:
    """Get the global Config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
