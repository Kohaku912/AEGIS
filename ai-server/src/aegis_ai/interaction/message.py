"""Unified Message Model — defines messages across all interaction channels."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class Channel(Enum):
    """Interaction channels."""
    WEB_CHAT = auto()
    CLI = auto()
    LINE = auto()       # Stub only
    DISCORD = auto()    # Stub only
    VOICE = auto()      # Stub only


class PrivacyLevel(Enum):
    """Privacy level for messages."""
    PUBLIC = auto()
    INTERNAL = auto()
    SENSITIVE = auto()
    LOCAL_ONLY = auto()


@dataclass
class Message:
    """Unified message model across all channels."""
    message_id: str = ""
    channel: Channel = Channel.WEB_CHAT
    user_id: str = "local_user"
    session_id: str = ""
    text: str = ""
    attachments: list[dict[str, Any]] = field(default_factory=list)
    timestamp_ms: int = 0
    privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL
    source_context: str = ""  # e.g. "dashboard", "approval_ui", "cli"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Response:
    """Response from AEGIS to the user."""
    response_id: str = ""
    message_id: str = ""  # Original message ID
    text: str = ""
    sources: list[dict[str, Any]] = field(default_factory=list)
    pending_approvals: list[dict[str, Any]] = field(default_factory=list)
    task_status: dict[str, Any] = field(default_factory=dict)
    memory_notes: list[str] = field(default_factory=list)
    channel: Channel = Channel.WEB_CHAT
    timestamp_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
