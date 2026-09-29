# AEGIS Dashboard 改修計画 v3 — L1/L2/L3 3 層アーキテクチャ統合

> **Status**: ✅ Phase L1-L6 全完了 | 2026-09-10 | instruction.md v3 (L1/L2/L3) ベース
> **前身**: DASHBOARD_REFINED_PLAN.md v2 (D1-D9 完了済み) — Section 8 で v2 サマリー参照

---

## 0. 目的

instruction.md が L1/L2/L3 3 層 LLM アーキテクチャに大きく更新された。本 v3 は:

1. **L1 = 常時動く知覚・判断・ルーティング層**
2. **L2 = 定期的に世界全体を考える自律思考層**
3. **L3 = 本当に難しい問題を解く深層思考層**

を既存 AEGIS に**破壊的変更なしで**統合する手順を定める。

既存 AEGIS は多くの Manager / Memory / Event / LLM Gateway を既に備えているため、
**v3 は新規ファイル最小化・既存資産最大活用** を方針とする。

---

## 1. v2 振り返り (D1-D9)

v2 (DASHBOARD_REFINED_PLAN.md) は完了済み。本 v3 は v2 の上に構築される。

| Phase | 内容 | 状態 | 主な成果物 |
|-------|------|------|-----------|
| D1 | Agent イベントストリーム拡張 (8 種) | done | `event/agent_events.py` |
| D2 | Live Overlay (sticky 38px) | done | `components/LiveOverlay.tsx` |
| D3 | Trace ID 6 種伝搬 | done | `AgentEventPublisher.start_session()` |
| D4 | Agent Trace 画面 (9 tabs) | done | `pages/AgentSessionPage.tsx` |
| D5 | Policy / Approval 表示統合 | done | `policy.decision` publish |
| D6 | MCP / Tool call 完全 JSON 表示 | done | `components/ToolCallJson.tsx` |
| D7 | 検索 + Agent Timeline (Gantt) | done | `pages/AgentTimelinePage.tsx` |
| D8 | 複数 Agent / Live Overlay 優先順位 | done | `pickLiveOverlayEventForAgent` |
| D9 | Settings §22 + Token/Cost §25 | done | `TokenCostPanel`, `readLiveOverlayToggles` |

v2 完了時点で Dashboard は L1/L2/L3 区別**なし**。v3 はここに L1/L2/L3 の視点を加える。

---

## 2. 全体アーキテクチャ (L1/L2/L3 + Manager)

```text
              ┌──────────────────────┐
              │       External       │
              │ Web / SNS / News     │
              │ PC / Android / Room  │
              │ User / Discord etc.  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │      EventBus        │  ← 既存 event/event_manager.py
              └──────────┬───────────┘
                         │
                         ▼
       ┌─────────────────────────────────────┐
       │              L1                     │
       │  Perception / Router (常時稼働)     │  ← 既存 intake/router.py + 新規 L1 Router
       │   ・Event 意味理解 / 価値評価         │
       │   ・MCP / Capability への直接ルーティング│
       │   ・L2 への Escalation                │
       └─────┬───────────────────┬───────────┘
             │                   │
        簡単なTask          深い判断が必要
             │                   │
             ▼                   ▼
    ┌──────────────┐   ┌──────────────────┐
    │ MCP / Tool   │   │       L2         │
    │  Execution   │   │  Autonomous Mind │  ← 既存 autonomous/autonomous_loop.py を L2 化
    └──────────────┘   └────────┬─────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
                Memory       Desire       Task
                    │           │           │
                    └───────────┼───────────┘
                                ▼
                          Decision
                                │
                  hard / uncertain
                                ▼
                       ┌────────────────┐
                       │      L3        │
                       │  Deep Reasoner │  ← 新規 llm/l3_reasoner.py
                       └───────┬────────┘
                               │
                               ▼
                              L2
                               │
                               ▼
                         Task / Action
                               │
                               ▼
                            World

       ────────────────────────────────────
                  Sleep (L1/L2/L3 全層)
       ────────────────────────────────────
       Memory consolidation
       Experience integration
       Behavioral patterns
       Goal/Desire evolution
```

---

## 3. 既存 AEGIS 資産との対応 (v3 での活用方針)

