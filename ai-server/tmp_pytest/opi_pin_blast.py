#!/usr/bin/env python3
"""TX IR-off variants on one (or all) Zero3 header pin(s)."""
from __future__ import annotations

import os
import sys
import time

PINS = [
    ("3", "PH5"),
    ("5", "PH4"),
    ("7", "PC9"),
    ("8", "PH2"),
    ("10", "PH3"),
    ("11", "PC6"),
    ("12", "PC11"),
    ("13", "PC5"),
    ("15", "PC8"),
    ("16", "PC15"),
    ("18", "PC14"),
    ("19", "PH7"),
    ("21", "PH8"),
    ("22", "PC7"),
    ("23", "PH6"),
    ("24", "PH9"),
    ("26", "PC10"),
]


def tx(soc: str, *, active_low: str, bit_order: str, addr_mode: str, repeat: int = 4) -> dict:
    os.environ["AEGIS_ROOM_LIGHT_PROVIDER"] = "gpio"
    os.environ["AEGIS_ROOM_IR_PIN"] = soc
    os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"] = active_low
    os.environ["AEGIS_ROOM_IR_BIT_ORDER"] = bit_order
    os.environ["AEGIS_ROOM_IR_ADDR_MODE"] = addr_mode
    # Fresh import path each time — provider reads env in __init__
    from aegis_room.providers import create_light_provider

    p = create_light_provider()
    ev = p.send_ir_command("light", "0xD001:0x23", repeat)
    return {
        "soc": soc,
        "active_low": active_low,
        "bit_order": bit_order,
        "addr_mode": addr_mode,
        "tx": ev.get("tx"),
        "warning": ev.get("warning"),
    }


def blast_pin(soc: str) -> None:
    # Arduino IRremote NEC is typically LSB-first; try that first, then MSB.
    for bit_order in ("lsb", "msb"):
        for addr_mode in ("extended", "standard"):
            for active_low in ("0", "1"):
                print(tx(soc, active_low=active_low, bit_order=bit_order, addr_mode=addr_mode), flush=True)
                time.sleep(0.08)


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else ""
    if not target:
        raise SystemExit("usage: opi_pin_blast.py <SOC>")
    blast_pin(target.upper())


if __name__ == "__main__":
    main()
