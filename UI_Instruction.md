# AEGIS Spatial Information Design 再設計計画

## 1. 調査結果

### Googleの`DESIGN.md`について

ユーザーが言及したものは、Google LabsのStitchに追加された`DESIGN.md`を指している可能性が高いです。

報道されている`DESIGN.md`の役割は、個別画面のCSSではなく、次のような**プロジェクト全体のデザイン言語を保存し、別画面や別プロジェクトでも再利用すること**です。

* 色
* タイポグラフィ
* 形状
* 余白
* コンポーネント
* デザイン原則
* 画面間の一貫性

Stitch自体も、プロンプトや画像から高品質なUIとコードを生成し、デザインシステムを複数画面へ継承する方向へ進化しています。現時点では、Google公式の詳細な`DESIGN.md`仕様書そのものは確認できず、機能の存在と概要はStitch更新に関する報道に基づきます。

AEGISでも、現在の`tokens.json`だけでなく、**色・奥行き・動き・形・情報優先度・デバイス別適応を含む`DESIGN.md`**を作るべきです。

---

## 2. 現在の球体がダサく見える技術的理由

### 2.1 数学的には3Dでも、視覚的にはほぼ2D

現在のServer Arcは半径`2.05`の円に対し、Z方向の変化が最大約`0.18`しかありません。

```text
x = cos(t) × 2.05
y = sin(t) × 2.05
z = sin(t × 1.7) × 0.18
```

つまり、リングはほぼ同じ平面に重なっています。視差、前後関係、深い交差、遠近差が弱く、正面から見ると「円の周囲に線を置いたもの」に見えます。

### 2.2 Server Arcが光に反応しない

Arcは`MeshBasicMaterial`を使用しています。これは照明計算を行わないため、SceneにAmbientLightやPointLightを置いても、Arcの材質には立体的な陰影が付きません。

結果として、

* 表面の向き
* 光源との距離
* 手前と奥
* 材質の厚さ
* 反射
* 影

が見た目に反映されず、「発光する線画」に留まっています。

### 2.3 中央球体の内部構造がない

中央は一枚のSphereGeometryと、Fresnel輪郭、わずかな頂点変形だけです。内部コア、複数シェル、粒子、流体、エネルギー経路、屈折などがありません。

したがって、近づいて見ても新しい情報がなく、単なる半透明のボールに見えます。

### 2.4 動きが状態ではなく装飾

現在の主な常時動作は、

* 全体回転
* 球体の呼吸
* Event時のScale変更
* 色とOpacityの補間
* Recovery ringの回転

です。

「回っている＝何か処理している」以上の意味がなく、

* どこから情報が入ったか
* どこへ送ったか
* 何を選択したか
* どこで停止したか
* 何が原因で失敗したか

を伝えていません。

Googleのアニメーションガイドでも、アニメーションはAppearance、Content transition、Value change、状態遷移などを理解しやすくするためのものとして整理されています。常時回転を増やすことではなく、変化の意味を伝えることが重要です。

### 2.5 色に役割を詰め込みすぎている

現在は同じ色が複数の意味を持ちます。

* Cyan：通常、Online、Pulse、AI本体

* White：Active、Complete

* Amber：Degraded、Approval、Containment

* Red：Offline、Disconnect、Failure、Critical

* Green：Recovery

* Violet：Next server

色だけでは、

```text
これはデータの種類なのか
状態なのか
優先度なのか
処理段階なのか
```

を区別できません。

### 2.6 3DシーンとDOMが別世界に見える

Canvasの下にServer legendと、

```text
Mode / Health / Confidence
```

のCaptionが置かれています。

これにより「映画内の一体化したインターフェース」ではなく、「WebページにThree.jsのデモを置いたもの」に見えます。

---

# 3. UIに追加すべき「表示の次元」

画面の次元とは、単なる3D座標ではありません。

AEGISでは、少なくとも次の8つを同時に使います。

| 情報軸    | 表現手段                |
| ------ | ------------------- |
| 情報の種類  | 色相、空間領域             |
| 重要度    | サイズ、輝度、手前への移動       |
| 状態     | 形状、線種、動作パターン        |
| 時間     | 奥行き、残像、Timeline上の位置 |
| 因果関係   | 方向を持つ線、伝播する光        |
| 確信度    | 焦点、輪郭、ノイズ、透明度       |
| 活動量    | 流量、密度、速度            |
| 対応の必要性 | 動きの停止、隔離、画面占有率      |

色はその一つにすぎません。

---

# 4. Googleのデザイン原則から採用するもの

Material 3では、デザインを単一の配色ではなく、**Color、Typography、Shapeの連携したシステム**として扱っています。Material 3 Expressiveも、色、形、サイズ、動き、タイポグラフィを協調させ、重要要素の発見や操作性を高める方向です。

