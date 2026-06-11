# Protocol Buffers — Overview

> **Status**: Complete (2026-06-11)  
> **Related**: [`architecture.md`](architecture.md), [`proto-build.md`](proto-build.md)

---

## File Map

| File | Purpose | Services |
|------|---------|----------|
| `common.proto` | **All shared types** — enums, base messages | (no service — imported by all) |
| `ai_server.proto` | AI Server — central brain API | `AIServer` (registry, events, tools, approval, audit, health) |
| `pc_server.proto` | PC control API | `PCServer` (observe, input, app, files, health) |
| `android_server.proto` | Android device API | `AndroidServer` (observe, input, app, health) |
| `browser_server.proto` | Web automation API | `BrowserServer` (navigation, observe, interaction, health) |
| `room_server.proto` | Room/IoT control API | `RoomServer` (observe, device, robot, health) |
| `dev_server.proto` | Sandboxed self-dev API | `DevServer` (observe, branch, test, commit, PR, rollback, health) |

---

## SafetyLevel Usage

Every `Capability` declares a `safety_level`. The Policy Engine enforces:

| Level | Name | Policy | Examples |
|-------|------|--------|----------|
| 1 | `LEVEL_0_READ` | ALLOW | Screenshot, sensor read, DOM snapshot |
| 2 | `LEVEL_1_SAFE_ACT` | ALLOW (audit) | Open app, navigate browser, move mouse |
| 3 | `LEVEL_2_APPROVAL` | ASK_APPROVAL | Delete file, send DM, IR control, create PR |
| 4 | `LEVEL_3_RESTRICTED` | DENY or ASK_APPROVAL | Purchase, rm -rf, production deploy |

**Unregistered capabilities**: Treated as `LEVEL_3_RESTRICTED` → DENY.

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
ApprovalRequest ──► SafetyLevel, ApprovalStatus, ApprovalType
AuditRecord ──► AuditAction, SafetyLevel
```

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
    ──► Policy Engine ──► Capability Server (execute)

Approval Flow:
  Policy Engine ──► ApprovalRequest (PENDING)
  User ──ResolveApproval──► ApprovalRequest (APPROVED/REJECTED)
  ToolBroker ──► Check approval ──► Execute

Audit:
  Every decision/action ──WriteAuditLog──► Audit Log (immutable)
```

---

## Service Summary

### AIServer (ai_server.proto)

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
| `SubscribeEvents` | Subscribe to filtered event stream |
| `InvokeTool` | Invoke a capability (Policy Engine enforced) |
| `RequestApproval` | Create an approval request |
| `ResolveApproval` | Approve or reject a pending request |
| `ListPendingApprovals` | List pending approvals |
| `WriteAuditLog` | Write an audit record |
| `QueryAuditLog` | Query audit records |
| `HealthCheck` | Server health check |

### PCServer (pc_server.proto)

| RPC | Level | Purpose |
|-----|-------|---------|
| `GetScreenshot` | 0 | Capture screen |
| `GetActiveWindow` | 0 | Get active window info |
| `ListWindows` | 0 | List all windows |
| `GetClipboard` | 0 | Read clipboard |
| `MoveMouse` | 1 | Move mouse cursor |
| `ClickMouse` | 1 | Click at coordinates |
| `TypeText` | 1 | Type text via keyboard |
| `PressHotkey` | 1 | Press key combination |
| `LaunchApp` | 1 | Launch application |
| `ShowOverlay` | 1 | Display overlay |
| `ReadFile` | 1 | Read file contents |
| `WriteFile` | 1 | Write file |
| `DeleteFile` | 2 | Delete file (approval required) |
| `ListDirectory` | 0 | List directory contents |
| `HealthCheck` | 0 | Health check |

### AndroidServer (android_server.proto)

| RPC | Level | Purpose |
|-----|-------|---------|
| `GetScreenshot` | 0 | Capture screen |
| `GetCurrentApp` | 0 | Get foreground app |
| `GetUiTree` | 0 | Get UI hierarchy |
| `GetNotifications` | 0 | Get notification list |
| `Tap` | 1 | Tap at coordinates |
| `Swipe` | 1 | Swipe gesture |
| `TypeText` | 1 | Type text |
| `PressBack` | 1 | Press back button |
| `PressHome` | 1 | Press home button |
| `OpenApp` | 1 | Launch app |
| `ShowOverlay` | 1 | Display overlay |
| `HealthCheck` | 0 | Health check |

### BrowserServer (browser_server.proto)

| RPC | Level | Purpose |
|-----|-------|---------|
| `OpenPage` | 1 | Navigate to URL |
| `GetDomSnapshot` | 0 | Get DOM HTML |
| `GetScreenshot` | 0 | Capture page screenshot |
| `ExtractPageText` | 0 | Extract text content |
| `GetNetworkLog` | 0 | Get network requests |
| `Click` | 1 | Click element |
| `FillForm` | 2 | Fill form fields (approval) |
| `DownloadFile` | 1 | Download file |
| `HealthCheck` | 0 | Health check |

### RoomServer (room_server.proto)

| RPC | Level | Purpose |
|-----|-------|---------|
| `GetEnvironment` | 0 | Read sensors |
| `GetDeviceStatus` | 0 | Device status |
| `GetCameraSnapshot` | 0 | Camera snapshot |
| `SendIrCommand` | 2 | Send IR signal (approval) |
| `SetLight` | 2 | Control lights (approval) |
| `SetAirConditioner` | 2 | Control AC (approval) |
| `MoveRobotArm` | 3 | Move robot arm (restricted) |
| `EmergencyStopRobotArm` | 1 | Emergency stop (safe override) |
| `HealthCheck` | 0 | Health check |

### DevServer (dev_server.proto)

| RPC | Level | Purpose |
|-----|-------|---------|
| `GetRepoStatus` | 0 | Check git status |
| `GetTestResults` | 0 | Get test results |
| `GetDiff` | 0 | Get diff |
| `CreateBranch` | 1 | Create feature branch |
| `ApplyPatch` | 1 | Apply code patch |
| `RunTests` | 1 | Run test suite |
| `RunLint` | 1 | Run linter |
| `CreateCommit` | 1 | Create commit |
| `CreatePullRequest` | 2 | Create PR (approval) |
| `RevertChanges` | 2 | Revert changes (approval) |
| `HealthCheck` | 0 | Health check |

---

## What is NOT in the Protos

By design, the following are **absent** from the proto definitions:

| Omission | Reason |
|----------|--------|
| Direct push/merge to main API | Self-dev must go through PR (architecture §8.3) |
| Production deploy API | Not safe for autonomous execution |
| Secret/credential access API | Structural prohibition |
| Docker daemon control API | Sandbox boundary |
| System package install API | Potential security risk |
| SNS/DM send APIs (direct) | Blocked by Policy Engine deny patterns |
| Purchase API | Blocked by Policy Engine deny patterns |
| PERMANENT approval type | Nothing is permanently auto-approved |
