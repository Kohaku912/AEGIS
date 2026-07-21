"""PC overlay approval channel."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.approval.fanout import ApprovalChannel, ApprovalEvent

logger = logging.getLogger("aegis_ai.approval.channels.pc_overlay")


class PcOverlayApprovalChannel(ApprovalChannel):
    """Deliver approval events to PC Server via overlay display."""

    def __init__(self, server_executor: Any = None) -> None:
        self._executor = server_executor

    @property
    def channel_id(self) -> str:
        return "pc_overlay"

    async def deliver(self, event: ApprovalEvent) -> bool:
        return self._send_overlay(event, action="show")

    async def update(self, event: ApprovalEvent) -> bool:
        return self._send_overlay(event, action="update")

    async def health_check(self) -> bool:
        if self._executor is None:
            return False
        try:
            result = self._executor.execute_capability("pc-server.system.health_check", {})
            return self._successful_result(result, require_shown=False)
        except Exception:
            return False

    def _send_overlay(self, event: ApprovalEvent, action: str) -> bool:
        if self._executor is None:
            logger.debug("No server executor, skipping PC overlay")
            return False

        try:
            # Terminal updates replace the pending notice briefly. The PC
            # overlay protocol has no remote window handle to dismiss safely.
            if event.state in ("approved", "rejected", "executed", "failed", "cancelled", "expired"):
                result = self._executor.execute_capability(
                    "pc-server.overlay.show_rich",
                    {
                        "title": f"Approval {event.state}",
                        "body": f"{event.approval_id}: {event.state}",
                        "duration_seconds": 2,
                        "style": "info" if event.state in {"approved", "executed"} else "warning",
                    },
                )
                return self._successful_result(result)

            summary = event.request_summary
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

            result = self._executor.execute_capability(
                "pc-server.overlay.show_rich",
                {
                    "title": title.replace("\n", " "),
                    "body": body,
                    "duration_seconds": 30,
                    "style": "approval",
                },
            )
            return self._successful_result(result)
        except Exception:
            logger.exception("PC overlay delivery failed for %s", event.approval_id)
            return False

    @staticmethod
    def _successful_result(result: Any, *, require_shown: bool = True) -> bool:
        if not isinstance(result, dict) or result.get("error"):
            return False
        if result.get("ok") is False:
            return False
        if require_shown and result.get("shown") is not True:
            return False
        if require_shown and not str(result.get("delivery_id") or ""):
            return False
        return True
