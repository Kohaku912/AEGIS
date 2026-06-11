# Research Agent — Design & Usage

> **Status**: Phase 3.3 — Minimal implementation (2026-06-11)  
> **Related**: [`architecture.md`](architecture.md) §5.5

## Overview

The Research Agent conducts deep-dive information gathering by:
1. Collecting sources from URLs via Browser Server
2. Extracting and cleaning page text
3. Ranking sources by reliability and relevance
4. Assigning citation labels
5. Building a structured report with summary and findings

## Architecture

```
ResearchAgent.research_topic("topic", urls=[...])
  │
  ├─ SourceCollector.collect(url)
  │     ├─ ToolBroker.invoke_tool("browser.open_page", {url})
  │     ├─ ToolBroker.invoke_tool("browser.extract_page_text", {})
  │     ├─ Assess reliability (domain heuristic)
  │     └─ SourceNote { source_id, url, title, extracted_text_summary, key_points, ... }
  │
  ├─ TextExtractor.extract(raw_text)
  │     └─ ExtractedContent { cleaned_text, key_points, word_count, entities }
  │
  ├─ SourceRanker.rank(sources)
  │     ├─ Domain priority (official > documentation > news > blog > forum)
  │     ├─ Reliability priority (high > medium > unknown > low > unverified)
  │     └─ Content richness score
  │
  ├─ CitationManager
  │     └─ [1], [2], [3], ... labels
  │
  └─ ReportBuilder.build(topic, sources)
        └─ ResearchReport { summary, key_findings, conflicting_info, reference_list }
```

## SourceNote Fields

| Field | Description |
|-------|-------------|
| source_id | Unique identifier |
| url | Source URL |
| title | Page title |
| accessed_at | When the source was collected |
| extracted_text_summary | First ~500 chars of extracted text |
| key_points | Top 5 key sentences |
| reliability_hint | high/medium/low/unverified/unknown |
| domain_category | official/documentation/news/blog/forum |
| citation_label | [1], [2], etc. |

## Testing with Local HTML

```python
from aegis_ai.agents.research import ResearchAgent

agent = ResearchAgent()
fixtures = [
    ("https://docs.python.org/3.12/", "Python 3.12", "<html>...</html>"),
    ("https://example.com", "Example", "<html>...</html>"),
]
sources = agent.collect_local(fixtures)
report = agent.research_topic("Python 3.12", urls=["https://docs.python.org/3.12/"])
```

## Safety

- All browser operations go through `ToolBroker.invoke_tool()` which enforces `PolicyEngine`
- No SNS posting, DM sending, purchases — blocked by PolicyEngine
- No login/credential storage
- No CAPTCHA bypass
- No ToS bypass automation
- No assumption of truth — conflicting info is flagged as "uncertain"
