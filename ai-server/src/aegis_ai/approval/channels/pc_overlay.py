"""PC overlay approval channel."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.approval.fanout import ApprovalChannel, ApprovalEvent

logger = logging.getLogger("aegis_ai.approval.channels.pc_overlay")


class PcOverlayApprovalChannel(ApprovalChannel):
    """Deliver approval events to PC Server via interactive Y/N overlay."""

    def __init__(self, server_executor: Any = None, approval_manager: Any = None) -> None:
        self._executor = server_executor
        self._approval_manager = approval_manager

    @property
    def channel_id(self) -> str:
        return "pc_overlay"

    async def deliver(self, event: ApprovalEvent) -> bool:
        return self._handle(event)

    async def update(self, event: ApprovalEvent) -> bool:
        return self._handle(event)

    async def health_check(self) -> bool:
        if self._executor is None:
            return False
        try:
            result = self._executor.execute_capability("pc-server.system.health_check", {})
            return self._successful_result(result, require_decision=False)
        except Exception:
            return False

    def _handle(self, event: ApprovalEvent) -> bool:
        if self._executor is None:
            logger.debug("No server executor, skipping PC overlay")
            return False

        try:
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
                return self._successful_result(result, require_decision=False)

            summary = event.request_summary
            title = str(
                summary.get("title")
                or f"Approval required: {summary.get('tool_name', summary.get('capability_id', 'unknown'))}"
            )
            body = str(
                summary.get("body")
                or summary.get("user_facing_summary")
                or summary.get("approval_reason")
                or "操作の承認が必要です"
            )
            action = f"{title}\n{body}".strip()
            # Blocking Y/N overlay (not show_rich, which is dismiss-only).
            result = self._executor.execute_capability(
                "pc-server.approval.overlay",
                {
                    "action": action.replace("\n", " | ")[:500],
                    "timeout": 60,
                },
            )
            if not self._successful_result(result, require_decision=True):
                return False
            self._apply_decision(event.approval_id, result)
            return True
        except Exception:
            logger.exception("PC overlay delivery failed for %s", event.approval_id)
            return False

    def _apply_decision(self, approval_id: str, result: dict[str, Any]) -> None:
        manager = self._approval_manager
        if manager is None:
            logger.warning("PC overlay decision received but approval_manager is unset")
            return
        approved = bool(result.get("approved"))
        response = str(result.get("response") or "")
        try:
            if approved:
                manager.approve(approval_id, channel="pc_overlay", user="pc_user")
                return
            lowered = response.lower()
            if any(token in lowered for token in ("esc", "cancel", "timeout", "dismiss")):
                # Soft dismiss: keep central pending so Dashboard/Android can still decide.
                logger.info(
                    "PC overlay dismissed without decision for %s: %s",
                    approval_id,
                    response or "dismissed",
                )
                return
            if hasattr(manager, "global_reject"):
                manager.global_reject(
                    approval_id,
                    channel="pc_overlay",
                    user="pc_user",
                    reason=response or "rejected via PC overlay",
                )
            else:
                manager.reject(approval_id, channel="pc_overlay", user="pc_user", reason=response)
        except Exception:
            logger.exception("Failed to apply PC overlay decision for %s", approval_id)

    @staticmethod
    def _successful_result(result: Any, *, require_decision: bool) -> bool:
        if not isinstance(result, dict) or result.get("error"):
            return False
        if result.get("ok") is False:
            return False
        if require_decision:
            # overlay_approval returns approved bool + request_id
            return "approved" in result
        if result.get("shown") is True:
            return True
        return True
