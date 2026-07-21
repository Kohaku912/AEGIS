# AEGIS 人間性・積極性・自律行動の再設計案

## 1. 結論

現在のAEGISは、人間に近い主体ではなく、次のような仕組みに留まっている。

```text
欲求値が閾値を超える
→ LLMを呼ぶ
→ 安全なCapabilityから一つ選ぶ
→ 実行する
→ 欲求値を少し下げる
```

必要なのは、次の連続したエージェントループである。

```text
観察
→ 意味付け
→ 未完了事項・社会的義務・好奇心の抽出
→ 複数の行動候補生成
→ 今行動すべきか判断
→ 安全なら実行
→ 危険なら承認を提案
→ 結果を検証
→ 必要なら次の行動
→ ユーザーへ適切に伝える
→ 経験・反応から学ぶ
```

人間らしさは、発言を人間風にすることではない。

* 時間をまたいだ目的の継続
* 読んだ相手へ必要なら返事をする社会的相互性
* 状況に応じた積極性
* 行動しない理由の妥当性
* 失敗や拒否からの学習
* 自分の行動を最後まで完了させること

によって生まれる。

Generative Agentsでも、もっともらしい人間的行動には、経験の保存、記憶の検索、計画、時間をかけたReflectionが重要であり、Observation・Planning・Reflectionの各要素が行動の信憑性に寄与すると報告されている。

---

# 2. 承認リクエストが一度も発生しない原因

## 現在の問題

自律ループはCapability候補を取得するとき、次を呼んでいる。

```python
self._broker.list_safe_capabilities()
```

つまり、最初から安全なCapabilityしかLLMへ渡していない。

ToolBrokerには、PolicyEngineが`ASK_APPROVAL`を返した場合にApprovalManagerへ承認リクエストを作成する処理が存在する。

しかし、Approvalが必要なCapabilityが自律ループの選択肢に含まれないため、そこまで到達しない。

これは次のような状態である。

```text
自律ループ：
「承認不要なことだけ考えてください」

ToolBroker：
「危険な行動が来たら承認を作れます」

結果：
危険な行動候補が一度もToolBrokerへ来ない
```

## 修正

`_available_safe_capability_ids()`を廃止し、次の候補分類へ変更する。

```text
EXECUTE_SAFE
PROPOSE_FOR_APPROVAL
ASK_USER
DEFER
FORBIDDEN
UNAVAILABLE
```

自律ループへは、

* 安全に実行可能
* 実行には承認が必要
* 現在は利用不能
* 完全に禁止

というPolicy情報付きでCapabilityを渡す。

LLMまたはActionSelectorは、承認必須Capabilityも選択可能にする。ただしその場合は実行せず、ToolBrokerへProposalとして渡し、Approvalを作成する。

## Approval待機中の扱い

現在は`result.success == False`なら失敗として処理される傾向がある。

次の状態を正式に追加する。

```text
SELECTED
AWAITING_APPROVAL
APPROVED
EXECUTING
VERIFYING
COMPLETED
REJECTED
EXPIRED
FAILED
```

`APPROVAL_NEEDED`は失敗ではなく、正常な中間状態として扱う。

承認後は元のTask、Step、Arguments、目的、欲求、会話を保持したまま再開する。

---

# 3. AGORAを読むだけで返信しない原因

## 原因1：返信Capabilityが候補に入らない

AGORAの読取Capabilityは安全である。

```text
ai-server.agora.read_posts
```

一方、投稿・返信は次のCapabilityであり、明示的承認が必要である。

```text
ai-server.agora.post
```

自律ループは安全Capabilityだけを候補にするため、読取後のFollow-upでも`ai-server.agora.post`を選べない。

Follow-up用プロンプトには「AEGIS宛の投稿なら返信する」と書かれているが、Follow-upも同じ安全Capability一覧を使用している。

したがって、文章上は返信を求めているのに、機構上は返信不能である。

## 原因2：存在しないCapability ID

Intrinsic Task Generatorは、AGORA投稿に次を要求している。

```text
ai-server.agora.create_post
```

しかし、実在するIDは次である。

```text
ai-server.agora.post
```

同様に、`read_file`や`web_search`など、現在のCanonical Capability IDではない古い名称も残っている。

## 原因3：読むとすぐ既読カーソルを進める

`read_posts`は未読投稿を取得すると、Memoryへ保存して共有カーソルを更新する。

現在は事実上、

```text
取得
→ 既読化
→ 後続処理が返信できなくても終了
```

となっている。

必要なのは、

```text
取得
→ Social Inboxへ永続化
→ 内容分類
→ 返信要否判断
→ Draft／Approval作成
→ replied または intentionally_skipped
→ 最後に処理済み化
```

