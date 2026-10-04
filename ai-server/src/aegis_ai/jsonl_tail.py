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
        dropped = 0
        for raw in lines[-limit:]:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except Exception:
                dropped += 1
                continue
            if isinstance(item, dict):
                records.append(item)
        if dropped:
            # A malformed line used to be dropped in silence, so the caller saw a *shorter*
            # window and could not tell it apart from a file with fewer records.
            logger.warning(
                "Skipped %d unreadable line(s) while tailing %s; those records are not returned.",
                dropped,
                target,
            )
        return records[-limit:]
    except Exception:
        # Returning [] here is indistinguishable from "no records in the window", so the
        # caller cannot tell an unreadable file from an empty one. Say so.
        logger.warning("Failed to tail JSONL %s; returning an empty window.", target, exc_info=True)
        return []


def append_jsonl(path: Path | str, record: dict[str, Any]) -> None:
    """Append one JSON object; never rewrites historical rows."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
