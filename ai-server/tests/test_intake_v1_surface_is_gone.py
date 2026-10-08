"""The v1 intake surface is gone (DELEGATION.md §4 item 47).

Phase 4's intake path — `IntakeRouter` / `IntakeClassifier` / `IntakeDeduplicator`
plus the data models in `intake/models.py` — was **deleted 2026-10-08** under the
owner's §4 item 47 decision ("削除する"). `L1Router` had replaced `IntakeRouter` on
the live path (`runtime.py` builds `L1Router(llm_gateway=...)`), so the v1 classes
were constructed nowhere in `src/` and the v1 models had no live importer: the
package's own re-exports were the only thing keeping the names importable.

This pin is the **inverse** of the module it replaces
(`tests/test_intake_classes_are_constructed_nowhere.py`), which asserted the three
classes were *unconstructed but still exported*. That assertion is now false by
construction, so it was inverted rather than deleted: the coverage it held (the
intake package's shape) moves from "present and unwired" to "absent".

The deletion's one real hazard is a **name collision**: `intake/models.py` defined a
`RoutingDecision` that is a *different class* from the live
`aegis_ai.agents.profiles.models.RoutingDecision` (the intake one alone had
`should_delegate_to_agent`). Test 4 pins that the live class survived untouched --
otherwise "the name is gone" would be satisfied by deleting the wrong one.

Every "nothing found" check carries a control, so a broken walk cannot pass:
  - the scan still sees the live `L1Router` (test 2);
  - the deleted directory still contains its surviving `l1_*.py` siblings (test 1);
  - `__all__` still lists the nine live L1 names (test 3);
  - the live `RoutingDecision` still has the shape the dead one did not (test 4).
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
_PKG = SRC / "aegis_ai" / "intake"

# Deleted 2026-10-08 (DELEGATION.md §4 item 47).
_DELETED_MODULES = ("models.py", "classifier.py", "deduplicator.py", "router.py")

# Every name the package used to re-export from those modules.
_REMOVED_EXPORTS = (
    "IntakeRouter",
    "IntakeClassifier",
    "IntakeDeduplicator",
    "IntakeResult",
    "IntakeDecision",
    "IntakeRoute",
    "RoutingDecision",
)

# The subset safe to hunt by *bare name* across src/.
#
# `RoutingDecision` is deliberately excluded: `intake/models.py` defined a class of
# that name that is **different** from the live
# `aegis_ai.agents.profiles.models.RoutingDecision`, and three live modules name the
# latter (`agents/__init__.py`, `agents/profiles/__init__.py`,
# `agents/runtime/router.py`). A bare-name absence scan cannot tell the two apart, so
# including it makes this pin fail on a *correct* tree -- which is exactly what this
# pin's first draft did. The collision is pinned from both sides instead: test 3 (the
# intake one is unreachable) and test 5 (the live one is still in use).
_REMOVED_NAMES = (
    "IntakeRouter",
    "IntakeClassifier",
    "IntakeDeduplicator",
    "IntakeResult",
    "IntakeDecision",
    "IntakeRoute",
)

# The shared name, kept separate so its exclusion is visible rather than implicit.
_SHARED_NAME = "RoutingDecision"

# The surviving public surface -- must still be exported.
_LIVE_EXPORTS = (
    "L1Action",
    "L1ActionResult",
    "L1ActionType",
    "L1Decision",
    "L1Escalation",
    "L1Executor",
    "L1Observation",
    "L1Router",
    "RequiredIntelligence",
)

# Controls: a live name in the same scan, and a floor on the walk's size.
_CONTROL_NAME = "L1Router"
_CONTROL_SIBLING = "l1_router.py"
_MIN_SOURCE_FILES = 390


def _source_files() -> list[Path]:
    return sorted(SRC.rglob("*.py"))


def _parsed() -> list[tuple[Path, ast.Module]]:
    out = []
    for path in _source_files():
        out.append((path, ast.parse(path.read_text(encoding="utf-8"), filename=str(path))))
    return out


def _names_in(tree: ast.Module) -> set[str]:
    """Every identifier the module *binds or reads*: Name, Attribute, imports."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                found.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.asname or alias.name.split(".")[0])
    return found


