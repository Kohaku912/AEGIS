# Memory System — Design & Usage

> **Status**: Implemented (2026-06-13)
> **Related**: `docs/architecture.md` §5.10

## Overview

AEGIS's memory system stores and retrieves information across sessions.
Inspired by Zep (https://github.com/getzep/zep) for human-like memory.

The system has two layers:
1. **Core memory** — entity/fact tracking, person data, semantic search
2. **Learning memory** — action traces, lessons, workflows, skills (promoted via sleep consolidation)

## Memory Components

### Core Memory

#### AdvancedMemory (`memory/advanced.py`)

Zep-inspired memory system with:
- **Entity tracking**: People, places, things with relationships
- **Fact extraction**: LLM extracts facts from conversations
- **Temporal awareness**: Tracks when facts were valid/invalid
- **Importance scoring**: More important memories recalled more easily
- **Consolidation**: Periodic cleanup and summarization

**Data storage**: `data/memory/` (entities.jsonl, facts.jsonl, conversations.jsonl)

#### PersonaMemory (`memory/persona.py`)

Person tracking system:
- **Person data**: Name, relationship, notes, preferences
- **Conversation history**: Summaries and key points
- **Topic tracking**: What was discussed

**Data storage**: `data/persona.jsonl`

#### ChromaSemanticMemory (`memory/chroma_semantic.py`)

Vector DB with Chroma:
- **Semantic search**: Find similar content
- **OpenAI embeddings**: text-embedding-3-small
- **Fact storage**: Categorized facts

**Data storage**: `data/chroma/`

#### MemoryConsolidator (`memory/consolidation.py`)

Periodic memory cleanup:
- **Duplicate merging**: Combine similar facts
- **Persona updates**: Update person profiles
- **LLM reflection**: Generate insights from memory

### Learning Memory

#### ActionTraceMemory (`memory/action_trace.py`)

Records full traces of autonomous actions. Inspired by ExpeL and Reflexion.

Each trace captures:
- **Goal**: What the action was trying to achieve
- **Context**: Desire state, trigger, environment
- **Steps**: Ordered list of `ExecutionStep` (tool call, args, result, duration)
- **Verification**: Whether the goal was met
- **Failure reasons**: Why it failed (if applicable)

Traces are the raw material for the learning pipeline — lessons, workflows, and skills are all derived from successful and failed traces.

```python
atm = ActionTraceMemory()
trace = atm.begin_trace(goal="Check AGORA", context="social_connection desire")
atm.add_step(trace, tool_call="agora.read_posts", result="{posts: [...]}")
atm.complete_trace(trace, success=True, verification="Posts read successfully")
```

**Data storage**: `data/memory/action_traces.jsonl`

#### LessonMemory (`memory/lesson_memory.py`)

Stores lessons extracted from action traces during consolidation. Inspired by Reflexion and ExpeL.

Lesson types:
- `success_pattern` — what worked and why
- `failure_analysis` — what went wrong and how to avoid it
- `optimization` — ways to do things faster/cheaper
- `warning` — risks or edge cases to watch for

Each lesson has:
- **applicability**: Pattern for when the lesson applies
- **confidence/importance**: Scoring for retrieval ranking
- **helpfulness tracking**: `times_applied` / `times_helpful` for auto-deprecation

```python
lm = LessonMemory()
lm.add(Lesson(
    content="AGORA API requires authentication before reading posts",
    lesson_type="failure_analysis",
    source_trace_id="trace_abc",
    applicability="agora.*",
))
relevant = lm.get_relevant("Read AGORA posts")
```

**Data storage**: `data/memory/lessons.jsonl`

#### WorkflowMemory (`memory/workflow_memory.py`)

Stores repeated successful action patterns extracted from traces. Inspired by Agent Workflow Memory and Voyager.

Workflows are ordered sequences of steps that have been observed to work for specific goal types. They sit between raw traces (too specific) and skills (too abstract).

```python
wm = WorkflowMemory()
wm.add(Workflow(
    name="Check AGORA for messages",
    goal_pattern="agora.*message|check.*agora",
    steps=[
        {"tool": "ai.agora.read_posts", "args": {"limit": 10}},
        {"tool": "llm", "action": "Summarize posts"},
    ],
))
workflow = wm.find_matching("Check AGORA for new messages")
```

**Data storage**: `data/memory/workflows.jsonl`

#### SkillMemory (`memory/skill_memory.py`)

Stores reusable skills — the highest level of learning. Inspired by Voyager's skill library and ExpeL's policy extraction.

Skills are promoted from workflows that have been repeatedly successful. Each skill has:
- **activation_conditions**: When to use this skill
- **execution_steps**: How to execute (tool calls + LLM actions)
- **termination_conditions**: When to stop
- **failure_handling**: What to do on failure
- **Success/failure tracking**: Auto-deprecates skills with low success rates

```python
sm = SkillMemory()
sm.add_skill(Skill(
    name="Read AGORA Messages",
    activation_conditions="User asks about messages OR social_connection desire is low",
    execution_steps=[
        {"tool": "ai.agora.read_posts", "args": {"limit": 10}},
        {"tool": "llm", "action": "Summarize important messages"},
    ],
    termination_conditions="Posts read and summarized",
    failure_handling="If AGORA unavailable, inform user and retry later",
))
skill = sm.find_skill("Check for new messages")
```

**Data storage**: `data/memory/skills.jsonl`

### Sleep Consolidation

#### SleepConsolidationSystem (`memory/sleep_consolidation.py`)

Periodically consolidates short-term memories into long-term organized memory. Inspired by how human sleep organizes memories from the day.

Runs automatically (default: every 6 hours) or can be triggered manually.

**Consolidation pipeline:**

```
ActionTrace ──→ Lesson ──→ Workflow ──→ Skill
     │              │            │           │
     └── summarize  └── extract  └── promote └── promote
         episodes      knowledge    patterns    procedures
```

Operations during sleep:
1. Summarize recent episodes and action traces
2. Extract lessons from successes and failures
3. Promote repeated successful traces → workflows
4. Promote repeated successful workflows → skills
5. Update person records from interactions
6. Create association links between related memories
7. Auto-deprecate low-confidence lessons and low-success skills
8. Log consolidation results

```python
sleep = SleepConsolidationSystem(
    episodic=ep, semantic=sem, person=pm, association=am,
    action_trace=atm, lesson=lm, workflow=wm, skill=sm,
    llm=llm,
)
result = sleep.consolidate()       # Manual trigger
# Or: sleep.start_auto(interval_hours=6)  # Automatic
```

**Data storage**: `data/memory/consolidation_log.jsonl`

## Learning Hierarchy

The learning pipeline promotes raw experience into reusable knowledge:

```
ActionTrace → Lesson → Workflow → Skill
(failed/successful)   (extracted)  (repeated)   (proven)
```

| Level | Source | Represents |
|-------|--------|------------|
| **ActionTrace** | Raw execution | What happened (one specific run) |
| **Lesson** | Extracted from traces | What to learn (knowledge nugget) |
| **Workflow** | Repeated successful traces | How to do it (reusable sequence) |
| **Skill** | Repeated successful workflows | Proven procedure (with conditions) |

Promotion criteria:
- **Trace → Lesson**: After consolidation, LLM extracts insights
- **Trace → Workflow**: Same goal pattern succeeded 3+ times with similar steps
- **Workflow → Skill**: Workflow succeeded 5+ times, promoted with activation/termination conditions

## How It Works

### Memory Context

Before each LLM call, the system:
1. Queries AdvancedMemory for relevant entities and facts
2. Queries PersonaMemory for person information
3. Queries LessonMemory for relevant lessons
4. Queries SkillMemory for applicable skills
5. Builds context string for LLM prompt

### Auto-Save

After each conversation:
1. LLM extracts entities and facts
2. Saves to AdvancedMemory
3. Updates PersonaMemory if person mentioned

### Autonomous Action Recording

After each autonomous action:
1. ActionTraceMemory records full trace (goal, steps, result)
2. During next sleep consolidation:
   - Lessons extracted from trace
   - If successful pattern repeated → workflow created
   - If workflow proven → skill promoted

### Memory Operations

| Operation | LLM Action | Description |
|-----------|-----------|-------------|
| Save | `memory_save` | LLM decides what to save |
| Search | `memory_search` | LLM queries memory |
| Delete | `memory_delete` | LLM deletes matching facts |
| Clear | `memory_clear` | Delete all memory |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/stream` | POST | Chat with memory context |
| `/dashboard/memory` | GET | View memory data |

## Design Decisions

1. **LLM-managed**: LLM decides what to remember/search/delete
2. **No keyword matching**: All memory operations through LLM
3. **Zep-inspired**: Entity tracking, fact extraction, temporal awareness
4. **ChromaDB**: Vector DB for semantic search
5. **JSONL storage**: Simple, reliable, human-readable
6. **Sleep consolidation**: Experience → knowledge promotion during idle periods
7. **Learning hierarchy**: Traces → Lessons → Workflows → Skills (ExpeL/Voyager/Reflexion)
