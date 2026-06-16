"""Context Builder - assembles structured context for LLM and decision logic."""

from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

from aegis_schema.models import Event

MAX_RECENT_EVENTS = 20
MAX_MEMORIES = 10
MAX_CAPABILITIES = 30
MAX_FACTS = 10
MAX_PROCEDURES = 5
MAX_REFLECTIONS = 5
MAX_GOALS = 5
MAX_FAILURE_LESSONS = 5
MAX_SAFETY_LESSONS = 3
MAX_APPROVAL_LESSONS = 3
MAX_USER_PREFERENCES = 5
MAX_MEDIA_SUMMARIES = 4
MAX_TOTAL_CHARS = 8000
MEDIA_CACHE_SIZE = 32


def _truncate(text: str, max_chars: int) -> str:
    return text[:max_chars] + "..." if len(text) > max_chars else text


@dataclass
class MediaInput:
    """Normalized multimodal input passed into ContextBuilder."""

    kind: str = "image"
    image_base64: str = ""
    frames_base64: list[str] = field(default_factory=list)
    caption: str = ""
    source: str = ""
    name: str = ""
    mime_type: str = "image/png"
    timestamp_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Context:
    """Structured context for the Autonomous Loop and other LLM callers."""

    recent_events: list[Event] = field(default_factory=list)
    recent_media_summaries: list[str] = field(default_factory=list)
    recent_episodes: list[str] = field(default_factory=list)
    relevant_facts: list[str] = field(default_factory=list)
    relevant_procedures: list[str] = field(default_factory=list)
    recent_reflections: list[str] = field(default_factory=list)
    failure_lessons: list[str] = field(default_factory=list)
    safety_lessons: list[str] = field(default_factory=list)
    approval_lessons: list[str] = field(default_factory=list)
    user_preferences: list[str] = field(default_factory=list)
    identity: str = "AEGIS - autonomous multi-device AI assistant"
    current_goals: list[str] = field(default_factory=list)
    emotional_state: str = "neutral"
    priorities: str = ""
    desires: str = ""
    available_capability_ids: list[str] = field(default_factory=list)
    recent_user_messages: list[str] = field(default_factory=list)
    dialogue_policy: str = ""
    pending_tasks: list[str] = field(default_factory=list)
    agora_summary: str = ""
    built_at_ms: int = 0
    context_id: str = ""
    total_chars: int = 0
    truncated: bool = False


