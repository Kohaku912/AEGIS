from __future__ import annotations

import base64
from pathlib import Path

from aegis_ai.capability_catalog import CapabilityCatalog
from aegis_ai.core_capabilities import AegisCoreCapabilityClient
from aegis_ai.integrations.agora.agora_types import AgoraAuthor, AgoraCursor, AgoraFetchResult, AgoraPost


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
    agora_post = catalog.resolve("ai-server.agora.post")
    assert agora_post is not None
    assert agora_post.requires_approval is True


class FakeMemoryManager:
    def search_memory(self, query: str, limit: int = 20) -> list[dict]:
        return [{"type": "semantic", "content": f"hit:{query}", "source": "fake"}][:limit]


class FakeAgora:
    def __init__(self) -> None:
        self.cursor_updates: list[int] = []

    def get_cursor(self) -> AgoraCursor:
        return AgoraCursor(last_read_post_id=10)

    def update_cursor(self, last_read_post_id: int) -> AgoraCursor:
        self.cursor_updates.append(last_read_post_id)
        return AgoraCursor(last_read_post_id=last_read_post_id)

    def read_posts(self, since_id: int = 0, limit: int = 50) -> AgoraFetchResult:
        if since_id == 10:
            return AgoraFetchResult(
                posts=[
                    AgoraPost(
                        id=11,
                        thread_id=1,
                        author=AgoraAuthor(id=2, name="tester"),
                        body="hello",
                    )
                ],
                max_post_id=11,
                has_new_posts=True,
            )
        return AgoraFetchResult(posts=[], max_post_id=since_id, has_new_posts=False)

    def create_post(self, thread_id: int = 1, body: str = "", reply_to: int | None = None) -> AgoraPost:
        return AgoraPost(id=20, thread_id=thread_id, author=AgoraAuthor(id=1, name="aegis"), body=body, reply_to=reply_to)


def test_memory_search_is_supported(tmp_path: Path) -> None:
    executor = FakeExecutor()
    client = AegisCoreCapabilityClient(
        data_dir=str(tmp_path / "data"),
        server_executor=executor,
        personal_managers={"memory_manager": FakeMemoryManager()},
    )

    result = client.invoke_capability("ai-server.memory.search", {"query": "project"})

    assert result["ok"] is True
    assert result["results"][0]["content"] == "hit:project"


def test_agora_read_posts_uses_unread_cursor_and_updates_once(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    fake = FakeAgora()
    client._agora = fake

    result = client.invoke_capability("ai-server.agora.read_posts", {"limit": 20})

    assert result["ok"] is True
    assert result["read_mode"] == "unread"
    assert result["cursor_before"] == 10
    assert result["cursor_after"] == 11
    assert fake.cursor_updates == [11]
    assert result["posts"][0]["id"] == 11


def test_agora_explicit_since_id_does_not_advance_cursor(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    fake = FakeAgora()
    client._agora = fake

    result = client.invoke_capability("ai-server.agora.read_posts", {"since_id": 5, "limit": 20})

    assert result["ok"] is True
    assert result["read_mode"] == "history"
    assert fake.cursor_updates == []
