# JEV (L1) 動作確認レポート — 2026-10-02

> **対象**: TypeSafe System One (`jev-latest`) — AEGIS の L1 レイヤ
> **範囲**: 実際の API を呼んでの動作確認。**L2 の DeepSeek は一切呼んでいない。**
> **結果**: チェック **20/20 合格**。ただし**設定が意図どおり効いていない箇所を 4 件**発見（§5.1〜§5.4。
> ほかに小項目 §5.5・§5.6）。**うち 1 件（§5.1）は「L1 が JEV に一度も到達しない」**。

> **⚠️ これは 2026-10-02 時点の記録です。以下はその後変わっており、読み替えが必要です:**
> - **§5.1 / §0 の判定 4・4b → 解消**。`f8e0b06`（2026-10-03）で `llm.yaml` を `mode: "cloud"` にし、
>   `privacy.egress_allowed_hosts` が `api.typesafe.ai` を許可したので、**L1 は JEV に到達する**（実測）。
> - **§5.6 → 解消**。`EgressGate.status()` は「ゲートが閉じていること」ではなく「**開いているなら
>   許可先が限定されていること**」を検査するようになったため、3 つの錠が揃った状態は**違反ではなく正常**。
> - **§6「実サーバ起動経由の L1 は未検証」 → 検証済み**。`get_runtime()` 経由で
>   `publish_event` → L1 購読 → JEV を実行し、`data/audit.db` に `provider=typesafe` /
>   `model=jev-latest` / `source=l1_router.observe` を確認。
> - **§5.2 / §5.3 / §5.4 / §5.5 → 修正済み**（2026-10-03、本ファイルを更新したコミット）。
>   `timeout_seconds` の引き回し、`detail` の読み取り、無効パラメータの明示、成功ログの追加。
> - **副作用 1 件**: `mode: cloud` では `vision_observation` が `local_vision` に remap されなくなり、
>   宣言先の Aliyun ホストは未許可なので **vision は Mock に劣化する**（`verify_egress_configuration`
>   の `reachable_destinations` が「宣言済み・未許可」として報告する）。

---

## 0. 結論（先に要点）

| # | 判定 | 内容 |
|---|---|---|
| 1 | ✅ | **正常系は期待どおり**。L1 observation も tool gate も実 API から妥当な応答が返る |
| 2 | ✅ | **異常系はすべて「送信せず失敗」**。鍵なし / 未対応呼び出し / ゲート閉 の 3 件は **HTTP 呼び出し 0 回** |
| 3 | ✅ | **実 API のエラーも正しく報告される**（401 / 400）。429 はリトライ、401 はリトライしない |
| 4 | ⚠️ | **【重大】`mode: "local"` のため、L1 は JEV に到達しない**（§5.1）。resolver は仕様どおりで、**既存テストがこの remap を固定している**。欠陥は「`llm.yaml` が typesafe/jev-latest と宣言し続けている」点 |
| 4b | ⚠️ | **その remap はラベルから見えない**。監査の `profile_id`・スパンの `llm.profile`・ダッシュボードの指標はすべて**要求側の名前**（`l1_default`）で、実際に動いたのは Ollama（§5.1） |
| 5 | ⚠️ | **構築経路によって `timeout_seconds` が 20 秒 / 30 秒に割れる**（§5.2） |
| 6 | ⚠️ | **API のエラーメッセージが捨てられている**（§5.3） |
| 7 | ⚠️ | **`max_tokens` / `temperature` / `reasoning_level` / `max_tool_rounds` は JEV には送られない**（§5.4） |

---

## 1. 対象の特定

- **JEV = TypeSafe System One の `jev-latest` モデル**
  - エンドポイント: `https://api.typesafe.ai/v1/systemone`
  - 実装: `ai-server/src/aegis_ai/llm/providers/typesafe_provider.py`
  - プロファイル: `ai-server/config/llm.yaml` の `l1_default`（L1）と `jev_decision`
- 認証: `TYPESAFE_API_KEY`（リポジトリ root の `.env` に設定済み。長さ 108、`apikey_` で始まる）
- 実行環境: Python 3.13.14 / venv `aegis`
- 疎通: `GET` に対して **405**（POST 専用）→ エンドポイントは生存

### JEV プロバイダの仕様（ソースから確定）

`generate()` は **3 種類の呼び出ししか受け付けない**。それ以外は失敗を返す。

