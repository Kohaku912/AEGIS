"""Persistence helper for the compact user-understanding snapshot."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.user_understanding.store")


class UserUnderstandingStore:
    """Stores the latest compact understanding snapshot for reuse across surfaces."""

    def __init__(self, data_dir: str | Path = "data/user_understanding") -> None:
        self._dir = Path(data_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path = self._dir / "latest_snapshot.json"

    def save(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        try:
            self._path.write_text(
                json.dumps(snapshot, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning("Failed to save user understanding snapshot: %s", exc)
        return snapshot

    def load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Failed to load user understanding snapshot: %s", exc)
            return {}
