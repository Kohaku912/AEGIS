"""The three *execution* classes of the mandate declare eight knobs that are wired and ignored (item 112).

Item 111 recorded the mandate's two **entry** classes -- the interaction router and the
autonomous loop -- each declaring stored-but-unread constructor parameters, and noted
that the router's four could not even be supplied.  This item is the sibling census one
layer down: the three classes that actually **execute** the mandate's work.

``autonomous/planner.py::AutonomousPlanner`` declares **6** parameters; **2** are stored
and never read -- ``memory_store`` -> ``self._memory`` and ``policy_engine`` ->
``self._policy``.  Its only call site (``autonomous/autonomous_loop.py``, inside
``AutonomousLoop._execute_tasks``) passes **all six**, both dead ones included.  So the
planner receives a memory store and a policy engine and reads *neither*: it rebuilds a
memory context from disk via ``_memory_root()`` and has no policy code at all -- while its
class docstring advertises "safety enforcement".

``autonomous/spontaneous_observation.py::SpontaneousObservationSystem`` -- the resident,
self-initiated observer -- declares **13** parameters; **4** are stored and never read --
``llm`` -> ``self._llm``, ``broker`` -> ``self._broker``, ``person_memory`` ->
``self._person``, ``semantic_memory`` -> ``self._semantic``.  All four are keys of the
``observation_kwargs`` literal that ``runtime.py::_create_autonomous_loop`` builds, so the
observer is handed an LLM, a tool broker and two memory stores and uses none of them.

``autonomous/curiosity_exploration.py::CuriosityDrivenExplorationSystem`` declares **11**
parameters; **2** are stored and never read -- ``association_memory`` ->
``self._association`` and ``person_memory`` -> ``self._person``.  Its live construction
site passes both dead ones among ten keywords.

**Why the census must be class-scoped, and how sharply.**  Every one of the eight dead
attribute names is read *somewhere else in the repo* -- ``self._llm`` is Loaded 84 times,
``self._semantic`` 41, ``self._broker`` 37, ``self._memory`` 19, ``self._person`` 9,
``self._policy`` 7, ``self._association`` 5 -- but **never inside its owning class**.
A global scan answers "read" for all eight and reports **zero** dead knobs here.  The scan
is scoped to the owning class.

**The per-class boundary is not stylistic -- it is testable.**  ``_llm``, ``_broker`` and
``_semantic`` are **dead** in ``SpontaneousObservationSystem`` and **live** in
``CuriosityDrivenExplorationSystem`` (and ``_llm``/``_broker`` live in ``AutonomousPlanner``
too).  The same name, the same file family, opposite verdicts.  That is the control that a
name-keyed or file-keyed census cannot pass.

The relationship to item 111: 111 is the two *entry* classes and the router's
*unsuppliable* agents.  This item is the three *execution* classes and their
*wired-but-ignored* collaborators -- a strictly stronger shape, since the composition root
supplies every one of the eight.

Nothing here is fixed.  Reading any of these is a **behaviour change** (the planner would
start honouring the injected policy engine; the observer would start using the LLM and the
semantic/person stores), so it is an owner decision, recorded in ``DELEGATION.md`` §4 item
112.  Each test fails the moment a real reader appears.
"""

from __future__ import annotations

import ast
from pathlib import Path

from test_ineffective_flags import _SRC

_PLANNER = _SRC / "aegis_ai" / "autonomous" / "planner.py"
_OBSERVATION = _SRC / "aegis_ai" / "autonomous" / "spontaneous_observation.py"
_CURIOSITY = _SRC / "aegis_ai" / "autonomous" / "curiosity_exploration.py"
_LOOP = _SRC / "aegis_ai" / "autonomous" / "autonomous_loop.py"
_RUNTIME = _SRC / "aegis_ai" / "runtime.py"

