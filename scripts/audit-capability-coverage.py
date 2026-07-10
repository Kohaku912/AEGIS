#!/usr/bin/env python3
"""Audit capability manifests for production coverage signals."""

from __future__ import annotations

import json
from pathlib import Path

from audit_common import ROOT, parse_args, write_json


def main() -> int:
    args = parse_args("Audit capability manifest coverage")
    report_dir = Path(args.report_dir)
    capability_root = ROOT / "ai-server" / "capabilities"
    rows: list[dict[str, object]] = []
    for manifest_path in sorted(capability_root.rglob("*.json")):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({
                "file": manifest_path.relative_to(ROOT).as_posix(),
                "status": "fail",
                "error": str(exc),
            })
            continue
        parts = manifest_path.relative_to(capability_root).parts
        server_id = str(data.get("server_id") or (parts[1] if len(parts) > 3 else ""))
        app_id = str(data.get("app_id") or (parts[2] if len(parts) > 3 else ""))
        action = str(data.get("action") or manifest_path.stem)
        cap_id = str(data.get("capability_id") or data.get("id") or f"{server_id}.{app_id}.{action}")
        operation_category = str(data.get("operation_category") or "")
        rows.append({
            "file": manifest_path.relative_to(ROOT).as_posix(),
            "capability_id": cap_id,
            "server_id": server_id,
            "status": "pass" if cap_id and server_id and app_id and action else "fail",
            "has_completion": bool((data.get("completion") or {}).get("checks")),
            "has_operation_category": bool(operation_category),
            "requires_approval": bool(data.get("requires_approval")),
            "risk_level": data.get("risk_level") or data.get("risk", {}).get("level"),
        })
    failing = [row for row in rows if row.get("status") != "pass"]
    payload = {
        "summary": {
            "total": len(rows),
            "failing": len(failing),
            "with_completion": sum(1 for row in rows if row.get("has_completion")),
        },
        "capabilities": rows,
    }
    write_json(report_dir / "capability_coverage.json", payload)
    md = [
        "# AEGIS Capability Coverage",
        "",
        f"- total: {payload['summary']['total']}",
        f"- failing: {payload['summary']['failing']}",
        f"- with_completion: {payload['summary']['with_completion']}",
        "",
        "| Status | Capability | File | Risk | Completion |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        md.append(
            f"| {row.get('status')} | `{row.get('capability_id')}` | `{row.get('file')}` | "
            f"{row.get('risk_level')} | {row.get('has_completion')} |"
        )
    (report_dir / "capability_coverage.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"capabilities={len(rows)} failing={len(failing)}")
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
