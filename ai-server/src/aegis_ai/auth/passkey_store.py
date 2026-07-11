"""JSON-backed passkey auth store."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

from aegis_ai.auth.models import AuthChallenge, AuthEvent, AuthSession, AuthUser, PasskeyCredential


def now_ms() -> int:
    return int(time.time() * 1000)


class PasskeyStore:
    """Persist users, passkeys, challenges, sessions, and auth events."""

    def __init__(self, data_dir: str | Path = "data/auth") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.data_dir / "auth.json"
        self._lock = threading.RLock()
        self.users: dict[str, AuthUser] = {}
        self.credentials: dict[str, PasskeyCredential] = {}
        self.challenges: dict[str, AuthChallenge] = {}
        self.sessions: dict[str, AuthSession] = {}
        self.events: list[AuthEvent] = []
        self._load()

    def has_users(self) -> bool:
        with self._lock:
            return bool(self.users)

    def add_user(self, user: AuthUser) -> None:
        with self._lock:
            self.users[user.user_id] = user
            self._save()

    def get_user(self, user_id: str) -> AuthUser | None:
        with self._lock:
            return self.users.get(user_id)

    def get_user_by_name(self, username: str) -> AuthUser | None:
        normalized = username.strip().lower()
        with self._lock:
            for user in self.users.values():
                if user.username.lower() == normalized:
                    return user
        return None

    def list_users(self) -> list[AuthUser]:
        with self._lock:
            return list(self.users.values())

    def add_credential(self, credential: PasskeyCredential) -> None:
        with self._lock:
            self.credentials[credential.credential_id] = credential
            self._save()

    def get_credential(self, credential_id: str) -> PasskeyCredential | None:
        with self._lock:
            return self.credentials.get(credential_id)

    def list_credentials(self, user_id: str = "") -> list[PasskeyCredential]:
        with self._lock:
            values = list(self.credentials.values())
        if user_id:
            values = [item for item in values if item.user_id == user_id]
        values.sort(key=lambda item: item.created_at, reverse=True)
        return values

    def update_credential(self, credential: PasskeyCredential) -> None:
        with self._lock:
            self.credentials[credential.credential_id] = credential
            self._save()

    def delete_credential(self, credential_id: str, user_id: str) -> bool:
        with self._lock:
            credential = self.credentials.get(credential_id)
            if credential is None or credential.user_id != user_id:
                return False
            del self.credentials[credential_id]
            self._save()
            return True

    def add_challenge(self, challenge: AuthChallenge) -> None:
        with self._lock:
            self._cleanup_locked()
            self.challenges[challenge.challenge_id] = challenge
            self._save()

    def consume_challenge(self, challenge_id: str, kind: str) -> AuthChallenge | None:
        with self._lock:
            self._cleanup_locked()
            challenge = self.challenges.get(challenge_id)
            if challenge is None or challenge.kind != kind or challenge.used or challenge.expires_at < now_ms():
                return None
            challenge.used = True
            del self.challenges[challenge_id]
            self._save()
            return challenge

    def add_session(self, session: AuthSession) -> None:
        with self._lock:
            self._cleanup_locked()
            self.sessions[session.session_id] = session
            self._save()

    def get_session(self, session_id: str) -> AuthSession | None:
        with self._lock:
            self._cleanup_locked()
            session = self.sessions.get(session_id)
            if session is None or session.revoked:
                return None
            return session

    def update_session(self, session: AuthSession) -> None:
        with self._lock:
            self.sessions[session.session_id] = session
            self._save()

    def revoke_session(self, session_id: str) -> None:
        with self._lock:
            session = self.sessions.get(session_id)
            if session is not None:
                session.revoked = True
                self._save()

    def add_event(self, event: AuthEvent) -> None:
        with self._lock:
            self.events.append(event)
            self.events = self.events[-1000:]
            self._save()

    def _cleanup_locked(self) -> None:
        now = now_ms()
        self.challenges = {
            key: value for key, value in self.challenges.items() if not value.used and value.expires_at >= now
        }
        self.sessions = {
            key: value for key, value in self.sessions.items() if not value.revoked and value.expires_at >= now
        }

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.users = {k: AuthUser(**v) for k, v in (data.get("users") or {}).items()}
            self.credentials = {
                k: PasskeyCredential(**v) for k, v in (data.get("credentials") or {}).items()
            }
            self.challenges = {k: AuthChallenge(**v) for k, v in (data.get("challenges") or {}).items()}
            self.sessions = {k: AuthSession(**v) for k, v in (data.get("sessions") or {}).items()}
            self.events = [AuthEvent(**v) for v in (data.get("events") or [])]
        except Exception:
            corrupt = self.path.with_suffix(f".corrupt-{now_ms()}.json")
            self.path.replace(corrupt)

    def _save(self) -> None:
        data: dict[str, Any] = {
            "users": {key: value.to_dict() for key, value in self.users.items()},
            "credentials": {key: value.to_dict() for key, value in self.credentials.items()},
            "challenges": {key: value.to_dict() for key, value in self.challenges.items()},
            "sessions": {key: value.to_dict() for key, value in self.sessions.items()},
            "events": [event.to_dict() for event in self.events[-1000:]],
            "saved_at": now_ms(),
        }
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)
