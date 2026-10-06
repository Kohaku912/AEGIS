"""The advertised event-driven core is now constructed, subscribed, and consumed.

Branch ① of ``DELEGATION.md`` §4 item 24, executed 2026-10-06. This file used to be
``test_event_driven_core_stays_unbuilt.py`` and asserted the opposite; it was **inverted**,
not weakened, because the premise changed by owner decision — the *same* measurements are
still made, and the same trap is still guarded.

**The defect it recorded.** ``docs/architecture.md:20`` defines AEGIS as an "autonomous,
**event-driven**, self-improving AI assistant", and carries the core through the rest of
the document: a node at ``:57``, the edge ``EventBus --> TriggerEngine --> ContextBuilder``
at ``:84-85``, a core-class list at ``:108``, a Key-modules line at ``:170``, "Decide when
to wake up (TriggerEngine)" at ``:174``, and a sequence-diagram participant at ``:559``.
``AGENTS.md:15`` calls event-driven coordination the core principle. Two safety documents
repeat the edge.

Measured 2026-10-03 with ``ast`` over ``src/`` (408 modules): **0** construction sites for
each of ``TriggerEngine``, ``Scheduler`` and ``EventView``, and references only to their own
re-export shims. ``EventBus`` / ``EventManager`` *were* live (``.publish`` 17 call sites,
``.subscribe`` 9) — the system published and read events, but it was **poll-driven**:
``context_builder.py`` called ``list_recent_events()`` on a timer instead of a trigger
engine waking the loop. The gap was the *triggering* half, not the bus.

**What changed** (all inside ``runtime.py::_build_runtime`` unless noted):

| class | construction site | note |
|---|---|---|
| ``TriggerEngine`` | ``runtime.py::_build_runtime`` | all **13** ``create_default_rules()`` rules added |
| ``Scheduler`` | ``runtime.py::_build_runtime`` | constructed **empty**; its designed consumer is never given one — asserted below |
| ``EventView`` | ``runtime.py::_build_runtime`` | **both** halves — a bare ``EventView()`` is a silent no-op; **no consumer** either |
| ``AutonomousLoop`` | ``runtime.py::_create_autonomous_loop`` | the pre-existing contrast |

The consumption half is ``AutonomousLoop._drain_trigger_tasks`` (``autonomous_loop.py``),
called from ``_run_loop``. Without it the engine would queue ``TaskRequest``\\ s that nobody
ever drains — the *other* half of the same defect. It is gated on ``can_execute`` because
``drain_tasks()`` clears the queue: draining into a cycle that then does not run would
discard the tasks without a trace.

``config.trigger_enabled`` (default **true**, ``config.py:35``) is now the *construction
condition* rather than a log-only mention, so the ``main.py:27`` startup line is true
instead of claiming "Trigger Engine: enabled" with nothing behind it. That is also why
``trigger_enabled`` left ``_INEFFECTIVE_CONFIG_FIELDS`` in ``test_ineffective_flags.py`` —
layer 4's equality assertion is what forced the census to move.

**The trap this pin still guards.** The survey's first draft recorded "the only
``TriggerEngine()`` is ``trigger_engine.py:175``'s self-module ``__main__`` demo" — and the
same for ``Scheduler()`` at ``scheduler.py:75``. Both halves of that are wrong, and the
second half is the interesting one:

* there is **no** ``if __name__ == "__main__"`` block in either file, so there is no demo;
* line 175 / line 75 sit inside the class's **docstring** (``Usage: engine = TriggerEngine()``).

A mention inside a string literal is not an invocation, so the count was 0 rather than 1.
Now that a *real* call site exists the trap is **sharper, not softer**: the pin asserts the
docstring text is still in the tree **and** that neither defining module contributes a
construction site, so a reader can tell the mention from the call by *location*.

The pin fails in **both** directions — deleting a construction site (un-wiring the core) and
deleting the docstring mention both trip it — so neither can happen as a side effect.

**Constructed is not consulted** (added 2026-10-06, cycle 69). The table above has described
``Scheduler``'s missing consumer in *prose* since branch ① ran; prose is not an assertion, and
``EventView``'s missing consumer was recorded nowhere at all. The two tests at the end of this
file measure *reads* of the runtime attributes each core class is assigned to, assert the
unconsumed set by **equality**, and use the ``TriggerEngine`` — consumed only through
``getattr(runtime, "trigger_engine", None)`` — as the control proving the scan can see the
string form.

**Starved, not unconsumed** (added 2026-10-06, cycle 70). "No consumer" is the wrong phrase for
``Scheduler``. A consumer *was* written — ``ContextBuilder.__init__(scheduler=...)`` stores
``self._scheduler``, and the build reads ``self._scheduler.get_due_tasks()`` — but the composition
root constructs ``ContextBuilder`` without it, so the guard ``if self._scheduler:`` is always false
and ``scheduler=`` appears **zero** times in ``src/``. The path is dead **twice**: the runtime also
builds ``Scheduler()`` with an empty task map, because ``create_default_tasks()`` is called nowhere.
That is the ``QuietHoursManager()`` shape (§4 item 35) — supplying the object is not supplying its
state — and it is why the fix is a behaviour change rather than a one-line wire: it would add
``pending_tasks`` lines to every prompt.
"""

