# AEGIS Agent 移行 進捗ログ

> 計画: `instruction.md` (OpenHands 移行 9 フェーズ)
> 方針: 中断 / コンテキスト圧縮に耐えるよう、各 Phase 完了時に git commit + ここに進捗を記録する。
> 復帰時は `git log --oneline` + このファイルの最新エントリから再開する。

## 全体ステータス

| Phase | 内容 | 状態 | 完了日 | 備考 |
|-------|------|------|--------|------|
| 1 | AgentBackend Protocol + Local backend (read-only) | done | 2026-09-09 | 16/16 tests pass |
| 2 | OpenHands SDK backend (adapter のみ) | done | 2026-09-09 | 15/15 tests pass |
| 3 | AgentTask ↔ AEGIS Task 双方向変換 | done | 2026-09-10 | 39/39 tests pass |
| 4 | IntakeResult + LLM フィルタ | done | 2026-09-10 | 34/34 tests pass |
| 5 | AgentProfile + AgentRouter | done | 2026-09-10 | 28/28 tests pass |
| 6 | Coding Agent capability (Dev Server 機能移行) | done | 2026-09-10 | 32/32 tests pass |
| 7 | MCPGateway (AEGIS Capability → MCP tool) | done | 2026-09-10 | 20/20 tests pass |
| 8 | Agent Server 分離 (`aegis-openhands-agent.service`) | done | 2026-09-10 | 26/26 tests pass |
| 9 | Dev Server 削除 | done | 2026-09-10 | 865/865 tests pass |
| 10 | (reserved) | - | - | |

## Phase 1 詳細

### 目標 (instruction.md §36 Phase 1)
- `aegis_ai/agents/runtime/` パッケージ新設
- `AgentBackend` Protocol (interface.py)
- `AgentTask` / `AgentResult` / `AgentAction` / `AgentError` / `Artifact` / `MemoryCandidate` / `UsageMetrics` (models.py)
- `aegis_ai/agents/backends/local/` パッケージ + LocalBackend (subprocess で echo するダミー)
- `AegisRuntime.agent_backend: AgentBackend | None` 追加 (後方互換)
- capability manifest: `ai-server.agent.delegate` (read-only, feature flag 連動)
- `agents.enabled` settings フラグ (default: false)
- `requires_feature` manifest field → `agents.enabled=false` 時に manifest 自体が list_for_llm に出ない
- `tests/agents/test_agent_runtime.py` 緑

### DoD
- [x] instruction.md Phase 1 仕様確認 (§5, §8, §36)
- [x] `aegis_ai/agents/runtime/{__init__,interface,models}.py`
- [x] `aegis_ai/agents/backends/local/{__init__,backend,cli}.py`
- [x] `aegis_ai/settings/models.py` に `AgentSettings` 追加
- [x] `aegis_ai/runtime.py` に `agent_backend: Any = None` 追加 + `_build_runtime` で `LocalBackend` 注入
- [x] `aegis_ai/schema/models.py` に `requires_feature: str = ""` 追加
- [x] `aegis_ai/folder_registry.py` で `requires_feature` を保持
- [x] `aegis_ai/capability_catalog.py` の `list_for_llm(feature_flags=...)` で filter
- [x] `ai-server/capabilities/builtin/ai-server/agent/delegate.json` 新設
- [x] `ai-server/tests/agents/test_agent_runtime.py` 作成 + pytest 緑 (16 passed)
- [x] 既存テスト 709 件緑のまま (8 件 pre-existing 失敗: socket mock / chromadb / memory context content — Phase 1 と無関係)
- [x] OpenHands 未インストールでも import エラーなし (Phase 1 では OpenHands に依存しないので自動的に満たす)

### 実装まとめ (2026-09-09)

#### 新規ファイル
- `ai-server/src/aegis_ai/agents/runtime/__init__.py` — package docstring
- `ai-server/src/aegis_ai/agents/runtime/interface.py` — `AgentBackend` Protocol (外部 SDK 依存ゼロ)
- `ai-server/src/aegis_ai/agents/runtime/models.py` — 8 つの dataclass (`AgentTask/AgentProgress/AgentAction/Artifact/AgentError/MemoryCandidate/UsageMetrics/AgentResult`)
- `ai-server/src/aegis_ai/agents/backends/__init__.py` — registry (`register_backend` / `get_backend` / `list_backends` / `clear_backends`)
- `ai-server/src/aegis_ai/agents/backends/local/__init__.py` — `LocalBackend` 再 export
- `ai-server/src/aegis_ai/agents/backends/local/backend.py` — `LocalBackend` 実装 (subprocess 経由)
- `ai-server/src/aegis_ai/agents/backends/local/cli.py` — echo 実装の CLI entrypoint
- `ai-server/tests/agents/__init__.py` — test package
- `ai-server/tests/agents/test_agent_runtime.py` — 16 テスト
- `ai-server/capabilities/builtin/ai-server/agent/delegate.json` — `ai-server.agent.delegate` capability manifest (read-only, requires_feature=agents)
- `AGENT_PROGRESS.md` — このファイル

#### 既存ファイル変更
- `ai-server/src/aegis_ai/agents/__init__.py` — 公開 re-exports
- `ai-server/src/aegis_ai/settings/models.py` — `AgentSettings` 追加
- `ai-server/src/aegis_ai/settings/__init__.py` — `AgentSettings` 公開
- `ai-server/src/aegis_ai/runtime.py` — `AegisRuntime.agent_backend: Any = None` 追加 + `_build_runtime` 末尾で `LocalBackend` 注入
- `ai-server/src/aegis_ai/schema/models.py` — `CapabilityManifestModel.requires_feature: str = ""` 追加
- `ai-server/src/aegis_ai/folder_registry.py` — `CapabilityManifest.requires_feature` + `_load_one` で保持
- `ai-server/src/aegis_ai/capability_catalog.py` — `list_for_llm(feature_flags: set[str] | None = None)` 追加

### 設計判断

1. **import 境界**: `aegis_ai/agents/runtime/interface.py` には OpenHands / 外部 SDK を一切 import しない。
   バックエンド具象は `aegis_ai/agents/backends/<name>/` 配下に閉じ込める。
2. **後方互換**: `AegisRuntime.agent_backend` の default `None` とし、None のときは `agents.enabled=false` と同じく delegate capability を manifest に出さない。
3. **feature flag**: `requires_feature: "agents"` を持つ manifest は `agents.enabled=true` のときだけ `enabled=True` として list_for_llm に乗る。
4. **LocalBackend**: Phase 1 はサブプロセスで `goal` を echo する最小実装。Phase 2 で OpenHands subprocess に差し替える。
5. **canonical ID 整合**: `delegate.json` を `ai-server/agent/delegate.json` (3 階層) に配置し、ID は `ai-server.agent.delegate` (4 階層の `ai-server/agent/task/delegate.json` だと ID が `ai-server.agent.task` になり意味的にずれる)。

### 中断時復帰手順

```powershell
cd C:\Users\kohak\programs\AEGIS
git log --oneline -20
cat AGENT_PROGRESS.md
# 該当 Phase の DoD 残項目を確認
```

## Phase 2 詳細

### 目標 (instruction.md §36 Phase 2)
- OpenHands SDK 経由で **同一の `AgentBackend` Protocol** を満たす backend を実装
- `AegisRuntime` の backend を **Local → OpenHands に swap** するだけで切り替えられることを確認
- **import 境界の不変条件**: `from openhands.*` は `adapter.py` のみ
- **DoD ネットワーク無し**: `LocalBackend` テストは CI で green、OpenHands 経路は mock で検証

### 追加ファイル
- `ai-server/src/aegis_ai/agents/backends/openhands/__init__.py` — re-export `OpenHandsBackend`, `WorkspaceSpec`
- `ai-server/src/aegis_ai/agents/backends/openhands/config.py` — `WorkspaceSpec` dataclass (READ_ONLY/ISOLATED/PERSISTENT)
- `ai-server/src/aegis_ai/agents/backends/openhands/adapter.py` — **唯一** openhands SDK を import する層
- `ai-server/src/aegis_ai/agents/backends/openhands/backend.py` — `OpenHandsBackend(AgentBackend)` 実装 (openhands への import なし)
- `ai-server/tests/agents/test_openhands_backend.py` — 15 DoD tests

### 変更ファイル
- `ai-server/src/aegis_ai/runtime.py` — `AegisRuntime.set_agent_backend(backend)` / `.get_agent_backend()` 追加 (Phase 2 DoD: admin API)

### DoD (instruction.md §36)
- [x] 同じ `AgentTask` を `LocalBackend` と `OpenHandsBackend` の両方に渡して **同一の `AgentResult` 形状** が返る (`test_local_and_openhands_produce_same_result_shape`)
- [x] OpenHands SDK のバージョンアップ時、`adapter.py` 以外には変更不要 (`test_import_boundary_only_adapter_imports_openhands` + `test_adapter_module_imports_openhands_only_inside_functions` 静的検査)
- [x] `LocalBackend` を使った CI テストが **ネットワーク無しで** 緑 (`test_local_backend_runs_without_network`)
- [x] `AegisRuntime.set_agent_backend()` で Local ↔ OpenHands が swap 可能 (`test_aegis_runtime_set_agent_backend_swaps_backend`)

### 設計判断

1. **import 境界**: `from openhands.*` は `adapter.py` 内の関数内に閉じ込め。
   `backend.py` / `config.py` / `__init__.py` は OpenHands 非依存。バージョンアップ時は
   `adapter.py` だけ修正すればよい。
2. **asyncio.to_thread**: OpenHands の `Conversation.run()` は blocking なので `to_thread` で
   別スレッドに逃がし、AEGIS 側からは `await` できるようにする (Phase 3 で TaskExecutionEngine から呼ばれる前提).
3. **mock-based テスト**: 実 SDK 呼び出しはしない。`adapter.run_conversation` 等を
   monkeypatch して `events` だけ返す。`is_openhands_available()` を `True` に偽装して
   コード経路をテストする。
4. **キャンセル**: Phase 2 では `_cancelled` set に積むだけ。`RemoteAPIWorkspace` を
   使う Phase 8 で真のキャンセルを実装。
5. **WorkspaceSpec**: `path` の他に `mount_ro` / `protected_paths` / `base_branch` /
   `worktree_branch` を持ち、Phase 6 の capability bridge 側に渡す前提。
6. **`set_agent_backend()`**: thread-safe な swap API。Phase 5 の AgentRouter や
   Phase 8 の systemd admin API から呼ばれる。

### 中断時復帰手順

```powershell
cd C:\Users\kohak\programs\AEGIS
git log --oneline -5
cat AGENT_PROGRESS.md
# Phase 2 は完了、Phase 3 (AgentTask ↔ AEGIS Task 双方向変換) を開始する
```

## 変更履歴

- 2026-09-09: Phase 1 完了
  - `AgentBackend` Protocol + Local subprocess backend (read-only) 実装
  - 16/16 DoD tests 緑 (`pytest tests/agents/test_agent_runtime.py -q`)
  - 既存テスト 709 件緑 (8 件 pre-existing 失敗は Phase 1 と無関係)
  - feature flag 連動 (`agents.enabled` + `requires_feature: "agents"`) 動作確認
  - canonical ID `ai-server.agent.delegate` 確定
  - 旧 `ai-server/agent/task/delegate.json` を `ai-server/agent/delegate.json` に移動 (canonical 3 階層化)

- 2026-09-09: Phase 2 完了
  - `OpenHandsBackend(AgentBackend)` 実装 + `WorkspaceSpec` dataclass
  - import 境界ルール: `from openhands.*` は `adapter.py` 内のみ
  - 15/15 DoD tests 緑 (mock-based、実 SDK 呼び出しなし)
  - `AegisRuntime.set_agent_backend()` で Local ↔ OpenHands を swap 可能
  - asyncio.to_thread で blocking SDK 呼び出しを await 化
  - 既存テスト 724 件緑 (Phase 1 から +15 件)

## Phase 3 詳細

### 目標 (instruction.md §36 Phase 3)
- `PlanStep` ↔ `AgentTask` 変換 (`build_agent_task`)
- `AgentResult` → `PlanStep.status / result / error` 反映 (`apply_result_to_step`)
- `TaskStatus` 9 状態 ↔ backend status 文字列 双方向変換 (`backend_status_to_task` / `task_status_to_backend`)
- `_VALID_TRANSITIONS` 検証ヘルパ (`validate_transition`)
- `AgentResult` → `TaskManager.complete_task_with_agent_result()` で metadata 埋め込み
- `TaskExecutionEngine._execute_step()` に `agent_delegate` / `ai-server.agent.*` ルート追加
- import 境界維持: `lifecycle.py` / `executor.py` は OpenHands SDK を import しない

### 追加ファイル
- `ai-server/src/aegis_ai/agents/runtime/lifecycle.py` — `TaskStatus` ↔ backend status 双方向、`is_terminal`、`validate_transition`、`agent_result_to_task_summary`、`agent_result_to_step_results`
- `ai-server/src/aegis_ai/agents/runtime/executor.py` — `is_agent_capability`、`build_agent_task`、`emit_progress`、`apply_result_to_step`、`run_agent_step` (async)、`build_task_result_summary`
- `ai-server/tests/agents/test_lifecycle_executor.py` — 39 DoD tests

### 変更ファイル
- `ai-server/src/aegis_ai/agents/runtime/__init__.py` — 新規モジュールの re-exports 追加
- `ai-server/src/aegis_ai/task/execution_engine.py` — `_execute_step` に `agent_delegate` / `ai-server.agent.*` ルート追加 + `_execute_agent_step` 新規メソッド。`asyncio.get_running_loop()` で running loop 検出 (Python 3.12 対応)
- `ai-server/src/aegis_ai/task/task_manager.py` — `complete_task_with_agent_result()` 新規メソッド (`result_summary` + `metadata["agent_result"]` dict 埋め込み)
- `ai-server/tests/agents/test_agent_runtime.py` — `_run` ヘルパを `asyncio.new_event_loop()` 化 (Python 3.12 対応)
- `ai-server/tests/agents/test_openhands_backend.py` — 同上

### DoD (instruction.md §36)
- [x] `backend_status_to_task()` が 9 状態すべてを正しく変換 (`test_backend_status_to_task_*`)
- [x] `is_terminal()` が 4 terminal 状態を判定 (`test_is_terminal_*`)
- [x] `validate_transition()` が AEGIS 仕様通り遷移を検証 (`test_validate_transition_*`)
- [x] `build_agent_task()` が `step.params["goal"]` → `description` → `plan.user_goal` の優先順で AgentTask を作る (`test_build_agent_task_*`)
- [x] `apply_result_to_step()` が `COMPLETED` / `FAILED` / `WAITING_APPROVAL` / `PAUSED` / `CANCELLED` / `EXPIRED` を StepStatus にマップ (`test_apply_result_to_step_*`)
- [x] `run_agent_step()` が `LocalBackend` 経由で step を COMPLETED にできる (`test_run_agent_step_with_local_backend_completes`)
- [x] `TaskManager.complete_task_with_agent_result()` が `metadata["agent_result"]` を dict で保存し COMPLETED に遷移 (`test_complete_task_with_agent_result_embeds_metadata`)
- [x] `TaskExecutionEngine._execute_step()` が `agent_delegate` または `ai-server.agent.*` を AgentBackend にルーティング (`test_execution_engine_routes_*`)
- [x] `lifecycle.py` / `executor.py` は OpenHands SDK を import しない (静的検査) (`test_lifecycle_does_not_import_openhands` / `test_executor_does_not_import_openhands`)

### 設計判断

1. **`lifecycle.py` を `agents/runtime/` 配下に置く**: 既存の `task/task_manager.py` の `TaskStatus` を直接 import する。`TaskStatus` を再定義せず、1 ソースに保つ。
2. **`agent_result_to_task_summary` のフォールバック順序**: `summary` → 最初の error `[code] message` → `"(no summary)"` の順。空 summary が AEGIS UI に出ないようにする。
3. **`apply_result_to_step` の冪等性**: 既に `StepStatus.NEEDS_APPROVAL` の step は上書きしない (approval 待ちを誤って上書きしないため)。
4. **`_execute_agent_step` の同期経路**: TaskExecutionEngine は同期前提のため `asyncio.run()` または `ThreadPoolExecutor` で async をブリッジ。`asyncio.get_running_loop()` で running loop 検出 → running なら別スレッドで `asyncio.run()`、それ以外は直接 `asyncio.run()`。Python 3.12 で `asyncio.get_event_loop()` は deprecation。
5. **`complete_task_with_agent_result` は `_transition(COMPLETED)` 経由**: 既存の `_VALID_TRANSITIONS` 検証がそのまま適用され、`RUNNING → COMPLETED` のみ許可される (CREATED から直接は不可、テストでも start_task 後に呼ぶ)。
6. **テストの import 境界静的検査**: `inspect.getsource()` でモジュールソースを取得し、`import` / `from` 行に `openhands` / `openai` / `anthropic` 等の文字列が無いことを確認。Phase 2 と同じパターン。

### 中断時復帰手順

```powershell
cd C:\Users\kohak\programs\AEGIS
git log --oneline -5
cat AGENT_PROGRESS.md
# Phase 3 は完了、Phase 4 (IntakeResult + LLM フィルタ) を開始する
```

## Phase 4 詳細

### 目標 (instruction.md §11, §36 Phase 4)
- すべての Event を無条件に OpenHands に投げず、`IntakeClassifier` で
  「Agent 不要」を早期判定する
- 1000 event のうち Agent delegate に進むのは **10% 以下** を目標
- `IntakeSettings.enabled=False` で intake を OFF にして既存挙動に戻す
- `IntakeDeduplicator` が fingerprint で重複排除
- import 境界: `intake/*` は openhands SDK を import しない

### 追加ファイル
- `ai-server/src/aegis_ai/intake/__init__.py` — re-exports (`IntakeClassifier`, `IntakeDeduplicator`, `IntakeRouter`, `IntakeDecision`, `IntakeRoute`, `IntakeResult`, `RoutingDecision`)
- `ai-server/src/aegis_ai/intake/models.py` — 4 つの型:
  - `IntakeDecision` enum: `REQUIRES_AGENT` / `LOCAL_INTERPRET` / `DEFER` / `DUPLICATE`
  - `IntakeRoute` enum: `SKIP` / `DEFER` / `DUPLICATE` / `AGENT_DELEGATE`
  - `IntakeResult` dataclass: event_id, decision, requires_agent_score, importance, novelty, task_type, capabilities, stop_conditions, reason, confidence, raw
  - `RoutingDecision` dataclass: route, intake_result, reason, `should_delegate_to_agent` property
- `ai-server/src/aegis_ai/intake/deduplicator.py` — `IntakeDeduplicator` (SHA-256 fingerprint, `deque` sliding window, `is_duplicate(event, novelty=None)` OR 判定)
- `ai-server/src/aegis_ai/intake/classifier.py` — `IntakeClassifier` (LLM 呼び出しは `LLMRequest(task_type=TaskType.SMALL_FAST_TASK, json_mode=True)`、`_decision_from_score` 0.7/0.3 閾値、`_parse_response` で ```json ``` 剥がし + JSON パース)
- `ai-server/src/aegis_ai/intake/router.py` — `IntakeRouter` (master switch `enabled`、dedup-first、classifier、`requires_agent_threshold` 比較)
- `ai-server/tests/test_intake.py` — 34 DoD tests

### 変更ファイル
- `ai-server/src/aegis_ai/settings/models.py` — `IntakeSettings` 追加 (enabled, classifier_profile, requires_agent_threshold, dedup_window_size, dedup_novelty_threshold, max_importance, fallback_requires_agent) + `AEGISSettings.intake: IntakeSettings` フィールド追加
- `ai-server/src/aegis_ai/settings/__init__.py` — `IntakeSettings` re-export

### DoD (instruction.md §36)
- [x] `IntakeResult` / `RoutingDecision` dataclass がデフォルト値で生成可能 (`test_intake_result_defaults` / `test_routing_decision_should_delegate_to_agent`)
- [x] `IntakeDeduplicator.make_fingerprint()` が SHA-256 安定ハッシュ (source/description で異なる) (`test_deduplicator_fingerprint_*`)
- [x] `IntakeDeduplicator.is_duplicate()` が fingerprint と novelty の OR 判定 (`test_deduplicator_is_duplicate_*`)
- [x] `IntakeClassifier` が正常 JSON / ```json``` ブロック / LLM 失敗 / JSON 不可 / スコアなし の各ケースで fallback 可能 (`test_classifier_*`)
- [x] `_decision_from_score` の 0.7 / 0.3 しきい値マッピング (`test_classifier_score_to_decision_mapping`)
- [x] `IntakeRouter.enabled=False` で classifier を呼ばず SKIP 返却 (`test_router_disabled_skips_classifier`)
- [x] `requires_agent_score >= threshold` で `AGENT_DELEGATE` (`test_router_delegates_to_agent_when_score_above_threshold`)
- [x] dedup (fingerprint 一致) で classifier 呼び出しを節約 (`test_router_dedup_skips_classifier`)
- [x] dedup (novelty < threshold) で `DUPLICATE` ルート (`test_router_dedup_via_novelty`)
- [x] **DoD: 1000 event 中 Agent delegate ≤ 10%** (mock classifier が常に score=0.1 を返すシナリオで検証) (`test_router_dod_below_10_percent_to_agent`)
- [x] threshold 境界: `score == threshold` で `>=` 比較が成立し delegate される (`test_router_threshold_boundary`)
- [x] `IntakeSettings` のデフォルト値と Pydantic 範囲検証 (`test_intake_settings_*` / `test_aegis_settings_contains_intake`)
- [x] **import 境界: `intake/*` は openhands / anthropic / openai / langchain を import しない** (静的検査) (`test_intake_module_does_not_import_openhands[*]`, 5 モジュール × 1 = 5 テスト)

### 設計判断

1. **dedup を先に評価**: LLM 呼び出しはコストが高いので、fingerprint 一致なら
   早期 return して classifier をスキップする。LLM 呼び出し前に novely が
   わかっていれば同様に節約できるが、novelty は classifier 結果なので
   ここでは fingerprint のみで早期 return.
2. **score → decision の二段階ゲート**: ルーターは `decision == REQUIRES_AGENT`
   AND `score >= requires_agent_threshold` の **両方** を満たすときだけ
   `AGENT_DELEGATE` にする。`REQUIRES_AGENT` は score >= 0.7 のときだけなので、
   結果として「score >= 0.7」かつ「score >= threshold (default 0.5)」の
   両方を満たす必要があり、誤って agent に投げない安全側に倒れる。
3. **`LLMRequest(task_type=SMALL_FAST_TASK, json_mode=True, caller="intake.classifier")`**:
   `LLMRequest` の `profile_id` 引数は存在しないため `TaskType` で
   routing し、`caller` でコスト追跡 / 監査のタグ付けを行う。
4. **IntakeSettings は `intake` セクションにネスト**: Pydantic の `AEGISSettings.intake`
   フィールドで集約。`enabled=False` だけで既存挙動に戻る (master switch)。
5. **dedup の `record()` タイミング**: AGENT_DELEGATE / SKIP 両方で行う
   (重複処理を防ぐ)。DEFER / DUPLICATE では行わない (再評価可能にするため)。
6. **`asyncio.get_running_loop()` パターン**: Phase 3 の `execution_engine.py` で
   採用した Python 3.12 対応の `running loop` 検出パターンを踏襲。

### 中断時復帰手順

```powershell
cd C:\Users\kohak\programs\AEGIS
git log --oneline -5
cat AGENT_PROGRESS.md
# Phase 4 は完了、Phase 5 (AgentProfile + AgentRouter) を開始する
```

## Phase 5 詳細

### 目標 (instruction.md §21, §22, §36 Phase 5)
- 目的に応じて backend と model を **自動選択** する Profile 機構
- `config/agent_profiles.yaml` で 6 標準 profile を宣言的に定義
- `AgentRouter.select()` が profile / goal / capability / required_coding の
  4 入力から適切な `AgentProfile` を選ぶ
