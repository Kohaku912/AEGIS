"""AGORA types — data models for AGORA chat integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgoraAccount:
    id: int = 0
    name: str = ""
    bio: str = ""
    created_at: str = ""


@dataclass
class AgoraAuthor:
    id: int = 0
    name: str = ""


@dataclass
class AgoraPost:
    id: int = 0
    thread_id: int = 0
    author: AgoraAuthor = field(default_factory=AgoraAuthor)
    body: str = ""
    reply_to: int | None = None
    mentions: list[AgoraAuthor] = field(default_factory=list)
    attachments: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = ""

    @staticmethod
    def from_dict(d: dict[str, Any]) -> AgoraPost:
        author_data = d.get("author", {})
        author = AgoraAuthor(
            id=author_data.get("id", 0),
            name=author_data.get("name", ""),
        )
        mentions = [
            AgoraAuthor(id=m.get("id", 0), name=m.get("name", ""))
            for m in d.get("mentions", [])
        ]
        return AgoraPost(
            id=d.get("id", 0),
            thread_id=d.get("thread_id", 0),
            author=author,
            body=d.get("body", ""),
            reply_to=d.get("reply_to"),
            mentions=mentions,
            attachments=d.get("attachments", []),
            created_at=d.get("created_at", ""),
        )


@dataclass
class AgoraCursor:
    last_read_post_id: int = 0


@dataclass
class AgoraPostCreate:
    body: str = ""
    reply_to: int | None = None
    mentions: list[int] = field(default_factory=list)


@dataclass
class AgoraFetchResult:
    posts: list[AgoraPost] = field(default_factory=list)
    max_post_id: int = 0
    has_new_posts: bool = False
    fetched_at: int = 0

    def summarize(self, max_posts: int = 5) -> str:
        if not self.posts:
            return "AGORA: No new posts."
        lines = [f"AGORA: {len(self.posts)} new post(s)."]
        for p in self.posts[:max_posts]:
            body_preview = p.body[:80].replace("\n", " ")
            reply_info = f" (reply to #{p.reply_to})" if p.reply_to else ""
            lines.append(f"  [{p.id}] {p.author.name}: {body_preview}{reply_info}")
        if len(self.posts) > max_posts:
            lines.append(f"  ... and {len(self.posts) - max_posts} more.")
        return "\n".join(lines)


@dataclass
class AgoraTaskDetection:
    is_task_request: bool = False
    task_title: str = ""
    task_description: str = ""
    urgency: str = "normal"
    requires_reply: bool = False
    reply_to: int = 0
    confidence: float = 0.0
    reason: str = ""


@dataclass
class AgoraReplyDraft:
    reply_body: str = ""
    reply_to: int = 0
    reason: str = ""
    risk_level: str = "low"
    requires_approval: bool = True
