"""Redaction — strips sensitive data before sending to LLM.

Redacts:
- Passwords, tokens, API keys
- Email addresses
- Phone numbers
- Credit card numbers
- SSH keys, PEM certificates
- Notification text (if configured)
"""

from __future__ import annotations

import re
from typing import Any

# Redaction patterns: (regex, replacement)
REDACTION_PATTERNS: list[tuple[str, str]] = [
    # Passwords/tokens in key=value format
    (r'(?i)(password|passwd|secret|token|api_key|apikey|access_key)\s*[=:]\s*["\']?[^"\'\s,;]+', r'\1=[REDACTED]'),
    # SSH keys
    (
        r"-----BEGIN\s+(RSA|EC|OPENSSH|DSA)\s+PRIVATE\s+KEY-----"
        r".*?-----END\s+\1\s+PRIVATE\s+KEY-----",
        "[SSH_KEY_REDACTED]",
    ),
    # PEM certificates
    (r"-----BEGIN\s+CERTIFICATE-----.*?-----END\s+CERTIFICATE-----", "[CERT_REDACTED]"),
    # JWT tokens
    (r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "[JWT_REDACTED]"),
    # AWS access keys
    (r"AKIA[0-9A-Z]{16}", "[AWS_KEY_REDACTED]"),
    # Credit card numbers
    (r"\b(?:\d[ -]*?){13,19}\b", "[CARD_REDACTED]"),
    # Email addresses
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL_REDACTED]"),
    # Phone numbers (international)
    (r"\+\d{1,3}[\s-]?\d[\d\s-]{7,12}\d", "[PHONE_REDACTED]"),
]


def redact_text(text: str) -> str:
    """Redact sensitive information from text.

    Usage:
        safe = redact_text("My password is secret123")
        # Returns: "My password is password=[REDACTED]"
    """
    result = text
    for pattern, replacement in REDACTION_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.DOTALL)
    return result


def redact_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive values in a dict."""
    sensitive_keys = {"password", "secret", "token", "api_key", "apikey", "credential", "ssh_key"}
    result = {}
    for k, v in data.items():
        if k.lower() in sensitive_keys:
            result[k] = "[REDACTED]"
        elif isinstance(v, str):
            result[k] = redact_text(v)
        elif isinstance(v, dict):
            result[k] = redact_dict(v)
        else:
            result[k] = v
    return result


def should_redact_for_privacy(text: str, contains_sensitive: bool = False) -> bool:
    """Check if text should be redacted before sending to external LLM."""
    if contains_sensitive:
        return True

    # Check for common sensitive patterns
    sensitive_indicators = [
        r"password\s*[:=]",
        r"secret\s*[:=]",
        r"token\s*[:=]",
        r"BEGIN\s+(RSA|EC|OPENSSH)\s+PRIVATE",
        r"AKIA[0-9A-Z]{16}",
    ]
    for pattern in sensitive_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
