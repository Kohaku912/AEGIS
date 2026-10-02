"""The advertised event-driven core is defined, documented — and never constructed.

``docs/architecture.md:20`` defines AEGIS as an "autonomous, **event-driven**, self-improving
AI assistant", and carries the core through the rest of the document: a node at ``:57``, the
edge ``EventBus --> TriggerEngine --> ContextBuilder`` at ``:84-85``, a core-class list at
``:108``, a Key-modules line at ``:170``, "Decide when to wake up (TriggerEngine)" at ``:174``,
and a sequence-diagram participant at ``:559``. ``AGENTS.md:15`` calls event-driven
coordination the core principle. Two safety documents repeat the edge.

Measured 2026-10-03 with ``ast`` over ``src/`` (408 modules):

| class | construction sites | referenced by |
|---|---|---|
| ``TriggerEngine`` | **0** | its own re-export shim only (``aegis_ai/trigger_engine.py``) |
| ``Scheduler`` | **0** | **nothing** |
| ``EventView`` | **0** | the re-export at ``observability/__init__.py:5`` only |
| ``AutonomousLoop`` | 1 (``runtime.py::_create_autonomous_loop``) | the runtime — the contrast |
| ``EventBus`` / ``EventManager`` | 1 each (``runtime.py::_build_runtime``) | the runtime |

The three unbuilt classes are fully written — ``trigger_engine.py`` even carries **13** default
``TriggerRule``\\ s — and ``EventView`` is re-exported from the observability package as though
it were part of the surface. What is missing is a *composition site*: nothing in ``src/``
constructs any of them.

**The trap this pin is built around.** The survey's first draft recorded "the only
``TriggerEngine()`` is ``trigger_engine.py:175``'s self-module ``__main__`` demo" — and the same
for ``Scheduler()`` at ``scheduler.py:75``. Both halves of that are wrong, and the second half
is the interesting one:

* there is **no** ``if __name__ == "__main__"`` block in either file, so there is no demo; and
* line 175 / line 75 sit inside the class's **docstring** (``Usage: engine = TriggerEngine()``).

A mention inside a string literal is not an invocation, so the true count is 0 rather than 1 —
and a reader following the recorded path ``scheduler.py`` from ``src/`` finds no file at all
(the real path is ``aegis_ai/scheduler.py``). This pin therefore asserts both directions of the
trap: the text **is** in the tree, and it is **not** a call.

**Not the same finding as "the event bus is dead".** ``EventBus`` and ``EventManager`` *are*
constructed by ``_build_runtime`` and do carry live traffic (``.publish`` has 17 call sites
across 17 modules, ``.subscribe`` 9). The system publishes and reads events — but it is
**poll-driven**: ``context_builder.py`` calls ``list_recent_events()`` on a timer instead of a
trigger engine waking the loop. The gap is the *triggering* half, not the bus.

**Recorded, not built, not deleted** — deliberately. Building the core changes *what wakes the
assistant*, which is a product decision, and constructing ``EventView`` alone would not even
surface data: ``get_trigger_stats()`` guards ``self._engine`` and returns ``{}`` (behavioural
assertion at the bottom of this file). Aligning the documents to the measurement is the other
branch. ``DELEGATION.md`` §4 item 24 carries the decision and both return paths; the register
row is ``PROJECT_STATUS_REVIEW.md`` §3.2.

The pin fails in **both** directions — constructing any of the three, or deleting the class and
its docstring mention, both trip it — so neither can happen as a side effect. The flag half of
this finding (``config.trigger_enabled`` read only by the startup log line) is *not* duplicated
here: ``test_ineffective_flags.py`` layer 4 already owns it, with the log-only reading built in.
"""

from __future__ import annotations

import ast
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1]
_SRC = _SERVER / "src"

#: The advertised core: class name -> the module that *defines* it, and the modules allowed to
#: reference it (a re-export shim is a reference, not a use). Measured 2026-10-03. Every entry
#: here is constructed nowhere; ``test_the_three_core_classes_are_constructed_nowhere`` says so
#: by equality, so a new construction site fails rather than silently widening the record.
_UNBUILT_CORE: dict[str, tuple[str, frozenset[str]]] = {
    "TriggerEngine": ("trigger_engine.py", frozenset({"aegis_ai/trigger_engine.py"})),
    "Scheduler": ("aegis_ai/scheduler.py", frozenset()),
    "EventView": (
        "aegis_ai/observability/event_view.py",
        frozenset({"aegis_ai/observability/__init__.py"}),
    ),
}

#: The contrast. These *are* constructed, so a scan that reads nothing cannot satisfy the
#: emptiness assertion above for the wrong reason. A floor, not an equality: a second
#: construction site is a legitimate change, not a defect.
_CONSTRUCTED_CONTRAST = ("AutonomousLoop", "EventBus", "EventManager")

