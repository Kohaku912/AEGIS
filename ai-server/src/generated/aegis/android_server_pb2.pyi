from aegis import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AndroidAuth(_message.Message):
    __slots__ = ("device_id", "pairing_token", "connection_id")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PAIRING_TOKEN_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    pairing_token: str
    connection_id: str
    def __init__(self, device_id: _Optional[str] = ..., pairing_token: _Optional[str] = ..., connection_id: _Optional[str] = ...) -> None: ...

class AndroidRegister(_message.Message):
    __slots__ = ("auth", "device_model", "manufacturer", "android_version", "app_version", "capability_ids", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    AUTH_FIELD_NUMBER: _ClassVar[int]
    DEVICE_MODEL_FIELD_NUMBER: _ClassVar[int]
    MANUFACTURER_FIELD_NUMBER: _ClassVar[int]
    ANDROID_VERSION_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    auth: AndroidAuth
    device_model: str
    manufacturer: str
    android_version: str
    app_version: str
    capability_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, auth: _Optional[_Union[AndroidAuth, _Mapping]] = ..., device_model: _Optional[str] = ..., manufacturer: _Optional[str] = ..., android_version: _Optional[str] = ..., app_version: _Optional[str] = ..., capability_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class AndroidHeartbeat(_message.Message):
    __slots__ = ("auth", "timestamp_ms", "battery_level", "screen_on", "locked")
    AUTH_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    BATTERY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    SCREEN_ON_FIELD_NUMBER: _ClassVar[int]
    LOCKED_FIELD_NUMBER: _ClassVar[int]
    auth: AndroidAuth
    timestamp_ms: int
    battery_level: int
    screen_on: bool
    locked: bool
    def __init__(self, auth: _Optional[_Union[AndroidAuth, _Mapping]] = ..., timestamp_ms: _Optional[int] = ..., battery_level: _Optional[int] = ..., screen_on: _Optional[bool] = ..., locked: _Optional[bool] = ...) -> None: ...

class AndroidEventEnvelope(_message.Message):
    __slots__ = ("auth", "event")
    AUTH_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    auth: AndroidAuth
    event: _common_pb2.Event
    def __init__(self, auth: _Optional[_Union[AndroidAuth, _Mapping]] = ..., event: _Optional[_Union[_common_pb2.Event, _Mapping]] = ...) -> None: ...

class AndroidCommandResult(_message.Message):
    __slots__ = ("auth", "command_id", "capability_id", "status", "result_json")
    AUTH_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_JSON_FIELD_NUMBER: _ClassVar[int]
    auth: AndroidAuth
    command_id: str
    capability_id: str
    status: _common_pb2.Status
    result_json: str
    def __init__(self, auth: _Optional[_Union[AndroidAuth, _Mapping]] = ..., command_id: _Optional[str] = ..., capability_id: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., result_json: _Optional[str] = ...) -> None: ...

class AndroidApprovalDecision(_message.Message):
    __slots__ = ("auth", "approval_id", "approved", "rejected", "global_reject", "surface_id", "user", "reason")
    AUTH_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVED_FIELD_NUMBER: _ClassVar[int]
    REJECTED_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_REJECT_FIELD_NUMBER: _ClassVar[int]
    SURFACE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    auth: AndroidAuth
    approval_id: str
    approved: bool
    rejected: bool
    global_reject: bool
    surface_id: str
    user: str
    reason: str
    def __init__(self, auth: _Optional[_Union[AndroidAuth, _Mapping]] = ..., approval_id: _Optional[str] = ..., approved: _Optional[bool] = ..., rejected: _Optional[bool] = ..., global_reject: _Optional[bool] = ..., surface_id: _Optional[str] = ..., user: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class AndroidClientMessage(_message.Message):
    __slots__ = ("register", "heartbeat", "event", "command_result", "approval_decision")
    REGISTER_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    COMMAND_RESULT_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_DECISION_FIELD_NUMBER: _ClassVar[int]
    register: AndroidRegister
    heartbeat: AndroidHeartbeat
    event: AndroidEventEnvelope
    command_result: AndroidCommandResult
    approval_decision: AndroidApprovalDecision
    def __init__(self, register: _Optional[_Union[AndroidRegister, _Mapping]] = ..., heartbeat: _Optional[_Union[AndroidHeartbeat, _Mapping]] = ..., event: _Optional[_Union[AndroidEventEnvelope, _Mapping]] = ..., command_result: _Optional[_Union[AndroidCommandResult, _Mapping]] = ..., approval_decision: _Optional[_Union[AndroidApprovalDecision, _Mapping]] = ...) -> None: ...

class AndroidStreamAck(_message.Message):
    __slots__ = ("connection_id", "status")
    CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    connection_id: str
    status: _common_pb2.Status
    def __init__(self, connection_id: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class AndroidInvokeCommand(_message.Message):
    __slots__ = ("command_id", "capability_id", "method", "params_json", "timeout_ms", "correlation_id")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_ID_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    PARAMS_JSON_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    capability_id: str
    method: str
    params_json: str
    timeout_ms: int
    correlation_id: str
    def __init__(self, command_id: _Optional[str] = ..., capability_id: _Optional[str] = ..., method: _Optional[str] = ..., params_json: _Optional[str] = ..., timeout_ms: _Optional[int] = ..., correlation_id: _Optional[str] = ...) -> None: ...

class AndroidApprovalCommand(_message.Message):
    __slots__ = ("approval_id", "title", "body", "state", "summary_json")
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_JSON_FIELD_NUMBER: _ClassVar[int]
    approval_id: str
    title: str
    body: str
    state: str
    summary_json: str
    def __init__(self, approval_id: _Optional[str] = ..., title: _Optional[str] = ..., body: _Optional[str] = ..., state: _Optional[str] = ..., summary_json: _Optional[str] = ...) -> None: ...

class AndroidServerHeartbeat(_message.Message):
    __slots__ = ("timestamp_ms",)
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    timestamp_ms: int
    def __init__(self, timestamp_ms: _Optional[int] = ...) -> None: ...

class AndroidStopCommand(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class AndroidServerCommand(_message.Message):
    __slots__ = ("ack", "invoke", "approval_request", "heartbeat", "stop")
    ACK_FIELD_NUMBER: _ClassVar[int]
    INVOKE_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    ack: AndroidStreamAck
    invoke: AndroidInvokeCommand
    approval_request: AndroidApprovalCommand
    heartbeat: AndroidServerHeartbeat
    stop: AndroidStopCommand
    def __init__(self, ack: _Optional[_Union[AndroidStreamAck, _Mapping]] = ..., invoke: _Optional[_Union[AndroidInvokeCommand, _Mapping]] = ..., approval_request: _Optional[_Union[AndroidApprovalCommand, _Mapping]] = ..., heartbeat: _Optional[_Union[AndroidServerHeartbeat, _Mapping]] = ..., stop: _Optional[_Union[AndroidStopCommand, _Mapping]] = ...) -> None: ...

class GetAndroidScreenshotRequest(_message.Message):
    __slots__ = ("quality",)
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    quality: int
    def __init__(self, quality: _Optional[int] = ...) -> None: ...

class GetAndroidScreenshotResponse(_message.Message):
    __slots__ = ("status", "image_data", "width", "height")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    image_data: bytes
    width: int
    height: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., image_data: _Optional[bytes] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class GetCurrentAppRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCurrentAppResponse(_message.Message):
    __slots__ = ("status", "package_name", "activity_name", "app_name")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_NAME_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    package_name: str
    activity_name: str
    app_name: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., package_name: _Optional[str] = ..., activity_name: _Optional[str] = ..., app_name: _Optional[str] = ...) -> None: ...

class GetUiTreeRequest(_message.Message):
    __slots__ = ("include_invisible",)
    INCLUDE_INVISIBLE_FIELD_NUMBER: _ClassVar[int]
    include_invisible: bool
    def __init__(self, include_invisible: _Optional[bool] = ...) -> None: ...

class UiNode(_message.Message):
    __slots__ = ("class_name", "text", "content_desc", "resource_id", "is_clickable", "is_focusable", "x", "y", "width", "height", "children")
    CLASS_NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_DESC_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    IS_CLICKABLE_FIELD_NUMBER: _ClassVar[int]
    IS_FOCUSABLE_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    class_name: str
    text: str
    content_desc: str
    resource_id: str
    is_clickable: bool
    is_focusable: bool
    x: int
    y: int
    width: int
    height: int
    children: _containers.RepeatedCompositeFieldContainer[UiNode]
    def __init__(self, class_name: _Optional[str] = ..., text: _Optional[str] = ..., content_desc: _Optional[str] = ..., resource_id: _Optional[str] = ..., is_clickable: _Optional[bool] = ..., is_focusable: _Optional[bool] = ..., x: _Optional[int] = ..., y: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., children: _Optional[_Iterable[_Union[UiNode, _Mapping]]] = ...) -> None: ...

class GetUiTreeResponse(_message.Message):
    __slots__ = ("status", "root")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ROOT_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    root: UiNode
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., root: _Optional[_Union[UiNode, _Mapping]] = ...) -> None: ...

class GetNotificationsRequest(_message.Message):
    __slots__ = ("max_count",)
    MAX_COUNT_FIELD_NUMBER: _ClassVar[int]
    max_count: int
    def __init__(self, max_count: _Optional[int] = ...) -> None: ...

class AndroidNotification(_message.Message):
    __slots__ = ("key", "package_name", "app_name", "title", "text", "posted_ms", "is_ongoing", "is_clearable")
    KEY_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    POSTED_MS_FIELD_NUMBER: _ClassVar[int]
    IS_ONGOING_FIELD_NUMBER: _ClassVar[int]
    IS_CLEARABLE_FIELD_NUMBER: _ClassVar[int]
    key: str
    package_name: str
    app_name: str
    title: str
    text: str
    posted_ms: int
    is_ongoing: bool
    is_clearable: bool
    def __init__(self, key: _Optional[str] = ..., package_name: _Optional[str] = ..., app_name: _Optional[str] = ..., title: _Optional[str] = ..., text: _Optional[str] = ..., posted_ms: _Optional[int] = ..., is_ongoing: _Optional[bool] = ..., is_clearable: _Optional[bool] = ...) -> None: ...

class GetNotificationsResponse(_message.Message):
    __slots__ = ("status", "notifications")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    notifications: _containers.RepeatedCompositeFieldContainer[AndroidNotification]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., notifications: _Optional[_Iterable[_Union[AndroidNotification, _Mapping]]] = ...) -> None: ...

class GetPermissionStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AndroidPermissionState(_message.Message):
    __slots__ = ("name", "granted", "detail")
    NAME_FIELD_NUMBER: _ClassVar[int]
    GRANTED_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    name: str
    granted: bool
    detail: str
    def __init__(self, name: _Optional[str] = ..., granted: _Optional[bool] = ..., detail: _Optional[str] = ...) -> None: ...

class GetPermissionStatusResponse(_message.Message):
    __slots__ = ("status", "permissions", "screen_locked")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    SCREEN_LOCKED_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    permissions: _containers.RepeatedCompositeFieldContainer[AndroidPermissionState]
    screen_locked: bool
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., permissions: _Optional[_Iterable[_Union[AndroidPermissionState, _Mapping]]] = ..., screen_locked: _Optional[bool] = ...) -> None: ...

class AndroidGetDeviceStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AndroidGetDeviceStatusResponse(_message.Message):
    __slots__ = ("status", "device_id", "model", "manufacturer", "android_version", "battery_level", "charging", "screen_on", "locked")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    MANUFACTURER_FIELD_NUMBER: _ClassVar[int]
    ANDROID_VERSION_FIELD_NUMBER: _ClassVar[int]
    BATTERY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    CHARGING_FIELD_NUMBER: _ClassVar[int]
    SCREEN_ON_FIELD_NUMBER: _ClassVar[int]
    LOCKED_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    device_id: str
    model: str
    manufacturer: str
    android_version: str
    battery_level: int
    charging: bool
    screen_on: bool
    locked: bool
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., device_id: _Optional[str] = ..., model: _Optional[str] = ..., manufacturer: _Optional[str] = ..., android_version: _Optional[str] = ..., battery_level: _Optional[int] = ..., charging: _Optional[bool] = ..., screen_on: _Optional[bool] = ..., locked: _Optional[bool] = ...) -> None: ...

class GetAccessibilityStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAccessibilityStatusResponse(_message.Message):
    __slots__ = ("status", "enabled", "service_name", "detail")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    enabled: bool
    service_name: str
    detail: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., enabled: _Optional[bool] = ..., service_name: _Optional[str] = ..., detail: _Optional[str] = ...) -> None: ...

