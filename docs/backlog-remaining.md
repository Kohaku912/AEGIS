# AEGIS — 未実装・未テスト一覧

> **最終更新**: 2026-06-12
> **テスト**: 1328 passed, 7 skipped
> **Lint**: All checks passed

---

## 1. 完了済み実装

| ID | 機能 | 状態 | 備考 |
|----|------|------|------|
| U-01 | **Real LLM Provider 統合** | ✅ 完了 | `llm/factory.py` — DeepSeek/OpenAI 自動選択 |
| U-02 | **Chroma ベクトル DB 統合** | ✅ 完了 | `memory/factory.py` — ChromaDB/JSONL フォールバック |
| U-03 | **Docker Compose ビルド検証** | ✅ 完了 | config 検証済み |
| U-04 | **Android Foreground Service** | ✅ 完了 | `specialUse` type に変更 |
| U-05 | **Android Notification Listener** | ✅ 完了 | パッケージパス修正 |
| U-06 | **browser-use Agent 実行** | ✅ 完了 | Playwright 直接呼び出し |
| U-07 | **LLM Task Interpreter → Browser-Use 統合** | ✅ 完了 | Playwright + LLM 要約 |
| U-08 | **PC Server 実機 mouse/keyboard** | ✅ 完了 | Windows API (SendInput) |
| U-09 | **PC Server gRPC サーバー** | ✅ 完了 | TCP JSON + Health |
| U-10 | **Android 実機 screenshot** | ✅ 完了 | MediaProjection |
| U-11 | **Android UI tree (AccessibilityService)** | ✅ 完了 | AccessibilityService |
| U-13 | **TLS for gRPC** | ✅ 完了 | `security/tls_config.py` |
| U-14 | **OS 通知統合** | ✅ 完了 | `notification/os_provider.py` |
| U-21 | **Settings Web UI** | ✅ 完了 | `web/settings_ui_routes.py` + テンプレート |
| U-22 | **Daily briefing 実データ** | ✅ 完了 | `briefing/provider.py` |

### 完了済みモジュール

| モジュール | ファイル数 | テスト数 | 状態 |
|-----------|----------|---------|------|
| AI Server Core | 12 | 362 | ✅ |
| Agents (Research, Support, SelfDev) | 3 | 63 | ✅ |
| Mind Layer + Memory + Scheduler | 8 | 72 | ✅ |
| Server Clients (PC/Android/Room/Dev) | 4 | 368 | ✅ |
| Safety & Security | 5 | 119 | ✅ |
| UI (Dashboard, Approval, Web Chat) | 4 | 47 | ✅ |
| LLM Router + Cost Tracker | 6 | 28 | ✅ |
| External Integrations Gate | 6 | 24 | ✅ |
| Voice I/O Gate | 5 | 29 | ✅ |
| Notification Gateway | 2 | 22 | ✅ |
| Backup/Restore | 1 | 22 | ✅ |
| Evaluation Harness | 4 | 40 | ✅ |
| Prompt Regression Pack | 1 | 21 | ✅ |
| LLM Task Interpreter + TaskPlan | 2 | 23 | ✅ |
| Browser-Use Agent | 6 | 17 | ✅ |
| PC Server (Rust) | 6 | 5 | ✅ |
| Android Server (Kotlin) | 5 | 7 (ADB) | ✅ |
| Room MQTT Provider | 1 | 9 | ✅ |
| OS Notification Provider | 1 | 3 | ✅ |
| Daily Briefing Provider | 1 | 7 | ✅ |

---

## 2. 未実装機能

### P1 — Beta 完成に必要

| ID | 機能 | 理由 | 作業量 |
|----|------|------|-------|
| U-12 | **Room Server MQTT adapter** | ✅ 完了 | `room/mqtt_provider.py` |

### P2 — 利便性向上

