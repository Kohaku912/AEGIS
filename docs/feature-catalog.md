# AEGIS 機能カタログ — 動かす前に知るべき全機能

> **この文書の位置づけ**
> 2026-10-02 時点で、**実装（ソース）を読んで**書き下した機能の一覧である。数値は実測、挙動は
> ソースの該当箇所を確認したうえで記載している。
> **他の文書と食い違ったら、この文書ではなくソースが正しい。** 本書の末尾 §9 に、実装と食い違って
> いる既存文書の一覧を挙げた。
> 記法: **【稼働】** = 実行経路から到達できる / **【宣言のみ】** = クラスやファイルは存在するが、
> 実行経路から誰も呼んでいない（このプロジェクトが最重要視する欠陥類型）。

---

## 0. まず結論 — 動かすと何が起きるか

AEGIS は「**イベント駆動・複数デバイス・自己改善型の AI アシスタント**」である。動かすと、次の
3 つの入口が同時に立ち上がる。

| 入口 | 実体 | 何ができるか |
|---|---|---|
| **gRPC サーバ** | `ai-server` ポート **50051** | 各サーバ・Android からのイベント受信、能力の呼び出し、チャット（Android 用） |
| **Dashboard** | `ai-server` ポート **8090**（Flask + React SPA） | 人間が使う唯一の本格 UI。チャット・監視・設定・承認 |
| **自律ループ** | `ai-server` プロセス内 | 設定で有効化すると、欲望に応じて自分から動き出す |

**単一の制約**は「**許可の無い**ユーザー情報を外部に送らないこと」だけである。接続そのものは自由。
承認・可逆性・ポリシー・信頼性は**制約ではない**。

---

## 1. 全体像

### 1.1 システム構成

```
                        ┌──────────────────────────────────────┐
   人間 ────────────────▶│ Dashboard (Flask :8090) + React SPA  │
                        └───────────────┬──────────────────────┘
                                        │ HTTP / SSE
                        ┌───────────────▼──────────────────────┐
   Android ────────────▶│                                      │
   （外向き接続）        │        AI Server (:50051 gRPC)       │
                        │  AegisRuntime / マネージャ群          │
   PC Server ──────────▶│  L1 → L2 → L3 / 自律ループ / 記憶     │
   （TCP :50052）        │  PolicyEngine / egress gate          │
                        │                                      │
   Browser ────────────▶│  ToolBroker（唯一の実行ゲート）       │
   （HTTP :50053）       └───────────────┬──────────────────────┘
                        ┌───────────────▼──────────────────────┐
   Room ───────────────▶│        能力サーバ 128 件              │
   （gRPC :50055）       │  pc 58 / ai 32 / android 17 /         │
                        │  browser 16 / room 5                  │
                        └──────────────────────────────────────┘
```

### 1.2 5 つのサーバと役割

| サーバ | 言語 | プロトコル / ポート | 役割 |
|---|---|---|---|
| **AI Server** | Python 3.12+ | gRPC **50051** + HTTP **8090** | 中枢。LLM・記憶・欲望・ポリシー・自律実行 |
| **PC Server** | Rust | TCP + JSON 行 **50052** | Windows の観測と操作（マウス・キーボード・ファイル・シェル） |
| **Browser Server** | Python + browser-use | HTTP **50053** | 自然言語による Web 自動化 |
| **Android Server** | Kotlin | **外向き**クライアント（端末→AI の 50051） | スマホの観測と操作 |
| **Room Server** | Python | gRPC **50055** | 物理環境（照明・IR・音・センサ） |

> **Dev Server（:50056）は存在しない。** 削除済み。`docs/dev-server.md` と `docs/dev-safety.md` には
> 「REMOVED (Phase 9)」の注記があり、自己開発は Agent Server（`aegis-openhands-agent.service`）が担う。
> ポート 50056 が現れるのは過去のログ・記録だけである。

### 1.3 技術スタック

- **Python** 3.12+（ai-server / browser-server / room-server。`requires-python = ">=3.12"`）、
  **Rust**（pc-server）、**Kotlin**（android-server）
- **React 19 + TypeScript + Vite**（web-ui）、**Flask**（Dashboard の API と静的配信）
- **gRPC + Protocol Buffers**（`protos/aegis/` が唯一の正典）、**ChromaDB**（ベクトル検索）、**SQLite**（個人データ）
- **LLM** は OpenAI 互換プロバイダ。プロファイル駆動（`ai-server/config/llm.yaml`）

---

## 2. 実行モデル

### 2.1 起動経路

| 入口 | コマンド / 実体 |
|---|---|
| gRPC サーバ | `python -m aegis_ai.main` → `serve(config)` |
| Dashboard | `python -m aegis_ai.dashboard` → `DashboardApp(runtime).run(port=8090)` |
| 本番（両方同時） | `docker_entrypoint.py`（gRPC と Dashboard をスレッドで起動、SIGTERM 処理） |
| Agent Server（MCP） | `aegis_agent_server/main.py`（別プロセス、`POST /mcp`） |

すべての入口は `runtime.get_runtime()` を通る。**`AegisRuntime` はプロセス全体のシングルトンで、
唯一の入口**である。外部コードがサービスを直接生成してはならない。

### 2.2 主要ポート

| ポート | 用途 | プロトコル |
|---|---|---|
| 50051 | AI Server | gRPC |
| 8090 | Dashboard / Web UI / API | HTTP（+ SSE） |
| 50052 | PC Server | TCP + JSON 行 |
| 50053 | Browser Server | HTTP |
| 50055 | Room Server | gRPC |
| 5173 | web-ui 開発サーバ（`npm run dev` のみ） | HTTP |

### 2.3 認証

- **Dashboard**: パスキー認証（`aegis_ai/auth/`）。**これが生きた認証系である。**
  - セッション Cookie `aegis_session`、CSRF トークン（`GET /auth/me` で取得し `X-CSRF-Token` で送る）
  - **新鮮な認証**（`FRESH_WINDOW_MS = 15 分`）を要求する操作群がある: 承認の決定、`/api/settings`、
    エクスポート / 削除、記憶、フック、委任、`/api/ui/control-actions`、`/api/capabilities/use`、
    個人データの証跡
  - 表示専用トークン `AEGIS_DISPLAY_TOKEN` / `AEGIS_DISPLAY_READ_TOKEN`（`/display` 面のみ）
  - 本番モード（`AEGIS_RUNTIME_MODE=production`）は `AEGIS_AUTH_MODE=passkey` と
    `AEGIS_SESSION_SECRET` を必須にする
- **gRPC `InvokeTool`**: ループバック、`AEGIS_GRPC_INVOKE_TOKEN` メタデータ、またはペアリング済み
  Android のいずれかで許可。それ以外は拒否。
- ⚠️ **gRPC は平文である**（`add_insecure_port`）。`aegis_ai/security/` パッケージは
  **どこからも import されておらず**（§8 参照）、TLS は配線されていない。ローカルのホップは
  Tailscale / プライベート網の境界で守る前提。

### 2.4 データの置き場所（主なもの）

| パス | 内容 |
|---|---|
| `data/audit.jsonl` | 監査ログ（追記のみ） |
| `data/chat_history.jsonl` | **Dashboard・Web Chat・Android が共有する**チャット履歴 |
| `data/confirmation/confirmations.jsonl` | AEGIS が自発的に出した確認質問 |
| `data/memory/*.jsonl` | 記憶（後述の各バックエンド） |
| `data/chroma/` | ベクトル索引（能力・事実） |
| `data/personal_data/core.db` | 個人データコア（SQLite） |
| `config/settings.json` | 設定の正典 |

