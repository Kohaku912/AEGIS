"""Cycle 105 pin: the three unwired `mind/` modules are gone — and the *live* names they
shadowed are not.

`DELEGATION.md` §4 item 39 recorded four `mind/` classes that nothing constructs
(`Desire`, `Emotion`, `GoalManager`, `SocialIntelligence`, plus `priorities.py`'s
`PriorityEngine`). Measurement for this cycle narrowed the *executable* half: three of
those modules had no importer at all outside `mind/__init__.py`, so deleting them needs
no other decision.

  * `mind/desire.py`             -- no importer anywhere in `src/` or `tests/`
  * `mind/priorities.py`         -- imported by nothing, not even a test
  * `mind/social_intelligence.py` -- imported only by the persistence family's own pin

`mind/emotion.py` and `mind/goals.py` are deliberately **not** here: their only importer
is `reflection_loop.py`, which the row defers as a separate decision (measured 2026-10-08:
146 lines, itself imported by nothing). They stay until that call is made.

Two name traps were measured, and the pin keys on them rather than around them:

  * `Desire` is **not** a removed name. `desire/desire_system.py` defines the live legacy
    alias `Desire = DesireDimension`, so a bare-name absence scan over `Desire` fails on a
    correct tree (the cycle-102/103 rule: a *shared* name's live side must be pinned, not
    scanned). `Desire` is therefore asserted **present** in `src/` and absent only from
    `mind/`.
  * `SocialIntelligence` is unique to the deleted module, and the live sibling is spelled
    differently (`social/intelligence.py`'s `SocialIntelligenceSystem`). That sibling is
    asserted present as the control that the deletion took the *dead* one.

The scan for the removed dotted paths skips **this file**, which has to name them in order
to test for them -- the same "a comment that names the removed artefact re-adds it to a
namer census" trap, met from the inside.
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
from pathlib import Path

import pytest

import aegis_ai.mind as mind_pkg

_AI_SERVER = Path(__file__).resolve().parents[1]
_SRC = _AI_SERVER / "src"
_MIND = _SRC / "aegis_ai" / "mind"
_SELF = Path(__file__).resolve()

# The declared population: every module this cycle removed.
_REMOVED_MODULES = ("desire.py", "priorities.py", "social_intelligence.py")
# The dotted names, for the import checks and the tree-wide scan.
_REMOVED_DOTTED = (
    "aegis_ai.mind.desire",
    "aegis_ai.mind.priorities",
    "aegis_ai.mind.social_intelligence",
)
# Names unique to the removed modules -- safe to assert *absent* from `src/`.
_REMOVED_UNIQUE_NAMES = ("DesireEntry", "PriorityEngine", "PriorityScore", "SocialIntelligence", "SocialState")
# A *shared* spelling: the removed `mind/desire.py::Desire` and the live legacy alias in
# `desire/desire_system.py` are the same name, so only the live side can be asserted.
_SHARED_NAME = "Desire"
_LIVE_SHARED_DEFINITION = "aegis_ai/desire/desire_system.py"
# The live sibling of the deleted `SocialIntelligence` (a different spelling, so the
# absence scan for the dead name does not touch it).
_LIVE_SIBLING_DEFINITION = "aegis_ai/social/intelligence.py"
_CONTROL_LIVE_SIBLING = "SocialIntelligenceSystem"
# Controls: a surviving class, and the re-exports `mind/__init__.py` kept.
_CONTROL_NAME = "Identity"
_KEPT_REEXPORTS = ("Emotion", "Goal", "GoalManager", "GoalStatus", "GoalType")
# The surviving modules (11 - 3). Enumerated, not sampled.
_EXPECTED_MODULE_COUNT = 8
_SURVIVING_MODULE = "identity.py"


def _defined_names(path: Path) -> set[str]:
    """Names *bound* in `path`: class/def definitions, assignments, and import aliases.

    Parsed, not grepped -- a name inside a comment or a docstring is not a binding, which
    is the whole point (the live alias's comment says "old code may import ``Desire``").
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.ImportFrom):
            names.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            names.update((alias.asname or alias.name).split(".")[0] for alias in node.names)
    return names


