# AEGIS UI Information Coverage

Last updated: 2026-07-29

This document tracks the path from Runtime managers to API contracts and UI surfaces. It is intentionally separate from the visual checklist so missing operational data is visible before polishing layout.

Legend:
- `covered`: normalized API field exists and at least one UI surface consumes it.
- `api-only`: normalized API field exists, but no primary UI consumes it yet.
- `legacy-only`: old Jinja/API surface exists, but v2/v4 UI does not consume it.
- `missing`: Runtime has or should have data, but no normalized contract exists.

## Manager Coverage

| Source | Normalized Contract | Web Dashboard | Display | Android | Status |
| --- | --- | --- | --- | --- | --- |
| Runtime core | `core`, `connection`, `freshness` | Command Center HUD | Core Sphere, Display shell | parsed via gRPC overview | covered |
| TaskManager | `current_task` (= `tasks.primary`), `tasks`, `goals`, `open_loops` | Open Loops, Command Center, Judgment Goals | Current Operation, Mission Phase | Tasks tab has overview model | covered |
| ApprovalManager | `approvals`, `attention`, `open_loops` | Approvals, Open Loops, Command | P1 takeover/Attention | Approvals tab | covered |
| StatusManager | `servers`, `connection` | Systems, Command Center | Server Rail, Core arcs | Devices tab partial | covered |
| NotificationManager | `notifications`, `attention`, `display_queue` | Communications / Notifications | Director dock/overlays | Home partial | covered |
| PresentationManager | `presentations`, `display_scene` | Presentation Surfaces | Display Director source | not consumed | covered for Web |
| CapabilityCatalog | `capabilities`, `generated_capabilities` | Catalog + Generated pages | Core capability counts indirectly | not consumed | covered for Web |
| MemoryManager | `memory`, `mind` (= `mind_summary`) | Memory / Judgment | Mission context only | not consumed | covered for Web |
| UserStateManager | `situation` (= `user_state` / `user_situation`) | Situation, Command | not shown directly | not consumed | covered for Web |
| CommitmentManager | `commitments`, `open_loops` | Open Loops, Command | Mission context | not consumed | covered for Web |
| AgentState | `agent_state`, `decision_context` | Decision Context / Judgment | not consumed | not consumed | covered for Web |
| InitiativeEngine | `initiative` | Initiative & Non-action, Command | not consumed | not consumed | covered for Web |
| ContinuationManager | `continuations`, `open_loops` | Continuations, Open Loops | not consumed | not consumed | covered for Web |
| RepairManager | `repairs`, `errors` | Repairs & Learning / Repair Feed | not consumed | not consumed | covered for Web |
| SocialManager | `social`, `open_loops` | Social & AGORA | not consumed | not consumed | covered for Web |
| BehavioralEvaluation | `behavioral_reports` | Behavioral Reports | not consumed | not consumed | covered for Web |
| Cost/LLM usage | `usage` | LLM Usage, Command partial | not shown | not consumed | covered for Web |
| AuditManager / autonomous logs | `activity.operations` (+ `causal_chain`), `executions`, `autonomous_logs` | Operations, Activity, Executions | Director P0/P2 future source | not consumed | covered for Web |
| Settings/Policy/Auth | Settings APIs, auth routes | Configuration | read-only token enforcement | not consumed | covered for Web settings |

## Normalized API Fields

| Field | Purpose | Status |
| --- | --- | --- |
| `schema_version=ui-overview.v4` | Judgment/progress contract; aliases keep v3 field names. | covered |
| `core` | mode, health, active goal, activity, pending approvals, offline/degraded servers. | covered |
| `connection` | online counts, quality, attention count, last update. | covered |
| `display_scene` / `presentations` / `display_queue` | Display phase, presentation groups, persistent queue. | covered |
| `tasks` / `current_task` | Task groups; `current_task` aliases `tasks.primary`. | covered |
| `activity.operations[].causal_chain` | Trigger → Decision → … → Learning chain. | covered |
| `open_loops` | Unified tasks/commitments/approvals/social/incidents. | covered |
| `agent_state` / `decision_context` | Obligations, situation, identity used for judgments. | covered |
| `goals` | GoalGraph + unmet verification conditions. | covered |
| `initiative` | Funnel, non-action reasons, recent decisions. | covered |
| `continuations` | Open/due follow-ups from ContinuationManager. | covered |
| `repairs` / `errors` | RepairManager history (errors prefer repair source). | covered |
| `social` | Social inbox + AGORA pending/decided. | covered |
| `behavioral_reports` | Restraint / goal achievement / continuity metrics. | covered |
| `generated_capabilities` | Generated-origin capabilities only. | covered |
| `executions` | Operation + autonomous-cycle execution history. | covered |
| `approvals` / `servers` / `capabilities` | Pending approvals, server health, catalog slice. | covered |
| `situation` / `user_state` / `user_situation` | Same UserStateManager projection (deduped). | covered |
| `mind` / `mind_summary` | Same autonomy + memory stats projection (deduped). | covered |
| `memory` / `notifications` / `commitments` / `usage` / `freshness` | Supporting operational summaries. | covered |

## Navigation (judgment-first)

Command → Open Loops → Judgment → Communications → Systems → Governance → Developer → Configuration.

Raw IDs/JSON stay behind Developer Mode. Domain pages that previously reused wrong entity resources (Executions→capabilities, Context→memories, Errors/Reports→audit, Conversations→sessions-only) now read the matching overview sections.

## Event Envelope

`/api/ui/stream` emits normalized events with:

`event_id`, `sequence`, `event_type`, `occurred_at`, `received_at`, `priority`, `severity`, `dedupe_key`, `persistence`, `expires_at`, `resolved_by`, `affected_servers`, `affected_capabilities`, `task_id`, `approval_id`, `safe_title`, `safe_message`, `visual_hint`, and bounded `payload`.

## Duplicate Displays (resolved direction)

| Data | Direction |
| --- | --- |
| `user_state` / `user_situation` / `situation` | One Situation page; same backend object. |
| `mind` / `mind_summary` | One Memory/Judgment mind projection. |
| `current_task` / `tasks.primary` | Alias only; no second source. |
| Tasks / Commitments / Approvals / Social / Incidents | Prefer **Open Loops** as the unified unfinished-work surface. |

## Remaining Gaps

| Gap | Impact |
| --- | --- |
| Settings advanced editors | Nested/array settings still need purpose-built editors. |
| Android full v4 groups | Android parses overview summary but does not mirror every judgment field. |
| Readiness report files | `data/reports/*.json` audit scripts exist; Behavioral Reports is runtime evaluation, not file readiness packs. |
| 72-hour Display soak test | Long-run memory/event stability not proven. |
