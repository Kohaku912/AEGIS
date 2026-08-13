"""Content-addressed AES-GCM evidence blobs."""

from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_JST = timezone.utc


class EvidenceStore:
    def __init__(self, root: str | Path, *, key: bytes) -> None:
        if len(key) != 32:
            raise ValueError("evidence key must be 32 bytes")
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._key = key

    def put(
        self,
        data: bytes,
        *,
        codec: str,
        source_device: str,
        timestamp_ms: int,
        retention_class: str,
        mime: str = "",
        duration_ms: int = 0,
        metadata: dict[str, Any] | None = None,
        evidence_id: str = "",
    ) -> dict[str, Any]:
        digest = hashlib.sha256(data).hexdigest()
        ext = _ext(codec, mime)
        day = datetime.fromtimestamp(timestamp_ms / 1000, tz=_JST).strftime("%Y/%m/%d")
        rel = Path(day) / f"{digest}{ext}.aesgcm"
        path = self._root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            nonce = secrets.token_bytes(12)
            encrypted = AESGCM(self._key).encrypt(nonce, data, digest.encode("utf-8"))
            path.write_bytes(nonce + encrypted)
        return {
            "id": evidence_id or f"ev_{digest[:16]}",
            "sha256": digest,
            "codec": codec,
            "byte_size": len(data),
            "path": str(path),
            "retention_class": retention_class,
            "timestamp_ms": timestamp_ms,
            "duration_ms": duration_ms,
            "source_device": source_device,
            "mime": mime,
            "metadata": metadata or {},
        }

    def get(self, path: str, sha256: str) -> bytes:
        blob = Path(path).read_bytes()
        nonce, encrypted = blob[:12], blob[12:]
        return AESGCM(self._key).decrypt(nonce, encrypted, sha256.encode("utf-8"))

    def delete(self, path: str) -> None:
        try:
            Path(path).unlink(missing_ok=True)
        except TypeError:
            target = Path(path)
            if target.exists():
                target.unlink()


def _ext(codec: str, mime: str) -> str:
    mapping = {
        "jpeg": ".jpg",
        "jpg": ".jpg",
        "png": ".png",
        "webp": ".webp",
        "opus": ".opus",
        "wav": ".wav",
        "h265": ".hevc",
        "hevc": ".hevc",
        "av1": ".ivf",
        "json": ".json",
        "pcm_s16le": ".pcm",
    }
    if codec in mapping:
        return mapping[codec]
    if mime.startswith("image/"):
        return ".img"
    if mime.startswith("audio/"):
        return ".aud"
    if mime.startswith("video/"):
        return ".vid"
    return ".bin"
