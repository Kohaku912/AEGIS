# Room Server — AGENTS.md

## Purpose

The Room Server handles **IoT and sensor operations** for AEGIS:
- Environment monitoring (temperature, humidity, brightness)
- Motion detection
- Device control (lights, AC, smart plugs)
- IR command sending
- Robot arm control (with approval)

## Technology Stack

- **Language**: Python
- **Framework**: gRPC service with mock/GPIO providers
- **Port**: 50055 (gRPC)
- **Testing**: pytest

## Directory Structure

```
room-server/
├── src/
│   ├── main.py           # Entry point
│   ├── mqtt_provider.py  # MQTT sensor provider
│   ├── capabilities/
│   │   ├── environment.py    # Environment sensors
│   │   ├── motion.py         # Motion detection
│   │   ├── devices.py        # Device control
│   │   └── robot_arm.py      # Robot arm control
│   └── safety.py         # Safety boundaries
├── tests/                # Test files
└── requirements.txt      # Dependencies
```

## Key Components

### Providers (`src/providers.py` / GPIO path)

**Features**:
- Mock-first sensor/actuator behavior
- Optional GPIO light path when `AEGIS_ROOM_LIGHT_PROVIDER=gpio`
- No MQTT provider is present in the current runtime

### Capabilities

**Observe (L0)**:
- `get_environment()` — Get temperature, humidity, brightness
- `get_motion()` — Get motion detection status
- `get_device_status()` — Get device status
- `list_sensors()` — List available sensors

**Safety (L1)**:
- `stop_robot_arm()` — Emergency stop
- `emergency_stop_robot_arm()` — Emergency stop (always allowed)

**Approval (L2)**:
- `set_light(state)` — Control lights
- `set_air_conditioner(settings)` — Control AC
- `send_ir_command(command)` — Send IR command
- `set_smart_plug(state)` — Control smart plug
- `get_camera_snapshot()` — Get camera image

**Blocked**:
- Robot arm movement (Level 3, denied by default)

## Safety Model

| Level | Operations | Approval |
|-------|-----------|----------|
| L0 | Environment, motion, sensors | Auto-allowed |
| L1 | Emergency stop | Immediate |
| L2 | Lights, AC, IR, smart plug, camera | Requires approval |
| L3 | Robot arm movement | Denied by default |

## Key Design Decisions

1. **gRPC primary**: The runtime is a Python gRPC service
2. **Mock-first providers**: CI uses mock providers; GPIO is optional
3. **Safety levels**: Graduated safety model
4. **Emergency stop**: Always allowed regardless of approval
5. **Robot arm blocked**: Level 3 operations denied by default
