"""Bounded JSONL readers — full history stays on disk; callers load only a hot window."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.jsonl_tail")


def read_jsonl_tail(
    path: Path | str,
    limit: int,
    *,
    max_bytes: int | None = None,
) -> list[dict[str, Any]]:
    """Read the last ``limit`` JSONL objects without loading the whole file.

    Persistence remains append-only elsewhere. This helper only bounds *reads*.
    """
    target = Path(path)
    if limit <= 0 or not target.exists():
        return []

    byte_budget = max_bytes
    if byte_budget is None:
        # Rough budget: ~4KB/record with a floor so tiny files still work.
        byte_budget = max(64 * 1024, int(limit) * 4096)

    try:
        size = target.stat().st_size
        with target.open("rb") as fh:
            offset = max(0, size - byte_budget)
            fh.seek(offset)
            payload = fh.read(byte_budget)
        if offset:
            newline = payload.find(b"\n")
            payload = payload[newline + 1 :] if newline >= 0 else b""
        lines = payload.splitlines()
        records: list[dict[str, Any]] = []
        for raw in lines[-limit:]:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue
            if isinstance(item, dict):
                records.append(item)
        return records[-limit:]
    except Exception:
        logger.debug("Failed to tail JSONL %s", target, exc_info=True)
        return []


def append_jsonl(path: Path | str, record: dict[str, Any]) -> None:
    """Append one JSON object; never rewrites historical rows."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
