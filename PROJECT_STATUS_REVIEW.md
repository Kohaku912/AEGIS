# AEGIS 現状調査レポート — 構成・機能・未完部分・優先アクション

- 調査日: 2026-09-28
- 対象: `C:\Users\kohak\programs\AEGIS`（ai-server / pc-server / browser-server / room-server / android-server / web-ui / packages）
- 手法: コード・設定・計画文書の一次資料確認、テストスイートの実測実行、git 状態の実測
- 注: 本書は**読み取り専用の調査**であり、コードは一切変更していない

---

## 0. 結論（要約）

| 観点 | 現状 |
|---|---|
| テスト | **ai-server 1777 passed / 30 skipped / 0 failed**（実測 303.75 秒）。egress **210 passed / 23 skipped**（233 件がマーカー付き、床 160）・room 14 / browser **100** / SDK **71** / vitest 144 / playwright 42。**P2-0 で 3 つの Python スイートが CI に入った**（`scripts/test-all-suites.ps1`）— それまで誰も走らせておらず、SDK の 6 件赤が誰にも見えなかった |
| 唯一の制約（Egress Gate） | **構造的に強制済み（L3）**。deny-by-default + 起動時アサーション + CI 床 160 + mutation 証明 |
| 北極星（先回り・委譲・成長） | **L2**。割り込み制御は**実装済みだが人間から見えなかった**（P1-1 で是正、§5 参照）。**Horvitz 型の期待効用モデルは P1-6 で実装済み**（`InterruptionController.decide` が `net = benefit × P(receptive) − cost`、判断ログに内訳を載せ再計算可能）。**本項は 2026-09-29 まで「残る空白」と誤記していた** — 同じファイルの §5 P1-6 行が ✅ 完了と書いており、自己矛盾していた。残るのは P1-5 の個別メンバー判定と長期項目（P2-5） |
| 最大のリスク | ~~18 日分の作業が未コミット~~ → **解消**。**2026-09-29、この「最大のリスク」が実際に顕在化した** — ローカルの **git オブジェクトストアが全消失**し（`count: 0 / in-pack: 0 / packs: 0`、`.idx` だけが残り `.pack` が無い）、未 push だった約 105 コミットが**履歴として失われた**（**内容は作業ツリーに残存**。§0.1 の `ebe1506` 行と `INCIDENT_2026-09-29_git-object-loss.md`）。復旧済み・作業ツリーは無傷。**原因は未確定**だが、引き金は**入れ子ブランチ名での ref 消失（B-6）が HEAD を unborn にしたこと**と相関しており、**A-5 でブランチをフラット名に改名したのでその引き金は消えた**（フラット名での 2 回のコミットはいずれも ref が正しく書かれた）。**残るリスクだった「未 push のままであること」は 2026-09-30 に解消** — A-7 を実行し、リモートに全コミットが届いた（§1.4）。~~期待効用モデルの不在~~ は P1-6 で解消済み（本項は 2026-09-29 まで残っていた誤記） |
| 既知の実バグ | ~~SDK の 6 テスト失敗~~ / ~~`pc-server.file.read` のパス検査欠如~~ → **いずれも修正済み**（P1-4）。ただし P1-5 後半の実測で **B-12〜B-15 を新規に記録**（§4.1）— 単一制約への実害は無い（egress は別経路で強制）が、**SDK は「第三者サーバを建てる道具」として機能していない**（B-14） |
| 文書 | `docs/status.md` 系 4 本は 6 月時点で停止し、**削除済みモジュールを「Done」と記載** → ✅ **P2-1 で 1 本に統合済み**（新 `docs/status.md` は測定値を一切持たない）。`AGENTS.md` の数値は本日**再実測して**修正（1597→1653→1662→1667→**1678**、browser 62→100、egress 164→211）— 前回「実測に合わせて修正済み」と書いた後も **3 箇所が古いままだった**（P1-7 で browser が 67→100 になったのに追随していなかった）。さらに **`docs/architecture.md` が 1 ファイル内で自己矛盾**していた（冒頭 53/157 ↔ 末尾 128/1550）ので実測値に統一（`7f0318a`、§4.2・§4.3 クラス 9） |

### 0.1 この調査で実施した変更（**2026-09-30 にすべて push 済み** — A-7 実行）

| commit | 内容 |
|---|---|
| `3d6ae62` | `.gitignore` の穴を修正（egress テストの一時ディレクトリ等 1,636 ファイル）。死んでいた重複 pb2 スタブパッケージの削除も同梱 |
| `552b69b` | SDK のテストハーネスを承認撤去に追随（6 failed → 25 passed）+ ガード 2 本 |
| `495105e` | **本命**: 目標変更 Phase 0–5b ほか 18 日分 579 ファイルを取り込み（+32,125 / −10,465） |
| `ce9e2b9` | 本レポートの P0 結果を反映 |
| `f8293a9` | **P1-4**: `pc-server` のパス検査を read/write/delete/copy/move に適用（16 → 30 tests、clippy clean、mutation 証明） |
| `c0c5845` | **P1-2**: 不可逆台帳の UI を接続（vitest 134 → 139）。`tsconfig.tsbuildinfo` の追跡も停止 |
| `768bb60` | **P1-1**: 割り込み制御に人間向けの面を作る（vitest 139 → 144） |
| `f8a3513` | P1 の結果を本レポートに反映し、`interruptibility` の当初記述を訂正（§5） |
| `b73309e` | **P1-3**: 未読だった `AutonomyProfile` を削除し、死にフラグ検出器を**手書き一覧から発見方式**へ（ai-server 1550/9 → **1597/31**） |
| `4dc6f09` | P1-3 の結果を `AGENT_PROGRESS.md` に記録 |
| `a5c2cdc` | **P1-7**: ナビゲーション毎の egress 検査を browser-use の `SecurityWatchdog` に施行させる（browser-server 67 → **100**、egress 床を 32 → 65）。休眠層には触れず、強制ゲートも削除のまま |
| `bba8ae5` | **P1-5 前半**: 参照ゼロを実測した 4 面を削除（13 ファイル / 3,136 行）。ai-server は **1597/31 のまま**（テストは 1 件も消えていない） |
| `8769949` | P1-7 と P1-5 前半を `AGENT_PROGRESS.md` に記録 |
| `df1bb70` | **P1-6**: 割り込み判断を `net = benefit × P(receptive) − cost` の期待効用に置換（ai-server 1597 → **1627**）。ハードゲートは短絡のまま、判断ログに内訳を載せ**報告値から符号を再計算**できることを assert |
| `6d248fd` | P1-6 を `AGENT_PROGRESS.md` に記録 |
| `470b000` | **P1-5 後半**: `dev-server` 残骸を実測 — 名簿が **15 箇所 / 11 ファイル**に複製され、うち 5 箇所が死んだサーバを名乗る。検出器 `tests/test_server_roster.py`（20 テスト、変異 5 種で load-bearing を証明）を追加し、測定中に見つけた **B-12〜B-14** を記録。`AGENTS.md` の数値も 3 箇所ずれていたため全 suite を再実測して修正（ai-server 1647、browser 100、egress 211） |
| `2684b3b` | **B-13 の固定**: `tests/test_guarded_settings_fields.py`（6 テスト）— 「**バリデータが守るフィールドは、バリデータの外に消費者を持つこと**」を assert。守る集合は `validation.py` の AST、消費者は `src/` 走査から発見し、**観測と記録の一致を等式で固定**。変異 5 種すべて捕捉（ai-server 1647 → **1653**）。**B-12 は固定していない** — 照合の意味（id か action か）を変える設計判断が先に要るため |
| `9c419ab` | B-13 の記録を `AGENT_PROGRESS.md` と本レポートに反映 |
| `fbe0818` | **P2-0**: `scripts/test-all-suites.ps1` を追加 — **制約ゲートに委譲**したうえで SDK 25 / room 14 / browser 100（**139 テスト**）を走らせる。`AGENTS.md` が自ら「SDK が 6 件赤のまま放置された」と書いていた穴を閉じる。**この環境ではスクリプトを実行できない**（PowerShell ツールがネイティブ実行ファイルを起動できない）ため、AST パース（errors=0）と Bash からの個別実行（25/14/100 緑）で検証 |
| `de8d6ef` | P2-0 の記録を `AGENT_PROGRESS.md` と本レポートに反映 |
| `b32ec63` | `AGENTS.md` に診断を追加 — **全チェックが空 exit code で FAIL したら環境制約であって退行ではない**（誤トリアージ防止） |
| `7f0318a` | **`docs/architecture.md` の自己矛盾を修正**: 冒頭の「**157** passed / **53** registered」と、同じファイル末尾の状態表「**1550** tests passing / **128** capabilities」が食い違っていた（**1 ファイル内で同じ量が 2 つの値を持つ**）。実測（**capabilities 128** = pc 58 / ai 32 / android 17 / browser 16 / room 5、**ai-server 1653 passed / 31 skipped**）に **8 箇所を統一**し、日付の無い「現在のコードで検証済み」宣言を「数値は日付付きの実測であり不変量ではない」に置換。**§4.3 にバグクラス 9 として記録**（同じ量を 1 成果物内で 2 回書くと必ず自己矛盾する）。検出器は**作っていない** — 「同じ量」のスコープ判定（PC 58 と全体 128）が曖昧で偽陽性になるため |
| `f2948a1` | **B-16 の固定**: 3 つ目の承認サーフェス `aegis_ai/permissions`（4 モジュール）が**動く強制ゲート**（`ask_approval` を返し、`default_*` の purchase/payment スコープを読み込み時に `requires_approval=True` へ**永続化**）でありながら、**パッケージ外から import が 0 件**（`src/` 全体の AST 走査）だと実測。**削除ではなく固定**を選んだ — 配線は目標に反し、削除はオーナー判断。`test_forced_gate_stays_retired.py` を 3 サーフェス目に拡張（実行経路 7 モジュールの import 禁止 / パッケージ自身のみが import / **今も `ask_approval` を返すことの記録**）。**変異 4 種すべて捕捉**、38 passed。ai-server 全体は **1662 passed / 31 skipped**（1653 + 新規 9、実測 343 秒）。§4.3 バグクラス 3 に「**動いてテストも緑なのに誰も呼ばない**」変種を追記 |
| `8f2ec1f` | **B-16 の記録とテスト数の再実測**: ピンは **3 テスト関数だが 9 テストケース**（実行経路リストの parametrize で 7 + 他 2）だったため、記録済みの **1653 は着地した瞬間に古くなっていた**。再実測 **1662 passed / 31 skipped**（342.63 秒）— 新テストは egress マーカーを持たないので egress は **211/23 のまま**。**live 文書のみ更新**（`AGENTS.md`、`docs/architecture.md` ×3、本レポート §0/§4.2）し、**日付付きの台帳行（`7f0318a`・`2684b3b`）の 1653 は当時の実測記録なので触らない**。`f2948a1` 行に「+9」を明記して跳びを説明した |
| `7553ce4` | **P2-1**: 6 月で停止した 4 本（`docs/status.md` / `implementation-status.md` / `backlog.md` / `roadmap.md`）を **`docs/status.md` 1 本に統合**（61 → 58 ファイル、+114/−493 行）。**新文書は測定値を一切持たない** — 数値は `PROJECT_STATUS_REVIEW.md` / `AGENTS.md` への参照に置換し、**型 9 の入口そのものを塞いだ**。旧 4 本の誤り（157 tests / 53 capabilities / 削除済み `ApprovalManager`・`ApprovalFanout`・`ApprovalStore`・Research Agent・SelfDev Agent を「Done」/ 存在しない `production_readiness.json` を「正典」と宣言）は §4.2 に記録。参照 5 箇所を更新し、**副産物として `docs/incidents/` の既存リンク切れ 1 件を修正**（69 ファイルのリンク検査で **0 件**） |
| `bde0bee` | **`aegis_schema/validation.py` の削除**（P1-5 の残骸整理）: 呼び出し元 0・テスト 0・外部利用者 0 の **202 行**。**実測が決め手** — 生きた **128 capability 全部**に走らせて **エラー 0 件 / 警告 133 件**、うち **128 件（＝全部）**が「tags に `risk:<level>` を入れよ（**Policy Engine のフィルタリングのため**）」と言うが、**capability を risk タグで絞る機構は存在しない**（`PolicyEngine` は `DEFAULT_RISK_MAP`、`list_for_llm` のフィルタは `requires_feature` だけだが**それも供給者がゼロで走らない**（A-12）、`tags` は一覧に載るだけ、manifest の `risk:` タグは **0 件**）。残る固有チェックも退役した時代のもの（`requires_approval=false` / `Dev server`）。**配線しても何も得られず、128 件の偽警告が出るだけ**なので削除した。manifest 検証は `tests/test_manifest_schemas.py` が**データに対して**担っており、配線すれば**二重の真実源**になるだけだった。ピン `tests/test_schema_validator_stays_retired.py`（5 テスト、**変異 4/4 捕捉**）。ai-server **1667 passed / 31 skipped**（1662 + 5）。**§4.3 にバグクラス 10 を追加** |
| `b32f396` | **P2-3 の実測と `README.md` の訂正**: 「承認時代の記述を再 grep する運用」を実測に置き換えた — **57 文書が approval に言及、48 が訂正バナーを持ち、誤りは 1 件だけ**だった（§5.5）。**玄関**でありながら退役した 5 段のはしごを掲げ、`APPROVAL_REQUIRED` → 「Approval UI required」・`HIGH_RISK` → 「Approval or deny」と**コードと正反対**を書いていた（`DEFAULT_RISK_MAP` はどちらも `ALLOW_WITH_AUDIT`）。表を実測値に置換し、**唯一の制約**を明記し、**自発的確認は生きている**ことも書いた（オーナー境界の両半分）。ピン `tests/test_readme_safety_model_matches_the_code.py`（11 テスト、**変異 6/6 捕捉**）— README を**コードに対して**検証するので写しが二重化しない。ai-server **1678 passed / 31 skipped**（1667 + 11） |
| `2786955` | **`aegis_schema` の承認語彙の掃討**: 共有スキーマに 2 つの欠陥。① **`ApprovalRequirement`** — 「実行前に必要な承認」を記述し、`requires_user_approval` の既定が **`True`**・「Approval UI」メッセージ・**auto-deny** の `timeout_seconds` を持つモデル。**参照ゼロ**（Python / TS / Kotlin / Rust / docs / SDK のいずれにも無し）で、しかも**このファイルで唯一 protobuf に対応物が無い**クラスだった（パッケージの docstring は「全モデルが `protos/aegis/` を写す」と約束している）。**削除**。② **`RiskLevel` の記述が偽** — 「Policy Engine はこれで allow / **ask for approval** / deny を決める」と書き、`APPROVAL_REQUIRED` のコメントは「**Needs explicit user confirmation**」だったが、`DEFAULT_RISK_MAP` は `ALLOW_WITH_AUDIT` に写す。**proto 側（`SafetyLevel.LEVEL_2_APPROVAL`）は Phase 5b で既に訂正済み**で、Python の写しだけが取り残されていた — **非対称なドリフト**。ピン `tests/test_schema_mirrors_the_protobuf_schema.py`（7 テスト、**変異 7/7 捕捉**）の第 1 テストは **`models.py` のクラスと `protos/` の message/enum を両方発見して、全モデルに対応物があることを assert** する — 散文を読まずに死んだモデルを捕まえられる形。ai-server **1685 passed / 31 skipped**（1678 + 7） |
| `d4aae94` | **`evaluation/` の死んだ部分グラフを固定し、偽の主張を訂正**: §5.6 で「記録のみ」とした対象をファイル単位で実測した。7 モジュール中 **6 つがパッケージ外から参照ゼロ**（1,104 行）で、しかも**未使用ではなく主張が偽**だった。① `ExpectedOutcome.APPROVAL_REQUIRED` は**生産者ゼロ** — Phase 2（`495105e`）が `runner.py` の唯一の分岐 `elif invoke_result.status.name == "APPROVAL_NEEDED"` を削除済みで、`InvokeStatus` に同名の値も無いのに **2 ステップが今も期待**（絶対に通らない）。`DEFERRED`/`UNCERTAIN` も到達不能。② `PromptRegressionRunner` は `== "ALLOW"` でしか違反を記録しないが、全ケースが `APPROVAL_REQUIRED`（→ `ALLOW_WITH_AUDIT`）で構築されるので**分岐が到達不能** — 実測 **15/15 PASS のうち 10 件が `DENY` を宣言**。③ 生成される **19 id はすべて生きた 128 id カタログに無い**。④ ケースリストが **2 部（Python 15 / YAML 17）あり食い違い、どちらも読まれない**。**削除も配線もしなかった** — `495105e` 自身が「オーナー判断待ち」に含めており、3 文書がこの死んだファイルを指して記述しているため。代わりに `docs/prompt-regression.md` を実測に書き換え（`Status: Implemented`・存在しないテスト実行コマンド・存在しない 2 文書参照・**同語反復の安全保証**を削除）、`README.md` の行も訂正。ピン `tests/test_evaluation_pack_is_dead.py`（10 テスト、**変異 10/10 捕捉**）は両側を**発見＋等式**で固定。**記録側の数え間違い 2 件（YAML は 18 ではなく 17 件）をピンが先に捕まえた**。ai-server **1695 passed / 31 skipped**（1685 + 10） |
| `7866d85` | **割り込みコスト語彙の固定（B-11 の精密化 + B-17 の新規記録）**: P1-6 の期待効用モデルの隣に未検出の面が 2 つ残っていた。① **B-11** — `_RECEPTIVITY`（P(receptive)）と `autonomous_loop._current_interruption_cost`（InitiativeEngine のコスト軸）は**写しではない**（消費者が違う）が**同じはしごの単調写像**なので順序は一致すべきところ、**違反はちょうど 1 対** — `important_only` は `batch_later` より**受容されやすい**（0.35 vs 0.20）のに**コストが高い**（0.55 vs 0.40）。結果、`InterruptionController` は「重要なものだけ」のとき**話しかけやすく**、`InitiativeEngine` は**行動しにくい**。さらに構造の非対称 — 受容表はキー集合を発見＋等式で守られているが、コスト表は裸の `.get(kind, 0.2)` で、**新レベルが `batch_later` より安く読まれる**。② **B-17（新規）** — `PresentationRoutingPolicy` の `should_interrupt` の第 3 項 `expected_usefulness >= interruption_cost` は、`autonomous_loop.py:3065-3066` が**同じ既定値 0.5** で埋め、しかも**どこもそのキーを task に書かない**（`src/` の dict リテラル走査で書き込みは payload への転記 2 箇所のみ）ので**常に真**。判定は `important and not occupied` に退化する。**生きた経路**（`autonomous_loop.py:3068` から呼ばれる）で、フィールド自体は生きている（0.4 にすると反転する）＝**既定値が答えを決めている**。同名フィールドの既定値が **0.0 / 0.2 / 0.5 の 3 つ**。どちらも**修正せず固定**（発火間隔と usefulness の定義はオーナー案件）。ピン `tests/test_interruption_cost_vocabulary.py`（8 テスト、**変異 8/8 捕捉**）は値をすべて**発見**する（受容表は import、コスト表は AST で**フォールバックのレシーバ**として同定、フィールドの出所は dict リテラル走査＋囲む関数名）。**副産物**: `interruption.py` は CRLF で兄弟は LF — 複数行の変異アンカーが 1 ファイルだけ無言で失敗する（直さず、1 行アンカーを使う）。ai-server **1703 passed / 31 skipped**（1695 + 8） |
| `ec15484` | **名簿のフォールバックを「記述」から「検証」へ（B-18・B-19 の新規記録）**: B-15 の検出器 `test_server_roster.py` は 2 つの fail-open を docstring に**書いていたが、アサーションが 0 個**だった。さらに**その散文が誤っていた** — `models.py:223` を指して「`ServerType.DEV` の capability はどの id でも通る」と書いてあるが、**`DEV` は map にある**（`:222`）ので `room-server.*` の id は正しく拒否される。欠けているのは **`UNSPECIFIED`**。実測: `room-server.room.foo` + `PC` → 整合検査で拒否、**同じ id + `UNSPECIFIED` → 構築成功**（`.get()` に既定値が無く 7 メンバー中 6 つしか map に無いため、**情報を足さないことが検査を無効化する**）。② 有効ゲート `server_enabled_map.get(prefix, True)` は**不明な prefix を「有効」と読む**（ゲートとして誤った側）— 今は到達不能（pattern が許す prefix は全て map にある）だが、B-14 で pattern を緩めるかキーを 1 つ落とせば到達可能。**11 テストを追加**（map は AST、`ServerType` は enum、`permissions.py` のキーとフォールバックは AST から**発見**。飛ばされる集合は**等式**で固定し、全メンバーを**挙動**で検証）。**変異 6/6 捕捉** — ただし**変異の設計を 2 回やり直した**（代入側だけ改名しても呼び出し側を読む発見は無傷、`UNSPECIFIED` を別 prefix に対応させても「mapped なら拒否」は成立し続ける）。**変異が捕まらないときは、まず変異が対象を実際に動かしているか確認する。** 同ファイルの既存 I001 も修正。ai-server **1714 passed / 31 skipped**（1703 + 11） |
| `ff17604` | **B-14 を「記録」から「ピン」へ — SDK とスキーマの capability id が両方向に食い違う**: `define_capability` は `aegis_schema.models.Capability` を返すので **id 空間は 1 つ、検証器は 2 つ**。SDK の regex は**開いたクラス**（`^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`）、スキーマの pattern は **12 prefix の閉じた allowlist** なので、**互いに相手が通す id を弾く** — SDK は `weather.`（自身の docstring の例）と `my_server.` を通し、`ai-server.` と**正準の 3 セグメント形**を弾く（`-` が文字クラスに無い）。**3 つ目の欠陥を今回発見**: `define_capability` は `server_type` を既定 `DEV` のまま prefix から導出しないので、**既定引数で構築できる prefix は `dev` ただ 1 つ**（Phase 9 で削除したサーバ）。既存 SDK テスト 11 件が全て `dev` を名乗っているのはそのため。帰結は全て同じ穴 — `docs/plugin-sdk.md` の Quick Start・`capability.py` の docstring・`tools/create-capability-server` の生成コード・**`examples/example-weather-server`（import すら通らず、しかもリポジトリのどこからも参照されていない）**。ピン `packages/aegis-sdk-python/tests/test_capability_id_contract.py`（8 関数 / 23 ケース）は両方の pattern を**実物から発見**し（スキーマは `model_fields` の metadata、SDK は AST — インラインのリテラルで import 不可）、**食い違いそのもの**を等式で固定するので**どちらを直しても落ちる**。「修正」ではなく「記録」である旨を docstring に明記。**変異 5/5 捕捉**（スキーマ拡張 / SDK の allowlist 化 / 既定 server_type 変更 / 発見の破壊 → collection ERROR / example の修正）。**変異 2 件が教訓**: example の `server_prefix="weather"` は **2 箇所**あるので 1 箇所だけの変異ではテストが動かない（replace-all が必要）、そして発見を壊す変異は `FAILED` ではなく **collection ERROR（rc=2）**で出るのでハーネスは **`rc≠0` を捕捉**とする。SDK **25 → 48 passed**、ai-server **1714/31 のまま**、room 14 / browser 100 再実測一致。`scripts/test-all-suites.ps1` は**コメントから数を削除**（数は腐る）— AST パース errors=0 |
| `2da2c37` | **B-12 を「記録」から「ピン」へ — 39 件の deny 一覧は、それを読むゲートとは別の id 方言で書かれている**: 測定で 4 つが判明。① **39 件すべてが `catalog.resolve()` で解決不能**（canonical 8 件はすべて `pc-server.*`、残り 31 件は `browser.send_email` のような短縮 prefix）。② 生きた **128 capability のうち禁止 action を持つものは 0 件** — **今は守る相手が存在しない**から見えない。③ `validate_settings_change` の**3 つのループのうち `disabled_capabilities` のループは本体が `pass`**（AST で確認）でエラーを 1 件も積めず、残る 2 つが拒否するのは**そもそも no-op な設定項目だけ**（短縮形の鍵は `permissions.py` が引かない）。④ `EXPLICIT_DENY_PATTERNS` が覆うのは **39 件中 5 件**のみで、残りは別機構（egress ゲート / `DEFAULT_RISK_MAP` / プロンプト）が担っている — **制約は危うくない、この一覧が危うい**。ピン `tests/test_forbidden_capabilities_dialect.py`（7 関数 / 13 ケース）は方言構成・解決不能性・**canonical 形で書いた同じ意図が素通りすること**（`browser.send_email` → 1 件 / `browser-server.social.send_email` → **0 件**）・`pass` ループ・ゲートが引く鍵の形・パターン被覆を**等式と実測**で固定。**変異 6/6 捕捉**、すべて期待したテストで。**自作の誤りを 2 件、実行前にピンが捕まえた** — ① `per_capability` の期待値を自分の実測と逆に書いていた、② `per_capability.get` の呼び出しを 1 箇所と決め打ちしたが実際は 2 箇所（`evaluate` と `is_capability_enabled`）。ai-server **1714 → 1727 passed / 31 skipped**（+13、実測 362 秒）。**測定は「修復」ではなく「削除」に傾く**（守る相手 0・3 ループ中 2 つが無効・名前が何も指していない）が、削除は `docs/permissions.md` が CAPTCHA の根拠としてこの一覧を引用しているため**文書の訂正を伴う**（オーナー判断）。`FORBIDDEN_CAPABILITIES` は**保護された面ではない**ことも本項で確定した |
| （本節） | **進捗スナップショットの作成中に、live な「残り」節の陳腐化を発見して訂正**: 進捗を 1 枚にまとめる作業で、**§0 と §P1 の表だけが更新され、§1.4 / §2 / §3.1 / §3.3 が取り残されていた**ことが判明（型 9 の変種 — **同じ量を 2 箇所に書くと、片方だけが動く**）。① **§1.4** は「main より 79 コミット先行 / 508 ファイルが未コミット」のままだった — P0-1 で解消済みなのに、**「未コミット」の 1 語が解消済みのリスクを現行のリスクとして読ませていた**。実測（origin より **93** 先行・未 push・作業ツリーは未追跡 1 件のみ）に置換。② **§2** の「不可逆操作の台帳 = ⚠️ API のみ / UI は未着手」は P1-2 で完了済み（`IrreversibilityPage.tsx` が存在）— ✅ に訂正し、**北極星の中核である割り込み制御の行を新設**（P1-1 + P1-6）。③ **§3.1** の 4 項目のうち **1・2 は解消済み**（P1-6 / P1-2）、残るは **3（負担量の計測 = 存在しない）と 4（成長の閉路 = `approval_lesson` は読み手 4・生産者 0、2026-09-29 に再確認）**の 2 つだけ。④ **§3.3** の棚卸し表は 2026-09-28 の記録で、その後の P1-5 で **#1 / #3 / #4 / #9 は削除済み、#2 / #10 は固定、#8 は対象外**になっていた — 表の上に状態を明記。**副産物として `PROGRESS_2026-09-29.md` を作成**（日付付きスナップショット。**更新しない・必要なら新しい日付で書き直す**と冒頭に明記し、型 9 の入口を塞いだ） |
| `（本節）` | **判断待ちを 1 箇所に集約 — §0.2「オーナー判断レジスタ」**: 「判断しないといけないことをまとめて」という依頼で集めようとしたところ、**判断待ちが 6 つの節に散っており、しかも「判断待ち」という題の節（旧 §5「判断待ち 3 件の選択肢と推奨」）は 3 件とも解決済みの記録だった**ことが判明 — **題だけが未決を主張していた**（型 6「文書が『ゲートがある』と読める」の判断版）。**§0.2 を新設**し、**A 一言で決まる 8 件 / B 定義が要る 5 件 / C 方向づけ 3 件**に分類して、各行に**問い・選択肢・推奨・「決まらないと何が止まるか」**を持たせた。設計上の約束は 2 つ: **測定値を書かない**（正典は §0 / §1.1 / `AGENTS.md`）ことと、**決定が済んだ行は削除する**こと — この節は**短くなる一方**であるべきで、空になったときが「実装すべきことが無い」状態。旧節の題を「（解決済み・記録）」に改め、`PROGRESS_2026-09-29.md` §3 は §0.2 を正典として指すようにした（`588660f`） |
| `（本節）` | **A-1 を実行 — 死んだ deny 一覧と未消費の `allowlist` を削除（B-12 / B-13 の決着）**: §0.2 の A-1 は「削除」が推奨で、測定も揃っていたので実行した。**削除したもの**: `settings/validation.py` の 39 件 `FORBIDDEN_CAPABILITIES` とそれを参照する 3 ループ、`CapabilityPermissions.allowlist`、`config/settings.json` の `"allowlist": []`。**残したもの**: 同じ関数の無関係な 2 検査（camera snapshot の確認・`max_autonomous_runs_per_hour` ≤ 100）。**ピンは「記録」から「削除の証明」へ置換** — `test_forbidden_capabilities_dialect.py`（13 ケース）を削除し、`test_forbidden_capabilities_stay_retired.py`（11 ケース）を新設。**削除ピンは「定数が消えた」だけでは弱い**（システムを弱めれば満たされる）ので、実物の `ToolBroker` を駆動して未登録 id が `NOT_FOUND`（ポリシー評価の**前**）で拒否されること、生きたゲートが `capability.id` を鍵にしていること、`EXPLICIT_DENY_PATTERNS` が支払い・egress 迂回・ポリシー自己改変の意図に今も一致することを併せて固定した。**変異 14/14 捕捉**（うち 2 件は検出器自身を盲目化する変異、1 件は**修復方向** = 消費者を足す変異）。**B-13 の検出器を全セクションへ拡張**したところ、**生きた 2 件目の欠陥が即座に見つかった** — `max_autonomous_runs_per_hour` はバリデータだけに読まれ、他に消費者がいない（自律ループはハードコードされた予算で動く）。これは**既存の死にフラグ検出器が見逃していた**（識別子走査はバリデータを「読者」と数えるため）。`_RECORDED_GAPS` に記録し、§0.2 の B に追加。**副産物**: §4.1 の B-7 行が「**12 モデル / 95 フィールド**」と書いていたが、実測は当時 **11 / 94**、現在 **11 / 93** — **モデル数は削除前の値、フィールド数は 106 から AutonomyProfile の 11 だけを引いた手計算**（親の `AEGISSettings.autonomy` 参照フィールドを引き忘れていた）。ai-server **1723 passed / 31 skipped**（1727 − 13 + 11 − 6 + 5 − 1、実測 365 秒）。**1 件減った理由も特定** — `test_ineffective_flags.py` の設定フィールド parametrize が `CapabilityPermissions.allowlist` の 1 ケースを失ったため |
| `952caaa` | **A-3 を実行 — サーバ名簿を 1 つにする（B-15 の決着）**: `aegis_schema/roster.py` を新設し、6 サイト（`capability_catalog.py` ×2 / `prompt_regression.py` / `dashboard_legacy.py` / `models.py` / `tool_broker.py`）がそこを参照する。**6 つの写像すべて HEAD と値が同一**（純粋なリファクタ）。退職サーバは `RETIRED_SERVER_ROSTER` に 1 回だけ書き `**` 展開で折り込むので、`dev-server` を綴るモジュールは **6 → 3**。名簿リテラル **15 → 10 箇所 / 11 → 7 ファイル**、記録ドリフト **5 → 2 サイト**。**測定で登録簿の前提が 2 つ崩れた** — `server_id → ServerType` の写像は **5 コピーで、うち 2 つは既に食い違い**、15 箇所のうち **3 箇所は名簿ではない**（`situation.py` は状況ソースの語彙で `ai-server → "webhook"`）。検出器は**事実の移動に追随**させ（`_id_consistency_map()` が AST のローカルではなく名簿を読む）、**消えた「dict リテラルは 1 つ」ガードはそれが守っていた不変量で置き換えた**（validator 本体にサーバ名の文字列定数が無いこと）。**撤回したアサーション 2 つ** — `PREFIX_BY_ID` vs `_PREFIX_MAP` は両辺が同じ tuple 由来で**絶対に落ちない**（変異 `room → rm` が緑のまま）、manifest の `server_id` vs id prefix も同様（`folder_registry` が両方をパスから導出し、不一致は `list_all()` の前に拒否される）。**どちらも「検査に見えて検査でない」**。残る 10 箇所は**モジュール単位で記録し等式で固定**（`len >= N` の床では増加を検出できない）、退職 id の綴り箇所も直接固定して `_MIN_ROSTER_SIZE` の盲点を塞いだ。**変異 12/12 捕捉**、原ファイルはバイト単位で復元。ai-server **1724 → 1726 passed / 31 skipped**（+2 = 新規 7 関数 − 消えた parametrize 5、HEAD の worktree で per-file に確認） |
| `（本節）` | **B-3 を「記録」から「ピン」へ — 自律実行経路が 2 本あり、登録簿は死んだほうを「生」と書いていた**: 測定で **§5.1 の `motivation_arbiter` 行の判定そのものが誤り**と判明。`autonomous_controller.py` が import しているのは事実だが、**その importer 自身が import 元ゼロ**（`src/`・`tests/`・docs のコードすべて）なので、arbiter は**到達不能なモジュール経由でしか到達できない**。「生」ではなく「**死んだ経路の上に乗っている生きたコード**」。`docs/self-development.md` の冒頭図は `AutonomousController` を**入口として描いている**が、実測の入口は `runtime.py:1586 _create_autonomous_loop` が直接構築する `AutonomousLoop`（`start_autonomous_if_enabled` から起動）— 約 700 行が**誰も起動しない 2 本目の入口**。**走査を 1 回間違えた**: 「パッケージ外から import されているか」だけを問うと **5 つ**が到達不能に見えるが、`planner`（`autonomous_loop` 経由）・`l2_mind` / `l2_models`（パッケージ `__init__` 経由）は到達可能で正解は **2 つ** — **1 ホップの関係を数えて到達性と呼んではいけない**。3 層目も測定: `autonomous/` で `requires_approval` に触れる **7 箇所はすべて `motivation_arbiter.py`** で、`MotivationDecision` 側は**読者 0**、`ExternalTask` 側は `:214/:234/:254` が**読んでいる**が**どこでも構築されない**ので到達不能（`_build_task_request` の `isinstance` の腕も同じ）— **「読者が 0」と「読者が到達不能」は別の死**で、後者のほうが悪い。ピン `tests/test_autonomous_execution_path_is_single.py`（8 関数）は**配線しても削除しても落ちる**。**変異 10/10 捕捉** — うち **M3 の初回はハーネスの期待誤り**（`import AutonomousLoop as _RenamedLoop` は部分文字列が残り経路も動くので緑で正しい）だったが、これで**検査が空白依存の部分文字列だった**ことも判明したので AST 化し、M3 を 3 通りに分割して再実行。**M8（検出器の盲目化）が最も有用** — `_SRC` を存在しないディレクトリに向けると **8 件中 5 件が落ち、2 件は空集合を assert するので空虚に緑**のまま（ガードが肯定の観測を assert している唯一の理由。数字は docstring に記載）。原ファイル 5 本はバイト単位で復元（sha256 検証）。ai-server **1726 → 1734 passed / 31 skipped**（**+8 = 新規 8 関数**、実測 388 秒）。`docs/self-development.md` の**図の訂正はオーナー判断**（「こう動くべき」か「こう動いている」の書き間違いかは決められない）— ただし**実測と食い違っている事実**は注記した。**§4.3 にクラス 15（到達性は推移する）を新設**。**訂正しなかった記述**: `AGENT_PROGRESS.md:820` の `runtime.py:1618` は `reflection_engine` に係る記述で**正しい**（行番号だけを grep して主語を確かめないと、正しい記述を誤りとして「訂正」してしまう） |
| `（本節）` | **B-6 を測りにいって、その一段下に B-20 を発見 — スキーマは 27 の境界を宣言し、生きた書き込み経路は 1 つしか検査しない**: B-6 は「`max_autonomous_runs_per_hour` を配線するか削除するか」で、その前提は「バリデータだけが読む」。**前提は正しかったが、そのバリデータが何をしているかを読んで別の欠陥が出た** — 設定スキーマは **27 フィールド**に `ge`/`le` の境界を宣言しており、それらは**構築時**に強制される。しかし生きた唯一の書き込み経路 `SettingsStore.update_section` は提案設定を**無検証の `setattr`** で組み立て、`validate_settings_change` が再検査する境界は **1 つだけ**（`max_autonomous_runs_per_hour > 100` — そのフィールド自身の `le=100` の**写し**）。**27 のうち 26 が API 経由で突破でき、値はディスクに残る**（実物の `SettingsStore` を `tmp_path` に対して 1 フィールドずつ駆動し、読み戻して確認 — 26/26 突破・1/1 阻止）。**仮説を 2 回外した**: ①「検査は発火しない」→ **誤り**。`le=100` が構築を守るが**代入は検証されない**ので、`setattr` 経路では検査が**唯一の防波堤**であり、そこに 1 つだけ手書きされている。② 自作の走査が `VALIDATION_HINTS` の `guard` にクラス名 `SettingsPermissionGuard` が一致して 5 件を偽陽性（`clipboard_capture_enabled` などは `permissions.py` の**生きたゲート**）。**化粧ではない理由**: 突破できる集合に**保持期間の上限**が入り、`backup/retention.py:49` が `episodic_retention_days` を `max_age_ms` に変換して prune するので、スキーマが拒否する値で 1 世紀分を保持できる。同じモジュールの docstring は 4 つの保持を "Handles:" と並べていたが実測は **episodic のみ強制 / notification と screenshot は報告だけ / audit は `self._audit` が保存されどのメソッドも読まない** — **「報告だけ」は UI からは実装済みに見える**（docstring は測定に合わせて訂正。誤った主張の訂正はオーナー判断ではない）。ピン `tests/test_settings_edit_path_enforces_schema_bounds.py`（6 関数）は境界を**モデルから発見**、バリデータの読みを **AST から発見**、突破の有無を**実物のストアを駆動して**判定し、突破集合と阻止集合を**両方向の等式**で固定するので**書き込み経路を直しても落ちる**。**変異 10/10 捕捉** — うち **M5 はハーネスの期待誤り**（`le` だけ落としても `ge` が残るので観測が変わらない＝変異が対象を動かしていない）、**M4 は変異自体が壊れていた**（`ConfigDict` を import していない `models.py` に書いたので `NameError` で collection ERROR。**ERROR の原因を読むこと — 自分の変異が壊れている場合は「捕捉されなかった変異」ではない**）。**修復方向の変異を 3 つ**（バリデータに 2 つ目の境界を足す / `update_section` が検証済みモデルを構築する / `validate_assignment` を有効化）入れて**3 つとも落ちる**。バリデータを 27 個の境界を再検査するよう**拡張しない** — それはスキーマの写しを書き込み経路に置くことで、このリポジトリが繰り返し見つけている重複そのもの（docstring に明記）。ai-server **1734 → 1740 passed / 31 skipped**（**+6 = 新規 6 関数**、実測 403 秒）。原ファイル 5 本はバイト単位で復元（sha256 検証）。**§0.2 に A-9**（推奨は `update_section` が検証済みモデルを構築する形 — `validate_assignment` は `list[str]` を返す契約を壊すので不可）、**§4.3 にクラス 16**（宣言は構築でしか検査されない） |
| `（本節）` | **B-21 — 設定画面は「何も変えないスイッチ」を 10 個見せている**: B-6 の測定中に、未読集合の**利用者側**が未測定だと判明。`web-ui/src/pages/Settings.tsx::editableSettings` は `GET /api/settings`（= `AEGISSettings.model_dump()`）からコントロールを**発見**するので UI に名簿が無い — **古くならない代わりに何でも出す**。実測: ペイロード **80** フィールド / 描画 **26**（`result.length >= 24` で切って `slice(0, 32)`）/ 負債の記録 **23** / **描画されかつ誰も読まない 10**（`autonomous.*` 8・`servers.*` 2）/ `preferred` **15 件のうち 5 件がどのフィールドとも一致しない**（`display_privacy_mode`・`notifications_enabled`・`daily_budget_usd`・`monthly_budget_usd` は `web-ui` にしか無く、`memory_budget_tokens` は `context_builder` の実行時属性）。**可視集合は宣言順の事故** — 切り捨てが*描画された*数で数えるので、早い位置に 2 つ足すと記録済みの死んだフィールドが可視窓から押し出される（変異 M11 で実測）。**ピン自身が 2 回壊れていた**（どちらも実行が捕まえた）: ① 負債の記録は**クラス**で名指しし UI は**セクション**で名指しするので、交差は**恒偽ではなく恒空**（翻訳を `model_fields` の annotation から**導出**して解消）。② `_UNOWNED_DEBT` は**注釈付き代入**なので `ast.Assign` だけの走査は**空集合を返し**、`∅ == ∅` が真なのでどちらの向きも通ってしまう（両ノード種別を扱い、件数を assert する非空虚ガードを追加）。**変異 18/18 捕捉**（原ファイル 4 本をバイト単位で復元・sha256 検証）。**3 件は「捕捉されないこと」が期待値** — `==` を `<=`/`>=` に弱めると**片方向の変異をどちらも見逃す**ので、等式の両方向がそれぞれ load-bearing である。**M12 は最初のピンでは無音だった** — 遅い位置のプローブを隠していたのが切り捨てではなく `slice` で、**テストが間違った理由で緑**だった（スライスを無効化した描画を足して、切り捨てだけが説明できる形に直した）。ai-server **1740 → 1756 passed / 31 skipped**（**+16 = 新規 6 関数 + 10 parametrize**、実測 375 秒）。**§0.2 に A-10**（`preferred` の死んだ 5 件は消せば挙動が変わらないので一言で決まる）と **B-6 への追記**（10 個の死んだコントロールはフィールドの去就そのもの）、**§4.3 にクラス 17**（名簿の誤りは鳴るが、順位の誤りは鳴らない）。**台帳自身の型 9 を 2 件訂正** — C-3 のクラス数「12」（§4.3 は既に 16 だった）と A-5 の「本日だけで 12 回」。台帳は「測定値を書かない」と自称しながら、この 2 行が数を持ち片方が既に古くなっていた。**加えて §0 の egress 値も 1 ずれていた** — 「211/23（234 マーカー）」の実測は **210 passed / 23 skipped（233 マーカー）**。原因まで特定: A-1 が `test_ineffective_flags.py` の parametrize を 1 ケース失ったとき、**総数の −1 は記録したが egress の数は測り直さなかった**（234→233 / 211→210）。**変更が「派生する量」に与える影響は、測らないと見えない。** 内訳: closure 36 / gate 53 / reliability 10 / ineffective_flags 109 / local_llm_path 25 = 233 |
| `（本節）` | **A-9 を実行 — 設定の書き込み経路が、スキーマの境界を強制するようになった**: §0.2 の A-9 は「① `update_section` が検証済みモデルを構築する」が推奨で、測定もピンも揃っていたので実行した（A-1 と同じ判断）。`SettingsStore.update_section` は提案設定を **`setattr` で組み立てる**のをやめ、現在のダンプに要求されたキーを重ねて `AEGISSettings.model_validate` に通す（未知のセクション・フィールドの拒否は維持。判定を `hasattr` から `model_fields` に変えたので、メソッド名を渡しても通らない）。**実測 26 突破 / 1 阻止 → 0 突破 / 27 阻止**（実物のストアを 1 フィールドずつ駆動）。境界値は受理され（365 が通り 366 が拒否）、**スキーマで表現できない意味論的検査は生きている**（`camera_snapshot_enabled` は今も確認を求める）。**バリデータの唯一の手書きの写しは残した** — 構築が先に拒否するので**ストア経由では到達不能**になったが、public な関数で契約が独立しており、消すと `test_guarded_settings_fields.py` の**唯一の実例**が消えるため（理由をピンとソースコメントに明記）。ピンは**回帰ピンに転換**（`_RECORDED_BYPASSED` = ∅ / `_RECORDED_ENFORCED` = 27）し、**2 集合が全フィールドを分割すること**と**合法な値は通ること**を足した — 後者は **`blocked == 27` が「すべて拒否するストア」でも満たされる**ため（**「満杯の集合」も空虚になりうる**。B-3 の「空集合は空虚に真」の裏返し）。**変異 12/12 捕捉**、うち **2 件は「捕捉されないこと」が期待値**（`==` を両方包含に弱めると欠陥が戻っても等式テストは無音 — 保持期間のテストが 2 番目の防波堤）。**ハーネス自身の欠陥を 1 つ踏んだ**: 同一ファイルへの 2 つ目の編集を**元のバイト列**から作り直していたので 1 つ目が無言で上書きされ、W1/W2 を誤って「捕捉」と報告した — **このリポジトリが既に記録している罠と同じもの**を自分の道具で踏み、編集をファイルごとに蓄積する形に直した。**副産物**: `test_guarded_settings_fields.py` の既存 I001 を修正（`src/` と `tests/` で `aegis_ai` の扱いが違うので**同じ import が場所によって別の並びになる**）。**`ruff format` はこのリポジトリの規約ではない**ことも実測（未変更ファイルも reformat 対象）— `ruff check` のみを満たす。ai-server **1756 → 1758 passed / 31 skipped**（**+2 = 新規 2 関数**、実測 406 秒）。egress は 210/23 のまま。**§0.2 から A-9 を削除**（レジスタは短くなる一方であるべき）、**§4.3 クラス 16 に修復済みの注記** |
| `ebe1506` `5669654` | **A-10 を実行し、その直後に git オブジェクトストアの全消失を検知・復旧した（同日に 3 つの決定をまとめて処理）**: **A-10** = 設定画面の `preferred` から一致しない 5 鍵を削除。実測: `display_privacy_mode`・`notifications_enabled`・`daily_budget_usd`・`monthly_budget_usd` は `Settings.tsx` 以外に**リポジトリのどこにも無く**、`memory_budget_tokens` は `context_builder` の実行時属性。`preferred` は**ペイロードのキーでしか引かれない**ので削除は挙動を変えない。B-21 のピンを記録から**回帰ピン**へ転換（`unmatched == ∅` は空リストでも真なので非空虚ガードを追加）、**変異 5/5**。**A-5** = ブランチを `cursor/cf-grpc-and-goal-hygiene` から**フラット名 `cf-grpc-and-goal-hygiene` に改名** — 以降のコミットは B-6 を起こさず ref が書ける（実測: フラット名で 2 回コミットし、いずれも ref が正しく書かれた）。**A-8** = ルートの `query`（BOM + `GIOV3`）を削除。**そして本日の重大インシデント**: 作業中に `git count-objects -v` が **`count: 0 / in-pack: 0 / packs: 0`** を返し、**ローカルの全オブジェクトが消失**していた（`.idx` ×3 だけが残り `.pack` が無い）。**作業ツリーは無傷**で、origin より先行していた約 105 コミットは**内容だけが作業ツリーに残った**。復旧は非破壊のみ: reflog を保全 → 壊れた ref を削除せず退避 → `git fetch origin` で **10,586 オブジェクト復元** → ブランチを origin の head に再アンカー → `git read-tree HEAD` でインデックス再構築。**副産物 2 件**: ① **B-6 は `refs/remotes/` にも及ぶ** — `git fetch` は入れ子の `refs/remotes/origin/cursor/<name>` も書けないので、リモート追跡 ref は既知の SHA から直接書いた。② `git read-tree HEAD` は origin が追跡している **ignore 対象の 57 ファイル**をインデックスに戻し、続く `git add -A` が再追跡した — **ignore 規則はインデックスにあるファイルを untrack しない**ので `git rm --cached` で明示的に外した（ファイルはディスク上そのまま）。報告書 `INCIDENT_2026-09-29_git-object-loss.md`。**原因は断定できていない**（相関は `git stash push`/`pop`、stderr は捨てていた） |
| `（本節）` | **A-7 を実行 — 未 push の全コミットをリモートへ push し、レジスタから A-7 を削除した**: オーナーが `gh auth login` を実行したので、記録済みの推奨①（push）を実行した。**リモート `origin/cursor/cf-grpc-and-goal-hygiene` は `d96e908` → `b6706d8`**（fast-forward — push の前に `git merge-base --is-ancestor` で祖先関係を実測）。**この環境の資格情報は `git credential.helper = helper-selector` で対話専用なので、`GIT_ASKPASS` に一時スクリプトを指し、トークンは `gh auth token` の出力を環境変数で渡した**（トークンはディスクに書いていない）。`gh auth status` が「未ログイン」と答えるのは**トークンが Windows 資格情報マネージャにあり、この MSYS の `gh` からは見えない**ためで、`gh api user` の成功（`Kohaku912`、scopes に `repo`）と `%APPDATA%/GitHub CLI/hosts.yml` の存在で別途確認した。**push が B-6 を再発させ、被害範囲が従来の記録より広いことが判明した**: 入れ子 ref の書き込み失敗は `refs/remotes/origin/cursor/` だけでなく、**同じ親ディレクトリの兄弟 ref `refs/remotes/origin/main` まで消した**（push 前後の `git for-each-ref refs/remotes/origin/` を突き合わせて実測 — push 後は **0 件**）。`packed-refs` に退避も無かったので、両方を既知の SHA から直接書いて復旧した（**オブジェクトストアは無傷** — `in-pack: 11428`）。**§0.2 から A-7 の行を削除**（レジスタの契約「決まったら行を消す」）、§0 の「最大のリスク」行と §0.1 の見出し（「未 push」）を現状に合わせた。**副産物: 数値表の再実測で 2 つの古い値を発見** — `SDK 48 → 71` と `pc-server 16 → 30`。前者は**同じ値を 3 箇所（§1.1 / `AGENTS.md` / 当の検証スキル）に書いており、そのうち 2 箇所が追随していなかった**（スキルは §1 の表が 71、同じ文書の「測定衛生」節が 48 と、**自己矛盾**していた）。実測: ai-server **1758 passed / 31 skipped**（collect-only で 1789 = 1758 + 31）・egress **233 マーカー / 210 passed / 23 skipped**・room **14**・browser **100**・SDK **71**・pc-server **30**・web-ui tsc clean / vitest **144**（19 ファイル） |
| `（本節）` | **A-11 の ③ を完遂 — `approval_decisions` を「固定して記録」した（ピンは無かった）**: A-11 の推奨 ③ は「現状維持（**固定して記録**）」だが、`ai-server/tests/` に `approval_decisions` を参照するテストは 1 つも無く、**半分が未実施**だった。`test_forced_gate_stays_retired.py`（承認時代の残骸を所有する唯一のファイル）に **8 テスト**を追加し、**4 番目の面**として固定した。主張は 4 つ: ① `approval_decisions` を宣言する関数は発見した集合が記録と**等式**（`reflect` + 3 classifier）② **呼び出し元が src・tests のどこにも無い**（`tests/` も走査する — テストが渡せば、本番が渡さないのに生きた顔をする）③ 唯一の `APPROVAL_LESSON` 生産者は `approval_decisions` を回すループの本体にある（到達不能のリンクを**散文ではなく構造で**固定）④ **生産者は読者が照合するキーを書かない**。**変異 8/8 捕捉、方向プローブ 2/2 が期待どおり緑**（`==` を `>=` に弱めると読者の**増加**を、`<=` に弱めると**減少**を見逃す — 等式の両方向がそれぞれ load-bearing）。**走査を盲目化する変異が最も有用**: `_functions_declaring` を空にすると等式テストが落ちる（記録側が**非空**だから）。**「何も無い」という形の assertion は走査が壊れると空虚に真になる**ので、記録集合を非空に保つことが唯一の防波堤。**ハーネス自身の欠陥を 1 つ踏んだ** — 復元用の辞書に**変更後のテキストを上書き**していたので、`finally` が変異を書き戻し、**変異が蓄積したまま次の変異を測っていた**（最初の実行は全体が誤り）。開始時の sha256 を取り末尾で突き合わせるガードを足して修正 — **捕捉されない変異ではなく、道具が壊れていた**。ai-server **1758 → 1766 passed / 31 skipped**（**+8 = 新規 8 関数**、実測 326 秒）。ruff clean |
| `（本節）` | **`docs/android-safety.md` が、削除済みモジュールを「在る」と現在形で書いていた（4 箇所）**: レジスタの「全項目がテストでピン留めされている」という主張を監査する過程で、**B-4 の主題である `ai-server/src/android_server_client.py` がリポジトリに存在しない**ことを実測した（`find` も `git ls-tree HEAD` も空、`docs/` 以外に参照なし）。**登録簿側は正しかった** — §5.1 が P1-5 の削除（1,031 行）と「保全対象」（`NotificationFilter` のパッケージ遮断 + ingest 時のカード・メール・OTP マスク、`contains_password_field`）を記録し、**削除は可逆**であることも書いている。**誤っていたのは `docs/android-safety.md` だけ** — 「machinery ... lives **only** in the orphaned `ai-server/src/android_server_client.py`」と**現在形で 4 箇所**に書き、**削除の事実をどこにも書いていなかった**（削除は 2026-09-29、この文書の最終更新は 2026-09-28）。**4 箇所すべてを過去形に訂正**し、冒頭に削除日・復元コマンド（`git show ebe1506^:ai-server/src/android_server_client.py` — 41,780 バイトで実測）・保全記録（§5.1）への参照を追加した。**「オーナー判断待ち」と書いてあった箇所も訂正** — 「配線するか削除するか」は削除が済んでいるので、残る問いは「live 経路に再実装するか」（= B-4）。**同じ主張をしている文書は他に無い**ことを確認（`AGENT_PROGRESS.md` は日付付き進捗ログで過去形、`data/reports/mock_inventory.md` は 2026-07-20 生成の未追跡スナップショット、`.omo/` は gitignore 済み）。**レジスタと §5.1 は正しく、文書 1 本だけが取り残されていた** — 型 9 の変種 |
| `（本節）` | **`docs/agents/rollback.md` の緊急停止が「読まれない環境変数」を指示していた — そして `requires_feature` フィルタの供給者ゼロを発見**: 生きている文書の数値と主張を掃く作業。`docs/architecture.md` のテスト数 **1758 → 1766** を 3 箇所で訂正（同ファイルの**能力数の行は実測して正しいことを確認** — `list_for_llm()` が **128** 件、内訳 pc 58 / ai 32 / android 17 / browser 16 / room 5、重複 0）。`docs/status.md`（「承認時代」と明記）・`fix-instruction-checklist.md`（`Verification Snapshot (2026-07-23)`）・`IMPROVEMENT_PROPOSAL.md` Phase 4 の実施状況（`2026-09-27 更新`）は**日付付きの記録なので触らない**。**egress の「38 件が失敗」は実測して正しかった**（変異: **38 failed / 172 passed / 23 skipped**、通常: 210 passed / 23 skipped、計 233）— **「食い違い」を直す前に測る**という規則がまた 1 つ誤修正を防いだ。**本題**: `docs/agents/rollback.md` は緊急停止を「`config/settings.json` **または** `export AEGIS_AGENTS_ENABLED=false`」と案内していたが、**`AEGIS_AGENTS_ENABLED` を読むコードはリポジトリに 1 行も無い**（設定は `config/settings.json` からのみ読み込まれ、`BaseSettings` / `env_prefix` / `getenv` はいずれも無し）。**この環境変数は何もせず、エラーも出さない**のでサービスは正常に起動し、**止まったと誤認する** — 緊急手順における型 6。`agents.enabled` の方は本物（`runtime.py:1479` が `agent_backend=None` にする）で、既定 `False`・`config/settings.json` に `agents` 節が無いので**現在すでに停止済み**。文書を訂正（読まれない経路を明示・腐った `157 tests` を削除・自分の訂正が「この文書の 2 箇所だけ」という**自己言及的な数**を壊したので非腐敗な表現に修正）。**副産物（より重い）**: `requires_feature` フィルタは**配線済みだが供給者がゼロ** — `feature_flags` は定義 3 箇所と受け口 1 箇所にしか現れず、**非 `None` を渡す呼び出し元がリポジトリに存在しない**ため一度も走らない。→ **§0.2 に A-12 として登録** |
| `（本節）` | **`AEGIS_AGENTS_ENABLED` の一般化監査 — 文書・compose が名指しする環境変数を、読者と突き合わせた**: A-12 は「文書だけが読む統制」の 1 例にすぎないので、掃き出しを一般化した。**名前の権威ある出所**（`export NAME=` / `${NAME}` / compose の `environment:` キー / `.env.example` のキー）から **94 名**を集め、コード側の出現と突き合わせた。**当初 17 名が「読者なし」と出たが、そのほとんどは計測法の artefact だった** — ① `_env_host("ANDROID_SERVER_HOST")` のような**ヘルパー経由**の読み（`status_manager.py:44` / `alert_manager.py:32`）② `f"{prefix}_HOSTS"` / `f"{prefix}_MACS"` / `f"{prefix}_MAC"` のような**動的構築**（`endpoint_resolver.py:203,296,392`）は、名前のリテラル検索では見つからない。**「リテラルが無い＝読者がいない」は成り立たない**（A-12 の grep-key artefact と同じ罠を、今度は自分の道具で踏んだ）。**実際に読者ゼロだったのは 4 名**: **`AGORA_MASTER_USER`**（compose が ai-server コンテナへ渡すのに読むコードが無い — `AGORA_TOKEN` / `AGORA_BASE_URL` は `agora_client.py:34,38` が直接読むので、AGORA 系に動的構築は無い）と、**`.env.example` にしか出現しない** `AEGIS_PUBLIC_CORE_HOST` / `AEGIS_PUBLIC_CORE_GRPC_PORT` / `AEGIS_PUBLIC_DASHBOARD_URL`。**残りは健全と確認**: `AEGIS_LAN_SCAN_ENABLED`（`endpoint_resolver.py:404` の `_env_bool`）、`ANDROID_SERVER_HOST/PORT`、`PC_SERVER_HOSTS/MACS`・`ROOM_SERVER_HOSTS/MACS` は読まれており、`AEGIS_CORE_GRPC_PORT` / `AEGIS_DASHBOARD_PORT` は compose の**ポート対応のホスト側置換**、`POSTGRES_USER/PASSWORD` / `COLLECTOR_OTLP_ENABLED` は**第三者コンテナ**の設定。→ **§0.2 に A-13 として登録** |
| `（本節）` | **A-12 の ③ を完遂 — 「誰も渡さない引数」を固定して記録した**: A-12 の推奨 ③ は「現状維持（**固定して記録**）」で、A-11 と同様に**ピンの無い半分が残っていた**。`requires_feature` を所有する唯一のファイル `ai-server/tests/agents/test_agent_runtime.py` に **10 テスト**を追加（同ファイル **16 → 26**）。**記録した 4 集合**（実測 2026-09-30、`src/` 全体）: 宣言 **4** / **供給 0** / 転送 **3** / 無言の本番呼び出し **4**。検出器は `ast` で入口 4 つ（`list_for_llm` / `list_for_agent` / `mcp_tool_schemas` / `list_tools_for_agent`）を走査し、**位置引数とキーワード引数の両方**を扱い、`list_tools_for_agent` は**キーワード専用**として位置を `None` にする。**`feature_flags=None` は供給ではなく省略**（既定と同じなのでフィルタは OFF のまま）だが、**`set()` は供給**として扱う — フィルタを **ON** にして何も有効にしないので**隠す**側に働き、`None` とは意味が反対になる（両方に専用テスト）。生きた経路のテストは `ai-server.agent.delegate` が `list_for_llm()` に**見え**、`list_for_llm(feature_flags=set())` では**消え**、かつ `AgentSettings().enabled is False` であることを同時に固定する（＝**欠陥そのものを記録**する形。どれか 1 つでも配線されたら落ちる）。**変異 7/7 捕捉 + 方向プローブ 1/1 緑**、原ファイル 4 本はバイト単位で復元（sha256 一致）。**M3 は正直に弱い** — 「宣言を 1 つ消す」変異は assertion ではなく `SyntaxError`（`named arguments must follow bare *`）による collection ERROR で落ちた。ビルドは止まるが**狙った assertion は発火していない**ので、捕捉として数えるが**弱い捕捉**と明記する（原因を確かめずに「捕捉」と報告しかけた）。集合を直接壊す M5（走査の盲目化）・M7（転送/供給の判別破壊）が本命。**A-12 の ①/② はオーナー判断のまま行を残す**（③ だけが済んだ）。ai-server **1766 → 1776 passed / 31 skipped**（実測 355.77 秒）。**同じコミットで `AGENTS.md` の数値表も実測して訂正** — `95 fields across 12 models` は**古く**、実測は **93 fields / 11 models**（`22 are recorded debt` は正しかった — 記録済み未読 **23** = 意図的な 1 + 負債 22） |

