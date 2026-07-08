# AEGIS Roadmap

> **Last Updated**: 2026-06-17
> **Current Phase**: Beta (real LLM, desire-driven autonomy)
> **Total Tests**: 157 passed

## Milestones

### Alpha — Local-Only MVP ✅ (Complete)

**Goal**: Single-user, local-only, all safety gates operational

| Component | Status |
|-----------|--------|
| AI Server core (PolicyEngine, ToolBroker, EventBus, TriggerEngine) | ✅ Done |
| Capability schema + registration (folder-based, JSON manifests, 53 capabilities) | ✅ Done |
| Approval system (ApprovalManager + Fanout, 4 channels) | ✅ Done |
| PC Server (Rust, TCP, 40+ capabilities) | ✅ Done |
| Android Server (observe + action, mock + ADB) | ✅ Done |
| Room Server (observe + action, mock) | ✅ Done |
| Browser Server (browser-use, DeepSeek compatibility) | ✅ Done |
| Research Agent | ✅ Done |
| Support Agent | ✅ Done |
| SelfDev Agent | ✅ Done |
| Mind Layer (Identity/Desire/Emotion/Goals) | ✅ Done |
| Memory (episodic/semantic/procedural/chroma) | ✅ Done |
| Scheduler | ✅ Done |
| AutonomousLoop with TaskManager integration | ✅ Done |
| Planner | ✅ Done |
| CuriosityDrivenExploration | ✅ Done |
| Learning Pipeline (ActionTrace → Lesson → Workflow → Skill) | ✅ Done |
| SleepConsolidation via SleepManager | ✅ Done |
| SocialIntelligence | ✅ Done |
| Observation Service | ✅ Done |
| Settings + Permissions (config/settings.json persistence) | ✅ Done |
| Dashboard + Observability + Manager API routes | ✅ Done |
| LLM Router + LLMGateway + CostTracker | ✅ Done |
| PromptRegistry (YAML-backed) + LLMSettingsResolver (YAML-backed) | ✅ Done |
| Security (token auth, CSRF, rate limit) | ✅ Done |
| Backup/Restore | ✅ Done |
| Interaction Hub (Web Chat + CLI) | ✅ Done |
| Notification Gateway | ✅ Done |
| External Integrations Gate (stubs) | ✅ Done |
| Voice I/O Gate (stubs) | ✅ Done |
| Evaluation Harness | ✅ Done |
| Prompt Regression Pack | ✅ Done |
| Runtime singleton + Manager Architecture | ✅ Done |
| E2E Lifecycle Tests (8 tests) | ✅ Done |
| **Tests**: 157 passed | ✅ |
| **Lint**: ruff clean | ✅ |

### Beta — Personal Daily Use

**Goal**: Real providers, daily automation, usable by developer

| Task | Priority | Status |
|------|----------|--------|
| Daily briefing automation (real calendar/weather) | P1 | ✅ Done (`briefing/provider.py`) |
| Settings Web UI (real forms) | P1 | ✅ Done (`settings_ui_routes.py`) |
| Browser Server (browser-use) implementation | P1 | ✅ Done (`browser-use-agent`) |
| Real LLM provider (DeepSeek) integration | P1 | ✅ Done (`llm/factory.py`) |
| Docker Compose with all services | P1 | 🔲 Not started |
| Notification to real channels (OS notification) | P2 | ✅ Done (`notification/os_provider.py`) |
| Chroma vector DB integration for semantic memory | P2 | ✅ Done (`memory/chroma_semantic.py`) |
| TaskManager lifecycle tracking | P1 | ✅ Done (`task/task_manager.py`) |
| StatusManager health checks | P1 | ✅ Done (`status/status_manager.py`) |
| Manager API routes (tasks/events/audit/status) | P1 | ✅ Done (`web/manager_routes.py`) |
| E2E lifecycle tests | P1 | ✅ Done (`tests/test_e2e_lifecycle.py`) |

### Hardware Integration

**Goal**: Real device control with safety gates

| Task | Priority | Status |
|------|----------|--------|
| PC Server Rust implementation (Windows SendInput) | P1 | ✅ Done (`pc-server/`) |
| PC Server overlay (custom click-through) | P1 | ✅ Done (`overlay.rs`) |
| PC Server shell commands (powershell/cmd) | P1 | ✅ Done (`shell.rs`) |
| Android real screenshot (MediaProjection) | P2 | ✅ Done |
| Android UI automation (AccessibilityService) | P2 | ✅ Done |
| Room Server MQTT adapter | P2 | ✅ Done (`room/mqtt_provider.py`) |
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
| Device health monitoring (StatusManager) | P1 | ✅ Done |
| Graceful degradation (device offline) | P2 | 🔲 Not started |
| Multi-user support | P3 | 🔲 Not started |
| TLS for gRPC | P3 | ✅ Done (`security/tls_config.py`) |

## Phase Mapping

| Phase | Milestone | Timeline |
|-------|-----------|----------|
| Phase 1-6 | Alpha | ✅ Complete |
| Phase 7 | Beta (partially complete) | In progress |
| Phase 8 | Hardware Integration | Mostly complete |
| Phase 9 | External Messaging | Not started |
| Phase 10 | Multi-Device Polish | Partial |
