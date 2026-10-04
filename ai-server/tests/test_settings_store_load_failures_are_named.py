"""The settings store's failure paths must say what happened.

`SettingsStore._load` runs once from `__init__` and, on any failure, silently
substitutes the built-in defaults — so the shipped configuration stops being in
effect with no signal at all.  `import_json` had the mirror problem: a single `try`
around both the parse and the apply meant a *disk* failure was reported as
`Invalid settings JSON`, sending the reader to the wrong artefact (the same
fixed-message shape as `llm.first_stage.*.failed`).

Both are now named.  The controls are the other half — a missing settings file, a
valid one, a real parse error, and a successful import must each keep their own
message, or the assertions are vacuous.

The warning's wording is itself a claim, so it is pinned: the built-in defaults
differ from the shipped config in exactly three keys, all egress permissions, and
the fallback is therefore *fail-closed* — nothing is opened up, but every external
destination is denied and cloud LLM profiles degrade.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from aegis_ai.settings.defaults import create_default_settings
from aegis_ai.settings.models import AEGISSettings
from aegis_ai.settings.store import SettingsStore

_LOGGER = "aegis_ai.settings.store"
_AI_SERVER = Path(__file__).resolve().parents[1]
_SHIPPED_CONFIG = _AI_SERVER / "config" / "settings.json"

_EGRESS_KEYS = [
    "privacy.egress_allowed_hosts",
    "privacy.external_egress_allowed",
    "privacy.external_llm_allowed",
]


def _warnings(caplog) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == _LOGGER and r.levelno >= logging.WARNING]


def _store(tmp_path) -> SettingsStore:
    return SettingsStore(
        path=str(tmp_path / "settings.json"),
        audit_path=str(tmp_path / "settings_audit.jsonl"),
    )


def _shipped() -> AEGISSettings:
    return AEGISSettings.model_validate(json.loads(_SHIPPED_CONFIG.read_text(encoding="utf-8")))


def _differing_paths(a, b, prefix: str = "") -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out: list[str] = []
        for key in sorted(set(a) | set(b)):
            out += _differing_paths(a.get(key), b.get(key), f"{prefix}.{key}" if prefix else key)
        return out
    return [] if a == b else [prefix]


# --------------------------------------------------------------------------- #
# _load — the silent revert to defaults
# --------------------------------------------------------------------------- #


def test_a_corrupt_settings_file_is_named(tmp_path, caplog) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{not json", encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        store = SettingsStore(path=str(path), audit_path=str(tmp_path / "audit.jsonl"))

    assert store.get() == create_default_settings(), "a corrupt file should fall back to defaults"
    records = _warnings(caplog)
    assert records, "a corrupt settings file reverted to the defaults without a word"
    message = records[0].getMessage()
    assert "settings.json" in message, f"the failing path was not named: {message!r}"
    assert "defaults" in message, f"the fallback was not named: {message!r}"


def test_an_unreadable_settings_file_is_named(tmp_path, caplog) -> None:
    """The other failure mode: the path exists but cannot be opened."""
    (tmp_path / "settings.json").mkdir()

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        store = SettingsStore(
            path=str(tmp_path / "settings.json"), audit_path=str(tmp_path / "audit.jsonl")
        )

    assert store.get() == create_default_settings()
    assert _warnings(caplog), "an unreadable settings file reverted to defaults without a word"


def test_a_missing_settings_file_stays_silent(tmp_path, caplog) -> None:
    """Control: no settings file yet is the ordinary case, not a failure."""
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        store = _store(tmp_path)

    assert store.get() == create_default_settings()
    assert _warnings(caplog) == [], "a first run with no settings file was reported as a failure"


def test_a_valid_settings_file_stays_silent(tmp_path, caplog) -> None:
    """Control: the load path runs and reports nothing when it succeeds."""
    path = tmp_path / "settings.json"
    path.write_text(_SHIPPED_CONFIG.read_text(encoding="utf-8"), encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        store = SettingsStore(path=str(path), audit_path=str(tmp_path / "audit.jsonl"))

    assert _warnings(caplog) == []
    assert store.get() == _shipped(), "the shipped config should have loaded verbatim"


def test_the_defaults_differ_from_the_shipped_config_only_in_egress_permissions() -> None:
    """Pins the claim the warning makes: the fallback is fail-closed, not open."""
    defaults = create_default_settings().model_dump()
    shipped = _shipped().model_dump()

    assert _differing_paths(defaults, shipped) == _EGRESS_KEYS
    # ... and the direction: the defaults are the *narrower* side.
    assert defaults["privacy"]["egress_allowed_hosts"] == []
    assert defaults["privacy"]["external_egress_allowed"] is False
    assert defaults["privacy"]["external_llm_allowed"] is False
    assert shipped["privacy"]["egress_allowed_hosts"], "the shipped allowlist must not be empty"


# --------------------------------------------------------------------------- #
# import_json — two failure modes, two messages
# --------------------------------------------------------------------------- #


def test_import_json_succeeds_on_valid_input(tmp_path) -> None:
    """Control: the happy path reports no errors."""
    store = _store(tmp_path)
    assert store.import_json(store.export_json()) == []


def test_import_json_reports_a_parse_error_as_a_json_error(tmp_path) -> None:
    """Control: a genuine parse failure must still blame the JSON."""
    store = _store(tmp_path)
    errors = store.import_json("{not json")
    assert errors and "Invalid settings JSON" in errors[0]


def test_import_json_reports_a_persist_failure_as_such(tmp_path) -> None:
    store = _store(tmp_path)
    (tmp_path / "settings.json").mkdir()  # the persist target becomes unwritable

    errors = store.import_json(store.export_json())

    assert errors, "a failed apply returned no error"
    assert "Invalid settings JSON" not in errors[0], (
        "a disk failure is still reported as a JSON parse failure"
    )
    assert errors[0].startswith("Could not apply imported settings:")
    assert any(
        token in errors[0]
        for token in ("PermissionError", "IsADirectoryError", "OSError", "FileNotFoundError")
    ), f"the cause was not named: {errors[0]!r}"


def test_a_failed_persist_leaves_memory_and_disk_diverged(tmp_path) -> None:
    """Documents current behaviour: `update` assigns before it persists.

    Recorded in `DELEGATION.md` §4 item 37 and deliberately *not* fixed — persisting
    first and assigning after would change when the in-memory value moves, which is a
    behaviour change.  This test exists so that fixing it has to be deliberate.
    """
    store = _store(tmp_path)
    (tmp_path / "settings.json").mkdir()
    proposed = store.get()
    proposed.privacy.external_llm_allowed = True

    with pytest.raises(OSError):
        store.update(proposed, "test", "persist failure")

    assert store.get().privacy.external_llm_allowed is True, (
        "the in-memory value no longer moves when the persist fails — "
        "update DELEGATION.md §4 item 37 and this pin together"
    )