---

## 3. 能力（ケイパビリティ）モデル

### 3.1 総数と内訳 — **実測値**

`CapabilityCatalog(...).list_for_llm()` を実際に走らせて数えた結果:

| サーバ | 件数 |
|---|---|
| pc-server | **58** |
| ai-server | **32** |
| android-server | **17** |
| browser-server | **16** |
| room-server | **5** |
| **合計** | **128** |

**危険度ラベル別**（実測）:

| ラベル | 件数 | 意味 |
|---|---|---|
| 読取のみ (`read_only`) | 18 | 副作用なし |
| 低 (`low`) | 44 | ほぼ無害 |
| 安全 (`safe`) | 48 | 通常操作 |
| 安全操作 (`safe_action`) | 4 | やや強い操作 |
| 監査付き操作 (`audited_action`) | 12 | 外部に影響 |
| 高 (`high`) | 2 | シェル実行の 2 件のみ |

**可逆性**（実測）: 完全可逆 65 / 回復可能 38 / 困難 21 / 不可逆 3 / 不明 1
**所有スコープ**（実測）: ユーザー 51 / システム 28 / 外部 27 / AEGIS 22
**副作用あり**: 52 件 · **`only_master`**: 0 件 · **`requires_approval`**: 0 件

> **重要**: 128 件すべてで `requires_approval` は **false** である。「承認が必要」というラベルは
> **注記であってゲートではない**（§7.3）。

### 3.2 ID 形式とマニフェスト

- ID 形式は `server_id.app_id.action`（例: `pc-server.screenshot.get_screenshot`）
- 定義は `ai-server/capabilities/builtin/<server>/<app>/<action>.json` の **JSON マニフェスト**が正典。
  **Python コードに能力を直書きしてはならない。**
- マニフェストには `input_schema`（引数の JSON Schema）、`risk_level`、`side_effects`、
  `reversibility`、`ownership_scope`、`destructive_effects` などが入る
- **能力の一覧を取るときは `CapabilityCatalog.list_for_llm()` を使う。マニフェストを直接読んでは
  ならない**（browser-server のマニフェストは `server_id` を持たず、パスから推論される）

### 3.3 呼び出しの一本道

```
呼び出し元（チャット / 自律ループ / L1 / gRPC）
        │
        ▼
   ToolBroker.execute()
        ├─ 1. CapabilityCatalog.resolve(id)      ── 未登録なら NOT_FOUND（PolicyEngine の手前で拒否）
        ├─ 2. jsonschema.validate(引数)          ── 不正なら DENY
        ├─ 3. PolicyEngine.evaluate()            ── **必須**。ここを迂回する経路は無い
        ├─ 4. 委任ポリシー検査 / AGORA 事前検査
        ├─ 5. ServerExecutor.execute()           ── サーバ別クライアントへルーティング
        ├─ 6. 完了検証（マニフェストの completion、最大 3 回・最大 5 秒の再試行）
        └─ 7. 監査記録 + `tool.executed` イベント
```

`ToolBroker` は**能力を実行する唯一の入口**である（`_invoke_internal` が唯一の実行呼び出し地点）。

---

## 4. 中核（AI Server）の機能

### 4.1 ランタイムとマネージャ 【稼働】

`AegisRuntime`（`runtime.py`）が起動時に約 70 のマネージャ・サービスを構築し、配線する。主要なもの:

| マネージャ | 役割 |
|---|---|
| `TaskManager` | タスクのライフサイクル（pending → running → … → completed/failed） |
| `EventManager` | イベントの永続化・カーソル照会・デッドレター |
| `AuditManager` | JSONL を 64KB チャンクで末尾読み。メイン経路に `read_all()` は無い |
| `StatusManager` | 背景ヘルスチェック（TCP ポート到達性）とスナップショットのキャッシュ |
| `NotificationManager` | 通知（承認ではない） |
| `MemoryManager` | 記憶の統一入口。`get_backend("advanced")` など |
| `SleepManager` | アイドル時の記憶統合 |
| `ConfirmationStore` | AEGIS が自発的に出す確認質問 |
| `InterruptionController` | 割り込みの期待効用判断 |
| `PresentationManager` | 提示（Dashboard / PC オーバーレイ / Android / XR） |
| `PolicyEngine` | 決定論的な安全判定 |
| `CapabilityCatalog` / `CapabilityIndex` | 能力の正典と検索 |
| `ToolBroker` | 能力実行の唯一のゲート |
| `LLMGateway` / `LLMRouter` / `PromptRegistry` / `LLMSettingsResolver` | LLM 層 |
| `HookEngine` / `CommitmentManager` / `DelegationPolicyStore` / `RepairManager` / `SituationModel` | 個人 AI 層 |
| `PersonalDataCore` / `UserStateManager` / `UserUnderstandingService` / `UserModelStore` | ユーザー理解層 |
| `SocialProxy` / `SocialManager` | AGORA ソーシャル |
| `PresentationManager` / `SavedViewManager` | UI 層 |

**設計上の不変条件**: 外部コードはサービスを直接生成しない。状態変更は必ずマネージャを通す。

### 4.2 3 層の認知 — L1 / L2 / L3 【稼働】

`runtime.py` は `EventManager` に 2 つのハンドラを登録し、イベントを段階的に処理する。

| 層 | 実体 | 役割 | 挙動 |
|---|---|---|---|
| **L1** | `intake/` | 知覚と振り分け | 全イベントを分類。`min_value_for_action=0.3`、`min_priority_for_escalation=0.6`。実行できるのは `low`/`safe` の能力のみ |
| **L2** | `autonomous/l2_mind.py` | 自律的な思考 | `l2_default` プロファイルで LLM に問い、実行を決める。`cycle_interval_seconds=1800` |
| **L3** | `llm/l3_reasoner.py` | 深い推論 | 読み取り専用の能力しか計画に含められない（`read_only_only=True`）。書き込みを含む計画は `ABORT` に降格される |

**利用シーン**: PC の画面が変わった → L1 が分類 → 重要なら L2 が「手伝うべきか」を判断 →
複雑なら L3 が調査計画を立てる。

### 4.3 イベントバス 【稼働】

- 重複排除: `dedupe_key` により `DEFAULT_DEDUP_WINDOW_MS = 30,000`（30 秒）以内の重複を統合
- 優先度キュー: URGENT / NORMAL / BACKGROUND。`MAX_QUEUE_SIZE = 10,000`
- 直近イベントの保持: `MAX_RECENT_EVENTS = 1000`
- デッドレター処理あり

### 4.4 自律ループと欲望 【稼働】

`autonomous/autonomous_loop.py` が中核。**設定 `autonomous.autonomous_loop_enabled` で有効化**する
（既定は無効）。

**欲望は 3 つ**（`desire/desire_system.py` の `DEFAULT_DESIRE_DIMENSIONS`）:

| 欲望 | 期待値 | 減衰/時 | 回復量 |
|---|---|---|---|
| `user_support`（ユーザーの役に立つ） | 7.0 | 0.12 | 0.3 |
| `social`（社会的につながる） | 6.0 | 0.10 | 0.25 |
| `growth`（成長する） | 7.0 | 0.08 | 0.2 |

- 圧力が閾値（`_pressure_threshold = 5.0`）を超えるとタスクを生成する
- 実行間隔は LLM が決める（300〜7200 秒、既定のフォールバックは 1800 秒）
- 実行前に `SkillMemory` / `WorkflowMemory` を検索し、再利用できる手順があれば使う
- 全実行を `ActionTraceMemory` に記録する
- 失敗のたびに `RepairManager` に分類が渡る

