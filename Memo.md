AEGISのRuntime singleton / Manager構造を完成させた後の安定化フェーズを実装してください。

最優先:
1. `runtime.py` の `_build_runtime()` を修正してください。
   - `return AegisRuntime(...)` の後に `runtime._dashboard_approval_channel = ...` や `status_manager.start_background_checks()` が来ている場合、それらは到達不能です。
   - `runtime = AegisRuntime(...)` に代入し、追加初期化・background start後に `return runtime` してください。

3. TaskManagerを全実行経路に接続してください。
   - User / Web Chat / CLI / Autonomous / Scheduler / Event由来の処理はTaskManager.create_task()から始める。
   - ToolBrokerがApprovalを要求したらTaskをwaiting_approvalへ遷移させる。
   - Approval approve後にTaskManager.resume_after_approval()で再開できるようにする。
   - cancel / retry / fail / completeをDashboardから操作できるようにする。

4. AuditManagerを本当に全件読み込みなしにしてください。
   - `AuditManager.list_recent()` / `get_detail()` / `search()` / `summarize()` / `rotate()` で `AuditLog.read_all()` を使わない。
   - SQLite AuditStore、またはcursor付きtail readerを実装する。
   - Dashboard一覧はsummaryのみ、詳細は1件取得にする。
   - 1万件以上auditがあってもAPIが固まらないテストを追加する。

5. MemoryManagerを自律系の唯一入口にしてください。
   - AutonomousLoop / SpontaneousObservationSystem / CuriosityDrivenExplorationSystem が個別Memory backendを直接使わないようにする。
   - memory write/search/context取得は `runtime.memory_manager` 経由に統一する。
   - 個別Memory backendはMemoryManager内部に閉じ込める。
   - SleepManagerはMemoryManager経由で整理・統合・教訓抽出を行う。

6. StatusManagerを完全稼働させてください。
   - Runtime起動時に必ず `status_manager.start_background_checks()` が呼ばれるようにする。
   - Dashboard routeやprompt生成で直接 `_check_port()` / `_http_json()` を呼ばない。
   - すべて `runtime.status_manager.get_snapshot()` を使う。
   - offline serverがあってもDashboardが固まらないテストを追加する。

7. DashboardをManager中心に整理してください。
   - Task一覧
   - Approval待ち
   - Sleep状態
   - Status snapshot
   - Audit summary
   - Notification一覧
   をすべてRuntime上のManagerから取得するようにしてください。

8. E2Eテストを追加してください。
   - ユーザー依頼 → Task作成 → ToolBroker → Approval待ち → Dashboard通知 → approve → Task再開 → complete → Audit記録
   の流れを1本のテストで確認してください。