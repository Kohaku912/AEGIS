# AGENTS.md — AEGIS Project

## Purpose

AEGIS is a platform for **AEGIS**, an autonomous multi-device AI assistant.
AEGIS operates via event-driven coordination across multiple servers to provide:

- User assistance (schedule, tasks, information)
- Information gathering and analysis
- Self-improvement and learning

**Core principle**: AEGIS is event-driven, multi-device, and self-improving.
All server communication uses **gRPC** with shared protobuf definitions.

---

## Technology Decision Gate 🚦

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
| **Local → Cloud shift** | Moving from local-only to cloud-dependent architecture |
| **Security/privacy impact** | New data storage, new network exposure, credential handling |
| **Language/Framework change** | Switching Node.js→Python, SQLite→Postgres, etc. |
| **Database/Storage change** | Chroma vs Qdrant vs SQLite vector, MQTT vs gRPC stream |
| **LLM library change** | LangGraph vs AutoGen vs CrewAI vs custom AutonomousLoop |
| **Device control approach** | Appium vs Android AccessibilityService, Home Assistant vs custom |

### NOT Required to Ask

The agent may proceed without asking when:
- Implementing to an existing proto contract
- Following AGENTS.md / architecture.md specifications exactly
- Adding tests for existing code
- Fixing bugs within existing implementation patterns
- Writing documentation for existing features

### Decision Request Format

When asking the user, present options in this format:

```markdown
## Technology Decision: {topic}

### Option A: {name}
- **Overview**: One-sentence summary
- **Pros**: 2-3 key advantages
- **Cons**: 2-3 key disadvantages

### Option B: {name}
- **Overview**: One-sentence summary
- **Pros**: 2-3 key advantages
- **Cons**: 2-3 key disadvantages

### Recommendation
{suggested choice with brief justification}

### Impact
- Affected files: {list}
- Migration effort: {estimate}
- Rollback difficulty: {easy/medium/hard}

### User Decision Needed
Please choose: Option A / Option B / Other (specify)
```

### Browser Server Decision (Resolved)

The user has explicitly chosen **browser-use** (Python) for the Browser Server.
All Browser Server implementation must use Python + browser-use, not Node.js + Playwright.

---

## Directory Structure (Planned)

```
AEGIS/
├── AGENTS.md              # This file — AI agent instructions
├── README.md              # Human-readable project overview
├── docker-compose.yml     # Multi-server orchestration
├── protos/                # Shared gRPC proto definitions (single source of truth)
│   └── AEGIS/
│       ├── common.proto
│       ├── ai_server.proto
│       ├── pc_server.proto
│       ├── android_server.proto
│       ├── room_server.proto
│       ├── browser_server.proto
│       └── dev_server.proto
├── ai-server/             # Python — Core AI logic & orchestration
├── pc-server/             # Controls a Windows/Mac/Linux PC
├── android-server/        # Android device control (Kotlin)
├── room-server/           # Room hardware control (lights, sensors, etc.)
├── browser-server/        # Browser automation & web scraping
├── dev-server/            # Sandboxed dev environment execution
└── docs/                  # Architecture decisions, API docs, specs
```

> **Note**: Directory structure skeleton exists (created 2026-06-11). All directories are empty placeholders.
> When adding files, follow this layout unless an ADR (in `docs/`) supersedes it.

---

## Server Responsibilities

### AI Server (`ai-server/`)
- **Runtime**: Python 3.12+
- **Role**: Central brain of AEGIS
- Orchestrates all other servers via gRPC calls
- Manages event queue and priority scheduling
- Handles NLP/LLM integration for user interaction
- Stores user preferences, learned behaviors, memory
- Makes autonomous decisions within safety boundaries
- **Must NOT**: Execute unapproved dangerous operations (see Security Policy)

### PC Server (`pc-server/`)
- **Role**: Controls the user's PC (Windows/Mac/Linux)
- File system operations (read/write with approval)
- Application launch/control
- Clipboard monitoring, screen capture (with consent)
- System notifications
- **Must NOT**: Delete files without explicit approval, access sensitive directories without confirmation

### Android Server (`android-server/`)
- **Runtime**: Kotlin / Android
- **Role**: Mobile device integration
- Notification sync, SMS/call awareness
- Location data (with permission)
- App interaction on-device
- **Must NOT**: Send SMS/DMs autonomously, access contacts without approval

### Room Server (`room-server/`)
- **Role**: Physical room/environment control
- IoT device management (lights, AC, sensors)
- Presence detection
- **Must NOT**: Operate physical devices that could cause harm without confirmation

### Browser Server (`browser-server/`)
- **Runtime**: Python 3.12+ + browser-use
- **Role**: Web automation & information gathering
- Web scraping, form filling, data extraction
- Web app interaction
- **Must NOT**: Post to SNS, send messages, make purchases autonomously

### Dev Server (`dev-server/`)
- **Role**: Sandboxed development environment
- Code execution in isolated containers
- Build/test/lint automation for the AEGIS project itself (self-improvement)
- **Must NOT**: Execute code outside sandbox, access production secrets

---

