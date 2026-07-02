"""Prompt usage analysis for recent LLM audit records."""

from __future__ import annotations

import argparse
import html
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aegis_ai.llm.json_utils import extract_json_object


LLM_ACTIONS = {"llm_call", "llm_tool_call", "llm_vision_call"}


@dataclass
class PromptSection:
    section_id: str
    title: str
    text: str
    estimated_tokens: int


class PromptUsageAnalyzer:
    """Analyze prompt sections that appear unused by the model response."""

    def __init__(self, *, audit_manager: Any = None, llm_provider: Any = None) -> None:
        self._audit_manager = audit_manager
        self._llm = llm_provider

    def analyze(
        self,
        *,
        hours: int = 24,
        max_prompts: int = 20,
        max_sections_per_prompt: int = 14,
        entries: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        audit_entries = entries if entries is not None else self._load_entries()
        cutoff_ms = int(time.time() * 1000) - max(1, hours) * 3_600_000
        records = [
            self._record_from_entry(entry)
            for entry in audit_entries
            if int(entry.get("timestamp_ms") or 0) >= cutoff_ms
            and entry.get("action") in LLM_ACTIONS
            and isinstance(entry.get("detail"), dict)
            and entry["detail"].get("prompt_preview")
        ]
        records = [record for record in records if record is not None]
        records.sort(key=lambda item: item["timestamp_ms"], reverse=True)
        sampled = records[: max(1, max_prompts)]

        analyzed_records: list[dict[str, Any]] = []
        section_totals: dict[str, dict[str, Any]] = {}
        errors: list[str] = []
        for record in sampled:
            sections = self._split_sections(record["prompt"])[:max_sections_per_prompt]
            judgement = self._judge_record(record, sections)
            if judgement.get("error"):
                errors.append(judgement["error"])
            section_results = judgement.get("sections", [])
            section_by_id = {
                str(item.get("section_id") or ""): item
                for item in section_results
                if isinstance(item, dict)
            }
            rendered_sections = []
            for section in sections:
                result = section_by_id.get(section.section_id) or {
                    "section_id": section.section_id,
                    "usage": "unclear",
                    "confidence": 0.0,
                    "evidence": "LLM analysis unavailable for this section.",
                    "suggestion": "Keep until a valid analysis is available.",
                }
                rendered = {
                    "section_id": section.section_id,
                    "title": section.title,
                    "estimated_tokens": section.estimated_tokens,
                    "usage": str(result.get("usage") or "unclear"),
                    "confidence": _bounded_float(result.get("confidence")),
                    "evidence": str(result.get("evidence") or "")[:500],
                    "suggestion": str(result.get("suggestion") or "")[:500],
                }
                rendered_sections.append(rendered)
                bucket = section_totals.setdefault(
                    section.title,
                    {
                        "title": section.title,
                        "estimated_tokens": 0,
                        "count": 0,
                        "unused": 0,
                        "partial": 0,
                        "used": 0,
                        "unclear": 0,
                        "examples": [],
                    },
                )
                bucket["estimated_tokens"] += section.estimated_tokens
                bucket["count"] += 1
                usage = rendered["usage"]
                if usage == "unused":
                    bucket["unused"] += 1
                elif usage in {"partially_used", "partial"}:
                    bucket["partial"] += 1
                elif usage == "used":
                    bucket["used"] += 1
                else:
                    bucket["unclear"] += 1
                if len(bucket["examples"]) < 3:
                    bucket["examples"].append(rendered["evidence"] or rendered["suggestion"])
            analyzed_records.append({
                "entry_id": record["entry_id"],
                "timestamp_ms": record["timestamp_ms"],
                "action": record["action"],
                "model": record["model"],
                "tokens": record["tokens"],
                "prompt_chars": len(record["prompt"]),
                "estimated_prompt_tokens": _estimate_tokens(record["prompt"]),
                "sections": rendered_sections,
            })

        section_summary = list(section_totals.values())
        for item in section_summary:
            item["unused_ratio"] = round(item["unused"] / item["count"], 3) if item["count"] else 0.0
            item["candidate_savings_tokens"] = item["estimated_tokens"] if item["unused_ratio"] >= 0.5 else 0
        section_summary.sort(key=lambda item: (item["candidate_savings_tokens"], item["unused_ratio"]), reverse=True)

        total_prompt_chars = sum(len(record["prompt"]) for record in sampled)
        total_prompt_tokens = sum(_estimate_tokens(record["prompt"]) for record in sampled)
        return {
            "generated_at_ms": int(time.time() * 1000),
            "hours": hours,
            "entries_considered": len(records),
            "prompts_analyzed": len(sampled),
            "total_prompt_chars": total_prompt_chars,
            "estimated_prompt_tokens": total_prompt_tokens,
            "candidate_savings_tokens": sum(item["candidate_savings_tokens"] for item in section_summary),
            "analysis_status": "ok" if self._llm is not None and not errors else "partial",
            "errors": errors,
            "section_summary": section_summary,
            "records": analyzed_records,
        }

    def write_report(self, report: dict[str, Any], *, json_path: str | Path | None = None, html_path: str | Path | None = None) -> None:
        if json_path:
            path = Path(json_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        if html_path:
            path = Path(html_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render_html_report(report), encoding="utf-8")

    def _load_entries(self) -> list[dict[str, Any]]:
        if self._audit_manager is None:
            return []
        if hasattr(self._audit_manager, "read_recent_for_dashboard"):
            return self._audit_manager.read_recent_for_dashboard(max_entries=10000)
        if hasattr(self._audit_manager, "list_recent"):
            return self._audit_manager.list_recent(limit=10000).get("entries", [])
        return []

    def _record_from_entry(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        detail = entry.get("detail")
        if not isinstance(detail, dict):
            return None
        prompt = str(detail.get("prompt_preview") or "")
        if not prompt:
            return None
        return {
            "entry_id": str(entry.get("entry_id") or ""),
            "timestamp_ms": int(entry.get("timestamp_ms") or 0),
            "action": str(entry.get("action") or ""),
            "model": str(detail.get("model") or entry.get("model") or ""),
            "tokens": int(detail.get("tokens") or entry.get("tokens_used") or 0),
            "prompt": prompt,
            "response": str(detail.get("response_preview") or ""),
            "tool_calls": detail.get("tool_calls") or [],
            "context_meta": {
                key: value
                for key, value in detail.items()
                if key not in {"prompt_preview", "response_preview", "tool_calls"}
            },
        }

    def _split_sections(self, prompt: str) -> list[PromptSection]:
        lines = prompt.splitlines()
        sections: list[tuple[str, list[str]]] = []
        current_title = "Preamble"
        current_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if _looks_like_heading(stripped) and current_lines:
                sections.append((current_title, current_lines))
                current_title = stripped.rstrip(":")
                current_lines = []
            elif _looks_like_heading(stripped) and not current_lines:
                current_title = stripped.rstrip(":")
            else:
                current_lines.append(line)
        if current_lines:
            sections.append((current_title, current_lines))
        result: list[PromptSection] = []
        for idx, (title, chunk_lines) in enumerate(sections):
            text = "\n".join(chunk_lines).strip()
            if not text:
                continue
            result.append(PromptSection(
                section_id=f"s{idx + 1}",
                title=title[:80],
                text=text,
                estimated_tokens=_estimate_tokens(text),
            ))
        return result or [PromptSection("s1", "Prompt", prompt, _estimate_tokens(prompt))]

    def _judge_record(self, record: dict[str, Any], sections: list[PromptSection]) -> dict[str, Any]:
        if self._llm is None or not hasattr(self._llm, "generate"):
            return {"error": "LLM provider unavailable", "sections": []}
        payload = {
            "instruction": (
                "For each prompt section, decide whether the assistant response or tool choice appears to use it. "
                "Return JSON only: {\"sections\":[{\"section_id\":\"s1\",\"usage\":\"used|partially_used|unused|unclear\","
                "\"confidence\":0.0,\"evidence\":\"...\",\"suggestion\":\"...\"}]}. "
                "Do not mark a section used just because it exists; require evidence in the response or tool calls."
            ),
            "action": record["action"],
            "model": record["model"],
            "response": record["response"][:3000],
            "tool_calls": record["tool_calls"],
            "sections": [
                {
                    "section_id": section.section_id,
                    "title": section.title,
                    "estimated_tokens": section.estimated_tokens,
                    "text": section.text[:1500],
                }
                for section in sections
            ],
        }
        prompt = json.dumps(payload, ensure_ascii=False)
        try:
            response = self._llm.generate(
                prompt=prompt,
                system_prompt="You analyze prompt section usefulness. Return compact JSON only.",
                max_tokens=1200,
                temperature=0.0,
                json_mode=True,
                profile="decision",
                context_meta={"caller": "prompt_usage_analyzer"},
            )
        except TypeError:
            response = self._llm.generate(
                prompt=prompt,
                system_prompt="You analyze prompt section usefulness. Return compact JSON only.",
                max_tokens=1200,
                temperature=0.0,
            )
        if not getattr(response, "success", False):
            return {"error": str(getattr(response, "error", "") or "LLM analysis failed"), "sections": []}
        data = extract_json_object(getattr(response, "content", "") or "")
        sections_data = data.get("sections")
        if not isinstance(sections_data, list):
            return {"error": "LLM analysis returned no sections", "sections": []}
        return {"sections": sections_data}


def render_html_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report.get("section_summary", []):
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('title', '')))}</td>"
            f"<td>{item.get('count', 0)}</td>"
            f"<td>{item.get('unused', 0)}</td>"
            f"<td>{item.get('unused_ratio', 0)}</td>"
            f"<td>{item.get('estimated_tokens', 0)}</td>"
            f"<td>{item.get('candidate_savings_tokens', 0)}</td>"
            f"<td>{html.escape('; '.join(str(x) for x in item.get('examples', []) if x))}</td>"
            "</tr>"
        )
    rows_html = "\n".join(rows)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>AEGIS Prompt Usage</title>
