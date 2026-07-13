# AEGIS UI Information Coverage

Last updated: 2026-07-13 16:49 JST

This document tracks the path from Runtime managers to API contracts and UI surfaces. It is intentionally separate from the visual checklist so missing operational data is visible before polishing layout.

Legend:
- `covered`: normalized API field exists and at least one UI surface consumes it.
- `api-only`: normalized API field exists, but no primary UI consumes it yet.
- `legacy-only`: old Jinja/API surface exists, but v2/v3 UI does not consume it.
- `missing`: Runtime has or should have data, but no normalized contract exists.

## Manager Coverage

| Source | Normalized Contract | Web Dashboard | Display | Android | Status |
| --- | --- | --- | --- | --- | --- |
| Runtime core | `core`, `connection`, `freshness` | Command Center HUD | Core Sphere, Display shell | parsed via gRPC overview | covered |
| TaskManager | `current_task`, `tasks` | Work, Command Center | Current Operation, Mission Phase | Tasks tab has overview model | covered |
| ApprovalManager | `approvals`, `attention` | Approvals, Command Center | P1 takeover/Attention | Approvals tab | covered |
| StatusManager + effective dashboard status | `servers`, `connection` | Systems, Command Center summary | Server Rail, Core arcs | Devices tab partial | covered |
| NotificationManager | `notifications`, `attention`, `display_queue` | Activity partial | Director dock/overlays | Home partial | covered |
| PresentationManager | `presentations`, `display_scene` | legacy Presentations page | Display Director source | not consumed | api-only |
| CapabilityCatalog | `capabilities` | Systems partial, legacy Capability page | Core server capability counts indirectly | not consumed | api-only |
| MemoryManager | `memory`, `mind`, `mind_summary` | Mind & Memory summary | Mission context only | not consumed | covered for Web |
| UserStateManager | `user_situation`, `user_state` | Mind & Memory | not shown directly | not consumed | covered for Web |
| CommitmentManager | `commitments` | Mind & Memory, Work counts | Mission context | not consumed | covered for Web |
| Cost/LLM usage | `usage` | Command/Settings partial, legacy LLM Usage | not shown | not consumed | api-only |
| AuditManager | `errors`, raw Activity routes | Activity partial | Director P0/P2 future source | not consumed | api-only |
| Settings/Policy/Auth | Settings APIs, auth routes | Settings v2 reads/mutates simple values | read-only token enforcement | not consumed | covered for Web settings |

## Normalized API Fields

| Field | Purpose | Status |
| --- | --- | --- |
| `schema_version=ui-overview.v3` | Stable contract marker with v2-compatible legacy fields retained. | covered |
| `core` | mode, health, active goal, activity, pending approvals, offline/degraded servers. | covered |
| `connection` | online counts, quality, attention count, last update. | api-only |
| `display_scene` | Display phase, takeover candidate, ambient background, privacy/offline flags. | covered |
| `presentations` | takeover/overlays/persistent/ambient presentation groups. | api-only |
| `display_queue` | server-side projection of persistent display items from EventManager. | covered |
| `tasks` | primary/active/waiting/scheduled/recent task groups. | covered |
| `activity` | server-persisted EventManager history grouped for Activity. | covered |
| `current_task` | backward-compatible primary task field. | covered |
| `approvals` | pending approvals and count. | covered |
| `servers` | effective server list with dependencies and Android capability availability. | covered |
| `capabilities` | capability count, by server, approval/high-risk counts, bounded item list. | api-only |
| `user_situation` / `user_state` | user state summary. | covered for Web |
| `mind` / `mind_summary` | autonomy and memory stats. | covered for Web |
| `memory` | episodic/semantic/procedural summary and consolidation marker. | covered for Web |
| `notifications` | recent notifications and unread count. | api-only |
| `commitments` | due/active commitments. | covered |
| `usage` | current LLM/cost summary when available. | api-only |
| `errors` | recent operational/audit errors. | api-only |
| `freshness` | global staleness and oldest source update. | covered |

## Event Envelope

`/api/ui/stream` now emits normalized events with:

`event_id`, `sequence`, `event_type`, `occurred_at`, `received_at`, `priority`, `severity`, `dedupe_key`, `persistence`, `expires_at`, `resolved_by`, `affected_servers`, `affected_capabilities`, `task_id`, `approval_id`, `safe_title`, `safe_message`, `visual_hint`, and bounded `payload`.

Display consumes `priority`, `persistence`, `dedupe_key`, and `visual_hint` through the Display Director model. Replay cursor support is implemented through SSE `id:` frames, `last_event_id` / `Last-Event-ID`, and client session storage. Persistent display state is restored from the `display_queue` overview projection.

## Raw JSON Displays

| Surface | Current Handling |
| --- | --- |
| Mind & Memory | Raw state removed from standard view; kept behind `Developer raw state` details drawer. |
| Activity | Uses grouped EventManager history by default, with live SSE events overlaid. Audit/LLM/settings/security-specific grouping remains partial. |
| Legacy Jinja pages | Several pages still render raw-ish structures and inline JS. These are legacy-only until v2 parity is complete. |

## Duplicate Displays

| Data | Duplicates | Direction |
| --- | --- | --- |
| Server health | Command summary, Systems, Display rail, legacy Servers | Keep summary in Command/Display, detail in Systems. |
| Approvals | Approvals page, Command attention, Display takeover, Android approvals | Keep same approval id and lifecycle across all. |
| Presentations | Legacy dashboard page and dedicated Display | Move dashboard management into v2 later; Display remains read-only. |
| Memory stats | Mind & Memory and legacy Memory page | Keep Mind summary as default; legacy/raw behind developer/debug. |

## Missing Or Partial Coverage

| Gap | Impact |
| --- | --- |
| Settings v2 advanced editors | Simple scalar settings can be changed; nested/array settings still need purpose-built editors. |
| Android consumption of full v3 groups | Android parses overview summary but does not mirror every field. |
| Activity grouped operation history | EventManager grouping exists; audit/LLM/settings/security-specific grouping is still broad. |
| 72-hour Display soak test | Long-run memory/event stability not proven. |
