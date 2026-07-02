from __future__ import annotations

import json
import time
from types import SimpleNamespace

from aegis_ai.analysis.prompt_usage import PromptUsageAnalyzer, render_html_report


class _PromptUsageLLM:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        payload = json.loads(kwargs["prompt"])
        sections = []
        for section in payload["sections"]:
            usage = "unused" if "unused" in section["title"].lower() else "used"
            sections.append(
                {
                    "section_id": section["section_id"],
                    "usage": usage,
                    "confidence": 0.9,
                    "evidence": f"{section['title']} evidence",
                    "suggestion": "Keep it" if usage == "used" else "Compress or remove this section.",
                }
            )
        return SimpleNamespace(success=True, content=json.dumps({"sections": sections}))


def test_prompt_usage_analyzer_uses_recent_audit_entries_and_llm_sections(tmp_path) -> None:
    now_ms = int(time.time() * 1000)
    entries = [
        {
            "entry_id": "recent",
            "timestamp_ms": now_ms,
            "action": "llm_call",
            "detail": {
                "prompt_preview": "TASK:\nSummarize current state\nUNUSED CONTEXT:\nVerbose old logs",
                "response_preview": "Current state summarized.",
                "tokens": 120,
                "tool_calls": [],
            },
        },
        {
            "entry_id": "old",
            "timestamp_ms": now_ms - 49 * 3_600_000,
            "action": "llm_call",
            "detail": {"prompt_preview": "OLD:\nIgnore", "response_preview": "Old"},
        },
        {
            "entry_id": "non-llm",
            "timestamp_ms": now_ms,
            "action": "tool_call",
            "detail": {"prompt_preview": "TOOL:\nIgnore"},
        },
    ]
    llm = _PromptUsageLLM()
    analyzer = PromptUsageAnalyzer(llm_provider=llm)

    report = analyzer.analyze(hours=24, entries=entries)

    assert report["prompts_analyzed"] == 1
    assert report["entries_considered"] == 1
    assert llm.calls
    unused = [item for item in report["section_summary"] if item["unused"]]
    assert unused
    assert report["candidate_savings_tokens"] > 0

    json_path = tmp_path / "prompt_usage.json"
    html_path = tmp_path / "prompt_usage.html"
    analyzer.write_report(report, json_path=json_path, html_path=html_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["prompts_analyzed"] == 1
    assert "AEGIS Prompt Usage Report" in html_path.read_text(encoding="utf-8")


def test_render_html_report_includes_metrics() -> None:
    html = render_html_report(
        {
            "prompts_analyzed": 2,
            "estimated_prompt_tokens": 100,
            "candidate_savings_tokens": 20,
            "analysis_status": "ok",
            "section_summary": [
                {
                    "title": "UNUSED CONTEXT",
                    "count": 1,
                    "unused": 1,
                    "unused_ratio": 1.0,
                    "estimated_tokens": 20,
                    "candidate_savings_tokens": 20,
                    "examples": ["Not reflected in the answer."],
                }
            ],
        }
    )

    assert "Prompts analyzed: 2" in html
    assert "UNUSED CONTEXT" in html
