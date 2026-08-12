"""Room device providers.

The mock provider is the default and never touches GPIO. The Orange Pi provider
is an env-gated skeleton so hardware integration can be completed on the target
device without changing the gRPC service contract.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from aegis_room.light_ir import (
    LIGHT_ADDR,
    format_ir_code,
    normalize_mode,
    parse_ir_code,
    power_on_for_mode,
)


def now_ms() -> int:
    return int(time.time() * 1000)


def default_ir_repeat() -> int:
    """Arduino IrSender.sendNEC(..., repeats) default used by the ceiling remote."""
    try:
        value = int(os.environ.get("AEGIS_ROOM_IR_REPEAT", "3") or "3")
    except ValueError:
        value = 3
    return max(1, min(10, value))


@dataclass
class LightState:
    device_id: str
    power_on: bool = False
    brightness: int = -1
    color_temp_k: int = 0
    color_rgb: str = ""
    ir_code: str = ""
    provider: str = "mock"
    updated_at_ms: int = field(default_factory=now_ms)

    def to_json(self) -> str:
        return json.dumps(
            {
                "power_on": self.power_on,
                "brightness": self.brightness,
                "color_temp_k": self.color_temp_k,
                "color_rgb": self.color_rgb,
                "ir_code": self.ir_code,
                "provider": self.provider,
                "updated_at_ms": self.updated_at_ms,
            },
            ensure_ascii=True,
        )


class LightProvider(Protocol):
    provider_name: str

    def set_light(
        self,
        device_id: str,
        power_on: bool,
        brightness: int,
        color_temp_k: int,
        color_rgb: str,
        ir_code: str,
        mode: str = "",
        repeat: int | None = None,
    ) -> LightState:
        ...

    def send_ir_command(self, device_type: str, ir_code: str, repeat: int) -> dict[str, Any]:
        ...

    def get_light_states(self) -> list[LightState]:
        ...

    def get_light_state(self, device_id: str) -> LightState | None:
        ...


class MockLightIrProvider:
    """Deterministic in-memory provider for development and CI."""

    provider_name = "mock"

    def __init__(self, default_device_id: str = "light-main") -> None:
        self._states: dict[str, LightState] = {
            default_device_id: LightState(device_id=default_device_id, provider=self.provider_name)
        }
        self.ir_log: list[dict[str, Any]] = []

    def set_light(
        self,
        device_id: str,
        power_on: bool,
        brightness: int,
        color_temp_k: int,
        color_rgb: str,
        ir_code: str,
        mode: str = "",
        repeat: int | None = None,
    ) -> LightState:
        device_id = device_id or "light-main"
        resolved_mode = normalize_mode(mode or None, power_on=power_on)
        resolved_ir = ir_code
        if not resolved_ir and resolved_mode:
            resolved_ir = format_ir_code(resolved_mode)
        if resolved_mode is not None:
            power_on = power_on_for_mode(resolved_mode)
        state = LightState(
            device_id=device_id,
            power_on=power_on,
            brightness=brightness,
            color_temp_k=color_temp_k,
            color_rgb=color_rgb,
            ir_code=resolved_ir,
            provider=self.provider_name,
        )
        self._states[device_id] = state
        # Arduino IrSender.sendNEC(addr, cmd, N) with N=3 — emit N full frames.
        frames = default_ir_repeat() if repeat is None else max(1, min(10, int(repeat)))
        ir_event = self.send_ir_command(
            "light",
            resolved_ir or format_ir_code("all" if power_on else "off"),
            frames,
        )
        ir_event["device_id"] = device_id
        if resolved_mode:
            ir_event["mode"] = resolved_mode
        return state

    def send_ir_command(self, device_type: str, ir_code: str, repeat: int) -> dict[str, Any]:
        parsed = parse_ir_code(ir_code) if ir_code else {"address": LIGHT_ADDR, "command": None, "mode": None, "ir_code": ir_code}
        event = {
            "device_type": device_type or "other",
            "ir_code": parsed.get("ir_code") or ir_code,
            "address": parsed.get("address"),
            "command": parsed.get("command"),
            "mode": parsed.get("mode"),
            "repeat": repeat,
            "timestamp_ms": now_ms(),
            "mock": True,
            "provider": self.provider_name,
        }
        self.ir_log.append(event)
        return event

    def get_light_states(self) -> list[LightState]:
        return list(self._states.values())

    def get_light_state(self, device_id: str) -> LightState | None:
        return self._states.get(device_id)


# Orange Pi Zero3 26-pin header: physical BOARD pin -> SoC pin name.
_ZERO3_BOARD_TO_SOC: dict[int, str] = {
    3: "PH5",
    5: "PH4",
    7: "PC9",
    8: "PH2",
    10: "PH3",
    11: "PC6",
    12: "PC11",
    13: "PC5",
    15: "PC8",
    16: "PC15",
    18: "PC14",
    19: "PH7",
    21: "PH8",
    22: "PC7",
    23: "PH6",
    24: "PH9",
    26: "PC10",
}

# Allwinner H616/H618 PIO controller (Orange Pi Zero 3).
# Calibrated on device: bank stride is 0x24 (not 0x30).
_SUNXI_PIO_BASE = 0x0300B000
_SUNXI_BANK_STRIDE = 0x24


def _soc_pin_to_bank_bit(soc_pin: str) -> tuple[int, int]:
    text = soc_pin.strip().upper()
    if len(text) < 3 or text[0] != "P" or not text[1].isalpha():
        raise ValueError(f"Unsupported SoC pin name: {soc_pin!r}")
    bank = ord(text[1]) - ord("A")
    bit = int(text[2:])
    if bank < 0 or bit < 0 or bit > 31:
        raise ValueError(f"Unsupported SoC pin name: {soc_pin!r}")
    return bank, bit


# Board 3/5 (PH5/PH4) share the TWI/I2C path used by AXP313a. Remuxing them
# via /dev/mem causes axp313a IRQ storms ("irq 76: nobody cared") and hard hangs.
_FORBIDDEN_IR_SOC_PINS = frozenset({"PH4", "PH5"})


def resolve_ir_pin(pin: str) -> dict[str, Any]:
    """Resolve AEGIS_ROOM_IR_PIN into SoC bank/bit for Zero3 IR TX.

    Accepts: PC11 | 12 (BOARD) | gpiochip1:75 | 75 | PC9 | …
    """
    raw = (pin or "").strip()
    if not raw:
        raise ValueError("empty pin")

    soc = ""
    chip_line: int | None = None
    if raw.upper().startswith("P") and raw[1:2].isalpha():
        soc = raw.upper()
    elif ":" in raw:
        _, line_text = raw.split(":", 1)
        chip_line = int(line_text.strip(), 0)
    elif raw.isdigit():
        num = int(raw)
        if num in _ZERO3_BOARD_TO_SOC:
            soc = _ZERO3_BOARD_TO_SOC[num]
        else:
            chip_line = num
    else:
        raise ValueError(f"Unrecognized IR pin spec: {pin!r}")

    if chip_line is not None and not soc:
        bank, bit = divmod(chip_line, 32)
        soc = f"P{chr(ord('A') + bank)}{bit}"
    if soc in _FORBIDDEN_IR_SOC_PINS:
        raise ValueError(
            f"IR pin {soc} is forbidden: remuxing PH4/PH5 breaks AXP313a (I2C) and hangs the board"
        )
    bank, bit = _soc_pin_to_bank_bit(soc)
    return {
        "spec": raw,
        "soc_pin": soc,
        "bank": bank,
        "bit": bit,
        "gpio_line": bank * 32 + bit,
    }


class OrangePiGpioIrProvider(MockLightIrProvider):
    """Orange Pi GPIO IR transmitter (Zero3 PC11 / BOARD 12).

    gpiod often cannot drive EINT-boot pins; transmit uses /dev/mem PIO with a
    software 38 kHz carrier.

    Arduino-compatible IR LED modules (KY-005 style): VCC=5V, DATA idle must be
    **physical LOW** or the transistor stays on and the module overheats.
    Do not reuse PC6/PC8/PC9 — those are wired to INMP441 I2S.
    """

    provider_name = "orangepi-gpio"

    def __init__(self, pin: str, default_device_id: str = "light-main") -> None:
        if not pin:
            raise RuntimeError("AEGIS_ROOM_IR_PIN is required when AEGIS_ROOM_LIGHT_PROVIDER=gpio")
        super().__init__(default_device_id=default_device_id)
        self.pin = pin
        self._pin_info = resolve_ir_pin(pin)
        # Arduino IRremote modules are active-HIGH (HIGH=LED on). active_low=1 idles
        # the wire HIGH and will cook the module — keep default off.
        self._active_low = os.environ.get("AEGIS_ROOM_IR_ACTIVE_LOW", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if self._active_low:
            # KY-005 / Arduino modules idle LOW; active_low leaves DATA HIGH between marks → heat.
            import logging

            logging.getLogger("aegis_room.providers").warning(
                "AEGIS_ROOM_IR_ACTIVE_LOW=1 will idle IR DATA high; Arduino-compatible modules overheat"
            )
        self._carrier_hz = int(os.environ.get("AEGIS_ROOM_IR_CARRIER_HZ", "38000") or "38000")
        # Arduino IRremote NEC is LSB-first.
        self._bit_order = os.environ.get("AEGIS_ROOM_IR_BIT_ORDER", "lsb").strip().lower() or "lsb"
        # Arduino IRremote sendNEC: auto extended when address has high byte.
        self._addr_mode = os.environ.get("AEGIS_ROOM_IR_ADDR_MODE", "auto").strip().lower() or "auto"
        self._gpio_available = os.path.exists("/dev/mem")
        # Claim pin immediately and park at safe idle (physical 0V) so the module
        # cannot sit partially-on while the SoC left the pin as floating EINT input.
        if self._gpio_available:
            try:
                idle = self.ensure_safe_idle()
                if idle.get("level") != 0:
                    raise RuntimeError(f"IR DATA failed to park LOW after init: {idle}")
            except Exception as exc:
                raise RuntimeError(f"IR pin safe-idle init failed on {self._pin_info['soc_pin']}: {exc}") from exc

    def ensure_safe_idle(self) -> dict[str, Any]:
        """Drive IR DATA to physical 0V (Arduino idle). Prevents module overheating."""
        return self._with_pio(self._park_idle_locked)

    def send_ir_command(self, device_type: str, ir_code: str, repeat: int) -> dict[str, Any]:
        event = super().send_ir_command(device_type, ir_code, repeat)
        event["mock"] = False
        event["pin"] = self.pin
        event["pin_info"] = dict(self._pin_info)
        event["gpio_available"] = self._gpio_available
        if not self._gpio_available:
            event["warning"] = "/dev/mem unavailable; IR command was recorded but not sent"
            return event
        try:
            event["tx"] = self._transmit_nec(int(event["address"]), int(event["command"]), repeat)
        except Exception as exc:
            event["warning"] = f"IR transmit failed: {exc}"
            try:
                event["idle"] = self.ensure_safe_idle()
            except Exception as idle_exc:
                event["idle_error"] = str(idle_exc)
        return event

    def _build_nec_payload(self, address: int, command: int) -> int:
        """Match Arduino-IRremote ``computeNECRawDataAndChecksum`` / ``sendNEC``.

        Layout (LSB-first on the wire), little-endian 32-bit word:
        - address < 0x100:  addr, ~addr, cmd, ~cmd
        - else (e.g. 0xD001): addr16, cmd, ~cmd
        """
        cmd = command & 0xFF
        inv = (~cmd) & 0xFF
        if self._addr_mode == "standard":
            addr8 = address & 0xFF
            return addr8 | (((~addr8) & 0xFF) << 8) | (cmd << 16) | (inv << 24)
        if self._addr_mode == "extended" or (address & 0xFF00) != 0:
            return (address & 0xFFFF) | (cmd << 16) | (inv << 24)
        addr8 = address & 0xFF
        return addr8 | (((~addr8) & 0xFF) << 8) | (cmd << 16) | (inv << 24)

    def _with_pio(self, fn):  # type: ignore[no-untyped-def]
        import mmap
        import struct

        bank = int(self._pin_info["bank"])
        bit = int(self._pin_info["bit"])
        bank_off = bank * _SUNXI_BANK_STRIDE
        cfg_off = bank_off + (bit // 8) * 4
        cfg_shift = (bit % 8) * 4
        dat_off = bank_off + 0x10
        with open("/dev/mem", "r+b", buffering=0) as mem_file:
            mapping = mmap.mmap(mem_file.fileno(), 0x1000, offset=_SUNXI_PIO_BASE)
            try:
                return fn(mapping, struct, bit, cfg_off, cfg_shift, dat_off)
            finally:
                mapping.close()

    def _set_output_locked(self, mapping, struct, bit, cfg_off, cfg_shift, dat_off) -> None:  # noqa: ANN001
        cfg = struct.unpack_from("<I", mapping, cfg_off)[0]
        cfg = (cfg & ~(0xF << cfg_shift)) | (0x1 << cfg_shift)
        struct.pack_into("<I", mapping, cfg_off, cfg)

    def _write_physical_locked(self, mapping, struct, bit, dat_off, high: bool) -> None:  # noqa: ANN001
        """Write the wire level in volts: high=True => ~3.3V, False => 0V."""
        dat = struct.unpack_from("<I", mapping, dat_off)[0]
        if high:
            dat |= 1 << bit
        else:
            dat &= ~(1 << bit)
        struct.pack_into("<I", mapping, dat_off, dat)

    def _read_physical_locked(self, mapping, struct, bit, dat_off) -> int:  # noqa: ANN001
        dat = struct.unpack_from("<I", mapping, dat_off)[0]
        return 1 if (dat >> bit) & 1 else 0

    def _park_idle_locked(self, mapping, struct, bit, cfg_off, cfg_shift, dat_off) -> dict[str, Any]:  # noqa: ANN001
        # Always park at physical 0V. Active-high Arduino modules need this; an
        # active-low module would need a different safe idle (not used here).
        self._set_output_locked(mapping, struct, bit, cfg_off, cfg_shift, dat_off)
        self._write_physical_locked(mapping, struct, bit, dat_off, False)
        level = self._read_physical_locked(mapping, struct, bit, dat_off)
        cfg = struct.unpack_from("<I", mapping, cfg_off)[0]
        return {
            "soc_pin": self._pin_info["soc_pin"],
            "cfg_mode": (cfg >> cfg_shift) & 0xF,
            "level": level,
            "safe_idle_v": 0,
        }

    def _transmit_nec(self, address: int, command: int, repeat: int) -> dict[str, Any]:
        """NEC-like frame with 38 kHz carrier via sunxi PIO mmap."""

        half_period = 1.0 / max(1, self._carrier_hz * 2)
        payload = self._build_nec_payload(address, command)
        lsb_first = self._bit_order in {"lsb", "lsb_first", "least"}

        def _run(mapping, struct, bit, cfg_off, cfg_shift, dat_off):  # noqa: ANN001
            def write_ir_on(on: bool) -> None:
                # on=True => emit IR (mark). Arduino-compatible: physical HIGH.
                # active_low modules invert (rare for KY-005 style).
                physical_high = (not on) if self._active_low else on
                self._write_physical_locked(mapping, struct, bit, dat_off, physical_high)

            def busy_until(deadline: float) -> None:
                while time.perf_counter() < deadline:
                    pass

            def mark(us: int) -> None:
                end = time.perf_counter() + (us / 1_000_000.0)
                next_edge = time.perf_counter()
                carrier_on = True
                while time.perf_counter() < end:
                    write_ir_on(carrier_on)
                    next_edge += half_period
                    busy_until(min(end, next_edge))
                    carrier_on = not carrier_on
                write_ir_on(False)

            def space(us: int) -> None:
                write_ir_on(False)
                busy_until(time.perf_counter() + (us / 1_000_000.0))

            self._set_output_locked(mapping, struct, bit, cfg_off, cfg_shift, dat_off)
            # Physical LOW before/after — never leave DATA high (module heat).
            self._write_physical_locked(mapping, struct, bit, dat_off, False)
            frames = 0
            bit_range = range(0, 32) if lsb_first else range(31, -1, -1)
            try:
                for _ in range(max(1, repeat)):
                    mark(9000)
                    space(4500)
                    for bit_i in bit_range:
                        mark(560)
                        space(1690 if (payload >> bit_i) & 1 else 560)
                    mark(560)
                    space(40000)
                    frames += 1
            finally:
                self._write_physical_locked(mapping, struct, bit, dat_off, False)

            idle_level = self._read_physical_locked(mapping, struct, bit, dat_off)
            return {
                "protocol": "nec-like-38k",
                "frames": frames,
                "address": address,
                "command": command,
                "payload": f"0x{payload:08X}",
                "bit_order": "lsb" if lsb_first else "msb",
                "addr_mode": self._addr_mode,
                "soc_pin": self._pin_info["soc_pin"],
                "active_low": self._active_low,
                "carrier_hz": self._carrier_hz,
                "idle_level": idle_level,
            }

        return self._with_pio(_run)


def create_light_provider() -> LightProvider:
    provider = os.environ.get("AEGIS_ROOM_LIGHT_PROVIDER", "mock").strip().lower()
    runtime_mode = os.environ.get("AEGIS_RUNTIME_MODE", "development").strip().lower()
    if provider in {"disabled", "none", "off", "unconfigured"}:
        raise RuntimeError(
            "Room light provider is disabled/unconfigured; deploy room-server only after "
            "configuring the Orange Pi real provider."
        )
    if runtime_mode == "production" and provider in {"", "mock"}:
        raise RuntimeError(
            "AEGIS_ROOM_LIGHT_PROVIDER=mock is not allowed when AEGIS_RUNTIME_MODE=production; "
            "disable room-server or configure a real provider."
        )
    default_device_id = os.environ.get("AEGIS_ROOM_DEVICE_ID", "light-main")
    if provider == "gpio":
        return OrangePiGpioIrProvider(
            pin=os.environ.get("AEGIS_ROOM_IR_PIN", ""),
            default_device_id=default_device_id,
        )
    if runtime_mode == "production":
        raise RuntimeError(f"AEGIS_ROOM_LIGHT_PROVIDER={provider!r} is not a supported production provider.")
    return MockLightIrProvider(default_device_id=default_device_id)
