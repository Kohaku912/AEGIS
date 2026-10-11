"""The two classes that own the mandate's wiring declare eight knobs nothing reads (item 111).

The owner's mandate is AEGIS's *resident, proactive support* and *self-improvement*
(「常駐されたユーザーの先回りサポートと自己改善」).  The two classes that would carry
it -- the interaction entry point and the autonomous loop -- each declare constructor
parameters that are stored on ``self`` and **read by no line of code**.

``interaction/router.py::InteractionRouter`` declares **14** constructor parameters;
**4** of them are the agent collaborators -- ``browser_executor`` -> ``self._browser``,
``research_agent`` -> ``self._research``, ``support_agent`` -> ``self._support``,
``self_dev_agent`` -> ``self._self_dev``.  None is ever read, and the composition root
that builds the router (``runtime.py::_build_runtime``) passes **7** keywords, none of
them one of the four.  No class named ``BrowserExecutor`` / ``ResearchAgent`` /
``SupportAgent`` / ``SelfDevAgent`` exists anywhere under ``src/``, so the parameters
cannot be supplied even if a caller wanted to.

``autonomous/autonomous_loop.py::AutonomousLoop`` declares **25** constructor
parameters; **4** are stored and never read -- ``settings_resolver`` ->
``self._settings_resolver`` (the *live* settings resolver), ``lesson_memory`` ->
``self._lesson`` (the self-improvement lesson store), ``desire_threshold`` ->
``self._desire_threshold`` and ``frustration_threshold`` -> ``self._frustration_threshold``.
Here the composition root **does** wire them (``runtime.py::_create_autonomous_loop``
passes ``settings_resolver``, ``lesson_memory`` and ``desire_threshold``), so the loop
receives a live-settings handle and a lesson store and ignores both.

**Why this is measured class-scoped, and why that matters.**  Three of the eight
attribute names collide with *live* attributes on other classes -- ``_browser`` is read
by ``MultimodalObservationService``, ``_settings_resolver`` by the LLM gateway and the
execution engine, ``_lesson`` by ``MemoryManager``.  A file-level or global attribute
scan therefore calls all three **read** and the census collapses to five.  The scan is
scoped to the *owning class*, and ``test_the_census_must_be_class_scoped`` drives that
boundary: a global scan is not merely coarser, it is **wrong** here.

The relationship to item 110: that item records the ``support_agent`` half of the router
plus the ``AutonomousSettings.support_agent_enabled`` settings flag.  This item is the
*census* -- all eight knobs across both classes -- and the settings flag remains item
110's own record.

Nothing here is fixed.  Reading any of these is a **behaviour change** (the loop would
start honouring live settings and lessons; the router would start handing an agent to
the plan path), so it is an owner decision, recorded in ``DELEGATION.md`` §4 item 111.
Each test fails the moment a real reader appears.
"""

from __future__ import annotations

import ast
from pathlib import Path

from test_ineffective_flags import _SRC

_ROUTER = _SRC / "aegis_ai" / "interaction" / "router.py"
_LOOP = _SRC / "aegis_ai" / "autonomous" / "autonomous_loop.py"
_RUNTIME = _SRC / "aegis_ai" / "runtime.py"

#: ``param -> self._attr`` for the four agent collaborators the router declares and
#: no code can supply.  Measured 2026-10-12 (item 111).
_ROUTER_DEAD: dict[str, str] = {
    "browser_executor": "_browser",
    "research_agent": "_research",
    "support_agent": "_support",
    "self_dev_agent": "_self_dev",
}

#: ``param -> self._attr`` for the four loop knobs the composition root wires and the
#: loop ignores (``frustration_threshold`` is not even wired).  Measured 2026-10-12.
_LOOP_DEAD: dict[str, str] = {
    "settings_resolver": "_settings_resolver",
    "lesson_memory": "_lesson",
    "desire_threshold": "_desire_threshold",
    "frustration_threshold": "_frustration_threshold",
}

