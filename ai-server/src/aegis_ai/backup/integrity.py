"""Integrity — checksum verification and manifest validation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def calculate_checksum(data: str) -> str:
    """Calculate SHA-256 checksum of a string."""
    return hashlib.sha256(data.encode()).hexdigest()


def verify_checksum(data: str, expected_checksum: str) -> bool:
    """Verify data matches expected checksum."""
    return calculate_checksum(data) == expected_checksum


def validate_manifest(manifest_path: str) -> tuple[bool, list[str]]:
    """Validate an export manifest.

    Returns (is_valid, list_of_errors).
    """
    errors: list[str] = []

    path = Path(manifest_path)
    if not path.exists():
        return False, ["Manifest file not found"]

    try:
        with open(path, encoding="utf-8") as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        return False, [f"Invalid manifest JSON: {e}"]

    # Check required fields
    required = ["export_id", "timestamp_ms", "version", "checksum", "contents"]
    for field in required:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    # Check data file exists
    data_path = path.parent / "aegis_data.json"
    if not data_path.exists():
        errors.append("Data file 'aegis_data.json' not found alongside manifest")
    else:
        # Verify checksum
        data_content = data_path.read_text(encoding="utf-8")
        if not verify_checksum(data_content, manifest.get("checksum", "")):
            errors.append("Data checksum mismatch — file may be corrupted")

    return len(errors) == 0, errors


def create_export_manifest(
    export_id: str,
    contents: list[str],
    checksum: str,
    redacted: bool = True,
    entry_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Create an export manifest dict."""
    return {
        "export_id": export_id,
        "timestamp_ms": int(__import__("time").time() * 1000),
        "version": "1.0.0",
        "schema_version": "1.0.0",
        "contents": contents,
        "checksum": checksum,
        "redacted": redacted,
        "entry_counts": entry_counts or {},
    }
