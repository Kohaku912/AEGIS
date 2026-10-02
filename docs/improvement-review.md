# AEGIS 改善点レビュー — コードベース全体の掃討

> **この文書の位置づけ（最初に読むこと）**
>
> これは **正典（レジスタ）ではなく調査報告**である。各行は「**現状 / 改善の方向性 / 優先度 / 帰属**」を持ち、
> **帰属**の欄が「この判断の所有者は誰か」を名指しする。所有者が既存レジスタにある行は、**そちらが正典**であり
> この文書は写しを持たない（写しは腐る。規則 1）。
>
> - 目標そのものの定義 → `docs/GOAL-CHANGE.md`
> - 実装在庫と未決 → `PROJECT_STATUS_REVIEW.md` §0.2 / §3.1 / §3.2 / §4.1 / §4.3
> - 委任で決めた枝と戻し方 → `DELEGATION.md` §2 / §4
> - 機能の網羅的な説明 → `docs/feature-catalog.md`
>
> **この調査の新規部分は「測定」であって「決定」ではない。** 下の §1〜§5 のうち、既存レジスタに無い行には
> `【新規】` を付けた。`【既知】` は既存レジスタが既に所有しており、ここでは**優先度の判断材料として再掲**する。
>
> **測定日**: 2026-10-02。**測定環境**: `ai-server` のソースツリー、`git ls-files`、AST/`grep` 走査。
> **この文書は「AEGIS が完成した」とは主張しない。** 主張するのは「測定した範囲で、以下が未達である」ことだけである。

---

## 0. 結論

### 0.1 最も重い 3 件

| # | 一言で | なぜ目標に効くか |
|---|---|---|
| **1** | **egress ゲートが「全拒否」のまま実装されている**（目標は再定義済みで、接続は可・許可ある開示も可） | **唯一の制約そのもの**。今の実装は**目標より厳しい**。許可の配線が未了なので、クラウド LLM・Web 検索・外部メッセージ・音声は**許可を与えても到達不能** |
| **2** | **宣伝されている「イベント駆動の中核」がインスタンス化されていない**（`TriggerEngine` / `Scheduler` / `EventView` の 3 つが全部） | `docs/architecture.md` は AEGIS を "**event-driven**" と定義し図とシーケンス図まで載せるが、プロセス内にトリガエンジンが存在しない。実体は**ポーリング駆動** |
| **3** | **`docs/testing.md` が挙げるテスト **17 本**が、1 本も存在しない**（同種の写し 4 文書も — すべて修正済み） | 「その検証はある」と読者に信じさせる。しかも 2026-09-28 の掃討は**この文書を漏らしていた** |

### 0.2 測定で**反証された**懸念（＝対応不要。これも成果である）

| 懸念 | 測定結果 |
|---|---|
| 「egress ゲートを迂回する外部呼び出しがあるのでは」 | **11 モジュール・12 呼び出し点**が `get_egress_gate()` を直接呼び、LLM 層はさらに `egress_allows_llm` ヘルパ経由で 4 箇所（`factory.py:164,234,267` / `gateway.py:142`）。**すべて fail-closed**。直接 `urlopen` する 2 箇所も確認済みで、両方ゲートに到達する |
| 「ダッシュボードに認証の穴があるのでは」 | **passkey 態**では 169 の route を全数分類して**穴は 1 つも無い**（保護外は「設計上の除外」か「ハンドラが自己防衛」のみ）。ただし**既定の開発構成では認証ミドルウェア自体が載らない**（意図的な dev 逃げ道 — S-1） |
| 「秘密情報がコミットされているのでは」 | **0 件**。`.gitignore` が `.env` / `secrets/` / `*.pem` / `*.key` / `data/` を覆い、`scripts/audit-secrets.py` とテストが監視している |
| 「同期ブロッキング I/O がイベントループを止めるのでは」 | gRPC は **sync サーバ + スレッドプール**なので、ブロッキングは 1 ワーカーを占有するだけでループ飢餓にはならない（ただし §2 E-2 の容量上限は残る） |

---

## 1. 目標との齟齬

### G-1 【新規】egress ゲートが目標より厳しい — 「許可があっても出せない」　`P0`

**現状（測定）**

制約は 2026-09-30 に再定義された: **許可の無い**ユーザー情報の送信を禁じる。**接続は可、許可ある開示は可**（正典 `docs/GOAL-CHANGE.md`）。ところがゲートの実装は再定義前の**全拒否**のままである。ソース自身がそれを記録している:

