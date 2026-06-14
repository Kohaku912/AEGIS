"""Settings Store — JSON-based persistence for AEGIS settings.

Thread-safe, with audit logging for all changes.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

from aegis_ai.settings.defaults import create_default_settings
from aegis_ai.settings.models import AEGISSettings
from aegis_ai.settings.validation import validate_settings_change


class SettingsStore:
    """Manages AEGIS settings with JSON persistence and audit logging.

    Settings are persisted to config/settings.json (survives data/ deletion).
    Audit logs are written to data/settings_audit.jsonl.

    Usage:
        store = SettingsStore()
        settings = store.get()
        settings.autonomous.support_agent_enabled = False
        store.update(settings, changed_by="user", reason="Disabled support agent")
    """

    def __init__(
        self,
        path: str = "config/settings.json",
        audit_path: str = "data/settings_audit.jsonl",
    ) -> None:
        self._path = Path(path)
        self._audit_path = Path(audit_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._audit_path.parent.mkdir(parents=True, exist_ok=True)
        self._settings: AEGISSettings = create_default_settings()
        self._lock = threading.Lock()
        self._load()

    def get(self) -> AEGISSettings:
        """Get current settings."""
        with self._lock:
            return self._settings.model_copy(deep=True)

    def update(
        self,
        settings: AEGISSettings,
        changed_by: str = "user",
        reason: str = "",
    ) -> list[str]:
        """Update settings with validation.

        Returns a list of validation errors. Empty list means success.
        """
        errors = validate_settings_change(self._settings, settings)
        if errors:
            return errors

        with self._lock:
            self._settings = settings.model_copy(deep=True)
            self._persist()
            self._audit(changed_by, reason)
            return []

    def update_section(
        self,
        section: str,
        values: dict[str, Any],
        changed_by: str = "user",
        reason: str = "",
    ) -> list[str]:
        """Update a single settings section.

        Returns a list of validation errors.
        """
        current = self.get()
        section_obj = getattr(current, section, None)
        if section_obj is None:
            return [f"Unknown settings section: {section}"]

        # Update fields
        for key, value in values.items():
            if hasattr(section_obj, key):
                setattr(section_obj, key, value)
            else:
                return [f"Unknown field '{key}' in section '{section}'"]

        return self.update(current, changed_by, reason)

    def reset_to_defaults(self, changed_by: str = "user") -> None:
        """Reset all settings to defaults."""
        with self._lock:
            self._settings = create_default_settings()
            self._persist()
            self._audit(changed_by, "Reset to defaults")

    def export_json(self) -> str:
        """Export settings as JSON string."""
        return self.get().model_dump_json(indent=2)

    def import_json(self, json_str: str, changed_by: str = "user") -> list[str]:
        """Import settings from JSON string."""
        try:
            settings = AEGISSettings.model_validate_json(json_str)
            return self.update(settings, changed_by, "Imported from JSON")
        except Exception as e:
            return [f"Invalid settings JSON: {e}"]

    def _persist(self) -> None:
        """Persist settings to disk."""
        with open(self._path, "w", encoding="utf-8") as f:
            f.write(self._settings.model_dump_json(indent=2))

    def _audit(self, changed_by: str, reason: str) -> None:
        """Append audit entry."""
        entry = {
            "timestamp_ms": int(time.time() * 1000),
            "changed_by": changed_by,
            "reason": reason,
            "settings_snapshot": self._settings.model_dump(),
        }
        with open(self._audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _load(self) -> None:
        """Load settings from disk."""
        if not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            self._settings = AEGISSettings.model_validate(data)
        except (json.JSONDecodeError, Exception):
            self._settings = create_default_settings()
