"""AEGIS Browser Server — entry point.

Usage:
    python -m aegis_browser.main

Uses browser-use for AI-driven browser automation.
"""

from __future__ import annotations

import logging
import sys

from aegis_browser.config import Config
from aegis_browser.safety import CAPABILITIES, BLOCKED_CAPABILITIES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_browser.main")


def main() -> None:
    """Start the AEGIS Browser Server."""
    config = Config()
    logger.info("AEGIS Browser Server v0.2.0")
    logger.info("gRPC: %s:%d", config.grpc_host, config.grpc_port)
    logger.info("AI Server: %s", config.ai_server_addr)
    logger.info("Headless: %s", config.browser_headless)

    logger.info("Registered capabilities: %d", len(CAPABILITIES))
    for cap_id, info in CAPABILITIES.items():
        logger.info("  %s (level=%s)", cap_id, info["safety_level"].name)

    logger.info("Blocked capabilities: %d", len(BLOCKED_CAPABILITIES))
    for cap_id, reason in BLOCKED_CAPABILITIES.items():
        logger.info("  %s — %s", cap_id, reason)

    # Quick browser-use test
    logger.info("Testing browser-use import...")
    try:
        from browser_use import Agent
        logger.info("browser-use Agent imported successfully")
    except ImportError as e:
        logger.error("browser-use import failed: %s", e)
        logger.info("Install with: pip install browser-use playwright")
        sys.exit(1)

    logger.info("Browser Server ready (browser-use mode).")
    logger.info("Press Ctrl+C to stop.")

    try:
        while True:
            import time
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Shutdown requested — stopping.")


if __name__ == "__main__":
    main()