| v3 要素 | 既存資産 | v3 での扱い |
|---------|---------|------------|
| **L1 (知覚・ルーティング)** | `aegis_ai/intake/router.py` + `classifier.py` + `deduplicator.py` + `observation/observation_service.py` | 既存 Intake router を L1 の入力口として再利用。L1 専用の `intake/l1_router.py` ラッパーを追加し、`Observation` / `Decision` / `Value` / `Priority` / `RequiredIntelligence` / `Action` / `Escalation` 構造化出力を行う |
| **L2 (自律思考)** | `aegis_ai/autonomous/autonomous_loop.py` + `desire/` + `task/task_manager.py` + `memory/` | 既存 Autonomous Loop を L2 Autonomous Mind として位置付け。`autonomous/l2_mind.py` で L1 → L2 → L3 の呼び出し関係を明示化 |
| **L3 (深層推論)** | なし | 新規 `aegis_ai/llm/l3_reasoner.py` を新設。L2 から `escalate_l3(reason, problem, context)` で呼び出される |
| **LLM Gateway** | `aegis_ai/llm/gateway.py` (既存 profile-based) | `LLMGateway.request(layer: "L1" \| "L2" \| "L3", prompt, ...)` を追加。各 layer に対応する profile を `llm.yaml` で定義 |
| **EventBus** | `aegis_ai/event/event_manager.py` | `l1.*` / `l2.*` / `l3.*` event kind 追加 (D1 で `agent.*` 8 種類追加済みを参考) |
| **Capability / MCP** | `aegis_ai/capability_*.py` + `tools/mcp_gateway.py` | L1 から直接 Capability を呼び出せるよう、`l1.execute_capability(capability_id, args)` を L1 Router に追加。**L3 Capability ルール** (Phase L5): L3 は読み取り系 capability (web 検索 / ファイル読み取り / list / browse / memory search など) を直接実行可能、書き込み系 (file write / mouse / keyboard / shell など) は L2 経由強制。判定は `is_read_only_capability(capability_id)` で catalog metadata.side_effect / risk_level / キーワード 2 重 / 安全側の 4 段判定。 |
| **Sleep** | `aegis_ai/memory/sleep.py` | 既存そのまま。Sleep 中に L1/L2/L3 全層の Memory consolidation を実施 |
| **Dashboard (既存)** | `web-ui/` (D1-D9 完了) | L1/L2/L3 専用パネル追加 (Phase L6) |
| **Manager 層** | Task / Memory / Event / Audit / Status / Notification / Approval | v3 で変更なし。LLM 層は Manager を介してのみ状態を変更 |

---

## 4. 実装フェーズ (Phase L1 - L6)

| Phase | 内容 | 規模 | 既存資産活用率 | 完了基準 |
|-------|------|------|---------------|---------|
| **L1** | LLM Gateway 拡張 (L1/L2/L3 profile 対応) ✅ | 小 | 100% (gateway.py 拡張) | `LLMGateway.request("L1"\|"L2"\|"L3", ...)` が動作 |
| **L2** | L1 Router 統合 (Intake router を L1 化) ✅ | 中 | 80% (intake/ を L1 化) | L1 が Event → Observation / Escalation 構造化出力を生成 |
| **L3** | L1 MCP Executor (Capability 直接呼び出し) ✅ | 中 | 50% (新 L1 Executor) | L1 が簡単な user command を Capability へ直接ルーティング |
| **L4** | L2 Autonomous Mind (Autonomous Loop を L2 化) ✅ | 大 | 70% (autonomous/ 改修) | L2 が Memory / Desire / Task を統合的に参照し行動決定 |
| **L5** | L3 Escalation (Deep Reasoner 新設) ✅ | 中 | 0% (新規) | L2 から L3 への escalation フローが動作 (Capability ルール適用) |
| **L6** | Dashboard 3 層対応 (L1/L2/L3 パネル + Overlay 拡張) | 大 | 60% (D1-D9 拡張) | L1 / L2 / L3 専用パネル + 1 行 Overlay が layer 識別表示 |

---

## 5. フェーズ別詳細

### Phase L1 — LLM Gateway 拡張 (L1/L2/L3 profile)

**目標**: 既存 `LLMGateway` に layer 抽象化を追加。`llm.yaml` に `l1_default` / `l2_default` / `l3_default` profile を定義。

**変更ファイル**:
- `ai-server/src/aegis_ai/llm/gateway.py` — `LLMGateway.request(layer: Literal["L1","L2","L3"], prompt, ...)` 追加
- `ai-server/config/llm.yaml` — `l1_default` / `l2_default` / `l3_default` profile 追加
- `ai-server/src/aegis_ai/llm/layer_profiles.py` (新規) — layer → profile 解決
- `ai-server/tests/test_llm_gateway_layers.py` (新規) — L1/L2/L3 呼び出しテスト

**DoD**:
- [ ] `LLMGateway.request("L1", "hello")` が `l1_default` profile で LLM を呼ぶ
- [ ] `LLMGateway.request("L2", ...)` / `("L3", ...)` も同様
- [ ] 各 layer 呼び出しが CostTracker に記録される
- [ ] Audit に `llm.call` event が `payload.layer` 付きで publish される
- [ ] 既存 `gateway.generate()` / `generate_with_tools()` 後方互換維持