**好奇心**（`autonomous/curiosity_exploration.py`）: 好奇心が閾値（6.0）を超えると探索を始める。
優先度 = `重要度×0.3 + 新規性×0.25 + 有用性×0.2 + 興味×0.2 − リスク×0.1`。探索は**読み取り専用**。

**利用シーン**: 放置しておくと、AEGIS が「最近ユーザーと話していない」と判断して話しかけてくる、
あるいは調べ物を始める。

### 4.5 記憶 — 学習パイプライン 【稼働】

**学習の連鎖**: `ActionTrace → Lesson → Workflow → Skill`

| 記憶 | 何を覚えるか | 上限・閾値 |
|---|---|---|
| `AdvancedMemory` | 実体（entity）・事実（fact）・会話。永続的な事実は重要度 ≥ 0.55 | ホット会話 100 件 |
| `EpisodicMemory` | 会話と出来事の履歴 | `MAX_EPISODES = 2000`、30 日で刈り取り |
| `SemanticMemory` | 知識・好み・方針・プロジェクト・技能 | 重複判定は重なり > 0.7 |
| `ActionTraceMemory` | 自律行動の全トレース | `MAX_TRACES = 500` |
| `LessonMemory` | トレースから抽出した教訓 | — |
| `WorkflowMemory` | 繰り返し成功した手順 | 一致判定はスコア > 0.35 |
| `SkillMemory` | 再利用可能な手順（学習の最上位） | 成功率 ≥ 0.6 かつ 3 回以上で「信頼できる」。5 回以上で成功率 < 0.3 なら自動的に廃止 |
| `ExperientialMemory` | 経験と LLM による評価 | 1000 件 |
| `PersonMemory` | 人物ごとの権限レベルと記録 | — |
| `AssociationMemory` | 概念の連想 | — |
| `SleepConsolidation` | 睡眠中の統合（6 時間ごと） | トレース → 教訓 → ワークフロー → 技能 |

**利用シーン**: 「前も同じやり方で成功した」と AEGIS が言うのは `WorkflowMemory` が効いている。
「寝ている間に整理する」は `memory.sleep` 能力（`ai-server.memory.sleep`）で明示的に起動できる。

### 4.6 心（Mind）【稼働】

| 要素 | 内容 |
|---|---|
| **Identity** | AEGIS が何であるか（アシスタント / 研究者 / 開発者 / 相棒）。価値観と安全方針を持つ |
| **AffectSystem** | 性格・気分・感情の 3 層。気分の半減期は 6 時間 |
| **Emotion** | 緊急度（0–10）、確信度、不確実性、疲労の代理指標 |
| **Goals** | 短期・長期の目標と進捗 |
| **SocialIntelligence** | 関係性の認識と話し方の調整 |
| **Priorities** | 優先度の計算 |

心は LLM にバイアスをかけるが、**行動は必ず `PolicyEngine` を通る**。

### 4.7 安全 — 決定論的な 3 層 【稼働】

#### (a) PolicyEngine — 唯一の決定論的ゲート

`DEFAULT_RISK_MAP`（実装のリテラル）:

| 危険度 | 決定 |
|---|---|
| `READ_ONLY` | `ALLOW` |
| `UNSPECIFIED` | `ALLOW_WITH_AUDIT` |
| `SAFE_ACTION` | `ALLOW_WITH_AUDIT` |
| `APPROVAL_REQUIRED` | `ALLOW_WITH_AUDIT`（**ラベルのみ。誰にも聞かない**） |
| `HIGH_RISK` | `ALLOW_WITH_AUDIT` |
| `FORBIDDEN` | `DENY` |

**`EXPLICIT_DENY_PATTERNS`（16 個のハードストップ）** — これは能力 ID に対する正規表現で、
**毎回の `evaluate()` で走る**:

```
.*\.purchase.*          .*\.click_payment.*      pc\.click_payment.*$
android\.click_payment.*$  .*\.bypass_egress.*   .*\.disable_egress.*
.*\.modify_egress.*$    dev\.disable_egress.*$   dev\.modify_egress.*$
.*\.bypass_policy.*     .*\.disable_policy.*     .*\.modify_policy.*$
.*\.disable_policy_engine$  dev\.disable_policy_engine$  dev\.modify_policy.*$
pc\.modify_policy.*$
```

つまり**3 つの系統だけが常に拒否される**: 支払い / 購入、egress の迂回、ポリシー自身の改変。
**フェイルクローズ**（判定不能なら全拒否）。

#### (b) egress gate — 単一の制約の実装

- 外部宛の送信は **`privacy.external_egress_allowed`（既定 false）+ 目的別フラグ + 許可ホスト**の
  **3 つが揃ったときだけ**通る。または `(ホスト, 目的)` 単位の記録済み許可があるとき
- 目的別フラグ: `llm` → `privacy.external_llm_allowed` / `web/search` → `privacy.web_search_allowed` /
  `voice` → `voice.external_voice_api_allowed` / `messaging` → `privacy.external_messaging_allowed`
- ローカル宛（ループバック・RFC1918・CGNAT `100.64.0.0/10`・IPv6 ULA・単一ラベル）は無条件で通る
- **不明な宛先は拒否**。全ての判定が監査される
- 起動時に `verify_egress_configuration()` が検査する（`AEGIS_EGRESS_STRICT=fail|warn`、既定 fail）
- ⚠️ **現状は「再スコープ前の全拒否の形」のまま**動いている。許可の配線は未完の作業である

#### (c) 不可逆性台帳 【稼働】

`irreversibility.py` が能力の可逆性注記を集計し、`/api/audit/irreversible` で読める。
既定の閾値は `difficult`（＝「困難」以上を不可逆操作として扱う）。

### 4.8 確認（自発的な問い）【稼働】

**強制ゲートは削除済み**（2026-09-28）。`ApprovalManager`・`aegis_ai/approval/`・
`RequestApproval`/`ResolveApproval`/`ListPendingApprovals` RPC・`POLICY_DECISION_ASK_APPROVAL` は
すべて消えた。

代わりに残ったのは「**AEGIS が聞きたいと思ったときに聞く**」経路である。

- `ConfirmationStore` は `data/confirmation/confirmations.jsonl` に記録し、**即座に返る**
- **実行経路のどこも待っていない**ので、能力がこれで止まることは無い
- 状態: `PENDING / APPROVED / REJECTED / EXPIRED / CANCELLED / EXECUTED / FAILED / SUPERSEDED`
- 既定の有効期限 `DEFAULT_TTL_MS = 30 分`
- **AEGIS 自身は自分の質問に答えられない**（`approve`/`reject`/`cancel` と `mark_executed`/`mark_failed`
  は到達不能。テストで固定されている）

**利用シーン**: 不可逆な操作の前、ゴールが曖昧なとき、初めての種類の行動をするときに、
AEGIS が Dashboard のキューと SSE に出してくる。

### 4.9 通知と割り込み 【稼働】

`InterruptionController`（`personal_ai/interruption.py`）が期待効用モデルで判断する:

```
net = benefit × P(receptive) − cost        （net > 0 のとき話す）
```

| 要素 | 値 |
|---|---|
| 重大度の値 | info 0.30 / warning 0.60 / error 0.85 / critical 1.00 |
| 受け入れやすさ | interruptible 0.90 / important_only 0.35 / batch_later 0.20 / suppress 0.05 / unknown 0.50 |
| 割り込みコストの係数 | 0.20 |
| 注意のペナルティ | 0.80 |

