"""Start AEGIS Dashboard server.

Usage:
    python -m aegis_ai.dashboard
"""

from __future__ import annotations

import logging

from aegis_ai.web.dashboard_routes import DashboardApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_ai.dashboard")

if __name__ == "__main__":
    logger.info("Starting AEGIS Dashboard on http://127.0.0.1:8090")
    app = DashboardApp()
    app.run(host="127.0.0.1", port=8090, debug=False)
