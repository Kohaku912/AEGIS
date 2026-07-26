from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace


def _load_executor_module():
    path = (
        Path(__file__).resolve().parents[1]
        / "apps"
        / "builtin"
        / "ai-server"
        / "agora"
        / "read_posts"
        / "executor.py"
    )
    spec = importlib.util.spec_from_file_location("agora_read_posts_executor", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _SyncResult:
    def __init__(self, posts):
        self._posts = posts

    def to_dict(self):
        if not self._posts:
            return {
                "ok": True,
                "message": "AGORA: No new posts.",
                "result": "AGORA: No new posts.",
                "summary": "AGORA: No new posts.",
                "posts": [],
            }
        ids = ", ".join(str(p.id) for p in self._posts)
        return {
            "ok": True,
            "message": f"AGORA: {len(self._posts)} new post(s): {ids}",
            "result": f"AGORA: {len(self._posts)} new post(s): {ids}",
            "summary": f"AGORA: {len(self._posts)} new post(s): {ids}",
            "posts": [{"id": p.id} for p in self._posts],
        }


def test_default_read_does_not_fall_back_when_cursor_has_no_unread(monkeypatch) -> None:
    executor = _load_executor_module()

    class FakeClient:
        calls = []

        def get_cursor(self):
            return executor.AgoraCursor(last_read_post_id=225)

        def list_posts(self, since_id: int = 0, limit: int = 50):
            self.calls.append(since_id)
            assert since_id == 225
            return executor.AgoraFetchResult(posts=[], max_post_id=0, has_new_posts=False, fetched_at=1)

    client = FakeClient()
    result, meta = executor._read_posts(client, since_id=0, limit=10)

    assert meta["fallback_recent"] is False
    assert meta["read_mode"] == "unread"
    assert meta["read_since_id"] == 225
    assert result.posts == []
    assert client.calls == [225]


def test_run_loads_env_and_returns_explicit_since_posts(monkeypatch) -> None:
    executor = _load_executor_module()
    monkeypatch.setenv("AGORA_TOKEN", "test-token")
    monkeypatch.setattr(executor, "_load_env_files", lambda: None)

    class FakeClient:
        def get_me(self):
            return executor.AgoraAccount(id=1, name="aegis")

        def get_cursor(self):
            return executor.AgoraCursor(last_read_post_id=223)

        def list_posts(self, since_id: int = 0, limit: int = 50):
            assert since_id == 211
            posts = [SimpleNamespace(id=post_id) for post_id in (212, 213, 214)]
            return executor.AgoraFetchResult(posts=posts, max_post_id=214, has_new_posts=True, fetched_at=1)

        def update_cursor(self, last_read_post_id: int):
            raise AssertionError("Historical reads must not update the shared cursor")

    monkeypatch.setattr(executor, "AgoraClient", FakeClient)
    monkeypatch.setattr(
        executor,
        "sync_agora_posts_to_memory",
        lambda **kwargs: _SyncResult(kwargs["posts"]),
    )

    result = executor.run({"since_id": 211, "limit": 10})

    assert result["ok"] is True
    assert result["read_mode"] == "history"
    assert result["unread_count"] == 0
    assert result["cursor_after"] == 223
    assert result["read_since_id"] == 211
    assert result["fetched_count"] == 3
    assert [post["id"] for post in result["posts"]] == [212, 213, 214]


def test_default_run_keeps_cursor_until_social_processing_finishes(monkeypatch) -> None:
    executor = _load_executor_module()
    monkeypatch.setenv("AGORA_TOKEN", "test-token")
    monkeypatch.setattr(executor, "_load_env_files", lambda: None)

    class FakeClient:
        def __init__(self):
            self.cursor = 223
            self.cursor_updates = []

        def get_me(self):
            return executor.AgoraAccount(id=1, name="aegis")

        def get_cursor(self):
            return executor.AgoraCursor(last_read_post_id=self.cursor)

        def list_posts(self, since_id: int = 0, limit: int = 50):
            posts = [SimpleNamespace(id=post_id) for post_id in (224, 225) if post_id > since_id]
            return executor.AgoraFetchResult(
                posts=posts,
                max_post_id=max((post.id for post in posts), default=0),
                has_new_posts=bool(posts),
                fetched_at=1,
            )

        def update_cursor(self, last_read_post_id: int):
            self.cursor_updates.append(last_read_post_id)
            self.cursor = last_read_post_id
            return executor.AgoraCursor(last_read_post_id=self.cursor)

    client = FakeClient()
    sync_calls = []
    monkeypatch.setattr(executor, "AgoraClient", lambda: client)
    monkeypatch.setattr(
        executor,
        "sync_agora_posts_to_memory",
        lambda **kwargs: sync_calls.append(kwargs["posts"]) or _SyncResult(kwargs["posts"]),
    )

    first = executor.run({"limit": 20})
    second = executor.run({"limit": 20})

    assert first["read_mode"] == "unread"
    assert first["unread_count"] == 2
    assert first["cursor_after"] == 223
    assert first["retrieved_through"] == 225
    assert first["processing_pending"] is True
    assert second["unread_count"] == 2
    assert second["cursor_after"] == 223
    assert client.cursor_updates == []
    assert len(sync_calls) == 2
