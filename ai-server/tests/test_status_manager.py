from __future__ import annotations

from aegis_ai.status.status_manager import ServerStatus, StatusManager


def test_status_manager_marks_disabled_server_unconfigured(monkeypatch) -> None:
    monkeypatch.setenv("AEGIS_DISABLED_SERVERS", "room-server,dev-server")

    manager = StatusManager()
    snapshot = manager.check_now()

    assert snapshot["room-server"]["status"] == ServerStatus.UNCONFIGURED.value
    assert snapshot["room-server"]["mode"] == "unconfigured"
    assert "unconfigured" in snapshot["room-server"]["error"]
    assert snapshot["dev-server"]["status"] == ServerStatus.UNCONFIGURED.value
