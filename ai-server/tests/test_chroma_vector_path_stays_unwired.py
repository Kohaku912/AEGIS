"""The Chroma vector path is defined but unreachable — recorded, not wired.

Why this file exists
--------------------
``POST /api/memory/reload`` answers ``"chroma_synced": 0``. That zero is a **literal**, not
a measurement: nothing on the live path can sync Chroma, because the whole vector branch is
unreachable. Measured 2026-10-03, right after the shadowed legacy closure was deleted
(``DELEGATION.md`` §4 item 28) — that closure had been the **last** link in the chain:

1. ``ChromaSemanticMemory`` (``memory/chroma_semantic.py``) is constructed **only** inside
   ``create_semantic_memory`` (``memory/factory.py``).
2. ``create_semantic_memory`` has **no caller** — its only other mention is the module
   docstring's ``Usage:`` example, i.e. a **string literal** (the same shape as the
   event-driven core's docstring demo, §4 item 24).
3. So ``ChromaSemanticMemory`` is never instantiated in production. The runtime builds a
   plain ``SemanticMemory`` **directly**, and ``llm/memory_context.py`` does the same.
4. Therefore ``sync_from_advanced_memory`` has **no caller**, and ``chroma_available`` —
   the key ``ChromaSemanticMemory.get_stats`` emits — has **no reader**. On the live path it
   is not even produced, because the live backend is not that class.

⚠️ **Wiring this is not a free cleanup.** The class embeds through
``OpenAIEmbeddingFunction`` (``OPENAI_API_KEY``, default ``text-embedding-3-small``), so
turning the branch on would put **memory content** on the wire. That is the single
constraint's subject matter, and the mechanism that may carry it is the **voluntary ask**,
not a settings flag — so the decision is the owner's. This file only fixes the facts.

A second, entangled defect
--------------------------
The Chroma subclass extends ``SemanticMemory`` **from ``memory/semantic.py``** — which is
**not** the class the runtime uses. Two unrelated classes share the name:

===========================  ========  ===============================================
module                       methods   note
===========================  ========  ===============================================
``memory/semantic.py``            6    ``add``/``clear``/``get``/``list_by_category``/
                                        ``search``; **no ``get_stats``**
``memory/semantic_memory.py``    15    the **live** backend (``runtime.py``), with
                                        ``get_stats``, ``get_preferences``, ``supersede``…
===========================  ========  ===============================================

They share only ``__init__``/``add``/``search``, so they are different implementations, not
one class re-exported. The runtime and ``memory_context`` name ``semantic_memory``
explicitly — but the **package root** (``memory/__init__.py``) re-exports the **other** one,
so ``from aegis_ai.memory import SemanticMemory`` hands out the 6-method class. Nothing
imports it that way yet, which is why this is a **latent trap** rather than a live bug: the
next importer who does the natural thing gets a class with no ``get_stats`` and no
``get_preferences``, and nothing fails at import time.

Both halves are pinned here because they are one measurement (the import split), and because
they are **two decisions** (``DELEGATION.md`` §4 items 29 and 30).

The floors and the explicit positive controls below exist so no assertion can pass
vacuously: ``SemanticMemory`` **is** called in ``src/``, ``create_semantic_memory`` **is**
defined, and the route **does** serve the ``chroma_synced`` key.
"""

from __future__ import annotations

import ast
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SRC = _TESTS_DIR.parent / "src" / "aegis_ai"

_CHROMA_MODULE = _SRC / "memory" / "chroma_semantic.py"
_DEAD_SEMANTIC = _SRC / "memory" / "semantic.py"
_LIVE_SEMANTIC = _SRC / "memory" / "semantic_memory.py"
_FACTORY_MODULE = _SRC / "memory" / "factory.py"
_PACKAGE_INIT = _SRC / "memory" / "__init__.py"
_ROUTE_MODULE = _SRC / "web" / "routes" / "memory.py"
_RUNTIME_MODULE = _SRC / "runtime.py"

_CHROMA_CLASS = "ChromaSemanticMemory"
_PLAIN_CLASS = "SemanticMemory"
_FACTORY_FUNCTION = "create_semantic_memory"
_SYNC_METHOD = "sync_from_advanced_memory"
_AVAILABLE_KEY = "chroma_available"
_SYNCED_KEY = "chroma_synced"
_PACKAGE = "aegis_ai.memory"

#: Floor on the module count, so a broken walk cannot make the scans vacuous.
_MIN_MODULES = 300

#: The embedding provider the class reaches for. This is what makes wiring a constraint
#: question rather than a refactor.
_EMBEDDING_MARKERS = ("OpenAIEmbeddingFunction", "OPENAI_API_KEY")


