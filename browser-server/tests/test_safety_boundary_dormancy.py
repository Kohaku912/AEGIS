"""The browser safety boundary is dormant — record that, do not let it drift.

``BrowserSafetyBoundary`` offers four checks. **Nothing in ``src/`` calls any of
them.** The boundary is constructed (``browser_use_agent.py``) and only
``get_actions_taken()`` is ever read — which always returns ``[]``, because
``record_action()`` is never called either.

So the "forbidden actions" that the browser server advertises — including
``use_proxy_for_evasion`` and ``bulk_signup`` — reach the model **only as prompt
text**. They are not enforced by code. That is a live gap, not a design: the hard
checks exist and are unit-tested, but no execution path consults them.

This guard does not close the gap. It makes the gap *visible and stable* so that
(a) nobody reads the boundary as active enforcement, and (b) wiring any check
forces this record to be updated in the same change.

Why the checks are not simply switched on (recorded 2026-09-29):

* ``check_action`` compares against **our** action vocabulary
  (``read_page``/``open_link``/``click_button``…). browser-use emits its *own*
  action names, so wiring it as-is would block every action rather than only the
  forbidden ones. It needs a translation layer first.
* ``check_page_observation`` returns ``needs_approval=True`` for its
  ``APPROVAL_BOUNDARIES`` (``publish``/``submit``/``upload``/``account_creation``).
  Wiring it wholesale would **re-introduce a forced approval gate**, which the
  owner boundary forbids (the forced gate stays deleted). Only its
  ``STOP_BOUNDARIES`` half is compatible with the current goal.
* ``check_domain`` is the per-navigation egress check and has no approval
  semantics, so it is the safest one to wire — but the pre-flight
  ``_navigation_egress_denied`` already covers *declared* targets, and hooking
  browser-use's per-action loop cannot be verified here (``browser-use`` is not
  installed in the test environment).

Following the same discipline as ``test_ineffective_flags.py``: the checks are
**discovered**, not hand-listed, and the recorded set must *equal* the unwired
set — so the record cannot drift silently.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from aegis_browser.safety_boundary import BrowserSafetyBoundary

_SRC = Path(__file__).resolve().parents[1] / "src"

#: Checks that nothing calls yet. This is an **inventory of debt**, not a set of
#: approvals: every entry needs a decision about *how* to wire it, for the reasons
#: in the module docstring.
_UNWIRED_CHECKS: dict[str, str] = {
    "check_action": (
        "Needs an action-vocabulary translation (ours vs browser-use's) before it "
        "can be wired; as-is it would block every action."
    ),
    "check_page_content": (
        "Unreachable by design: it rejects unstructured prose so that safety is "
        "never inferred from page text. Nothing calls it because nothing should."
    ),
    "check_domain": (
        "Per-navigation egress check. Declared targets are already covered "
        "pre-flight; wiring this needs a browser-use per-action hook that cannot "
        "be verified in this environment."
    ),
    "check_page_observation": (
        "Its APPROVAL_BOUNDARIES half is a forced approval gate, which the owner "
        "boundary forbids. Only the STOP_BOUNDARIES half could be wired."
    ),
}


def _boundary_checks() -> list[str]:
    """Every ``check_*`` method the boundary offers, discovered rather than listed."""
    return sorted(name for name in vars(BrowserSafetyBoundary) if name.startswith("check_"))


def _called_in_src() -> set[str]:
    """Names of boundary checks actually invoked somewhere under ``src/``.

    Parsed with ``ast`` rather than grepped so that a docstring or comment
    mentioning a check is not mistaken for a call — the same distinction
    ``test_goal_change_guard.py`` draws.
    """
    called: set[str] = set()
    for path in _SRC.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:  # pragma: no cover - source should always parse
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr.startswith("check_"):
                called.add(func.attr)
    return called


def test_the_boundary_checks_are_discovered_not_listed():
    """The scan covers the real surface, so a new check cannot be invisible."""
    checks = _boundary_checks()
    assert "check_action" in checks
    assert "check_domain" in checks
    assert len(checks) >= 4


def test_every_unwired_check_is_recorded_with_a_reason():
    """No check may be dormant without an entry explaining why."""
    for name, reason in _UNWIRED_CHECKS.items():
        assert name in _boundary_checks(), f"{name} is recorded but no longer exists"
        assert len(reason) > 40, f"{name} needs a real reason, not a placeholder"


def test_the_recorded_dormancy_matches_reality():
    """The unwired set must *equal* the recorded set.

    If someone wires a check, this fails until the record is updated — which is
    the point: activation is a decision, and the docstring above has to move with
    it.
    """
    checks = set(_boundary_checks())
    wired = _called_in_src()
    unwired = checks - wired
    assert unwired == set(_UNWIRED_CHECKS), (
        "The set of dormant safety checks changed.\n"
        f"  dormant now : {sorted(unwired)}\n"
        f"  recorded    : {sorted(_UNWIRED_CHECKS)}\n"
        "Update _UNWIRED_CHECKS and the module docstring together with the change."
    )


def test_the_forbidden_actions_are_prompt_only_today():
    """Pin the consequence: the advertised prohibitions are not code-enforced.

    ``use_proxy_for_evasion`` and ``bulk_signup`` appear in the task's
    ``forbidden_actions``, but since ``check_action`` is never called they only
    reach the model as prompt text. This asserts the *current* truth so the gap
    cannot be described as closed without wiring something.
    """
    from aegis_browser.main import _BASE_FORBIDDEN_ACTIONS

    assert "use_proxy_for_evasion" in _BASE_FORBIDDEN_ACTIONS
    assert "bulk_signup" in _BASE_FORBIDDEN_ACTIONS
    assert "check_action" not in _called_in_src(), (
        "check_action is now called — the prohibitions are enforced, so update "
        "docs/permissions.md and the report (P1-7)."
    )


def test_the_approval_exception_is_unreachable():
    """A dead ``except`` implies a dead ``raise`` (bug class: dead except).

    ``ApprovalBoundary`` is caught but never raised, so ``TaskStatus.NEEDS_APPROVAL``
    is an enum member with no producer — a forced-gate surface that exists only on
    paper. Recorded here because the goal change deleted the forced gate.
    """
    raised = set()
    for path in _SRC.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        raised |= set(re.findall(r"raise\s+(\w+)", text))
    assert "ApprovalBoundary" not in raised, (
        "ApprovalBoundary is now raised — that is a forced approval gate, which "
        "the owner boundary forbids. See docs/permissions.md."
    )
