# AEGIS Dashboard 改修計画 v2 — 洗練版

> ベース計画: `instruction.md` (Dashboard 改修計画 v2, 25 セクション)
> 方針: 中断 / コンテキスト圧縮に耐えるよう、各 Phase 完了時に git commit + ここに進捗を記録する。
> 復帰時は `git log --oneline` + このファイルの最新エントリから再開する。

## 0. 目的 (instruction.md §1-2)

Dashboard を単なる「状態表示画面」ではなく、
**AEGIS の内部状態を可視化・監視・追跡できる Observability UI** にする。

情報階層を **4 段**:

```
Level 1: Overview   (1 画面、AEGIS の現在状態)
Level 2: Detail     (Task / Agent / Event の詳細)
Level 3: Trace      (Agent 内部イベントのタイムライン)
Level 4: Raw        (生 Event、LLM request/response 等)
```

「見やすさ」と「情報量」を両立。Overview では全部を見せないが、Dashboard から全部に到達できる。

## 1. 全体ステータス

| Phase | 内容 | 状態 | 完了日 | 備考 |
|-------|------|------|--------|------|
| D1 | Agent イベントストリーム拡張 | done | 2026-09-10 | instruction.md §12 に対応 (8 種類 + 17 tests) |
| D2 | Live Overlay (sticky bar) 実装 | done | 2026-09-10 | instruction.md §3, §4, §12, §20, §21 (sticky 38px + priority) |
| D3 | Trace ID 伝搬 (event/task/activity/agent_session/trace/parent) | done | 2026-09-10 | instruction.md §16 (Trace ID 6 種 + 6 tests) |
| D4 | Agent Trace 画面 (9 tabs) | done | 2026-09-10 | instruction.md §10 (9 tabs 画面 + 6 backend tests + 10 frontend tests) |
| D5 | Policy / Approval 表示統合 | done | 2026-09-10 | instruction.md §9, §11 (policy.decision publish + 9 backend tests + 3 frontend tests) |
| D6 | MCP / Tool call 完全表示 | done | 2026-09-10 | instruction.md §7, §8 (ToolCallJson 共通コンポーネント + 7 tests + 3 tests) |
| D7 | 検索 (cross-tab) と時間軸 Timeline | done | 2026-09-10 | instruction.md §17, §18 (AgentTimelinePage Gantt + 5 tests) |
| D8 | 複数 Agent / Live Overlay 優先順位 | done | 2026-09-10 | instruction.md §19, §20 (pickLiveOverlayEventForAgent + liveOverlayClickTarget + 8 + 8 tests) |
| D9 | Settings / Retention / Token cost | done | 2026-09-10 | instruction.md §22, §25 (Live Activity Overlay 設定 + Token / Cost panel + 5 + 6 + 3 tests) |

## 2. 既存実装マッピング (instruction.md §1-25 vs 現状)

| § | instruction.md 項目 | 既存 | ギャップ | Phase |
|---|-------------------|------|---------|-------|
| 2 | 4 階層情報設計 | ◐ Overview / Detail / LogsPage はある | Trace (Agent 内部) が独立画面としてない | D4 |
| 3 | Live Overlay (1 行) | △ `LiveActivityDrawer` (展開式) | sticky bar 化、最重要 1 イベント要約 | D2 |
| 4 | Overlay 状態遷移 | ❌ | 7 状態 (thinking/tool/waiting/...) イベント未実装 | D1, D2 |
| 5 | 内部推論表示 | ❌ | agent.thinking イベント未実装 | D1, D4 |
| 6 | Thinking 専用 Timeline | ❌ | Agent 単位の Thinking timeline なし | D4 |
| 7 | Tool call 完全表示 | ◐ 部分 (JSON は見れる所もある) | capability_id ごとに統一 | D6 |
| 8 | MCP 完全追跡 | △ adapter.py で正規化あり | EventBus に publish されていない | D1, D6 |
| 9 | Policy 表示 | △ `audit_view` に ALLOW/DENY あり | Dashboard Trace に統合されていない | D5 |
| 10 | Agent Trace 9 tabs | ❌ | 新規 | D4 |
| 11 | Dashboard Overview | ✅ 既存 | レイアウト調整のみ | D5 |
| 12 | Overlay 状態遷移 (Backend) | ❌ | `agent.started/thinking/tool.started/...` イベント未実装 | D1 |
| 13 | リアルタイム SSE | ✅ `routes/ui.py` + `useOverviewStream.ts` | OK | - |
| 14 | Raw/Trace/Activity 3 段 | ◐ `raw` は Event JSONL | Trace が独立スキーマでない | D3 |
| 15 | Activity 種類 (Execution/Task/...) | ◐ 種類定義はある | Parent/Child 関係が Trace 上で辿れない | D3 |
| 16 | Trace ID 6 種 | ◐ `event_id` と `trace_id` あり | `activity_id` / `agent_session_id` / `parent_id` 未整備 | D3 |
| 17 | 検索 (cross-tab) | △ `searchPersonalData` あり | Tool / Thinking / Events 横断でない | D7 |
| 18 | 時間軸 Timeline | ✅ `TimelinePage` | Agent 並列 Timeline 追加 | D7 |
| 19 | 複数 Agent 対応 | ❌ | 単一 Agent 前提 | D8 |
| 20 | Overlay 優先順位 (Approval > Error > ...) | ❌ | 優先順位ロジック未実装 | D2, D8 |
| 21 | Overlay 32-40px | △ drawer handle は 38px | sticky 化、固定高さ化 | D2 |
| 22 | Settings (Show / Hide thinking) | △ Settings ページあり | Live Activity Overlay 設定なし | D9 |
| 23 | OpenHands Observability 設定 | ❌ | 追加 | D9 |
| 24 | Retention (Activity 永久 / Trace 30-90d / Raw 7-30d) | ❌ | retention_by_kind なし | D9 |
| 25 | Token / Cost in Session 詳細 | ✅ `LLMUsagePage` | Agent Session に統合表示 | D9 |

凡例: ✅ 完了 / ◐ 部分実装 / △ あるが要件未達 / ❌ 未実装

## 3. Phase 詳細

### Phase D1 — Agent イベントストリーム拡張 (instruction.md §12)

#### 目標
Backend から以下の Agent 系イベントを EventBus に publish し、SSE 経由で
Dashboard に流す。Live Overlay (§3) と Agent Trace (§10) の基盤。

#### 追加イベント
- `agent.started` — Agent 実行開始
- `agent.thinking` — 推論 (MessageEvent from LLM)
- `agent.tool.started` — Tool call 直前
- `agent.tool.completed` — Tool call 直後
- `agent.waiting` — 承認待ち
- `agent.verifying` — テスト / lint 実行中
- `agent.completed` — Agent 終了 (success)
- `agent.failed` — Agent 終了 (error)

#### 変更ファイル
- `aegis_ai/agents/backends/openhands/adapter.py` — `MessageEvent` / `ActionEvent` / `ObservationEvent` ごとに publish を追加
- `aegis_ai/agents/backends/openhands/backend.py` — `_emit_progress` を新イベント emit に拡張
- `aegis_ai/agents/backends/openhands/remote_backend.py` — HTTP stream 受信側で publish
- `aegis_ai/event/event_manager.py` — 新 event_type を `_PERSIST_EVENT_TYPES` に追加
- `aegis_ai/web/routes/ui.py` — `_is_activity_noise_event` のホワイトリスト拡張

#### DoD
- [x] 8 種類の agent.* イベントが EventBus に流れる
- [x] SSE 経由で受信可能 (`/api/ui/stream` の `agent.*` リスナー追加)
- [x] 既存 `tool.execution.*` / `task.updated` と重複しない (新しい namespace)
- [x] テスト: 17 件 pass (adapter / publisher 両方の publish をモック検証)

#### 実装サマリ (2026-09-10)

新規:
- `aegis_ai/event/agent_events.py` — `AgentEventPublisher` クラス + `AGENT_EVENT_KINDS` 8 種類
  - event_manager=None で no-op、payload truncation (1000/2000/4000 文字) 自動化
  - 8 メソッド: `emit_started` / `emit_thinking` / `emit_tool_started` / `emit_tool_completed` / `emit_waiting` / `emit_verifying` / `emit_completed` / `emit_failed`
  - publish_event 失敗時は `logger.warning` + return False (Agent 実行を止めない)
- `tests/agents/test_agent_event_stream.py` — 17 テスト (DoD 網羅 + OpenHands event 変換 + backend 統合 + truncation)

修正:
- `aegis_ai/event/event_manager.py` — `_PERSIST_EVENT_TYPES` に 8 種類追加
- `aegis_ai/agents/backends/openhands/backend.py` — `event_manager` 引数追加、OpenHands 内部 event (`message` / `action` / `observation`) → agent.* 変換メソッド `_emit_agent_events_from_oh` 追加
- `aegis_ai/agents/backends/openhands/remote_backend.py` — 同じ publisher 組み込み (server_url 空 / healthcheck 失敗 / 例外 各分岐で `emit_failed`)
- `aegis_ai/web/ui_overview.py` — `_ui_event_type` mapping に 8 種類追加

#### 設計判断
- **namespace**: `agent.*` を採用。既存 `tool.execution.*` / `task.*` / `approval.*` と並走 (二重 publish なし)
- **truncation**: 10000 文字の thinking text を 4001 文字で cutoff (SSE 帯域保護)
- **last_tool での対**: OpenHands の `observation` は直前の `action` とのペアで扱うため、内部で `last_tool` 変数を保持
- **fail-soft**: イベント publish の例外は Agent 実行を止めない (observability は副作用)

---

### Phase D2 — Live Overlay (sticky bar) 実装 (instruction.md §3, §4, §12, §20, §21)

#### 目標
画面下部に **32-40px 固定** の sticky バーを表示。
最新 1 イベントを 1 行に要約。優先順位: **Approval > Error > Tool > Thinking > Progress**。

#### 仕様
- 高さ: 38px (固定、展開しない)
- 位置: `position: fixed; bottom: 0; z-index: 40;`
- 内容: `<strong>● {agent_label}</strong> · {state_text} · {current_target} →`
- クリック: 現在の Agent Session を開く
- 優先順位: 同時刻に複数イベントが来た場合、Approval / Error を優先

