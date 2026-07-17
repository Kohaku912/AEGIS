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
    "AEGIS_DISPLAY_OVERVIEW_URL", "http://127.0.0.1:8090/display/overview"
)
IDLE_SECONDS = max(60, int(os.environ.get("AEGIS_DISPLAY_IDLE_SECONDS", "600")))
POLL_SECONDS = max(2, int(os.environ.get("AEGIS_DISPLAY_POLL_SECONDS", "5")))
DISPLAY_TOKEN = os.environ.get("AEGIS_DISPLAY_TOKEN", "").strip()


def fetch_overview() -> dict[str, Any]:
    headers = {"X-AEGIS-Display-Token": DISPLAY_TOKEN} if DISPLAY_TOKEN else {}
    request = urllib.request.Request(OVERVIEW_URL, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=4) as response:
        payload = json.load(response)
    return payload if isinstance(payload, dict) else {}


def operational_signature(overview: dict[str, Any]) -> str:
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


def set_display_power(on: bool) -> None:
    action = "on" if on else "off"
    subprocess.run(
        ["xset", "dpms", "force", action],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    previous_signature = ""
    last_activity = time.monotonic()
    display_on = True
    while True:
        try:
            overview = fetch_overview()
            signature = operational_signature(overview)
            if signature != previous_signature or keep_awake(overview):
                previous_signature = signature
                last_activity = time.monotonic()
            should_be_on = time.monotonic() - last_activity < IDLE_SECONDS
            if should_be_on != display_on:
                set_display_power(should_be_on)
                display_on = should_be_on
        except Exception as exc:
            print(f"display power poll failed: {exc}", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
