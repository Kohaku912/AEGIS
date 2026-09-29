# AEGIS Agent 移行 ロールバック手順

> 計画: `instruction.md` §39.9
> 目的: 24 時間以内に **旧アーキ** (Dev Server + LLMTaskInterpreter 直接実行) へ戻せるようにする

## 緊急時の停止 (Phase 1-9 すべてを 1 行で切る)

`config/settings.json` または環境変数で:

```json
{
  "agents": { "enabled": false }
}
```

または:

```bash
export AEGIS_AGENTS_ENABLED=false
systemctl restart aegis.service
```

これで `aegis_ai/agents/` 配下の全コードは feature flag で bypass され、
`LLMTaskInterpreter.interpret()` 経由の旧挙動に戻る。

## Dev Server への完全切り戻し (Phase 9 完了後のため参考)

> **注意**: Phase 9 (commit `cfea844` / `69b90b2`) で Dev Server コードは
> 完全に削除済み。Dev Server を使った旧アーキに戻すには **git 操作が必要**。

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
6. AEGIS 設定で `AEGIS_AGENTS_ENABLED=false` を維持しつつ、`dev-server` を有効化:
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
| 5 | 既存 157 tests が緑 | `cd ai-server && pytest -q` |
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
| Phase 6-8 で導入した ToolBridge 層が壊れる | git revert 該当 commit | 30 分 |
| Phase 9 で破壊的変更があった | Dev Server 復活 + `git checkout 7c0ffe5` | 1-2 時間 |

> ロールバック判断は **まず `agents.enabled=false` で** Agent 機能のみを止め、
> それで足りない場合に限り git 操作を行う。
