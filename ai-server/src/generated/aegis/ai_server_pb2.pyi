from generated.aegis import common_pb2 as _common_pb2
from generated.aegis import android_server_pb2 as _android_server_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RegisterServerRequest(_message.Message):
    __slots__ = ("server_info",)
    SERVER_INFO_FIELD_NUMBER: _ClassVar[int]
    server_info: _common_pb2.ServerInfo
    def __init__(self, server_info: _Optional[_Union[_common_pb2.ServerInfo, _Mapping]] = ...) -> None: ...

class RegisterServerResponse(_message.Message):
    __slots__ = ("status", "server_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    server_id: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., server_id: _Optional[str] = ...) -> None: ...

class UnregisterServerRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: str
    def __init__(self, server_id: _Optional[str] = ...) -> None: ...

class UnregisterServerResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class RegisterCapabilityRequest(_message.Message):
    __slots__ = ("capability",)
    CAPABILITY_FIELD_NUMBER: _ClassVar[int]
    capability: _common_pb2.Capability
    def __init__(self, capability: _Optional[_Union[_common_pb2.Capability, _Mapping]] = ...) -> None: ...

class RegisterCapabilityResponse(_message.Message):
    __slots__ = ("status", "capability_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    capability_id: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., capability_id: _Optional[str] = ...) -> None: ...

class UnregisterCapabilityRequest(_message.Message):
    __slots__ = ("capability_id", "server_id")
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    capability_id: str
    server_id: str
    def __init__(self, capability_id: _Optional[str] = ..., server_id: _Optional[str] = ...) -> None: ...

class UnregisterCapabilityResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class ListCapabilitiesRequest(_message.Message):
    __slots__ = ("server_type", "max_safety_level", "tags", "search_query")
    SERVER_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAX_SAFETY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_QUERY_FIELD_NUMBER: _ClassVar[int]
    server_type: _common_pb2.ServerType
    max_safety_level: _common_pb2.SafetyLevel
    tags: _containers.RepeatedScalarFieldContainer[str]
    search_query: str
    def __init__(self, server_type: _Optional[_Union[_common_pb2.ServerType, str]] = ..., max_safety_level: _Optional[_Union[_common_pb2.SafetyLevel, str]] = ..., tags: _Optional[_Iterable[str]] = ..., search_query: _Optional[str] = ...) -> None: ...

class ListCapabilitiesResponse(_message.Message):
    __slots__ = ("status", "capabilities")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    capabilities: _containers.RepeatedCompositeFieldContainer[_common_pb2.Capability]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., capabilities: _Optional[_Iterable[_Union[_common_pb2.Capability, _Mapping]]] = ...) -> None: ...

class GetCapabilityRequest(_message.Message):
    __slots__ = ("capability_id",)
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    capability_id: str
    def __init__(self, capability_id: _Optional[str] = ...) -> None: ...

class PushEventRequest(_message.Message):
    __slots__ = ("event",)
    EVENT_FIELD_NUMBER: _ClassVar[int]
    event: _common_pb2.Event
    def __init__(self, event: _Optional[_Union[_common_pb2.Event, _Mapping]] = ...) -> None: ...

class PushEventResponse(_message.Message):
    __slots__ = ("status", "event_id", "deduplicated")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    DEDUPLICATED_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    event_id: str
    deduplicated: bool
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., event_id: _Optional[str] = ..., deduplicated: _Optional[bool] = ...) -> None: ...

class StreamEventsRequest(_message.Message):
    __slots__ = ("server_id", "max_events_per_second")
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_EVENTS_PER_SECOND_FIELD_NUMBER: _ClassVar[int]
    server_id: str
    max_events_per_second: int
    def __init__(self, server_id: _Optional[str] = ..., max_events_per_second: _Optional[int] = ...) -> None: ...

class SubscribeEventsRequest(_message.Message):
    __slots__ = ("source_type", "min_severity", "min_priority", "event_type_pattern")
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MIN_SEVERITY_FIELD_NUMBER: _ClassVar[int]
    MIN_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_PATTERN_FIELD_NUMBER: _ClassVar[int]
    source_type: _common_pb2.ServerType
    min_severity: _common_pb2.EventSeverity
    min_priority: _common_pb2.EventPriority
    event_type_pattern: str
    def __init__(self, source_type: _Optional[_Union[_common_pb2.ServerType, str]] = ..., min_severity: _Optional[_Union[_common_pb2.EventSeverity, str]] = ..., min_priority: _Optional[_Union[_common_pb2.EventPriority, str]] = ..., event_type_pattern: _Optional[str] = ...) -> None: ...

