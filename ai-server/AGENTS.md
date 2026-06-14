# AI Server — AGENTS.md

## Purpose

The AI Server is the **central brain** of AEGIS. It handles:
- LLM integration (DeepSeek/OpenAI)
- Memory management (AdvancedMemory, PersonaMemory, ChromaSemantic)
- Desire system (D2A-inspired intrinsic motivations)
- Autonomous loop (desire-driven task execution)
- Dashboard (Flask web UI with streaming chat)
- Policy engine (deterministic safety gates)

## Technology Stack

- **Language**: Python 3.14
- **Framework**: Flask (dashboard), gRPC (server communication)
- **LLM**: DeepSeek API (`deepseek-chat` model)
- **Embedding**: OpenAI API (`text-embedding-3-small`)
- **Vector DB**: ChromaDB
- **Testing**: pytest

## Directory Structure

```
ai-server/
├── src/aegis_ai/
│   ├── memory/           # Memory system
│   │   ├── advanced.py   # AdvancedMemory (Zep-inspired)
│   │   ├── persona.py    # PersonaMemory
│   │   ├── chroma_semantic.py  # ChromaSemanticMemory
│   │   └── consolidation.py    # MemoryConsolidator
│   ├── desire/           # Desire system
│   │   └── desire_system.py    # DesireSystem (D2A-inspired)
│   ├── autonomous/       # Autonomous loop
│   │   └── autonomous_loop.py  # AutonomousLoop
│   ├── llm/              # LLM integration
│   │   ├── factory.py    # LLM provider factory
│   │   └── providers/    # LLM providers (OpenAI, mock)
│   ├── web/              # Dashboard
│   │   ├── dashboard_routes.py  # Flask routes
│   │   └── templates/    # HTML templates
│   └── policy_engine.py  # Safety gates
├── capabilities/         # Capability definitions (JSON manifests)
│   ├── builtin/
│   │   ├── pc-server/
│   │   ├── browser-server/
│   │   ├── android-server/
│   │   └── room-server/
│   └── generated/
├── tests/                # Test files
└── data/                 # Runtime data
    ├── memory/           # AdvancedMemory data
    ├── persona.jsonl     # PersonaMemory data
    ├── chroma/           # ChromaDB data
    ├── desires/          # Desire state
    ├── autonomous/       # Autonomous loop state
    └── chat_history.jsonl # Chat history
```

## Key Components

### Memory System (`src/aegis_ai/memory/`)

**AdvancedMemory** (Zep-inspired):
- Entity tracking (people, places, things)
- Fact extraction from conversations
- Temporal awareness (valid_at, invalid_at)
- Importance scoring
- LLM-based extraction

**PersonaMemory**:
- Person tracking with relationships
- Conversation history
- Topic tracking

**ChromaSemanticMemory**:
- Vector DB with Chroma
- OpenAI embeddings
- Semantic search

### Desire System (`src/aegis_ai/desire/`)

**8 Desires** (0-10 scale):
- social_connectivity, personal_fulfillment, curiosity, safety
- recognition, autonomy, creativity, purpose

**Features**:
- Time-based decay
- LLM-based evaluation after actions
- Task generation for low desires
- Self-scheduling

### Autonomous Loop (`src/aegis_ai/autonomous/`)

**Features**:
- Desire-driven task execution
- Self-scheduling (LLM decides next run)
- Fallback: 1 hour if not called
- Manual trigger via API

### Dashboard (`src/aegis_ai/web/`)

**Features**:
- Streaming chat (real-time LLM response)
- Memory integration
- Desire context
- All actions through LLM
- Settings management (persists to `config/settings.json`)

## API Endpoints

### Chat API
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/send` | POST | Send message (non-streaming) |
| `/api/chat/stream` | POST | Send message (streaming) |
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

- **Total tests**: 1336+ passing
- **Memory system**: 8 tests
- **Desire system**: 7 tests
- **Autonomous loop**: 5 tests

## Key Design Decisions

1. **LLM-driven operations**: All decisions made by LLM, not keyword matching
2. **All responses through LLM**: Every tool action result passes through LLM
3. **Memory is LLM-managed**: LLM decides what to remember/search/delete
4. **Desire-driven autonomy**: Desires drive autonomous behavior
5. **Self-scheduling**: AI decides when to run next
6. **Folder-based capabilities**: All capabilities defined in JSON manifests, no hardcoded definitions
7. **Persistent settings**: Settings stored in `config/settings.json`, survives `data/` deletion
