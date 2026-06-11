from aegis import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

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
