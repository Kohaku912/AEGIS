# AEGIS UI Implementation Checklist

This checklist tracks completion against `UI_Instruction.md`. Update it whenever UI scope is implemented, tested, or deliberately deferred.

Legend:
- `[x]` implemented and verified
- `[~]` partially implemented, usable but incomplete
- `[ ]` not implemented
- `[!]` blocker or production risk

## Current Snapshot

- Last updated: 2026-07-13 21:24 JST
- Web UI version: React/Vite v2 under `web-ui/`
- Display surface: React `/display` and `/display/presentations`
- Android UI: Compose v2 package exists under `android-server/app/src/main/java/com/aegis/android/ui/`
- Android live status: ADB visible, updated debug APK installed, gRPC capability `android-server.device.get_status` reports `21121210G / reverse_stream`; AEGIS AccessibilityService is enabled; observe E2E passes while the device is unlocked.
- Production deploy: Ubuntu `/opt/aegis` rebuilt and `aegis-ai-server-1` is healthy; Cloudflare `/auth/login` returns 200 and `/dashboard` redirects to login; `/display/overview` reports `ui-overview.v3` and `presentations.status=ok`.

## Phase 0: UI Information Audit

- [x] `docs/ui-information-coverage.md` lists Runtime Managers, APIs, overview fields, displayed fields, missing fields, duplicate displays, raw JSON displays, and legacy dependencies.
  - Evidence: `docs/ui-information-coverage.md`
- [~] UI consumes normalized overview through `/api/ui/overview` and `/display/overview`.
  - Evidence: `ai-server/src/aegis_ai/web/ui_overview.py`, `web-ui/src/api/client.ts`
- [x] UI consumes normalized stream through `/api/ui/stream` with replay cursor recovery.
  - Evidence: `web-ui/src/api/useOverviewStream.ts`, `ai-server/src/aegis_ai/web/routes/ui.py`, `web-ui/tests/display.spec.ts`
- [x] Core state uses the same effective server projection as the Systems view.
  - Evidence: `ai-server/tests/test_ui_overview.py::test_core_uses_effective_server_status`; production `/display/overview` reports `core.offline_servers=[]` while Android is `ONLINE / reverse_stream`.
- [x] Manager-to-API-to-UI coverage test exists.
  - Evidence: `web-ui/src/pages/DashboardPages.test.tsx::keeps manager-to-api-to-ui coverage visible across primary pages`

## Phase 1: Common Design System

- [x] Shared token source exists.
  - Evidence: `design-tokens/tokens.json`
- [~] Web CSS variables use AEGIS Operational Futurism tokens.
  - Evidence: `web-ui/src/styles/tokens.css`, `web-ui/src/styles/main.css`
- [x] Android Compose theme exists.
  - Evidence: `android-server/app/src/main/java/com/aegis/android/ui/designsystem/AegisTheme.kt`
- [x] Token generation from `design-tokens/tokens.json` to Web CSS and Android Compose is automated.
  - Evidence: `scripts/generate-design-tokens.py`, `web-ui/src/styles/tokens.css`, `android-server/app/src/main/java/com/aegis/android/ui/designsystem/GeneratedTokens.kt`
- [x] Contrast test data and automated contrast tests exist.
  - Evidence: `design-tokens/contrast-report.json`, `ai-server/tests/test_design_tokens.py`
- [~] Shared status/freshness/approval components exist for Web.
  - Evidence: `web-ui/src/components/StatusBadge.tsx`, `Freshness.tsx`, `ApprovalCard.tsx`
- [~] Android components mirror status/freshness/approval semantics for primary mobile screens.
  - Evidence: `android-server/app/src/main/java/com/aegis/android/ui/designsystem/AegisComponents.kt`, `./gradlew.bat :app:assembleDebug` with Android Studio JBR 21.

## Phase 2: UI Overview v3 Contract

- [x] v3 overview has freshness envelopes for core sections while retaining v2-compatible fields.
  - Evidence: `ai-server/tests/test_ui_overview.py`
- [x] `ui-overview.v3` schema is implemented.
  - Evidence: `build_ui_overview()` returns `schema_version=ui-overview.v3`.
