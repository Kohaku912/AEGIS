# AEGIS Daily Use

> **Status**: Beta
> **Last Updated**: 2026-06-14

## 毎日の流れ

### 1. 起動

```bash
cd AEGIS
docker compose up -d
```

### 2. 確認

```
http://0.0.0.0:8090          # Dashboard
http://0.0.0.0:8080/approvals # Approval UI
```

### 3. 使いたい操作

| 操作 | 方法 |
|------|------|
| Web 検索 | Browser Server 経由（read-only） |
| データ確認 | Dashboard → Memory |
| 設定変更 | Dashboard → Settings |
| 承認操作 | Approval UI で確認・承認 |

### 4. 終了

```bash
docker compose down
```

## 自律動作

AEGIS は Desire System に基づいて自律的に動作します:

- **8つの欲求** (social_connectivity, personal_fulfillment, curiosity, safety, recognition, autonomy, creativity, purpose) が 0-10 スケールで管理
- 欲求が低下すると AutonomousLoop (`src/aegis_ai/autonomous/autonomous_loop.py`) が自動的にタスクを生成・実行
- Planner (`src/aegis_ai/autonomous/planner.py`) がタスクを計画し、CuriosityDrivenExploration (`src/aegis_ai/autonomous/curiosity_exploration.py`) が探索タスクを生成
- 学習パイプライン: ActionTrace → Lesson → Workflow → Skill で自己改善
- SleepConsolidation (`src/aegis_ai/memory/sleep_consolidation.py`) がメモリの定期整理を実行
- Dashboard で欲求状態と自律ループの状態を監視可能

## Safety Reminder

- 承認なしで危険操作は実行されません
- Dashboard は read-only です
- 設定変更は AuditLog に記録されます
- 自律タスクも PolicyEngine による安全性チェックを受けます