def _definitions_of(name: str) -> list[str]:
    """Every `src/` file that binds `name`, as `src/`-relative paths, sorted."""
    found: list[str] = []
    for module in sorted(_SRC.rglob("*.py")):
        if name in _defined_names(module):
            found.append(module.relative_to(_SRC).as_posix())
    return found


def test_the_three_modules_are_gone() -> None:
    """The declared population, enumerated: these three files, and no others."""
    for name in _REMOVED_MODULES:
        assert not (_MIND / name).exists(), f"{name} is back -- it was deleted in cycle 105"
    # Control: the walk reaches the directory at all.
    assert (_MIND / _SURVIVING_MODULE).exists(), "control: the surviving module is missing"
    assert len(sorted(_MIND.glob("*.py"))) == _EXPECTED_MODULE_COUNT


def test_the_package_cannot_resolve_them() -> None:
    """Behavioural half: the import machinery agrees, not just the filesystem."""
    for dotted in _REMOVED_DOTTED:
        assert importlib.util.find_spec(dotted) is None, f"{dotted} still has an import spec"
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(dotted)
    # Control: a surviving sibling still resolves, and to the file we mean.
    spec = importlib.util.find_spec("aegis_ai.mind.identity")
    assert spec is not None and spec.origin is not None
    assert Path(spec.origin).name == _SURVIVING_MODULE


def test_the_removed_classes_are_defined_nowhere_in_src() -> None:
    """The unique names must be bound by nothing, anywhere under `src/`."""
    for name in _REMOVED_UNIQUE_NAMES:
        found = _definitions_of(name)
        assert found == [], f"{name} is still defined in src/: {found}"


def test_the_shared_name_keeps_its_live_definition() -> None:
    """`Desire` is a *shared* spelling: pin the live side, do not scan it away.

    `desire/desire_system.py` defines `Desire = DesireDimension` for old callers. The
    deletion removed the `mind/` one; a pin that only counted occurrences would call this
    file a regression.
    """
    assert _definitions_of(_SHARED_NAME) == [_LIVE_SHARED_DEFINITION]
    in_mind = [p.name for p in sorted(_MIND.glob("*.py")) if _SHARED_NAME in _defined_names(p)]
    assert in_mind == [], f"mind/ still binds {_SHARED_NAME}: {in_mind}"
    # Control: the live sibling of the deleted `SocialIntelligence` is still there.
    assert _LIVE_SIBLING_DEFINITION in _definitions_of(_CONTROL_LIVE_SIBLING)


def test_the_package_no_longer_reexports_them() -> None:
    """`mind/__init__.py` re-exported all three; the names must be gone from the package."""
    for name in (*_REMOVED_UNIQUE_NAMES, _SHARED_NAME):
        assert not hasattr(mind_pkg, name), f"aegis_ai.mind still re-exports {name}"
    # Controls: what was kept still resolves.
    assert hasattr(mind_pkg, _CONTROL_NAME), "control: Identity is no longer re-exported"
    for name in _KEPT_REEXPORTS:
        assert hasattr(mind_pkg, name), f"aegis_ai.mind lost the surviving re-export {name}"


def test_no_source_or_test_imports_a_removed_module() -> None:
    """The dotted paths, over the whole tree -- with a subject for the scan."""
    seen = 0
    for root in (_SRC, _AI_SERVER / "tests"):
        for module in sorted(root.rglob("*.py")):
            if module.resolve() == _SELF:
                continue  # this pin names them in order to test for them
            text = module.read_text(encoding="utf-8")
            for dotted in _REMOVED_DOTTED:
                assert dotted not in text, f"{module.relative_to(_AI_SERVER).as_posix()} still names {dotted}"
            if "aegis_ai.mind.identity" in text:
                seen += 1
    # Control: the scan's needle matches on a correct tree.
    assert seen >= 1, "control: no file names a surviving mind module, so the scan proves nothing"
