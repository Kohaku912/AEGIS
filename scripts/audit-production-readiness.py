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


def _source_text(rel: str) -> str | None:
    """Read a repo source file, or ``None`` when it is missing.

    A source-reading check must not take the whole audit down: ``main`` evaluates every
    check *before* it writes ``readiness_summary.json``, so an unguarded ``read_text`` on
    a moved file raises out of ``main`` and leaves the **previous** report on disk -- a
    stale report that every downstream reader (the dashboard route via
    ``load_production_blocker_report``, and ``_load_blockers``) then reads as fresh.
    ``_docker_bind_check``, ``_room_production_scope_check`` and
    ``_volume_persistence_check`` already guard with ``.exists()``; three siblings did
    not (measured 2026-10-07: they raised ``FileNotFoundError`` while the guarded three
    returned a clean ``fail`` naming the file).
    """
    path = ROOT / rel
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="ignore")


def _as_int(value: object) -> int | None:
    """Coerce a report number the way ``int(value or 0)`` did -- but never raise.

    ``None`` means "the value is truthy and is not a number" -- the only input for which the
    old expression raised. An exception here would abort ``main`` before it writes
    ``readiness_summary.json``, leaving the **previous** report on disk for every downstream
    reader (the cycle-85 shape, reached through a value rather than a missing file). Callers
    that only carry metadata collapse ``None`` to ``0``; callers that take a verdict from the
    value treat it as a malformed measurement.
    """
    if not value:  # falsy -> 0, exactly as ``value or 0`` did
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _display_path(path: Path) -> str:
    """A report's path as the audit has always reported it.

    Relative to ``ROOT`` when the path is inside it -- so the default ``--report-dir``
    (``ROOT/data/reports``) reports exactly what it always did -- and absolute otherwise.
    A custom report dir outside ``ROOT`` must not raise ``ValueError`` from ``relative_to``,
    which would abort ``main`` before it writes ``readiness_summary.json``.
    """
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _result_cause(match: dict[str, object], status: str) -> str:
    """Why an E2E result is not a pass -- its message, or its failing sub-checks.

    The E2E runner records the top-level ``error`` only sometimes. The live
    ``manager-e2e.json`` is ``status: fail`` with ``error: ""`` while its ten nested
    ``checks`` name the reason (seven "リモート サーバーに接続できません。" and three
    "ai-server container is not running"), so recording the top-level field alone left the
    readiness summary with a ``fail`` and **no cause**. Fall back to the nested checks,
    then to the status itself -- a non-pass result never returns ``""``. The list is
    bounded so a pathological report cannot flood the summary.
    """
    if status == "pass":
        return ""
    message = str(match.get("error") or "").strip()
    if message:
        return message
    nested = match.get("checks")
    if isinstance(nested, list):
        reasons = [
            f"{c.get('id') or c.get('name') or '?'}: {c.get('error') or c.get('status') or 'fail'}"
            for c in nested
            if isinstance(c, dict) and str(c.get("status") or "fail") != "pass"
        ]
        if reasons:
            head = reasons[:5]
            extra = len(reasons) - len(head)
            return "; ".join(head) + (f" (+{extra} more)" if extra else "")
    return f"E2E result status is {status} and carries no error message"


def _process_cause(result: dict[str, object]) -> str:
    """Why a spawned audit is not a pass -- its stderr, else its stdout.

    ``run_command`` captures both streams separately, each bounded to its last 4000
    chars. A failing audit writes its one-line reason to *stdout* and exits nonzero
    (measured 2026-10-07: ``audit-mocks.py`` -> ``status=fail mock findings=1611
    production_blockers=2 files_scanned=3915 error=production_blockers=2``), leaving
    ``stderr`` empty -- so recording ``stderr`` alone gave the readiness summary four
    ``fail`` checks with **no cause**. ``stderr`` still wins when it is populated,
    because that is where an unexpected traceback lands.

    ``_result_cause`` reads an E2E *record* (``error`` / nested ``checks``); this reads
    a *process* result. Two helpers so that neither shape's caller has to know the
    other's fallbacks -- and so a passing check is silent either way.

    ``audit-ui-completeness.py`` is the one audit that prints only its output path on
    stdout, so for it the recorded cause is that path -- a pointer at the report rather
    than a reason, but no longer silence.
    """
    if str(result.get("status") or "fail") == "pass":
        return ""
    for key in ("stderr", "stdout"):
        value = str(result.get(key) or "").strip()
        if value:
            return value
    return "audit exited nonzero with no output on stdout or stderr"


