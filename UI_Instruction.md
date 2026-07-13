# AEGIS UI全面刷新計画

## 1. 基本方針

今回の刷新では、旧UIのレイアウト・CSS・画面構成・ナビゲーションを継承しない。

ただし、以下のバックエンド資産は維持する。

* PolicyEngineと安全レベル
* ApprovalManagerと承認ライフサイクル
* TaskManager、StatusManager、NotificationManagerなどのManager群
* Web・Android間で共有されるチャット履歴
* Manager API
* ストリーミングチャット
* グループ化された監査ログ
* サーバー間通信とCapability実行

AEGISには既に、タスク、イベント、監査、状態、通知、記憶、睡眠、ユーザー状態、委任、状況認識などのAPIが存在するため、内部ロジックまで作り直す必要はない。

現在のダッシュボードはFlaskベースで、一部が`dashboard_legacy`に委譲された互換構造になっている。新UIはこの構造へ追加実装するのではなく、独立したフロントエンドとして構築し、最終的に旧テンプレートと旧表示ルートを削除する。

---

## 2. 3つのUIの役割

| UI         | 主な役割              | 操作密度 |     表示情報量 |
| ---------- | ----------------- | ---: | --------: |
| Webダッシュボード | 管理、分析、設定、詳細調査     |   高い |        最大 |
| Androidアプリ | 会話、承認、緊急確認、外出中の操作 |  中程度 |  必要なものに限定 |
| AI専用ディスプレイ | AIの現在状態と注意事項を常時表示 | 原則なし | 一目で把握できる量 |

3つのUIで情報構造を共有するが、画面構成は共有しない。

共通の情報軸は次の4つとする。

1. **Now：今、何をしているか**
2. **Attention：ユーザーの対応が必要か**
3. **Next：次に何をするか**
4. **History：何が起きたか**

ダッシュボードは大量の情報を単に並べるのではなく、重要度に基づいて階層化する。監視UIでは認知負荷を減らし、重要な異常が集約情報に埋もれない構造が重要とされている。

---

## 3. デザインコンセプト

### コンセプト名

**AEGIS Operational Futurism**

映画的な派手さではなく、「実際に稼働している高度なAIシステム」に見える近未来感を目指す。

### 避けるもの

* 画面全体への強いネオン発光
* すべてのカードへのGlassmorphism
* 装飾目的だけの円グラフや波形
* 読めないほど細いフォント
* 状態を色だけで伝える設計
* 常時動き続ける背景アニメーション
* 意味のない巨大なAI球体
* どの情報も同じ強さで表示する画面

### 推奨ビジュアル

* ほぼ黒に近い青系背景
* 面ごとに明度差を付けたレイヤー
* 細い境界線と限定的な発光
* Cyanを主要アクセント、VioletをAI内部状態に限定
* Amberを承認待ち、Redを重大障害に限定
* 数値は等幅またはtabular numerals
* 角丸は12～16px程度
* 背景グリッドや回路線は極めて薄く表示

### カラートークン案

| 用途                 | 色         |
| ------------------ | --------- |
| Background         | `#05090F` |
| Surface            | `#0B111B` |
| Elevated Surface   | `#111A27` |
| Border             | `#1E2A3A` |
| Primary Text       | `#EAF2FF` |
| Secondary Text     | `#8EA0B8` |
| AEGIS Cyan         | `#29D3FF` |
| Cognitive Violet   | `#8B7CFF` |
| Success            | `#2DD4A8` |
| Warning / Approval | `#FFB84D` |
| Critical           | `#FF5D73` |

グラフでは隣接色の識別性を優先し、警告色と通常のカテゴリ色を分離する。Carbonのデータ可視化設計でも、カテゴリ間の識別性と専用のアラートパレットが区別されている。

実装前に、通常文字4.5:1以上、大きな文字3:1以上を基準として全トークンを機械検査する。

### モーション

* ボタン、パネル切替：120～240ms
* 通知出現：200～300ms
* AI待機時の呼吸表現：6～12秒周期
* 承認待ち：ゆっくりしたAmber境界線
* Critical：最大でも約1秒周期の控えめなパルス
* `prefers-reduced-motion`とAndroidのアニメーション設定に対応
* 状態変化以外では画面を動かさない

---

## 4. 共通デザインシステム

WebとAndroidで見た目を似せるだけでなく、意味と状態を共有する。

### 共通トークン

* Color
* Typography
* Spacing
* Radius
* Elevation
* Motion duration
* Severity
* Risk level
* Server state
* Task state
* Data freshness

`design-tokens/tokens.json`を単一の定義元とし、以下を生成する。

* Web用CSS Variables
* Android Compose用`AegisTheme`
* StorybookとCompose Preview用サンプル
* コントラスト検査用データ

### 共通コンポーネント

#### System Status

必ず以下を併記する。

* 状態アイコン
* `ONLINE`、`DEGRADED`などの文字
* 最終更新時刻
* 短い説明
* 必要なら復旧方法

#### Data Freshness

全リアルタイムカードに次を持たせる。

* `LIVE`
* `12秒前`
* `STALE`
* `OFFLINE SNAPSHOT`

通信切断後も古い値を正常値として表示し続けない。

#### Task Progress

* タスク名
* 状態
* 現在の段階
* 使用中Capability
* 実行サーバー
* 開始時刻
* 最近の結果
* 次の処理
* 停止理由
* ユーザー待ちの有無

#### Approval Card

WebとAndroidでは次を表示する。

* AIが実行しようとしている行動
* 対象アプリ、Webサイト、ファイル、デバイス
* Capability ID
* リスクレベル
* 予想される副作用
* AIが必要だと判断した理由
* 送信内容、変更差分、操作対象のプレビュー
* 要求元タスク
* 発行時刻と期限
* 承認、拒否
* 詳細表示

高リスク操作では一括承認を禁止する。

設定UIはPolicyEngineを弱められず、制約を追加することしかできない現在の原則を維持する。

#### Empty、Loading、Error状態

すべての画面で次を個別に設計する。

* Loading
* Empty
* Permission missing
* Degraded
* Disconnected
* Stale
* Partial data
* Fatal error
* Unauthorized

「何も表示されない状態」を許容しない。

システム状態の可視化、ユーザー制御、エラー予防、専門用語ではなく理解可能な説明、問題の解決方法の提示を全画面の基本原則とする。

---

# 5. Webダッシュボード

## 5.1 役割

Web版はAEGISの**司令室兼デバッグ・管理画面**とする。

スマホと異なり、以下を省略しない。

* 詳細な監査情報
* サーバー依存関係
* Capability統計
* 記憶の検索と根拠
* 自律実行履歴
* LLM使用量
* 設定変更履歴
* エラーのスタックトレース
* タスクと承認の関連性

## 5.2 グローバルナビゲーション

旧画面の項目別ページを整理し、次の7領域に再編する。

1. **Command Center**
2. **Work**
3. **Approvals**
4. **Systems**
5. **Mind & Memory**
6. **Activity**
7. **Settings**

チャットは独立ページだけにせず、全ページから開ける右側ドロワーとして提供する。

## 5.3 Command Center

### 画面上部

* AEGISロゴ
* Core状態
* 自律モード
* Autonomy profile
* 接続品質
* 未処理承認数
* Critical通知数
* 現在時刻
* データ更新状態

### 12カラム構成

#### 最上段：Attention Strip

重大度順に表示する。

1. Critical security/room alert
2. Approval required
3. Server disconnected
4. Permission missing
5. Budget warning
6. 通常通知

AEGISには既にこれらの通知種別と重大度が定義されているため、新UIでは個別カードではなく統一されたAttentionモデルに正規化する。

#### 左8カラム：Current Operation

* 現在のメインタスク
* 進行フェーズ
* 実行中Capability
* 直前の結果
* 次の処理
* 子タスク
* 停止、再試行、承認待ち状態
* 関連する会話へのリンク

#### 右4カラム：AI State

* `IDLE / OBSERVING / PLANNING / EXECUTING / WAITING / BLOCKED`
* 現在の最優先目標
* 判断の信頼度
* 最も強い欲求
* 注意対象
* 最終自律サイクル
* 次回評価予定

感情や欲求を派手なメーターとして並べず、現在の判断に影響している上位要素だけを表示する。

#### 中段

* Server Health
* User Situation
* Device Context
* Pending Commitments
* Recent Notifications
* LLM Usage

#### 下段

「直近の出来事」を時系列で統合する。

* ユーザーメッセージ
* 計画生成
* Capability選択
* 承認要求
* Capability実行
* 結果確認
* 通知
* エラー
* タスク完了

既存のグループ監査を標準表示とし、Raw Auditは展開後のデバッグ情報に下げる。現行AEGISもチャット、タスク、自律サイクル、承認を単位として監査ログをグループ化している。

## 5.4 Work

タスクを以下のビューで表示する。

* Active
* Waiting for user
* Scheduled
* Research
* Self-development
* Commitments
* Delegated
* Completed
* Failed

デスクトップでは左に一覧、右に詳細を表示するList–Detail構成にする。

タスク詳細には以下を含める。

* 目的
* 元のユーザー指示
* AIの計画
* 子タスク依存関係
* Capability実行履歴
* 承認
* 使用記憶
* 使用モデルとコスト
* 完了条件
* 検証結果
* 最終出力

