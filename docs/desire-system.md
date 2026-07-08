# Desire System — Design & Usage

> **Status**: Implemented (verified against current code snapshot)
> **Source**: `ai-server/src/aegis_ai/desire/`

## Overview

AEGIS uses a **pressure-based 3-desire model** to drive autonomous behavior.
The desire system does not manage a large list of motivations anymore. The current runtime tracks:

| Desire | Meaning |
|--------|---------|
| `user_support` | Assist the user, resolve pending requests, be helpful |
| `social` | Handle AGORA / conversations / social interaction |
| `growth` | Learn, explore, reflect, and improve |

The system is intentionally small. Desire pressure accumulates over time and from unprocessed events, then the autonomous loop decides whether to act.

## Core Modules

| File | Purpose |
|------|---------|
| `desire_system.py` | Desire state, snapshots, decay, thresholds |
| `pressure.py` | Pressure accumulation and gating |
| `fulfillment.py` | Task result evaluation and pressure deltas |
| `intrinsic_task_generator.py` | Generates candidate tasks from low desires |
| `desire_action_evaluator.py` | Scores task results against desire outcomes |

## How It Works

### 1. Pressure Accumulates

Pressure rises from:
- elapsed time
- pending events
- unresolved tasks
- low-satisfaction states

The loop does not use keyword matching. LLM decisions and task outcomes drive the updates.

### 2. The Loop Checks Gating

`_preflight_check()` and the autonomous loop gate LLM-driven work behind:
- desire pressure threshold
- provider availability
- state-change checks
- `AEGIS_MIN_LLM_INTERVAL_MS` minimum interval

### 3. Tasks Are Evaluated

`evaluate_task_result()` classifies a task into:
- `useful`
- `no_effect`
- `failed`
- `blocked`
- `needs_followup`

The result feeds pressure updates.

### 4. Desire Deltas Apply

Current fulfillment behavior:

| Desire | Condition | Delta |
|--------|-----------|-------|
| `user_support` | User request completed | positive |
| `user_support` | Mention reply created | positive |
| `user_support` | Tool error | negative |
| `social` | Posted to AGORA | positive |
| `social` | Read new posts | small positive |
| `social` | No new posts | 0.0 |
| `growth` | New info summarized | positive |
| `growth` | Empty results | 0.0 |

## Autonomous Loop Integration

The loop uses desire state to decide when to execute tasks.

Pipeline:

1. Apply decay / update pressure
2. Check whether the minimum LLM interval has elapsed
3. Generate candidate tasks when pressure is high enough
4. Execute through ToolBroker / TaskManager
5. Evaluate result and reduce or preserve pressure

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/desires` | GET | Current desire states |
| `/api/autonomous/status` | GET | Loop status |
| `/api/autonomous/trigger` | POST | Manual trigger |
| `/api/autonomous/start` | POST | Start loop |
| `/api/autonomous/stop` | POST | Stop loop |

## Data Storage

- `data/desires/desire_state.json`
- `data/autonomous/loop_state.json`
- `data/autonomous/execution_log.jsonl`
- `data/autonomous/exploration_log.jsonl`
- `data/memory/action_traces.jsonl`
- `data/memory/skills.jsonl`

## Notes

- The old 10-desire model is obsolete.
- Curiosity exploration exists in the autonomous subsystem, but the desire surface itself is now the 3-desire pressure model.
- All updates are code-driven and LLM-mediated.