```
ai-server/src/aegis_ai/llm/factory.py:157-164
    # ── Egress gate: the single constraint ──────────────────────────────────
    # ... re-scoped 2026-09-30 to "**unpermitted** user information must never leave
    # the local environment", with outbound connections and user-permitted disclosure
    # allowed. The check below still implements the pre-re-scope deny-all form;
    # the permission wiring is open work. It cannot be bypassed by a settings flag alone.
```

帰結（測定）:

- `privacy.external_llm_allowed` は **読まれている**（`llm/factory.py:267` が `settings.privacy.external_llm_allowed and egress_allows_llm(...)` の形で参照）。しかし**結合条件**なので、ゲートが拒否すれば設定を立てても無効。クラウド LLM は `_local_or_mock` へ落ちる。
- 同じ形が Web 検索（`integrations/duckduckgo_search.py:_egress_allows`）、外部メッセージ（`notification/channels/outbound.py:_egress_allows`）、Webhook、Agora、TTS、OpenHands、天気、`server_executor` に波及する。
- **fail-closed は正しい**（安全側）。問題は**許可の側の配線が無い**ことである。

**改善の方向性**

ゲートの API は既に許可の 3 経路を持っている: ① master スイッチ `privacy.external_egress_allowed` ② purpose フラグ ③ `allowed_hosts` 収載、または記録済み `(host, purpose)` グラント。**実装すべきは「許可が与えられたときゲートが通す」ことの配線と、その許可をユーザーから取る経路**である。既存の `ConfirmationStore`（強制ゲートではない、AEGIS 起点の非ブロッキング確認）がその担い手になりうる。

**帰属**: **オーナー判断**（制約の解釈と、どの開示を許可と呼ぶかの定義）。実装はそれに従う。

---

### G-2 【新規】イベント駆動の中核が 3 つとも未構築 — 実体はポーリング駆動　`P1`

**現状（測定）**

| 構成要素 | `src/` 内の構築箇所 | 判定 |
|---|---|---|
| `TriggerEngine` | **0 件**。唯一の `TriggerEngine()` は `trigger_engine.py:175` の**自モジュールの `__main__` デモ** | **未構築** |
| `Scheduler` | **0 件**。唯一の `Scheduler()` は `scheduler.py:75` の**自モジュールの `__main__` デモ** | **未構築** |
| `EventView` | **0 件**。`observability/__init__.py:5` の再輸出のみ | **未構築** |
| `AutonomousLoop` | **構築される** — `runtime.py:1625`。フラグ `autonomous_loop_enabled` は `runtime.py:122` に**実読者**を持つ | **稼働** |

`TriggerEngine` には `src/trigger_engine.py` に **13 個の既定ルール**が書かれている。`EventView.get_trigger_stats()` / `get_pending_tasks()` は `self._engine` を guard するので、たとえ構築されても `{}` / `[]` を返す（`event_view.py:52,65`）。

さらに**起動ログが偽の主張を印字する**:

```
ai-server/src/aegis_ai/main.py:27
    logger.info("Trigger Engine: %s", "enabled" if config.trigger_enabled else "disabled")
```

`config.trigger_enabled` の読者は**この 1 行だけ**（`config.py:34` の宣言を除く）。つまり **`TriggerEngine` が存在しないプロセスが「Trigger Engine: enabled」と毎回出力する**。設定フラグの読者がログ 1 行だけという形は、`test_ineffective_flags.py` が「読まれている」と判定するため**検出器の死角**である（読まれること ≠ 効くこと）。

**文書側の主張（測定）** — 齟齬は文書に明記されている:

- `docs/architecture.md:20` — "AEGIS is an **autonomous, event-driven, self-improving** AI assistant"
- `docs/architecture.md:57`（図のノード）, `:84-85`（`EventBus --> TriggerEngine --> ContextBuilder`）, `:108`（core クラス一覧）, `:170`（Key modules）, `:174`（"Decide when to wake up (TriggerEngine)"）, `:559`（**シーケンス図** `participant TE as TriggerEngine`）
- `docs/android-safety.md:190`, `docs/room-safety.md:100` — `EventBus → TriggerEngine → ContextBuilder`
- `docs/proto-overview.md:114` — `AI Server (Event Bus) ──► Trigger Engine`

**改善の方向性**

2 つの枝のどちらか。**① 構築する** — `runtime.py` で `TriggerEngine` を生成し `EventBus` を購読させ、`config.trigger_enabled` をその生成条件として読む（`AutonomousLoop` と同じ形）。`Scheduler` と `EventView` も同様。**② 文書を実測に合わせる** — 「イベント駆動」の記述と図を実態に直し、`trigger_enabled` を**宣言ごと外す**（読者が 1 つもいないなら、無いより無いほうが正直）。①を選ぶなら、**ログ行が主張する前に**生成を確認する順序にする。

