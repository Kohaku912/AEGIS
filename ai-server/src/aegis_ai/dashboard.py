"""Start AEGIS Dashboard server.

Usage:
    python -m aegis_ai.dashboard
"""

from __future__ import annotations

import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_ai.dashboard")


def main() -> None:
    """Start the Dashboard server."""
    from aegis_ai.web.dashboard_routes import DashboardApp
    
    host = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    port = int(os.getenv("DASHBOARD_PORT", "8090"))
    
    logger.info("Starting AEGIS Dashboard on http://%s:%d", host, port)
    app = DashboardApp()
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
