"""Approval Fanout — multi-channel approval delivery.

Delivers approval events to registered channels (Dashboard, PC overlay,
Android, Room) in parallel. Channel failures do not block approval creation.

Architecture:
- ApprovalChannel ABC defines the contract for each delivery channel
- ApprovalFanout manages channel registration and parallel delivery
- Sensitive data is masked before delivery
"""

from __future__ import annotations

import asyncio
import logging
import re
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("aegis_ai.approval.fanout")

# ── Sensitive data masking ────────────────────────────────────

_SENSITIVE_KEYS = {"key", "token", "password", "secret", "cookie", "auth", "credential"}
_SENSITIVE_PATTERNS = [
    (re.compile(r"(api[_-]?key|token|password|secret|cookie|auth)[=:]\s*\S+", re.IGNORECASE), r"\1=***"),
    (re.compile(r"Bearer\s+\S+", re.IGNORECASE), "Bearer ***"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "sk-***"),
]


def _mask_value(key: str, value: Any) -> Any:
    if any(s in key.lower() for s in _SENSITIVE_KEYS):
        return "***MASKED***"
    if isinstance(value, str):
        for pat, repl in _SENSITIVE_PATTERNS:
            value = pat.sub(repl, value)
    return value


def mask_approval_request(request: Any) -> dict[str, Any]:
    """Create a masked summary of an approval request for safe delivery.

    Includes only user-facing fields. Excludes raw arguments (uses summary).
    """
    if hasattr(request, "to_dict"):
        data = request.to_dict()
    elif isinstance(request, dict):
        data = request
    else:
        data = {
            "approval_id": getattr(request, "approval_id", ""),
            "capability_id": getattr(request, "capability_id", ""),
            "tool_name": getattr(request, "tool_name", ""),
            "risk_level": getattr(request, "risk_level", ""),
            "approval_reason": getattr(request, "approval_reason", ""),
            "user_facing_summary": getattr(request, "user_facing_summary", ""),
            "arguments_summary": getattr(request, "arguments_summary", ""),
            "expected_outcome": getattr(request, "expected_outcome", ""),
            "possible_side_effects": getattr(request, "possible_side_effects", ""),
            "status": getattr(request, "status", ""),
            "created_at": getattr(request, "created_at", 0),
            "expires_at": getattr(request, "expires_at", 0),
        }

    # Keep only safe fields
    safe_keys = {
        "approval_id", "capability_id", "tool_name", "risk_level",
        "approval_reason", "user_facing_summary", "arguments_summary",
        "expected_outcome", "possible_side_effects",
        "status", "created_at", "expires_at", "source", "source_desire",
        "origin_channel", "conversation_id",
    }
    masked = {}
    for k, v in data.items():
        if k in safe_keys:
            masked[k] = _mask_value(k, v)
    return masked


def build_approval_display_payload(request: Any) -> dict[str, Any]:
    """Build a safe, user-facing approval payload for UI surfaces."""
    summary = mask_approval_request(request)
    capability = str(summary.get("capability_id") or "unknown")
    tool_name = str(summary.get("tool_name") or capability)
    reason = str(summary.get("approval_reason") or "").strip()
    user_summary = str(summary.get("user_facing_summary") or "").strip()
    args_summary = str(summary.get("arguments_summary") or "").strip()
    risk = str(summary.get("risk_level") or "unknown")
    expected = str(summary.get("expected_outcome") or "").strip()
    side_effects = str(summary.get("possible_side_effects") or "").strip()

    if not expected:
        expected = "承認後、この操作を一度だけ実行します。"
    if not side_effects and risk not in {"low", "read_only", "safe", "safe_action"}:
        side_effects = "外部サービス、端末、またはデバイスの状態が変更される可能性があります。"

    title = f"承認が必要: {tool_name}"
    body_lines: list[str] = []
    if reason:
        body_lines.append(f"理由: {reason}")
    if user_summary:
        body_lines.append(user_summary)
    elif args_summary:
        body_lines.append(f"内容: {args_summary}")
    if expected:
        body_lines.append(f"結果: {expected}")
    if side_effects:
        body_lines.append(f"注意: {side_effects}")
    body_lines.append(f"リスク: {risk}")
    body_lines.append(f"ID: {summary.get('approval_id', '')}")

    payload = dict(summary)
    payload.update(
        {
            "title": title,
            "body": "\n".join(line for line in body_lines if line),
            "expected_outcome": expected,
            "possible_side_effects": side_effects,
        }
    )
    return payload


# ── Approval Event ────────────────────────────────────────────

@dataclass
class ApprovalEvent:
    """Event delivered to channels on approval state changes."""

    approval_id: str = ""
    event_type: str = ""  # created, approved, rejected, modified, expired, cancelled, executing, executed, failed
    request_summary: dict[str, Any] = field(default_factory=dict)
    state: str = ""  # current status
    timestamp: int = 0  # epoch ms
    channel: str = ""  # which channel triggered this event
    user: str = ""  # who triggered this event

    @classmethod
    def from_request(
        cls,
        request: Any,
        event_type: str,
        channel: str = "",
        user: str = "",
    ) -> ApprovalEvent:
        """Create an event from an ApprovalRequest."""
        return cls(
            approval_id=getattr(request, "approval_id", ""),
            event_type=event_type,
            request_summary=build_approval_display_payload(request),
            state=getattr(request, "status", ""),
            timestamp=int(time.time() * 1000),
            channel=channel,
            user=user,
        )