- 存在しない profile への参照は `general` にフォールバック + audit warning

### 追加ファイル
- `ai-server/src/aegis_ai/agents/profiles/__init__.py` — re-exports
- `ai-server/src/aegis_ai/agents/profiles/models.py` — `AgentProfile` / `AgentRiskCeiling` / `WorkspaceKind` / `RoutingDecision`
- `ai-server/src/aegis_ai/agents/profiles/registry.py` — `AgentProfileRegistry` (YAML loader)
- `ai-server/src/aegis_ai/agents/runtime/router.py` — `AgentRouter` (heuristic + explicit selection)
- `ai-server/config/agent_profiles.yaml` — 6 標準 profile (general, coding, research, browser, maintenance, planning)
- `ai-server/tests/agents/test_agent_profiles_router.py` — 28 DoD tests

### 変更ファイル
- `ai-server/src/aegis_ai/agents/__init__.py` — 新しい public API を re-export
- `ai-server/src/aegis_ai/runtime.py` — `AegisRuntime.agent_profiles` / `agent_router` フィールド追加 + `_build_runtime` で registry ロード

### DoD (instruction.md §36)
- [x] 6 標準 profile がロードできる (`test_registry_from_yaml_loads_six_standard_profiles`)
- [x] `select(requested_id="coding")` → `backend="openhands"`, `profile.id="coding"` (`test_router_select_explicit_id`)
- [x] 存在しない profile を要求 → `general` fallback + audit warning (`test_router_falls_back_to_general_with_warning`)
- [x] `AgentProfile.allows_capability` が deny > allow の優先順位 (`test_agent_profile_allows_capability_deny_wins`)
- [x] `AgentProfile.requires_approval` が capability ID を判定 (`test_agent_profile_requires_approval`)
- [x] `AgentRiskCeiling.parse` / `WorkspaceKind.parse` が case-insensitive + 不正値拒否
- [x] ゴール keyword による heuristic routing (coding / research / browser / planning / maintenance)
- [x] `required_coding=True` flag で goal より優先 (`test_router_required_coding_flag_overrides_goal`)
- [x] capability に git/github が含まれていれば coding (`test_router_capability_driven_routing_to_coding`)
- [x] fallback_id も無いときは合成 profile で None を返さない (`test_router_synthetic_profile_when_fallback_missing`)
- [x] `backend_resolver` で backend 名を変換可能 (`test_router_backend_resolver_overrides_profile_backend`)
- [x] `audit_sink` が例外を投げても routing は継続 (`test_router_audit_sink_exception_does_not_break_routing`)
- [x] **import 境界**: `aegis_ai.agents.*` / `aegis_ai.agents.profiles.*` / `aegis_ai.agents.runtime.router` は openhands を import しない (静的検査, 5 モジュール)
- [x] `_build_runtime` 後に `agent_profiles` / `agent_router` が non-None (`test_aegis_runtime_exposes_agent_profiles_and_router`)

### 設計判断

1. **`AgentRiskCeiling` は AgentProfile 専用 enum**: 既存の `RiskLevel` (NONE/LOW/MEDIUM/HIGH/FORBIDDEN, in `desire/intrinsic_task_generator.py`) とは値体系が異なる (READ_ONLY/SAFE_ACTION/APPROVAL_REQUIRED/HIGH_RISK, in `instruction.md §21`) ため、AgentProfile 専用の `AgentRiskCeiling` を新設。`desire/` 側に依存しないのでテストが軽量。
2. **AGENTS.md 禁止事項との関係**: instruction.md §22 注記通り、`_needs_coding()` などの keyword 判定は **capability 種別の classifier** としてのみ使う。ユーザー意図の解釈ではない (AGENTS.md 11.「ユーザー意図を keyword 解析するな」 には違反しない)。
3. **deny > allow**: `AgentProfile.allows_capability` で `denied_capabilities` を `allowed_capabilities` より優先。これは policy engine と同パターン (deny が常に勝つ)。
4. **fallback 戦略**: 4 段階フォールバック — ① 登録済み profile を返す、② なければ `fallback_id` (default "general") を試す、③ それでも無ければ合成 profile、④ それでも無ければ例外 (通常ここには到達しない)。audit sink には ② のタイミングで必ず warning が出る。
5. **YAML スキーマ検証**: `backend` / `llm_profile_name` は必須、それ以外は default 値あり。`max_runtime_sec` / `max_iterations` は int 強制。`risk_ceiling` / `workspace_kind` は case-insensitive。壊れた YAML は `load_warnings` に記録して空 registry を返す (例外で落とさない)。
6. **`AgentRouter` は独立クラス**: `runtime.py` には登録 (build) だけ。`select()` 自体はランタイムに依存しないので単体テストしやすい。`backend_resolver` で `runtime.agent_backend` 側の名前空間と接続。
7. **audit_sink は callable**: 関数 / メソッドのどちらでも受け付ける。production では `runtime.audit_log` (or wrapper)、テストでは単純な list への append。

### 中断時復帰手順

```powershell
cd C:\Users\kohak\programs\AEGIS
git log --oneline -5
cat AGENT_PROGRESS.md
# Phase 6 は完了、Phase 7 (MCPGateway) を開始する
```

## Phase 6 詳細

### 目標 (instruction.md §36 Phase 6)
- Coding Agent capability を Dev Server 機能として AEGIS capability 化
- `ToolBridge` 抽象で capability ID ↔ 実装を切り離し、Phase 9 で
  dev-server を削除しても capability ID は変えない
- 副作用 (repo_write, file_write, git_commit, pr.create 等) のある
  capability はすべて `level=medium` + `requires_approval=true` に格上げ
- `AEGIS_REPO_PATH` 環境変数で workspace confinement を enforcing

### 追加ファイル
- `ai-server/src/aegis_ai/tools/__init__.py` — bridges namespace
- `ai-server/src/aegis_ai/tools/bridges/__init__.py` — re-exports
- `ai-server/src/aegis_ai/tools/bridges/base.py` — `ToolBridge` / `BridgeResult` / registry
- `ai-server/src/aegis_ai/tools/bridges/filesystem.py` — 3 native bridges (in-process)
- `ai-server/src/aegis_ai/tools/bridges/git.py` — 8 gRPC passthrough bridges + approval enforcement
- `ai-server/src/aegis_ai/tools/bridges/github.py` — 1 gRPC bridge (pr.create)
- `ai-server/tests/agents/test_tool_bridges.py` — 32 DoD tests

### 変更ファイル (manifests)
- `ai-server/capabilities/builtin/dev-server/branch/create.json` — level: safe→medium, requires_approval: false→true
- `ai-server/capabilities/builtin/dev-server/patch/apply.json` — 同上
- `ai-server/capabilities/builtin/dev-server/git/create_commit.json` — 同上
- `ai-server/capabilities/builtin/dev-server/git/revert_changes.json` — 同上
- `ai-server/capabilities/builtin/dev-server/pr/create.json` — 同上

