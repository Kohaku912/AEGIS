"""Audit → LLMTrace normalisation and deduplication."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.observability.llm_usage.models import LLMTrace

logger = logging.getLogger("aegis_ai.observability.llm_usage.audit_extractor")

_LLM_ACTIONS = {
    "llm_call",
    "llm_request",
    "llm_tool_request",
    "llm_tool_call",
    "llm_vision_call",
    "llm_media_call",
}


def extract_traces(entries: list[dict[str, Any]], limit: int = 5000) -> list[LLMTrace]:
    """Normalise LLM-related audit entries into LLMTrace objects.

    Deduplicates by request_id: when both a router-level and provider-level
    entry exist for the same request_id, keep the provider-level one (richer
    detail).
    """
    llm_entries: list[dict[str, Any]] = []
    for entry in entries[:limit]:
        action = str(entry.get("action") or "")
        if action in _LLM_ACTIONS:
            llm_entries.append(entry)

    # Deduplicate by request_id — prefer provider-level (richer detail / more tokens)
    _PROVIDER_ACTIONS = {"llm_call", "llm_tool_call", "llm_vision_call", "llm_media_call"}
    by_request: dict[str, dict[str, Any]] = {}
    for entry in llm_entries:
        rid = str(entry.get("request_id") or entry.get("entry_id") or "")
        if not rid:
            rid = entry.get("entry_id", "")
        if rid in by_request:
            existing = by_request[rid]
            existing_detail = existing.get("detail") or {}
            new_detail = entry.get("detail") or {}
            existing_is_provider = str(existing.get("action", "")) in _PROVIDER_ACTIONS
            new_is_provider = str(entry.get("action", "")) in _PROVIDER_ACTIONS
            # Prefer provider-level over router-level
            if new_is_provider and not existing_is_provider:
                by_request[rid] = entry
            elif new_is_provider == existing_is_provider:
                # Same level: prefer richer detail or higher tokens
                existing_tokens = int(existing.get("tokens_used") or existing_detail.get("tokens") or 0)
                new_tokens = int(entry.get("tokens_used") or new_detail.get("tokens") or 0)
                if new_tokens > existing_tokens or len(new_detail) > len(existing_detail):
                    by_request[rid] = entry
        else:
            by_request[rid] = entry

    traces: list[LLMTrace] = []
    for entry in by_request.values():
        try:
            traces.append(_entry_to_trace(entry))
        except Exception:
            logger.debug("Failed to normalise audit entry", exc_info=True)

    traces.sort(key=lambda t: t.timestamp_ms, reverse=True)
    return traces


def _entry_to_trace(entry: dict[str, Any]) -> LLMTrace:
    detail = entry.get("detail") or {}

    tokens_raw = entry.get("tokens_used") or 0
    if tokens_raw == 0:
        tokens_raw = detail.get("tokens") or 0

    success = detail.get("success")
    if success is None:
        success = not bool(detail.get("error"))

    tool_calls = detail.get("tool_calls") or []
    tool_names: list[str] = []
    tool_count = 0
    if isinstance(tool_calls, list):
        tool_count = len(tool_calls)
        for tc in tool_calls:
            if isinstance(tc, dict):
                tool_names.append(str(tc.get("name") or tc.get("function", {}).get("name") or ""))

    caller = str(detail.get("caller") or entry.get("actor") or "")
    route_type = str(detail.get("route_type") or "")

    return LLMTrace(
        trace_id=str(entry.get("entry_id") or ""),
        timestamp_ms=int(entry.get("timestamp_ms") or 0),
        action=str(entry.get("action") or ""),
        caller=caller,
        profile_id=str(entry.get("profile_id") or ""),
        prompt_id=str(entry.get("prompt_id") or ""),
        prompt_version=int(entry.get("prompt_version") or 0),
        prompt_hash=str(entry.get("prompt_hash") or ""),
        model=str(entry.get("model") or detail.get("model") or ""),
        provider=str(entry.get("provider") or detail.get("provider") or ""),
        tokens_used=int(tokens_raw),
        input_tokens=int(detail.get("input_tokens") or 0),
        output_tokens=int(detail.get("output_tokens") or 0),
        duration_ms=int(entry.get("duration_ms") or detail.get("duration_ms") or 0),
        success=bool(success),
        error=str(detail.get("error") or ""),
        route_type=route_type,
        tool_call_count=tool_count,
        tool_names=tool_names,
        media_kind=str(detail.get("media_kind") or ""),
        media_count=int(detail.get("media_count") or 0),
        request_id=str(entry.get("request_id") or ""),
        task_id=str(entry.get("task_id") or ""),
        detail_preview=str(detail.get("prompt_preview") or "")[:500],
        response_preview=str(detail.get("response_preview") or "")[:500],
    )
