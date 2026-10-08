"""Cycle 106 pin: `aegis_ai/reflection_loop.py` is *superseded*, not merely unwired -- and
the live successor is named here, so a later reader does not "finish the job" by wiring it.

`DELEGATION.md` §4 item 39's branch ② lists `reflection_loop.py` as a delete target but
defers its fate ("削除は別判断", on the premise that it is a ~700-line module). Measured
2026-10-08:

  * it is **146 lines**, not ~700 -- the premise of the caution is refuted;
  * it is imported by **nothing** under `src/` or `tests/` (only its own logger name and
    two pins' docstrings name it, which is not an import);
  * `ReflectionLoop` is **constructed nowhere**;
  * its only importers-in-reverse are `mind/emotion.py` and `mind/goals.py` -- those two
    exist *for it*, so its deletion is the precondition for theirs (cycle 105 kept them).

It is superseded by a **live** engine: `aegis_ai/reflection/reflection_engine.py`'s
`ReflectionEngine` (a real `reflect()`), constructed in the composition root
(`runtime.py`, passed as `reflection_engine=` to `AutonomousLoop`) and consumed at
`autonomous/autonomous_loop.py`. So the honest branch is neither "wire it" -- that would
create a *second* reflection implementation -- nor "delete it silently": it is a recorded
decision, and this pin fixes the record so the decision cannot rot.

⚠️ `ReflectionResult` is a **shared name**. `memory/memory_types.py` defines the live one
(re-exported by `memory/__init__.py`, imported by `reflection/reflection_engine.py`); the
dead module defines a *different* class with the same name. A bare-name absence scan over
it would fail on a correct tree -- the cycle-102/103/105 rule, met a third time.

Both scans walk `src/` **and** `tests/`, and skip **this file**, which has to name the
module in order to test for it.
"""

from __future__ import annotations

import ast
from pathlib import Path

_AI_SERVER = Path(__file__).resolve().parents[1]
_SRC = _AI_SERVER / "src"
_TESTS = _AI_SERVER / "tests"
_SELF = Path(__file__).resolve()

# The dead surface.
_DEAD_MODULE = "aegis_ai/reflection_loop.py"
_DEAD_DOTTED = "aegis_ai.reflection_loop"
_DEAD_CLASS = "ReflectionLoop"

# The live successor, and where it is wired.
_SUCCESSOR_MODULE = "aegis_ai/reflection/reflection_engine.py"
_SUCCESSOR_DOTTED = "aegis_ai.reflection.reflection_engine"
_SUCCESSOR_CLASS = "ReflectionEngine"
_COMPOSITION_ROOT = "aegis_ai/runtime.py"
_CONSUMER = "aegis_ai/autonomous/autonomous_loop.py"
_CONSUMED_METHOD = "reflect"

# A *shared* spelling: the dead module's `ReflectionResult` and the live
# `memory/memory_types.py` one are the same name, so only the live side can be asserted.
_SHARED_NAME = "ReflectionResult"
_LIVE_SHARED_DEFINITION = "aegis_ai/memory/memory_types.py"
_LIVE_REEXPORTER = "aegis_ai/memory/__init__.py"

# Files that *name* the dead module in prose (their docstrings) without importing it. If the
# scanner were text-based it would count these as importers -- so they are the control that
# proves it parses.
_PROSE_NAMERS = (
    "tests/test_mind_persistence_failures_are_named.py",
    "tests/test_mind_unwired_modules_are_gone.py",
)


def _scanned_files() -> list[Path]:
    return sorted(p for root in (_SRC, _TESTS) for p in root.rglob("*.py"))


def _relative(path: Path) -> str:
    """Source files are named from `src/` (`aegis_ai/...`), test files from the root.

    This matches the cycle-105 pin's convention, so a constant can be written the same
    way in either file -- and `tests/...` never collides with an `aegis_ai/...` name.
    """
    if path.is_relative_to(_SRC):
        return path.relative_to(_SRC).as_posix()
    return path.relative_to(_AI_SERVER).as_posix()


def _imported_modules(path: Path) -> set[str]:
    """Every module `path` brings into scope, as dotted names.

    `from aegis_ai import reflection_loop` imports the *submodule*, so it counts;
    `from aegis_ai.mind import desire` does not (the parent differs). `from . import x`
    (level 1) resolves against `aegis_ai`, since every source file here lives under it.
    """
    mods: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            mods.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level == 1 and not base:
                base = "aegis_ai"
            elif node.level:
                continue
            if base:
                mods.add(base)
            mods.update(f"{base}.{alias.name}" if base else alias.name for alias in node.names)
    return mods


