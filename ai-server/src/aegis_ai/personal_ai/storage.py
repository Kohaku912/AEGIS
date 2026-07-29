"""Small JSON persistence helpers for personal AI managers."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

_PATH_LOCKS: dict[str, threading.RLock] = {}
_PATH_LOCKS_GUARD = threading.Lock()


def _path_lock(path: Path) -> threading.RLock:
    key = str(path.resolve())
    with _PATH_LOCKS_GUARD:
        return _PATH_LOCKS.setdefault(key, threading.RLock())


class JsonStateFile:
    """Atomic JSON file persistence."""

    def __init__(self, path: str | Path, default: dict[str, Any] | None = None) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.default = default or {}
        self._lock = _path_lock(self.path)

    def load(self) -> dict[str, Any]:
        with self._lock:
            if not self.path.exists():
                return dict(self.default)
            try:
                with self.path.open(encoding="utf-8") as f:
                    data = json.load(f)
                return data if isinstance(data, dict) else dict(self.default)
            except Exception:
                return dict(self.default)

    def save(self, data: dict[str, Any]) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=self.path.parent,
                    prefix=f".{self.path.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as f:
                    tmp_path = Path(f.name)
                    json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
                    f.flush()
                    os.fsync(f.fileno())
                for attempt in range(5):
                    try:
                        os.replace(tmp_path, self.path)
                        break
                    except PermissionError:
                        if attempt == 4:
                            raise
                        time.sleep(0.01 * (attempt + 1))
            finally:
                if tmp_path is not None and tmp_path.exists():
                    tmp_path.unlink()


def now_ms() -> int:
    import time

    return int(time.time() * 1000)


def append_jsonl(path: str | Path, entry: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
