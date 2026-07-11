#!/usr/bin/env python3
"""Audit capability manifests for production coverage signals."""

from __future__ import annotations

import json
from pathlib import Path

from audit_common import ROOT, parse_args, write_json


RISKY_LEVELS = {"medium", "high", "critical", "approval_required", "high_risk"}
ACTION_SERVERS = {"pc-server", "android-server", "browser-server"}
ACTION_CATEGORIES = {
    "general",
    "external_send",
    "physical_device",
    "workspace_file",
    "dev_operation",
    "notification",
    "personal_policy",
    "commitment_management",
    "hook_management",
    "draft_create",
    "delete",
}


def _risk(data: dict[str, object]) -> dict[str, object]:
    value = data.get("risk")
    return value if isinstance(value, dict) else {}


def _risk_level(data: dict[str, object]) -> str:
    return str(data.get("risk_level") or _risk(data).get("level") or "").strip().lower()


def _requires_approval(data: dict[str, object]) -> bool:
    return bool(data.get("requires_approval") or _risk(data).get("requires_approval"))


def _side_effects(data: dict[str, object]) -> list[object]:
    value = data.get("side_effects")
    if value is None:
        value = _risk(data).get("side_effects")
    return value if isinstance(value, list) else []


def _completion(data: dict[str, object]) -> dict[str, object]:
    value = data.get("completion") or data.get("verification") or data.get("postcondition")
    return value if isinstance(value, dict) else {}


def _completion_checks(data: dict[str, object]) -> list[object]:
    completion = _completion(data)
    checks = completion.get("checks") or completion.get("conditions")
    return checks if isinstance(checks, list) else []


def _enabled(data: dict[str, object]) -> bool:
    return bool(data.get("enabled", True))


def _issue(code: str, severity: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "message": message}


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
        operation_category = str(data.get("operation_category") or "").strip().lower()
        risk_level = _risk_level(data)
        requires_approval = _requires_approval(data)
        side_effects = _side_effects(data)
        checks = _completion_checks(data)
        has_completion = bool(checks)
        issues: list[dict[str, str]] = []
        if side_effects and not has_completion:
            issues.append(_issue(
                "side_effects_without_completion",
                "blocker",
                "Capability declares side effects but has no completion checks.",
            ))
        if server_id in ACTION_SERVERS and operation_category in ACTION_CATEGORIES and side_effects and not has_completion:
            issues.append(_issue(
                "operation_without_verification",
                "blocker",
                "PC/Android/Browser operation has side effects but no verification/completion checks.",
            ))
        if (requires_approval or risk_level in RISKY_LEVELS) and not has_completion:
            issues.append(_issue(
                "risky_without_postcondition",
                "blocker",
                "High-risk or approval-required capability lacks a postcondition.",
            ))
        if _enabled(data) and server_id == "room-server" and cap_id.startswith("room-server.light."):
            issues.append(_issue(
                "room_real_provider_unverified",
                "warning",
                "Room light capabilities require a real provider E2E result in production.",
            ))
        row = {
            "file": manifest_path.relative_to(ROOT).as_posix(),
            "capability_id": cap_id,
            "server_id": server_id,
            "app_id": app_id,
            "action": action,
            "status": "pass" if cap_id and server_id and app_id and action and not any(i["severity"] == "blocker" for i in issues) else "fail",
            "has_completion": has_completion,
            "completion_check_count": len(checks),
            "has_operation_category": bool(operation_category),
            "operation_category": operation_category,
            "requires_approval": requires_approval,
            "risk_level": risk_level,
            "side_effects": side_effects,
            "enabled": _enabled(data),
            "issues": issues,
        }
        rows.append(row)
    failing = [row for row in rows if row.get("status") != "pass"]
    payload = {
        "summary": {
            "total": len(rows),
            "failing": len(failing),
            "with_completion": sum(1 for row in rows if row.get("has_completion")),
            "issues": sum(len(row.get("issues") or []) for row in rows),
            "blocker_issues": sum(
                1
                for row in rows
                for issue in (row.get("issues") or [])
                if isinstance(issue, dict) and issue.get("severity") == "blocker"
            ),
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
        f"- blocker_issues: {payload['summary']['blocker_issues']}",
        "",
        "| Status | Capability | File | Risk | Completion | Issues |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        issue_text = ", ".join(
            str(issue.get("code"))
            for issue in (row.get("issues") or [])
            if isinstance(issue, dict)
        )
        md.append(
            f"| {row.get('status')} | `{row.get('capability_id')}` | `{row.get('file')}` | "
            f"{row.get('risk_level')} | {row.get('has_completion')} | {issue_text} |"
        )
    (report_dir / "capability_coverage.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(
        f"capabilities={len(rows)} failing={len(failing)} "
        f"blocker_issues={payload['summary']['blocker_issues']}"
    )
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