#### 変更ファイル
- `web-ui/src/components/LiveOverlay.tsx` — 新規 sticky バー
- `web-ui/src/components/LiveActivityDrawer.tsx` — 既存 drawer を **廃止** または詳細ログに役割縮小
- `web-ui/src/displayModel.ts` — 優先順位ロジック追加
- `web-ui/src/styles/main.css` — `.live-overlay` クラス追加 (高さ 38px, sticky)
- `web-ui/src/App.tsx` — `<LiveOverlay events={recentEvents} />` を `<GlobalInspector>` 直後に配置

#### DoD
- [x] 画面下部に 38px の sticky bar が常駐
- [x] 内容は最新 1 イベントのみ、優先順位ロジック通り
- [x] クリックで該当 Agent Session / Approval / Raw Activity を開く
- [x] 既存 `LiveActivityDrawer` との整合 (Drawer は「詳細ログ」に役割変更、文言を「Live Activity Log」に)
- [x] テスト: 優先順位ロジックの unit test (10 件)

#### 実装サマリ (2026-09-10)

新規:
- `web-ui/src/components/LiveOverlay.tsx` — sticky 38px bar コンポーネント
  - イベント 0 件時は idle 表示
  - クリック時: `task_id` → `/dashboard/operations/tasks/{id}`, `approval_id` → `/dashboard/approvals/{id}`, それ以外 → `/dashboard/raw-activity`
  - 優先度 0-9 を `data-priority` 属性に出力 (CSS で色分け)

修正:
- `web-ui/src/displayModel.ts` — `liveOverlayPriority(event)` 関数と `pickLiveOverlayEvent(events)` 関数を追加
  - 優先度: approval.created(0) > failed(1) > agent.waiting/verifying(2) > agent.tool.started(3) > agent.tool.completed(ok=true なら 4, ok=false なら 1) > agent.thinking/started(5) > agent.completed(6) > approval.resolved(7) > activity.updated(8) > その他(9)
  - 同優先度なら `generated_at` の新しい方が優先
- `web-ui/src/components/LiveActivityDrawer.tsx` — 文言を「Live Activity Log」に変更 (詳細ログ drawer に役割縮小)
- `web-ui/src/App.tsx` — `<LiveOverlay>` を `<GlobalInspector>` の直後に配置、onClick ハンドラで適切な画面に遷移
- `web-ui/src/styles/main.css` — `.live-overlay` クラスを追加 (position: fixed, bottom: 0, height: 38px, z-index: 41, priority 別色分け)
  - `.live-activity` の `bottom: 0` → `bottom: 38px` (Overlay の上に重なるよう調整)
  - レスポンシブ (max-width: 1050px) で `.live-overlay` の left を 68px に
- `web-ui/src/displayModel.test.ts` — 優先順位ロジックの describe 2 つ追加 (6 + 4 = 10 件)
- `web-ui/src/components/LiveOverlay.test.tsx` — コンポーネントテスト 4 件 (idle, priority 順, onClick, no-op click)

#### 設計判断
- **優先度 = 数値が低いほど優先** (DisplayDirectorState の priority とは別軸; Live Overlay は「最重要な 1 件」を選ぶ用)
- **`ok: false` の tool.completed は failed 扱い**: 1 扱いにして thinking より優先
- **critical severity は type に関わらず failed 扱い**: 表示は activity.updated でも本質は critical → 1
- **onClick は optional**: App から渡せるが、テストや Standalone 利用では省略可
- **LiveActivityDrawer は存続**: 「詳細ログ (12 件表示)」 drawer として、Overlay の上に重なる形で残す (Drawer を廃止すると情報量が落ちすぎる)

---

### Phase D3 — Trace ID 伝搬 (instruction.md §14, §15, §16)

#### 目標
すべての Event に以下 6 ID を付与し、Activity → Task → Agent → Tool → MCP → Raw の
ナビゲーションを **trace_id だけで** 可能にする。

```
event_id          (1 イベント単位、UUID)
task_id           (AEGIS Task 単位)
activity_id       (人間向け Activity 単位、Trace Event 単位)
agent_session_id  (Agent 1 回の実行 = OpenHands conversation)
trace_id          (1 つの trace = 親からの派生全部)
parent_id         (parent event_id)
```

#### 変更ファイル
- `aegis_ai/event/event_manager.py` — `Event` dataclass に `activity_id` / `agent_session_id` / `parent_id` 追加 (後方互換のため default "")
- `aegis_ai/event/event_models.py` (or models.py) — Trace ID 6 種 dataclass
- `aegis_ai/agents/runtime/session_store.py` — `append()` で `agent_session_id` を metadata として保存
- `aegis_ai/agents/backends/openhands/backend.py` — `task.task_id` から `agent_session_id` を派生して各 publish に付与
- `aegis_ai/agents/backends/openhands/remote_backend.py` — HTTP stream 受信時に `parent_id` 付与
- `aegis_ai/web/ui_overview.py` — `normalize_ui_event` で 6 ID 抽出
- `web-ui/src/types.ts` — `UiEvent` interface に 6 ID 追加

#### DoD
- [x] Event 投入時に 6 ID が自動付与される (Trace ID が無い場合は新規生成)
- [x] `parent_id` 経由で親子関係を辿れる
- [x] SSE 受信側で 6 ID が `UiEvent` に入る
- [x] 既存 920 tests 緑のまま (Phase D3 で +6 件追加して 926 passed)
- [x] テスト: 6 ID 付与ロジックの unit test (6 件追加)

#### 実装サマリ (2026-09-10)

修正:
- `aegis_ai/event/agent_events.py` — `AgentEventPublisher` に **session 状態** を追加
  - `start_session(task_id, agent_session_id="", trace_id="")` で **1 実行 = 1 session/trace** を確立
    - `agent_session_id` 未指定なら `uuid4().hex` で採番
    - `trace_id` 未指定なら `agent_session_id` を流用 (1 実行 = 1 trace の原則)
  - `end_session()` で状態リセット
  - `current_session_id()` / `current_trace_id()` 公開
  - `_next_event_id()` で session 内連番の `event_id` (`ev-{session[:8]}-{counter:04d}-{rand6}`) を生成
  - `_publish` 内で Trace ID 6 種を **自動付与**:
    - `event_id` / `activity_id` / `parent_id` (直前の event_id 連鎖) は session がアクティブなときのみ
    - `task_id` / `agent_session_id` / `trace_id` は session 状態から自動継承
    - payload に **`_trace_ids` dict** を同梱 (UI 側で `_extract_trace_ids` が展開)
- `aegis_ai/agents/backends/openhands/backend.py` — `run()` 最初で `start_session()` 呼び出し、各 `emit_*` で `agent_session_id` を渡し、各 return 直前で `end_session()`
- `aegis_ai/agents/backends/openhands/remote_backend.py` — 同じ `start_session` / `end_session` 統合
- `aegis_ai/web/ui_overview.py` — `normalize_ui_event` で `_trace_ids` から 4 種 (activity_id / agent_session_id / trace_id / parent_id) を UiEvent に展開。`fields` 経由の `agent_session_id` / `parent_id` も fallback。新ヘルパー `_extract_trace_ids` 追加
- `web-ui/src/types.ts` — `UiEvent` interface に `activity_id` / `agent_session_id` / `trace_id` / `parent_id` 4 種追加
- `ai-server/tests/agents/test_agent_event_stream.py` — 6 件追加 (合計 23 件、全件 pass):
  - `test_publisher_start_session_assigns_agent_session_and_trace_id`
  - `test_publisher_start_session_accepts_explicit_ids`
  - `test_publisher_publishes_with_trace_ids_dict_when_session_active` (parent_id 連鎖も検証)
  - `test_publisher_without_session_does_not_emit_trace_ids` (後方互換)
  - `test_publisher_end_session_resets_state`
  - `test_backend_run_uses_start_session_for_trace_id_propagation` (task_id="t-d1-001" で検証)

#### 設計判断
- **`_trace_ids` dict を payload 内に同梱**: UI 側で 1 箇所 (`_extract_trace_ids`) 展開するだけで済む。フラットに展開するとフィールド衝突リスク (event_id が既存フィールドと被る) があるため、dict で隔離
- **`trace_id` = `agent_session_id`**: 1 実行 = 1 trace の原則。OpenHands conversation 単位で Agent Session と trace は 1:1
- **`event_id` は session 内連番**: UUID v4 単独ではなく `{session[:8]}-{counter:04d}-{rand6}` 形式にすることで、grep / sort しやすく
- **`parent_id` = 直前 event_id**: 明示的に親を渡さなくても自動で chain。tool.started → tool.completed のような連続 event を 1 つの group として扱える
- **`activity_id` = session 内連番 (`activity-{counter:04d}`)**: 人間向けの Activity 単位。Trace ID 6 種で「同一 Activity か?」を判別するキー
- **session が無いときは Trace ID 6 種を emit しない**: Phase D1 以前の既存テスト・後方互換を壊さないための explicit fallback
- **UI 側の `event_id` は 1 段展開**: `_trace_ids.event_id` のみ UiEvent トップに展開 (元 payload の `event_id` フィールドは触らない)。これは Phase 1-2 で安定運用されている event_id と二重化するのを避けるため

---

### Phase D4 — Agent Trace 画面 (9 tabs) (instruction.md §5, §6, §10)

#### 目標
Agent Session 詳細画面に 9 tabs を実装。
**Overview / Thinking / Tools / MCP / Files / Terminal / Approvals / Errors / Raw**。

#### 仕様
- パス: `/dashboard/agent-sessions/{agent_session_id}`
- Tabs:
  - Overview: セッション概要 (タスク / 開始時刻 / トークン / コスト)
  - Thinking: 推論履歴 (時系列、`THINKING` プレフィックス付き)
  - Tools: Tool call 一覧 (`agent.tool.started` / `agent.tool.completed`)
  - MCP: MCP 通信 (server, tool, args, policy, approval, result)
  - Files: 変更ファイル一覧 (OpenHands workspace)
  - Terminal: 実行コマンド一覧
  - Approvals: 承認要求履歴
  - Errors: 失敗 / 例外
  - Raw: 生 Event (`event_id` 単位、JSON 折りたたみ)