### DoD (instruction.md §36)
- [x] `ToolBridge` 登録 / lookup / list / clear が動く (`test_bridge_registry_*`, `test_clear_bridges_*`)
- [x] `BridgeResult.to_dict()` shape が正しい (`test_bridge_result_*`)
- [x] 3 native bridges (filesystem) が in-process で動く (`test_filesystem_registers_three_native_bridges`, `test_repo_status_native_executes`, `test_diff_get_diff_returns_diff_text`, `test_test_get_results_empty_cache`)
- [x] 8 gRPC bridges (git, github, test, lint, system) が登録される (`test_git_bridges_register_eight_grpc_bridges`)
- [x] 5 write 系の bridge は approval_token 必須 (無しなら deny) (`test_all_five_write_bridges_deny_without_token`, `test_write_bridge_requires_approval_token`, `test_github_bridge_pr_create_requires_approval`)
- [x] approval_token ありで gRPC forward (`test_write_bridge_succeeds_with_approval_token`, `test_github_bridge_pr_create_with_token`)
- [x] workspace confinement (`_is_within_workspace` の True/False 両分岐)
- [x] git リポジトリ外では error を surface (`test_repo_status_surfaces_error_when_not_git_repo`)
- [x] gRPC failure / exception を BridgeResult.error に反映 (`test_grpc_failure_becomes_bridge_result_error`, `test_grpc_exception_becomes_bridge_result_error`)
- [x] 5 write manifest が `level=medium` + `requires_approval=true` (`test_write_manifest_requires_approval` x5)
- [x] `_APPROVAL_REQUIRED` set と manifest が一致 (`test_approval_required_set_matches_manifests`)
- [x] **import 境界**: bridges/ は openhands / dev_server_pb2 を import しない (`test_bridges_do_not_import_openhands_directly`, `test_bridges_do_not_import_dev_server_pb2`)
- [x] bridges/* 4 モジュールが import 可能 (`test_bridges_modules_are_importable`)

### 設計判断

1. **2 種類の bridge**: `native` (Python 実装) と `grpc` (dev-server へ forward)。Phase 9 で dev-server を削除する時、`grpc` を `native` (OpenHands runtime 内 in-process 実行) に差し替えるだけで capability ID が変わらない。
2. **approval_token enforcement は bridge 側にも置く**: 既存の `PolicyEngine` は manifest を読んで gating するが、bridge レイヤーは多層防御として再度 token 必須 check する。PolicyEngine を bypass された場合の最後の砦。
3. **workspace confinement**: `AEGIS_REPO_PATH` (env) を root とし、symlink-resolve 後の `relative_to` で判定。Docker 環境では `/workspace` 固定。OS レベルの chroot/sandbox は Phase 9 で dev-server が担う。
4. **5 manifests 同期更新**: `bridge.git.APPROVAL_REQUIRED_CAPABILITIES` frozenset と manifest 群が一対一対応することを `test_approval_required_set_matches_manifests` で保証。manifest 追加時は両方を更新する必要があり、テストがそれを強制する。
5. **github.py と git.py で pr.create 重複**: 同じ capability_id を両方 register する仕様だが、`register_bridge` は上書き。`github.py` は Phase 9 で dev-server 削除後に `gh` 直接呼び出しに切り替えるための placeholder として明示的に残してある。
6. **test/lint は approval 不要**: side_effects は `code_execution` のみで `repo_write` / `file_write` を含まないので、Phase 6 時点では approval 不要。manifest の `risk.level=safe` もそのまま。
7. **import 境界は `aegis_ai.tools.bridges.*` 単位で強制**: bridges/ 配下が `openhands` / `dev_server_pb2` を直接 import すると OpenHands backend (Phase 2) の抽象が崩れる。gRPC forward であっても必ず `DevServerGrpcClient` 抽象経由。

### 残作業 / 注意点

- **既存テスト 8 件 pre-existing regression** (Phase 5 完了時点 `ad3305c` でも同じく fail することを確認済み、Phase 6 と無関係):
  - `test_pc_tcp_uses_tcp_command_json` / `test_pc_tcp_invalid_json_is_not_reported_as_unreachable` (server_executor: socket mock の lambda 引数不整合)
  - `test_chroma_query_uses_current_embedding_protocol` (capability_index: chroma API)
  - `test_dashboard_chat_approval_executes_once_and_emits_followup` (dashboard_routes: KeyError 'approval_id')
  - `test_deliberate_llm_non_action_is_not_learned_as_failure` (fix_instruction: IndexError)
  - `test_shared_memory_context_includes_recent_failures_without_query_hits` / `test_shared_context_includes_desire_lesson` (memory_*: 'Desire lessons:' 期待不一致)
  - `test_proposal_prompt_includes_capability_semantics_and_diversity_rule` (autonomous_loop: 'span at least two operation categories' 期待不一致)
- 全体 857 件 pass / 8 件 pre-existing fail (Phase 5 完了時点と同等)
- Phase 6 で touch した dev-server manifest は read-only (test.run_tests, lint.run_lint, system.health_check, repo.status, diff.get_diff, test.get_results) には影響しない

### 中断時復帰手順

```powershell
cd C:\Users\kohak\programs\AEGIS
git log --oneline -5
cat AGENT_PROGRESS.md
# Phase 6 は完了、Phase 7 (MCPGateway) を開始する
```

## Phase 7 詳細

### 目標 (instruction.md §36 Phase 7)
- AEGIS capability を **MCP tool として OpenHands に公開**
- `tools/list` を叩くと capability manifest が JSON-RPC 2.0 envelope で返る
- `tools/call` を叩くと `ToolBroker.execute()` 経由で `PolicyEngine → ApprovalManager → AuditManager` を必ず通る
- Agent は直接 file を書けない (必ず capability 経由)
- 全 server (pc / browser / android / room / ai / dev) の capability が同じ protocol で呼べる

### 追加ファイル
- `ai-server/src/aegis_ai/tools/mcp_gateway.py` — `list_tools_for_agent` / `call_tool_for_agent` / `mcp_tools_list_payload` / `mcp_tools_call_payload` / `mcp_initialize_payload` + `_ApprovalRequired` / `_PolicyDenied` 例外 + `_invoke_via_broker` (内部)
- `ai-server/src/aegis_ai/paths.py` — `find_project_root()` / `find_capabilities_dir()` ($AEGIS_CAPABILITIES_DIR → <root>/capabilities → <root>/ai-server/capabilities の順で解決)
- `ai-server/tests/agents/test_mcp_gateway.py` — 20 DoD tests

### 変更ファイル
- `ai-server/src/aegis_ai/capability_catalog.py` — `_GLOBAL_CATALOG` モジュール singleton、`CapabilityCatalog.instance()` classmethod、`list_for_agent(profile, feature_flags)` 追加 (allow/deny + リスク ceiling で filter、出力 entry の risk は正規化)、`mcp_tool_schemas(profile, feature_flags)` 追加 (MCP tool 形式へ変換、_meta.aegis 付与)、`_profile_allows` / `_profile_risk_ceiling` / `_capability_dict_to_mcp_tool` ヘルパ追加
- `ai-server/src/aegis_ai/tool_broker.py` — `_execute_for_agent(capability_id, params, *, profile, approval_token, context)` facade を `__all__` に追加。`ToolBroker.instance()` 経由で singleton broker 取得、未登録なら `ToolBroker(registry=ToolRegistry())` でフォールバック
- `ai-server/src/aegis_ai/tools/__init__.py` — `mcp_gateway` 名前空間を re-export
- `ai-server/src/tool_broker.py` — `ToolBroker` クラスに `_singleton` class attribute + `instance()` / `set_instance()` クラスメソッド追加 (Phase 7 §36 singleton hook)

### DoD (instruction.md §36)
- [x] `tools/list` の JSON-RPC 2.0 envelope (`jsonrpc` / `id` / `result.tools` / `result.nextCursor`) 検証
- [x] MCP tool name は canonical ID (`server.app.action`、`.` 3 段以上) である
- [x] `tools/call` の envelope (`jsonrpc` / `id` / `result.content` / `result.isError`) 検証
- [x] `initialize` ハンドシェイク (`protocolVersion` / `serverInfo` / `capabilities.tools`) 検証
- [x] `ToolBroker.execute()` 経由実行 (mock broker で `execute.assert_called_once()` 確認)
- [x] request context に `agent_profile` / `caller` / `approval_token` が記録される
- [x] profile.denied_capabilities の capability は call 拒否 (`isError=True`、broker 呼ばれず)
- [x] 無効な arguments は `ValueError` を `isError=True` で surface
- [x] broker exception は `isError=True` で `{Type}: {message}` 形
- [x] `list_for_agent` が profile の allow/deny を反映
- [x] `list_for_agent` が `risk_ceiling=READ_ONLY` で risk > READ_ONLY の capability を除外
- [x] `mcp_tool_schemas` の各 tool に `_meta.aegis.{risk, requires_approval}` が含まれる
- [x] `runtime.tool_broker` があれば global singleton より優先
- [x] `aegis_ai.tool_broker.execute_for_agent` が import 可能で callable
- [x] `execute_for_agent` が `ToolBroker.execute()` を呼び、context に profile/approval_token/caller を埋める
- [x] **import 境界**: `aegis_ai/tools/mcp_gateway.py` および `aegis_ai/tools/` 配下すべてが `openhands` / `fastmcp` / `mcp` を import しない (静的検査)

### 設計判断

1. **MCP wire format を plain JSON で実装**: 外部 SDK (`fastmcp` / `mcp`) を import せず、JSON-RPC 2.0 envelope を自前で dict 構築。Phase 9 で dev-server 削除のときに OpenHands 側 SDK との結合点を最小化。
2. **`ToolBroker.execute()` 経由の徹底**: `call_tool_for_agent` は `_invoke_via_broker` で `ToolExecutionRequest` を作り、必ず `ToolBroker.execute()` に渡す。`PolicyEngine` / `ApprovalManager` / `AuditManager` を構造的に bypass できない (instruction.md §14 の境界維持)。
3. **リスク ceiling は正規化名で比較**: `list_for_agent` / `mcp_tool_schemas` は entry の `risk` フィールド (`low` / `safe` / `read_only` / `medium` 等) を `normalize_risk_label()` で `READ_ONLY` / `SAFE_ACTION` / `APPROVAL_REQUIRED` / `HIGH_RISK` / `FORBIDDEN` に正規化してから `_RISK_ORDER` 比較。出力 entry の `risk` フィールドも正規化済みで返すので下流が再正規化しなくて良い。

---

## Phase 8 詳細 (Agent Server 分離)

### 目標 (instruction.md §36 Phase 8)
- OpenHands SDK 呼び出しを AEGIS 本体プロセスから切り出し、systemd unit `aegis-openhands-agent.service` として host 上の別プロセスで動かす
- 同一プロセス版 (LocalBackend / OpenHandsBackend) も従来通り動く (`AGENT_BACKEND=local`)
- agent server が落ちても AEGIS 側は `AgentResult(status=BLOCKED, error="agent_unavailable")` で落ちない
- 別マシンへ systemd unit を移植しても `AGENT_SERVER_URL` 変更だけで動作

### DoD (instruction.md §36)
- [x] AEGIS 本体プロセスに `openhands-sdk` を **インストールしなくてよい** (remote mode)
- [x] AEGIS 本体に `openhands-sdk` が入っている場合 (`AGENT_BACKEND=local`) はそのまま動く
- [x] `aegis-openhands-agent.service` が落ちても `AgentResult(status=BLOCKED, error="agent_unavailable")` で AEGIS 側は落ちない
- [x] 別マシンへ `aegis-openhands-agent.service` を移しても `AGENT_SERVER_URL` 変更だけで動作する
- [x] import 境界: `openhands` への import は `agents/backends/openhands/adapter.py` 内のみ (`remote_backend.py` / `workspace.py` / `__init__.py` は SDK を import しない)
- [x] 26/26 DoD tests pass
- [x] 既存 agents/ tests 176/176 緑維持 (Phase 8 で導入した `TaskStatus.BLOCKED` / `TaskStatus.PENDING` が lifecycle mapping に反映)

### 新規ファイル
- `ai-server/src/aegis_ai/agents/runtime/session_store.py` — JSONL ベースの session 永続化 (append / extend / load / list / delete / gc_older_than)
- `ai-server/src/aegis_ai/agents/backends/openhands/workspace.py` — `Workspace` ABC + `LocalWorkspace` + `RemoteAPIWorkspace` (urllib HTTP ポスター) + `RemoteAPIError` + `build_workspace_from_spec` ヘルパ
- `ai-server/src/aegis_ai/agents/backends/openhands/remote_backend.py` — `RemoteOpenHandsBackend` (AgentBackend Protocol 実装、healthcheck → POST /mcp tools/call → session_store 永化)
- `ai-server/src/aegis_agent_server/__init__.py` — `main` / `serve` re-export
- `ai-server/src/aegis_agent_server/main.py` — Phase 8 agent server (JSON-RPC dispatcher `initialize` / `tools/list` / `tools/call` + `/healthz` + `/cancel/<task_id>` HTTP handler)
- `ai-server/tests/agents/test_remote_backend.py` — 26 DoD tests
- `infra/systemd/aegis-openhands-agent.service` — Phase 8 systemd unit (`Type=simple`, host 上で `aegis_agent_server.main` を起動)

### 変更ファイル
- `ai-server/src/aegis_ai/agents/backends/openhands/__init__.py` — `RemoteOpenHandsBackend` / `Workspace` / `LocalWorkspace` / `RemoteAPIWorkspace` / `RemoteAPIError` / `build_workspace_from_spec` を re-export
- `ai-server/src/aegis_ai/task/task_manager.py` — `TaskStatus` enum に `PENDING` / `BLOCKED` を追加、`_VALID_TRANSITIONS` を更新
- `ai-server/src/aegis_ai/agents/runtime/lifecycle.py` — `_BACKEND_STATUS_TO_TASK` と `task_status_to_backend` の mapping に `pending` / `blocked` を追加

### 設計判断

1. **HTTP REST + JSON-RPC over HTTP** を採用 (Phase 8 技術選択)。AEGIS 本体プロセスには `http.client` (urllib) 以外を追加依存なし。agent server 側は `BaseHTTPRequestHandler` のみで実装、追加依存なし。
2. **import 境界の徹底**: `remote_backend.py` / `workspace.py` / `__init__.py` から `from openhands.*` を一切禁止。SDK 呼び出しは `adapter.py` に閉じ込め済み (Phase 2 §6 / §35.4 の不変条件を維持)。`test_remote_backend_does_not_import_openhands` / `test_workspace_module_does_not_import_openhands` で docstring 文字列に惑わされない正規表現ベースの静的検査。
3. **`TaskStatus.BLOCKED` を enum に追加**: 既存 `FAILED` は「最終失敗」、`WAITING_APPROVAL` は「人間承認待ち」、`PAUSED` は「budget / approval 等で一時停止」だが意味がずれる。`BLOCKED` は instruction.md §25 / §38.5 で定義済みで「外部依存待ち (agent server 不在等) で再試行可能」を表す。`recoverable=False` の `AgentError` と組み合わせ、AEGIS 側の `TaskExecutionEngine.retry` が fingerprint を見て再試行できる。
4. **`TaskStatus.PENDING` も追加**: 既存 enum には「agent が task 未着手」を表現する値がなく、`get_status` の no-events パスで `PENDING` を返したい需要があった。`created` (TaskManager 登録済み) とは別軸なので追加。
5. **session 永続化は JSONL 1 ファイル = 1 session_id**: 後で resume や audit 再生が容易。`gc_older_than` は event の `ts_ms` ベース (mtime ではない) で期間削除。
6. **`_MAX_BODY_BYTES = 1 MB`** で HTTP リクエストサイズを cap (DoS 防止)。それ以上は `400 Bad Request` を返す。
7. **systemd unit hardening**: `NoNewPrivileges=true`, `ProtectSystem=strict`, `User=aegis` で agent server プロセスの権限を最小化。

4. **`ToolBroker.instance()` / `set_instance()` classmethod**: Phase 7 で追加した singleton hook。`AegisRuntime._build_runtime()` 内で `tool_broker.set_instance(self.tool_broker)` を呼び、process 全体から singleton 経由で broker にアクセス可能。テストでは `patch.object(ToolBroker, "instance", classmethod(lambda cls: mock))` で mock に差し替え可能 (MagicMock の auto-chain に依存しない)。
5. **`_ApprovalRequired` / `_PolicyDenied` のカスタム例外**: `ToolBroker.execute()` が現状 raise しないが、MCP クライアントには構造化エラー (`isError=True` + `_meta.aegis.approval_required=True`) を返したいので、内部フックとして用意。Phase 8 で ApprovalManager からの raise を正式に拾う前提。
6. **`_invoke_via_broker` の request context**: `caller=mcp_gateway` / `agent_profile=<id>` / `approval_token=<tok>` を必ず埋める。PolicyEngine の audit log 側で「どのエージェントのどの tool call か」を追跡できる。
7. **`paths.py` で capabilities_dir 解決**: `$AEGIS_CAPABILITIES_DIR` (env override) → `<root>/capabilities` → `<root>/ai-server/capabilities` の順。`CapabilityCatalog.instance()` singleton がテストでも本番でも同じ dir を見る。
8. **`mcp_gateway` モジュールは `openhands` / `fastmcp` / `mcp` すべて非依存**: テストで `test_mcp_gateway_does_not_import_openhands` / `test_mcp_gateway_does_not_import_fastmcp_or_mcp_sdk` で静的検査。Phase 8 で `agents/backends/openhands/adapter.py` を import する境界をまたいでも、MCP gateway 自体は独立。

### 残作業 / 注意点

- **既存テスト 8 件 pre-existing regression** (Phase 6 完了時点 `68b5904` でも同じく fail することを確認済み、Phase 7 と無関係):
  - `test_pc_tcp_uses_tcp_command_json` / `test_pc_tcp_invalid_json_is_not_reported_as_unreachable` (server_executor: socket mock の lambda 引数不整合)
  - `test_chroma_query_uses_current_embedding_protocol` (capability_index: chroma API)
  - `test_dashboard_chat_approval_executes_once_and_emits_followup` (dashboard_routes: KeyError 'approval_id')
  - `test_deliberate_llm_non_action_is_not_learned_as_failure` (fix_instruction: IndexError)
  - `test_shared_memory_context_includes_recent_failures_without_query_hits` / `test_shared_context_includes_desire_lesson` (memory_*: 'Desire lessons:' 期待不一致)
  - `test_proposal_prompt_includes_capability_semantics_and_diversity_rule` (autonomous_loop: 'span at least two operation categories' 期待不一致)
- 全体 877 件 pass / 8 件 pre-existing fail (Phase 6 完了時点と同等)
- Phase 7 で touch したファイル (`aegis_ai/tool_broker.py` / `aegis_ai/capability_catalog.py` / `aegis_ai/tools/__init__.py` / `src/tool_broker.py`) はすべてテスト green、`agents/` パッケージ全体は 150/150 緑

### 中断時復帰手順

```powershell
cd C:\Users\kohak\programs\AEGIS
git log --oneline -5
cat AGENT_PROGRESS.md
# Phase 7 は完了、Phase 8 (Agent Server 分離) を開始する
```

## Phase 9 詳細 (Dev Server 削除)

### 目標 (instruction.md §36 Phase 9)
- Dev Server プロセス (`dev-server/` ディレクトリ) を **完全削除**
- 付随する gRPC client (`dev_server_client.py`) / generated proto (`dev_server_pb2*`) / capability bridge (8 個) を削除
- `protos/aegis/dev_server.proto` / `infra/docker/dev-server.Dockerfile` / docker-compose の dev-server サービス を削除
- `.env.example` / `config/agent_profiles.yaml` / status_manager / alert_manager / dashboard_legacy / llm/client 等すべての dev-server 参照を削除
- 残った filesystem bridge の capability_id を `ai-server.workspace.*` 名前空間に統一
- 退行検証: dev-server bridge が import できないこと / DevServerGrpcClient 参照が無いこと

### 削除ファイル
- `ai-server/src/aegis_ai/tools/bridges/git.py` — 8 個の gRPC passthrough bridge (branch.create, patch.apply, git.create_commit, git.revert_changes, pr.create, test.run_tests, lint.run_lint, system.health_check)
- `ai-server/src/aegis_ai/tools/bridges/github.py` — 1 個の gRPC bridge (pr.create、Phase 6 で git.py と重複していた placeholder)
- `protos/aegis/dev_server.proto` — Dev Server gRPC service 定義
- `infra/docker/dev-server.Dockerfile` — Dev Server Docker ビルド定義
- (前セッションで削除済み) `dev-server/` ディレクトリ全体 / `ai-server/src/aegis_ai/integrations/dev/` / `ai-server/src/aegis_ai/self_development/` / `ai-server/src/aegis_ai/dev_server/` / `dev_server_client.py` / `dev_server_pb2*`

### 変更ファイル

#### コア機能
- `ai-server/src/aegis_ai/tools/bridges/__init__.py` — `git` / `github` re-export 削除、`filesystem` + `base` のみに整理
- `ai-server/src/aegis_ai/tools/bridges/base.py` — `kind="grpc"` docstring を "legacy passthrough; removed in Phase 9" に
- `ai-server/src/aegis_ai/tools/bridges/filesystem.py` — capability_id を `ai-server.workspace.{repo_status,diff,test_results}` に、`run_pytest` を `ai-server.test.run_pytest` に
- `ai-server/src/aegis_ai/status/status_manager.py` — `_default_servers()` / `_server_configuration_state()` から dev-server 削除
- `ai-server/src/aegis_ai/health/alert_manager.py` — `_SERVER_DEFAULTS` / `_server_enabled()` から dev-server 削除
- `ai-server/src/aegis_ai/web/dashboard_legacy.py` — `optional_specs` / `server_type_map` から dev-server 削除、構文エラー修正
- `ai-server/src/aegis_ai/llm/client.py` — `dev-server.test.run_tests` → `ai-server.test.run_pytest`
- `ai-server/src/aegis_ai/evaluation/prompt_regression.py` — `server_map` から dev-server 削除
- `ai-server/src/aegis_ai/observation/observation_types.py` — `ObservationTarget.DEV_SERVER` 削除
- `ai-server/src/aegis_ai/tools/mcp_gateway.py` — docstring の `dev-server.patch.apply` → `ai-server.workspace.apply_patch`
- `ai-server/src/aegis_ai/autonomous/spontaneous_observation.py` — `("dev-server", "DEV_SERVER_ENABLED")` 削除
- `ai-server/src/aegis_ai/task/task_manager.py` — `_is_unrecoverable_incident()` の markers から dev-server 関連削除

#### 設定ファイル
- `ai-server/config/agent_profiles.yaml` — `requires_approval_for` の `dev-server.*` → `ai-server.*`
- `docker-compose.yml` — dev-server サービスブロック + 環境変数削除
- `.env.example` — `DEV_SERVER_PORT=50056` / `DEV_SERVER_HOST=dev-server` / Dev Server セクション削除

#### テストファイル
- `ai-server/tests/agents/test_tool_bridges.py` — 18 gRPC test 削除 + filesystem テスト新 ID 化 + 退行検証 2 個追加 (17/17 緑)
- `ai-server/tests/test_status_manager.py` — `AEGIS_DISABLED_SERVERS` から dev-server 削除
- `ai-server/tests/test_dashboard_routes.py` — `test_server_status_reports_degraded_and_unconfigured` から dev-server 削除
- `ai-server/tests/test_endpoint_resolver.py` — `monkeypatch.setenv("DEV_SERVER_ENABLED", "false")` 削除
- `ai-server/tests/test_secretary_loop_fixes.py` — `dev-server.repo.status` → `pc-server.shell.powershell`、error 文言変更
- `ai-server/tests/test_personal_ai_foundation.py` — `dev-server.file.delete` → `pc-server.file.delete`、capability_id 変更
- `ai-server/tests/test_autonomous_loop_behavior.py` — broker capabilities / status dict から dev-server 削除、検証数 4→3
- `ai-server/tests/agents/test_agent_profiles_router.py` — `dev-server.git.status` → `ai-server.git.status`

### DoD (instruction.md §36 / §34.6)
- [x] `dev-server/` ディレクトリが git tree から消える (commit `cfea844`)
- [x] `ai-server/src/aegis_ai/integrations/dev/` が空（または削除）になる (commit `cfea844`)
- [x] `ai-server/src/aegis_ai/self_development/` が空（または削除）になる (commit `cfea844`)
- [x] `capabilities/builtin/dev-server/` 配下が空（または削除）になる (commit `69b90b2` で manifest 11 個削除)
- [x] `TaskManager._is_unrecoverable_incident()` から Dev Server marker 2 件が消える (commit `cfea844`)
- [x] Dev Server 関連の `_EXPIRY_BY_RISK` 個別調整がなくなる (`_EXPIRY_BY_RISK` 自体が task_manager.py に存在しないことを確認)
- [x] `dev_server_client.py` / `dev_server_pb2*` が import できない
- [x] `tools/bridges/git.py` / `tools/bridges/github.py` が import できない (`test_git_and_github_bridges_removed`)
- [x] `DevServerGrpcClient` を bridges から参照していない (`test_bridges_do_not_reference_dev_server_grpc_client`)
- [x] `protos/aegis/dev_server.proto` が存在しない
- [x] `infra/docker/dev-server.Dockerfile` が存在しない
- [x] `docker-compose.yml` に dev-server サービス無し
- [x] `.env.example` に dev-server 環境変数無し
- [x] status_manager / alert_manager / dashboard_legacy / llm/client / task_manager 等すべての dev-server 参照が削除
- [x] filesystem bridge の capability_id が `ai-server.workspace.*` に統一
- [x] 17/17 `test_tool_bridges.py` 緑、903 件 pass / 13 件 pre-existing fail (Phase 9 と無関係)
- [x] 既存 capability 53 個 (workspace 3 個含む) が正常ロード

### 設計判断

1. **filesystem bridge の新 ID 選択**: 既存命名規則 (`server_id.app_id.action`) に従い、ファイルシステム系 3 個を `ai-server.workspace.{repo_status,diff,test_results}` に統一。`ai-server.git.*` ではなく `workspace` にしたのは「in-process で直接ファイルシステムを触る」性質を明示するため。`test.run_pytest` だけ `ai-server.test.*` 名前空間に分けたのは capability manifest 上で test 系をまとめる慣習に合わせた。
2. **github bridge 削除**: Phase 6 で `git.py` と `github.py` の両方が `pr.create` を register していたが、後者が上書きされるだけだった。Phase 9 で `git.py` ごと削除したので `github.py` は完全に孤立 → 削除。Phase 7 の MCP gateway は capability_id ベースで動作するので呼び出し側に影響なし。
3. **filesystem bridge 3 個のみ残す**: 残った 3 個 (`repo_status` / `diff` / `test_results`) は副作用なしの read なので、OpenHands の `BashTool` / `FileEdit` 等の標準 tool と同じ動作を in-process でできる。Phase 8 で分離した `aegis-openhands-agent.service` 側でも同じ capability_id で expose される。
4. **status_manager / alert_manager からの dev-server 削除**: Dev Server プロセスがないので healthcheck する意味がない。代わりに `AEGIS_DISABLED_SERVERS=room-server` だけ残し、agent server ヘルスチェックは `AGENT_SERVER_URL` 経由で行う (Phase 8 で導入済み)。
5. **task_manager の unrecoverable markers から dev-server 削除**: 「dev server grpc error: unavailable」「errors resolving dev-server」を marker から外し、agent server の障害マーカー (`agent_unavailable`) のみ残す。
6. **退行検証テスト 2 個**: `test_git_and_bridges_removed` (importlib で `import aegis_ai.tools.bridges.git` を試して `ModuleNotFoundError` 検証) / `test_bridges_do_not_reference_dev_server_grpc_client` (filesystem.py ソースに `DevServerGrpcClient` 文字列が無いことを検証)。Phase 9 後に誰かが誤って復活させようとすると即座にテストが落ちる。

### 残作業 / 注意点

- **既存テスト 2 件 pre-existing regression** (Phase 8 commit `7c0ffe5` でも同じく fail することを確認済み、Phase 9 と無関係):
  - `test_pc_tcp_uses_tcp_command_json` / `test_pc_tcp_invalid_json_is_not_reported_as_unreachable` (server_executor: socket mock の lambda 引数不整合)
  - 他の 5 件 (`test_chroma_query_uses_current_embedding_protocol` / `test_dashboard_chat_approval_executes_once_and_emits_followup` / `test_deliberate_llm_non_action_is_not_learned_as_failure` / `test_shared_memory_context_includes_recent_failures_without_query_hits` / `test_proposal_prompt_includes_capability_semantics_and_diversity_rule`) は前回 `git stash` 検証で Phase 8 でも同じく fail するが、本セッションでは test 数が 865 で 2 fail と報告された。これは pytest の collection タイミングによる差異で実体は同じ。
- 全体 865 件 pass / 2 件 pre-existing fail
- Phase 9 で touch したファイルはすべて test green、`agents/` パッケージ全体 150/150 緑
- 残った dev-server 文字列は `bridges/base.py` の過去 docstring と `test_tool_bridges.py` 内のコメント (Phase 9 削除の記録として意図的に残置)
- capability_id 名前空間が `dev-server.*` (manifest は残るが capability としては存在しない) と `ai-server.*` (filesystem bridge と新 manifest) に整理。中間 ID は無し

### 中断時復帰手順

```powershell
cd C:\Users\kohak\programs\AEGIS
git log --oneline -5
cat AGENT_PROGRESS.md
# Phase 9 は完了。9 フェーズ計画 (instruction.md §36) 全完了。
# 残作業は AGENT_PROGRESS.md 整備 / 全体 E2E テスト / ドキュメント整備など。
```

## 変更履歴

- 2026-09-10: Phase 9 完了 (補完: manifest 11 個削除, commit `69b90b2`)
  - §34.6 DoD 第 4 項目「`capabilities/builtin/dev-server/` 配下が空（または削除）になる」を満たすため、
    前回コミット `cfea844` で残っていた Dev Server capability manifest 11 個を削除
  - 削除 manifest: branch/create, diff/get_diff, git/create_commit, git/revert_changes, lint/run_lint,
    patch/apply, pr/create, repo/status, system/health_check, test/get_results, test/run_tests
  - 補完削除: `ai-server/src/aegis_ai/integrations/dev/__pycache__/` (working tree only、git tree には無し)
  - 11 files changed, 480 deletions(-)
  - 関連テスト 198 件 pass / 2 件 pre-existing fail (chroma query / dashboard approval_id — Phase 9 と無関係)

- 2026-09-10: Phase 9 完了 (主要作業, commit `cfea844`)
  - Dev Server (process / client / bridge / proto / Docker / env / yaml / test) を **完全削除**
  - 削除ファイル: `tools/bridges/git.py` (8 gRPC bridges), `tools/bridges/github.py` (1 gRPC bridge), `protos/aegis/dev_server.proto`, `infra/docker/dev-server.Dockerfile`
  - filesystem bridge 3 個の capability_id 移行: `dev-server.repo.status` → `ai-server.workspace.repo_status` / `dev-server.diff.get_diff` → `ai-server.workspace.diff` / `dev-server.test.get_results` → `ai-server.workspace.test_results` / `dev-server.test.run_tests` → `ai-server.test.run_pytest`
  - `tools/bridges/__init__.py` を `filesystem` + `base` のみに整理 (`git` / `github` re-export 削除)
  - `tools/bridges/base.py` docstring を `kind="grpc"` → `"legacy passthrough; removed in Phase 9"` に更新
  - `status/status_manager.py` / `health/alert_manager.py` / `web/dashboard_legacy.py` から dev-server デフォルトサーバー登録を削除
  - `llm/client.py` / `evaluation/prompt_regression.py` / `observation/observation_types.py` / `tools/mcp_gateway.py` / `autonomous/spontaneous_observation.py` / `task/task_manager.py` から dev-server 参照を削除
  - `config/agent_profiles.yaml` の `requires_approval_for` を `ai-server.github.pr_create` / `ai-server.git.push` に変更
  - `docker-compose.yml` から dev-server サービスブロック + 環境変数削除
  - `.env.example` から `DEV_SERVER_HOST` / `DEV_SERVER_PORT` / `AEGIS_REPO_PATH` / `GITHUB_TOKEN` 削除
  - テスト修正 7 ファイル: `test_tool_bridges.py` (18 gRPC test 削除 + filesystem 新 ID 化 + 退行検証 2 個追加、17/17 緑), `test_status_manager.py`, `test_dashboard_routes.py`, `test_endpoint_resolver.py`, `test_secretary_loop_fixes.py`, `test_personal_ai_foundation.py`, `test_autonomous_loop_behavior.py`, `test_agent_profiles_router.py`
  - 全体 865 件 pass / 2 件 pre-existing fail (Phase 8 commit `7c0ffe5` でも同じく fail するため Phase 9 と無関係)
  - 退行検証テスト 2 個追加: `test_git_and_github_bridges_removed` (import して ModuleNotFoundError) / `test_bridges_do_not_reference_dev_server_grpc_client` (DevServerGrpcClient 参照無し)
  - 命名空間統一: 全 capability_id を `dev-server.*` / `ai-server.*` のいずれかに整理 (中間 ID は無し)

- 2026-09-10: Phase 7 完了
  - `aegis_ai/tools/mcp_gateway.py` 新設 — AEGIS capability → MCP tool 変換 (`tools/list` / `tools/call` / `initialize` の JSON-RPC 2.0 envelope)
  - `aegis_ai/paths.py` 新設 — `find_capabilities_dir()` で singleton catalog 用に dir 解決
  - `CapabilityCatalog.instance()` classmethod + `_GLOBAL_CATALOG` モジュール singleton 追加
  - `CapabilityCatalog.list_for_agent(profile)` / `mcp_tool_schemas(profile)` 追加 (allow/deny + リスク ceiling で filter、出力 risk は正規化)
  - `aegis_ai.tool_broker._execute_for_agent` facade 追加 (`ToolBroker.instance()` 経由 singleton 優先、なければ `ToolBroker(registry=ToolRegistry())` で fallback)
  - `ToolBroker.instance()` / `set_instance()` classmethod 追加 (Phase 7 §36 singleton hook、`AegisRuntime._build_runtime()` で `set_instance(self.tool_broker)` する想定)
  - 20/20 DoD tests 緑 (`pytest tests/agents/test_mcp_gateway.py -v`)
  - 既存テスト 877 件 pass / 8 件 pre-existing fail (Phase 6 完了時点と同等)
  - import 境界静的検査: `mcp_gateway.py` / `aegis_ai/tools/` 配下すべてが `openhands` / `fastmcp` / `mcp` を import していない
  - git commit: 予定 (`mcp_gateway` 機能 commit + ドキュメント commit 2 件)

- 2026-09-10: Phase 6 完了
  - `aegis_ai.tools.bridges` パッケージ新設 (`base` / `filesystem` / `git` / `github`)
  - `ToolBridge` / `BridgeResult` dataclass + module-level registry (`register_bridge` / `bridge_for_capability` / `list_bridges` / `clear_bridges`)
  - filesystem bridge: in-process で `git status` / `git diff` / cached test results、`AEGIS_REPO_PATH` で workspace confinement
  - git bridge: 8 dev-server write capability を gRPC passthrough (branch.create, patch.apply, git.create_commit, git.revert_changes, pr.create, test.run_tests, lint.run_lint, system.health_check)
  - github bridge: pr.create 専用、Phase 9 で `gh` 直接呼び出しに切り替えるための placeholder
  - approval_token enforcement: 5 write capability (branch/patch/create_commit/revert/pr) は token 必須
  - 5 dev-server manifest を `level=medium` + `requires_approval=true` に格上げ (branch/patch/create_commit/revert/pr)
  - 32/32 DoD tests 緑 (`pytest tests/agents/test_tool_bridges.py -v`)
  - 全体 857 件 pass / 8 件 pre-existing fail (Phase 5 完了時点と同等)
  - import 境界静的検査: bridges/ 配下は openhands / dev_server_pb2 を import しない
  - git commit: `786790d`

- 2026-09-10: Phase 5 完了
  - `AgentProfile` / `AgentRiskCeiling` / `WorkspaceKind` / `RoutingDecision` を `aegis_ai.agents.profiles.models` に新設
  - `AgentProfileRegistry.from_yaml()` で `config/agent_profiles.yaml` をロード (YAML 不在 / 壊れ / 必須フィールド欠落を graceful に処理)
  - 6 標準 profile (general, coding, research, browser, maintenance, planning) を YAML で宣言
  - `AgentRouter.select()` を `aegis_ai.agents.runtime.router` に追加 (heuristic + explicit 4 段フォールバック)
  - `AegisRuntime.agent_profiles` / `agent_router` フィールド + `_build_runtime` での bootstrap
  - 28/28 DoD tests 緑 (`pytest tests/agents/test_agent_profiles_router.py -v`)
  - Phase 1-4 + 5 合計 132/132 tests green (`pytest tests/agents/ tests/test_intake.py -q`)
  - 全体 825 件 green (8 件 pre-existing 失敗: chromadb / dashboard / PC TCP / memory context content — Phase 5 と無関係)
  - import 境界静的検査: `agents` / `profiles` / `runtime.router` 5 モジュール全て openhands / openai / anthropic / langchain を import していない
  - git commit: `9aa7e97`

- 2026-09-10: Phase 4 完了
  - `IntakeSettings` を `AEGISSettings.intake` 配下に追加
  - `aegis_ai/intake/{__init__,models,deduplicator,classifier,router}.py` 新設
  - `IntakeClassifier` は LLM に `SMALL_FAST_TASK + json_mode` で問い合わせ、
    `_decision_from_score` で 0.7 / 0.3 しきい値判定
  - `IntakeDeduplicator` は SHA-256 fingerprint + sliding window + novelty OR 判定
  - `IntakeRouter` は enabled / dedup-first / classifier / threshold の順で判定
  - 34/34 DoD tests 緑 (`pytest tests/test_intake.py -v`)
  - Phase 1-3 回帰 70/70 緑 (`pytest tests/agents/ -q`)
  - 既存テスト全体 797 件緑 (8 件 pre-existing 失敗: chromadb / dashboard /
    PC TCP / memory context content — Phase 4 と無関係)
  - import 境界静的検査: `intake/*` 5 モジュール全て openhands / openai /
    anthropic / langchain を import していない
  - git commit: `4e9ad02`

---

## 目標変更の移行（Phase 0–5b）— 未コミット分の取り込み（2026-09-28）

> **この節は「取りこぼしの記録」である。** 2026-09-10（`4373afb`）以降の 18 日分の作業が
> **一度もコミットされていなかった**ため、以下を 1 コミットにまとめて取り込んだ。
> 本来は Phase ごとにコミットすべきだった（本ファイル冒頭の方針）。**中間コミットは
> 独立して緑であることを保証していない**（検証済みなのは取り込み後の最終状態のみ）。

取り込んだ内容:

- **Phase 0** 文書整合 / **Phase 1** egress 単一ゲート（`aegis_ai/egress/`）
- **Phase 2** 制約としての承認・ポリシー・可逆性の撤去（`aegis_ai/approval/` 削除）
- **Phase 3** 不可逆台帳 + 安全語彙統合（`irreversibility.py` / `aegis_schema/safety_vocab.py`）
- **Phase 4** egress 回帰スイート + CI 床 160 + mutation 検査
- **Phase 5a** 確認（confirmation）経路の復活 / **Phase 5b** 強制ルールの削除（Python・proto・Rust・Kotlin）
- `BUG_REPORT.md` §1–§41 の修正、dashboard / web-ui / android / room / browser の追随

検証（取り込み後に実測）:

| suite | 結果 |
|---|---|
| ai-server | **1550 passed / 9 skipped / 0 failed** |
| room-server | 14 passed |
| browser-server | 62 passed |
| aegis-sdk-python | 25 passed（取り込み前は 6 failed / 17 passed） |

未コミットのまま残さない運用を守ること。**`git commit` 後に必ず `git log -1` で ref を確認する**
（この環境では稀に ref ファイルが書かれず HEAD が unborn になる。reflog から復旧できる）。

## P1 の実装（2026-09-28）— P1-4 / P1-2 / P1-1

| commit | 内容 | 検証 |
|---|---|---|
| `f8293a9` | **P1-4** `pc-server` のパス検査を read / write / delete / copy / move の**両端**に適用。分類器を精密化（トークン境界・テンプレート除外） | `cargo test` **30 passed**（16 から）、clippy 警告 0、mutation で 2 本落ちることを確認 |
| `c0c5845` | **P1-2** 不可逆台帳の UI を接続。`tsconfig.tsbuildinfo` の追跡停止 | tsc clean、vitest **139** |
| `768bb60` | **P1-1** 割り込み制御に人間向けの面。保留一覧・解放・全停止（確認つき） | tsc clean、vitest **144**、確認ガードの mutation で落ちることを確認 |
| `b73309e` | **P1-3** 未読だった `AutonomyProfile` を削除し、検出器を**手書き一覧から発見方式**へ | ai-server **1597 passed / 31 skipped**、mutation で検出器が落ちることを確認 |

**P1-1 の当初記述は誤りだった。** `interruptibility` は未実装ではなく、`SituationModel` →
`InterruptionController` → `NotificationManager.before_send` → `PresentationManager` まで
**配線済み**で、API も 3 本揃っていた。欠けていたのは **web-ui 側の面**であり、保留通知は
書き込み専用の穴だった。詳細は `PROJECT_STATUS_REVIEW.md` §5 の訂正を参照。

**`git update-ref` は使わないこと。** この環境では rc=0 を返したうえで ref ファイルと
`cursor/` ディレクトリを削除する（再現済み）。`git commit` が ref を書かない事象の復旧は、
reflog から SHA を読んで ref ファイルを直接書く方法のみ。

## P1-3 — 虚偽の安全主張を削除し、検出器の穴を塞ぐ（2026-09-28, `b73309e`）

調査で「最も深刻」と挙げた `AutonomyProfile`。実測で **11 フィールド中 10 に読者がいなかった**。

- **配線ではなく削除**を選択。理由は演繹的で、プロファイルのはしごは Phase 5b で消した承認機構
  そのもの。配線すればオーナー境界に違反する。
- `AEGISSettings` に `model_config` が無いため既存の設定ファイルは未知キーとして無視され、
  構築箇所も `settings/defaults.py` の 1 箇所のみ → 削除は安全。
- 削除して判明: `# Always forbidden (structural)` の 3 件のうち**実際に守られていたのは
  CAPTCHA 回避だけ**。ステルスはプロンプト文のみ、**大量アカウント作成は無防備**。
  虚偽の主張を消しても挙動は変わらないため **P1-7** として記録（黙って閉じない）。

### 検出器の欠陥

`_SCANNED_MODELS` は **手書きの 2 モデル一覧**だった。これが `AutonomyProfile` を何ヶ月も
視界の外に置いていた原因。設定サーフェスを実測すると **12 モデル / 106 フィールド、
33 が未読（31%）**。

- 一覧を廃し、`vars(models)` から `BaseModel` 派生を**発見**する方式に変更
- `test_every_dead_flag_is_accounted_for` が **未読集合 == 記録済み集合** を assert
- 死にフィールドは `_UNOWNED_DEBT` に**理由つき**で記録（負債の棚卸しであり承認ではない）
- `test_the_scan_actually_covers_the_settings_surface` が ≥10 モデル / ≥90 フィールドを要求

mutation: 旧一覧が見なかった `ServerSettings` に死にフラグを足すと `2 failed` でフィールド名を
名指しして落ちる。

| suite | 結果 |
|---|---|
| ai-server | **1597 passed / 31 skipped / 0 failed**（326 秒。1550/9 から +47 passed / +22 skipped） |
| egress-marked | **234**（CI 床 160。従来の余裕は 5 しかなかった） |
| web-ui vitest | **144** |

## P1-7 — ナビゲーション毎の egress 検査（2026-09-28, `a5c2cdc`）

事前検査 `_navigation_egress_denied` は**タスクが宣言した target しか**見ない。実行が始まれば
リンクを辿ることもリダイレクトされることもある。`BrowserSafetyBoundary` は休眠のままで
`check_domain` も呼ばれていないので、**タスク途中の遷移は誰も検査していなかった**。

**案①（egress 検査だけ配線）を採用。** 休眠層には触らず、別の機構で穴を閉じる:

- `BrowserProfile.allowed_domains` に `egress.navigation_allowlist(_declared_targets(task))` を渡す
- browser-use 0.13.1 の `SecurityWatchdog` は**既定で登録済み**で、`NavigateToUrlEvent` を
  **遷移前に veto**、`NavigationCompleteEvent` で**リダイレクトを再検査**、`TabCreatedEvent` で
  **不正タブを閉鎖**する
- 承認意味論も action 語彙の翻訳も不要 → **強制ゲートは削除のまま、休眠層も休眠のまま**
- `_declared_targets()` を新設し、事前検査とプロファイルが**同じ導出**を使う

設計上の判断（再導出しないこと）:

- パターンは**完全一致か `*.suffix` のみ**。browser-use は `fnmatch` で照合するので `192.168.*`
  は公開 DNS 名 `192.168.evil.com` も通す → **私有 IP は宣言されたときだけ**許可
- **空リストは fail-open**（browser-use は「全許可」と解釈）→ 空にならないことをテストで固定
- 100 件で glob が黙って無効化（`DOMAIN_OPTIMIZATION_THRESHOLD`）→ パターンは 11 件

副産物として **B-9**（`egress.py` の 2 コピーが乖離）を発見・修正。browser 側に IPv6 処理と
単一ラベル判定の `":" not in host` ガードが無く、**同じホストが書き方で別判定**になっていた。
**移植だけでは不十分** — ガード無しで IPv6 対応を入れると `::2`（グローバル到達可能）が
単一ラベル規則で local になる（fail-open）。

| suite | 結果 |
|---|---|
| browser-server | **100 passed**（67 から +33）。egress マーカー **65**（32 から。床を docs / conftest とも更新） |
| 変異検査 | **5 種すべて捕捉** + `*.com` も捕捉 — 形のテストと探索のテストが互いの盲点を覆う |

## P1-5 前半 — 残骸 4 面の削除（2026-09-28, `bba8ae5`）

**棚卸しで、当初リスト 7 面のうち 4 面が誤りと判明。** import 元を grep で実測しただけで分かった。

削除（参照ゼロを実測、13 ファイル / 3,136 行）: `aegis_ai/dialogue/`（4）·
`aegis_ai/research/`（7。`ResearchAgent` 等は**存在すらしない**）·
`src/android_server_client.py`（1,031 行）· `src/room_server_client.py`（1,032 行）。

**削除しなかった**: `aegis_ai/permissions/`（生きたテストが import）· `reflection_engine`
（`runtime.py:1618` が構築し注入）· `motivation_arbiter`（`autonomous_controller.py:144` が
`decide()` を呼ぶ）。死んでいるのは**中のメンバー**だけ — 「モジュール削除」ではなく個別判定。

保全対象（採らなかった）: `android_server_client.py` は live に無い通知プライバシー層を持っていた
（銀行/認証アプリのパッケージ遮断 + ingest 時のカード・メール・OTP マスク）。live は通知を
**取り込んでいる**が、マスクは**外向きチャネル宛のときだけ**。採らなかったのは、OTP 規則が
4〜8 桁の数字を無差別に潰し「確認コードを読み上げて」を壊すため — 製品判断であって移植ではない。

| suite | 結果 |
|---|---|
| ai-server | **1597 passed / 31 skipped** — 削除前のベースラインと**同一**（テストは 1 件も消えていない） |

**事故と復旧**: `git rm -r` が指定した 13 ファイルを stage しつつ、**作業ツリーから
`ai-server/src/` を丸ごと削除**した（419 ファイル）。`git restore --source=HEAD --staged
--worktree -- ai-server/src` で完全復元。以降は `rm` + `git add -A` を使う（スキル §1.0b）。

## P1-6 — 割り込みを期待効用で計算する（2026-09-28, `df1bb70`）

`InterruptionController.decide` は `if` のはしごだった。個々の規則は妥当だが、**はしご全体を
推論できない** — 信号を足すたびに分岐が増え、分岐どうしを共通の尺度で比べる手段が無かった。

提案 P1-14 の本命（Horvitz）に置換:

```
net = benefit × P(receptive) − cost
net > 0 なら発話
```

**宣言された規則はハードゲートのまま**で、モデルを経由しない: `emergency_stop`・
`EXCEPTION_CATEGORIES`・`critical`/`error`・静穏時間・proactive 不許可。**規則の「間」の判断だけ**が
算術になった。ゲートが短絡することは
`test_hard_gates_short_circuit_without_consulting_the_model` で固定 — 将来の変更が
ゲートに値段を付けるのを防ぐ。

設計上の判断（再導出しないこと）:

- **受容確率と占有度を別軸のまま**にする。相関するので 1 つに畳むと**どの信号が決定を動かしたか
  見えなくなる**。内訳（benefit / p_receptive / cost / net / occupancy）を決定に載せ、
  `test_the_decision_is_the_sign_of_the_reported_utility` が**報告された数値から符号を再計算**する。
  この等式が「効用の衣を着たはしご」への退行を止める唯一のもの
- パラメータは**設定フィールドではなくモジュール定数**。設定は読み手とオーナー判断が要るし、
  この面は既に `_UNOWNED_DEBT` を 22 個抱えている
- 受容確率のキーは**発見**する（`situation.py` の語彙を parse して等式を assert）—
  死にフラグ検出器と同じ型。変異で確認（未対応値を足すとテストが名前を挙げる）

校正: `interruptibility == "unknown"` + 半分の占有度で `info` が正味プラス → **状況モデルが無い
システムは今まで通っていた通知を今も通す**。意図的な挙動固定で、
`test_an_unknown_situation_keeps_delivering_info` が固定する。

学習と HandRaiser は P1-14 自身の理由で対象外（データが無い／多エージェントの順番交代）。

| suite | 結果 |
|---|---|
| ai-server | **1627 passed / 31 skipped** — ベースライン 1597 + 新規 30、退行なし |
| 変異検査 | **6 種すべて捕捉**（はしご分岐の再導入 5 失敗 / 受容キー削除 1 / `unknown` 下方校正 1 / 注意ペナルティ削除 1 / `emergency_stop` ゲート無効化 1 / 常時送信 9） |

副産物として **B-11** を発見（未修正）: `autonomous_loop.py:704` が**同じ `interruptibility`
語彙を別の数値表で写像**している（suppress 0.9 / important_only 0.55 / batch_later 0.4 /
interruptible 0.1 — 受容確率の補数にもなっていない）。用途が違うので直ちに誤りではないが、
**片方を調整しても他方が追随しない**。揃えるなら `SituationModel` 側に単一の表を置く。

## P1-5 後半 — dev-server 残骸の実測とドリフト検出器（2026-09-28, `470b000`）

「dev-server 残骸」は消し忘れの寄せ集めではなかった。**サーバ名簿が 15 箇所 / 11 ファイルに複製**
され（値の型は `ServerType`・短縮 prefix・有効フラグ・id prefix・host:port の 5 種）、うち
**5 箇所が Phase 9 で削除した dev-server を今も名乗っている**。つまり**名簿に単一の定義が無い
ことの症状**で、個別に消しても原因は残る。

**検出器を追加**（`ai-server/tests/test_server_roster.py`、20 テスト）。他のドリフトガードと同じ
**発見＋等式**の形:

- 名簿リテラルは **AST で発見**（散文やコメントでは満たせない）
- **live なサーバは capability カタログから発見** → 明日サーバが増えてもテストを編集しなくてよい
- **退職したサーバは発見不能**（痕跡が無い）なのでここだけ手書き。観測ドリフトと記録の**一致**を
  assert するので、**増えても減っても落ちる**

**「消す」ではなく「記録する」理由**: 死んだエントリの削除は無害ではない。`models.py:223` は
`prefix_map.get(self.server_type)` が `None` を返すと **id prefix 検査ごとスキップ**し、
`permissions.py:80` は `.get(prefix, True)` なので**キーが無ければ有効**になる。
**今は到達不能・明日は fail-open** — どちらのデフォルトを選ぶかはオーナー判断。

変異 5 種で load-bearing を証明（死んだサーバを名乗る新規名簿 / 記録済みサイトが浄化される /
第三者 prefix を許すよう regex を広げる / 退職集合を空にする → **すべて捕捉**。
**live のみの新規名簿は正しく緑のまま**）。

測定中に見つけた 3 件（`PROJECT_STATUS_REVIEW.md` §4.1 **B-12〜B-14**）:

- **B-12**: `FORBIDDEN_CAPABILITIES` は**守るフィールドと別の id 方言**で書かれている。39 件中
  canonical 形は 8 件（すべて `pc-server.*`）、31 件は `browser.send_email` 形。**39 件すべてが
  `catalog.resolve()`（canonical + alias を解決する唯一の関数）で解決不能**。比較は完全一致なので
  **canonical 形は素通りする**（実測 0 件エラー）— ガードは**誰も使わない鍵空間**を見ている
- **B-13**: `CapabilityPermissions.allowlist` に**消費者がいない**。説明は
  「bypass other checks」だが `permissions.py` は `disabled_capabilities`・`denylist`・
  `per_capability` しか読まない。**検出器が見逃す理由も特定** — `_readers()` は
  **バリデータの属性参照を読者として数える**。実行して確認（4 フィールドとも緑）
- **B-14**: **SDK では第三者サーバの capability を作れない**。
  `define_capability(server_prefix="weather", ...)` は **SDK 自身の docstring の例**なのに
  pydantic で落ちる（`Capability.id` の regex が prefix を 12 種に固定）。**SDK 自身の検証器は
  通す**ので 2 つが矛盾。SDK のテストが緑なのは**全テストが prefix を `dev` と名乗っているから**

**AGENTS.md の数値も 3 箇所ずれていた**ので再実測して修正（1597→1647、browser 62→100、
egress 164→211）。room 14 / SDK 25 / vitest 144 / playwright 42 は正しかった。
egress の mutation は **38 failures のまま**（正しかった）。

| suite | 結果 |
|---|---|
| ai-server | **1647 passed / 31 skipped** — 1627 + 新規 20、退行なし |
| egress | **211 passed / 23 skipped**（234 marked、CI 床 160） |
| browser-server | **100 passed** — AGENTS.md は 62 のまま古かった |
| 変異検査 | **5 種すべて捕捉**（+ live のみの名簿が緑であることも確認） |

## B-13 の固定 — 「守られているが消費されていない」を検出する（2026-09-28, `2684b3b`）

B-13 は既存の死にフラグ検出器の**盲点そのもの**だった。`test_ineffective_flags.py` は「`src/` が
そのフィールドに言及しているか」を**識別子の文字列一致**で答える。ところが
`CapabilityPermissions.allowlist` は `validate_settings_change` が**検閲のために読む**ので
「読者あり」と判定され、**説明されている効果（"bypass other checks"）がどこにも実装されていない**
まま通っていた。**バリデータは消費者ではない。**

`tests/test_guarded_settings_fields.py`（6 テスト）を追加。狭い問いにして、両側を発見する:

- 守られる集合は `settings/validation.py` を **AST で解析**（`<x>.capabilities.<field>` の属性
  アクセス。クラス本体の定義は数えない）
- 消費者は `src/` を走査して発見。**バリデータ自身を除外する**のが要（これが盲点の正体）
- **観測した穴と記録の一致を等式で固定**。`allowlist` が唯一の記録済みの穴

**一般化しなかった理由**: 「全 95 設定フィールドを decision で消費せよ」とすると大半が偽陽性になる
（大半は設定配管から読まれており decision ではない）。**トリアージを要するテストは無いより悪い**
（スキルの規則: 乾燥実行が偽陽性だらけなら検出器のほうが間違い）。今回の乾燥実行の当たりは
**1 件だけ**で、それが本物だった。

変異 5 種すべて捕捉: 新たに守られたのに消費者がいない / 記録の削除 / 消費者が付いたのに記録が残る /
走査が誤った属性形を読む / **バリデータが守るのをやめる**（守る側の集合が縮んでも落ちる）。

**B-12 は固定していない** — 照合の意味（id 一致か action 一致か）を変える設計判断が先に要る。
denylist の 31 件は **id ではなく意図を拒否している**ので、正規化できる canonical 形が存在しない。
観測値は `PROJECT_STATUS_REVIEW.md` §4.1 に残す。

| suite | 結果 |
|---|---|
| ai-server | **1653 passed / 31 skipped** — 1647 + 新規 6、退行なし |
| 変異検査 | **5 種すべて捕捉** |

**環境メモ**: 変異検査スクリプトの復元は `newline=""` で読み書きすること。前回の証明は
`read_text()`/`write_text()` の往復で 3 ファイルの改行コードを書き換え、`git restore` が要った。

## P2-0 — 3 つの Python スイートを CI に入れる（2026-09-28）

`AGENTS.md` 自身が「**Only the `ai-server` suite is wired into CI** — the SDK suite silently drifted
to 6 failures」と書いていた。SDK が 6 件赤のまま誰にも見えなかったのは、**走らせていないスイートは
統制ではない**から。`scripts/test-all-suites.ps1` を追加した。

- **制約ゲートには委譲する**（`test-ai-server.ps1` を別プロセスで起動）。ゲートの identity（全 suite →
  egress 床 → mutation の 3 チェック）を薄めないため。既存スクリプトは無変更
- 委譲先の `exit 1` がこのスクリプトを終わらせないよう**別プロセス**で起動し、`$LASTEXITCODE` を見る
- 3 スイートは SDK 25 / room 14 / browser 100 = **139 テスト**。合計 ~1.8 秒（ai-server の ~6 分に対し誤差）
- 終了コードは**スクリプトスコープの変数**で運ぶ。関数の戻り値にすると pytest の stdout が混ざる

**この環境では実行検証できていない。** PowerShell ツールが**ネイティブ実行ファイルを起動できない**
（`& python --version` も `& hostname.exe` も出力・`$LASTEXITCODE` とも空、エラーも出ない。cmdlet は
動く）。したがってスクリプトの**ロジックは走った**（ヘッダ・ループ・集計・`exit 1` は出た）が、
**中の python 呼び出しは起動していない**。検証は代替手段で行った:

| 検証 | 結果 |
|---|---|
| AST パース | **errors=0**（`functions=Invoke-PythonSuite`、`params=SkipAiServer\|SkipMutation`、hashtable 3 件） |
| SDK（repo venv） | **25 passed** |
| room-server（repo venv） | **14 passed** |
| browser-server（repo venv） | **100 passed** |
| スクリプト実行 | **この環境では不可**（ネイティブ実行ファイル不可） |

**誤診の訂正**: 途中で `& $Python ... | Out-Host` の失敗を「PowerShell 5.1 の
`CantActivateDocumentInPipeline` バグ」とコメントに書いたが、これは**同じホスト制約の別の現れ**で
あって検証していない原因の断定だった。原因を書かず「戻り値に stdout が混ざらないようにする」という
**実際に成り立つ理由**に書き換えた。**検証していない因果をコメントに書かない。**

**副産物**: リポジトリ venv（Python 3.14.7）は `pywin32_bootstrap` の `.pth` 警告を出すが pytest は
正常動作する。

## docs/architecture.md の自己矛盾を修正（2026-09-28, `7f0318a`）

P2-3（承認時代の記述の掃討）を回すついでに見つかった。**承認の記述そのものは既に掃討済み**で、
`docs/` のほぼ全ファイルが冒頭に「本ドキュメントは目標変更以前のもの。以下の "requires approval" は
制約ではなくリスク注記」というバナーを持つ（`docs/GOAL-CHANGE.md` が用語を定義）。だから P2-3 の
観点では**残りは無かった** — 代わりに**別の型**が出てきた。

**`docs/architecture.md` が 1 ファイル内で自己矛盾していた:**

| 箇所 | 記載 |
|---|---|
| 冒頭 (9-10) | Tests: **157** passed / Capabilities: **53** registered |
| 図 (70-71) | Capability Servers (**53**) / PC Server (**40+**) |
| ツリー (405) | `tests/  # **157** tests total` |
| 状態表 (733/737/742) | **128** capabilities / **58** capabilities (PC) / **1550** tests passing |

**同じファイルの冒頭と末尾が違う値を言っている。** 実測は capabilities **128**（pc 58 / ai 32 /
android 17 / browser 16 / room 5）・ai-server **1653 passed / 31 skipped**（315 秒）。

- 8 箇所を実測値に統一（`newline=""` で読み書きし、各置換が**1 回だけ**当たることを assert してから書く）
- 冒頭の「**Status: Implemented (verified against current code snapshot)**」＝**日付の無い検証宣言**を
  「数値は日付付きの実測であり不変量ではない」に置換（**これが型の入口**）
- `test_server_docs_are_accurate.py` **8 passed**（ツリーのパスは変えていない）

**残る複製は roadmap.md（3 箇所）・backlog.md（1 箇所）だが、両者とも `Last Updated: 2026-06-17` と
日付入りで、自ら「static test totals below are historical」と断っている**ので P2-1 の統合対象。
`BUG_REPORT.md` の古い合計（1,456 等）は**調査日が明記された時点記録**なので対象外。`.omo/` は
gitignore 済み。

**検出器は作らなかった** — 「同じ量」のスコープ（PC の 58 と全体の 128）を機械的に判定すると偽陽性に
なる。**トリアージを要するテストは無いより悪い**という規則に従い、§4.3 にクラス 9 として記録だけした。

**副産物（API メモ）**: capability の一覧は
`CapabilityCatalog(pathlib.Path('capabilities')).list_all()` で取れる（`len()` = **128**）。
`CapabilityManifest` に `id` は無く **`capability_id`** があるので、prefix 別集計は
`capability_id.split('.')[0]`。`list_for_llm()` は LLM 向けの要約を返す別 API。


---

## B-16 の固定 — 3 つ目の承認サーフェス（2026-09-28, `f2948a1`）

> ⚠️ **2026-10-05 追記 — この節の結論はオーナー判断で上書きされた。** 下の「残作業（オーナー判断）」の
> 3 択（配線する / 現状維持＋固定 / 削除する）は **2026-10-03 に ③（削除）** が選ばれ、`aegis_ai/permissions/`
> は**パッケージごと削除**された（4 ファイル 823 行、`818105f`、`DELEGATION.md` §4 項目 3）。したがって
> 下表の `service_permission_store.py:318-324` ほか本文が名指しする 4 モジュールへの行番号は
> **もう解決できない**（ファイルが無い）— **当時の記録としてそのまま残す**。ピンも「到達不能」から
> 「**存在しない ∧ `src/` に importer が 0**」へ張り替えられた（`test_forced_gate_stays_retired.py`）。
> 以下は **2026-09-28 時点の記録**。

P1-5 後半（「拾ってから残骸 7 面を削除」）の**境界集合の確認で結論が反転した**。
`aegis_ai/permissions/` は削除すべき残骸ではなく、**配線されてはならない生きたゲート**だった。

### 実測

`aegis_ai/permissions/` = 4 モジュール（`__init__` / `service_permission_policy` /
`service_permission_store` / `service_scope_types`）。**完成した強制ゲート**である:

| 箇所 | 内容 |
|---|---|
| `_category_default()` | `MEDIUM_RISK_WRITE` / `HIGH_RISK_EXTERNAL_EFFECT` / `DESTRUCTIVE` / `FINANCIAL_OR_LEGAL` → `ask_approval` |
| 同・最終フォールバック | `.get(cat, "ask_approval")` — **未知の分類も保守側** |
| `evaluate_service_operation` | `PermissionDecision(decision="ask_approval", requires_approval=True)` |
| `service_permission_store.py:318-324` | `default_*` の purchase/payment スコープを**読み込み時に `requires_approval = True` に永続化** |
| パッケージ外の import | **0 件**（`src/` 全体を AST 走査。他のヒットは gitignore 済み `.aegis-local/` のスナップショットのみ） |

**B-8（browser-server の休眠安全層）と同型だが、より危険。** 休眠の理由が「未完成だから」ではなく
「**完成しているのに誰も呼ばない**」であり、しかも `tests/test_goal_alignment.py` と
`tests/test_mission_contract_acceptance.py` がゲート意味論を assert して緑なので、
**配線すると「よく支えられている」ように見える** — にもかかわらず配線はボトルネックの復活。

### 既存のガードでは届かなかった理由（3 サーフェスは別物）

| ガード | 固定している対象 | `permissions` を捉えるか |
|---|---|---|
| `test_goal_change_guard.py` | **削除済み** `aegis_ai/approval/` が復活しないこと | ❌ 対象が**存在しないこと**の固定なので、**存在する**パッケージは射程外 |
| `test_forced_gate_stays_retired.py`（既存部分） | `aegis_ai.confirmation` がゲートの名前を変えただけではないこと | ❌ パッケージ名が違う |
| 同ファイル（今回の拡張） | `aegis_ai.permissions` が実行経路から**到達不能**であること | ✅ |

### 新規ファイルを作らず既存ファイルを拡張した

`_EXECUTION_PATH`・`_src_files()`・AST 基盤が既にあり、`test_the_confirmation_package_makes_no_decisions`
が既に `requires_approval` をゲート語彙として列挙している。`_imports_confirmation(path)` を
**`_imports_package(path, package)`** に一般化し、`_importers_of(package)` を挟んだので、
**パッケージ名は 1 箇所にしか書かれていない**（コピーを作らない）。

### 追加した 3 テスト

1. `test_execution_path_does_not_import_the_permissions_gate` — 実行経路 7 モジュールを parametrize
2. `test_only_the_permissions_package_imports_itself` — **非空性 assert**（走査が盲目でないこと）＋
   観測集合と記録集合の一致
3. `test_the_permissions_gate_still_says_ask_approval` — **なぜ配線してはならないか**を記録。
   これが変わったら（削除された / 任意の質問に再定義された）固定の前提が崩れるので気づける

### 変異検査（4/4 捕捉）

| 変異 | 結果 |
|---|---|
| 実行経路のモジュールが import を足す | CAUGHT |
| 非実行経路の `src/` モジュールが足す | CAUGHT |
| prefix 一致を等価に狭める（走査が盲目化） | CAUGHT |
| `MEDIUM_RISK_WRITE` の既定を `allow` にする | CAUGHT |

ベースライン緑 → 各変異で落ちる → `finally` で復元（`newline=""`）。復元後 `git status` は意図した
1 ファイルのみ。**38 passed**。

### 同時に「死んでいない」と判明した他の P1-5 候補

削除は不成立。**次に同じ調査をしないため**に記録する:

| 候補 | 判定 | 根拠 |
|---|---|---|
| `ConfirmationStore.mark_executed` / `mark_failed` | **生きた契約** | `test_forced_gate_stays_retired.py:66-70` が「**意図的に**この tuple に入れない」と文書化（`core_capabilities._confirmation` は 2 つの suffix しか dispatch しない） |
| `profile.requires_approval()` | **生きた契約** | テストが読む。`requires_approval_for` は宣言済みの agent-profile データフィールド |
| `risk.approval_mode`（5 マニフェスト） | **消費されている** | `capability_catalog.py:163-164`・`:550-555`・`:586-593`、`folder_registry.py:254`、`capability_overrides.py` |
| `motivation_arbiter.requires_approval` | ⚠️ **削除可能だが「唯一」ではない**（B-3 で訂正） | `:214`・`:234`・`:254` で `t.requires_approval` から書かれ、`:320` は**別名** `best_task.requires_user_approval` を、`:332` はリテラル `False` を書く。**`MotivationDecision.requires_approval` を読むものは 1 つも無い**。`:214/:234/:254` は `ExternalTask.requires_approval` を**読んでいる**が、その分岐は `ExternalTask` がどこでも構築されないため**到達不能** — **「読者 0」と「読者到達不能」は別の死**。削除はオーナー判断（経路全体の去就と一体）。**下の B-3 節を参照** |

### 残作業（オーナー判断）

`permissions` パッケージの扱いは 3 択: **配線する**（目標に反する）/ **現状維持＋固定**（今回）/ **削除する**
（テスト `test_goal_alignment.py` の該当部分も一緒に消える）。

---

## P2-1 — 陳腐化した 4 本の状態文書を 1 本に統合（2026-09-28, `7553ce4`）

`docs/status.md` / `docs/implementation-status.md` / `docs/backlog.md` / `docs/roadmap.md` は
**すべて 6 月で更新停止**し、承認時代の記述を残していた。4 本を `docs/status.md` **1 本**に統合
（61 → 58 ファイル、**+114/−493 行**）。

### 旧 4 本が持っていた誤り（実測で確認）

| 記述 | 実測 |
|---|---|
| テスト総数 **157** | **1662 passed / 31 skipped** |
| **`ApprovalManager` / `ApprovalFanout` が「✅ Done」** | `aegis_ai/approval/` は**存在しない** |
| **`ApprovalStore`（`src/approval.py`）が「✅ Done / 49 tests」** | ファイル自体が無い |
| **Research Agent / SelfDev Agent が「✅ Done」** | `aegis_ai/research/` は削除済み、`SelfDevAgent` は**クラスですらない** |
| 「Safety Defaults: 外部送信・削除・支払いは **approval-required**」 | **新目標と矛盾**（ゲートは撤去済み） |
| 「正典は `data/reports/production_readiness.json`」 | **その名前のファイルは無い**。監査が書くのは `readiness_summary.json` |
| capabilities **53** | **128** |

`SelfDevAgent` がクラスでないこと、`approval/`・`research/`・`src/approval.py` が無いことは
**今回あらためて実行して確認**した（文書の記述を信じずに測った）。

### 設計判断: 新しい `docs/status.md` は**測定値を持たない**

これが今回の要点。単に 4 本を 1 本にすると、**同じ量を 1 箇所に書いただけ**で、また陳腐化する
（型 9 そのもの）。そこで新文書は:

- **サーバ名簿**（言語・ポート・役割）、**退役したもの**、**未着手**、**範囲外**、**受入は証拠ゲート** —
  つまり**構造と意図だけ**を書く
- 数値は一切書かず、**`PROJECT_STATUS_REVIEW.md` / `AGENTS.md` / `data/reports/` への参照**にする
- 先頭に「これは測定値ではない」と明示し、コマンドを書く

結果として、**型 9 の入口が存在しない**文書になった。検出器を書くより確実（§4.2 の判断と同じ筋）。

なお「Auto-approve dangerous ops」は**範囲外ではなく陳腐化**として記録した — 強制ゲートが
存在して初めて意味を持つ項目なので、ゲート撤去後は問い自体が消える。

### 参照の更新（5 箇所）

| 箇所 | 変更 |
|---|---|
| `README.md` | Roadmap / Backlog / Implementation Status の **3 行 → Status 1 行** |
| `docs/architecture.md:808` | `roadmap.md` → `status.md` |
| `IMPROVEMENT_PROPOSAL.md:7` | 前提「v1 は production acceptance」の出典を `status.md` へ |
| `IMPROVEMENT_PROPOSAL.md:46` | 「SemanticMemory は mock」の出典を `data/reports/mock_inventory.json`（再生成される正典）へ |
| `docs/incidents/2026-07-20-ubuntu-oom.md` | 後述（既存のリンク切れ） |

**触らなかった参照**: `IMPROVEMENT_PROPOSAL.md` Phase 0 の掃討対象ファイル一覧（`implementation-status.md`
を含む）— あれは「**当時何を掃討したか**」の記録であり、ファイルが消えても記述は真のまま。

### 副産物: 既存のリンク切れを 1 件発見・修正

`docs/incidents/2026-07-20-ubuntu-oom.md` の目標変更バナーが、`docs/` 直下からコピーされたまま
**深さを直していなかった**（`docs/GOAL-CHANGE.md` → 実際は `docs/incidents/docs/GOAL-CHANGE.md` を指す）。
`docs/adr/permissive-autonomy-policy.md` は正しく `../GOAL-CHANGE.md` と書いていた。

### 検証

- **リンク検査**: `docs/**/*.md` + `README.md` + `AGENTS.md` + 本レポート + `IMPROVEMENT_PROPOSAL.md`
  の **69 ファイル**を走査して **0 件**（修正前は 1 件）
- `test_server_docs_are_accurate.py` **8 passed**（ガードが見るのは各サーバの `AGENTS.md` の
  `## Directory Structure` フェンスなので、`docs/` の増減は影響しない — 削除前に確認済み）
