"""A BOM on the override store must not read as corruption.

`CapabilityOverrideStore._load` reads `data/settings/capability_overrides.json` with
`encoding="utf-8"`.  A file that begins with a UTF-8 BOM raised `JSONDecodeError`, which
the handler turns into `corrupted = True` and an **empty** override map -- so a BOM
(a) reported a valid user-policy file as corrupt, and (b) dropped every override,
reverting each capability to its manifest risk level.  The store is reachable in
production: `CapabilityCatalog.__init__` constructs it (`capability_catalog.py:139`),
and its sibling `CapabilityCatalog` already reads capability manifests as `utf-8-sig`.

A BOM is not corruption -- Windows editors add one (Notepad; PowerShell
`Set-Content -Encoding utf8`, which in Windows PowerShell 5.1 writes a BOM).  The fix
reads `utf-8-sig`, a strict superset of `utf-8` for reading.

The same fix covers `endpoint_resolver`'s two JSON readers (`data/neighbors.json` and
the disk cache), which swallowed the same exception into an empty mapping.

The controls are the other half: a BOM-free file must be unchanged, and a genuinely
corrupt file must still report corruption (the fix must not make corruption readable).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from aegis_ai.capability_overrides import CapabilityOverrideStore
from aegis_ai.net.endpoint_resolver import _load_disk_cache, _parse_neighbors_json

_LOGGER = "aegis_ai.capability_overrides"
_BOM = b"\xef\xbb\xbf"

_VALID_OVERRIDES = {
    "overrides": {
        "pc-server.test.sample": {
            "capability_id": "pc-server.test.sample",
            "risk_level": "APPROVAL_REQUIRED",
            "requires_approval": True,
            "enabled": True,
            "updated_by": "user",
        }
    }
}

_DISABLING_OVERRIDES = {
    "overrides": {
        "pc-server.test.sample": {
            "capability_id": "pc-server.test.sample",
            "enabled": False,
            "updated_by": "user",
        }
    }
}


def _write_manifest(root: Path, cap_id: str = "pc-server.test.sample", risk: str = "safe") -> Path:
    path = root / "builtin" / "pc-server" / "test" / f"{cap_id.rsplit('.', 1)[-1]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "id": cap_id,
                "server_id": "pc-server",
                "app_id": "test",
                "action": cap_id.rsplit(".", 1)[-1],
                "operation_category": "test_operation",
                "title": "Sample",
                "description": "Sample capability",
                "risk": {"level": risk, "requires_approval": False},
            }
        ),
        encoding="utf-8",
    )
    return path


def _catalog(tmp_path: Path, overrides_bytes: bytes):
    from aegis_ai.capability_catalog import CapabilityCatalog

    capabilities_dir = tmp_path / "capabilities"
    data_dir = tmp_path / "data"
    _write_manifest(capabilities_dir)
    override_path = data_dir / "settings" / "capability_overrides.json"
    override_path.parent.mkdir(parents=True, exist_ok=True)
    override_path.write_bytes(overrides_bytes)
    return CapabilityCatalog(
        capabilities_dir=str(capabilities_dir),
        apps_dir=str(tmp_path / "apps"),
        data_dir=str(data_dir),
    )


def _store(tmp_path: Path, name: str, payload: bytes) -> CapabilityOverrideStore:
    path = tmp_path / name / "capability_overrides.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return CapabilityOverrideStore(path=str(path))


# --- the fix ---------------------------------------------------------------------------


def test_a_bomd_valid_override_store_is_not_corrupt(tmp_path) -> None:
    """The core pin: a BOM'd valid file is read, not flagged corrupt."""
    catalog = _catalog(tmp_path, _BOM + json.dumps(_VALID_OVERRIDES).encode("utf-8"))
    details = catalog.risk_details("pc-server.test.sample")
    assert details["override_store_corrupted"] is False
    assert details["effective"]["risk_level"] == "approval_required"
    assert details["effective"]["requires_approval"] is True


def test_a_bomd_override_store_matches_the_plain_one(tmp_path) -> None:
    plain = _store(tmp_path, "plain", json.dumps(_VALID_OVERRIDES).encode("utf-8"))
    bomd = _store(tmp_path, "bom", _BOM + json.dumps(_VALID_OVERRIDES).encode("utf-8"))
    assert plain.corrupted is False
    assert bomd.corrupted is False
    assert bomd.list() == plain.list()
    assert bomd.list() != {}


def test_a_bomd_override_store_does_not_warn(tmp_path, caplog) -> None:
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        _store(tmp_path, "bom", _BOM + json.dumps(_VALID_OVERRIDES).encode("utf-8"))
    assert [r for r in caplog.records if r.levelno >= logging.WARNING] == []


def test_a_disabling_override_survives_a_bom(tmp_path) -> None:
    """The consequence that matters: a dropped override loses the user's restriction."""
    catalog = _catalog(tmp_path, _BOM + json.dumps(_DISABLING_OVERRIDES).encode("utf-8"))
    details = catalog.risk_details("pc-server.test.sample")
    assert details["override_store_corrupted"] is False
    assert details["effective"]["enabled"] is False


def test_the_neighbors_reader_tolerates_a_bom(tmp_path) -> None:
    """The same fix covers endpoint_resolver's neighbors reader."""
    payload = {"neighbors": [{"mac": "aa:bb:cc:dd:ee:ff", "ip": "10.0.0.7", "state": "REACHABLE"}]}
    path = tmp_path / "neighbors.json"
    path.write_bytes(_BOM + json.dumps(payload).encode("utf-8"))
    assert _parse_neighbors_json(path) == {"aa:bb:cc:dd:ee:ff": "10.0.0.7"}


def test_the_disk_cache_reader_tolerates_a_bom(tmp_path, monkeypatch) -> None:
    """And endpoint_resolver's disk-cache reader -- the third site of the same fix."""
    payload = {"room-server": {"host": "10.0.0.9", "port": 50052}}
    path = tmp_path / "endpoint_cache.json"
    path.write_bytes(_BOM + json.dumps(payload).encode("utf-8"))
    monkeypatch.setenv("AEGIS_ENDPOINT_CACHE_PATH", str(path))
    assert _load_disk_cache() == payload


# --- controls --------------------------------------------------------------------------


def test_a_bom_free_override_store_is_unchanged(tmp_path) -> None:
    store = _store(tmp_path, "plain", json.dumps(_VALID_OVERRIDES).encode("utf-8"))
    assert store.corrupted is False
    assert list(store.list()) == ["pc-server.test.sample"]


def test_a_genuinely_corrupt_override_store_still_reports_corrupt(tmp_path) -> None:
    """Control: a BOM must not make corruption readable."""
    store = _store(tmp_path, "bad", _BOM + b"{not json")
    assert store.corrupted is True
    assert store.list() == {}


def test_a_bom_only_override_file_still_reports_corrupt(tmp_path) -> None:
    store = _store(tmp_path, "bomonly", _BOM)
    assert store.corrupted is True
    assert store.list() == {}


def test_the_neighbors_reader_still_returns_empty_on_corruption(tmp_path) -> None:
    path = tmp_path / "neighbors.json"
    path.write_bytes(_BOM + b"{not json")
    assert _parse_neighbors_json(path) == {}


def test_the_disk_cache_reader_still_returns_empty_on_corruption(tmp_path, monkeypatch) -> None:
    path = tmp_path / "endpoint_cache.json"
    path.write_bytes(_BOM + b"{not json")
    monkeypatch.setenv("AEGIS_ENDPOINT_CACHE_PATH", str(path))
    assert _load_disk_cache() == {}
