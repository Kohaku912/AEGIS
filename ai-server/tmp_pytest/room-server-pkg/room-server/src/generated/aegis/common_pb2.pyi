from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SafetyLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SAFETY_LEVEL_UNSPECIFIED: _ClassVar[SafetyLevel]
    LEVEL_0_READ: _ClassVar[SafetyLevel]
    LEVEL_1_SAFE_ACT: _ClassVar[SafetyLevel]
    LEVEL_2_APPROVAL: _ClassVar[SafetyLevel]
    LEVEL_3_RESTRICTED: _ClassVar[SafetyLevel]

class ServerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SERVER_TYPE_UNSPECIFIED: _ClassVar[ServerType]
    SERVER_TYPE_AI: _ClassVar[ServerType]
    SERVER_TYPE_PC: _ClassVar[ServerType]
    SERVER_TYPE_ANDROID: _ClassVar[ServerType]
    SERVER_TYPE_BROWSER: _ClassVar[ServerType]
    SERVER_TYPE_ROOM: _ClassVar[ServerType]
    SERVER_TYPE_DEV: _ClassVar[ServerType]

class ServerStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SERVER_STATUS_UNSPECIFIED: _ClassVar[ServerStatus]
    SERVER_STATUS_ONLINE: _ClassVar[ServerStatus]
    SERVER_STATUS_OFFLINE: _ClassVar[ServerStatus]
    SERVER_STATUS_DEGRADED: _ClassVar[ServerStatus]
    SERVER_STATUS_STARTING: _ClassVar[ServerStatus]

class EventSeverity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_SEVERITY_UNSPECIFIED: _ClassVar[EventSeverity]
    EVENT_SEVERITY_INFO: _ClassVar[EventSeverity]
    EVENT_SEVERITY_LOW: _ClassVar[EventSeverity]
    EVENT_SEVERITY_MODERATE: _ClassVar[EventSeverity]
    EVENT_SEVERITY_HIGH: _ClassVar[EventSeverity]
    EVENT_SEVERITY_CRITICAL: _ClassVar[EventSeverity]

