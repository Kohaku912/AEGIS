"""Interaction Hub — unified user interaction across channels.

Provides:
- Message: Unified message model
- SessionManager: Conversation session management
- InteractionRouter: Intent classification and routing
- CLIChannel: Command-line interface
- Intent: Intent classification
"""

from aegis_ai.interaction.channels.cli import CLIChannel  # noqa: F401
from aegis_ai.interaction.message import Channel, Message, PrivacyLevel, Response  # noqa: F401
from aegis_ai.interaction.router import InteractionRouter  # noqa: F401
from aegis_ai.interaction.session import Session, SessionManager  # noqa: F401

try:
    from aegis_ai.interaction.intent import Intent, classify_intent  # noqa: F401
except ImportError:
    Intent = None  # type: ignore[assignment]

    def classify_intent(*args, **kwargs):  # type: ignore[override]
        raise ImportError("aegis_ai.interaction.intent is unavailable")
