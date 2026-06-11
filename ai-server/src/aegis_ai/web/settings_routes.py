"""Settings Web Routes — Flask routes for AEGIS settings management UI.

Provides:
- GET  /settings              → view all settings
- GET  /settings/<section>    → view a specific section
- POST /settings/<section>    → update a section
- POST /settings/reset        → reset to defaults
- GET  /settings/export       → export as JSON
- POST /settings/import       → import from JSON
- GET  /settings/capabilities → list all capabilities with status

All changes are logged to AuditLog.
"""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.settings.store import SettingsStore

logger = logging.getLogger("aegis_ai.web.settings")


class SettingsWebApp:
    """Flask-based settings management UI for AEGIS.

    Provides REST API for reading and updating settings.
    All changes are validated and audited.
    """

    def __init__(
        self,
        settings_store: SettingsStore,
        audit_log: Any = None,
        tool_registry: Any = None,
    ) -> None:
        self._store = settings_store
        self._audit = audit_log
        self._registry = tool_registry

    def get_settings(self) -> dict[str, Any]:
        """Get all settings."""
        return self._store.get().model_dump()

    def get_section(self, section: str) -> dict[str, Any]:
        """Get a specific settings section."""
        settings = self._store.get()
        section_obj = getattr(settings, section, None)
        if section_obj is None:
            return {"error": f"Unknown section: {section}"}
        return section_obj.model_dump()

    def update_section(
        self,
        section: str,
        values: dict[str, Any],
        changed_by: str = "user",
        reason: str = "",
    ) -> dict[str, Any]:
        """Update a settings section."""
        errors = self._store.update_section(section, values, changed_by, reason)
        if errors:
            return {"success": False, "errors": errors}

        if self._audit:
            self._audit.log_decision(
                "settings_changed", f"settings.{section}", "UPDATED",
                reason=reason,
                detail={"section": section, "values": values},
            )

        return {"success": True}

    def reset_to_defaults(self, changed_by: str = "user") -> dict[str, Any]:
        """Reset all settings to defaults."""
        self._store.reset_to_defaults(changed_by)

        if self._audit:
            self._audit.log_decision(
                "settings_reset", "settings.all", "RESET",
                reason="Reset to defaults",
            )

        return {"success": True}

    def export_settings(self) -> str:
        """Export settings as JSON."""
        return self._store.export_json()

    def import_settings(
        self,
        json_str: str,
        changed_by: str = "user",
    ) -> dict[str, Any]:
        """Import settings from JSON."""
        errors = self._store.import_json(json_str, changed_by)
        if errors:
            return {"success": False, "errors": errors}

        if self._audit:
            self._audit.log_decision(
                "settings_imported", "settings.all", "IMPORTED",
                reason="Imported from JSON",
            )

        return {"success": True}

    def list_capabilities(self) -> list[dict[str, Any]]:
        """List all capabilities with their current status."""
        if not self._registry:
            return []

        settings = self._store.get()
        caps = self._registry.list_capabilities()
        result = []
        for cap in caps:
            disabled = cap.id in settings.capabilities.disabled_capabilities
            denied = cap.id in settings.capabilities.denylist
            result.append({
                "id": cap.id,
                "name": cap.name,
                "risk_level": cap.risk_level.name,
                "server_type": cap.server_type.name,
                "enabled": not disabled and not denied,
                "requires_approval": cap.requires_approval,
            })
        return result
