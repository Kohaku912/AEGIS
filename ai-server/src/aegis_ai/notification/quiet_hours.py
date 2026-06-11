"""Quiet Hours — defers non-critical notifications during quiet periods."""

from __future__ import annotations

import time
from typing import Any


class QuietHoursManager:
    """Manages quiet hours for notifications.

    Usage:
        qh = QuietHoursManager(enabled=True, start="22:00", end="08:00")
        if qh.is_quiet():
            # Defer non-critical notifications
    """

    def __init__(
        self,
        enabled: bool = False,
        start: str = "22:00",
        end: str = "08:00",
        settings_store: Any = None,
    ) -> None:
        self._enabled = enabled
        self._start = start
        self._end = end
        self._settings = settings_store
        self._load_from_settings()

    def is_quiet(self) -> bool:
        """Check if current time is within quiet hours."""
        if not self._enabled:
            return False

        now = time.localtime()
        current_minutes = now.tm_hour * 60 + now.tm_min

        start_minutes = self._parse_time(self._start)
        end_minutes = self._parse_time(self._end)

        if start_minutes <= end_minutes:
            # Same day range (e.g., 09:00 - 17:00)
            return start_minutes <= current_minutes <= end_minutes
        else:
            # Overnight range (e.g., 22:00 - 08:00)
            return current_minutes >= start_minutes or current_minutes <= end_minutes

    def _parse_time(self, time_str: str) -> int:
        """Parse HH:MM string to minutes since midnight."""
        try:
            parts = time_str.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except (ValueError, IndexError):
            return 0

    def _load_from_settings(self) -> None:
        """Load quiet hours from settings."""
        if not self._settings:
            return
        try:
            settings = self._settings.get()
            self._enabled = settings.notifications.quiet_hours_enabled
            self._start = settings.notifications.quiet_hours_start
            self._end = settings.notifications.quiet_hours_end
        except Exception:
            pass
