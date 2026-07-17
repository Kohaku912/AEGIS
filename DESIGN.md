# AEGIS Design Language

## Vision

Calm spatial intelligence, not decorative sci-fi. Every visible object must
explain an active domain, lifecycle state, causal relation, or required action.

## Information Dimensions

AEGIS encodes domain, urgency, lifecycle, time, causality, confidence,
ownership, and interaction independently. Color identifies information domain;
shape, line style, depth, label, and motion identify operational state.

## Semantic Colors

| Domain | Token | Role |
| --- | --- | --- |
| Cognition / Planning | `cognition` | reasoning and selected plans |
| Observation / Sensors | `perception` | inbound evidence |
| Task / Execution | `action` | active mission work |
| Memory / Context | `memory` | retrieved context and provenance |
| User / Communication | `communication` | conversations and user state |
| Device / Infrastructure | `infrastructure` | servers, devices, and transport |
| Policy / Approval | `policy` | gates and controlled actions |
| Security / Critical | `critical` | isolated failures and threats |
| Recovery | `recovery` | transient reconstruction only |

Green is never a steady online color. Recovery returns to the domain color.

## Status Modifiers

- Planned: dotted, low contrast, placed ahead of the focus plane.
- Active: solid, directional packet flow, high local contrast.
- Waiting: stopped at a visible gate with a slow pulse.
- Stale: desaturated, unstable outline, timestamp visible.
- Failed: broken path and settled diagnostic fragments; no continuous flash.
- Offline: dark region and absent connection path.
- Recovering: ordered isolate, restart, reconnect, verify, resume stages.
- Complete: one white transit wave, then return to domain color.

## Depth Model

1. Environment at `z=-1200`: horizon, confidence, time, quiet particles.
2. Memory at `z=-800`: only memories used by the current mission.
3. Topology at `z=-450`: fixed functional regions, never concentric rings.
4. Mission at `z=0`: observe, understand, plan, approve, execute, verify, complete.
5. Execution at `z=250`: current capability and directional packets.
6. Attention at `z=500`: actionable signals attached to their source region.
7. Takeover at `z=900`: critical cause, impact, and recovery path.

Depth requires perspective scale, occlusion, fog, focus, thickness, and local
lighting. Bloom alone is not depth.

## Motion Grammar

- Ambient: 12-20 seconds, quiet drift, no focal rotation.
- Observe: 600-900ms from source region toward cognition.
- Plan: 1-2 seconds of branching followed by selected-path convergence.
- Execute: continuous cognition-to-capability-to-target packets.
- Approve: execution decelerates and stops before the policy gate.
- Fail: 100-160ms break, 500-800ms settle, then static diagnosis.
- Recover: isolate, restart, reconnect, verify, resume.
- Complete: one white wave; no permanent completion color.

Only one dominant motion may own attention at a time. Motion must be driven by
an event or state transition.

## Shape Grammar

- Sensor: thin open arc.
- Memory: soft band, cloud, or crystal.
- Plan: branching lattice.
- Execution: straight corridor, arrow, or packet.
- Device: stable hexagonal plate.
- User: soft circular form.
- Policy: closed boundary and visible gate.
- Failure: sharp cut and separated fragments.
- Recovery: reconnecting curve.

## Typography

Display type is reserved for the current mission or critical takeover.
Operational headings are compact. Labels and metrics use stable dimensions.
Identifiers, timestamps, and provenance use monospace. Long text remains DOM
content and is never forced into WebGL.

## Scene States

- Idle: diffuse intelligence without a central sphere.
- Observing: inbound evidence converges on the focus plane.
- Planning: a 3D lattice branches and selects one path.
- Executing: a directed corridor connects cognition to target.
- Waiting / Approval: the corridor stops at an amber containment gate.
- Critical: topology moves back and a diagnostic cutaway takes focus.
- Recovery: affected structures reassemble in ordered stages.
- Complete: a single white wave resolves to idle.

## Surface Adaptation

- Dedicated display: full Cognitive Field, camera transitions, no controls.
- Dashboard: compact interactive topology plus readable management surfaces.
- Android: 2D Material-style domain color, shape, size, and shared-axis motion.
- PC overlay: appearance, progress, resolution only; no ambient 3D.
- Room display: concise scene and acknowledgment state.

## Accessibility

All states have labels and non-color encoding. Grayscale and color-vision
variants preserve shape and line style. Reduced motion uses static source,
target, gate, break, and recovery-stage diagrams. Privacy redacts DOM and scene
labels before rendering.

## Performance Budget

- High: full 3D, particles, restrained post-processing, target 60fps at 1080p.
- Medium: 3D topology and lightweight bloom.
- Low: Canvas/SVG 2.5D without post-processing.
- Reduced motion: static spatial structure and state deltas.
- Pixel ratio is capped; inactive particles and effects are pooled.

## Prohibited Patterns

- Meaningless constant rotation.
- A central sphere as the only cognition metaphor.
- All-cyan or one-hue interfaces.
- Constant red flashing.
- Glow-only hierarchy.
- Flat concentric server rings.
- Decorative metrics without operational meaning.
- Raw JSON outside Developer Mode.
- Dangerous actions without preview, approval, and fresh authentication.