## 5.5 Approvals

承認は通知一覧の一項目ではなく、独立した主要画面とする。

### 左ペイン

* Pending
* Expiring soon
* High risk
* Resolved
* Expired

### 中央ペイン

承認の完全な説明とプレビュー。

### 右ペイン

* 関連タスク
* 直前の操作
* リスク判定根拠
* 過去の同種操作
* 監査情報
* 承認後に行われる処理

外部送信、投稿、購入などは操作対象を明示し、承認後の動作が曖昧な要求を許可しない。

## 5.6 Systems

AI、PC、Android、Browser、Room、Devを共通形式で表示する。

各サーバーカードには次を持たせる。

* Online / Degraded / Offline / Disabled
* Heartbeat age
* Version
* Connection mode
* Capability数
* エラー
* 依存サービス
* 復旧方法
* 最終正常時刻

Androidについては追加で以下を表示する。

* 端末名
* 接続方式
* Permission状態
* 利用可能Capability
* Active approval
* 最終観測時刻

現在のStatusモデルにもAndroidの権限、Capability、Active Approvalなどが含まれている。

## 5.7 Mind & Memory

タブを次のように分ける。

* Current Mind
* Goals
* Desires
* Memories
* People
* Skills
* Sleep / Consolidation

Memory画面では、記憶本文だけでなく次を表示する。

* 種類
* 情報源
* 作成時刻
* 最終使用時刻
* 信頼度
* 関連人物・タスク
* 他の記憶との関係
* 検索された理由
* 編集・無効化履歴

## 5.8 Activity

* Operations Timeline
* Audit Groups
* Raw Audit
* Events
* Errors
* Notifications
* LLM Usage
* Hooks

通常運用画面と開発者向け情報を同じ深さに置かず、Raw JSONやスタックトレースは明示的に展開した場合だけ表示する。

## 5.9 Settings

設定を以下に分類する。

* Autonomy
* Safety and permissions
* Servers
* Privacy
* Notifications
* Models and budgets
* Memory
* Display and kiosk
* Developer
* Backup and data

設定変更時には以下を表示する。

* 変更前
* 変更後
* 影響範囲
* 再起動の要否
* 安全性への影響
* 永続化されたか
* 変更者
* 変更時刻

Docker再起動後も設定が戻らないことをE2Eテストに含める。

## 5.10 Webのレスポンシブ方針

| 幅           | 構成                            |
| ----------- | ----------------------------- |
| 1440px以上    | ナビゲーション＋2～3ペイン                |
| 1024～1439px | 縮小Rail＋2ペイン                   |
| 768～1023px  | Drawer＋1～2ペイン                 |
| 767px以下     | 1ペイン。管理機能は使用可能だがAndroidアプリを優先 |

---

# 6. Androidアプリ

## 6.1 現状からの変更

現在のComposeアプリは`State / Home / Action`タブを持ち、Homeには最小限の状態、権限警告、共有チャットが表示される。これを全面的に置き換える。

新しい下部ナビゲーションは次の5項目とする。

1. Home
2. Chat
3. Approvals
4. Tasks
5. More

## 6.2 Home

上から次の順に表示する。

### Status Hero

文章で状況を要約する。

例：

> AEGISはオンラインです。PC上で調査タスクを実行しています。承認が1件あります。

単なる状態ドットではなく、現在の最重要情報を一文で伝える。

### Attention Stack

* 承認待ち
* 権限不足
* 切断
* 重大通知

### Current Task

* タスク名
* 現在段階
* 進捗
* 承認待ちか
* 詳細を開く

### Quick Commands

固定ボタンではなく、状況に応じた候補を最大4件表示する。

### Recent Activity

直近3～5件のみ表示する。

## 6.3 Chat

* ストリーミング応答
* Tool execution card
* Approval card
* Screenshot/image result
* Task progress
* Error and retry
* 会話とタスクの関連表示

既存のWebとAndroidの共有チャット履歴を維持する。

## 6.4 Approvals

モバイル承認は最重要画面とする。

通常操作：

1. カードを開く
2. 内容と影響を確認
3. 承認または拒否
4. 高リスクの場合は確認シート
5. 実行状態へ遷移
6. 結果を同じカード内に表示

高リスク操作では誤タップ防止のため、単一タップで即時実行しない。

承認ボタンの近くに拒否ボタンを置くが、色だけで区別しない。

Android側ではtap、swipe、type_textなどが既に承認対象になっており、パスワード欄や機密アプリに対する追加防御も存在する。

## 6.5 Tasks

* Active
* Waiting
* Scheduled
* Completed

詳細画面ではユーザーに理解できる表現を優先し、Capability IDやRaw EventはDeveloper sectionに格納する。

## 6.6 More

* Devices
* Permissions
* Connectivity
* Notification settings
* Autonomy
* Privacy
* Models and budget
* Debug
* Pairing

不足権限は単なる赤文字ではなく、「何が使えないか」「どの設定画面を開くか」を示す。Android側は権限不足をUrgent Eventとして送信できるため、このイベントを直接Permission Cardへ変換する。

## 6.7 Androidの適応レイアウト

* スマートフォン：Bottom navigation
* 横画面・折りたたみ・タブレット：Navigation rail
* 大画面：一覧と詳細の同時表示
* Approvals、Tasks、DevicesはList–Detail
* Chatは大画面で会話とタスクContextを並列表示

Android公式のAdaptive UIでも、Window Size Classに応じたNavigation bar／railの切替とList–Detail構成が推奨されている。

背景はEdge-to-Edgeで描画するが、ボタンや重要文字はSystem barのInset内に収める。

タップ領域は最低48dp、隣接操作間は原則8dp以上とする。

---

# 7. AI専用ディスプレイ

## 7.1 目的

ノートパソコンのディスプレイ全体を使い、AEGISの存在、活動、問題、承認待ちを常時表示する。

これはダッシュボードを全画面表示したものではなく、**入力を前提としない専用画面**とする。

ルート例：

`/display`

または独立バンドル：

`display-ui/`

## 7.2 入力に関する原則

* キーボード入力を要求しない
* マウス操作を要求しない
* テキスト入力欄を置かない
* ナビゲーションメニューを置かない
* 承認、拒否ボタンを置かない
* スクロールを要求しない
* カーソルは非表示
* 表示内容は自動で状態に追従
* 詳細はページ切替ではなく、重要度に応じたレイアウト変化で表示

承認要求は表示するが、次の案内を出す。

> スマートフォンまたはWebダッシュボードで確認してください

## 7.3 基準解像度

* 基準：1920×1080
* 対応：1366×768
* 対応：2560×1440
* 16:9を主対象
* `100vw × 100vh`
* ブラウザUI、タスクバー、タイトルバーを非表示

## 7.4 通常レイアウト

### Header：画面高の約7%

* AEGIS
* Core状態
* 自律モード
* 接続状態
* 現在時刻
* 最終同期

### Main：画面高の約70%

#### 左24%：AI Core

* 抽象的なCore Signature
* 現在モード
* 最優先目標
* 判断信頼度
* 現在注目している対象
* 選択中のデバイス／サーバー

Core Signatureは雰囲気を作る補助表現とし、状態は必ず文字でも表示する。

#### 中央52%：Current Operation

最も大きく表示する。

* 現在のタスク
* 現在フェーズ
* 実行中の行動
* 直前の結果
* 次の処理
* 子タスク
* 待機理由
* 実測可能な場合のみ残り時間

推測だけのETAは表示しない。

#### 右24%：Attention

最大3件まで表示する。

* Approval
* Critical alert
* Permission missing
* Disconnected server
* Failed task

4件以上は「ほか5件」のように集約する。

### Footer：画面高の約23%

* 6サーバーの状態
* 次の予定
* 最新の通知
* Room状態
* LLM予算状態

横に流れ続けるマークィーは使用せず、数秒ごとのフェード切替とする。

## 7.5 表示モード

### IDLE

* 次の予定
* 最近完了したタスク
* Memory consolidation
* システム状態
* 穏やかな低速アニメーション

### OBSERVING

* 観測中のデバイス
* 最終観測
* 更新頻度
* 現在の状況推定

### PLANNING

* 目的
* 計画段階
* 検討中の候補数
* 使用しているContext

内部Chain of Thoughtは表示せず、要約された計画状態だけを表示する。

### EXECUTING

Current Operationを最大化する。

* 使用Capability
* 対象
* サーバー
* 進捗
* 実行結果

### WAITING FOR APPROVAL

画面中央に大きなAmberパネルを表示する。

* 承認が必要な操作
* 対象
* リスク
* 理由
* 要求時刻
* 有効期限
* 関連タスク
* 「スマートフォンまたはWebで確認」

背景の通常情報は暗くするが、サーバー状態は残す。

### CRITICAL

* 上部にRedのCritical strip
* 問題内容
* 影響対象
* 発生時刻
* 自動復旧状態
* ユーザーが行うべき対応

### OFFLINE / DEGRADED

* `LIVE`を消す
* 最後に接続していた時刻
* 最後のSnapshotであること
* 再接続試行状態
* 影響を受けている機能

### PRIVACY

ユーザー不在、画面ロック、来客などの条件で以下だけを表示する。

