"""Memory ingestion helpers for AGORA and generic memory saves."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from aegis_ai.integrations.agora.agora_types import AgoraPost
from aegis_ai.memory.advanced import AdvancedMemory
from aegis_ai.memory.person_memory import PersonMemory, PersonRecord
from aegis_ai.social.intelligence import SocialIntelligenceSystem

logger = logging.getLogger("aegis_ai.memory.ingest")

_PERSON_TYPES = {"person", "people", "persona", "entity", "contact", "profile"}


@dataclass
class MemorySaveResult:
    ok: bool
    message: str
    saved_to: list[str] = field(default_factory=list)
    kind: str = ""
    entity: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "message": self.message,
            "saved_to": list(self.saved_to),
            "kind": self.kind,
            "entity": self.entity,
        }


@dataclass
class AgoraMemorySyncResult:
    ok: bool
    message: str
    result: str
    summary: str = ""
    posts: list[dict[str, Any]] = field(default_factory=list)
    mentions: list[dict[str, Any]] = field(default_factory=list)
    saved_people: list[str] = field(default_factory=list)
    social_observations: int = 0
    social_episodes: int = 0
    advanced_conversations: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "message": self.message,
            "result": self.result,
            "summary": self.summary or self.result,
            "posts": list(self.posts),
            "mentions": list(self.mentions),
            "saved_people": list(self.saved_people),
            "social_observations": self.social_observations,
            "social_episodes": self.social_episodes,
            "advanced_conversations": self.advanced_conversations,
        }


def _truncate(text: str, limit: int = 120) -> str:
    compact = " ".join(text.replace("\r\n", "\n").replace("\r", "\n").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def _post_to_dict(post: AgoraPost) -> dict[str, Any]:
    return {
        "id": post.id,
        "thread_id": post.thread_id,
        "author": {"id": post.author.id, "name": post.author.name},
        "body": post.body,
        "reply_to": post.reply_to,
        "mentions": [{"id": m.id, "name": m.name} for m in post.mentions],
        "attachments": list(post.attachments),
        "created_at": post.created_at,
    }


def _build_post_summary(posts: list[AgoraPost], *, body_limit: int = 80, max_posts: int = 5) -> str:
    if not posts:
        return "AGORA: No new posts."
    lines = [f"AGORA: {len(posts)} new post(s)."]
    for post in posts[:max_posts]:
        reply_info = f" (reply to #{post.reply_to})" if post.reply_to else ""
        mention_info = ""
        if post.mentions:
            mention_info = " mentions=" + ", ".join(m.name for m in post.mentions[:3] if m.name)
        lines.append(
            f"  [{post.id}] {post.author.name}: {_truncate(post.body, body_limit)}{reply_info}{mention_info}"
        )
    if len(posts) > max_posts:
        lines.append(f"  ... and {len(posts) - max_posts} more.")
    return "\n".join(lines)


def build_agora_posts_text(
    posts: list[Any],
    *,
    body_limit: int = 2000,
    max_posts: int = 50,
    header: str | None = None,
) -> str:
    """Build LLM-facing AGORA text that preserves post bodies.

    Capability payloads often set ``result`` to a count-only status string while
    the real bodies live under ``posts``. Callers that feed tool output back to
    an LLM should prefer this helper (or ``posts`` itself) over the opaque
    status string alone.
    """
    normalized = _normalise_posts(posts)
    if not normalized:
        return header or "AGORA: No new posts."
    lines = [header or f"AGORA: {len(normalized)} post(s)."]
    for post in normalized[:max_posts]:
        reply_info = f" (reply to #{post.reply_to})" if post.reply_to else ""
        body = post.body if len(post.body) <= body_limit else _truncate(post.body, body_limit)
        lines.append(f"[{post.id}] {post.author.name}: {body}{reply_info}")
    if len(normalized) > max_posts:
        lines.append(f"... and {len(normalized) - max_posts} more.")
    return "\n".join(lines)


def _normalise_posts(raw_posts: list[Any]) -> list[AgoraPost]:
    posts: list[AgoraPost] = []
    for item in raw_posts:
        if isinstance(item, AgoraPost):
            posts.append(item)
        elif isinstance(item, dict):
            posts.append(AgoraPost.from_dict(item))
    return posts


def _person_record_from_agora(
    name: str,
    *,
    relationship: str,
    note: str,
    topics: list[str],
    tags: list[str],
) -> PersonRecord:
    return PersonRecord(
        name=name,
        relationship=relationship,
        notes=note,
        topics=topics,
        tags=tags,
        last_context=note[:200],
    )


def _save_people_from_posts(
    person_memory: PersonMemory,
    posts: list[AgoraPost],
    *,
    self_author_ids: set[int] | None = None,
    self_author_names: set[str] | None = None,
) -> list[str]:
    saved_people: list[str] = []
    reported: set[str] = set()
    self_author_ids = self_author_ids or set()
    self_author_names = {name.lower() for name in (self_author_names or set()) if name}

    for post in posts:
        author = post.author
        if author.id in self_author_ids or author.name.lower() in self_author_names:
            continue
        if author.name:
            record = _person_record_from_agora(
                author.name,
                relationship="AGORA participant",
                note=f"Recent AGORA post #{post.id}: {_truncate(post.body, 180)}",
                topics=["agora"],
                tags=["agora", "author"],
            )
            saved = person_memory.upsert(record)
            person_memory.record_interaction(saved.person_id, context=f"AGORA post #{post.id}")
            if saved.name not in reported:
                saved_people.append(saved.name)
                reported.add(saved.name)

        for mention in post.mentions:
            if not mention.name:
                continue
            if mention.id in self_author_ids or mention.name.lower() in self_author_names:
                continue
            record = _person_record_from_agora(
                mention.name,
                relationship="AGORA participant",
                note=f"Mentioned in AGORA post #{post.id} by {author.name}: {_truncate(post.body, 160)}",
                topics=["agora", "mention"],
                tags=["agora", "mention"],
            )
            saved = person_memory.upsert(record)
            person_memory.record_interaction(saved.person_id, context=f"Mentioned in AGORA post #{post.id}")
            if saved.name not in reported:
                saved_people.append(saved.name)
                reported.add(saved.name)

    return saved_people


def sync_agora_posts_to_memory(
    *,
    posts: list[Any],
    data_dir: str,
    llm_provider: Any | None = None,
    self_author_ids: set[int] | None = None,
    self_author_names: set[str] | None = None,
) -> AgoraMemorySyncResult:
    """Sync AGORA posts into social/person/advanced memory."""
    normalized_posts = _normalise_posts(posts)
    data_root = Path(data_dir).resolve()
    memory_dir = data_root / "memory"

    person_memory = PersonMemory(path=str(memory_dir / "persons.jsonl"))
    social = SocialIntelligenceSystem(
        llm=llm_provider,
        person_memory=person_memory,
        data_dir=str(data_root / "social"),
    )

    observable_posts = [
        post
        for post in normalized_posts
        if post.author.id not in (self_author_ids or set())
        and post.author.name.lower() not in {name.lower() for name in (self_author_names or set()) if name}
    ]

    fake_agora = SimpleNamespace(
        read_posts=lambda limit=20: SimpleNamespace(posts=observable_posts[:limit]),
    )
    social._agora = fake_agora  # type: ignore[attr-defined]

    social_observations = 0
    if observable_posts:
        observed = social.observe_recent_posts(limit=len(observable_posts))
        social_observations = len(observed)
        for post in observable_posts:
            participants = [post.author.name] + [m.name for m in post.mentions if m.name]
            purpose = "reply" if post.reply_to else "post"
            social.record_conversation(
                participants=[p for p in participants if p],
                purpose=purpose,
                context=_truncate(post.body, 200),
                key_points=[_truncate(post.body, 80)],
                related_posts=[post.id],
                tags=["agora", purpose],
            )

    saved_people = _save_people_from_posts(
        person_memory,
        observable_posts,
        self_author_ids=self_author_ids,
        self_author_names=self_author_names,
    )

    advanced_conversations = 0
    summary = _build_post_summary(normalized_posts)
    if summary and normalized_posts:
        advanced = AdvancedMemory(data_dir=str(memory_dir), llm_provider=llm_provider)
        advanced.add_conversation("AGORA read_posts", summary)
        advanced_conversations = 1

    mentions = []
    seen_mentions: set[str] = set()
    for post in normalized_posts:
        for mention in post.mentions:
            if not mention.name or mention.name in seen_mentions:
                continue
            seen_mentions.add(mention.name)
            mentions.append({"id": mention.id, "name": mention.name})

    return AgoraMemorySyncResult(
        ok=True,
        message=summary,
        result=summary,
        summary=summary,
        posts=[_post_to_dict(post) for post in normalized_posts],
        mentions=mentions,
        saved_people=saved_people,
        social_observations=social_observations,
        social_episodes=len(normalized_posts),
        advanced_conversations=advanced_conversations,
    )


def save_memory_payload(
    payload: dict[str, Any],
    *,
    data_dir: str,
    llm_provider: Any | None = None,
) -> MemorySaveResult:
    """Route memory.save payloads to the appropriate backing store."""
    content = str(payload.get("content", payload.get("text", "")) or "").strip()
    entity = str(payload.get("entity", payload.get("name", "")) or "").strip()
    kind = str(payload.get("type", "conversation")).strip().lower() or "conversation"

    if not content:
        return MemorySaveResult(ok=False, message="No content provided", kind=kind, entity=entity)

    data_root = Path(data_dir).resolve()
    memory_dir = data_root / "memory"

    if kind in _PERSON_TYPES:
        if not entity:
            entity = content[:80].strip()
        if not entity:
            return MemorySaveResult(ok=False, message="Person name is required for person memory", kind=kind, entity="")

        person_memory = PersonMemory(path=str(memory_dir / "persons.jsonl"))
        record = _person_record_from_agora(
            entity,
            relationship="known person",
            note=content,
            topics=["memory"],
            tags=["memory", "person"],
        )
        saved = person_memory.upsert(record)
        person_memory.record_interaction(saved.person_id, context=content[:200])
        return MemorySaveResult(
            ok=True,
            message=f"Saved person: {saved.name}",
            saved_to=["person_memory"],
            kind=kind,
            entity=saved.name,
        )

    advanced = AdvancedMemory(data_dir=str(memory_dir), llm_provider=llm_provider)
    advanced.add_conversation(content, entity or kind.title())
    return MemorySaveResult(
        ok=True,
        message=f"Saved: {content[:50]}",
        saved_to=["advanced_memory"],
        kind=kind,
        entity=entity,
    )