#: ``(relative module, class, {param -> self._attr})`` for the three execution classes.
#: Measured 2026-10-12 (item 112).
_TARGETS: tuple[tuple[str, str, dict[str, str]], ...] = (
    (
        "autonomous/planner.py",
        "AutonomousPlanner",
        {"memory_store": "_memory", "policy_engine": "_policy"},
    ),
    (
        "autonomous/spontaneous_observation.py",
        "SpontaneousObservationSystem",
        {
            "llm": "_llm",
            "broker": "_broker",
            "person_memory": "_person",
            "semantic_memory": "_semantic",
        },
    ),
    (
        "autonomous/curiosity_exploration.py",
        "CuriosityDrivenExplorationSystem",
        {"association_memory": "_association", "person_memory": "_person"},
    ),
)

#: Declared parameter count per class, in the same order as ``_TARGETS``.
_DECLARED: dict[str, int] = {
    "AutonomousPlanner": 6,
    "SpontaneousObservationSystem": 13,
    "CuriosityDrivenExplorationSystem": 11,
}

#: Attribute names that are **dead in one class and live in another** -- the per-class
#: isolation control.  ``attr -> (dead_in, live_in)``.
_ISOLATION: dict[str, tuple[str, str]] = {
    "_llm": ("SpontaneousObservationSystem", "CuriosityDrivenExplorationSystem"),
    "_broker": ("SpontaneousObservationSystem", "CuriosityDrivenExplorationSystem"),
    "_semantic": ("SpontaneousObservationSystem", "CuriosityDrivenExplorationSystem"),
}

#: One parameter per class that *is* read, used as the positive control.
_LIVE_CONTROL: tuple[tuple[str, str, str, str], ...] = (
    ("autonomous/planner.py", "AutonomousPlanner", "llm_provider", "_llm"),
    ("autonomous/spontaneous_observation.py", "SpontaneousObservationSystem", "desire_system", "_desire"),
    ("autonomous/curiosity_exploration.py", "CuriosityDrivenExplorationSystem", "tool_broker", "_broker"),
)


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _class(path: Path, name: str) -> ast.ClassDef:
    return next(
        n for n in ast.walk(_parse(path)) if isinstance(n, ast.ClassDef) and n.name == name
    )


def _ctor(path: Path, name: str) -> tuple[list[str], dict[str, str]]:
    """(params, {attr: param}) for ``name``'s ``__init__``."""
    cls = _class(path, name)
    init = next(
        n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"
    )
    a = init.args
    names = [x.arg for x in a.posonlyargs] + [x.arg for x in a.args] + [x.arg for x in a.kwonlyargs]
    params = [n for n in names if n != "self"]
    assigned: dict[str, str] = {}
    for node in ast.walk(init):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.value, ast.Name)
            and node.value.id in params
        ):
            target = node.targets[0]
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                assigned[target.attr] = node.value.id
    return params, assigned


def _class_loads(path: Path, name: str) -> dict[str, list[int]]:
    """``self.<attr>`` Load line numbers, scoped to the class body."""
    loads: dict[str, list[int]] = {}
    for node in ast.walk(_class(path, name)):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
            and isinstance(node.ctx, ast.Load)
        ):
            loads.setdefault(node.attr, []).append(node.lineno)
    return loads


def _global_loads(attr: str) -> list[str]:
    """Every ``self.<attr>`` Load anywhere under ``src/``, as ``module:line``."""
    found: list[str] = []
    for path in sorted(_SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for node in ast.walk(_parse(path)):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == attr
                and isinstance(node.value, ast.Name)
                and node.value.id == "self"
                and isinstance(node.ctx, ast.Load)
            ):
                found.append(f"{path.relative_to(_SRC).as_posix()}:{node.lineno}")
    return found


def _dead_params(path: Path, name: str) -> dict[str, str]:
    """``param -> attr`` for every stored parameter the class never reads."""
    _, assigned = _ctor(path, name)
    loads = _class_loads(path, name)
    return {param: attr for attr, param in assigned.items() if not loads.get(attr)}