* AEGIS状態
* サーバー状態
* 一般化されたタスク種別
* 承認件数

メッセージ本文、通知本文、スクリーンショット、個人名は隠す。

## 7.6 キオスクのセキュリティ

AIディスプレイには専用の権限を使用する。

`display:read`

許可するもの：

* UI用Snapshot取得
* UI Event Stream購読
* 承認状態の閲覧
* 通知の閲覧
* Server状態の閲覧

禁止するもの：

* POSTによる操作
* 承認、拒否
* 設定変更
* Capability実行
* チャット送信
* Raw secretの取得

Windows上ではAssigned AccessやEdgeの全画面キオスクを利用でき、単一アプリを全画面で実行し、終了時の再起動を含む専用端末化が可能である。

## 7.7 自動復旧

* 10秒間隔のHeartbeat
* Stream切断時は指数バックオフ
* 切断中は最後のSnapshotへ移行
* 一定回数失敗後にページ再読み込み
* ブラウザクラッシュ時に自動再起動
* 毎日、活動の少ない時間に安全な再読み込み
* 長時間稼働でメモリ使用量が増加し続けないか監視

---

# 8. UI向けAPI構成

既存APIを画面から大量に並列取得すると、読み込み順と状態の整合性が複雑になる。

UI専用集約層を追加する。

## 8.1 Overview API

`GET /api/ui/overview`

返却内容：

```text
core
attention
current_task
servers
user_state
mind_summary
notifications
approvals
commitments
usage
freshness
```

各項目に必ず含める。

* `generated_at`
* `source_updated_at`
* `status`
* `stale`
* `error`

## 8.2 UI Event Stream

`GET /api/ui/stream`

SSEイベントを正規化する。

* `status.changed`
* `task.created`
* `task.updated`
* `task.completed`
* `approval.created`
* `approval.resolved`
* `approval.expired`
* `notification.created`
* `mind.changed`
* `chat.updated`
* `permission.changed`
* `connection.changed`

既存のチャットSSEは残し、全UI状態用Streamとは分離する。現在のチャットには既にSSEストリーミングが存在する。

## 8.3 Approval Schema

Web、Android、ディスプレイで同じApproval IDと内容を表示する。

```text
approval_id
status
risk_level
capability_id
title
summary
reason
target
side_effects
preview
requested_at
expires_at
task_id
audit_group_id
allowed_responses
```

承認後に同じ操作が二重実行されないことをバックエンド側で保証する。

## 8.4 UIからJSONLを直接読まない

新UIは以下を直接参照しない。

* `audit.jsonl`
* `chat_history.jsonl`
* 設定ファイル
* Memory内部ファイル

すべてManagerまたはAPIを経由する。

---

# 9. 推奨コード構成

## Web

```text
web-ui/
  src/
    app/
    pages/
      command-center/
      work/
      approvals/
      systems/
      mind-memory/
      activity/
      settings/
    features/
    components/
    design-system/
    api/
    state/
    streams/
    types/
    test/
```

推奨技術：

* React
* TypeScript
* Vite
* TanStack Query
* SSE
* Storybook
* Playwright
* Vitest

## Android

```text
android-server/
  app/
  core/
    designsystem/
    model/
    network/
    grpc/
    datastore/
  feature/
    home/
    chat/
    approvals/
    tasks/
    devices/
    permissions/
    settings/
```

* Jetpack Compose
* Material 3を基礎とするが、見た目はAEGIS独自Theme
* Navigation Compose
* Window Size Class
* Flowによる状態管理
* Compose PreviewとScreenshot Test

## AI Display

```text
display-ui/
  src/
    layout/
    modes/
    components/
    stream/
    snapshot/
    privacy/
    recovery/
```

Webのデザイントークンと一部表示コンポーネントは共有するが、操作コンポーネントは依存させない。

---

# 10. 旧UIの削除方針

最初に旧UIを消してから作り始めると、API不足や承認経路の欠落を比較できなくなる。

そのため、コード上は次の順で処理する。

1. `ui-v2`ブランチを作成
2. 旧UIの機能一覧とAPI依存を記録
3. 旧UIルートをFeature Flag配下へ移動
4. 新UIをデフォルトにする
5. 新旧の機能パリティをE2Eで確認
6. 旧Jinjaテンプレート、CSS、JavaScriptを削除
7. 旧Android Composableを削除
8. `dashboard_legacy`から表示責務を除去
9. 再利用していたロジックをManager／Serviceへ移動
10. Feature Flagと互換ルートを削除

最終状態では旧UIを残さない。Git履歴だけを復旧手段とする。

削除対象：

* 旧Dashboardテンプレート
* 旧Dashboard CSS／JavaScript
* 旧画面専用の整形関数
* 旧`State / Home / Action` Composable
* 使われなくなったUI API
* 旧UIだけが使用するテスト
* 重複した状態モデル
* モックのまま残ったUIデータ

残す対象：

* PolicyEngine
* Manager群
* Approval lifecycle
* Audit data
* Chat history
* gRPC
* Capability Catalog
* Notification routing
* Redaction処理

---

# 11. 実装ロードマップ

## Phase 0：調査と契約固定

* 現在の全画面、API、イベント、状態を棚卸し
* UIから参照されているJSONLや内部関数を特定
* Approval lifecycleを図式化
* Web／Android／Displayの情報マッピングを作成
* 旧UI削除対象を確定
* UI Contractを定義

完了条件：

* 全旧画面が新しい画面のどこに移るか決まっている
* 未定義状態がない
* API不足一覧が完成している

## Phase 1：デザインシステム

* Design tokens
* Typography
* Iconography
* Layout grid
* Severity／Risk表現
* 共通カード
* Loading／Error／Offline
* Approval Card
* Task Card
* Server Card
* Timeline
* Chart規約

完了条件：

* StorybookとCompose Previewで全状態を確認可能
* コントラスト検査に合格
* Light themeを作らず、Dark themeを完成させる

## Phase 2：UI API

* `/api/ui/overview`
* `/api/ui/stream`
* Approval統一Schema
* Server状態統一
* Freshness情報
* Read-only display token
* API Contract test

完了条件：

* UIが内部ファイルを直接読まない
* Web、Android、Displayが同じ状態を表示する
* 切断時にStaleへ変化する

## Phase 3：Web基盤

* Application shell
* Navigation
* Command Center
* Global chat drawer
* Attention center
* Responsive layout
* Authentication

## Phase 4：Web詳細

* Approvals
* Work
* Systems
* Mind & Memory
* Activity
* Settings
* LLM Usage
* Developer details

## Phase 5：Android

* 新Theme
* 新Navigation
* Home
* Chat
* Approvals
* Tasks
* Permissions
* Settings
* Tablet layout
* Reconnect／Offline

## Phase 6：AI Display

* Fullscreen shell
* Display state machine
* Normal／Idle／Executing／Approval／Critical／Offline／Privacy
* Read-only authentication
* Snapshot cache
* Stream reconnect
* Cursor非表示
* キオスク起動
* 自動復旧

## Phase 7：統合と実機試験

* Windows Web
* Android実機
* AndroidをWi-Fiから切断
* LAN外接続
* Ubuntu上のAI Server
* Display用ノートPC
* Docker再起動
* サーバー単体停止
* AI Server再起動
* Approval同時配信
* 承認後の一度だけの実行
* 設定永続化

## Phase 8：切替と削除

* 新UIをデフォルト化
* 実運用で安定性確認
* 旧UIコード削除
* 不要API削除
* モック調査
* ドキュメント更新
* スクリーンショットと操作手順を更新

---

# 12. テストと完了条件

## 12.1 画面サイズ

### Web／Display

* 1366×768
* 1920×1080
* 2560×1440

### Android

* 360×800
* 412×915
* 横画面
* 8インチ相当
* タブレット
* 文字サイズ200%

## 12.2 アクセシビリティ

* WebはWCAG 2.2 AAを目標
* Androidは48dp以上の操作領域
* 色だけに依存しない
* キーボードフォーカスを可視化
* TalkBackの読み上げ順を検証
* Reduce motion対応
* グラフにテキスト要約を付ける
* エラーの原因と復旧方法を表示

## 12.3 機能

* WebとAndroidのチャット履歴が一致
* 全チャネルで同じApproval IDを表示
* Kioskは承認操作できない
* 承認された処理は一度だけ実行
* Expired approvalは実行不可
* Audit Groupから関連タスクへ遷移可能
* Server状態が実際の状態と一致
* 設定がDocker再構築後も保持される

## 12.4 障害耐性

* AI Server停止
* Browser Server停止
* Android切断
* SSE切断
* gRPC再接続
* API部分失敗
* 古いSnapshot
* 不正なイベント
* 長時間稼働
* PC再起動
* ブラウザクラッシュ

## 12.5 セキュリティ

* Display tokenでPOST不可
* CSRF対策
* Approval replay不可
* 認証期限切れ
* Raw secret非表示
* OTPやカード情報のRedaction
* Privacy mode
* Raw Screenshotの不用意な常時表示禁止

## 12.6 性能目標

LAN環境でのプロジェクト目標として次を設定する。

* 状態変化から画面反映まで500ms以内
* 通常操作への視覚応答100ms以内
* Command Center初期表示2秒以内
* Displayを72時間連続稼働してメモリが増加し続けない
* 画面更新によるCPU占有を抑える
* 非表示タブではアニメーションとPollingを縮退