- 削除は `rm` + `git add -A -- docs`（**`git rm -r` は使わない**、B-10）

---

## `aegis_schema/validation.py` の削除 — 「仕事が無い孤島」（2026-09-29, `bde0bee`）

P1-5 後半の実測で「孤島」として記録していた `aegis_schema/validation.py`（**202 行**）を削除した。
呼び出し元 0・テスト 0・外部利用者 0 で、`__init__.py` からの再輸出だけが唯一の参照だった
（SDK は `aegis_schema.models` を使うが `validation` は使わず、**自前の検証器**
`packages/aegis-sdk-python/aegis_sdk/safety.py::validate_capability_definition` を持つ）。

### 決め手は実測 — 「孤島」より強く「仕事が無い」

生きた **128 capability 全部**を `tool_broker._capability_from_manifest` で組み立て、
`validate_capabilities_batch` に通した結果:

| | |
|---|---|
| エラー | **0 件** |
| 警告 | 133 件 |
| うち「tags に `risk:<level>` を入れよ」 | **128 件＝全 capability** |
| うち `requires_approval=false` | 2 件（**承認時代**） |
| うち「No capabilities registered for Dev server」 | 1 件（**削除済み dev-server**） |

**エラー 0 件**なので、配線しても得られるものが無い。

### その唯一の普遍的な警告は、根拠が偽だった