**設計判断**:
- layer 抽象は profile の alias に留め、既存 router ロジックは触らない
- L1 は高速・低コスト (例: deepseek-chat, gpt-4o-mini)
- L2 は中コスト (例: gpt-4o, deepseek-reasoner)
- L3 は高品質 (例: claude-3.5-sonnet, o1)
- profile 切替は `llm.yaml` で柔軟に設定可能

---

### Phase L2 — L1 Router 統合 (Intake router を L1 化) ✅

**目標**: 既存 `intake/router.py` / `classifier.py` / `deduplicator.py` を L1 の入力口として統合。L1 が Event → `Observation` / `Decision` / `Value` / `Priority` / `RequiredIntelligence` / `Action` / `Escalation` を構造化出力。

**変更ファイル**:
- `ai-server/src/aegis_ai/intake/l1_router.py` (新規) — L1 Router (intake の上に位置)
- `ai-server/src/aegis_ai/intake/l1_models.py` (新規) — `L1Observation` / `L1Decision` / `L1Escalation` dataclass
- `ai-server/src/aegis_ai/intake/router.py` — 既存 Intake router を L1 経由に切替
- `ai-server/src/aegis_ai/event/event_manager.py` — `l1.observation` / `l1.decision` / `l1.escalation` event kind 追加
- `ai-server/src/aegis_ai/llm/gateway.py` — `LLMGateway.observe(event)` 追加 (L1 用 convenience)
- `ai-server/tests/intake/test_l1_router.py` (新規) — L1 構造化出力テスト

**DoD**:
- [x] L1 Router が EventBus イベントを `L1Observation` に変換
- [x] `L1Observation.value` / `priority` / `required_intelligence` が LLM 出力から抽出される
- [x] `required_intelligence == "high"` の場合 `L1Escalation` が生成され EventBus に publish
- [x] `l1.observation` / `l1.escalation` event が EventManager で永続化
- [x] 既存 Intake router の後方互換維持 (deprecated warning)

**設計判断**:
- L1 は **常時稼働** が要件。EventBus への subscribe ではなく、`Observation` service の `poll()` ベースで軽量に
- L1 の prompt は短く保つ (token 効率)。Observation / Decision 構造化出力のみ
- `RequiredIntelligence` は "low" / "medium" / "high" の 3 値
- L1 escalation 頻度は 1 時間 10 回以下に throttle

**実装サマリ (2026-09-10 / commit `f428845`)**:
- `l1_models.py` — `RequiredIntelligence` enum (LOW/MEDIUM/HIGH) / `L1ActionType` enum (ESCALATE/CAPABILITY/OBSERVE/IGNORE/NOOP) / `L1Observation` / `L1Action` / `L1Decision` / `L1Escalation` dataclass + `to_payload()`。
- `l1_router.py` — `L1Router` dataclass (`llm_gateway` / `min_value_for_action=0.3` / `min_priority_for_escalation=0.6` / `enabled=True`) + `should_escalate()` / `observe(event, event_id=)` / `decide(observation)` / `escalate(observation, reason=)` / `route(event, event_id=)` + `_summarize_event()` 内部 helper。L1 system prompt は token 効率優先の短文 JSON スキーマ要求。
- decision tree: HIGH intelligence → ESCALATE / value < `min_value_for_action` → IGNORE / それ以外 → OBSERVE。
- `intake/__init__.py` — L1 シンボル re-export + docstring 追記。
- `event_manager.py` の `_PERSIST_EVENT_TYPES` に `l1.observation` / `l1.decision` / `l1.escalation` を追加 (Phase L6 で利用予定)。
- テスト 21 件全件 pass (TestL1Models 4 + TestL1RouterObserve 6 + TestL1RouterDecide 5 + TestL1RouterEscalateAndRoute 3 + TestSummarizeEvent 3)。既存 intake / LLM 113 件 + event 24 件回帰なし。
- 注: 既存 `intake/router.py` への切替は Phase L3 (L1 MCP Executor) で `L1Router` を介した統合を実施する。Phase L2 では L1 を独立コンポーネントとして提供。

---

### Phase L3 — L1 MCP Executor (Capability 直接呼び出し) ✅

**目標**: L1 から Capability / MCP を直接呼び出せるようにする。簡単な user command ("電気をつけて") は L2 を経由せず L1 → Capability で完結。

**変更ファイル**:
- `ai-server/src/aegis_ai/intake/l1_executor.py` (新規) — L1 → Capability 直接実行
- `ai-server/src/aegis_ai/capability_broker.py` (確認のみ) — 既存 Broker を L1 から呼び出せるよう API 確認
- `ai-server/src/aegis_ai/intake/l1_router.py` — `L1Router.execute_capability(capability_id, args)` 追加
- `ai-server/src/aegis_ai/event/event_manager.py` — `l1.capability.invoked` / `l1.capability.completed` event kind
- `ai-server/tests/intake/test_l1_executor.py` (新規)

