"""Tests for AGORA poller — autonomous reading, state management, task detection."""

from __future__ import annotations

import shutil
import tempfile
from unittest.mock import MagicMock

import pytest

from aegis_ai.integrations.agora.agora_poller import AgoraPoller, AgoraPollResult, AgoraState
from aegis_ai.integrations.agora.agora_service import AgoraService
from aegis_ai.integrations.agora.agora_types import (
    AgoraAccount,
    AgoraAuthor,
    AgoraCursor,
    AgoraFetchResult,
    AgoraPost,
    AgoraTaskDetection,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _make_post(id: int, name: str = "User", body: str = "hi", reply_to=None, mentions=None):
    return AgoraPost(
        id=id, thread_id=1,
        author=AgoraAuthor(id=10, name=name),
        body=body, reply_to=reply_to,
        mentions=[AgoraAuthor(id=m, name="AEGIS") for m in (mentions or [])],
    )


class TestAgoraState:
    def test_create(self):
        state = AgoraState()
        assert state.staleness == "fresh"
        assert state.unread_count == 0

    def test_to_context_string(self):
        state = AgoraState(
            me=AgoraAccount(id=1, name="AEGIS"),
            last_cursor=42,
            unread_count=3,
            recent_posts_summary="3 new posts",
        )
        ctx = state.to_context_string()
        assert "AEGIS" in ctx
        assert "42" in ctx
        assert "Unread: 3" in ctx

    def test_to_dict(self):
        state = AgoraState(me=AgoraAccount(id=1, name="AEGIS"))
        d = state.to_dict()
        assert d["me_name"] == "AEGIS"
        assert d["staleness"] == "fresh"

    def test_mark_stale(self):
        state = AgoraState()
        state.staleness = "stale"
        assert state.staleness == "stale"

    def test_context_string_truncation(self):
        state = AgoraState(recent_posts_summary="x" * 1000)
        ctx = state.to_context_string(max_chars=100)
        assert len(ctx) <= 100


class TestAgoraPoller:
    def test_not_configured(self):
        svc = AgoraService(client=MagicMock(is_configured=False))
        poller = AgoraPoller(service=svc)
        assert poller.is_configured is False

    def test_poll_once_success(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.is_configured = True
        mock_service.get_me.return_value = AgoraAccount(id=1, name="AEGIS")
        mock_service.get_cursor.return_value = AgoraCursor(last_read_post_id=10)
        mock_service.read_posts.return_value = AgoraFetchResult(
            posts=[_make_post(11), _make_post(12)],
            max_post_id=12, has_new_posts=True,
        )
        mock_service.read_mentions.return_value = AgoraFetchResult(
            posts=[_make_post(11, mentions=[1])],
            max_post_id=11, has_new_posts=True,
        )
        mock_service.detect_task.side_effect = [
            AgoraTaskDetection(is_task_request=False, reason="Not a task."),
            AgoraTaskDetection(is_task_request=True, task_title="Task from AGORA"),
        ]
        mock_service.update_cursor.return_value = AgoraCursor(last_read_post_id=12)

        poller = AgoraPoller(service=mock_service)
        result = poller.poll_once(dry_run=True)

        assert result.success is True
        assert result.new_posts == 2
        assert result.tasks_detected == 1
        assert result.cursor_updated is False
        assert poller.state.me.name == "AEGIS"
        assert poller.state.last_cursor == 10

    def test_poll_once_dry_run_no_cursor_update(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.is_configured = True
        mock_service.get_me.return_value = AgoraAccount(id=1, name="AEGIS")
        mock_service.get_cursor.return_value = AgoraCursor(last_read_post_id=5)
        mock_service.read_posts.return_value = AgoraFetchResult(
            posts=[_make_post(6)], max_post_id=6, has_new_posts=True,
        )
        mock_service.read_mentions.return_value = AgoraFetchResult(posts=[], max_post_id=0)

        poller = AgoraPoller(service=mock_service)
        result = poller.poll_once(dry_run=True)

        assert result.success is True
        assert result.cursor_updated is False
        mock_service.update_cursor.assert_not_called()

    def test_poll_once_auth_error(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.is_configured = True
        mock_service.get_me.return_value = {"error": "authentication_required", "message": "No token."}

        poller = AgoraPoller(service=mock_service)
        result = poller.poll_once()

        assert result.success is False
        assert "token" in result.error.lower() or "auth" in result.error.lower()

    def test_poll_once_posts_error(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.is_configured = True
        mock_service.get_me.return_value = AgoraAccount(id=1, name="AEGIS")
        mock_service.get_cursor.return_value = AgoraCursor(last_read_post_id=0)
        mock_service.read_posts.return_value = {"error": "server_error", "message": "500"}

        poller = AgoraPoller(service=mock_service)
        result = poller.poll_once()

        assert result.success is False

    def test_poll_detects_mention_tasks(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.is_configured = True
        mock_service.get_me.return_value = AgoraAccount(id=99, name="AEGIS")
        mock_service.get_cursor.return_value = AgoraCursor(last_read_post_id=0)
        mock_service.read_posts.return_value = AgoraFetchResult(
            posts=[_make_post(1, body="AEGIS please check", mentions=[99])],
            max_post_id=1, has_new_posts=True,
        )
        mock_service.read_mentions.return_value = AgoraFetchResult(
            posts=[_make_post(1, mentions=[99])],
            max_post_id=1, has_new_posts=True,
        )
        mock_service.detect_task.return_value = AgoraTaskDetection(
            is_task_request=True,
            task_title="AGORA request",
            requires_reply=True,
            reply_to=1,
            confidence=0.8,
        )

        poller = AgoraPoller(service=mock_service)
        result = poller.poll_once(dry_run=True)

        assert result.tasks_detected == 1
        assert result.tasks[0].is_task_request is True
        assert 1 in poller.state.pending_reply_candidates

    def test_poll_skips_own_posts(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.is_configured = True
        mock_service.get_me.return_value = AgoraAccount(id=99, name="AEGIS")
        mock_service.get_cursor.return_value = AgoraCursor(last_read_post_id=0)
        mock_service.read_posts.return_value = AgoraFetchResult(
            posts=[_make_post(1, name="AEGIS", body="I posted")],
            max_post_id=1, has_new_posts=True,
        )
        mock_service.read_mentions.return_value = AgoraFetchResult(posts=[], max_post_id=0)
        mock_service.detect_task.return_value = AgoraTaskDetection(
            is_task_request=False, reason="Own post.",
        )

        poller = AgoraPoller(service=mock_service)
        result = poller.poll_once(dry_run=True)

        assert result.tasks_detected == 0

    def test_get_context_string(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.is_configured = True
        mock_service.get_me.return_value = AgoraAccount(id=1, name="AEGIS")
        mock_service.get_cursor.return_value = AgoraCursor(last_read_post_id=0)
        mock_service.read_posts.return_value = AgoraFetchResult(posts=[], max_post_id=0)
        mock_service.read_mentions.return_value = AgoraFetchResult(posts=[], max_post_id=0)

        poller = AgoraPoller(service=mock_service)
        poller.poll_once(dry_run=True)
        ctx = poller.get_context_string()

        assert "AGORA" in ctx
        assert "AEGIS" in ctx

    def test_mark_stale(self):
        poller = AgoraPoller()
        poller.mark_stale()
        assert poller.state.staleness == "stale"


class TestAgoraPollResult:
    def test_create(self):
        result = AgoraPollResult(success=True, new_posts=3)
        assert result.success is True
        assert result.new_posts == 3


class TestModuleExports:
    def test_poller_importable(self):
        from aegis_ai.integrations.agora import AgoraPoller, AgoraPollResult, AgoraState
        assert AgoraPoller is not None
        assert AgoraPollResult is not None
        assert AgoraState is not None
