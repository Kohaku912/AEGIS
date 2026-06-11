"""Room Server Client — Python adapter for Room Server integration with AEGIS Core.

This module bridges the Room Server with AEGIS Core's Python modules.
It provides:
- Capability registration with ToolRegistry (observe + action)
- Event push to EventBus (sensor readings, motion, device status, actions)
- Mock sensor/actuator provider for CI testing
- Real provider interface (MQTT/HA/Serial adapters — optional)
- Retry/backoff when AEGIS Core is unavailable
- Graceful failure when sensors/actuators are unavailable
- Threshold-based event filtering
- IR command allowlist
- AC temperature range validation

Architecture reference: docs/architecture.md §3.5, §4
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Protocol

from aegis_schema.models import (
    Capability,
    Event,
    EventPriority,
    RiskLevel,
    ServerInfo,
    ServerStatus,
    ServerType,
)

logger = logging.getLogger("aegis.room_server_client")


# ═══════════════════════════════════════════════════════════════
# Safety Constants — IR allowlist, AC range, etc.
# ═══════════════════════════════════════════════════════════════

# IR commands that are allowed (Pronto hex format or custom codes)
ALLOWED_IR_COMMANDS: set[str] = {
    "tv_power",
    "tv_volume_up",
    "tv_volume_down",
    "tv_mute",
    "tv_input",
    "ac_power",
    "ac_cool",
    "ac_heat",
    "ac_dry",
    "ac_fan",
    "ac_temp_up",
    "ac_temp_down",
    "light_power",
    "light_brightness_up",
    "light_brightness_down",
    "speaker_power",
    "speaker_volume_up",
    "speaker_volume_down",
}

# AC temperature range (Celsius)
AC_TEMP_MIN = 16.0
AC_TEMP_MAX = 32.0

# AC valid modes
AC_VALID_MODES = {"cool", "heat", "dry", "fan", "auto"}


# ═══════════════════════════════════════════════════════════════
# Sensor Provider Protocol
# ═══════════════════════════════════════════════════════════════


class SensorProvider(Protocol):
    """Protocol for room sensor providers (read-only)."""

    def get_temperature(self) -> dict[str, Any]: ...

    def get_humidity(self) -> dict[str, Any]: ...

    def get_brightness(self) -> dict[str, Any]: ...

    def get_motion_status(self) -> dict[str, Any]: ...

    def get_environment(self) -> dict[str, Any]: ...

    def get_device_status(self, device_ids: list[str] | None = None) -> list[dict[str, Any]]: ...

    def list_sensors(self) -> list[dict[str, Any]]: ...

    def is_available(self) -> bool: ...


# ═══════════════════════════════════════════════════════════════
# Actuator Provider Protocol — for physical device control
# ═══════════════════════════════════════════════════════════════


class ActuatorProvider(Protocol):
    """Protocol for room actuator providers (write/control).

    Real implementations:
    - MqttActuatorProvider (MQTT broker)
    - HomeAssistantAdapter (Home Assistant API)
    - SerialArduinoAdapter (Arduino/ESP32 serial)
    - RobotArmAdapter (dedicated robot arm controller)
    - CameraProvider (camera hardware)

    All methods return {success: bool, ...} dicts.
    """

    def set_light(
        self,
        device_id: str,
        power_on: bool,
        brightness: int = -1,
        color_temp_k: int = 0,
        color_rgb: str = "",
    ) -> dict[str, Any]:
        """Control a light. Returns {success, device_id, state}."""
        ...

    def set_air_conditioner(
        self,
        device_id: str,
        power_on: bool,
        target_temperature_c: float = -1,
        mode: str = "",
        fan_speed: int = 0,
    ) -> dict[str, Any]:
        """Control an AC unit. Returns {success, device_id, state}."""
        ...

    def send_ir_command(self, device_type: str, ir_code: str, repeat: int = 1) -> dict[str, Any]:
        """Send an IR command. Returns {success, device_type, ir_code}."""
        ...

    def set_smart_plug(self, device_id: str, power_on: bool) -> dict[str, Any]:
        """Control a smart plug. Returns {success, device_id, state}."""
        ...

    def get_camera_snapshot(
        self,
        camera_id: str = "",
        format: str = "jpeg",
        quality: int = 80,
        max_width: int = 0,
        max_height: int = 0,
    ) -> dict[str, Any]:
        """Capture a camera snapshot. Returns {success, image_base64, width, height}."""
        ...

    def move_robot_arm(self, arm_id: str, target_position_json: str, speed_pct: int = 50) -> dict[str, Any]:
        """Move robot arm. Returns {success, arm_id}."""
        ...

    def stop_robot_arm(self, arm_id: str = "") -> dict[str, Any]:
        """Stop robot arm (graceful). Returns {success, stopped_arms}."""
        ...

    def emergency_stop_robot_arm(self, arm_id: str = "") -> dict[str, Any]:
        """Emergency stop robot arm (immediate). Returns {success, stopped_arms}."""
        ...

    def is_available(self) -> bool:
        """Check if actuators are reachable."""
        ...


# ═══════════════════════════════════════════════════════════════
# Threshold Config
# ═══════════════════════════════════════════════════════════════


@dataclass
class SensorThresholds:
    """Thresholds for triggering sensor change events."""

    temperature_delta_c: float = 1.0
    humidity_delta_pct: float = 5.0
    brightness_delta_lux: float = 50.0
    motion_cooldown_seconds: float = 120.0


# ═══════════════════════════════════════════════════════════════
# Mock Sensor Provider — for CI testing (no real hardware)
# ═══════════════════════════════════════════════════════════════


class MockSensorProvider:
    """Mock sensor provider for CI testing. Returns deterministic fake data."""

    def __init__(self, available: bool = True) -> None:
        self._available = available
        self.call_log: list[tuple[str, dict[str, Any]]] = []
        self._mock_temp = 22.5
        self._mock_humidity = 45.0
        self._mock_brightness = 300.0
        self._mock_motion = False

    def set_mock_values(
        self,
        temperature_c: float | None = None,
        humidity_pct: float | None = None,
        brightness_lux: float | None = None,
        motion_detected: bool | None = None,
    ) -> None:
        if temperature_c is not None:
            self._mock_temp = temperature_c
        if humidity_pct is not None:
            self._mock_humidity = humidity_pct
        if brightness_lux is not None:
            self._mock_brightness = brightness_lux
        if motion_detected is not None:
            self._mock_motion = motion_detected

    def get_temperature(self) -> dict[str, Any]:
        self.call_log.append(("get_temperature", {}))
        return {"temperature_c": self._mock_temp, "timestamp_ms": int(time.time() * 1000)}

    def get_humidity(self) -> dict[str, Any]:
        self.call_log.append(("get_humidity", {}))
        return {"humidity_pct": self._mock_humidity, "timestamp_ms": int(time.time() * 1000)}

    def get_brightness(self) -> dict[str, Any]:
        self.call_log.append(("get_brightness", {}))
        return {"brightness_lux": self._mock_brightness, "timestamp_ms": int(time.time() * 1000)}

    def get_motion_status(self) -> dict[str, Any]:
        self.call_log.append(("get_motion_status", {}))
        return {
            "motion_detected": self._mock_motion,
            "motion_zone": "living_room" if self._mock_motion else "",
            "timestamp_ms": int(time.time() * 1000),
        }

    def get_environment(self) -> dict[str, Any]:
        self.call_log.append(("get_environment", {}))
        return {
            "temperature_c": self._mock_temp,
            "humidity_pct": self._mock_humidity,
            "brightness_lux": self._mock_brightness,
            "motion_detected": self._mock_motion,
            "motion_zone": "living_room" if self._mock_motion else "",
            "timestamp_ms": int(time.time() * 1000),
        }

    def get_device_status(self, device_ids: list[str] | None = None) -> list[dict[str, Any]]:
        self.call_log.append(("get_device_status", {"device_ids": device_ids}))
        devices = [
            {
                "device_id": "sensor-temp-001",
                "device_type": "sensor",
                "state_json": json.dumps({"value": self._mock_temp, "unit": "°C"}),
                "online": True,
                "last_seen_ms": int(time.time() * 1000),
            },
            {
                "device_id": "sensor-humidity-001",
                "device_type": "sensor",
                "state_json": json.dumps({"value": self._mock_humidity, "unit": "%"}),
                "online": True,
                "last_seen_ms": int(time.time() * 1000),
            },
            {
                "device_id": "sensor-motion-001",
                "device_type": "sensor",
                "state_json": json.dumps({"motion": self._mock_motion}),
                "online": True,
                "last_seen_ms": int(time.time() * 1000),
            },
        ]
        return [d for d in devices if d["device_id"] in device_ids] if device_ids else devices

    def list_sensors(self) -> list[dict[str, Any]]:
        self.call_log.append(("list_sensors", {}))
        return [
            {"sensor_id": "sensor-temp-001", "sensor_type": "temperature", "unit": "°C", "online": True},
            {"sensor_id": "sensor-humidity-001", "sensor_type": "humidity", "unit": "%", "online": True},
            {"sensor_id": "sensor-brightness-001", "sensor_type": "brightness", "unit": "lux", "online": True},
            {"sensor_id": "sensor-motion-001", "sensor_type": "motion", "unit": "bool", "online": True},
        ]

    def is_available(self) -> bool:
        return self._available


# ═══════════════════════════════════════════════════════════════
# Mock Actuator Provider — for CI testing (no real hardware)
# ═══════════════════════════════════════════════════════════════


class MockActuatorProvider:
    """Mock actuator provider for CI testing. Returns deterministic fake data.

    NEVER controls real hardware. All operations are simulated.
    """

    def __init__(self, available: bool = True) -> None:
        self._available = available
        self.call_log: list[tuple[str, dict[str, Any]]] = []
        self._lights: dict[str, dict[str, Any]] = {}
        self._acs: dict[str, dict[str, Any]] = {}
        self._plugs: dict[str, dict[str, Any]] = {}
        self._robot_arm_stopped = False

    def set_light(
        self,
        device_id: str,
        power_on: bool,
        brightness: int = -1,
        color_temp_k: int = 0,
        color_rgb: str = "",
    ) -> dict[str, Any]:
        self.call_log.append(
            (
                "set_light",
                {
                    "device_id": device_id,
                    "power_on": power_on,
                    "brightness": brightness,
                    "color_temp_k": color_temp_k,
                    "color_rgb": color_rgb,
                },
            )
        )
        state = {"power_on": power_on, "brightness": brightness, "color_temp_k": color_temp_k, "color_rgb": color_rgb}
        self._lights[device_id] = state
        return {"success": True, "device_id": device_id, "state": state}

    def set_air_conditioner(
        self,
        device_id: str,
        power_on: bool,
        target_temperature_c: float = -1,
        mode: str = "",
        fan_speed: int = 0,
    ) -> dict[str, Any]:
        self.call_log.append(
            (
                "set_air_conditioner",
                {
                    "device_id": device_id,
                    "power_on": power_on,
                    "target_temperature_c": target_temperature_c,
                    "mode": mode,
                    "fan_speed": fan_speed,
                },
            )
        )
        state = {
            "power_on": power_on,
            "target_temperature_c": target_temperature_c,
            "mode": mode,
            "fan_speed": fan_speed,
        }
        self._acs[device_id] = state
        return {"success": True, "device_id": device_id, "state": state}

    def send_ir_command(self, device_type: str, ir_code: str, repeat: int = 1) -> dict[str, Any]:
        self.call_log.append(
            (
                "send_ir_command",
                {
                    "device_type": device_type,
                    "ir_code": ir_code,
                    "repeat": repeat,
                },
            )
        )
        return {"success": True, "device_type": device_type, "ir_code": ir_code}

    def set_smart_plug(self, device_id: str, power_on: bool) -> dict[str, Any]:
        self.call_log.append(("set_smart_plug", {"device_id": device_id, "power_on": power_on}))
        self._plugs[device_id] = {"power_on": power_on}
        return {"success": True, "device_id": device_id, "state": {"power_on": power_on}}

    def get_camera_snapshot(
        self,
        camera_id: str = "",
        format: str = "jpeg",
        quality: int = 80,
        max_width: int = 0,
        max_height: int = 0,
    ) -> dict[str, Any]:
        self.call_log.append(
            (
                "get_camera_snapshot",
                {
                    "camera_id": camera_id,
                    "format": format,
                    "quality": quality,
                },
            )
        )
        return {
            "success": True,
            "image_base64": "[MOCK_CAMERA_SNAPSHOT]",
            "width": 640,
            "height": 480,
            "format": format,
            "captured_ms": int(time.time() * 1000),
        }

    def move_robot_arm(self, arm_id: str, target_position_json: str, speed_pct: int = 50) -> dict[str, Any]:
        self.call_log.append(
            (
                "move_robot_arm",
                {
                    "arm_id": arm_id,
                    "target_position_json": target_position_json,
                    "speed_pct": speed_pct,
                },
            )
        )
        return {"success": True, "arm_id": arm_id}

    def stop_robot_arm(self, arm_id: str = "") -> dict[str, Any]:
        self.call_log.append(("stop_robot_arm", {"arm_id": arm_id}))
        self._robot_arm_stopped = True
        return {"success": True, "stopped_arms": [arm_id] if arm_id else ["all"]}

    def emergency_stop_robot_arm(self, arm_id: str = "") -> dict[str, Any]:
        self.call_log.append(("emergency_stop_robot_arm", {"arm_id": arm_id}))
        self._robot_arm_stopped = True
        return {"success": True, "stopped_arms": [arm_id] if arm_id else ["all"]}

    def is_available(self) -> bool:
        return self._available


# ═══════════════════════════════════════════════════════════════
# Connection State & Retry
# ═══════════════════════════════════════════════════════════════


class ConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    FAILED = auto()


@dataclass
class RetryConfig:
    max_retries: int = 5
    base_delay_ms: int = 100
    max_delay_ms: int = 30_000
    backoff_factor: float = 2.0


@dataclass
class ConnectionStats:
    state: ConnectionState = ConnectionState.DISCONNECTED
    retry_count: int = 0
    last_error: str = ""
    last_connected_at_ms: int = 0
    last_attempt_at_ms: int = 0
    total_registrations: int = 0
    total_events_pushed: int = 0


# ═══════════════════════════════════════════════════════════════
# Room Server Capabilities — Observe + Action
# ═══════════════════════════════════════════════════════════════

ROOM_SERVER_ID = "room-server-main"

ROOM_CAPABILITIES: list[Capability] = [
    # ── Observe (Level 0) ──
    Capability(
        id="room.get_environment",
        name="Get Environment",
        description="Read all environment sensors (temperature, humidity, brightness, motion) at once.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.READ_ONLY,
        tags=["environment", "sensor", "observe", "read_only"],
        timeout_ms=3000,
    ),
    Capability(
        id="room.get_temperature",
        name="Get Temperature",
        description="Read the current temperature in Celsius.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.READ_ONLY,
        tags=["temperature", "sensor", "observe", "read_only"],
        timeout_ms=1000,
    ),
    Capability(
        id="room.get_humidity",
        name="Get Humidity",
        description="Read the current humidity percentage.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.READ_ONLY,
        tags=["humidity", "sensor", "observe", "read_only"],
        timeout_ms=1000,
    ),
    Capability(
        id="room.get_brightness",
        name="Get Brightness",
        description="Read the current ambient brightness in lux.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.READ_ONLY,
        tags=["brightness", "sensor", "observe", "read_only"],
        timeout_ms=1000,
    ),
    Capability(
        id="room.get_motion_status",
        name="Get Motion Status",
        description="Check if motion is currently detected and in which zone.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.READ_ONLY,
        tags=["motion", "sensor", "observe", "read_only"],
        timeout_ms=1000,
    ),
    Capability(
        id="room.get_device_status",
        name="Get Device Status",
        description="Get the status of room devices (sensors, actuators).",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.READ_ONLY,
        tags=["device", "status", "observe", "read_only"],
        timeout_ms=2000,
    ),
    Capability(
        id="room.list_sensors",
        name="List Sensors",
        description="List all available room sensors with their types and status.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.READ_ONLY,
        tags=["sensor", "list", "observe", "read_only"],
        timeout_ms=1000,
    ),
    # ── Action Level 1 (auto-allowed) ──
    Capability(
        id="room.stop_robot_arm",
        name="Stop Robot Arm",
        description="Stop robot arm gracefully (not emergency).",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["robot_arm", "action", "safety"],
        timeout_ms=2000,
    ),
    Capability(
        id="room.emergency_stop_robot_arm",
        name="Emergency Stop Robot Arm",
        description="Emergency stop all robot arm movement immediately.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["robot_arm", "action", "safety", "emergency"],
        timeout_ms=1000,
    ),
    # ── Action Level 2 (approval required) ──
    Capability(
        id="room.set_light",
        name="Set Light",
        description="Control a room light (power, brightness, color). Requires approval.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["light_control"],
        tags=["light", "action", "approval_required"],
        timeout_ms=3000,
    ),
    Capability(
        id="room.set_air_conditioner",
        name="Set Air Conditioner",
        description="Control AC (power, temperature, mode, fan). Requires approval. Temp range: 16-32°C.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["ac_control"],
        tags=["ac", "action", "approval_required"],
        timeout_ms=3000,
    ),
    Capability(
        id="room.send_ir_command",
        name="Send IR Command",
        description="Send an IR command to a device. Allowlisted commands only. Requires approval.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["ir_transmission"],
        tags=["ir", "action", "approval_required"],
        timeout_ms=2000,
    ),
    Capability(
        id="room.set_smart_plug",
        name="Set Smart Plug",
        description="Control a smart plug (on/off). Requires approval.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["plug_control"],
        tags=["plug", "action", "approval_required"],
        timeout_ms=2000,
    ),
    Capability(
        id="room.get_camera_snapshot",
        name="Get Camera Snapshot",
        description="Capture a snapshot from a room camera. Requires approval.",
        server_type=ServerType.ROOM,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["camera_capture"],
        tags=["camera", "action", "approval_required"],
        timeout_ms=5000,
    ),
]


def get_room_server_info() -> ServerInfo:
    """Create ServerInfo for the Room Server."""
    return ServerInfo(
        server_id=ROOM_SERVER_ID,
        server_type=ServerType.ROOM,
        version="0.2.0",
        status=ServerStatus.ONLINE,
        capability_ids=[cap.id for cap in ROOM_CAPABILITIES],
        host="localhost",
        port=50054,
        started_at_ms=int(time.time() * 1000),
    )


# ═══════════════════════════════════════════════════════════════
# Room Server Client — main integration point
# ═══════════════════════════════════════════════════════════════


class RoomServerClient:
    """Python client that integrates Room Server with AEGIS Core.

    Responsibilities:
    1. Register Room capabilities with ToolRegistry
    2. Push Room events to EventBus
    3. Handle connection state and retry/backoff
    4. Graceful failure when sensors/actuators are unavailable
    5. Threshold-based event filtering
    6. Invoke capabilities through ToolBroker (with PolicyEngine enforcement)
    7. Push action result events to EventBus
    8. Validate AC temperature range and IR allowlist
    """

    def __init__(
        self,
        event_bus: Any,
        registry: Any,
        sensor_provider: SensorProvider | None = None,
        actuator_provider: ActuatorProvider | None = None,
        retry_config: RetryConfig | None = None,
        thresholds: SensorThresholds | None = None,
        tool_broker: Any = None,
    ) -> None:
        self._event_bus = event_bus
        self._registry = registry
        self._sensor_provider = sensor_provider or MockSensorProvider()
        self._actuator_provider = actuator_provider or MockActuatorProvider()
        self._retry = retry_config or RetryConfig()
        self._stats = ConnectionStats()
        self._registered = False
        self._thresholds = thresholds or SensorThresholds()
        self._tool_broker = tool_broker

        # Last known values for threshold comparison
        self._last_temp: float | None = None
        self._last_humidity: float | None = None
        self._last_brightness: float | None = None
        self._last_motion: bool = False
        self._last_motion_event_ms: int = 0

    @property
    def stats(self) -> ConnectionStats:
        return self._stats

    @property
    def is_registered(self) -> bool:
        return self._registered

    @property
    def thresholds(self) -> SensorThresholds:
        return self._thresholds

    @property
    def sensor_provider(self) -> Any:
        return self._sensor_provider

    @property
    def actuator_provider(self) -> Any:
        return self._actuator_provider

    # ── Registration ─────────────────────────────────────────

    def register(self) -> bool:
        """Register Room Server and its capabilities with AEGIS Core."""
        if not self._sensor_provider.is_available():
            self._stats.state = ConnectionState.FAILED
            self._stats.last_error = "Room sensors are not available"
            logger.warning("Room sensors not available — skipping registration")
            return False

        try:
            server_info = get_room_server_info()
            self._registry.register_server(server_info)
            for cap in ROOM_CAPABILITIES:
                self._registry.register_capability(cap)

            self._registered = True
            self._stats.state = ConnectionState.CONNECTED
            self._stats.total_registrations = len(ROOM_CAPABILITIES)
            self._stats.last_connected_at_ms = int(time.time() * 1000)
            logger.info("Room Server registered %d capabilities", len(ROOM_CAPABILITIES))
            return True

        except Exception as e:
            self._stats.state = ConnectionState.FAILED
            self._stats.last_error = str(e)
            logger.error("Room Server registration failed: %s", e)
            return False

    def unregister(self) -> None:
        """Unregister Room Server from AEGIS Core."""
        self._registry.unregister_server(ROOM_SERVER_ID)
        for cap in ROOM_CAPABILITIES:
            self._registry.unregister_capability(cap.id)
        self._registered = False
        self._stats.state = ConnectionState.DISCONNECTED

    # ── Event Push ───────────────────────────────────────────

    def push_event(self, event: Event) -> bool:
        """Push an event to the EventBus."""
        if not self._registered:
            logger.warning("Cannot push event — Room Server not registered")
            return False
        try:
            result = self._event_bus.publish(event)
            if result:
                self._stats.total_events_pushed += 1
            return result
        except Exception as e:
            self._stats.last_error = str(e)
            logger.error("Failed to push event: %s", e)
            return False

    def push_action_result_event(
        self,
        capability_id: str,
        success: bool,
        output: dict[str, Any] | None = None,
        error: str = "",
        *,
        severity: int = 2,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """Push a room.action_completed or room.action_failed event."""
        event_type = "room.action_completed" if success else "room.action_failed"
        payload = json.dumps(
            {
                "capability_id": capability_id,
                "success": success,
                "output": output or {},
                "error": error,
                "timestamp_ms": int(time.time() * 1000),
            }
        )
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            source_server_type=ServerType.ROOM,
            source_server_id=ROOM_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=payload,
            severity=severity,
            priority=priority,
            dedupe_key=f"{event_type}:{capability_id}:{success}",
        )
        return self.push_event(event)

    def push_environment_event(
        self,
        environment: dict[str, Any],
        *,
        severity: int = 2,
        priority: EventPriority = EventPriority.BACKGROUND,
    ) -> bool:
        """Push a room.environment_updated event."""
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="room.environment_updated",
            source_server_type=ServerType.ROOM,
            source_server_id=ROOM_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=json.dumps(environment),
            severity=severity,
            priority=priority,
            dedupe_key="room.environment_updated",
        )
        return self.push_event(event)

    def push_temperature_event(
        self,
        temperature_c: float,
        *,
        severity: int = 3,
        priority: EventPriority = EventPriority.BACKGROUND,
    ) -> bool:
        """Push a room.temperature_changed event."""
        payload = json.dumps({"temperature_c": temperature_c, "timestamp_ms": int(time.time() * 1000)})
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="room.temperature_changed",
            source_server_type=ServerType.ROOM,
            source_server_id=ROOM_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=payload,
            severity=severity,
            priority=priority,
            dedupe_key=f"room.temperature_changed:{temperature_c:.1f}",
        )
        return self.push_event(event)

    def push_motion_event(
        self,
        motion_detected: bool,
        motion_zone: str = "",
        *,
        severity: int = 4,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """Push a room.motion_detected event."""
        payload = json.dumps(
            {"motion_detected": motion_detected, "motion_zone": motion_zone, "timestamp_ms": int(time.time() * 1000)}
        )
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="room.motion_detected",
            source_server_type=ServerType.ROOM,
            source_server_id=ROOM_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=payload,
            severity=severity,
            priority=priority,
            dedupe_key=f"room.motion_detected:{motion_zone}:{motion_detected}",
        )
        return self.push_event(event)

    def push_sensor_unavailable_event(
        self,
        sensor_id: str,
        reason: str = "",
        *,
        severity: int = 7,
        priority: EventPriority = EventPriority.URGENT,
    ) -> bool:
        """Push a room.sensor_unavailable event (wakes AI)."""
        payload = json.dumps({"sensor_id": sensor_id, "reason": reason, "timestamp_ms": int(time.time() * 1000)})
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="room.sensor_unavailable",
            source_server_type=ServerType.ROOM,
            source_server_id=ROOM_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=payload,
            severity=severity,
            priority=priority,
            dedupe_key=f"room.sensor_unavailable:{sensor_id}",
        )
        return self.push_event(event)

    # ── Poll and Push ────────────────────────────────────────

    def poll_and_push(self) -> dict[str, bool]:
        """Read sensors and push events only if thresholds are exceeded."""
        results: dict[str, bool] = {}

        if not self._sensor_provider.is_available():
            self.push_sensor_unavailable_event("all", "Provider unavailable")
            return {"sensor_unavailable": True}

        try:
            env = self._sensor_provider.get_environment()
        except Exception as e:
            self.push_sensor_unavailable_event("all", str(e))
            return {"sensor_unavailable": True}

        now_ms = int(time.time() * 1000)

        temp = env.get("temperature_c", 0.0)
        if self._last_temp is None or abs(temp - self._last_temp) >= self._thresholds.temperature_delta_c:
            results["temperature_changed"] = self.push_temperature_event(temp)
            self._last_temp = temp

        humidity = env.get("humidity_pct", 0.0)
        if self._last_humidity is None or abs(humidity - self._last_humidity) >= self._thresholds.humidity_delta_pct:
            results["humidity_changed"] = self.push_environment_event(env)
            self._last_humidity = humidity

        brightness = env.get("brightness_lux", 0.0)
        if self._last_brightness is None:
            results["brightness_changed"] = self.push_environment_event(env)
            self._last_brightness = brightness
        elif abs(brightness - self._last_brightness) >= self._thresholds.brightness_delta_lux:
            results["brightness_changed"] = self.push_environment_event(env)
            self._last_brightness = brightness

        motion = env.get("motion_detected", False)
        if motion and not self._last_motion:
            elapsed_s = (now_ms - self._last_motion_event_ms) / 1000.0
            if elapsed_s >= self._thresholds.motion_cooldown_seconds or self._last_motion_event_ms == 0:
                results["motion_detected"] = self.push_motion_event(motion, env.get("motion_zone", ""))
                self._last_motion_event_ms = now_ms
        self._last_motion = motion

        return results

    # ── Capability Invocation ────────────────────────────────

    def invoke_capability(self, capability_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Invoke a Room capability via the appropriate provider (for testing)."""
        if not self._sensor_provider.is_available():
            return {"error": "Room sensors are not available", "capability_id": capability_id}

        params = params or {}
        try:
            # ── Observe ──
            if capability_id == "room.get_environment":
                return self._sensor_provider.get_environment()
            elif capability_id == "room.get_temperature":
                return self._sensor_provider.get_temperature()
            elif capability_id == "room.get_humidity":
                return self._sensor_provider.get_humidity()
            elif capability_id == "room.get_brightness":
                return self._sensor_provider.get_brightness()
            elif capability_id == "room.get_motion_status":
                return self._sensor_provider.get_motion_status()
            elif capability_id == "room.get_device_status":
                return {"devices": self._sensor_provider.get_device_status(params.get("device_ids"))}
            elif capability_id == "room.list_sensors":
                return {"sensors": self._sensor_provider.list_sensors()}

            # ── Light ──
            elif capability_id == "room.set_light":
                return self._actuator_provider.set_light(
                    params["device_id"],
                    params.get("power_on", True),
                    params.get("brightness", -1),
                    params.get("color_temp_k", 0),
                    params.get("color_rgb", ""),
                )

            # ── AC ──
            elif capability_id == "room.set_air_conditioner":
                target_temp = params.get("target_temperature_c", -1)
                if target_temp != -1 and not (AC_TEMP_MIN <= target_temp <= AC_TEMP_MAX):
                    return {"error": f"Temperature {target_temp}°C out of range ({AC_TEMP_MIN}-{AC_TEMP_MAX}°C)"}
                mode = params.get("mode", "")
                if mode and mode not in AC_VALID_MODES:
                    return {"error": f"Invalid AC mode '{mode}'. Valid: {AC_VALID_MODES}"}
                return self._actuator_provider.set_air_conditioner(
                    params["device_id"],
                    params.get("power_on", True),
                    target_temp,
                    mode,
                    params.get("fan_speed", 0),
                )

            # ── IR ──
            elif capability_id == "room.send_ir_command":
                ir_code = params.get("ir_code", "")
                if ir_code not in ALLOWED_IR_COMMANDS:
                    return {"error": f"IR command '{ir_code}' not in allowlist", "allowed": list(ALLOWED_IR_COMMANDS)}
                return self._actuator_provider.send_ir_command(
                    params.get("device_type", "other"),
                    ir_code,
                    params.get("repeat", 1),
                )

            # ── Smart Plug ──
            elif capability_id == "room.set_smart_plug":
                return self._actuator_provider.set_smart_plug(params["device_id"], params.get("power_on", True))

            # ── Camera ──
            elif capability_id == "room.get_camera_snapshot":
                return self._actuator_provider.get_camera_snapshot(
                    params.get("camera_id", ""),
                    params.get("format", "jpeg"),
                    params.get("quality", 80),
                    params.get("max_width", 0),
                    params.get("max_height", 0),
                )

            # ── Robot Arm ──
            elif capability_id == "room.move_robot_arm":
                return {"error": "room.move_robot_arm is Level 3 — denied by default", "capability_id": capability_id}

            elif capability_id == "room.stop_robot_arm":
                return self._actuator_provider.stop_robot_arm(params.get("arm_id", ""))

            elif capability_id == "room.emergency_stop_robot_arm":
                return self._actuator_provider.emergency_stop_robot_arm(params.get("arm_id", ""))

            else:
                return {"error": f"Unknown capability: {capability_id}"}
        except KeyError as e:
            return {"error": f"Missing required parameter: {e}", "capability_id": capability_id}
        except Exception as e:
            return {"error": str(e), "capability_id": capability_id}

    # ── Retry / Backoff ──────────────────────────────────────

    def connect_with_retry(self) -> bool:
        """Attempt to connect to Room Server with exponential backoff."""
        delay_ms = self._retry.base_delay_ms
        for attempt in range(self._retry.max_retries):
            self._stats.retry_count = attempt + 1
            self._stats.last_attempt_at_ms = int(time.time() * 1000)
            self._stats.state = ConnectionState.CONNECTING
            if self._sensor_provider.is_available():
                if self.register():
                    return True
            time.sleep(delay_ms / 1000.0)
            delay_ms = min(delay_ms * self._retry.backoff_factor, self._retry.max_delay_ms)
        self._stats.state = ConnectionState.FAILED
        self._stats.last_error = f"Failed to connect after {self._retry.max_retries} attempts"
        return False
