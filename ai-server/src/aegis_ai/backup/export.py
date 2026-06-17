"""Export — exports AEGIS data to JSON files.

Supports:
- Full export (all data)
- Settings only
- Memory only (episodic, semantic, procedural, reflection)
- Audit only
- Redacted export (default — secrets stripped)
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.backup.scrub import scrub_dict


@dataclass
class ExportManifest:
    """Manifest for an export bundle."""
    export_id: str = ""
    timestamp_ms: int = 0
    version: str = "1.0.0"
    schema_version: str = "1.0.0"
    contents: list[str] = field(default_factory=list)
    checksum: str = ""
    redacted: bool = True
    entry_counts: dict[str, int] = field(default_factory=dict)


class DataExporter:
    """Exports AEGIS data to JSON bundles.

    Usage:
        exporter = DataExporter(
            settings_store=settings_store,
            audit_log=audit_log,
            episodic_memory=episodic,
            semantic_memory=semantic,
        )
        manifest = exporter.export_all("data/backups/", redacted=True)
    """

    def __init__(
        self,
        settings_store: Any = None,
        audit_log: Any = None,
        episodic_memory: Any = None,
        semantic_memory: Any = None,
        procedural_memory: Any = None,
        reflection_log: Any = None,
    ) -> None:
        self._settings = settings_store
        self._audit = audit_log
        self._episodic = episodic_memory
        self._semantic = semantic_memory
        self._procedural = procedural_memory
        self._reflection = reflection_log

    def export_all(
        self,
        output_dir: str,
        redacted: bool = True,
    ) -> ExportManifest:
        """Export all data to a directory.

        Args:
            output_dir: Directory to write export files.
            redacted: If True, scrub secrets from export (default).

        Returns:
            ExportManifest with checksums and metadata.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        manifest = ExportManifest(
            export_id=f"export_{int(time.time() * 1000)}",
            timestamp_ms=int(time.time() * 1000),
            redacted=redacted,
        )

        # Export each component
        data: dict[str, Any] = {}

        if self._settings:
            settings_data = json.loads(self._settings.export_json())
            if redacted:
                settings_data = scrub_dict(settings_data)
            data["settings"] = settings_data
            manifest.contents.append("settings")

        if self._audit:
            if hasattr(self._audit, 'read_all_for_export'):
                audit_data = self._audit.read_all_for_export()
            else:
                audit_data = []
            if redacted:
                audit_data = [scrub_dict(entry) for entry in audit_data]
            data["audit"] = audit_data
            manifest.contents.append("audit")
            manifest.entry_counts["audit"] = len(audit_data)

        if self._episodic:
            episodes = self._episodic.list_recent(10000)
            episode_data = [
                {
                    "episode_id": e.episode_id,
                    "summary": e.summary,
                    "category": e.category,
                    "events": e.events,
                    "detail": e.detail,
                    "timestamp_ms": e.timestamp_ms,
                }
                for e in episodes
            ]
            if redacted:
                episode_data = [scrub_dict(e) for e in episode_data]
            data["episodic"] = episode_data
            manifest.contents.append("episodic")
            manifest.entry_counts["episodic"] = len(episode_data)

        if self._semantic:
            facts = list(self._semantic._facts.values()) if hasattr(self._semantic, '_facts') else []
            fact_data = [
                {
                    "fact_id": f.fact_id,
                    "content": f.content,
                    "category": f.category,
                    "source": f.source,
                    "confidence": f.confidence,
                    "tags": f.tags,
                    "timestamp_ms": f.timestamp_ms,
                }
                for f in facts
            ]
            if redacted:
                fact_data = [scrub_dict(f) for f in fact_data]
            data["semantic"] = fact_data
            manifest.contents.append("semantic")
            manifest.entry_counts["semantic"] = len(fact_data)

        if self._procedural:
            procs = self._procedural.list_recent(10000)
            proc_data = [
                {
                    "procedure_id": p.procedure_id,
                    "goal": p.goal,
                    "steps": p.steps,
                    "confidence": p.confidence,
                    "success_count": p.success_count,
                    "failure_count": p.failure_count,
                }
                for p in procs
            ]
            data["procedural"] = proc_data
            manifest.contents.append("procedural")
            manifest.entry_counts["procedural"] = len(proc_data)

        if self._reflection:
            refs = self._reflection.list_recent(10000)
            ref_data = [
                {
                    "reflection_id": r.reflection_id,
                    "summary": r.summary,
                    "what_worked": r.what_worked,
                    "what_failed": r.what_failed,
                    "improvement_ideas": r.improvement_ideas,
                    "timestamp_ms": r.timestamp_ms,
                }
                for r in refs
            ]
            data["reflection"] = ref_data
            manifest.contents.append("reflection")
            manifest.entry_counts["reflection"] = len(ref_data)

        # Write data file
        data_path = output_path / "aegis_data.json"
        data_json = json.dumps(data, ensure_ascii=False, indent=2)
        data_path.write_text(data_json, encoding="utf-8")

        # Calculate checksum
        manifest.checksum = hashlib.sha256(data_json.encode()).hexdigest()

        # Write manifest
        manifest_path = output_path / "manifest.json"
        manifest_json = json.dumps(manifest.__dict__, ensure_ascii=False, indent=2)
        manifest_path.write_text(manifest_json, encoding="utf-8")

        return manifest

    def export_settings_only(self, output_path: str, redacted: bool = True) -> str:
        """Export settings only."""
        if not self._settings:
            return ""
        data = json.loads(self._settings.export_json())
        if redacted:
            data = scrub_dict(data)
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        Path(output_path).write_text(json_str, encoding="utf-8")
        return json_str

    def export_memory_only(self, output_path: str, redacted: bool = True) -> str:
        """Export all memory types."""
        data: dict[str, Any] = {}

        if self._episodic:
            episodes = self._episodic.list_recent(10000)
            data["episodic"] = [
                {"episode_id": e.episode_id, "summary": e.summary,
                 "category": e.category, "timestamp_ms": e.timestamp_ms}
                for e in episodes
            ]

        if self._semantic:
            facts = list(self._semantic._facts.values()) if hasattr(self._semantic, '_facts') else []
            data["semantic"] = [{"fact_id": f.fact_id, "content": f.content, "category": f.category} for f in facts]

        if self._procedural:
            procs = self._procedural.list_recent(10000)
            data["procedural"] = [{"procedure_id": p.procedure_id, "goal": p.goal, "steps": p.steps} for p in procs]

        if self._reflection:
            refs = self._reflection.list_recent(10000)
            data["reflection"] = [{"reflection_id": r.reflection_id, "summary": r.summary} for r in refs]

        if redacted:
            data = scrub_dict(data)

        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        Path(output_path).write_text(json_str, encoding="utf-8")
        return json_str

    def export_audit_only(self, output_path: str, redacted: bool = True) -> str:
        """Export audit log only."""
        if not self._audit:
            return ""
        if hasattr(self._audit, 'read_all_for_export'):
            data = self._audit.read_all_for_export()
        else:
            data = []
        if redacted:
            data = [scrub_dict(entry) for entry in data]
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        Path(output_path).write_text(json_str, encoding="utf-8")
        return json_str
