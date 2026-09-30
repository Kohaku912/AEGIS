# Phase 5b — ルール単位の置換案

**Status**: **完了（2026-09-28）** — Python・proto・Rust・Kotlin の全層で実装済み。
**Date**: 2026-09-28
**前提**: 単一制約（ユーザー情報はローカルから出ない）のみが制約。
承認は制約ではない。5a で「AEGIS が自主的に確認する」経路は実装済み。

---

## オーナー決定（2026-09-28）

1. `risk ∈ {forbidden, blocked}` は**拒否軸に残さない** → R1 は `enabled=False` のみが deny
2. R3 の delegation policy への移設を**承認**
3. proto / Kotlin / Rust の変更を**許可**
4. 支払いの第一級拒否への格上げは**不要**（現状の delegation deny のまま）

## 実装結果（2026-09-28）

| 対象 | 実施内容 |
|---|---|
| R1 | `enabled=False` のみが `BLOCKED`。`forbidden`/`blocked` の拒否軸を削除。`requires_approval=True` の代入も削除 |
| R2 | 承認分岐を削除 → `plan.risk_notes` に注記 |
| R3 | `_evaluate_delegation()` 経由で `DelegationPolicyStore.evaluate()` に移設。`forbidden`→`BLOCKED`、`rule_id` 一致時は注記。broker と同じ enrichment（`operation_category`/`ownership_scope`）を mirror |
| R4/R5/R6 | 3分岐すべて削除（R6 は到達不能だった） |
| `l2_mind._requires_approval` | 削除。`_risk_category_for_capability` は残したが `FORBIDDEN→BLOCKED` を削除し、fallback を `READ`→`DEVICE_ACTION` に変更（未知を「無害」と偽らないため） |
| `PlanStep.requires_approval` | 削除（field / `to_dict` / `from_dict`） |
| `TaskPlan.approval_needed` | 削除（field / `to_dict` / `from_dict`） |
| LLM プロンプト | step テンプレートの `requires_approval` と plan テンプレートの `approval_needed` を削除 |
| `interaction/router.py` | interpreter へ broker の delegation store を注入 |
| `tool_broker.py` | `delegation_policy` プロパティを追加（読み取り用） |
| `web/chat_tools.py` | `approval_needed`/`approval_id` 定数を削除 |
| `web/chat_service.py` / `web/routes/chat.py` | 死んだ `approval_needed` 分岐を削除 |
| `web-ui` `ChatDrawer.tsx` / `api/client.ts` | 承認ログ行と `ChatSendResult` の 2 フィールドを削除 |

**検証**: ai-server **1536 passed / 9 skipped**（Python 側 1528 + ワイヤ契約テスト 8 本）。
web-ui `tsc -b` clean、vitest **134 passed**。`cargo check --all-targets` clean。

### proto / Rust / Kotlin 層（2026-09-28 完了）

オーナー決定③の範囲。**強制承認のライフサイクルは削除、AEGIS が自主的に問う UI と
トランスポートは残置** — この線引きが 5b の核心であり、片側だけ満たすと必ず壊れる
（過剰削除＝確認 UI が死ぬ／削除不足＝ゲートが戻る）。

