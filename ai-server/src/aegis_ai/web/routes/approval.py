"""Dashboard approval routes."""

from __future__ import annotations

import json
import queue
import uuid
from typing import Any

from flask import Blueprint, Response, jsonify, request


def init_approval_routes(owner: Any) -> None:
    bp = Blueprint("dashboard_approval", __name__)

    def _manager():
        return owner._runtime.approval_manager

    @bp.route("/api/approvals/pending")
    def approvals_pending():
        try:
            return jsonify({"approvals": [r.to_dict() for r in _manager().list_pending()]})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/approvals/<approval_id>")
    def approval_detail(approval_id: str):
        try:
            req = _manager().get(approval_id)
            if req is None:
                return jsonify({"error": "Not found"}), 404
            return jsonify(req.to_dict())
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/approvals/<approval_id>/approve", methods=["POST"])
    def approval_approve(approval_id: str):
        try:
            req = _manager().approve(approval_id, channel="dashboard", user="user")
            if req is None:
                return jsonify({"error": "Not found or not pending"}), 404
            return jsonify(req.to_dict())
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/approvals/<approval_id>/reject", methods=["POST"])
    def approval_reject(approval_id: str):
        try:
            reason = request.json.get("reason", "") if request.is_json else ""
            req = _manager().reject(approval_id, channel="dashboard", user="user", reason=reason)
            if req is None:
                return jsonify({"error": "Not found or not pending"}), 404
            return jsonify(req.to_dict())
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/approvals/<approval_id>/modify-and-approve", methods=["POST"])
    def approval_modify(approval_id: str):
        try:
            if not request.is_json:
                return jsonify({"error": "JSON body required"}), 400
            req = _manager().modify_and_approve(
                approval_id,
                request.json.get("arguments", {}),
                channel="dashboard",
                user="user",
            )
            if req is None:
                return jsonify({"error": "Not found or not pending"}), 404
            return jsonify(req.to_dict())
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/approvals/<approval_id>/cancel", methods=["POST"])
    def approval_cancel(approval_id: str):
        try:
            reason = request.json.get("reason", "") if request.is_json else ""
            req = _manager().cancel(approval_id, reason=reason)
            if req is None:
                return jsonify({"error": "Not found or not cancellable"}), 404
            return jsonify(req.to_dict())
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/approvals/events")
    def approval_events():
        client_id = f"sse_{uuid.uuid4().hex[:8]}"

        def generate():
            try:
                dashboard_channel = getattr(owner._runtime, "_dashboard_approval_channel", None)
                if dashboard_channel is None:
                    yield f"data: {json.dumps({'error': 'Dashboard channel not initialized'})}\n\n"
                    return
                q = dashboard_channel.register_client(client_id)
                try:
                    yield f"data: {json.dumps({'type': 'connected', 'client_id': client_id})}\n\n"
                    while True:
                        try:
                            data = q.get(timeout=30)
                            yield f"data: {data}\n\n"
                        except queue.Empty:
                            yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                finally:
                    dashboard_channel.unregister_client(client_id)
            except GeneratorExit:
                pass
            except Exception as exc:
                yield f"data: {json.dumps({'error': str(exc)})}\n\n"

        return Response(generate(), mimetype="text/event-stream")

    owner.app.register_blueprint(bp)
