# Room Server — Safety & Privacy

> **Status**: Phase 4.3 + Action capabilities
> **Related**: `docs/room-server.md`, `docs/architecture.md` §7

## Safety Level Classification

### Level 0 — READ_ONLY (auto-allowed)

| Capability | Side Effects |
|-----------|-------------|
| `room.get_environment` | None |
| `room.get_temperature` | None |
| `room.get_humidity` | None |
| `room.get_brightness` | None |
| `room.get_motion_status` | None |
| `room.get_device_status` | None |
| `room.list_sensors` | None |

### Level 1 — SAFE_ACTION (auto-allowed, audited)

| Capability | Notes |
|-----------|-------|
| `room.stop_robot_arm` | Graceful stop — safety override |
| `room.emergency_stop_robot_arm` | Immediate stop — safety override |

### Level 2 — APPROVAL_REQUIRED

| Capability | Validation | Approval Flow |
|-----------|-----------|---------------|
| `room.set_light` | — | Approval UI → execute |
| `room.set_air_conditioner` | Temp range: 16–32°C, valid modes | Approval UI → validate → execute |
| `room.send_ir_command` | IR allowlist check | Approval UI → validate → execute |
| `room.set_smart_plug` | — | Approval UI → execute |
| `room.get_camera_snapshot` | — | Approval UI → execute |

### Explicitly Denied (always DENY)

| Capability | Reason |
|-----------|--------|
| `room.move_robot_arm` | Physical safety risk — robot arm near people |
| `room.robot_arm_move` | Physical safety risk |
| `room.lock_door` | Physical security |
| `room.ac_power_on` | Legacy — use `room.set_air_conditioner` |

## IR Command Safety

### Allowlist

Only pre-approved IR commands can be sent. Unknown commands are denied.

| Category | Commands |
|----------|---------|
| TV | `tv_power`, `tv_volume_up`, `tv_volume_down`, `tv_mute`, `tv_input` |
| AC | `ac_power`, `ac_cool`, `ac_heat`, `ac_dry`, `ac_fan`, `ac_temp_up`, `ac_temp_down` |
| Light | `light_power`, `light_brightness_up`, `light_brightness_down` |
| Speaker | `speaker_power`, `speaker_volume_up`, `speaker_volume_down` |

### What is NOT allowed

- Unknown IR codes (not in allowlist)
- Arbitrary Pronto hex codes
- IR codes for devices not in the allowlist

## AC Temperature Safety

| Parameter | Range | Validation |
|-----------|-------|-----------|
| `target_temperature_c` | 16.0°C – 32.0°C | Client-side range check |
| `mode` | `cool`, `heat`, `dry`, `fan`, `auto` | Client-side enum check |
| `fan_speed` | 0 (auto), 1–5 | No additional validation |

Out-of-range values are denied before reaching PolicyEngine.

## Robot Arm Safety

| Operation | Level | Rationale |
|-----------|-------|-----------|
| `room.move_robot_arm` | Level 3 (DENY) | Physical safety risk — arm could hit people or objects |
| `room.stop_robot_arm` | Level 1 (ALLOW) | Safety override — must be able to stop immediately |
| `room.emergency_stop_robot_arm` | Level 1 (ALLOW) | Emergency — immediate stop, no approval needed |

### Future: Robot Arm with Safety Constraints

When robot arm move is eventually allowed (with user confirmation):
- Speed limits enforced
- Workspace boundaries defined
- Proximity sensor integration
- Always require approval (Level 2 minimum)
- Emergency stop always available (Level 1)

## Camera Privacy

| Capability | Level | Notes |
|-----------|-------|-------|
| `room.get_camera_snapshot` | Level 2 | Requires approval — privacy concern |

Camera snapshots:
- Require explicit user approval before capture
- Are not stored long-term without approval
- Should be treated as ephemeral
- May contain sensitive content (people, documents)

## Mock Provider Safety

- `MockActuatorProvider` NEVER controls real hardware
- All operations are simulated and logged to `call_log`
- CI tests verify behavior without physical devices
- Real providers are optional and require explicit user configuration

## Data Flow

```
Room Hardware
  ├── Sensors (read-only) → SensorProvider
  └── Actuators (write) → ActuatorProvider
        ↓
RoomServerClient
  ├── Threshold check (suppress noise)
  ├── AC temp range validation
  ├── IR allowlist check
  ├── Robot arm safety check
  └── Dedupe / Cooldown
        ↓
ToolBroker → PolicyEngine → Approval UI (Level 2+)
        ↓
EventBus → TriggerEngine → ContextBuilder → AuditLog
```
