# LLM Router — Design & Usage

> **Status**: Implemented
> **Related**: `docs/model-policy.md`, `docs/architecture.md` §5.3

## Overview

The LLM Router routes tasks to appropriate LLM models based on task type,
privacy requirements, cost budget, and provider availability.

## Architecture

```
Agent (Research/Support/SelfDev/Reflection)
  ↓ LLMRequest(task_type, prompt, privacy_level)
LLMRouter
  ├── Privacy check (LOCAL_ONLY → mock/local only)
  ├── Cost budget check (daily/monthly limits)
  ├── Model Policy lookup (task_type → model profile)
  └── Provider dispatch
        ├── MockLLMProvider (CI/testing)
        ├── OpenAIProvider (optional)
        ├── AnthropicProvider (optional)
        └── LocalProvider (optional)
```

## Task Types

| Task Type | Description | Default Model |
|-----------|-------------|---------------|
| `RESEARCH_SUMMARY` | Summarize research findings | mock |
| `PLANNING` | Plan next steps | mock |
| `SUPPORT_SUGGESTION` | Generate support suggestions | mock |
| `SELF_DEV_ANALYSIS` | Analyze for self-improvement | mock |
| `CODE_GENERATION` | Generate code | mock |
| `REFLECTION` | Reflect on results | mock |
| `MEMORY_SUMMARIZATION` | Summarize memories | mock |
| `CLASSIFICATION` | Classify data | mock |
| `SMALL_FAST_TASK` | Quick tasks | mock |
| `HIGH_REASONING_TASK` | Complex reasoning | mock |

## Privacy Levels

| Level | Description | Behavior |
|-------|-------------|----------|
| `PUBLIC` | No sensitive data | Any provider |
| `INTERNAL` | Internal AEGIS data | Any provider |
| `SENSITIVE` | May contain user data | Redaction applied |
| `LOCAL_ONLY` | Must not leave local network | Mock/local only |

## Usage

```python
from aegis_ai.llm import LLMRouter, LLMRequest, TaskType, PrivacyLevel
from aegis_ai.llm.providers.mock import MockLLMProvider

router = LLMRouter()
router.register_provider("mock", MockLLMProvider())

request = LLMRequest(
    task_type=TaskType.PLANNING,
    prompt="Plan the next steps for the user",
    privacy_level=PrivacyLevel.INTERNAL,
)
response = router.route(request)
```

## Cost Control

```python
from aegis_ai.llm import CostTracker

tracker = CostTracker(daily_budget=10.0, monthly_budget=100.0)
router = LLMRouter(cost_tracker=tracker)

# Check budget before request
if tracker.can_afford(estimated_tokens=500):
    response = router.route(request)
```

## Privacy: External LLM Blocked

When `settings.privacy.external_llm_allowed = False`:
- Router automatically selects local/mock provider
- External providers (OpenAI, Anthropic) are skipped
- All requests use local-only processing
