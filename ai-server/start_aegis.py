"""AEGIS unified startup.

Creates one AegisRuntime and injects it into every process-local entry point:
gRPC, Dashboard, CLI, and the Autonomous Loop.
"""

from __future__ import annotations

import logging
import os
import threading
import time

# Set DeepSeek-compatible environment defaults.
os.environ["OPENAI_API_KEY"] = os.environ.get("DEEPSEEK_API_KEY", "")
os.environ["OPENAI_BASE_URL"] = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_startup")


def start_grpc_server(runtime):
    """Start AI Server gRPC in a background thread."""
    from aegis_ai.grpc_server import serve

    config = runtime.config
    logger.info("AI Server (gRPC): starting on %s:%d", config.grpc_host, config.grpc_port)
    serve(config=config, runtime=runtime)


def start_dashboard(runtime):
    """Start Dashboard in a background thread."""
    from aegis_ai.web.dashboard_routes import DashboardApp

    logger.info("Dashboard: starting on http://0.0.0.0:8090")
    app = DashboardApp(runtime=runtime)
    app.run(host="0.0.0.0", port=8090, debug=False)


def start_cli(runtime):
    """Start CLI in the main thread."""
    from aegis_ai.interaction.channels.cli import CLIChannel

    cli = CLIChannel(
        router=runtime.interaction_router,
        session_manager=runtime.session_manager,
    )

    print()
    print("=" * 60)
    print("  AEGIS - Autonomous Multi-Device AI")
    print("=" * 60)
    print()
    print("  Interfaces:")
    print("    1. CLI:   type directly in this terminal")
    print("    2. Web:   http://0.0.0.0:8090/chat")
    print()
    print("  Monitoring:")
    print("    Dashboard:   http://0.0.0.0:8090/")
    print("=" * 60)
    print()

    cli.run()


def main():
    """Start all AEGIS services from one Runtime composition root."""
    from aegis_ai.runtime import get_runtime

    runtime = get_runtime()
    runtime.start_autonomous_if_enabled()

    threads = [
        threading.Thread(target=start_grpc_server, args=(runtime,), daemon=True),
        threading.Thread(target=start_dashboard, args=(runtime,), daemon=True),
    ]
    for thread in threads:
        thread.start()

    time.sleep(2)
    start_cli(runtime)


if __name__ == "__main__":
    main()
