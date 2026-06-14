## [2026-06-14] Initial Analysis

### Dashboard Display Issues
- `memory_summary` in home route (line 512-517) is HARDCODED with all zeros
  - episodic_count, semantic_count, procedural_count, reflection_count all 0
  - Should read from AdvancedMemory.get_stats(), EpisodicMemory.get_stats(), etc.
- `event_stats` hardcoded `{"total_published": 0}` (line 509)
- `trigger_stats` hardcoded `{"tasks_generated": 0}` (line 510)
- `api_overview` (line 1300-1309) also has hardcoded zeros for memory

### Available Memory Stats Methods
- `AdvancedMemory.get_stats()` returns: `{"entities": int, "facts": int, "conversations": int, "valid_facts": int}`
- `EpisodicMemory.get_stats()` returns: `{"total_episodes": int, "consolidated": int, "unconsolidated": int, ...}`
- `SemanticMemory.get_stats()` returns: `{"total_entries": int, "active": int, ...}`
- `ActionTraceMemory.get_stats()` returns: `{"total_traces": int, "active": int, "completed": int, "failed": int, ...}`

### LLM Overuse in Autonomous Loop
1. `_update_desires` (line 747-797): Calls LLM via `update_after_action` for EACH successful task, even when desire is near expected
2. `_decide_next_interval` (line 890-951): ALWAYS calls LLM for scheduling, even when all desires are healthy
3. `_auto_save_memory` (line 1369-1391): Calls `desire_system.update_after_action()` (LLM) after EVERY chat message