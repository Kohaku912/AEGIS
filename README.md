# AEGIS — Autonomous Multi-Device AI

AEGIS is an event-driven, self-improving AI assistant that coordinates across multiple devices and servers.

## Architecture

AEGIS consists of several gRPC-connected servers:
- **AI Server** (Python) — Central brain, event orchestration, LLM integration
- **PC Server** (Rust) — PC control and monitoring
- **Android Server** (Kotlin) — Mobile companion app / outbound client
- **Room Server** — Physical environment control
- **Browser Server** (Python + browser-use) — Web automation

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Kohaku912/AEGIS.git
cd AEGIS

# 2. Configure secrets locally
cp .env.example .env
# Set LLM_API_KEY / AGORA_TOKEN / AEGIS_ANDROID_PAIRING_TOKEN in .env

# 3. Start Docker services
docker compose build ai-server browser-server room-server
docker compose up -d ai-server browser-server room-server

# 4. Start host-native PC server separately when PC control is needed
# PC Server listens on 50052; containers reach it via host.docker.internal.

# 5. Run targeted tests with a local basetemp
cd ai-server
.\.venv\Scripts\python.exe -m pytest --basetemp .tmp-pytest -p no:cacheprovider
```

## Status

| Item | Status |
|------|--------|
| Phase | Beta (real LLM, real devices) |
| Lint | ruff clean |
| Safety | PolicyEngine structural, 4 levels |
| Capabilities | Folder-based JSON manifests, canonical `server_id.app_id.action` IDs |
| LLM | Profile-driven OpenAI-compatible providers |
| Dashboard | HTTP server on port 8090, grouped audit log, shared chat history |
| PC Server | Rust TCP on port 50052 |
| Browser Server | Python service on port 50053 |
| Room Server | Python gRPC on port 50055, mock light provider by default |

## Documentation

### Core

| Document | Description |
|----------|-------------|
| [Feature Catalog](docs/feature-catalog.md) | Every feature, what is live vs declared-only, and the full 128-capability inventory |
| [Improvement Review](docs/improvement-review.md) | Codebase-wide survey: goal gaps, inefficiency, security, maintainability, extensibility — each with priority |
| [Architecture](docs/architecture.md) | System design |
| [Status](docs/status.md) | Servers, roadmap, backlog, and what is retired |
| [Risk Register](docs/risk-register.md) | Risk analysis and mitigation |
| [ADR Index](docs/adr/README.md) | Architecture Decision Records |

### Operations

| Document | Description |
|----------|-------------|
| [Docker Services](docs/docker-services.md) | Canonical Docker Compose startup |
| [Beta Runbook](docs/beta-runbook.md) | Setup, startup, daily use |
| [Daily Use](docs/daily-use.md) | Everyday workflow |
| [Troubleshooting](docs/troubleshooting.md) | Common issues |
| [Operations](docs/operations.md) | Monitoring, backup |
| [Settings](docs/settings.md) | Configuration |
| [Security](docs/security.md) | Authentication |
| [Dashboard](docs/dashboard.md) | Operations dashboard |

### Safety

| Document | Description |
|----------|-------------|
| [PC Safety](docs/pc-safety.md) | PC operation safety rules |
| [Android Safety](docs/android-safety.md) | Android operation safety |
| [Room Safety](docs/room-safety.md) | Room/physical device safety |
| [Dev Safety](docs/dev-safety.md) | Dev server safety |
| [Browser Safety](docs/browser-safety.md) | Browser automation safety |
| [Prompt Regression](docs/prompt-regression.md) | Injection-defense pack — **not wired** (see doc) |

### Components

| Document | Description |
|----------|-------------|
| [PC Server](docs/pc-server.md) | PC control design |
| [Android Server](docs/android-server.md) | Android integration |
| [Room Server](docs/room-server.md) | Room/physical control |
| [Self-Development](docs/self-development.md) | SelfDev Agent |
| [Mind Layer](docs/mind-layer.md) | Identity/Emotion/Goals/AffectSystem |
| [Memory](docs/memory.md) | Episodic/Semantic/Procedural |
| [Scheduler](docs/scheduler.md) | Task scheduling |
| [LLM Router](docs/llm-router.md) | LLM provider routing |
| [Interaction Hub](docs/interaction-hub.md) | Web Chat + CLI |
| [Notification Gateway](docs/notification-gateway.md) | Notification routing |
| [External Integrations](docs/external-integrations.md) | LINE/Discord/Email sending, permission-gated |
| [Voice I/O](docs/voice-io.md) | Local STT/TTS; external path is permission-gated |
| [Testing](docs/testing.md) | Unit, integration, real-device checks |

## Current Runtime Notes

- AI, Browser, Room, and Dev servers are Docker Compose services.
- PC Server remains host-native for Windows automation.
- Android is the installed app and connects outbound to AI gRPC on port `50051`.
- Dashboard, Web Chat, and Android Home chat share `data/chat_history.jsonl`.
- Audit Log is grouped by chat turn, autonomous cycle, task, or approval while raw events remain available.
- Autonomous LLM calls are gated by `AEGIS_MIN_LLM_INTERVAL_MS` and default to 30 minutes.
- AGORA normal reads are unread-only; explicit positive `since_id` is history lookup and does not advance the shared cursor.

## Safety Model

The single constraint is that **the user's information is never sent outside without the user's
permission**, and the egress gate is what enforces it. Outbound connections are allowed; *unpermitted*
disclosure of user data is not. Approval, reversibility, policy, and reliability-proof are **not**
constraints — see [`docs/GOAL-CHANGE.md`](docs/GOAL-CHANGE.md).

AEGIS uses **structural safety** — `PolicyEngine` is a deterministic rules engine, not LLM-based.
Risk levels are **annotations, not gates**: each one selects a `PolicyDecision`, and none of them
causes a prompt.

| Risk level | Policy decision | Behavior |
|------------|-----------------|----------|
| `UNSPECIFIED` | `ALLOW_WITH_AUDIT` | Auto-allow, audited |
| `READ_ONLY` | `ALLOW` | Auto-allow |
| `SAFE_ACTION` | `ALLOW_WITH_AUDIT` | Auto-allow, audited |
| `APPROVAL_REQUIRED` | `ALLOW_WITH_AUDIT` | **Label only — nobody is asked** |
| `HIGH_RISK` | `ALLOW_WITH_AUDIT` | Auto-allow, audited |
| `FORBIDDEN` | `DENY` | Always denied |

Three groups are hard-denied regardless of risk level: payments/purchases, egress-gate bypass, and
policy self-modification.

AEGIS may still *voluntarily* ask the user — that path is live
(`ai-server/src/aegis_ai/confirmation/`) — but nothing forces it. See
[`docs/permissions.md`](docs/permissions.md) for the layers that actually decide.

## License

Private — not yet licensed for distribution.
