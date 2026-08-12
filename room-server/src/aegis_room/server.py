"""gRPC Room Server implementation."""

from __future__ import annotations

import json
import time
from concurrent import futures
from typing import Any

import grpc

from generated.aegis import common_pb2, room_server_pb2, room_server_pb2_grpc

from aegis_room.providers import LightProvider, create_light_provider, now_ms
from aegis_room.sound_inmp441 import create_sound_provider

VERSION = "0.1.4+pc11-ir-inmp441"


def _status(code: int = 0, message: str = "ok") -> common_pb2.Status:
    return common_pb2.Status(code=code, message=message)


def _validate_brightness(brightness: int) -> str:
    if brightness == -1:
        return ""
    if 0 <= brightness <= 255:
        return ""
    return "brightness must be -1 or between 0 and 255"


def _validate_repeat(repeat: int) -> str:
    if 1 <= repeat <= 10:
        return ""
    return "repeat must be between 1 and 10"


class RoomServer(room_server_pb2_grpc.RoomServerServicer):
    def __init__(
        self,
        light_provider: LightProvider | None = None,
        sound_provider: Any | None = None,
    ) -> None:
        self._started_at_ms = now_ms()
        self._light_provider = light_provider or create_light_provider()
        # None sentinel for "use factory"; pass an object to inject, or set provider env=off.
        if sound_provider is None:
            self._sound_provider = create_sound_provider()
        else:
            self._sound_provider = sound_provider
        self._environment: dict[str, Any] = {
            "temperature_c": 22.5,
            "humidity_pct": 45.0,
            "brightness_lux": 300.0,
            "motion_detected": False,
            "motion_zone": "",
        }

    def HealthCheck(self, request, context):
        return common_pb2.HealthCheckResponse(
            status=_status(message="room-server online"),
            server_status=common_pb2.SERVER_STATUS_ONLINE,
            uptime_ms=max(0, now_ms() - self._started_at_ms),
            version=VERSION,
        )

    def GetEnvironment(self, request, context):
        env = dict(self._environment)
        env["timestamp_ms"] = now_ms()
        return room_server_pb2.GetEnvironmentResponse(
            status=_status(),
            temperature_c=float(env["temperature_c"]),
            humidity_pct=float(env["humidity_pct"]),
            brightness_lux=float(env["brightness_lux"]),
            motion_detected=bool(env["motion_detected"]),
            motion_zone=str(env["motion_zone"]),
            timestamp_ms=int(env["timestamp_ms"]),
        )

    def _sound_device_status(self, duration_ms: int = 250) -> room_server_pb2.DeviceStatus | None:
        if self._sound_provider is None:
            return None
        sample = self._sound_provider.sample(duration_ms=duration_ms)
        return room_server_pb2.DeviceStatus(
            device_id=sample.device_id,
            device_type="sensor",
            state_json=sample.to_json(),
            online=bool(sample.available),
            last_seen_ms=sample.updated_at_ms,
        )

    def GetDeviceStatus(self, request, context):
        requested = set(request.device_ids)
        devices = []
        for state in self._light_provider.get_light_states():
            if requested and state.device_id not in requested:
                continue
            devices.append(
                room_server_pb2.DeviceStatus(
                    device_id=state.device_id,
                    device_type="light",
                    state_json=state.to_json(),
                    online=True,
                    last_seen_ms=state.updated_at_ms,
                )
            )
        sound = self._sound_device_status()
        if sound is not None and (not requested or sound.device_id in requested):
            devices.append(sound)
        return room_server_pb2.GetDeviceStatusResponse(status=_status(), devices=devices)

    def SetLight(self, request, context):
        err = _validate_brightness(request.brightness)
        if err:
            return room_server_pb2.SetLightResponse(status=_status(400, err))
        try:
            mode = str(getattr(request, "mode", "") or "")
            state = self._light_provider.set_light(
                device_id=request.device_id or "light-main",
                power_on=bool(request.power_on),
                brightness=int(request.brightness),
                color_temp_k=int(request.color_temp_k),
                color_rgb=request.color_rgb or "",
                ir_code="",
                mode=mode,
            )
            return room_server_pb2.SetLightResponse(
                status=_status(
                    message=(
                        f"light {state.device_id} updated by {state.provider}"
                        + (f" ir={state.ir_code}" if state.ir_code else "")
                    )
                )
            )
        except Exception as exc:
            return room_server_pb2.SetLightResponse(status=_status(500, str(exc)))

    def SendIrCommand(self, request, context):
        repeat = request.repeat or 3
        err = _validate_repeat(repeat)
        if err:
            return room_server_pb2.SendIrCommandResponse(status=_status(400, err))
        if not request.ir_code:
            return room_server_pb2.SendIrCommandResponse(status=_status(400, "ir_code is required"))
        try:
            event = self._light_provider.send_ir_command(request.device_type, request.ir_code, repeat)
            return room_server_pb2.SendIrCommandResponse(
                status=_status(message=f"ir command recorded: {json.dumps(event, ensure_ascii=True)}")
            )
        except Exception as exc:
            return room_server_pb2.SendIrCommandResponse(status=_status(500, str(exc)))

    def GetCameraSnapshot(self, request, context):
        return room_server_pb2.GetCameraSnapshotResponse(
            status=_status(503, "camera provider is not configured"),
            image_data=b"",
            width=0,
            height=0,
            format=request.format or "jpeg",
            captured_ms=now_ms(),
        )

    def SetAirConditioner(self, request, context):
        return room_server_pb2.SetAirConditionerResponse(status=_status(503, "air conditioner provider is not configured"))

    def MoveRobotArm(self, request, context):
        return room_server_pb2.MoveRobotArmResponse(status=_status(403, "robot arm movement is disabled by default"))

    def EmergencyStopRobotArm(self, request, context):
        return room_server_pb2.EmergencyStopResponse(
            status=_status(message="no robot arm provider configured"),
            stopped_arms=[],
        )


def create_server() -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    room_server_pb2_grpc.add_RoomServerServicer_to_server(RoomServer(), server)
    return server


def serve(host: str = "0.0.0.0", port: int = 50055) -> None:
    server = create_server()
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    print(f"Room Server listening on {host}:{port}")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(grace=2)
