"""gRPC client adapter for Room Server capabilities."""

from __future__ import annotations

import json
import os
from typing import Any

import grpc

from generated.aegis import room_server_pb2, room_server_pb2_grpc


class RoomServerGrpcClient:
    """Adapter used by ServerExecutor for canonical room-server capabilities."""

    def __init__(self, host: str | None = None, port: int | None = None, timeout_seconds: float = 10.0) -> None:
        self.host = host or os.getenv("ROOM_SERVER_HOST", "localhost")
        self.port = port or int(os.getenv("ROOM_SERVER_PORT", "50055"))
        self.timeout_seconds = timeout_seconds

    def invoke_capability(self, capability_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}
        try:
            with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
                stub = room_server_pb2_grpc.RoomServerStub(channel)
                if capability_id == "room-server.environment.get_environment":
                    return self._get_environment(stub, params)
                if capability_id == "room-server.light.set_light":
                    return self._set_light(stub, params)
                if capability_id == "room-server.ir.send_command":
                    return self._send_ir_command(stub, params)
                if capability_id == "room-server.device.get_status":
                    return self._get_device_status(stub, params)
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
        response = stub.SetLight(
            room_server_pb2.SetLightRequest(
                device_id=device_id,
                power_on=bool(params.get("power_on", True)),
                brightness=int(params.get("brightness", -1)),
                color_temp_k=int(params.get("color_temp_k", 0)),
                color_rgb=str(params.get("color_rgb", "") or ""),
            ),
            timeout=self.timeout_seconds,
        )
        result = self._status_dict(response.status)
        result["device_id"] = device_id
        if response.status.code == 0:
            ir_code = str(params.get("ir_code", "") or "")
            if ir_code:
                result["ir_command"] = self._send_ir_command(
                    stub,
                    {
                        "device_type": "light",
                        "ir_code": ir_code,
                        "repeat": 1,
                    },
                )
                result["ir_code"] = ir_code
            result["device"] = self._get_single_device_status(stub, device_id)
        return result

    def _send_ir_command(self, stub: room_server_pb2_grpc.RoomServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.SendIrCommand(
            room_server_pb2.SendIrCommandRequest(
                device_type=str(params.get("device_type", "light") or "light"),
                ir_code=str(params.get("ir_code", "") or ""),
                repeat=int(params.get("repeat", 1)),
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
