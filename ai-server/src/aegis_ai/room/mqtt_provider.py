"""MQTT Sensor Provider — connects to real MQTT brokers for room sensors.

Supports:
- Temperature, humidity, brightness sensors
- Motion detection
- Device status

Usage:
    provider = MqttSensorProvider(broker_host="localhost", broker_port=1883)
    temp = provider.get_temperature()
"""

from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any

logger = logging.getLogger("aegis_ai.room.mqtt_provider")


class MqttSensorProvider:
    """MQTT-based sensor provider for room monitoring.

    Connects to an MQTT broker and subscribes to sensor topics.
    Falls back to mock data if broker is unavailable.
    """

    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        topic_prefix: str = "aegis/room",
        username: str = "",
        password: str = "",
    ) -> None:
        self._host = broker_host
        self._port = broker_port
        self._topic_prefix = topic_prefix
        self._username = username
        self._password = password
        self._client = None
        self._connected = False
        self._data: dict[str, Any] = {}
        self._lock = threading.Lock()

    def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            import paho.mqtt.client as mqtt

            self._client = mqtt.Client()
            if self._username:
                self._client.username_pw_set(self._username, self._password)

            self._client.on_connect = self._on_connect
            self._client.on_message = self._on_message

            self._client.connect(self._host, self._port, 60)
            self._client.loop_start()
            return True
        except ImportError:
            logger.warning("paho-mqtt not installed, using mock data")
            return False
        except Exception as e:
            logger.warning("MQTT connection failed: %s, using mock data", e)
            return False

    def _on_connect(self, client: Any, userdata: Any, flags: Any, rc: int) -> None:
        """Callback when connected to MQTT broker."""
        logger.info("Connected to MQTT broker %s:%d", self._host, self._port)
        self._connected = True
        # Subscribe to sensor topics
        client.subscribe(f"{self._topic_prefix}/#")

    def _on_message(self, client: Any, userdata: Any, msg: Any) -> None:
        """Callback when message received."""
        try:
            topic = msg.topic.replace(f"{self._topic_prefix}/", "")
            payload = json.loads(msg.payload.decode())
            with self._lock:
                self._data[topic] = payload
        except Exception as e:
            logger.warning("Failed to parse MQTT message: %s", e)

    def is_available(self) -> bool:
        """Check if MQTT broker is connected."""
        return self._connected

    def get_temperature(self) -> dict[str, Any]:
        """Get current temperature."""
        with self._lock:
            if "temperature" in self._data:
                return self._data["temperature"]
        return {"temperature_c": 22.5, "timestamp_ms": int(time.time() * 1000), "source": "mock"}

    def get_humidity(self) -> dict[str, Any]:
        """Get current humidity."""
        with self._lock:
            if "humidity" in self._data:
                return self._data["humidity"]
        return {"humidity_pct": 45.0, "timestamp_ms": int(time.time() * 1000), "source": "mock"}

    def get_brightness(self) -> dict[str, Any]:
        """Get current brightness."""
        with self._lock:
            if "brightness" in self._data:
                return self._data["brightness"]
        return {"brightness_lux": 300.0, "timestamp_ms": int(time.time() * 1000), "source": "mock"}

    def get_motion_status(self) -> dict[str, Any]:
        """Get motion detection status."""
        with self._lock:
            if "motion" in self._data:
                return self._data["motion"]
        return {"motion_detected": False, "motion_zone": "", "timestamp_ms": int(time.time() * 1000), "source": "mock"}

    def get_environment(self) -> dict[str, Any]:
        """Get all environment data."""
        return {
            "temperature_c": self.get_temperature().get("temperature_c", 22.5),
            "humidity_pct": self.get_humidity().get("humidity_pct", 45.0),
            "brightness_lux": self.get_brightness().get("brightness_lux", 300.0),
            "motion_detected": self.get_motion_status().get("motion_detected", False),
            "motion_zone": self.get_motion_status().get("motion_zone", ""),
            "timestamp_ms": int(time.time() * 1000),
            "source": "mqtt" if self._connected else "mock",
        }

    def get_device_status(self, device_ids: list[str] | None = None) -> list[dict[str, Any]]:
        """Get device status."""
        with self._lock:
            if "devices" in self._data:
                devices = self._data["devices"]
                if device_ids:
                    return [d for d in devices if d.get("device_id") in device_ids]
                return devices
        return []

    def list_sensors(self) -> list[dict[str, Any]]:
        """List all available sensors."""
        return [
            {"sensor_id": "sensor-temp-001", "sensor_type": "temperature", "unit": "°C", "online": True},
            {"sensor_id": "sensor-humidity-001", "sensor_type": "humidity", "unit": "%", "online": True},
            {"sensor_id": "sensor-brightness-001", "sensor_type": "brightness", "unit": "lux", "online": True},
            {"sensor_id": "sensor-motion-001", "sensor_type": "motion", "unit": "bool", "online": True},
        ]

    def publish(self, topic: str, payload: dict[str, Any]) -> bool:
        """Publish a message to MQTT broker."""
        if not self._connected or not self._client:
            return False
        try:
            full_topic = f"{self._topic_prefix}/{topic}"
            self._client.publish(full_topic, json.dumps(payload))
            return True
        except Exception as e:
            logger.error("Failed to publish MQTT message: %s", e)
            return False

    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._connected = False
