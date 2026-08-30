#!/usr/bin/env python3
"""Turn off only the kiosk display after inactivity while keeping AEGIS running."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import urllib.request
from typing import Any

OVERVIEW_URL = os.environ.get(
    "AEGIS_DISPLAY_OVERVIEW_URL", "http://127.0.0.1:8090/display/power-state"
)
IDLE_SECONDS = max(60, int(os.environ.get("AEGIS_DISPLAY_IDLE_SECONDS", "600")))
POLL_SECONDS = max(2, int(os.environ.get("AEGIS_DISPLAY_POLL_SECONDS", "5")))
MAX_POLL_SECONDS = max(
    POLL_SECONDS, int(os.environ.get("AEGIS_DISPLAY_MAX_POLL_SECONDS", "60"))
)
REQUEST_TIMEOUT_SECONDS = max(
    1.0, float(os.environ.get("AEGIS_DISPLAY_REQUEST_TIMEOUT_SECONDS", "3"))
)
ERROR_LOG_INTERVAL_SECONDS = max(
    10, int(os.environ.get("AEGIS_DISPLAY_ERROR_LOG_INTERVAL_SECONDS", "60"))
)
FAIL_OPEN_AFTER = max(1, int(os.environ.get("AEGIS_DISPLAY_FAIL_OPEN_AFTER", "2")))
DISPLAY_TOKEN = os.environ.get("AEGIS_DISPLAY_TOKEN", "").strip()


def fetch_overview() -> dict[str, Any]:
    headers = {"X-AEGIS-Display-Token": DISPLAY_TOKEN} if DISPLAY_TOKEN else {}
    request = urllib.request.Request(OVERVIEW_URL, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        payload = json.load(response)
    return payload if isinstance(payload, dict) else {}


def operational_signature(overview: dict[str, Any]) -> str:
    if overview.get("schema_version") == "display-power-state.v1":
        sections = {
            "task": _pick(
                _direct_section(overview, "current_task"),
                "task_id",
                "source",
                "phase",
                "capability_id",
                "current_action",
            ),
            "approvals": _direct_section(overview, "approvals"),
            "servers": _item_projection(
                overview.get("servers"),
                "server_id",
                "status",
                "permission_missing",
                "recovery_state",
            ),
            "presentations": _item_projection(
                overview.get("presentations"),
                "presentation_id",
                "id",
                "status",
                "surface_role",
                "updated_at",
            ),
        }
        encoded = json.dumps(sections, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    sections = {
        "core": _pick(section_data(overview, "core"), "mode", "health", "active_goal"),
        "task": _pick(
            section_data(overview, "current_task"),
            "task_id",
            "status",
            "phase",
            "capability_id",
            "current_action",
        ),
        "attention": _item_projection(
            section_data(overview, "attention").get("items"),
            "id",
            "severity",
            "status",
        ),
        "approvals": _item_projection(
            section_data(overview, "approvals").get("pending"),
            "approval_id",
            "status",
            "capability_id",
        ),
        "servers": _item_projection(
            section_data(overview, "servers").get("items"),
            "server_id",
            "status",
            "permission_missing",
            "recovery_state",
        ),
        "presentations": _item_projection(
            section_data(overview, "presentations").get("items"),
            "presentation_id",
            "id",
            "status",
            "surface_role",
        ),
    }
    encoded = json.dumps(sections, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _pick(value: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {key: value.get(key) for key in keys if key in value}


def _item_projection(value: Any, *keys: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    projected = [_pick(item, *keys) for item in value if isinstance(item, dict)]
    return sorted(projected, key=lambda item: json.dumps(item, sort_keys=True, default=str))


def keep_awake(overview: dict[str, Any]) -> bool:
    if isinstance(overview.get("keep_awake"), bool):
        return bool(overview["keep_awake"])
    task = section_data(overview, "current_task")
    task_status = str(task.get("status") or "").lower()
    approvals = section_data(overview, "approvals")
    return task_status in {"running", "executing", "verifying"} or int(
        approvals.get("pending_count") or 0
    ) > 0


def section_data(overview: dict[str, Any], name: str) -> dict[str, Any]:
    section = overview.get(name)
    if not isinstance(section, dict):
        return {}
    data = section.get("data")
    return data if isinstance(data, dict) else {}


def _direct_section(payload: dict[str, Any], name: str) -> dict[str, Any]:
    value = payload.get(name)
    return value if isinstance(value, dict) else {}


def failure_backoff_seconds(consecutive_failures: int) -> int:
    """Return bounded exponential delay for repeated Overview failures."""

    exponent = max(0, min(consecutive_failures - 1, 8))
    return min(MAX_POLL_SECONDS, POLL_SECONDS * (2**exponent))


def should_fail_open(display_on: bool, consecutive_failures: int) -> bool:
    """Wake a powered-down display when state cannot be observed safely."""

    return not display_on and consecutive_failures >= FAIL_OPEN_AFTER


def set_display_power(on: bool) -> bool:
    action = "on" if on else "off"
    result = subprocess.run(
        ["xset", "dpms", "force", action],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or "unknown xset failure").strip()
        print(f"display power {action} failed: {detail}", flush=True)
        return False
    print(f"display power set: {action}", flush=True)
    return True


def main() -> int:
    previous_signature = ""
    last_activity = time.monotonic()
    display_on = True
    consecutive_failures = 0
    last_error_log = 0.0
    suppressed_errors = 0
    while True:
        delay = POLL_SECONDS
        try:
            overview = fetch_overview()
            consecutive_failures = 0
            suppressed_errors = 0
            signature = operational_signature(overview)
            if signature != previous_signature or keep_awake(overview):
                previous_signature = signature
                last_activity = time.monotonic()
            should_be_on = time.monotonic() - last_activity < IDLE_SECONDS
            if should_be_on != display_on:
                if set_display_power(should_be_on):
                    display_on = should_be_on
        except Exception as exc:
            consecutive_failures += 1
            delay = failure_backoff_seconds(consecutive_failures)
            if should_fail_open(display_on, consecutive_failures):
                if set_display_power(True):
                    display_on = True
                    last_activity = time.monotonic()
            now = time.monotonic()
            if now - last_error_log >= ERROR_LOG_INTERVAL_SECONDS:
                suffix = f" ({suppressed_errors} similar errors suppressed)" if suppressed_errors else ""
                print(
                    f"display power poll failed: {exc}; retrying in {delay}s{suffix}",
                    flush=True,
                )
                last_error_log = now
                suppressed_errors = 0
            else:
                suppressed_errors += 1
        time.sleep(delay)


if __name__ == "__main__":
    raise SystemExit(main())
