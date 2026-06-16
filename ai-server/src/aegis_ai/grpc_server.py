"""gRPC server for AEGIS Core.

Implements the AIServer service defined in protos/aegis/ai_server.proto.
Uses generated stubs from ai-server/src/generated/aegis/.

Minimal implementation:
- HealthCheck — fully functional
- Other RPCs — return UNIMPLEMENTED or delegate to existing modules
"""

from __future__ import annotations

import logging
import json
import time
import uuid
from concurrent import futures
from typing import Any

import grpc

from aegis_ai.config import Config
from aegis_ai.runtime import AegisRuntime, get_runtime

# Generated proto stubs
from generated.aegis import ai_server_pb2, ai_server_pb2_grpc, common_pb2
from generated.aegis.common_pb2 import (
    HealthCheckRequest,
    HealthCheckResponse,
    ServerStatus,
    Status,
)
from aegis_schema.models import Capability, Event, EventPriority, RiskLevel, ServerInfo, ServerStatus as SchemaServerStatus, ServerType

logger = logging.getLogger("aegis_ai.grpc_server")

# Server start time for uptime calculation
_SERVER_START_MS: int = 0


class AegisAIServicer(ai_server_pb2_grpc.AIServerServicer):
    """gRPC service implementation for the AI Server.

    Architecture reference: docs/architecture.md §3.1
    Proto definition: protos/aegis/ai_server.proto
    """

    def __init__(self, runtime: AegisRuntime) -> None:
        self._runtime = runtime
        self._config = runtime.config

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
        server_info = _server_info_from_proto(request.server_info)
        self._runtime.tool_registry.register_server(server_info)
        server_id = server_info.server_id
        logger.info("Server registered: %s (type=%s)", server_id, server_info.server_type.name)
        return ai_server_pb2.RegisterServerResponse(
            status=Status(code=0, message="ok"),
            server_id=server_id,
        )

    def UnregisterServer(self, request, context):
        """Unregister a server."""
        server_id = request.server_id
        self._runtime.tool_registry.unregister_server(server_id)
        logger.info("Server unregistered: %s", server_id)
        return ai_server_pb2.UnregisterServerResponse(
            status=Status(code=0, message="ok"),
        )

    def RegisterCapability(self, request, context):
        """Register a capability with AEGIS Core."""
        cap = _capability_from_proto(request.capability)
        cap_id = cap.id
        self._runtime.tool_registry.register_capability(cap)
        logger.info("Capability registered: %s", cap_id)
        return ai_server_pb2.RegisterCapabilityResponse(
            status=Status(code=0, message="ok"),
            capability_id=cap_id,
        )

    def UnregisterCapability(self, request, context):
        """Unregister a capability."""
        cap_id = request.capability_id
        self._runtime.tool_registry.unregister_capability(cap_id)
        logger.info("Capability unregistered: %s", cap_id)
        return ai_server_pb2.UnregisterCapabilityResponse(
            status=Status(code=0, message="ok"),
        )

    def ListCapabilities(self, request, context):
        """List registered capabilities."""
        server_type = ServerType(request.server_type) if request.server_type else None
        max_risk = _risk_from_safety(request.max_safety_level) if request.max_safety_level else None
        if request.search_query:
            caps = self._runtime.tool_registry.search(
                request.search_query,
                server_type=server_type,
                max_risk_level=max_risk,
            )
        else:
            caps = self._runtime.tool_registry.list_capabilities(
                server_type=server_type,
                max_risk_level=max_risk,
                tags=list(request.tags),
            )
        return ai_server_pb2.ListCapabilitiesResponse(
            status=Status(code=0, message="ok"),
            capabilities=[_capability_to_proto(cap) for cap in caps],
        )

    def GetCapability(self, request, context):
        """Get a specific capability."""
        cap_id = request.capability_id
        cap = self._runtime.tool_registry.get_capability(cap_id)
        if cap is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Capability not found: {cap_id}")
            return common_pb2.Capability()
        return _capability_to_proto(cap)

    # ── Event Bus ────────────────────────────────────────────

    def PushEvent(self, request, context):
        """Push an event to the EventBus."""
        event = _event_from_proto(request.event)
        accepted = self._runtime.event_bus.publish(event)
        logger.info("Event received: %s from %s", event.event_type, event.source_server_id)
        return ai_server_pb2.PushEventResponse(
            status=Status(code=0, message="ok"),
            event_id=event.event_id,
            deduplicated=not accepted,
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
        from tool_broker import ExecutionSource, ToolExecutionRequest

        try:
            params = json.loads(request.params_json or "{}")
        except json.JSONDecodeError as exc:
            return common_pb2.ToolInvocationResult(
                status=Status(code=1, message=f"Invalid params_json: {exc}"),
                capability_id=request.capability_id,
                invocation_id=request.invocation_id,
                error=str(exc),
            )

        if request.is_approved and request.approval_id:
            result = self._runtime.tool_broker.execute_approved(request.approval_id)
            output = result.output
            success = result.success
            error = result.error
            duration_ms = result.duration_ms
            invocation_id = result.request_id or request.invocation_id
        else:
            tool_request = ToolExecutionRequest(
                request_id=request.invocation_id,
                capability_id=request.capability_id,
                arguments=params,
                source=ExecutionSource.USER_EXPLICIT,
                reason=f"gRPC invocation by {request.caller or 'unknown'}",
            )
            result = self._runtime.tool_broker.execute(tool_request)
            output = result.output
            success = result.success
            error = result.error
            duration_ms = int(result.duration_ms)
            invocation_id = result.request_id

        return common_pb2.ToolInvocationResult(
            status=Status(code=0 if success else 1, message="ok" if success else error),
            capability_id=request.capability_id,
            invocation_id=invocation_id,
            output_json=json.dumps(output or {}, ensure_ascii=False),
            error=error,
            duration_ms=int(duration_ms),
            was_approved=request.is_approved,
        )

    # ── Approval ─────────────────────────────────────────────

    def RequestApproval(self, request, context):
        req = self._runtime.approval_store.create_request(
            capability_id=request.capability_id,
            tool_name=request.tool_name,
            requested_action=request.requested_action,
            human_readable_summary=request.human_readable_summary,
            risk_explanation=request.risk_explanation,
            payload_preview=request.payload_preview,
            risk_level=request.safety_level,
        )
        return _approval_to_proto(req)

    def ResolveApproval(self, request, context):
        if request.rejected:
            ok = self._runtime.approval_store.reject(request.approval_id)
        else:
            ok = self._runtime.approval_store.approve(request.approval_id)
        return ai_server_pb2.ResolveApprovalResponse(
            status=Status(code=0 if ok else 1, message="ok" if ok else "approval not found"),
            approval_id=request.approval_id,
        )

    def ListPendingApprovals(self, request, context):
        approvals = [_approval_to_proto(req) for req in self._runtime.approval_store.get_pending()]
        return ai_server_pb2.ListPendingApprovalsResponse(
            status=Status(code=0, message="ok"),
            approvals=approvals,
        )

    # ── Audit ────────────────────────────────────────────────

    def WriteAuditLog(self, request, context):
        from aegis_ai.audit import AuditEntry

        try:
            detail = json.loads(request.detail_json or "{}")
        except json.JSONDecodeError:
            detail = {"raw": request.detail_json}
        self._runtime.audit_log.append(
            AuditEntry(
                entry_id=request.record_id,
                timestamp_ms=request.timestamp_ms,
                action=str(request.action),
                actor=request.actor,
                capability_id=request.capability_id,
                decision="RECORDED",
                detail=detail,
            )
        )
        return Status(code=0, message="ok")

    def QueryAuditLog(self, request, context):
        records = []
        for entry in self._runtime.audit_log.read_all():
            ts = int(entry.get("timestamp_ms", 0) or 0)
            if request.since_ms and ts < request.since_ms:
                continue
            if request.until_ms and ts > request.until_ms:
                continue
            if request.capability_id and entry.get("capability_id") != request.capability_id:
                continue
            records.append(common_pb2.AuditRecord(
                record_id=str(entry.get("entry_id", "")),
                timestamp_ms=ts,
                actor=str(entry.get("actor", "")),
                capability_id=str(entry.get("capability_id", "")),
                detail_json=json.dumps(entry.get("detail", {}), ensure_ascii=False),
            ))
        max_records = request.max_records or 100
        return ai_server_pb2.QueryAuditLogResponse(
            status=Status(code=0, message="ok"),
            records=records[-max_records:],
        )


def serve(config: Config | None = None, runtime: AegisRuntime | None = None) -> None:
    """Start the gRPC server. Blocks until shutdown."""
    global _SERVER_START_MS
    _SERVER_START_MS = int(time.time() * 1000)
    runtime = runtime or get_runtime(config)
    config = runtime.config

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.max_workers),
    )
    ai_server_pb2_grpc.add_AIServerServicer_to_server(
        AegisAIServicer(runtime), server
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


def _risk_from_safety(safety_level: int) -> RiskLevel:
    if safety_level >= common_pb2.LEVEL_3_RESTRICTED:
        return RiskLevel.HIGH_RISK
    if safety_level == common_pb2.LEVEL_2_APPROVAL:
        return RiskLevel.APPROVAL_REQUIRED
    if safety_level == common_pb2.LEVEL_1_SAFE_ACT:
        return RiskLevel.SAFE_ACTION
    if safety_level == common_pb2.LEVEL_0_READ:
        return RiskLevel.READ_ONLY
    return RiskLevel.UNSPECIFIED


def _safety_from_risk(risk_level: RiskLevel) -> int:
    if risk_level == RiskLevel.READ_ONLY:
        return common_pb2.LEVEL_0_READ
    if risk_level == RiskLevel.SAFE_ACTION:
        return common_pb2.LEVEL_1_SAFE_ACT
    if risk_level == RiskLevel.APPROVAL_REQUIRED:
        return common_pb2.LEVEL_2_APPROVAL
    return common_pb2.LEVEL_3_RESTRICTED


def _capability_from_proto(cap: common_pb2.Capability) -> Capability:
    risk = _risk_from_safety(cap.safety_level)
    return Capability(
        id=cap.id,
        name=cap.name or cap.id,
        description=cap.description or cap.name or cap.id,
        server_type=ServerType(cap.server_type or common_pb2.SERVER_TYPE_AI),
        input_schema=cap.input_schema or "{}",
        output_schema=cap.output_schema or "{}",
        risk_level=risk,
        requires_approval=cap.requires_approval,
        side_effects=list(cap.side_effects),
        timeout_ms=cap.timeout_ms,
        tags=list(cap.tags),
        version=cap.version or "0.1.0",
    )


def _capability_to_proto(cap: Capability) -> common_pb2.Capability:
    return common_pb2.Capability(
        id=cap.id,
        name=cap.name,
        description=cap.description,
        server_type=int(cap.server_type),
        input_schema=cap.input_schema,
        output_schema=cap.output_schema,
        safety_level=_safety_from_risk(cap.risk_level),
        requires_approval=cap.requires_approval,
        side_effects=list(cap.side_effects),
        tags=list(cap.tags),
        timeout_ms=cap.timeout_ms,
        version=cap.version,
    )


def _server_info_from_proto(info: common_pb2.ServerInfo) -> ServerInfo:
    return ServerInfo(
        server_id=info.server_id,
        server_type=ServerType(info.server_type or common_pb2.SERVER_TYPE_AI),
        version=info.version or "0.1.0",
        status=SchemaServerStatus(info.status or common_pb2.SERVER_STATUS_ONLINE),
        capability_ids=list(info.capability_ids),
        host=info.host or "localhost",
        port=info.port or 50051,
        started_at_ms=info.started_at_ms,
        last_heartbeat_ms=info.last_heartbeat_ms,
        metadata=dict(info.metadata),
    )


def _event_from_proto(event: common_pb2.Event) -> Event:
    return Event(
        event_id=event.event_id or f"event_{uuid.uuid4().hex[:12]}",
        event_type=event.event_type or "unknown",
        source_server_type=ServerType(event.source_server_type or common_pb2.SERVER_TYPE_AI),
        source_server_id=event.source_server_id or "unknown",
        timestamp_ms=event.timestamp_ms or int(time.time() * 1000),
        payload_json=event.payload_json or "{}",
        severity=int(event.severity),
        priority=EventPriority(event.priority or common_pb2.EVENT_PRIORITY_NORMAL),
        dedupe_key=event.dedupe_key,
        correlation_id=event.correlation_id,
        requires_attention=event.requires_attention,
        attributes=dict(event.attributes),
    )


def _approval_to_proto(req: Any) -> common_pb2.ApprovalRequest:
    return common_pb2.ApprovalRequest(
        approval_id=req.approval_id,
        capability_id=req.capability_id,
        tool_name=req.tool_name,
        requested_action=getattr(req, "requested_action", ""),
        human_readable_summary=getattr(req, "human_readable_summary", ""),
        risk_explanation=getattr(req, "risk_explanation", ""),
        payload_preview=getattr(req, "payload_preview", ""),
        safety_level=getattr(req, "risk_level", 0),
        status=int(getattr(req, "status", 0).value) if hasattr(getattr(req, "status", None), "value") else 0,
        created_at_ms=getattr(req, "created_at_ms", 0),
        expires_at_ms=getattr(req, "expires_at_ms", 0),
    )
