"""Redaction utilities — prevent sensitive data leakage in logs."""

from __future__ import annotations

import re

# Patterns to redact from logs and payloads
_REDACT_PATTERNS: list[tuple[str, str]] = [
    (r"Authorization:\s*[^\n]+", "Authorization: [REDACTED]"),
    (r"Set-Cookie:\s*[^\n]+", "Set-Cookie: [REDACTED]"),
    (r"Cookie:\s*[^\n]+", "Cookie: [REDACTED]"),
    (r"api[_-]?key[=:]\s*[^\s,;\n]+", "api_key=[REDACTED]"),
    (r"token[=:]\s*[^\s,;\n]+", "token=[REDACTED]"),
    (r"secret[=:]\s*[^\s,;\n]+", "secret=[REDACTED]"),
    (r"password[=:]\s*[^\s,;\n]+", "password=[REDACTED]"),
    (r'"[^"]*token[^"]*"\s*:\s*"[^"]+"', '"token":"[REDACTED]"'),
]

_REDACTED: list[re.Pattern] = [(re.compile(p, re.IGNORECASE), r) for p, r in _REDACT_PATTERNS]


def redact(text: str) -> str:
    """Redact sensitive information from a string."""
    for pattern, replacement in _REDACTED:
        text = pattern.sub(replacement, text)
    return text


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Redact sensitive headers."""
    sensitive = {"authorization", "cookie", "set-cookie", "x-api-key"}
    return {k: "[REDACTED]" if k.lower() in sensitive else v for k, v in headers.items()}
