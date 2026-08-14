"""Docker entry point for AEGIS Core.

Runs gRPC and the Dashboard in one container without starting the CLI.
"""

from __future__ import annotations

import logging
import os
import signal
import threading
import time

from aegis_ai.production_readiness import is_production_mode
from aegis_ai.runtime import get_runtime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_ai.docker_entrypoint")

_STOP = threading.Event()


def _handle_stop(signum, frame) -> None:
    logger.info("Shutdown signal received: %s", signum)
    _STOP.set()


def _start_grpc(runtime) -> None:
    from aegis_ai.grpc_server import serve

    serve(config=runtime.config, runtime=runtime, stop_event=_STOP)


def _start_dashboard(runtime) -> None:
    from aegis_ai.web.dashboard_routes import DashboardApp

    host = os.getenv("AEGIS_DASHBOARD_HOST", "0.0.0.0")
    DashboardApp(runtime=runtime).run(host=host, port=8090, debug=False)


def _refresh_status_after_start(runtime) -> None:
    """Refresh cached status after sockets have had time to bind."""
    for _ in range(5):
        if _STOP.wait(1):
            return
        try:
            snapshot = runtime.status_manager.check_now()
            if (
                snapshot.get("ai-server", {}).get("status") == "online"
                and snapshot.get("dashboard", {}).get("status") == "online"
            ):
                return
        except Exception:
            logger.debug("Startup status refresh failed", exc_info=True)


def main() -> None:
    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    if is_production_mode():
        if os.getenv("AEGIS_AUTH_MODE", "passkey").strip().lower() != "passkey":
            raise SystemExit("AEGIS_AUTH_MODE=passkey is required when AEGIS_RUNTIME_MODE=production")
        if not os.getenv("AEGIS_SESSION_SECRET", "").strip():
            raise SystemExit("AEGIS_SESSION_SECRET is required when AEGIS_RUNTIME_MODE=production")

    runtime = get_runtime()
    runtime.start_autonomous_if_enabled()

    threads = [
        threading.Thread(target=_start_grpc, args=(runtime,), daemon=True, name="aegis-grpc"),
        threading.Thread(target=_start_dashboard, args=(runtime,), daemon=True, name="aegis-dashboard"),
    ]
    for thread in threads:
        thread.start()

    threading.Thread(
        target=_refresh_status_after_start,
        args=(runtime,),
        daemon=True,
        name="aegis-startup-status-refresh",
    ).start()

    logger.info("AEGIS Core Docker services started")
    while not _STOP.is_set():
        time.sleep(1)

    threads[0].join(timeout=6)
    runtime.stop()


if __name__ == "__main__":
    main()
