# AEGIS — 未実装・未テスト一覧

> **最終更新**: 2026-06-12
> **テスト**: 1306 passed, 7 skipped
> **Lint**: All checks passed

---

## 1. 完了済み実装

| ID | 機能 | 状態 | 備考 |
|----|------|------|------|
| U-01 | **Real LLM Provider 統合** | ✅ 完了 | `llm/factory.py` で自動選択 |
| U-02 | **Chroma ベクトル DB 統合** | ✅ 完了 | `memory/factory.py` でフォールバック付き |
| U-04 | **Android Foreground Service** | ✅ 完了 | `specialUse` type に変更 |
| U-05 | **Android Notification Listener** | ✅ 完了 | パッケージパス修正 |

### 完了済み

| モジュール | ファイル数 | テスト数 | 状態 |
|-----------|----------|---------|------|
| AI Server Core (PolicyEngine, ToolBroker, EventBus, TriggerEngine) | 12 | 362 | ✅ |
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

---

## 2. 未実装機能

### P0 — 実用化前に必要

| ID | 機能 | 理由 | 作業量 |
|----|------|------|-------|
| U-01 | **Real LLM Provider 統合** | DeepSeek API key 設定済みだが、InteractionRouter への正式統合が不完全 | 中 |
| U-02 | **Chroma ベクトル DB 統合** | `ChromaSemanticMemory` は作成済みだが、全メモリ検索を Chroma に移行していない | 中 |
| U-03 | **Docker Compose ビルド検証** | config 検証済みだが、実際の `docker compose build` と `up` が未検証 | 小 |
| U-04 | **Android Foreground Service** | gRPC 接続を維持する Foreground Service が権限エラーで停止中 | 中 |
| U-05 | **Android Notification Listener** | `AegisNotificationListener` が ClassNotFoundException で起動しない | 中 |

### P1 — Beta 完成に必要

| ID | 機能 | 理由 | 作業量 |
|----|------|------|-------|
| U-06 | **browser-use Agent 実行** | ✅ 完了 | Playwright 直接呼び出し成功 |
| U-07 | **LLM Task Interpreter → Browser-Use 統合** | ✅ 完了 | Playwright + LLM 要約 |
| U-08 | **PC Server 実機 mouse/keyboard** | ⬜ 未着手 | Windows API (SendInput) 未統合 |
| U-09 | **PC Server gRPC サーバー** | ⬜ 未着手 | TCP JSON プロトコルのみ |
| U-10 | **Android 実機 screenshot** | ⬜ 未着手 | MediaProjection 未実装 |
| U-11 | **Android UI tree (AccessibilityService)** | ⬜ 未着手 | mock のみ |
| U-12 | **Room Server MQTT adapter** | ⬜ 未着手 | mock sensor のみ |
| U-13 | **TLS for gRPC** | ✅ 完了 | `security/tls_config.py` |

### P2 — 利便性向上

| ID | 機能 | 理由 | 作業量 |
|----|------|------|-------|
| U-14 | **OS 通知統合** | stub のみ | 小 |
| U-15 | **LINE Bot 実装** | stub のみ。ユーザー確認必要 | 大 |
| U-16 | **Discord Bot 実装** | stub のみ。ユーザー確認必要 | 大 |
| U-17 | **Email SMTP 実装** | stub のみ。ユーザー確認必要 | 中 |
| U-18 | **Webhook 実装** | stub のみ | 中 |
| U-19 | **Real STT (faster-whisper)** | stub のみ | 中 |
| U-20 | **Real TTS (edge-tts)** | stub のみ | 中 |
| U-21 | **Settings Web UI** | API のみ。フォーム UI なし | 中 |
| U-22 | **Daily briefing 実データ** | mock のみ。カレンダー/天気連携 | 中 |
| U-23 | **Multi-user サポート** | 単一ユーザー前提 | 大 |

---

## 3. 未実機テスト

### Android 実機テスト

| ID | テスト | 現在の状態 | 必要な作業 |
|----|--------|-----------|-----------|
| T-01 | **gRPC 接続維持** | ボタン押下で接続するが、Foreground Service が停止 | Foreground Service 権限修正 |
| T-02 | **通知リスニング** | ClassNotFoundException で起動しない | AegisNotificationListener のパス修正 |
| T-03 | **通知 → AEGIS Core イベント送信** | 未テスト | T-01/T-02 完了後 |
| T-04 | **Screenshot (MediaProjection)** | mock のみ | MediaProjection 実装 |
| T-05 | **UI tree (AccessibilityService)** | mock のみ | AccessibilityService 実装 |
| T-06 | **Tap/Swipe (AccessibilityService)** | mock のみ | AccessibilityService 実装 |

### PC Server 実機テスト

| ID | テスト | 現在の状態 | 必要な作業 |
|----|--------|-----------|-----------|
| T-07 | **gRPC 接続 (Docker → Windows)** | TCP テスト成功 | 正式 gRPC 実装 |
| T-08 | **Screenshot 実機取得** | mock のみ | Windows API 統合 |
| T-09 | **Active window 実機取得** | mock のみ | Windows API 統合 |
| T-10 | **Overlay 表示** | mock のみ | Tauri/Win32 overlay |
| T-11 | **Mouse click 実機** | mock のみ | SendInput 統合 |
| T-12 | **Keyboard type 実機** | mock のみ | SendInput 統合 |

