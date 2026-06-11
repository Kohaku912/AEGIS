"""Configuration for AEGIS Browser Server."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    grpc_port: int = field(default_factory=lambda: int(os.getenv("AEGIS_GRPC_PORT", "50052")))
    grpc_host: str = field(default_factory=lambda: os.getenv("AEGIS_GRPC_HOST", "0.0.0.0"))
    ai_server_addr: str = field(default_factory=lambda: os.getenv("AEGIS_AI_GRPC_ADDR", "ai-server:50051"))
    server_id: str = field(default_factory=lambda: os.getenv("AEGIS_SERVER_ID", "browser-main"))
    log_level: str = field(default_factory=lambda: os.getenv("AEGIS_LOG_LEVEL", "INFO"))
    browser_headless: bool = field(
        default_factory=lambda: os.getenv("AEGIS_BROWSER_HEADLESS", "true").lower() == "true")
    browser_timeout_ms: int = field(
        default_factory=lambda: int(os.getenv("AEGIS_BROWSER_TIMEOUT_MS", "30000")))
    browser_use_cloud: bool = False  # NOT using cloud — must ask user per Technology Decision Gate
