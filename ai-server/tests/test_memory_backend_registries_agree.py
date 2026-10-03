"""``MemoryManager`` carries **three** registries of the same concept, and none agrees.

Why this file exists
--------------------
``aegis_ai/memory/memory_manager.py`` names its backends three times:

1. ``get_backend()``'s **docstring** — ``Names: advanced, …, association, action_trace`` (**11**).
2. ``get_backend()``'s **mapping** — the names it can actually resolve (**10**).
3. ``get_stats()``'s **list** — the names it iterates (**7**).

Measured 2026-10-03:

* The docstring advertises ``association``, which the mapping does **not** contain, so
  ``get_backend("association")`` returns ``None``. The name is not a typo of something
  imaginary: ``AssociationMemory`` is a real class (``memory/association_memory.py:79``)
  and it is **live** — ``runtime.py`` constructs it and hands it to
  ``CuriosityExploration`` — but it is registered on the **runtime**, not on the manager.
  The docstring conflates the two registries.
* ``get_stats()`` iterates **7** of the **10** resolvable names. The omission set is
  ``{person, store, action_trace}``. Of those, ``store`` is **justified**
  (``MemoryStore`` defines no ``get_stats``), but ``person`` and ``action_trace`` **do**
  define it (``PersonMemory.get_stats``, ``ActionTraceMemory.get_stats``) — so their
  stats are silently dropped from the live route ``GET /api/memory/stats``
  (``manager_routes.py:361``, which returns ``rt.memory_manager.get_stats()`` verbatim).

Impact is a **silently incomplete** response, not a crash: a client asking for memory
stats is told about 7 backends and given no way to learn that 2 more exist and are
counted by nobody. Fixing it (extend ``get_stats()``; correct the docstring or register
``association``) is an **owner decision** — wiring the manager to the runtime's
``AssociationMemory`` touches the composition root — so this pins the facts instead.

**This file will fail the day either registry is corrected.** That is the point: the pin
and the record must move together, deliberately.
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

#: Recorded 2026-10-03 — the **ghost**: documented by ``get_backend`` but absent from its
#: mapping. Pinned by **equality** in both directions: a second ghost fails, and so does
#: *removing* ``association`` from the docstring (the record would then be stale).
_RECORDED_GHOST = frozenset({"association"})

#: Recorded 2026-10-03 — the names ``get_stats()`` iterates. Equality: a new name is a
#: widening, a missing one a narrowing, and either must move this record.
_RECORDED_STATS_BACKENDS = frozenset(
    {
        "advanced",
        "episodic",
        "semantic",
        "skill",
        "lesson",
        "workflow",
        "experiential",
    }
)

#: The omitted names whose class **does** define ``get_stats`` — i.e. the omission is a
#: defect, not a capability gap. Measured, not assumed: the method is read from the class.
_OMITTED_BUT_CAPABLE = frozenset({"person", "action_trace"})

#: The omitted name whose class defines **no** ``get_stats`` — the omission is justified.
_OMITTED_AND_INCAPABLE = frozenset({"store"})

#: name → (module under ``aegis_ai/memory/``, class name), for the capability check.
_OMITTED_CLASS = {
    "person": ("person_memory.py", "PersonMemory"),
    "store": ("memory_store.py", "MemoryStore"),
    "action_trace": ("action_trace.py", "ActionTraceMemory"),
}

#: The class behind the ghost name, and the composition root that constructs it.
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
        "under-report stopped being user-visible; re-measure and update this pin together "
        "with DELEGATION.md §4."
    )


# ── Registry 1 vs 2: the docstring advertises a name the mapping cannot resolve ──


def test_get_backend_documents_exactly_the_names_it_resolves() -> None:
    node = _func(_tree(_MM), "get_backend")
    documented = set(_doc_names(node))
    resolvable = set(_mapping_keys(node))

    assert len(resolvable) >= _MIN_BACKENDS, (
        f"get_backend's mapping has only {len(resolvable)} names; the scan or the mapping "
        "changed shape"
    )
    assert documented - resolvable == set(_RECORDED_GHOST), (
        f"the set of names documented-but-not-resolvable changed: "
        f"{sorted(documented - resolvable)} != {sorted(_RECORDED_GHOST)}. A *new* ghost "
        "is a new broken contract; an *empty* set means the docstring was corrected — "
        "either way this pin and DELEGATION.md §4 must move together."
    )
    assert resolvable - documented == set(), (
        f"these names resolve but are undocumented: {sorted(resolvable - documented)} — "
        "the docstring is now incomplete"
    )


def test_the_documented_ghost_is_a_real_class_that_lives_on_the_runtime() -> None:
    """The ghost is a *registry conflation*, not a typo of something imaginary."""
    methods = _class_methods(_GHOST_CLASS_MODULE.name, _GHOST_CLASS)
    assert "get_stats" in methods, (
        f"{_GHOST_CLASS} no longer defines get_stats — the class behind the ghost name "
        "changed"
    )
    runtime_src = _source_text(_RUNTIME)
    assert f"{_GHOST_CLASS}(" in runtime_src, (
        f"{_RUNTIME} no longer constructs {_GHOST_CLASS}; the ghost name may now be dead "
        "in both registries — re-measure and update DELEGATION.md §4"
    )
    resolvable = set(_mapping_keys(_func(_tree(_MM), "get_backend")))
    assert "association" not in resolvable, (
        "the manager now resolves 'association' — the ghost was wired; re-measure"
    )


# ── Registry 2 vs 3: get_stats() silently drops two capable backends ─────────


def test_get_stats_covers_exactly_the_recorded_backends() -> None:
    node = _func(_tree(_MM), "get_stats")
    names = set(_list_names(node))
    assert names == set(_RECORDED_STATS_BACKENDS), (
        f"get_stats() now iterates {sorted(names)}, not "
        f"{sorted(_RECORDED_STATS_BACKENDS)}. A *new* name narrows the under-report; a "
        "*missing* one widens it — re-measure and re-record either way."
    )


def test_the_omission_set_is_exactly_the_recorded_one() -> None:
    tree = _tree(_MM)
    resolvable = set(_mapping_keys(_func(tree, "get_backend")))
    stats = set(_list_names(_func(tree, "get_stats")))
    omitted = resolvable - stats
    expected = set(_OMITTED_BUT_CAPABLE) | set(_OMITTED_AND_INCAPABLE)
    assert omitted == expected, (
        f"the set of registered backends missing from get_stats() changed: "
        f"{sorted(omitted)} != {sorted(expected)}"
    )


def test_the_omission_is_a_defect_for_two_names_and_justified_for_one() -> None:
    """Both directions: the two *can* report, the one *cannot*."""
    for name in sorted(_OMITTED_BUT_CAPABLE):
        module_name, class_name = _OMITTED_CLASS[name]
        assert "get_stats" in _class_methods(module_name, class_name), (
            f"{class_name}.get_stats is gone — the omission of {name!r} is no longer a "
            "defect, so this pin's premise is stale; re-measure and update DELEGATION.md "
            "§4 and this pin together."
        )
    for name in sorted(_OMITTED_AND_INCAPABLE):
        module_name, class_name = _OMITTED_CLASS[name]
        assert "get_stats" not in _class_methods(module_name, class_name), (
            f"{class_name} now defines get_stats — omitting {name!r} is no longer "
            "justified; the expected set in this pin must grow."
        )


# ── The defect, measured by driving the manager ──────────────────────────────


class _Backend:
    """A minimal backend that reports stats, so a name's presence is observable."""

    def get_stats(self) -> dict[str, int]:
        return {"entries": 1}


