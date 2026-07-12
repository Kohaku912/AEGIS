from generated.aegis import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OpenPageRequest(_message.Message):
    __slots__ = ("url", "wait_until", "timeout_ms")
    URL_FIELD_NUMBER: _ClassVar[int]
    WAIT_UNTIL_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    url: str
    wait_until: str
    timeout_ms: int
    def __init__(self, url: _Optional[str] = ..., wait_until: _Optional[str] = ..., timeout_ms: _Optional[int] = ...) -> None: ...

class OpenPageResponse(_message.Message):
    __slots__ = ("status", "title", "final_url", "status_code")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    FINAL_URL_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    title: str
    final_url: str
    status_code: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., title: _Optional[str] = ..., final_url: _Optional[str] = ..., status_code: _Optional[int] = ...) -> None: ...

class GetDomSnapshotRequest(_message.Message):
    __slots__ = ("selector", "include_styles")
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_STYLES_FIELD_NUMBER: _ClassVar[int]
    selector: str
    include_styles: bool
    def __init__(self, selector: _Optional[str] = ..., include_styles: _Optional[bool] = ...) -> None: ...

class GetDomSnapshotResponse(_message.Message):
    __slots__ = ("status", "html")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    HTML_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    html: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., html: _Optional[str] = ...) -> None: ...

class GetBrowserScreenshotRequest(_message.Message):
    __slots__ = ("selector", "format", "quality", "full_page")
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    FULL_PAGE_FIELD_NUMBER: _ClassVar[int]
    selector: str
    format: str
    quality: int
    full_page: bool
    def __init__(self, selector: _Optional[str] = ..., format: _Optional[str] = ..., quality: _Optional[int] = ..., full_page: _Optional[bool] = ...) -> None: ...

class GetBrowserScreenshotResponse(_message.Message):
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

class ExtractPageTextRequest(_message.Message):
    __slots__ = ("selector", "max_length", "include_alt_text")
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_ALT_TEXT_FIELD_NUMBER: _ClassVar[int]
    selector: str
    max_length: int
    include_alt_text: bool
    def __init__(self, selector: _Optional[str] = ..., max_length: _Optional[int] = ..., include_alt_text: _Optional[bool] = ...) -> None: ...

class ExtractPageTextResponse(_message.Message):
    __slots__ = ("status", "text", "char_count", "truncated")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CHAR_COUNT_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    text: str
    char_count: int
    truncated: bool
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., text: _Optional[str] = ..., char_count: _Optional[int] = ..., truncated: _Optional[bool] = ...) -> None: ...

class GetNetworkLogRequest(_message.Message):
    __slots__ = ("max_entries", "include_response_body")
    MAX_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_RESPONSE_BODY_FIELD_NUMBER: _ClassVar[int]
    max_entries: int
    include_response_body: bool
    def __init__(self, max_entries: _Optional[int] = ..., include_response_body: _Optional[bool] = ...) -> None: ...

class NetworkEntry(_message.Message):
    __slots__ = ("url", "method", "status_code", "mime_type", "size_bytes", "duration_ms")
    URL_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    url: str
    method: str
    status_code: int
    mime_type: str
    size_bytes: int
    duration_ms: int
    def __init__(self, url: _Optional[str] = ..., method: _Optional[str] = ..., status_code: _Optional[int] = ..., mime_type: _Optional[str] = ..., size_bytes: _Optional[int] = ..., duration_ms: _Optional[int] = ...) -> None: ...

class GetNetworkLogResponse(_message.Message):
    __slots__ = ("status", "entries")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    entries: _containers.RepeatedCompositeFieldContainer[NetworkEntry]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., entries: _Optional[_Iterable[_Union[NetworkEntry, _Mapping]]] = ...) -> None: ...

class BrowserClickRequest(_message.Message):
    __slots__ = ("selector", "x", "y", "button", "double_click")
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    BUTTON_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_CLICK_FIELD_NUMBER: _ClassVar[int]
    selector: str
    x: int
    y: int
    button: str
    double_click: bool
    def __init__(self, selector: _Optional[str] = ..., x: _Optional[int] = ..., y: _Optional[int] = ..., button: _Optional[str] = ..., double_click: _Optional[bool] = ...) -> None: ...

class BrowserClickResponse(_message.Message):
    __slots__ = ("status", "navigated_url")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    NAVIGATED_URL_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    navigated_url: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., navigated_url: _Optional[str] = ...) -> None: ...

class FillFormRequest(_message.Message):
    __slots__ = ("form_selector", "fields", "submit")
    FORM_SELECTOR_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    SUBMIT_FIELD_NUMBER: _ClassVar[int]
    form_selector: str
    fields: _containers.RepeatedCompositeFieldContainer[FormField]
    submit: bool
    def __init__(self, form_selector: _Optional[str] = ..., fields: _Optional[_Iterable[_Union[FormField, _Mapping]]] = ..., submit: _Optional[bool] = ...) -> None: ...

class FormField(_message.Message):
    __slots__ = ("selector", "value", "type")
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    selector: str
    value: str
    type: str
    def __init__(self, selector: _Optional[str] = ..., value: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class FillFormResponse(_message.Message):
    __slots__ = ("status", "fields_filled", "submitted")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FILLED_FIELD_NUMBER: _ClassVar[int]
    SUBMITTED_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    fields_filled: int
    submitted: bool
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., fields_filled: _Optional[int] = ..., submitted: _Optional[bool] = ...) -> None: ...

class DownloadFileRequest(_message.Message):
    __slots__ = ("url", "save_path", "timeout_ms")
    URL_FIELD_NUMBER: _ClassVar[int]
    SAVE_PATH_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    url: str
    save_path: str
    timeout_ms: int
    def __init__(self, url: _Optional[str] = ..., save_path: _Optional[str] = ..., timeout_ms: _Optional[int] = ...) -> None: ...

class DownloadFileResponse(_message.Message):
    __slots__ = ("status", "saved_path", "size_bytes")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SAVED_PATH_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    saved_path: str
    size_bytes: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., saved_path: _Optional[str] = ..., size_bytes: _Optional[int] = ...) -> None: ...
