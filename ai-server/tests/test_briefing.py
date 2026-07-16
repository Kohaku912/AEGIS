"""Tests for the daily briefing provider."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aegis_ai.briefing.provider import (
    DailyBriefingProvider,
    BriefingSection,
    _WEATHER_CODES,
    _DEFAULT_LATITUDE,
    _DEFAULT_LONGITUDE,
)


class TestWeatherCodes:
    def test_clear_sky(self):
        assert _WEATHER_CODES[0] == "Clear sky"

    def test_heavy_rain(self):
        assert _WEATHER_CODES[65] == "Heavy rain"

    def test_thunderstorm(self):
        assert _WEATHER_CODES[95] == "Thunderstorm"


class TestGetWeather:
    def test_cache_hit(self):
        provider = DailyBriefingProvider()
        provider._weather_cache = {
            "temperature": 25,
            "humidity": 60,
            "weather_code": 0,
            "wind_speed": 10,
            "location": "Tokyo",
            "unit": "°C",
        }
        provider._weather_cache_ts = time.time()
        section = provider._get_weather()
        assert "Clear sky" in section.content
        assert "25" in section.content
        assert "Tokyo" in section.content

    def test_cache_expired(self):
        provider = DailyBriefingProvider()
        provider._weather_cache = {"temperature": 20}
        provider._weather_cache_ts = time.time() - 600

        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "current": {
                "temperature_2m": 30,
                "relative_humidity_2m": 50,
                "weather_code": 3,
                "wind_speed_10m": 15,
            },
            "current_units": {"temperature_2m": "°C"},
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.get", return_value=mock_resp):
            section = provider._get_weather()
            assert "Overcast" in section.content
            assert "30" in section.content

    def test_network_error(self):
        provider = DailyBriefingProvider()
        with patch("httpx.get", side_effect=Exception("Network error")):
            section = provider._get_weather()
            assert "unavailable" in section.content.lower()

    def test_default_location(self):
        lat, lon, name = DailyBriefingProvider()._resolve_location()
        assert lat == _DEFAULT_LATITUDE
        assert lon == _DEFAULT_LONGITUDE
        assert name == "Tokyo"


class TestGetCalendar:
    def test_no_calendar_file(self, tmp_path):
        provider = DailyBriefingProvider()
        with patch("aegis_ai.briefing.provider._DATA_DIR", str(tmp_path)):
            section = provider._get_calendar()
            assert "No calendar configured" in section.content

    def test_empty_calendar(self, tmp_path):
        import json

        config_dir = tmp_path.parent / "config"
        config_dir.mkdir(exist_ok=True)
        cal_file = config_dir / "calendar.json"
        cal_file.write_text("[]", encoding="utf-8")

        provider = DailyBriefingProvider()
        with patch("aegis_ai.briefing.provider._DATA_DIR", str(tmp_path)):
            section = provider._get_calendar()
            assert "No events today" in section.content

    def test_today_events(self, tmp_path):
        import json
        from datetime import date

        config_dir = tmp_path.parent / "config"
        config_dir.mkdir(exist_ok=True)
        cal_file = config_dir / "calendar.json"
        today = date.today().isoformat()
        events = [
            {"date": today, "time": "10:00", "title": "Meeting"},
            {"date": today, "time": "14:00", "title": "Lunch"},
        ]
        cal_file.write_text(json.dumps(events), encoding="utf-8")

        provider = DailyBriefingProvider()
        with patch("aegis_ai.briefing.provider._DATA_DIR", str(tmp_path)):
            section = provider._get_calendar()
            assert "Meeting" in section.content
            assert "Lunch" in section.content


class TestGenerateBriefing:
    def test_basic_briefing(self):
        provider = DailyBriefingProvider()
        with patch.object(provider, "_get_weather", return_value=BriefingSection(title="Weather", content="Sunny")):
            briefing = provider.generate_briefing()
            assert briefing.date
            assert len(briefing.sections) > 0
            assert briefing.summary