**帰属**: **オーナー判断**（①/②は製品判断）。ただし**偽の起動ログは判断を待たずに直すべき**（P0 相当の小さな修正）。

---

### G-3 【新規（クラスは既知）】`docs/testing.md` は 17 本の存在しないテストを名指ししていた　`P1` — **修正済み**

**現状（測定、2026-10-02）**

`docs/testing.md` は「**Status**: Active (verified against current code snapshot)」と名乗りながら、
名指しするテストファイルの大半が存在しない。1 本ずつ測った:

| 節 | 記載 | 実測 |
|---|---|---|
| Quick Reference | `pytest ../tests/` | **`../tests/` はディレクトリとして存在しない**（テストは `ai-server/tests/`） |
| Unit Tests | 8 本 | **8 本すべて存在しない** |
| E2E Integration | 8 本 | **8 本すべて存在しない** |
| Local-Only | `test_pc_observe_e2e.py` | 存在しない |
| Current Test Commands | `test_approval_redesign.py` | 存在しない |

**17 本**のテストファイルがリポジトリ全体で 0 件。実在するのは `test_e2e_lifecycle.py` と
`test_e2e_integration.py` の 2 本で、後者が触るのは `EventBus` のみ（`TriggerEngine` /
`ContextBuilder` / `AutonomousLoop` は 1 箇所も現れない）。テストモジュール総数は **144** で
ディレクトリ自体は充実している — **名指しだけが虚構**である。

**このクラスは既知であり、掃討が漏れていた。** 2026-09-28 の掃討は `docs/pc-server.md`・
`docs/room-server.md`・`docs/testing-real-devices.md` を直し、`test_server_docs_are_accurate.py`
を作った（`PROJECT_STATUS_REVIEW.md` に台帳行がある）。しかしそのピンが読むのは各サーバの
`AGENTS.md` の **`## Directory Structure` フェンスだけ**なので、**別の文書の別のフェンスにある
`pytest tests/...` は最初から視野の外**だった。**掃討の被覆は主張であり、測る必要がある** — 実例。

同じ掃討が漏らしていた写し（本調査で実測・修正）:

| 写し | 内容 |
|---|---|
| `docs/android-server.md` §Testing | `test_android_observe_e2e.py` / `test_android_action_e2e.py` を実行せよと指示 |
| `docs/research-e2e.md` §Running | 3 本。しかも**同じ文書のバナーが既に「No test file covers them」と書いていた** — バナーは足されたがその下のコマンド節は掃かれず、**文書が自分と矛盾していた** |
| `ai-server/AGENTS.md` | エージェントが最初に読む面が、存在しないテスト 3 本を指示 |
| `docs/beta-runbook.md` | `--ignore=tests/test_approval_ui.py`（存在しない） |

**実施した修正**: 上記 4 文書を実測に合わせた。`docs/testing.md` のテスト一覧は**フェンス内の名前を
ディレクトリ参照に置き換えた** — 新しい手書きリストは同じ腐り方を再生産するだけだからである。
`docs/dev-server.md` は**触っていない**（バナー付きの歴史的記録で、「do not follow the setup
instructions below」と明記されている）。

**ピン**: `ai-server/tests/test_docs_run_tests_that_exist.py` を追加。**フェンス内**の
`tests/<name>.py` だけを見て（散文は自由 — 退職したテストを語る記録は残さねばならない）、
解決しない集合が**記録済み集合と等しい**ことを主張する。除外は**規則**（ドット始まりの
ディレクトリを丸ごと刈る）で、除外リストではない。変異 **4/4** 捕捉。

**帰属**: **推奨で閉じられる**（修正・ピンとも完了）。`TriggerEngine` を通す e2e の追加は G-2 の枝に従属。

---

### G-4 【既知】`§3.2` の ❌ 群 — どれを v1 に入れるか　`P2`

**現状**: gRPC TLS 未配線 / Room devices 未構成 / オフライン劣化は v1 対象外 / マルチユーザー・プラグインマーケット未着手（`PROJECT_STATUS_REVIEW.md` §3.2）。
**改善の方向性**: オーナーが v1 の範囲を決める。決定した行だけ実装に落ちる。
**帰属**: **オーナー判断**（`DELEGATION.md` §4 項目 10）。**ここでは再掲のみ、写しは持たない。**

---

## 2. 非効率

### E-1 【新規】中核が死んでいるので全体がポーリングになっている　`P1`

**現状（測定）**

- 自律ループは `time.sleep(sleep_s)` で待つ（`autonomous/autonomous_loop.py:489`、`sleep_s` は `_compute_idle_sleep_seconds(now)`）。例外時は `time.sleep(60)`（`:492`）。
- 記憶の統合ループは `time.sleep(60)` の固定ポーリング（`memory/sleep_consolidation.py:107`）。
- イベントは `EventBus` に届くが、**それを購読して早期起床させる `TriggerEngine` が居ない**（G-2）。