## Technology Stack

| Component | Language | Key Frameworks |
|-----------|----------|----------------|
| AI Server | Python 3.12+ | gRPC (grpcio), asyncio, LLM integration (未確認) |
| PC Server | 未確認 | gRPC, OS-specific APIs |
| Android Server | Kotlin | gRPC (grpc-kotlin), Android SDK |
| Room Server | 未確認 | gRPC, IoT protocols (未確認) |
| Browser Server | Python 3.12+ | gRPC (grpcio), browser-use |
| Dev Server | 未確認 | Docker SDK, gRPC |
| Shared | Protocol Buffers | proto3 syntax |
| Infrastructure | Docker Compose | Multi-container orchestration |

**Runtime**: All servers containerized via Docker. Docker Compose for local dev & deployment.

---

## Build / Test / Lint / Format / Run Commands

> **STATUS**: 未確認 — No project files exist yet. Commands below are planned, not verified.
> Update this section IMMEDIATELY after project initialization and verify each command.

### AI Server (Python) — Verified

```bash
# Create virtual environment
cd ai-server && python -m venv .venv && source .venv/bin/activate  # Linux/Mac
cd ai-server && python -m venv .venv && .venv\Scripts\activate     # Windows

# Build (install deps)
cd ai-server && pip install -e ".[dev]"

# Test — ✅ VERIFIED (57 tests pass as of 2026-06-11)
cd ai-server && pytest

# Lint
cd ai-server && ruff check .

# Format
cd ai-server && ruff format .

# Run (not yet implemented)
cd ai-server && python -m ai_server
```

### Browser Server (Python) — Planned

```bash
# Build (install deps)
cd browser-server && pip install -e ".[dev]"

# Test
cd browser-server && pytest

# Lint
cd browser-server && ruff check .

# Format
cd browser-server && ruff format .

# Run
cd browser-server && python -m browser_server
```

### All Servers (Docker Compose) — Planned

```bash
# Build all images
docker compose build

# Run all services
docker compose up

# Run all services (detached)
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f
```

---

## Important Design Files

| File | Purpose | Priority |
|------|---------|----------|
| `protos/AEGIS/*.proto` | **Single source of truth** for all server APIs | HIGHEST |
| `protos/AEGIS/capability.proto` | Capability, Tool, ServerInfo, Event, Approval schema | HIGHEST |
| `protos/AEGIS/common.proto` | Shared enums: RiskLevel, ServerType, EventPriority, etc. | HIGHEST |
| `ai-server/src/AEGIS_schema/` | Python Pydantic models mirroring proto definitions | HIGH |
| `ai-server/samples/capabilities.json` | 10 sample capability definitions | MEDIUM |
| `docs/architecture.md` | High-level architecture decisions | HIGH |
| `docker-compose.yml` | Service definitions, networking, volumes (未作成) | HIGH |
| `docs/adr/` | Architecture Decision Records | MEDIUM |
| `ai-server/src/event_queue.py` | Core event loop (未作成) | HIGH |
| `ai-server/src/policy_engine.py` | Safety/approval gate — deterministic, not LLM | CRITICAL |
| `ai-server/src/tool_registry.py` | Capability and server registration, search, filtering | HIGH |
| `ai-server/src/tool_broker.py` | Structured invocation with mandatory PolicyEngine check | HIGH |
| `ai-server/src/safety.py` | Safety/approval gate (未作成) | CRITICAL |

---

## Files to Check Before Making Changes

1. **`AGENTS.md`** (this file) — Read first, every session
2. **`protos/AEGIS/*.proto`** — Understand current API contracts before touching any server
3. **`docs/architecture.md`** — Overall system design, server modules, security model
4. **`docker-compose.yml`** — Understand service dependencies and networking (when created)
5. **`docs/adr/`** — Any relevant Architecture Decision Records

---

## Code Style

### Python (`ai-server/`, possibly `pc-server/`, `room-server/`)
- Follow **PEP 8**
- Use `ruff` for linting & formatting
- **Type hints required** on all public functions and methods
- Use `asyncio` for async operations (not threading)
- Docstrings: Google style

### Kotlin (`android-server/`)
- Follow **Google Kotlin Style Guide**
- Use `ktlint` or `detekt` for linting
- Coroutines for async, not bare threads

### Node.js / TypeScript (`browser-server/`, possibly others)
- Use **Prettier** + **ESLint**
- Prefer TypeScript over JavaScript
- Use `async/await`, avoid callback patterns

