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
    ) -> LightState:
        device_id = device_id or "light-main"
        state = LightState(
            device_id=device_id,
            power_on=power_on,
            brightness=brightness,
            color_temp_k=color_temp_k,
            color_rgb=color_rgb,
            ir_code=ir_code,
            provider=self.provider_name,
        )
        self._states[device_id] = state
        self.ir_log.append(
            {
                "device_type": "light",
                "device_id": device_id,
                "ir_code": ir_code or ("light_power_on" if power_on else "light_power_off"),
                "repeat": 1,
                "timestamp_ms": state.updated_at_ms,
                "mock": True,
            }
        )
        return state

    def send_ir_command(self, device_type: str, ir_code: str, repeat: int) -> dict[str, Any]:
        event = {
            "device_type": device_type or "other",
            "ir_code": ir_code,
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
        event["pin"] = self.pin
        event["gpio_available"] = self._gpio_available
        if not self._gpio_available:
            event["warning"] = "OPi.GPIO is not installed; IR command was recorded but not sent"
        return event


def create_light_provider() -> LightProvider:
    provider = os.environ.get("AEGIS_ROOM_LIGHT_PROVIDER", "mock").strip().lower()
    runtime_mode = os.environ.get("AEGIS_RUNTIME_MODE", "development").strip().lower()
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
    return MockLightIrProvider(default_device_id=default_device_id)
