# Room Server — AGENTS.md

> ⚠️ **Goal change (2026-09-27)**: the only constraint is now **"the user's information must never
> leave the local environment."** Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. The L0–L3 levels below are a **risk annotation**, not a gate.
> Note: these L0–L3 are **autonomy levels** — distinct from the L1/L2/L3 **LLM 3-layer** architecture.
> See [`docs/GOAL-CHANGE.md`](../docs/GOAL-CHANGE.md).

## Purpose

The Room Server handles **IoT and sensor operations** for AEGIS on a single-board computer
(Orange Pi Zero3). What it actually serves today:

- Ambient sound level (INMP441 I2S MEMS microphone) — a real sample
- Ceiling-light control over IR (Arduino-IRremote / NEC) — real, via mock or GPIO provider
- Raw IR transmit — real
- Device status — real, assembled from the light + sound providers

Two surfaces are **placeholders, not sensors**, and the docs used to overstate them:

- `GetEnvironment` returns **hardcoded constants** — `_environment` is set once in `RoomServer.__init__`
  and never updated, so temperature 22.5 °C / humidity 45 % / brightness 300 lux / `motion_detected=false`
  are fixtures, not readings. No environment sensor is wired.
- `GetCameraSnapshot`, `SetAirConditioner` and `MoveRobotArm` have **no provider** and answer
  503 / 503 / 403 respectively.

## Technology Stack

- **Language**: Python (`>=3.12`)
- **Framework**: gRPC service, mock-first providers (`grpcio>=1.81`; `protobuf` is pinned to **7.35.1**
  by `uv.lock`, which is the version the generated stubs require)
- **Port**: 50055 (gRPC)
- **Testing**: pytest

## Directory Structure

```
room-server/
├── src/
│   ├── main.py                  # Thin entry point -> aegis_room.main
│   ├── aegis_room/
│   │   ├── main.py              # serve() / argument parsing
│   │   ├── server.py            # RoomServer servicer (the 9 RPCs below)
│   │   ├── providers.py         # LightProvider protocol, Mock + OrangePi GPIO IR, IR pin resolution
│   │   ├── light_ir.py          # NEC code format/parse, mode <-> command mapping
│   │   └── sound_inmp441.py     # INMP441 I2S microphone sound-level sampling
│   └── generated/aegis/         # protoc output — a mirror, never edit by hand
├── tests/                       # test_ir_pin_resolve, test_nec_arduino_payload,
│                                # test_room_server, test_sound_inmp441
├── overlays/                    # sun50i-h616-i2s3-inmp441.dts (device-tree overlay)
├── pyproject.toml
└── uv.lock
```

## Key Components

### Providers (`src/aegis_room/providers.py`)

- `LightProvider` protocol with a **mock-first** default (`MockLightIrProvider`) and an
  `OrangePiGpioIrProvider` selected when `AEGIS_ROOM_LIGHT_PROVIDER=gpio`
- `resolve_ir_pin()` maps an SoC pin name to bank/bit for GPIO output
- `create_light_provider()` is the factory the servicer calls; sound is separate
  (`sound_inmp441.create_sound_provider()`)
- There is **no MQTT provider** — an earlier version of this file described one that never existed

### Capability manifests (`ai-server/capabilities/builtin/room-server/`)

The AI server owns the capability catalog; this server only serves the RPCs. There are **five**
manifests, and they are the authoritative list — do not infer capabilities from the RPC names:

| Capability | Risk | Notes |
|---|---|---|
| `environment/get_environment` | low | returns the fixtures described above |
| `device/get_status` | low | light + sound devices the server knows about |
| `sound/get_level` | low | INMP441 ambient sound level |
| `ir/send_ir_command` | safe | raw NEC transmit, LSB-first |
| `light/set_light` | safe | ceiling light via IR |

### RPCs with no provider

| RPC | Answer |
|---|---|
| `GetCameraSnapshot` | `503` "camera provider is not configured" |
| `SetAirConditioner` | `503` "air conditioner provider is not configured" |
| `MoveRobotArm` | `403` "robot arm movement is disabled by default" |
| `EmergencyStopRobotArm` | `0` "no robot arm provider configured", `stopped_arms=[]` |

## Safety Model

> ⚠️ **Approval is no longer a constraint.** The "Annotation" column records the **risk** AEGIS
> attaches to each level. Nothing on this server asks for a confirmation or blocks on one.

| Level | Operations | Annotation |
|-------|-----------|------------|
| L0 | Environment, device status, sound level | Low risk |
| L1 | Emergency stop | Immediate |
| L2 | Light, IR | Physical device control — auto-executed, audited |
| L3 | Robot arm movement | Disabled by default (no provider) |

## Key Design Decisions

1. **gRPC primary**: The runtime is a Python gRPC service
2. **Mock-first providers**: CI uses mock providers; GPIO is optional
3. **Safety levels**: Risk annotation model (was: graduated approval)
4. **Emergency stop**: Always allowed
5. **Robot arm blocked**: L3 operations denied by default
6. **Local only**: Sensor and camera data stay inside the local environment
7. **Generated stubs are mirrors, never sources**: `src/generated/aegis/` is produced from
   `protos/aegis/` by `scripts/generate_protos.ps1`. Do not edit it by hand.
   It drifted once: after the 2026-09-28 goal change removed the approval types from the canonical
   contract, this copy still declared `ApprovalRequest`, `requires_approval` and
   `POLICY_DECISION_ASK_APPROVAL` as live members, because the generation script only ever wrote to
   `ai-server`. `tests/test_goal_change_guard.py` now fails if this copy diverges from `ai-server`'s.
