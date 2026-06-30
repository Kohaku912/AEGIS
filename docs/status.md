# AEGIS Implementation Status

Updated: 2026-06-30

## Current Personal AI Foundation

AEGIS now includes the first integrated version of the personal-AI foundation. The implementation is owned by `AegisRuntime` and reuses the existing execution and safety path:

- Tool execution still goes through `ToolBroker`.
- Hard safety gates still come from `PolicyEngine`.
- Runtime state and observations flow through `EventManager`.
- Decisions, transitions, failures, and manager updates are recorded through `AuditManager`.
- Lessons from repeated failures are written through `MemoryManager`.
- Dashboard APIs are registered through the existing manager route blueprint.

## Implemented

- `UserModelStore` has structured fields for preferences, work patterns, permission scopes, common apps, notification conditions, writing style, and long-term goals.
- `ContextBuilder` injects relevant UserModel, Situation, DelegationPolicy, and due Commitment context instead of dumping the full model.
- `HookEngine` supports interval, schedule, and event hooks. It only runs read-only capabilities, evaluates deterministic conditions without calling the LLM on every tick, and emits `self_call` only on match.
- `HookEngine` now supports dashboard stop, persisted stop reasons, exponential backoff, max backoff, consecutive failure counts, and dedupe suppression by result dot-path.
- `CommitmentManager` persists commitments, transitions, due dates, and follow-up hooks.
- Commitment due hooks use the dedicated read-only `ai-server.commitment.wakeup` capability.
- `SituationModel` persists current situation, interruptibility, confidence, and evidence from device/server events.
- `SituationModel` accepts structured observations such as `device_type`, `activity`, `foreground_app`, `screen_state`, `presence`, and `focus_mode`.
- `DelegationPolicyStore` adds user-specific approval/deny requirements without weakening PolicyEngine hard denials.
- `SocialProxy` supports draft-first webhook/email flow. Sending is exposed only through approval-required capability.
- SocialProxy sends now require a ToolBroker-approved execution marker internally, so direct in-process calls without approval are blocked.
- `InterruptionController` can suppress or batch non-critical notifications based on situation, UserModel, and emergency-stop state.
- `RepairManager` classifies failures, records repair history, and writes repeated failure lessons through MemoryManager.
- `RepairManager` includes safe retry execution, rollback strategy registration, and rollback requests through ToolBroker so risky rollback remains approval-gated.
- Dashboard has `/dashboard/personal-ai` and APIs for UserModel, Hooks, Commitments, DelegationPolicy, Situation, Interruption, Repair, and Social drafts.
- Dashboard Personal AI now shows pending approvals, notification/interruption state, hook backoff/error status, and hook stop controls.
- New `ai-server.*` capability manifests expose personal-AI read/write operations to the LLM with approval gates for policy-changing or external-send actions.
- Capability manifests include required `operation_category` metadata and the registry rejects manifests missing it.

## Not Yet Complete

- SocialProxy v1 sends webhook/email only. Discord, LINE, and AGORA are represented at the interface level but need channel-specific adapters for unified outbound sending.
- RepairManager retry remains conservative and limited to safe/idempotent cases.
- SituationModel uses deterministic event heuristics. A future version can add learned situation inference while preserving deterministic notification gates.
- Hook condition language is intentionally small: dot-path plus `eq/ne/gt/lt/contains/exists/changed`.
- Dashboard Personal AI page is a status/control surface with stop controls; richer creation/editing UX can be added on top of the existing APIs.

## Safety Defaults

- External send, social post, deletion, Git push, payment/billing API, system changes, and physical device control remain approval-required.
- PolicyEngine hard denies cannot be overridden by DelegationPolicy.
- HookEngine refuses non-read-only capabilities.
- Dashboard direct edits are treated as explicit user operation; LLM/autonomous policy-changing capabilities require approval.
