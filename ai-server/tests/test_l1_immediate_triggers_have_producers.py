"""Three L1 immediate triggers are declared but unproduced — and this pin holds
that *specific* absence, not a blanket "every trigger has a producer"
(DELEGATION.md section 4 item 45).

Measured 2026-10-05: `hook.matched`, `commitment.due` and `browser.discovery` are
declared in `runtime._L1_IMMEDIATE_EVENT_TYPES` but nothing publishes them; the
concepts they name are already carried by `self_call` (the hook engine emits it on
a match, and a due commitment is turned into a hook). Keeping the declarations is
a statement of intent; this pin makes the *absence of a producer* explicit rather
than assumed.

⚠️ What this module does NOT assert (corrected 2026-10-05, cycle 32). The scanner
below is deliberately narrow: it reads only `ai-server/src/**/*.py`, and only calls
whose callee name contains "publish". It is blind to `Event(event_type=...)`, to
`build_event(...)`, and to producers written in another language (Kotlin in
`android-server`, Rust in `pc-server`). Measured with this exact scanner: only
**one** of the sixteen declared triggers (`social.inbox.received`) has a literal
publisher here. The other fifteen do not — so the older phrasing "every trigger
except these three has a publisher" was a claim about *mentions* (a consumer, an
allow-list entry or a UI reader in some other file), not about producers. The three
assertions actually made:

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


def test_the_scanner_sees_only_one_declared_trigger() -> None:
    """Pin the scanner's *scope limit*, so its silence about the other fifteen is
    an asserted fact rather than an assumed one.

    Measured 2026-10-05: of the sixteen declared triggers this scanner (ai-server
    Python, callee name containing "publish") finds a literal publisher for exactly
    one. That is a statement about the *scanner*, not about the system — the other
    fifteen are produced elsewhere (Kotlin `eventType = …` in android-server, Rust
    `event_type: …` in pc-server) or via shapes this scanner cannot see
    (`Event(event_type=…)`, `build_event(...)`). Adding a Python publisher for any
    of them, or widening the scanner, comes back here.
    """
    from aegis_ai.runtime import _L1_IMMEDIATE_EVENT_TYPES

    declared = set(_L1_IMMEDIATE_EVENT_TYPES)
    found = sorted(_literal_published_event_types() & declared)
    assert found == ["social.inbox.received"], (
        f"the scanner now finds {found} among the declared triggers (was "
        "['social.inbox.received']) — if a real publisher was added, say so here "
        "and in DELEGATION.md section 4 item 45; if the scanner was widened, the "
        "scope note in this module's docstring is now stale"
    )
