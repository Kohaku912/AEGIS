"""Session — browser session management for browser-use agent.

Manages browser profiles, cookies, and session state.
Sessions can be persisted to Docker volumes.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_browser.session")


@dataclass
class SessionState:
    """Current browser session state."""
    session_id: str = ""
    created_at_ms: int = 0
    last_active_ms: int = 0
    pages_visited: list[str] = field(default_factory=list)
    cookies_count: int = 0
    local_storage_keys: list[str] = field(default_factory=list)


class BrowserSession:
    """Manages browser sessions and profiles.

    Usage:
        session = BrowserSession(session_id="user_1", profile_dir="/app/profiles/user_1")
        session.save_cookies()
        session.clear_cookies()
    """

    def __init__(
        self,
        session_id: str = "default",
        profile_dir: str = "/app/browser-profiles",
        session_dir: str = "/app/browser-sessions",
    ) -> None:
        self._session_id = session_id
        self._profile_dir = Path(profile_dir) / session_id
        self._session_dir = Path(session_dir)
        self._state = SessionState(
            session_id=session_id,
            created_at_ms=int(time.time() * 1000),
            last_active_ms=int(time.time() * 1000),
        )

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def profile_dir(self) -> Path:
        return self._profile_dir

    def ensure_dirs(self) -> None:
        """Ensure profile and session directories exist."""
        self._profile_dir.mkdir(parents=True, exist_ok=True)
        self._session_dir.mkdir(parents=True, exist_ok=True)

    def save_state(self) -> None:
        """Save session state to disk."""
        self.ensure_dirs()
        state_file = self._session_dir / f"{self._session_id}.json"
        data = {
            "session_id": self._state.session_id,
            "created_at_ms": self._state.created_at_ms,
            "last_active_ms": self._state.last_active_ms,
            "pages_visited": self._state.pages_visited[-100:],  # Keep last 100
            "cookies_count": self._state.cookies_count,
        }
        state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_state(self) -> bool:
        """Load session state from disk."""
        state_file = self._session_dir / f"{self._session_id}.json"
        if not state_file.exists():
            return False

        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            self._state.session_id = data.get("session_id", self._session_id)
            self._state.created_at_ms = data.get("created_at_ms", 0)
            self._state.last_active_ms = data.get("last_active_ms", 0)
            self._state.pages_visited = data.get("pages_visited", [])
            self._state.cookies_count = data.get("cookies_count", 0)
            return True
        except Exception as e:
            logger.warning("Failed to load session state: %s", e)
            return False

    def record_page_visit(self, url: str) -> None:
        """Record a page visit."""
        self._state.pages_visited.append(url)
        self._state.last_active_ms = int(time.time() * 1000)

    def get_state(self) -> SessionState:
        """Get current session state."""
        return self._state

    def clear_cookies(self) -> bool:
        """Clear cookies for this session."""
        cookies_file = self._profile_dir / "cookies.json"
        if cookies_file.exists():
            cookies_file.unlink()
            logger.info("Cookies cleared for session %s", self._session_id)
            return True
        return False

    def clear_all(self) -> bool:
        """Clear all session data (cookies, local storage, etc.)."""
        import shutil
        if self._profile_dir.exists():
            shutil.rmtree(self._profile_dir)
            self._profile_dir.mkdir(parents=True, exist_ok=True)
            logger.info("All session data cleared for %s", self._session_id)
            return True
        return False

    def get_storage_info(self) -> dict[str, Any]:
        """Get storage information."""
        profile_size = 0
        if self._profile_dir.exists():
            profile_size = sum(f.stat().st_size for f in self._profile_dir.rglob("*") if f.is_file())

        return {
            "session_id": self._session_id,
            "profile_dir": str(self._profile_dir),
            "profile_size_bytes": profile_size,
            "pages_visited": len(self._state.pages_visited),
        }
