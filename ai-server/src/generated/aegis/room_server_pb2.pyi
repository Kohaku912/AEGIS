from aegis import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetEnvironmentRequest(_message.Message):
    __slots__ = ("sensors",)
    SENSORS_FIELD_NUMBER: _ClassVar[int]
    sensors: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, sensors: _Optional[_Iterable[str]] = ...) -> None: ...

class GetEnvironmentResponse(_message.Message):
    __slots__ = ("status", "temperature_c", "humidity_pct", "brightness_lux", "motion_detected", "motion_zone", "timestamp_ms")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_C_FIELD_NUMBER: _ClassVar[int]
    HUMIDITY_PCT_FIELD_NUMBER: _ClassVar[int]
    BRIGHTNESS_LUX_FIELD_NUMBER: _ClassVar[int]
    MOTION_DETECTED_FIELD_NUMBER: _ClassVar[int]
    MOTION_ZONE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    temperature_c: float
    humidity_pct: float
    brightness_lux: float
    motion_detected: bool
    motion_zone: str
    timestamp_ms: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., temperature_c: _Optional[float] = ..., humidity_pct: _Optional[float] = ..., brightness_lux: _Optional[float] = ..., motion_detected: _Optional[bool] = ..., motion_zone: _Optional[str] = ..., timestamp_ms: _Optional[int] = ...) -> None: ...

class GetDeviceStatusRequest(_message.Message):
    __slots__ = ("device_ids",)
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    device_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, device_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeviceStatus(_message.Message):
    __slots__ = ("device_id", "device_type", "state_json", "online", "last_seen_ms")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATE_JSON_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_MS_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    device_type: str
    state_json: str
    online: bool
    last_seen_ms: int
    def __init__(self, device_id: _Optional[str] = ..., device_type: _Optional[str] = ..., state_json: _Optional[str] = ..., online: _Optional[bool] = ..., last_seen_ms: _Optional[int] = ...) -> None: ...

class GetDeviceStatusResponse(_message.Message):
    __slots__ = ("status", "devices")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    devices: _containers.RepeatedCompositeFieldContainer[DeviceStatus]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., devices: _Optional[_Iterable[_Union[DeviceStatus, _Mapping]]] = ...) -> None: ...

class GetCameraSnapshotRequest(_message.Message):
    __slots__ = ("camera_id", "format", "quality", "max_width", "max_height")
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    MAX_WIDTH_FIELD_NUMBER: _ClassVar[int]
    MAX_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    camera_id: str
    format: str
    quality: int
    max_width: int
    max_height: int
    def __init__(self, camera_id: _Optional[str] = ..., format: _Optional[str] = ..., quality: _Optional[int] = ..., max_width: _Optional[int] = ..., max_height: _Optional[int] = ...) -> None: ...

class GetCameraSnapshotResponse(_message.Message):
    __slots__ = ("status", "image_data", "width", "height", "format", "captured_ms")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    CAPTURED_MS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    image_data: bytes
    width: int
    height: int
    format: str
    captured_ms: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., image_data: _Optional[bytes] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., format: _Optional[str] = ..., captured_ms: _Optional[int] = ...) -> None: ...

class SendIrCommandRequest(_message.Message):
    __slots__ = ("device_type", "ir_code", "repeat")
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IR_CODE_FIELD_NUMBER: _ClassVar[int]
    REPEAT_FIELD_NUMBER: _ClassVar[int]
    device_type: str
    ir_code: str
    repeat: int
    def __init__(self, device_type: _Optional[str] = ..., ir_code: _Optional[str] = ..., repeat: _Optional[int] = ...) -> None: ...

class SendIrCommandResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class SetLightRequest(_message.Message):
    __slots__ = ("device_id", "power_on", "brightness", "color_temp_k", "color_rgb")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    POWER_ON_FIELD_NUMBER: _ClassVar[int]
    BRIGHTNESS_FIELD_NUMBER: _ClassVar[int]
    COLOR_TEMP_K_FIELD_NUMBER: _ClassVar[int]
    COLOR_RGB_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    power_on: bool
    brightness: int
    color_temp_k: int
    color_rgb: str
    def __init__(self, device_id: _Optional[str] = ..., power_on: _Optional[bool] = ..., brightness: _Optional[int] = ..., color_temp_k: _Optional[int] = ..., color_rgb: _Optional[str] = ...) -> None: ...

class SetLightResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class SetAirConditionerRequest(_message.Message):
    __slots__ = ("device_id", "power_on", "target_temperature_c", "mode", "fan_speed")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    POWER_ON_FIELD_NUMBER: _ClassVar[int]
    TARGET_TEMPERATURE_C_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    FAN_SPEED_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    power_on: bool
    target_temperature_c: float
    mode: str
    fan_speed: int
    def __init__(self, device_id: _Optional[str] = ..., power_on: _Optional[bool] = ..., target_temperature_c: _Optional[float] = ..., mode: _Optional[str] = ..., fan_speed: _Optional[int] = ...) -> None: ...

class SetAirConditionerResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class MoveRobotArmRequest(_message.Message):
    __slots__ = ("arm_id", "target_position_json", "speed_pct")
    ARM_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_POSITION_JSON_FIELD_NUMBER: _ClassVar[int]
    SPEED_PCT_FIELD_NUMBER: _ClassVar[int]
    arm_id: str
    target_position_json: str
    speed_pct: int
    def __init__(self, arm_id: _Optional[str] = ..., target_position_json: _Optional[str] = ..., speed_pct: _Optional[int] = ...) -> None: ...

class MoveRobotArmResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class EmergencyStopRequest(_message.Message):
    __slots__ = ("arm_id",)
    ARM_ID_FIELD_NUMBER: _ClassVar[int]
    arm_id: str
    def __init__(self, arm_id: _Optional[str] = ...) -> None: ...

class EmergencyStopResponse(_message.Message):
    __slots__ = ("status", "stopped_arms")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STOPPED_ARMS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    stopped_arms: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., stopped_arms: _Optional[_Iterable[str]] = ...) -> None: ...
