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

- LLM mode is configured via the `mode` field of `llm.yaml`. In `mode: "local"`, `settings_resolver.py` remaps cloud profile names (chat_balanced, tool_planning, etc.) to local profiles (local_chat, local_tool_planning, etc.), and **vision profiles must also resolve to a local VLM**. The shipped file is **`mode: "cloud"`** so that `l1_default` actually reaches TypeSafe JEV — in local mode the remap sends L1 to Ollama and the JEV declaration is dead (measured 2026-10-02: the file said `provider: typesafe` while every call ran on `qwen2.5:3b`). What keeps that safe is **not** the mode but the **allowlist**: `privacy.egress_allowed_hosts` names only the destinations AEGIS is meant to use — `api.typesafe.ai` for L1 (JEV) and `api.deepseek.com` for L2 (`deepseek-v4-flash`) — so every *other* declared cloud destination is denied by the gate and degrades to Mock. (Before the 2026-09-30 re-scope *any* external transmission was forbidden, which made `mode: "cloud"` a violation in itself; the constraint is now **permission**-gated — `docs/GOAL-CHANGE.md`.)

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

- **Chat with tool calling**: `POST /api/chat/send` (plain JSON). The `GET /api/chat/events` SSE route **was deleted 2026-10-08** (`DELEGATION.md` §4 item 23): it was registered and returned `text/event-stream`, but it was **dead on both ends** (measured 2026-10-03) — **no producer published to it** (nothing called `put` anywhere in `dashboard_legacy.py`) and **no client subscribed** (the path occurred in exactly one file, its own definition). Pinned by `ai-server/tests/test_chat_sse_surface_is_gone.py`
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
> The **+5** on top of 1960 was `tests/test_egress_grant_source_is_unwired.py` — the recorded-grant
> path (`ConfirmationGrantSource`) was implemented and consulted on every `check()`, but no `src/`
> module constructed one and the composition root passed no `permission_source`, so it was **inert
> in the running system** (`DELEGATION.md` §4 item 22, `PROJECT_STATUS_REVIEW.md` §3.2). **Wired
> 2026-10-08** — the owner took item 22 — and the pin is now
> `tests/test_egress_grant_source_is_wired.py`. A further
> **+5** was `tests/test_chat_sse_route_stays_dead.py` — `GET /api/chat/events` was dead on **both**
> ends, which is two independent facts (`DELEGATION.md` §4 item 23); the surface was **deleted
> 2026-10-08** and the pin is now `tests/test_chat_sse_surface_is_gone.py`. And **+2** is
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
> **Update (2026-10-08, cycle 104): the audit-JSONL surface was deleted.** `DELEGATION.md` §4
> item 25 was executed under the owner's decision to **delete**: `aegis_ai/audit.py` (the shadowed
> module), `GET /api/audit/stream`, `GET /api/autonomous/skip-reasons`, the never-called
> `_load_audit_entries` helper, and the JSONL fallback inside `GET /api/audit/grouped`.
> ⚠️ The row counted "**four readers**" and its delete branch named "**4 routes**"; measurement
> found **two routes, one helper with no call site, and one dead branch inside a *live*
> route** — so the count held and the *kind* did not. `/api/audit/grouped` has a client
> (`web-ui/src/api/client.ts`) and its main path always runs, so only its fallback was removed. The pin was **inverted**, not
> deleted: `tests/test_audit_jsonl_has_no_writer.py` → `tests/test_audit_jsonl_surface_is_gone.py`
> (7 cases, **mutation 9/9 + control**). The app now registers **187 rules / 197 pairs** (was
> 189 / 199), **6** `text/event-stream` routes (was 7), and the unreferenced-route count is
> **93** (was 95).
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
> (`manager_routes.py:371`) silently reports 7 of 10 (`store` is legitimately absent — `MemoryStore` has
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
> `dashboard_memory.memory_reload` and leaves **`api_memory_reload` (`dashboard_legacy.py:1374`)** dead.
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
> The chain is dead end to end: `ChromaSemanticMemory` is constructed **only** at `memory/factory.py:38`, and
> that `create_semantic_memory` has **no caller** either (its sole mention is the module docstring's
> `Usage:` example — a string literal), while the live path builds plain `SemanticMemory` directly at
> `runtime.py:1206`. So `chroma_available` is not merely unread, it is **not even produced** on the
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
> directly (`runtime.py:1206`). The live `POST /api/memory/reload` answers `"chroma_synced": 0` as a
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
> **Update (2026-10-08, cycle 103): the chain above was deleted — `DELEGATION.md` §4 items 29 + 30.**
> The owner took the delete branch. Removed: `memory/chroma_semantic.py` (the class,
> `sync_from_advanced_memory`, `chroma_available`), `memory/factory.py`'s Chroma-selecting
> `create_semantic_memory`, `web/routes/memory.py`'s `chroma_synced` key, and `memory/semantic.py`'s
> orphaned `SemanticMemory` class. `memory/__init__.py` now re-exports the **live** class, so the
> package root no longer hands out the 6-method one — the latent trap is closed, not recorded.
> ⚠️ **Two premises in the note above were refuted by measurement.** (a) `Fact` is *not* used only
> by `chroma_semantic.py` — `backup/import_restore.py` builds one too, so `memory/semantic.py`
> **cannot** be dropped whole (only its class went). (b) The three *sibling* factory helpers
> (`create_episodic_memory` / `create_procedural_memory` / `create_reflection_log`) are **also**
> uncalled — the whole module is unreachable — but the row's scope named only the Chroma selector,
> so they **stay**, and the pin asserts they must stay, so the scope cannot creep silently.
> ⚠️ `SemanticMemory` is deliberately kept **out** of the removed-token set: it is a *shared, live*
> name, and a bare-name absence scan over it fails on a correct tree — the same trap the deleted
> `RoutingDecision` set for the intake pin in cycle 102. The pin is **inverted** into
> `tests/test_chroma_memory_chain_is_gone.py` (**11 → 10 cases**, mutation **11/11** plus a
> negative control, every mutated file restored byte-identically). ai-server **2771 passed /
> 8 skipped** (588.07 s; the **−3** is the inversion 11 → 10 and the two Chroma cases dropped from
> `test_memory_failures_are_named.py`). Egress is **unchanged at 319 passed / 1 skipped** (2459
> deselected, was 2462); non-egress is **2452 / 7 / 320**.
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
>   allowlist (`privacy.egress_allowed_hosts` = `api.typesafe.ai` only **at the time**) **denied**. A
>   denied profile degrades to Mock, `is_trustworthy` is False, and a correctly-wired asker would
>   therefore **never ask**: the whole feature wired and silent. It is now `jev_decision` (TypeSafe
>   JEV). Measured by **driving the real resolver and the real gate**, not by reading config
>   (2026-10-03): `decision` → `EgressDecision.DENY`, `jev_decision` → `ALLOW`. ⚠️ **That premise has
>   since lapsed** — the allowlist gained `api.deepseek.com` on 2026-10-06 so L2 could run, and
>   re-measured 2026-10-08 `decision` → **ALLOW** too; the rename stands for its other reason (the
>   judgement belongs to the TypeSafe JEV profile). The existing pin had
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

> **The shipped manifest tree is coherent (2026-10-04): `2092 passed / 8 skipped`** (2100 collected,
> 413.30 s). The **+5** is `tests/test_shipped_manifest_tree_is_coherent.py`. No other test reads
> `apps/` from disk, so two failure modes were invisible: an unparseable `executor.json` (the executor
> is *absent*, and `EXECUTOR_NOT_FOUND` is also the honest answer for the ~105 capabilities served
> in-process, so a typo is indistinguishable from a capability that never had an executor), and an
> `executor.json` whose capability was renamed or removed (a dead manifest nothing reads). Measured
> 2026-10-04: 23 on disk = 23 loaded, 0 load errors, 0 orphans, 128 capabilities. The counts are
> **derived from the filesystem**, so adding a capability needs no edit here — only *breaking*
> coherence fails it. It also `ast`-checks that `runtime.py` still binds those two directories, so the
> pin cannot pass while testing a tree nothing uses. **Mutation 6/6**, control green, four modified
> files restored byte-identically and two created files removed. ⚠️ The first candidate for this pin —
> "every capability has an executor" — was **refuted by measurement**: 105 of 128 have none, because
> in-process handlers serve them. That is the design, not a defect; **measure the premise before
> pinning it**. Egress is **unchanged at 314 passed / 1 skipped** (315 carry the marker); the
> deselected count moved **1780 → 1785** with the 5 non-egress tests, and the **derived** figure is now
> **138** (`2100 − 1962` collected, or `1785 − 1647` deselected).

> **A corrupt social store is reported (2026-10-04): `2102 passed / 8 skipped`** (2110 collected,
> 399.98 s). The **+10** is `tests/test_social_store_failures_are_reported.py`.
> `SocialIntelligenceSystem._load` reads six JSONL stores; `_load_jsonl` (observations / episodes)
> had always logged its failures, but the four specific loaders (relationships / reputations /
> social_norms / social_skills) used `except Exception: pass`. The consequence is the familiar one:
> the store falls back to an **empty dict**, and the only other signal is `_load`'s summary line,
> which counts entries — so a store that failed to parse and a store with no entries yet produce
> **the same line**, and a corrupted `relationships.jsonl` is indistinguishable from a fresh install.
> The four now warn exactly as `_load_jsonl` does; the empty fallback is unchanged. The pin captures
> the **log records** (`caplog`) rather than asserting on text, parameterised over the four stores,
> with a control that a *missing* store stays silent and one that a single corrupt store does not
> stop the others loading. **Mutation 7/7**, control green, both files restored byte-identically.
> Egress is **unchanged at 314 passed / 1 skipped** (315 carry the marker); the deselected count moved
> **1785 → 1795** with the 10 non-egress tests, and the **derived** figure is now **148**
> (`2110 − 1962` collected, or `1795 − 1647` deselected).

> **A corrupt `risk_overrides.json` silently dropped every override (2026-10-04): `2110 passed / 8 skipped`**
> (2118 collected, 394.55 s). The **+8** is `tests/test_policy_override_load_failures_are_named.py`.
> `PolicyEngine._load_overrides` (called from `__init__`, and in the **live** file — the
> `aegis_ai/policy_engine.py` sibling is only a re-export shim) swallowed two failures with a bare `pass`:
> an unreadable or corrupt file, and an unknown risk-level name. The consequence is not a crash but a
> silent **downgrade** — `DEFAULT_RISK_MAP` maps `RiskLevel.FORBIDDEN` to `PolicyDecision.DENY`, so an
> override that raised a capability to FORBIDDEN simply stops applying and the capability falls back to
> its (more permissive) manifest level. "No overrides file" and "corrupt overrides file" were
> indistinguishable. The **sibling mechanism** (`CapabilityCatalog`'s override store) had always reported
> this (`corrupted` / `override_store_corrupted`), so the loader now names the cause (path + exception
> type) and the consequence. Severity was **measured, not assumed**: the three hard stops do not depend on
> this file (`EXPLICIT_DENY_PATTERNS` runs on every `evaluate()`), and `set_risk_override` has **no
> production caller** today, so the exposure is **latent** — and the *fallback* asymmetry (this loader is
> fail-**open** where its sibling is fail-**closed**) is a behaviour question recorded for the owner, not
> changed. The pin's control **bites**: the same capability is DENY with a good file and ALLOW with a
> corrupt one. **Mutation 7/7**, control green, restored byte-identically. Egress is **unchanged at
> 314 passed / 1 skipped** (315 carry the marker); the deselected count moved **1795 → 1803** with the 8
> non-egress tests, and the **derived** figure is now **156** (`2118 − 1962` collected, or
> `1803 − 1647` deselected).

> **A dropped memory line was silent — and the swallow was in a shared helper (2026-10-04): `2123 passed / 8 skipped`**
> (2131 collected, 404.81 s). The **+13** is `tests/test_advanced_memory_load_failures_are_named.py`.
> `AdvancedMemory._load` reads three JSONL stores; a line it could not parse was dropped with a bare
> `except Exception: pass`, so the store came back **short** — and the only other signal, `get_stats()`,
> reports *counts*, so a store that failed to parse and a store never written produce the same kind of
> answer: **a smaller number**. The asymmetry was *inside one class* — the same class already warns when
> its LLM extraction fails. The three loops now count drops and warn once per file (per-line warnings
> would flood a badly corrupted file).
> ⚠️ **Measurement refuted a first assumption and found a second layer**: the conversation store never
> reaches `_load`'s loop — it goes through the shared `aegis_ai.jsonl_tail.read_jsonl_tail`, which
> swallowed the malformed line **itself**. The pin failed on exactly that case (it is parameterised over
> all three stores; covering only the two I had reasoned about would have passed while the third stayed
> silent). The helper now reports its per-line drops **and** its whole-read failure, which used to log at
> **DEBUG** and `return []` — indistinguishable from "no records in the window". **Mutation 8/8**, control
> green, both files restored byte-identically. The missing-file case stays silent and the tail-reader
> fallback stays at DEBUG (both pinned as non-vacuity controls). ⚠️ Also a **false positive of my own
> scanner**: `settings/store.py::import_json` was flagged as a silent `return <empty>`, but it returns
> `[f"Invalid settings JSON: {e}"]` — an AST shape check cannot tell an empty literal from an error
> literal. Egress is **unchanged at 314 passed / 1 skipped** (315 carry the marker); the deselected count
> moved **1803 → 1816** with the 13 non-egress tests, and the **derived** figure is now **169**
> (`2131 − 1962` collected, or `1816 − 1647` deselected).

> **Seven notification settings whose only readers are dead code — and the detector calls them read (2026-10-04): `2146 passed / 8 skipped`**
> (2154 collected, 379.23 s). The **+23** is `tests/test_notification_settings_are_read_only_by_dead_code.py`.
> Found by following the previous cycle's "sibling asymmetry" heuristic, then **narrowed by measurement**:
> the *class*-level fact is already recorded (`docs/feature-catalog.md` §8 lists `NotificationRouter`, all
> six channel classes and `OsNotificationProvider` as 宣言のみ; §7 says `send()` does not fan out), so the
> new finding is the **settings-level consequence plus the detector's silence**. An `ast` sweep of every
> `src/` module shows **`NotificationManager` is the only notification class constructed anywhere**
> (`runtime.py:1239`, with `event_manager=` only). So the seven `NotificationSettings` fields have exactly
> two readers — `NotificationPreferences._load_from_settings` and `QuietHoursManager._load_from_settings`
> — inside two classes **nothing constructs**; the router that owns them is itself unconstructed, and it
> builds `QuietHoursManager()` **with no `settings_store`**, so the loaders are dead **twice over**
> (`if not self._settings: return`). `tests/test_ineffective_flags.py` layer 1 scans the **bare field name
> textually**, so a reference inside dead code counts as a reader: the detector is **green on seven
> user-settable, shipped, documented flags** and its unread maps stay empty.
> **Two controls, because "nothing reads it" is also true of a broken reader**: (1) both classes *do*
> honour the settings when handed a store; (2) the read-site scan is non-vacuous **and attributes scope**,
> naming the exact `(module, class.method)` pairs for a live control field. ⚠️ **A mutation survived, and
> it was the harness rather than the pin**: the first version of control 2 asserted only "some read site
> lies outside the dead set", so rewriting **one of two** live reads as
> `getattr(..., "external_llm_allowed")` left it green; the fix is to assert the expected sites. Reads are
> attributed to the **innermost `class.method`**, not the file — a file-level check is not equivalent even
> when the file holds only the dead class, and mutation M10 (a live module-level reader added to
> `preferences.py`) is caught **only** by the scope-level assertion. **Mutation 12/12** after that fix,
> control green, seven files restored byte-identically. Records: `DELEGATION.md` §4 item 35 (wiring the
> router is a **behaviour** change — quiet hours would start deferring and the external channels would
> start attempting sends), `feature-catalog.md` §9 +4 rows, and a dated warning block in
> `docs/notification-gateway.md`, whose Quiet Hours / Preferences / Safety sections all claimed these work.
> Egress is **unchanged at 314 passed / 1 skipped**; the deselected count moved **1816 → 1839** with the 23
> non-egress tests, and the **derived** figure is now **192** (`2154 − 1962` collected, or
> `1839 − 1647` deselected). ⚠️ **A measurement trap worth repeating**: the first full run reported
> `2145 / 8` while the two marker runs reported `314 / 1 / 1839` and `1832 / 7 / 315` — **one test short**.
> The cause was that I had **rewritten the pin while the full run was still going**, so it collected the
> 22-test version. The three selections partition the collection, so `egress + non-egress == full` must
> hold; when it does not, suspect the measurement's inputs before the suite. `--collect-only` arbitrated
> (2154 for all three).

> **The operation timeline's four silent read failures now name themselves (2026-10-04): `2159 passed / 8 skipped`**
>
> `web/ui_overview._operations` merges three sources, and each was wrapped in a handler that returns an
> *absence* on failure — so a broken read is indistinguishable from "nothing recorded yet", and the
> fallbacks keep the timeline rendering a plausible result either way. All four now log a WARNING naming
> the cause and the consequence: the store (`operation_store.list_recent`), the audit groups
> (`audit_manager.list_groups`), the autonomous execution log, and — one layer down — `OperationStore._load`
> itself, where an unreadable file leaves an empty cache and a dropped line is simply not there. The two
> *legitimate* absences (no autonomous loop; no log file yet) stay silent, and the pin asserts that, or the
> warnings would be noise. Measured, not inferred: `_autonomous_logs` parses without a per-line guard, so
> **one unparsable line discards the whole cycle history** — recorded as `DELEGATION.md` §4 item 36 and
> deliberately **not** fixed, because skipping the bad line changes what the timeline shows. Pin
> `tests/test_operation_timeline_failures_are_named.py` (**13 tests**, mutation **9/9**, controls green,
> 2 files restored byte-exactly). The **+13** is that pin and nothing else; egress is **unchanged at
> 314 passed / 1 skipped**, the deselected count moved **1839 → 1852**, and the derived "added since carry
> no marker" figure is **192 → 205** (`2167 − 1962` collected, or `1852 − 1647` deselected).
> ⚠️ **Sweeping the cycle-10 counts turned up two stale copies the strengthening had left behind**:
> `DELEGATION.md` §4 item 35 and `docs/notification-gateway.md` both still said the notification pin was
> **22 tests / 9 mutations** after it had become **23 / 12**. A count that moves in two places must be swept
> in *all* of them — the pin's own file, the register, the doc, and the status report are four copies of one
> number, and the strengthening updated only some.

> **A corrupt `settings.json` silently reverted every egress permission to the narrow default (2026-10-04): `2168 passed / 8 skipped`**
>
> `SettingsStore._load` runs once from `__init__` and, on any failure, substituted the built-in
> defaults with no signal — and `runtime.py:1062` points it at the **shipped** `config/settings.json`,
> so a mistyped or corrupt file silently stopped the shipped configuration from being in effect.
> Measured before writing the message: the built-in defaults differ from the shipped config in
> **exactly three keys, all egress permissions** — `privacy.egress_allowed_hosts` `[]` vs
> `['api.typesafe.ai']`, and `external_egress_allowed` / `external_llm_allowed` `False` vs `True`. So
> the fallback is **fail-closed** (nothing is opened up — the single constraint is not at risk), but
> every external destination is then denied by the gate and cloud LLM profiles degrade. Driving the
> factory confirmed both halves: with defaults the gate logs `egress deny … reason=external egress is
> disabled`, while the shipped config's profile is *permitted* and reaches Mock only because no local
> Ollama is listening. The same file's `import_json` had the mirror defect — **one `try` around both
> the parse and the apply** made a *disk* failure read as `Invalid settings JSON`, the fixed-message
> shape again — now split into two messages. Pin `tests/test_settings_store_load_failures_are_named.py`
> (**9 tests**, mutation **8/8**, four of them degrading the controls, 2 files restored
> byte-exactly). The **+9** is that pin and nothing else; egress is **unchanged at 314 passed / 1
> skipped**, the deselected count moved **1852 → 1861**, and the derived "added since carry no marker"
> figure is **205 → 214** (`2176 − 1962` collected, or `1861 − 1647` deselected).
> ⚠️ **A second defect was measured and recorded, not fixed**: `update` assigns `self._settings`
> *before* `_persist()`, so a persist failure leaves the in-memory value changed and the disk
> unchanged (measured: before `False`, `PermissionError`, after `True`). Persisting first would change
> when the in-memory value moves — a behaviour change — so it is `DELEGATION.md` §4 item 37, and the
> pin fixes the current behaviour so that fixing it must be deliberate.

> **The `mind/` persistence family named its read failures — and the family's silence turned out to be keyed on the exception type (2026-10-04): `2202 passed / 8 skipped`**
>
> Eight modules in `aegis_ai/mind/` (`desire`, `emotion`, `goals`, `identity`, `layered_emotion`,
> `mood`, `personality`, `social_intelligence`) carried an **identical** `_load` whose
> `except (json.JSONDecodeError, OSError): pass` made a corrupt file indistinguishable from
> "no data yet" — the family had **no logger at all**. All eight now name the path, the exception
> and the consequence (`goals.py` also catches `KeyError`).
> ⚠️ **The boundary was measured, not assumed** — the family's silence is keyed on the exception
> *type*, not on whether the file is usable: a valid JSON line that is **not an object** (`123`)
> raises `AttributeError` out of `__init__` in all eight, because `json.loads` accepts it and the
> next `last.get(...)` fails. `123` is exactly as unusable as `{"a": 1`, yet one is defaulted and
> the other stops construction. And the exposure depends on the site: both live construction
> points are **unguarded** (`runtime.py:1163`, `runtime.py:1837`) while a third swallows the same
> call at DEBUG (`llm/memory_context.py:323`). Widening the caught set changes behaviour, so it is
> `DELEGATION.md` §4 item 38 and the pin fixes the current divergence.
> ⚠️ **The family's scope was measured too** — by *construction*, not by import: of the eleven
> modules, the only one built outside `mind/` is **`Identity`** (`runtime.py:1163`); `Mood`,
> `Personality` and `LayeredEmotion` are live only through `AffectSystem`, and `Desire`, `Emotion`,
> `GoalManager`, `SocialIntelligence` are built **nowhere** — `Emotion`/`GoalManager` are imported
> only by `reflection_loop.py`, which is itself never constructed (a second-order dead surface).
> Two of the unwired ones share a name with a **live** class (`mind/desire.py`'s `Desire` vs
> `desire/desire_system.py::DesireSystem`; `mind/social_intelligence.py`'s `SocialIntelligence` vs
> `social/intelligence.py::SocialIntelligenceSystem`), so the convenient import gets the dead one.
> `mind/social_intelligence.py` also implements **keyword matching** (`"too long" in feedback`),
> against AGENTS.md's core rule — inert today only because the class is never built. All of it is
> `DELEGATION.md` §4 item 39.
> **⚠️ 2026-10-08 (cycle 105): three of them are now gone.** `mind/desire.py` (105 lines),
> `mind/priorities.py` (77) and `mind/social_intelligence.py` (120) were **deleted**, together with
> their re-exports in `mind/__init__.py` — measured first: no importer in `src/` or `tests/` outside
> `mind/__init__.py`, `priorities.py` imported by **nothing** (not even a test), and `mind/desire.py`
> had **no importer at all**. `Emotion`/`GoalManager` were **kept**: their only importer is
> `aegis_ai/reflection_loop.py` (146 lines, itself never constructed), whose fate the row defers as a
> separate decision — so branch ② of the row is **internally ordered**. New pin
> `tests/test_mind_unwired_modules_are_gone.py` (6 tests, mutation **8/8**); the family pin
> `test_mind_persistence_failures_are_named.py` was trimmed from eight modules to **six** (26 passed).
> ⚠️ `Desire` is **not** a removed name — `desire/desire_system.py:720` defines the live legacy alias
> `Desire = DesireDimension`, so a bare-name absence scan over `Desire` fails on a correct tree; the
> new pin pins that alias's **presence** as its control.
> **`docs/mind-layer.md`'s "ContextBuilder Integration" was corrected** after it failed to run:
> its example passed `affect_system=` / `social_intelligence=`, which `ContextBuilder.__init__`
> does not accept (`TypeError` measured), and read `ctx.affect` / `ctx.social`, which do not exist.
> The only `ContextBuilder(` call site in `src/` is `runtime.py:1165`, and the only mind component
> it receives is `identity`.
> Pin `tests/test_mind_persistence_failures_are_named.py` (**34 cases**, mutation **8/8**, three of
> them degrading a control, 2 files restored byte-exactly). The **+34** is that pin and nothing
> else; egress is **unchanged at 314 passed / 1 skipped**, the deselected count moved
> **1861 → 1895**, and the derived figure is **214 → 248** (`2210 − 1962` collected).
> ⚠️ **My own structural test was wrong once**: it filtered out `ast.Expr` before asking "is the
> handler body only `pass`?" — and a bare `logger.warning(...)` statement **is** an `ast.Expr`, so
> all eight named handlers were reported as silent (eight false positives, measured). Dropping the
> filter gave 34 passed.
> **⚠️ 2026-10-08 (cycle 107): the last two are gone, and with them the module that kept them alive.**
> `mind/emotion.py` (153 lines) and `mind/goals.py` (171 lines) were deleted together with
> `aegis_ai/reflection_loop.py` (146 lines) -- their **only** importer. The loop was measured before it
> was deleted: 0 importers under `src/` or `tests/`, its class constructed nowhere, and its role already
> filled by `reflection/reflection_engine.py::ReflectionEngine` (built in `runtime.py`, called from
> `autonomous/autonomous_loop.py`) -- so "wire it up" would have created a *second* reflection
> implementation. `mind/__init__.py` now re-exports `Identity` **only**.
> The cycle-106 pin was **inverted**, not resized: `tests/test_reflection_loop_is_gone.py` (7 cases,
> mutation **7/7**) keeps the cycle-106 **positive half** -- the successor defined, imported, consumed and
> wired from the composition root -- because a pin asserting only absences cannot be told apart from "the
> feature was never written". The sibling pin now covers five modules, and its re-export check became an
> **equality** (`imported == {"Identity"}`): the hand-maintained kept-list had gone *empty*, so a loop
> over it would have passed vacuously. The family pin went **6 -> 4 modules (26 -> 18 cases)**.
> ⚠️ **The deletion's own litter turned into a census.** `ai-server/pyproject.toml`'s
> `per-file-ignores` still exempted the deleted files -- and enumerating that table (not sampling it)
> found **8 of 25 keys naming a file that does not exist** (6 deleted, 2 relocated into `autonomous/`).
> Ruff does not warn about such a key, so each one silently asserted an exemption that was **not in
> force**. All eight were inert: removing them left `ruff check src tests` at **1194 findings**,
> unchanged, with the CI gate (`--select F821`) green. The table is now pinned by
> `tests/test_ruff_per_file_ignores_resolve.py` (3 cases, mutation **3/3**).
> **⚠️ 2026-10-09 (cycle 108): L1 was pinned on both sides of the L2 boundary but never *at* it.**
> `tests/test_runtime_singleton.py` drives `_run_l1_pipeline_for_event` (the L1 event sequence) and
> `tests/test_l1_runs_off_the_publisher_thread.py` pins *where* the immediate route runs (a dedicated worker) and
> that its failure is loud. **Nothing drove `_run_l1_immediate_pipeline`** -- the dispatch that decides whether the
> event is handed to L2, notified to `initiative_engine` / the `AutonomousLoop`, or dropped. That is the "just
> before L2" boundary the owner asked to confirm.
> `tests/test_l1_reaches_the_l2_boundary.py` (**9 cases, mutation 8/8 + control**) now drives it: `ignore` returns
> before any notification (while L1's own record is already published); `capability` returns after
> `record_trigger`; anything else calls `_run_l2_pipeline` **once** with `trigger=event_type` and the `detail["l1"]`
> projection, records `detail["l2"]`, and returns after `record_trigger` **only if** L2 reported `handled` with an
> action type outside `{"noop", "observe"}` -- otherwise it falls through to `record_trigger` + `evaluate_event`;
> with no `l2_mind` the L2 call is skipped and the two notifications still happen. Behaviour unchanged (test-only).
> ⚠️ **`ruff format` and `ruff check` disagreed on one line**: `format --check` *joined* an implicitly concatenated
> f-string onto one line, which came out **134 columns** and tripped `E501` (limit 120). `ruff format` does not split
> string literals, so the only exit was to shorten the message and move the prose into a comment. Keep applying such
> joins by hand -- `ruff format` rewrites the file as CRLF on Windows -- and measure against **both** checks.
> **⚠️ 2026-10-09 (cycle 109): `AEGIS_DATA_DIR` is honoured by the leaf and ignored by the root -- and the record's *scope* hid that.**
> Three **shipped** capability executors (`apps/builtin/ai-server/memory/{save,search,sleep}/executor.py`) resolve
> their root as `os.environ.get("AEGIS_DATA_DIR") or os.path.join(ROOT, "data")`, while `runtime.py:1061` computes
> `data_dir = str(base_dir / "data")` and reads no environment at all. Setting the variable therefore moves what
> `memory.save` / `memory.search` / `memory.sleep` read and write, and nothing else -- the audit DB, settings,
> confirmations, user model, journals and logs stay in the repository's `data/`. That is worse than an inert variable:
> it *appears* to work.
> The fact was already recorded -- in the module docstring of `tests/test_egress_grant_source_is_wired.py`: "nothing
> under `src/` reads `AEGIS_DATA_DIR`". True, and misleading on its own: the reader concludes the variable is dead,
> when three shipped capabilities depend on it. The docstring is corrected and the reader set is now an **equality**
> in `tests/test_data_dir_is_honoured_by_the_leaf_not_the_root.py` (6 cases, mutation **8/8** + control).
> ⚠️ **The name has a sibling**: `AEGIS_DATA_DIR_WARNING_MB` is a *different* variable read by `alert_manager.py`, so
> a substring scan reports a `src/` reader that does not exist. The pin reads `ast` string arguments and asserts the
> sibling as a control.
> **Both halves driven**: the leaf (`memory.save` with `type="person"`, which avoids the LLM path, writes
> `<temp>/memory/persons.jsonl` and leaves the repository's `data/` untouched -- `audit.db` byte-identical); the root
> (the `data_dir` expression is extracted with `ast` and asserted to read no environment).
> **Recorded, not fixed** (both fixes are behaviour changes) -> DELEGATION.md section 4 item 75.
> ⚠️ **By-product: `ruff format` is declared and never enforced** -- `ruff format --check src tests` reports
> **403 files would be reformatted / 222 already formatted**. CI runs `--select F821` only, so nothing looks at
> formatting; same shape as cycle 107's `per-file-ignores` (a declared property with no validator). A single-file
> `format --check` says nothing about the repository: extracting `git show HEAD:...` **outside** the repo makes ruff
> use its default config (line-length 88) and answer "already formatted" -- pass `--stdin-filename` instead. -> item 76.
> **⚠️ 2026-10-09 (cycle 110): the audit JSONL is a read-only legacy source, and two live reads fall back to it.**
> `AuditLog` carries `_path` (JSONL, default `data/audit.jsonl`) and `_db_path` (SQLite). Writes go to **SQLite**; the
> JSONL is read **once** by `_migrate_jsonl_if_needed` and is **never written** by anything under `src/` (`ast`).
> `AuditManager._audit_path` (`audit_manager.py:69`) points at it and uses it in three places: (1) `rotate()`'s **only**
> source, so `_read_tail(10000)` always returns fewer than 10000 entries and `rotate()` **always returns 0** -- and
> `rotate` has **0 call sites** under `src/`, so it is unreachable (a future wiring would add a silent no-op);
> (2) a **fallback** in `_read_recent_entries`; (3) a **fallback** in `_read_recent_entries_filtered`.
> On the shipped deployment `data/audit.jsonl` does not exist, so those fallbacks return `[]`: a SQLite failure makes
> a dashboard read an **empty** audit history, indistinguishable from "there are no entries". That is the "an
> unreadable source looks like an empty source" family, one level below the naming already pinned by
> `test_audit_failures_are_named.py`. **Recorded, not fixed** (removing the fallback, carrying its cause, or wiring
> rotation are all behaviour changes) -> DELEGATION.md section 4 item 77. Pin: 9 cases, mutation **6/6** + control.
> **⚠️ 2026-10-09 (cycle 111): the Testing Guide's own commands did not run -- the interpreter path was wrong in three places.**
> `docs/testing.md` and `README.md` both said `cd ai-server` then `.\.venv\Scripts\python.exe`, but `ai-server/.venv`
> **does not exist**: the venv is at the **repository root** (`AEGIS/.venv`), one editable env for every server
> (`__editable__.aegis_ai_server-0.1.0.pth` and `__editable__.aegis_browser_server-0.1.0.pth` in its `site-packages`).
> The gate (`scripts/test-ai-server.ps1:38`) and `docs/egress-gate.md` (`../.venv`) already used the root; the two
> guides were the outliers. Both now say `..\.venv`.
> ⚠️ **The line under a warning against hand-maintained numbers was a hand-maintained number**: the section that says
> "enumerate the directory rather than trusting a hand-maintained list" carried `# 126 files, measured 2026-10-02`;
> measured today it is **213** (+87 in seven days). The count is removed, not refreshed.
> ⚠️ **The "CI pipeline (planned)" section named no gate**: it listed `pytest` / `ruff check .` / `ruff format --check .`
> / `./gradlew test`, omitting the egress floor and the mutation check -- the two steps that guard the single
> constraint. There is no hosted CI (no `.github/workflows/`); the gate is `scripts/test-ai-server.ps1`, delegated to by
> `test-all-suites.ps1`, and it scopes ruff to `--select F821`. The section now names the runner. -> section 4 item 78.
> ⚠️ **Running the suite with the root `.venv` reddens one test, and it is not the edit**: that venv's two broken
> `.pth` files (`distutils-precedence.pth` -> `_distutils_hack`, `pywin32.pth` -> `pywin32_bootstrap`) print two
> tracebacks to **every** python start, subprocesses included, so `tests/test_a_failing_sub_audit_check_carries_its_cause.py`
> -- whose premise is "a failing sub-audit leaves stderr empty" -- fails there (**1 failed, 12 passed**) and passes
> under the AEGIS venv (**13 passed**). The gate uses the root `.venv`, so it is **red on this machine**. -> section 4 item 79.
> Test delta **0** (documents only), so every live count copy is unchanged.
> **⚠️ 2026-10-09 (cycle 112): two of the Testing Guide's claims were true when written and false now -- a falsified premise, and a snippet naming two classes that no longer exist.**
> `docs/testing.md:42` -- a *dated correction* (2026-10-02) -- explained that the removed E2E entries described an
> `EventBus -> TriggerEngine -> ContextBuilder` flow "that cannot run, **because no `TriggerEngine` is constructed**".
> That reason was **falsified on 2026-10-06**: branch (1) of section 4 item 24 built the event-driven core, so a
> `TriggerEngine` **is** constructed in `runtime.py::_build_runtime` and subscribed to the bus (pinned by
> `ai-server/tests/test_event_driven_core_is_constructed.py`). The **16** absent filenames are still absent; only the
> *explanation* was stale. **A dated correction is a claim about the code at a moment -- re-measure it before quoting it.**
> ⚠️ **The "Android E2E pattern" snippet was a fabrication.** It named `AndroidServerClient` and `MockAndroidProvider`,
> both of which existed **only** in `ai-server/src/android_server_client.py` (deleted 2026-09-29, P1-5), and it defined a
> helper `_setup_full_stack` that exists **nowhere** in the repository. Copying it produced an `ImportError`, and nothing
> noticed because no pin reads a fence for *class names* -- `test_docs_run_tests_that_exist.py` reads fences only for
> `tests/...py` paths. It now shows the shape of the **live** integration (`aegis_ai.integrations.android`, covered by
> `ai-server/tests/test_android_integration.py`) and notes that `AuditLog(path=...)` derives a `.db` sibling, so the old
> `path="data/test_audit.jsonl"` would have created a *SQLite* file.
> ⚠️ **The "16" in that correction and the "17" in the pin's header are both right -- they are different scopes.**
> Measured at `5c8b34a^`: the "Unit Tests" list held **8** absent names and the "E2E Integration" list held **8** (16
> together, the correction's stated scope); a **17th** (`test_approval_redesign.py`) sat in the *focused-checks command*,
> a different section. **The predicate must match the claim's scope** -- "fixing" 16 to 17 would have introduced an error.
> ⚠️ **The `path.py:NNN` citation family has rotted a second time.** Eight citations in `DELEGATION.md` rows 172/244/246
> were **git-verified as exactly right at `827d6e1` (2026-10-06)** and have drifted since (row 244: `:1799`->**1813**,
> `:1803`->**1817**, `:1804`->**1818**, `:1916`->**1930**; rows 172/246: `:1110`->**1111**, `:1221`->**1222**,
> `:1283`->**1284**, `:1516`->**1530**, `:1229`->**1230**, `:1227`->**1228**). Cycle 67 renumbered eleven of these, and
> the pin's own header (section 4 item 70) already records that a bare `:NNN` **is not durable** while `path.py::<symbol>`
> is. The sweep must be by **claim**, not by file -- copies live in this file, `DELEGATION.md`,
> `PROJECT_STATUS_REVIEW.md`, two test docstrings and the `aegis-verify-and-test` skill -- and the number `1110` names
> **two different targets** (`tool_broker = ToolBroker(` and `DelegationPolicyStore`). **Recorded, not fixed** ->
> section 4 item 80.
> ⚠️ **And the documented *command* was not inert either.** `docs/testing.md` recommended a
> `--basetemp .tmp-pytest` **inside the repository** as the standard full-suite invocation -- but that puts
> `tmp_path` in `ai-server/.tmp-pytest/...`, which is *inside* `ROOT`, and
> `scripts/audit-production-readiness.py::_display_path` renders a path **relative to `ROOT` when it is inside it**.
> Four tests whose premise is "a custom report dir is reported *absolutely*" therefore fail
> (`test_every_report_read_honours_the_report_dir.py` x2, `test_every_sibling_audit_honours_the_report_dir.py` x2).
> Measured 2026-10-09 as a pair: those two files with `--basetemp .tmp-c112-control` -> **4 failed / 31 passed**;
> with no `--basetemp` -> **35 passed**. The section now gives the canonical command and says to put a basetemp
> **outside** the repository. ⚠️ **Cycle 111 fixed `..\.venv` in this very command and did not run it** -- a
> documented command is a claim about the *environment*, and a false failure is as bad as a failure to start.
> -> section 4 item 81.
> Test delta **0** (documents only), so every live count copy is unchanged -- but a documented
> *command* was not inert either, and a false failure is the same class.

> **`AutonomousLoop`'s four swallowed failures now name themselves — one of them was feeding the planner a false statement (2026-10-04): `2209 passed / 8 skipped`**
>
> `AutonomousLoop` turned four *failures* into an *absence* or a *default*, none of them logged, so
> each was indistinguishable from a positive fact: `_priority_obligations` -> `[]` ("every duty is
> already resolved"); `_current_interruption_cost` -> `0.15` -- **the same value as the "no AgentState
> wired" default**, so "read failed" and "nothing wired" were one number; `_manifest_for` -> `None`
> ("capability absent", which `_is_inventory_capability` reads as `False`); and `_load_recent_history`
> -> `[]`, which `_build_action_history_summary` renders as the literal string **`"Autonomous
> execution history: no actions executed yet. First run."`** and injects into the planning LLM's
> context -- while `_burden_activity` reports the period as empty and `_recent_capability_ids` reports
> no recent capabilities.
> All four now name the path (where there is one), the exception type and the consequence. **The
> return values are unchanged**, so the pin fixes behaviour that already existed and may not move.
> Two sibling handlers stay silent **on purpose** and are allow-listed in the pin:
> `_call_propose_candidates_llm` degrades malformed LLM JSON to
> `{"candidates": [], "no_action_reason": <raw content>}` (the reason is preserved, so it is not
> silent) and `_sanitize_for_execution_log` is a masking layer, not a data read.
> Pin `tests/test_autonomous_loop_failures_are_named.py` (**7 cases**, mutation **7/7** plus a no-op
> control, original restored byte-exactly). The **+7** is that pin and nothing else; egress is
> **unchanged at 314 passed / 1 skipped**, the deselected count moved **1895 -> 1902**, and the
> derived figure is **248 -> 255** (`2217 - 1962` collected).
> ⚠️ **The control caught my own unrealistic double**: `_capability_catalog()` reads `self._broker`
> directly (no `getattr` default), so a bare `object.__new__` instance raised `AttributeError` instead
> of returning `None` -- production always sets that attribute. **The double must match production.**
> ⚠️ **The consequence is recorded, not fixed**: `_build_action_history_summary` still asserts
> "no actions executed yet. First run." on a read failure -- changing that string changes what the
> planner is told, so it is `DELEGATION.md` §4 item 40.
>
> **`CuriosityExploration`'s fifteen swallowed failures now name themselves — an unreadable source scored the same as an empty one (2026-10-04): `2227 passed / 8 skipped`**
>
> `curiosity_exploration.py` turns seven candidate sources plus a curiosity update, three
> context builders and a four-way save into candidate lists. Every one of the fifteen failure
> paths was silent, so **a source that could not be read contributed exactly as many
> candidates as an empty source: none** — an unreadable store was indistinguishable from a
> system with nothing to be curious about. The module already named its *LLM* failure
> (`_candidates_from_llm` logs "LLM suggestion failed"), so only the *source* failures were
> silent: an asymmetry measurable inside one class.
> All fifteen now name the source, the exception type and the consequence. **The return
> values are unchanged**, so the pin fixes behaviour that already existed.
> Pin `tests/test_curiosity_exploration_failures_are_named.py` (**18 cases** = 15 driven sites
> + a legitimate-absence control + 2 structural, mutation **19/19** with a no-op control,
> original restored byte-exactly). The **+18** is that pin and nothing else; egress is
> **unchanged at 314 passed / 1 skipped**, the deselected count moved **1902 -> 1920**, and the
> derived figure is **255 -> 273** (`2235 - 1962` collected).
> ⚠️ **The pin caught a defect in my own message text**: adjacent string literals concatenate
> with no separator, so a message split as `"...leaves no record"` + `"on disk..."` rendered
> **"no recordon disk"** — visible only because the pin asserts on the *rendered* text.
> ⚠️ **Three self-inflicted tooling defects were caught by three different mechanisms**: the
> pre-write `ast.parse` (a replacement missing a trailing comma), `git` (replacement blocks
> built from only the `except` block **deleted** the 15 `context` lines), and the rendered-text
> assertion (the missing spaces). None reached a commit.
>
> **`SpontaneousObservation`'s nine swallowed failures now name themselves — an unreadable source looked like a calm system (2026-10-04): `2239 passed / 8 skipped`**
>
> `spontaneous_observation.py` builds its observation list from seven sources plus a log
> write, and nine of those paths sat in `except Exception: pass` (or a bare `return obs`).
> A source that could not be read contributed exactly as many observations as a healthy,
> quiet source: **zero**. The stakes are higher here than a missing log line:
> `autonomous_loop._refresh_observations_for_cycle` filters these into
> `_pending_actionable_observations`, and at `autonomous_loop.py:1121`
> `should_run_l2 = bool(self._pending_actionable_observations)` — so a real signal (a full
> disk, a stuck task, a degraded server) that could not be read is never surfaced, and the
> loop proceeds as if the system were calm. (A failed source does not *clear* the pending
> list; it prevents the signal from ever entering it.)
> All nine now name the source, the exception type and the consequence. **The return values
> are unchanged**, so the pin fixes behaviour that already existed.
> Pin `tests/test_spontaneous_observation_failures_are_named.py` (**12 cases** = 9 driven
> sites + a legitimate-absence control + 2 structural, mutation **11/11** with a no-op
> control, original restored byte-exactly). The **+12** is that pin and nothing else; egress
> is **unchanged at 314 passed / 1 skipped**, the deselected count moved **1920 -> 1932**,
> and the derived figure is **273 -> 285** (`2247 - 1962` collected).
> ⚠️ **The unit is a choice, and this module had a second mechanism**: three sibling handlers
> already call `logger.debug(..., exc_info=True)`. Measured: **every entrypoint configures
> `logging.INFO`** (`AGENT_SERVER_LOG_LEVEL` defaults to it), so those three leave a record
> that never ships. That is a *visibility* question, not a *silence* one, so cycle 16 fixes
> the nine that record at **no** level and records the three separately (`DELEGATION.md` §4
> item 42). Conflating them would have blurred the unit of the scan.
> ⚠️ **My own verifier was wrong before the code was**: the first post-edit check searched the
> *source text* for each consequence phrase and reported five missing — but the phrases span
> adjacent string literals, which only concatenate at runtime. Re-checking the **rendered**
> format string via `ast` showed 9/9 present, with `%s` count == argument count.
> ⚠️ **The behaviour is recorded, not fixed**: `should_run_l2` still cannot distinguish "no
> actionable observations" from "every source failed" — `DELEGATION.md` §4 item 41.

> **`ContextBuilder`'s four reachable swallows now name themselves — an unreadable backend looked like an empty one (2026-10-04): `2246 passed / 8 skipped`**
>
> `context_builder.py` has **fourteen** `except` handlers and, before this cycle, **no logger at
> all**. Measuring *reachability before writing* changed the claim: the composition root
> (`runtime.py:1165`) constructs the builder with **7 of the ~20** backends it accepts, so ten
> handlers sit on paths that either never run or are deliberate fallbacks — **8** on unwired
> backends, and **2** that still produce a value (`_user_model_store` falls back to
> `to_context_string()`, `_media_fingerprint` to `str(metadata)`). Naming the first group would
> add a record to code that cannot run; naming the second would misdescribe a handled failure.
> This cycle names the remaining **four** (`recent_events`, `available_capability_ids`, the
> media payload, the media summary), each of which yields a value indistinguishable from a
> successful-but-empty result. **The return values are unchanged**, so the pin fixes behaviour
> that already existed.
> Consequence, measured: `ctx.recent_events` and `ctx.recent_media_summaries` are rendered into
> the interpreter's context (`llm_task_interpreter.py:367-370`), so a failed read silently drops
> a line from what the LLM is told. `ctx.available_capability_ids` is read only for **token
> accounting** (`:750`, `:787`) — its consequence is a wrong budget, **not** "the LLM sees no
> capabilities". `ctx.dialogue_policy` is read only inside this module and rendered nowhere.
> Pin `tests/test_context_builder_failures_are_named.py` (**7 cases** = 4 driven sites + a
> legitimate-absence control + 2 structural, mutation **7/7** with a no-op control, original
> restored byte-exactly). The **+7** is that pin and nothing else; egress is **unchanged at
> 314 passed / 1 skipped**, the deselected count moved **1932 -> 1939**, and the derived
> figure is **285 -> 292** (`2254 - 1962` collected).
> ⚠️ **The pin encodes reachability, not just the fix**: it parses `runtime.py` and asserts the
> `ContextBuilder(...)` keyword set **equals** the seven wired backends, so *wiring* another
> backend turns it red and sends the reader back here (`DELEGATION.md` §4 item 43).
> ⚠️ **My mutation harness was wrong before the pin was**: the first "rename the phrase" mutant
> was a **no-op** — the phrase spans adjacent string literals, so `str.replace` found 0
> occurrences and the pin "passed" for the wrong reason. A mutant identical to the original
> reads as "the pin is vacuous", so the harness now **asserts the mutant differs** and checks
> the phrase in the **rendered** text (`ast`), not the source.

> **`web/ui_overview.py`'s eight bare-absence swallows now name themselves — an unreadable source looked like an empty section (2026-10-04): `2259 passed / 8 skipped`**
>
> The module has **26** `except` handlers; cycle 11 had already named **four**. Measuring the
> remaining 22 *before* naming them split them three ways, and only **eight** are swallows:
> **8 are deliberate coercion / signature retries** (`_number`, `_as_wire_text`, `_json_preview`,
> `_call_with_limit`, `_humanize_event_message`, `_causal_chain_from_operation`'s optional
> `ImportError`, and two `except TypeError` retries that call a narrower signature) — naming them
> would misdescribe a handled conversion; **5 already put the exception into the payload**
> (`_section`, `_agent_state`, `_user_understanding`, `_initiative`, `_behavioral_reports` all
> return `{"summary": f"... unavailable: {exc}"}`), so the failure is *visible*, not swallowed;
> and **1 is a documented fallback** whose own comment calls the raw data usable.
> Reachability was measured first: all five enclosing functions are live (`_mind_summary` /
> `_usage` / `_errors` are registered as sections at `:38` / `:69` / `:70`; `_server_list` at
> `:725`/`:769`/`:848`/`:1651`; `_recent_ui_events` at `:905`/`:939`/`:964`).
> The heaviest consequence is `_usage`: when the read fails, `data` stays empty, `if not data:`
> fires, and the section displays the text **"LLM usage is available from the LLM Usage
> service."** — a failed read reported as an available service. **Return values unchanged.**
> Pin `tests/test_ui_overview_failures_are_named.py` (**13 cases** = 8 driven sites + a
> legitimate-absence control + 4 structural). The structural tests pin the *deliberate* handlers
> as unnamed (26 handlers / 12 named; the coercion set stays silent; the five surfacing handlers
> must mention `exc` in their body). **Mutation 12/12** (each site neutered individually, all
> eight at once, an added silent handler, and a renamed phrase) with a no-op control; the module
> was restored byte-exactly.
> ⚠️ **The pin found a real asymmetry before it was finished**: `_server_list` reads
> `runtime.status_manager` (via `_runtime_server_status`) with **no** getattr default, so a
> minimal runtime raises `AttributeError` that *propagates* — while `_errors` swallows the same
> call. Recorded as `DELEGATION.md` §4 item 44.
> ⚠️ **The instrument lied once more, in the same way**: the recon's first scan reported
> **0 handlers in a 3706-line file** because the visitor object was built twice, so the result
> came from a fresh instance. A clean zero is the signature of a dead instrument.

> **L1-only operation: the key that makes it work, the three dead triggers beside it, and two instruments that lied (2026-10-05): `2262 passed / 8 skipped`**
>
> The question "what is missing for full-scale L1-only operation?" was answered by measurement, not reading.
> **(1) The LLM key.** `config/llm.yaml:125` `l1_default` is `provider=typesafe, model=jev-latest,
> api_key_env=TYPESAFE_API_KEY`. With the key absent the gateway builds a **`TypeSafeProvider` with an empty
> key** (`llm/gateway.py:168-174`), the call fails, `_l1_unavailable_observation` (`intake/l1_router.py:160`)
> returns `value=1.0 / priority=1.0 / required_intelligence=HIGH`, and **every event escalates** — L1 classifies
> nothing. This is **loud, not silent**: `_audit_llm_profile_health` (`runtime.py:285`, called `:1146`) already
> logs `profile=l1_default … issue=missing_api_key` at ERROR. Verified live with the local `.env`: `l1_default`
> resolved to typesafe/jev-latest, the gateway built **`TypeSafeProvider`** (not Mock), and a real call returned
> `value 0.2075 / priority 0.135 / confidence 0.722`. The requirement is now documented in `.env.example`,
> `docs/ubuntu-production.md`, and `docs/jev-l1-verification-2026-10-02.md` (placeholder only — the real key
> stays in the gitignored `.env`).
> **(2) Three of the 16 immediate triggers have no producer.** `hook.matched` / `commitment.due` /
> `browser.discovery` (`runtime.py:989`) never appear as a `publish` literal. `hook.matched` and
> `commitment.due` are superseded by `self_call` (`personal_ai/hooks.py:371`, `commitments.py:117`);
> `browser.discovery` has no concept anywhere. Nothing is lost today, so they are **recorded, not deleted**
> (deleting would break `tests/test_runtime_singleton.py:617`). New pin
> `tests/test_l1_immediate_triggers_have_producers.py` (**4 cases, mutation 2/2**, control green) pins the
> **negative half only**: the three recorded triggers still have no producer, and the scanner's visible
> range is exactly one of the sixteen (`social.inbox.received`). ⚠️ **Corrected 2026-10-05 (cycle 32)**:
> the older wording here claimed it also pinned *that the other 13 have a producer* — it never did, and
> that claim is false: measured, only **1 of 16** has a publish-literal producer inside `ai-server/src`.
> The earlier "3" counted *mentions* (a consumer, an allow-list entry, a UI reader) as producers; the
> real producers live in other languages (Kotlin `eventType=`, Rust `event_type:`) or in
> `build_event`/`Event(event_type=)` shapes this scanner cannot see. Without the control the absence
> assertions would be vacuously true.
> ✅ **Fixed 2026-10-06 (cycle 66, §4 item 45)**: this block's line numbers were renumbered
> (`runtime.py:826` → **989**, `personal_ai/hooks.py:367` → **371**; `commitments.py:117` was still
> right) — cycles 63–65 inserted lines above them, and a *pointer* is not a historical datum. The
> substantive fix is in `runtime.py`: its comment still claimed this pin asserts "every other member
> still does [have a literal publisher]" — the **inverse** of what the pin asserts, and false
> (measured: **1 of 16**, not 13 of 13). The partition is now stated as measured **and pinned by
> number** (`test_the_partition_is_pinned_by_number`: 16 declared / 1 published / 15 not). That closes
> a real hole: the pin's other three assertions intersect with the *published* set, so a newly added
> **dead** declaration left them all green — mutation M1 of cycle 66 fails the new test **alone**
> (**5 cases, mutation 4/4**, control green).
> **(3) L1 runs inline on the publisher's thread.** `EventBus._notify_subscribers` (`src/event_bus.py:234`)
> calls `sub.handler(event)` synchronously; `_evaluate_immediate_event` (`runtime.py:1725`) →
> `_run_l1_pipeline_for_event` (`:764`) → `router.observe(...)` (`:771`, the LLM round-trip). The gRPC
> `PushEvent` handler (`grpc_server.py:169` → `publish` at `:185`) is one publisher, so a remote push blocks
> for the whole L1 call. **L2 was already moved off the request thread** (`_submit_background_l2`,
> `runtime.py:792`); there is **no `_submit_background_l1`**. Recorded as §4 items 47–49, together with the
> intake-side dead classes (item 47).
> ✅ **Fixed 2026-10-06 (cycle 64, §4 item 48 branch ①)**: the asymmetry is gone. `_submit_background_l1`
> hands the **whole immediate route** (L1 decision → `detail["l1"]` → capability short-circuit → L2 hand-off
> → `initiative_engine` / `AutonomousLoop`) to a single worker (`aegis-background-l1`), mirroring
> `_submit_background_l2`, and `_evaluate_immediate_event` is now a route check plus one submit. The pin was
> **inverted, not deleted**: `tests/test_l1_runs_off_the_publisher_thread.py` (**7 cases, mutation 7/7**,
> control green). The *background* route is still inline — item 48 scoped the offload to the immediate
> route, and the pin's last case fixes that boundary.
> ⚠️ **Two instruments were wrong before the code was.** My `DELEGATION.md` insert asserted the file was CRLF
> and failed — but the file **is** 100% CRLF (211 CRLF, 0 bare LF); I had read it in *text mode*, where
> universal-newline translation makes `count("\r\n")` necessarily 0. **Measure newlines in bytes.** And a
> planned register claim ("`PushEvent` can block up to `timeout_seconds = 20`") was **false** — no such
> constant exists in `grpc_server.py`; the measured fact is `PushEvent` → `publish` at `:185`, synchronous. A
> register row is a claim about the code: **re-measure every line number after an edit** (my own comment moved
> `_L1_IMMEDIATE_EVENT_TYPES` from ~808 to **826**, shifting everything below it).
> ⚠️ **A template that looks tracked may be ignored**: `.env.production.example` matches `.gitignore:57`
> (`.env.*`, exception only `!.env.example`), so it is **not in HEAD** and my edit to it is local-only. The
> tracked carrier is `docs/ubuntu-production.md`. Recorded as §4 item 50.
> ✅ **Fixed 2026-10-06 (cycle 62, §4 item 50 branch ①)**: `!.env.production.example` was added to
> `.gitignore`, so the template **is** tracked now, and the real production host it carried was replaced
> with `example.com` (a template should be generic, and this repo is public). `git show
> HEAD:.env.production.example` resolves instead of failing.

> **The L1 key requirement is now a class-level pin, and the dead intake classes are pinned too (2026-10-05): `2269 passed / 8 skipped`**
>
> Cycle 19 fixed *one* instance -- `TYPESAFE_API_KEY` was missing from `.env.example`. Measuring the class
> before pinning it: `config/llm.yaml` declares 12 profiles whose `api_key_env` is one of **three** distinct
> names (`LLM_API_KEY`, `LLM_VISION_API_KEY`, `TYPESAFE_API_KEY`), and after the fix all three are present.
> New pin `tests/test_every_required_api_key_is_documented.py` (**4 cases, mutation 3/3**, control green)
> parses the shipped profiles and requires each key to appear in `.env.example` as an **assignment line**
> (`KEY=`) -- a *mention inside a comment* does not count, which is the difference between "the template tells
> you the key exists" and "the template sets it". (The first draft used a plain substring test; the comment
> above the assignment contains the key name, so deleting just the assignment line would **not** have failed
> it. The control `test_the_assignment_check_rejects_a_comment_only_mention` pins that distinction.)
> New pin `tests/test_intake_classes_are_constructed_nowhere.py` (**3 cases, mutation 3/3**) measures
> *construction* (`ast.Call` with a bare `Name` callee), not mentions: `IntakeRouter` / `IntakeClassifier` /
> `IntakeDeduplicator` are re-exported by `aegis_ai.intake` and built **nowhere** in `src/`, while `L1Router`
> (`runtime.py:1272`) is the live control. Both pins also assert the *other* half -- the classes still exist
> and are still exported, and the keys the config requires are still declared -- so a rename or deletion comes

>
> **Update (2026-10-08, cycle 102):** the owner took §4 item 47's branch ①, so the v1 intake
> path -- `IntakeRouter` / `IntakeClassifier` / `IntakeDeduplicator` and `intake/models.py` -- was
> **deleted**, and the pin above was **inverted** into `tests/test_intake_v1_surface_is_gone.py`
> (**5 cases, mutation 5/5 + a negative control**) rather than kept: its "the classes still exist
> and are still exported" half is false by construction once the classes are gone. The live control
> is now `runtime.py:1273` -- the `1272` written above was correct when cycle 67 renumbered it and
> drifted by +1 in cycle 77, which is exactly the rot this block is dated against.

> **Two recorded asymmetries are now pinned: an unguarded `status_manager` read, and L1 running inline where L2 does not (2026-10-05): `2277 passed / 8 skipped`**
>
> **Item 44.** `dashboard_legacy._runtime_server_status` reads `runtime.status_manager.get_snapshot()` with
> **no** getattr default (`dashboard_legacy.py:227`), so `ui_overview._server_list` -- which calls it
> unguarded at `:2604` -- raises `AttributeError` for a runtime without a `status_manager`, while the sibling
> `_errors` guards the *same* value with `getattr(runtime, "status_manager", None)` + `hasattr` (`:1952`), and
> so does `_status_snapshot` (`:2672`). The correct pattern therefore already exists twice in the module and
> the bare read is the single outlier. Cycle 18's pin had to monkeypatch `_runtime_server_status` to isolate
> the Android path (`test_ui_overview_failures_are_named.py:140-145`); the new pin
> `tests/test_server_list_requires_a_status_manager.py` (**5 cases, mutation 3/3**) records the *reason* --
> it asserts the raise for both functions, a control (with a `status_manager` present `_server_list` returns a
> list, so the raise is caused by the missing attribute), and the asymmetry (`_errors` survives).
> **Item 48.** L1 runs **inline on the publisher's thread**: `EventBus._notify_subscribers`
> (`src/event_bus.py:234`) calls handlers synchronously, `_evaluate_immediate_event` (`runtime.py:1725`) calls
> `_run_l1_pipeline_for_event` directly (`:1562`), and that awaits `router.observe(...)` -- the L1 LLM
> round-trip. The gRPC `PushEvent` handler (`grpc_server.py:169` -> `publish` at `:185`) is one publisher, so
> a remote push blocks for the whole call. **L2 was already moved off** (`_submit_background_l2`,
> `runtime.py:792`, whose docstring records exactly this); there is no `_submit_background_l1`. The new pin
> `tests/test_l1_runs_inline_on_the_publisher_thread.py` (**3 cases, mutation 3/3**) measures the *asymmetry*
> by AST: the L2 submitter exists, the L1 one does not, and the immediate handler calls the pipeline directly
> (no `submit`). Both pins fail if the recorded fix is applied, so the record moves with the code.
> ✅ **Fixed 2026-10-06 (cycle 64, §4 item 48 branch ①)**: L1 no longer runs inline on the publisher's thread — see
> the correction under "(3)" above. The pin named here was **renamed and inverted** to
> `tests/test_l1_runs_off_the_publisher_thread.py` (**7 cases, mutation 7/7**, control green), and the
> immediate route's L1 work now runs on `aegis-background-l1`.

> **The `_server_list` exposure is 4 of 5 call sites, not 1 (2026-10-05): `2280 passed / 8 skipped`**
>
> Cycle 21 pinned the unguarded `status_manager` read at one site. Measuring the *exposure* generalises it:
> `web/ui_overview.py` calls `_server_list` from five enclosing functions, and only one wraps the call in a
> `try` with an `except` -- `_core` (725), `_attention` (769), `_connection` (848) and `_servers` (1651) are
> unguarded; `_errors` (1977) is guarded. All four unguarded callers are **registered sections** in the
> `sections` dict (`:41`, `:42`, `:56`, `:57`), so they are reachable: a runtime without a `status_manager`
> raises `AttributeError` in four sections while `_errors` survives on the same runtime.
> ⚠️ **The module contradicts its own stated intent.** `_errors`' guard carries the comment "Raw StatusManager
> data remains a usable fallback for **minimal runtimes** and focused tests that do not install all dashboard
> managers" -- so 4 of the 5 call sites break the contract that comment declares. Recorded as §4 item 51,
> generalising item 44.
> New pin `tests/test_server_list_call_sites_are_guarded_or_recorded.py` (**3 cases, mutation 3/3**) records
> the **exposure map** rather than one call: it asserts the set of unguarded enclosing functions *equals* the
> recorded set, so guarding a site or adding a new unguarded one turns it red and the record moves with the
> code. The control is that the guard detector is not vacuous -- on a synthetic source it reports `try/except`
> as guarded and **`try/finally` as not** (a `finally` swallows nothing).

> **A duplicate audit `entry_id` vanishes with no row, no exception and no record (2026-10-05): `2287 passed / 8 skipped`**
>
> `AuditLog._insert_record` (`audit/audit_log.py:245`) issues `INSERT OR IGNORE INTO audit`. `OR IGNORE` already absorbs the very constraint violation that the `except sqlite3.IntegrityError: pass` beneath it names, so a second record with an existing `entry_id` produces **no row, no exception and no log line** (measured: `count() == 1` after two appends of the same id). `append` (`:291`) writes to `self._entries` unconditionally (`:321`), so the in-memory reader `list_recent()` keeps reporting the dropped record while `count()` / `read_all()` deny it -- **two readers of the same audit log disagree**.
> ⚠️ **Reachable from outside the process.** The gRPC `WriteAuditLog` (`grpc_server.py:405`) passes the **client-supplied** `record_id` straight into `entry_id` (`:414`) and returns `code=0 "ok"` either way (measured: two calls with the same `record_id` both return ok, and the table gains exactly one row). Recorded as §4 item 52; behaviour unchanged -- reject / merge / announce is an owner call.
> New pin `tests/test_audit_duplicate_entry_ids_are_announced.py` (**7 cases, mutation 4/5**).
> ✅ **Branch ② executed (2026-10-06, cycle 61): the drop is now announced.** `_insert_record` captures the cursor and, when `cursor.rowcount == 0`, emits a `logger.warning` naming the dropped `entry_id`. `OR IGNORE` is kept, so the row is still dropped and the two readers still disagree — branch ③ was **not** taken. The pin was renamed `…_are_announced.py` and its central case now asserts the warning; mutations **4/5** (M5 is a no-op control that survives on purpose). §4 item 52 closed.
> ⚠️ **The first version of that pin was too weak, and the harness caught it.** It asserted only that `append` did not raise -- which a plain `INSERT` plus the swallowing handler satisfies just as well, so the mutation turning `OR IGNORE` into `INSERT` **survived every case in the file**. The handler's *execution* is now measured with a line tracer (both line numbers read from the module's own AST), with `execute_line in executed` as the non-vacuity control. The 5th mutation (`pass` -> `raise` inside the handler) **survives on purpose**: its survival *is* the evidence that the handler is dead while `OR IGNORE` stands.
> Also repaired `DELEGATION.md` §4, which was rendering as **eight** tables: 7 stray blank lines inside the register, plus three rows with the wrong cell count (row 17 an unescaped `|` inside a code span, row 40 an unclosed 4th column, row 42 a stray empty 5th cell). It is now one contiguous 52x4 table, verified as pure CRLF + one run of 1..52 + every row equal to the header's cell count.
> **The register's citations in files that were *not* shifted were rotten too (2026-10-05): `2287 passed / 8 skipped`** -- the count is **unchanged** because this cycle touched **no code and no test**: `DELEGATION.md` only (+9/-8). Cycle 24 repaired the `runtime.py` citations that the cycle-19 comment had shifted by +18; this cycle swept the *remaining* suspects, which live in files that were never shifted. Method: resolve each `path.py:NNN` against the two roots the register actually uses (`ai-server/src/aegis_ai/`, `ai-server/src/`) and flag any citation whose named neighbour is absent from the cited line, then measure each flag individually -- what the line *is* versus what the row *claims*. **6 citations were rotten**, and the largest error was not a shift but a *different statement*: `autonomous_loop.py:1092-1099` -> `:1254` (3 occurrences, **162 lines away**) -- the range named an `l2_result` assignment while the row claimed the `approval_decisions` supply site. The rest: `manager_routes.py:906`->`:911` (906 is `except Exception as e:` inside `presentation_dismiss`), `manager_routes.py:361`->`:371` (361 is the `/api/memory/search` route), `context_builder.py:203`->`:206` (203 initialises `events`), `dashboard_legacy.py:226`->`:227` (226 is **blank**), `dashboard_legacy.py:1372`->`:1374` (the `api_memory_reload` tombstone).
> ⚠️ **The scanner's other 20 flags are false positives, in two shapes worth knowing**: (a) the row names a **callee** while citing the **call site** (`scheduler.py:75`, `personal_ai/hooks.py:367`, `intake/l1_router.py:160`, `llm/gateway.py:162-169`, `tests/*:NNN`) -- a citation is not a claim about one identifier; (b) a **basename that exists more than once** resolves to the wrong file (`main.py:27` and `dashboard.py:13` are correct under `aegis_ai/`, but the scan picked `aegis_agent_server/main.py` and `notification/channels/dashboard.py`) -- a basename-only citation is ambiguous *by construction*. Verification: every corrected citation was checked to land on a line that names the cited thing, and the register re-measured as pure CRLF + one contiguous run of 52 + 4 cells in every row. Deferred, with its size measured: **31 bare `:NNN` refs** (a line number with no filename) are a distinct surface that no scanner can resolve. **Swept the same day**: of the 31, **one is not a line ref at all** (`:99` is `DISPLAY=:99`), **25 measured correct**, **3 rotten** (`runtime.py:1764`->`:1792`, `runtime.py:1020`->`:1038`, `grpc_server.py:191`->`:185`). The 2 left (item 26's `:917`/`:909`) are line numbers inside a **done** row's "as found" text -- historical, and now labelled so in the note.
> **AGENTS.md carried a *second copy* of the register's citations, and the +18 fix missed it (2026-10-05): `2287 passed / 8 skipped`** -- unchanged again, doc-only. Sweeping this file's 53 file-qualified citations found **13 corrections, and 9 of them were exactly +18** (`runtime.py:880`->`:898`, `:977`->`:995`, `:979`->`:997`, `:1020`->`:1038`, `:1053`->`:1071`, `:1651`->`:1669`). That is the same rot cycle 24 repaired **in the register only** -- the citations live in two documents, and fixing one copy left the other stale: **"I fixed the one place" is not a sweep.** The other 3: `manager_routes.py:361`->`:371` (361 is the `/api/memory/search` route), `dashboard_legacy.py:1372`->`:1374` (the tombstone), `dashboard_legacy.py:226`->`:227` (226 is **blank**). Plus one disambiguation: `factory.py:38` -> `memory/factory.py:38` (`factory.py` exists under both `llm/` and `memory/`; only the latter constructs `ChromaSemanticMemory`).
> ⚠️ **The corrections had to be line-targeted, not global.** This file's own cycle-25 note contains the *old* numbers as an old->new mapping, so a global replace would rewrite `:1020`->`:1038` into `:1038`->`:1038` -- **a note that records a fix must not be rewritten by the next fix.** Every correction was then checked to land on a line that names the cited thing. Residue: 7 flags remain, all expected -- 5 are that note's own mapping, 1 is a set *declaration* cited for a member (`runtime.py:826` for `browser.discovery`), 1 cites a function name where the line carries the route path (`dashboard_legacy.py:1374`).
> ✅ **Fixed 2026-10-06 (cycle 67, §4 item 70)**: the drifted `runtime.py` citations in the notes
> above were renumbered to their measured lines. Every one was **right when written** -- the drift is
> the lines cycles 19-66 inserted above them, and it is consistent per note: `:995`->**1163**,
> `:997`->**1165**, `:1038`->**1206**, `:1071`->**1239**, `:1104`->**1272**, `:1557`->**1725** and
> `:1669`->**1837** all moved by exactly **+168**; `:898`->**1062** by **+164**; `:983`->**1146** by
> **+163**; `:732`->**792** by **+60**; `:276`->**285** by **+9**. Each new number was checked to land
> on a line that **names the cited thing** (`Identity(`, `ContextBuilder(`, `SemanticMemory(`,
> `NotificationManager(`, `L1Router(`, `DesireSystem(`, `settings.json`,
> `def _audit_llm_profile_health`, `def _evaluate_immediate_event`, `def _submit_background_l2`).
> ⚠️ **Five citations were deliberately NOT touched**: the ones that *record* an earlier fix and carry
> old->new mappings or a false-positive census (the `runtime.py:826` mapping and residue notes, and the
> `:1764` / `:1020` / `:880` census). Rewriting those would destroy the record -- the trap this file
> already warns about in the note above.
> ⚠️ **This will rot again** -- a bare `:NNN` is not durable. The durable form is `runtime.py::_build_runtime`
> (already used 7 times in this file), and it is now pinned by `tests/test_doc_citations_resolve.py`.
> Call-site citations cannot adopt it without losing precision (four of the eleven point into
> `_build_runtime`), so they stay as lines; that trade-off is recorded in `DELEGATION.md` §4 item 70.
> ✅ **The sweep had a *second* copy, and the placeholder was one of them (2026-10-06, cycle 67 continued)**:
> the first pass renumbered this file and left `DELEGATION.md` alone -- **the same "I fixed the one place is not
> a sweep" trap this file warns about two notes above** -- and the same citations were rotten there. Re-swept
> **both** docs, resolving every `path.py:NNN` against the whole repo (basename-ambiguous names resolved by
> `rglob`, ambiguity reported rather than guessed). **8 live landings were rotten and are renumbered**:
> `autonomous_loop.py:1074`->**1121** (`should_run_l2 = bool(...)`, **+47**, in both docs);
> `llm/gateway.py:162-169`->**168-174** (re-targeted to the `TypeSafeProvider(` construction, so the range no
> longer *starts* on a blank line; in both docs); `grpc_server.py:402`->**405** (`def WriteAuditLog`) and
> `:411`->**414** (`entry_id=request.record_id`), a consistent **+3**, in both docs; `runtime.py:1067`->**1122**
> (the `MockLLMProvider` startup refusal, +55); `runtime.py:1104`->**1272** (`L1Router(llm_gateway=...)`, the
> same **+168** as the first pass).
> ⚠️ **6 landings are *records* and were left alone**: `dashboard_legacy.py:226` and `llm/gateway.py:162-169`
> in this file's two censuses and `DELEGATION.md`'s copy of them -- their own text *is about* the staleness
> ("226 is **blank**"). A **§5 closed row**'s number was **labelled, not renumbered** (item 26's `:917`/`:909`
> precedent): it now reads "**当時** `:1053`、**現在** `:1239`".
> ⚠️ **The durable form was itself written as a placeholder, and the new pin read it as a citation.** The
> pin failed on the placeholder I had written for the durable form -- my own prose, parsed as a citation. That
> is the guard working (a guard that reacts to the document's own text is alive), and the fix is to write a
> **real** example, never to weaken the guard: the sentence now cites `runtime.py::_build_runtime`. It stood in
> **four** places -- three in `DELEGATION.md`, one here -- and the first pass fixed only this file's.
> ⚠️ **A set-typed pin collapses duplicates into one failure, so its count is not a census**: one
> unresolvable `(path, symbol)` pair is reported **once** however many times it appears. Fix by *string*, count
> by *set* -- and sweep by *claim*, which is how the other two copies were found.
> ⚠️ **The surface is wider than these two files, and is now measured**: sweeping *every* maintained `*.md`
> (**113** files) finds **53** blank/out-of-range landings -- `PROJECT_STATUS_REVIEW.md` 15, `BUG_REPORT.md` 13,
> `AGENT_PROGRESS.md` 8, `docs/improvement-review.md` 5, `docs/jev-l1-verification-2026-10-02.md` 4,
> `IMPROVEMENT_PROPOSAL.md` 2, and the 6 records here. Most sit in **dated snapshots** and in
> `AGENT_PROGRESS.md`'s explicit old->new mapping table, i.e. they are records -- but that adjudication is
> **not** done, so it is recorded as **§4 item 72**, not swept. (Including the frozen plan archives `.omo/`
> and `.mimocode/` the count is **164**; those are archival by construction and are excluded.)
> **AGENTS.md's *bare* `:NNN` refs rotted too, and the same claim has a *third* copy (2026-10-05): `2287 passed / 8 skipped`** -- unchanged, doc-only. Cycle 27 swept this file's *file-qualified* citations; a **bare** `:NNN` (a line number with no filename) is a separate surface, because no scanner can resolve it -- the owning file has to be inferred from the sentence. Of **30** substantive bare refs, **25 measured correct** and **5 were rotten**: `grpc_server.py:191`->`:185` (**3 occurrences in this file alone** -- `publish` is a single line at 185, and 191 is the closing paren of `PushEventResponse(`) and `context_builder.py:722`/`:759` -> `:750`/`:787` (**+28**; both land on the two `available_capability_ids` *token-accounting* reads, one in `_recalc_chars` and one in `_annotate_usage`). The 31 bare refs inside this file's own dated notes are **records** -- old->new mappings -- and were left alone.
> ⚠️ **A bare ref's owning file is the note's *subject*, not the file named last.** The `:722`/`:759` pair follows an explicit `llm_task_interpreter.py:367-370` in the *same sentence*, but `llm_task_interpreter.py` is **450 lines** -- the refs belong to `context_builder.py`, the paragraph's subject. That is how a bare ref rots *unresolvably*: the reader must reconstruct an inference the author never wrote down.
> ⚠️ **The `:722`/`:759` claim had a *third* copy.** `PROJECT_STATUS_REVIEW.md:14` stated the same fact (`ctx.available_capability_ids` is read only for token accounting `:722`/`:759`); it is corrected there too. So one claim lived in **three** documents, and the "second copy" cycle 27 found was not the last: **after repairing a citation, grep every `*.md` for the *claim*, not just for the string.**
>
> **The event-driven core is built — and the test-count copies had diverged (2026-10-06): `2540 passed / 8 skipped`** — measured 2540 / 8 / 0 (2548 collected, 529.03 s); marker-selected: egress **314 / 1 / 315 marked**, non-egress **2226 / 7 / 315 deselected**, and the three selections reconcile exactly (`2226 + 314 = 2540`, `7 + 1 = 8`, `315 + 2233 = 2548 = 2540 + 8`).
> The **+4** is the event-driven-core pin growing **6 → 10** cases when branch ① of `DELEGATION.md` §4 item 24 was executed (the core is now constructed, subscribed **and consumed**); nothing else moved and egress is unchanged.
> ⚠️ **This block repairs a divergence, not just a number.** The copies that must move together held **three different values**: `PROJECT_STATUS_REVIEW.md` §0 and §1.1 said **2259** (2026-10-04), this list said **2287** (2026-10-05), and the verification skill §1 said **2259** (cycle 18) — against a measured **2540**. The drift is not "nobody updated them" but "**each copy stopped on a different day**". Recorded as `DELEGATION.md` §4 item 69.
> **L1 now runs off the publisher's thread, mirroring L2 (2026-10-06): `2544 passed / 8 skipped`** — measured 2544 / 8 / 0
> (2552 collected, 546.04 s); marker-selected: egress **314 / 1 / 2237 deselected**, non-egress **2230 / 7 / 315 deselected**,
> and the three selections reconcile exactly (`2230 + 314 = 2544`, `7 + 1 = 8`, `315 + 2237 = 2552 = 2544 + 8`).
> **The +4 is the pin itself**, and nothing else moved: `DELEGATION.md` §4 item 48 branch ① was executed, so the pin was
> **inverted** — `tests/test_l1_runs_inline_on_the_publisher_thread.py` (3 cases) became
> `tests/test_l1_runs_off_the_publisher_thread.py` (**7 cases, mutation 7/7**, control green). The 4 new cases carry no
> marker, which is why egress is unchanged at 314 / 1.
> ⚠️ **The four copies were moved in the same commit this time.** The block above records the *opposite* outcome — three
> different values across four copies. The rule it recorded (a change that moves the count moves all four copies together)
> was applied from the start here.
> **Production now refuses to start an L1 it cannot authenticate (2026-10-06): `2554 passed / 8 skipped`** — measured
> 2554 / 8 / 0 (2562 collected, 524.86 s); marker-selected: egress **314 / 1 / 2247 deselected**, non-egress **2240 / 7 / 315 deselected**,
> reconciling exactly (`2240 + 314 = 2554`, `7 + 1 = 8`, `315 + 2247 = 2562`).
> **The item-45 partition is pinned by number, and one false copy was corrected (2026-10-06): `2555 passed / 8 skipped`** — measured
> 2555 / 8 / 0 (2563 collected, 569.3 s); marker-selected: egress **314 / 1 / 2248 deselected**, non-egress **2241 / 7 / 315 deselected**,
> reconciling exactly (`2241 + 314 = 2555`, `7 + 1 = 8`, `315 + 2248 = 2563`). ⚠️ **The first run of this cycle was not usable**: it reported
> 2551 / 10 / 0 with 2 ERRORS in `tests/agents/test_tool_bridges.py` (that module was deleted 2026-10-08 with the `tools/bridges/` package — `DELEGATION.md` §4 item 53), because that harness passed a minimal env instead of inheriting
> `os.environ`; it also created an untracked `%SystemDrive%` junk tree. Re-run with an inherited env: 0 errors, no junk. A harness is part
> of the measurement.
> **The +10 is the new pin exactly**, and no existing case moved. `DELEGATION.md` §4 item 46 branch ①:
> `_require_l1_api_key_in_production` stops a production start whose L1 profile has no key, because an
> unauthenticated L1 still starts and then escalates **every** event. No new flag was added — the gate is
> the `AEGIS_RUNTIME_MODE=production` signal `_build_runtime` already fails fast on (MockLLMProvider) and
> `docker_entrypoint.main` uses (auth mode / session secret). Scope is the one profile L1 uses,
> discovered from `llm/layer_profiles.py`; the other cloud profiles are legitimately unconfigured, so a
> fail-fast over all of them would refuse a correct production start. Pin
> `tests/test_l1_requires_its_key_in_production.py` (**10 cases, mutation 8/8**, control green).
> CI is unaffected: `AEGIS_RUNTIME_MODE` defaults to `development` and appears nowhere else in the repo
> except `.env.production.example` — the pin measures that premise instead of trusting it.
> **The register's drifted citations were renumbered in *both* copies, and the record's own placeholder was a citation (2026-10-06): `2558 passed / 8 skipped`** — measured
> 2558 / 8 / 0 (2566 collected, 560.15 s); marker-selected: egress **314 / 1 / 2251 deselected**, non-egress **2244 / 7 / 315 deselected**,
> reconciling exactly (`2244 + 314 = 2558`, `7 + 1 = 8`, `315 + 2251 = 2566`). **The +3 is the new pin exactly**:
> `tests/test_doc_citations_resolve.py` (**3 cases, mutation 5/5**, control green) resolves every **symbol-anchored citation** in
> `AGENTS.md` and `DELEGATION.md` — **28 distinct** (the union; the per-document sum is 33 because the docs share five). It also caught two
> citations with an *incomplete path* (`autonomous_loop.py` -> `autonomous/autonomous_loop.py`, and a bare
> `test_mind_persistence_failures_are_named.py` -> `tests/...`); the symbols themselves were already right. No source file was touched, so
> egress is unchanged at 314 / 1.
> ⚠️ **The pin failed on its own record first.** The durable form was written as a placeholder and the pin parsed it as a citation; it
> stood in **4** places (3 in `DELEGATION.md`, 1 here) and the pin reported it **once** — **a set-typed pin's failure count is not a
> census**. The fix was to write a real example (`runtime.py::_build_runtime`), never to weaken the guard.
> ⚠️ **The four copies moved together again**: `PROJECT_STATUS_REVIEW.md` §0 and §1.1, this list, and the verification skill §1 all carry
> **2558**. The cycle-67 body is the dated block above (item 70's second pass, the 8 renumbered landings, and §4 item 72).
> **Two of the three event-driven core members are constructed but never read (2026-10-06): `2560 passed / 8 skipped`** — measured 2560 / 8 / 0 (2568 collected, 578.65 s); marker-selected: egress **314 / 1 / 2253 deselected**, non-egress **2246 / 7 / 315 deselected**, reconciling exactly (`2246 + 314 = 2560`, `7 + 1 = 8`, `315 + 2253 = 2568 = 2560 + 8`). **The +2 is the event-driven-core pin growing 10 -> 12 cases**: `runtime.py::_build_runtime` constructs `TriggerEngine` (`runtime.py::_build_runtime@1813`), `Scheduler` (`runtime.py::_build_runtime@1817`) and `EventView` (`runtime.py::_build_runtime@1818`), but `src/` reads `.trigger_engine` **once** (`getattr(runtime, "trigger_engine", None)`, `runtime.py::_create_autonomous_loop@1930`) and `.scheduler` / `.event_view` **zero** times (control `.event_manager` **24**). Constructing an object is not consuming it.
> ⚠️ **The claim lived in the pin's own header as *prose* for two cycles and nothing checked it** — the `EventView` half was recorded nowhere. The new tests assert the unconsumed set by **equality**, with the `getattr`-only `TriggerEngine` as the positive control proving the scanner sees the string form. Recorded in `DELEGATION.md` §4 item 24 col 3 and §5.
> ⚠️ **The four copies moved together again**: `PROJECT_STATUS_REVIEW.md` §0 and §1.1, this list, and the verification skill §1 all carry **2560**.
> **`Scheduler` is starved, not unconsumed -- and the record said the wrong thing (2026-10-06): `2562 passed / 8 skipped`** — measured 2562 / 8 / 0 (2570 collected, 580.03 s); marker-selected: egress **314 / 1 / 2255 deselected**, non-egress **2248 / 7 / 315 deselected**, reconciling exactly (`2248 + 314 = 2562`, `7 + 1 = 8`, `315 + 2255 = 2570 = 2562 + 8`). **The +2 is the event-driven-core pin growing 12 -> 14 cases.** "No consumer" was the wrong phrase: a consumer *is* written — `ContextBuilder.__init__(scheduler=...)` stores `self._scheduler` and `context_builder.py:268` reads `get_due_tasks()`, behind `if self._scheduler:` — but `scheduler=` is passed **zero** times in `src/`, so the guard is always false. The path is dead **twice**: `Scheduler()` is also built empty, since `create_default_tasks()` is called nowhere, so even a wired scheduler returns `[]`. The `QuietHoursManager()` shape (§4 item 35).
> ⚠️ **The fix is a behaviour change, so it is recorded and not executed**: wiring it would add `pending_tasks` lines to every prompt. Pinned by equality on the composition root's `ContextBuilder` kwargs and on the zero call sites, **mutation 5/5**, control green.
> ⚠️ **The four copies moved together again**: `PROJECT_STATUS_REVIEW.md` §0 and §1.1, this list, and the verification skill §1 all carry **2562**.
> **`ToolBroker`'s event publication is silently disabled — the composition root builds it before the `EventManager` exists (2026-10-06): `2565 passed / 8 skipped`** — measured 2565 / 8 / 0 (2573 collected, 574.38 s); marker-selected: egress **314 / 1 / 2258 deselected**, non-egress **2251 / 7 / 315 deselected**, reconciling exactly (`2251 + 314 = 2565`, `7 + 1 = 8`, `315 + 2258 = 2573 = 2565 + 8`). **The +3 is the new pin exactly.** `ToolBroker.__init__` takes `event_manager` and stores `self._event_manager`, but `runtime.py::_build_runtime@1111` passes **7 kwargs** and not that one — because `EventManager` is created at `runtime.py::_build_runtime@1222`, 111 lines later. Two branches then die **silently**: `_publish_tool_event` returns early, so `tool.executed` is **never published** (and `personal_data/core.py:71` lists it as a fact-recording trigger); `_observe_recent_event` returns `False`, so a manifest's `check_type: "event"` verification always fails with text that reads as "the event did not happen" rather than "the checker was never armed".
> ⚠️ **The guards are deliberate** — the code handles a `None` manager explicitly, so this is not a crash. The defect is the **silence** (§4 items 37/38's family: an unreadable source looking like an empty one). Recorded as §4 item 74, not executed: wiring it is a behaviour change. **Exposure is latent** — no shipped manifest uses `check_type: "event"`.
> ⚠️ **The four copies moved together again**: `PROJECT_STATUS_REVIEW.md` §0 and §1.1, this list, and the verification skill §1 all carry **2565**.
> **`ToolBroker`'s starved parameters: the omitted population is four, and only `event_manager` has no path (2026-10-06): `2566 passed / 8 skipped`** — measured 2566 / 8 / 0 (2574 collected, 534.90 s); marker-selected: egress **314 / 1 / 2259 deselected**, non-egress **2252 / 7 / 315 deselected**, reconciling exactly (`2252 + 314 = 2566`, `7 + 1 = 8`, `315 + 2259 = 2574 = 2566 + 8`). **The +1 is the new test exactly.** Cycle 71 recorded "the root passes 7 kwargs and not `event_manager`", which reads as if the broker were left with 7 of 11 parameters. Measured: `__init__` takes 11, the root supplies 7, so **4 are omitted** — `delegation_policy`, `repair_manager`, `event_manager`, `capability_health` — and **3 of the 4 are wired after construction** (`tool_broker.set_delegation_policy(delegation_policy)` at `runtime.py::_build_runtime@1284`, `tool_broker.set_repair_manager(repair_manager)` at `runtime.py::_build_runtime@1530`, `tool_broker._capability_health = capability_health` at `runtime.py::_build_runtime@1230`). **Only `event_manager` has no assignment and no setter** — `runtime.py::_build_runtime@1228`'s `journal_projector._event_manager = event_manager` sets the *journal projector's* attribute, a different class. So the defect is not the ordering; it is that three siblings got a post-hoc path and this one did not.
> ⚠️ **The new test pins the effect, not the call site** — an equality on the attributes each setter writes, so an inert setter fails. It pins `event_manager` as an **absence** (no `tool_broker._event_manager =` and no `set_event*`), checking both channels so either route to arming it fails. Mutation **9/9**; the first three mutations were **ineffective, not survived** (M1's anchor matched 3 sites, M5's anchor did not exist, M8 used `EventManager.__new__(...)` so `attr == "__new__"` and the ordering extractor ignored it) — **a surviving mutation is evidence about the mutation too**.
> ⚠️ **The four copies moved together again**: `PROJECT_STATUS_REVIEW.md` §0 and §1.1, this list, and the verification skill §1 all carry **2566**.
> **DeepSeek is permitted as the L2 model, and every layer profile must be reachable (2026-10-06): `2567 passed / 8 skipped`** — measured 2567 / 8 / 0. The owner asked for the DeepSeek key in `.env` and `deepseek-v4-flash` as L2, and for AEGIS to actually run. The key was already the declared `api_key_env` (`LLM_API_KEY`) and `llm.yaml` already declared `l2_default` -> `deepseek-v4-flash`, but `privacy.egress_allowed_hosts` named only `api.typesafe.ai`, so `gateway._get_provider_for_profile` **denied DeepSeek and silently returned Mock** — L2 was declared and inert. The remedy is the one the code itself prints at startup ("Permit them via privacy.egress_allowed_hosts ... if that is intended"), so `api.deepseek.com` was added: the allowlist entry **is** the owner's permission. Measured after: `gate(api.deepseek.com)=allow`, `l2_default` resolves to `OpenAIProvider` (not Mock), and a **live L2 call returned `content='OK'` / `provider_used=openai` / `model_used=deepseek-v4-flash`** (L1 on JEV and L3 answered live too).
> ⚠️ **Widening a pinned allowlist means re-adjudicating every pin that names it, including the negative controls.** Four assertions encoded the old single-host permission: three in `test_egress_gate.py` (the exact list, the sorted reachable set, and the shipped-settings test, renamed `..._permits_exactly_the_intended_hosts`) and one **negative control** in `test_burden_metric_is_judged.py` whose whole job was to prove the allowlist is a filter — it used the `decision` profile, which resolves to DeepSeek, so permitting DeepSeek would have made it pass vacuously. The control moved to `vision_observation`, an external host the allowlist still does not name.
> ⚠️ **New pin: `test_every_layer_profile_is_reachable_under_the_shipped_allowlist`** drives the real resolver and the real gate over L1/L2/L3 and asserts each layer's `base_url` is permitted, with `vision_observation` as the negative control. **Mutation 2/2 KILLED** (drop `api.deepseek.com` from the allowlist; point `l2_default` at the unpermitted vision host), both restored sha256-exact.
> ⚠️ **The four copies moved together again**: `PROJECT_STATUS_REVIEW.md` §0 and §1.1, this list, and the verification skill §1 all carry **2567**.
> **The composition root's own gateway must resolve every layer — and nothing pinned that (2026-10-06): `2569 passed / 8 skipped`** — measured 2569 / 8 / 0 (2577 collected, 462.50 s); marker-selected: egress **317 / 1 / 2259 deselected**, non-egress **2252 / 7 / 318 deselected**. The `+2` is a new egress-marked module, `tests/test_composition_root_resolves_llm_layers.py`.
> ⚠️ **`scripts/verify_llm_layers.py` proves the *layer wiring*, but it builds its own gateway.** The repo's own rule is "composition root, not a bare import", so the new pin boots the real `get_runtime()` and asks **its** gateway: measured `gateway._settings_resolver is runtime.settings_resolver` -> `True`, and each of L1/L2/L3 resolves to a provider built for its declared host (`_base_url == settings.base_url`).
> ⚠️ **The silent half was the wiring, not the resolution.** `LLMGateway._resolve` returns a bare `LLMSettings()` when it has no resolver — every layer would run on defaults with no error — so the pin asserts the gateway's *own* resolution of each layer's profile equals the declared settings, not merely that `_get_provider_for_profile` behaves. The control is **discovered**, not named: it enumerates every profile whose external host the gate denies and asserts no provider is built for it, so permitting that host later cannot leave the control vacuous.
> ⚠️ **Mutation 3/3 killed — and the first M2 was *ineffective*, not survived**: `SettingsStore()`'s default path is the *relative* `config/settings.json`, and tests run with cwd `ai-server/`, so "swap in a default store" changed nothing. Replaced with a store pointed at a missing file (built-in defaults -> the gate denies every external host). Restores used `git checkout HEAD -- <path>` and asserted the file was clean afterwards.
> ⚠️ **Adding an egress-marked file reddened an older pin**: `tests/test_egress_closure.py::test_the_mutation_roster_covers_every_marked_file` asserts the mutation check's `EGRESS_TESTS` roster equals the marked set, so the new module was added to `scripts/verify_egress_tests_catch_regression.py` — the roster's own documented hazard, caught by its own guard.
> **The four copies moved together again**: `PROJECT_STATUS_REVIEW.md` §0 and §1.1, this list, and the verification skill §1 all carry **2569**.

> **The "are all layers live?" tool could print OK over a call it never got -- and the fix is now pinned (2026-10-06): `2571 passed / 8 skipped`** -- measured 2571 / 8 / 0 (2579 collected, 461.31 s); marker-selected: egress **319 / 1 / 2259 deselected**, non-egress **2252 / 7 / 320 deselected**. The `+2` is a new egress-marked module, `tests/test_verify_llm_layers_contract.py`. ⚠️ **The instrument, not the wiring, was the defect**: `scripts/verify_llm_layers.py --live` printed `OK ... answered live` while L3 returned `content=''`. Measured: an empty body is **intermittent and *not* a `max_tokens` effect** (0/20 empty at 32/64/128/256), so the tool now re-issues once and then reports a **WARN** while keeping exit 0 -- the provider *was* reached, which is what proves the wiring, and failing on a model-side hiccup would manufacture false "not operational" readings. The pin drives the real `main()` and doubles only the provider call, so the gate, the resolver and the provider factory stay production code; its control changes one field (`success=False`, `provider_used="mock"`) and must flip the verdict to **exit 1 with three FAIL lines**. **Mutation 3/3 killed plus one deliberate survivor** -- M4 removes the retry and is *expected* to survive: the pin is on the verdict, not on how many times the tool asks.
> **The four copies moved together again**: `PROJECT_STATUS_REVIEW.md` §0 and §1.1, this list, and the verification skill §1 all carry **2571**. The egress mutation figure moved with the roster -- **78 failures** (measured 2026-10-06; it was 76 at the 318-marker baseline, 74 at 305, 62 at 268) -- and the roster's own unmutated run reports **319 passed / 1 skipped**, i.e. the roster covers exactly the marked set.

> **Three audits reported a clean verdict over a population they never read -- and the fix is pinned (2026-10-06): `2576 passed / 8 skipped`** -- measured 2576 / 8 / 0 (2584 collected, 461.06 s); marker-selected: egress **319 / 1 / 2264 deselected**, non-egress **2257 / 7 / 320 deselected**. The `+5` is a new **non-egress** module, `tests/test_audits_refuse_to_pass_over_an_empty_population.py`. ⚠️ **The population is discovered, so it can be empty -- and an empty one audited nothing while printing the same verdict as a clean one** (measured before the fix): capability coverage 128 manifests -> `fail`, 0 -> `rc=0 "pass"`; the secret audit 1267 files -> `pass`, 0 files -> `rc=0 "pass"`; the mock inventory 3901 files -> `fail`, 0 -> `rc=0`. The secret audit is where a false clean costs most, and its population comes from `git ls-files` -- absent in a tarball or a non-git checkout. Each audit now prints the denominator it read and refuses to call a zero population clean, and `audit-v1-completion.py` requires the denominator in the mock report, so the guard propagates instead of stopping at the file. **Mutation 5/5 killed plus one deliberate survivor** (renaming a `schema_version` key survives: the pin is on the verdict and the denominator, not on cosmetic metadata). The control matters as much as the guard -- a real, minimal manifest tree must still pass -- and one mutation was *ill-formed* before it was a mutation: JSON's `true` inside a Python dict died with `NameError` and read as "killed" for the wrong reason.
> ⚠️ **The "four copies" phrasing was loose**: `AGENTS.md` deliberately carries no *live* full-suite total (it says so, and tells you to re-measure), so the **full** count moved in **three** live copies -- `PROJECT_STATUS_REVIEW.md` §0 and §1.1 and the verification skill §1 -- while the **egress deselected** figure moved in two more (`AGENTS.md`'s egress bullet and the skill's egress row), because it counts everything *unmarked* and therefore grows with a non-egress pin.
> **Three readers of the production-blocker report turned "I could not read the population" into "there are no blockers" -- and all three are fixed and pinned (2026-10-06, cycle 81): `2588 passed / 8 skipped`** -- measured 2588 / 8 / 0 (2596 collected, 498.24 s); marker-selected: egress **319 / 1 / 2276 deselected**, non-egress **2269 / 7 / 320 deselected** (the `+12` is a new **non-egress** module, `tests/test_a_missing_blocker_report_is_not_a_clean_report.py`). The asymmetry was *inside each loader*: a report that could not be **parsed** produced a blocker -- the `except`/`catch` synthesised one -- while a report that could not be **found** returned the clean default (`{"blockers": []}` in the Python loader, an empty array in the PowerShell runner, an empty list in the readiness audit). Every consumer counts blockers, so "the control never ran" and "nothing is blocked" were the same value. That includes the dashboard route `/api/production/readiness`, whose report path is **relative**: on a host that has never run the mock audit the answer used to be "0 production blockers". Measured before -> after: absent -> `blockers=0` with no marker -> **`1` + `unreadable=True` + `cause="was not found"`**; valid JSON of the wrong shape (`[1, 2, 3]`) fell past the `isinstance(dict)` guard to the clean default -> **`1`**; unparseable -> 1 (unchanged). A report that *was* read is returned verbatim (the real repo report still reads `blockers=2` / `status=fail`, and `_load_blockers` the same two). The `corrupted` key had no reader and was folded into `unreadable` + `cause`. **Mutation 8/8 killed plus one deliberate survivor**: the PowerShell reader has no pytest pin (CI has no PowerShell), so mutating its absent branch *survives* -- that survival is the recorded coverage gap, not a wrong guard. The harness `py_compile`s each mutation first, so an ill-formed one cannot read as a kill.

> **A gate's verdict did not say what it had skipped -- and both gates now count their checks (2026-10-06, cycle 82): `2597 passed / 8 skipped`** -- measured 2597 / 8 / 0 (2605 collected, 558.32 s); marker-selected: egress **319 / 1 / 2285 deselected**, non-egress **2278 / 7 / 320 deselected**, and the three selections reconcile exactly (`2278 + 319 = 2597`, `7 + 1 = 8`, `320 + 2285 = 2605 = 2597 + 8`). The `+9` is a new **non-egress** module, `tests/test_the_verdict_carries_its_denominator.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2276 -> 2285**. ⚠️ **The defect was in the verdict itself**: `scripts/test-ai-server.ps1` runs four checks and `-SkipMutation` runs three; `scripts/test-all-suites.ps1` runs four and `-SkipAiServer` runs three; both printed the *same* bare `ALL CHECKS PASSED` for the complete and for the reduced run, so the last line -- the line CI and the run records quote -- could not tell a run that skipped the mutation check from one that ran it, and the mutation check is the control that says the egress suite has been *observed* failing. Each gate now appends its own name to `$ran` or `$skipped`, reconciles that census against a declared `$checksTotal`, and prints `ALL <ran>/<total> CHECKS PASSED (skipped: ...)`; a broken census (a check added without bumping the total) exits 1 rather than print a denominator it made up. `scripts/test-beta-real.ps1` carried the same family one layer down -- its browser check was neither passed, failed, nor skipped when the browser did not respond, so `Results: 6 passed, 0 failed` described a run that attempted seven checks; it now counts the browser as skipped and carries the denominator too, with the exit code unchanged (the browser is deliberately best-effort). **Mutation 5/5 killed plus a green control** -- reverting either bare verdict, dropping the skip naming in either gate, uncounting the beta browser path, and deleting a `$checksTotal` all go red, while a comment-only edit stays green; every file was restored byte-exactly. The behavioural proof is a **replay** of each gate's extracted verdict tail on four shapes (complete / reduced / one failed / broken census) -> four distinct lines, because CI has no PowerShell; the pytest pin is therefore *static* (the denominator must appear in the verdict, the verdict must depend on the skipped set, the bare form must not return). ⚠️ **The first version of the guard pinned one script's syntax instead of the property** -- it required the verdict line itself to contain `(skipped: $($... -join`, which is how `test-ai-server.ps1` writes it, while `test-all-suites.ps1` builds a `$reduction` list first, so the pin went red on correct code. ⚠️ **And the first verdict was self-contradictory**: the numerator was `$ran.Count + $skipped.Count`, so a reduced run printed `ALL 4/4 CHECKS PASSED (skipped: mutation check)` -- '4 passed' beside '1 skipped'. The numerator is the checks that *ran*. ⚠️ **The three surviving `ALL CHECKS PASSED` strings are historical, not live** -- `IMPROVEMENT_PROPOSAL.md` (a dated Phase-3 record), `DELEGATION.md` §5 (a run at `ea01d80`), and `build/ci-ai-server.log` (captured output); each was true when written, so they stay. ⚠️ **A stale table found while sweeping**: `docs/testing-real-devices.md` said the `egress` marker selects **233 tests** and that the suite is **1807 tests**; measured 2026-10-06: **320** and **2605** (and `-m pc_local` collects nothing with **2605 deselected**). Corrected in place.

> **The dead-code audit was the one audit outside every accounting -- and it is now inside it (2026-10-07, cycle 83): `2608 passed / 8 skipped`** -- measured 2608 / 8 / 0 (2616 collected, 457.44 s); marker-selected: egress **319 / 1 / 2296 deselected**, non-egress **2289 / 7 / 320 deselected**, and the three selections reconcile exactly (`2289 + 319 = 2608`, `7 + 1 = 8`, `320 + 2296 = 2616 = 2608 + 8`). The `+11` is a new **non-egress** module, `tests/test_the_dead_code_audit_is_inside_the_accounting.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2285 -> 2296**. ⚠️ **Three coupled defects, all measured**: (i) `scripts/audit-dead-code.py` was the **only** `scripts/audit-*.py` that could not fail -- it ended `return 0` while its six siblings end `return 0 if status == "pass" else 1` -- and it printed `dead_or_obsolete=0` over a tree it never walked, i.e. the empty-population family cycle 80 pinned in three siblings **minus one member**; (ii) its reference lookup collapsed **three** outcomes into one blank string -- `rg` exits 1 for "no match", which `run_command` reports as `status="fail"`, the same status it uses when the binary could not be launched at all, so a failed search and a real empty result both rendered as `""`, and the live report had **0 of 5** non-empty reference cells (a blank cell reads as the strongest dead-code claim, "nothing references this file", when nothing was searched -- and `rg` is **declared nowhere** in the repository); (iii) `scripts/audit-production-readiness.py` **discarded** the result (a bare `run_command(...)` statement), so the audit's status was in neither `checks` nor `summary.checks_total` -- the live report had **30 checks and no dead-code id**, while all five siblings contribute two checks each. The audit now counts `files_walked` (`58187` live) and refuses a zero population; the reference column renders "could not run" / "no references found" / the matches as three distinct values and carries `reference_search_failures`; the consumer captures the result into a `dead_code` check plus a `_report_pass` on `dead_code_report.json` that **requires `files_walked`**, so `checks_total` moves 30 -> **32** and the denominator is read, not merely written. **Mutation 13/13 killed** -- dropping the renderer call, re-blanking the failure, collapsing rg's no-match, forcing `status`/`return 0`, discarding the result again, dropping the required field, dropping either check, and dropping `files_walked`/`status`/`reference_search_failures` from the payload or the print all go red; every file was restored byte-exactly. ⚠️ **The first pin went red on correct code, twice for the same reason**: the script name lives inside a *list literal*, not a direct argument, and `_report_pass` takes its check id **positionally**, so scanning `call.args` for a `Constant` and scanning for `{"id": ...}` both missed the call; the pin now walks every string under it. ⚠️ **And one mutation survived the first pin** (`M7`, drop the required population field): the test called `_report_pass(..., ["files_walked"])` *itself*, which proves the function *can* require a field but not that this call site *does* -- a survivor is evidence about the pin, so the call site is now pinned from the source. ⚠️ **A loud failure that nothing counts is the same bypass one layer up**: making the audit able to fail *without* fixing the discard would have been worse than leaving it, which is why all three defects were closed in one cycle.

> **The dashboard's readiness route read a report with no `blockers` list as "0 production blockers" (2026-10-07, cycle 84): `2612 passed / 8 skipped`** -- measured 2612 / 8 / 0 (2620 collected, 465.86 s); marker-selected: egress **319 / 1 / 2300 deselected**, non-egress **2293 / 7 / 320 deselected**, reconciling exactly (`2293 + 319 = 2612`, `7 + 1 = 8`, `320 + 2300 = 2620 = 2612 + 8`). The `+4` are new **non-egress** tests in `tests/test_a_missing_blocker_report_is_not_a_clean_report.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2296 -> 2300**. ⚠️ **Cycle 81 fixed the asymmetry in two of the three readers and left the third**: `load_production_blocker_report` (`ai-server/src/aegis_ai/production_readiness.py`) -- the one the dashboard route `/api/production/readiness` reads -- passed a valid-JSON report with **no `blockers` list** straight through, so `production_blocker_count` read **0**, while `_load_blockers` (the readiness audit) and `run-readiness-report.ps1` both turned the same report into a blocker. Measured 2026-10-07 on one path: `{}` -> **0**, `{"blockers": "nope"}` -> **0**, `{"blockers": null}` -> **0**; the audit's reader said 1 for all three. Cycle 81's own test *docstring* claims the whole family ("a report that is missing, unreadable, not an object, or missing its `blockers` key") but its assertions exercise the missing-key case only for `_load_blockers` -- a claim about a family that one member did not satisfy. The loader now has the same `isinstance(data.get("blockers"), list)` branch, with the cause `has no blockers list`. **Mutation 8/8 killed plus a green control** -- reverting the passthrough, colliding the cause, returning an unreadable-but-empty list, testing key presence instead of the value's type, and drifting *either* Python reader all go red; the `.ps1` wording and literal-count mutations redden too; a comment-only edit stays green; all three files restored byte-exactly. ⚠️ **The strongest new pin is differential, not absolute**: `test_the_two_python_blocker_readers_agree` drives both Python readers over an 8-row table and requires the same blocker/clean verdict, so a future drift in *either* direction reddens -- which the old tests, each pinned to one reader, could not see. ⚠️ **The third reader is still unpinnable** (CI has no PowerShell, and the script will not execute in this sandbox -- the execution policy refuses it), so its pin is **static**: three `production_blocker` literals, and the family's words for the absent and no-`blockers`-list cases -- the shape cycle 82 established. ⚠️ **The old cause test sampled what it claimed to enumerate**: `test_the_three_unreadable_causes_are_named_apart` checked 2 of 3 and used two *different* paths, so its reasons differed by path, not by cause; it now enumerates all four causes on **one** path. ⚠️ **Measured while writing it**: a JSON *parse* failure and an encoding failure share `could not be read` (both reach the `except`), so `is not a JSON object` needs JSON that **parsed** to a non-dict -- `[1, 2, 3]`, not `{not json`. ⚠️ **Recorded, not fixed**: the dead-code audit's population is **58,551** files against the family's **3,906** (it re-implements its own exclude set), but **0** findings come only from the wider set -- and narrowing it to `iter_text_files()` would be *wrong*, since `classify_file` matches `debug_*` regardless of suffix. Live behaviour is unchanged: the shipped report has a `blockers` list (len 2).

> **A readiness check that raised took the whole audit with it -- and the three unguarded ones are now guarded (2026-10-07, cycle 85): `2618 passed / 8 skipped`** -- measured 2618 / 8 / 0 (2626 collected, 470.99 s); marker-selected: egress **319 / 1 / 2306 deselected**, non-egress **2299 / 7 / 320 deselected**, reconciling exactly (`2299 + 319 = 2618`, `7 + 1 = 8`, `320 + 2306 = 2626 = 2618 + 8`). The `+6` are new **non-egress** tests in `tests/test_a_source_reading_check_cannot_abort_the_readiness_audit.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2300 -> 2306**. ⚠️ **`main` evaluates all 32 checks before it writes `readiness_summary.json`**, so an exception inside one check aborts the audit and leaves the **previous** report on disk -- which the dashboard route (`load_production_blocker_report`) and `_load_blockers` then read as fresh. Three of the six source-reading checks called `(ROOT / rel).read_text()` with **no** existence guard (`_dashboard_auth_check`, `_capability_override_persistence_check`, `_mock_provider_reject_check`) while their three siblings guarded with `.exists()`. Measured 2026-10-07 by rebinding `ROOT` to an empty directory and driving all six: the three unguarded ones raised `FileNotFoundError`; the three guarded ones returned a clean `fail` naming the file. A shared `_source_text(rel)` helper now routes every read, so a missing file is a **named** failure. ⚠️ **And the same check returned `evidence=[]` on every branch** -- the only check in the live readiness summary naming nothing it measured; it now names the two files it read. **Mutation 7/7 killed plus a green control** -- reverting each of the three guards, emptying the pass-branch evidence, restoring the inline `(ROOT / rel).read_text(...)`, renaming a member, and adding a *new* source reader all go red, while a cosmetic edit stays green; the target file was restored byte-exactly. ⚠️ **The pin discovers its population from the AST** (zero-argument functions whose body reads a file) and compares it to a declared set, so a new source-reading check cannot be added unguarded without the pins noticing. ⚠️ **And the first version of the pin keyed on one syntax**: discovery looked for `read_text` calls only, so once the fix moved three checks onto `_source_text` they dropped out of the population -- the cycle-83 trap (the script name inside a list literal). Live behaviour is unchanged: all six checks keep their status (all `pass`), the summary stays `fail` / 32 checks / 11 failed, and only `dashboard_auth_required`'s evidence moved, 0 -> 2.

> **The readiness audit's report-pass accepted a report that measured nothing -- four of its six call sites are now required to name a population (2026-10-07, cycle 86): `2625 passed / 8 skipped`** -- measured 2625 / 8 / 0 (2633 collected, 478.90 s); marker-selected: egress **319 / 1 / 2313 deselected**, non-egress **2306 / 7 / 320 deselected**, reconciling exactly (`2306 + 319 = 2625`, `7 + 1 = 8`, `320 + 2313 = 2633 = 2625 + 8`). The `+7` are new **non-egress** tests in `tests/test_every_report_pass_names_a_population.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2306 -> 2313**. ⚠️ **Cycle 80 closed the empty-population family in the *generators*** ("an empty scan is not a clean inventory"), but the readiness audit is the **consumer** that turns those reports into the verdict, and its `_report_pass` accepted a report whose status was `pass` while the report measured nothing. Measured 2026-10-07 with a `{"status": "pass", "overall_status": "pass"}` report carrying **no** population field, at each of the six call sites: `mock_inventory_report`, `capability_coverage_report`, `ui_completeness_report` and `v1_completion_report` all read **pass** (vacuous), while `dead_code_report` (cycle 83) and `android_reconnect_metrics` -- the two that named a field -- correctly read **fail**. Cycle 83 gave exactly one of these a denominator and left the other four behind. The four now require `files_scanned` / `capabilities` / `checks` / `checks` respectively, and the argument is **required**, not defaulted to `None`, so a new call site cannot omit it. **Mutation 7/7 killed plus a green control** -- dropping each of the four fields, re-adding the `None` default, making `_report_pass` ignore the fields, and adding a field-less call site all go red, while a docstring-only edit stays green; the target file was restored byte-exactly. ⚠️ **The population is discovered from the source, not listed** (an AST walk of every `_report_pass(...)` call site), so a new call site is covered without editing the pin. ⚠️ **And one of my own assumptions died on measurement**: the first live-report pin asserted "every shipped report passes" -- but the live `mock_inventory.json` is `fail` (two production blockers), so the invariant is not "every report passes" but "**requiring the population changes no live verdict**", because every shipped report carries its field. Live behaviour is unchanged: the summary stays `fail` / 32 checks / 11 failed and the five `*_report` checks keep their statuses (the four failing reports short-circuit at the status branch before the population is read).

> **The readiness audit's E2E check accepted a `report_dir` it never read -- every E2E read now goes through it (2026-10-07, cycle 87): `2634 passed / 8 skipped`** -- measured 2634 / 8 / 0 (2642 collected, 466.64 s); marker-selected: egress **319 / 1 / 2322 deselected**, non-egress **2315 / 7 / 320 deselected**, reconciling exactly (`2315 + 319 = 2634`, `7 + 1 = 8`, `320 + 2322 = 2642 = 2634 + 8`). The `+9` are new **non-egress** tests in `tests/test_e2e_check_reads_from_its_report_dir.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2313 -> 2322**. ⚠️ `_e2e_check` took `report_dir` as its first argument and **all six call sites passed it**, but the body never used it -- it hard-coded `ROOT / "data" / "reports" / "e2e" / "latest"`. With the default `--report-dir` (`data/reports`) the two agree, so the audit looked fine; with a custom one they do not. Measured 2026-10-07: a `report_dir` holding a valid `summary.json` while `ROOT` holds none returned **"Missing E2E result for docker_core"** -- the argument was ignored, disagreeing with `_report_pass`, which honours it. The fix routes every read through `report_dir / "e2e" / "latest"` -- **byte-identical for the default**, correct for a custom one. **Mutation 5/5 killed plus a green control** -- reverting to the hard-coded `ROOT`, dropping the `e2e/latest` suffix, removing the standalone-override loop, removing the `id` guard, and making one call site pass `ROOT` all go red; the target file was restored byte-exactly. ⚠️ **The pin reads the dead parameter's return through the AST** (the body must contain the Name `report_dir` and not `ROOT`) -- the explanatory comment that *names* `ROOT` cannot satisfy it, because a mention is not a reader. ⚠️ **Live behaviour is unchanged**: the audit was re-run end-to-end and the six E2E statuses, `overall_status` (`fail`), 32 checks, 11 failed and 2 blockers are all identical (the writes were restored). ⚠️ **A second defect was measured and recorded, not fixed**: the second loop (a standalone `docker-core.json` overriding the `summary.json` entry) has **no freshness guard** -- a summary `fail` plus a standalone `pass` returns `pass`. The precedence is pinned as-is; changing it is an owner decision.

> **The readiness audit coerced report numbers with a bare `int()` -- a malformed value could abort the whole audit (2026-10-07, cycle 88): `2667 passed / 8 skipped`** -- measured 2667 / 8 / 0 (2675 collected, 480.32 s); marker-selected: egress **319 / 1 / 2355 deselected**, non-egress **2348 / 7 / 320 deselected**, reconciling exactly (`2348 + 319 = 2667`, `7 + 1 = 8`, `320 + 2355 = 2675 = 2667 + 8`). The `+33` are new **non-egress** tests in `tests/test_a_malformed_soak_number_does_not_abort_the_audit.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2322 -> 2355**. ⚠️ `_display_soak_check` coerced three report fields with `int(data.get(...) or 0)` and `_e2e_check` a fourth with `int(match.get("duration_ms") or 0)`. A **truthy, non-numeric** value raised -- measured: `"abc"` -> `ValueError`, `[1, 2]` -> `TypeError`, `{"a": 1}` -> `TypeError`, `failure_count="x"` -> `ValueError`. `main` evaluates every check *before* it writes `readiness_summary.json`, so the exception leaves the **previous** report on disk -- the cycle-85 shape, reached through a *value* rather than a missing file. The fix adds `_as_int`, which reproduces `int(value or 0)` **exactly for every input that did not raise** and returns `None` only where it did; the three soak inputs treat `None` as a malformed measurement (a clean `fail` naming the field) and `duration_ms` is metadata, so it collapses to `0` with the verdict unchanged. **Mutation 7/7 killed plus a green control**; the target file was restored byte-exactly. ⚠️ **A differential pin keeps the pre-fix formula as the oracle**, so "no verdict changes for well-formed input" is measured, not asserted. ⚠️ **The family is closed**: no `int(...)` in the audit reads a mapping any more (an AST walk asserts the empty set). ⚠️ **Reachability is latent, and recorded as such**: today's writers emit numbers, so the defect needs a hand-edited, partially-written or third-party report to fire -- but its consequence is the whole audit. Live behaviour is unchanged (`fail` / 32 / 11 / 2 blockers, writes restored).

> **The readiness audit accepted a report that measured *zero* as clean -- a zero count is now empty, a zero *metric* is not (2026-10-07, cycle 89): `2706 passed / 8 skipped`** -- measured 2706 / 8 / 0 (2714 collected, 466.10 s); marker-selected: egress **319 / 1 / 2394 deselected**, non-egress **2387 / 7 / 320 deselected**, reconciling exactly (`2387 + 319 = 2706`, `7 + 1 = 8`, `320 + 2394 = 2714 = 2706 + 8`). The `+39` are new **non-egress** tests in `tests/test_a_zero_population_is_not_a_clean_report.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2355 -> 2394**. ⚠️ Cycle 86 gave `_report_pass` a required population field, but its emptiness test was `data.get(field) in (None, "", [])` -- and a **zero count is none of those**, so `{"status": "pass", "files_scanned": 0}` read as **clean**, as did `capabilities: 0`, `checks: 0` and `files_walked: 0` -- a report that measured *nothing*, exactly what the empty-population family (cycles 80/83/86) exists to catch. The test is now `not data.get(field)`, so `0`, `False` and `{}` are empty too. ⚠️ **Tightening is wrong if it flips a correct verdict**: the live `android-real.json` carries `heartbeat_failure_count: 0`, which is the *good* outcome, so folding it into the population list would turn a correct `pass` into a `fail`. Hence two distinct kinds -- `required_fields` (a *population*; empty = falsy) and a new keyword-only `present_fields` (a *metric*; zero is legitimate). The android call site now requires `["checks"]` and merely *carries* `reconnect_count` / `heartbeat_failure_count`. **Mutation 7/7 killed plus a green control**; the target file was restored byte-exactly. ⚠️ **Live behaviour is unchanged**: the audit was re-run end-to-end and all 32 checks and both `summary.json` / `readiness_summary.json` are byte-identical (writes restored) -- the live `android-real.json` carries a non-empty `checks` list (7 entries) and `heartbeat_failure_count: 0`, so the old and the new logic both pass it.

> **Every report read and write in the readiness audit now honours --report-dir -- seven sites hard-coded ROOT (2026-10-07, cycle 90): `2729 passed / 8 skipped`** -- measured 2729 / 8 / 0 (2737 collected, 462.67 s); marker-selected: egress **319 / 1 / 2417 deselected**, non-egress **2410 / 7 / 320 deselected**, reconciling exactly (`2410 + 319 = 2729`, `7 + 1 = 8`, `320 + 2417 = 2737 = 2729 + 8`). The `+23` are new **non-egress** tests in `tests/test_every_report_read_honours_the_report_dir.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2394 -> 2417**. ⚠️ `main` runs its sub-audits with `--report-dir <report_dir>` and `_e2e_check` (cycle 87) reads `<report_dir>/e2e/latest` -- but seven sites still hard-coded the tree to `ROOT`: the `pc_real` and `android_real` reads (two call sites), the `summary.json` / `summary.md` **write**, `_secrets_check` (whose sub-audit `main` had just told to write into `<report_dir>`), `_capability_override_persistence_check` and `_display_soak_check`. Measured with a custom `--report-dir`: the three checks' `evidence` named the ROOT tree, `<custom>/e2e/latest/summary.json` was never written, and ROOT's `summary.json` / `summary.md` were **rewritten** -- a sandbox run clobbered the operator's real E2E summary while the sandbox got nothing. The fix routes all seven through `report_dir`; the three zero-argument checks gain the parameter, and `_display_path` keeps the default's evidence strings byte-identical (relative to ROOT when inside it) without raising `ValueError` for a report dir outside ROOT. ⚠️ **The default is a no-op**: re-running the audit end-to-end left all 32 check statuses and the E2E summary identical (one evidence string differs only by separator style -- the same path). **Mutation 10/10 killed plus a green control**; the target file was restored byte-exactly. ⚠️ **Closing the family reddened cycle 85's pin** (it discovered *zero-argument* readers), so its discovery now admits "only parameter is `report_dir`" -- an allow-list updated, not loosened.

> **The two sibling audits the readiness audit *runs* ignored `--report-dir` -- one never parsed argv, the other rooted its four reads at ROOT (2026-10-07, cycle 91): `2741 passed / 8 skipped`** -- measured 2741 / 8 / 0 (2749 collected, 472.56 s); marker-selected: egress **319 / 1 / 2429 deselected**, non-egress **2422 / 7 / 320 deselected**, reconciling exactly (`2422 + 319 = 2741`, `7 + 1 = 8`, `320 + 2429 = 2749 = 2741 + 8`). The `+12` are new **non-egress** tests in `tests/test_every_sibling_audit_honours_the_report_dir.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2417 -> 2429**. ⚠️ Cycle 90 routed the readiness audit's *own* report paths through `--report-dir`, but the two siblings it *runs* did not follow. `scripts/audit-ui-completeness.py` called **no `argparse` at all** (`parse_args` / `args.` appear zero times), so the `--report-dir` the parent passes was ignored outright -- measured with a custom dir: it wrote `ROOT/data/reports/ui_completeness.{json,md}`, never created the custom dir, and moved ROOT's report mtime, while the readiness audit then read `<custom>/ui_completeness.json` and found nothing. `scripts/audit-v1-completion.py` **wrote** into the custom dir but its four report **reads** were module-level `ROOT` constants (`E2E_SUMMARY` / `UI_REPORT` / `MOCK_REPORT` / `CAPABILITY_REPORT`), so pointed at an empty dir its evidence still named `data/reports/...` -- a sandbox run judged the operator's real reports. The fix routes every report path through `report_dir`; `_display_path` (posix, relative to ROOT when inside it) keeps the default's evidence byte-identical. ⚠️ **The default is a no-op**: re-running both with the default `--report-dir` leaves `ui_completeness.json` / `.md` and `v1_completion.md` **byte-identical**, and `v1_completion.json` identical once `generated_at` / `duration_ms` are dropped. ⚠️ **Measured end-to-end**: the readiness audit pointed at a custom dir now leaves `ui_completeness.json` there (it did not before) and its `ui_completeness_report` / `v1_completion_report` checks report "Report status is fail" rather than a missing report -- they read the file. **Mutation 6/6 killed plus a green control**; the target files were restored byte-exactly. ⚠️ **Closing the family reddened cycle 80's pin** (it monkeypatched the four constants to redirect the reads), so it now redirects via `--report-dir` -- the claim (require the denominator) is unchanged, only the redirection follows the new contract. ⚠️ Incidental, recorded not fixed: `--json-only` is declared by the shared parser and passed by the parent but read by only two of six audits -- an owner decision, since honouring it would drop the `.md` outputs the default run currently writes.

> **A failing E2E result recorded no cause when its reason sat one level down (2026-10-07, cycle 92): `2755 passed / 8 skipped`** -- measured 2755 / 8 / 0 (2763 collected, 544.13 s); marker-selected: egress **319 / 1 / 2443 deselected**, non-egress **2436 / 7 / 320 deselected**, reconciling exactly (`2436 + 319 = 2755`, `7 + 1 = 8`, `320 + 2443 = 2763 = 2755 + 8`). The `+14` are new **non-egress** tests in `tests/test_a_failing_e2e_check_carries_its_cause.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2429 -> 2443**. ⚠️ `_e2e_check` recorded the matched record's **top-level** `error` and nothing else. The live `manager-e2e.json` is `status: fail` with `error: ""` while its **ten nested `checks`** name the reason (7 x "リモート サーバーに接続できません。" and 3 x "ai-server container is not running"), so the readiness summary carried a `fail` with **no cause** -- and `readiness_summary.md` rendered an empty error cell beside it. The fix adds `_result_cause`: the top-level message when present, else the failing nested checks (bounded to 5, with `(+N more)`), else a sentence naming the status -- a non-pass result never returns `""`. ⚠️ **The default is a no-op except where the defect was**: re-running the audit with the default `--report-dir` and diffing it against the same run of the *unpatched* script leaves **9 differing leaves** -- six per-check `duration_ms`, the top-level `duration_ms`, `generated_at`, and **exactly one semantic leaf, `checks[21].error`** (the `manager_e2e` entry). All 32 statuses, every `evidence` / `report_path`, and every other error are identical; on the markdown surface the only row that changes is `Stateful Manager E2E`. **Mutation 6/6 killed plus a green control**; the target file was restored byte-exactly. ⚠️ **Why the six sub-audit checks could stay silent while this one could not**: each of the six has a `*_report` sibling (`ui_completeness` / `ui_completeness_report`) that reads the report and says "Report status is fail" -- but that sibling repeats the *status*, it does **not** carry the *cause*, so the exit-code check beside it was reason-less **and the information was lost**. `manager_e2e` has **no such sibling** at all. **Cycle 93 closed this** (`_process_cause`: `stderr` then `stdout`). ⚠️ **Recorded, not fixed** (owner decisions): the six sub-audit checks record only `stderr` while the reason goes to `stdout` (**closed in cycle 93** -- the stated dilemma was false: fixing it was taken to require changing `run_command`'s contract, but reading both streams *at the call site* leaves the shared component untouched); `scripts/audit-v1-completion.py::_load_json` and `scripts/audit-ui-completeness.py::read_json` read `utf-8` behind a broad `except Exception: return {}`, so a **BOM'd** report reads as `{}` (measured: 48 of 68 JSON reports under `data/reports/` carry a BOM; the readiness audit's own `_load_json` already reads `utf-8-sig`) -- **latent today**, since no file either sibling reads is BOM'd at present.

> **A BOM on the override store read as *corruption* -- and dropped every override (2026-10-08, cycle 97): `2820 passed / 8 skipped`** -- measured 2820 / 8 / 0 (2828 collected, 820.77 s); marker-selected: egress **319 / 1 / 2508 deselected**, non-egress **2501 / 7 / 320 deselected**, reconciling exactly (`2501 + 319 = 2820`, `7 + 1 = 8`, `320 + 2508 = 2828 = 2820 + 8`). The `+11` are new **non-egress** tests in `tests/test_a_bom_does_not_corrupt_the_override_store.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2497 -> 2508**. ⚠️ `CapabilityOverrideStore._load` read `data/settings/capability_overrides.json` with `encoding="utf-8"`, so a file beginning with a UTF-8 BOM raised `JSONDecodeError` and the handler set `corrupted = True` with an **empty** override map. Measured: a valid overrides file is `corrupted = False` with 2 overrides plain, and `corrupted = True` with **0** overrides when the same bytes carry a BOM. The store is reachable -- `CapabilityCatalog.__init__` constructs it (`capability_catalog.py:139`) -- and its sibling already reads capability manifests as `utf-8-sig`, so the override store was the odd one out. ⚠️ **The consequence is not just a false alarm**: dropping every override reverts each capability to its manifest risk level, so a `FORBIDDEN` override the user set is lost -- the file that *restricts* is silently ignored, and a valid file is reported as corrupt. ⚠️ **The same fix covers two more sites in `endpoint_resolver`** (`data/neighbors.json` and the disk cache), which swallowed the same exception into an empty mapping; both are reachable (`resolve_by_mac` / `resolve_tcp_endpoint` are used by `grpc_client` and `status_manager`). All three now read `utf-8-sig` -- a strict superset of `utf-8` for reading. ⚠️ **The differential is over a BOM-free file**: HEAD and patched agree on the whole override map (2 entries); on a BOM'd copy HEAD reports `corrupted=True / 0` and the patched store `corrupted=False / 2`. ⚠️ **A mutation survived and that was evidence about the pin**: the disk-cache reader's mutation passed because the pin had no cache test; adding one made it **3/3 killed plus a green control**. ⚠️ **Recorded, not fixed**: the remaining 7 `src/` JSON file readers (machine-written stores -- we write them `utf-8`, so a BOM cannot occur) still read `utf-8`.

> **A BOM on `settings.json` silently reverted the shipped configuration (2026-10-08, cycle 96): `2809 passed / 8 skipped`** -- measured 2809 / 8 / 0 (2817 collected, 496.53 s); marker-selected: egress **319 / 1 / 2497 deselected**, non-egress **2490 / 7 / 320 deselected**, reconciling exactly (`2490 + 319 = 2809`, `7 + 1 = 8`, `320 + 2497 = 2817 = 2809 + 8`). The `+7` are new **non-egress** tests in `tests/test_a_bom_does_not_revert_the_settings.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2490 -> 2497**. ⚠️ `SettingsStore._load` read `config/settings.json` with `encoding="utf-8"`, so a file beginning with a UTF-8 BOM raised `JSONDecodeError` and fell back to the built-in defaults. Measured with the real store over the shipped config's own bytes: the shipped `privacy.egress_allowed_hosts` `['api.typesafe.ai', 'api.deepseek.com']` becomes `[]`, and `external_egress_allowed` / `external_llm_allowed` flip `True` -> `False` -- **byte-identical to the built-in defaults**, and `privacy` is the only section that differs between the shipped config and the defaults. So a BOM silently took the shipped configuration out of effect and denied every external destination -- exactly the egress L2 needs. ⚠️ **A BOM is not corruption.** Windows editors add one (Notepad, and PowerShell `Set-Content -Encoding utf8`, which in Windows PowerShell 5.1 writes a BOM) -- the same source as the 48-of-68 BOM'd E2E reports found in cycle 95. The same repository already reads capability manifests as `utf-8-sig` (`capability_catalog.py`, `folder_registry.py`), so the settings reader was the odd one out. The fix reads `utf-8-sig` -- a strict superset of `utf-8` for reading. ⚠️ **This is a behaviour change on the egress path, and it is recorded as one**: a BOM'd settings.json previously denied every external destination, and now the user's *declared* allowlist applies. That is the declared permission taking effect, not a widening -- but it is not inert, so it is not called a robustness fix. ⚠️ **The differential is over the live config**: HEAD and patched agree on **every** field of the live (BOM-free) `config/settings.json`, and differ only in `privacy` on a BOM'd copy. **Mutation 2/2 killed plus a green control**; the target file was restored byte-exactly. ⚠️ **Recorded, not fixed**: 9 other `src/` JSON file readers still read `utf-8` -- 7 are machine-written data stores (a BOM cannot occur, because we write them with `utf-8`), and 2 read config-shaped files (`capability_overrides.py`, `endpoint_resolver.py`'s neighbors map). Widening the fix to them is the next cycle, not this one.

> **A JSON reader could not read a BOM'd report -- and a BOM is what a lot of writers emit (2026-10-08, cycle 95): `2802 passed / 8 skipped`** -- measured 2802 / 8 / 0 (2810 collected, 500.38 s); marker-selected: egress **319 / 1 / 2490 deselected**, non-egress **2483 / 7 / 320 deselected**, reconciling exactly (`2483 + 319 = 2802`, `7 + 1 = 8`, `320 + 2490 = 2810 = 2802 + 8`). The `+14` are new **non-egress** tests in `tests/test_a_json_reader_tolerates_a_bom.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2476 -> 2490**. ⚠️ `Path.read_text(encoding="utf-8")` **raises** `JSONDecodeError` on a file that begins with a UTF-8 BOM (`\xef\xbb\xbf`), and every reader here collapses that exception into a *non-neutral* default. Measured on the pre-fix readers, with an otherwise-clean input: `_load_blockers` **fabricates a `production_blocker`** (`Could not read production readiness report: ... (Unexpected UTF-8 BOM (decode using utf-8-sig): line 1 column 1 (char 0))`); `v1._report_status` turns a **`pass` into `fail`** (`Missing or unreadable ...`); `audit_common.read_overrides` **silently drops every override classification**; `ui.read_json` returns `{}`. Measured on disk: **48 of 68** JSON reports under `data/reports` carry a BOM -- including the live `e2e/latest/android-real.json` and `e2e/latest/manager-e2e.json`. The fix reads every one of them as **`utf-8-sig`**, a strict superset of `utf-8` for reading (it strips a BOM when present and is otherwise identical), so no BOM-free file changes behaviour. ⚠️ **The population is discovered, never listed**: an `ast` walk of every `json.loads(<file>.read_text(...))` site in `scripts/audit*.py` + `scripts/audit_common.py` found **7 sites, 6 intolerant** (the 7th, `generate-design-tokens.py`, is not a report reader and was left alone); a guard test asserts the discovery is non-empty so a broken walk cannot pass vacuously. **Mutation 6/6 killed plus a green control**; a live differential over the 12 readers on the real report dir shows **0 differing** values (the change is invisible where the defect is absent), and the audit-touching family is **135 passed**. ⚠️ **Recorded, not fixed**: the other half of this defect is the *writers* -- something in the toolchain emits BOMs (48 of 68 on disk). Making the readers tolerant is the safe, reversible half; whether to also stop the writers emitting BOMs -- which would change every consumer of those files -- is an owner decision.

> **A failing report check recorded no cause -- and the cause was one level down (2026-10-08, cycle 94): `2788 passed / 8 skipped`** -- measured 2788 / 8 / 0 (2796 collected, 494.94 s); marker-selected: egress **319 / 1 / 2476 deselected**, non-egress **2469 / 7 / 320 deselected**, reconciling exactly (`2469 + 319 = 2788`, `7 + 1 = 8`, `320 + 2476 = 2796 = 2788 + 8`). The `+20` are new **non-egress** tests in `tests/test_a_failing_report_check_carries_its_cause.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2456 -> 2476**. ⚠️ `_report_pass` recorded only `f"Report status is {status}"` when a report's status was not `pass` -- which repeats the status the reader already had and names no cause. Measured: of the four reports that fail, two carry a top-level reason (`mock_inventory.json` -> `error: production_blockers=2`, `capability_coverage.json` -> `error: failing=1`) and two carry it **one level down** in their `checks` (`v1_completion.json` -> `v1_checklist_closed: open=5 partial=5 blocker=0`; `ui_completeness.json` -> `web-dashboard: missing [...]`). The fix adds `_report_cause(data, status)`: the report's own `error` / `reason`, else its failing nested `checks` (naming each in `error` or `missing`, bounded to five), else the status alone -- plus `_summarise`, which collapses a list value (the live `missing` list holds 17 files) to its first three and a count. ⚠️ **The default is a no-op except where the defect was**: with one report dir shared by both runs and wiped between them, the patched and unpatched audits differ in **exactly 4 of 32 checks, all in `error` only** -- and those four are exactly the four that had been failing with the bare status. Every `status`, `evidence`, `report_path`, `name` and the audit's own `summary` are identical. **Mutation 5/5 killed plus a green control**; the target file was restored byte-exactly. ⚠️ **The pin discovers its population from the source** -- an `ast` walk of every `_report_pass(...)` call site, rebuilding the `report_dir / "a" / "b.json"` chain into a relative path -- so a new call site is covered without editing the test, and a sibling test asserts the discovery finds six so an empty discovery cannot pass vacuously. ⚠️ **Deliberately not merged with `_result_cause`**: the two read different record schemas (an E2E runner result names `error` on each nested check; a sub-audit report also uses `missing`) and each names its own noun in the fallback sentence. ⚠️ **Recorded, not fixed**: the longest recorded cause is now **469 characters** (`v1_completion_report` -- five nested reasons, some embedding a report path) where the previous maximum was **103**; the bound is on the reason *count* (5, as in cycle 92), not on length. Whether to cap the length is an owner decision.

> **A failing sub-audit check recorded no cause -- the reason is on `stdout` and only `stderr` was read (2026-10-08, cycle 93): `2768 passed / 8 skipped`** -- measured 2768 / 8 / 0 (2776 collected, 508.06 s); marker-selected: egress **319 / 1 / 2456 deselected**, non-egress **2449 / 7 / 320 deselected**, reconciling exactly (`2449 + 319 = 2768`, `7 + 1 = 8`, `320 + 2456 = 2776 = 2768 + 8`). The `+13` are new **non-egress** tests in `tests/test_a_failing_sub_audit_check_carries_its_cause.py`, so egress passed/marked stay 319/320 and only the deselected figure moves, **2443 -> 2456**. ⚠️ `main` spawns six sub-audits with `run_command` and recorded each exit-code check's cause as `<proc>["stderr"] if <proc>["status"] != "pass"`. `run_command` captures `stdout` and `stderr` **separately**, and a failing audit writes its one-line reason to `stdout` and exits nonzero -- measured for all six: `stderr` was **0 bytes** in every case, while the four failures printed `error=production_blockers=2` / `error=failing=1` / `wrote ...ui_completeness.md` / `open=5 partial=5 blockers=0`. So those four reached `readiness_summary.json` as `status: fail, error: ""` -- the same defect cycle 92 closed for the E2E checks. The fix adds `_process_cause(result)`: `stderr` when it is populated (where an unexpected traceback lands), else `stdout`, else a sentence naming the exit -- a non-pass result never returns `""`, and a passing one still returns `""`. ⚠️ **The default is a no-op except where the defect was**: with one report dir shared by both runs and wiped between them, the patched and unpatched audits differ in **exactly 4 of 32 checks, all in `error` only**, all four inside the sub-audit population; every `status`, `evidence`, `report_path` and `name` is identical. **Mutation 4/4 killed plus a green control**; the target file was restored byte-exactly. ⚠️ **Two cycle-92 claims corrected**: that block justified the six checks' silence by their `*_report` sibling "carrying the cause" -- it does not, `_report_pass` returns `f"Report status is {status}"`, repeating the status the exit-code check already gave; and its recorded-not-fixed note said fixing it "would change `run_command`'s contract", which it does not. ⚠️ **`audit-ui-completeness.py` is the caveat that keeps the fix honest**: it prints only its output path, so its recorded cause is a pointer at the report rather than a reason -- more than silence, less than a diagnosis.

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
  `aegis-verify-and-test` skill) rather than "fixing" code that is fine. **Re-measured 2026-10-04: the
  PowerShell tool *does* run native binaries here now** (`& $python --version` → `3.13.14`,
  `$LASTEXITCODE` = **0**), and both `.ps1` gates ran end-to-end — so treat this as a *fallback*
  diagnosis, not the expected state.
- **Egress regression suite**: **329 passed / 1 skipped** (330 tests carry the `egress` marker,
  2527 deselected). CI enforces a floor of 160 (`--require-egress-tests=160`) **and** mutation-proves
  the gate: breaking it yields failures, restoring it yields 319 passes. The mutation figure is
  **78 failures** (measured 2026-10-06 on the 320-marker baseline; it was 76 at the 318-marker baseline, 74 at the 2026-10-01
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
| **Egress Gate** | ✅ Complete — constraint **re-scoped 2026-09-30** | Deny-by-default and fail-closed (`egress/gate.py`), **plus the second permission path the re-scope requires**: a permission the user gave about a *specific* destination, read out of the confirmation store via `egress/permissions.py`. The gate **consults and never asks**, so the retired forced gate stays retired (`test_forced_gate_stays_retired.py`). A request carrying **no user information** needs no permission — the constraint is about user information, not connectivity. The startup assertion checks that an opening is **scoped** (a scoped permission passes; an unscoped opening or a dead allowlist entry fails), not that egress is closed. Wired into 25 modules with 10 real enforcement sites. CI-enforced: **320 egress-marked tests** (319 passed / 1 skipped) against a floor of 160, plus a mutation check that fails the build when the gate is broken (76 failures, measured 2026-10-03). |
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
