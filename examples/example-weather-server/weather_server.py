"""Example Weather Server — demonstrates READ_ONLY capability with AEGIS SDK.

This server provides weather data as read-only capabilities.
No approval required, no side effects.
"""

from __future__ import annotations

import time
from typing import Any

from aegis_sdk import (
    EventClient,
    RegistrationClient,
    define_capability,
)
from aegis_schema.models import EventPriority, RiskLevel, ServerType


# ── Capabilities ─────────────────────────────────────────────

GET_FORECAST = define_capability(
    server_prefix="weather",
    action="get_forecast",
    name="Get Weather Forecast",
    description="Retrieve weather forecast for a location.",
    risk_level=RiskLevel.READ_ONLY,
    input_schema={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name"},
        },
        "required": ["location"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "temp_c": {"type": "number"},
            "condition": {"type": "string"},
            "humidity_pct": {"type": "number"},
        },
    },
    tags=["weather", "observe", "read_only"],
)

GET_CURRENT_WEATHER = define_capability(
    server_prefix="weather",
    action="get_current",
    name="Get Current Weather",
    description="Get current weather conditions.",
    risk_level=RiskLevel.READ_ONLY,
    input_schema={
        "type": "object",
        "properties": {
            "location": {"type": "string"},
        },
    },
    output_schema={
        "type": "object",
        "properties": {
            "temp_c": {"type": "number"},
            "condition": {"type": "string"},
        },
    },
    tags=["weather", "observe", "read_only"],
)

ALL_CAPABILITIES = [GET_FORECAST, GET_CURRENT_WEATHER]


# ── Mock Weather Data ────────────────────────────────────────

MOCK_WEATHER = {
    "tokyo": {"temp_c": 22.5, "condition": "partly_cloudy", "humidity_pct": 65},
    "new_york": {"temp_c": 18.0, "condition": "sunny", "humidity_pct": 45},
    "london": {"temp_c": 15.5, "condition": "rainy", "humidity_pct": 80},
}


# ── Server Implementation ────────────────────────────────────


class WeatherServer:
    """Example weather server using AEGIS SDK."""

    def __init__(self) -> None:
        self._registration = RegistrationClient(
            server_id="weather-server",
            server_type=ServerType.ROOM,
            port=50060,
        )
        self._events = EventClient(
            server_type=ServerType.ROOM,
            server_id="weather-server",
        )

    def register(self, registry: Any) -> bool:
        """Register server and capabilities with AEGIS Core."""
        if not self._registration.register_server(registry):
            return False
        return self._registration.register_capabilities(registry, ALL_CAPABILITIES) == len(ALL_CAPABILITIES)

    def get_forecast(self, location: str) -> dict[str, Any]:
        """Get weather forecast for a location."""
        location_key = location.lower().replace(" ", "_")
        data = MOCK_WEATHER.get(location_key, {"temp_c": 20.0, "condition": "unknown", "humidity_pct": 50})
        return {
            "location": location,
            "temp_c": data["temp_c"],
            "condition": data["condition"],
            "humidity_pct": data["humidity_pct"],
            "forecast_at_ms": int(time.time() * 1000),
        }

    def get_current(self, location: str) -> dict[str, Any]:
        """Get current weather."""
        return self.get_forecast(location)

    def publish_weather_update(self, event_bus: Any, location: str, temp_c: float) -> bool:
        """Publish a weather update event."""
        return self._events.publish(
            event_bus,
            "weather.forecast_updated",
            {"location": location, "temp_c": temp_c},
            severity=2,
            priority=EventPriority.BACKGROUND,
        )
