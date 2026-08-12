"""gRPC client adapter for Room Server capabilities."""

from __future__ import annotations

import json
import os
from typing import Any

import grpc

from generated.aegis import room_server_pb2, room_server_pb2_grpc

from aegis_ai.integrations.room.light_ir import format_ir_code, normalize_mode, power_on_for_mode
try:
    from aegis_ai.net.endpoint_resolver import resolve_tcp_endpoint
except ImportError:  # older container images without aegis_ai.net
    def resolve_tcp_endpoint(*_args, **_kwargs):  # type: ignore[misc]
        return None


class RoomServerGrpcClient:
    """Adapter used by ServerExecutor for canonical room-server capabilities."""

    def __init__(self, host: str | None = None, port: int | None = None, timeout_seconds: float = 10.0) -> None:
        self._fixed_host = host
        self.port = port or int(os.getenv("ROOM_SERVER_PORT", "50055"))
        self.timeout_seconds = timeout_seconds

    @property
    def host(self) -> str:
        if self._fixed_host:
            return self._fixed_host
        resolved = resolve_tcp_endpoint("room-server", port=self.port, timeout=min(0.5, self.timeout_seconds))
        if resolved:
            return resolved[0]
        return os.getenv("ROOM_SERVER_HOST", "localhost")

    def invoke_capability(self, capability_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}
        try:
            with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
                stub = room_server_pb2_grpc.RoomServerStub(channel)
                if capability_id == "room-server.environment.get_environment":
                    return self._get_environment(stub, params)
                if capability_id == "room-server.light.set_light":
                    return self._set_light(stub, params)
                if capability_id in {"room-server.ir.send_ir_command", "room-server.ir.send_command"}:
                    return self._send_ir_command(stub, params)
                if capability_id == "room-server.device.get_status":
                    return self._get_device_status(stub, params)
                if capability_id == "room-server.sound.get_level":
                    return self._get_sound_level(stub, params)
                return {"error": f"Unsupported Room capability: {capability_id}", "capability_id": capability_id}
        except grpc.RpcError as exc:
            return {
                "error": f"Room server gRPC error: {exc.code().name}: {exc.details()}",
                "capability_id": capability_id,
            }
        except Exception as exc:
            return {"error": f"Room server execution error: {exc}", "capability_id": capability_id}

    def _get_environment(self, stub: room_server_pb2_grpc.RoomServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.GetEnvironment(
            room_server_pb2.GetEnvironmentRequest(sensors=list(params.get("sensors", []) or [])),
            timeout=self.timeout_seconds,
        )
        result = self._status_dict(response.status)
        result.update(
            {
                "temperature_c": response.temperature_c,
                "humidity_pct": response.humidity_pct,
                "brightness_lux": response.brightness_lux,
                "motion_detected": response.motion_detected,
                "motion_zone": response.motion_zone,
                "timestamp_ms": response.timestamp_ms,
            }
        )
        return result

    def _set_light(self, stub: room_server_pb2_grpc.RoomServerStub, params: dict[str, Any]) -> dict[str, Any]:
        device_id = str(params.get("device_id") or "light-main")
        mode = normalize_mode(str(params.get("mode") or "") or None)
        if mode is None and "power_on" in params:
            mode = normalize_mode(None, power_on=bool(params.get("power_on")))
        if mode is None:
            return {"success": False, "error": "mode or power_on is required", "status_code": 400}

        power_on = power_on_for_mode(mode)
        ir_code = str(params.get("ir_code") or "") or format_ir_code(mode)
        request_kwargs: dict[str, Any] = {
            "device_id": device_id,
            "power_on": power_on,
            "brightness": int(params.get("brightness", -1)),
            "color_temp_k": int(params.get("color_temp_k", 0)),
            "color_rgb": str(params.get("color_rgb", "") or ""),
        }
        # Proto field `mode` is present after regeneration; keep getattr-safe for older stubs.
        if "mode" in room_server_pb2.SetLightRequest.DESCRIPTOR.fields_by_name:
            request_kwargs["mode"] = mode

        response = stub.SetLight(
            room_server_pb2.SetLightRequest(**request_kwargs),
            timeout=self.timeout_seconds,
        )
        result = self._status_dict(response.status)
        result["device_id"] = device_id
        result["mode"] = mode
        result["ir_code"] = ir_code
        result["light_addr"] = "0xD001"
        result["ir_protocol"] = "arduino-irremote-sendNEC"
        if response.status.code == 0:
            # Room server SetLight already transmits IR for mapped modes. Keep optional
            # explicit SendIrCommand only when caller forced a custom ir_code override.
            if params.get("ir_code"):
                result["ir_command"] = self._send_ir_command(
                    stub,
                    {
                        "device_type": "light",
                        "ir_code": ir_code,
                        "repeat": int(params.get("repeat", 3) or 3),
                    },
                )
            result["device"] = self._get_single_device_status(stub, device_id)
        return result

    def _send_ir_command(self, stub: room_server_pb2_grpc.RoomServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.SendIrCommand(
            room_server_pb2.SendIrCommandRequest(
                device_type=str(params.get("device_type", "light") or "light"),
                ir_code=str(params.get("ir_code", "") or ""),
                repeat=int(params.get("repeat", 3) or 3),
            ),
            timeout=self.timeout_seconds,
        )
        return self._status_dict(response.status)

    def _get_device_status(self, stub: room_server_pb2_grpc.RoomServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.GetDeviceStatus(
            room_server_pb2.GetDeviceStatusRequest(device_ids=list(params.get("device_ids", []) or [])),
            timeout=self.timeout_seconds,
        )
        result = self._status_dict(response.status)
        result["devices"] = [self._device_to_dict(device) for device in response.devices]
        return result

    def _get_sound_level(self, stub: room_server_pb2_grpc.RoomServerStub, params: dict[str, Any]) -> dict[str, Any]:
        device_id = str(params.get("device_id") or "sound-inmp441")
        # Fresh sample is taken inside room-server GetDeviceStatus for the mic device.
        response = stub.GetDeviceStatus(
            room_server_pb2.GetDeviceStatusRequest(device_ids=[device_id]),
            timeout=max(self.timeout_seconds, 8.0),
        )
        result = self._status_dict(response.status)
        result["device_id"] = device_id
        result["duration_ms"] = int(params.get("duration_ms", 250) or 250)
        if not response.devices:
            result["success"] = False
            result["error"] = f"sound device not found: {device_id}"
            return result
        device = self._device_to_dict(response.devices[0])
        result["device"] = device
        state = device.get("state") or {}
        result.update(
            {
                "sensor": state.get("sensor", "INMP441"),
                "rms": state.get("rms"),
                "peak": state.get("peak"),
                "db_fs": state.get("db_fs"),
                "available": state.get("available"),
                "wiring": state.get("wiring"),
                "warning": state.get("warning", ""),
                "provider": state.get("provider"),
            }
        )
        if state.get("available") is False:
            result["success"] = False
            if state.get("warning"):
                result["error"] = state["warning"]
        return result

    def _get_single_device_status(self, stub: room_server_pb2_grpc.RoomServerStub, device_id: str) -> dict[str, Any]:
        response = stub.GetDeviceStatus(
            room_server_pb2.GetDeviceStatusRequest(device_ids=[device_id]),
            timeout=self.timeout_seconds,
        )
        if not response.devices:
            return {}
        return self._device_to_dict(response.devices[0])

    @staticmethod
    def _status_dict(status: Any) -> dict[str, Any]:
        result: dict[str, Any] = {
            "success": int(status.code) == 0,
            "status_code": int(status.code),
            "message": status.message,
        }
        if status.code:
            result["error"] = status.message
        return result

    @staticmethod
    def _device_to_dict(device: Any) -> dict[str, Any]:
        try:
            state = json.loads(device.state_json) if device.state_json else {}
        except json.JSONDecodeError:
            state = {"raw": device.state_json}
        return {
            "device_id": device.device_id,
            "device_type": device.device_type,
            "state": state,
            "online": device.online,
            "last_seen_ms": device.last_seen_ms,
        }
