# AEGIS v1 Completion Checklist

This checklist defines "single-user production v1" readiness for AEGIS. Keep it
in sync with `scripts/audit-v1-completion.py` and the latest E2E reports.

Legend:
- `[x]` done and verified
- `[~]` implemented but not fully accepted
- `[ ]` incomplete
- `[!]` production blocker

## 0. Completed Foundation

- [x] Runtime singleton, Manager pattern, PolicyEngine, and CapabilityCatalog are in place.
- [x] ToolBroker, TaskExecutionEngine, ApprovalManager, AuditManager, and EventManager are integrated.
- [x] LLMRouter, LLMGateway, ContextBuilder, and LLM Usage foundations are implemented.
- [x] Capability risk overrides are persistent.
- [x] Completion verification foundations exist.
- [x] Passkey-only Dashboard auth is the production default.
- [x] React/Vite Web UI v2 and read-only `/display` exist.
- [x] Android real device basic observe path has been verified.
- [x] Ubuntu production AI Server deploy path exists and Cloudflare `/auth/login` is reachable.
- [x] UI Overview v3, PresentationEvent, and SurfaceRole contracts exist.

## 1. P0 Production Blockers

- [x] Production readiness output is the canonical release gate.
- [x] Production blocker mock/stub count is zero, or explicitly deferred out of v1 scope.
- [x] Room Server mock provider is never treated as production-online.
- [x] Voice, LINE, Discord, Email, and external send stubs are disabled/blocker-marked in production.
- [x] Production Docker bind scope avoids unnecessary `0.0.0.0` exposure.
- [ ] Cloudflare Tunnel recovery and systemd autostart are verified.
- [ ] Ubuntu reboot restores AI Server, Cloudflare Tunnel, and Display kiosk.
- [x] `.env`, data volume, auth DB, capability overrides, audit, memory, and reports persist across restart/rebuild.
- [x] Readiness Gate uses real E2E evidence, not file existence alone.

## 2. P0 Real E2E

- [x] Manager E2E performs state changes, not only GET checks.
- [x] Task create, step execute, verification, and terminal status are verified.
- [x] Capability risk override reload affects PolicyEngine and ToolBroker effective policy.
- [x] Approval fanout, approve/reject, and Audit reflection are verified.
- [x] Memory save/search/ContextBuilder/LLM Usage flow is verified.
- [x] Presentation create, Display visibility, user_action, Event, and Audit are verified.
- [x] LLM Usage displays audit-backed input/output/context/cache/cost data.
- [x] Browser real task verifies DOM/selector/text/http status.
- [x] Dev Server is normally stopped and write/deploy paths require fresh passkey and approval.
- [x] E2E results are aggregated in `data/reports/e2e/latest/summary.json`.

## 3. P0 Devices

- [~] Windows PC Server service install/start/health/screenshot/active_window/overlay is verified.
- [ ] PC real click/type/hotkey is verified only after approval on a safe test surface.
- [~] PC Server firewall script restricts access to Private/Tailscale and an explicit remote address; applying the rule still requires an elevated Windows session.
- [~] Android connects to AI gRPC over stable LAN or Tailscale.
- [~] `/api/android/status` reports online, reverse_stream, and model `21121210G`.
- [~] Android permissions/accessibility/current_app/ui_tree/notifications are verified.
- [ ] Android Wi-Fi OFF/ON, screen off, AI restart, and app restart reconnect are verified.
- [ ] Android reconnect_count and heartbeat_failure_count are measured.
- [x] Orange Pi Room Server candidate is recorded with SSH/Wi-Fi/MAC/IP inventory.
- [x] Room Server remains UNCONFIGURED/DISABLED until a real Orange Pi provider is installed.

## 4. P1 UI Completion

- [~] `UI_Instruction.md` is mapped to the UI checklist and audit output; Android approval/reconnect real-device acceptance remains open.
- [x] UI completeness audit is included in production readiness.
- [x] Web pages handle Loading, Empty, Error, Stale, Unauthorized, and Fresh-auth-required states.
- [x] Command Center prioritizes Current Operation, Attention, AI State, and LLM budget.
- [x] Work traces task detail, step graph, approval, verification, cost, and audit group.
- [x] Approvals use list-detail layout with preview, side effects, risk rationale, history, and fresh auth state.
- [x] Systems centers dependency graph and recovery state for AI/PC/Android/Browser/Room/Dev.
- [x] Mind & Memory hides raw JSON outside Developer drawer.
- [x] Activity is a persisted Event/Audit/LLM/Settings/Security/Error operation history.
- [x] Settings uses dedicated editors for Autonomy, Permissions, Servers, Privacy, Notifications, Models, Budgets, Memory, Display, Developer, and Backup.
- [x] `/display` is a read-only Display Compositor.
- [x] CoreSphere visual states are regression tested.
- [x] Android Compose UI is practical for Home, Approvals, Tasks, Devices, Permissions, and Settings.
- [x] Android portrait, landscape, tablet, and 200% font scale are tested.
- [x] PC overlay is limited to approval, notification, and emergency display.

## 5. P1 Verification And Closed Loop