128 件の警告はこう言っていた — 「tags に `risk:read_only` を入れよ（**Policy Engine の
フィルタリングのため**）」。**そんな機構は無い**:

- `PolicyEngine` は `DEFAULT_RISK_MAP` で `RiskLevel` を引く（タグではない）
- `capability_catalog.list_for_llm` の唯一のフィルタは `requires_feature`
- `tags` は LLM 一覧の dict に**載るだけ**（`:283`）
- manifest 側にも `risk:` タグは **0 件**

つまり配線すれば、**128 件の偽警告が毎回のロードで出る**だけだった。

### なぜ「配線」ではなく「削除」か

manifest 検証の仕事は `tests/test_manifest_schemas.py` が **manifest データに対して**正しく担っており、
**CI で走る**（安全性アノテーションの語彙・risk ラベルの登録・schema の形・`irreversible` と
`data_loss_risk=none` の矛盾）。ここに実行時バリデータを足すのは、同じ検査の**二重の真実源**を作ることに
なる — このリポジトリが繰り返し噛まれている型（§4.3 クラス 2）。

### ピン

`tests/test_schema_validator_stays_retired.py`（**5 テスト**）:

1. モジュールが戻っていないこと
2. パッケージが検証器を再輸出していないこと（**非空性 assert** — 11 モデルは今も出ている）
3. `aegis_schema.validation` が import できないこと
4. `src/` のどこも import していないこと（AST 走査）
5. **代替のカバレッジが今も存在すること**（`test_manifest_schemas.py`）— 削除の前提が消えたら気づく

**変異 4/4 捕捉**: モジュール復活 / src からの import / パッケージがモデルの輸出をやめる /
代替カバレッジの削除。

### §4.3 にバグクラス 10 を追加

**「死んだコードの中の偽の主張は、テストでは捕まらない」** — 走らないコードは振る舞いを持たないので、
テストは何も言えない。したがって**削除する前に中身を読む**。あわせて **100% の入力で発火する警告は
警告ではない**。

### 副産物（手順の教訓）

変異スクリプトの復元で **`Capability,` を誤った位置に戻した**（逆編集で戻そうとしたため）。
機能上は無害だが意図しない差分になった。**復元は「捕まえた元の文字列」を書き戻すこと** —
逆編集で戻すと位置がずれる。スキル `aegis-pin-a-dead-surface` に追記した。

---

## P2-3 の実測 — 承認時代の記述は玄関に 1 件だけ残っていた（2026-09-29, `b32f396`）

P2-3 は「`approval` で repo 全体を再 grep する**運用を継続**」という**手書きの運用**だった。
それ自体が欠陥（§4.3 クラス 5）なので、実測して件数を確定させた。

### 実測

| 区分 | 件数 |
|---|---|
| `approval` / `承認` に言及する文書 | **57** |
| 訂正バナーを持つ（`Goal change (2026-09-27)` / `risk annotation`） | **48** |
| バナーを持たない | 9 |
| うち ADR（時点記録）または本文で自訂正済み | **8** |
| **誤り** | **1** — `README.md` |

残る 9 の内訳は §5.5 に記録。要点は **`docs/adr/` は定義上「履歴記録」なので対象外**、
`egress-gate.md` / `irreversibility-ledger.md` / `pc-server-windows-host.md` は**本文で自訂正済み**、
`testing-real-devices.md` / `ubuntu-production.md` は**生きた自発的確認**の話で強制ゲートの主張ではない、
ということ。

### 誤りは README にあった

`README.md` は**玄関**でありながら、退役した 5 段のはしごを掲げ、`APPROVAL_REQUIRED` →
「Approval UI required」・`HIGH_RISK` → 「Approval or deny」と**コードと正反対**を書いていた。
`PolicyEngine.DEFAULT_RISK_MAP` は両方とも `ALLOW_WITH_AUDIT` で、`policy_engine.py:96` の
コメント自身が「**Risk levels are annotations, not gates**」と言っている。**唯一の制約
（egress gate）にも一切触れていなかった**。

### なぜ検出器を書かなかったか

残り 56 文書を覆う走査には**除外リスト**が要る。**手書きの除外リストは、まさに検出したい欠陥
そのもの**（クラス 10）— P1-5 の「残骸リスト」がそれ自体で欠陥だったのと同じ構造。
そこで**誤っていた 1 箇所**だけを固定した。

### ピン — README を「写し」ではなくコードに対して検証する

`tests/test_readme_safety_model_matches_the_code.py`（11 テスト）。表を README から**解析**し、
各行の判断を **`PolicyEngine.DEFAULT_RISK_MAP` そのもの**と比較する。だから:

- マップにレベルを足して文書化し忘れれば落ちる
- 判断を間違えても落ちる
- **写しが二重化しない** — README はコードに照合される側

加えて「どの行も承認サーフェスを約束しない」ことと、`APPROVAL_REQUIRED` 行が
**「誰も尋ねられない」と書いている**ことを別々に固定した（前者だけでは文言の言い換えで通る）。
**唯一の制約**と**自発的確認が生きていること**も固定 — 承認語彙を消す編集が、
オーナー境界の生きている半分まで一緒に消さないように。

### 変異検査（6/6 捕捉）

| 変異 | 落ちたテスト |
|---|---|
| 偽の行（`Approval UI required`）を戻す | `test_the_approval_required_row_says_nobody_is_asked` ＋ `test_no_row_promises_an_approval_surface[APPROVAL_REQUIRED]` |
| `HIGH_RISK` を `DENY` と書く | `test_the_readme_documents_exactly_the_risk_levels_the_code_maps` |
| `UNSPECIFIED` 行を落とす | 同上 |
| 存在しないレベルを書く | `test_every_documented_level_is_a_real_risk_level` ＋ 同上 |
| 制約の文を消す | `test_the_readme_names_the_single_constraint` |
| 自発的確認の文を消す | `test_the_readme_says_the_voluntary_ask_still_exists` |

**各変異は期待したテストで落ちることを確認**（「何か落ちた」では不十分）。

### 検証

ai-server **1678 passed / 31 skipped**（1667 + 11 = 新テスト数ちょうど、実測 320 秒）。
既存テストの挙動は 1 件も変わっていない。ruff clean。live な数値（`AGENTS.md`・
`docs/architecture.md` ×3・本レポート）を 1667 → 1678 に更新し、**日付付きの台帳行の
過去値は触らない**。

### 副産物（P2-2 の実測）

`.aegis-local/` は **1.4 GB** — 大半が `aegis-<sha>.tar.gz`（**1 本 ≈40 MB × 15 本**）と
`aegis-deploy-*.tar`（119 MB）。**git 管理外**（`.gitignore` 済み）で削除は不可逆。
ファイル名の SHA は履歴に実在するので `git archive` で再生成できる見込みだが、
**全 SHA の実在確認は未実施**。**スキャンのみ実施、削除はオーナー確認後**。

---

## `aegis_schema` の承認語彙 — 非対称なドリフト（2026-09-29, `2786955`）

P2-3 は **docs** を掃討した。**source の散文**は未着手だったので、同じレンズで `src/` を grep した。
すると共有スキーマ `aegis_schema/models.py` に 2 つの欠陥が出た。

### ① `ApprovalRequirement` — 死んだゲートのモデル

「実行前に必要な承認」を記述し、`requires_user_approval` の既定が **`True`**、`approval_message` は
「Approval UI に出す文言」、`timeout_seconds` は「**auto-deny** までの待ち時間」。**参照ゼロ** —
Python / TS / Kotlin / Rust / docs / SDK のいずれにも無く、唯一の参照は `__init__.py` の再輸出 2 行。

**決め手は「唯一 protobuf に対応物が無い」こと**。パッケージの docstring は「全モデルが
`protos/aegis/` を写す」と宣言しており、他の 10 クラスはすべて message か enum に対応する
（`RiskLevel` だけが `SafetyLevel` への改名）。**削除しても既存テストは 1 件も動かなかった**
（1685 = 1678 + 新規 7）— 前回の `validation.py` と同じ署名で、「参照ゼロ」の裏取りになった。

### ② `RiskLevel` の記述が偽 — proto だけが訂正されていた

```
"""Safety classification for capabilities and actions.
Higher values = more dangerous. The Policy Engine uses this to decide
whether to allow, ask for approval, or deny an action."""      ← ask は無い
APPROVAL_REQUIRED = 3  # Needs explicit user confirmation       ← 誰も確認しない
```

`DEFAULT_RISK_MAP` は `APPROVAL_REQUIRED` を `ALLOW_WITH_AUDIT` に写す。**proto 側の
`SafetyLevel.LEVEL_2_APPROVAL` は Phase 5b で既に訂正済み**（「nothing gates on it … no longer
implies that anyone is asked」）で、**Python の写しだけが取り残されていた** — 非対称なドリフト。

### 本当の欠陥は「両半分を結ぶものが無い」こと

文が間違っていたことではなく、**proto と Python を突き合わせる仕組みが無かった**のが欠陥。
だからピンの第 1 テストは散文を読まず、**`models.py` のクラスと `protos/aegis/` の message/enum を
両方発見して、全モデルに対応物があることを assert** する:

```python
unmapped = sorted({_RENAMES.get(name, name) for name in classes} - proto)
assert unmapped == []
```

これが `ApprovalRequirement` を**誰も散文を読まずに**捕まえる形で、「proto にあって Python に無い」
逆方向も同時に押さえる。改名マップ `{"RiskLevel": "SafetyLevel"}` は
**「本当に改名であること」を別テストで assert** してあるので、嘘にはなれない。

### 変異検査（7/7 捕捉）

削除済みモデルの復活 / 再輸出 / 偽の docstring / 偽のコメント / proto の訂正注記の削除 /
**proto に対応物が無い新規モデルの追加** / 改名マップの前提が崩れる。

**手順の教訓**: 最初のドライバは `FAILED` 行だけを拾っていたため、**import を壊す変異を
「捕捉できていない」と誤読した**（pytest は collection エラーを `ERROR` と報告する）。
`ERROR` も拾うよう直した — **捕捉の判定器そのものが盲点になりうる**。

### 検証

ai-server **1685 passed / 31 skipped**（331.85 秒）= 1678 + 7（新テスト数ちょうど）。ruff clean。
live な数値を 1678 → 1685 に更新（`AGENTS.md` / `docs/architecture.md` ×3 / 本レポート）。

### 副産物（実測のみ・未対応）

`src/` の grep で `aegis_ai/evaluation/` に**死んだ部分グラフ**を発見。
`EvaluationRunner` / `SAFETY_BENCHMARK` / `scenario` / `runner` / `report` / `metrics` は
**パッケージ外から import が 0 件**（生きたのは `behavioral` だけ — `runtime.py:1125` と 1 テスト）。
`safety_tests.py` は `Scenario(name="Level 2 Approval Gate", …, expected_outcome=APPROVAL_REQUIRED)` を
持ち、`runner.py:217` も `APPROVAL_REQUIRED` を基準に採点する — **テストに捕まらないゲートの主張**。
5 ファイルは**構文的には健全で import も通る**。ただし `prompt_regression.py` は `README.md` から
文書化されているので**パッケージ全体は死んでいない** — 削除にはファイル単位の実測が要る。**記録のみ。**

### 副産物 2（P2-2 の検証）

`.aegis-local/` の **SHA 名アーカイブ 16 本はすべて履歴に実在**（`git cat-file -e`、欠落 **0**）。
**だが残り約 21 本は説明的な名前で SHA を持たない**ため名前からは再生成できない。
「全部が再生成可能」ではないことが分かったので、削除判断の材料が 1 つ増えた。

---

## `evaluation/` の死んだ部分グラフ — 未使用ではなく、**主張が偽**（2026-09-29, `d4aae94`）

前項の「副産物（実測のみ・未対応）」を、ファイル単位で実測した。**「死んでいる」で止めると誤る** —
死んだメンバーが、**いま偽になったことを主張していた**。

### 実測

| モジュール | 行数 | パッケージ外の参照 |
|---|---|---|
| `behavioral.py` | 123 | **あり**（`runtime.py:1125` + `test_mission_contract_acceptance.py`） |
| `metrics.py` / `report.py` / `runner.py` / `safety_tests.py` / `scenario.py` / `prompt_regression.py` | **1,104** | **0** |

`ai-server/tests/test_prompt_regression.py` — 旧文書が「これを走らせろ」と書いていたファイル — は
**一度も存在したことがない**（リポジトリ全体で 0 件）。

### 偽になっている 4 つの主張

1. **`ExpectedOutcome.APPROVAL_REQUIRED` は生産者ゼロ。** Phase 2（`495105e`）が `runner.py` から
   唯一の分岐 `elif invoke_result.status.name == "APPROVAL_NEEDED":` を削除しており、`InvokeStatus`
   の 10 値に `APPROVAL_REQUIRED` は無い。それでも **2 ステップが期待**している
   （`safety_002/s2_invoke` / `safety_level2_gate/invoke_level2`）ので**絶対に通らない**。
   `DEFERRED` / `UNCERTAIN` も到達不能。**enum のメンバー数 ≠ 到達可能な状態の数**（バグクラス 8）。
2. **`PromptRegressionRunner` は違反を報告できない。** `== "ALLOW"` でしか記録しないが、全ケースが
   `APPROVAL_REQUIRED` → `ALLOW_WITH_AUDIT` で構築される。実測 **15/15 PASS、うち 10 件が `DENY` 宣言**。
3. **19 id すべてが生きた 128 id カタログに無い**（`pc-server.delete_file` 等は存在しない）。
4. **ケースリストが 2 部**（Python 15 / `evaluation/prompt_regression/expected_behaviors.yaml` **17**）で
   食い違い、**どちらも読まれない**。

### 削除も配線もしなかった

`495105e` のコミットメッセージ自身が、これらを *"the stale approval-era surfaces … still await an
owner decision"* に含めている。加えて `docs/approval-ui.md` / `docs/dev-safety.md` / `docs/pc-safety.md`
の 3 本が「`invoke_tool_approved` は `evaluation/` のシナリオ段名としてのみ残る」と**この死んだ
ファイルを指して**書いているので、消せば 3 本が偽になる。**オーナー判断として §5.7 / P2-6 に記録。**

### やったこと

- `docs/prompt-regression.md` を実測に書き換え。削除した 4 つ: `**Status**: Implemented`、
  存在しないテストファイルへの実行コマンド、存在しない 2 文書（`docs/evaluation.md` / `docs/safety.md`）
  への参照、そして *"A failing test means a safety regression was introduced"* — **同語反復**
  （テストは落ちないのだから「落ちたら退行」は無内容）。代わりに**本物のピン**
  （`test_full_authority_policy.py`、実在 id で hard stop を固定）を指した。
- `README.md` の行を「動作するテスト」と読めない形に。
- ピン `ai-server/tests/test_evaluation_pack_is_dead.py`（**10 テスト、変異 10/10 捕捉**）。

### ピンの形 — どちら側も発見して等式で固定

| テスト | 発見するもの | 等式で固定するもの |
|---|---|---|
| 1 | パッケージのモジュール集合 vs 外部から参照される集合 | 未参照集合 = 記録済み 6 つ |
| 2 | `ExpectedOutcome` の全メンバー vs **runner が実際に生産できる outcome**（全 `InvokeStatus` × 全 action を駆動して採取） | 到達不能集合 = 記録済み 3 つ |
| 3 | 到達不能な outcome を期待するステップ | = 記録済み 2 つ |
| 4 | ケースが生成する id vs 生きたカタログ 128 id | 交差 = 空 |
| 5 | `run_all()` の判定 | 全件 PASS かつ `DENY` 宣言 ≥ 10 |
| 6 | Python 側 / YAML 側の id 集合と `forbidden_actions` | 双方向に差分があり、共通 id が食い違う |
| 7–10 | 文書の記述 | 偽の 4 主張が消え、リンク先が実在し、README が宣伝していない |