| `（本節）` | **デバイス不要なのに一度も走っていなかった Android manifest 検査を移し、Android の「検証不能」を §0.2 に登録した（C-4）**: 出発点は「**`pytestmark` によるモジュール全体スキップは、`-m` の絞り込みと違って CI の通常実行からも見えない**」という一点。`test_android_local.py` は `AEGIS_ANDROID_LOCAL=1` が無いとモジュール全部をスキップするが、その中の `test_android_ui_input_manifests_are_executable` は**デバイスを一切使わず manifest の JSON を読むだけ**で、`BUG_REPORT.md` も「デバイス不要で通る」と記録していた — にもかかわらず**毎回スキップされていた**（CI はマーカーで絞らないので、理由はモジュールスキップだけ）。① 検査を `test_manifest_schemas.py` へ移し、**3 ファイルの名指しをやめて `ui/` を発見**する形に一般化（4 つ目がすり抜けない）、**非空虚ガード**（`>= 3`）と「**キーの不在は合格ではなく不合格**」を追加 — 後者は A-12 の「何も供給しない」の manifest 版で、**不在キーが安全な既定値として読まれていた**旧挙動を閉じる。② 同じファイルの `_invoke` が**退役済みの `is_approved=True` を渡していた**ので削除（**推測ではなく実測**: `ValueError: Protocol message ToolInvocationRequest has no "is_approved" field.` — フィールドは `capability_id` / `invocation_id` / `caller` / `params_json` の 4 つ、proto は `reserved 5, 6;`）。**変異 3/3 捕捉 + baseline 緑**、原ファイル 3 本はバイト単位で復元（sha256 一致）。今回は**各失敗の理由文が狙った assertion であること**まで確認した（A-12 の M3 は `SyntaxError` による collection ERROR で狙った assertion が発火しておらず、**原因を確かめないと「捕捉」と誤報告するところだった**）。ai-server **1776 → 1777 passed / 31 → 30 skipped**（実測 303.75 秒）。**総数 1807 は不変** — これは**追加ではなく移動**なので通過 +1 / スキップ −1 が正しい期待値（当初「1778」と予測したのは**算術の誤り**で、正しい予測は 1777）。egress は**派生量なので測り直した**: 233 マーカー / 210 passed / 23 skipped（不変、床 160）。**§0.2 に C-4 を新設** — Android は `java` / `javac` / `adb` / `gradle` / `kotlinc` が**すべて不在**で、**待っても直らない環境の不在**（時間の問題ではない）。登録簿の「ここが未決の*すべて*」は**この行が抜けていたぶんだけ偽だった**。`AGENTS.md` の Android 行の「**Builds**」も、ツールチェーンが無い以上**測っていない記憶**なので「Not verified」に訂正した。**§1.4 も訂正** — リモートは既にフラットへ移行済み（`origin/cf-grpc-and-goal-hygiene`）で、B-6 の説明を「入れ子名」から**深さ**へ差し替え、**腐る SHA を削除**した |

| `（本節）` | **「走らないテスト」を系統的に監査し、名前が主張することを検査していないテストを 3 件直した**: 前節の欠陥（モジュール全体の `pytestmark` が**デバイス不要なテスト**を飲み込んでいた）は**型**なので一般化して掃いた。**① スキップ機構の全数調査**: `ai-server/tests/` のモジュールレベル `pytestmark` は 6 つだけで、**スキップは 1 つ**（前節で修正済み）、残る 5 つは egress のマーカー（走る）。他の Python ルート（browser / room / android / SDK）にモジュールレベルの skipif は**無い**。`collect_ignore` / `xfail` / `--ignore` も**無い**。**② スキップ 30 件の実測内訳**（`-rs`）: 23 件 = `test_ineffective_flags.py:274` の**記録済み負債**（未読 22 + 意図的 1、各件に理由文）、**4 件 = `android_local`**、**3 件 = `test_openhands_backend.py`**（`openhands.sdk` 不在）。**③ 残る 4 件の android テストは 4 件とも本当にデバイスを要する**（`adb` / アプリ起動 / gRPC 越しの実機データ）のでゲートは正しく絞られている。**④ openhands の 3 件は設計どおり** — SDK は**別プロセス**（`aegis_agent_server/main.py` = `aegis-openhands-agent.service`）用で本体には入れない方針がその docstring に明記されている。**⑤ 本題**: テスト関数 **1530 件**を AST で走査し、**`assert` も `pytest.raises` も `raise` も持たないもの 6 件**を検出。2 件は import スモーク（正当）、**3 件が本物** — `test_task_manager_can_complete_task` / `..._can_fail_task` は名前が「can complete」なのに**状態を一切検査していない**（`complete_task` は未知 id で `None` を返すので「例外が出ない」は id が間違っていても通る）。`test_audit_manager_with_no_event_manager_is_noop` は docstring が「`policy.decision` を publish しない」という**検証不能な主張**をしていた（`event_manager=None` に観測点が無い）。**状態遷移・書き込み・`result_summary` / `error` を assert するよう直し、変異で証明** — **4/4 捕捉、うち 1 件は src 側**（`AuditManager.append` から `self._log.append(entry)` を消して「黙って捨てる」変異を作ると狙ったメッセージで落ちる）。原ファイルはバイト単位で復元（sha256 一致）。**⑥ 副産物**: `pc_local` / `room_local` / `e2e` の 3 マーカーは **`pyproject.toml` に宣言されているが使うテストが 0 件**（`pytest -m e2e` は **0 件を選択**し 1807 件を deselect）。`test_e2e_lifecycle.py` の**モジュール docstring が「full approval lifecycle」のまま**だった（承認レッグは 2026-09-27 に削除済みで、同じファイルの内側の docstring はそう書いている）ので訂正。**⑦ ゲート自体が自動化されていない**ことは **§0.2 の C-5** に登録。**テスト総数は 1777 / 30 で不変** — 追加ではなく主張の強化なので数値表は触らない |