報道されたGoogleの調査では、Material 3 Expressiveは多数の研究ラウンドと参加者による評価を経て、重要なUI要素の発見速度などを改善したとされています。これは「派手さ」ではなく、表現力を情報階層に利用する考え方です。

Android XRの公式ガイドでも、平面画面の制限を超える方法として、

* Spatial panel
* Spatial elevation
* 3D element
* Scale
* Depth
* Dynamic environment
* Motion

が挙げられています。AEGISはXRではありませんが、前後関係、遮蔽、視差、焦点、空間分割という原則は通常のディスプレイにも応用できます。

---

# 5. 球体を廃止し、Cognitive Fieldへ変更する

## 基本構造

中央に一つの物体を置くのではなく、画面全体をAEGISの内部空間として使います。

```text
Z -1200  Environment / Atmosphere
Z  -800  Memory Field
Z  -450  System Topology
Z     0  Mission Plane
Z  +250  Active Execution
Z  +500  Attention
Z  +900  Critical Takeover
```

### L0：Environment

最も奥に置くもの：

* 微細な空間グリッド
* Context Horizon
* 全体Confidence
* 時刻や環境状態
* 非常に遅い粒子

ここでは情報を主張しない。

### L1：Memory Field

現在使われた記憶だけを、遠方の光の帯として配置する。

* Episodic
* Semantic
* Procedural
* User preference
* Recent context

Memoryから現在Taskへ、必要な瞬間だけ光が流れる。

### L2：System Topology

AI、PC、Android、Browser、Room、Devを、同心円ではなく奥行きの異なる領域に置く。

サーバーごとに固定色を与えるのではなく、**機能領域として場所を固定**する。

```text
左奥    Perception / Browser
右奥    Memory
左手前  PC / Physical action
右手前  Android / Communication
上部    Policy / Security
下部    Task / Time
中央    Cognition
```

視線を見れば、どの領域が動いたか分かる。

### L3：Mission Plane

現在Taskを、中央から伸びる一本の経路として表示する。

```text
Observe
→ Understand
→ Plan
→ Approve
→ Execute
→ Verify
→ Complete
```

過去は奥へ、現在は焦点面へ、次の処理は手前へ配置する。

### L4：Execution Field

実行中のCapabilityだけを前面へ出す。

* 方向を持つData packet
* 対象への光路
* 実行時間
* Input／Output要約
* Progress

### L5：Attention

重要通知は平面的なカードとして重ねず、該当する領域から前方へ浮上させる。

### L6：Takeover

Critical時だけ通常の空間を後退させ、原因・影響・復旧経路を手前へ展開する。

---

# 6. 新しい色の設計

## 6.1 色を「情報領域」に割り当てる

| 情報領域                  | 基準色            |
| --------------------- | -------------- |
| Cognition／Planning    | Violet         |
| Observation／Sensors   | Cyan           |
| Task／Execution        | Electric blue  |
| Memory／Context        | Indigo–Magenta |
| User／Communication    | Rose           |
| Device／Infrastructure | Teal           |
| Policy／Approval       | Amber          |
| Security／Critical     | Red            |
| Recovery              | Green、ただし一時的   |

Materialの色設計でも、Primary、Secondary、Tertiaryなどの役割を定義し、色を用途に応じて使い分けます。AEGISでも、単純なステータス色ではなくRole-based colorを採用します。

## 6.2 状態は色相以外でも表す

| 状態       | 色以外の表現             |
| -------- | ------------------ |
| Planned  | 点線、低輝度、ゆっくり前進      |
| Active   | 実線、明るい、方向流         |
| Waiting  | Gateで停止、周期の遅いPulse |
| Approval | Amberの隔離境界         |
| Stale    | 低彩度、輪郭の揺れ、時刻表示     |
| Failed   | 線の断絶、粒子の散逸         |
| Offline  | 領域の暗転、接続線の消失       |
| Recovery | 逆方向の再構築            |
| Complete | 白い通過波の後、元の領域色へ戻る   |

Recovery完了後も緑色のままにしない。緑は「復旧の瞬間」だけに使う。

---

# 7. Motion Grammar

すべての動きへ意味を割り当てます。

## Ambient

```text
周期：12～20秒
動き：非常に遅い漂い
意味：システムが生きている
```

主視線を奪わない。

## Observation

```text
時間：600～900ms
方向：外部領域 → Cognition
形：細い走査線、少量の粒子
```

どのデバイスから情報が来たかを示す。

## Planning

```text
時間：1～2秒
動き：経路が複数へ枝分かれ
終端：選択された経路だけが残る
```

## Execution

```text
時間：処理中継続
動き：Cognition → Capability → Target
形：方向を持つPacket
速度：処理進捗またはイベント頻度に対応
```

## Approval

```text
動き：Execution pathが減速
停止：Policy Gateの直前
状態：AmberのContainment field
```

## Failure

