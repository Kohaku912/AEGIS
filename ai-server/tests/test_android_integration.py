from __future__ import annotations

import json
from pathlib import Path


def test_android_manager_unavailable_returns_explicit_code(tmp_path):
    from aegis_ai.integrations.android.manager import AndroidServerManager

    manager = AndroidServerManager(data_dir=str(tmp_path), host="127.0.0.1", port=9)
    result = manager.invoke_capability("android-server.device.get_status", {})

    assert result["code"] == "ANDROID_SERVER_UNAVAILABLE"
    assert result["capability_id"] == "android-server.device.get_status"


def test_android_manager_rejects_unregistered_capability(tmp_path):
    from aegis_ai.integrations.android.manager import AndroidServerManager

    manager = AndroidServerManager(data_dir=str(tmp_path), host="127.0.0.1", port=9)
    result = manager.invoke_capability("android-server.shell.execute", {})

    assert result["code"] == "UNREGISTERED_ANDROID_CAPABILITY"


def test_android_manager_reports_missing_permission(tmp_path):
    from aegis_ai.integrations.android.manager import AndroidServerManager

    manager = AndroidServerManager(data_dir=str(tmp_path), host="127.0.0.1", port=9)
    manager._permission_status["accessibility"] = False

    result = manager.invoke_capability("android-server.ui.tap", {"x": 1, "y": 2})

    assert result["code"] == "ANDROID_PERMISSION_MISSING"
    assert result["missing_permissions"] == ["accessibility"]


def test_android_device_registry_requires_pairing_token(tmp_path):
    from aegis_ai.integrations.android.device_registry import AndroidDeviceRegistry

    registry = AndroidDeviceRegistry(data_dir=str(tmp_path), pairing_token="secret")

    assert not registry.verify_and_authorize(device_id="phone", pairing_token="wrong")
    assert registry.verify_and_authorize(device_id="phone", pairing_token="secret")
    assert registry.is_authorized("phone", "secret")


def test_android_ui_input_manifests_require_approval() -> None:
    manifest_dir = Path(__file__).resolve().parents[1] / "capabilities" / "builtin" / "android-server" / "ui"

    for filename in ("tap.json", "swipe.json", "type_text.json"):
        manifest = json.loads((manifest_dir / filename).read_text(encoding="utf-8"))
        assert manifest["risk"]["level"] == "approval_required"
        assert manifest["risk"]["requires_approval"] is True


def test_android_status_reports_persisted_connection_metrics(tmp_path) -> None:
    from aegis_ai.integrations.android.manager import AndroidServerManager

    manager = AndroidServerManager(
        data_dir=str(tmp_path),
        host="127.0.0.1",
        port=9,
        pairing_token="test-pairing-token",
    )
    manager.device_registry.verify_and_authorize(
        device_id="phone",
        pairing_token="test-pairing-token",
        metadata={"reconnect_count": "4", "heartbeat_failure_count": "2"},
    )
    manager._connection_metrics.update({"reconnect_count": 5, "heartbeat_failure_count": 1})

    status = manager.get_status()

    assert status["reconnect_count"] == 5
    assert status["heartbeat_failure_count"] == 2
