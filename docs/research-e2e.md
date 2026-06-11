# Research E2E — Integration Testing

> **Status**: Phase 3.5 (2026-06-11)  
> **Related**: [`research-agent.md`](research-agent.md), [`browser-safety.md`](browser-safety.md), [`testing.md`](testing.md)

## E2E Scenarios Covered

| # | Scenario | Level | Approval | Result |
|---|----------|-------|----------|--------|
| 1 | Read-only research (3 local HTML sources) | 0 | No | ✅ Sources collected, citations, report generated |
| 2 | Multi-source comparison (conflicting info) | 0 | No | ✅ Conflicting info flagged, uncertain points marked |
| 3 | Memory persistence (episodic, semantic, reflection) | 0 | No | ✅ All 4 memory types stored and queryable |
| 4 | Approval gating (Level 2 download/form fill blocked) | 2 | Yes | ✅ APPROVAL_NEEDED returned |
| 5 | Dangerous ops blocked (SNS, purchase, DM, CAPTCHA) | 3 | N/A | ✅ All DENIED |
| 6 | Unknown capability | — | N/A | ✅ NOT_FOUND |
| 7 | Graceful failure (broken sources) | — | N/A | ✅ Failed sources marked, report handles empty |

## Running

```bash
# All research E2E tests
cd ai-server && pytest tests/test_research_e2e.py tests/test_research_approval_e2e.py tests/test_research_memory_e2e.py -v

# Quick research tests (no approval)
cd ai-server && pytest tests/test_research_e2e.py -v

# Approval gating tests
cd ai-server && pytest tests/test_research_approval_e2e.py -v

# Memory persistence tests
cd ai-server && pytest tests/test_research_memory_e2e.py -v
```

## Pipeline

```
ResearchAgent.research_topic("Python 3.12", urls=[...])
  │
  ├─ SourceCollector.collect(url)
  │     ├─ browser.open_page → ToolBroker → PolicyEngine
  │     └─ browser.extract_page_text → ToolBroker → PolicyEngine
  │
  ├─ TextExtractor (clean, key points, entities)
  ├─ SourceRanker (domain + reliability + content score)
  ├─ CitationManager ([1], [2], ...)
  │
  ├─ EpisodicMemory.add(episode)
  ├─ SemanticMemory.add(fact) × N
  ├─ ProceduralMemory.add(procedure)
  ├─ ReflectionLog.add(reflection)
  │
  └─ ResearchReport { summary, key_findings, sources, conflicting_info, reference_list }
```

## Safety Verification

- **Level 0**: All read-only caps auto-allow (text extraction, title, links, screenshot)
- **Level 1**: open_page auto-allows (safe navigation)
- **Level 2**: download_file → APPROVAL_NEEDED, fill_form → APPROVAL_NEEDED
- **Level 3**: post_sns, purchase, send_message, captcha_bypass → DENIED
- **Unknown**: not_found → no approval request created
