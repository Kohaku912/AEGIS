#!/usr/bin/env python3
"""Safer IR blast: one header pin, Arduino-like LSB first, fewer variants."""
from __future__ import annotations

import os
import sys
import time


def tx(soc: str, *, active_low: str, bit_order: str, addr_mode: str, repeat: int = 3) -> dict:
    os.environ["AEGIS_ROOM_LIGHT_PROVIDER"] = "gpio"
    os.environ["AEGIS_ROOM_IR_PIN"] = soc
    os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"] = active_low
    os.environ["AEGIS_ROOM_IR_BIT_ORDER"] = bit_order
    os.environ["AEGIS_ROOM_IR_ADDR_MODE"] = addr_mode
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


def main() -> None:
    soc = (sys.argv[1] if len(sys.argv) > 1 else "").upper()
    if not soc:
        raise SystemExit("usage: opi_pin_blast_safe.py <SOC>")
    # Prefer Arduino IRremote defaults: LSB + both polarities; extended then standard.
    for bit_order, addr_mode, active_low in (
        ("lsb", "extended", "0"),
        ("lsb", "extended", "1"),
        ("lsb", "standard", "0"),
        ("lsb", "standard", "1"),
        ("msb", "extended", "0"),
        ("msb", "extended", "1"),
    ):
        print(tx(soc, active_low=active_low, bit_order=bit_order, addr_mode=addr_mode), flush=True)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
