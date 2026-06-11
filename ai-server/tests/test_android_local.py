"""Android Server Local Tests — tests using real ADB device.

These tests require:
- ADB installed and in PATH
- Android device connected via USB with USB debugging enabled
- Notification access enabled on the device (for notification tests)

Run with: pytest -m android_local -v

Architecture reference: docs/architecture.md §3.3
"""

from __future__ import annotations

import json
import subprocess

import pytest

from aegis_schema.models import EventPriority, ServerType
from android_server_client import ADBAndroidProvider, AndroidServerClient
from event_bus import EventBus
from tool_registry import ToolRegistry


def _adb_available() -> bool:
    """Check if ADB can reach a device."""
    try:
        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True, timeout=5, check=False,
        )
        lines = result.stdout.strip().split("\n")
        return any("\tdevice" in line for line in lines[1:])
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


pytestmark = pytest.mark.skipif(
    not _adb_available(),
    reason="ADB device not available",
)


# ═══════════════════════════════════════════════════════════════
# ADB Provider Tests
# ═══════════════════════════════════════════════════════════════


class TestADBProvider:
    """Test ADBAndroidProvider with real device."""

    def test_is_available(self):
        """ADB provider detects connected device."""
        provider = ADBAndroidProvider()
        assert provider.is_available() is True

    def test_get_device_info(self):
        """ADB provider returns real device info."""
        provider = ADBAndroidProvider()
        info = provider.get_device_info()

        assert info["model"] != "unknown"
        assert info["manufacturer"] != "unknown"
        assert info["android_version"] != "unknown"
        assert info["sdk_version"] > 0
        print(f"Device: {info['manufacturer']} {info['model']}, Android {info['android_version']}")

    def test_get_current_app(self):
        """ADB provider returns current foreground app."""
        provider = ADBAndroidProvider()
        app = provider.get_current_app()

        # Should return some package name (even if launcher)
        assert app["package_name"] != ""
        print(f"Current app: {app['package_name']}")

    def test_get_notifications(self):
        """ADB provider returns notifications (may be empty if none)."""
        provider = ADBAndroidProvider()
        notifications = provider.get_notifications(max_count=5)

        # Notifications may or may not be present
        assert isinstance(notifications, list)
        print(f"Notifications: {len(notifications)} found")
        for n in notifications[:3]:
            print(f"  - [{n.get('app_name', '?')}] {n.get('title', '?')}")


# ═══════════════════════════════════════════════════════════════
# Full Stack Integration with Real Device
# ═══════════════════════════════════════════════════════════════


class TestADBIntegration:
    """Integration tests using ADB provider with AEGIS Core."""

    def test_register_with_adb_provider(self):
        """Android Server registers with AEGIS Core using ADB provider."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = ADBAndroidProvider()
        client = AndroidServerClient(bus, registry, provider)

        result = client.register()
        assert result is True
        assert client.is_registered is True

        server = registry.get_server("android-server-main")
        assert server is not None
        assert server.server_type == ServerType.ANDROID

    def test_push_notification_event_with_adb(self):
        """Android Server can push notification events to EventBus."""
        bus = EventBus()
        registry = ToolRegistry()
        provider = ADBAndroidProvider()
        client = AndroidServerClient(bus, registry, provider)
        client.register()

        received = []
        bus.subscribe(lambda e: received.append(e))

        # Push a test notification event
        result = client.push_notification_event(
            "TestApp", "Test Title", "Test Text",
            package_name="com.test.app",
        )
        assert result is True
        assert len(received) == 1
        assert received[0].source_server_type == ServerType.ANDROID

    def test_invoke_get_device_info_via_broker(self):
        """android.get_device_info can be invoked through ToolBroker."""
        from tool_broker import ToolBroker
        from policy_engine import create_default_policy_engine

        bus = EventBus()
        registry = ToolRegistry()
        policy = create_default_policy_engine()
        broker = ToolBroker(registry, policy)
        provider = ADBAndroidProvider()
        client = AndroidServerClient(bus, registry, provider)
        client.register()

        # Register mock executor that calls real ADB
        def mock_android_executor(cap, params):
            if cap.id == "android.get_device_info":
                return provider.get_device_info()
            return {"mock": True}

        broker.register_mock("android.", mock_android_executor)

        result = broker.invoke_tool("android.get_device_info")
        assert result.success is True
        assert result.output["model"] != "unknown"
