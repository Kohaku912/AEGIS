# Capability Management Unification Plan

## Goal
Unify AEGIS capability management to folder-based system. Single source of truth: `capabilities/{builtin,generated}/{server_id}/{app_id}/{action}.json`.

## Current Problems
1. `_capability_from_manifest()` in tool_broker.py converts `pc-server` → `pc` prefix (OLD format)
2. ServerExecutor has hardcoded AGORA routing with `ai-server.agora.*` IDs
3. Multiple places create FolderCapabilityRegistry instances
4. LLMTaskInterpreter uses `self._registry.list_all()` instead of `CapabilityCatalog.list_for_llm()`
5. ID format inconsistency: `pc.app.action` vs `pc-server.app.action`

## Target State
- **ID format**: `server_id.app_id.action` (canonical, e.g., `pc-server.screenshot.get_screenshot`)
- **Single source**: CapabilityCatalog loads from folder, registers into ToolRegistry
- **Startup**: Dashboard creates CapabilityCatalog → registers all into ToolRegistry
- **LLMTaskInterpreter**: Uses `CapabilityCatalog.list_for_llm()`
- **ServerExecutor**: Uses manifest from CapabilityCatalog for routing
- **Old IDs**: Aliases in CapabilityCatalog._aliases

## TODOs

- [x] 1. Fix `_capability_from_manifest()` to use canonical ID format
  - Change prefix mapping: `pc-server` → `pc-server` (not `pc`)
  - Update all prefix mappings to use full `server_id`

- [x] 2. Fix ServerExecutor to use CapabilityCatalog for routing
  - Remove hardcoded AGORA routing
  - Use `self._catalog.resolve(cap_id)` to get manifest
  - Route by `manifest.server_id` instead of prefix matching

- [x] 3. Fix LLMTaskInterpreter to use CapabilityCatalog
  - Change `_build_capability_list()` to use `CapabilityCatalog.list_for_llm()`
  - Accept `capability_catalog` parameter instead of `capability_registry`

- [x] 4. Fix dashboard_routes.py startup
  - Single CapabilityCatalog instance
  - Register all capabilities into ToolRegistry using canonical IDs
  - Pass catalog to ServerExecutor and LLMTaskInterpreter

- [x] 5. Update AGENTS.md
  - Document new capability management architecture
  - Update ID format conventions

## Final Verification Wave

- [x] F1. py_compile all modified files
- [x] F2. Verify capability IDs are canonical format in ToolRegistry
- [x] F3. Verify LLMTaskInterpreter uses CapabilityCatalog.list_for_llm()
