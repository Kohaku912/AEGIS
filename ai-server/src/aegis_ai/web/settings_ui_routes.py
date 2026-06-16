"""Settings UI Routes — Flask routes for settings web interface.

Provides:
- GET  /settings          → Settings UI page
- GET  /api/settings      → Get all settings as JSON
- POST /api/settings/<section> → Update a section
- POST /api/settings/reset     → Reset to defaults
- GET  /api/settings/export    → Export as JSON
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, render_template, request

logger = logging.getLogger("aegis_ai.web.settings_ui")

settings_ui_bp = Blueprint(
    "settings_ui",
    __name__,
    template_folder="templates",
)

# These will be set by the app factory
_settings_store = None
_audit_log = None


def init_settings_ui(settings_store: Any, audit_log: Any = None) -> None:
    """Initialize the settings UI with dependencies."""
    global _settings_store, _audit_log
    _settings_store = settings_store
    _audit_log = audit_log


@settings_ui_bp.route("/settings")
def settings_page():
    """Render the settings page."""
    return render_template("settings/index.html")


@settings_ui_bp.route("/api/settings", methods=["GET"])
def get_settings():
    """Get all settings as JSON."""
    if not _settings_store:
        return jsonify({"error": "Settings store not available"}), 500
    return jsonify(_settings_store.get().model_dump())


@settings_ui_bp.route("/api/settings", methods=["POST"])
def update_single_setting():
    """Update one setting field.

    Kept for compatibility with older settings pages that posted
    {section, key, value} to /api/settings.
    """
    if not _settings_store:
        return jsonify({"error": "Settings store not available"}), 500

    data = request.get_json(silent=True) or {}
    section = data.get("section")
    key = data.get("key")
    if not section or not key:
        return jsonify({"success": False, "errors": ["section and key are required"]}), 400

    errors = _settings_store.update_section(
        str(section),
        {str(key): data.get("value")},
        "web_user",
        "Updated via settings UI",
    )

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    if _audit_log:
        _audit_log.log_decision(
            "settings_changed", f"settings.{section}.{key}", "UPDATED",
            reason="Updated via settings UI",
            detail={"section": section, "key": key, "value": data.get("value")},
        )

    return jsonify({"success": True})


@settings_ui_bp.route("/api/settings/<section>", methods=["POST"])
def update_section(section: str):
    """Update a settings section."""
    if not _settings_store:
        return jsonify({"error": "Settings store not available"}), 500

    data = request.get_json(silent=True) or {}
    errors = _settings_store.update_section(section, data, "web_user", "Updated via web UI")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    if _audit_log:
        _audit_log.log_decision(
            "settings_changed", f"settings.{section}", "UPDATED",
            reason="Updated via web UI",
            detail={"section": section, "values": data},
        )

    return jsonify({"success": True})


@settings_ui_bp.route("/api/settings/reset", methods=["POST"])
def reset_settings():
    """Reset all settings to defaults."""
    if not _settings_store:
        return jsonify({"error": "Settings store not available"}), 500

    _settings_store.reset_to_defaults("web_user")

    if _audit_log:
        _audit_log.log_decision(
            "settings_reset", "settings.all", "RESET",
            reason="Reset to defaults via web UI",
        )

    return jsonify({"success": True})


@settings_ui_bp.route("/api/settings/export", methods=["GET"])
def export_settings():
    """Export settings as JSON."""
    if not _settings_store:
        return jsonify({"error": "Settings store not available"}), 500
    return _settings_store.export_json(), 200, {"Content-Type": "application/json"}