from __future__ import annotations

import ast
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1]
_SRC = _SERVER / "src"

#: The advertised core: class name -> the module that *defines* it, the modules allowed to
#: reference it (a re-export shim is a reference, not a use), and the ``module::function``
#: sites that construct it. Measured 2026-10-06, after branch ①. Every set is asserted by
#: **equality**, so both a new construction site and a deleted one fail rather than
#: silently widening or narrowing the record.
_CORE: dict[str, tuple[str, frozenset[str], tuple[str, ...]]] = {
    "TriggerEngine": (
        "trigger_engine.py",
        frozenset({"aegis_ai/trigger_engine.py", "aegis_ai/runtime.py"}),
        ("aegis_ai/runtime.py::_build_runtime",),
    ),
    "Scheduler": (
        "aegis_ai/scheduler.py",
        frozenset({"aegis_ai/runtime.py"}),
        ("aegis_ai/runtime.py::_build_runtime",),
    ),
    "EventView": (
        "aegis_ai/observability/event_view.py",
        frozenset({"aegis_ai/observability/__init__.py", "aegis_ai/runtime.py"}),
        ("aegis_ai/runtime.py::_build_runtime",),
    ),
}

#: The contrast. These were constructed before the core was, so a scan that reads nothing
#: cannot satisfy the assertions above for the wrong reason. A floor, not an equality: a
#: second construction site is a legitimate change, not a defect.
_CONSTRUCTED_CONTRAST = ("AutonomousLoop", "EventBus", "EventManager")

#: Text that exists in the tree but is not a call node — the docstring trap, pinned as a
#: positive control so the extractor cannot pass by being blind to it.
#: module -> (class named by the example, the example text)
_DOCSTRING_MENTIONS: dict[str, tuple[str, str]] = {
    "trigger_engine.py": ("TriggerEngine", "engine = TriggerEngine()"),
    "aegis_ai/scheduler.py": ("Scheduler", "scheduler = Scheduler()"),
}

#: ``src/`` holds 400+ modules; a scan that silently reads nothing must not be able to
#: satisfy the assertions below by returning empty sets. (Same shape as the sibling
#: "stays unwired" pins.)
_MIN_SRC_FILES = 300


def _src_files() -> list[Path]:
    return sorted(p for p in _SRC.rglob("*.py") if "__pycache__" not in p.parts)


def _parsed(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))


