# Draft: Capability Retrieval Refactor

## Requirements (confirmed)
- Replace full capability schema LLM passing with `CapabilityIndex` + `CapabilityRetriever` (lightweight catalog + Chroma vector search + keyword search + progressive detail retrieval)
- LLM receives only `ask_user`, `capability.search`, `capability.describe` meta tools as always-direct
- Executable capabilities: top_k_schema=8 full schemas, top_k_summary=50 lightweight summaries
- ToolBroker must validate with `catalog.resolve()` + `jsonschema` before execution
- Japanese aliases for screenshot/browser capabilities

## Research Findings (2026-06-16)

### STATUS: Implementation is ALREADY COMPLETE

After thorough code review, the entire spec described by the user has **already been implemented**:

| Component | File | Status |
|-----------|------|--------|
| CapabilityIndex + CapabilityRetriever | `aegis_ai/capability_index.py` (525 lines) | ✅ Complete |
| CapabilityDocument, SearchResult, Selection | `aegis_ai/capability_index.py` | ✅ Complete |
| Chroma vector backend + keyword fallback | `aegis_ai/capability_index.py` | ✅ Complete |
| Hash embedding (no external deps) | `_HashEmbeddingFunction` | ✅ Complete |
| Score synthesis (0.45/0.35/0.10/0.10) | `capability_index.py` lines 163-168 | ✅ Complete |
| Japanese aliases in keyword scoring | weighted alias field (1.6) | ✅ Complete |
| Runtime initialization | `runtime.py` lines 245-249 | ✅ Complete |
| Chat tools integration | `chat_tools.py` `get_tools_for_chat()` | ✅ Complete |
| Meta tool interception | `chat_tools.py` `_execute_meta_tool()` | ✅ Complete |
| Lightweight catalog in prompts | `chat_tools.py` `_build_tool_loop_prompt()` | ✅ Complete |
| ContextBuilder integration | `context_builder.py` lines 195-205 | ✅ Complete |
| LLMTaskInterpreter integration | `llm_task_interpreter.py` lines 261-287 | ✅ Complete |
| Autonomous Loop integration | `autonomous_loop.py` lines 618-628, 930-940 | ✅ Complete |
| ToolBroker jsonschema validation | `tool_broker.py` lines 715-723 | ✅ Complete |
| Dashboard reload + reindex | `dashboard_routes.py` lines 1079-1084 | ✅ Complete |
| Screenshot aliases/examples | `get_screenshot.json` | ✅ Complete |
| Browser browse aliases/examples | `browse.json` | ✅ Complete |
| CapabilityManifest aliases/examples | `folder_registry.py` lines 44-45, 167-168 | ✅ Complete |
| All 16 related tests passing | `test_capability_index.py`, etc. | ✅ All pass |

### What the user may actually need
The user presented a detailed spec that matches the existing implementation exactly. Possible interpretations:
1. **Verification** — They want confirmation that the implementation matches their spec
2. **Remaining gaps** — There may be minor gaps not caught in this analysis
3. **Extension** — They may want additional work beyond what's described
4. **Documentation** — They may need this documented

### Open Questions
- Is the user aware the implementation is already complete?
- Are there specific gaps or bugs they've noticed?
- Do they want additional alias/example coverage for other capabilities?
- Do they want the full test suite run (1336+ tests)?
- Is there a deployment/integration issue they're experiencing?

## Scope Boundaries
- INCLUDE: What the user described (all confirmed as already implemented)
- EXCLUDE: Unknown — need to ask user

## Test Strategy Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: Tests already exist and pass (16/16)
- **Agent-Executed QA**: Can run full test suite on request
