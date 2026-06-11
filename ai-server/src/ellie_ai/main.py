"""Ellie AI Server — entry point.

Usage:
    python -m ellie_ai.main
"""

from __future__ import annotations

import logging
import sys

from ellie_ai.config import get_config
from ellie_ai.grpc_server import serve

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ellie_ai.main")


def main() -> None:
    """Start the Ellie AI Server."""
    config = get_config()
    logger.info("Starting Ellie AI Server...")
    logger.info("gRPC: %s:%d", config.grpc_host, config.grpc_port)
    logger.info("Trigger Engine: %s", "enabled" if config.trigger_enabled else "disabled")
    logger.info("Autonomous Loop: %s", "enabled" if config.autonomous_loop_enabled else "disabled")

    try:
        serve(config)
    except KeyboardInterrupt:
        logger.info("Shutdown requested — stopping.")
    except Exception:
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
