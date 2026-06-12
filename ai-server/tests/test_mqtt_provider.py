"""Tests for Room Server MQTT Provider."""

from __future__ import annotations

import pytest

from aegis_ai.room.mqtt_provider import MqttSensorProvider


class TestMqttSensorProvider:
    """MQTT sensor provider tests."""

    def test_provider_creation(self):
        """Provider can be created."""
        provider = MqttSensorProvider(broker_host="localhost", broker_port=1883)
        assert provider is not None

    def test_not_connected_by_default(self):
        """Provider is not connected by default."""
        provider = MqttSensorProvider()
        assert provider.is_available() is False

    def test_get_temperature_mock(self):
        """Returns mock temperature when not connected."""
        provider = MqttSensorProvider()
        temp = provider.get_temperature()
        assert "temperature_c" in temp
        assert temp["source"] == "mock"

    def test_get_humidity_mock(self):
        """Returns mock humidity when not connected."""
        provider = MqttSensorProvider()
        humidity = provider.get_humidity()
        assert "humidity_pct" in humidity
        assert humidity["source"] == "mock"

    def test_get_brightness_mock(self):
        """Returns mock brightness when not connected."""
        provider = MqttSensorProvider()
        brightness = provider.get_brightness()
        assert "brightness_lux" in brightness
        assert brightness["source"] == "mock"

    def test_get_motion_status_mock(self):
        """Returns mock motion status when not connected."""
        provider = MqttSensorProvider()
        motion = provider.get_motion_status()
        assert "motion_detected" in motion
        assert motion["source"] == "mock"

    def test_get_environment_mock(self):
        """Returns mock environment when not connected."""
        provider = MqttSensorProvider()
        env = provider.get_environment()
        assert "temperature_c" in env
        assert "humidity_pct" in env
        assert "brightness_lux" in env
        assert env["source"] == "mock"

    def test_list_sensors(self):
        """Returns sensor list."""
        provider = MqttSensorProvider()
        sensors = provider.list_sensors()
        assert len(sensors) >= 4
        assert any(s["sensor_type"] == "temperature" for s in sensors)

    def test_publish_fails_when_disconnected(self):
        """Publish fails when not connected."""
        provider = MqttSensorProvider()
        result = provider.publish("test", {"value": 1})
        assert result is False
