"""The memory/ Chroma vector chain is gone — deleted, not merely unwired.

Why this file exists
--------------------
This is the **inversion** of ``test_chroma_vector_path_stays_unwired.py`` (11 cases,
measured 2026-10-03, deleted 2026-10-08). That pin recorded a *live* surface that was
unreachable: ``POST /api/memory/reload`` answered ``"chroma_synced": 0`` — a literal,
not a measurement, because ``ChromaSemanticMemory`` had no construction site outside a
factory nothing called. The owner chose the delete branch (``DELEGATION.md`` §4 items
29 + 30), so the pin flips from "recorded" to **absence**.

What the deletion removed
-------------------------
- ``memory/chroma_semantic.py`` — ``ChromaSemanticMemory``,
  ``sync_from_advanced_memory`` and the ``chroma_available`` key.
- ``memory/factory.py``'s Chroma-selecting ``create_semantic_memory``. Its three JSONL
  siblings **stay**, and that is pinned below so the scope cannot creep.
- ``web/routes/memory.py``'s ``chroma_synced`` response key.
- ``memory/semantic.py``'s orphaned ``SemanticMemory`` class — the dead half of the
  duplicate-name pair. ``Fact`` stays: ``backup/import_restore.py`` builds one when it
  restores a semantic backup, which is what stopped the module from being dropped whole.
- ``memory/__init__.py`` now re-exports the **live** ``SemanticMemory``.

⚠️ ``SemanticMemory`` is deliberately **not** in the removed-name set. It is a *shared*
name: the live class still lives in ``memory/semantic_memory.py`` and the runtime imports
it explicitly. A bare-name absence scan over a shared name fails on a correct tree — the
same trap the deleted ``RoutingDecision`` set for ``test_intake_v1_surface_is_gone.py``.
Only ``ChromaSemanticMemory`` is exclusive to the deleted module.

⚠️ The capability / personal_data Chroma paths are **untouched** — they are live
(``capability_index.py``, ``personal_data/search.py``). This pin is about the *memory*
package's vector branch, not the word "chroma".

The floors and the positive controls exist so no assertion can pass vacuously: the walk
still sees ``SemanticMemory`` in ``src/``, the live class is still importable, and the
three surviving factory helpers are still defined.
"""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SRC = _TESTS_DIR.parent / "src"
_AEGIS = _SRC / "aegis_ai"

_MEMORY = _AEGIS / "memory"
_CHROMA_MODULE = _MEMORY / "chroma_semantic.py"
_DEAD_SEMANTIC = _MEMORY / "semantic.py"
_LIVE_SEMANTIC = _MEMORY / "semantic_memory.py"
_FACTORY_MODULE = _MEMORY / "factory.py"
_PACKAGE_INIT = _MEMORY / "__init__.py"
_ROUTE_MODULE = _AEGIS / "web" / "routes" / "memory.py"
_RUNTIME_MODULE = _AEGIS / "runtime.py"
_IMPORT_RESTORE = _AEGIS / "backup" / "import_restore.py"
_DASHBOARD_TEST = _TESTS_DIR / "test_dashboard_routes.py"

_CHROMA_MODULE_NAME = "aegis_ai.memory.chroma_semantic"
_CHROMA_CLASS = "ChromaSemanticMemory"
_PLAIN_CLASS = "SemanticMemory"
_FACT = "Fact"
_PACKAGE = "aegis_ai.memory"
_LIVE_MODULE = "aegis_ai.memory.semantic_memory"
_DEAD_MODULE = "aegis_ai.memory.semantic"

#: Tokens that must not survive anywhere under ``src/``.  ``SemanticMemory`` is
#: deliberately absent — it is a shared, live name (see the module docstring).
_REMOVED_TOKENS = (
    "chroma_semantic",
    "chroma_synced",
    "chroma_available",
    "ChromaSemanticMemory",
    "create_semantic_memory",
    "sync_from_advanced_memory",
)

