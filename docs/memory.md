# Memory System — Design & Usage

> **Status**: Implemented (2026-06-13)
> **Related**: `docs/architecture.md` §5.10

## Overview

AEGIS's memory system stores and retrieves information across sessions.
Inspired by Zep (https://github.com/getzep/zep) for human-like memory.

## Memory Components

### AdvancedMemory (`memory/advanced.py`)

Zep-inspired memory system with:
- **Entity tracking**: People, places, things with relationships
- **Fact extraction**: LLM extracts facts from conversations
- **Temporal awareness**: Tracks when facts were valid/invalid
- **Importance scoring**: More important memories recalled more easily
- **Consolidation**: Periodic cleanup and summarization

**Data storage**: `data/memory/` (entities.jsonl, facts.jsonl, conversations.jsonl)

### PersonaMemory (`memory/persona.py`)

Person tracking system:
- **Person data**: Name, relationship, notes, preferences
- **Conversation history**: Summaries and key points
- **Topic tracking**: What was discussed

**Data storage**: `data/persona.jsonl`

### ChromaSemanticMemory (`memory/chroma_semantic.py`)

Vector DB with Chroma:
- **Semantic search**: Find similar content
- **OpenAI embeddings**: text-embedding-3-small
- **Fact storage**: Categorized facts

**Data storage**: `data/chroma/`

### MemoryConsolidator (`memory/consolidation.py`)

Periodic memory cleanup:
- **Duplicate merging**: Combine similar facts
- **Persona updates**: Update person profiles
- **LLM reflection**: Generate insights from memory

## How It Works

### Memory Context

Before each LLM call, the system:
1. Queries AdvancedMemory for relevant entities and facts
2. Queries PersonaMemory for person information
3. Builds context string for LLM prompt

### Auto-Save

After each conversation:
1. LLM extracts entities and facts
2. Saves to AdvancedMemory
3. Updates PersonaMemory if person mentioned

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
