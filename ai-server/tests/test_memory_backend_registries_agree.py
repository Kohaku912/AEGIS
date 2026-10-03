"""``MemoryManager``'s three backend registries name the same set — pinned so they stay so.

Why this file exists
--------------------
``aegis_ai/memory/memory_manager.py`` names its backends three times:

1. ``get_backend()``'s **docstring** — the ``Names:`` list.
2. ``get_backend()``'s **mapping** — the names it can actually resolve.
3. ``get_stats()``'s **list** — the names it iterates, and therefore the names in the live
   ``GET /api/memory/stats`` response (``manager_routes.py`` returns
   ``rt.memory_manager.get_stats()`` verbatim).

Before 2026-10-03 they disagreed, in two ways measured that day:

* The docstring advertised ``association``, which the mapping did **not** contain, so
  ``get_backend("association")`` returned ``None``. The name was not a typo of something
  imaginary: ``AssociationMemory`` is real and **live** — but it is constructed on the
  **runtime** (``runtime.py``) and handed to ``CuriosityExploration``, i.e. registered on
  the runtime, not on the manager. The docstring was conflating the two registries.
* ``get_stats()`` iterated **7** of the **10** resolvable names, dropping ``person`` and
  ``action_trace`` — **both of which define ``get_stats``** — so the live route silently
  reported 7 of 10. ``store`` was the one *justified* omission (``MemoryStore`` defines no
  ``get_stats``). The impact was a silently incomplete answer, not a crash.

Both were fixed on 2026-10-03 (``DELEGATION.md`` §4 item 27): the docstring no longer names
``association``, and ``get_stats()`` now iterates every resolvable backend that can report.

**This pin asserts the agreement, not the disagreement** — it is the inverse of the pin that
first recorded the defect. Back then the file asserted the sets *differed*; a regression to
either defect now fails here.

The invariant, in full:

* ``documented == resolvable`` (registry 1 == registry 2), with no ghost and nothing
  undocumented;
* ``resolvable - stats == {"store"}`` — registry 3 omits exactly the one incapable backend;
* ``MemoryStore`` defines **no** ``get_stats`` (the justification), and every other
  resolvable backend's class **does** — read from the class body, not assumed;
* behaviourally, a manager wired with 10 stat-reporting fakes reports exactly the 9 names
  and ``person`` / ``action_trace`` are among them; wired with backends that cannot report,
  it reports nothing.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "ai-server" / "src"
_MM = _SRC / "aegis_ai" / "memory" / "memory_manager.py"
_RUNTIME = _SRC / "aegis_ai" / "runtime.py"
_ROUTE_FILE = _SRC / "aegis_ai" / "web" / "manager_routes.py"

_ROUTE_PATH = "/api/memory/stats"

#: Recorded 2026-10-03 (after the fix) — the names ``get_backend()`` resolves. The docstring
#: must name exactly this set, and ``get_stats()`` must iterate it minus the one justified
#: omission below. Equality in both directions: a new backend, or a removed one, moves this.
_RECORDED_BACKENDS = frozenset(
    {
        "advanced",
        "episodic",
        "semantic",
        "skill",
        "lesson",
        "workflow",
        "experiential",
        "person",
        "store",
        "action_trace",
    }
)

#: The single resolvable backend that **cannot** report — ``MemoryStore`` defines no
#: ``get_stats``. ``get_stats()`` omits exactly this one.
_JUSTIFIED_OMISSION = frozenset({"store"})

#: The names ``get_stats()`` iterates: every resolvable backend that defines ``get_stats``.
_RECORDED_STATS_BACKENDS = _RECORDED_BACKENDS - _JUSTIFIED_OMISSION

#: name → (module under ``aegis_ai/memory/``, class). Lets the pin read, from the **class
#: body**, whether a backend can report. Equality-checked against ``_RECORDED_BACKENDS``, so
#: adding or renaming a backend must move this roster too.
_BACKEND_CLASS = {
    "advanced": ("advanced.py", "AdvancedMemory"),
    "episodic": ("episodic_memory.py", "EpisodicMemory"),
    "semantic": ("semantic_memory.py", "SemanticMemory"),
    "skill": ("skill_memory.py", "SkillMemory"),
    "lesson": ("lesson_memory.py", "LessonMemory"),
    "workflow": ("workflow_memory.py", "WorkflowMemory"),
    "experiential": ("experiential.py", "ExperientialMemory"),
    "person": ("person_memory.py", "PersonMemory"),
    "store": ("memory_store.py", "MemoryStore"),
    "action_trace": ("action_trace.py", "ActionTraceMemory"),
}

#: The name the docstring used to advertise and the mapping never resolved. It is **not** a
#: typo: the class is real and **live**, but the *runtime* owns it, not the manager.
_GHOST_NAME = "association"
_GHOST_CLASS_MODULE = _SRC / "aegis_ai" / "memory" / "association_memory.py"
_GHOST_CLASS = "AssociationMemory"

#: Floor: the mapping must have at least this many names, or the scan has gone blind.
_MIN_BACKENDS = 8


# ── Scans ────────────────────────────────────────────────────────────────────


def _src_files() -> list[Path]:
    return [
        p
        for p in _SRC.rglob("*.py")
        if "__pycache__" not in p.parts and ".venv" not in p.parts
    ]


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _func(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name}() not found — re-measure and update this pin")


def _doc_names(node: ast.FunctionDef) -> list[str]:
    """The names listed after ``Names:`` in the docstring, in order."""
    doc = ast.get_docstring(node) or ""
    if "Names:" not in doc:
        return []
    tail = doc.split("Names:", 1)[1].replace("\n", " ")
    # Stop at the first sentence — the docstring continues with prose after the list.
    tail = tail.split("This list")[0]
    return [item.strip().rstrip(".") for item in tail.split(",") if item.strip()]


def _mapping_keys(node: ast.FunctionDef) -> list[str]:
    """Keys of the largest dict literal in the function — the name→backend mapping."""
    best: list[str] = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Dict):
            keys = [k.value for k in sub.keys if isinstance(k, ast.Constant)]
            if len(keys) > len(best):
                best = keys
    return best


def _list_names(node: ast.FunctionDef) -> list[str]:
    """First elements of the tuple list in the function — the iterated names."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.List):
            names = [
                el.elts[0].value
                for el in sub.elts
                if isinstance(el, ast.Tuple)
                and el.elts
                and isinstance(el.elts[0], ast.Constant)
            ]
            if names:
                return names
    return []