| 判定キー | 経路 | 送る質問 |
|---|---|---|
| `context_meta["layer"] == "L1"` または `context_meta["source"] == "l1_router.observe"` | L1 observation | 6 問（intelligence / value / priority / summary_bucket / intent_class / direct_handle） |
| `context_meta["caller"] == "chat_tools.tool_gate"` | 真偽ゲート | `use_tools` |
| `context_meta["caller"] == "chat_tools.satisfaction_gate"` | 真偽ゲート | `satisfies` |
| 上記以外 | **失敗**（送信しない） | — |

---

## 2. 確認手順

1. **設定の解決を確認** — `LLMSettingsResolver` で `l1_default` を解決し、`mode` による差を見る（`local` / `cloud` の両方）。
2. **egress ゲートの扱いを確認** — 既定は外部宛を拒否するため、この実行に限り `api.typesafe.ai` を許可して構成。
3. **正常系 2 件** — L1 observation / tool gate を **実 API** で呼ぶ。
4. **異常系 7 件** — 鍵なし・未対応呼び出し・ゲート閉・実 401・実 400・429 リトライ・到達不能。
5. **ログと監査** — 関連ロガー（`aegis_ai.egress.gate` / `aegis_ai.llm.providers.typesafe` / factory / gateway）を捕捉し、監査エントリを確認。
6. **送信リクエストの捕捉** — `urlopen` を差し替えて、実際に送られた URL・メソッド・ヘッダ・タイムアウト・**ボディ**を記録。

> ⚠️ **この確認のために egress を一時的に許可した。** `config/settings.json` も `llm.yaml` も**書き換えていない**（スクリプト内でプロセス内ゲートを構成しただけ）。したがって**リポジトリの出荷状態は「外部宛は拒否」のまま**である。

---

## 3. 結果

### 3.1 設定の解決（A）

| ケース | 解決結果 | 判定 |
|---|---|---|
| `mode: local`（**出荷状態**） | provider=`openai` / model=`qwen2.5:3b` / base_url=`http://localhost:11434/v1` | ⚠️ **JEV に到達しない** |
| `mode: cloud` | provider=`typesafe` / model=`jev-latest` / base_url=`https://api.typesafe.ai/v1/systemone` / api_key_env=`TYPESAFE_API_KEY` / timeout=20 / max_tokens=1024 / temperature=0.0 / reasoning=low / max_tool_rounds=1 | ✅ プロファイルどおり |

### 3.2 正常系（B, C）— 実 API

**B. L1 observation**（1 回の HTTP 呼び出し、所要 0.99 秒、**1270 トークン**）

```
{"meaning": "user opened the AEGIS dashboard",
 "value": 0.3375, "priority": 0.1,
 "required_intelligence": "low", "confidence": 0.678,
 "summary_bucket": "user_state",
 "observed_action": "user opened the AEGIS dashboard",
 "possible_intent": "Likely updates current user state or context",
 "should_execute_directly": false,
 "candidate_capability_id": "", "candidate_args": {}}
```

→ 期待する **11 キーがすべて揃い**、`confidence` は 0..1、`required_intelligence` は `low/medium/high` のいずれか。内容も入力イベントと整合。

**C. tool gate**（実 API）

```
{"use_tools": true, "reason": "typesafe_probability=0.980"}
```

→ 「スクリーンショットを撮って」に対して `use_tools=true`（確率 0.980）。妥当。

### 3.3 異常系（D）

| # | ケース | 結果 | 送信 | 判定 |
|---|---|---|---|---|
| D1 | 鍵なし | `TypeSafe API key is not configured` | **0 回** | ✅ 送信せず失敗 |
| D2 | 未対応 caller | `only supports L1 observation and chat first-stage boolean decisions` | **0 回** | ✅ 送信せず失敗 |
| D3 | egress ゲート閉 | `Egress gate denied TypeSafe destination …` | **0 回** | ✅ 送信せず失敗 |
| D4 | **実 401**（不正な鍵） | `TypeSafe API error 401` | 1 回 | ✅ リトライせず即失敗 |
| D5 | **実 400**（未知モデル） | `TypeSafe API error 400` | 1 回 | ✅ 報告される |
| D6 | 429 → 成功（模擬） | 2 回目の試行で成功 | 2 回 | ✅ バックオフして再試行 |
| D7 | 到達不能ホスト | `TypeSafe request failed: [WinError 10061] …` | **3 回** | ✅ 3 回試行後、失敗を報告 |

