"""Assert Arduino-IRremote sendNEC payload layout."""
from __future__ import annotations

import os

os.environ["AEGIS_ROOM_LIGHT_PROVIDER"] = "gpio"
os.environ["AEGIS_ROOM_IR_PIN"] = "PC11"
os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"] = "0"
# Avoid touching /dev/mem in unit test — stub availability.
import aegis_room.providers as providers

providers.OrangePiGpioIrProvider._gpio_available = False  # type: ignore[attr-defined]


def test_nec_payload_matches_arduino_sendNEC_extended() -> None:
    p = providers.OrangePiGpioIrProvider.__new__(providers.OrangePiGpioIrProvider)
    p._addr_mode = "auto"
    # IrSender.sendNEC(0xD001, 0x23, 3) → 0xDC23D001
    assert p._build_nec_payload(0xD001, 0x23) == 0xDC23D001


def test_nec_payload_matches_arduino_sendNEC_standard() -> None:
    p = providers.OrangePiGpioIrProvider.__new__(providers.OrangePiGpioIrProvider)
    p._addr_mode = "auto"
    # 8-bit address 0x01, cmd 0x23 → 01 FE 23 DC
    assert p._build_nec_payload(0x01, 0x23) == 0xDC23FE01