def _importers_of(dotted: str) -> list[str]:
    found = []
    for module in _scanned_files():
        if module.resolve() == _SELF:
            continue  # this pin names the module in order to test for it
        if dotted in _imported_modules(module):
            found.append(_relative(module))
    return found


def _calls(name: str) -> list[str]:
    """Files that call `name(...)` -- as a bare name or as an attribute."""
    found = []
    for module in _scanned_files():
        if module.resolve() == _SELF:
            continue
        for node in ast.walk(ast.parse(module.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if (isinstance(func, ast.Name) and func.id == name) or (
                isinstance(func, ast.Attribute) and func.attr == name
            ):
                found.append(_relative(module))
                break
    return found


def _defined_names(path: Path) -> set[str]:
    """Names *bound* in `path`: class/def definitions, assignments, import aliases."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
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
    return [_relative(m) for m in _scanned_files() if name in _defined_names(m)]


def test_the_dead_module_is_imported_by_nothing() -> None:
    """The recorded claim: nothing under `src/` or `tests/` imports it."""
    assert _importers_of(_DEAD_DOTTED) == [], "reflection_loop.py has gained an importer"
    # Control: the file is still there, so the claim is about a live record, not a typo.
    assert (_SRC / _DEAD_MODULE).exists(), "the module is gone -- re-measure before trusting this pin"


def test_the_dead_class_is_constructed_nowhere() -> None:
    """Nor does anything build it."""
    assert _calls(_DEAD_CLASS) == [], "ReflectionLoop is now constructed somewhere"


def test_the_successor_is_live_and_consumed() -> None:
    """The positive half: this is *superseded*, so name the successor and its use.

    Without this the pin would be indistinguishable from "the feature was never written",
    and the tempting fix ("wire reflection_loop.py") would look correct.
    """
    assert _SUCCESSOR_CLASS in _defined_names(_SRC / _SUCCESSOR_MODULE)
    assert _importers_of(_SUCCESSOR_DOTTED), "the successor is no longer imported anywhere"
    assert _CONSUMER in _calls(_CONSUMED_METHOD), "the successor's reflect() is no longer called"


def test_the_successor_is_wired_from_the_composition_root() -> None:
    """`AutonomousLoop(...)` must still receive a `ReflectionEngine` -- not the dead class."""
    kwargs: dict[str, ast.expr] = {}
    for node in ast.walk(ast.parse((_SRC / _COMPOSITION_ROOT).read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "AutonomousLoop":
            kwargs = {kw.arg: kw.value for kw in node.keywords}
            break
    assert "reflection_engine" in kwargs, "the composition root no longer passes reflection_engine="
    value = kwargs["reflection_engine"]
    assert isinstance(value, ast.Call) and isinstance(value.func, ast.Name), "reflection_engine= is not a call"
    assert value.func.id == _SUCCESSOR_CLASS, f"reflection_engine= is built from {value.func.id!r}"


def test_the_result_name_is_shared_so_it_is_not_scanned_away() -> None:
    """`ReflectionResult` lives twice; the live copy is `memory/memory_types.py`.

    A pin that asserted this name absent from `src/` would fail on a correct tree, so what
    is held here is the *dead copy's own module* plus the live re-export.
    """
    definitions = _definitions_of(_SHARED_NAME)
    assert _LIVE_SHARED_DEFINITION in definitions, f"the live ReflectionResult moved: {definitions}"
    assert _DEAD_MODULE in definitions, f"the dead module no longer defines {_SHARED_NAME}: {definitions}"
    assert len(definitions) >= 2, "ReflectionResult is no longer a shared name -- re-adjudicate this pin"
    assert _SHARED_NAME in _defined_names(_SRC / _LIVE_REEXPORTER), "the live copy is no longer re-exported"


def test_the_scans_are_not_vacuous() -> None:
    """Controls: the same scanners find the live successor, and a prose mention is not an import."""
    assert _importers_of(_SUCCESSOR_DOTTED), "control: the importer scan finds nothing at all"
    assert _calls(_SUCCESSOR_CLASS), "control: the construction scan is blind"
    importers = set(_importers_of(_DEAD_DOTTED))
    for relative in _PROSE_NAMERS:
        path = _AI_SERVER / relative
        assert path.exists(), f"control: {relative} moved -- the prose-namer list is stale"
        assert "reflection_loop" in path.read_text(encoding="utf-8"), f"control: {relative} stopped naming it"
        assert relative not in importers, f"{relative} is counted as an importer -- the scan reads prose"