```text
初動：100～160msの急な断絶
収束：500～800ms
その後：静止したDiagnostic state
```

赤い点滅を続けない。

## Recovery

```text
Isolate
→ Restart
→ Reconnect
→ Verify
→ Resume
```

各段階を順番に再構築する。

Googleのアニメーション体系でも、Transition、Appearance、Content change、複数値の連動、EasingやSpringを用途に応じて使い分ける構成になっています。AEGISも単一の回転速度ではなく、意味ごとのMotion tokenを持つべきです。

---

# 8. Shape Grammar

MaterialのShapeは装飾ではなく、注意誘導、状態伝達、コンポーネント識別にも使われます。

AEGISでは次の形状規則を使います。

| 種類          | 形               |
| ----------- | --------------- |
| Observation | 細い開いた弧          |
| Memory      | 柔らかい帯、雲、結晶      |
| Planning    | 分岐する線           |
| Execution   | 明確な直線、矢印、Packet |
| Device      | 安定した六角形／プレート    |
| User        | 柔らかい円形          |
| Approval    | 閉じた境界、Gate      |
| Critical    | 鋭い断面、破断         |
| Recovery    | 再接続する曲線         |

すべてを丸いカードと丸いリングにしない。

---

# 9. 奥行きを本当に感じさせる技術

## 必須

* 手前と奥で明確に異なるScale
* 物体同士のOcclusion
* Perspectiveによる大きさの差
* 微細なCamera parallax
* 奥ほど低いContrast
* Depth fog
* Focus plane
* 手前だけ高解像度
* 線やPanelに実際の厚み
* 光源からの距離による明暗

## 控えめに使う

* Bloom
* Chromatic aberration
* Depth of field
* Scanline
* Noise
* Lens flare
* Glass blur

Bloomを増やすだけでは立体感は出ません。光る物体の前後関係、遮蔽、材質、焦点差が必要です。

## 推奨Camera

現在の正面固定Cameraから、状態ごとの構図へ変える。

```text
Idle       34°、広い全景
Observing  情報源側へ2～4°回転
Planning   少し引いて分岐全体を表示
Executing  実行経路へ浅く寄る
Approval   GateへFocus
Critical   問題箇所へCutaway
Recovery   徐々に全景へ戻る
```

Cameraは常時回転させない。

---

# 10. 中央表現の状態変化

## Idle：Diffuse Intelligence

小さな粒子群と薄い神経線が漂う。

明確な球体を作らない。

## Observing：Convergence

外部から入った情報が中心へ収束する。

## Planning：Branching Lattice

複数の経路が立体的に分岐し、評価後に一本へ収束する。

## Executing：Directed Corridor

中心から対象へ、奥行きのある処理回廊を形成する。

## Approval：Contained Action

実行回廊をGateで遮断し、その内部にActionを隔離する。

## Critical：Diagnostic Cutaway

中央構造を分解し、障害箇所と因果関係を断面表示する。

## Recovery：Reassembly

分解された構造を順番に再構築する。

つまり、AEGISの状態が変わると「球体の色が変わる」のではなく、**空間の構造自体が変わる**ようにします。

---

# 11. Rendering Architecture

```text
AEGISScene
├─ EnvironmentLayer
├─ ContextHorizonLayer
├─ MemoryFieldLayer
├─ CognitiveFieldLayer
├─ SystemTopologyLayer
├─ MissionFlowLayer
├─ ExecutionLayer
├─ EventParticleLayer
├─ SpatialLabelLayer
├─ AttentionLayer
└─ TakeoverLayer
```

管理側：

```text
SceneDirector
├─ CurrentScene
├─ TargetScene
├─ TransitionPhase
├─ CameraTarget
├─ FocusEntity
├─ MotionBudget
├─ PriorityOwner
└─ ReducedMotionMode
```

### WebGLとDOMの分担

WebGL：

* 空間
* 経路
* 粒子
* 光
* 奥行き
* Camera
* Event propagation

DOM／SVG：

* 長文
* 数値
* Approval detail
* Accessibility
* Screen reader
* Takeover本文

文字まで無理にThree.js内へ置かない。ただしDOM PanelもWebGLのCamera位置と対応させ、同じ空間に浮いているように見せる。

---

# 12. AEGIS用`DESIGN.md`

リポジトリ直下に、次を含む`DESIGN.md`を作成します。