**D1〜D3 が「送信 0 回」であることが重要** — 失敗しても外部に出ない（fail-closed）。

### 3.4 ログ出力（E）

捕捉した 9 件のうち、実質は次のとおり。

```
INFO     aegis_ai.egress.gate :: egress allow component=llm.factory purpose=llm.chat
                                  destination=https://api.typesafe.ai/v1/systemone
                                  reason=explicitly allowlisted external destination
INFO     aegis_ai.egress.gate :: egress allow component=llm.typesafe_provider … (同上)
WARNING  aegis_ai.llm.providers.typesafe :: No TypeSafe API key set. Set TYPESAFE_API_KEY.
WARNING  aegis_ai.egress.gate :: egress deny component=llm.typesafe_provider purpose=llm.chat
                                  destination=https://api.typesafe.ai/v1/systemone
                                  reason=external egress is disabled (single constraint)
```

- ✅ **egress の判断は必ず 1 行ログに出る**（許可=INFO / 拒否=WARNING）。宛先・purpose・理由が読める。
- ⚠️ **成功時のログが無い**（§5.5）。呼び出しの記録は**監査のみ**。

### 3.5 監査（F）

`llm_call` が **8 件**記録され、`success` と `error` が区別できる。例:

```
llm_call decision=success {'model': 'jev-latest', 'provider': 'typesafe', 'duration_ms': 993.4}
llm_call decision=error   {'model': 'jev-latest', 'provider': 'typesafe', 'duration_ms': 0.0,
                           'error': 'TypeSafe provider only supports …', 'api_key_configured': True}
llm_call decision=error   {'model': 'jev-latest', 'provider': 'typesafe', 'duration_ms': 7582.1,
                           'error': 'TypeSafe request failed: [WinError 10061] …'}
```

`egress_decision` も許可・拒否の両方が記録される。

### 3.6 実際に送られたリクエスト（捕捉）

```
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer apikey_…
Content-Type: application/json
timeout = 20

{"model": "jev-latest",
 "state": {"event_summary": "…", "event_id": "…", "event_json": {…},
           "aegis_context": {…}, "system_role": "You are AEGIS L1."},
 "questions": {required_intelligence, value_band, priority_band,
               summary_bucket, intent_class, direct_handle}}
```

→ **model / base_url / 認証ヘッダ / timeout は正しく反映**。ただし **`max_tokens` と `temperature` は送られていない**（§5.4）。

---

## 4. 再現方法

検証スクリプトは一時ディレクトリに置き、リポジトリには追加していない。

```
# ai-server ディレクトリで実行
CODEBUDDY_SAFE_DELETE_ENABLED=0 <venv>/Scripts/python.exe <script>.py
```

- スクリプトは `sys.path` に `ai-server/src` を追加し、root の `.env` を読む
- `configure_egress_gate(settings_store=…)` で**このプロセスに限り** `api.typesafe.ai` を許可
- `urlopen` を差し替えて送信内容と呼び出し回数を記録

---

## 5. 気づいた点

### 5.1 【重大】`mode: "local"` のため L1 は JEV に到達しない

`llm.yaml` は `mode: "local"`。`settings_resolver.py` の `_LOCAL_PROFILE_MAP` は

```
"l1_default": "local_decision"     # → provider=openai / model=qwen2.5:3b / localhost:11434
"jev_decision": "local_decision"
```

を持ち、`resolve(profile_id="l1_default")` は **`local_decision`（Ollama）に置き換わる**。

#### remap が実際に発火する条件（3 つすべてを実測で確認）

`resolve()` の分岐は `if mode == "local" and profile_id in self._LOCAL_PROFILE_MAP:` のうえ、
さらに `if local_name in self._profiles:` を要求する。**3 つとも成立している**:

| # | 条件 | 実測 |
|---|---|---|
| 1 | `mode == "local"` | `config/llm.yaml:9` = `mode: "local"` ✅ |
| 2 | `"l1_default"` がマップにある | `settings_resolver.py:91` ✅ |
| 3 | 写し先 `local_decision` が `llm.yaml` に定義されている | `config/llm.yaml:177`（`provider: openai` / `model: qwen2.5:3b` / `http://localhost:11434/v1` / `timeout_seconds: 60`）✅ |