def _enclosing(tree: ast.Module, lineno: int) -> str:
    """The innermost function containing ``lineno``, or ``<module>``."""
    best: ast.AST | None = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end = max((getattr(n, "lineno", 0) for n in ast.walk(node)), default=0)
        if node.lineno <= lineno <= end and (best is None or node.lineno > best.lineno):
            best = node
    return best.name if isinstance(best, (ast.FunctionDef, ast.AsyncFunctionDef)) else "<module>"


def _called_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _construction_sites(name: str) -> list[str]:
    """Every ``name(...)`` call site in ``src/``, as ``module::function``."""
    sites: list[str] = []
    for path in _src_files():
        tree = _parsed(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _called_name(node) == name:
                rel = path.relative_to(_SRC).as_posix()
                sites.append(f"{rel}::{_enclosing(tree, node.lineno)}")
    return sorted(sites)


def _construction_sites_in(name: str, path: Path) -> list[ast.Call]:
    """The ``ast.Call`` nodes for ``name(...)`` inside one module."""
    return [
        node
        for node in ast.walk(_parsed(path))
        if isinstance(node, ast.Call) and _called_name(node) == name
    ]


def _defining_modules(name: str) -> list[str]:
    """Modules carrying a ``class name`` statement."""
    found: list[str] = []
    for path in _src_files():
        for node in ast.walk(_parsed(path)):
            if isinstance(node, ast.ClassDef) and node.name == name:
                found.append(path.relative_to(_SRC).as_posix())
    return sorted(found)


def _referencing_modules(name: str) -> list[str]:
    """Modules that reference ``name`` as an identifier — import, bare name, or attribute.

    Deliberately *not* a text search: a docstring that mentions the class is not a reference,
    which is exactly what this file's header is about.
    """
    found: list[str] = []
    for path in _src_files():
        for node in ast.walk(_parsed(path)):
            hit = False
            if isinstance(node, ast.Name) and node.id == name:
                hit = True
            elif isinstance(node, ast.Attribute) and node.attr == name:
                hit = True
            elif isinstance(node, ast.ImportFrom):
                hit = any(alias.name == name for alias in node.names)
            elif isinstance(node, ast.Import):
                hit = any(alias.name.endswith(name) for alias in node.names)
            if hit:
                found.append(path.relative_to(_SRC).as_posix())
                break
    return sorted(found)


def _string_literals(path: Path) -> list[str]:
    """Every ``str`` constant in the module — docstrings included, since ``ast`` stores a
    docstring as a plain ``Constant`` in the body."""
    return [
        node.value
        for node in ast.walk(_parsed(path))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} is not defined in this module any more")


# ── Non-vacuity: the scan must be reading a tree, and the classes must exist ──


def test_the_scan_reads_the_tree_and_the_classes_exist() -> None:
    files = _src_files()
    assert len(files) >= _MIN_SRC_FILES, (
        f"the src scan found only {len(files)} modules (floor {_MIN_SRC_FILES}) — a scan that "
        "reads nothing would satisfy the assertions below for the wrong reason"
    )

    missing = [
        name
        for name, (module, _, _) in _CORE.items()
        if _defining_modules(name) != [module]
    ]
    assert missing == [], (
        f"{missing} are no longer defined where the record says — if a class was renamed or "
        "deleted, this pin is measuring nothing and the register row (PROJECT_STATUS_REVIEW.md "
        "§3.2) must move with it"
    )


def test_the_contrast_classes_are_constructed() -> None:
    """``AutonomousLoop`` / ``EventBus`` / ``EventManager`` are built — the scan works.

    Without this, ``_construction_sites`` returning ``[]`` for everything would look like a
    clean result rather than a broken extractor.
    """
    for name in _CONSTRUCTED_CONTRAST:
        sites = _construction_sites(name)
        assert sites, (
            f"{name} has no construction site either — the extractor is broken, or the runtime "
            "was dismantled; either way this pin cannot report on the core classes"
        )


# ── The claim: the three core classes are constructed, at the recorded sites ─


def test_the_core_classes_are_constructed_at_the_recorded_sites() -> None:
    measured = {name: tuple(_construction_sites(name)) for name in _CORE}
    recorded = {name: sites for name, (_, _, sites) in _CORE.items()}
    assert measured == recorded, (
        f"construction sites moved. measured: {measured}; recorded: {recorded}. If a site was "
        "deleted the core is un-wired again (see DELEGATION.md §4 item 24); if a *second* site "
        "appeared, the record must be updated in the same commit as PROJECT_STATUS_REVIEW.md "
        "§3.2 and docs/architecture.md."
    )


def test_the_referencing_modules_match_the_record() -> None:
    """A reference is not a use, but the *set* of referencing modules is the record.

    Measured by equality so neither a new importer nor a removed one can drift silently.
    """
    measured = {
        name: frozenset(_referencing_modules(name)) - {module}
        for name, (module, _, _) in _CORE.items()
    }
    recorded = {name: allowed for name, (_, allowed, _) in _CORE.items()}
    assert measured == recorded, (
        f"references moved. measured: { {k: sorted(v) for k, v in measured.items()} }; "
        f"recorded: { {k: sorted(v) for k, v in recorded.items()} } — see DELEGATION.md §4 item 24"
    )


def test_the_core_is_built_only_when_the_flag_is_set() -> None:
    """``config.trigger_enabled`` gates the construction — the flag has a real reader.

    ``test_ineffective_flags.py`` layer 4 used to record this field as read only by
    ``main.py:27``'s log line. That entry is gone because the construction below *is* a
    reader. This asserts the shape, which is what makes the removal honest: the
    ``TriggerEngine()`` statement is a direct child of an ``if ... trigger_enabled:`` body,
    so ``AEGIS_TRIGGER_ENABLED=0`` yields a runtime without the core rather than a half-built
    one.
    """
    path = _SRC / "aegis_ai" / "runtime.py"
    calls = _construction_sites_in("TriggerEngine", path)
    assert len(calls) == 1, (
        f"expected exactly one TriggerEngine() in runtime.py, found {len(calls)} — this test "
        "pins the guard around that one site"
    )
    call = calls[0]

    tree = _parsed(path)
    guards = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.If)
        and "trigger_enabled" in ast.dump(node.test)
        and any(getattr(stmt, "lineno", 0) == call.lineno for stmt in node.body)
    ]
    assert guards, (
        "the TriggerEngine() construction is not a direct child of an `if ... trigger_enabled` "
        "body — the flag would not gate it, and layer 4's census removal would be wrong "
        "(DELEGATION.md §4 item 24)"
    )