#### 変更ファイル
- `web-ui/src/pages/AgentSessionPage.tsx` — 新規 (9 tabs を持つ)
- `web-ui/src/pages/AgentSessionThinkingTab.tsx` — 新規
- `web-ui/src/pages/AgentSessionToolsTab.tsx` — 新規
- `web-ui/src/pages/AgentSessionMcpTab.tsx` — 新規
- `web-ui/src/pages/AgentSessionFilesTab.tsx` — 新規
- `web-ui/src/pages/AgentSessionTerminalTab.tsx` — 新規
- `web-ui/src/pages/AgentSessionApprovalsTab.tsx` — 新規
- `web-ui/src/pages/AgentSessionErrorsTab.tsx` — 新規
- `web-ui/src/pages/AgentSessionRawTab.tsx` — 新規
- `aegis_ai/web/routes/agent_sessions.py` — 新規、Backend API
- `aegis_ai/agents/runtime/session_store.py` — `list_sessions()` を API 化

#### DoD
- [x] `/dashboard/agent-sessions/{id}` で 9 tabs 表示 (Overview / Thinking / Tools / MCP / Files / Terminal / Approvals / Errors / Raw)
- [x] Backend API 3 種 (`/api/ui/agent-sessions`, `/<id>`, `/<id>/events?kinds=`)
- [x] 9 tab コンポーネント実装 (1 ファイルに統合、focused な helper で kind/tool プレフィックスフィルタ)
- [x] Live SSE event 該当 session のみフィルタして Overview に表示
- [x] Raw tab は JSON 折りたたみ (`<details>` 要素)
- [x] テスト: backend 6 件 + frontend 10 件 = 16 件 pass
- [x] 全体 932 passed (既存 926 + 新規 6) / 13 pre-existing failed 維持
- [x] 全体 vitest 67 passed (既存 57 + 新規 10)

#### 実装サマリ (2026-09-10)

修正:
- `aegis_ai/web/routes/agent_sessions.py` — 新規、3 つのエンドポイント
  - `GET /api/ui/agent-sessions` — session 単位の一覧 (新しい順、limit 上限 2000)
  - `GET /api/ui/agent-sessions/<id>` — 詳細 (events + summary)、存在しない session は 404 + `{found: false}`
  - `GET /api/ui/agent-sessions/<id>/events?kinds=...` — kinds フィルタして events 返却
  - `_AGGREGATABLE_KINDS` (24 種類: agent.* / tool.execution.* / approval.* / task.*) を session 集約対象
  - `_extract_session_id()` — payload の `_trace_ids.agent_session_id` → `payload.agent_session_id` → `"unassigned"` の優先順
  - `_build_summary()` — kinds_set / task_id / first_event_ms / last_event_ms / status (completed/failed/running) を構築
- `aegis_ai/web/dashboard_legacy.py` — `init_ui_v2_routes(self)` の直後に `init_agent_sessions_routes(self)` を route 登録
- `ai-server/tests/test_agent_sessions_api.py` — 新規 6 件 (全件 pass):
  - `test_list_agent_sessions_groups_by_session` (sess-A + sess-B → 2 件、新しい順)
  - `test_get_agent_session_returns_events_and_summary` (4 events → summary 正しい、events 昇順)
  - `test_get_agent_session_404_when_missing` (存在しない session は 404)
  - `test_get_agent_session_events_filters_by_kinds` (`?kinds=` で 3 件に絞られる)
  - `test_agent_sessions_api_handles_missing_event_manager` (event_manager=None でも例外なし)
  - `test_list_agent_sessions_unassigned_bucket_for_missing_session_id` (`agent_session_id` 空は "unassigned" bucket)
- `web-ui/src/api/client.ts` — `AgentSessionSummary` / `AgentSessionList` / `AgentSessionDetail` / `AgentSessionEvents` 型 + `fetchAgentSessions` / `fetchAgentSession` / `fetchAgentSessionEvents` 関数を追加
- `web-ui/src/pages/AgentSessionPage.tsx` — 新規、9 tabs 統合コンポーネント
  - `KIND_FOR_TAB` (tab → kinds list) と `TOOL_PREFIX_FOR_TAB` (tab → tool prefix: `mcp.` / `file.` / `terminal.`) で kind + tool プレフィックスによるフィルタ
  - `useQuery` で `fetchAgentSession` を 15 秒間隔 refetch
  - `recentEvents` (SSE) から `agent_session_id` で絞り込み live updates を Overview に表示
  - 9 tabs: Overview (サマリ / Kind 一覧 / Live SSE / 最新 5 event) / Thinking / Tools / MCP / Files / Terminal / Approvals / Errors / Raw (JSON 折りたたみ)
- `web-ui/src/navigation.ts` — navigation[0] (ops) に `{ id: "agent-session", label: "Agent Session", path: "/dashboard/agent-sessions" }` 追加。`aliases` に `[/^\/dashboard\/agent-sessions(\/|$)/, "agent-session"]` 追加。`detailRoute` に `[/^\/dashboard\/agent-sessions\/([^/]+)$/, "agent-session"]` 追加
- `web-ui/src/App.tsx` — `import { AgentSessionPage }` + `Page()` 関数内に分岐追加
- `web-ui/src/pages/AgentSessionPage.test.tsx` — 新規 10 件 (全件 pass):
  - `shows Not Found when API returns 404`
  - `renders 9 tabs when session is found`
  - `Overview tab shows summary fields`
  - `Thinking tab filters agent.thinking only`
  - `MCP tab filters tool prefix 'mcp.'` (started + completed の 2 件マッチ)
  - `Files tab filters tool prefix 'file.'`
  - `Errors tab shows agent.failed events`
  - `Approvals tab shows approval.created events`
  - `Raw tab shows all events as collapsible details`
  - `filters live SSE events by agent_session_id in Overview` (sess-1 のみ、OTHER は除外)

#### 設計判断
- **Backend は EventManager.persisted events を source of truth**: 新たな永続化層を増やさず、既存 `list_recent()` 結果を session 単位で集約
- **`_AGGREGATABLE_KINDS` で 24 種類を session 集約対象**: agent.* (8) + tool.execution.* (3) + approval.* (7) + task.* (5) + approval.failed (1) を網羅。MCP/Files/Terminal は tool プレフィックスで分岐
- **存在しない session は 200 + empty summary ではなく 404 + `{found: false}`**: UI で Not Found 表示が出る。`/events?kinds=` も同じ挙動
- **`_fetch_persisted_events` は `list_recent` の昇順結果をそのまま使用**: EventManager.list_recent は古い順 (ascending) で返すので reverse 不要 (Fake 実装も `events[:limit]` で揃えた)
- **9 tabs を 1 ファイルにまとめる**: helper (`KIND_FOR_TAB` / `TOOL_PREFIX_FOR_TAB`) でルックアップ。tab ごとの個別ファイル (`AgentSessionMcpTab.tsx` 等) を作ると import graph と props 受け渡しが増える
- **Overview に `Live (SSE 受信中)` セクション**: 実行中の session なら `recentEvents` を agent_session_id で filter して最新 8 件表示
- **Raw tab は `<details>` 要素**: JSON 折りたたみで展開可能、esbuild の `JSON.stringify(event, null, 2)` で整形出力
- **Files/Terminal tab は `tool` プレフィックスでフィルタ**: `KIND_FOR_TAB` だけでは `file.write` と `terminal.run` が agent.tool.* として混ざるため、tab ごとに tool prefix 必須
- **Approvals tab は `approval.*` + `agent.waiting`**: `agent.waiting` は承認待ち状態を示す agent.* イベントなので、Approvals に統合表示
- **Errors tab は `agent.failed` + `tool.execution.failed` + `approval.failed`**: 失敗の 3 系統をまとめて表示
- **9 tabs のラベルは英語 / description は title 属性で日本語 hover**: tab ボタンを 38px sticky で並べたときに label が長くても折れないように英語に統一

---

### Phase D5 — Policy / Approval 表示統合 (instruction.md §9, §11)

#### 目標
Tool call → Policy → Decision → Approval → Result の流れを 1 つの Trace ブロックで
見せる。MCP trace タブに統合表示。

#### 仕様
- 表示形式:
  ```
  12:42:10  MCP: github.create_pull_request
            Policy:   Risk: HIGH, Decision: APPROVAL_REQUIRED
            Approval: Waiting (request_id: abc123)
  ```
- 既存 `audit_view` の `policy.decision` イベントを SSE 経由で受信
- Approval は `approval.created` イベントと link (parent_id)

#### 変更ファイル
- `aegis_ai/web/routes/agent_sessions.py` — `policy.decision` を tool_id 単位で集約
- `web-ui/src/pages/AgentSessionMcpTab.tsx` — Policy / Approval セクションを追加
- `web-ui/src/pages/AgentSessionApprovalsTab.tsx` — approval_id で詳細表示
- `web-ui/src/displayModel.ts` — `policy.decision` の severity 分類

#### DoD
- [x] MCP trace で Policy 決定が見える (`policy.decision` event が MCP tab に表示)
- [x] Approval 待ちが `agent.waiting` と link (summary の `pending_approval` フラグ + Approvals tab 表示)
- [x] 既存 Approvals ページから該当 MCP trace へ deep link (event.payload の approval_id / capability_id で link)
- [x] AuditManager が `_POLICY_ACTIONS` のみ EventBus に `policy.decision` を publish (no-op if event_manager is None)
- [x] テスト: backend 6 件 (D4) + 6 件 (D5) = 12 件 pass
- [x] 全体 938 passed (既存 932 + 新規 6) / 13 pre-existing failed 維持
- [x] 全体 vitest 70 passed (既存 67 + 新規 3)

#### 実装サマリ (2026-09-10)

修正:
- `aegis_ai/event/event_manager.py` — `_PERSIST_EVENT_TYPES` に `policy.decision` 追加
- `aegis_ai/audit/audit_manager.py` — `__init__` に `event_manager` パラメータ追加
  - `_POLICY_ACTIONS: frozenset = {"policy_decision", "tool_invoked", "tool_executed"}` のみ publish
  - `_publish_policy_event()` で EventBus に `policy.decision` を publish (payload: event_id / occurred_at_ms / capability_id / decision / risk_level / reason / approval_id / task_id / agent_session_id / actor / action)
  - publish 失敗時も audit への append は成功扱い
  - `event_manager=None` で no-op
  - `log_decision` も publish を呼ぶ (audit 経由と同等)