---

# 13. 最終的な画面像

## Web

多数のカードが並ぶ管理画面ではなく、

* 現在の仕事
* 注意が必要なこと
* システム状態
* AIの判断状態
* 最近の出来事

が上から自然に理解でき、必要に応じて深く掘れる司令室。

## Android

ダッシュボードの縮小版ではなく、

* AEGISと会話する
* 承認する
* 現在の仕事を見る
* 接続や権限問題を直す

ための携帯コントローラー。

## AI専用ディスプレイ

操作パネルではなく、

* AEGISが今何をしているか
* 正常に動いているか
* 何を考慮しているか
* ユーザーの対応が必要か

を常時伝える、AEGISの「顔兼ステータスディスプレイ」。

この3役を明確に分けることが、今回の刷新で最も重要である。

# AEGIS シネマティックUI拡張計画

## 1. 基本コンセプト

映画的要素を装飾として追加するのではなく、AEGIS内部の状態を人間が短時間で理解するための表現として利用する。

各演出には必ず意味を割り当てる。

| 表現     | 示す情報                              |
| ------ | --------------------------------- |
| 色      | 正常性、警告、エラー、承認待ち                   |
| 動く速さ   | AEGISの活動量                         |
| 線の密度   | 利用可能な機能数                          |
| 発光の強さ  | 現在の重要度                            |
| パルス    | 実際の通信やCapability実行                |
| 揺れ・歪み  | 不安定、再試行、エラー                       |
| 線の切断   | サーバーや機能の停止                        |
| 球体の大きさ | システム全体の活動規模                       |
| 外側のリング | タスク、承認、セキュリティなどの外部状態              |
| 周囲のノード | PC、Android、Browser、Room、Devなどの接続先 |

映画的演出を見ただけで、次のことが分かる状態を目指す。

* AEGISは正常か
* 今活動しているか
* どのサーバーを使用しているか
* 問題が起きているか
* ユーザーの対応が必要か
* 何をしようとしているか

---

# 2. AEGIS Core Sphere

## 2.1 役割

AI球体を、AEGIS全体の状態を集約する「Core Visualization」とする。

専用ディスプレイでは画面中央または左中央に大きく配置する。Webダッシュボードでは縮小版をCommand Centerに配置し、詳細画面と連動させる。

スマートフォンでは3D球体をそのまま縮小せず、意味を保った簡略版のCore Glyphを表示する。

## 2.2 球体の構造

球体は次のレイヤーで構成する。

### Core

中心にある半透明の発光体。

AEGIS本体、LLM、Planner、Autonomous Loopなど、AIの中心的な処理状態を表す。

### Primary Arcs

球体を形成する大きな線。

各線を主要サーバーに割り当てる。

* AI Server
* PC Server
* Android Server
* Browser Server
* Room Server
* Dev Server

各サーバーの線は異なる角度で球体を一周する。

### Capability Segments

Primary Arcを複数の短い区間に分け、それぞれをCapabilityまたはCapability群に割り当てる。

例としてBrowser Serverの線を次の区間に分ける。

* Browser control
* Page observation
* Search
* Form interaction
* Download
* Authentication session
* Screenshot
* Verification

Capabilityが多い場合は、1機能1区間ではなく、機能カテゴリ単位に集約する。

### Activity Pulses

線の上を移動する光。

実際にデータや命令が流れていることを表す。

例：

* AI ServerからBrowser Serverへ光が移動
  → AEGISがブラウザ操作を要求

* Browser ServerからAI Serverへ光が戻る
  → 観測結果または実行結果が返ってきた

* AI ServerからAndroidへAmberの光が移動
  → 承認リクエストを送信

単なるループアニメーションにはせず、実際のイベントを受けたときだけ発生させる。

## 2.3 線の状態表現

| 状態       | 表現                    |
| -------- | --------------------- |
| 利用可能・待機  | 細いCyanの連続線            |
| 現在使用中    | 白に近い強い発光と移動パルス        |
| 高負荷      | 線の回転速度とパルス頻度が上昇       |
| 無効化済み    | 暗い点線                  |
| 未設定      | 輪郭だけの半透明線             |
| 接続確認中    | 断続的に明滅                |
| Degraded | Amberの揺らぎ             |
| Offline  | 線の一部が消失または切断          |
| Error    | 赤い亀裂と局所的な振動           |
| 復旧中      | AmberからGreenへ伸びる再構築線  |
| 復旧完了     | Greenの波が一周した後、Cyanへ戻る |

Greenは正常状態の常時色にはしない。

正常時はCyanとし、Greenは「問題が解決した」という一時的なイベント表現に使う。これにより、復旧を視覚的に認識しやすくする。

## 2.4 球体全体の状態

### IDLE

* ゆっくり回転
* 線は細い
* Coreは弱く呼吸する
* パーティクルは少ない
* 背景も静か

### OBSERVING

* 球体表面を走査線が移動
* 観測対象のサーバー線が明るくなる
* 外側からCoreへ小さなパルスが流れる
* 「情報を取り込んでいる」方向を表現

### PLANNING

* 球体内部に複数の枝分かれ線が現れる
* 候補が比較されるように一時的な経路が形成される
* 計画決定時、選択された経路だけが明るく残る
* 内部推論そのものではなく、計画段階と選択結果を表現する

### EXECUTING

* 回転速度が上がる
* 使用中サーバーの線が強く発光
* 実際の通信に合わせてパルスが走る
* Coreから対象ノードに向かってエネルギーが放出される
* Current Operationパネルも球体と同期する

### WAITING

* 回転が遅くなる
* 使用予定の線だけが点滅
* 待機理由を画面上に表示
* 通信待ちなら対象サーバーとの線だけがゆっくり伸縮

### WAITING FOR APPROVAL

* 球体の周囲にAmberの封鎖リングが形成される
* 実行予定のサーバー線が途中で停止
* パルスも承認リングの手前で止まる
* 承認内容を中央パネルに表示
* スマートフォンまたはWebで確認するよう案内

### ERROR

* 問題が起きた部分だけを赤くする
* システム全体が停止していない限り、球体全体を赤くしない
* エラー箇所に赤い亀裂、ノイズ、振動を表示
* 関係のないサーバーは通常表示を維持
* Criticalの場合だけCoreまで赤く変化

### RECOVERY

* 問題箇所をAmberで診断中として表示
* 復旧処理の進行に合わせて線を再生成
* 成功するとGreenの波が該当線から球体全体へ広がる
* 数秒後に通常のCyanへ戻る

---

# 3. Core Sphereの情報量制御

Capabilityをすべて線として表示すると、球体が情報過多になる。

そのため、3段階の表示レベルを用意する。

## Level 1：通常表示

* 主要サーバー6本
* 現在使用中のCapability
* 問題があるCapability
* 承認待ちのCapability

## Level 2：対象サーバー詳細

あるサーバーが使われたとき、そのサーバーの線を手前へ回転させ、Capabilityカテゴリを展開する。

専用ディスプレイでは自動的にフォーカスする。

Webでは球体またはサーバーカードを選択して表示する。

## Level 3：診断表示

エラー時のみ利用する。

* Capability単位の状態
* 依存関係
* 接続状態
* リトライ回数
* 最後に成功した時刻
* エラー発生地点

通常時には表示しない。

---

# 4. 球体以外の映画的かつ実用的な表現

## 4.1 Mission Orbit

球体の外側を回る軌道リングで、現在のタスクを表現する。

リングをタスクの進行段階に分割する。

```text
Observe → Understand → Plan → Approve → Execute → Verify → Complete
```

現在地点が発光し、完了した区間は固定表示される。

### 実用性

* タスクの現在段階が一目で分かる
* 単なる不正確なパーセンテージより意味が明確
* どこで停止しているか分かる
* 承認や検証が未完了であることを表示できる

複数タスクがある場合、最重要タスクだけを球体のMission Orbitに表示し、他は画面下部のTask Queueに置く。

---

## 4.2 Device Constellation

球体の周囲に接続デバイスを小さなノードとして配置する。

* PC
* Android
* Browser
* Room
* Dev environment
* AI専用ディスプレイ
* 将来的なスマートグラスやロボット

### 表現

| 状態                 | ノード表現            |
| ------------------ | ---------------- |
| Online             | 明るい輪郭            |
| Active             | Coreとの接続線が発光     |
| Observing          | ノードからCoreへパルス    |
| Acting             | Coreからノードへパルス    |
| Offline            | 暗くなり接続線が消える      |
| Degraded           | Amberの点滅         |
| Permission missing | ノード上にAmberの欠損マーク |
| Approval pending   | ノードの周囲にAmberリング  |

### 実用性

「AEGISがどの端末を見ているか」「どの端末を操作しているか」が分かる。

---

## 4.3 Data Flow Trails

サーバー間の処理を、光の軌跡で表示する。

例：

```text
User
 ↓
AI Core
 ↓
Planner
 ↓
Browser Server
 ↓
Web page
 ↓
Verification
 ↓
Memory
```

常時表示はせず、処理が発生したときだけ数秒間表示する。

### 実用性

* AEGISの処理経路が分かる
* どこで止まったか分かる
* サーバー間通信の問題を発見できる
* Capability実行の透明性が上がる

