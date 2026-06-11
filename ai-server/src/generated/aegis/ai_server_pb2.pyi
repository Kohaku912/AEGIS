from aegis import common_pb2 as _common_pb2
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
    __slots__ = ("approval_id", "approved_type", "rejected")
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVED_TYPE_FIELD_NUMBER: _ClassVar[int]
    REJECTED_FIELD_NUMBER: _ClassVar[int]
    approval_id: str
    approved_type: _common_pb2.ApprovalType
    rejected: bool
    def __init__(self, approval_id: _Optional[str] = ..., approved_type: _Optional[_Union[_common_pb2.ApprovalType, str]] = ..., rejected: _Optional[bool] = ...) -> None: ...

class ResolveApprovalResponse(_message.Message):
    __slots__ = ("status", "approval_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    approval_id: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., approval_id: _Optional[str] = ...) -> None: ...

class ListPendingApprovalsRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: str
    def __init__(self, server_id: _Optional[str] = ...) -> None: ...

class ListPendingApprovalsResponse(_message.Message):
    __slots__ = ("status", "approvals")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVALS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    approvals: _containers.RepeatedCompositeFieldContainer[_common_pb2.ApprovalRequest]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., approvals: _Optional[_Iterable[_Union[_common_pb2.ApprovalRequest, _Mapping]]] = ...) -> None: ...

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