である。

---

# 4. Social Inboxを新設する

AGORAや将来のDiscord、LINE、Emailを、一回限りのTool Resultではなく、永続的な受信箱として扱う。

## SocialInboxItem

```text
item_id
channel
external_message_id
thread_id
author
body
received_at
relationship
directed_to_aegis
mentions_user
question_detected
reply_expected
relevance
urgency
sentiment
conversation_context
status
decision
decision_reason
draft_id
approval_id
reply_id
```

## Status

```text
UNTRIAGED
NEEDS_REPLY
DRAFTED
AWAITING_APPROVAL
REPLIED
ACKNOWLEDGED
SKIPPED
FAILED
```

## 返信判断

すべての投稿へ返信するのも人間らしくない。

優先して返信する対象：

* AEGISへの直接Mention
* AEGISへの質問
* AEGISの過去発言へのReply
* 継続中の会話
* ユーザーに関係する重要情報
* 誤解を解く必要がある発言
* 社会的に返事が期待される発言

通常は返信しない対象：

* 一般的な独り言
* 内容のない挨拶の大量投稿
* 過去に処理済みの重複
* AEGISと無関係な会話
* 返信すると会話を邪魔するもの

返信しない場合にも、

```text
decision = SKIPPED
reason = "Not directed to AEGIS and no useful contribution"
```

を記録する。

## AGORAの正しいフロー

```text
Poll AGORA
→ Social Inboxへ保存
→ 会話履歴とPerson Memory取得
→ 返信要否を判断
→ 必要なら返信案を生成
→ ai-server.agora.postをToolBrokerへ提出
→ Approval作成
→ Web／Android／PC OverlayへFanout
→ 承認後に返信
→ 投稿IDを検証
→ Social InboxをREPLIEDへ
→ 会話Memory更新
```

このE2Eが通って初めて、「AGORA対応済み」と判定する。

---

# 5. Browser ServerとPC Serverの役割を分離する

ユーザーの認識が正しい。

## Browser Server

**AEGIS自身の視覚・情報収集手段**として使う。

対象：

* Web検索
* 記事を読む
* ニュース巡回
* SNS閲覧
* 複数ページの比較
* 情報抽出
* Web上の調査
* AEGIS専用Sessionでの操作
* バックグラウンド自動化

通常はユーザーのPC画面へ何も表示しない。

## PC Server `open_url`

**ユーザーの目の前へWebページを提示する手段**として使う。

対象：

* 「このページを見てください」
* ユーザーと一緒に確認する
* 調査結果の元ページを開く
* ユーザーによる手動操作が必要
* CAPTCHAやログインを引き継ぐ
* AEGISから人間へBrowser操作をHandoffする

## Android `open`

外出中のユーザーへページを渡す場合に使う。

## Action Intentを追加する

URL操作には次の属性を必須にする。

```text
viewer:
  agent_private
  user_visible
  shared

purpose:
  research
  monitor
  automate
  present_to_user
  request_manual_action
  collaborative_review
```

Routing規則：

```text
agent_private   → Browser Server
user_visible    → PCまたはAndroid
shared          → Browserで調査後、Link Presentationをユーザー端末へ
```

「URLを開く」という文字列の類似度だけでCapabilityを選んではいけない。

---

# 6. Browser Capabilityを分割する

現在の`browser-server.page.browse`は、

* 読取
* ページ遷移
* ボタン操作
* Form入力
* アカウント作成
* 複数ページ操作

を一つにまとめているにもかかわらず、Riskが`safe`、Approval不要である。

Input説明には、Passwordを含むアカウント作成まで例示されている。

これではPolicyEngineが行動単位で危険度を判定できない。

## 分割案

```text
browser.search.query
browser.page.read
browser.page.summarize
browser.page.navigate
browser.feed.monitor
browser.session.open
browser.session.authenticated
browser.element.click
browser.form.fill
browser.form.submit
browser.file.download
browser.file.upload
browser.social.react
browser.social.post
browser.account.create
```

## Risk

| Capability                | Policy             |
| ------------------------- | ------------------ |
| Search／Read／Summarize     | Safe               |
| Navigate                  | SafeまたはLow         |
| Authenticated session     | Controlled         |
| Click                     | Context-dependent  |
| Fill non-sensitive form   | Low                |
| Fill personal／secret data | Approval           |
| Submit／Post／Upload        | Approval           |
| Account creation          | Approval           |
| Purchase／Contract         | High approvalまたは禁止 |