class GetLocationRequest(_message.Message):
    __slots__ = ("accuracy",)
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    accuracy: str
    def __init__(self, accuracy: _Optional[str] = ...) -> None: ...

class GetLocationResponse(_message.Message):
    __slots__ = ("status", "latitude", "longitude", "accuracy_meters", "captured_ms")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    ACCURACY_METERS_FIELD_NUMBER: _ClassVar[int]
    CAPTURED_MS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    latitude: float
    longitude: float
    accuracy_meters: float
    captured_ms: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., accuracy_meters: _Optional[float] = ..., captured_ms: _Optional[int] = ...) -> None: ...

class TapRequest(_message.Message):
    __slots__ = ("x", "y", "duration_ms")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    duration_ms: int
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ..., duration_ms: _Optional[int] = ...) -> None: ...

class TapResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class SwipeRequest(_message.Message):
    __slots__ = ("start_x", "start_y", "end_x", "end_y", "duration_ms")
    START_X_FIELD_NUMBER: _ClassVar[int]
    START_Y_FIELD_NUMBER: _ClassVar[int]
    END_X_FIELD_NUMBER: _ClassVar[int]
    END_Y_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    duration_ms: int
    def __init__(self, start_x: _Optional[int] = ..., start_y: _Optional[int] = ..., end_x: _Optional[int] = ..., end_y: _Optional[int] = ..., duration_ms: _Optional[int] = ...) -> None: ...

class SwipeResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class AndroidTypeTextRequest(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class AndroidTypeTextResponse(_message.Message):
    __slots__ = ("status", "characters_typed")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CHARACTERS_TYPED_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    characters_typed: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., characters_typed: _Optional[int] = ...) -> None: ...

class PressBackRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PressBackResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class PressHomeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PressHomeResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class OpenAppRequest(_message.Message):
    __slots__ = ("package_name", "activity_name")
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_NAME_FIELD_NUMBER: _ClassVar[int]
    package_name: str
    activity_name: str
    def __init__(self, package_name: _Optional[str] = ..., activity_name: _Optional[str] = ...) -> None: ...

class OpenAppResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class AndroidShowOverlayRequest(_message.Message):
    __slots__ = ("text", "x", "y", "duration_ms", "color")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    text: str
    x: int
    y: int
    duration_ms: int
    color: str
    def __init__(self, text: _Optional[str] = ..., x: _Optional[int] = ..., y: _Optional[int] = ..., duration_ms: _Optional[int] = ..., color: _Optional[str] = ...) -> None: ...

class AndroidShowOverlayResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class AndroidApprovalRequest(_message.Message):
    __slots__ = ("approval_id", "title", "body", "summary_json", "expires_at_ms")
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_JSON_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_MS_FIELD_NUMBER: _ClassVar[int]
    approval_id: str
    title: str
    body: str
    summary_json: str
    expires_at_ms: int
    def __init__(self, approval_id: _Optional[str] = ..., title: _Optional[str] = ..., body: _Optional[str] = ..., summary_json: _Optional[str] = ..., expires_at_ms: _Optional[int] = ...) -> None: ...

class AndroidApprovalResponse(_message.Message):
    __slots__ = ("status", "surface_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SURFACE_ID_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    surface_id: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., surface_id: _Optional[str] = ...) -> None: ...

class AndroidEmergencyStopRequest(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class AndroidEmergencyStopResponse(_message.Message):
    __slots__ = ("status", "stopped")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STOPPED_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    stopped: bool
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., stopped: _Optional[bool] = ...) -> None: ...
