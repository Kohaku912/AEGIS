# AI Server — AGENTS.md

## Purpose

The AI Server is the **central brain** of AEGIS. It handles:
- LLM integration (profile-driven OpenAI-compatible providers: DeepSeek, OpenAI, Ollama, mock)
- Memory management (AdvancedMemory, episodic/semantic, learning backends, MemoryManager)
- Desire system (pressure-based 3-desire system)
- Autonomous loop (desire-driven task execution)
- Dashboard (Flask web UI with streaming chat)
- Policy engine (deterministic safety gates)

## Technology Stack

- **Language**: Python 3.14
- **Framework**: Flask (dashboard), gRPC (server communication)
- **LLM**: YAML profile-driven OpenAI-compatible providers
- **Embedding**: OpenAI-compatible embeddings
- **Vector DB**: ChromaDB
- **Testing**: pytest

## Directory Structure

```
ai-server/
├── src/aegis_ai/
│   ├── memory/           # Memory system (advanced, episodic, semantic, learning)
│   ├── desire/           # Desire system (pressure + fulfillment)
│   ├── autonomous/       # Autonomous loop, planner, curiosity
│   ├── llm/              # LLM gateway/router/settings/prompt/cost tracking
│   ├── web/              # Dashboard, auth, chat service, manager routes
│   └── policy_engine.py  # Safety gates
├── capabilities/         # Capability definitions (JSON manifests)
│   ├── builtin/
│   │   ├── pc-server/
│   │   ├── browser-server/
│   │   ├── ai-server/
│   │   ├── android-server/
│   │   └── room-server/
│   └── generated/
├── apps/                 # Capability executors
│   └── builtin/
│       ├── pc-server/
│       ├── browser-server/
│       ├── ai-server/
│       ├── android-server/
│       └── room-server/
├── config/               # Persistent settings
│   └── settings.json
└── data/                 # Runtime data (ephemeral)
    ├── memory/
    ├── desires/
    ├── autonomous/
    └── audit.jsonl
```

## Key Components

### Capability Management

**CapabilityCatalog** (`capability_catalog.py`):
- Single source of truth for all capabilities
- Loads from `capabilities/` folder
- Provides `list_for_llm()` and `list_for_tools()`
- Alias management (old IDs → canonical IDs)

**Tool calling in chat** (`web/chat_tools.py`):
- `call_llm_with_tools()` — LLM with tool calling support
- `ask_user` tool for user input during task execution
- DeepSeek native format parsing support
- **Recursive multi-step tool calling** (max 15 rounds)
- XML tag format support (`<pc-server__shell__powershell><command>...</command></pc-server__shell__powershell>`)
- Error handling with retry logic

### Desire System (`src/aegis_ai/desire/`)

**3 Desires** (pressure-based):
- user_support
- social
- growth

**Fulfillment rules** (`fulfillment.py`):
- Per-desire conditions with delta values
- `evaluate_task_result()` classifies effect
- `TaskEffect`: useful, no_effect, failed, blocked, needs_followup

### Autonomous Loop (`src/aegis_ai/autonomous/`)

**Features**:
- Desire-driven task execution via tool calling
- `_generate_tasks()` uses CapabilityCatalog.list_for_tools()
- `_generate_follow_up_tasks()` with tool calling
- `_update_desires()` uses fulfillment rules (delta-based)
- Pressure-based trigger; LLM interval gate is off by default

### Dashboard (`src/aegis_ai/web/`)

**Features**:
- Tool calling chat with `call_llm_with_tools()`
- `ask_user` tool for interactive user input
- Memory context with system-reminder filtering
- Settings persistence to `config/settings.json`

## API Endpoints

### Chat API
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/send` | POST | Send message (tool calling, ask_user support) |
| `/api/chat/respond` | POST | Respond to ask_user question |
| `/api/chat/history` | GET | Get chat history |
| `/api/chat/clear` | POST | Clear chat history |

### Settings API
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/settings` | GET | Get all settings |
| `/api/settings/<section>` | POST | Update a section |
| `/api/settings/reset` | POST | Reset to defaults |
| `/api/settings/export` | GET | Export as JSON |

