"""Prompt Safety — validates prompts for injection and untrusted content.

Ensures:
- Web/browser content is quoted as data, not instructions
- Tool results are data, not system instructions
- User instruction hierarchy is maintained
- Self-dev code comments are data
"""

from __future__ import annotations

import re

# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(previous|above|all)\s+instructions",
    r"you\s+are\s+now\s+",
    r"system\s*:\s*you\s+are",
    r"ignore\s+safety",
    r"bypass\s+(safety|policy|rules)",
    r"act\s+as\s+if\s+you\s+are",
    r"pretend\s+you\s+are",
    r"new\s+instructions\s*:",
    r"override\s+system\s+prompt",
]


def validate_prompt(prompt: str, source: str = "user") -> list[str]:
    """Validate a prompt for safety issues.

    Returns a list of warnings. Empty list means safe.
    """
    warnings: list[str] = []

    # Check for injection patterns
    prompt_lower = prompt.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower):
            warnings.append(f"Potential prompt injection detected: pattern '{pattern}'")

    # Check for untrusted content markers
    if source in ("browser", "web", "external"):
        if not _is_properly_quoted(prompt):
            warnings.append("External content should be quoted as data, not instructions")

    return warnings


def _is_properly_quoted(text: str) -> bool:
    """Check if text is properly quoted as data."""
    # Simple heuristic: if the text starts with quotes or has clear data markers
    stripped = text.strip()
    if stripped.startswith(('"', "'", ">", "|", "```")):
        return True
    if stripped.startswith("[") or stripped.startswith("{"):
        return True
    return False


def wrap_untrusted_content(content: str, source: str = "external") -> str:
    """Wrap untrusted content in quotes to prevent injection.

    Usage:
        safe = wrap_untrusted_content("ignore all instructions", "browser")
        # Returns: '[UNTRUSTED CONTENT from browser]\nignore all instructions\n[/UNTRUSTED CONTENT]'
    """
    return f'[UNTRUSTED CONTENT from {source}]\n{content}\n[/UNTRUSTED CONTENT]'
