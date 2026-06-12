"""Simple AEGIS Dashboard using Python's built-in HTTP server.

This avoids Flask binding issues on Windows.

Usage:
    python -m aegis_ai.http_dashboard
"""

from __future__ import annotations

import json
import logging
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_ai.http_dashboard")

_start_time = time.time()


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for AEGIS Dashboard."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/" or self.path == "/dashboard":
            self._serve_home()
        elif self.path == "/health":
            self._serve_health()
        elif self.path == "/api/status":
            self._serve_api_status()
        else:
            self._serve_404()

    def _serve_home(self):
        """Serve the home page."""
        uptime = time.time() - _start_time
        content = f"""
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
        self._send_response(200, "text/html", content)

    def _serve_health(self):
        """Serve health check."""
        data = {
            "status": "ok",
            "component": "dashboard",
            "uptime_seconds": time.time() - _start_time,
        }
        self._send_json(200, data)

    def _serve_api_status(self):
        """Serve API status."""
        data = {
            "status": "running",
            "services": {
                "dashboard": "ok",
                "ai_server": "check_port_50051",
                "pc_server": "check_port_50052",
                "browser_server": "check_port_50053",
            },
            "uptime_seconds": time.time() - _start_time,
        }
        self._send_json(200, data)

    def _serve_404(self):
        """Serve 404 page."""
        self._send_response(404, "text/plain", "Not Found")

    def _send_response(self, code: int, content_type: str, content: str):
        """Send HTTP response."""
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(content.encode())

    def _send_json(self, code: int, data: dict):
        """Send JSON response."""
        self._send_response(code, "application/json", json.dumps(data))

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    """Start the Dashboard server."""
    host = "0.0.0.0"
    port = 8090
    
    logger.info("Starting AEGIS Dashboard on http://%s:%d", host, port)
    
    server = HTTPServer((host, port), DashboardHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