```markdown
# AEGIS Design Language

## Vision
Calm spatial intelligence, not decorative sci-fi.

## Information Dimensions
Domain, urgency, lifecycle, time, causality,
confidence, ownership, interaction.

## Semantic Colors
cognition, perception, action, memory,
communication, infrastructure, policy,
critical, recovery.

## Status Modifiers
planned, active, waiting, stale, failed,
offline, recovering, complete.

## Depth Model
environment, memory, topology, mission,
execution, attention, takeover.

## Motion Grammar
ambient, observe, plan, execute,
approve, fail, recover, complete.

## Shape Grammar
sensor, memory, plan, device,
user, policy, failure, recovery.

## Typography
display, operational, label, metric, mono.

## Scene States
idle, observing, planning, executing,
waiting, approval, critical, recovery, complete.

## Surface Adaptation
dedicated display, dashboard, Android,
PC overlay, room display.

## Accessibility
contrast, non-color encoding,
reduced motion, grayscale, privacy.

## Performance Budget
FPS, draw calls, particles, GPU memory,
pixel ratio, fallback level.

## Prohibited Patterns
meaningless rotation, all-cyan UI,
constant red flashing, glow-only hierarchy,
flat concentric rings, decorative metrics.
```

これを人間向けドキュメントとしてだけでなく、Coding AgentがUIを変更するときの制約として使用します。

---

# 13. デバイス別適用

## AI専用ディスプレイ

Cognitive Fieldを全面的に使用する。

* 空間演出
* Camera transition
* Mission flow
* Attention scene
* Diagnostic cutaway

を許可する。

## Webマスターボード

同じ色・形・Motion grammarを使うが、3Dは小型のInteractive Topologyへ限定する。

操作や文字の可読性を優先する。

## スマホ

3Dは使わず、Material 3 Expressiveを基礎にする。

* 色
* Shape
* Size
* Container transformation
* Shared-axis transition
* Spring motion

で同じ意味を2Dへ変換する。

## PC Overlay

動きはAppearance、Progress、Resolutionだけに限定する。

常時漂う粒子や3Dは使わない。

---

# 14. 実装手順

## Phase 0：3案を映像プロトタイプ化

本実装の前に、同じExecuting状態を次の3方向で作る。

1. Neural Loom
2. Holographic Machine
3. Mission Constellation

静止画だけでなく、5～10秒の状態遷移を作って比較する。

## Phase 1：DESIGN.md

Semantic color、Motion、Shape、Depthを確定する。

## Phase 2：CoreSphereを分解

`CoreSphere.tsx`を直接増築せず、

```text
CognitiveField
MissionFlow
SystemTopology
EventParticles
SceneCamera
```

へ分割する。

## Phase 3：Directional Event Flow

Eventに、

```text
source_entity
target_entity
direction
lifecycle
confidence
intensity
```

を追加する。

## Phase 4：Scene Morphing

Idle、Planning、Executing、Approval、Critical、Recoveryを別構造として作る。

## Phase 5：Spatial Typography

Current action、Next action、Server labelを、空間上の対象と対応させる。

## Phase 6：Performance fallback

* High：Full 3D＋Particles＋Post-processing
* Medium：3D topology＋軽量Bloom
* Low：Canvas／SVG 2.5D
* Reduced Motion：静的構造＋状態差のみ

---

# 15. 完了条件

* 球体を非表示にしても画面の中心構造が成立する
* 2秒以内にIdle／Executing／Approval／Criticalを区別できる
* 色を消しても状態をShapeとMotionで識別できる
* すべての大きな動きが実イベントと対応する
* 常時動く主役は最大一つ
* 情報の入力元と出力先が方向で分かる
* CurrentとNextが奥行きで区別できる
* Approvalの停止位置が見える
* Failureの原因と影響先が見える
* Recoveryの段階が見える
* Grayscale、色覚差、Reduced Motionで意味が失われない
* 1920×1080で安定60fpsを目標とする
* 低性能環境では自動的に軽量Rendererへ切り替わる
* 全SceneをVisual Regressionで比較する
* 装飾だけの回転、発光、数字を置かない
# AEGIS Master Dashboard 全面拡張計画

## 1. Dashboardの位置付け

Web Dashboardを、単なる状態表示画面ではなく、AEGIS全体のマスターコントロールプレーンとする。

Dashboardから次のほぼすべてへ到達できるようにする。

* 状態を見る
* 詳細を調べる
* 設定を変更する
* Taskを作成・停止・再開する
* Approvalを処理する
* Capabilityを管理する
* Memoryを検索・編集する
* Autonomous behaviorを調整する
* ServerやDeviceを操作する
* 障害を診断・復旧する
* Policyや権限を変更する
* LLM使用量を分析する
* イベントを追跡する
* Backup／Restoreを実行する
* テスト・監査・本番準備状況を確認する

ただし、生データを一画面へ並べるのではなく、すべての対象に共通して次の構造を持たせる。

```text
Overview
List
Detail
Relations
History
Configuration
Actions
Raw data
```

---

# 2. 新しい全体ナビゲーション

現在の7画面構成を、次の9領域へ再編成する。

```text
01 Command
02 Work
03 Intelligence
04 Capabilities
05 Infrastructure
06 Communications
07 Governance
08 Observability
09 Configuration
```

Developer機能は通常ナビゲーションから分離し、Developer Modeで追加表示する。