class ContextBuilder:
    """Assembles Context from events, memory, and optional multimodal inputs."""

    def __init__(
        self,
        event_bus: Any = None,
        episodic_memory: Any = None,
        semantic_memory: Any = None,
        procedural_memory: Any = None,
        reflection_log: Any = None,
        tool_broker: Any = None,
        identity: Any = None,
        desire: Any = None,
        emotion: Any = None,
        goal_manager: Any = None,
        scheduler: Any = None,
        user_model_store: Any = None,
        memory_store: Any = None,
        world_state_store: Any = None,
        multimodal_llm: Any = None,
        capability_retriever: Any = None,
    ) -> None:
        self._event_bus = event_bus
        self._episodic = episodic_memory
        self._semantic = semantic_memory
        self._procedural = procedural_memory
        self._reflection = reflection_log
        self._tool_broker = tool_broker
        self._identity = identity
        self._desire = desire
        self._emotion = emotion
        self._goals = goal_manager
        self._scheduler = scheduler
        self._user_model_store = user_model_store
        self._memory_store = memory_store
        self._world_state_store = world_state_store
        self._capability_retriever = capability_retriever
        self._goals_list: list[str] = []
        self._last_context: Context | None = None
        self._multimodal_llm = multimodal_llm or self._create_default_multimodal_llm()
        self._media_summary_cache: OrderedDict[str, str] = OrderedDict()

    def _create_default_multimodal_llm(self) -> Any:
        try:
            from aegis_ai.llm.factory import create_multimodal_llm_provider

            return create_multimodal_llm_provider()
        except Exception:
            return None

    def set_goals(self, goals: list[str]) -> None:
        """Set goals directly (legacy support). Prefer goal_manager."""
        self._goals_list = goals

    def build(
        self,
        triggering_events: list[Event] | None = None,
        triggering_query: str = "",
        media_inputs: list[MediaInput | dict[str, Any]] | None = None,
    ) -> Context:
        """Build a Context object from all available data sources."""
        ctx = Context(
            built_at_ms=int(time.time() * 1000),
            context_id=f"ctx_{int(time.time() * 1000)}",
        )

        if self._identity:
            if hasattr(self._identity, "to_context_string"):
                ctx.identity = self._identity.to_context_string()
            else:
                ctx.identity = str(self._identity)

        if self._desire and hasattr(self._desire, "to_context_string"):
            ctx.desires = self._desire.to_context_string()

        if self._emotion and hasattr(self._emotion, "to_context_string"):
            ctx.emotional_state = self._emotion.to_context_string()

        if self._goals:
            ctx.current_goals = [g.description for g in self._goals.list_active()[:MAX_GOALS]]
        elif self._goals_list:
            ctx.current_goals = self._goals_list[:MAX_GOALS]

        events: list[Event] = []
        if self._event_bus:
            try:
                events = self._event_bus.list_recent_events(MAX_RECENT_EVENTS)
            except Exception:
                events = []
        if triggering_events:
            events = list(triggering_events) + events
        ctx.recent_events = events[:MAX_RECENT_EVENTS]

        if self._episodic:
            episodes = self._episodic.list_recent(MAX_MEMORIES)
            ctx.recent_episodes = [f"[{e.category}] {e.summary}" for e in episodes]

        if self._semantic and triggering_query:
            facts = self._semantic.search(triggering_query, category=None)
            ctx.relevant_facts = [
                _truncate(f"[{f.category}] {f.content}", 200)
                for f in facts[:MAX_FACTS]
            ]

        if self._procedural and triggering_query:
            procs = self._procedural.find_for_goal(triggering_query)
            ctx.relevant_procedures = [
                f"[conf={p.confidence:.0%}] {p.goal}: {' -> '.join(p.steps[:5])}"
                for p in procs[:MAX_PROCEDURES]
                if p.confidence > 0.3
            ]

        if self._reflection:
            refs = self._reflection.list_recent(MAX_REFLECTIONS)
            ctx.recent_reflections = [f"Reflection: {r.summary}" for r in refs]

        if self._capability_retriever:
            try:
                selection = self._capability_retriever.select_for_request(
                    triggering_query,
                    {},
                    top_k_schema=8,
                    top_k_summary=MAX_CAPABILITIES,
                )
                ctx.available_capability_ids = list(selection.all_candidate_ids[:MAX_CAPABILITIES])
            except Exception:
                ctx.available_capability_ids = []
        elif self._tool_broker:
            try:
                safe_caps = self._tool_broker.list_safe_capabilities()
                ctx.available_capability_ids = [c.id for c in safe_caps[:MAX_CAPABILITIES]]
            except Exception:
                ctx.available_capability_ids = []

        if self._scheduler:
            due_tasks = self._scheduler.get_due_tasks()
            ctx.pending_tasks = [f"{t.name}: {t.description}" for t in due_tasks[:5]]

        if self._user_model_store:
            ctx.dialogue_policy = self._user_model_store.to_context_string()

        if self._memory_store:
            ctx.failure_lessons = [
                r.to_context_string(200)
                for r in self._memory_store.search_memories(
                    memory_type="failure_lesson",
                    min_importance=0.5,
                    limit=MAX_FAILURE_LESSONS,
                )
                if r.visibility != "hidden" and r.sensitivity != "secret"
            ]
            ctx.safety_lessons = [
                r.to_context_string(200)
                for r in self._memory_store.search_memories(
                    memory_type="safety_lesson",
                    limit=MAX_SAFETY_LESSONS,
                )
                if r.visibility != "hidden" and r.sensitivity != "secret"
            ]
            ctx.approval_lessons = [
                r.to_context_string(200)
                for r in self._memory_store.search_memories(
                    memory_type="approval_lesson",
                    limit=MAX_APPROVAL_LESSONS,
                )
                if r.visibility != "hidden" and r.sensitivity != "secret"
            ]
            ctx.user_preferences = [
                r.to_context_string(200)
                for r in self._memory_store.search_memories(
                    memory_type="user_preference",
                    limit=MAX_USER_PREFERENCES,
                )
                if r.visibility != "hidden" and r.sensitivity != "secret"
            ]

        if self._world_state_store:
            agora_ctx = self._world_state_store.state.agora_state.to_context_string()
            if agora_ctx:
                ctx.agora_summary = agora_ctx

        media_candidates = self._collect_media_inputs(triggering_events=events, media_inputs=media_inputs)
        if media_candidates:
            ctx.recent_media_summaries = self._summarize_media_inputs(
                media_candidates=media_candidates,
                triggering_query=triggering_query,
            )

        self._apply_budget(ctx)
        self._last_context = ctx
        return ctx

    def _collect_media_inputs(
        self,
        *,
        triggering_events: list[Event] | None = None,
        media_inputs: list[MediaInput | dict[str, Any]] | None = None,
    ) -> list[MediaInput]:
        collected: list[MediaInput] = []

        for event in triggering_events or []:
            collected.extend(self._media_inputs_from_event(event))

        for item in media_inputs or []:
            normalized = self._normalize_media_input(item)
            if normalized:
                collected.append(normalized)

        unique: list[MediaInput] = []
        seen: set[str] = set()
        for item in collected:
            fingerprint = self._media_fingerprint(item)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            unique.append(item)
        return unique[:MAX_MEDIA_SUMMARIES]

    def _media_inputs_from_event(self, event: Event) -> list[MediaInput]:
        try:
            payload = json.loads(event.payload_json or "{}")
        except Exception:
            return []
        source = event.event_type or event.source_server_id or ""
        return self._media_inputs_from_payload(payload, default_source=source)

    def _media_inputs_from_payload(self, payload: Any, *, default_source: str = "") -> list[MediaInput]:
        if isinstance(payload, list):
            items: list[MediaInput] = []
            for item in payload:
                items.extend(self._media_inputs_from_payload(item, default_source=default_source))
            return items

        if not isinstance(payload, dict):
            return []

        items: list[MediaInput] = []
        media_block = payload.get("media_inputs") or payload.get("media") or payload.get("media_input")
        if isinstance(media_block, list):
            for item in media_block:
                normalized = self._normalize_media_input(item, default_source=default_source)
                if normalized:
                    items.append(normalized)
        elif isinstance(media_block, dict):
            normalized = self._normalize_media_input(media_block, default_source=default_source)
            if normalized:
                items.append(normalized)

        if payload.get("image_base64"):
            items.append(
                MediaInput(
                    kind="image",
                    image_base64=str(payload.get("image_base64", "")),
                    caption=str(payload.get("caption", "")),
                    source=default_source,
                    name=str(payload.get("name", payload.get("title", ""))),
                    mime_type=str(payload.get("mime_type", "image/png")),
                    timestamp_ms=int(payload.get("timestamp_ms", 0) or 0),
                    metadata={k: v for k, v in payload.items() if k not in {"image_base64"}},
                )
            )

        if payload.get("frames_base64") or payload.get("video_frames_base64"):
            items.append(
                MediaInput(
                    kind="video",
                    frames_base64=[
                        str(frame)
                        for frame in (payload.get("frames_base64") or payload.get("video_frames_base64") or [])
                        if frame
                    ],
                    caption=str(payload.get("caption", "")),
                    source=default_source,
                    name=str(payload.get("name", payload.get("title", ""))),
                    mime_type=str(payload.get("mime_type", "video/mp4")),
                    timestamp_ms=int(payload.get("timestamp_ms", 0) or 0),
                    metadata={k: v for k, v in payload.items() if k not in {"frames_base64", "video_frames_base64"}},
                )
            )

        return [item for item in items if item.image_base64 or item.frames_base64]

    def _normalize_media_input(
        self,
        item: MediaInput | dict[str, Any],
        *,
        default_source: str = "",
    ) -> MediaInput | None:
        if isinstance(item, MediaInput):
            return item
        if not isinstance(item, dict):
            return None

        kind = str(item.get("kind") or item.get("type") or item.get("media_type") or "image").lower()
        source = str(item.get("source") or default_source or "")
        name = str(item.get("name") or item.get("title") or "")
        caption = str(item.get("caption") or item.get("description") or "")
        mime_type = str(item.get("mime_type") or ("video/mp4" if kind == "video" else "image/png"))
        timestamp_ms = int(item.get("timestamp_ms", 0) or item.get("created_at", 0) or 0)

        image_base64 = str(
            item.get("image_base64")
            or item.get("image")
            or item.get("data")
            or item.get("base64")
            or ""
        )
        frames_raw = item.get("frames_base64") or item.get("video_frames_base64") or item.get("frames") or []
        if isinstance(frames_raw, str):
            frames_base64 = [frames_raw]
        else:
            frames_base64 = [str(frame) for frame in frames_raw if frame]

        metadata = dict(item.get("metadata", {})) if isinstance(item.get("metadata", {}), dict) else {}
        for key, value in item.items():
            if key in {
                "kind",
                "type",
                "media_type",
                "source",
                "name",
                "title",
                "caption",
                "description",
                "mime_type",
                "timestamp_ms",
                "created_at",
                "image_base64",
                "image",
                "data",
                "base64",
                "frames_base64",
                "video_frames_base64",
                "frames",
                "metadata",
            }:
                continue
            metadata[key] = value

        return MediaInput(
            kind="video" if frames_base64 or kind == "video" else "image",
            image_base64=image_base64,
            frames_base64=frames_base64,
            caption=caption,
            source=source,
            name=name,
            mime_type=mime_type,
            timestamp_ms=timestamp_ms,
            metadata=metadata,
        )

    def _media_fingerprint(self, media: MediaInput) -> str:
        hasher = hashlib.sha256()
        hasher.update(media.kind.encode("utf-8"))
        hasher.update(media.source.encode("utf-8"))
        hasher.update(media.name.encode("utf-8"))
        hasher.update(media.caption.encode("utf-8"))
        hasher.update(media.mime_type.encode("utf-8"))
        if media.image_base64:
            hasher.update(media.image_base64.encode("utf-8"))
        for frame in media.frames_base64:
            hasher.update(frame.encode("utf-8"))
        if media.metadata:
            try:
                hasher.update(json.dumps(media.metadata, sort_keys=True, ensure_ascii=False).encode("utf-8"))
            except Exception:
                hasher.update(str(media.metadata).encode("utf-8"))
        return hasher.hexdigest()[:24]

    def _media_prompt(self, media: MediaInput, triggering_query: str) -> str:
        query_line = f"User goal or query: {triggering_query}\n" if triggering_query else ""
        header = [
            "Summarize this media for the next AEGIS decision.",
            "Focus on visible UI, important text, state changes, and likely next actions.",
            "Return a concise actionable summary in under 120 words.",
        ]
        if media.kind == "video":
            header[0] = "Summarize these ordered video keyframes for the next AEGIS decision."
            header[1] = "Describe the overall scene, motion, state transitions, and any blocking issues."
        if media.caption:
            header.append(f"Caption or hint: {media.caption}")
        if media.name:
            header.append(f"Name: {media.name}")
        if media.source:
            header.append(f"Source: {media.source}")
        return query_line + "\n".join(header)

    def _summarize_media_inputs(
        self,
        *,
        media_candidates: list[MediaInput],
        triggering_query: str,
    ) -> list[str]:
        summaries: list[str] = []
        for media in media_candidates:
            fingerprint = self._media_fingerprint(media)
            cached = self._media_summary_cache.get(fingerprint)
            if cached:
                summaries.append(cached)
                self._media_summary_cache.move_to_end(fingerprint)
                continue

            summary = self._summarize_media(media, triggering_query)
            summary = _truncate(summary.strip(), 320) if summary else ""
            if not summary:
                summary = self._fallback_media_summary(media)

            rendered = self._render_media_summary(media, summary)
            summaries.append(rendered)
            self._cache_media_summary(fingerprint, rendered)

        return summaries

    def _cache_media_summary(self, fingerprint: str, summary: str) -> None:
        self._media_summary_cache[fingerprint] = summary
        self._media_summary_cache.move_to_end(fingerprint)
        while len(self._media_summary_cache) > MEDIA_CACHE_SIZE:
            self._media_summary_cache.popitem(last=False)

    def _fallback_media_summary(self, media: MediaInput) -> str:
        if media.kind == "video":
            frame_count = len(media.frames_base64) or (1 if media.image_base64 else 0)
            base = f"Video input with {frame_count} frame(s)"
        else:
            base = "Image input"
        if media.caption:
            base += f" ({media.caption})"
        return base

    def _render_media_summary(self, media: MediaInput, summary: str) -> str:
        prefix = "video" if media.kind == "video" else "image"
        label_parts = [prefix]
        if media.name:
            label_parts.append(media.name)
        if media.source:
            label_parts.append(media.source)
        label = " / ".join(label_parts)
        if media.kind == "video":
            frame_count = len(media.frames_base64) or (1 if media.image_base64 else 0)
            return f"[{label}; frames={frame_count}] {summary}"
        return f"[{label}] {summary}"

    def _summarize_media(self, media: MediaInput, triggering_query: str) -> str:
        llm = self._multimodal_llm
        if not llm:
            return ""

        prompt = self._media_prompt(media, triggering_query)
        system_prompt = "You turn images and video frames into concise actionable observations."
        try:
            if media.kind == "video":
                frames = list(media.frames_base64)
                if not frames and media.image_base64:
                    frames = [media.image_base64]
                if hasattr(llm, "generate_with_media"):
                    result = llm.generate_with_media(
                        prompt=prompt,
                        image_base64s=frames,
                        system_prompt=system_prompt,
                        max_tokens=240,
                        temperature=0.2,
                        detail="low",
                        media_kind="video",
                        context_meta={
                            "media_kind": "video",
                            "media_frames": len(frames),
                            "media_source": media.source,
                        },
                    )
                    if result.success and result.content:
                        return result.content.strip()
                if frames and hasattr(llm, "generate_with_image"):
                    result = llm.generate_with_image(
                        prompt=prompt + "\nThe provided input is a video keyframe sequence; summarize from the first frame if needed.",
                        image_base64=frames[0],
                        system_prompt=system_prompt,
                        max_tokens=240,
                        temperature=0.2,
                        detail="low",
                        context_meta={
                            "media_kind": "video",
                            "media_frames": len(frames),
                            "media_source": media.source,
                            "vision_fallback": True,
                        },
                    )
                    if result.success and result.content:
                        return result.content.strip()
                return ""

            if hasattr(llm, "generate_with_image") and media.image_base64:
                result = llm.generate_with_image(
                    prompt=prompt,
                    image_base64=media.image_base64,
                    system_prompt=system_prompt,
                    max_tokens=240,
                    temperature=0.2,
                    detail="low",
                    context_meta={
                        "media_kind": "image",
                        "media_source": media.source,
                    },
                )
                if result.success and result.content:
                    return result.content.strip()
        except Exception:
            return ""
        return ""

    def _apply_budget(self, ctx: Context) -> None:
        """Truncate context if it exceeds the character budget."""
        total = self._recalc_chars(ctx)
        ctx.total_chars = total
        if total <= MAX_TOTAL_CHARS:
            return

        ctx.truncated = True
        while total > MAX_TOTAL_CHARS and len(ctx.recent_events) > 3:
            ctx.recent_events = ctx.recent_events[1:]
            total = self._recalc_chars(ctx)
        while total > MAX_TOTAL_CHARS and len(ctx.recent_media_summaries) > 1:
            ctx.recent_media_summaries.pop()
            total = self._recalc_chars(ctx)
        while total > MAX_TOTAL_CHARS and len(ctx.relevant_facts) > 1:
            ctx.relevant_facts.pop()
            total = self._recalc_chars(ctx)
        while total > MAX_TOTAL_CHARS and len(ctx.failure_lessons) > 1:
            ctx.failure_lessons.pop()
            total = self._recalc_chars(ctx)
        while total > MAX_TOTAL_CHARS and len(ctx.approval_lessons) > 1:
            ctx.approval_lessons.pop()
            total = self._recalc_chars(ctx)

        ctx.total_chars = total

    def _recalc_chars(self, ctx: Context) -> int:
        return (
            len(ctx.identity)
            + len(ctx.desires)
            + len(ctx.emotional_state)
            + len(ctx.priorities)
            + len(" ".join(ctx.current_goals))
            + sum(len(str(e)) for e in ctx.recent_events)
            + sum(len(s) for s in ctx.recent_media_summaries)
            + sum(len(s) for s in ctx.recent_episodes)
            + sum(len(s) for s in ctx.relevant_facts)
            + sum(len(s) for s in ctx.relevant_procedures)
            + sum(len(s) for s in ctx.recent_reflections)
            + sum(len(s) for s in ctx.failure_lessons)
            + sum(len(s) for s in ctx.safety_lessons)
            + sum(len(s) for s in ctx.approval_lessons)
            + sum(len(s) for s in ctx.user_preferences)
            + sum(len(s) for s in ctx.available_capability_ids)
            + sum(len(s) for s in ctx.recent_user_messages)
            + sum(len(s) for s in ctx.pending_tasks)
            + len(ctx.dialogue_policy)
            + len(ctx.agora_summary)
        )

    @property
    def last_context(self) -> Context | None:
        return self._last_context