→ **`resolve("l1_default")` は `local_decision`（Ollama）を返す**。プローブでも実測済み（§3.1）。
つまり **`llm.yaml` の `l1_default`（provider: typesafe / model: jev-latest）は、出荷状態では一度も使われない**。

**掃討範囲**（この主張の被覆を明示する）。まず `ai-server/src/` 内の参照は **6 件のみ**
（`grep -rn 'l1_default' ai-server/src/`、`__pycache__` の 2 件を除く）:

| # | 位置 | 役割 |
|---|---|---|
| 1 | `llm/layer_profiles.py:34` | `LAYER_L1 → "l1_default"`（層→プロファイルの対応表） |
| 2 | `llm/settings_resolver.py:91` | `"l1_default" → "local_decision"`（**remap 本体**） |
| 3 | `web/chat_tools.py:868` | tool gate が `profile="l1_default"` を渡す |
| 4 | `web/chat_tools.py:960` | satisfaction gate が同様に渡す |
| 5 | `web/chat_tools.py:104` | 失敗ハンドラの**イベントラベル**（解決経路ではない） |
| 6 | `web/routes/l1_routes.py:114` | **メトリクスのフィルタ**（下記） |

リポジトリ全体を **大文字小文字を無視して**掃討した結果（`grep -rniI 'l1_default|l1default|l1-default'`、
`__pycache__` / `node_modules` / `.git` / `dist` を除外）。`src/` の 6 件以外は次のとおりで、
**いずれも「層の名前」としての参照であり、JEV を使う経路ではない**:

| 区分 | 件数 | 内容 |
|---|---|---|
| 設定 | 1 | `config/llm.yaml:112` — `l1_default` プロファイル**宣言**（typesafe / jev-latest） |
| テスト | 約 20 | `tests/` の profile 解決・chat_tools・l1_routes 系。`test_local_llm_path.py:191` は **`mode=local` で cloud 宛にならないこと**を全プロファイルについて検査しており、**この remap を前提にしたテストが既にある** |
| ドキュメント | 3 | `DASHBOARD_V3_PLAN.md`、`docs/feature-catalog.md:417` |
| **git 管理外** | — | `.trae/documents/`（後述）と `build/_core.txt`（`.gitignore:17`） |

実際の経路:

- `chat_tools.py:868` / `:960` → `LLMGateway.generate(..., profile="l1_default")` → `_resolve("l1_default")` → **`local_decision`**
- `intake/l1_router.py:250` は `request_json(layer="L1", …)` を呼び、`gateway.py:629` の `profile_id = layer_to_profile(layer)` を経由して同じ `l1_default` になる（**文字列 `"l1_default"` は書かれておらず、対応表 #1 経由**）

**監査には「要求した名前」と「実際に使った provider」が別々に入る。** `gateway.py:205-209` は
`meta.setdefault("profile_id", profile)` で**要求側**（`l1_default`）を記録し、同じ辞書に**解決後の**
`provider` / `model`（`openai` / `qwen2.5:3b`）も入れる。したがって監査エントリ自体は真実を含むが、
**`profile_id` だけを見て「JEV が動いた」と読むのは誤り**。

> ⚠️ `l1_routes.py:114` は `profile_id == "l1_default"` **かつ** `source == "l1_router.observe"` を
> `event_driven_llm_calls_60s` として数える。これは**層の流量**を見る指標としては remap をまたいで正しく
> 動く（要求側の名前で数えているため）が、**「JEV の使用量」ではない**。名前だけでは区別できない。

**テレメトリも「要求側の名前」を載せる。** `gateway.py:330-331`（および `:430-431`）はスパン属性を

```
"llm.profile": str(resolved_profile),   # ← 要求側（"l1_default"）。変数名に反して「解決後」ではない
"llm.model":   str(settings.model),     # ← こちらは解決後（local では "qwen2.5:3b"）
```

とする。`resolved_profile` は `generate()` の `resolved_profile = profile or "default"`（`gateway.py:315`、
同種の代入は `:416` / `:494` / `:559` にもある）であり、**remap 前の名前**である。したがって
**スパンに `llm.profile=l1_default` と出ていても JEV が動いた証拠にはならない**。`llm.model` のほうは
解決後なので、`llm.model` を見れば真実が分かる。