#: The three dead attribute names that also name a *live* attribute on another class.
#: A global scan would call them read; the class-scoped scan must not.
_NAME_COLLISIONS: dict[str, str] = {
    "_browser": "aegis_ai/observation/observation_service.py",
    "_settings_resolver": "aegis_ai/llm/gateway.py",
    "_lesson": "aegis_ai/memory/memory_manager.py",
}

#: Classes that would implement the router's four collaborators. None exists.
_ROUTER_AGENT_CLASSES = (
    "BrowserExecutor",
    "ResearchAgent",
    "SupportAgent",
    "SelfDevAgent",
)

#: A parameter that *is* read, used as the positive control.
_LIVE_CONTROL = ("autonomous/autonomous_loop.py", "AutonomousLoop", "llm_provider", "_llm")


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _class(path: Path, name: str) -> ast.ClassDef:
    return next(
        n
        for n in ast.walk(_parse(path))
        if isinstance(n, ast.ClassDef) and n.name == name
    )


def _ctor(path: Path, name: str) -> tuple[list[str], dict[str, str]]:
    """(params, {attr: param}) for ``name``'s ``__init__``."""
    cls = _class(path, name)
    init = next(
        n
        for n in cls.body
        if isinstance(n, ast.FunctionDef) and n.name == "__init__"
    )
    params = [a.arg for a in init.args.args if a.arg != "self"]
    assigned: dict[str, str] = {}
    for node in ast.walk(init):
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Name)
            and node.value.id in params
        ):
            for target in node.targets:
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
    """Every ``.<attr>`` Load anywhere under ``src/``, as ``module:line``."""
    found: list[str] = []
    for path in sorted(_SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for node in ast.walk(_parse(path)):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == attr
                and isinstance(node.ctx, ast.Load)
            ):
                found.append(f"{path.relative_to(_SRC).as_posix()}:{node.lineno}")
    return found


def _call_keywords(path: Path, class_name: str) -> list[tuple[str, set[str]]]:
    """(enclosing function, keyword names) for every ``class_name(...)`` call."""
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


def _dead_params(path: Path, name: str) -> dict[str, str]:
    """``param -> attr`` for every stored parameter the class never reads."""
    _, assigned = _ctor(path, name)
    loads = _class_loads(path, name)
    return {param: attr for attr, param in assigned.items() if not loads.get(attr)}


# ── The census ────────────────────────────────────────────────────────────────


def test_the_router_declares_fourteen_parameters_and_the_dead_four():
    params, _ = _ctor(_ROUTER, "InteractionRouter")
    assert len(params) == 14, f"the router now declares {len(params)} parameters"
    assert _dead_params(_ROUTER, "InteractionRouter") == _ROUTER_DEAD, (
        "the router's stored-but-unread parameters changed. If a reader appeared, this "
        "pin has done its job -- clear the record and DELEGATION.md §4 item 111."
    )


def test_the_loop_declares_twentyfive_parameters_and_the_dead_four():
    params, _ = _ctor(_LOOP, "AutonomousLoop")
    assert len(params) == 25, f"the loop now declares {len(params)} parameters"
    assert _dead_params(_LOOP, "AutonomousLoop") == _LOOP_DEAD, (
        "the loop's stored-but-unread parameters changed. A new dead knob must be "
        "decided (wire it, delete it, or extend the record), not shipped unseen."
    )


def test_every_recorded_dead_param_is_stored_and_never_read():
    """The property, per site: ``self._X = <param>`` exists and ``self._X`` is never Loaded."""
    sites = [
        ("interaction/router.py", "InteractionRouter", attr, param)
        for param, attr in _ROUTER_DEAD.items()
    ] + [
        ("autonomous/autonomous_loop.py", "AutonomousLoop", attr, param)
        for param, attr in _LOOP_DEAD.items()
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
            f"waiting for. Clear the record (this file and DELEGATION.md §4 item 111)."
        )


