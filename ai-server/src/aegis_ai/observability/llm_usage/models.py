"""LLM Usage data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMTrace:
    """Normalised representation of a single LLM call from audit logs."""

    trace_id: str = ""
    timestamp_ms: int = 0
    action: str = ""
    caller: str = ""
    profile_id: str = ""
    prompt_id: str = ""
    prompt_version: int = 0
    prompt_hash: str = ""
    model: str = ""
    provider: str = ""
    tokens_used: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0
    success: bool = True
    error: str = ""
    route_type: str = ""
    tool_call_count: int = 0
    tool_names: list[str] = field(default_factory=list)
    media_kind: str = ""
    media_count: int = 0
    request_id: str = ""
    task_id: str = ""
    detail_preview: str = ""
    response_preview: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "timestamp_ms": self.timestamp_ms,
            "action": self.action,
            "caller": self.caller,
            "profile_id": self.profile_id,
            "prompt_id": self.prompt_id,
            "prompt_version": self.prompt_version,
            "prompt_hash": self.prompt_hash,
            "model": self.model,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "route_type": self.route_type,
            "tool_call_count": self.tool_call_count,
            "tool_names": self.tool_names,
            "media_kind": self.media_kind,
            "media_count": self.media_count,
            "request_id": self.request_id,
            "task_id": self.task_id,
            "detail_preview": self.detail_preview,
            "response_preview": self.response_preview,
        }


@dataclass
class LLMSummary:
    """Aggregate summary of LLM usage."""

    total_calls: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    avg_tokens: float = 0.0
    p95_tokens: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: int = 0
    failed_calls: int = 0
    failure_rate: float = 0.0
    tool_call_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "estimated_cost": round(self.estimated_cost, 6),
            "avg_tokens": round(self.avg_tokens, 1),
            "p95_tokens": self.p95_tokens,
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "p95_latency_ms": self.p95_latency_ms,
            "failed_calls": self.failed_calls,
            "failure_rate": round(self.failure_rate, 4),
            "tool_call_rate": round(self.tool_call_rate, 4),
        }


@dataclass
class TimeSeriesBucket:
    """A single time-bucket in a time series."""

    bucket_start_ms: int = 0
    calls: int = 0
    tokens: int = 0
    cost: float = 0.0
    failures: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "bucket_start_ms": self.bucket_start_ms,
            "calls": self.calls,
            "tokens": self.tokens,
            "cost": round(self.cost, 6),
            "failures": self.failures,
        }


@dataclass
class BreakdownRow:
    """A single row in a dimensional breakdown."""

    key: str = ""
    calls: int = 0
    tokens: int = 0
    avg_tokens: float = 0.0
    p95_tokens: int = 0
    failure_rate: float = 0.0
    last_seen_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "calls": self.calls,
            "tokens": self.tokens,
            "avg_tokens": round(self.avg_tokens, 1),
            "p95_tokens": self.p95_tokens,
            "failure_rate": round(self.failure_rate, 4),
            "last_seen_ms": self.last_seen_ms,
        }


@dataclass
class PromptRow:
    """Per-prompt statistics."""

    prompt_id: str = ""
    calls: int = 0
    tokens: int = 0
    avg_tokens: float = 0.0
    p95_tokens: int = 0
    last_seen_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "calls": self.calls,
            "tokens": self.tokens,
            "avg_tokens": round(self.avg_tokens, 1),
            "p95_tokens": self.p95_tokens,
            "last_seen_ms": self.last_seen_ms,
        }


@dataclass
class WasteCandidate:
    """A potential waste / review candidate — never a definitive judgement."""

    candidate_type: str = ""
    description: str = ""
    confidence: float = 0.0
    evidence: str = ""
    recommended_experiment: str = ""
    affected_traces: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_type": self.candidate_type,
            "description": self.description,
            "confidence": round(self.confidence, 2),
            "evidence": self.evidence,
            "recommended_experiment": self.recommended_experiment,
            "affected_traces": self.affected_traces,
        }
