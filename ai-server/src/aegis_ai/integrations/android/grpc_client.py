"""LAN-mode Android gRPC client."""

from __future__ import annotations

from typing import Any

import grpc
from google.protobuf.json_format import MessageToDict

from generated.aegis import android_server_pb2, android_server_pb2_grpc, common_pb2


class AndroidGrpcClient:
    """Thin AndroidServer gRPC client using fixed protobuf methods only."""

    def __init__(self, host: str = "localhost", port: int = 50054, timeout_seconds: float = 10.0) -> None:
        self.host = host
        self.port = port
        self.timeout_seconds = timeout_seconds
        self._channel: grpc.Channel | None = None
        self._stub: android_server_pb2_grpc.AndroidServerStub | None = None

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"

    def is_available(self) -> bool:
        try:
            stub = self._get_stub()
            response = stub.HealthCheck(common_pb2.HealthCheckRequest(server_id="android-server"), timeout=2)
            return response.status.code == 0
        except Exception:
            return False

    def invoke_route(self, route: Any, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Invoke a fixed route on AndroidServer."""
        params = params or {}
        stub = self._get_stub()
        rpc = getattr(stub, route.method, None)
        if rpc is None:
            return {
                "error": f"Android RPC '{route.method}' is not implemented by this client stub",
                "code": "UNIMPLEMENTED_ANDROID_CAPABILITY",
                "capability_id": route.capability_id,
            }
        request_cls = getattr(android_server_pb2, route.request_type, None)
        if request_cls is None:
            return {
                "error": f"Android request type '{route.request_type}' is unavailable",
                "code": "UNIMPLEMENTED_ANDROID_CAPABILITY",
                "capability_id": route.capability_id,
            }
        try:
            request = self._build_request(request_cls, params)
            response = rpc(request, timeout=self.timeout_seconds)
        except grpc.RpcError as exc:
            return {
                "error": f"Android gRPC error: {exc.details() or exc.code().name}",
                "code": "ANDROID_SERVER_UNAVAILABLE",
                "capability_id": route.capability_id,
                "grpc_code": exc.code().name,
            }
        except Exception as exc:
            return {
                "error": str(exc),
                "code": "UNIMPLEMENTED_ANDROID_CAPABILITY",
                "capability_id": route.capability_id,
            }

        output = MessageToDict(response, preserving_proto_field_name=True)
        status = output.get("status", {})
        if isinstance(status, dict) and status.get("code", 0):
            return {
                "error": status.get("message", "Android command failed"),
                "code": "ANDROID_COMMAND_FAILED",
                "capability_id": route.capability_id,
                "response": output,
            }
        output.setdefault("connection_mode", "lan")
        return output

    def _get_stub(self) -> android_server_pb2_grpc.AndroidServerStub:
        if self._stub is None:
            self._channel = grpc.insecure_channel(self.endpoint)
            self._stub = android_server_pb2_grpc.AndroidServerStub(self._channel)
        return self._stub

    @staticmethod
    def _build_request(request_cls: Any, params: dict[str, Any]) -> Any:
        field_names = set(request_cls.DESCRIPTOR.fields_by_name)
        filtered = {key: value for key, value in params.items() if key in field_names}
        return request_cls(**filtered)
