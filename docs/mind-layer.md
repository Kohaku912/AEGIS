# Mind Layer — Design & Usage

> **Status**: Verified against current code snapshot — layered affect model
> **Related**: `docs/architecture.md` §5.11

## Overview

The Mind Layer is AEGIS's structured personality model — NOT sentient,
but persistent state that guides decision-making through ContextBuilder.

It uses a **three-layer affect model** (inspired by FAtiMA + LLMA):
1. **Personality** (long-term) — Big Five traits, stable
2. **Mood** (medium-term) — PAD model, influenced by emotion history
3. **Emotion** (short-term) — OCC-inspired appraisal, reactive

**Critical constraint**: Mind state does NOT override PolicyEngine safety decisions.

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

### Desire (`desire.py`)

Priorities that bias decision-making. Higher weight = higher priority.

| Desire | Default Weight | Purpose |
|--------|---------------|---------|
| `help_user` | 1.0 | Effectively assist the user |
| `stay_safe` | 0.95 | Never bypass safety gates |
| `learn` | 0.8 | Learn from interactions |
| `be_useful` | 0.75 | Proactively suggest helpful actions |
| `avoid_annoying_user` | 0.7 | Don't spam or interrupt |
| `reduce_repeated_failures` | 0.65 | Learn from failures |
| `be_curious` | 0.6 | Explore when appropriate |

Persists to `data/mind_desire.jsonl`.

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

### Priorities (`priorities.py`)

Calculates priority scores based on Mind state. Used by ContextBuilder.

- Combines desire weights, emotion state, and goal relevance
- `score_action(action_type, context)` — Returns `PriorityScore` (0.0–1.0) with reason
- `should_defer(action_type)` — Returns True if fatigued or desire weight < 0.3
- Never overrides PolicyEngine

### SocialIntelligence (`social_intelligence.py`)

Tracks social context and interaction patterns to adapt response behavior.

| Indicator | Range | Default | Purpose |
|-----------|-------|---------|---------|
| `formality` | 0.0–1.0 | 0.5 | 0=casual, 1=formal |
| `verbosity` | 0.0–1.0 | 0.5 | 0=concise, 1=detailed |
| `user_patience` | 0.0–1.0 | 0.7 | 0=impatient, 1=patient |
| `interaction_count` | int | 0 | Total interactions tracked |

**Key methods:**

- `update_from_interaction(action, response, feedback)` — Adjusts formality/verbosity based on user feedback (e.g., "too long" → less verbose, "too formal" → less formal)
- `to_context_string()` — Social state for ContextBuilder

Persists to `data/mind_social.jsonl`.

## ContextBuilder Integration

Mind Layer components are injected into ContextBuilder:

```python
from aegis_ai.mind import (
    Identity, Desire, Emotion, GoalManager,
    SocialIntelligence, AffectSystem,
)

builder = ContextBuilder(
    identity=Identity(),
    desire=Desire(),
    emotion=Emotion(),
    goal_manager=GoalManager(),
    affect_system=AffectSystem(),
    social_intelligence=SocialIntelligence(),
)
ctx = builder.build()
# ctx.identity contains identity string
# ctx.desires contains desire priorities
# ctx.emotional_state contains emotion indicators
# ctx.current_goals contains active goals
# ctx.affect contains layered affect state
# ctx.social contains social context
```

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
         ↓                    ↓
┌────────────────┐  ┌─────────────────┐
│    Emotion     │  │   SocialIntel   │
│  (state proxy) │  │ (interaction)   │
└────────────────┘  └─────────────────┘
         ↓                    ↓
┌─────────────────────────────────────────────────┐
│              ContextBuilder                      │
│  Identity + Desire + Goals + Priorities          │
│  + AffectSystem + Emotion + SocialIntelligence   │
└─────────────────────────────────────────────────┘
```

## Safety

- Mind state NEVER overrides PolicyEngine decisions
- Desire weights are context biases, not permission grants
- Emotion state is informational, not authoritative
- "stay_safe" desire (0.95) is high but doesn't grant extra permissions
- Personality changes are tiny deltas (0.01–0.05) — large shifts require many experiences
- Mood decays toward personality baseline (6-hour half-life)
- AffectSystem biases decisions but never overrides safety gates