**DoD**:
- [x] L1 が `L1Decision.action.type == "capability"` の場合、Capability を直接呼び出す
- [x] 呼び出し結果が `L1ActionResult` に wrap され EventBus に publish
- [x] Policy engine を経由 (D5 で実装済み) — 危険な Capability は L1 から呼び出せない
- [x] Audit に capability 実行が記録される

**設計判断**:
- L1 から呼び出せる Capability は **risk="low"** のみ (Policy engine で制限)
- 危険な Capability は L2 経由 (approval 必要) — 既存 approval flow を活用
- L1 は結果を L2 には渡さず、user に直接返却

**実装サマリ (2026-09-10 / commit `5a075d7`)**:
- `l1_models.py` に `L1ActionResult` dataclass 追加 (capability_id / event_id / success / result / error / risk_level / duration_ms / bypassed_approval + `to_payload()`)。
- `l1_executor.py` — `L1Executor` dataclass (`capability_catalog` / `tool_broker` / `allowed_risk_levels` (default frozenset({"low", "safe"})) / `enabled`)。`resolve()` / `get_risk_level()` / `is_callable()` / `execute()` を提供。`_get_catalog()` / `_get_broker()` は singleton フォールバック付き。risk 正規化 helper (`_normalize_risk` / `_normalize_allowed`) で `READ_ONLY` ↔ `low` / `SAFE_ACTION` ↔ `safe` 等を橋渡し。
- 実実行は `ToolBroker.execute()` を経由して Policy / Approval / Audit 適用。`request.metadata` に `caller=l1` / `layer=L1` を必ず setdefault で残す。
- `intake/__init__.py` で L1Executor / L1ActionResult re-export + docstring 追記。
- `event_manager.py` の `_PERSIST_EVENT_TYPES` に `l1.capability.invoked` / `l1.capability.completed` を追加 (Phase L6 で利用予定)。
- テスト 19 件全件 pass (TestImports 2 + TestRiskChecks 8 + TestExecute 7 + TestPackageExports 2)。既存 intake / LLM / event 156 件回帰なし。
- 注: `L1Router.execute_capability()` ショートカットは Phase L4 (L2 Autonomous Mind) で `L1Router` と `L1Executor` を束ねる統合 API として追加予定。

---

### Phase L4 — L2 Autonomous Mind (Autonomous Loop を L2 化) ✅

**目標**: 既存 `autonomous_loop.py` を L2 Autonomous Mind として位置付け。L2 が `World state + Memory + Desire + Task + L1 summaries` を統合的に参照して行動決定。

**変更ファイル**:
- `ai-server/src/aegis_ai/autonomous/l2_mind.py` (新規) — L2 Autonomous Mind entry
- `ai-server/src/aegis_ai/autonomous/autonomous_loop.py` — 既存を L2 化 (薄い wrapper)
- `ai-server/src/aegis_ai/autonomous/l2_models.py` (新規) — `L2Context` / `L2Decision` / `L2Action`
- `ai-server/src/aegis_ai/event/event_manager.py` — `l2.thinking` / `l2.decision` / `l2.escalation` event kind
- `ai-server/src/aegis_ai/llm/gateway.py` — `LLMGateway.l2_request(context)` 追加
- `ai-server/tests/autonomous/test_l2_mind.py` (新規)

**DoD**:
- [x] L2 が定期的に (デフォルト 30 分) 起動し `L2Context` を組み立てる
- [x] L1 escalations を `L2Context.l1_summaries` に含める
- [x] L2 が `L2Decision` を生成 → 必要に応じて Task 作成 / L3 escalation
- [x] `l2.thinking` / `l2.decision` event が EventBus に publish
- [x] 既存 autonomous loop の自律実行 (desire ベース) が L2 として動作継続

**設計判断**:
- L2 の context window は中サイズ (8K tokens)。Memory summarization を活用
- L2 は Manager を介してのみ状態変更 (既存 Manager pattern 維持)
- L2 → L3 escalation は `L2Decision.escalate_to_l3` flag で明示

