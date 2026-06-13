"""Tests for AGORA bridge — ToolRegistry, ApprovalQueue, Verification, Memory, InteractionPolicy integration."""

from __future__ import annotations

from unittest.mock import MagicMock

from aegis_ai.integrations.agora.agora_bridge import (
    create_agora_post_approval,
    evaluate_agora_notification,
    record_agora_event,
    register_agora_capabilities,
    verify_agora_cursor,
    verify_agora_post,
)
from aegis_ai.integrations.agora.agora_service import AgoraService
from aegis_ai.integrations.agora.agora_types import AgoraAuthor, AgoraFetchResult, AgoraPost


def _make_post(id: int, name: str = "User", body: str = "hi", thread_id: int = 1):
    return AgoraPost(
        id=id, thread_id=thread_id,
        author=AgoraAuthor(id=10, name=name), body=body,
    )


class TestToolRegistryIntegration:
    def test_register_agora_capabilities(self):
        mock_registry = MagicMock()
        registered = register_agora_capabilities(mock_registry)
        assert len(registered) == 8
        assert "ai.agora.get_me" in registered
        assert "ai.agora.read_posts" in registered
        assert "ai.agora.create_post" in registered
        assert mock_registry.register_capability.call_count == 8

    def test_capability_ids(self):
        mock_registry = MagicMock()
        registered = register_agora_capabilities(mock_registry)
        expected = [
            "ai.agora.get_me", "ai.agora.read_posts", "ai.agora.read_thread_posts",
            "ai.agora.read_mentions", "ai.agora.get_cursor", "ai.agora.update_cursor",
            "ai.agora.draft_reply", "ai.agora.create_post",
        ]
        assert registered == expected


class TestApprovalQueueIntegration:
    def test_create_agora_post_approval(self):
        mock_queue = MagicMock()
        mock_queue.submit.return_value = MagicMock(approval_id="app_1")
        create_agora_post_approval(
            mock_queue, thread_id=1, body="Hello AGORA", reply_to=None,
        )
        mock_queue.submit.assert_called_once()
        req = mock_queue.submit.call_args[0][0]
        assert req.capability_id == "agora.create_post"
        assert req.risk_level == "high"
        assert "外部チャット" in req.user_facing_summary
        assert "Hello AGORA" in req.user_facing_summary

    def test_approval_masks_secrets(self):
        mock_queue = MagicMock()
        create_agora_post_approval(
            mock_queue, thread_id=1,
            body="My api_key=sk-abcdef1234567890abcdef1234567890", reply_to=None,
        )
        req = mock_queue.submit.call_args[0][0]
        assert "sk-abcdef1234567890abcdef1234567890" not in req.user_facing_summary

    def test_approval_with_desire(self):
        mock_queue = MagicMock()
        create_agora_post_approval(
            mock_queue, thread_id=1, body="test", reply_to=5,
            source="desire_driven", source_desire="social_connection", frustration=0.7,
        )
        req = mock_queue.submit.call_args[0][0]
        assert req.source == "desire_driven"
        assert req.source_desire == "social_connection"


class TestVerificationIntegration:
    def test_verify_post_success(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.read_posts.return_value = AgoraFetchResult(
            posts=[_make_post(10, "AEGIS", "Hello", thread_id=1)],
            max_post_id=10,
        )
        result = verify_agora_post(mock_service, "Hello", 1, 10)
        assert result["verified"] is True
        assert result["post_id"] == 10
        assert result["body_match"] is True

    def test_verify_post_body_mismatch(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.read_posts.return_value = AgoraFetchResult(
            posts=[_make_post(10, "AEGIS", "Different", thread_id=1)],
            max_post_id=10,
        )
        result = verify_agora_post(mock_service, "Hello", 1, 10)
        assert result["verified"] is False
        assert result["body_match"] is False

    def test_verify_post_not_found(self):
        mock_service = MagicMock(spec=AgoraService)
        mock_service.read_posts.return_value = AgoraFetchResult(posts=[], max_post_id=0)
        result = verify_agora_post(mock_service, "Hello", 1, 999)
        assert result["verified"] is False

    def test_verify_cursor_match(self):
        mock_service = MagicMock(spec=AgoraService)
        from aegis_ai.integrations.agora.agora_types import AgoraCursor
        mock_service.get_cursor.return_value = AgoraCursor(last_read_post_id=42)
        result = verify_agora_cursor(mock_service, 42)
        assert result["verified"] is True

    def test_verify_cursor_mismatch(self):
        mock_service = MagicMock(spec=AgoraService)
        from aegis_ai.integrations.agora.agora_types import AgoraCursor
        mock_service.get_cursor.return_value = AgoraCursor(last_read_post_id=40)
        result = verify_agora_cursor(mock_service, 42)
        assert result["verified"] is False


class TestMemoryIntegration:
    def test_record_agora_event(self):
        mock_memory = MagicMock()
        record_agora_event(mock_memory, "post_created", post=_make_post(10, "AEGIS", "Hello"))
        mock_memory.add.assert_called_once()

    def test_record_event_no_memory(self):
        record_agora_event(None, "test")

    def test_record_event_masks_secrets(self):
        mock_memory = MagicMock()
        record_agora_event(
            mock_memory, "test",
            details={"token": "secret123", "body": "hello"},
        )
        record = mock_memory.add.call_args[0][0]
        assert "secret123" not in record.content


class TestInteractionPolicyIntegration:
    def test_mention_high_urgency(self):
        mock_policy = MagicMock()
        mock_policy.evaluate.return_value = MagicMock(
            decision=MagicMock(value="notify_now"),
        )
        decision = evaluate_agora_notification(
            mock_policy, category="approval_required",
            is_mention=True, is_task_request=True,
        )
        assert decision.decision.value == "notify_now"
        ctx = mock_policy.evaluate.call_args[0][0]
        assert ctx.urgency == "high"

    def test_normal_post_low_urgency(self):
        mock_policy = MagicMock()
        mock_policy.evaluate.return_value = MagicMock(
            decision=MagicMock(value="queue_for_later"),
        )
        evaluate_agora_notification(
            mock_policy, category="task_completed",
        )
        ctx = mock_policy.evaluate.call_args[0][0]
        assert ctx.urgency == "normal"


class TestModuleExports:
    def test_bridge_importable(self):
        from aegis_ai.integrations.agora import (
            create_agora_post_approval,
            register_agora_capabilities,
            verify_agora_post,
        )
        assert register_agora_capabilities is not None
        assert create_agora_post_approval is not None
        assert verify_agora_post is not None
