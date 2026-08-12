#!/usr/bin/env python3
"""TX IR off on one Orange Pi Zero3 header pin (via mmap)."""
from __future__ import annotations

import os
import sys
import time

os.environ["AEGIS_ROOM_LIGHT_PROVIDER"] = "gpio"
os.environ.setdefault("AEGIS_ROOM_IR_BIT_ORDER", "msb")
os.environ.setdefault("AEGIS_ROOM_IR_ADDR_MODE", "extended")

from aegis_room.providers import create_light_provider  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: opi_tx_pin.py <SOC_OR_BOARD> [active_low=0|1] [repeat=4]")
    pin = sys.argv[1]
    active_low = sys.argv[2] if len(sys.argv) > 2 else "0"
    repeat = int(sys.argv[3] if len(sys.argv) > 3 else "4")
    os.environ["AEGIS_ROOM_IR_PIN"] = pin
    os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"] = active_low
    p = create_light_provider()
    ev = p.send_ir_command("light", "0xD001:0x23", repeat)
    print({"pin": pin, "active_low": active_low, "tx": ev.get("tx"), "warning": ev.get("warning")})
    time.sleep(0.15)


if __name__ == "__main__":
    main()