# ── The consumption half: the queue has a reader, and draining cannot discard ─


def test_the_trigger_tasks_are_drained_and_consumed() -> None:
    """``_drain_trigger_tasks`` exists, is called from ``_run_loop``, and is guarded.

    Three properties, all structural:

    * the method exists — without it the engine queues ``TaskRequest``\\ s nobody drains;
    * the call sits inside a ``... if can_execute else ...`` — ``drain_tasks()`` clears the
      queue, so draining into a cycle that then does not run would throw the tasks away
      *silently*, which is the defect family this project keeps re-finding;
    * the drained list reaches the wake condition — otherwise the drain is a no-op that
      still looks like a consumer.
    """
    path = _SRC / "aegis_ai" / "autonomous" / "autonomous_loop.py"
    tree = _parsed(path)

    defined = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert "_drain_trigger_tasks" in defined, (
        "_drain_trigger_tasks is gone — the TriggerEngine would queue TaskRequests that "
        "nobody ever drains (DELEGATION.md §4 item 24)"
    )

    run_loop = _function(tree, "_run_loop")
    calls = [
        node
        for node in ast.walk(run_loop)
        if isinstance(node, ast.Call) and _called_name(node) == "_drain_trigger_tasks"
    ]
    assert len(calls) == 1, (
        f"expected one _drain_trigger_tasks() call in _run_loop, found {len(calls)}"
    )

    guard = [
        node
        for node in ast.walk(run_loop)
        if isinstance(node, ast.IfExp) and any(sub is calls[0] for sub in ast.walk(node))
    ]
    assert guard, (
        "the drain is not guarded by a conditional expression — it must not run when the "
        "cycle cannot, because drain_tasks() clears the queue"
    )
    test = guard[0].test
    assert isinstance(test, ast.Name) and test.id == "can_execute", (
        f"the drain guard is {ast.dump(test)} rather than `can_execute`"
    )

    wake = [
        node
        for node in ast.walk(run_loop)
        if isinstance(node, ast.If) and "triggered_tasks" in ast.dump(node.test)
    ]
    assert wake, (
        "triggered_tasks never reaches a wake condition — the tasks are drained and then "
        "ignored, which is a consumer in name only"
    )


