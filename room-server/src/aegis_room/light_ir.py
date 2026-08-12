"""Ceiling light IR command map for the room lighting remote.

Address/command values match the installed fixture remote and Arduino
``IrSender.sendNEC(address, command, repeats)`` (LSB-first NEC).

Proven wiring on Orange Pi Zero3: DATA=PC11 (board pin 12), VCC=5V, GND=GND.
DATA must idle LOW or the TX module overheats. (PC9 is reserved for INMP441 SD.)
"""

from __future__ import annotations

from typing import Any

LIGHT_ADDR = 0xD001

# Command codes for the room ceiling light remote.
LIGHT_COMMANDS: dict[str, int] = {
    "all": 0x20,  # 全灯
    "full": 0x20,
    "on": 0x20,
    "eco": 0x21,  # エコ
    "night": 0x22,  # 常夜灯
    "night_light": 0x22,
    "off": 0x23,  # 消灯
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
            return "all" if key in {"full", "on"} else ("night" if key == "night_light" else key)
    if power_on is True:
        return "all"
    if power_on is False:
        return "off"
    return None


def command_for_mode(mode: str) -> int:
    normalized = normalize_mode(mode)
    if normalized is None:
        raise ValueError(f"Unsupported light mode: {mode!r}")
    return LIGHT_COMMANDS[normalized]


def format_ir_code(mode: str | None = None, *, command: int | None = None) -> str:
    if command is None:
        if mode is None:
            raise ValueError("mode or command is required")
        command = command_for_mode(mode)
    return f"0x{LIGHT_ADDR:04X}:0x{command:02X}"


def parse_ir_code(ir_code: str) -> dict[str, Any]:
    """Parse `0xD001:0x20` / `D001:20` / bare command hex into structured fields."""
    raw = (ir_code or "").strip()
    if not raw:
        raise ValueError("ir_code is empty")

    addr = LIGHT_ADDR
    cmd_text = raw
    if ":" in raw:
        left, right = raw.split(":", 1)
        addr = int(left.strip(), 0)
        cmd_text = right.strip()
    elif raw.lower() in LIGHT_COMMANDS or raw in MODE_ALIASES:
        mode = normalize_mode(raw)
        assert mode is not None
        return {
            "address": LIGHT_ADDR,
            "command": LIGHT_COMMANDS[mode],
            "mode": mode,
            "ir_code": format_ir_code(mode),
        }
    command = int(cmd_text, 0)
    mode = next((name for name, value in (("all", 0x20), ("eco", 0x21), ("night", 0x22), ("off", 0x23)) if value == command), None)
    return {
        "address": addr,
        "command": command,
        "mode": mode,
        "ir_code": f"0x{addr:04X}:0x{command:02X}",
    }


def power_on_for_mode(mode: str) -> bool:
    return normalize_mode(mode) != "off"
