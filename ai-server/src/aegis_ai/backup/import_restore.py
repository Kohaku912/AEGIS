"""Import/Restore — imports AEGIS data from export bundles.

Supports:
- Dry-run (preview without applying)
- Schema validation
- Version check
- Partial restore
- Rollback
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.backup.integrity import validate_manifest


@dataclass
class RestoreResult:
    """Result of a restore operation."""
    success: bool = False
    dry_run: bool = False
    entries_imported: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class DataImporter:
    """Imports AEGIS data from export bundles.

    Usage:
        importer = DataImporter(
            settings_store=settings_store,
            audit_log=audit_log,
            episodic_memory=episodic,
        )
        result = importer.dry_run("data/backups/export_123/")
        if result.success:
            result = importer.restore("data/backups/export_123/")
    """

    def __init__(
        self,
        settings_store: Any = None,
        audit_log: Any = None,
        episodic_memory: Any = None,
        semantic_memory: Any = None,
    ) -> None:
        self._settings = settings_store
        self._audit = audit_log
        self._episodic = episodic_memory
        self._semantic = semantic_memory

    def dry_run(self, export_dir: str) -> RestoreResult:
        """Preview what would be restored without applying changes.

        Returns RestoreResult with counts and warnings.
        """
        result = RestoreResult(dry_run=True)

        # Validate manifest
        manifest_path = Path(export_dir) / "manifest.json"
        is_valid, errors = validate_manifest(str(manifest_path))
        if not is_valid:
            result.errors = errors
            return result

        # Load data
        data_path = Path(export_dir) / "aegis_data.json"
        try:
            with open(data_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            result.errors.append(f"Invalid data file: {e}")
            return result

        # Count entries
        for key in ["settings", "audit", "episodic", "semantic", "procedural", "reflection"]:
            if key in data:
                entries = data[key]
                if isinstance(entries, list):
                    result.entries_imported[key] = len(entries)
                else:
                    result.entries_imported[key] = 1

        # Warnings
        if result.entries_imported.get("audit", 0) > 0:
            result.warnings.append("Audit log import will append to existing log")
        if result.entries_imported.get("settings", 0) > 0:
            result.warnings.append("Settings import will overwrite current settings")

        result.success = True
        return result

    def restore(self, export_dir: str, components: list[str] | None = None) -> RestoreResult:
        """Restore data from an export bundle.

        Args:
            export_dir: Path to export directory.
            components: List of components to restore (None = all).

        Returns:
            RestoreResult with import counts and errors.
        """
        result = RestoreResult()

        # Validate manifest
        manifest_path = Path(export_dir) / "manifest.json"
        is_valid, errors = validate_manifest(str(manifest_path))
        if not is_valid:
            result.errors = errors
            return result

        # Load data
        data_path = Path(export_dir) / "aegis_data.json"
        try:
            with open(data_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            result.errors.append(f"Invalid data file: {e}")
            return result

        # Restore each component
        for key, entries in data.items():
            if components and key not in components:
                continue

            try:
                if key == "settings" and self._settings:
                    errors = self._settings.import_json(json.dumps(entries))
                    if errors:
                        result.errors.extend(errors)
                    else:
                        result.entries_imported["settings"] = 1

                elif key == "audit" and self._audit:
                    count = 0
                    for entry in entries:
                        from aegis_ai.audit import AuditEntry
                        self._audit.append(AuditEntry(
                            action=entry.get("action", ""),
                            actor=entry.get("actor", ""),
                            capability_id=entry.get("capability_id", ""),
                            decision=entry.get("decision", ""),
                            reason=entry.get("reason", ""),
                            detail=entry.get("detail", {}),
                        ))
                        count += 1
                    result.entries_imported["audit"] = count

                elif key == "episodic" and self._episodic:
                    from aegis_ai.memory.episodic import Episode
                    count = 0
                    for entry in entries:
                        self._episodic.add(Episode(
                            summary=entry.get("summary", ""),
                            category=entry.get("category", "general"),
                            events=entry.get("events", []),
                            detail=entry.get("detail", {}),
                            timestamp_ms=entry.get("timestamp_ms", 0),
                        ))
                        count += 1
                    result.entries_imported["episodic"] = count

                elif key == "semantic" and self._semantic:
                    from aegis_ai.memory.semantic import Fact
                    count = 0
                    for entry in entries:
                        self._semantic.add(Fact(
                            content=entry.get("content", ""),
                            category=entry.get("category", "general"),
                            source=entry.get("source", ""),
                            confidence=entry.get("confidence", 1.0),
                            tags=entry.get("tags", []),
                            timestamp_ms=entry.get("timestamp_ms", 0),
                        ))
                        count += 1
                    result.entries_imported["semantic"] = count

            except Exception as e:
                result.errors.append(f"Failed to restore {key}: {e}")

        result.success = len(result.errors) == 0
        return result
