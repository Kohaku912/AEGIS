#!/usr/bin/env python3
"""Find obvious dead/obsolete AEGIS files without deleting them."""

from __future__ import annotations

from pathlib import Path

from audit_common import ROOT, Finding, parse_args, run_command, write_json, write_markdown

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


def reference_lookup_text(refs: dict[str, object]) -> tuple[str, bool]:
    """Render a reference-search result, keeping "could not search" apart from "no match".

    ``rg`` exits 1 when it finds nothing, and ``run_command`` reports that as
    ``status="fail"`` -- the same status it uses when the binary could not be launched at
    all. Rendering both as an empty string makes a blank reference cell read as the
    strongest possible dead-code claim ("nothing references this file") when in fact
    nothing was searched. The three outcomes therefore get three distinct renderings, and
    the boolean says whether a search actually ran.
    """
    if refs.get("status") == "pass":
        text = str(refs.get("stdout") or "").strip()
        return (text[:240] if text else "<no references found>"), True
    if refs.get("exit_code") == 1 and not str(refs.get("stderr") or "").strip():
        # rg's documented "no match" exit code, with nothing on stderr: a real empty result.
        return "<no references found>", True
    lines = str(refs.get("stderr") or "").strip().splitlines()
    reason = lines[0] if lines else f"exit_code={refs.get('exit_code')}"
    return f"<reference search could not run: {reason}>"[:240], False


def main() -> int:
    args = parse_args("Audit dead/obsolete code candidates")
    report_dir = Path(args.report_dir)
    findings: list[Finding] = []
    files_walked = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", "target", "__pycache__"} for part in path.relative_to(ROOT).parts):
            continue
        files_walked += 1
        finding = classify_file(path)
        if finding:
            findings.append(finding)

    reference_search_failures = 0
    for finding in list(findings):
        if finding.classification not in {"dead", "obsolete"}:
            continue
        refs = run_command(["rg", "-n", "--fixed-strings", Path(finding.file).name, "."], timeout=20)
        finding.text, ran = reference_lookup_text(refs)
        if not ran:
            reference_search_failures += 1

    # "No dead files" is only clean if a tree was actually walked. A walk over an empty tree
    # produces no findings either, and the two must not share a verdict -- the rule the
    # mock/secret/capability audits already carry. The reference-search failure count travels
    # with the findings so a reader can tell a blank reference from a failed search.
    status = "pass" if files_walked else "fail"
    payload = {
        "status": status,
        "files_walked": files_walked,
        "reference_search_failures": reference_search_failures,
        "summary": {"dead_or_obsolete": len(findings)},
        "findings": [f.__dict__ for f in findings],
    }
    write_json(report_dir / "dead_code_report.json", payload)
    if not args.json_only:
        write_markdown(report_dir / "dead_code_report.md", "AEGIS Dead Code Report", findings)
    print(
        f"dead_or_obsolete={len(findings)} files_walked={files_walked} "
        f"reference_search_failures={reference_search_failures}"
    )
    if not files_walked:
        print("no files were walked -- an empty tree is not a clean dead-code audit")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