class EventPriority(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_PRIORITY_UNSPECIFIED: _ClassVar[EventPriority]
    EVENT_PRIORITY_URGENT: _ClassVar[EventPriority]
    EVENT_PRIORITY_NORMAL: _ClassVar[EventPriority]
    EVENT_PRIORITY_BACKGROUND: _ClassVar[EventPriority]

class ApprovalStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    APPROVAL_STATUS_UNSPECIFIED: _ClassVar[ApprovalStatus]
    APPROVAL_STATUS_PENDING: _ClassVar[ApprovalStatus]
    APPROVAL_STATUS_APPROVED: _ClassVar[ApprovalStatus]
    APPROVAL_STATUS_REJECTED: _ClassVar[ApprovalStatus]
    APPROVAL_STATUS_EXPIRED: _ClassVar[ApprovalStatus]

class ApprovalType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    APPROVAL_TYPE_UNSPECIFIED: _ClassVar[ApprovalType]
    APPROVAL_TYPE_ONE_TIME: _ClassVar[ApprovalType]
    APPROVAL_TYPE_SESSION: _ClassVar[ApprovalType]

class AuditAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUDIT_ACTION_UNSPECIFIED: _ClassVar[AuditAction]
    AUDIT_ACTION_TOOL_INVOKED: _ClassVar[AuditAction]
    AUDIT_ACTION_TOOL_DENIED: _ClassVar[AuditAction]
    AUDIT_ACTION_APPROVAL_REQUESTED: _ClassVar[AuditAction]
    AUDIT_ACTION_APPROVAL_GRANTED: _ClassVar[AuditAction]
    AUDIT_ACTION_APPROVAL_REJECTED: _ClassVar[AuditAction]
    AUDIT_ACTION_EVENT_RECEIVED: _ClassVar[AuditAction]
    AUDIT_ACTION_TRIGGER_FIRED: _ClassVar[AuditAction]
    AUDIT_ACTION_POLICY_DECISION: _ClassVar[AuditAction]

class PolicyDecisionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    POLICY_DECISION_UNSPECIFIED: _ClassVar[PolicyDecisionType]
    POLICY_DECISION_ALLOW: _ClassVar[PolicyDecisionType]
    POLICY_DECISION_ASK_APPROVAL: _ClassVar[PolicyDecisionType]
    POLICY_DECISION_DENY: _ClassVar[PolicyDecisionType]
SAFETY_LEVEL_UNSPECIFIED: SafetyLevel
LEVEL_0_READ: SafetyLevel
LEVEL_1_SAFE_ACT: SafetyLevel
LEVEL_2_APPROVAL: SafetyLevel
LEVEL_3_RESTRICTED: SafetyLevel
SERVER_TYPE_UNSPECIFIED: ServerType
SERVER_TYPE_AI: ServerType
SERVER_TYPE_PC: ServerType
SERVER_TYPE_ANDROID: ServerType
SERVER_TYPE_BROWSER: ServerType
SERVER_TYPE_ROOM: ServerType
SERVER_TYPE_DEV: ServerType
SERVER_STATUS_UNSPECIFIED: ServerStatus
SERVER_STATUS_ONLINE: ServerStatus
SERVER_STATUS_OFFLINE: ServerStatus
SERVER_STATUS_DEGRADED: ServerStatus
SERVER_STATUS_STARTING: ServerStatus
EVENT_SEVERITY_UNSPECIFIED: EventSeverity
EVENT_SEVERITY_INFO: EventSeverity
EVENT_SEVERITY_LOW: EventSeverity
EVENT_SEVERITY_MODERATE: EventSeverity
EVENT_SEVERITY_HIGH: EventSeverity
EVENT_SEVERITY_CRITICAL: EventSeverity
EVENT_PRIORITY_UNSPECIFIED: EventPriority
EVENT_PRIORITY_URGENT: EventPriority
EVENT_PRIORITY_NORMAL: EventPriority
EVENT_PRIORITY_BACKGROUND: EventPriority
APPROVAL_STATUS_UNSPECIFIED: ApprovalStatus
APPROVAL_STATUS_PENDING: ApprovalStatus
APPROVAL_STATUS_APPROVED: ApprovalStatus
APPROVAL_STATUS_REJECTED: ApprovalStatus
APPROVAL_STATUS_EXPIRED: ApprovalStatus
APPROVAL_TYPE_UNSPECIFIED: ApprovalType
APPROVAL_TYPE_ONE_TIME: ApprovalType
APPROVAL_TYPE_SESSION: ApprovalType
AUDIT_ACTION_UNSPECIFIED: AuditAction
AUDIT_ACTION_TOOL_INVOKED: AuditAction
AUDIT_ACTION_TOOL_DENIED: AuditAction
AUDIT_ACTION_APPROVAL_REQUESTED: AuditAction
AUDIT_ACTION_APPROVAL_GRANTED: AuditAction
AUDIT_ACTION_APPROVAL_REJECTED: AuditAction
AUDIT_ACTION_EVENT_RECEIVED: AuditAction
AUDIT_ACTION_TRIGGER_FIRED: AuditAction
AUDIT_ACTION_POLICY_DECISION: AuditAction
POLICY_DECISION_UNSPECIFIED: PolicyDecisionType
POLICY_DECISION_ALLOW: PolicyDecisionType
POLICY_DECISION_ASK_APPROVAL: PolicyDecisionType
POLICY_DECISION_DENY: PolicyDecisionType

class Parameter(_message.Message):
    __slots__ = ("name", "type", "description", "required", "default_value", "validation")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    description: str
    required: bool
    default_value: str
    validation: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., description: _Optional[str] = ..., required: _Optional[bool] = ..., default_value: _Optional[str] = ..., validation: _Optional[str] = ...) -> None: ...

class Value(_message.Message):
    __slots__ = ("string_value", "int_value", "double_value", "bool_value", "bytes_value", "json_value")
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    BYTES_VALUE_FIELD_NUMBER: _ClassVar[int]
    JSON_VALUE_FIELD_NUMBER: _ClassVar[int]
    string_value: str
    int_value: int
    double_value: float
    bool_value: bool
    bytes_value: bytes
    json_value: str
    def __init__(self, string_value: _Optional[str] = ..., int_value: _Optional[int] = ..., double_value: _Optional[float] = ..., bool_value: _Optional[bool] = ..., bytes_value: _Optional[bytes] = ..., json_value: _Optional[str] = ...) -> None: ...