#: The one name the removal shares with live code. Pinned from both sides below.
_SHARED_NAME = _PLAIN_CLASS

#: The three factory helpers the deletion must **not** have taken.
_SURVIVING_FACTORY_HELPERS = (
    "create_episodic_memory",
    "create_procedural_memory",
    "create_reflection_log",
)

#: Positive control for the text scan: this token is everywhere in ``src/``.
_CONTROL_TOKEN = _PLAIN_CLASS

#: Floor on the module count, so a broken walk cannot make the scans vacuous.
_MIN_SOURCE_FILES = 390


def _source_files() -> list[Path]:
    files = sorted(p for p in _SRC.rglob("*.py") if "__pycache__" not in p.parts)
    assert len(files) >= _MIN_SOURCE_FILES, f"only {len(files)} modules scanned; the walk is not reaching src/"
    return files


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _function_names(path: Path) -> set[str]:
    return {n.name for n in ast.walk(_tree(path)) if isinstance(n, ast.FunctionDef)}


def _class_defs(path: Path) -> list[str]:
    return [n.name for n in ast.walk(_tree(path)) if isinstance(n, ast.ClassDef)]


def _imports_of(module: str, name: str) -> set[str]:
    """Paths under ``src/`` doing ``from <module> import <name>``."""

    found: set[str] = set()
    for path in _source_files():
        for node in ast.walk(_tree(path)):
            if not isinstance(node, ast.ImportFrom) or (node.module or "") != module:
                continue
            if any(alias.name == name for alias in node.names):
                found.add(path.relative_to(_SRC).as_posix())
    return found


def _text_hits(token: str) -> list[str]:
    return [p.relative_to(_SRC).as_posix() for p in _source_files() if token in p.read_text(encoding="utf-8")]


def _jsonify_keys(path: Path) -> set[str]:
    """The literal string keys of the first ``jsonify({...})`` call in ``path``."""

    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "jsonify":
            for arg in node.args:
                if isinstance(arg, ast.Dict):
                    return {k.value for k in arg.keys if isinstance(k, ast.Constant)}
    raise AssertionError(f"no jsonify(dict) call in {path}")


# ── the scan is not blind ─────────────────────────────────────────────────────


def test_the_scan_reads_the_tree_and_the_subjects_exist() -> None:
    files = _source_files()
    assert len(files) >= _MIN_SOURCE_FILES

    for path in (
        _DEAD_SEMANTIC,
        _LIVE_SEMANTIC,
        _FACTORY_MODULE,
        _PACKAGE_INIT,
        _ROUTE_MODULE,
        _RUNTIME_MODULE,
        _IMPORT_RESTORE,
    ):
        assert path.is_file(), f"{path} is missing — the scan is looking in the wrong tree"

    # Positive controls: the live classes really are reachable from source, so the
    # absences below are findings about the deletion and not about a broken extractor.
    assert _PLAIN_CLASS in _class_defs(_LIVE_SEMANTIC), "the live SemanticMemory is gone"
    assert _FACT in _class_defs(_DEAD_SEMANTIC), "the Fact record type is gone"


# ── item 29: the Chroma chain is gone ─────────────────────────────────────────


def test_the_chroma_module_is_gone() -> None:
    assert not _CHROMA_MODULE.exists(), f"{_CHROMA_MODULE} still exists"
    assert importlib.util.find_spec(_CHROMA_MODULE_NAME) is None, (
        f"{_CHROMA_MODULE_NAME} is still importable — the deletion did not take"
    )
    # Control: the sibling module that must survive is still there.
    assert _LIVE_SEMANTIC.is_file(), "the live semantic module was deleted by mistake"


def test_no_source_file_names_a_removed_token() -> None:
    offenders = {token: _text_hits(token) for token in _REMOVED_TOKENS}
    offenders = {token: hits for token, hits in offenders.items() if hits}
    assert offenders == {}, f"a removed token survives under src/: {offenders}"

    # Control: the walk is not returning nothing — a live name is still found.
    assert _text_hits(_CONTROL_TOKEN), f"the scan found no {_CONTROL_TOKEN} anywhere — it is broken"


