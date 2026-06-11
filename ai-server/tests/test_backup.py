"""Tests for Backup — export, import, restore, retention, scrub."""

from __future__ import annotations

import json
import os
import tempfile
import time

from aegis_ai.audit import AuditLog
from aegis_ai.backup.export import DataExporter
from aegis_ai.backup.import_restore import DataImporter
from aegis_ai.backup.integrity import calculate_checksum, validate_manifest, verify_checksum
from aegis_ai.backup.retention import RetentionManager
from aegis_ai.backup.scrub import scrub_dict, scrub_text
from aegis_ai.memory.episodic import Episode, EpisodicMemory
from aegis_ai.memory.semantic import Fact, SemanticMemory
from aegis_ai.settings.store import SettingsStore
from approval import ApprovalStore

# ── Helpers ──────────────────────────────────────────────────


def _tmpdir() -> str:
    """Create a temporary directory."""
    d = tempfile.mkdtemp(prefix="aegis_backup_test_")
    return d


def _make_settings(tmpdir: str, name: str = "settings") -> SettingsStore:
    """Create a SettingsStore with unique paths."""
    return SettingsStore(
        path=os.path.join(tmpdir, f"{name}.json"),
        audit_path=os.path.join(tmpdir, f"{name}_audit.jsonl"),
    )


def _make_episodic(path: str) -> EpisodicMemory:
    """Create episodic memory with test data."""
    mem = EpisodicMemory(path=path)
    mem.add(Episode(summary="Test episode 1", category="event", timestamp_ms=int(time.time() * 1000)))
    mem.add(Episode(summary="Test episode 2", category="action_result", timestamp_ms=int(time.time() * 1000)))
    return mem


def _make_semantic(path: str) -> SemanticMemory:
    """Create semantic memory with test data."""
    mem = SemanticMemory(path=path)
    mem.add(Fact(content="User prefers dark mode", category="preference", source="user"))
    mem.add(Fact(content="Project uses Python 3.12", category="knowledge", source="inference"))
    return mem


# ═══════════════════════════════════════════════════════════════
# 1. Scrub
# ═══════════════════════════════════════════════════════════════


class TestScrub:
    """Scrub removes sensitive data."""

    def test_scrub_password(self):
        """Password is scrubbed."""
        result = scrub_text("password: mysecret123")
        assert "mysecret123" not in result

    def test_scrub_email(self):
        """Email is scrubbed."""
        result = scrub_text("Contact test@example.com")
        assert "test@example.com" not in result
        assert "[EMAIL_REDACTED]" in result

    def test_scrub_ssh_key(self):
        """SSH key is scrubbed."""
        result = scrub_text("-----BEGIN RSA PRIVATE KEY-----\nMIIEow...\n-----END RSA PRIVATE KEY-----")
        assert "RSA PRIVATE KEY" not in result
        assert "[SSH_KEY_REDACTED]" in result

    def test_scrub_dict_password_key(self):
        """Dict with password key is scrubbed."""
        data = {"username": "admin", "password": "secret123"}
        result = scrub_dict(data)
        assert result["password"] == "[REDACTED]"
        assert result["username"] == "admin"

    def test_scrub_dict_nested(self):
        """Nested dict is scrubbed."""
        data = {"config": {"api_key": "sk-abc123"}}
        result = scrub_dict(data)
        assert result["config"]["api_key"] == "[REDACTED]"

    def test_scrub_preserves_safe_data(self):
        """Safe data is preserved."""
        data = {"name": "AEGIS", "version": "1.0.0"}
        result = scrub_dict(data)
        assert result["name"] == "AEGIS"
        assert result["version"] == "1.0.0"


# ═══════════════════════════════════════════════════════════════
# 2. Integrity
# ═══════════════════════════════════════════════════════════════


