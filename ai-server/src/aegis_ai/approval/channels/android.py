"""Android Approval Channel — delivers approvals as Android notifications."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.approval.fanout import ApprovalChannel, ApprovalEvent

logger = logging.getLogger("aegis_ai.approval.channels.android")


class AndroidApprovalChannel(ApprovalChannel):
    """Delivers approval events to Android Server as notifications.

    Uses ServerExecutor to send notification commands to Android Server.
    Fire-and-forget: Android Server unreachable does not block approval.
    """

    def __init__(self, android_manager: Any = None) -> None:
        self._android_manager = android_manager

    @property
    def channel_id(self) -> str:
        return "android"

    async def deliver(self, event: ApprovalEvent) -> bool:
        """Send approval notification to Android device."""
        return self._send_notification(event)

    async def update(self, event: ApprovalEvent) -> bool:
        """Update notification state on Android device."""
        return self._send_notification(event, is_update=True)

    async def health_check(self) -> bool:
        if self._android_manager is None:
            return False
        try:
            return bool(self._android_manager.get_status().get("online"))
        except Exception:
            return False

    def _send_notification(self, event: ApprovalEvent, is_update: bool = False) -> bool:
        """Send notification to Android Server."""
        if self._android_manager is None:
            logger.debug("No server executor, skipping Android notification")
            return False

        try:
            summary = event.request_summary
            title = f"承認が必要: {summary.get('tool_name', summary.get('capability_id', 'unknown'))}"
            body = summary.get("user_facing_summary", "操作の承認が必要です")
            approval_id = event.approval_id

            if is_update:
                title = f"承認更新: {event.state}"
                body = f"ID: {approval_id} — 状態: {event.state}"

            return self._android_manager.send_approval_to_android(
                approval_id=approval_id,
                title=title,
                body=body,
                state=event.state,
                summary=summary,
            )
        except Exception:
            logger.exception("Android notification failed for %s", event.approval_id)
            return False
