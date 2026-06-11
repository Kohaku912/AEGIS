# AGENTS.md — AEGIS Project

## Purpose

AEGIS is a platform for **Ellie**, an autonomous multi-device AI assistant.
Ellie operates via event-driven coordination across multiple servers to provide:

- User assistance (schedule, tasks, information)
- Information gathering and analysis
- Self-improvement and learning

**Core principle**: Ellie is event-driven, multi-device, and self-improving.
All server communication uses **gRPC** with shared protobuf definitions.

---

## Directory Structure (Planned)

```
AEGIS/
├── AGENTS.md              # This file — AI agent instructions
├── README.md              # Human-readable project overview
├── docker-compose.yml     # Multi-server orchestration
├── protos/                # Shared gRPC proto definitions (single source of truth)
│   └── ellie/
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

> **Note**: Directory structure is PLANNED. No directories exist yet (repo initialized 2026-06-11).
> When creating directories, follow this layout unless an ADR (in `docs/`) supersedes it.

---

## Server Responsibilities

### AI Server (`ai-server/`)
- **Runtime**: Python 3.12+
- **Role**: Central brain of Ellie
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
- **Runtime**: Node.js + Playwright
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
| Browser Server | Node.js | gRPC (@grpc/grpc-js), Playwright |
| Dev Server | 未確認 | Docker SDK, gRPC |
| Shared | Protocol Buffers | proto3 syntax |
| Infrastructure | Docker Compose | Multi-container orchestration |

**Runtime**: All servers containerized via Docker. Docker Compose for local dev & deployment.

---

## Build / Test / Lint / Format / Run Commands

> **STATUS**: 未確認 — No project files exist yet. Commands below are planned, not verified.
> Update this section IMMEDIATELY after project initialization and verify each command.

### AI Server (Python) — Planned

```bash
# Create virtual environment
cd ai-server && python -m venv .venv && source .venv/bin/activate  # Linux/Mac
cd ai-server && python -m venv .venv && .venv\Scripts\activate     # Windows

# Build (install deps)
cd ai-server && pip install -e ".[dev]"

# Test
cd ai-server && pytest

# Lint
cd ai-server && ruff check .

# Format
cd ai-server && ruff format .

# Run
cd ai-server && python -m ai_server
```

### Browser Server (Node.js) — Planned

```bash
# Build (install deps)
cd browser-server && npm install

# Test
cd browser-server && npm test

# Lint
cd browser-server && npm run lint

# Format
cd browser-server && npm run format

# Run
cd browser-server && npm start
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

## Important Design Files (Planned)

| File | Purpose | Priority |
|------|---------|----------|
| `protos/ellie/*.proto` | **Single source of truth** for all server APIs | HIGHEST |
| `docker-compose.yml` | Service definitions, networking, volumes | HIGH |
| `docs/architecture.md` | High-level architecture decisions | HIGH |
| `docs/adr/` | Architecture Decision Records | MEDIUM |
| `ai-server/src/event_queue.py` | Core event loop | HIGH |
| `ai-server/src/safety.py` | Safety/approval gate | CRITICAL |

---

## Files to Check Before Making Changes

1. **`AGENTS.md`** (this file) — Read first, every session
2. **`protos/ellie/*.proto`** — Understand current API contracts before touching any server
3. **`docker-compose.yml`** — Understand service dependencies and networking
4. **`docs/architecture.md`** — Overall system design
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

- **Repository**: Empty. Two commits on `main` (first commit added `a.txt`, second deleted it).
- **Remote**: `https://github.com/Kohaku912/AEGIS.git`
- **Branch**: `main`
- **Next steps**:
  1. Initialize project structure per the directory layout above
  2. Define proto files first (contract-first development)
  3. Set up Docker Compose skeleton
  4. Implement AI Server core event loop
  5. Add other servers incrementally

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
be2c6d8 (HEAD -> main, origin/main) create project  — deleted a.txt
e1aad96 first commit                                — added a.txt
```

### Commands Verified
| Command | Result |
|---------|--------|
| `git status` | ✅ Clean working tree (empty) |
| `git log --oneline --stat` | ✅ 2 commits, a.txt added then deleted |
| `git ls-tree -r HEAD` | ✅ Empty (no tracked files) |
| `build` | ❌ N/A — no project files |
| `test` | ❌ N/A — no project files |
| `lint` | ❌ N/A — no project files |
| `format` | ❌ N/A — no project files |
| `run` | ❌ N/A — no project files |
