from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

import grpc
import pytest

from generated.aegis import ai_server_pb2_grpc, common_pb2


pytestmark = [
    pytest.mark.android_local,
    pytest.mark.skipif(
        os.getenv("AEGIS_ANDROID_LOCAL", "") != "1",
        reason="Set AEGIS_ANDROID_LOCAL=1 to run real Android device tests.",
    ),
]


ADB = os.getenv("ADB", "adb")
CORE_HTTP = os.getenv("AEGIS_CORE_HTTP", "http://127.0.0.1:8090")
CORE_GRPC = os.getenv("AEGIS_CORE_GRPC", "127.0.0.1:50051")
ANDROID_HOST = os.getenv("AEGIS_ANDROID_TEST_HOST", "192.168.50.175")
ANDROID_PORT = int(os.getenv("AEGIS_ANDROID_TEST_PORT", "50051"))


def _run(*args: str, timeout: int = 20) -> str:
    result = subprocess.run(
        [ADB, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    return (result.stdout or result.stderr or "").strip()


def _android_status() -> dict:
    with urllib.request.urlopen(f"{CORE_HTTP}/api/android/status", timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _invoke(capability_id: str, params: dict | None = None) -> dict:
    channel = grpc.insecure_channel(CORE_GRPC)
    stub = ai_server_pb2_grpc.AIServerStub(channel)
    response = stub.InvokeTool(
        common_pb2.ToolInvocationRequest(
            capability_id=capability_id,
            invocation_id=f"android-local-{capability_id.split('.')[-1]}-{int(time.time() * 1000)}",
            caller="pytest-android-local",
            params_json=json.dumps(params or {}),
            is_approved=True,
        ),
        timeout=30,
    )
    output = json.loads(response.output_json or "{}")
    return {
        "status_code": response.status.code,
        "status_message": response.status.message,
        "error": response.error,
        "output": output,
    }


def test_adb_device_and_app_installed() -> None:
    devices = _run("devices", "-l")
    packages = _run("shell", "pm", "list", "packages")

    assert any(" device " in f" {line} " for line in devices.splitlines()), devices
    assert "package:com.aegis.android" in packages


def test_android_reverse_stream_connects_or_reports_actionable_failure() -> None:
    _run("shell", "am", "force-stop", "com.aegis.android")
    _run(
        "shell",
        "am",
        "start",
        "-n",
        "com.aegis.android/.MainActivity",
        "--es",
        "host",
        ANDROID_HOST,
        "--ei",
        "port",
        str(ANDROID_PORT),
        "--ez",
        "auto_connect",
        "true",
    )

    deadline = time.time() + 45
    status = {}
    while time.time() < deadline:
        status = _android_status()
        if status.get("online"):
            break
        time.sleep(3)

    assert status.get("online") is True, status
    assert status.get("connection_mode") == "reverse_stream"
    assert status.get("device_model")


def test_android_observe_capabilities_return_real_device_data() -> None:
    required = [
        "android-server.device.get_status",
        "android-server.permissions.get_status",
        "android-server.accessibility.get_status",
        "android-server.notification.get_notifications",
    ]
    results = {cap: _invoke(cap) for cap in required}

    assert results["android-server.device.get_status"]["status_code"] == 0
    assert results["android-server.device.get_status"]["output"].get("connection_mode") == "reverse_stream"
    assert results["android-server.permissions.get_status"]["status_code"] == 0
    assert results["android-server.accessibility.get_status"]["status_code"] == 0
    notification = results["android-server.notification.get_notifications"]
    if notification["status_code"] != 0:
        assert notification["output"].get("code") in {"ANDROID_PERMISSION_MISSING", "ANDROID_SCREEN_LOCKED"}


def test_android_ui_tree_reports_data_or_permission_gap() -> None:
    result = _invoke("android-server.screen.get_ui_tree", {"include_invisible": False})
    output = result["output"]

    if result["status_code"] == 0:
        assert "root" in output
        return

    assert output.get("code") in {"ANDROID_PERMISSION_MISSING", "ANDROID_SCREEN_LOCKED"}
    if output.get("code") == "ANDROID_PERMISSION_MISSING":
        assert "accessibility" in output.get("missing_permissions", [])


def test_android_ui_input_manifests_require_approval() -> None:
    root = Path(__file__).resolve().parents[1] / "capabilities" / "builtin" / "android-server" / "ui"
    for name in ("tap.json", "swipe.json", "type_text.json"):
        manifest = json.loads((root / name).read_text(encoding="utf-8"))
        assert manifest["risk"]["level"] == "approval_required"
        assert manifest["risk"]["requires_approval"] is True