画面上には同時に最大3本まで表示し、それ以上はまとめる。

---

## 4.4 Event Shockwave

重要イベントが起きたとき、球体から波紋を出す。

### 波紋の意味

| 波紋     | イベント           |
| ------ | -------------- |
| Cyan   | 通常タスク開始        |
| White  | Capability実行成功 |
| Violet | 計画確定           |
| Amber  | 承認要求           |
| Red    | エラーまたは重大警告     |
| Green  | 復旧またはタスク完了     |

波紋の大きさは重要度、速度は緊急度を表す。

### 実用性

画面を注視していなくても、周辺視野で重要な変化を認識できる。

---

## 4.5 Approval Containment Field

承認が必要な操作を、AEGISが意図的に止めていることを表現する。

球体から対象サーバーへ伸びた光を、Amberの半透明フィールドが遮断する。

フィールド内に以下を表示する。

* 操作内容
* 対象
* リスク
* AIが必要とした理由
* 期限
* 承認先

### 実用性

「AEGISが故障して止まっている」のではなく、「安全のため意図的に待っている」ことを明確に区別できる。

---

## 4.6 Threat Horizon

画面外周に細いリングを配置し、セキュリティや重大な問題を表示する。

通常はほぼ見えない。

問題が発生した方向だけが発光する。

例：

* 左上：PC
* 右上：Browser
* 右下：Android
* 左下：Room

Browser Serverでセキュリティ問題が起きた場合、右上側の外周だけが赤くなる。

### 実用性

中央のタスク表示を壊さず、異常の発生領域を認識できる。

---

## 4.7 Diagnostic Fracture

映画でよくあるホログラムの亀裂を、エラーの依存関係表示として使う。

問題が発生した線から、影響を受ける機能へ亀裂が伸びる。

例：

```text
Browser Server Offline
 ├─ Search unavailable
 ├─ Page observation unavailable
 └─ Web task paused
```

### 実用性

原因と影響範囲を同時に表示できる。

関係のない機能まで赤くしないことが重要。

---

## 4.8 Recovery Reconstruction

エラー解消時に単に赤から緑へ変えるのではなく、壊れた線が再構築される過程を表示する。

1. 赤い亀裂が停止
2. Amberで接続確認
3. 線が端から再生成
4. Greenのパルスが往復
5. 接続検証に成功
6. Cyanへ戻る

### 実用性

「エラー表示が消えただけ」なのか、「接続を再検証して復旧した」のかを区別できる。

---

## 4.9 Holographic Operation Timeline

画面下部に、監査ログを映画的なタイムラインとして表示する。

ただし生ログを高速スクロールさせない。

操作単位でまとめる。

```text
21:14:02  User request received
21:14:04  Plan created
21:14:06  Browser capability selected
21:14:08  Approval requested
21:15:21  Approved from Android
21:15:24  Action executed
21:15:27  Verification passed
```

### 表現

* 現在イベントは中央
* 過去イベントは左へ薄くなる
* 次に予定されている処理は右側に点線で表示
* エラー箇所は赤い切れ目
* 承認待ちはAmberの停止線

### 実用性

AEGISが突然動いたように見えず、直前に何が起きたかをすぐ確認できる。

---

## 4.10 Context Scan

AEGISがユーザーや周囲の状況を観測するとき、薄いスキャン表示を使用する。

対象例：

* PCのアクティブウィンドウ
* Androidの現在アプリ
* ユーザー位置
* Room sensor
* 予定
* 通知
* Webページ

画面上に常時監視映像を出すのではなく、次のような概要を表示する。

```text
CONTEXT UPDATED 8s AGO

Location: Home
Active device: PC
Activity: Development
Focused application: VS Code
Confidence: 87%
```

### 実用性

AEGISの状況推定が、何を根拠にしているか確認できる。

古い情報の場合、スキャン線を停止し`STALE`表示に変える。

---

## 4.11 Memory Constellation

記憶を宇宙空間の星のように大量表示するのではなく、現在の判断に使用された記憶だけを小さな光点として球体周辺に出す。

* 人物記憶
* 過去の会話
* 手順記憶
* 失敗経験
* ユーザー設定

使用された記憶はCoreへ光が流れる。

### 実用性

AEGISが現在の判断で何種類の記憶を参照しているか分かる。

内容そのものは隣のMemory Contextパネルに要約表示する。

プライバシーモードでは内容を隠し、カテゴリだけ表示する。

---

## 4.12 Decision Branch

AEGISが複数案を比較しているとき、球体の前方に数本の薄い分岐線を出す。

例：

```text
A: Browserで操作
B: APIを使用
C: ユーザーへ確認
```

決定後、選ばれた線だけを残し、理由を短く表示する。

### 実用性

Chain of Thoughtを公開せずに、AEGISが選択肢を比較したことと、採用した方針を表示できる。

---

## 4.13 Confidence Halo

Coreの周囲にある薄い光輪で、状況認識や判断の確信度を表す。

ただし単純な数値だけに依存しない。

| 状態  | 表現        |
| --- | --------- |
| 高信頼 | 安定した完全な輪  |
| 中信頼 | 薄い切れ目のある輪 |
| 低信頼 | 揺れる断続的な輪  |
| 不明  | 輪を表示しない   |

隣に必ず文字を表示する。

```text
Confidence: Low
Reason: Android context is unavailable
```

### 実用性

AIが曖昧な状況を確信しているように見せることを防ぐ。

---

## 4.14 Voice Presence

AEGISが音声を出している場合、球体表面に発話波形を流す。

* 発話中：表面に波形
* 聞き取り中：外部からCoreへ波形
* 音声無効：表示なし
* 認識失敗：Amberの短い崩れ

字幕は別パネルに必ず表示する。

### 実用性

音声が届いているか、AEGISが発話しているかを目視できる。

---

## 4.15 Cinematic Focus Shift

重要イベント発生時、カメラやレイアウト全体が対象へゆっくりフォーカスする。

例：

* Browserエラー
  → Browserの線が前面へ回転

* Android承認
  → AndroidノードとApproval Fieldを拡大

* Room alert
  → Roomノードが前面へ移動し、環境情報を表示

### 実用性

ユーザーが画面内を探さなくても、重要情報へ視線を誘導できる。

急激なズームは避け、300～700ms程度の移動にする。

---

# 5. シネマティック状態プリセット

## 通常待機

* Core Sphereは低速回転
* 主要サーバー線は薄いCyan
* 接続ノードは静止
* 次の予定を右下に表示
* 画面全体は暗く落ち着いた状態

## Web調査実行

* Browser Arcが前面へ移動
* AI CoreからBrowserノードへパルス
* Mission Orbitが`Execute`へ進む
* 右側に現在閲覧中のサイトと行動概要
* 結果取得時にBrowserからCoreへ光が戻る
* Verify段階で白いスキャンが走る

## PCとBrowserを使う複合タスク

* Browser ArcとPC Arcが同時に発光
* サーバー間の依存関係を光線で表示
* 現在使用中の方を白、次に使う方をVioletで表示
* タスク切替時にフォーカスも移動

## 承認待ち

* 実行パルスがAmber Fieldで停止
* 球体の回転が低速化
* Mission Orbitが`Approve`で停止
* 承認内容を中央へ表示
* AndroidノードがAmberに点滅
* 期限が近づくと外周リングが縮む

## Browser Server障害

* Browser Arcが赤く亀裂
* Browserノードとの接続線が切断
* 影響を受けるCapability区間だけ消える
* Mission Orbitが停止
* 右側に原因、影響、再接続状況
* 他サーバーは正常表示を維持

## 自動復旧成功

* 赤い亀裂が停止
* Amberの診断パルスが走る
* Browser Arcが再生成
* Browserとの往復通信が成功
* Greenの波が一周
* `RECOVERED`を数秒表示
* Cyanの通常状態へ戻る
* 停止中タスクを再開

## タスク完了

* Mission Orbitが閉じる
* GreenまたはWhiteの波紋
* 完了結果を中央に短く表示
* 使用したサーバー線が一度だけ強く発光
* その後IDLEへ戻る

---

# 6. 各UIへの適用

## AI専用ディスプレイ

球体を画面の主役にする。

### 推奨レイアウト

```text
┌────────────────────────────────────────────────────────┐
│ AEGIS / STATUS / AUTONOMY / TIME / CONNECTION          │
├───────────────┬──────────────────────┬─────────────────┤
│ AI STATE      │                      │ ATTENTION       │
│ GOAL          │     CORE SPHERE      │ APPROVAL        │
│ CONFIDENCE    │     MISSION ORBIT    │ ERRORS          │
│ CONTEXT       │                      │ NEXT ACTION     │
├───────────────┴──────────────────────┴─────────────────┤
│ OPERATION TIMELINE / SERVER STATUS / UPCOMING TASK     │
└────────────────────────────────────────────────────────┘
```

操作は要求しない。

状態に応じて球体周辺の補助パネルが自動的に入れ替わる。

## Webダッシュボード

球体をCommand Centerの中央に配置するが、詳細情報を隠さない。

### Web固有機能

* 球体上のサーバー線を選択
* 該当サーバー詳細を開く
* Capability区間にフォーカス
* Timelineと同期
* エラー発生地点からAuditへ移動
* Approval Cardへ移動
* アニメーション停止
* 診断モード切替

