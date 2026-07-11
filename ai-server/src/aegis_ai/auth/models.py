"""Persistent auth models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AuthUser:
    user_id: str
    username: str
    display_name: str
    role: str = "admin"
    created_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PasskeyCredential:
    credential_id: str
    user_id: str
    public_key: str
    sign_count: int = 0
    nickname: str = ""
    aaguid: str = ""
    device_type: str = ""
    backed_up: bool = False
    created_at: int = 0
    last_used_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuthChallenge:
    challenge_id: str
    challenge: str
    kind: str
    user_id: str = ""
    username: str = ""
    display_name: str = ""
    created_at: int = 0
    expires_at: int = 0
    bootstrap: bool = False
    used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuthSession:
    session_id: str
    user_id: str
    created_at: int
    expires_at: int
    last_seen_at: int
    last_auth_at: int
    csrf_token: str
    user_agent: str = ""
    ip_address: str = ""
    revoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuthEvent:
    event_id: str
    event_type: str
    created_at: int
    user_id: str = ""
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