def test_the_loop_receives_the_trigger_engine() -> None:
    """``_create_autonomous_loop`` hands the loop *the runtime's* engine.

    Without this assignment the loop's ``_drain_trigger_tasks`` reads its ``None`` default
    and returns ``[]`` forever: the core would be built, subscribed — and still never
    consumed. The two halves are only a fix together.

    ⚠️ The assertion is on the **right-hand side**, not merely on the presence of an
    assignment. A first draft checked only that some ``loop._trigger_engine = ...`` existed,
    and mutation M1 (replacing the value with a bare ``None``) **survived** it — the shape was
    there while the wiring was gone. Same family as "a mention is not a reader".
    """
    path = _SRC / "aegis_ai" / "runtime.py"
    factory = _function(_parsed(path), "_create_autonomous_loop")
    assignments = [
        node
        for node in ast.walk(factory)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Attribute) and target.attr == "_trigger_engine"
            for target in node.targets
        )
    ]
    assert len(assignments) == 1, (
        "expected exactly one `loop._trigger_engine = ...` in _create_autonomous_loop, found "
        f"{len(assignments)} — the engine is built and subscribed, but the loop that should "
        "drain it still sees None"
    )
    rhs = ast.dump(assignments[0].value)
    assert "trigger_engine" in rhs, (
        f"the loop's _trigger_engine is assigned {rhs}, which does not read the runtime's "
        "engine — the assignment exists but the wiring does not (mutation M1)"
    )


# ── The trap: the docstring mention is a mention, not a call ─────────────────


def test_the_docstring_mention_is_still_a_mention_not_a_call() -> None:
    """Both halves at once: the text is in the tree, and its own module makes no call.

    This is the assertion that would have caught the survey's original wording ("the only
    ``TriggerEngine()`` is a ``__main__`` demo"). It is written as a conjunction on purpose —
    asserting only the absence of a call would pass on a tree where the mention had been
    deleted too, and asserting only the presence of the text would say nothing about calls.

    The call-side half is now scoped to the **defining module** rather than to all of
    ``src/``: a real call site legitimately exists elsewhere (asserted above), so the trap
    that remains is "the docstring example must not itself become a call".
    """
    for module, (class_name, mention) in _DOCSTRING_MENTIONS.items():
        assert class_name in _CORE, (
            f"{class_name} is not in _CORE — this control must guard a class the pin actually "
            "records"
        )
        path = _SRC / module
        assert path.is_file(), f"{module} is gone — the record's path was wrong too"

        literals = _string_literals(path)
        assert any(mention in text for text in literals), (
            f"the docstring example {mention!r} is no longer in {module} — the mention this pin "
            "guards was removed, so the 'no demo, only a docstring' record is stale"
        )
        own_calls = _construction_sites_in(class_name, path)
        assert own_calls == [], (
            f"{module} now constructs {class_name} itself ({len(own_calls)} call site(s)) — the "
            f"docstring example {mention!r} has become a real call, so the mention is no longer "
            "distinguishable from a use"
        )


# ── Why constructing EventView with only one half would not have helped ──────


