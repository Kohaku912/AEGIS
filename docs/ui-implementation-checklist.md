# AEGIS UI Instruction Completion Ledger

This ledger maps the replacement `UI_Instruction.md` to implementation and test evidence. The previous Core Sphere / seven-area checklist is obsolete.

Legend: `[x]` implemented, `[~]` implemented with remaining real-device or visual evidence, `[ ]` not complete, `[!]` production blocker.

## 1. Design Language

- [x] Root `DESIGN.md` defines information dimensions, semantic colors, status modifiers, depth, motion, shape, scene states, adaptation, accessibility, performance, and prohibited patterns.
- [x] `design-tokens/tokens.json` is the shared semantic source for Web and Android generated tokens.
- [x] Status is represented by shape, motion, labels, and topology rather than hue alone.
- [x] Dashboard uses dense operational typography and progressive disclosure instead of hero/card marketing composition.

## 2. Cognitive Field

- [x] The decorative central sphere, great-circle server globe, and concentric-ring composition are removed from active pages.
- [x] Cognitive Field is split into `EnvironmentLayer`, `MemoryField`, `SystemTopology`, `MissionFlow`, `EventParticles`, `SceneCamera`, and `SceneDirector`.
- [x] Environment, Memory, System Topology, Mission, Execution, Attention, and Takeover layers are represented.
- [x] Observation, planning, execution, approval, failure, and recovery use distinct spatial/motion grammar.
- [x] Scene, camera, renderer, composer, geometry, and materials are mount-only and disposed on unmount.
- [x] Frame movement is delta-time based and reduced-motion has a static information-equivalent presentation.
- [x] High, medium, and low rendering quality paths are selected from motion preference and device capacity.
- [~] Final GPU profiling on Ubuntu dedicated display at 60 Hz remains to be recorded.

## 3. Master Dashboard Shell

- [x] Nine domains exist: Command, Work, Intelligence, Capabilities, Infrastructure, Communications, Governance, Observability, Configuration.
- [x] Hierarchical left navigation preserves route state and browser back/forward navigation.
- [x] Global Search searches Overview immediately and Manager-backed resources asynchronously.
- [x] Global Inspector displays identity, status, relations, permissions, actions, and developer-only raw detail.
- [x] `Ctrl/Cmd+K` Command Palette and persistent Live Activity drawer exist.
- [x] Top bar exposes Create Task, Attention, Approvals, Chat, and current security session.
- [x] Unauthorized, forbidden, fresh-auth-required, loading, error, stale, empty, and permission states have dedicated UI primitives.

## 4. Command And Work

- [x] Command Center prioritizes current operation, attention, AI state, situation, commitments, budget, and recent operations.
- [x] Attention Center has a searchable operational resource view and Inspector drill-down.
- [x] Tasks retain the specialized list/detail view with steps, plan, verification, approval, cost, audit group, and final output.
- [x] Plans, Commitments, Schedule & Hooks, and Delegation have routes, field contracts, search, filters, saved-view affordance, and Inspector.
- [x] Schedule and Delegation use their owning HookEngine/DelegationPolicyStore resources and require preview, fresh auth, confirmation, Manager persistence, verification, and audit.

## 5. Intelligence

- [x] Autonomy, Memory, Consolidation & Sleep, User Model, User Situation, Context Builder, and Models & Prompts routes exist.
- [x] Memory has a Manager-backed plural API and normal UI does not expose raw JSON.
- [x] Context fields include system/history/memory/events/user/tool schema budgets and retrieval reasons.
- [x] Models & Prompts exposes routing, fallback, limits, usage, dead prompts, evaluation, and rollback field contracts.
- [x] Prompt contents are Developer Mode-only; candidate validation, required-variable checks, diff review, persistent revisions, fresh-auth save, rollback, and Audit are implemented.

## 6. Capabilities

- [x] Catalog, Generated, Executions, and Policy Simulation routes exist.
- [x] Catalog data is loaded from `CapabilityCatalog`, including manifest and effective fields in Inspector detail.
- [x] Capability screens expose schema, risk, approval, permissions, completion, verification, latency, and execution health contracts.
- [x] Controlled and dangerous Inspector actions are preview-only and never execute directly.
- [x] Policy Simulation accepts capability, arguments, target, environment, and actor context and returns decision, reason, effective risk, matching gate, approval, fresh-auth, and audit requirements without execution.

## 7. Infrastructure And Communications