---

# 3. Command

## 3.1 Command Center

AEGIS全体の現在状態を表示する。

### 表示項目

* Core Health
* Current Mode
* Current Goal
* Current Task
* Current Action
* Next Action
* Attention
* Pending Approvals
* Active Servers
* Active Devices
* Active Capabilities
* Autonomous Loop状態
* User Situation
* Commitments
* LLM Budget
* Recent Failures
* Security状態
* Backup状態
* Latest deployment
* Connection freshness

### 操作

* 新しいTaskを作成
* AEGISへ指示
* Autonomous Loop一時停止
* 全Task一時停止
* Emergency Stop
* Privacy Mode
* Maintenance Mode
* DisplayへPresentation送信
* 全Server再確認

## 3.2 Attention Center

AEGIS内で人間の確認が必要なものを統合する。

* Approvals
* Failed Tasks
* Blocked Tasks
* Missing Permissions
* Offline Servers
* Disconnected Devices
* Budget Warnings
* Security Alerts
* Expiring Commitments
* Stale Data
* Failed Backups
* Verification failures
* User confirmation requests

単なる通知一覧ではなく、原因・影響・推奨操作を表示する。

---

# 4. Work

## 4.1 Tasks

### 一覧分類

* Running
* Planning
* Waiting
* Waiting for Approval
* Blocked
* Scheduled
* Paused
* Completed
* Failed
* Cancelled
* Archived

### Task詳細

* Original Instruction
* Parsed Goal
* Task type
* Priority
* Status
* Owner
* Created source
* Conversation
* Plan
* Step graph
* Dependencies
* Capability executions
* Approval history
* Memory used
* Context breakdown
* Current and next action
* Verification
* Retry history
* Repair attempts
* Cost
* Duration
* Final output
* Related audit entries
* Related events

### 操作

* Pause
* Resume
* Cancel
* Retry
* Retry selected step
* Skip step
* Re-plan
* Change priority
* Add note
* Request user confirmation
* Clone Task
* Archive

危険な操作にはApprovalとFresh Authを要求する。

## 4.2 Plans

Taskから独立してPlanを表示する。

* Plan version
* Generated by
* Goal
* Assumptions
* Steps
* Dependency graph
* Required capabilities
* Expected cost
* Expected duration
* Risk
* Approval points
* Verification strategy
* Revision history

古いPlanと新しいPlanを差分表示できるようにする。

## 4.3 Commitments

* Active
* Due soon
* Overdue
* Completed
* Cancelled
* Recurring

表示項目：

* 約束内容
* 相手
* 期限
* 根拠となる会話
* 関連Task
* 通知予定
* 実行状態
* 信頼度

## 4.4 Schedule & Hooks

* Scheduled Tasks
* Recurring Tasks
* Event Hooks
* Conditional Triggers
* Daily Briefing
* Maintenance jobs
* Memory consolidation
* Backup schedule
* Notification schedule

各Triggerについて、

```text
Trigger
Condition
Action
Cooldown
Last fired
Next evaluation
Result
Enabled
```

を管理する。

## 4.5 Delegation

* Delegation policies
* Agent assignments
* Server selection
* Capability selection rules
* Escalation policy
* Human intervention threshold
* Time／cost limits

---

# 5. Intelligence

## 5.1 Autonomy

Autonomous Loop全体を管理する。

### 表示

* Enabled／Paused
* Last evaluation
* Next likely evaluation
* Last autonomous action
* Suppression reason
* Budget suppression
* User activity suppression
* Recent decisions
* Success rate
* Duplicate action prevention
* Average execution interval

### Desire管理

* user_helpfulness
* learning_progress
* curiosity
* social_connection
* autonomy
* creativity
* purpose

各Desireについて、

* Current value
* Growth rate
* Threshold
* Last satisfied
* Satisfaction history
* Triggered actions
* Suppression reason
* Related settings

を表示する。

## 5.2 Memory

統計表示だけでなく、実際のMemoryを管理する。

### 分類

* Episodic
* Semantic
* Procedural
* User preferences
* People
* Skills
* Lessons
* Workflows
* Conversation summaries
* Task results

### Memory詳細

* Content
* Summary
* Type
* Source
* Created at
* Last accessed
* Access count
* Confidence
* Importance
* Embedding status
* Relationships
* Related Task
* Related Person
* Related Capability
* Consolidation history
* Provenance
* Expiration／forgetting policy

### 操作

* Search
* Filter
* Edit
* Merge
* Split
* Pin
* Archive
* Forget
* Re-embed
* Change importance
* Link to Task
* Link to Person
* Export

## 5.3 Memory Consolidation & Sleep

* Last sleep
* Current phase
* Candidate memories
* Duplicate candidates
* Merge candidates
* Contradictions
* Forgotten items
* Consolidated lessons
* Failed consolidation
* Next scheduled run