| 層 | 削除 | 残置（意図的） |
|---|---|---|
| `common.proto` | `ApprovalStatus` / `ApprovalType` / `ApprovalRequest`、`AuditAction.APPROVAL_*`、`PolicyDecisionType.ASK_APPROVAL`、`Capability.requires_approval`、`ToolInvocationRequest.is_approved`/`approval_id`、`ToolInvocationResult.was_approved` | `SafetyLevel.LEVEL_2_APPROVAL`（**記述的な階層ラベル**。何もゲートしない） |
| `ai_server.proto` | RPC 3 本 + メッセージ 5 種、`ChatResponse.approval_needed`/`approval_id` | `WriteAuditLog` / `QueryAuditLog` |
| `android_server.proto` | 単方向 `RequestApproval`、`AndroidApprovalRequest`/`AndroidApprovalResponse` | `AndroidApprovalCommand` / `AndroidApprovalDecision`、`approval_request` / `approval_decision` oneof（**ストリーム経由の「問い」**） |
| Python スタブ (`ai-server`) | `grpc_tools.protoc` で再生成。`from aegis import` → `from generated.aegis import` | — |
| Python スタブ (`room-server`) | **2 度目の掃引で発見（同日）**。`protoc 6.33.5` のまま停止しており、`ApprovalRequest` / `ApprovalStatus` / `ApprovalType` / `Capability.requires_approval` / `ToolInvocationRequest.is_approved`・`approval_id` / `ToolInvocationResult.was_approved` / `AUDIT_ACTION_APPROVAL_*` / `POLICY_DECISION_ASK_APPROVAL` を**生きたメンバーとして**保持していた。正規プロトコルから再生成し、`ai-server` とバイト単位で一致させた | — |
| Rust (`pc-server`) | `safety.rs`/`main.rs`/`overlay_approval.rs`/`health.rs` の「承認が必要」表現を**記述的な注記**に是正 | Y/N 確認オーバーレイ（AEGIS が自発的に出す問い） |
| Kotlin (`android-server`) | `ChatReply.approvalNeeded`/`approvalId`、`ApprovalItem.createdAtMs`/`expiresAtMs` | メソッド名を維持したまま**ストリーム上の確認キュー**へ再接続。画面は無改修 |

削除は proto の作法どおり `reserved <番号>; reserved "<名前>";` で行い、ワイヤ番号を再利用しない。

**副産物**: 死んでいた重複スタブ `ai-server/src/aegis/`（6 ファイル・git 追跡下）を削除。
`generated/aegis/` の**不完全な**コピー（`common`/`room_server` のみ）で、
`ApprovalStatus`/`ApprovalType`/`ASK_APPROVAL` を**生きたメンバーとして**保持していた
＝ ガードテストの除外設定に隠れて生き残っていた「削除済みのはずの承認型」そのもの。
これで `ai-server` 側の proto スタブは `src/generated/aegis/` の 1 箇所のみ。

**同日の追加掃引で判明した 2 つ目の盲点**: サーバごとに**独自の生成スタブ**を持つ。
`room-server/src/generated/aegis/` は正規コントラクトの**古いミラー**で、5b の削除が
一切反映されていなかった（上表）。ガードテストが `ai-server/src` しか見ていなかったため、
**緑のまま**残っていた。対策は 3 点:

1. `room-server` のスタブを正規 `protos/aegis/` から再生成（`ai-server` とバイト単位で一致）。
   `room-server` 自身の `uv.lock` は `protobuf 7.35.1` を固定しており、再生成はむしろ
   lockfile に**整合**させた（旧スタブは 6.33.5 産で、宣言と実際の依存がずれていた）。
2. `scripts/generate_protos.{sh,ps1}` を修復。**存在しない proto 3 本**
   （`pc_server` / `browser_server` / `dev_server`）を列挙していたため `protoc` が
   ファイル不在で落ち、**スクリプト自体が実行不能**だった（＝ミラーが放置された根本原因）。
   さらに出力先が `ai-server` のみで、`room-server` には一度も書いていなかった。
   各サーバが実際に消費する proto だけを出力するよう修正。
3. ガードテストを**リポジトリ全体**に拡張。全 `*_pb2.py` の**シリアライズ済みディスクリプタ**を
   読み、削除済みの名前が `reserved` 以外（＝生きたメンバー）で現れないことを検証する。
   併せて「同じ proto の生成物はサーバ間でバイト単位一致」も検証。これらは
   `room-server` の旧スタブを意図的に戻すと**実際に落ちる**ことを確認済み。

**注意（未検証）**: Android の Kotlin コンパイルは**このマシンに JDK が無いため未検証**
（`JAVA_HOME` 未設定・`java.exe` 不在）。静的な記号検査では削除済み proto シンボルの参照はゼロ。

> **追記（2026-09-30）— 検証済みになった。** JDK 17 と Android SDK は**入っており**（`PATH` に
> 無いだけ）、`:app:compileDebugKotlin` が実行され `:app:assembleDebug` が `app-debug.apk`
> （21,024,388 bytes）を生成した。上の記述は**当時の測定**。**実機確認は未実施**（デバイス未接続）。