def _scan(collect) -> tuple[bool, list[str]]:
    """Walk src/, return (control_seen, offenders). Raises if the walk is tiny."""
    parsed = _parsed()
    assert len(parsed) >= _MIN_SOURCE_FILES, (
        f"only {len(parsed)} source files parsed under {SRC} -- the walk is broken, so "
        f"every 'nothing found' assertion below would pass vacuously"
    )
    control_seen = False
    offenders: list[str] = []
    for path, tree in parsed:
        rel = path.relative_to(SRC).as_posix()
        names = collect(tree)
        if _CONTROL_NAME in names:
            control_seen = True
        for hit in sorted(names & set(_REMOVED_NAMES)):
            offenders.append(f"{rel}: {hit}")
    return control_seen, offenders


def _files_naming(name: str) -> list[str]:
    """Every src/ file that binds or reads `name`."""
    out = []
    for path, tree in _parsed():
        if name in _names_in(tree):
            out.append(path.relative_to(SRC).as_posix())
    return sorted(out)


def test_the_deleted_v1_modules_are_gone() -> None:
    gone = [name for name in _DELETED_MODULES if (_PKG / name).exists()]
    assert not gone, f"{gone} still exists under {_PKG}"
    # Control: the directory survived the deletion, minus exactly these four files.
    assert (_PKG / _CONTROL_SIBLING).is_file(), (
        f"{_CONTROL_SIBLING} is missing too -- the whole intake package went, not just "
        "the v1 modules; this pin would then be testing an empty directory"
    )
    for mod in _DELETED_MODULES:
        dotted = f"aegis_ai.intake.{mod[:-3]}"
        assert importlib.util.find_spec(dotted) is None, f"{dotted} is still importable"


def test_no_source_file_names_a_removed_intake_name() -> None:
    control_seen, offenders = _scan(_names_in)
    assert control_seen, (
        f"the scan never saw {_CONTROL_NAME} -- it is not reading the tree, so the "
        "'no removed names' result below is meaningless"
    )
    assert not offenders, (
        "a removed v1 intake name is still referenced in src/: "
        f"{offenders}. If a live module needs one, it was not dead -- re-open "
        "DELEGATION.md §4 item 47 instead of re-adding the name here."
    )


def test_the_removed_names_are_no_longer_exported() -> None:
    intake = importlib.import_module("aegis_ai.intake")
    exported = set(getattr(intake, "__all__", ()))
    still = sorted(set(_REMOVED_EXPORTS) & exported)
    assert not still, f"aegis_ai.intake still exports {still}"
    for name in _REMOVED_EXPORTS:
        assert not hasattr(intake, name), f"aegis_ai.intake.{name} is still importable"
    # Control: the live surface is intact, so this is not "the package went empty".
    missing = sorted(set(_LIVE_EXPORTS) - exported)
    assert not missing, f"aegis_ai.intake stopped exporting the live names {missing}"


def test_the_live_routing_decision_is_untouched() -> None:
    """`intake.models.RoutingDecision` was a same-name twin of the live one.

    The live class is `aegis_ai.agents.profiles.models.RoutingDecision`, and it does
    **not** have `should_delegate_to_agent` -- that attribute belonged to the deleted
    twin. If this fails, the wrong `RoutingDecision` was removed.
    """
    live = importlib.import_module("aegis_ai.agents.profiles.models").RoutingDecision
    assert live.__module__ == "aegis_ai.agents.profiles.models"
    assert not hasattr(live, "should_delegate_to_agent"), (
        "the live RoutingDecision now carries the deleted twin's attribute -- the two "
        "classes were conflated"
    )
    from aegis_ai.agents.runtime.router import RoutingDecision as FromRouter

    assert FromRouter is live, (
        "agents.runtime.router no longer resolves RoutingDecision to the profiles model"
    )


def test_the_shared_name_is_not_treated_as_removed() -> None:
    """`RoutingDecision` is out of the bare-name scan because live code uses the name.

    The exclusion is only correct while that stays true, so this is its control: if
    the live class is ever renamed or dropped, `_REMOVED_NAMES` is stale and the pin
    must be re-derived rather than quietly widening.
    """
    assert _SHARED_NAME not in _REMOVED_NAMES, (
        f"{_SHARED_NAME} is shared with live code; putting it in the bare-name absence "
        "scan makes this pin fail on a correct tree"
    )
    users = _files_naming(_SHARED_NAME)
    assert users, (
        f"no src/ file names {_SHARED_NAME} any more -- if the live class moved, the "
        "exclusion above is stale; re-derive it instead of leaving it implicit"
    )
