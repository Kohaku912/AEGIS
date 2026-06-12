"""AEGIS Browser Server — entry point.

Usage:
    python -m aegis_browser.main

Currently shows status only. Real browser-use integration requires
playwright and browser-use packages.
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
    logger.info("AEGIS Browser Server v0.1.0")
    logger.info("gRPC: %s:%d", config.grpc_host, config.grpc_port)
    logger.info("AI Server: %s", config.ai_server_addr)
    logger.info("Headless: %s", config.browser_headless)

    logger.info("Registered capabilities: %d", len(CAPABILITIES))
    for cap_id, info in CAPABILITIES.items():
        logger.info("  %s (level=%s)", cap_id, info["safety_level"].name)

    logger.info("Blocked capabilities: %d", len(BLOCKED_CAPABILITIES))
    for cap_id, reason in BLOCKED_CAPABILITIES.items():
        logger.info("  %s — %s", cap_id, reason)

    logger.info("Browser Server ready (stub mode).")
    logger.info("Real browser-use integration requires: pip install playwright browser-use")

    try:
        while True:
            import time
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Shutdown requested — stopping.")


if __name__ == "__main__":
    main()
