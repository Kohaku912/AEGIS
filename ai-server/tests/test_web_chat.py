"""Tests for Web Chat — Flask chat routes."""

from __future__ import annotations

import json

from aegis_ai.interaction.channels.web import WebChatApp
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.interaction.session import SessionManager


def _setup_chat() -> tuple[WebChatApp, SessionManager]:
    """Set up web chat app with router."""
    router = InteractionRouter()
    sessions = SessionManager()
    app = WebChatApp(router=router, session_manager=sessions)
    return app, sessions


class TestWebChatRoutes:
    """Web chat routes work correctly."""

    def test_chat_page(self):
        """Chat page returns 200."""
        app, _ = _setup_chat()
        with app.app.test_client() as client:
            resp = client.get("/chat")
            assert resp.status_code == 200

    def test_send_message(self):
        """Send message returns response."""
        app, _ = _setup_chat()
        with app.app.test_client() as client:
            resp = client.post("/chat/send", json={"text": "help"})
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert "text" in data
            assert data["text"] != ""

    def test_send_empty_message(self):
        """Empty message returns 400."""
        app, _ = _setup_chat()
        with app.app.test_client() as client:
            resp = client.post("/chat/send", json={"text": ""})
            assert resp.status_code == 400

    def test_send_research_request(self):
        """Research request gets research response."""
        app, _ = _setup_chat()
        with app.app.test_client() as client:
            resp = client.post("/chat/send", json={"text": "research Python 3.12"})
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert data["text"] != ""

    def test_get_history(self):
        """History returns conversation history."""
        app, sessions = _setup_chat()
        with app.app.test_client() as client:
            # Send a message first
            resp = client.post("/chat/send", json={"text": "hello"})
            data = json.loads(resp.data)
            session_id = data["session_id"]

            # Get history
            resp2 = client.get(f"/chat/history?session_id={session_id}")
            assert resp2.status_code == 200
            history = json.loads(resp2.data)
            assert len(history["history"]) >= 2  # user message + response

    def test_list_sessions(self):
        """Sessions list returns sessions."""
        app, _ = _setup_chat()
        with app.app.test_client() as client:
            # Create a session
            client.post("/chat/send", json={"text": "hello"})

            # List sessions
            resp = client.get("/chat/sessions")
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert len(data["sessions"]) >= 1

    def test_health(self):
        """Health endpoint returns ok."""
        app, _ = _setup_chat()
        with app.app.test_client() as client:
            resp = client.get("/health")
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert data["status"] == "ok"