- [x] Overview includes `connection`, `display_scene`, `presentations`, `tasks`, `capabilities`, `user_situation`, `memory`, `errors`.
- [x] UI events expose server/capability/status/severity/message.
  - Evidence: `normalize_ui_event()` in `ui_overview.py`
- [x] Event envelope includes event_id, sequence, priority, dedupe_key, persistence, expires_at, resolved_by, affected_servers, affected_capabilities, visual_hint.
  - Evidence: `ai-server/tests/test_ui_overview.py::test_normalize_ui_event_exposes_visual_fields`
- [x] Multi-device `PresentationEvent` contract exists and is attached to normalized UI events.
  - Evidence: `ai-server/src/aegis_ai/presentation/surface_contract.py`, `ai-server/tests/test_ui_overview.py::test_normalize_ui_event_exposes_visual_fields`
- [x] Surface roles are defined for dedicated display, web dashboard, mobile app, PC overlay, Android notification, room display, developer console, and future smart glasses.
  - Evidence: `ai-server/src/aegis_ai/presentation/surface_contract.py`, `web-ui/src/pages/Settings.tsx`
- [x] Overview exposes `presentation_events` and `surface_roles` so surfaces can restore the same presentation state after reconnect.
  - Evidence: `ai-server/src/aegis_ai/web/ui_overview.py`, `ai-server/tests/test_ui_overview.py::test_ui_overview_sections_have_freshness_envelope`
- [x] SSE replay cursor and reconnect gap recovery are implemented.
  - Evidence: SSE emits `id:` frames, accepts `last_event_id` / `Last-Event-ID`, replays persisted events via `EventManager.list_recent()`, and the client persists last ids in session storage.

## Phase 3: Web Dashboard

### Global Shell

- [x] New React/Vite app exists and legacy shell is not used for v2 primary navigation.
  - Evidence: `web-ui/`, `ai-server/src/aegis_ai/web/routes/ui_v2.py`
- [x] Seven primary areas exist: Command Center, Work, Approvals, Systems, Mind & Memory, Activity, Settings.
  - Evidence: `web-ui/src/App.tsx`
- [x] Chat is available as a right drawer.
  - Evidence: `web-ui/src/components/ChatDrawer.tsx`
- [~] Existing URLs route to v2 without breaking legacy compatibility.
  - Evidence: `ui_v2.py`

### Command Center

- [x] Current Operation and Attention are top priority.
  - Evidence: `web-ui/src/pages/CommandCenter.tsx`
- [x] Server Health is summarized instead of a permanent large card.
- [~] AI State and memory summary are shown without raw JSON.
- [x] Top HUD includes core state, connection quality, pending approvals, critical/open issue count, and freshness.
  - Evidence: `web-ui/src/pages/CommandCenter.tsx`, `web-ui/src/styles/main.css`
- [~] Current Operation shows current/next action and user-waiting state; related conversation link remains partial.
- [x] Middle section includes User Situation, Device Context through Systems, Pending Commitments, and LLM Budget.
- [~] Recent events use SSE events plus server-persisted EventManager activity history.

### Work

- [~] Active task and steps are visible.
  - Evidence: `web-ui/src/pages/Work.tsx`
- [x] Work tabs exist: Active, Waiting, Scheduled, Research, Self-development, Commitments, Completed, Failed.
- [~] Desktop Work page uses list-detail layout.
- [x] Task detail includes objective, phase, current capability, execution server, current action, next action, blocked reason, and step history.
  - Evidence: `web-ui/src/pages/Work.tsx`
- [x] Task detail includes original instruction, plan/dependency summary, approvals, memories used, model/cost, completion/verification, and final output when reported.
  - Evidence: `web-ui/src/pages/Work.tsx`

### Approvals

- [~] Pending approvals can be listed and resolved.
  - Evidence: `web-ui/src/pages/Approvals.tsx`, `ApprovalCard.tsx`
- [x] Approvals page has left filters: Pending, Expiring, High risk, Resolved, Expired, Failed after approval.
- [x] Approval detail has center preview and right context pane.
  - Evidence: `web-ui/src/components/ApprovalCard.tsx`, `web-ui/src/pages/Approvals.tsx`
- [x] Approval detail includes related task, previous action, risk rationale, similar past action, audit, and post-approval effect when reported.
  - Evidence: `web-ui/src/pages/Approvals.tsx`