def _modules(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _called_name(node: ast.Call) -> str:
    """The bare name a call goes through — ``f(...)`` or ``x.f(...)``."""

    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _call_sites(root: Path, name: str) -> set[str]:
    """Paths under ``root`` that **call** ``name`` — an ``ast.Call``, not a mention.

    A substring test would be satisfied by the name in a comment, a docstring or a
    ``Usage:`` example; measured 2026-10-03 on a sibling pin, a mutation that commented a
    construction out left a substring check green.
    """

    found: set[str] = set()
    for path in _modules(root):
        for node in ast.walk(_tree(path)):
            if isinstance(node, ast.Call) and _called_name(node) == name:
                found.add(path.relative_to(root).as_posix())
    return found


def _class_methods(path: Path, class_name: str) -> set[str]:
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                member.name
                for member in node.body
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
    raise AssertionError(f"{class_name} is not defined in {path}")


def _method_source(path: Path, method: str) -> str:
    """The source of a single function, for "this key is produced here" checks."""

    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.FunctionDef) and node.name == method:
            return ast.unparse(node)
    raise AssertionError(f"{method} is not defined in {path}")


def _bases(path: Path, class_name: str) -> list[str]:
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return [ast.unparse(base) for base in node.bases]
    raise AssertionError(f"{class_name} is not defined in {path}")


def _jsonify_dict(path: Path) -> ast.Dict:
    """The literal dict handed to ``jsonify`` in ``path``."""

    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Call) and _called_name(node) == "jsonify":
            for arg in node.args:
                if isinstance(arg, ast.Dict):
                    return arg
    raise AssertionError(f"no jsonify(dict) call in {path}")


def _imports_of(root: Path, module: str, name: str) -> set[str]:
    """Paths under ``root`` doing ``from <module> import <name>``."""

    found: set[str] = set()
    for path in _modules(root):
        for node in ast.walk(_tree(path)):
            if not isinstance(node, ast.ImportFrom) or (node.module or "") != module:
                continue
            if any(alias.name == name for alias in node.names):
                found.add(path.relative_to(root).as_posix())
    return found


# ── the scan is not blind ─────────────────────────────────────────────────────


def test_the_scan_reads_the_tree_and_the_subjects_exist() -> None:
    modules = _modules(_SRC)
    assert len(modules) >= _MIN_MODULES, f"only {len(modules)} modules under {_SRC}"

    for path in (
        _CHROMA_MODULE,
        _DEAD_SEMANTIC,
        _LIVE_SEMANTIC,
        _FACTORY_MODULE,
        _PACKAGE_INIT,
        _ROUTE_MODULE,
        _RUNTIME_MODULE,
    ):
        assert path.is_file(), f"{path} is missing — the scan is looking in the wrong tree"

    assert _CHROMA_CLASS in {n.name for n in ast.walk(_tree(_CHROMA_MODULE)) if isinstance(n, ast.ClassDef)}
    assert _SYNC_METHOD in _class_methods(_CHROMA_MODULE, _CHROMA_CLASS)
    assert _FACTORY_FUNCTION in {
        n.name for n in ast.walk(_tree(_FACTORY_MODULE)) if isinstance(n, ast.FunctionDef)
    }
    # Positive control: the live class really is reachable from source, so "no caller"
    # below is a finding about the Chroma branch and not about a broken extractor.
    assert _call_sites(_SRC, _PLAIN_CLASS), "no SemanticMemory call found anywhere — scan is broken"


# ── half one: the vector branch is unreachable ────────────────────────────────


def test_the_chroma_class_is_constructed_only_inside_the_dead_factory() -> None:
    sites = _call_sites(_SRC, _CHROMA_CLASS)
    assert sites == {"memory/factory.py"}, (
        f"ChromaSemanticMemory is constructed in {sorted(sites)}; the recorded fact is that "
        f"its only construction site is the factory"
    )


def test_the_factory_that_builds_it_has_no_caller() -> None:
    assert _call_sites(_SRC, _FACTORY_FUNCTION) == set(), (
        "create_semantic_memory now has a caller — the vector branch may be reachable"
    )
    assert _call_sites(_TESTS_DIR, _FACTORY_FUNCTION) == set(), (
        "create_semantic_memory is called from the tests — re-measure the chain"
    )
    # Positive control: the name is present, so the empty set is not a typo.
    assert _FACTORY_FUNCTION in _FACTORY_MODULE.read_text(encoding="utf-8")


