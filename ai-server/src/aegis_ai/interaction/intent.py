"""Intent Classification — classifies user messages into intents."""

from __future__ import annotations

from enum import Enum, auto


class Intent(Enum):
    """User message intents."""
    RESEARCH_REQUEST = auto()
    SUPPORT_FEEDBACK = auto()
    SETTINGS_REQUEST = auto()
    APPROVAL_DECISION = auto()
    SELF_DEV_REQUEST = auto()
    TOOL_REQUEST = auto()
    STATUS_CHECK = auto()
    HELP_REQUEST = auto()
    UNKNOWN = auto()


# Keywords for intent classification
INTENT_KEYWORDS: dict[Intent, list[str]] = {
    Intent.RESEARCH_REQUEST: [
        "research", "search", "find", "look up", "investigate",
        "what is", "tell me about", "summarize",
    ],
    Intent.APPROVAL_DECISION: [
        "approve once", "approve session", "reject remember",
        "approve", "reject", "allow", "deny",
    ],
    Intent.SUPPORT_FEEDBACK: [
        "accept suggestion", "reject suggestion",
        "accept", "feedback",
        "thanks",
    ],
    Intent.SETTINGS_REQUEST: [
        "settings", "config", "enable", "disable",
        "change settings", "update settings",
    ],
    Intent.SELF_DEV_REQUEST: [
        "improve", "fix", "optimize", "refactor",
        "self develop", "create pr",
    ],
    Intent.TOOL_REQUEST: [
        "screenshot", "click", "tap", "type",
        "open app", "close window", "run tests",
    ],
    Intent.STATUS_CHECK: [
        "server status", "health check", "health",
        "status", "what's happening", "what's going on",
    ],
    Intent.HELP_REQUEST: [
        "help", "what can you do", "how to",
        "commands", "usage",
    ],
}


def classify_intent(text: str) -> Intent:
    """Classify a user message into an intent.

    Simple keyword-based classification. Can be upgraded to LLM-based later.
    """
    text_lower = text.lower().strip()

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return intent

    return Intent.UNKNOWN