<style>body{{font-family:system-ui,sans-serif;background:#0b1020;color:#e5e7eb;margin:24px}}
table{{border-collapse:collapse;width:100%;background:#111827}}th,td{{border:1px solid #374151;padding:8px;vertical-align:top}}
th{{background:#1f2937}}.metric{{display:inline-block;margin:0 12px 16px 0;padding:10px 12px;background:#111827;border:1px solid #374151;border-radius:8px}}</style>
</head><body>
<h1>AEGIS Prompt Usage Report</h1>
<div class="metric">Prompts analyzed: {report.get("prompts_analyzed", 0)}</div>
<div class="metric">Estimated prompt tokens: {report.get("estimated_prompt_tokens", 0)}</div>
<div class="metric">Candidate savings: {report.get("candidate_savings_tokens", 0)}</div>
<div class="metric">Status: {html.escape(str(report.get("analysis_status", "")))}</div>
<table><thead><tr><th>Section</th><th>Count</th><th>Unused</th><th>Unused ratio</th><th>Tokens</th><th>Candidate savings</th><th>Evidence / Suggestion</th></tr></thead>
<tbody>{rows_html}</tbody></table>
</body></html>"""


def _looks_like_heading(line: str) -> bool:
    if not line or len(line) > 90:
        return False
    if line.endswith(":") and sum(ch.isalpha() for ch in line) >= 3:
        return True
    letters = [ch for ch in line if ch.isalpha()]
    return bool(letters) and len(letters) >= 4 and line.upper() == line


def _estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def _bounded_float(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _build_runtime_analyzer() -> PromptUsageAnalyzer:
    from aegis_ai.runtime import get_runtime

    runtime = get_runtime()
    return PromptUsageAnalyzer(audit_manager=runtime.audit_manager, llm_provider=runtime.llm_gateway)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze recent AEGIS LLM prompt section usage.")
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--max-prompts", type=int, default=20)
    parser.add_argument("--json", dest="json_path", default="data/reports/prompt_usage_latest.json")
    parser.add_argument("--html", dest="html_path", default="data/reports/prompt_usage_latest.html")
    args = parser.parse_args(argv)

    analyzer = _build_runtime_analyzer()
    report = analyzer.analyze(hours=args.hours, max_prompts=args.max_prompts)
    analyzer.write_report(report, json_path=args.json_path, html_path=args.html_path)
    print(json.dumps({
        "ok": True,
        "json": args.json_path,
        "html": args.html_path,
        "prompts_analyzed": report.get("prompts_analyzed", 0),
        "candidate_savings_tokens": report.get("candidate_savings_tokens", 0),
        "status": report.get("analysis_status"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