def _call_keywords(path: Path, class_name: str) -> list[tuple[str, set[str]]]:
    """(enclosing function, keyword names) for every ``class_name(...)`` call in ``path``."""
    tree = _parse(path)
    calls: list[tuple[str, set[str]]] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == class_name
        ):
            scope = next(
                (
                    n.name
                    for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.lineno <= node.lineno <= (n.end_lineno or n.lineno)
                ),
                "<module>",
            )
            calls.append((scope, {kw.arg for kw in node.keywords if kw.arg}))
    return calls


def _dict_literal_keys(path: Path, varname: str) -> set[str]:
    """String keys of ``varname = { ... }`` (a literal, not a comprehension) in ``path``."""
    for node in ast.walk(_parse(path)):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == varname
            and isinstance(node.value, ast.Dict)
        ):
            return {k.value for k in node.value.keys if isinstance(k, ast.Constant)}
    return set()


# ── The census ────────────────────────────────────────────────────────────────


def test_each_execution_class_declares_its_recorded_parameter_count():
    for rel, cls, _ in _TARGETS:
        params, _ = _ctor(_SRC / "aegis_ai" / rel, cls)
        assert len(params) == _DECLARED[cls], (
            f"{cls} now declares {len(params)} parameters (recorded {_DECLARED[cls]}). "
            "A new parameter must be decided (wire it, delete it, or extend the record)."
        )


def test_each_execution_class_has_exactly_its_recorded_dead_params():
    for rel, cls, dead in _TARGETS:
        measured = _dead_params(_SRC / "aegis_ai" / rel, cls)
        assert measured == dead, (
            f"{cls}'s stored-but-unread parameters changed: {measured!r}. If a reader "
            "appeared, this pin has done its job -- clear the record and DELEGATION.md "
            "§4 item 112."
        )


def test_every_recorded_dead_param_is_stored_and_never_read():
    """The property, per site: ``self._X = <param>`` exists and ``self._X`` is never Loaded."""
    sites = [
        (rel, cls, attr, param)
        for rel, cls, dead in _TARGETS
        for param, attr in dead.items()
    ]
    assert len(sites) == 8
    for rel, cls, attr, param in sites:
        path = _SRC / "aegis_ai" / rel
        _, assigned = _ctor(path, cls)
        assert assigned.get(attr) == param, (
            f"{cls}.{attr} is no longer assigned from {param!r} (now {assigned.get(attr)!r})"
        )
        loads = _class_loads(path, cls).get(attr, [])
        assert loads == [], (
            f"{cls}.{attr} is now read at lines {loads} -- the reader this record was "
            f"waiting for. Clear the record (this file and DELEGATION.md §4 item 112)."
        )


# ── The controls ──────────────────────────────────────────────────────────────


def test_the_census_must_be_class_scoped():
    """Control: every dead name is read *elsewhere* in the repo.

    A global attribute scan answers "read" for all eight and reports zero dead knobs
    here. This drives the boundary: each dead attribute must have a ``self.<attr>``
    Load **outside** its owning module, which is exactly what makes the class scope
    load-bearing rather than a stylistic choice.
    """
    for rel, cls, dead in _TARGETS:
        for attr in dead.values():
            global_hits = _global_loads(attr)
            outside = [h for h in global_hits if not h.startswith(rel + ":")]
            assert outside, (
                f"'{attr}' (dead in {cls}) no longer has a global Load outside {rel} -- "
                f"the collision that justified the class-scoped scan is gone; re-derive "
                f"this pin. global hits: {global_hits}"
            )


def test_the_same_attribute_is_dead_in_one_class_and_live_in_another():
    """Control: the verdict is per-class, not per-name.

    ``_llm``, ``_broker`` and ``_semantic`` are dead in ``SpontaneousObservationSystem``
    and live in ``CuriosityDrivenExplorationSystem``. A name-keyed or file-keyed census
    cannot produce two opposite verdicts for the same attribute; only a class-scoped one
    can.
    """
    by_name = {cls: (rel, cls) for rel, cls, _ in _TARGETS}
    for attr, (dead_in, live_in) in _ISOLATION.items():
        rel_dead, cls_dead = by_name[dead_in]
        rel_live, cls_live = by_name[live_in]
        assert _class_loads(_SRC / "aegis_ai" / rel_dead, cls_dead).get(attr, []) == [], (
            f"control broken: {cls_dead}.{attr} is now read -- it was recorded dead"
        )
        live = _class_loads(_SRC / "aegis_ai" / rel_live, cls_live).get(attr, [])
        assert live, (
            f"control broken: {cls_live}.{attr} is no longer read -- the isolation pair "
            f"({cls_dead} dead / {cls_live} live) cannot be demonstrated"
        )


