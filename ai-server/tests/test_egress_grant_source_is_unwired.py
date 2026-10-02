"""The gate's second permission path is implemented, tested — and never attached.

``aegis_ai/egress/permissions.py`` supplies the permission path the 2026-09-30 re-scope
requires: a permission the user gave about a **specific** destination, recorded as an
ordinary confirmation whose ``capability_id`` is ``egress.external_permission``. The gate
consults it on every ``check()`` via ``_user_grant``, and ``tests/test_egress_permission.py``
pins the behaviour thoroughly — the exact host match, the purpose match, case-insensitivity,
the absence of a wildcard, expiry, non-permitting statuses, a raising source, a source that
cannot answer at all.

**All of that runs against a gate the test assembles.** Measured 2026-10-03:

* ``ConfirmationGrantSource(...)`` has **no construction site in ``src/``** — the only calls
  anywhere are three in ``tests/test_egress_permission.py``.
* The composition root calls ``configure_egress_gate(settings_store=...)`` and never
  ``set_permission_source``, so ``_permission_source`` stays ``None`` and ``_user_grant``
  answers "no grant" on every request.

So in the running system a recorded egress permission has **no effect**: only the standing
configuration (master switch + purpose flag + allowlist) can permit anything. The ask
machinery works; the grant it records is not consumed.

**Recorded, not wired, not deleted** — deliberately. Wiring it *widens* what may leave the
local environment (a user-approved confirmation would become sufficient for that host and
purpose), which is a decision about the constraint rather than a cleanup; deleting it would
throw away the mechanism the re-scope names. ``DELEGATION.md`` §4 item 22 carries the
decision, including the exact one-line change and where it has to go.

The pin fails in **both** directions — attaching the source at the composition root and
removing the mechanism both trip it — so neither can happen as a side effect.
"""

from __future__ import annotations

import ast
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1]
_SRC = _SERVER / "src"
_TESTS = _SERVER / "tests"
_RUNTIME = _SRC / "aegis_ai" / "runtime.py"
_EGRESS_DIR = _SRC / "aegis_ai" / "egress"

_SOURCE_CLASS = "ConfirmationGrantSource"
_SETTER = "set_permission_source"

#: The non-vacuity floor for the positive control. ``src/`` holds 400+ modules; a scan that
#: silently reads nothing must not be able to satisfy the assertions below by returning
#: empty sets. (Same shape as the other "stays unwired" pins.)
_MIN_SRC_FILES = 300


def _src_files() -> list[Path]:
    return sorted(p for p in _SRC.rglob("*.py") if "__pycache__" not in p.parts)


def _parsed(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))


def _identifier_references(tree: ast.Module, name: str) -> int:
    """How often ``name`` appears as an identifier — an import, a call, a bare name.

    Deliberately *not* a text search: a docstring that mentions the class is not a
    reference, and ``gate.py``'s docstring does mention it. Comments and strings are
    therefore excluded by construction.
    """
    hits = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name:
            hits += 1
        elif isinstance(node, ast.Attribute) and node.attr == name:
            hits += 1
        elif isinstance(node, ast.ImportFrom):
            hits += sum(1 for alias in node.names if alias.name == name)
        elif isinstance(node, ast.Import):
            hits += sum(1 for alias in node.names if alias.name.endswith(name))
    return hits


def _composition_root_calls() -> list[ast.Call]:
    """Every ``configure_egress_gate(...)`` call in ``runtime.py``."""
    return [
        node
        for node in ast.walk(_parsed(_RUNTIME))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "configure_egress_gate"
    ]


# ── Non-vacuity: the scan must be reading a tree, and the mechanism must exist ──


def test_the_scan_reads_the_tree_and_the_mechanism_exists() -> None:
    files = _src_files()
    assert len(files) >= _MIN_SRC_FILES, (
        f"the src scan found only {len(files)} modules (floor {_MIN_SRC_FILES}) — a scan that "
        "reads nothing would satisfy the unwired assertion below for the wrong reason"
    )

    in_package = [
        p
        for p in _EGRESS_DIR.rglob("*.py")
        if "__pycache__" not in p.parts
        and _identifier_references(_parsed(p), _SOURCE_CLASS) > 0
    ]
    assert in_package, (
        f"nothing inside {_EGRESS_DIR.name}/ references {_SOURCE_CLASS} — the mechanism this "
        "pin records as unwired appears to have been deleted, which needs its own decision "
        "(DELEGATION.md §4 item 22)"
    )


def test_the_tests_still_exercise_the_mechanism() -> None:
    """The other half of the non-vacuity: if the tests stop calling it, "unwired" is trivially true.

    The pin file itself is excluded — it names the class on purpose, and an instrument that
    counts its own references erases what it measures.
    """
    pin_file = Path(__file__).resolve()
    scanned = sorted(
        p
        for p in _TESTS.rglob("*.py")
        if "__pycache__" not in p.parts and p.resolve() != pin_file
    )
    callers = [p for p in scanned if _identifier_references(_parsed(p), _SOURCE_CLASS) > 0]

    assert callers, (
        "no test outside this pin references the grant source — the coverage that makes "
        "'implemented but unwired' a meaningful statement is gone"
    )
    assert len(scanned) >= 50, (
        f"only {len(scanned)} test modules scanned; the exclusion may have swallowed the tree"
    )


# ── The claim: nothing in src/ attaches it ───────────────────────────────────


def test_no_module_outside_the_egress_package_references_the_grant_source() -> None:
    offenders = sorted(
        str(p.relative_to(_SRC))
        for p in _src_files()
        if _EGRESS_DIR not in p.parents
        and _identifier_references(_parsed(p), _SOURCE_CLASS) > 0
    )
    assert offenders == [], (
        f"{offenders} reference {_SOURCE_CLASS} outside the egress package. If that is the "
        "composition root *attaching* it, the grant path is now live — that is a deliberate "
        "change to what may leave the local environment, so update the register "
        "(PROJECT_STATUS_REVIEW.md §3.2) and DELEGATION.md §4 item 22 in the same commit."
    )


def test_the_composition_root_passes_no_permission_source() -> None:
    calls = _composition_root_calls()
    assert calls, (
        "runtime.py no longer calls configure_egress_gate at all — the gate is the single "
        "enforcement point for the constraint, so this needs investigating, not a relaxed pin"
    )

    # An explicit ``permission_source=None`` is inert and is not the thing this pin is about;
    # any *other* value attaches a source, which is the deliberate change.
    offending = [
        call.lineno
        for call in calls
        for kw in call.keywords
        if kw.arg == "permission_source"
        and not (isinstance(kw.value, ast.Constant) and kw.value.value is None)
    ]
    assert offending == [], (
        f"runtime.py:{offending} passes permission_source to configure_egress_gate — the grant "
        "path is live, so the register and DELEGATION.md §4 item 22 must be updated in the "
        "same commit"
    )


def test_the_composition_root_never_attaches_it_after_the_fact() -> None:
    """The other way to wire it: ``set_permission_source`` once the store exists.

    The confirmation store is built ~300 lines *after* the gate is configured, so this is the
    natural place a future wiring would land.
    """
    assert _identifier_references(_parsed(_RUNTIME), _SETTER) == 0, (
        f"runtime.py calls {_SETTER} — the grant path is live; see the register"
    )
