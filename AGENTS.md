# AGENTS.md — AEGIS Project

## Purpose

AEGIS is an **autonomous multi-device AI assistant** platform.
AEGIS operates via event-driven coordination across multiple servers to provide:

- User assistance (schedule, tasks, information)
- Information gathering and analysis
- Self-improvement and learning
- Desire-driven autonomous behavior

**Core principle**: AEGIS is event-driven, multi-device, self-improving, and desire-driven.
All server communication uses **gRPC** with shared protobuf definitions.

---

## Technology Decision Gate

**CRITICAL RULE**: AI coding agents MUST NOT make major technology decisions autonomously.
When multiple viable options exist for the same feature, the agent MUST present a
structured comparison and ask the user to decide.

### When to Ask (Mandatory Consultation Triggers)

Ask the user before implementing when:

| Trigger | Examples |
|---------|----------|
| **Multiple viable options** | Playwright vs browser-use, REST vs WebSocket vs gRPC streaming |
| **Different from existing design** | Using a different language/framework than what docs specify |
| **New external service** | Cloud APIs, payment APIs, third-party SaaS |
| **Security/privacy impact** | New data storage, new network exposure, credential handling |
| **Language/Framework change** | Switching Node.js→Python, SQLite→Postgres, etc. |

### NOT Required to Ask

The agent may proceed without asking when:
- Implementing to an existing proto contract
- Following AGENTS.md / architecture.md specifications exactly
- Adding tests for existing code
- Fixing bugs within existing implementation patterns

---

## Core Design Philosophy: LLM-Driven Operations

**ALL operations must be decided by LLM, not keyword matching.**

### Absolute Rules

1. **NEVER implement keyword-based detection systems.**
   - No keyword matching, regex patterns, or string detection
   - No `if "screenshot" in text.lower()` patterns
   - No `if any(kw in text for kw in [...])` patterns

2. **LLM is the interpreter.**
   - All user messages MUST be interpreted by the LLM
   - LLM decides what actions to take
   - LLM decides what to remember
   - LLM generates all final responses

3. **All responses must come from LLM.**
   - Every tool action result must pass through LLM
   - No raw JSON or system messages returned to user
   - Pattern: Action → Result → LLM → Final Response

4. **Memory is LLM-managed.**
   - LLM decides what to remember
   - LLM decides what to search
   - LLM decides what to delete
   - No keyword-based memory operations

---

## Architecture Overview

### Servers

| Server | Language | Port | Purpose |
|--------|----------|------|---------|
| **AI Server** | Python 3.14 | 50051 | Central brain, LLM, memory, desires |
| **PC Server** | Rust | 50052 | Windows operations (screenshot, mouse, keyboard) |
| **Browser Server** | Python | 50053 | Web browsing with browser-use |
| **Android Server** | Kotlin | 50054 | Mobile device control |
| **Room Server** | Python | 50055 | IoT/sensor data |
| **Dashboard** | Flask | 8090 | Web UI, chat, monitoring |

### Core Systems

| System | Location | Purpose |
|--------|----------|---------|
| **Memory System** | `ai-server/src/aegis_ai/memory/` | AdvancedMemory (Zep-inspired), PersonaMemory, ChromaSemantic |
| **Desire System** | `ai-server/src/aegis_ai/desire/` | D2A-inspired intrinsic motivations (8 desires) |
| **Autonomous Loop** | `ai-server/src/aegis_ai/autonomous/` | Desire-driven task execution, self-scheduling |
| **LLM Router** | `ai-server/src/aegis_ai/llm/` | DeepSeek/OpenAI provider, task routing |
| **Policy Engine** | `ai-server/src/aegis_ai/policy_engine.py` | Deterministic safety gate |
| **Dashboard** | `ai-server/src/aegis_ai/web/` | Flask UI with streaming chat |

---

## Memory System

### Components

| Component | File | Purpose |
|-----------|------|---------|
| **AdvancedMemory** | `memory/advanced.py` | Zep-inspired: entity tracking, fact extraction, temporal awareness |
| **PersonaMemory** | `memory/persona.py` | Person tracking with conversations |
| **ChromaSemanticMemory** | `memory/chroma_semantic.py` | Vector DB with Chroma |
| **MemoryConsolidator** | `memory/consolidation.py` | Periodic cleanup and reflection |

### Data Storage

- `data/memory/` — AdvancedMemory (entities.jsonl, facts.jsonl, conversations.jsonl)
- `data/persona.jsonl` — PersonaMemory
- `data/chroma/` — ChromaDB vector data
- `data/chat_history.jsonl` — Chat history

---

## Desire System (D2A-Inspired)

### Desires (0-10 scale)

| Desire | Description |
|--------|-------------|
| **social_connectivity** | Need for social interaction and connection |
| **personal_fulfillment** | Need for growth, achievement, self-actualization |
| **curiosity** | Need for exploration, learning, discovery |
| **safety** | Need for security, stability, protection |
| **recognition** | Need for acknowledgment, appreciation, respect |
| **autonomy** | Need for independence, control, self-determination |
| **creativity** | Need for self-expression, innovation, creative output |
| **purpose** | Need for meaning, direction, sense of purpose |

### How It Works