帰結: ユーザー入力に対する反応の遅延が**ポーリング間隔に下限を食われる**。アイドル時の起床も間隔依存である。**G-2 と E-1 は同じ 1 つの欠落の 2 つの顔**である。

**改善の方向性**: G-2 の枝に従う（構築すれば早期起床が可能になる）。構築しないなら、間隔を短くするのは**コストと引き換えの対症療法**であることを記録する。
**帰属**: **G-2 に従属**。

---

### E-2 【新規】gRPC ワーカープールが 10、外部呼び出しのタイムアウトが最大 30 秒　`P2`

**現状（測定）**: `config.max_workers` の既定は **10**（`config.py:24`、`AEGIS_MAX_WORKERS`）。gRPC は `futures.ThreadPoolExecutor(max_workers=config.max_workers)` で回る（`grpc_server.py:502-503`）。一方、外向き呼び出しのタイムアウトは `agents/backends/openhands/workspace.py:_default_http_post(timeout=30.0)`、天気は 10 秒、通知は 15 秒。

帰結: **遅い外部呼び出しが 10 本同時に立つと、AI Server 全体が新規要求を受けられなくなる**。しかも egress 許可の配線（G-1）が入ると、外部呼び出しは**増える方向**に動く。

**改善の方向性**: ① `max_workers` を実測負荷に合わせて上げる（設定なので運用で可能）② 外部呼び出しを要求処理スレッドから**切り離す**（結果は確認/通知経路で返す）③ タイムアウトを用途別に見直す。①②の順で安い。
**帰属**: **推奨で閉じられる**（①は設定、②は設計）。

---

### E-3 【新規】エージェント 1 ステップごとにスレッドプールを生成・破棄している　`P2`

**現状（測定）**: `task/execution_engine.py:349` が、既にイベントループが動いている枝で `concurrent.futures.ThreadPoolExecutor(max_workers=1)` を `with` で**呼び出しごとに生成**する。生成・破棄のコストがステップ数に比例して乗る。

**改善の方向性**: 共有の単一スレッド実行器（または既存プール）を使い回す。分岐の意図（sync からコルーチンを回す）は保てる。
**帰属**: **推奨で閉じられる**。

---

### E-4 【既知】検索式で最高重みの項 `aliases` に生産者が 0 件　`P3`

**現状**: `capability_index._keyword_score` は `aliases` に **1.6**（全フィールド中最高、`title` の 1.2 より上）を与えるが、出荷 manifest **128 件のうち 0 件**が `aliases` を宣言する（`DELEGATION.md` §4 項目 15、実測 2026-10-01）。空文字列は分母の `if text` で除外されるため**挙動への影響は無い**（純粋な死んだ重み）。
**改善の方向性**: 128 件に alias を書く（検索品質の製品判断）か、`aliases` を宣言ごと外す。
**帰属**: **オーナー判断**（§4 項目 15）。

---

## 3. セキュリティのリスク

### S-1 【新規・一部訂正】認証は**三態**で、既定の開発構成では**ミドルウェアが 1 つも載らない**　`P1`

**現状（測定）**

> **本節は当初「保護はミドルウェア 1 箇所で決まる」と書いていたが、それは誤りだった。** 測り直すと、
> **既定の開発構成では認証ミドルウェアがそもそも install されない**。以下は測定し直した内容である。

`install_dashboard_token_auth`（`web/auth.py:29`）は **3 態**を解決する:

| 条件 | 解決 | 実際に載るもの |
|---|---|---|
| `AEGIS_RUNTIME_MODE=production`、または `AEGIS_AUTH_MODE=passkey` | **passkey** | `install_passkey_auth` → 接頭辞許可リストの `before_request` |
| 非 production かつ `AEGIS_DASHBOARD_ACCESS_TOKEN` あり（または `AEGIS_AUTH_MODE=token`） | **token** | `_require_dashboard_token` |
| **非 production かつ token なし**（＝**素の既定**） | **disabled** | **何も載らない** — 全 route が公開 |

実測: 素の構成で `DashboardApp` を組み立てると **169 route** に対し `before_request` は
`ui_v2_prefer_spa_shell` / `_before_request` / `_bind_request_correlation` の 3 つだけで、
`_load_and_require_auth` は**存在しない**。（当初「84 経路」と書いたのは**ソースのデコレータが宣言する
経路**の数で、実際に登録される rule は 169 ある — 両者は別の量である。）

