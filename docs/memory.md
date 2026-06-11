# Advanced Memory — Design & Usage

> **Status**: Phase 6 — Enhanced with persistence and retrieval
> **Related**: `docs/architecture.md` §5.10

## Overview

AEGIS's memory system stores and retrieves information across sessions.
All memory types persist to JSONL files for durability.

## Memory Types

### Episodic Memory (`episodic.py`)

Stores conversation, event, and action history.

| Field | Purpose |
|-------|---------|
| `summary` | What happened |
| `category` | "conversation", "event", "action_result" |
| `events` | Referenced event IDs |
| `detail` | Arbitrary detail dict |

Persists to `data/episodic.jsonl`.

### Semantic Memory (`semantic.py`)

Stores facts, knowledge, user info, design docs.

| Field | Purpose |
|-------|---------|
| `content` | The fact or knowledge |
| `category` | "user_info", "knowledge", "design", "preference", "project" |
| `source` | Where fact came from ("user", "conversation", "inference") |
| `confidence` | 0.0–1.0 certainty |
| `tags` | Searchable tags |

Persists to `data/semantic.jsonl`.

### Procedural Memory (`procedural.py`)

Stores successful procedures and failure patterns.

| Field | Purpose |
|-------|---------|
| `goal` | What the procedure achieves |
| `steps` | Capability IDs in order |
| `success_count` / `failure_count` | Track success rate |
| `confidence` | Calculated from success rate |

Persists to `data/procedural.jsonl`.

### Reflection Memory (`reflection.py`)

Stores self-analysis and improvement ideas.

| Field | Purpose |
|-------|---------|
| `summary` | What happened |
| `what_worked` | Successful aspects |
| `what_failed` | Failed aspects |
| `improvement_ideas` | Ideas for improvement |
| `next_experiment` | What to try next |

Persists to `data/reflection.jsonl`.

## ContextBuilder Integration

Memory is injected into ContextBuilder:

```python
builder = ContextBuilder(
    episodic_memory=EpisodicMemory(),
    semantic_memory=SemanticMemory(),
    procedural_memory=ProceduralMemory(),
    reflection_log=ReflectionLog(),
)
ctx = builder.build(triggering_query="temperature")
# ctx.recent_episodes — recent episodic memories
# ctx.relevant_facts — semantic facts matching query
# ctx.relevant_procedures — procedures matching query
# ctx.recent_reflections — recent reflections
```

## Privacy

- Memory is local-only (no external transmission)
- Secrets are never stored in memory
- Users can request memory deletion
- Sensitive data should be redacted before storage