1. **Time-based decay**: Desires naturally decrease over time
2. **Action evaluation**: LLM evaluates how actions affect desires
3. **Task generation**: When desires are low, generate tasks to fulfill them
4. **Self-scheduling**: LLM decides when to run next based on desire states

---

## Autonomous Loop

### Features

- **Desire-driven execution**: When desires are low, execute tasks autonomously
- **Self-scheduling**: AI decides when to be called next
- **Fallback**: Runs every 1 hour if not called
- **Manual trigger**: Can be triggered via API

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/autonomous/status` | GET | Get loop status |
| `/api/autonomous/trigger` | POST | Manual trigger |
| `/api/autonomous/start` | POST | Start loop |
| `/api/autonomous/stop` | POST | Stop loop |
| `/api/desires` | GET | Get desire states |

---

## Dashboard

### Features

- **Streaming chat**: Real-time LLM response display
- **Memory integration**: AdvancedMemory context in LLM prompts
- **Desire context**: Current desire states in LLM prompts
- **All actions through LLM**: Every result passes through LLM for final response

### Chat API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/send` | POST | Send message (non-streaming) |
| `/api/chat/stream` | POST | Send message (streaming) |
| `/api/chat/history` | GET | Get chat history |
| `/api/chat/clear` | POST | Clear chat history |

---

## Code Style

### Python (ai-server/, browser-server/)
- Follow **PEP 8**
- Use `ruff` for linting & formatting
- **Type hints required** on all public functions
- Use `asyncio` for async operations
- Docstrings: Google style

### Rust (pc-server/)
- Follow **Rust style guide**
- Use `cargo fmt` and `cargo clippy`
- Error handling: `Result<T, E>` pattern

### Protocol Buffers (protos/)
- Use **proto3** syntax
- Service method names: `VerbNoun` pattern
- One service per proto file

---

## Testing Policy

- **Unit tests**: Required for all business logic
- **Integration tests**: Required for all gRPC services
- **Test files**: Co-located with source or in `tests/`
- **Test command**: `cd ai-server && pytest`

### Test Status
- **Total tests**: 1336+ passing
- **Memory system**: 8 tests
- **Desire system**: 7 tests
- **Autonomous loop**: 5 tests

---

## Security Policy

### Approval Gates (HARD REQUIREMENT)

The following operations MUST go through explicit user approval:

1. File deletion (any path outside temp directories)
2. SNS posting, DM sending, email sending
3. Physical device operation (lights, locks, AC, etc.)
4. Code execution in non-sandboxed environments
5. Access to credential stores (~/.ssh, ~/.aws, etc.)
6. Installing/updating system packages
7. Any operation costing money

### Data Handling
- User data never leaves local network without explicit consent
- Secrets managed via environment variables (never committed)
- Proto files must not contain sensitive defaults

---

## What AI Agents Must NOT Do

1. Delete or modify existing code without explicit instruction
2. Simplify the architecture (e.g., merging servers, removing gRPC layer)
3. Bypass or weaken security approval gates
4. Auto-execute: SNS posts, DM sends, physical device operations
5. Add dependencies without documenting the reason
6. Change proto definitions without updating all affected servers
7. Commit secrets, tokens, or credentials
8. Implement keyword-based detection systems
9. Return raw JSON or system messages to user
10. Make decisions without LLM involvement
11. **NEVER parse user messages with keyword matching, regex, or string detection.** The LLM is the interpreter. All user intent must be understood by the LLM, not by pattern matching. This applies to routing, action selection, category detection, and any decision based on user text. The LLM decides what the user wants — code never inspects user text for keywords.

---

## Current Status (2026-06-13)

### Implemented Systems

| System | Status | Tests |
|--------|--------|-------|
| **Memory System** | ✅ Complete | 8 tests |
| **Desire System** | ✅ Complete | 7 tests |
| **Autonomous Loop** | ✅ Complete | 5 tests |
| **Dashboard** | ✅ Complete | 14 pages |
| **PC Server** | ✅ Complete | 6 features |
| **LLM Integration** | ✅ Complete | DeepSeek API |

### Key Files

| File | Purpose |
|------|---------|
| `ai-server/src/aegis_ai/memory/advanced.py` | AdvancedMemory (Zep-inspired) |
| `ai-server/src/aegis_ai/desire/desire_system.py` | DesireSystem (D2A-inspired) |
| `ai-server/src/aegis_ai/autonomous/autonomous_loop.py` | AutonomousLoop |
| `ai-server/src/aegis_ai/web/dashboard_routes.py` | Dashboard with streaming chat |
| `ai-server/src/aegis_ai/llm/factory.py` | LLM provider factory |

### Environment

- **Python**: `C:\Users\kohak\AppData\Local\Python\pythoncore-3.14-64\python.exe`
- **LLM**: DeepSeek API (`deepseek-chat` model)
- **Embedding**: OpenAI API (`text-embedding-3-small`)
- **Dashboard**: Flask on port 8090
- **PC Server**: Rust on port 50052

---

## Per-Server Documentation

See individual AGENTS.md files for each server:

- `ai-server/AGENTS.md` — AI Server details
- `pc-server/AGENTS.md` — PC Server details
- `browser-server/AGENTS.md` — Browser Server details
- `android-server/AGENTS.md` — Android Server details
- `room-server/AGENTS.md` — Room Server details
