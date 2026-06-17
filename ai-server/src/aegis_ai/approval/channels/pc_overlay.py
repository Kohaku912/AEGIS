"""PC Overlay Approval Channel — delivers approvals to PC Server overlay."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.approval.fanout import ApprovalChannel, ApprovalEvent

logger = logging.getLogger("aegis_ai.approval.channels.pc_overlay")


class PcOverlayApprovalChannel(ApprovalChannel):
    """Delivers approval events to PC Server via overlay display.

    Uses ServerExecutor to send overlay commands to PC Server.
    Fire-and-forget: PC Server unreachable does not block approval.
    """

    def __init__(self, server_executor: Any = None) -> None:
        self._executor = server_executor

    @property
    def channel_id(self) -> str:
        return "pc_overlay"

    async def deliver(self, event: ApprovalEvent) -> bool:
        """Show approval overlay on PC screen."""
        return self._send_overlay(event, action="show")

    async def update(self, event: ApprovalEvent) -> bool:
        """Update overlay state (approved/rejected)."""
        return self._send_overlay(event, action="update")

    async def health_check(self) -> bool:
        if self._executor is None:
            return False
        try:
            result = self._executor.execute_capability(
                "pc-server.system.health_check", {}
            )
            return result is not None
        except Exception:
            return False

    def _send_overlay(self, event: ApprovalEvent, action: str) -> bool:
        """Send overlay command to PC Server."""
        if self._executor is None:
            logger.debug("No server executor, skipping PC overlay")
            return False

        try:
            summary = event.request_summary
            title = f"承認が必要: {summary.get('tool_name', summary.get('capability_id', 'unknown'))}"
            body = summary.get("user_facing_summary", "操作の承認が必要です")
            risk = summary.get("risk_level", "unknown")
            approval_id = event.approval_id

            if action == "show":
                overlay_body = (
                    f"{body}\n\n"
                    f"リスク: {risk}\n"
                    f"ID: {approval_id}\n\n"
                    f"[Y] 承認  [N] 拒否  [ESC] キャンセル"
                )
                cmd = f"show_approval_overlay {title}|{overlay_body}|{approval_id}"
            else:
                state = event.state
                overlay_body = f"状態: {state}\nID: {approval_id}"
                cmd = f"update_approval_overlay {approval_id}|{state}"

            self._executor.execute_capability(
                "pc-server.approval.overlay",
                {"command": cmd},
            )
            return True
        except Exception:
            logger.exception("PC overlay delivery failed for %s", event.approval_id)
            return False
