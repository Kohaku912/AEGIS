"""LLM-driven social triage, approval binding, and reply verification."""

from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any

from aegis_ai.llm.json_utils import extract_json_object
from aegis_ai.social.adapters import (
    AgoraReplyAdapter,
    SocialReplyAdapter,
    UnavailableReplyAdapter,
)
from aegis_ai.social.inbox import SocialInboxStore
from aegis_ai.social.models import (
    TERMINAL_SOCIAL_STATUSES,
    SocialInboxItem,
    SocialInboxStatus,
)

logger = logging.getLogger("aegis_ai.social.manager")
_RETRY_BATCH_SIZE = 5
_MAX_RETRIES = 5
_RETRY_BASE_MS = 5 * 60 * 1000
_RETRY_MAX_MS = 6 * 60 * 60 * 1000


def _parse_timestamp(value: Any) -> int:
    """Parse a timestamp from int (ms), float, or ISO 8601 string to int (ms)."""
    if value is None:
        return int(time.time() * 1000)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            pass
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return int(dt.timestamp() * 1000)
        except (ValueError, OSError):
            pass
    return int(time.time() * 1000)


def _parse_author(value: Any) -> str:
    """Parse author from string or dict format, returning the display name."""
    if isinstance(value, dict):
        return str(value.get("name") or value.get("username") or value.get("id") or "")
    return str(value or "")


