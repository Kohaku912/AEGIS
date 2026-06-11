# Architecture Decision Records (ADR)

> **Last Updated**: 2026-06-12

ADR は AEGIS の主要な設計判断を記録します。各 ADR は一度確定すると変更困難です。

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-0001](0001-technology-decision-gate.md) | Technology Decision Gate | ✅ Accepted | 2026-06-11 |
| [ADR-0002](0002-browser-server-browser-use.md) | Browser Server: browser-use | ✅ Accepted | 2026-06-11 |

## Determined (not yet formalized as ADR, but confirmed)

以下の設計判断は AGENTS.md / architecture.md で確定済みですが、個別 ADR にはまだ移行していません。

| 判断 | 確定日 | 根拠 |
|------|--------|------|
| AI名は AEGIS | 2026-06-11 | ユーザー明示 |
| gRPC + proto3 を全サーバー通信に採用 | 2026-06-11 | 型安全、言語非依存 |
| PolicyEngine は構造的安全 (LLM非依存) | 2026-06-11 | プロンプト注入に耐性 |
| Graduated Safety (4レベル) | 2026-06-11 | READ_ONLY → SAFE_ACTION → APPROVAL_REQUIRED → FORBIDDEN |
| PC Server は Rust | 2026-06-11 | ユーザー選択 (Option B) |
| Android Server は Kotlin Native | 2026-06-11 | ユーザー選択 (Option A) |
| Room Server は MQTT | 2026-06-11 | ユーザー選択 (Option A) |
| EventBus は in-memory | 2026-06-11 | ユーザー選択 (Option A) |
| Memory Backend は Chroma (vector DB) | 2026-06-11 | ユーザー選択 (Option C) |
| Embedding API は外部 (OpenAI) | 2026-06-11 | ユーザー選択 |
| Scheduler は LangGraph | 2026-06-11 | ユーザー選択 |
| Mind Layer は deterministc state + LLM context bias | 2026-06-11 | パーミッションモデルではなく状態バイアス |
| Dev Server は local sandbox | 2026-06-12 | OpenHands/SWE-agent 参考 |
| SelfDevAgent は main merge FORBIDDEN | 2026-06-12 | 安全上必須 |
| LLM Router は task type + privacy level でルーティング | 2026-06-12 | コスト制御 + プライバシー |
| External integrations は default disabled + stub | 2026-06-12 | プライバシー保護 |
| Voice I/O は MVP out of scope (stubs only) | 2026-06-12 | 複雑性 > 価値 |

## Pending Decisions (requires user confirmation)

| 判断 | 選択肢 | 状態 |
|------|--------|------|
| Real LLM provider | OpenAI / Anthropic / Local (llama.cpp) | 🔲 未決定 |
| Browser automation library | browser-use (確定済み) vs Playwright 直接 | ✅ 確定済み |
| STT provider | faster-whisper / whisper.cpp / Cloud | 🔲 未決定 |
| TTS provider | edge-tts / Piper / VOICEVOX | 🔲 未決定 |
| Room hardware protocol | MQTT (確定済み) vs HTTP | ✅ 確定済み |
| Multi-user auth method | Token / OAuth / Certificate | 🔲 未決定 |
