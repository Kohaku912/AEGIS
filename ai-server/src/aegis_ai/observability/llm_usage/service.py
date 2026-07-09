"""LLM Usage service — facade over extractors and aggregators."""

from __future__ import annotations

import logging
import time
import threading
from typing import Any

from aegis_ai.observability.llm_usage.aggregator import (
    breakdown_by_caller,
    breakdown_by_context,
    breakdown_by_model,
    breakdown_by_profile,
    breakdown_by_provider,
    compute_summary,
    compute_timeseries,
)
from aegis_ai.observability.llm_usage.audit_extractor import extract_traces
from aegis_ai.observability.llm_usage.models import LLMTrace
from aegis_ai.observability.llm_usage.prompt_analyzer import analyze_prompts
from aegis_ai.observability.llm_usage.waste_finder import find_waste_candidates, find_waste_candidates_with_prompt_registry

logger = logging.getLogger("aegis_ai.observability.llm_usage.service")

_PERIOD_MS = {
    "1h": 3_600_000,
    "6h": 6 * 3_600_000,
    "24h": 24 * 3_600_000,
    "7d": 7 * 24 * 3_600_000,
    "30d": 30 * 24 * 3_600_000,
}


class LLMUsageService:
    """Reads audit data and produces LLM usage analytics."""

    def __init__(self, audit_manager: Any = None, prompt_registry: Any = None) -> None:
        self._audit = audit_manager
        self._prompt_registry = prompt_registry
        self._cache: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    # ── Public API ───────────────────────────────────────────────

    def get_summary(self, period: str = "24h", **filters: Any) -> dict[str, Any]:
        traces = self._load_traces(period, **filters)
        return compute_summary(traces).to_dict()

    def get_timeseries(
        self, period: str = "24h", bucket: str = "1h", **filters: Any
    ) -> list[dict[str, Any]]:
        traces = self._load_traces(period, **filters)
        bucket_ms = _PERIOD_MS.get(bucket, 3_600_000)
        return [b.to_dict() for b in compute_timeseries(traces, bucket_ms)]

    def get_breakdown(
        self, dimension: str, period: str = "24h", **filters: Any
    ) -> list[dict[str, Any]]:
        traces = self._load_traces(period, **filters)
        fn = {
            "caller": breakdown_by_caller,
            "profile": breakdown_by_profile,
            "model": breakdown_by_model,
            "provider": breakdown_by_provider,
            "context": breakdown_by_context,
        }.get(dimension)
        if fn is None:
            return []
        return [r.to_dict() for r in fn(traces)]

    def get_prompts(self, period: str = "24h", **filters: Any) -> list[dict[str, Any]]:
        traces = self._load_traces(period, **filters)
        return [r.to_dict() for r in analyze_prompts(traces)]

    def get_traces(
        self, period: str = "24h", limit: int = 200, **filters: Any
    ) -> list[dict[str, Any]]:
        traces = self._load_traces(period, **filters)
        return [t.to_dict() for t in traces[:limit]]

    def get_waste_candidates(
        self, period: str = "24h", **filters: Any
    ) -> list[dict[str, Any]]:
        traces = self._load_traces(period, **filters)
        raw = self._load_raw_entries(period, **filters)
        return [c.to_dict() for c in find_waste_candidates_with_prompt_registry(
            traces, self._prompt_registry
        )]

    # ── Internal ─────────────────────────────────────────────────

    def _load_traces(self, period: str, **filters: Any) -> list[LLMTrace]:
        cache_key = f"{period}:{filters}"
        now = time.time()
        with self._lock:
            cached = self._cache.get(cache_key)
            if cached and now - cached[0] < 60:
                return cached[1]

        period_ms = _PERIOD_MS.get(period, 24 * 3_600_000)
        now_ms = int(now * 1000)
        cutoff_ms = now_ms - period_ms

        raw = self._read_audit(limit=5000)
        traces = extract_traces(raw)
        traces = [t for t in traces if t.timestamp_ms >= cutoff_ms]
        traces = self._apply_filters(traces, **filters)

        with self._lock:
            self._cache[cache_key] = (now, traces)
        return traces

    def _load_raw_entries(self, period: str, **filters: Any) -> list[dict[str, Any]]:
        return self._read_audit(limit=5000)

    def _read_audit(self, limit: int = 5000) -> list[dict[str, Any]]:
        if self._audit is None:
            return []
        try:
            if hasattr(self._audit, "read_recent_for_dashboard"):
                return self._audit.read_recent_for_dashboard(limit=limit)
            if hasattr(self._audit, "list_recent"):
                return self._audit.list_recent(limit=limit)
            if hasattr(self._audit, "read_all"):
                return self._audit.read_all()[:limit]
        except Exception:
            logger.debug("Failed to read audit data", exc_info=True)
        return []

    @staticmethod
    def _apply_filters(
        traces: list[LLMTrace],
        caller: str = "",
        profile: str = "",
        prompt_id: str = "",
        model: str = "",
        errors_only: bool = False,
        min_tokens: int = 0,
        **_rest: Any,
    ) -> list[LLMTrace]:
        result = traces
        if caller:
            result = [t for t in result if t.caller == caller]
        if profile:
            result = [t for t in result if t.profile_id == profile]
        if prompt_id:
            result = [t for t in result if t.prompt_id == prompt_id]
        if model:
            result = [t for t in result if t.model == model]
        if errors_only:
            result = [t for t in result if not t.success]
        if min_tokens > 0:
            result = [t for t in result if t.tokens_used >= min_tokens]
        return result
