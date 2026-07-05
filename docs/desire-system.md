# Desire System — Design & Usage

> **Status**: Implemented (2026-06-13)
> **Inspired by**: D2A (Desire-driven Autonomous Agent) — https://github.com/zfw1226/D2A
> **Source**: `ai-server/src/aegis_ai/desire/desire_system.py`

## Overview

AEGIS's desire system implements intrinsic motivations that drive autonomous behavior.
Based on the D2A framework from ICLR 2025.

Each desire has a **value** (current satisfaction), an **expected value** (target), and a derived **frustration** (`max(0, expected − value)`). Desires only increase via LLM evaluation after actions; they decay naturally over time.

## Desires (0-10 scale)

| Desire | Description | Expected | Decay/hr | Safety Category |
|--------|-------------|----------|----------|-----------------|
| **user_helpfulness** | Drive to effectively assist the user | 8.0 | 0.15 | general |
| **learning_progress** | Need for personal growth and self-improvement | 7.0 | 0.10 | general |
| **curiosity** | Need for exploration and discovering new things | 7.0 | 0.08 | general |
| **system_safety** | Need for security, stability, and protection | 9.0 | 0.05 | security |
| **reliability** | Need to be dependable and error-free | 8.0 | 0.10 | general |
| **autonomy** | Need for independence and self-determination | 6.0 | 0.12 | general |
| **social_connection** | Need for social interaction and connection | 6.0 | 0.15 | social |
| **creativity** | Need for self-expression and creative output | 6.0 | 0.10 | general |
| **purpose** | Need for meaning, direction, and sense of purpose | 7.0 | 0.08 | general |
| **maintenance** | Need for system health and resource management | 7.0 | 0.10 | general |

**Note**: Physiological needs (hunger, thirst, sleepiness) are excluded.

### Legacy Name Mapping

Older code/docs used different names. The system maps them automatically:

| Old Name | Current Name |
|----------|--------------|
| social_connectivity | social_connection |
| personal_fulfillment | learning_progress |
| safety | system_safety |
| recognition | reliability |

## How It Works

### 1. Time-Based Decay

Desires naturally decrease over time based on per-desire `decay_rate_per_hour`:
- Applied via `apply_decay()` before each evaluation
- Prevents desires from staying at maximum
- Hidden desires are skipped

### 2. Action Evaluation (LLM-Driven)

After each action, LLM evaluates how it affects desires:
```
Action: Helped user with coding
Observation: User was satisfied

→ user_helpfulness: 7.0 → 7.5 (positive interaction)
→ learning_progress: 5.5 → 6.0 (task achievement)
→ reliability: 6.0 → 6.5 (task completed successfully)
→ purpose: 5.0 → 5.5 (being useful)
```

The LLM receives current desire states, recent action history, and the action/observation pair. It returns JSON with updated values and reasons.

### 3. Frustration Tracking

Each desire tracks **frustration** = `max(0, expected_value − value)`:
- High frustration signals unmet needs
- Tasks are generated when frustration exceeds threshold (3.0) or value drops below threshold (4.0)
- `create_snapshot()` provides `average_frustration`, `max_frustration`, and `top_unsatisfied_desires`

### 4. Task Generation

When desires are below threshold:
1. Identify low desires (value < 4.0 or frustration >= 3.0)
2. LLM generates tasks to fulfill them
3. Execute tasks autonomously via the autonomous loop
4. Update desires based on results

## CuriosityDrivenExploration

> **Source**: `ai-server/src/aegis_ai/autonomous/curiosity_exploration.py`

When the `curiosity` desire is high (>= threshold, default 6.0), AEGIS autonomously explores:

### Exploration Sources

| Source | Description |
|--------|-------------|
| **Questions** | Unresolved questions from semantic and episodic memory |
| **Failures** | Recent failed actions — why did they fail? |
| **Unknowns** | Partially understood concepts (low confidence knowledge) |
| **Improvements** | Underperforming skills (success rate < 60%) |
| **LLM Suggestions** | LLM-recommended topics based on current state |

### Candidate Scoring

Each exploration candidate is scored by:

| Factor | Weight | Description |
|--------|--------|-------------|
| Importance | 0.30 | Relevance to current goals |
| Novelty | 0.25 | How new/unknown |
| Usefulness | 0.20 | Potential benefit |
| Interest | 0.20 | Curiosity engagement |
| Risk | -0.10 | Safety concern (penalty) |

### Exploration Flow

1. `generate_exploration_candidates()` — gather from all sources, deduplicate, sort by priority
2. `select_best_candidate()` — pick highest priority score
3. `explore(candidate)` — LLM investigates the topic, generates findings
4. Results saved to episodic memory, semantic memory, and action trace

**Safety**: All exploration is read-only. Side effects require PolicyEngine approval.

## Autonomous Loop Integration

> **Source**: `ai-server/src/aegis_ai/autonomous/autonomous_loop.py`

The desire system drives the autonomous execution loop:

### Loop Tick

