"""Validate all capability manifests against Pydantic boundary models."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aegis_ai.folder_registry import FolderCapabilityRegistry


def _capabilities_root() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "capabilities"


def test_all_builtin_manifests_load_without_registry_errors() -> None:
    root = _capabilities_root()
    registry = FolderCapabilityRegistry(str(root))
    errors = registry.errors()
    assert not errors, f"manifest load errors: {errors[:5]}"
    manifests = registry.list_all(origin="builtin")
    assert manifests, "expected builtin capability manifests"


def test_manifest_input_schema_is_object_when_present() -> None:
    root = _capabilities_root()
    for path in root.rglob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        schema = data.get("input_schema") or data.get("input") or {}
        if schema:
            assert schema.get("type") in {"object", None}, f"{path} input schema must be object"
