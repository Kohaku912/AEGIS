#!/usr/bin/env python3
"""Audit mock/stub/skeleton markers across AEGIS."""

from __future__ import annotations

from pathlib import Path

from audit_common import asdicts, parse_args, scan_mock_findings, summarize, write_json, write_markdown


def main() -> int:
    args = parse_args("Audit mock/stub/skeleton markers")
    report_dir = Path(args.report_dir)
    findings, files_scanned = scan_mock_findings(report_dir)
    blockers = [f for f in findings if f.classification == "production_blocker"]

    # "No blockers" is only clean if something was actually read. A scan that walked
    # no files produces no findings either, and the two must not share a verdict.
    status = "pass" if files_scanned and not blockers else "fail"
    if not files_scanned:
        error = "no files were walked -- an empty scan is not a clean inventory"
    elif blockers:
        error = f"production_blockers={len(blockers)}"
    else:
        error = ""

    payload = {
        "schema_version": "aegis-mock-inventory.v1",
        "status": status,
        "files_scanned": files_scanned,
        "error": error,
        "summary": summarize(findings),
        "findings": asdicts(findings),
        "blockers": asdicts(blockers),
    }
    write_json(report_dir / "mock_inventory.json", payload)
    write_json(
        report_dir / "production_blockers.json",
        {
            "status": status,
            "files_scanned": files_scanned,
            "error": error,
            "summary": summarize(blockers),
            "blockers": asdicts(blockers),
        },
    )
    if not args.json_only:
        write_markdown(report_dir / "mock_inventory.md", "AEGIS Mock Inventory", findings)
        write_markdown(report_dir / "production_blockers.md", "AEGIS Production Blockers", blockers)
    print(
        f"status={status} mock findings={len(findings)} production_blockers={len(blockers)} "
        f"files_scanned={files_scanned}"
        + (f" error={error}" if error else "")
    )
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
