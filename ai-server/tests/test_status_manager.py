from __future__ import annotations

import json

from aegis_ai.status.status_manager import ServerStatus, StatusManager


def test_status_manager_distinguishes_disabled_and_unconfigured(monkeypatch) -> None:
    monkeypatch.setenv("AEGIS_DISABLED_SERVERS", "room-server,dev-server")

    manager = StatusManager()
    snapshot = manager.check_now()

    assert snapshot["room-server"]["status"] == ServerStatus.DISABLED.value
    assert snapshot["room-server"]["mode"] == "disabled"
    assert "disabled" in snapshot["room-server"]["error"]
    assert snapshot["dev-server"]["status"] == ServerStatus.DISABLED.value

    monkeypatch.delenv("AEGIS_DISABLED_SERVERS")
    manager = StatusManager()
    snapshot = manager.check_now()
    assert snapshot["room-server"]["status"] == ServerStatus.UNCONFIGURED.value
    assert snapshot["dev-server"]["status"] == ServerStatus.UNCONFIGURED.value


def test_browser_health_preserves_structured_runtime_details(monkeypatch) -> None:
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return json.dumps(
                {
                    "status": "ok",
                    "version": "0.2.0",
                    "capabilities": 15,
                    "mode": "full",
                    "browser_use_available": True,
                    "playwright_available": True,
                    "profile_name": "default",
                }
            ).encode()

    monkeypatch.setattr("aegis_ai.status.status_manager.urllib.request.urlopen", lambda *_args, **_kwargs: Response())
    manager = StatusManager()

    status, details = manager._check_browser_health("browser-server", 50053)

    assert status == ServerStatus.ONLINE.value
    assert details["capabilities"] == 15
    assert details["browser_use_available"] is True
    assert details["playwright_available"] is True
