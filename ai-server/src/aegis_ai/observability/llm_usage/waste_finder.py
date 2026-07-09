"""Waste / review candidate detection.

Every finding is presented as a *candidate for review* — never an automatic
conclusion that something is wasteful.
"""

from __future__ import annotations

import math
from collections import Counter

from aegis_ai.observability.llm_usage.models import LLMTrace, WasteCandidate


def find_waste_candidates(traces: list[LLMTrace]) -> list[WasteCandidate]:
    """Detect potential waste / review candidates."""
    candidates: list[WasteCandidate] = []
    candidates.extend(_high_token_traces(traces))
    candidates.extend(_failed_high_cost(traces))
    candidates.extend(_high_token_no_tool(traces))
    candidates.extend(_retry_loop_suspects(traces))
    candidates.extend(_prompt_unused(traces))
    candidates.sort(key=lambda c: c.confidence, reverse=True)
    return candidates


def _p95(values: list[int]) -> int:
    if not values:
        return 0
    s = sorted(values)
    return s[int(math.ceil(0.95 * len(s))) - 1]


def _avg(values: list[int]) -> float:
    return sum(values) / len(values) if values else 0


def _high_token_traces(traces: list[LLMTrace]) -> list[WasteCandidate]:
    """Traces with tokens > 2x the p95 — potential for review."""
    if len(traces) < 5:
        return []
    tokens = [t.tokens_used for t in traces if t.tokens_used > 0]
    p95 = _p95(tokens)
    threshold = p95 * 2
    if threshold == 0:
        return []

    hits = [t for t in traces if t.tokens_used > threshold]
    if not hits:
        return []

    return [
        WasteCandidate(
            candidate_type="high_token_trace",
            description=f"トークン使用量がp95({p95})の2倍以上 ({t.tokens_used} tokens)",
            confidence=min(0.9, t.tokens_used / (threshold * 3)),
            evidence=f"model={t.model}, caller={t.caller}, tokens={t.tokens_used}",
            recommended_experiment="プロンプト短縮テスト: contextを削減して品質を比較",
            affected_traces=[t.trace_id],
        )
        for t in hits[:10]
    ]


def _failed_high_cost(traces: list[LLMTrace]) -> list[WasteCandidate]:
    """Failed calls that consumed significant tokens."""
    avg = _avg([t.tokens_used for t in traces if t.tokens_used > 0])
    if avg == 0:
        return []

    failed = [t for t in traces if not t.success and t.tokens_used > avg]
    if not failed:
        return []

    return [
        WasteCandidate(
            candidate_type="failed_high_cost_call",
            description=f"失敗した呼び出しで平均以上のトークン消費 ({t.tokens_used} tokens)",
            confidence=0.7,
            evidence=f"error={t.error}, model={t.model}, tokens={t.tokens_used}",
            recommended_experiment="エラーハンドリングの改善: リトライ前にcontext削減",
            affected_traces=[t.trace_id],
        )
        for t in failed[:10]
    ]


def _high_token_no_tool(traces: list[LLMTrace]) -> list[WasteCandidate]:
    """High-token calls with no tool use — might be over-contextualised."""
    tokens = [t.tokens_used for t in traces if t.tokens_used > 0]
    if len(tokens) < 5:
        return []
    threshold = _p95(tokens)
    if threshold == 0:
        return []

    hits = [
        t
        for t in traces
        if t.tokens_used > threshold and t.tool_call_count == 0
    ]
    if not hits:
        return []

    return [
        WasteCandidate(
            candidate_type="high_token_no_tool_call",
            description=f"ツール未使用で高トークン ({t.tokens_used} tokens)",
            confidence=0.5,
            evidence=f"model={t.model}, caller={t.caller}, action={t.action}",
            recommended_experiment="不要なcontext候補を除外してトークン削減を測定",
            affected_traces=[t.trace_id],
        )
        for t in hits[:10]
    ]


def _retry_loop_suspects(traces: list[LLMTrace]) -> list[WasteCandidate]:
    """Same request_id appearing 3+ times — possible retry loop."""
    counts: Counter[str] = Counter()
    for t in traces:
        rid = t.request_id or t.trace_id
        if rid:
            counts[rid] += 1

    suspects = {rid for rid, cnt in counts.items() if cnt >= 3}
    if not suspects:
        return []

    result: list[WasteCandidate] = []
    for rid in list(suspects)[:10]:
        group = [t for t in traces if (t.request_id or t.trace_id) == rid]
        total_tokens = sum(t.tokens_used for t in group)
        result.append(
            WasteCandidate(
                candidate_type="retry_loop_suspect",
                description=f"同一リクエストの繰り返し ({len(group)}回, {total_tokens} tokens合計)",
                confidence=min(0.9, len(group) / 5),
                evidence=f"request_id={rid}, count={len(group)}",
                recommended_experiment="リトライ条件の見直し: 最大リトライ回数・バックオフ戦略の確認",
                affected_traces=[t.trace_id for t in group],
            )
        )
    return result


def _prompt_unused(traces: list[LLMTrace]) -> list[WasteCandidate]:
    """Prompt IDs with very few calls and old last-seen — possible dead prompts."""
    now_ms = max((t.timestamp_ms for t in traces), default=0)
    if now_ms == 0:
        return []

    groups: dict[str, list[LLMTrace]] = {}
    for t in traces:
        pid = t.prompt_id
        if pid:
            groups.setdefault(pid, []).append(t)

    seven_days_ms = 7 * 24 * 3600 * 1000
    result: list[WasteCandidate] = []
    for pid, group in groups.items():
        if len(group) >= 3:
            continue
        last_seen = max(t.timestamp_ms for t in group)
        if now_ms - last_seen < seven_days_ms:
            continue
        result.append(
            WasteCandidate(
                candidate_type="prompt_unused_candidate",
                description=f"使用頻度の低いprompt ({pid}): {len(group)}回のみ",
                confidence=0.4,
                evidence=f"calls={len(group)}, last_seen_ms={last_seen}",
                recommended_experiment="このpromptを削除/統合して影響を確認",
                affected_traces=[t.trace_id for t in group],
            )
        )

    return result[:10]