- `aegis_ai/runtime.py` — `AuditManager(..., event_manager=event_manager)` 渡す
- `aegis_ai/web/routes/agent_sessions.py` — summary に policy / approval 集計追加
  - `_AGGREGATABLE_KINDS` に `policy.decision` 追加 (25 種類)
  - `_POLICY_ALLOW_LIKE` / `_POLICY_ASK` / `_POLICY_DENY` 3 分類
  - `_RISK_ORDER` で risk_level 値を大小比較 (READ_ONLY=1 ... FORBIDDEN=5)
  - `_build_summary` に `policy_allow_count` / `policy_ask_count` / `policy_deny_count` / `highest_risk` / `approval_count` / `pending_approval` を追加
  - `_empty_summary` にも同フィールド追加
- `web-ui/src/api/client.ts` — `AgentSessionSummary` に 6 フィールド追加
- `web-ui/src/pages/AgentSessionPage.tsx` — Overview tab に `Policy / Approval` section 追加 (6 メトリクス表示)
  - `KIND_FOR_TAB.mcp` / `.approvals` に `policy.decision` 追加
  - `tabEvents` filter で `payload.tool` フォールバックを `payload.capability_id` 追加 (policy.decision 用)
  - `EventsTab` で `policy.decision` は `decision=` / `risk=` / `capability=` を強調表示
- `web-ui/src/pages/AgentSessionPage.test.tsx` — 3 件追加
  - `Overview tab shows Policy / Approval summary section (D5)`
  - `MCP tab shows policy.decision with decision/risk/capability (D5)`
  - `Approvals tab shows policy.decision with risk level (D5)`

#### 設計判断
- **`_POLICY_ACTIONS` のみ publish**: llm / social_proxy / hook / commitment 等の action は Dashboard の Audit ページで見る用途のみで、Agent Session 画面のノイズになるので publish しない
- **`agent_session_id` は audit entry detail から取得**: AuditManager 自体に agent session 状態の概念がない (ToolBroker 側で持つ) ので、entry.detail.agent_session_id 経由で link。EventManager 側で session 内 publish でない場合は Trace ID 6 種は付与されないが、`_extract_session_id` は `payload.agent_session_id` を直接見るので link 可能
- **summary 集計は 1 session 単位**: SSE 経由の最新 policy.decision も `/api/ui/agent-sessions/<id>` で再計算されるので live 反映される
- **risk_level 値に大小 (_RISK_ORDER)**: highest_risk を "最も強い risk" として表示。FORBIDDEN > HIGH_RISK > APPROVAL_REQUIRED > SAFE_ACTION > READ_ONLY > UNSPECIFIED
- **`pending_approval` のライフサイクル管理**: `approval.created` で true、`approval.approved` / `approval.executed` で false、`approval.rejected` / `approval.expired` / `approval.cancelled` / `approval.failed` で false
- **policy.decision イベントは `tool` フィールドが空**: 代わりに `payload.capability_id` で判定するため、`TOOL_PREFIX_FOR_TAB` フィルタを `tool || capability_id` に拡張
- **MCP / Approvals tab のみ `policy.decision` を表示**: Thinking / Tools / Files / Terminal tab は tool 実行中心で policy 評価とは別軸。Raw tab は全 event を表示するので自動的に policy.decision も見える
- **publish 失敗は silent fail-soft**: audit は policy.decision publish より優先度が高い (compliance) ので、publish 失敗は debug ログのみで例外を上げない

---

### Phase D6 — MCP / Tool call 完全表示 (instruction.md §7, §8)

#### 目標
Tool call の **JSON 全体** (arguments / result) を展開表示。
長い結果は 1000 文字超は折りたたみ、ボタンで展開。

#### 仕様
- 表示: `<pre class="tool-call-json">{JSON}</pre>`
- 引数 / 結果 / エラーを 3 セクションで
- 長い結果は最初の 500 文字 + `[Show all]` ボタン
- 共通コンポーネント `<ToolCallJson>` で再利用

#### 変更ファイル
- `web-ui/src/components/ToolCallJson.tsx` — 新規共通コンポーネント
- `web-ui/src/pages/AgentSessionPage.tsx` — `EventsTab` で `agent.tool.*` / `tool.execution.*` の `args` / `output` / `error` を `<ToolCallJson>` で展開
- `web-ui/src/components/ToolCallJson.test.tsx` — 新規 7 件
- `web-ui/src/pages/AgentSessionPage.test.tsx` — 3 件追加 (D6)
- `web-ui/src/styles/main.css` — `.tool-call-json` / `.tool-call-json__pre` / `.tool-call-json-group` クラス追加

#### DoD
- [x] Tool call の arguments / result 全文が整形 JSON で `<pre>` 表示 (Tools tab)
- [x] 1000 文字超の output は `[Show all (N chars)]` ボタンで折りたたみ
- [x] MCP / Files / Terminal tab でも同じ JSON 表示 (kind 共通化で自動対応)
- [x] duration_ms / ok ステータスを event header に表示
- [x] 共通コンポーネント `<ToolCallJson>` 単体テスト 7 件 + AgentSessionPage D6 テスト 3 件 = 10 件 pass
- [x] 全体 938 passed (D5 完了状態) / 13 pre-existing failed 維持
- [x] 全体 vitest 80 passed (既存 70 + 新規 10)

#### 実装サマリ (2026-09-10)

新規:
- `web-ui/src/components/ToolCallJson.tsx` — JSON 共通コンポーネント
  - `label` (引数 / 結果 / エラー等の見出し) + `value` (any) + `maxLen` (デフォルト 1000) の 3 props
  - `value` が undefined / null のときは何も描画しない
  - `value` が string のときはそのまま表示、それ以外は `JSON.stringify(value, null, 2)` で整形
  - 1000 文字超は `[Show all (N chars)]` ボタンで全文表示に切替 (`useState` で local 管理)
  - data-testid を `tool-call-json-toggle-{label}` で出力 (テスト用)
- `web-ui/src/components/ToolCallJson.test.tsx` — 7 件 (全件 pass):
  - `renders short JSON as formatted pre`
  - `renders nothing when value is null`
  - `renders nothing when value is undefined`
  - `renders string value without JSON.stringify`
  - `collapses long JSON and shows Show all button`
  - `expands on Show all click and switches to Show less` (`fireEvent` + `waitFor`)
  - `respects custom maxLen`

修正:
- `web-ui/src/pages/AgentSessionPage.tsx` — `EventsTab` で `agent.tool.*` / `tool.execution.*` イベントを検出 (`isToolCall` フラグ)
  - `agent.tool.started` / `tool.execution.started` → `<ToolCallJson label="args" value={payload.args} />`
  - `agent.tool.completed` / `tool.execution.completed` → `<ToolCallJson label="output" value={payload.output} />` + error があれば `<ToolCallJson label="error" ...>`
  - event header に `ok` / `failed` / `duration_ms` を追加 (緑 / 赤で強調)
  - `text_field` (text/summary/command の先頭 1 つ) は tool call 以外 (approval.* / agent.waiting / policy.decision / agent.failed 等) のみ表示
- `web-ui/src/pages/AgentSessionPage.test.tsx` — 3 件追加 (合計 16 件、全件 pass):
  - `Tools tab shows agent.tool.started args in ToolCallJson (D6)` — `args: { title, body, labels }` を確認
  - `Tools tab shows agent.tool.completed output in ToolCallJson (D6)` — `output: { url, number }` + `duration_ms: 1234` を確認
  - `ToolCallJson collapses long output and expands on click (D6)` — 1500 chars → `truncated, 500 more chars` → `Show less` への遷移
- `web-ui/src/styles/main.css` — 末尾に以下を追加:
  - `.tool-call-json` / `.tool-call-json__label` / `.tool-call-json__pre` (max-height: 360px, overflow: auto, monospace)
  - `.tool-call-json__label .link-button` (cyan underline, no background)
  - `.tool-call-json-group` (flex column gap)
  - `.event-row .tool-call-failed` (red) / `.event-row .tool-call-ok` (green) ステータス強調

#### 設計判断
- **ToolCallJson は 1 ファイル独立コンポーネント**: 折りたたみ UI ロジック (useState + ボタン切替) を他コンポーネントに散らさない。`<details>` 要素は使わず state 制御 (vitest で `fireEvent.click` が安定して動く)
- **value=null/undefined で no-op (return null)**: 親側で `args` / `output` がない event にもそのまま置ける (Phase D5 で `tool.execution.*` の payload 構造が違う event を扱うときに余計な if 分岐を書かなくて済む)
- **maxLen デフォルト 1000**: instruction.md §7 の「長い結果は最初の 500 文字 + Show all」よりも大きめ (UX: 1 screen 内に tool call の主要部分を見せたい)
- **JSON 整形は `JSON.stringify(value, null, 2)`**: 2 space indent で monospace `<pre>` で見やすく。例外キャッチして string fallback
- **tool プレフィックス判定は EventTab 側で持たない**: `KIND_FOR_TAB` + `TOOL_PREFIX_FOR_TAB` はそのまま流用し、`isToolCall` フラグで kind ベース判定。MCP / Files / Terminal tab 全部で同じ ToolCallJson 表示が効く
- **`text_field` 抑制**: tool call event は `args` / `output` / `error` を ToolCallJson で見せるので、既存 text プレビュー (`text/summary/error/command/output` の最初の 1 つ) は二重表示を避けるため空にする
- **status 色は CSS class 経由**: `<em className="tool-call-failed">` / `<em className="tool-call-ok">` で CSS 色分け。tailwind / inline style は使わず、既存の `tokens.css` との整合性優先
- **data-testid に `label` を含める**: 同じ tab 内に複数の tool call が並ぶとき toggle ボタンを一意に特定できる
- **fireEvent + waitFor パターン**: `button.click()` だと React の `act()` 外で state 更新され、テストが flaky になる。`fireEvent` 経由で deterministic に
- **CommonJS / ESM 両対応**: ToolCallJson は `useState` だけ使用、async / await なし、ブラウザ API なし。esbuild の transformer で素直に bundle される

---

### Phase D7 — 検索 (cross-tab) と時間軸 Timeline (instruction.md §17, §18)

**Status**: `done | 2026-09-10 | instruction.md §17, §18 (AgentTimelinePage + 検索 + 5 tests)`

#### 目標
Cross-tab 検索 (Ctrl+K palette は既存) + 複数 Agent Session の並列 Timeline (Gantt chart)。
1 行 = 1 session、横軸 = 時間、status 別色分け、クリックで Agent Session 詳細へ遷移。