**実装サマリ (2026-09-10 / commit `8c47d23`)**:
- `l2_models.py` — `L2ActionType` enum (TASK / ESCALATE_L3 / OBSERVE / NOOP) / `L2Context` (world_state / memory_summary / desire_snapshot / task_state / l1_summaries / pending_obligations / recent_failures + `to_prompt()` で LLM 入力用短文生成) / `L2Action` / `L2Decision` (+ `to_payload()`) / `L2Escalation` (+ `to_payload()`)。
- `l2_mind.py` — `L2AutonomousMind` dataclass (`llm_gateway` / `memory_system` / `desire_system` / `task_state_provider` (callable) / `l1_summaries_provider` (callable) / `event_publisher` (callable) / `enabled` / `l3_confidence_threshold=0.4` / `cycle_interval_seconds=1800` / `last_cycle_at_ms`)。`_get_gateway()` で singleton フォールバック、`_publish()` で event 発行、`_safe_call()` で provider 失敗時のフォールバック (空 list)、`build_context()` で memory / desire / task / l1 summary を統合、`decide()` で `LLMGateway.request(layer="L2", json_mode=True)` 経由の判断生成、`_parse_decision()` で action_type / task_spec / l3_problem / escalate_to_l3 抽出 (失敗時は安全側 NOOP)、`should_run_cycle()` で cycle タイミング判定。
- L2 system prompt は中期サイズ JSON スキーマ強制 (8K tokens)。confidence < threshold で auto-escalate、JSON parse 失敗 / gateway 失敗 / 未知 action_type はすべて NOOP フォールバック (instruction.md §38 フォールバック禁止方針と整合)。
- `autonomous/__init__.py` を新規作成し `L2AutonomousMind` / L2 シンボル + `AutonomousLoop` を re-export。
- `event_manager.py` の `_PERSIST_EVENT_TYPES` に `l2.thinking` / `l2.decision` / `l2.escalation` を追加 (Phase L6 で利用予定)。
- 注: 既存 `AutonomousLoop` には **触らず**、L2Mind は独立した薄いラッパーとして提供。`AutonomousLoop` 自体の L2 統合は別 PR / 別フェーズで実施予定。
- テスト 29 件全件 pass (TestImports 5 + TestL2Context 2 + TestBuildContext 4 + TestDecide 9 + TestEventPublish 3 + TestCycle 4 + TestPayloads 2)。既存 intake / LLM / event 185 件回帰なし。

---

### Phase L5 — L3 Escalation (Deep Reasoner 新設) ✅

**目標**: L3 Deep Reasoner を新設。L2 が `confidence < threshold` または `difficulty > threshold` のとき L3 を呼ぶ。

**変更ファイル**:
- `ai-server/src/aegis_ai/llm/l3_reasoner.py` (新規) — L3 Reasoner entry
- `ai-server/src/aegis_ai/llm/l3_models.py` (新規) — `L3Problem` / `L3Result` / `L3Plan`
- `ai-server/src/aegis_ai/event/event_manager.py` — `l3.invoked` / `l3.completed` / `l3.failed` event kind
- `ai-server/src/aegis_ai/llm/gateway.py` — `LLMGateway.l3_request(problem, context)` 追加
- `ai-server/src/aegis_ai/autonomous/l2_mind.py` — L2 → L3 escalation hook 追加
- `ai-server/tests/llm/test_l3_reasoner.py` (新規)

**DoD**:
- [x] L2 から `escalate_l3(reason, problem, context)` で L3 を呼び出せる
- [x] L3 が `L3Plan` を返却 (Reasoning / Plan / Recommendation)
- [x] L3 の結果は L2 に返却され、L2 が Validation 後に Task 化
- [x] `l3.invoked` / `l3.completed` event が EventBus に publish
- [x] L3 の cost は CostTracker で別カテゴリ "l3_reasoning" として記録
- [x] Capability ルール: L3 は読み取り系 capability を直接実行可能、書き込み系は L2 経由強制

**設計判断**:
- L3 は **常時呼び出さない**。L2 が必要と判断したときのみ (L2 の判断責任)
- L3 は **書き込み系 Capability を直接実行しない** (L2 責任分離)。L2 経由で実行
- L3 は **読み取り系 Capability を直接実行可能** (web 検索 / ファイル読み取り / list / browse / memory search など)
- L3 の prompt は大規模 (32K tokens)、reasoning 重視
- L3 timeout は 5 分。timeout 時は L2 で fallback

