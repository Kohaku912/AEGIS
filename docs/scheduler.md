# Scheduler — Design & Usage

> **Status**: Phase 6 — Interval-based implementation
> **Related**: `docs/architecture.md` §5.11

## Overview

The Scheduler manages recurring tasks with interval-based scheduling,
cooldown, and daily budgets. Prevents high-frequency LLM calls.

## Features

- **Interval-based scheduling** — not cron (simpler, more predictable)
- **Cooldown per task** — prevents rapid re-execution
- **Daily budget** — limits total runs per day
- **Task type classification** — for prioritization

## Default Tasks

| Task ID | Type | Interval | Cooldown | Daily Budget |
|---------|------|----------|----------|-------------|
| `daily-briefing` | DAILY_BRIEFING | 24h | 1h | 1 |
| `periodic-research` | PERIODIC_RESEARCH | 1h | 30min | 12 |
| `reflection-interval` | REFLECTION | 30min | 15min | 24 |
| `memory-summarize` | MEMORY_SUMMARIZE | 2h | 1h | 6 |
| `self-dev-scan` | SELF_DEV_SCAN | 4h | 2h | 4 |

## Usage

```python
from aegis_ai.scheduler import Scheduler, ScheduledTask, TaskType

scheduler = Scheduler()
scheduler.create_default_tasks()

# Check for due tasks
due = scheduler.get_due_tasks()
for task in due:
    scheduler.mark_started(task.task_id)
    # ... execute task ...
    scheduler.mark_completed(task.task_id)
```

## Safety

- All scheduled tasks are read-only or generate proposals
- Level 2+ actions require approval through normal PolicyEngine flow
- Cooldown prevents high-frequency LLM calls
- Daily budget limits total runs
