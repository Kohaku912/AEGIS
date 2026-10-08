# AEGIS 現状調査レポート — 構成・機能・未完部分・優先アクション

- 調査日: 2026-09-28
- 対象: `C:\Users\kohak\programs\AEGIS`（ai-server / pc-server / browser-server / room-server / android-server / web-ui / packages）
- 手法: コード・設定・計画文書の一次資料確認、テストスイートの実測実行、git 状態の実測
- 注: 本書は**読み取り専用の調査**であり、コードは一切変更していない

---

## 0. 結論（要約）

| 観点 | 現状 |
|---|---|
| テスト | **ai-server 2768 passed / 8 skipped / 0 failed**（実測 508.06 秒、2026-10-07 再実測 — ⚠️ **直前の記録 2259 は 2026-10-04 の値**で、それ以降の増分が**この写しに反映されていなかった**（実測との差 **+281**。正典は §1.1 の表）。**2026-10-04 再実測の内訳** — presentation-stream の修正で +2、memory 名簿の修正で +3、影の重複ルートの削除で **+0**（ピンは反転したが本数は **6 → 6** で総数は動かず）、Chroma の死んだ連鎖と `SemanticMemory` の同名衝突の記録で **+11 = 新ピンちょうど**、**§4 項目 8（負担量の指標）の配線で +18 = 新ピンちょうど**（`test_burden_metric_is_judged.py` +3 と `test_burden_check_is_asked_by_the_loop.py` +15 — うち **+2 は配線の硬化**: `_create_autonomous_loop` はスイートに一度も実行されないので、`set_burden_metric` を**実走させる**ピンと composition root の**位置引数ちょうど 1 つ**を形で固定するピン。配線そのものは 5 箇所 — `JUDGMENT_PROFILE` の改名・`side_effects` の型修正・ループの周期フック・`loop_state.json` の永続化・composition root。**そのうち 2 つは「配線したのに動かない」型だった**: 旧 profile `decision` は allowlist に拒否され Mock へ落ち、ask の `side_effects` は**能力自身の `input_schema`** に拒否される）、**Docker の静的整合の記録で +8 = 新ピンちょうど**（`test_compose_is_coherent.py` — `docker` を呼ばず CI で走る。実測 rc=0 / 本番 secret 無し rc=1、healthcheck は 3 実像すべてにあるのに compose は宣言せず何もゲートしていない）。**L1 ゲート失敗の記録が原因を捨てていたのを直して +9 = 新ピンちょうど**（`test_l1_gate_failures_carry_the_cause.py` — 706 行の失敗が `error="exception during L1 tool gate"` という**固定文字列**で原因を捨て、実例外は `logger.debug` にしか出ていなかった。4 つの `except Exception` が `型: メッセージ` を記録し、traceback は ERROR レコードへ。**変異 12/12**）、**L1 ゲートの黙った迂回を塞いで +5 = 新ピンちょうど**（`test_the_l1_gate_is_not_bypassed.py` — ゲートは `llm.generate(..., profile="l1_default")` を呼ぶが、**この `profile=` を受け取れるのは `LLMGateway.generate` だけ**（`MockLLMProvider` / `openai_provider` / `typesafe_provider` はいずれも取らない — シグネチャ 3 つを実測）。ゲートウェイ以外の `llm` を束ねると例外が**握り潰され**（呼び手は `None` を「判断なし」と読む）、**ゲートが一度も走らない**のにテストは緑のままだった。実測 2026-10-04: 直前の診断性の修正で原因が載るようになって**1 時間で 2 件**判明 — `MockLLMProvider.generate() got an unexpected keyword argument 'profile'` と `AttributeError: 'NativeToolLLM' object has no attribute 'generate'`。テストダブル `NativeToolLLM` を本番の形に合わせ、**呼び出し点を発見方式で走査**するピンを追加（`src/` と `tests/` の全 `call_llm_with_tools` / `_call_llm_with_runtime` を解決し、束ねた `llm` の `generate` がゲートの kwargs を満たすことを assert。**変異 9/9**）、**同じ `generate(..., profile=...)` の呼び出し形を `src/` 全体で掃討して +3 = 新ピンちょうど**（`test_the_l1_gate_is_not_bypassed.py` が 5 本 → **8 本**。`src/` の同形サイトは実測 **9 箇所**で、握り潰していたのはゲートだけ — 6 箇所は防御済み（`TypeError` で再試行、または原因を記録）、3 箇所は未防御だが安全（ゲートウェイ自身の 2 箇所は `profile` を取る、`social/manager.py::_generate_json` は本番がゲートウェイを束ねるので不一致は**大声で**落ちる）。ピンは 9 箇所を分類し、**新しい未防御サイトを丸ごと拒否**する — 次の不完全な束縛はここで落ち、`llm.first_stage.*.failed` の不透明な行を増やさない。**変異 15/15**、対照緑、6 ファイルをバイト単位で復元）、**読めない `executor.json` を黙って捨てていたのを名指しできるようにして +9 = 新ピンちょうど**（`test_executor_manifest_failures_are_named.py`。`ExecutorRegistry._load_one` は読めないマニフェストで `return` しており、結果は**クラッシュではなく不在** — 実行器が登録簿に無いので `execute` は `EXECUTOR_NOT_FOUND`（「No executor for …」）を返すが、呼び手は「そもそも書かれていない」と「書かれているが解析できない」を**区別できない**。姉妹ローダ `FolderCapabilityRegistry` は元から `_errors` / `errors()` / `reload()["errors"]` を持っていたので、実行器側を同じ水準に合わせ、`CapabilityCatalog.reload()` が**結果ごと捨てていた**のを `executor_errors` として転送（`errors` は能力マニフェストの意味のまま）。**変異 10/10**、対照緑、3 ファイルをバイト単位で復元）、**出荷されたマニフェストの木が内部で整合していることを固定して +5 = 新ピンちょうど**（`test_shipped_manifest_tree_is_coherent.py` — 他のどのテストも `apps/` をディスクから読まないので、① 解析できない `executor.json`（実行器が**不在**になり `EXECUTOR_NOT_FOUND` になるが、それは**内製ハンドラで処理される 105 の能力**にとっても正直な答えなので区別できない）② 能力が改名・削除された**孤児の `executor.json`**、のどちらも誰も見ていなかった。実測 2026-10-04: ディスク上 23 = 読込 23、読込エラー 0、孤児 0。数は**ファイルシステムから導出**するので、能力を足してもこのファイルは編集不要 — **整合性を壊したときだけ**落ちる。`runtime.py` が本当にその 2 つのディレクトリを束ねていることも `ast` で突き合わせる。**変異 6/6**、対照緑、変更ファイル 4 本をバイト単位で復元・作成ファイル 2 本を削除）、**壊れた社会データのストアを名指しできるようにして +10 = 新ピンちょうど**（`test_social_store_failures_are_reported.py` — `SocialIntelligenceSystem._load` は 6 つの JSONL を読むが、`_load_jsonl`（observations / episodes）は**元から警告していた**のに、4 つの専用ローダ（relationships / reputations / social_norms / social_skills）は `except Exception: pass` だった。結果はいつもの形: ストアは**空の dict** に落ち、他の唯一の信号は `_load` の集計行（件数を数える）だけ — **解析に失敗したストアと、まだ 1 件も無いストアが同じ行を出す**ので、壊れた `relationships.jsonl` は**新規インストールと見分けがつかない**。`_load_jsonl` と同じ警告に揃えた（挙動は不変 — 空へのフォールバックはそのまま）。`caplog` で**記録を捕まえる**ピン（テキストではなく挙動）で、4 ストアのパラメータ化 + **欠測時は黙る**（非空虚対照）+ **1 つ壊れても他は読める** + 既存ヘルパの警告。**変異 7/7**）。**壊れた `risk_overrides.json` を名指しできるようにして +8 = 新ピンちょうど**（`test_policy_override_load_failures_are_named.py` — `PolicyEngine._load_overrides` は `__init__` から呼ばれ、**生きたファイル**（`aegis_ai/policy_engine.py` は再輸出シムにすぎず、`runtime.py` は `from policy_engine import PolicyEngine` を束ねる）で 2 つの失敗を裸の `pass` で飲んでいた: 読めない/壊れたファイル（全上書きが消える）と未知の危険度名（その 1 つが消える）。結果はクラッシュではなく**静かな降格** — `DEFAULT_RISK_MAP` は `RiskLevel.FORBIDDEN` → `PolicyDecision.DENY` なので、能力を FORBIDDEN に引き上げた上書きは適用されなくなり、能力は（より寛容な）マニフェストの水準へ落ちる。「上書きファイルが無い」と「壊れている」が区別できなかった。**姉妹機構**（`CapabilityCatalog` の `OverrideStore`）は元から報告していた（`corrupted` / `override_store_corrupted`）ので、読み込み側が原因（パス + 例外型）と結果を名指しするようにした。**重症度は推論ではなく実測**: 3 つのハードストップはこのファイルに依存せず（`EXPLICIT_DENY_PATTERNS` が毎 `evaluate()` で走る）、`set_risk_override` には現在**本番の呼び手が無い**ので露出は**潜在** — また*フォールバック*の非対称（この読み込みは姉妹の fail-**closed** に対し fail-**open**）は**挙動**の問いなので、所有者向けに記録し変更しない。ピンの対照は**噛む**: 同じ能力が良いファイルで DENY、壊れたファイルで ALLOW。**変異 7/7**、対照緑、バイト単位で復元）。**捨てられた記憶の行を名指しできるようにして +13 = 新ピンちょうど**（`test_advanced_memory_load_failures_are_named.py` — `AdvancedMemory._load` は 3 つの JSONL ストアを読むが、解析できない行は裸の `except Exception: pass` で捨てられ、ストアは**短く**戻っていた。他の唯一の信号 `get_stats()` は**件数**を報告するので、解析に失敗したストアと一度も書かれていないストアが**同じ種類の答え（より小さい数）**を出す。非対称は**同じクラスの中**にあった — 同じクラスは LLM 抽出の失敗では既に警告している。3 つのループが捨てた数を数え、**ファイルごとに 1 回**警告する。⚠️ **測定が最初の前提を否定し、第 2 の層を見つけた**: 会話ストアは `_load` のループに到達せず、共有ヘルパ `aegis_ai.jsonl_tail.read_jsonl_tail` を通り、**そこで**不正な行が握り潰されていた（ピンはまさにそのケースで落ちた — 3 ストアすべてでパラメータ化していたから捕まえられた。私が推論した 2 つだけを覆うピンなら緑のまま 3 つ目が黙っていた）。ヘルパは行ごとの捨て数**と**、**DEBUG** で `return []` していた読み込み全体の失敗（「窓に記録が無い」と区別できない）を報告するようになった。**変異 8/8**、対照緑、**2 ファイル**をバイト単位で復元。欠測時は黙り、フォールバックは DEBUG のまま（どちらも非空虚対照として固定）。⚠️ **自作スキャナの偽陽性**も 1 件: `settings/store.py::import_json` は `return <empty>` として検出されたが、実際は `[f"Invalid settings JSON: {e}"]` を返す — **AST の形では空リテラルとエラーリテラルを区別できない**）。**通知設定 7 フィールドの唯一の読み手が死んだコードの中にあり、それでも検出器は「読まれている」と判定して +23 = 新ピンちょうど**（`test_notification_settings_are_read_only_by_dead_code.py` — 前サイクルの「族の中の非対称」を通知パッケージへ広げ、**測定で絞り込んだ**: *クラス*水準の事実は既に `feature-catalog.md` §8 に記録済み（`NotificationRouter`・6 チャネル・`OsNotificationProvider` が宣言のみ、§7 は `send()` がファンアウトしないと書く）なので、新しいのは**設定水準の帰結と検出器の沈黙**。`src/` の全モジュールを `ast` で走査すると**構築される通知クラスは `NotificationManager` ただ 1 つ**（`runtime.py:1071`、`event_manager=` のみ）。よって 7 フィールドの読み手は `NotificationPreferences._load_from_settings` と `QuietHoursManager._load_from_settings` の 2 つだけで、どちらのクラスも**誰も構築しない**。所有する router も未構築で、しかも `QuietHoursManager()` を**引数なしで**作るので**二重に死んでいる**（`if not self._settings: return`）。`test_ineffective_flags.py` の layer 1 は**フィールド名のテキスト一致**なので死んだコード内の参照も読み手と数え、**7 つのユーザー設定可能・出荷済み・文書化済みのフラグに対して検出器が緑**のままになる。**対照 2 つ**（「読まれない」は壊れた読み手でも真なので）: ① store を渡せば両クラスとも設定を尊重する ② 読み取りサイトの走査は非空虚で**スコープも帰属する**（生きた対照フィールドの `(module, class.method)` を名指し）。⚠️ **変異が 1 つ生き残り、それはピンではなくハーネスだった**: 対照②の初版は「死んだ集合の外に読み取りが 1 つでもある」だけを assert したので、生きた 2 つの読みの**片方**を `getattr(..., "external_llm_allowed")` に書き換える変異が緑のまま通った → 期待サイトを名指しする形に修正。読みは**最内の `class.method`** に帰属させる（ファイル水準の検査は、そのファイルが死んだクラスしか含まなくても等価ではない — `preferences.py` に生きたモジュール水準の読み手を足す変異 M10 は**スコープ水準の assert だけ**が捕まえる）。**変異 12/12**、対照緑、7 ファイルをバイト単位で復元。記録: `DELEGATION.md` §4 項目 35（router の配線は**挙動変更** — クワイエットアワーが実際に延期を始め、外部チャネルが送信を試み始める）、`feature-catalog.md` §9 に 4 行、`docs/notification-gateway.md` に日付付き警告ブロック（Quiet Hours / Preferences / Safety の各節が「動いている」と書いていた）。⚠️ **計測の罠**: 最初の全体実行が `2145 / 8` を報告し、2 つのマーカー実行が `314 / 1 / 1839` と `1832 / 7 / 315` を報告した — **1 本足りない**。原因は**全体実行が走っている最中にピンを書き換えた**ことで、その実行は 22 本版を収集していた。egress と非 egress は収集を**分割**するので `egress + 非 egress == 全体` が成り立たねばならない。成り立たないときは、スイートより先に**計測の入力**を疑う。`--collect-only` が裁定した（3 つとも 2154））。**操作タイムラインの 4 つの無言の読み込み失敗が名乗るようにして +13 = 新ピンちょうど**（`test_operation_timeline_failures_are_named.py` — `web/ui_overview._operations` は 3 つの源を併合し、それぞれが失敗時に**不在**を返していたので、壊れた読み込みと「まだ 1 件も無い」が区別できず、監査グループと自律ログへのフォールバックが**もっともらしい結果**を描き続けていた。4 箇所が原因と帰結を名乗る: store（`operation_store.list_recent`）・監査グループ（`audit_manager.list_groups`）・自律実行ログ、そして 1 層下の `OperationStore._load`（読めないファイルは空のキャッシュを残し、捨てた行は単に「無い」）。**正当な不在 2 つ**（ループ未設定・ログ未作成）は黙ったままで、ピンがそれを assert する（さもないと警告が雑音になる）。**推論ではなく実測**: `_autonomous_logs` は行ごとのガードを持たないので、**解析できない 1 行がサイクル履歴全体を捨てる** — `DELEGATION.md` §4 項目 36 として記録し、**直していない**（行を飛ばすとタイムラインの見え方が変わる＝挙動変更）。**変異 9/9**、対照緑、2 ファイルをバイト単位で復元。⚠️ **サイクル 10 の数の掃討で、強化が置き去りにした写しが 2 つ見つかった**: `DELEGATION.md` §4 項目 35 と `docs/notification-gateway.md` がどちらも通知ピンを **22 テスト / 変異 9** と言い続けていた（正は **23 / 12**）。**壊れた `settings.json` が egress 許可を全部「狭い既定」へ黙って戻していたのを名指しできるようにして +9 = 新ピンちょうど**（`test_settings_store_load_failures_are_named.py` — `SettingsStore._load` は `__init__` から 1 回走り、失敗時は**無言で**組み込み既定に差し替えていた。`runtime.py:898` は**出荷** `config/settings.json` を指すので、壊れた/綴りを誤ったファイルは**出荷設定が効いていない状態**を無音で作る。**メッセージを書く前に測った**: 既定と出荷設定の差は**ちょうど 3 鍵で全部 egress 許可**（`privacy.egress_allowed_hosts` は `[]` vs `['api.typesafe.ai']`、`external_egress_allowed` / `external_llm_allowed` は `False` vs `True`）なので、フォールバックは **fail-closed**（何も開かない＝単一制約は危険に晒されない）だが、ゲートが全ての外部宛先を拒否しクラウド LLM プロファイルが降格する。**工場を駆動して両方を確認**: 既定ではゲートが `egress deny … reason=external egress is disabled` を出し、出荷設定のプロファイルは**許可**されていて Mock に落ちるのはローカル Ollama が居ないからだけ。同じファイルの `import_json` は**鏡像の欠陥**を持っていた — **1 つの `try` が解析と適用の両方を包む**ので、**ディスク**の失敗が `Invalid settings JSON` と読める（固定メッセージ型の再発）→ 2 つに分けた。**変異 8/8**（うち 3 つは**対照の劣化**）、対照緑、2 ファイルをバイト単位で復元。⚠️ **第 2 の欠陥は測って記録し、直していない**: `update` は `_persist()` の**前**に `self._settings` を代入するので、永続化の失敗はメモリだけ変えてディスクを変えない（実測: 前 `False` → `PermissionError` → 後 `True`）。先に永続化すると値が動く時点が変わる＝**挙動変更**なので `DELEGATION.md` §4 項目 37、ピンは現状を固定する）。egress **314 passed / 1 skipped**（315 件がマーカー付き・**1861 deselected**、床 160）・room 16 / browser **100** / SDK **71** / vitest 144 / playwright 42。**P2-0 で 3 つの Python スイートが CI に入った**（`scripts/test-all-suites.ps1`）— それまで誰も走らせておらず、SDK の 6 件赤が誰にも見えなかった。**この数は A-12（−3）と B-1①（+1）で動いたのに、3 つの写し（本行・§1.1 の表・`AGENTS.md`）が追随していなかった** — §1.1 の脚注が警告している「片方だけが動く」型の再発。B-5② の実装時に 3 写しとも揃えた。**B-6 で 1891 → 1885 passed / 30 → 8 skipped に動いた**（内訳は §0.1 の B-6 行。**スキップの −22 は消したフィールドそのもので、通過の −6 は置換** — どちらも「負債が静かに消えた」のではない）。**B-5① で 1885 → 1889 passed に動いた**（**+4 = 新ピンそのもの**）、続いて **`autonomy` 残骸の削除と一般形のピンで 1889 → 1890**（**+1 = 新ピン**）。egress は不変 — 新 5 本はいずれもマーカーを持たない。**音声ゲートの「死んだ検査」の記録で 1890 → 1893 passed**（**+3 = 新ピン**、実測 342.68 秒）。**egress は動いた** — 303 → **306 マーカー / 302 → 305 passed / 1 skipped**、deselected 1595。`tests/test_voice_io.py` は**モジュール全体が egress マーカー**なので、新 3 本もそこに載る（他の 5 本は非 egress のファイルだった）。**承認の監査 API の記録で 1893 → 1895 passed**（**+2 = 新ピン**、実測 332.29 秒）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1595 → 1597 — 新 2 本は非 egress のファイル）。**`aegis_ai/security/` パッケージ全体が未配線であることを記録して 1895 → 1900 passed**（**+5 = 新ピン**、実測 362.80 秒）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1597 → 1602）。**`aliases` の「読者はいるが生産者はいない」を記録して 1900 → 1902 passed**（**+2 = 新ピン**、実測 410.51 秒）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1602 → **1604** — 新 2 本は非 egress）。**`executor.json` の機械固有の絶対パスを可搬な綴りに直して 1902 → 1905 passed**（**+3 = 新ピン**、実測 392.57 秒）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1604 → **1607** — 新 3 本は非 egress）。**Docker 面の検証で 1905 → 1907 passed**（**+2 = 新ピン**、実測 414.60 秒、collected 1913 → 1915）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1607 → **1609** — 新 2 本は非 egress）。**視覚の誤った主張を訂正し Room fixture を応答に明示して 1907 → 1911 passed**（**+4 = 新ピン**、実測 392.15 秒、collected 1915 → **1919**）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1609 → **1613** — 新 4 本は非 egress）。**同日 13 度目に、12 度目の掃討の被覆そのものが誤りと判明した** — 走査語を「vision」に限ったため生きた写しは 3 つではなく **6 つ**（テスト数は動かず、記録の訂正のみ）。**`mypy>=1.8` が宣言だけで一度も走っていないことを記録して 1911 → 1914 passed**（**+3 = 新ピン**、実測 408.75 秒、collected 1919 → **1922**）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1613 → **1616** — 新 3 本は非 egress）。**proto 生成の「検証」段が何も検証していないことを記録して 1914 → 1919 passed**（**+5 = 新ピン**、実測 401.44 秒、collected 1922 → **1927**）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1616 → **1621** — 新 5 本は非 egress）。**§3.1 穴 3 の前提（「既存の決定ログから導出できる」）を測って 1919 → 1923 passed**（**+4 = 新ピン**、実測 414.56 秒、collected 1927 → **1931**）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1621 → **1625** — 新 4 本は非 egress）。**前提は 3 つの副指標のうち 1 つでしか成り立たない** — ① 1 日あたりの回数は可 ② 応答割合は**不可**（メモリ内 dict・監査書き込みゼロ・`dismiss` がユーザーとシステムを区別できない）③ コスト中央値は **5 経路中 1 つだけ**。**ドラフトをそのまま実行していれば、計算できない指標を計算できると主張していた**。**`PresentationManager.dismiss` の優先名がテストダブルにしか定義されていないことを記録して 1923 → 1926 passed**（**+3 = 新ピン**、実測 415.77 秒、collected 1931 → **1934**）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1625 → **1628** — 新 3 本は非 egress）。**危険度は推論ではなく実測** — フォールバックを削除すると**スイートが緑のまま**で、生産は黙って通知の dismiss をやめる。**その後 2026-10-02〜03 に 1926 → 1960 passed へ +34**（すべて帰属: +16 = S-1① / M-2 / S-2 と**未帰属 +4**、+9 = E-3 / E-2 / S-4、+3 = `f8e0b06` — 旧制約を符号化していた **21 ピンを書き換え**、新しいゲートテスト 2 本を追加、+6 = `31e4066` — JEV の**実行時文字列**に残っていた再スコープ前の主張の掃討と §5.2〜§5.5 の修正）。**egress は 306 → 315 マーカー / 314 passed / 1 skipped**、deselected 1628 → **1653**（egress マーカーが増えたのは `f8e0b06` の 2 本だけで、以降の 6 本は非 egress）。**イベント駆動の中核が未構築であることを記録して 1978 → 1984 passed**（**+6 = 新ピン**、実測 439.95 秒。canonical は 1984 / 4 skipped / 4 deselected、collected 1992）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、deselected 1671 → **1677** — 新 6 本は非 egress）。**`data/audit.jsonl` に書き手が無いことを記録して 1984 → 1992 passed**（**+8 = 新ピン**、実測 427.30 秒。canonical は 1992 / 4 skipped / 4 deselected、collected 2000）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、deselected 1677 → **1685** — 新 8 本は非 egress）。これに伴い `AGENTS.md` の**派生値**「追加分」も **30 → 38**（`2000 − 1962` collected、`1685 − 1647` deselected）。**この掃討で `AGENTS.md` の「追加分 18 本」が**派生値の取り残し**と判明**（18 は総数 1972 のときだけ真で、1977 / 1978 への更新が passed / deselected だけを動かし、この計算値を置き去りにしていた — 型 9 の一段内側）。**30** に訂正し、算術を本文に書き残した。**`/api/presentations/stream` の購読者漏れを記録して 1992 → 1997 passed**（**+5 = 新ピン**、実測 499.73 秒。canonical は 1997 / 4 skipped / 4 deselected、collected 2005）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、deselected 1685 → **1690** — 新 5 本は非 egress）。**派生値**「追加分」は **38 → 43**（`2005 − 1962` collected、`1690 − 1647` deselected）。**`GET /api/memory/stats` の応答が不完全であることを記録して 1997 → 2011 passed**（**+14 = 新ピンの 14 ケースちょうど**（7 関数 + 7 パラメータ化）、実測 538.07 秒。canonical は 2011 / 4 skipped / 4 deselected、collected 2019）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、deselected 1690 → **1704** — 新 14 本は非 egress）。**派生値**「追加分」は **43 → 57**（`2019 − 1962` collected、`1704 − 1647` deselected）。**影の落ちた重複ルート 2 本を記録して 2011 → 2017 passed**（**+6 = 新ピンの 6 関数ちょうど**、実測 488.49 秒。canonical は 2017 / 4 skipped / 4 deselected、collected 2025）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、deselected 1704 → **1710** — 新 6 本は非 egress）。**派生値**「追加分」は **57 → 63**（`2025 − 1962` collected、`1710 − 1647` deselected）。**`mind/` の 8 つの無言の読み込みを名指しできるようにして +34 = 新ピンの 34 ケースちょうど**（`test_mind_persistence_failures_are_named.py` — `aegis_ai/mind/` の 8 モジュールが**同一の** `_load` を持ち、`except (json.JSONDecodeError, OSError): pass` で壊れたファイルを「まだ 1 件も無い」と区別できなくしていた。8 つともパス・例外型・帰結を名乗る（この族には**ロガーが 1 つも無かった**）。⚠️ **境界も測って固定した** — 一族の「無言」は**例外型**で決まっており、ファイルが使えるかどうかではない: 妥当な JSON だが**非オブジェクト**の行（`123`）は 8 つすべてで `AttributeError` を投げて `__init__` から出る。しかも生きている 2 つの構築点は**どちらも try の外**（`runtime.py:995`・`runtime.py:1669`）で、3 つ目は同じ呼び出しを **DEBUG で握り潰す**（`llm/memory_context.py:323`）→ §4 項目 38。⚠️ **族の範囲も測って固定した**（`import` ではなく構築）: `mind/` の外で構築されるのは `Identity` **だけ**（`AffectSystem` 経由で `Mood`・`Personality`・`LayeredEmotion` が生きる）で、`Desire`・`Emotion`・`GoalManager`・`SocialIntelligence` は**どこでも構築されない**（`Emotion`・`GoalManager` を import する `reflection_loop.py` 自身が構築されない＝2 次の死）。うち 2 つは生きたクラスと同名で、`mind/social_intelligence.py` は**キーワード一致**を実装している（AGENTS.md の中核規則に反するが未配線なので不活性）→ §4 項目 39。**`docs/mind-layer.md` の「ContextBuilder Integration」が実行不能と判明して訂正**（`affect_system=` / `social_intelligence=` は `ContextBuilder.__init__` が取らず `ctx.affect` / `ctx.social` も無い。本番の呼び出しは `src/` に 1 つだけで、渡すのは `identity` のみ）。**変異 8/8**（うち **3 つは対照の劣化** = M4 正当な不在に警告・M5 読めるファイルに警告・M8 `AffectSystem` の連結を切る）、対照緑、2 ファイルをバイト単位で復元、`leftovers=[]`。**egress は不変**（315 マーカー / 314 passed / 1 skipped、deselected 1861 → **1895** — 新 34 本は非 egress）。**派生値**「追加分」は **214 → 248**（`2210 − 1962` collected、`1895 − 1647` deselected）。**3 つの実行は厳密に整合**: `1888 + 314 = 2202`、`7 + 1 = 8`、`315 + 1895 = 2210`。⚠️ **本行の物語は途中で「走行合計」を書くのをやめている**（実測 2026-10-04）: `X → Y passed` の形の段は **`2011 → 2017`** の後 **`2202 → 2209`**（サイクル 14）へ飛び、**`2017 → 2202` の区間はどの節も埋めていない**（現在の数は **2209**、飛びは **185**）。節が名乗る `+N` は**時系列順に並んでいない**（サイクル 14 を足した後の最後の 4 つは `+14`・`+6`・`+34`・`+7`）ので、節を足しても差を突き合わせられない。**走行合計の正典は §1.1 の表と下の日付付き注記**であり、本行は要約 — 同じ行の中の 2 つの主張を突き合わせる一般形は未着手（サイクル 13 の候補 ③）。**`AutonomousLoop` の 4 つの握り潰しを名指しできるようにして +7 = 新ピンちょうど**（`test_autonomous_loop_failures_are_named.py` — 4 箇所とも**失敗**を**不在／既定値**に変えており、どれも無言だったので**肯定的な事実と区別できなかった**: `_priority_obligations` → `[]`（「未解決の務めは無い」）／`_current_interruption_cost` → `0.15`（**「AgentState 未接続」の既定値と同じ数**なので、「読めなかった」と「繋がっていない」が 1 つの値だった）／`_manifest_for` → `None`（`_is_inventory_capability` が `False` と読む）／`_load_recent_history` → `[]` — 呼び手が**リテラル文字列** `"Autonomous execution history: no actions executed yet. First run."` として**計画 LLM の文脈に注入**し、加えて `_burden_activity` が期間を空として報告し `_recent_capability_ids` が直近能力なしと報告する。**戻り値は不変** — ピンは既存の挙動を固定するので動かせない。兄弟 2 つは**意図的に無言**としてピンに許可リストした（`_call_propose_candidates_llm` は壊れた LLM JSON を理由ごと `no_action_reason` に載せるので無言ではなく、`_sanitize_for_execution_log` はデータ読みではなくマスク層）。**変異 7/7** ＋ **変異なし対照**、原ファイルをバイト単位で復元。⚠️ **対照が私の非現実的なダブルを捕まえた**: `_capability_catalog()` は `self._broker` を `getattr` 既定なしで読むので、`object.__new__` の裸の実体は `None` ではなく `AttributeError` を投げた — **本番は常にその属性を持つ**。⚠️ **帰結は記録のみ**: `_build_action_history_summary` は今も読込失敗で「no actions executed yet. First run.」と言い切る — 文字列を変えるのは計画器への入力の変更なので `DELEGATION.md` §4 項目 40）。**`CuriosityExploration` の 15 の無言の失敗を名指しできるようにして +18 = 新ピンちょうど**（`test_curiosity_exploration_failures_are_named.py` — 7 つの候補源＋好奇心更新＋文脈構築 3＋保存 4 の 15 箇所がすべて無言だったので、**読めない源は空の源と同じ数の候補（ゼロ）**を出し、壊れたストアと「好奇心の対象が無い系」が区別できなかった。同じクラスは **LLM の失敗だけは既に名指ししていた**（`_candidates_from_llm`）ので、**源の失敗だけが無言**という非対称が測れた。**戻り値は不変**。**変異 19/19** ＋ 変異なし対照、原ファイルをバイト単位で復元。⚠️ **ピンが私のメッセージ本文の欠陷を捕まえた**: 隣接文字列リテラルは区切り無しで連結されるので `"no record"` + `"on disk"` が **"no recordon disk"** と描画された — **描画後のテキスト**に assert していたから見つかった）。**`SpontaneousObservation` の 9 の無言の失敗を名指しできるようにして +12 = 新ピンちょうど**（`test_spontaneous_observation_failures_are_named.py` — 7 つの観測源＋ログ書き込みの 9 箇所が無言で、**読めない源は静かな源と同じ数（ゼロ）**の観測を出していた。帰結はログ行より重い: `_pending_actionable_observations` に載らず `autonomous_loop.py:1074` の `should_run_l2` が偽になり、**読めなかった本物の信号（ディスク満杯・固まったタスク・劣化サーバ）が一度も表に出ない**まま「平穏」として扱われる（失敗は保留リストを**消さない** — 信号が**入らない**だけ）。**戻り値は不変**。**変異 11/11** ＋ 変異なし対照、原ファイルをバイト単位で復元。⚠️ **単位は選択**: 同モジュールの 3 つは既に `logger.debug(..., exc_info=True)` で記録しているが、**全 entrypoint が `logging.INFO`**（実測）なので**出荷既定では見えない** — これは**可視性**の問題で**無言**ではないので、サイクル 16 は「どの水準でも記録が無い」9 つを直し、3 つは §4 項目 42 として別に記録した。⚠️ **私の検証器がコードより先に間違えた**: 最初の編集後チェックは**ソース文字列**を検索して 5 つを「欠落」と報告したが、句は隣接リテラルに跨っており実行時にしか連結されない — **描画後の**書式文字列を `ast` で見ると 9/9 が在り `%s` の数 == 引数の数だった、**`ContextBuilder` の 4 つの到達可能な握り潰しを名指しできるようにして +7 = 新ピンちょうど**（`test_context_builder_failures_are_named.py` — `context_builder.py` は **14 個の `except`** を持ちながら**ロガーが 1 つも無かった**。**書く前に到達性を測った**ので主張が変わった: composition root `runtime.py:997` は受け取れる **~20 の backend のうち 7 つ**しか渡さないので、14 のうち **8 つは未配線の backend の上**にあり（`_create_default_multimodal_llm` は `multimodal_llm` が渡されるので呼ばれず、`elif self._tool_broker` の枝は直前の `if self._capability_retriever` が勝つので到達不能、`_situation_model`・`_user_state_manager`・`_delegation_policy`・`_commitment_manager`・`_user_understanding_service`・`_agent_state` は未配線）、**2 つは意図的なフォールバック**（`_user_model_store` は `to_context_string()` に、`_media_fingerprint` は `str(metadata)` に落ちる — どちらも**値を作る**）。到達不能な 8 つに記録を足すのは**動かないコードに記録を足すこと**で、2 つを「握り潰し」と呼ぶのは**処理済みの失敗を誤記すること**なので、残る **4 つ**（`recent_events`・`available_capability_ids`・media payload・media summary）を名指しした。帰結は実測: `ctx.recent_events` と `ctx.recent_media_summaries` は**解釈器の文脈に描画される**（`llm_task_interpreter.py:367-370`）ので、読めないイベントバスは**静かなシステム**として LLM に渡っていた。`ctx.available_capability_ids` は**トークン会計**（`:750`/`:787`）にしか読まれないので、帰結は**予算の誤り**であって「能力が見えない」ではない。`ctx.dialogue_policy` は同モジュール内でしか読まれず**どこにも描画されない**。**戻り値は不変**。**変異 7/7**（4 サイト + 追加方向 + 句の改名）＋変異なし対照、原ファイルをバイト単位で復元。⚠️ **ピンは修正ではなく到達性を固定する**: `runtime.py` を解析して `ContextBuilder(...)` のキーワード集合が**7 つの配線済み backend と等しい**ことを assert するので、backend を**配線すれば赤くなってここへ戻る**（§4 項目 43）。⚠️ **私の変異ハーネスがピンより先に間違えた**: 最初の「句の改名」変異は**空振り**だった — 句が隣接リテラルに跨るので `replace` が 0 件で、ピンが**誤った理由で緑**になった。原と同一の変異は「ピンが空虚」と読めるので、ハーネスは**変異が原と異なることを assert** し、句を**ソースではなく描画後のテキスト**（`ast`）で見るようにした、**`ui_overview.py` の 8 つの「不在」型の握り潰しを名指しできるようにして +13 = 新ピンちょうど**（`test_ui_overview_failures_are_named.py` — 同モジュールは **26 個の `except`** を持ち、サイクル 11 が 4 つ（`_operations` ×2・`_autonomous_logs`・`_pending_approvals`）を名指し済みだった。残る **22** は一様ではなく、**測って 3 つに割れた**: **8 つは意図的な変換/シグネチャ再試行**（`_number`・`_as_wire_text`・`_json_preview`・`_call_with_limit`・`_humanize_event_message`・`_causal_chain_from_operation` の `ImportError` と、狭い署名で呼び直す `except TypeError` 2 つ）で、名指しすれば**処理済みの変換を誤記する**。**5 つは既に例外を戻り値に載せている**（`_section`・`_agent_state`・`_user_understanding`・`_initiative`・`_behavioral_reports` は `{"summary": f"... unavailable: {exc}"}` 等を返すので**失敗は見えている**）。**1 つはコメントで意図的と明記されたフォールバック**（`_errors` のマージ）。残る **8 つ**が「読めなかった → 黙って空」型で、これを名指しした。到達性は先に実測（5 関数すべて live — `_mind_summary`/`_usage`/`_errors` は `:38`/`:69`/`:70` でセクション登録、`_server_list` は `:725`/`:769`/`:848`/`:1651`、`_recent_ui_events` は `:905`/`:939`/`:964`）。最も重い帰結は `_usage`: 読みが失敗すると `data` が空のまま `if not data:` に落ち、**「LLM usage is available from the LLM Usage service.」という偽の文言**が表示される（失敗がサービスの可用性として報告される）。**戻り値は不変**。**変異 12/12**（8 サイトの個別無力化 + 全無力化 + 追加方向 + 句の改名）＋変異なし対照、原ファイルをバイト単位で復元。⚠️ **ピン自身が実バグを炙り出した**: `_server_list` は `_runtime_server_status` 経由で `runtime.status_manager` を **getattr 既定値なしで**読むので、最小 runtime では `AttributeError` が**伝播する**（`_errors` 側は同じ呼び出しを握り潰すので非対称）→ §4 項目 44 として記録）） |
| 唯一の制約（Egress Gate） | **構造的に強制済み（L3）**。**2026-09-30 に再定義** — 禁止されるのは「**許可の無い**ユーザー情報の外部送信」で、**接続自体は可**（旧: deny-all）。**許可の 2 経路を実装済み**（常設設定 / ユーザーが特定の宛先に与えた許可）— ただし **②は未配線**（`src/` に構築点ゼロ。§3.2 の「記録された許可」行と `DELEGATION.md` §4 項目 22）。起動時アサーション・CI 床 160・mutation 証明は維持 |
| 北極星（先回り・委譲・成長） | **L2**。割り込み制御は**実装済みだが人間から見えなかった**（P1-1 で是正、§5 参照）。**Horvitz 型の期待効用モデルは P1-6 で実装済み**（`InterruptionController.decide` が `net = benefit × P(receptive) − cost`、判断ログに内訳を載せ再計算可能）。**本項は 2026-09-29 まで「残る空白」と誤記していた** — 同じファイルの §5 P1-6 行が ✅ 完了と書いており、自己矛盾していた。残るのは P1-5 の個別メンバー判定と長期項目（P2-5） |
| 最大のリスク | ~~18 日分の作業が未コミット~~ → **解消**。**2026-09-29、この「最大のリスク」が実際に顕在化した** — ローカルの **git オブジェクトストアが全消失**し（`count: 0 / in-pack: 0 / packs: 0`、`.idx` だけが残り `.pack` が無い）、未 push だった約 105 コミットが**履歴として失われた**（**内容は作業ツリーに残存**。§0.1 の `ebe1506` 行と `INCIDENT_2026-09-29_git-object-loss.md`）。復旧済み・作業ツリーは無傷。**原因は未確定**だが、引き金は**入れ子ブランチ名での ref 消失（B-6）が HEAD を unborn にしたこと**と相関しており、**A-5 でブランチをフラット名に改名したのでその引き金は消えた**（フラット名での 2 回のコミットはいずれも ref が正しく書かれた）。**残るリスクだった「未 push のままであること」は 2026-09-30 に解消** — A-7 を実行し、リモートに全コミットが届いた（§1.4）。~~期待効用モデルの不在~~ は P1-6 で解消済み（本項は 2026-09-29 まで残っていた誤記） |
| 既知の実バグ | ~~SDK の 6 テスト失敗~~ / ~~`pc-server.file.read` のパス検査欠如~~ → **いずれも修正済み**（P1-4）。ただし P1-5 後半の実測で **B-12〜B-15 を新規に記録**（§4.1）— 単一制約への実害は無い（egress は別経路で強制）が、**SDK は「第三者サーバを建てる道具」として機能していない**（B-14） |
| 文書 | `docs/status.md` 系 4 本は 6 月時点で停止し、**削除済みモジュールを「Done」と記載** → ✅ **P2-1 で 1 本に統合済み**（新 `docs/status.md` は測定値を一切持たない）。`AGENTS.md` の数値は本日**再実測して**修正（1597→1653→1662→1667→**1678**、browser 62→100、egress 164→211）— 前回「実測に合わせて修正済み」と書いた後も **3 箇所が古いままだった**（P1-7 で browser が 67→100 になったのに追随していなかった）。さらに **`docs/architecture.md` が 1 ファイル内で自己矛盾**していた（冒頭 53/157 ↔ 末尾 128/1550）ので実測値に統一（`7f0318a`、§4.2・§4.3 クラス 9） |
> **2026-10-06 再実測（テスト数の写しが乖離していた）**: 実測 **2540 passed / 8 skipped / 0 failed**（2548 collected、529.03 秒）。マーカー別は egress **314 / 1 / 315 marked**・非 egress **2226 / 7 / 315 deselected** で、**3 つの選択が厳密に整合**する（`2226 + 314 = 2540`、`7 + 1 = 8`、`315 + 2233 = 2548 = 2540 + 8`）。
>
> ⚠️ **同じコミットで動くべき 4 つの写しが、3 つの異なる値を持っていた**: 本行と §1.1 の表は **2259**（2026-10-04）、`AGENTS.md` の再実測列は **2287**（2026-10-05）、検証スキル §1 は **2259**（サイクル 18）— 実測は **2540**。つまり乖離は「誰も更新していない」ではなく「**写しごとに止まった日が違う**」形だった（`AGENTS.md` だけが 2026-10-05 まで動き、他は 2026-10-04 で止まっていた）。**数を動かす変更は 4 つの写しを同じコミットで直す**という本節の規則が、規則自身が警告した型で再発した（`DELEGATION.md` §4 項目 69 として記録）。
> **2026-10-06 サイクル 64 で再び動いた**: 実測 **2544 passed / 8 skipped / 0 failed**（2552 collected、546.04 秒）。マーカー別は egress **314 / 1 / 2237 deselected**・非 egress **2230 / 7 / 315 deselected** で、3 つの選択が厳密に整合する（`2230 + 314 = 2544`、`7 + 1 = 8`、`315 + 2237 = 2552 = 2544 + 8`）。**+4 = ピンそのもの**（`DELEGATION.md` §4 項目 48 の枝 ① の実行でピンを反転し 3 → **7 本**。新しい 4 本はマーカーを持たないので egress は 314 / 1 のまま）。⚠️ 4 つの写し（本節・§1.1・`AGENTS.md`・検証スキル §1）を**同じコミットで**動かした — サイクル 63 が記録した規則を、今度は最初から適用している。
> **2026-10-06 サイクル 65 でさらに動いた**: 実測 **2554 passed / 8 skipped / 0 failed**（2562 collected、524.86 秒）。マーカー別は egress **314 / 1 / 2247 deselected**・非 egress **2240 / 7 / 315 deselected** で、3 つの選択が厳密に整合する（`2240 + 314 = 2554`、`7 + 1 = 8`、`315 + 2247 = 2562 = 2554 + 8`）。**+10 = 新ピンちょうど**（`DELEGATION.md` §4 項目 46 の枝 ① の実行 — 本番モードで鍵の無い L1 の起動を拒否する。`tests/test_l1_requires_its_key_in_production.py`）。新しい 10 本はマーカーを持たないので egress は 314 / 1 のまま。
> **2026-10-06 サイクル 66 で再び動いた**: 実測 **2555 passed / 8 skipped / 0 failed**（2563 collected、569.3 秒）。マーカー別は egress **314 / 1 / 2248 deselected**・非 egress **2241 / 7 / 315 deselected** で、3 つの選択が厳密に整合する（`2241 + 314 = 2555`・`7 + 1 = 8`・`315 + 2248 = 2563 = 2555 + 8`）。⚠️ **この値は 2 回目の実測** — 1 回目は 2551 / 10 / 0 と **2 件の ERROR** を報告したが、原因はコードではなく**計測用ハーネスが `os.environ` を継承せず最小の env を渡していたこと**（実測: 同じコマンドを継承 env で再実行すると 0 error・不要な `%SystemDrive%` の木も作られない）。**ハーネスは測定の一部**。
> **2026-10-06 サイクル 67 で動いた**: 実測 **2558 passed / 8 skipped / 0 failed**（2566 collected、560.15 秒）。マーカー別は egress **314 / 1 / 2251 deselected**・非 egress **2244 / 7 / 315 deselected** で、3 つの選択が厳密に整合する（`2244 + 314 = 2558`・`7 + 1 = 8`・`315 + 2251 = 2566 = 2558 + 8`）。**+3 = 新ピンちょうど**（`tests/test_doc_citations_resolve.py` — `AGENTS.md` と `DELEGATION.md` の**記号アンカー引用 28 件（和集合）** を解決する。`src/` は不変なので egress は 314 / 1 のまま）。⚠️ **このピンは最初に自分の「記録」で落ちた** — 耐久形をプレースホルダで書いたため引用として読まれ、**4 箇所**に在ったものが **1 件**として報告された（**集合型のピンの失敗数は計数ではない**）。直したのは「本物の例を書く」ことで、ガードは緩めていない。4 つの写し（本節・§1.1・`AGENTS.md`・検証スキル §1）は同じコミットで動かした。
> **2026-10-06 サイクル 69 で再び動いた**: 実測 **2560 passed / 8 skipped / 0 failed**（2568 collected、578.65 秒）。マーカー別は egress **314 / 1 / 2253 deselected**・非 egress **2246 / 7 / 315 deselected** で、3 つの選択が厳密に整合する（`2246 + 314 = 2560`・`7 + 1 = 8`・`315 + 2253 = 2568 = 2560 + 8`）。**+2 = ピンそのもの**（`tests/test_event_driven_core_is_constructed.py` が 10 → **12 本** — イベント駆動の中核のうち `Scheduler`（`runtime.scheduler`）と `EventView`（`runtime.event_view`）は構築されるが `src/` に読み手が **0**。`TriggerEngine` だけが `getattr(runtime, "trigger_engine", None)`（`runtime.py:1916`）で消費される）。新しい 2 本はマーカーを持たないので egress は 314 / 1 のまま。4 つの写し（本節・§1.1・`AGENTS.md`・検証スキル §1）を同じコミットで動かした。
> **2026-10-06 サイクル 70 でさらに動いた**: 実測 **2562 passed / 8 skipped / 0 failed**（2570 collected、580.03 秒）。マーカー別は egress **314 / 1 / 2255 deselected**・非 egress **2248 / 7 / 315 deselected** で、3 つの選択が厳密に整合する（`2248 + 314 = 2562`・`7 + 1 = 8`・`315 + 2255 = 2570 = 2562 + 8`）。**+2 = ピンそのもの**（`tests/test_event_driven_core_is_constructed.py` が 12 → **14 本** — `Scheduler` の「消費者」を精密化: 消費者は `ContextBuilder` に**書かれている**が `scheduler=` が一度も渡されず（`src/` に **0** 件）、`Scheduler` は `create_default_tasks()` が呼ばれず**空**。配線しても `[]` を返す**二重死**）。新しい 2 本はマーカーを持たないので egress は 314 / 1 のまま。4 つの写しを同じコミットで動かした。
> **2026-10-06 サイクル 71 でさらに動いた**: 実測 **2565 passed / 8 skipped / 0 failed**（2573 collected、574.38 秒）。マーカー別は egress **314 / 1 / 2258 deselected**・非 egress **2251 / 7 / 315 deselected** で、3 つの選択が厳密に整合する（`2251 + 314 = 2565`・`7 + 1 = 8`・`315 + 2258 = 2573 = 2565 + 8`）。**+3 = 新ピンちょうど**（`tests/test_tool_broker_events_are_silently_disabled.py` — `ToolBroker` の `event_manager` が未配線で、`_publish_tool_event` と `_observe_recent_event` の `None` 分岐が**無言**。原因は順序: ブローカーは `runtime.py:1110`、`EventManager` は `:1221`）。新しい 3 本はマーカーを持たないので egress は 314 / 1 のまま。4 つの写しを同じコミットで動かした。
> **2026-10-06 サイクル 72 でさらに動いた**: 実測 **2566 passed / 8 skipped / 0 failed**（2574 collected、534.90 秒）。マーカー別は egress **314 / 1 / 2259 deselected**・非 egress **2252 / 7 / 315 deselected** で、3 つの選択が厳密に整合する（`2252 + 314 = 2566`・`7 + 1 = 8`・`315 + 2259 = 2574 = 2566 + 8`）。**+1 = 新テストちょうど**（`tests/test_tool_broker_events_are_silently_disabled.py` に 4 本目を追加）。**§4 項目 74 の母集団を精密化** — サイクル 71 は「ルートは 7 kwarg を渡す」と記録し、11 引数のうち 7 つ、と読めた。実測では**欠落は 4**（`delegation_policy`・`repair_manager`・`event_manager`・`capability_health`）で、うち **3 つは構築後に配線される** — `set_delegation_policy`（`:1283`）・`set_repair_manager`（`:1516`）・`_capability_health =`（`:1229`）。**代入も setter も無いのは `event_manager` だけ**（`:1227` は `journal_projector` の属性）。よって欠陥は順序一般ではなく、**3 兄弟に与えられた事後経路がこの 1 つには無い**こと。変異 9/9（当初の 3 変異は**無効** — 生存した変異はピンではなく変異の証拠）。
> **2026-10-06 サイクル 77 でさらに動いた（出荷設定の変更）**: 実測 **2567 passed / 8 skipped / 0 failed**（482.34 秒）。**+1 = 新ピンちょうど**（`tests/test_egress_gate.py::test_every_layer_profile_is_reachable_under_the_shipped_allowlist` — egress マーカーを持つので egress は 314 → **315**）。**出荷 `config/settings.json` の allowlist が `["api.typesafe.ai"]` → `["api.typesafe.ai", "api.deepseek.com"]` に変わった** — オーナーが L2 を `deepseek-v4-flash` で動かすと指示したため。`l2_default` は元から DeepSeek を宣言していたが、ゲートが拒否して **Mock へ静かに降格**していた（宣言されているが効いていない）。実測: `gate(api.deepseek.com)=allow`、`l2_default` は `OpenAIProvider` に解決、**L2 の実呼び出しが `content='OK'` / `used=openai/deepseek-v4-flash`**。allowlist を名指ししていたピン 4 本を再裁定（`test_egress_gate.py` 3 本 ＋ `test_burden_metric_is_judged.py` の負の対照を `decision` → `vision_observation` へ）。**変異 2/2 捕捉**。
> **2026-10-06 サイクル 78 でさらに動いた**: 実測 **2569 passed / 8 skipped / 0 failed**（2577 collected、462.50 秒）。マーカー別は egress **317 / 1 / 2259 deselected**・非 egress **2252 / 7 / 318 deselected** で、**3 つの選択が厳密に整合**する（`2252 + 317 = 2569`、`7 + 1 = 8`、`318 + 2259 = 2577 = 2569 + 8`）。**+2 = 新ピンちょうど**（`tests/test_composition_root_resolves_llm_layers.py` — egress マーカーを持つので egress は 316 → **318** マーカー / 315 → **317** passed）。**動機**: `scripts/verify_llm_layers.py` は層の配線を測るが、**ゲートウェイを自分で組み立てる**ので `runtime._build_runtime` の中の食い違いは見えない。composition root の実 `get_runtime()` を起動し、**その**ゲートウェイに訊く: 実測 `gateway._settings_resolver is runtime.settings_resolver` → **True**、L1/L2/L3 はそれぞれ宣言ホスト用に組まれた provider に解決（`_base_url == settings.base_url`）。⚠️ **静かな半分は配線のほうだった**: `LLMGateway._resolve` は resolver を持たないと素の `LLMSettings()` を返すので、層は**既定で走り**エラーは出ない — ピンはゲートウェイ**自身**の解決が宣言設定と一致することまで assert する。対照は**名指しせず発見**する（ゲートが拒否する外部ホストを持つ全プロファイルを列挙し、そのホスト用の provider を作らないことを assert）ので、そのホストを後で許可しても対照は空虚にならない。⚠️ **変異 3/3 捕捉。ただし最初の M2 は「生存」ではなく「無効」だった** — `SettingsStore()` の既定パスは**相対** `config/settings.json` で、テストの cwd は `ai-server/` なので何も変わらなかった。存在しないファイルを指す store に差し替えて再実行（→ 組み込み既定 → ゲートが全外部宛先を拒否）。復元は `git checkout HEAD -- <path>` で行い、直後にクリーンであることを assert した。⚠️ **egress マーカー付きファイルを足すと古いピンが赤くなる**: `tests/test_egress_closure.py::test_the_mutation_roster_covers_every_marked_file` が変異検査の `EGRESS_TESTS` 名簿とマーカー集合の一致を assert するので、新モジュールを `scripts/verify_egress_tests_catch_regression.py` に追加した（名簿自身が文書化している危険を、名簿自身のガードが捕まえた）。

> **2026-10-06 サイクル 79 でさらに動いた（計測器そのものを直した）**: 実測 **2571 passed / 8 skipped / 0 failed**（2579 collected、461.31 秒）。マーカー別は egress **319 / 1 / 2259 deselected**・非 egress **2252 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2252 + 319 = 2571`、`7 + 1 = 8`、`320 + 2259 = 2579 = 2571 + 8`）。**+2 = 新ピンちょうど**（`tests/test_verify_llm_layers_contract.py` — egress マーカーを持つので egress は 318 → **320** マーカー / 317 → **319** passed）。⚠️ **欠陥は配線ではなく計測器のほうだった**: `scripts/verify_llm_layers.py --live` が L3 の `content=''` を隠して `OK ... answered live` と表示していた。実測: 空ボディは**断続的で `max_tokens` の効果ではない**（32/64/128/256 で 0/20 空）。ツールは 1 回だけ再試行し、それでも空なら **WARN** を出して exit 0 を保つ — provider には**到達しており**、それこそが配線の証明で、モデル側の不調で FAIL にすると「動作していない」という誤読を生む。ピンは実 `main()` を駆動し、二重化するのは provider 呼び出しだけ（ゲート・resolver・provider factory は本番のまま）。対照は 1 フィールドだけ変える（`success=False` / `provider_used="mock"`）と **exit 1 と FAIL 3 行**に反転することを assert する。**変異 3/3 捕捉＋意図的な生存 1 件** — M4（再試行の削除）は*生存するのが正しい*: ピンは判定にあり、問い合わせ回数にはない。⚠️ **名簿の数値も動いた**: 変異検査の非変異実行は **319 passed / 1 skipped**（名簿はマーカー集合とちょうど一致）、変異実行は **78 failed**（318 マーカー基準の 76 から増えた）。

> **2026-10-06 サイクル 80 でさらに動いた（監査そのものが空の母集団で合格を出していた）**: 実測 **2576 passed / 8 skipped / 0 failed**（2584 collected、461.06 秒）。マーカー別は egress **319 / 1 / 2264 deselected**・非 egress **2257 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2257 + 319 = 2576`、`7 + 1 = 8`、`320 + 2264 = 2584 = 2576 + 8`）。**+5 = 新ピンちょうど**（`tests/test_audits_refuse_to_pass_over_an_empty_population.py` — 非 egress なので egress の **passed / marked は 319 / 320 のまま動かない**。ただし **deselected は 2259 → 2264** — 非マーカーの総数なので新テストぶん増える）。⚠️ **母集団は発見方式なので空になりうる — そして空の母集団は「何も監査していない」のに、清潔な母集団と**同じ判定**を出していた**（修正前の実測）: 能力カバレッジ 128 マニフェスト → `fail`、0 → `rc=0 "pass"`；機密監査 1267 ファイル → `pass`、0 ファイル → `rc=0 "pass"`；モック棚卸 3901 ファイル → `fail`、0 → `rc=0`。**偽の合格の代償が最も大きいのは機密監査**で、その母集団は `git ls-files` から来る — tarball や非 git のチェックアウトでは得られない。各監査は**読んだ分母を印字**し、分母 0 を清潔とは呼ばない。`audit-v1-completion.py` はモック報告に分母を要求するので、ガードはファイルで止まらず**連鎖に伝播**する。**変異 5/5 捕捉＋意図的な生存 1 件**（`schema_version` の改名は生存する — ピンは判定と分母にあり、化粧的なメタデータにはない）。**対照はガードと同じくらい重要**（実在する最小のマニフェスト木は今も合格すること）。⚠️ **変異のうち 1 つは「変異」になる前から不正だった** — Python の dict に JSON の `true` を書いたため `NameError` で落ち、**誤った理由で「捕捉」と読めた**。

> **2026-10-06 サイクル 81 でさらに動いた（報告書を読めなかったことを「ブロッカー無し」と読んでいた）**: 実測 **2588 passed / 8 skipped / 0 failed**（2596 collected、498.24 秒）。マーカー別は egress **319 / 1 / 2276 deselected**・非 egress **2269 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2269 + 319 = 2588`、`7 + 1 = 8`、`320 + 2276 = 2596 = 2588 + 8`）。**+12 = 新ピンちょうど**（`tests/test_a_missing_blocker_report_is_not_a_clean_report.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2264 → 2276**）。⚠️ **欠陥は 3 つの読み手すべてに同じ形であった**: `data/reports/production_blockers.json` を読む 3 経路のうち、*解析できない* 報告書は `except`/`catch` がブロッカーを作るのに、*存在しない* 報告書は清潔な既定値（`{"blockers": []}` / 空配列 / 空リスト）を返していた。消費者はどれもブロッカーを数えるので、「対照が走っていない」と「何も塞がっていない」が同じ値になっていた — これには dashboard のルート `/api/production/readiness` も含まれる（既定パスが**相対**なので、モック監査を一度も走らせていないホストでは答えが「ブロッカー 0」だった）。修正前→後の実測: 不在 → `blockers=0`・標識なし → **`1` + `unreadable=True` + `cause="was not found"`**；正しい JSON だが非オブジェクト（`[1, 2, 3]`）は `isinstance(dict)` を素通りして清潔な既定値に落ちていた → **`1`**；解析不能 → 1（不変）。**読めた報告書は逐語で通る**（実リポジトリの報告書は `blockers=2` / `status=fail`）。読み手の無かった `corrupted` は `unreadable` + `cause` に畳んだ。**変異 8/8 捕捉＋意図的な生存 1 件**（M8 = `.ps1` の不在枝を戻す — CI に PowerShell が無く pytest がこのファイルを読まないので**構造的に生存**する。これが記録すべき被覆の穴）。ハーネスは各変異を先に `py_compile` するので、不正な変異が「捕捉」と誤読されない。⚠️ **計測の罠**: 非 egress の 1 回目が `audit_log.py::_insert_record`（SQLite）の **Windows fatal exception: access violation** で落ちた — 変更したコードの外（egress ゲートの監査記録）で、全体実行は緑だったので**環境の揺らぎ**と判定し、再実測して数を採った。
> **2026-10-06 サイクル 82 でさらに動いた（ゲートの判定が「何を飛ばしたか」を言っていなかった）**: 実測 **2597 passed / 8 skipped / 0 failed**（2605 collected、558.32 秒）。マーカー別は egress **319 / 1 / 2285 deselected**・非 egress **2278 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2278 + 319 = 2597`、`7 + 1 = 8`、`320 + 2285 = 2605 = 2597 + 8`）。**+9 = 新ピンちょうど**（`tests/test_the_verdict_carries_its_denominator.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2276 → 2285**）。⚠️ **欠陥は判定の行そのものにあった**: `scripts/test-ai-server.ps1` は 4 検査、`-SkipMutation` はそのうち 3 つ。`scripts/test-all-suites.ps1` は 4 検査、`-SkipAiServer` は 3 つ。どちらも**完全な実行と縮小した実行で同じ `ALL CHECKS PASSED` を印字**していたので、CI と実行記録が引用する最終行からは「変異検査を飛ばした実行」と「走らせた実行」が区別できなかった — そして変異検査は「egress スイートが*失敗するのを観測済み*」だと言う統制である。各ゲートは自分の名前を `$ran` / `$skipped` に追記し、その計数を宣言した `$checksTotal` と突き合わせ、`ALL <ran>/<total> CHECKS PASSED (skipped: ...)` を印字する。計数が壊れていれば（総数を上げずに検査を足した場合）作り話の分母を印字せず **exit 1**。`scripts/test-beta-real.ps1` は同じ族を 1 層下に持っていた — ブラウザ検査は応答が無いとき passed でも failed でも skipped でもなく、`Results: 6 passed, 0 failed` が**7 つ試みた実行**を記述していた。いまはブラウザを skipped として数え、判定も分母を運ぶ（**exit code は不変** — ブラウザは意図的に best-effort）。**変異 5/5 捕捉＋対照緑**（どちらの素の判定を戻す／どちらのゲートでも飛ばした名前を落とす／beta のブラウザ経路を数えなくする／`$checksTotal` を消す — すべて赤。コメントだけの編集は緑）、全ファイルをバイト単位で復元。⚠️ **挙動の証明は「再生」**（各ゲートの判定末尾を抜き出し 4 つの形 — 完全／縮小／1 失敗／計数破壊 — で走らせて 4 つの異なる行を得た）。CI に PowerShell が無いので、pytest のピンは**静的**である（分母が判定に出ること・判定が飛ばした集合に依存すること・素の形が戻らないこと）。⚠️ **ピンの初版は性質ではなく一方のスクリプトの文法を固定していた** — 判定行そのものに `(skipped: $($... -join` を要求したが、それは `test-ai-server.ps1` の書き方で、`test-all-suites.ps1` は `$reduction` を先に組む — **正しいコードで赤くなった**。⚠️ **そして最初の判定は自己矛盾していた**: 分子が `$ran.Count + $skipped.Count` だったので、縮小実行が `ALL 4/4 CHECKS PASSED (skipped: mutation check)`（「4 合格」の隣に「1 飛ばし」）を印字した。分子は**走った**検査である。⚠️ **残る 3 つの `ALL CHECKS PASSED` は歴史であって生きていない** — `IMPROVEMENT_PROPOSAL.md`（日付付き Phase-3 記録）・`DELEGATION.md` §5（`ea01d80` での実行）・`build/ci-ai-server.log`（取得した出力）。いずれも書いた時点で正しかったので残す。⚠️ **掃討中に見つけた腐った表**: `docs/testing-real-devices.md` は `egress` マーカーが **233 tests**、スイートが **1807 tests** と書いていた — 実測 2026-10-06: **320** と **2605**（`-m pc_local` は何も集めず **2605 deselected**）。その場で訂正した。

> **2026-10-07 サイクル 83 でさらに動いた（死んだコード監査だけが会計の外にいた）**: 実測 **2608 passed / 8 skipped / 0 failed**（2616 collected、457.44 秒）。マーカー別は egress **319 / 1 / 2296 deselected**・非 egress **2289 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2289 + 319 = 2608`、`7 + 1 = 8`、`320 + 2296 = 2616 = 2608 + 8`）。**+11 = 新ピンちょうど**（`tests/test_the_dead_code_audit_is_inside_the_accounting.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2285 → 2296**）。⚠️ **3 つの結合した欠陥を実測**: ①`scripts/audit-dead-code.py` は `scripts/audit-*.py` で**唯一失敗できない**監査だった（`return 0` で終わり、6 つの兄弟は `return 0 if status == "pass" else 1`）うえ、歩いていない木の上で `dead_or_obsolete=0` を印字していた — サイクル 80 が 3 つの兄弟で塞いだ空母集団の族の**最後の一員**；②参照検索が**3 つの結果**を 1 つの空文字列に畳んでいた — `rg` は「一致なし」で exit 1 を返し、`run_command` はそれを `status="fail"`（**バイナリを起動できなかったときと同じ**）と報告するので、失敗した検索と本当の空結果が同じ `""` になった。実報告書は **5 件中 0 件**しか参照欄が埋まっていなかった（空欄は「このファイルを参照するものは無い」という**最も強い主張**として読めるのに、実際には何も検索していない。しかも `rg` はリポジトリのどこにも宣言されていない）；③`scripts/audit-production-readiness.py` が結果を**捨てていた**（素の `run_command(...)` 文）ので、監査の状態は `checks` にも `summary.checks_total` にも入らず、実報告書は **30 検査で dead-code の id が無い**（5 つの兄弟はどれも 2 検査ずつ寄与する）。監査は歩いた分母を数え（実測 `files_walked=58187`）分母 0 を清潔と呼ばず、参照欄は「実行できず」／「参照なし」／一致を**3 つの異なる値**として描いて `reference_search_failures` を運び、消費者は結果を `dead_code` 検査＋`files_walked` を**要求する** `_report_pass` に取り込む — `checks_total` は 30 → **32** になり、分母は書かれるだけでなく**読まれる**。**変異 13/13 捕捉**、全ファイルをバイト単位で復元。⚠️ **ピンの初版は正しいコードで赤くなった**（2 回、同じ理由）: スクリプト名は**リストリテラルの中**にあり直接の引数ではないので `call.args` の `Constant` 走査が外し、`_report_pass` は検査 id を**位置引数**で取るので `{"id": ...}` 走査が外した — ピンは呼び出しの下の**すべての文字列**を歩くように直した。⚠️ **そして 1 つの変異が最初のピンを生き延びた**（M7 = 要求フィールドを落とす）: テスト自身が `_report_pass(..., ["files_walked"])` と呼んでいたので、関数が要求**できる**ことは示せても、この呼び出し地点が実際に要求していることは示せていなかった — **生存はピンについての証拠**であり、呼び出し地点をソースから固定した。⚠️ **数えられない大きな失敗は 1 層上の同じ迂回**: 監査を失敗可能にする一方で捨てる側を直さなければ、放置するより悪くなったはずで、だから 3 つを 1 サイクルで閉じた。

> **2026-10-07 サイクル 84 でさらに動いた（ダッシュボードの readiness ルートが `blockers` の無い報告書を「ブロッカー 0」と読んでいた）**: 実測 **2612 passed / 8 skipped / 0 failed**（2620 collected、465.86 秒）。マーカー別は egress **319 / 1 / 2300 deselected**・非 egress **2293 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2293 + 319 = 2612`、`7 + 1 = 8`、`320 + 2300 = 2620 = 2612 + 8`）。**+4 = 新ピンちょうど**（`tests/test_a_missing_blocker_report_is_not_a_clean_report.py` に 4 本追加 — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2296 → 2300**）。⚠️ **サイクル 81 は 3 人の読み手のうち 2 人を直して 3 人目を残していた**: `load_production_blocker_report`（`ai-server/src/aegis_ai/production_readiness.py`）— ダッシュボードのルート `/api/production/readiness` が読むのはこれ — は、**`blockers` リストを持たない**有効な JSON をそのまま通していたので `production_blocker_count` が **0** を返していた。同じ報告書を `_load_blockers`（readiness 監査）と `run-readiness-report.ps1` はどちらもブロッカーにしていた。実測 2026-10-07（同一パス）: `{}` → **0**、`{"blockers": "nope"}` → **0**、`{"blockers": null}` → **0**、監査側の読み手は 3 つとも 1。サイクル 81 のテストの**docstring は族全体を主張している**（「missing, unreadable, not an object, or missing its `blockers` key」）が、assert が missing-key を試すのは `_load_blockers` に対してだけだった — **族についての主張を、族の 1 人だけが満たしていた**。ローダーに同じ `isinstance(data.get("blockers"), list)` の枝と cause `has no blockers list` を追加。**変異 8/8 捕捉＋対照緑** — 素通りへの差し戻し・cause の衝突・「unreadable だが空リスト」・キーの存在だけを見る形・**どちらの Python 読み手をずらしても**赤、`.ps1` の文言改名とリテラル削除も赤、コメントだけの編集は緑。3 ファイルすべてバイト単位で復元。⚠️ **最も強い新しいピンは差分であって絶対値ではない**: `test_the_two_python_blocker_readers_agree` は 8 行の表で両方の Python 読み手を駆動し、ブロッカー/清潔の判定が一致することを要求する — **どちら向きのずれでも**赤くなる（旧テストはそれぞれ 1 人の読み手に固定されていて、これが見えなかった）。⚠️ **3 人目は依然ピンできない**（CI に PowerShell が無く、このサンドボックスでは実行ポリシーがスクリプトを拒否する）ので、ピンは**静的**（`production_blocker` リテラル 3 つ＋不在／`blockers` 無しの 2 ケースが族と同じ語を使うこと）— サイクル 82 が確立した形。⚠️ **古い cause テストは「数える」と言って「抽出」していた**: `test_the_three_unreadable_causes_are_named_apart` は 3 のうち 2 を検査し、しかも 2 つの**別々のパス**を使っていたので、reason の違いは cause ではなく**パス**の違いだった。いまは 4 つの cause を**同一パス**で列挙する。⚠️ **書いている途中で実測したこと**: JSON の*解析*失敗とエンコード失敗はどちらも `could not be read` に落ちる（両方 `except` に届く）ので、`is not a JSON object` には**解析が通って**非 dict になった JSON が要る — `[1, 2, 3]` であって `{not json` ではない。

> **2026-10-07 サイクル 85 でさらに動いた（readiness 監査の 3 つの検査が、ソースが 1 つ動くだけで監査全体を落とし得た）**: 実測 **2618 passed / 8 skipped / 0 failed**（2626 collected、470.99 秒）。マーカー別は egress **319 / 1 / 2306 deselected**・非 egress **2299 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2299 + 319 = 2618`、`7 + 1 = 8`、`320 + 2306 = 2626 = 2618 + 8`）。**+6 = 新ピンちょうど**（`tests/test_a_source_reading_check_cannot_abort_the_readiness_audit.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2300 → 2306**）。⚠️ **`main` は 32 の検査をすべて評価してから `readiness_summary.json` を書く**ので、検査の中の例外は監査を中断させ、**前回の報告書がディスクに残る** — ダッシュボードのルート（`load_production_blocker_report`）も `_load_blockers` もそれを**新しいものとして**読む。実測 2026-10-07（`ROOT` を空ディレクトリに差し替えて 6 つのソース読み検査を駆動）: **3 つが `FileNotFoundError` を投げ**、3 つは**ファイルを名指しした `fail` を返した**。ガードの有無が非対称だった — `_docker_bind_check` / `_room_production_scope_check` / `_volume_persistence_check` は `.exists()` で守り、`_dashboard_auth_check` / `_capability_override_persistence_check` / `_mock_provider_reject_check` は守っていなかった。共通ヘルパ `_source_text(rel)` を足し、3 つとも「欠測はそのファイルを名指しした `fail`」に揃えた。⚠️ **分母の欠落も同時に直した**: `_dashboard_auth_check` は**どの枝でも `evidence=[]`** を返しており、live の readiness 要約で**唯一「測ったものを何も名乗らない」検査**だった（`dashboard_auth_required`）。いまは読んだ 2 ファイルを名乗る。**変異 7/7 捕捉＋対照緑** — 3 つのガードをそれぞれ戻す・pass 枝の evidence を空にする・ヘルパをインラインの `(ROOT / rel).read_text(...)` に戻す・メンバーを改名する・**新しいソース読み検査を足す**、がすべて赤、化粧だけの編集は緑、対象ファイルはバイト単位で復元。⚠️ **ピンの母集団は AST から発見する**（0 引数で本体がファイルを読む関数）ので、宣言集合との不一致が赤くなる — **新しいソース読み検査をガード無しで足せない**。⚠️ **ピンの初版は形を 1 つだけ見ていた**: 発見を `read_text` 呼び出しに限ったため、修正で 3 つが `_source_text` へ移った後は**その 3 つが丸ごと発見から落ちた**（サイクル 83 と同じ罠 — データを追うこと、構文 1 つではない）。⚠️ **live の判定は不変**: 6 つの検査の status は前後で同じ（すべて `pass`）、要約も `fail` / 32 検査 / 11 失敗のまま。変わったのは `dashboard_auth_required` の evidence が 0 → 2 になったことだけ。

> **2026-10-07 サイクル 86 でさらに動いた（readiness 監査の report-pass が「何も測っていない報告書」を通していた）**: 実測 **2625 passed / 8 skipped / 0 failed**（2633 collected、478.90 秒）。マーカー別は egress **319 / 1 / 2313 deselected**・非 egress **2306 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2306 + 319 = 2625`、`7 + 1 = 8`、`320 + 2313 = 2633 = 2625 + 8`）。**+7 = 新ピンちょうど**（`tests/test_every_report_pass_names_a_population.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2306 → 2313**）。⚠️ **サイクル 80 は空の母集団の族を*生成側*で閉じた**（「空のスキャンは清潔な目録ではない」）が、readiness 監査はその報告書を判定に変える**消費側**であり、`_report_pass` は「status は pass だが何も測っていない」報告書を受け入れていた。実測 2026-10-07（母集団フィールドを**持たない** `{"status": "pass", "overall_status": "pass"}` を 6 つの呼び出し点で）: `mock_inventory_report` / `capability_coverage_report` / `ui_completeness_report` / `v1_completion_report` の **4 つが pass**（空虚）、分母を名乗っていた `dead_code_report`（サイクル 83）と `android_reconnect_metrics` は正しく **fail**。サイクル 83 は 6 つのうち 1 つに分母を与えて 4 つを残していた。4 つは `files_scanned` / `capabilities` / `checks` / `checks` を要求するようになり、引数は `None` 既定ではなく**必須**なので新しい呼び出し点が省けない。**変異 7/7 捕捉＋対照緑** — 4 つのフィールド削除・`None` 既定の復活・`_report_pass` にフィールドを無視させる・フィールド無しの呼び出し点の追加、がすべて赤、docstring だけの編集は緑、対象ファイルをバイト単位で復元。⚠️ **母集団はソースから発見する**（全 `_report_pass(...)` 呼び出し点の AST 走査）ので、ピンを編集せずに新しい呼び出し点を覆う。⚠️ **そして私の前提が 1 つ実測で死んだ**: 最初の live 報告書ピンは「出荷された報告書はすべて通る」と assert したが、live の `mock_inventory.json` は `fail`（本番ブロッカー 2 件）— 不変条件は「すべて通る」ではなく「**分母を要求しても live の判定が変わらない**」である（出荷された報告書はすべてフィールドを持つ）。live の判定は不変: 要約は `fail` / 32 検査 / 11 失敗のまま、5 つの `*_report` 検査の status も不変（失敗する 4 つは母集団を読む前に status の枝で短絡する）。

> **2026-10-07 サイクル 87 でさらに動いた（readiness 監査の `_e2e_check` が、渡された `report_dir` を一度も読んでいなかった）**: 実測 **2634 passed / 8 skipped / 0 failed**（2642 collected、466.64 秒）。マーカー別は egress **319 / 1 / 2322 deselected**・非 egress **2315 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2315 + 319 = 2634`、`7 + 1 = 8`、`320 + 2322 = 2642 = 2634 + 8`）。**+9 = 新ピンちょうど**（`tests/test_e2e_check_reads_from_its_report_dir.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2313 → 2322**）。⚠️ `_e2e_check` は第 1 引数 `report_dir` を受け取り、**6 つの呼び出し点すべてが渡していた**のに、本体は一度も読まず `ROOT/data/reports/e2e/latest` を直書きしていた。既定の `--report-dir`（`data/reports`）では両者が一致するので気づけないが、`--report-dir` を変えると E2E 検査だけが既定の木を読み続け、`_report_pass`（`report_dir` を尊重する）と食い違う。実測 2026-10-07: `report_dir` に有効な `summary.json` を置き `ROOT` に何も置かないと **"Missing E2E result for docker_core"**（引数は無視されていた）。修正は全読みを `report_dir / "e2e" / "latest"` に通す — 既定では**バイト単位で同一**（`data/reports` + `e2e/latest` = 旧い直書きパス）、独自の `report_dir` では正しい。**変異 5/5 捕捉＋対照緑**（直書き `ROOT` への復帰・`e2e/latest` 接尾辞の削除・上書きループの削除・id ガードの除去・1 つの呼び出し点が `ROOT` を渡す）、対象ファイルをバイト単位で復元。⚠️ **ピンは死んだ引数の復活を AST で見る**（本体に `report_dir` という Name があり `ROOT` が無いこと — 説明コメントが `ROOT` を*名指し*しても読者にはならない）。⚠️ **live の判定は不変**: 監査を端から端まで再実行し、6 つの E2E 検査の status・`overall_status`（`fail`）・32 検査・11 失敗・ブロッカー 2 がすべて同一（書き込み前に復元）。⚠️ **別の欠陥を測って記録し、直していない**: 第 2 ループ（`docker-core.json` などの単体ファイルが `summary.json` の項目を上書きする）には**鮮度ガードが無く**、summary が `fail` でも単体が `pass` なら **pass** が勝つ（実測）。優先順位はそのままピンし、変更は所有者の決定とした。

> **2026-10-07 サイクル 88 でさらに動いた（readiness 監査の数値強制が、壊れた値で監査全体を落とし得た）**: 実測 **2667 passed / 8 skipped / 0 failed**（2675 collected、480.32 秒）。マーカー別は egress **319 / 1 / 2355 deselected**・非 egress **2348 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2348 + 319 = 2667`、`7 + 1 = 8`、`320 + 2355 = 2675 = 2667 + 8`）。**+33 = 新ピンちょうど**（`tests/test_a_malformed_soak_number_does_not_abort_the_audit.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2322 → 2355**）。⚠️ `_display_soak_check` は 3 つの報告書フィールドを `int(data.get(...) or 0)` で、`_e2e_check` は 4 つ目を `int(match.get("duration_ms") or 0)` で強制していた。**真値だが数値でない**値は例外になる（実測: `"abc"` → `ValueError`、`[1, 2]` → `TypeError`、`{"a": 1}` → `TypeError`、`failure_count="x"` → `ValueError`）。`main` は書き込み前に全検査を評価するので、例外は監査を落とし、**前回の報告書**をディスクに残す — サイクル 85 と同じ形を、欠けたファイルではなく**値**から踏む。修正は `_as_int` を追加し、**例外を出さなかったすべての入力で `int(value or 0)` と厳密に一致**し、例外を出した入力でのみ `None` を返す。3 つの soak 入力は `None` を「測定不能」として**フィールド名を名乗る `fail`** にし、`duration_ms` はメタデータなので `0` に畳んで**判定を変えない**。**変異 7/7 捕捉＋対照緑**、バイト単位で復元。⚠️ **差動ピンが修正前の式を oracle として保持**するので、「よく形成された入力で判定が変わらない」は主張ではなく実測。⚠️ **族は閉じた**: `int(...)` がマッピングを読む形はもう無い（AST 走査で空集合を assert）。⚠️ **到達性は正直に**: 現在の writer は数値しか書かないので欠陥は**潜在**（手編集・部分書き込み・第三者 writer で顕在化）。live の判定は不変（`fail` / 32 / 11 / ブロッカー 2、書き込み前に復元）。

> **2026-10-07 サイクル 89 でさらに動いた（readiness 監査の report-pass が「ゼロを測った報告書」を清潔と読んでいた）**: 実測 **2706 passed / 8 skipped / 0 failed**（2714 collected、466.10 秒）。マーカー別は egress **319 / 1 / 2394 deselected**・非 egress **2387 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2387 + 319 = 2706`、`7 + 1 = 8`、`320 + 2394 = 2714 = 2706 + 8`）。**+39 = 新ピンちょうど**（`tests/test_a_zero_population_is_not_a_clean_report.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2355 → 2394**）。⚠️ サイクル 86 は `_report_pass` に母集団フィールドを**必須**にしたが、空判定が `data.get(field) in (None, "", [])` だった — **ゼロはそのどれでもない**ので、`{"status": "pass", "files_scanned": 0}` は**清潔**と読まれ、`capabilities: 0`・`checks: 0`・`files_walked: 0` も同様だった。「何も測っていない報告書」はまさに空の母集団の族（サイクル 80/83/86）が捕まえるためにある。判定は `not data.get(field)` になり、`0`・`False`・`{}` も空になる。⚠️ **締め付けは、正しい判定を反転させるなら誤り**: live の `android-real.json` は `heartbeat_failure_count: 0` を持ち、これは**良い**結果なので、母集団リストに畳むと正しい `pass` が `fail` になる。よって 2 種類に分ける — `required_fields`（*母集団*、空 = falsy）と新しいキーワード専用 `present_fields`（*指標*、ゼロが正しい）。android の呼び出し点は `["checks"]` を要求し、`reconnect_count` / `heartbeat_failure_count` は**持つだけ**になった。**変異 7/7 捕捉＋対照緑**、バイト単位で復元。⚠️ **live の判定は不変**: 監査を端から端まで再実行し、32 検査と `summary.json` / `readiness_summary.json` がバイト単位で同一（書き込み前に復元）— live の `android-real.json` は非空の `checks`（7 件）と `heartbeat_failure_count: 0` を持ち、旧・新どちらの論理でも通る。

> **2026-10-07 サイクル 90 でさらに動いた（readiness 監査の報告書の読み書き 7 箇所が `--report-dir` を無視していた）**: 実測 **2729 passed / 8 skipped / 0 failed**（2737 collected、462.67 秒）。マーカー別は egress **319 / 1 / 2417 deselected**・非 egress **2410 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2410 + 319 = 2729`、`7 + 1 = 8`、`320 + 2417 = 2737 = 2729 + 8`）。**+23 = 新ピンちょうど**（`tests/test_every_report_read_honours_the_report_dir.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2394 → 2417**）。⚠️ `main` は副監査を `--report-dir <report_dir>` で走らせ、`_e2e_check`（サイクル 87）は `<report_dir>/e2e/latest` を読むのに、**7 箇所**が報告書の木を `ROOT` に直書きしていた — `pc_real` / `android_real` の読み（2 箇所）・`summary.json` / `summary.md` の**書き**・`_secrets_check`（副監査は `main` に `--report-dir` を渡されて書いた先と別の木を読んでいた）・`_capability_override_persistence_check`・`_display_soak_check`。独自の `--report-dir` で実測: 3 つの検査の `evidence` は ROOT の木を名指しし、`<custom>/e2e/latest/summary.json` は書かれず、ROOT の `summary.json` / `summary.md` が**書き換えられた** — サンドボックス実行が運用者の本物の E2E 要約を上書きし、サンドボックスには何も残らなかった。修正は 7 箇所すべてを `report_dir` に通す。引数ゼロだった 3 つの検査はパラメータを得て、`_display_path` が既定の evidence 文字列をバイト単位で保つ（ROOT の内側なら相対）—— ROOT の外の報告書ディレクトリで `ValueError` を出さない。⚠️ **既定は no-op**: 監査を端から端まで再実行し、32 検査の status と E2E 要約が同一（evidence 1 つだけ区切り文字が変わる — パスは同じ）。**変異 10/10 捕捉＋対照緑**、バイト単位で復元。⚠️ **族を閉じたことでサイクル 85 のピンが赤くなった**（*引数ゼロ*の読み手を発見していた）ので、その発見は「唯一のパラメータが `report_dir`」を許すように直した — 許容リストの更新であって緩和ではない。

> **2026-10-07 サイクル 91 でさらに動いた（readiness 監査が*走らせる* 2 つの姉妹監査が `--report-dir` を無視していた）**: 実測 **2741 passed / 8 skipped / 0 failed**（2749 collected、472.56 秒）。マーカー別は egress **319 / 1 / 2429 deselected**・非 egress **2422 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2422 + 319 = 2741`、`7 + 1 = 8`、`320 + 2429 = 2749 = 2741 + 8`）。**+12 = 新ピンちょうど**（`tests/test_every_sibling_audit_honours_the_report_dir.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2417 → 2429**）。⚠️ サイクル 90 は readiness 監査**自身**の報告書パスを `--report-dir` に通したが、それが**走らせる**姉妹 2 本は追随していなかった。`scripts/audit-ui-completeness.py` は **`argparse` を一切呼んでいなかった**（`parse_args` / `args.` の出現ゼロ）ので `--report-dir` は丸ごと無視され、独自ディレクトリで駆動すると `ROOT/data/reports/ui_completeness.{json,md}` に書き、独自ディレクトリは作られず、ROOT の報告書の mtime が動いた（readiness 監査はその後 `<custom>/ui_completeness.json` を読んで**何も無い**）。`scripts/audit-v1-completion.py` は独自ディレクトリに**書き**はしたが、4 つの報告書**読み**がモジュール定数（`E2E_SUMMARY` / `UI_REPORT` / `MOCK_REPORT` / `CAPABILITY_REPORT`）で `ROOT` を名指ししていたので、空のディレクトリを指しても evidence は `data/reports/...` を名乗った — サンドボックス実行が**運用者の本物の報告書**を読んで判定していた。修正は全報告書パスを `report_dir` に通し、`_display_path`（posix、ROOT の内側なら相対）が既定の evidence をバイト単位で保つ。⚠️ **既定は no-op**: 両監査を既定の `--report-dir` で再実行し、`ui_completeness.json` / `.md` と `v1_completion.md` が**バイト単位で同一**、`v1_completion.json` は `generated_at` / `duration_ms` を落とせば同一。⚠️ **端から端まで測った**: readiness 監査を独自ディレクトリで走らせると、修正前は `ui_completeness.json` がそこに**存在しなかった**のが、修正後は存在し `ui_completeness_report` / `v1_completion_report` が「報告書が無い」ではなく「報告書の status が fail」を返す（＝読めた）。**変異 6/6 捕捉＋対照緑**、バイト単位で復元。⚠️ **族を閉じたことでサイクル 80 のピンが赤くなった**（4 つの定数を monkeypatch して読みを差し替えていた）ので、`--report-dir` で差し替える形に直した — 主張（分母を要求する）は不変で、差し替え方だけが新契約に追随した。

> **2026-10-07 サイクル 92 でさらに動いた（readiness 監査の E2E 検査が、理由が 1 層下にある失敗の原因を記録していなかった）**: 実測 **2755 passed / 8 skipped / 0 failed**（2763 collected、544.13 秒）。マーカー別は egress **319 / 1 / 2443 deselected**・非 egress **2436 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2436 + 319 = 2755`、`7 + 1 = 8`、`320 + 2443 = 2763 = 2755 + 8`）。**+14 = 新ピンちょうど**（`tests/test_a_failing_e2e_check_carries_its_cause.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2429 → 2443**）。⚠️ `_e2e_check` は一致したレコードの**トップ水準**の `error` だけを記録していた。生きた `manager-e2e.json` は `status: fail` で `error: ""`、理由は**10 件の入れ子 `checks`**（7 x 「リモート サーバーに接続できません。」+ 3 x 「ai-server container is not running」）にあり、`readiness_summary.json` は原因なしの `fail` を、`readiness_summary.md` は空の error セルを出していた。修正は `_result_cause`（トップのメッセージ → 失敗した入れ子チェック（5 件まで、`(+N more)` 付き）→ status を名乗る文。非 pass は `""` を返さない）。⚠️ **既定は欠陥の箇所だけが動く**: 既定 `--report-dir` で修正前後のスクリプトをそれぞれ走らせて突き合わせると、差は **9 leaf** — 6 x `duration_ms`、トップ `duration_ms`、`generated_at`、そして**意味のある差は `checks[21].error`（`manager_e2e`）ただ 1 つ**。32 の status・全 `evidence` / `report_path`・他の error は同一で、md 面で動くのは `Stateful Manager E2E` の行だけ。**変異 6/6 捕捉＋対照緑**、バイト単位で復元。⚠️ 記録のみ（所有者判断）: 6 つの副監査検査は `stderr` しか記録せず理由は `stdout` に出る（**サイクル 93 で閉じた** — 挙げられていた二者択一は偽で、呼び出し点で両ストリームを読めば共有部品は触らずに済む）、`_load_json` / `read_json` に BOM 耐性が無い（実測: 68 件中 48 件が BOM、readiness 側は `utf-8-sig`）— **潜在**。⚠️ 本サイクル中に **git オブジェクトストアの消失（第 3 回）** が発生し、`origin` から復旧した（`INCIDENT_2026-10-07_git-object-loss-3.md`）。

> **2026-10-08 サイクル 93 でさらに動いた（readiness 監査の 6 つの副監査検査が、理由が `stdout` にある失敗の原因を記録していなかった）**: 実測 **2768 passed / 8 skipped / 0 failed**（2776 collected、508.06 秒）。マーカー別は egress **319 / 1 / 2456 deselected**・非 egress **2449 / 7 / 320 deselected** で、**3 つの選択が厳密に整合**する（`2449 + 319 = 2768`、`7 + 1 = 8`、`320 + 2456 = 2776 = 2768 + 8`）。**+13 = 新ピンちょうど**（`tests/test_a_failing_sub_audit_check_carries_its_cause.py` — 非 egress なので egress の passed / marked は 319 / 320 のまま動かず、**deselected は 2443 → 2456**）。⚠️ `main` は 6 つの副監査を `run_command` で走らせ、各検査の原因を `<proc>["stderr"] if <proc>["status"] != "pass"` として記録していた。`run_command` は `stdout` と `stderr` を**別々に**捕るが、失敗する監査は一行の理由を `stdout` に出して非ゼロで終わる — 6 つすべてで `stderr` は **0 バイト**（実測）、失敗した 4 つは `error=production_blockers=2` / `error=failing=1` / `wrote ...ui_completeness.md` / `open=5 partial=5 blockers=0` を印字していた。よって 4 つは `readiness_summary.json` に `status: fail, error: ""` として届いていた — サイクル 92 が E2E 検査で閉じたのと同じ欠陥。修正は `_process_cause(result)`（`stderr`（予期しない traceback の落ちる先）→ `stdout` → 終了を名乗る文。非 pass は `""` を返さず、pass は `""` のまま）。⚠️ **既定は欠陥の箇所だけが動く**: 1 つの報告書ディレクトリを両実行で共有し間で消すと、修正前後の差は **32 検査中ちょうど 4 つ、すべて `error` のみ**で、4 つとも副監査の母集団の内側。`status` / `evidence` / `report_path` / `name` はすべて同一。**変異 4/4 捕捉＋対照緑**、バイト単位で復元。⚠️ **サイクル 92 の主張を 2 つ訂正**: あのブロックは 6 つの検査の沈黙を「`*_report` の姉妹が原因を運ぶ」ことで正当化していたが、姉妹は**原因を運ばない** — `_report_pass` は `f"Report status is {status}"` を返し、終了コード検査が既に与えた status を繰り返すだけである。また「記録のみ」の注記は直すと「`run_command` の契約が変わる」と書いていたが、**変わらない** — 呼び出し点で両ストリームを読めば共有部品は触らずに済む。⚠️ **`audit-ui-completeness.py` は修正を正直に保つ例外**: 出力パスしか印字しないので、記録される原因は理由ではなく報告書へのポインタ — 沈黙よりはましだが診断ではない。

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
| `（本節）` | **B-6 を測りにいって、その一段下に B-20 を発見 — スキーマは 27 の境界を宣言し、生きた書き込み経路は 1 つしか検査しない**: B-6 は「`max_autonomous_runs_per_hour` を配線するか削除するか」で、その前提は「バリデータだけが読む」。**前提は正しかったが、そのバリデータが何をしているかを読んで別の欠陥が出た** — 設定スキーマは **27 フィールド**に `ge`/`le` の境界を宣言しており、それらは**構築時**に強制される。しかし生きた唯一の書き込み経路 `SettingsStore.update_section` は提案設定を**無検証の `setattr`** で組み立て、`validate_settings_change` が再検査する境界は **1 つだけ**（`max_autonomous_runs_per_hour > 100` — そのフィールド自身の `le=100` の**写し**）。**27 のうち 26 が API 経由で突破でき、値はディスクに残る**（実物の `SettingsStore` を `tmp_path` に対して 1 フィールドずつ駆動し、読み戻して確認 — 26/26 突破・1/1 阻止）。**仮説を 2 回外した**: ①「検査は発火しない」→ **誤り**。`le=100` が構築を守るが**代入は検証されない**ので、`setattr` 経路では検査が**唯一の防波堤**であり、そこに 1 つだけ手書きされている。② 自作の走査が `VALIDATION_HINTS` の `guard` にクラス名 `SettingsPermissionGuard` が一致して 5 件を偽陽性（`clipboard_capture_enabled` などは `permissions.py` の**生きたゲート**）。**化粧ではない理由**: 突破できる集合に**保持期間の上限**が入り、`backup/retention.py:60` が `episodic_retention_days` を `max_age_ms` に変換して prune するので、スキーマが拒否する値で 1 世紀分を保持できる。同じモジュールの docstring は 4 つの保持を "Handles:" と並べていたが実測は **episodic のみ強制 / notification と screenshot は報告だけ / audit は `self._audit` が保存されどのメソッドも読まない** — **「報告だけ」は UI からは実装済みに見える**（docstring は測定に合わせて訂正。誤った主張の訂正はオーナー判断ではない）。ピン `tests/test_settings_edit_path_enforces_schema_bounds.py`（6 関数）は境界を**モデルから発見**、バリデータの読みを **AST から発見**、突破の有無を**実物のストアを駆動して**判定し、突破集合と阻止集合を**両方向の等式**で固定するので**書き込み経路を直しても落ちる**。**変異 10/10 捕捉** — うち **M5 はハーネスの期待誤り**（`le` だけ落としても `ge` が残るので観測が変わらない＝変異が対象を動かしていない）、**M4 は変異自体が壊れていた**（`ConfigDict` を import していない `models.py` に書いたので `NameError` で collection ERROR。**ERROR の原因を読むこと — 自分の変異が壊れている場合は「捕捉されなかった変異」ではない**）。**修復方向の変異を 3 つ**（バリデータに 2 つ目の境界を足す / `update_section` が検証済みモデルを構築する / `validate_assignment` を有効化）入れて**3 つとも落ちる**。バリデータを 27 個の境界を再検査するよう**拡張しない** — それはスキーマの写しを書き込み経路に置くことで、このリポジトリが繰り返し見つけている重複そのもの（docstring に明記）。ai-server **1734 → 1740 passed / 31 skipped**（**+6 = 新規 6 関数**、実測 403 秒）。原ファイル 5 本はバイト単位で復元（sha256 検証）。**§0.2 に A-9**（推奨は `update_section` が検証済みモデルを構築する形 — `validate_assignment` は `list[str]` を返す契約を壊すので不可）、**§4.3 にクラス 16**（宣言は構築でしか検査されない） |
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

| `（本節）` | **「走らないテスト」を系統的に監査し、名前が主張することを検査していないテストを 3 件直した**: 前節の欠陥（モジュール全体の `pytestmark` が**デバイス不要なテスト**を飲み込んでいた）は**型**なので一般化して掃いた。**① スキップ機構の全数調査**: `ai-server/tests/` のモジュールレベル `pytestmark` は 6 つだけで、**スキップは 1 つ**（前節で修正済み）、残る 5 つは egress のマーカー（走る）。他の Python ルート（browser / room / android / SDK）にモジュールレベルの skipif は**無い**。`collect_ignore` / `xfail` / `--ignore` も**無い**。**② スキップ 30 件の実測内訳**（`-rs`）: 23 件 = `test_ineffective_flags.py:273` の**記録済み負債**（未読 22 + 意図的 1、各件に理由文）、**4 件 = `android_local`**、**3 件 = `test_openhands_backend.py`**（`openhands.sdk` 不在）。**③ 残る 4 件の android テストは 4 件とも本当にデバイスを要する**（`adb` / アプリ起動 / gRPC 越しの実機データ）のでゲートは正しく絞られている。**④ openhands の 3 件は設計どおり** — SDK は**別プロセス**（`aegis_agent_server/main.py` = `aegis-openhands-agent.service`）用で本体には入れない方針がその docstring に明記されている。**⑤ 本題**: テスト関数 **1530 件**を AST で走査し、**`assert` も `pytest.raises` も `raise` も持たないもの 6 件**を検出。2 件は import スモーク（正当）、**3 件が本物** — `test_task_manager_can_complete_task` / `..._can_fail_task` は名前が「can complete」なのに**状態を一切検査していない**（`complete_task` は未知 id で `None` を返すので「例外が出ない」は id が間違っていても通る）。`test_audit_manager_with_no_event_manager_is_noop` は docstring が「`policy.decision` を publish しない」という**検証不能な主張**をしていた（`event_manager=None` に観測点が無い）。**状態遷移・書き込み・`result_summary` / `error` を assert するよう直し、変異で証明** — **4/4 捕捉、うち 1 件は src 側**（`AuditManager.append` から `self._log.append(entry)` を消して「黙って捨てる」変異を作ると狙ったメッセージで落ちる）。原ファイルはバイト単位で復元（sha256 一致）。**⑥ 副産物**: `pc_local` / `room_local` / `e2e` の 3 マーカーは **`pyproject.toml` に宣言されているが使うテストが 0 件**（`pytest -m e2e` は **0 件を選択**し 1807 件を deselect）。`test_e2e_lifecycle.py` の**モジュール docstring が「full approval lifecycle」のまま**だった（承認レッグは 2026-09-27 に削除済みで、同じファイルの内側の docstring はそう書いている）ので訂正。**⑦ ゲート自体が自動化されていない**ことは **§0.2 の C-5** に登録。**テスト総数は 1777 / 30 で不変** — 追加ではなく主張の強化なので数値表は触らない |

| `（本節）` | **規約を直し、その規約に違反していた行と、同じ主張の「他の写し」を全部掃いた**: ① §0.2 の脚注は「各行は**問いと選択肢**だけを持ち、**測定値は書かない**」と言っていたが、**実測すると 15 行中 7 行が測定値を持ち**、しかも表には「**推奨と理由**」列と「**決まらないと何が止まるか**」列がある — **規約の方が実態と食い違っていた**。腐るのは**日付の無い現在値**だけなので、規約をその形に狭め、`問い` 列は数を伴ってよい（ただし**正典へのポインタを添える**）と明記した。C-3 の「12」と A-5 の「12 回」が 2026-09-29 に消されたのは**まさにこの形**で、狭めた規約はその一般化。② **狭めた規約をその場で適用** — B-2 の「1,104 行」・B-3 の「約 700 行」・B-6 の「22 件 / 26 個 / 10 個」・C-2 の「6 項目」を正典（§5.7 / §5.14 / §1.1・§5.16）への**ポインタに置換**（09-29 の「ポインタ化」と同じ手当て）。③ **B-6 の撤回が写しに届いていなかった** — 撤回は §1.4・`MEMORY.md`・skill 1 つに適用済みだったが、**§4.3 のバグクラス B-6 行は反証済みの 3 主張（「原因を特定」／「入れ子名でのみ発生」／「`update-ref` は解決策にならない」）をそのまま持ち、§1.4 と正面から矛盾**していた。加えて skill `aegis-consolidate-a-duplicated-fact`・`aegis-add-dashboard-page`・**インシデント報告**の 3 写し（履歴文書は書き換えず、冒頭に日付入りの訂正バナーを追加 — **観測事実は有効**で、撤回したのは*機序の説明*だけ）。④ **skill `aegis-verify-and-test` の push レシピが古い入れ子名**（`HEAD:refs/heads/cursor/…`）を指していた。**実測**: `git ls-remote --heads origin` は 2 本だけ（`cf-grpc-and-goal-hygiene` / `main`）で **`refs/heads/cursor/*` は存在しない** — そのまま実行すれば**リモートに 2 本目のブランチを作り、本物を古いまま残す**ところだった（無音の分裂）。⑤ 深さの数字が文書間で揺れていた（§1.4 は 2/3/4、skill は 1/2/3 — **葉を数えるかの差**）ので**数字をやめて ref 名で書く**ことにし、skill 側の表に規約を明記。**教訓を `MEMORY.md` に記録**: *訂正は写しを全部掃くまで終わらない*。**コードは不変** — テスト数は `ddced6a` の **1777 / 30** のまま |

| `（本節）` | **`docs/testing-real-devices.md` が「存在しないテスト基盤」を説明していた（型 6）**: 推奨 #2「未使用マーカー」を調べる過程で、**マーカー表そのものが虚構**と判明。**実測**: 登録済みマーカーは `android_local` / `pc_local` / `room_local` / `e2e` / `egress` の 5 つだが、**テストが使うのは `android_local`（1 モジュール）と `egress`（7 箇所）だけ**。表に載っていた `mock` / `real_browser` / `real_pc_host` は**未登録**（pytest はその名前を知らない）。さらに**文書が与えるコマンドが実際に何を選ぶか**を測ると: `-m "not real_browser and not real_pc_host"`（本文は「CI の mock テスト」と称していた）は **1807 件すべてを選択**＝**何も絞っていない**、`-m real_browser` / `-m real_pc_host` / `-m e2e` / `-m pc_local` / `-m room_local` は **`no tests collected (1807 deselected)` で exit 5**、`-m android_local` は **4 件**、`-m egress` は **233 件**。本文が名指しする `test_pc_observe_e2e.py` / `test_pc_action_e2e.py` / `test_room_observe_e2e.py` は**存在しない**。`docker compose --profile real-browser` / `--profile pc-host` も**虚構** — compose ファイル中の `profiles:` は `docker-compose.production.yml` の `room` **1 つだけ**。**正しい部分（Android 節・スクリプト表・実機フロー）は触らず**、虚構の 7 箇所を実測で置換した（`docs/pc-server.md`・`docs/room-server.md` が同種の主張を直したのと同じ手当て）。**マーカー登録は残した** — `pc-server.md` は既に「登録済みだが誰も使わない」と正しく書いており、削除するとそちらが嘘になる |
| `（本節）` | **`aliases` は「読者はいるが生産者がいない」— 最高重みの検索項が本番データを持たない（型 1 の裏面、記録のみ）**: 既存の alias テストは**フィクスチャの上で通っていた**（同ファイルの `_write_capability` が `"aliases": aliases or []` を書く）ので、**本番 manifest を測った**。**実測**: 出荷 manifest **128 件のうち `aliases` を宣言するのは 0 件**（`tags` は **113 件**が宣言 = 陽性対照）。ところが `capability_index._keyword_score` の重み付きフィールドは `aliases` に **1.6** を与えており、**全フィールド中で最高**（`title` 1.2 / `id` 0.9 / `tags` 0.8）。**帰属は 1 箇所だけ** — `CapabilityDocument.aliases` の構築は `capability_index.py:462` の 1 箇所のみで、そこは `manifest.aliases` を読み、`CapabilityManifest.aliases` は `folder_registry.py:257` が manifest JSON から読む。よって**生産者は manifest のキーただ 1 つ**で、それは**誰も書かない**。**挙動への影響は無い**（`" ".join([])` は `""` になり、分母 `max_score` の `if text` で除外されるので、スコアは一切動かない）— 純粋な死んだ重み。**同名が 3 つあり、生きているのは manifest のものだけが空**という判別不能性も記録した: ① `CapabilityManifest.aliases`（manifest の検索語。**本番で空**）② `CapabilityCatalog._aliases`（short/旧 id → 正準 id、**254 件が生きている**）③ `FolderCapabilityRegistry._short_names`（`_cap_reg.get()` の**内側**で `_aliases` より先に引かれるので、short 名では②を覆い隠す）。**ピン 2 本**（`tests/test_capability_index.py`）: ① **出荷 manifest を発見して**（手書きの一覧にしない）`aliases` が空であることを**等式**で固定、**非空虚ガード 2 つ**（`entries` が空でない／`tags` を持つ能力が実在する）② **その空のキーが今も `list_for_llm()` に出ている**（記録の反証可能な半分 — キーが消えれば「空」は LLM の見るものではなくなる）。**変異 3/3 捕捉 — 各変異が*狙った* assertion を発火させたことまで確認**（M1 実在 manifest に alias を足す→**等式**が発火、名指しで報告／M2 `list_for_llm()` から鍵を落とす→**surface ピン**が発火／M3 走査の根を盲目化→**非空虚ガード**が発火）。原ファイル 3 本は**開始時に捕捉したバイト列から復元**（sha256 一致）。**`DELEGATION.md` §4 項目 15**（オーナー項目 — 配線は 128 件に alias を書く製品判断、削除は manifest スキーマの縮小）。**実測**: ai-server **1902 passed / 8 skipped / 0 failed**（410.51 秒）= 前回 **1900** + **2 = 新ピンそのもの**。**1 回目の実行では `tests/test_endpoint_resolver.py::test_resolve_tcp_endpoint_tries_candidates_and_caches` が 1 件だけ落ち、再実行では落ちなかった**（＝間欠的）— **この変更と無関係**と帰属した: ① 総数が **1902 = 1900 + 2** で厳密 ② 当該ファイルは**単独実行で 6 passed** ③ 機構は `_candidate_hosts` が env より**先に** `_MEMORY` を読むので、**漏れた `status-check` スレッドが実 LAN アドレスを書き込む**と `probed[0]` が変わる — `tests/conftest.py:21-60` が**同型を既に文書化**し、そのための検知器（`_no_leaked_status_thread`）も置いている。**検知器があるのに 1 度発火した**ことは記録に値する（再現しなかったので欠陥とは断定しない — 監視項目） |
| `（本節）` | **`ruff` を CI ゲートに入れた（§4 項目 7 を実行）— 記録していた前提「スクリプトに 1 行」は 3 点で偽だった**: 記録は「いまゲートを足せば**新規負債なしで入る**／戻し方は**スクリプトに 1 行**」と書いていた。**測ると 3 つとも成り立たなかった**。**① CI venv に ruff が入っていない** — 台本が使う `$RepoRoot/.venv` は **uv 管理で `pip` 自体が無い**（`python -m pip` → `No module named pip`）。`pyproject.toml` の `[project.optional-dependencies] dev` には `ruff>=0.4` が**宣言されているのに未導入**だったので、`uv pip install --python .venv/Scripts/python.exe "ruff>=0.4"` で導入（**ruff 0.16.9**）。**② `tests/` に F821 が 1 件あった**（`src/` は 0 件で、記録どおり）。`tests/agents/test_agent_profiles_router.py:238` の `def _build_router(...) -> "AgentRouter"` — 実体は**関数本体で import される正しい前方参照**で実行時の問題は無い。ただし抑制が **`# type: ignore[name-defined]`（mypy の書式）**で書かれていた。**mypy を走らせるものはリポジトリに 1 つも無い**（`pyproject.toml` の dev 依存に `mypy>=1.8` はあるが、`scripts/` にも CI にも呼び出しが無い — 唯一の言及は `scripts/audit_common.py` の `.mypy_cache` 除外）ので、**この抑制は何も抑止していなかった**。走る側の ruff は `# noqa` しか見ない → **`# noqa: F821` に置換**（リポジトリの慣習も `# noqa:` が優勢で 40 箇所以上ある）。**③ 全ルールでは 994 errors**（`E501` 305 / `UP007` 104 / `I001` 67 / `UP035` 21 / `E402` 12 / `F401` 12 …）なので `--select F821` に限定。**絞る根拠**: F821 だけが「**負債ゼロ**」と「**スイートが緑のまま見逃した実バグを捕捉済み**」の両方を満たす（B-5① の配線時に `_create_autonomous_loop` へ `_build_runtime` のローカルを渡したバグを、全スイート緑のまま **ruff だけ**が捉えた）。**台本への追加は [1/4]（fail-fast）** — 安い静的検査を 7 分のスイートの前に置く。**非空虚ガードを自分で足した（測定で必要と判明）**: `ruff check <存在しないパス>` は**警告を出すだけで exit 0**（実測 `rc=0`）なので、改名・移動で対象が消えても `[PASS]` と表示される — **egress 床が防いでいるのと同じ空虚化**で、その根拠は台本の冒頭に既に書いてある。`src`/`tests` の存在と `.py` の実在を先に assert する。**検証**（台本はこの環境で実行できない — PowerShell ツールがネイティブ実行ファイルを起動できず `$LASTEXITCODE` が空になる。P2-0 と同じ手当て）: **AST パース errors=0**、**ガードの意味論を式ごと実行して確認**（両方存在→`missing=0 / files=544 / 発火せず`、片方改名→`missing=1 / 発火`、両方消失→`発火`）、**変異 2/2 捕捉**（`src/` に未定義名を足す→`rc=1` で**その名前を報告**／スコープを外す→`rc=1`）、原ファイルは sha256 一致で復元。**実測**: ai-server **1902 passed / 8 skipped**（395.27 秒、**前回と同数** — コメント 1 行の変更なので数は動かないのが正しい）。**副産物 2 件**: ① **`mypy>=1.8` は宣言されているのに走らせるものが無い**（`ruff` と同じ型。ただし mypy 側は今回スコープ外 — `# type: ignore` を消したので、mypy を将来入れるなら**モジュール先頭 import に直す方が正しい**旨を台本と本行に残した）② `.venv` は**壊れた `.pth` を 2 つ抱えている**（`distutils-precedence.pth` → `_distutils_hack` 不在、`pywin32.pth` → `pywin32_bootstrap` 不在）。**毎回の python 起動で stderr に警告が出る**がテスト結果には影響しない（環境側の観察であってリポジトリの欠陥ではない — 未処理） |
| `（本節）` | **B-6 の「未検証の手がかり」を測ったら、手がかりではなかった — 代わりに `.git/` の中の第三者を据えた**: 前節の台帳行が残した「まだ試していない手がかり」（`git fsck` が報告する腐った reflog）を測りにいった。**① 手がかりは手がかりではなかった** — その reflog（`.git/logs/refs/heads/cursor/cf-grpc-and-goal-hygiene`、15 行）は**失われたコミットの SHA とメッセージを保持する唯一の記録**で、インシデント報告 §8 が**まさにその理由で残した**もの。**破壊せずに試す方法が無く**、**存在しない ref の reflog を書く経路が無い**ので因果の道も無い。**唯一の記録に対して破壊的な実験を行う直前で止めた**（記録ではなく実測を読み直したから）。**② 除外を 1 つ増やした** — `.git/hooks/` に**有効なフックは 1 つも無い**（すべて `.sample`）、`core.hooksPath` も未設定。**`reference-transaction` / `post-commit` が ref を消す経路は無い。** **③ `git fsck` は reflog 以外に何も報告しない**（実測: `HEAD` **226** / 入れ子 **30** / フラット **30**、すべて `invalid reflog entry`、**オブジェクト / ref の整合性エラーは 0**）＝オブジェクトストアは健全。**④ 新しい手がかり** — `.git/` の中に **git 以外のツールが所有するディレクトリが 2 つ以上**ある（`.git/cursor/crepe/` **20 MB**、2026-09-04 19:19 ／ `.git/refs/codex/turn-diffs/` は**空**だが**中身が変わったのは 2026-09-29 18:54 ＝ 消失の検知と同時刻**、親 `refs/codex` は 2026-09-04 19:19 ／ `.git/mimocode-project-id`）。**うち 1 つは ref の名前空間を書く。** 症状（rc=0 で ref が消え、囲むディレクトリごと消える）の**形と整合する**が、**相関であって機序の証明ではない**。**⑤ 候補 A を精密化** — `gc.auto=0` / `maintenance.auto=false` で**自動** gc はもう走らないが、これは**候補 A の反証ではなく**、**ref の消失も止めない**（skill が実測で記録済み）。**オブジェクトの消失と ref の消失は別の症状**。**コードは不変** |
| `（本節）` | **「完成まで推奨で」の委任を受け、完成の定義と委任台帳を作り、A-13(a) を実行した**: オーナーの指示（2026-09-30）は「AEGIS の完成まですべて推奨で進め、問題点は完成後に修正する」。**まず「完成」を測れる形に定義した** — 台帳自身の契約（§0.2 が空＝実装すべきことが無い）を採用し、§3.1 の北極星 2 穴と §3.2 の機能表を足して **3 条件**にした。**そして「推奨では閉じられないもの」を先に切り分けた**（負担量の指標の定義 / Room の実ハードウェア / vision のローカル化＝オーナーが不追及を決定済み / C-1・C-2・C-4）— **これを曖昧にすると「完成」の主張が嘘になる**。判断の記録と戻し方は新規 **`DELEGATION.md`** に置いた（§0.1 は「何をしたか」、§0.2 は「未決」、`DELEGATION.md` は「委任で決めたこと＋戻し方」で役割を分けた）。**方針**: 各行の「推奨」列は**もともと保守側の枝**なので、委任で行うのは**その枝の実行**であって新しい判断の発明ではない。**A-13(a) を実行** — `AEGIS_PUBLIC_CORE_HOST` / `AEGIS_PUBLIC_CORE_GRPC_PORT` / `AEGIS_PUBLIC_DASHBOARD_URL` は **`.env.example` にしか出現しない**ことを `git grep`（追跡ファイルのみ＝`node_modules` を踏まない）で実測してから削除。**A-13(b) `AGORA_MASTER_USER` は消さず**、`.env.example` に「compose が渡すが読むコードが無い／将来の機能か消し忘れかはオーナー判断」と**現地に**書いた。**道具の欠陥を 1 つ踏んだ**: 最初の編集は**リストを行番号で splice したあと、splice 前の番号を再利用**したため挿入で添字が 3 ずれ、**生きた変数 `AEGIS_GRPC_INVOKE_TOKEN` と無関係なコメント行を削除**していた（`git diff` が捕まえた）。**git blob のハッシュが捕捉済みの元バイト列と一致することを確認して復元**し、道具を**行ごとの判定関数**（添字を使わない）に書き換えた。書き換え後の初回は**ガードが正しく拒否**した — `AEGIS_PUBLIC_CORE_GRPC_PORT=50051` は値を持つので**完全一致では 3 行目が落ちない**（名前で照合すべき）。**コードは `.env.example` のみ、テスト数は不変** |
| `（本節）` | **委任で 5 行を閉じた（A-6 / A-11 / A-13 / B-2 / B-3）— うち 1 行は「行の方が古かった」**: 委任（「完成まで推奨で」）に従い、**§0.2 の各行の推奨列＝保守側の枝**を実行して行を閉じた。**閉じる前にピンを実行した**（記録を信じない）: `tests/test_forced_gate_stays_retired.py` / `tests/test_evaluation_pack_is_dead.py` / `tests/test_autonomous_execution_path_is_single.py` が **64 passed**（2026-09-30 実測、18.91 秒）。**A-6**（`aegis_ai/permissions/`）と **A-11**（`ReflectionEngine.approval_decisions`）は ③ 現状維持 — ② は前者が**強制承認ゲートの復活**、後者が**製品判断**なので選ばない。**A-13** は (a) 3 名削除・(b) 現状維持＋現地注記。**B-2**（`evaluation/` の死んだ部分グラフ）は ③。**B-3** は ③ だが、**§0.2 の行が「図が嘘のままなのは残る」と書いていたのに対し、`docs/self-development.md` の冒頭図には既に 2026-09-29 に実測との食い違いの注記が入っていた** — **行の方が古かった**（同じ事実が §0.1 の B-3 行と文書では正しく、§0.2 の行だけが取り残されていた。型 9 の変種）。よって「図の訂正」という軽い判断は**既に済んでおり**、残るのは配線か削除かという製品判断だけ。**閉じた 5 行の測定内容は失われていない** — 各 ③ の実施は §0.1 の既存の台帳行（`f2948a1` / A-11③ の行 / A-12③ の行 / `d4aae94` / B-3 の行）にあり、ピンはテストとして残っている。**コードは不変、テスト数は不変** |
| `（本節）` | **A-12 を ② で実行 — 「誰も渡さない引数」を機構ごと削除し、4 つの嘘の docstring を真にした**: 委任（「完成まで推奨で」）に従い、A-12 の推奨順（③ → ②）の **②** を実行した（③ は 2026-09-30 に完了済み）。**削除した面**: ① `feature_flags` 引数 4 箇所（`capability_catalog.list_for_llm` / `list_for_agent` / `mcp_tool_schemas` + `mcp_gateway.list_tools_for_agent`）と `list_for_llm` 本体のフィルタ ② `CapabilityManifest.requires_feature`（dataclass）と `CapabilityManifestModel.requires_feature`（pydantic — `extra="allow"` で、**スキーマ写像ピンは別モジュール `aegis_schema/models.py` を見ているので protobuf に対応物は無い**） ③ `delegate.json` の `requires_feature` キー ④ **嘘になっていた散文 5 箇所**（`AgentSettings` の docstring / `settings/models.py` / `runtime.py:102` / `runtime.py:1435` / `folder_registry.py:83`）。**① 配線は選ばなかった** — フィルタは一度も走っておらず、配線は「設定で capability を隠せる」という**新しい挙動**を製品判断なしに足すことになる。**帰結を実測してから書いた**: `agents.enabled=False` でも `ai-server.agent.delegate` は **LLM に見え続ける**が、実行すると `execution_engine.py:330` が `"agent backend is not registered"` で**失敗する**（`ai-server.agent.*` は `:302` で必ず `_execute_agent_step` に落ちる）— 新しい docstring はこの挙動を書いている。**ピンを「欠陥の記録」から「削除の記録」へ置換**（`tests/agents/test_agent_runtime.py`、同ファイル **26 → 23**、A-12 ブロック **10 → 7**）: `src/` 全体の AST 走査で引数ゼロ／**走査に被写体があること**（改名で空虚化しない）／4 入口の `inspect.signature`／両 manifest 型にフィールド無し／**出荷 manifest の全 JSON を発見**して鍵ゼロ／**識別子が `src/` に 1 文字も無い**（期待値ゼロなので**除外リストが要らない** — 手で保守する除外リストはこのリポジトリが警告している欠陥そのもの）／帰結。加えて「**鍵を書いても無効**」を固定（`requires_feature` を持つ manifest が普通にロードされ**可視のまま**になる）。**写しを 1 つ発見して直した**: `tests/test_schema_validator_stays_retired.py` の docstring が「`list_for_llm` の唯一のフィルタは `requires_feature`」と**現在形**で書いており、削除で偽になる — 論証の結論は不変で**さらに強くなる**。**触らなかった記録**: `AGENT_PROGRESS.md:1208`（日付付き P1-5 記録 `bde0bee` の内側）と、A-12 に触れている §0.1 の既存台帳行（当時の実測）。**実測**: ai-server **1777 → 1774 passed / 30 skipped（不変）**（249.60 秒、2 回とも同値）— **−3 は消したテスト関数 3 本そのもの**（`grep -c "^def test_"` が HEAD 26 / 現在 23）。egress は**派生量なので測り直した**: **233 マーカー / 210 passed / 23 skipped**（不変。`-rs` のスキップ 30 = 負債 23 + android 4 + openhands 3）。ruff は変更 8 ファイルで**変更前後とも 21 errors（同一分布）**、追加 172 行に 120 文字超 0 件 — **`ruff format` はこのリポジトリの規約ではない**。**§0.2 から A-12 を削除**（A 節は「現在、該当なし」に）、**§4.3 の生きた論証を訂正**（「走らないフィルタ」→「存在しないフィルタ」） |
| `（本節）` | **B-1① を実行 — 割り込みコスト表の中央 2 値を入れ替え、B-11 の「順序の半分」を閉じた**: 委任に従い、B-1 の推奨のうち **①（コスト表の中央 2 値を入れ替える）** を実行した。**B-11 の測定**: `personal_ai/interruption.py::_RECEPTIVITY`（P(receptive) — `interruptible > important_only > batch_later > suppress` を**降順**）と `autonomous/autonomous_loop.py::_current_interruption_cost`（InitiativeEngine のコスト軸）は**同じ梯子の単調写像**なので順序が一致すべきところ、**違反はちょうど 1 対**だった — `important_only` は `batch_later` より**受容されやすい**（0.35 vs 0.20）のに**コストが高い**（0.55 vs 0.40）。結果、`InterruptionController` は「重要なものだけ」のとき**話しかけやすく**、`InitiativeEngine` は**行動しにくい** — **同じ入力から正反対の結論**。入れ替え後は `important_only` 0.4 / `batch_later` 0.55 で、コスト表は梯子を**昇る**。**ピンを「欠陥の記録」から「契約の記録」へ再指向**（`tests/test_interruption_cost_vocabulary.py`）: 「ちょうど 1 対が食い違う」→「**コスト表が梯子を昇る**」＋**非空虚ガード**（2 表が 4 レベルを共有し、受容表が今も降順であることを**先に** assert — **空集合の一致は何も証明しない**）＋**歴史的な対を名指しする回帰検出器**（`_THE_TRANSPOSED_PAIR`）。**変異 4/4 捕捉** — うち **M1（入れ替えを戻す）は新ピン 2 本を赤にする**。一般の梯子テストでも捕まるが、**名指しの方は「どの対か」を言う**（診断もガードの一部）。原ファイルは**開始時のバイト列から復元**（sha256 一致）。**残る ②（自律的な結果の `expected_usefulness` / `interruption_cost` に実値を入れる）は「usefulness とは何か」の定義が先**なので、**B-1 の行は §0.2 に残す**（枝 ① だけ閉じた — `DELEGATION.md` §5）。**未着手のまま残した構造の非対称**: `_RECEPTIVITY` はキー集合を発見＋等式で守られているが、コスト表は裸の `.get(kind, 0.2)` のままで、**新しいレベルが `batch_later` より安く読まれる**（ピンに残した）。**実測**: ai-server **1774 → 1775 passed / 30 skipped**（**+1 = 1 テストを 2 テストに置換**、実測 359.60 秒）。egress は**派生量なので測り直した**: **233 マーカー / 210 passed / 23 skipped**（不変 — deselected が 1571 → 1572 で、増えた 1 本は非 egress） |
| `（本節）` | **B-5② の契約半分を実行 — 成長の閉路の生産者を「3 通りに壊れている」から「1 通り」へ**: 委任に従い、B-5 の枝 ② のうち **契約バグ（§3.1 穴 4 の ②③）だけ**を直した（① 配線は A-11③ の決定どおり触らない）。**読者側を先に実測してから直した** — 登録簿は読者を「`structured_data["decision"] == "rejected"` で絞り、両方とも `related_desire=` で検索する」と書いていたが、**その通りだった**（`autonomous_loop.py:1365`・`motivation_arbiter.py:171`）。**ただし登録簿に無かった事実が 2 つ**: ① ループ側の読者 `_recent_failure_penalty` は **`source_desire` が空なら即 `return 0.0`** するので、`related_desire` 欠落は**その読者では常に致命**（arbiter 側は「空なら絞らない」ので `decision` 欠落だけが致命）。② 生産者のガードは `status`、読者の述語は `decision` — **キー名が違うので `status` をコピーしても直らない**。**修正**: 生産者に `related_desire=source_desire` と `structured_data={"decision": _DECISION_REJECTED}` を追加し、**`_DECISION_REJECTED` をモジュール定数 1 つに**（`_OUTCOME_REJECTED` とは**別名にした** — 綴りが同じだけで、outcome 語彙と decision 語彙は別のリストで、片方の改名が他方を黙って動かすのを避ける）。**ピンを「不一致の記録」から「契約の記録」へ再指向**（`tests/test_forced_gate_stays_retired.py`、`_omits_`→`_writes_`）: 旧ピンは `"related_desire" not in producer_keywords` と `"structured_data" not in producer_keywords` を assert していた（＝**欠陥を固定**していた）ので、両方を `in` に反転し、**end-to-end ピン**を追加 — 実物の `ReflectionEngine.reflect` → 実物の store → **実物の読者 2 つ**（`MotivationArbiter._check_memory_penalties` / `AutonomousLoop._recent_failure_penalty`、後者は `MemoryManager(memory_store=…)` を注入して到達）を走らせ、**両方が 0.2 を課す**ことを assert。負の対照（**別の欲求では 0 件・0.0**、`approved` では記録が作られない）付き — **引数を無視する読者でも通ってしまう形にしない**ため。**変異 4/4 捕捉**: M1 鍵 2 つ落とす→2 本赤 / M2 **値だけ** `"rejected"`→`"denied"`→**end-to-end ピン 1 本だけ赤**（構造ピンは「同じ鍵名がある」ことしか見ないので**原理的に見えない** — これが end-to-end を足した理由そのもの）/ M3 `related_desire` だけ落とす→2 本赤 / M4 `structured_data` だけ落とす→2 本赤。原ファイルは**開始時に捕捉したバイト列から復元**（sha256 一致）。**写しの掃除**: 同ファイルの節コメントが「**生産者と消費者は記録の形について不一致**」と現在形で書いており修正で偽になるので訂正（型 6）。**実測**: ai-server **1775 → 1776 passed / 30 skipped**（総数 1805 → 1806 = **+1 は追加したテスト関数 1 本そのもの**、`grep -c "^def test_"` が 23 → 24。実測 304.06 秒）。egress は派生量なので測り直した: **233 マーカー / 210 passed / 23 skipped / deselected 1573**（不変）。**この過程でテスト数の写しが 3 つ腐っていたのを発見**（§0 要約行・§1.1 表・`AGENTS.md` が 1777 のまま。正しくは 1775）— 3 写しを 1776 に揃え、§1.1 の脚注に 3 度目の再発として記録した。**§3.1 穴 4 を「未着手」から「契約半分は解消 / ① は未着手」へ更新** |
| `（本節）` | **B-4 を ② で閉じ、その根拠にあった「名前の衝突」を直した**: 委任に従い B-4 を **②（移植しない）** で閉じた。**まず現状が既に ② であることを実測した** — `NotificationFilter` / `contains_password_field` / OTP 規則 `(?<!\d)\d{4,8}(?!\d)` は**すべて文書にのみ**残り、`ai-server/src` と `ai-server/tests` には **0 件**（`git grep`）。つまり**コードの変更は無い**（`DELEGATION.md` §2 の「戻し方: なし」どおり）。**ただし閉じる過程で、この決定の根拠にしていた記述が読者に判別できないことが分かった**: 根拠は「`REDACTION_PATTERNS` の OTP 規則が『確認コードを読み上げて』を壊す」だが、**`REDACTION_PATTERNS` は同名が 2 つある** — ① **削除されたモジュールの中**のもの（OTP 規則**あり**。`NotificationFilter` が ingest で使っていた）と、② **生きた** `ai-server/src/aegis_ai/llm/redaction.py:18` のもの（**8 パターン**、OTP 規則は**無い**）。§5.1 の文はどちらを指すか書いておらず、`REDACTION_PATTERNS` で grep すると**live な方（OTP 規則なし）**が出るので、**「live に 4〜8 桁を潰す規則がある」と誤読できる**（**型 6**）。実測 `git grep 'd{4,8}' -- ai-server/src ai-server/tests` = **0 件**。§5.1 の 2 箇所に「**名前の衝突**」とどちらを指すのかを明記した。**コードは不変・テスト数も不変**（1776 / 30）。**§0.2 から B-4 を削除**（閉じた 7 行目） |
| `（本節）` | **B-6 の前提を実測で反証した（行は閉じずに残した）**: 登録簿は「未読集合全体に 1 つの一貫した枝（削除 or 配線）を選ぶ」としていた。**23 件を実測したところ同質でなかった** — **群 A（対象の機能が既に無い）= 1 件だけ**（`research_watch_enabled`。`research/` は P1-5 で削除済み）、**群 B（機能は在るのにスイッチが未配線）= 21 件**（`reflection/`・`memory/semantic.py`・`semantic_memory.py`・`procedural.py`・`briefing/`・`social/`・`intake/`・`agents/` の存在を確認した）、**群 C（害の実例）= 1 件**（`sensitive_data_storage_enabled`）。**配線は「挙動が変わる」変更**なので、集合に 1 つの枝を選ぶのは**新しい判断の発明**にあたる。委任の原則（推奨列＝保守側の枝を実行するだけ）では、**枝を選ぶこと自体が発明になる行は閉じられない** — よって **§0.2 に行を残したまま**、`DELEGATION.md` §2 の当該行を**撤回**し、§4 に**項目 11** として登録した。**この行は §0.2 が空にならない理由の 1 つ**。**教訓**: 「同じ形の未読フィールド」は同じ形ではない — **未読である理由**を数えずに「集合」と呼ぶと、集合への 1 つの判断が**個別の判断 21 個をすり替える**。**副産物**: `B-6` という ID が本文書内で 2 つの意味を持つ（§0.2 の設定行 / §4.3 の git ref 消失バグクラス）— 型 9 の変種。振り直しは影響が大きいので**記録のみ** |
| `（本節）` | **C-3 と C-5 を閉じた（「決めることが無かった」行）— そして `MEMORY.md` 自身の誤りを訂正**: どちらの行も**枝は既に決まっており**（C-3 = 正典は §4.3、C-5 = テストゲートは手動のまま）、**残った問いは `DELEGATION.md` §4 の項目 6・7 に既に移してあった**ので、**§0.2 の行だけが二重**だった — 行を削除した（コードも文書の中身も不変）。**C-3 の実測**: §4.3 に **17 クラス**、skill `aegis-pin-a-dead-surface` の見出しが「**正典は §4.3**、食い違えば §4.3 が勝つ、この一覧は直す側」と**明記済み**だった。**副産物**: `MEMORY.md` の当該行が**逆向き**（「names and glosses live in ONE place — **skill**」）と書いていたが、**§4.3 が 17 件の名前と gloss を両方持ち**、skill は圧縮語彙で、**skill 自身が §4.3 を正典と名乗っている**。つまり `MEMORY.md` は**3 つ目の成果物として配置を誤って説明**していた（次のセッションを**派生側**へ送り、それを**源**と呼ぶ）— 訂正した。**教訓**: **所有の主張も事実であり、数を数えても検査にならない**（17 という数は合っていた）。**§0.2 の残りは 6 行**（B-1②・B-5①・B-6、C-1・C-2・C-4）— いずれもオーナーの判断が要る |
| `（本節）` | **Android のコンパイル検証を実施 — そして C-4 の前提は「書かれた時点で既に偽」だった**: 委任に従い C-4 の導入決定を実行し、`:app:compileDebugKotlin` が走り `:app:assembleDebug` が `app-debug.apk`（**21,024,388 bytes**、sha256 `6c5d0eda…`）を生成することを実測した（`--offline`、依存キャッシュ温で compile 約 76 秒 / assemble 約 27 秒）。**実機は対象外のまま**（`adb devices` は空）。**測定中に、C-4 行そのものが誤りだったと判明** — 行は「`java`/`javac`/`adb`/`gradle`/`kotlinc` すべて不在、**待っても直らない環境の不在**」と書くが、JDK 17 は **2026-08-19**、Android SDK は **2026-09-25** にディスクへ入っており、**`BUG_REPORT.md` の「android-server: 実ビルドで §36 を検証」節がその導入と `BUILD SUCCESSFUL`（21m52s）を既に記録していた**（`ebe1506`、2026-09-29）。C-4 行は **2026-09-30 14:17（`bc6e870`）** なので、**偽だったのは「当時」ではなく「書いた時点」**で、反証は**同じリポジトリの中に既にあった**。原因は**測定のスコープ** — `command -v java` は `PATH` しか見ないので、**ディスクにあるツールを「不在」と報告する**（A-12 の「リテラルが無い＝読者がいない」と同じ罠を、今度は環境で踏んだ）。**掃討**: `AGENTS.md`・`docs/status.md`・`DECISION_DRAFTS.md`・`DELEGATION.md` を実測に置換し、履歴文書（`IMPROVEMENT_PROPOSAL.md`・`PHASE5B_RULE_PROPOSAL.md`・`BUG_REPORT.md`）には**日付入りの追記**を足した（本文は書き換えない）。**ピンは足していない** — C-4 が提案していた「『検証済み』と書かれたら落とすピン」は**散文スキャナ**で、**この節自身が「検証済み」を含むので除外リストが要る**（手で保守する除外リストはこのリポジトリが警告している欠陥そのもの）。代わりに **§4.3 クラス 6 に鏡像の変種を追記**（「在る」と読める文書だけでなく「**無い**」と読める文書も測る）。**コードは不変**。ただし**テスト数はこの間のコミットで動いていた** — 実測 **1776 → 1891 passed / 30 skipped**、egress マーカー **233 → 325**（新規 3 ファイルで **72 件** = 音声 30 / メッセージング 24 / cross-device 18。**残りは既存ファイル側**で、内訳は測っていない）。live な写し 3 つ（§0 要約行・§1.1 表・`AGENTS.md`）と skill §1 を実測値に揃えた |
| `（本節）` | **B-5① の「1 手（配線）」を実測したら 1 手ではなかった — 確認を欲求に結びつける機構が無い**: §3.1 穴 4 と `DELEGATION.md` §4 項目 9 は「`reflect()` に呼び出し元を配線する（**1 手**）」としていたので、配線先を測った。**① 読者はどちらも `related_desire=source_desire` で引く**（`autonomous_loop.py:1589`・`motivation_arbiter.py:162`）ので、`related_desire` が入らなければ**記録は作られても誰も読まない**（ループ側の読者は `:1583` で `source_desire` が空なら即 `return 0.0`）。**② `related_desire` に入るのは `reflect()` の呼び出し元が渡す `source_desire` だけ**で、唯一の呼び出し元（`autonomous_loop.py:1228`）は**失敗したタスクの `desire`** を渡す。**③ `ConfirmationRequest` は欲求を持たない**（`confirmation/models.py` — `summary`/`reason`/`capability_id`/`task_id`/… はあるが `desire` は無い）。**④ 解決済みの確認を欲求に結びつける機構が無い** — `_decide`（`web/routes/approval.py`）は `store.reject()` を呼んで記録を返すだけ、実行経路で store に触る唯一の場所 `_confirmation()` は `request`/`list` のみ、**ループは store を 1 度も参照しない**（`autonomous_loop.py` に `confirmation` の出現 **0 件**）。→ **そのまま配線すると、拒否された確認が「無関係なタスクの欲求」への罰則になる**（誤帰属）。**正しく配線するには「確認 ↔ 欲求」のリンクを先に決める必要がある**（案: 確認に欲求を記録させる／`task_id` で照合する — どちらも契約と挙動を変える**製品判断**）。つまり**推奨列の「1 手」は誤りで、実際はリンクの定義を含む製品判断**だった。**コードは不変**（§3.1 穴 4 と `DELEGATION.md` §3/§4 を実測に訂正） |
| `（本節）` | **B-6 を「削除」で実行 — 未読 23 フィールドのうち 22 を削除し、ピン留めされた安全既定値 1 件を残した**: オーナー決定（削除）に従ったが、**実行前に測って範囲を変えた**。23 件は**同質ではなかった** — **22 件は純粋な負債**（`src/` 全体で読者ゼロ。定義モジュール以外に出現 0）だが、**1 件 `voice.push_to_talk_only` はピン留めされた安全既定値**で、削除すると `test_ineffective_flags.py` の `_INTENTIONALLY_UNREAD` が指す対象そのものが消える。よって**22 件を削除し `push_to_talk_only` を残した**（当初指示の「23 件削除」は**そのままでは実行できない**——集合が 1 つの枝を選べる形をしていなかった。これは §0.1 の B-6 反証行と同じ型の再発）。**削除した面**: `settings/models.py` の **5 セクション 22 フィールド**（`AutonomousSettings` 10 / `AgentSettings` 2 / `IntakeSettings` 4 / `MemorySettings` 4 / `ServerSettings` 2）、`config/settings.json` の対応 22 鍵、`web-ui/src/pages/Settings.tsx` の `preferred` から `self_dev_proposal_enabled`、`_UNOWNED_DEBT`（**空にした**——これが削除の目的そのもの）、`docs/beta-runbook.md` の 2 行。**`IntakeSettings` の docstring は偽だった** — `intake.classifier_profile` を引用していたが、生きた経路は `L1Router`/`L1Executor`（`runtime.py:1033` で構築、設定を受け取らない）で、そのフィールドは**一度も読まれていなかった**。**新ピン** `tests/test_settings_debt_stays_retired.py`（4 テスト）: `src/` 全体の**識別子単位**走査（`ast` 非依存）で 22 名の残存ゼロ、**陽性対照**（`push_to_talk_only` と `episodic_retention_days` を走査が見つけられること——不在表明は走査が壊れると空虚に真になる）、モデル側の独立検出器、出荷 config に鍵ゼロ。`test_settings_ui_matches_the_schema.py` は**記録テストを不変条件に置換**（`rendered & unread == set()` + 非空虚ガード。旧 `_RECORDED_DEAD_CONTROLS` は削除）。`_RECORDED_ENFORCED` 27 → **15**（日付付き B-20 実測の 27 はそのまま保存）。被覆床 90 → **70**（実測 72）。**挙動が変わった 2 点（「挙動に寄与しないので削除は挙動を保存する」は*ほぼ*真だが完全ではない）**: ① **書き込み経路が鍵を拒否するようになった**（`SettingsStore.update_section` が `Unknown field '{key}'` を返す——A-9/B-20 の修正で `AEGISSettings.model_validate` を通すため）② **設定画面にコントロールが出なくなった**（B-21 の死んだ 10 コントロールの一部が消えた）。**実測**: ai-server **1891 → 1885 passed / 30 → 8 skipped**（実測 324.58 秒）。**内訳は厳密**: スキップの **−22 は削除したフィールドそのもの**、通過の **−6 = 新ピン +4 − 削除されたパラメータ化ケース 10**。egress は派生量なので測り直した: **325 → 303 マーカー / 302 passed / 1 skipped / deselected 1590**。**掃討中に 2 つの腐った数値を実測で発見**: ① `AGENTS.md` の「**93 fields across 11 models**」は**古かった**——A-12 の台帳行の 93 は**当時は正しく**（`273f0c1` で実測 93）、`ad9d32f`（メッセージング）が 94 に上げたのに `AGENTS.md` が追随していなかった。**live な主張は 1 ずれ**（正: 94 → 72 = 削除 22）。② **egress 変異チェックの失敗数は 62 でも 38 でもなく 74**（`scripts/verify_egress_tests_catch_regression.py` 実測: 非変異 302 passed / 1 skipped、変異 **74 failed / 228 passed / 1 skipped**）——`AGENTS.md` の 62 と skill の 38 は**どちらも古い**。両方を実測値に置換。**副産物（B-6 の範囲外なので残置）**: `config/settings.json` の `"autonomy"` ブロックは P1-3 の `AutonomyProfile` 残骸で、**どのモデルにも対応しない**（**2026-10-01 に削除 — 次項の台帳行**）。**§0.2 は空のまま**（B-6 は決定済み） |

| （本節） | **B-5① を実行 — 確認を欲求に結びつけ、成長の閉路を閉じた（オーナーが (A) を選択）**: 2026-09-30 の実測が「1 手ではない」と示した（読者 2 つは `related_desire=source_desire` で引くのに `ConfirmationRequest` は欲求を持たない）ので、**リンクの定義を先に**行った。**実装**: ① `ConfirmationRequest.desire`（`confirmation/models.py`、既定 `""`。**LLM 供給＝不信**なので「値は素通しで運び、**読者が照合する**」と docstring に明記）② `_CONFIRMATION_FIELDS` に `desire` を追加（**設定画面が描画しない唯一のフィールド**である旨をコメント）③ `AutonomousLoop` が `confirmation_store` を受け取り（`runtime.py:1589` の `_create_autonomous_loop` が `runtime.confirmation_store` を渡す）、**読み取り専用**で `all(limit=200)` を引き、`REJECTED` のみを `desire` ごとにまとめて `reflect(approval_decisions=…, source_desire=<desire>)` に渡す ④ **実在する欲求集合**（`self._desire.get_all_desires()`）と照合し、**空・未知は捨てる**（誤帰属より欠落を選ぶ）⑤ `_reflected_approval_ids` を state に永続化（無いと `0.2 × 件数` が上限 0.9 に張り付く）。**ピン 4 本**を `tests/test_forced_gate_stays_retired.py` に追加（実 desire は**両読者**に届く／未知・空の desire は教訓を作らない／同じ拒否は 1 回だけ／**ループは store を読むだけで答えない**（AST で `called ⊆ {all, get, pending, pending_count}`））。`_ALLOWED_IMPORTERS` に `autonomous_loop.py` を追加（**ピンが新 import を検出して落ちた＝設計どおり**）。**変異 4/4 捕捉**（各変異が**狙った assertion** を発火させたことまで確認）、原ファイルは sha256 一致で復元。**実測**: ピン **47 → 51 passed**、ai-server **1885 → 1889 passed / 8 skipped**（**+4 = 新ピンそのもの**、実測 326.65 秒）。egress は**派生量なので測り直した**: **303 マーカー / 302 passed / 1 skipped / deselected 1590 → 1594**（不変 — 新 4 本は非 egress）。**副産物（重い）**: 配線時に**自分でバグを入れた** — `_create_autonomous_loop` は `_build_runtime` と**別関数**で `confirmation_store` はそこに無い。**全スイートは緑のまま通った**（`autonomous_loop_enabled` が既定 `False` で、この関数はテストから一度も実行されない）。**ruff の `F821` だけが捉えたが、CI は ruff を走らせていない** → §4 の項目 7（C-5）。**残る穴は §3.1 の 3 のみ**（① は閉じた） |

| （本節） | **出荷 `config/settings.json` の死んだ `autonomy` ブロックを削除し、一般形のピンを追加した — 検出器がモデルしか見ていなかった**: B-6 の副産物として「範囲外」に残していた残骸を、B-6 の完了後に片付けた。**実測**: 出荷 config の全鍵をモデルに対して歩くと、未宣言は**ちょうど 1 つ** — `autonomy`（**11 鍵すべてがどのモデルにも未宣言**）。**読者がいないことを確認**（`git grep`: 他の `autonomy` 出現は無関係 — `user_model.autonomy_level`・`web/resource_routes._autonomy`・欲求名）。**このブロックは無害ではなかった** — `external_send_requires_approval` / `payment_requires_approval` / `publish_requires_approval` を綴っていたので、**出荷ファイルが「これらのゲートが設定されている」ように読めた**。Pydantic は余剰鍵を無視するので、設定しても**効かず、失敗もしない** — 症状は「読者が統制の存在を信じる」ことだけ（型 6）。**気づいた経緯が型の実例**: `docs/adr/permissive-autonomy-policy.md` は **2026-09-28 に「`autonomy` settings 節は削除された」と書いており**、**モデルについては正しい**（P1-3）が、**出荷 config のブロックは残っていた** — つまり ADR の主張は*書いた時点で既に*半分偽で、**検出器（`test_ineffective_flags.py`）がモデルしか見ていなかった**ので 2 日間誰も気づかなかった。**削除は挙動を保存する**（`extra="ignore"` + 読者ゼロ。`AEGISSettings.model_validate` は削除後も通る）。**新ピン** `test_every_shipped_key_is_a_live_settings_field`（`tests/test_settings_debt_stays_retired.py`）: 出荷 config を `AEGISSettings` に対して歩き、**注釈が settings モデルであるフィールドにだけ再帰**する（`capabilities.per_capability` は `dict[str, CapabilityPermission]` で**利用者が選ぶ鍵**なので判定しない）。**非空虚ガードは数ではなく構造** — 歩きが**全トップレベル節を訪れ**、かつ**サブモデルへ降りた**ことを assert する（数を書くと config の大きさが変わったとき腐る）。**このピンの docstring は元から「carry する全鍵が live でなければならない」と主張していた**のに、22 の**名前**に対してしか assert していなかった — ピンが docstring を真にした。**変異 2/2 捕捉**（**狙った assertion** が発火したことを確認）: M1（死んだ鍵を戻す）→ 未宣言の指摘が発火し `autonomy` を名指し／M2（歩きを盲目化）→ 非空虚ガードが発火。原ファイルは sha256 一致で復元。**実測**: ai-server **1889 → 1890 passed / 8 skipped**（320.40 秒）。egress は派生量なので測り直した: **303 マーカー / 302 passed / 1 skipped / deselected 1594 → 1595**（新 1 本は非 egress） |
| （本節） | **音声ゲートの「死んだ検査」4 本を記録した — 検出器の読者定義の 2 つ目の盲点**: `voice/gate.py` の docstring が「No always-listening」「No audio storage by default」を**安全特性**として並べているので、それを施行するはずのメソッドを測った。**実測**: `VoiceGate` の公開検査 7 本のうち `is_audio_recording_allowed` / `is_wake_word_enabled` が **`src/` から呼ばれていない**（`VoiceGate(...).x()` と gate.py 内の `self.x()` を AST で走査。非空虚ガードは `check_voice_input` / `check_voice_output` が見つかること）。**同じ測定を `VoicePrivacy` にも広げたら 4 本に増えた** — `should_store_audio` / `is_external_api_allowed` も未呼び出しで、**生きたのは `redact_sensitive_text` だけ**（`integrations/stt_service.py:76`）。**帰結**: 4 本は 3 設定の**唯一の読者**なので、`voice.record_audio`・`voice.voice_data_retention_hours`・`voice.wake_word_enabled` は**生きた読者を持たない**。**なのに `test_ineffective_flags.py` は 3 つとも「読まれている」と報告する** — 識別子が `src/` に現れるかを数える検出器なので、**死んだコードの中の読者も読者として数える**（B-13「検証器だけの読者は未読として数える」の**鏡像**。§4.3 クラス 7 に 2 つ目の機構として追記した）。**記録であって配線ではない**（意図的）: どちらのフラグも**存在しない機能**を gate している（音声保存の経路も wake-word の経路も無い — `docs/voice-io.md`）ので、配線は機能の実装になる。**ピン 3 本**（`tests/test_voice_io.py`）: ① `VoiceGate` の未到達検査 == 2 本 ② `VoicePrivacy` の未到達検査 == 2 本 ③ 3 設定の**読者が死んだ検査だけ**であること — **ファイル単位ではなく「囲む関数」単位**で assert する（同じファイルの生きたメソッドに読者が足されても鳴るように。ファイル単位の走査はこれを見逃す）。**陽性対照**は `voice_enabled`（生きた `is_voice_enabled` から読まれる）— 走査が「生きた読者」と「死んだ読者」を区別できることを示す。**変異 3/3 捕捉**（各変異が**狙った assertion** を発火させたことまで確認）: M1 死んだ `VoiceGate` 検査に呼び出しを足す／M2 死んだ `VoicePrivacy` 検査に呼び出しを足す／M3 **生きた `is_voice_enabled` に `wake_word_enabled` の読みを足す**（＝現実の故障モード）。原ファイルは**開始時に捕捉したバイト列から復元**（sha256 一致）。**散文も掃討した**: `voice/gate.py` と `voice/privacy.py` の docstring、`docs/voice-io.md` の Status・Safety・Next Steps・Wake Word 表 — いずれも「施行されている」と読める書き方だったので、**施行済み / 真だが未施行**を明示した（型 6）。**実測**: ai-server **1890 → 1893 passed / 8 skipped**（**+3 = 新ピン**、実測 342.68 秒）。egress は派生量なので測り直した: **303 → 306 マーカー / 302 → 305 passed / 1 skipped / deselected 1595**（`test_voice_io.py` はモジュール全体が egress マーカーなので +3 が載る）。**§0.2 は空のまま**（これはオーナー判断ではなく記録） |
| （本節） | **承認の監査 API（`log_approval`）が未配線であることを記録した — 4 つ目の承認時代の面**: §3.1 の副産物として「設計済みで繋がれていない」と書かれていたまま誰も測定していなかった面を測った。**実測**: `log_approval` は**定義 3 つ**（`audit.py`・`audit/audit_log.py`・`audit/audit_manager.py`）で、**自分の転送連鎖の外に呼び出し元が 1 つも無い**（`AuditManager.log_approval` → `AuditLog.log_approval` の転送だけ。動的ディスパッチは無い — `getattr` は `publish_event` 用のみ）。**帰結**: `AuditEntry.source_desire` を書くのは**その死んだ本体 2 つだけ**なので、**本番が作れる全監査レコードで `source_desire == ""`** — `audit.py` の `if entry.source_desire:` 分岐と SQLite の同名カラムは**常に空**である。**「監査イベントは原因の欲求に紐づく」と読めるカラムが、一度も紐づけない**（型 6）。**ピン 2 本**（`tests/test_forced_gate_stays_retired.py`、4 つ目の面として）: ① `log_approval` の呼び出し元集合 == `{"log_approval"}`（**囲む関数で数える** — 呼び出し*箇所*を数えると転送が生きた呼び出し元に見える）② `AuditEntry` 構築で `source_desire=` を渡す関数集合 == `{"log_approval"}`（**`AuditEntry` 構築に限定** — `source_desire=` は `ContinuationManager.create` やタスクモデルにも渡っており、素のキーワード走査では生きた書き手を拾って何も証明しない）。**陽性対照**は兄弟 API の `log_decision`（生きた呼び出し元が約 30）と `decision=`（生きた `AuditEntry` 構築が渡す）。**変異 2/2 捕捉**（狙った assertion が発火）、原ファイルは sha256 一致で復元。**削除ではなく記録を選んだ**（意図的）: 削除は**永続化された監査カラム**と **2 つの `AuditEntry` データクラス**に波及するので、純粋なコード整理ではなく**データ面の変更**である。`IMPROVEMENT_PROPOSAL.md` は既に削除を勧めており、`DELEGATION.md` §4 項目 13 として起票した。**実測**: ai-server **1893 → 1895 passed / 8 skipped**（**+2 = 新ピン**、実測 332.29 秒）。egress は派生量なので測り直した: **306 マーカー / 305 passed / 1 skipped / deselected 1595 → 1597**（新 2 本は非 egress） |

| （本節） | **`aegis_ai/security/` パッケージ全体が未配線であることを記録した — 「宣言されているが効いていない」をパッケージ規模で**: `docs/security.md` が 6 クラス（`LocalTokenAuth`・`TokenStore`・`CSRFProtection`・`RateLimiter`・`OriginChecker`・`TLSConfig`）を**使用例つきで**解説しているので、それぞれの到達性を測った。**実測**: `ai-server/src`・`ai-server/tests` と全兄弟サーバ（pc / browser / room / android / SDK / scripts / web-ui）の **596 ファイル**を AST 走査すると、`aegis_ai.security` を import するのは **`security/__init__.py` 自身だけ**（14 ヒットすべて自己参照）。**6 クラス名もパッケージ外で一度も参照されない**。**生きた認証系は `aegis_ai/auth/`**（パスキー＋独自 `csrf.py`、`web/auth.py` が `install_passkey_auth` で設置）なので、これは**欠落ではなく置換済み**である。**TLS は特に**: `add_secure_port` を呼ぶのは**誰も import しない `tls_config.configure_server` だけ**で、`grpc_server.serve` と room-server は `add_insecure_port` — **gRPC は平文**（`docs/architecture.md` の「TLS available for gRPC」は偽だった）。**`TLSConfig` は 2 つ**あり API が非互換で、`__init__.py` が再輸出するのは `tls.py` の方だけ。**ピン 5 本**（`tests/test_security_package_stays_unwired.py`）: ① パッケージ外に import 者ゼロ ② 6 クラス名がパッケージ外で未参照 ③ `TLSConfig` が 2 クラス存在することの記録 ④ `ssl_server_credentials` の構築元 == 死んだ 2 関数 ⑤ `add_secure_port` の呼び出し元 == `configure_server` のみ。**陽性対照は 2 つ**（生きた `aegis_ai.auth` は import されており、`PasskeyService` はパッケージ外で参照される／生きたサーバは `add_insecure_port` を呼ぶ）。**変異 3/3 捕捉**（import を足す／クラス名を使う／`add_insecure_port` を `add_secure_port` に変える — 各変異が**狙った assertion** を発火）、原ファイルは**開始時に捕捉したバイト列から復元**（sha256 一致）。**散文も掃討した**: `docs/security.md` を実測に書き換え、`docs/architecture.md` §7.4 の「TLS available」を訂正、`docs/status.md`・`docs/risk-register.md` を「統合未完」から「未配線」へ、`BUG_REPORT.md` §1/§8 の「✅ 修正」が**死んだモジュールに入っている**旨の追記、そして `security/` の **8 ファイル全部**の docstring に UNWIRED バナーを追加した（型 6 の掃討）。**記録であって配線でも削除でもない**（意図的）: 配線は生きた `auth/` と**二重の認証実装**を作り、削除は文書化されたパッケージ全体の話でオーナー判断。`DELEGATION.md` §4 項目 14 として起票。**実測**: ai-server **1895 → 1900 passed / 8 skipped**（**+5 = 新ピン**、実測 362.80 秒）。egress は派生量なので測り直した: **306 マーカー / 305 passed / 1 skipped / deselected 1597 → 1602**（新 5 本は非 egress） |
| `（本節）` | **出荷 manifest の 1 件だけが機械固有の絶対パスを名乗っていた — 値は不活性だが、潜在故障（型 1 の裏面、記録のみ）**: `apps/builtin/pc-server/screenshot/get_screenshot/executor.json` の `command` が `C:\Users\kohak\...\ai-server\.venv\Scripts\python.exe executor.py` で、**command 型 7 件のうち絶対パスを名乗るのはこれ 1 件だけ**（他 6 件は `python executor.py`）。しかもそのパスは**この機械に存在しない**（venv はリポジトリ直下で `ai-server/.venv` は無い — `Path(named).exists() == False` を実測）。**壊れていない理由を実測で特定した**: `ExecutorRegistry._normalize_command` が `executor.py` を含む command を `sys.executable` + 絶対パスへ**置換する**ので、値は**装飾**。ただし**不活性 ≠ 無害** — 正規化は `executor.py` が隣にある間だけ効き、**フォールバックは `return command`** なので、スクリプトが消えれば絶対パスが実行される。**ピン 3 本**（`tests/test_executor_commands_stay_portable.py`）: ① **不活性を実関数で**検証（正規化結果が入力と一致する command があれば赤 = 「装飾でなくなった」警報 — 条件を復唱せず関数を呼ぶ）② 先頭トークンの集合を**等式**で固定（`{"python"}`。除外リスト無し、floor ではなく等式なので新しい綴りも既存の消滅も捕まる）③ **フォールバックを固定**（`executor.py` の無いディレクトリでは command がそのまま返る = リスクが仮定でなく実在する）。**変異 4/4 捕捉** — 各変異が*狙った* assertion を発火させたことまで確認（M1 **実測した元の値に戻す**→等式が発火。**先に再構成バイト列の sha256 が記録した `4f2b79ab…` と一致することを確認**／M2 `py executor.py`→等式／M3 `executor.py` を含まない command 型 manifest を足す→①／M4 `exists()` ガードを外す→③）。原ファイル 2 本は**開始時に捕捉したバイト列から復元**（sha256 一致）。**掃討**: リポジトリ全体で `C:\Users\kohak` を探したが出荷 artefact はこれ 1 件だけ（他は文書の「対象」・テストの例示・`.gitignore` 済みの `local.properties` / `*.log` / `build/`）。**副産物 2 件**: ① **`\s*` が改行を飲む**ため M4 の最初のアンカーが 1 行長く削り、**コンパイルできない変異**を作った — pytest は rc=2 で `FAILED` を出さないので**「捕捉できなかった」と誤読する**（ハーネスに構文検査を足した）② **`docs/architecture.md` が同じ数を 2 箇所（`:11` と `:408`）に持ち、1900 のまま古かった** — 前回の掃討が漏らしていた（「訂正したら*全ての*写しを掃く」の再発）。本行で 1902 → **1905** に掃討（`AGENTS.md`・§1.1・`:11`・`:408`。`:12` の capability 数は pc 58 / ai 32 / android 17 / browser 16 / room 5 = 128 を**測り直して一致**）。**`DELEGATION.md` §4 項目 16**（`command` フィールドを残すか）。**実測**: ai-server **1902 → 1905 passed / 8 skipped**（**+3 = 新ピンそのもの**、392.57 秒）。egress は派生量なので測り直した: **306 マーカー / 305 passed / 1 skipped / deselected 1604 → 1607**（新 3 本は非 egress）。**ruff F821 は変更後も 0 件** |
| （本節） | **Docker 面の配線を固定し、dev-server の残存を実測して生きた写しだけを修正した — 穴は検出器の走査対象ではなく「掃討の一覧」だった**: compose↔Dockerfile の配線を誰も検査していなかったのでピンを追加した（`docker-compose.yml` が指す 3 件は実在、未参照は 3 件で、うち `infra/docker/pc-server.Dockerfile` はヘッダが「プレースホルダ」と明記する意図的な 1 件 → **等値**で固定）。実測で **2 件の未参照 Dockerfile が本番経路と乖離**していた（`ai-server/Dockerfile` は web-ui ビルド段も HEALTHCHECK も無く `aegis_ai.main` を起動し `pip install -e ".[dev]"`／`browser-server/Dockerfile` は apt `chromium` + `DISPLAY=:99` でインストール失敗を `\|\| true` で握り潰す）。さらに `BUG_REPORT.md` §9 の残骸表が **5 行すべて反証** — 掃討は 4 ファイルで止まり、**README からリンクされる正典 `docs/docker-services.md` と 2 つの起動スクリプトが漏れていた**（両スクリプトは `docker compose build/up ... dev-server` を実行していて**必ず失敗した**）。§28 は記録が指すファイル名と実際に修正したファイルが食い違っていた（修正は `infra/docker/ai-server.Dockerfile`、`ai-server/Dockerfile` は今も `-e ".[dev]"`）。**削除はしない**（オーナー項目、`DELEGATION.md` §4 項目 17） | 変異 **6/6** 捕捉（各変異が**狙った assertion** を発火させたことまで確認。**M5 は当初 MISS** — 元の欠陥が**大文字小文字を無視する glob** だったので、素朴な `in` 版は被対象を動かしていなかった）、原ファイルは**開始時に捕捉したバイト列から復元**（sha256 一致）。ピン 2 本（`tests/test_dockerfiles_are_owned.py`。非空虚ガードは参照 `>= 3` / ファイル `>= 4`、未参照集合は**等値**）。ai-server **1905 → 1907 passed / 8 skipped**（**+2 = 新ピン**、実測 414.60 秒、collected 1913 → 1915）。egress 不変（306 マーカー / 305 passed / 1 skipped、deselected 1602 → 1609） |
| （本節） | **視覚の「実質不可」は誤りだった — ドラフトの推奨をそのまま実行したら、嘘を公開するところだった**: `DECISION_DRAFTS.md` §C の vision 行は「**UI/文書で『視覚機能は無効』と明示**する」を推奨していたが、**着手前の測定で前提が崩れた**。`ai-server/config/llm.yaml` は `mode: local` で、`profiles.local_vision` は**コメントアウトされておらず**（`http://localhost:11434/v1`、Ollama `qwen2.5vl:7b`）、`LLMSettingsResolver._LOCAL_PROFILE_MAP` が `vision_observation → local_vision` に remap する。resolver を直接駆動した実測: `resolve("vision_observation")` → `qwen2.5vl:7b @ localhost:11434`。AEGIS 自身の `verify_egress_configuration` も **`local_llm_readiness: ok` / 違反ゼロ**で、**egress は視覚を止めていない**。よって §3.2 の ❌（「`llm.yaml` が Aliyun を指したまま／egress が止めるため**視覚機能は実質不可**」）は**機制・結論とも誤り**であり、そこに「視覚機能は無効」と書けば**システム自身の判定と矛盾する嘘**になる → **取り下げ**、§3.2 を ✅ に訂正（Aliyun 定義は **cloud 用で local モードでは使われない**）。**生きた写し 6 つ**（§3.2 / `DECISION_DRAFTS.md` §C / `IMPROVEMENT_PROPOSAL.md` §9.5 項目 3 / **`DELEGATION.md` §1 条件 3・§3 表** / **`IMPROVEMENT_PROPOSAL.md` §9.7 リスク表**）を掃討し、**日付付き記録 `PROGRESS_2026-09-29.md` は不変**として触らない。**最初の掃討は 3 つで止まり、3 つ漏れていた** — 同日 13 度目の掃討で判明（**走査語を「vision」に限ったため、`DELEGATION.md` の 2 箇所は「vision ローカル代替」として、`§9.7` は「**視覚**の欠落」として現れた**。「掃討の被覆そのものが主張であり、**走査語の集合も**主張である」の再発）。`docs/egress-gate.md` の「vision has no local profile」は**検査器の条件の記述**であって状態の主張ではないので**測って正しいことを確認して据え置いた**（`egress/startup.py:59-76`）。**ピンは散文走査にしなかった** — 訂正後の行は**反証した文言を引用している**ので、禁止語走査は**訂正そのものに落ちる**（除外リストが欠陥になる型）。代わりに**行の判定マーカーを resolver の解決先に結びつけた**（ローカル解決なら ✅／外部解決なら ❌ を要求 = **両方向に落ちる**）。**副産物**: 同日、Room の `GetEnvironment` が**ハードコード fixture を「ok」と称していた**ので `Status.message` で fixture と明示した（`code=0` のまま＝注記であってエラーではない。偽の環境を本物として見せない） | **変異 6/6 捕捉**（vision 3 本 + Room 3 本。各変異が**狙った assertion** を発火させたことまで確認、原ファイルは**開始時に捕捉したバイト列から復元**、sha256 一致）。**ハーネス自身の欠陥を 1 つ踏んだ** — 初版は `run_pin()` の文字コード例外で**変異を書いた後に落ち**、`finally` が無かったので**変異がディスクに残った**（次の実行で気づき、`finally` 復元に直した）。ピン: `tests/test_vision_row_matches_the_local_profile.py`（3 本。非空虚ガードは行の存在と判定マーカー）、`room-server/tests/test_room_server.py`（+2）、`tests/test_room_integration.py`（+1 = `Status.message` が client の `_status_dict` を通って**エージェントに届く**ことまで）。ai-server **1907 → 1911 passed / 8 skipped**（**+4 = 新ピン**、実測 392.15 秒、collected 1915 → **1919**）。egress 不変（306 マーカー / 305 passed / 1 skipped、deselected 1609 → **1613**）。room **14 → 16 passed** |
| （本節） | **`mypy>=1.8` は宣言だけで一度も走っていない — 「宣言されているが効いていない」が検査ツール自身に及んだ例**: dev 依存に `mypy>=1.8` が宣言され（`ai-server/pyproject.toml:39` と `browser-server/pyproject.toml:26`、両方の `uv.lock` にも入るので**導入はされる**）、**走らせるものがリポジトリに 1 つも無い** — `.github/` も `Makefile` も pre-commit 設定も無く、`[tool.mypy]`・`mypy.ini`・`.mypy.ini`・`setup.cfg` も無い。`scripts/` で唯一ヒットするのは `audit_common.py:27` の `".mypy_cache"` skip 項目だが、**そのディレクトリを作るものが無い**（台本自身が「走っている」と主張してしまっている）。**帰結**: 53 件の `# type: ignore`（26 ファイル、内訳 43 コード付き + 10 素）が**検証されない主張**になり、`--warn-unused-ignores` で **21 件は何も抑止していない**（`src/` 16 / `tests/` 5。対照として `--check-untyped-defs` を足しても `src/` は **16 のまま** = 「mypy が見ていないだけ」ではない）。素の 10 件は**すべて import 行**（`main.py` 6 / `mcp_gateway.py` 4）。**非対称**: `browser-server` は宣言して抑止 **0**、`room-server` は宣言せず抑止 **2**。既定設定での `python -m mypy src` は **317 errors / 94 files**（407 検査） | 変異 **8/8** 捕捉（各変異が**狙った assertion** を発火させたことまで確認、原ファイルは**開始時に捕捉したバイト列から復元**、sha256 一致）。**M5 は当初 MISS** — 陽性対照が `_mentions_tool` を**通さず** `re.search` を直接使っていたので、ヘルパーを `return False` に盲目化してもピンが緑のままだった（**規則を再実装した対照は、規則について何も証明しない**）。ピン `tests/test_type_suppressions_are_unverified.py` の 3 本は**静的な 3 事実**（宣言集合・走者の不在・素の抑止集合）を**両方向の等式**で固定し、非空虚な床（抑止 40 / pyproject 4 / 走者候補 20）を持つ。**抑止の判定は `tokenize` の COMMENT トークン**で行い、規則は「**コメントが指令で始まる**」に錨を下ろした（緩い正規表現は 54 件、厳しい規則は 53 件 — **差の 1 件はピン自身の説明コメント**で、散文走査ならピンが自分に落ちる）。ai-server **1911 → 1914 passed / 8 skipped**（**+3 = 新ピン**、実測 408.75 秒、collected 1919 → **1922**）。egress 不変（306 マーカー / 305 passed / 1 skipped、deselected 1613 → **1616**）。**配線も削除もしない** — 配線はスコープ判断（317 件をそのまま入れるゲートは無い。`ruff` が 994 → `--select F821` に絞ったのと同じ形）、削除は宣言 2 行の話（`DELEGATION.md` §4 項目 18） |
| （本節） | **proto 生成の「検証」段が何も検証していない — 契約連鎖の中間リンクが無検査だった**: `protos/aegis/` は `docs/architecture.md` が「**唯一の正典**」と名乗る共有契約で、`scripts/generate_protos.{sh,ps1}` が唯一の変換器。連鎖は `.proto` → `_pb2*.py` → 実行時だが、**中間がどのテストにも見られていなかった**（`test_schema_mirrors_the_protobuf_schema.py` は `.proto` の**テキスト**を pydantic モデルと比べるだけ）。**実測 4 件**: ① **`ai_server_pb2_grpc.py` は再生成と一致しなかった** — 3 箇所で `═`+改行（`90 0a`）が `╁E`（`81 45`）に化けており、両ファイルは**同じ長さ**、差は**docstring の中**なので実行時には見えない。**プロジェクト自身のスクリプトを走らせると直り**、現在のスクリプトは 12 ファイル中 11 を byte 一致で再現する（**`sed` のロケール説は反証された**）ので、**破損は歴史的**（原因は未同定）。② **`dev_server_pb2.pyi` は orphan** — 源の `dev_server.proto` は Dev Server と共に削除済み、参照はゼロ（名前が出るのは「bridges が import してはならない」というピンだけ）。③ **共有 proto 3 本が `android-server/app/src/main/proto/aegis/` に複製されている** — Gradle が Kotlin 用にコンパイルする。**今日は byte 一致だが、何も主張していない**。④ **`grpcio-tools` は宣言済みだが CI の `.venv` に無い**ので、再生成をテストにすると**検査が要る場所で skip する**。**副産物**: `.gitattributes` が `*.pyi` を `eol=lf` に含めていなかったため生成 `.pyi` が `core.autocrlf` の支配下にあり、**作業ツリーが恒久的に stat-dirty**（`git hash-object` は index と一致するのに `git status` が ` M` を出し続ける）で、同じ proto の 2 つの写しの改行が食い違っていた → `*.pyi text eol=lf` を追加 | 変異 **9/9** 捕捉（各変異が**狙った assertion** を発火させたことまで確認、原ファイルは**開始時に捕捉したバイト列から復元**、sha256 一致）。**M8 は想定済みの空虚化**: 比較器 `_read` を定数に盲目化すると**両辺が等しくなって一致検査が常に緑**になり、**ファイル数の床では見えない** — 内容の床（`>= 100` バイト）を足して捕捉可能にした。ピン `tests/test_generated_stubs_have_proto_sources.py` **5 本**（orphan 集合の等式・proto→スタブの被覆・room-server の絞り込み・Android 複製の一致・内容の床）。**道具なしで見える等式だけをピンした** — 再生成は `grpcio-tools` を要し CI に無いので、**環境依存の skip を単一の数に混ぜない**ため記録に回した。ai-server **1914 → 1919 passed / 8 skipped**（**+5 = 新ピン**、実測 401.44 秒、collected 1922 → **1927**）。egress 不変（306 マーカー / 305 passed / 1 skipped、deselected 1616 → **1621**）。**配線も削除もしない** — orphan 削除は 1 ファイル、CI への導入は `ruff` と同じ形（`DELEGATION.md` §4 項目 19） |
| （本節） | **§3.1 穴 3 の前提を測った — ドラフトの答えは 3 つの副指標のうち 1 つでしか成り立たない**: `DECISION_DRAFTS.md` §B-5 は穴 3（負担量の指標）を「**既存の決定ログから導出する。新しい計装は要らない**」と答えている（P1-6 が `net = benefit x P(receptive) - cost` の内訳をログに載せたから）。**着手前の測定で前提が崩れた**。**実測 3 件**: ① **1 日あたりの割り込み回数 — 計算可能**（`AuditEntry.timestamp_ms` があり、`InterruptionController.before_send` が `action="interruption_decision"` で全決定を監査するので `GROUP BY day` になる）② **ユーザーが応答した割合 — 計算不能**（応答は `NotificationManager._notifications` という**メモリ内 dict** にあり `mark_read` / `dismiss` / `expire` が書くが、`notification_manager.py` は**監査呼び出しを 1 つも持たない**ので再起動後は決定ログと join できない。さらに、それを載せるはずのメソッドが**呼び出し元を区別できない** — `dismiss(notification_id)` はユーザーの web 経路（`web/manager_routes.py`）からも**システム**（`PresentationManager.dismiss` → `notification_manager.dismiss(...)`）からも呼ばれ、**引数に印が無い**ので、dismiss をユーザー応答として数えると**システム自身の dismiss も数える**）③ **受け入れられた割り込みのコスト中央値 — 部分集合でのみ計算可能**（`utility`（＝`cost`）が付くのは **5 つある `_decision(...)` の戻り経路のうち 1 つだけ**。4 つのハードゲート — `emergency_stop`・例外カテゴリ/critical の `send_now`・静穏時間の `batch_later`・`UserModel` の `suppress` — は**内訳の無い**決定を返すので、「受け入れられた」は内訳を持つ記録と持たない記録を混ぜ、中央値が**どのゲートが発火したか**に黙って依存する）。**前提を測って崩すことは枝の実行である** — ドラフトをそのまま実行していれば、**計算できない指標を計算できると主張していた**。**記録であって配線でも削除でもない**（意図的）: 応答の永続化は**データ面＋ API 面の変更**、計装の追加は新規実装。`DELEGATION.md` §4 項目 20 として起票 | **変異 12/12 捕捉**（各変異が**狙った assertion** を発火させたことまで確認、原ファイルは**開始時に捕捉したバイト列から復元**、sha256 一致）。**M9 は当初「狙った assertion を発火させた」を満たさなかった** — 非空虚の床が `len(defining) >= 2` と**記録値と同値**だったので、`presentation/manager.py` の `dismiss` 改名（＝**このピンが炙り出すべき内容変化そのもの**）が「the scan is not reading the tree」という**嘘の診断**を出し、等式の正しいメッセージを**抑止**していた。**床を上流の量へ移した**（`_src_files()` の本数、実測 407 → 床 300）うえで `_decision` 側は **5 → 1** に下げ（M12 = 経路を 1 つ消す変異が**等式に届く**ことを確認）、**床は「等式を守る」のではなく「等式のメッセージを守る」ものだ**と分かった — 記録値と同値の床は、等式の代わりに答えて**間違って**答える。ピン `tests/test_burden_metric_has_no_instrument.py` **4 本**（決定ログの時刻と action 名・内訳を持つ経路の集合の**等値**・応答を永続化する監査呼び出しの**不在**（陽性対照つき）・`dismiss` の定義集合の等値と署名）。ai-server **1919 → 1923 passed / 8 skipped**（**+4 = 新ピン**、実測 414.56 秒、collected 1927 → **1931**）。egress 不変（306 マーカー / 305 passed / 1 skipped、deselected 1621 → **1625**） |
| （本節） | **`PresentationManager.dismiss` の優先名はテストダブルだけが定義する — 「唯一のテストが、生産が通らない枝を通っている」**: Unit 5 で測ったのと同じ呼び出し箇所を読み直したところ、`presentation/manager.py` が `getattr(mgr, "dismiss_notification", None)` を試し、`None` なら `getattr(mgr, "dismiss", None)` に落ちることに気づいた。**生産が渡す実 `NotificationManager` は `dismiss` だけを定義する**ので、**最初の探索は生産では常に `None`** — つまり**生産は常にフォールバックを通る**。ところが `dismiss_notification` を定義するクラスは**リポジトリ全体で 1 つだけ**で、それが **テストダブル**（`tests/test_presentation_engine.py` の `FakeNotificationManager`）。**この経路を覆う唯一のテストはそのダブルを渡している**ので、**テストは生産が決して通らない枝を通っている**。**危険度は推論ではなく実測**: フォールバックを削除する（＝明白な「これは死んだコードだ」という掃除）と**フルスイートが 1923 passed / 8 skipped のまま緑**（407.74 秒）— 生産は**黙って通知の dismiss をやめ、何も落ちない**。**記録であって削除でも改名でもない**（意図的）: どれを正典にするか（ダブルを実クラスに合わせる／manager に別名を足す／死んだ探索を削る）は**判断**。`DELEGATION.md` §4 項目 21 として起票 | **変異 6/6 捕捉**（各変異が**狙った assertion** を発火させたことまで確認、原ファイルは**開始時に捕捉したバイト列から復元**、sha256 一致）。**M1 = フォールバック削除**（＝このピンが存在する理由である危険そのもの）が狙いどおり 3 本目を赤にする。ピン `tests/test_dismiss_fallback_is_uncovered.py` **3 本**（生産が渡すクラスはフォールバックだけを定義する・優先名を定義するクラスは**テストダブル 1 つだけ**（**等値**）・`dismiss` が優先→フォールバックの順に解決する）。**非空虚の床は上流の量**（`src/` + `tests/` のファイル数、実測 550 → 床 400）に置いた — **M6 = 読み手 `_classes_defining` を盲目化しても床は満たされ、等式が発火する**ので、規則 10（床は等式の代わりに答えない）の実地確認にもなった。ai-server **1923 → 1926 passed / 8 skipped**（**+3 = 新ピン**、実測 415.77 秒、collected 1931 → **1934**）。egress 不変（306 マーカー / 305 passed / 1 skipped、deselected 1625 → **1628**） |

> **台帳の範囲**: ここには**実質的な変更**だけを載せる。台帳に行を足すだけの記録コミットは
> 行を持たない。この規則は遡って適用していないため、**初期の `docs(review)` 系
> （`6067c20`・`b17da28`・`55ac93f`・`6249bfb`）と `fed358e` は未記載**のまま —
> 完全な記録は `git log` にある。

### 0.2 オーナー判断レジスタ（未決のみ）

**実装で閉じられる項目は尽きており、残っているのは判断です。** ここが未決の**すべて**です
（2026-09-29 に、6 つの節に散っていた判断待ちを 1 箇所に集めた — 集める過程で、
**「判断待ち」という題の節が実は解決済みの記録だった**ことも判明した）。
**決まったらこの表から行を消す。**

> ⚠️ **2026-09-30: この表は空になりました。ただし「実装すべきことが無い」意味ではありません。**
> 以前ここには「**空になったときが「実装すべきことが無い」状態です**」と書いてありましたが、
> **それは今は偽です**。空が意味するのは「**未決の判断が無い**」ことで、**実装の在庫は §3.2 に
> 移りました**（音声 I/O・外部メッセージング・cross-device context・egress の許可制化・
> Android ツールチェーン・負担量の指標）。**判断が尽きたことと実装が尽きたことは別**です。
> **実装の残りは §3.2 を見ること**（この節ではありません）。
>
> **2026-09-30（オーナー決定）**: 残っていた **6 行すべて**が決定しました —
> **B-1** = ② を実行 / **B-5** = ① を配線 / **B-6** = **削除** / **C-1** = 維持 /
> **C-2** = 優先順位を承認 / **C-4** = ツールチェーンを導入。**さらに制約そのものが再定義**されました
> （egress は「許可の無いユーザー情報の送信」を禁じる形へ — 接続は可・許可があれば外部利用可）。
> **決定の記録と戻し方は `DELEGATION.md` §2・§5、制約の正典は `docs/GOAL-CHANGE.md`。**

> **2026-09-30（委任）**: **A-6 / A-11 / A-13 / B-2 / B-3 / A-12 / B-4 / C-3 / C-5 の 9 行を閉じて削除した** —
> 前 6 行はピンが既にあり、**緑であることを実行して確認してから**閉じた（実測は §0.1 の台帳行）。
> **B-4 はピンではなく実測で**閉じた（移植対象の識別子が `src`・`tests` に **0 件**）。
> **C-3 と C-5 は「そもそも決めることが無かった」** — どちらも枝が既に決まっており（C-3 = 正典は §4.3、
> C-5 = 手動のまま維持）、**残った問いは §4 の項目 6・7 に既に移してあった**ので、行だけが二重だった。
> **決定の理由と戻し方は `DELEGATION.md`。** この節は未決の一覧なので、決定済みの内容はここに残さない
> （決定が済んだ行を削除するのがこの節の契約）。
>
> **参照の意味**: 決定済みの行は削除されるので、**過去の節（§0.1・§5.x）やスキルが「§0.2 の
> ○○ 行」と参照していても、その行は既に無いことがあります** — 参照は**当時の記録**であって、
> 現在の在庫ではありません。**在庫はこの節にしかなく、決定の記録は `DELEGATION.md` にあります。**

#### A. 一言で決まる（実装は数行）

**（現在、該当なし）** — 最後の 1 行（A-12）を 2026-09-30 に ② で閉じた。

#### B. 定義が要る（挙動が動く）

**（現在、該当なし）** — 3 行（**B-1** / **B-5** / **B-6**）を **2026-09-30 にオーナーが決定**した
（B-1 = ② を実行 / B-5 = ① を配線 / B-6 = **削除**）。決定と戻し方は `DELEGATION.md` §2・§5。

#### C. 方向づけ（急がない）

**（現在、該当なし）** — 3 行（**C-1** / **C-2** / **C-4**）を **2026-09-30 にオーナーが決定**した
（C-1 = 維持 / C-2 = 優先順位を承認 / C-4 = ツールチェーンを導入）。同上。

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
| **AI Server** | Python 3.13/3.14 | 50051 | 中枢（LLM / 記憶 / 欲求 / 自律ループ） | **2768 passed / 8 skipped** |
| **PC Server** | Rust | 50052 | Windows 操作（TCP JSON プロトコル） | Python テスト **0**（Rust 側のみ） |
| **Browser Server** | Python | 50053 | Web 閲覧（HTTP、`ThreadingHTTPServer`） | **100 passed** |
| **Android Server** | Kotlin | 契約上 50054（実機は 50051 へ outbound） | 端末コンパニオン | 実機テストのみ（`android_local`） |
| **Room Server** | Python | 50055 | IoT / センサ | 16 passed |
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
>
> **同日、同じ型が 3 度目に再発した。** A-12（−3 テスト関数）と B-1①（+1）が AI Server の数を
> **1777 → 1775** に動かしたのに、**live な写し 3 つ（§0 の要約行・本表・`AGENTS.md`）が追随して
> いなかった**（§0.1 の台帳行だけが動いていた — まさに「片方だけが動く」）。B-5② の実装時に 3 写しを
> **1776** へ揃え、**§0 の要約行にもこのドリフト自体を書いた**（次に数が動いたとき、どの写しを見るべきかが
> 分かるように）。**この段落の上の 1777 は「その時に測った値」なので動かさない** — 動かすのは
> **現在値を名乗っている写し**だけ、というのがこの節の規約。**教訓**: テスト数を動かす変更は、
> **この 3 写しを同じコミットで直す**まで終わらない。
>
> **2026-10-03 に再実測 — 同じ型が 4 度目。** 本表の AI Server 行が **1923** のまま §0（**1960**）と
> 食い違っていた。`f8e0b06`（+3）と `cafac24`（+6）を含む 1926 → 1960 の **+34 が §0 の要約行にしか
> 反映されていなかった**（台帳行は当時の値なので正しい）。本表を **1960** に揃え（同日さらに **+10** = `test_egress_grant_source_is_unwired.py` と `test_chat_sse_route_stays_dead.py`、さらに **+2** = `test_documented_routes_are_registered.py` で **1972**、さらに **+5** = `test_e2e_compose_services_exist.py` で **1977**、さらに **+1** = 同じピンの走査を `.ps1` から **`.sh` へ広げて**（`scripts/ubuntu/*.sh` の 7 呼び出しが未読だった）**1978**、さらに **+6** = `test_event_driven_core_stays_unbuilt.py`（イベント駆動の中核が未構築であること）で **1984**、さらに **+8** = `test_audit_jsonl_has_no_writer.py`（`data/audit.jsonl` に書き手が 0・読み手 4）で **1992**、さらに **+5** = `test_presentation_stream_leaks_a_subscriber.py`（**当時の名前** — 後に `test_presentation_stream_is_sound.py` へ改名。`/api/presentations/stream` がリクエストごとに購読者を漏らす）で **1997**、さらに **+14** = `test_memory_backend_registries_agree.py`（`MemoryManager` の 3 名簿が一致しない）で **2011**、さらに **+6** = `test_no_route_is_shadowed.py`（legacy の写しが影を落としている 2 ルート）で **2017**、さらに **+2** = オーナー決定の実行（`aegis_ai/permissions/` 削除・負担量の指標の定義・`AGORA_MASTER_USER` 削除。内訳は **+15 − 8 − 4 − 1**）で **2019**、さらに **+2** = その presentation-stream ピンを**修正の assert へ反転**（5 → 7 本）して **2021**、さらに **+3** = memory 名簿ピンを**一致の assert へ反転**（14 → 17 ケース）して **2024**、さらに **+0** = `test_no_route_is_shadowed.py` を**影が 0 という不変条件へ反転**（**6 → 6 本** — 反転であって増設ではないので総数は動かない。代わりにルート面が動いた: **192 ルール / 202 対 / 200 一意対 → 190 / 200 / 200**、未参照 **98 → 96**、literal のみ **127 → 125**）で **2024 のまま**、さらに **+11** = `test_chroma_vector_path_stays_unwired.py`（Chroma のベクトル経路が到達不能であること ＋ 同名 `SemanticMemory` が 2 つありパッケージ根が死んだ方を再輸出していること）で **2035**、さらに **+18** = §4 項目 8（負担量の指標）の**配線**で **2053**（`test_burden_metric_is_judged.py` +3・`test_burden_check_is_asked_by_the_loop.py` +15 — うち **+2 は配線の硬化**（`_create_autonomous_loop` はスイートに一度も実行されないので、`set_burden_metric` の**実走**ピンと composition root の**位置引数ちょうど 1 つ**を形で固定するピン）。配線は 5 箇所 — ① `JUDGMENT_PROFILE` を `decision` → **`jev_decision`**（旧値は allowlist に拒否され Mock へ落ち、`is_trustworthy=False` なので**決して聞かない**）② `build_user_question` の `side_effects` を **list → string**（能力自身の `input_schema` が `string` を宣言しており、`[]` は broker の `VALIDATION_DENY` になる）③ `AutonomousLoop._maybe_ask_burden_check` の周期フック ④ `last_burden_ask_ms` の永続化 ⑤ composition root の `set_burden_metric`）、他行も再実測した
> （browser **100** / room **16** / SDK **71** / vitest **144** / playwright 42）。
> **教訓は変わらない** — 数を動かす変更は、§0・本表・`AGENTS.md`・検証スキル §1 を**同じコミットで**
> 直すまで終わらない。
>
> **同日さらに 4 度目の再発**（2026-09-30）: 音声 I/O（`d9a01cb`）・外部メッセージング（`ad9d32f`）・
> cross-device context（`19ae1b1`）の 3 コミットが AI Server を **1776 → 1891**、egress マーカーを
> **233 → 325** 動かしたのに、**3 写しは 1776 のまま**だった（3 コミットはいずれも `docs/` を触ったが、
> この数を直していない）。実測して 3 写しを **1891 / 30**（egress **302 / 23**）に揃えた。
> **今回は 4 つ目の写しも見つかった** — 検証スキル §1 の表が **1766** を名乗っており、
> **リポジトリ内のどの写しよりも古かった**。**理由**: スキルはリポジトリの外にあるので、
> **数を動かすコミットがスキルに届かない**（誰も直さない）。**教訓**: 数を動かす変更は
> **リポジトリの外の写しも含めて**同じコミットで直す。
>
> **同日 5 度目（B-6、2026-09-30）**: 未読スイッチ 22 件の削除が AI Server を **1891 → 1885 passed /
> 30 → 8 skipped**、egress マーカーを **325 → 303** に動かした。**今回は 4 写しすべてを同じコミットで
> 直した**（§0 要約行・本表・`AGENTS.md`・検証スキル §1）。**内訳を先に確定させてから書いた** —
> 通過 −6 = 新ピン **+4** / 削除した記録ピン **−10**、スキップ −22 = **消したフィールドそのもの**。
> **スキップの減少は B-6 の記録を消した副作用**なので、**記録だけ消して負債を残す変更と見分けが
> 付かない**（検証スキル §1 が警告している型）。**だから内訳をここに書く** — 数だけでは
> 「負債を返した」と「負債の記録を捨てた」が同じ形になる。
>
> **同日 6 度目（B-5①、2026-10-01）**: 確認を欲求に結びつける配線が AI Server を **1885 → 1889 passed**
> に動かした（**+4 = 新ピンそのもの**）。**egress は動かなかった**（**303 マーカー / 302 passed / 1 skipped**
> のまま、deselected 1590 → 1594）— 新 4 本がマーカーを持たないため。**今回は 4 写しを同じコミットで直した**
> （§0 要約行・本表・`AGENTS.md`・検証スキル §1）。**派生量は測り直した**（egress の数は `src/` が変われば
> 動きうる）。**副産物**: この配線で**スイートが緑のまま通った未定義名**（`F821`）を自分で入れた —
> `autonomous_loop_enabled` が既定 `False` で当該関数がテストから実行されないため。**ruff だけが捉え、
> CI は ruff を走らせていない**（`DELEGATION.md` §4 項目 7）。
>
> **同日 7 度目（`autonomy` 残骸の削除、2026-10-01）**: 出荷 `config/settings.json` に、どのモデルも
> 宣言しないブロックが 1 つ残っていた（P1-3 が削除した `AutonomyProfile` の残骸、11 鍵すべてが
> 未宣言）。削除と**一般形のピン**（出荷 config の全鍵がモデルに宣言されていること）で AI Server は
> **1889 → 1890 passed**（**+1 = 新ピン**）。**egress は不変**（303 マーカー / 302 passed / 1 skipped、
> deselected 1594 → 1595）。**気づいた経緯そのものが型の実例** — `docs/adr/permissive-autonomy-policy.md`
> は 2026-09-28 に「`autonomy` settings 節は**削除された**」と書いていたが、**モデルは消えて出荷 config の
> ブロックは残っていた**（ADR の主張は*その時点で既に*半分偽）。**検出器がモデルしか見ていなかった**
> ので 2 日間見えなかった。
>
> **同日 8 度目（音声ゲートの死んだ検査、2026-10-01）**: `VoiceGate` / `VoicePrivacy` の公開検査 4 本
> （`is_audio_recording_allowed`・`is_wake_word_enabled`・`should_store_audio`・`is_external_api_allowed`）が
> **`src/` から一度も呼ばれていない**ことを実測した。帰結として 3 設定（`voice.record_audio`・
> `voice.voice_data_retention_hours`・`voice.wake_word_enabled`）が**生きた読者を持たない** — なのに
> `test_ineffective_flags.py` は「読まれている」と報告する（**死んだコードの中の読者も読者として数える**。
> B-13「検証器だけの読者は未読として数える」の**鏡像**で、§4.3 クラス 7 の 2 つ目の機構）。記録ピン 3 本で
> AI Server は **1890 → 1893 passed**（**+3 = 新ピン**）。**今回は egress も動いた** —
> `tests/test_voice_io.py` は**モジュール全体が egress マーカー**なので **303 → 306 マーカー /
> 302 → 305 passed**（deselected 1595 のまま）。**4 写しを同じコミットで直した**
> （§0 要約行・本表・`AGENTS.md`・検証スキル §1）。
>
> **同日 9 度目（承認の監査 API、2026-10-01）**: `log_approval`（定義 3 つ）に**自分の転送連鎖の外の
> 呼び出し元が無い**ことを実測した。帰結として `AuditEntry.source_desire` の書き手は死んだ本体 2 つだけ
> なので、**監査レコードの `source_desire` は常に空** — カラムが「欲求に紐づく」と読めるのに一度も
> 紐づかない（型 6）。記録ピン 2 本で AI Server は **1893 → 1895 passed**（**+2 = 新ピン**）。
> **egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1595 → 1597）。
> **4 写しを同じコミットで直した**（§0 要約行・本表・`AGENTS.md`・検証スキル §1）。
> **削除はオーナー項目**（`DELEGATION.md` §4 項目 13）— 永続カラムと 2 つのデータクラスに波及する。

> **同日 10 度目（`aegis_ai/security/` が未配線、2026-10-01）**: パッケージ外からの import が
> **ゼロ**であることを実測した（自己参照 14 ヒットのみ）。6 クラス名も外部で未参照、生きた認証は
> `aegis_ai/auth/`。TLS は `add_secure_port` の呼び出し元が死んだ `configure_server` だけなので
> **gRPC は平文**。記録ピン 5 本で AI Server は **1895 → 1900 passed**（**+5 = 新ピン**）。
> **egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1597 → 1602）。
> **4 写しを同じコミットで直した**（§0 要約行・本表・`AGENTS.md`・検証スキル §1）。
> **配線も削除もしない** — 配線は二重の認証実装、削除はオーナー判断（`DELEGATION.md` §4 項目 14）。

> **同日 11 度目（Docker 面の検証、2026-10-01）**: compose↔Dockerfile の配線を固定し、dev-server の残存を実測した。記録ピン 2 本で AI Server は **1905 → 1907 passed**（**+2 = 新ピン**、実測 414.60 秒、collected 1913 → 1915）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1607 → 1609）。**6 箇所（5 ファイル）を同じコミットで直した**（§0 要約行・本表・`AGENTS.md`・`docs/architecture.md` の 2 箇所・検証スキル §1）。**副産物 2 件**: `BUG_REPORT.md` §9 の残骸表が **5 行すべて反証**（掃討が 4 ファイルで止まっていた）、§28 の記録が指すファイル名と実際の修正先が違った。**削除はしない**（オーナー判断、`DELEGATION.md` §4 項目 17）。

> **同日 12 度目（視覚の誤った主張の訂正と Room fixture の明示、2026-10-01）**: §3.2 の vision 行は「`llm.yaml` が Aliyun を指したまま／egress が止めるため**視覚機能は実質不可**」と書いていたが、**着手前の測定で機制・結論とも誤り**と判明した（`profiles.local_vision` は生きており `localhost:11434`、`_LOCAL_PROFILE_MAP` が remap、`verify_egress_configuration` は `local_llm_readiness: ok`）。**ドラフトの推奨（UI/文書で「視覚機能は無効」と明示）を実行していれば、システム自身の判定と矛盾する嘘を公開していた** — 取り下げ、§3.2 を ✅ に訂正し、生きた写し 3 つを掃討（`PROGRESS_2026-09-29.md` は**日付付き記録なので不変**）。**ただしこの「3 つ」は同日 13 度目に反証された** — 走査語を「vision」に限ったため `DELEGATION.md` §1 条件 3・§3 表（「vision ローカル代替」）と `IMPROVEMENT_PROPOSAL.md` §9.7（「**視覚**の欠落」）が漏れ、**正しい数は 6**。ピンは**散文走査にせず**、**行の判定マーカーを resolver の解決先に結びつけた**（両方向に落ちる）。同時に Room の `GetEnvironment` が**ハードコード fixture を「ok」と称していた**ので `Status.message` で fixture と明示。AI Server は **1907 → 1911 passed**（**+4 = 新ピン**、実測 392.15 秒、collected 1915 → **1919**）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1609 → **1613**）。**10 箇所（5 ファイル）を同じコミットで直した**（§0 要約行・§1.1 の表・§0.1 の本行・本注記・`AGENTS.md`・`docs/architecture.md` の 2 箇所・検証スキル 2 箇所・`DELEGATION.md` §5）— **うち §1.1 の表（`| **AI Server** | … | 1907 passed |`）は最初の掃討で漏れ、`grep` で拾い直した**（「掃討の被覆そのものが主張であり、測らないと見えない」の再発）。room は **14 → 16 passed**。
>
> **同日 13 度目（掃討の被覆そのものが誤りだった、2026-10-01）**: 12 度目が記録した「生きた写し 3 つ」は
> **誤り**で、正しい数は **6**。走査語を「vision」に限ったため、`DELEGATION.md` §1 条件 3・§3 表
> （「vision ローカル代替」）と `IMPROVEMENT_PROPOSAL.md` §9.7（「**視覚**の欠落」）が**別の語で現れている**
> ことに気づけなかった。**テスト数は動いていない**（記録の訂正のみ）ので §0 の要約行に載る数は変わらない —
> それでも**数が動かない変更が記録を腐らせうる**、というのがこの行の内容。**教訓**: 掃討の被覆は主張であり、
> **走査語の集合も主張**である（`grep` した語を名乗る限り、別名で書かれた写しは見えない）。
>
> **同日 14 度目（`mypy` は宣言だけで走っていない、2026-10-01）**: dev 依存に `mypy>=1.8` が宣言され
> **導入はされる**のに、**走らせるものがリポジトリに 1 つも無い**ことを実測した（`DELEGATION.md` §4 項目 18）。
> 帰結として **53 件の `# type: ignore` が検証されない主張**になり、うち **21 件は何も抑止していない**
> （`src/` 16 / `tests/` 5。対照として `--check-untyped-defs` を足しても `src/` は **16 のまま**）。
> **10 件はコード無しの素の `# type: ignore`** で、**すべて import 行**。記録ピン 3 本で AI Server は
> **1911 → 1914 passed**（**+3 = 新ピン**、実測 408.75 秒、collected 1919 → **1922**）。
> **egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1613 → **1616** — 新 3 本は非 egress）。
> **同じコミットで直した写し**: `PROJECT_STATUS_REVIEW.md` の 4 箇所（§0 要約行・§1.1 の表・§0.1 の本行・
> 本注記）・`AGENTS.md`・`docs/architecture.md` の 2 箇所・`DELEGATION.md` §4 項目 18・検証スキル §1。
> **配線も削除もしない** — 317 errors をそのまま入れるゲートは無く、削除は宣言 2 行の話。
> ⚠️ **変異ハーネスが私の欠陥を 1 つ捕まえた**: 陽性対照が `_mentions_tool` を**通さず** `re.search` を
> 直接呼んでいたので、ヘルパーを盲目化する変異 M5 が**捕捉されなかった** — **規則を再実装した対照は、
> 規則について何も証明しない**（ファイル走査が動くことだけを証明する）。
>
> **同日 15 度目（proto 生成の検証段と、契約連鎖の中間リンク、2026-10-01）**: `protos/aegis/` は
> 「唯一の正典」と名乗るのに、**`.proto` → サーバが import するスタブ**のリンクがどのテストにも
> 見られていなかった。実測 4 件 — ① **`ai_server_pb2_grpc.py` は再生成と一致しない**（`═`+改行 →
> `╁E` が docstring 内に 3 箇所。**両ファイルは同じ長さ**なので diff 以外では見えない）。
> **プロジェクト自身のスクリプトで修復**し、現在のスクリプトは 12 ファイル中 11 を byte 一致で
> 再現するので**破損は歴史的**（`sed` のロケール説は反証）。② **`dev_server_pb2.pyi` は orphan**
> （源の proto は削除済み、参照ゼロ）。③ **共有 proto 3 本が Android 側に複製され、今日は一致して
> いるが無検査**。④ **`grpcio-tools` は CI の `.venv` に無い**ので再生成をテストにすると skip する。
> **副産物**: `*.pyi` が `.gitattributes` の `eol=lf` に含まれず、生成 `.pyi` が `core.autocrlf` の
> 支配下にあった（**作業ツリーが恒久的に stat-dirty** で、同じ proto の 2 写しの改行が食い違う）。
> ピン 5 本で AI Server は **1914 → 1919 passed**（**+5 = 新ピン**、実測 401.44 秒、collected
> 1922 → **1927**）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected
> 1616 → **1621** — 新 5 本は非 egress）。**同じコミットで直した写し**: §0 要約行・§1.1 の表・
> §0.1 の本行・本注記・`AGENTS.md`・`docs/architecture.md` の 2 箇所・`DELEGATION.md` §4 項目 19 と
> §5・検証スキル §1。**変異 9/9 捕捉** — うち **M8 は空虚化の実例**: 比較器を定数に盲目化すると
> **両辺が等しくなり一致検査が常に緑**で、**ファイル数の床では見えない**（内容の床を足した）。
> **再生成の検査はピンにしなかった** — `grpcio-tools` が CI に無く、**環境依存の skip を単一の数に
> 混ぜない**ため（記録に回した）。
> **同じ掃討で、vision 単位の「副作用の数」も腐っていた** — `room-server` は実測 **16** なのに
> **4 つの生きた写しが 14 のまま**だった（§0 要約行・§1.1 の表・`AGENTS.md`・検証スキル §1）。
> 12 度目の単位は room の 14 → 16 を**自分の台帳行には書いたが、現在値を名乗る表に伝えていない**。
> **数を動かす変更は、その変更の「副作用として動いた数」まで掃討しないと終わらない** — 15 度目までと
> 同じ型の **16 度目**。
>
> **同日 17 度目（§3.1 穴 3 の前提の測定、2026-10-01）**: `DECISION_DRAFTS.md` §B-5 は穴 3 を「**既存の
> 決定ログから導出する。新しい計装は要らない**」と答えているが、**測ると 3 つの副指標のうち 1 つでしか
> 成り立たない** — ① 1 日あたりの回数は**可**（`AuditEntry.timestamp_ms` + `action="interruption_decision"`）
> ② 応答割合は**不可**（応答は `NotificationManager._notifications` のメモリ内 dict にあり、
> `notification_manager.py` は**監査呼び出しを 1 つも持たない**。しかも `dismiss(notification_id)` は
> ユーザーの web 経路と `PresentationManager.dismiss`（**システム自身**）の両方から呼ばれ、**引数に印が
> 無い**）③ コスト中央値は **5 経路中 1 つだけ**（4 つのハードゲートは内訳を返さない）。**前提を測って
> 崩すことは枝の実行**であり、ドラフトをそのまま実行していれば**計算できない指標を計算できると主張して
> いた**。ピン 4 本で AI Server は **1919 → 1923 passed**（**+4 = 新ピン**、実測 414.56 秒、collected
> 1927 → **1931**）。**egress は不変**（306 マーカー / 305 passed / 1 skipped、deselected 1621 → **1625**
> — 新 4 本は非 egress）。**同じコミットで直した写し**: §0 要約行（見出しの数と末尾の記録）・§1.1 の表・
> §0.1 の本行・本注記・`AGENTS.md`・`docs/architecture.md` の 2 箇所・`DELEGATION.md` §4 項目 20 と §5・
> 検証スキル §1。**変異 12/12 捕捉** — うち **M9 は当初「狙った assertion を発火させた」を満たさなかった**:
> 非空虚の床が**記録値と同値**（`len(defining) >= 2`）だったので、`dismiss` の改名という**このピンが
> 炙り出すべき内容変化**が「the scan is not reading the tree」という**嘘の診断**を出し、等式の正しい
> メッセージを抑止していた。**床は等式の代わりに答えて、間違って答える** — 床は上流の量に置き、等式より
> 厳密に弱くする（記録値と同値の床は床ではない）。
>
> **同日 18 度目（同じセッションの中で日付の規約が 2 つ使われていた、2026-10-01）**: このセッションは
> **日付の境界をまたいでいる** — 開始 2026-10-01 23:41 JST、`411a569`（Docker 面）は **2026-10-02 00:48**、
> 以降の `dae92dd`/`86862a2`（vision）・`b654968`（mypy）・`2203e20`（proto）・`bd01937`（穴 3）も
> **すべて 2026-10-02** である。**日付を名乗る生きた成果物は 18 ファイル、うち 17 が `2026-10-01` で
> 1 件だけが `2026-10-02`** — その 1 件が `tests/test_dockerfiles_are_owned.py:38` の
> 「Drift (measured 2026-10-02)」だった。**同じ者が 1 時間半違いで 2 つの規約を使っていた**（proto のピンは
> 02:09 のコミットで「measured 2026-10-01」と書いている）。**日付も数と同じく主張である** — 2 箇所に書けば
> 2 回腐り、ここでは**同じセッションの中**で既に食い違っていた。
> **採った規約（推奨で選んだ。オーナーは反転できる）**: **成果物も台帳も「セッション日」で揃える** —
> セッションが日付をまたぐと `git log` の日付とは**必ず 1 日ずれる**（その 1 日は**壁時計 2026-10-02**）。
> よって逸脱していた 1 件（Docker ピン）を `2026-10-01` に揃え、他の 17 件はそのまま。
> **「いつ測ったか」の正典は `git log --date=format:'%Y-%m-%d %H:%M %Z'`** — 壁時計を示すのはそこだけ。
>
> **同日 19 度目（`PresentationManager.dismiss` の優先名はテストダブルだけが定義する、2026-10-01）**:
> Unit 5 で測ったのと同じ呼び出し箇所を読み直して見つけた。`presentation/manager.py` は
> `dismiss_notification` を先に探し `dismiss` に落ちるが、**生産が渡す実 `NotificationManager` は
> `dismiss` だけを定義する**ので**生産は常にフォールバックを通る**。優先名を定義するクラスは
> **リポジトリ全体で 1 つだけ**で、それが**テストダブル**（`FakeNotificationManager`）— つまり
> **この経路を覆う唯一のテストは、生産が決して通らない枝を通っている**。**危険度は推論ではなく実測**:
> フォールバックを削除すると**フルスイートが 1923 passed / 8 skipped のまま緑**（407.74 秒）で、
> **生産は黙って通知の dismiss をやめ、何も落ちない**。ピン 3 本で AI Server は **1923 → 1926 passed**
> （**+3 = 新ピン**、実測 415.77 秒、collected 1931 → **1934**）。**egress は不変**（306 マーカー /
> 305 passed / 1 skipped、deselected 1625 → **1628** — 新 3 本は非 egress）。**変異 6/6 捕捉** —
> **M1（フォールバック削除）がこのピンの存在理由そのもの**で、狙いどおり赤になる。**M6 は規則 10 の
> 実地確認**になった: 読み手 `_classes_defining` を盲目化しても**上流の床（ファイル数 550 → 400）は
> 満たされ**、等式が発火する。**同じコミットで直した写し**: §0 要約行（見出しと末尾）・§1.1 の表・
> §0.1 の本行・本注記・`AGENTS.md`・`docs/architecture.md` の 2 箇所・`DELEGATION.md` §4 項目 21 と
> §5・検証スキル §1。
> **教訓**: **テストダブルが実クラスに無いメソッドを定義すると、テストは生産が通らない枝を通る** —
> そして**その枝を消しても緑のまま**である（＝**緑は「覆っている」証拠にならない**）。
>
> **同日 20 度目（L1 ゲートの黙った迂回と、掃討の記録そのものが誤っていた件、2026-10-04）**: 前コミット
> （`50c26a5`、**+9**）は §0 要約行・`AGENTS.md`・`DELEGATION.md` §5・検証スキル §1 を動かしたが、
> **本表の AI Server 行とこの注記は `2061` のまま**だった — 記録は「4 つの写しを同コミットで移動」と
> 書いていた。今回の **+5** の掃討中に実測で発見し、両方を **2075** に揃えた（**「掃討した」という記録
> 自体が主張であり、測るまでは真でない**）。**+5 = 新ピンちょうど**（`tests/test_the_l1_gate_is_not_bypassed.py`、
> **変異 9/9**）で、直したのは**ゲートの黙った迂回**: ゲートは `llm.generate(..., profile="l1_default")` を
> 呼ぶが、`profile=` を受け取れるのは `LLMGateway.generate` **だけ**（`MockLLMProvider` /
> `openai_provider` / `typesafe_provider` はいずれも取らない — シグネチャ 3 つを実測）なので、
> ゲートウェイ以外の `llm` を束ねると例外が**握り潰され**、**ゲートが一度も走らない**ままテストは緑になる。
> 診断性の修正で 2026-10-04 に**1 時間で 2 件**判明した（`MockLLMProvider` が `profile` を取らない／
> テストダブル `NativeToolLLM` が `generate` を持たない）。ダブルを本番の形に合わせ、`src/` と `tests/` の
> 全呼び出し点（`call_llm_with_tools` / `_call_llm_with_runtime`）を**発見方式で解決**するピンを追加。
> AI Server は **2070 → 2075 passed**（実測 519.92 秒、collected **2083**）。**egress は不変**
> （315 マーカー / 314 passed / 1 skipped、deselected 1763 → **1768** — 新 5 本は非 egress）。
> **同じコミットで直した写し**: §0 要約行（見出しと末尾）・本表・本注記・`AGENTS.md`・`DELEGATION.md` §5・
> 検証スキル §1。
>
> **同日 21 度目（同形の掃討、2026-10-04）**: 前コミット（`3d2738e`、**+5**）の掃討は**今回は正しかった** —
> 4 つの写し（§0 要約行・本表・`AGENTS.md`・検証スキル §1）が揃って動いていた。**+3 = 新ピンちょうど**
> （`test_the_l1_gate_is_not_bypassed.py` が 5 → **8 本**）。`src/` の `generate(..., profile=...)` は実測 **9 箇所**、
> 握り潰していたのはゲートだけ（6 防御 / 3 未防御だが安全）で、ピンは**新しい未防御サイトを拒否**する
> （**変異 15/15**）。AI Server は **2075 → 2078 passed**（実測 426.13 秒、collected **2086**）。**egress は不変**
> （315 マーカー / 314 passed / 1 skipped、deselected 1768 → **1771** — 新 3 本は非 egress）。
>
> **同日 22 度目（黙って捨てられる読み込み、2026-10-04）**: 続き — 前コミット（`ce4ba44`、**+3**）の掃討も
> 正しかった。**+9 = 新ピンちょうど**（`tests/test_executor_manifest_failures_are_named.py`）。
> `ExecutorRegistry._load_one` は読めない `executor.json` で `return` していた — 結果は**クラッシュではなく
> 不在**で、`execute` は `EXECUTOR_NOT_FOUND` を返すが「未作成」と「解析不能」を区別できない。姉妹ローダ
> `FolderCapabilityRegistry` は元から `_errors` / `errors()` / `reload()["errors"]` を持っていたので同じ水準に
> 合わせ、`CapabilityCatalog.reload()` が**実行器側の結果ごと捨てていた**のを `executor_errors` として転送した
> （`errors` は能力マニフェストの意味のまま — **2 つの経路は別のまま**）。**変異 10/10**。AI Server は
> **2078 → 2087 passed**（実測 405.54 秒、collected **2095**）。**egress は不変**（315 マーカー / 314 passed /
> 1 skipped、deselected 1771 → **1780** — 新 9 本は非 egress）。
>
> **同日 23 度目（出荷されたマニフェストの木の整合性、2026-10-04）**: **+5 = 新ピンちょうど**
> （`tests/test_shipped_manifest_tree_is_coherent.py`）。他のどのテストも `apps/` を**ディスクから読まない**
> ので、2 つの失敗モードが誰にも見えていなかった: ① 解析できない `executor.json` — 実行器が**不在**になり
> `EXECUTOR_NOT_FOUND` を返すが、それは**内製ハンドラで処理される 105 の能力**にとっても正直な答えなので、
> 打ち間違いと「そもそも実行器を持たない能力」を区別できない。② 能力が改名・削除された**孤児の
> `executor.json`** — 誰も読まない死んだマニフェスト。実測 2026-10-04: ディスク上 **23** = 読込 **23**、
> 読込エラー **0**、孤児 **0**、能力 **128**。数は**ファイルシステムから導出**するので、能力を足しても
> このファイルは編集不要で、**整合性を壊したときだけ**落ちる。`runtime.py` が本当にその 2 つの
> ディレクトリを束ねていることも `ast` で突き合わせる（**2 つの成果物が同じことを言っているか**）。
> **変異 6/6**。AI Server は **2087 → 2092 passed**（実測 413.30 秒、collected **2100**）。**egress は
> 不変**（315 マーカー / 314 passed / 1 skipped、deselected 1780 → **1785** — 新 5 本は非 egress）。
> ⚠️ **先に「全ての能力が実行器を持つ」をピンしようとして実測で反証された** — 128 中 **105** が実行器を
> 持たない（内製ハンドラで処理されるので**設計**であって欠陥ではない）。**前提を測ってから実行する**。
>
> **同日 24 度目（壊れた社会データのストア、2026-10-04）**: **+10 = 新ピンちょうど**
> （`tests/test_social_store_failures_are_reported.py`）。`SocialIntelligenceSystem._load` は 6 つの JSONL を
> 読むが、`_load_jsonl`（observations / episodes）は**元から警告していた**のに、4 つの専用ローダ
> （relationships / reputations / social_norms / social_skills）は `except Exception: pass` だった。結果は
> いつもの形: ストアは**空の dict** に落ち、他の唯一の信号は `_load` の集計行（件数を数える）だけ —
> **解析に失敗したストアと、まだ 1 件も無いストアが同じ行を出す**ので、壊れた `relationships.jsonl` は
> **新規インストールと見分けがつかない**。`_load_jsonl` と同じ警告に揃えた（挙動は不変 — 空への
> フォールバックはそのまま）。ピンは `caplog` で**記録を捕まえる**（テキストではなく挙動）ので、4 ストアの
> パラメータ化 + **欠測時は黙る**（非空虚対照）+ **1 つ壊れても他は読める** + 既存ヘルパの警告を固定。
> **変異 7/7**。AI Server は **2092 → 2102 passed**（実測 399.98 秒、collected **2110**）。**egress は不変**
> （315 マーカー / 314 passed / 1 skipped、deselected 1785 → **1795** — 新 10 本は非 egress）。
>
> **同日 25 度目（壊れた上書きファイルが全上書きを黙って捨てる、2026-10-04）**: **+8 = 新ピンちょうど**
> （`tests/test_policy_override_load_failures_are_named.py`）。`PolicyEngine._load_overrides` は `__init__`
> から呼ばれ、2 つの失敗を裸の `pass` で飲んでいた — 読めない/壊れたファイル（**全上書きが消える**）と
> 未知の危険度名（その 1 つが消える）。結果はクラッシュではなく**静かな降格**である: `DEFAULT_RISK_MAP` は
> `RiskLevel.FORBIDDEN` → `PolicyDecision.DENY` なので、能力を FORBIDDEN に引き上げた上書きは適用されなく
> なり、能力は（より寛容な）マニフェストの水準へ落ちる。**「ファイルが無い」と「壊れている」が区別できない**
> — これまで何度も見た形だが、今回は**判定そのもの**（DENY か ALLOW か）に効く。**姉妹機構との非対称**:
> `CapabilityCatalog` の `OverrideStore` は元から `corrupted` を報告し、壊れたときは **fail-closed**
> （`approval_required` へ）に倒れる。こちらは原因（パス + 例外型）と結果を名指しするようにした。
> ⚠️ **重症度は推論ではなく実測**: 3 つのハードストップはこのファイルに依存しない
> （`EXPLICIT_DENY_PATTERNS` が毎 `evaluate()` で走る）し、`set_risk_override` には現在**本番の呼び手が無い**
> （`tests/test_dashboard_routes.py:591` のみ）ので、露出は**潜在**である。**フォールバックの非対称
> （こちら fail-open / 姉妹 fail-closed）は挙動の問い**なので、所有者向けに記録し変更しない。
> ピンの対照は**噛む**: 同じ能力が良いファイルで DENY、壊れたファイルで ALLOW。**変異 7/7**、対照緑、
> `sha256` 一致で復元、`leftovers=[]`。**AI Server は 2102 → 2110 passed**（実測 394.55 秒、
> collected **2118**、`-m "not egress"` = **1796 / 7 / 315**）。**egress は不変**
> （315 マーカー / 314 passed / 1 skipped、deselected 1795 → **1803** — 新 8 本は非 egress）。
> **派生値**「追加分」は **148 → 156**（`2118 − 1962` collected、`1803 − 1647` deselected）。
>
> **同日 26 度目（捨てられた記憶の行、そして握り潰しは共有ヘルパにあった、2026-10-04）**: **+13 = 新ピンちょうど**
> （`tests/test_advanced_memory_load_failures_are_named.py`）。`AdvancedMemory._load` は 3 つの JSONL ストア
> （entities / facts / conversations）を読むが、解析できない行は裸の `except Exception: pass` で捨てられ、
> ストアは**短く**戻っていた。他の唯一の信号 `get_stats()` は**件数**を報告するので、**解析に失敗した
> ストアと一度も書かれていないストアが同じ種類の答え（より小さい数）**を出す — 帰属の手段が無い。
> 非対称は**同じクラスの中**にあった: 同じクラスは LLM 抽出の失敗では既に
> `logger.warning("LLM extraction failed: %s", e)` を出している。3 つのループが捨てた数を数え、
> **ファイルごとに 1 回**警告する（行ごとだと壊れたファイルでログが溢れる）。
> ⚠️ **測定が最初の前提を否定し、第 2 の層を見つけた**: 会話ストアは `_load` のループに到達**しない** —
> 共有ヘルパ `aegis_ai.jsonl_tail.read_jsonl_tail` を通り、**そこで**不正な行が握り潰されていた
> （`except Exception: continue`、数えも記録もしない）。呼び出し側で数えても、呼ばれた側が既に食べた
> ものは見えない。**ピンはまさにそのケースで落ちた** — 3 ストアすべてでパラメータ化していたから
> 捕まえられた。私が推論した 2 つだけを覆うピンなら、緑のまま 3 つ目が黙っていた。
> **より鋭い欠陥はヘルパ側**: 読み込み全体の失敗が `[]` を返しており、これは
> **「窓に記録が無い」と区別できない** — しかも **DEBUG** でしか記録していなかった。成功と同じ値を
> 返して失敗を伝える関数は、例外を投げる関数より悪い: **assert できる観測量が無い**。ヘルパは行ごとの
> 捨て数と読み込み全体の失敗（パスを名指し）を報告するようになった。**変異 8/8**（3 ストアの各カウンタ・
> ヘルパの行ごとカウンタ・ヘルパの外側の降格・欠測時の警告・健全ストアでの無条件警告・フォールバックの
> WARNING 昇格・メッセージから件数を落とす）、対照緑、**2 ファイル**をバイト単位で復元（`sha256` 一致）。
> 欠測時は黙り、フォールバックは DEBUG のまま — どちらも**非空虚対照**として固定した。
> ⚠️ **自作スキャナの偽陽性**も 1 件見つけた: `settings/store.py::import_json` は `return <empty>` として
> 検出されたが、実際は `[f"Invalid settings JSON: {e}"]` を返す — **AST の形では空リテラルと
> エラーリテラルを区別できない**。スキャナの被覆は主張であり、当たりは読んで検証する。
> **AI Server は 2110 → 2123 passed**（実測 404.81 秒、collected **2131**、
> `-m "not egress"` = **1809 / 7 / 315**）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、
> deselected 1803 → **1816** — 新 13 本は非 egress）。**派生値**「追加分」は **156 → 169**
> （`2131 − 1962` collected、`1816 − 1647` deselected）。

> **同日 27 度目（通知設定 7 フィールドの唯一の読み手が死んだコードの中にあり、それでも検出器は「読まれている」と判定する、2026-10-04）**: **+23 = 新ピンちょうど**
> （`tests/test_notification_settings_are_read_only_by_dead_code.py`）。前サイクルの「族の中の非対称」を通知パッケージへ
> 広げ、**測定で絞り込んだ**: *クラス*水準の事実は既に `docs/feature-catalog.md` §8 に記録済み（`NotificationRouter`・
> 6 チャネル・`OsNotificationProvider` が宣言のみ、§7 は `send()` がファンアウトしないと書く）なので、新しいのは
> **設定水準の帰結と検出器の沈黙**である。
> `src/` の全モジュールを `ast` で走査すると、**構築される通知クラスは `NotificationManager` ただ 1 つ**
> （`runtime.py:1071` が `NotificationManager(event_manager=event_manager)` とするだけ）。よって
> `NotificationSettings` の 7 フィールド（`approval_notification_enabled` / `support_suggestions_enabled` /
> `daily_briefing_notification` / `error_notification` / `quiet_hours_enabled` / `quiet_hours_start` /
> `quiet_hours_end`）の読み手は `NotificationPreferences._load_from_settings` と
> `QuietHoursManager._load_from_settings` の 2 つだけで、どちらのクラスも**誰も構築しない**。所有する router も
> 未構築で、しかも `QuietHoursManager()` を**引数なしで**作るので `settings_store` が `None` のままになる
> （`if not self._settings: return`）— **二重に死んでいる**。クワイエットアワーは `_enabled` 既定 `False` のまま
> 永久に無効。ところが `tests/test_ineffective_flags.py` の layer 1 は**フィールド名のテキスト一致**なので、
> **死んだコード内の参照も読み手と数え**、この 7 つを「読まれている」と判定して **unread マップが空のまま緑**になる —
> ユーザーが設定でき、`config/settings.json` に載り、`docs/settings.md` §7 に説明があるのに。
> **対照 2 つ**（「読まれない」は**壊れた読み手でも真**なので）: ① store を渡せば両クラスとも設定を尊重する
> ② 読み取りサイトの走査は非空虚で**スコープも帰属する**（生きた対照フィールドの `(module, class.method)` を名指し）。
> ⚠️ **変異が 1 つ生き残り、それはピンではなくハーネスだった**: 対照②の初版は「死んだ集合の外に読み取りが
> 1 つでもある」だけを assert したので、生きた 2 つの読みの**片方**を `getattr(..., "external_llm_allowed")` に
> 書き換える変異が緑のまま通った — **集合の任意の元で満たせる条件は、元を 1 つ消しても気づけない**。期待サイトを
> 名指しする形に直した。読みは**最内の `class.method`** に帰属させる（ファイル水準の検査は、そのファイルが
> 死んだクラスしか含まなくても等価ではない — `preferences.py` に生きたモジュール水準の読み手を足す変異 M10 は
> **スコープ水準の assert だけ**が捕まえる）。**変異 12/12**（対照緑、7 ファイルをバイト単位で復元、`leftovers=[]`）。
> 記録: `DELEGATION.md` §4 項目 35（router の配線は**挙動変更** — クワイエットアワーが実際に延期を始め、
> 外部チャネルが egress gate 越しに送信を試み始め、spam 抑制と監査が効き始める）、`feature-catalog.md` §9 に 4 行、
> `docs/notification-gateway.md` に日付付き警告ブロック（Quiet Hours / Preferences / Safety の各節が
> 「動いている」と書いており、**Safety 節は同じ文書の 22-24 行目と自己矛盾**していた）。
> **AI Server は 2123 → 2146 passed**（実測 379.23 秒、collected **2154**、
> `-m "not egress"` = **1832 / 7 / 315**）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、
> deselected 1816 → **1839** — 新 23 本は非 egress）。**派生値**「追加分」は **169 → 192**
> （`2154 − 1962` collected、`1839 − 1647` deselected）。
> ⚠️ **計測の罠（再発しやすい）**: 最初の全体実行は `2145 / 8` を報告し、2 つのマーカー実行は
> `314 / 1 / 1839` と `1832 / 7 / 315` を報告した — **1 本足りない**。原因は**全体実行が走っている最中に
> ピンを書き換えた**ことで、その実行は 22 本版を収集していた。egress と非 egress は収集を**分割**するので
> `egress + 非 egress == 全体` が成り立たねばならない。**成り立たないときは、スイートより先に計測の入力を疑う。**
> `--collect-only` が裁定した（3 つとも 2154）。

> **同日 28 度目（操作タイムラインの 4 つの無言の読み込み失敗が名乗るようになった、2026-10-04）**: **+13 = 新ピンちょうど**
> （`tests/test_operation_timeline_failures_are_named.py`）。`web/ui_overview._operations` は 3 つの源
> （OperationStore / 監査グループ / 自律実行ログ）を併合し、**それぞれが失敗時に「不在」を返していた** —
> 結果はクラッシュではなく**静かな降格**で、しかもフォールバックが描き続けるので、壊れた読み込みと
> 「まだ 1 件も無い」が**外から区別できない**。4 箇所が原因（例外型 + メッセージ）と帰結を名乗るようにした:
> ① store（`operation_store.list_recent`）② 監査グループ（`audit_manager.list_groups`）
> ③ 自律実行ログ（`_autonomous_logs` の包括ハンドラ）④ 1 層下の `OperationStore._load`
> （読めないファイルは**空のキャッシュ**を残し、捨てた行は**単に「無い」**）。
> **正当な不在は黙ったまま**にした — ループ未設定・ログ未作成の 2 つで、**ピンがそれを assert する**
> （さもないと警告が雑音になり、assertion の方が空虚になる）。**推論ではなく実測した帰結**:
> `_autonomous_logs` は `_json.loads` を**行ごとに守っていない**ので、**解析できない 1 行がサイクル履歴全体を捨てる**
> （実測: 良い 2 行 + 壊れた 1 行 → `{"cycles": [], "count": 0}`）。これは**挙動変更**になるので
> `DELEGATION.md` §4 項目 36 として**記録のみ**（ピンは現状を固定し、直すときは意図的にピンを動かす）。
> **変異 9/9 捕捉**（M1〜M5 = 5 つの警告の除去、M6〜M8 = **対照の劣化** — 正当な不在に警告を足す／
> 正常時に警告を出す、M9 = 行ごとの寛容化）、対照緑、**2 ファイルをバイト単位で復元**、`leftovers=[]`。
> ⚠️ **M9 の anchor が最初 0 件だった**（本文のインデントを 20 と誤認、実際は 12）— **ハーネスの欠陥**であって
> ピンの弱さではない（直して 9/9）。
> **AI Server は 2146 → 2159 passed**（実測 429.51 秒、collected **2167**、
> `-m "not egress"` = **1845 / 7 / 315**）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、
> deselected 1839 → **1852** — 新 13 本は非 egress）。**派生値**「追加分」は **192 → 205**
> （`2167 − 1962` collected、`1852 − 1647` deselected）。**3 つの実行は厳密に整合**:
> `1845 + 314 = 2159`、`7 + 1 = 8`、`315 + 1852 = 2167`。
> ⚠️ **掃討でサイクル 10 の写しが 2 つ腐っていたのを見つけた**: 通知ピンは強化で **22 テスト / 変異 9 → 23 / 12**
> になったのに、`DELEGATION.md` §4 項目 35 と `docs/notification-gateway.md` が**古い数を持ったまま**だった
> （§5 と本注記だけが追随した）。**数を動かす強化は、その数を持つ写しを全部掃かないと終わらない。**

> **同日 29 度目（壊れた `settings.json` が出荷設定を無音で捨てていた、2026-10-04）**: **+9 = 新ピンちょうど**
> （`tests/test_settings_store_load_failures_are_named.py`）。`SettingsStore._load` は `__init__` から 1 回だけ走り、
> 失敗すると**無言で**組み込み既定に差し替えていた（`settings/store.py` には**ロガーが 1 つも無かった**）。
> `runtime.py:898` は**出荷** `config/settings.json` を指すので、壊れた／綴りを誤ったファイルは
> **出荷設定が効いていない状態**を無音で作る — 例外もログも残らない。**メッセージを書く前に測った**:
> 既定と出荷設定の差は**ちょうど 3 鍵で全部 egress 許可**（`privacy.egress_allowed_hosts` は `[]` vs
> `['api.typesafe.ai']`、`external_egress_allowed` / `external_llm_allowed` は `False` vs `True`）なので、
> フォールバックは **fail-closed**（何も開かない＝単一制約は危険に晒されない）だが、ゲートが全ての外部宛先を
> 拒否しクラウド LLM プロファイルが降格する。**工場を駆動して両方を確認**: 既定ではゲートが
> `egress deny … reason=external egress is disabled` を出し、出荷設定のプロファイルは**許可**されていて
> Mock に落ちるのはローカル Ollama が居ないからだけ（＝「Mock に落ちる」を結論にしなかった）。
> 同じファイルの `import_json` は**鏡像の欠陥**を持っていた — **1 つの `try` が解析と適用の両方を包む**ので、
> **ディスク**の失敗が `Invalid settings JSON` と読める（固定メッセージ型の再発）→ 2 つに分けた。
> **変異 8/8**（本ピン = M1 `_load` の警告を除去・M3 フォールバックが既定でなくなる・M4 既定が狭い側でなくなる・
> M5 `import_json` を 1 つの `try` に戻す、**対照の劣化 4 つ** = M2 正常時に警告・M6 解析エラーを適用失敗として報告・
> M7 `update` で先に永続化・M8 適用失敗を握り潰す）、対照緑、
> **2 ファイルをバイト単位で復元**、`leftovers=[]`。⚠️ **M3 の anchor が最初 2 件だった**
> （`self._settings = create_default_settings()` は `__init__` と `_load` の両方にある）— **ハーネスの
> anchor 不足**であってピンの弱さではない（anchor を伸ばして 8/8）。
> ⚠️ **第 2 の欠陥は測って記録し、直していない**: `update` は `_persist()` の**前**に `self._settings` を
> 代入するので、永続化の失敗はメモリだけ変えてディスクを変えない（実測: 前 `False` → `PermissionError` →
> 後 `True`）。先に永続化すると値が動く時点が変わる＝**挙動変更**なので `DELEGATION.md` §4 項目 37、
> ピンは現状を固定する。
> **AI Server は 2159 → 2168 passed**（実測 409.85 秒、collected **2176**、
> `-m "not egress"` = **1854 / 7 / 315**）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、
> deselected 1852 → **1861** — 新 9 本は非 egress）。**派生値**「追加分」は **205 → 214**
> （`2176 − 1962` collected、`1861 − 1647` deselected）。**3 つの実行は厳密に整合**:
> `1854 + 314 = 2168`、`7 + 1 = 8`、`315 + 1861 = 2176`。

> **同日 30 度目（`mind/` の 8 つの無言の読み込みを名指しできるようにした、2026-10-04）**: **+34 = 新ピンの 34 ケースちょうど**
> （`tests/test_mind_persistence_failures_are_named.py`）。`aegis_ai/mind/` の 8 モジュール
> （`desire`・`emotion`・`goals`・`identity`・`layered_emotion`・`mood`・`personality`・`social_intelligence`）は
> **同一の** `_load` を持ち、`except (json.JSONDecodeError, OSError): pass` で壊れたファイルを
> 「まだ 1 件も無い」と区別できなくしていた（`goals.py` だけ `KeyError` も捕捉）。この族には
> **ロガーが 1 つも無かった**（`affect_system.py` にだけあり、それは `_load` を持たない）。
> **8 つともパス・例外型・帰結を名乗る**ようにした。
> ⚠️ **境界も測って固定した** — 一族の「無言」は**例外型**で決まっており、ファイルが使えるかどうかではない:
> `json.loads` が**通ってしまう**行（`123` のような非オブジェクト）は次の `last.get(...)` で落ちるので、
> **8 つすべてで `__init__` から `AttributeError` が出て、警告は 0**（実測）。`123` は `{"a": 1` と
> 同じくらい使えないのに、片方は既定へ落ちて片方は構築を止める。**露出は場所で変わる** — 生きている 2 つの
> 構築点（`runtime.py:995` の `Identity`・`runtime.py:1669` の `AffectSystem`）は**どちらも try の外**で、
> 3 つ目は**同じ呼び出しを DEBUG で握り潰す**（`llm/memory_context.py:323`）。**挙動を変える**ので
> `DELEGATION.md` §4 項目 38 として記録のみ。
> ⚠️ **族の範囲も測って固定した**（`import` ではなく**構築**で測る）: 11 モジュールのうち `mind/` の外で
> 構築されるのは **`Identity` だけ**。`Mood`・`Personality`・`LayeredEmotion` は `AffectSystem` 経由で生き、
> `Desire`・`Emotion`・`GoalManager`・`SocialIntelligence`（＋`priorities.py` の `PriorityEngine`）は
> **どこでも構築されない** — `Emotion`・`GoalManager` を import するのは `reflection_loop.py` だけで、
> **その `reflection_loop.py` 自身が構築されない**（2 次の死）。うち 2 つは生きたクラスと**同名**
> （`mind/desire.py::Desire` vs `desire/desire_system.py::DesireSystem`、`mind/social_intelligence.py::SocialIntelligence`
> vs `social/intelligence.py::SocialIntelligenceSystem`）なので、次に「自然な」import を書いた者は
> **死んだ方**を受け取る。`mind/social_intelligence.py` はさらに**キーワード一致**（`"too long" in lower_feedback`）
> を実装しており、AGENTS.md の中核規則に反する — **未配線なので今は不活性**（live な `social/intelligence.py` は
> 同じ綴りを持たない、実測 0 件）。すべて §4 項目 39 として記録のみ。
> **`docs/mind-layer.md` の「ContextBuilder Integration」が実行不能と判明して訂正** — 例は
> `affect_system=` / `social_intelligence=` を渡すが `ContextBuilder.__init__` は**どちらも取らず**
> （実測 `TypeError: … unexpected keyword argument 'affect_system'`）、`ctx.affect` / `ctx.social` も
> **存在しない**。本番の `ContextBuilder(` 呼び出しは `src/` に**1 つだけ**（`runtime.py:997`）で、
> mind 族から渡すのは **`identity` だけ**（`desire=` / `emotion=` / `goal_manager=` は**受け取れる**のに渡されていない）。
> **変異 8/8**（本ピン = M1 `Mood` の警告を除去・M2 メッセージからパスを落とす・M3 例外名を落とす・
> M6 `except Exception` に広げて非オブジェクト行を握る、**対照の劣化 3 つ** = M4 正当な不在に警告・
> M5 読めるファイルに警告・M8 `AffectSystem` の連結を切る）、対照緑、**2 ファイルをバイト単位で復元**、
> `leftovers=[]`。**対照 4 種**（欠測は黙る・健全は黙る・壊れた行は名指す・非オブジェクト行は投げる）。
> ⚠️ **自作の構造テストを 1 回間違えた**: `ast.Expr` を除外してから「本体が `pass` だけか」を問うたので、
> **裸の `logger.warning(...)` 文そのもの（＝`ast.Expr`）が全部「無言」と判定された**（8 件の偽陽性、実測）。
> 除外をやめて 34 passed。
> **AI Server は 2168 → 2202 passed**（実測 494.75 秒、collected **2210**、
> `-m "not egress"` = **1888 / 7 / 315**）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、
> deselected 1861 → **1895** — 新 34 本は非 egress）。**派生値**「追加分」は **214 → 248**
> （`2210 − 1962` collected、`1895 − 1647` deselected）。**3 つの実行は厳密に整合**:
> `1888 + 314 = 2202`、`7 + 1 = 8`、`315 + 1895 = 2210`。

> **`SpontaneousObservation` は 2227 → 2239 passed**（実測 466.57 秒、collected **2247**、`-m "not egress"` = **1925 / 7 / 315**。**egress は不変**（315 マーカー / 314 passed / 1 skipped、deselected 1920 → **1932** — 新 12 本は非 egress）。**派生値**「追加分」は **273 → 285**（`2247 − 1962` collected、`1932 − 1647` deselected）。**3 つの実行は厳密に整合**: `1925 + 314 = 2239`、`7 + 1 = 8`、`315 + 1932 = 2247`。

> **`CuriosityExploration` は 2209 → 2227 passed**（実測 502.43 秒、collected **2235**、`-m "not egress"` = **1913 / 7 / 315**。**egress は不変**（315 マーカー / 314 passed / 1 skipped、deselected 1902 → **1920** — 新 18 本は非 egress）。**派生値**「追加分」は **255 → 273**（`2235 − 1962` collected、`1920 − 1647` deselected）。**3 つの実行は厳密に整合**: `1913 + 314 = 2227`、`7 + 1 = 8`、`315 + 1920 = 2235`。

> **AI Server は 2202 → 2209 passed**（実測 458.78 秒、collected **2217**、`-m "not egress"` = **1895 / 7 / 315**）。**egress は不変**（315 マーカー / 314 passed / 1 skipped、deselected 1895 → **1902** — 新 7 本は非 egress）。**派生値**「追加分」は **248 → 255**（`2217 − 1962` collected、`1902 − 1647` deselected）。**3 つの実行は厳密に整合**: `1895 + 314 = 2209`、`7 + 1 = 8`、`315 + 1902 = 2217`。
> **`AutonomousLoop` の 4 つの握り潰しを名指しできるようにした**（`test_autonomous_loop_failures_are_named.py` — 4 箇所とも**失敗**を**不在／既定値**に変えており、どれも無言だったので**肯定的な事実と区別できなかった**: `_priority_obligations` → `[]`（「未解決の務めは無い」）／`_current_interruption_cost` → `0.15`（**「AgentState 未接続」の既定値と同じ数**）／`_manifest_for` → `None`／`_load_recent_history` → `[]` — 呼び手が**リテラル文字列** `"Autonomous execution history: no actions executed yet. First run."` として**計画 LLM の文脈に注入**する。**戻り値は不変**、兄弟 2 つは**意図的に無言**として許可リスト、**変異 7/7** ＋ 変異なし対照、原ファイルをバイト単位で復元。

> **`PROJECT_STATUS_REVIEW.md` の引用にも +18 の腐りがあった — 登録簿の写しは 4 つ目（2026-10-05）**: `runtime.py` の行番号を名乗る引用 **17 箇所**（**12** の異なる写像）を 1 件ずつ測り直した。すべて **+18** — サイクル 19 が `runtime.py` に入れたコメントが、それより下の行を 18 行ずらした: `:880`→`:898`（`SettingsStore(`、L14・L547）・`:977`→`:995`（`Identity(`、L14・L584）・`:979`→`:997`（`ContextBuilder(`、L14・L600）・`:1053`→`:1071`（`NotificationManager(`、L14・L486）・`:1651`→`:1669`（`AffectSystem(`、L14・L584）・`:884`→`:902`（`AuditLog(path=…/audit.jsonl)`、L922）・`:1020`→`:1038`（`SemanticMemory(`、L928）・`:1009`→`:1027`（`semantic_memory` の明示 import、L929）・`:1653`→`:1671`（`AssociationMemory(`、L926）。**同じ写像は既に 2 文書で直っていた**（サイクル 24 が `DELEGATION.md`、27 が `AGENTS.md`）ので、これは**4 つ目の写し** — 「1 箇所直した」は掃討ではない。加えて `context_builder.py:203`→`:206`（`list_recent_events()`、L927）・`manager_routes.py:361`→`:371`（`get_stats()`、L926 — 361 は隣の `/api/memory/search` の呼び出し）・`factory.py:38`→`memory/factory.py:38`（L928 — 同名が `llm/` にもあり、`ChromaSemanticMemory` を構築するのは後者）。
> ⚠️ **同じ文書の中で腐り方が違う。** L62 の 2 件（`:1586`・`:1618`）は **+67** で、しかもこの行は「訂正しなかった記述」として `AGENT_PROGRESS.md:820` の `runtime.py:1618` を**正しいと記録している**（スイート数 **1734** の時代の行 — 現在 2287）。行は書かれた時刻を運ぶので、**行ごとに測る**。L925 の `:906`/`:917`/`:909` は**修正前の欠陥叙述**（実測: 修正前の `def presentation_stream` は 906、`subscribe` は 917、`queue.Queue()` は 909 / 現在は 911・940・916）なので、**歴史的な番号として意図的に残した** — 付け替えると叙述が偽になる。
> **同じ走査で「空白行に着地する引用」を全部見た（2026-10-05）**: 修正は **2 件** — `backup/retention.py:49`→`:60`（L63・§5.15。`episodic_retention_days`→`max_age_ms` の変換は 60-61 にあり、49 は空行。しかも**同ファイルの docstring が「(line ~49)」と自分で古い番号を書いていた**ので、その写しも直した）と `test_ineffective_flags.py:274`→`:273`（L76。`pytest.skip(f"recorded: ...")` は 273、274 は空行）。**残りは意図的に据え置いた**: `autonomous_loop.py:3065-3066`・`:3068`（L54・L995・L1559）は**欠陥叙述**で、しかもその対象（既定値 0.5 を埋めていたこと）は**その後 `_expected_usefulness` に置き換えられて直っている**（`autonomous_loop.py:902` の docstring が "used to read" と記録）— 番号は当時のもの。`capability_catalog.py:379` ほかは**「下表は実施前の測定値」と明示された表**の中。`egress/startup.py:59-76` は**範囲の開始が空行**なだけ（範囲は主張を覆っているので据え置きが正しい）。`test_forced_gate_stays_retired.py:61-65` も同じ扱いにしたが**これは誤り** — その範囲は同じコメントの**別段落**（`request`/`list` の説明）を指していた（**→ サイクル 36 で `:66-70` に訂正**、§9）。


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

> **2026-09-30 18:04 に再発した（この日の 10 回目の push で 1 回）** — 症状は記録どおり:
> `.git/refs/remotes/origin/` が**ディレクトリごと**消え、**push と無関係な兄弟 ref の `main` と
> `origin/HEAD` も道連れ**になった（`git for-each-ref refs/remotes/` が空、`packed-refs` は無い）。
> **新しい観測**: `.git/logs/refs/remotes/origin/` は**残っており**、追跡 ref の reflog は
> **push 自身が書いていた**（mtime 18:04:27、内容 `update by push`）— つまり
> **reflog は着地し、ref は着地しない**。**壊れたのは `refs/` 側だけで `logs/` 側ではない。**
> **引き金は依然として未特定**（同じコマンドが 9 回は成功した）。復旧は上記の手順で完了
> （3 ref を復元、`git status` の `[gone]` は解消）。
>
> **2026-09-30 19:52 に 2 回目の再発 — 今度は `fetch` で**（18:04 は push）。`git fetch origin
> cf-grpc-and-goal-hygiene` は `* [new branch] … -> origin/cf-grpc-and-goal-hygiene` と**成功を表示し**、
> 追跡 ref の reflog も 19:52 に**書かれた**（2,957 バイト）のに、**`.git/refs/remotes/origin/` は
> 作られなかった** — 18:04 と**同じ署名**（reflog は着地、ref は着地しない）。**新しい観測 2 つ**:
> ① **push だけでなく fetch でも起きる** — fetch は読み取りに見えるので「安全な方」と書いていた
> （同日の成功例を根拠にしていた）が、**その前提は反証された**。② **被害が軽い回がある** — 今回は
> `refs/remotes/` ディレクトリ自体は残り、**中身が空**だった（18:04 はディレクトリごと消えた）。
> よって**「ディレクトリが在るか」を見る検査は不十分**で、`git rev-parse refs/remotes/origin/<branch>`
> のように**ref を解決して**確かめる必要がある。**`refs/heads/` と HEAD は無傷**、`ls-remote` は
> 一貫して正しかった — **リモートは常に正しく、欠けていたのはローカルキャッシュだけ**。
> 復旧は上記の手順で **3 ref**（`cf-grpc-and-goal-hygiene` / `main` / `origin/HEAD`）を復元した。
> **推奨の記録先は skill `aegis-verify-and-test` §1.0f の push 節**（そちらに検査と診断を追記済み）。
>
> **2026-09-30 19:58 — 機序を絞り込んだ。「間欠的」ではない**（同日 3 回目の実測。18:04 と 19:52 の
> 記録は「この日の 10 回の push で 1 回」と書いていたが、**再現手順が確定した**）:
> **このリポジトリでは `git fetch origin` が `refs/remotes/origin/` 配下のファイルを毎回すべて消す。**
> 対照実験（すべて同一バイナリ `git 2.55.0.windows.3` / PortableGit）:
>
> | 操作 | `refs/remotes/` のファイル数 |
> |---|---|
> | 何もしない（10 秒放置） | 2 → 2（消えない） |
> | `git status` / `for-each-ref` | 2 → 2（消えない） |
> | `git ls-remote --heads origin` | 2 → 2（消えない） |
> | `git gc --auto` | 2 → 2（消えない） |
> | **`git fetch origin`** | **2 → 0（毎回）** |
> | `git fetch --no-auto-gc`（`gc.auto=0`・`maintenance.auto=false` 済み） | **2 → 0** |
> | `git -c remote.origin.fetch= fetch origin`（追跡 ref を 1 つも書かない空 refspec） | **origin の 2 件が消える** |
> | 別リポジトリ（`git init` + ローカル remote）で `git fetch` | 2 → 2（**正常**） |
>
> **fetch は「管理していない」ref も消す** — `refs/remotes/origin/HEAD` と、私が作った
> `refs/remotes/origin/nested/deep` も消えた。逆に **refspec の外にある `refs/remotes/probe` は残った**。
> よって消えているのは **`refs/remotes/origin/` という名前空間まるごと**で、ref の**更新**ではない。
> しかも **fetch は `= [up to date]` と表示して 1 つも書いていないのに消える**（`GIT_TRACE=1` で確認 —
> 追跡 ref の書き込みは実行されず、`git rev-list … --exclude-hidden=fetch` だけが走る）。
> **除外できた原因**: フック無し（`.git/hooks/` に非 `.sample` は 0 件、`core.hooksPath` 未設定）、
> ジャンクション無し、`objects/info/alternates`・`commondir` 無し、`fetch.prune` 無し、
> `.git/config` は正常（`safe.directory=*` 以外のグローバル設定も無し）。
> **同一バイナリが別リポジトリでは正常**なので、**原因はこのリポジトリの `.git/` 側にある**。
> `.git/` には git 以外のツールの痕跡がある（`.git/cursor/`、`.git/refs/codex/turn-diffs`）。
> **結論は変わらないが頻度の前提が変わる**: `fetch` も `push` も**毎回**追跡 ref を失うものとして扱う。
> `git ls-remote` が真実、`git status -sb` の `[gone]` は意味を持たない、復旧はファイルを直接書く。
> **リモートは一貫して無傷**（失われるのはローカルキャッシュだけ）。**引き金は fetch と確定、機序は未確定。**
>
> **リモート名はフラットに移行済み**（2026-09-30 — PR が無く既定ブランチが `main` であることを確認した上で
> 入れ子のリモートブランチを削除し、フラットなブランチを `--set-upstream` で push した）。
>
> **2026-10-01 追記 — 09-30 の「`update-ref` はどの深さでも成功した」は再現せず、そして上の 19:58 の表は
> すでに深さを指していた。** 同日、`refs/` 下の**深さ ≥ 2** の ref を `git update-ref` で書くと
> **25/25 回**、`rc=0`・stderr 空のまま**ref を書かず、囲むディレクトリを削除**した
> （`refs/remotes/origin/<name>` / `refs/remotes/other/<name>` / `refs/heads/<dir>/<name>` /
> `refs/remotes/origin/a/b`）。**深さ ≤ 1** は **15/15 回生存**（`refs/heads/<flat>` /
> `refs/remotes/<remote>` / `refs/<name>` / 新規作成した親の `refs/newdir/<name>`）。
> **制御で除外済み**: 外部の監視者（直後および 2 秒後で既に消えている。かつ
> **同一マシン・同一バイナリ・同一設定の新規 `git init` リポジトリは深さ 2 を正常に書ける**）、
> バイナリ差（PortableGit 1.2.0 とシステム Git for Windows は**どちらも `2.55.0.windows.3`** で両方失敗）、
> 新規作成か更新か（**既存 ref も死ぬ**）、親ディレクトリが新規か（深さ 1 の新規親は生存）、
> reflog の有無（`logs/refs/remotes/origin/` を退避しても不変）、
> フック / `core.fsmonitor` / `core.hooksPath`（未設定、`repositoryformatversion=0`）。
> **上の 19:58 の表は、実は同じ結論を含んでいた** — `refs/remotes/origin/HEAD`（深さ 2）と
> `refs/remotes/origin/nested/deep`（深さ 3）は消え、**`refs/remotes/probe`（深さ 1）だけが残った**。
> つまり **`fetch` も `update-ref` も、深さ ≥ 2 の ref を壊し、深さ ≤ 1 は壊さない** — 引き金は
> コマンドではなく **ref の形**である。**別リポジトリは正常**という 19:58 の対照も、10-01 の対照と
> **一致**する。**結論**: 失敗は **git の挙動ではない** — **このリポジトリの `.git` 固有**。
> **機序は依然未特定**、09-30 の反証も未説明なので**どちらの規則も確定していない**。**実務上の結論は
> 変わらない**（入れ子 ref は**ファイルへ直接書く**）が、**フラット名が効く理由**が付いた —
> `refs/heads/<flat>` は**深さ 1**、`refs/remotes/origin/<flat>` は**深さ 2**。
> **正典は skill `aegis-verify-and-test` §1.0**（表と制御はそちら）。**コードは不変** — テスト数は
> `f58d685` の **1905 / 8 skipped** のまま。

> **未検証の手がかり（2026-09-30 に更新）**: 以前ここに書いていた「腐った reflog
> `.git/logs/refs/heads/cursor/…`」は**手がかりではない**と判定した — **破壊せずに試せない唯一の
> 記録**（失われたコミットの SHA とメッセージを保持している）であり、**存在しない ref の reflog を
> 書く経路が無い**ので因果の道が無い。代わりに残る手がかりは **`.git/` の中を git 以外のツールが
> 読み書きしている**こと: `.git/refs/codex/turn-diffs/`（**空**、中身が変わったのは
> **2026-09-29 18:54** ＝ 消失の検知と同時刻）、`.git/cursor/crepe/`（20 MB）、
> `.git/mimocode-project-id`。**うち 1 つは ref の名前空間を書く。** 実測と除外は
> `INCIDENT_2026-09-29_git-object-loss.md` §3 の 2026-09-30 追記、運用上の手順は skill
> `aegis-verify-and-test` §1.0。**reflog は復旧の手段なので prune しない。**

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
| **Egress Gate（唯一の制約）** | ✅ 強制（**2026-09-30 に再定義**） | `ai-server/src/aegis_ai/egress/{gate.py,permissions.py,startup.py}`、25 モジュール配線、10 実効点、起動時 fail-closed、CI 床 160（実測 **320 marked / 319 passed / 1 skipped**）、**mutation 証明**（壊すと **76 failed**）。**再定義の内容**: 禁止されるのは「**許可の無い**ユーザー情報の外部送信」で、**接続自体は可**（旧: deny-all）。**許可の 2 経路を実装済み**: ①常設設定（マスタスイッチ＋目的別フラグ＋allowlist。**出荷 `settings.json` はマスタスイッチを開き、`egress_allowed_hosts` に `api.typesafe.ai` **のみ**を許可** — 2026-10-03）②**ユーザーが特定の宛先について与えた許可**（`egress/permissions.py` が confirmation ストアを読む — ⚠️ **未配線**: `src/` に構築点が 1 つも無く、composition root も `permission_source` を渡さないため実行時は常に grant 無し。`(host, purpose)` 完全一致・**ワイルドカード無し**・期限内のみ）。ゲートは**読むだけで問わない**ため、退職済みの強制ゲートは退職のまま（`test_forced_gate_stays_retired.py`）。ユーザー情報を運ばない要求は許可不要（既定は `carries_user_information=True`＝厳しい側） |
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
> まま残っていた（§0 と §P1 の表だけが追随 — **型 9**）。**残る穴は 3 と 4 の 2 つ**だった。
>
> **2026-10-03 更新: 穴 3・穴 4 とも閉じた。** 穴 4 は **2026-10-01**（オーナーが (A) を選び
> `ConfirmationRequest.desire` を追加して配線 — 下の 4）、穴 3 は **2026-10-03**（オーナー定義:
> **判断用 LLM が判断し、ちょくちょくユーザーに確認する** — 下の 3）。**穴 3 は同日、定義だけでなく
> 配線も済んだ** — `_create_autonomous_loop` が `BurdenMetric` を構築し、`AutonomousLoop._run_loop`
> の周期フックが `ai-server.confirmation.request` でユーザーに問い、`last_burden_ask_ms` を
> `loop_state.json` に永続化する（`DELEGATION.md` §4 項目 8）。⚠️ **配線は 2 回「動かない形」で
> 書かれかけた** — ① 判断 profile が `decision`（＝ allowlist に拒否され Mock へ落ち、
> `is_trustworthy=False` なので**決して聞かない**）② ask の `side_effects` が list（＝能力自身の
> `input_schema` が `string` を宣言しているので broker が `VALIDATION_DENY` で拒む）。**どちらも
> ピンは緑のまま**で、`declared` と `resolves` を別々に測って初めて見えた。

1. ~~**`interruptibility` が未実装**~~ → ✅ **解消**（P1-6 `df1bb70`）。`InterruptionController.decide`
   が `net = benefit × P(receptive) − cost` の期待効用で判断し、判断ログに内訳を載せて**報告値から
   符号を再計算できる**ことを assert する。宣言された規則（emergency_stop・例外カテゴリ・critical・
   静穏時間・proactive 不許可）は**ハードゲートのまま**でモデルを経由しないことをテストで固定。
   人間向けの面は P1-1（`768bb60`）。**残る宿題は 1 つ**（**2026-10-01 実測で 2 → 1**）—
   ~~割り込みコストの写像が 2 つに分かれている~~（**B-11 の順序違反は 2026-09-30 に修正済み**:
   コスト表は `_RECEPTIVITY` が下るはしごを上る。**写像を統合しない**のが正しい — 消費者も軸も違う）。
   ~~自律的な結果の `expected_usefulness` が定数~~（**B-17 も 2026-09-30 に修正済み** —
   `_expected_usefulness(task)` が圧力を既存変換 `min(1.0, pressure / 10.0)` で正規化し、
   `:3381-3382` で `_current_interruption_cost()` と並んで渡される）。
   **残るのは B-11 の構造面だけ** — `_current_interruption_cost` が素の `.get(kind, 0.2)` で終わるので、
   **新しいレベルが `batch_later` より安く読まれる**（`_RECEPTIVITY` 側は discovery+等式で守られている）。
   **残余の罠**: `PresentationRoutingContext` の既定は両方 0.5 のまま。`src/` の呼び手はループだけなので
   **本番は直っている**が、新しい呼び手が省略すると空虚な比較が再生成される（ピンが可視化を保つ）。
   ピン: `tests/test_interruption_cost_vocabulary.py`。
2. ~~**事後可視化の UI が無い**~~ → ✅ **解消**（P1-2 `c0c5845`）。
   `web-ui/src/pages/IrreversibilityPage.tsx`（テスト付き）が `GET /api/audit/irreversible` を表示する。
3. ~~**負担量の計測が無い**~~ → ✅ **定義は解消（2026-10-03、オーナー）**。「どれだけ楽になったか」の
   指標は **判断用 LLM（`profile="decision"`）が判断し、ちょくちょくユーザーに確認する** と定義された
   （`docs/burden-metric.md`、`aegis_ai/burden/`、`DELEGATION.md` §4 項目 8）。**`DECISION_DRAFTS.md`
   §B-5 の「既存ログから導出」は採らなかった** — 実測で 3 副指標のうち **1 つ**でしか成り立たない
   （§4.1 / §0.1 の測定行）。⚠️ **未配線** — `src/` に `BurdenMetric` の構築点が **0**（実測）なので、
   実行時にはまだ指標が出ない。配線は composition root とループの周期フック。
4. ~~**成長フィードバックの閉路が切れている**~~ → ✅ **解消（2026-10-01）**（当初の記載は「契約半分は解消 / ① は未着手」）— **訂正 2026-09-30:
   「生産者 0」は誤り。** 生産者は 1 つあり（`reflection_engine.py:90`、`MemoryType.APPROVAL_LESSON`
   を書く）、ただし `approval_decisions` がどこからも渡されないので到達不能
   （`reflect(approval_decisions=...)` は src・tests のどちらからも未指定 → 常に `[]`）。
   **「生産者 0」という結論自体が測定の産物だった** — `decision` という*キー*で grep したので、
   そのキーを書く生産者だけを探していた。*型*（`APPROVAL_LESSON`）で探せば 1 つ見つかる。
   閉路は**「生産者が無い」のではなく「1 つの生産者が 3 通りに壊れている」**: ① 到達不能 ②
   `structured_data["decision"]` を書かない ③ `related_desire` を書かない。
   **②③ は 2026-09-30 に修正した** — 生産者が `_DECISION_REJECTED` と `related_desire` を書き、
   罰則側の 2 つ（`autonomous_loop._recent_failure_penalty`・
   `motivation_arbiter._check_memory_penalties`）が**実際に 0.2 を課す**ことを実測し、変異 **4/4**
   で固定した（`tests/test_forced_gate_stays_retired.py`、§0.1 の台帳行）。
   **ただし閉路は依然として切れている** — 今回の成果は「**切れている場所が呼び出し元 1 箇所だけに
   なった**」ことで、**① は A-11③（引数は残して固定する）の決定どおり触っていない**。
   実害が無いのは**この経路に到達する呼び出し元が無いから**であって、直ったからではない。
   **（2026-09-30 訂正）「① を配線した瞬間に閉路が閉じる」は誤り** — 実測すると、配線しても
   **正しくは閉じない**。理由: 読者 2 つはどちらも `search_memories(related_desire=source_desire)` で
   引き（`autonomous_loop.py:1589`・`motivation_arbiter.py:162`）、ループ側の読者は
   **`source_desire` が空なら即 `return 0.0`**（`:1583`）。`related_desire` に入るのは
   **`reflect()` の呼び出し元が渡す `source_desire`** で、唯一の呼び出し元（`autonomous_loop.py:1228`）は
   **失敗したタスクの `desire`** を渡す。ところが **`ConfirmationRequest` は欲求を持たず**
   （`confirmation/models.py`）、**解決済みの確認を欲求に結びつける機構がどこにも無い** — 実測:
   `store.reject()` は記録を返すだけ（`web/routes/approval.py::_decide`）、`_confirmation()` は
   `request`/`list` のみ、**ループは store を 1 度も参照しない**（`confirmation` の出現 0 件）。
   よって「拒否された確認」をそのまま渡すと、**その質問とは無関係なタスクの欲求に罰則が付く**
   （誤帰属）。正しく配線するには**「確認 ↔ 欲求」のリンクを先に決める**必要がある（どれも契約と
   挙動を変える**製品判断**）。
   **（2026-10-01 実測）`task_id` 案は「死んでいない」— ただし繋がるのは片側だけ。** `task_id` は
   **3 つの名前空間**に現れる: ① **ループは実在の `task_id` を作る** — `TaskManager` のタスクを起こし、
   その metadata に **`autonomous_task.desire`** を書く（`autonomous_loop.py:2716-2753`）。つまり
   **`task_id` → 欲求** の表は**既にある** ② 同じ `task_id` と `source_desire` は実行要求にも渡る
   （`:3067`・`:3072`）③ reflection の `task_id` は reflect 時に合成（`:1228-1229`）で①②とは無関係。
   **繋がらないのは確認側**: `ConfirmationRequest.task_id` は **LLM が自由に渡す値**
   （`core_capabilities.py:832` の `_CONFIRMATION_FIELDS` に含まれ、`:872-875` で `params` から素通し）なので、
   **渡さなければ空・渡しても未検証**。**LLM に loop の `task_id` を知らせる経路も今は無い。**
   **副産物（未配線の発見）**: `AuditEntry` は `task_id` と **`source_desire`** を持ち、
   `AuditManager.log_approval(source_desire=...)` も用意されているのに、**`log_approval` を呼ぶコードが
   `src/` にも `tests/` にも 1 つも無い** — **承認イベントに欲求を載せる配線は設計済みで、繋がれていない**。
   候補は 2 つだった: **(A)** 確認に欲求（または loop の `task_id`）を記録させる。**(B)** 教訓を
   `related_desire` ではなく **`capability_id` で引く** — 確認が確実に持つ唯一のフィールドだが、
   **読者 2 つはどちらも `related_desire` で厳密に引く**ので**読者の問い合わせを変える**＝挙動変更で、
   **意味も変わる**（「この欲求は高コスト」ではなく「この行動を提案するな」を学ぶ）。
   **（2026-10-01 決定・実行）オーナーが (A) を選び、閉路は閉じた。** 実装: `ConfirmationRequest.desire`
   を追加（`confirmation/models.py`）し、LLM が `ai-server.confirmation.request` で渡せるよう
   `_CONFIRMATION_FIELDS` に加えた。ループは **store を読み取り専用で参照**して（`all()` のみ）
   拒否済みの確認を desire ごとにまとめ、`reflect(approval_decisions=..., source_desire=<desire>)` に渡す。
   **値は LLM 供給なのでループ側で実在する欲求集合と照合**し、空・未知は**捨てる**（誤帰属より欠落を選ぶ）。
   同じ拒否を毎サイクル再学習しないよう `_reflected_approval_ids` を state に永続化した（無いと
   `0.2 × 件数` が上限 0.9 まで張り付く）。
   **ピン**: `tests/test_forced_gate_stays_retired.py` に 4 本追加 — 実 desire は両読者に届く／
   未知・空の desire は教訓を作らない／同じ拒否は 1 回だけ／**ループは store を読むだけで答えない**。
   **変異 4/4 捕捉**（各変異が**狙った assertion** を発火させたことまで確認）、原ファイルは sha256 一致で復元。
   **副産物 2 件**: ① `_ALLOWED_IMPORTERS` ピンが新しい import を検出して落ちた（**設計どおり**）②
   **配線時に自分でバグを入れた** — `_create_autonomous_loop` は `_build_runtime` と**別関数**で、
   `confirmation_store` はそこに無い。**全スイートは緑のまま通った**（`autonomous_loop_enabled` が既定
   False で、この関数はテストから一度も実行されない）。ruff の `F821` だけが捉えたが、**CI は ruff を
   走らせていない** → §4 の C-5 項目へ。
   ~~**残る穴は 3 のみ**（① は閉じた）。~~ → **2026-10-03 更新: 穴 3 もオーナーが定義し、同日
   配線も済んだ**ので、**北極星層の穴はもう無い**（`_create_autonomous_loop` が `BurdenMetric` を
   構築し、`_run_loop` の周期フックがユーザーに問う — 上記 3 と `DELEGATION.md` §4 項目 8）。

### 3.2 機能面

| 項目 | 状態 |
|---|---|
| vision のローカル代替 | ✅ **配線済み（2026-10-01 実測）** — `llm.yaml` の `profiles.local_vision` は `http://localhost:11434/v1`（Ollama, `qwen2.5vl:7b`）を指し、`LLMSettingsResolver._LOCAL_PROFILE_MAP` が `vision_observation → local_vision` に remap する。**egress ゲートは止めない** — 解決先がローカルなので `verify_egress_configuration` は `local_llm_readiness: ok`／違反ゼロ（実測）。`llm.yaml` の Aliyun 定義は **cloud 用で、local モードでは使われない**。この行は以前「`llm.yaml` が Aliyun を指したまま／egress が止めるため**視覚機能は実質不可**」と書いていたが、**機制・結論とも誤り**だった（オーナーの「ローカル LLM は追わない」は**運用しない**決定であって、配線の不在ではない）。実運用には Ollama が `qwen2.5vl:7b` を配信している必要があり、未配信なら他の全プロファイルと同じく **Mock に縮退**する。ピンは `tests/test_vision_row_matches_the_local_profile.py`。⚠️ **2026-10-03 追記（composition root で実測）**: `llm.yaml` は **`mode: "cloud"`** になった（L1 を JEV に届かせるため, `f8e0b06`）ので、この remap は**出荷構成では発火しない** — `vision_observation` は宣言どおり **Aliyun**（`qwen3-vl-flash`, `…maas.aliyuncs.com/compatible-mode/v1`）に解決し、その host は allowlist に無いためゲートが拒否し、**実行時は Mock に縮退**する（実測: resolver `_mode=cloud`、`verify_egress_configuration` が同 host を「declared but not permitted → degrade to Mock」と列挙）。Ollama を配信しても `mode: "local"` に戻さない限り届かない。この行の ✅ は「**local モードなら**局所代替が存在する」という主張で、その意味では今も真 |
| gRPC TLS | ❌ **未配線**（2026-10-01 実測）— `aegis_ai/security/` パッケージ全体がパッケージ外から import されておらず、`add_secure_port` を呼ぶ生きた経路は無い（**gRPC は平文**）。ローカル hop は Tailscale / プライベート網の境界で守る。記録は `DELEGATION.md` §4 項目 14、ピンは `tests/test_security_package_stays_unwired.py` |
| Room 実機 | ❌ `UNCONFIGURED/DISABLED`（Orange Pi の実プロバイダ待ち）。`GetEnvironment` は**ハードコード fixture を返す**が、**そのことを応答に明示する**（2026-10-01）— `Status.message` が「hardcoded fixture … constants rather than measurements」を返し、`code=0` のまま（**注記であってエラーではない**）。**偽の環境を本物として見せない**。ピン 2 本: `room-server/tests/test_room_server.py`（fixture を名乗ること／値が実際に定数であること）と `ai-server/tests/test_room_integration.py`（`Status.message` が client の `_status_dict` を通ってエージェントに届くこと） |
| cross-device context 共有 | ✅ **実装**（2026-09-30）— chat history は全サーフェス共通の**ローカル 1 ファイル**で、各エントリが `source`（デバイス）を持つ。プロンプトを **conversation 単位**に絞り、各ターンにデバイス名を付ける（`web/chat_history.py` の `conversation_entries` / `context_excerpt`）。**他会話は混入せず、会話 id の無いエントリは決して混ぜない**。dashboard は `conversation_id` を**受理して再利用**する（以前はリクエストごとに新規採番していたため、そもそも会話を継続できなかった） |
| 端末オフライン時の縮退 | ❌ **v1 に入れない**（`DECISION_DRAFTS.md` C-2: 複雑さの割に北極星へ寄与しない） |
| 音声 I/O（STT/TTS） | ✅ **実装**（2026-09-30）— ローカル TTS は `integrations/local_tts.py`（Windows `sapi` で実測、日本語 132,734 バイト）、ローカル STT は `integrations/stt_service.py`（`faster-whisper` は**この環境に未インストール**）。外部 TTS は egress の許可制を通る。**残り**: wake word・ハブの音声チャネル・`push_to_talk_only` の強制（フィールドは依然として読み手ゼロ） |
| 外部メッセージング（LINE / Discord / SMTP） | ✅ 実装 — 3 チャネルとも **egress ゲート経由**で、既定では拒否される（`notification/channels/{line,discord,email}.py` + 共通の `outbound.py`）。許可は standing（master switch + `privacy.external_messaging_allowed` + allowlist）**のみ** — **記録済み grant 経路は現状効かない**（下の「記録された許可」行を参照）。Webhook は `WebhookSender` が `personal_ai/social_proxy.py` で使われているが `NotificationRouter` 経由ではない。`interaction/channels/{line,discord}.py` は**内向き**の置物（外向きは実装済み） |
| egress の「記録された許可」（第 2 の許可経路） | ❌ **記録のみ・未配線**（2026-10-03 実測）— `egress/permissions.py` の `ConfirmationGrantSource` は実装済みで、ゲートの `check()` は**毎回** `_user_grant` を通じて読むが、**`src/` に構築点が 1 つも無い**（呼び出しは `tests/test_egress_permission.py` の 3 箇所だけ）。composition root は `configure_egress_gate(settings_store=…)` しか呼ばず `set_permission_source` も呼ばないので、実行時は常に grant 無し＝**ユーザーが記録した許可は効かない**。したがって許可経路は standing のみで、出荷構成では master switch は開いているが purpose フラグは `llm` だけが True（`web_search_allowed` は false が実測）・allowlist は `api.typesafe.ai` のみ → **実質 JEV だけが外に出られる**（`agora` の様な未マップ purpose は `_purpose_allowed` が False）。戻し方は `DELEGATION.md` §4 項目 22、ピンは `tests/test_egress_grant_source_is_unwired.py`（**変異 5/5 捕捉**） |
| 死んでいる chat の SSE ルート | ❌ **両端とも死んでいる**（2026-10-03 実測）— `GET /api/chat/events` は登録され `text/event-stream` を返すが、① **publish する側が無い**（`dashboard_legacy.py` の `_chat_event_clients` は書かれるだけで、**ファイル内に `put` が 0 件**）② **subscribe する側が無い**（パス文字列は定義ファイル 1 つにしか現れず、`EventSource` は**別チャネル**（`/api/ui/stream`、`web-ui/src/api/useOverviewStream.ts:24）にしか無い）。接続しても 15 秒の heartbeat しか届かない。ピン `ai-server/tests/test_chat_sse_route_stays_dead.py`（**変異 6/6 捕捉**）、配線/削除は `DELEGATION.md` §4 項目 23 |
| `data/audit.jsonl` の読み手（書き手ゼロ） | ❌ **書き手 0・読み手 4 箇所**（2026-10-03 実測）— `aegis_ai/audit.py`（**JSONL** を書く `AuditLog`）と `aegis_ai/audit/`（**SQLite** を書く**パッケージ**）が同名で、**パッケージが勝つ**（実測: `importlib.util.find_spec("aegis_ai.audit").origin` = `audit/__init__.py`）ので **JSONL を書く側は到達不能**。`runtime.py:902` は `AuditLog(path=…/audit.jsonl)` を構築するが、到達可能な `AuditLog.__init__` は `db_path = Path(path).with_suffix('.db')` を通すので**実際に書かれるのは `data/audit.db`**（実測: `AuditLog(path=<tmp>/a.jsonl)` に 1 行記録 → `a.jsonl` は**作られず** `a.db` が作られる）。`audit.jsonl` の名は**一度きりの移行入力**（`_migrate_jsonl_if_needed` が DB 空のときだけ読む）としてしか生きていない。**`src/` に書き込み 0 件**（書き込みモードの `open` が audit パスを指すのは `settings/store.py` の `settings_audit.jsonl` = **別ファイル**のみ。`AuditManager.rotate` の `audit_archive/audit_YYYY-MM.jsonl` も別ファイルで、しかも**先にこの死んだファイルを読む**ので永久に 0 件しか回さない）。読み手は **4 ルート**（`GET /api/audit/stream`・同ファイルのもう 1 つ・`routes/autonomous.py` の 2 つ）＋ `AuditManager` の SQLite 障害時フォールバック 2 つ。よって `GET /api/audit/stream` は**第 3 の機構**で死んでいる — producer 不在（chat SSE 型）でも「クライアント無し」でもなく、**供給元が stale**（移行入力としてしか存在しなかったファイルを流す）ので heartbeat しか出ない。ピン `ai-server/tests/test_audit_jsonl_has_no_writer.py`（**8 本・変異 7/7 捕捉**、両方向）、張り替え/削除は `DELEGATION.md` §4 **項目 25** |
| 宣言済みルートのクライアント側 | ⚠️ **未検証（候補 96 件）**（2026-10-03 実測。⚠️ 同日、影の重複ルート 2 本の削除で **98 → 96**）— 実アプリ（production / `AEGIS_UI_VERSION=v2`）の `url_map` は **190 ルール / 200 の (method, path) 対**を持ち、照合規則を「**クライアントが rule の literal path、または最初の `<` までの静的接頭辞を含む**」と定めると、**200 のうち 96 がクライアントソース（`web-ui/src`・android-server・SDK・pc/browser/room）から一度も参照されない**（literal のみなら **125**）。⚠️ **2026-10-03 に訂正**: 分母の **202 は重複込み**の数で、**一意な対は 200**。同じ規則で測り直すと**未参照は 96**（一意ベース、実測）。**96 + 2 = 98** の差は、**影の落ちた重複ルート 2 本**（`GET /api/servers`・`POST /api/memory/reload` — 下の「影」の行）が**どちらも未参照かつ 2 回登録**なので、**多重度で数えると二重に数えられる**分である。**正しい分母は一意な対**（当時 192 ルール / 200 一意対）。⚠️ **その 2 本を削除した結果、多重度と一意が一致した** — 現在は **190 ルール / 200 対 / 200 一意対**、未参照は **96**（多重度＝一意）、内訳は **GET 56 / POST 35 / DELETE 3 / PATCH 2**（＝**可変 40 本**）— 可変ルートは「クライアントが無い」だけでは済まないので、`DELEGATION.md` §4 項目 28 の判断材料にする。⚠️ **この数は記録されていた「189 のうち 86」を置き換える** — 旧値は試した **4 つの照合規則（16 / 75 / 98 / 127）でも、面の数え方（**当時**: 192 ルール / 202 対 / 182 一意パス / 200 一意対）でも再現しない**（クライアント集合を 6 ルートからツリー全体へ広げても 97 でほぼ不変）。**規則を書かずに引用された数は再導出できない** — それがこの値が生き延びた理由である。**結論は不変**。ただし**これは候補であって判定ではない** — 多くは operator 向けの公開 API・Android・XR/display 面で、「クライアントが無い」だけでは死と言えない（chat SSE が死んでいたのは **両端**が死んでいたから）。**push 面は 8 本だけ**（`url_map` の SSE = 8・WebSocket = 0）で、うち **同梱バンドルが購読するのは `/api/ui/stream` の 1 本だけ**（`EventSource` は `web-ui/src/api/useOverviewStream.ts:24` の 1 箇所のみ、ビルド済みバンドルにもこの 1 パスしか現れない）。**両端とも死んでいるのは 2 本** — `GET /api/chat/events`（項目 23）と `GET /api/audit/stream`（項目 25）。**残る 5 本は producer が実在する**（`/api/approvals/events`・`/api/presentations/stream` は**接続ごとの queue** を store / event bus のリスナが満たし、`/api/stream/{desires,autonomous,memory}` は**生きたオブジェクトを poll する生成器**）。⚠️ **producer が実在する = 健全ではない** — `/api/presentations/stream` は `subscribe` の**返り id を捨て**、`unsubscribe` を**持たず**、queue も**無限**なので、切断後も**購読者を保持し続ける**（route を駆動して実測 **1 → 1**。兄弟の `routes/ui.py` は `finally` で解放し **1 → 0**）。項目 26 — **2026-10-03 に修正済み**（ピン `tests/test_presentation_stream_is_sound.py`、**7 本・変異 8/8 捕捉**）。⚠️ **「`.put(` がある」は producer の証拠にならない** — **接続ごとの queue** に書く `put` は producer だが、**共有 registry** に書く `put` は（chat SSE の様に）書かれても誰も読まないことがある。**未購読は判定ではない**（`/api/approvals/events` の docstring は「現在のバンドルは消費しないが、このモジュールが所有する wire 契約である」と明記している）。**文書化された部分集合は固定済み**: `docs/approval-ui.md` と `docs/feature-catalog.md` のルート表 **13 行**を `ai-server/tests/test_documented_routes_are_registered.py` が**等式**で固定（**文書 ⇒ 登録**の向きのみ。逆は上記 96 候補があるので主張しない）。変異 7/7 捕捉 |
| 影の落ちた重複ルート（legacy の写し） | ✅ **修正済み（2026-10-03）** — かつて **登録済みの view 関数 2 つが決して実行されなかった**（同日実測）。app は **192 ルール**を登録していたが、**(method, path) 対が 2 つ重複**している。Werkzeug は同じパスの**最初の**ルールに当たるので、2 番目は到達不能。実測（adapter を駆動して、ファイルを読むのではなく）: **186 エンドポイントのうち到達不能はちょうど 2 つ** — `GET /api/servers` は `dashboard_server_status.api_servers` が勝ち **`api_servers`（`dashboard_legacy.py:1159`）** が負け、`POST /api/memory/reload` は `dashboard_memory.memory_reload` が勝ち **`api_memory_reload`（`dashboard_legacy.py:1372`）** が負ける。**敗者はどちらも legacy の closure ハンドラ**（blueprint へ移行したときの残骸で、blueprint が先に登録される）。影響は**エンドポイントの故障ではなく死んだコード** — 勝者が正しく応答する。**削除した**（`DELEGATION.md` §4 **項目 28**）— legacy の closure 2 つだけを落とし、**ルート自体は blueprint が serving し続ける**（実測: 削除後も両パスは解決する）。現在 **190 ルール / 200 対 / 200 一意対**（重複 **0**）。ピン `ai-server/tests/test_no_route_is_shadowed.py`（**6 本・変異 5/5 捕捉**、両方向 — 影を**増やす**変異と**勝者を消す**変異の両方が赤になる）。⚠️ この 2 本は**上の「未参照」集合にも入っており**、多重度で数えると二重に数えられていた（上の訂正を参照） |
| `GET /api/presentations/stream` の二重の欠陥（漏れ + 未配信） | ✅ **修正済み（2026-10-03）** — かつて **2 つ**の欠陥が重なっていた。① **漏れ**（2026-10-03 実測）: `manager_routes.presentation_stream`（`manager_routes.py:906`）は `rt.event_manager.subscribe(_on_event)` を **route 関数スコープ**（`:917`）で呼ぶ — **リクエストごとに 1 回**、generator が始まる**前** — しかも**返り id を捨てる**ので後で解放できない。モジュール内に `unsubscribe` は **0**、queue は**無限**（`queue.Queue()`、`:909`）なので、切断後も**ドレインされない queue** に `presentation.*` が積まれ続ける。**実測（route を駆動して、読むのではなく）**: 実行後 **1** → イベント発火 → generator 前進 → `close()`（切断）後も **1**。**陽性対照**は同パッケージの兄弟ルート — `routes/ui.py` は id を保持し `finally` で解放（**1 → 0**、`maxsize=200`）、`routes/approval.py` は `add_listener` の remover を `finally` で呼ぶ。影響は**潜在**（今日購読するクライアントは無い — パスは自分の定義ファイル 1 つにしか現れない）が、**最初の接続**で発火し接続ごとに累積する。⚠️ **「producer が実在する」は「健全」ではない** — このルートは上記の「生きた 5 本」に数えられていた。直した（枝 ①、`DELEGATION.md` §4 **項目 26**）。② **実測で見つけた第 2 の欠陥**: ハンドラは `_on_event(event_type, payload_json)` の **2 引数**だが、バスは `sub.handler(event)` と**1 引数**で呼ぶ（`event_bus.py:241`、notify ループ内の例外は `:243-246` で dead-letter 行き）ので、**このハンドラは一度も走っていなかった** — 購読者数は正しいままなので**数では見えない**。**片方だけ直すと配信か解放のどちらかが死んだまま残る**ので 1 つの修正にした。ピン `ai-server/tests/test_presentation_stream_is_sound.py`（`..._leaks_a_subscriber.py` から**改名**、**7 本・変異 8/8 捕捉**、陽性対照つき）。⚠️ **漏れるのはこの 1 本だけと実測** — 残る「生きた 4 本」のうち `GET /api/approvals/events` は**正しい形**（`store.add_listener` を generator **内**で呼び、queue は `maxsize=_CLIENT_QUEUE_SIZE`、`finally` で `unsubscribe()` — そのコメントが「閉じたタブが listener を残すと store が**誰も読まない queue** に書き続ける」と、**同じ欠陥を名指しして回避**している）、`/api/stream/{desires,autonomous,memory}` の 3 本は **subscribe を一切しない**（`while True` で生きたオブジェクトを poll するだけ）ので**漏れようがない**。つまり 5 本の内訳は、修正前が **漏れる 1 / 正しい 1 / 購読しない 3**、**修正後は漏れる 0 / 正しい 2 / 購読しない 3**（presentations が正しい形へ移った） |
| `GET /api/memory/stats` の応答 | ✅ **修正済み（2026-10-03）** — かつて **10 中 7 しか報告しなかった**（同日実測）— `MemoryManager`（`memory/memory_manager.py`）は同じ概念を **3 回**名指しする: `get_backend()` の **docstring 11 名** / `get_backend()` の **mapping 10 名** / `get_stats()` の **list 7 名**。① docstring は `association` を宣伝するが mapping に無いので **`get_backend("association")` は `None`** — この名前は架空のものの綴り違いでは**ない**: `AssociationMemory` は**実在して live**（`runtime.py:1671` が構築し `CuriosityExploration` に渡す）が、**manager ではなく runtime に登録**されている（docstring が 2 つの名簿を混同）。② `get_stats()` の脱落集合 `{person, store, action_trace}` のうち `person`・`action_trace` は `get_stats` を**持つのに**応答から落ちる（`store` は持たないので正当）。live な `GET /api/memory/stats`（`manager_routes.py:371`）が `get_stats()` を**そのまま返す**ので、影響はクラッシュではなく**静かに不完全な応答** — 7 つ答えて、さらに 2 つ存在することを知る手段が無い。修正は `DELEGATION.md` §4 **項目 27**（枝 ①＋②）— `get_stats()` に `person`・`action_trace` を足し docstring から `association` を落としたので、**live な応答は 7 → 9**（`action_trace` は runtime が `mm._action_trace` へ**代入**して配線するので実行時に効く）。ピン `ai-server/tests/test_memory_backend_registries_agree.py`（**9 本 / 17 ケース・変異 12/12 捕捉**、両方向）。⚠️ 修正中に**ピン自身の弱点**を 1 つ実測で捕まえた — 「runtime が ghost クラスを構築する」検査が**部分文字列**だったので、構築を**コメントアウト**する変異が緑のまま通った（**文字列リテラル内の言及は呼び出しではない**）→ `ast.Call` の検査へ変更 |
| イベント駆動の中核（`TriggerEngine` / `Scheduler` / `EventView`） | ✅ **3 つとも構築済み（2026-10-06 実行）** — `DELEGATION.md` §4 項目 24 の**枝 ①（構築する）**をオーナーが選択。**変更前の記録（2026-10-03 実測、以下は歴史）**: `docs/architecture.md:20` は AEGIS を "**event-driven**" と定義し、`:57`・`:84-85`（`EventBus --> TriggerEngine --> ContextBuilder`）・`:108`・`:170`・`:174`・`:559`（**シーケンス図**）に中核を載せ、`AGENTS.md:15` は event-driven な調整を中核原理と呼ぶ。ところが `src/` に**構築点が 1 つも無かった**（`ast` 走査、408 モジュール）: `TriggerEngine` **0**・`Scheduler` **0**・`EventView` **0**。参照もそれぞれ**再輸出シム 1 つ／0 件／再輸出 1 つ**だけで、**どのモジュールからも到達不能**だった。対照に `AutonomousLoop` は `runtime.py` の `_create_autonomous_loop` で構築される。**イベントバス自体は死んでいない** — `EventBus`/`EventManager` は `_build_runtime` が構築し、`.publish` は 17 モジュール 17 箇所・`.subscribe` は 9 箇所ある。**欠けていたのは「起動する側」だけ**で、実体は**ポーリング駆動**（`context_builder.py:206` が `list_recent_events()` を定期に読む）。**2026-10-06 の変更**（すべて `runtime.py::_build_runtime`）: `config.trigger_enabled` を**構築条件として**読み、`TriggerEngine`（`create_default_rules()` の **13** ルールを全追加）・`Scheduler`・`EventView`（**両方の半分**を渡す）を構築し、`event_manager.subscribe(trigger_engine.on_event)` で購読する。**消費側**は `AutonomousLoop._drain_trigger_tasks`（`autonomous_loop.py`）— `_run_loop` が `can_execute` のときだけ drain し（`drain_tasks()` はキューを消すので、走らないサイクルへ drain すると**無言で捨てる**）、結果を起床条件に載せる（`or triggered_tasks`）。`_create_autonomous_loop` が `loop._trigger_engine` に実体を渡す — **片方だけでは直らない**。⚠️ これで `config.trigger_enabled` は**ログ 1 行だけの読者ではなくなり**、`main.py:27` の行は**真**になった（`test_ineffective_flags.py` 層 4 の台帳から `trigger_enabled` が外れたのは、等式 assertion がそれを強制したため）。⚠️ 実体は**まだポーリング駆動のまま** — 中核は起動するが `context_builder.py:206` の定期読みは残り、`Scheduler` には**消費者がまだ無い**。⚠️ `EventView` は**半分だけでは何も出ない** — `get_trigger_stats()`/`get_pending_tasks()` が `self._engine` を guard して `{}`/`[]` を返すので、`EventView(event_bus=...)` で止めると**空の節が静かに描かれる**（ピンが**挙動と構造の両方**で固定）。⚠️ **証拠の記述は 2026-10-03 に 2 点訂正済み**（旧記録の「`__main__` デモ」は誤りで、実体は**クラス docstring の `Usage:` 例**＝文字列リテラル、`__main__` ブロックは存在しない／`AutonomousLoop` の行番号 1625 は 1669 に腐っていた → 関数名に置換）。ピン `ai-server/tests/test_event_driven_core_is_constructed.py`（**10 本・変異 8/8 ＋ 対照 1**、両方向 — 構築点の集合が記録と**等式**であること**と** docstring の文字列が実在し**その定義モジュール自身は呼ばない**こと）。⚠️ **変異 M1 が初版を生存した** — 「`loop._trigger_engine = ...` が在る」だけを見ていたので右辺を `None` にしても通った（「言及は読者ではない」の同族）。右辺が `trigger_engine` を読むことまで固定して捕捉。構築/文書整合は `DELEGATION.md` §4 **項目 24** |
| `POST /api/memory/reload` の `chroma_synced`（Chroma のベクトル経路） | ❌ **常に 0 — 経路が到達不能**（2026-10-03 実測）— ルートは `"chroma_synced": 0` を**リテラル**で返す。連鎖は端から端まで死んでいる: `ChromaSemanticMemory`（`memory/chroma_semantic.py:18`）の構築点は `create_semantic_memory`（`memory/factory.py:38`）**だけ**、その関数に**呼び出し元が無く**（唯一の言及はモジュール docstring の `Usage:` 例＝**文字列リテラル**）、live は `runtime.py:1038` が `semantic_memory` から**直接** `SemanticMemory` を構築する。よって `sync_from_advanced_memory` は**呼び出し元 0**、`chroma_available` は**読み手 0**（live では**生産すらされない**）。⚠️ `chromadb` は venv に**入っている** — 「依存が無い」ではなく「**能力はあるが到達不能**」。⚠️ **配線は無料ではない**: `OpenAIEmbeddingFunction`（`OPENAI_API_KEY`、既定 `text-embedding-3-small`）で埋め込むので、有効にすると**記憶の内容が外部へ出る** — 単一制約の対象そのもので、担うべき機構は**自発的な問い**。判断と戻し方は `DELEGATION.md` §4 **項目 29**、ピン `ai-server/tests/test_chroma_vector_path_stays_unwired.py`（**11 本・変異 11/11 捕捉**、陽性対照 3 つ） |
| 同名 `SemanticMemory` の衝突（2 つのクラス） | ❌ **パッケージ根が「死んだ方」を再輸出している**（2026-10-03 実測）— `memory/semantic.py:28`（70 行・**6** メソッド・`get_stats` 無し）と `memory/semantic_memory.py:84`（257 行・**15** メソッド）が**無関係な**同名クラスを定義する（共通は `__init__`・`add`・`search` だけ）。live は後者 — `runtime.py:1027`・`llm/memory_context.py:373` が `aegis_ai.memory.semantic_memory` を**明示** import する。ところが `memory/__init__.py:16` は**前者**を再輸出するので、`from aegis_ai.memory import SemanticMemory` は 6 メソッドの方を渡す。**その綴りで import する者は今 0**（`src/`・`tests/` 実測）なので**生きたバグではなく潜在的な罠** — 次に自然な import を書いた者は `get_stats` も `get_preferences` も無いクラスを受け取り、**import 時には何も失敗しない**。⚠️ `audit.py` / `audit/` の衝突（項目 25）と**同じ形** — 名前が**解決先ではなく要求**を指す。判断と戻し方は `DELEGATION.md` §4 **項目 30**、ピンは項目 29 と同じファイルが**両方の半分**を固定 |
| 負担量の指標（§3.1 穴 3）の**配線** | ✅ **配線済み（2026-10-03）** — 定義はオーナー（**判断用 LLM が判断し、ちょくちょくユーザーに確認する**）で、`aegis_ai/burden/metric.py` が既にあったが `src/` に**構築点が 0** だった。配線は 5 箇所: ① `JUDGMENT_PROFILE` を `decision` → **`jev_decision`** ② `build_user_question` の `side_effects` を **list → string** ③ `AutonomousLoop._maybe_ask_burden_check`（周期フック）④ `last_burden_ask_ms` の `loop_state.json` 永続化 ⑤ `_create_autonomous_loop` の `set_burden_metric(BurdenMetric(llm_gateway))`。⚠️ **①と②は「配線したのに動かない」型で、既存ピンは緑のままだった** — ① 旧 profile `decision` は `api.deepseek.com` に解決し、出荷 allowlist（`api.typesafe.ai` のみ）が**拒否**するので Mock へ縮退し、`is_trustworthy=False` → **決して聞かない**（実測: resolver + 実ゲートを駆動。`decision` → DENY / `jev_decision` → ALLOW）。既存ピンは profile が**宣言されている**ことしか見ておらず、**解決先**は見ていなかった（`declared` ≠ `resolves`）。② ask は能力 `ai-server.confirmation.request` の**引数として**運ばれるので、**能力自身の `input_schema`** を通る必要がある — `side_effects` はそこで `string` を宣言されており、`[]` は `jsonschema.validate` に落ちて broker が `VALIDATION_DENY` を返す（実測）。**キー名を dataclass と突き合わせるだけのピンでは見えない**（`ConfirmationRequest.side_effects` は `Any`）。⚠️ **ループは確認ストアに直接 `request` しない** — `ai-server.confirmation.request` を broker 経由で実行する（`self._confirmations` は**読み取り専用**、`test_forced_gate_stays_retired.py` が固定）。ask は**信頼できない判断については行わない**（Mock の数字をユーザーに確認させない）ので、**クロックも進めない**。初回サイクルは**問わずにクロックを開始**する（質問は「期間」についてなので、背後に期間が要る）。判断に渡す activity は**ループ自身の `execution_log.jsonl`** から窓で濾す（`aegis_ai.burden` は監査パッケージを参照しない — `test_burden_metric_has_no_instrument.py` が前提を実測済み）。判断と戻し方は `DELEGATION.md` §4 **項目 8**、ピンは `ai-server/tests/test_burden_metric_is_judged.py`（**18 本**）＋ `ai-server/tests/test_burden_check_is_asked_by_the_loop.py`（**15 本** — うち **+2 は配線の硬化**: `_create_autonomous_loop` はスイートに一度も実行されないので、`set_burden_metric` を**実走させる**ピンと、composition root の呼び出しが**位置引数ちょうど 1 つ**であることを `inspect.signature` と `ast` で固定するピン）、**変異 16/16 捕捉**（3 ファイル、制御実行は緑、原ファイルは開始時に捕捉したバイト列から復元し sha256 一致 — `86b3a9aaa644` / `b50e692729a8` / `f7139f755595`） |
| multi-user / plugin marketplace | ❌ 未着手（v1 スコープ外） |
| Docker 全体検証 | ⚠️ **静的な整合は実測で固定した（2026-10-03）。実機でのマルチサービス起動は未完** — 実測（Docker 29.7.2 / Compose v5.5.0、デーモン不要のクライアント側）: `docker compose -f docker-compose.yml config --quiet` **rc=0**、本番 overlay は `AEGIS_SESSION_SECRET` 無しで **rc=1**（`${AEGIS_SESSION_SECRET:?…}` の fail-fast が実際に効いている。与えると rc=0）。サービス数は base **6** / 本番既定 **5**（`room-server` が `profiles: [room]` で外れる）/ 本番 `--profile room` **6**。構造も測った — `depends_on` の宛先はすべて定義済み（2 辺）、公開ホストポートに衝突なし（6 本）、名前付きボリュームは**宣言＝使用**（6 = 6、両方向）、`build.dockerfile` は 3 件すべて実在。⚠️ **3 つの実像すべてが `HEALTHCHECK` を持つのに compose は 1 つも宣言せず、`depends_on` は全部 `service_started`** — healthcheck は存在するが**何もゲートしていない**（`service_healthy` にするのは挙動変更＝判断、§4 項目 31）。⚠️ 疑わしかった `COPY --from=web-ui-build /ai-server/…` は**実測で正しい**（`web-ui/package.json` の `--outDir ../ai-server/src/aegis_ai/web/static/ui-v2` が WORKDIR `/web-ui` からそのパスに解決する）。ピン `ai-server/tests/test_compose_is_coherent.py`（**8 本・変異 14/14 捕捉**、`docker` を呼ばない＝CI にデーモンが無くても走る） |

### 3.3 承認時代の残骸（棚卸し記録 — 残る判断は §0.2）

> **2026-09-29 更新 — 下の表は 2026-09-28 の棚卸し記録。** その後の P1-5 で:
> **#1 `AutonomyProfile` / #3 `dialogue/` / #4 `research/` / #9 `{room,android}_server_client.py` は
> 削除済み**（`b73309e` / `bba8ae5`、計 13 ファイル / 3,136 行。**テストは 1 件も消えていない**）。
> **#2 `permissions/` は 2026-10-03 に削除、#10 `evaluation/` は削除せず固定**（`f2948a1` / `d4aae94`）—
> 前者は**「動くゲート」**で配線すると目標に反するので**配線せず、オーナー決定でパッケージごと削除**した
> （`DELEGATION.md` §4 項目 3）。後者は**未使用ではなく主張が偽**なので、消す前に記録が要る。
> **#8 `BrowserSafetyBoundary` は削除対象から外した** — 休眠しているだけで本来効くべき層で、
> **egress 半分は P1-7 で閉じた**（`a5c2cdc`）。
> **残るオーナー判断は 3 件**: #10 `evaluation/`（**B-2**）・
> `motivation_arbiter` を含む到達不能な経路（**B-3**）・`reflection_engine` の死んだ
> `approval_decisions` 引数（**A-11**）— **#2 `permissions/` は削除済みなので外した**。**#6
> `risk.approval_mode` と #7 `ConfirmationStore.mark_executed/mark_failed` は下の §5.1 の実測で
> 「消費されている」「生きた契約」と判明したので判断は要らない** — この行は長く 6 件を「判断待ち」と書いていた。
> **正典は §0.2**（この行はその写しだった）。

**下の表は 2026-09-28 時点の判定**で、その後の実測で**7 面中 4 面が誤り**と判明しています（上の更新
ブロックと §5.1）。**「誰も読まない/呼ばない」を表から読み取らないでください** — 面ごとに実測が
必要で、実際 `permissions/` と `reflection_engine` は**生きたテストとランタイム経路**を持っていました。

| # | 対象 | 問題 |
|---|---|---|
| 1 | **`AutonomyProfile`（`settings/models.py`）** | **最も深刻**。`AEGISSettings.autonomy` に入るが**1 フィールドも読まれない**。しかも `captcha_bypass_forbidden` 等が自ら *"Always forbidden (structural)"* と名乗るのに**何も強制していない** = **虚偽の安全主張**。`test_ineffective_flags.py` は privacy/voice モデルしか走査しないため見逃している |
| 2 | ~~`aegis_ai/permissions/`~~ | 第 3 の承認面。本番呼び出し元ゼロ（テスト 2 本のみ import）。**2026-10-03 に削除**（オーナー決定 — `DELEGATION.md` §4 項目 3） |
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
| **B-6** | **この環境で `git commit` が ref を書かないことがある** — コミット自体は成功し reflog に記録されるが `.git/refs/heads/<branch>` が作られず HEAD が unborn になる。⚠️ **この行の機構は 2026-09-30 に撤回した（実測で反証）— ただし 2026-10-01 に深さ説が再現し、撤回は未決着に戻った（§1.4 の 10-01 追記）** — ①「**原因を特定**」は誤り: rename が無音で失敗するという説明は**仮説**で、`update-ref`（同じ lock+rename 経路）が成功した測定がこれを弱める。**原因は未特定**。②「**入れ子名でのみ発生**」も**反証**（平坦な `refs/heads/<branch>` は入れ子の `refs/remotes/origin/<branch>` と**同時に**失われた）。③「**`git update-ref` は解決策にならない**」は**いったん反証されたが、2026-10-01 に再現した** — 深さ ≥ 2 で **25/25 失敗**（`rc=0`・ref を書かず囲むディレクトリを削除）、深さ ≤ 1 で **15/15 生存**。**残るのは予防だけ** — コミット後に `git log -1` で確認し、失敗していれば`.git/refs/heads/` を `mkdir -p` して `.git/logs/HEAD` の最終行から ref を直接書く。**正典は §1.4 と skill `aegis-verify-and-test` §1.0** | ⚠️ **回避策を確立**: コミット後に `git log -1` で必ず確認し、失敗していれば `mkdir -p .git/refs/heads` + `.git/logs/HEAD` の最終行から ref を直接書く（作業内容は無傷。今回 6 回とも復旧済み） |
| **B-7** | **設定サーフェスの 31% が誰にも読まれていない** — 12 モデル 106 フィールド中 **33 が未読**。最悪は `AutonomyProfile` で、`# Always forbidden (structural)` と書きながら**その挙動を守っているものは何も無かった**（CAPTCHA は別経路で守られているが、bulk signup は**プロンプト文にしか無い** — §4.2 B-8 で判明）。検出器 `test_ineffective_flags.py` はモデルを**手書きのリスト**（privacy / voice の 2 つ）で持っていたため、サーフェスが増えても追随せず、**この 10 フィールドを一度も見ていなかった** | ✅ **対応済み**（P1-3）。`AutonomyProfile` を削除。検出器を**モデル自動発見**に変更し、残る 22 は理由付きで `_UNOWNED_DEBT` に記録し、**「未読の集合」と「記録の集合」の一致**をテストで固定。**未走査だったモデルに死にフラグを足しても落ちる**ことを変異検査で確認。**2026-09-29 訂正**: ここは「**12 モデル / 95 フィールド**」と書いていたが、実測は当時 **11 / 94**、A-1 後は **11 / 93**。**モデル数は削除前の値**（`b73309e^` = 12 モデル / 106 フィールド、AutonomyProfile は 11 フィールド）、**フィールド数は 106 から AutonomyProfile の 11 だけを引いた手計算**で、親の `AEGISSettings.autonomy` 参照フィールドを引き忘れていた（106 − 11 − 1 = 94）。**引いて作った数は測った数ではない** |
| **B-8** | **browser-server の安全層が丸ごと休眠している** — `BrowserSafetyBoundary` は構築され `get_actions_taken()` だけが読まれるが、**`check_*` は 4 つとも `src/` から一度も呼ばれない**。`record_action()` も呼ばれないので `actions_taken` は常に空。`forbidden_actions` の `use_proxy_for_evasion` / `bulk_signup` は**プロンプト文としてのみ**届く。`except SafetyStop` / `ApprovalBoundary` / `UserInputNeeded` は**死んだ `except`**（対応する `raise` が無い）なので `STOPPED` / `NEEDS_APPROVAL` は到達不能な enum 値。さらに `test_goal_change_guard.py` は **`ai-server/src` しか走査しない**ため、browser-server 側に残る**強制ゲート（`ApprovalBoundary` / `NEEDS_APPROVAL`）が視界の外**にある。**単一制約への実害**: `check_domain`（ナビゲーション毎の egress 検査）も死んでおり、事前検査は宣言済み target しか見ない | ⚠️ **記録済み・未修正**（P1-7）。休眠を `browser-server/tests/test_safety_boundary_dormancy.py` が**発見＋等式**で固定（変異 2 種で load-bearing を証明）。配線には action 語彙の翻訳と `APPROVAL_BOUNDARIES` の扱いの判断が要る。**うち egress 半分は P1-7 で閉じた**（下記 B-9 と P1-7 行） |
| **B-9** | **egress ゲートの 2 コピーが乖離していた** — browser-server は `aegis_ai` に依存しない別ディストリビューションなので `egress.py` を自前で持つ。docstring と `docs/egress-gate.md` は「意味論は意図的に同一」と書いていたが、**実際は乖離していた**: browser 側の `_extract_host` に IPv6 リテラルの処理が無く、`is_local_destination` の単一ラベル判定に `":" not in host` のガードも無かった。結果、**同じホストが書き方で別判定**（`::1` は external、`http://[::1]/` は local）になり、`_admissible_host` と `egress_allowed` が食い違っていた | ✅ **修正済み**（`a5c2cdc`）。ai-server 側の実装を移植。**移植だけでは不十分だった**: ガードが無いまま IPv6 対応を入れると、ドットを含まない `::2`（グローバル到達可能）が**単一ラベル規則で local になる** — fail-open。両方を同時に入れて初めて閉じる。残る相違（`.lan`/`.home`/`.internal` の有無、`is_private` と明示ネットワーク）は**意図的**として `docs/egress-gate.md` に表で明記した |
| **B-10** | **この環境の `git rm -r` は要求していないファイルまで消す** — `git rm -r -q <4 パス>` は指定した 13 ファイルを index に stage したが、**作業ツリーからは `ai-server/src/` を丸ごと削除**した（419 ファイルが未 stage の削除として現れた）。指定パス以外は一切触っていない。**B-6 と同根の疑い** — この環境の git は index 更新に `rename()` を使う経路が壊れている | ✅ **復旧済み**。`git restore --source=HEAD --staged --worktree -- ai-server/src` で完全復元（内容は無傷、`git status` は元の 2 件に戻った）。**回避策**: 削除は `rm` + `git add -A -- <パス>` で行い、**`git rm -r` は使わない**。削除後は必ず `git status --short` の件数を確認する |
| **B-11** | **「割り込みやすさ」の写像が 2 箇所に別々にある** — `personal_ai/interruption.py` の `_RECEPTIVITY`（受容確率）と `autonomous_loop.py:704` の `_current_interruption_cost()`（コスト軸）が、**同じ `SituationModel.interruptibility` を別々の数値表で写像**している。値も一致しない（コスト側 suppress 0.9 / important_only 0.55 / batch_later 0.4 / interruptible 0.1 に対し、受容確率は 0.05 / 0.35 / 0.20 / 0.90 — 補数関係にもなっていない） | ⚠️ **記録済み・未修正**（P1-6 の副産物）。用途が違う（自律ループの発火判断 vs 通知の割り込み判断）ので直ちに誤りではないが、**片方を調整しても他方が追随しない**。揃えるなら「interruptibility → 割り込みやすさ」の単一の表を `SituationModel` 側に置いて両者が参照するのが筋。**今は触らない** — 自律ループの発火間隔は挙動そのもので P1-6 の範囲外 |
| **B-12** | **`FORBIDDEN_CAPABILITIES` は、それが守るフィールドとは別の id 方言で書かれている** — 39 件のうち canonical な形（`server.app.action`）は **8 件だけ**（すべて `pc-server.*`）。残り **31 件は `browser.send_email` のような「短縮 prefix + app_id なし」**。実測で **39 件すべてが `catalog.resolve()`（canonical + alias を解決する唯一の関数）で解決不能**。`validate_settings_change` は**完全一致**で比較するため、**canonical 形で書かれた同じ意図は素通りする**（実測: `per_capability["browser.send_email"]` → 1 件 / `per_capability["browser-server.social.send_email"]` → **0 件**）。守る相手の 1 つ `per_capability` は `permissions.py:89` が **canonical id** で引くので、**短縮形の 31 件は誰も使わない鍵空間を見ており、canonical な 8 件は正しい鍵空間だが存在しない capability を指している**。**今回さらに判明**: ① 生きた 128 capability のうち**禁止 action を持つものは 0 件** — つまり**今は守る相手が存在しない**（だから見えない）。② **3 つのループのうち `disabled_capabilities` のループは本体が `pass`** で、エラーを 1 件も積めない（AST で確認）— 実効は 3 中 2。③ その 2 つが拒否するのは**そもそも no-op な設定項目だけ**（短縮形の鍵はゲートに引かれない）。④ `EXPLICIT_DENY_PATTERNS` が覆うのは **39 件中 5 件**（支払いとポリシー自己改変のみ）で、残りは**別機構**が担っている（egress 系はネットワーク層の egress ゲート、FORBIDDEN を自称するものは `DEFAULT_RISK_MAP`、CAPTCHA/TOS はプロンプト）— **制約は危うくない、この一覧が危うい** | ⚠️ **記録済み・ピン済み・未修正**（`tests/test_forbidden_capabilities_dialect.py`、7 関数 / 13 ケース、**変異 6/6 捕捉**）。ピンは方言構成・解決不能性・素通りする witness・`pass` ループ・ゲートの鍵の形・パターン被覆を**等式と実測**で固定する。**この測定は「修復」ではなく「削除」に傾く** — 守る相手が 0 件、3 ループ中 2 つが無効、名前は何も指していない。**2026-09-29 に「削除」で決着した**（A-1）。削除したものは 39 件の一覧とそれを参照する 3 ループ、`CapabilityPermissions.allowlist`、`config/settings.json` の `"allowlist": []`。ピンは `tests/test_forbidden_capabilities_stay_retired.py`（11 ケース、**変異 14/14 捕捉**）に置換 — **「定数が消えた」だけでは弱い**（システムを弱めれば満たされる）ので、実物の `ToolBroker` が未登録 id を `NOT_FOUND`（ポリシー評価の**前**）で拒否すること、生きたゲートが `capability.id` を鍵にすること、`EXPLICIT_DENY_PATTERNS` が支払い・egress 迂回・ポリシー自己改変の 3 意図群に今も一致することを併せて固定する。`docs/permissions.md` / `pc-safety.md` / `android-safety.md` / `dev-safety.md` も訂正済み |
| **B-13** | **`CapabilityPermissions.allowlist` を消費する者がいない** — 説明は「Capability IDs explicitly allowed (**bypass other checks**)」だが、`settings/permissions.py` が読むのは `disabled_capabilities`（:47）・`denylist`（:56）・`per_capability`（:89）の 3 つだけで、**`allowlist` を読む決定は存在しない**。唯一の参照は `validate_settings_change` 自身（＝自分を検閲するためだけに読む）。**検出器がこれを見逃す理由も特定**: `test_ineffective_flags.py` の `_readers()` は **src 内の識別子テキスト一致**なので、「バリデータが検査のために属性に触れる」を**読者として数えてしまう** | ⚠️ **記録済み・検出器で固定**。`tests/test_guarded_settings_fields.py` が「**バリデータが守るフィールドは、バリデータの外に消費者を持つこと**」を assert する（守られる集合は `validation.py` を AST で解析、消費者は `src/` を走査して発見、現在の穴は理由付きで記録し、**観測と記録の一致を等式で固定**）。変異 5 種すべて捕捉 — 新たに守られたのに消費者がいないフィールド / 記録の削除 / 消費者が付いたのに記録が残る / 走査が誤った属性形を読む / バリデータが守るのをやめる。B-12 と同じ面。オーナー境界の観点では**機能しなかった承認機構の残骸**だったので、**A-1（2026-09-29）で `allowlist` を削除**し、`FORBIDDEN_CAPABILITIES` の 3 ループも同時に消えた。**検出器は守る対象を `*.capabilities.<field>` から全設定セクションへ拡張され、その場で 2 件目の生きた欠陥を発見した** — `max_autonomous_runs_per_hour` はバリデータだけに読まれ、他に消費者がいない（自律ループはハードコードされた予算で動く）。**既存の死にフラグ検出器が見逃していた**のは、識別子走査がバリデータを「読者」と数えるため — 2 つの検出器が同じフィールドに別の答えを返すのはこの理由で、効果について正しいのはこちら。`_RECORDED_GAPS` に記録し、§0.2 の B に追加した |
| **B-14** | **SDK では第三者サーバの capability を作れない** — `define_capability(server_prefix="weather", ...)` は **`capability.py` 自身の docstring にある例**だが、`Capability.id` の `pattern`（`models.py:124`）が prefix を **12 種（6 サーバ × 長短）に固定**しているため **pydantic ValidationError で落ちる**（実測）。しかも **SDK 自身の検証器はこれを通す**（`safety.py:98` の `^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$` は任意 prefix を許容）＝**2 つの検証器が矛盾**し、しかも**両方向**に食い違う: SDK は `weather.` を通して `ai-server.` を弾き（`-` が文字クラスに無い）、スキーマはその逆。**加えて `define_capability` は `server_type` を既定 `DEV` のまま prefix から導出しない**ので、既定引数で通る prefix は **`dev` ただ 1 つ** — つまり **Phase 9 で削除したサーバの身元を借りたときだけ通る**（実測）。`docs/plugin-sdk.md` の Quick Start・`capability.py` の docstring・`examples/example-weather-server`（**import すら通らない**）・`tools/create-capability-server` が生成する `server_prefix="{prefix}"` がすべて同じ穴に落ちる。**SDK のテストが緑なのは、既存 11 件すべてが `dev` を名乗っているから** | ✅ **解決済み**（2026-09-29、A-2 ②、§5.18）— 二択のうち **「SDK が第三者 prefix を明示的に断る」** を選んだ。`safety.py` は自前の regex を捨てて `aegis_schema.models.CAPABILITY_ID_PATTERN` を **import** する（規則が 1 つになる）。`define_capability` は `server_type` を prefix から**導出**する（既定 `None`、引数で矛盾を渡すと拒否）。docstring の例・同梱 example・scaffold の生成物は**説明ではなく実行**で検証される。ピンは「食い違い」から「契約」へ**張り替えた**（`tests/test_capability_id_contract.py`、**変異 5/5 捕捉**）。上の記述は**修正前**の状態 |
| **B-15** | **サーバ名簿が 15 箇所に複製されていた**（11 ファイル、値の型は 5 種: `ServerType` / 短縮 prefix / 有効フラグ / id prefix / host:port。AST で計測）。うち **5 箇所が削除済み `dev-server` を今も列挙**していた（`capability_catalog.py:70`・`:379`、`models.py:215`、`permissions.py:66`、`ui_overview.py:3388`）。**「dev-server 残骸」の実体はこれ** — 個別の消し忘れではなく、**名簿に単一の定義が無いこと**の症状。**ただし実装前の測定で前提が 2 つ崩れた**: ① `server_id → ServerType` の写像は **5 コピー**あり、うち **2 つは既に食い違っていた**（`tool_broker.py` は `dev-server` を持たず、`capability_catalog.py` は持っていた）— 「5 箇所を直す」ではなく「5 コピーが 1 つになる」。② 15 箇所のうち **3 箇所は名簿ではない** — `situation.py:51/189/204` は**状況ソース**の語彙で、`ai-server` を `"webhook"` に写し、`:189` は `"status."`（サーバですらない）を含む。**キーが同じだけの別物**。`alert_manager.py` の 4 サーバも意図的（**サーバは自分を健康診断できない**） | ✅ **解消済み（`952caaa`、2026-09-29）** — `aegis_schema/roster.py` が単一の定義。6 サイト（`capability_catalog.py` ×2 / `prompt_regression.py` / `dashboard_legacy.py` / `models.py` / `tool_broker.py`）が import する。**6 つの写像すべて HEAD と値が同一**であることを確認（＝純粋なリファクタ）。退職サーバは `RETIRED_SERVER_ROSTER` に **1 回だけ**書き、`**` 展開で 3 サイトに折り込む（`dev-server` を綴るモジュールは 6 → 3）。名簿リテラルは **15 → 10 箇所 / 11 → 7 ファイル**、記録ドリフトは **5 → 2 サイト**。検出器は事実の移動に追随させた（`_id_consistency_map()` は AST のローカルではなく名簿を読む。失った「dict リテラルは 1 つ」ガードは、それが守っていた不変量 `test_the_validator_names_no_server_of_its_own` に置き換え）。**測定で 2 つのアサーションを撤回した** — ① `PREFIX_BY_ID` と `_PREFIX_MAP` の比較は**両辺が同じ tuple 由来**なので絶対に落ちない（変異 `room → rm` で緑のままだった）。短縮 prefix は代わりに **id 許可リスト**（別の宣言）と突き合わせる。② manifest の `server_id` と id prefix の比較も同じ理由で無効（`folder_registry` が両方を**パスから**導出し、JSON とパスの不一致は `list_all()` に届く前に**拒否**される）。真の不変量「拒否が 0 件」は既に `test_manifest_schemas.py` が固定している。**変異 12/12 捕捉**（各変異が期待どおりのテストで落ちることを観測、原ファイルはバイト単位で復元） |
| **B-16** | **3 つ目の承認サーフェスが「動くゲート」として休眠している** — `aegis_ai/permissions/`（4 モジュール、**2026-10-03 に削除**）は `{"decision": "ask_approval", "requires_approval": True}` を返す**完成した強制ゲート**。`_category_default()` は `MEDIUM_RISK_WRITE` / `HIGH_RISK_EXTERNAL_EFFECT` / `DESTRUCTIVE` / `FINANCIAL_OR_LEGAL` の 4 分類に `ask_approval` を返し、**最終フォールバックも `ask_approval`**（未知の操作は保守側に倒れる）。`ServicePermissionStore` は `default_*` の purchase/payment スコープを**読み込み時に `requires_approval = True` に永続化**する（`:318-324`）。**パッケージ外からの import は 0 件**（`src/` 全体を AST 走査。他のヒットは gitignore 済みの `.aegis-local/` スナップショットのみ）。B-8（browser-server の休眠安全層）と同型だが、**より危険なのは「動く」こと**: `tests/test_goal_alignment.py` と `test_mission_contract_acceptance.py` がゲート意味論を assert して緑なので、**配線すると「よく支えられている」ように見える** | ⚠️ **記録済み・固定**（P1-5 後半）。`test_forced_gate_stays_retired.py` を 3 サーフェス目に拡張 — 実行経路 7 モジュールが import しないこと（parametrize）、**パッケージ自身だけが import する**こと（非空性 assert ＋ 観測集合と記録集合の一致）、そして**なぜ配線してはならないか**（今も `ask_approval` を返すこと）を記録。**変異 4 種すべて捕捉**（実行経路への import 追加 / 非実行経路への追加 / prefix 一致を等価に狭める / `MEDIUM_RISK_WRITE` を `allow` にする）。**削除ではなく固定を選んだ** — 削除するか配線するかはオーナー判断（配線は目標に反する） |
| **B-17** | **`PresentationRoutingPolicy` の「割り込む価値があるか」判定が定数になっている** — 最後の判定は `should_interrupt = important and not occupied and context.expected_usefulness >= context.interruption_cost`。第 3 項の 2 つの被演算子は `autonomous_loop.py:3065-3066` が**同じ既定値**で埋める（`float(task.get(..., 0.5) or 0.5)` が両方）が、**リポジトリのどこもその 2 つのキーを task に書かない**（`src/` 全体の dict リテラル走査で、書き込みは `_present_autonomous_result` 内の**プレゼンテーション payload への転記 2 箇所だけ** — task 構築側ではない）。したがって比較は常に `0.5 >= 0.5` = **真**で、`should_interrupt` は実質 `important and not occupied` に退化する。**生きた経路**（`routing_policy.py:78`）の欠陥で、死んだモジュールの話ではない。フィールド自体は生きている（`expected_usefulness` を 0.4 に下げると判定は反転する）= **既定値が答えを決めている**。加えて `>=` は等しい既定値どうしで**割り込む側に倒れる**。さらに同名フィールドが**3 つの既定値**を持つ — `ActionCandidate` は **0.0**、コスト表のフォールバックは **0.2**、`PresentationRoutingContext` は **0.5**（`0.0` は `src/` では生成されず、テストだけが到達する。§5.8 の訂正を参照） | ⚠️ **記録済み・固定**（`d4aae94` の副産物）。ピン `tests/test_interruption_cost_vocabulary.py`（8 テスト、**変異 8/8 捕捉**）。修正は「自律的な結果の usefulness とは何か」の設計判断なのでオーナー案件 |
| **B-18** | **`Capability.id_server_type_consistency` は `server_type=UNSPECIFIED` を宣言すると検査を丸ごと飛ばす** — `prefix_map.get(self.server_type)` に**既定値が無く**、`ServerType` 7 メンバー中 **6 つしか map に無い**（欠けているのは `UNSPECIFIED`）。したがって `.get()` は `None` を返し、続く `if expected_prefixes and not any(...)` が**偽**になって id とサーバ種別の整合検査が走らない。**実測**: `room-server.room.foo` + `server_type=PC` → **整合検査で拒否**、**同じ id + `server_type=UNSPECIFIED` → 構築成功**。つまり**情報を *足さない* ことが検査を無効化する**（`UNSPECIFIED` は enum の第 1 メンバーで、`server_type` は必須フィールドなので「明示的に 0 を渡す」だけで起きる）。**この欠陥は検出器自身の docstring が 2 年以上前から記述していたが、主張が 2 重に誤っていた** — ①「`ServerType.DEV` の capability はどの id でも通る」と書いてあるが **`DEV` は map にある**（`room-server.*` の id は正しく拒否される）。欠けているのは `UNSPECIFIED`。② 記述だけで**アサーションが 1 つも無く**、既定値がどちらに倒れても誰も気づかなかった | ⚠️ **記録済み・固定**（`ec15484`。**A-3 の `952caaa` で発見先を更新**）。`tests/test_server_roster.py` に 11 テストを追加 — map は**当初 `models.py` の AST から**読んでいた（ローカル変数で import 不可だったため）が、**A-3 で名簿が import 可能になったので読み先を `aegis_schema.roster` へ移した**（事実の移動に検出器を追随させる。失った「dict リテラルは 1 つ」ガードは、それが守っていた不変量「validator 本体にサーバ名の文字列定数が無いこと」で置き換え）。`ServerType` は enum から、`permissions.py` の map キーとフォールバックは**今も** AST から**発見**する。飛ばされるメンバー集合は**等式で固定**し、**全メンバーを挙動で**検証する（mapped なら他人の id を拒否／unmapped なら受理）。**変異 6/6 捕捉**（既定値を fail-closed に反転 / `UNSPECIFIED` を map に追加 / `DEV` を削除 / pattern が通すキーを削除 / **呼び出し側を改名して発見を盲目化** / **unmapped のフォールバックを fail-closed 化**）。ai-server **1714 passed / 31 skipped**（1703 + 11） |
| **B-19** | **`settings/permissions.py` のサーバ有効ゲートは「不明な prefix = 有効」に倒れる** — `server_enabled_map.get(server_prefix, True)` の**既定値が `True`** なので、map に無い prefix は「そのサーバは有効」と読まれ、**無効化ゲートが発火しない**。ゲートとしては**誤った側**の既定値。**現時点では到達不能**（id の pattern が許す prefix は閉集合で、**その全てが map のキー**）だが、(a) B-14 で pattern を緩めれば即座に到達可能になり、(b) map からキーを 1 つ落とすだけでも到達可能になる。`test_server_roster.py` の docstring はこれも記述していたが**アサーションは無かった** | ⚠️ **記録済み・固定**（`ec15484`）。既定値の**側**を AST で読み `True` として記録（fail-closed に変われば失敗する＝改善として記録を更新する）。さらに「**pattern が通す prefix は全て map にある**」を等式で assert するので、**フォールバックが到達可能になった瞬間に失敗する**（B-14 を修正する人が必ず踏む）。修正は B-15 の名簿一本化と同じ判断 |

### 4.2 文書の陳腐化（構造的）

- **2026-09-27 のゴール変更バナーが、再定義前の制約を現在形で引用したまま 47 ファイルに貼られていた**（✅ **2026-09-30 修正**）:
  - バナー自体は日付付きの記録なので**残すのが正しい**。古いのはバナー内の**引用文**だけで、正典 `docs/GOAL-CHANGE.md` は既に「*許可の無い*ユーザー情報」に更新済みだった。しかし `docs/pc-safety.md` などを単体で読む読者はバナーしか見ない。
  - 実測: **47 ファイルが同一の 2 行を 1 箇所ずつ**持っていた（`Goal change (2026-09-27)` を含むファイルは 48 — 残る 1 つ `ai-server/src/policy_engine.py` は既に再定義後の文面）。引用部分だけを現在形に置換し、各ファイル 4 行追加 / 2 行削除。
  - `Goal change (2026-09-27)` の**文字列は保存**したので、§5.5 の「バナーを持つ文書 = 48」という**時点記録は今も整合する**。
  - **同じ規約の残骸 2 件**: `docs/permissions.md` と `ai-server/AGENTS.md` は「egress の許可制は未配線」と書いていた（`4d3f825` で配線済み）。両方を実装済みに更新。
  - **型 2 の実例**: 正典 1 本の写しが 47 個ある。将来は 1 行のポインタに畳むのが妥当。
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
2. **読み手はいるが生産者がいない**（`executed`/`failed`）— **`approval_lesson` はこの型の実例ではなかった（訂正 2026-09-30）**: 生産者は 1 つあり（`reflection_engine.py:90`）、**到達不能で、しかも読者が照合するキーを書いていなかった**（§3.1 項目 4。**キーは 2026-09-30 に書くよう直した** — 契約は今は合っているが**① 配線は未了**）。**「生産者がいない」と「生産者がいるのに契約が合っていない」は別の型**で、後者のほうが厄介 — ペアが端から端まで一度も実行されないので、**どちらの側も相手に合わせる必要が無く、独立にドリフトできる**。「生産者 0」という判定も*キー*（`decision`）で探した産物だった。**数える前に、何を数えているのかを確かめる**。**この型を直すときに分かったこと（2026-09-30）**: ドリフトは**値の側でも起きる** — 両側が同じ*鍵名*を書いていても、片方が `"rejected"`、もう片方が `"denied"` を比べていれば同じように静かに空になる。**鍵名を assert する構造ピンでは原理的に見えない**ので、**実物の生産者と実物の読者を繋いだ end-to-end ピンが要る**（この変更で M2「値だけ変える」変異が構造ピンを全部通って end-to-end ピンだけを赤にした）**3 つ目の機構（2026-10-03）**: 同じクラスの中で**同じ概念を 3 回**名指しすると、**写しの数そのものが欠陥**になる — `MemoryManager` はバックエンド名を docstring（**11**）・mapping（**10**）・`get_stats()` のリスト（**7**）に書き、**どれも一致しない**。docstring の `association` は mapping に無いので `get_backend()` は **`None`** を返し（実クラス `AssociationMemory` は live だが runtime 側に登録されている）、`get_stats()` は `person`・`action_trace` を落とす（**どちらも `get_stats` を定義する**）。**「写しが一致することを assert する」の一般形は「N 個の写しが互いに一致し、その N が意図されていることを assert する」** — 名簿の数え上げが 1 箇所に閉じていることを誰も検査していなかった（記録: `tests/test_memory_backend_registries_agree.py`、`DELEGATION.md` §4 項目 27）
3. **構築されるが参照されない**（`BrowserSafetyBoundary`）— **その変種が最も危険**: **動いてテストも緑なのに誰も呼ばない**強制ゲート（`aegis_ai/permissions/`、B-16。**2026-10-03 に削除**）。「未完成だから休眠している」のではなく「**完成しているのに休眠している**」ので、**配線が改善に見える**。判定は**呼び出し側を grep する**ことで、宣言やそのモジュール自身のテストでは分からない（B-16 のゲートは自前のテストで `ask_approval` と `fail safe` を assert している）
4. **死んだ `except` は死んだ `raise` を意味する**（`SafetyStop` 等）
5. **正規化の既定値が危険側に倒れる**（`audited_action` が `READ_ONLY` に黙って落ち、12 ケイパビリティが監査なしで実行されていた → 2026-09-28 修正済み）
6. **文書が「ゲートがある」と読める**（削除より危険。プロンプト・マニフェスト・docstring・起動バナーも対象）。**（2026-09-30 追記）鏡像も同じ型である — 「無い」と読める文書**: C-4 の登録行は「`java`/`javac`/`adb`/`gradle`/`kotlinc` が**すべて不在**、**待っても直らない環境の不在**」と書いたが、JDK 17 は **2026-08-19**、Android SDK は **2026-09-25** に**ディスクに入っており**、`BUG_REPORT.md` の「android-server: 実ビルドで §36 を検証」節が**その導入と `BUILD SUCCESSFUL` を既に記録していた**（`ebe1506`、2026-09-29 — C-4 行は 2026-09-30 なので、**書いた時点で既に偽**）。**不在の主張も主張である**: 書く前に (1) **同じリポジトリの記録**を読み、(2) `PATH` ではなく**ディスク**を探す。`command -v java` は `PATH` しか見ないので、**入っているツールを「不在」と報告する** — A-12 の「リテラルが無い＝読者がいない」の**環境版**。**「在る」側は grep で見つかるが、「無い」側は何も鳴らない**ので、「無い」と書くときだけは探し方を疑うパッケージにも及ぶ — 監査の単位を「フラグ」と決め打ちしない**: `docs/security.md` は 6 クラス（token auth / token store / CSRF / rate limit / origin / TLS）を**使用例つきで**解説していたが、実測すると `aegis_ai/security/` は**パッケージ外から import が 0 件**（596 ファイルの AST 走査、14 ヒットはすべて自己参照。生きた認証は `aegis_ai/auth/`）。`test_ineffective_flags.py` は**設定モデルしか見ない**ので、**まるごと死んだパッケージは原理的に見えない** — 「宣言されているが効いていない」を探すときは、**走査の単位（フィールド / メソッド / モジュール / パッケージ）を先に疑う**。もう 1 つの教訓は「修正済み」の意味: `BUG_REPORT.md` は §1 を **✅ 修正** と記録していたが、**その修正は誰も import しないモジュールに入っていた**ので本番では無効 — 「直した」は**コードについての主張**であって**効果についての主張ではない**。効果を言うなら**呼び出し元を測る**
7. **検出器の「読者」定義が甘い** — 「属性に触れている」を読者と数えるため、**検査されるが消費されない**フィールドが素通りする（B-13）。**（2026-10-01 追記）2 つ目の機構は逆側 — 「死んだコードの中の読者」**: 識別子が `src/` に現れれば読者と数えるので、**到達不能なメソッドの中の読みも読者として数える**。実測: `VoiceGate` / `VoicePrivacy` の公開検査 **4 本**が未呼び出しで、3 設定（`voice.record_audio`・`voice.voice_data_retention_hours`・`voice.wake_word_enabled`）の**唯一の読者**だった — 検出器は 3 つとも「読まれている」と報告する。**両方向の盲点は同じ 1 つの定義から出る**（「触れている」＝「読者」）ので、**読者を数えるときは「その読者は到達可能か」を別に問う**（記録: `tests/test_voice_io.py`、台帳 §0.1）。型 1 の検出器自身が型 1 を見逃すので、検出器を書いたら**その検出器の盲点を探す**
8. **同じ名簿・同じ写像が多数のコピーに散る** — 1 箇所直しても他が追随しない（B-11 の 2 つの割り込み写像、B-15 のサーバ名簿）。**「残骸が消し忘れられている」と見えたら、まず名簿の単一性を疑う**。B-15 は **A-3 で解消**（`952caaa`）。ただし**実測で数え方が 2 つ崩れた**: 「15 箇所」のうち **3 箇所は同じ鍵を持つ*別の語彙***（`situation.py` は `ai-server → "webhook"` と写す状況ソースの表で、`"status."`＝サーバですらない値も持つ）、「同じ写像の 5 コピー」のうち **2 つは既に食い違っていた**。**コピーを数えるときは、値の型ではなく *写像の向きと余域* で数える** — 同じ `server_id → X` でも X が違えば別の事実である。**（2026-10-01 追記）名簿が同名 *クラス* のときは、どれが正典かを「輸出されている方」で決められない**: `security/` には `TLSConfig` が **2 つ**（`tls.py` は `is_valid` / `get_grpc_credentials`、`tls_config.py` は `from_env` / `configure_server` / `configure_channel`）あり API が非互換なのに、`security/__init__.py` が再輸出するのは `tls.py` の方だけ — そして**実際に `add_secure_port` を呼ぶのは輸出されていない方**である。**「輸出されている方が正典」も「完全な方が正典」も成り立たない**ので、コピーを見つけたら**どちらが生きているかを呼び出し元で測る**（ここでは両方 0 件だった）
9. **同じ量を 1 つの成果物の中で 2 回書くと、必ず自己矛盾する** — `docs/architecture.md` は冒頭で「53 capabilities / 157 passed」、**同じファイルの**末尾の状態表で「128 capabilities / 1550 passed」と書いていた（✅ 修正済み）。片方だけ更新されるので、**読者はどちらも信じられなくなる**。対策は「測定値を書き写さない」か「**日付付きで書き、不変量ではないと明示する**」のどちらか。**「現在のコードで検証済み」という日付の無い宣言は、この型の入口**（`BUG_REPORT.md` が無事なのは調査日が明記されているから）
10. **死んだコードの中の偽の主張は、テストでは捕まらない** — `aegis_schema/validation.py` は **128 件すべて**の capability に「tags に `risk:<level>` を入れよ（**Policy Engine のフィルタリングのため**）」と警告していたが、**capability を risk タグで絞る機構は存在しない**（✅ 削除済み）。**走らないコードは振る舞いを持たない**ので、テストは何も言えない。したがって**削除する前に中身を読む** — 消すだけでは、同じ偽の主張が別の場所で再生される。あわせて **100% の入力で発火する警告は警告ではない**: 配線すれば 128 件の雑音になるだけで、**「配線しても何も得られない」ことは `0 errors / 133 warnings` を実測して初めて分かる**
11. **誰も走らせない成果物は検証されない** — `examples/example-weather-server` は **import すら通らない**状態で出荷されていたが、**テストもスクリプトも CI もこのファイルを参照していなかった**ので誰も気づかなかった（B-14）。同梱の example・scaffold（`tools/create-capability-server`）が生成するテンプレート・`tools/` 配下は「動くはず」と思われているが、**走らせる者がいなければ 1 行目から壊れていても緑のまま**である。型 8（スイートが走っていない、P2-0）の兄弟で、こちらは**コードではなく成果物**についての話。**「参照されているか」ではなく「実行されているか」を問う**。**（2026-09-29 追記）この型の実例だった 2 つは、いま SDK のピンが実際に import して実行する**（`test_capability_id_contract.py` の `test_the_shipped_example_server_runs_end_to_end` は example を登録・呼び出しまで通し、`test_the_scaffold_generates_a_server_that_builds` は scaffold を生成して生成物を import する）。**型そのものは残る** — `tools/` の他のスクリプトと `web-ui` の Playwright はまだ誰も走らせていない
12. **検査は在るが、報告できない** — ガードが存在し、呼ばれ、実行されるのに、**1 件も指摘を出せない**。3 つの形を実測した（B-12・B-19）: ① **本体が `pass`** — `validate_settings_change` の 3 ループのうち 1 つは `if … in FORBIDDEN_CAPABILITIES: pass` で、条件が真でも何も積まない（実効 3 中 2）。② **誰も使わない語彙と比較する** — 一覧の 39 件は短縮 prefix、ゲートが引く鍵は canonical なので、**同じ意図を正しい綴りで書くと素通りする**（`browser.send_email` → 1 件 / `browser-server.social.send_email` → 0 件）。③ **フォールバックが緩い側** — `server_enabled_map.get(prefix, True)` は不明な prefix を「有効」と読む（B-19）。**型 1（宣言されているが効いていない）の検査版**で、判定は「ガードがあるか」ではなく「**このガードはどの入力で発火するか**」— 実測で **witness を 1 件作って発火させる**。発火しない witness しか作れないなら、それはガードではなく**装飾**である。**発火しないガードは、削除の判断が済んだら消す** — ①〜③ のうち ①② は A-1 で削除済み（§5.13）
13. **測らずに差分で作った数は、測定値ではない** — §4.1 の B-7 は「**12 モデル / 95 フィールド**」と書いていたが、実測は当時 **11 / 94**。**モデル数は削除前の値をそのまま残し**（`AutonomyProfile` の削除後も 12 のまま）、**フィールド数は 106 からその 11 だけを引いた手計算**で、親の `AEGISSettings.autonomy` という**参照フィールド 1 つを引き忘れていた**（106 − 11 − 1 = 94）。型 9 の変種だが**機構が違う** — 型 9 は「同じ量を 2 箇所に書く」、こちらは「**1 箇所にしか書いていないが、書く前に測っていない**」。したがって「同じ量を 2 回書くな」では防げず、**編集の前に必ず走らせる**しかない。**差分の算式を書くなら、その差分の根拠も測る**
14. **検査に見えて検査でない（恒真のアサーション）** — 比較の**両辺が同じ出所から導出**されていると、その assert は**絶対に落ちない**。A-3 の実装中に **2 件**書いてしまい、**どちらも変異を当てた瞬間に発覚**した: ① `PREFIX_BY_ID == {s: _PREFIX_MAP[s] for s in SERVER_IDS}` — `_PREFIX_MAP` は `PREFIX_BY_ID` から**導出**されるので、短縮 prefix を `room → rm` に壊しても**両辺が一緒に動いて緑**。② 「manifest の `server_id` と id prefix が一致すること」— `folder_registry._derive_ids` が `server_id` を**パスから**取り、`capability_id` も**同じ dict から**組み立てるので**構造上**一致する。**判定法は「その assert を落とすには、どのファイルの何を変えればよいか 1 つ挙げられるか」**。挙げられないなら検査ではなく**検査の形をした恒真式**である。**変異は「テストが load-bearing か」ではなく「アサーションが load-bearing か」を測る道具**なので、テストを書いたら**その場で必ず 1 つ当てる**（この 2 件は §5.2 の追記のとおり撤回し、スタブとして残さなかった）。なお ② の真の不変量（manifest の**拒否が 0 件**）は**別ファイルで既に固定済み**だった — **重複した落ちないテストを足すことは、検査を増やすことではなく負債を増やすこと**である
15. **到達性は推移する — 1 ホップの関係を数えて「到達可能」と呼ぶと、死んだ経路が生きて見える**（B-3） — §5.1 の `motivation_arbiter` 行は「**❌ 生** — `autonomous_controller.py` が import している」と書いていた。import は**事実**だが、**その importer 自身が import 元ゼロ**である。**「このモジュールを名指しするものがあるか」と「このモジュールは実行されるか」は別の問い**で、前者は推移しない。`AutonomousController` 経路（約 700 行）は `docs/self-development.md` の冒頭図に**入口として描かれている**のに、実測の入口は `runtime.py:1586` が直接構築する `AutonomousLoop`。**この型は 3（構築されるが参照されない）を隠す** — 死んだ経路の上のコードは「呼び出し元がある」ように見えるので、登録簿そのものが生存を主張してしまう。**同じ誤りは逆方向にも出る**: 最初の走査は「**パッケージ外から** import されているか」だけを問い、**5 つ**を到達不能と報告したが、`planner`（`autonomous_loop` 経由）・`l2_mind`・`l2_models`（パッケージ `__init__` 経由）は到達可能で、正解は **2 つ**だった。**判定法は「根を 1 つ名指しし、そこまでの連鎖を示す」** — 根とは実際に走るもの（`runtime.py`、テスト、CLI）である。ピンはホップではなく**連鎖**を assert する（`tests/test_autonomous_execution_path_is_single.py`）
16. **宣言は「構築」でしか検査されない — 生きた書き込み経路が構築せず代入するなら、宣言は系の半分しか縛らない**（B-20） — 設定スキーマは **27 フィールド**に `ge`/`le` の境界を宣言しており、それらは**構築時**に強制される。しかし生きたプロセスの唯一の書き込み経路 `SettingsStore.update_section` は、提案設定を **`setattr` で無検証に組み立てて**から `validate_settings_change` を呼ぶ。そしてそのバリデータが再検査する境界は **1 つだけ**（`max_autonomous_runs_per_hour > 100` — しかもそのフィールド自身の `le=100` の**写し**で、構築時に拒否される値をもう一度弾いているだけ）。**結果、27 のうち 26 が API 経由で突破でき、値はディスクに残る**（すべて実測 — 実物の `SettingsStore` を `tmp_path` に対して駆動し、読み戻して確認）。**この型は 2（真実源が 2 つ）と 12（検査は在るが発火しない）の合成**だが、機構が違う: 検査は**存在し、発火もする**（1 フィールドについて）。欠けているのは**範囲**である。判定法は「**この制約は、どの経路で強制されているか**」— 宣言・構築・書き込みの 3 つを別々に問い、**書き込み経路を実際に駆動して**確かめる。なお、この形は**上書きを許すフィールドだけ**が対象で、`getattr(obj, "name")` のように**文字列で名前を渡す**アクセスは属性ベースの検出器から見えない（今回 3 度目の偽陰性）— 発見器は属性と文字列の両方を見る必要がある。**A-9 で修復済み（2026-09-29）** — 生きた書き込み経路が**構築**するようになり、27 の境界すべてが書き込み時点で強制される（実測 **突破 0 / 阻止 27**）。この型の要点は残る: **宣言・構築・書き込みの 3 つを別々に問い、書き込み経路を実際に駆動して確かめる**。なお**唯一の手書きの写し**（`validate_settings_change` の `> 100`）は**残した** — 構築が先に拒否するので**ストア経由では到達不能**になったが、この関数は public（`settings/__init__.py` が再輸出）で契約が独立しており、消すと `tests/test_guarded_settings_fields.py` が記録している**唯一の実例**が消えるため。この判断はピンとソースのコメントに明記した（**「残した」理由も記録しないと、次に読む者は「気づかなかった」と読む**）
17. **名簿の誤りは鳴るが、順位の誤りは鳴らない**（B-21） — `web-ui/src/pages/Settings.tsx` の `editableSettings` は 2 つの集合を持つ。**どのコントロールを出すか**は `GET /api/settings` のペイロードから**発見**するので、スキーマが変わっても古くならない（UI 側に名簿が存在しない）。しかし**どれを先頭に出すか**は 15 件の**手書きの `preferred`** で、そのうち **5 件はどの設定フィールドとも一致しない**（`display_privacy_mode` / `notifications_enabled` / `daily_budget_usd` / `monthly_budget_usd` は `web-ui` にしか存在せず、`memory_budget_tokens` は `context_builder` の実行時属性）。**これが無音なのは機構が違うからである** — 名簿の欠落は**引く側が落ちる**（capability が見つからない → `NOT_FOUND`）、順位の欠落は**引く側が黙って既定を返す**（`Set.has` が false → 並び順が変わらないだけ）。**同じファイルの中で、同じ「手書きの一覧」が片方だけ無音で腐る。** 判定法は「**この一覧の要素が何も指さなかったとき、何が起きるか**」— 例外か、`false` か、既定値か。`false` や既定値なら、それは検証されていない。型 5・型 12 の親戚だが**検査が存在しない**点が違う — 比較すべき相手（スキーマ）は存在するのに、**誰も比較していなかった**。あわせて**発見方式そのものの副作用**も実測した: 可視集合は `result.length >= 24` の切り捨てと `slice(0, 32)` で決まるので、**フィールドの宣言位置が「利用者に見えるか」を決める** — 早い位置に 2 つ足すと**記録済みの死んだフィールドが 1 つ可視窓から押し出される**（変異 M11 で実測）。誰も記録を触っていないのに、設定画面の中身が変わる
18. **テストダブルが実クラスに無いメソッドを定義すると、テストは生産が通らない枝を通る — そしてその枝を消しても緑のまま**（2026-10-01） — `PresentationManager.dismiss` は `getattr(mgr, "dismiss_notification", None)` を試し、`None` なら `getattr(mgr, "dismiss", None)` に落ちる。**生産が渡す実 `NotificationManager` は `dismiss` だけを定義する**ので、**最初の探索は生産では常に `None`** ＝ **生産は常にフォールバックを通る**。ところが `dismiss_notification` を定義するクラスは**リポジトリ全体で 1 つだけ**で、それが **テストダブル**（`tests/test_presentation_engine.py` の `FakeNotificationManager`）— **この経路を覆う唯一のテストはそのダブルを渡している**ので、**テストは生産が決して通らない枝を通る**。**帰結は推論ではなく実測**: フォールバックを削除する（＝明白な「これは死んだコードだ」という掃除）と**フルスイートが 1923 passed / 8 skipped のまま緑**（407.74 秒）で、**生産は黙って通知の dismiss をやめ、何も落ちない**。型 7（テストがバグを覆い隠す）の親戚だが機構が違う — あちらは**テストが間違った期待を持つ**、こちらは**テストが間違った相手を差し込む**。**判定法は「この分岐を、生産と同じ型で通るテストがあるか」** — `getattr` の優先→フォールバック鎖では、**優先名が生産に存在しない**なら**フォールバックが本線**であり、ダブルが優先名を定義していると**本線が無検査になる**。**緑は「覆っている」証拠にならない**（記録: `tests/test_dismiss_fallback_is_uncovered.py`、`DELEGATION.md` §4 項目 21）
19. **生きた面は健全とは限らない — 「producer が実在する」は「健全」ではない**（2026-10-03） — push ルートの集合を **producer の有無**で bound しても、答えるのは「生産するか」だけである。**生きたルートは、自分を生かしている資源そのものを漏らしうる**。実測: `GET /api/presentations/stream` は `event_manager.subscribe()` を **route 関数スコープ**で呼び（リクエストごと・generator 起動前）、**返り id を捨てる**ので誰も解放できず、**route 実行後 1 購読者・クライアント切断後も 1**。兄弟の `routes/ui.py` は id を保持し `finally` で解放する（**1 → 0**）。**「生きた」「未購読」「健全」は 1 つの数ではなく 3 つの軸** — 生きたまま未購読で漏れる（このルート）／生きたまま購読される（UI ストリーム）／両端とも死んでいる（chat SSE）。producer 判定自体にも罠がある: **接続ごとの queue への `.put(` は producer だが、共有 registry への `.put(` は producer ではない**（chat SSE の形 — 書かれても誰も読まない）。型 6（構築されるが参照されない）の鏡像で、機構が違う — あちらは**参照が無い**、こちらは**参照が解放されない**（記録: `tests/test_presentation_stream_is_sound.py` — **2026-10-03 に修正**、`..._leaks_a_subscriber.py` から改名。`DELEGATION.md` §4 項目 26）。⚠️ **この実例はさらに深い第 2 の欠陥を隠していた** — 修正の途中で、ハンドラが **2 引数**なのにバスは **1 引数**で呼ぶため**一度も走っていなかった**ことが判明した（購読者数は正しいままなので**数では見えない**）。**漏れだけ直しても配信は動かない** — これが「健全」が 3 つ目の軸である証拠である

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
| ~~`aegis_ai/permissions/`~~ | 承認の第 3 面・呼び出し元ゼロ | ✅ **2026-10-03 に削除**（オーナー決定）。当時の判定「生きたテストが import しているので**パッケージ削除は不可**」は、**テスト側を先に更新すれば解けた** — `test_forced_gate_stays_retired.py` の 3 本を「**パッケージが無い** ∧ **`src/` に importer が 0**」に置換し、`test_goal_alignment.py` §33 の 4 本・`test_mission_contract_acceptance.py` の 1 本を削除（変異 2/2、影響スイート 123 passed） | **実行済み** |
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
  **⚠️ 名前の衝突（2026-09-30 実測）**: この `REDACTION_PATTERNS` は**削除されたモジュールの中の**
  定数であって、**生きた** `ai-server/src/aegis_ai/llm/redaction.py:18` の同名定数とは**別物**。
  実測: live な方は **8 パターン**（password/token・SSH 鍵・PEM・JWT・AWS 鍵・カード・メール・電話）で
  **OTP 規則を持たない** — `git grep 'd{4,8}' -- ai-server/src ai-server/tests` は **0 件**。
  この節の「OTP 規則」はすべて**削除済みモジュールの話**である。
- `contains_password_field(ui_tree)` — UI ツリーのパスワード欄検出。

**live 経路の実測**: `android-server.notification.get_notifications` は**配線済み**
（`integrations/android/capability_mapper.py:58`）で、端末の通知は実際に AEGIS へ流れ込む。
かつて `notification/router.py` には `_redact_if_needed` があり、**外向きチャネル（LINE/Discord/Email）宛のときだけ**
本文を空にしていたが、**2026-09-30 に削除した**。理由は 2 つで、どちらも実測にもとづく:
① 空にした本文がそのまま配送されるので **ユーザーが与えた許可が無意味になる**（egress 許可制と正面から矛盾する）;
② `notification.body` はローカルチャネルと**同じオブジェクト**なので、外向きチャネルを 1 つでも宣言すると
**ダッシュボードの表示まで本文を失う**。今は **egress ゲートが唯一の制御点**である。
端末から取り込む時点では今も何も絞っていない。

**それでも移植しなかった理由**: これは製品判断であって機械的な移植ではない。とくに
`REDACTION_PATTERNS` の OTP 規則 `(?<!\d)\d{4,8}(?!\d)` は **4〜8 桁の数字を無差別に潰す**ので、
「確認コードを読み上げて」という正当な用途を壊す。採否はオーナーの判断。
**（この `REDACTION_PATTERNS` は削除済みモジュールのもので、live な `llm/redaction.py` には
OTP 規則が無い — 上の「名前の衝突」を参照。）**
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
  一度も走らないことが分かった**（**A-12**）。つまり **`list_for_llm` に効いている
  フィルタは 0 個**で、この論証はさらに強くなる。
  **同日、A-12 を ②（機構ごと削除）で閉じた**ので、`list_for_llm` はフィルタ引数そのものを持たない
  — 「走らないフィルタ」ではなく「存在しないフィルタ」になった。決定と戻し方は `DELEGATION.md`。
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

> **2026-10-03 更新 — 「到達不能の固定」は「削除」に置き換わった。** オーナーが `aegis_ai/permissions/` の
> **削除**を決めたので（`DELEGATION.md` §4 項目 3）、上の「到達不能であること」という肯定は**空虚**になった
> （対象が無ければ何も主張しない）。ピンは **`test_the_permissions_gate_package_is_gone`** に置き換えた —
> **ディレクトリが存在しない** ∧ **`src/` に importer が 0** の**独立した 2 事実**を固定する。変異 **2/2**
> 捕捉（M1 パッケージ再作成 / M2 `runtime.py` に import 追加）。**削除は「到達不能の固定」より強い** —
> 誰も取らない面でも、**取れる面ではあった**。

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
| `ConfirmationStore.mark_executed` / `mark_failed` | **生きた契約** | `test_forced_gate_stays_retired.py:66-70` が「**意図的に**この tuple に入れない」と文書化している。将来の配線点 |
| `profile.requires_approval()` | **生きた契約** | テストが読む。`requires_approval_for` は宣言済みの agent-profile データフィールド |
| `risk.approval_mode`（5 マニフェスト） | **消費されている** | `capability_catalog.py:163-164`・`:550-555`・`:586-593`、`folder_registry.py:254`、`capability_overrides.py` |
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
> 同じ関数 `_current_interruption_cost` は **4 つ目の値 `0.15`** も返す（`:880` agent state が無い /
> `:890` snapshot が例外）。旧ピンは `_RECORDED_COST_DEFAULT = 0.2` しか記録しておらず、
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
`backup/retention.py:60` は `settings.memory.episodic_retention_days` を `max_age_ms` に変換して
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
| P2-4 | ✅ **決着**（**2026-09-30 オーナー決定 = C-1「維持」**）— `/approve` `/modify-and-approve` `/cancel` の fresh passkey（15 分）は**そのまま**。根拠: 再認証の契機はこれ 1 つで**負担に上限が付く**。短くすると 1 タスクで 2 回聞かれ**北極星に反する**。比例の根拠は「頻度の上限」であって危険度への比例ではない。正典は `DELEGATION.md` §2 の C-1（**§0.2 の行は契約どおり削除済み** — 決定済みの行は残さない） |
| P2-5 | 長期（**在庫の正典は §3.2**。この行は元の 6 項目の記録で、状態は 2026-10-01 に実測して付け直した）: ~~vision のローカル化~~ ✅ 配線済み（`local_vision` → `localhost:11434`、egress は止めない）/ ~~gRPC TLS~~ ❌ 未配線（`DELEGATION.md` §4 項目 14）/ **Room 実機プロバイダ** ❌ Orange Pi 待ち / ~~cross-device context~~ ✅ 2026-09-30 / ~~音声 I/O~~ ✅ 2026-09-30 / **multi-user** ❌ v1 スコープ外 |
| P2-6 | ✅ **決着**（**2026-09-30 オーナー決定 = B-2「③ 現状維持（固定済み）」**）— `aegis_ai/evaluation/` の死んだ部分グラフ（1,104 行）は**削除も配線もしない**。配線は期待の書き直しを伴う製品判断（`delete_file` → `ALLOW_WITH_AUDIT` は**今は正しい**）で、**固定済みなので急がない**。正典は `DELEGATION.md` §2 の B-2（**§0.2 の行は契約どおり削除済み**）、記録は §5.7 と `tests/test_evaluation_pack_is_dead.py` |
| P2-7 | ✅ **決着**（**2026-09-30 オーナー決定 = B-1**）— ① コスト表の中央 2 値は**入れ替え済み**（実測: `suppress` 0.9 / `batch_later` 0.55 / `important_only` 0.4 / `interruptible` 0.1 — 受容表と単調に整合）。② は**実測で定義が不要になり実行済み**: `_expected_usefulness(task)` が圧力（0–10）を既存変換 `min(1.0, pressure / 10.0)` で正規化し、`:3381-3382` で `interruption_cost=self._current_interruption_cost()` と**並んで**生きた `PresentationRoutingPolicy().decide` に渡される。~~③~~ は撤回済み。正典は `DELEGATION.md` §2 の B-1（**§0.2 の行は契約どおり削除済み**）、ピンは `tests/test_interruption_cost_vocabulary.py` |

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

---

## 7. 引用の掃討記録（サイクル 31、2026-10-05）

> **本レポートの「ファイル名を持たない」裸の `:NNN` を 90 件すべて測った。** サイクル 29 は**ファイル名つき**の引用を掃討したが、裸の `:NNN`（持ち主を主語から推論するしかない）は未着手だった。90 件は 5 つに割れた: **偽陽性 4**・**本レポート自身の日付つき注記の中 28**（サイクル 29/30 の掃討記録そのもの）・**日付つき叙述／台帳行として据え置き 15**・**腐っていたので修正 4**・**実測して正しいと確認 39**。
> ⚠️ **腐っていたのは 2 つの事実だけ**（4 件は写しの重複）。① `_expected_usefulness(task)` と `_current_interruption_cost()` が**並んで** `PresentationRoutingPolicy().decide` に渡される場所: `:3218-3219` → **`:3381-3382`**（写し **3** — 本レポート §3.1 と §0.x の P2-7 行、`DELEGATION.md` の B-1② 行）。② `risk.approval_mode` の消費サイト: `capability_catalog.py:165-166`→**`:163-164`**（override 適用）・`:563-568`→**`:550-555`**（書き）・`:599-606`→**`:586-593`**（読み）、`folder_registry.py:258`→**`:254`**（写し **2** — 本レポート §5.4 と `AGENT_PROGRESS.md`）。
> ⚠️ **どちらも「書かれた時は正しかった」ことを `git` で確認した**（`:3218` は `a75c3db` で `expected_usefulness=` の行、`capability_catalog.py:599` と `folder_registry.py:258` は `d483813` で `approval_mode` の行）。つまり**誤った主張ではなく、腐った写像**なので現在の番号へ付け替えた。置換は**すべて同じ長さ**（`165-166`→`163-164` など）なので**バイト数は不変**（`503390`・`184139`・`186434`）。
> ⚠️ **据え置いた腐り（記録）**: ① §3.1 と §5.8 の**日付つき叙述**の `:1379`（正 `:1583`）・`:2806-2812`・`:1051`・`:868`（正 `:872-875`）・`:708`（正 `:880`）・`:712`（正 `:890`）— これらは**同じ段落にファイル名つきの引用**（`autonomous_loop.py:1389`→正 `:1589`・`:1050`）を併せ持つので、裸の分だけ直すと**段落が半端に掃討された状態**になる。段落ごと直すのは次のサイクル（**→ サイクル 34 で実施済み**、§8）。② `:917`/`:909`（`manager_routes.py` の `presentation_stream` 欠陥）は**修正前の番号**（サイクル 29 の判断と同じ）。③ §5.1 の裸の `165 / 521 / 563` は **2026-09-28 のスナップショット**で、判定（「保留」）は §5.4 に**上書き済み**。
> ⚠️ **走査器の盲点**: 裸の番号が**コロン無し**で並ぶ形（`（165 / 521 / 563）`）は `:NNN` の走査に**掛からない** — §5.1 のそれは `approval_mode` を grep して初めて出た。**「走査した」は「全部見た」ではない。**
> ⚠️ **同名ファイルの罠（実測）**: `event_bus.py:241`/`:243` は**正しい**が、それは `ai-server/src/event_bus.py`（262 行）の話で、`aegis_ai/event_bus.py` は**3 行の再輸出シム**。basename だけの引用は**構築上曖昧**。

## 8. §3.1・§5.8 の段落まるごとの掃討（サイクル 34、2026-10-05）

§7 の ① で「次のサイクル」に据え置いた §3.1・§5.8 の**日付つき叙述**を、**段落ごと**掃討した。裸の番号
だけを直すと段落が半端になるので、同じ段落のファイル名つき引用も同時に直した（**11 箇所 / 8 行**）。

| 旧 | 正 | 実測の根拠 | 行 |
|---|---|---|---|
| `:1379` | `:1583` | `autonomous_loop.py:1583` = `if not source_desire:`（`:1584` が `return 0.0, ""`） | L93・L871 |
| `autonomous_loop.py:1389` | `autonomous_loop.py:1589` | `:1589` = `related_desire=source_desire,` | L93・L870 |
| `autonomous_loop.py:1050` | `autonomous_loop.py:1228` | `:1228` = `reflection = self._reflection.reflect(`（唯一の呼び出し元） | L93・L872 |
| `:2806-2812` | `:3067`・`:3072` | `:3067` = `task_id=task_id,` / `:3072` = `source_desire=desire_name,` | L884 |
| `:1051` | `:1228-1229` | `:1229` = `task_id=f"auto_{int(time.time() * 1000)}_{i}",`（reflect 時に合成） | L884 |
| `:868` | `:872-875` | **所有者は段落の主題 `core_capabilities.py`**（最後に名指しされた `autonomous_loop.py` ではない）: `:872-875` = `fields = {key: params[key] for key in self._CONFIRMATION_FIELDS …}` | L886 |
| `:708` | `:880` | `:880` = `return 0.15`（`if agent_state is None:` の下） | L1585 |
| `:712` | `:890` | `:890` = `return 0.15`（snapshot の `except` ハンドラ内） | L1586 |

⚠️ **裸の番号の所有者は段落の主題**であって、最後に名指しされたファイルではない — `:868` は
`autonomous_loop.py` ではなく `core_capabilities.py` の行だった（`core_capabilities.py:872-875` が
`params` の素通しそのもの）。

⚠️ **ノートは書き換えていない**: §7 の L2421 は自分自身の old→new 写像を持つので、番号はそのまま残し、
実施済みの印だけを足した（`段落ごと直すのは次のサイクル` の後）。

**据え置き（記録）**: ② `:917`/`:909`（`manager_routes.py` の `presentation_stream`）は**修正前の番号**の
まま（サイクル 29 と同じ判断）。③ §5.1 の裸の `165 / 521 / 563` は 2026-09-28 のスナップショットで、判定は
§5.4 に上書き済み。④ `docs/*.md` の **76 件**のファイル名つき引用はサイクル 34 で走査し**すべて健全**
（2 件の空行着地は `jev-l1-verification-2026-10-02.md` の**日付つき記録**なので据え置き）。

**長さ**: 506555 → 本節の直前で 506569 B（引用の修正で +14、CRLF 維持）。

## 9. サイクル 36 の掃討記録（2026-10-05）

`AGENT_PROGRESS.md` の引用を掃討した（サイクル 36）。本ファイル側で動いたのは **2 箇所**:

- **L1348** `test_forced_gate_stays_retired.py:61-65` → **`:66-70`**（`AGENT_PROGRESS.md:1103` と同一事実の写し）。
  書かれた時は正しかった（`d483813`〜`a75c3db` は `mark_executed` が **61** 行目）が `e125f04` で **+5 ずれ**。
- **L624 のノートの訂正** — サイクル 31 は `:61-65` を「範囲としては成立している」と判定したが、その範囲は
  **同じコメントブロックの別段落**を指していた。**「非空か」ではなく「主張の句を含むか」**で判定すべきだった
  （対照: `egress/startup.py:59-76` は開始が空行でも主張を覆っているので据え置きが正しい）。**L624 の文面は
  その場で直した**（行数は変えていないので以下の行番号は動いていない）。

**⚠️ 削除の掃討は 2 文書を漏らしていた**: `818105f`（`aegis_ai/permissions/` 削除）は 7 文書を掃討したが、
`AGENT_PROGRESS.md`（B-16 節）と `BUG_REPORT.md`（§33）が漏れた。両方に追記した（それぞれのファイル参照）。

**長さ**: 509294 → **本節の直前で 509502 B**（L1348 の付け替えは同幅、L624 の訂正で +208。CRLF 維持）。