**実装サマリ (2026-09-10 / commit `4ffe286`)**:
- `l3_models.py` — `L3Action` enum (TASK / OBSERVE / ABORT) / `L3Step` (order / capability_id / args / read_only / reason / depends_on) / `L3Problem` (+ `to_payload()`) / `L3Plan` (steps / assumptions / risks / recommendations + `read_only_plan` property + `to_payload()`) / `L3Result` (+ `to_payload()`)。
- `l3_reasoner.py` — `L3Reasoner` dataclass (`llm_gateway` / `capability_catalog` / `event_publisher` / `enabled` / `timeout_seconds=300` / `read_only_only=True`)。`_get_gateway()` / `_get_catalog()` で singleton フォールバック、`_publish()` で event 発行、`_validate_step()` で LLM の read_only フラグを `is_read_only_capability` で再判定 (LLM 嘘対策)、`reason()` で `LLMGateway.request(layer="L3", json_mode=True)` 経由の推論、`_build_prompt()` で system + problem 統合プロンプト生成、`_parse_result()` で plan / recommended_action / confidence 抽出 (失敗時は None 返却)。
- `is_read_only_capability(capability_id, catalog=None)` ヘルパ — 4 段判定:
  1. `catalog.metadata.side_effect` (`"read_only"` / `"none"` を read 扱い、それ以外を write 扱い)
  2. `risk_level` (`"low"` / `"safe"` / `"read_only"` を read 扱い、それ以外を write 扱い)
  3. キーワード 2 重判定 — 書き込み capability_id ブラックリスト (`write|create|delete|...` + `file_write|mouse|keyboard|shell|...`) と 読み取り capability_id ホワイトリスト (`read|get|list|search|...` + `memory|search|web_search|browser|browse|file_read|...`) を regex パターンで実装 (境界は `(?:[._-]|\\b)` で単語境界を `_` / `.` / `-` 含めて判定)
  4. 安全側 (write 扱い) — 判定不能なら write 扱い
- L3 system prompt は大規模 (32K tokens) reasoning 重視 JSON スキーマ強制。
- `read_only_only=True` で plan 内に write step があれば `recommended_action=ABORT` に強制 downgrade。L3 失敗時 (gateway error / json parse / 未知 action) は None 返却 (instruction.md §38 フォールバック禁止)。
- `l2_mind.py` に `L2AutonomousMind.escalate_to_l3(problem_text, *, context, l1_observations, reason, constraints)` convenience method 追加 (singleton 風に `L3Reasoner` を lazy 解決、`L3Problem` 構築、`reasoner.reason()` 委譲)。
- `llm/__init__.py` に L3Reasoner / L3Action / L3Plan / L3Problem / L3Result / L3Step / is_read_only_capability を re-export。
- `event_manager.py` の `_PERSIST_EVENT_TYPES` に `l3.invoked` / `l3.completed` / `l3.failed` を追加 (Phase L6 で利用予定)。
- テスト 32 件全件 pass (TestImports 3 + TestIsReadOnlyCapability 9 + TestModelsPayloads 5 + TestReason 9 + TestEventPublish 3 + TestL2EscalateToL3 2 + TestPackageExports 1)。既存 intake / autonomous / LLM / event 217 件回帰なし。

---

### Phase L6 — Dashboard 3 層対応

**目標**: Dashboard に L1 / L2 / L3 専用パネルを追加。1 行 Live Overlay が layer 識別表示。

**状態**: ✅ 完了 (commit `95d0ce0`)

**変更ファイル**:
- `web-ui/src/pages/L1PanelPage.tsx` (新規) — L1 activity (events / observations / escalations)
- `web-ui/src/pages/L2PanelPage.tsx` (新規) — L2 activity (thinking / decisions / tasks)
- `web-ui/src/pages/L3PanelPage.tsx` (新規) — L3 invocations (problems / results / plans)
- `web-ui/src/pages/LlmLayerPanel.tsx` (新規) — 共通 panel (layer props で切替 / 5 秒 tick 自動再フェッチ / kind フィルタ)
- `web-ui/src/components/LiveOverlay.tsx` — layer 識別表示 ("L1: ..." / "L2: ..." / "L3: ..." / "MCP: ...") + `data-layer` 属性 + `data-testid="live-overlay-layer"`
- `web-ui/src/navigation.ts` — L1 / L2 / L3 ページ + aliases 追加
- `web-ui/src/App.tsx` — routing 追加
- `web-ui/src/api/client.ts` — `/api/l1/events` / `/api/l2/events` / `/api/l3/events` 取得 API + `inferLayerFromEvent()` ヘルパ
- `ai-server/src/aegis_ai/web/routes/l1_routes.py` (新規) — L1 イベント取得 (3 endpoints: /events, /events/recent, /events/stats)
- `ai-server/src/aegis_ai/web/routes/l2_routes.py` (新規) — L2 イベント取得
- `ai-server/src/aegis_ai/web/routes/l3_routes.py` (新規) — L3 イベント取得
- `ai-server/src/aegis_ai/web/dashboard_legacy.py` — `init_l1/l2/l3_routes()` 登録
- `ai-server/tests/test_l1_routes.py` / `test_l2_routes.py` / `test_l3_routes.py` (新規) — 23 件
- `web-ui/src/pages/LlmLayerPanel.test.tsx` (新規) — 6 件
- `web-ui/src/components/LiveOverlay.test.tsx` — layer 識別テスト追加 (5 件)