class RequestApprovalRequest(_message.Message):
    __slots__ = ("capability_id", "tool_name", "requested_action", "human_readable_summary", "risk_explanation", "payload_preview", "safety_level", "caller")
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    TOOL_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_ACTION_FIELD_NUMBER: _ClassVar[int]
    HUMAN_READABLE_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    RISK_EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    SAFETY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    CALLER_FIELD_NUMBER: _ClassVar[int]
    capability_id: str
    tool_name: str
    requested_action: str
    human_readable_summary: str
    risk_explanation: str
    payload_preview: str
    safety_level: _common_pb2.SafetyLevel
    caller: str
    def __init__(self, capability_id: _Optional[str] = ..., tool_name: _Optional[str] = ..., requested_action: _Optional[str] = ..., human_readable_summary: _Optional[str] = ..., risk_explanation: _Optional[str] = ..., payload_preview: _Optional[str] = ..., safety_level: _Optional[_Union[_common_pb2.SafetyLevel, str]] = ..., caller: _Optional[str] = ...) -> None: ...

class ResolveApprovalRequest(_message.Message):
    __slots__ = ("approval_id", "approved_type", "rejected", "global_reject", "surface_id", "user", "reason", "auth")
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVED_TYPE_FIELD_NUMBER: _ClassVar[int]
    REJECTED_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_REJECT_FIELD_NUMBER: _ClassVar[int]
    SURFACE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    AUTH_FIELD_NUMBER: _ClassVar[int]
    approval_id: str
    approved_type: _common_pb2.ApprovalType
    rejected: bool
    global_reject: bool
    surface_id: str
    user: str
    reason: str
    auth: _android_server_pb2.AndroidAuth
    def __init__(self, approval_id: _Optional[str] = ..., approved_type: _Optional[_Union[_common_pb2.ApprovalType, str]] = ..., rejected: _Optional[bool] = ..., global_reject: _Optional[bool] = ..., surface_id: _Optional[str] = ..., user: _Optional[str] = ..., reason: _Optional[str] = ..., auth: _Optional[_Union[_android_server_pb2.AndroidAuth, _Mapping]] = ...) -> None: ...

class ResolveApprovalResponse(_message.Message):
    __slots__ = ("status", "approval_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    approval_id: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., approval_id: _Optional[str] = ...) -> None: ...

class ListPendingApprovalsRequest(_message.Message):
    __slots__ = ("server_id", "auth")
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    AUTH_FIELD_NUMBER: _ClassVar[int]
    server_id: str
    auth: _android_server_pb2.AndroidAuth
    def __init__(self, server_id: _Optional[str] = ..., auth: _Optional[_Union[_android_server_pb2.AndroidAuth, _Mapping]] = ...) -> None: ...

class ListPendingApprovalsResponse(_message.Message):
    __slots__ = ("status", "approvals")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVALS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    approvals: _containers.RepeatedCompositeFieldContainer[_common_pb2.ApprovalRequest]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., approvals: _Optional[_Iterable[_Union[_common_pb2.ApprovalRequest, _Mapping]]] = ...) -> None: ...

class ChatRequest(_message.Message):
    __slots__ = ("conversation_id", "text", "device_id", "context", "auth")
    class ContextEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONVERSATION_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    AUTH_FIELD_NUMBER: _ClassVar[int]
    conversation_id: str
    text: str
    device_id: str
    context: _containers.ScalarMap[str, str]
    auth: _android_server_pb2.AndroidAuth
    def __init__(self, conversation_id: _Optional[str] = ..., text: _Optional[str] = ..., device_id: _Optional[str] = ..., context: _Optional[_Mapping[str, str]] = ..., auth: _Optional[_Union[_android_server_pb2.AndroidAuth, _Mapping]] = ...) -> None: ...

class ChatResponse(_message.Message):
    __slots__ = ("status", "conversation_id", "response", "approval_needed", "approval_id", "tool_results_json")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONVERSATION_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_NEEDED_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    TOOL_RESULTS_JSON_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    conversation_id: str
    response: str
    approval_needed: bool
    approval_id: str
    tool_results_json: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., conversation_id: _Optional[str] = ..., response: _Optional[str] = ..., approval_needed: _Optional[bool] = ..., approval_id: _Optional[str] = ..., tool_results_json: _Optional[str] = ...) -> None: ...

class MobileDashboardStateRequest(_message.Message):
    __slots__ = ("device_id", "history_limit", "auth")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HISTORY_LIMIT_FIELD_NUMBER: _ClassVar[int]
    AUTH_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    history_limit: int
    auth: _android_server_pb2.AndroidAuth
    def __init__(self, device_id: _Optional[str] = ..., history_limit: _Optional[int] = ..., auth: _Optional[_Union[_android_server_pb2.AndroidAuth, _Mapping]] = ...) -> None: ...