### 実装中に新たに判明した未着手の面

| 面 | 状態 |
|---|---|
| ~~**proto の承認型**~~ | **完了（2026-09-28）** — 上記の表を参照。`SafetyLevel.LEVEL_2_APPROVAL` だけは意図的に残置 |
| **`aegis_ai/permissions/`** | `ServicePermissionPolicy` / `ServicePermissionStore` が `ask_approval` / `requires_approval` を持つ**第三の承認面**。`ai-server/src` に**本番呼び出し元がゼロ**（参照はテストのみ）。丸ごと孤立 — **オーナー判断待ち**（削除には `test_goal_alignment.py` / `test_mission_contract_acceptance.py` の改修が伴う） |
| **`agents/profiles`** | `requires_approval_for` リストと `Profile.requires_approval()` — もう一つの独立した承認面 |
| **`motivation_arbiter`** | `requires_approval` フィールドを自前の dataclass に持つ |
| **`reflection_engine.py:254`** | `{"approval_needed", "waiting_approval"}` という**到達不能な status 集合**を判定。**同日さらに追跡**（下記） |
| **承認レッスン系（書き手のいない読取系）** | `reflection_engine.reflect(approval_decisions=...)` は **src・tests のどちらからも渡されない**（`autonomous_loop.py:994` と `tests/test_personal_ai_foundation.py:426` の 2 箇所のみ、どちらも未指定）→ 常に `[]`。したがって `_classify_outcome` の `_OUTCOME_REJECTED`、`_identify_root_cause` の "Approval rejected"、`_classify_failure` の `APPROVAL_REJECTED` / `APPROVAL_EXPIRED`、`reflect()` 内の `MemoryType.APPROVAL_LESSON` 書き込みは**すべて到達不能**。その結果 `approval_lesson` メモリを読む 3 箇所（`context_builder.py:326`、`autonomous_loop.py:1333`、`motivation_arbiter.py:162`）も**常に空**。書き手が死んでいるので読取側も空振りする、という**閉じた死角** — **オーナー判断待ち**（`FailureType` は `structured_data["failure_type"]` として永続化されるため、メンバ削除は保存済みメモリとの互換判断を伴う） |
| **`web-ui` の承認 UI** | `/api/approvals/*` は 5a で事後可視化として稼働中（`resource_routes.py:601`）。D4=(b) の範囲 |

---

## 当初の提案本文（実装前の記録）

---

## 0. まず前提の訂正

引き継いだ計画は Phase 5b の対象を
`llm_task_interpreter._validate_plan` と `l2_mind._requires_approval` としていたが、
**`_validate_plan` は存在しない**（`ai-server/src` と `ai-server/tests` を検索して 0 件）。

実際の強制ルールは `llm_task_interpreter._validate_safety`（269–314行、180行で呼ばれる）
にインラインで並んでいる **6 ルール**である。

---

## 1. 検証済みの強制マップ

| # | ルール | 位置 | 設定するもの | **実際に拘束するか** |
|---|---|---|---|---|
| R1 | `not enabled` または `risk ∈ {forbidden, blocked}` | 277–280 | `risk_category = BLOCKED` + `requires_approval` | **する（唯一）** |
| R2 | `capability.requires_approval` または `risk ∈ {approval_required, high, critical}` | 281–283 | `approval_needed = True` | **しない** |
| R3 | delegation_context の次元値（scope/audience/content_sensitivity/reversibility） | 285–299 | `approval_needed = True` | **しない** |
| R4 | `risk_category == EXTERNAL_SEND` | 301–304 | `approval_needed = True` | **しない** |
| R5 | `risk_category == DEVICE_ACTION` | 306–309 | `approval_needed = True` | **しない** |
| R6 | `risk_category == PAYMENT` | 311–314 | `approval_needed = True` | **しない（かつ到達不能）** |
| — | `l2_mind._requires_approval` | l2_mind 393–402 | `approval_needed` + `step.requires_approval` | **しない** |

