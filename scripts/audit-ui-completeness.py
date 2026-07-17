#!/usr/bin/env python3
"""Audit AEGIS UI completion against UI_Instruction.md.

The audit is intentionally heuristic: it catches missing surfaces and common
quality risks that make the UI feel unfinished, then writes a stable report for
humans and CI/readiness gates.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "data" / "reports"


@dataclass
class Check:
    id: str
    area: str
    title: str
    status: str
    evidence: list[str]
    missing: list[str]
    severity: str = "medium"


def main() -> int:
    checks = [
        check_files(
            "web-dashboard",
            "Nine-domain master dashboard",
            [
                "DESIGN.md",
                "web-ui/src/App.tsx",
                "web-ui/src/navigation.ts",
                "web-ui/src/pages/DomainPage.tsx",
                "web-ui/src/components/GlobalSearch.tsx",
                "web-ui/src/components/GlobalInspector.tsx",
                "web-ui/src/components/CommandPalette.tsx",
                "web-ui/src/components/LiveActivityDrawer.tsx",
                "web-ui/src/pages/CommandCenter.tsx",
                "web-ui/src/pages/Work.tsx",
                "web-ui/src/pages/Approvals.tsx",
                "web-ui/src/pages/Systems.tsx",
                "web-ui/src/pages/MindMemory.tsx",
                "web-ui/src/pages/ActivityPage.tsx",
                "web-ui/src/pages/Settings.tsx",
                "web-ui/src/pages/CapabilityCatalogPage.tsx",
                "web-ui/src/pages/LLMUsagePage.tsx",
                "web-ui/src/pages/PolicySimulationPage.tsx",
                "web-ui/src/pages/ModelsPromptsPage.tsx",
                "web-ui/src/pages/RuleManagementPage.tsx",
            ],
        ),
        check_files(
            "display",
            "Dedicated Display compositor",
            [
                "web-ui/src/pages/Display.tsx",
                "web-ui/src/components/cognitive-field/CognitiveField.tsx",
                "web-ui/src/components/cognitive-field/EnvironmentLayer.ts",
                "web-ui/src/components/cognitive-field/MemoryField.ts",
                "web-ui/src/components/cognitive-field/SystemTopology.ts",
                "web-ui/src/components/cognitive-field/MissionFlow.ts",
                "web-ui/src/components/cognitive-field/EventParticles.ts",
                "web-ui/src/components/cognitive-field/SceneCamera.ts",
                "web-ui/src/components/cognitive-field/SceneDirector.ts",
                "web-ui/src/displayModel.ts",
            ],
        ),
        check_files(
            "android",
            "Android mobile UI surfaces",
            [
                "android-server/app/src/main/java/com/aegis/android/ui/AegisMobileV2App.kt",
                "android-server/app/src/main/java/com/aegis/android/ui/feature/home/HomeScreen.kt",
                "android-server/app/src/main/java/com/aegis/android/ui/feature/approvals/ApprovalsScreen.kt",
                "android-server/app/src/main/java/com/aegis/android/ui/feature/tasks/TasksScreen.kt",
                "android-server/app/src/main/java/com/aegis/android/ui/feature/devices/DevicesScreen.kt",
                "android-server/app/src/main/java/com/aegis/android/ui/feature/permissions/PermissionsScreen.kt",
                "android-server/app/src/main/java/com/aegis/android/ui/feature/settings/SettingsScreen.kt",
            ],
        ),
        check_files(
            "overview-v3",
            "Normalized UI overview contract",
            [
                "ai-server/src/aegis_ai/web/ui_overview.py",
                "web-ui/src/types.ts",
                "android-server/app/src/main/java/com/aegis/android/ui/model/MobileUiModels.kt",
            ],
        ),
        check_presentation_contract(),
        check_master_navigation(),
        check_cognitive_field(),
        check_resource_contract(),
        check_tokens(),
        check_quality_smells(),
        check_state_coverage(),
        check_tests(),
        check_legacy_dependency(),
        check_completion_ledger(),
    ]
    payload = {
        "schema_version": "ui-completeness.v1",
        "overall_status": overall(checks),
        "summary": {
            "pass": sum(1 for c in checks if c.status == "pass"),
            "partial": sum(1 for c in checks if c.status == "partial"),
            "fail": sum(1 for c in checks if c.status == "fail"),
        },
        "checks": [asdict(check) for check in checks],
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "ui_completeness.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (REPORT_DIR / "ui_completeness.md").write_text(render_markdown(payload), encoding="utf-8")
    print(f"wrote {REPORT_DIR / 'ui_completeness.md'}")
    return 0 if payload["overall_status"] == "pass" else 1


def check_files(check_id: str, title: str, paths: list[str]) -> Check:
    missing = [path for path in paths if not (ROOT / path).exists()]
    evidence = [path for path in paths if (ROOT / path).exists()]
    return Check(check_id, "surface", title, "pass" if not missing else "fail", evidence, missing, "high")


def check_tokens() -> Check:
    paths = [
        "design-tokens/tokens.json",
        "web-ui/src/styles/tokens.css",
        "android-server/app/src/main/java/com/aegis/android/ui/designsystem/GeneratedTokens.kt",
        "design-tokens/contrast-report.json",
    ]
    check = check_files("design-tokens", "Shared design token generation and contrast data", paths)
    if check.status == "pass":
        report = read_json(ROOT / "design-tokens/contrast-report.json")
        if not report.get("all_aa_body", False):
            check.status = "fail"
            check.missing.append("contrast-report all_aa_body=true")
    return check


def check_presentation_contract() -> Check:
    paths = [
        "ai-server/src/aegis_ai/presentation/surface_contract.py",
        "ai-server/src/aegis_ai/web/ui_overview.py",
        "web-ui/src/pages/ActivityPage.tsx",
        "web-ui/src/pages/Settings.tsx",
    ]
    check = check_files("presentation-event-contract", "PresentationEvent and Surface Role contract", paths)
    haystack = "\n".join(read_text(ROOT / path) for path in paths)
    required = [
        "PresentationEvent",
        "recommended_surfaces",
        "privacy_class",
        "surface_roles",
        "presentation_events",
        "dedicated_display",
        "web_dashboard",
        "mobile_app",
        "pc_overlay",
        "android_notification",
        "room_display",
        "developer_console",
    ]
    missing = [token for token in required if token not in haystack]
    if missing:
        check.status = "partial" if check.status == "pass" else check.status
        check.missing.extend(missing)
    return check


def check_master_navigation() -> Check:
    text = read_text(ROOT / "web-ui/src/navigation.ts")
    required = [
        "Command",
        "Work",
        "Intelligence",
        "Capabilities",
        "Infrastructure",
        "Communications",
        "Governance",
        "Observability",
        "Configuration",
    ]
    missing = [label for label in required if f'label: "{label}"' not in text]
    return Check(
        "master-navigation",
        "architecture",
        "Nine management domains",
        "pass" if not missing else "fail",
        ["web-ui/src/navigation.ts"],
        missing,
        "high",
    )


def check_cognitive_field() -> Check:
    active = "\n".join(read_text(path) for path in (ROOT / "web-ui/src").rglob("*.tsx"))
    required = [
        "CognitiveField",
        "EnvironmentLayer",
        "MemoryField",
        "SystemTopology",
        "MissionFlow",
        "EventParticles",
        "SceneCamera",
        "SceneDirector",
    ]
    module_text = "\n".join(read_text(path) for path in (ROOT / "web-ui/src/components/cognitive-field").glob("*.*"))
    missing = [token for token in required if token not in module_text and token not in active]
    if 'from "../components/CoreSphere"' in active or 'from "./CoreSphere"' in active:
        missing.append("active UI still imports deprecated CoreSphere")
    return Check(
        "cognitive-field",
        "spatial",
        "Layered Cognitive Field replaces central sphere",
        "pass" if not missing else "fail",
        ["web-ui/src/components/cognitive-field"],
        missing,
        "high",
    )


def check_resource_contract() -> Check:
    paths = [
        "ai-server/src/aegis_ai/web/resource_routes.py",
        "web-ui/src/api/client.ts",
        "web-ui/src/entityModel.ts",
        "ai-server/tests/test_resource_routes.py",
    ]
    check = check_files("resource-contract", "Manager-backed EntitySummary API", paths)
    text = "\n".join(read_text(ROOT / path) for path in paths)
    required = [
        "/api/ui/entities",
        "/api/ui/search",
        "/api/memories",
        "/api/approvals",
        "/api/policy/simulate",
        "/api/hooks/",
        "/api/delegations/",
        "EntitySummary",
    ]
    missing = [token for token in required if token not in text]
    if missing:
        check.status = "fail"
        check.missing.extend(missing)
    return check


def check_quality_smells() -> Check:
    files = list((ROOT / "web-ui/src").rglob("*.tsx")) + list(
        (ROOT / "android-server/app/src/main/java/com/aegis/android/ui").rglob("*.kt")
    )
    inline_styles = 0
    not_reported = 0
    raw_standard = 0
    generic_panels = 0
    for path in files:
        text = read_text(path)
        inline_styles += len(re.findall(r"style=\{\{", text))
        not_reported += text.count("Not reported")
        generic_panels += text.count('className="panel"')
        if "rawJson" in text or "Developer raw state" in text:
            raw_standard += 1 if "Developer raw state" not in text and "debug" not in text.lower() else 0
    missing: list[str] = []
    if inline_styles:
        missing.append(f"{inline_styles} inline style occurrences")
    if not_reported > 45:
        missing.append(f"{not_reported} Not reported fallbacks")
    if generic_panels > 35:
        missing.append(f"{generic_panels} generic panel usages")
    if raw_standard:
        missing.append("raw JSON appears outside debug/developer context")
    status = "pass" if not missing else "partial"
    return Check(
        "quality-smells",
        "quality",
        "UI polish smell scan",
        status,
        [str(p.relative_to(ROOT)) for p in files[:12]],
        missing,
    )


def check_state_coverage() -> Check:
    required = ["Loading", "Empty", "Permission", "Degraded", "Disconnected", "Stale", "Unauthorized", "Fresh"]
    haystack = "\n".join(read_text(path) for path in (ROOT / "web-ui/src").rglob("*.tsx"))
    missing = [word for word in required if word.lower() not in haystack.lower()]
    return Check(
        "state-coverage",
        "states",
        "Loading/empty/error/auth/freshness state coverage",
        "pass" if not missing else "partial",
        ["web-ui/src"],
        missing,
        "high",
    )


def check_tests() -> Check:
    required = [
        "web-ui/src/pages/DashboardPages.test.tsx",
        "web-ui/tests/display.spec.ts",
        "web-ui/tests/master-dashboard.spec.ts",
        "ai-server/tests/test_ui_overview.py",
        "ai-server/tests/test_resource_routes.py",
        "ai-server/tests/test_design_tokens.py",
    ]
    check = check_files("tests", "UI unit/API/Display test coverage", required)
    android_tests = list((ROOT / "android-server").rglob("*Test.kt"))
    if not android_tests:
        check.status = "partial"
        check.missing.append("Android Compose UI tests")
    else:
        check.evidence.extend(str(path.relative_to(ROOT)) for path in android_tests[:5])
    return check


def check_legacy_dependency() -> Check:
    ui_v2 = read_text(ROOT / "ai-server/src/aegis_ai/web/routes/ui_v2.py")
    shell = read_text(ROOT / "ai-server/src/aegis_ai/web/dashboard_routes.py")
    missing: list[str] = []
    if 'AEGIS_UI_VERSION", "legacy"' in ui_v2:
        missing.append("AEGIS_UI_VERSION default is legacy")
    if "dashboard_legacy" in shell and "Compatibility shell" not in shell:
        missing.append("dashboard_routes still delegates compatibility to dashboard_legacy")
    return Check(
        "legacy-dependency",
        "compat",
        "Legacy UI dependency remaining",
        "partial" if missing else "pass",
        ["ai-server/src/aegis_ai/web/routes/ui_v2.py"],
        missing,
    )


def check_completion_ledger() -> Check:
    path = ROOT / "docs/ui-implementation-checklist.md"
    text = read_text(path)
    deferred = text.split("## Deferred", 1)[0]
    partial = re.findall(r"^- \[~\]\s+(.+)$", deferred, flags=re.MULTILINE)
    open_items = re.findall(r"^- \[ \]\s+(.+)$", deferred, flags=re.MULTILINE)
    blockers = re.findall(r"^- \[!\]\s+(.+)$", deferred, flags=re.MULTILINE)
    missing = [f"partial: {item}" for item in partial]
    missing.extend(f"open: {item}" for item in open_items)
    missing.extend(f"blocker: {item}" for item in blockers)
    status = "pass" if not missing else "partial"
    if blockers:
        status = "fail"
    return Check(
        "completion-ledger",
        "acceptance",
        "UI instruction completion ledger is closed",
        status,
        [path.relative_to(ROOT).as_posix()] if path.exists() else [],
        missing or ([] if path.exists() else ["docs/ui-implementation-checklist.md"]),
        "high",
    )


def overall(checks: list[Check]) -> str:
    if any(check.status == "fail" and check.severity == "high" for check in checks):
        return "fail"
    if any(check.status != "pass" for check in checks):
        return "partial"
    return "pass"


def render_markdown(payload: dict) -> str:
    lines = [
        "# AEGIS UI Completeness Report",
        "",
        f"- Overall status: `{payload['overall_status']}`",
        f"- Pass: {payload['summary']['pass']}",
        f"- Partial: {payload['summary']['partial']}",
        f"- Fail: {payload['summary']['fail']}",
        "",
        "| ID | Area | Status | Missing |",
        "| --- | --- | --- | --- |",
    ]
    for check in payload["checks"]:
        missing = "<br>".join(check["missing"]) if check["missing"] else "-"
        lines.append(f"| `{check['id']}` | {check['area']} | `{check['status']}` | {missing} |")
    lines.append("")
    return "\n".join(lines)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def read_json(path: Path) -> dict:
    try:
        return json.loads(read_text(path))
    except Exception:
        return {}


if __name__ == "__main__":
    raise SystemExit(main())
