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

- LLM mode is configured via the `mode` field of `llm.yaml`. In `mode: "local"`, `settings_resolver.py` remaps cloud profile names (chat_balanced, tool_planning, etc.) to local profiles (local_chat, local_tool_planning, etc.), and **vision profiles must also resolve to a local VLM**. The shipped file is **`mode: "cloud"`** so that `l1_default` actually reaches TypeSafe JEV — in local mode the remap sends L1 to Ollama and the JEV declaration is dead (measured 2026-10-02: the file said `provider: typesafe` while every call ran on `qwen2.5:3b`). What keeps that safe is **not** the mode but the **allowlist**: `privacy.egress_allowed_hosts` names `api.typesafe.ai` and nothing else, so every other declared cloud destination is denied by the gate and degrades to Mock. (Before the 2026-09-30 re-scope *any* external transmission was forbidden, which made `mode: "cloud"` a violation in itself; the constraint is now **permission**-gated — `docs/GOAL-CHANGE.md`.)

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
| **Dashboard** | `ai-server/src/aegis_ai/web/` | Flask UI with chat |

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

- **Chat with tool calling**: `POST /api/chat/send` (plain JSON). The `GET /api/chat/events` SSE route is registered but **dead on both ends** (measured 2026-10-03) — **no producer publishes to it** (nothing calls `put` anywhere in `dashboard_legacy.py`) and **no client subscribes** (the path occurs in exactly one file, its own definition). Pinned by `ai-server/tests/test_chat_sse_route_stays_dead.py`; wiring or deleting it is `DELEGATION.md` §4 item 23
- **Memory integration**: AdvancedMemory context in LLM prompts
- **Desire context**: Current desire states in LLM prompts
- **Tool calling**: Chat uses CapabilityCatalog for capability execution
- **Settings management**: All settings changes persist to `config/settings.json`

### Agentic Tool Calling Loop

The chat system supports **recursive multi-step tool calling** (up to **15** rounds — the `call_llm_with_tools` default; `LLMSettings.max_tool_rounds = 5` is displayed in the settings UI but never passed by a caller):

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