def test_a_constructed_manager_under_reports_its_own_backends() -> None:
    from aegis_ai.memory.memory_manager import MemoryManager

    backend = _Backend()
    mm = MemoryManager(
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

    reported = set(mm.get_stats())
    assert reported == set(_RECORDED_STATS_BACKENDS), (
        f"get_stats() reported {sorted(reported)}; the pin expects "
        f"{sorted(_RECORDED_STATS_BACKENDS)}"
    )

    # The defect, behaviourally: two backends that *are* registered and *can* report are
    # absent from the response the live route returns verbatim.
    for name in sorted(_OMITTED_BUT_CAPABLE):
        assert mm.get_backend(name) is backend, f"{name} is not registered"
        assert name not in reported, (
            f"{name} now appears in get_stats() — the under-report was fixed; re-measure "
            "and update DELEGATION.md §4 and this pin together."
        )

    # The ghost resolves to None while its class is live on the runtime.
    assert mm.get_backend("association") is None, (
        "the manager now resolves 'association' — the ghost was wired; re-measure"
    )


@pytest.mark.parametrize("name", sorted(_RECORDED_STATS_BACKENDS))
def test_every_reported_name_is_one_the_mapping_resolves(name: str) -> None:
    """A reported name the mapping cannot resolve would be the reverse defect."""
    resolvable = set(_mapping_keys(_func(_tree(_MM), "get_backend")))
    assert name in resolvable, (
        f"get_stats() iterates {name!r}, which get_backend() cannot resolve"
    )