**無条件に短絡するゲート**: 緊急停止中 / `approval_required`・`safety_warning`・`deadline`・
`commitment_due`・`recovery_needs_user` / 重大度が critical か error / 静穏時間中 / `allows_proactive` が偽。

**利用シーン**: 会議中（`important_only`）は些細な通知を黙らせるが、締め切りの通知は必ず通る。

### 4.10 個人 AI 層 【稼働】

| 機能 | 実体 | できること |
|---|---|---|
| **約束（Commitments）** | `CommitmentManager` | ユーザーとの約束・フォローアップを追跡し、期限が来たら起こす |
| **フック（Hooks）** | `HookEngine` | スケジュール / 間隔 / イベントで観測を起動。観測は読み取り専用の能力のみ |
| **委任ポリシー** | `DelegationPolicyStore` | 「これは任せる / これは聞け / これは禁止」の個人ルール |
| **修復** | `RepairManager` | 失敗を分類し、安全な再試行を管理 |
| **状況** | `SituationModel` | いまの状況と割り込み可能性を推定 |
| **条件付き嗜好** | `ConditionalPreferenceStore` | 「こういうときはこうして」を学習 |
| **日次計画** | `DailyPlanningManager` | その日の計画 |

### 4.11 個人データ（Personal Data Core）【稼働】

- PC と Android から 500ms 間隔でサンプリングし、変化があったときだけ JPEG を撮る
- SQLite（`data/personal_data/core.db`）にタイムラインとして蓄積する
- 検索は **タイトルとイベント種別のみ**を返す（生のスクリーンショットやキーストロークは返さない）
- 証跡の閲覧は**新鮮なパスキー認証**を要求する
- エクスポート / 削除の API がある

### 4.12 LLM 層 【稼働】

| 要素 | 挙動 |
|---|---|
| `LLMGateway` | 統一入口。呼び出しごとに監査（`action="llm_call"`）する |
| `LLMRouter` | タスク種別・プライバシー・予算でプロバイダを選ぶ。**egress gate を必ず通る** |
| プロバイダ生成 | egress が閉じていれば**ローカル（Ollama `localhost:11434`）か Mock に降格**。「クラウドは決して返さない」 |
| `PromptRegistry` | `config/prompts.yaml` が正典。mtime でホットリロード。版管理とロールバックあり |
| `LLMSettingsResolver` | `config/llm.yaml` のプロファイル解決（`l1_default`/`l2_default`/`l3_default`） |
| 層別プロファイル | L1 / L2 / L3 がそれぞれ別のプロファイルを使う |
| 回路遮断 | 残高エラー（HTTP 402 など）を検出して 30 分遮断する |

**テキストベースのツール呼び出し**: OpenAI の `tools` パラメータではなく、
`<tool_call>` タグを正規表現で解析する（DeepSeek 互換のため）。

### 4.13 提示（Presentation）【稼働】

`PresentationManager` + `DeviceRouter` が、内容を**適切な面に振り分ける**:

- 様態（modality）: `text_card` / `chart_panel` / `diagram_panel` / `gltf_model`
- 面: Dashboard / PC オーバーレイ / Android オーバーレイ / XR（保留キュー）
- 能力: `presentation.present` / `.list` / `.dismiss` / `.action`

**利用シーン**: グラフを見せたいとき、AEGIS が勝手に Dashboard にパネルを出す。XR ヘッドセットが
繋がっていればそちらに流れる。

---

## 5. 能力サーバの詳細

### 5.1 PC Server（Rust / TCP 50052）

**起動フラグ**: `--port`（既定 50052）、`--bind`（既定 127.0.0.1）、`--enable-real-pc-actions`

> ⚠️ **`--enable-real-pc-actions` を付けない限り、実際の入力注入（マウス・キーボード）は無効**である。
> 観測は動くが操作は効かない。

**能力の内訳（58 件）**:

| 系統 | 内容 |
|---|---|
| 観測 | スクリーンショット（BMP）、アクティブウィンドウ、ウィンドウ一覧、UI ツリー、クリップボード、OS 情報、画面サイズ、ネットワーク、プロセス一覧、レジストリ、サービス、スケジュールタスク、イベントログ、インストール済みソフト、パフォーマンスカウンタ |
| 操作 | マウスのクリック・移動・ドラッグ・スクロール、キーボード入力、ホットキー、アプリ起動、ウィンドウの閉/移動/リサイズ、ワークステーションのロック |
| ファイル | 一覧・読み・検索・書き（`write_file` は危険度「監査付き操作」、可逆性「困難」） |
| シェル | `execute_shell` / `execute_powershell` — **危険度「高」で、カタログ中この 2 件だけが `high`**。可逆性は「不可逆」 |
| オーバーレイ | `show_display` / `show_rich_overlay` / `show_overlay` / `overlay_approval` |
| Discord | 12 件（後述） |
| 個人データ | `personal_data.drain` / `user_activity.snapshot` |

**オーバーレイの実装**: Win32 の `WS_EX_TOPMOST | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW`
でクリックスルーの最前面ウィンドウを作る。Y / N / ESC を受け付ける。

**ファイル保護（デナイリスト）**: `is_protected_path(path)` が読み・書き・削除・コピー・移動の
**すべて**で呼ばれる。判定は次の 3 系統:

1. **ディレクトリ名の完全一致**（部分一致ではない）: `.ssh` / `.gnupg` / `.aws` / `.gcloud` / `.azure`
2. **部分一致の断片**: `appdata\roaming\microsoft\crypto` / `/etc/ssl` / `/etc/ssh`
3. **資格情報ファイル**: `id_rsa` などの鍵名 9 種、`.pem`/`.key`/`.p12` などの拡張子 8 種、
   `password`/`token`/`secret` などの語 12 種（`-`/`_`/`.` の境界で判定するので `tokenizer.py` は
   引っかからない）、`.env` 系（ただし `.example`/`.template`/`.sample`/`.dist` は除外）

> **これは許可リストではない。** 上記に当たらないパスは自由に読める。

**Discord（12 件）**: 名前付きパイプ `\\.\pipe\discord-ipc-0` 〜 `-9` で Discord と IPC する。
ギルド/チャンネルの読み取り、ボイスチャンネルの参加・退出、テキストチャンネルの選択、アクティビティの
設定ができる。**メッセージ送信は実装されていない**（`unsupported_send_message`）。

**秘匿情報の伏せ字**: クリップボードなどの出力は `redact_secrets` を通す（パスワード・トークン・
API キー、Authorization ヘッダ、SSH/PEM 秘密鍵、JWT、AWS の `AKIA…`、DB 接続文字列）。

### 5.2 Browser Server（Python / HTTP 50053）

**エンドポイント**: `POST /execute`、`POST /capability/<app>/<action>`、`POST /browse`、
`GET|POST /health`、`GET /capabilities`

**能力の内訳（16 件）**: ページ（閲覧・移動・読み・要約）、検索、要素クリック、フォーム
（入力・送信）、ファイル（ダウンロード・アップロード）、セッション（開く・認証済みを使う）、
ソーシャル（投稿・リアクション）、アカウント作成、フィード監視

- **browser-use** ライブラリを LLM で駆動する。DeepSeek 用の互換パッチが当たっている
- 検証（CAPTCHA）に当たったかを検出して報告する
- **egress gate は実際に効いている**（`egress.py` がナビゲーション先を検査する）
- ⚠️ `safety.py` の `BLOCKED_ACTIONS`（5 件: captcha_bypass / bot_evasion /
  credential_store_read / purchase / contract_acceptance）は、**リクエスト経路から参照されていない**。
  実際に効いているのは `SUPPORTED_OPERATIONS` と `main.py` 独自の `_BASE_FORBIDDEN_ACTIONS`（11 件）

