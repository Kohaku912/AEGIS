"""A corrupt social store must be reported, not just silently empty.

``SocialIntelligenceSystem._load`` reads six JSONL stores. One of them —
``_load_jsonl`` — has always logged its failures; the four specific loaders
(``relationships`` / ``reputations`` / ``social_norms`` / ``social_skills``) used
``except Exception: pass``.

The consequence is the familiar one: the store falls back to an empty dict, and
the only other signal is ``_load``'s summary line, which counts entries. A store
that failed to parse and a store that has no entries yet produce **the same
line** — so a corrupted ``relationships.jsonl`` looks exactly like a fresh
install, and nothing else in the suite reads these files.

Measured 2026-10-04 by driving the class with a corrupt file, not by reading it.
"""

from __future__ import annotations

import dataclasses
import json
import logging

import pytest

from aegis_ai.social.intelligence import Reputation, SocialIntelligenceSystem

_LOGGER = "aegis_ai.social.intelligence"

# (filename on disk, the private dict it fills)
_STORES = [
    ("relationships.jsonl", "_relationships"),
    ("reputations.jsonl", "_reputations"),
    ("social_norms.jsonl", "_norms"),
    ("social_skills.jsonl", "_skills"),
]


def _warnings(caplog) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING]


@pytest.mark.parametrize("filename,attr", _STORES)
def test_a_corrupt_store_is_reported_by_name(tmp_path, caplog, filename, attr) -> None:
    (tmp_path / filename).write_text("{ not jsonl", encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        system = SocialIntelligenceSystem(data_dir=str(tmp_path))

    # The fallback is unchanged — the store is still simply empty…
    assert getattr(system, attr) == {}
    # …but now it says *which file* failed, so "empty" and "corrupt" differ.
    messages = _warnings(caplog)
    assert any(filename in m for m in messages), messages


@pytest.mark.parametrize("filename,attr", _STORES)
def test_a_missing_store_stays_silent(tmp_path, caplog, filename, attr) -> None:
    # Non-vacuity control: no file at all is the normal first-run case, and warning
    # about it would make the real warnings useless.
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        system = SocialIntelligenceSystem(data_dir=str(tmp_path))

    assert getattr(system, attr) == {}
    assert _warnings(caplog) == []


def test_one_corrupt_store_does_not_stop_the_others(tmp_path, caplog) -> None:
    (tmp_path / "relationships.jsonl").write_text("{ not jsonl", encoding="utf-8")
    good = dataclasses.asdict(Reputation(person_name="alice"))
    (tmp_path / "reputations.jsonl").write_text(json.dumps(good) + "\n", encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        system = SocialIntelligenceSystem(data_dir=str(tmp_path))

    assert "alice" in system._reputations, system._reputations
    messages = _warnings(caplog)
    assert any("relationships.jsonl" in m for m in messages), messages
    assert not any("reputations.jsonl" in m for m in messages), messages


def test_the_pre_existing_helper_reports_too(tmp_path, caplog) -> None:
    # ``_load_jsonl`` (observations / episodes) already warned. Pinning it here keeps
    # the four loaders and their precedent from drifting apart again.
    (tmp_path / "observations.jsonl").write_text("{ not jsonl", encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        SocialIntelligenceSystem(data_dir=str(tmp_path))

    messages = _warnings(caplog)
    assert any("observations.jsonl" in m for m in messages), messages
