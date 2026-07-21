"""LLM-driven social triage, approval binding, and reply verification."""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, is_dataclass
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
    ) -> None:
        self._store = SocialInboxStore(data_dir)
        self._llm = llm
        self._broker = tool_broker
        self._events = event_manager
        self._audit = audit_manager
        self._cursor_updaters: dict[str, Callable[[int], Any]] = {}
        self._relationship_provider: Callable[[SocialInboxItem], dict[str, Any]] | None = None
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

    def ingest(self, channel: str, messages: list[Any]) -> list[SocialInboxItem]:
        created: list[SocialInboxItem] = []
        now = int(time.time() * 1000)
        for message in messages:
            raw = asdict(message) if is_dataclass(message) else dict(message)
            external_id = str(raw.get("id") or raw.get("message_id") or raw.get("external_message_id") or "")
            if not external_id:
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
                author=str(raw.get("author") or raw.get("author_name") or raw.get("username") or ""),
                body=str(raw.get("body") or raw.get("content") or raw.get("text") or ""),
                received_at=int(raw.get("created_at") or raw.get("timestamp") or now),
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
                metadata={"source": channel},
            )
            stored = self._store.upsert(item)
            if stored.item_id == item.item_id:
                created.append(stored)
                self._publish("social.inbox.received", stored)
        return created

    def triage(self, item_id: str, *, relationship: dict[str, Any] | None = None) -> SocialInboxItem:
        item = self._require(item_id)
        item.relationship = relationship or item.relationship
        if self._llm is None:
            item.status = SocialInboxStatus.FAILED
            item.decision = "observe_more"
            item.decision_reason = "LLM unavailable; social intent was not guessed."
            saved = self._save(item)
            self._advance_processed_cursor(item.channel)
            return saved

        prompt = f"""Decide how AEGIS should respond to this social inbox item.
Return JSON only. Do not infer from keyword rules; reason from the full message and context.

Message:
{json.dumps(item.to_dict(), ensure_ascii=False)}

Relationship context:
{json.dumps(relationship or item.relationship, ensure_ascii=False)}

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
            item.status = SocialInboxStatus.NEEDS_REPLY
            item.draft_body = str(data.get("draft_body") or "").strip()
        elif decision == "acknowledge":
            item.status = SocialInboxStatus.ACKNOWLEDGED
        elif decision == "skip":
            item.status = SocialInboxStatus.SKIPPED
        else:
            item.status = SocialInboxStatus.UNTRIAGED
        self._save(item)
        self._publish("social.inbox.triaged", item)
        self._advance_processed_cursor(item.channel)
        return item

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
                if current.status == SocialInboxStatus.NEEDS_REPLY:
                    current = self.propose_reply(current.item_id)
                processed.append(current)
            except Exception as exc:
                current = self._store.get(item.item_id)
                if current is None:
                    continue
                current.status = SocialInboxStatus.FAILED
                current.decision = current.decision or "observe_more"
                current.decision_reason = f"Social processing failed: {exc}"
                processed.append(self._save(current))
                self._publish("social.inbox.failed", current)
                self._advance_processed_cursor(current.channel)
        return processed

    def propose_reply(self, item_id: str) -> SocialInboxItem:
        item = self._require(item_id)
        if item.status != SocialInboxStatus.NEEDS_REPLY or not item.draft_body:
            raise ValueError("A triaged reply draft is required before proposal")
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
        result = self._llm.generate(
            prompt=prompt,
            system_prompt="You are AEGIS SocialManager. Make a reasoned social decision and return JSON only.",
            max_tokens=600,
            json_mode=True,
        )
        if not getattr(result, "success", False):
            raise RuntimeError(getattr(result, "error", "Social triage LLM failed"))
        return extract_json_object(str(getattr(result, "content", "")))

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
            from aegis_schema.models import Event

            self._events.publish(
                Event(
                    event_type=event_type,
                    source="social_manager",
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