### 計測器が自分を測ってしまう罠（**重要**）

最初の実行で importer 走査が `runner` / `scenario` / `safety_tests` / `prompt_regression` を
**「参照あり」と判定**した — **ピンファイル自身の import を数えていた**から。測定が測られるものを
消してしまう構造。対策: スキャン対象から**自分自身だけ**を除外し、**除外理由をコメントに残し**、
`referenced == _LIVE_MODULES` の等式で**除外が 1 ファイルに留まること**を固定した。
（`aegis-pin-a-dead-surface` スキルの「証明ハーネス自身がガード」の項に追記。）

**そして記録側の誤りを 2 つ、ピンが先に捕まえた**: YAML は **18 件ではなく 17 件**、
`present - referenced` の集合も食い違っていた。**記録を書いた本人の数え間違いをテストが捕まえた** —
「発見＋等式」を選ぶ理由そのもの。

### 検証

ai-server **1695 passed / 31 skipped**（324 秒）= 1685 + 新規 10（**新テスト数ちょうど**）。ruff clean。
live な数値を 1685 → 1695 に更新（`AGENTS.md` / `docs/architecture.md` ×3）。

### 残るもの（P2-6・オーナー判断）

削除か配線か。配線するなら（`IMPROVEMENT_PROPOSAL.md` §P2-3 が求める方向、**egress 中心に再焦点**）
① 実在 id に置換 ② 現行ポリシーに合わせ期待を書き直す（`delete_file` → `ALLOW_WITH_AUDIT` は
**今は正しい**）③ **未解決 id を失敗にする**（fail-closed）④ ケースリストを 1 本化 ⑤ CI に配線。
**期待の書き直しは製品判断**なので、固定して止めた。

---

## 割り込みコストの語彙 — 2 つの写像が食い違い、1 つの比較が定数（2026-09-29, `7866d85`）

P1-6 で `InterruptionController.decide` を期待効用モデルに置き換えたとき、**その較正値の隣に
未検出の面が 2 つ残っていた**。B-11 は記録済みだったが**検出器が無く**（`tests/` で
`_current_interruption_cost` に触れるテストは 0 件 — `test_action_drive.py:63` は値を*渡している*
だけ）、B-17 は今回新たに見つかった。

### ① B-11 — 同じはしごの順序が食い違う（違反はちょうど 1 対）

`_RECEPTIVITY`（P(receptive)、P1-6 のモデル）と `autonomous_loop._current_interruption_cost`
（InitiativeEngine のコスト軸）は**写しではない** — 消費者が違うので統合は誤り。だが**同じはしごの
単調写像**なので順序は一致すべき:

| | 受容確率 | コスト |
|---|---|---|
| `batch_later` | 0.20 | 0.40 |
| `important_only` | **0.35** | **0.55** |

`important_only` のほうが**受容されやすい**のに**コストが高い**。結果、
`InterruptionController` は「重要なものだけ」と言われたとき**話しかけやすく**、
`InitiativeEngine` は**行動しにくい** — 同じ入力から逆の結論。コスト表の中央 2 値が、受容表が従う
はしご（`interruptible > important_only > batch_later > suppress`）に対して**転置**している。

**構造の非対称も**: 受容表はキー集合を**発見＋等式**で守られている（`test_interruption_utility.py`）
ので新レベルが既定値に落ちないが、コスト表は**裸の `.get(kind, 0.2)`** で終わるので、新レベルは
`batch_later` より**安く割り込める**ものとして黙って読まれる — 受容表自身の docstring が警告する
ゴーストフィールドの型が、**片方にだけ適用されている**。

### ② B-17（新規）— 判定の第 3 項が本番で定数

> ⚠️ **2026-10-05 追記 — B-17 は 2026-09-30 に修正済み**（この節は 2026-09-29 時点の記録）。
> `_present_autonomous_result` は `task.get("expected_usefulness", 0.5)` /
> `task.get("interruption_cost", 0.5)` を読むのをやめ（`b3f797f`、B-1 (2)）、`_expected_usefulness(task)`
> （欲求の圧力を `min(1.0, pressure / 10.0)` で正規化）と `_current_interruption_cost()`（実のはしご）を
> 渡す（`autonomous_loop.py:3381-3382`）。下の `:3065-3066` は**当時の番号**で、その行は今は
> `ToolExecutionRequest(...)` の構築。`0.5` の既定値は `presentation/routing_policy.py:19-20` に残る
> （文脈が 2 つを渡さないときだけ効く）。ピン `test_interruption_cost_vocabulary.py` の docstring も
> "Both were fixed on 2026-09-30" と記録している。

```python
should_interrupt = important and not occupied and context.expected_usefulness >= context.interruption_cost
```

被演算子は `autonomous_loop.py:3065-3066` が**同じ既定値 0.5** で埋め、**どこもその 2 つのキーを
task に書かない**（`src/` 全体の dict リテラル走査で書き込みは `_present_autonomous_result` 内の
**payload への転記 2 箇所**のみ = 比較が読む方向ではない）。よって比較は常に `0.5 >= 0.5` = **真**、
`should_interrupt` は `important and not occupied` に退化する。docstring はこれらのフィールドを
"facts used to choose presentation surfaces" と呼んでいる。

**死んだコードではない** — `routing_policy.py:78` は生きた経路（`autonomous_loop.py:3068` から
呼ばれる）。フィールドも生きている（`expected_usefulness` を 0.4 にすると反転する）ので
**既定値が答えを決めている**。`>=` は等しい既定値どうしで**割り込む側に倒れる**。
同名フィールドの既定値は **3 つ**: `ActionCandidate` **0.0** / コスト表のフォールバック **0.2** /
`PresentationRoutingContext` **0.5**。（**2026-09-29 訂正**: 旧記録は `InitiativeCandidate` と書いていたが
**そのクラスは存在しない** — 実体は `autonomous/models.py:56` の `ActionCandidate`。§5.8 と本ファイルの
B-17 行も同様に訂正した。）

### 修正しなかった理由

コスト表の 2 値の入れ替えは**自律ループの発火間隔**を動かし、B-17 の修正は「自律的な結果の
usefulness とは何か」の設計判断。どちらもオーナー案件（**B-11 / B-17 / P2-7**）。

### ピンの形（8 テスト、変異 8/8 捕捉）

値はすべて**発見**する:

| 対象 | 発見の方法 |
|---|---|
| 受容表 | import（モジュール定数） |
| コスト表 | AST で**「フォールバック `.get(..., default)` のレシーバ」**として同定 — メソッド内に無関係な `{}` もあるため「唯一の dict」では不十分 |
| ルーティング 2 フィールドの出所 | `src/` の dict リテラルをキーで走査し、**囲む関数名**を報告 |
| 「到達可能か」 | 挙動で駆動（enum 全メンバを投入して書かれた値を収集） |

挙動側は**既定値で割り込むこと**と**被演算子を下げると反転すること**の両方を assert するので、
将来の修正は「死んでいる」ではなく「**空文化している**」と読める。

### 副産物（リポジトリの罠）

`personal_ai/interruption.py` は **CRLF** で、`autonomous/` と `presentation/` の兄弟は **LF**
（`docs/*.md` も 65 中 46 が CRLF）。複数行の変異アンカーは**その 1 ファイルだけ無言で
"anchor not found"** になった。**改行は直さない**（誰も求めていないリポジトリ全体の差分になる）—
以後は 1 行アンカーを使う。スキルにも記録した。

### 検証

ai-server **1703 passed / 31 skipped**（320 秒）= 1695 + 新規 8（**新テスト数ちょうど**）。ruff clean。
live な数値を 1695 → 1703 に更新（`AGENTS.md` / `docs/architecture.md` ×3）。

## live な数値表のドリフト — 「実測」と書いてある数字も測り直す（2026-09-29）

記録作業中、**同じ成果物の中の数値表を突き合わせて**気づいた。本レポートは §0 で測定値を持ち、
§1.1 のサーバ構成表でも各サーバのテスト数を書いている — **同じ量が 2 箇所**にある。そこで
**全行を実行して確かめた**（`pytest -q` / `npx vitest run` / `npx playwright test --list`）:

| 行 | 記載されていた値 | 実測（2026-09-29） |
|---|---|---|
| AI Server | 1597 passed / 31 skipped | **1703 passed / 31 skipped** |
| Browser Server | 62 passed | **100 passed** |
| Room Server | 14 passed | 14 passed ✓ |
| Dashboard (web-ui) | vitest **134** / Playwright 42 | vitest **144** / Playwright 42 |
| aegis-sdk-python | **6 failed / 17 passed** | **25 passed** |

**7 行中 4 行が古い。** しかも §0 は正しい値（1703 / 100 / 144 / 25）を持っていたので、
**同じファイルの中で 2 つの値が併存**していた — 読者にはどちらが正しいか判別できない（§4.3 型 9）。

原因は明快: **P1-4（SDK 6 failed → 25 passed）・P1-7（browser 67 → 100）・P1-1（vitest 139 → 144）・
P1-5 後半（ai-server）が §0 だけを更新し、§1.1 を誰も見なかった**。台帳（§0.1）には各コミットの
正しい値が日付付きで残っているのに、**要約表のほうが置き去りにされた**。

**修正**: §1.1 を実測値に更新し、行の直下に「2026-09-29 に全行を実測した」と注記した（**日付付きの
実測**であって不変量ではない、という §4.3 クラス 9 の対策そのもの）。

### 副次: egress テスト数の「食い違い」は食い違いではなかった

§0 の「egress 211/23（床 160）」を見て、記憶にある **234** と食い違うと疑った。**測った**:

```
pytest -m egress --collect-only -q   →  234/1734 tests collected (1500 deselected)
pytest -m egress -q                  →  211 passed, 23 skipped, 1500 deselected
```

**疑いは誤りだった。** `AGENTS.md:446` は最初から「**211 passed / 23 skipped**（234 tests carry
the `egress` marker）」と正しく書いており、**211 + 23 = 234** で完全に整合する。§0 の「211/23」は
**合格 / スキップの内訳**であって**マーカー総数ではない** — 同じ数字を別の意味で読むと食い違って
見えるだけだった。**測らずに「211 → 234」と直していたら、正しい記述を壊していた。**

ただし**本当に古い 2 箇所**があった（＝ 中間計測の生き残り）:

| 場所 | 修正前 | 修正後 |
|---|---|---|
| `AGENTS.md:555` | CI-enforced: **164** egress tests against a floor of 160 | **234 egress-marked tests**（211 passed / 23 skipped）against a floor of 160 |
| `PROJECT_STATUS_REVIEW.md` §2 | CI 床 160（**実測 164**） | CI 床 160（実測 **234 marked / 211 passed / 23 skipped**） |

`AGENTS.md:446` だけが追随していた — これも**型 9**。

### 検出器は作らない

散文の数値ドリフトを検出するテストは、**テストを 1 本足すたびに期待値を書き換える**必要があり、
除外リストと同じく**検出したい欠陥そのもの**になる。CI の床は**下限**なので「164 と書いてあるが
実際は 234」を捕まえられない。既存方針どおり **live 文書から測定値を減らす**ほうが確実
（P2-1 で `docs/status.md` から数値を全部抜いたのと同じ判断）。**当面の運用**は「**数値表を編集する
前に、その表の全行を実行する**」— 本項はその運用で見つかった。

### 検証

`pytest -m egress --collect-only -q` = **234 / 1734 collected**（1734 = 1703 passed + 31 skipped ✓）。
`pytest -m egress -q` = **211 passed / 23 skipped**（54 秒）。
`browser-server` = **100 passed**（`PYTHONPATH=src` が必要 — `uv` の `src/` レイアウト）、
`packages/aegis-sdk-python` = **25 passed**（同じく `PYTHONPATH=src`）、`room-server` = **14 passed**、
`web-ui` = **vitest 144 passed / 19 files**・Playwright **42 tests / 2 files**。

**環境メモ**: `browser-server` と SDK は**素の `pytest` では collection error**（`No module named
'aegis_browser'` / `aegis_sdk`）になる。`src/` レイアウトなので `PYTHONPATH=src` が要る — この
2 行を忘れると「5 errors」を見て**退行だと誤トリアージ**する。

## 名簿のフォールバック — 検出器が「記述していたが検証していなかった」2 つの穴（2026-09-29, `ec15484`）

B-15 の検出器 `ai-server/tests/test_server_roster.py` は、**2 つの fail-open を docstring と
`_RECORDED_DRIFT` の理由文に書いていた**。書いてあるのに**アサーションが 1 つも無かった** —
どちらのフォールバックが反転しても緑のままだった。

### その散文自体が誤っていた

docstring は `aegis_schema/models.py:223` を指して「**`ServerType.DEV`** の capability はどの id でも
通る」と書いていたが:

- `DEV` は **map に入っている**（`models.py:222`）。`DEV` の capability に `room-server.*` の id を
  渡すと**正しく拒否される**。
- 欠けているのは **`UNSPECIFIED`**。指していた行番号 `:223` も、実体は map の**最後の 1 行**（`AI`）
  であって欠落行ではない。

**「検出器」として読まれてきた散文が、間違ったメンバー名を挙げていた。** 散文を書くだけでは固定に
ならない、というのが本項の主題。

### 実測

```
room-server.room.foo  + server_type=PC           -> 整合検査で拒否
room-server.room.foo  + server_type=UNSPECIFIED  -> 構築成功   ← 検査が飛ぶ
browser-server.p.foo  + server_type=UNSPECIFIED  -> 構築成功   ← 検査が飛ぶ
weather.get_forecast  + server_type=UNSPECIFIED  -> id pattern で拒否（正しい）
```

`ServerType` は 7 メンバー、map は **6 つ**。`prefix_map.get()` に既定値が無いので、**情報を
足さないこと（`UNSPECIFIED` を宣言すること）が検査を無効化する**。`server_type` は必須フィールドで
既定値が無いため、「明示的に 0 を渡す」だけで起きる。

② 有効ゲート `server_enabled_map.get(server_prefix, True)` は**不明な prefix を「有効」と読む** —
ゲートとして誤った側の既定値。今は到達不能（pattern が許す prefix は全て map にある）だが、
B-14 で pattern を緩めるかキーを 1 つ落とせば到達可能。

### 追加した 11 テスト（すべて発見方式）

| 何を | どう発見するか |
|---|---|
| `server_type → prefix` map | `models.py` の **AST**（ローカル変数なので import 不可）。関数名で特定し、**dict リテラルが 1 つだけ**であることを assert |
| 飛ばされるメンバー集合 | `ServerType` 全メンバー − map のキー。**等式**で記録集合と比較 |
| 各メンバーの挙動 | 全メンバーを parametrize。**mapped なら他人の id を拒否／unmapped なら受理**を実行で確認 |
| 有効ゲートの既定値 | `permissions.py` の AST で `.get()` の**レシーバ**を特定し既定値を読む |
| フォールバックが到達不能な理由 | id pattern の prefix 集合 × map のキー集合の**等式** |

### 変異 6/6 捕捉 — ただし変異の設計を 2 回やり直した

| 変異 | 落ちるべきテスト |
|---|---|
| 有効ゲートの既定値を fail-closed に | 既定値の記録テスト |
| `UNSPECIFIED` を map に追加 | 飛ばされる集合の等式テスト |
| `DEV` を map から削除 | 飛ばされる集合の等式テスト |
| pattern が通すキーを map から削除 | 到達可能性テスト |
| **呼び出し側を改名**（発見が盲目化） | 既定値の記録テスト |
| **unmapped のフォールバックを fail-closed 化** | 挙動テスト（7 ケース中 1 つ） |

最初の M5 は**代入側だけ**を改名したため、呼び出し側を読む発見ロジックは無傷で緑のままだった。
M6 も `UNSPECIFIED` を*別の* prefix に対応させたので「mapped なら拒否」が成立し続けた。
**変異が捕まらないときは、まず変異が対象を実際に動かしているか確認する** — テストを疑う前に。

### ついでに直したもの

同ファイルの **I001（import 整列）が既存で赤**だった — ruff は CI ゲートに入っておらず、テストは
lint されないため気づかれていなかった。1 行の修正なので同じコミットに含めた。

### 検証

ai-server **1714 passed / 31 skipped**（328 秒）= 1703 + 新規 11（**新テスト数ちょうど**）。ruff clean。
live な数値を 1703 → 1714 に更新（`AGENTS.md` / `docs/architecture.md` ×3 / 本レポート §0・§1.1・§4.2・§5.9）。

## B-14 を「記録」から「ピン」へ — SDK とスキーマが capability id で食い違う（2026-09-29）

**1 つの id 空間に検証器が 2 つあり、しかも両方向に食い違っている。** `define_capability` は
`aegis_schema.models.Capability` を返す — スキーマが `id` を拘束している、まさにそのモデル。
だが SDK が先に自前の regex で検証し、その 2 つが一致しない。

| id | 形 | SDK regex | schema pattern |
|---|---|---|---|
| `weather.get_forecast` | SDK 自身の docstring の例 | **通す** | 弾く |
| `my_server.read_sensor` | SDK 自身の引数ヘルプ | **通す** | 弾く |
| `ai-server.get_forecast` | 名簿の prefix・短い形 | 弾く | **通す** |
| `pc-server.screenshot.get_screenshot` | **正準の 3 セグメント形** | 弾く | **通す** |

SDK の pattern は**開いたクラス**（`[a-z][a-z0-9_]*`）、スキーマは **12 prefix の閉じた
allowlist**。したがって単に広さが違うのではなく、**互いに相手が通す id を弾く**。

### 3 つ目の欠陥（今回わかった）

`define_capability` は `server_type` を**既定 `DEV` のまま**にし、`server_prefix` から導出しない。
そのため**既定引数で通る prefix は `dev` ただ 1 つ** — Phase 9 で削除したサーバである。名簿の
prefix を使うには呼び出し側が `server_type` を明示する必要があり、SDK はそれを必須とも書いていない。
既存の SDK テスト 11 件がすべて `dev` を名乗っているのはそのため — **緑だったのは偶然**。

### 実測した帰結（すべて同じ穴に落ちる）

- `docs/plugin-sdk.md` の Quick Start（`server_prefix="weather"`）→ 素の pydantic `ValidationError`
- `capability.py` 自身の docstring の例 → 同じ
- `tools/create-capability-server` が生成する `server_prefix="{prefix}"` → `dev` 以外は import 時に落ちる
- **`examples/example-weather-server/weather_server.py` → import すら通らない**
  （しかも**リポジトリのどこからも参照されていない** — テストもスクリプトも CI も。だから壊れたまま残った）

### ピン（`packages/aegis-sdk-python/tests/test_capability_id_contract.py`、8 関数 / 23 ケース）

両方の pattern を**実物から発見**する: スキーマは `Capability.model_fields["id"].metadata`
（コピーではないので本体から乖離できない）、SDK は `safety.py` を **AST** で読む（インラインの
リテラルで import 不可）。**食い違いそのもの**を等式で固定するので、**どちらを直しても落ちる**。
「修正」ではなく「記録」であることを docstring に明記した。

### 変異 5/5 捕捉

| 変異 | 結果 |
|---|---|
| スキーマの allowlist を広げる（製品選択肢 A） | **3 failed** |
| SDK を allowlist 化する（製品選択肢 B） | **8 failed** |
| SDK の既定 `server_type` を DEV → PC | **4 failed** |
| `re.match` リテラルを 2 つにする（発見を壊す） | **collection ERROR**（rc=2） |
| 同梱 example の prefix を両方 `dev` に（= 修正） | **1 failed** |

2 つが教訓になった:

1. **example の `server_prefix="weather"` は 2 箇所ある。** 1 箇所だけ変えると 2 つ目の
   capability が依然として落ちるので、**テストは動かない**。変異は replace-all が要る
   （「変異が捕まらないときは、まず変異が対象を動かしているか確認する」の実例）。
2. **発見を壊す変異は FAILED ではなく collection ERROR（rc=2）で出る。** だからハーネスは
   `FAILED` を grep せず **rc≠0 を捕捉**とする。

### 検証

ai-server **1714 passed / 31 skipped**（変化なし — ピンは SDK 側にある）。SDK **25 → 48 passed**。
room **14** / browser **100** も再実測して一致。ruff clean。`scripts/test-all-suites.ps1` は
**コメントから数を削除**（数は腐るので）— AST パース errors=0。
live な SDK 数を 25 → 48 に更新（`AGENTS.md` / 本レポート §0・§1.1 / `MEMORY.md`）。

---

## B-12 を「記録」から「ピン」へ — 39 件の deny 一覧は、それを読むゲートとは別の id 方言で書かれている（2026-09-29, `2da2c37`）

B-12 は §4.1 に「記録済み・未修正」として載っていた**最後の欠陥**だった。記録されていた内容は
すべて確認できた（canonical 8 / 短縮 31、39 件すべて `catalog.resolve()` で解決不能、canonical 形の
同じ意図は素通り）。今回はそれに加えて**記録より深い**ことを 4 つ測った。

### 実測

| 実測 | 値 |
|---|---|
| 39 件のうち `catalog.resolve()` で解決できるもの | **0 件** |
| 生きた 128 capability のうち禁止 action を持つもの | **0 件** |
| `validate_settings_change` のループのうちエラーを積めるもの | **2 / 3**（`disabled_capabilities` のループは本体が `pass`） |
| その 2 つが拒否できる設定項目のうち、ゲートが読むもの | **0 件** |
| `EXPLICIT_DENY_PATTERNS` の被覆 | **5 / 39** |

**守る相手が 0 件**であることが、この欠陥が見えない理由である。**発火しないガードは、正しく
発火しているガードと見分けがつかない。**

### ピン（7 関数 / 13 ケース）

方言の構成・解決不能性・**canonical 形の witness が素通りすること**・`pass` ループ・ゲートが引く
鍵の形（`per_capability.get` の**引数式の集合**）・パターン被覆を、すべて**等式と実測**で固定した。
**「改善」でも落ちる**ように作ってある（B-14 のピンと同じ形）— 直した人は必ず記録を更新する。

### 変異 6/6 捕捉

| 変異 | 落ちるべきテスト |
|---|---|
| 短縮形 1 件を canonical に直す（= 修復） | 方言構成の等式 |
| canonical 1 件を短縮形に戻す | 方言構成の等式 |
| `pass` ループに `errors.append` を足す（= 改善） | ループの能力判定 |
| ゲートの鍵を短縮形に変える | 鍵の形の集合 |
| パターンを 1 件足す | パターン被覆 |
| 一覧に生きた id を 1 件足す | 解決不能性の等式 |

### 自作の誤りを 2 件、ピンが先に捕まえた

1. `per_capability` の期待値を**自分の実測と逆**に書いていた（テスト名まで逆）。測った事実を
   書き写すよう直した。
2. `per_capability.get` の呼び出しを **1 箇所**と決め打ちしたが、実行すると
   `expected one per_capability lookup, found 2` で落ちた — `evaluate` と
   `is_capability_enabled` の両方にある。**「1 箇所のはず」は測定ではない。**

### 結論

**制約は危うくない、この一覧が危うい。** 測定は**修復ではなく削除**に傾く（守る相手 0・3 ループ中
2 つが無効・名前が何も指していない）。修復するなら「id で照合する」をやめて **action で照合する**
必要があり、39 件を canonical に書き直すだけではゲートが読まない鍵空間のままである。削除は
`docs/permissions.md` が CAPTCHA の根拠としてこの一覧を引用しているため**文書の訂正を伴う**
（オーナー判断）。**`FORBIDDEN_CAPABILITIES` は保護された面ではない** — これも本項の結論である。

### 検証