### Protocol Buffers (`protos/`)
- Follow [Google's protobuf style guide](https://protobuf.dev/programming-guides/style/)
- Use **proto3** syntax
- Service method names: `VerbNoun` pattern (e.g., `SendNotification`, `GetFileList`)
- One service per proto file, shared messages in `common.proto`

### General
- Meaningful names over comments — code should be self-documenting
- Functions should do ONE thing (Single Responsibility)
- All public APIs must have proto definitions
- No commented-out code in commits

---

## Testing Policy

- **Unit tests**: Required for all business logic. Target >80% coverage.
- **Integration tests**: Required for all gRPC service implementations.
- **Contract tests**: Verify proto definitions match implementations.
- **E2E tests**: Critical user journeys only (due to multi-device complexity).
- Test files co-located with source or in `tests/` subdirectory.
- CI must pass all tests before merge.

> **STATUS**: 未確認 — No test framework or CI configured yet.

---

## Security Policy

### Approval Gates (HARD REQUIREMENT)

The following operations MUST go through an explicit user approval gate in the AI Server's safety module:

1. **File deletion** (any path outside temp directories)
2. **SNS posting, DM sending, email sending**
3. **Physical device operation** (lights, locks, AC, etc.)
4. **Code execution in non-sandboxed environments**
5. **Access to `~/.ssh`, `~/.aws`, `~/.gcloud`, or any credential store**
6. **Installing/updating system packages**
7. **Any operation costing money** (API calls with billing, purchases)

### Data Handling
- User data never leaves the local network without explicit consent
- Secrets managed via Docker secrets or environment variables (never committed)
- Proto files must not contain sensitive defaults

### AI Agent Restrictions
- AI coding agents MUST NOT bypass or weaken approval gates
- AI coding agents MUST NOT implement auto-approve logic for dangerous operations
- AI coding agents MUST NOT remove or comment out safety checks

---

## What AI Agents Must NOT Do Autonomously

1. **Delete or modify existing code without explicit instruction**
2. **Simplify the architecture** (e.g., merging servers, removing gRPC layer)
3. **Bypass or weaken security approval gates** (see Security Policy)
4. **Auto-execute**: SNS posts, DM sends, physical device operations, production deployments
5. **Add dependencies without documenting the reason**
6. **Change proto definitions without updating all affected servers**
7. **Commit secrets, tokens, or credentials**
8. **Make assumptions about 「未確認」 items** — items marked 未確認 must be clarified before acting
9. **Operate outside the sandbox** when modifying the Dev Server
10. **Generate code that auto-approves dangerous operations**

---

## Current Status (2026-06-11)

- **Repository**: Initialized with directory skeleton, AGENTS.md, README.md, .gitignore, proto stubs, and architecture document.
- **Remote**: `https://github.com/Kohaku912/AEGIS.git`
- **Branch**: `main`
- **Implemented**:
  - Shared Capability Protocol (`protos/AEGIS/capability.proto`, `common.proto` extended)
  - Python Pydantic models + validation (`ai-server/src/AEGIS_schema/`)
  - Policy Engine (`ai-server/src/policy_engine.py`) — deterministic safety gate with ApprovalStore
  - Approval System (`ai-server/src/approval.py`) — ApprovalRequest lifecycle + ApprovalStore
  - Tool Registry (`ai-server/src/tool_registry.py`) — capability/server registration & search
  - Tool Broker (`ai-server/src/tool_broker.py`) — structured invocation with mandatory policy check
  - Event Bus (`ai-server/src/event_bus.py`) — publish/subscribe with dedup and priority queue
  - Trigger Engine (`ai-server/src/trigger_engine.py`) — rule-based event → TaskRequest generation
  - 10 sample capabilities (`ai-server/samples/capabilities.json`)
  - 10 sample events (`ai-server/samples/events.json`)
  - Docker Compose skeleton (Phase 1.2: 5 services, all healthy)
  - 356 tests (all passing): 57 schema + 49 approval/policy + 37 broker + 33 registry + 22 event bus + 39 trigger engine + 72 policy/approval/audit + 15 capability_registry
- **Next steps**:
  1. Complete remaining proto definitions for all 6 servers
  2. Set up Docker Compose skeleton
  3. Implement AI Server: Event Bus, Trigger Engine, Audit Log (Phase 1)
  4. Implement Browser Server as first capability server (Phase 2)
  5. See `docs/architecture.md` §9 for full MVP roadmap

---

## Appendix: Investigation Results (2026-06-11)

### Files Investigated
- `.git/HEAD` — `refs/heads/main`
- `.git/config` — Remote: `https://github.com/Kohaku912/AEGIS.git`, branch `main`
- `.git/COMMIT_EDITMSG` — "create project"
- `.git/index` — Exists (empty tree)
- `.git/objects/` — Git objects present (directories: `1a/`, `2e/`, `4b/`, `be/`, `e1/`)
- `.git/logs/` — Reflog exists
- GitHub repo page — Confirmed empty, no files

### Commits
```
79d0d2d (HEAD -> main, origin/main) Initialize project structure with AGENTS.md and protos
be2c6d8 create project  — deleted a.txt
e1aad96 first commit     — added a.txt
```

### Commands Verified
| Command | Result |
|---------|--------|
| `git status` | ✅ Clean working tree (empty) |
| `git log --oneline --stat` | ✅ 3 commits |
| `git ls-tree -r HEAD` | ✅ 17 files tracked |
| `git push origin main` | ✅ Success |
| `build` | ❌ N/A — no project files |
| `test` | ❌ N/A — no project files |
| `lint` | ❌ N/A — no project files |
| `format` | ❌ N/A — no project files |
| `run` | ❌ N/A — no project files |
