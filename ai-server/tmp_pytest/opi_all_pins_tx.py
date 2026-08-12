#!/usr/bin/env python3
"""On OPi: TX IR-off on every Zero3 header GPIO (both polarities). Caller measures cam between pins."""
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


def tx_one(soc: str, active_low: str, repeat: int = 5) -> dict:
    os.environ["AEGIS_ROOM_LIGHT_PROVIDER"] = "gpio"
    os.environ["AEGIS_ROOM_IR_PIN"] = soc
    os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"] = active_low
    os.environ["AEGIS_ROOM_IR_BIT_ORDER"] = "msb"
    os.environ["AEGIS_ROOM_IR_ADDR_MODE"] = "extended"
    from aegis_room.providers import create_light_provider

    p = create_light_provider()
    ev = p.send_ir_command("light", "0xD001:0x23", repeat)
    return {"soc": soc, "active_low": active_low, "tx": ev.get("tx"), "warning": ev.get("warning")}


def main() -> None:
    # args: all | <soc>
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        for board, soc in PINS:
            for al in ("0", "1"):
                print(tx_one(soc, al), flush=True)
                time.sleep(0.1)
            print(f"PIN_DONE board={board} soc={soc}", flush=True)
            time.sleep(0.5)
        return
    # single pin both polarities
    print(tx_one(target, "0"), flush=True)
    print(tx_one(target, "1"), flush=True)


if __name__ == "__main__":
    main()
