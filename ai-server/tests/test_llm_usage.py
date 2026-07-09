"""Tests for LLM Usage observability module."""

from __future__ import annotations

import time
from types import SimpleNamespace

import pytest

from aegis_ai.observability.llm_usage.models import (
    BreakdownRow,
    LLMSummary,
    LLMTrace,
    TimeSeriesBucket,
    WasteCandidate,
)
from aegis_ai.observability.llm_usage.audit_extractor import extract_traces
from aegis_ai.observability.llm_usage.aggregator import (
    breakdown_by_caller,
    breakdown_by_model,
    compute_summary,
    compute_timeseries,
)
from aegis_ai.observability.llm_usage.prompt_analyzer import analyze_prompts
from aegis_ai.observability.llm_usage.waste_finder import find_waste_candidates
from aegis_ai.observability.llm_usage.service import LLMUsageService


# ── Helpers ──────────────────────────────────────────────────────


_entry_counter = 0


def _mk_audit_entry(
    action="llm_call",
    entry_id=None,
    request_id=None,
    timestamp_ms=None,
    tokens_used=100,
    duration_ms=500,
    model="gpt-5.4-mini",
    provider="openai",
    profile_id="chat_balanced",
    prompt_id="p1",
    success=True,
    error="",
    caller="",
    route_type="",
    tool_calls=None,
    media_kind="",
    media_count=0,
    extra_detail=None,
):
    global _entry_counter
    _entry_counter += 1
    if entry_id is None:
        entry_id = f"e{_entry_counter}"
    if request_id is None:
        request_id = f"r{_entry_counter}"
    detail = {
        "success": success,
        "model": model,
        "provider": provider,
        "tokens": tokens_used,
        "duration_ms": duration_ms,
        "prompt_preview": "test prompt",
        "response_preview": "test response",
    }
    if error:
        detail["error"] = error
    if caller:
        detail["caller"] = caller
    if route_type:
        detail["route_type"] = route_type
    if tool_calls is not None:
        detail["tool_calls"] = tool_calls
    if media_kind:
        detail["media_kind"] = media_kind
    if media_count:
        detail["media_count"] = media_count
    if extra_detail:
        detail.update(extra_detail)

    return {
        "action": action,
        "entry_id": entry_id,
        "request_id": request_id,
        "timestamp_ms": timestamp_ms or int(time.time() * 1000),
        "tokens_used": tokens_used,
        "duration_ms": duration_ms,
        "model": model,
        "provider": provider,
        "profile_id": profile_id,
        "prompt_id": prompt_id,
        "prompt_version": 1,
        "prompt_hash": "abc123",
        "actor": "gateway",
        "detail": detail,
    }


def _mk_traces(n=5, **kwargs) -> list[LLMTrace]:
    traces = []
    for i in range(n):
        traces.append(
            LLMTrace(
                trace_id=f"t{i}",
                timestamp_ms=int(time.time() * 1000) - (n - i) * 60000,
                tokens_used=kwargs.get("tokens", 100 + i * 50),
                duration_ms=kwargs.get("duration", 200 + i * 100),
                success=kwargs.get("success", True),
                model=kwargs.get("model", "gpt-5.4-mini"),
                provider=kwargs.get("provider", "openai"),
                caller=kwargs.get("caller", "chat"),
                profile_id=kwargs.get("profile_id", "chat_balanced"),
                prompt_id=kwargs.get("prompt_id", "p1"),
                action=kwargs.get("action", "llm_call"),
                tool_call_count=kwargs.get("tool_call_count", 0),
                request_id=f"r{i}",
            )
        )
    return traces


# ── Model tests ──────────────────────────────────────────────────


class TestModels:
    def test_llm_trace_to_dict(self):
        t = LLMTrace(trace_id="t1", tokens_used=100, model="gpt-5.4-mini")
        d = t.to_dict()
        assert d["trace_id"] == "t1"
        assert d["tokens_used"] == 100
        assert d["model"] == "gpt-5.4-mini"

    def test_llm_summary_to_dict(self):
        s = LLMSummary(total_calls=10, total_tokens=1000)
        d = s.to_dict()
        assert d["total_calls"] == 10
        assert d["total_tokens"] == 1000

    def test_waste_candidate_to_dict(self):
        c = WasteCandidate(candidate_type="high_token_trace", confidence=0.8)
        d = c.to_dict()
        assert d["candidate_type"] == "high_token_trace"
        assert d["confidence"] == 0.8


# ── Audit extractor tests ────────────────────────────────────────


