from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
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
    assert captured == {"token": "display-secret", "timeout": "3.0"}


def test_compact_power_state_signature_ignores_poll_timestamp(monkeypatch: Any) -> None:
    module = _load_watch_module(monkeypatch)
    first = {
        "schema_version": "display-power-state.v1",
        "generated_at": 1000,
        "current_task": {"task_id": "task-1", "phase": "running"},
        "approvals": {"pending_count": 0, "ids": []},
        "servers": [{"server_id": "ai-server", "status": "online", "updated_at": 1000}],
        "presentations": [],
    }
    second = json.loads(json.dumps(first))
    second["generated_at"] = 2000
    second["servers"][0]["updated_at"] = 2000

    assert module.operational_signature(first) == module.operational_signature(second)
    assert module.keep_awake({**first, "keep_awake": True}) is True


def test_failure_backoff_is_bounded_and_display_fails_open(monkeypatch: Any) -> None:
    module = _load_watch_module(monkeypatch)

    assert module.failure_backoff_seconds(1) == module.POLL_SECONDS
    assert module.failure_backoff_seconds(99) == module.MAX_POLL_SECONDS
    assert module.should_fail_open(True, 99) is False
    assert module.should_fail_open(False, module.FAIL_OPEN_AFTER - 1) is False
    assert module.should_fail_open(False, module.FAIL_OPEN_AFTER) is True


def test_display_power_calls_xset_and_returns_success(monkeypatch: Any) -> None:
    module = _load_watch_module(monkeypatch)
    calls = []

    def run(command: list[str], **_kwargs: Any) -> SimpleNamespace:
        calls.append(command)
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(module.subprocess, "run", run)

    assert module.set_display_power(False) is True
    assert calls == [["xset", "dpms", "force", "off"]]


def test_display_power_returns_false_when_xset_fails(monkeypatch: Any) -> None:
    module = _load_watch_module(monkeypatch)
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=1,
            stderr="cannot open display",
        ),
    )

    assert module.set_display_power(True) is False