### R1 だけが拘束する理由

`risk_category == BLOCKED` は `task_plan.has_blocked_steps()` 経由で
**`interaction/router.py:119–125`** が読み、タスク全体を失敗させる（"Some actions are blocked"）。
これは承認ではなく**拒否**である。

### R2〜R6 が拘束しない理由（4点で確認）

1. `execution_engine.py` に承認ロジックが無い。唯一の "approval" 文字列は
   `"no approval signal is required"` という**設計意図の表明**（209行・490行）。
2. `approval_needed` の読み手は4箇所だけで、どれも実行を止めない:
   - `web/chat_service.py:82` — タスクを**完了させない**だけ（ツールは実行済み）
   - `web/routes/chat.py:209,214–215` — レスポンス payload に載せるだけ（結果は生成済み）
   - `grpc_server.py:297` — 素通し
   - `web-ui/src/components/ChatDrawer.tsx:36–42` — **ログ行を1行足すだけ**
3. `web/chat_tools.py:51` は `"approval_needed": False` を**ハードコード**している。
   コメントに「approval is no longer a constraint (2026-09-27), so they can never be anything else」。
4. `PlanStep.requires_approval` は `task_plan.py:69` で**シリアライズされるだけ**で、
   読み手が1つも無い。

> **結論**: R2〜R6 は既に死んでいる。Phase 5b の本体は「拘束するルールを外す」ことではなく、
> **死んだ配線を撤去し、R3 を本来の置き場所（delegation policy）へ移す**ことである。

---

## 2. ルール単位の置換案

### R1 — `not enabled` / `risk ∈ {forbidden, blocked}` → BLOCKED

**判定**: 唯一の拘束ルール。**承認ゲートではなく拒否**なので、原則として残す。

**置換案**: 2つの理由を分離し、無意味な `requires_approval = True` を削除する。

| 条件 | 現在 | 置換後 |
|---|---|---|
| `not enabled` | BLOCKED + requires_approval | **BLOCKED のみ**（ケイパビリティが切られている） |
| `risk ∈ {forbidden, blocked}` | BLOCKED + requires_approval | **BLOCKED のみ**（明示的な拒否リスト） |
| — | `step.requires_approval = True` | **削除**（誰も読まない） |

**根拠**: オーナーの定義は「承認を強制する仕組みを消す」であって
「ケイパビリティを無効化する手段を消す」ではない。`enabled=False` は承認概念ではない。

**判断が必要な点**: `risk ∈ {forbidden, blocked}` を拒否軸として残すか。
単一制約下で唯一の構造的制約は egress なので、`forbidden` を
「能力の無効化」と同義に格下げする選択肢もある。

---

### R2 — `capability.requires_approval` / `risk ∈ {approval_required, high, critical}`

**判定**: 非拘束。

**置換案**: **承認分岐を削除し、注記に置換。**

```python
# 現在
elif requires_approval or risk in {"approval_required", "high", "critical"}:
    step.requires_approval = True
    plan.approval_needed = True

# 置換後（D5=(b)「risk は注記として残す」）
elif requires_approval or risk in {"approval_required", "high", "critical"}:
    plan.risk_notes.append(f"high-risk capability: {step.capability_id} (risk={risk})")
```

**副次的な発見**: `capability.requires_approval` 自体が
`capability_catalog.py:96 aligned_policy()` と `:721` で **`risk` ラベルから再導出**されている。
つまり R2 は同じ事実を二重に導出しており、片方は冗長。

---

### R3 — delegation_context の次元値 → 承認 ★最重要

**判定**: 非拘束。ただし**このルールだけは置換に実質的な意味がある**。

**現状の問題**: `_validate_safety` が次元値の集合をハードコードしている。

```python
str(delegation.get("scope")) in {"user", "system", "external"}
or str(delegation.get("audience")) in {"shared", "public", "third_party"}
or str(delegation.get("content_sensitivity")) in {"personal", "confidential", "secret"}
or str(delegation.get("reversibility")) in {"difficult", "irreversible"}
```