def test_event_view_reports_nothing_without_a_trigger_engine() -> None:
    """Behavioural, not structural: the guards make a bare ``EventView`` a silent no-op.

    A wiring that stopped at ``EventView(event_bus=...)`` would render an empty dashboard
    section, not an error — so "construct EventView" was never sufficient on its own.
    """
    from aegis_ai.observability.event_view import EventView

    view = EventView()
    assert view.get_trigger_stats() == {}
    assert view.get_pending_tasks() == []


def test_the_runtime_event_view_is_built_with_both_halves() -> None:
    """The structural counterpart: the runtime's ``EventView`` gets a trigger engine.

    Together with the behavioural control above this is the whole argument — a bare
    ``EventView()`` returns ``{}`` silently, so the *runtime's* call site must supply the
    engine, or the dashboard section is empty rather than broken.
    """
    path = _SRC / "aegis_ai" / "runtime.py"
    calls = _construction_sites_in("EventView", path)
    assert len(calls) == 1, (
        f"expected exactly one EventView() in runtime.py, found {len(calls)}"
    )
    keywords = {kw.arg for kw in calls[0].keywords}
    assert "trigger_engine" in keywords, (
        f"the runtime builds EventView without a trigger_engine (keywords: {sorted(keywords)}) — "
        "get_trigger_stats() would return {} and the section would look empty, not broken"
    )


# ── Constructed is not consulted: two of the three core members have no reader ──

#: Inventory of **debt**, not a set of approvals: core members that are constructed and then
#: never read. ``Scheduler`` lands on ``runtime.scheduler`` and ``EventView`` on
#: ``runtime.event_view``; nothing under ``src/`` loads either attribute. The ``TriggerEngine``
#: is the contrast — it *is* consumed, through ``getattr(runtime, "trigger_engine", None)`` in
#: ``_create_autonomous_loop``, which is why the scanner has to see the string form too.
#:
#: This map used to be prose. The module header above has said "``Scheduler`` … constructed; it
#: has no consumer wired yet" since branch ① ran, and **nothing failed if that stopped being
#: true**; ``EventView``'s lack of a consumer was recorded nowhere at all. Describing a hazard
#: is not detecting it — so each entry here is asserted by equality.
_RECORDED_UNCONSULTED: dict[str, str] = {
    "Scheduler": "scheduler",
    "EventView": "event_view",
}

#: A plainly live runtime attribute, used as the scanner's positive control. If the extractor
#: goes blind, this is what fails — rather than the equality above passing on an empty map.
_LIVE_ATTRIBUTE_CONTRAST = "event_manager"


def _runtime_attribute(class_name: str) -> set[str]:
    """The ``runtime.<attr>`` attributes this class's objects are assigned to.

    Resolved from the AST in two hops rather than hand-listed, because a hand-maintained list
    *is* the defect this file exists to record:

    * direct — ``runtime.<attr> = ClassName(...)`` (``Scheduler``, ``EventView``);
    * indirect — ``local = ClassName(...)`` then ``runtime.<attr> = local`` (``TriggerEngine``).
    """
    tree = _parsed(_SRC / "aegis_ai" / "runtime.py")
    attrs: set[str] = set()
    produced: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        if _called_name(node.value) != class_name:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                produced.add(target.id)
            elif (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "runtime"
            ):
                attrs.add(target.attr)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Name):
            continue
        if node.value.id not in produced:
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "runtime"
            ):
                attrs.add(target.attr)
    return attrs


