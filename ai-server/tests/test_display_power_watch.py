from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_watch_module(monkeypatch: Any) -> ModuleType:
    monkeypatch.setenv("AEGIS_DISPLAY_TOKEN", "display-secret")
    path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "display"
        / "aegis-display-power-watch.py"
    )
    spec = importlib.util.spec_from_file_location("aegis_display_power_watch", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fetch_overview_uses_read_only_display_header(monkeypatch: Any) -> None:
    module = _load_watch_module(monkeypatch)
    captured: dict[str, str] = {}

    class Response:
        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self, _size: int = -1) -> bytes:
            return json.dumps({"schema_version": "ui-overview.v3"}).encode()

    def fake_urlopen(request: Any, timeout: int) -> Response:
        captured["token"] = request.get_header("X-aegis-display-token")
        captured["timeout"] = str(timeout)
        return Response()

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)

    assert module.fetch_overview()["schema_version"] == "ui-overview.v3"
    assert captured == {"token": "display-secret", "timeout": "4"}
