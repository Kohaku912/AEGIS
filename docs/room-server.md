# Room Server — Design & Usage

> **Status**: Phase 4.3 + Action capabilities (light, AC, IR, plug, camera, robot arm)
> **Language**: Python (AEGIS Core integration via `room_server_client.py`)

## Overview

The Room Server provides AEGIS with physical environment observation AND control capabilities.
Actions go through ToolBroker → PolicyEngine → Approval UI (for Level 2+).
Emergency stop is Level 1 (auto-allowed for safety).

## Implemented Capabilities

### Observe (Level 0 — READ_ONLY)

| Capability | Status |
|-----------|--------|
| `room.get_environment` | ✅ Mock provider |
| `room.get_temperature` | ✅ Mock provider |
| `room.get_humidity` | ✅ Mock provider |
| `room.get_brightness` | ✅ Mock provider |
| `room.get_motion_status` | ✅ Mock provider |
| `room.get_device_status` | ✅ Mock provider |
| `room.list_sensors` | ✅ Mock provider |

### Action (Level 1 — SAFE_ACTION, auto-allowed)

| Capability | Status |
|-----------|--------|
| `room.stop_robot_arm` | ✅ Mock actuator |
| `room.emergency_stop_robot_arm` | ✅ Mock actuator |

### Action (Level 2 — APPROVAL_REQUIRED)

| Capability | Status |
|-----------|--------|
| `room.set_light` | ✅ Mock actuator + Approval UI |
| `room.set_air_conditioner` | ✅ Mock actuator + Approval UI + temp range validation |
| `room.send_ir_command` | ✅ Mock actuator + Approval UI + IR allowlist |
| `room.set_smart_plug` | ✅ Mock actuator + Approval UI |
| `room.get_camera_snapshot` | ✅ Mock actuator + Approval UI |

### Explicitly Denied (Level 3)

| Capability | Reason |
|-----------|--------|
| `room.move_robot_arm` | Physical safety risk |
| `room.robot_arm_move` | Physical safety risk |
| `room.lock_door` | Physical security |
| `room.ac_power_on` | Legacy pattern — use `room.set_air_conditioner` |

## Technology Decisions

| 項目 | 選択 |
|------|------|
| Sensor provider | MockSensorProvider (CI) / optional real providers |
| Actuator provider | MockActuatorProvider (CI) / optional real providers |
| 実デバイス連携 | MQTT / Home Assistant / Serial — optional adapters |
| Robot arm | Emergency stop は即時実行、move は Level 3 deny |

## Safety Features

### IR Command Allowlist

Only pre-approved IR commands can be sent:

| Category | Allowed Commands |
|----------|-----------------|
| TV | `tv_power`, `tv_volume_up`, `tv_volume_down`, `tv_mute`, `tv_input` |
| AC | `ac_power`, `ac_cool`, `ac_heat`, `ac_dry`, `ac_fan`, `ac_temp_up`, `ac_temp_down` |
| Light | `light_power`, `light_brightness_up`, `light_brightness_down` |
| Speaker | `speaker_power`, `speaker_volume_up`, `speaker_volume_down` |

Unknown IR commands are denied at the client level.

### AC Temperature Range

| Parameter | Range |
|-----------|-------|
| Temperature | 16.0°C – 32.0°C |
| Modes | `cool`, `heat`, `dry`, `fan`, `auto` |

Out-of-range temperatures and invalid modes are denied at the client level.

### Robot Arm Safety

| Operation | Level | Behavior |
|-----------|-------|----------|
| `room.move_robot_arm` | Level 3 | **Denied** — explicit deny in PolicyEngine |
| `room.stop_robot_arm` | Level 1 | Auto-allowed — graceful stop |
| `room.emergency_stop_robot_arm` | Level 1 | Auto-allowed — immediate stop |

## Providers

### Mock Sensor Provider (CI)

Returns deterministic fake data. No real hardware.

### Mock Actuator Provider (CI)

Simulates all actuator operations. Returns deterministic fake results.
All calls are logged to `call_log` for audit verification.

### Real Providers (optional — user confirmation required)

| Provider | Status | Notes |
|----------|--------|-------|
| MqttActuatorProvider | Not implemented | Requires MQTT broker |
| HomeAssistantAdapter | Not implemented | Requires HA installation |
| SerialArduinoAdapter | Not implemented | Requires Arduino/ESP32 firmware |
| RobotArmAdapter | Not implemented | Dedicated robot arm controller |
| CameraProvider | Not implemented | Camera hardware |

## Testing

```bash
cd ai-server

# Observe E2E
pytest tests/test_room_observe_e2e.py -v

# Action E2E
pytest tests/test_room_action_e2e.py -v

# All Room tests
pytest tests/test_room_observe_e2e.py tests/test_room_action_e2e.py -v
```