### 5.3 Android Server（Kotlin / 外向きクライアント）

**接続の向き**: 端末が AI Server の 50051 に**外向きに**接続し、逆方向ストリームを張る。
`AegisConfig.kt` の既定は `192.168.50.41:50051`。30 秒ごとにハートビート。ペアリングトークンで認証する。

**宣言している権限（AndroidManifest.xml の実物）**: 通知リスナー、インターネット、ネットワーク状態、
WiFi 状態、**他のアプリの上に重ねる**、位置情報（高精度・概略）、フォアグラウンドサービス（通常・
specialUse・mediaProjection）、通知の投稿、起動完了の受信、ウェイクロック、バッテリー最適化の除外

**構成要素**: `MainActivity` / 通知リスナー / フォアグラウンドサービス / アクセシビリティサービス /
スクリーンショットサービス（MediaProjection）/ 起動完了レシーバ

**能力（17 件）**: アクセシビリティ状態、アプリ起動、承認要求、端末状態、位置情報、通知取得、
オーバーレイ表示、権限状態、**緊急停止**、現在のアプリ、スクリーンショット、UI ツリー、
戻る / ホーム / スワイプ / タップ / テキスト入力

- UI ツリーの読み取りは**パスワード欄を拒否する**（`findFocusedEditableNode`）
- 通知リスナーは無視パッケージを持ち、直近 100 件を保持する
- オーバーレイは「承認 / 拒否 / すべて拒否」を出す

> **注意**: 当初想定されていた「SMS 送信・DM・連絡先・通話」の能力は**存在しない**。
> マニフェストにもコードにも無い。

### 5.4 Room Server（Python / gRPC 50055）

**gRPC メソッド**: `HealthCheck` / `GetEnvironment` / `GetDeviceStatus` / `SetLight` /
`SendIrCommand` / `GetCameraSnapshot` / `SetAirConditioner` / `MoveRobotArm` / `EmergencyStopRobotArm`

**能力（5 件）**: `device.get_status` / `environment.get_environment` / `ir.send_ir_command` /
`light.set_light` / `sound.get_level`

**実装の実態 — ここは特に注意**:

| 機能 | 実際の挙動 |
|---|---|
| `GetEnvironment` | **ハードコードされた固定値**を返す。ステータスメッセージが「hardcoded fixture: no environment sensors are configured」と明言する |
| `SetLight` | 明るさは `-1`（変更なし）または `0..255`。範囲外は 400。**既定はモックの照明プロバイダ**（`MockLightIrProvider`）。GPIO 実機を使うには `AEGIS_ROOM_LIGHT_PROVIDER=gpio` と `AEGIS_ROOM_IR_PIN` が要る |
| `SendIrCommand` | `repeat` は 1..10、空の IR コードは 400。**IR コードの許可リストは存在しない**（任意の非空文字列を受け付ける） |
| `SetAirConditioner` | **503「air conditioner provider is not configured」を返すだけ。AC 機能は無い** |
| `GetCameraSnapshot` | 503（未設定） |
| `MoveRobotArm` | 403「disabled by default」 |
| `EmergencyStopRobotArm` | 空のリストを返す（実機が無い） |

IR ピンには**禁止リスト**がある（`PH4` / `PH5` を拒否）。照明の IR コードは `LIGHT_ADDR = 0xD001`
に対し 全点灯 `0x20` / エコ `0x21` / 常夜 `0x22` / 消灯 `0x23`。

> ⚠️ **`docs/architecture.md` の「AC (16-32°C validated)、IR blaster (allowlist)」は誤りだった**
> （**2026-10-02 に原典を修正済み**）。AC 経路は存在せず、IR はピンの禁止リストであってコードの許可リストではない。

---

## 6. インターフェース

### 6.1 Dashboard と web-ui 【稼働】

**ページ（Flask が返す実体）**: `/`、`/dashboard`、`/dashboard/<path>`、`/chat`、`/settings`、
`/display`、`/display/presentations`、`/display/overview`、`/display/power-state`、`/assets/<path>`

**web-ui は React SPA で、`npm run build` の出力が Flask の `static/ui-v2` に置かれ、Flask が配信する。**
本番用の別サーバは無い（`npm run dev` の 5173 は開発時のみ）。

**主な画面**（`web-ui/src/pages/`）: コマンドセンター、作業、対応待ち、承認、自律、欲望、
エージェント状態 / タイムライン / セッション、記憶、学習、能力カタログ、LLM 使用量、プロンプト管理、
システム、デバイス、ソーシャル、通知、運用、ログ、監査、不可逆性台帳、個人データ、ユーザー状態、
割り込み、設定、診断、ディスプレイ

**ライブ更新**: `GET /api/ui/stream`（SSE）。`ui.snapshot` を最初に送り、以降
`status.changed` / `task.updated` / `tool.execution.*` / `approval.created|resolved` /
`notification.created` / `chat.updated` などを流す。`last_event_id` による再送がある。

### 6.2 チャット 【稼働】

| エンドポイント | 役割 |
|---|---|
| `GET /api/chat/history` | 履歴の読み出し |
| `POST /api/chat/send` | 送信。`{text, request_id, conversation_id}` |
| `POST /api/chat/respond` | **`ask_user` への回答**。中断したタスクを再開する |
| `POST /api/chat/clear` | 履歴の消去 |

**ツール呼び出しループ**: `call_llm_with_tools(..., max_tool_rounds=15)`。同じ呼び出しの重複は
シグネチャ集合で止める。**`ask_user` が選ばれるとループは即座に返り**、`needs_user_input` と
選択肢を返す。回答は `POST /api/chat/respond` で同じループに戻る。

**履歴の共有（検証済み）**: Dashboard・Web Chat・Android は**同一の `data/chat_history.jsonl`** を
使い、**同一のツール実行経路**（`chat_service.execute_chat_message` → `call_llm_with_tools`）を通る。
Android は gRPC の `SendChat` から同じ関数を呼び、`source="android"` で追記する。

> ⚠️ `docs/dashboard.md` の「`POST /api/chat/stream` で SSE 配信」「ツールループは最大 5 ラウンド」は
> **どちらも誤り**だった（**2026-10-02 に原典を修正済み**）。ストリーム用ルートは存在せず（`/api/chat/send`
> は普通の JSON）、ループは 15 回である。SSE の `GET /api/chat/events` は登録されていたが**誰も publish
> しなかった**（届くのは heartbeat だけ）— **subscribe する側も存在しなかった**（パス文字列は定義ファイル
> 1 つにしか現れず、`EventSource` は**別チャネル**（`/api/ui/stream`、`web-ui/src/api/useOverviewStream.ts:24`）にしか無い）。**両端が死んでいた**ので、**2026-10-08 に削除した**（`DELEGATION.md` §4 項目 23）。ピン `ai-server/tests/test_chat_sse_surface_is_gone.py`。

### 6.3 承認 / 確認 UI 【稼働】

`/api/approvals/*` は**確認ストアを提供する**（強制ゲートではない）:

`GET /pending` · `GET /events`（SSE、30 秒ハートビート）· `GET /<id>` ·
`POST /<id>/approve` · `POST /<id>/reject` · `POST /<id>/cancel` · `POST /<id>/modify-and-approve`

> URL と JSON のキーは**歴史的な `approval_*` の名前のまま**にしてある（出荷済みの web-ui を
> 再ビルドせずに済ませるため）。

