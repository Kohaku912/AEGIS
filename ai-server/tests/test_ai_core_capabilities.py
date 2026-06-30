from __future__ import annotations

import base64
from pathlib import Path

from aegis_ai.capability_catalog import CapabilityCatalog
from aegis_ai.core_capabilities import AegisCoreCapabilityClient


class FakeExecutor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def execute_capability(self, capability_id: str, params: dict | None = None) -> dict:
        params = params or {}
        self.calls.append((capability_id, params))
        if capability_id == "android-server.overlay.show":
            return {"shown": True, "connection_mode": "reverse_stream"}
        if capability_id == "pc-server.overlay.show_rich":
            return {"shown": True, "response": "Displayed"}
        return {"error": "unexpected capability"}


def _client(tmp_path: Path) -> tuple[AegisCoreCapabilityClient, FakeExecutor]:
    executor = FakeExecutor()
    return AegisCoreCapabilityClient(data_dir=str(tmp_path / "data"), server_executor=executor), executor


def test_workspace_write_read_and_list(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)

    written = client.invoke_capability(
        "ai-server.workspace.write_file",
        {"relative_path": "notes/hello.txt", "content": "hello aegis"},
    )
    assert written["ok"] is True

    read = client.invoke_capability(
        "ai-server.workspace.read_file",
        {"relative_path": "notes/hello.txt"},
    )
    assert read["content"] == "hello aegis"

    listed = client.invoke_capability(
        "ai-server.workspace.list_files",
        {"relative_dir": "notes"},
    )
    assert listed["ok"] is True
    assert listed["files"][0]["relative_path"] == "notes\\hello.txt" or listed["files"][0]["relative_path"] == "notes/hello.txt"


def test_workspace_rejects_path_escape(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)

    result = client.invoke_capability(
        "ai-server.workspace.write_file",
        {"relative_path": "../outside.txt", "content": "nope"},
    )

    assert result["ok"] is False
    assert "workspace" in result["error"].lower()


def test_broadcast_overlay_sends_text_to_pc_and_android(tmp_path: Path) -> None:
    client, executor = _client(tmp_path)

    result = client.invoke_capability(
        "ai-server.notification.broadcast_overlay",
        {"message": "テスト通知", "title": "AEGIS", "duration_ms": 3000},
    )

    assert result["ok"] is True
    assert set(result["delivered"]) == {"pc", "android"}
    assert [call[0] for call in executor.calls] == [
        "pc-server.overlay.show_rich",
        "android-server.overlay.show",
    ]
    assert executor.calls[0][1]["body"] == "テスト通知"
    assert executor.calls[1][1]["text"] == "テスト通知"


def test_broadcast_overlay_includes_workspace_image(tmp_path: Path) -> None:
    client, executor = _client(tmp_path)
    image_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADElEQVR42mP8z8BQDwAFgwJ/luzG8QAAAABJRU5ErkJggg=="
    )
    (client.workspace_dir / "images").mkdir(parents=True)
    (client.workspace_dir / "images" / "dot.png").write_bytes(image_bytes)

    result = client.invoke_capability(
        "ai-server.notification.broadcast_overlay",
        {"message": "画像通知", "image_path": "images/dot.png"},
    )

    assert result["ok"] is True
    pc_payload = executor.calls[0][1]
    android_payload = executor.calls[1][1]
    assert pc_payload["image_mime"] == "image/png"
    assert android_payload["image_mime"] == "image/png"
    assert pc_payload["image_base64"]
    assert android_payload["image_base64"]


def test_broadcast_overlay_rejects_image_outside_workspace(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"not really an image")

    result = client.invoke_capability(
        "ai-server.notification.broadcast_overlay",
        {"message": "bad", "image_path": str(outside)},
    )

    assert result["ok"] is False
    assert result["code"] == "INVALID_IMAGE_PATH"


def test_new_manifests_load_from_catalog() -> None:
    catalog = CapabilityCatalog(capabilities_dir="capabilities", apps_dir="apps")
    for cap_id in {
        "ai-server.notification.broadcast_overlay",
        "ai-server.workspace.write_file",
        "ai-server.workspace.read_file",
        "ai-server.workspace.list_files",
        "pc-server.overlay.show_rich",
    }:
        assert catalog.resolve(cap_id) is not None