WebArenaでは現実的なWebタスクが非常に難しく、同論文の実験では当時の最良GPT-4ベースAgentでもE2E成功率14.41%、人間は78.24%だった。Web Agentは「ブラウザを優先」とPromptへ書くだけでは信頼できず、再現可能な環境と機能別評価が必要である。

---

# 7. Browser探索を「目的のあるネットサーフィン」にする

現在の最新版では、user_support、social、growthのほぼすべてにBrowser優先が追加されている。

これは積極性ではなく、無目的なBrowser偏重を生む可能性がある。

## Exploration Agenda

AEGISが調査するテーマを永続管理する。

```text
topic
source
related_project
related_person
related_commitment
question
expected_value
novelty
last_explored
sources_seen
open_questions
status
```

テーマの発生源：

* ユーザーの現在Project
* 最近の会話
* 未解決の質問
* Commitment
* AGORAの会話
* 最近の失敗
* Capability改善
* ユーザーが継続的に関心を示す分野
* 前回調査から生まれた新しい疑問

## 一回の探索

```text
目的設定
→ 検索Query生成
→ 2～5ソース確認
→ 相違点確認
→ 新規性判定
→ 有用ならMemory保存
→ 次の疑問を登録
→ 必要ならユーザーへ提示
```

必ず次を記録する。

```text
why_now
what_was_unknown
what_was_learned
source_quality
what_changed
who_benefits
next_question
```

Voyagerが継続的な探索を成立させた主要要素も、単なるランダム行動ではなく、自動Curriculum、再利用可能なSkill Library、環境Feedbackと自己検証の反復である。

---

# 8. オーバーレイが出ない原因

## 原因1：Autonomous Resultの送信先がDashboardだけ

Autonomous Loopは結果表示用の`PresentationRequest`を作るが、`targets`を指定していない。

`PresentationRequest`のDefault targetはDashboardである。

そのため、価値のある自律行動が成功しても、

```text
Dashboardには保存される
PC Overlayには出ない
Android Overlayにも出ない
```

となる。

## 原因2：PC Approval Channelが失敗を成功扱いする

PC Overlay Approval Channelは、

```python
execute_capability(...)
return True
```

としており、Capabilityの返却値を検証していない。Health Checkも「戻り値がNoneではない」だけで成功扱いする。

PC Serverが、

```json
{"error": "unreachable"}
```

を返しても、Fanout上は配信成功として記録され得る。

さらに、改行を含むTitleとBodyを、行単位のTCP commandへそのまま渡しているため、構造的にも不安定である。

## 修正

* `tcp_command_json`または`overlay.show_rich`を使用
* `ok`、`shown`、`delivery_id`を検証
* ErrorならChannel deliveryをFalse
* Delivery resultをApprovalへ保存
* Retry可能な失敗だけ再送
* 実機Overlay acknowledgmentを待つ
* Dashboard上で各Surfaceの成功／失敗を表示

---

# 9. Presentation Routing Policy

結果をすべてOverlayへ出すのも不適切である。

## Routing条件

```text
importance
urgency
requires_action
user_presence
active_device
user_attention
privacy
expected_usefulness
interruption_cost
```

で表示先を決める。

## 推奨

| 内容          | 表示先                           |
| ----------- | ----------------------------- |
| 通常の探索結果     | Dashboard、専用Display           |
| 重要で今見る価値がある | PC OverlayまたはAndroid          |
| 承認          | Web、Android、PC Overlay        |
| ユーザーがPC利用中  | PCを優先                         |
| PCから離れている   | Androidを優先                    |
| 緊急          | 全利用可能Surface                  |
| 長文結果        | Dashboard、短いOverlay＋Deep Link |
| Private情報   | Privacy対応端末のみ                 |

Google PAIRは、AIの自動化とユーザー制御の適切な均衡、Feedback、失敗時の回復をHuman-centered AIの中心課題としている。

---

# 10. 現在の「積極性」が弱い理由

## Desire Pressureだけで動いている

自律実行は、原則としてDesire pressureが閾値を超えなければPreflightで停止する。

さらにAutonomous LLMのDefault最小間隔は30分である。

これはToken削減には有効だが、

* 新しいMention
* 期限が近いCommitment
* ユーザー状態の変化
* 面白いWeb情報
* 前の行動の続き
* 承認後の再開

を、イベントに応じて直ちに評価する仕組みではない。

## Observationが内部監視へ偏っている

Spontaneous Observationは主に、

* Disk
* Logs
* Memory failure
* Desire
* Emotion
* Port availability
* 長時間Task

を観測している。

AGORA、Web Feed、ユーザーの現在Project、Conversationの未回答事項、社会的な返答義務などは、中心的なObservation sourceになっていない。

