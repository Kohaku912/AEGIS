#!/usr/bin/env python3
"""Audit AEGIS v1 completion gate inputs."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from audit_common import ROOT, parse_args, write_json


CHECKLIST = ROOT / "docs" / "v1-completion-checklist.md"
E2E_SUMMARY = ROOT / "data" / "reports" / "e2e" / "latest" / "summary.json"
UI_REPORT = ROOT / "data" / "reports" / "ui_completeness.json"
MOCK_REPORT = ROOT / "data" / "reports" / "production_blockers.json"
CAPABILITY_REPORT = ROOT / "data" / "reports" / "capability_coverage.json"


def _load_json(path: Path) -> dict[str, object]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def _check(check_id: str, name: str, status: str, evidence: list[str], error: str = "") -> dict[str, object]:
    return {
        "id": check_id,
        "name": name,
        "status": status,
        "duration_ms": 0,
        "evidence": evidence,
        "error": error,
        "report_path": evidence[0] if evidence else "",
    }


def _report_status(path: Path, ok_values: set[str] | None = None) -> tuple[str, str]:
    ok_values = ok_values or {"pass"}
    data = _load_json(path)
    if not data:
        return "fail", f"Missing or unreadable {path.relative_to(ROOT).as_posix()}"
    status = str(data.get("overall_status") or data.get("status") or "").lower()
    if status in ok_values:
        return "pass", ""
    return "fail", f"{path.relative_to(ROOT).as_posix()} status is {status or 'unknown'}"


def _checklist_counts() -> tuple[dict[str, int], list[str]]:
    text = CHECKLIST.read_text(encoding="utf-8") if CHECKLIST.exists() else ""
    v1_text = text.split("## Deferred After v1", 1)[0]
    counts = {
        "done": len(re.findall(r"^- \[x\]", v1_text, flags=re.MULTILINE | re.IGNORECASE)),
        "partial": len(re.findall(r"^- \[~\]", v1_text, flags=re.MULTILINE)),
        "open": len(re.findall(r"^- \[ \]", v1_text, flags=re.MULTILINE)),
        "blocker": len(re.findall(r"^- \[!\]", v1_text, flags=re.MULTILINE)),
    }
    return counts, re.findall(r"^##\s+(.+)$", v1_text, flags=re.MULTILINE)


def _required_e2e() -> dict[str, object]:
    summary = _load_json(E2E_SUMMARY)
    checks = summary.get("checks") if isinstance(summary.get("checks"), list) else []
    required = {
        "docker_core",
        "manager_e2e",
        "pc_real",
        "android_real",
        "browser_real",
        "dev_real",
    }
    present = {
        str(item.get("id")): str(item.get("status") or "fail")
        for item in checks
        if isinstance(item, dict) and item.get("id")
    }
    missing = sorted(required - set(present))
    failed = sorted(check_id for check_id in required if present.get(check_id) not in {None, "pass"})
    return {"present": present, "missing": missing, "failed": failed, "ok": not missing and not failed}


def main() -> int:
    args = parse_args("Audit AEGIS v1 completion")
    report_dir = Path(args.report_dir)
    start = time.time()
    checks: list[dict[str, object]] = []

    counts, sections = _checklist_counts()
    checklist_ok = CHECKLIST.exists() and counts["open"] == 0 and counts["partial"] == 0 and counts["blocker"] == 0
    checks.append(_check(
        "v1_checklist_closed",
        "v1 completion checklist is fully closed",
        "pass" if checklist_ok else "fail",
        [CHECKLIST.relative_to(ROOT).as_posix()],
        "" if checklist_ok else f"open={counts['open']} partial={counts['partial']} blocker={counts['blocker']}",
    ))

    ui_status, ui_error = _report_status(UI_REPORT)
    checks.append(_check("ui_completeness", "UI completeness audit", ui_status, [UI_REPORT.relative_to(ROOT).as_posix()], ui_error))
    cap_status, cap_error = _report_status(CAPABILITY_REPORT)
    checks.append(_check("capability_coverage", "Capability coverage audit", cap_status, [CAPABILITY_REPORT.relative_to(ROOT).as_posix()], cap_error))

    mock = _load_json(MOCK_REPORT)
    blockers = mock.get("blockers") if isinstance(mock.get("blockers"), list) else []
    checks.append(_check(
        "production_blocker_mock_zero",
        "Production blocker mock/stub count is zero",
        "pass" if not blockers else "fail",
        [MOCK_REPORT.relative_to(ROOT).as_posix()],
        "" if not blockers else f"production_blockers={len(blockers)}",
    ))

    e2e = _required_e2e()
    checks.append(_check(
        "required_real_e2e",
        "Required real E2E checks are present and passing",
        "pass" if e2e["ok"] else "fail",
        [E2E_SUMMARY.relative_to(ROOT).as_posix()],
        "" if e2e["ok"] else f"missing={e2e['missing']} failed={e2e['failed']}",
    ))

    overall = "pass" if all(check["status"] == "pass" for check in checks) else "fail"
    payload = {
        "schema_version": "aegis-v1-completion.v1",
        "overall_status": overall,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_ms": int((time.time() - start) * 1000),
        "checklist": {
            "path": CHECKLIST.relative_to(ROOT).as_posix(),
            "counts": counts,
            "sections": sections,
        },
        "checks": checks,
        "summary": {
            "checks_total": len(checks),
            "checks_failed": sum(1 for check in checks if check["status"] != "pass"),
            "open_checkboxes": counts["open"],
            "partial_checkboxes": counts["partial"],
            "blocker_checkboxes": counts["blocker"],
        },
    }
    write_json(report_dir / "v1_completion.json", payload)
    lines = [
        "# AEGIS v1 Completion Audit",
        "",
        f"- overall_status: `{overall}`",
        f"- open_checkboxes: {counts['open']}",
        f"- partial_checkboxes: {counts['partial']}",
        f"- blocker_checkboxes: {counts['blocker']}",
        "",
        "| Status | Check | Error |",
        "|---|---|---|",
    ]
    for check in checks:
        lines.append(f"| {check['status']} | {check['name']} | `{check.get('error', '')}` |")
    (report_dir / "v1_completion.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"overall_status={overall} open={counts['open']} "
        f"partial={counts['partial']} blockers={counts['blocker']}"
    )
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
