# Memory System — Design & Operations

> **Status**: Phase 1.x — Basic implementation (2026-06-11)  
> **Related**: [`architecture.md`](architecture.md)

## Overview

AEGIS has four memory types, each persisted to JSONL files:

| Memory Type | File | Purpose |
|-------------|------|---------|
| Episodic | `data/episodic.jsonl` | Conversations, events, action history |
| Semantic | `data/semantic.jsonl` | Facts, knowledge, user info, design |
| Procedural | `data/procedural.jsonl` | Successful procedures, failure patterns, tool tips |
| Reflection | `data/reflection.jsonl` | Self-analysis, improvement ideas |

## Storage Format

All memories use **JSONL** (one JSON object per line) for simplicity and append-only guarantees.

### Episodic Memory Entry

```json
{"episode_id": "ep_...", "summary": "User asked about weather", "category": "conversation", "events": ["evt-001"], "detail": {"topic": "weather"}, "timestamp_ms": 1700000000000}
```

### Semantic Memory Entry

```json
{"fact_id": "fact_...", "content": "User prefers dark mode", "category": "preference", "source": "user", "confidence": 1.0, "tags": ["ui"], "timestamp_ms": 1700000000000}
```

### Procedural Memory Entry

```json
{"procedure_id": "proc_...", "goal": "Check weather", "steps": ["browser.open_page", "browser.extract_page_text"], "tags": ["successful"], "success_count": 3, "failure_count": 0, "confidence": 1.0, "timestamp_ms": 1700000000000}
```

### Reflection Entry

```json
{"reflection_id": "refl_...", "summary": "Screenshot worked well", "what_worked": ["fast response"], "what_failed": [], "improvement_ideas": ["increase quality"], "next_experiment": "Try full page", "linked_event_ids": ["evt-001"], "timestamp_ms": 1700000000000}
```

## Data Location

All memory files are stored in the `data/` directory:
```
ai-server/
└── data/
    ├── episodic.jsonl
    ├── semantic.jsonl
    ├── procedural.jsonl
    └── reflection.jsonl
```

## Data Deletion

To reset all memories:
```bash
rm ai-server/data/episodic.jsonl
rm ai-server/data/semantic.jsonl
rm ai-server/data/procedural.jsonl
rm ai-server/data/reflection.jsonl
```

Individual entries cannot be deleted — memories are append-only by design. If a fact becomes incorrect, add a new entry with updated confidence or tags.

## Context Builder Integration

The ContextBuilder queries all four memory types when building context:
- **Episodic**: `list_recent(10)` — last 10 episodes
- **Semantic**: `search(query)` — facts matching the trigger query
- **Procedural**: `find_for_goal(query)` — procedures for this goal
- **Reflection**: `list_recent(5)` — last 5 reflections

Context is capped at ~8000 characters (~2000 tokens) to stay within LLM budget.

## Future Extensions

- **Vector DB**: Semantic memory will be upgraded to support RAG with embedding-based search
- **SQLite**: May replace JSONL for better query performance
- **Tamper-evident log**: Hash chain for audit trail

## Security

- **No secrets**: Passwords, tokens, and API keys must never be stored in memory
- **No external transmission**: Memory data stays on local disk
- **Append-only**: Entries cannot be modified or deleted (immutable history)
