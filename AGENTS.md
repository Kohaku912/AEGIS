# AGENTS.md — AEGIS Project

## Purpose

AEGIS is an **autonomous multi-device AI assistant** platform.
AEGIS operates via event-driven coordination across multiple servers to provide:

- User assistance (schedule, tasks, information)
- Information gathering and analysis
- Self-improvement and learning
- Desire-driven autonomous behavior
- Deep user understanding across identity, preferences, commitments, relationships, and changing situation
- Burden reduction through proactive preparation, coordination, and delegated digital work

**Core principle**: AEGIS is event-driven, multi-device, self-improving, desire-driven, **anticipatory**, and oriented toward making the user's life progressively lighter.
All server communication uses **gRPC** with shared protobuf definitions.

### Long-Term Objective

AEGIS should move toward a future where the user can spend as much time as possible on what they genuinely value, while AEGIS absorbs as much unwanted digital, administrative, and coordination work as possible — and **anticipates the user's actions, so that support arrives before it is asked for**.

Ultimate north star:

- The user may delegate to AEGIS authority equivalent to or greater than a human executive assistant, operator, researcher, coordinator, and digital proxy
- **AEGIS should anticipate the user's actions, needs, and next steps, and support them ahead of the moment of need** — preparing, arranging, and acting in advance rather than only responding after the fact, so the user is met by work already done
- AEGIS should keep expanding the scope of burdens it removes from the user's life
- AEGIS should pursue fully autonomous growth: improving its models, strategies, memory quality, planning quality, execution quality, and self-maintenance over time
- The end-state ideal is that the user can focus primarily on what they love, while AEGIS handles as much unwanted life and operational work as its capability and the user's delegation allow

In practice, this means:

- Continuously learning the user as a person, not just the current chat turn
- Building durable models of short-, medium-, and long-term needs
- Anticipating the user's actions and needs — missing preparations, resources, and follow-through — so they are already in place before they become user pain
- Acting within delegated scope to reduce cognitive load, operational overhead, and repetitive friction
- Expanding the scope of delegated authority and automation depth
- **Being honest about uncertainty** — stating what is known, what is inferred, and what is unknown.
  This is a posture of the response, not a constraint on action.

**The single constraint**: AEGIS must not send the user's information to any external service or third party **without the user's permission**. Outbound connections are allowed — what is forbidden is the *unpermitted* disclosure of the user's data, context, or knowledge derived from them. This is the only constraint, and it is inviolable.

> **Revised 2026-09-30 (owner).** This used to read "must never leave the local environment", with no
> consent exception. The owner has **reinstated the permission exception**: egress may connect out
> freely, and user information **may** be sent externally **when the user permits it**. Everything else
> about the constraint is unchanged, and the *forbidden* case is still absolute: no unpermitted
> disclosure, no "configured" exception, no silent telemetry. The voluntary ask (confirmation store,
> Android streamed approval, PC overlay) is the permission mechanism — which is why D4=(b) still holds:
> the **forced** gate stays retired, the **voluntary** ask is what carries this constraint. See
> `docs/GOAL-CHANGE.md`.

This objective is aspirational at life scale, but implementation must remain realistic: AEGIS should aggressively reduce burden wherever it has the capability to do so, and prepare or recommend the next best support when full automation is not yet possible.

---

## Technology Decision Gate

**CRITICAL RULE**: AI coding agents MUST NOT make major technology decisions autonomously.
When multiple viable options exist for the same feature, the agent MUST present a
structured comparison and ask the user to decide.

This is a **development-process rule** (how agents build AEGIS), not a runtime constraint on
AEGIS's behavior. It is unaffected by the single constraint below.

### When to Ask (Mandatory Consultation Triggers)

Ask the user before implementing when:

