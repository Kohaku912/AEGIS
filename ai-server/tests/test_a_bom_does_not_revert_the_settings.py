"""A BOM on settings.json must not revert the shipped configuration.

`SettingsStore._load` reads `config/settings.json`, and on any failure it substitutes
the built-in defaults -- which differ from the shipped config in exactly three egress
keys.  The read used `encoding="utf-8"`, so a file that begins with a UTF-8 BOM raised
`JSONDecodeError` and the *shipped configuration stopped being in effect*: the egress
allowlist emptied and both egress booleans flipped to False.

A BOM is not corruption.  Windows editors add one (Notepad, and PowerShell
`Set-Content -Encoding utf8`, which in Windows PowerShell 5.1 writes a BOM), and the
same repository already reads capability manifests as `utf-8-sig`
(`capability_catalog.py`, `folder_registry.py`).  `utf-8-sig` strips a leading BOM if
present and is otherwise identical to `utf-8`, so a BOM-free file is unaffected.

The fix is on the egress path, so the change is recorded rather than assumed to be
inert: a BOM'd settings.json previously denied every external destination, and now the
declared allowlist applies.  That is the user's own declared permission taking effect,
not a widening -- but it is a behaviour change and is pinned as one.

The controls are the other half: a BOM-free file must be unchanged, and a genuinely
corrupt file must still fall back (the fix must not make corruption readable).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from aegis_ai.settings.defaults import create_default_settings
from aegis_ai.settings.store import SettingsStore

_LOGGER = "aegis_ai.settings.store"
_AI_SERVER = Path(__file__).resolve().parents[1]
_SHIPPED_CONFIG = _AI_SERVER / "config" / "settings.json"

_BOM = b"\xef\xbb\xbf"
_EGRESS_KEYS = [
    ("privacy", "egress_allowed_hosts"),
    ("privacy", "external_egress_allowed"),
    ("privacy", "external_llm_allowed"),
]


def _store(path: Path) -> SettingsStore:
    return SettingsStore(path=str(path), audit_path=str(path.parent / "settings_audit.jsonl"))


def _egress(store: SettingsStore) -> dict[str, object]:
    dumped = store.get().model_dump()
    return {
        f"{section}.{key}": dumped.get(section, {}).get(key) for section, key in _EGRESS_KEYS
    }


def _shipped_egress() -> dict[str, object]:
    dumped = json.loads(_SHIPPED_CONFIG.read_text(encoding="utf-8"))
    return {
        f"{section}.{key}": dumped.get(section, {}).get(key) for section, key in _EGRESS_KEYS
    }


def _warnings(caplog) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == _LOGGER and r.levelno >= logging.WARNING]


# --- the fix ---------------------------------------------------------------------------


def test_a_bomd_settings_file_is_read_not_reverted(tmp_path, caplog) -> None:
    """The core pin: a BOM'd shipped config must take effect, not fall back."""
    path = tmp_path / "settings.json"
    path.write_bytes(_BOM + _SHIPPED_CONFIG.read_bytes())
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        store = _store(path)
    assert _egress(store) == _shipped_egress()
    assert _egress(store) != _egress(_default_store(tmp_path))
    assert _warnings(caplog) == []


def test_a_bomd_config_matches_the_plain_config_exactly(tmp_path) -> None:
    """Not just egress: every section of a BOM'd file matches the BOM-free file."""
    plain = tmp_path / "plain" / "settings.json"
    bomd = tmp_path / "bomd" / "settings.json"
    plain.parent.mkdir(parents=True)
    bomd.parent.mkdir(parents=True)
    plain.write_bytes(_SHIPPED_CONFIG.read_bytes())
    bomd.write_bytes(_BOM + _SHIPPED_CONFIG.read_bytes())
    assert _store(bomd).get().model_dump() == _store(plain).get().model_dump()


def test_a_bomd_settings_file_does_not_warn(tmp_path, caplog) -> None:
    """No warning means no fallback -- the BOM is read, not reported as a failure."""
    path = tmp_path / "settings.json"
    path.write_bytes(_BOM + _SHIPPED_CONFIG.read_bytes())
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        _store(path)
    assert _warnings(caplog) == []


# --- controls --------------------------------------------------------------------------


def test_a_bom_free_settings_file_is_unchanged(tmp_path, caplog) -> None:
    """Control: the fix must not alter a file that has no BOM."""
    path = tmp_path / "settings.json"
    path.write_bytes(_SHIPPED_CONFIG.read_bytes())
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        store = _store(path)
    assert _egress(store) == _shipped_egress()
    assert _warnings(caplog) == []


def test_a_genuinely_corrupt_file_still_falls_back(tmp_path, caplog) -> None:
    """Control: a BOM must not make corruption readable -- the fallback stays."""
    path = tmp_path / "settings.json"
    path.write_bytes(_BOM + b"{not json")
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        store = _store(path)
    assert _egress(store) == _egress(_default_store(tmp_path))
    assert len(_warnings(caplog)) == 1


def test_a_truncated_bom_only_file_still_falls_back(tmp_path, caplog) -> None:
    """Control: a file that is *only* a BOM is empty, not valid JSON."""
    path = tmp_path / "settings.json"
    path.write_bytes(_BOM)
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        store = _store(path)
    assert _egress(store) == _egress(_default_store(tmp_path))
    assert len(_warnings(caplog)) == 1


# --- the writer side -------------------------------------------------------------------


def test_the_store_writes_no_bom(tmp_path) -> None:
    """The reader tolerates a BOM; our own writer must not emit one."""
    path = tmp_path / "settings.json"
    store = _store(path)
    store.update(store.get(), changed_by="test", reason="pin the writer")
    written = path.read_bytes()
    assert written[:3] != _BOM
    assert written.lstrip().startswith(b"{")


# --- helpers ---------------------------------------------------------------------------


def _default_store(tmp_path: Path) -> SettingsStore:
    """A store with no file on disk -- the built-in defaults, the fail-closed baseline."""
    return _store(tmp_path / "absent.json")
