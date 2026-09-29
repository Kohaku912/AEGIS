# Room Server — Design & Usage

> ⚠️ **Goal change (2026-09-27)**: the only constraint is now **"the user's information must never
> leave the local environment."** Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. The L0–L3 levels below are a **risk annotation**, not a gate — nothing on this
> server blocks on a confirmation. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

> **Status**: Code-backed room server (gRPC, mock-first providers)
> **Language**: Python
> **Source**: `room-server/` — see [`room-server/AGENTS.md`](../room-server/AGENTS.md)

> This document was rewritten on 2026-09-28. It previously listed ~18 capabilities under the old
> `room.*` id scheme (only five exist), an IR allowlist and an AC temperature range that are not
> implemented, `MockSensorProvider` / `MockActuatorProvider` classes that do not exist, and test
> commands pointing at files that were never committed.

## What actually runs

The Room Server is a Python gRPC service on **50055** with **mock-first** providers. Only two
providers are real code paths, and both are local:

| Provider | Default | Real path |
|---|---|---|
| Light / IR | `MockLightIrProvider` | `OrangePiGpioIrProvider` when `AEGIS_ROOM_LIGHT_PROVIDER=gpio` |
| Sound level | `MockSoundProvider` | `AlsaInmp441Provider` (INMP441 I2S MEMS mic) |

`create_light_provider()` and `create_sound_provider()` are the factories; sound may be `None`
(provider disabled), in which case the device simply does not appear in `GetDeviceStatus`.

## Capabilities (five — the catalog is authoritative)

The AI server owns the catalog in `ai-server/capabilities/builtin/room-server/`. The ids are
`room-server.<app>.<action>`, **not** `room.*`:

| Capability id | Level | Risk | Status |
|---|---|---|---|
| `room-server.environment.get_environment` | L0 | low | Returns **hardcoded fixtures** — see below |
| `room-server.device.get_status` | L0 | low | Real: assembled from the light + sound providers |
| `room-server.sound.get_level` | L0 | low | Real: INMP441 sample |
| `room-server.ir.send_ir_command` | L2 | safe | Real: raw NEC transmit |
| `room-server.light.set_light` | L2 | safe | Real: ceiling light via IR |

### `GetEnvironment` is a fixture, not a sensor

`RoomServer._environment` is set once in `__init__` and **never updated**, so `GetEnvironment` always
returns temperature 22.5 °C, humidity 45 %, brightness 300 lux, `motion_detected=false`. No
environment sensor is wired. Treat it as a placeholder until a real provider exists.

## RPCs in the contract with no provider

| RPC | Answer |
|---|---|
| `GetCameraSnapshot` | `503` "camera provider is not configured" |
| `SetAirConditioner` | `503` "air conditioner provider is not configured" |
| `MoveRobotArm` | `403` "robot arm movement is disabled by default" |
| `EmergencyStopRobotArm` | `0` "no robot arm provider configured", `stopped_arms=[]` |

## Validation that actually exists

| Surface | Rule | Failure |
|---|---|---|
| `SetLight.brightness` | `-1` (unchanged) or `0–255` | `400` "brightness must be -1 or between 0 and 255" |
| `SendIrCommand.repeat` | `1–10`, default `3` | `400` "repeat must be between 1 and 10" |
| `SendIrCommand.ir_code` | required, non-empty | `400` "ir_code is required" |

**There is no IR allowlist.** `send_ir_command` accepts any `0xADDR:0xCMD` pair with
Arduino-IRremote `sendNEC` semantics, and the manifest documents the ceiling-light codes
(`0xD001:0x23` off, `0xD001:0x20` all, `0xD001:0x21` eco, `0xD001:0x22` night). An earlier version of
this document claimed unknown commands were denied at the client level; that check does not exist.
`room-server.light.set_light` is the preferred path for the ceiling light.

There is also **no AC temperature validation**, because there is no AC provider.

## Environment variables

| Variable | Default | Effect |
|---|---|---|
| `AEGIS_ROOM_HOST` / `AEGIS_ROOM_PORT` | — / `50055` | Bind address |
| `AEGIS_ROOM_LIGHT_PROVIDER` | `mock` | `gpio` selects `OrangePiGpioIrProvider`; anything else keeps the mock |
| `AEGIS_ROOM_IR_PIN` | — | SoC pin for IR output, resolved by `resolve_ir_pin()` |
| `AEGIS_ROOM_IR_REPEAT`, `AEGIS_ROOM_IR_CARRIER_HZ`, `AEGIS_ROOM_IR_ACTIVE_LOW`, `AEGIS_ROOM_IR_BIT_ORDER`, `AEGIS_ROOM_IR_ADDR_MODE` | — | IR transmit tuning |
| `AEGIS_ROOM_SOUND_PROVIDER` | `mock` | `alsa` selects `AlsaInmp441Provider`; `off` / `none` / `disabled` / empty yields **no** sound device |
| `AEGIS_ROOM_SOUND_ALSA_DEVICE`, `AEGIS_ROOM_SOUND_RATE`, `AEGIS_ROOM_SOUND_CHANNELS`, `AEGIS_ROOM_SOUND_ARECORD` | — | ALSA capture settings |
| `AEGIS_ROOM_DEVICE_ID` | — | Overrides the default device id |

## Testing

The room server has its own suite (run from `room-server/`):

```bash
cd room-server
pytest -q          # test_ir_pin_resolve, test_nec_arduino_payload,
                   # test_room_server, test_sound_inmp441
```

The AI server side is covered by `ai-server/tests/test_room_integration.py`. The
`test_room_observe_e2e.py` / `test_room_action_e2e.py` files that this document used to reference
were never committed.
