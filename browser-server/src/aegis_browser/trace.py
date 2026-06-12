"""Trace — logging and recording for browser-use agent actions.

Records all actions, page states, and decisions for debugging and audit.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_browser.trace")


@dataclass
class TraceEntry:
    """A single trace entry."""
    timestamp_ms: int = 0
    action: str = ""
    description: str = ""
    page_url: str = ""
    page_title: str = ""
    screenshot_path: str = ""
    result: str = ""
    error: str = ""
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class BrowserTrace:
    """Records browser actions for debugging and audit.

    Usage:
        trace = BrowserTrace(task_id="task_001")
        trace.record("navigate", "Opened example.com", page_url="https://example.com")
        trace.save("/app/traces/")
    """

    def __init__(self, task_id: str = "", output_dir: str = "/app/traces") -> None:
        self._task_id = task_id or f"trace_{uuid.uuid4().hex[:8]}"
        self._output_dir = Path(output_dir)
        self._entries: list[TraceEntry] = []
        self._start_time = time.time()

    @property
    def task_id(self) -> str:
        return self._task_id

    def record(
        self,
        action: str,
        description: str = "",
        page_url: str = "",
        page_title: str = "",
        result: str = "",
        error: str = "",
        duration_ms: float = 0.0,
        **kwargs: Any,
    ) -> None:
        """Record a trace entry."""
        entry = TraceEntry(
            timestamp_ms=int(time.time() * 1000),
            action=action,
            description=description,
            page_url=page_url,
            page_title=page_title,
            result=result,
            error=error,
            duration_ms=duration_ms,
            metadata=kwargs,
        )
        self._entries.append(entry)
        logger.debug("Trace: %s — %s", action, description[:100])

    def get_entries(self) -> list[TraceEntry]:
        """Get all trace entries."""
        return list(self._entries)

    def get_summary(self) -> dict[str, Any]:
        """Get trace summary."""
        return {
            "task_id": self._task_id,
            "total_entries": len(self._entries),
            "total_duration_ms": (time.time() - self._start_time) * 1000,
            "actions": [e.action for e in self._entries],
            "errors": [e.error for e in self._entries if e.error],
        }

    def save(self, output_dir: str | None = None) -> str:
        """Save trace to file."""
        out_dir = Path(output_dir) if output_dir else self._output_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        filepath = out_dir / f"{self._task_id}.json"
        data = {
            "task_id": self._task_id,
            "start_time": self._start_time,
            "entries": [
                {
                    "timestamp_ms": e.timestamp_ms,
                    "action": e.action,
                    "description": e.description,
                    "page_url": e.page_url,
                    "page_title": e.page_title,
                    "result": e.result[:500] if e.result else "",
                    "error": e.error,
                    "duration_ms": e.duration_ms,
                }
                for e in self._entries
            ],
        }

        filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Trace saved: %s", filepath)
        return str(filepath)