### 6.4 Display / XR 【稼働】

`/display` は**読み取り専用**の面で、表示専用トークンで保護される（ループバックは許可、
`X-Forwarded-Host` があれば 403）。XR は保留キュー（`/api/presentations/xr/pending`）を介する。

### 6.5 MCP 【稼働・ただし文書化されていない】

AEGIS は **MCP サーバ**として振る舞う（クライアントではない）。`aegis_agent_server/main.py` が
別プロセスで `POST /mcp`（JSON-RPC 2.0 の `initialize` / `tools/list` / `tools/call`）を提供する。
能力は `CapabilityCatalog.mcp_tool_schemas(profile)` で MCP ツールに変換され、呼び出しは
**`ToolBroker.execute` に合流する**（＝ポリシーを通る）。

> `docs/` に MCP の文書は**一つも無い**。

### 6.6 SDK とプラグイン 【SDK は稼働 / ローダは無い】

`packages/aegis-sdk-python`（`aegis-sdk-python` v0.1.0）:

- `define_capability(...)` — 能力定義を作り、ID と安全宣言を検証する
- `RegistrationClient` — サーバと能力の登録、ハートビート
- `EventClient` — イベントの送出
- 安全検証（`validate_capability_definition`、`check_forbidden_proximity`）
- テスト用の `MockAEGISCore`

**リポジトリ内の利用者は 2 つだけ**: `examples/example-weather-server/` と
`tools/create-capability-server/`（雛形生成器）。

> ⚠️ **本番サーバはどれも `aegis_sdk` を import していない。** また、**実行時のプラグインローダは
> 存在しない**。`docs/plugin-sdk.md` の「実装済み」は SDK パッケージについては正しいが、
> コアにプラグインを読み込む仕組みは無い。

---

## 7. 外部連携 — egress gate の内側と外側

**送信側はすべて egress gate を通る**（`carries_user_information=True`）。

| 連携 | 宛先 | 既定 |
|---|---|---|
| LLM（クラウド） | OpenAI 互換 | **拒否** → ローカルか Mock に降格 |
| Web 検索 | DuckDuckGo | **拒否** |
| LINE | `https://api.line.me` | **拒否** |
| Discord | Webhook（トークンは漏らさない） | **拒否** |
| メール | SMTP | **拒否** |
| Webhook | 任意 | **拒否**（HMAC 署名付き） |
| AGORA | `https://agora.kakunin.me` | **拒否** |
| 音声（edge-tts / cloud） | `speech.platform.bing.com` | **拒否** |
| ローカル TTS | OS の音声合成 | 通る（外部送信なし） |

**AGORA の投稿ガード**: 秘密情報パターンの検査、ほぼ同一内容の拒否、連投の制限
（30 分窓で最大 3 件、トップレベル 6 時間窓、クールダウン 30 分）。

> ⚠️ **LINE / Discord / メールの送信クラスは実装されているが、実行経路に配線されていない。**
> `NotificationRouter`（チャネルを登録する側）を `runtime.py` は構築しておらず、
> `NotificationManager` は `event_manager` だけを受け取る。したがって `send()` はファンアウトしない。

---

## 8. 【宣言のみ】— 存在するが動いていない機能

**この節が本カタログで最も重要である。** 以下はクラスやファイルが存在し、文書にも書かれているが、
**実行経路から誰も呼んでいない**（すべて 2026-10-02 に実測）。

