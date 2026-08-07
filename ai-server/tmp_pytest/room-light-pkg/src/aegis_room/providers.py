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
        ir_event = self.send_ir_command("light", resolved_ir or format_ir_code("all" if power_on else "off"), 1)
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


class OrangePiGpioIrProvider(MockLightIrProvider):
    """Orange Pi GPIO IR skeleton.

    The real carrier/waveform implementation is intentionally isolated here.
    Until the target GPIO library and IR code format are finalized, this class
    validates configuration and records the requested command.
    """

    provider_name = "orangepi-gpio"

    def __init__(self, pin: str, default_device_id: str = "light-main") -> None:
        if not pin:
            raise RuntimeError("AEGIS_ROOM_IR_PIN is required when AEGIS_ROOM_LIGHT_PROVIDER=gpio")
        super().__init__(default_device_id=default_device_id)
        self.pin = pin
        self._gpio_available = self._detect_gpio_library()

    def _detect_gpio_library(self) -> bool:
        try:
            __import__("OPi.GPIO")
            return True
        except Exception:
            return False

    def send_ir_command(self, device_type: str, ir_code: str, repeat: int) -> dict[str, Any]:
        event = super().send_ir_command(device_type, ir_code, repeat)
        event["mock"] = False
        event["pin"] = self.pin
        event["gpio_available"] = self._gpio_available
        if not self._gpio_available:
            event["warning"] = "OPi.GPIO is not installed; IR command was recorded but not sent"
            return event
        try:
            event["tx"] = self._transmit_nec(int(event["address"]), int(event["command"]), repeat)
        except Exception as exc:
            event["warning"] = f"IR transmit failed: {exc}"
        return event

    def _transmit_nec(self, address: int, command: int, repeat: int) -> dict[str, Any]:
        """Best-effort NEC-like bit bang. Timing may need calibration on hardware."""
        import OPi.GPIO as GPIO  # type: ignore

        pin = int(self.pin) if str(self.pin).isdigit() else self.pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        def mark(us: int) -> None:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(us / 1_000_000)

        def space(us: int) -> None:
            GPIO.output(pin, GPIO.LOW)
            time.sleep(us / 1_000_000)

        # Pack address (16-bit) + command (8-bit) + inverted command.
        payload = ((address & 0xFFFF) << 16) | ((command & 0xFF) << 8) | ((~command) & 0xFF)
        frames = 0
        for _ in range(max(1, repeat)):
            mark(9000)
            space(4500)
            for bit in range(31, -1, -1):
                mark(560)
                space(1690 if (payload >> bit) & 1 else 560)
            mark(560)
            space(40000)
            frames += 1
        GPIO.output(pin, GPIO.LOW)
        return {"protocol": "nec-like", "frames": frames, "address": address, "command": command}


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
