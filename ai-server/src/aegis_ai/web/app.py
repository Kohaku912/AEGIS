"""Approval UI — Flask web application for user approval of dangerous operations.

Architecture reference: docs/architecture.md §7.4

Security:
- localhost-only by default
- No external exposure
- Secrets masked in payload preview
- Approval IDs are UUID-based (hard to guess)
- CSRF tokens in forms
"""

from __future__ import annotations

import logging
import os
import secrets
from typing import Any

from flask import Flask, jsonify, render_template, request

from approval import ApprovalStore, ApprovalStatus, ApprovalType

logger = logging.getLogger("aegis_ai.web")


class ApprovalWebApp:
    """Flask-based Approval UI for AEGIS.

    Provides:
    - GET  /approvals              → list all pending approvals
    - GET  /approvals/<id>         → detail view
    - POST /approvals/<id>/approve-once
    - POST /approvals/<id>/approve-session
    - POST /approvals/<id>/reject
    - POST /approvals/<id>/reject-remember
    """

    def __init__(self, approval_store: ApprovalStore, secret_key: str | None = None) -> None:
        self._store = approval_store
        self._app = Flask(__name__, template_folder="templates")
        self._app.secret_key = secret_key or secrets.token_hex(32)
        self._csrf_tokens: dict[str, str] = {}
        self._setup_routes()

    @property
    def app(self) -> Flask:
        return self._app

    def run(self, host: str = "127.0.0.1", port: int = 8080, debug: bool = False) -> None:
        """Run the Flask development server (localhost only)."""
        self._app.run(host=host, port=port, debug=debug)

    def _setup_routes(self) -> None:
        app = self._app

        @app.route("/approvals")
        def list_approvals():
            pending = self._store.get_pending()
            items = []
            for req in pending:
                items.append({
                    "approval_id": req.approval_id,
                    "capability_id": req.capability_id,
                    "tool_name": req.tool_name,
                    "requested_action": req.requested_action,
                    "risk_level": req.risk_level,
                    "expires_in_seconds": max(0, (req.expires_at_ms - int(__import__("time").time() * 1000)) // 1000),
                    "status": req.status.name,
                })
            return render_template("approvals.html", approvals=items)

        @app.route("/approvals/<approval_id>")
        def approval_detail(approval_id: str):
            req = self._store.get_request(approval_id)
            if req is None:
                return "Not found", 404
            expires_in = max(0, (req.expires_at_ms - int(__import__("time").time() * 1000)) // 1000)
            # Generate CSRF token
            csrf = secrets.token_hex(16)
            self._csrf_tokens[approval_id] = csrf

            # Mask secrets in payload
            masked = self._mask_payload(req.payload_preview)

            return render_template("approval_detail.html",
                approval=req, expires_in=expires_in, csrf_token=csrf,
                masked_payload=masked,
            )

        def _get_store_result(approval_id: str, action: str) -> tuple[dict[str, Any], int]:
            """Helper for POST handlers: validate CSRF and process action."""
            # CSRF check
            token = request.form.get("csrf_token", "")
            if self._csrf_tokens.get(approval_id) != token:
                return {"error": "Invalid CSRF token"}, 403

            if action == "approve_once":
                ok = self._store.approve_once(approval_id)
            elif action == "approve_session":
                ok = self._store.approve_for_session(approval_id)
            elif action == "reject":
                ok = self._store.reject(approval_id)
            elif action == "reject_remember":
                ok = self._store.reject_and_remember(approval_id)
            else:
                return {"error": "Unknown action"}, 400

            # Clean up CSRF
            self._csrf_tokens.pop(approval_id, None)

            if ok:
                return {"status": "ok", "action": action, "approval_id": approval_id}, 200
            else:
                return {"error": "Approval not found or already processed"}, 404

        @app.route("/approvals/<approval_id>/approve-once", methods=["POST"])
        def approve_once(approval_id: str):
            result, code = _get_store_result(approval_id, "approve_once")
            if code == 200:
                return render_template("result.html", message="Approved (one-time)", success=True)
            return jsonify(result), code

        @app.route("/approvals/<approval_id>/approve-session", methods=["POST"])
        def approve_session(approval_id: str):
            result, code = _get_store_result(approval_id, "approve_session")
            if code == 200:
                return render_template("result.html", message="Approved (session)", success=True)
            return jsonify(result), code

        @app.route("/approvals/<approval_id>/reject", methods=["POST"])
        def reject_approval(approval_id: str):
            result, code = _get_store_result(approval_id, "reject")
            if code == 200:
                return render_template("result.html", message="Rejected", success=False)
            return jsonify(result), code

        @app.route("/approvals/<approval_id>/reject-remember", methods=["POST"])
        def reject_remember(approval_id: str):
            result, code = _get_store_result(approval_id, "reject_remember")
            if code == 200:
                return render_template("result.html", message="Rejected — capability permanently blocked", success=False)
            return jsonify(result), code

        # Health check
        @app.route("/health")
        def health():
            return jsonify({"status": "ok"})

    @staticmethod
    def _mask_payload(payload: str) -> str:
        """Mask sensitive values in payload preview."""
        import re
        patterns = [
            (r'(password|passwd|secret|token|api_key|apikey)\s*[=:]\s*"[^"]*"', r'\1="[REDACTED]"'),
            (r'(password|passwd|secret|token|api_key|apikey)\s*[=:]\s*[^\s,;]+', r'\1=[REDACTED]'),
        ]
        for pattern, replacement in patterns:
            payload = re.sub(pattern, replacement, payload, flags=re.IGNORECASE)
        return payload


def create_app(approval_store: ApprovalStore) -> ApprovalWebApp:
    """Factory function to create an ApprovalWebApp."""
    return ApprovalWebApp(approval_store)