- [x] Side-effecting capabilities declare completion conditions.
- [x] PC, Android, and Browser operation capabilities declare verification.
- [x] High-risk or approval-required capabilities declare postconditions.
- [x] ToolBroker/TaskExecutionEngine uses VerificationService status for step terminal state.
- [x] FAILED flows into retry/repair; REQUIRES_OBSERVATION flows into observation/user confirmation.
- [x] PC verification uses screenshot/active_window/app_state before/after signals.
- [x] Android verification uses ui_tree/current_app/permission before/after signals.
- [x] Browser verification uses DOM selector/text/http status, not URL only.
- [x] Verification results and suggested recovery are visible in Audit/Event/Task detail.
- [x] Capability coverage audit is included in Readiness Gate.

## 6. P1 LLM, Memory, Autonomy

- [x] All LLM calls record input/output/context/cache/cost audit detail.
- [x] ContextBuilder always passes system/history/memory/events/capability/tool_schema/user_state breakdown.
- [x] LLM Usage shows context breakdown, retry loop, prompt usage, and heavy memory cases.
- [x] Retry loop detection uses dedup-before raw audit entries.
- [x] All prompts are classified as used/unused/dead_runtime/test_only/duplicated/hardcoded_candidate.
- [x] Memory interface is organized as episodic/semantic/procedural.
- [x] ContextBuilder exposes memory_budget_tokens, memory_top_k, and memory_reason.
- [x] AutonomousLoop suppresses autonomous LLM use when usage is high.
- [x] AutonomousLoop uses user_commitment/system_health/learning/curiosity-level decision axes.
- [x] Autonomous execution never treats mock success as real success.

## 7. P1 Security

- [x] Production mode rejects unauthenticated Dashboard/API/SSE/WebSocket access.
- [x] Fresh passkey auth is required for risk changes, approvals, secrets/LLM config, and dangerous actions.
- [x] CSRF is enforced for POST/PUT/DELETE APIs.
- [x] Display token is GET-only and local/token limited.
- [x] Dashboard access token is bootstrap/recovery only.
- [x] Secret scanning confirms no secrets in image, Git, or static assets.
- [x] Backup and restore have been executed once.
- [x] gRPC TLS status is documented as integrated or intentionally not used for v1.
- [x] WAN exposure is prohibited except Cloudflare/Tailscale-controlled entrypoints.

## 8. P2 Packaging And Operations

- [x] PC Server portable zip can be built.
- [ ] PC Server service install/uninstall is verified on Windows.
- [x] PC Server logs/config/firewall paths are documented.
- [x] NSIS installer plan is documented.
- [ ] Ubuntu install/start/healthcheck/systemd are verified on real host.
- [x] AI dedicated Display opens only Presentation/Display surfaces.
- [ ] Display backlight turns off when idle and wakes on relevant events.
- [~] Device IP/MAC/role inventory exists locally on the working machine; copy to each device during real-host maintenance.
- [x] `.aegis-local/` is gitignored and checked for accidental commits.
- [x] Logs/reports/audit retention and rotation are defined.

## 9. P2 Documentation

- [x] Roadmap reflects current implementation.
- [x] Implementation status is generated or audit-backed.
- [x] Risk register reflects TLS, Docker, notifications, external integrations, and Room status.
- [x] Backlog is production-readiness centered.
- [x] Testing docs include real-device markers and skip conditions.
- [x] Ubuntu runbook covers Cloudflare, Tailscale, backup/restore, and systemd recovery.
- [x] PC Server production docs cover service, installer, and real-action E2E.
- [x] Android docs cover LAN-outside/Tailscale/reconnect/permission runbooks.
- [x] Room docs cover Orange Pi migration and mock prohibition.
- [x] UI docs, summary, checklist, and audit report are consistent.

## 10. v1 Completion Gate

- [x] `cd ai-server && pytest` passes.
- [x] `cd web-ui && npm test -- --run` passes.
- [x] `cd web-ui && npm run build` passes.
- [x] `cd web-ui && npx playwright test` passes for major UI states.
- [x] `cd android-server && ./gradlew.bat :app:assembleDebug` passes.
- [ ] Android observe/approval/reconnect real E2E passes.
- [ ] PC service observe/approval/action real E2E passes.
- [x] Browser/Dev real checks pass.
- [x] Docker restart/rebuild persistence passes.
- [x] Cloudflare login and Dashboard auth redirect pass.
- [ ] Dedicated Display kiosk recovers after reboot.
- [ ] `scripts/e2e/run-readiness-report.ps1` reports `overall_status: pass`.
- [x] Production blocker mock/stub count is zero, or all remaining items are v1-scope excluded.
- [x] 72-hour-equivalent Display/server soak shows no memory/SSE/UI degradation.
- [ ] Daily operation works across PC, Android, Browser, Display, Approval, and LLM Usage.

## Deferred After v1

- [ ] LINE Bot real integration.
- [ ] Discord Bot real integration.
- [ ] Email SMTP real sending.
- [ ] Voice I/O real STT/TTS/wake word.
- [ ] Smart Glasses UI.
- [ ] Multi-user support.
- [ ] Payment or money-spending actions.
- [ ] Full gRPC TLS rollout if Tailscale/Cloudflare-only v1 operation remains accepted.
