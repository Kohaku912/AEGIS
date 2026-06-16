"""Session Management — manages conversation sessions and history."""

from __future__ import annotations

import time
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any

from aegis_ai.interaction.message import Message, Response


@dataclass
class Session:
    """A conversation session."""
    session_id: str = ""
    user_id: str = "local_user"
    channel: str = "web_chat"
    created_at_ms: int = 0
    last_active_ms: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)
    pending_approvals: list[str] = field(default_factory=list)
    paused_tasks: list[str] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """Manages conversation sessions.

    Usage:
        manager = SessionManager()
        session = manager.get_or_create("user-1", "web_chat")
        manager.add_message(session.session_id, message)
        history = manager.get_history(session.session_id)
    """

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = threading.RLock()

    def get_or_create(self, user_id: str, channel: str) -> Session:
        """Get or create a session for a user/channel."""
        with self._lock:
            # Find existing active session
            for session in self._sessions.values():
                if session.user_id == user_id and session.channel == channel:
                    # Check if session is still active (within 1 hour)
                    if time.time() * 1000 - session.last_active_ms < 3600000:
                        return session

            # Create new session
            session = Session(
                session_id=f"sess_{uuid.uuid4().hex[:12]}",
                user_id=user_id,
                channel=channel,
                created_at_ms=int(time.time() * 1000),
                last_active_ms=int(time.time() * 1000),
            )
            self._sessions[session.session_id] = session
            return session

    def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID."""
        with self._lock:
            return self._sessions.get(session_id)

    def add_message(self, session_id: str, message: Message) -> None:
        """Add a message to session history."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.history.append({
                    "role": "user",
                    "text": message.text,
                    "timestamp_ms": message.timestamp_ms,
                    "channel": message.channel.name,
                })
                session.last_active_ms = int(time.time() * 1000)

    def add_response(self, session_id: str, response: Response) -> None:
        """Add a response to session history."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.history.append({
                    "role": "aegis",
                    "text": response.text,
                    "timestamp_ms": response.timestamp_ms,
                    "sources": response.sources,
                })
                session.last_active_ms = int(time.time() * 1000)

    def get_history(self, session_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent conversation history."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return []
            return list(session.history[-limit:])

    def list_sessions(self, user_id: str | None = None) -> list[Session]:
        """List all sessions, optionally filtered by user."""
        with self._lock:
            sessions = list(self._sessions.values())
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        return sessions
