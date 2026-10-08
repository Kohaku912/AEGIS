# Mind Layer — Design & Usage

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).


> **Status**: Re-verified against the code **2026-10-04** — the *ContextBuilder Integration* section
> was corrected (its example passed kwargs the constructor does not accept and read fields that do
> not exist; it could not run). **Updated 2026-10-08**: `desire.py`, `priorities.py` and
> `social_intelligence.py` were deleted (`DELEGATION.md` §4 item 39) — their sections are gone
> from this document too. Layered affect model.
> **Related**: `docs/architecture.md` §5.11

## Overview

The Mind Layer is AEGIS's structured personality model — NOT sentient,
but persistent state that guides decision-making through ContextBuilder.

It uses a **three-layer affect model** (inspired by FAtiMA + LLMA):
1. **Personality** (long-term) — Big Five traits, stable
2. **Mood** (medium-term) — PAD model, influenced by emotion history
3. **Emotion** (short-term) — OCC-inspired appraisal, reactive

**Critical constraint**: Mind state does NOT override PolicyEngine safety decisions.

> ⚠️ **Measured 2026-10-04, updated 2026-10-08** — read this before the component list: of the
> components below, only **`Identity`** is actually constructed outside this package
> (`runtime.py:1164`). `Mood`, `Personality` and `LayeredEmotion` are live through `AffectSystem`;
> `Emotion` and `GoalManager` are constructed **nowhere** in `src/`. `Desire`, `Priorities` and
> `SocialIntelligence` were **deleted** on 2026-10-08 — nothing constructed them and nothing
> outside `mind/__init__.py` imported them. See *ContextBuilder Integration* below and
> `DELEGATION.md` §4 item 39.

## Components

### Identity (`identity.py`)

Defines who AEGIS is, its values, and policies.

| Field | Default | Purpose |
|-------|---------|---------|
| `name` | "AEGIS" | Agent name |
| `role` | "Autonomous multi-device AI assistant" | Agent role |
| `values` | help user, stay safe, learn, be curious, respect privacy | Core values |
| `safety_policy` | All actions through PolicyEngine | Safety constraint |
| `self_improvement_policy` | May analyze logs, propose improvements, create PRs | Self-dev constraint |
| `user_support_policy` | Proactive help, no consent for Level 2+ | User support constraint |

Persists to `data/mind_identity.jsonl`.

### Emotion (`emotion.py`)

State proxies that bias ContextBuilder. Not real emotions.

| Indicator | Range | Purpose |
|-----------|-------|---------|
| `urgency` | 0–10 | 0=calm, 10=critical |
| `confidence` | 0.0–1.0 | 0=uncertain, 1=very confident |
| `uncertainty` | 0.0–1.0 | 0=certain, 1=very uncertain |
| `fatigue_proxy` | 0.0–1.0 | Cognitive load proxy |
| `risk_sensitivity` | 0.0–1.0 | 0=risk-tolerant, 1=risk-averse |
| `novelty_interest` | 0.0–1.0 | 0=ignore novelty, 1=very interested |

**Key methods:**

- `update(...)` — Manually update any indicator
- `appraise_from_experience(action, observation, success, desire_name)` — Updates `confidence`, `fatigue_proxy`, and `uncertainty` based on action outcomes. Success increases confidence and decreases fatigue/uncertainty; failure decreases confidence and increases uncertainty.
- `is_urgent()` / `is_confident()` / `is_fatigued()` — Threshold checks

Persists to `data/mind_emotion.jsonl`.

### Personality (`personality.py`)

Long-term stable traits based on the Big Five (OCEAN) model.

| Trait | Default | High Value Means |
|-------|---------|------------------|
| `openness` | 0.7 | Curious, creative, open to new experiences |
| `conscientiousness` | 0.6 | Organized, dependable, disciplined |
| `extraversion` | 0.5 | Sociable, energetic, assertive |
| `agreeableness` | 0.6 | Cooperative, trusting, empathetic |
| `neuroticism` | 0.3 | Anxious, moody, emotionally unstable |