def test_a_live_parameter_is_not_in_the_dead_set():
    """Control: the scan can tell a read parameter from an unread one, in every class."""
    for rel, cls, param, attr in _LIVE_CONTROL:
        loads = _class_loads(_SRC / "aegis_ai" / rel, cls).get(attr, [])
        assert loads, f"the control {cls}.{attr} is no longer read -- the scan is blind"
        dead = next(dead for r, c, dead in _TARGETS if c == cls)
        assert param not in dead and attr not in dead.values(), (
            f"the control {param!r} was added to {cls}'s dead record"
        )


# ── The wiring that is supplied and ignored ───────────────────────────────────


def test_the_live_call_sites_supply_every_dead_param():
    """The composition root hands each execution class *all* of its dead knobs.

    This is the shape that distinguishes item 112 from item 111: there the router's four
    agents could not be supplied at all; here every one of the eight is passed in.
    """
    # The planner: one call site, six keywords, both dead params among them.
    planner_calls = _call_keywords(_LOOP, "AutonomousPlanner")
    assert len(planner_calls) == 1, f"expected one AutonomousPlanner call, got {planner_calls}"
    _, planner_kw = planner_calls[0]
    planner_dead = next(dead for _, c, dead in _TARGETS if c == "AutonomousPlanner")
    assert set(planner_dead) <= planner_kw, (
        f"the planner call site no longer supplies {sorted(set(planner_dead) - planner_kw)}; "
        f"keywords: {sorted(planner_kw)}"
    )

    # The curiosity system: one call site, both dead params among its keywords.
    curiosity_calls = _call_keywords(_RUNTIME, "CuriosityDrivenExplorationSystem")
    assert len(curiosity_calls) == 1, f"expected one curiosity call, got {curiosity_calls}"
    _, curiosity_kw = curiosity_calls[0]
    curiosity_dead = next(
        dead for _, c, dead in _TARGETS if c == "CuriosityDrivenExplorationSystem"
    )
    assert set(curiosity_dead) <= curiosity_kw, (
        f"the curiosity call site no longer supplies "
        f"{sorted(set(curiosity_dead) - curiosity_kw)}; keywords: {sorted(curiosity_kw)}"
    )

    # The observer: built from **observation_kwargs, so the dict literal is the supply.
    obs_keys = _dict_literal_keys(_RUNTIME, "observation_kwargs")
    obs_dead = next(dead for _, c, dead in _TARGETS if c == "SpontaneousObservationSystem")
    assert obs_keys, "no observation_kwargs dict literal found in runtime.py"
    assert set(obs_dead) <= obs_keys, (
        f"observation_kwargs no longer contains {sorted(set(obs_dead) - obs_keys)}; "
        f"keys: {sorted(obs_keys)}"
    )


def test_the_planner_docstring_promises_safety_enforcement():
    """The planner advertises "safety enforcement"; its only policy input is dead.

    The claim is in the class docstring; the backing is ``policy_engine`` ->
    ``self._policy``, which is stored and never read. This records the gap without
    asserting what enforcement (if any) happens elsewhere.
    """
    doc = ast.get_docstring(_class(_PLANNER, "AutonomousPlanner")) or ""
    assert "safety enforcement" in doc, (
        f"the planner docstring no longer claims 'safety enforcement' (now: {doc!r}); "
        "if the claim moved, move this record with it"
    )
    assert "policy_engine" in _dead_params(_PLANNER, "AutonomousPlanner"), (
        "policy_engine is now read -- the docstring claim has backing; clear this record"
    )
