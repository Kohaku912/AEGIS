"""Tests for AGORA post guards and social reply-once behavior."""

from __future__ import annotations

import json
from types import SimpleNamespace

from aegis_ai.integrations.agora.agora_service import AgoraService, bodies_are_near_duplicates
from aegis_ai.integrations.agora.agora_types import AgoraAuthor, AgoraPost
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


class _ReplyDraftLLM:
    def __init__(self, draft: str) -> None:
        self._draft = draft

    def generate(self, **kwargs):
        payload = {
            "decision": "reply",
            "reason": "friendly reply",
            "directed_to_aegis": True,
            "mentions_user": False,
            "question_detected": True,
            "reply_expected": True,
            "relevance": 0.9,
            "urgency": 0.2,
            "sentiment": "positive",
            "draft_body": self._draft,
        }
        return SimpleNamespace(success=True, content=json.dumps(payload))


def test_exact_duplicate_body_is_advisory_only(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_SuitableLLM())
    assert isinstance(svc.create_post(body="hello friends"), AgoraPost)
    posted = svc.create_post(body="hello friends", already_approved=True)
    assert isinstance(posted, AgoraPost)
    assert len(client.posts) == 2


def test_near_duplicate_helper_still_detects_similarity(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_SuitableLLM())
    first = (
        "k3320138さん、chromadbの件ありがとうございます。"
        "メモリ構造の指摘を踏まえて整理します。"
    )
    near = (
        "k3320138さん、chromadbの件ありがとうございます。"
        "メモリ構造の指摘を踏まえて、これから整理します。"
    )
    assert bodies_are_near_duplicates(first, near)
    assert isinstance(svc.create_post(body=first), AgoraPost)
    posted = svc.create_post(body=near, already_approved=True)
    assert isinstance(posted, AgoraPost)


def test_reply_to_history_is_tracked_as_advice_only(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_SuitableLLM())
    first = svc.create_post(body="Thanks for the tip about chromadb.", reply_to=315)
    assert isinstance(first, AgoraPost)
    posted = svc.create_post(body="Another chromadb note.", reply_to=315, already_approved=True)
    assert isinstance(posted, AgoraPost)
    assert len(client.posts) == 2
    assert svc.has_replied_to(315) is True


def test_post_avoidance_context_lists_replied_and_recent(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_SuitableLLM())
    assert isinstance(svc.create_post(body="Fresh social note about learning.", reply_to=410), AgoraPost)
    ctx = svc.post_avoidance_context()
    assert 410 in ctx["replied_to_ids"]
    assert any("Fresh social note" in body for body in ctx["recent_bodies"])
    assert ctx["recent_post_count_30m"] >= 1
    assert "not hard rules" in ctx["guidance"]


def test_post_avoidance_context_reports_recent_cadence_without_blocking(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_SuitableLLM())
    assert isinstance(svc.create_post(body="First thoughtful reply.", reply_to=101), AgoraPost)
    assert isinstance(svc.create_post(body="Second thoughtful reply.", reply_to=102, already_approved=True), AgoraPost)
    assert isinstance(svc.create_post(body="Third thoughtful reply.", reply_to=103, already_approved=True), AgoraPost)
    assert isinstance(svc.create_post(body="Fourth reply would be too much.", reply_to=104, already_approved=True), AgoraPost)
    ctx = svc.post_avoidance_context()
    assert ctx["recent_post_count_30m"] >= 4


def test_post_avoidance_context_reports_recent_top_level_posts_without_blocking(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_SuitableLLM())
    assert isinstance(svc.create_post(body="Public project update about memory architecture."), AgoraPost)
    assert isinstance(svc.create_post(body="Public project update about AGORA etiquette guardrails.", already_approved=True), AgoraPost)
    assert isinstance(
        svc.create_post(body="Public project update about autonomous loop selection changes.", already_approved=True),
        AgoraPost,
    )
    ctx = svc.post_avoidance_context()
    assert ctx["recent_top_level_count_6h"] >= 3


def test_unsuitable_body_is_not_hard_blocked(tmp_path) -> None:
    client = _FakeClient()
    svc = AgoraService(client=client, data_dir=tmp_path / "social", llm=_UnsuitableLLM())
    posted = svc.create_post(body="AEGIS: system status timeout approval pending")
    assert isinstance(posted, AgoraPost)
    assert len(client.posts) == 1


def test_already_approved_skips_suitability(tmp_path) -> None:
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
        status=SocialInboxStatus.DRAFTED,
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


def test_triage_treats_already_replied_as_advice_not_hard_skip(tmp_path) -> None:
    calls = {"n": 0}

    class _CountingLLM:
        def generate(self, **kwargs):
            calls["n"] += 1
            return SimpleNamespace(success=True, content='{"decision":"observe_more","reason":"already replied, so probably no need"}')

    manager = SocialManager(data_dir=str(tmp_path / "inbox"), llm=_CountingLLM())
    manager.set_post_avoidance_provider(
        lambda: {"replied_to_ids": [315], "recent_bodies": [], "guidance": "skip"}
    )
    item = SocialInboxItem(
        item_id="social_c",
        channel="agora",
        external_message_id="315",
        thread_id="1",
        author="friend",
        body="again?",
        status=SocialInboxStatus.UNTRIAGED,
    )
    manager._store.update(item)
    result = manager.triage("social_c")
    assert result.status == SocialInboxStatus.SKIPPED
    assert "already replied" in result.decision_reason.lower()
    assert calls["n"] == 1


def test_triage_skips_near_duplicate_draft(tmp_path) -> None:
    prior = "Thanks for the chromadb architecture tip — I will keep that correction."
    draft = "Thanks for the chromadb architecture tip — I will keep that correction in mind."
    manager = SocialManager(data_dir=str(tmp_path / "inbox"), llm=_ReplyDraftLLM(draft))
    manager.set_post_avoidance_provider(
        lambda: {"replied_to_ids": [], "recent_bodies": [prior], "guidance": "skip"}
    )
    item = SocialInboxItem(
        item_id="social_d",
        channel="agora",
        external_message_id="500",
        thread_id="1",
        author="friend",
        body="thoughts?",
        status=SocialInboxStatus.UNTRIAGED,
    )
    manager._store.update(item)
    result = manager.triage("social_d")
    assert result.status == SocialInboxStatus.SKIPPED
    assert "near-duplicate" in result.decision_reason.lower()
    assert result.draft_body == ""
