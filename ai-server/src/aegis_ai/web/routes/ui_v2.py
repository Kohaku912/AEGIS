"""React/Vite v2 UI static shell routes."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Response, abort, jsonify, request, send_from_directory

from aegis_ai.web.ui_overview import build_display_power_state, build_ui_overview

_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}

# Legacy Jinja pages historically registered on these exact paths. When ui-v2 is
# enabled they must not win over the SPA on browser reload.
_SPA_ROOTS = ("/dashboard", "/chat", "/settings", "/display")
_SPA_JSON_EXEMPT = {
    "/display/overview",
    "/display/power-state",
    "/display/presentations/data",
}


def init_ui_v2_routes(owner: Any) -> None:
    app = owner.app
    dist_dir = _ui_dist_dir()

    def _spa_index() -> Response:
        response = send_from_directory(dist_dir, "index.html")
        # index.html must never be cached — hashed assets can stay immutable.
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        return response

    @app.before_request
    def ui_v2_prefer_spa_shell():
        """Serve the React shell for dashboard HTML paths even when legacy routes exist.

        Flask matches more-specific legacy rules (e.g. /dashboard/desires) before the
        /dashboard/<path> SPA catch-all, so a reload would show the old Jinja page.
        """
        if not ui_v2_available():
            return None
        if request.method != "GET":
            return None
        path = request.path or "/"
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/") or "/"
        if path.startswith("/api") or path.startswith("/assets") or path.startswith("/static"):
            return None
        if path.startswith(("/login", "/auth", "/health", "/webauthn", "/.well-known")):
            return None
        if path in _SPA_JSON_EXEMPT:
            return None
        if path == "/" or any(path == root or path.startswith(root + "/") for root in _SPA_ROOTS):
            accept = request.accept_mimetypes
            # Browser navigations prefer HTML; JSON API clients should pass through.
            if accept and accept.best_match(["application/json", "text/html"]) == "application/json":
                if "text/html" not in str(request.headers.get("Accept", "")):
                    return None
            return _spa_index()
        return None

    @app.route("/")
    @app.route("/dashboard")
    @app.route("/dashboard/<path:_path>")
    @app.route("/chat")
    @app.route("/settings")
    def ui_v2_shell(_path: str = ""):
        if not ui_v2_available():
            abort(404)
        return _spa_index()

    @app.route("/display")
    @app.route("/display/presentations")
    def display_v2_shell():
        _require_display_read()
        if ui_v2_available():
            return _spa_index()
        return owner.app.jinja_env.get_or_select_template("display/presentations.html").render()

    @app.route("/display/overview")
    def display_overview():
        _require_display_read()
        return jsonify(build_ui_overview(owner._runtime))

    @app.route("/display/power-state")
    def display_power_state():
        _require_display_read()
        return jsonify(build_display_power_state(owner._runtime))

    @app.route("/assets/<path:filename>")
    def ui_v2_assets(filename: str):
        if not ui_v2_available():
            abort(404)
        response = send_from_directory(dist_dir / "assets", filename)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


def ui_v2_available() -> bool:
    if os.getenv("AEGIS_UI_VERSION", "v2").strip().lower() != "v2":
        return False
    return (_ui_dist_dir() / "index.html").exists()


def _ui_dist_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "static" / "ui-v2"


def _require_display_read() -> None:
    if request.method != "GET":
        abort(405)
    token = os.getenv("AEGIS_DISPLAY_TOKEN", "").strip() or os.getenv("AEGIS_DISPLAY_READ_TOKEN", "").strip()
    provided = request.args.get("display_token", "") or request.headers.get("X-AEGIS-Display-Token", "")
    if token and provided == token:
        return
    host = _request_host_without_port()
    remote = (request.remote_addr or "").strip().lower()
    if host in _LOOPBACK_HOSTS:
        return
    if request.headers.get("X-Forwarded-Host"):
        abort(403)
    if remote in _LOOPBACK_HOSTS:
        return
    abort(403)


def _request_host_without_port() -> str:
    host = (request.headers.get("X-Forwarded-Host") or request.host or "").strip().lower()
    if host.startswith("["):
        return host.split("]", 1)[0].lstrip("[")
    return host.split(":", 1)[0]