Sleep処理を手動実行し、実行前後の差分を確認できるようにする。

## 5.4 User Model

* Known preferences
* Communication preferences
* Routines
* Locations
* Devices
* Relationships
* Skills
* Current projects
* Commitments
* Confidence
* Information source
* Last updated
* Conflicting observations

各推定を、事実・推定・一時状態に分類する。

## 5.5 User Situation

現在状態を時間軸付きで表示する。

* Estimated location
* Current device
* Active application
* Activity
* Attention state
* Availability
* Room state
* Phone connectivity
* PC activity
* Confidence
* Evidence
* Last observation

## 5.6 Context Builder

LLMへ何が渡されたかを管理する。

* System Prompt
* Conversation history
* Memories
* Events
* User state
* Tool schemas
* Capability descriptions
* Token allocation
* Truncated sections
* Retrieval reasons
* Context cache

TaskやLLM Request単位で再現できるようにする。

## 5.7 Models & Prompts

* Model registry
* Routing rules
* Fallbacks
* Vision models
* Reasoning levels
* Temperature
* Token limits
* Prompt registry
* Prompt usage
* Dead prompts
* Duplicate prompts
* Prompt versions
* Evaluation results

Prompt変更は差分確認、テスト、Rollbackを必須にする。

---

# 6. Capabilities

## 6.1 Capability Catalog

全Capabilityを管理する。

### 分類

* Builtin
* Generated
* Disabled
* Deprecated
* Unavailable
* Approval required
* High risk
* Failing
* Unused

### Capability詳細

* ID
* Name
* Description
* Server
* Executor
* Input schema
* Output schema
* Risk
* Approval policy
* Permissions
* Preconditions
* Completion conditions
* Verification
* Postconditions
* Timeout
* Retry policy
* Version
* Source file
* Last execution
* Success rate
* Average latency
* Average cost
* Related Tasks
* Related Errors

### 操作

* Enable／Disable
* Execute test
* Edit risk override
* Edit approval requirement
* Edit timeout
* Edit verification
* Deprecate
* Duplicate
* Export
* Open source
* Regenerate vector index

## 6.2 Generated Capabilities

Generated配下を独立管理する。

* Generation reason
* Generated by Task
* Source files
* Test status
* Security review
* Capability review
* Last modified
* Usage count
* Promotion status

状態：

```text
Draft
Testing
Awaiting Review
Approved
Production
Deprecated
Rejected
```

## 6.3 Capability Executions

Capability実行を横断検索する。

* Capability
* Task
* Server
* Arguments
* Result
* Verification
* Approval
* Duration
* Retry
* Error
* Timestamp

## 6.4 Policy Simulation

Capabilityを実際に実行せず、

```text
このユーザー
この引数
このTarget
この環境
```

でPolicy結果をシミュレーションする。

表示：

* Allowed
* Approval required
* Blocked
* Fresh auth required
* Reason
* Effective risk
* Matching rule

---

# 7. Infrastructure

## 7.1 Servers

対象：

* AI Server
* PC Server
* Android Server
* Browser Server
* Room Server
* Dev Server

### Server詳細

* Status
* Required／Optional
* Host
* Version
* Build
* Uptime
* Last seen
* Health checks
* Dependencies
* Capabilities
* Active Tasks
* Connection mode
* Latency
* Error rate
* Resource usage
* Logs
* Configuration
* Permissions
* Recovery history

### 操作

* Health check
* Connect
* Disconnect
* Restart
* Stop
* Enter maintenance
* Test capability
* Open logs
* Run diagnostics
* Deploy update

## 7.2 Devices

* Windows PC
* Android phones
* Display kiosk
* Room devices
* Orange Pi
* Future wearable devices

表示：

* Device identity
* Model
* OS
* App version
* Network
* Battery
* Screen state
* Last seen
* Permissions
* Capabilities
* Connection history
* Assigned role

## 7.3 Network

* LAN
* Tailscale
* Cloudflare Tunnel
* gRPC
* SSE
* WebSocket
* HTTP
* Device heartbeat

Topology上で接続状態と通信方向を表示する。

## 7.4 Deployment

* Current version
* Git commit
* Docker image
* Deployment target
* Last deployment
* Rollback point
* Migration state
* Config drift
* Service state
* Restart persistence

## 7.5 Storage

* Database
* ChromaDB
* Audit storage
* Memory storage
* Logs
* Reports
* Backups
* Cache
* Disk usage
* Retention

---

# 8. Communications

## 8.1 Conversations

* Dashboard Chat
* AGORA
* Discord
* LINE
* Email
* Voice
* Room conversations

各会話について、

* Participants
* Messages
* Drafts
* Sent messages
* Approvals
* Related Tasks
* Related Memories
* Delivery state

を表示する。

## 8.2 Notifications

