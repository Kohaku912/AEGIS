#!/usr/bin/env python3
"""Build the AEGIS production readiness report."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from audit_common import ROOT, parse_args, run_command, write_json


def _check(
    check_id: str,
    name: str,
    status: str,
    evidence: list[str] | None = None,
    error: str = "",
    report_path: str = "",
    duration_ms: int = 0,
) -> dict[str, object]:
    return {
        "id": check_id,
        "name": name,
        "status": status,
        "duration_ms": duration_ms,
        "evidence": evidence or [],
        "error": error,
        "report_path": report_path,
    }


def check_file(path: str, name: str) -> dict[str, object]:
    exists = (ROOT / path).exists()
    return _check(
        path.replace("/", "_"),
        name,
        "pass" if exists else "fail",
        [path] if exists else [],
        "" if exists else f"Missing {path}",
        path if exists else "",
    )


def _load_json(path: Path) -> dict[str, object]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def _e2e_check(report_dir: Path, check_id: str, name: str, required: bool = True) -> dict[str, object]:
    summary = _load_json(ROOT / "data" / "reports" / "e2e" / "latest" / "summary.json")
    checks = summary.get("checks") if isinstance(summary.get("checks"), list) else []
    match = next((c for c in checks if isinstance(c, dict) and c.get("id") == check_id), None)
    for candidate in (
        ROOT / "data" / "reports" / "e2e" / "latest" / f"{check_id.replace('_', '-')}.json",
        ROOT / "data" / "reports" / "e2e" / "latest" / f"{check_id}.json",
    ):
        loaded = _load_json(candidate)
        if loaded.get("id") == check_id:
            match = loaded
            break
    if not match:
        return _check(
            check_id,
            name,
            "fail" if required else "warn",
            [str(ROOT / "data/reports/e2e/latest/summary.json")],
            f"Missing E2E result for {check_id}",
        )
    status = str(match.get("status") or "fail")
    return _check(
        check_id,
        name,
        "pass" if status == "pass" else "fail",
        [str(match.get("report_path") or ROOT / "data/reports/e2e/latest/summary.json")],
        str(match.get("error") or "") if status != "pass" else "",
        str(match.get("report_path") or ""),
        int(match.get("duration_ms") or 0),
    )


def _docker_bind_check() -> dict[str, object]:
    compose = ROOT / "docker-compose.yml"
    production = ROOT / "docker-compose.production.yml"
    evidence = [str(compose.relative_to(ROOT))]
    if production.exists():
        evidence.append(str(production.relative_to(ROOT)))
    text = compose.read_text(encoding="utf-8", errors="ignore") if compose.exists() else ""
    if '"0.0.0.0:' in text or "'0.0.0.0:" in text:
        return _check(
            "docker_bind_scope",
            "Production Docker bind scope",
            "fail",
            evidence,
            "docker-compose.yml contains hard-coded 0.0.0.0 port bindings.",
        )
    production_text = production.read_text(encoding="utf-8", errors="ignore") if production.exists() else ""
    combined = f"{text}\n{production_text}"
    if "AEGIS_PRODUCTION_BIND_HOST" not in combined and "AEGIS_BIND_HOST" not in combined:
        return _check(
            "docker_bind_scope",
            "Production Docker bind scope",
            "fail",
            evidence,
            "No production bind host control found.",
        )
    if "127.0.0.1" not in combined:
        return _check(
            "docker_bind_scope",
            "Production Docker bind scope",
            "fail",
            evidence,
            "docker-compose.production.yml does not default production bindings to 127.0.0.1.",
        )
    return _check("docker_bind_scope", "Production Docker bind scope", "pass", evidence)


def _room_production_scope_check() -> dict[str, object]:
    production = ROOT / "docker-compose.production.yml"
    text = production.read_text(encoding="utf-8", errors="ignore") if production.exists() else ""
    if "profiles:" not in text or "- room" not in text:
        return _check(
            "room_server_production_scope",
            "Room Server is scoped out until Orange Pi real provider",
            "fail",
            [str(production.relative_to(ROOT))],
            "room-server is not behind the room profile.",
        )
    if "AEGIS_ROOM_LIGHT_PROVIDER:-disabled" not in text:
        return _check(
            "room_server_production_scope",
            "Room Server is scoped out until Orange Pi real provider",
            "fail",
            [str(production.relative_to(ROOT))],
            "production compose does not default Room provider to disabled.",
        )
    return _check(
        "room_server_production_scope",
        "Room Server is scoped out until Orange Pi real provider",
        "pass",
        [str(production.relative_to(ROOT))],
    )


def _dashboard_auth_check() -> dict[str, object]:
    mode = os.environ.get("AEGIS_RUNTIME_MODE", "development").strip().lower()
    code = (ROOT / "ai-server/src/aegis_ai/docker_entrypoint.py").read_text(encoding="utf-8", errors="ignore")
    auth_code = (ROOT / "ai-server/src/aegis_ai/web/auth.py").read_text(encoding="utf-8", errors="ignore")
    if "AEGIS_AUTH_MODE=passkey is required" not in code or "install_passkey_auth" not in auth_code:
        return _check(
            "dashboard_auth_required",
            "Passkey auth required in production",
            "fail",
            [],
            "Passkey runtime guard missing",
        )
    if mode == "production" and not os.environ.get("AEGIS_SESSION_SECRET", "").strip():
        return _check(
            "dashboard_auth_required",
            "Passkey auth required in production",
            "fail",
            [],
            "AEGIS_SESSION_SECRET is unset in production environment.",
        )
    if mode == "production" and os.environ.get("AEGIS_AUTH_MODE", "passkey").strip().lower() != "passkey":
        return _check(
            "dashboard_auth_required",
            "Passkey auth required in production",
            "fail",
            [],
            "AEGIS_AUTH_MODE must be passkey in production.",
        )
    return _check("dashboard_auth_required", "Passkey auth required in production", "pass")


def _volume_persistence_check() -> dict[str, object]:
    compose = ROOT / "docker-compose.yml"
    text = compose.read_text(encoding="utf-8", errors="ignore") if compose.exists() else ""
    required = ["aegis-data", "aegis-reports"]
    missing = [name for name in required if name not in text]
    if missing:
        return _check(
            "docker_volume_persistence",
            "Docker data/report volumes",
            "fail",
            [str(compose)],
            f"Missing volumes: {missing}",
        )
    return _check("docker_volume_persistence", "Docker data/report volumes", "pass", [str(compose)])


def _capability_override_persistence_check() -> dict[str, object]:
    code = (ROOT / "ai-server/src/aegis_ai/capability_catalog.py").read_text(encoding="utf-8", errors="ignore")
    store = ROOT / "ai-server/src/aegis_ai/capability_overrides.py"
    if "capability_overrides.json" not in code or '"settings"' not in code or not store.exists():
        return _check(
            "capability_override_persistence",
            "Capability risk override persistence",
            "fail",
            [str(store.relative_to(ROOT))],
            "CapabilityCatalog is not wired to the persistent override store.",
        )
    e2e = _load_json(ROOT / "data/reports/e2e/latest/manager-risk-override.json")
    if not e2e:
        return _check(
            "capability_override_persistence",
            "Capability risk override persistence",
            "fail",
            ["data/reports/e2e/latest/manager-risk-override.json"],
            "No stateful E2E evidence for override persistence/effective policy.",
        )
    return _check(
        "capability_override_persistence",
        "Capability risk override persistence",
        "pass",
        ["data/reports/e2e/latest/manager-risk-override.json"],
    )


def _mock_provider_reject_check() -> dict[str, object]:
    core = (ROOT / "ai-server/src/aegis_ai/production_readiness.py").read_text(encoding="utf-8", errors="ignore")
    room = (ROOT / "room-server/src/aegis_room/providers.py").read_text(encoding="utf-8", errors="ignore")
    if "is_mock_like_output" not in core or "not allowed when AEGIS_RUNTIME_MODE=production" not in room:
        return _check(
            "mock_provider_rejected",
            "Mock providers rejected in production",
            "fail",
            ["ai-server/src/aegis_ai/production_readiness.py", "room-server/src/aegis_room/providers.py"],
            "Production mock rejection guard is missing.",
        )
    return _check(
        "mock_provider_rejected",
        "Mock providers rejected in production",
        "pass",
        ["ai-server/src/aegis_ai/production_readiness.py", "room-server/src/aegis_room/providers.py"],
    )


def _secrets_check() -> dict[str, object]:
    report = ROOT / "data" / "reports" / "secret_inventory.json"
    data = _load_json(report)
    if not data:
        return _check(
            "secrets_not_baked",
            "Secrets not baked into Git/static assets",
            "fail",
            [str(report.relative_to(ROOT))],
            "Secret audit report is missing.",
        )
    if str(data.get("status") or "").lower() != "pass":
        findings = data.get("findings") if isinstance(data.get("findings"), list) else []
        return _check(
            "secrets_not_baked",
            "Secrets not baked into Git/static assets",
            "fail",
            [str(report.relative_to(ROOT))],
            f"Secret audit findings: {len(findings)}",
        )
    return _check(
        "secrets_not_baked", "Secrets not baked into Git/static assets", "pass", [str(report.relative_to(ROOT))]
    )


def _report_pass(path: Path, check_id: str, name: str, required_fields: list[str] | None = None) -> dict[str, object]:
    data = _load_json(path)
    if not data:
        return _check(check_id, name, "fail", [str(path)], f"Missing or unreadable {path}")
    status = str(data.get("status") or data.get("overall_status") or "").lower()
    if status and status != "pass":
        return _check(check_id, name, "fail", [str(path)], f"Report status is {status}", str(path))
    for field in required_fields or []:
        if data.get(field) in (None, "", []):
            return _check(check_id, name, "fail", [str(path)], f"Report missing measured field: {field}", str(path))
    return _check(check_id, name, "pass", [str(path)], report_path=str(path))


def _real_device_report_check(
    path: Path,
    check_id: str,
    name: str,
    *,
    required_true: list[str],
    required_check_ids: list[str],
) -> dict[str, object]:
    """Require explicit real-device evidence instead of trusting top-level pass."""
    data = _load_json(path)
    if not data:
        return _check(check_id, name, "fail", [str(path)], f"Missing or unreadable {path}")
    errors: list[str] = []
    if str(data.get("status") or "").lower() != "pass":
        errors.append(f"status={data.get('status') or 'unknown'}")
    errors.extend(f"{field}=false" for field in required_true if data.get(field) is not True)
    checks = data.get("checks") if isinstance(data.get("checks"), list) else []
    statuses = {
        str(item.get("id")): str(item.get("status") or "").lower()
        for item in checks
        if isinstance(item, dict) and item.get("id")
    }
    errors.extend(
        f"{item_id}={statuses.get(item_id, 'missing')}"
        for item_id in required_check_ids
        if statuses.get(item_id) != "pass"
    )
    return _check(
        check_id,
        name,
        "fail" if errors else "pass",
        [str(path)],
        "; ".join(errors),
        str(path),
    )


def _display_soak_check() -> dict[str, object]:
    path = ROOT / "data/reports/e2e/latest/display_soak_summary.json"
    data = _load_json(path)
    duration = int(data.get("duration_seconds") or 0) if data else 0
    equivalent_duration = int(data.get("equivalent_duration_seconds") or 0) if data else 0
    failures = int(data.get("failure_count") or 0) if data else 0
    passed = (
        str(data.get("status") or "").lower() == "pass"
        and max(duration, equivalent_duration) >= 72 * 60 * 60
        and failures == 0
    )
    error = (
        ""
        if passed
        else (
            "72-hour soak incomplete: "
            f"duration_seconds={duration}, equivalent_duration_seconds={equivalent_duration}, failures={failures}"
        )
    )
    return _check(
        "display_soak", "Dedicated Display 72-hour soak", "pass" if passed else "fail", [str(path)], error, str(path)
    )


def main() -> int:
    args = parse_args("Audit AEGIS production readiness")
    report_dir = Path(args.report_dir)
    start = time.time()
    checks: list[dict[str, object]] = []

    python = sys.executable
    mock = run_command([python, "scripts/audit-mocks.py", "--report-dir", str(report_dir), "--json-only"])
    checks.append(
        {
            "id": "production_blocker_mock",
            "name": "production_blocker mock inventory",
            "status": mock["status"],
            "duration_ms": mock["duration_ms"],
            "evidence": [str(report_dir / "production_blockers.json")],
            "error": mock["stderr"] if mock["status"] != "pass" else "",
            "report_path": str(report_dir / "production_blockers.json"),
        }
    )
    coverage = run_command(
        [python, "scripts/audit-capability-coverage.py", "--report-dir", str(report_dir), "--json-only"]
    )
    checks.append(
        {
            "id": "capability_coverage",
            "name": "Capability manifest coverage",
            "status": coverage["status"],
            "duration_ms": coverage["duration_ms"],
            "evidence": [str(report_dir / "capability_coverage.json")],
            "error": coverage["stderr"] if coverage["status"] != "pass" else "",
            "report_path": str(report_dir / "capability_coverage.json"),
        }
    )
    run_command([python, "scripts/audit-dead-code.py", "--report-dir", str(report_dir), "--json-only"])
    secret = run_command([python, "scripts/audit-secrets.py", "--report-dir", str(report_dir), "--json-only"])
    checks.append(
        {
            "id": "secret_inventory",
            "name": "Secret inventory audit",
            "status": secret["status"],
            "duration_ms": secret["duration_ms"],
            "evidence": [str(report_dir / "secret_inventory.json")],
            "error": secret["stderr"] if secret["status"] != "pass" else "",
            "report_path": str(report_dir / "secret_inventory.json"),
        }
    )
    ui = run_command([python, "scripts/audit-ui-completeness.py", "--report-dir", str(report_dir), "--json-only"])
    checks.append(
        {
            "id": "ui_completeness",
            "name": "UI completeness audit",
            "status": ui["status"],
            "duration_ms": ui["duration_ms"],
            "evidence": [str(report_dir / "ui_completeness.json")],
            "error": ui["stderr"] if ui["status"] != "pass" else "",
            "report_path": str(report_dir / "ui_completeness.json"),
        }
    )
    v1 = run_command([python, "scripts/audit-v1-completion.py", "--report-dir", str(report_dir), "--json-only"])
    checks.append(
        {
            "id": "v1_completion",
            "name": "v1 completion audit",
            "status": v1["status"],
            "duration_ms": v1["duration_ms"],
            "evidence": [str(report_dir / "v1_completion.json")],
            "error": v1["stderr"] if v1["status"] != "pass" else "",
            "report_path": str(report_dir / "v1_completion.json"),
        }
    )

    checks.extend(
        [
            _docker_bind_check(),
            _room_production_scope_check(),
            _dashboard_auth_check(),
            _volume_persistence_check(),
            _capability_override_persistence_check(),
            _mock_provider_reject_check(),
            _secrets_check(),
            _report_pass(report_dir / "mock_inventory.json", "mock_inventory_report", "Mock inventory report"),
            _report_pass(
                report_dir / "capability_coverage.json", "capability_coverage_report", "Capability coverage report"
            ),
            _report_pass(report_dir / "ui_completeness.json", "ui_completeness_report", "UI completeness report"),
            _report_pass(report_dir / "v1_completion.json", "v1_completion_report", "v1 completion report"),
            _e2e_check(report_dir, "docker_core", "Docker core E2E"),
            _e2e_check(report_dir, "docker_persistence", "Docker restart/recreate persistence E2E"),
            _e2e_check(report_dir, "backup_restore", "Docker volume backup/isolated restore E2E"),
            _e2e_check(report_dir, "manager_e2e", "Stateful Manager E2E"),
            _real_device_report_check(
                ROOT / "data/reports/e2e/latest/pc-real.json",
                "pc_real",
                "PC service observe/action E2E",
                required_true=["service_install_tested", "real_actions_tested"],
                required_check_ids=[
                    "pc_service_install_start",
                    "pc_health",
                    "pc_screenshot",
                    "pc_active_window",
                    "pc_show_overlay",
                    "pc_real_action",
                    "pc_service_restart",
                    "pc_service_logs",
                    "pc_service_uninstall",
                ],
            ),
            _real_device_report_check(
                ROOT / "data/reports/e2e/latest/android-real.json",
                "android_real",
                "Android LAN-outside E2E",
                required_true=[
                    "tailscale",
                    "wifi_off_tested",
                    "screen_off_tested",
                    "ai_restart_tested",
                    "app_restart_tested",
                ],
                required_check_ids=[
                    "adb_device",
                    "android_app_installed",
                    "android_online",
                    "android_screen_off_reconnect",
                    "android_ai_restart_reconnect",
                    "android_app_restart_reconnect",
                    "android_wifi_off_tailscale",
                ],
            ),
            _e2e_check(report_dir, "browser_real", "Browser real E2E"),
            _e2e_check(report_dir, "dev_real", "Dev server real E2E"),
            _report_pass(
                ROOT / "data/reports/e2e/latest/android-real.json",
                "android_reconnect_metrics",
                "Android reconnect metrics",
                ["reconnect_count", "heartbeat_failure_count"],
            ),
            _display_soak_check(),
            check_file("docs/ubuntu-production.md", "Ubuntu production runbook"),
            check_file("scripts/e2e/run-all-real.ps1", "Real E2E runner"),
            check_file("scripts/test-android-real.ps1", "Android real-device test runner"),
            check_file("scripts/pc/build-portable.ps1", "PC portable package script"),
        ]
    )

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
