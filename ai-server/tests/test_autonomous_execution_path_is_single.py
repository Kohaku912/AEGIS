"""There are two autonomous execution paths, and only one of them runs (B-3, §5.1).

``docs/self-development.md`` opens with an architecture diagram whose **entry point** is
``AutonomousController``::

    ┌─────────────────────────────────────────────────────────┐
    │                   AutonomousController                   │
    │  DesireSystem → IntrinsicTaskGenerator → MotivationArbiter│
    └──────────────────────────┬──────────────────────────────┘
                               │ tick()
                               ▼
    ┌─────────────────────────────────────────────────────────┐
    │                     AutonomousLoop                       │

Measured, **nothing imports ``AutonomousController``** — not from the package, not from
``src/``, not from ``tests/``, not from any doc's code. ``runtime.py`` builds
``AutonomousLoop`` directly in ``_create_autonomous_loop``, so the controller is not an
entry point at all: it is a *second, unreachable path* that the diagram presents as the
first one. ``motivation_arbiter`` hangs off it and is therefore unreachable too.

This is not a stray constant — it is an **execution path**, ~700 lines, described by the
project's own architecture doc as the thing that runs. So it is **pinned, not deleted**,
for the same reason ``aegis_ai/permissions/`` (a *working* forced gate with no importers)
and ``aegis_ai/evaluation/`` (a sub-graph whose claims had gone false) were pinned: the
delete-vs-wire call is the owner's, and deleting an unreachable path is only safe once you
know what it claimed. What this file guarantees is that **either decision has to be made
deliberately** — wiring it, or deleting it, both turn a test red.

**The scan is transitive, and getting that wrong over-reports deadness.** A first version
asked only "is this module imported from *outside* the package?" and reported **five**
unreachable modules. Three of them — ``planner`` (via ``autonomous_loop``), ``l2_mind``
and ``l2_models`` (via the package ``__init__``) — are reachable. The real answer is
**two**. Follow the chain to a root before calling anything dead.

What the three-layer claim inside the dead path actually is (also measured, also pinned):

* ``AutonomousController`` — zero importers (layer 1).
* ``motivation_arbiter`` — imported only by it (layer 2).
* The approval fields — layer 3, below. They are **not** dead in the same way, and saying
  "both are write-only" would be sloppy in the direction that hides the worse half:

* ``MotivationDecision.requires_approval`` — written at five sites (``:214`` / ``:234`` /
  ``:254`` copy it from ``t.requires_approval``; ``:320`` writes ``best_task``'s
  *differently-named* ``requires_user_approval``; ``:332`` writes a literal ``False``) and
  **read by nothing at all**.
* ``ExternalTask.requires_approval`` — *is* read, at ``:214`` / ``:234`` / ``:254``, but only
  inside ``decide``'s user / scheduled / event branches. Those branches are typed
  ``list[ExternalTask] | None`` and **nothing in the repository ever constructs an
  ``ExternalTask``**, so the field is a claim about a task that cannot occur — and the
  ``isinstance(task, ExternalTask)`` arm of ``_build_task_request`` cannot fire either.
"""

from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
_PKG_REL = "aegis_ai/autonomous"

#: The module ``docs/self-development.md`` presents as the autonomous entry point.
_DEAD_ENTRY_POINT = "autonomous_controller"

#: Its only dependent — reachable *only* through the dead module, so also unreachable.
_ONLY_THROUGH_THE_DEAD_MODULE = "motivation_arbiter"

#: The module ``runtime.py`` actually constructs.
_LIVE_ENTRY_POINT = "autonomous_loop"

#: Types whose handlers would be the only place an approval flag on a motivation decision
#: could be consumed.
_MOTIVATION_TYPES = ("MotivationDecision", "ExternalTask", "MotivationArbiter")


def _parseable_sources():
    """Every ``*.py`` under ``src/`` that parses, as ``(relative path, tree, text)``."""
    for path in sorted(_SRC.rglob("*.py")):
        if "generated" in path.parts or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError:  # pragma: no cover - a syntax error fails elsewhere
            continue
        yield path.relative_to(_SRC).as_posix(), tree, text


def _imported_names(tree: ast.AST) -> set[str]:
    """Every dotted name this tree imports, in both forms.

    ``from aegis_ai.autonomous.autonomous_loop import AutonomousLoop`` contributes both
    ``aegis_ai.autonomous.autonomous_loop`` and ``...autonomous_loop.AutonomousLoop``, so a
    direct import and a re-export are matched by the same lookup.
    """
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out.add(node.module)
            out.update(f"{node.module}.{alias.name}" for alias in node.names)
    return out


def _importers_of(module: str) -> set[str]:
    """Files under ``src/`` that import ``aegis_ai.autonomous.<module>``."""
    target = f"aegis_ai.autonomous.{module}"
    return {rel for rel, tree, _ in _parseable_sources() if target in _imported_names(tree)}


