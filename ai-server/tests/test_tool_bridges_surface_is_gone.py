"""The Phase 6 ``tools/bridges/`` package was deleted — this pins its absence.

Measured 2026-10-08 (cycle 101, `DELEGATION.md` §4 item 53): the package was
**never wired**. On a bare import `list_bridges()` returned `[]` and
`bridge_for_capability("ai-server.workspace.repo_status")` returned `None`; the
control (`register_default_bridges()` called by hand) made three bridges appear
and a real `ToolBridge` come back from the lookup, so the empty result was real
and not a broken instrument. The only callers of `register_default_bridges` /
`bridge_for_capability` anywhere in the repository were in
`tests/agents/test_tool_bridges.py`, which was deleted with the package.

The old pin fixed the package's *behaviour* and its import-boundary invariants,
and every one of those invariants was scoped to the package's own directory
(`pkg_path.rglob("*.py")`) — so deleting the package loses no coverage outside
itself. The one orphan the old pin was the sole referent of, `dev_server_pb2`,
is pinned independently by `tests/test_generated_stubs_have_proto_sources.py`.

So this file pins the **absence**, in four parts:

1. the package directory and its three source files are gone;
2. no `src/` file names the removed API;
3. the three `ai-server.workspace.*` ids it declared appear nowhere in `src/`;
4. `aegis_ai.tools.__all__` no longer exports `bridges`.

Every scan carries a **control** — a sibling that must still be found — because
a walk that stops reading the tree satisfies every "nothing found" assertion.
"""
from __future__ import annotations

import ast
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "ai-server" / "src"
_TOOLS = _SRC / "aegis_ai" / "tools"
_DELETED_PACKAGE = _TOOLS / "bridges"
_DELETED_FILES = ("__init__.py", "base.py", "filesystem.py")

# The API the package exported. No src/ file may name any of these.
_REMOVED_NAMES = (
    "BridgeResult",
    "ToolBridge",
    "bridge_for_capability",
    "clear_bridges",
    "list_bridges",
    "register_bridge",
    "register_default_bridges",
)

# The three capability ids the package declared. All three resolved nowhere:
# they are in no manifest, so `CapabilityCatalog.resolve()` cannot return them.
_REMOVED_IDS = (
    "ai-server.workspace.repo_status",
    "ai-server.workspace.diff",
    "ai-server.workspace.test_results",
)

# Controls — siblings that must STILL be found, so a dead scan cannot pass.
_CONTROL_NAME = "mcp_gateway"
_CONTROL_ID = "ai-server.workspace.read_file"
_MIN_SOURCE_FILES = 380


def _source_files() -> tuple[Path, ...]:
    """Every `.py` under `src/`, excluding bytecode caches."""
    return tuple(sorted(p for p in _SRC.rglob("*.py") if "__pycache__" not in p.parts))


def _parsed(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _names_in(tree: ast.AST) -> set[str]:
    """Every identifier the module names: `Name` ids, `Attribute` attrs, import aliases."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
        elif isinstance(node, ast.ImportFrom):
            found.update(a.name for a in node.names)
        elif isinstance(node, ast.Import):
            found.update(a.name.rsplit(".", 1)[-1] for a in node.names)
    return found


def _string_constants(tree: ast.AST) -> set[str]:
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def _scan(collect) -> tuple[bool, list[str]]:  # type: ignore[no-untyped-def]
    """Walk `src/` and return (control_seen, offenders).

    The control flag is the whole point: an empty offender list is only
    evidence if the same walk found something it was supposed to find.
    """
    files = _source_files()
    assert len(files) >= _MIN_SOURCE_FILES, (
        f"found only {len(files)} .py files under {_SRC} — the scan is not reading the tree, "
        "so the assertions below would pass vacuously"
    )
    seen_control = False
    offenders: list[str] = []
    for path in files:
        tree = _parsed(path)
        hits = collect(tree)
        if _CONTROL_NAME in hits or _CONTROL_ID in hits:
            seen_control = True
        for name in _REMOVED_NAMES:
            if name in hits:
                offenders.append(f"{path.relative_to(_REPO)}: {name}")
        for cap in _REMOVED_IDS:
            if cap in hits:
                offenders.append(f"{path.relative_to(_REPO)}: {cap}")
    return seen_control, offenders


def test_the_deleted_package_and_its_modules_are_gone() -> None:
    assert not _DELETED_PACKAGE.exists(), (
        f"{_DELETED_PACKAGE} exists again. It was deleted 2026-10-08 "
        "(DELEGATION.md §4 item 53) because nothing wired it: `list_bridges()` was empty in "
        "production and the three capability ids it declared resolved nowhere."
    )
    for name in _DELETED_FILES:
        assert not (_DELETED_PACKAGE / name).exists(), f"{_DELETED_PACKAGE / name} came back"

    # Control: the rest of the tools package is still on disk, so the paths this
    # test computes are real paths and not the reason the assertions above passed.
    assert (_TOOLS / f"{_CONTROL_NAME}.py").is_file(), (
        f"{_TOOLS / (_CONTROL_NAME + '.py')} is missing — the path this test builds is wrong, "
        "so the assertions above would pass vacuously"
    )


def test_no_source_file_names_the_removed_bridge_api() -> None:
    seen_control, offenders = _scan(_names_in)
    assert seen_control, (
        f"no src/ file names {_CONTROL_NAME!r} — the walk stopped reading the tree, so an "
        "empty result would prove nothing"
    )
    assert not offenders, (
        "a src/ file names an identifier from the deleted `tools/bridges/` package:\n  "
        + "\n  ".join(offenders)
        + "\nThat package was deleted 2026-10-08 (DELEGATION.md §4 item 53). Re-adding the "
        "surface means re-adding the wiring and the capability ids with it, or nothing will "
        "call it."
    )


def test_the_removed_capability_ids_appear_nowhere_in_src() -> None:
    seen_control, offenders = _scan(_string_constants)
    assert seen_control, (
        f"no src/ file contains the string {_CONTROL_ID!r} — the walk stopped reading the "
        "tree, so an empty result would prove nothing"
    )
    assert not offenders, (
        "a src/ file contains a capability id from the deleted `tools/bridges/` package:\n  "
        + "\n  ".join(offenders)
        + "\nThese ids are in no manifest, so nothing can resolve them; the package that "
        "declared them was deleted 2026-10-08 (DELEGATION.md §4 item 53)."
    )


def test_the_tools_package_no_longer_exports_bridges() -> None:
    tree = _parsed(_TOOLS / "__init__.py")
    exported: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            continue
        if isinstance(node.value, ast.List):
            exported = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]

    assert exported, (
        f"{_TOOLS / '__init__.py'} no longer declares a non-empty `__all__` — this check would "
        "pass vacuously"
    )
    assert "bridges" not in exported, (
        f"`aegis_ai.tools.__all__` exports 'bridges' again: {exported}. The package was deleted "
        "2026-10-08 (DELEGATION.md §4 item 53)."
    )
    assert _CONTROL_NAME in exported, (
        f"`aegis_ai.tools.__all__` no longer exports {_CONTROL_NAME!r}: {exported} — the "
        "assertion above is only meaningful while the sibling that survived is still exported"
    )