def _class_methods(module_name: str, class_name: str) -> set[str]:
    tree = _tree(_SRC / "aegis_ai" / "memory" / module_name)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                m.name
                for m in node.body
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
    raise AssertionError(f"class {class_name} not found in {module_name}")


def _constructs(path: Path, class_name: str) -> bool:
    """Whether ``path`` actually **calls** ``class_name`` — an ``ast.Call``, not a mention.

    A substring test would be satisfied by the name in a comment or a docstring; measured
    2026-10-03, a mutation that commented the construction out left a substring check green.
    """
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Call):
            fn = node.func
            name = (
                fn.id
                if isinstance(fn, ast.Name)
                else fn.attr
                if isinstance(fn, ast.Attribute)
                else ""
            )
            if name == class_name:
                return True
    return False


def _source_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── Non-vacuity: the subjects exist and the scans still read ─────────────────


def test_the_scan_reads_the_tree_and_the_subjects_exist() -> None:
    files = _src_files()
    assert len(files) >= 300, (
        f"only {len(files)} source files found; a root moved and the scans would pass "
        "vacuously"
    )
    for path in (_MM, _RUNTIME, _ROUTE_FILE, _GHOST_CLASS_MODULE):
        assert path.exists(), f"{path} is gone; re-measure and update DELEGATION.md §4"
    assert f'"{_ROUTE_PATH}"' in _source_text(_ROUTE_FILE), (
        f"{_ROUTE_FILE} no longer registers {_ROUTE_PATH} — if the route was deleted, the "
        "report stopped being user-visible; re-measure and update this pin together "
        "with DELEGATION.md §4."
    )
    assert set(_BACKEND_CLASS) == set(_RECORDED_BACKENDS), (
        "the backend roster and the recorded backend set disagree — re-measure both "
        "together (a backend was added, removed or renamed)."
    )


# ── Registry 1 == Registry 2: the docstring names exactly what resolves ──────


def test_get_backend_documents_exactly_the_names_it_resolves() -> None:
    node = _func(_tree(_MM), "get_backend")
    documented = set(_doc_names(node))
    resolvable = set(_mapping_keys(node))

    assert len(resolvable) >= _MIN_BACKENDS, (
        f"get_backend's mapping has only {len(resolvable)} names; the scan or the mapping "
        "changed shape"
    )
    assert resolvable == set(_RECORDED_BACKENDS), (
        f"get_backend() resolves {sorted(resolvable)}, not the recorded "
        f"{sorted(_RECORDED_BACKENDS)} — re-measure and re-record."
    )
    assert documented == resolvable, (
        f"the docstring and the mapping disagree: documented-only "
        f"{sorted(documented - resolvable)}, resolvable-only "
        f"{sorted(resolvable - documented)}. A documented-but-unresolvable name is the "
        "ghost defect; a resolvable-but-undocumented name is an incomplete docstring. "
        "Either way this pin and DELEGATION.md §4 move together."
    )


# ── Registry 3: get_stats() omits exactly the one backend that cannot report ─


def test_get_stats_iterates_every_reportable_backend() -> None:
    tree = _tree(_MM)
    resolvable = set(_mapping_keys(_func(tree, "get_backend")))
    stats = set(_list_names(_func(tree, "get_stats")))

    assert stats == set(_RECORDED_STATS_BACKENDS), (
        f"get_stats() iterates {sorted(stats)}, not {sorted(_RECORDED_STATS_BACKENDS)}. "
        "A *missing* name re-opens the under-report; a *new* one claims a backend the "
        "mapping may not resolve. Re-measure and re-record either way."
    )
    assert resolvable - stats == set(_JUSTIFIED_OMISSION), (
        f"the set of resolvable backends missing from get_stats() changed: "
        f"{sorted(resolvable - stats)} != {sorted(_JUSTIFIED_OMISSION)}"
    )