球体だけですべてを操作させず、従来型の一覧やテーブルも横に残す。

## Android

スマートフォンではCore Sphereを簡略化する。

### Core Glyph

* 中心Core
* 最大6本の短い軌道
* Active serverだけ強調
* Error Arc
* Approval Ring
* Activity pulse

ホーム上部に120～180dp程度で配置する。

フル3D演出は詳細画面だけにし、通常画面ではバッテリー消費を抑える。

---

# 7. 映画的演出の制限ルール

## 7.1 色だけで状態を伝えない

赤い線には必ず以下のいずれかを併記する。

* `ERROR`
* `OFFLINE`
* `DEGRADED`
* エラーアイコン
* 問題の説明

## 7.2 激しく動かす条件を限定する

激しい動きは次の場合だけ。

* 高負荷の実行中
* 複数サーバーの複合タスク
* Critical alert
* 短時間のタスク完了演出

通常時まで激しく動くと、活動状態を判別できなくなる。

## 7.3 常時点滅を避ける

点滅はAttentionまたは接続確認中だけに限定する。

通常のOnline状態は静的な発光にする。

## 7.4 情報を隠さない

球体のアニメーションだけでなく、隣に必ず文字情報を置く。

例：

```text
BROWSER SERVER
Status: DEGRADED
Issue: Verification service unavailable
Affected: browser.form_submit
Retry: 2 / 5
Last success: 42 seconds ago
```

## 7.5 Reduced Motion

動きを抑える設定では次のように変える。

* 回転を停止
* パルスを短い発光に置換
* 波紋を色変化に置換
* カメラ移動を即時切替に置換
* 状態表現の意味は維持

---

# 8. 実装用状態モデル

UI側が個別イベントを直接解釈するのではなく、バックエンドでVisual Stateを生成する。

```text
core_state:
  mode
  health
  activity_level
  confidence
  active_goal
  attention_level

server_visuals:
  server_id
  health
  availability
  activity
  load
  latency
  capabilities_available
  capabilities_active
  capabilities_degraded
  last_seen

task_visual:
  task_id
  phase
  progress_type
  current_action
  next_action
  blocked_reason
  involved_servers

approval_visual:
  approval_id
  target_server
  target_capability
  risk
  expires_at

visual_events:
  pulse
  shockwave
  fracture
  recovery
  focus_target
```

## Activity Level

0～4の段階で統一する。

| Level | 意味                   | 球体       |
| ----: | -------------------- | -------- |
|     0 | Sleep / Offline      | ほぼ停止     |
|     1 | Idle                 | 低速       |
|     2 | Observing / Thinking | 中速、内部変化  |
|     3 | Executing            | 高速、通信パルス |
|     4 | Intensive            | 複数線が活性化  |

CPU使用率をそのまま活動レベルにしない。

AEGISが論理的に何をしているかを基準にする。

---

# 9. 表示イベントの優先順位

複数の演出が同時に起きた場合の優先順位を固定する。

1. Critical safety alert
2. Approval expiring soon
3. Server or capability error
4. User-requested task execution
5. Autonomous task execution
6. Recovery
7. Task completion
8. Observation
9. Idle animation

Critical中にタスク完了演出を前面へ出さない。

承認待ち中に背景の自律活動が目立ちすぎないようにする。

---

# 10. 推奨する最終デザイン

AEGIS専用ディスプレイの中央には、多数の光線から構成された立体的なCore Sphereを配置する。

球体は次の3つを同時に表す。

1. **AEGIS自身の活動状態**
2. **各サーバーとCapabilityの稼働状態**
3. **現在のタスクにおける情報と命令の流れ**

球体の周囲には以下を配置する。

* Mission Orbit：タスク進行
* Device Constellation：接続端末
* Confidence Halo：判断の確信度
* Approval Field：安全停止
* Threat Horizon：重大問題
* Memory Points：使用中の記憶
* Data Flow：サーバー間通信

球体の下にはOperation Timelineを置き、横には人間が読める状態説明を表示する。

これにより、映画的でありながら、単なる雰囲気ではなく、AEGISの内部状態を把握するための実用的なUIになる。
# AEGIS UI 第3次改修計画

## Display Director・多層画面・情報網羅性の再設計

# 1. 現状評価

## 改善された部分

今回の更新では、以前指摘した球体の再生成問題は解消されています。

* Three.js Sceneをマウント時に一度だけ生成
* Props更新を`targetRef`へ反映
* `THREE.Clock`によるDelta time
* `MathUtils.damp`による速度・Opacity補間
* 色の連続補間
* Shader Core
* Server Arc
* Unreal Bloom
* Display向けSSE
* Capability開始・完了・失敗イベント
* ContainmentとRecovery表現

が追加されています。

専用ディスプレイでも`surface=display`としてSSEを購読するようになっているため、以前の15秒ポーリングだけの状態からは改善しています。

ただし、現在追加されたのは主に「球体内の視覚効果」であり、**画面全体を管理する表示システム**が不足しています。

---

# 2. 発見した主要問題

## P0：専用ディスプレイにレイヤー管理が存在しない

現在のDisplayは次の要素を通常のDOMレイアウトとして縦に並べています。

* Current Operation
* Attention
* Core Sphere
* Mission Phase
* Recent Events
* Server Rail

Attentionも通常のカードであり、Overlay、Portal、Takeover Layer、Modal Layerなどはありません。

したがって、現在は以下を実現できません。

* 右上から一時的に出る通知
* 球体の前面に浮かぶ通知
* 画面中央を占有する重要警告
* 背景全体を暗くするCritical表示
* 承認要求による一時的な画面構成変更
* 複数通知の優先順位制御
* 通知が解決されたときの解除演出
* Privacy／Offline Layer
* 通知同士の割り込みと待ち行列

必要なのは通知コンポーネントの追加ではなく、**Display DirectorとCompositor**です。

---

## P0：一画面に収まる構造になっていない

現在のCSSは、

* `min-height: 100vh`
* 4行のGrid
* 上部カード
* 最低52vhのCore
* 下部2カード
* Server Rail
* Core凡例
* Core Caption
* 各領域間のGapとPadding

を同時に積み上げています。

さらに幅1040px以下では、Display上部と下部を1カラムへ変更します。非操作画面なのに縦長化し、スクロールしなければ見られない画面になります。

`min-height`ではなく、次の制約が必要です。

```text
height: 100dvh
max-height: 100dvh
overflow: clip
```

動的Viewport単位の`dvh`は、実際に見えているViewportに合わせて寸法を調整するための単位です。通常の`vh`は現在のブラウザでは大きいViewport相当となる場合があり、全画面表示で内容が隠れる可能性があります。

ただし、単に`100dvh`へ変更するだけでは足りません。全要素に高さの予算を割り当てる必要があります。

---

## P0：通知の重要度を画面構成へ反映していない

現在のAttentionは最大4件を右上カードへ並べるだけです。

次の2件が同時に発生しても、

* Room Serverで火災センサー警告
* 軽微な承認要求

同じAttention領域へ並びます。

また、`attentionItems()`は承認要求を先頭に置いてから既存Attentionを連結しており、最終的な重大度ソートをしていません。したがってCriticalよりApprovalが上に出る可能性があります。

重要通知には「カード内の並び順」ではなく、画面全体の優先権が必要です。

---

## P0：Visual Eventの意味判定が単純すぎる

現在のクライアント側判定では、`status`または`connection`を含むイベントは、

* OfflineならDisconnect
* それ以外ならRecovery

と判断します。

そのため、通常のOnline heartbeatや初回接続までRecovery Waveになる可能性があります。

また、全イベントの寿命が一律4.5秒です。

```text
expiresAt = createdAt + 4500
```

これでは、

* 軽い処理完了
* 承認待ち
* Critical failure
* Server offline
* Recovery

がすべて同じ時間的扱いになります。

Criticalや承認は時間切れで消すのではなく、**状態が解決されるまで継続**させる必要があります。

---

## P0：バックエンドのCore Health判定が誤解を招く

現在のCore Healthは、

* Degradedサーバーがあれば`DEGRADED`
* 全サーバーに近い数がOfflineなら`OFFLINE`
* それ以外は`ONLINE`

となっています。

つまり、Browser、Android、Roomなど複数サーバーの一部がOfflineでも、Core全体は`ONLINE`と表示される可能性があります。

また、Attention LevelはApprovalが1件でもあれば、CriticalなOfflineよりApprovalが優先されます。

```text
approval if pending
else critical if offline
```

これでは全体状態を表す球体の色と実際の問題の深刻度が一致しません。

### 修正後の判定

| 状態                | Core Health           |
| ----------------- | --------------------- |
| AI Server自体が停止    | OFFLINE               |
| 実行中タスクに必要なサーバーが停止 | BLOCKED               |
| 必須サーバーの一部が停止      | DEGRADED              |
| 任意サーバーが停止         | ONLINE_WITH_ATTENTION |
| サーバー復旧処理中         | RECOVERING            |
| 全必須サービス正常         | ONLINE                |

ApprovalはHealthではなく、別軸の`interaction_state`として扱います。

---

## P0：Freshnessが実際のLive状態を表していない