# ── Guards on the detector itself ─────────────────────────────────────────────


def test_the_scan_actually_sees_imports() -> None:
    """A scan that found nothing would make every assertion below vacuously true.

    Measured, not assumed: with ``_SRC`` pointed at a nonexistent directory, **two** of the
    eight tests here still pass — ``test_the_documented_entry_point_has_no_importers_at_all``
    and ``test_external_task_is_never_constructed``, both of which assert an *empty* set. The
    five that assert a non-empty expectation fail loudly. So this guard is the only thing
    standing between those two and a silent no-op, and it must keep asserting a **positive**
    observation rather than an absence.
    """
    assert _importers_of(_LIVE_ENTRY_POINT), (
        "the scan does not see runtime.py importing the live loop, so it is not reading src/"
    )
    assert _importers_of("models"), "the scan does not see the shared models module"


# ── The invariant ─────────────────────────────────────────────────────────────


def test_the_documented_entry_point_has_no_importers_at_all() -> None:
    """``AutonomousController`` is unreachable. Equality against the empty set.

    Both repairs fail this test, which is the point: wiring the controller means updating
    the architecture diagram that currently presents it as the entry point, and deleting it
    means deleting this assertion with a reason.
    """
    observed = _importers_of(_DEAD_ENTRY_POINT)
    assert observed == set(), (
        f"`{_DEAD_ENTRY_POINT}` now has importers: {sorted(observed)}.\n"
        "That is a decision, not a detail. Either it is being wired — in which case "
        "docs/self-development.md's architecture diagram becomes true and this test must be "
        "replaced by one asserting the controller *is* constructed by runtime.py — or the "
        "import is a leftover. Decide, then change this file."
    )


def test_the_arbiter_is_reachable_only_through_the_dead_controller() -> None:
    """``motivation_arbiter`` is not independently dead — it is dead *because* of layer 1.

    Recording the importer by name rather than just asserting "nobody imports it" keeps the
    two layers distinguishable: if the controller is ever wired, this test stays green and
    the one above is the single place that changes.
    """
    observed = _importers_of(_ONLY_THROUGH_THE_DEAD_MODULE)
    assert observed == {f"{_PKG_REL}/{_DEAD_ENTRY_POINT}.py"}, (
        f"`{_ONLY_THROUGH_THE_DEAD_MODULE}` importers changed: {sorted(observed)}.\n"
        f"  recorded: ['{_PKG_REL}/{_DEAD_ENTRY_POINT}.py']\n"
        "A second importer makes the arbiter reachable independently of the controller — "
        "which changes what the controller's fate means."
    )


# ── The replacement control: something *is* the entry point ───────────────────


def _runtime_tree() -> ast.AST:
    return ast.parse((_SRC / "aegis_ai" / "runtime.py").read_text(encoding="utf-8"))


def _runtime_imports_from(module: str) -> set[str]:
    """Names ``runtime.py`` imports *from* ``module``.

    AST rather than a substring: ``import AutonomousLoop as _X`` keeps the module path but
    changes which name exists, and a substring check on the import statement cannot tell the
    difference. ``alias.name`` is the *imported* name either way.
    """
    names: set[str] = set()
    for node in ast.walk(_runtime_tree()):
        if isinstance(node, ast.ImportFrom) and node.module == module:
            names.update(alias.name for alias in node.names)
    return names


def _runtime_constructs(name: str) -> bool:
    """Whether ``runtime.py`` calls ``name(...)`` (bare or as an attribute)."""
    for node in ast.walk(_runtime_tree()):
        if isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Name) and func.id == name) or (
                isinstance(func, ast.Attribute) and func.attr == name
            ):
                return True
    return False


def test_the_live_loop_is_the_one_runtime_constructs() -> None:
    """Why "unreachable" is a defect and not just a curiosity: there *is* a live path.

    The autonomous loop is not missing — it is built by ``runtime.py`` and started from
    ``start_autonomous_if_enabled``. So the controller is a *duplicate* entry point, not the
    only one, and the architecture doc names the wrong one.

    Note what this test deliberately does **not** forbid: renaming the binding consistently
    on both sides. That leaves the path running, which is the property being checked.
    """
    module = f"aegis_ai.autonomous.{_LIVE_ENTRY_POINT}"
    imported = _runtime_imports_from(module)
    assert "AutonomousLoop" in imported, (
        f"runtime.py no longer imports AutonomousLoop from {module} "
        f"(it imports {sorted(imported) or 'nothing from that module'}). The live path "
        "moved, so the claim in this file's docstring now describes a different system."
    )
    assert _runtime_constructs("AutonomousLoop"), (
        "runtime.py imports AutonomousLoop but no longer constructs it. There would then be "
        "*no* autonomous entry point at all — which makes `the controller is unreachable` a "
        "wrong description of the problem, not a stronger one."
    )