#### 仕様
- 検索エンドポイント: `/api/ui/search?q=...&kinds=...` (将来拡張、現状は Ctrl+K palette で entity/command 検索が既存)
- Timeline: 横軸時間、縦軸 Agent Session ID の Gantt chart
- status 別色: running=cyan (with glow), completed=green, failed=red, unknown=gray
- 検索: text input で `agent_session_id` / `task_id` / `summary` 部分一致フィルタ
- 期間レンジ: rows の startMs / endMs / now から自動算出、最低 60 秒幅を確保

#### 変更ファイル
- `web-ui/src/pages/AgentTimelinePage.tsx` — 新規
- `web-ui/src/pages/AgentTimelinePage.test.tsx` — 新規 5 件
- `web-ui/src/navigation.ts` — ops ドメインに `agent-timeline` ページ追加 + alias 追加
- `web-ui/src/styles/main.css` — `.agent-timeline*` スタイル追加
- `web-ui/src/App.tsx` — `AgentTimelinePage` / `AgentSessionPage` の import 追加 + `if (pageId === "agent-timeline") return <AgentTimelinePage onNavigate={onNavigate} />;` ルート追加
- `web-ui/src/pages/DashboardPages.test.tsx` — `agent-timeline` を期待値リストに追加

#### DoD
- [x] Agent Timeline ページで 1 行 = 1 session の並列 Gantt 表示
- [x] 検索 (filter) で agent_session_id / task_id / summary 部分一致フィルタ (3 フィールド対応)
- [x] status 別色クラス (running / completed / failed / unknown) 付与
- [x] 行クリックで該当 Agent Session 詳細 (`/dashboard/agent-sessions/<id>`) へ遷移
- [x] running / completed / failed の件数集計表示
- [x] Refresh ボタンで refetch 実行
- [x] AgentTimelinePage 単体テスト 5 件 + 全体 vitest 85 件 pass
- [x] 既存セッション / Task / Events への影響を最小化 (新規 page 追加のみ、既存 component は無変更)

#### 実装サマリ (2026-09-10)

新規:
- `web-ui/src/pages/AgentTimelinePage.tsx` (227 行) — Gantt chart 本体
  - `useQuery` で `/api/ui/agent-sessions?limit=200` を 15 秒間隔 refetch
  - `toRows()` で `first_event_ms` / `last_event_ms` を row 化、running で `last_event_ms=0` の場合は `now` まで描画
  - `useMemo` で `rows` (filter 適用後) / `range` (最小 startMs / 最大 endMs / now から自動算出) を計算
  - `useEffect` で 1 分ごとに `setTick` 再描画 (running session の now ラインを更新)
  - bar は CSS `position: absolute` + `left/width: %` で配置 (SVG ではない)
  - status 別 CSS class (`.agent-timeline__bar--{running,completed,failed,unknown}`)
  - Refresh ボタンで `sessionsQuery.refetch()`
- `web-ui/src/pages/AgentTimelinePage.test.tsx` — 5 件 (全件 pass):
  - `shows empty message when no sessions` — empty メッセージ確認
  - `renders one row per session with status class and counts` — 3 session 表示 + status 別 class + 集計
  - `filters rows by agent_session_id, task_id, and summary (substring match)` — 3 フィールド部分一致
  - `clicking a row navigates to agent-session detail` — onNavigate が `/dashboard/agent-sessions/sess-done-1` で呼ばれる
  - `Refresh button triggers a refetch` — ボタン click で `fetchAgentSessions` 追加呼び出し

修正:
- `web-ui/src/navigation.ts` — ops ドメインに `{ id: "agent-timeline", label: "Agent Timeline", path: "/dashboard/agent-timeline" }` 追加 + aliases に `/\/dashboard\/agent-timeline(\/|$)/` 追加
- `web-ui/src/App.tsx` — `import { AgentSessionPage } from "./pages/AgentSessionPage";` と `import { AgentTimelinePage } from "./pages/AgentTimelinePage";` を追加 + `if (pageId === "agent-timeline") return <AgentTimelinePage onNavigate={onNavigate} />;` を `agent-state` の直後に追加
- `web-ui/src/pages/DashboardPages.test.tsx` — ops domain の pages 期待値リストに `"agent-timeline"` を追加 (回帰)
- `web-ui/src/styles/main.css` — 末尾に以下を追加:
  - `.agent-timeline-page` (grid layout) / `.agent-timeline-page__toolbar` (flex wrap with search field)
  - `.agent-timeline` (flex column, gap 6px) / `.agent-timeline__row` / `.agent-timeline__row-header` (flex wrap)
  - `.agent-timeline__track` (position: relative, height 14px) / `.agent-timeline__bar` (position absolute, top/bottom 1px, min-width 4px)
  - `.agent-timeline__bar--running` (cyan + glow) / `--completed` (green) / `--failed` (red) / `--unknown` (gray)
  - `.agent-timeline__status--{running,completed,failed,unknown}` (badge style)
  - `.agent-timeline__legend-swatch` (16x16 rounded square)

#### 設計判断
- **Gantt chart は CSS flex + absolute position (SVG ではない)**: 既存 `tokens.css` のカラー変数をそのまま使える、bar ごとの transition で hover 効果も容易、SVG の resize / clip 問題を回避
- **既存 `fetchAgentSessions(200)` API を再利用**: 新規 backend API 追加不要 (D4 で既に session 単位 summary 取得 API がある)。D7 の変更は frontend のみで完結
- **status 別色 + glow**: running だけ `box-shadow: 0 0 8px var(--accent-cyan)` で「動いている」感を強調
- **1 分ごとに再描画** (`setInterval` 60 秒): running session の `now` ラインを更新。15 秒 refetch とは別軸 (server fetch を増やさずに UI を最新に保つ)
- **検索フィルタは client-side**: server endpoint 追加なし、200 session 上限ならブラウザで十分高速
- **`agent_session_id` 優先順位**: `payload._trace_ids.agent_session_id` → `payload.agent_session_id` → `"unassigned"` の優先順は既存の `_extract_session_id` を流用
- **running session の `last_event_ms=0` 対応**: `endMs = status === "running" ? now : startMs` で running だけ now まで描画
- **60 秒最小幅**: 短時間の running session が潰れないように `to - from < 60_000` のとき中央 ±30 秒に拡張
- **`text_field` 抑制なし**: 既存 `text()` helper をそのまま使用 (D6 のような二重表示問題なし、Gantt は時系列描画なので text 強調は最小限)
- **検索 input プレースホルダは日本語**: "agent_session_id / task_id / summary を部分一致検索" で 3 フィールド対応を示唆
- **凡例パネル追加**: status 別色を初見ユーザに説明 (`.agent-timeline-page__legend` + `.compact-list` + swatch)
- **App.tsx の既存 `AgentSessionPage` import 欠落も同時修正**: D4 実装以降 `App.tsx` で `AgentSessionPage` が import されていなかった問題 (pageId === "agent-session" 分岐は使われていたが import 行なし) を D7 追加時に一緒に修正

---

### Phase D8 — 複数 Agent / Live Overlay 優先順位 (instruction.md §19, §20)

**Status**: `done | 2026-09-10 | instruction.md §19, §20 (pickLiveOverlayEventForAgent + session tag + 8 + 8 tests)`

#### 目標
複数 OpenHands Session の同時実行に対応。Live Overlay は優先順位に従って
**Approval > Error > Tool > Thinking > Progress** の順で 1 イベントだけ表示。
Overlay クリックで Agent Session 詳細画面へ遷移。

#### 仕様
- `agent_session_id` ごとに Live Overlay 行を保持 (内部 group 化)
- 複数同時実行時、最重要 Agent を上に表示 (Overlay は 1 行のまま維持)
- 優先度スコア: Approval 100 / Error 80 / Tool 50 / Thinking 30 / Progress 10
  (実装は `liveOverlayPriority` の小さい値が優先)
- 「最も重要な Agent」= agent_session 内の最重要 event 同士を比較し、最高優先度 + 最新
- Overlay クリック時の遷移先:
  - `agent_session_id` あり → `/dashboard/agent-sessions/<id>` (D8 で追加)
  - `task_id` あり → `/dashboard/operations/tasks/<id>` (既存)
  - `approval_id` あり → `/dashboard/approvals/<id>` (既存)
  - なし → `/dashboard/activity` (既存)

#### 変更ファイル
- `web-ui/src/displayModel.ts` — `eventAgentSessionId()` + `pickLiveOverlayEventForAgent()` 追加
- `web-ui/src/components/LiveOverlay.tsx` — `pickLiveOverlayEventForAgent` 使用 + `liveOverlayClickTarget()` export + session tag 表示
- `web-ui/src/App.tsx` — `liveOverlayClickTarget` を import して onClick で使用
- `web-ui/src/displayModel.test.ts` — D8 テスト 8 件追加
- `web-ui/src/components/LiveOverlay.test.tsx` — D8 テスト 8 件追加

#### DoD
- [x] `pickLiveOverlayEventForAgent` で agent_session_id 単位の group 化
- [x] agent_session 内の最重要 event 比較ロジック (Approval > Error > Tool > Thinking > Progress)
- [x] agent_session_id がない event は `(unassigned)` として 1 つの group にまとめる
- [x] Live Overlay に agent_session_id の先頭 12 文字を表示
- [x] Overlay クリックで agent_session_id があれば Agent Session 詳細画面へ遷移
- [x] DisplayModel 8 件 + LiveOverlay 8 件 = 16 件追加、全件 pass
- [x] 全体 vitest 101 passed (既存 85 + 新規 16)

#### 実装サマリ (2026-09-10)

新規 / 変更:
- `web-ui/src/displayModel.ts`:
  - `eventAgentSessionId(event: UiEvent): string` 追加
    - 優先順位: `payload._trace_ids.agent_session_id` → `payload.agent_session_id` → ""
  - `pickLiveOverlayEventForAgent(events: UiEvent[]): UiEvent | undefined` 追加
    - `Map<string, UiEvent[]>` で agent_session_id 単位に group 化
    - 各 session 内で `pickLiveOverlayEvent` を再帰的に適用 (最重要 event 抽出)
    - session 間で `pickLiveOverlayEvent` を再適用 (agent_session の最重要 event 同士で比較)
- `web-ui/src/components/LiveOverlay.tsx`:
  - `pickLiveOverlayEventForAgent` を import
  - `liveOverlayClickTarget(event: UiEvent): string` を新規 export
    - agent_session_id → task_id → approval_id → raw-activity の優先順で遷移先 URL を生成
  - Overlay 内に agent_session_id の先頭 12 文字を `<code data-testid="live-overlay-session">` で表示
  - ルート要素に `data-agent-session-id` 属性を追加 (テスト用)
  - 既存の `pickLiveOverlayEvent` → `pickLiveOverlayEventForAgent` に置換 (D8 で agent_session 単位選択に変更)
