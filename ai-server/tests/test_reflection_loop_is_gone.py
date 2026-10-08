"""Cycle 107 pin: `aegis_ai/reflection_loop.py` is **gone** -- and the live engine that
replaced it is still defined, imported, consumed and wired.

`DELEGATION.md` §4 item 39. Cycle 106 *measured* this module instead of deleting it, because
the row deferred its fate on the premise that it was a ~700-line file. Measurement refuted
the premise: 146 lines, imported by nothing under `src/` or `tests/`, its class constructed
nowhere. And it was *superseded*, not merely unwired -- the live successor is
`reflection/reflection_engine.py::ReflectionEngine`, constructed in the composition root
(`runtime.py`, passed as `reflection_engine=` to `AutonomousLoop`) and consumed at
`autonomous/autonomous_loop.py`. So "wire it up" would have created a *second* reflection
implementation; deleting it was the honest branch.

Cycle 107 then deleted it, together with the two `mind/` modules whose only importer it was
(`mind/emotion.py`, `mind/goals.py` -- pinned by `test_mind_unwired_modules_are_gone.py`).

The **positive half** is kept from the cycle-106 pin, and it is the point of this file: a
pin that only asserted the absences could not be told apart from "the feature was never
written", so it could not refute the tempting repair. Four assertions do that here -- the
successor is *defined*, *imported*, *consumed*, and *wired from the composition root*.

⚠️ `ReflectionResult` is a **shared name**. The deleted module defined one; the live
`memory/memory_types.py` defines another, re-exported by `memory/__init__.py` and imported
by `reflection/reflection_engine.py`. A bare-name absence scan over it would fail on a
correct tree -- the cycle-102/103/105 rule, met a **fourth** time -- so the live copy is
pinned **present** (by equality, now that the dead twin is gone).

Both scans walk `src/` **and** `tests/`, and skip **this file**, which has to name the
module in order to test for it.
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
from pathlib import Path

import pytest

_AI_SERVER = Path(__file__).resolve().parents[1]
_SRC = _AI_SERVER / "src"
_TESTS = _AI_SERVER / "tests"
_SELF = Path(__file__).resolve()

# The dead surface.
_DEAD_MODULE = "aegis_ai/reflection_loop.py"
_DEAD_DOTTED = "aegis_ai.reflection_loop"
_DEAD_CLASS = "ReflectionLoop"

# The live successor, and where it is wired.
_SUBJECT_MODULE = "aegis_ai/reflection/reflection_engine.py"
_SUBJECT_DOTTED = "aegis_ai.reflection.reflection_engine"
_SUBJECT_CLASS = "ReflectionEngine"
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

    This matches the sibling pins' convention, so a constant can be written the same way in
    either file -- and `tests/...` never collides with an `aegis_ai/...` name.
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


def _definition_sites(name: str) -> list[str]:
    """Files that *declare* `name` -- class/def/assignment, **not** an import alias.

    `_defined_names` counts import bindings too (it is used to ask "is this name in scope
    here"), and a re-export is exactly that: `memory/__init__.py` and
    `reflection/reflection_engine.py` both `import` `ReflectionResult` without declaring it.
    A claim about *where a class is defined* needs this stricter predicate -- otherwise the
    equality below would fail on a correct tree (measured: it did, on the first run).
    """
    found: list[str] = []
    for module in _scanned_files():
        for node in ast.walk(ast.parse(module.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == name:
                    found.append(_relative(module))
                    break
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(t, ast.Name) and t.id == name for t in targets):
                    found.append(_relative(module))
                    break
    return found


def test_the_dead_module_is_gone() -> None:
    """The file, and the import machinery, must both agree."""
    assert not (_SRC / _DEAD_MODULE).exists(), "reflection_loop.py is back"
    assert importlib.util.find_spec(_DEAD_DOTTED) is None, "it still has an import spec"
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(_DEAD_DOTTED)
    # Control: the walk reaches the directory that used to hold it.
    assert (_SRC / "aegis_ai" / "runtime.py").exists(), "control: the src tree moved"


def test_the_dead_class_is_defined_nowhere() -> None:
    """Nor does anything re-declare it under a surviving module."""
    assert _definition_sites(_DEAD_CLASS) == [], "ReflectionLoop is defined again"


def test_nothing_imports_the_dead_module() -> None:
    """No surviving file may name its dotted path in an import."""
    assert _importers_of(_DEAD_DOTTED) == [], "reflection_loop.py has gained an importer"


def test_the_successor_is_live_and_consumed() -> None:
    """The positive half: this was *superseded*, so name the successor and its use.

    Without this the pin would be indistinguishable from "the feature was never written",
    and the tempting fix ("wire reflection_loop.py") would look correct.
    """
    assert _SUBJECT_CLASS in _defined_names(_SRC / _SUBJECT_MODULE)
    assert _importers_of(_SUBJECT_DOTTED), "the successor is no longer imported anywhere"
    assert _CONSUMER in _calls(_CONSUMED_METHOD), "the successor's reflect() is no longer called"


def test_the_successor_is_wired_from_the_composition_root() -> None:
    """`AutonomousLoop(...)` must still receive a `ReflectionEngine`."""
    kwargs: dict[str, ast.expr] = {}
    for node in ast.walk(ast.parse((_SRC / _COMPOSITION_ROOT).read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "AutonomousLoop":
            kwargs = {kw.arg: kw.value for kw in node.keywords}
            break
    assert "reflection_engine" in kwargs, "the composition root no longer passes reflection_engine="
    value = kwargs["reflection_engine"]
    assert isinstance(value, ast.Call) and isinstance(value.func, ast.Name), "reflection_engine= is not a call"
    assert value.func.id == _SUBJECT_CLASS, f"reflection_engine= is built from {value.func.id!r}"


def test_the_result_name_keeps_its_live_definition() -> None:
    """`ReflectionResult` lived twice; with the dead twin gone the live copy is *unique*.

    Pinned as an equality, which is stronger than the cycle-106 form (a membership test):
    it fails both if the live copy moves *and* if a third one appears.
    """
    assert _definition_sites(_SHARED_NAME) == [_LIVE_SHARED_DEFINITION], (
        f"the live ReflectionResult moved: {_definition_sites(_SHARED_NAME)}"
    )
    assert _SHARED_NAME in _defined_names(_SRC / _LIVE_REEXPORTER), "the live copy is no longer re-exported"


def test_the_scans_are_not_vacuous() -> None:
    """Controls: the same scanners find the live successor, and a prose mention is not an import."""
    assert _importers_of(_SUBJECT_DOTTED), "control: the importer scan finds nothing at all"
    assert _calls(_SUBJECT_CLASS), "control: the construction scan is blind"
    assert _definitions_of(_SUBJECT_CLASS), "control: the definition scan is blind"
    importers = set(_importers_of(_DEAD_DOTTED))
    for relative in _PROSE_NAMERS:
        path = _AI_SERVER / relative
        assert path.exists(), f"control: {relative} moved -- the prose-namer list is stale"
        assert "reflection_loop" in path.read_text(encoding="utf-8"), f"control: {relative} stopped naming it"
        assert relative not in importers, f"{relative} is counted as an importer -- the scan reads prose"
