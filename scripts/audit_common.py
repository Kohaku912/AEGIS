#!/usr/bin/env python3
"""Shared audit helpers for AEGIS production readiness scripts."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "data" / "reports"
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "target",
    "build",
    ".gradle",
    ".idea",
    ".mypy_cache",
    "node_modules",
    "dist",
    "htmlcov",
    "logs",
    "packages",
}
DEFAULT_EXCLUDE_PARTS = {
    ("pc-server", "target"),
    ("browser-server", "data", "traces"),
    ("ai-server", "src", "generated"),
    ("dev-server", "src", "generated"),
    ("android-server", "app", "build"),
    ("data", "reports"),
}
TEXT_SUFFIXES = {
    ".py",
    ".rs",
    ".kt",
    ".kts",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".ps1",
    ".sh",
    ".toml",
    ".txt",
    ".nsi",
    ".service",
}


MOCK_PATTERNS = [
    ("mock", re.compile(r"\bmock\b|\[MOCK\]", re.IGNORECASE)),
    ("fake", re.compile(r"\bfake\b", re.IGNORECASE)),
    ("stub", re.compile(r"\bstub\b", re.IGNORECASE)),
    ("skeleton", re.compile(r"\bskeleton\b", re.IGNORECASE)),
    ("todo", re.compile(r"\bTODO\b")),
    ("fixme", re.compile(r"\bFIXME\b")),
    ("notimplemented", re.compile(r"NotImplemented|todo!\(|unimplemented!\(")),
    ("pass", re.compile(r"^\s*pass\s*(#.*)?$")),
    ("provider_mock", re.compile(r"provider\s*[:=]\s*[\"']?mock[\"']?", re.IGNORECASE)),
    ("deprecated", re.compile(r"\bdeprecated\b", re.IGNORECASE)),
    ("legacy", re.compile(r"\blegacy\b", re.IGNORECASE)),
]


@dataclass
class Finding:
    file: str
    line: int
    term: str
    classification: str
    reason: str
    text: str
    capability_id: str = ""

    def key(self) -> str:
        return f"{self.file}:{self.line}:{self.term}"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def should_skip(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    if any(part in DEFAULT_EXCLUDE_DIRS for part in parts):
        return True
    for excluded in DEFAULT_EXCLUDE_PARTS:
        if len(parts) >= len(excluded) and tuple(parts[: len(excluded)]) == excluded:
            return True
    return path.suffix.lower() not in TEXT_SUFFIXES


def iter_text_files(root: Path = ROOT) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and not should_skip(path):
            yield path


def read_overrides(report_dir: Path = REPORT_DIR) -> dict[str, str]:
    path = report_dir / "audit_overrides.json"
    try:
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            overrides: dict[str, str] = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    overrides[str(key)] = str(value.get("classification") or "")
                else:
                    overrides[str(key)] = str(value)
            return {k: v for k, v in overrides.items() if v}
    except Exception:
        return {}
    return {}


def infer_capability_id(path: str, text: str) -> str:
    match = re.search(r"([a-z0-9-]+\.[a-z0-9_-]+\.[a-z0-9_-]+)", text)
    if match:
        return match.group(1)
    if "/capabilities/" in path and path.endswith(".json"):
        try:
            data = json.loads((ROOT / path).read_text(encoding="utf-8"))
            return str(data.get("capability_id") or data.get("id") or "")
        except Exception:
            return ""
    return ""


def classify(path: str, term: str, text: str) -> tuple[str, str]:
    lower_path = path.lower()
    lower_text = text.lower()
    if "/tests/" in lower_path or lower_path.startswith("tests/") or "/test_" in lower_path:
        return "test_only", "test path"
    if "/tests/mocks/" in lower_path or "/testing/mocks/" in lower_path:
        return "test_only", "dedicated test mock path"
    if lower_path.startswith("scripts/audit") or lower_path.endswith("audit_common.py"):
        return "dev_only", "audit tooling"
    if lower_path.startswith("scripts/e2e/") or lower_path.startswith("scripts/pc/"):
        return "dev_only", "production validation or packaging tooling"
    if lower_path.startswith("docs/"):
        return "keep", "documentation reference"
    if lower_path.endswith(".md"):
        return "keep", "documentation reference"
    if "/generated/" in lower_path or lower_path.endswith("_pb2.py") or lower_path.endswith("_pb2_grpc.py"):
        return "keep", "generated code"
    if lower_path.startswith("ai-server/src/aegis_ai/voice/") and "_stub" in lower_path:
        return "production_blocker", "voice stub is not production implementation"
    if lower_path.startswith("ai-server/src/aegis_ai/integrations/") and lower_path.endswith("_stub.py"):
        return "production_blocker", "external integration stub"
    if "llm/providers/mock.py" in lower_path or "mockllmprovider" in lower_text:
        return "dev_only", "mock LLM provider is rejected by production output guard"
    if lower_path.endswith("tool_broker.py") and ("default mock executor" in lower_text or '"mock": true' in lower_text):
        return "dev_only", "ToolBroker mock executor is rejected by production output guard"
    if lower_path.startswith("pc-server/src/") and "[mock]" in lower_text:
        return "dev_only", "PC mock action output is rejected by production ToolBroker and real-action E2E"
    if "room" in lower_path and "provider" in lower_path and "mock" in lower_text:
        guard_path = ROOT / "room-server/src/aegis_room/providers.py"
        try:
            guarded = "not allowed when AEGIS_RUNTIME_MODE=production" in guard_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            guarded = False
        if guarded:
            return "dev_only", "Room mock provider is blocked at startup in production mode"
        return "production_blocker", "Room mock provider has no production startup guard"
    if term in {"todo", "fixme", "notimplemented"} and "/src/" in lower_path:
        return "production_blocker", "unfinished production source"
    if "deprecated" in lower_text or "legacy" in lower_text:
        return "obsolete", "deprecated/legacy marker"
    if term == "pass":
        return "keep", "empty branch may be intentional"
    return "dev_only", "non-production marker"


def scan_mock_findings(report_dir: Path = REPORT_DIR) -> list[Finding]:
    overrides = read_overrides(report_dir)
    findings: list[Finding] = []
    for path in iter_text_files():
        rel_path = rel(path)
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for idx, line in enumerate(lines, start=1):
            for term, pattern in MOCK_PATTERNS:
                if not pattern.search(line):
                    continue
                classification, reason = classify(rel_path, term, line)
                finding = Finding(
                    file=rel_path,
                    line=idx,
                    term=term,
                    classification=classification,
                    reason=reason,
                    text=line.strip()[:240],
                    capability_id=infer_capability_id(rel_path, line),
                )
                override = overrides.get(finding.key())
                if override:
                    finding.classification = override
                    finding.reason = "manual override"
                findings.append(finding)
    return findings


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_markdown(path: Path, title: str, findings: list[Finding]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.classification] = counts.get(finding.classification, 0) + 1
    lines = [f"# {title}", "", f"Generated at: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}", ""]
    lines.append("## Summary")
    for key in sorted(counts):
        lines.append(f"- {key}: {counts[key]}")
    lines.append("")
    lines.append("## Findings")
    lines.append("| Classification | File | Line | Term | Reason | Text |")
    lines.append("|---|---:|---:|---|---|---|")
    for finding in findings:
        text = finding.text.replace("|", "\\|")
        lines.append(
            f"| {finding.classification} | `{finding.file}` | {finding.line} | "
            f"{finding.term} | {finding.reason} | `{text}` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize(findings: list[Finding]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.classification] = counts.get(finding.classification, 0) + 1
    return counts


def run_command(command: list[str], cwd: Path = ROOT, timeout: int = 120) -> dict[str, object]:
    start = time.time()
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "status": "pass" if proc.returncode == 0 else "fail",
            "exit_code": proc.returncode,
            "duration_ms": int((time.time() - start) * 1000),
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
        }
    except Exception as exc:
        return {
            "command": command,
            "status": "fail",
            "exit_code": 1,
            "duration_ms": int((time.time() - start) * 1000),
            "stdout": "",
            "stderr": str(exc),
        }


def parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--report-dir", default=str(REPORT_DIR))
    parser.add_argument("--json-only", action="store_true")
    return parser.parse_args()


def asdicts(findings: list[Finding]) -> list[dict[str, object]]:
    return [asdict(finding) for finding in findings]
