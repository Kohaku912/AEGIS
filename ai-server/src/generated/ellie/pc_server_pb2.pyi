from ellie import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetScreenshotRequest(_message.Message):
    __slots__ = ("display_id", "format", "quality")
    DISPLAY_ID_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    display_id: int
    format: str
    quality: int
    def __init__(self, display_id: _Optional[int] = ..., format: _Optional[str] = ..., quality: _Optional[int] = ...) -> None: ...

class GetScreenshotResponse(_message.Message):
    __slots__ = ("status", "image_data", "width", "height", "format")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    image_data: bytes
    width: int
    height: int
    format: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., image_data: _Optional[bytes] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., format: _Optional[str] = ...) -> None: ...

class GetActiveWindowRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetActiveWindowResponse(_message.Message):
    __slots__ = ("status", "title", "process_name", "pid", "x", "y", "width", "height")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PROCESS_NAME_FIELD_NUMBER: _ClassVar[int]
    PID_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    title: str
    process_name: str
    pid: int
    x: int
    y: int
    width: int
    height: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., title: _Optional[str] = ..., process_name: _Optional[str] = ..., pid: _Optional[int] = ..., x: _Optional[int] = ..., y: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class ListWindowsRequest(_message.Message):
    __slots__ = ("visible_only",)
    VISIBLE_ONLY_FIELD_NUMBER: _ClassVar[int]
    visible_only: bool
    def __init__(self, visible_only: _Optional[bool] = ...) -> None: ...

class WindowInfo(_message.Message):
    __slots__ = ("title", "process_name", "pid", "x", "y", "width", "height", "is_minimized")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PROCESS_NAME_FIELD_NUMBER: _ClassVar[int]
    PID_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    IS_MINIMIZED_FIELD_NUMBER: _ClassVar[int]
    title: str
    process_name: str
    pid: int
    x: int
    y: int
    width: int
    height: int
    is_minimized: bool
    def __init__(self, title: _Optional[str] = ..., process_name: _Optional[str] = ..., pid: _Optional[int] = ..., x: _Optional[int] = ..., y: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., is_minimized: _Optional[bool] = ...) -> None: ...

class ListWindowsResponse(_message.Message):
    __slots__ = ("status", "windows")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    WINDOWS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    windows: _containers.RepeatedCompositeFieldContainer[WindowInfo]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., windows: _Optional[_Iterable[_Union[WindowInfo, _Mapping]]] = ...) -> None: ...

class GetClipboardRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetClipboardResponse(_message.Message):
    __slots__ = ("status", "text", "has_image")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    HAS_IMAGE_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    text: str
    has_image: bool
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., text: _Optional[str] = ..., has_image: _Optional[bool] = ...) -> None: ...

class MoveMouseRequest(_message.Message):
    __slots__ = ("x", "y", "absolute")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    absolute: bool
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ..., absolute: _Optional[bool] = ...) -> None: ...

class MoveMouseResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class ClickMouseRequest(_message.Message):
    __slots__ = ("x", "y", "button", "double_click")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    BUTTON_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_CLICK_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    button: str
    double_click: bool
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ..., button: _Optional[str] = ..., double_click: _Optional[bool] = ...) -> None: ...

class ClickMouseResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class TypeTextRequest(_message.Message):
    __slots__ = ("text", "delay_ms")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    DELAY_MS_FIELD_NUMBER: _ClassVar[int]
    text: str
    delay_ms: int
    def __init__(self, text: _Optional[str] = ..., delay_ms: _Optional[int] = ...) -> None: ...

class TypeTextResponse(_message.Message):
    __slots__ = ("status", "characters_typed")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CHARACTERS_TYPED_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    characters_typed: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., characters_typed: _Optional[int] = ...) -> None: ...

class PressHotkeyRequest(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, keys: _Optional[_Iterable[str]] = ...) -> None: ...

class PressHotkeyResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class LaunchAppRequest(_message.Message):
    __slots__ = ("path", "args")
    PATH_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    path: str
    args: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, path: _Optional[str] = ..., args: _Optional[_Iterable[str]] = ...) -> None: ...

class LaunchAppResponse(_message.Message):
    __slots__ = ("status", "pid")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PID_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    pid: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., pid: _Optional[int] = ...) -> None: ...

class ShowOverlayRequest(_message.Message):
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

class ShowOverlayResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class ReadFileRequest(_message.Message):
    __slots__ = ("path", "max_bytes", "offset")
    PATH_FIELD_NUMBER: _ClassVar[int]
    MAX_BYTES_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    path: str
    max_bytes: int
    offset: int
    def __init__(self, path: _Optional[str] = ..., max_bytes: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class ReadFileResponse(_message.Message):
    __slots__ = ("status", "content", "total_size", "truncated")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    content: bytes
    total_size: int
    truncated: bool
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., content: _Optional[bytes] = ..., total_size: _Optional[int] = ..., truncated: _Optional[bool] = ...) -> None: ...

class WriteFileRequest(_message.Message):
    __slots__ = ("path", "content", "append")
    PATH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    APPEND_FIELD_NUMBER: _ClassVar[int]
    path: str
    content: bytes
    append: bool
    def __init__(self, path: _Optional[str] = ..., content: _Optional[bytes] = ..., append: _Optional[bool] = ...) -> None: ...

class WriteFileResponse(_message.Message):
    __slots__ = ("status", "bytes_written")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BYTES_WRITTEN_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    bytes_written: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., bytes_written: _Optional[int] = ...) -> None: ...

class DeleteFileRequest(_message.Message):
    __slots__ = ("path", "permanent")
    PATH_FIELD_NUMBER: _ClassVar[int]
    PERMANENT_FIELD_NUMBER: _ClassVar[int]
    path: str
    permanent: bool
    def __init__(self, path: _Optional[str] = ..., permanent: _Optional[bool] = ...) -> None: ...

class DeleteFileResponse(_message.Message):
    __slots__ = ("status", "moved_to_trash")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MOVED_TO_TRASH_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    moved_to_trash: bool
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., moved_to_trash: _Optional[bool] = ...) -> None: ...

class ListDirectoryRequest(_message.Message):
    __slots__ = ("path", "recursive", "max_entries")
    PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    MAX_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    path: str
    recursive: bool
    max_entries: int
    def __init__(self, path: _Optional[str] = ..., recursive: _Optional[bool] = ..., max_entries: _Optional[int] = ...) -> None: ...

class FileEntry(_message.Message):
    __slots__ = ("name", "path", "is_directory", "size_bytes", "modified_ms")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    IS_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_MS_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    is_directory: bool
    size_bytes: int
    modified_ms: int
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ..., is_directory: _Optional[bool] = ..., size_bytes: _Optional[int] = ..., modified_ms: _Optional[int] = ...) -> None: ...

class ListDirectoryResponse(_message.Message):
    __slots__ = ("status", "entries", "truncated")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    entries: _containers.RepeatedCompositeFieldContainer[FileEntry]
    truncated: bool
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., entries: _Optional[_Iterable[_Union[FileEntry, _Mapping]]] = ..., truncated: _Optional[bool] = ...) -> None: ...