# ── Channel ABC ───────────────────────────────────────────────

class ApprovalChannel(ABC):
    """Abstract base class for approval delivery channels."""

    @property
    @abstractmethod
    def channel_id(self) -> str:
        """Unique channel identifier (e.g., 'dashboard', 'pc_overlay')."""
        ...

    @abstractmethod
    async def deliver(self, event: ApprovalEvent) -> bool:
        """Deliver a 'created' event. Return True on success."""
        ...

    @abstractmethod
    async def update(self, event: ApprovalEvent) -> bool:
        """Deliver an update event (approved/rejected/etc). Return True on success."""
        ...

    async def health_check(self) -> bool:
        """Check if channel is available. Default: True."""
        return True


# ── Fanout Manager ────────────────────────────────────────────

class ApprovalFanout:
    """Manages parallel delivery of approval events to registered channels.

    Parameters
    ----------
    audit_log:
        Optional audit log for recording delivery status.
    """

    def __init__(self, audit_log: Any = None) -> None:
        self._channels: dict[str, ApprovalChannel] = {}
        self._audit = audit_log
        self._lock = threading.Lock()

    def register_channel(self, channel: ApprovalChannel) -> None:
        """Register a delivery channel."""
        with self._lock:
            self._channels[channel.channel_id] = channel
        logger.info("Approval channel registered: %s", channel.channel_id)

    def unregister_channel(self, channel_id: str) -> None:
        """Unregister a delivery channel."""
        with self._lock:
            self._channels.pop(channel_id, None)
        logger.info("Approval channel unregistered: %s", channel_id)

    def get_channels(self) -> list[ApprovalChannel]:
        """Return list of registered channels."""
        with self._lock:
            return list(self._channels.values())

    async def fanout(self, event: ApprovalEvent) -> dict[str, bool]:
        """Deliver a 'created' event to all registered channels in parallel.

        Returns dict of channel_id -> success.
        Channel failures are logged but do NOT raise.
        """
        with self._lock:
            channels = list(self._channels.values())
        if not channels:
            return {}

        results: dict[str, bool] = {}
        tasks = []
        for ch in channels:
            tasks.append(self._deliver_to_channel(ch, event, results))

        await asyncio.gather(*tasks, return_exceptions=True)

        self._record_delivery(event, results)
        return results

    async def fanout_update(self, event: ApprovalEvent) -> dict[str, bool]:
        """Deliver an update event to all registered channels in parallel.

        Returns dict of channel_id -> success.
        """
        with self._lock:
            channels = list(self._channels.values())
        if not channels:
            return {}

        results: dict[str, bool] = {}
        tasks = []
        for ch in channels:
            tasks.append(self._update_to_channel(ch, event, results))

        await asyncio.gather(*tasks, return_exceptions=True)

        self._record_delivery(event, results)
        return results

    async def _deliver_to_channel(
        self,
        channel: ApprovalChannel,
        event: ApprovalEvent,
        results: dict[str, bool],
    ) -> None:
        """Deliver to a single channel, recording result."""
        try:
            success = await channel.deliver(event)
            results[channel.channel_id] = success
            if not success:
                logger.warning(
                    "Approval delivery failed: channel=%s approval=%s",
                    channel.channel_id, event.approval_id,
                )
        except Exception:
            results[channel.channel_id] = False
            logger.exception(
                "Approval delivery error: channel=%s approval=%s",
                channel.channel_id, event.approval_id,
            )

    async def _update_to_channel(
        self,
        channel: ApprovalChannel,
        event: ApprovalEvent,
        results: dict[str, bool],
    ) -> None:
        """Update a single channel, recording result."""
        try:
            success = await channel.update(event)
            results[channel.channel_id] = success
            if not success:
                logger.warning(
                    "Approval update failed: channel=%s approval=%s event=%s",
                    channel.channel_id, event.approval_id, event.event_type,
                )
        except Exception:
            results[channel.channel_id] = False
            logger.exception(
                "Approval update error: channel=%s approval=%s",
                channel.channel_id, event.approval_id,
            )

    def _record_delivery(
        self,
        event: ApprovalEvent,
        results: dict[str, bool],
    ) -> None:
        """Record delivery status to audit log."""
        if self._audit is None:
            return
        failed = [ch_id for ch_id, ok in results.items() if not ok]
        succeeded = [ch_id for ch_id, ok in results.items() if ok]
        if failed:
            try:
                self._audit.append(
                    event_type="approval_delivery_failed",
                    details={
                        "approval_id": event.approval_id,
                        "event_type": event.event_type,
                        "failed_channels": failed,
                        "succeeded_channels": succeeded,
                    },
                )
            except Exception:
                logger.debug("Failed to record delivery audit", exc_info=True)
