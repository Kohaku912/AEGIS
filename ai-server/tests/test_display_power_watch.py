from __future__ import annotations

import importlib.util
from pathlib import Path


def _module():
    path = Path(__file__).resolve().parents[2] / "scripts" / "display" / "aegis-display-power-watch.py"
    spec = importlib.util.spec_from_file_location("aegis_display_power_watch", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _overview(task_status: str = "idle", pending_count: int = 0) -> dict:
    return {
        "core": {"data": {"mode": "IDLE"}},
        "current_task": {"data": {"status": task_status}},
        "attention": {"data": {"items": []}},
        "approvals": {"data": {"pending_count": pending_count}},
        "servers": {"data": {"items": []}},
        "presentations": {"data": {"items": []}},
    }


def test_display_power_signature_changes_only_with_operational_state() -> None:
    module = _module()
    first = _overview()
    second = _overview()
    second["generated_at"] = "later"
    assert module.operational_signature(first) == module.operational_signature(second)

    second["servers"]["data"]["items"] = [{"server_id": "pc-server", "status": "OFFLINE"}]
    assert module.operational_signature(first) != module.operational_signature(second)

    heartbeat = _overview()
    heartbeat["servers"]["data"]["items"] = [
        {
            "server_id": "pc-server",
            "status": "ONLINE",
            "last_seen": "2026-07-14T10:00:00Z",
        }
    ]
    later_heartbeat = _overview()
    later_heartbeat["servers"]["data"]["items"] = [
        {
            "server_id": "pc-server",
            "status": "ONLINE",
            "last_seen": "2026-07-14T10:00:05Z",
        }
    ]
    assert module.operational_signature(heartbeat) == module.operational_signature(
        later_heartbeat
    )


def test_display_power_stays_awake_for_execution_or_approval() -> None:
    module = _module()
    assert module.keep_awake(_overview("executing")) is True
    assert module.keep_awake(_overview(pending_count=1)) is True
    assert module.keep_awake(_overview()) is False
