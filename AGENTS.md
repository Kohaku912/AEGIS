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

## Capability Management

### Architecture

Capabilities are defined as JSON files in a folder structure. This is the **single source of truth**.

```
capabilities/
├── builtin/
│   ├── pc-server/
│   │   ├── screenshot/
│   │   │   └── get_screenshot.json
│   │   └── system/
│   │       └── get_os_info.json
│   ├── browser-server/
│   ├── android-server/
│   └── room-server/
└── generated/
    └── ...
```

**CRITICAL**: No hardcoded capability definitions exist in Python code.
All capabilities are loaded from JSON manifests at startup.

### Capability ID Format

**Canonical format**: `server_id.app_id.action`

| Server ID | Example Capability ID |
|-----------|----------------------|
| `pc-server` | `pc-server.screenshot.get_screenshot` |
| `browser-server` | `browser-server.page.open_page` |
| `android-server` | `android-server.notification.get_notifications` |
| `room-server` | `room-server.environment.get_environment` |

### Backward-Compatible Aliases

Old ID formats are resolved via aliases in `CapabilityCatalog`:

| Old Format | Canonical Format |
|------------|------------------|
| `pc.screenshot.get_screenshot` | `pc-server.screenshot.get_screenshot` |
| `browser.page.open_page` | `browser-server.page.open_page` |
| `screenshot.get_screenshot` | `pc-server.screenshot.get_screenshot` |

Aliases are built at startup from JSON manifests. Code MUST use canonical format.

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| **CapabilityCatalog** | `aegis_ai/capability_catalog.py` | Unified interface, alias management, LLM listing |
| **FolderCapabilityRegistry** | `aegis_ai/folder_registry.py` | Loads JSON manifests from folder structure |
| **ToolRegistry** | `tool_registry.py` | In-memory registry for runtime capability lookup |
| **ToolBroker** | `tool_broker.py` | Capability invocation with safety enforcement |
| **ServerExecutor** | `server_executor.py` | Manifest-driven routing to server clients |

### Startup Flow

1. `CapabilityCatalog` loads all JSON manifests from `capabilities/`
2. `_capability_from_manifest()` converts manifests to `Capability` objects (canonical IDs)
3. `ToolRegistry` registers all capabilities
4. `ToolBroker` uses `ToolRegistry` + `CapabilityCatalog` for execution
5. `LLMTaskInterpreter` uses `CapabilityCatalog.list_for_llm()` for capability listing

### LLM Capability Listing

`CapabilityCatalog.list_for_llm()` returns capabilities formatted for LLM consumption:

```python
[
    {
        "id": "pc-server.screenshot.get_screenshot",
        "short_name": "screenshot.get_screenshot",
        "description": "Capture a screenshot of the desktop.",
        "params": [],
        "risk": "low",
        "only_master": False,
    },
    ...
]
```

### Rules for AI Agents

1. **NEVER hardcode capability IDs in Python code** — use `CapabilityCatalog.list_for_llm()`
2. **NEVER create `Capability()` objects directly** — load from JSON manifests
3. **ALWAYS use canonical format** `server_id.app_id.action`
4. **Add new capabilities** by creating JSON files in `capabilities/builtin/`

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
| **user_helpfulness** | Need to effectively assist the user |
| **reliability** | Need to be dependable and error-free |
| **system_safety** | Need for security and protection |
| **curiosity** | Need for exploration and learning |
| **social_connection** | Need for social interaction |
| **autonomy** | Need for independence and self-determination |
| **creativity** | Need for creative expression |
| **purpose** | Need for meaningful action |
| **learning_progress** | Need for growth and learning |
| **maintenance** | Need for system health |

### Task Evaluation (3-tier)

| Field | Description |
|-------|-------------|
| `tool_success` | Whether the tool execution succeeded (bool) |
| `task_effect` | Classification: `useful`, `no_effect`, `failed`, `blocked`, `needs_followup` |
| `desire_delta_hint` | Per-desire delta based on fulfillment conditions |

### Desire Fulfillment Rules

| Desire | Condition | Delta |
|--------|-----------|-------|
| **user_helpfulness** | User request completed | +0.8 |
| | Mention reply created | +0.5 |
| | No new posts | 0.0 |
| | Tool error | -0.3 |
| **reliability** | Error diagnosed and fixed | +0.8 |
| | Healthcheck passed | +0.4 |
| | Tool error | -0.3 |
| **system_safety** | Security check done | +0.8 |
| | Safety info saved | +0.3 |
| **curiosity** | New info summarized | +0.5 |
| | Empty results | 0.0 |
| **social_connection** | Posted to AGORA | +1.0 |
| | Read new posts | +0.1 (barely satisfies) |
| | Reactions received | +0.5 (meaningful) |
| | No new posts | 0.0 |

