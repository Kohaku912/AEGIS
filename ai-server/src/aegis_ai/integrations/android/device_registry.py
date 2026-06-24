"""Android device registry and pairing-token authentication."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AndroidDeviceRecord:
    """Persisted Android device authorization record."""

    device_id: str
    token_hash: str
    approved: bool = True
    device_model: str = ""
    manufacturer: str = ""
    android_version: str = ""
    app_version: str = ""
    first_seen_ms: int = 0
    last_seen_ms: int = 0
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "token_hash": self.token_hash,
            "approved": self.approved,
            "device_model": self.device_model,
            "manufacturer": self.manufacturer,
            "android_version": self.android_version,
            "app_version": self.app_version,
            "first_seen_ms": self.first_seen_ms,
            "last_seen_ms": self.last_seen_ms,
            "metadata": self.metadata,
        }


class AndroidDeviceRegistry:
    """Stores and verifies approved Android devices.

    Pairing token is mandatory. A valid token authorizes first registration and
    the device is then persisted in data/android/devices.json.
    """

    def __init__(self, data_dir: str, pairing_token: str | None = None) -> None:
        self._data_dir = Path(data_dir) / "android"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._path = self._data_dir / "devices.json"
        self._pairing_token = (
            pairing_token if pairing_token is not None else os.getenv("AEGIS_ANDROID_PAIRING_TOKEN", "")
        )
        self._devices: dict[str, AndroidDeviceRecord] = {}
        self._lock = threading.RLock()
        self._load()

    @property
    def pairing_configured(self) -> bool:
        return bool(self._pairing_token)

    def verify_and_authorize(
        self,
        *,
        device_id: str,
        pairing_token: str,
        metadata: dict[str, str] | None = None,
        device_model: str = "",
        manufacturer: str = "",
        android_version: str = "",
        app_version: str = "",
    ) -> bool:
        """Verify pairing token and persist an approved device."""
        if not device_id or not self._pairing_token:
            return False
        if not hmac.compare_digest(pairing_token, self._pairing_token):
            return False

        now_ms = int(time.time() * 1000)
        token_hash = self._hash_token(pairing_token)
        with self._lock:
            existing = self._devices.get(device_id)
            record = existing or AndroidDeviceRecord(
                device_id=device_id,
                token_hash=token_hash,
                first_seen_ms=now_ms,
            )
            record.token_hash = token_hash
            record.approved = True
            record.device_model = device_model or record.device_model
            record.manufacturer = manufacturer or record.manufacturer
            record.android_version = android_version or record.android_version
            record.app_version = app_version or record.app_version
            record.last_seen_ms = now_ms
            record.metadata.update(metadata or {})
            self._devices[device_id] = record
            self._save()
        return True

    def is_authorized(self, device_id: str, pairing_token: str = "") -> bool:
        """Return True if a device is approved and token matches when supplied."""
        with self._lock:
            record = self._devices.get(device_id)
        if record is None or not record.approved:
            return False
        if pairing_token:
            return hmac.compare_digest(record.token_hash, self._hash_token(pairing_token))
        return True

    def touch(self, device_id: str) -> None:
        with self._lock:
            record = self._devices.get(device_id)
            if record is None:
                return
            record.last_seen_ms = int(time.time() * 1000)
            self._save()

    def list_devices(self) -> list[dict[str, Any]]:
        with self._lock:
            return [record.to_dict() for record in self._devices.values()]

    def get(self, device_id: str) -> dict[str, Any] | None:
        with self._lock:
            record = self._devices.get(device_id)
            return record.to_dict() if record else None

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _save(self) -> None:
        data = {
            "devices": [record.to_dict() for record in self._devices.values()],
            "saved_at_ms": int(time.time() * 1000),
        }
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            for item in data.get("devices", []):
                record = AndroidDeviceRecord(**item)
                self._devices[record.device_id] = record
        except Exception:
            self._devices = {}
