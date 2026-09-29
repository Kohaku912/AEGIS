"""The README's Safety Model table is a claim about ``PolicyEngine`` — check it against the code.

Why this file exists
--------------------
On 2026-09-29 the README — the repo's front door, and the only doc in it that made a
flat claim while carrying **no** goal-change banner — still advertised the retired
ladder:

    | Level 2 (APPROVAL_REQUIRED) | Needs approval | Approval UI required |
    | Level 3 (HIGH_RISK)         | High risk       | Approval or deny     |

Both rows are false. ``PolicyEngine.DEFAULT_RISK_MAP`` maps ``APPROVAL_REQUIRED`` and
``HIGH_RISK`` to ``ALLOW_WITH_AUDIT``, and nothing prompts — risk levels are annotations,
not gates. The 5-level ladder is itself retired; the live model is the 4-value
``PolicyDecision``.

Why not a general prose scanner. A sweep of the whole repo found this was the *only* such
site: 57 docs mention approval, 48 carry a corrective banner, and of the 9 that do not, 8
are ADRs (historical by definition) or already self-correcting in their own text. A scanner
covering the rest would need an exclusion list, and a hand-maintained exclusion list is
itself the defect it is meant to catch. So this pins the one site that was wrong.

How it checks. The table is parsed out of the README and each row's stated decision is
compared against ``PolicyEngine.DEFAULT_RISK_MAP`` **itself** — the README is verified
against the code, not against a second copy of the mapping. So adding a risk level to the
map without documenting it fails, and documenting one with the wrong decision fails.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from aegis_schema.models import RiskLevel
from policy_engine import PolicyEngine

_REPO = Path(__file__).resolve().parents[2]
_README = _REPO / "README.md"

_SECTION = re.compile(r"^## Safety Model\s*$(?P<body>.*?)(?=^## |\Z)", re.S | re.M)

#: A row of the documented table. The backticks are required so the header row
#: (``| Risk level | Policy decision | ...``) and the separator cannot match.
_ROW = re.compile(
    r"^\|\s*`(?P<level>[A-Z_]+)`\s*\|\s*`(?P<decision>[A-Z_]+)`\s*\|\s*(?P<behaviour>.+?)\s*\|\s*$",
    re.M,
)


def _section() -> str:
    text = _README.read_text(encoding="utf-8")
    match = _SECTION.search(text)
    assert match is not None, "README.md has no '## Safety Model' section"
    return match.group("body")


def _rows() -> dict[str, tuple[str, str]]:
    """``{risk level: (documented decision, behaviour text)}``."""
    return {
        m.group("level"): (m.group("decision"), m.group("behaviour"))
        for m in _ROW.finditer(_section())
    }


# ── The invariant: the front door agrees with the decision engine ─────────────


def test_the_readme_documents_exactly_the_risk_levels_the_code_maps() -> None:
    documented = {level: decision for level, (decision, _) in _rows().items()}
    assert len(documented) >= 5, (
        f"only {len(documented)} risk-level rows parsed from the README's Safety Model "
        "table — it was probably reformatted, which would make this file vacuous"
    )

    expected = {level.name: decision.name for level, decision in PolicyEngine.DEFAULT_RISK_MAP.items()}
    assert documented == expected, (
        "README.md's Safety Model table disagrees with PolicyEngine.DEFAULT_RISK_MAP.\n"
        f"  documented : {documented}\n"
        f"  in the code: {expected}\n"
        "Risk levels are annotations, not gates — the table must say which decision each "
        "one selects, and there is one right answer, in the engine."
    )


def test_every_documented_level_is_a_real_risk_level() -> None:
    """A typo'd or invented level would otherwise just be an unmatched string."""
    unknown = sorted(set(_rows()) - {level.name for level in RiskLevel})
    assert unknown == [], f"README.md documents risk levels that do not exist: {unknown}"


def test_the_approval_required_row_says_nobody_is_asked() -> None:
    """The exact regression: the README claimed ``APPROVAL_REQUIRED`` triggers an Approval UI.

    ``ALLOW_WITH_AUDIT`` means the call executes; no surface prompts. If this row stops
    saying so, the front door is advertising a forced gate that does not exist again.
    """
    decision, behaviour = _rows()["APPROVAL_REQUIRED"]
    assert decision == "ALLOW_WITH_AUDIT"
    assert "nobody is asked" in behaviour.lower(), (
        f"the APPROVAL_REQUIRED row reads {behaviour!r} — it must state that the label "
        "causes no prompt"
    )


@pytest.mark.parametrize("row_level", sorted(_rows()))
def test_no_row_promises_an_approval_surface(row_level: str) -> None:
    """A prompt is never the consequence of a risk level, whichever level it is."""
    _, behaviour = _rows()[row_level]
    lowered = behaviour.lower()
    for claim in ("approval ui", "needs approval", "approval or deny", "requires approval"):
        assert claim not in lowered, (
            f"the {row_level} row claims {claim!r}: {behaviour!r}. No risk level prompts — "
            "see PolicyEngine.DEFAULT_RISK_MAP."
        )


# ── The other half: the one real constraint must be named ─────────────────────


def test_the_readme_names_the_single_constraint() -> None:
    """The front door described a 5-level approval ladder and never named the constraint."""
    section = _section()
    assert "egress gate" in section
    assert "never leaves the local environment" in section


def test_the_readme_says_the_voluntary_ask_still_exists() -> None:
    """Removing the forced gate did not remove the *voluntary* ask (owner boundary, both halves).

    Pinned here so a future edit that deletes the approval language cannot also quietly
    delete the statement that AEGIS may still choose to ask.
    """
    section = _section()
    assert "confirmation/" in section
    assert "voluntarily" in section.lower()
