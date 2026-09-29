はい。これまでのAEGISの方針を維持しつつ、**LLMをL1/L2/L3の3層に分けることだけをアーキテクチャとして追加**するなら、次の計画が一番自然です。

ポイントは、単純な「賢さの違う3つのLLM」ではなく、

> **L1 = 常時動く知覚・判断・ルーティング層**
> **L2 = 定期的に世界全体を考える自律思考層**
> **L3 = 本当に難しい問題を解く深層思考層**

と役割を明確に分けることです。

## 1. 全体構造

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
                         │        EventBus      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                 ┌──────────────────────────────────┐
                 │              L1                   │
                 │     Perception / Router           │
                 │                                  │
                 │ ・最新情報の監視                  │
                 │ ・ユーザー状態の観測              │
                 │ ・イベントの意味理解              │
                 │ ・価値 / 重要度判断               │
                 │ ・必要な知能量の判断              │
                 │ ・L2/L3へのエスカレーション      │
                 │ ・簡単な指示の遂行                │
                 │ ・MCPへの接続                     │
                 └───────┬──────────────┬───────────┘
                         │              │
                    簡単なTask       深い判断が必要
                         │              │
                         ▼              ▼
                  ┌────────────┐   ┌────────────────┐
                  │ MCP / Tool │   │       L2       │
                  │ Execution  │   │ Autonomous Mind│
                  └────────────┘   └───────┬────────┘
                                           │
                                  難易度・重要度判定
                                           │
                                  ┌────────┴────────┐
                                  │                 │
                               L2で解決          L3が必要
                                  │                 │
                                  ▼                 ▼
                             行動計画           ┌────────┐
                                                │   L3   │
                                                │ Deep   │
                                                │ Reason │
                                                └───┬────┘
                                                    │
                                                    ▼
                                                  L2
                                                    │
                                                    ▼
                                                 Action
```

---

# 2. L1 ― 常時動作する「神経系」

ここが今回の変更で最も重要です。

L1は**AEGISの主役ではなく、世界とAEGIS内部を常時観測する層**です。

### L1が見るもの

既存のEvent/Server構造から、

* PC
* Android
* Browser
* Room
* Discord / AGORA
* Web
* SNS
* News
* Memory
* Task
* 現在のAEGIS状態
* ユーザーの操作
* カメラのイベント
* 各種センサー

などを受け取ります。

ただし、生データを無条件に全部L2へ渡すのではありません。

### L1の基本処理

```text
Event
 ↓
意味を理解
 ↓
価値を評価
 ↓
重要度を評価
 ↓
今処理する必要があるか？
 ↓
必要な知能量を推定
 ↓
┌──────────────┬──────────────┬──────────────┐
│              │              │
L1で処理       L2へ           L3へ
```

例えば、

```text
「電気をつけて」
```

なら、

```text
L1
 ↓
意図理解
 ↓
単純Task
 ↓
MCP
 ↓
照明ON
```

で終わります。

逆に、

```text
「最近AI業界で何が起きてる？」
```

なら、

```text
L1
 ↓
最新情報が必要
 ↓
Web/SNSを調査
 ↓
情報を整理
 ↓
L2へ
```

となります。

---

# 3. L1は「情報圧縮器」でもある

これは以前のAEGISのコスト問題とも整合します。

L1が、

```text
1000件のイベント
```

をそのままL2へ送るのではなく、

```text
1000 events
      ↓
      L1
      ↓