def test_the_census_must_be_class_scoped():
    """Control: three of the eight names collide with a *live* attribute elsewhere.

    A global scan would call ``_browser``, ``_settings_resolver`` and ``_lesson`` read
    and report five dead knobs instead of eight. This drives the boundary: each of the
    three must have a global Load **outside** its owning module, which is exactly what
    makes the class scope load-bearing rather than a stylistic choice.
    """
    for attr, live_module in _NAME_COLLISIONS.items():
        global_hits = _global_loads(attr)
        assert global_hits, (
            f"'{attr}' no longer has any global Load -- the collision that justified the "
            "class-scoped scan is gone; re-derive this pin."
        )
        outside = [h for h in global_hits if live_module in h]
        assert outside, (
            f"'{attr}' is no longer read in {live_module}; the recorded collision moved. "
            f"global hits: {global_hits}"
        )


def test_a_live_parameter_is_not_in_the_dead_set():
    """Control: the scan can tell a read parameter from an unread one."""
    rel, cls, param, attr = _LIVE_CONTROL
    path = _SRC / "aegis_ai" / rel
    loads = _class_loads(path, cls).get(attr, [])
    assert loads, f"the control {cls}.{attr} is no longer read -- the scan is blind"
    assert param not in _LOOP_DEAD and attr not in _LOOP_DEAD.values(), (
        f"the control {param!r} was added to the dead record"
    )


# ── The wiring that does not exist ────────────────────────────────────────────


def test_the_router_call_site_supplies_none_of_the_four():
    """``_build_runtime`` builds the router with seven keywords, none of the four."""
    calls = _call_keywords(_RUNTIME, "InteractionRouter")
    assert len(calls) == 1, f"expected one InteractionRouter call in src/, got {len(calls)}"
    scope, keywords = calls[0]
    assert scope == "_build_runtime", f"the router is now built in {scope!r}"
    assert keywords == {
        "llm_provider",
        "context_builder",
        "capability_catalog",
        "capability_retriever",
        "tool_broker",
        "audit_log",
        "settings_store",
    }, f"the router's call-site keywords changed: {sorted(keywords)}"
    supplied = set(_ROUTER_DEAD) & keywords
    assert supplied == set(), (
        f"a call site now passes {sorted(supplied)}. If the agents were wired "
        "deliberately, clear this record; if not, remove the keywords again."
    )


def test_the_loop_call_site_supplies_three_of_the_four():
    """The composition root *does* wire three of the loop's four dead knobs.

    That asymmetry is the finding: ``settings_resolver``, ``lesson_memory`` and
    ``desire_threshold`` are handed to the loop and ignored; ``frustration_threshold``
    is not even wired. So "the composition root forgot" is not the whole story.
    """
    calls = _call_keywords(_RUNTIME, "AutonomousLoop")
    assert len(calls) == 1, f"expected one AutonomousLoop call in src/, got {len(calls)}"
    scope, keywords = calls[0]
    assert scope == "_create_autonomous_loop", f"the loop is now built in {scope!r}"
    wired = set(_LOOP_DEAD) & keywords
    assert wired == {"settings_resolver", "lesson_memory", "desire_threshold"}, (
        f"the loop's call site now wires {sorted(wired)} of its dead knobs (expected "
        f"the three). keywords: {sorted(keywords)}"
    )


def test_no_class_implements_the_four_router_agents():
    """The four parameters cannot be supplied: no class implements any of them."""
    found: list[str] = []
    for path in sorted(_SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for node in ast.walk(_parse(path)):
            if isinstance(node, ast.ClassDef) and node.name in _ROUTER_AGENT_CLASSES:
                found.append(f"{path.relative_to(_SRC).as_posix()}:{node.name}")
    assert found == [], (
        f"a class now implements one of the router's collaborators: {found}. If it was "
        "wired deliberately, clear the record; otherwise this parameter is no longer "
        "unsuppliable and the reason above must be re-derived."
    )
