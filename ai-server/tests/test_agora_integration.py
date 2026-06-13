"""Tests for AGORA integration with WorldState, PolicyEngine, ToolRegistry, ContextBuilder, and Verification."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from aegis_schema.models import Capability, RiskLevel, ServerType

from aegis_ai.context_builder import Context, ContextBuilder
from aegis_ai.integrations.agora.agora_poller import (
    AgoraPoller,
    AgoraPollResult,
    register_agora_capabilities,
)
from aegis_ai.integrations.agora.agora_service import AgoraService
from aegis_ai.integrations.agora.agora_types import (
    AgoraAccount,
    AgoraAuthor,
    AgoraCursor,
    AgoraFetchResult,
    AgoraPost,
    AgoraTaskDetection,
)
from aegis_ai.world.world_state_store import WorldStateStore
from aegis_ai.world.world_state_types import AgoraState as WSAgoraState
from aegis_ai.world.world_state_types import WorldState
from tool_registry import ToolRegistry


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _make_post(id: int, name: str = "User", body: str = "hi", mentions=None):
    return AgoraPost(
        id=id, thread_id=1,
        author=AgoraAuthor(id=10, name=name),
        body=body,
        mentions=[AgoraAuthor(id=m, name="AEGIS") for m in (mentions or [])],
    )


class TestAgoraStateInWorldState:
    def test_worldstate_has_agora_state(self):
        ws = WorldState()
        assert hasattr(ws, "agora_state")
        assert isinstance(ws.agora_state, WSAgoraState)

    def test_agora_state_defaults(self):
        state = WSAgoraState()
        assert state.me_name == ""
        assert state.last_cursor == 0
        assert state.unread_count == 0
        assert state.staleness == "fresh"

    def test_agora_state_to_context_string(self):
        state = WSAgoraState(
            me_name="AEGIS", me_id=1, last_cursor=42,
            unread_count=3, recent_posts_summary="3 new posts",
        )
        ctx = state.to_context_string()
        assert "AEGIS" in ctx
        assert "42" in ctx
        assert "unread=3" in ctx

    def test_agora_state_in_worldstate_context(self):
        ws = WorldState(version=1)
        ws.agora_state = WSAgoraState(
            me_name="AEGIS", last_observation_at=9999999999,
            recent_posts_summary="test",
        )
        ctx = ws.to_context_string()
        assert "AGORA" in ctx

    def test_agora_state_in_to_dict(self):
        ws = WorldState()
        ws.agora_state = WSAgoraState(me_name="AEGIS", unread_count=5)
        d = ws.to_dict()
        assert "agora_state_summary" in d
        assert "agora_state_raw" in d
        assert d["agora_state_raw"]["me_name"] == "AEGIS"
        assert d["agora_state_raw"]["unread_count"] == 5

    def test_agora_state_no_secrets(self):
        state = WSAgoraState(
            recent_posts_summary="api_key=sk-abcdef1234567890abcdef1234567890",
        )
        ctx = state.to_context_string()
        assert "sk-abcdef1234567890abcdef1234567890" not in ctx
        assert "MASKED" in ctx


class TestWorldStateStoreAgora:
    def test_update_from_agora_poll(self, tmpdir):
        store = WorldStateStore(data_dir=str(Path(tmpdir) / "ws"))
        poll_result = AgoraPollResult(
            success=True, new_posts=2,
            posts=[_make_post(11), _make_post(12)],
            mentions=[_make_post(11, mentions=[99])],
            tasks=[AgoraTaskDetection(is_task_request=True, requires_reply=True, reply_to=11)],
            summary="2 new posts",
        )
        store.update_from_agora_poll(poll_result)
        agora = store.state.agora_state
        assert agora.last_seen_post_id == 12
        assert agora.unread_count == 2
        assert agora.last_observation_at > 0

    def test_update_agora_account(self, tmpdir):
        store = WorldStateStore(data_dir=str(Path(tmpdir) / "ws"))
        store.update_agora_account(1, "AEGIS")
        assert store.state.agora_state.me_id == 1
        assert store.state.agora_state.me_name == "AEGIS"

    def test_update_agora_cursor(self, tmpdir):
        store = WorldStateStore(data_dir=str(Path(tmpdir) / "ws"))
        store.update_agora_cursor(42)
        assert store.state.agora_state.last_cursor == 42

    def test_agora_in_context_string(self, tmpdir):
        store = WorldStateStore(data_dir=str(Path(tmpdir) / "ws"))
        store.update_agora_account(1, "AEGIS")
        store.update_agora_cursor(42)
        ctx = store.state.to_context_string()
        assert "AGORA" in ctx


class TestPolicyEngineAgora:
    def test_agora_create_post_in_approval_patterns(self):
        from policy_engine import PolicyEngine
        engine = PolicyEngine()
        patterns = [p.pattern for p in engine._explicit_approval]
        assert any("agora" in p for p in patterns)

    def test_agora_read_in_permissive_patterns(self):
        from policy_engine import PolicyEngine
        engine = PolicyEngine()
        patterns = [p.pattern for p in engine._permissive_read]
        assert any("agora" in p for p in patterns)


class TestAgoraPollerIntegration:
    def test_poll_updates_world_state(self, tmpdir):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.is_configured = True
        mock_service.get_me.return_value = AgoraAccount(id=1, name="AEGIS")
        mock_service.get_cursor.return_value = AgoraCursor(last_read_post_id=0)
        mock_service.read_posts.return_value = AgoraFetchResult(
            posts=[_make_post(1, "User", "Hello AEGIS", mentions=[1])],
            max_post_id=1, has_new_posts=True,
        )
        mock_service.read_mentions.return_value = AgoraFetchResult(
            posts=[_make_post(1, mentions=[1])],
            max_post_id=1, has_new_posts=True,
        )
        mock_service.detect_task.return_value = AgoraTaskDetection(
            is_task_request=True, requires_reply=True, reply_to=1,
        )
        mock_service.update_cursor.return_value = AgoraCursor(last_read_post_id=1)

        poller = AgoraPoller(service=mock_service)
        result = poller.poll_once(dry_run=True)

        ws_store = WorldStateStore(data_dir=str(Path(tmpdir) / "ws"))
        ws_store.update_from_agora_poll(result)
        ws_store.update_agora_account(poller.state.me.id, poller.state.me.name)

        agora = ws_store.state.agora_state
        assert agora.me_name == "AEGIS"
        assert agora.last_seen_post_id == 1
        assert agora.unread_count == 1
        assert len(agora.pending_reply_candidates) == 1

    def test_poll_context_for_llm(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.is_configured = True
        mock_service.get_me.return_value = AgoraAccount(id=1, name="AEGIS")
        mock_service.get_cursor.return_value = AgoraCursor(last_read_post_id=10)
        mock_service.read_posts.return_value = AgoraFetchResult(
            posts=[_make_post(11, "User", "Hey AEGIS")],
            max_post_id=11, has_new_posts=True,
        )
        mock_service.read_mentions.return_value = AgoraFetchResult(posts=[], max_post_id=0)
        mock_service.detect_task.return_value = AgoraTaskDetection(is_task_request=False)

        poller = AgoraPoller(service=mock_service)
        poller.poll_once(dry_run=True)
        ctx = poller.get_context_string()

        assert "AGORA" in ctx
        assert "AEGIS" in ctx
        assert "11" in ctx or "unread" in ctx.lower()


class TestAgoraSecurity:
    def test_secret_in_body_blocks_post(self):
        svc = AgoraService()
        result = svc.create_post(body="my api_key=sk-abcdef1234567890abcdef1234567890")
        assert isinstance(result, dict)
        assert result["error"] == "blocked"

    def test_token_not_in_context(self):
        state = WSAgoraState(recent_posts_summary="Bearer abc123token")
        ctx = state.to_context_string()
        assert "abc123token" not in ctx

    def test_token_not_in_to_dict(self):
        ws = WorldState()
        ws.agora_state = WSAgoraState(recent_posts_summary="api_key=secret123")
        d = ws.to_dict()
        assert "secret123" not in str(d)


class TestAgoraTaskDetection:
    def test_mention_detected_as_task(self):
        svc = AgoraService()
        post = _make_post(1, "User", "AEGIS please help", mentions=[99])
        result = svc.detect_task(post, my_account_id=99)
        assert result.is_task_request is True
        assert result.requires_reply is True

    def test_own_post_ignored(self):
        svc = AgoraService()
        post = _make_post(1, "AEGIS", "I posted this")
        post.author.id = 99
        result = svc.detect_task(post, my_account_id=99)
        assert result.is_task_request is False

    def test_greeting_low_priority(self):
        svc = AgoraService()
        post = _make_post(1, "User", "こんにちは")
        result = svc.detect_task(post, my_account_id=99)
        assert result.is_task_request is False
        assert result.requires_reply is True
        assert result.confidence < 0.5


class TestAgoraCapabilities:
    def test_register_agora_capabilities(self):
        registry = ToolRegistry()
        register_agora_capabilities(registry)
        caps = registry.list_capabilities()
        agora_caps = [c for c in caps if c.id.startswith("ai.agora_")]
        assert len(agora_caps) == 8

    def test_agora_read_caps_are_read_only(self):
        registry = ToolRegistry()
        register_agora_capabilities(registry)
        for cap_id in [
            "ai.agora_get_me", "ai.agora_read_posts",
            "ai.agora_read_thread_posts", "ai.agora_read_mentions",
            "ai.agora_get_cursor", "ai.agora_draft_reply",
        ]:
            cap = registry.get_capability(cap_id)
            assert cap is not None, f"Missing {cap_id}"
            assert cap.risk_level == RiskLevel.READ_ONLY

    def test_agora_update_cursor_is_safe_action(self):
        registry = ToolRegistry()
        register_agora_capabilities(registry)
        cap = registry.get_capability("ai.agora_update_cursor")
        assert cap is not None
        assert cap.risk_level == RiskLevel.SAFE_ACTION

    def test_agora_create_post_requires_approval(self):
        registry = ToolRegistry()
        register_agora_capabilities(registry)
        cap = registry.get_capability("ai.agora_create_post")
        assert cap is not None
        assert cap.risk_level == RiskLevel.APPROVAL_REQUIRED
        assert cap.requires_approval is True
        assert "external_chat_send" in cap.side_effects

    def test_agora_caps_have_correct_server_type(self):
        registry = ToolRegistry()
        register_agora_capabilities(registry)
        for cap in registry.list_capabilities():
            if cap.id.startswith("ai.agora_"):
                assert cap.server_type == ServerType.AI

    def test_agora_caps_have_tags(self):
        registry = ToolRegistry()
        register_agora_capabilities(registry)
        for cap in registry.list_capabilities():
            if cap.id.startswith("ai.agora_"):
                assert "agora" in cap.tags


class TestAgoraContextBuilder:
    def test_context_has_agora_summary_field(self):
        ctx = Context()
        assert hasattr(ctx, "agora_summary")
        assert ctx.agora_summary == ""

    def test_context_builder_populates_agora_from_world_state(self, tmpdir):
        store = WorldStateStore(data_dir=str(Path(tmpdir) / "ws"))
        store.update_agora_account(1, "AEGIS")
        store.update_agora_cursor(42)
        builder = ContextBuilder(world_state_store=store)
        ctx = builder.build()
        assert "AEGIS" in ctx.agora_summary

    def test_context_builder_empty_when_no_store(self):
        builder = ContextBuilder()
        ctx = builder.build()
        assert ctx.agora_summary == ""

    def test_context_builder_agora_no_secrets(self, tmpdir):
        store = WorldStateStore(data_dir=str(Path(tmpdir) / "ws"))
        store.update_agora_account(1, "AEGIS")
        store.state.agora_state.recent_posts_summary = "api_key=sk-abcdef1234567890abcdef1234567890"
        builder = ContextBuilder(world_state_store=store)
        ctx = builder.build()
        assert "sk-abcdef1234567890abcdef1234567890" not in ctx.agora_summary


class TestAgoraModuleExports:
    def test_register_importable(self):
        from aegis_ai.integrations.agora import register_agora_capabilities
        assert register_agora_capabilities is not None

    def test_all_exports_importable(self):
        from aegis_ai.integrations.agora import (
            AgoraClient, AgoraService, AgoraPoller, AgoraState,
            AgoraPollResult, AgoraAccount, AgoraAuthor, AgoraPost,
            AgoraCursor, AgoraFetchResult, AgoraTaskDetection,
            AgoraReplyDraft, AgoraPostCreate, check_cooldown,
            register_agora_capabilities,
        )
        assert all([
            AgoraClient, AgoraService, AgoraPoller, AgoraState,
            AgoraPollResult, AgoraAccount, AgoraAuthor, AgoraPost,
            AgoraCursor, AgoraFetchResult, AgoraTaskDetection,
            AgoraReplyDraft, AgoraPostCreate, check_cooldown,
            register_agora_capabilities,
        ])
