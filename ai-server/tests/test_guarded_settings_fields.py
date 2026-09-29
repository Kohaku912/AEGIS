"""A settings field that a validator guards must also be consumed by a decision (B-13).

`test_ineffective_flags.py` asks "does anything in `src/` mention this field?" — a plain
identifier search. That is the right question for most of the surface, but it has one shape
it cannot see: **a field that exists only to be validated.** A field read by
`settings/validation.py::validate_settings_change` has a "reader", so the identifier scan
passes — while the effect the field advertises is implemented nowhere.

This file asks the narrower, answerable question: **for the fields a validator reads, is
there a consumer outside the validator?** Discovery on both sides — the guarded fields are
parsed out of `validation.py`, the sections are taken from `AEGISSettings.model_fields`, and
the consumers are found by scanning `src/` — so a newly guarded field with no consumer fails
here, and a field that gains one fails the equality check until its debt entry is removed.

The two files can legitimately disagree about the same field, and that is the point rather
than a bug: `test_ineffective_flags.py` counts the validator as a reader, this file does not.
When they disagree, this file is the one that is right about the *effect* — see
`max_autonomous_runs_per_hour` below, which the identifier scan reports as read.

## Scope, and what changed on 2026-09-29 (A-1)

The original scan looked only at `*.capabilities.<field>`, because the first instance found
was `CapabilityPermissions.allowlist` — a field that existed solely to be policed. A-1
deleted that field, the deny-list it was checked against, and all three validator loops, so
`allowlist` is no longer guarded and no longer here; the deletion is pinned by
`tests/test_forbidden_capabilities_stay_retired.py`. The scan was widened to every settings
section at the same time, and immediately found a second, live instance:
`max_autonomous_runs_per_hour`, recorded in `_RECORDED_GAPS`.

Scope is still deliberately the guarded fields only. Demanding "consumed by a decision" of
all 95 settings fields would fail most of them, because most are read by config plumbing
rather than by a decision — and a detector whose failures must be triaged is worse than
none (see the `aegis-verify-and-test` skill, "if a dry run is mostly false positives, the
detector is wrong").
"""

from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

import pytest

from aegis_ai.settings.models import AEGISSettings

_SRC = Path(__file__).resolve().parents[1] / "src"
_VALIDATOR = _SRC / "aegis_ai" / "settings" / "validation.py"

#: Fields the validator reads but nothing else consumes. An inventory of debt, not an
#: approval — each entry needs an owner decision (wire it or delete it).
_RECORDED_GAPS: dict[str, str] = {
    "max_autonomous_runs_per_hour": (
        "Guarded by `validate_settings_change` ('cannot exceed 100') and read nowhere "
        "outside it. The autonomous loop runs on hardcoded budgets and intervals (see the "
        "`_AUTONOMOUS` note in test_ineffective_flags.py), so editing this field in the "
        "settings file changes no behaviour — it only decides whether the *edit* is "
        "rejected. Found 2026-09-29 when this file's scan widened from "
        "`*.capabilities.<field>` to every settings section; the identifier scan cannot see "
        "it, because it counts the validator as a reader. Owner call — wire it into the "
        "loop, or delete it."
    ),
}


def _parsed(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:  # pragma: no cover - a syntax error fails elsewhere
        return None


def _source_files() -> list[Path]:
    return [
        path
        for path in sorted(_SRC.rglob("*.py"))
        if "__pycache__" not in path.parts and "generated" not in path.parts
    ]


def _settings_sections() -> set[str]:
    """The sub-model field names on ``AEGISSettings``, discovered from the model itself."""
    return set(AEGISSettings.model_fields)


def _guarded_fields() -> set[str]:
    """Settings fields ``validate_settings_change`` reads, e.g. ``privacy.<field>``.

    Discovered on both sides: the section names come from the model and the reads come from
    the validator's AST, so neither is a hand list. Attribute access rather than class-body
    definitions, so ``settings/models.py`` declaring the fields does not count as reading
    them.
    """
    tree = _parsed(_VALIDATOR)
    assert tree is not None, f"{_VALIDATOR} did not parse"
    sections = _settings_sections()
    found: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Attribute)
            and node.value.attr in sections
        ):
            found.add(node.attr)
    return found


def _consumers(field: str) -> list[str]:
    """Modules under ``src/`` that read ``<something>.<field>`` outside the validator.

    The validator is excluded because policing a field is not implementing its effect —
    that is the blind spot this file exists to cover.
    """
    hits: list[str] = []
    for path in _source_files():
        if path == _VALIDATOR:
            continue
        tree = _parsed(path)
        if tree is None:
            continue
        if any(isinstance(node, ast.Attribute) and node.attr == field for node in ast.walk(tree)):
            hits.append(path.relative_to(_SRC).as_posix())
    return hits


GUARDED = sorted(_guarded_fields())
UNCONSUMED = [f for f in GUARDED if not _consumers(f)]


# ── Guards on the detector itself ─────────────────────────────────────────────


def test_the_scan_finds_the_fields_the_validator_guards() -> None:
    """An empty or truncated guarded set would pass the invariant vacuously."""
    assert len(GUARDED) >= 2, f"only {len(GUARDED)} guarded fields discovered: {GUARDED}"
    assert "camera_snapshot_enabled" in GUARDED, (
        "the scan no longer sees `proposed.privacy.camera_snapshot_enabled` — it is reading "
        "the wrong shape of attribute access"
    )
    assert "max_autonomous_runs_per_hour" in GUARDED


def test_the_consumer_scan_actually_finds_consumers() -> None:
    """The scan must be able to return a non-empty answer, or every gap is fake."""
    assert _consumers("camera_snapshot_enabled"), (
        "the consumer scan found nothing for a field that settings/permissions.py reads"
    )
    assert not _consumers("max_autonomous_runs_per_hour")


# ── The invariant ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("field", GUARDED)
def test_every_guarded_field_is_consumed_somewhere(field: str) -> None:
    """A validator is not a consumer: policing a field does not implement its effect."""
    if _consumers(field):
        return
    assert field in _RECORDED_GAPS, (
        f"`{field}` is read by validate_settings_change but nowhere outside it. Either wire "
        "it to a decision, delete it, or record it in _RECORDED_GAPS with a reason. Note "
        "that being mentioned in validation.py does NOT count as a reader — that is the "
        "blind spot this file exists to cover."
    )


def test_the_recorded_gaps_are_exactly_the_current_gaps() -> None:
    """Equality both ways: a new gap fails, and a closed gap fails until the entry goes."""
    observed = Counter(UNCONSUMED)
    recorded = Counter(_RECORDED_GAPS.keys())
    assert observed == recorded, (
        "the recorded unconsumed fields no longer match the observed ones.\n"
        f"  newly unconsumed : {sorted(observed - recorded)}\n"
        f"  now consumed     : {sorted(recorded - observed)}\n"
        "Update _RECORDED_GAPS. If a field gained a consumer, say so in the commit message "
        "rather than silently dropping the entry."
    )