def test_the_omission_is_justified_because_the_class_cannot_report() -> None:
    """The premise of the omission, read from the class body — not assumed."""
    for name in sorted(_JUSTIFIED_OMISSION):
        module_name, class_name = _BACKEND_CLASS[name]
        assert "get_stats" not in _class_methods(module_name, class_name), (
            f"{class_name} now defines get_stats — omitting {name!r} is no longer "
            "justified; add it to get_stats() and move this pin and DELEGATION.md §4 "
            "together."
        )


def test_every_reported_backend_defines_get_stats() -> None:
    """The other half: each name ``get_stats()`` iterates can actually report."""
    for name in sorted(_RECORDED_STATS_BACKENDS):
        module_name, class_name = _BACKEND_CLASS[name]
        assert "get_stats" in _class_methods(module_name, class_name), (
            f"{class_name}.get_stats is gone, but {name!r} is still in get_stats()'s list "
            "— the manager guards with hasattr, so the name would silently drop out of "
            "the response again. Fix the class or the list, then move this pin."
        )


# ── The ghost name: gone from the manager, still live on the runtime ─────────


def test_the_ghost_name_is_gone_but_its_class_is_still_live_on_the_runtime() -> None:
    """``association`` is a *registry conflation*, not a typo of something imaginary."""
    node = _func(_tree(_MM), "get_backend")
    assert _GHOST_NAME not in set(_doc_names(node)), (
        f"get_backend()'s docstring names {_GHOST_NAME!r} again — the manager does not "
        "own that backend, so the name resolves to None."
    )
    assert _GHOST_NAME not in set(_mapping_keys(node)), (
        "the manager now resolves the ghost name — the runtime's backend was wired in; "
        "re-measure and update DELEGATION.md §4"
    )
    # Still real, and still owned by the runtime — which is *why* it is not a manager
    # backend. If the class is deleted the name is dead, and this pin's premise is stale.
    assert "get_stats" in _class_methods(_GHOST_CLASS_MODULE.name, _GHOST_CLASS), (
        f"{_GHOST_CLASS} no longer defines get_stats — the class behind the ghost name "
        "changed"
    )
    assert _constructs(_RUNTIME, _GHOST_CLASS), (
        f"{_RUNTIME} no longer constructs {_GHOST_CLASS}; the ghost name may now be dead "
        "in both registries — re-measure and update DELEGATION.md §4"
    )


# ── The invariant, measured by driving the manager ───────────────────────────


class _Reportable:
    """A minimal backend that reports stats, so a name's presence is observable."""

    def get_stats(self) -> dict[str, int]:
        return {"entries": 1}


class _Silent:
    """A minimal backend that **cannot** report — no ``get_stats``."""


def _manager_with(backend: object):
    from aegis_ai.memory.memory_manager import MemoryManager

    return MemoryManager(
        advanced_memory=backend,
        episodic_memory=backend,
        semantic_memory=backend,
        skill_memory=backend,
        lesson_memory=backend,
        workflow_memory=backend,
        experiential_memory=backend,
        person_memory=backend,
        memory_store=backend,
        action_trace=backend,
    )


def test_a_constructed_manager_reports_every_backend_that_can_report() -> None:
    backend = _Reportable()
    mm = _manager_with(backend)

    reported = set(mm.get_stats())
    assert reported == set(_RECORDED_STATS_BACKENDS), (
        f"get_stats() reported {sorted(reported)}; the pin expects "
        f"{sorted(_RECORDED_STATS_BACKENDS)}"
    )

    # The fix, behaviourally: both backends that *are* registered and *can* report now
    # appear in the response the live route returns verbatim.
    for name in sorted(_RECORDED_STATS_BACKENDS):
        assert mm.get_backend(name) is backend, f"{name} is not registered"
    assert "person" in reported and "action_trace" in reported, (
        "person / action_trace are registered and define get_stats, so they must appear "
        "in the response — the under-report is back."
    )
    # …and the one incapable backend is the only absence.
    assert "store" not in reported, (
        "store appeared in get_stats() — MemoryStore defines no get_stats, so this "
        "assertion (and the recorded omission) must move together."
    )


def test_a_manager_whose_backends_cannot_report_reports_nothing() -> None:
    """The response is filtered by *capability*, not by name."""
    mm = _manager_with(_Silent())
    assert mm.get_stats() == {}, (
        "get_stats() reported backends that define no get_stats — the hasattr guard is gone"
    )


@pytest.mark.parametrize("name", sorted(_RECORDED_STATS_BACKENDS))
def test_every_reported_name_is_one_the_mapping_resolves(name: str) -> None:
    """A reported name the mapping cannot resolve would be the reverse defect."""
    resolvable = set(_mapping_keys(_func(_tree(_MM), "get_backend")))
    assert name in resolvable, (
        f"get_stats() iterates {name!r}, which get_backend() cannot resolve"
    )
