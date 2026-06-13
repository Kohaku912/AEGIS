"""Tests for AGORA integration — client, service, types, safety, and live tests."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aegis_ai.integrations.agora.agora_client import AgoraClient
from aegis_ai.integrations.agora.agora_service import AgoraService, _has_secret, check_cooldown
from aegis_ai.integrations.agora.agora_types import (
    AgoraAccount,
    AgoraAuthor,
    AgoraCursor,
    AgoraFetchResult,
    AgoraPost,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def client():
    return AgoraClient(token="test_token_12345", base_url="https://agora.kakunin.me")


@pytest.fixture()
def service(client):
    return AgoraService(client=client)


# ── Types ─────────────────────────────────────────────────────

class TestAgoraTypes:
    def test_post_from_dict(self):
        d = {
            "id": 42, "thread_id": 1,
            "author": {"id": 5, "name": "TestUser"},
            "body": "Hello AEGIS", "reply_to": None,
            "mentions": [{"id": 10, "name": "AEGIS"}],
            "attachments": [], "created_at": "2026-06-13T12:00:00Z",
        }
        post = AgoraPost.from_dict(d)
        assert post.id == 42
        assert post.thread_id == 1
        assert post.author.name == "TestUser"
        assert post.body == "Hello AEGIS"
        assert len(post.mentions) == 1
        assert post.mentions[0].name == "AEGIS"

    def test_fetch_result_summarize(self):
        posts = [
            AgoraPost(id=1, author=AgoraAuthor(id=1, name="Alice"), body="Hi"),
            AgoraPost(id=2, author=AgoraAuthor(id=2, name="Bob"), body="Hello"),
        ]
        result = AgoraFetchResult(posts=posts, max_post_id=2, has_new_posts=True)
        summary = result.summarize()
        assert "2 new post(s)" in summary
        assert "Alice" in summary
        assert "Bob" in summary

    def test_fetch_result_empty(self):
        result = AgoraFetchResult()
        assert "No new posts" in result.summarize()

    def test_task_detection_own_post(self):
        post = AgoraPost(id=1, author=AgoraAuthor(id=5, name="AEGIS"), body="test")
        svc = AgoraService()
        result = svc.detect_task(post, my_account_id=5)
        assert result.is_task_request is False

    def test_task_detection_mention(self):
        post = AgoraPost(
            id=1, author=AgoraAuthor(id=10, name="User"),
            body="AEGIS please check this",
            mentions=[AgoraAuthor(id=99, name="AEGIS")],
        )
        svc = AgoraService()
        result = svc.detect_task(post, my_account_id=99)
        assert result.is_task_request is True
        assert result.requires_reply is True
        assert result.confidence > 0.5

    def test_task_detection_greeting(self):
        post = AgoraPost(id=1, author=AgoraAuthor(id=10, name="User"), body="こんにちは")
        svc = AgoraService()
        result = svc.detect_task(post, my_account_id=99)
        assert result.is_task_request is False
        assert result.requires_reply is True


# ── Client ────────────────────────────────────────────────────

class TestAgoraClient:
    def test_not_configured(self):
        c = AgoraClient(token="", base_url="https://agora.kakunin.me")
        assert c.is_configured is False

    def test_configured(self, client):
        assert client.is_configured is True

    def test_no_token_returns_auth_error(self):
        c = AgoraClient(token="", base_url="https://agora.kakunin.me")
        result = c.get_me()
        assert isinstance(result, dict)
        assert result["error"] == "authentication_required"

    def test_get_me_success(self, client):
        mock_data = {"id": 1, "name": "AEGIS", "bio": "AI", "created_at": "2026-01-01"}
        with patch.object(client, "_request", return_value=mock_data):
            result = client.get_me()
        assert isinstance(result, AgoraAccount)
        assert result.name == "AEGIS"

    def test_list_posts_success(self, client):
        mock_data = [{
            "id": 1, "thread_id": 1,
            "author": {"id": 1, "name": "A"},
            "body": "hi", "reply_to": None,
            "mentions": [], "attachments": [],
            "created_at": "2026-01-01",
        }]
        with patch.object(client, "_request", return_value=mock_data):
            result = client.list_posts()
        assert isinstance(result, AgoraFetchResult)
        assert len(result.posts) == 1
        assert result.max_post_id == 1

    def test_create_post_success(self, client):
        mock_data = {
            "id": 10, "thread_id": 1,
            "author": {"id": 1, "name": "AEGIS"},
            "body": "test", "reply_to": None,
            "mentions": [], "attachments": [],
            "created_at": "2026-01-01",
        }
        with patch.object(client, "_request", return_value=mock_data):
            result = client.create_post(thread_id=1, body="test")
        assert isinstance(result, AgoraPost)
        assert result.id == 10

    def test_get_cursor_success(self, client):
        mock_data = {"last_read_post_id": 42}
        with patch.object(client, "_request", return_value=mock_data):
            result = client.get_cursor()
        assert isinstance(result, AgoraCursor)
        assert result.last_read_post_id == 42

    def test_update_cursor_success(self, client):
        mock_data = {"last_read_post_id": 50}
        with patch.object(client, "_request", return_value=mock_data):
            result = client.update_cursor(50)
        assert isinstance(result, AgoraCursor)
        assert result.last_read_post_id == 50

    def test_get_mentions_success(self, client):
        mock_data = [{
            "id": 5, "thread_id": 1,
            "author": {"id": 2, "name": "User"},
            "body": "@AEGIS hi", "reply_to": None,
            "mentions": [{"id": 1, "name": "AEGIS"}],
            "attachments": [], "created_at": "2026-01-01",
        }]
        with patch.object(client, "_request", return_value=mock_data):
            result = client.get_mentions()
        assert isinstance(result, AgoraFetchResult)
        assert len(result.posts) == 1

    def test_401_returns_auth_error(self, client):
        with patch("httpx.Client") as mock_cls:
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_cls.return_value)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_cls.return_value.request.return_value = mock_resp
            result = client._request("GET", "/api/v1/me")
        assert result["error"] == "authentication_required"

    def test_429_returns_rate_limited(self, client):
        with patch("httpx.Client") as mock_cls:
            mock_resp = MagicMock()
            mock_resp.status_code = 429
            mock_resp.headers = {"Retry-After": "30"}
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_cls.return_value)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_cls.return_value.request.return_value = mock_resp
            result = client._request("GET", "/api/v1/me")
        assert result["error"] == "rate_limited"

    def test_500_returns_server_error(self, client):
        with patch("httpx.Client") as mock_cls:
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_cls.return_value)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_cls.return_value.request.return_value = mock_resp
            result = client._request("GET", "/api/v1/me")
        assert result["error"] == "server_error"


# ── Service ───────────────────────────────────────────────────

class TestAgoraService:
    def test_secret_detection(self):
        assert _has_secret("api_key=sk-abcdef1234567890abcdef1234567890") is True
        assert _has_secret("password: mysecret123") is True
        assert _has_secret("Bearer token123") is True
        assert _has_secret("Hello world") is False

    def test_create_post_blocks_secret(self, service):
        result = service.create_post(body="My api_key=sk-abcdef1234567890abcdef1234567890 is here")
        assert isinstance(result, dict)
        assert result["error"] == "blocked"

    def test_create_post_blocks_empty(self, service):
        result = service.create_post(body="")
        assert isinstance(result, dict)
        assert result["error"] == "blocked"

    def test_draft_reply(self, service):
        post = AgoraPost(id=42, author=AgoraAuthor(id=1, name="User"), body="Hello")
        draft = service.draft_reply(post, context="Thanks!")
        assert draft.reply_to == 42
        assert draft.requires_approval is True

    def test_detect_task_request(self, service):
        post = AgoraPost(
            id=1, author=AgoraAuthor(id=10, name="User"),
            body="AEGIS please check this",
            mentions=[AgoraAuthor(id=99, name="AEGIS")],
        )
        result = service.detect_task(post, my_account_id=99)
        assert result.is_task_request is True

    def test_check_cooldown(self):
        result = check_cooldown()
        assert "cooldown_active" in result


# ── Module exports ────────────────────────────────────────────

class TestModuleExports:
    def test_imports(self):
        from aegis_ai.integrations.agora import (
            AgoraClient,
            AgoraService,
        )
        assert AgoraClient is not None
        assert AgoraService is not None


# ── Safety ────────────────────────────────────────────────────

class TestAgoraSafety:
    def test_token_not_in_error_messages(self, client):
        with patch("httpx.Client") as mock_cls:
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_cls.return_value)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_cls.return_value.request.side_effect = Exception("timeout")
            result = client._request("GET", "/api/v1/me")
        result_str = str(result)
        assert "test_token_12345" not in result_str

    def test_token_not_in_repr(self, client):
        r = repr(client)
        assert "test_token_12345" not in r

    def test_agora_in_permission_store(self, tmpdir):
        from aegis_ai.permissions.service_permission_store import ServicePermissionStore
        path = str(Path(tmpdir) / "perms.json")
        store = ServicePermissionStore(path=path)
        store.load_defaults()
        assert store.is_allowed("agora", "read") is True
        assert store.requires_approval("agora", "send") is True
        assert store.is_allowed("agora", "draft") is True
        assert store.is_allowed("agora", "summarize") is True
        assert store.requires_approval("agora", "delete") is True or store.is_allowed("agora", "delete") is False


# ── Live tests (require AGORA_TOKEN) ─────────────────────────

@pytest.mark.skipif(
    not os.environ.get("AGORA_TOKEN"),
    reason="AGORA_TOKEN not set",
)
class TestAgoraLiveRead:
    def test_get_me(self):
        svc = AgoraService()
        result = svc.get_me()
        assert isinstance(result, AgoraAccount)
        assert result.id > 0
        assert result.name

    def test_get_cursor(self):
        svc = AgoraService()
        result = svc.get_cursor()
        assert isinstance(result, AgoraCursor)
        assert result.last_read_post_id >= 0

    def test_read_posts(self):
        svc = AgoraService()
        result = svc.read_posts(limit=5)
        assert isinstance(result, AgoraFetchResult)
        for post in result.posts:
            assert post.id > 0
            assert post.author.name
            assert post.created_at

    def test_read_mentions(self):
        svc = AgoraService()
        result = svc.read_mentions(limit=5)
        assert isinstance(result, AgoraFetchResult)

    def test_token_not_in_post_body(self):
        svc = AgoraService()
        result = svc.read_posts(limit=1)
        if isinstance(result, AgoraFetchResult) and result.posts:
            token = os.environ.get("AGORA_TOKEN", "")
            for post in result.posts:
                assert token not in post.body


@pytest.mark.skipif(
    not os.environ.get("AEGIS_AGORA_LIVE_WRITE_TEST"),
    reason="AEGIS_AGORA_LIVE_WRITE_TEST not set",
)
class TestAgoraLiveWrite:
    def test_create_post(self):
        svc = AgoraService()
        test_body = "AEGIS接続テストです。外部投稿のApproval/Verification実機確認を行っています。"
        result = svc.create_post(thread_id=1, body=test_body)
        assert isinstance(result, AgoraPost)
        assert result.id > 0
        assert result.body == test_body
        assert result.thread_id == 1

    def test_update_cursor_after_post(self):
        svc = AgoraService()
        posts = svc.read_posts(limit=200)
        if isinstance(posts, AgoraFetchResult) and posts.max_post_id > 0:
            cursor = svc.update_cursor(posts.max_post_id)
            assert isinstance(cursor, AgoraCursor)
            assert cursor.last_read_post_id == posts.max_post_id