def test_the_factory_kept_its_jsonl_helpers() -> None:
    defined = _function_names(_FACTORY_MODULE)
    assert "create_semantic_memory" not in defined, "the Chroma selector survived"
    for helper in _SURVIVING_FACTORY_HELPERS:
        assert helper in defined, (
            f"{helper} was deleted too — the scope of the deletion has crept past the Chroma chain"
        )


def test_the_route_no_longer_serves_the_key() -> None:
    keys = _jsonify_keys(_ROUTE_MODULE)
    assert "chroma_synced" not in keys, "the retired key is back on the wire"
    # Control: the route still serves its real payload, so this is about the one key.
    assert {"ok", "summary"} <= keys, f"the route lost its payload: {sorted(keys)}"


def test_the_route_and_its_test_agree() -> None:
    """The dashboard test must not re-assert the key we deleted from the route."""

    text = _DASHBOARD_TEST.read_text(encoding="utf-8")
    assert 'assert "chroma_synced" in payload' not in text, (
        "test_dashboard_routes.py still asserts the retired key is served"
    )
    assert '"chroma_synced" not in payload' in text, (
        "test_dashboard_routes.py no longer pins the key's absence"
    )


# ── item 30: one SemanticMemory remains, and the root re-exports the live one ──


def test_exactly_one_semantic_memory_class_remains() -> None:
    holders = [p.relative_to(_SRC).as_posix() for p in _source_files() if _PLAIN_CLASS in _class_defs(p)]
    assert holders == ["aegis_ai/memory/semantic_memory.py"], (
        f"the package defines SemanticMemory in {holders}; exactly one (the live class) is expected"
    )
    # And the dead module kept its record type while losing the class.
    assert _PLAIN_CLASS not in _class_defs(_DEAD_SEMANTIC), "the orphaned class survived"
    assert _FACT in _class_defs(_DEAD_SEMANTIC), "Fact was deleted with the class — it has a live consumer"


def test_the_package_root_reexports_the_live_class() -> None:
    # Static: the root imports from the live module, not the dead one.
    assert _imports_of(_LIVE_MODULE, _PLAIN_CLASS) >= {"aegis_ai/memory/__init__.py"}, (
        "the package root no longer re-exports SemanticMemory from the live module"
    )
    assert _imports_of(_DEAD_MODULE, _PLAIN_CLASS) == set(), (
        "something still imports SemanticMemory from memory.semantic — the trap is live again"
    )

    # Runtime: ``from aegis_ai.memory import SemanticMemory`` hands out the live class.
    import aegis_ai.memory as memory_package

    reexported = memory_package.SemanticMemory
    assert reexported.__module__ == _LIVE_MODULE, (
        f"the package root hands out {reexported.__module__}, not the live class"
    )
    assert hasattr(reexported, "get_stats"), "the class the root hands out has no get_stats"


def test_the_live_fact_consumer_still_resolves() -> None:
    """``Fact`` was kept *because* this import exists — pin the reason, not just the name."""

    assert _imports_of(_DEAD_MODULE, _FACT) >= {"aegis_ai/backup/import_restore.py"}, (
        "backup/import_restore.py no longer imports Fact — re-measure whether semantic.py can be dropped whole"
    )


def test_the_removed_name_set_excludes_the_shared_name() -> None:
    """The exclusion is the point: a bare-name scan over a shared name fails on a good tree."""

    assert _SHARED_NAME not in _REMOVED_TOKENS, (
        "SemanticMemory was added to the removed-token set — it is a live, shared name"
    )
    assert _text_hits(_SHARED_NAME), "the shared name is nowhere in src/ — the exclusion has no subject"
    # And the exclusive name really is exclusive: it survives in no file.
    assert _text_hits(_CHROMA_CLASS) == [], f"{_CHROMA_CLASS} still appears in src/"
