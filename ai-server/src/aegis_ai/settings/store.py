"""Settings Store — JSON-based persistence for AEGIS settings.

Thread-safe, with audit logging for all changes.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from aegis_ai.settings.defaults import create_default_settings
from aegis_ai.settings.models import AEGISSettings
from aegis_ai.settings.validation import validate_settings_change

logger = logging.getLogger("aegis_ai.settings.store")


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

        The proposal is built by **construction**, not by assignment: the schema's
        ``ge``/``le`` bounds bind at construction, and pydantic does not validate
        assignment (no model here sets ``validate_assignment``). An earlier version
        ``setattr``-ed onto the loaded object, which made **26 of the 27** declared
        bounds exceedable through this API with the value persisted to disk — including
        the retention caps, which ``backup/retention.py`` turns into the prune cutoff.
        Recorded as B-20 / register A-9; pinned by
        ``tests/test_settings_edit_path_enforces_schema_bounds.py``.

        The alternative repair — re-checking every bound inside
        ``validate_settings_change`` — is deliberately rejected: it would place a second
        copy of the schema in the write path, which is the duplication this repo keeps
        finding. Constructing means there is exactly one definition of each bound.
        """
        current = self.get()
        section_obj = getattr(current, section, None)
        if not isinstance(section_obj, BaseModel):
            return [f"Unknown settings section: {section}"]

        unknown = [key for key in values if key not in type(section_obj).model_fields]
        if unknown:
            return [f"Unknown field '{unknown[0]}' in section '{section}'"]

        merged = current.model_dump()
        merged[section] = {**merged[section], **values}
        try:
            proposed = AEGISSettings.model_validate(merged)
        except ValidationError as exc:
            return [
                f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
                for error in exc.errors()
            ]

        return self.update(proposed, changed_by, reason)

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
        """Import settings from JSON string.

        The two failure modes are reported separately: the parse, and the *apply*
        (``update`` validates, persists and audits). A single ``try`` around both made
        a disk failure read as ``Invalid settings JSON`` — the same fixed-message shape
        as ``llm.first_stage.*.failed``, sending the reader to the wrong artefact.
        """
        try:
            settings = AEGISSettings.model_validate_json(json_str)
        except Exception as exc:
            return [f"Invalid settings JSON: {exc}"]
        try:
            return self.update(settings, changed_by, "Imported from JSON")
        except Exception as exc:
            return [f"Could not apply imported settings: {type(exc).__name__}: {exc}"]

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
        except Exception as exc:
            # Named rather than swallowed. The fallback is fail-closed: the built-in
            # defaults differ from the shipped config in exactly three keys, all of
            # them egress permissions (measured 2026-10-04 — `egress_allowed_hosts`
            # [] vs ['api.typesafe.ai'], `external_egress_allowed` and
            # `external_llm_allowed` False vs True), so nothing is opened up. But the
            # gate then denies every external destination, and without this line the
            # only evidence is the degradation itself.
            logger.warning(
                "Could not read settings from %s (%s: %s); falling back to the built-in "
                "defaults, so the shipped configuration is not in effect. The defaults "
                "empty `privacy.egress_allowed_hosts` and set `external_egress_allowed` "
                "and `external_llm_allowed` to False, so the egress gate will deny every "
                "external destination and cloud LLM profiles will degrade.",
                self._path,
                type(exc).__name__,
                exc,
            )
            self._settings = create_default_settings()