class TestAuditExtractor:
    def test_extract_traces_filters_llm_actions(self):
        entries = [
            _mk_audit_entry(action="llm_call", entry_id="e1"),
            _mk_audit_entry(action="capability_invoked", entry_id="e2"),
            _mk_audit_entry(action="llm_tool_call", entry_id="e3"),
        ]
        traces = extract_traces(entries)
        assert len(traces) == 2
        assert all(t.action.startswith("llm_") for t in traces)

    def test_extract_traces_deduplicates_by_request_id(self):
        entries = [
            _mk_audit_entry(action="llm_request", entry_id="e1", request_id="r1", tokens_used=50),
            _mk_audit_entry(action="llm_call", entry_id="e2", request_id="r1", tokens_used=100),
        ]
        traces = extract_traces(entries)
        assert len(traces) == 1
        assert traces[0].tokens_used == 100

    def test_extract_traces_extracts_detail_fields(self):
        entries = [
            _mk_audit_entry(
                action="llm_call",
                entry_id="e1",
                caller="autonomous_loop",
                route_type="tools",
                tool_calls=[{"name": "search"}],
            )
        ]
        traces = extract_traces(entries)
        assert len(traces) == 1
        assert traces[0].caller == "autonomous_loop"
        assert traces[0].route_type == "tools"
        assert traces[0].tool_call_count == 1
        assert traces[0].tool_names == ["search"]

    def test_extract_traces_empty_input(self):
        assert extract_traces([]) == []


# ── Aggregator tests ─────────────────────────────────────────────


class TestAggregator:
    def test_compute_summary(self):
        traces = _mk_traces(5, tokens=200)
        s = compute_summary(traces)
        assert s.total_calls == 5
        assert s.total_tokens == 1000
        assert s.avg_tokens == 200.0
        assert s.failed_calls == 0
        assert s.failure_rate == 0.0

    def test_compute_summary_failures(self):
        traces = _mk_traces(10)
        traces[0] = LLMTrace(**{**traces[0].__dict__, "success": False})
        traces[1] = LLMTrace(**{**traces[1].__dict__, "success": False})
        s = compute_summary(traces)
        assert s.failed_calls == 2
        assert abs(s.failure_rate - 0.2) < 0.01

    def test_compute_timeseries(self):
        now = int(time.time() * 1000)
        traces = [
            LLMTrace(timestamp_ms=now - 7200000, tokens_used=100, model="m"),
            LLMTrace(timestamp_ms=now - 3600000, tokens_used=200, model="m"),
            LLMTrace(timestamp_ms=now, tokens_used=300, model="m"),
        ]
        buckets = compute_timeseries(traces, bucket_ms=3600000)
        assert len(buckets) == 3
        assert sum(b.calls for b in buckets) == 3

    def test_breakdown_by_caller(self):
        traces = _mk_traces(3, caller="chat") + _mk_traces(2, caller="autonomous")
        rows = breakdown_by_caller(traces)
        assert len(rows) == 2
        assert rows[0].key in ("chat", "autonomous")

    def test_breakdown_by_model(self):
        traces = _mk_traces(3, model="gpt-5.4-mini") + _mk_traces(2, model="deepseek")
        rows = breakdown_by_model(traces)
        assert len(rows) == 2

    def test_compute_summary_empty(self):
        s = compute_summary([])
        assert s.total_calls == 0


# ── Prompt analyzer tests ────────────────────────────────────────


class TestPromptAnalyzer:
    def test_analyze_prompts(self):
        traces = _mk_traces(3, prompt_id="p1") + _mk_traces(2, prompt_id="p2")
        rows = analyze_prompts(traces)
        assert len(rows) == 2
        p1 = next(r for r in rows if r.prompt_id == "p1")
        assert p1.calls == 3

    def test_analyze_prompts_empty(self):
        assert analyze_prompts([]) == []


# ── Waste finder tests ───────────────────────────────────────────


class TestWasteFinder:
    def test_high_token_trace(self):
        traces = _mk_traces(20, tokens=100)
        traces.append(LLMTrace(trace_id="high", tokens_used=5000, model="m", timestamp_ms=int(time.time() * 1000)))
        cands = find_waste_candidates(traces)
        high = [c for c in cands if c.candidate_type == "high_token_trace"]
        assert len(high) >= 1
        assert high[0].confidence > 0

    def test_failed_high_cost(self):
        traces = _mk_traces(5, tokens=100, success=True)
        traces.append(LLMTrace(trace_id="fail", tokens_used=500, success=False, model="m", error="timeout", timestamp_ms=int(time.time() * 1000)))
        cands = find_waste_candidates(traces)
        failed = [c for c in cands if c.candidate_type == "failed_high_cost_call"]
        assert len(failed) >= 1

    def test_retry_loop_suspect(self):
        now = int(time.time() * 1000)
        traces = [
            LLMTrace(trace_id=f"t{i}", request_id="same_req", tokens_used=100, model="m", timestamp_ms=now - i * 1000)
            for i in range(4)
        ]
        cands = find_waste_candidates(traces)
        retry = [c for c in cands if c.candidate_type == "retry_loop_suspect"]
        assert len(retry) >= 1

    def test_empty_traces(self):
        assert find_waste_candidates([]) == []


# ── Service tests ────────────────────────────────────────────────