同じ語彙・同じ次元を `personal_ai/delegation.py` の
`DelegationPolicyStore.evaluate()` も持っている。**ポリシーが2箇所に分裂している。**

**置換案**: 承認フラグではなく **delegation policy の判定結果**に置き換える。

```python
decision = self._delegation_store.evaluate(
    step.capability_id,
    operation_context=dict(step.delegation_context or {}),
)
if decision.decision == "forbidden":
    step.risk_category = RiskCategory.BLOCKED
    plan.risk_notes.append(f"Delegation policy denies {step.capability_id}: {decision.reason}")
elif decision.decision == "auto_allowed":
    pass  # 続行。注記のみ
```

**利点**:
- 次元の解釈が `safety_vocab` + `DelegationPolicyStore` の**1箇所**に統一される
- ユーザーは `delegation_policy.upsert`（5a で追加済み）で自分のルールを書ける
- `forbidden` は承認ではなく**拒否**として扱われる（R1 と同じ軸に乗る）

**注意**: `evaluate()` はルール未一致時に `auto_allowed` へフォールスルーする。
次元を `unknown` にすると**マッチが緩む**方向に働く（既知の性質、テストで固定済み）。

---

### R4 — `EXTERNAL_SEND` → 承認

**判定**: 非拘束。

**置換案**: **削除し、注記に置換。**

**安全性の根拠（重要）**: 外部送信を止めているのは承認ではない。
`egress/gate.py` が deny-by-default・fail-closed・「no consent exception」で
**構造的に**拒否している。R4 を消しても egress の防御は1ミリも弱まらない。

**副次的な発見**: `EXTERNAL_SEND` は `l2_mind._risk_category_for_capability:385–386` で
`APPROVAL_REQUIRED` / `MEDIUM` から生成される。
つまり**実際に外部送信するとは限らない**ケイパビリティが `EXTERNAL_SEND` と名付けられている。
名前が実態を過大に表現している。

---

### R5 — `DEVICE_ACTION` → 承認

**判定**: 非拘束。

**置換案**: **削除し、注記に置換。**

**根拠**: このルールは北極星と直接矛盾する。
PC・Android・room の操作は AEGIS が存在する理由そのものであり、
ここに強制承認を残すと「AEGIS がやるために存在することを、AEGIS が止まる」ことになる。
承認撤去の目的はまさにこの摩擦の除去である。

---

### R6 — `PAYMENT` → 承認

**判定**: 非拘束、**かつ到達不能**。

**発見**: `RiskCategory.PAYMENT` は**どこからも代入されていない**。
唯一の出現は 312 行の**チェック側**のみ。
`_risk_category_for_capability` も `_parse_risk` も PAYMENT を生成しない
（`_parse_risk` は LLM が `"PAYMENT"` と書けば生成しうるが、ケイパビリティからは導出されない）。
**「宣言されているが効果がない」バグ類型の再発。**

**置換案**: ルールを削除する。拒否は既に別の場所にある。

`delegation.evaluate()` が `operation_category == "payment"` に対して
`forbidden` を返す（`default_payment_deny`、190–196行）。
これが **D1=(b)「支払いはハード拒否のまま」を満たしている。**

**提案（任意）**: 支払いの拒否を呼び出し側の `operation_category` 宣言に依存させず、
第一級の構造的拒否に格上げする。現状は宣言漏れがあると
`_normalize_context:241–244` の side_effects 推論にしかフォールバックがない。

---

### `l2_mind._requires_approval`（393–402）

**置換案**: **削除。**

`approval_needed` と `PlanStep.requires_approval` に流れるだけで、どちらも読まれない。

**ただし `_risk_category_for_capability`（380–391）は残す。**
これは `risk_category` を生成しており、R1 の BLOCKED がこれに依存している。

---

## 3. 併せて撤去する死んだ面