class Status(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("code", "message", "detail", "capability_id", "required_level")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_LEVEL_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    capability_id: str
    required_level: SafetyLevel
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., capability_id: _Optional[str] = ..., required_level: _Optional[_Union[SafetyLevel, str]] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: str
    def __init__(self, server_id: _Optional[str] = ...) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "server_status", "uptime_ms", "version")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVER_STATUS_FIELD_NUMBER: _ClassVar[int]
    UPTIME_MS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    status: Status
    server_status: ServerStatus
    uptime_ms: int
    version: str
    def __init__(self, status: _Optional[_Union[Status, _Mapping]] = ..., server_status: _Optional[_Union[ServerStatus, str]] = ..., uptime_ms: _Optional[int] = ..., version: _Optional[str] = ...) -> None: ...

class Capability(_message.Message):
    __slots__ = ("id", "name", "description", "server_type", "server_id", "input_schema", "output_schema", "safety_level", "requires_approval", "side_effects", "tags", "timeout_ms", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SERVER_TYPE_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SAFETY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    SIDE_EFFECTS_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    server_type: ServerType
    server_id: str
    input_schema: str
    output_schema: str
    safety_level: SafetyLevel
    requires_approval: bool
    side_effects: _containers.RepeatedScalarFieldContainer[str]
    tags: _containers.RepeatedScalarFieldContainer[str]
    timeout_ms: int
    version: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., server_type: _Optional[_Union[ServerType, str]] = ..., server_id: _Optional[str] = ..., input_schema: _Optional[str] = ..., output_schema: _Optional[str] = ..., safety_level: _Optional[_Union[SafetyLevel, str]] = ..., requires_approval: _Optional[bool] = ..., side_effects: _Optional[_Iterable[str]] = ..., tags: _Optional[_Iterable[str]] = ..., timeout_ms: _Optional[int] = ..., version: _Optional[str] = ...) -> None: ...