class TestIntegrity:
    """Integrity checks verify data correctness."""

    def test_checksum_deterministic(self):
        """Same data produces same checksum."""
        c1 = calculate_checksum("hello world")
        c2 = calculate_checksum("hello world")
        assert c1 == c2

    def test_checksum_different_data(self):
        """Different data produces different checksum."""
        c1 = calculate_checksum("hello")
        c2 = calculate_checksum("world")
        assert c1 != c2

    def test_verify_checksum_valid(self):
        """Valid checksum passes verification."""
        data = "test data"
        checksum = calculate_checksum(data)
        assert verify_checksum(data, checksum) is True

    def test_verify_checksum_invalid(self):
        """Invalid checksum fails verification."""
        assert verify_checksum("test data", "wrong_checksum") is False

    def test_validate_manifest_valid(self):
        """Valid manifest passes validation."""
        tmpdir = _tmpdir()
        data = '{"test": true}'
        checksum = calculate_checksum(data)

        manifest = {
            "export_id": "test",
            "timestamp_ms": int(time.time() * 1000),
            "version": "1.0.0",
            "checksum": checksum,
            "contents": ["settings"],
        }
        manifest_path = os.path.join(tmpdir, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        data_path = os.path.join(tmpdir, "aegis_data.json")
        with open(data_path, "w") as f:
            f.write(data)

        is_valid, errors = validate_manifest(manifest_path)
        assert is_valid is True
        assert errors == []

    def test_validate_manifest_missing_checksum(self):
        """Manifest with missing checksum fails."""
        tmpdir = _tmpdir()
        manifest = {"export_id": "test"}
        manifest_path = os.path.join(tmpdir, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        is_valid, errors = validate_manifest(manifest_path)
        assert is_valid is False
        assert len(errors) >= 1


# ═══════════════════════════════════════════════════════════════
# 3. Export
# ═══════════════════════════════════════════════════════════════


class TestExport:
    """Export creates valid backup bundles."""

    def test_export_all(self):
        """Full export creates manifest and data files."""
        tmpdir = _tmpdir()
        settings = _make_settings(tmpdir)
        audit = AuditLog(path=os.path.join(tmpdir, "audit.jsonl"))
        episodic = _make_episodic(os.path.join(tmpdir, "episodic.jsonl"))
        semantic = _make_semantic(os.path.join(tmpdir, "semantic.jsonl"))

        exporter = DataExporter(
            settings_store=settings,
            audit_log=audit,
            episodic_memory=episodic,
            semantic_memory=semantic,
        )

        out_dir = os.path.join(tmpdir, "export")
        manifest = exporter.export_all(out_dir, redacted=True)

        assert manifest.export_id != ""
        assert manifest.checksum != ""
        assert "settings" in manifest.contents
        assert "episodic" in manifest.contents
        assert manifest.redacted is True

        # Files exist
        assert os.path.exists(os.path.join(out_dir, "manifest.json"))
        assert os.path.exists(os.path.join(out_dir, "aegis_data.json"))

    def test_export_redacted(self):
        """Redacted export scrubs secrets."""
        tmpdir = _tmpdir()
        settings = _make_settings(tmpdir)

        exporter = DataExporter(settings_store=settings)
        out_dir = os.path.join(tmpdir, "export_redacted")
        exporter.export_all(out_dir, redacted=True)

        data_path = os.path.join(out_dir, "aegis_data.json")
        with open(data_path) as f:
            data = json.load(f)
        # Settings should be present but scrubbed
        assert "settings" in data

    def test_export_settings_only(self):
        """Settings-only export works."""
        tmpdir = _tmpdir()
        settings = _make_settings(tmpdir)

        exporter = DataExporter(settings_store=settings)
        out_path = os.path.join(tmpdir, "settings_export.json")
        result = exporter.export_settings_only(out_path, redacted=True)

        assert result != ""
        assert os.path.exists(out_path)

    def test_export_memory_only(self):
        """Memory-only export works."""
        tmpdir = _tmpdir()
        episodic = _make_episodic(os.path.join(tmpdir, "episodic.jsonl"))

        exporter = DataExporter(episodic_memory=episodic)
        out_path = os.path.join(tmpdir, "memory_export.json")
        result = exporter.export_memory_only(out_path, redacted=True)

        assert result != ""
        data = json.loads(result)
        assert "episodic" in data


# ═══════════════════════════════════════════════════════════════
# 4. Import/Restore
# ═══════════════════════════════════════════════════════════════


class TestImportRestore:
    """Import/restore from export bundles."""

    def test_dry_run(self):
        """Dry run previews without applying."""
        tmpdir = _tmpdir()
        settings = _make_settings(tmpdir)
        episodic = _make_episodic(os.path.join(tmpdir, "episodic.jsonl"))

        exporter = DataExporter(settings_store=settings, episodic_memory=episodic)
        export_dir = os.path.join(tmpdir, "export")
        exporter.export_all(export_dir, redacted=True)

        importer = DataImporter(settings_store=settings, episodic_memory=episodic)
        result = importer.dry_run(export_dir)

        assert result.success is True
        assert result.dry_run is True
        assert result.entries_imported.get("episodic", 0) >= 2

    def test_restore_settings(self):
        """Settings restore works."""
        tmpdir = _tmpdir()
        settings1 = _make_settings(tmpdir, "s1")
        settings1.update_section("autonomous", {"support_agent_enabled": False}, changed_by="test")

        exporter = DataExporter(settings_store=settings1)
        export_dir = os.path.join(tmpdir, "export")
        exporter.export_all(export_dir, redacted=False)

        settings2 = _make_settings(tmpdir, "s2")
        importer = DataImporter(settings_store=settings2)
        result = importer.restore(export_dir, components=["settings"])

        assert result.success is True
        assert result.entries_imported.get("settings", 0) == 1

    def test_restore_episodic(self):
        """Episodic memory restore works."""
        tmpdir = _tmpdir()
        episodic1 = _make_episodic(os.path.join(tmpdir, "ep1.jsonl"))

        exporter = DataExporter(episodic_memory=episodic1)
        export_dir = os.path.join(tmpdir, "export")
        exporter.export_all(export_dir, redacted=False)

        episodic2 = EpisodicMemory(path=os.path.join(tmpdir, "ep2.jsonl"))
        importer = DataImporter(episodic_memory=episodic2)
        result = importer.restore(export_dir, components=["episodic"])

        assert result.success is True
        assert result.entries_imported.get("episodic", 0) >= 2

    def test_corrupted_backup_rejected(self):
        """Corrupted backup is rejected."""
        tmpdir = _tmpdir()

        # Create corrupted export
        manifest = {"export_id": "test", "checksum": "wrong"}
        manifest_path = os.path.join(tmpdir, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        data_path = os.path.join(tmpdir, "aegis_data.json")
        with open(data_path, "w") as f:
            f.write('{"test": true}')

        importer = DataImporter()
        result = importer.restore(tmpdir)
        assert result.success is False
        assert len(result.errors) >= 1


# ═══════════════════════════════════════════════════════════════
# 5. Retention
# ═══════════════════════════════════════════════════════════════


class TestRetention:
    """Retention manager handles data lifecycle."""

    def test_cleanup_expired_approvals(self):
        """Expired approvals are cleaned up."""
        approval_store = ApprovalStore(request_timeout_ms=1)
        approval_store.create_request(capability_id="test.cap")
        time.sleep(0.01)

        manager = RetentionManager(approval_store=approval_store)
        cleaned = manager.cleanup_expired()
        assert cleaned["expired_approvals"] >= 1

    def test_retention_status(self):
        """Retention status returns settings."""
        tmpdir = _tmpdir()
        settings = _make_settings(tmpdir)

        manager = RetentionManager(settings_store=settings)
        status = manager.get_retention_status()
        assert "episodic_retention_days" in status
