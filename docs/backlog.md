# AEGIS Backlog

> **Last Updated**: 2026-06-17
> **Total Tests**: 157 passed

## P0 — Safety Issues (Must fix before any external use)

| ID | Issue | Status |
|----|-------|--------|
| P0-01 | Chroma/OpenAI memory not integrated (semantic search is mock) | ✅ Done — AdvancedMemory, PersonaMemory, ChromaSemanticMemory |
| P0-02 | Real LLM not integrated (all LLM calls are mock) | ✅ Done — DeepSeek API via LLMRouter + LLMGateway |
| P0-03 | Docker Compose incomplete (services not containerized) | 🔲 Not started |
| P0-04 | No TLS for gRPC (plaintext only) | ✅ Done — `security/tls_config.py` |
| P0-05 | Single-user only (no multi-user auth) | 🔲 Not started |

## P1 — MVP Completeness

| ID | Issue | Status |
|----|-------|--------|
| P1-01 | Browser Server real implementation (browser-use) | ✅ Done |
| P1-02 | PC Server Rust implementation (OS-native) | ✅ Done — 40+ capabilities |
| P1-03 | Android real screenshot (MediaProjection) | ✅ Done |
| P1-04 | Android UI automation (AccessibilityService) | ✅ Done |
| P1-05 | Room Server MQTT adapter | ✅ Done |
| P1-06 | Real LLM provider integration (DeepSeek) | ✅ Done — `llm/factory.py` |
| P1-07 | Daily briefing with real data (calendar/weather) | ✅ Done — `briefing/provider.py` |
| P1-08 | Settings Web UI (real forms) | ✅ Done — `settings_ui_routes.py` |
| P1-09 | Runtime singleton + Manager Architecture | ✅ Done — `runtime.py` |
| P1-10 | TaskManager lifecycle tracking | ✅ Done — `task/task_manager.py` |
| P1-11 | StatusManager health checks | ✅ Done — `status/status_manager.py` |
| P1-12 | Manager API routes (19 routes) | ✅ Done — `web/manager_routes.py` |
| P1-13 | E2E lifecycle tests | ✅ Done — 8 tests |
| P1-14 | PromptRegistry + LLMSettingsResolver (YAML) | ✅ Done |
| P1-15 | Text-based tool calling for DeepSeek | ✅ Done — `chat_tools.py` |

## P2 — Usability

| ID | Issue | Status |
|----|-------|--------|
| P2-01 | OS notification integration | 🔲 Not started |
| P2-02 | Push-to-talk voice input | 🔲 Not started |
| P2-03 | Cross-device context sharing | 🔲 Not started |
| P2-04 | Device health monitoring dashboard | 🔲 Not started |
| P2-05 | Graceful device offline handling | 🔲 Not started |
| P2-06 | Better error messages in Approval UI | 🔲 Not started |
| P2-07 | Chat UI improvements (history, search) | 🔲 Not started |

## P3 — Advanced Autonomy

| ID | Issue | Status |
|----|-------|--------|
| P3-01 | LINE Bot real integration | 🔲 Not started |
| P3-10 | AutonomousLoop desire-driven execution | ✅ Done — `src/aegis_ai/autonomous/autonomous_loop.py` |
| P3-11 | Learning pipeline (ActionTrace → Lesson → Workflow → Skill) | ✅ Done |
| P3-12 | SleepConsolidation memory maintenance | ✅ Done — `src/aegis_ai/memory/sleep_consolidation.py` |
| P3-13 | CuriosityDrivenExploration | ✅ Done — `src/aegis_ai/autonomous/curiosity_exploration.py` |
| P3-02 | Discord Bot real integration | 🔲 Not started |
| P3-03 | Email SMTP real integration | 🔲 Not started |
| P3-04 | Webhook real integration | 🔲 Not started |
| P3-05 | Real STT (faster-whisper) | 🔲 Not started |
| P3-06 | Real TTS (edge-tts) | 🔲 Not started |
| P3-07 | Multi-user support | 🔲 Not started |
| P3-08 | TLS for gRPC | 🔲 Not started |
| P3-09 | Plugin marketplace | 🔲 Not started |

## Deferred / Out of Scope

| ID | Issue | Reason |
|----|-------|--------|
| D-01 | Cloud/SaaS deployment | Local-first architecture |
| D-02 | Always-listening voice | Privacy concern |
| D-03 | Auto-approve dangerous ops | Safety violation |
| D-04 | Plugin marketplace | Premature (needs real usage first) |
| D-05 | Multi-tenant isolation | Single-user MVP |
| D-06 | Real purchase/payment | Safety — always requires approval |
