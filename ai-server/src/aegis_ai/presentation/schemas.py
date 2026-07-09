"""Allowed content schemas for Presentation modalities.

The presentation layer only accepts a small set of renderable payload shapes.
This keeps the renderer safe and prevents arbitrary HTML/JS generation.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".avif"}
_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v", ".avi", ".mkv"}
_HUD_POSITIONS = {"top", "bottom", "left", "right", "center"}


def _extension_from_url(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return ""
    path = urlparse(value).path.lower()
    if "." not in path:
        return ""
    return path[path.rfind(".") :]


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    return bool(value)


def schema_for_modality(modality: str) -> dict[str, Any]:
    """Return the allowed content schema for a modality."""
    if modality == "chart_panel":
        return {
            "type": "object",
            "required": ["chart_type", "data"],
            "properties": {
                "chart_type": {"type": "string", "enum": ["line", "bar", "pie", "scatter", "area"]},
                "data": {"type": "object"},
                "options": {"type": "object"},
            },
        }
    if modality == "diagram_panel":
        return {
            "type": "object",
            "required": ["diagram_type", "nodes", "edges"],
            "properties": {
                "diagram_type": {"type": "string", "enum": ["graph", "flowchart", "mindmap", "sequence"]},
                "nodes": {"type": "array"},
                "edges": {"type": "array"},
            },
        }
    if modality == "gltf_model":
        return {
            "type": "object",
            "required": ["model_url"],
            "properties": {
                "model_url": {"type": "string"},
                "scale": {"type": "number"},
                "position": {"type": "array"},
            },
        }
    if modality == "overlay_short":
        return {
            "type": "object",
            "required": ["message"],
            "properties": {
                "message": {"type": "string"},
                "title": {"type": "string"},
                "duration_ms": {"type": "integer"},
            },
        }
    if modality == "image":
        return {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string"},
                "alt": {"type": "string"},
                "width": {"type": "integer"},
                "height": {"type": "integer"},
            },
        }
    if modality == "video":
        return {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string"},
                "poster": {"type": "string"},
                "autoplay": {"type": "boolean"},
                "loop": {"type": "boolean"},
            },
        }
    if modality == "speech":
        return {
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {"type": "string"},
                "voice": {"type": "string"},
                "language": {"type": "string"},
                "speed": {"type": "number"},
            },
        }
    if modality == "hud":
        return {
            "type": "object",
            "required": ["elements"],
            "properties": {
                "elements": {"type": "array"},
                "position": {"type": "string", "enum": sorted(_HUD_POSITIONS)},
            },
        }
    return {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string"},
            "footer": {"type": "string"},
            "icon": {"type": "string"},
        },
    }


def normalize_content(modality: str, content: dict[str, Any] | None) -> dict[str, Any]:
    """Best-effort content normalizer for the selected modality."""
    payload = dict(content or {})
    if modality == "chart_panel":
        data = payload.get("data") or payload.get("series") or {}
        if not isinstance(data, dict):
            data = {"value": data}
        return {
            "chart_type": payload.get("chart_type", "line"),
            "data": data,
            "options": payload.get("options", {}),
        }
    if modality == "diagram_panel":
        return {
            "diagram_type": payload.get("diagram_type", "graph"),
            "nodes": payload.get("nodes", []),
            "edges": payload.get("edges", []),
        }
    if modality == "gltf_model":
        return {
            "model_url": payload.get("model_url") or payload.get("url", ""),
            "scale": payload.get("scale", 1.0),
            "position": payload.get("position", [0, 0, 0]),
        }
    if modality == "overlay_short":
        message = payload.get("message") or payload.get("text") or payload.get("summary") or ""
        return {
            "message": str(message),
            "title": payload.get("title", "AEGIS"),
            "duration_ms": int(payload.get("duration_ms") or 8000),
        }
    if modality == "image":
        normalized = {"url": str(payload.get("url", ""))}
        if "alt" in payload:
            normalized["alt"] = str(payload.get("alt", ""))
        if payload.get("width") is not None:
            normalized["width"] = int(payload["width"])
        if payload.get("height") is not None:
            normalized["height"] = int(payload["height"])
        return normalized
    if modality == "video":
        normalized = {"url": str(payload.get("url", ""))}
        if "poster" in payload:
            normalized["poster"] = str(payload.get("poster", ""))
        if "autoplay" in payload:
            normalized["autoplay"] = _coerce_bool(payload.get("autoplay"), False)
        if "loop" in payload:
            normalized["loop"] = _coerce_bool(payload.get("loop"), False)
        return normalized
    if modality == "speech":
        normalized = {"text": str(payload.get("text") or payload.get("summary") or payload.get("message") or "")}
        if "voice" in payload:
            normalized["voice"] = str(payload.get("voice", ""))
        if "language" in payload:
            normalized["language"] = str(payload.get("language", ""))
        if payload.get("speed") is not None:
            normalized["speed"] = float(payload["speed"])
        return normalized
    if modality == "hud":
        elements = payload.get("elements")
        if not isinstance(elements, list):
            elements = []
        position = payload.get("position", "center")
        if position not in _HUD_POSITIONS:
            position = "center"
        normalized = {"elements": elements}
        if "position" in payload:
            normalized["position"] = position
        return normalized
    text = payload.get("text") or payload.get("summary") or payload.get("message") or ""
    return {
        "text": str(text),
        "footer": payload.get("footer", ""),
        "icon": payload.get("icon", ""),
    }


def infer_modality(content: dict[str, Any] | None, fallback: str = "text_card") -> str:
    """Infer the best modality from a payload shape."""
    payload = content or {}
    if isinstance(payload, dict):
        url = payload.get("url")
        if isinstance(url, str):
            ext = _extension_from_url(url)
            if ext in _IMAGE_EXTENSIONS:
                return "image"
            if ext in _VIDEO_EXTENSIONS:
                return "video"
        if "text" in payload and "voice" in payload:
            return "speech"
        if "elements" in payload and "position" in payload:
            return "hud"
        if payload.get("model_url") or payload.get("gltf"):
            return "gltf_model"
        if payload.get("diagram_type") or (payload.get("nodes") and payload.get("edges")):
            return "diagram_panel"
        if payload.get("chart_type") or payload.get("series") or payload.get("data_points"):
            return "chart_panel"
        if payload.get("message") or payload.get("overlay"):
            return "overlay_short"
    return fallback