1. **Desire monitoring** — `apply_decay()`, check for low desires
2. **Spontaneous observation** — every 5 minutes (if observation system configured)
3. **Curiosity exploration** — when `curiosity` desire >= threshold
4. **Desire-driven execution** — when desires are critically low (gap >= 2.0) or scheduled time reached

### Task Execution Pipeline

For each task the loop:
1. **Creates a Task** via TaskManager (9-state lifecycle)
2. Begins an **ActionTrace** for tracking
3. Searches **SkillMemory** for a reusable skill
4. Falls back to **WorkflowMemory** if no skill found
5. Retrieves relevant **LessonMemory** entries
6. Executes via ToolBroker (capability) or AutonomousPlanner (LLM plan)
7. **Completes/Fails the Task** via TaskManager
8. Records result to skill/workflow memory
9. Completes the action trace

### Task Evaluation (3-tier)

| Field | Description |
|-------|-------------|
| `tool_success` | Whether the tool execution succeeded (bool) |
| `task_effect` | Classification: `useful`, `no_effect`, `failed`, `blocked`, `needs_followup` |
| `desire_delta_hint` | Per-desire delta based on fulfillment conditions |

The fulfillment rules are defined in `ai-server/src/aegis_ai/desire/fulfillment.py`
as per-desire condition→delta pairs. "No new posts" etc. are `task_effect=NO_EFFECT`
with delta=0.0 (no desire decrease).

### Self-Scheduling

After execution, LLM decides the next interval:

| Desire State | Next Run |
|--------------|----------|
| Many low | 5-15 minutes |
| Balanced | 30-60 minutes |
| All high | 1-2 hours |
| Fallback | 1 hour |

## Learning Pipeline (ActionTrace → Skill)

> **Sources**:
> - `ai-server/src/aegis_ai/memory/action_trace.py`
> - `ai-server/src/aegis_ai/memory/skill_memory.py`

The learning pipeline converts experience into reusable knowledge:

```
ActionTrace → Lesson → Workflow → Skill
```

### ActionTrace

Full trace of every autonomous action:
- Goal, context, triggering desire
- Execution steps with tool calls and results
- Success/failure outcome and failure reason
- Difficulty and novelty scores
- Consolidation and lesson-extraction flags

Stored in `data/memory/action_traces.jsonl` (max 500 traces).

### SkillMemory

Reusable procedures extracted from successful patterns:

| Field | Description |
|-------|-------------|
| activation_conditions | When to use this skill |
| execution_steps | How to execute (tool calls with args) |
| termination_conditions | When to stop |
| failure_handling | What to do on failure |
| success_count / failure_count | Outcome tracking |

Skills are auto-deprecated when success rate drops below 30% after 5+ uses.

### Integration with Autonomous Loop

During task execution (`_execute_tasks`):
- ActionTrace records every step
- SkillMemory is searched before execution for reusable skills
- Results feed back into skill reliability tracking
- CuriosityDrivenExploration records findings to action trace

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/desires` | GET | Get current desire states |
| `/api/autonomous/status` | GET | Get autonomous loop status |
| `/api/autonomous/trigger` | POST | Manual trigger |
| `/api/autonomous/start` | POST | Start autonomous loop |
| `/api/autonomous/stop` | POST | Stop autonomous loop |

## Data Storage

- `data/desires/desire_state.json` — Current desire values with history
- `data/autonomous/loop_state.json` — Loop scheduling state
- `data/autonomous/execution_log.jsonl` — Execution history
- `data/autonomous/exploration_log.jsonl` — Curiosity exploration results
- `data/memory/action_traces.jsonl` — Action traces (max 500)
- `data/memory/skills.jsonl` — Learned skills

## Design Decisions

1. **D2A-inspired**: Based on ICLR 2025 paper
2. **LLM evaluation**: LLM objectively evaluates how actions affect desires
3. **No keyword matching**: All decisions through LLM
4. **Self-scheduling**: AI decides when to run next
5. **Desire-driven**: Desires drive autonomous behavior
6. **Frustration tracking**: Gap between expected and actual drives task generation
7. **Curiosity exploration**: High curiosity triggers autonomous learning

## Current Autonomous Fulfillment Rules

- LLM-backed autonomous decisions are gated by `AEGIS_MIN_LLM_INTERVAL_MS`, default `1800000` ms (30 minutes). Desire pressure checks continue every minute, and high-pressure cycles should attempt at least one safe/read-only action after the gate opens.
- Observations and pressure updates continue between LLM calls, but they do not bypass the gate.
- A `USEFUL` tool result reduces desire pressure by the normal amount and updates `last_action_at`.
- `NEEDS_FOLLOWUP` reduces pressure by half.
- `NO_EFFECT`, failed, or blocked results do not reduce pressure.
- Browser, Room, Dev, PC, and Android capability availability is based on StatusManager server status, not localhost port checks.
8. **Learning pipeline**: ActionTrace → Skill for cumulative self-improvement
9. **Excluded physiological**: No hunger, thirst, sleepiness