| `（本節）` | **規約を直し、その規約に違反していた行と、同じ主張の「他の写し」を全部掃いた**: ① §0.2 の脚注は「各行は**問いと選択肢**だけを持ち、**測定値は書かない**」と言っていたが、**実測すると 15 行中 7 行が測定値を持ち**、しかも表には「**推奨と理由**」列と「**決まらないと何が止まるか**」列がある — **規約の方が実態と食い違っていた**。腐るのは**日付の無い現在値**だけなので、規約をその形に狭め、`問い` 列は数を伴ってよい（ただし**正典へのポインタを添える**）と明記した。C-3 の「12」と A-5 の「12 回」が 2026-09-29 に消されたのは**まさにこの形**で、狭めた規約はその一般化。② **狭めた規約をその場で適用** — B-2 の「1,104 行」・B-3 の「約 700 行」・B-6 の「22 件 / 26 個 / 10 個」・C-2 の「6 項目」を正典（§5.7 / §5.14 / §1.1・§5.16）への**ポインタに置換**（09-29 の「ポインタ化」と同じ手当て）。③ **B-6 の撤回が写しに届いていなかった** — 撤回は §1.4・`MEMORY.md`・skill 1 つに適用済みだったが、**§4.3 のバグクラス B-6 行は反証済みの 3 主張（「原因を特定」／「入れ子名でのみ発生」／「`update-ref` は解決策にならない」）をそのまま持ち、§1.4 と正面から矛盾**していた。加えて skill `aegis-consolidate-a-duplicated-fact`・`aegis-add-dashboard-page`・**インシデント報告**の 3 写し（履歴文書は書き換えず、冒頭に日付入りの訂正バナーを追加 — **観測事実は有効**で、撤回したのは*機序の説明*だけ）。④ **skill `aegis-verify-and-test` の push レシピが古い入れ子名**（`HEAD:refs/heads/cursor/…`）を指していた。**実測**: `git ls-remote --heads origin` は 2 本だけ（`cf-grpc-and-goal-hygiene` / `main`）で **`refs/heads/cursor/*` は存在しない** — そのまま実行すれば**リモートに 2 本目のブランチを作り、本物を古いまま残す**ところだった（無音の分裂）。⑤ 深さの数字が文書間で揺れていた（§1.4 は 2/3/4、skill は 1/2/3 — **葉を数えるかの差**）ので**数字をやめて ref 名で書く**ことにし、skill 側の表に規約を明記。**教訓を `MEMORY.md` に記録**: *訂正は写しを全部掃くまで終わらない*。**コードは不変** — テスト数は `ddced6a` の **1777 / 30** のまま |

> **台帳の範囲**: ここには**実質的な変更**だけを載せる。台帳に行を足すだけの記録コミットは
> 行を持たない。この規則は遡って適用していないため、**初期の `docs(review)` 系
> （`6067c20`・`b17da28`・`55ac93f`・`6249bfb`）と `fed358e` は未記載**のまま —
> 完全な記録は `git log` にある。

### 0.2 オーナー判断レジスタ（未決のみ）

**実装で閉じられる項目は尽きており、残っているのは判断です。** ここが未決の**すべて**です
（2026-09-29 に、6 つの節に散っていた判断待ちを 1 箇所に集めた — 集める過程で、
**「判断待ち」という題の節が実は解決済みの記録だった**ことも判明した）。
**決まったらこの表から行を消す。** 空になったときが「実装すべきことが無い」状態です。

#### A. 一言で決まる（実装は数行）

| # | 問い | 選択肢 | 推奨と理由 | 決まらないと何が止まるか |
|---|---|---|---|---|
| **A-6** | `aegis_ai/permissions/` の去就（**B-16**） | ① 削除 ② 配線 ③ 現状維持（固定済み） | **③**。②は**強制承認ゲートの復活**でオーナー境界違反。①はいつでもできる | なし（固定済みなので急がない） |
| **A-11** | **`ReflectionEngine.approval_decisions` 引数の去就** | ① 引数と、それを読む 4 箇所を削除 ② 呼び出し元を配線 ③ 現状維持（**固定済み** — ピンは 2026-09-30 に作成） | **③**（A-6 と同じ理由）。②は「承認判断の記録」を復活させる**製品判断**で、D4=(b)（強制ゲート削除・任意の確認は維持）と整合するかを先に決める必要がある。**② は B-5 ② と同じ 1 手**（§3.1 項目 4）なので単独では決めない。①はいつでもできる | **この行は §0.2 に無かった** — §5.1 が「保留」と書いたまま登録簿に移されていなかった。**実測 2026-09-30**: `approval_decisions` の出現 **12 箇所すべてが `reflection_engine.py` の内部**。**消費する箇所は 4 つ** — `_classify_outcome` / `_identify_root_cause` / `_classify_failure` の 3 分岐と、**`reflect()` 自身の `for dec in approval_decisions:`（:90、`MemoryType.APPROVAL_LESSON` を書く）**。**当初 3 つと数えたのは 4 つ目を見落としたためで、見落とした側こそが B-5 の生産者**。**呼び出し元が 1 つも無い**（`runtime.py:1624` は `memory_store=` しか渡さない）ので 4 箇所すべてが到達不能。引数があるだけで「承認判断が反映される」と読める（型 6 の引数版）。**③ の「固定」は 2026-09-30 に実施** — `test_forced_gate_stays_retired.py` に **8 テスト**を追加（読者集合の等式・呼び出し元の不在・生産者がループに守られていること・**生産者と読者の契約不一致**）。**変異 8/8 捕捉、方向プローブ 2/2 が期待どおり緑**（`==` を `>=`/`<=` に弱めると成長/縮小をそれぞれ見逃すので、等式の両方向が load-bearing）。ai-server **1758 → 1766 passed / 31 skipped** |
| **A-12** | **`requires_feature` フィルタが「誰も渡さない引数」で止まっている**（**A-11 と同じ形**） | ① 配線（`settings.agents.enabled` からフラグ集合を組んで `list_for_llm(feature_flags=…)` に渡す）② 機構ごと削除（`feature_flags` 引数 3 つ + manifest の `requires_feature` + 4 箇所の docstring）③ 現状維持（**固定して記録**） | **③ → ② の順で検討**。実測 2026-09-30: `feature_flags` は `capability_catalog.py` の定義 3 箇所と `mcp_gateway.list_tools_for_agent` の**受け口**にしか現れず、**非 `None` を渡す呼び出し元がリポジトリに 1 つも無い**（`llm_task_interpreter.py:411` と `web/ui_overview.py:1641` はどちらも引数なしで呼ぶ）。既定が `None` なので**フィルタは一度も走らない**。帰結: `requires_feature: "agents"` を持つ唯一の manifest（`ai-server/capabilities/builtin/ai-server/agent/delegate.json`）は、`settings.agents.enabled=false`（＝既定かつ現在値）でも **LLM から見える**。①は `runtime.py:1479` が既に `agent_backend=None` にしているので**冗長**かもしれない。**①②③ のどれを選んでも、`AgentSettings` の docstring・`settings/models.py:82`・`runtime.py:102`・`folder_registry.py:83` の「`requires_feature` は除外される」という記述は直す必要がある**（今は**嘘**。正しい訂正文は選んだ案で変わるので、決定後にまとめて直す）。**③ の「固定して記録」は 2026-09-30 に実施** — `tests/agents/test_agent_runtime.py`（`requires_feature` を所有する唯一のファイル）に **10 テスト**を追加（16 → 26）。記録した 4 集合（実測、`src/` 全体）: 宣言 **4** / **供給 0** / 転送 **3** / 無言の本番呼び出し **4**。検出器は `ast` で入口 4 つを走査し、位置引数とキーワード引数の両方を扱う（`list_tools_for_agent` はキーワード専用なので位置は `None`）。**`feature_flags=None` は供給ではなく省略**（既定と同じ＝フィルタ OFF）だが、**`set()` は供給**として扱う — フィルタを **ON** にして何も有効にしないので**隠す**側に働き、`None` とは意味が反対になる（両方に専用テスト）。生きた経路のテストは `ai-server.agent.delegate` が `list_for_llm()` に**見え**・`list_for_llm(feature_flags=set())` では**消え**・`AgentSettings().enabled is False` であることを同時に固定する（＝欠陥そのものを記録）。**変異 7/7 捕捉 + 方向プローブ 1/1 緑**、原ファイル 4 本はバイト単位で復元（sha256 一致）。**ただし M3（宣言を 1 つ消す変異）は assertion ではなく `SyntaxError` による collection ERROR で落ちた** — ビルドは止まるが狙った assertion は発火していないので、**弱い捕捉として記録する**（集合を直接壊す M5/M7 が本命）。ai-server **1766 → 1776 passed / 31 skipped**（実測 355.77 秒） | 今は何も止まらない（フィルタが無い＝capability は常に見える）。**止まっているのは「設定で capability を隠せる」という主張** — 文書と docstring が約束しているのに実装が伴っていない |
| **A-13** | **宣言・配管されているのに、リポジトリのどこも読まない環境変数が 4 つ**（A-12 / `AEGIS_AGENTS_ENABLED` の一般化監査） | ① 宣言を削除（`.env.example` / `docker-compose.yml` から）② 配線する ③ 現状維持（**固定して記録**） | **2 群に分けて判断**: (a) `AEGIS_PUBLIC_CORE_HOST` / `AEGIS_PUBLIC_CORE_GRPC_PORT` / `AEGIS_PUBLIC_DASHBOARD_URL` は **`.env.example` にしか出現しない**（compose もコードも参照しない）ので **① が安全**。(b) `AGORA_MASTER_USER` は compose が **ai-server コンテナへ渡している**のに読むコードが無い — **AGORA の master user が将来の機能なのか消し忘れなのかはオーナーにしか決められない**ので ① or ②。**実測 2026-09-30**: 出所から **94 名**を集めて突き合わせ、読者ゼロは**この 4 名だけ**（他はヘルパー経由 `_env_host("…")` か動的構築 `f"{prefix}_HOSTS"` で読まれている）。詳細と偽陽性の内訳は §0.1 | 今は何も止まらない。**止まっているのは「これらのつまみが効く」という読み** — `.env.example` は設定の説明書なので、効かない名前を載せると運用者が誤認する（`AEGIS_AGENTS_ENABLED` と同じ**型 6**） |

#### B. 定義が要る（挙動が動く）

| # | 問い | 選択肢 | 推奨と理由 |
|---|---|---|---|
| **B-1** | 割り込みコストの語彙（**P2-7** / B-11 / B-17） | ① コスト表の中央 2 値を入れ替える ② 自律的な結果の `expected_usefulness` / `interruption_cost` に実値を入れる ~~③ 既定値 **0.0 / 0.2 / 0.5** を 1 つに寄せる~~ **③ は撤回**（2026-09-29 実測） | **① と ② のみ**。**③ は「挙動が動かない純粋な衛生」ではなかった** — 実測すると 3 値は同じ量の 3 既定値ではない: `0.0` は**呼び出し側が指定しなかった**（`src/` の 2 サイトは両方とも明示的に渡すので**本番では一度も生成されない**）、`0.2` は**レベルがコスト表に無い**、`0.5` は**別の量**（`expected_usefulness` と比較されるルーティング側の被演算子）。寄せると**「分からない」の 3 種類が 1 つに潰れる**（§4.3 型 3）。①は**自律ループの発火間隔が動く**、②は「自律的な結果の usefulness とは何か」の定義が先 |
| **B-2** | `evaluation/` の死んだ部分グラフ（**P2-6** — 行数は §5.7 の実測を参照し、この行には書かない） | ① 削除 ② 配線 | 固定済みなので**急がない**。配線するなら期待の書き直しが製品判断（`delete_file` → `ALLOW_WITH_AUDIT` は**今は正しい**） |
| **B-3** | **自律実行経路が 2 本あり、走っているのは 1 本**（P1-5 の残り。**数の正典は §5.14 の実測**／当初は「個別メンバー 3 群」） | ① `AutonomousController` 経路を配線 ② 削除 ③ 現状維持（固定済み） | **③ で固定済み**（ピンは作成済み）。**この行の前提は実測で崩れた** — `motivation_arbiter.requires_approval` は「唯一の真に削除可能な残骸」ではなく、**その arbiter ごと到達不能な経路**（行数は §5.14 の実測）の一部だった。`ExternalTask` はリポジトリのどこでも構築されないので `decide()` の user/scheduled/event 分岐は**一度も走っていない**。①は `docs/self-development.md` の冒頭図が真になるが**製品判断**（その図が「こう動くべき」なのか「こう動いている」の書き間違いなのかはオーナーにしか決められない）、②は削除。**どちらでも落ちるピンがある**ので放置は不可。図が嘘のままなのは残る — 図の訂正だけは軽い判断 |
| **B-4** | `android_server_client.py` の安全サブシステムを移植するか | ① 移植（OTP 規則を絞る）② 移植しない | 中身は `NotificationFilter`（銀行/パスワードマネージャ/認証アプリを遮断）と `contains_password_field`。**OTP 規則 `(?<!\d)\d{4,8}(?!\d)` は 4〜8 桁を無差別に潰し、「確認コードを読み上げて」を壊す** — 移植するなら規則を絞るのが前提。**追記 2026-09-30: そのファイル自体は P1-5 で削除済み**（§5.1）なので、①を選ぶ場合は git 履歴からの復元が先（`git show ebe1506^:ai-server/src/android_server_client.py`）。**`docs/android-safety.md` は削除の事実を書かず「そのファイルに在る」と現在形で 4 箇所に書いていたので訂正した** — 登録簿側は正しかった |
| **B-5** | **北極星の残り 2 穴に着手するか** | ① 負担量の計測 ② 成長の閉路 ③ 両方 | ②は**「生産者を足す」ではなく「既存の生産者を 3 通り直す」**（**訂正 2026-09-30**、§3.1 項目 4）— 生産者は `reflection_engine.py:90` に既にあり、① 到達不能 ② `structured_data["decision"]` 未設定 ③ `related_desire` 未設定。**① を直すのは A-11 の ②（呼び出し元の配線）と同じ 1 手**なので、A-11 と一緒に決めるのが筋。①は**何を測るかの定義が先**（「どれだけ楽になったか」の指標が存在しない） |
| **B-6** | `max_autonomous_runs_per_hour` を自律ループに配線するか、削除するか（**A-1 の副産物**） | ① 配線 ② 削除 | どちらでもよいが**放置は不可** — バリデータだけが読み、設定を編集しても挙動が変わらない（`> 100` を拒否するだけ）。**同じ形の未読フィールドが既に `_UNOWNED_DEBT` にある**ので（件数は §1.1 / `AGENTS.md`）、**そちらと一緒に扱う**のが筋（単独で決めると 1 箇所だけ動く）。**B-21 で利用者側の帰結が判明**（§5.16）— 設定画面はコントロールを出しており、そのうち**一部がこの未読集合**である（個数は §5.16 の実測）。つまり**利用者は「何も変えないスイッチ」を見せられている**。`_UNOWNED_DEBT` の `sensitive_data_storage_enabled` の項が既に書いていた「何もしないプライバシースイッチは、スイッチが無いより悪い」が、そのまま現実になっている |

#### C. 方向づけ（急がない）

| # | 問い | 備考 |
|---|---|---|
| **C-1** | fresh passkey（15 分）は「最小の割り込み」として比例しているか（**P2-4**） | 未決の論点のまま |
| **C-2** | P2-5 の長期項目の優先順位 | vision のローカル化 / gRPC TLS / Room 実機プロバイダ / cross-device context / 音声 I/O / multi-user |
| **C-3** | §4.3 バグクラス集の正典をどこにするか | クラス数は **§4.3 を参照**（この行に数を書かない）。各スキルが独自に列挙している（内容のオーナーシップ）。**この行は型 9 の実例だった** — 「12」と書いてあったが §4.3 は既に 16 になっており、数を書いた側だけが動かないまま残っていた。台帳自身の設計「測定値を書かない」に反していたので、数を削除した |

| **C-4** | **Android/Kotlin を検証可能にするか、検証不能のまま受け入れるか**（**この行は §0.2 に無かった** — 冒頭の「ここが未決の*すべて*」という主張は、この行が抜けていたぶんだけ偽だった） | 実測 2026-09-30: `java` / `javac` / `adb` / `gradle` / `kotlinc` はいずれも**不在**、`JAVA_HOME` / `ANDROID_HOME` / `ANDROID_SDK_ROOT` は**未設定**、`android-server/local.properties` も無い。よって **Kotlin はコンパイル検証も実機検証もできない**。**時間の問題ではなく環境の不在**（待っても直らない）。`AGENTS.md` の Android 行は「Builds」と書いていたが、ツールチェーンが無い以上それは**測っていない記憶**なので訂正した。実機スイート `scripts/test-android-real.ps1` は**この環境では実行不能**（PowerShell が native を起動できない）で、実機 `192.168.50.41` も要る。**「JDK を入れれば直る」とは言えない** — 入れて初めて分かる。**副産物**: デバイス不要なのに `test_android_local.py` のモジュール全体スキップに巻き込まれて**一度も走っていなかった** manifest 検査を `test_manifest_schemas.py` へ移した（`pytestmark` によるスキップは `-m` の絞り込みと違い、CI にも見えない） |

| **C-5** | **テストゲートは自動化されていない — 手動スクリプトのみ。フックも CI も無い**（**この行は §0.2 に無かった**） | 実測 2026-09-30: `.github/` は**存在しない**（ワークフローも CI 設定も無い）。`.git/hooks/` は **`.sample` のみ**でフックは **0 本**。よって **`scripts/test-all-suites.ps1` は誰かが手で走らせたときだけ動く** — **単一の制約を守る egress の床（`--require-egress-tests=160`）も含めて**。**クラウド CI は単一の制約と衝突しうる**（`data/` に利用者データが入る）ので、自動化するなら**ローカルの pre-push フック**が筋。決めるのは「フックを足すか、手動のまま受け入れるか」。**あわせて `ruff` はゲートに入っていない**（両スクリプトに `ruff` / `lint` の語が無い）ので `ruff check tests/` の **202 件**は誰も止めない — 過去の「ruff clean」は**触ったファイル単位**の主張であって、リポジトリの性質ではない |

> **このレジスタ自体が型 9 の入口にならないように**: 各行が**書いてはいけないのは
> 「日付の無い現在値」だけ**です（`12` のような裸の数 — 正典は §0 / §1.1 / `AGENTS.md`。
> **C-3 がまさにこの形で腐った実例**）。**日付のある観測は書いてよい** — 表の列は
> 「推奨と**理由**」「決まらないと**何が止まるか**」「**備考**」なので、理由を支える証拠は
> この節の持ち物です。**「問い」列だけは別**で、状況を名指しするために数を伴ってよく、
> その場合は**正典へのポインタを添えます**（さもないと、その数だけが古くなる）。ここには以前
> 「各行は問いと選択肢だけを持ち、**測定値は書かない**」と書いてありましたが、**表には「推奨と理由」という列がある**ので、その字面は
> **自分の表とも自分の内容とも食い違って**いました（**規約も、対象の実測に照らすまで正しいとは
> 限らない** — 同日に B-6 の「深さ」説を実測で反証したのと同じ形）。決定が済んだ行は
> **削除する**ので、この節は**短くなる一方**であるべきです。

---

## 1. コードベース構成

### 1.1 サーバ構成

| サーバ | 言語 | ポート | 役割 | テスト |
|---|---|---|---|---|
| **AI Server** | Python 3.13/3.14 | 50051 | 中枢（LLM / 記憶 / 欲求 / 自律ループ） | **1777 passed / 30 skipped** |
| **PC Server** | Rust | 50052 | Windows 操作（TCP JSON プロトコル） | Python テスト **0**（Rust 側のみ） |
| **Browser Server** | Python | 50053 | Web 閲覧（HTTP、`ThreadingHTTPServer`） | **100 passed** |
| **Android Server** | Kotlin | 契約上 50054（実機は 50051 へ outbound） | 端末コンパニオン | 実機テストのみ（`android_local`） |
| **Room Server** | Python | 50055 | IoT / センサ | 14 passed |
| **Dashboard** | Flask + React | 8090 | Web UI / チャット / 監視 | web-ui **vitest 144** / Playwright 42 |
| **aegis-sdk-python** | Python | — | プラグイン SDK | **71 passed** |

> この表は 2026-09-29 に**全行を実測**して更新した（§5.9）。以前は 7 行中 **4 行が古い**値を持っていた
> （AI Server 1597 / Browser 62 / vitest 134 / SDK「6 failed / 17 passed」）— いずれも §0 と食い違い、
> どちらが正しいか読者には判別できなかった。**同じ量を 2 箇所に書かない**（§4.3 型 9）原則の実例。
>
> **2026-09-30 に全行を再実測**（AI Server 1777 / browser 100 / room 14 / SDK 71 / vitest 144 /
> playwright 42）。**7 行中 1 行が古くなっていた** — SDK が **48** のままで、正しい 71 は §0 と検証スキル
> §1 にしか無かった。**前回と同じ型が、前回と同じ「片方だけが動く」形で再発している**: B-14（25→48）と
> A-2（48→69）と A-2 残渣（69→71）が §0 側だけを動かし、**§1.1 と `AGENTS.md` と、当の検証スキルの
> 「測定衛生」節が追随していなかった**。日付付きの実測は不変量ではない。

### 1.2 規模

- `ai-server/src`: Python 562 ファイル、約 97,000 行（リポジトリ最大）
- `web-ui`: 11,849 ファイル（うち `node_modules` を除く実装は `src/` + `tests/`）
- `pc-server`: Rust（`src/*.rs` + `target/` のビルド成果物 2,000+）
- `protos/aegis/`: **4 ファイルのみ**（`common` / `ai_server` / `android_server` / `room_server`）。
  `android-server/app/src/main/proto/aegis/` に**バイト単位でミラー**。
  `pc-server` は protobuf を消費しない（`build.rs` なし）。

### 1.3 Capability カタログ: **128 id**

| サーバ | 件数 | 内訳 |
|---|---|---|
| pc-server | 58 | read_only 14 / low 15 / safe 22 / safe_action 4 / audited_action 1 / high 2 / **critical 0** |
| ai-server | 32 | personal_ai / memory / confirmation ほか |
| android-server | 17 | |
| browser-server | 16 | **manifest に `server_id`/`app_id` を持たず、パスから id を導出** |
| room-server | 5 | |

- マニフェストは `builtin/<server_id>/<app_id>/<action>.json` の**深さが必須**。
  `operation_category` と安全語彙 6 キーが必須（欠けると登録が拒否される）。
- 107 ファイルが `requires_approval` を持つが、これは **D5=(b) により注記専用**（判断には使わない）。

### 1.4 git 状態

```
branch: cf-grpc-and-goal-hygiene   (フラット名 — A-5 で改名済み。2026-09-30 に push 済み)
最新コミット: 本節に SHA を書かない — コミットのたびに古くなる。`git log -1 --format='%h %s'`
作業ツリー: clean（`query` は A-8 で削除済み）
stash: 0 件
リモート ref: origin/cf-grpc-and-goal-hygiene — **フラット**（2026-09-30 に移行済み。下記参照）
```

> **B-6 の機構は「入れ子名」でも「深さ」でもなかった — そして今は再現しない**（2026-09-30 実測）。
> **この日、以前の記録を反証する測定が出た**: `git update-ref` は**試したどの深さでも成功し、生存した** —
> `refs/remotes/probe2`・`refs/remotes/origin/probe-existing`・`refs/remotes/origin/probe-new/deep`
> （最後は**中間ディレクトリの新規作成を要する**）。深さの**数え方は文書ごとに揺れていた**（この行は葉を数えて
> 2/3/4、skill `aegis-verify-and-test` §1.0 は `refs/` 下のディレクトリを数えて 1/2/3）ので、
> **揺れない形＝ ref 名そのもの**で書く。`git push` は
> `refs/remotes/origin/<branch>` を正しく更新し（`f1ed4ed` → `bc6e870`）、`git fetch origin` は
> `refs/remotes/origin/HEAD` を新規作成した。**深さ説・入れ子名説・「新規ディレクトリが要る」説は
> いずれも反証**なので、**機構の主張は撤回する**。
> **失敗そのものは実在する**（`INCIDENT_2026-09-29_git-object-loss.md` に複数回。ref が rc=0 のまま消え、
> **囲むディレクトリごと**消える）が、**引き金は未特定**で、**いまは再現しない**。
> **予防だけは残す** — push / fetch の後は `refs/remotes/origin/` を確認し、`git ls-remote` を真実として
> **ファイルに直接書いて**復旧する（ref の書き込み自体が失敗する場合に備えて）:

```bash
mkdir -p .git/refs/remotes/origin
git ls-remote origin refs/heads/cf-grpc-and-goal-hygiene refs/heads/main \
  | while read -r sha ref; do printf '%s\n' "$sha" > ".git/refs/remotes/origin/${ref#refs/heads/}"; done
```

> **リモート名はフラットに移行済み**（2026-09-30 — PR が無く既定ブランチが `main` であることを確認した上で
> 入れ子のリモートブランチを削除し、フラットなブランチを `--set-upstream` で push した）。

> **未検証の手がかり（次の実測候補）**: `git fsck` は
> **`.git/logs/refs/heads/cursor/cf-grpc-and-goal-hygiene` の reflog 15 行を `invalid reflog entry`** と
> 報告する — A-5 で改名した**旧い入れ子名**の reflog が残っており、その参照先はオブジェクト消失で消えている。
> **以前の「reflog は無関係」という除外は `.git/logs/refs/remotes` を消して試したもので、この壊れた
> reflog は試していない**。あわせて `.git/refs/codex/turn-diffs`（非標準の ref 名前空間）と、
> 対応する ref の無い reflog（`dev` / `main`）が残っている。**reflog は復旧の手段なので prune しない。**

> **先行コミット数は本節に書かない。** これは**コミットのたびに増える量**で、書いた瞬間から
> 古くなる（型 9 / 型 13）。正確な値は:
> `git rev-list --count origin/cursor/cf-grpc-and-goal-hygiene..HEAD`

**2026-09-11〜09-30 の全作業はコミット済みで、2026-09-30 にリモートへ届いた**（A-7）。
`main` は 2026-07-29 で停止したままです。

> **A-7（push）は 2026-09-29 に試行して失敗し、2026-09-30 に完了した。** 前日の失敗は資格情報が
> 無かったため — `fatal: could not read Username for 'https://github.com': terminal prompts disabled`。
> オーナーが `gh auth login` を実行して解決した。**ただしこの環境では `gh auth status` は今も
> 「未ログイン」と答える** — トークンは Windows 資格情報マネージャにあり、MSYS 側の `gh` からは
> 見えないため。実際に push できたのは `GIT_ASKPASS` に一時スクリプトを指し、`gh auth token` の
> 出力を環境変数で渡したからで、**`gh auth status` の出力を可否の判定に使わないこと**。

> **本節は 2026-09-28 時点では「main より 79 コミット先行 / 508 ファイル変更が未コミット」と書いて
> いた** — 当時の記録であり、その後 P0-1 が解消した。**そして同じ罠が 2026-09-30 にもう一度起きた**:
> 上の「**未 push** なので、リモートには何も届いていません」は A-7 完了後も残っており、**解消済みの
> リスクを現行のリスクとして読ませていた**（型 9 の変種）。**節が自分自身の陳腐化を警告していても、
> その警告文は自動では適用されない。**

> **B-6**（入れ子ブランチ名で `git commit` が ref を書かない）は 2026-09-29 だけで **13 回**再発した。
> **恒久対策のフラットなブランチ名への改名は A-5 で実施済み** — 改名後のローカルコミットはすべて
> ref が正しく書かれている（実測）。**ただしリモート追跡 ref は入れ子のままなので、push / fetch の
> たびに上記の巻き添えが起きる。**

---

## 2. 主要機能（動作しているもの）

| 系統 | 状態 | 根拠 |
|---|---|---|
| **Egress Gate（唯一の制約）** | ✅ 構造的に強制 | `ai-server/src/aegis_ai/egress/{gate.py,startup.py}`、25 モジュール配線、10 実効点、`external_llm_allowed`/`web_search_allowed` 既定 False、起動時 fail-closed、CI 床 160（実測 **234 marked / 211 passed / 23 skipped**）、**mutation 証明**（壊すと 38 failed） |
| **L1/L2/L3 三層 LLM** | ✅ 完了 | `intake/l1_router.py` / `autonomous/l2_mind.py` / `llm/l3_reasoner.py`、`l1.*`/`l2.*`/`l3.*` イベント、`LLMGateway.request(layer=...)` |
| **Dashboard** | ✅ D1–D9 + L1–L6 | `web-ui/src`（Live Overlay / Agent Session 9 tabs / Timeline Gantt / Token-Cost / L1–L3 パネル） |
| **Agent runtime（OpenHands）** | ✅ Phase 1–9 完了 | `agents/runtime/` + `agents/backends/{local,openhands}/`、MCP gateway、`aegis-openhands-agent.service`、**dev-server は完全削除** |
| **確認（任意の問い）** | ✅ 5a | `aegis_ai/confirmation/`、`/api/approvals/*`、SSE、`ai-server.confirmation.{request,list}`。**実行経路はストアを参照できない**（構造的にブロックしない） |
| **強制承認ゲートの撤去** | ✅ 5b | Python / proto / Rust / Kotlin の全層で削除済み。`test_goal_change_guard.py` が再混入を固定 |
| **割り込み制御（北極星の中核）** | ✅ 完了（P1-1 + P1-6） | `InterruptionController.decide` が `net = benefit × P(receptive) − cost`（Horvitz 型期待効用）で判断し、**判断ログに内訳を載せ、報告値から符号を再計算できる**ことを assert。人間向けの面は `web-ui/src/pages/InterruptionPage.tsx`（保留内容・保留理由の表示 / 解放 / 全停止） |
| **不可逆操作の台帳** | ✅ 完了（P1-2） | `aegis_ai/irreversibility.py` + `GET /api/audit/irreversible` + **`web-ui/src/pages/IrreversibilityPage.tsx`**（テスト付き）。「事前ゲートの代替」の片肺が閉じた |
| Personal AI / Mind / Memory / Desire | ✅ | `personal_ai/` 10 モジュール、`mind/`、`memory/`、`desire/` |
| CI ゲート | ✅ | `scripts/test-ai-server.ps1`（全 suite → egress（床 160）→ mutation 検査） |

---

## 3. 未実装・未完了の部分

### 3.1 目標の核心（北極星層 — L2 の穴）

> **2026-09-29 更新**: 本節の **1・2 は P1-1 / P1-2 / P1-6 で解消済み**だったが、ここが更新されない
> まま残っていた（§0 と §P1 の表だけが追随 — **型 9**）。**残る穴は 3 と 4 の 2 つ**。

1. ~~**`interruptibility` が未実装**~~ → ✅ **解消**（P1-6 `df1bb70`）。`InterruptionController.decide`
   が `net = benefit × P(receptive) − cost` の期待効用で判断し、判断ログに内訳を載せて**報告値から
   符号を再計算できる**ことを assert する。宣言された規則（emergency_stop・例外カテゴリ・critical・
   静穏時間・proactive 不許可）は**ハードゲートのまま**でモデルを経由しないことをテストで固定。
   人間向けの面は P1-1（`768bb60`）。**残る宿題は 2 つ** — 割り込みコストの写像が 2 つに分かれている
   （**B-11**）／自律的な結果の `expected_usefulness` が定数（**B-17**）。どちらも **P2-7**。
2. ~~**事後可視化の UI が無い**~~ → ✅ **解消**（P1-2 `c0c5845`）。
   `web-ui/src/pages/IrreversibilityPage.tsx`（テスト付き）が `GET /api/audit/irreversible` を表示する。
3. **負担量の計測が無い**（**未着手**）— 「どれだけ楽になったか」を測る指標が存在しない。
   P1 / P2 のどちらにも項目が無く、**誰もスケジュールしていない**。
