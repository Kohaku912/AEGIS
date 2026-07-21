#!/usr/bin/env python3
"""Audit tracked source and built static assets for committed secrets."""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

from audit_common import ROOT, parse_args, write_json

STATIC_ROOTS = [
    ROOT / "ai-server" / "src" / "aegis_ai" / "web" / "static",
]

BASE_SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
    ("openai_compatible_key", re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b")),
    ("github_token", re.compile(r"\bghp_[A-Za-z0-9_]{30,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
]

ALLOW_TEXT = (
    "sk-your",
    "sk-redacted",
    "sk-test",
    "sk-example",
    "example",
    "placeholder",
    "[REDACTED]",
)

ALLOW_PATH_PARTS = (
    "tests",
    "test_",
    "README.md",
    "docs/testing-real-devices.md",
)


def _patterns_from_local_notes(notes: str) -> list[tuple[str, re.Pattern[str]]]:
    """Build exact-match patterns from ignored local infrastructure notes."""
    secrets: set[str] = set()
    for line in notes.splitlines():
        if not re.search(r"password|passphrase|secret|token", line, flags=re.IGNORECASE):
            continue
        for match in re.finditer(r"`([^`]+)`", line):
            value = match.group(1).strip()
            if len(value) >= 6 and not re.search(r"\s|[/\\:]", value):
                secrets.add(value)
    return [
        ("known_local_secret", re.compile(rf"(?<![A-Za-z0-9_]){re.escape(value)}(?![A-Za-z0-9_])"))
        for value in sorted(secrets)
    ]


def _secret_patterns() -> list[tuple[str, re.Pattern[str]]]:
    notes_path = ROOT / ".aegis-local" / "infra_access.md"
    try:
        local = _patterns_from_local_notes(notes_path.read_text(encoding="utf-8"))
    except OSError:
        local = []
    return [*BASE_SECRET_PATTERNS, *local]


def _tracked_files() -> list[Path]:
    try:
        out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True, encoding="utf-8", errors="ignore")
    except Exception:
        return []
    return [ROOT / line.strip() for line in out.splitlines() if line.strip()]


def _static_files() -> list[Path]:
    files: list[Path] = []
    for root in STATIC_ROOTS:
        if root.exists():
            files.extend(path for path in root.rglob("*") if path.is_file())
    return files


def _is_allowed(path: Path, line: str) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    lowered = line.lower()
    if any(marker.lower() in lowered for marker in ALLOW_TEXT):
        return True
    return any(part in rel for part in ALLOW_PATH_PARTS)


def _scan_file(
    path: Path,
    patterns: list[tuple[str, re.Pattern[str]]] | None = None,
) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings
    rel = path.relative_to(ROOT).as_posix()
    patterns = patterns or _secret_patterns()
    for line_no, line in enumerate(text.splitlines(), start=1):
        for pattern_id, pattern in patterns:
            if not pattern.search(line):
                continue
            if _is_allowed(path, line):
                continue
            findings.append({
                "path": rel,
                "line": line_no,
                "pattern": pattern_id,
                "preview": pattern.sub("[SECRET]", line.strip())[:220],
                "classification": "production_blocker",
            })
    return findings


def main() -> int:
    args = parse_args("Audit tracked source/static assets for committed secrets")
    report_dir = Path(args.report_dir)
    start = time.time()
    seen: set[Path] = set()
    files = []
    for path in [*_tracked_files(), *_static_files()]:
        if path in seen or not path.exists() or path.is_dir():
            continue
        seen.add(path)
        files.append(path)

    findings: list[dict[str, object]] = []
    patterns = _secret_patterns()
    for path in files:
        if ".aegis-local" in path.parts or "data" in path.relative_to(ROOT).parts:
            continue
        findings.extend(_scan_file(path, patterns))

    status = "pass" if not findings else "fail"
    payload = {
        "schema_version": "aegis-secret-audit.v1",
        "status": status,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_ms": int((time.time() - start) * 1000),
        "files_scanned": len(files),
        "findings": findings,
        "summary": {
            "production_blocker": len(findings),
        },
    }
    write_json(report_dir / "secret_inventory.json", payload)
    lines = [
        "# AEGIS Secret Inventory",
        "",
        f"- status: `{status}`",
        f"- files_scanned: {len(files)}",
        f"- production_blocker: {len(findings)}",
        "",
        "| Classification | Pattern | Location | Preview |",
        "|---|---|---|---|",
    ]
    for finding in findings:
        location = f"{finding['path']}:{finding['line']}"
        preview = str(finding["preview"]).replace("|", "\\|")
        lines.append(f"| {finding['classification']} | {finding['pattern']} | `{location}` | `{preview}` |")
    (report_dir / "secret_inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"status={status} production_blockers={len(findings)}")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