**この `disabled` は意図的である** — `BUG_REPORT.md` 項目 7 が「dev 逃げ道は `web/auth.py` 側で担保」
として記録している。安全側の向き（**production では token が拒否される**）は
`tests/test_passkey_auth.py:282 test_production_token_mode_is_rejected` が既に固定している。
**したがってコードの欠陥ではない。**

**残る欠陥は 2 つ:**

1. **route 被覆の不変条件を何も強制していない。** passkey 態の保護は
   `auth/session_middleware.py` の接頭辞許可リスト 1 箇所で決まり、対象は `/`, `/dashboard`,
   `/settings`, `/chat`, `/api/`, SSE/WS のみ。**一致しない経路は `return None`（無認証で通す）** —
   default-deny ではないので、**新しい接頭辞に route を 1 本足すと既定で公開**になる。
   この不変条件を固定するテストは無く（`url_map.iter_rules()` を使うテスト 2 本は、特定 route の
   存在と GET 限定性しか見ない）、route 単位の認証デコレータも **0 件**。
2. **文書が `http://0.0.0.0:8090` を案内しながら、認証の状態を書いていない。** `dashboard.py:24` と
   `docker_entrypoint.py:53` の bind 既定は **`0.0.0.0`** で、`docs/operations.md`・
   `docs/daily-use.md`・`docs/beta-runbook.md` がその URL を案内する。素の構成では
   **全インターフェースに無認証で開く**ことになるが、どの文書もそれを書いていない
   （`docs/v1-completion-checklist.md:117` は本番についてのみ「unauthenticated を拒否」と書く）。

**測定された「passkey 態での穴が無い」ことの内訳** — 保護外に出る経路は 8 種のみ:
`/assets/<path:filename>`, `/display`（5 種）, `/health`, `/static/<path:filename>`。
`/display/*` はハンドラが `_require_display_read()` で自己防衛する（`web/routes/ui_v2.py:80,87,92`）。
`/auth/*` は接頭辞外だが**ハンドラが自己防衛**する（`/auth/me`・`/auth/passkeys` は
`_session_required()`、`auth/routes.py:125,138`）。

**改善の方向性**: ① route 被覆の不変条件を **`url_map` 駆動のテスト**で固定する（保護でも除外でも
分類されていない route が現れたら落ちる）② `docs/operations.md` に**既定の認証状態**を明記する
（`0.0.0.0` に開くなら、無認証であることも書く）。
**帰属**: **推奨で閉じられる**（①②）。dev の既定 bind を loopback に変えるかは**オーナー判断**。

---

### S-2 【新規】表示トークンの規則が 2 箇所にあり、片方は**拒否経路が到達不能**　`P2`

**現状（測定）**: 同じ規則が 2 つ存在する。

- `auth/session_middleware._display_read_allowed`（`:178-194`）
- `web/routes/ui_v2._require_display_read`（`:114-129`）

`_display_read_allowed` は「早期に**許可**する」ことしかできない。理由: 呼び出し位置は `protected` 判定の**前**にあり、`/display/...` は**保護接頭辞に 1 つも一致しない**ので、`_display_read_allowed` が `False` を返しても後段の `if not protected: return None` に落ちて**やはり通る**。つまり**この関数の拒否分岐は到達不能**である。実質的に生きた唯一の用途は `/api/ui/stream?surface=display`（`/api/` 配下なので保護され、早期許可が効く）である。

実際に `/display/*` を守っているのは `ui_v2._require_display_read`（`tests/test_passkey_auth.py:217` が 403 を assert しており、そのテストは**ミドルウェアを install していない**ので、403 はハンドラ由来だと確認できる）。

**改善の方向性**: ① 規則を 1 実装に統合する ② または 2 つを残すなら**一致を assert する**（「同じ事実を 2 つが語るなら一致を主張する」）。統合が素直。あわせて、**拒否分岐が到達不能であること**を記録する（現状は「守っている」と読める）。
**帰属**: **推奨で閉じられる**。

---

### S-3 【既知・数値訂正あり】`aegis_ai/security/` は未配線のパッケージ — 実測は **9 クラス**（記録は 6）　`P2`

**現状（測定 2026-10-02）**: `ai-server/src/aegis_ai/security/` は **9 クラス / 7 ファイル**（`auth.py` 2, `csrf.py` 1, `origin.py` 1, `rate_limit.py` 2, `tls.py` 1, `tls_config.py` 1, `tokens.py` 1）。`src/` 内の**外部 import は 0 件**。生きた認証は `aegis_ai/auth/`（passkey + セッション）なので、これは**欠落ではなく置換済み**。gRPC は**平文**（`add_secure_port` の生存呼び出し元が無い）。

**数値の訂正**: `DELEGATION.md` §4 項目 14 は「**6 クラス**」と記録しているが、実測は **9** である。同項目の「パッケージ外 import 0 件」という**結論は変わらない**（そちらは正しい）。クラス数のみ訂正が必要。

