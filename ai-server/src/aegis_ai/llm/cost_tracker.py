"""Cost Tracker — tracks LLM usage and enforces budget limits.

Tracks:
- Per-request token usage and cost
- Daily and monthly budgets
- Budget exceeded → deny/defer
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CostEntry:
    """A single LLM usage record."""
    timestamp_ms: int = 0
    provider: str = ""
    model: str = ""
    tokens_used: int = 0
    cost: float = 0.0
    task_type: str = ""


class CostTracker:
    """Tracks LLM usage and enforces budget limits.

    Usage:
        tracker = CostTracker(daily_budget=10.0, monthly_budget=100.0)
        if tracker.can_afford(estimated_tokens):
            tracker.record_usage(provider, model, tokens, cost)
    """

    def __init__(
        self,
        daily_budget: float = 10.0,
        monthly_budget: float = 100.0,
        path: str = "data/cost_tracker.jsonl",
    ) -> None:
        self._daily_budget = daily_budget
        self._monthly_budget = monthly_budget
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[CostEntry] = []
        self._lock = threading.Lock()
        self._load()

    def can_afford(self, estimated_tokens: int) -> bool:
        """Check if a request is within budget.

        Estimates cost at $0.01 per 1000 tokens (conservative).
        """
        estimated_cost = estimated_tokens * 0.01 / 1000
        daily_cost = self._get_daily_cost()
        monthly_cost = self._get_monthly_cost()

        return (daily_cost + estimated_cost <= self._daily_budget and
                monthly_cost + estimated_cost <= self._monthly_budget)

    def record_usage(
        self,
        provider: str,
        model: str,
        tokens: int,
        cost: float,
        task_type: str = "",
    ) -> None:
        """Record LLM usage."""
        entry = CostEntry(
            timestamp_ms=int(time.time() * 1000),
            provider=provider,
            model=model,
            tokens_used=tokens,
            cost=cost,
            task_type=task_type,
        )
        with self._lock:
            self._entries.append(entry)
            self._persist(entry)

    def get_daily_cost(self) -> float:
        """Get total cost for today."""
        return self._get_daily_cost()

    def get_monthly_cost(self) -> float:
        """Get total cost for this month."""
        return self._get_monthly_cost()

    def get_usage_summary(self) -> dict[str, Any]:
        """Get usage summary for dashboard."""
        daily = self._get_daily_cost()
        monthly = self._get_monthly_cost()
        return {
            "daily_cost": round(daily, 4),
            "monthly_cost": round(monthly, 4),
            "daily_budget": self._daily_budget,
            "monthly_budget": self._monthly_budget,
            "daily_remaining": round(self._daily_budget - daily, 4),
            "monthly_remaining": round(self._monthly_budget - monthly, 4),
            "total_requests": len(self._entries),
        }

    def _get_daily_cost(self) -> float:
        """Calculate cost for today."""
        now = time.time()
        day_start = now - (now % 86400)
        day_start_ms = int(day_start * 1000)
        return sum(e.cost for e in self._entries if e.timestamp_ms >= day_start_ms)

    def _get_monthly_cost(self) -> float:
        """Calculate cost for this month (last 30 days)."""
        now_ms = int(time.time() * 1000)
        month_start_ms = now_ms - (30 * 86400 * 1000)
        return sum(e.cost for e in self._entries if e.timestamp_ms >= month_start_ms)

    def _persist(self, entry: CostEntry) -> None:
        """Append entry to JSONL file."""
        record = {
            "timestamp_ms": entry.timestamp_ms,
            "provider": entry.provider,
            "model": entry.model,
            "tokens_used": entry.tokens_used,
            "cost": entry.cost,
            "task_type": entry.task_type,
        }
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _load(self) -> None:
        """Load entries from JSONL file."""
        if not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        self._entries.append(CostEntry(**data))
        except (json.JSONDecodeError, Exception):
            pass
