#!/usr/bin/env python3
"""Sweep IR TX variants; print brightness deltas from host cam (caller measures)."""
from __future__ import annotations

import os
import time

os.environ.setdefault("AEGIS_ROOM_LIGHT_PROVIDER", "gpio")
os.environ.setdefault("AEGIS_ROOM_IR_PIN", "PC9")

from aegis_room.providers import create_light_provider  # noqa: E402


VARIANTS = [
    # active_low, bit_order, addr_mode, code
    ("0", "msb", "extended", "0xD001:0x23"),
    ("1", "msb", "extended", "0xD001:0x23"),
    ("0", "lsb", "extended", "0xD001:0x23"),
    ("1", "lsb", "extended", "0xD001:0x23"),
    ("0", "msb", "standard", "0xD001:0x23"),
    ("1", "msb", "standard", "0xD001:0x23"),
    ("0", "lsb", "standard", "0xD001:0x23"),
    ("1", "lsb", "standard", "0xD001:0x23"),
    # try low byte of address as standard addr
    ("1", "lsb", "standard", "0x01:0x23"),
    ("1", "msb", "standard", "0x01:0x23"),
    ("1", "lsb", "extended", "0x00D0:0x23"),
]


def main() -> None:
    for active_low, bit_order, addr_mode, code in VARIANTS:
        os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"] = active_low
        os.environ["AEGIS_ROOM_IR_BIT_ORDER"] = bit_order
        os.environ["AEGIS_ROOM_IR_ADDR_MODE"] = addr_mode
        provider = create_light_provider()
        ev = provider.send_ir_command("light", code, 3)
        print(
            "TX",
            active_low,
            bit_order,
            addr_mode,
            code,
            ev.get("tx"),
            ev.get("warning"),
            flush=True,
        )
        time.sleep(0.8)


if __name__ == "__main__":
    main()
