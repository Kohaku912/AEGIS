"""The shipped capability/executor manifest tree must be internally coherent.

``apps/`` holds one ``executor.json`` per capability served by a subprocess. Two
failure modes are invisible at runtime:

* an **unparseable** ``executor.json`` makes the executor *absent*, and the caller
  only sees ``EXECUTOR_NOT_FOUND`` — which is also the honest answer for the ~105
  capabilities that are served in-process. So a typo in the JSON is
  indistinguishable from a capability that was never meant to have an executor.
  (The registry records the cause since 2026-10-04, but nothing reads the shipped
  tree, so a bad manifest would only surface when that capability is first used.)
* an ``executor.json`` whose **capability was renamed or removed** — a dead
  manifest nothing reads.

No other test loads ``apps/`` from disk, so both are unpinned.

Measured 2026-10-04: 23 manifests on disk, 23 loaded, 0 load errors, 0 orphans.
The counts are derived from the filesystem, not hardcoded, so adding a
capability does not need this file edited — only *breaking* coherence does.
"""

from __future__ import annotations

import ast
from pathlib import Path

_AI_SERVER = Path(__file__).resolve().parents[1]
_CAPABILITIES = _AI_SERVER / "capabilities"
_APPS = _AI_SERVER / "apps"
_RUNTIME = _AI_SERVER / "src" / "aegis_ai" / "runtime.py"

# Floors, not counts: they exist so the pin cannot pass by scanning nothing.
_MIN_EXECUTORS = 20
_MIN_CAPABILITIES = 100


def _executor_manifests() -> list[Path]:
    return sorted(_APPS.rglob("executor.json"))


def test_production_binds_the_dirs_this_pin_scans() -> None:
    # The two artefacts must agree: if production stops reading ``apps/``, this pin
    # would keep passing while testing a tree nothing uses. Read the source of
    # truth (``runtime.py``) rather than a second copy of the answer.
    tree = ast.parse(_RUNTIME.read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CapabilityCatalog"
    ]
    assert len(calls) == 1, f"expected exactly one CapabilityCatalog(...) call, found {len(calls)}"
    kwargs = {k.arg: ast.unparse(k.value) for k in calls[0].keywords}
    assert "capabilities" in kwargs.get("capabilities_dir", ""), kwargs
    assert "apps" in kwargs.get("apps_dir", ""), kwargs


def test_every_shipped_executor_manifest_loads_without_error() -> None:
    from aegis_ai.folder_registry import ExecutorRegistry

    on_disk = _executor_manifests()
    registry = ExecutorRegistry(str(_APPS))
    result = registry.reload()

    assert result["errors"] == [], f"unloadable executor manifests: {result['errors']}"
    # Equality, not a floor: a manifest that loads nothing must be visible as a gap.
    assert result["new"] == len(on_disk), (
        f"{len(on_disk)} executor.json on disk but {result['new']} loaded"
    )


def test_every_shipped_capability_manifest_loads_without_error() -> None:
    from aegis_ai.folder_registry import FolderCapabilityRegistry

    registry = FolderCapabilityRegistry(str(_CAPABILITIES))

    assert registry.errors() == [], f"unloadable capability manifests: {registry.errors()}"
    assert registry.count() >= _MIN_CAPABILITIES, registry.count()


def test_no_shipped_executor_is_orphaned() -> None:
    # An executor whose capability does not exist is dead weight: nothing can route
    # to it, and its presence hides the typo. Compare *matched* to *on disk* so the
    # key format stays the registry's business.
    from aegis_ai.folder_registry import ExecutorRegistry, FolderCapabilityRegistry

    capabilities = FolderCapabilityRegistry(str(_CAPABILITIES))
    executors = ExecutorRegistry(str(_APPS))
    on_disk = _executor_manifests()

    matched = [m for m in capabilities.list_all() if executors.get(m) is not None]

    assert len(matched) == len(on_disk), (
        f"{len(on_disk)} executor.json on disk, but only {len(matched)} belong to a "
        f"shipped capability — at least one is orphaned (a capability was renamed or "
        f"removed without its executor directory)"
    )


def test_the_shipped_tree_is_not_vacuous() -> None:
    on_disk = _executor_manifests()
    assert len(on_disk) >= _MIN_EXECUTORS, f"only {len(on_disk)} executor manifests found"
    assert _CAPABILITIES.is_dir(), _CAPABILITIES
    # Every manifest must sit at <origin>/<server>/<app>/<action>/executor.json —
    # a shallower one cannot produce a key, so it would be silently skipped.
    for path in on_disk:
        depth = len(path.parent.relative_to(_APPS).parts)
        assert depth == 4, f"{path} is at depth {depth}, expected 4"
