# Scheduler — Autonomous Loop Design & Usage

> **Status**: Implemented — Desire-driven with self-scheduling
> **Source**: `ai-server/src/aegis_ai/autonomous/autonomous_loop.py`
> **Related**: `docs/architecture.md` §5.12, `docs/mind-layer.md`

## Overview

The AEGIS scheduler is not a traditional cron/interval scheduler. It is a
**desire-driven autonomous loop** that monitors intrinsic motivations,
generates tasks to fulfill low desires, executes them, and decides when to
run next via LLM-based self-scheduling.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 AutonomousLoop                   │
│                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │  Desire   │──▶│  Task    │──▶│  Task    │    │
│  │  Monitor  │   │ Generator│   │ Executor │    │
│  └──────────┘   └──────────┘   └──────────┘    │
│       │                             │            │
│       ▼                             ▼            │
│  ┌──────────┐              ┌──────────────┐     │
│  │ Observe  │              │   Desire     │     │
│  │ System   │              │   Updater    │     │
│  └──────────┘              └──────────────┘     │
│       │                             │            │
│       ▼                             ▼            │
│  ┌──────────┐              ┌──────────────┐     │
│  │ Curiosity│              │ Self-Schedule│     │
│  │ Explorer │              │  (LLM)       │     │
│  └──────────┘              └──────────────┘     │
└─────────────────────────────────────────────────┘
```

## Execution Cycle

Each tick of the loop:

1. **Desire monitoring** — Apply time-based decay, check for low desires
2. **Spontaneous observation** — Every 5 minutes, run observation system
3. **Curiosity exploration** — When curiosity desire is high, explore topics
4. **Task execution** — If desires are low or scheduled time reached:
   - Generate tasks via LLM (or use default capability mappings)
   - Execute tasks through ToolBroker
   - Run reflection on results
   - Update desire values based on outcomes
   - Record experiences and appraise emotions
5. **Self-schedule** — LLM decides when to run next (300s–7200s)
6. **Fallback** — 1 hour if LLM scheduling fails or desires are balanced

## Desire-Driven Triggering

The loop triggers execution when:

| Condition | Behavior |
|-----------|----------|
| Desire gap ≥ 2.0 | Immediate execution (bypasses schedule) |
| Scheduled time reached | Normal execution cycle |
| All desires above threshold (4.0) | Fallback to 1-hour interval |

### Monitored Desires (0–10 scale)

| Desire | Low-desire default action |
|--------|--------------------------|
| `user_helpfulness` | Read AGORA posts for user requests |
| `learning_progress` | Read recent AGORA conversations |
| `curiosity` | Explore new topics via curiosity system |
| `system_safety` | Capture screenshot to verify state |
| `reliability` | Get system info for health check |
| `social_connection` | Check AGORA for new messages |
| `autonomy` | List windows to understand system state |
| `creativity` | Read AGORA posts for inspiration |
| `purpose` | Read AGORA mentions for user needs |
| `maintenance` | Check clipboard for pending tasks |

## Self-Scheduling

After each cycle, the LLM decides the next interval:

| Desire state | Typical interval |
|-------------|-----------------|
| Many desires low | 300–900 seconds (5–15 min) |
| Desires balanced | 1800–3600 seconds (30–60 min) |
| All desires high | 3600–7200 seconds (1–2 hours) |

Interval is clamped to [300, 7200] seconds. Falls back to 3600s (1 hour)
if the LLM response is unparseable.

## Observation System

Runs every 5 minutes (`_observation_interval_ms = 300_000`):

- Calls `observation_system.observe_all()`
- Filters for actionable items (importance ≥ 0.7)
- Logs count of actionable observations

## Curiosity Exploration

Activates when `curiosity_system.should_explore` is true (curiosity desire is high):

1. Generate exploration candidates
2. Select best candidate (priority > 0.5)
3. Execute exploration
4. Record findings

## Task Execution Pipeline

For each task:

1. **Action trace** — Begin trace with goal and desire context
2. **Skill search** — Check skill memory for reusable skill
3. **Workflow search** — Check workflow memory for matching workflow
4. **Lesson search** — Find relevant past lessons
5. **Execute** — Via ToolBroker (capability-based) or AutonomousPlanner (LLM plan)
6. **Analyze** — Screenshots analyzed via multimodal LLM
7. **Record** — Update skill/workflow success stats, complete trace

## Configuration

```python
loop = AutonomousLoop(
    llm_provider=llm,
    desire_system=desire,
    memory_system=memory,
    reflection_engine=reflection,
    tool_broker=broker,
    observation_system=observation,
    curiosity_system=curiosity,
    policy_engine=policy,
    desire_threshold=4.0,          # Below this = "low"
    max_tasks_per_cycle=3,         # Max tasks per execution
    fallback_interval_seconds=3600, # 1 hour fallback
)
loop.start()
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/autonomous/status` | GET | Loop status, next run time |
| `/api/autonomous/trigger` | POST | Manually trigger a cycle |
| `/api/autonomous/start` | POST | Start the loop |
| `/api/autonomous/stop` | POST | Stop the loop |
| `/api/desires` | GET | Current desire states |

## State Persistence

Loop state is saved to `data/autonomous/loop_state.json`:

```json
{
  "next_run_ms": 1718000000000,
  "last_run_ms": 1717996400000,
  "timestamp_ms": 1717996400000
}
```

Execution history is appended to `data/autonomous/execution_log.jsonl`.

## Safety

- All autonomous tasks go through PolicyEngine
- ToolBroker enforces capability-based execution limits
- Tasks are constructive and desire-aligned by design
- Manual trigger available via API for testing
- Fallback interval prevents runaway execution