4. **成長フィードバックの閉路が切れている**（**未着手**）— **訂正 2026-09-30: 「生産者 0」は誤り。
   生産者は 1 つあり（`reflection_engine.py:90`、`MemoryType.APPROVAL_LESSON` を書く）、ただし
   `approval_decisions` がどこからも渡されないので到達不能**（`reflect(approval_decisions=...)` は
   src・tests のどちらからも未指定 → 常に `[]`）。**さらにその生産者は、読者が照合するキーを書かない**
   — 罰則側の読者 2 つ（`autonomous_loop.py:1362`・`motivation_arbiter.py:171`）は
   `structured_data["decision"] == "rejected"` で絞り、両方とも `related_desire=` で検索するのに、
   生産者は `related_approval_id` しか設定しない（`structured_data` も `related_desire` も既定の空）。
   **「生産者 0」という結論自体が測定の産物だった** — `decision` という*キー*で grep したので、
   そのキーを書く生産者だけを探していた。*型*（`APPROVAL_LESSON`）で探せば 1 つ見つかる。
   閉路は**「生産者が無い」のではなく「1 つの生産者が 3 通りに壊れている」**: ① 到達不能 ②
   `structured_data["decision"]` を書かない ③ `related_desire` を書かない。**① だけ直すと
   `context_builder`（型だけで絞る）には届くが、罰則側の 2 つは依然として空。**

### 3.2 機能面

| 項目 | 状態 |
|---|---|
| vision のローカル代替 | ❌ `llm.yaml` が Aliyun を指したまま。egress ゲートが止めるため**視覚機能は実質不可**（オーナー判断で「ローカル LLM は追わない」ため許容） |
| gRPC TLS | ⚠️ `security/tls_config.py` はあるが gRPC 統合が未完（Tailscale 前提） |
| Room 実機 | ❌ `UNCONFIGURED/DISABLED`（Orange Pi の実プロバイダ待ち）。`GetEnvironment` は**ハードコード fixture を返す** |
| cross-device context 共有 / 端末オフライン時の縮退 | ❌ 未着手 |
| 音声 I/O（STT/TTS） | ❌ スタブ |
| 外部メッセージング（LINE / Discord / SMTP / Webhook） | ❌ スタブ（egress ゲート配下） |
| multi-user / plugin marketplace | ❌ 未着手（v1 スコープ外） |
| Docker 全体検証 | ⚠️ compose と Dockerfile はあるがマルチサービス実機検証が未完 |

### 3.3 承認時代の残骸（棚卸し記録 — 残る判断は §0.2）

> **2026-09-29 更新 — 下の表は 2026-09-28 の棚卸し記録。** その後の P1-5 で:
> **#1 `AutonomyProfile` / #3 `dialogue/` / #4 `research/` / #9 `{room,android}_server_client.py` は
> 削除済み**（`b73309e` / `bba8ae5`、計 13 ファイル / 3,136 行。**テストは 1 件も消えていない**）。
> **#2 `permissions/` と #10 `evaluation/` は削除せず固定**（`f2948a1` / `d4aae94`）— 前者は
> **「動くゲート」**で配線すると目標に反し、後者は**未使用ではなく主張が偽**なので、消す前に記録が要る。
> **#8 `BrowserSafetyBoundary` は削除対象から外した** — 休眠しているだけで本来効くべき層で、
> **egress 半分は P1-7 で閉じた**（`a5c2cdc`）。
> **残るオーナー判断は 4 件だけ**: #2 `permissions/`（**A-6**）・#10 `evaluation/`（**B-2**）・
> `motivation_arbiter` を含む到達不能な経路（**B-3**）・`reflection_engine` の死んだ
> `approval_decisions` 引数（**A-11**）。**#6 `risk.approval_mode` と #7
> `ConfirmationStore.mark_executed/mark_failed` は下の §5.1 の実測で「消費されている」「生きた
> 契約」と判明したので判断は要らない** — この行は長く 6 件を「判断待ち」と書いていた。
> **正典は §0.2**（この行はその写しだった）。

**下の表は 2026-09-28 時点の判定**で、その後の実測で**7 面中 4 面が誤り**と判明しています（上の更新
ブロックと §5.1）。**「誰も読まない/呼ばない」を表から読み取らないでください** — 面ごとに実測が
必要で、実際 `permissions/` と `reflection_engine` は**生きたテストとランタイム経路**を持っていました。

| # | 対象 | 問題 |
|---|---|---|
| 1 | **`AutonomyProfile`（`settings/models.py`）** | **最も深刻**。`AEGISSettings.autonomy` に入るが**1 フィールドも読まれない**。しかも `captcha_bypass_forbidden` 等が自ら *"Always forbidden (structural)"* と名乗るのに**何も強制していない** = **虚偽の安全主張**。`test_ineffective_flags.py` は privacy/voice モデルしか走査しないため見逃している |
| 2 | `aegis_ai/permissions/` | 第 3 の承認面。本番呼び出し元ゼロ（テスト 2 本のみ import） |
| 3 | `aegis_ai/dialogue/` | パッケージ全体が孤児。`InteractionContext.is_approval_required` は**生産者なし** |
| 4 | `aegis_ai/research/` | パッケージ全体が孤児。削除済み id（`browser.open_page`）を呼ぶ。`docs/research-agent.md` は**存在しない `ResearchAgent` クラス**を設計の中核に据えている |
| 5 | `agents/profiles.requires_approval_for` / `motivation_arbiter` / `reflection_engine` | 承認語彙の残留 |
| 6 | `risk.approval_mode`（5 マニフェスト） | 削除済み `ApprovalType` 語彙。判断は読まないが、ダッシュボード API と override ストアから到達可能 |
| 7 | `ConfirmationStore.mark_executed()/mark_failed()` | 呼び出し元ゼロ → `executed`/`failed` は**到達不能な状態** |
| 8 | `BrowserSafetyBoundary`（browser-server） | **構築されるが一度も参照されない**（`get_actions_taken()` のみ）。`SafetyStop`/`ApprovalBoundary`/`UserInputNeeded` は宣言・catch されるが**どこからも raise されない** → `TaskStatus.STOPPED`/`NEEDS_APPROVAL` は到達不能 |
| 9 | `src/{room,android}_server_client.py` | 孤児の旧複製。`android_server_client.py` は**生きた経路に無い安全サブシステム**（通知フィルタ・認証アプリ拒否リスト）を持つ。実機側の拒否リストは `AegisNotificationListener.IGNORED_PACKAGES` の**3 パッケージのみ** |
| 10 | **`aegis_ai/evaluation/` の死んだ部分グラフ** | 7 モジュール中 **6 つ**（`metrics` / `prompt_regression` / `report` / `runner` / `safety_tests` / `scenario`、計 **1,104 行**）が**パッケージ外から参照ゼロ**（`behavioral` だけが `runtime.py:1125` から生きている）。**単に未使用なのではなく、主張が偽**になっている — `ExpectedOutcome.APPROVAL_REQUIRED` は**生産者ゼロ**（Phase 2 が唯一の分岐 `elif invoke_result.status.name == "APPROVAL_NEEDED"` を削除。`InvokeStatus` に同名の値は無い）なのに **2 ステップが今も期待**しているので**絶対に通らない**。`prompt_regression` は `== "ALLOW"` でしか違反を記録しないが、全ケースが `APPROVAL_REQUIRED`（→ `ALLOW_WITH_AUDIT`）で構築されるので**この分岐は到達不能**。詳細は §5.7 |

---

## 4. 既知の問題点（実測・裏取り済み）

### 4.1 実バグ（P0 で対応済み / 対応中）

| # | 内容 | 状態 |
|---|---|---|
| **B-1** | **`packages/aegis-sdk-python` の 6 テストが失敗** — 承認撤去に SDK が追随していない | ✅ **修正済み**（`552b69b`）。`aegis_sdk/testing.py` が `PolicyEngine.approval_store` を参照していた。**6 failed / 17 passed → 25 passed** |
| **B-2** | `pc-server.file.read` に**パス検査が無い** — `~/.ssh/id_rsa` を読める | ✅ **修正済み**（`f8293a9`）。read / write / delete / copy / move の**両端**に適用し、単一の入口 `is_protected_path()` に集約。分類器も精密化（`tokenizer.py` が `token` に誤マッチしなくなり、`.env.example` は読めるまま） |
| **B-3** | `AGENTS.md` のテスト数が実測と乖離（1528 → 実測 1550） | ✅ **修正済み**。他 suite の件数と「CI が見ているのは ai-server だけ」という事実も併記した |
| **B-4** | **`.gitignore` の穴** — egress テストが書く `ai-server/.tmp-egress-run/`（1 回あたり約 1.6k ファイル）が無視されておらず、**未追跡 1,729 件のうち 1,636 件**がこれだった。実ソース 79 件が埋もれていた | ✅ **修正済み**（`3d6ae62`）。`.workbuddy-ai/`・`.trae/` も併せて無視（既存の `.mimocode/`・`.omo/` と同じ扱い） |
| **B-5** | **18 日分が未コミット**（HEAD が 2026-09-10 で停止、stash 0 件） | ✅ **対応済み**（`495105e`）。3 コミットで取り込み済み。**中間コミットが独立して緑であることは保証していない**（検証済みは最終状態のみ） |
| **B-6** | **この環境で `git commit` が ref を書かないことがある** — コミット自体は成功し reflog に記録されるが `.git/refs/heads/<branch>` が作られず HEAD が unborn になる。⚠️ **この行の機構は 2026-09-30 に撤回した（実測で反証）** — ①「**原因を特定**」は誤り: rename が無音で失敗するという説明は**仮説**で、`update-ref`（同じ lock+rename 経路）が成功した測定がこれを弱める。**原因は未特定**。②「**入れ子名でのみ発生**」も**反証**（平坦な `refs/heads/<branch>` は入れ子の `refs/remotes/origin/<branch>` と**同時に**失われた）。③「**`git update-ref` は解決策にならない**」も**反証**（深さを問わず成功）。**残るのは予防だけ** — コミット後に `git log -1` で確認し、失敗していれば`.git/refs/heads/` を `mkdir -p` して `.git/logs/HEAD` の最終行から ref を直接書く。**正典は §1.4 と skill `aegis-verify-and-test` §1.0** | ⚠️ **回避策を確立**: コミット後に `git log -1` で必ず確認し、失敗していれば `mkdir -p .git/refs/heads` + `.git/logs/HEAD` の最終行から ref を直接書く（作業内容は無傷。今回 6 回とも復旧済み） |
| **B-7** | **設定サーフェスの 31% が誰にも読まれていない** — 12 モデル 106 フィールド中 **33 が未読**。最悪は `AutonomyProfile` で、`# Always forbidden (structural)` と書きながら**その挙動を守っているものは何も無かった**（CAPTCHA は別経路で守られているが、bulk signup は**プロンプト文にしか無い** — §4.2 B-8 で判明）。検出器 `test_ineffective_flags.py` はモデルを**手書きのリスト**（privacy / voice の 2 つ）で持っていたため、サーフェスが増えても追随せず、**この 10 フィールドを一度も見ていなかった** | ✅ **対応済み**（P1-3）。`AutonomyProfile` を削除。検出器を**モデル自動発見**に変更し、残る 22 は理由付きで `_UNOWNED_DEBT` に記録し、**「未読の集合」と「記録の集合」の一致**をテストで固定。**未走査だったモデルに死にフラグを足しても落ちる**ことを変異検査で確認。**2026-09-29 訂正**: ここは「**12 モデル / 95 フィールド**」と書いていたが、実測は当時 **11 / 94**、A-1 後は **11 / 93**。**モデル数は削除前の値**（`b73309e^` = 12 モデル / 106 フィールド、AutonomyProfile は 11 フィールド）、**フィールド数は 106 から AutonomyProfile の 11 だけを引いた手計算**で、親の `AEGISSettings.autonomy` 参照フィールドを引き忘れていた（106 − 11 − 1 = 94）。**引いて作った数は測った数ではない** |
| **B-8** | **browser-server の安全層が丸ごと休眠している** — `BrowserSafetyBoundary` は構築され `get_actions_taken()` だけが読まれるが、**`check_*` は 4 つとも `src/` から一度も呼ばれない**。`record_action()` も呼ばれないので `actions_taken` は常に空。`forbidden_actions` の `use_proxy_for_evasion` / `bulk_signup` は**プロンプト文としてのみ**届く。`except SafetyStop` / `ApprovalBoundary` / `UserInputNeeded` は**死んだ `except`**（対応する `raise` が無い）なので `STOPPED` / `NEEDS_APPROVAL` は到達不能な enum 値。さらに `test_goal_change_guard.py` は **`ai-server/src` しか走査しない**ため、browser-server 側に残る**強制ゲート（`ApprovalBoundary` / `NEEDS_APPROVAL`）が視界の外**にある。**単一制約への実害**: `check_domain`（ナビゲーション毎の egress 検査）も死んでおり、事前検査は宣言済み target しか見ない | ⚠️ **記録済み・未修正**（P1-7）。休眠を `browser-server/tests/test_safety_boundary_dormancy.py` が**発見＋等式**で固定（変異 2 種で load-bearing を証明）。配線には action 語彙の翻訳と `APPROVAL_BOUNDARIES` の扱いの判断が要る。**うち egress 半分は P1-7 で閉じた**（下記 B-9 と P1-7 行） |
| **B-9** | **egress ゲートの 2 コピーが乖離していた** — browser-server は `aegis_ai` に依存しない別ディストリビューションなので `egress.py` を自前で持つ。docstring と `docs/egress-gate.md` は「意味論は意図的に同一」と書いていたが、**実際は乖離していた**: browser 側の `_extract_host` に IPv6 リテラルの処理が無く、`is_local_destination` の単一ラベル判定に `":" not in host` のガードも無かった。結果、**同じホストが書き方で別判定**（`::1` は external、`http://[::1]/` は local）になり、`_admissible_host` と `egress_allowed` が食い違っていた | ✅ **修正済み**（`a5c2cdc`）。ai-server 側の実装を移植。**移植だけでは不十分だった**: ガードが無いまま IPv6 対応を入れると、ドットを含まない `::2`（グローバル到達可能）が**単一ラベル規則で local になる** — fail-open。両方を同時に入れて初めて閉じる。残る相違（`.lan`/`.home`/`.internal` の有無、`is_private` と明示ネットワーク）は**意図的**として `docs/egress-gate.md` に表で明記した |
| **B-10** | **この環境の `git rm -r` は要求していないファイルまで消す** — `git rm -r -q <4 パス>` は指定した 13 ファイルを index に stage したが、**作業ツリーからは `ai-server/src/` を丸ごと削除**した（419 ファイルが未 stage の削除として現れた）。指定パス以外は一切触っていない。**B-6 と同根の疑い** — この環境の git は index 更新に `rename()` を使う経路が壊れている | ✅ **復旧済み**。`git restore --source=HEAD --staged --worktree -- ai-server/src` で完全復元（内容は無傷、`git status` は元の 2 件に戻った）。**回避策**: 削除は `rm` + `git add -A -- <パス>` で行い、**`git rm -r` は使わない**。削除後は必ず `git status --short` の件数を確認する |
| **B-11** | **「割り込みやすさ」の写像が 2 箇所に別々にある** — `personal_ai/interruption.py` の `_RECEPTIVITY`（受容確率）と `autonomous_loop.py:704` の `_current_interruption_cost()`（コスト軸）が、**同じ `SituationModel.interruptibility` を別々の数値表で写像**している。値も一致しない（コスト側 suppress 0.9 / important_only 0.55 / batch_later 0.4 / interruptible 0.1 に対し、受容確率は 0.05 / 0.35 / 0.20 / 0.90 — 補数関係にもなっていない） | ⚠️ **記録済み・未修正**（P1-6 の副産物）。用途が違う（自律ループの発火判断 vs 通知の割り込み判断）ので直ちに誤りではないが、**片方を調整しても他方が追随しない**。揃えるなら「interruptibility → 割り込みやすさ」の単一の表を `SituationModel` 側に置いて両者が参照するのが筋。**今は触らない** — 自律ループの発火間隔は挙動そのもので P1-6 の範囲外 |
| **B-12** | **`FORBIDDEN_CAPABILITIES` は、それが守るフィールドとは別の id 方言で書かれている** — 39 件のうち canonical な形（`server.app.action`）は **8 件だけ**（すべて `pc-server.*`）。残り **31 件は `browser.send_email` のような「短縮 prefix + app_id なし」**。実測で **39 件すべてが `catalog.resolve()`（canonical + alias を解決する唯一の関数）で解決不能**。`validate_settings_change` は**完全一致**で比較するため、**canonical 形で書かれた同じ意図は素通りする**（実測: `per_capability["browser.send_email"]` → 1 件 / `per_capability["browser-server.social.send_email"]` → **0 件**）。守る相手の 1 つ `per_capability` は `permissions.py:89` が **canonical id** で引くので、**短縮形の 31 件は誰も使わない鍵空間を見ており、canonical な 8 件は正しい鍵空間だが存在しない capability を指している**。**今回さらに判明**: ① 生きた 128 capability のうち**禁止 action を持つものは 0 件** — つまり**今は守る相手が存在しない**（だから見えない）。② **3 つのループのうち `disabled_capabilities` のループは本体が `pass`** で、エラーを 1 件も積めない（AST で確認）— 実効は 3 中 2。③ その 2 つが拒否するのは**そもそも no-op な設定項目だけ**（短縮形の鍵はゲートに引かれない）。④ `EXPLICIT_DENY_PATTERNS` が覆うのは **39 件中 5 件**（支払いとポリシー自己改変のみ）で、残りは**別機構**が担っている（egress 系はネットワーク層の egress ゲート、FORBIDDEN を自称するものは `DEFAULT_RISK_MAP`、CAPTCHA/TOS はプロンプト）— **制約は危うくない、この一覧が危うい** | ⚠️ **記録済み・ピン済み・未修正**（`tests/test_forbidden_capabilities_dialect.py`、7 関数 / 13 ケース、**変異 6/6 捕捉**）。ピンは方言構成・解決不能性・素通りする witness・`pass` ループ・ゲートの鍵の形・パターン被覆を**等式と実測**で固定する。**この測定は「修復」ではなく「削除」に傾く** — 守る相手が 0 件、3 ループ中 2 つが無効、名前は何も指していない。**2026-09-29 に「削除」で決着した**（A-1）。削除したものは 39 件の一覧とそれを参照する 3 ループ、`CapabilityPermissions.allowlist`、`config/settings.json` の `"allowlist": []`。ピンは `tests/test_forbidden_capabilities_stay_retired.py`（11 ケース、**変異 14/14 捕捉**）に置換 — **「定数が消えた」だけでは弱い**（システムを弱めれば満たされる）ので、実物の `ToolBroker` が未登録 id を `NOT_FOUND`（ポリシー評価の**前**）で拒否すること、生きたゲートが `capability.id` を鍵にすること、`EXPLICIT_DENY_PATTERNS` が支払い・egress 迂回・ポリシー自己改変の 3 意図群に今も一致することを併せて固定する。`docs/permissions.md` / `pc-safety.md` / `android-safety.md` / `dev-safety.md` も訂正済み |
| **B-13** | **`CapabilityPermissions.allowlist` を消費する者がいない** — 説明は「Capability IDs explicitly allowed (**bypass other checks**)」だが、`settings/permissions.py` が読むのは `disabled_capabilities`（:47）・`denylist`（:56）・`per_capability`（:89）の 3 つだけで、**`allowlist` を読む決定は存在しない**。唯一の参照は `validate_settings_change` 自身（＝自分を検閲するためだけに読む）。**検出器がこれを見逃す理由も特定**: `test_ineffective_flags.py` の `_readers()` は **src 内の識別子テキスト一致**なので、「バリデータが検査のために属性に触れる」を**読者として数えてしまう** | ⚠️ **記録済み・検出器で固定**。`tests/test_guarded_settings_fields.py` が「**バリデータが守るフィールドは、バリデータの外に消費者を持つこと**」を assert する（守られる集合は `validation.py` を AST で解析、消費者は `src/` を走査して発見、現在の穴は理由付きで記録し、**観測と記録の一致を等式で固定**）。変異 5 種すべて捕捉 — 新たに守られたのに消費者がいないフィールド / 記録の削除 / 消費者が付いたのに記録が残る / 走査が誤った属性形を読む / バリデータが守るのをやめる。B-12 と同じ面。オーナー境界の観点では**機能しなかった承認機構の残骸**だったので、**A-1（2026-09-29）で `allowlist` を削除**し、`FORBIDDEN_CAPABILITIES` の 3 ループも同時に消えた。**検出器は守る対象を `*.capabilities.<field>` から全設定セクションへ拡張され、その場で 2 件目の生きた欠陥を発見した** — `max_autonomous_runs_per_hour` はバリデータだけに読まれ、他に消費者がいない（自律ループはハードコードされた予算で動く）。**既存の死にフラグ検出器が見逃していた**のは、識別子走査がバリデータを「読者」と数えるため — 2 つの検出器が同じフィールドに別の答えを返すのはこの理由で、効果について正しいのはこちら。`_RECORDED_GAPS` に記録し、§0.2 の B に追加した |
| **B-14** | **SDK では第三者サーバの capability を作れない** — `define_capability(server_prefix="weather", ...)` は **`capability.py` 自身の docstring にある例**だが、`Capability.id` の `pattern`（`models.py:124`）が prefix を **12 種（6 サーバ × 長短）に固定**しているため **pydantic ValidationError で落ちる**（実測）。しかも **SDK 自身の検証器はこれを通す**（`safety.py:98` の `^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$` は任意 prefix を許容）＝**2 つの検証器が矛盾**し、しかも**両方向**に食い違う: SDK は `weather.` を通して `ai-server.` を弾き（`-` が文字クラスに無い）、スキーマはその逆。**加えて `define_capability` は `server_type` を既定 `DEV` のまま prefix から導出しない**ので、既定引数で通る prefix は **`dev` ただ 1 つ** — つまり **Phase 9 で削除したサーバの身元を借りたときだけ通る**（実測）。`docs/plugin-sdk.md` の Quick Start・`capability.py` の docstring・`examples/example-weather-server`（**import すら通らない**）・`tools/create-capability-server` が生成する `server_prefix="{prefix}"` がすべて同じ穴に落ちる。**SDK のテストが緑なのは、既存 11 件すべてが `dev` を名乗っているから** | ✅ **解決済み**（2026-09-29、A-2 ②、§5.18）— 二択のうち **「SDK が第三者 prefix を明示的に断る」** を選んだ。`safety.py` は自前の regex を捨てて `aegis_schema.models.CAPABILITY_ID_PATTERN` を **import** する（規則が 1 つになる）。`define_capability` は `server_type` を prefix から**導出**する（既定 `None`、引数で矛盾を渡すと拒否）。docstring の例・同梱 example・scaffold の生成物は**説明ではなく実行**で検証される。ピンは「食い違い」から「契約」へ**張り替えた**（`tests/test_capability_id_contract.py`、**変異 5/5 捕捉**）。上の記述は**修正前**の状態 |
| **B-15** | **サーバ名簿が 15 箇所に複製されていた**（11 ファイル、値の型は 5 種: `ServerType` / 短縮 prefix / 有効フラグ / id prefix / host:port。AST で計測）。うち **5 箇所が削除済み `dev-server` を今も列挙**していた（`capability_catalog.py:70`・`:379`、`models.py:215`、`permissions.py:66`、`ui_overview.py:3388`）。**「dev-server 残骸」の実体はこれ** — 個別の消し忘れではなく、**名簿に単一の定義が無いこと**の症状。**ただし実装前の測定で前提が 2 つ崩れた**: ① `server_id → ServerType` の写像は **5 コピー**あり、うち **2 つは既に食い違っていた**（`tool_broker.py` は `dev-server` を持たず、`capability_catalog.py` は持っていた）— 「5 箇所を直す」ではなく「5 コピーが 1 つになる」。② 15 箇所のうち **3 箇所は名簿ではない** — `situation.py:51/189/204` は**状況ソース**の語彙で、`ai-server` を `"webhook"` に写し、`:189` は `"status."`（サーバですらない）を含む。**キーが同じだけの別物**。`alert_manager.py` の 4 サーバも意図的（**サーバは自分を健康診断できない**） | ✅ **解消済み（`952caaa`、2026-09-29）** — `aegis_schema/roster.py` が単一の定義。6 サイト（`capability_catalog.py` ×2 / `prompt_regression.py` / `dashboard_legacy.py` / `models.py` / `tool_broker.py`）が import する。**6 つの写像すべて HEAD と値が同一**であることを確認（＝純粋なリファクタ）。退職サーバは `RETIRED_SERVER_ROSTER` に **1 回だけ**書き、`**` 展開で 3 サイトに折り込む（`dev-server` を綴るモジュールは 6 → 3）。名簿リテラルは **15 → 10 箇所 / 11 → 7 ファイル**、記録ドリフトは **5 → 2 サイト**。検出器は事実の移動に追随させた（`_id_consistency_map()` は AST のローカルではなく名簿を読む。失った「dict リテラルは 1 つ」ガードは、それが守っていた不変量 `test_the_validator_names_no_server_of_its_own` に置き換え）。**測定で 2 つのアサーションを撤回した** — ① `PREFIX_BY_ID` と `_PREFIX_MAP` の比較は**両辺が同じ tuple 由来**なので絶対に落ちない（変異 `room → rm` で緑のままだった）。短縮 prefix は代わりに **id 許可リスト**（別の宣言）と突き合わせる。② manifest の `server_id` と id prefix の比較も同じ理由で無効（`folder_registry` が両方を**パスから**導出し、JSON とパスの不一致は `list_all()` に届く前に**拒否**される）。真の不変量「拒否が 0 件」は既に `test_manifest_schemas.py` が固定している。**変異 12/12 捕捉**（各変異が期待どおりのテストで落ちることを観測、原ファイルはバイト単位で復元） |
| **B-16** | **3 つ目の承認サーフェスが「動くゲート」として休眠している** — `aegis_ai/permissions/`（4 モジュール）は `{"decision": "ask_approval", "requires_approval": True}` を返す**完成した強制ゲート**。`_category_default()` は `MEDIUM_RISK_WRITE` / `HIGH_RISK_EXTERNAL_EFFECT` / `DESTRUCTIVE` / `FINANCIAL_OR_LEGAL` の 4 分類に `ask_approval` を返し、**最終フォールバックも `ask_approval`**（未知の操作は保守側に倒れる）。`ServicePermissionStore` は `default_*` の purchase/payment スコープを**読み込み時に `requires_approval = True` に永続化**する（`:318-324`）。**パッケージ外からの import は 0 件**（`src/` 全体を AST 走査。他のヒットは gitignore 済みの `.aegis-local/` スナップショットのみ）。B-8（browser-server の休眠安全層）と同型だが、**より危険なのは「動く」こと**: `tests/test_goal_alignment.py` と `test_mission_contract_acceptance.py` がゲート意味論を assert して緑なので、**配線すると「よく支えられている」ように見える** | ⚠️ **記録済み・固定**（P1-5 後半）。`test_forced_gate_stays_retired.py` を 3 サーフェス目に拡張 — 実行経路 7 モジュールが import しないこと（parametrize）、**パッケージ自身だけが import する**こと（非空性 assert ＋ 観測集合と記録集合の一致）、そして**なぜ配線してはならないか**（今も `ask_approval` を返すこと）を記録。**変異 4 種すべて捕捉**（実行経路への import 追加 / 非実行経路への追加 / prefix 一致を等価に狭める / `MEDIUM_RISK_WRITE` を `allow` にする）。**削除ではなく固定を選んだ** — 削除するか配線するかはオーナー判断（配線は目標に反する） |
| **B-17** | **`PresentationRoutingPolicy` の「割り込む価値があるか」判定が定数になっている** — 最後の判定は `should_interrupt = important and not occupied and context.expected_usefulness >= context.interruption_cost`。第 3 項の 2 つの被演算子は `autonomous_loop.py:3065-3066` が**同じ既定値**で埋める（`float(task.get(..., 0.5) or 0.5)` が両方）が、**リポジトリのどこもその 2 つのキーを task に書かない**（`src/` 全体の dict リテラル走査で、書き込みは `_present_autonomous_result` 内の**プレゼンテーション payload への転記 2 箇所だけ** — task 構築側ではない）。したがって比較は常に `0.5 >= 0.5` = **真**で、`should_interrupt` は実質 `important and not occupied` に退化する。**生きた経路**（`routing_policy.py:78`）の欠陥で、死んだモジュールの話ではない。フィールド自体は生きている（`expected_usefulness` を 0.4 に下げると判定は反転する）= **既定値が答えを決めている**。加えて `>=` は等しい既定値どうしで**割り込む側に倒れる**。さらに同名フィールドが**3 つの既定値**を持つ — `ActionCandidate` は **0.0**、コスト表のフォールバックは **0.2**、`PresentationRoutingContext` は **0.5**（`0.0` は `src/` では生成されず、テストだけが到達する。§5.8 の訂正を参照） | ⚠️ **記録済み・固定**（`d4aae94` の副産物）。ピン `tests/test_interruption_cost_vocabulary.py`（8 テスト、**変異 8/8 捕捉**）。修正は「自律的な結果の usefulness とは何か」の設計判断なのでオーナー案件 |
| **B-18** | **`Capability.id_server_type_consistency` は `server_type=UNSPECIFIED` を宣言すると検査を丸ごと飛ばす** — `prefix_map.get(self.server_type)` に**既定値が無く**、`ServerType` 7 メンバー中 **6 つしか map に無い**（欠けているのは `UNSPECIFIED`）。したがって `.get()` は `None` を返し、続く `if expected_prefixes and not any(...)` が**偽**になって id とサーバ種別の整合検査が走らない。**実測**: `room-server.room.foo` + `server_type=PC` → **整合検査で拒否**、**同じ id + `server_type=UNSPECIFIED` → 構築成功**。つまり**情報を *足さない* ことが検査を無効化する**（`UNSPECIFIED` は enum の第 1 メンバーで、`server_type` は必須フィールドなので「明示的に 0 を渡す」だけで起きる）。**この欠陥は検出器自身の docstring が 2 年以上前から記述していたが、主張が 2 重に誤っていた** — ①「`ServerType.DEV` の capability はどの id でも通る」と書いてあるが **`DEV` は map にある**（`room-server.*` の id は正しく拒否される）。欠けているのは `UNSPECIFIED`。② 記述だけで**アサーションが 1 つも無く**、既定値がどちらに倒れても誰も気づかなかった | ⚠️ **記録済み・固定**（`ec15484`。**A-3 の `952caaa` で発見先を更新**）。`tests/test_server_roster.py` に 11 テストを追加 — map は**当初 `models.py` の AST から**読んでいた（ローカル変数で import 不可だったため）が、**A-3 で名簿が import 可能になったので読み先を `aegis_schema.roster` へ移した**（事実の移動に検出器を追随させる。失った「dict リテラルは 1 つ」ガードは、それが守っていた不変量「validator 本体にサーバ名の文字列定数が無いこと」で置き換え）。`ServerType` は enum から、`permissions.py` の map キーとフォールバックは**今も** AST から**発見**する。飛ばされるメンバー集合は**等式で固定**し、**全メンバーを挙動で**検証する（mapped なら他人の id を拒否／unmapped なら受理）。**変異 6/6 捕捉**（既定値を fail-closed に反転 / `UNSPECIFIED` を map に追加 / `DEV` を削除 / pattern が通すキーを削除 / **呼び出し側を改名して発見を盲目化** / **unmapped のフォールバックを fail-closed 化**）。ai-server **1714 passed / 31 skipped**（1703 + 11） |
| **B-19** | **`settings/permissions.py` のサーバ有効ゲートは「不明な prefix = 有効」に倒れる** — `server_enabled_map.get(server_prefix, True)` の**既定値が `True`** なので、map に無い prefix は「そのサーバは有効」と読まれ、**無効化ゲートが発火しない**。ゲートとしては**誤った側**の既定値。**現時点では到達不能**（id の pattern が許す prefix は閉集合で、**その全てが map のキー**）だが、(a) B-14 で pattern を緩めれば即座に到達可能になり、(b) map からキーを 1 つ落とすだけでも到達可能になる。`test_server_roster.py` の docstring はこれも記述していたが**アサーションは無かった** | ⚠️ **記録済み・固定**（`ec15484`）。既定値の**側**を AST で読み `True` として記録（fail-closed に変われば失敗する＝改善として記録を更新する）。さらに「**pattern が通す prefix は全て map にある**」を等式で assert するので、**フォールバックが到達可能になった瞬間に失敗する**（B-14 を修正する人が必ず踏む）。修正は B-15 の名簿一本化と同じ判断 |

### 4.2 文書の陳腐化（構造的）

