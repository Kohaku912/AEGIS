# Room Server — Safety & Privacy

> ⚠️ **Goal change (2026-09-27)**: the only constraint is now **"the user's information must never
> leave the local environment."** Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. The L0–L3 levels below are a **risk annotation**, not a gate — nothing on this
> server asks for a confirmation or blocks on one. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

> **Status**: Code-backed room server safety model
> **Related**: [`room-server.md`](room-server.md), [`room-server/AGENTS.md`](../room-server/AGENTS.md)

> Rewritten 2026-09-28. It previously documented ~18 capabilities under the old `room.*` ids (five
> exist), an IR allowlist and an AC temperature range that are **not implemented**, an "Approval UI →
> execute" flow for Level 2 that **no longer exists**, and `MockActuatorProvider` — a class that was
> never written.

## Safety Level Classification

Levels come from `SafetyLevel` in `protos/aegis/common.proto`. They are a **risk label** carried on
the capability, not an enforcement path.

### Level 0 — READ_ONLY

| Capability | Side effects |
|---|---|
| `room-server.environment.get_environment` | None — returns **hardcoded fixtures** |
| `room-server.device.get_status` | None |
| `room-server.sound.get_level` | None — captures ambient sound locally |

### Level 1 — SAFE_ACTION

Nothing is implemented at this level. `EmergencyStopRobotArm` exists in the contract and answers
`0` with `stopped_arms=[]` ("no robot arm provider configured") — there is no arm to stop.

### Level 2 — physical device control

| Capability | Validation | Flow |
|---|---|---|
| `room-server.light.set_light` | `brightness` must be `-1` or `0–255` | validate → execute |
| `room-server.ir.send_ir_command` | `repeat` `1–10`; `ir_code` required | validate → execute |

There is **no approval step**. These execute immediately and are recorded in the audit log. AEGIS may
*choose* to ask the user first — that is AEGIS's decision, not a gate on this server.

### Level 3 — disabled

| Capability | Reason |
|---|---|
| `MoveRobotArm` (RPC) | `403` "robot arm movement is disabled by default" |

`room.lock_door`, `room.ac_power_on` and `room.robot_arm_move` were listed here previously. None of
them exist in the catalog or in the RPC surface.

## IR Command Safety — there is no allowlist

An earlier version of this document claimed "only pre-approved IR commands can be sent; unknown
commands are denied." **No such check exists.** `send_ir_command` accepts any `0xADDR:0xCMD` pair and
transmits it with Arduino-IRremote `sendNEC` semantics (LSB-first, `repeat` 1–10, default 3).

What constrains it in practice:

- The manifest documents the intended codes for the ceiling light
  (`0xD001:0x23` off, `0xD001:0x20` all, `0xD001:0x21` eco, `0xD001:0x22` night).
- `room-server.light.set_light` is the preferred path for normal light control.
- The transmit is local: it drives a GPIO IR LED on the host board and sends nothing over a network.

## AC Temperature Safety — not applicable

There is **no AC provider**. `SetAirConditioner` answers `503` "air conditioner provider is not
configured", so there is no temperature range, no mode enum and no client-side validation to describe.

## Camera Privacy — not applicable

There is **no camera provider**. `GetCameraSnapshot` answers `503` "camera provider is not
configured" and returns empty image data. The privacy rules that used to be listed here described a
capture path that does not exist.

## Mock Provider Safety

- `MockLightIrProvider` **never** controls real hardware; it records calls in memory.
  `OrangePiGpioIrProvider` subclasses it and adds the GPIO write.
- `MockSoundProvider` returns synthetic samples; `AlsaInmp441Provider` captures from the local ALSA
  device.
- `AEGIS_ROOM_SOUND_PROVIDER=off` makes `create_sound_provider()` return `None`, so no sound device
  appears in `GetDeviceStatus` at all.
- The room server's own suite runs entirely against the mocks — 14 tests, no hardware required.

## Data Flow

```
Room hardware (Orange Pi GPIO IR LED / INMP441 I2S mic)
  └── providers.py: MockLightIrProvider -> OrangePiGpioIrProvider
      sound_inmp441.py: MockSoundProvider -> AlsaInmp441Provider
        ↓
RoomServer (gRPC :50055)          ← validates brightness / repeat / ir_code
        ↓
AI Server: capability catalog -> ToolBroker -> audit log
        ↓
EventBus -> TriggerEngine -> ContextBuilder -> AuditLog
```

Every hop is on the local machine. The room server has no outbound network path: it reads a GPIO pin
and an ALSA device, and answers gRPC on its own port.