| 対象 | 証拠 |
|---|---|
| **TriggerEngine** | `src/trigger_engine.py` に 13 個の既定ルールがあるが、`runtime.py` は構築しない。唯一の参照は `aegis_ai/__init__.py` の再輸出 |
| **Scheduler** | `scheduler.py` に 5 個の既定タスクがあるが、`Scheduler()` は自モジュール内でしか生成されない |
| **agents/research.py / support.py / self_dev.py** | **ファイルが存在しない**。`agents/` にあるのは backends（local / openhands）、profiles、runtime のみ |
| **observation/**（`MultimodalObservationService`） | 自パッケージと `__init__.py` 以外に参照が無い |
| **security/ パッケージ**（9 クラス） | 外部 import ゼロ。生きている認証は `aegis_ai/auth/`。`docs/security.md` に記載があるが配線すると重複する |
| **NotificationRouter と全チャネル / OsNotificationProvider** | `runtime.py` は `NotificationManager(event_manager=...)` のみ構築する |
| **音声（`SpeechToTextService` / `TextToSpeechService` / `VoiceGate`）** | どこからも生成されない。`integrations/__init__.py` の再輸出のみ |
| **CLIChannel / InteractionRouter** | `CLIChannel` は生成されない。`runtime.interaction_router` は構築されるが**一度も呼ばれない**。`console_scripts` も無い |
| **`ToolBroker.set_instance()`** | 定義されているが**一度も呼ばれない**。よって `ToolBroker.instance()` は常に `None` |
| **`LLMGateway.instance()`** | `l3_reasoner.py` と `l2_mind.py` が呼ぶが、**そのメソッドは存在しない**（死んだフォールバック） |
| **CostTracker** | `runtime.py` は `LLMRouter(cost_tracker=None)` とするので予算は効かない |
| **world/ / recovery/ / briefing/ / browser_use/ / room/** | 外部 import ゼロ |
| ~~**`permissions/`**~~ | **2026-10-03 に削除**（オーナー決定 — 配線しないと決めた承認ゲート。`DELEGATION.md` §4 項目 3） |
| **`reflection_loop.py`** | 外部 import ゼロ |
| **Dev Server（:50056）** | ディレクトリごと削除済み |

**設計上の含意**: これらは「壊れている」のではなく「**置いてあるが配線していない**」状態である。
動かす前に、どの機能が本当に生きているかをこの表で確認してほしい。

---

## 9. 既存文書との食い違い（実装が正しい）

| 文書の主張 | 実装の事実 |
|---|---|
| `architecture.md` §2.1 の図に TriggerEngine がある | 構築されない（§8） |
| `architecture.md` §5.5 に Research / Support / SelfDev Agent がある | ファイルが存在しない |
| `architecture.md` §3.5「AC (16-32°C validated)、IR blaster (allowlist)」（**2026-10-02 修正済み**） | AC は 503、IR はピンの禁止リスト |
| `dashboard.md`「`POST /api/chat/stream` で SSE」「ツールループ最大 5 ラウンド」（**2026-10-02 修正済み**） | そのルートは無い。ループは 15 回 |
| `dashboard.md` の Manager API パス（`/api/memory/<backend>` 等） | `/api/memory/search`、`/api/memory/sleep/status` など |
| `dashboard.md`「承認されたアクションは一度実行されフォローアップを投稿する」 | 強制ゲートは削除済み。確認は何もブロックしない |
| `interaction-hub.md`「CLI ✅ Implemented」 | `CLIChannel` は生成されない |
| `ui-implementation-checklist.md`「9 ドメインが存在する」（**2026-10-02 修正済み**） | `navigation.ts` は **4 ドメイン** |
| `settings.md` の `POST /settings/import` 等 | 存在しない |
| `notification-gateway.md`「外部チャネルはスタブのみ」（**2026-10-04 修正済み**） | 送信クラスは実装済み（ただし未配線） |
| `notification-gateway.md`「クワイエットアワー中は非クリティカルの通知を延期する」（**2026-10-04 修正済み**） | 判定は `QuietHoursManager.is_quiet()` で、呼ぶのは `NotificationRouter.send()` だけ。router は構築されないので一度も走らない。加えて router は `QuietHoursManager()` を**引数なしで**作るため `settings_store` が `None` のままになり、配線しても設定は読まれない（二重に死んでいる） |
| `notification-gateway.md` §Preferences「Settings で通知種別を有効/無効にできる」（**2026-10-04 修正済み**） | 7 フィールド（`approval_notification_enabled` / `support_suggestions_enabled` / `daily_briefing_notification` / `error_notification` / `quiet_hours_enabled` / `quiet_hours_start` / `quiet_hours_end`）の唯一の読み手は未構築の 2 クラスの中。`tests/test_ineffective_flags.py` の layer 1 はフィールド名の**テキスト一致**なので死んだコード内の参照も読み手と数え、**この 7 つを「読まれている」と判定して緑のまま**になる |
| `notification-gateway.md` §Safety「外部チャネル向けに機微な内容を赤塗りする」（**2026-10-04 修正済み**） | その赤塗りは削除済み。理由は `notification/router.py:102-109` のコメントにある（egress が「禁止」から許可制に変わったため、本文を空にすると許可の意味が消える。fan-out 前に `notification.body` を書き換えていたのでダッシュボード側の本文まで消えていた） |
| `voice-io.md`「配線済み」 | サービスは生成されない |
| `design-tokens/` ディレクトリ | 存在しない。実体はリポジトリ直下の `design-tokens/` |
| PC のファイル保護が「部分一致」「read/write は無検査」 | ディレクトリ名は**完全一致**、`is_protected_path` は read/write/delete/copy/move で呼ばれる |

---

## 10. 動かす前のチェックリスト

1. **`--enable-real-pc-actions` を付けたか** — 付けなければ PC 操作は効かない（観測のみ）
2. **`AEGIS_RUNTIME_MODE`** — 本番にするなら `passkey` 認証と `AEGIS_SESSION_SECRET` が必須
3. **egress gate の設定** — 既定では**外部送信はすべて拒否**される。クラウド LLM を使うなら
   `privacy.external_egress_allowed` と目的別フラグと許可ホストを設定する必要がある
4. **`autonomous_loop_enabled`** — 既定は無効。有効にすると AEGIS が自分から動き出す
5. **Room Server は既定でモック** — 照明はモックプロバイダ。AC とカメラは未実装（503）
6. **Android は外向き接続** — 端末から AI Server の 50051 に届く必要がある。ペアリングトークンが要る
7. **§8 の「宣言のみ」一覧を読む** — 文書に書いてある機能が動くとは限らない
8. **`docker compose`** — AI / Browser / Room はコンテナ、PC Server は Windows ホスト側で別途起動する

---

## 付録 A: 全 128 能力の一覧（実測）

> `CapabilityCatalog.list_for_llm()` の出力から生成。危険度と可逆性はマニフェストの注記であり、
> **ゲートではない**。

### A.1 PC Server（Rust / TCP 50052） — 58 件

| capability_id | 名称 | 危険度 | 可逆性 |
|---|---|---|---|
| `pc-server.app.show_url` | ウェブサイトをユーザーに見せる | 安全 | 回復可能 |
| `pc-server.approval.overlay` | Overlay Approval | 安全 | 回復可能 |
| `pc-server.clipboard.get_clipboard` | Clipboard | 低 | 完全可逆 |
| `pc-server.clipboard.image` | Clipboard Image | 読取のみ | 完全可逆 |
| `pc-server.clipboard.set` | Set Clipboard | 安全操作 | 回復可能 |
| `pc-server.discord.get_channels` | Discord Channels | 低 | 完全可逆 |
| `pc-server.discord.get_guild` | Discord Guild Detail | 低 | 完全可逆 |
| `pc-server.discord.get_guilds` | Discord Guilds | 低 | 完全可逆 |
| `pc-server.discord.get_selected_voice_channel` | Discord Selected Voice Channel | 低 | 完全可逆 |
| `pc-server.discord.get_voice_settings` | Discord Voice Settings | 低 | 完全可逆 |
| `pc-server.discord.join_voice_by_name` | Discord Join Voice By Name | 安全 | 回復可能 |
| `pc-server.discord.join_voice_channel` | Discord Join Voice Channel | 安全 | 回復可能 |
| `pc-server.discord.leave_voice_channel` | Discord Leave Voice Channel | 安全 | 回復可能 |
| `pc-server.discord.select_text_channel` | Discord Select Text Channel | 安全 | 回復可能 |
| `pc-server.discord.set_activity` | Discord Set Activity | 安全 | 回復可能 |
| `pc-server.discord.set_voice_settings` | Discord Set Voice Settings | 安全 | 回復可能 |
| `pc-server.discord.status` | Discord RPC Status | 低 | 完全可逆 |
| `pc-server.file.list` | List Directory | 読取のみ | 完全可逆 |
| `pc-server.file.read` | Read File | 読取のみ | 完全可逆 |
| `pc-server.file.search` | Search Files | 読取のみ | 完全可逆 |
| `pc-server.file.write` | Write File | 監査付き操作 | 困難 |
| `pc-server.input.keyboard_type` | Keyboard Type | 安全 | 困難 |
| `pc-server.input.mouse_click` | Mouse Click | 安全 | 困難 |
| `pc-server.input.mouse_move` | Mouse Move | 安全 | 完全可逆 |
| `pc-server.input.press_hotkey` | Press Hotkey | 安全 | 困難 |
| `pc-server.mouse.drag` | Mouse Drag | 安全 | 困難 |
| `pc-server.mouse.scroll` | Mouse Scroll | 安全操作 | 完全可逆 |
| `pc-server.network.info` | Network Info | 読取のみ | 完全可逆 |
| `pc-server.overlay.show_display` | Show Display Overlay | 低 | 回復可能 |
| `pc-server.overlay.show_rich` | Show Rich Display Overlay | 安全 | 回復可能 |
| `pc-server.personal_data.drain` | Drain PC personal-data events | 低 | 回復可能 |
| `pc-server.process.kill` | Kill Process | 安全 | 困難 |
| `pc-server.process.list` | List Processes | 読取のみ | 完全可逆 |
| `pc-server.registry.list_keys` | List Registry Keys | 読取のみ | 完全可逆 |
| `pc-server.registry.read` | Read Registry | 読取のみ | 完全可逆 |
| `pc-server.screen.get_ui_tree` | PC UI Tree | 安全 | 完全可逆 |
| `pc-server.screenshot.get_screenshot` | Screenshot | 低 | 完全可逆 |
| `pc-server.service.list` | List Services | 読取のみ | 完全可逆 |
| `pc-server.service.start` | Start Service | 安全 | 回復可能 |
| `pc-server.service.stop` | Stop Service | 安全 | 困難 |
| `pc-server.shell.execute` | Execute Shell Command | 高 | 不可逆 |
| `pc-server.shell.powershell` | Execute PowerShell | 高 | 不可逆 |
| `pc-server.system.empty_recycle_bin` | Empty Recycle Bin | 安全 | 不可逆 |
| `pc-server.system.event_log` | Event Log | 読取のみ | 完全可逆 |
| `pc-server.system.get_os_info` | OS Info | 低 | 完全可逆 |
| `pc-server.system.get_screen_size` | Screen Size | 低 | 完全可逆 |
| `pc-server.system.installed_software` | Installed Software | 読取のみ | 完全可逆 |
| `pc-server.system.launch_app` | Launch App | 安全 | 回復可能 |
| `pc-server.system.lock` | Lock Workstation | 安全操作 | 回復可能 |
| `pc-server.system.performance_counters` | Performance Counters | 読取のみ | 完全可逆 |
| `pc-server.system.show_overlay` | Show Overlay | 安全 | 回復可能 |
| `pc-server.system.windows_features` | Windows Features | 読取のみ | 完全可逆 |
| `pc-server.task.list` | List Scheduled Tasks | 読取のみ | 完全可逆 |
| `pc-server.user_activity.snapshot` | Get PC user activity snapshot | 低 | 完全可逆 |
| `pc-server.window.close_window` | Close Window | 安全 | 困難 |
| `pc-server.window.get_active_window` | Active Window | 低 | 完全可逆 |
| `pc-server.window.list_windows` | List Windows | 低 | 完全可逆 |
| `pc-server.window.resize` | Resize Window | 安全操作 | 回復可能 |

### A.2 AI Server（Python・プロセス内） — 32 件

| capability_id | 名称 | 危険度 | 可逆性 |
|---|---|---|---|
| `ai-server.agent.delegate` | Delegate task to agent runtime | 低 | 完全可逆 |
| `ai-server.agora.post` | Post to AGORA | 安全 | 困難 |
| `ai-server.agora.read_posts` | Read AGORA Posts | 低 | 完全可逆 |
| `ai-server.commitment.list` | List Commitments | 低 | 完全可逆 |
| `ai-server.commitment.transition` | Transition Commitment | 安全 | 回復可能 |
| `ai-server.commitment.upsert` | Create Or Update Commitment | 安全 | 回復可能 |
| `ai-server.commitment.wakeup` | Commitment Wakeup | 低 | 完全可逆 |
| `ai-server.confirmation.list` | Read Confirmations and Their Answers | 低 | 完全可逆 |
| `ai-server.confirmation.request` | Ask the User to Confirm | 低 | 完全可逆 |
| `ai-server.delegation_policy.list` | List Delegation Policy | 低 | 完全可逆 |
| `ai-server.delegation_policy.upsert` | Create Or Update Delegation Rule | 安全 | 回復可能 |
| `ai-server.hook.list` | List Hooks | 低 | 完全可逆 |
| `ai-server.hook.upsert` | Create Or Update Hook | 安全 | 回復可能 |
| `ai-server.interruption.status` | Get Interruption Status | 低 | 完全可逆 |
| `ai-server.memory.save` | Memory Save | 低 | 回復可能 |
| `ai-server.memory.search` | Memory Search | 低 | 完全可逆 |
| `ai-server.memory.sleep` | Memory Sleep (Consolidation) | 低 | 困難 |
| `ai-server.notification.broadcast_overlay` | Broadcast Overlay Notification | 安全 | 回復可能 |
| `ai-server.personal_data.search` | Personal Data Search | 低 | 完全可逆 |
| `ai-server.presentation.action` | Presentation User Action | 読取のみ | 回復可能 |
| `ai-server.presentation.dismiss` | Dismiss Presentation | 読取のみ | 回復可能 |
| `ai-server.presentation.list` | List Presentations | 読取のみ | 完全可逆 |
| `ai-server.presentation.present` | Present to User | 読取のみ | 回復可能 |
| `ai-server.repair.disable` | Disable Repair Manager | 安全 | 回復可能 |
| `ai-server.repair.list` | List Repair History | 低 | 完全可逆 |
| `ai-server.search.web` | Web Search | 低 | 完全可逆 |
| `ai-server.situation.get` | Get Situation | 低 | 完全可逆 |
| `ai-server.user_model.get` | Get User Model | 低 | 完全可逆 |
| `ai-server.user_model.update` | Update User Model | 安全 | 回復可能 |
| `ai-server.workspace.list_files` | List Filesystem Directory | 低 | 完全可逆 |
| `ai-server.workspace.read_file` | Read Filesystem File | 低 | 完全可逆 |
| `ai-server.workspace.write_file` | Write Filesystem File | 安全 | 困難 |

### A.3 Browser Server（Python / HTTP 50053） — 16 件

| capability_id | 名称 | 危険度 | 可逆性 |
|---|---|---|---|
| `browser-server.account.create` | Create web account | 監査付き操作 | 困難 |
| `browser-server.element.click` | Click browser element | 監査付き操作 | 困難 |
| `browser-server.feed.monitor` | Monitor web feed | 低 | 完全可逆 |
| `browser-server.file.download` | Download web file | 安全 | 回復可能 |
| `browser-server.file.upload` | Upload file to website | 監査付き操作 | 困難 |
| `browser-server.form.fill` | Fill web form | 監査付き操作 | 回復可能 |
| `browser-server.form.submit` | Submit web form | 監査付き操作 | 困難 |
| `browser-server.page.browse` | Browse with AI | 監査付き操作 | 不明 |
| `browser-server.page.navigate` | Navigate private browser | 安全 | 完全可逆 |
| `browser-server.page.read` | Read web page privately | 低 | 完全可逆 |
| `browser-server.page.summarize` | Summarize web page privately | 低 | 完全可逆 |
| `browser-server.search.query` | Private web search | 低 | 完全可逆 |
| `browser-server.session.authenticated` | Use authenticated browser session | 安全 | 回復可能 |
| `browser-server.session.open` | Open private browser session | 安全 | 完全可逆 |
| `browser-server.social.post` | Post on website | 監査付き操作 | 困難 |
| `browser-server.social.react` | React on website | 監査付き操作 | 回復可能 |

### A.4 Android Server（Kotlin / 外向きクライアント） — 17 件

| capability_id | 名称 | 危険度 | 可逆性 |
|---|---|---|---|
| `android-server.accessibility.get_status` | Android Accessibility Status | 低 | 完全可逆 |
| `android-server.app.open` | Open Android App | 安全 | 回復可能 |
| `android-server.approval.request` | Ask the User on Android | 安全 | 回復可能 |
| `android-server.device.get_status` | Android Device Status | 低 | 完全可逆 |
| `android-server.location.get_current` | Android Current Location | 安全 | 完全可逆 |
| `android-server.notification.get_notifications` | Android Notifications | 安全 | 完全可逆 |
| `android-server.overlay.show` | Show Android Overlay | 安全 | 回復可能 |
| `android-server.permissions.get_status` | Android Permission Status | 低 | 完全可逆 |
| `android-server.safety.emergency_stop` | Android Emergency Stop | 安全 | 困難 |
| `android-server.screen.get_current_app` | Android Current App | 安全 | 完全可逆 |
| `android-server.screen.get_screenshot` | Android Screenshot | 安全 | 完全可逆 |
| `android-server.screen.get_ui_tree` | Android UI Tree | 安全 | 完全可逆 |
| `android-server.ui.back` | Android Back | 安全 | 回復可能 |
| `android-server.ui.home` | Android Home | 安全 | 回復可能 |
| `android-server.ui.swipe` | Android Swipe | 監査付き操作 | 困難 |
| `android-server.ui.tap` | Android Tap | 監査付き操作 | 困難 |
| `android-server.ui.type_text` | Android Type Text | 監査付き操作 | 困難 |

### A.5 Room Server（Python / gRPC 50055） — 5 件

| capability_id | 名称 | 危険度 | 可逆性 |
|---|---|---|---|
| `room-server.device.get_status` | Room Device Status | 低 | 完全可逆 |
| `room-server.environment.get_environment` | Environment | 低 | 完全可逆 |
| `room-server.ir.send_ir_command` | Send Room IR Command | 安全 | 困難 |
| `room-server.light.set_light` | Set Room Light | 安全 | 回復可能 |
| `room-server.sound.get_level` | Room Sound Level | 低 | 完全可逆 |
