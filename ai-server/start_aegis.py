"""AEGIS Unified Startup — starts all services.

Services:
- AI Server (gRPC) on port 50051
- Dashboard on port 8090
- Web Chat on port 8091
- CLI in terminal

User interaction:
- Web Chat: http://127.0.0.1:8091/chat
- CLI: Terminal input
- Dashboard: http://127.0.0.1:8090/ (monitoring)
- Approval UI: http://127.0.0.1:8080/ (when needed)

Usage:
    python start_aegis.py
"""

from __future__ import annotations

import logging
import os
import sys
import threading

# Set DeepSeek API key
os.environ["OPENAI_API_KEY"] = os.environ.get("DEEPSEEK_API_KEY", "")
os.environ["OPENAI_BASE_URL"] = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_startup")


def start_grpc_server():
    """Start AI Server gRPC in background thread."""
    from aegis_ai.config import get_config
    from aegis_ai.grpc_server import serve

    config = get_config()
    logger.info("AI Server (gRPC): starting on %s:%d", config.grpc_host, config.grpc_port)
    serve(config)


def start_dashboard():
    """Start Dashboard in background thread."""
    from aegis_ai.web.dashboard_routes import DashboardApp

    logger.info("Dashboard: starting on http://127.0.0.1:8090")
    app = DashboardApp()
    app.run(host="127.0.0.1", port=8090, debug=False)


def start_web_chat():
    """Start Web Chat in background thread."""
    from aegis_ai.interaction.channels.web import WebChatApp
    from aegis_ai.interaction.router import InteractionRouter
    from aegis_ai.interaction.session import SessionManager
    from aegis_ai.llm.factory import create_llm_provider

    llm = create_llm_provider()
    router = InteractionRouter(llm_provider=llm)
    sessions = SessionManager()
    logger.info("Web Chat: starting on http://127.0.0.1:8091/chat")
    app = WebChatApp(router=router, session_manager=sessions)
    app.run(host="127.0.0.1", port=8091, debug=False)


def start_cli():
    """Start CLI in main thread."""
    from aegis_ai.interaction.channels.cli import CLIChannel
    from aegis_ai.interaction.router import InteractionRouter
    from aegis_ai.interaction.session import SessionManager
    from aegis_ai.llm.factory import create_llm_provider

    llm = create_llm_provider()
    router = InteractionRouter(llm_provider=llm)
    sessions = SessionManager()
    cli = CLIChannel(router=router, session_manager=sessions)

    print()
    print("=" * 60)
    print("  AEGIS — Autonomous Multi-Device AI")
    print("=" * 60)
    print()
    print("  AIに指示を出すには:")
    print("    1. CLI:   このターミナルで直接入力")
    print("    2. Web:   http://127.0.0.1:8091/chat")
    print()
    print("  モニタリング:")
    print("    Dashboard:   http://127.0.0.1:8090/")
    print("    Approval UI: http://127.0.0.1:8080/ (承認が必要な時)")
    print()
    print("  例: 「天気を調べて」「スクリーンショットを撮って」")
    print("=" * 60)
    print()

    cli.run()


def main():
    """Start all AEGIS services."""
    # Start background services
    threads = []

    # gRPC server
    t1 = threading.Thread(target=start_grpc_server, daemon=True)
    t1.start()
    threads.append(t1)

    # Dashboard
    t2 = threading.Thread(target=start_dashboard, daemon=True)
    t2.start()
    threads.append(t2)

    # Web Chat
    t3 = threading.Thread(target=start_web_chat, daemon=True)
    t3.start()
    threads.append(t3)

    # Wait for services to start
    import time
    time.sleep(2)

    # Start CLI in main thread
    start_cli()


if __name__ == "__main__":
    main()
