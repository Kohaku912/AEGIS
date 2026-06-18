"""Android server manager for fixed gRPC Android terminals."""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Iterable
from typing import Any

import grpc

from aegis_ai.integrations.android.capability_mapper import AndroidCapabilityMapper
from aegis_ai.integrations.android.device_registry import AndroidDeviceRegistry
from aegis_ai.integrations.android.grpc_client import AndroidGrpcClient
from aegis_ai.integrations.android.stream_session import AndroidStreamSession
from aegis_schema.models import Event, EventPriority, ServerType

logger = logging.getLogger("aegis_ai.integrations.android.manager")


class AndroidServerManager:
    """Unified Android execution surface for LAN and reverse stream modes."""

    def __init__(
        self,
        *,
        data_dir: str,
        event_manager: Any = None,
        status_manager: Any = None,
        approval_manager: Any = None,
        host: str = "localhost",
        port: int = 50054,
        pairing_token: str | None = None,
    ) -> None:
        self.mapper = AndroidCapabilityMapper()
        self.device_registry = AndroidDeviceRegistry(data_dir=data_dir, pairing_token=pairing_token)
        self._event_manager = event_manager
        self._status_manager = status_manager
        self._approval_manager = approval_manager
        self._lan_client = AndroidGrpcClient(host=host, port=port)
        self._sessions: dict[str, AndroidStreamSession] = {}
        self._device_to_connection: dict[str, str] = {}
        self._permission_status: dict[str, bool] = {}
        self._last_device_status: dict[str, Any] = {}
        self._last_connection_mode = "unavailable"

    def invoke_capability(self, capability_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Invoke a fixed Android capability through LAN or reverse stream."""
        params = params or {}
        route = self.mapper.get_route(capability_id)
        if route is None:
            return {
                "error": f"Android capability is not registered in the fixed dispatch map: {capability_id}",
                "code": "UNREGISTERED_ANDROID_CAPABILITY",
                "capability_id": capability_id,
            }
        if not route.implemented:
            return {
                "error": f"Android capability is not implemented: {capability_id}",
                "code": "UNIMPLEMENTED_ANDROID_CAPABILITY",
                "capability_id": capability_id,
            }
        missing = [perm for perm in route.required_permissions if self._permission_status.get(perm) is False]
        if missing:
            return {
                "error": f"Android permission missing: {', '.join(missing)}",
                "code": "ANDROID_PERMISSION_MISSING",
                "capability_id": capability_id,
                "missing_permissions": missing,
            }
        if route.required_permissions and self._last_device_status.get("locked") is True:
            return {
                "error": "Android screen is locked",
                "code": "ANDROID_SCREEN_LOCKED",
                "capability_id": capability_id,
            }

        session = self._get_active_session()
        if session is not None:
            result = session.invoke(capability_id, route.method, params)
            self._after_invoke(capability_id, result)
            return result

        if self._lan_client.is_available():
            self._last_connection_mode = "lan"
            result = self._lan_client.invoke_route(route, params)
            self._after_invoke(capability_id, result)
            return result

        return {
            "error": "Android server is unavailable",
            "code": "ANDROID_SERVER_UNAVAILABLE",
            "capability_id": capability_id,
        }

    def register_lan_server(self, server_info: Any) -> tuple[bool, str]:
        """Authorize and register an Android LAN-mode server announcement."""
        metadata = dict(getattr(server_info, "metadata", {}) or {})
        device_id = metadata.get("device_id") or getattr(server_info, "server_id", "")
        token = metadata.get("pairing_token", "")
        if not self.device_registry.verify_and_authorize(
            device_id=device_id,
            pairing_token=token,
            metadata={k: v for k, v in metadata.items() if k != "pairing_token"},
            device_model=metadata.get("device_model", ""),
            manufacturer=metadata.get("manufacturer", ""),
            android_version=metadata.get("android_version", ""),
            app_version=metadata.get("app_version", ""),
        ):
            return False, "ANDROID_DEVICE_UNAUTHORIZED"
        host = getattr(server_info, "host", "") or "localhost"
        port = int(getattr(server_info, "port", 50054) or 50054)
        self._lan_client = AndroidGrpcClient(host=host, port=port)
        self._last_connection_mode = "lan"
        self._publish_android_event(
            "android.connected",
            device_id=device_id,
            connection_id="lan",
            payload={"connection_mode": "lan", "host": host, "port": port},
            dedupe_key=f"android.connected:{device_id}:lan",
        )
        if self._status_manager:
            self._status_manager.mark_online("android-server")
        return True, "ok"

    def validate_event_auth(self, event: Any) -> tuple[bool, str, str]:
        """Validate Android PushEvent auth from event attributes."""
        attrs = dict(getattr(event, "attributes", {}) or {})
        device_id = attrs.get("device_id") or getattr(event, "source_server_id", "")
        token = attrs.get("pairing_token", "")
        if not self.device_registry.is_authorized(device_id, token):
            return False, device_id, "ANDROID_DEVICE_UNAUTHORIZED"
        return True, device_id, "ok"

    def open_stream(self, request_iterator: Iterable[Any], context: grpc.ServicerContext) -> Iterable[Any]:
        """Accept an Android reverse stream and yield server commands."""
        try:
            first = next(iter(request_iterator))
        except StopIteration:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "ANDROID_REGISTER_REQUIRED")
        if first.WhichOneof("kind") != "register":
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "ANDROID_REGISTER_REQUIRED")

        register = first.register
        auth = register.auth
        connection_id = auth.connection_id or f"android_{uuid.uuid4().hex[:10]}"
        if not self.device_registry.verify_and_authorize(
            device_id=auth.device_id,
            pairing_token=auth.pairing_token,
            metadata=dict(register.metadata),
            device_model=register.device_model,
            manufacturer=register.manufacturer,
            android_version=register.android_version,
            app_version=register.app_version,
        ):
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "ANDROID_DEVICE_UNAUTHORIZED")

        session = AndroidStreamSession(
            device_id=auth.device_id,
            connection_id=connection_id,
            on_message=self._handle_stream_message,
            on_disconnect=self._handle_stream_disconnect,
        )
        self._sessions[connection_id] = session
        self._device_to_connection[auth.device_id] = connection_id
        self._last_connection_mode = "reverse_stream"
        if self._status_manager:
            self._status_manager.mark_online("android-server")
        self._publish_android_event(
            "android.connected",
            device_id=auth.device_id,
            connection_id=connection_id,
            payload={
                "connection_mode": "reverse_stream",
                "device_model": register.device_model,
                "capability_ids": list(register.capability_ids),
            },
            dedupe_key=f"android.connected:{auth.device_id}:{connection_id}",
        )

        session.start_reader(request_iterator)
        return session.command_generator()

    def send_approval_to_android(
        self,
        approval_id: str,
        title: str,
        body: str,
        state: str,
        summary: dict[str, Any],
    ) -> bool:
        """Deliver an approval request/update to Android overlay as one surface."""
        session = self._get_active_session()
        if session is not None:
            session.send_approval(approval_id, title, body, state, summary)
            return True
        result = self.invoke_capability(
            "android-server.approval.request",
            {
                "approval_id": approval_id,
                "title": title,
                "body": body,
                "summary_json": json.dumps(summary, ensure_ascii=False),
            },
        )
        return not result.get("error")

    def get_status(self) -> dict[str, Any]:
        """Return dashboard-friendly Android connection state."""
        session = self._get_active_session()
        online = session is not None or self._lan_client.is_available()
        devices = self.device_registry.list_devices()
        current_device = devices[-1] if devices else {}
        active_approvals = []
        if self._approval_manager is not None:
            active_approvals = [req.to_dict() for req in self._approval_manager.list_pending()]
        return {
            "online": online,
            "connection_mode": session.connection_mode if session else ("lan" if online else "offline"),
            "last_seen": session.last_seen_ms if session else current_device.get("last_seen_ms", 0),
            "device_model": current_device.get("device_model", ""),
            "devices": devices,
            "permission_status": dict(self._permission_status),
            "device_status": dict(self._last_device_status),
            "capability_availability": self.mapper.availability(self._permission_status),
            "active_approvals": active_approvals,
            "pairing_configured": self.device_registry.pairing_configured,
        }

    def _handle_stream_message(self, message: Any, session: AndroidStreamSession) -> None:
        kind = message.WhichOneof("kind")
        if kind == "heartbeat":
            auth = message.heartbeat.auth
            if not self.device_registry.is_authorized(auth.device_id, auth.pairing_token):
                session.close("unauthorized heartbeat")
                return
            self.device_registry.touch(auth.device_id)
            if self._status_manager:
                self._status_manager.update_heartbeat("android-server")
            self._publish_android_event(
                "android.heartbeat",
                device_id=auth.device_id,
                connection_id=session.connection_id,
                payload={
                    "battery_level": message.heartbeat.battery_level,
                    "screen_on": message.heartbeat.screen_on,
                    "locked": message.heartbeat.locked,
                },
                dedupe_key=f"android.heartbeat:{auth.device_id}",
            )
            return
        if kind == "event":
            auth = message.event.auth
            if not self.device_registry.is_authorized(auth.device_id, auth.pairing_token):
                session.close("unauthorized event")
                return
            self._publish_proto_event(message.event.event, auth.device_id, session.connection_id)
            return
        if kind == "command_result":
            auth = message.command_result.auth
            if not self.device_registry.is_authorized(auth.device_id, auth.pairing_token):
                session.close("unauthorized result")
                return
            session.handle_result(message.command_result)
            return
        if kind == "approval_decision":
            decision = message.approval_decision
            auth = decision.auth
            if not self.device_registry.is_authorized(auth.device_id, auth.pairing_token):
                session.close("unauthorized approval decision")
                return
            self._handle_approval_decision(decision, session)

    def _handle_stream_disconnect(self, session: AndroidStreamSession, reason: str) -> None:
        if self._sessions.get(session.connection_id) is session:
            self._sessions.pop(session.connection_id, None)
        if self._device_to_connection.get(session.device_id) == session.connection_id:
            self._device_to_connection.pop(session.device_id, None)
        self._publish_android_event(
            "android.disconnected",
            device_id=session.device_id,
            connection_id=session.connection_id,
            payload={"reason": reason},
            dedupe_key=f"android.disconnected:{session.device_id}:{session.connection_id}",
        )
        if self._status_manager:
            self._status_manager.mark_offline("android-server", reason)

    def _handle_approval_decision(self, decision: Any, session: AndroidStreamSession) -> None:
        if self._approval_manager is not None:
            surface = decision.surface_id or "android_overlay"
            user = decision.user or session.device_id
            if decision.approved:
                self._approval_manager.approve(decision.approval_id, channel=surface, user=user)
            elif decision.global_reject:
                self._approval_manager.global_reject(
                    decision.approval_id,
                    channel=surface,
                    user=user,
                    reason=decision.reason,
                )
            elif decision.rejected:
                self._approval_manager.reject(
                    decision.approval_id,
                    channel=surface,
                    user=user,
                    reason=decision.reason,
                )
        self._publish_android_event(
            "android.approval.decided",
            device_id=session.device_id,
            connection_id=session.connection_id,
            payload={
                "approval_id": decision.approval_id,
                "approved": decision.approved,
                "rejected": decision.rejected,
                "global_reject": decision.global_reject,
                "surface_id": decision.surface_id or "android_overlay",
            },
            dedupe_key=f"android.approval.decided:{decision.approval_id}:{decision.surface_id}",
            correlation_id=decision.approval_id,
        )

    def _after_invoke(self, capability_id: str, result: dict[str, Any]) -> None:
        if result.get("error"):
            return
        if capability_id == "android-server.permissions.get_status":
            permissions = result.get("permissions") or []
            self._permission_status = {
                item.get("name", ""): bool(item.get("granted", False))
                for item in permissions
                if isinstance(item, dict) and item.get("name")
            }
            self._last_device_status["locked"] = bool(result.get("screen_locked", False))
        elif capability_id == "android-server.accessibility.get_status":
            self._permission_status["accessibility"] = bool(result.get("enabled", False))
        elif capability_id == "android-server.device.get_status":
            self._last_device_status = dict(result)

    def _get_active_session(self) -> AndroidStreamSession | None:
        for session in list(self._sessions.values()):
            if not session.closed:
                self._last_connection_mode = "reverse_stream"
                return session
        return None

    def _publish_proto_event(self, event: Any, device_id: str, connection_id: str) -> None:
        attrs = dict(event.attributes)
        attrs.setdefault("device_id", device_id)
        attrs.setdefault("connection_id", connection_id)
        try:
            payload = json.loads(event.payload_json or "{}")
        except json.JSONDecodeError:
            payload = {"raw": event.payload_json}
        payload.setdefault("device_id", device_id)
        payload.setdefault("connection_id", connection_id)
        self._publish_android_event(
            event.event_type or "android.event",
            device_id=device_id,
            connection_id=connection_id,
            payload=payload,
            dedupe_key=event.dedupe_key or f"{event.event_type}:{device_id}",
            correlation_id=event.correlation_id,
            attributes=attrs,
        )

    def _publish_android_event(
        self,
        event_type: str,
        *,
        device_id: str,
        connection_id: str,
        payload: dict[str, Any],
        dedupe_key: str,
        correlation_id: str = "",
        attributes: dict[str, str] | None = None,
    ) -> None:
        payload = dict(payload)
        payload.setdefault("device_id", device_id)
        payload.setdefault("connection_id", connection_id)
        attrs = dict(attributes or {})
        attrs.setdefault("device_id", device_id)
        attrs.setdefault("connection_id", connection_id)
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            source_server_type=ServerType.ANDROID,
            source_server_id="android-server",
            timestamp_ms=int(time.time() * 1000),
            payload_json=json.dumps(payload, ensure_ascii=False),
            priority=EventPriority.NORMAL,
            dedupe_key=dedupe_key,
            correlation_id=correlation_id,
            attributes=attrs,
        )
        if self._event_manager is not None:
            self._event_manager.publish(event)