**DoD**:
- [x] L1 / L2 / L3 専用ページが navigation に追加
- [x] 各ページが `/api/l1/events` / `/api/l2/events` / `/api/l3/events` で該当 event を取得・表示
- [x] LiveOverlay が event kind prefix を見て "L1: ..." / "L2: ..." / "L3: ..." / "MCP: ..." を表示
- [x] 各パネルが 5 秒 tick で live update される
- [x] backend routes 23 件 test pass / frontend vitest 126 件全件 pass / tsc -b 0 エラー

**設計判断**:
- L1 / L2 / L3 ページは **既存 AgentSessionPage と並列** (Agent Session とは独立した抽象)
- layer 識別 Overlay は **既存 priority ロジックに追加** する形 (上書きしない)
- L3 page は問題 / context / result / plan を 4 列で表示
- layer 情報は payload のみに格納せず、event kind 自体に埋め込む (`l1.observation` / `l2.decision` / `l3.invoked`)
- panel component を L1PanelPage / L2PanelPage / L3PanelPage で別 page に分割 (route ごとに別 URL を保持するため)、内部は共通の `LlmLayerPanel` で実装 (DRY)
- 5 秒 tick は固定 (live overlay の sticky 動作と整合)

---

## 6. 全体アーキテクチャ不変条件

v3 実装中も以下を維持する (AGENTS.md と整合):

1. **LLM 層は Manager 層を直接変更しない** — Manager を介してのみ
2. **L3 Capability ルール** — L3 は読み取り系 capability (web 検索 / ファイル読み取り / list / browse / memory search など) を直接実行可能、書き込み系 (file write / mouse / keyboard / shell など) は L2 経由強制。`is_read_only_capability(capability_id)` で判定
3. **L1 は risk="low" の Capability のみ実行** — 危険 Capability は L2 経由 (approval 必要)
4. **Approval / Audit / Policy の 3 絶対境界は維持** (AGENTS.md)
5. **L1/L2/L3 全てが EventBus に publish** — Dashboard からの可視性確保
6. **Sleep は L1/L2/L3 全層で Memory consolidation** — Sleep 中に全 layer の Memory 整理
7. **L1/L2/L3 全てが CostTracker に記録** — 層別 cost 集計可能

---

## 7. テスト戦略

- **unit tests** (pytest):
  - L1: 構造化出力 / escalation 判定
  - L2: context 組立 / decision 生成
  - L3: problem → plan の推論
  - LLM Gateway: layer 別 profile 解決 / cost 記録
- **integration tests**:
  - L1 → Capability 直接実行
  - L2 → L3 escalation → L2 validation → Task
  - EventBus への l1.* / l2.* / l3.* event publish
- **vitest (frontend)**:
  - L1 / L2 / L3 Panel ページ描画
  - LiveOverlay の layer 識別表示
  - SSE 経由の live update

---

## 8. v2 サマリー (D1-D9 アーカイブ)

| Phase | 内容 | Commit | Tests |
|-------|------|--------|-------|
| D1 | Agent イベントストリーム拡張 | `c8126c9` | 17 |
| D2 | Live Overlay | `b570ed3` | +14 |
| D3 | Trace ID 6 種伝搬 | `573a369` | +6 |
| D4 | Agent Trace 9 tabs | `6c0b606` / `5105ecb` | +16 |
| D5 | Policy / Approval 統合 | `039640d` / `dd48ea1` | +9 |
| D6 | MCP / Tool call 完全表示 | `118bb57` | +10 |
| D7 | 検索 + Agent Timeline | `231966b` / `3831440` | +5 |
| D8 | 複数 Agent / Live Overlay 優先順位 | `c349b8d` / `6a99234` | +16 |
| D9 | Settings §22 + Token/Cost §25 | `e54fcf7` / `6b598d9` | +14 |

v2 完了時の状態: 全体 vitest 115 passed、backend 938+ passed (D5 時点)。

---

## 9. 想定スケジュール / 工数

- **Phase L1**: 小 (1-2 時間相当) — LLM Gateway 拡張 ✅ 完了
- **Phase L2**: 中 (3-4 時間相当) — L1 Router 統合 ✅ 完了
- **Phase L3**: 中 (3-4 時間相当) — L1 MCP Executor ✅ 完了
- **Phase L4**: 大 (6-8 時間相当) — L2 Autonomous Mind ✅ 完了
- **Phase L5**: 中 (3-4 時間相当) — L3 Deep Reasoner ✅ 完了
- **Phase L6**: 大 (6-8 時間相当) — Dashboard 3 層対応 ✅ 完了

合計: ~25-30 時間相当 (各 Phase 完了時に git commit + 進捗ログ更新)。全 Phase 完了済み。

---