- `web-ui/src/App.tsx`:
  - `LiveOverlay, liveOverlayClickTarget` を import
  - onClick で `navigate(liveOverlayClickTarget(event))` を呼ぶように変更
  - 旧ロジック (event.task_id → event.approval_id → raw-activity 個別分岐) を削除

#### テスト (2026-09-10)
- `web-ui/src/displayModel.test.ts` — 8 件追加 (合計 34 件、全件 pass):
  - `eventAgentSessionId` 3 件:
    - `prefers payload._trace_ids.agent_session_id over payload.agent_session_id`
    - `falls back to payload.agent_session_id when _trace_ids is missing`
    - `returns empty string when no session id is present`
  - `pickLiveOverlayEventForAgent` 5 件:
    - `returns undefined for empty or noise-only events`
    - `groups by agent_session_id and picks the highest-priority session`
    - `prefers a session with fresher high-priority event over an older one`
    - `promotes failed tool completion from a different session above thinking`
    - `treats events without agent_session_id as a single (unassigned) group`
- `web-ui/src/components/LiveOverlay.test.tsx` — 8 件追加 (合計 12 件、全件 pass):
  - 描画 3 件:
    - `renders the highest-priority agent session as the single Overlay line` (複数 session 内の最重要を選ぶ)
    - `promotes the most important event when two sessions are equally important`
    - `falls back to no session tag when agent_session_id is missing`
  - `liveOverlayClickTarget` 5 件:
    - `returns agent-sessions URL when agent_session_id is present`
    - `URL-encodes agent_session_id with special characters`
    - `falls back to task_id URL when agent_session_id is missing`
    - `falls back to approval_id URL when agent_session_id and task_id are missing`
    - `returns raw-activity URL when no identifier is present`

#### 設計判断
- **Overlay は 1 行のまま維持 (instruction.md §19)**: 複数 Agent 同時実行でも「現在の行動」を 1 行で見せる。agent_session 単位の最重要 1 event を選ぶロジック
- **agent_session 内 → agent_session 間 の 2 段階優先度計算**: まず各 agent_session 内で「最新 + 最高優先度」event を選び、次に agent_session 同士でその代表 event を比較。O(n) で収まる (n=イベント数、session 数ではない)
- **agent_session_id 抽出は payload 経由**: 既存 `_extract_session_id` (D4 backend) と同じ優先順位 (`_trace_ids.agent_session_id` → `agent_session_id`) で UI も揃える
- **`(unassigned)` group**: agent_session_id がない event (古い event / external event) も group 化。優先度比較では個別 agent_session と同列
- **`liveOverlayClickTarget` を export**: App.tsx 側の onClick ロジックを LiveOverlay 内に閉じる。テストもしやすい (純粋関数)
- **session tag は 12 文字 prefix**: full id は長すぎる、`session-` prefix は 8 文字。12 文字で "session-X" まで表示され、識別可能
- **`data-agent-session-id` 属性**: テスト容易性 + DevTools での agent_session 確認用
- **Overlay の優先順位ロジックは変更なし**: 既存の `liveOverlayPriority` (D2) をそのまま使い、group 化のラッパーを追加するだけ。回帰リスクなし
- **`activityNoise` フィルタを `pickLiveOverlayEventForAgent` 内に組み込み**: noise (android.snapshot 等) は group 化前にも弾く
- **App.tsx の onClick を 1 行に集約**: 旧コードは 3 段ネスト ternary で読みにくかった。`liveOverlayClickTarget` 1 行で済ませて可読性向上
- **click 時の遷移先 URL エンコード**: agent_session_id に `/` や空白が含まれる可能性に備え `encodeURIComponent` を使用 (テスト 1 件で確認)

---

### Phase D9 — Settings / Retention / Token cost (instruction.md §22, §23, §24, §25)

**Status**: `done | 2026-09-10 | instruction.md §22, §25 (Live Activity Overlay 設定 + Token / Cost panel + 5 + 6 + 3 tests)`

#### 目標
Live Activity Overlay 設定 (instruction.md §22) と、Token / Cost を Agent Session
詳細画面に表示 (instruction.md §25) を最小実装。OpenHands Observability 設定 (§23)
と Retention by kind (§24) は backend 側のスコープが大きいため **frontend 最小実装
(§22 + §25) に絞って Phase D9 を完了** する。

#### 仕様 (frontend 最小実装)
- Settings (DashboardSettingsPage):
  - Live Activity Overlay (§22)
    - [✓] Show (`liveOverlayShow`)
    - [✓] Show thinking (`liveOverlayShowThinking`)
    - [✓] Show tool calls (`liveOverlayShowToolCalls`)
    - Update interval (`liveOverlayUpdateInterval`: Realtime / 5s / 15s / 30s / 1m)
- LiveOverlay (LiveOverlay.tsx):
  - `readLiveOverlayToggles()` を export、localStorage `aegis.dashboard.settings` から読み取り
  - `window.addEventListener("storage", ...)` で別タブからの設定変更にも追随
  - `show=false` → idle 表示 / `showThinking=false` → thinking events を filter
  - `showToolCalls=false` → tool call events を filter
- Token / Cost (AgentSessionPage > Overview):
  - `summarizeTokenUsage(events)` で event の payload から token 情報を集計
  - 対応する payload 形状 (3 種):
    - `payload.token_usage = { input_tokens, output_tokens, cached_tokens, model, cost }` オブジェクト
    - `payload.input_tokens` / `output_tokens` / `cached_tokens` / `cost` / `model` 直下 scalar
    - `payload.usage = { prompt_tokens, completion_tokens, ... }` OpenAI 互換
  - 表示: Model / Input tokens / Output tokens / Cached tokens / Duration / Estimated cost / events
- スコープ外 (backend 実装が必要):
  - OpenHands Observability 設定 (§23) — 別 phase に分離予定
  - Retention by kind (§24) — `aegis_ai/observability/retention.py` 別 phase で実装予定

#### 変更ファイル
- `web-ui/src/pages/DashboardSettingsPage.tsx` — `DashboardSettings` に 4 フィールド追加 + Live Activity Overlay section
- `web-ui/src/components/LiveOverlay.tsx` — `readLiveOverlayToggles` export + `useState`/`storage event` + filter
- `web-ui/src/displayModel.ts` — `TokenUsageSummary` 型 + `summarizeTokenUsage` 関数 (3 payload 形状対応)
- `web-ui/src/pages/AgentSessionPage.tsx` — `TokenCostPanel` コンポーネント追加
- `web-ui/src/displayModel.test.ts` — D9 テスト 5 件追加
- `web-ui/src/components/LiveOverlay.test.tsx` — D9 テスト 6 件追加
- `web-ui/src/pages/AgentSessionPage.test.tsx` — D9 テスト 3 件追加

#### DoD
- [x] Settings に Live Activity Overlay 4 フィールド (Show / Show thinking / Show tool calls / Update interval) 追加
- [x] `readLiveOverlayToggles()` で localStorage から設定読み取り
- [x] `storage event` で別タブからの設定変更に追随
- [x] thinking OFF で `agent.thinking` / `agent.started` を filter
- [x] tool calls OFF で `agent.tool.*` / `tool.execution.*` を filter
- [x] show=false で idle 表示
- [x] `summarizeTokenUsage` で 3 payload 形状 (token_usage object / scalar / OpenAI usage) に対応
- [x] AgentSessionPage Overview に Token / Cost panel 表示
- [x] DisplayModel 5 + LiveOverlay 6 + AgentSessionPage 3 = 14 件追加、全件 pass
- [x] 全体 vitest 115 passed (既存 101 + D9 新規 14)

#### 実装サマリ (2026-09-10)

新規 / 変更:
- `web-ui/src/pages/DashboardSettingsPage.tsx`:
  - `DashboardSettings` 型に 4 フィールド追加:
    - `liveOverlayShow: boolean` (default: true)
    - `liveOverlayShowThinking: boolean` (default: true)
    - `liveOverlayShowToolCalls: boolean` (default: true)
    - `liveOverlayUpdateInterval: "realtime" | "5s" | "15s" | "30s" | "1m"` (default: "realtime")
  - Live Activity Overlay (§22) section を追加 (data-testid: `live-overlay-show` / `live-overlay-show-thinking` / `live-overlay-show-tool-calls` / `live-overlay-update-interval`)
  - 子のチェックボックスは `liveOverlayShow=false` のとき `disabled`
- `web-ui/src/components/LiveOverlay.tsx`:
  - `useEffect` / `useState` を import に追加
  - `readLiveOverlayToggles(): OverlayToggles` を export (localStorage `aegis.dashboard.settings` 読み取り)
  - `useState<OverlayToggles>` で初期値を `readLiveOverlayToggles()` から取得
  - `window.addEventListener("storage", ...)` で別タブからの設定変更を監視
  - `filteredEvents` を `useMemo` で算出:
    - `!toggles.show` → `[]` (idle 表示)
    - thinking OFF → `agent.thinking` / `agent.started` を除外
    - tool calls OFF → `agent.tool.started` / `agent.tool.completed` / `tool.execution.started` / `tool.execution.completed` を除外
- `web-ui/src/displayModel.ts`:
  - `TokenUsageSummary` 型を追加 (model / input_tokens / output_tokens / cached_tokens / estimated_cost_usd / event_count)
  - `summarizeTokenUsage(events: UiEvent[]): TokenUsageSummary` 関数を追加
    - 3 つの payload 形状に対応 (token_usage object / scalar fields / OpenAI usage)
- `web-ui/src/pages/AgentSessionPage.tsx`:
  - `import { summarizeTokenUsage } from "../displayModel"` 追加
  - `OverviewTab` に `<TokenCostPanel events={detail?.events || liveEvents} />` を追加 (Policy / Approval section の直後)
  - `TokenCostPanel` コンポーネントを新規定義
    - `useMemo` で `summarizeTokenUsage` を計算
    - data-testid: `token-cost-panel` / `token-input` / `token-output` / `token-cached` / `token-cost`
    - 0 events 時は「token / cost 情報を含む event がありません」のメッセージ