### How It Works

1. **Time-based decay**: Desires naturally decrease over time
2. **Task execution**: Tool calling executes capabilities
3. **Result evaluation**: `evaluate_task_result()` classifies effect and computes deltas
4. **Desire update**: Deltas are applied to desire values
5. **No-effect handling**: "No new posts" etc. are `task_effect=no_effect` with delta=0.0 (no decrease)

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

- **Streaming chat**: Real-time LLM response display with tool calling
- **Memory integration**: AdvancedMemory context in LLM prompts
- **Desire context**: Current desire states in LLM prompts
- **Tool calling**: Chat uses CapabilityCatalog for capability execution
- **Settings management**: All settings changes persist to `config/settings.json`

### Agentic Tool Calling Loop

The chat system supports **recursive multi-step tool calling** (max 5 rounds):

1. LLM receives user message and available tools
2. LLM calls a tool (or responds directly if no tool needed)
3. Tool executes and returns result
4. Result is fed back to the LLM
5. LLM decides: call another tool OR respond with summary
6. Loop continues until LLM responds without tool call, or max rounds reached

**Supported tool call formats:**
- `` format
- DeepSeek DSML format (`<｜DSML｜invoke ...>`)
- XML tag format (`<pc-server__shell__powershell><command>...</command></pc-server__shell__powershell>`)
- Plain JSON (`{"name": "...", "arguments": {...}}`)

**Error handling:**
- Tool failures are reported back to the LLM with error details
- LLM can retry with different arguments or try alternative approaches
- Command failures (exit code != 0) are properly detected and reported

**User input handling:**
- When a tool requires user input (e.g., browser verification), the loop pauses
- User is prompted to complete the action
- After user responds, the loop continues with the next tool call

### Chat API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/send` | POST | Send message (non-streaming, tool calling) |
| `/api/chat/stream` | POST | Send message (streaming, tool calling) |
| `/api/chat/history` | GET | Get chat history |
| `/api/chat/clear` | POST | Clear chat history |

### Settings API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/settings` | GET | Get all settings |
| `/api/settings/<section>` | POST | Update a section |
| `/api/settings/reset` | POST | Reset to defaults |
| `/api/settings/export` | GET | Export as JSON |

### Settings Persistence

Settings are persisted to `config/settings.json` (survives `data/` deletion).
Audit logs are written to `data/settings_audit.jsonl`.

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
- **Total tests**: 191 passing
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

## Current Status (2026-06-17)

### Implemented Systems

| System | Status | Notes |
|--------|--------|-------|
| **Capability Management** | ✅ Complete | Folder-based, JSON manifests, canonical ID format |
| **Desire System** | ✅ Complete | Delta-based evaluation, fulfillment rules |
| **Autonomous Loop** | ✅ Complete | Tool calling, frustration-based trigger, TaskManager integrated |
| **Dashboard** | ✅ Complete | Tool calling chat, user input support, Manager API routes (19 routes) |
| **PC Server** | ✅ Complete | Rust, TCP protocol, 40+ capabilities |
| **Browser Server** | ✅ Complete | browser-use, DeepSeek compatibility patch, verification detection |
| **LLM Integration** | ✅ Complete | DeepSeek API, tool calling, JSON fallback |
| **Approval System** | ✅ Complete | ApprovalManager + Fanout, multi-channel (Dashboard SSE, PC overlay, Android, Room) |
| **Manager Architecture** | ✅ Complete | TaskManager, MemoryManager, SleepManager, EventManager, AuditManager, StatusManager, NotificationManager |
| **Runtime Integration** | ✅ Complete | Single entry point, all managers wired, _build_runtime post-init fixed |
| **TaskExecutionEngine** | ✅ Complete | Approval-aware step execution, pause/resume, args hash verification, PromptRegistry/LLMSettingsResolver integration |
| **E2E Testing** | ✅ Complete | 8 lifecycle tests + 9 execution engine tests covering full approval flow, concurrent operations, all managers |

### Architecture Invariants

