# Desire System — Design & Usage

> **Status**: Implemented (2026-06-13)
> **Inspired by**: D2A (Desire-driven Autonomous Agent) — https://github.com/zfw1226/D2A

## Overview

AEGIS's desire system implements intrinsic motivations that drive autonomous behavior.
Based on the D2A framework from ICLR 2025.

## Desires (0-10 scale)

| Desire | Description | Low State | High State |
|--------|-------------|-----------|------------|
| **social_connectivity** | Need for social interaction | Isolated, lonely | Connected, engaged |
| **personal_fulfillment** | Need for growth and achievement | Unfulfilled | Accomplished |
| **curiosity** | Need for exploration and learning | Uninterested | Fascinated |
| **safety** | Need for security and stability | Vulnerable | Secure |
| **recognition** | Need for acknowledgment | Unappreciated | Respected |
| **autonomy** | Need for independence | Dependent | Self-determined |
| **creativity** | Need for self-expression | Uninspired | Innovative |
| **purpose** | Need for meaning and direction | Aimless | Purposeful |

**Note**: Physiological needs (hunger, thirst, sleepiness) are excluded.

## How It Works

### 1. Time-Based Decay

Desires naturally decrease over time:
- Decay rate: 0.1 per hour
- Applied before each evaluation
- Prevents desires from staying at maximum

### 2. Action Evaluation

After each action, LLM evaluates how it affects desires:
```
Action: Helped user with coding
Observation: User was satisfied

→ social_connectivity: 7.0 → 7.5 (positive interaction)
→ personal_fulfillment: 5.5 → 6.0 (task achievement)
→ recognition: 6.0 → 6.5 (user appreciation)
→ purpose: 5.0 → 5.5 (being useful)
```

### 3. Task Generation

When desires are below threshold (4.0):
1. Identify low desires
2. LLM generates tasks to fulfill them
3. Execute tasks autonomously
4. Update desires based on results

### 4. Self-Scheduling

LLM decides when to run next:
- Low desires → Run sooner (5-15 minutes)
- Balanced desires → Run later (30-60 minutes)
- High desires → Run much later (1-2 hours)
- Fallback: 1 hour if not called

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/desires` | GET | Get current desire states |
| `/api/autonomous/status` | GET | Get autonomous loop status |
| `/api/autonomous/trigger` | POST | Manual trigger |
| `/api/autonomous/start` | POST | Start autonomous loop |
| `/api/autonomous/stop` | POST | Stop autonomous loop |

## Data Storage

- `data/desires/desire_state.json` — Current desire values
- `data/autonomous/loop_state.json` — Loop scheduling state
- `data/autonomous/execution_log.jsonl` — Execution history

## Design Decisions

1. **D2A-inspired**: Based on ICLR 2025 paper
2. **LLM evaluation**: LLM evaluates how actions affect desires
3. **No keyword matching**: All decisions through LLM
4. **Self-scheduling**: AI decides when to run next
5. **Desire-driven**: Desires drive autonomous behavior
6. **Excluded physiological**: No hunger, thirst, sleepiness