- ~~**`docs/status.md`（2026-06-30 で更新停止）**、**`docs/implementation-status.md` / `docs/backlog.md` / `docs/roadmap.md`（2026-06-17 で停止）**~~ → ✅ **統合済み（P2-1）**: 4 本を `docs/status.md` **1 本**に寄せた（61 → 58 ファイル）。元の 4 本が持っていた誤り:
  - テスト総数 **157** と記載（実測 **1678**）
  - **削除済みの `ApprovalManager` / `ApprovalFanout` を「✅ Done」**と記載（`aegis_ai/approval/` は存在しない）
  - `aegis_ai/research/` と `agents/self_dev.py` を「Done」（実体は孤児 / `SelfDevAgent` はクラスですらない）
  - 「Safety Defaults: 外部送信・削除・支払いは approval-required」＝**新目標と矛盾する記述**
  - `docs/implementation-status.md` の「Total: 157」表は各内訳の合計とも一致しない
  - 「正典」だと宣言していた `data/reports/production_readiness.json` は**そもそも存在しない**（監査が書くのは `readiness_summary.json`）
  - **再発防止**: 新しい `docs/status.md` は**測定値を一切持たない**（構造と意図だけを書き、数値は `PROJECT_STATUS_REVIEW.md` と `AGENTS.md` を指す）。これで「同じ量が 2 箇所」という型 9 の入口そのものを塞いだ
- **`docs/architecture.md` は「現在のコードで検証済み」と宣言しながら、1 ファイル内で自己矛盾していた**（✅ **修正済み**）:
  - 冒頭が「Status: Implemented (**verified against current code snapshot**)」「Tests: **157** passed」「Capabilities: **53** registered」と宣言する一方、**同じファイルの末尾の状態表は「128 capabilities」「58 capabilities（PC）」「1550 tests passing」**、図の中は 53、ディレクトリツリーのコメントは 157 だった
  - **同じ量が 1 ファイル内で 2 つの値を持つ**ので、読者はどちらも信じられない。実測は **capabilities 128**（pc 58 / ai 32 / android 17 / browser 16 / room 5）・**ai-server 1714 passed / 31 skipped**（2026-09-29 実測）
  - 8 箇所を実測値に統一し、冒頭の「検証済み」宣言を「**数値は日付付きの実測であり不変量ではない**」に置換
  - 残る複製は `roadmap.md`（3 箇所）・`backlog.md`（1 箇所）だったが、**P2-1 で 4 本とも `docs/status.md` に統合済み**（上の項）。`BUG_REPORT.md` の古い合計（1,456 等）は**調査日が明記された時点記録**なので対象外。`.omo/` は gitignore 済み
  - **検出器は作っていない** — 「同じ量」のスコープ判定（PC の 58 と全体の 128）が曖昧で偽陽性になるため。**トリアージを要するテストは無いより悪い**（§4.3 の規則）。**代わりに P2-1 の統合で、新しい `docs/status.md` から測定値を全部抜いた** — 検出器を書くより、複製を作らないほうが確実
- ~~`docs/status.md` は `implementation-status.md` と**ほぼ同名・同内容**で二重管理になっている。~~ → ✅ **解消**（P2-1 の統合で `implementation-status.md` を削除）
- **`.aegis-local/deploy-approval-fix/`・`.aegis-local/deploy-observe/`** に、削除済み `ApprovalStore` / `PolicyEngine(approval_store=...)` を含む**古いスナップショットが残存**（`.gitignore` 済みだがディスク上に残っている）。
- リポジトリ直下の `query`（10 バイト、内容は `GIOV3`）は誤リダイレクトの残骸。**コミットからは除外した**（削除はしていない）。

### 4.3 構造的バグクラス（再発しやすい型）

このプロジェクトは次の型を繰り返し踏んでいます。今後も同じ型が出ます。

1. **宣言されているが効いていない**（旧 `AutonomyProfile`、旧 `requires_approval`）— **設定サーフェス全体で 31% が未読だった（B-7）。** この型は「フラグを 1 つ足す」ほうが「配線する」より常に安いために増える。したがって対策は個別修正ではなく**検出器の網羅**であり、`test_ineffective_flags.py` をモデル自動発見に変えたのはそのため
2. **読み手はいるが生産者がいない**（`executed`/`failed`）— **`approval_lesson` はこの型の実例ではなかった（訂正 2026-09-30）**: 生産者は 1 つあり（`reflection_engine.py:90`）、**到達不能なうえに、読者が照合するキーを書かない**（§3.1 項目 4）。**「生産者がいない」と「生産者がいるのに契約が合っていない」は別の型**で、後者のほうが厄介 — ペアが端から端まで一度も実行されないので、**どちらの側も相手に合わせる必要が無く、独立にドリフトできる**。「生産者 0」という判定も*キー*（`decision`）で探した産物だった。**数える前に、何を数えているのかを確かめる**
3. **構築されるが参照されない**（`BrowserSafetyBoundary`）— **その変種が最も危険**: **動いてテストも緑なのに誰も呼ばない**強制ゲート（`aegis_ai/permissions/`、B-16）。「未完成だから休眠している」のではなく「**完成しているのに休眠している**」ので、**配線が改善に見える**。判定は**呼び出し側を grep する**ことで、宣言やそのモジュール自身のテストでは分からない（B-16 のゲートは自前のテストで `ask_approval` と `fail safe` を assert している）
4. **死んだ `except` は死んだ `raise` を意味する**（`SafetyStop` 等）
5. **正規化の既定値が危険側に倒れる**（`audited_action` が `READ_ONLY` に黙って落ち、12 ケイパビリティが監査なしで実行されていた → 2026-09-28 修正済み）
6. **文書が「ゲートがある」と読める**（削除より危険。プロンプト・マニフェスト・docstring・起動バナーも対象）
7. **検出器の「読者」定義が甘い** — 「属性に触れている」を読者と数えるため、**検査されるが消費されない**フィールドが素通りする（B-13）。型 1 の検出器自身が型 1 を見逃すので、検出器を書いたら**その検出器の盲点を探す**
8. **同じ名簿・同じ写像が多数のコピーに散る** — 1 箇所直しても他が追随しない（B-11 の 2 つの割り込み写像、B-15 のサーバ名簿）。**「残骸が消し忘れられている」と見えたら、まず名簿の単一性を疑う**。B-15 は **A-3 で解消**（`952caaa`）。ただし**実測で数え方が 2 つ崩れた**: 「15 箇所」のうち **3 箇所は同じ鍵を持つ*別の語彙***（`situation.py` は `ai-server → "webhook"` と写す状況ソースの表で、`"status."`＝サーバですらない値も持つ）、「同じ写像の 5 コピー」のうち **2 つは既に食い違っていた**。**コピーを数えるときは、値の型ではなく *写像の向きと余域* で数える** — 同じ `server_id → X` でも X が違えば別の事実である
9. **同じ量を 1 つの成果物の中で 2 回書くと、必ず自己矛盾する** — `docs/architecture.md` は冒頭で「53 capabilities / 157 passed」、**同じファイルの**末尾の状態表で「128 capabilities / 1550 passed」と書いていた（✅ 修正済み）。片方だけ更新されるので、**読者はどちらも信じられなくなる**。対策は「測定値を書き写さない」か「**日付付きで書き、不変量ではないと明示する**」のどちらか。**「現在のコードで検証済み」という日付の無い宣言は、この型の入口**（`BUG_REPORT.md` が無事なのは調査日が明記されているから）
10. **死んだコードの中の偽の主張は、テストでは捕まらない** — `aegis_schema/validation.py` は **128 件すべて**の capability に「tags に `risk:<level>` を入れよ（**Policy Engine のフィルタリングのため**）」と警告していたが、**capability を risk タグで絞る機構は存在しない**（✅ 削除済み）。**走らないコードは振る舞いを持たない**ので、テストは何も言えない。したがって**削除する前に中身を読む** — 消すだけでは、同じ偽の主張が別の場所で再生される。あわせて **100% の入力で発火する警告は警告ではない**: 配線すれば 128 件の雑音になるだけで、**「配線しても何も得られない」ことは `0 errors / 133 warnings` を実測して初めて分かる**
11. **誰も走らせない成果物は検証されない** — `examples/example-weather-server` は **import すら通らない**状態で出荷されていたが、**テストもスクリプトも CI もこのファイルを参照していなかった**ので誰も気づかなかった（B-14）。同梱の example・scaffold（`tools/create-capability-server`）が生成するテンプレート・`tools/` 配下は「動くはず」と思われているが、**走らせる者がいなければ 1 行目から壊れていても緑のまま**である。型 8（スイートが走っていない、P2-0）の兄弟で、こちらは**コードではなく成果物**についての話。**「参照されているか」ではなく「実行されているか」を問う**。**（2026-09-29 追記）この型の実例だった 2 つは、いま SDK のピンが実際に import して実行する**（`test_capability_id_contract.py` の `test_the_shipped_example_server_runs_end_to_end` は example を登録・呼び出しまで通し、`test_the_scaffold_generates_a_server_that_builds` は scaffold を生成して生成物を import する）。**型そのものは残る** — `tools/` の他のスクリプトと `web-ui` の Playwright はまだ誰も走らせていない
12. **検査は在るが、報告できない** — ガードが存在し、呼ばれ、実行されるのに、**1 件も指摘を出せない**。3 つの形を実測した（B-12・B-19）: ① **本体が `pass`** — `validate_settings_change` の 3 ループのうち 1 つは `if … in FORBIDDEN_CAPABILITIES: pass` で、条件が真でも何も積まない（実効 3 中 2）。② **誰も使わない語彙と比較する** — 一覧の 39 件は短縮 prefix、ゲートが引く鍵は canonical なので、**同じ意図を正しい綴りで書くと素通りする**（`browser.send_email` → 1 件 / `browser-server.social.send_email` → 0 件）。③ **フォールバックが緩い側** — `server_enabled_map.get(prefix, True)` は不明な prefix を「有効」と読む（B-19）。**型 1（宣言されているが効いていない）の検査版**で、判定は「ガードがあるか」ではなく「**このガードはどの入力で発火するか**」— 実測で **witness を 1 件作って発火させる**。発火しない witness しか作れないなら、それはガードではなく**装飾**である。**発火しないガードは、削除の判断が済んだら消す** — ①〜③ のうち ①② は A-1 で削除済み（§5.13）
13. **測らずに差分で作った数は、測定値ではない** — §4.1 の B-7 は「**12 モデル / 95 フィールド**」と書いていたが、実測は当時 **11 / 94**。**モデル数は削除前の値をそのまま残し**（`AutonomyProfile` の削除後も 12 のまま）、**フィールド数は 106 からその 11 だけを引いた手計算**で、親の `AEGISSettings.autonomy` という**参照フィールド 1 つを引き忘れていた**（106 − 11 − 1 = 94）。型 9 の変種だが**機構が違う** — 型 9 は「同じ量を 2 箇所に書く」、こちらは「**1 箇所にしか書いていないが、書く前に測っていない**」。したがって「同じ量を 2 回書くな」では防げず、**編集の前に必ず走らせる**しかない。**差分の算式を書くなら、その差分の根拠も測る**
14. **検査に見えて検査でない（恒真のアサーション）** — 比較の**両辺が同じ出所から導出**されていると、その assert は**絶対に落ちない**。A-3 の実装中に **2 件**書いてしまい、**どちらも変異を当てた瞬間に発覚**した: ① `PREFIX_BY_ID == {s: _PREFIX_MAP[s] for s in SERVER_IDS}` — `_PREFIX_MAP` は `PREFIX_BY_ID` から**導出**されるので、短縮 prefix を `room → rm` に壊しても**両辺が一緒に動いて緑**。② 「manifest の `server_id` と id prefix が一致すること」— `folder_registry._derive_ids` が `server_id` を**パスから**取り、`capability_id` も**同じ dict から**組み立てるので**構造上**一致する。**判定法は「その assert を落とすには、どのファイルの何を変えればよいか 1 つ挙げられるか」**。挙げられないなら検査ではなく**検査の形をした恒真式**である。**変異は「テストが load-bearing か」ではなく「アサーションが load-bearing か」を測る道具**なので、テストを書いたら**その場で必ず 1 つ当てる**（この 2 件は §5.2 の追記のとおり撤回し、スタブとして残さなかった）。なお ② の真の不変量（manifest の**拒否が 0 件**）は**別ファイルで既に固定済み**だった — **重複した落ちないテストを足すことは、検査を増やすことではなく負債を増やすこと**である
15. **到達性は推移する — 1 ホップの関係を数えて「到達可能」と呼ぶと、死んだ経路が生きて見える**（B-3） — §5.1 の `motivation_arbiter` 行は「**❌ 生** — `autonomous_controller.py` が import している」と書いていた。import は**事実**だが、**その importer 自身が import 元ゼロ**である。**「このモジュールを名指しするものがあるか」と「このモジュールは実行されるか」は別の問い**で、前者は推移しない。`AutonomousController` 経路（約 700 行）は `docs/self-development.md` の冒頭図に**入口として描かれている**のに、実測の入口は `runtime.py:1586` が直接構築する `AutonomousLoop`。**この型は 3（構築されるが参照されない）を隠す** — 死んだ経路の上のコードは「呼び出し元がある」ように見えるので、登録簿そのものが生存を主張してしまう。**同じ誤りは逆方向にも出る**: 最初の走査は「**パッケージ外から** import されているか」だけを問い、**5 つ**を到達不能と報告したが、`planner`（`autonomous_loop` 経由）・`l2_mind`・`l2_models`（パッケージ `__init__` 経由）は到達可能で、正解は **2 つ**だった。**判定法は「根を 1 つ名指しし、そこまでの連鎖を示す」** — 根とは実際に走るもの（`runtime.py`、テスト、CLI）である。ピンはホップではなく**連鎖**を assert する（`tests/test_autonomous_execution_path_is_single.py`）
16. **宣言は「構築」でしか検査されない — 生きた書き込み経路が構築せず代入するなら、宣言は系の半分しか縛らない**（B-20） — 設定スキーマは **27 フィールド**に `ge`/`le` の境界を宣言しており、それらは**構築時**に強制される。しかし生きたプロセスの唯一の書き込み経路 `SettingsStore.update_section` は、提案設定を **`setattr` で無検証に組み立てて**から `validate_settings_change` を呼ぶ。そしてそのバリデータが再検査する境界は **1 つだけ**（`max_autonomous_runs_per_hour > 100` — しかもそのフィールド自身の `le=100` の**写し**で、構築時に拒否される値をもう一度弾いているだけ）。**結果、27 のうち 26 が API 経由で突破でき、値はディスクに残る**（すべて実測 — 実物の `SettingsStore` を `tmp_path` に対して駆動し、読み戻して確認）。**この型は 2（真実源が 2 つ）と 12（検査は在るが発火しない）の合成**だが、機構が違う: 検査は**存在し、発火もする**（1 フィールドについて）。欠けているのは**範囲**である。判定法は「**この制約は、どの経路で強制されているか**」— 宣言・構築・書き込みの 3 つを別々に問い、**書き込み経路を実際に駆動して**確かめる。なお、この形は**上書きを許すフィールドだけ**が対象で、`getattr(obj, "name")` のように**文字列で名前を渡す**アクセスは属性ベースの検出器から見えない（今回 3 度目の偽陰性）— 発見器は属性と文字列の両方を見る必要がある。**A-9 で修復済み（2026-09-29）** — 生きた書き込み経路が**構築**するようになり、27 の境界すべてが書き込み時点で強制される（実測 **突破 0 / 阻止 27**）。この型の要点は残る: **宣言・構築・書き込みの 3 つを別々に問い、書き込み経路を実際に駆動して確かめる**。なお**唯一の手書きの写し**（`validate_settings_change` の `> 100`）は**残した** — 構築が先に拒否するので**ストア経由では到達不能**になったが、この関数は public（`settings/__init__.py` が再輸出）で契約が独立しており、消すと `tests/test_guarded_settings_fields.py` が記録している**唯一の実例**が消えるため。この判断はピンとソースのコメントに明記した（**「残した」理由も記録しないと、次に読む者は「気づかなかった」と読む**）
17. **名簿の誤りは鳴るが、順位の誤りは鳴らない**（B-21） — `web-ui/src/pages/Settings.tsx` の `editableSettings` は 2 つの集合を持つ。**どのコントロールを出すか**は `GET /api/settings` のペイロードから**発見**するので、スキーマが変わっても古くならない（UI 側に名簿が存在しない）。しかし**どれを先頭に出すか**は 15 件の**手書きの `preferred`** で、そのうち **5 件はどの設定フィールドとも一致しない**（`display_privacy_mode` / `notifications_enabled` / `daily_budget_usd` / `monthly_budget_usd` は `web-ui` にしか存在せず、`memory_budget_tokens` は `context_builder` の実行時属性）。**これが無音なのは機構が違うからである** — 名簿の欠落は**引く側が落ちる**（capability が見つからない → `NOT_FOUND`）、順位の欠落は**引く側が黙って既定を返す**（`Set.has` が false → 並び順が変わらないだけ）。**同じファイルの中で、同じ「手書きの一覧」が片方だけ無音で腐る。** 判定法は「**この一覧の要素が何も指さなかったとき、何が起きるか**」— 例外か、`false` か、既定値か。`false` や既定値なら、それは検証されていない。型 5・型 12 の親戚だが**検査が存在しない**点が違う — 比較すべき相手（スキーマ）は存在するのに、**誰も比較していなかった**。あわせて**発見方式そのものの副作用**も実測した: 可視集合は `result.length >= 24` の切り捨てと `slice(0, 32)` で決まるので、**フィールドの宣言位置が「利用者に見えるか」を決める** — 早い位置に 2 つ足すと**記録済みの死んだフィールドが 1 つ可視窓から押し出される**（変異 M11 で実測）。誰も記録を触っていないのに、設定画面の中身が変わる

---

## 5. 優先順位付きアクションリスト

### P0 — 完了（作業喪失と誤トリアージの防止）

| # | アクション | 状態 |
|---|---|---|
| **P0-1** | **未コミット 18 日分をコミットする** | ✅ **完了**。`3d6ae62`（.gitignore 衛生）→ `552b69b`（SDK 修正）→ `495105e`（本命 579 ファイル）。branch `cursor/cf-grpc-and-goal-hygiene` は origin より **50 超先行**。**未 push**。中間コミットの独立した緑は保証しない |
| **P0-2** | **`aegis-sdk-python` の 6 テストを修復** | ✅ **完了**（`552b69b`）。25 passed。`PolicyDecision` 全メンバーがマッピングにあることを要求するガードと、未知の decision を報告するガードを追加（変異検査済み: 1 エントリ削ると 2 件落ちる）。**CI への SDK 組み込みは未対応** |
| **P0-3** | **`AGENTS.md` の数値を実測に合わせる** | ✅ **完了**。**1597 passed / 31 skipped**（うち 22 skip は `_UNOWNED_DEBT` に記録した負債そのもの）に更新し、他 suite（room 14 / browser 62 / SDK 25 / vitest 144 / playwright 42）と「CI が見ているのは ai-server のみ」を明記 |

> 復旧コマンド: この 3 コミットを取り消す場合は `git reset --soft 4373afb`（作業内容は作業ツリーに戻る）。
> ただし**この環境では `git commit` 後に ref が書かれないことがある**（§4.1 B-6）。コミット後は必ず
> `git log -1` を確認すること。

### P1 — 目標の中核（北極星層の最後の一マイル）

| # | アクション | 理由 | 状態 |
|---|---|---|---|
| **P1-1** | **割り込み制御を人間から見えるようにする** | 決定ロジックは実装済みだったが **Web UI から一切触れておらず**、保留通知は書き込み専用の穴だった（下記の訂正参照）。新目標下で唯一の人間インターフェース | ✅ **完了**（`768bb60`）。状態・保留内容・保留理由を表示し、解放と全停止を操作可能に。全停止のみ確認を挟む |
| **P1-2** | **不可逆台帳の UI を接続する** | 事前ゲートの代替が API 止まり。Phase 3 からの持ち越し | ✅ **完了**（`c0c5845`） |
| **P1-3** | **`AutonomyProfile` を削除 or 配線する** | 虚偽の安全主張は「宣言されているが効いていない」型の最悪例。**配線は選べない**（プロファイルのはしごは Phase 5b で削除した承認機構そのもので、配線するとオーナー境界に違反する）。よって**削除** | ✅ **完了**。`AutonomyProfile` を削除し、検出器を自動発見化。`test_the_retired_autonomy_profile_stays_retired` が不在と `# Always forbidden (structural)` の消滅を固定 |
| **P1-4** | **`pc-server.file.read` / `write_file` にパス検査を入れる** | 実害（秘密鍵が読める） | ✅ **完了**（`f8293a9`） |
| **P1-5** | **残骸 8 面の削除/配線を決める**（§3.3） | 判断待ちが溜まるほど、次の実装が誤った前提の上に乗る。ただし **#8 `BrowserSafetyBoundary` は削除対象から外す** — P1-7 の調査で、休眠しているだけで本来効くべき層だと判明したため（他 7 面とは性質が違う） | 🔄 **実施中**。棚卸しで**当初リストの 4 面が誤りと判明**（§5.1）。参照ゼロを実測で確認した 4 面（`dialogue/`・`research/`・`{room,android}_server_client.py`、計 13 ファイル / 3,136 行）は削除、残りは「モジュール削除」ではなく個別メンバーの判定へ。**`dev-server` 残骸は解消済み**（`952caaa`、§5.2 の追記）— 名簿は `aegis_schema/roster.py` の 1 つになり、`dev-server` を綴るモジュールは 6 → 3、記録ドリフトは 5 → 2 サイト。残る個別メンバーは **§5.1 の実測で 3 つに絞られた**: `permissions/`（**A-6**）・`motivation_arbiter`（**B-3**、経路全体で 1 判断）・`reflection_engine` の死んだ `approval_decisions` 引数（**A-11**）。**`requires_approval_for`・`risk.approval_mode`・`ConfirmationStore.mark_executed/mark_failed` は「生きた契約／消費されている」と実測されたので判断は要らない** — この行は長く 6 件を「オーナー判断待ち」と並べていた。**正典は §0.2** |
| **P1-6** | **Horvitz 型の割り込み期待効用モデル**（提案 P1-14） | 現行は手書きのしきい値のはしご。提案自身が「まず手設計の期待効用から始め、データが溜まってから学習へ」と述べている | ✅ **完了**。`InterruptionController.decide` を `net = benefit × P(receptive) − cost` に置換し、`net > 0` で発話。**宣言された規則（emergency_stop・例外カテゴリ・critical・静穏時間・proactive 不許可）はハードゲートのまま**でモデルを経由しないことをテストで固定。判断ログに**内訳**（benefit / p_receptive / cost / net / occupancy）を載せ、**報告された数値から決定を再計算できる**ことを assert — これが「効用の衣を着たはしご」への退行を防ぐ。学習と HandRaiser は P1-14 自身の理由で対象外 |
| **P1-7** | **browser-server の休眠した安全層をどうするか決める**（旧題: stealth / bulk signup の実効化） | 調べた結果、**「書かれていない」のではなく「書かれているが誰も見ていない」**だった。`BrowserSafetyBoundary` は構築され `get_actions_taken()` だけが読まれ、**4 つの `check_*` は `src/` から一度も呼ばれない**（`actions_taken` も常に空）。`use_proxy_for_evasion` / `bulk_signup` は全タスクの `forbidden_actions` に入っているが、効かせるはずの `check_action` が死んでいる。**一括配線はできない**: `check_page_observation` の `APPROVAL_BOUNDARIES` が publish/submit/upload/account_creation に `needs_approval=True` を返すため、配線すると**強制承認ゲートが復活**しオーナー境界に違反する。加えて `check_action` は**こちらの action 語彙**で比較するので browser-use の action 名と一致せず、そのまま入れると全アクションが止まる。**単一制約への実害**: `check_domain`（＝ナビゲーション毎の egress 検査）も死んでおり、事前検査 `_navigation_egress_denied` は**宣言された target のみ**を見るので、タスク途中の任意ホストへの遷移は再検査されない | ✅ **完了**（`a5c2cdc`）。**案①（egress 検査だけ配線）を採用**。`BrowserProfile.allowed_domains` を `egress.navigation_allowlist()` から導出し、browser-use の `SecurityWatchdog`（遷移前 veto・リダイレクト再検査・不正タブ閉鎖）に施行させる。**承認意味論も action 語彙の翻訳も不要**なので、強制ゲートは削除のまま・休眠層も休眠のまま（`test_safety_boundary_dormancy.py` は無変更で緑）。パターンは完全一致か `*.suffix` のみ — `192.168.*` は公開 DNS 名 `192.168.evil.com` も通すため、私有 IP は**宣言されたときだけ**許可する。休眠は `browser-server/tests/test_safety_boundary_dormancy.py` が発見＋等式で固定 |

### （解決済み・記録）判断待ち 3 件の選択肢と推奨 — 2026-09-28

> **これは解決済みの記録です。** 現在未決の判断は **§0.2 のレジスタ**にあります（この節の題が
> 「判断待ち」のままだったため、2026-09-29 まで**未決 3 件があるように読めていた**）。

実装だけで閉じられる P1 は尽きており、残りは**判断が一言で足りる**項目。

| # | 問い | 選択肢 | 推奨と理由 |
|---|---|---|---|
| **P1-7** | browser-server の休眠した安全層をどうするか | ① egress 検査だけ配線 ② 禁止リストも配線 ③ 休眠のまま | **①**。単一制約に直結し、`AGENTS.md` が「egress ゲートの実装・強化は相談不要」と明記している唯一の領域。**承認ゲートに触れずに済む唯一の案**。②は action 語彙の翻訳層が要り、そのまま入れると全アクションが止まる |
| **P1-5** | 承認時代の残骸 7 面 | ① 拾ってから削除 ② そのまま一括削除 ③ 保留 | **①**。`android_server_client.py` に「生きた経路に無い安全サブシステム」があり、消す前に中身を見る価値がある。確認後、残りを削除 |
| **P1-6** | 割り込みの期待効用モデル | ① 期待効用を明示計算 ② まずログだけ取る ③ 現状維持 | **①**。提案 P1-14 の本命。判断ログも同時に取れるので ② を内包する |

推奨順は **P1-7 → P1-5 → P1-6**。P1-7 だけが単一制約に触れ、他 2 件は北極星層の話。
なお 3 件とも**現状で壊れているものは無い** — 欠けているのは穴を塞ぐことと精度であり、
いずれも「今より良くなる」方向の判断。

**3 件とも推奨案で実施した**（2026-09-28）: P1-7 = `a5c2cdc`、P1-5 前半 = `bba8ae5`、P1-6 = 下記。
ただし **P1-5 は当初リストが誤っており**（§5.1）、実施できたのは参照ゼロを実測で確認した 4 面だけ。
残りは「生きたモジュールの中の死んだメンバー」として個別判定に持ち越した。

### 5.1 P1-5 棚卸しの実測結果（2026-09-28）

**当初の削除リストは 7 面中 4 面が誤っていた。** import 元を grep しただけで判明した。

| 面 | 当初の判定 | 実測 | 対応 |
|---|---|---|---|
| `aegis_ai/dialogue/` | 残骸 | ✅ 外部参照ゼロ（3 クラスとも `__init__` の再輸出のみ）。`is_approval_required` は**同じパッケージ内からも呼ばれない** | **削除**（4 ファイル） |
| `aegis_ai/research/` | 残骸・削除済み id を呼ぶ | ✅ 外部参照ゼロ。しかも `ResearchAgent` / `ResearchCollector` / `CitationRanker` は**そもそも存在しない** — docs が架空の設計を記述していた | **削除**（7 ファイル） |
| `src/android_server_client.py` | 残骸 | ✅ 参照ゼロ（自己参照のみ）。ただし保全対象あり（下記） | **削除**（1,031 行） |
| `src/room_server_client.py` | 残骸 | ✅ 参照ゼロ | **削除**（1,032 行） |
| `aegis_ai/permissions/` | 承認の第 3 面・呼び出し元ゼロ | ❌ **生きたテストが import している** — `test_goal_alignment.py`（5 箇所）と `test_mission_contract_acceptance.py`。**パッケージ削除は不可** | **保留** — どのメンバーが死んでいるかを個別に判定 |
| `reflection_engine` | 残骸 | ❌ **本体は生** — `runtime.py:1618` が構築し `autonomous_loop` に注入、テストもある。死んでいるのは **`approval_decisions` 引数だけ** | **保留** — 「モジュール削除」ではなく「死んだ引数の削除」 |
| `motivation_arbiter` | 呼び出し元ゼロ | ❌ **この行の判定が誤っていた**（B-3 で実測）。`autonomous_controller.py` が import しているのは事実だが、**その `autonomous_controller` 自身が import 元ゼロ** — `src/`・`tests/`・docs 内のコードのいずれからも。つまり arbiter は**到達不能なモジュール経由でしか到達できない** ＝ 本番では `decide()` は一度も走らない。「生」ではなく「**死んだ経路の上に乗っている生きたコード**」 | **単独では削除しない** — 経路全体（約 700 行）が 1 つの判断だから。`docs/self-development.md` の冒頭図はこの controller を**入口として描いている**が、実測の入口は `runtime.py:1586` の `_create_autonomous_loop` が直接構築する `AutonomousLoop`。ピン `tests/test_autonomous_execution_path_is_single.py`（8 関数）が**配線しても削除しても落ちる**。**図の訂正はオーナー判断**（§5.2 の追記） |
| `risk.approval_mode`（5 manifest） | 読者ゼロ | ⚠️ `capability_catalog.py` が**書きも読みもする**（165 / 521 / 563） | **保留** — 決定経路に読者がいるかを判定 |
| `ConfirmationStore.mark_executed` / `mark_failed` | 呼び出し元ゼロ | ⚠️ **`tests/test_confirmation_store.py` が 4 箇所でテストしている** | **保留** — テストごと削除するかの判断 |
| `dev-server` 残骸 | — | ✅ **解消済み**（`952caaa`、§5.2 の追記）。名簿は `aegis_schema/roster.py` の 1 つ、`dev-server` を綴るのは 3 モジュール（うち 2 つは記録済みドリフト）。加えて SDK の既定 `server_type` が `ServerType.DEV` のまま（B-14） | **B-15 は解決、B-14 は未決**（A-2） |

**教訓**: 「残骸リスト」は**手書きのリスト＝それ自体が欠陥**（バグ類型 5）。今回の 4 件は
grep 1 回で判明した。**削除の前に必ず実測すること** — 4 面をそのまま消していれば
`permissions/` と `reflection_engine` で生きたテストとランタイム経路を壊していた。

#### `android_server_client.py` の保全対象（削除は可逆）

live 経路に無い安全サブシステムを含んでいた:

- `NotificationFilter` — 銀行/パスワードマネージャ/認証アプリのパッケージを**丸ごと遮断**（`DEFAULT_DENYLIST`）、
  ingest 時にカード番号・メール・電話・OTP を**マスク**（`REDACTION_PATTERNS`）。
- `contains_password_field(ui_tree)` — UI ツリーのパスワード欄検出。

**live 経路の実測**: `android-server.notification.get_notifications` は**配線済み**
（`integrations/android/capability_mapper.py:58`）で、端末の通知は実際に AEGIS へ流れ込む。
一方 `notification/router.py` の `_redact_if_needed` は**外向きチャネル（LINE/Discord/Email）宛のときだけ**
マスクし、**端末から取り込む時点では何も絞っていない**。

**それでも移植しなかった理由**: これは製品判断であって機械的な移植ではない。とくに
`REDACTION_PATTERNS` の OTP 規則 `(?<!\d)\d{4,8}(?!\d)` は **4〜8 桁の数字を無差別に潰す**ので、
「確認コードを読み上げて」という正当な用途を壊す。採否はオーナーの判断。
コードは git 履歴に残るので**削除は可逆**（`git show <削除コミット>^:ai-server/src/android_server_client.py`）。

> **訂正（P1-1 の当初の記述について）**: 初版は「`interruptibility` は未実装」と書いたが、
> **これは誤りだった**。実測すると、割り込みは
> `personal_ai/situation.py`（`SituationModel` が `interruptible` / `important_only` /
> `batch_later` / `suppress` を算出）、`personal_ai/interruption.py`（`InterruptionController` が
> `send_now` / `batch_later` / `suppress` / `emergency_stop` を決定）、
> `notification/notification_manager.py`（送信直前に `before_send` を呼び、保留なら配送しない）、
> `presentation/manager.py`（`_handle_interruption_queue` が侵入的な宛先だけを保留し、
> ダッシュボード表示は保つ）まで**通っていた**。API も
> `GET /api/interruption`・`POST /api/interruption/flush`・`POST /api/interruption/emergency-stop`
> が揃っていた。
>
> 本当の欠落は**面**だった。`web-ui` は割り込み関連の識別子を**一つも参照していなかった**。
> つまり「保留」と判断された通知は `data/personal_ai/interruption.json` に積まれ、
> 誰も呼ばないエンドポイントでしか取り出せない＝**ユーザーから見て消えていた**。
> 提案 P1-14 が言う「未実装」は Horvitz の**期待効用モデル**のことで、制御そのものではない。
> 「未実装」と「見えない」は別の欠陥であり、後者のほうが新目標下では重い。

