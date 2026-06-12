"""Simple AEGIS Dashboard — minimal dependencies.

This is a simplified Dashboard that works without requiring
all the complex AEGIS services to be running.

Usage:
    python -m aegis_ai.simple_dashboard
"""

from __future__ import annotations

import logging
import time
from flask import Flask, jsonify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_ai.simple_dashboard")

app = Flask(__name__)

# Store some basic state
_start_time = time.time()


@app.route("/")
def home():
    """Dashboard home page."""
    uptime = time.time() - _start_time
    return f"""
    <html>
    <head><title>AEGIS Dashboard</title></head>
    <body style="font-family: sans-serif; padding: 20px; background: #0d1117; color: #e6edf3;">
        <h1 style="color: #58a6ff;">AEGIS Dashboard</h1>
        <p>Status: <span style="color: #3fb950;">Running</span></p>
        <p>Uptime: {uptime:.0f} seconds</p>
        <h2>Services</h2>
        <ul>
            <li><a href="/health" style="color: #58a6ff;">Health Check</a></li>
            <li><a href="/api/status" style="color: #58a6ff;">API Status</a></li>
        </ul>
        <h2>Quick Links</h2>
        <ul>
            <li><a href="http://127.0.0.1:8091/chat" style="color: #58a6ff;">Web Chat</a></li>
        </ul>
    </body>
    </html>
    """


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "component": "dashboard",
        "uptime_seconds": time.time() - _start_time,
    })


@app.route("/api/status")
def api_status():
    """API status endpoint."""
    return jsonify({
        "status": "running",
        "services": {
            "dashboard": "ok",
            "ai_server": "check_port_50051",
            "pc_server": "check_port_50052",
            "browser_server": "check_port_50053",
        },
        "uptime_seconds": time.time() - _start_time,
    })


if __name__ == "__main__":
    logger.info("Starting AEGIS Dashboard on http://0.0.0.0:8090")
    app.run(host="0.0.0.0", port=8090, debug=False, threaded=True)