### Browser 実機テスト

| ID | テスト | 現在の状態 | 必要な作業 |
|----|--------|-----------|-----------|
| T-13 | **browser-use Agent 実行** | openai バージョン競合 | 依存関係修正 |
| T-14 | **ローカル HTML 読み取り** | Playwright 直接呼び出し成功 | browser-use 統合 |
| T-15 | **HN ストーリー取得 + LLM 要約** | 成功 (Playwright 直接) | browser-use 統合 |
| T-16 | **CAPTCHA 検出 → 停止** | テスト済み (mock) | 実ページテスト |
| T-17 | **支払い検出 → 停止** | テスト済み (mock) | 実ページテスト |

### Room Server 実機テスト

| ID | テスト | 現在の状態 | 必要な作業 |
|----|--------|-----------|-----------|
| T-18 | **MQTT センサー接続** | mock のみ | MQTT adapter 実装 |
| T-19 | **温度/湿度/明るさ取得** | mock のみ | 実デバイス接続 |
| T-20 | **照明操作** | mock のみ | 実デバイス接続 |
| T-21 | **エアコン操作** | mock のみ | 実デバイス接続 |

### Docker テスト

| ID | テスト | 現在の状態 | 必要な作業 |
|----|--------|-----------|-----------|
| T-22 | **docker compose build** | 未検証 | Dockerfile 検証 |
| T-23 | **docker compose --profile beta up** | config 検証済み、実行未検証 | 実行テスト |
| T-24 | **Docker → Windows host PC Server** | TCP 接続成功 | gRPC 正式化 |
| T-25 | **Docker 内 browser-use** | 未検証 | Chromium インストール確認 |

---

## 4. 未完了の設計・ドキュメント

| ID | ドキュメント | 状態 |
|----|------------|------|
| D-01 | `docs/adr/0003-real-device-docker-testing.md` | ✅ 作成済み |
| D-02 | `docs/adr/0004-permissive-autonomy-policy.md` | ✅ 作成済み |
| D-03 | `docs/beta-architecture.md` | ✅ 作成済み |
| D-04 | `docs/beta-safety.md` | ✅ 作成済み |
| D-05 | `docs/browser-use-agent.md` | ✅ 作成済み |
| D-06 | `docs/evaluation.md` | ✅ 作成済み |
| D-07 | `docs/prompt-regression.md` | ✅ 作成済み |
| D-08 | `docs/external-integrations.md` | ✅ 作成済み |
| D-09 | `docs/voice-io.md` | ✅ 作成済み |
| D-10 | `docs/notification-gateway.md` | ✅ 作成済み |
| D-11 | `docs/docker-real-testing.md` | ✅ 作成済み |
| D-12 | `docs/pc-server-windows-host.md` | ✅ 作成済み |
| D-13 | `docs/testing-real-devices.md` | ✅ 作成済み |

---

## 5. 依存関係の問題

| ID | 問題 | 影響 |
|----|------|------|
| DEP-01 | `openai==2.16.0` (browser-use) vs `openai==2.41.1` (ai-server) | browser-use Agent が使えない |
| DEP-02 | OpenAI embedding API クォータ不足 | Chroma ベクトル検索が使えない |
| DEP-03 | Python 3.14 と一部ライブラリの互換性 | langchain の pydantic v1 警告 |
| DEP-04 | Android SDK 35 の Foreground Service 制限 | dataSync type に権限必要 |

---

## 6. 次にやるべきこと (推奨順)

### 即座に取り組むべきもの

1. **Android gRPC 接続維持** (U-04)
   - Foreground Service を `specialUse` type に変更するか、WorkManager に切り替え
   - または接続を Activity 内で維持し、切断時に再接続

2. **Android Notification Listener 修正** (U-05)
   - `AegisNotificationListener` のクラスパス確認
   - Manifest の service 宣言修正

3. **browser-use 依存関係修正** (U-06)
   - `openai` バージョンを統一するか、browser-use を分離

4. **Docker Compose 実行テスト** (U-03)
   - `docker compose --profile beta build`
   - `docker compose --profile beta up`

### 短期 (1-2週間)

5. **Real LLM 統合** (U-01)
6. **Chroma メモリ統合** (U-02)
7. **PC Server gRPC 正式化** (U-09)

### 中期 (1ヶ月)

8. **Android MediaProjection** (U-10)
9. **Android AccessibilityService** (U-11)
10. **PC Server Windows API** (U-08)

### 長期 (3ヶ月+)

11. **Room Server MQTT** (U-12)
12. **外部メッセージング統合** (U-15-U-18)
13. **Voice I/O** (U-19-U-20)
14. **Multi-user** (U-23)

---

## 7. 統計

| 項目 | 数 |
|------|-----|
| 実装済みモジュール | 59 |
| テスト | 1304 passed |
| Lint エラー | 0 |
| 未実装機能 | 23 |
| 未実機テスト | 25 |
| 依存関係問題 | 4 |
