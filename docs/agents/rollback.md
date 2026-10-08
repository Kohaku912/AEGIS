# AEGIS Agent 移行 ロールバック手順

> 計画: `instruction.md` §39.9
> 目的: 24 時間以内に **旧アーキ** (Dev Server + LLMTaskInterpreter 直接実行) へ戻せるようにする

## 緊急時の停止 (Phase 1-9 すべてを 1 行で切る)

`config/settings.json` で:

```json
{
  "agents": { "enabled": false }
}
```

> ⚠️ **環境変数 `AEGIS_AGENTS_ENABLED` はどこからも読まれていません**（2026-09-30 実測）。
> 設定は `config/settings.json` からのみ読み込まれ（`SettingsStore` →
> `AEGISSettings.model_validate_json`）、`aegis_ai/settings/` には環境変数を読む箇所が 1 つも
> ありません（`BaseSettings` / `env_prefix` / `getenv` いずれも無し）。リポジトリ全体で
> `AEGIS_AGENTS_ENABLED` を**読むコードは 1 行もありません**（2026-09-30 実測 — 出現は
> この文書の散文のみ）。したがって
> `export AEGIS_AGENTS_ENABLED=false` は**何もせず、エラーも出しません** — サービスは正常に
> 起動するので、止まったと誤認します。**緊急停止に使えるのは `config/settings.json` の
> `agents.enabled` だけです**（`runtime.py:1479` が `agent_backend = None` にします）。
> なお既定値は `False` で、現在の `config/settings.json` に `agents` 節は無いため、
> **この停止は既に効いています**（＝切るべきものが動いていない）。

> ⚠️ **`config/settings.json` が壊れていると `SettingsStore` は黙って組み込み既定へ戻ります**（2026-10-04 実測・サイクル 12）:
> 綴りを誤った JSON や読み取り不能なファイルを置くと、`SettingsStore._load` は**例外もログも残さず**既定値に差し替えるので、
> **ファイル全体が効いていない状態**になります。既定と出荷設定の差は**ちょうど 3 鍵で全部 egress 許可**
> （`privacy.egress_allowed_hosts` が `[]`、`external_egress_allowed` / `external_llm_allowed` が `False`）なので、
> この状態は **fail-closed**（何も開かない — 単一制約は危険に晒されない）ですが、egress ゲートが全ての外部宛先を拒否し、
> クラウド LLM プロファイルは降格します。**この停止手順を打つときは、JSON が妥当かどうかを別途確かめてください** —
> 壊れたファイルは「何も変えない」ではなく「既定へ戻す」ので、意図した変更が**効いていない**のにサービスは正常に起動します
> （`AEGIS_AGENTS_ENABLED` を読んでいない件と同型の誤認）。サイクル 12 以降、`aegis_ai.settings.store` の WARNING が
> この降格を名乗ります。

これで `aegis_ai/agents/` の**バックエンドは**起動しなくなり、
`LLMTaskInterpreter.interpret()` 経由の旧挙動に戻る。
（`requires_feature: "agents"` による capability の**非表示化は起きません** — その機構は
配線済みなのに、フラグ集合を渡す呼び出し元がリポジトリに 1 つも無いためです。登録簿を参照。）

## Dev Server への完全切り戻し (Phase 9 完了後のため参考)

> **注意**: Phase 9 (commit `cfea844` / `69b90b2`) で Dev Server コードは
> 完全に削除済み。Dev Server を使った旧アーキに戻すには **git 操作が必要**。
> ⚠️ **この手順は今のリポジトリでは実行できません**（2026-10-05 実測）。手順が名指す `7c0ffe5` は
> **有効なオブジェクトではありません**（`git cat-file -t 7c0ffe5` → `fatal: Not a valid object name`）。
> 同様に上の `cfea844` / `69b90b2` も存在しません（3 つとも `fatal`）。**理由（実測）**: リカバリ
> コミット `d483813`（2026-09-29、「recover: re-commit the working tree after the local object store
> was lost」）が記録するとおり**ローカルのオブジェクトストアが失われた**ためで、Phase 8/9 のコミットは
> 消え、それ以前（`1327cf2` = 2026-08-30 など）は残っています。**「書いた時点で誤っていた」とは判定
> できません**（履歴の穴 ⇒ 不可知）ので、`git checkout 7c0ffe5 -- …` は**書き換えず**、測定結果だけを
> 記録します。
>
> **届く範囲（実測）**: 削除直前の**到達可能な**最後のコミットは `1327cf2`（2026-08-30、`d483813` の親）。
> 下の手順 2 が並べる 12 経路のうち **10 がそこに在り**、**2 つ**
> （`ai-server/src/aegis_ai/tools/bridges/git.py` / `github.py`）は**到達可能な全履歴のどこにも
> ありません**（`git log --all -- <path>` が空）。`docker-compose.yml.archive`（手順 3 の退避物）は
> **在ります**（7842 B）。`git tag -l` は**0 件**なので、下のタグ復元の手順も**空振りします**。
> 復元するか廃止するかはオーナー判断（`DELEGATION.md` §4 項目 55）。
>
> **追記（2026-10-08、サイクル 101）**: 手順 2 が名指す `ai-server/src/aegis_ai/tools/bridges/git.py` /
> `github.py` は、その**親パッケージごと削除された**（`DELEGATION.md` §4 項目 53 — production で
> 登録簿が空で、到達不能だったため）。したがって手順 4 の最初の 3 つ
> （`ai-server.workspace.{repo_status,diff,test_results}`）は、**戻す先の bridge 実装がもう存在しない**。
> 3 つの ID も `ai-server/src` から消えた（能力 ID の全数調査は 44 → 41、未解決 8 → 5 に再実測）。