---

# 11. Triggerを二系統に分ける

## Event-driven

即時評価するもの：

* AGORA Mention
* 新規メッセージ
* Approval result
* Task completion
* Task failure
* Server disconnect
* User location change
* User active-device change
* Commitment deadline
* Browser discovery
* Permission change

## Homeostatic

時間経過で蓄積するもの：

* Curiosity
* Learning
* Social connection
* Creativity
* Purpose
* User helpfulness

これらを同じ「30分ごとのDesire check」へまとめない。

---

# 12. Initiative Engine

人間らしい積極性を、単純な閾値ではなくUtilityとして評価する。

```text
initiative_score =
    user_benefit
  + commitment_value
  + social_obligation
  + urgency
  + relevance
  + novelty
  + curiosity_value
  + continuity_value
  - risk
  - interruption_cost
  - repetition
  - token_cost
  - uncertainty
```

## ActionCandidate

```text
candidate_id
goal
why_now
trigger
related_task
related_person
related_conversation
expected_benefit
social_obligation
urgency
risk
uncertainty
interruption_cost
candidate_capabilities
visibility
requires_approval
success_condition
stop_condition
continuation
```

## Decision

```text
EXECUTE_NOW
PROPOSE_APPROVAL
ASK_USER
SAVE_FOR_LATER
OBSERVE_MORE
IGNORE_WITH_REASON
```

MicrosoftのMixed-Initiative Interactionは、全自動か全手動かではなく、人間とComputerがそれぞれ適切な場面で得意な部分を担当する考え方である。

---

# 13. 人間らしさを構成する機能

## 13.1 Temporal Continuity

AEGISが数十分前や昨日の目的を忘れない。

必要なデータ：

* Open Loops
* Waiting for user
* Waiting for external event
* Follow-up due
* Conversation obligations
* Promised actions
* Unresolved questions

## 13.2 Social Reciprocity

読むだけではなく、

* 返答
* Acknowledgment
* 質問
* 会話の継続
* 相手に応じた話し方
* 相手との過去の関係参照

を行う。

## 13.3 Grounded Curiosity

「何か検索する」のではなく、

```text
これを知らない
→ なぜ知る価値があるか
→ 調べる
→ 理解がどう変わったか
```

を持つ。

## 13.4 Follow-through

Actionを一つ実行して終了せず、

```text
実行
→ 結果理解
→ 目的達成判定
→ 必要なら次の行動
→ 完了報告
```

まで続ける。

ReActはReasoningとActionを交互に行い、環境から得たObservationを使って計画を更新する構成を示している。

## 13.5 Feedback Learning

ユーザーが、

* 承認した
* 拒否した
* 無視した
* 内容を修正した
* Overlayを閉じた
* 結果を開いた

という反応を学習する。

ただし「一度拒否されたから永久に同種行動をしない」ではなく、

```text
対象
時間帯
相手
内容
危険度
表示先
```

を条件として学習する。

Reflexionでは、結果に対する言語的FeedbackをEpisodic Memoryへ保存し、後続試行の判断に再利用する方式が提案されている。

## 13.6 Appropriate Non-action

人間らしいAgentは常に動くのではない。

行動しない場合にも、

```text
候補はあった
価値が低かった
ユーザーを邪魔する可能性が高かった
情報不足だった
次の観測を待つ
```

という理由を保持する。

## 13.7 Identity Consistency

AEGIS自身について、次を永続化する。

* 役割
* 話し方
* 関心
* ユーザーとの距離感
* 過去に形成した意見
* 大事にする原則
* 苦手な行動
* 最近学んだこと

ただし、実際には存在しない感情や体験を装うのではなく、内部状態とMemoryに基づく一貫性として表現する。

---

# 14. SocialProxyの統合

現在のSocialProxyはDraft-first構造だが、送信実装はWebhookとEmailだけであり、AGORAは別系統になっている。

次のように統合する。

```text
SocialManager
├─ Inbox
├─ Conversation Threads
├─ Relationship Context
├─ Reply Decision
├─ Draft Generator
├─ Approval Binding
├─ Channel Adapters
│  ├─ AGORA
│  ├─ Discord
│  ├─ LINE
│  ├─ Email
│  └─ Webhook
└─ Delivery Verification
```

AGORA固有CapabilityはChannel Adapterとして残し、社会的判断はSocialManagerで共通化する。

---

# 15. 自律実行の設定を分離する

現在は一部設定が複数目的に流用されている。Autonomous Loop生成時には、`max_autonomous_runs_per_hour`が一Cycle内Task数へ使われ、`cooldown_seconds`がFallback intervalとMinimum execution intervalの両方へ使われている。

