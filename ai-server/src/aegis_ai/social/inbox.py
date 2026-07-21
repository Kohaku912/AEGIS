"""Thread-safe JSON persistence for the social inbox."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from aegis_ai.social.models import SocialInboxItem


class SocialInboxStore:
    def __init__(self, data_dir: str = "data/social") -> None:
        self._path = Path(data_dir) / "social_inbox.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._items: dict[str, SocialInboxItem] = {}
        self._external_index: dict[tuple[str, str], str] = {}
        self._load()

    def upsert(self, item: SocialInboxItem) -> SocialInboxItem:
        with self._lock:
            existing_id = self._external_index.get((item.channel, item.external_message_id))
            if existing_id:
                return self._items[existing_id]
            self._items[item.item_id] = item
            self._external_index[(item.channel, item.external_message_id)] = item.item_id
            self._save()
            return item

    def update(self, item: SocialInboxItem) -> SocialInboxItem:
        with self._lock:
            self._items[item.item_id] = item
            self._external_index[(item.channel, item.external_message_id)] = item.item_id
            self._save()
            return item

    def get(self, item_id: str) -> SocialInboxItem | None:
        with self._lock:
            return self._items.get(item_id)

    def list(self, status: str = "", limit: int = 200) -> list[SocialInboxItem]:
        with self._lock:
            values = list(self._items.values())
        if status:
            values = [item for item in values if item.status.value == status]
        values.sort(key=lambda item: item.received_at, reverse=True)
        return values[:limit]

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            for raw in data.get("items", []):
                item = SocialInboxItem.from_dict(raw)
                self._items[item.item_id] = item
                self._external_index[(item.channel, item.external_message_id)] = item.item_id
        except Exception:
            corrupt = self._path.with_suffix(".corrupt.json")
            try:
                os.replace(self._path, corrupt)
            except OSError:
                pass

    def _save(self) -> None:
        payload = {"version": 1, "items": [item.to_dict() for item in self._items.values()]}
        temporary = self._path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporary, self._path)