def _e2e_check(report_dir: Path, check_id: str, name: str, required: bool = True) -> dict[str, object]:
    # The caller passes the audit's ``--report-dir`` (default ``data/reports``), so the
    # E2E tree is ``<report_dir>/e2e/latest``. This used to be hard-coded to
    # ``ROOT/data/reports/e2e/latest`` -- identical for the default, but it silently
    # ignored ``--report-dir`` and disagreed with ``_report_pass`` (which honours it).
    latest = report_dir / "e2e" / "latest"
    summary = _load_json(latest / "summary.json")
    checks = summary.get("checks") if isinstance(summary.get("checks"), list) else []
    match = next((c for c in checks if isinstance(c, dict) and c.get("id") == check_id), None)
    for candidate in (
        latest / f"{check_id.replace('_', '-')}.json",
        latest / f"{check_id}.json",
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
            [str(latest / "summary.json")],
            f"Missing E2E result for {check_id}",
        )
    status = str(match.get("status") or "fail")
    return _check(
        check_id,
        name,
        "pass" if status == "pass" else "fail",
        [str(match.get("report_path") or latest / "summary.json")],
        _result_cause(match, status),
        str(match.get("report_path") or ""),
        _as_int(match.get("duration_ms")) or 0,
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
    entrypoint = "ai-server/src/aegis_ai/docker_entrypoint.py"
    auth = "ai-server/src/aegis_ai/web/auth.py"
    code = _source_text(entrypoint)
    auth_code = _source_text(auth)
    if code is None or auth_code is None:
        missing = entrypoint if code is None else auth
        return _check(
            "dashboard_auth_required",
            "Passkey auth required in production",
            "fail",
            [missing],
            f"Missing source file: {missing}",
        )
    evidence = [entrypoint, auth]
    if "AEGIS_AUTH_MODE=passkey is required" not in code or "install_passkey_auth" not in auth_code:
        return _check(
            "dashboard_auth_required",
            "Passkey auth required in production",
            "fail",
            evidence,
            "Passkey runtime guard missing",
        )
    if mode == "production" and not os.environ.get("AEGIS_SESSION_SECRET", "").strip():
        return _check(
            "dashboard_auth_required",
            "Passkey auth required in production",
            "fail",
            evidence,
            "AEGIS_SESSION_SECRET is unset in production environment.",
        )
    if mode == "production" and os.environ.get("AEGIS_AUTH_MODE", "passkey").strip().lower() != "passkey":
        return _check(
            "dashboard_auth_required",
            "Passkey auth required in production",
            "fail",
            evidence,
            "AEGIS_AUTH_MODE must be passkey in production.",
        )
    return _check("dashboard_auth_required", "Passkey auth required in production", "pass", evidence)


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


def _capability_override_persistence_check(report_dir: Path) -> dict[str, object]:
    catalog = "ai-server/src/aegis_ai/capability_catalog.py"
    code = _source_text(catalog)
    if code is None:
        return _check(
            "capability_override_persistence",
            "Capability risk override persistence",
            "fail",
            [catalog],
            f"Missing source file: {catalog}",
        )
    store = ROOT / "ai-server/src/aegis_ai/capability_overrides.py"
    if "capability_overrides.json" not in code or '"settings"' not in code or not store.exists():
        return _check(
            "capability_override_persistence",
            "Capability risk override persistence",
            "fail",
            [str(store.relative_to(ROOT))],
            "CapabilityCatalog is not wired to the persistent override store.",
        )
    e2e_path = report_dir / "e2e" / "latest" / "manager-risk-override.json"
    e2e = _load_json(e2e_path)
    if not e2e:
        return _check(
            "capability_override_persistence",
            "Capability risk override persistence",
            "fail",
            [_display_path(e2e_path)],
            "No stateful E2E evidence for override persistence/effective policy.",
        )
    return _check(
        "capability_override_persistence",
        "Capability risk override persistence",
        "pass",
        [_display_path(e2e_path)],
    )


def _mock_provider_reject_check() -> dict[str, object]:
    core_rel = "ai-server/src/aegis_ai/production_readiness.py"
    room_rel = "room-server/src/aegis_room/providers.py"
    core = _source_text(core_rel)
    room = _source_text(room_rel)
    if core is None or room is None:
        missing = core_rel if core is None else room_rel
        return _check(
            "mock_provider_rejected",
            "Mock providers rejected in production",
            "fail",
            [missing],
            f"Missing source file: {missing}",
        )
    if "is_mock_like_output" not in core or "not allowed when AEGIS_RUNTIME_MODE=production" not in room:
        return _check(
            "mock_provider_rejected",
            "Mock providers rejected in production",
            "fail",
            [core_rel, room_rel],
            "Production mock rejection guard is missing.",
        )
    return _check(
        "mock_provider_rejected",
        "Mock providers rejected in production",
        "pass",
        [core_rel, room_rel],
    )


def _secrets_check(report_dir: Path) -> dict[str, object]:
    report = report_dir / "secret_inventory.json"
    data = _load_json(report)
    if not data:
        return _check(
            "secrets_not_baked",
            "Secrets not baked into Git/static assets",
            "fail",
            [_display_path(report)],
            "Secret audit report is missing.",
        )
    if str(data.get("status") or "").lower() != "pass":
        findings = data.get("findings") if isinstance(data.get("findings"), list) else []
        return _check(
            "secrets_not_baked",
            "Secrets not baked into Git/static assets",
            "fail",
            [_display_path(report)],
            f"Secret audit findings: {len(findings)}",
        )
    return _check("secrets_not_baked", "Secrets not baked into Git/static assets", "pass", [_display_path(report)])


def _report_pass(
    path: Path,
    check_id: str,
    name: str,
    required_fields: list[str],
    *,
    present_fields: list[str] = (),
) -> dict[str, object]:
    """Read a sub-audit's report and pass only if it measured a population.

    `required_fields` names the report's own measured-**population** field(s): each must be
    present and non-empty, where a **zero count is empty**. It is **required**, not optional:
    a report whose status is `pass` but which measured nothing must not read as clean -- the
    empty-population family cycle 80 closed in the *generators*, one layer up here.
    Measured 2026-10-07, before this: four of the six call sites passed no fields, so a
    `{"status": "pass"}` report with no population read as a pass, while the two that named a
    field correctly failed it.

    Measured again 2026-10-07 (cycle 89): the emptiness test was `in (None, "", [])`, which
    lets a **zero count** through -- `{"status": "pass", "files_scanned": 0}` read as clean,
    and so did `capabilities: 0`, `checks: 0` and `files_walked: 0`. It is now `not value`, so
    `0`, `False` and `{}` are empty too.

    `present_fields` names fields that must merely be **carried**: there a count of zero is a
    legitimate measurement (`heartbeat_failure_count: 0` is the *good* outcome -- the live
    `android-real.json` has exactly that, so folding it into `required_fields` would flip a
    correct `pass` to `fail`). Kept as its own keyword-only list so the two kinds cannot be
    confused.
    """
    data = _load_json(path)
    if not data:
        return _check(check_id, name, "fail", [str(path)], f"Missing or unreadable {path}")
    status = str(data.get("status") or data.get("overall_status") or "").lower()
    if status and status != "pass":
        return _check(check_id, name, "fail", [str(path)], f"Report status is {status}", str(path))
    for field in required_fields or []:
        if not data.get(field):
            return _check(check_id, name, "fail", [str(path)], f"Report missing measured field: {field}", str(path))
    for field in present_fields or []:
        if data.get(field) in (None, "", []):
            return _check(check_id, name, "fail", [str(path)], f"Report missing field: {field}", str(path))
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


def _display_soak_check(report_dir: Path) -> dict[str, object]:
    path = report_dir / "e2e" / "latest" / "display_soak_summary.json"
    data = _load_json(path)
    raw_duration = _as_int(data.get("duration_seconds"))
    raw_equivalent = _as_int(data.get("equivalent_duration_seconds"))
    raw_failures = _as_int(data.get("failure_count"))
    malformed = [
        field
        for field, value in (
            ("duration_seconds", raw_duration),
            ("equivalent_duration_seconds", raw_equivalent),
            ("failure_count", raw_failures),
        )
        if value is None
    ]
    if malformed:
        return _check(
            "display_soak",
            "Dedicated Display 72-hour soak",
            "fail",
            [str(path)],
            f"Soak report has a non-numeric field: {', '.join(malformed)}",
            str(path),
        )
    duration = raw_duration or 0
    equivalent_duration = raw_equivalent or 0
    failures = raw_failures or 0
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


def _load_blockers(blocker_path: Path) -> list[dict[str, object]]:
    """Read the blocker list, or one blocker that says why it could not be read.

    An absent report and a clean report both yield an empty list, and `main` turns an
    empty list into "no production blockers". The two must not share a verdict, so a
    report that is missing, unreadable, not an object, or missing its `blockers` key
    becomes a blocker itself -- the same shape the parse failure already produced.
    """
    if not blocker_path.exists():
        return [
            {
                "classification": "production_blocker",
                "reason": f"Production readiness report was not found: {blocker_path}",
            }
        ]
    try:
        data = json.loads(blocker_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [
            {
                "classification": "production_blocker",
                "reason": f"Could not read production readiness report: {blocker_path} ({exc})",
            }
        ]
    if not isinstance(data, dict):
        return [
            {
                "classification": "production_blocker",
                "reason": f"Production readiness report is not a JSON object: {blocker_path}",
            }
        ]
    blockers = data.get("blockers")
    if not isinstance(blockers, list):
        return [
            {
                "classification": "production_blocker",
                "reason": f"Production readiness report has no blockers list: {blocker_path}",
            }
        ]
    return blockers


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
            "error": _process_cause(mock),
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
            "error": _process_cause(coverage),
            "report_path": str(report_dir / "capability_coverage.json"),
        }
    )
    dead = run_command([python, "scripts/audit-dead-code.py", "--report-dir", str(report_dir), "--json-only"])
    checks.append(
        {
            "id": "dead_code",
            "name": "Dead/obsolete code inventory",
            "status": dead["status"],
            "duration_ms": dead["duration_ms"],
            "evidence": [str(report_dir / "dead_code_report.json")],
            "error": _process_cause(dead),
            "report_path": str(report_dir / "dead_code_report.json"),
        }
    )
    secret = run_command([python, "scripts/audit-secrets.py", "--report-dir", str(report_dir), "--json-only"])
    checks.append(
        {
            "id": "secret_inventory",
            "name": "Secret inventory audit",
            "status": secret["status"],
            "duration_ms": secret["duration_ms"],
            "evidence": [str(report_dir / "secret_inventory.json")],
            "error": _process_cause(secret),
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
            "error": _process_cause(ui),
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
            "error": _process_cause(v1),
            "report_path": str(report_dir / "v1_completion.json"),
        }
    )

    checks.extend(
        [
            _docker_bind_check(),
            _room_production_scope_check(),
            _dashboard_auth_check(),
            _volume_persistence_check(),
            _capability_override_persistence_check(report_dir),
            _mock_provider_reject_check(),
            _secrets_check(report_dir),
            _report_pass(
                report_dir / "mock_inventory.json",
                "mock_inventory_report",
                "Mock inventory report",
                ["files_scanned"],
            ),
            _report_pass(
                report_dir / "capability_coverage.json",
                "capability_coverage_report",
                "Capability coverage report",
                ["capabilities"],
            ),
            _report_pass(
                report_dir / "ui_completeness.json",
                "ui_completeness_report",
                "UI completeness report",
                ["checks"],
            ),
            _report_pass(
                report_dir / "v1_completion.json",
                "v1_completion_report",
                "v1 completion report",
                ["checks"],
            ),
            _report_pass(
                report_dir / "dead_code_report.json", "dead_code_report", "Dead code report", ["files_walked"]
            ),
            _e2e_check(report_dir, "docker_core", "Docker core E2E"),
            _e2e_check(report_dir, "docker_persistence", "Docker restart/recreate persistence E2E"),
            _e2e_check(report_dir, "backup_restore", "Docker volume backup/isolated restore E2E"),
            _e2e_check(report_dir, "manager_e2e", "Stateful Manager E2E"),
            _real_device_report_check(
                report_dir / "e2e" / "latest" / "pc-real.json",
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
                report_dir / "e2e" / "latest" / "android-real.json",
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
                report_dir / "e2e" / "latest" / "android-real.json",
                "android_reconnect_metrics",
                "Android reconnect metrics",
                ["checks"],
                present_fields=["reconnect_count", "heartbeat_failure_count"],
            ),
            _display_soak_check(report_dir),
            check_file("docs/ubuntu-production.md", "Ubuntu production runbook"),
            check_file("scripts/e2e/run-all-real.ps1", "Real E2E runner"),
            check_file("scripts/test-android-real.ps1", "Android real-device test runner"),
            check_file("scripts/pc/build-portable.ps1", "PC portable package script"),
        ]
    )

    blocker_path = report_dir / "production_blockers.json"
    blockers = _load_blockers(blocker_path)

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
    # The E2E tree is ``<report_dir>/e2e/latest`` -- the very tree ``_e2e_check`` reads.
    # Hard-coding ``ROOT/data/reports/e2e/latest`` made a custom ``--report-dir`` read its
    # E2E results from the *default* tree and, worse, write its summary there -- clobbering
    # the operator's real E2E summary while the custom tree got none (measured 2026-10-07).
    latest = report_dir / "e2e" / "latest"
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