class SocialManager:
    """Owns social inbox state; adapters only retrieve or deliver messages."""

    def __init__(
        self,
        *,
        data_dir: str,
        llm: Any = None,
        tool_broker: Any = None,
        event_manager: Any = None,
        audit_manager: Any = None,
        self_author_ids: set[int] | None = None,
        self_author_names: set[str] | None = None,
    ) -> None:
        self._store = SocialInboxStore(data_dir)
        self._llm = llm
        self._broker = tool_broker
        self._events = event_manager
        self._audit = audit_manager
        self._self_author_ids = self_author_ids or set()
        self._self_author_names = self_author_names or set()
        self._cursor_updaters: dict[str, Callable[[int], Any]] = {}
        self._relationship_provider: Callable[[SocialInboxItem], dict[str, Any]] | None = None
        self._post_avoidance_provider: Callable[[], dict[str, Any]] | None = None
        self._agent_state: Any = None
        self._processing_lock = threading.RLock()
        self._processing_ids: set[str] = set()
        self._adapters: dict[str, SocialReplyAdapter] = {
            "agora": AgoraReplyAdapter(),
            "discord": UnavailableReplyAdapter("discord", "Discord adapter is not configured"),
            "line": UnavailableReplyAdapter("line", "LINE adapter is not configured"),
            "email": UnavailableReplyAdapter("email", "Email inbox adapter is not configured"),
            "webhook": UnavailableReplyAdapter("webhook", "Webhook inbox adapter is not configured"),
        }

    def set_cursor_updater(self, channel: str, updater: Callable[[int], Any]) -> None:
        self._cursor_updaters[channel] = updater

    def register_adapter(self, adapter: SocialReplyAdapter) -> None:
        """Register a channel adapter without changing social decision logic."""
        self._adapters[adapter.channel] = adapter

    def set_relationship_provider(
        self,
        provider: Callable[[SocialInboxItem], dict[str, Any]],
    ) -> None:
        self._relationship_provider = provider

    def set_agent_state(self, agent_state: Any) -> None:
        """Use the same state snapshot as conversation and autonomy."""
        self._agent_state = agent_state

    def set_post_avoidance_provider(self, provider: Callable[[], dict[str, Any]] | None) -> None:
        """Optional AGORA (or other) avoidance facts for draft generation."""
        self._post_avoidance_provider = provider

    def post_avoidance_context(self) -> dict[str, Any]:
        if self._post_avoidance_provider is None:
            return {}
        try:
            data = self._post_avoidance_provider()
        except Exception:
            logger.debug("post avoidance provider failed", exc_info=True)
            return {}
        return data if isinstance(data, dict) else {}

    def set_self_authors(
        self,
        author_ids: set[int] | None = None,
        author_names: set[str] | None = None,
    ) -> None:
        if author_ids is not None:
            self._self_author_ids = author_ids
        if author_names is not None:
            self._self_author_names = author_names

    def retry_pending_items(self, limit: int = _RETRY_BATCH_SIZE) -> list[SocialInboxItem]:
        """Retry a bounded batch of due items."""
        now = int(time.time() * 1000)
        pending = [
            item for item in self._store.list(limit=10000)
            if item.status == SocialInboxStatus.RETRY_PENDING
            and int(item.metadata.get("retry_count", 0) or 0) < _MAX_RETRIES
            and int(item.metadata.get("next_retry_at", 0) or 0) <= now
        ]
        pending.sort(
            key=lambda item: (
                int(item.metadata.get("next_retry_at", 0) or 0),
                item.received_at,
                item.item_id,
            )
        )
        pending = pending[: max(0, limit)]
        if not pending:
            return []
        return self.process_new_items(pending)

    def enqueue_processing(self, items: list[SocialInboxItem]) -> list[SocialInboxItem]:
        """Process inbox items asynchronously so retrieval RPCs remain bounded."""
        with self._processing_lock:
            selected = [item for item in items if item.item_id not in self._processing_ids]
            self._processing_ids.update(item.item_id for item in selected)
        if not selected:
            return items

        worker = threading.Thread(
            target=self._process_queued_items,
            args=(selected,),
            daemon=True,
            name="social-inbox-triage",
        )
        worker.start()
        return items

    def resume_pending_processing(self) -> list[SocialInboxItem]:
        """Resume unfinished inbox obligations after a runtime restart."""
        untriaged = [
            item
            for item in self._store.list(limit=10000)
            if item.status == SocialInboxStatus.UNTRIAGED
        ][: _RETRY_BATCH_SIZE]
        due_retries = [
            item
            for item in self._store.list(limit=10000)
            if item.status == SocialInboxStatus.RETRY_PENDING
            and int(item.metadata.get("retry_count", 0) or 0) < _MAX_RETRIES
            and int(item.metadata.get("next_retry_at", 0) or 0) <= int(time.time() * 1000)
        ]
        pending = (untriaged + due_retries)[:_RETRY_BATCH_SIZE]
        self.enqueue_processing(pending)
        return pending

    def _process_queued_items(self, items: list[SocialInboxItem]) -> None:
        try:
            self.process_new_items(items)
        except Exception:
            logger.exception("Queued social inbox processing failed")
        finally:
            with self._processing_lock:
                self._processing_ids.difference_update(item.item_id for item in items)

    def ingest(self, channel: str, messages: list[Any]) -> list[SocialInboxItem]:
        created: list[SocialInboxItem] = []
        now = int(time.time() * 1000)
        for message in messages:
            raw = asdict(message) if is_dataclass(message) else dict(message)
            external_id = str(raw.get("id") or raw.get("message_id") or raw.get("external_message_id") or "")
            if not external_id:
                continue
            author_raw = raw.get("author") or raw.get("author_name") or raw.get("username")
            author_name = _parse_author(author_raw)
            author_id = 0
            if isinstance(author_raw, dict):
                try:
                    author_id = int(author_raw.get("id") or 0)
                except (TypeError, ValueError):
                    pass
            if self._is_own_post(author_name, author_id):
                continue
            thread_id = str(raw.get("thread_id") or "")
            recent_thread = [
                existing
                for existing in self._store.list(limit=1000)
                if existing.channel == channel and existing.thread_id == thread_id
            ][:5]
            item = SocialInboxItem(
                item_id=f"social_{uuid.uuid4().hex[:12]}",
                channel=channel,
                external_message_id=external_id,
                thread_id=thread_id,
                author=author_name,
                body=str(raw.get("body") or raw.get("content") or raw.get("text") or ""),
                decision="observe_more",
                decision_reason="Queued for LLM social triage.",
                received_at=_parse_timestamp(raw.get("created_at") or raw.get("timestamp")),
                updated_at=now,
                conversation_context={
                    "recent_items": [
                        {
                            "external_message_id": existing.external_message_id,
                            "author": existing.author,
                            "body": existing.body,
                            "status": existing.status.value,
                        }
                        for existing in reversed(recent_thread)
                    ]
                },
                metadata={"source": channel, "own_post": False},
            )
            stored = self._store.upsert(item)
            if stored.item_id == item.item_id:
                created.append(stored)
                self._publish("social.inbox.received", stored)
        return created

    def _is_own_post(self, author_name: str, author_id: int) -> bool:
        if author_id and author_id in self._self_author_ids:
            return True
        if author_name and author_name in self._self_author_names:
            return True
        return False

    def _has_active_or_completed_reply(self, item: SocialInboxItem) -> bool:
        """True when this external message already has an in-flight or finished reply."""
        external_id = str(item.external_message_id or "")
        if not external_id:
            return False
        blocking = {
            SocialInboxStatus.AWAITING_APPROVAL,
            SocialInboxStatus.DRAFTED,
            SocialInboxStatus.REPLIED,
        }
        for existing in self._store.list(limit=10000):
            if existing.item_id == item.item_id:
                continue
            if existing.channel != item.channel:
                continue
            if str(existing.external_message_id or "") != external_id:
                continue
            if existing.status in blocking:
                return True
        return False

    def triage(self, item_id: str, *, relationship: dict[str, Any] | None = None) -> SocialInboxItem:
        item = self._require(item_id)
        item.relationship = relationship or item.relationship
        if self._has_active_or_completed_reply(item):
            item.decision = "skip"
            item.status = SocialInboxStatus.SKIPPED
            item.draft_body = ""
            item.decision_reason = (
                "Reply-once: an approval or completed reply already exists for this message."
            )
            saved = self._save(item)
            self._publish("social.inbox.triaged", saved)
            self._advance_processed_cursor(item.channel)
            return saved

        avoidance = self.post_avoidance_context()
        replied_ids = {
            int(x)
            for x in (avoidance.get("replied_to_ids") or [])
            if str(x).lstrip("-").isdigit() or isinstance(x, int)
        }
        try:
            external_id = int(item.external_message_id)
        except (TypeError, ValueError):
            external_id = 0
        if external_id and external_id in replied_ids:
            item.decision = "skip"
            item.status = SocialInboxStatus.SKIPPED
            item.draft_body = ""
            item.decision_reason = (
                f"Already replied to post #{external_id}; skipped before drafting."
            )
            saved = self._save(item)
            self._publish("social.inbox.triaged", saved)
            self._advance_processed_cursor(item.channel)
            return saved

        if self._llm is None:
            item.status = SocialInboxStatus.RETRY_PENDING
            item.decision = "observe_more"
            item.decision_reason = "LLM unavailable; will retry on next cycle."
            return self._save(item)

        prompt = f"""Decide how AEGIS should respond to this social inbox item.
Return JSON only. Do not infer from keyword rules; reason from the full message and context.

Message:
{json.dumps(item.to_dict(), ensure_ascii=False)}

Relationship context:
{json.dumps(relationship or item.relationship, ensure_ascii=False)}

Shared AgentState:
{json.dumps(self._agent_state.snapshot(item.body).to_dict() if self._agent_state else {}, ensure_ascii=False)}

Post avoidance (do not re-answer or paraphrase these):
{json.dumps(avoidance, ensure_ascii=False)}

Rules:
- Reply when a social reply would help the user or continue a real conversation.
- Skip when AEGIS already answered this message id, when a reply would be noise/spam,
  or when the only draft you can write would restate a recent AEGIS body.
- draft_body must be a genuine social reply with new substance. Never draft internal
  system status, approval meta, test probes, duplicate answers, or near-paraphrases
  of recent AEGIS posts listed above.

Return:
{{
  "decision": "reply|acknowledge|skip|observe_more",
  "reason": "specific reason",
  "directed_to_aegis": true,
  "mentions_user": false,
  "question_detected": true,
  "reply_expected": true,
  "relevance": 0.0,
  "urgency": 0.0,
  "sentiment": "neutral",
  "draft_body": "reply text when decision is reply"
}}"""
        data = self._generate_json(prompt)
        decision = str(data.get("decision") or "observe_more")
        item.directed_to_aegis = bool(data.get("directed_to_aegis", False))
        item.mentions_user = bool(data.get("mentions_user", False))
        item.question_detected = bool(data.get("question_detected", False))
        item.reply_expected = bool(data.get("reply_expected", False))
        item.relevance = float(data.get("relevance", 0.0) or 0.0)
        item.urgency = float(data.get("urgency", 0.0) or 0.0)
        item.sentiment = str(data.get("sentiment") or "")
        item.decision = decision
        item.decision_reason = str(data.get("reason") or "LLM supplied no reason")
        if decision == "reply":
            draft = str(data.get("draft_body") or "").strip()
            if not draft:
                item.decision = "skip"
                item.status = SocialInboxStatus.SKIPPED
                item.draft_body = ""
                item.decision_reason = "Reply chosen without draft body; skipped."
            elif self._draft_matches_recent_bodies(draft, avoidance):
                item.decision = "skip"
                item.status = SocialInboxStatus.SKIPPED
                item.draft_body = ""
                item.decision_reason = (
                    "Draft was a near-duplicate of a recent AEGIS post; skipped before posting."
                )
            else:
                item.status = SocialInboxStatus.NEEDS_REPLY
                item.draft_body = draft
        elif decision == "acknowledge":
            item.status = SocialInboxStatus.ACKNOWLEDGED
        elif decision == "skip":
            item.status = SocialInboxStatus.SKIPPED
        else:
            # "observe_more" is a deliberate no-action decision for this
            # message, not a failed triage.  Leaving it UNTRIAGED makes startup
            # replay select the same item forever and prevents cursor progress.
            item.status = SocialInboxStatus.SKIPPED
        self._save(item)
        self._publish("social.inbox.triaged", item)
        self._advance_processed_cursor(item.channel)
        return item

    @staticmethod
    def _draft_matches_recent_bodies(draft: str, avoidance: dict[str, Any]) -> bool:
        from aegis_ai.integrations.agora.agora_service import bodies_are_near_duplicates

        recent = [str(b) for b in (avoidance.get("recent_bodies") or []) if str(b).strip()]
        return any(bodies_are_near_duplicates(draft, prior) for prior in recent)

    def process_new_items(
        self,
        items: list[SocialInboxItem],
        *,
        relationship_provider: Callable[[SocialInboxItem], dict[str, Any]] | None = None,
    ) -> list[SocialInboxItem]:
        """Triage newly retrieved items and create approval-bound drafts."""
        processed: list[SocialInboxItem] = []
        for item in items:
            try:
                provider = relationship_provider or self._relationship_provider
                relationship = provider(item) if provider else item.relationship
                current = self.triage(item.item_id, relationship=relationship)
                if current.status == SocialInboxStatus.RETRY_PENDING:
                    current = self._schedule_retry(current, RuntimeError("LLM unavailable"))
                elif current.status == SocialInboxStatus.NEEDS_REPLY:
                    current = self.propose_reply(current.item_id)
                processed.append(current)
            except Exception as exc:
                current = self._store.get(item.item_id)
                if current is None:
                    continue
                processed.append(self._schedule_retry(current, exc))
        return processed

    def _schedule_retry(self, item: SocialInboxItem, error: Exception) -> SocialInboxItem:
        retry_count = int(item.metadata.get("retry_count", 0) or 0) + 1
        item.metadata["retry_count"] = retry_count
        item.metadata["last_error"] = str(error)[:1000]
        item.decision = item.decision or "observe_more"
        if retry_count >= _MAX_RETRIES:
            item.status = SocialInboxStatus.FAILED
            item.metadata["next_retry_at"] = 0
            item.decision_reason = f"Social processing stopped after {retry_count} attempts: {error}"
        else:
            delay_ms = min(_RETRY_MAX_MS, _RETRY_BASE_MS * (2 ** (retry_count - 1)))
            item.status = SocialInboxStatus.RETRY_PENDING
            item.metadata["next_retry_at"] = int(time.time() * 1000) + delay_ms
            item.decision_reason = (
                f"Social processing failed; will retry {retry_count}/{_MAX_RETRIES}: {error}"
            )
        saved = self._save(item)
        if saved.status == SocialInboxStatus.FAILED:
            self._advance_processed_cursor(saved.channel)
        return saved

    def propose_reply(self, item_id: str) -> SocialInboxItem:
        item = self._require(item_id)
        if item.status != SocialInboxStatus.NEEDS_REPLY or not item.draft_body:
            raise ValueError("A triaged reply draft is required before proposal")
        if self._has_active_or_completed_reply(item):
            item.status = SocialInboxStatus.SKIPPED
            item.decision_reason = (
                "Reply-once: an approval or completed reply already exists for this message."
            )
            saved = self._save(item)
            self._advance_processed_cursor(item.channel)
            return saved
        adapter = self._adapters.get(item.channel)
        if adapter is None or not adapter.available:
            item.status = SocialInboxStatus.FAILED
            reason = getattr(adapter, "reason", "Channel adapter is not registered")
            item.decision_reason = f"Channel adapter is unavailable: {item.channel}. {reason}"
            saved = self._save(item)
            self._advance_processed_cursor(item.channel)
            return saved
        if self._broker is None:
            item.status = SocialInboxStatus.FAILED
            item.decision_reason = "ToolBroker unavailable"
            saved = self._save(item)
            self._advance_processed_cursor(item.channel)
            return saved

        from tool_broker import ExecutionSource, InvokeStatus, ToolExecutionRequest

        item.draft_id = item.draft_id or f"draft_{uuid.uuid4().hex[:12]}"
        item.status = SocialInboxStatus.DRAFTED
        self._save(item)
        request = ToolExecutionRequest(
            capability_id=adapter.capability_id(item),
            arguments=adapter.build_arguments(item),
            source=ExecutionSource.EVENT_DRIVEN,
            reason=f"Reply to social inbox item {item.item_id}: {item.decision_reason}",
            source_desire="social",
            conversation_id=item.thread_id,
            metadata={
                "social_inbox_item_id": item.item_id,
                "draft_id": item.draft_id,
                "continuation_stage": "propose",
            },
        )
        result = self._broker.execute(request)
        if result.status == InvokeStatus.APPROVAL_NEEDED and result.approval_id:
            item.approval_id = result.approval_id
            item.status = SocialInboxStatus.AWAITING_APPROVAL
        elif result.success:
            self._apply_reply_result(item, result.output)
        else:
            item.status = SocialInboxStatus.FAILED
            item.decision_reason = result.error or "Reply proposal failed"
        self._save(item)
        if item.status in TERMINAL_SOCIAL_STATUSES:
            self._advance_processed_cursor(item.channel)
        self._publish("social.reply.proposed", item)
        return item

    def handle_approval_event(self, event: dict[str, Any]) -> None:
        request = event.get("request")
        metadata = getattr(request, "metadata", {}) if request is not None else {}
        item_id = str(metadata.get("social_inbox_item_id") or "")
        if not item_id:
            return
        item = self._store.get(item_id)
        if item is None:
            return
        event_type = str(event.get("event_type") or "")
        if event_type in {"rejected", "cancelled", "expired"}:
            item.status = SocialInboxStatus.SKIPPED
            item.decision_reason = f"Reply approval {event_type}"
            self._save(item)
            self._advance_processed_cursor(item.channel)
        elif event_type == "failed":
            item.status = SocialInboxStatus.FAILED
            item.decision_reason = "Approved reply execution failed"
            self._save(item)
            self._advance_processed_cursor(item.channel)
        elif event_type == "executed":
            output = dict(metadata.get("execution_result") or {})
            self._apply_reply_result(item, output)
            self._save(item)
            self._advance_processed_cursor(item.channel)

    def list_items(self, status: str = "", limit: int = 200) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self._store.list(status=status, limit=limit)]

    def get_status(self) -> dict[str, Any]:
        items = self._store.list(limit=10000)
        counts = {status.value: 0 for status in SocialInboxStatus}
        for item in items:
            counts[item.status.value] += 1
        return {
            "total": len(items),
            "counts": counts,
            "channels": {
                channel: {
                    "available": bool(adapter.available),
                    "reason": str(getattr(adapter, "reason", "")),
                }
                for channel, adapter in self._adapters.items()
            },
        }

    def _apply_reply_result(self, item: SocialInboxItem, output: dict[str, Any]) -> None:
        adapter = self._adapters.get(item.channel)
        reply_id = adapter.verified_delivery_id(output) if adapter is not None else ""
        if reply_id:
            item.reply_id = reply_id
            item.status = SocialInboxStatus.REPLIED
            item.decision_reason = item.decision_reason or "Reply delivered and post ID verified"
        else:
            item.status = SocialInboxStatus.FAILED
            item.decision_reason = "Reply execution returned no verifiable post ID"

    def _advance_processed_cursor(self, channel: str) -> None:
        updater = self._cursor_updaters.get(channel)
        if updater is None:
            return
        numeric_items: list[tuple[int, SocialInboxItem]] = []
        for item in self._store.list(limit=10000):
            if item.channel != channel:
                continue
            try:
                numeric_items.append((int(item.external_message_id), item))
            except (TypeError, ValueError):
                continue
        items = [item for _, item in sorted(numeric_items, key=lambda pair: pair[0])]
        terminal_ids: list[int] = []
        for item in items:
            if item.status not in TERMINAL_SOCIAL_STATUSES:
                break
            terminal_ids.append(int(item.external_message_id))
        if terminal_ids:
            updater(max(terminal_ids))

    def _generate_json(self, prompt: str) -> dict[str, Any]:
        last_error = ""
        current_prompt = prompt
        for attempt in range(2):
            result = self._llm.generate(
                prompt=current_prompt,
                system_prompt="You are AEGIS SocialManager. Make a reasoned social decision and return JSON only.",
                json_mode=True,
                profile="decision",
            )
            if not getattr(result, "success", False):
                last_error = str(getattr(result, "error", "Social triage LLM failed"))
            else:
                try:
                    return extract_json_object(str(getattr(result, "content", "")))
                except (TypeError, ValueError, json.JSONDecodeError) as exc:
                    last_error = f"{type(exc).__name__}: {exc}"
            if attempt == 0:
                current_prompt = (
                    f"{prompt}\n\nYour previous response was invalid ({last_error}). "
                    "Return one complete JSON object only, with every requested field."
                )
        raise RuntimeError(last_error or "Social triage LLM returned invalid JSON")

    def _require(self, item_id: str) -> SocialInboxItem:
        item = self._store.get(item_id)
        if item is None:
            raise KeyError(f"Social inbox item not found: {item_id}")
        return item

    def _save(self, item: SocialInboxItem) -> SocialInboxItem:
        item.updated_at = int(time.time() * 1000)
        return self._store.update(item)

    def _publish(self, event_type: str, item: SocialInboxItem) -> None:
        if self._events is None or not hasattr(self._events, "publish"):
            return
        try:
            from aegis_ai.event.helpers import build_event

            self._events.publish(
                build_event(
                    event_type,
                    source_server_id="social_manager",
                    payload={
                        "item_id": item.item_id,
                        "channel": item.channel,
                        "status": item.status.value,
                        "approval_id": item.approval_id,
                    },
                )
            )
        except Exception:
            return
