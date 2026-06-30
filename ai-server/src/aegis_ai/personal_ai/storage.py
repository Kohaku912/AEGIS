"""Small JSON persistence helpers for personal AI managers."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class JsonStateFile:
    """Atomic JSON file persistence."""

    def __init__(self, path: str | Path, default: dict[str, Any] | None = None) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.default = default or {}

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return dict(self.default)
        try:
            with self.path.open(encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else dict(self.default)
        except Exception:
            return dict(self.default)

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        os.replace(tmp, self.path)


def now_ms() -> int:
    import time

    return int(time.time() * 1000)


def append_jsonl(path: str | Path, entry: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