| 対象 | 場所 | 対応 |
|---|---|---|
| `PlanStep.requires_approval` | `task_plan.py:69` | 削除（読み手ゼロ） |
| `TaskPlan.approval_needed` | `task_plan.py:135` | 削除、または互換のため常時 False で残す |
| `chat_tools.py` の定数 | `web/chat_tools.py:51` | 既に False。削除 |
| `ChatDrawer` のログ行 | `web-ui/.../ChatDrawer.tsx:36–42` | 事後可視化（不可逆台帳）へのリンクに置換 |
| タスク完了条件 | `chat_service.py:82` / `routes/chat.py:209` | `needs_user_input` のみで判定するよう変更 |
| proto の承認型 | `ApprovalRequest` / `ApprovalStatus` / `ApprovalType` / `ApprovalAction` | 削除は Kotlin/Rust に波及 → **Technology Decision Gate** → **実施済み（2026-09-28）** |

> 上表 6 件はすべて実装済み。`SafetyLevel.LEVEL_2_APPROVAL` のみ記述的ラベルとして残置。

---

## 4. 撤去後も残る防御（安全性の担保）

| 防御 | 実装 | 状態 |
|---|---|---|
| 外部送信 | `egress/gate.py` deny-by-default、CI 床160、mutation 証明 | 無傷 |
| 支払い | `delegation.evaluate()` の `default_payment_deny` | 無傷（D1=(b)） |
| 無効化されたケイパビリティ | R1 の BLOCKED → タスク失敗 | 維持 |
| ゲート迂回 | ToolBroker + AuditManager 不変条件 | 無傷 |
| AEGIS が自主的に確認する | `confirmation/`（5a） | 維持 |
| 事後可視化 | `irreversibility.py` 台帳 | 維持 |

**R2〜R6 を消しても防御は減らない。** それらは既に何も止めていないため。

---

## 5. 推奨する実施順

| 順 | 対象 | 挙動変化 | リスク |
|---|---|---|---|
| 1 | R6 削除 | なし（到達不能） | ゼロ |
| 2 | R4・R5 削除 → 注記 | なし | ゼロ |
| 3 | R2 削除 → 注記 | なし | ゼロ |
| 4 | 死んだ面の撤去（§3） | なし（表示のみ変化） | 極小 |
| 5 | **R3 → delegation policy へ移設** | **あり**（唯一） | 中。要テスト |
| 6 | R1 の分離 | あり（`forbidden` 軸の扱い次第） | 要オーナー判断 |

1〜4 は**挙動を変えない純粋な削除**なので、まとめて1回で実施できる。
5 だけが実質的な変更で、`test_forced_gate_stays_retired.py` の思想
（「store にブロッキング API を持たせない」「実行経路は confirmation を import しない」）と整合する。

---

## 6. オーナーの判断が必要な点

1. **`risk ∈ {forbidden, blocked}` を拒否軸として残すか**（R1 の分離）
2. **R3 を delegation policy へ移設してよいか** — 唯一の挙動変化
3. **proto の承認型を削除するか** — Kotlin/Rust に波及（Technology Decision Gate）
4. **支払いの拒否を第一級の構造的拒否に格上げするか**

> **結果（2026-09-28・オーナー決定済み）**: ①残さない ②承認 ③削除する（Technology Decision
> Gate は「開発プロセスの規則」であり実行時のゲートではないため、抵触しないと判断）④不要。
> 上記 4 点はすべて決着し、実装済み。この節は**判断前の記録**として残す。

---

## 付録: 検証方法

すべて `grep` と実ファイル読みで確認。推測なし。

```
_validate_plan                     → src/tests で 0 件（存在しない）
_validate_safety                   → llm_task_interpreter.py:269（180 で呼出）
risk_category == BLOCKED の読み手  → interaction/router.py:120 のみ
approval_needed の読み手           → chat_service.py:82 / routes/chat.py:209,214
                                     grpc_server.py:297 / ChatDrawer.tsx:36
execution_engine の承認ロジック     → なし（209・490 は「不要」と述べる文字列のみ）
PlanStep.requires_approval の読み手 → task_plan.py:69（シリアライズのみ）
RiskCategory.PAYMENT の代入         → 0 件（312 のチェックのみ）
payment の拒否                     → delegation.py:190–196 default_payment_deny
```
