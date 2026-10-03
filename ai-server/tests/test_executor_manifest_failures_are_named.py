"""An unreadable ``executor.json`` must be *named*, not silently dropped.

``ExecutorRegistry._load_one`` used to ``return`` on a manifest it could not read.
The consequence is not a crash — it is an **absence**: the executor is simply not
in the registry, so ``ExecutorRegistry.execute`` answers ``EXECUTOR_NOT_FOUND``
("No executor for <cap>") for a capability whose manifest loaded fine and whose
``executor.json`` is sitting on disk. The caller cannot tell "never written" from
"written and unparseable".

Its sibling loader, ``FolderCapabilityRegistry``, has always recorded this —
``self._errors`` + ``errors()`` + ``"errors"`` in ``reload()``. This pin holds the
executor registry to the same standard and holds ``CapabilityCatalog.reload`` to
*forwarding* what the executor registry returns (it previously discarded that
result outright, so the errors would have had no reader).

Measured 2026-10-04 by driving the classes with a malformed manifest, not by
reading them.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

# ---------------------------------------------------------------------------------------
# Fixtures — every directory under ``tmp_path``, so nothing touches the repo.
# ---------------------------------------------------------------------------------------


def _write_executor(root: Path, rel: str, payload: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return path


def _good(root: Path, action: str = "good") -> Path:
    return _write_executor(
        root,
        f"builtin/pc-server/app/{action}/executor.json",
        json.dumps({"type": "command", "command": "echo hi"}),
    )


def _capability_manifest(capabilities_dir: Path) -> None:
    path = capabilities_dir / "builtin" / "pc-server" / "app" / "good.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "id": "pc-server.app.good",
                "server_id": "pc-server",
                "app_id": "app",
                "action": "good",
                "operation_category": "test_operation",
                "title": "Sample",
                "description": "Sample capability",
                "risk": {"level": "safe", "requires_approval": False},
            }
        ),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------------------
# The registry records what it skipped.
# ---------------------------------------------------------------------------------------


def test_an_unparseable_executor_manifest_is_recorded_with_its_cause(tmp_path) -> None:
    from aegis_ai.folder_registry import ExecutorRegistry

    apps = tmp_path / "apps"
    _good(apps)
    broken = _write_executor(apps, "builtin/pc-server/app/broken/executor.json", "{ not json")

    registry = ExecutorRegistry(str(apps))

    # The defect's *shape*: the executor is absent, exactly as if never written.
    assert "builtin.pc-server.app.broken" not in registry._executors
    # …but the reason is now recoverable, and it names the cause, not just the fact.
    errors = registry.errors()
    assert len(errors) == 1, errors
    assert errors[0]["path"] == str(broken)
    assert "JSONDecodeError" in errors[0]["error"], errors[0]
    # The loadable manifest is untouched — the fix must not turn a skip into a failure.
    assert "builtin.pc-server.app.good" in registry._executors


def test_a_manifest_that_is_too_shallow_is_recorded(tmp_path) -> None:
    from aegis_ai.folder_registry import ExecutorRegistry

    apps = tmp_path / "apps"
    # A manifest directly under the origin root has 1 part, not <server>/<app>/<action>.
    shallow = _write_executor(apps, "builtin/executor.json", json.dumps({"type": "command"}))

    registry = ExecutorRegistry(str(apps))

    errors = registry.errors()
    assert len(errors) == 1, errors
    assert errors[0]["path"] == str(shallow)
    assert "<server>/<app>/<action>" in errors[0]["error"], errors[0]


def test_a_clean_registry_reports_no_errors(tmp_path) -> None:
    # Non-vacuity control: if ``_errors`` were always populated, the two tests above
    # would pass for the wrong reason.
    from aegis_ai.folder_registry import ExecutorRegistry

    apps = tmp_path / "apps"
    _good(apps)

    registry = ExecutorRegistry(str(apps))

    assert registry.errors() == []
    assert registry.reload()["errors"] == []
    assert sorted(registry._executors) == ["builtin.pc-server.app.good"]


def test_reload_reports_the_errors_it_found(tmp_path) -> None:
    from aegis_ai.folder_registry import ExecutorRegistry

    apps = tmp_path / "apps"
    _good(apps)
    _write_executor(apps, "builtin/pc-server/app/broken/executor.json", "{ not json")

    registry = ExecutorRegistry(str(apps))
    result = registry.reload()

    assert result["errors"], "reload() must carry the errors, or they have no reader"
    assert result["errors"][0]["error"].startswith("JSONDecodeError"), result["errors"]


def test_errors_do_not_persist_after_the_manifest_is_fixed(tmp_path) -> None:
    # ``_load`` clears ``_errors`` first. Without that, a repaired manifest keeps
    # reporting its old failure forever, which is its own kind of lie.
    from aegis_ai.folder_registry import ExecutorRegistry

    apps = tmp_path / "apps"
    broken = _write_executor(apps, "builtin/pc-server/app/broken/executor.json", "{ not json")

    registry = ExecutorRegistry(str(apps))
    assert len(registry.errors()) == 1

    broken.write_text(json.dumps({"type": "command", "command": "echo hi"}), encoding="utf-8")
    result = registry.reload()

    assert result["errors"] == [], result["errors"]
    assert "builtin.pc-server.app.broken" in registry._executors


# ---------------------------------------------------------------------------------------
# The catalog must *forward* them — it used to discard the executor result entirely.
# ---------------------------------------------------------------------------------------


def test_the_catalog_reload_carries_the_executor_errors(tmp_path) -> None:
    from aegis_ai.capability_catalog import CapabilityCatalog

    capabilities_dir = tmp_path / "capabilities"
    apps = tmp_path / "apps"
    _capability_manifest(capabilities_dir)
    _good(apps)
    _write_executor(apps, "builtin/pc-server/app/broken/executor.json", "{ not json")

    catalog = CapabilityCatalog(
        capabilities_dir=str(capabilities_dir),
        apps_dir=str(apps),
        data_dir=str(tmp_path / "data"),
    )
    result = catalog.reload()

    assert "executor_errors" in result, sorted(result)
    assert len(result["executor_errors"]) == 1, result["executor_errors"]
    assert "JSONDecodeError" in result["executor_errors"][0]["error"]


def test_the_two_error_channels_stay_separate(tmp_path) -> None:
    # ``errors`` means *capability* manifests; folding executor errors into it would
    # silently change what an existing consumer is counting.
    from aegis_ai.capability_catalog import CapabilityCatalog

    capabilities_dir = tmp_path / "capabilities"
    apps = tmp_path / "apps"
    _capability_manifest(capabilities_dir)
    _write_executor(apps, "builtin/pc-server/app/broken/executor.json", "{ not json")

    catalog = CapabilityCatalog(
        capabilities_dir=str(capabilities_dir),
        apps_dir=str(apps),
        data_dir=str(tmp_path / "data"),
    )
    result = catalog.reload()

    assert result["errors"] == [], result["errors"]
    assert len(result["executor_errors"]) == 1


def test_the_reload_route_returns_the_executor_errors(tmp_path) -> None:
    # End-to-end: the reader of ``catalog.reload()`` is the reload endpoint. Drive it
    # with a stub runtime (no tool registry, so the sync short-circuits).
    from aegis_ai.capability_catalog import CapabilityCatalog
    from aegis_ai.web.dashboard_legacy import _reload_capabilities_runtime

    capabilities_dir = tmp_path / "capabilities"
    apps = tmp_path / "apps"
    _capability_manifest(capabilities_dir)
    _write_executor(apps, "builtin/pc-server/app/broken/executor.json", "{ not json")

    catalog = CapabilityCatalog(
        capabilities_dir=str(capabilities_dir),
        apps_dir=str(apps),
        data_dir=str(tmp_path / "data"),
    )
    runtime = SimpleNamespace(capability_catalog=catalog, tool_registry=None, tool_broker=None)

    response = _reload_capabilities_runtime(runtime)

    assert response["registry_sync"] == {"registered": 0, "unregistered": 0, "skipped": 0}
    assert len(response["executor_errors"]) == 1, response
    assert "JSONDecodeError" in response["executor_errors"][0]["error"]


def test_a_catalog_without_apps_dir_does_not_invent_the_key(tmp_path) -> None:
    # ``apps_dir=""`` means no executor registry at all — the key must not appear as an
    # empty list, or a consumer cannot tell "no executor registry" from "no errors".
    from aegis_ai.capability_catalog import CapabilityCatalog

    capabilities_dir = tmp_path / "capabilities"
    _capability_manifest(capabilities_dir)

    catalog = CapabilityCatalog(
        capabilities_dir=str(capabilities_dir),
        data_dir=str(tmp_path / "data"),
    )
    result = catalog.reload()

    assert "executor_errors" not in result, sorted(result)
