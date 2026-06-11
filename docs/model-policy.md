# Model Policy — LLM Model Configuration

> **Status**: Implemented
> **Related**: `docs/llm-router.md`

## Overview

Model Policy defines which LLM model to use for each task type,
along with cost, privacy, and capability constraints.

## Model Profiles

Each model profile defines:

| Field | Description |
|-------|-------------|
| `provider` | Provider name (mock, openai, anthropic, local) |
| `model` | Model identifier |
| `max_tokens` | Maximum tokens per request |
| `temperature` | Sampling temperature |
| `cost_per_1k_tokens` | Cost per 1000 tokens |
| `privacy_level` | Privacy level (PUBLIC, INTERNAL, SENSITIVE, LOCAL_ONLY) |
| `allowed_task_types` | Which task types this model can handle |
| `disallowed_for_sensitive_data` | Whether to block for sensitive contexts |
| `fallback_model` | Fallback if primary model fails |
| `requires_user_confirmation` | Whether user must confirm before use |

## Default Profiles

| Profile | Provider | Model | Privacy | Cost |
|---------|----------|-------|---------|------|
| `mock` | mock | mock-model | PUBLIC | $0 |
| `local` | local | local-model | LOCAL_ONLY | $0 |

## Task-to-Model Mapping

All task types default to `mock` profile. Users can change mappings:

```python
from aegis_ai.llm import ModelPolicy, ModelProfile, TaskType

policy = ModelPolicy()
policy.add_profile("gpt4", ModelProfile(
    provider="openai",
    model="gpt-4",
    cost_per_1k_tokens=0.03,
    privacy_level=PrivacyLevel.INTERNAL,
))
policy.set_task_model(TaskType.HIGH_REASONING_TASK, "gpt4")
```

## Adding External Providers

To add OpenAI/Anthropic providers:
1. User confirms the provider addition
2. API key is stored securely (environment variable, not code)
3. Model profile is added to policy
4. Task mappings are updated

**Requires user confirmation** for new providers.
