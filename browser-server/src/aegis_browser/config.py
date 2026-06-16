"""Configuration for AEGIS Browser Server."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_data_root() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


@dataclass
class Config:
    grpc_port: int = field(default_factory=lambda: int(os.getenv("AEGIS_GRPC_PORT", "50053")))
    grpc_host: str = field(default_factory=lambda: os.getenv("AEGIS_GRPC_HOST", "0.0.0.0"))
    ai_server_addr: str = field(default_factory=lambda: os.getenv("AEGIS_AI_GRPC_ADDR", "ai-server:50051"))
    server_id: str = field(default_factory=lambda: os.getenv("AEGIS_SERVER_ID", "browser-main"))
    log_level: str = field(default_factory=lambda: os.getenv("AEGIS_LOG_LEVEL", "INFO"))
    browser_headless: bool = field(
        default_factory=lambda: os.getenv("AEGIS_BROWSER_HEADLESS", "true").lower() == "true"
    )
    browser_timeout_ms: int = field(
        default_factory=lambda: int(os.getenv("AEGIS_BROWSER_TIMEOUT_MS", "30000"))
    )
    browser_channel: str = field(default_factory=lambda: os.getenv("AEGIS_BROWSER_CHANNEL", "chrome"))
    browser_profile_root: str = field(
        default_factory=lambda: os.getenv(
            "AEGIS_BROWSER_PROFILE_ROOT",
            str(_default_data_root() / "browser-profiles"),
        )
    )
    browser_session_root: str = field(
        default_factory=lambda: os.getenv(
            "AEGIS_BROWSER_SESSION_ROOT",
            str(_default_data_root() / "browser-sessions"),
        )
    )
    browser_trace_root: str = field(
        default_factory=lambda: os.getenv(
            "AEGIS_BROWSER_TRACE_ROOT",
            str(_default_data_root() / "traces"),
        )
    )
    browser_profile_name: str = field(
        default_factory=lambda: os.getenv("AEGIS_BROWSER_PROFILE_NAME", "default")
    )
    browser_use_cloud: bool = False
