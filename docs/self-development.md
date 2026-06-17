# Self-Development — Architecture & Design

> **Status**: Implemented — desire-driven autonomous loop with learning pipeline
> **Related**: `docs/architecture.md`, `docs/memory.md`, `docs/mind-layer.md`

## Overview

AEGIS improves itself through a desire-driven autonomous loop that generates,
executes, and learns from actions. The system is organized around six core
components connected by a learning pipeline that promotes raw experience into
reusable skills.

**Main merge is always user-only.**

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   AutonomousController                   │
│  DesireSystem → IntrinsicTaskGenerator → MotivationArbiter│
└──────────────────────────┬──────────────────────────────┘
                           │ tick()
                           ▼
┌─────────────────────────────────────────────────────────┐
│                     AutonomousLoop                       │
│  desire monitoring · task generation · execution ·       │
│  self-scheduling · reflection · experience recording     │
│                                                          │
│  ┌──────────────┐  ┌──────────────────┐                 │
│  │   Planner    │  │ CuriosityDriven  │                 │
│  │  (subtask    │  │   Exploration    │                 │
│  │decomposition)│  │  (autonomous     │                 │
│  └──────────────┘  │   learning)      │                 │
│                    └──────────────────┘                 │
│  ┌──────────────────────────────────────┐               │
│  │    SpontaneousObservationSystem      │               │
│  │  (periodic environment awareness)    │               │
│  └──────────────────────────────────────┘               │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Learning Pipeline                       │
│                                                          │
│  ActionTrace ──consolidation──→ Lesson                   │
│       │                            │                     │
│       │──repeated patterns────→ Workflow                 │
│       │                            │                     │
│       └──reliable workflows────→ Skill                   │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 SleepConsolidationSystem                  │
│  episode summarization · person updates ·                │
│  knowledge extraction · association linking ·             │
│  lesson extraction · trace→workflow→skill promotion       │
└─────────────────────────────────────────────────────────┘
```

## Components

### AutonomousLoop

**File**: `src/aegis_ai/autonomous/autonomous_loop.py`

The central execution engine. Runs in a background thread and drives
all autonomous behavior.

| Feature | Description |
|---------|-------------|
| Desire monitoring | Checks desire states every tick; triggers execution when gap ≥ 2.0 |
| Task generation | LLM generates tasks for low desires; fallback to capability-mapped defaults |
| Skill/workflow reuse | Searches skill and workflow memory before executing from scratch |
| Action tracing | Full trace of every autonomous action (ExpeL/Reflexion inspired) |
| Self-scheduling | LLM decides next run interval (300–7200s); fallback 1 hour |
| Spontaneous observation | Periodic environment scan (every 5 minutes) |
| Curiosity exploration | Triggers when curiosity desire ≥ 6.0 |
| Reflection | Writes reflections after each task for future learning |
| **TaskManager integration** | Creates task before execution, completes/fails after |

**Constructor dependencies**: `llm_provider`, `desire_system`, `memory_system`,
`reflection_engine`, `tool_broker`, `world_state_store`, `experiential_memory`,
`affect_system`, `action_trace`, `skill_memory`, `workflow_memory`, `lesson_memory`,
`observation_system`, `curiosity_system`, `policy_engine`, `task_manager` (optional)

### AutonomousPlanner

**File**: `src/aegis_ai/autonomous/planner.py`

Converts high-level goals into executable subtask plans.

| Feature | Description |
|---------|-------------|
| LLM decomposition | Breaks goals into subtasks with capability_ids and dependencies |
| "Don't do" decisions | LLM can cancel unsafe or impossible goals |
| Dependency resolution | Executes subtasks in dependency order |
| Verification | Post-execution verification of subtask outputs |
| Failure replanning | Retries failed subtasks (up to 3 replans) |
| Permission checking | Detects approval-required steps via PolicyEngine |

**Data structures**: `ExecutionPlan` → `Subtask` (with `SubtaskStatus`)

### CuriosityDrivenExplorationSystem

**File**: `src/aegis_ai/autonomous/curiosity_exploration.py`

Autonomous learning through exploration, inspired by Voyager and
curiosity-driven RL.

| Feature | Description |
|---------|-------------|
| Candidate generation | From questions, failures, unknown concepts, improvements, LLM suggestions |
| Multi-factor prioritization | importance×0.3 + novelty×0.25 + usefulness×0.2 + interest×0.2 − risk×0.1 |
| Read-only exploration | All exploration is read-only; side effects require approval |
| Memory integration | Saves findings to episodic, semantic, and action trace memory |

### SpontaneousObservationSystem

**File**: `src/aegis_ai/autonomous/spontaneous_observation.py`

Periodic self-initiated environmental awareness without being asked.

Observes: system state changes, unfinished tasks, memory patterns,
emotional state shifts, desire fluctuations, capability availability,
and interesting anomalies.

### MotivationArbiter

**File**: `src/aegis_ai/autonomous/motivation_arbiter.py`

Selects the single task to execute next from candidates provided by
multiple sources (user, schedule, events, desires). Respects safety,
cooldowns, and priority ordering. Does NOT replace PolicyEngine.

### AutonomousController

**File**: `src/aegis_ai/autonomous/autonomous_controller.py`

Connects DesireSystem, IntrinsicTaskGenerator, MotivationArbiter,
and DesireActionEvaluator into a single `tick()` cycle.

Safety: `tick(dry_run=True)` returns decision without executing.
Single task per tick — no batch execution.

## Learning Pipeline

The learning pipeline promotes raw experience into reusable knowledge
through four stages, driven by SleepConsolidation.

### Stage 1: ActionTrace

**File**: `src/aegis_ai/memory/action_trace.py`

Records every autonomous action with complete context: purpose, plan,
execution steps, tool calls, results, failure reasons, verification.
Inspired by ExpeL and Reflexion.

### Stage 2: Lesson

**File**: `src/aegis_ai/memory/lesson_memory.py`

Extracted from ActionTraces during consolidation. Types: `success_pattern`,
`failure_analysis`, `optimization`, `warning`. Has applicability patterns
for matching future situations.

### Stage 3: Workflow

**File**: `src/aegis_ai/memory/workflow_memory.py`

Repeated successful action patterns promoted from traces. Contains
ordered steps with tool calls and arguments. Matched by goal pattern.

### Stage 4: Skill

**File**: `src/aegis_ai/memory/skill_memory.py`

The highest level of learning. Proven, reusable procedures extracted
from reliable workflows. Each skill has:

- **activation_conditions**: When to use
- **execution_steps**: How to execute
- **termination_conditions**: When to stop
- **failure_handling**: What to do on failure
- **Success/failure tracking**: Continuous performance monitoring

### Promotion Pipeline (SleepConsolidation)

```
ActionTrace ──_traces_to_lessons()──→ Lesson
    │
    │──_traces_to_workflows()──→ Workflow  (≥2 similar successful traces)
    │
    └──_workflows_to_skills()──→ Skill    (≥3 uses, ≥70% success rate)
