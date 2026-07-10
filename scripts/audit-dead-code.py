#!/usr/bin/env python3
"""Find obvious dead/obsolete AEGIS files without deleting them."""

from __future__ import annotations

from pathlib import Path

from audit_common import ROOT, parse_args, run_command, write_json, write_markdown, Finding


DEAD_FILE_NAMES = {
    "tmp_audit.py",
    "tmp_audit2.py",
    "tmp_audit3.py",
    "debug_out.txt",
    "debug_err.txt",
}


def classify_file(path: Path) -> Finding | None:
    rel_path = path.relative_to(ROOT).as_posix()
    name = path.name.lower()
    if name in DEAD_FILE_NAMES or name.startswith("debug_"):
        return Finding(rel_path, 0, "dead_file", "dead", "temporary/debug artifact", "")
    if name.startswith("test_") and path.parent == ROOT:
        return Finding(rel_path, 0, "root_test", "obsolete", "root-level ad-hoc test", "")
    if "legacy" in name and path.suffix == ".py":
        return Finding(rel_path, 0, "legacy_file", "obsolete", "legacy compatibility shell candidate", "")
    return None


def main() -> int:
    args = parse_args("Audit dead/obsolete code candidates")
    report_dir = Path(args.report_dir)
    findings: list[Finding] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", "target", "__pycache__"} for part in path.relative_to(ROOT).parts):
            continue
        finding = classify_file(path)
        if finding:
            findings.append(finding)

    for finding in list(findings):
        if finding.classification not in {"dead", "obsolete"}:
            continue
        refs = run_command(["rg", "-n", "--fixed-strings", Path(finding.file).name, "."], timeout=20)
        finding.text = str(refs.get("stdout") or "")[:240]

    payload = {"summary": {"dead_or_obsolete": len(findings)}, "findings": [f.__dict__ for f in findings]}
    write_json(report_dir / "dead_code_report.json", payload)
    if not args.json_only:
        write_markdown(report_dir / "dead_code_report.md", "AEGIS Dead Code Report", findings)
    print(f"dead_or_obsolete={len(findings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