> **Re-measured 2026-10-02: `1942 passed / 8 skipped`.** The +16 over the record below is +2
> (S-1①, the passkey route-coverage invariant), +6 (M-2, the ineffective-flag detector's fourth
> layer over `aegis_ai/config.py`) and +4 (S-2, the display-access consolidation). **The remaining
> +4 landed after 2026-10-01 and is *not attributed*** — the count-history table in the
> `aegis-verify-and-test` skill carries the same gap. Egress is now **311 passed / 1 skipped**
> (312 carry the marker, 1647 deselected), not 305.
>
> **Re-measured again 2026-10-02 (E-2 + S-4): `1951 passed / 8 skipped`** (1959 collected). The +9
> over the 1942 above is **+3 (E-3's pin, which landed in the same session *after* the 1942 figure was
> taken — so that figure was already stale), +3 (E-2's pin) and +3 (S-4's pin)**. The +4 gap noted
> above is **untouched and still unattributed**. ⚠️ This is a **chunked sum, not one invocation**: a
> single full-suite `pytest` here dies partway (**rc=127**, observed at 36% and 44% after ~3–4 min),
> so the suite was run as 6 chunks whose totals equalled their collected counts exactly.
>
> **Re-measured 2026-10-03: `1984 passed / 8 skipped`** (1992 collected, 439.95 s; the canonical
> marker-excluded form is 1984 / 4 skipped / 4 deselected).
> The +9 over the 1951 above is **+3 (`f8e0b06`, the JEV re-scope: 21 pins rewritten + 2 new gate tests)
> and +6 (`31e4066`, the JEV provider fixes: `detail` in the error text, `timeout_seconds` threaded
> through the factory, the inert generation parameters documented, a success log).** Egress is now
> **314 passed / 1 skipped** (315 carry the marker, **1677** deselected) — only `f8e0b06` added egress
> tests; the **30** added since carry no marker (`1992 collected − 1962 collected` at `f8e0b06`, or
> `1677 − 1647` deselected — the figure read **18** until 2026-10-03, which had been true only while
> the total was 1972: the later edits moved the passed/deselected numbers and left this derived one
> behind, the same "only one of the copies moved" shape).
>
> The **+5** on top of 1960 is `tests/test_egress_grant_source_is_unwired.py` — the recorded-grant
> path (`ConfirmationGrantSource`) is implemented and consulted on every `check()`, but no `src/`
> module constructs one and the composition root passes no `permission_source`, so it is **inert in
> the running system** (`DELEGATION.md` §4 item 22, `PROJECT_STATUS_REVIEW.md` §3.2). A further
> **+5** is `tests/test_chat_sse_route_stays_dead.py` — `GET /api/chat/events` is dead on **both**
> ends, which is two independent facts (`DELEGATION.md` §4 item 23). And **+2** is
> `tests/test_documented_routes_are_registered.py` — the route tables in `docs/approval-ui.md`
> and `docs/feature-catalog.md` must name routes the app actually registers. And **+5** then **+1** is
> `tests/test_e2e_compose_services_exist.py` — every service and profile a script names to
> `docker compose` must be defined by a compose file, with `dev-server` and `--profile dev`
> recorded as the only exceptions. The pin was written `.ps1`-only and **had the very defect it
> exists to catch**: `scripts/ubuntu/*.sh` invokes compose too, so widening the walk added 7
> invocations and 5 service names (`DELEGATION.md` §4 item 17 (2)).
>
> **Re-measured 2026-10-03 (the audit-JSONL pin): `1992 passed / 8 skipped`** (2000 collected,
> 427.30 s; the canonical marker-excluded form is 1992 / 4 skipped / 4 deselected). The **+8** is
> `tests/test_audit_jsonl_has_no_writer.py` — `data/audit.jsonl` has **four readers and no writer**,
> because `aegis_ai/audit.py` (a module whose `AuditLog` writes JSONL) and `aegis_ai/audit/` (a
> package whose `AuditLog` writes SQLite) are **the same import name** and **the package wins**
> (measured with `find_spec`, not reasoned), so `runtime.py`'s `AuditLog(path=…/audit.jsonl)`
> actually opens `data/audit.db` (`DELEGATION.md` §4 item 25). Egress is **314 passed / 1 skipped**
> (315 carry the marker, **1685** deselected — the markers are unchanged; the +8 non-egress tests
> moved the deselected count). The **derived** "added since carry no marker" figure is now **38**
> (`2000 − 1962` collected, or `1685 − 1647` deselected); it read **30** in the note above, which was
> correct for that measurement — write the arithmetic beside a derived number or it rots silently.
>
> **Re-measured 2026-10-03 (the presentation-stream pin): `1997 passed / 8 skipped`** (2005 collected,
> 499.73 s; the canonical marker-excluded form is 1997 / 4 skipped / 4 deselected). The **+5** is
> `tests/test_presentation_stream_is_sound.py` (written as `..._leaks_a_subscriber.py`; **renamed
> 2026-10-03** when the leak was fixed and the pin was inverted to assert the fix) — `GET /api/presentations/stream` calls
> `event_manager.subscribe(_on_event)` at **route-function scope**, i.e. once per request *before* the
> generator starts, and **discards the returned id**, so every request retains one subscriber for ever;
> there is no `unsubscribe` in the module and the queue is **unbounded**. Measured by *driving the
> route*, not reading it: **1 subscriber after the route runs, still 1 after the client disconnects** —
> where the sibling `routes/ui.py`, which keeps the id and releases it in a `finally`, measures **1 → 0**.
> Latent today (no client subscribes), but it fires on the **first** connection (`DELEGATION.md` §4
> item 26). Egress is **unchanged at 314 passed / 1 skipped** (315 carry the marker, **1690**
> deselected — the +5 non-egress tests moved the deselected count). The **derived** "added since carry
> no marker" figure is now **43** (`2005 − 1962` collected, or `1690 − 1647` deselected). ⚠️ **Both
> defects were fixed the same day** — see the *presentation-stream fix* paragraph below. The pin was **renamed**
> `test_presentation_stream_is_sound.py` and now carries **7** tests (it asserts the fix instead of
> pinning the leak).
>
> **Re-measured 2026-10-03 (the memory-registry pin): `2011 passed / 8 skipped`** (2019 collected,
> 538.07 s; the canonical marker-excluded form is 2011 / 4 skipped / 4 deselected). The **+14** is
> `tests/test_memory_backend_registries_agree.py` (**7 functions, 7 parametrized**) — `MemoryManager`
> names its backends **three** times and no two agree: the `get_backend()` docstring lists **11**, its
> mapping **10**, and `get_stats()` **7**. The docstring advertises `association`, which the mapping
> lacks, so `get_backend("association")` returns `None` — and `AssociationMemory` is real and **live**,
> just registered on the *runtime* rather than the manager. `get_stats()` drops `person` and
> `action_trace`, **both of which define `get_stats`**, so the live `GET /api/memory/stats`
> (`manager_routes.py:361`) silently reports 7 of 10 (`store` is legitimately absent — `MemoryStore` has
> no `get_stats`). `DELEGATION.md` §4 item 27. Egress is **unchanged at 314 passed / 1 skipped** (315
> carry the marker, **1704** deselected). The **derived** "added since carry no marker" figure is now
> **57** (`2019 − 1962` collected, or `1704 − 1647` deselected). ⚠️ **Fixed the same day** — see the
> *memory-registry fix* paragraph below; the pin now asserts the *agreement* (**9** functions / **17** cases).
>
> **Re-measured 2026-10-03 (the shadowed-route pin): `2017 passed / 8 skipped`** (2025 collected,
> 488.49 s; the canonical marker-excluded form is 2017 / 4 skipped / 4 deselected). The **+6** is
> `tests/test_no_route_is_shadowed.py` — the app registers **192 rules**, and **two `(method, path)`
> pairs are registered twice**, so the second handler can never run. Measured by driving the adapter,
> not by reading the file: of **186 endpoints**, **exactly two** are unreachable —
> `GET /api/servers` resolves to `dashboard_server_status.api_servers` and leaves **`api_servers`
> (`dashboard_legacy.py:1159`)** dead; `POST /api/memory/reload` resolves to
> `dashboard_memory.memory_reload` and leaves **`api_memory_reload` (`dashboard_legacy.py:1372`)** dead.
> Both losers are **legacy closures** left behind by the blueprint migration. `DELEGATION.md` §4 item 28.
> This also corrects a stale number: §3.2's "**98** unreferenced pairs" is the **multiplicity** count —
> the distinct count is **200** pairs and the unreferenced set is **96**, because the two shadowed pairs
> are unreferenced *and* registered twice. Egress is **unchanged at 314 passed / 1 skipped** (315 carry
> the marker, **1710** deselected). The **derived** "added since carry no marker" figure is now **63**
> (`2025 − 1962` collected, or `1710 − 1647` deselected). ⚠️ **Both legacy copies were deleted the
> same day** — see the *shadow deletion* paragraph below; the rule count fell **192 → 190** and the
> multiplicity count **converged on** the distinct one (**98 → 96**).
>
> **Re-measured 2026-10-03 (the owner's decisions executed — the retired gate package deleted, the
> burden metric defined, a leftover var removed): `2019 passed / 8 skipped`** (2027 collected, 473.55 s).
> The **+2** is **measured, and the arithmetic is +15 − 8 − 4 − 1**: **+15** = the new burden pin's cases;
> **−8** = `test_forced_gate_stays_retired.py` **53 → 45** (three *parametrized* positives replaced by one
> "the package is gone ∧ unreferenced" pin); **−4** = `test_goal_alignment.py` **20 → 16**; **−1** =
> `test_mission_contract_acceptance.py` **16 → 15**. ⚠️ **An estimate of "+8" was wrong, and the error is
> the lesson**: it read the three replaced tests as three *cases*; collection says they were **nine** —
> **a `def` count is not a case count, and only collection settles it**. The deletion removed a
> **package**, not coverage: the replaced pin is *stronger* (two independent facts). Egress is
> **unchanged at 314 passed / 1 skipped** (315 carry the marker, **1712** deselected). The **derived**
> "added since carry no marker" figure is now **65** (`2027 − 1962` collected, or `1712 − 1647` deselected).
>
> **Re-measured 2026-10-03 (the presentation-stream fix — the leak *and* the arity defect):
> `2021 passed / 8 skipped`** (2029 collected, 464.32 s; the canonical marker-excluded form is
> 2021 / 4 skipped / 4 deselected — `android_local` is the marker it drops, and it carries exactly 4
> tests). The **+2** is the same pin going **5 → 7** tests, because the fix **inverted** it: it now
> asserts the correct shape instead of pinning the leak. The change moved `subscribe` **inside** the
> generator, keeps the returned id and releases it in a `finally`, bounds the queue at
> `maxsize = _PRESENTATION_QUEUE_SIZE = 200` (the shape `routes/ui.py` already used), and rewrites the
> handler to take **one** argument. ⚠️ **The second defect is why reading the body mattered**:
> `_on_event(event_type, payload_json)` took **two** arguments, but `EventBus._notify_subscribers` calls
> `sub.handler(event)` with **one** (`event_bus.py:241`) and routes a raise to `_dead_letter_handler`
> (`:243-246`) — so the handler **never ran at all**, silently, while the subscriber count still looked
> right. **Fixing the leak alone would have left the route delivering nothing; fixing the handler alone
> would have left it leaking** — the concrete proof that *live / subscribed / sound* are three axes, not
> one count (`DELEGATION.md` §4 item 26). Mutation-proved **8/8** with a control run; originals restored
> byte-identically. Egress is **unchanged at 314 passed / 1 skipped** (315 carry the marker, **1714**
> deselected). The **derived** "added since carry no marker" figure is now **67**
> (`2029 − 1962` collected, or `1714 − 1647` deselected).
>
> **Re-measured 2026-10-03 (the memory-registry fix — the live route stops under-reporting):
> `2024 passed / 8 skipped`** (2032 collected, 441.95 s; the canonical marker-excluded form is
> 2024 / 4 skipped / 4 deselected). The **+3** is that same pin going **14 → 17** cases, because the
> fix **inverted** it: it now asserts the three registries **agree** instead of pinning that they
> disagree. `MemoryManager.get_stats()` gained `person` and `action_trace` — both define `get_stats`,
> while `store` is the one *justified* omission (`MemoryStore` defines none) — and the
> `get_backend()` docstring dropped the ghost `association` (the manager does not own that backend;
> the **runtime** does, which is why `get_backend("association")` always returned `None`). So the
> live `GET /api/memory/stats` now reports **9, not 7**. ⚠️ **The pin's own weakness was found by
> mutation, not by review**: the "the runtime constructs the ghost class" check was a **substring**
> test, so a mutation that *commented the construction out* left it green — **a mention in a string
> literal is not an invocation** (the same lesson as the event-driven core's `__main__` demo). It is
> now an `ast.Call` check, and the commented-out form is mutation **M8b**. Mutation-proved **12/12**
> with a control run; four originals restored byte-identically (`DELEGATION.md` §4 item 27). Egress
> is **unchanged at 314 passed / 1 skipped** (315 carry the marker, **1717** deselected). The
> **derived** "added since carry no marker" figure is now **70** (`2032 − 1962` collected, or
> `1717 − 1647` deselected).
>
> **Re-measured 2026-10-03 (the shadow deletion — the two legacy copies are gone): `2024 passed /
> 8 skipped`** (2032 collected, 439.40 s; the canonical marker-excluded form is 2024 / 4 skipped /
> 4 deselected). ⚠️ **The total did not move** — the pin was **rewritten but not resized** (**6 → 6**
> cases), so this paragraph carries the same numbers as the one above. The prediction here was
> `+3`; the measurement says **+0**, which is the reason the figure is written from a run rather
> than from the size of the change. What moved instead is the *route surface*: `dashboard_legacy.py`
> no longer registers the two closure handlers that the `dashboard_server_status` and
> `dashboard_memory` blueprints had been **shadowing** (Werkzeug matches the first rule for a path),
> so the registered rules fell **192 → 190** and the multiplicity count **converged on** the distinct
> one — **202 pairs / 200 distinct → 200 / 200**, i.e. **no pair is registered twice**. The §3.2
> "unreferenced **98**" was that multiplicity artefact: the two shadowed pairs were unreferenced *and*
> counted twice, so the honest figure is **96** (**96 + 2 = 98**), and the literal-only variant moved
> **127 → 125** (breakdown unchanged: GET 56 / POST 35 / DELETE 3 / PATCH 2). The two paths are still
> served — the blueprints were always the winners — and `_get_server_status` / `_load_memory_snapshot`
> were **kept** (the winning blueprints call them). The pin is **inverted** to assert the invariant
> (*no* shadow) instead of pinning the two unreachable handlers; mutation-proved **5/5** (M1 a *new*
> shadow, M2 the original closure re-added, M3 a readiness route re-pointed at `/api/servers`, M4 the
> **winner** deleted, M5 a legacy `def` renamed back) with a control run, and both originals restored
> byte-identically (`DELEGATION.md` §4 item 28). ⚠️ **Side finding, recorded not fixed**: the deleted
> closure was the **only** reader of `chroma_available` and the **only** caller of
> `ChromaSemanticMemory.sync_from_advanced_memory` (defined once at `chroma_semantic.py:163`, now
> called nowhere), and the surviving `POST /api/memory/reload` returns `"chroma_synced": 0` as a
> **literal** — the only other mention of that key is a test asserting its *presence*, not its value.
> The chain is dead end to end: `ChromaSemanticMemory` is constructed **only** at `factory.py:38`, and
> that `create_semantic_memory` has **no caller** either (its sole mention is the module docstring's
> `Usage:` example — a string literal), while the live path builds plain `SemanticMemory` directly at
> `runtime.py:1020`. So `chroma_available` is not merely unread, it is **not even produced** on the
> live path. ⚠️ **Wiring it is not free**: the class embeds through `OpenAIEmbeddingFunction`
> (`OPENAI_API_KEY`, default `text-embedding-3-small`), so it would put **memory content** on the wire
> — the single constraint's subject matter, which the *voluntary ask* must carry, not a settings flag.
> Recorded as a new register row rather than fixed. Egress is
> **unchanged at 314 passed / 1 skipped** (315 carry the marker, **1717** deselected). The **derived**
> "added since carry no marker" figure is **70** (`2032 − 1962` collected, or `1717 − 1647` deselected).
>
> **Re-measured 2026-10-03 (the dead Chroma vector path, and the `SemanticMemory` name collision):
> `2035 passed / 8 skipped`** (2043 collected, 423.59 s; the canonical marker-excluded form is
> 2035 / 4 skipped / 4 deselected). The **+11** is the new pin's 11 test functions, exactly; **no
> production code changed**. What the pin records is a chain that is dead **end to end**: the deleted
> legacy closure (`DELEGATION.md` §4 item 28) was the last link, so `create_semantic_memory` has **no
> caller** (its only other mention is the module docstring's `Usage:` example — a string literal, the
> same shape as the event-driven core's demo), `ChromaSemanticMemory` is constructed **only** inside
> that function, `sync_from_advanced_memory` therefore has **no caller**, and `chroma_available` has
> **no reader** — and is not even *produced*, because the live path builds plain `SemanticMemory`
> directly (`runtime.py:1020`). The live `POST /api/memory/reload` answers `"chroma_synced": 0` as a
> **literal** (pinned as an `ast.Constant`, not a call). ⚠️ **Wiring it is not a free cleanup**: the
> class embeds through `OpenAIEmbeddingFunction` (`OPENAI_API_KEY`, default `text-embedding-3-small`),
> so it would put **memory content** on the wire — the single constraint's subject matter, which the
> *voluntary ask* must carry rather than a settings flag. The same pin fixes a second, entangled
> defect: **two unrelated classes are named `SemanticMemory`** (`memory/semantic.py` — 70 lines, 6
> methods, no `get_stats`; and `memory/semantic_memory.py` — 257 lines, 15 methods, the **live**
> backend). The runtime and `memory_context` name the second explicitly, but the **package root
> re-exports the first**, so `from aegis_ai.memory import SemanticMemory` hands out the 6-method
> class — a **latent trap**, not a live bug, because nothing imports it that way yet (measured: 0 in
> `src/` and `tests/`). ⚠️ **The first mutation run had a SURVIVOR, and it was a bad mutation rather
> than a weak pin**: the embedding assertion requires **both** markers, so replacing only
> `OpenAIEmbeddingFunction` left `OPENAI_API_KEY` in place and the claim still held. Removing **both**
> caught it. Final **11/11** with a control run; seven originals restored byte-identically. Egress is
> **unchanged at 314 passed / 1 skipped** (315 carry the marker), while the deselected count moved
> **1717 → 1728** with the 11 non-egress tests. The
> **derived** "added since carry no marker" figure is now **81** (`2043 − 1962` collected, or
> `1728 − 1647` deselected).
>
> **Re-measured 2026-10-03 (wiring the burden metric — `DELEGATION.md` §4 item 8):
> `2053 passed / 8 skipped`** (2061 collected, 470.71 s; the canonical marker-excluded form is
> 2053 / 4 skipped / 4 deselected). The **+18** is the new pins exactly — **+3** in
> `tests/test_burden_metric_is_judged.py` and **+15** in the new
> `tests/test_burden_check_is_asked_by_the_loop.py` (two of those 15 are the **hardening** of this
> wiring: `_create_autonomous_loop` is never executed by the suite, so one pin *runs*
> `set_burden_metric(BurdenMetric(object()))` and asserts storage, and another fixes the call's
> **shape** — exactly one positional argument — via `inspect.signature` and `ast`, because an arity
> mistake there is invisible to both the suite and `F821`). This is the first entry in this list where
> **production code changed for a north-star item**: `aegis_ai/burden/metric.py`,
> `autonomous/autonomous_loop.py` and `runtime.py`. Five places were wired — the judging profile, the
> ask's field type, a cadence hook in `_run_loop`, `last_burden_ask_ms` persistence, and
> `set_burden_metric` at the composition root — and **two of them are the "wired but inert" shape**,
> which is why they are worth naming:
>
> * The judging profile was `decision`, which resolves to `api.deepseek.com` — a host the shipped
>   allowlist (`privacy.egress_allowed_hosts` = `api.typesafe.ai` only) **denies**. A denied profile
>   degrades to Mock, `is_trustworthy` is False, and a correctly-wired asker would therefore **never
>   ask**: the whole feature wired and silent. It is now `jev_decision` (TypeSafe JEV, the one
>   allowlisted destination). Measured by **driving the real resolver and the real gate**, not by
>   reading config: `decision` → `EgressDecision.DENY`, `jev_decision` → `ALLOW`. The existing pin had
>   asserted only that the profile was **declared** in `llm.yaml` — `declared` and `resolves` are two
>   different claims, and only the second is load-bearing.
> * The ask travels as the **arguments of the capability** `ai-server.confirmation.request`, so it must
>   satisfy **that capability's own `input_schema`** and not merely the `ConfirmationRequest`
>   dataclass. `side_effects` was a list where the manifest declares a **string**, so
>   `jsonschema.validate` rejected it (`[] is not of type 'string'`) and the broker would have denied
>   the ask with `VALIDATION_DENY` — the question never reaching the user. A key-name check against the
>   dataclass cannot see this (`ConfirmationRequest.side_effects` is typed `Any`); the pin now drives
>   the manifest's schema, with the old shape as a **negative control**.
>
> Two boundaries were kept rather than re-derived: the loop raises the ask **through the capability**,
> never through the `confirmation_store` it holds read-only (a loop that asks its own question is the
> forced approval gate retired 2026-09-27 — `tests/test_forced_gate_stays_retired.py`), and an
> **untrustworthy judgement is never asked about** (asking the user to confirm a Mock's number is
> asking them to check something no model produced), so the clock does not advance either. The first
> cycle **starts the clock without asking**, because the question is about a *period*; the clock is
> persisted, or every restart would re-ask. The end-to-end pins drive the **real** broker — real
> catalog, real policy engine, real capability client, real store — because a fake broker would have
> accepted the list and hidden exactly the defect above. **Mutation-proved 16/16 across the three
> files** (13 for the wiring, 3 for its hardening) with a green control and all originals restored
> byte-identically (sha256-verified: `86b3a9aaa644` / `b50e692729a8` / `f7139f755595`). Egress is
> **unchanged at 314 passed / 1 skipped** (315 carry the marker); the deselected count moved
> **1728 → 1746** with the 18 non-egress tests, and the **derived** "added since carry no marker"
> figure is now **99** (`2061 − 1962` collected, or `1746 − 1647` deselected).
>
> **Re-measured 2026-10-03 (the Docker surface — the multi-service half of `PROJECT_STATUS_REVIEW.md`
> §3.2): `2061 passed / 8 skipped`** (2069 collected, 453.34 s). The **+8** is the new pin file
> `tests/test_compose_is_coherent.py`, exactly. Measured with the real CLI (Docker 29.7.2 / Compose
> v5.5.0): `docker compose -f docker-compose.yml config --quiet` → **rc=0**; the production overlay
> **without** `AEGIS_SESSION_SECRET` → **rc=1** (`required variable … is missing a value`) and **rc=0**
> with it, so the overlay's `${…:?}` fail-fast is real rather than decorative. Services: base **6**,
> production **5** (`room-server` sits behind `profiles: [room]`), production `--profile room` **6** —
> and that profile **agrees** with the overlay's `AEGIS_DISABLED_SERVERS=room-server`: two mechanisms for
> one intent, now pinned together. The pin calls **no docker** (CI has no daemon), so it asserts
> properties of the *text*: no `depends_on` names an undefined service, no two services claim one host
> port, the named-volume set is exactly what is mounted, every `build.dockerfile` exists — plus the one
> cross-artefact pair that looks wrong and is not: `COPY --from=web-ui-build /ai-server/…` resolves
> because `web-ui/package.json` builds with `--outDir ../ai-server/src/aegis_ai/web/static/ui-v2` from
> `WORKDIR /web-ui`. ⚠️ **The gap it records**: all three built images declare a `HEALTHCHECK`, the
> compose files declare none, and every `depends_on` is `condition: service_started` — the healthchecks
> exist and **nothing gates on them** (gating is a behaviour change, `DELEGATION.md` §4 item 31). ⚠️
> **The pin's own first version had the defect it exists to catch**: it tested `"HEALTHCHECK" in text`,
> so a mutation replacing the instruction with a *comment* that mentions it stayed green — "a mention is
> not an invocation", again; the check is now `startswith` on the stripped line and excludes
> `HEALTHCHECK NONE`. **Mutation-proved 14/14** with a green control and five files restored
> byte-identically. Egress is **unchanged at 314 passed / 1 skipped** (315 carry the marker); the
> deselected count moved **1728 → 1754** with the 26 non-egress tests, and the **derived** "added since
> carry no marker" figure is now **107** (`2069 − 1962` collected, or `1754 − 1647` deselected).

> **Re-measured 2026-10-03 (the L1 gate failure record — it recorded the *fact* and threw away the
> *cause*): `2070 passed / 8 skipped`** (2078 collected, 445.07 s). The **+9** is the new pin file
> `tests/test_l1_gate_failures_carry_the_cause.py`, exactly. What it fixes: `ai-server/data/audit.db`
> held **706** `llm.first_stage.*.failed` rows whose `error` was a **fixed string**
> (`"exception during L1 tool gate"` / `…satisfaction gate`), while the real exception went only to
> `logger.debug(..., exc_info=True)` — so none of the 706 rows could be traced to anything, and the
> record could not tell "the gate broke" from "the gate was never reachable". All four `except
> Exception` sites in the gate path now carry `Type: message` via `_describe_exception`, and the
> traceback attaches to an **ERROR** record instead of a debug one. **Mutation-proved 12/12**, green
> control, original restored byte-identically. ⚠️ **The pin itself was vacuous twice**: it first
> asserted "an ERROR record exists carrying the cause", but `_emit_l1_gate_failure` *already* logs at
> ERROR — so the mutation demoting the traceback to DEBUG **survived**. What only the fixed branch can
> supply is `exc_info`, and pinning that catches it. The **harness, not review**, found this. Egress is
> **unchanged at 314 passed / 1 skipped** (315 carry the marker); the deselected count moved
> **1754 → 1763** with the 9 non-egress tests, and the **derived** "added since carry no marker"
> figure is now **116** (`2078 − 1962` collected, or `1763 − 1647` deselected).

> **Re-measured 2026-10-04 (the L1 gate was *silently bypassed*): `2075 passed / 8 skipped`** (2083
> collected, 519.92 s). The **+5** is the new pin file `tests/test_the_l1_gate_is_not_bypassed.py`,
> exactly. The gate calls `llm.generate(..., profile="l1_default")`, and **only `LLMGateway.generate`
> accepts `profile`** — `MockLLMProvider`, `openai_provider` and `typesafe_provider` all reject it
> (three signatures read, not inferred). So whenever anything other than the gateway is bound as `llm`,
> the call raises, the exception is **swallowed** (the caller reads `None` as "no decision"), and **the
> gate never runs** while the test stays green. The previous commit's diagnosability fix is what
> surfaced it: within the hour the record named two instances —
> `TypeError: MockLLMProvider.generate() got an unexpected keyword argument 'profile'` and
> `AttributeError: 'NativeToolLLM' object has no attribute 'generate'`. The `NativeToolLLM` double
> (tests only) now defines `generate`, and the new pin resolves **every** `call_llm_with_tools` /
> `_call_llm_with_runtime` site across `src/` and `tests/` and asserts the bound object accepts the
> gate's keywords — **mutation 9/9**, control green, four files restored byte-identically. ⚠️ **The
> 2026-10-03 paragraph above claimed "the four copies moved in the same commit"; two of them had not** —
> this file and the skill moved, but `PROJECT_STATUS_REVIEW.md`'s §1.1 row and its footnote stayed at
> `2061` until this commit measured them. **A record that a sweep happened is itself a claim.** Egress
> is **unchanged at 314 passed / 1 skipped** (315 carry the marker); the deselected count moved
> **1763 → 1768** with the 5 non-egress tests, and the **derived** figure is now **121**
> (`2083 − 1962` collected).

> **Extended 2026-10-04 (the same `generate(..., profile=...)` shape, swept across `src/`):
> `2078 passed / 8 skipped`** (2086 collected, 426.13 s). The **+3** is the pin file above growing
> from 5 tests to 8. Sweeping every `generate(..., profile=...)` site in `src/` (**9** of them, measured)
> showed the gate was the **only** one that swallowed a shape mismatch: 6 are guarded (a `TypeError`
> retry, or a record that carries the cause) and 3 are unguarded-but-safe (the gateway's own two, which
> *do* accept `profile`, and `social/manager.py::_generate_json`, where production binds the gateway so a
> mismatch raises loudly). The pin now classifies all 9 and **refuses a new unguarded site outright** —
> the next incomplete binding fails here instead of writing another opaque `llm.first_stage.*.failed`
> row. **Mutation 15/15**, control green, six files restored byte-identically. Egress is **unchanged at
> 314 passed / 1 skipped** (315 carry the marker); the deselected count moved **1768 → 1771** with the 3
> non-egress tests, and the **derived** figure is now **124** (`2086 − 1962` collected, or
> `1771 − 1647` deselected).

> **Named, not dropped (2026-10-04): `2087 passed / 8 skipped`** (2095 collected, 405.54 s). The **+9**
> is a new pin, `tests/test_executor_manifest_failures_are_named.py`. `ExecutorRegistry._load_one`
> returned on a manifest it could not read, so the result was **an absence, not a crash**: the executor
> is simply not in the registry, and `execute` answers `EXECUTOR_NOT_FOUND` ("No executor for <cap>")
> for a capability whose manifest loaded fine and whose `executor.json` is sitting on disk — the caller
> cannot tell "never written" from "written and unparseable". Its sibling loader
> `FolderCapabilityRegistry` has always recorded this (`_errors` / `errors()` / `reload()["errors"]`);
> the executor registry now matches, and `CapabilityCatalog.reload()` — which **discarded the executor
> registry's result outright** — forwards it as `executor_errors`, leaving what `errors` means
> (capability manifests) unchanged. **Mutation 10/10**, control green, three files restored
> byte-identically. Egress is **unchanged at 314 passed / 1 skipped** (315 carry the marker); the
> deselected count moved **1771 → 1780** with the 9 non-egress tests, and the **derived** figure is now
> **133** (`2095 − 1962` collected, or `1780 − 1647` deselected).

- **Total tests (2026-10-01 record)**: **1926 passed / 8 skipped**
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
  The **+8** over that figure are two pins for "declared, documented, and checked by nothing":
  `mypy`, which is installed yet run by nothing, so the 53 `# type: ignore` comments it justifies
  are unverified (`tests/test_type_suppressions_are_unverified.py`; `DELEGATION.md` §4 item 18);
  and the `.proto` -> generated-stub link, which nothing compared, alongside an orphan stub whose
  `.proto` source was deleted (`tests/test_generated_stubs_have_proto_sources.py`; `DELEGATION.md`
  §4 item 19).
  The **+4** over that figure is the measurement of **§3.1 hole 3's premise** — `DECISION_DRAFTS.md`
  §B-5 answers the burden metric with "derive it from the existing decision log; no new instrumentation
  is needed", and measuring shows that holds for **one of the three** proposed sub-metrics: interruptions
  per day are computable (`AuditEntry.timestamp_ms` plus the `interruption_decision` audit action), the
  fraction the user responded to is **not** (`NotificationManager` makes no audit call at all, and
  `dismiss(notification_id)` is called by the user's route *and* by `PresentationManager.dismiss` with no
  marker argument), and the median cost covers **1 of the 5** `_decision(...)` paths, because the four
  hard gates report no breakdown (`tests/test_burden_metric_has_no_instrument.py`; `DELEGATION.md`
  §4 item 20).
  The **+3** over that figure is the **dismiss path**: `PresentationManager.dismiss` looks up
  `dismiss_notification` first and falls back to `dismiss`, but production's `NotificationManager`
  defines only `dismiss`, and the sole class in the repository defining `dismiss_notification` is a
  **test double** — so the one test covering this path takes the branch production never takes, and
  the branch production always takes is covered by nothing. Measured rather than inferred: deleting
  the fallback leaves the suite at **1923 passed / 8 skipped**, i.e. production would silently stop
  dismissing notifications and nothing would fail (`tests/test_dismiss_fallback_is_uncovered.py`;
  `DELEGATION.md` §4 item 21).
- **Other suites**: `room-server` 16 · `browser-server` 100 · `aegis-sdk-python` 71 ·
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
- **Egress regression suite**: **314 passed / 1 skipped** (315 tests carry the `egress` marker,
  1780 deselected). CI enforces a floor of 160 (`--require-egress-tests=160`) **and** mutation-proves
  the gate: breaking it yields failures, restoring it yields 314 passes. The mutation figure is
  **76 failures** (measured 2026-10-03 on the 315-marker baseline; it was 74 at the 2026-10-01
  baseline of 305 and 62 at the 268-marker baseline — **re-run it before quoting**, the number is a
  function of how many tests detect the breakage).
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
| **Egress Gate** | ✅ Complete — constraint **re-scoped 2026-09-30** | Deny-by-default and fail-closed (`egress/gate.py`), **plus the second permission path the re-scope requires**: a permission the user gave about a *specific* destination, read out of the confirmation store via `egress/permissions.py`. The gate **consults and never asks**, so the retired forced gate stays retired (`test_forced_gate_stays_retired.py`). A request carrying **no user information** needs no permission — the constraint is about user information, not connectivity. The startup assertion checks that an opening is **scoped** (a scoped permission passes; an unscoped opening or a dead allowlist entry fails), not that egress is closed. Wired into 25 modules with 10 real enforcement sites. CI-enforced: **315 egress-marked tests** (314 passed / 1 skipped) against a floor of 160, plus a mutation check that fails the build when the gate is broken (76 failures, measured 2026-10-03). |
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
