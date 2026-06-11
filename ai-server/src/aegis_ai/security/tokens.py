"""Token management — generation, validation, rotation for AEGIS security."""

from __future__ import annotations

import json
import secrets
import threading
import time
from pathlib import Path
from typing import Any


class TokenStore:
    """Manages authentication tokens with persistence.

    Usage:
        store = TokenStore(path="data/tokens.json")
        token = store.get_or_create_token("server-id")
        store.rotate_token("server-id")
    """

    def __init__(self, path: str = "data/tokens.json") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._tokens: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._load()

    def get_or_create_token(self, server_id: str) -> str:
        """Get existing token or create new one for a server."""
        with self._lock:
            if server_id in self._tokens:
                return self._tokens[server_id]["token"]

            token = secrets.token_hex(32)
            self._tokens[server_id] = {
                "token": token,
                "created_at_ms": int(time.time() * 1000),
                "rotated_at_ms": 0,
            }
            self._persist()
            return token

    def rotate_token(self, server_id: str) -> str:
        """Rotate (replace) a server's token."""
        with self._lock:
            new_token = secrets.token_hex(32)
            self._tokens[server_id] = {
                "token": new_token,
                "created_at_ms": self._tokens.get(server_id, {}).get("created_at_ms", int(time.time() * 1000)),
                "rotated_at_ms": int(time.time() * 1000),
            }
            self._persist()
            return new_token

    def validate_token(self, server_id: str, token: str) -> bool:
        """Validate a server's token."""
        with self._lock:
            entry = self._tokens.get(server_id)
            if not entry:
                return False
            return entry["token"] == token

    def remove_token(self, server_id: str) -> None:
        """Remove a server's token."""
        with self._lock:
            self._tokens.pop(server_id, None)
            self._persist()

    def _persist(self) -> None:
        """Persist tokens to disk."""
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._tokens, f, indent=2)

    def _load(self) -> None:
        """Load tokens from disk."""
        if not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                self._tokens = json.load(f)
        except (json.JSONDecodeError, Exception):
            self._tokens = {}