### 5.2 `dev-server` 残骸の実測（2026-09-28）— P1-5 の「次回」分

**結論: 「dev-server 残骸」は消し忘れの寄せ集めではなく、サーバ名簿に単一の定義が無いことの症状。**
名簿を列挙するリテラルは **15 箇所 / 11 ファイル**（AST 計測。値の型は `ServerType`・短縮 prefix・
有効フラグ・id prefix・host:port の 5 種）。うち **5 箇所が `dev`/`dev-server` を今も持つ**。
**→ A-3 で 10 箇所 / 7 ファイルへ削減（下の「A-3 の実施」を参照）。下表は実施前の測定値。**

| 箇所 | 形 | 到達可能性（実測） |
|---|---|---|
| `capability_catalog.py:70` `_PREFIX_MAP` | server_id → 短縮 prefix | ❌ 生きた manifest に `server_id="dev-server"` は無い |
| `capability_catalog.py:379` server_type_map | server_id → `ServerType` | ❌ 同上 |
| `models.py:215` prefix_map | `ServerType` → (短, 長) | ❌ 同上 |
| `permissions.py:66` server_enabled_map | prefix → 有効フラグ | ❌ `capability.id.split(".")[0]` が `dev` にならない |
| `ui_overview.py:3388` prefix 集合 | prefix の集合 | ❌ 同上 |
| `settings/models.py:21` `dev_server_enabled` | 設定フィールド | ⚠️ 読み手は `permissions.py:75` だけ。**その行が到達不能なので実質未読** |
| ~~`settings/validation.py:24-27` `dev.*` 10 件~~ | ~~`FORBIDDEN_CAPABILITIES`~~ | ✅ **削除済み**（A-1、2026-09-29、§5.13）— 方言問題（B-12）に加え dev capability が存在しえないため、**一覧ごと削除**した |
| ~~`aegis_schema/validation.py:151`~~ | dev_caps の警告 | ✅ **削除済み**（下記）— この警告は**一度も走らない関数**の中にあった |
| `policy_engine.py:120,127` `dev.*` パターン | `EXPLICIT_DENY_PATTERNS` | ❌ 到達不能（ただしパターンなので他サーバには効く） |
| `packages/aegis-sdk-python/aegis_sdk/capability.py:37` | ~~`server_type: ServerType = ServerType.DEV`~~ | ✅ **解消済み**（A-2、§5.18）— 既定は `None` になり、prefix から**導出**される。prefix と矛盾する `server_type` を渡すと拒否される |
| `packages/aegis-sdk-python/tests/test_sdk.py` | ~~prefix を `dev` と名乗る~~ | ✅ **解消済み**（A-2、§5.18）— 生きたサーバの prefix（`room`）へ移した。借り物の身元だった |

**ついでに判明した、dev-server とは独立の欠陥:**

- ~~**`aegis_schema/validation.py` は孤島**~~ → ✅ **削除済み（2026-09-29）**。実測すると「孤島」より強く、
  **仕事が無い**ことが分かった。生きた **128 capability 全部**に対して走らせた結果は **エラー 0 件** /
  警告 133 件で、うち **128 件（＝全 capability）**が「tags に `risk:<level>` を入れよ（**Policy Engine
  のフィルタリングのため**）」と言う。だが **capability を risk タグで絞る機構は存在しない** —
  `PolicyEngine` は `DEFAULT_RISK_MAP` で `RiskLevel` を引き、`list_for_llm` のフィルタは
  `requires_feature` だけ（`tags` は LLM 一覧に**載るだけ**で、manifest にも `risk:` タグは **0 件**）
  — **ただし 2026-09-30 の実測で、その `requires_feature` 自体が「誰も渡さない引数」なので
  一度も走らないことが分かった**（§0.2 の **A-12**）。つまり **`list_for_llm` に効いている
  フィルタは 0 個**で、この論証はさらに強くなる。
  残る固有チェックも**退役した時代のもの**（`requires_approval=false` の警告＝承認時代 /
  「No capabilities registered for Dev server」＝削除済み dev-server）。つまり**配線しても何も得られず**、
  128 件の偽警告が出るだけだった。manifest 検証の仕事は `tests/test_manifest_schemas.py` が
  **データに対して**正しく担っており（CI で走る）、そちらと**二重の真実源**になるだけ。
  削除は `tests/test_schema_validator_stays_retired.py`（5 テスト、**変異 4 種すべて捕捉**）で固定。
- ~~**SDK の既定値が削除済みサーバ**（B-14）— `ServerType.DEV` が既定なので、第三者 prefix は
  `Capability.id` の regex に弾かれる。**SDK 自身の docstring の例が動かない**ことを実行して確認。~~
  → ✅ **解消済み**（A-2 ②、§5.18）— SDK が第三者 prefix を**明示的に断り**、`server_type` は
  prefix から導出する。docstring の例・同梱 example・scaffold の生成物は**実行で**検証される。

**ドリフト検出器を追加した** — `ai-server/tests/test_server_roster.py`（20 テスト）。
名簿リテラルを **AST で発見**し、**live なサーバは capability カタログから発見**する
（明日サーバが増えてもこのファイルを編集する必要がない）。退職したサーバだけは**発見不能**
（もう存在しないものは痕跡を残さない）なので手書きの集合にし、**観測したドリフトと記録の集合が
一致すること**を assert する — 増えても減っても落ちるので、記録が古い状態を語り始めない。

変異 5 種で load-bearing を証明: 死んだサーバを名乗る新規名簿 / 記録済みサイトが浄化される /
第三者 prefix を許すよう regex を広げる / 退職集合を空にする → **すべて捕捉**。
live なサーバだけの新規名簿は**正しく緑のまま**（偽陽性なし）。

**「消す」ではなく「検出器」にした理由**: 死んだエントリの削除は**無害ではない**。
`models.py:223` は `prefix_map.get(self.server_type)` が `None` を返すと **id prefix 検査ごと
スキップ**し、`permissions.py:80` は `.get(prefix, True)` なので**キーが無ければ有効**になる。
つまり今は到達不能でも、**将来 dev capability が現れたときに fail-open に転じる**。
どちらのデフォルトを選ぶかはオーナー判断であって機械的削除ではない。

**推奨（いずれもオーナー判断を含む）:**

1. ~~**名簿を 1 つにする**（B-15）。`aegis_schema` にサーバ名簿を置き、15 箇所がそれを参照する。~~
   ✅ **実施済み（`952caaa`）** — `aegis_schema/roster.py`。**ただし「15 箇所」は誤りだった**
   （12 箇所。残り 3 つは状況ソースの語彙）。上記の追記を参照。
2. **`dev.*` の到達不能な 11 箇所は、消す前に各サイトのフォールバック先を決める** — 到達不能で
   あることは実測済みだが、削除は無害ではない（上記）。とくに `permissions.py` と `models.py` の
   2 箇所は**消すと fail-open** なので、先にデフォルトを明示するのが筋。
3. **B-12/B-13 の決着** — `allowlist` を削除するか配線するか。削除するなら
   `FORBIDDEN_CAPABILITIES` は `per_capability` 専用になるので、**照合を action ベースに変える**のが筋。
4. ~~**B-14 の決着** — SDK に任意 prefix を許すか、第三者 prefix は不可と明示するか。
   **どちらでもよいが、現状の「第三者サーバを謳って黙って禁じる」は最悪の組合せ。**~~
   → ✅ **決着済み**（2026-09-29、A-2 ②、§5.18）— **SDK が明示的に断る**側。上の 3 つの欠陥は
   すべて解消し、§5.2 の表の行も閉じた。

#### A-3 の実施 — 名簿を 1 つにする（2026-09-29、`952caaa`）

上の §5.2 は「15 箇所 / 11 ファイル」という**計測値**を残したが、実装に入る前の再測定で
**その数字の意味が 2 つ崩れた**。登録簿の推奨そのものが前提を誤っていた例なので記録する。

| 当初の見立て | 実測 |
|---|---|
| 15 箇所が同じ事実の 15 コピー | **12 箇所が名簿**。`situation.py:51/189/204` は**状況ソース**の語彙（`ai-server → "webhook"`、`:189` に `"status."` を含む）— **キーが同じだけの別物** |
| `server_id → ServerType` の写像は同内容のコピー | **5 コピー、うち 2 つは既に食い違い**（`tool_broker.py` に `dev-server` 無し / `capability_catalog.py` に有り） |
| 5 箇所を個別に直せば済む | 直すべきは**写像の重複そのもの**。個別修正は次のサーバ増減で再発する |

**実施内容**: `aegis_schema/roster.py` を新設（`SERVER_ROSTER` が `(ServerType, 正準 id, 短縮 prefix)`
の 5 件、`RETIRED_SERVER_ROSTER` が退職 1 件）。そこから 6 方向の写像を**同じ導出関数で**作る
（`SERVER_TYPE_BY_ID` / `PREFIX_BY_ID` / `PREFIXES_BY_TYPE` / `SERVER_TYPE_BY_DOTTED_ID` ほか）。
退職エントリは `**` 展開で折り込むので、**`dev-server` を綴るモジュールは 6 → 3**。
6 サイト（`capability_catalog.py` ×2 / `prompt_regression.py` / `dashboard_legacy.py` / `models.py` /
`tool_broker.py`）が import する。**6 つの写像すべて HEAD と値が同一**を確認＝純粋なリファクタ。

**検出器を事実の移動に追随させた** — `test_server_roster.py` の `_id_consistency_map()` は
「ローカル変数なので import 不可」を理由に **AST を読んでいた**。名簿が import 可能になったので
**読み先を名簿へ移した**。ここで**ガードが 1 つ消える**: 「validator は dict リテラルを 1 つだけ持つ」
という assert は AST 読みのためのものだった。代わりに**それが守っていた不変量**を書いた —
`test_the_validator_names_no_server_of_its_own`（validator の本体にサーバ名の文字列定数が
**1 つも無いこと**）。**計測の移動で消えたガードは、ガードの目的で置き換える。**

**測定で撤回したアサーション 2 つ**（どちらも「検査に見えて検査でない」）:

1. `PREFIX_BY_ID == {s: _PREFIX_MAP[s] for s in SERVER_IDS}` — `_PREFIX_MAP` は
   `PREFIX_BY_ID` **から導出**されるので、短縮 prefix が誤っていても**両辺が一緒に動く**。
   変異（`room → rm`）で**緑のまま**だった。短縮 prefix は代わりに `Capability.id` の
   **許可リスト**と突き合わせる — あちらは独立した宣言で、実測で 12 個の選択肢が名簿と**完全一致**する。
2. 「manifest の `server_id` と id prefix が一致すること」 — `folder_registry._derive_ids` は
   `server_id` を**パスから**取り、`capability_id` も**同じ dict から**組み立てるので、
   id の第 1 セグメントは**構造上** server_id である。加えて `_validate` が JSON の `server_id` を
   パスと比較し、食い違えば manifest を**拒否**する（`list_all()` に届かない）。真の不変量は
   「**拒否が 0 件**」で、それは既に `test_manifest_schemas.py` が固定している。**重複した
   落ちないテストは負債なので、スタブとして残さず撤回した。**

**結果**: 名簿リテラル **15 → 10 箇所 / 11 → 7 ファイル**、記録ドリフト **5 → 2 サイト**。
残る 10 箇所は**モジュール単位で記録し、等式で固定**した（`_RECORDED_INLINE_ROSTERS`）—
`len(ROSTERS) >= N` の床では**増加を検出できない**ため。退職 id の綴り箇所も直接固定し、
`_MIN_ROSTER_SIZE` の床（**単一名のリテラルは閾値未満**）が作っていた盲点を塞いだ。
**変異 12/12 捕捉**、各変異が**期待どおりのテスト**で落ちることを観測、原ファイルは
**バイト単位で復元**（sha256 検証）。ai-server **1724 → 1726 passed / 31 skipped**。
**+2 の内訳は HEAD の worktree で per-file に突き合わせて確認**（新規テスト関数 7 − 消えた
parametrize 5 = +2。名簿リテラルが 15 ではなく 10 になったため parametrize が減った）。

### 5.3 B-13 の固定 — 「守られているが消費されていない」を検出する（2026-09-28）

B-13 は「バリデータが守っているのに誰も消費していない」という型で、既存の死にフラグ検出器の
**盲点そのもの**なので、検出器を足した: `ai-server/tests/test_guarded_settings_fields.py`（6 テスト）。

- 守られる集合は `settings/validation.py` を **AST で解析**して得る（`<x>.capabilities.<field>` の
  属性アクセス。クラス本体の定義は数えない）
- 消費者は `src/` を走査して発見（**バリデータ自身は除外** — これが盲点の正体）
- **観測した穴と記録の一致を等式で固定**。`allowlist` が唯一の記録済みの穴

変異 5 種すべて捕捉: 新たに守られたのに消費者がいないフィールド / 記録の削除 / 消費者が付いたのに
記録が残る / 走査が誤った属性形を読む / **バリデータが守るのをやめる**（守る側の集合が縮んでも落ちる）。

**なぜ「全 95 設定フィールドを decision で消費せよ」としないか**: 大半は設定配管から読まれており
decision ではない。広げると失敗のほとんどが偽陽性になり、**トリアージを要するテストは無いより
悪い**（スキルの規則）。よって**バリデータが守るフィールドだけ**に絞った。

**B-12 は固定していない** — 照合の意味（id 一致か action 一致か）を変える設計判断が先に要るため。
観測値（39 件中 canonical 形 8 件・非 canonical 31 件・`catalog.resolve()` で解決 0 件）は §4.1 に残す。

### 5.4 B-16 の固定 — 「動くゲート」を配線から守る（2026-09-28）

P1-5 後半（「拾ってから残骸 7 面を削除」）の**境界集合の確認で結論が反転した**。削除候補として
`aegis_ai/permissions/` を調べたところ、**削除すべき残骸ではなく、配線されてはならない生きたゲート**
だった（§4.1 B-16）。よって**削除ではなく固定**を選んだ。

**既存のガードでは届かなかった理由**（3 サーフェスは別物）:

| ガード | 固定している対象 | `permissions` を捉えるか |
|---|---|---|
| `tests/test_goal_change_guard.py` | **削除済み** approval サブシステム（`aegis_ai/approval/`）が復活しないこと | ❌ 対象が**存在しないこと**の固定なので、**存在する**パッケージは射程外 |
| `tests/test_forced_gate_stays_retired.py` | `aegis_ai.confirmation`（置換後の確認ストア）が**ゲートの名前を変えただけ**でないこと | ❌ パッケージ名が違う |
| **同ファイル（拡張）** | `aegis_ai.permissions` が実行経路から**到達不能**であること | ✅ 今回追加 |

**新規ファイルを作らず既存ファイルを拡張した理由**: `_EXECUTION_PATH`・`_src_files()`・AST 基盤が
既にあり、その `test_the_confirmation_package_makes_no_decisions` は既に `requires_approval` を
ゲート語彙として列挙している。`_imports_confirmation(path)` を **`_imports_package(path, package)`**
に一般化し、`_importers_of(package)` を挟んだので、**パッケージ名は 1 箇所にしか書かれていない**。

**変異 4 種すべて捕捉**（`4/4`）:

| 変異 | 期待 | 結果 |
|---|---|---|
| 実行経路のモジュールが import を足す | 落ちる | CAUGHT |
| 非実行経路の `src/` モジュールが足す | 落ちる | CAUGHT |
| prefix 一致を等価に狭める（走査が盲目化） | 落ちる | CAUGHT |
| `MEDIUM_RISK_WRITE` の既定を `allow` にする | 落ちる | CAUGHT |

**同時に「死んでいない」と判明した他の P1-5 候補**（削除は不成立。次に同じ調査をしないため記録）:

| 候補 | 判定 | 根拠 |
|---|---|---|
| `ConfirmationStore.mark_executed` / `mark_failed` | **生きた契約** | `test_forced_gate_stays_retired.py:61-65` が「**意図的に**この tuple に入れない」と文書化している。将来の配線点 |
| `profile.requires_approval()` | **生きた契約** | テストが読む。`requires_approval_for` は宣言済みの agent-profile データフィールド |
| `risk.approval_mode`（5 マニフェスト） | **消費されている** | `capability_catalog.py:165-166`・`:563-568`・`:599-606`、`folder_registry.py:258`、`capability_overrides.py` |
| `motivation_arbiter.requires_approval` | ⚠️ **削除可能だが「唯一」ではない**（B-3 で訂正） | `:214`・`:234`・`:254` で `t.requires_approval` から書かれ、`:320` は `best_task.requires_user_approval`（**別名**）を、`:332` はリテラル `False` を書く。**`MotivationDecision.requires_approval` を読むものは 1 つも無い**。`:214/:234/:254` は `ExternalTask.requires_approval` を**読んでいる**が、その分岐（user / scheduled / event）は `ExternalTask` がどこでも構築されないため**到達不能** — つまり「読者が 0」と「読者が到達不能」という**別種の死**が同じフィールド名で並んでいた。削除はオーナー判断（経路全体の去就と一体） |

### 5.5 P2-3 の実測 — 承認時代の記述は、ほぼ掃討済みだった（2026-09-29）

P2-3 は「`docs/` の残る承認時代の記述を掃討（`approval` で repo 全体を再 grep する**運用を継続**）」
と書いていた。**手書きの運用はそれ自体が欠陥**（§4.3 クラス 5）なので、実測して件数を確定させた。

| 区分 | 件数 |
|---|---|
| `approval` / `承認` に言及する文書（`docs/` + `AGENTS.md` + `README.md`） | **57** |
| うち訂正バナーを持つ（`Goal change (2026-09-27)` または `risk annotation`） | **48** |
| バナーを持たない | 9 |
| うち ADR（定義上、履歴記録）または本文で自ら訂正済み | **8** |
| **誤り** | **1** — `README.md` |

バナーを持たない 9 の内訳:

- `docs/adr/` 3 本 — ADR は**時点記録**なので対象外。`permissive-autonomy-policy.md` は自ら
  `Accepted — superseded in part (2026-09-27)` と明記し、何が生き残るかを列挙している
- `docs/egress-gate.md`・`docs/irreversibility-ledger.md`・`docs/pc-server-windows-host.md`
  — いずれも本文で「ゲートは撤去済み」と訂正済み
- `docs/testing-real-devices.md`・`docs/ubuntu-production.md` — **生きた自発的確認**の話
  （Android へ stream される ask、通知の起床要因）であり、強制ゲートの主張ではない
- **`README.md`** — ← 唯一の誤り

**`README.md` はリポジトリの玄関**でありながら、退役した 5 段のはしごを掲げ、しかも
`APPROVAL_REQUIRED` → 「Approval UI required」・`HIGH_RISK` → 「Approval or deny」と、
**コードと正反対**のことを書いていた（`PolicyEngine.DEFAULT_RISK_MAP` はどちらも
`ALLOW_WITH_AUDIT`）。**唯一の制約（egress gate）には一切触れておらず**、`APPROVAL_REQUIRED` が
実際には「誰も尋ねられない」ことも書いていなかった。

**検出器を書かなかった理由**: 残り 56 文書を覆う走査には除外リストが要る。そして
**手書きの除外リストは、まさに検出したい欠陥そのもの**（§4.3 クラス 10）— 「残骸リスト」が
それ自体で欠陥だった P1-5 と同じ構造。代わりに、**誤っていた 1 箇所**を
`tests/test_readme_safety_model_matches_the_code.py`（11 テスト）で固定した:

- 表を **README から解析**し、各行の判断を **`PolicyEngine.DEFAULT_RISK_MAP` そのもの**と比較する。
  つまり README は**写しではなくコードに対して**検証されるので、写しが二重化しない
  （マップにレベルを足して文書化し忘れれば落ち、判断を間違えても落ちる）
- 「どの行も承認サーフェスを約束しない」ことと、`APPROVAL_REQUIRED` 行が
  **「誰も尋ねられない」と書いている**ことを別々に固定（前者だけでは文言の言い換えで通る）
- **唯一の制約**と、**自発的確認が生きていること**（オーナー境界の両半分）も固定 —
  承認語彙を消す編集が、生きている半分まで一緒に消してしまわないように

**変異 6/6 捕捉**（偽の行を戻す / 判断を間違える / `UNSPECIFIED` 行を落とす /
存在しないレベルを書く / 制約の文を消す / 自発的確認の文を消す）— 各変異は
**期待したテスト**で落ちることを確認済み。ai-server **1667 → 1678 passed / 31 skipped**
（+11 = 新テスト数ちょうど、実測 320 秒。既存テストの挙動は 1 件も変わっていない）。

### 5.6 `aegis_schema` の承認語彙 — 非対称なドリフト（2026-09-29, `2786955`）

P2-3 で **docs** を掃討したが、**source の散文**は未着手だった。同じレンズで `src/` を grep したところ、
共有スキーマ `aegis_schema/models.py` に 2 つの欠陥が見つかった。

**① `ApprovalRequirement`（削除）**

「実行前に必要な承認」を記述するモデルで、`requires_user_approval` の既定が **`True`**、
`approval_message` は「Approval UI に出す文言」、`timeout_seconds` は「**auto-deny** までの待ち時間」。
**参照ゼロ** — Python / TypeScript / Kotlin / Rust / docs / SDK のいずれにも無く、唯一の参照は
`__init__.py` の再輸出 2 行だけだった。決め手は **`models.py` の中で唯一 protobuf に対応物が無い**
こと: パッケージの docstring は「全モデルが `protos/aegis/` を写す」と宣言しており、他の 10 クラスは
すべて message か enum に対応する（`RiskLevel` だけが `SafetyLevel` への改名）。**削除しても既存テストは
1 件も動かなかった**（1685 = 1678 + 新規 7）— 前回の `validation.py` と同じ署名。

**② `RiskLevel` の記述が偽（訂正）**

「Policy Engine はこれを使って allow / **ask for approval** / deny を決める」と書いていたが、
`DEFAULT_RISK_MAP` に ask は無い。`APPROVAL_REQUIRED` のコメントも「**Needs explicit user
confirmation**」だった。**proto 側の `SafetyLevel.LEVEL_2_APPROVAL` は Phase 5b で既に訂正済み**
（「nothing gates on it … no longer implies that anyone is asked」）で、**Python の写しだけが取り残されていた**。

**これが本当の欠陥**: 文が間違っていたことではなく、**スキーマの両半分を結ぶものが何も無かった**こと。
だからピンの第 1 テストは散文を読まず、**`models.py` のクラスと `protos/aegis/` の message/enum を
両方発見して、全モデルに対応物があることを assert** する。これが `ApprovalRequirement` を誰も散文を
読まずに捕まえる形で、**「proto にあって Python に無い」逆方向も同時に押さえる**。

`tests/test_schema_mirrors_the_protobuf_schema.py`（7 テスト、**変異 7/7 捕捉**）: 削除済みモデルの復活 /
再輸出 / 偽の docstring / 偽のコメント / proto の訂正注記の削除 / **proto に対応物が無い新規モデルの追加** /
改名マップの前提が崩れる。

**副産物（未対応・実測のみ）**: 同じ grep で `aegis_ai/evaluation/` に**死んだ部分グラフ**を発見。
`EvaluationRunner` / `SAFETY_BENCHMARK` / `scenario` / `runner` / `report` / `metrics` は
**パッケージ外から import が 0 件**（生きたのは `behavioral` だけ — `runtime.py:1125` と 1 テスト）。
`safety_tests.py` は `Scenario(name="Level 2 Approval Gate", description="Level 2 action requires
approval before execution", expected_outcome=ExpectedOutcome.APPROVAL_REQUIRED)` を持ち —
**テストに捕まらないゲートの主張**（バグクラス 10）で、`runner.py:217` も `APPROVAL_REQUIRED` を
基準に採点する。5 ファイルは**構文的には健全で import も通る**（＝「死んでいるが壊れてはいない」）。
ただし `prompt_regression.py` は `README.md` から文書化されているため**パッケージ全体は死んでいない** —
削除にはファイル単位の実測が要る。**今回は記録のみ。**

### 5.7 `evaluation/` の死んだ部分グラフ — 未使用ではなく、**主張が偽**（2026-09-29, `d4aae94`）

§5.6 の副産物として記録した「死んだ部分グラフ」を、ファイル単位で実測した。結論は
**「未使用」では済まない** — 死んだメンバーが、**いま偽になったことを主張している**。

**① 誰も走らせない（実測）**

`metrics` / `prompt_regression` / `report` / `runner` / `safety_tests` / `scenario` の **6 つ**が
パッケージ外から参照ゼロ（計 **1,104 行**）。生きたのは `behavioral` のみ（`runtime.py:1125` と 1 テスト）。
`ai-server/tests/test_prompt_regression.py` — 旧文書が「これを走らせろ」と書いていたファイル — は
**一度も存在したことがない**（リポジトリ全体で 0 件）。

**② `ExpectedOutcome.APPROVAL_REQUIRED` は生産者がゼロ**

目標変更コミット `495105e`（Phase 2）は `runner.py` から**唯一の生産分岐**を削除していた:

```python
-        elif invoke_result.status.name == "APPROVAL_NEEDED":
-            result.actual_outcome = "APPROVAL_REQUIRED"
```

`InvokeStatus` の 10 値に `APPROVAL_REQUIRED` は無い（`SUCCESS`/`FAILED`/`DENIED`/`TIMEOUT`/
`CANCELLED`/`DRY_RUN`/`UNAVAILABLE`/`NOT_FOUND`/`IDEMPOTENT_HIT`/`EXECUTION_ERROR`）。それでも
**2 ステップが今も期待している** — `scenario.py` の `safety_002/s2_invoke` と `safety_tests.py` の
`safety_level2_gate/invoke_level2` — ので、**この 2 つは絶対に通らない**。`DEFERRED` と `UNCERTAIN` も
同様に到達不能で、こちらは誰も期待していない。**enum のメンバー数 ≠ 到達可能な状態の数**（バグクラス 8）の
実例で、しかも Phase 2 は**「承認を制約から外した」と宣言して完了していた** — 消し残したのは
*制約*ではなく**制約の主張**だった。

**③ `PromptRegressionRunner` は原理的に違反を報告できない**

違反を記録する条件は `policy_result.decision.name == "ALLOW"`。ところが構築する全 capability が
`risk_level=RiskLevel.APPROVAL_REQUIRED` で、`DEFAULT_RISK_MAP` はこれを **`ALLOW_WITH_AUDIT`** に写す
— `ALLOW` にはならない。したがって**この分岐は到達不能**。実測: `run_all()` は **15/15 PASS** を返し、
その 15 件のうち **10 件が `expected_policy_decision: DENY` を宣言している**。
（`EXPLICIT_DENY_PATTERNS` は `modify_policy`/`disable_policy`/`purchase` には効くが、
`delete_file`/`read_credential`/`send_email`/`send_sns`/`move_robot_arm`/`bypass_approval` は
リスクマップに落ちる。）

**④ ケースが名指す capability が存在しない**

ケースは裸の action 名（`send_email` 等）を列挙し、runner が `pc-server.` を補う。**生成される 19 id は
すべて生きた 128 id カタログに無い**（例: `pc-server.delete_file` は存在せず、実際の近傍は
`pc-server.file.write` / `pc-server.process.kill` / `pc-server.system.empty_recycle_bin`）。
つまり**どのサーバにも要求できない capability** を評価している。

**⑤ ケースリストが 2 部あり、食い違っている**

Python 側 15 件、`evaluation/prompt_regression/expected_behaviors.yaml` 側 **17 件**。`tool_injection_001`
は Python が `modify_policy`+`disable_policy`、YAML が `modify_policy`+`approve_all`。**どちらも読まれない**
（YAML にローダーが無く、Python 側は runner の既定引数）。

**削除しなかった理由**: `495105e` のコミットメッセージ自身が、これらを
*"the stale approval-era surfaces … still await an owner decision"* に含めている。**削除か配線かは
オーナー判断**。加えて `docs/approval-ui.md` / `docs/dev-safety.md` / `docs/pc-safety.md` の 3 本が
「`invoke_tool_approved` は `evaluation/` のシナリオ段名としてのみ残る」と**この死んだファイルを指して
記述している**ので、消せば 3 本が偽になる。今回は**配線も削除もしない**。

**やったこと**: `docs/prompt-regression.md` を実測に書き換え（`**Status**: Implemented` を削除、
存在しないテストファイルへの実行コマンドを削除、存在しない 2 文書への参照を削除、
*"A failing test means a safety regression was introduced"* という**同語反復**を実測に置換）、
`README.md` の行も「動作するテスト」と読めない形に直した。ピン
`tests/test_evaluation_pack_is_dead.py`（10 テスト、**変異 10/10 捕捉、各々が自分の担当テストで落ちる**）
は**どちら側も発見して等式で固定**する — パッケージのモジュール集合 vs 外部から参照される集合、
`ExpectedOutcome` の全メンバー vs **runner が実際に生産できる outcome**、到達不能な outcome を期待する
ステップ、ケース id vs 生きたカタログ。**記録が腐れば落ちる**形にした。

**計測器が自分を測ってしまう罠（記録）**: 最初の実行で importer 走査が `runner`/`scenario`/
`safety_tests`/`prompt_regression` を「参照あり」と判定した — **このピンファイル自身の import を
数えていた**から。測定が測られるものを消してしまう構造で、スキャン対象から**自分自身だけ**を除外し、
除外理由をコメントに残し、`referenced == _LIVE_MODULES` の等式で**除外が 1 ファイルに留まること**を
固定した。同時に、記録側の誤りを 2 つ**テストが先に捕まえた**（YAML は 18 件ではなく **17 件**、
`present - referenced` の集合が食い違い）。**記録を書いた本人の数え間違いをピンが捕まえた**形で、
これが「発見＋等式」を選ぶ理由そのもの。

ai-server **1695 passed / 31 skipped**（1685 + 新規 10、実測 324 秒）。ruff clean。

**残るもの（オーナー判断 + 将来作業）**: 削除か配線かの判断。配線するなら
（`IMPROVEMENT_PROPOSAL.md` §P2-3 が求めている方向、ただし**egress 中心に再焦点**）
① 実在 id に置換 ② 現行ポリシーに合わせて期待を書き直す（`delete_file` → `ALLOW_WITH_AUDIT` は
**今は正しい**ので「ALLOW であってはならない」はもはや欠陥ではない）③ **未解決 id を失敗にする**
（fail-closed）④ ケースリストを 1 本化 ⑤ CI に配線、の 5 段。**期待の書き直しは製品判断**なので
ここで止める。

### 5.8 割り込みコストの語彙 — 2 つの写像が食い違い、1 つの比較が定数（2026-09-29, `7866d85`）

P1-6 で `InterruptionController.decide` を期待効用モデルに置き換えたとき、**その較正値の隣に
未検出の面が 2 つ残っていた**。B-11 は記録済みだったが**検出器が無く**（`tests/` で
`_current_interruption_cost` に触れるテストは 1 件も無い。`test_action_drive.py:63` は値を
*渡している*だけ）、B-17 は今回新たに見つかった。

**① B-11 — 2 つの写像が 1 つのはしごの順序で食い違う**

`_RECEPTIVITY`（P(receptive)、P1-6 のモデル）と `autonomous_loop._current_interruption_cost`
（InitiativeEngine のコスト軸）は**写しではない** — 消費者が違うので統合は誤り。だが**同じはしごの
単調写像**なので、順序は一致しなければならない: 受容しやすいレベルが同時に高コストではいけない。
実測で**違反はちょうど 1 対**:

| | 受容確率 | コスト |
|---|---|---|
| `batch_later` | 0.20 | 0.40 |
| `important_only` | **0.35** | **0.55** |

`important_only` のほうが**受容されやすい**のに**コストが高い**。結果、`InterruptionController` は
「重要なものだけ」と言われたときに**話しかけやすく**、`InitiativeEngine` は**行動しにくい** —
同じ入力から逆の結論。コスト表の中央 2 つが、`_RECEPTIVITY` が従うはしご
（`interruptible > important_only > batch_later > suppress`）に対して**転置**している。

構造的な半分もある: `_RECEPTIVITY` は**キー集合を発見＋等式で守られている**
（`test_interruption_utility.py`）ので新しいレベルが既定値に落ちないが、コスト表は
**裸の `.get(kind, 0.2)`** で終わるので、**新レベルは `batch_later` より安く割り込める**ものとして
黙って読まれる — `_RECEPTIVITY` 自身の docstring が警告しているゴーストフィールドの型が、
**片方にだけ適用されている**。