### Dev Server を復活させる手順

1. Dev Server が居た commit を確認:
   ```bash
   git log --oneline --all | grep -i "dev-server"
   # 7c0ffe5 (Phase 8) 以前に戻すのが安全
   ```
2. Dev Server が削除される直前の commit に checkout:
   ```bash
   git checkout 7c0ffe5 -- dev-server/ \
     ai-server/src/aegis_ai/integrations/dev/ \
     ai-server/src/aegis_ai/self_development/ \
     ai-server/src/aegis_ai/dev_server/ \
     ai-server/src/dev_server_client.py \
     ai-server/src/generated/aegis/dev_server_pb2.py \
     ai-server/src/generated/aegis/dev_server_pb2_grpc.py \
     ai-server/src/aegis_ai/tools/bridges/git.py \
     ai-server/src/aegis_ai/tools/bridges/github.py \
     protos/aegis/dev_server.proto \
     infra/docker/dev-server.Dockerfile \
     ai-server/capabilities/builtin/dev-server/
   ```
3. `docker-compose.yml` を dev-server サービス込みの版に戻す:
   ```bash
   git checkout 7c0ffe5 -- docker-compose.yml
   ```
4. capability_id を旧形式に戻す:
   - `ai-server.workspace.repo_status` → `dev-server.repo.status`
   - `ai-server.workspace.diff` → `dev-server.diff.get_diff`
   - `ai-server.workspace.test_results` → `dev-server.test.get_results`
   - `ai-server.test.run_pytest` → `dev-server.test.run_tests`
5. `.env.example` に `DEV_SERVER_HOST` / `DEV_SERVER_PORT` を戻す:
   ```bash
   git checkout 7c0ffe5 -- .env.example
   ```
6. AEGIS 設定で `agents.enabled=false` を維持しつつ、`dev-server` を有効化
   （環境変数 `AEGIS_AGENTS_ENABLED` は読まれないので使わない — 冒頭の注記を参照）:
   ```bash
   export AEGIS_DISABLED_SERVERS=""
   docker compose up -d dev-server
   systemctl restart aegis.service
   ```

## ロールバック時の確認チェックリスト

| # | 項目 | 確認手段 |
|---|------|---------|
| 1 | `aegis-openhands-agent.service` が停止している | `systemctl status aegis-openhands-agent.service` |
| 2 | Dev Server container が起動している | `docker ps | grep dev-server` |
| 3 | `aegis.service` が健康 | `journalctl -u aegis -n 50 | grep -i error` |
| 4 | dev-server.* capability が manifest に復活 | `curl localhost:8090/api/capabilities | jq '.[] | select(.id | startswith("dev-server"))'` |
| 5 | 既存の ai-server スイートが緑（**件数は書かない** — 数は腐る。実測は登録簿） | `cd ai-server && pytest -q` |
| 6 | Capability Catalog に旧 dev-server 11 個が見える | Dashboard `/capabilities` 画面 |

## 旧 systemd unit の退避場所

旧 `infra/systemd/aegis.service` (`Type=oneshot` で `docker compose up` する版) は
**Phase 8 完了時点** で host 実行版に書き換え済み。旧版が必要な場合は
git tag で復元する:

```bash
git tag -l | grep -i "phase-7\|pre-host"
# 該当 tag 時点の aegis.service を退避場所にコピー
git show <tag>:infra/systemd/aegis.service > infra/systemd/aegis.service.archive
```

旧 `docker-compose.yml` 全体は **Phase 8 完了時点 (commit `7c0ffe5`)** の版を
`docker-compose.yml.archive` として 1 リリース残してある (commit `7c0ffe5` で
自動生成)。

## ロールバック判断の閾値

| 状況 | 対応 | 推定時間 |
|------|------|---------|
| Agent 関連の特定 task が fail | `agents.enabled=false` で task 単位 skip | 5 分 |
| `aegis-openhands-agent.service` 連続 crash | systemd unit 停止 + `agents.enabled=false` | 15 分 |
| Phase 6-8 で導入した ToolBridge 層が壊れる（**この層は 2026-10-08 に削除済み** — 上の追記を参照） | git revert 該当 commit | 30 分 |
| Phase 9 で破壊的変更があった | Dev Server 復活 + `git checkout 7c0ffe5` | 1-2 時間 |

> ロールバック判断は **まず `agents.enabled=false` で** Agent 機能のみを止め、
> それで足りない場合に限り git 操作を行う。
