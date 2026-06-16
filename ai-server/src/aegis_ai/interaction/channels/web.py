"""Web Chat Channel — Flask routes for web-based chat interface."""

from __future__ import annotations

import logging
import time
import uuid

from flask import Flask, jsonify, render_template, request

from aegis_ai.interaction.message import Channel, Message
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.interaction.session import SessionManager

logger = logging.getLogger("aegis_ai.interaction.web")


class WebChatApp:
    """Flask-based web chat UI for AEGIS.

    Provides:
    - GET  /chat              → Chat interface
    - POST /chat/send         → Send message
    - GET  /chat/history      → Get conversation history
    - GET  /chat/sessions     → List sessions

    Security: localhost only by default.
    """

    def __init__(
        self,
        router: InteractionRouter,
        session_manager: SessionManager | None = None,
    ) -> None:
        self._router = router
        self._sessions = session_manager or SessionManager()
        self._app = Flask(__name__, template_folder="templates")
        self._setup_routes()

    @property
    def app(self) -> Flask:
        return self._app

    def run(self, host: str = "0.0.0.0", port: int = 8091, debug: bool = False) -> None:
        """Run the chat server (localhost only)."""
        self._app.run(host=host, port=port, debug=debug)

    def _setup_routes(self) -> None:
        app = self._app

        @app.route("/chat")
        def chat_page():
            return render_template("chat.html")

        @app.route("/chat/send", methods=["POST"])
        def send_message():
            data = request.get_json(silent=True) or {}
            text = data.get("text", "").strip()
            user_id = data.get("user_id", "local_user")
            session_id = data.get("session_id", "")

            if not text:
                return jsonify({"error": "No text provided"}), 400

            # Get or create session
            session = self._sessions.get_or_create(user_id, "web_chat")
            if session_id:
                existing = self._sessions.get_session(session_id)
                if existing:
                    session = existing

            # Create message
            message = Message(
                message_id=f"msg_{uuid.uuid4().hex[:8]}",
                channel=Channel.WEB_CHAT,
                user_id=user_id,
                session_id=session.session_id,
                text=text,
                timestamp_ms=int(time.time() * 1000),
            )

            # Add to session
            self._sessions.add_message(session.session_id, message)

            # Route to appropriate handler
            response = self._router.route(message)

            # Add response to session
            self._sessions.add_response(session.session_id, response)

            return jsonify({
                "response_id": response.response_id,
                "text": response.text,
                "sources": response.sources,
                "pending_approvals": response.pending_approvals,
                "session_id": session.session_id,
            })

        @app.route("/chat/history")
        def get_history():
            session_id = request.args.get("session_id", "")
            if not session_id:
                return jsonify({"error": "session_id required"}), 400

            history = self._sessions.get_history(session_id)
            return jsonify({"session_id": session_id, "history": history})

        @app.route("/chat/sessions")
        def list_sessions():
            user_id = request.args.get("user_id", "")
            sessions = self._sessions.list_sessions(user_id or None)
            return jsonify({
                "sessions": [
                    {
                        "session_id": s.session_id,
                        "user_id": s.user_id,
                        "channel": s.channel,
                        "last_active_ms": s.last_active_ms,
                        "message_count": len(s.history),
                    }
                    for s in sessions
                ]
            })

        @app.route("/health")
        def health():
            return jsonify({"status": "ok", "component": "chat"})