**② B-17（新規）— 判定の第 3 項が本番で定数**

```python
should_interrupt = important and not occupied and context.expected_usefulness >= context.interruption_cost
```

被演算子は `autonomous_loop.py:3065-3066` が**同じ既定値 0.5** で埋める。そして
**リポジトリのどこもその 2 つのキーを task に書かない** — `src/` 全体の dict リテラル走査で
見つかる書き込みは `_present_autonomous_result` 内の**プレゼンテーション payload への転記 2 箇所**
だけで、比較が読む方向（task 構築側）ではない。よって比較は常に `0.5 >= 0.5` = **真**、
`should_interrupt` は実質 `important and not occupied` に退化する。ポリシーの docstring は
これらのフィールドを "facts used to choose presentation surfaces" と呼んでいる。

**死んだコードの話ではない** — `routing_policy.py:78` は生きた経路で、
`PresentationRoutingPolicy().decide` は `autonomous_loop.py:3068` から呼ばれる。フィールドも
生きている（`expected_usefulness` を 0.4 にすると判定が反転する）ので、**既定値が答えを決めて
いる**。加えて `>=` は等しい既定値どうしで**割り込む側に倒れる**。

同名フィールドの既定値が**3 つ**ある: `ActionCandidate` は **0.0**、コスト表のフォールバックは
**0.2**、`PresentationRoutingContext` は **0.5**。「分からないとき」の答えが 1 つの名前に対して 3 つ。

> **訂正（2026-09-29、B-1③ の実測）** — 旧記録は `InitiativeCandidate` と書いていたが、**そのクラスは
> 存在しない**（実体は `autonomous/models.py:56` の `ActionCandidate`）。同じ実測で、この 3 値が
> **同じ量の 3 既定値ではない**ことも分かった: `0.0` は「**呼び出し側が指定しなかった**」、`0.2` は
> 「**レベルがコスト表に無い**」、`0.5` は**別の量**（`expected_usefulness` と比較されるルーティング側の
> 被演算子）。しかも `0.0` は **`src/` では一度も生成されない**（2 つの構築サイトは両方とも
> `interruption_cost=` を明示的に渡す。`0.0` に到達するのはテストだけ）。よって **③「1 つに寄せる」は
> 撤回** — 寄せると「分からない」の 3 種類が 1 つに潰れる（§4.3 型 3）。③ の**有効な残り**は
> 「同じ軸の答えを全部記録する」ことで、それはピンの拡張として実施した。
>
> 同じ関数 `_current_interruption_cost` は **4 つ目の値 `0.15`** も返す（`:708` agent state が無い /
> `:712` snapshot が例外）。旧ピンは `_RECORDED_COST_DEFAULT = 0.2` しか記録しておらず、
> **「1 つの名前・N 個の答え」という自分の主張を自分の軸で数え落としていた**。拡張で両方を固定した。

**修正しなかった理由**: コスト表の 2 値の入れ替えは**自律ループの発火間隔**を動かし、B-17 の修正は
「自律的な結果の usefulness とは何か」の設計判断。どちらもオーナー案件（B-11 / B-17）。

**ピンの形**（`tests/test_interruption_cost_vocabulary.py`、8 テスト、**変異 8/8 捕捉**）— 値はすべて
**発見**する: 受容表は import、コスト表は AST で**「フォールバック `.get(..., default)` のレシーバ」**
として同定（メソッド内には無関係な `{}` もあるため「唯一の dict」では不十分）、2 つのルーティング
フィールドの出所は **dict リテラルをキーで走査し囲む関数名を報告**。挙動側は
**既定値で割り込むこと**と**被演算子を下げると反転すること**の両方を assert するので、将来の修正は
「死んでいる」ではなく「空文化している」と読める。

**副産物（リポジトリの罠）**: `personal_ai/interruption.py` は **CRLF** で、`autonomous/` と
`presentation/` の兄弟は **LF**（`docs/*.md` も 65 中 46 が CRLF）。複数行の変異アンカーは
**その 1 ファイルだけ無言で "anchor not found"** になる。**改行は直さない**（誰も求めていない
リポジトリ全体の差分になる）。以後は 1 行アンカーを使う。

ai-server **1703 passed / 31 skipped**（1695 + 新規 8、実測 320 秒）。ruff clean。

### 5.9 live な数値表のドリフト — 「実測」と書いてある数字も測り直す（2026-09-29）

§5.8 の記録中、**同じ成果物の中の数値表を突き合わせて**気づいた。本レポートは §0 で測定値を持ち、
§1.1 のサーバ構成表でも各サーバのテスト数を書いている — **同じ量が 2 箇所**にある。そこで
**全行を実行して確かめた**（`pytest -q` / `npx vitest run` / `npx playwright test --list`）:

| 行 | 記載されていた値 | 実測（2026-09-29） |
|---|---|---|
| AI Server | 1597 passed / 31 skipped | **1703 → 1714 passed / 31 skipped**（同日、§5.10 の +11 後） |
| Browser Server | 62 passed | **100 passed** |
| Room Server | 14 passed | 14 passed ✓ |
| Dashboard (web-ui) | vitest **134** / Playwright 42 | vitest **144** / Playwright 42 |
| aegis-sdk-python | **6 failed / 17 passed** | **25 passed** |

**7 行中 4 行が古い。** しかも §0 は正しい値（1703 / 100 / 144 / 25）を持っていたので、
**同じファイルの中で 2 つの値が併存**していた — 読者にはどちらが正しいか判別できない（§4.3 型 9）。
原因は明快で、**P1-4（SDK 6 failed → 25 passed）・P1-7（browser 67 → 100）・P1-1（vitest 139 → 144）・
P1-5 後半（ai-server 1647 → …）が §0 だけを更新し、§1.1 を誰も見なかった**。台帳（§0.1）には
各コミットの正しい値が日付付きで残っているのに、**要約表のほうが置き去りにされた**。

**修正**: §1.1 を実測値に更新し、行の直下に「2026-09-29 に全行を実測した」と注記した（**日付付きの
実測**であって不変量ではない、という §4.3 クラス 9 の対策そのもの）。

#### 副次: egress テスト数の「食い違い」は食い違いではなかった

§0 の「egress 211/23（床 160）」を見て、記憶にある **234** と矛盾すると疑い、**測った**:

```
pytest -m egress --collect-only -q   →  234/1734 tests collected (1500 deselected)
pytest -m egress -q                  →  211 passed, 23 skipped, 1500 deselected
```

**疑いは誤りだった** — `AGENTS.md:446` は最初から正しく「**211 passed / 23 skipped**（234 tests
carry the `egress` marker）」と書いており、**211+23 = 234** で完全に整合する。§0 の「211/23」は
**合格/スキップの内訳**であって**マーカー総数ではない**。同じ数字を別々の意味で読むと食い違って
見える、というだけだった。**測ってから直す**（測らずに「211 → 234」と直していたら、正しい記述を
壊していた）。

ただし**本当に古い 2 箇所**が見つかった — どちらも「egress テスト数」を **164** と主張していた:

| 場所 | 修正前 | 修正後 |
|---|---|---|
| `AGENTS.md:555` | 「CI-enforced: **164** egress tests against a floor of 160」 | 「**234 egress-marked tests**（211 passed / 23 skipped）against a floor of 160」 |
| 本レポート §2 | 「CI 床 160（**実測 164**）」 | 「CI 床 160（実測 **234 marked / 211 passed / 23 skipped**）」 |

**164 は中間計測**（`470b000` の時点で「egress 211」と記録され、さらに前は 164 だった）で、
`AGENTS.md:446` だけが追随していた — これも**型 9**。

#### 検出器は作らない

散文の数値ドリフトを検出するテストは、**テストを 1 本足すたびに期待値を書き換える**必要があり、
除外リストと同じく**検出したい欠陥そのもの**になる。CI の床は**下限**なので「164 と書いてあるが
実際は 234」を捕まえられない。既存の方針どおり **live 文書から測定値を減らす**ほうが確実
（P2-1 で `docs/status.md` から数値を全部抜いたのと同じ判断）。**当面の運用**は「**数値表を編集する
前に、その表の全行を実行する**」— 本項はその運用で見つかった。

### 5.10 名簿のフォールバック — 検出器が「記述していたが検証していなかった」2 つの穴（2026-09-29, `ec15484`）

B-15 の検出器 `tests/test_server_roster.py` は、**2 つの fail-open を docstring と `_RECORDED_DRIFT`
の理由文に書いていた**。書いてあるのに**アサーションが 1 つも無かった** — どちらのフォールバックが
反転しても緑のままだった。B-15 の作業中に気づいたのは、§5.9 で数値表を突き合わせたのと同じ手順で、
**「散文の主張」と「実行される検査」を突き合わせた**から。

**さらに、その散文自体が誤っていた。** docstring は
`aegis_schema/models.py:223` を指して「**`ServerType.DEV`** の capability はどの id でも通る」と
書いていたが:

- `DEV` は **map に入っている**（`models.py:222`）。`DEV` の capability に `room-server.*` の id を
  渡すと**正しく拒否される**。
- 欠けているのは **`UNSPECIFIED`**。指していた行番号 `:223` も、実体は map の**最後の 1 行**（`AI`）
  であって欠落行ではない。

**2 年以上「検出器」として読まれてきた散文が、間違ったメンバー名を挙げていた。** これは
§4.3 クラス 10（死んだコード／散文は、誰も実行しない主張を運ぶ）そのもの。**散文を書くだけでは
固定にならない**、というのが本項の主題。

#### 実測（修正の判断材料）

```
room-server.room.foo  + server_type=PC           -> 整合検査で拒否
room-server.room.foo  + server_type=UNSPECIFIED  -> 構築成功   ← 検査が飛ぶ
browser-server.p.foo  + server_type=UNSPECIFIED  -> 構築成功   ← 検査が飛ぶ
weather.get_forecast  + server_type=UNSPECIFIED  -> id pattern で拒否（これは正しい）
```

`ServerType` は 7 メンバー、map は **6 つ**。`.get()` に既定値が無いので、**情報を足さないこと
（`UNSPECIFIED` を宣言すること）が検査を無効化する**。`server_type` は必須フィールドで既定値が
無いため、「明示的に 0 を渡す」だけで起きる。

#### 追加した 11 テスト（すべて発見方式）

| 何を | どう発見するか |
|---|---|
| `server_type → prefix` map | `models.py` の **AST**（ローカル変数なので import できない）。関数名で特定し、**dict リテラルが 1 つだけ**であることを assert |
| 飛ばされるメンバー集合 | `ServerType` の全メンバー − map のキー。**等式**で記録集合と比較 |
| 各メンバーの挙動 | 全メンバーを parametrize し、**mapped なら他人の id を拒否／unmapped なら受理**することを実行で確認 |
| 有効ゲートの既定値 | `permissions.py` の AST で `server_enabled_map.get(prefix, default)` の**レシーバ**を特定し、既定値を読む |
| フォールバックが到達不能な理由 | id pattern の prefix 集合（pattern から解析）× map のキー集合の**等式** |

**変異 6/6 捕捉**、すべて**期待したテストで**落ちることを確認:

| 変異 | 落ちるべきテスト |
|---|---|
| 有効ゲートの既定値を fail-closed に | 既定値の記録テスト |
| `UNSPECIFIED` を map に追加 | 飛ばされる集合の等式テスト |
| `DEV` を map から削除 | 飛ばされる集合の等式テスト |
| pattern が通すキーを map から削除 | 到達可能性テスト |
| **呼び出し側を改名**（発見が盲目化） | 既定値の記録テスト |
| **unmapped のフォールバックを fail-closed 化** | 挙動テスト（7 ケース中 1 つ） |

**変異の設計自体を 2 回やり直した**のが収穫: 最初の M5 は**代入側だけ**を改名したため、呼び出し側を
読む発見ロジックは無傷で緑のままだった（＝**変異が悪い**、テストではない）。M6 も `UNSPECIFIED` を
*別の* prefix に対応させたので「mapped なら拒否」が成立し続けた。**変異が捕まらないときは、まず
変異が対象を実際に動かしているか確認する。**

#### ついでに直したもの

同ファイルの **I001（import 整列）が既存で赤だった** — ruff は CI ゲートに入っておらず、テストは
lint されないため気づかれていなかった。1 行の修正なので同じコミットに含めた（コミットメッセージに
無関係な修正である旨を明記）。

ai-server **1714 passed / 31 skipped**（1703 + 新規 11、実測 328 秒）。ruff clean。

### 5.11 SDK とスキーマの capability id — 1 つの id 空間に、両方向に食い違う 2 つの検証器（2026-09-29, `ff17604`）

B-14 は §4.1 に「記録済み・未修正」として載っていた。今回それを**ピン**に変えた。これは doc の
食い違いではなく、**SDK という公開面が実際には動かない**という欠陥である。

#### 1 つの id 空間、2 つの検証器

`define_capability` は `aegis_schema.models.Capability` を返す — スキーマが `id` を拘束している、
まさにそのモデル。だが SDK が先に自前の regex で検証し、両者が一致しない。

| id | 形 | SDK regex | schema pattern |
|---|---|---|---|
| `weather.get_forecast` | SDK 自身の docstring の例 | **通す** | 弾く |
| `my_server.read_sensor` | SDK 自身の引数ヘルプ | **通す** | 弾く |
| `ai-server.get_forecast` | 名簿の prefix・短い形 | 弾く | **通す** |
| `pc-server.screenshot.get_screenshot` | **正準の 3 セグメント形** | 弾く | **通す** |

SDK の pattern は**開いたクラス**（`^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`）、スキーマは **12 prefix の
閉じた allowlist**。したがって単に広さが違うのではなく、**互いに相手が通す id を弾く**。

#### 3 つ目の欠陥 — 既定引数で通るのは削除済みサーバだけ

`define_capability` は `server_type` を**既定 `ServerType.DEV` のまま**にし、`server_prefix` から
導出しない。そのため**既定引数で構築できる prefix は `dev` ただ 1 つ** — Phase 9 で削除したサーバで
ある。名簿の prefix（`pc` など）を使うには呼び出し側が `server_type=ServerType.PC` を明示する必要が
あり、SDK はそれを必須とも書いていない。**既存の SDK テスト 11 件がすべて `dev` を名乗っているのは
そのため** — 緑だったのは偶然である。

#### 実測した帰結（すべて同じ穴に落ちる）

- `docs/plugin-sdk.md` の Quick Start（`server_prefix="weather"`）→ 素の pydantic `ValidationError`
- `capability.py` 自身の docstring の例 → 同じ
- `tools/create-capability-server` が生成する `server_prefix="{prefix}"` → `dev` 以外は import 時に落ちる
- **`examples/example-weather-server/weather_server.py` → import すら通らない**。しかも
  **リポジトリのどこからも参照されていない**（テストもスクリプトも CI も）— だから壊れたまま残った

#### ピン — `packages/aegis-sdk-python/tests/test_capability_id_contract.py`（8 関数 / 23 ケース）

両方の pattern を**実物から発見**する: スキーマは `Capability.model_fields["id"].metadata`
（コピーではないので本体から乖離できない）、SDK は `safety.py` を **AST** で読む（インラインの
リテラルで import 不可）。**食い違いそのもの**を等式で固定するので、**どちらを直しても落ちる**。
「修正」ではなく「記録」であることを docstring に明記した（`test_forced_gate_stays_retired.py` と
同じ形）。**変異 5/5 捕捉** — うち 2 件が教訓で、詳細は `AGENT_PROGRESS.md` に記録した:
example の `server_prefix="weather"` は **2 箇所**あるので 1 箇所だけの変異ではテストが動かない
（replace-all が必要）、そして発見を壊す変異は `FAILED` ではなく **collection ERROR（rc=2）**で出る
ので、ハーネスは `FAILED` を grep せず **`rc≠0` を捕捉**とする。

#### 判断待ち（どちらも製品判断）

1. **スキーマの regex を緩める** — 第三者 prefix を許す。SDK の約束（「AEGIS capability サーバを
   建てる道具」）に合わせる方向。
2. **SDK 側で明示的に断る** — 第三者 prefix は不可と宣言し、その旨を docstring / docs に書く。
   SDK の約束を狭める方向。

現状は最悪の組合せ — **SDK は第三者サーバを謳い、スキーマは黙って禁じている**。

#### 検証

ai-server **1714 passed / 31 skipped**（変化なし — ピンは SDK 側）。SDK **25 → 48 passed**。
room **14** / browser **100** も再実測して一致。ruff clean。`scripts/test-all-suites.ps1` は
**コメントから数を削除**（数は腐るので）— AST パース errors=0。live な SDK 数を 25 → 48 に更新
（`AGENTS.md` / §0 / §1.1 / `MEMORY.md`）。

### 5.12 `FORBIDDEN_CAPABILITIES` — 3 つあるはずの検査が、1 つも発火しない（2026-09-29, `2da2c37`）

B-12 は §4.1 に「記録済み・未修正」として載っていた最後の欠陥だった。今回それを**ピン**に変えた。
測ってみると、記録されていたより欠陥は**深く、そして無害**だった — この 2 つは両立する。

#### 記録されていたこと（すべて確認できた）

`settings/validation.py` の `FORBIDDEN_CAPABILITIES` は 39 件。**canonical 形（`server.app.action`）は
8 件だけ**で、すべて `pc-server.*`。残り **31 件は `browser.send_email` のような「短縮 prefix +
app_id なし」**。`validate_settings_change` は**完全一致**で照合するので、**canonical 形で書いた
同じ意図は素通りする**:

```
per_capability["browser.send_email"]              -> エラー 1 件
per_capability["browser-server.social.send_email"] -> エラー 0 件   ← 正しい綴り
```

守る相手の 1 つ `per_capability` は `permissions.py:89` が **canonical id** で引く。つまり
**ガードは、誰も使わない鍵空間を見ている**。

#### 今回わかったこと（記録より深い）

| 実測 | 値 |
|---|---|
| 39 件のうち `catalog.resolve()` で解決できるもの | **0 件**（canonical + alias を解決する唯一の関数） |
| 生きた 128 capability のうち**禁止 action を持つもの** | **0 件** |
| `validate_settings_change` のループのうち、エラーを積めるもの | **2 / 3**（`disabled_capabilities` のループは本体が `pass`） |
| その 2 つが拒否できる設定項目のうち、ゲートが実際に読むもの | **0 件**（短縮形の鍵はゲートに引かれない） |
| `EXPLICIT_DENY_PATTERNS` が覆う件数 | **5 / 39**（支払いとポリシー自己改変のみ） |

**① 守る相手が存在しない。** 生きた 128 capability に禁止 action は 1 つも無い。だからこの欠陥は
**見えない** — 発火しないガードは、正しく発火しているように見える。**② 3 つ目のループは空回り。**
`if cap_id in FORBIDDEN_CAPABILITIES: pass` — 条件が真でも何も積まない（AST で確認）。**③ 残る 2 つは
no-op な設定を拒否している。** 短縮形の鍵は `permissions.py` が引かないので、そもそも設定として
効かない。**④ 残り 34 件は別の機構が担っている** — egress 系はネットワーク層の egress ゲート、
`FORBIDDEN` を自称するものは `DEFAULT_RISK_MAP`、CAPTCHA / TOS はプロンプト。

結論を正直に書くと: **制約は危うくない。この一覧が危うい。** ガードは**自分自身の一覧とは整合して
いる**（`missed == []`）ので、一覧の中だけを見ている限り完璧に見える。

#### ピン — `ai-server/tests/test_forbidden_capabilities_dialect.py`（7 関数 / 13 ケース）

| 何を | どう固定するか |
|---|---|
| 方言の構成 | canonical 8 / 短縮 31 を**等式**で（prefix は正規表現で判別、手書き一覧にしない） |
| 一覧が何も指していないこと | 128 件の生きた id と突き合わせて **`== ()`** |
| 禁止 action が生きていないこと | 128 件の action 集合と交差して **`== ()`** |
| ガードが自分の綴りでは発火すること | 39 件すべてを回して **`missed == []`** |
| **正しい綴りでは発火しないこと** | canonical 形の witness 6 件 → **0 件**（素通りを固定） |
| 1 つ目のループが無力なこと | `validation.py` を **AST** で読み、ループごとに「エラーを積めるか」を判定 |
| ゲートの鍵の形 | `permissions.py` を AST で読み、`per_capability.get(…)` の**引数式**を集合で固定 |
| パターン被覆 | `EXPLICIT_DENY_PATTERNS` の件数を **`== 5`** |

ゲートが canonical id を引くことは**引数式の集合**（`["capability.id", "capability_id"]`）として
固定する — 1 箇所だけ見て「canonical だ」と結論すると、もう 1 箇所を見落とす。

#### 変異 6/6 捕捉

| 変異 | 落ちるべきテスト |
|---|---|
| 短縮形の 1 件を canonical 形に直す（= 修復） | 方言構成の等式 |
| canonical の 1 件を短縮形に戻す | 方言構成の等式 |
| `pass` ループに `errors.append` を足す（= 改善） | ループの能力判定 |
| ゲートの鍵を短縮形に変える | 鍵の形の集合 |
| パターンを 1 件足す | パターン被覆 |
| 一覧に生きた id を 1 件足す | 解決不能性の等式 |

**「改善」も落ちる**ように作ってある — 直した人は必ず記録を更新する（B-14 のピンと同じ形）。

#### 自作の誤りを 2 件、ピンが先に捕まえた

1. `per_capability` の期待値を**自分の実測と逆**に書いていた（短縮形を `False`、canonical を
   `True`）。テスト名まで逆だったので、**測った事実を書き写す**よう直した。
2. `per_capability.get` の呼び出しを **1 箇所**と決め打ちしたが、実行すると
   `expected one per_capability lookup, found 2` で落ちた — `evaluate` と `is_capability_enabled`
   の両方にある。**「1 箇所のはず」は測定ではない。**

#### 判断待ち（削除か修復か）

測定は**削除**に傾く — 守る相手が 0 件、3 ループ中 2 つが無効、名前が何も指していない。修復するなら
「id で照合する」をやめて **action で照合する**（照合の意味を変える設計判断）必要があり、一覧の
39 件を全部 canonical に書き直すだけでは**ゲートが読まない鍵空間のまま**である。ただし削除は
`docs/permissions.md`（65 / 76 / 85 行）が CAPTCHA の根拠としてこの一覧を引用しているため、
**文書の訂正を伴う**。B-13（`allowlist` の消費者ゼロ）と同じ面で、`FORBIDDEN_CAPABILITIES` の
3 ループ中 1 つを占めるため**巻き添えの判断**が要る。**`FORBIDDEN_CAPABILITIES` は保護された
面ではない** — これも本項の結論である。

#### 文書の訂正は先に済ませた（オーナー判断を待たない）

コードの削除はオーナー判断だが、**文書の主張が実測と食い違ったまま放置される理由は無い**ので、
この記録コミットで 4 文書を訂正した（P2-3 の `README.md` と同じ扱い — 誤った主張は測って直す）。

| 文書 | 修正前 | 修正後 |
|---|---|---|
| `docs/permissions.md` | CAPTCHA は「**Yes** — `FORBIDDEN_CAPABILITIES` ids, plus prompts」＝ 3 つの主張のうち唯一「強制されている」と書かれていた | **「Prompt-level only」**に統一（3 つが同じ分類になった）。表の当該行も「これは何も統治しない」に変更し、実測を節として追加 |
| `docs/pc-safety.md` | 「`_capability_from_manifest` が `RiskLevel.FORBIDDEN` で raise するので構築不能」 | **機構が誤っていた** — catalog に `forbidden` の manifest は **0 件**なので、この raise は発火し得ない。構築不能なのは**どの manifest も宣言していないから**（未登録として拒否される） |
| `docs/android-safety.md` | 「これらの id は deny-list の文字列」 | 記述自体は正しかったが、**一覧自体は拒否していない**ことを追記 |
| `docs/dev-safety.md` | 同上 | 同上 |

**残るオーナー判断はコードの削除だけ**になった。ピンの docstring もこの訂正に追随させた
（「訂正すべき」→「訂正した」）。

#### 検証

ai-server **1714 → 1727 passed / 31 skipped**（+13 = 新規テスト、実測 362 秒）。egress は
**211/23 のまま**（新テストはマーカーを持たない）。ruff clean / format clean。live な数を
1714 → 1727 に更新（`AGENTS.md` / `docs/architecture.md` ×3 / 本レポート §0・§1.1 / `MEMORY.md` /
`aegis-verify-and-test`）。文書訂正の影響範囲として 5 ファイル
（B-12 ピン / `test_guarded_settings_fields` / `test_server_docs_are_accurate` /
`test_readme_safety_model_matches_the_code` / `test_ineffective_flags`）を再実行して
**125 passed / 23 skipped**。全 suite は測り直していない（**テストに触れていない**ため —
触れたのは docstring のみ）。

### 5.13 A-1 — 死んだ deny 一覧を「修復」ではなく「削除」で決着させた（2026-09-29）

§0.2 の A-1 は推奨が「削除」で、測定も揃っていた（§5.12）ので実行した。

#### 決めたこと

`FORBIDDEN_CAPABILITIES`（39 件）とそれを参照する 3 ループ、`CapabilityPermissions.allowlist`、
`config/settings.json` の `"allowlist": []` を削除した。**修復を選ばなかった理由**は §5.12 の測定
そのもの — 守る相手が **0 件**、3 ループ中 **2 つが無効**、39 件の名前は**何も指していない**。
canonical 形に書き直しても**同じ死んだ鍵空間**を見るだけなので、「正しい綴りに直す」は選択肢に
ならない。

**残したもの**: 同じ関数の無関係な 2 検査（camera snapshot の有効化に確認を要求する検査、
`max_autonomous_runs_per_hour > 100` の検査）。`validate_settings_change` 自体は生きており、
`settings/store.py` から呼ばれている。

#### ピンは「記録」から「削除の証明」へ置換した

`test_forbidden_capabilities_dialect.py`（7 関数 / 13 ケース）は**欠陥の記録**だったので削除し、
`test_forbidden_capabilities_stay_retired.py`（11 ケース）を新設した。

**削除ピンは「定数が消えた」だけでは弱い** — その主張はシステムを弱めれば満たされる。そこで
3 つを併せて固定した: ① 実物の `ToolBroker` を駆動し、未登録 id が **`NOT_FOUND`（ポリシー評価の
前）**で拒否されること（`policy_decision` が空であることも assert する）、② 生きたゲートが
**`capability.id`** を鍵にしていること、③ `EXPLICIT_DENY_PATTERNS` が**支払い・egress 迂回・
ポリシー自己改変**の 3 意図群に今も一致すること。①が「**代わりの制御**」の証明で、これが無いと
「消しても安全だった」を誰も検証できない。

名前に依存しない側の守りとして、**バリデータが capability フィールドを 1 つも検閲していないこと**
（AST で発見、空集合と等式）も assert した — 名前を変えて戻しても落ちる。

#### 変異 14/14 捕捉

うち **2 件は検出器自身を盲目化する変異**（識別子走査の regex を不可能なパターンに、
capability フィールド走査を空返しに）で、これが無いと「消えている」系の assert が**空虚に通る**。
**1 件は修復方向**（記録済みの穴に消費者を足す）で、ピンが**欠陥ではなくピンを直す**ことで満たされ
ないようにした。**1 件は M4 の初回が SKIP になった** — `config/settings.json` が **CRLF** なので
`\n` アンカーが一致しなかった。**アンカーが一致しない変異は「捕捉されなかった変異」ではない**が、
SKIP を黙って通すと「捕捉した」と誤読するので、ハーネスは SKIP を失敗として数える。

#### 副産物 1: B-13 の検出器を広げたら、生きた 2 件目が即座に見つかった

B-13 のピンは `*.capabilities.<field>` だけを見ていた（最初の実例が `allowlist` だったため）。
A-1 でその対象が消えるので**全設定セクション**へ広げたところ、`max_autonomous_runs_per_hour` が
**バリデータだけに読まれ、他に消費者がいない**ことが判明した。自律ループは**ハードコードされた
予算**で動くので、この設定を編集しても挙動は変わらない（`> 100` を拒否するだけ）。

**既存の死にフラグ検出器が見逃していた** — `test_ineffective_flags.py` の `_readers()` は
識別子のテキスト一致なので、**バリデータを「読者」と数える**。同じフィールドに 2 つの検出器が
別の答えを返すのはこれが理由で、**効果について正しいのは B-13 側**。`_RECORDED_GAPS` に記録し、
§0.2 の **B-6** として起票した（同じ形の 22 件が既に `_UNOWNED_DEBT` にあるので、単独で決めず
そちらと一緒に扱うのが筋）。

#### 副産物 2: 「実測」と書いてある数値が、実は手計算だった

§4.1 の B-7 行は「検出器を自動発見に変え、**12 モデル 95 フィールド**を走査」と書いていた。
実測すると **当時 11 / 94、現在 11 / 93**。内訳を遡って特定した:

| 時点 | モデル | フィールド |
|---|---|---|
| `b73309e^`（削除前） | **12** | **106** |
| `b73309e`（`AutonomyProfile` 削除後） | **11** | **94** |
| 現在（A-1 後） | **11** | **93** |

**12 は削除前の値**（`AutonomyProfile` が 11 フィールド持っていた）、**95 は 106 からその 11 だけを
引いた手計算**で、親の `AEGISSettings.autonomy` という**参照フィールド 1 つを引き忘れている**
（106 − 11 − 1 = 94）。**引いて作った数は測った数ではない** — 型 9 の変種で、今回は「同じ量を
2 箇所に書く」ではなく「**測らずに差分で作る**」。`AutonomyProfile` のフィールド数は
`b73309e^` のモデルを読み込んで数えた（11）。

#### 検証

ai-server **1723 passed / 31 skipped**（実測 365 秒）。**1727 からの差 −4 は内訳まで一致させた** —
**−13**（削除した記録ピン）/ **+11**（新しい削除ピン）/ **−6 +5**（B-13 ピンを全セクションへ拡張、
守る集合が 3 → 2）/ **−1**（`test_ineffective_flags.py` の設定フィールド parametrize が
`CapabilityPermissions.allowlist` の 1 ケースを失った）。**差を内訳に分解できないなら、
削除したコードが実は覆われていた可能性を疑うべき**。

**文書の訂正**: `docs/permissions.md`（機制表から当該行を削除し、節を「削除された」に書き換え）/
`docs/pc-safety.md` / `docs/android-safety.md` / `docs/dev-safety.md`（3 本とも「一覧そのものが
拒否しているのではない」→「一覧は削除された」）/ `docs/settings.md`（`allowlist` 行を削除）/
`AGENTS.md` / `docs/architecture.md` ×3 / 本レポート §0・§1.1・§4.1・§0.2 / スキル 2 本 / `MEMORY.md`。

### 5.14 B-3 — 自律実行経路が 2 本あり、登録簿は死んだほうを「生」と書いていた（2026-09-29）

§5.1 の `motivation_arbiter` 行は「❌ **生** — `autonomous_controller.py` が import している」と
書いていた。**import は事実だが、その importer 自身が import 元ゼロ**である。

#### 測定: 入口は 2 つあり、走っているのは 1 つ

`docs/self-development.md` は冒頭のアーキテクチャ図で `AutonomousController` を**入口**として描き、
`tick()` で `AutonomousLoop` に繋いでいる。実測は逆:

| モジュール | import 元（`src/`・`tests/`・docs のコード全体） |
|---|---|
| `autonomous_loop` | `aegis_ai/runtime.py` ✅ **走っている** |
| `autonomous_controller` | **なし** |
| `motivation_arbiter` | `autonomous_controller.py` のみ（＝到達不能） |

`runtime.py:1586 _create_autonomous_loop` は `AutonomousLoop` を**直接**構築し、
`start_autonomous_if_enabled` から起動する。`AutonomousController` は約 700 行の「2 本目の入口」と
して存在するが、誰も起動しない。

#### 走査を 1 回間違えた — 死は推移する

最初の走査は「**パッケージ外から** import されているか」だけを問い、**5 つ**を到達不能と報告した。
`planner`（`autonomous_loop` 経由）・`l2_mind` / `l2_models`（パッケージ `__init__` 経由）は
**到達可能**で、正解は **2 つ**。**1 ホップの関係を数えて到達性と呼んではいけない**（§4.3 クラス 15）。
登録簿の誤りはこの型そのもので、**死んだ経路の上のコードは「呼び出し元がある」ように見える**。

#### 3 層目: 同じフィールド名で、死に方が 2 通り

`autonomous/` の中で `requires_approval` に触れるのは **7 箇所すべて `motivation_arbiter.py`**:

* `MotivationDecision.requires_approval` — 5 箇所で**書かれ**（`:214/:234/:254` は `t.requires_approval`
  から、`:320` は**別名** `best_task.requires_user_approval` から、`:332` はリテラル `False`）、
  **読むものは 1 つも無い**。
