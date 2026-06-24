"""Shared chat history storage for dashboard and mobile chat surfaces."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any


class ChatHistoryStore:
    """JSONL-backed chat history compatible with the dashboard API."""

    def __init__(self, path: str | Path = "data/chat_history.jsonl") -> None:
        self.path = Path(path)

    def append(
        self,
        user_msg: str,
        bot_msg: str,
        image: str = "",
        *,
        source: str = "",
        conversation_id: str = "",
    ) -> dict[str, Any]:
        timestamp = time.time()
        entry = {
            "timestamp": timestamp,
            "timestamp_ms": int(timestamp * 1000),
            "message_id": f"chat_{uuid.uuid4().hex[:12]}",
            "user": user_msg,
            "bot": bot_msg,
            "image": image,
        }
        if source:
            entry["source"] = source
        if conversation_id:
            entry["conversation_id"] = conversation_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def load(self, limit: int = 100) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        if not self.path.exists():
            return entries
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                try:
                    parsed = json.loads(line.strip())
                except Exception:
                    continue
                if isinstance(parsed, dict):
                    entries.append(parsed)
        entries.sort(key=lambda item: int(item.get("timestamp_ms") or float(item.get("timestamp", 0) or 0) * 1000))
        return entries[-limit:]

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()


def entry_to_mobile_messages(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten one dashboard history entry into role-based mobile bubbles."""
    timestamp_ms = int(entry.get("timestamp_ms") or float(entry.get("timestamp", 0) or 0) * 1000)
    base_id = str(entry.get("message_id") or f"chat_{timestamp_ms}")
    conversation_id = str(entry.get("conversation_id", ""))
    source = str(entry.get("source", ""))
    messages: list[dict[str, Any]] = []
    user_text = str(entry.get("user", "") or "")
    bot_text = str(entry.get("bot", "") or "")
    image = str(entry.get("image", "") or "")
    if user_text:
        messages.append(
            {
                "message_id": f"{base_id}:user",
                "role": "user",
                "text": user_text,
                "timestamp_ms": timestamp_ms,
                "image": "",
                "conversation_id": conversation_id,
                "source": source,
            }
        )
    if bot_text or image:
        messages.append(
            {
                "message_id": f"{base_id}:assistant",
                "role": "assistant",
                "text": bot_text,
                "timestamp_ms": timestamp_ms + 1 if user_text else timestamp_ms,
                "image": image,
                "conversation_id": conversation_id,
                "source": source,
            }
        )
    return messages


def entries_to_mobile_messages(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for entry in entries:
        messages.extend(entry_to_mobile_messages(entry))
    return messages
