# Mind Layer — Design & Usage

> **Status**: Phase 6 — Full implementation with persistence
> **Related**: `docs/architecture.md` §5.11

## Overview

The Mind Layer is AEGIS's structured personality model — NOT sentient,
but persistent state that guides decision-making through ContextBuilder.

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

Persists to `data/mind_emotion.jsonl`.

### Goals (`goals.py`)

Tracks short-term, long-term, and recurring goals with progress.

| Goal Type | Purpose |
|-----------|---------|
| `SHORT_TERM` | Immediate tasks |
| `LONG_TERM` | Ongoing objectives |
| `RECURRING` | Repeated tasks |

Each goal has: `description`, `priority`, `status`, `progress` (0.0–1.0).

Persists to `data/mind_goals.jsonl`.

### Priorities (`priorities.py`)

Calculates priority scores based on Mind state. Used by ContextBuilder.

- Combines desire weights, emotion state, and goal relevance
- `should_defer()` — returns True if action should be deferred
- Never overrides PolicyEngine

## ContextBuilder Integration

Mind Layer components are injected into ContextBuilder:

```python
builder = ContextBuilder(
    identity=Identity(),
    desire=Desire(),
    emotion=Emotion(),
    goal_manager=GoalManager(),
)
ctx = builder.build()
# ctx.identity contains identity string
# ctx.desires contains desire priorities
# ctx.emotional_state contains emotion indicators
# ctx.current_goals contains active goals
```

## Safety

- Mind state NEVER overrides PolicyEngine decisions
- Desire weights are context biases, not permission grants
- Emotion state is informational, not authoritative
- "stay_safe" desire (0.95) is high but doesn't grant extra permissions
