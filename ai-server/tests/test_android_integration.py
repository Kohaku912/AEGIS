from __future__ import annotations


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
