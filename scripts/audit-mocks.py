#!/usr/bin/env python3
"""Audit mock/stub/skeleton markers across AEGIS."""

from __future__ import annotations

from pathlib import Path

from audit_common import asdicts, parse_args, scan_mock_findings, summarize, write_json, write_markdown


def main() -> int:
    args = parse_args("Audit mock/stub/skeleton markers")
    report_dir = Path(args.report_dir)
    findings = scan_mock_findings(report_dir)
    blockers = [f for f in findings if f.classification == "production_blocker"]
    payload = {
        "summary": summarize(findings),
        "findings": asdicts(findings),
        "blockers": asdicts(blockers),
    }
    write_json(report_dir / "mock_inventory.json", payload)
    write_json(report_dir / "production_blockers.json", {"summary": summarize(blockers), "blockers": asdicts(blockers)})
    if not args.json_only:
        write_markdown(report_dir / "mock_inventory.md", "AEGIS Mock Inventory", findings)
        write_markdown(report_dir / "production_blockers.md", "AEGIS Production Blockers", blockers)
    print(f"mock findings={len(findings)} production_blockers={len(blockers)}")
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