```

## SleepConsolidationSystem

**File**: `src/aegis_ai/memory/sleep_consolidation.py`

Memory consolidation that runs periodically (default every 6 hours)
or on manual trigger. Inspired by how human sleep organizes memories.

| Operation | Description |
|-----------|-------------|
| Episode summarization | Groups unconsolidated episodes by category, LLM summarizes |
| Person record updates | Updates person records from recent episode interactions |
| Knowledge extraction | Converts episode lessons → semantic knowledge |
| Association linking | Creates links between related episodes (person, tag, temporal) |
| Lesson extraction | Extracts lessons from failed/negative episodes |
| Duplicate merging | Finds and merges duplicate semantic entries |
| Affect consolidation | Personality drift from emotional patterns |
| Trace → Lesson | Extracts lessons from unconsolidated ActionTraces |
| Trace → Workflow | Promotes repeated successful patterns to Workflows |
| Workflow → Skill | Promotes reliable workflows (≥3 uses, ≥70% success) to Skills |

## Safety Model

| Gate | Behavior |
|------|---------|
| PolicyEngine | All tool calls pass through deterministic safety engine |
| Planner cancellation | LLM can cancel unsafe/impossible goals |
| Curiosity read-only | Exploration has no side effects; actions require approval |
| Observation read-only | Observations are read-only; actions require approval |
| Single task per tick | AutonomousController executes one task per cycle |
| Dry-run mode | `tick(dry_run=True)` returns decision without executing |
| Approval flow | Level 2+ operations require user approval |
| MERGE | **FORBIDDEN** — user-only, no API exists |

## What AutonomousLoop NEVER Does

- Merges to main
- Pushes to main
- Deploys to production
- Accesses secrets
- Installs system packages
- Bypasses PolicyEngine
- Auto-approves its own operations
- Deletes the repository

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/autonomous/status` | GET | Get loop status |
| `/api/autonomous/trigger` | POST | Manual trigger |
| `/api/autonomous/start` | POST | Start loop |
| `/api/autonomous/stop` | POST | Stop loop |
| `/api/desires` | GET | Get desire states |