**改善の方向性**: 配線する（**生きた `auth/` と二重実装になる**ので非推奨）か、削除する（文書化されたパッケージ全体で 1 コミット）。
**帰属**: **オーナー判断**（§4 項目 14。ただし**クラス数の訂正は推奨で閉じられる**）。

---

### S-4 【新規】`typesafe_provider._system_one` は呼び出し時にゲートを見ない（構築経路依存）　`P3`

**現状（測定）**: `llm/providers/typesafe_provider.py:312-349` は `Authorization: Bearer` を付けて `request.urlopen(req, ...)` を直接呼ぶ。**メソッド内にゲート呼び出しは無い**。安全側の根拠は**構築経路**にある — `TypeSafeProvider(` の構築は `src/` 内で `llm/factory.py:171` と `llm/gateway.py:167` の 2 箇所のみで、**どちらもゲート済み**（`factory.py:164` / `gateway.py:142`）。

**改善の方向性**: 多層防御として、`_system_one` の直前でもゲートを 1 回引く（コストは無視できる）。あるいは「構築経路が唯一の入口である」ことをテストで固定する（現状は**規約**であって検査ではない）。
**帰属**: **推奨で閉じられる**。

---

### S-5 / S-6 【新規・反証】直接 `urlopen` する残り 2 箇所と、秘密情報　`P3`

- `agents/backends/openhands/workspace.py:_default_http_post` — **ゲート済み**（`:213-228`。ゲートが引けない場合も `allowed = False` に倒す fail-closed）。対応不要。
- `status/status_manager.py:357` — `http://{host}:{port}/health` への**ループバック**健全性検査。ユーザー情報を運ばない。対応不要。
- **コミットされた秘密情報 0 件**。`.gitignore` が `.env` / `.env.*` / `secrets/` / `*.pem` / `*.key` / `data/` / `ai-server/data/` を覆い、`scripts/audit-secrets.py` とテストが存在する。対応不要。

---

## 4. 保守性のリスク

### M-1 【新規 + 既知】文書とソースの食い違いが複数箇所に残っている　`P1`

**現状（測定）**: この調査で新たに測ったものを含め、少なくとも以下が**文書の主張とソースが食い違う**:

| 文書の主張 | ソースの実測 | 出典 |
|---|---|---|
| `docs/testing.md` のテスト名 **17 本** | **17 本すべて存在しない**（実在は別名 2 本）。同種の写し 4 文書も本調査で修正 | **本調査**（G-3） |
| `docs/architecture.md` の TriggerEngine 図・シーケンス | **未構築**（3 構成要素とも） | **本調査**（G-2） |
| `DELEGATION.md` §4 項目 14「6 クラス」 | **9 クラス / 7 ファイル** | **本調査**（S-3） |
| `docs/architecture.md` §3.5「AC（16-32°C 検証済み）、IR blaster（allowlist）」 | ソースは `SetAirConditioner` に **503**、許可方式は**ピン denylist（PH4/PH5）**で allowlist ではない | `feature-catalog.md` §9 |
| `docs/dashboard.md`「`POST /api/chat/stream`」 | **その route は存在しない** | `feature-catalog.md` §9 |
| `docs/dashboard.md`「最大 5 ラウンド」 | ソースの既定は **15** | `feature-catalog.md` §9 |
| `docs/ui-implementation-checklist.md:36`「**Nine domains exist: Command, Work, Intelligence, Capabilities, Infrastructure, Communications, Governance, Observability, Configuration**」（`:120` にも再掲） | `web-ui/src/navigation.ts:10` の `DomainId` は **4**（`cockpit \| observe \| personal \| settings`）で、**名前も 1 つも一致しない** | **本調査**（実測） |

**改善の方向性**: ① 各主張をソースに合わせて掃討する（**掃討は「言い換え」ではなく「測り直し」**。数値表は全行を実行してから直す）② 重要な主張は**文書ではなくソースに固定する**（`test_schema_mirrors_the_protobuf_schema.py` の形で「2 つが同じ事実を語るなら一致を assert する」）。
**帰属**: **推奨で閉じられる**（①）。②の対象選定は判断。

---

### M-2 【新規 + 既知】「宣言されているが効かない」クラスは**今も増えている**　`P1`

**現状（測定）**: この調査だけで新しい実例が 3 つ出た。

1. **`TriggerEngine` / `Scheduler` / `EventView`** — クラスは存在し、文書は図に載せ、`__init__.py` は再輸出するが、**構築されない**（G-2）。
2. **`config.trigger_enabled`** — 読者は `main.py:27` の**ログ 1 行だけ**。したがって設定は「読まれている」と検出されるが、**挙動を 1 つも変えない**。
3. **`_display_read_allowed`** — 存在し、テストもあり、`/api/ui/stream` では生きているが、`/display/*` に対しては**拒否分岐が到達不能**（S-2）。