**Key methods:**

- `get_appraisal_bias()` — Returns multipliers (0.5–1.5) that influence emotion generation: `positive_valence_bias`, `negative_valence_bias`, `arousal_sensitivity`, `social_relevance`, `novelty_seeking`, `control_perception`
- `get_mood_baseline()` — Returns PAD (Pleasure-Arousal-Dominance) baseline derived from traits
- `update_trait(trait_name, delta)` — Nudge a trait (very small changes, 0.01–0.05)

Persists to `data/mind_personality.jsonl`.

### Mood (`mood.py`)

Medium-term affective state using the PAD (Pleasure-Arousal-Dominance) model.
Sits between personality (long-term) and emotion (short-term).

| Dimension | Range | Purpose |
|-----------|-------|---------|
| `pleasure` | -1.0 to 1.0 | Negative to positive affect |
| `arousal` | 0.0 to 1.0 | Calm to excited |
| `dominance` | 0.0 to 1.0 | Low to high control |

Mood labels are derived from PAD values (e.g., "cheerful", "tense", "serene").

**Key methods:**

- `update_from_emotion(pleasure, arousal, dominance, weight)` — Weighted moving average update
- `decay_toward_baseline(baseline)` — Exponential decay toward personality-derived baseline (half-life: 6 hours)
- `get_emotion_modulation()` — Returns multipliers that influence emotion generation: `positive_emotion_boost`, `negative_emotion_boost`, `arousal_modulation`
- `label` — Closest mood label (e.g., "cheerful", "stressed")

Persists to `data/mind_mood.jsonl`.

### LayeredEmotion (`layered_emotion.py`)

Short-term affective states using OCC-inspired appraisal.
Emotions are generated through appraisal of events against goals, standards, and preferences.

| Emotion Type | Valence | Category |
|--------------|---------|----------|
| Joy / Distress | +/− | Reactions to events |
| Hope / Fear | +/− | Prospective emotions |
| Satisfaction / Disappointment | +/− | Confirmation emotions |
| Pride / Shame | +/− | Self-attributed reactions |
| Admiration / Reproach | +/− | Other-attributed reactions |
| Gratitude / Anger | +/− | Other-attributed (helpful/harmful) |
| Love / Hate | +/− | Attraction-based |
| Surprise / Curiosity / Boredom / Frustration | mixed | Compound/derived |

Emotions decay over time (high-arousal emotions decay faster).

**Key methods:**

- `appraise_and_generate(trigger, appraisal, ...)` — Core emotion generation from appraisal pattern
- `get_active_emotions()` / `get_dominant_emotion()` — Query current state
- `get_pad_contribution()` — PAD values for mood updates

Persists to `data/mind_layered_emotion.jsonl`.

### AffectSystem (`affect_system.py`)

Integrated layered affect system that orchestrates Personality, Mood, and LayeredEmotion.

**Layer interactions:**
- Personality → appraisal biases → emotion generation
- Personality → mood baseline → mood tendencies
- Emotions → accumulate → mood updates
- Mood → modulation → emotion generation

**Key methods:**

- `appraise_event(trigger, desirability, ...)` — Full appraisal cycle: build pattern → get biases → get modulation → generate emotions → update mood
- `appraise_from_experience(action, observation, success, desire_name)` — Convenience method that derives appraisal parameters from outcome
- `appraise_user_interaction(user_message, bot_response, positive_outcome)` — Appraise user interactions
- `to_context_string()` — Full affect state for LLM prompts

Persists to `data/mind_personality.jsonl`, `data/mind_mood.jsonl`, `data/mind_layered_emotion.jsonl`.

### Goals (`goals.py`)

Tracks short-term, long-term, and recurring goals with progress.

