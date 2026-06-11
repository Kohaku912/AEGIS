"""Logging configuration for Browser Server."""

from __future__ import annotations

import logging
import sys

from aegis_browser.redaction import redact


class RedactingFormatter(logging.Formatter):
    """Logging formatter that redacts sensitive data."""

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        return redact(msg)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RedactingFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), handlers=[handler])