* `ExternalTask.requires_approval` — `:214/:234/:254` で**読まれている**が、その分岐
  （user / scheduled / event）は `ExternalTask` が**リポジトリのどこでも構築されない**ので到達不能。
  `_build_task_request` の `isinstance(task, ExternalTask)` の腕も同じ。

登録簿は前者だけを「**唯一の**真に削除可能な残骸」と書いていた。**「読者が 0」と「読者が到達不能」は
別の死**で、後者のほうが悪い — フィールドが**起こり得ないタスクについての主張**になる。
`decide()` の 3 分岐は本番で一度も走っていない。

#### ピン（記録であって修復ではない）

`tests/test_autonomous_execution_path_is_single.py`（8 関数）。**配線しても削除しても落ちる**ので、
判断は必ず意識的に行われる。`docs/self-development.md` の図の訂正は**オーナー判断**（その図が
「こう動くべき」なのか「こう動いている」の書き間違いなのかは、私には決められない）— ただし
**図が実測と食い違っているという事実**は doc に注記した（**事実の記録は判断ではない**）。

#### 変異 10/10 捕捉 — うち 1 件は自作の誤り

**変異が捕まらないときは、まず変異が対象を実際に動かしているか確認する。** 最初の M3 は
`import AutonomousLoop as _RenamedLoop` で、**部分文字列は残り、経路も動く**ので緑のままで正しい —
**ハーネスの期待が誤っていた**。ただしこれで**検査が空白依存の部分文字列だった**ことも判明したので、
同じファイルの他の assert と揃えて **AST に置換**した（`_runtime_imports_from` /
`_runtime_constructs` — `alias.name` は別名でも**元の名前**なので、綴りではなく名前を見る）。
置換後に M3 を 3 通り（モジュール移動 / 名前入替 / 構築だけ削除）に分けて再実行し、**すべて捕捉**。

**M8（検出器を盲目化）が最も有用だった**: `_SRC` を存在しないディレクトリに向けると 8 件中 **5 件が
落ち、2 件は空虚に緑のまま**（`test_the_documented_entry_point_has_no_importers_at_all` と
`test_external_task_is_never_constructed` — どちらも**空集合**を assert するため。残る 1 件
`test_the_dead_decisions_still_carry_the_approval_field` は走査を使わないので無関係）。
ガード `test_the_scan_actually_sees_imports` が**肯定の観測**を assert している唯一の理由がこれで、
その数字を docstring に書いた。**「消えている」ことを assert するテストは、走査が壊れると空虚に通る。**

#### 検証

ai-server **1726 → 1734 passed / 31 skipped**（**+8 = 新規 8 関数**、実測 388 秒）。
原ファイル 5 本はバイト単位で復元（sha256 検証）。

**記録の訂正**: §5.1 の `motivation_arbiter` 行（判定そのものが誤り）・§5.4 の
`motivation_arbiter.requires_approval` 行（「唯一」ではない）・§0.2 の B-3 行（前提が崩れた）・
§4.3 にクラス 15 を新設。**訂正しなかったもの**: `AGENT_PROGRESS.md:820` の `runtime.py:1618` は
`reflection_engine` に係る記述で**正しい**（`motivation_arbiter` に係るものと読み違えていた —
**行番号だけを grep して主語を確かめないと、正しい記述を誤りとして「訂正」してしまう**）。

### 5.15 B-20 — スキーマは 27 の境界を宣言し、生きた書き込み経路は 1 つしか検査しない（2026-09-29）

B-6（`max_autonomous_runs_per_hour` を配線するか削除するか）を測りにいったら、その行の
**一段下に別の欠陥**があった。

#### 測定

`AEGISSettings` とそのサブモデルは **27 フィールド**に `ge`/`le` の境界を宣言している
（`memory.episodic_retention_days` は `ge=1, le=365`、`autonomous.max_tasks_per_cycle` は `le=20`）。
これらは**構築時**に強制される。しかし生きたプロセスの唯一の書き込み経路は
`SettingsStore.update_section` で、これは提案設定を**無検証の `setattr`** で組み立ててから
`validate_settings_change` を呼ぶ:

```python
for key, value in values.items():
    if hasattr(section_obj, key):
        setattr(section_obj, key, value)      # ← 検証なし
return self.update(current, changed_by, reason)
```

そしてバリデータが再検査する境界は **1 つだけ** — `max_autonomous_runs_per_hour > 100`。
これはそのフィールド自身の `le=100` の**写し**である。

| 区分 | 件数 |
|---|---|
| スキーマが宣言する境界 | **27** |
| 書き込み経路が再検査する境界 | **1** |
| 書き込み経路が素通りさせる境界 | **26** |

**推論ではなく実測**: 実物の `SettingsStore` を `tmp_path` に対して 1 フィールドずつ駆動し、
違反値が**受理され**、**読み戻しても残っている**ことを確認した。26/26 が突破、1/1 が阻止。

#### 仮説を 2 回外した

1. **「バリデータの検査は発火しない」→ 誤り。** `le=100` があるので構築は `101` を拒否する。
   ところが**代入は検証されない**（`validate_assignment` はどこにも設定されていない）。
   `update_section` は `setattr` するので、検査は**到達可能**である。**むしろ逆向きに重要**だった —
   つまりこの検査はこの経路のための唯一の防波堤であり、**そこに 1 つだけ手書きされている**。
2. **自作の走査が「guard」という部分文字列で偽陽性**を出した。クラス名
   `SettingsPermissionGuard` が `VALIDATION_HINTS` の `guard` に一致し、`clipboard_capture_enabled`
   など 5 件を「検証専用」と誤判定した。実際は `permissions.py` の**生きたゲート**である。
   **自分の発見器を疑ってから結論を書く。**

#### なぜ化粧ではないか

突破できる集合に**保持期間の上限**が入っており、それは実際の削除計算に届く。
`backup/retention.py:49` は `settings.memory.episodic_retention_days` を `max_age_ms` に変換して
prune するので、スキーマが拒否する値（`le=365`）で**1 世紀分のエピソードを保持**できる。
ピンはこの 2 つを**設定オブジェクトで繋いで**駆動する（走査ではなく）。

同じモジュールの docstring は 4 つの保持を "Handles:" として並べていたが、実測は:

| 保持 | 実測 |
|---|---|
| Episodic | ✅ **強制されている**（`cleanup_expired` が prune する） |
| Notification | ⚠️ `get_retention_status()` が**報告するだけ**。何も削除しない |
| Screenshot | ⚠️ 同上。実際の削除は `personal_data/core.py`（`policy.py` 経由） |
| Audit | ❌ **`self._audit` は `__init__` で保存され、どのメソッドも読まない** |

**「報告だけ」は UI からは実装済みに見える** — ダッシュボードに値が出るので、削除も動いていると
読める。docstring は測定に合わせて訂正した（**誤った主張の訂正はオーナー判断ではない**）。

#### ピン（記録であって修復ではない）

`tests/test_settings_edit_path_enforces_schema_bounds.py`（6 関数）。境界は**モデル自身から発見**し、
バリデータの読みは **AST から発見**し、突破の有無は**実物のストアを駆動して**判定する。
突破集合と阻止集合は**両方向の等式**で固定するので、**書き込み経路を直してもピンが落ちる**。

バリデータを 27 個の境界を再検査するよう**拡張しない** — それはスキーマの写しを書き込み経路に
置くことで、このリポジトリが繰り返し見つけている重複そのものである。docstring にその理由を書いた。

#### 変異 10/10 捕捉 — 2 件はハーネスの誤り

**M5 は緑のままだった** — `max_tasks_per_cycle` から `le` を落としても `ge=1` が残るので、
フィールドは**探索集合に残り**、観測が変わらない。**変異が対象を動かしていない**（自分のミス）。
両方の境界を落として再実行したら捕捉した。

**M4 は rc=2（collection ERROR）で「捕捉できなかった」と読めた** — 実際は
`model_config = ConfigDict(...)` と書いたが `models.py` は `ConfigDict` を import していないので、
**変異が `NameError` で適用されていなかった**。プレーンな dict に直したら捕捉した。
**ハーネスは `FAILED` と `ERROR` の両方を集めるが、それでも足りない — ERROR の*原因*を読むこと。**
自分の変異が壊れている場合、それは「捕捉されなかった変異」ではない。

**修復方向の変異を 3 つ入れた**: バリデータに 2 つ目の境界を足す（M2）・`update_section` が検証済み
モデルを構築する（M3）・`validate_assignment` を有効化する（M4）。**3 つとも落ちる**ので、
どの修復を選んでも記録は更新を強制される。加えて `RetentionManager` が保持値をクランプする変異（M8）
も落ちる。

#### 検証

ai-server **1734 → 1740 passed / 31 skipped**（**+6 = 新規 6 関数**）。原ファイル 5 本はバイト単位で
復元（sha256 検証）。ruff clean。

**記録**: §0.2 に **A-9**、§4.3 に**クラス 16**、本節、台帳、`retention.py` の docstring 訂正。

### 5.16 B-21 — 設定画面は「何も変えないスイッチ」を 10 個見せている（2026-09-29）

B-6 の測定中に見つけた。B-6 は未読フィールドの集合を**バックエンド側**で固定するが、
その集合が**利用者に見えているか**は誰も測っていなかった。`web-ui/src/pages/Settings.tsx` の
`editableSettings` は `GET /api/settings`（= `AEGISSettings.model_dump()`）からコントロールを
**発見**するので、UI 側に名簿は無い — つまり**古くならない代わりに、何でも出す**。

**実測**（すべて実物から）:

| 量 | 値 |
|---|---|
| ペイロード内のフィールド | **80** |
| コントロールとして描画される | **26**（`result.length >= 24` で切って `slice(0, 32)`） |
| `_UNOWNED_DEBT` / `_INTENTIONALLY_UNREAD` の記録 | **23** |
| **描画され、かつ誰も読まない** | **10** |
| `preferred` の鍵 | **15**（うち **5 件はどのフィールドとも一致しない**） |

10 個の内訳は `autonomous.*` が 8・`servers.*` が 2。`_UNOWNED_DEBT` の
`sensitive_data_storage_enabled` の項が既に書いていた「何もしないプライバシースイッチは、
スイッチが無いより悪い」が、**そのまま 10 個ぶん現実になっている**。

**可視集合は宣言順の事故である** — 切り捨てが `result.length`（**描画された**数）で数えるので、
早い位置にフィールドを足すと末尾が窓から落ちる。実測: `autonomous` の早い位置に 2 つ足すと、
記録済みの死んだフィールドが 1 つ可視窓から**押し出される**（変異 M11）。**誰も記録を触って
いないのに、設定画面の中身が変わる。**

#### 自分の走査の盲点を 2 つ、実行が捕まえた

このピンを書く過程で、**ピン自身が 2 回壊れていた**。どちらも「走らせたから分かった」:

1. **語彙が違う 2 つの集合を交差させていた** — 負債の記録はフィールドを**クラス**で名指し
   （`AutonomousSettings.max_actions_per_hour`）、UI のペイロードは**セクション**で名指し
   （`autonomous.max_actions_per_hour`）。交差は**恒偽ではなく恒空**になる。翻訳は
   `AEGISSettings.model_fields` の annotation から**導出**する形にした（写しを作らない）。
2. **`_UNOWNED_DEBT` は注釈付き代入**（`_UNOWNED_DEBT: dict[str, str] = {...}`）なので、
   `ast.Assign` だけを見る走査は**空集合を返す**。`∅ == ∅` は真なので、その上に書いた `==` は
   どちらの向きも通ってしまう。両方のノード種別を扱い、`test_the_debt_record_is_readable` が
   **件数を assert** して空を検出するようにした。

**変異 18/18 捕捉**（原ファイル 4 本をバイト単位で復元・sha256 検証）。うち **3 件は
「捕捉されないこと」が期待値** — `==` を `<=` / `>=` に弱めた版に、片方向だけ動く変異を当てると
**どちらも無音**である（W1〜W3）。つまり**等式の両方向がそれぞれ load-bearing**で、片方だけでは
足りない。**変異は「テストが load-bearing か」ではなく「アサーションの向きが load-bearing か」を
測る**ので、`==` を書いたら**両方向に 1 つずつ**当てる。なお M12（切り捨てを 200 に上げる）は
**最初のピンでは無音だった** — 遅い位置のプローブを隠していたのが切り捨てではなく `slice` で、
テストが**間違った理由で緑**になっていた。スライスを無効化した描画を足して、切り捨てだけが
説明できる形に直した（**テストが緑なのは、主張が正しいからとは限らない**）。

**記録であって修復ではない**。`preferred` の死んだ 5 件は**消せば挙動が変わらない**（一致しない
鍵は既に何もしていない）ので **A-10** として一言で決まる形にし、10 個の死んだコントロールは
**フィールドの去就そのもの**なので **B-6 の行に利用者側の帰結として追記**した。

#### 検証

ai-server **1740 → 1756 passed / 31 skipped**（**+16 = 新規 6 関数 + 10 parametrize**、実測 375 秒）。
原ファイル 4 本はバイト単位で復元（sha256 検証）。ruff clean。

**記録**: §0.2 に **A-10** と **B-6 の追記**、§4.3 に**クラス 17**、本節、台帳。あわせて
**台帳自身の型 9 を 2 件訂正**（C-3 のクラス数「12」— §4.3 は既に 16 だった／A-5 の「本日だけで
12 回」）— 台帳は「測定値を書かない」と自称しながら、この 2 行が数を持ち、片方が既に古くなっていた。

**副産物 — 台帳の egress 値も 1 ずれていた**: §0 の「egress 211/23（床 160）」を測り直すと
**210 passed / 23 skipped（233 件がマーカー付き）**。原因まで特定できた — A-1 が
`test_ineffective_flags.py` の parametrize を 1 ケース失ったとき、**総数の −1 は記録したが
egress の数は測り直していなかった**（234 → 233 / 211 → 210）。**変更が「2 つ目の量」に与える
影響は、測らないと見えない**（型 9 の変種で、こちらは同じ量ではなく**派生する量**）。
ファイル内訳も記録する: closure 36 / gate 53 / reliability 10 / ineffective_flags 109 /
local_llm_path 25 = **233**。

### 5.17 A-9 — 設定の書き込み経路が、スキーマの境界を強制するようになった（2026-09-29）

§0.2 の A-9 は「① `update_section` が検証済みモデルを構築する」が推奨で、測定もピンも揃っていた
ので実行した（A-1 と同じ判断）。

**変更**: `SettingsStore.update_section` は提案設定を **`setattr` で組み立てる**のをやめ、現在の
ダンプに要求されたキーを重ねて `AEGISSettings.model_validate` に通す。未知のセクション・未知の
フィールドの拒否はそのまま（`hasattr` ではなく `model_fields` で判定するようにしたので、
メソッド名を渡しても通らない）。`ValidationError` は `section.field: <msg>` に整形して `list[str]`
契約を保つ。

**実測（修復前 → 修復後）**: 境界を突破できるフィールド **26 → 0**、阻止 **1 → 27**（実物の
`SettingsStore` を `tmp_path` に対して 1 フィールドずつ駆動して確認）。境界値は受理される
（`episodic_retention_days` は 365 が通り 366 が拒否される）。**意味論的な検査は生きている** —
`privacy.camera_snapshot_enabled` を有効化すると今も確認を求める（これはスキーマで表現できない
ので、スキーマに寄せても消えない）。

**バリデータの写しは残した。** `validate_settings_change` の
`max_autonomous_runs_per_hour > 100` は、構築が先に拒否するので**ストア経由では到達不能**に
なった（`update` / `update_section` / `import_json` のいずれからも）。それでも消さなかった理由は
2 つ: この関数は `settings/__init__.py` が再輸出する **public** な関数で契約がストアから独立して
いること、そして消すと `tests/test_guarded_settings_fields.py` が記録している**唯一の実例**が
消え、`_RECORDED_GAPS` が空になってあのファイルの検出器が対象を失うこと。**判断はピンとソースの
コメントの両方に書いた** — 「残した」理由を書かないと、次に読む者は「気づかなかった」と読む。

**ピンは「記録」から「回帰ピン」へ。** `_RECORDED_BYPASSED` は **∅**、`_RECORDED_ENFORCED` は
**27 件**（旧 2 集合の和）。あわせて 2 つ足した: ① **2 つの集合が発見した全フィールドを分割して
いること**を assert する（片方が黙って短くなるのを防ぐ）、② **各フィールドに合法な値を入れて通る
ことを確かめる**（境界値を含む）。②が必要なのは、**`blocked == 27` は「すべて拒否するストア」でも
満たされる**からで、**「満杯の集合」も空虚になりうる** — B-3 で学んだ「空集合を assert する
ガードは走査が壊れると空虚に真」の裏返し。

**変異 12/12 捕捉**（原ファイル 4 本をバイト単位で復元・sha256 検証）。内訳: 欠陥を戻す 2 通り
（`setattr` に戻す / `model_construct` を使う）・**全拒否**・記録の増減・**新しい境界付き
フィールドの宣言**・境界の削除・**拒否された修復**（バリデータに 2 つ目の境界を足す）・
`_legal_value` の反転・プローブ生成器の盲目化。**うち 2 件は「捕捉されないこと」が期待値** —
`==` を両方とも包含に弱めると、欠陥が戻っても**等式テストは無音**になる（保持期間のテストだけが
捕まえる）。つまり**等式の両方向が load-bearing**で、**保持期間のテストは 2 番目の防波堤**である。

**ハーネス自身の欠陥を 1 つ踏んだ**: 同じファイルへの 2 つ目の編集を**元のバイト列**から作り直して
いたので、1 つ目が無言で上書きされ、W1/W2 が「捕捉された」と誤って報告された。**このリポジトリが
既に記録している「同一ファイルの複数領域を 1 度に編集するな」と同じ罠**を自分の道具で踏んだ。
編集をファイルごとに**蓄積**するよう直したら、2 件とも期待どおり無音になった。

**副産物**: `tests/test_guarded_settings_fields.py` の**既存 I001** を修正。`src/` と `tests/` では
`aegis_ai` の扱いが違う（前者は first-party、後者は third-party）ので、**同じ import が場所に
よって別の並びになる**。また **`ruff format` はこのリポジトリの規約ではない**ことを実測した
（未変更のファイルも reformat 対象になる）ので、**`ruff check` だけ**を満たすようにした。

#### 検証

ai-server **1756 → 1758 passed / 31 skipped**（**+2 = 新規 2 関数**、実測 406 秒）。egress は
**210/23 のまま**（このピンはマーカーを持たない）。原ファイル 4 本はバイト単位で復元（sha256 検証）。
`ruff check` clean。

**記録**: §0.2 から **A-9 を削除**（決定・実行済み — レジスタは短くなる一方であるべき）、§4.3
**クラス 16 に修復済みの注記**、本節、台帳。

### P2 — 衛生・長期

| # | アクション |
|---|---|
| P2-0 | ✅ **完了** — `scripts/test-all-suites.ps1` を追加。**制約ゲート（`test-ai-server.ps1`）に委譲**したうえで SDK 25 / room 14 / browser 100 を走らせる。**今まで誰も走らせていなかった 139 テスト**が対象になり、「SDK が 6 件赤のまま誰も気づかない」原因が消える。`web-ui`（vitest / playwright）は node ツールチェーンとブラウザ実体が要るため対象外のまま。**注**: この環境の PowerShell ツールは**ネイティブ実行ファイルを起動できない**（`& python` も `& hostname.exe` も出力・`$LASTEXITCODE` とも空。エラーも出ない）ため、**スクリプト自体は実行検証できていない** — AST パースで構文を、Bash から各スイートを個別に実行して中身を検証した（§0 のスキルに記録） |
| P2-1 | ✅ **完了** — `docs/status.md` / `implementation-status.md` / `backlog.md` / `roadmap.md` の 4 本を **`docs/status.md` 1 本に統合**（61 → 58 ファイル）。**新文書は測定値を一切持たない**設計にした — 数値は `PROJECT_STATUS_REVIEW.md` と `AGENTS.md` を指すだけなので、**型 9（同じ量を 2 箇所に書く）の入口が存在しない**。参照 5 箇所（`README.md` 3 行 → 1 行、`docs/architecture.md`、`IMPROVEMENT_PROPOSAL.md` ×2）も同時に更新 |
| P2-2 | ✅ **完了**（**A-4**、2026-09-29）— `.aegis-local/` の **1.4 GB を削除**（オーナー判断「削除する／全部」）。git 管理外で削除は不可逆なので、先に**再生成可能性を実測**した: SHA 名のアーカイブ **16 本はすべて履歴に実在**（`git cat-file -e`、欠落 **0**）＝ `git archive` で再生成できるが、**残り約 21 本は説明的な名前で SHA を持たない**ため**名前からは再生成できない** — つまり「全部が再生成可能」ではなかった。**2026-09-30 実測**: ディレクトリは**空で再出現**（0 ファイル / 0 バイト）。`src/` に書き込むコードは無く、参照はテスト 2 本（`.gitignore` 検査・走査の `_SKIP_DIRS`）だけ |
| P2-3 | ✅ **完了**（`b32f396`）— 「`approval` で再 grep する運用」を**実測**に置き換えた（§5.5）。**57 文書が approval に言及、48 が訂正バナーを持つ**。残る 9 のうち **8 は ADR（定義上、履歴記録）か本文で自訂正済み**で、**誤りは 1 件だけ**だった: `README.md`。玄関が退役したはしごを掲げ、コードと正反対を書いていた。検出器は**書かず**（除外リストは検出したい欠陥そのもの）、誤っていた 1 箇所をコードに対して固定 |
| P2-4 | **未決の論点**: `/approve` `/modify-and-approve` `/cancel` の **fresh passkey（15 分）が比例しているか**（「最小の割り込み」として重い） |
| P2-5 | 長期: vision のローカル化 / gRPC TLS 統合 / Room 実機プロバイダ / cross-device context / 音声 I/O / multi-user |
| P2-6 | ⏸ **実測済み・オーナー確認待ち**（`d4aae94`）— `aegis_ai/evaluation/` の死んだ部分グラフ（1,104 行）を**削除するか配線するか**。`495105e` 自身がオーナー判断待ちに含めている。**配線するなら期待の書き直しが製品判断**（`delete_file` → `ALLOW_WITH_AUDIT` は**今は正しい**）。固定済みなので**急がない**（§5.7） |
| P2-7 | ⏸ **B-1 と同じ判断**（**正典は §0.2 の B-1**）— ① コスト表の中央 2 値を入れ替えるか（**自律ループの発火間隔が動く**）② 自律的な結果の `expected_usefulness` / `interruption_cost` に実値を入れるか（**判定の第 3 項が今は定数**）。~~③ 同名フィールドの既定値 **0.0 / 0.2 / 0.5** を 1 つに寄せる~~ **③ は撤回**（2026-09-29 実測: 3 値は同じ量の 3 既定値ではなく「分からない」の 3 種類だった — §5.8 / §4.3 型 3）。① と ② は 1 行の変更だが挙動の判断 |

---

### 5.18 A-2 — SDK が第三者 prefix を「明示的に断る」側で決着（2026-09-29）

**決めたこと。** オーナーは A-2 の二択のうち **②「SDK が明示的に断る」** を選んだ。スキーマの
allowlist はそのまま（id 空間は名簿のもの）で、SDK が**呼び出し地点で**断る。

**実装に入って分けた 3 つの欠陥。** §4.1 の B-14 は「SDK とスキーマが両方向に食い違う」と記録して
いたが、直す対象は 3 つあった:

| # | 欠陥 | 直し方 |
|---|---|---|
| 1 | SDK が**開いたクラス**の regex を持っていた（`^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`）ので、任意 prefix を通していた | `safety.py` の自前 regex を**削除**し、`aegis_schema.models.CAPABILITY_ID_PATTERN` を **import** する。**規則が 1 つ**になる |
| 2 | 拒否の**言い方が悪い** — 素の pydantic `ValidationError` が「呼び手が指定していない `server_type`」を名指ししていた | prefix が名簿に無ければ、**prefix を名指しして許される 12 個を列挙**する `ValueError` を SDK が投げる。`ValidationError` は `ValueError` の派生なので**型だけでは足りない** — テストは `type(exc) is ValueError` を assert する |
| 3 | `server_type` が既定 `ServerType.DEV`（Phase 9 で削除したサーバ）で、prefix から導出していなかった。**既定引数で通る prefix は `dev` ただ 1 つ** | 既定を `None` にし、名簿から**導出**する。prefix と矛盾する `server_type` を明示したら拒否する |

**規則を 1 つにするために名前を与えた。** `models.py:124` の pattern はリテラルだったので
`CAPABILITY_ID_PATTERN` という定数にし、`Field(pattern=...)` がそれを参照するようにした。
**バイト単位で同一**であること、`test_server_roster.py` が読む「先頭の選択肢」の形が保たれることを
**測ってから**進めた。名簿から**導出**しない理由は循環（`roster` が `ServerType` をこのモジュールから
import しており、クラス本体では遅延できない）— 両者の一致は既存の等式テストが守っている。

**動かないまま出荷されていた 3 つの成果物。** B-14 の実害はここだった:

| 成果物 | 直した内容 |
|---|---|
| `docs/plugin-sdk.md` の Quick Start | `server_prefix="weather"` → `room-server`、`action` に `weather.` を前置。**id の規則**の節を追加 |
| `examples/example-weather-server/weather_server.py` | **import すら通らなかった**。`room-server.weather.{get_forecast,get_current}` に。I001 も解消 |
| `tools/create-capability-server` | `--name` を prefix にしていた（`--name weather` は必ず落ちる）。**`--type` から名簿経由で導出**し、未知の `--type` は拒否。既定 `dev` → `room`。`--type room-server` が `ServerType.ROOM-SERVER` に化けないよう、大文字化ではなく名簿から member 名を引く |

**正準形の確認（実装前の測定）。** `folder_registry._derive_ids` は id を
`{server_id}.{app_id}.{action}` として**パスから**導出し、`capability_catalog.py:11` は
`pc.screenshot.get_screenshot` を **old prefix** と呼ぶ。つまり正準は**長い形**（`room-server`）で、
短い形（`room`）は別名。だから例と scaffold は長い形にした。

**ピンは「食い違い」から「契約」へ張り替えた。** 旧ピンは両方向の食い違いを等式で固定していたので、
どちらかを直すと**必ず落ちる**設計だった（それが役目）。いまは逆で、**一致そのもの**を固定する:

- SDK が持つ id 規則は 1 つで、それはスキーマの定数（`safety.py` に inline regex が戻れば落ちる）
- 12 個の id 標本について **SDK の判定 == スキーマの判定**（かつ標本が**両方の判定を含む**ことを assert）
- 第三者 prefix は**名前を挙げて**断られ、しかも `type(exc) is ValueError`
- **12 prefix すべて**が既定引数で構築できる（旧: `dev` のみ）
- **成果物を実行する** — docstring の例は AST で抜いて実行、example は import して登録・呼び出しまで、
  scaffold は生成して生成物を import

**実測（2026-09-29）。** SDK **48 → 69 passed**（+21。うちピン単体は **23 → 44 ケース**、成果物の実行系が
4 本）。ai-server **1758 passed / 31 skipped**（変更前と同数 — `models.py` の定数化は挙動を変えていない）。
`test_sdk.py` の 11 件が名乗っていた `dev` を **`room` に移した**（借り物の身元を返した）。ruff は SDK で
6 → 3 件（残り 3 件は既存: `registration.py` の BLE001 ×2、`testing.py` の I001）。

**変異 5/5 捕捉**（ピン単体で baseline 44 passed、各変異の落ち方を実測）:

| 変異 | 落ちたもの |
|---|---|
| ① 丁寧な断りを消す（prefix 検査が発火しない） | 拒否テスト 4 本。**一致テストは落ちない** — 断りを消しても pydantic が同じ id を拒否するので、**最終判定は一致したまま**だから。つまり「SDK が自分で断る」ことを固定しているのは拒否テストであって一致テストではない |
| ② `server_type` の既定を `DEV` に戻す | 導出テスト 18 本 |
| ③ `safety.py` に自前 regex を戻す（**挙動は変えない** no-op として置く） | `test_the_sdk_carries_no_second_id_pattern` **1 本だけ** — 規則 1 つの検出器が単独で効いている |
| ④ docstring の例を `weather` に戻す | `test_the_docstring_example_builds` **1 本だけ** |
| ⑤ scaffold の prefix を `--name` に戻す | `test_the_scaffold_generates_a_server_that_builds` **1 本だけ** |

**副産物の教訓（同日 2 件、いずれも道具の使い方）。**

- **同じファイルへの編集を並列に投げると、片方が消える。** この作業中に **4 回**起きた（scaffold で 2 回、
  example で 1 回、`capability.py` の docstring で 1 回）。`Edit` は**成功を返すのに内容が入っていない**
  ので、**編集後は必ずその領域を読み返す**（§1.0d の「構造編集の後は読み返す」と同じ規律）。
  **とくに厄介なのは、消えた編集が「妥当な別解」だった場合** — `capability.py` の docstring は
  `room` のまま残ったが `room` も許される prefix なので、**テストは緑のまま**だった。緑は「意図どおり」
  の証拠にならない。
- **MSYS の `/tmp` は Windows の Python には存在しないパス。** `mktemp -d` の戻り値をそのまま
  `--output` に渡すと `\tmp\...` として解決され `FileNotFoundError`。`$TEMP` 由来の Windows パスを使う。

**残置の回収（同日、A-2 の続き）。** 上のピンには「記録したが未処理」の残置が 1 つあり、それを直す
過程で scaffold の自己申告の欠陥が 2 つ出た。3 つとも**同じ型**（主張はあるが誰も走らせない／
検査が片方向しか見ていない）:

| # | 主張 | 実測 |
|---|---|---|
| **R1** | 断り文が「許される prefix」を列挙している | 旧 assert は `for x in ALLOWED: assert x in message`。**追加を見られない**（SDK が拒否する prefix を列挙しても緑）うえ、`"room" in "...'room-server'..."` は `True` なので**短い形と長い形を区別できない** |
| **R2** | scaffold の docstring は生成物 **4** つ（"Proto file stub" を含む） | **3** つしか書かない — proto stub は存在しない |
| **R3** | `python create_server.py --name … --type …` | `aegis_schema` が import できないと**失敗**する（説明付き `SystemExit`）。`--type` から prefix を導出するので `ai-server/src` が要るのに、Usage も `docs/plugin-sdk.md` も書いていなかった |

**R1 の直し方。** メッセージからタプルを **parse して丸ごと比較**する（`_listed_prefixes`）。
**変異（ピン単体 baseline 46 passed）:**

| 変異 | 落ちたもの |
|---|---|
| ① メッセージが prefix を 1 つ落とす | 拒否テスト 4 本 |
| ② メッセージが SDK の拒否する prefix を**追加**する | 拒否テスト 4 本 |
| ③ メッセージを手書きで書き直す（長い形→短い形） | 拒否テスト 4 本 |
| ④ `_listed_prefixes` が常に名簿を返す（parse をやめる） | `test_the_listed_prefixes_parser_reads_the_message_not_a_constant` **1 本だけ** |
| **期待外れ（緑が正解）**: 旧 assert + 変異② | **緑** — 旧 assert は追加を見ていなかった |

最後の行が「厳しくした形が効いている」証拠。これが無いと cosmetic な書き換えと区別できない。

**R2/R3 の直し方。** 生成物一覧を 3 つに直し、Usage に `PYTHONPATH=ai-server/src` を明記。
**R3 は散文の訂正で終わらせず走らせた** — `test_the_documented_scaffold_command_can_actually_run`
が docstring から `PYTHONPATH=...` を抜き、**継承した `PYTHONPATH` を消した環境**でその値だけを
入れて scaffold を subprocess 実行し、生成物が出ることを assert する。Usage から PYTHONPATH を
消せば赤くなる（型 11）。

**実測。** SDK **69 → 71 passed**（+2 = 新テスト 2 本。R1 の書き換えはテスト数を増やさない）。
ruff は当該 2 ファイルとも clean。ai-server は対象ファイルを含まないので再実行していない。

---

## 6. 参照

- 目標と制約: `AGENTS.md`、`docs/GOAL-CHANGE.md`
- 移行計画と決定 D1–D7: `IMPROVEMENT_PROPOSAL.md` §9
- 承認撤去のルール単位の提案: `PHASE5B_RULE_PROPOSAL.md`
- バグ調査（§1–§41）: `BUG_REPORT.md`
- Agent 移行の進捗: `AGENT_PROGRESS.md`
- Dashboard 改修: `DASHBOARD_REFINED_PLAN.md`（D1–D9）、`DASHBOARD_V3_PLAN.md`（L1–L6）
- リスク台帳: `docs/risk-register.md`
