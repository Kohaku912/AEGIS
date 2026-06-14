# AEGIS Roadmap

> **Last Updated**: 2026-06-14
> **Current Phase**: Beta (real LLM, desire-driven autonomy)

## Milestones

### Alpha — Local-Only MVP ✅ (Current)

**Goal**: Single-user, local-only, all safety gates operational

| Component | Status |
|-----------|--------|
| AI Server core (PolicyEngine, ToolBroker, EventBus, TriggerEngine) | ✅ Done |
| Capability schema + registration | ✅ Done |
| Approval system (ApprovalStore + UI) | ✅ Done |
| PC Server (observe + action, mock) | ✅ Done |
| Android Server (observe + action, mock + ADB) | ✅ Done |
| Room Server (observe + action, mock) | ✅ Done |
| Dev Server (sandbox, self-dev workflow) | ✅ Done |
| Research Agent | ✅ Done |
| Support Agent | ✅ Done |
| SelfDev Agent | ✅ Done |
| Mind Layer (Identity/Desire/Emotion/Goals) | ✅ Done |
| Memory (episodic/semantic/procedural) | ✅ Done |
| Scheduler | ✅ Done |
| AutonomousLoop (`src/aegis_ai/autonomous/autonomous_loop.py`) | ✅ Done |
| Planner (`src/aegis_ai/autonomous/planner.py`) | ✅ Done |
| CuriosityDrivenExploration (`src/aegis_ai/autonomous/curiosity_exploration.py`) | ✅ Done |
| Learning Pipeline (ActionTrace → Lesson → Workflow → Skill) | ✅ Done |
| SleepConsolidation (`src/aegis_ai/memory/sleep_consolidation.py`) | ✅ Done |
| SocialIntelligence (`src/aegis_ai/mind/social_intelligence.py`) | ✅ Done |
| Observation Service (`src/aegis_ai/observation/observation_service.py`) | ✅ Done |
| Settings + Permissions | ✅ Done |
| Dashboard + Observability | ✅ Done |
| LLM Router + Cost Tracker | ✅ Done |
| Security (token auth, CSRF, rate limit) | ✅ Done |
| Backup/Restore | ✅ Done |
| Interaction Hub (Web Chat + CLI) | ✅ Done |
| Notification Gateway | ✅ Done |
| External Integrations Gate (stubs) | ✅ Done |
| Voice I/O Gate (stubs) | ✅ Done |
| Evaluation Harness | ✅ Done |
| Prompt Regression Pack | ✅ Done |
| **Tests**: 1336+ passed | ✅ |
| **Lint**: ruff clean | ✅ |

### Beta — Personal Daily Use

**Goal**: Real providers, daily automation, usable by developer

| Task | Priority | Status |
|------|----------|--------|
| Chroma vector DB integration for semantic memory | P1 | 🔲 Not started |
| OpenAI embedding API integration | P1 | 🔲 Not started |
| Real LLM provider (OpenAI/Anthropic) integration | P1 | 🔲 Not started |
| Docker Compose with all services | P1 | 🔲 Not started |
| Browser Server (browser-use) implementation | P1 | 🔲 Not started |
| Daily briefing automation (real calendar/weather) | P2 | 🔲 Not started |
| Notification to real channels (OS notification) | P2 | 🔲 Not started |
| Settings Web UI (real forms, not just API) | P2 | 🔲 Not started |

### Hardware Integration

**Goal**: Real device control with safety gates

| Task | Priority | Status |
|------|----------|--------|
| PC Server Rust implementation (Windows SendInput) | P2 | 🔲 Not started |
| Android real screenshot (MediaProjection) | P2 | 🔲 Not started |
| Android UI automation (AccessibilityService) | P2 | 🔲 Not started |
| Room Server MQTT adapter | P2 | 🔲 Not started |
| Room real sensor integration | P3 | 🔲 Not started |
| Push-to-talk voice input | P3 | 🔲 Not started |

### External Messaging

**Goal**: Safe external communication with approval gates

| Task | Priority | Status |
|------|----------|--------|
| LINE Bot integration (real) | P3 | 🔲 Not started (requires user confirmation) |
| Discord Bot integration (real) | P3 | 🔲 Not started (requires user confirmation) |
| Email SMTP integration (real) | P3 | 🔲 Not started (requires user confirmation) |
| Webhook integration (real) | P3 | 🔲 Not started (requires user confirmation) |

### Multi-Device Polish

**Goal**: Seamless multi-device coordination

| Task | Priority | Status |
|------|----------|--------|
| Cross-device context sharing | P2 | 🔲 Not started |
| Device health monitoring | P2 | 🔲 Not started |
| Graceful degradation (device offline) | P2 | 🔲 Not started |
| Multi-user support | P3 | 🔲 Not started |
| TLS for gRPC | P3 | 🔲 Not started |

## Phase Mapping

| Phase | Milestone | Timeline |
|-------|-----------|----------|
| Phase 1-6 | Alpha (current) | Done |
| Phase 7 | Beta | TBD |
| Phase 8 | Hardware Integration | TBD |
| Phase 9 | External Messaging | TBD |
| Phase 10 | Multi-Device Polish | TBD |
