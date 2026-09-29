# Protocol Buffers — Overview

> ⚠️ **Goal change (2026-09-27)**: the only constraint is now **"the user's information must never
> leave the local environment."** Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

> **Status**: Verified against `protos/aegis/` — **four** files, no more
> **Related**: [`architecture.md`](architecture.md), [`proto-build.md`](proto-build.md)

---

## File Map

`protos/aegis/` contains exactly these four files. It is the single source of truth for gRPC.

| File | Purpose | Service |
|------|---------|---------|
| `common.proto` | **All shared types** — enums and base messages | (no service — imported by the others) |
| `ai_server.proto` | AI Server — central brain API | `AIServer` |
| `android_server.proto` | Android device API | `AndroidServer` |
| `room_server.proto` | Room/IoT control API | `RoomServer` |

### There is no `pc_server.proto`, `browser_server.proto`, or `dev_server.proto`

This is deliberate, not an omission:

| Server | Real transport | Why no proto |
|---|---|---|
| **PC Server** | newline-delimited **TCP JSON** on `:50052` | The Rust server owns its own command grammar (`mouse_click {x},{y},{button}`). The AI Server reaches it through `pc_server_client.py`, which speaks that grammar directly. |
| **Browser Server** | **HTTP** (Flask) on `:50053` | Exposes REST endpoints; `browser_server_client.py` calls them. |
| **Dev Server** | *deleted* | `dev-server/` was removed; self-development now runs through `agents/backends/openhands/` + `infra/systemd/aegis-openhands-agent.service`. |

`AGENTS.md`'s "all server communication uses gRPC" describes the **original** design. The three
servers above never adopted it, and the PC/Browser clients are the contract instead. A
`grep` for `pc_server.proto` or `browser_server.proto` anywhere in the tree returns nothing.

---

## SafetyLevel

`common.proto` declares four tiers plus an unspecified value. **They are descriptive only** —
nothing in the execution path reads a tier to decide anything.

| Value | Name | Meaning |
|-------|------|---------|
| 0 | `SAFETY_LEVEL_UNSPECIFIED` | Invalid — treated as `LEVEL_3_RESTRICTED` |
| 1 | `LEVEL_0_READ` | Observe only, no side effects (screenshot, sensor read, DOM snapshot) |
| 2 | `LEVEL_1_SAFE_ACT` | Non-destructive, reversible (open app, navigate, move mouse) |
| 3 | `LEVEL_2_APPROVAL` | **Historical label.** Elevated impact (delete file, send DM). It no longer implies anyone is asked — the forced gate was removed 2026-09-28. |
| 4 | `LEVEL_3_RESTRICTED` | May be prohibited entirely (purchase, `rm -rf`, production deploy) |

**The gate lives elsewhere.** Execution decisions come from `PolicyEngine`, whose output type is
`PolicyDecisionType` — and that enum now carries only two live values:

| Value | Name |
|-------|------|
| 0 | `POLICY_DECISION_UNSPECIFIED` |
| 1 | `POLICY_DECISION_ALLOW` |
| ~~2~~ | ~~`POLICY_DECISION_ASK_APPROVAL`~~ — **reserved**, removed with the forced gate |
| 3 | `POLICY_DECISION_DENY` |

> **The proto is narrower than the in-process engine.** `aegis_schema`'s Python `PolicyDecision`
> (`ai-server/src/policy_engine.py`) has four values — `ALLOW`, `ALLOW_WITH_AUDIT`, `DENY`,
> `UNAVAILABLE` — and `ALLOW_WITH_AUDIT` is the common case. `PolicyDecisionType` cannot express
> it, because a wire decision was only ever needed to tell a *client* whether to proceed. Keep the
> two in mind separately: they are not the same vocabulary.

**Unregistered capabilities never reach `PolicyEngine`.** `ToolBroker` resolves the id against the
capability catalog first and returns `InvokeStatus.NOT_FOUND` when it fails
(`tool_broker.py:549`). So "unknown → `LEVEL_3_RESTRICTED` → DENY" is not the path that runs;
unknown → *not registered* is.

---

## Entity Relationships

```
ServerInfo ──► Capability (many-to-many via capability_ids)
Capability ──► SafetyLevel
Tool ──► Capability
Event ──► ServerType, EventSeverity, EventPriority
ToolInvocationRequest ──► Capability
ToolInvocationResult ──► Status
PolicyDecision ──► PolicyDecisionType, SafetyLevel
AuditRecord ──► AuditAction, SafetyLevel
```

Enums in `common.proto`: `SafetyLevel`, `ServerType`, `ServerStatus`, `EventSeverity`,
`EventPriority`, `AuditAction`, `PolicyDecisionType`.

`AuditAction` had three approval members — `AUDIT_ACTION_APPROVAL_REQUESTED` / `_GRANTED` /
`_REJECTED` — at 3–5. They were deleted with the forced gate and the numbers are `reserved`, so an
old log entry with action 3 fails to decode rather than silently reading as something else. Live
values: `TOOL_INVOKED`, `TOOL_DENIED`, `EVENT_RECEIVED`, `TRIGGER_FIRED`, `POLICY_DECISION`.

`ApprovalStatus` (`PENDING`/`APPROVED`/`REJECTED`/`EXPIRED`) and `ApprovalType`
(`ONE_TIME`/`SESSION`) were deleted on 2026-09-28. They described a pending-request lifecycle and
a grant validity window — the mechanism that made execution wait for a human. AEGIS may still
*ask* the user a question, but nothing is queued or granted.