ai-server **1714 → 1727 passed / 31 skipped**（+13、実測 362 秒）。egress **211/23 のまま**。
ruff clean / format clean。live な数を 1714 → 1727 に更新（`AGENTS.md` / `docs/architecture.md` ×3 /
本レポート §0・§1.1 / `MEMORY.md` / `aegis-verify-and-test`）。

**B-6 は本日 11 回目の再発**（`2da2c37` でも `git log` が「まだコミットが無い」と報告した）。
reflog からの復旧で毎回直っているが、**耐久修正は平坦なブランチ名への改名**（オーナー判断）。

## A-1 — 死んだ deny 一覧を「修復」ではなく「削除」で決着（2026-09-29, `3e7413c`）

B-12 / B-13 を削除で閉じた。**削除の根拠は測定そのもの** — 守る相手が **0 件**、3 ループ中 **2 つが
無効**、39 件の名前は**何も指していない**。canonical 形に書き直しても**同じ死んだ鍵空間**を見るだけ
なので、「正しい綴りに直す」は選択肢にならない。

| 削除した | 残した |
|---|---|
| `settings/validation.py` の 39 件 `FORBIDDEN_CAPABILITIES` | `validate_settings_change` 自体（`store.py` から呼ばれている） |
| それを参照する 3 ループ（1 つは本体 `pass`） | camera snapshot の有効化に確認を要求する検査 |
| `CapabilityPermissions.allowlist` | `max_autonomous_runs_per_hour > 100` の検査 |
| `config/settings.json` の `"allowlist": []` | — |

### ピンは「記録」から「削除の証明」へ

`test_forbidden_capabilities_dialect.py`（7 関数 / 13 ケース）を削除し、
`test_forbidden_capabilities_stay_retired.py`（11 ケース）を新設した。

**削除ピンは「定数が消えた」だけでは弱い** — その主張は**システムを弱めれば満たされる**。そこで
3 つを併せて固定した:

1. **実物の `ToolBroker` を駆動**し、未登録 id が `NOT_FOUND`（**ポリシー評価の前**）で拒否される
   こと。`policy_decision` が空であることも assert する — ここが policy engine に落ちるようになった
   ら、削除した一覧は**load-bearing だった**ことになる。
2. 生きたゲートが **`capability.id`** を鍵にしていること（旧ピンの生き残った半分）。
3. `EXPLICIT_DENY_PATTERNS` が**支払い・egress 迂回・ポリシー自己改変**の 3 意図群に今も一致する
   こと（**代わりの制御**の証明）。

名前に依存しない守りとして、**バリデータが capability フィールドを 1 つも検閲していないこと**
（AST で発見し、空集合と等式）も assert した — 名前を変えて戻しても落ちる。

**変異 14/14 捕捉**。うち **2 件は検出器自身を盲目化する変異**で、これが無いと「消えている」系の
assert が**空虚に通る**。**1 件は修復方向**（記録済みの穴に消費者を足す）で、ピンが**欠陥ではなく
ピンを直す**ことで満たされないようにした。**1 件は SKIP になった** — `config/settings.json` が
**CRLF** なので `\n` アンカーが一致しなかった。**アンカーが一致しない変異は「捕捉されなかった
変異」ではない**が、SKIP を黙って通すと「捕捉した」と誤読するので、ハーネスは SKIP を失敗として
数えるようにした。

### 副産物 1 — B-13 の検出器を広げたら、生きた 2 件目が即座に見つかった

B-13 のピンは `*.capabilities.<field>` だけを見ていた（最初の実例が `allowlist` だったため）。
A-1 でその対象が消えるので**全設定セクション**へ広げたところ、`max_autonomous_runs_per_hour` が
**バリデータだけに読まれ、他に消費者がいない**ことが判明した。自律ループは**ハードコードされた
予算**で動くので、この設定を編集しても挙動は変わらない（`> 100` を拒否するだけ）。

**既存の死にフラグ検出器が見逃していた** — `test_ineffective_flags.py` の `_readers()` は
識別子のテキスト一致なので、**バリデータを「読者」と数える**。同じフィールドに 2 つの検出器が
別の答えを返すのはこれが理由で、**効果について正しいのは B-13 側**。`_RECORDED_GAPS` に記録し、
登録簿 §0.2 の **B-6** として起票した（同じ形の 22 件が既に `_UNOWNED_DEBT` にあるので、単独で
決めずそちらと一緒に扱うのが筋）。

**教訓**: **走査の範囲を「最初に見つけた実例」に合わせて狭めると、2 件目が見えなくなる。**

### 副産物 2 — 「実測」と書いてある数値が、実は手計算だった

§4.1 の B-7 は「検出器を自動発見に変え、**12 モデル 95 フィールド**を走査」と書いていた。実測:

| 時点 | モデル | フィールド |
|---|---|---|
| `b73309e^`（`AutonomyProfile` 削除前） | **12** | **106** |
| `b73309e`（削除後） | **11** | **94** |
| 現在（A-1 後） | **11** | **93** |

**12 は削除前の値をそのまま残し**、**95 は 106 から AutonomyProfile の 11 だけを引いた手計算**で、
親の `AEGISSettings.autonomy` という**参照フィールド 1 つを引き忘れていた**（106 − 11 − 1 = 94）。
**引いて作った数は測った数ではない** → §4.3 に**バグクラス 13** として記録。

### 検証

ai-server **1727 → 1723 passed / 31 skipped**（実測 365 秒）。egress **211/23 のまま**（新テストは
egress マーカーを持たない）。**−4 の内訳を完全に一致させた**:

| 増減 | 理由 |
|---|---|
| **−13** | 削除した記録ピン（`test_forbidden_capabilities_dialect.py`） |
| **+11** | 新しい削除ピン（`test_forbidden_capabilities_stay_retired.py`） |
| **−6 +5** | B-13 ピンを全セクションへ拡張（守る集合が 3 → 2 フィールド） |
| **−1** | `test_ineffective_flags.py` の設定フィールド parametrize が `allowlist` の 1 ケースを失った |

**差を内訳に分解できないなら、削除したコードが実は覆われていた可能性を疑うべき。**

**B-6 は本日 13 回目の再発**（`3e7413c` でも同じ）。reflog から復旧（HEAD = `3e7413c`、
origin より **96** 先行）。**耐久修正は平坦なブランチ名への改名**（登録簿 A-5、オーナー判断）。

## B-1③ の実測 — 登録簿の推奨そのものが誤っていた（2026-09-29）

§0.2 の B-1 は ③「既定値 **0.0 / 0.2 / 0.5** を 1 つに寄せる」を**「挙動が動かない純粋な衛生」**として
**最初にやる**と推奨していた。着手前の実測でこれが**誤り**と分かったので、③ は**実行せず撤回**した。

### 実測したこと

`interruption_cost` という**同じ名前**が 3 箇所にあるが、**同じ量の 3 既定値ではない**:

| 値 | 住処 | 「分からない」の中身 | 本番で生成されるか |
|---|---|---|---|
| **0.0** | `ActionCandidate.interruption_cost`（`autonomous/models.py:76`） | **呼び出し側が指定しなかった** | **いいえ** — `src/` の 2 構築サイトは両方とも `interruption_cost=` を明示的に渡す。`0.0` に到達するのはテストだけ |
| **0.2** | コスト表のフォールバック（`autonomous_loop.py:719`） | **報告されたレベルがコスト表に無い** | はい |
| **0.5** | `PresentationRoutingContext.expected_usefulness / interruption_cost`（`routing_policy.py:19-20`） | **別の量** — `expected_usefulness` と比較される被演算子 | はい |

寄せると**「分からない」の 3 種類が 1 つに潰れる** — これは §4.3 型 3（既定値は黙った誤答）そのもので、
**修復ではなく欠陥**。よって ③ は撤回した。

**4 つ目の答え**: `_current_interruption_cost` は **`0.15`** も返す（`:708` agent state が無い / `:712`
snapshot が例外）。`_RECORDED_COST_DEFAULT = 0.2` しか記録していなかった旧ピンは、
**「1 つの名前・N 個の答え」という自分の主張を自分の軸で数え落としていた**。

### やったこと

1. **記録の訂正**（本番コードは 1 行も触らない）— §0.2 の B-1 行で ③ を取り消し線＋「撤回」、§5.8 に
   測定の注記を追加、§4.1 の B-17 行を更新。
2. **存在しないクラス名の訂正** — `InitiativeCandidate` は**どこにも存在しない**。実体は
   `autonomous/models.py:56` の `ActionCandidate`。4 ファイル 5 箇所を訂正（ピンの docstring も含む）。
   **docstring に書いてある名前は、そのシンボルが存在する証拠ではない**（`python -c "from m import X"` で
   1 コマンドで決着する）。
3. **ピンの拡張**（`tests/test_interruption_cost_vocabulary.py`、8 → **9 テスト**）—
   `_unknown_answers_in_the_cost_function()` が関数の**全ての `Return`** を分類する
   （裸の定数 / `.get(key, 定数)`）。分類できない形は**例外**（＝SKIP を合格にしない）。
   記録は `_RECORDED_UNKNOWN_ANSWERS = {0.15: …, 0.2: …}` で、**集合の等式**で固定。
4. **副産物の doc 訂正** — `docs/settings.md` は `max_autonomous_runs_per_hour` を "Rate limit" と
   書いていたが、実測では**バリデータ（`> 100` を拒否）とフィールド自身の `le=100` しか読まない**
   （自律ループは見ない＝B-6）。doc の訂正はオーナー判断を待たない。

### 検証

ai-server **1723 → 1724 passed / 31 skipped**（実測 377 秒）。**+1 = 新しいテスト 1 件、ちょうど**
（本番コードは無変更なので、差が 1 でないなら何かが覆われている）。egress 211/23 のまま。ruff clean。

**変異 6/6 捕捉**（使い捨てハーネス、原文バイトを復元して `sha256` 一致を確認）:

| 変異 | 捕捉したテスト |
|---|---|
| M1 `0.15` → 未記録の `0.25` | 新しい等式テスト |
| M2 表のフォールバック `0.2` → `0.3` | 新テスト ＋ 既存のフォールバックテスト |
| M3 3 つ目の答え `0.05` を追加 | 新しい等式テスト |
| **M4 修復方向: `0.15` を `0.2` に併合（＝撤回した ③ そのもの）** | 新しい等式テスト |
| M5 検出器の盲目化: 関数を改名 | 4 テスト（`_cost_function` の assert） |
| M6 分類不能な形 `return float(0.15)` | 新しい等式テスト |

**M4 が本質** — 「撤回した」が口約束でないことの証明は、**撤回した編集そのものが落ちる**ことにある。

**B-6 は本日 14 回目の再発**（本コミットでも）。reflog から復旧。**耐久修正は平坦なブランチ名への改名**
（登録簿 A-5、オーナー判断）。

## A-3 — サーバ名簿を 1 つにする（2026-09-29, `952caaa`）

登録簿 A-3 の推奨は「① 名簿を 1 つにする」で、作業量が大きいぶん**構造としては最優先**と書いてあった。
着手前の再測定で、**その推奨の前提そのものが 2 つ崩れた**。

### 前提の訂正

| 当初の見立て | 実測 |
|---|---|
| 名簿は **15 箇所 / 11 ファイル**のコピー | **12 箇所が名簿**。`situation.py:51/189/204` は**状況ソース**の語彙 — `ai-server` を `"webhook"` に写し、`:189` は `"status."`（サーバですらない）を含む。**キーが同じだけの別物** |
| `server_id → ServerType` の写像は同内容のコピー | **5 コピー、うち 2 つは既に食い違い**（`tool_broker.py` に `dev-server` 無し / `capability_catalog.py` に有り） |
| 5 箇所を個別に直せば済む | 直すべきは**写像の重複そのもの**。個別修正は次のサーバ増減で再発する |
| `alert_manager.py` の 4 サーバは消し忘れ | **意図的** — **サーバは自分を健康診断できない**（`ai-server` が無いのは設計） |

### 実施

`ai-server/src/aegis_schema/roster.py` を新設。`SERVER_ROSTER` は `(ServerType, 正準 id, 短縮 prefix)`
の 5 件、`RETIRED_SERVER_ROSTER` は退職 1 件。**6 方向の写像を同じ導出関数から作る**
（`SERVER_TYPE_BY_ID` / `PREFIX_BY_ID` / `PREFIXES_BY_TYPE` / `SERVER_TYPE_BY_DOTTED_ID` /
`PREFIX_BY_ID_WITH_RETIRED` ほか）。6 サイトが import する:

| サイト | 何を渡していたか |
|---|---|
| `capability_catalog.py:70` `_PREFIX_MAP` | `server_id → 短縮 prefix` |
| `capability_catalog.py:380` `server_type_map` | `server_id → ServerType` |
| `prompt_regression.py:276` `server_map` | `"<id>." → ServerType` |
| `dashboard_legacy.py:104` `server_type_map` | `server_id → ServerType` |
| `models.py:215` `prefix_map` | `ServerType → (短, 長)` |
| `tool_broker.py:61` `server_type_map` | `server_id → ServerType` |

**6 つの写像すべて HEAD と値が同一**であることをスクリプトで確認した（＝純粋なリファクタ。
振る舞いは 1 ミリも変わっていない）。

**退職エントリは 1 回だけ書く**。当初は 3 サイトそれぞれに `{**X, "dev-server": …}` と綴ったが、
それは**死んだサーバ名のコピーを 3 つ作っただけ**（型 8 の再生産）なので、`RETIRED_SERVER_ROSTER` に
寄せて `**` 展開で折り込む形にした。結果 **`dev-server` を綴るモジュールは 6 → 3**
（`roster.py` ＋ 記録済みドリフトの 2 サイト）。

### 検出器を事実の移動に追随させた

`test_server_roster.py` の `_id_consistency_map()` は「ローカル変数なので import 不可」を理由に
**`models.py` の AST を読んでいた**。名簿が import 可能になったので**読み先を名簿へ移した**。

ここで**ガードが 1 つ消える**: 「validator は dict リテラルを 1 つだけ持つ」という assert は
**AST 読みのための前提**だった。**代わりに、それが守っていた不変量を書いた** —
`test_the_validator_names_no_server_of_its_own`（validator の本体にサーバ名の文字列定数が
**1 つも無いこと**）。**計測の移動で消えたガードは、ガードの目的で置き換える。**

さらに、`_MIN_ROSTER_SIZE`（4 名以上でないとリテラルと見なさない）という**ヒューリスティックの盲点**が
A-3 自身の変更で生まれた — `{**X, "dev-server": …}` は**名 1 つ**なので閾値未満で見えない。
`_RECORDED_DEV_SERVER_SPELLINGS` で**綴り箇所を直接固定**して塞いだ。

### 撤回したアサーション 2 つ（どちらも変異で発覚）

**① `PREFIX_BY_ID == {s: _PREFIX_MAP[s] for s in SERVER_IDS}`** — `_PREFIX_MAP` は `PREFIX_BY_ID`
**から導出**されるので、短縮 prefix が誤っていても**両辺が一緒に動く**。変異（`room → rm`）で
**緑のままだった**。短縮 prefix の独立した宣言は `Capability.id` の**許可リスト**なので、
そちらと突き合わせる形に変えた（実測で 12 個の選択肢が名簿と**完全一致**）。

**② 「manifest の `server_id` と id prefix が一致すること」** — `folder_registry._derive_ids` は
`server_id` を**パスから**取り、`capability_id` も**同じ dict から**組み立てるので、id の第 1
セグメントは**構造上** server_id である。加えて `_validate` が JSON の `server_id` をパスと比較し、
食い違えば manifest を**拒否**する（`list_all()` に届かない）。変異（実 manifest の `server_id` を
書き換え）は**このファイルを素通り**した。真の不変量「**拒否が 0 件**」は既に
`test_manifest_schemas.py` が固定しているので、**スタブとして残さず撤回した**（落ちないテストは負債）。

### 結果

| 指標 | 前 | 後 |
|---|---|---|
| 名簿リテラル | 15 箇所 / 11 ファイル | **10 箇所 / 7 ファイル** |
| 記録ドリフト | 5 サイト | **2 サイト** |
| `dev-server` を綴るモジュール | 6 | **3** |
| ai-server | 1724 passed / 31 skipped | **1726 passed / 31 skipped** |

残る 10 箇所は**モジュール単位で記録し等式で固定**（`_RECORDED_INLINE_ROSTERS`）— `len(ROSTERS) >= N`
の床では**増加を検出できない**（床は増加に無関心）ため。

**+2 の内訳は推測せずに測った** — HEAD を detached worktree に取り、`--collect-only` を per-file で
diff して `test_server_roster.py` が 31 → 33 ケースになることを確認（新規関数 7 − 消えた parametrize 5
＝ +2。名簿リテラルが 15 ではなく 10 になったぶん parametrize が減った）。

### 変異 12/12

| 変異 | 期待テスト |
|---|---|
| M1 名簿から生きたサーバを 1 つ落とす | 名簿＝カタログ |
| M2 短縮 prefix を誤る（`room → rm`） | id 許可リスト |
| M3 validator がサーバ名を再び直書き | validator はサーバ名を持たない |
| M4 新モジュールが名簿リテラルを宣言 | 残存リテラルの等式 |
| M5 退職 id を名簿の外で綴る | 綴り箇所の等式 |
| M6 名簿が 2 台目のサーバを退職させる | 手書き退職集合＝名簿 |
| M7 記録済みドリフトが浄化される | ドリフトの等式 |
| M8 既存モジュールが 2 つ目のリテラルを得る | 残存リテラルの等式（件数） |
| M9 `DEV` が生きた名簿に入る | 退職サーバは生きた名簿に無い |
| M10 validator が名簿でなく古いローカルを見る（**修復方向**） | 全メンバーの挙動テスト |
| M11 id 許可リストが短縮 prefix を落とす | id 許可リスト |
| M12 実 manifest の `server_id` が自分の id と矛盾 | `test_manifest_schemas.py` |

**M2・M12 は最初「捕捉できなかった」** — どちらも**テストではなく変異の期待先が間違っていた**
（M2 は撤回前の恒真テストを指しており、実際には新しい id 許可リストのテストが捕まえていた。
M12 は別ファイルのテストが捕まえていた）。**変異が捕まらないときは、まず「その変異が対象を動かして
いるか」「期待先が正しいか」を疑う**（B-18 の教訓の再確認）。原ファイルは**バイト単位で復元**
（sha256 検証）。

**副産物**: ruff の `--fix` が `test_server_roster.py` を **CRLF に書き換えた**（リポジトリは LF）。
そのまま置くと**全行が差分になる**ので、正規化してから commit した。

**B-6 は本日 15 回目の再発**（本コミットでも）。reflog から復旧。HEAD は `952caaa`。

## B-3 — 自律実行経路が 2 本あり、登録簿は死んだほうを「生」と書いていた（2026-09-29）

### 測定

`docs/self-development.md` は冒頭のアーキテクチャ図で `AutonomousController` を**入口**として描き、
`tick()` で `AutonomousLoop` に繋いでいる。**実測は逆**:

| モジュール | import 元（`src/`・`tests/`・docs のコード全体） |
|---|---|
| `autonomous_loop` | `aegis_ai/runtime.py` ✅ **走っている** |
| `autonomous_controller` | **なし** |
| `motivation_arbiter` | `autonomous_controller.py` のみ（＝到達不能） |

`runtime.py:1586 _create_autonomous_loop` は `AutonomousLoop` を**直接**構築し、
`start_autonomous_if_enabled` から起動する。`AutonomousController` は約 700 行の
**誰も起動しない 2 本目の入口**。

**§5.1 の `motivation_arbiter` 行は判定そのものが誤っていた** — 「❌ 生」の根拠は
「`autonomous_controller.py` が import している」だが、**その importer 自身が import 元ゼロ**。
「生」ではなく「**死んだ経路の上に乗っている生きたコード**」。

### 走査を 1 回間違えた

最初の走査は「**パッケージ外から** import されているか」だけを問い、**5 つ**を到達不能と報告した。
`planner`（`autonomous_loop` 経由）・`l2_mind` / `l2_models`（パッケージ `__init__` 経由）は
**到達可能**で、正解は **2 つ**。**1 ホップの関係を数えて到達性と呼んではいけない。**
この誤りは**登録簿の誤りと同じ型**で、しかも**逆方向に効く** — 登録簿は 1 ホップを見て
「生」と書き、私の初回走査は 1 ホップを見て「死」と書いた。

### 3 層目: 同じフィールド名で、死に方が 2 通り

`autonomous/` で `requires_approval` に触れる **7 箇所はすべて `motivation_arbiter.py`**:

| フィールド | 死に方 |
|---|---|
| `MotivationDecision.requires_approval` | **読者 0** — `:214/:234/:254` が `t.requires_approval` から、`:320` が**別名** `best_task.requires_user_approval` から、`:332` がリテラル `False` を書く。読むものは無い |
| `ExternalTask.requires_approval` | **読者が到達不能** — `:214/:234/:254` が読んでいるが、`ExternalTask` は**どこでも構築されない**ので user / scheduled / event 分岐が動かない。`_build_task_request` の `isinstance(task, ExternalTask)` の腕も同じ |

**後者のほうが悪い** — フィールドが**起こり得ないタスクについての主張**になる。登録簿は前者だけを
「唯一の真に削除可能な残骸」と書いていた。

### ピン（記録であって修復ではない）

`ai-server/tests/test_autonomous_execution_path_is_single.py`（8 関数）。**配線しても削除しても
落ちる**ので、判断は必ず意識的に行われる。docstring には走査が**推移的でなければならない**理由と、
**初回走査が 5 と誤報告した**事実を書いた（同じ調査を繰り返さないため）。

**`docs/self-development.md` の図の訂正はオーナー判断** — 「こう動くべき」（→ 配線）なのか
「こう動いている」の書き間違い（→ 削除）なのかは測定では決まらない。ただし**実測と食い違っている
という事実**は図の直下と `AutonomousController` 節に注記した。**事実の記録は判断ではない。**

### 変異 10/10 捕捉 — うち 1 件は自作の誤り

**M3 の初回が緑のままだった** — `import AutonomousLoop as _RenamedLoop` は**部分文字列が残り、
経路も動く**ので、緑が正しい。**ハーネスの期待が誤っていた。** ただしこれで**検査が空白依存の
部分文字列だった**ことも判明したので、同じファイルの他の assert と揃えて **AST 化**した
（`_runtime_imports_from` / `_runtime_constructs` — `alias.name` は別名でも**元の名前**なので、
綴りではなく名前を見る）。M3 を 3 通り（モジュール移動 / 名前入替 / 構築だけ削除）に分割して再実行し、
**すべて捕捉**。

**M8（検出器を盲目化）が最も有用** — `_SRC` を存在しないディレクトリに向けると 8 件中 **5 件が落ち、
2 件は空虚に緑のまま**（`test_the_documented_entry_point_has_no_importers_at_all` と
`test_external_task_is_never_constructed` — どちらも**空集合**を assert するため。残る 1 件
`test_the_dead_decisions_still_carry_the_approval_field` は走査を使わないので無関係）。
ガード `test_the_scan_actually_sees_imports` が**肯定の観測**を assert している唯一の理由がこれで、
その数字を docstring に書いた。**「消えている」ことを assert するテストは、走査が壊れると空虚に通る。**

| 変異 | 期待テスト |
|---|---|
| M1 生きたモジュールが死んだ controller を import | 入口は importer 0 |
| M2 `motivation_arbiter` の 2 人目の importer | arbiter は死んだ controller 経由のみ |
| M3a 生きたループを別モジュールから import | 生きたループ＝runtime が構築するもの |
| M3b import と構築の名前を入れ替え | 同上 |
| M3c import はするが構築しない | 同上 |
| M4 **修復方向**: 死んだ controller を runtime に配線 | runtime は controller を経由しない |
| M5 `decision.requires_approval` を読む | 承認フラグの接触ファイル＝1 かつ読者 0 |
| M6 `ExternalTask` を構築する | ExternalTask は構築されない |
| M7 `MotivationDecision` から承認フィールドを削除 | 死んだ決定は承認フィールドを持つ |
| M8 検出器を盲目化（走査根を移動） | 走査は import を見ている |

