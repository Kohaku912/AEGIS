# AEGIS UI Instruction Summary

This file is a readable implementation summary of `UI_Instruction.md` for
environments where the original Japanese file is displayed with mojibake.

## Core Intent

AEGIS has three UI surfaces with shared information axes but separate layouts:

- Web Dashboard: command center, administration, debugging, audit, settings.
- Android App: mobile chat, approvals, emergency checks, concise status.
- Dedicated Display: read-only ambient status for current AI state and attention.

All surfaces must prioritize:

1. Now: what AEGIS is doing.
2. Attention: whether the user must act.
3. Next: what happens next.
4. History: what just happened.

## Visual Direction

The target is **AEGIS Operational Futurism**: practical, readable, advanced, and
not decorative. Avoid oversized generic cards, constant motion, unreadable thin
text, meaningless charts, color-only state, and a huge AI sphere that does not
carry information.

Use shared tokens from `design-tokens/tokens.json`:

- Dark layered surfaces.
- Cyan for normal accent.
- Violet for AI/internal/future state.
- Amber for approval/warning.
- Red for critical.
- Green only for explicit success/recovery, not always-online.

## Shared UI Requirements

Every real-time card or surface must expose:

- state text and icon/shape, not color alone
- freshness/live/stale/offline snapshot
- short explanation
- recovery hint where useful
- loading, empty, permission missing, degraded, disconnected, stale, partial,
  fatal error, unauthorized states

Raw JSON belongs only in developer/debug drawers.

## Web Dashboard Requirements

The Web Dashboard must keep seven primary areas:

- Command Center
- Work
- Approvals
- Systems
- Mind & Memory
- Activity
- Settings

It must show detailed audit, task, approval, server dependency, memory, usage,
settings history, errors, and task/approval relationships. Server health should
be summarized in Command Center and detailed in Systems.

## Dedicated Display Requirements

The Display is read-only and must never show Dashboard management controls.

It uses a fixed one-screen compositor:

- Global HUD
- Current Operation
- Attention
- Core Sphere
- Mission Rail
- Server Rail

Priority levels:

- P0: system critical, central takeover until resolved.
- P1: user action required, central amber takeover, no input buttons.
- P2: important overlay then attention dock.
- P3: ambient pulse/timeline.

Display must dedupe notifications, keep persistent unresolved items, replay SSE
after reconnect, show stale/offline snapshots correctly, hide personal data in
privacy mode, and pass 1366x768 / 1920x1080 / 2560x1440 no-scroll tests.

## Android Requirements

Android should be concise and useful away from the desk:

- Home: Now / Attention / Next / Systems.
- Approvals: same approval identity and risk context as Web.
- Tasks: summary plus drill-down.
- Devices and Permissions: actionable status and recovery.
- Settings: connection and safe mobile configuration.

It must handle phone portrait, landscape, tablet-like width, and 200% text scale.

## Contract Requirements

UI surfaces should consume normalized `ui-overview.v3` and `/api/ui/stream`.
They must not read audit files, chat history, settings files, or memory internals
directly.

Backend should provide visual hints and safe titles/messages so clients do not
infer critical UI behavior from raw event names.
