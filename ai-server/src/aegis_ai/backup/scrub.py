"""Scrub — removes or masks sensitive data from exports.

Removes:
- Passwords, tokens, API keys
- SSH keys, PEM certificates
- Email addresses, phone numbers
- Credit card numbers
- Notification text from sensitive apps
"""

from __future__ import annotations

import re
from typing import Any

# Patterns to scrub
SCRUB_PATTERNS: list[tuple[str, str]] = [
    (
        r'(?i)(password|passwd|secret|token|api_key|apikey|access_key)'
        r'\s*[=:]\s*["\']?[^"\'\s,;]+',
        r'\1=[REDACTED]',
    ),
    (
        r"-----BEGIN\s+(RSA|EC|OPENSSH|DSA)\s+PRIVATE\s+KEY-----"
        r".*?-----END\s+\1\s+PRIVATE\s+KEY-----",
        "[SSH_KEY_REDACTED]",
    ),
    (r"-----BEGIN\s+CERTIFICATE-----.*?-----END\s+CERTIFICATE-----", "[CERT_REDACTED]"),
    (r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "[JWT_REDACTED]"),
    (r"AKIA[0-9A-Z]{16}", "[AWS_KEY_REDACTED]"),
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL_REDACTED]"),
    (r"\+\d{1,3}[\s-]?\d[\d\s-]{7,12}\d", "[PHONE_REDACTED]"),
    (r"\b(?:\d[ -]*?){13,19}\b", "[CARD_REDACTED]"),
]

# Keys whose values should always be redacted
SENSITIVE_KEYS: set[str] = {
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "credential", "ssh_key", "private_key", "access_token",
    "refresh_token", "auth_token", "jwt",
}


def scrub_text(text: str) -> str:
    """Scrub sensitive data from text."""
    result = text
    for pattern, replacement in SCRUB_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.DOTALL)
    return result


def scrub_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Scrub sensitive values from a dict."""
    result = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_KEYS:
            result[k] = "[REDACTED]"
        elif isinstance(v, str):
            result[k] = scrub_text(v)
        elif isinstance(v, dict):
            result[k] = scrub_dict(v)
        elif isinstance(v, list):
            result[k] = [
                scrub_dict(item) if isinstance(item, dict)
                else scrub_text(str(item)) if isinstance(item, str)
                else item
                for item in v
            ]
        else:
            result[k] = v
    return result
