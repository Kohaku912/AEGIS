from __future__ import annotations

from typing import Any


def summarize_openhands_events(events: list[dict[str, Any]], *, prefix: str) -> str:
    """Build a short human-readable summary from normalized OpenHands events."""
    last_text = _last_assistant_text(events)
    if last_text:
        return last_text

    terminal_command: str | None = None
    file_paths: list[str] = []
    tool_counts: dict[str, int] = {}

    for ev in events:
        if ev.get("kind") != "action":
            continue
        tool = str(ev.get("tool") or "unknown")
        tool_counts[tool] = tool_counts.get(tool, 0) + 1
        args = ev.get("args")
        if tool == "terminal" and terminal_command is None:
            terminal_command = _truncate_inline(
                _extract_first_string(args, ("cmd", "command"))
            )
        elif tool == "file_editor":
            for path in _extract_paths(args):
                if path not in file_paths:
                    file_paths.append(path)

    fragments: list[str] = []
    if terminal_command:
        fragments.append(f"ran {terminal_command}")
    if file_paths:
        preview = ", ".join(file_paths[:3])
        if len(file_paths) > 3:
            preview += f" and {len(file_paths) - 3} more files"
        fragments.append(f"touched {preview}")

    other_tools = [
        _format_tool_count(tool, count)
        for tool, count in tool_counts.items()
        if tool not in {"terminal", "file_editor"}
    ]
    if other_tools:
        fragments.append(f"used {', '.join(other_tools[:3])}")

    if fragments:
        return f"{prefix} " + "; ".join(fragments)
    return f"{prefix} completed with {len(events)} events"


def is_generic_openhands_summary(summary: str) -> bool:
    value = str(summary or "").strip()
    return value.startswith("OpenHands completed with ") or value.startswith(
        "RemoteOpenHands completed with "
    )


def _last_assistant_text(events: list[dict[str, Any]]) -> str:
    last_text = ""
    for ev in events:
        if ev.get("kind") != "message":
            continue
        if ev.get("role") not in ("assistant", "agent"):
            continue
        text = str(ev.get("text") or "").strip()
        if text:
            last_text = text
    return last_text[:4000]


def _extract_first_string(value: Any, keys: tuple[str, ...]) -> str:
    if isinstance(value, dict):
        for key in keys:
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        for candidate in value.values():
            found = _extract_first_string(candidate, keys)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _extract_first_string(item, keys)
            if found:
                return found
    return ""


def _extract_paths(value: Any) -> list[str]:
    found: list[str] = []
    _extract_paths_into(value, found)
    return found


def _extract_paths_into(value: Any, out: list[str]) -> None:
    if isinstance(value, dict):
        for key, candidate in value.items():
            if key in {
                "path",
                "file_path",
                "target_file",
                "source_file",
                "old_path",
                "new_path",
            } and isinstance(candidate, str):
                normalized = _truncate_inline(candidate.strip(), limit=80)
                if normalized and normalized not in out:
                    out.append(normalized)
            else:
                _extract_paths_into(candidate, out)
        return
    if isinstance(value, list):
        for item in value:
            _extract_paths_into(item, out)


def _format_tool_count(tool: str, count: int) -> str:
    if count == 1:
        return tool
    return f"{tool} x{count}"


def _truncate_inline(text: str, *, limit: int = 120) -> str:
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."