class Tool(_message.Message):
    __slots__ = ("id", "capability_id", "server_id", "config_json", "enabled", "display_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_JSON_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    capability_id: str
    server_id: str
    config_json: str
    enabled: bool
    display_name: str
    def __init__(self, id: _Optional[str] = ..., capability_id: _Optional[str] = ..., server_id: _Optional[str] = ..., config_json: _Optional[str] = ..., enabled: _Optional[bool] = ..., display_name: _Optional[str] = ...) -> None: ...

class ServerInfo(_message.Message):
    __slots__ = ("server_id", "server_type", "version", "status", "capability_ids", "host", "port", "started_at_ms", "last_heartbeat_ms", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    SERVER_TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_IDS_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    LAST_HEARTBEAT_MS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    server_id: str
    server_type: ServerType
    version: str
    status: ServerStatus
    capability_ids: _containers.RepeatedScalarFieldContainer[str]
    host: str
    port: int
    started_at_ms: int
    last_heartbeat_ms: int
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, server_id: _Optional[str] = ..., server_type: _Optional[_Union[ServerType, str]] = ..., version: _Optional[str] = ..., status: _Optional[_Union[ServerStatus, str]] = ..., capability_ids: _Optional[_Iterable[str]] = ..., host: _Optional[str] = ..., port: _Optional[int] = ..., started_at_ms: _Optional[int] = ..., last_heartbeat_ms: _Optional[int] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("event_id", "event_type", "source_server_type", "source_server_id", "timestamp_ms", "payload_json", "severity", "priority", "dedupe_key", "correlation_id", "requires_attention", "attributes")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SERVER_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_JSON_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    DEDUPE_KEY_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_ATTENTION_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    event_type: str
    source_server_type: ServerType
    source_server_id: str
    timestamp_ms: int
    payload_json: str
    severity: EventSeverity
    priority: EventPriority
    dedupe_key: str
    correlation_id: str
    requires_attention: bool
    attributes: _containers.ScalarMap[str, str]
    def __init__(self, event_id: _Optional[str] = ..., event_type: _Optional[str] = ..., source_server_type: _Optional[_Union[ServerType, str]] = ..., source_server_id: _Optional[str] = ..., timestamp_ms: _Optional[int] = ..., payload_json: _Optional[str] = ..., severity: _Optional[_Union[EventSeverity, str]] = ..., priority: _Optional[_Union[EventPriority, str]] = ..., dedupe_key: _Optional[str] = ..., correlation_id: _Optional[str] = ..., requires_attention: _Optional[bool] = ..., attributes: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ToolInvocationRequest(_message.Message):
    __slots__ = ("capability_id", "invocation_id", "caller", "params_json", "is_approved", "approval_id")
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    INVOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    CALLER_FIELD_NUMBER: _ClassVar[int]
    PARAMS_JSON_FIELD_NUMBER: _ClassVar[int]
    IS_APPROVED_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    capability_id: str
    invocation_id: str
    caller: str
    params_json: str
    is_approved: bool
    approval_id: str
    def __init__(self, capability_id: _Optional[str] = ..., invocation_id: _Optional[str] = ..., caller: _Optional[str] = ..., params_json: _Optional[str] = ..., is_approved: _Optional[bool] = ..., approval_id: _Optional[str] = ...) -> None: ...

class ToolInvocationResult(_message.Message):
    __slots__ = ("status", "capability_id", "invocation_id", "output_json", "error", "duration_ms", "was_approved")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    INVOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_JSON_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    WAS_APPROVED_FIELD_NUMBER: _ClassVar[int]
    status: Status
    capability_id: str
    invocation_id: str
    output_json: str
    error: str
    duration_ms: int
    was_approved: bool
    def __init__(self, status: _Optional[_Union[Status, _Mapping]] = ..., capability_id: _Optional[str] = ..., invocation_id: _Optional[str] = ..., output_json: _Optional[str] = ..., error: _Optional[str] = ..., duration_ms: _Optional[int] = ..., was_approved: _Optional[bool] = ...) -> None: ...

class PolicyDecision(_message.Message):
    __slots__ = ("decision_id", "decision", "reason", "capability_id", "required_level", "audit_required")
    DECISION_ID_FIELD_NUMBER: _ClassVar[int]
    DECISION_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_LEVEL_FIELD_NUMBER: _ClassVar[int]
    AUDIT_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    decision_id: str
    decision: PolicyDecisionType
    reason: str
    capability_id: str
    required_level: SafetyLevel
    audit_required: bool
    def __init__(self, decision_id: _Optional[str] = ..., decision: _Optional[_Union[PolicyDecisionType, str]] = ..., reason: _Optional[str] = ..., capability_id: _Optional[str] = ..., required_level: _Optional[_Union[SafetyLevel, str]] = ..., audit_required: _Optional[bool] = ...) -> None: ...

class ApprovalRequest(_message.Message):
    __slots__ = ("approval_id", "capability_id", "tool_name", "requested_action", "human_readable_summary", "risk_explanation", "payload_preview", "safety_level", "status", "approved_type", "created_at_ms", "expires_at_ms")
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    TOOL_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_ACTION_FIELD_NUMBER: _ClassVar[int]
    HUMAN_READABLE_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    RISK_EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    SAFETY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVED_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_MS_FIELD_NUMBER: _ClassVar[int]
    approval_id: str
    capability_id: str
    tool_name: str
    requested_action: str
    human_readable_summary: str
    risk_explanation: str
    payload_preview: str
    safety_level: SafetyLevel
    status: ApprovalStatus
    approved_type: ApprovalType
    created_at_ms: int
    expires_at_ms: int
    def __init__(self, approval_id: _Optional[str] = ..., capability_id: _Optional[str] = ..., tool_name: _Optional[str] = ..., requested_action: _Optional[str] = ..., human_readable_summary: _Optional[str] = ..., risk_explanation: _Optional[str] = ..., payload_preview: _Optional[str] = ..., safety_level: _Optional[_Union[SafetyLevel, str]] = ..., status: _Optional[_Union[ApprovalStatus, str]] = ..., approved_type: _Optional[_Union[ApprovalType, str]] = ..., created_at_ms: _Optional[int] = ..., expires_at_ms: _Optional[int] = ...) -> None: ...

class AuditRecord(_message.Message):
    __slots__ = ("record_id", "action", "timestamp_ms", "actor", "capability_id", "detail_json", "safety_level", "server_id", "correlation_id")
    RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    DETAIL_JSON_FIELD_NUMBER: _ClassVar[int]
    SAFETY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    record_id: str
    action: AuditAction
    timestamp_ms: int
    actor: str
    capability_id: str
    detail_json: str
    safety_level: SafetyLevel
    server_id: str
    correlation_id: str
    def __init__(self, record_id: _Optional[str] = ..., action: _Optional[_Union[AuditAction, str]] = ..., timestamp_ms: _Optional[int] = ..., actor: _Optional[str] = ..., capability_id: _Optional[str] = ..., detail_json: _Optional[str] = ..., safety_level: _Optional[_Union[SafetyLevel, str]] = ..., server_id: _Optional[str] = ..., correlation_id: _Optional[str] = ...) -> None: ...
