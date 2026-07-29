"""User-scoped saved dashboard views."""

from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any


class SavedViewManager:
    """Persist filter views without owning the underlying resource state."""

    def __init__(self, data_dir: str, audit_manager: Any = None) -> None:
        self._path = Path(data_dir) / "ui" / "saved_views.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._audit_manager = audit_manager
        self._lock = threading.RLock()

    def list_views(self, user_id: str, resource: str = "") -> list[dict[str, Any]]:
        with self._lock:
            items = [item for item in self._read() if item["user_id"] == user_id]
        if resource:
            items = [item for item in items if item["resource"] == resource]
        return [self._public(item) for item in sorted(items, key=lambda item: item["updated_at"], reverse=True)]

    def create_view(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        now = int(time.time() * 1000)
        item = {
            "id": uuid.uuid4().hex,
            "user_id": user_id,
            **self._validated(payload),
            "created_at": now,
            "updated_at": now,
        }
        with self._lock:
            items = self._read()
            items.append(item)
            self._write(items)
        self._audit("saved_view.created", user_id, item)
        return self._public(item)

    def update_view(self, user_id: str, view_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            items = self._read()
            item = next((entry for entry in items if entry["id"] == view_id and entry["user_id"] == user_id), None)
            if item is None:
                return None
            item.update(self._validated({**item, **payload}))
            item["updated_at"] = int(time.time() * 1000)
            self._write(items)
        self._audit("saved_view.updated", user_id, item)
        return self._public(item)

    def delete_view(self, user_id: str, view_id: str) -> bool:
        with self._lock:
            items = self._read()
            remaining = [entry for entry in items if not (entry["id"] == view_id and entry["user_id"] == user_id)]
            if len(remaining) == len(items):
                return False
            self._write(remaining)
        self._audit("saved_view.deleted", user_id, {"id": view_id})
        return True

    @staticmethod
    def _validated(payload: dict[str, Any]) -> dict[str, Any]:
        resource = str(payload.get("resource") or "").strip().lower()
        name = str(payload.get("name") or "").strip()
        if not resource or not name:
            raise ValueError("resource and name are required")
        filters = payload.get("filters") if isinstance(payload.get("filters"), dict) else {}
        return {
            "resource": resource[:64],
            "name": name[:80],
            "query": str(payload.get("query") or "")[:500],
            "filters": {str(key)[:64]: str(value)[:500] for key, value in filters.items()},
            "sort": str(payload.get("sort") or "updated_at")[:64],
            "order": "asc" if str(payload.get("order")).lower() == "asc" else "desc",
            "page_size": max(10, min(200, int(payload.get("page_size") or 25))),
        }

    def _read(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def _write(self, items: list[dict[str, Any]]) -> None:
        temporary = self._path.with_suffix(".tmp")
        temporary.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(self._path)

    @staticmethod
    def _public(item: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in item.items() if key != "user_id"}

    def _audit(self, action: str, user_id: str, detail: dict[str, Any]) -> None:
        if self._audit_manager is not None:
            self._audit_manager.log_decision(
                action=action,
                actor=user_id,
                decision="success",
                reason=action,
                detail={"view_id": detail.get("id"), "resource": detail.get("resource")},
            )