**改善の方向性**: 検出器（`test_ineffective_flags.py`）は**設定モデルを列挙する**ので、①のような**パッケージ/クラス丸ごとの死**は原理的に見えない。②のような「読者はいるが効かない」も見えない。**検出器の走査単位そのものが選択である**ことを踏まえ、単位を「モデルのフィールド」から「**実行経路に到達するか**」へ一段広げる価値がある。
**帰属**: **推奨で閉じられる**（検出器の拡張）。個々の行の処理はオーナー判断。

---

### M-3 【新規】レジスタ自身が読めなくなっている　`P2`

**現状（測定）**: `PROJECT_STATUS_REVIEW.md` は **2114 行**。`DELEGATION.md` §4 は **21 行すべてが「記録のみ（意図的）」**で、いずれも「オーナーが戻せる」形。一方 `§0.2 オーナー判断レジスタ（未決のみ）` は**空**である。

帰結: 読者は「**決定済みだが未実装**」と「**未決定**」を、`§0.2` が空であることからは区別できない。`DELEGATION.md` §5 の末尾が明記しているとおり、**§0.2 から消えたのは「未決」という状態だけ**で、実装が済んだ意味ではない。

**改善の方向性**: 現状の分離（未決は §0.2、実装在庫は §3.2、記録は §4）は**正しい**。守るべきは「**この文書を第 4 のレジスタにしない**」ことである（だから §0 で帰属を名指ししている）。
**帰属**: **推奨で閉じられる**（運用規則）。

---

### M-4 【既知】`# type: ignore` 53 件が未検証 — `mypy` は宣言されているが走っていない　`P2`

**現状**: `mypy>=1.8` は `ai-server` / `browser-server` の dev 依存にあり両方の `uv.lock` にも入るが、**走らせるものがリポジトリに 1 つも無い**。既定設定で `python -m mypy src` は **317 errors / 94 files**。よって **53 件の `# type: ignore`（26 ファイル）が検証されない主張**になり、`--warn-unused-ignores` で **21 件は何も抑止していない**（`DELEGATION.md` §4 項目 18）。
**改善の方向性**: `ruff` が 994 → `--select F821` に絞ったのと同じ形で、**スコープを切って**ゲートに入れる。または宣言ごと外す。
**帰属**: **オーナー判断**（§4 項目 18）。

---

## 5. 拡張性を妨げる箇所

### X-1 【新規】第三者・利用者向けのプラグイン機構が無い　`P2`

**現状（測定）**: `ai-server/pyproject.toml` に `[project.scripts]` / `entry-points` は無い。`plugin` の語はソース中で**生成物のヘッダと docstring にしか現れない**。能力の拡張点は**マニフェスト**である: `CapabilityCatalog(capabilities_dir=str(base_dir / "capabilities"), ...)`（`runtime.py:862`）が `capabilities/` を走査し、現在 `capabilities/builtin/` 配下に **128 件**の JSON がある。つまり拡張 = 「`capabilities/<server>/<app>/<action>.json` を置き、その server プロトコルを実装する」こと。

**改善の方向性**: 拡張点を**文書化された契約**にする（利用者が置けるディレクトリ + ローダ + 検証）。`/api/capabilities/reload` は既に存在するので、再読み込みの口はある。第三者向けマーケットは §3.2 で ❌。
**帰属**: **オーナー判断**（§3.2 ❌ 群の一部）。

---

### X-2 【既知】拡張の語彙を担う `aliases` が未配線　`P2`

**現状**: `CapabilityManifest.aliases` は**第三者が自分の語彙で能力を見つけられるようにする**ための面だが、出荷 128 件で宣言 **0 件**（E-4 / `DELEGATION.md` §4 項目 15）。検索重みは最高（1.6）なのに生産者が居ない。
**改善の方向性**: alias を書く運用にする（＝拡張の入口を実際に使う）か、フィールドごと外す。
**帰属**: **オーナー判断**（§4 項目 15）。

---

### X-3 【既知】Room Server と Android 通知フィルタが未構成　`P2`

**現状**: Room Server は 503 / 403 / ハードコード fixture を返す未構成状態（`GetEnvironment` は fixture を "ok" と称していたのを注記で明示済み）。Android の通知フィルタ（OTP 規則）は移植されていない（`DELEGATION.md` §4 項目 5）。
**改善の方向性**: 実機/実環境の構成が前提。fixture の注記は済んでいるので、次の一歩は**構成**である。
**帰属**: **オーナー判断**（§3.2 / §4 項目 5）。