| Rule | Description |
|------|-------------|
| **Runtime singleton** | `AegisRuntime` is the sole entry point. External code MUST NOT create services directly. |
| **Manager pattern** | All state mutations go through Managers. Managers are owned by AegisRuntime. |
| **MemoryManager** | All memory backends accessed through `runtime.memory_manager.get_backend()`. |
| **EventManager** | All event publishing through `runtime.event_manager.publish()`. |
| **StatusManager** | All server status via `runtime.status_manager.get_snapshot()`. No `_check_port()` in routes. |
| **TaskManager** | AutonomousLoop creates/finishes tasks via TaskManager. Step-level tracking via add_step/update_step_status. |
| **TaskExecutionEngine** | Step execution, approval pause/resume, cancel/retry all through TaskExecutionEngine. InteractionRouter delegates step execution to it. |
| **AuditManager** | JSONL tail reader only. No `read_all()` in main path. |

### Key Files

| File | Purpose |
|------|---------|
| `ai-server/src/aegis_ai/runtime.py` | Process-wide singleton, builds and wires all managers |
| `ai-server/src/aegis_ai/task/task_manager.py` | 9-state task lifecycle management with step-level tracking |
| `ai-server/src/aegis_ai/task/execution_engine.py` | Approval-aware step execution engine (execute, pause, resume, cancel, retry) |
| `ai-server/src/aegis_ai/memory/memory_manager.py` | Unified memory entry point, `get_backend()` for backends |
| `ai-server/src/aegis_ai/memory/sleep.py` | SleepManager for memory consolidation |
| `ai-server/src/aegis_ai/event/event_manager.py` | Event persistence, cursor queries, dead letter |
| `ai-server/src/aegis_ai/audit/audit_manager.py` | JSONL tail reader, cursor pagination, no read_all |
| `ai-server/src/aegis_ai/status/status_manager.py` | Background health checks, cached snapshots |
| `ai-server/src/aegis_ai/notification/notification_manager.py` | Non-approval notification management |
| `ai-server/src/aegis_ai/web/manager_routes.py` | 19 Manager API routes (tasks/events/audit/status/notifications/memory/sleep) |
| `ai-server/src/aegis_ai/autonomous/autonomous_loop.py` | TaskManager integration for task lifecycle tracking |
| `ai-server/tests/test_e2e_lifecycle.py` | 8 E2E tests: approval lifecycle, concurrent tasks, all managers | |
| `ai-server/src/aegis_ai/approval/approval_manager.py` | Unified approval lifecycle manager |
| `ai-server/src/aegis_ai/approval/fanout.py` | Multi-channel approval delivery (ApprovalFanout + ApprovalChannel ABC) |
| `ai-server/src/aegis_ai/approval/channels/dashboard.py` | Dashboard SSE approval channel |
| `ai-server/src/aegis_ai/approval/channels/pc_overlay.py` | PC Server overlay approval channel |
| `ai-server/src/aegis_ai/approval/channels/android.py` | Android notification approval channel |
| `ai-server/src/aegis_ai/approval/channels/room.py` | Room Server display+TTS approval channel |
| `browser-server/src/aegis_browser/browser_use_agent.py` | browser-use with DeepSeek compatibility, verification detection |
| `browser-server/src/aegis_browser/main.py` | HTTP server for browser automation |
| `aegis_ai/event/event_manager.py` | Centralized event management with persistence and replay |
| `aegis_ai/audit/audit_manager.py` | Audit log with cursor pagination and search |
| `aegis_ai/status/status_manager.py` | Background server health monitoring |
| `aegis_ai/task/task_manager.py` | Execution unit lifecycle tracking |
| `aegis_ai/notification/notification_manager.py` | Non-approval notification management |
| `aegis_ai/memory/memory_manager.py` | Unified memory entry point across 15+ backends |
| `aegis_ai/memory/sleep.py` | Memory consolidation during idle periods |
| `aegis_ai/web/manager_routes.py` | Dashboard API routes for all Managers |
| `tests/test_e2e_lifecycle.py` | E2E lifecycle tests (approval, task, status, sleep, notification, event) |

### Servers

| Server | Language | Port | Status |
|--------|----------|------|--------|
| **AI Server** | Python 3.14 | 8090 | ✅ Running |
| **PC Server** | Rust | 50052 | ✅ Running |
| **Browser Server** | Python | 50053 | ✅ Running |

### Capability Count: 53

- pc-server: 40 capabilities
- browser-server: 1 capability (page.browse via browser-use)
- ai-server: 4 capabilities (agora, memory, search)
- android-server: 1 capability
- room-server: 1 capability

---

## Per-Server Documentation

See individual AGENTS.md files for each server:

- `ai-server/AGENTS.md` — AI Server details
- `pc-server/AGENTS.md` — PC Server details
- `browser-server/AGENTS.md` — Browser Server details
- `android-server/AGENTS.md` — Android Server details
- `room-server/AGENTS.md` — Room Server details