- [x] Servers retain the specialized topology/detail surface.
- [x] Devices, Network, Deployment, and Storage routes expose their required operational field contracts.
- [x] Conversations, Notifications, and Presentation Surfaces routes exist and consume Event-backed entities.
- [x] Healthy systems are compact; degraded/offline/permission states receive visual priority.
- [x] Deployment and Notification surfaces expose persisted operational state without presenting unimplemented or unsafe mutation buttons.

## 8. Governance And Observability

- [x] Approvals retain per-item decision UI; high-risk bulk approval does not exist.
- [x] Policy, Security, Privacy, and Audit routes exist with safety field contracts.
- [x] Activity retains persisted operations plus live SSE events.
- [x] LLM Usage, Errors, Performance, and Reports routes exist with request/cost/context/retry and operational field contracts.
- [x] Complete approval lifecycle and audit data are available through normalized resource APIs.

## 9. Configuration And Safety

- [x] Seventeen configuration routes exist.
- [x] Settings input is staged locally and never saves on keystroke/change.
- [x] Save shows a before/after review; Cancel discards the draft.
- [x] Reset requires a second explicit confirmation.
- [x] Settings show effective source, schema-default ownership, validation type, and session change history.
- [x] Existing CSRF, passkey session, and fresh-auth enforcement remain in the API path.
- [x] Dangerous actions are represented as preview/review commands, not immediate execution buttons.

## 10. Backend Contracts

- [x] Existing `ui-overview.v3` and normalized SSE contracts remain compatible.
- [x] `GET /api/ui/entities` provides stable resource type, search, filter, sort, paging, freshness timestamp, and normalized summaries.
- [x] `GET /api/ui/entities/<resource>/<id>` provides Inspector detail.
- [x] `GET /api/ui/search` performs cross-Manager search without reading storage files in the client.
- [x] `GET /api/memories` and `GET /api/approvals` provide full list surfaces.
- [x] Runtime Managers and CapabilityCatalog remain state owners; the UI API is an adapter only.
- [x] HookEngine, DelegationPolicyStore, AutonomousLoop, SleepManager, UserModelStore, SituationModel, PromptRegistry, AndroidManager, SessionManager, and PresentationManager have distinct normalized resources.
- [x] Resource pages provide server-side search, status filter, sorting, pagination, stable IDs, Saved Views, relation links, and Inspector drill-down.
- [x] Density preferences and pinned resources persist across browser reloads.

## 11. Device Surfaces

- [x] Dedicated Display uses Cognitive Field and remains read-only, GET-only, token/local constrained, no Dashboard controls.
- [x] Android Compose has Home, Chat, Approvals, Tasks, Devices, Permissions, and Settings with shared status semantics.
- [x] PC Overlay remains restricted to approval, notification, and emergency presentation.
- [~] Android portrait/landscape/tablet/font-200% automated coverage exists; latest physical-device screenshot evidence is pending this revision.
- [~] Ubuntu production deployment, token-authenticated snapshot/SSE, physical kiosk capture, and display-power polling are verified; final 60 Hz GPU/frame pacing evidence remains pending.

## 12. Verification

- [x] Resource API contract tests cover normalization, search, paging, approval lifecycle, and memory listing.
- [x] Web unit tests cover primary pages and Display director states.
- [x] Playwright covers Display scene states, no-scroll, no-focus, reduced motion, SSE latency, and canvas identity.
- [x] Nine-domain shell, global search, command palette, relation-aware Inspector, Pins, Density, staged Settings, Policy Simulation, Prompt revision, and Hook preview have Playwright coverage.
- [x] Every major dashboard domain is exercised at 1366x768, 1920x1080, and 2560x1440 with overflow checks and attached screenshots.
- [x] Ubuntu production deployment serves the replacement bundle and restarts the local dedicated Display kiosk successfully.
- [ ] Android physical-device E2E for this replacement UI revision (the latest Windows ADB enumeration returned no connected device).

## Completion Gate

- [x] `scripts/audit-ui-completeness.py` has no open non-device implementation items; physical acceptance remains explicitly separated below.
- [x] Web unit tests, production build, all 19 Playwright tests, all 489 AI Server tests, and Android unit/build tasks pass.
- [x] Production Cloudflare Passkey entry and local dedicated Display serve the replacement UI; unauthenticated Dashboard redirects to Passkey login and remote Display access remains denied.
- [x] No old Core Sphere component is imported by active Web UI code.
- [x] Physical Display evidence is attached at `data/reports/e2e/latest/screenshots/ubuntu-display-production.png`.
- [ ] Android physical-device evidence is attached to the E2E report.