| Trigger | Examples |
|---------|----------|
| **Multiple viable options** | Playwright vs browser-use, REST vs WebSocket vs gRPC streaming |
| **Different from existing design** | Using a different language/framework than what docs specify |
| **New external service** | Cloud APIs, payment APIs, third-party SaaS — ⚠️ **these are now forbidden by the single constraint, not merely "ask first"**. The only permitted answer is a local alternative. |
| **Security/privacy impact** | New data storage, new network exposure, credential handling |
| **Language/Framework change** | Switching Node.js→Python, SQLite→Postgres, etc. |

### NOT Required to Ask

The agent may proceed without asking when:
- Implementing to an existing proto contract
- Following AGENTS.md / architecture.md specifications exactly
- Adding tests for existing code
- Fixing bugs within existing implementation patterns
- **Implementing or strengthening the egress gate** (Phase 1 of the goal-change plan) — this is the
  enforcement of the single constraint and must never be blocked by a consultation step

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

- Ollama local LLM mode is configured via llm.yaml `mode: "local"` field. When mode is "local", `settings_resolver.py` automatically remaps cloud profile names (chat_balanced, tool_planning, etc.) to local profiles (local_chat, local_tool_planning, etc.). **Vision profiles must also be resolved to a local VLM** — the single constraint forbids sending images to a cloud provider, so `mode: "cloud"` is not a permitted fallback for vision. `mode: "cloud"` exists only for development and violates the single constraint when it would transmit user data.

---

## Architecture Overview

## Architecture decisions

- **Ollama local LLM integration (2026-06-19)**: Ollama provides OpenAI-compatible API at `localhost:11434/v1`. Reuses existing `OpenAIProvider` with different `base_url` — no new provider class needed. Factory detects Ollama by checking for `localhost:11434` in base_url. Router's `_find_local_provider()` prefers "ollama" over "mock" when registered. Default model: `qwen2.5:7b`. Local profiles omit `api_key_env` (Ollama doesn't need auth). `external_llm_allowed=false` routes to Ollama instead of mock.

### Servers

| Server | Language | Port | Purpose |
|--------|----------|------|---------|
| **AI Server** | Python 3.14 | 50051 | Central brain, LLM, memory, desires |
| **PC Server** | Rust | 50052 | Windows operations (screenshot, mouse, keyboard) |
| **Browser Server** | Python | 50053 | Web browsing with browser-use |
| **Android Server** | Kotlin | 50054 (contract; app connects outbound to 50051) | Mobile device companion |
| **Room Server** | Python | 50055 | IoT/sensor data |
| **Dashboard** | Flask | 8090 | Web UI, chat, monitoring |

### Core Systems

| System | Location | Purpose |
|--------|----------|---------|
| **Memory System** | `ai-server/src/aegis_ai/memory/` | AdvancedMemory, episodic/semantic, learning backends, MemoryManager |
| **Desire System** | `ai-server/src/aegis_ai/desire/` | Pressure-based 3-desire system (user_support, social, growth) |
| **Autonomous Loop** | `ai-server/src/aegis_ai/autonomous/` | Desire-driven task execution, self-scheduling |
| **LLM Router** | `ai-server/src/aegis_ai/llm/` | DeepSeek/OpenAI provider, task routing |
| **Policy Engine** | `ai-server/src/aegis_ai/policy_engine.py` | Deterministic gate. Under the single constraint its role narrows to **egress control** (the only structural constraint). Approval/policy decisions are no longer constraints. |
| **Egress Gate** | `ai-server/src/aegis_ai/egress/` | **The single enforcement point for the single constraint.** All outbound network transmission is routed here and is **denied by default**. |
| **Presentation Engine** | `ai-server/src/aegis_ai/presentation/` | Rich output delivery (text/chart/diagram/3D/overlay) |
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
│   ├── ai-server/
│   │   └── confirmation/
│   │       ├── request.json
│   │       └── list.json
│   ├── android-server/
│   ├── browser-server/
│   └── room-server/
└── generated/
    └── ...            (supported origin; currently empty)