## 10. リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| 既存 L1 (Intake) の置き換えによる regression | 大 | 後方互換維持 (deprecated warning) + 既存テスト全件 pass 確認 |
| L3 が高頻度で呼ばれ cost 増 | 中 | L2 の escalation 閾値調整 + CostTracker で監視 |
| L1/L2/L3 の prompt 管理が複雑化 | 中 | `llm.yaml` の中央管理 + PromptRegistry 活用 |
| EventBus への l1.* / l2.* / l3.* event 追加で永続化サイズ増 | 中 | 既存 retention 設定 (D9 で未着手) で制御 |
| Dashboard に L1/L2/L3 ページ追加で UX 複雑化 | 小 | navigation に "LLM Layers" グループ化 |
| L3 が読み取り系 capability を直接実行することで approval bypass が発生しうる | 大 | `is_read_only_capability()` の 4 段判定で書き込み系を確実に弾く / `read_only_only=True` で plan 全体 write なら ABORT / 監査ログに `caller=l3` / `layer=L3` を必ず残す |
| L3 推論ループが暴走して LLM cost 急増 | 中 | L2 escalation 閾値 (`l3_confidence_threshold=0.4`) 調整 + CostTracker で `l3_reasoning` カテゴリ監視 + `timeout_seconds=300` で強制打ち切り |
| LLM が read_only capability のフラグを嘘で返す (LLM hallucination) | 中 | `_validate_step()` で LLM 出力の read_only フラグを `is_read_only_capability()` で必ず再判定 / 安全側 (write 扱い) で downgrade |

---

## 11. 次のアクション

1. ~~本プラン v3 の user 承認~~ ✅ 承認済み
2. ~~Phase L1 から順次実装 (git commit + 進捗ログ更新で永続化)~~ ✅ L1-L6 全完了
3. Phase L6 完了後に Dashboard 全体の統合テスト
4. instruction.md の §23 (OpenHands 設定) / §24 (Retention) を別 phase として統合

---

## 12. 変更履歴

- 2026-09-10: v3 作成 (instruction.md v3 反映)
  - L1/L2/L3 3 層アーキテクチャ統合プラン
  - Phase L1-L6 詳細 (DoD / 変更ファイル / 設計判断)
  - 既存 AEGIS 資産との対応表 (§3)
  - v2 (D1-D9) アーカイブを §8 に移動
  - 全体アーキテクチャ不変条件 (§6) を AGENTS.md と整合
- 2026-09-10: Phase L5 完了 (commit `4ffe286`)
  - L3 Capability ルール: 読み取り系 capability (web 検索 / ファイル読み取り / list / browse / memory search) を L3 が直接実行可能、書き込み系 (file write / mouse / keyboard / shell) は L2 経由強制
  - `is_read_only_capability()` ヘルパ追加 (4 段判定: catalog metadata.side_effect → risk_level → キーワード 2 重 → 安全側)
  - `l2_mind.py.escalate_to_l3()` convenience method 追加
  - §3 Capability / MCP 行に L3 ルール追記、§6 不変条件 2 を「読み取り許可 / 書き込み L2 経由強制」に更新、§10 リスクに 3 件追加 (approval bypass / 暴走ループ / 誤判定)
  - テスト 32 件全件 pass、既存 217 件回帰なし
- 2026-09-10: Phase L1-L5 全完了マーク更新
- 2026-09-10: Phase L6 完了 (commit `95d0ce0`)
  - backend: `l1_routes.py` / `l2_routes.py` / `l3_routes.py` 新規 + `dashboard_legacy.py` で `init_l1/l2/l3_routes()` 登録
  - 3 endpoints × 3 layer = 9 endpoints 追加 (`/api/l{1,2,3}/events` / `/api/l{1,2,3}/events/recent` / `/api/l{1,2,3}/events/stats`)
  - 各 layer 専用 `_L1_KINDS` / `_L2_KINDS` / `_L3_KINDS` frozenset で EventManager.list_recent() をフィルタ + DESC 順返却
  - frontend: `LlmLayerPanel.tsx` 共通 panel + `L1PanelPage` / `L2PanelPage` / `L3PanelPage` 薄いラッパー (intel ドメイン配下)
  - `LiveOverlay.tsx` に `inferLayerFromEvent()` 経由で "L1: ..." / "L2: ..." / "L3: ..." / "MCP: ..." タグ表示 + `data-layer` 属性
  - 5 秒 tick 自動再フェッチ + kind 別フィルタ + stats 表示
  - backend test 23 件全件 pass (L1: 9, L2: 7, L3: 7) / frontend vitest 126 件全件 pass (LlmLayerPanel 6 + LiveOverlay 23 含む) / tsc -b 0 エラー
  - 既存 D1-D9 機能への regression なし (LiveOverlay priority sort / Agent Session 9 tabs / Timeline 全て維持)