### Flow Diagram

```
Server Registration:
  Capability Server ──RegisterServer──► AI Server (Tool Registry)

Capability Registration:
  Capability Server ──RegisterCapability──► AI Server (Tool Registry)

Event Flow:
  Capability Server ──PushEvent──► AI Server (Event Bus) ──► Trigger Engine

Tool Invocation:
  AI Server (Planner) ──InvokeTool──► AI Server (Tool Broker)
    ──► resolve id in the catalog ──► (miss) InvokeStatus.NOT_FOUND
    ──► Policy Engine ──► Capability Server (execute)

Asking the user (AEGIS-initiated, non-blocking):
  AEGIS decides to ask ──► Confirmation (aegis_ai.confirmation, Android overlay)
  User answers ──► the answer informs the next step; nothing was waiting on it
  (The forced approval flow — RequestApproval / ResolveApproval /
   ListPendingApprovals — was removed on 2026-09-28.)

Audit:
  Every decision/action ──WriteAuditLog──► Audit Log (immutable)
```

---

## Service Summary

### AIServer (`ai_server.proto`) — 18 RPCs

| RPC | Purpose |
|-----|---------|
| `RegisterServer` | Register a capability server |
| `UnregisterServer` | Remove a server |
| `RegisterCapability` | Register a capability |
| `UnregisterCapability` | Remove a capability |
| `ListCapabilities` | Query capabilities (by type, safety, tags, search) |
| `GetCapability` | Get a single capability by ID |
| `PushEvent` | Push an event to the Event Bus |
| `StreamEvents` | Server-side streaming of events |
| `SubscribeEvents` | Subscribe to a filtered event stream |
| `Connect` | Bidirectional Android client stream |
| `InvokeTool` | Invoke a capability (Policy Engine enforced) |
| `SendChat` | Chat turn |
| `GetMobileDashboardState` | Mobile dashboard payload |
| `GetUiOverview` | Web dashboard overview payload |
| `StreamUiEvents` | Server-side streaming of UI events |
| `WriteAuditLog` | Write an audit record |
| `QueryAuditLog` | Query audit records |
| `HealthCheck` | Server health check |

> The five approval RPCs (`RequestApproval` / `ResolveApproval` / `ListPendingApprovals` and
> their messages) are gone. `ai_server.proto:136` records the removal in a comment.

### AndroidServer (`android_server.proto`) — 18 RPCs

| RPC | Level | Purpose |
|-----|-------|---------|
| `Connect` | — | Bidirectional client stream (the app dials **out** to the AI Server) |
| `GetScreenshot` | 0 | Capture screen |
| `GetCurrentApp` | 0 | Get foreground app |
| `GetUiTree` | 0 | Get UI hierarchy |
| `GetNotifications` | 0 | Get notification list |
| `GetPermissionStatus` | 0 | Runtime permission status |
| `GetDeviceStatus` | 0 | Device status |
| `GetAccessibilityStatus` | 0 | Accessibility service status |
| `GetLocation` | 0 | Device location |
| `Tap` | 1 | Tap at coordinates |
| `Swipe` | 1 | Swipe gesture |
| `TypeText` | 1 | Type text |
| `PressBack` | 1 | Press back |
| `PressHome` | 1 | Press home |
| `OpenApp` | 1 | Launch app |
| `ShowOverlay` | 1 | Display overlay |
| `EmergencyStop` | 1 | Stop in-flight device action |
| `HealthCheck` | 0 | Health check |

### RoomServer (`room_server.proto`) — 9 RPCs

| RPC | Level | Purpose |
|-----|-------|---------|
| `GetEnvironment` | 0 | Read sensors |
| `GetDeviceStatus` | 0 | Device status |
| `GetCameraSnapshot` | 0 | Camera snapshot |
| `SendIrCommand` | 2 | Send IR signal |
| `SetLight` | 2 | Control lights |
| `SetAirConditioner` | 2 | Control AC |
| `MoveRobotArm` | 3 | Move robot arm |
| `EmergencyStopRobotArm` | 1 | Emergency stop (safe override) |
| `HealthCheck` | 0 | Health check |

Levels are the **manifest risk tier**, shown for orientation. A level-2 row does not mean anything
is asked before it runs.

---

## What is NOT in the Protos

By design, the following are **absent**:

| Omission | Reason |
|----------|--------|
| Direct push/merge to main API | Self-dev goes through a PR (architecture §8.1) |
| Production deploy API | Not safe for autonomous execution |
| Secret/credential access API | Structural prohibition |
| Docker daemon control API | Sandbox boundary |
| System package install API | Potential security risk |
| SNS/DM send APIs (direct) | Simply absent — there is no RPC for them. The three `EXPLICIT_DENY_PATTERNS` hard stops are purchases/payments, egress-gate bypass, and policy self-modification. |
| Purchase API | Absent here, **and** `.*\.purchase.*` / `.*\.click_payment.*` are hard-denied by `EXPLICIT_DENY_PATTERNS` |
| ~~PERMANENT approval type~~ | Removed with the gate — nothing is approved at all now, so there is no grant to make permanent |
| `PC Server` / `Browser Server` services | Not gRPC servers — see the File Map above |
| `Dev Server` service | The server was deleted |
