"""Shared chat history storage for dashboard and mobile chat surfaces."""

from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.web.chat_history")


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
                    logger.debug(
                        "Skipped a chat-history line that would not parse; it is missing from the history",
                        exc_info=True,
                    )
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


# ── Cross-device context ──────────────────────────────────────────────────────
#
# The chat history is one local file shared by every surface (dashboard, mobile, …), and each
# entry carries the ``source`` that wrote it. That is enough to give the **assistant** the same
# continuity the UI already has: the context of a conversation is not the context of a device.
#
# Both helpers below are pure — they read the entries they are handed and touch no I/O — so the
# cross-device behaviour can be tested without a server or a file.

#: Used when an entry was written by a caller that did not say which device it was.
UNKNOWN_DEVICE = "unknown device"


def device_label(entry: dict[str, Any]) -> str:
    """Which device produced this entry.

    ``source`` is written by the callers that know ("dashboard", "android", …). An entry
    without one is labelled rather than left blank, so the prompt never shows an
    unattributed turn as if it were the current device's.
    """
    return str(entry.get("source", "") or "").strip() or UNKNOWN_DEVICE


def conversation_entries(
    entries: list[dict[str, Any]],
    *,
    conversation_id: str,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """The most recent entries of one conversation, from every device that took part.

    Cross-device context is scoped to the **conversation**, not to the device: a turn typed on
    the dashboard and a turn typed on the phone are the same conversation, so both are returned.

    An entry with no ``conversation_id`` is **never** matched. It cannot be attributed to a
    conversation, and folding an unattributable turn into one would invent a continuity the
    record does not support.
    """
    if not conversation_id or limit <= 0:
        return []
    matched = [
        entry
        for entry in entries
        if str(entry.get("conversation_id", "") or "") == conversation_id
    ]
    return matched[-limit:]


def context_excerpt(
    entries: list[dict[str, Any]],
    *,
    conversation_id: str = "",
    limit: int = 5,
) -> tuple[str, str]:
    """Build the continuity excerpt for the chat prompt, and name the scope that produced it.

    Returns ``(excerpt, scope)``. ``scope`` is ``"conversation"`` when the excerpt is one
    conversation's turns — possibly across several devices — or ``"recent"`` when it fell back
    to the most recent turns overall. The caller needs the scope because the two are different
    instructions to the model: a conversation continues, a recent excerpt is background only.

    ``entries`` must already have internal bookkeeping entries removed; this function does not
    know which entries those are.
    """
    scoped = conversation_entries(entries, conversation_id=conversation_id, limit=limit)
    if scoped:
        lines = [
            f"[{device_label(entry)}] Past user: {entry.get('user', '')}\n"
            f"[{device_label(entry)}] Past AEGIS: {str(entry.get('bot', ''))[:200]}"
            for entry in scoped
        ]
        return "\n".join(lines), "conversation"

    recent = entries[-limit:] if limit > 0 else []
    lines = [
        f"Past user: {entry.get('user', '')}\nPast AEGIS: {str(entry.get('bot', ''))[:200]}"
        for entry in recent
    ]
    return "\n".join(lines), "recent"