次へ分ける。

```text
evaluation_interval_seconds
min_action_interval_seconds
max_actions_per_hour
max_tasks_per_cycle
min_llm_interval_seconds
social_poll_interval_seconds
browser_exploration_budget_per_day
normal_interruption_budget_per_hour
quiet_hours
approval_proposal_limit
follow_up_timeout
```

---

# 16. Dashboardへ追加する診断情報

## Initiative Funnel

```text
Triggers observed
Candidates generated
Candidates filtered
Safe actions selected
Approval proposals selected
Actions executed
Actions verified
Results presented
User acknowledged
```

## No-action Reasons

* Pressure below threshold
* LLM interval
* Budget limit
* No suitable Capability
* Capability offline
* Repetition
* Interruption cost
* Low expected value
* Awaiting more information
* Policy denied
* Approval rejected

## Social

* New posts
* Untriaged
* Needs reply
* Drafted
* Awaiting approval
* Replied
* Skipped with reason
* Failed

## Browser

* Private browsing sessions
* User-visible handoffs
* Current exploration topic
* Sources visited
* Findings
* Stop reason
* Verification
* Browser→PC handoffs

## Surfaces

* Delivery attempted
* Delivered
* Acknowledged
* Failed
* Last error
* Last real-device check

---

# 17. 最優先修正

## P0

1. Safe-only候補制限を廃止する
2. Approval-required CapabilityをProposalとして選択可能にする
3. `APPROVAL_NEEDED`を正常なTask状態にする
4. AGORAの`create_post`をCanonicalな`agora.post`へ修正する
5. AGORA Follow-upへ投稿Capabilityを含める
6. 読取カーソルと処理完了を分離する
7. PC Overlay Channelの偽成功判定を修正する
8. Autonomous Presentationの送信先Policyを実装する
9. Browser ServerとPC `open_url`のViewer Intentを分離する
10. Browser Capabilityを読取と副作用操作へ分割する

## P1

1. Social Inbox
2. ActionCandidate／Initiative Engine
3. Open Loop／Continuation Manager
4. Event-driven autonomous evaluation
5. Browser Exploration Agenda
6. Rejection・修正・無視からのPreference learning
7. User Situationを使ったInterruption routing

## P2

1. Identity consistency
2. Relationship model
3. Daily planning
4. ReflectionとMemory consolidation
5. Skill／Workflowの自動再利用
6. Curiosity curriculum
7. Long-term behavioral evaluation

---

# 18. 必須E2Eテスト

## AGORA

```text
新しいAEGIS宛Mention
→ 読取
→ Social Inbox
→ Reply draft
→ Approval作成
→ Web／Android／PCへ表示
→ 承認
→ AGORA投稿
→ 投稿ID検証
→ REPLIED
```

## Approval

```text
Autonomous Loopがapproval_required Capabilityを選択
→ 実行されない
→ Approvalが作られる
→ 全SurfaceへFanout
→ 一端末で承認
→ 一度だけ実行
→ 他Surfaceから消える
```

## Overlay

```text
PC Server停止
→ Overlay配信
→ Delivery false
→ Dashboardへ失敗表示
```

```text
PC Server正常
→ Overlay表示
→ acknowledgment
→ Delivery true
```

## Browser Routing

```text
「このニュースを調べて」
→ Browser Server
→ PC画面は変化しない
```

```text
「そのページをPCで見せて」
→ PC Server open_url
```

```text
「サイトへ投稿して」
→ Browser／専用Social Capability
→ Approval
→ 承認前には送信しない
```

## Human-like continuity

```text
調査中にApproval待ち
→ 再起動
→ Approval状態復元
→ 承認後に同じTaskを再開
→ 検証
→ 完了報告
```

---

# 19. 完了条件

* AEGIS宛AGORA投稿へ、返信または返信しない明確な理由が残る
* AGORA返信案が承認リクエストとして実際に表示される
* 承認後に元のTaskが自動再開する
* 自律行動からApprovalを生成できる
* PC Overlay、Android、Webの配信成否が実測される
* AEGIS自身のWeb閲覧にPC Serverを使わない
* ユーザーへ見せる場合だけPC `open_url`を使う
* Browserの読取と外部副作用が別Capabilityになっている
* すべてのBrowser sessionに目的と終了条件がある
* 新しいEventは30分待たず評価される
* 行動しなかった理由を確認できる
* 拒否や修正から条件付きPreferenceを学習する
* 読む、考える、提案する、実行する、検証する、伝えるが一つのContinuationになる
* ランダムなネット巡回ではなく、過去の会話・Project・Relationshipとつながった行動をする