#: Text that exists in the tree but is not a call node — the docstring trap, pinned as a
#: positive control so the extractor cannot pass by being blind to it.
#: module -> (class named by the example, the example text)
_DOCSTRING_MENTIONS: dict[str, tuple[str, str]] = {
    "trigger_engine.py": ("TriggerEngine", "engine = TriggerEngine()"),
    "aegis_ai/scheduler.py": ("Scheduler", "scheduler = Scheduler()"),
}

#: ``src/`` holds 400+ modules; a scan that silently reads nothing must not be able to satisfy
#: the assertions below by returning empty sets. (Same shape as the sibling "stays unwired"
#: pins.)
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


# ── Non-vacuity: the scan must be reading a tree, and the classes must exist ──


def test_the_scan_reads_the_tree_and_the_classes_exist() -> None:
    files = _src_files()
    assert len(files) >= _MIN_SRC_FILES, (
        f"the src scan found only {len(files)} modules (floor {_MIN_SRC_FILES}) — a scan that "
        "reads nothing would satisfy the emptiness assertion below for the wrong reason"
    )

    missing = [
        name
        for name, (module, _) in _UNBUILT_CORE.items()
        if _defining_modules(name) != [module]
    ]
    assert missing == [], (
        f"{missing} are no longer defined where the record says — if a class was renamed or "
        "deleted, this pin is measuring nothing and the register row (PROJECT_STATUS_REVIEW.md "
        "§3.2) must move with it"
    )


def test_the_contrast_classes_are_constructed() -> None:
    """``AutonomousLoop`` / ``EventBus`` / ``EventManager`` *are* built — the scan works.

    Without this, ``_construction_sites`` returning ``[]`` for everything would look like a
    clean result rather than a broken extractor.
    """
    for name in _CONSTRUCTED_CONTRAST:
        sites = _construction_sites(name)
        assert sites, (
            f"{name} has no construction site either — the extractor is broken, or the runtime "
            "was dismantled; either way this pin cannot report on the core classes"
        )


# ── The claim: nothing in src/ constructs the three core classes ─────────────


def test_the_three_core_classes_are_constructed_nowhere() -> None:
    offenders = {name: _construction_sites(name) for name in _UNBUILT_CORE}
    live = {name: sites for name, sites in offenders.items() if sites}
    assert live == {}, (
        f"{live} now construct the event-driven core. If that is the deliberate branch ① "
        "(build it), the system is no longer poll-driven: update PROJECT_STATUS_REVIEW.md §3.2, "
        "DELEGATION.md §4 item 24, docs/architecture.md and the startup log line in the same "
        "commit — the log currently reports 'Trigger Engine: enabled' with nothing behind it."
    )


def test_nothing_outside_the_defining_modules_references_the_core() -> None:
    """A reference is not a use, but a *new* one is how a wiring would start.

    The recorded sets allow only the re-export shim each class already has; anything else means
    something has begun importing the core, which is worth a look before it becomes a wiring.
    """
    measured = {
        name: frozenset(_referencing_modules(name)) - {module}
        for name, (module, _) in _UNBUILT_CORE.items()
    }
    recorded = {name: allowed for name, (_, allowed) in _UNBUILT_CORE.items()}
    assert measured == recorded, (
        f"references moved. measured: { {k: sorted(v) for k, v in measured.items()} }; "
        f"recorded: { {k: sorted(v) for k, v in recorded.items()} } — if the core is being "
        "wired, see DELEGATION.md §4 item 24"
    )


# ── The trap: the docstring mention is a mention, not a call ─────────────────


def test_the_docstring_mention_is_a_mention_not_a_call() -> None:
    """Both halves at once: the text is in the tree, and it is not an invocation.

    This is the assertion that would have caught the survey's original wording ("the only
    ``TriggerEngine()`` is a ``__main__`` demo"). It is written as a conjunction on purpose —
    asserting only the absence of a call would pass on a tree where the mention had been
    deleted too, and asserting only the presence of the text would say nothing about calls.
    """
    for module, (class_name, mention) in _DOCSTRING_MENTIONS.items():
        assert class_name in _UNBUILT_CORE, (
            f"{class_name} is not in _UNBUILT_CORE — this control must guard a class the pin "
            "actually records as unbuilt"
        )
        path = _SRC / module
        assert path.is_file(), f"{module} is gone — the record's path was wrong too"

        literals = _string_literals(path)
        assert any(mention in text for text in literals), (
            f"the docstring example {mention!r} is no longer in {module} — the mention this pin "
            "guards was removed, so the 'no demo, only a docstring' record is stale"
        )
        assert _construction_sites(class_name) == [], (
            f"{mention!r} became a real call site — {class_name} is now constructed"
        )


# ── Why constructing EventView alone would not help ──────────────────────────


def test_event_view_reports_nothing_without_a_trigger_engine() -> None:
    """Behavioural, not structural: the guards make a bare ``EventView`` a silent no-op.

    A wiring that stopped at ``EventView(event_bus=...)`` would render an empty dashboard
    section, not an error — so "construct EventView" is not a sufficient branch ①.
    """
    from aegis_ai.observability.event_view import EventView

    view = EventView()
    assert view.get_trigger_stats() == {}
    assert view.get_pending_tasks() == []