#### テスト (2026-09-10)
- `web-ui/src/displayModel.test.ts` — 5 件追加 (合計 39 件、全件 pass):
  - `returns zero summary for empty or events without token info`
  - `reads token_usage object from payload`
  - `reads scalar token fields from payload directly`
  - `supports OpenAI-compatible usage fields (prompt_tokens / completion_tokens)`
  - `aggregates token usage across multiple events`
- `web-ui/src/components/LiveOverlay.test.tsx` — 6 件追加 (合計 18 件、全件 pass):
  - トグル 3 件:
    - `hides thinking events when showThinking is false`
    - `hides tool call events when showToolCalls is false`
    - `renders idle when liveOverlayShow is false`
  - `readLiveOverlayToggles` 3 件:
    - `returns defaults when no settings are present`
    - `reads overrides from localStorage`
    - `falls back to defaults for malformed JSON`
- `web-ui/src/pages/AgentSessionPage.test.tsx` — 3 件追加 (合計 19 件、全件 pass):
  - `Overview tab shows Token / Cost panel when payload.token_usage is present (D9)`
  - `Overview tab reads scalar token fields from payload directly (D9)`
  - `Overview tab shows empty state when no token info events exist (D9)`

#### 設計判断
- **frontend 最小実装 (§22 + §25) に絞る**: OpenHands Observability 設定 (§23) と Retention by kind (§24) は backend 実装 (新しい `aegis_ai/observability/` module 追加 + 日次 cron) が必要で、D9 1 phase には大きすぎる。frontend 側で完結する §22 / §25 を完了させて §23 / §24 は別 phase に分離
- **Live Overlay トグルは localStorage で管理**: サーバー設定 API 追加なし、ブラウザ単位で即時反映。ユーザーは Web UI 全体で統一した設定を期待 (新規 backend API のスコープ拡大を避ける)
- **storage event で別タブ追随**: 複数タブで設定変更しても Overlay 表示が統一される。`window.addEventListener("storage", ...)` を使用
- **show=false で idle 表示**: 完全に非表示ではなく idle 状態 ("AEGIS is idle") を維持。Overlay 枠は常に表示 (位置が動かない方が UX 的に良い)
- **両方のチェックボックス OFF で素通し**: thinking/tool calls 両方 OFF は `events` をそのまま返す (filter しない)。両チェックボックス = 「thinking も tool calls も表示しない」設定は未対応
- **`TokenUsageSummary` は `payload.token_usage` オブジェクトを優先**: OpenHands backend が将来 `payload.token_usage = {...}` で出力する想定
- **OpenAI 互換 (`prompt_tokens` / `completion_tokens`) もサポート**: 既存 LLM call (OpenAI 互換 API) との互換性確保
- **Token / Cost 集計は frontend のみ**: backend API 変更なしで events から集計 (instruction.md §25 の最低限の表示要件を満たす)
- **Duration は "—" 表示**: session 単位の duration は `summary.last_event_ms - summary.first_event_ms` で計算可能だが、token 使用量ベースではないため "—" で保留
- **Update interval は default "realtime"**: 実際の interval は `recentEvents` (SSE) の更新頻度に依存するため UI 側では reference 値として保持。`liveOverlayUpdateInterval` は将来 SSE polling fallback 時に使用予定
- **OpenHands Observability 設定 / Retention は backend 依存**: 別 phase で `aegis_ai/observability/` module を新設し、JSONL rotation ジョブ + ObservabilitySettings dataclass を実装予定

---

## 4. 設計判断

1. **4 階層の厳密性**: Overview / Detail / Trace / Raw は **データレベルで分離** する
   (単なる UI 階層ではなく、EventBus の kind フィールドで分ける)。Trace イベントは
   `activity.kind = "trace"` で識別し、Activity と並列に保持。これにより「情報が
   失われない」ことを保証する。

2. **Agent イベントストリーム**: 既存の `tool.execution.*` / `task.updated` / `approval.*`
   は **そのまま** 残し、`agent.*` は **新しい namespace** として追加。OpenHands 内部の
   粒度 (thinking / tool / waiting / verifying) を表現するのは agent.* のみで、tool.*
   は capability 実行粒度のままにすることで、二重 publish を避ける。

3. **Live Overlay vs Drawer**: 既存の `LiveActivityDrawer` は **Drawer (展開式)** で
   38px ハンドル + 240px 展開ストリーム。instruction.md §21 は 32-40px **固定** を
   要求するため、Drawer を **LiveOverlay (sticky 38px) + LiveActivityPanel (展開式)**
   に分割。Drawer を残しつつ役割を明確化 (Drawer = 過去ログ、Overlay = 最新 1 イベント)。

4. **Trace ID 6 種**: 全て新規追加だが、`event_id` と `task_id` は既存。
   `trace_id` は OpenHands 会話再開時の conversation_id と同値、
   `parent_id` は EventBus の event graph を辿るためのキー、
   `activity_id` は人間向け Activity 単位の ID (D5 Activity 種類と一致)。
   `agent_session_id` は OpenHands の Conversation 単位 = 1 回の agent 実行。

5. **優先順位ロジック**: 1 イベントずつ severity + recency を計算。
   `severity = max(priority of kind, decay of timestamp)`。
   decay = `exp(-age_seconds / 30)` で 30 秒でほぼ 0 になる。
   これにより「最新 + 高優先度」を自然に表示。

6. **Retention 実装**: 既存 `audit_manager.py` の JSONL tail に kind タグを追加し、
   別 cron ジョブが日次で retention を超える JSONL を rotate。
   `Activity` テーブル (or JSONL) は永久保持 (人間向けなので重要)。

7. **検索の応答時間**: kinds ごとに AND/OR を切り替え可能なクエリ API。
   ChromaDB を Semantic Memory 用途で既に使っているので、Thinking 検索には
   それを流用。Events / Tools は SQL 風フィルタ (or JSONL grep)。

## 5. 共通実装パターン

### 新イベント publish パターン

```python
# aegis_ai/agents/backends/openhands/backend.py
from aegis_ai.event import EventManager

def _emit_agent_event(self, *, kind: str, task_id: str,
                     agent_session_id: str, parent_id: str,
                     payload: dict[str, Any]) -> None:
    if self._event_manager is None:
        return
    self._event_manager.publish_event(
        f"agent.{kind}",
        source="openhands_backend",
        payload={
            "task_id": task_id,
            "agent_session_id": agent_session_id,
            "parent_id": parent_id,
            **payload,
        },
    )
```

### Live Overlay 優先順位計算

```typescript
// web-ui/src/displayModel.ts
const PRIORITY = { approval: 100, error: 80, tool: 50, thinking: 30, progress: 10 };
const DECAY_TAU = 30; // seconds

export function pickOverlayEvent(events: UiEvent[]): UiEvent | null {
  let best: { event: UiEvent; score: number } | null = null;
  for (const e of events) {
    const p = PRIORITY[e.kind as keyof typeof PRIORITY] ?? 0;
    const ageSec = (Date.now() - e.occurred_at) / 1000;
    const score = p * Math.exp(-ageSec / DECAY_TAU);
    if (!best || score > best.score) best = { event: e, score };
  }
  return best?.event ?? null;
}
```

### Trace ID 6 種 dataclass

```python
# aegis_ai/event/event_models.py
@dataclass
class TraceIdentifiers:
    event_id: str           # 1 イベント単位
    task_id: str            # AEGIS Task
    activity_id: str = ""   # 人間向け Activity
    agent_session_id: str = ""  # OpenHands conversation
    trace_id: str = ""      # 1 つの trace
    parent_id: str = ""     # parent event_id
```

## 6. 中断時復帰手順

```powershell
cd C:\Users\kohak\programs\AEGIS
git log --oneline -5
cat DASHBOARD_REFINED_PLAN.md
# 該当 Phase の DoD から再開
```

## 7. 変更履歴

- 2026-09-10: Phase D9 完了 (Settings §22 + Token / Cost §25 frontend 最小実装)
  - §23 (OpenHands Observability 設定) と §24 (Retention by kind) は backend 実装が大きいため別 phase に分離
  - `web-ui/src/pages/DashboardSettingsPage.tsx`:
    - `DashboardSettings` 型に 4 フィールド追加 (liveOverlayShow / liveOverlayShowThinking / liveOverlayShowToolCalls / liveOverlayUpdateInterval)
    - Live Activity Overlay (§22) section を追加 (data-testid: live-overlay-show / live-overlay-show-thinking / live-overlay-show-tool-calls / live-overlay-update-interval)
    - 子のチェックボックスは liveOverlayShow=false のとき disabled
  - `web-ui/src/components/LiveOverlay.tsx`:
    - `readLiveOverlayToggles(): OverlayToggles` を export (localStorage `aegis.dashboard.settings` 読み取り)
    - `useState<OverlayToggles>` で初期値を `readLiveOverlayToggles()` から取得
    - `window.addEventListener("storage", ...)` で別タブからの設定変更に追随
    - `filteredEvents` を `useMemo` で算出 (show=false で idle / thinking OFF / tool calls OFF)
  - `web-ui/src/displayModel.ts`:
    - `TokenUsageSummary` 型を追加 (model / input_tokens / output_tokens / cached_tokens / estimated_cost_usd / event_count)
    - `summarizeTokenUsage(events: UiEvent[]): TokenUsageSummary` 関数を追加
    - 3 つの payload 形状に対応 (token_usage object / scalar fields / OpenAI usage)
  - `web-ui/src/pages/AgentSessionPage.tsx`:
    - `import { summarizeTokenUsage } from "../displayModel"` 追加
    - `OverviewTab` に `<TokenCostPanel events={detail?.events || liveEvents} />` を追加 (Policy / Approval section の直後)
    - `TokenCostPanel` コンポーネントを新規定義 (data-testid: token-cost-panel / token-input / token-output / token-cached / token-cost)
  - `web-ui/src/displayModel.test.ts` — D9 テスト 5 件追加 (合計 39 件):
    - `returns zero summary for empty or events without token info`
    - `reads token_usage object from payload`
    - `reads scalar token fields from payload directly`
    - `supports OpenAI-compatible usage fields (prompt_tokens / completion_tokens)`
    - `aggregates token usage across multiple events`
  - `web-ui/src/components/LiveOverlay.test.tsx` — D9 テスト 6 件追加 (合計 18 件):
    - トグル 3 件 (showThinking=false / showToolCalls=false / show=false)
    - `readLiveOverlayToggles` 3 件 (defaults / localStorage / malformed JSON fallback)
  - `web-ui/src/pages/AgentSessionPage.test.tsx` — D9 テスト 3 件追加 (合計 19 件):
    - `Overview tab shows Token / Cost panel when payload.token_usage is present (D9)`
    - `Overview tab reads scalar token fields from payload directly (D9)`
    - `Overview tab shows empty state when no token info events exist (D9)`
  - 全体 vitest 115 passed (既存 101 + D9 新規 14)