### Autonomous API
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/autonomous/status` | GET | Get loop status |
| `/api/autonomous/trigger` | POST | Manual trigger |
| `/api/autonomous/start` | POST | Start loop |
| `/api/autonomous/stop` | POST | Stop loop |
| `/api/desires` | GET | Get desire states |

## Environment Variables

```bash
OPENAI_API_KEY=sk-...        # DeepSeek/OpenAI API key
OPENAI_BASE_URL=https://api.deepseek.com  # DeepSeek base URL
EMBEDDING_API_KEY=sk-...     # OpenAI embedding API key
EMBEDDING_MODEL=text-embedding-3-small  # Embedding model
```

## Running

```bash
# Start dashboard
cd ai-server
python -m aegis_ai.dashboard

# Run tests
cd ai-server
pytest

# Run specific tests
pytest tests/test_memory_system.py
pytest tests/test_desire_system.py
pytest tests/test_autonomous_loop.py
```

## Settings Persistence

Settings are persisted to `config/settings.json` (survives `data/` deletion).
Audit logs are written to `data/settings_audit.jsonl`.

## Test Status

- **Total tests**: 157 passing
- **Memory system**: 8 tests
- **Desire system**: 7 tests
- **Autonomous loop**: 5 tests

### Presentation Engine (`src/aegis_ai/presentation/`)

AEGIS output layer for rich user-facing content. NOT a state viewer — it delivers information AEGIS decided the user should see.

- PresentationSpec has: presentation_id, source, intent, importance, modality, title, summary, content, delivery, placement, interaction, lifecycle
- safety / safety_level / requires_approval are intentionally ABSENT — safety belongs to the source capability
- Modalities: text_card, chart_panel, diagram_panel, gltf_model, overlay_short
- Targets: dashboard, pc_overlay, android_overlay, xr_scene
- Persistence: data/presentations/presentations.jsonl
- XR/MR: XRPendingAdapter stores XR-targeted presentations in a pending queue

**API**: `/api/presentations`, `/api/presentations/<id>`, `/api/presentations/<id>/action`, `/api/presentations/<id>/dismiss`, `/api/presentations/stream`

**Capabilities**: `ai-server.presentation.present`, `ai-server.presentation.list`, `ai-server.presentation.dismiss`, `ai-server.presentation.action`

## Key Design Decisions

1. **LLM-driven operations**: All decisions made by LLM, not keyword matching
2. **All responses through LLM**: Every tool action result passes through LLM
3. **Memory is LLM-managed**: LLM decides what to remember/search/delete
4. **Desire-driven autonomy**: Desires drive autonomous behavior
5. **Self-scheduling**: AI decides when to run next
6. **Folder-based capabilities**: All capabilities defined in JSON manifests, no hardcoded definitions
7. **Persistent settings**: Settings stored in `config/settings.json`, survives `data/` deletion
8. **Text-based tool calling for DeepSeek**: Use regex to parse `<tool_call>...</tool_call>` from LLM response instead of OpenAI's `tools` parameter
9. **Monkey-patch for browser-use DeepSeek compatibility**: `_patch_browser_use_models()` patches `ChatOpenAI.ainvoke()` globally to normalize DeepSeek's malformed JSON before pydantic validation
10. **Interactive user confirmation via `ask_user` tool**: LLM can ask user questions mid-task, dashboard shows selection/text UI, user responds via `/api/chat/respond`
11. **Recursive tool calling loop**: LLM can call multiple tools in sequence, results are fed back to LLM for next decision
12. **Multiple tool call formats**: Supports `<tool_call>`, DeepSeek DSML, XML tag, and plain JSON formats
13. **Browser verification detection**: Browser agent detects CAPTCHA/phone verification and returns `needs_user_input` to pause for user intervention
14. **Full-authority defaults**: PolicyEngine allows with audit except purchases and policy bypass/disable. Catalog `requires_approval` remains the user tighten path.
