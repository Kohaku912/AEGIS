# AEGIS — Autonomous Multi-Device AI

AEGIS is an event-driven, self-improving AI assistant that coordinates across multiple devices and servers.

## Architecture

AEGIS consists of 6 gRPC-connected servers:
- **AI Server** (Python) — Central brain, event orchestration, LLM integration
- **PC Server** (Rust) — PC control and monitoring
- **Android Server** (Kotlin) — Mobile device integration
- **Room Server** — Physical environment control
- **Browser Server** (Python + browser-use) — Web automation
- **Dev Server** — Sandboxed development and self-improvement

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Kohaku912/AEGIS.git
cd AEGIS

# 2. Python environment
cd ai-server
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -e ".[dev]"

# 3. Set environment variables
export OPENAI_API_KEY="your-deepseek-api-key"
export OPENAI_BASE_URL="https://api.deepseek.com"

# 4. Run tests
pytest -q  # 1328 tests

# 5. Start services
python start_aegis.py  # Starts AI Server + Dashboard + Web Chat + CLI
```

## Status

| Item | Status |
|------|--------|
| Phase | Beta (real LLM, real devices) |
| Lint | ruff clean |
| Safety | PolicyEngine structural, 4 levels |
| Capabilities | 53 registered (folder-based JSON manifests) |
| LLM | DeepSeek API (OpenAI compatible) |
| Dashboard | HTTP server on port 8090 |
| PC Server | Rust TCP on port 50052 |
| Browser Server | Python HTTP on port 50053 |

## Documentation

### Core

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design |
| [Roadmap](docs/roadmap.md) | Development roadmap |
| [Backlog](docs/backlog.md) | Prioritized task backlog |
| [Implementation Status](docs/implementation-status.md) | Module-by-module status |
| [Risk Register](docs/risk-register.md) | Risk analysis and mitigation |
| [ADR Index](docs/adr/README.md) | Architecture Decision Records |

### Operations

| Document | Description |
|----------|-------------|
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
| [Prompt Regression](docs/prompt-regression.md) | Injection defense tests |

### Components

| Document | Description |
|----------|-------------|
| [PC Server](docs/pc-server.md) | PC control design |
| [Android Server](docs/android-server.md) | Android integration |
| [Room Server](docs/room-server.md) | Room/physical control |
| [Dev Server](docs/dev-server.md) | Sandboxed development |
| [Self-Development](docs/self-development.md) | SelfDev Agent |
| [Mind Layer](docs/mind-layer.md) | Identity/Desire/Emotion/Goals |
| [Memory](docs/memory.md) | Episodic/Semantic/Procedural |
| [Scheduler](docs/scheduler.md) | Task scheduling |
| [LLM Router](docs/llm-router.md) | LLM provider routing |
| [Interaction Hub](docs/interaction-hub.md) | Web Chat + CLI |
| [Notification Gateway](docs/notification-gateway.md) | Notification routing |
| [External Integrations](docs/external-integrations.md) | LINE/Discord/Email stubs |
| [Voice I/O](docs/voice-io.md) | Voice gate + stubs |
| [Evaluation](docs/evaluation.md) | Benchmark harness |

## Safety Model

AEGIS uses **structural safety** — PolicyEngine is a deterministic rules engine, not LLM-based.

| Level | Meaning | Behavior |
|-------|---------|----------|
| Level 0 (READ_ONLY) | Read only | Auto-allow |
| Level 1 (SAFE_ACTION) | Safe actions | Auto-allow, audit |
| Level 2 (APPROVAL_REQUIRED) | Needs approval | Approval UI required |
| Level 3 (HIGH_RISK) | High risk | Approval or deny |
| FORBIDDEN | Forbidden | Always denied |

## License

Private — not yet licensed for distribution.