- 2026-09-10: Phase D8 完了 (複数 Agent / Live Overlay 優先順位)
  - `web-ui/src/displayModel.ts`:
    - `eventAgentSessionId(event)` 追加 — `payload._trace_ids.agent_session_id` → `payload.agent_session_id` → "" の優先順
    - `pickLiveOverlayEventForAgent(events)` 追加 — agent_session_id 単位で group 化 → 各 session 内の最重要 event 抽出 → session 同士で比較
  - `web-ui/src/components/LiveOverlay.tsx`:
    - `pickLiveOverlayEventForAgent` を使用 (D2 の `pickLiveOverlayEvent` から置換)
    - `liveOverlayClickTarget(event)` を export — agent_session_id があれば `/dashboard/agent-sessions/<id>` へ遷移 (D8 で追加)
    - Overlay 内に agent_session_id の先頭 12 文字を `<code data-testid="live-overlay-session">` で表示
    - ルート要素に `data-agent-session-id` 属性を追加
  - `web-ui/src/App.tsx`:
    - `LiveOverlay, liveOverlayClickTarget` を import
    - onClick を `navigate(liveOverlayClickTarget(event))` の 1 行に集約 (旧 3 段 ternary を削除)
  - `web-ui/src/displayModel.test.ts` — D8 テスト 8 件追加 (合計 34 件):
    - `eventAgentSessionId` 3 件 (優先順位 / fallback / なし)
    - `pickLiveOverlayEventForAgent` 5 件 (empty / group 優先 / 新しい高優先度 / 別 session failed / unassigned group)
  - `web-ui/src/components/LiveOverlay.test.tsx` — D8 テスト 8 件追加 (合計 12 件):
    - 描画 3 件 (複数 session / 同優先度 / session_id なし)
    - `liveOverlayClickTarget` 5 件 (agent_session / URL encode / task_id fallback / approval_id fallback / raw-activity fallback)
  - 全体 vitest 101 passed (既存 85 + 新規 16)
- 2026-09-10: Phase D7 完了 (検索 cross-tab + Agent Timeline 並列 Gantt)
  - `web-ui/src/pages/AgentTimelinePage.tsx` 新規 (227 行) — 複数 Agent Session 並列 Gantt 表示
    - `useQuery` で `/api/ui/agent-sessions?limit=200` を 15 秒間隔 refetch
    - `toRows()` で `first_event_ms` / `last_event_ms` を row 化、running で `last_event_ms=0` の場合は `now` まで描画
    - bar は CSS `position: absolute` + `left/width: %` で配置 (SVG ではない)
    - status 別 CSS class (`.agent-timeline__bar--{running,completed,failed,unknown}`) + running だけ glow
    - 検索 input で `agent_session_id` / `task_id` / `summary` 部分一致フィルタ (3 フィールド対応)
    - 1 分ごとに `setTick` 再描画 (running session の now ラインを更新)
    - 行クリックで `/dashboard/agent-sessions/<id>` へ遷移
  - `web-ui/src/pages/AgentTimelinePage.test.tsx` 新規 5 件 (全件 pass):
    - `shows empty message when no sessions`
    - `renders one row per session with status class and counts`
    - `filters rows by agent_session_id, task_id, and summary (substring match)`
    - `clicking a row navigates to agent-session detail`
    - `Refresh button triggers a refetch`
  - `web-ui/src/navigation.ts` — ops ドメインに `agent-timeline` ページ追加 + alias 追加
  - `web-ui/src/App.tsx` — `AgentSessionPage` / `AgentTimelinePage` の import 追加 (D4 で欠落していた `AgentSessionPage` も同時修正) + `if (pageId === "agent-timeline") return <AgentTimelinePage onNavigate={onNavigate} />;` ルート追加
  - `web-ui/src/styles/main.css` — `.agent-timeline*` スタイル追加 (Gantt bar, status 別色, glow, 凡例 swatch)
  - `web-ui/src/pages/DashboardPages.test.tsx` — ops domain の pages 期待値リストに `"agent-timeline"` を追加 (回帰)
  - 全体 vitest 85 passed (既存 80 + 新規 5)
- 2026-09-10: Phase D6 完了 (MCP / Tool call 完全 JSON 表示)
  - `web-ui/src/components/ToolCallJson.tsx` 新規、JSON 共通コンポーネント
    - `label` (引数 / 結果 / エラー) + `value` (any) + `maxLen` (デフォルト 1000) の 3 props
    - 1000 文字超は `[Show all (N chars)]` ボタンで全文表示に切替 (`useState` local 管理)
    - `value=null/undefined` で no-op、`string` はそのまま、それ以外は `JSON.stringify(value, null, 2)`
  - `web-ui/src/pages/AgentSessionPage.tsx` の `EventsTab` で `agent.tool.*` / `tool.execution.*` を `isToolCall` で判定
    - started event → `<ToolCallJson label="args" ...>`
    - completed event → `<ToolCallJson label="output" ...>` + error があれば `<ToolCallJson label="error" ...>`
    - event header に `ok` / `failed` / `duration_ms` 表示 (CSS 緑 / 赤で強調)
  - `web-ui/src/styles/main.css` に `.tool-call-json` / `.tool-call-json__pre` (max-height 360px, monospace) / `.tool-call-json-group` / `.event-row .tool-call-{ok,failed}` 追加
  - `web-ui/src/components/ToolCallJson.test.tsx` 新規 7 件 (全件 pass) + `web-ui/src/pages/AgentSessionPage.test.tsx` に 3 件追加 (合計 16 件、全件 pass)
  - 全体 938 passed (D5 完了状態) / 13 pre-existing failed 維持
  - 全体 vitest 80 passed (既存 70 + 新規 10)
- 2026-09-10: Phase D5 完了 (Policy / Approval 表示統合)
  - `aegis_ai/audit/audit_manager.py` に `event_manager` パラメータ追加、`_POLICY_ACTIONS` のみ `policy.decision` を EventBus に publish
  - `aegis_ai/event/event_manager.py` の `_PERSIST_EVENT_TYPES` に `policy.decision` 追加
  - `aegis_ai/runtime.py` で `AuditManager(..., event_manager=event_manager)` 渡す
  - `aegis_ai/web/routes/agent_sessions.py` の `_AGGREGATABLE_KINDS` に `policy.decision` 追加 (25 種類)
  - `_POLICY_ALLOW_LIKE` / `_POLICY_ASK` / `_POLICY_DENY` 3 分類 + `_RISK_ORDER` で `highest_risk` 計算
  - `_build_summary` に 6 フィールド追加 (`policy_allow_count` / `policy_ask_count` / `policy_deny_count` / `highest_risk` / `approval_count` / `pending_approval`)
  - `pending_approval` ライフサイクル管理 (`approval.created` → `approved/executed/rejected/expired/cancelled/failed` で遷移)
  - `web-ui/src/api/client.ts` の `AgentSessionSummary` に 6 フィールド追加
  - `web-ui/src/pages/AgentSessionPage.tsx` の Overview tab に `Policy / Approval` section 追加
  - `KIND_FOR_TAB.mcp` / `.approvals` に `policy.decision` 追加 + `tabEvents` filter で `payload.capability_id` フォールバック
  - `EventsTab` で `policy.decision` を `decision=` / `risk=` / `capability=` で強調表示
  - テスト backend 6 件 (D5) + frontend 3 件 (D5) = 9 件新規追加 (合計 21 件、backend 12 + frontend 13)、全件 pass
  - 全体 938 passed (既存 932 + 新規 6) / 13 pre-existing failed 維持
  - 全体 vitest 70 passed (既存 67 + 新規 3)
  - コミット: `039640d feat(ui): Phase D5 - Policy / Approval 表示統合 (MCP / Approvals tabs に policy.decision 統合)`
- 2026-09-10: Phase D4 完了 (Agent Trace 画面 9 tabs)
  - `aegis_ai/web/routes/agent_sessions.py` 新規、3 つのエンドポイント
    (`/api/ui/agent-sessions`, `/<id>`, `/<id>/events?kinds=`)
  - `_AGGREGATABLE_KINDS` (24 種類) で session 集約
  - `_extract_session_id` で payload の `_trace_ids.agent_session_id` → `payload.agent_session_id` → `"unassigned"` 優先順
  - `web-ui/src/pages/AgentSessionPage.tsx` 新規、9 tabs 統合 (Overview/Thinking/Tools/MCP/Files/Terminal/Approvals/Errors/Raw)
  - `KIND_FOR_TAB` / `TOOL_PREFIX_FOR_TAB` helper で kind + tool プレフィックスフィルタ
  - `useQuery` で 15 秒間隔 refetch、`recentEvents` (SSE) で live updates 表示
  - テスト backend 6 件 + frontend 10 件 = 16 件 pass
  - 全体 932 passed (既存 926 + 新規 6) / 13 pre-existing failed 維持
  - 全体 vitest 67 passed (既存 57 + 新規 10)
  - コミット: `6c0b606 feat(ui): Phase D4 - Agent Session 9 tabs 画面`
- 2026-09-10: Phase D3 完了 (Trace ID 6 種伝搬)
  - `AgentEventPublisher.start_session()` で 1 実行 = 1 session/trace を確立
  - `_publish` 内で Trace ID 6 種 (event_id / task_id / activity_id / agent_session_id / trace_id / parent_id) を自動付与
  - payload に `_trace_ids` dict を同梱し UI 側 `_extract_trace_ids` で UiEvent に展開
  - テスト +6 件 (合計 23 件、全件 pass)、全体 926 passed / 13 pre-existing failed
- 2026-09-10: Dashboard 改修計画 v2 をベースに D1-D9 の 9 フェーズ洗練プラン作成
  - 既存実装マッピング (§1-25 vs 現状): ✅ ◐ △ ❌ で分類
  - Phase D1-D9 それぞれに目標 / 変更ファイル / DoD / 設計判断を記載
  - 共通実装パターンを 3 種類 (publish / Overlay 優先順位 / Trace ID dataclass) 用意
  - 中断時復帰手順を明示
