"""Room Approval Channel — delivers approvals to Room Server (display + TTS)."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.approval.fanout import ApprovalChannel, ApprovalEvent

logger = logging.getLogger("aegis_ai.approval.channels.room")


class RoomApprovalChannel(ApprovalChannel):
    """Delivers approval events to Room Server via display and TTS.

    Uses ServerExecutor to send display/TTS commands to Room Server.
    Voice-based approval is DISABLED — display and TTS only.
    Fire-and-forget: Room Server unreachable does not block approval.
    """

    def __init__(self, server_executor: Any = None) -> None:
        self._executor = server_executor

    @property
    def channel_id(self) -> str:
        return "room"

    async def deliver(self, event: ApprovalEvent) -> bool:
        """Show approval on Room display and read aloud via TTS."""
        display_ok = self._send_display(event)
        tts_ok = self._send_tts(event)
        return display_ok or tts_ok

    async def update(self, event: ApprovalEvent) -> bool:
        """Update display and read state change via TTS."""
        display_ok = self._send_display(event, is_update=True)
        tts_ok = self._send_tts(event, is_update=True)
        return display_ok or tts_ok

    async def health_check(self) -> bool:
        if self._executor is None:
            return False
        try:
            result = self._executor.execute_capability(
                "room-server.system.health_check", {}
            )
            return result is not None
        except Exception:
            return False

    def _send_display(self, event: ApprovalEvent, is_update: bool = False) -> bool:
        """Send display command to Room Server."""
        if self._executor is None:
            return False

        try:
            summary = event.request_summary
            title = f"承認が必要: {summary.get('tool_name', '')}"
            body = summary.get("user_facing_summary", "操作の承認が必要です")
            approval_id = event.approval_id

            if is_update:
                title = f"承認更新: {event.state}"
                body = f"ID: {approval_id}"

            self._executor.execute_capability(
                "room-server.display.show_approval",
                {
                    "title": title,
                    "body": body,
                    "approval_id": approval_id,
                    "state": event.state,
                },
            )
            return True
        except Exception:
            logger.debug("Room display failed for %s", event.approval_id)
            return False

    def _send_tts(self, event: ApprovalEvent, is_update: bool = False) -> bool:
        """Send TTS readout to Room Server."""
        if self._executor is None:
            return False

        try:
            summary = event.request_summary
            tool_name = summary.get("tool_name", "不明な操作")

            if is_update:
                text = f"承認状態が更新されました。{event.state}。ID: {event.approval_id}"
            else:
                text = f"承認が必要です。{tool_name}。リスクレベル: {summary.get('risk_level', '不明')}"

            self._executor.execute_capability(
                "room-server.tts.say",
                {"text": text},
            )
            return True
        except Exception:
            logger.debug("Room TTS failed for %s", event.approval_id)
            return False
