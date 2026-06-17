"""Dashboard Approval Channel — SSE-based real-time approval notifications."""

from __future__ import annotations

import asyncio
import json
import logging
import queue
import threading
from typing import Any

from aegis_ai.approval.fanout import ApprovalChannel, ApprovalEvent

logger = logging.getLogger("aegis_ai.approval.channels.dashboard")


class DashboardApprovalChannel(ApprovalChannel):
    """Delivers approval events to Dashboard via SSE.

    Maintains a list of connected SSE clients. Each client has a queue.
    Events are pushed to all connected clients.
    """

    def __init__(self) -> None:
        self._clients: dict[str, queue.Queue] = {}
        self._lock = threading.Lock()

    @property
    def channel_id(self) -> str:
        return "dashboard"

    async def deliver(self, event: ApprovalEvent) -> bool:
        """Deliver a 'created' event to all SSE clients."""
        return self._broadcast(event)

    async def update(self, event: ApprovalEvent) -> bool:
        """Deliver an update event to all SSE clients."""
        return self._broadcast(event)

    async def health_check(self) -> bool:
        return True

    def register_client(self, client_id: str) -> queue.Queue:
        """Register a new SSE client. Returns its event queue."""
        q: queue.Queue = queue.Queue()
        with self._lock:
            self._clients[client_id] = q
        return q

    def unregister_client(self, client_id: str) -> None:
        """Unregister an SSE client."""
        with self._lock:
            self._clients.pop(client_id, None)

    def client_count(self) -> int:
        with self._lock:
            return len(self._clients)

    def _broadcast(self, event: ApprovalEvent) -> bool:
        """Broadcast event to all connected clients."""
        data = json.dumps({
            "approval_id": event.approval_id,
            "event_type": event.event_type,
            "request_summary": event.request_summary,
            "state": event.state,
            "timestamp": event.timestamp,
            "channel": event.channel,
            "user": event.user,
        }, ensure_ascii=False)

        with self._lock:
            clients = list(self._clients.items())

        for client_id, q in clients:
            try:
                q.put_nowait(data)
            except queue.Full:
                logger.warning("SSE client queue full, dropping: %s", client_id)

        return True
