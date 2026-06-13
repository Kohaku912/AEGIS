"""Observation types — data structures for multimodal observation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_SENSITIVE_PATTERNS = [
    re.compile(r"(api[_-]?key|token|password|secret|cookie|auth)[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"Bearer\s+\S+", re.IGNORECASE),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
]


def _mask_text(text: str) -> str:
    for pat in _SENSITIVE_PATTERNS:
        text = pat.sub("***MASKED***", text)
    return text


class ObservationTarget(Enum):
    PC = "pc"
    BROWSER = "browser"
    ANDROID = "android"
    DEV_SERVER = "dev_server"


class ObservationPurpose(Enum):
    PRE_ACTION = "pre_action"
    POST_ACTION = "post_action"
    VERIFICATION = "verification"
    RECOVERY = "recovery"
    PERIODIC_STATE = "periodic_state"


class ObservationStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    REDACTED = "redacted"


class ElementKind(Enum):
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    TEXT = "text"
    IMAGE = "image"
    ICON = "icon"
    CHECKBOX = "checkbox"
    MENU = "menu"
    DIALOG = "dialog"
    ERROR_MESSAGE = "error_message"
    SUCCESS_MESSAGE = "success_message"
    UNKNOWN = "unknown"


class ElementSource(Enum):
    DOM = "dom"
    ACCESSIBILITY = "accessibility"
    VISION = "vision"
    OCR = "ocr"
    API = "api"


@dataclass
class DetectedElement:
    element_id: str = ""
    kind: ElementKind = ElementKind.UNKNOWN
    label: str = ""
    text: str = ""
    bbox: list[float] = field(default_factory=list)
    confidence: float = 0.0
    source: ElementSource = ElementSource.DOM
    clickable: bool = False
    editable: bool = False
    sensitive: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "element_id": self.element_id,
            "kind": self.kind.value,
            "label": self.label,
            "text": self.text[:200],
            "confidence": self.confidence,
            "source": self.source.value,
            "clickable": self.clickable,
            "editable": self.editable,
            "sensitive": self.sensitive,
        }


@dataclass
class ObservationRequest:
    observation_id: str = ""
    task_id: str = ""
    request_id: str = ""
    source: str = ""
    target: ObservationTarget = ObservationTarget.PC
    purpose: ObservationPurpose = ObservationPurpose.POST_ACTION
    expected_state: str = ""
    previous_observation_id: str = ""
    sensitivity_level: str = "normal"
    created_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "task_id": self.task_id,
            "request_id": self.request_id,
            "source": self.source,
            "target": self.target.value,
            "purpose": self.purpose.value,
            "expected_state": self.expected_state,
            "sensitivity_level": self.sensitivity_level,
            "created_at": self.created_at,
        }


@dataclass
class ObservationResult:
    observation_id: str = ""
    target: ObservationTarget = ObservationTarget.PC
    status: ObservationStatus = ObservationStatus.UNAVAILABLE
    screenshot_ref: str = ""
    screenshot_summary: str = ""
    ui_tree: str = ""
    dom_summary: str = ""
    active_app: str = ""
    active_window: str = ""
    current_url: str = ""
    page_title: str = ""
    visible_text_summary: str = ""
    detected_elements: list[DetectedElement] = field(default_factory=list)
    state_fingerprint: str = ""
    sensitivity_flags: list[str] = field(default_factory=list)
    redactions: list[str] = field(default_factory=list)
    created_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "target": self.target.value,
            "status": self.status.value,
            "screenshot_ref": self.screenshot_ref,
            "screenshot_summary": self.screenshot_summary[:500],
            "dom_summary": _mask_text(self.dom_summary[:500]),
            "active_app": self.active_app,
            "active_window": self.active_window,
            "current_url": self.current_url,
            "page_title": self.page_title,
            "visible_text_summary": _mask_text(self.visible_text_summary[:500]),
            "detected_elements": [e.to_dict() for e in self.detected_elements[:20]],
            "state_fingerprint": self.state_fingerprint,
            "sensitivity_flags": self.sensitivity_flags,
            "redactions": self.redactions,
            "created_at": self.created_at,
        }

    def to_context_string(self, max_len: int = 500) -> str:
        parts = [f"[{self.target.value}] {self.status.value}"]
        if self.active_window:
            parts.append(f"window={self.active_window}")
        if self.current_url:
            parts.append(f"url={self.current_url[:100]}")
        if self.page_title:
            parts.append(f"title={self.page_title[:100]}")
        if self.visible_text_summary:
            parts.append(f"text={self.visible_text_summary[:200]}")
        if self.detected_elements:
            buttons = [e for e in self.detected_elements if e.kind == ElementKind.BUTTON]
            if buttons:
                parts.append(f"buttons={[e.label for e in buttons[:5]]}")
            errors = [e for e in self.detected_elements if e.kind == ElementKind.ERROR_MESSAGE]
            if errors:
                parts.append(f"errors={[e.text[:50] for e in errors[:3]]}")
        return " | ".join(parts)[:max_len]


@dataclass
class ObservationDiff:
    before_observation_id: str = ""
    after_observation_id: str = ""
    changed: bool = False
    url_changed: bool = False
    active_window_changed: bool = False
    visible_text_changed: bool = False
    dom_changed: bool = False
    ui_tree_changed: bool = False
    screenshot_changed: bool = False
    new_elements: list[DetectedElement] = field(default_factory=list)
    removed_elements: list[DetectedElement] = field(default_factory=list)
    new_error_messages: list[str] = field(default_factory=list)
    new_success_messages: list[str] = field(default_factory=list)
    state_change_summary: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "before_observation_id": self.before_observation_id,
            "after_observation_id": self.after_observation_id,
            "changed": self.changed,
            "url_changed": self.url_changed,
            "active_window_changed": self.active_window_changed,
            "visible_text_changed": self.visible_text_changed,
            "dom_changed": self.dom_changed,
            "new_element_count": len(self.new_elements),
            "removed_element_count": len(self.removed_elements),
            "new_error_messages": self.new_error_messages[:5],
            "new_success_messages": self.new_success_messages[:5],
            "state_change_summary": self.state_change_summary[:300],
            "confidence": self.confidence,
        }
