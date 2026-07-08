# LLM Router — Design & Usage

> **Status**: Implemented (verified against current code snapshot)
> **Related**: `docs/model-policy.md`, `docs/architecture.md` §5.10

## Overview

The LLM system routes tasks to appropriate LLM models based on task type,
privacy requirements, cost budget, and provider availability. Architecture:

```
LLMGateway (facade)
  ├── LLMSettingsResolver (YAML profiles from config/llm.yaml)
  ├── LLMRouter
  │     ├── Privacy check (LOCAL_ONLY → mock/local only)
  │     ├── Cost budget check (daily/monthly limits)
  │     ├── Model Policy lookup (task_type → model profile)
  │     └── Provider dispatch
   │           ├── MockLLMProvider (CI/testing)
   │           ├── OpenAIProvider (DeepSeek/OpenAI compatible)
   │           └── LocalProvider / Ollama (optional)
  └── PromptRegistry (YAML prompts from config/prompts.yaml)
```

### LLMGateway

**File**: `src/aegis_ai/llm/gateway.py`

Runtime-owned facade over LLMRouter. Created once at startup via
`create_llm_provider_from_settings()`. Backward-compatible method
signatures with optional `profile` keyword for profile-based resolution.

### PromptRegistry

**File**: `src/aegis_ai/llm/prompt_registry.py`

YAML-backed prompt management. `ai-server/config/prompts.yaml` is the
source of truth. Loads, renders, hot-reloads (mtime-gated), and updates
prompts with fail-closed validation.

### LLMSettingsResolver

**File**: `src/aegis_ai/llm/settings_resolver.py`

YAML-backed LLM profile resolution. `ai-server/config/llm.yaml` is the
source of truth. Validates against allowed_models/max_tokens_upper_bound/
temperature bounds. Hot-reloads on mtime change.

## Task Types

| Task Type | Description | Default Model |
|-----------|-------------|---------------|
| `RESEARCH_SUMMARY` | Summarize research findings | profile-driven |
| `PLANNING` | Plan next steps | profile-driven |
| `SUPPORT_SUGGESTION` | Generate support suggestions | profile-driven |
| `SELF_DEV_ANALYSIS` | Analyze for self-improvement | profile-driven |
| `CODE_GENERATION` | Generate code | profile-driven |
| `REFLECTION` | Reflect on results | profile-driven |
| `MEMORY_SUMMARIZATION` | Summarize memories | profile-driven |
| `CLASSIFICATION` | Classify data | profile-driven |
| `SMALL_FAST_TASK` | Quick tasks | profile-driven |
| `HIGH_REASONING_TASK` | Complex reasoning | profile-driven |

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

## Text-Based Tool Calling (DeepSeek)

When using DeepSeek, AEGIS uses text-based tool calling with regex parsing
of `<tool_call>...</tool_call>` instead of OpenAI's `tools` parameter
(DeepSeek returns unparsable native format when `tools` is used).

The `call_llm_with_tools()` function in `chat_tools.py` handles:
1. Prompt construction with tool descriptions
2. LLM call
3. Regex parsing of tool calls
4. Tool execution via ToolBroker
5. Follow-up response generation

## Cost Control

```python
from aegis_ai.llm import CostTracker

tracker = CostTracker(daily_budget=10.0, monthly_budget=100.0)
router = LLMRouter(cost_tracker=tracker)

if tracker.can_afford(estimated_tokens=500):
    response = router.route(request)
```

## Privacy: External LLM Blocked

When `settings.privacy.external_llm_allowed = False`:
- Router automatically selects local/mock provider
- External providers (OpenAI, Anthropic) are skipped
- All requests use local-only processing