def _attribute_reads(attr: str) -> list[str]:
    """Every ``Load`` of ``.<attr>`` under ``src/``, plus the ``getattr(obj, "<attr>", ...)`` form.

    The string form is not optional. The ``TriggerEngine``'s only consumer is written
    ``getattr(runtime, "trigger_engine", None)``, so an ``ast.Attribute``-only scan reports a
    **consumed** member as unconsumed — the "``getattr`` passes the name as a string" trap.
    The ``getattr`` form is accepted for any object, which can only *over*-count reads; the
    failure it would hide is a false "unconsumed", not a false "consumed".
    """
    hits: list[str] = []
    for path in _src_files():
        rel = path.relative_to(_SRC).as_posix()
        tree = _parsed(path)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == attr
                and isinstance(node.ctx, ast.Load)
            ):
                hits.append(f"{rel}::{_enclosing(tree, node.lineno)}")
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "getattr"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value == attr
            ):
                hits.append(f"{rel}::{_enclosing(tree, node.lineno)}")
    return sorted(set(hits))


def test_the_scan_can_tell_a_read_attribute_from_an_unread_one() -> None:
    """Non-vacuity, and the reason the ``getattr`` form is mandatory.

    Two positives: a plainly live runtime attribute has readers, *and* the ``TriggerEngine`` —
    whose only consumer is the string form — is seen as read. Without the second, an extractor
    blind to ``getattr`` would satisfy the equality below while calling a consumed member dead.
    """
    assert _attribute_reads(_LIVE_ATTRIBUTE_CONTRAST), (
        f"no reads of `.{_LIVE_ATTRIBUTE_CONTRAST}` anywhere in src/ — the extractor is not "
        "reading the tree, so the equality below would pass for the wrong reason"
    )
    assert _attribute_reads("trigger_engine"), (
        "the TriggerEngine is consumed through getattr(runtime, 'trigger_engine', None); a scan "
        "that cannot see the string form reports a consumed member as unconsumed"
    )


def test_the_unconsulted_core_members_are_the_recorded_set() -> None:
    """Constructing an object is not consuming it: the measured debt equals the record.

    Both directions are load-bearing — wiring ``runtime.scheduler`` or ``runtime.event_view``
    to a real consumer must fail this (so the record has to move in the same change), and so
    must a *new* core member that nothing reads.
    """
    measured = {
        name: attr
        for name in _CORE
        for attr in sorted(_runtime_attribute(name))
        if not _attribute_reads(attr)
    }
    assert measured == _RECORDED_UNCONSULTED, (
        f"the unconsumed core set moved. measured: {measured}; recorded: "
        f"{_RECORDED_UNCONSULTED} — see DELEGATION.md §4 item 24. Constructing an object is "
        "not consuming it, and this file's own header said 'no consumer wired yet' for two "
        "cycles while nothing checked it."
    )

# ── Starved, not unconsumed: the Scheduler's consumer exists and is never given one ──

#: The keyword set the composition root passes to ``ContextBuilder``, measured 2026-10-06. An
#: **equality**, so wiring the scheduler in (adding ``scheduler=``) fails this pin and forces the
#: record to move — the same shape as ``_RECORDED_UNCONSULTED`` above.
_CONTEXT_BUILDER_KWARGS = frozenset(
    {
        "capability_retriever",
        "event_bus",
        "identity",
        "multimodal_llm",
        "settings_resolver",
        "tool_broker",
        "user_model_store",
    }
)


