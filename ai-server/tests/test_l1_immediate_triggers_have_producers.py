"""Every L1 immediate trigger must have a publisher — except the three recorded
ones, which must NOT (DELEGATION.md section 4 item 45).

Measured 2026-10-05: `hook.matched`, `commitment.due` and `browser.discovery` are
declared in `runtime._L1_IMMEDIATE_EVENT_TYPES` but nothing publishes them; the
concepts they name are already carried by `self_call` (the hook engine emits it on
a match, and a due commitment is turned into a hook). Keeping the declarations is
a statement of intent; this pin makes the *absence of a producer* explicit rather
than assumed:

  - a **control** proves the scanner finds real literal publishers (otherwise the
    absence assertions would be vacuously true);
  - the three recorded names must still have **zero** literal publishers;
  - the three must still be **declared** — so deleting them from the set comes
    back here, and adding a producer for one of them does too.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"

# Recorded as declared-but-unproduced (DELEGATION.md section 4 item 45).
_UNPRODUCED = frozenset({"hook.matched", "commitment.due", "browser.discovery"})

# Literal event types passed to a publish-shaped call. Controls prove the scan is
# not empty: `l1.observation` is published positionally by `runtime.py`, and
# `presentation.created` positionally by `presentation/manager.py::_publish_event`.
_CONTROLS = ("l1.observation", "presentation.created")


def _literal_published_event_types() -> set[str]:
    """Event types passed as a string literal to any publish-shaped call in src/."""
    found: set[str] = set()
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if "publish" not in name:
                continue
            args = list(node.args) + [kw.value for kw in node.keywords]
            for arg in args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value:
                    found.add(arg.value)
    return found


def test_the_scanner_finds_real_publishers() -> None:
    published = _literal_published_event_types()
    missing = [c for c in _CONTROLS if c not in published]
    assert not missing, (
        f"scanner found no literal publisher for {missing} — the absence assertions "
        f"below would be vacuously true (found {len(published)} literal event types)"
    )


def test_the_recorded_triggers_still_have_no_producer() -> None:
    published = _literal_published_event_types()
    produced = sorted(_UNPRODUCED & published)
    assert not produced, (
        f"{produced} now has a literal publisher — remove it from _UNPRODUCED and "
        "update DELEGATION.md section 4 item 45 (the trigger is no longer dead)"
    )


def test_the_recorded_triggers_are_still_declared() -> None:
    from aegis_ai.runtime import _L1_IMMEDIATE_EVENT_TYPES

    missing = sorted(_UNPRODUCED - set(_L1_IMMEDIATE_EVENT_TYPES))
    assert not missing, (
        f"{missing} was removed from _L1_IMMEDIATE_EVENT_TYPES — if that is deliberate, "
        "drop it from _UNPRODUCED and update DELEGATION.md section 4 item 45"
    )
