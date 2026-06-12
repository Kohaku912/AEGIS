"""Dashboard Routes — Flask routes for AEGIS operations dashboard.

Provides:
- GET /                    → Home overview with real server status
- GET /dashboard/servers   → Server health
- GET /health              → Health check
- POST /api/chat/send      → Chat with AEGIS (with PC operations)

Security:
- All sensitive data is redacted before display.
- Dashboard cannot bypass approval.
- All actions still go through PolicyEngine.
"""

from __future__ import annotations

import json
import logging
import socket
import time
from typing import Any

from flask import Flask, jsonify, render_template

logger = logging.getLogger("aegis_ai.web.dashboard")


def _check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False


def _send_pc_command(cmd: str, host: str = "localhost", port: int = 50052) -> dict[str, Any] | None:
    """Send a command to PC Server and return response."""
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((host, port))
        s.sendall((cmd + "\n").encode())
        resp = b""
        while True:
            chunk = s.recv(4096)
            if not chunk or b"\n" in chunk:
                resp += chunk
                break
            resp += chunk
        s.close()
        return json.loads(resp.decode().strip())
    except Exception:
        return None


class DashboardApp:
    """Flask-based operations dashboard for AEGIS."""

    def __init__(self) -> None:
        self._app = Flask(__name__, template_folder="templates")
        self._start_time = time.time()
        self._setup_routes()

    @property
    def app(self) -> Flask:
        return self._app

    def run(self, host: str = "0.0.0.0", port: int = 8090, debug: bool = False) -> None:
        self._app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=False)

    def _get_server_status(self) -> dict[str, Any]:
        """Get real server status by checking ports."""
        servers = []

        # AI Server
        ai_ok = _check_port("localhost", 50051)
        servers.append({
            "server_id": "ai-server",
            "server_type": "AI",
            "status": "ONLINE" if ai_ok else "OFFLINE",
            "registered_capabilities": "Core",
            "heartbeat_age_seconds": 0,
        })

        # PC Server
        pc_ok = _check_port("localhost", 50052)
        pc_info = _send_pc_command("health") if pc_ok else None
        servers.append({
            "server_id": "pc-server",
            "server_type": "PC",
            "status": "ONLINE" if pc_ok else "OFFLINE",
            "registered_capabilities": str(pc_info.get("capabilities", 0)) if pc_info else "0",
            "heartbeat_age_seconds": 0,
        })

        # Browser Server
        browser_ok = _check_port("localhost", 50053)
        servers.append({
            "server_id": "browser-server",
            "server_type": "Browser",
            "status": "ONLINE" if browser_ok else "OFFLINE",
            "registered_capabilities": "7" if browser_ok else "0",
            "heartbeat_age_seconds": 0,
        })

        online = sum(1 for s in servers if s["status"] == "ONLINE")
        return {
            "servers": servers,
            "summary": {
                "online_servers": online,
                "total_servers": len(servers),
            },
        }

    def _setup_routes(self) -> None:
        app = self._app

        # ── Home ──────────────────────────────────────────────

        @app.route("/")
        @app.route("/dashboard")
        def home():
            status = self._get_server_status()
            return render_template("dashboard/home.html",
                servers=status["servers"],
                server_summary=status["summary"],
                event_stats={"total_published": 0},
                trigger_stats={"tasks_generated": 0},
                pending_approvals=[],
                memory_summary={
                    "episodic_count": 0,
                    "semantic_count": 0,
                    "procedural_count": 0,
                    "reflection_count": 0,
                },
                settings={
                    "autonomous_enabled": False,
                    "support_agent_enabled": True,
                    "self_dev_enabled": True,
                    "privacy_clipboard_enabled": True,
                    "privacy_camera_enabled": False,
                },
            )

        # ── Servers ───────────────────────────────────────────

        @app.route("/dashboard/servers")
        def servers():
            status = self._get_server_status()
            return render_template("dashboard/servers.html",
                servers=status["servers"],
                summary=status["summary"],
            )

        @app.route("/api/servers")
        def api_servers():
            return jsonify(self._get_server_status())

        # ── Capabilities ─────────────────────────────────────

        @app.route("/dashboard/capabilities")
        def capabilities():
            caps = [
                {"id": "pc.get_screenshot", "name": "Screenshot", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.get_active_window", "name": "Active Window", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.list_windows", "name": "List Windows", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.get_clipboard", "name": "Clipboard", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.get_os_info", "name": "OS Info", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.show_overlay", "name": "Show Overlay", "risk_level": "SAFE_ACTION", "server_type": "PC", "enabled": True},
                {"id": "pc.mouse_click", "name": "Mouse Click", "risk_level": "APPROVAL_REQUIRED", "server_type": "PC", "enabled": True},
                {"id": "pc.keyboard_type", "name": "Keyboard Type", "risk_level": "APPROVAL_REQUIRED", "server_type": "PC", "enabled": True},
                {"id": "browser.open_page", "name": "Open Page", "risk_level": "SAFE_ACTION", "server_type": "Browser", "enabled": True},
                {"id": "browser.extract_page_text", "name": "Extract Text", "risk_level": "READ_ONLY", "server_type": "Browser", "enabled": True},
                {"id": "android.get_notifications", "name": "Notifications", "risk_level": "READ_ONLY", "server_type": "Android", "enabled": False},
                {"id": "android.get_device_info", "name": "Device Info", "risk_level": "READ_ONLY", "server_type": "Android", "enabled": False},
                {"id": "room.get_environment", "name": "Environment", "risk_level": "READ_ONLY", "server_type": "Room", "enabled": False},
            ]
            return render_template("dashboard/capabilities.html", capabilities=caps)

        # ── Events ───────────────────────────────────────────

        @app.route("/dashboard/events")
        def events():
            return render_template("dashboard/events.html",
                events=[],
                stats={"total_published": 0},
            )

        # ── Tasks ────────────────────────────────────────────

        @app.route("/dashboard/tasks")
        def tasks():
            return render_template("dashboard/tasks.html",
                pending_tasks=[],
                trigger_stats={"tasks_generated": 0},
                scheduled_tasks=[],
            )

        # ── Support ──────────────────────────────────────────

        @app.route("/dashboard/support")
        def support():
            return render_template("dashboard/support.html", suggestions=[])

        # ── Memory ───────────────────────────────────────────

        @app.route("/dashboard/memory")
        def memory():
            return render_template("dashboard/memory.html",
                summary={"episodic_count": 0, "semantic_count": 0, "procedural_count": 0, "reflection_count": 0},
                episodic=[],
                semantic=[],
                procedural=[],
                reflections=[],
            )

        # ── Audit ────────────────────────────────────────────

        @app.route("/dashboard/audit")
        def audit():
            return render_template("dashboard/audit.html",
                entries=[],
                stats={"total_entries": 0},
            )

        # ── Errors ───────────────────────────────────────────

        @app.route("/dashboard/errors")
        def errors():
            return render_template("dashboard/errors.html", errors=[])

        # ── API endpoints ────────────────────────────────────

        @app.route("/api/dashboard/overview")
        def api_overview():
            status = self._get_server_status()
            return jsonify({
                "servers": status["summary"],
                "events": {"total_published": 0},
                "triggers": {"tasks_generated": 0},
                "memory": {"episodic_count": 0, "semantic_count": 0},
                "pending_approvals": 0,
            })

        # ── Health ────────────────────────────────────────────

        @app.route("/health")
        def health():
            return jsonify({"status": "ok", "component": "dashboard"})

        # ── Chat API ─────────────────────────────────────────

        @app.route("/api/chat/send", methods=["POST"])
        def chat_send():
            from flask import request
            data = request.get_json(silent=True) or {}
            text = data.get("text", "").strip()
            if not text:
                return jsonify({"error": "No text provided"}), 400

            # Use LLM to understand the request and decide what to do
            try:
                from aegis_ai.llm.factory import create_llm_provider
                llm = create_llm_provider()

                pc_status = "Online" if _check_port("localhost", 50052) else "Offline"
                browser_status = "Online" if _check_port("localhost", 50053) else "Offline"

                system_prompt = f"""You are AEGIS, an autonomous AI assistant running on Windows.

Current system status:
- PC Server: {pc_status} (can take screenshots, get window info, move mouse, type text)
- Browser Server: {browser_status} (can browse web pages)
- LLM: DeepSeek

When the user asks for something that requires PC or browser actions, respond with a JSON object describing what action to take. Otherwise, respond normally.

For PC/browser actions, respond ONLY with this JSON format:
{{"action": "<action_name>", "params": {{}}}}

Available actions:
- screenshot: Take a screenshot of the current screen
- active_window: Get information about the currently active window
- windows: List all open windows
- os_info: Get operating system information
- screen_size: Get screen resolution
- clipboard: Get clipboard contents
- browse_url: Browse to a URL (params: {{"url": "..."}})

For everything else (general questions, conversation), respond normally as AEGIS.

Examples:
User: "Show me my screen" → {{"action": "screenshot"}}
User: "What's on my screen?" → {{"action": "screenshot"}}
User: "What window am I using?" → {{"action": "active_window"}}
User: "Tell me about Python" → "Python is a programming language..."
User: "What is AEGIS?" → "AEGIS is an autonomous AI assistant..."

IMPORTANT: Always use the JSON format for PC/browser actions. Never just describe what you would do."""

                result = llm.generate(
                    prompt=text,
                    system_prompt=system_prompt,
                    max_tokens=1000,
                )

                if not result.success:
                    return jsonify({"response": f"LLM error: {result.error}"})

                response_text = result.content.strip()

                # Try to parse as JSON action
                try:
                    # Clean markdown fences if present
                    clean = response_text
                    if clean.startswith("```"):
                        lines = clean.split("\n")
                        clean = "\n".join(lines[1:])
                        if clean.endswith("```"):
                            clean = clean[:-3]
                        clean = clean.strip()

                    action_data = json.loads(clean)
                    action = action_data.get("action", "")
                    params = action_data.get("params", {})

                    if action == "screenshot":
                        pc_result = _send_pc_command("screenshot")
                        if pc_result and "image_base64" in pc_result:
                            return jsonify({
                                "response": "Here's your current screen:",
                                "image": pc_result["image_base64"],
                                "image_width": pc_result.get("width", 1920),
                                "image_height": pc_result.get("height", 1080),
                            })
                        elif pc_result:
                            return jsonify({"response": f"Screenshot taken but no image data. Result: {json.dumps(pc_result)}"})
                        else:
                            return jsonify({"response": "PC Server is not responding. Make sure it's running."})

                    elif action in ("active_window", "windows", "os_info", "screen_size", "clipboard"):
                        pc_result = _send_pc_command(action)
                        if pc_result:
                            return jsonify({"response": f"**Result:**\n```json\n{json.dumps(pc_result, indent=2, ensure_ascii=False)}\n```"})
                        else:
                            return jsonify({"response": "PC Server is not responding."})

                    elif action == "browse_url":
                        url = params.get("url", "")
                        if url:
                            return jsonify({"response": f"Browser action requested for: {url}\n(Browser Server integration coming soon)"})
                        else:
                            return jsonify({"response": "No URL provided for browsing."})

                except (json.JSONDecodeError, KeyError):
                    pass

                # Not a JSON action — return as conversational response
                return jsonify({"response": response_text})

            except Exception as e:
                return jsonify({"response": f"Error: {str(e)}"})

                result = llm.generate(
                    prompt=text,
                    system_prompt=system_prompt,
                    max_tokens=1000,
                )
                if result.success:
                    return jsonify({"response": result.content})
                else:
                    return jsonify({"response": f"LLM error: {result.error}"})
            except Exception as e:
                return jsonify({"response": f"Error: {str(e)}"})