def test_the_sync_method_has_no_caller() -> None:
    assert _call_sites(_SRC, _SYNC_METHOD) == set(), (
        "sync_from_advanced_memory now has a caller — the deleted closure was not the last one"
    )
    assert _call_sites(_TESTS_DIR, _SYNC_METHOD) == set()


def test_the_availability_key_is_produced_once_and_read_nowhere() -> None:
    holders = [
        path.relative_to(_SRC).as_posix()
        for path in _modules(_SRC)
        if _AVAILABLE_KEY in path.read_text(encoding="utf-8")
    ]
    assert holders == ["memory/chroma_semantic.py"], (
        f"{_AVAILABLE_KEY} now appears in {holders}; it used to be produced in exactly one place"
    )
    # It is a key in the class's own get_stats, i.e. a producer with no consumer.
    assert _AVAILABLE_KEY in _method_source(_CHROMA_MODULE, "get_stats")


def test_the_route_reports_a_literal_zero() -> None:
    body = _jsonify_dict(_ROUTE_MODULE)
    mapping: dict[object, ast.expr] = {}
    for key, value in zip(body.keys, body.values):
        if isinstance(key, ast.Constant):
            mapping[key.value] = value

    # Positive control: the key is served, so this is about the *value*, not its absence.
    assert _SYNCED_KEY in mapping, f"{_ROUTE_MODULE} no longer serves {_SYNCED_KEY}"
    value = mapping[_SYNCED_KEY]
    assert isinstance(value, ast.Constant) and value.value == 0, (
        f"{_SYNCED_KEY} is no longer a literal 0 — something now computes it: {ast.dump(value)}"
    )
    # And the route cannot be computing it from the sync method, which has no caller.
    assert _SYNC_METHOD not in _ROUTE_MODULE.read_text(encoding="utf-8")


def test_the_class_embeds_through_an_external_provider() -> None:
    text = _CHROMA_MODULE.read_text(encoding="utf-8")
    for marker in _EMBEDDING_MARKERS:
        assert marker in text, (
            f"{marker} is gone from {_CHROMA_MODULE.name}; re-check whether wiring the vector "
            f"branch still sends memory content off the machine"
        )


# ── half two: two unrelated classes share the name ────────────────────────────


def test_the_two_semantic_classes_are_different() -> None:
    dead = _class_methods(_DEAD_SEMANTIC, _PLAIN_CLASS)
    live = _class_methods(_LIVE_SEMANTIC, _PLAIN_CLASS)
    assert dead != live, "the two modules now define the same class — the collision changed shape"
    assert "get_stats" not in dead, "the dead class grew get_stats; re-read this pin"
    assert "get_stats" in live, "the live class lost get_stats; re-read this pin"


def test_the_live_runtime_uses_the_other_semantic_class() -> None:
    live_importers = _imports_of(_SRC, "aegis_ai.memory.semantic_memory", _PLAIN_CLASS)
    dead_importers = _imports_of(_SRC, "aegis_ai.memory.semantic", _PLAIN_CLASS)

    assert "runtime.py" in live_importers, (
        "the runtime no longer imports SemanticMemory from memory.semantic_memory"
    )
    assert "runtime.py" not in dead_importers, (
        "the runtime now imports the other class from memory.semantic — re-read this pin"
    )
    assert "runtime.py" not in _call_sites(_SRC, _CHROMA_CLASS), (
        "the runtime now constructs ChromaSemanticMemory — re-measure the whole chain"
    )
    # The dead module still has importers, so the collision is live code, not a vestige.
    assert dead_importers, "nothing imports the dead SemanticMemory — the collision is gone"


def test_the_package_reexport_points_at_the_dead_class() -> None:
    assert _imports_of(_SRC, _PACKAGE, _PLAIN_CLASS) == set(), (
        "something now imports SemanticMemory from the package root — the trap is live"
    )
    text = _PACKAGE_INIT.read_text(encoding="utf-8")
    assert "from aegis_ai.memory.semantic import SemanticMemory" in text, (
        "the package root no longer re-exports the dead class — re-read this pin"
    )
    assert "from aegis_ai.memory.semantic_memory import SemanticMemory" not in text


def test_the_chroma_subclass_extends_the_dead_class() -> None:
    assert _bases(_CHROMA_MODULE, _CHROMA_CLASS) == [_PLAIN_CLASS], (
        "ChromaSemanticMemory no longer subclasses SemanticMemory"
    )
    # Which one it extends is the point: it comes from semantic.py, the non-live module.
    assert "from aegis_ai.memory.semantic import" in _CHROMA_MODULE.read_text(encoding="utf-8")