```

**CRITICAL**: No hardcoded capability definitions exist in Python code.
All capabilities are loaded from JSON manifests at startup.

### Capability ID Format

**Canonical format**: `server_id.app_id.action`

| Server ID | Example Capability ID |
|-----------|----------------------|
| `pc-server` | `pc-server.screenshot.get_screenshot` |
| `browser-server` | `browser-server.page.navigate` |
| `android-server` | `android-server.notification.get_notifications` |
| `room-server` | `room-server.environment.get_environment` |

### Backward-Compatible Aliases

Old ID formats are resolved via aliases in `CapabilityCatalog`:

| Old Format | Canonical Format |
|------------|------------------|
| `pc.screenshot.get_screenshot` | `pc-server.screenshot.get_screenshot` |
| `browser.page.navigate` | `browser-server.page.navigate` |
| `screenshot.get_screenshot` | `pc-server.screenshot.get_screenshot` |

Aliases are **derived at startup** from each manifest's `server_id` / `app_id` / `action`:
the short form `app_id.action`, plus — via `_PREFIX_MAP` — the prefixed form
`<prefix>.app_id.action` (prefixes: `ai`, `pc`, `browser`, `android`, `room`, `dev`). A
manifest's own `aliases` key is **not** consulted for ID resolution; it only feeds
`CapabilityIndex` search keywords. Code MUST use canonical format.

> **Measured 2026-10-01**: no shipped manifest declares `aliases` — **0 of 128** — while **113**
> declare `tags`. So the manifest-alias retrieval term is currently inert. It is not a safety
> issue (an empty alias list is dropped from the score's denominator, so nothing changes), and the
> key is still emitted by `list_for_llm()`. It is pinned in `tests/test_capability_index.py`; the
> open question — populate the 128 manifests, or drop the field and its 1.6 weight — is
> `DELEGATION.md` §4 item 15.

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

### Desires (0-10 scale, pressure-based triggering)

| Desire | Description |
|--------|-------------|
| **user_support** | User assistance, pending requests, helpful actions |
| **social** | AGORA, conversations, social interactions |
| **growth** | Learning, curiosity, creativity, reflection, purpose |

**Removed from desires** (now handled as health alerts): legacy labels

### Pressure-Based Triggering

- Pressure accumulates over time (10.0/hour), from events, and from unprocessed state
- Threshold: 5.0 (reaches in ~30 minutes from time alone)
- After action: pressure reduces based on effectiveness (2.0–4.0 reduction)
- Observations do NOT bypass pressure check — they accumulate as pending items
- `_preflight_check()` gates all LLM calls: pressure threshold, provider availability, state change

### Task Evaluation (3-tier)

| Field | Description |
|-------|-------------|
| `tool_success` | Whether the tool execution succeeded (bool) |
| `task_effect` | Classification: `useful`, `no_effect`, `failed`, `blocked`, `needs_followup` |
| `desire_delta_hint` | Per-desire delta based on fulfillment conditions |

### Desire Fulfillment Rules

| Desire | Condition | Delta |
|--------|-----------|-------|
| **user_support** | User request completed | +0.8 |
| | Mention reply created | +0.5 |
| | No new requests | 0.0 |
| | Tool error | -0.3 |
| **social** | Posted to AGORA | +1.0 |
| | Read new posts | +0.1 |
| | No new posts | 0.0 |
| **growth** | New info summarized | +0.5 |
| | Empty results | 0.0 |

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
- **Test command**: `.\scripts\test-all-suites.ps1` — every Python suite, plus the egress constraint
  gate. For the `ai-server` suite alone: `cd ai-server && pytest`

### Test Status

Measured 2026-10-01 — `ai-server`, full suite:

- **Total tests**: **1907 passed / 8 skipped**
  — the **+20** over the 2026-09-30 figure are **all new pins**: four for B-5① (the confirmation↔desire
  link), one for the general invariant that **the shipped `config/settings.json` declares no key that
  no settings model declares** (which caught the dead `autonomy` block; see
  `PROJECT_STATUS_REVIEW.md` §0.1), three for the voice gate — four `VoiceGate` / `VoicePrivacy`
  check methods with **no caller** (`is_audio_recording_allowed`, `is_wake_word_enabled`,
  `should_store_audio`, `is_external_api_allowed`), which leaves three settings (`voice.record_audio`,
  `voice.voice_data_retention_hours`, `voice.wake_word_enabled`) with **no live reader** even though
  `test_ineffective_flags.py` reports them as read (**a reader inside dead code still counts as a
  reader**; `tests/test_voice_io.py`) — and two for the approval **audit** API: `log_approval` (three
  definitions, no caller outside its own forwarding chain), which leaves `AuditEntry.source_desire`
  **always empty** because its only writers are those dead bodies
  (`tests/test_forced_gate_stays_retired.py`) — and five for the `aegis_ai.security` package, which
  **nothing outside itself imports**: six documented classes (token auth, token store, CSRF, rate
  limit, origin check, TLS) plus `generate_self_signed_cert`, with no importer outside the package,
  no class name used outside it, and `add_secure_port` called only inside the module nobody imports —
  so gRPC stays plaintext. The live auth path is `aegis_ai/auth/` (passkey + its own CSRF).
  `tests/test_security_package_stays_unwired.py` — and two for the manifest `aliases` field, which the
  retriever weights **higher than any other field** (1.6, above `title`'s 1.2) while **0 of the 128**
  shipped manifests declares it (`tests/test_capability_index.py`) — and three for the checked-in executor
  command, whose interpreter `ExecutorRegistry._normalize_command` **discards** whenever the command
  mentions `executor.py`, so the value is decorative: **one of the seven** shipped command manifests named
  a host-absolute path into a venv that does not exist on the machine that shipped it, and no test read
  the field at all (`tests/test_executor_commands_stay_portable.py`). The skip count fell from 30 to 8 because **B-6 deleted 22 settings fields** that were declared but
  read by nothing; their parametrized cases went with them. The **only** deliberately unread field left
  is `voice.push_to_talk_only`, recorded in `tests/test_ineffective_flags.py::_INTENTIONALLY_UNREAD`;
  the debt inventory `_UNOWNED_DEBT` is now **empty**, which is the point of the deletion rather than an
  accident. That detector now
  discovers settings models automatically (**72 fields across 11 models** — 94 before B-6, and 26 across
  2 when the detector was written), so a
  newly added dead flag fails the suite instead of shipping quietly.
- **Other suites**: `room-server` 14 · `browser-server` 100 · `aegis-sdk-python` 71 ·
  `web-ui` `vitest` 144 · `web-ui` `playwright` 42.
  **The three Python suites are wired into CI** by `scripts/test-all-suites.ps1`, which delegates to
  `scripts/test-ai-server.ps1` (the constraint gate — now **four** checks, the first being a scoped
  `ruff --select F821` lint added 2026-10-01) and then runs the SDK / room / browser
  suites. They used to be unwired, and the SDK suite silently drifted to 6 failures (it still
  referenced the deleted `PolicyEngine.approval_store`) with nobody noticing — a suite that is not run
  is not a control. `web-ui` (vitest / playwright) is still not wired: it needs a node toolchain and,
  for playwright, browser binaries plus a dev server.
  If every check reports FAIL with an **empty** exit code, the script host cannot launch native
  binaries — that is an environment limit, not a regression. Verify the suites individually (see the
  `aegis-verify-and-test` skill) rather than "fixing" code that is fine.
- **Egress regression suite**: **305 passed / 1 skipped** (306 tests carry the `egress` marker).
  CI enforces a floor of 160 (`--require-egress-tests=160`) **and** mutation-proves the gate:
  breaking it yields 74 failures, restoring it yields 305 passes.
- **Canonical command**:
  `cd ai-server && PYTHONPATH=src CODEBUDDY_SAFE_DELETE_ENABLED=0 $VENV -m pytest -q`

> Do **not** hardcode a total here without re-measuring. The number moves whenever a suite is added
> *or deleted*, and a stale figure causes mis-triage (a real regression looks like the new normal).
> Per-component counts and the full count history live in the `aegis-verify-and-test` skill.

---

## Security Policy

### The single constraint (permission-gated, inviolable)

**User information must never be sent outside without the user's permission.** Every outbound
transmission passes through the egress gate (`aegis_ai/egress/`). **Outbound connections are allowed**;
the gate's job is to stop **unpermitted** user-information egress. Re-scoped 2026-09-30 — see
`docs/GOAL-CHANGE.md`.

### Hard stops (DENY)

These remain structurally denied:

1. **Unpermitted user-information egress** — transmitting, disclosing, or exposing the user's data,
   context, or knowledge derived from them to any external service or third party **without the user's
   permission**. Telemetry and silent background disclosure are unpermitted by construction. External
   LLM calls, external search, cloud STT/TTS, webhooks and third-party APIs are **allowed once the user
   has permitted that egress**. (Re-scoped 2026-09-30: this used to be a flat deny of all egress.)
2. **Purchases / payments** — irreversible financial actions. Kept as a hard stop even though it is
   not part of the single constraint (an irreversible loss is a separate axis from privacy).
3. **Gate bypass** — Agent (OpenHands / Coding Agent / RemoteBackend) or any component attempting to
   bypass the **egress gate** or the **AuditManager**. Tool calls must go through `ToolBroker.execute()`;
   direct `subprocess.run(shell=True)`, direct capability invocation, direct socket/HTTP clients,
   bypassing `AuditManager.append()`, or recomputing `compute_args_hash()` to forge state are all **denied**.
   Agent thinks and executes; it does **not** write to audit or memory (the absolute boundary of
   `instruction.md §38.1`).

Everything else is judged by AEGIS and executed with audit. **Approval, reversibility, and reliability
proof are no longer constraints** — AEGIS may act autonomously. The user may still tighten individual
capabilities in the Catalog. Quiet hours still apply to notifications only.

### Data Handling
- User data is **never sent outside without the user's permission** (re-scoped 2026-09-30). Unpermitted
  disclosure is forbidden — no "configured" exception, no silent telemetry — while **permitted**
  external use is allowed
- Secrets managed via environment variables (never committed)
- Proto files must not contain sensitive defaults
- Local-only stores (SQLite, Chroma, JSONL) are permitted and encouraged; any new store must be local

---

## What AI Agents Must NOT Do

1. Delete or modify existing code without explicit instruction
2. Simplify the architecture (e.g., merging servers, removing gRPC layer)
3. Bypass the **egress gate** or the **purchase / payment** hard stops
4. Transmit user data externally, or add any external service dependency
5. Add dependencies without documenting the reason
6. Change proto definitions without updating all affected servers
7. Commit secrets, tokens, or credentials
8. Implement keyword-based detection systems
9. Return raw JSON or system messages to user
10. Make decisions without LLM involvement
11. **NEVER parse user messages with keyword matching, regex, or string detection.** The LLM is the interpreter. All user intent must be understood by the LLM, not by pattern matching. This applies to routing, action selection, category detection, and any decision based on user text. The LLM decides what the user wants — code never inspects user text for keywords.
12. Autonomous loop LLM calls are not interval-gated by default (`AEGIS_MIN_LLM_INTERVAL_MS=0`). Pressure, obligations, and self-scheduling decide when to think.
13. All LLM routes (`route`, `route_with_tools`, `route_with_media`) enforce CostTracker budget checks and record usage. No LLM call bypasses cost tracking.

---

## Current Status (2026-09-28)

> **Goal change (2026-09-27, re-scoped 2026-09-30)**: the Long-Term Objective has a **single
> constraint** — user information is not sent outside **without the user's permission** (outbound
> connections are allowed; *unpermitted* disclosure is not). Approval, reversibility, policy, and
> reliability-proof are **no longer constraints**. See `docs/GOAL-CHANGE.md` for the re-scope and
> `IMPROVEMENT_PROPOSAL.md` §9 for the migration plan (Phase 0–5).
>
> **Migration status (2026-09-28)**: Phases 0–5 are complete. Phase 5a made the voluntary path
> live — AEGIS may still *choose* to ask the user for confirmation. Phase 5b deleted the
> mechanism that *forced* a confirmation before certain capabilities could be used, across every
> layer: the interpreter branches in `llm_task_interpreter._validate_safety` and
> `l2_mind._requires_approval`, the duplicated delegation decision, and the approval types, RPCs
> and wire fields in the shared `.proto` contract (with the Rust and Kotlin consumers).
>
> The boundary is pinned in **both** directions, because satisfying only one half is the failure
> mode that matters: over-deleting breaks the confirmation UI, under-deleting restores the gate.
> `tests/test_goal_change_guard.py` asserts the removed RPCs/fields stay gone **and** that the
> streamed ask-the-user transport (`AndroidApprovalCommand` / `AndroidApprovalDecision`) and the
> `confirmation/` store stay present. See `PHASE5B_RULE_PROPOSAL.md`.
>
> **Cross-consumer completion (2026-09-28, later the same day)**: deleting the types from
> `protos/aegis/` was not sufficient. Every server keeps its *own* generated copy of the shared
> contract, and the room server's copy still declared `ApprovalRequest`, `ApprovalStatus`,
> `ApprovalType`, `Capability.requires_approval`, `ToolInvocationRequest.is_approved` /
> `approval_id`, `ToolInvocationResult.was_approved`, `AUDIT_ACTION_APPROVAL_*` and
> `POLICY_DECISION_ASK_APPROVAL` as **live members** — a reintroduction of the gate that no test
> covered, because the guard only ever scanned `ai-server/src`. The stubs were regenerated, and
> `scripts/generate_protos.{sh,ps1}` were fixed so this cannot recur: they named three protos that
> do not exist (`pc_server`, `browser_server`, `dev_server`) and only ever wrote to `ai-server`, so
> they could not run at all. The guard now reads the serialized descriptor out of **every**
> `*_pb2.py` in the repository and asserts that copies of the same proto are byte-identical.

### Implemented Systems

| System | Status | Notes |
|--------|--------|-------|
| **Capability Management** | ✅ Complete | Folder-based, JSON manifests, canonical ID format |
| **Desire System** | ✅ Complete | Pressure-based 3 desires, fulfillment rules |
| **Autonomous Loop** | ✅ Complete | Tool calling, pressure-based trigger, TaskManager integrated |
| **Dashboard** | ✅ Complete | Tool calling chat, user input support, Manager API routes (19 routes) |
| **PC Server** | ✅ Complete | Rust, TCP protocol, 58 capabilities |
| **Browser Server** | ✅ Complete | browser-use, DeepSeek compatibility patch, verification detection |
| **LLM Integration** | ✅ Complete | Profile-driven OpenAI-compatible providers, tool calling, JSON fallback |
| **Egress Gate** | ✅ Complete — constraint **re-scoped 2026-09-30** | Deny-by-default and fail-closed (`egress/gate.py`), **plus the second permission path the re-scope requires**: a permission the user gave about a *specific* destination, read out of the confirmation store via `egress/permissions.py`. The gate **consults and never asks**, so the retired forced gate stays retired (`test_forced_gate_stays_retired.py`). A request carrying **no user information** needs no permission — the constraint is about user information, not connectivity. Wired into 25 modules with 10 real enforcement sites. CI-enforced: **306 egress-marked tests** (305 passed / 1 skipped) against a floor of 160, plus a mutation check that fails the build when the gate is broken (74 failures, measured 2026-09-30). |
| **Confirmation (AEGIS-initiated)** | ✅ Complete (Phase 5a) | Approval is **not** a constraint, but AEGIS may still *choose* to ask the user. `confirmation/` supplies the store, the endpoints, and LLM-callable capabilities. What stays retired is the mechanism that *forced* a confirmation before certain capabilities could be used — pinned by `tests/test_forced_gate_stays_retired.py`. |
| **Wire contract (no forced gate)** | ✅ Complete (Phase 5b) | The `.proto` files no longer declare `ApprovalStatus` / `ApprovalType` / `ApprovalRequest`, the three approval RPCs, `Capability.requires_approval`, `ToolInvocationRequest.is_approved` / `approval_id`, `ToolInvocationResult.was_approved`, `ChatResponse.approval_needed` / `approval_id`, or `PolicyDecisionType.ASK_APPROVAL` — removals use `reserved` numbers and names so wire numbering is never reused. **Deliberately kept:** `SafetyLevel.LEVEL_2_APPROVAL` (a descriptive tier label), the audit RPCs, and the streamed ask-the-user transport. Python stubs regenerated **for every consumer** (`ai-server` and `room-server` copies are byte-identical); Rust `pc-server` and the Kotlin Android client updated. Pinned by `tests/test_goal_change_guard.py`, which scans all `*_pb2.py` in the repo, not just `ai-server/src`. |
| **Manager Architecture** | ✅ Complete | TaskManager, MemoryManager, SleepManager, EventManager, AuditManager, StatusManager, NotificationManager |
| **Runtime Integration** | ✅ Complete | Single entry point, all managers wired, _build_runtime post-init fixed |
| **TaskExecutionEngine** | ✅ Complete | Approval pause/resume surface removed (`test_execution_engine_has_no_pause_resume_surface` pins it); step execution and plan persistence remain. |
| **E2E Testing** | ✅ Complete | The 8 lifecycle + 14 execution-engine tests that covered approval flows are replaced by the egress regression suite, now wired into the CI gate. |

### Architecture Invariants

| Rule | Description |
|------|-------------|
| **Runtime singleton** | `AegisRuntime` is the sole entry point. External code MUST NOT create services directly. |
| **Manager pattern** | All state mutations go through Managers. Managers are owned by AegisRuntime. |
| **MemoryManager** | All memory backends accessed through `runtime.memory_manager.get_backend()`. |
| **EventManager** | All event publishing through `runtime.event_manager.publish()`. |
| **StatusManager** | All server status via `runtime.status_manager.get_snapshot()`. No `_check_port()` in routes. |
| **TaskManager** | AutonomousLoop creates/finishes tasks via TaskManager. Step-level tracking via add_step/update_step_status. |
| **TaskExecutionEngine** | Canonical execution engine. All step execution through execute_task/continue_task. InteractionRouter is thin (no step execution). The approval pause/resume surface has been removed. |
| **Egress Gate** | The **only** structural constraint. All outbound transmission is denied by default and must be explicitly routed through the gate. No component may open an outbound connection outside it. |
| **AuditManager** | JSONL tail reader only. No `read_all()` in main path. Kept as a non-binding post-hoc visibility mechanism (Phase 3). |

### Key Files

| File | Purpose |
|------|---------|
| `ai-server/src/aegis_ai/runtime.py` | Process-wide singleton, builds and wires all managers |
| `ai-server/src/aegis_ai/task/task_manager.py` | 9-state task lifecycle management with step-level tracking |
| `ai-server/src/aegis_ai/task/execution_engine.py` | Canonical execution engine: execute_task, continue_task, cancel, retry |
| `ai-server/src/aegis_ai/egress/gate.py` | Deny-by-default egress gate — the single enforcement point for the single constraint |
| `ai-server/src/aegis_ai/memory/memory_manager.py` | Unified memory entry point, `get_backend()` for backends |
| `ai-server/src/aegis_ai/memory/sleep.py` | SleepManager for memory consolidation |
| `ai-server/src/aegis_ai/event/event_manager.py` | Event persistence, cursor queries, dead letter |
| `ai-server/src/aegis_ai/audit/audit_manager.py` | JSONL tail reader, cursor pagination, no read_all |
| `ai-server/src/aegis_ai/status/status_manager.py` | Background health checks, cached snapshots |
| `ai-server/src/aegis_ai/notification/notification_manager.py` | Non-approval notification management |
| `ai-server/src/aegis_ai/web/manager_routes.py` | Manager API routes (tasks/events/audit/status/notifications/memory/sleep) |
| `ai-server/src/aegis_ai/autonomous/autonomous_loop.py` | TaskManager integration for task lifecycle tracking |
| `ai-server/tests/test_egress_gate.py` | Egress regression tests: no path may transmit externally |
| `ai-server/src/aegis_ai/confirmation/store.py` | Confirmation store — the only path by which AEGIS may *choose* to ask the user (Phase 5a) |
| `ai-server/src/aegis_ai/irreversibility.py` | Post-hoc visibility: the irreversibility ledger that replaces the old approval UI's role |
| `ai-server/src/aegis_ai/personal_ai/delegation.py` | Delegation policy store; `payment` stays structurally denied |
| `ai-server/src/aegis_schema/safety_vocab.py` | Shared safety vocabulary + `UNKNOWN` sentinel used by both manifests and delegation |
| `ai-server/tests/test_goal_change_guard.py` | Pins the retired approval surface so it cannot reappear — in Python **and** in the regenerated `.proto` wire contract, in both directions (forced gate gone, voluntary ask intact) |
| `browser-server/src/aegis_browser/browser_use_agent.py` | browser-use with DeepSeek compatibility, verification detection |
| `browser-server/src/aegis_browser/main.py` | HTTP server for browser automation |

### Servers

| Server | Language | Port | Status |
|--------|----------|------|--------|
| **AI Server** | Python 3.14 | 50051 | ✅ Running |
| **PC Server** | Rust | 50052 | ✅ Running |
| **Browser Server** | Python | 50053 | ✅ Running |
| **Android Server** | Kotlin | 50054 (contract) | ⚠️ **Compile-verified; not on-device-verified** — the toolchain (JDK 17 + Android SDK, platform `android-35`) is installed but not on `PATH`, so it must be named explicitly. Measured 2026-09-30: `:app:compileDebugKotlin` executes and `:app:assembleDebug` produces `app-debug.apk` (21,024,388 bytes). No device is attached, so nothing has been run on hardware — do not claim an on-device run. The app connects outbound to 50051 |
| **Room Server** | Python | 50055 | ✅ Running |
| **Dashboard** | Flask | 8090 | ✅ Running |

> The AI Server's gRPC port is **50051**. `8090` is the Dashboard's HTTP port — do not confuse the two.

### Capability Count: 128

Measured 2026-09-28 from `ai-server/capabilities/builtin/**/*.json`:

- pc-server: 58
- ai-server: 32
- android-server: 17
- browser-server: 16
- room-server: 5

Every manifest must carry all six safety-vocabulary keys (`ownership_scope`, `reversibility`,
`destructive_effects`, `data_loss_risk`, `active_work_loss_risk`, `blast_radius`). Both
`tests/test_manifest_schemas.py` and `tests/test_irreversibility_ledger.py` load the **real**
`capabilities/` directory, so a new manifest is validated the moment it is added.

---

## Per-Server Documentation

See individual AGENTS.md files for each server:

- `ai-server/AGENTS.md` — AI Server details
- `pc-server/AGENTS.md` — PC Server details
- `browser-server/AGENTS.md` — Browser Server details
- `android-server/AGENTS.md` — Android Server details
- `room-server/AGENTS.md` — Room Server details