> **未解決の観測（結論ではない）**: git 管理外の `build/_core.txt`（ローカル実行のスパンダンプ、2026-09-25）
> には `llm.profile: "l1_default"` と **`llm.model: "jev-latest"`** の組が 100 件近く現れる。上記のとおり
> `llm.model` は解決後の値なので、**その時点では `l1_default` が `jev-latest` に解決していた**ことを示す。
> 現在の設定（`mode: "local"`）では同じ組は出ないはずで、**両者は両立しない**。原因（ダンプが設定変更前に
> 取得された／別の設定で走った／`mode` が後から `local` になった）は**特定していない**。`build/` は
> `.gitignore` 対象のローカル成果物なので、**リポジトリの主張として扱わない**。

> **過去の計画文書の前提は、現在の設定に対して偽である。** git 管理外の `.trae/documents/
> l1_event_driven_frequency_fix_plan_v2.md`（目的: `profile=l1_default` / `provider=typesafe` /
> `model=jev-latest` の実 Jev 呼び出しを 60 秒窓で 5 件超にする）は、冒頭でこう述べている:
>
> > 「`LLMSettingsResolver` の local remap は `mode == "local"` の時だけなので、**現状 `l1_default ->
> > local_decision` は発生しない**。」（同ファイル 15 行目）
>
> **これは現在の `llm.yaml`（`mode: "local"`）に対して成立しない**（上表の 3 条件がすべて真）。
> 同文書の「`l1_default` は現在も Jev を指している」（11 行目）は**宣言としては真、解決としては偽**である。
> この文書は git 管理外のローカル作業ファイルであり、コミットされた主張ではないが、**この remap を
> 見落としたまま JEV の頻度を測ると、実際には Ollama の呼び出しを数えることになる**。

**この remap は「抜け」ではなく、既存テストが固定した意図的な挙動である。**
`tests/test_local_llm_path.py:188` の `test_generation_attempts_no_external_destination_across_every_profile`
は `l1_default` を含む 5 プロファイルを回し、**外部宛が egress ゲートに一度も相談されないこと**を
表明している（＝ remap が効いていることの表明）。実測 **25 passed**。したがって:

- **resolver 側は仕様どおり**（直す対象ではない）
- 欠陥は **`llm.yaml` が `l1_default` を typesafe/jev-latest と宣言し続けているのに、resolver が
  それを意図的に上書きしている**点にある。宣言だけを読む人（設定・文書・計画）は JEV が動くと誤解する

#### この remap が導入された経緯（レジスタから復元）

`IMPROVEMENT_PROPOSAL.md` の Phase 1 完了記録（同ファイル 1045 行目）に、この remap の**目的**が残っている:

> | `llm.yaml:jev_decision` | `_LOCAL_PROFILE_MAP` に無く、`mode: local` でも**クラウド宛に解決される唯一のプロファイル** | マップに追加。これで「**local mode はクラウド宛を返さない**」が**全プロファイル**で成立し、テストで固定できる |

つまり元の不具合は **`jev_decision` が local remap をすり抜けてクラウド宛に解決される**ことで、その修正は
「**全プロファイルで不変条件を成立させる**」形で一般化された。`l1_default` は既にマップにあったため、
**この一般化の副作用として「JEV は出荷状態では一度も使われない」状態が確定した** — 不変条件は達成され、
**その代償は記録されていない**。同じ記録は `.workbuddy-ai/memory/2026-09-27.md:397` にもある。

これは「**A を直したら B が静かに壊れた**」型であり、テストは不変条件（クラウド宛を返さない）だけを見て、
**JEV が使われること**は誰も主張していないために検出されなかった。

#### 帰属

→ **JEV を L1 で使うには `mode: "cloud"` にする必要がある**。しかし `llm.yaml` 自身のコメントが「`cloud` は開発専用で、実行時は egress ゲートが止める」と書いている。

これは本プロジェクトが最も警戒している「**宣言されているが効かない**」型の欠陥である。どちらが意図か（JEV を L1 で使いたいのか、全部ローカルにしたいのか）は**オーナー判断**。判断の材料:

- **JEV を使いたい場合** → `mode` を `cloud` にするか、`l1_default` を `_LOCAL_PROFILE_MAP` から外す。
  ただし `mode: cloud` では **egress ゲートの 3 つの錠**（§5.6）を開ける必要があり、
  `test_local_llm_path.py` の上記テストも**書き換えが必要**になる。
