"""Docker entry point for AEGIS Core.

Runs gRPC, Dashboard, and Web Chat in one container without starting the CLI.
"""

from __future__ import annotations

import logging
import signal
import threading
import time

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

    serve(config=runtime.config, runtime=runtime)


def _start_dashboard(runtime) -> None:
    from aegis_ai.web.dashboard_routes import DashboardApp

    DashboardApp(runtime=runtime).run(host="0.0.0.0", port=8090, debug=False)


def _start_web_chat(runtime) -> None:
    from aegis_ai.interaction.channels.web import WebChatApp

    WebChatApp(router=runtime.interaction_router, session_manager=runtime.session_manager).run(
        host="0.0.0.0",
        port=8091,
        debug=False,
    )


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

    runtime = get_runtime()
    runtime.start_autonomous_if_enabled()

    threads = [
        threading.Thread(target=_start_grpc, args=(runtime,), daemon=True, name="aegis-grpc"),
        threading.Thread(target=_start_dashboard, args=(runtime,), daemon=True, name="aegis-dashboard"),
        threading.Thread(target=_start_web_chat, args=(runtime,), daemon=True, name="aegis-web-chat"),
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

    runtime.stop()


if __name__ == "__main__":
    main()