| Goal Type | Purpose |
|-----------|---------|
| `SHORT_TERM` | Immediate tasks |
| `LONG_TERM` | Ongoing objectives |
| `RECURRING` | Repeated tasks |

| Goal Status | Purpose |
|-------------|---------|
| `ACTIVE` | Currently being pursued |
| `COMPLETED` | Successfully finished |
| `ABANDONED` | Given up |
| `PAUSED` | Temporarily suspended |

Each goal has: `description`, `priority` (1=highest, 10=lowest), `status`, `progress` (0.0–1.0), `tags`, `notes`.

Persists to `data/mind_goals.jsonl`.

## ContextBuilder Integration

**Only `Identity` is injected in production.** Measured 2026-10-04: `src/` contains exactly
**one** `ContextBuilder(` call site (`runtime.py:979`), and of the mind-layer components it
passes **only `identity=`**:

```python
# runtime.py — the only construction site
context_builder = ContextBuilder(
    event_bus=event_bus,
    tool_broker=tool_broker,
    multimodal_llm=llm_gateway,
    capability_retriever=capability_retriever,
    settings_resolver=settings_resolver,
    user_model_store=user_model_store,
    identity=identity,          # <- from aegis_ai.mind.identity
)
```

`ContextBuilder.__init__` *does* accept `identity`, `desire`, `emotion` and `goal_manager`, so
`ctx.desires` / `ctx.emotional_state` / `ctx.current_goals` would be populated if those were
passed — they are not. It does **not** accept `affect_system` or `social_intelligence`, and
`Context` has **no** `affect` or `social` field:

```python
ContextBuilder(affect_system=None)
# TypeError: ContextBuilder.__init__() got an unexpected keyword argument 'affect_system'
```

`AffectSystem` reaches the model by a different route — `runtime.py:1852` (the autonomous
loop) and `llm/memory_context.py:323` (the `decision` profile) construct it — but never
through `ContextBuilder`.

An earlier version of this section showed an example that passed `affect_system=` /
`social_intelligence=` and read `ctx.affect` / `ctx.social`; it could not run. See
`DELEGATION.md` §4 item 39 for the unwired components (two remain — `Emotion` and `GoalManager`;
three were deleted 2026-10-08), and item 38 for the
`_load` failures that used to be silent.

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                  AffectSystem                    │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐  │
│  │Personality │→│   Mood   │→│LayeredEmotion│  │
│  │ (Big Five) │  │  (PAD)   │  │ (OCC-based)  │  │
│  └───────────┘  └──────────┘  └──────────────┘  │
│       ↑              ↑↓              ↑↓          │
│       └──────────────┴───────────────┘           │
└─────────────────────────────────────────────────┘
         ↓
┌────────────────┐
│    Emotion     │
│  (state proxy) │
└────────────────┘
         ↓
┌─────────────────────────────────────────────────┐
│              ContextBuilder                      │
│              Identity only                       │
└─────────────────────────────────────────────────┘
```

> ⚠️ **Measured 2026-10-04, updated 2026-10-08**: the bottom box overstates production. The only
> `ContextBuilder(` call site in `src/` is `runtime.py:979`, and it passes **only `Identity`** —
> `Emotion`, `GoalManager` and `AffectSystem` are never handed to it (`GoalManager` *would* be
> accepted; `AffectSystem` would raise `TypeError`). `Emotion` and `GoalManager` are constructed
> nowhere in `src/` at all; `Desire`, `Priorities` and `SocialIntelligence` no longer exist
> (deleted 2026-10-08). See `DELEGATION.md` §4 item 39.

## Safety

- Mind state NEVER overrides PolicyEngine decisions
- Desire weights are context biases, not permission grants
- Emotion state is informational, not authoritative
- Desire weights are context biases only — no desire value grants a permission
- Personality changes are tiny deltas (0.01–0.05) — large shifts require many experiences
- Mood decays toward personality baseline (6-hour half-life)
- AffectSystem biases decisions but never overrides safety gates