バックエンドのFreshnessは現在、常に`live: True`を返しています。

SSEが切断されても、

* 接続中
* 再接続中
* Snapshotのみ
* Stale
* 完全Offline

を区別できません。

Display側のSSE Hookにも、次がありません。

* `onopen`
* `onerror`
* 接続状態
* 最終イベント時刻
* 再接続回数
* Event cursor
* 取りこぼし検出
* Replay要求

専用画面では古いデータを正常なLive値のように見せるのが最も危険です。

---

# 3. ダッシュボードで表示されていない情報

UI Overviewには現在、次の情報があります。

* Core
* Attention
* Current Task
* Servers
* User State
* Mind Summary
* Notifications
* Approvals
* Commitments
* Usage
* Freshness

しかし表示側の利用状況は不完全です。

| 情報                     | 専用Display     | Dashboard        |
| ---------------------- | ------------- | ---------------- |
| Core                   | 部分表示          | 部分表示             |
| Attention              | 最大4件          | 表示               |
| Current Task           | 1件のみ          | 1件のみ             |
| Servers                | Rail          | 概要＋Systems       |
| User State             | 未表示           | Raw JSONのみ       |
| Mind Summary           | 未表示           | 一部要約／別画面Raw JSON |
| Notifications          | Attention経由のみ | Recentのみ         |
| Approvals              | 概要のみ          | Pendingのみ        |
| Commitments            | 未表示           | Raw JSONのみ       |
| Usage                  | 未表示           | Summary 1行のみ     |
| Freshness              | 未表示           | 上部に一部            |
| Scheduled Tasks        | 未提供           | 未表示              |
| Completed／Failed Tasks | 未提供           | 未表示              |
| Audit Groups           | 未提供           | 未表示              |
| Errors／Stack trace     | 未提供           | 未表示              |
| Capability stats       | 未提供           | 未表示              |
| Sleep状態                | 未提供           | 未表示              |
| Situation推定            | User State次第  | 構造化表示なし          |
| Delegation             | 未提供           | 未表示              |
| Hooks                  | 未提供           | 未表示              |

## Work画面

現在はCurrent Task 1件と最大12ステップだけです。Active一覧、Waiting、Scheduled、Completed、Failed、Research、Self-developmentなどはありません。

## Approvals画面

Pendingだけで、Resolved、Rejected、Expired、実行結果、履歴、関連Auditがありません。

## Systems画面

基本的なServer状態だけで、次が不足しています。

* Heartbeat age
* Capability数
* 利用可能Capability
* 現在使用中Capability
* 依存サービス
* Last success
* Retry
* Active approvals
* Permission status
* Latency
* Version差異

## Mind & Memory画面

User State、Mind、CommitmentsをRaw JSONで表示しており、検索・関係表示・根拠・信頼度・時系列などはありません。

## Activity画面

ページを開いてから受信した最大10イベントしか表示しません。再読み込みすると消え、イベントがない場合はAttentionへ置き換わります。Audit、Task履歴、Notification履歴ではありません。

## Settings画面

実際の設定フォームではなく、旧ページやAPIへのリンクだけです。

## Dashboardの球体

Command CenterのCore Sphereには`visualEvents={[]}`が渡されています。そのため、専用Displayでは出るPulseやFractureが、Dashboardの球体では一切出ません。

---

# 4. 最新UIデザインから採用する要素

## 4.1 Reactive GlassはOverlayだけに使う

2025年以降のAppleのLiquid Glassでは、透明素材、背景の屈折、動きに反応する表面などが大きな特徴になりました。一方、初期版では可読性への懸念もあり、後の調整で読みやすさが改善されています。

AEGISでは画面全体をGlassにしません。

使う場所は、

* 一時通知
* Priority Overlay
* Server Detail展開
* Context Panel
* Approval Containment
* Floating telemetry

だけに限定します。

基本情報は不透明度の高いDark Surfaceで読みやすく保ちます。

---

## 4.2 Z軸の高さを情報優先度に対応させる

Fluent 2ではElevationを、重要度とフォーカスを伝える視覚階層として使用しています。高いElevationほど背景から離れ、Pop-up dialogなどに利用されます。

AEGISでもZ軸を意味付けします。

| Zレベル | 用途                           |
| ---: | ---------------------------- |
|    0 | 背景、グリッド、環境光                  |
|   10 | Core Sphere                  |
|   20 | 常設Telemetry                  |
|   30 | Context Panel                |
|   40 | 通常通知                         |
|   50 | 重要通知                         |
|   60 | Approval Takeover            |
|   70 | Critical Takeover            |
|   80 | Privacy／Offline System Layer |

単なる`z-index`ではなく、Blur、Shadow、背景暗転、視差も同時に変えます。

---

## 4.3 映画的UIは「派手な警告」ではなくストーリーと実データを統合する

『The Martian』の画面制作では、映画的ストーリー、実データ、科学の中間を狙い、現実には使われない巨大な赤い警告をあえて避けたと説明されています。

AEGISも映画をそのまま真似するのではなく、

* 何が起きたか
* どこで起きたか
* 何に影響するか
* AEGISが何をしているか
* ユーザーに何が必要か

を演出に対応させます。

---

## 4.4 状態通知と割り込み通知を分ける

W3Cも、通常のStatus Messageは現在の文脈を不必要に中断せず通知し、ModalのようなContext changeはより重大な情報に使われるという区別をしています。

AEGISでは、

* 通常Status：端やTimeline
* 重要Status：浮遊Overlay
* Critical：画面中央Takeover

に分けます。

---

# 5. 新しいDisplay Compositor

専用画面を次の8レイヤーに分割します。

```text
L7  System Veil
    Privacy / Offline / Fatal / Reconnecting

L6  Priority Takeover
    Critical / Security / Room alert / fatal task

L5  Action Takeover
    Approval / user response required / blocked

L4  Transient Overlay
    Completion / warning / connection / recovery

L3  Persistent Context
    Current operation / attention / next action

L2  Ambient Telemetry
    Mission phase / recent events / confidence / clock

L1  Core World
    AI Sphere / server arcs / pulses / camera choreography

L0  Environment
    background / grid / noise / vignette / light
```

React構成案：

```text
DisplayCompositor
├─ EnvironmentLayer
├─ CoreWorldLayer
├─ AmbientTelemetryLayer
├─ ContextLayer
├─ OverlayStack
├─ ActionTakeover
├─ CriticalTakeover
└─ SystemVeil
```

各レイヤーは`position:absolute; inset:0`で重ねます。

通常のDocument Flowで縦に積み上げません。

---

# 6. Display Director

## 6.1 役割

Display Directorが以下を一元管理します。

* 表示すべき情報
* 優先順位
* 表示位置
* 表示開始
* 表示終了
* 割り込み
* 復帰
* 同種通知の統合
* 表示回数
* Critical継続
* 解決演出
* Privacy
* Offline

球体とDOM通知が別々にイベントを解釈してはいけません。

## 6.2 優先レベル

### P0：System Critical

対象：

* Security alert
* Room critical alert
* AI Core offline
* データ破損
* 全主要サービス停止
* 制御不能状態

表示：

* 画面中央の大型Takeover
* 背景を70%暗転
* 球体を後方へ移動
* 外周をRed
* 原因、影響、時刻、自動復旧状態
* 解決まで消さない
* 複数ある場合は件数と8秒周期の自動切替

### P1：User Action Required

対象：

* Approval
* Passwordなどユーザー入力待ち
* Permission設定待ち
* CAPTCHA
* 物理操作待ち
* 判断確認

表示：

* 中央のAmber Takeover
* 球体の実行Arcを途中で停止
* 操作対象と理由
* 有効期限
* 「スマートフォンまたはWebで確認」
* 入力ボタンは置かない
* 一定時間後は右上へ縮小するが、解決まで消さない

### P2：Important

対象：

* Server degraded
* Task failed
* Budget warning
* Reconnect
* High notification

表示：

* 右側または上部からOverlay
* 8～15秒
* 未解決ならAttention Dockへ移動

### P3：Ambient

対象：

* Capability開始
* Capability完了
* 通常の観測
* Memory consolidation
* 軽微な通知

表示：

* 球体Pulse
* Event Timeline
* 小さなEdge notification
* 3～6秒

---

# 7. 通知の競合ルール

1. P0はすべてに割り込む
2. P1はP2、P3へ割り込む
3. P2はP3へ割り込む
4. P0表示中もP1以下はQueueへ保存
5. 同一`dedupe_key`は統合
6. 同じServer障害を毎Heartbeatで再表示しない
7. 状態が解決するまでPersistent notificationを消さない
8. 解決時は「消える」のではなくRecovery表示へ遷移
9. 5件以上の同レベル通知はグループ化
10. Criticalを時間切れで消さない

---

# 8. 一画面固定レイアウト

## 基本構成

```text
┌─────────────────────────────────────────────────────────┐
│ AEGIS  MODE  CONNECTION                  CLOCK  LIVE    │
│                                                         │
│ CURRENT OPERATION                         ATTENTION     │
│ title                                     compact list  │
│ current action                                          │
│                                                         │
│                  CORE SPHERE                            │
│           server arcs / pulses / focus                  │
│                                                         │
│ OBSERVE ━ PLAN ━ EXECUTE ━ VERIFY ━ COMPLETE            │
│ ●AI ●PC ●ANDROID ●BROWSER ●ROOM ●DEV   EVENT SUMMARY   │
└─────────────────────────────────────────────────────────┘
```

