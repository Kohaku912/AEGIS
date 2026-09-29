"""AEGIS-initiated confirmation endpoints.

These endpoints serve ``aegis_ai.confirmation`` — the questions AEGIS *chooses* to ask
the user. They replace the compatibility stub that stood here while the forced approval
gate was being retired: the stub returned ``[]`` and ``410 Gone`` because nothing could
create an approval any more.

What changed, precisely:

* The **forced gate is still gone.** No endpoint here can block a capability, and
  nothing in the execution path calls this module. A capability runs because the LLM
  decided to run it, not because a request was approved.
* The **question is back.** AEGIS raises a confirmation when it judges that the user
  should decide, and the dashboard renders it. The answer informs what AEGIS does next;
  it does not unblock anything that was waiting.

The URLs, methods and JSON field names are unchanged from the historical contract, so
the shipped ``web-ui`` bundle keeps working without a new build.

**CSRF and authentication are not implemented here.** ``aegis_ai.auth.session_middleware``
enforces them centrally for every ``POST`` (``X-CSRF-Token``) and additionally requires a
fresh passkey for ``/approve``, ``/modify-and-approve`` and ``/cancel``. Re-checking them
per route would duplicate — and eventually contradict — that one implementation.
"""

from __future__ import annotations

import json
import logging
import queue
import uuid
from typing import Any

from flask import Blueprint, Response, jsonify, request

logger = logging.getLogger("aegis_ai.web.routes.approval")

#: How often an idle stream emits a keep-alive frame. The dashboard's fetch is a long
#: poll with its own timeout, so a silent stream would be reaped by the browser.
HEARTBEAT_SECONDS = 30.0

#: Cap on queued frames per client. A client that stops reading must not grow the
#: server's memory without bound; dropping frames is safe because the queue is a
#: "something changed" signal and the client re-reads the list on reconnect.
_CLIENT_QUEUE_SIZE = 100


class ConfirmationUnavailable(RuntimeError):
    """The store is not reachable — reported as 503 rather than silently faked."""


def init_approval_routes(owner: Any) -> None:
    """Register the confirmation blueprint.

    ``owner`` supplies ``.app`` (Flask) and ``._runtime``, like the other route modules.
    """
    bp = Blueprint("dashboard_approval", __name__)

    @bp.get("/api/approvals/pending")
    def approvals_pending():
        """Open confirmations, oldest first."""
        store = _require_store(owner)
        pending = store.pending()
        return jsonify(
            {
                "approvals": [item.to_dict() for item in pending],
                "pending_count": len(pending),
            }
        )

    @bp.get("/api/approvals/events")
    def approval_events():
        """Server-sent events: ``connected``, then live ``approval.created`` / ``.resolved``.

        Not consumed by the currently shipped bundle — it re-reads the overview payload
        instead — but it is part of the wire contract this module owns, and it is the
        only way a client can learn about a question without polling.
        """
        store = _require_store(owner)

        def generate():
            channel: queue.Queue = queue.Queue(maxsize=_CLIENT_QUEUE_SIZE)

            def _on_event(event: str, item: Any) -> None:
                try:
                    channel.put_nowait({"type": event, "approval": item.to_dict()})
                except queue.Full:
                    logger.debug("Dropped a confirmation event for a slow client")

            unsubscribe = store.add_listener(_on_event)
            try:
                yield _sse_frame({"type": "connected", "client_id": f"sse_{uuid.uuid4().hex[:8]}"})
                while True:
                    try:
                        frame = channel.get(timeout=HEARTBEAT_SECONDS)
                    except queue.Empty:
                        yield _sse_frame({"type": "heartbeat"})
                        continue
                    yield _sse_frame(frame)
            finally:
                # A closed tab must not leave a listener behind: the store would keep
                # appending to a queue nobody drains.
                unsubscribe()

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    @bp.get("/api/approvals/<approval_id>")
    def approval_detail(approval_id: str):
        store = _require_store(owner)
        item = store.get(approval_id)
        if item is None:
            return jsonify({"error": "unknown_confirmation", "approval_id": approval_id}), 404
        return jsonify(item.to_dict())

    @bp.post("/api/approvals/<approval_id>/approve")
    def approval_approve(approval_id: str):
        return _decide(owner, approval_id, "approve")

    @bp.post("/api/approvals/<approval_id>/reject")
    def approval_reject(approval_id: str):
        return _decide(owner, approval_id, "reject")

    @bp.post("/api/approvals/<approval_id>/cancel")
    def approval_cancel(approval_id: str):
        return _decide(owner, approval_id, "cancel")

    @bp.post("/api/approvals/<approval_id>/modify-and-approve")
    def approval_modify_and_approve(approval_id: str):
        return _decide(owner, approval_id, "modify_and_approve")

    @bp.errorhandler(ConfirmationUnavailable)
    def _store_unavailable(exc: ConfirmationUnavailable):
        """One handler for every route in this blueprint, reads included.

        Catching this per-view left the read endpoints returning 500 while only the
        decision endpoints degraded cleanly — the kind of inconsistency that only shows
        up when the store is actually missing.
        """
        return jsonify({"error": "confirmation_store_unavailable", "message": str(exc)}), 503

    owner.app.register_blueprint(bp)


# ── helpers ───────────────────────────────────────────────────────────────────


def _sse_frame(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _require_store(owner: Any) -> Any:
    """Return the process-wide confirmation store, or raise ``ConfirmationUnavailable``.

    Deliberately does **not** boot a runtime. Creating a second store on demand would
    split the queue in two — AEGIS's questions in one, the dashboard reading the other —
    and that failure would be invisible. An honest 503 is better.
    """
    runtime = getattr(owner, "_runtime", None)
    if runtime is None:
        from aegis_ai.runtime import peek_runtime

        runtime = peek_runtime()
    store = getattr(runtime, "confirmation_store", None) if runtime is not None else None
    if store is None:
        raise ConfirmationUnavailable("the confirmation store is not available")
    return store


def _decide(owner: Any, approval_id: str, action: str):
    """Apply one decision and report the resulting record.

    ``404`` means there is no such confirmation; ``409`` means it exists but is no longer
    open. Both are distinguished from ``503`` (the store is unreachable), so a client can
    tell "you are too late" apart from "the server is unwell". The 503 comes from the
    blueprint's ``ConfirmationUnavailable`` handler rather than a local try/except.
    """
    store = _require_store(owner)

    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        body = {}
    decided_by = str(body.get("decided_by") or "user")
    note = str(body.get("note") or "")

    if store.get(approval_id) is None:
        return jsonify({"error": "unknown_confirmation", "approval_id": approval_id}), 404

    if action == "modify_and_approve":
        edits = body.get("edits")
        if not isinstance(edits, dict):
            edits = {}
        result = store.modify_and_approve(
            approval_id, edits=edits, decided_by=decided_by, note=note
        )
    else:
        result = getattr(store, action)(approval_id, decided_by=decided_by, note=note)

    if result is None:
        current = store.get(approval_id)
        return (
            jsonify(
                {
                    "error": "confirmation_not_open",
                    "approval_id": approval_id,
                    "status": str(getattr(current, "status", "")),
                }
            ),
            409,
        )
    return jsonify({"ok": True, "approval": result.to_dict()})
