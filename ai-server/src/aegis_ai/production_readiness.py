"""Production readiness helpers.

This module is intentionally small and dependency-light so core runtime paths
can reject mock/stub success without importing dashboard or report code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


PRODUCTION_MODE = "production"
DEFAULT_REPORT_PATH = "data/reports/production_blockers.json"


def runtime_mode() -> str:
    return str(os.environ.get("AEGIS_RUNTIME_MODE") or "development").strip().lower()


def is_production_mode() -> bool:
    return runtime_mode() == PRODUCTION_MODE


def readiness_report_path() -> Path:
    return Path(os.environ.get("AEGIS_PRODUCTION_READINESS_REPORT") or DEFAULT_REPORT_PATH)


def is_mock_like_output(value: Any) -> bool:
    """Return True when a tool result is explicitly mock/stub-only.

    The check is structural and deliberately conservative: it only trips on
    explicit mock/stub markers, not arbitrary user-facing words.
    """
    if isinstance(value, dict):
        for key in ("mock", "stub", "skeleton"):
            if value.get(key) is True:
                return True
        provider = str(value.get("provider") or value.get("provider_used") or "").lower()
        source = str(value.get("source") or "").lower()
        if provider == "mock" or source == "mock":
            return True
        for nested in value.values():
            if is_mock_like_output(nested):
                return True
        return False
    if isinstance(value, list):
        return any(is_mock_like_output(item) for item in value)
    if isinstance(value, str):
        text = value.strip().lower()
        return text.startswith("[mock]") or text in {"mock", "stub"}
    return False


def _unreadable_report(report_path: Path, cause: str) -> dict[str, Any]:
    """A report we could not obtain is not a report that found nothing.

    `{"blockers": []}` from a file that was never read is indistinguishable from a
    clean inventory, and every caller here (the dashboard route, the readiness audit)
    turns "no blockers" into a pass. So return one explicit blocker -- the same shape
    the parse-failure branch already used -- and let the count be the machine signal.
    `cause` names *why*, because "was not found" and "is not a JSON object" are
    different failures and must not share a wording.
    """
    return {
        "blockers": [
            {
                "classification": "production_blocker",
                "reason": f"Production readiness report {cause}: {report_path}",
            }
        ],
        "summary": {"production_blocker": 1},
        "unreadable": True,
        "cause": cause,
    }


def load_production_blocker_report(path: str | Path | None = None) -> dict[str, Any]:
    """Load the blocker report, or a blocker that says why it could not be loaded.

    A missing report is not a clean report: see `_unreadable_report`. The previous
    `corrupted` key was folded into `unreadable` + `cause`, which covers the parse
    failure it used to flag and the two silent cases it did not.
    """
    report_path = Path(path) if path else readiness_report_path()
    try:
        if not report_path.exists():
            return _unreadable_report(report_path, "was not found")
        with report_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
        return _unreadable_report(report_path, "is not a JSON object")
    except Exception:
        return _unreadable_report(report_path, "could not be read")


def blocker_capability_ids(report: dict[str, Any] | None = None) -> set[str]:
    data = report if report is not None else load_production_blocker_report()
    ids: set[str] = set()
    for item in data.get("blockers", []) or []:
        if not isinstance(item, dict):
            continue
        cap_id = str(item.get("capability_id") or "").strip()
        if cap_id:
            ids.add(cap_id)
    return ids


def production_blocker_count(report: dict[str, Any] | None = None) -> int:
    data = report if report is not None else load_production_blocker_report()
    summary = data.get("summary") or {}
    if isinstance(summary, dict) and "production_blocker" in summary:
        try:
            return int(summary.get("production_blocker") or 0)
        except Exception:
            pass
    return sum(
        1
        for item in data.get("blockers", []) or []
        if isinstance(item, dict) and item.get("classification") == "production_blocker"
    )
