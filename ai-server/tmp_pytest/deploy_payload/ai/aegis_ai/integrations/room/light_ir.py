"""Ceiling light IR map mirrored for AI Server capability mapping.

Keep in sync with room-server/src/aegis_room/light_ir.py.
"""

from __future__ import annotations

LIGHT_ADDR = 0xD001
LIGHT_COMMANDS: dict[str, int] = {
    "all": 0x20,
    "full": 0x20,
    "on": 0x20,
    "eco": 0x21,
    "night": 0x22,
    "night_light": 0x22,
    "off": 0x23,
}
MODE_ALIASES: dict[str, str] = {
    "全灯": "all",
    "フル": "all",
    "エコ": "eco",
    "常夜灯": "night",
    "消灯": "off",
}


def normalize_mode(mode: str | None, *, power_on: bool | None = None) -> str | None:
    if mode:
        key = str(mode).strip().lower()
        key = MODE_ALIASES.get(str(mode).strip(), MODE_ALIASES.get(key, key))
        if key in LIGHT_COMMANDS:
            if key in {"full", "on"}:
                return "all"
            if key == "night_light":
                return "night"
            return key
    if power_on is True:
        return "all"
    if power_on is False:
        return "off"
    return None


def format_ir_code(mode: str) -> str:
    normalized = normalize_mode(mode)
    if normalized is None:
        raise ValueError(f"Unsupported light mode: {mode!r}")
    return f"0x{LIGHT_ADDR:04X}:0x{LIGHT_COMMANDS[normalized]:02X}"


def power_on_for_mode(mode: str) -> bool:
    return normalize_mode(mode) != "off"