* Unread
* Delivered
* Failed
* Suppressed
* Expired
* Acknowledged

Channel別：

* Web
* Android
* PC Overlay
* Room
* OS notification
* Dedicated Display

## 8.3 Presentation Surfaces

* Dedicated display
* Web Dashboard
* Android
* PC Overlay
* Room Display
* Developer Console

各Surfaceについて、

* Connection
* Current Scene
* Queue
* Supported priorities
* Privacy level
* Active presentation
* Last acknowledgment
* Rendering capability
* Reduced-motion state

を管理する。

---

# 9. Governance

## 9.1 Approvals

Pendingだけでなく、全ライフサイクルを管理する。

* Pending
* Approved
* Rejected
* Expired
* Cancelled
* Failed
* Superseded

詳細：

* Requested action
* Arguments
* Target
* Risk
* Policy reason
* Side effects
* Requesting Task
* Requested by
* Presented surfaces
* User response
* Fresh auth
* Execution after approval
* Final verification

## 9.2 Policy

* Global rules
* Capability rules
* Server rules
* Data access rules
* Privacy rules
* Approval rules
* Budget rules
* Time rules
* User-presence rules

Rule priority、適用範囲、理由、変更履歴を表示する。

## 9.3 Security

* Passkeys
* Sessions
* CSRF
* Authentication attempts
* Fresh-auth state
* Secrets
* Token health
* Network exposure
* Security events
* Secret scanning
* Permission changes
* Risk override changes

## 9.4 Privacy

* Display privacy
* Data collection
* Clipboard
* Camera
* Microphone
* Location
* Notifications
* User-state inference
* Retention
* Redaction
* Surface visibility

## 9.5 Audit

すべての変更と操作を検索できるようにする。

* Who
* What
* When
* Why
* Before
* After
* Related Task
* Related Approval
* Related Event
* Result
* Source device

---

# 10. Observability

## 10.1 Activity

Event、Audit、Task、Capability、LLM、Setting、Securityを一つの時間軸へ統合する。

Filter：

* Time
* Type
* Severity
* Task
* Server
* Capability
* Device
* User action
* Autonomous action
* Failure
* Cost

## 10.2 LLM Usage

* Requests
* Models
* Input tokens
* Output tokens
* Cache hit
* Cache miss
* Context size
* Memory tokens
* Tool schema tokens
* Cost
* Latency
* Retry loops
* Failure rate
* Autonomous usage
* Chat usage
* Vision usage

Request単位でContext内訳を開けるようにする。

## 10.3 Errors

* Active
* Recovered
* Repeated
* Suppressed
* Fatal
* Verification failure
* Connection failure
* LLM failure
* Capability failure

Error fingerprintで同種エラーをまとめる。

## 10.4 Performance

* API latency
* Manager latency
* Capability latency
* Event lag
* SSE reconnects
* gRPC reconnects
* CPU
* RAM
* GPU
* Disk
* Queue length
* Task throughput

## 10.5 Reports

* Production readiness
* UI completeness
* Capability coverage
* Mock／stub audit
* E2E results
* Soak test
* Security report
* Backup report
* Device test report
* Daily operation report

---

# 11. Configuration

設定を一枚の汎用フォームへ並べず、専用画面へ分ける。

```text
Autonomy
Models
Prompts
Memory
Context
Capabilities
Permissions
Approvals
Servers
Devices
Notifications
Privacy
Display
Budgets
Retention
Developer
Backup
```

各設定画面に必須の機能：

* Current effective value
* Source
* Default
* Description
* Validation
* Pending changes
* Before／After diff
* Save
* Cancel
* Rollback
* Change history
* Restart required表示

入力中に即保存しない。

---

# 12. Developer Mode

通常利用者向け情報と分離する。

Developer Modeでのみ表示するもの：

* Raw JSON
* Internal IDs
* Prompt contents
* Tool arguments
* Stack traces
* Manager internals
* Event payloads
* Feature flags
* Mock／stub inventory
* Database inspector
* ChromaDB inspector
* API explorer
* SSE inspector
* gRPC inspector
* Test runner
* Readiness runner
* Docker state
* Generated source
* Migration tools

---

# 13. 共通画面構造

## 左側

階層ナビゲーション。

```text
Work
 ├─ Tasks
 ├─ Plans
 ├─ Commitments
 ├─ Schedule
 └─ Delegation
```

## 上部

* Global Search
* Command Palette
* Create Task
* Attention count
* Approval count
* Health
* User menu

## 中央

選択中ページの一覧または可視化。

## 右側

Global Inspector。

選択したTask、Capability、Server、Memory、Eventなどの詳細を表示する。

## 下部

折りたたみ可能なLive Activity Drawer。

現在発生したEvent、Capability実行、Approval、Errorを表示する。

---

# 14. Global Search

Dashboard全体を横断検索できるようにする。

対象：

