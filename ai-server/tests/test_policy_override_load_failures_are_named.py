"""A corrupt ``risk_overrides.json`` must be *named*, not silently discarded.

``PolicyEngine._load_overrides`` used to swallow both failures with a bare ``pass``:

* the outer handler dropped an unreadable/corrupt file (every override lost), and
* the inner handler dropped an unknown risk-level name (that one override lost).

The consequence is not a crash — it is a silent **downgrade**. ``DEFAULT_RISK_MAP``
maps ``RiskLevel.FORBIDDEN`` to ``PolicyDecision.DENY``, so an override that raised a
capability to FORBIDDEN simply stops applying and the capability falls back to its
(more permissive) manifest level. "No overrides file" and "corrupt overrides file"
were indistinguishable.

Its sibling mechanism, ``CapabilityCatalog``'s override store, has always recorded
this (``OverrideStore.corrupted`` / ``override_store_corrupted``) — see
``test_capability_overrides.py::test_corrupt_capability_override_store_falls_back_strictly``.
This pin holds the policy engine to the same standard: *name the failure*.

Measured 2026-10-04 by driving the engine, not by reading it.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from aegis_schema.models import Capability, RiskLevel, ServerType
from policy_engine import PolicyDecision, PolicyEngine

_LOGGER = "aegis_ai.policy_engine"


def _cap(cap_id: str = "pc-server.test.sample", risk: RiskLevel = RiskLevel.READ_ONLY) -> Capability:
    return Capability(
        id=cap_id,
        name=cap_id,
        description=cap_id,
        server_type=ServerType.PC,
        risk_level=risk,
    )


def _data_dir_with(tmp_path: Path, payload: str | None) -> Path:
    """A data dir holding ``risk_overrides.json`` (or not, if payload is None)."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    if payload is not None:
        (data_dir / "risk_overrides.json").write_text(payload, encoding="utf-8")
    return data_dir


# ---------------------------------------------------------------------------------------
# Control first: the mechanism this pin is about must actually bite.
# ---------------------------------------------------------------------------------------


def test_a_forbidden_override_denies_the_capability(tmp_path) -> None:
    # The control. If this did not hold, the "corrupt file" tests below would pass for
    # the wrong reason — there would be no downgrade to demonstrate.
    data_dir = _data_dir_with(tmp_path, json.dumps({"pc-server.test.sample": "FORBIDDEN"}))

    engine = PolicyEngine(data_dir=str(data_dir))

    assert engine._risk_overrides == {"pc-server.test.sample": RiskLevel.FORBIDDEN}
    result = engine.evaluate(_cap(), {})
    assert result.decision == PolicyDecision.DENY, result
    assert result.risk_level == RiskLevel.FORBIDDEN


def test_without_the_override_the_same_capability_is_allowed(tmp_path) -> None:
    # The other half of the control: the manifest level alone is permissive, so the
    # DENY above came from the override and not from the capability id.
    engine = PolicyEngine(data_dir=str(_data_dir_with(tmp_path, None)))
    assert engine.evaluate(_cap(), {}).decision == PolicyDecision.ALLOW


# ---------------------------------------------------------------------------------------
# A corrupt file is named — and the downgrade it causes is measured.
# ---------------------------------------------------------------------------------------


def test_a_corrupt_overrides_file_is_reported_with_its_cause(tmp_path, caplog) -> None:
    data_dir = _data_dir_with(tmp_path, "{ not json")
    path = data_dir / "risk_overrides.json"

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        engine = PolicyEngine(data_dir=str(data_dir))

    records = [r for r in caplog.records if r.name == _LOGGER]
    assert len(records) == 1, [r.getMessage() for r in records]
    message = records[0].getMessage()
    # The cause, the path, and the consequence — not just "it failed".
    assert str(path) in message, message
    assert "JSONDecodeError" in message, message
    assert "NOT in effect" in message, message
    # …and the defect's *shape*: the override is gone, exactly as if never written.
    assert engine._risk_overrides == {}


def test_the_corrupt_file_downgrades_a_forbidden_capability_to_allowed(tmp_path, caplog) -> None:
    # This is the whole point of the pin: the same payload that DENIED above now
    # silently ALLOWs, and the only difference is the corruption of the file.
    data_dir = _data_dir_with(tmp_path, "{ not json")

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        engine = PolicyEngine(data_dir=str(data_dir))

    result = engine.evaluate(_cap(), {})
    assert result.decision == PolicyDecision.ALLOW, result
    assert result.risk_level == RiskLevel.READ_ONLY
    # The downgrade is no longer silent.
    assert any("NOT in effect" in r.getMessage() for r in caplog.records if r.name == _LOGGER)


def test_a_missing_overrides_file_stays_silent(tmp_path, caplog) -> None:
    # Non-vacuity control for the warning: "no file" must NOT warn, or a fresh install
    # would log a warning on every start and the real warning would be lost in it.
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        engine = PolicyEngine(data_dir=str(_data_dir_with(tmp_path, None)))

    assert engine._risk_overrides == {}
    assert [r for r in caplog.records if r.name == _LOGGER] == []


def test_a_non_object_payload_is_reported(tmp_path, caplog) -> None:
    # ``json.load`` can succeed and still not be a mapping; ``.items()`` then raises and
    # the outer handler must still name the file rather than swallow it.
    data_dir = _data_dir_with(tmp_path, json.dumps(["FORBIDDEN"]))

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        engine = PolicyEngine(data_dir=str(data_dir))

    records = [r for r in caplog.records if r.name == _LOGGER]
    assert len(records) == 1, [r.getMessage() for r in records]
    assert "AttributeError" in records[0].getMessage(), records[0].getMessage()
    assert engine._risk_overrides == {}


# ---------------------------------------------------------------------------------------
# An unknown level name loses only *that* override, and says which.
# ---------------------------------------------------------------------------------------


def test_an_unknown_risk_level_is_reported_by_capability(tmp_path, caplog) -> None:
    data_dir = _data_dir_with(
        tmp_path,
        json.dumps({"pc-server.test.sample": "NOT_A_LEVEL", "pc-server.test.other": "FORBIDDEN"}),
    )

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        engine = PolicyEngine(data_dir=str(data_dir))

    records = [r for r in caplog.records if r.name == _LOGGER]
    assert len(records) == 1, [r.getMessage() for r in records]
    message = records[0].getMessage()
    assert "NOT_A_LEVEL" in message, message
    assert "pc-server.test.sample" in message, message
    # The sibling override still loads — one bad name must not discard the rest.
    assert engine._risk_overrides == {"pc-server.test.other": RiskLevel.FORBIDDEN}
    assert engine.evaluate(_cap("pc-server.test.other"), {}).decision == PolicyDecision.DENY


def test_a_clean_overrides_file_does_not_warn(tmp_path, caplog) -> None:
    # Control for the inner handler, mirroring the missing-file control above.
    data_dir = _data_dir_with(tmp_path, json.dumps({"pc-server.test.sample": "HIGH_RISK"}))

    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        engine = PolicyEngine(data_dir=str(data_dir))

    assert engine._risk_overrides == {"pc-server.test.sample": RiskLevel.HIGH_RISK}
    assert [r for r in caplog.records if r.name == _LOGGER] == []
