"""Tests for AGORA post guards and social reply-once behavior."""

from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.integrations.agora.agora_service import AgoraService
from aegis_ai.integrations.agora.agora_types import AgoraPost, AgoraAuthor
from aegis_ai.social.manager import SocialManager
from aegis_ai.social.models import SocialInboxItem, SocialInboxStatus


class _FakeClient:
    def __init__(self) -> None:
        self.posts: list[dict] = []
        self.is_configured = True

    def create_post(self, thread_id: int = 1, body: str = "", reply_to: int | None = None):
        self.posts.append({"thread_id": thread_id, "body": body, "reply_to": reply_to})
        return AgoraPost(
            id=len(self.posts),
            thread_id=thread_id,
            author=AgoraAuthor(id=2, name="aegis"),
            body=body,
            reply_to=reply_to,
        )


class _SuitableLLM:
    def generate(self, **kwargs):
        return SimpleNamespace(
            success=True,
            content='{"suitable": true, "reason": "genuine social reply", "category": "social_reply"}',
        )


class _UnsuitableLLM:
    def generate(self, **kwargs):
        return SimpleNamespace(
            success=True,
            content='{"suitable": false, "reason": "internal system status", "category": "unsuitable_internal"}',
        )


def test_exact_duplicate_body_is_blocked(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_SuitableLLM())
    assert isinstance(svc.create_post(body="hello friends"), AgoraPost)
    svc._guard["last_post_time"] = 0.0
    svc._save_guard()
    blocked = svc.create_post(body="hello friends", already_approved=True)
    assert blocked.get("error") == "duplicate"


def test_structural_duplicate_reply_to_is_blocked(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_SuitableLLM())
    first = svc.create_post(body="Thanks for the tip about chromadb.", reply_to=315)
    assert isinstance(first, AgoraPost)
    svc._guard["last_post_time"] = 0.0
    svc._save_guard()
    blocked = svc.create_post(body="Another chromadb note.", reply_to=315, already_approved=True)
    assert isinstance(blocked, dict)
    assert blocked.get("error") == "duplicate_reply"
    assert len(client.posts) == 1


def test_unsuitable_body_blocked_before_approval_path(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_UnsuitableLLM())
    blocked = svc.create_post(body="AEGIS: system status timeout approval pending")
    assert blocked.get("error") == "blocked"
    assert "suitability" in blocked
    assert client.posts == []


def test_already_approved_skips_suitability_but_keeps_structure(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_UnsuitableLLM())
    posted = svc.create_post(
        body="Thanks for asking — here is a careful reply.",
        reply_to=100,
        already_approved=True,
    )
    assert isinstance(posted, AgoraPost)
    assert len(client.posts) == 1


def test_own_author_posts_are_not_ingested(tmp_path) -> None:
    manager = SocialManager(
        data_dir=str(tmp_path / "inbox"),
        self_author_ids={2},
        self_author_names={"aegis"},
    )
    created = manager.ingest(
        "agora",
        [
            {"id": 10, "author": {"id": 2, "name": "aegis"}, "body": "own post", "thread_id": 1},
            {"id": 11, "author": {"id": 9, "name": "friend"}, "body": "hi", "thread_id": 1},
        ],
    )
    assert len(created) == 1
    assert created[0].external_message_id == "11"


def test_reply_once_skips_second_propose(tmp_path) -> None:
    manager = SocialManager(data_dir=str(tmp_path / "inbox"))
    first = SocialInboxItem(
        item_id="social_a",
        channel="agora",
        external_message_id="315",
        thread_id="1",
        author="friend",
        body="question",
        status=SocialInboxStatus.AWAITING_APPROVAL,
        draft_body="first draft",
    )
    second = SocialInboxItem(
        item_id="social_b",
        channel="agora",
        external_message_id="315",
        thread_id="1",
        author="friend",
        body="question",
        status=SocialInboxStatus.NEEDS_REPLY,
        draft_body="second draft",
    )
    manager._store.update(first)
    manager._store.update(second)
    result = manager.propose_reply("social_b")
    assert result.status == SocialInboxStatus.SKIPPED
    assert "Reply-once" in result.decision_reason