## 高さ予算

1920×1080基準：

| 領域           |    高さ |
| ------------ | ----: |
| Global HUD   |  48px |
| Main Stage   | 残りすべて |
| Mission Rail |  64px |
| Server Rail  |  32px |

Current OperationとAttentionはStage上に浮かせます。

Coreの凡例とCaptionは通常Flowから削除し、Server RailまたはCanvas内ラベルへ統合します。

## 画面サイズ別Density

### 1366×768 Compact

* Attention最大2件
* Recent Event最大2件
* Coreラベル省略
* Current Operation最大2行
* Server detailは1件だけ展開
* Mission Rail 48px

### 1920×1080 Standard

* Attention最大3件
* Recent Event最大4件
* Core server label表示
* Mission Rail 64px

### 2560×1440 Cinematic

* Context summary
* Confidence Halo説明
* 次のCapability
* Memory source count
* より広い余白

幅で1カラムに崩すのではなく、**高さとアスペクト比に応じて情報密度だけを変えます**。

---

# 9. AIディスプレイで追加表示すべき情報

常時すべて出すのではなく、状況に応じて出します。

## 常設

* Mode
* Core Health
* SSE Connection
* Freshness
* Current time
* Current operation
* Current action
* Mission phase
* Server Rail

## タスク中

* Next action
* Current Capability
* Target device／site／application
* Verification state
* Child task数
* Blocked reason
* Task elapsed time

## Idle中

* 次のScheduled task
* Due commitment
* 最後に完了したタスク
* User situation
* Last observation
* Sleep consolidation
* Budget status

## 必要時だけ

* Approval
* Warning
* Error
* Recovery
* Permission missing
* Privacy
* Offline
* Security alert
* Room alert

---

# 10. Dashboard再構築

## Command Center

表示：

* Current Operation
* Critical／Approval
* Core Sphere
* Situation summary
* Task queue
* Next commitment
* LLM budget
* Recent operation timeline
* System summary

Server一覧は通常時に大きく表示しない。

## Work

タブ：

* Active
* Waiting
* Scheduled
* Research
* Self-development
* Commitments
* Completed
* Failed

詳細：

* 元の指示
* Plan
* Step graph
* Capability
* Approval
* Result
* Verification
* Cost
* Audit group

## Approvals

* Pending
* Expiring
* High risk
* Resolved
* Rejected
* Expired
* Failed after approval

List–Detail構成にし、関連Task、Preview、影響、Auditを表示。

## Systems

* Topology view
* Server list
* Capability availability
* Dependency graph
* Heartbeat
* Latency
* Errors
* Permission
* Recovery
* Active task relation

## Mind & Memory

Raw JSONを標準表示にしない。

* Current goal
* Desire state
* Emotion
* People
* Episodic memory
* Semantic memory
* Procedural memory
* Skills
* Recent memories used
* Sleep consolidation
* Confidence and sources

JSONはDeveloper Drawerに残す。

## Activity

サーバー側の永続データを使用する。

* Operations
* Audit groups
* Events
* Notifications
* Errors
* LLM calls
* Settings changes
* Security events

ブラウザを開いてから受信した10件だけに依存しない。

## Settings

旧ページへのリンクではなく、実際のV2設定画面を実装する。

* Autonomy
* Permissions
* Servers
* Privacy
* Notifications
* Models
* Budgets
* Memory
* Display
* Developer
* Backup

---

# 11. UI Overview v3

現在のOverview v2では、1件のCurrent Taskと要約データしか足りません。

次の契約へ拡張します。

```text
ui-overview.v3
├─ core
├─ connection
├─ display_scene
├─ presentations
│  ├─ takeover
│  ├─ overlays
│  ├─ persistent
│  └─ ambient
├─ tasks
│  ├─ primary
│  ├─ active
│  ├─ waiting
│  ├─ scheduled
│  └─ recent
├─ approvals
├─ servers
├─ capabilities
├─ user_situation
├─ mind
├─ memory
├─ commitments
├─ notifications
├─ usage
├─ errors
└─ freshness
```

## Event Envelope

```text
event_id
sequence
event_type
occurred_at
received_at
priority
severity
dedupe_key
persistence
expires_at
resolved_by
affected_servers
affected_capabilities
task_id
approval_id
safe_title
safe_message
visual_hint
payload
```

Clientが文字列からFractureやRecoveryを推測するのではなく、バックエンドが安全な`visual_hint`を渡します。

---

# 12. 映画的表現の追加

## Cinematic Focus Choreography

重要イベント時に、

1. 通常パネルが薄くなる
2. 球体が少し奥へ移動
3. 関係Server Arcが正面へ回転
4. Overlayが奥から前へ出る
5. 周囲のTelemetryが対象情報へ切り替わる

という一連の演出を行います。

ただし急激なZoomではなく、450～800msの連続遷移にします。

## Glass Refraction Overlay

Overlayの縁だけに、

* 背景屈折
* Chromatic aberration
* Fresnel edge
* 微細なNoise
* Light sweep

を使用します。

本文背景は十分な不透明度を保ちます。

## Edge Intelligence

画面外周を情報領域として使います。

* 上：Core／接続／時刻
* 左：現在タスク
* 右：Attention
* 下：Mission／Servers
* 四隅：重大度と対象領域

中央は球体とTakeoverのために空けます。

## Environmental Response

画面背景も状態に連動させます。

| 状態        | 背景             |
| --------- | -------------- |
| Idle      | 静かな暗青          |
| Observing | 微かな走査線         |
| Planning  | Violetの内部経路    |
| Executing | CyanのData Flow |
| Approval  | Amberの停止フィールド  |
| Critical  | 外周のみRed        |
| Recovery  | Greenの一時波      |
| Offline   | 色を失い静止         |
| Privacy   | ほぼ黒＋一般状態だけ     |

---

# 13. 実装順序

## Phase 0：全UI情報監査

* Runtime Manager一覧
* API一覧
* Overview field一覧
* Dashboard利用一覧
* Display利用一覧
* Android利用一覧
* 未表示field一覧
* 重複表示一覧
* Raw JSON表示一覧
* Legacy依存一覧

成果物：

`docs/ui-information-coverage.md`

## Phase 1：Display Director

* Priority model
* Notification queue
* Dedupe
* Preemption
* Persistent state
* Resolution
* Overlay lifecycle
* Offline／Privacy
* Connection state

## Phase 2：Display Compositor

* 8レイヤー構成
* Absolute positioning
* Portal roots
* Z-level tokens
* Backdrop dim
* Focus choreography
* No input
* No tab stops

## Phase 3：一画面固定

* `100dvh`
* `overflow: clip`
* Height budget
* Compact／Standard／Cinematic density
* Text clamp
* Content overflow strategy
* Core legend統合
* 1366×768対応

## Phase 4：Overview v3

* Task list
* Presentation model
* Connection state
* Event ID／sequence
* Replay cursor
* Visual hint
* Situation
* Errors
* Capability state
* Correct health and freshness

## Phase 5：Dashboard網羅性

* Work
* Approvals
* Systems
* Mind
* Memory
* Activity
* Notifications
* Settings
* Usage
* Situation

## Phase 6：映画的仕上げ

* Reactive glass
* Camera choreography
* Overlay refraction
* Ambient scan
* Edge HUD
* Recovery reconstruction
* Critical scene
* Optional sound cues

---

# 14. 完了条件

## 専用Display

* 1366×768、1920×1080、2560×1440ですべて一画面
* `scrollHeight === clientHeight`
* スクロールバーなし
* Button、Input、Link、Tab stopなし
* 全画面の各Layerが独立
* P0、P1、P2、P3通知が異なる表示になる
* Criticalが中央を覆う
* Approvalが中央へ優先表示される
* 解決まで重要通知が消えない
* 同一通知がHeartbeatごとに再表示されない
* Offline時にLive表示が消える
* Stale Snapshotと明示する
* Privacy modeで個人情報を隠す
* SSE再接続後に欠落イベントをReplay
* 72時間動作でCanvasやEventが蓄積し続けない

## Dashboard

* Overviewの全fieldについて表示先が定義されている
* Raw JSONはDeveloper表示以外で使用しない
* Active以外のTaskも確認できる
* Approval履歴を確認できる
* Audit／Event／Errorが再読み込み後も残る
* Settingsを実際に変更できる
* ServerとCapabilityの依存関係を確認できる
* UsageとBudgetを確認できる
* User situationとCommitmentを確認できる

## テスト

* Priority preemption test
* Overlay lifecycle test
* Notification dedupe test
* SSE reconnect test
* Event replay test
* Offline／Stale test
* Privacy test
* Viewport no-scroll test
* No-focusable-element test
* Visual regression test
* Reduced-motion test
* Schema coverage test
* Manager→API→UI coverage test

WindowsのAssigned Accessでは、単一アプリまたはEdgeを全画面で起動し、閉じられた場合に自動再起動するキオスク構成が用意されています。AEGIS Displayもブラウザ表示だけでなく、このOS側の全画面・自動復旧まで完了条件に含めます。