重要な変化 8件
ユーザー状態 2件
新しいTask 1件
Memory候補 3件
異常 1件
```

のようにします。

L2には、

> **「世界で何が起きたか」**

ではなく、

> **「世界で何が変化し、それがAEGISにとって何を意味するか」**

を渡します。

これは以前考えていた**大量の更新頻度の高い情報を次段階へ必要な場合だけ渡す**という設計にそのまま繋がります。

---

# 4. ユーザー観測もL1

ここも今回明確化します。

例えばRoomカメラで、

```text
人物が立ち上がった
```

という動作検知イベントが発生した場合、

L1は単に

```text
motion = true
```

とするのではなく、

```text
何が起きた？
↓
誰か？
↓
ユーザーか？
↓
何をしている可能性がある？
↓
AEGISが反応する価値がある？
↓
追加観測が必要？
↓
L2に渡す価値がある？
```

を判断します。

PCでも同様に、

```text
ブラウザを開いた
Discordを開いた
GitHubを開いた
コードを書いた
ゲームを起動した
```

というイベントを**ユーザーの意図・状況の変化として解釈する入口**をL1にします。

ただし、単なる操作ログを「意図」と断定するのではなく、L1の判断結果として

```text
observed_action
possible_intent
confidence
value
```

のように扱います。

---

# 5. L2 ― AEGISの「自律的な思考」

L2はL1とは性質が違います。

L1が

> 「今何が起きている？」

を考えるなら、L2は

> **「それらを踏まえてAEGISは何をすべきか？」**

を考えます。

### L2を起動する条件

基本的には、

* 定期的な思考タイミング
* L1からのエスカレーション
* 重要イベント
* 大きな状態変化
* 新しい情報の蓄積
* Taskの停滞
* Memory更新
* Desire/Goalの変化
* L1では判断できない状況

など。

したがって「数十分に一度」という既存方針は残しつつ、**重要なイベントが発生した場合には待たずに起動できる**ようにします。

---

# 6. L2にはMemory/Desire/Taskを統合して見せる

これまでのAEGIS設計を崩さず、

```text
                 L2
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    Memory      Desire      Task
       │          │          │
       └──────────┼──────────┘
                  ▼
             Current World
                  │
                  ▼
             Decision
```

とします。

特に以前の方針だった、

* Memory
* Identity
* Goals / Desire
* Sleep
* Event
* Task

を混ぜて一つの巨大な状態にするのではなく、**L2がそれぞれを参照して判断する**形にします。

---

# 7. L3 ― 「本当に難しいこと」専用

L3は常時動かしません。

L2自身が、

> 「自分の推論能力では十分でない」

と判断したときだけ呼びます。

例えば、

* 非常に複雑な設計
* 長期的な計画
* 難しい技術問題
* 複数分野を跨ぐ問題
* 大規模なコード変更
* L2同士で判断が割れる問題
* 未知の問題
* L2がconfidenceを十分に持てない問題

など。

L3の結果は直接世界を操作するのではなく、

```text
L3
 ↓
Reasoning / Plan / Recommendation
 ↓
L2
 ↓
Validation
 ↓
Task
 ↓
MCP
```

と戻します。

**これによりL3が勝手にAEGIS全体を制御するのではなく、L2が最終的な自律実行主体になります。**

---

# 8. L1/L2/L3と既存Managerの関係

以前決めたManager構造も維持します。

```text
LLM Layer
────────────────────

L1
 ↓
L2
 ↓
L3
 ↓
L2
 ↓

Manager Layer
────────────────────

Task
 ↓
Memory
 ↓
Event
 ↓
Audit
 ↓
Status
 ↓
Notification
```

LLMはManagerを直接勝手に管理するのではなく、**Managerを介してAEGISの状態を変更する**ようにします。

これによって、

```text
LLM
 ↓
Intent
 ↓
Manager
 ↓
State
```

という一貫した流れになります。

---

# 9. Sleepとの統合

以前の「Sleep＝忘却ではなくMemory consolidation」という方針もそのまま残します。

Sleepは、

```text
L1/L2/L3が活動
       ↓
大量の経験・イベント
       ↓
Sleep
       ↓
Memory整理
       ↓
行動傾向の整理
       ↓
重要情報の統合
       ↓
次の活動
```

とします。

そしてSleep中に、

* Memory consolidation
* 重複情報の統合
* 行動パターン抽出
* 長期的な傾向の更新
* Desire/Goalへの影響
* 不要な一時情報の整理

を行います。

**Sleep自体をL3専用処理にする必要はありません。**
必要な部分だけ適切なLLM層を使える構造にします。

---

# 10. Dashboardも3層対応にする

以前の計画で重要だった、

> **AEGIS内部で何が起きているかをできる限り全部見られるDashboard**

を3層構造に合わせます。

例えば、

```text
AEGIS Dashboard

┌─────────────────────────────────┐
│ Current Activity                │
│ L1: analyzing user movement...  │
└─────────────────────────────────┘

L1
├─ Events
├─ Observations
├─ Value judgments
├─ Routing decisions
├─ MCP calls
└─ Escalations

L2
├─ Current reasoning
├─ Current goal
├─ Active desires
├─ Tasks
├─ Context
└─ Decisions

L3
├─ Invocation reason
├─ Problem
├─ Context
├─ Result
└─ Returned plan

