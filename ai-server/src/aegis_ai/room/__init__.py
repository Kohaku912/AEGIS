"""Room Server — IoT device control and sensor monitoring.

Provides:
- MqttSensorProvider: MQTT-based sensor data
- MqttActuatorProvider: MQTT-based device control
- MockSensorProvider: Mock data for testing
- MockActuatorProvider: Mock control for testing
"""

from aegis_ai.room.mqtt_provider import MqttSensorProvider  # noqa: F401
