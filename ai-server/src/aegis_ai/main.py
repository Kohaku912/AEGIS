"""AEGIS Core — entry point.

Usage:
    python -m aegis_ai.main
"""

from __future__ import annotations

import logging
import sys

from aegis_ai.config import get_config
from aegis_ai.grpc_server import serve

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_ai.main")


def main() -> None:
    """Start the AEGIS Core."""
    config = get_config()
    logger.info("Starting AEGIS Core...")
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
