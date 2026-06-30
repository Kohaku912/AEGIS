"""Android approval notification channel."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.approval.fanout import ApprovalChannel, ApprovalEvent

logger = logging.getLogger("aegis_ai.approval.channels.android")


class AndroidApprovalChannel(ApprovalChannel):
    """Deliver approval events to Android devices."""

    def __init__(self, android_manager: Any = None) -> None:
        self._android_manager = android_manager

    @property
    def channel_id(self) -> str:
        return "android"

    async def deliver(self, event: ApprovalEvent) -> bool:
        return self._send_notification(event)

    async def update(self, event: ApprovalEvent) -> bool:
        return self._send_notification(event, is_update=True)

    async def health_check(self) -> bool:
        if self._android_manager is None:
            return False
        try:
            return bool(self._android_manager.get_status().get("online"))
        except Exception:
            return False

    def _send_notification(self, event: ApprovalEvent, is_update: bool = False) -> bool:
        if self._android_manager is None:
            logger.debug("No Android manager, skipping Android approval notification")
            return False

        try:
            summary = event.request_summary
            approval_id = event.approval_id
            title = str(
                summary.get("title")
                or f"承認が必要: {summary.get('tool_name', summary.get('capability_id', 'unknown'))}"
            )
            body = str(
                summary.get("body")
                or summary.get("user_facing_summary")
                or summary.get("approval_reason")
                or "操作の承認が必要です"
            )
            if is_update:
                title = f"承認更新: {event.state}"
                body = f"状態: {event.state}\nID: {approval_id}\n{body}"

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
