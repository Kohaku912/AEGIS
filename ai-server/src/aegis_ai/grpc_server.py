"""gRPC server for AEGIS Core.

Implements the AIServer service defined in protos/aegis/ai_server.proto.
Uses generated stubs from ai-server/src/generated/aegis/.

Minimal implementation:
- HealthCheck — fully functional
- Other RPCs — return UNIMPLEMENTED or delegate to existing modules
"""

from __future__ import annotations

import logging
import time
from concurrent import futures
from typing import Any

import grpc

from aegis_ai.config import Config

# Generated proto stubs
from generated.aegis import ai_server_pb2, ai_server_pb2_grpc, common_pb2
from generated.aegis.common_pb2 import (
    HealthCheckRequest,
    HealthCheckResponse,
    ServerStatus,
    Status,
)

logger = logging.getLogger("aegis_ai.grpc_server")

# Server start time for uptime calculation
_SERVER_START_MS: int = 0


class AegisAIServicer(ai_server_pb2_grpc.AIServerServicer):
    """gRPC service implementation for the AI Server.

    Architecture reference: docs/architecture.md §3.1
    Proto definition: protos/aegis/ai_server.proto
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._registered_servers: dict[str, Any] = {}
        self._registered_capabilities: dict[str, Any] = {}
        self._events: list[Any] = []

    # ── Health Check ────────────────────────────────────────

    def HealthCheck(self, request: HealthCheckRequest, context: grpc.ServicerContext) -> HealthCheckResponse:
        """Return server health status."""
        uptime_ms = int((time.time() * 1000) - _SERVER_START_MS) if _SERVER_START_MS else 0
        return HealthCheckResponse(
            status=Status(code=0, message="ok"),
            server_status=ServerStatus.SERVER_STATUS_ONLINE,
            uptime_ms=uptime_ms,
            version="0.1.0",
        )

    # ── Server & Capability Registry ──────────────────────────

    def RegisterServer(self, request, context):
        """Register a server with AEGIS Core."""
        server_info = request.server_info
        server_id = server_info.server_id
        self._registered_servers[server_id] = {
            "server_id": server_id,
            "server_type": server_info.server_type,
            "version": server_info.version,
            "host": server_info.host,
            "port": server_info.port,
        }
        logger.info("Server registered: %s (type=%d)", server_id, server_info.server_type)
        return ai_server_pb2.RegisterServerResponse(
            status=Status(code=0, message="ok"),
            server_id=server_id,
        )

    def UnregisterServer(self, request, context):
        """Unregister a server."""
        server_id = request.server_id
        self._registered_servers.pop(server_id, None)
        logger.info("Server unregistered: %s", server_id)
        return ai_server_pb2.UnregisterServerResponse(
            status=Status(code=0, message="ok"),
        )

    def RegisterCapability(self, request, context):
        """Register a capability with AEGIS Core."""
        cap = request.capability
        cap_id = cap.id
        self._registered_capabilities[cap_id] = {
            "id": cap_id,
            "name": cap.name,
            "description": cap.description,
            "server_type": cap.server_type,
            "safety_level": cap.safety_level,
        }
        logger.info("Capability registered: %s", cap_id)
        return ai_server_pb2.RegisterCapabilityResponse(
            status=Status(code=0, message="ok"),
            capability_id=cap_id,
        )

    def UnregisterCapability(self, request, context):
        """Unregister a capability."""
        cap_id = request.capability_id
        self._registered_capabilities.pop(cap_id, None)
        logger.info("Capability unregistered: %s", cap_id)
        return ai_server_pb2.UnregisterCapabilityResponse(
            status=Status(code=0, message="ok"),
        )

    def ListCapabilities(self, request, context):
        """List registered capabilities."""
        caps = []
        for cap_data in self._registered_capabilities.values():
            caps.append(common_pb2.Capability(
                id=cap_data["id"],
                name=cap_data["name"],
                description=cap_data["description"],
                server_type=cap_data["server_type"],
                safety_level=cap_data["safety_level"],
            ))
        return ai_server_pb2.ListCapabilitiesResponse(
            status=Status(code=0, message="ok"),
            capabilities=caps,
        )

    def GetCapability(self, request, context):
        """Get a specific capability."""
        cap_id = request.capability_id
        cap_data = self._registered_capabilities.get(cap_id)
        if not cap_data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Capability not found: {cap_id}")
            return common_pb2.Capability()
        return common_pb2.Capability(
            id=cap_data["id"],
            name=cap_data["name"],
            description=cap_data["description"],
            server_type=cap_data["server_type"],
            safety_level=cap_data["safety_level"],
        )

    # ── Event Bus ────────────────────────────────────────────

    def PushEvent(self, request, context):
        """Push an event to the EventBus."""
        event = request.event
        self._events.append({
            "event_id": event.event_id,
            "event_type": event.event_type,
            "source_server_type": event.source_server_type,
            "source_server_id": event.source_server_id,
            "timestamp_ms": event.timestamp_ms,
            "payload_json": event.payload_json,
            "severity": event.severity,
        })
        logger.info("Event received: %s from %s", event.event_type, event.source_server_id)
        return ai_server_pb2.PushEventResponse(
            status=Status(code=0, message="ok"),
            event_id=event.event_id,
            deduplicated=False,
        )

    def StreamEvents(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("StreamEvents not yet implemented")
        return  # Empty stream

    def SubscribeEvents(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("SubscribeEvents not yet implemented")
        return  # Empty stream

    # ── Tool Invocation ──────────────────────────────────────

    def InvokeTool(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("InvokeTool not yet implemented")
        return common_pb2.ToolInvocationResult()

    # ── Approval ─────────────────────────────────────────────

    def RequestApproval(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("RequestApproval not yet implemented")
        return common_pb2.ApprovalRequest()

    def ResolveApproval(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("ResolveApproval not yet implemented")
        return ai_server_pb2.ResolveApprovalResponse()

    def ListPendingApprovals(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("ListPendingApprovals not yet implemented")
        return ai_server_pb2.ListPendingApprovalsResponse()

    # ── Audit ────────────────────────────────────────────────

    def WriteAuditLog(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("WriteAuditLog not yet implemented")
        return Status()

    def QueryAuditLog(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("QueryAuditLog not yet implemented")
        return ai_server_pb2.QueryAuditLogResponse()


def serve(config: Config) -> None:
    """Start the gRPC server. Blocks until shutdown."""
    global _SERVER_START_MS
    _SERVER_START_MS = int(time.time() * 1000)

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.max_workers),
    )
    ai_server_pb2_grpc.add_AIServerServicer_to_server(
        AegisAIServicer(config), server
    )

    address = f"{config.grpc_host}:{config.grpc_port}"
    server.add_insecure_port(address)
    server.start()

    logger.info("gRPC server listening on %s", address)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Stopping gRPC server...")
        server.stop(grace=5)