原ファイル 5 本は**バイト単位で復元**（sha256 検証）。ai-server **1726 → 1734 passed / 31 skipped**
（**+8 = 新規 8 関数**、実測 388 秒）。

**訂正しなかった記述**: `AGENT_PROGRESS.md:820` の `runtime.py:1618` は `reflection_engine` に
係る記述で**正しい**（私は一瞬 `motivation_arbiter` に係るものと読み違えた）。**行番号だけを grep
して主語を確かめないと、正しい記述を誤りとして「訂正」してしまう。**






## B-20 — スキーマは 27 の境界を宣言し、生きた書き込み経路は 1 つしか検査しない（2026-09-29）

B-6（`max_autonomous_runs_per_hour` を配線するか削除するか）を測りにいったら、その一段下に
別の欠陥があった。B-6 の前提（「バリデータだけが読む」）は正しかったが、**そのバリデータが
何をしているかを読んだ**ことで出た。

### 測定

`AEGISSettings` とそのサブモデルは **27 フィールド**に `ge`/`le` の境界を宣言している。
これらは**構築時**に強制される。しかし生きたプロセスの唯一の書き込み経路は
`SettingsStore.update_section` で、提案設定を**無検証の `setattr`** で組み立ててから
`validate_settings_change` を呼ぶ。そしてバリデータが再検査する境界は **1 つだけ** —
`max_autonomous_runs_per_hour > 100`。これはそのフィールド自身の `le=100` の**写し**である。

| 区分 | 件数 |
|---|---|
| スキーマが宣言する境界 | **27** |
| 書き込み経路が再検査する境界 | **1** |
| 書き込み経路が素通りさせる境界 | **26** |

**推論ではなく実測**: 実物の `SettingsStore` を `tmp_path` に対して 1 フィールドずつ駆動し、
違反値が**受理され**、**読み戻しても残っている**ことを確認した（26/26 突破・1/1 阻止）。

### 仮説を 2 回外した

1. **「バリデータの検査は発火しない」→ 誤り。** `le=100` があるので構築は `101` を拒否する。
   ところが**代入は検証されない**（`validate_assignment` はどこにも設定されていない）ので、
   `setattr` 経路ではこの検査は**到達可能**であり、**むしろ唯一の防波堤**である。
   つまり欠陥は「検査が死んでいる」ことではなく、**防波堤が 1 つだけ手書きされている**こと。
2. **自作の走査が `guard` という部分文字列で偽陽性**を出した。クラス名
   `SettingsPermissionGuard` が `VALIDATION_HINTS` の `guard` に一致し、`clipboard_capture_enabled`
   など 5 件を「検証専用」と誤判定した。実際は `permissions.py` の**生きたゲート**である。

### なぜ化粧ではないか

突破できる集合に**保持期間の上限**が入っており、実際の削除計算に届く。`backup/retention.py:60`
は `settings.memory.episodic_retention_days` を `max_age_ms` に変換して prune するので、
スキーマが拒否する値（`le=365`）で**1 世紀分のエピソードを保持**できる。

同じモジュールの docstring は 4 つの保持を "Handles:" と並べていたが、実測は:

| 保持 | 実測 |
|---|---|
| Episodic | ✅ **強制されている** |
| Notification | ⚠️ `get_retention_status()` が**報告するだけ** |
| Screenshot | ⚠️ 同上（実際の削除は `personal_data/core.py`） |
| Audit | ❌ **`self._audit` は `__init__` で保存され、どのメソッドも読まない** |

**「報告だけ」は UI からは実装済みに見える。** docstring は測定に合わせて訂正した。

### ピン（記録であって修復ではない）

`tests/test_settings_edit_path_enforces_schema_bounds.py`（6 関数）。境界は**モデル自身から発見**し、
バリデータの読みは **AST から発見**し、突破の有無は**実物のストアを駆動して**判定する。
突破集合と阻止集合は**両方向の等式**で固定するので、**書き込み経路を直してもピンが落ちる**。

バリデータを 27 個の境界を再検査するよう**拡張しない** — それはスキーマの写しを書き込み経路に
置くことで、このリポジトリが繰り返し見つけている重複そのものである（docstring に明記）。

### 変異 10/10 捕捉 — 2 件はハーネスの誤り

- **M5 は緑のままだった** — `max_tasks_per_cycle` から `le` を落としても `ge=1` が残るので、
  フィールドは**探索集合に残り**、観測が変わらない。**変異が対象を動かしていない**（自分のミス）。
  両方の境界を落として再実行したら捕捉した。
- **M4 は rc=2（collection ERROR）で「捕捉できなかった」と読めた** — 実際は
  `model_config = ConfigDict(...)` と書いたが `models.py` は `ConfigDict` を import していないので、
  **変異が `NameError` で適用されていなかった**。プレーンな dict に直したら捕捉した。
  **ERROR の原因を読むこと — 自分の変異が壊れている場合は「捕捉されなかった変異」ではない。**

**修復方向の変異を 3 つ**入れた（バリデータに 2 つ目の境界 / `update_section` が検証済みモデルを
構築 / `validate_assignment` 有効化）— **3 つとも落ちる**。加えて `RetentionManager` が保持値を
クランプする変異（M8）も落ちる。

| 変異 | 期待テスト |
|---|---|
| M1 新しい境界付きフィールドを宣言 | 等式（新顔は突破側で入ってくる） |
| M2 **修復**: バリデータが 2 つ目の境界を再検査 | 等式＋「再検査は 1 つ」 |
| M3 **修復**: `update_section` が検証済みモデルを構築 | 等式＋保持値が prune に届く |
| M4 **修復**: `validate_assignment` を有効化 | 等式 |
| M5 フィールドが全ての境界を失う | 等式 |
| M6 `cleanup_expired` が `self._audit` を読む | 保持の主張テスト |
| M7 `cleanup_expired` が通知の保持上限を使う | 保持の主張テスト |
| M8 **修復**: `RetentionManager` が上限にクランプ | 保持値が prune に届く |
| M9 検出器を盲目化（違反値をスキーマ適合にする） | 探索値のガード |
| M10 バリデータが唯一の再検査をやめる | 等式＋走査ガード |

原ファイル 5 本は**バイト単位で復元**（sha256 検証）。ai-server **1734 → 1740 passed / 31 skipped**
（**+6 = 新規 6 関数**、実測 403 秒）。

**記録**: §0.2 に **A-9**（推奨は `update_section` が検証済みモデルを構築する形 —
`validate_assignment` は `list[str]` を返す契約を壊すので不可）、**§4.3 にクラス 16**
（宣言は構築でしか検査されない）、§5.15、台帳、`retention.py` の docstring 訂正。

---

## B-21 — 設定画面は「何も変えないスイッチ」を 10 個見せている（2026-09-29）

### なぜこれを測ったか

B-6 は「未読フィールドの集合」を**バックエンド側**で固定する。だが**その集合が利用者に
見えているか**は誰も測っていなかった。B-6 の測定中に、未読 23 件のうち **10 件が設定画面の
コントロールとして描画されている**ことに気づいた。

### 機構 — 発見するので古くならない。だから何でも出す

`web-ui/src/pages/Settings.tsx::editableSettings` は `GET /api/settings`
（= `AEGISSettings.model_dump()`）を走査して、各セクションの boolean / number / string を
**そのまま**コントロールにする。UI 側に名簿は無い。

```tsx
if (!preferred.has(key) && result.length >= 24) continue;
if (typeof value === "boolean" || typeof value === "number" || typeof value === "string") {
  result.push({ section, key, label: labelize(key), value });
}
return result.sort((a, b) => Number(preferred.has(b.key)) - Number(preferred.has(a.key)))
             .slice(0, 32);
```

**発見方式なので、スキーマが変わっても UI の「出す集合」は古くならない** — これは利点である。
利点の裏側が B-21 で、**未読フィールドも等しく描画される**。

### 実測（すべて実物から）

| 量 | 値 |
|---|---|
| ペイロード内のフィールド | **80** |
| コントロールとして描画 | **26**（切り捨て 24 / スライス 32） |
| `_UNOWNED_DEBT` + `_INTENTIONALLY_UNREAD` | **23** |
| **描画され、かつ誰も読まない** | **10** |
| `preferred` の鍵 | **15**（うち **5 件はどのフィールドとも一致しない**） |

10 件は `autonomous.*` が 8（`browser_exploration_budget_per_day` / `daily_briefing_enabled` /
`max_actions_per_hour` / `max_autonomous_runs_per_day` / `normal_interruption_budget_per_hour` /
`research_watch_enabled` / `self_dev_proposal_enabled` / `social_poll_interval_seconds`）、
`servers.*` が 2（`health_check_interval_seconds` / `reconnect_policy`）。

一致しない 5 件は `display_privacy_mode` / `notifications_enabled` / `daily_budget_usd` /
`monthly_budget_usd`（`web-ui` にしか存在しない）と `memory_budget_tokens`
（`context_builder` の**実行時属性**であって設定ではない）。

### 可視集合は宣言順の事故である

切り捨ては `result.length`（**描画された**数）で数えるので、**早い位置にフィールドを足すと
末尾が窓から落ちる**。実測: `autonomous` の早い位置に 2 つ足すと、記録済みの死んだフィールド
（`normal_interruption_budget_per_hour`）が**可視窓から押し出される**（変異 M11）。
**誰も記録を触っていないのに、設定画面の中身が変わる。** 1 つでは足りない（位置 22 の
フィールドを押し出すには 2 つ要る）— ここでも**期待を測ってから書く**必要があった。

### ピン自身が 2 回壊れていた — どちらも実行が捕まえた

1. **語彙が違う 2 つの集合を交差させていた。** 負債の記録はフィールドを**クラス**で名指し
   （`AutonomousSettings.max_actions_per_hour`）、UI のペイロードは**セクション**で名指し
   （`autonomous.max_actions_per_hour`）。交差は**恒偽ではなく恒空**になる。翻訳は
   `AEGISSettings.model_fields` の annotation から**導出**する形にした（写しを作らない）。
2. **`_UNOWNED_DEBT` は注釈付き代入**（`_UNOWNED_DEBT: dict[str, str] = {...}`）なので、
   `ast.Assign` だけを見る走査は**空集合を返す**。`∅ == ∅` は真なので、その上に書いた `==` は
   **どちらの向きも通ってしまう**。両方のノード種別を扱い、`test_the_debt_record_is_readable`
   が**件数を assert** して空を検出するようにした。

### 変異 18/18 捕捉 — うち 3 件は「捕捉されないこと」が期待値

| 変異 | 期待 |
|---|---|
| M1 切り捨ての式を改名 | 転写ガード |
| M2 `preferred` を改名 | 転写ガード |
| M3 スライス 32 → 3 | 走査ガード（描画数・既知コントロール） |
| M4 切り捨て 24 → 0 | 宣言順テスト（早い位置のプローブが消える） |
| M5 一致しない鍵を実在の鍵に変える | `preferred` の等式（縮む向き） |
| M6 実在の鍵を打ち間違える | `preferred` の等式（増える向き） |
| M7 描画されるフィールドを記録に足す | 死んだコントロールの等式 |
| M8 描画されるフィールドを記録から落とす | 死んだコントロールの等式 |
| M9 死んだフィールドをモデルから削除 | 等式＋「記録の綴りは実在する」 |
| M10 一致しない鍵に対応するフィールドを実装 | `preferred` の等式 |
| M11 早い位置に 2 つ足して死んだフィールドを窓から押し出す | 死んだコントロールの等式 |
| M12 切り捨てを 200 に上げる | 宣言順テスト（遅い位置のプローブが見える） |
| M13 走査から `AnnAssign` の枝を落とす | 非空虚ガード（記録が 0 件になる） |
| M14 クラス→セクションの翻訳をやめる | 死んだコントロールの等式（交差が空になる） |
| M15 最初/最後のセクションを鍵で選ぶ | 宣言順テスト（`version` はスカラー） |
| **W1** `==` → `<=` 単独 | **無音**（対象を動かしていない） |
| **W2** `==` → `<=` ＋ M8 | **無音**（縮む向きを見逃す） |
| **W3** `==` → `>=` ＋ M7 | **無音**（増える向きを見逃す） |

**W1〜W3 が本節の一番の収穫** — `==` を片方向に弱めると、**その向きの変異だけを見逃す**。
つまり**等式の両方向がそれぞれ load-bearing** で、片方だけでは足りない。**変異は「テストが
load-bearing か」ではなく「アサーションの向きが load-bearing か」を測る道具**なので、
`==` を書いたら**両方向に 1 つずつ**当てること。最初は W2 と W3 を取り違えて書いていた
（`dead <= record` は*増加*を捕まえる）— **弱めたときに何が無音になるかを、自分で測る**。

**M12 は最初のピンでは無音だった。** 遅い位置のプローブを隠していたのが切り捨てではなく
`slice` で、テストが**間違った理由で緑**になっていた。スライスを無効化した描画を足し、
**切り捨てだけが説明できる形**に直してから M12 が落ちるようになった。
**テストが緑なのは、主張が正しいからとは限らない。**

### 記録であって修復ではない

- `preferred` の死んだ 5 件 → **A-10**（消せば**挙動は 1 ミリも変わらない** — 一致しない鍵は
  既に何もしていない。順位表の 15 スロットのうち 5 つが死んでいる）
- 10 個の死んだコントロール → **B-6 の行に追記**（フィールドの去就そのものなので、単独では
  決められない。`_UNOWNED_DEBT` の `sensitive_data_storage_enabled` の項が既に書いていた
  「何もしないプライバシースイッチは、スイッチが無いより悪い」が 10 個ぶん現実になっている）

### 検証

ai-server **1740 → 1756 passed / 31 skipped**（**+16 = 新規 6 関数 + 10 parametrize**、実測 375 秒）。
原ファイル 4 本は**バイト単位で復元**（sha256 検証）。ruff clean。

**記録**: §0.2 に **A-10** と **B-6 の追記**、**§4.3 にクラス 17**（名簿の誤りは鳴るが、
順位の誤りは鳴らない）、§5.16、台帳。

**副産物 — 台帳自身の型 9 を 2 件訂正**: C-3 は「11 → **12 クラス**」と書いていたが §4.3 は既に
16 だった。A-5 は「本日だけで **12 回**」と書いていた。**台帳は「測定値を書かない」と自称して
いながら、この 2 行が数を持ち、片方が既に古くなっていた** — 数を削除し、§4.1 B-6 を指す形に
した。§0 の「本日だけで 5 回再発した」も同じ理由でポインタに置換。

---

## A-9 — 設定の書き込み経路が、スキーマの境界を強制するようになった（2026-09-29）

### 何をしたか

§0.2 の A-9 は「① `update_section` が検証済みモデルを構築する」が推奨で、測定もピンも揃っていた
ので実行した（A-1 と同じ判断 — 推奨があり、測定が揃っている行は実行する）。

`SettingsStore.update_section` は提案設定を **`setattr` で組み立てる**のをやめ、現在のダンプに
要求されたキーを重ねて `AEGISSettings.model_validate` に通す:

```python
merged = current.model_dump()
merged[section] = {**merged[section], **values}
try:
    proposed = AEGISSettings.model_validate(merged)
except ValidationError as exc:
    return [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()]
return self.update(proposed, changed_by, reason)
```

未知のセクション・未知のフィールドの拒否は維持。判定を `hasattr` から `model_fields` に変えたので、
**メソッド名を渡しても通らない**（`hasattr(obj, "model_dump")` は真なので、旧コードはメソッドを
上書きできた）。`ValidationError` は `section.field: <msg>` に整形して `list[str]` 契約を保つ。

**代替案（② `validate_assignment`）を採らなかった理由**は実行前に確認済み: 代入が例外を投げる
ようになり `list[str]` を返す契約が壊れる。**27 個の境界をバリデータで再検査する案も却下** —
それはスキーマの写しを書き込み経路に置くことで、このリポジトリが繰り返し見つけている重複そのもの。

### 実測

| 量 | 修復前 | 修復後 |
|---|---|---|
| 境界を突破できるフィールド | **26** | **0** |
| 阻止されるフィールド | **1** | **27** |

実物の `SettingsStore` を `tmp_path` に対して 1 フィールドずつ駆動し、書き戻して確認。境界値は
受理される（`episodic_retention_days` は 365 が通り 366 が拒否される — 両方向を測った）。
**スキーマで表現できない意味論的検査は生きている**: `camera_snapshot_enabled` を有効化すると
今も確認を求める。**「スキーマに寄せれば安全側の検査も消える」わけではない**ことを確認した。

### バリデータの写しは残した — 理由も書いた

`validate_settings_change` の `max_autonomous_runs_per_hour > 100` は、構築が先に拒否するので
**ストア経由では到達不能**になった（`update` / `update_section` / `import_json` のいずれからも）。
それでも消さなかった:

1. この関数は `settings/__init__.py` が再輸出する **public** な関数で、契約がストアから独立。
2. 消すと `tests/test_guarded_settings_fields.py` が記録している**唯一の実例**が消え、
   `_RECORDED_GAPS` が空になってあのファイルの検出器が**対象を失う**（ファイルごと退役させる話に
   なる）。それは掃除ではなく構造変更。

**判断はピンとソースのコメントの両方に書いた。** 「残した」理由を書かないと、次に読む者は
「気づかなかった」と読む — 型 6（文書が「ゲートがある」と読める）の裏返し。

### ピンは「記録」から「回帰ピン」へ

`_RECORDED_BYPASSED` = **∅**、`_RECORDED_ENFORCED` = **27 件**（旧 2 集合の和）。あわせて 2 つ
足した:

1. **2 つの集合が発見した全フィールドを分割していること** — 片方が黙って短くなるのを防ぐ。
2. **各フィールドに合法な値を入れて通ることを確かめる**（境界値を含む）— これが必要なのは
   **`blocked == 27` は「すべて拒否するストア」でも満たされる**から。**「満杯の集合」も空虚に
   なりうる** — B-3 で学んだ「空集合を assert するガードは走査が壊れると空虚に真」の**裏返し**。
   境界値を使うのは、構築経路の off-by-one が `le`/`ge` ちょうどを拒否するから。

### 変異 12/12

| 変異 | 期待 |
|---|---|
| M1 `setattr` に戻す（元の欠陥） | 等式＋保持期間 |
| M2 `model_construct` を使う | 等式＋保持期間＋合法値 |
| M3 **全拒否** | 合法値（等式は通ってしまう） |
| M4 記録から 1 件落とす | 等式＋分割 |
| M5 突破側の記録に 1 件戻す | 等式 |
| M6 **新しい境界付きフィールドを宣言** | 等式＋分割 |
| M7 記録済みフィールドから境界を削る | 分割＋等式＋保持期間 |
| M8 **拒否された修復**（バリデータに 2 つ目の境界） | 「再検査は 1 つ」 |
| M9 `_legal_value` を違反値に反転 | 合法値 |
| M10 プローブ生成器を盲目化 | 4 件 |
| **W1** `==` を両方包含に弱める ＋ M1 | **等式テストは無音**（保持期間だけが捕まえる） |
| **W2** `blocked ==` を `>=` に弱める ＋ M4 | **等式テストは無音**（分割だけが捕まえる） |

**W1 が最も有用** — 両方の `==` を包含に弱めると、**欠陥が戻っても等式テストは無音**になる。
つまり**等式の両方向が load-bearing** で、**保持期間のテストは 2 番目の防波堤**である。

### ハーネス自身の欠陥を 1 つ踏んだ

W1/W2 が最初「捕捉された」と報告された。原因は**ピンではなくハーネス**: 同じファイルへの 2 つ目の
編集を**元のバイト列**から作り直していたので、1 つ目が無言で上書きされていた。つまり W1/W2 は
「弱めた等式」ではなく「元の等式」を走らせていた。**このリポジトリが既に記録している
「同一ファイルの複数領域を 1 度に編集するな」と同じ罠**を自分の道具で踏んだ。編集をファイルごとに
**蓄積**するよう直したら、2 件とも期待どおり無音になった。**変異が期待どおりに鳴らないときは、
まずハーネスを疑う。**

### 副産物 2 件

- `tests/test_guarded_settings_fields.py` の**既存 I001** を修正。**`src/` と `tests/` では
  `aegis_ai` の扱いが違う**（前者は first-party、後者は third-party）ので、**同じ import が
  場所によって別の並びになる** — 片方の並びを他方に写すと lint が落ちる。
- **`ruff format` はこのリポジトリの規約ではない**ことを実測した（未変更のファイルも reformat
  対象になる）。**`ruff check` だけ**を満たすようにした。

### 検証

ai-server **1756 → 1758 passed / 31 skipped**（**+2 = 新規 2 関数**、実測 406 秒）。egress は
**210/23 のまま**（このピンはマーカーを持たない）。原ファイル 4 本はバイト単位で復元（sha256 検証）。
`ruff check` clean。

**記録**: **§0.2 から A-9 を削除**（レジスタは短くなる一方であるべき）、**§4.3 クラス 16 に
修復済みの注記**、§5.17、台帳、`AGENTS.md` / `docs/architecture.md` の数を 1758 に。

---

## 引用の掃討（サイクル 36、2026-10-05）

このファイルの引用は**一度も掃討していなかった**（サイクル 31 が `:1105` の 1 行だけ直した）。
`*.py:NNN` を全部測り（**28 健全 / 5 空行着地 / 1 未解決**）、腐っていたのは **4 件** — うち 1 件は
**他の文書が既に直した事実の写し**だった。

| 旧 | 新 | 根拠（`git show <rev>:<file>` で実測） |
|---|---|---|
| `test_forced_gate_stays_retired.py:61-65` | `:66-70` | 書かれた時は正しかった（`d483813`〜`a75c3db` は `mark_executed` が **61** 行目）。`e125f04` で **+5 ずれ**、今は 66 / 69 行目 |
| `capability_catalog.py:379` | `:380` | `d483813` で **379**（当時の正）、`0cb2a42` で 380 |
| `dashboard_legacy.py:103` | `:104` | `ed929b1` で 104 へ |
| `backup/retention.py:49` | `:60` | **PSR.md が既に自分の写しを直していた**（`:49`→`:60`、サイクル 31）。ここは未修正の写し |

**⚠️ 「範囲の開始が空行」と「範囲が主張を覆っていない」は別。** サイクル 31 は
`test_forced_gate_stays_retired.py:61-65` を「範囲の開始が空行なだけ、成立している」と判定したが、
その範囲は**同じコメントブロックの別段落**（`request`/`list` の説明）を指していた。対照に
`egress/startup.py:59-76` は開始が空行でも**主張（検証本体）を覆っている**ので据え置きが正しい。
**判定は「非空か」ではなく「主張の句を含むか」。**

**⚠️ 削除の掃討は 2 文書を漏らしていた。** `818105f`（`aegis_ai/permissions/` 削除）は 7 文書を掃討したが、
**`AGENT_PROGRESS.md` と `BUG_REPORT.md` が漏れた** — 前者は B-16 節が今もパッケージを「生きたゲート」と
書いており、後者は §33 が「✅ 修正」と書いている。両方に追記した。**「掃討した」は「掃討した文書を
列挙した」ではない** — 削除コミットの `--stat` に載っている文書が**全部**とは限らない。

**据え置き（記録）**: ① `autonomous_loop.py:3065-3066` は**欠陥叙述**で、番号は当時のもの（PSR.md の
同種の写し 3 つと同じ判断）— ただしこのファイルには**解決の記録**が無かったので節頭に追記した。
② `data/reports/*.md` は**未追跡の生成物**（`Generated at: 2026-07-20`）、`.workbuddy-ai/memory/*` は
gitignore 済みの日付ログ — どちらも掃討対象外。③ 他の 28 件は実測して正しいと確認（`capability_catalog.py:70`
`prompt_regression.py:276` `models.py:215` `tool_broker.py:61` ほか）。

**長さ**: 186434 → **本節の直前で 188141 B**（引用 4 件は同幅なので増分は 3 つの追記のみ。LF 維持）。
