"""gRPC server for AEGIS Core.

Implements the AIServer service defined in protos/aegis/ai_server.proto.
Uses generated stubs from ai-server/src/generated/aegis/.

Minimal implementation:
- HealthCheck — fully functional
- Other RPCs — return UNIMPLEMENTED or delegate to existing modules
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from concurrent import futures
from types import SimpleNamespace
from typing import Any

import grpc

from aegis_ai.config import Config
from aegis_ai.runtime import AegisRuntime, get_runtime
from aegis_schema.models import (
    Capability,
    Event,
    EventPriority,
    RiskLevel,
    ServerInfo,
    ServerType,
)
from aegis_schema.models import (
    ServerStatus as SchemaServerStatus,
)

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
            version="0.1.0+sendchat+history-v1+room-v1",
        )

    # ── Server & Capability Registry ──────────────────────────

    def RegisterServer(self, request, context):
        """Register a server with AEGIS Core."""
        server_info = _server_info_from_proto(request.server_info)
        if server_info.server_type == ServerType.ANDROID:
            ok, message = self._runtime.android_manager.register_lan_server(server_info)
            if not ok:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details(message)
                return ai_server_pb2.RegisterServerResponse(
                    status=Status(code=16, message=message),
                    server_id=server_info.server_id,
                )
            self._runtime.server_executor.register_client("android-server", self._runtime.android_manager)
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
        if cap.server_type == ServerType.ANDROID:
            return ai_server_pb2.RegisterCapabilityResponse(
                status=Status(code=1, message="ANDROID_DYNAMIC_CAPABILITY_DISABLED"),
                capability_id=cap.id,
            )
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
        if event.source_server_type == ServerType.ANDROID or event.source_server_id == "android-server":
            ok, device_id, message = self._runtime.android_manager.validate_event_auth(event)
            if not ok:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details(message)
                return ai_server_pb2.PushEventResponse(
                    status=Status(code=16, message=message),
                    event_id=event.event_id,
                    deduplicated=False,
                )
            attrs = dict(event.attributes)
            attrs.setdefault("device_id", device_id)
            event.attributes = attrs
        accepted = self._runtime.event_manager.publish(event)
        logger.info("Event received: %s from %s", event.event_type, event.source_server_id)
        return ai_server_pb2.PushEventResponse(
            status=Status(code=0, message="ok"),
            event_id=event.event_id,
            deduplicated=not accepted,
        )

    def Connect(self, request_iterator, context):
        """Accept Android reverse stream connections."""
        return self._runtime.android_manager.open_stream(request_iterator, context)

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

    def SendChat(self, request, context):
        from aegis_ai.web.chat_service import execute_chat_message, tool_results_json
        from aegis_ai.web.chat_history import ChatHistoryStore, entry_to_mobile_messages

        conversation_id = request.conversation_id or f"android_chat_{int(time.time() * 1000)}"
        result = execute_chat_message(
            self._runtime,
            request.text,
            origin_channel="android_app",
            conversation_id=conversation_id,
            device_id=request.device_id,
            context=dict(request.context),
            task_source="android_chat",
        )
        ok = not result.get("error")
        response_text = result.get("response", "")
        if response_text:
            entry = ChatHistoryStore().append(
                request.text,
                response_text,
                source="android",
                conversation_id=result.get("conversation_id", conversation_id),
            )
            android_manager = getattr(self._runtime, "android_manager", None)
            if android_manager is not None and hasattr(android_manager, "broadcast_chat_update"):
                android_manager.broadcast_chat_update(entry_to_mobile_messages(entry))
        return ai_server_pb2.ChatResponse(
            status=Status(code=0 if ok else 1, message="ok" if ok else str(result.get("error", ""))),
            conversation_id=result.get("conversation_id", conversation_id),
            response=response_text,
            approval_needed=bool(result.get("approval_needed", False)),
            approval_id=result.get("approval_id", ""),
            tool_results_json=tool_results_json(result),
        )

    def GetMobileDashboardState(self, request, context):
        from aegis_ai.web.chat_history import ChatHistoryStore, entries_to_mobile_messages
        from aegis_ai.web.dashboard_routes import _runtime_server_status

        limit = request.history_limit if request.history_limit > 0 else 50
        history = ChatHistoryStore().load(limit=limit)
        status_payload = _runtime_server_status(runtime=self._runtime)
        server_statuses = [
            _mobile_server_status_to_proto(item)
            for item in status_payload.get("servers", [])
            if item.get("server_id") in {"ai-server", "pc-server", "browser-server", "android-server", "room-server"}
        ]
        chat_history = [_chat_history_message_to_proto(item) for item in entries_to_mobile_messages(history)]
        warnings = _mobile_dashboard_warnings(status_payload)
        return ai_server_pb2.MobileDashboardStateResponse(
            status=Status(code=0, message="ok"),
            server_statuses=server_statuses,
            chat_history=chat_history,
            warnings=warnings,
        )

    # ── Approval ─────────────────────────────────────────────

    def RequestApproval(self, request, context):
        tool_request = SimpleNamespace(
            request_id=f"grpc_{uuid.uuid4().hex[:10]}",
            task_id="",
            step_id="",
            source="grpc",
            source_desire="",
            frustration=0.0,
            capability_id=request.capability_id,
            tool_name=request.tool_name,
            arguments={"payload_preview": request.payload_preview},
            risk_level=_risk_from_safety(request.safety_level),
        )
        policy_result = SimpleNamespace(
            reason=request.risk_explanation or request.human_readable_summary or request.requested_action,
        )
        req = self._runtime.approval_manager.create_request(tool_request, policy_result)
        return _approval_to_proto(req)

    def ResolveApproval(self, request, context):
        if request.rejected:
            if request.global_reject:
                req = self._runtime.approval_manager.global_reject(
                    request.approval_id,
                    channel=request.surface_id or "grpc",
                    user=request.user or "user",
                    reason=request.reason,
                )
            else:
                req = self._runtime.approval_manager.reject(
                    request.approval_id,
                    channel=request.surface_id or "grpc",
                    user=request.user or "user",
                    reason=request.reason,
                )
        else:
            req = self._runtime.approval_manager.approve(
                request.approval_id,
                channel=request.surface_id or "grpc",
                user=request.user or "user",
            )
        ok = req is not None
        return ai_server_pb2.ResolveApprovalResponse(
            status=Status(code=0 if ok else 1, message="ok" if ok else "approval not found"),
            approval_id=request.approval_id,
        )

    def ListPendingApprovals(self, request, context):
        approvals = [_approval_to_proto(req) for req in self._runtime.approval_manager.list_pending()]
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
        if hasattr(self._runtime, 'audit_manager') and self._runtime.audit_manager:
            audit_entries = self._runtime.audit_manager.read_all_for_export()
        else:
            audit_entries = []
        for entry in audit_entries:
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


def _mobile_server_status_to_proto(item: dict[str, Any]):
    return ai_server_pb2.MobileServerStatus(
        server_id=str(item.get("server_id", "")),
        label=str(item.get("server_type", item.get("server_id", ""))),
        status=str(item.get("status", "UNKNOWN")),
        mode=str(item.get("mode", "")),
        detail=str(item.get("degraded_reason") or item.get("status_detail") or ""),
    )


def _chat_history_message_to_proto(item: dict[str, Any]):
    return ai_server_pb2.ChatHistoryMessage(
        message_id=str(item.get("message_id", "")),
        role=str(item.get("role", "")),
        text=str(item.get("text", "")),
        timestamp_ms=int(item.get("timestamp_ms", 0) or 0),
        image=str(item.get("image", "")),
        conversation_id=str(item.get("conversation_id", "")),
        source=str(item.get("source", "")),
    )


def _mobile_dashboard_warnings(status_payload: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for item in status_payload.get("servers", []):
        if item.get("server_id") != "android-server":
            continue
        deps = item.get("dependencies") or {}
        permissions = deps.get("permission_status") or {}
        missing = [name for name, granted in permissions.items() if granted is False]
        if missing:
            warnings.append("Missing Android permissions: " + ", ".join(sorted(missing)))
        break
    return warnings


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
    status_map = {
        "pending": common_pb2.APPROVAL_STATUS_PENDING,
        "approved": common_pb2.APPROVAL_STATUS_APPROVED,
        "modified": common_pb2.APPROVAL_STATUS_APPROVED,
        "rejected": common_pb2.APPROVAL_STATUS_REJECTED,
        "expired": common_pb2.APPROVAL_STATUS_EXPIRED,
    }
    status_value = status_map.get(getattr(req, "status", ""), common_pb2.APPROVAL_STATUS_UNSPECIFIED)
    risk_safety_map = {
        "read_only": common_pb2.LEVEL_0_READ,
        "safe_action": common_pb2.LEVEL_1_SAFE_ACT,
        "approval_required": common_pb2.LEVEL_2_APPROVAL,
        "high_risk": common_pb2.LEVEL_3_RESTRICTED,
        "medium": common_pb2.LEVEL_2_APPROVAL,
        "high": common_pb2.LEVEL_3_RESTRICTED,
        "low": common_pb2.LEVEL_0_READ,
        "safe": common_pb2.LEVEL_1_SAFE_ACT,
    }
    risk_level = getattr(req, "risk_level", "")
    return common_pb2.ApprovalRequest(
        approval_id=req.approval_id,
        capability_id=req.capability_id,
        tool_name=req.tool_name,
        requested_action=getattr(req, "requested_action", "")
        or getattr(req, "tool_name", "")
        or getattr(req, "capability_id", ""),
        human_readable_summary=getattr(req, "human_readable_summary", "")
        or getattr(req, "user_facing_summary", ""),
        risk_explanation=getattr(req, "risk_explanation", "")
        or getattr(req, "approval_reason", ""),
        payload_preview=getattr(req, "payload_preview", "")
        or getattr(req, "arguments_summary", ""),
        safety_level=risk_safety_map.get(str(risk_level), common_pb2.LEVEL_2_APPROVAL),
        status=status_value,
        created_at_ms=getattr(req, "created_at", getattr(req, "created_at_ms", 0)),
        expires_at_ms=getattr(req, "expires_at", getattr(req, "expires_at_ms", 0)),
    )
