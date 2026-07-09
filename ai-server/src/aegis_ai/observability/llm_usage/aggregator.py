"""Aggregation logic for LLM usage data."""

from __future__ import annotations

import math
from typing import Any

from aegis_ai.observability.llm_usage.models import (
    BreakdownRow,
    LLMSummary,
    LLMTrace,
    TimeSeriesBucket,
)

# Approximate per-token cost by model (USD). Extend as needed.
_COST_PER_1K_TOKENS: dict[str, float] = {
    "deepseek-v4-flash": 0.0002,
    "deepseek-chat": 0.0002,
    "deepseek-reasoner": 0.0005,
    "qwen2.5:7b": 0.0,
    "qwen2.5:3b": 0.0,
    "gpt-4o": 0.005,
    "gpt-4o-mini": 0.00015,
    "gpt-5.4-mini": 0.0003,
    "gpt-5.4-nano": 0.0001,
}
_DEFAULT_COST_PER_1K = 0.0003


def _p95(values: list[int]) -> int:
    if not values:
        return 0
    s = sorted(values)
    idx = int(math.ceil(0.95 * len(s))) - 1
    return s[max(0, idx)]


def _cost_for(model: str, tokens: int) -> float:
    rate = _COST_PER_1K_TOKENS.get(model, _DEFAULT_COST_PER_1K)
    return tokens / 1000.0 * rate


def _trace_cost(trace: LLMTrace) -> float:
    if trace.provider_reported_cost > 0:
        return trace.provider_reported_cost
    return _cost_for(trace.model, trace.tokens_used)


def compute_summary(traces: list[LLMTrace]) -> LLMSummary:
    if not traces:
        return LLMSummary()

    total_calls = len(traces)
    total_tokens = sum(t.tokens_used for t in traces)
    token_values = [t.tokens_used for t in traces]
    latency_values = [t.duration_ms for t in traces]
    failed = sum(1 for t in traces if not t.success)
    tool_calls = sum(1 for t in traces if t.tool_call_count > 0)
    cost = sum(_trace_cost(t) for t in traces)

    return LLMSummary(
        total_calls=total_calls,
        total_tokens=total_tokens,
        estimated_cost=cost,
        avg_tokens=total_tokens / total_calls if total_calls else 0,
        p95_tokens=_p95(token_values),
        avg_latency_ms=sum(latency_values) / total_calls if total_calls else 0,
        p95_latency_ms=_p95(latency_values),
        failed_calls=failed,
        failure_rate=failed / total_calls if total_calls else 0,
        tool_call_rate=tool_calls / total_calls if total_calls else 0,
    )


def compute_timeseries(
    traces: list[LLMTrace], bucket_ms: int = 3_600_000
) -> list[TimeSeriesBucket]:
    if not traces:
        return []

    buckets: dict[int, TimeSeriesBucket] = {}
    for t in traces:
        key = (t.timestamp_ms // bucket_ms) * bucket_ms
        if key not in buckets:
            buckets[key] = TimeSeriesBucket(bucket_start_ms=key)
        b = buckets[key]
        b.calls += 1
        b.tokens += t.tokens_used
        b.cost += _trace_cost(t)
        if not t.success:
            b.failures += 1

    return sorted(buckets.values(), key=lambda b: b.bucket_start_ms)


def breakdown_by_caller(traces: list[LLMTrace]) -> list[BreakdownRow]:
    return _breakdown(traces, key_fn=lambda t: t.caller or "(unknown)")


def breakdown_by_profile(traces: list[LLMTrace]) -> list[BreakdownRow]:
    return _breakdown(traces, key_fn=lambda t: t.profile_id or "(none)")


def breakdown_by_model(traces: list[LLMTrace]) -> list[BreakdownRow]:
    return _breakdown(traces, key_fn=lambda t: t.model or "(unknown)")


def breakdown_by_provider(traces: list[LLMTrace]) -> list[BreakdownRow]:
    return _breakdown(traces, key_fn=lambda t: t.provider or "(unknown)")


def breakdown_by_context(traces: list[LLMTrace]) -> list[BreakdownRow]:
    totals: dict[str, list[int]] = {}
    last_seen: dict[str, int] = {}
    failures: dict[str, int] = {}
    for trace in traces:
        for key, tokens in (trace.context_tokens or {}).items():
            normalized = "capability" if key == "capabilities" else str(key)
            value = int(tokens or 0)
            if value <= 0:
                continue
            totals.setdefault(normalized, []).append(value)
            last_seen[normalized] = max(last_seen.get(normalized, 0), trace.timestamp_ms)
            failures[normalized] = failures.get(normalized, 0) + (0 if trace.success else 1)

    rows: list[BreakdownRow] = []
    for key, values in totals.items():
        calls = len(values)
        tokens = sum(values)
        rows.append(
            BreakdownRow(
                key=key,
                calls=calls,
                tokens=tokens,
                avg_tokens=tokens / calls if calls else 0,
                p95_tokens=_p95(values),
                failure_rate=failures.get(key, 0) / calls if calls else 0,
                last_seen_ms=last_seen.get(key, 0),
            )
        )
    rows.sort(key=lambda r: r.tokens, reverse=True)
    return rows


def _breakdown(
    traces: list[LLMTrace], key_fn: Any
) -> list[BreakdownRow]:
    groups: dict[str, list[LLMTrace]] = {}
    for t in traces:
        groups.setdefault(key_fn(t), []).append(t)

    rows: list[BreakdownRow] = []
    for key, group in groups.items():
        n = len(group)
        tokens_list = [t.tokens_used for t in group]
        total = sum(tokens_list)
        failed = sum(1 for t in group if not t.success)
        rows.append(
            BreakdownRow(
                key=key,
                calls=n,
                tokens=total,
                avg_tokens=total / n if n else 0,
                p95_tokens=_p95(tokens_list),
                failure_rate=failed / n if n else 0,
                last_seen_ms=max((t.timestamp_ms for t in group), default=0),
            )
        )

    rows.sort(key=lambda r: r.tokens, reverse=True)
    return rows