- [x] High-risk bulk approval is impossible in UI.
  - Evidence: only per-approval `ApprovalCard` actions are rendered; no bulk approve action exists.

### Systems

- [~] Server list exists.
  - Evidence: `web-ui/src/pages/Systems.tsx`
- [~] Topology view exists.
- [x] Dependency graph exists.
  - Evidence: `web-ui/src/pages/Systems.tsx`
- [~] Capability availability is visible for Android.
- [~] Android detail shows device name, connection mode, permissions, available capabilities, active approvals, last observation.
- [x] Server cards show heartbeat age, latency, active task, capability health, version, dependency status, permission state, last healthy time, and recovery method.
  - Evidence: `web-ui/src/pages/Systems.tsx`

### Mind & Memory

- [x] Raw JSON is removed from standard Mind & Memory view and isolated in a Developer drawer.
  - Evidence: `web-ui/src/pages/MindMemory.tsx`
- [~] Standard view shows current goal, dominant desire, confidence, memory stores, user situation, commitments, consolidation.
- [x] Raw JSON is available only in a Developer drawer.

### Activity

- [~] Browser-session SSE events are shown.
  - Evidence: `web-ui/src/pages/ActivityPage.tsx`
- [x] Activity has an Operational Replay timeline based on shared `PresentationEvent` state.
  - Evidence: `web-ui/src/pages/ActivityPage.tsx`, `web-ui/src/pages/DashboardPages.test.tsx`
- [~] Activity uses server-persisted EventManager history after reload.
  - Evidence: `ai-server/src/aegis_ai/web/ui_overview.py::_activity`, `web-ui/src/pages/ActivityPage.tsx`; audit/LLM/settings/security grouping remains partial.
- [x] Raw Audit is behind debug expansion; grouped operations are default.
  - Evidence: `web-ui/src/pages/ActivityPage.tsx`

### Settings

- [~] Settings page reads and mutates real SettingsStore values through `/api/settings` with CSRF/fresh-auth protection.
  - Evidence: `web-ui/src/pages/Settings.tsx`
- [x] Settings sections exist: Autonomy, Permissions, Servers, Privacy, Notifications, Models, Budgets, Memory, Display, Developer, Backup.
- [x] Settings changes call real APIs with CSRF/fresh passkey where required.
  - Evidence: `web-ui/src/api/client.ts::updateSetting`, `web-ui/src/pages/Settings.tsx`

## Phase 4: Dedicated Display

- [x] Display is read-only and separate from Dashboard.
  - Evidence: `/display`, `/display/presentations`, `ui_v2.py`
- [x] Display token/local-only GET access is enforced; POST is unavailable.
  - Evidence: `ai-server/tests/test_passkey_auth.py`
- [x] Server Health is a compact Server Rail.
  - Evidence: `web-ui/src/pages/Display.tsx`
- [x] Core Sphere uses mount-only Three.js lifecycle and does not recreate canvas on event updates.
  - Evidence: `web-ui/src/components/CoreSphere.tsx`, `web-ui/tests/display.spec.ts`
- [~] Visual events exist for pulse, containment, fracture, disconnect, recovery.
- [~] Display Director model centralizes priority, queue, dedupe, persistent state, resolution, privacy, offline.
  - Evidence: `web-ui/src/displayModel.ts::buildDisplayDirectorState`, `web-ui/src/pages/Display.tsx`
- [~] P0/P1/P2/P3 notifications have distinct layouts and preemption rules.
  - Evidence: P0/P1 takeover, P2 overlay stack, P3 ambient/recent event rows.
- [x] Persistent notifications are restored from server-side Display Queue projection and do not depend only on client session memory.
  - Evidence: `ai-server/src/aegis_ai/web/ui_overview.py::_display_queue`, `ai-server/tests/test_ui_overview.py::test_display_queue_resolves_persistent_server_items`, `web-ui/src/displayModel.test.ts::restores persistent display queue items from the server-side overview`
- [x] Same notification is deduped by server-side `dedupe_key` projection and client-side director state.
  - Evidence: `web-ui/src/displayModel.test.ts`
- [x] Offline removes LIVE indication and shows stale snapshot.
  - Evidence: `web-ui/tests/display.spec.ts`