class TestLLMUsageService:
    def test_get_summary(self):
        entries = [_mk_audit_entry(entry_id=f"e{i}") for i in range(5)]
        audit = SimpleNamespace(read_recent_for_dashboard=lambda limit=5000: entries)
        svc = LLMUsageService(audit_manager=audit)
        s = svc.get_summary(period="1h")
        assert s["total_calls"] == 5
        assert s["total_tokens"] == 500

    def test_get_traces(self):
        entries = [_mk_audit_entry(entry_id=f"e{i}") for i in range(3)]
        audit = SimpleNamespace(read_recent_for_dashboard=lambda limit=5000: entries)
        svc = LLMUsageService(audit_manager=audit)
        traces = svc.get_traces(period="1h", limit=10)
        assert len(traces) == 3

    def test_get_waste_candidates(self):
        entries = [_mk_audit_entry(entry_id=f"e{i}") for i in range(3)]
        audit = SimpleNamespace(read_recent_for_dashboard=lambda limit=5000: entries)
        svc = LLMUsageService(audit_manager=audit)
        cands = svc.get_waste_candidates(period="1h")
        assert isinstance(cands, list)

    def test_get_breakdown(self):
        entries = [_mk_audit_entry(entry_id=f"e{i}", caller="chat" if i < 2 else "auto") for i in range(4)]
        audit = SimpleNamespace(read_recent_for_dashboard=lambda limit=5000: entries)
        svc = LLMUsageService(audit_manager=audit)
        rows = svc.get_breakdown("caller", period="1h")
        assert len(rows) == 2

    def test_filter_by_model(self):
        entries = [_mk_audit_entry(entry_id=f"e{i}", model="m1" if i < 2 else "m2") for i in range(4)]
        audit = SimpleNamespace(read_recent_for_dashboard=lambda limit=5000: entries)
        svc = LLMUsageService(audit_manager=audit)
        traces = svc.get_traces(period="1h", model="m1")
        assert len(traces) == 2

    def test_filter_errors_only(self):
        entries = [_mk_audit_entry(entry_id=f"e{i}", success=(i < 3)) for i in range(5)]
        audit = SimpleNamespace(read_recent_for_dashboard=lambda limit=5000: entries)
        svc = LLMUsageService(audit_manager=audit)
        traces = svc.get_traces(period="1h", errors_only=True)
        assert len(traces) == 2

    def test_no_audit_manager(self):
        svc = LLMUsageService(audit_manager=None)
        s = svc.get_summary()
        assert s["total_calls"] == 0


# ── API route tests ──────────────────────────────────────────────


class TestLLMUsageRoutes:
    def _make_app(self, entries=None):
        from flask import Flask
        from aegis_ai.observability.llm_usage.service import LLMUsageService
        from aegis_ai.observability.llm_usage.routes import init_llm_usage_routes

        app = Flask(__name__)
        entries = entries or [_mk_audit_entry(entry_id=f"e{i}") for i in range(3)]
        audit = SimpleNamespace(read_recent_for_dashboard=lambda limit=5000: entries)
        svc = LLMUsageService(audit_manager=audit)
        init_llm_usage_routes(app, svc)
        return app

    def test_api_summary(self):
        app = self._make_app()
        with app.test_client() as c:
            r = c.get("/api/llm-usage/summary?period=1h")
            assert r.status_code == 200
            data = r.get_json()
            assert "total_calls" in data

    def test_api_timeseries(self):
        app = self._make_app()
        with app.test_client() as c:
            r = c.get("/api/llm-usage/timeseries?period=1h")
            assert r.status_code == 200

    def test_api_breakdown_callers(self):
        app = self._make_app()
        with app.test_client() as c:
            r = c.get("/api/llm-usage/breakdown/callers?period=1h")
            assert r.status_code == 200

    def test_api_breakdown_profiles(self):
        app = self._make_app()
        with app.test_client() as c:
            r = c.get("/api/llm-usage/breakdown/profiles?period=1h")
            assert r.status_code == 200

    def test_api_breakdown_prompts(self):
        app = self._make_app()
        with app.test_client() as c:
            r = c.get("/api/llm-usage/breakdown/prompts?period=1h")
            assert r.status_code == 200

    def test_api_breakdown_models(self):
        app = self._make_app()
        with app.test_client() as c:
            r = c.get("/api/llm-usage/breakdown/models?period=1h")
            assert r.status_code == 200

    def test_api_traces(self):
        app = self._make_app()
        with app.test_client() as c:
            r = c.get("/api/llm-usage/traces?period=1h")
            assert r.status_code == 200
            data = r.get_json()
            assert isinstance(data, list)

    def test_api_waste_candidates(self):
        app = self._make_app()
        with app.test_client() as c:
            r = c.get("/api/llm-usage/waste-candidates?period=1h")
            assert r.status_code == 200
            data = r.get_json()
            assert isinstance(data, list)