- **ローカルのままにする場合** → `llm.yaml` の `l1_default` / `jev_decision` から
  `provider` / `model` / `base_url` を消すか「local では無効」と明記し、**宣言と解決を一致させる**。
  あわせて `build/_core.txt` 型の「JEV が動いた」ように見えるラベル（`llm.profile`）の扱いを決める。

### 5.2 構築経路で `timeout_seconds` が割れる（20 秒 / 30 秒）

実測:

| 構築経路 | `_timeout_seconds` |
|---|---|
| `LLMGateway._get_provider_for_profile()` | **20**（プロファイルどおり） |
| `factory.create_llm_provider()` | **30**（プロファイルを無視） |

`factory.py:171-176` は `TypeSafeProvider(...)` を組み立てる際に `timeout_seconds` を**渡していない**ため、既定の 30 秒になる。gateway 側は `timeout_seconds=settings.timeout_seconds` を渡している（`gateway.py:172`）。

→ 同じ `l1_default` でも入口によってタイムアウトが変わる。**どちらかに統一すべき**。

### 5.3 【修正推奨】API のエラーメッセージが捨てられている

実 API のエラーボディは **`detail` キー**に入っている:

```
401: {"detail":{"error_type":"authentication_error",
                "message":"Cannot authenticate with the server. Please check your API key and try again."}}
400: {"detail":{"error_type":"api_usage_error","message":"Unknown model: jev-does-not-exist-verify"}}
422: {"detail":[{"type":"too_short","loc":["body","questions"],"msg":"Dictionary should have at least 1 item …"}]}
```

しかし `_http_error_text()` は `payload.get("message") or payload.get("error")` を読む。`detail` は**どちらでもない**ので、メッセージは捨てられ、利用者には **`TypeSafe API error 401`** としか出ない。

→ 「鍵が違う」のか「モデル名が違う」のかがログから分からない。**`detail` を読むべき**（`detail` が dict なら `message`、list なら `msg` を連結）。

### 5.4 `max_tokens` / `temperature` / `reasoning_level` / `max_tool_rounds` は JEV に送られない

`generate()` の冒頭に `del max_tokens, temperature` があり、**送信ボディは `model` / `state` / `questions` の 3 キーだけ**（実測）。`reasoning_level` と `max_tool_rounds` は `LLMSettings` にあるが、TypeSafe 経路では**一切読まれない**。

→ `l1_default` の `max_tokens: 1024` / `temperature: 0.0` / `reasoning_level: "low"` / `max_tool_rounds: 1` は **JEV に対しては無効**。出力長・温度は API 側の既定に委ねられる。意図的（型付き判断に生成パラメータは不要）とも読めるが、**プロファイルに書いてある以上、無効であることを明示すべき**。

### 5.5 成功時のログが無い

成功してもログは 1 行も出ず、記録は監査エントリのみ。障害調査で「JEV が呼ばれたか」をログだけで追えない。

### 5.6 egress ゲートは既定で閉（3 つの錠すべてが必要）

`EgressGate.status()` は、この実行の許可状態で **`ok=False`** と 3 件の違反を返した:

```
['privacy.external_egress_allowed is True',
 'privacy.external_llm_allowed is True',
 "egress allowlist is non-empty: ['api.typesafe.ai']"]
```

つまり JEV を実際に使うには **① master switch ② purpose フラグ ③ allowlist** の 3 つすべてが必要で、`raise_if_violated()` を呼ぶ起動経路では**その状態が「設定違反」として弾かれる**。再スコープ後の目標（許可があれば外部利用可）を配線する際の論点になる。

---

## 6. この確認で測っていないこと（限界）

- **L2 / L3 は未検証**（指示どおり DeepSeek は呼んでいない）。L1 以外の層は対象外。
- **実サーバ起動経由の L1 は未検証**。`ai-server` を起動し、gRPC / dashboard から L1 を発火させる経路は通していない。ソース読解とプロバイダ直接呼び出しで代替した（`mode: local` の remap は `settings_resolver` の解決結果として実測済み）。
- **実レート制限（429/529）は発生させられず**、D6 は `urlopen` の差し替えによる模擬。
- **応答の品質は評価していない**。「妥当に見える」以上のことは言っていない（正解データがない）。