---

## 6. 優先度つき要約表

**優先度の定義**

- **P0** — 唯一の制約（目標）を直接妨げる
- **P1** — 文書化された契約が偽である / 宣伝された部分系が丸ごと不活性
- **P2** — 実在するリスク・非効率（影響範囲は限定的）
- **P3** — 衛生・多層防御（対応不要、または測定で反証済み）

| ID | 軸 | 問題 | 優先度 | 帰属 |
|---|---|---|---|---|
| **G-1** | 目標 | egress ゲートが「全拒否」のまま。許可を与えても外部に出せない | **P0** | オーナー判断 |
| **G-2** | 目標 | `TriggerEngine` / `Scheduler` / `EventView` が未構築。起動ログが偽を印字 | **P1** | オーナー判断（ログは即修正） |
| **G-3** | 目標 | `docs/testing.md` のテスト名 17 本が全部存在しない（写し 4 文書も） | **P1** | **修正済み**（ピン追加） |
| **G-4** | 目標 | §3.2 の ❌ 群の v1 範囲 | **P2** | オーナー判断 |
| **E-1** | 非効率 | 中核が死んでいるので全体がポーリング駆動 | **P1** | G-2 に従属 |
| **E-2** | 非効率 | ワーカー 10 に対し外向きタイムアウト最大 30 秒 | **P2** | 推奨で閉じられる |
| **E-3** | 非効率 | エージェント 1 ステップごとにスレッドプール生成 | **P2** | 推奨で閉じられる |
| **E-4** | 非効率 | 最高重みの `aliases` に生産者 0 件 | **P3** | オーナー判断 |
| **S-1** | セキュリティ | 既定の開発構成では認証ミドルウェアが載らない（意図的）。passkey 態の route 被覆の不変条件は無検査。文書が `0.0.0.0` を案内し認証状態を書かない | **P1** | 推奨で閉じられる |
| **S-2** | セキュリティ | 表示トークン規則が 2 箇所。片方は拒否分岐が到達不能 | **P2** | 推奨で閉じられる |
| **S-3** | セキュリティ | `security/` 未配線パッケージ（実測 9 クラス、記録は 6） | **P2** | オーナー判断（数値訂正は推奨） |
| **S-4** | セキュリティ | `_system_one` が呼び出し時にゲートを見ない（構築経路依存） | **P3** | 推奨で閉じられる |
| **S-5/6** | セキュリティ | 残る `urlopen` 2 箇所・秘密情報 — **反証済み** | **P3** | 対応不要 |
| **M-1** | 保守性 | 文書とソースの食い違いが 7 箇所以上 | **P1** | 推奨で閉じられる |
| **M-2** | 保守性 | 「宣言されているが効かない」が今も増加（新例 3 件） | **P1** | 推奨で閉じられる |
| **M-3** | 保守性 | レジスタが読めなくなっている（2114 行 / §0.2 空） | **P2** | 推奨で閉じられる |
| **M-4** | 保守性 | `# type: ignore` 53 件が未検証 | **P2** | オーナー判断 |
| **X-1** | 拡張性 | 第三者向けプラグイン機構が無い | **P2** | オーナー判断 |
| **X-2** | 拡張性 | 拡張の語彙 `aliases` が未配線 | **P2** | オーナー判断 |
| **X-3** | 拡張性 | Room Server / Android 通知フィルタが未構成 | **P2** | オーナー判断 |

**「推奨で閉じられる」= 9 件**（G-3, E-2, E-3, S-1, S-2, S-4, M-1, M-2, M-3）。残りは**オーナー判断**が前提。

---

## 7. この調査が測っていないこと（正直な限界）

- **実行時の挙動は測っていない。** すべて**ソースと文書の静的走査**である。`ai-server` を起動して観測した結果ではない（Docker デーモンは本環境で停止している）。
- **`web-ui` / `android-server` / `pc-server` / `browser-server` / `room-server` のソースは網羅していない。** 深く測ったのは `ai-server` である。他サーバーについては既存レジスタと `feature-catalog.md` の記載に依拠した。
- **「性能」は測っていない。** E-2 / E-3 は**構造からの推定**であり、プロファイルを取った結果ではない。負荷試験なしに「遅い」とは主張しない。
- **優先度は測定ではなく判断である。** 表の P 値は、この調査の著者が「目標にどれだけ効くか」で並べたもので、オーナーの順序を拘束しない。
- **被覆は主張である。** この文書が「コードベース全体から特定した」と言えるのは、**上に列挙した走査を実行した範囲**においてだけである。走査しなかった面に同種の欠陥が無いことは、**何も主張していない**。