def _class_init(tree: ast.Module, class_name: str) -> ast.FunctionDef:
    """The ``__init__`` of ``class_name`` specifically — not the first ``__init__`` in the file."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    return item
    raise AssertionError(f"{class_name}.__init__ is gone")


def _keyword_call_sites(keyword: str) -> list[str]:
    """Every ``f(..., keyword=...)`` call site in ``src/``, as ``module::function``."""
    sites: list[str] = []
    for path in _src_files():
        tree = _parsed(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and any(k.arg == keyword for k in node.keywords):
                rel = path.relative_to(_SRC).as_posix()
                sites.append(f"{rel}::{_enclosing(tree, node.lineno)}")
    return sorted(set(sites))


def _context_builder_kwargs() -> set[str]:
    """The keyword names the composition root passes to ``ContextBuilder``."""
    tree = _parsed(_SRC / "aegis_ai" / "runtime.py")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _called_name(node) == "ContextBuilder":
            return {k.arg for k in node.keywords}
    raise AssertionError("the composition root no longer constructs ContextBuilder")


def test_the_scheduler_has_a_designed_consumer_that_is_never_given_one() -> None:
    """The *reverse* of "no consumer": ``ContextBuilder`` is one, and nothing supplies it.

    This sharpens the equality above rather than repeating it. ``runtime.scheduler`` has zero
    reads — but not because no consumer was ever written. ``ContextBuilder.__init__(scheduler=...)``
    stores ``self._scheduler``, and the build reads ``self._scheduler.get_due_tasks()``, behind
    ``if self._scheduler:``. The composition root builds ``ContextBuilder`` **without**
    ``scheduler=``, so the attribute is ``None`` and the branch cannot fire. ``scheduler=`` appears
    **zero** times in ``src/``, so this is not one forgotten call among many: the link was never
    drawn.

    Both directions are load-bearing: wiring it must fail this pin (so the register moves), and
    deleting the parameter or the read must fail it too (so the record cannot pass by describing a
    consumer that no longer exists).
    """
    tree = _parsed(_SRC / "aegis_ai" / "context_builder.py")
    init = _class_init(tree, "ContextBuilder")
    params = {a.arg for a in (*init.args.args, *init.args.kwonlyargs)}
    assert "scheduler" in params, (
        "ContextBuilder no longer accepts a `scheduler` — the consumer this pin records is gone, "
        "so 'starved' is no longer the right word for the Scheduler"
    )
    reads = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and n.attr == "_scheduler" and isinstance(n.ctx, ast.Load)
    ]
    assert reads, (
        "ContextBuilder no longer reads self._scheduler — the guarded branch this pin describes "
        "has been deleted"
    )
    assert _keyword_call_sites("event_bus"), (
        "no `event_bus=` call site found in src/ — the keyword scanner is not reading the tree, so "
        "the `scheduler=` check below would pass for the wrong reason"
    )
    starved = _keyword_call_sites("scheduler")
    assert starved == [], (
        f"`scheduler=` is now passed somewhere in src/ ({starved}) — the Scheduler is no longer "
        "starved, so DELEGATION.md §4 item 24's record has to move"
    )
    measured = _context_builder_kwargs()
    assert measured == _CONTEXT_BUILDER_KWARGS, (
        f"the composition root's ContextBuilder kwargs moved: {sorted(measured)} != "
        f"{sorted(_CONTEXT_BUILDER_KWARGS)} — if `scheduler` is now among them, the record moved "
        "and this pin is telling you to say so"
    )


def test_the_scheduler_would_be_empty_even_if_it_were_wired() -> None:
    """The second half of the double death: ``create_default_tasks()`` is never called.

    Supplying ``ContextBuilder(scheduler=runtime.scheduler)`` would not be enough — the runtime
    builds ``Scheduler()`` with an empty task map, and nothing calls ``create_default_tasks()``, so
    ``get_due_tasks()`` would return ``[]`` regardless. Measured 2026-10-06: **0** call sites in
    ``src/``. This is the ``QuietHoursManager()`` shape (§4 item 35): supplying the object is not
    the same as supplying its state.
    """
    module = _parsed(_SRC / "aegis_ai" / "scheduler.py")
    assert any(
        isinstance(n, ast.FunctionDef) and n.name == "create_default_tasks" for n in ast.walk(module)
    ), "Scheduler.create_default_tasks is gone — this pin's premise changed"
    assert _construction_sites("create_default_rules"), (
        "no `create_default_rules()` call found in src/ — the scanner is not reading the tree, so "
        "the emptiness check below would pass for the wrong reason"
    )
    empty = _construction_sites("create_default_tasks")
    assert empty == [], (
        f"create_default_tasks is now called ({empty}) — the Scheduler is no longer built empty, "
        "so DELEGATION.md §4 item 24's record has to move"
    )
