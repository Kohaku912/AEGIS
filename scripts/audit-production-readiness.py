#!/usr/bin/env python3
"""Build the AEGIS production readiness report."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from audit_common import ROOT, parse_args, run_command, write_json


def check_file(path: str, name: str) -> dict[str, object]:
    exists = (ROOT / path).exists()
    return {
        "id": path.replace("/", "_"),
        "name": name,
        "status": "pass" if exists else "fail",
        "duration_ms": 0,
        "evidence": [path] if exists else [],
        "error": "" if exists else f"Missing {path}",
        "report_path": path if exists else "",
    }


def main() -> int:
    args = parse_args("Audit AEGIS production readiness")
    report_dir = Path(args.report_dir)
    start = time.time()
    checks: list[dict[str, object]] = []

    mock = run_command(["python", "scripts/audit-mocks.py", "--report-dir", str(report_dir), "--json-only"])
    checks.append({
        "id": "production_blocker_mock",
        "name": "production_blocker mock inventory",
        "status": mock["status"],
        "duration_ms": mock["duration_ms"],
        "evidence": [str(report_dir / "production_blockers.json")],
        "error": mock["stderr"] if mock["status"] != "pass" else "",
        "report_path": str(report_dir / "production_blockers.json"),
    })
    coverage = run_command(["python", "scripts/audit-capability-coverage.py", "--report-dir", str(report_dir), "--json-only"])
    checks.append({
        "id": "capability_coverage",
        "name": "Capability manifest coverage",
        "status": coverage["status"],
        "duration_ms": coverage["duration_ms"],
        "evidence": [str(report_dir / "capability_coverage.json")],
        "error": coverage["stderr"] if coverage["status"] != "pass" else "",
        "report_path": str(report_dir / "capability_coverage.json"),
    })
    run_command(["python", "scripts/audit-dead-code.py", "--report-dir", str(report_dir), "--json-only"])

    checks.extend([
        check_file("docker-compose.yml", "Docker Compose"),
        check_file("docs/ubuntu-production.md", "Ubuntu production runbook"),
        check_file("scripts/e2e/run-all-real.ps1", "Real E2E runner"),
        check_file("scripts/test-android-real.ps1", "Android real-device test runner"),
        check_file("scripts/pc/build-portable.ps1", "PC portable package script"),
    ])

    blockers: list[dict[str, object]] = []
    blocker_path = report_dir / "production_blockers.json"
    if blocker_path.exists():
        try:
            blockers = json.loads(blocker_path.read_text(encoding="utf-8")).get("blockers", [])
        except Exception as exc:
            blockers = [{"classification": "production_blocker", "reason": str(exc)}]

    status = "pass" if all(c["status"] == "pass" for c in checks) and not blockers else "fail"
    payload = {
        "overall_status": status,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_ms": int((time.time() - start) * 1000),
        "environment": {
            "runtime_mode": os.environ.get("AEGIS_RUNTIME_MODE", "development"),
            "cwd": str(ROOT),
        },
        "checks": checks,
        "blockers": blockers,
        "summary": {
            "production_blocker": len(blockers),
            "checks_total": len(checks),
            "checks_failed": sum(1 for c in checks if c["status"] != "pass"),
        },
    }
    write_json(report_dir / "readiness_summary.json", payload)
    latest = ROOT / "data" / "reports" / "e2e" / "latest"
    write_json(latest / "summary.json", payload)
    md = [
        "# AEGIS Production Readiness",
        "",
        f"- overall_status: {status}",
        f"- production_blocker: {len(blockers)}",
        f"- generated_at: {payload['generated_at']}",
        "",
        "| Status | Check | Error |",
        "|---|---|---|",
    ]
    for check in checks:
        md.append(f"| {check['status']} | {check['name']} | `{check.get('error', '')}` |")
    (latest / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"overall_status={status} production_blockers={len(blockers)}")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
