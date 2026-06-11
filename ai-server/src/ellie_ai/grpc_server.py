"""gRPC server for Ellie AI Server.

Implements the AIServer service defined in protos/ellie/ai_server.proto.
Uses generated stubs from ai-server/src/generated/ellie/.

Minimal implementation:
- HealthCheck — fully functional
- Other RPCs — return UNIMPLEMENTED or delegate to existing modules
"""

from __future__ import annotations

import logging
import time
from concurrent import futures

import grpc

from ellie_ai.config import Config

# Generated proto stubs
from generated.ellie import ai_server_pb2, ai_server_pb2_grpc, common_pb2
from generated.ellie.common_pb2 import (
    HealthCheckRequest,
    HealthCheckResponse,
    ServerStatus,
    Status,
)

logger = logging.getLogger("ellie_ai.grpc_server")

# Server start time for uptime calculation
_SERVER_START_MS: int = 0


class EllieAIServicer(ai_server_pb2_grpc.AIServerServicer):
    """gRPC service implementation for the AI Server.

    Architecture reference: docs/architecture.md §3.1
    Proto definition: protos/ellie/ai_server.proto
    """

    def __init__(self, config: Config) -> None:
        self._config = config

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
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("RegisterServer not yet implemented")
        return ai_server_pb2.RegisterServerResponse()

    def UnregisterServer(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("UnregisterServer not yet implemented")
        return ai_server_pb2.UnregisterServerResponse()

    def RegisterCapability(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("RegisterCapability not yet implemented")
        return ai_server_pb2.RegisterCapabilityResponse()

    def UnregisterCapability(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("UnregisterCapability not yet implemented")
        return ai_server_pb2.UnregisterCapabilityResponse()

    def ListCapabilities(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("ListCapabilities not yet implemented")
        return ai_server_pb2.ListCapabilitiesResponse()

    def GetCapability(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("GetCapability not yet implemented")
        return common_pb2.Capability()

    # ── Event Bus ────────────────────────────────────────────

    def PushEvent(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("PushEvent not yet implemented")
        return ai_server_pb2.PushEventResponse()

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
        EllieAIServicer(config), server
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
