# AEGIS Backlog

> **Last Updated**: 2026-06-12
> **Total Tests**: 1204 passed, 0 failed

## P0 — Safety Issues (Must fix before any external use)

| ID | Issue | Status |
|----|-------|--------|
| P0-01 | Chroma/OpenAI memory not integrated (semantic search is mock) | 🔲 Not started |
| P0-02 | Real LLM not integrated (all LLM calls are mock) | 🔲 Not started |
| P0-03 | Docker Compose incomplete (services not containerized) | 🔲 Not started |
| P0-04 | No TLS for gRPC (plaintext only) | 🔲 Not started |
| P0-05 | Single-user only (no multi-user auth) | 🔲 Not started |

## P1 — MVP Completeness

| ID | Issue | Status |
|----|-------|--------|
| P1-01 | Browser Server real implementation (browser-use) | 🔲 Not started |
| P1-02 | PC Server Rust implementation (OS-native) | 🔲 Not started |
| P1-03 | Android real screenshot (MediaProjection) | 🔲 Not started |
| P1-04 | Android UI automation (AccessibilityService) | 🔲 Not started |
| P1-05 | Room Server MQTT adapter | 🔲 Not started |
| P1-06 | Real LLM provider integration (OpenAI/Anthropic) | 🔲 Not started |
| P1-07 | Daily briefing with real data (calendar/weather) | 🔲 Not started |
| P1-08 | Settings Web UI (real forms) | 🔲 Not started |

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