class MobileServerStatus(_message.Message):
    __slots__ = ("server_id", "label", "status", "mode", "detail")
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    server_id: str
    label: str
    status: str
    mode: str
    detail: str
    def __init__(self, server_id: _Optional[str] = ..., label: _Optional[str] = ..., status: _Optional[str] = ..., mode: _Optional[str] = ..., detail: _Optional[str] = ...) -> None: ...

class ChatHistoryMessage(_message.Message):
    __slots__ = ("message_id", "role", "text", "timestamp_ms", "image", "conversation_id", "source")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    CONVERSATION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    role: str
    text: str
    timestamp_ms: int
    image: str
    conversation_id: str
    source: str
    def __init__(self, message_id: _Optional[str] = ..., role: _Optional[str] = ..., text: _Optional[str] = ..., timestamp_ms: _Optional[int] = ..., image: _Optional[str] = ..., conversation_id: _Optional[str] = ..., source: _Optional[str] = ...) -> None: ...

class MobileDashboardStateResponse(_message.Message):
    __slots__ = ("status", "server_statuses", "chat_history", "warnings")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVER_STATUSES_FIELD_NUMBER: _ClassVar[int]
    CHAT_HISTORY_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    server_statuses: _containers.RepeatedCompositeFieldContainer[MobileServerStatus]
    chat_history: _containers.RepeatedCompositeFieldContainer[ChatHistoryMessage]
    warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., server_statuses: _Optional[_Iterable[_Union[MobileServerStatus, _Mapping]]] = ..., chat_history: _Optional[_Iterable[_Union[ChatHistoryMessage, _Mapping]]] = ..., warnings: _Optional[_Iterable[str]] = ...) -> None: ...

class UiOverviewRequest(_message.Message):
    __slots__ = ("surface_id", "auth")
    SURFACE_ID_FIELD_NUMBER: _ClassVar[int]
    AUTH_FIELD_NUMBER: _ClassVar[int]
    surface_id: str
    auth: _android_server_pb2.AndroidAuth
    def __init__(self, surface_id: _Optional[str] = ..., auth: _Optional[_Union[_android_server_pb2.AndroidAuth, _Mapping]] = ...) -> None: ...

class UiOverviewResponse(_message.Message):
    __slots__ = ("status", "overview_json", "generated_at_ms")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OVERVIEW_JSON_FIELD_NUMBER: _ClassVar[int]
    GENERATED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    overview_json: str
    generated_at_ms: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., overview_json: _Optional[str] = ..., generated_at_ms: _Optional[int] = ...) -> None: ...

class UiEventStreamRequest(_message.Message):
    __slots__ = ("surface_id", "auth")
    SURFACE_ID_FIELD_NUMBER: _ClassVar[int]
    AUTH_FIELD_NUMBER: _ClassVar[int]
    surface_id: str
    auth: _android_server_pb2.AndroidAuth
    def __init__(self, surface_id: _Optional[str] = ..., auth: _Optional[_Union[_android_server_pb2.AndroidAuth, _Mapping]] = ...) -> None: ...

class UiEvent(_message.Message):
    __slots__ = ("event_type", "event_json", "timestamp_ms")
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    EVENT_JSON_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    event_type: str
    event_json: str
    timestamp_ms: int
    def __init__(self, event_type: _Optional[str] = ..., event_json: _Optional[str] = ..., timestamp_ms: _Optional[int] = ...) -> None: ...

class QueryAuditLogRequest(_message.Message):
    __slots__ = ("since_ms", "until_ms", "action", "capability_id", "max_records")
    SINCE_MS_FIELD_NUMBER: _ClassVar[int]
    UNTIL_MS_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_RECORDS_FIELD_NUMBER: _ClassVar[int]
    since_ms: int
    until_ms: int
    action: _common_pb2.AuditAction
    capability_id: str
    max_records: int
    def __init__(self, since_ms: _Optional[int] = ..., until_ms: _Optional[int] = ..., action: _Optional[_Union[_common_pb2.AuditAction, str]] = ..., capability_id: _Optional[str] = ..., max_records: _Optional[int] = ...) -> None: ...

class QueryAuditLogResponse(_message.Message):
    __slots__ = ("status", "records")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    records: _containers.RepeatedCompositeFieldContainer[_common_pb2.AuditRecord]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., records: _Optional[_Iterable[_Union[_common_pb2.AuditRecord, _Mapping]]] = ...) -> None: ...
