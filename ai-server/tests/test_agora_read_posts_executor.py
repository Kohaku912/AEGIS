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


def test_default_read_falls_back_to_recent_posts_when_cursor_has_no_unread(monkeypatch) -> None:
    executor = _load_executor_module()

    class FakeClient:
        def get_cursor(self):
            return executor.AgoraCursor(last_read_post_id=225)

        def list_posts(self, since_id: int = 0, limit: int = 50):
            if since_id == 225:
                return executor.AgoraFetchResult(posts=[], max_post_id=0, has_new_posts=False, fetched_at=1)
            assert since_id == 215
            posts = [SimpleNamespace(id=post_id) for post_id in range(216, 226)]
            return executor.AgoraFetchResult(posts=posts, max_post_id=225, has_new_posts=True, fetched_at=1)

    result, meta = executor._read_posts(FakeClient(), since_id=0, limit=10)

    assert meta["fallback_recent"] is True
    assert meta["read_since_id"] == 215
    assert [post.id for post in result.posts] == list(range(216, 226))


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
            return executor.AgoraCursor(last_read_post_id=223)

    monkeypatch.setattr(executor, "AgoraClient", FakeClient)
    monkeypatch.setattr(
        executor,
        "sync_agora_posts_to_memory",
        lambda **kwargs: _SyncResult(kwargs["posts"]),
    )

    result = executor.run({"since_id": 211, "limit": 10})

    assert result["ok"] is True
    assert result["read_since_id"] == 211
    assert result["fetched_count"] == 3
    assert [post["id"] for post in result["posts"]] == [212, 213, 214]
