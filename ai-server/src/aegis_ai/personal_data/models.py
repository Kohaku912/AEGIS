"""Personal Data Core schemas. Observed / generated / inferred never mix on one row."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

SCHEMA_VERSION = 1
Epistemics = Literal["observed", "generated", "inferred"]
SourceDevice = Literal["pc", "android", "browser-aegis", "room", "aegis"]
Classification = Literal["public", "personal", "sensitive", "third_party", "secret"]
RetentionClass = Literal["ephemeral_screen", "short_media", "long_event", "forever_metadata"]


class Location(BaseModel):
    country: str = ""
    building: str = ""
    floor: str = ""
    room: str = ""
    zone: str = ""
    position: dict[str, float] = Field(default_factory=dict)
    confidence: float = 0.0


class Provenance(BaseModel):
    collector: str = "personal_data"
    schema_version: int = SCHEMA_VERSION
    code_version: str = ""
    bus_event_id: str = ""
    bus_event_type: str = ""


class RecordBase(BaseModel):
    id: str
    timestamp_ms: int
    duration_ms: int = 0
    source_device: str
    source_sensor: str
    event_type: str = ""
    epistemics: Epistemics
    confidence: float = 1.0
    classification: Classification = "personal"
    location: Location = Field(default_factory=Location)
    entity_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    provenance: Provenance = Field(default_factory=Provenance)
    retention_class: RetentionClass = "long_event"
    payload: dict[str, Any] = Field(default_factory=dict)
    title: str = ""


class Observation(RecordBase):
    epistemics: Epistemics = "observed"


class TimelineEvent(RecordBase):
    observation_ids: list[str] = Field(default_factory=list)


class StateSnapshot(RecordBase):
    epistemics: Epistemics = "generated"
    subject: str = "user"


class EvidenceMeta(BaseModel):
    id: str
    sha256: str
    codec: str
    byte_size: int
    path: str
    retention_class: RetentionClass
    timestamp_ms: int
    duration_ms: int = 0
    source_device: str
    mime: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class Entity(BaseModel):
    id: str
    kind: str
    name: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    first_seen_ms: int = 0
    last_seen_ms: int = 0


class Relationship(BaseModel):
    id: str
    from_id: str
    rel_type: str
    to_id: str
    valid_from_ms: int
    valid_to_ms: int | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    event_ids: list[str] = Field(default_factory=list)


class Fact(BaseModel):
    id: str
    statement: str
    confidence: float
    timestamp_ms: int
    source_event_ids: list[str]
    source_evidence_ids: list[str] = Field(default_factory=list)
    epistemics: Epistemics = "observed"


class Inference(BaseModel):
    id: str
    statement: str
    confidence: float
    timestamp_ms: int
    based_on_fact_ids: list[str] = Field(default_factory=list)
    based_on_event_ids: list[str] = Field(default_factory=list)
    method: str = "rule"


class MemoryDerivation(BaseModel):
    id: str
    memory_id: str
    fact_ids: list[str] = Field(default_factory=list)
    event_ids: list[str] = Field(default_factory=list)
    created_at_ms: int = 0


class CollectionPolicy(BaseModel):
    enabled: bool = True
    pc_uia_enabled: bool = True
    android_a11y_enabled: bool = True
    camera_enabled: bool = False
    mic_enabled: bool = False
    value_capture_enabled: bool = True
    screenshot_on_change: bool = True
    event_retention_days: int = 3650
    screenshot_retention_hours: int = 24
    media_retention_hours: int = 72
    notification_raw_text: bool = True