| ID | 機能 | 理由 | 作業量 |
|----|------|------|-------|
| U-15 | **LINE Bot 実装** | stub のみ。ユーザー確認必要 | 大 |
| U-16 | **Discord Bot 実装** | stub のみ。ユーザー確認必要 | 大 |
| U-17 | **Email SMTP 実装** | stub のみ。ユーザー確認必要 | 中 |
| U-18 | **Webhook 実装** | stub のみ | 中 |
| U-19 | **Real STT (faster-whisper)** | stub のみ | 中 |
| U-20 | **Real TTS (edge-tts)** | stub のみ | 中 |
| U-23 | **Multi-user サポート** | ❌ 除外 | ユーザー指示により作業予定から除外 |

---

## 3. 実機テスト状態

### Android 実機テスト

| ID | テスト | 状態 |
|----|--------|------|
| T-01 | **gRPC 接続維持** | ✅ 完了 |
| T-02 | **通知リスニング** | ✅ 完了 |
| T-03 | **通知 → AEGIS Core イベント送信** | ✅ 完了 |
| T-04 | **Screenshot (MediaProjection)** | ✅ 完了 |
| T-05 | **UI tree (AccessibilityService)** | ✅ 完了 |
| T-06 | **Tap/Swipe (AccessibilityService)** | ✅ 完了 |

### PC Server 実機テスト

| ID | テスト | 状態 |
|----|--------|------|
| T-07 | **gRPC 接続 (Docker → Windows)** | ✅ 完了 |
| T-08 | **Screenshot 実機取得** | ✅ 完了 |
| T-09 | **Active window 実機取得** | ✅ 完了 |
| T-10 | **Overlay 表示** | ✅ 完了 |
| T-11 | **Mouse click 実機** | ✅ 完了 |
| T-12 | **Keyboard type 実機** | ✅ 完了 |

### Browser 実機テスト

| ID | テスト | 状態 |
|----|--------|------|
| T-13 | **Playwright ブラウザ操作** | ✅ 完了 |
| T-14 | **ローカル HTML 読み取り** | ✅ 完了 |
| T-15 | **HN ストーリー取得 + LLM 要約** | ✅ 完了 |

### Dashboard/Web Chat

| ID | テスト | 状態 |
|----|--------|------|
| T-26 | **Dashboard HTTP アクセス** | ✅ 完了 |
| T-27 | **Web Chat API** | ✅ 完了 |

---

## 4. 依存関係の問題

| ID | 問題 | 影響 | 状態 |
|----|------|------|------|
| DEP-01 | `openai` バージョン競合 | browser-use Agent 直接呼び出し不可 | ⚠️ Playwright 直接呼び出しで回避 |
| DEP-02 | OpenAI embedding API クォータ不足 | Chroma ベクトル検索が使えない | ⚠️ ローカル embedding で回避 |
| DEP-03 | Python 3.14 と一部ライブラリの互換性 | langchain の pydantic v1 警告 | ⚠️ 警告のみ、動作に影響なし |
| DEP-04 | Windows Flask バインド問題 | Flask が Windows で接続拒否 | ✅ HTTP サーバーに変更して回避 |

---

## 5. 統計

| 項目 | 数 |
|------|-----|
| 実装済みモジュール | 62 |
| テスト | 1328 passed, 7 skipped |
| Lint エラー | 0 |
| 未実装機能 | 6 (ユーザー確認必要) |
| 完了済み実機テスト | 19/19 |
| 依存関係問題 | 3 (回避済み) |

---

## 6. 次にやるべきこと

### 即座に取り組めるもの

1. **Webhook 実装** (U-18) — stub → 実装
2. **LINE Bot 実装** (U-15) — ユーザー確認後に実装
3. **Discord Bot 実装** (U-16) — ユーザー確認後に実装
4. **Email SMTP 実装** (U-17) — ユーザー確認後に実装

### ユーザー確認必要

5. **Real STT** (U-19) — faster-whisper 統合
6. **Real TTS** (U-20) — edge-tts 統合

### 除外

7. **Multi-user サポート** (U-23) — ユーザー指示により除外
