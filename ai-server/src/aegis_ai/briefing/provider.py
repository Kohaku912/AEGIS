"""Daily Briefing Provider — generates daily summaries.

Collects:
- Calendar events (if available)
- Weather data (OpenMeteo API, free, no key)
- Pending tasks
- Recent notifications
- System health

Usage:
    provider = DailyBriefingProvider(context_builder=ctx)
    briefing = provider.generate_briefing()
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.llm.memory_context import build_shared_memory_context

logger = logging.getLogger("aegis_ai.briefing.provider")
_DATA_DIR = str(Path(__file__).resolve().parent.parent.parent / "data")

# ── Weather codes (WMO) → human-readable descriptions ──────────
_WEATHER_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

# ── Default location (Tokyo) ────────────────────────────────────
_DEFAULT_LATITUDE = 35.6762
_DEFAULT_LONGITUDE = 139.6503
_DEFAULT_LOCATION_NAME = "Tokyo"

# ── Cache TTL (seconds) ────────────────────────────────────────
_WEATHER_CACHE_TTL = 300  # 5 minutes


@dataclass
class BriefingSection:
    """A section of the daily briefing."""
    title: str = ""
    content: str = ""
    priority: str = "normal"  # low, normal, high
    source: str = ""


@dataclass
class DailyBriefing:
    """A complete daily briefing."""
    date: str = ""
    sections: list[BriefingSection] = field(default_factory=list)
    summary: str = ""
    generated_at_ms: int = 0


class DailyBriefingProvider:
    """Generates daily briefings from available data sources."""

    def __init__(
        self,
        context_builder: Any = None,
        memory: Any = None,
        llm_provider: Any = None,
        notification_store: Any = None,
        settings_store: Any = None,
    ) -> None:
        self._context = context_builder
        self._memory = memory
        self._llm = llm_provider
        self._notifications = notification_store
        self._settings = settings_store
        self._weather_cache: dict[str, Any] = {}
        self._weather_cache_ts: float = 0.0

    def generate_briefing(self) -> DailyBriefing:
        """Generate a daily briefing."""
        briefing = DailyBriefing(
            date=time.strftime("%Y-%m-%d"),
            generated_at_ms=int(time.time() * 1000),
        )

        # Collect sections
        sections = []

        # System health
        sections.append(self._get_system_health())

        # Recent notifications
        sections.append(self._get_recent_notifications())

        # Pending tasks
        sections.append(self._get_pending_tasks())

        # Memory highlights
        sections.append(self._get_memory_highlights())

        # Weather (placeholder)
        sections.append(self._get_weather())

        # Calendar (placeholder)
        sections.append(self._get_calendar())

        briefing.sections = [s for s in sections if s.content]

        # Generate summary
        if self._llm:
            briefing.summary = self._generate_summary(briefing)
        else:
            briefing.summary = self._generate_simple_summary(briefing)

        return briefing

    def _get_system_health(self) -> BriefingSection:
        """Get system health summary from StatusManager when available."""
        snapshot = None
        try:
            from aegis_ai.runtime import get_runtime

            status_manager = getattr(get_runtime(), "status_manager", None)
            if status_manager is not None and hasattr(status_manager, "get_snapshot"):
                snapshot = status_manager.get_snapshot()
        except Exception:
            snapshot = None
        if isinstance(snapshot, dict) and snapshot:
            lines = []
            for name, info in snapshot.items():
                if isinstance(info, dict):
                    lines.append(f"- {name}: {info.get('status', 'unknown')}")
                else:
                    lines.append(f"- {name}: {info}")
            content = "\n".join(lines)
        else:
            content = "Status snapshot unavailable."
        return BriefingSection(
            title="System Health",
            content=content,
            priority="normal",
            source="system",
        )

    def _get_recent_notifications(self) -> BriefingSection:
        """Get recent notifications."""
        if self._notifications:
            try:
                recent = self._notifications.get_recent(limit=5)
                if recent:
                    items = [f"- {n.get('title', 'No title')}" for n in recent]
                    return BriefingSection(
                        title="Recent Notifications",
                        content="\n".join(items),
                        priority="normal",
                        source="notifications",
                    )
            except Exception:
                pass
        return BriefingSection(
            title="Recent Notifications",
            content="No recent notifications.",
            priority="low",
            source="notifications",
        )

    def _get_pending_tasks(self) -> BriefingSection:
        """Get pending tasks."""
        return BriefingSection(
            title="Pending Tasks",
            content="No pending tasks.",
            priority="normal",
            source="scheduler",
        )

    def _get_memory_highlights(self) -> BriefingSection:
        """Get memory highlights."""
        if self._memory:
            try:
                facts = self._memory.search("important", limit=3)
                if facts:
                    items = [f"- {f.content}" for f in facts]
                    return BriefingSection(
                        title="Memory Highlights",
                        content="\n".join(items),
                        priority="low",
                        source="memory",
                    )
            except Exception:
                pass
        return BriefingSection(
            title="Memory Highlights",
            content="No highlights.",
            priority="low",
            source="memory",
        )

    def _get_weather(self) -> BriefingSection:
        """Fetch current weather from OpenMeteo (free, no API key)."""
        now = time.time()
        if self._weather_cache and (now - self._weather_cache_ts) < _WEATHER_CACHE_TTL:
            return self._build_weather_section(self._weather_cache)

        lat, lon, location = self._resolve_location()
        try:
            import httpx

            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "timezone": "auto",
            }
            resp = httpx.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            current = data.get("current", {})
            weather = {
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "weather_code": current.get("weather_code", 0),
                "wind_speed": current.get("wind_speed_10m"),
                "location": location,
                "unit": data.get("current_units", {}).get("temperature_2m", "°C"),
            }
            self._weather_cache = weather
            self._weather_cache_ts = now
            return self._build_weather_section(weather)
        except Exception as exc:
            logger.debug("Weather fetch failed: %s", exc)
            return BriefingSection(
                title="Weather",
                content=f"Weather data unavailable ({exc}).",
                priority="low",
                source="weather",
            )

    def _resolve_location(self) -> tuple[float, float, str]:
        if self._settings:
            try:
                s = self._settings.get()
                w = getattr(s, "weather", None)
                if w:
                    return (
                        getattr(w, "latitude", _DEFAULT_LATITUDE),
                        getattr(w, "longitude", _DEFAULT_LONGITUDE),
                        getattr(w, "location_name", _DEFAULT_LOCATION_NAME),
                    )
            except Exception:
                pass
        return _DEFAULT_LATITUDE, _DEFAULT_LONGITUDE, _DEFAULT_LOCATION_NAME

    @staticmethod
    def _build_weather_section(w: dict[str, Any]) -> BriefingSection:
        code = int(w.get("weather_code", 0))
        condition = _WEATHER_CODES.get(code, f"Code {code}")
        temp = w.get("temperature", "?")
        unit = w.get("unit", "°C")
        humidity = w.get("humidity", "?")
        wind = w.get("wind_speed", "?")
        location = w.get("location", "Unknown")
        content = f"{condition}, {temp}{unit}, humidity {humidity}%, wind {wind} km/h ({location})"
        return BriefingSection(title="Weather", content=content, priority="normal", source="weather")

    def _get_calendar(self) -> BriefingSection:
        """Load today's events from local calendar JSON."""
        try:
            from datetime import date, datetime
            import json

            cal_path = Path(_DATA_DIR).parent / "config" / "calendar.json"
            if not cal_path.exists():
                return BriefingSection(
                    title="Calendar",
                    content="No calendar configured. Add events to config/calendar.json.",
                    priority="low",
                    source="calendar",
                )
            with open(cal_path, encoding="utf-8") as f:
                events = json.load(f)
            today = date.today().isoformat()
            today_events = [
                e for e in events
                if isinstance(e, dict) and e.get("date") == today
            ]
            if not today_events:
                return BriefingSection(
                    title="Calendar",
                    content="No events today.",
                    priority="low",
                    source="calendar",
                )
            items = []
            for e in sorted(today_events, key=lambda x: x.get("time", "")):
                time_str = e.get("time", "All day")
                title = e.get("title", "Untitled")
                items.append(f"- {time_str}: {title}")
            return BriefingSection(
                title="Calendar",
                content="\n".join(items),
                priority="normal",
                source="calendar",
            )
        except Exception as exc:
            logger.debug("Calendar load failed: %s", exc)
            return BriefingSection(
                title="Calendar",
                content=f"Calendar error: {exc}",
                priority="low",
                source="calendar",
            )

    def _generate_summary(self, briefing: DailyBriefing) -> str:
        """Generate summary using LLM."""
        try:
            content = "\n\n".join([f"## {s.title}\n{s.content}" for s in briefing.sections])
            memory_context = build_shared_memory_context(
                query="daily briefing summary",
                data_dir=_DATA_DIR,
                profile="summary",
            )
            prompt = f"Summarize this daily briefing concisely:\n\n{content}"
            if memory_context.text:
                prompt = f"Shared memory context:\n{memory_context.text}\n\n{prompt}"
            result = self._llm.generate(
                prompt=prompt,
                system_prompt="You are AEGIS, a helpful AI assistant. Provide a brief daily summary.",
                max_tokens=300,
                context_meta=memory_context.audit_detail(),
            )
            if result.success:
                return result.content
        except Exception as e:
            logger.warning("LLM summary failed: %s", e)
        return self._generate_simple_summary(briefing)

    def _generate_simple_summary(self, briefing: DailyBriefing) -> str:
        """Generate simple summary without LLM."""
        high_priority = [s for s in briefing.sections if s.priority == "high"]
        if high_priority:
            return f"Daily briefing for {briefing.date}: {len(high_priority)} high priority items require attention."
        return f"Daily briefing for {briefing.date}: All systems normal. {len(briefing.sections)} sections available."
