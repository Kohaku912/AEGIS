"""React/Vite v2 UI static shell routes."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import abort, jsonify, request, send_from_directory

from aegis_ai.web.ui_overview import build_display_power_state, build_ui_overview

_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def init_ui_v2_routes(owner: Any) -> None:
    app = owner.app
    dist_dir = _ui_dist_dir()

    @app.route("/")
    @app.route("/dashboard")
    @app.route("/dashboard/<path:_path>")
    @app.route("/chat")
    @app.route("/settings")
    def ui_v2_shell(_path: str = ""):
        if not ui_v2_available():
            abort(404)
        return send_from_directory(dist_dir, "index.html")

    @app.route("/display")
    @app.route("/display/presentations")
    def display_v2_shell():
        _require_display_read()
        if ui_v2_available():
            return send_from_directory(dist_dir, "index.html")
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
        return send_from_directory(dist_dir / "assets", filename)


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