Memory
Task
Event
Audit
Status
Notification
```

そして以前指定した**リアルタイム1行Overlay**は、

```text
L1: ユーザーの操作を分析中
L1: 最新ニュースの重要度を評価中
L2: 今日のイベントを統合中
L2: Task「X」の実行計画を検討中
L3: 複雑な設計問題を分析中
MCP: Discordへのメッセージ送信を実行中
```

のように、**現在実行中の最も重要な活動を1行だけ表示**します。

---

# 11. 重要なのは「LLMの呼び出し階層」と「思考階層」を分離すること

ここは実装時にかなり重要です。

例えば、

```text
L1 → L2 → L3
```

という呼び出し関係だけにしない。

実際には、

```text
             Event
               │
               ▼
              L1
        ┌──────┼───────┐
        ▼      ▼       ▼
       MCP    L2      NOOP
               │
         ┌─────┼─────┐
         ▼     ▼     ▼
        MCP   L3    L2自身
                │
                ▼
                L2
```

とします。

つまり**L3から直接MCPを実行させる必要はありません。**

L3は「考える」。

L2は「決める」。

L1は「観測して振り分ける」。

MCP/Capabilityは「実行する」。

この責任分離が重要です。

---

# 12. 実装フェーズ

既存AEGISを壊さず移行するなら、順番はこうします。

### Phase 1 — LLM Gatewayを作る

現在各所から直接LLMを呼んでいる部分を、

```text
LLM Gateway
```

に集約。

```text
L1.request()
L2.request()
L3.request()
```

という抽象化にします。

この段階ではモデル自体は変更しません。

---

### Phase 2 — L1 Router

既存EventBusからL1へイベントを流す。

L1の出力を、

```text
Observation
Decision
Value
Priority
RequiredIntelligence
Action
Escalation
```

として構造化します。

---

### Phase 3 — L1 MCP Executor

簡単な操作をL1からCapability/MCPへ繋ぎます。

```text
User command
 ↓
L1
 ↓
Capability
 ↓
MCP
 ↓
Result
 ↓
L1
```

---

### Phase 4 — L2 Autonomous Mind

現在のAutonomous Loop / Desire / Task / MemoryをL2に統合。

L2が定期的に、

```text
World state
+
Memory
+
Desire
+
Task
+
L1 summaries
```

を見て行動を決める。

---

### Phase 5 — L3 Escalation

L2に、

```text
difficulty
confidence
required_capability
```

などを持たせ、

```text
confidence低
OR
difficulty高
OR
importance高
```

ならL3へ。

---

### Phase 6 — Dashboard/Overlay

最後に3層を完全に可視化。

```text
L1
 ↓
L2
 ↓
L3
```

の状態、入力、判断、出力、Tool実行、エラーをAuditとリアルタイムUIへ流します。

---

# 最終的なAEGIS

最終的にはこういう思想になります。

```text
                 ┌──────────────────┐
                 │      WORLD       │
                 │ User / Web / PC  │
                 │ Phone / Room     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │       L1         │
                 │  Always Awake    │
                 │                  │
                 │ Observe          │
                 │ Understand       │
                 │ Evaluate         │
                 │ Route            │
                 │ Execute simple   │
                 └──────┬───────────┘
                        │
             ┌──────────┼──────────┐
             ▼          ▼          ▼
           MCP        L2         Ignore
                        │
             ┌──────────┼──────────┐
             ▼          ▼          ▼
          Memory      Desire      Task
                        │
                        ▼
                       L2
                        │
                 hard / uncertain
                        │
                        ▼
                       L3
                        │
                        ▼
                       L2
                        │
                        ▼
                  Task / Action
                        │
                        ▼
                     World

              ─────────────────────
                     Sleep
              ─────────────────────
              Memory consolidation
              Experience integration
              Behavioral patterns
              Goal/Desire evolution
```

この構造なら、これまでのAEGISの**「人間レベルの権限を持ち、人間に似た言動をする超有能な秘書」**という方向性を崩さず、今回のL1/L2/L3を自然に組み込めます。

特に重要なのは、**L1を単なる安い分類器にしないこと**です。L1はAEGISが世界と接する常時稼働の「認知ゲート」であり、L2が自律的な意思決定、L3が深い問題解決を担当する、という3層にすると、これまで作ってきたEventBus・Memory・Desire・Task・Capability・Sleep・Dashboardの設計ともかなり綺麗に接続できます。
