"""Tests for Interaction Hub — message, intent, session, router."""

from __future__ import annotations

import time

from aegis_ai.interaction.intent import Intent, classify_intent
from aegis_ai.interaction.message import Channel, Message, Response
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.interaction.session import SessionManager

# ═══════════════════════════════════════════════════════════════
# 1. Intent Classification
# ═══════════════════════════════════════════════════════════════


class TestIntentClassification:
    """Intent classification works correctly."""

    def test_research_intent(self):
        """Research keywords classify as RESEARCH_REQUEST."""
        assert classify_intent("research Python 3.12") == Intent.RESEARCH_REQUEST
        assert classify_intent("search for AI news") == Intent.RESEARCH_REQUEST
        assert classify_intent("tell me about quantum computing") == Intent.RESEARCH_REQUEST

    def test_settings_intent(self):
        """Settings keywords classify as SETTINGS_REQUEST."""
        assert classify_intent("show settings") == Intent.SETTINGS_REQUEST
        assert classify_intent("enable support agent") == Intent.SETTINGS_REQUEST

    def test_approval_intent(self):
        """Approval keywords classify as APPROVAL_DECISION."""
        assert classify_intent("approve this") == Intent.APPROVAL_DECISION
        assert classify_intent("reject the request") == Intent.APPROVAL_DECISION

    def test_status_intent(self):
        """Status keywords classify as STATUS_CHECK."""
        assert classify_intent("what's the status") == Intent.STATUS_CHECK
        assert classify_intent("server status") == Intent.STATUS_CHECK

    def test_help_intent(self):
        """Help keywords classify as HELP_REQUEST."""
        assert classify_intent("help") == Intent.HELP_REQUEST
        assert classify_intent("what can you do") == Intent.HELP_REQUEST

    def test_unknown_intent(self):
        """Unknown text classifies as UNKNOWN."""
        assert classify_intent("asdfghjkl") == Intent.UNKNOWN
        assert classify_intent("") == Intent.UNKNOWN


# ═══════════════════════════════════════════════════════════════
# 2. Session Management
# ═══════════════════════════════════════════════════════════════


class TestSessionManager:
    """Session manager handles sessions correctly."""

    def test_create_session(self):
        """Session is created for new user."""
        manager = SessionManager()
        session = manager.get_or_create("user-1", "web_chat")
        assert session.session_id != ""
        assert session.user_id == "user-1"

    def test_reuse_active_session(self):
        """Active session is reused."""
        manager = SessionManager()
        s1 = manager.get_or_create("user-1", "web_chat")
        s2 = manager.get_or_create("user-1", "web_chat")
        assert s1.session_id == s2.session_id

    def test_different_channel_new_session(self):
        """Different channel creates new session."""
        manager = SessionManager()
        s1 = manager.get_or_create("user-1", "web_chat")
        s2 = manager.get_or_create("user-1", "cli")
        assert s1.session_id != s2.session_id

    def test_add_message_to_history(self):
        """Messages are added to session history."""
        manager = SessionManager()
        session = manager.get_or_create("user-1", "web_chat")

        msg = Message(text="Hello", timestamp_ms=int(time.time() * 1000))
        manager.add_message(session.session_id, msg)

        history = manager.get_history(session.session_id)
        assert len(history) == 1
        assert history[0]["text"] == "Hello"

    def test_add_response_to_history(self):
        """Responses are added to session history."""
        manager = SessionManager()
        session = manager.get_or_create("user-1", "web_chat")

        resp = Response(text="Hi there!", timestamp_ms=int(time.time() * 1000))
        manager.add_response(session.session_id, resp)

        history = manager.get_history(session.session_id)
        assert len(history) == 1
        assert history[0]["role"] == "aegis"


# ═══════════════════════════════════════════════════════════════
# 3. Interaction Router
# ═══════════════════════════════════════════════════════════════


class TestInteractionRouter:
    """Router routes messages to correct handlers."""

    def test_research_request(self):
        """Research request is handled."""
        router = InteractionRouter()
        msg = Message(text="research Python 3.12", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)
        assert response.text != ""

    def test_settings_request(self):
        """Settings request returns settings info."""
        router = InteractionRouter()
        msg = Message(text="show settings", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)
        assert "settings" in response.text.lower() or "dashboard" in response.text.lower()

    def test_help_request(self):
        """Help request returns help text."""
        router = InteractionRouter()
        msg = Message(text="help", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)
        assert "research" in response.text.lower() or "help" in response.text.lower()

    def test_status_request(self):
        """Status request returns status info."""
        router = InteractionRouter()
        msg = Message(text="status", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)
        assert "dashboard" in response.text.lower() or "status" in response.text.lower()

    def test_unknown_request(self):
        """Unknown request returns clarification."""
        router = InteractionRouter()
        msg = Message(text="asdfghjkl", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)
        assert "rephrase" in response.text.lower() or "not sure" in response.text.lower()

    def test_tool_request_routed_to_approval(self):
        """Tool requests are routed to approval UI."""
        router = InteractionRouter()
        msg = Message(text="screenshot the screen", timestamp_ms=int(time.time() * 1000))
        response = router.route(msg)
        assert "approval" in response.text.lower() or "tool" in response.text.lower()


# ═══════════════════════════════════════════════════════════════
# 4. Message Model
# ═══════════════════════════════════════════════════════════════


class TestMessageModel:
    """Message model has correct fields."""

    def test_message_creation(self):
        """Message can be created with all fields."""
        msg = Message(
            message_id="msg_001",
            channel=Channel.WEB_CHAT,
            user_id="user-1",
            session_id="sess-1",
            text="Hello",
            timestamp_ms=int(time.time() * 1000),
        )
        assert msg.message_id == "msg_001"
        assert msg.channel == Channel.WEB_CHAT
        assert msg.text == "Hello"

    def test_response_creation(self):
        """Response can be created with all fields."""
        resp = Response(
            response_id="resp_001",
            message_id="msg_001",
            text="Hi!",
            timestamp_ms=int(time.time() * 1000),
        )
        assert resp.response_id == "resp_001"
        assert resp.text == "Hi!"