* Task
* Memory
* Capability
* Server
* Device
* Approval
* Event
* Audit
* Person
* Commitment
* Setting
* Notification
* Conversation

検索結果から該当ページとDetailへ直接移動する。

---

# 15. Command Palette

`Ctrl+K`で開く。

例：

```text
Create new task
Pause autonomy
Open Browser Server
Show failed capabilities
Search memory
Review pending approvals
Enable privacy mode
Run readiness test
Restart Android connection
Export settings
```

危険操作はPaletteから即実行せず、Preview画面へ移動する。

---

# 16. バックエンド構造

`ui-overview`へすべてを詰め込まない。

`ui-overview`はCommand Center用の軽量Summaryとして残す。

詳細管理用にResource APIを追加する。

```text
GET    /api/tasks
GET    /api/tasks/{id}
POST   /api/tasks/{id}/actions

GET    /api/capabilities
GET    /api/capabilities/{id}
PATCH  /api/capabilities/{id}

GET    /api/memories
GET    /api/memories/{id}
PATCH  /api/memories/{id}

GET    /api/servers
GET    /api/servers/{id}
POST   /api/servers/{id}/actions

GET    /api/events
GET    /api/audit
GET    /api/llm/requests
GET    /api/approvals
GET    /api/commitments
```

全一覧APIへ次を実装する。

* Pagination
* Filtering
* Sorting
* Search
* Time range
* Cursor
* Stable ID
* Related-resource links

---

# 17. 共通Entity Contract

各Managerから取得するオブジェクトを、共通形式で扱う。

```text
EntitySummary
├─ id
├─ type
├─ title
├─ subtitle
├─ status
├─ severity
├─ created_at
├─ updated_at
├─ owner
├─ tags
├─ relations
├─ available_actions
└─ permissions
```

これによりGlobal Search、Inspector、Activity、Relation表示を共通実装できる。

---

# 18. 操作の安全設計

操作を4段階に分類する。

| レベル        | 例          | UI                  |
| ---------- | ---------- | ------------------- |
| View       | 閲覧、検索      | 即時                  |
| Safe       | Pause、再取得  | 通常ボタン               |
| Controlled | 設定変更、Retry | Preview＋確認          |
| Dangerous  | 削除、送信、PC操作 | Approval＋Fresh Auth |

操作前には必ず表示する。

* 対象
* 変更内容
* 影響
* Risk
* Rollback可能性
* Verification方法

---

# 19. 情報量を増やしても見づらくしない方法

## Progressive Disclosure

最初はSummaryだけを表示し、クリックで詳細を展開する。

## Saved Views

例：

* Daily Operations
* Development
* Device Maintenance
* LLM Cost
* Security
* Autonomous Activity

## Pins

よく見るTask、Server、Capability、MemoryをCommand Centerへ固定する。

## Density

* Comfortable
* Standard
* Compact

の3段階を選択可能にする。

## 色の使い方

色は情報領域を示す。

* Work：Blue
* Intelligence：Violet
* Capability：Cyan
* Infrastructure：Teal
* Communications：Rose
* Governance：Amber
* Critical：Red
* Recovery：Green

状態は色だけに依存せず、アイコン、形、線種、ラベルを併用する。

---

# 20. 実装優先順位

## Phase 1：管理基盤

* 新ナビゲーション
* Global Search
* Global Inspector
* Command Palette
* Entity Contract
* Resource API基盤

## Phase 2：中核管理

* Tasks
* Approvals
* Servers
* Devices
* Capabilities
* Settings
* Activity

## Phase 3：AI内部

* Autonomy
* Desires
* Memory
* User Model
* Context Builder
* Models
* Prompts

## Phase 4：運用

* Commitments
* Schedule
* Hooks
* Notifications
* Communications
* Presentation Surfaces

## Phase 5：高度管理

* Deployment
* Storage
* Network
* Backup
* Security
* Policy Simulation
* Reports
* Developer Mode

---

# 21. 完了条件

* すべてのRuntime Managerに対応する管理画面がある
* すべてのServerとDeviceにDetail画面がある
* すべてのCapabilityを検索・確認・設定できる
* Taskの作成から完了、検証、監査まで追跡できる
* Pending以外のApproval履歴を確認できる
* Memory本文を検索・編集・関連付けできる
* Autonomous behaviorとDesireを確認・設定できる
* LLM RequestごとのContextとCostを確認できる
* 全設定を専用Editorで安全に変更できる
* 全変更にAuditが残る
* Dashboard内の全オブジェクトを横断検索できる
* 関連Task、Memory、Capability、Event間を移動できる
* 概要データと詳細データを分離する
* 大量データでもPaginationとFilterが機能する
* Dangerous actionはApprovalとFresh Authを通る
* 通常利用者向け画面にRaw JSONを露出しない
* Developer Modeでは内部データまで調査できる
