"""A gate's verdict must carry its denominator.

`scripts/test-ai-server.ps1` runs four checks; `-SkipMutation` runs three of them.
`scripts/test-all-suites.ps1` runs four; `-SkipAiServer` runs three. Both printed a bare

    ALL CHECKS PASSED

for the complete run *and* for the reduced one (measured 2026-10-06, before the fix), so
the last line -- the line CI and the run records quote -- could not tell a run that
skipped the mutation check from one that ran it. The mutation check is the control that
says the egress suite has been observed failing; a verdict that hides its absence is the
silent-bypass shape in its purest form.

Each gate now counts what ran and what was skipped, reconciles that census against a
declared total, and prints `ALL <ran>/<total> CHECKS PASSED` plus the reason a run is
reduced. `scripts/test-beta-real.ps1` carried the same family one layer down: its browser
check was neither passed, failed, nor skipped when the browser did not respond, so
`Results: 6 passed, 0 failed` described a run that attempted seven checks.

Why this test is static: CI has no PowerShell (see the `aegis-verify-and-test` skill), so
the behavioural proof was done by extracting each script's verdict tail and replaying it
on four shapes -- complete, reduced, one failed, broken census -- which produced four
distinct lines. What a PowerShell-free CI *can* pin is the shape that made that possible:
the denominator must appear in the verdict, the verdict must depend on the skipped set,
and the bare form must not come back.

The two gates express "which checks were skipped" differently -- one interpolates
`$skipped` into the verdict, the other builds a `$reduction` list first -- so
`_verdict_depends_on_skipped` follows the variable one step instead of pinning either
script's syntax.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"
_GATES = ("test-ai-server.ps1", "test-all-suites.ps1")

# The denominator is in the verdict: `ALL $($ran.Count)/$checksTotal CHECKS PASSED`.
# The array name is left free, so renaming it does not read as a regression.
_VERDICT = re.compile(r"ALL \$\(\$\w+\.Count\)/\$checksTotal CHECKS PASSED")
_CHECKS_TOTAL = re.compile(r"^\$checksTotal = \d+\s*$", re.M)
# The old form, anchored to the statement that printed it. Both scripts carry a comment
# that *quotes* the bare line while explaining what changed; a mention is not the line.
_BARE = re.compile(r'Write-Host\s+"\s*ALL CHECKS PASSED\s*"')


def _text(name: str) -> str:
    return (_SCRIPTS / name).read_text(encoding="utf-8")


def _verdict_depends_on_skipped(text: str) -> bool:
    """True if the passing verdict's text depends on the skipped set.

    A verdict that is the same expression whether or not checks were skipped cannot tell
    the two runs apart. Statically, that means the `CHECKS PASSED` line must interpolate
    `$skipped`, or a variable assigned from it somewhere in the same tail.
    """
    tail = text[text.index("$checksAccounted") :]
    # A variable holding the "skipped: ..." label -- test-all-suites builds `$reduction`
    # that way (inside a one-line `if`, so the assignment is not at line start);
    # test-ai-server interpolates `$skipped` into the verdict directly.
    derived = set(re.findall(r"\$(\w+)\s*\+?=\s*[^\n]*skipped:[^\n]*\$skipped", tail))
    tokens = {"skipped", *derived}
    return any(
        "CHECKS PASSED" in line and any(f"${token}" in line for token in tokens)
        for line in tail.splitlines()
    )


def test_the_bare_verdict_pattern_matches_the_old_line_and_not_a_mention() -> None:
    """Control: the guard must be able to fail, and must not fire on a quoted mention."""
    old_line = 'Write-Host "  ALL CHECKS PASSED" -ForegroundColor Green'
    mention = '# a bare "ALL CHECKS PASSED" is the same string a full run prints'

    assert _BARE.search(old_line), "the pattern must catch the line that was removed"
    assert not _BARE.search(mention), "a comment quoting the old line is not the old line"
    assert not _VERDICT.search(old_line), "the old line carried no denominator"


def test_the_skip_awareness_predicate_rejects_the_old_verdict() -> None:
    """Control: `_verdict_depends_on_skipped` must be able to say no."""
    old = (
        "$checksAccounted = $ran.Count + $skipped.Count\n"
        'Write-Host "  ALL CHECKS PASSED" -ForegroundColor Green\n'
    )
    assert not _verdict_depends_on_skipped(old)


@pytest.mark.parametrize("name", _GATES)
def test_gate_declares_the_check_total_it_reconciles_against(name: str) -> None:
    assert _CHECKS_TOTAL.search(_text(name)), f"{name} must declare its check total"


@pytest.mark.parametrize("name", _GATES)
def test_gate_verdict_carries_its_denominator(name: str) -> None:
    text = _text(name)
    assert _VERDICT.search(text), f"{name} must print how many checks ran, of how many"
    assert not _BARE.search(text), f"{name} must not print the bare verdict again"


@pytest.mark.parametrize("name", _GATES)
def test_gate_verdict_can_differ_when_checks_are_skipped(name: str) -> None:
    assert _verdict_depends_on_skipped(_text(name)), (
        f"{name}'s passing verdict must depend on the skipped set, or a reduced run "
        "prints a line that says nothing about what it skipped"
    )


def test_beta_browser_check_is_counted_as_skipped() -> None:
    """One layer down: an attempted check that is not counted is not in the denominator."""
    text = _text("test-beta-real.ps1")
    assert "$total = $passed + $failed + $skipped" in text
    assert "$passed/$total" in text, "the beta verdict must carry its denominator too"
    assert text.count("$skipped++") == 2, "the no-response path and the -SkipBrowser path"
