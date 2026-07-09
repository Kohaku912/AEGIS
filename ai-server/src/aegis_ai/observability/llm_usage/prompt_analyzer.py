"""Per-prompt statistics analysis."""

from __future__ import annotations

import math

from aegis_ai.observability.llm_usage.models import LLMTrace, PromptRow


def analyze_prompts(traces: list[LLMTrace]) -> list[PromptRow]:
    """Aggregate traces by prompt_id."""
    groups: dict[str, list[LLMTrace]] = {}
    for t in traces:
        pid = t.prompt_id or "(no prompt)"
        groups.setdefault(pid, []).append(t)

    rows: list[PromptRow] = []
    for pid, group in groups.items():
        n = len(group)
        token_list = [t.tokens_used for t in group]
        total = sum(token_list)
        s = sorted(token_list)
        p95 = s[int(math.ceil(0.95 * len(s))) - 1] if s else 0
        rows.append(
            PromptRow(
                prompt_id=pid,
                calls=n,
                tokens=total,
                avg_tokens=total / n if n else 0,
                p95_tokens=p95,
                last_seen_ms=max((t.timestamp_ms for t in group), default=0),
            )
        )

    rows.sort(key=lambda r: r.tokens, reverse=True)
    return rows
