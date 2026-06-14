## Capability Unification Learnings

### Key Changes Made

1. **tool_broker.py** - `_capability_from_manifest()` now uses canonical ID format (`server_id.app_id.action`) instead of converting to old format (`pc.app.action`)

2. **server_executor.py** - Simplified to use CapabilityCatalog for manifest-driven routing. Removed hardcoded AGORA/search routing. Routes by `manifest.server_id` instead of prefix matching.

3. **llm_task_interpreter.py** - Added `capability_catalog` parameter. `_build_capability_list()` now prefers `CapabilityCatalog.list_for_llm()` over `ToolRegistry.list_all()`.

4. **AGENTS.md** - Added Capability Management section documenting the folder-based architecture, ID format, aliases, and startup flow.

### ID Format Convention

- **Canonical**: `server_id.app_id.action` (e.g., `pc-server.screenshot.get_screenshot`)
- **Old format (alias)**: `prefix.app.action` (e.g., `pc.screenshot.get_screenshot`)
- **Short format (alias)**: `app.action` (e.g., `screenshot.get_screenshot`)