- [x] Privacy mode hides personal data.
  - Evidence: `web-ui/tests/display.spec.ts`
- [x] Fixed one-screen layout is verified at 1366x768, 1920x1080, 2560x1440 with no scrollbars.
  - Evidence: `web-ui/tests/display.spec.ts`
- [x] Display has no buttons, inputs, links, or tab stops.
  - Evidence: `web-ui/tests/display.spec.ts`
- [x] 72-hour memory/event accumulation soak-test script exists.
  - Evidence: `scripts/e2e/run-display-soak.ps1`

## Phase 5: Android App

- [~] Compose v2 UI package exists with Home, Chat, Approvals, Tasks, Devices, Permissions, Settings.
  - Evidence: `android-server/app/src/main/java/com/aegis/android/ui/`
- [~] Android consumes the same normalized UI overview contract for primary mobile surfaces.
  - Evidence: `UiOverviewSnapshot` parses v3 `schema_version`, `connection`, `display_scene`, `tasks`, `servers`, `approvals`, `attention`, `notifications`, `memory`; real-device dump shows Home `Mission Phase / Attention / Connection / Memory`, Tasks `Task Buckets`, Devices `Heartbeat`.
- [x] Android approval card shows approval_id, action, target, capability, risk, reason, preview, task, timestamps, approve/reject/detail.
  - Evidence: `android-server/app/src/main/java/com/aegis/android/ui/designsystem/AegisComponents.kt`, `android-server/app/src/main/java/com/aegis/android/ui/feature/approvals/ApprovalsScreen.kt`
- [ ] Phone, landscape, 8-inch/tablet, and 200% text size are tested.
  - Remaining: Compose UI/preview tests still need to be added.
- [x] Android connection and observe capabilities are verified on real device through ADB and production Core gRPC.
  - Evidence: ADB model `21121210G`; `uv run pytest tests/test_android_local.py -k "adb_device_and_app_installed or observe_capabilities or ui_tree" -q` passed; `android-server.device.get_status`, `permissions.get_status`, `accessibility.get_status`, `screen.get_ui_tree`, and `notification.get_notifications` returned status 0.
- [ ] Android permission-missing, approval approve/reject, Wi-Fi disconnect/reconnect are verified on real device.
  - Partial evidence: Android debug build passes with JBR 21; real-device UI interaction still pending.

## Phase 6: PC Overlay / Legacy Approval

- [x] PC overlay uses the new token/status visual language.
  - Evidence: `pc-server/src/overlay_approval.rs`
- [x] PC overlay is limited to approval, notification, emergency display.
  - Evidence: `docs/pc-overlay-v2.md`
- [x] Legacy approval UI compatibility is documented and scheduled for removal.
  - Evidence: `docs/pc-overlay-v2.md`

## Phase 7: Tests And Acceptance

- [x] Display reduced-motion and canvas identity Playwright tests exist.
  - Evidence: `web-ui/tests/display.spec.ts`
- [x] Priority preemption test.
  - Evidence: `web-ui/src/displayModel.test.ts::builds display director takeover from approval and dedupes events`
- [~] Overlay lifecycle test.
  - Evidence: Display overlay stack is covered at model/page level; server-persisted overlay lifecycle remains incomplete.
- [x] Notification dedupe test.
  - Evidence: `web-ui/src/displayModel.test.ts::keeps persistent items until resolved while expiring ephemeral duplicates`
- [x] SSE reconnect test.
- [x] Event replay test.
- [x] Offline/Stale test.
  - Evidence: `web-ui/tests/display.spec.ts::display shows offline snapshot and privacy redaction without interactive controls`
- [x] Privacy test.
  - Evidence: `web-ui/src/displayModel.test.ts::surfaces offline, stale, and privacy display modes from display scene`
- [x] Viewport no-scroll test.
- [x] No-focusable-element test.
- [ ] Visual regression snapshots for Display states.
- [~] Automated UI completion audit exists and records remaining implementation gaps.
  - Evidence: `scripts/audit-ui-completeness.py`, `data/reports/ui_completeness.md`
- [x] Schema coverage test.
- [x] Manager-to-API-to-UI coverage test.
- [x] Android real-device E2E test result recorded.