def test_runtime_does_not_route_through_the_dead_controller() -> None:
    """The direct statement of the defect: the entry point does not use the controller."""
    runtime = (_SRC / "aegis_ai" / "runtime.py").read_text(encoding="utf-8")
    assert "AutonomousController" not in runtime, (
        "runtime.py now references AutonomousController. If the controller is being wired, "
        "this test and `test_the_documented_entry_point_has_no_importers_at_all` are the two "
        "records that must be updated — together, in one commit."
    )


# ── Layer 3: the approval claim inside the dead path ──────────────────────────

#: Files that both reference a motivation-decision type and touch ``.requires_approval``.
#: Only ``motivation_arbiter.py`` does, and it only ever *writes* — so the field is
#: write-only. Recorded as a set so a new reader (or a new writer) fails loudly.
_RECORDED_APPROVAL_FIELD_TOUCHERS: frozenset[str] = frozenset(
    {f"{_PKG_REL}/{_ONLY_THROUGH_THE_DEAD_MODULE}.py"}
)


def _files_touching_an_approval_field() -> set[str]:
    """Files that reference a motivation type *and* touch ``.requires_approval``.

    Narrowed to that intersection deliberately. ``.requires_approval`` is a common field
    name — the capability catalog, the permission store and the recovery planner each have
    their own, and all three are live. A bare name scan would be noise; what matters is
    whether anything that handles a *motivation decision* touches it.
    """
    found: set[str] = set()
    for rel, tree, text in _parseable_sources():
        if not any(name in text for name in _MOTIVATION_TYPES):
            continue
        if any(
            isinstance(node, ast.Attribute) and node.attr == "requires_approval"
            for node in ast.walk(tree)
        ):
            found.add(rel)
    return found


def test_the_motivation_approval_flag_is_touched_by_one_file_and_read_by_none() -> None:
    """The field is written inside the dead path and consumed nowhere.

    ``autonomous_controller.py`` mentions ``MotivationDecision`` in annotations and reads
    ``task.requires_user_approval`` — a *different* name, on ``IntrinsicTask`` — which is
    why the intersection below is one file rather than two. That distinction is exactly the
    kind of near-miss a name-based scan gets wrong, so it is asserted rather than assumed.
    """
    observed = _files_touching_an_approval_field()
    assert observed == set(_RECORDED_APPROVAL_FIELD_TOUCHERS), (
        "the set of files touching a motivation decision's approval flag changed.\n"
        f"  newly touching: {sorted(observed - _RECORDED_APPROVAL_FIELD_TOUCHERS)}\n"
        f"  no longer     : {sorted(_RECORDED_APPROVAL_FIELD_TOUCHERS - observed)}\n"
        "If something now *reads* it, the field is no longer write-only — and a decision "
        "made on an approval flag needs the owner-boundary review the rest of this repo "
        "already applies."
    )


def test_external_task_is_never_constructed() -> None:
    """``ExternalTask`` exists only as a type annotation, so its field describes no task.

    ``MotivationArbiter.decide`` takes ``user_tasks`` / ``scheduled_tasks`` /
    ``event_tasks`` typed ``list[ExternalTask] | None`` and ``autonomous_controller.tick``
    forwards them — but nothing in the repository ever builds one, so branches 1, 2 and 4 of
    ``decide`` cannot be reached in production, and ``_build_task_request``'s
    ``isinstance(task, ExternalTask)`` arm cannot fire.
    """
    constructed: set[str] = set()
    for rel, tree, _ in _parseable_sources():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if (isinstance(func, ast.Name) and func.id == "ExternalTask") or (
                isinstance(func, ast.Attribute) and func.attr == "ExternalTask"
            ):
                constructed.add(rel)
    assert constructed == set(), (
        f"ExternalTask is now constructed in {sorted(constructed)}. That unblocks the "
        "user / scheduled / event branches of MotivationArbiter.decide, which have never "
        "run — re-measure before assuming they work."
    )


def test_the_dead_decisions_still_carry_the_approval_field() -> None:
    """Pin the *claim*, not only its absence.

    Removing the field is a legitimate cleanup — but it is a change to a surface whose fate
    is undecided, so it should be as deliberate as wiring it. If you remove it, remove this
    test in the same commit and say why.
    """
    from aegis_ai.autonomous.motivation_arbiter import ExternalTask, MotivationDecision

    for cls in (MotivationDecision, ExternalTask):
        names = {f.name for f in fields(cls)}
        assert "requires_approval" in names, (
            f"{cls.__name__} no longer declares `requires_approval`. Nothing read it, so this "
            "is a safe deletion — but it is a *decision* about the dead path, not a detail: "
            "record it (this test and the B-3 register row) rather than dropping it silently."
        )
