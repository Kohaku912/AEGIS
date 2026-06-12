"""Tests for Autonomous Loop."""

from __future__ import annotations

import tempfile
import shutil

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.desire.desire_system import DesireSystem


class TestAutonomousLoop:
    """Autonomous loop tests."""

    def test_init(self):
        """System initializes."""
        tmpdir = tempfile.mkdtemp()
        try:
            loop = AutonomousLoop(data_dir=f"{tmpdir}/loop")
            status = loop.get_status()
            assert status["running"] == False
            assert status["execution_count"] == 0
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_get_low_desires(self):
        """Low desires are detected."""
        tmpdir = tempfile.mkdtemp()
        try:
            desire = DesireSystem(
                data_dir=f"{tmpdir}/desires",
                initial_values={"curiosity": 2.0, "safety": 8.0},
            )
            loop = AutonomousLoop(
                data_dir=f"{tmpdir}/loop",
                desire_system=desire,
                desire_threshold=4.0,
            )
            low = loop._get_low_desires()
            assert len(low) == 1
            assert low[0]["name"] == "curiosity"
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_generate_default_tasks(self):
        """Default tasks are generated."""
        tmpdir = tempfile.mkdtemp()
        try:
            loop = AutonomousLoop(data_dir=f"{tmpdir}/loop")
            low_desires = [
                {"name": "curiosity", "value": 2.0, "gap": 2.0},
                {"name": "social_connectivity", "value": 3.0, "gap": 1.0},
            ]
            tasks = loop._generate_default_tasks(low_desires)
            assert len(tasks) == 2
            assert tasks[0]["desire"] == "curiosity"
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_trigger_now(self):
        """Manual trigger works."""
        tmpdir = tempfile.mkdtemp()
        try:
            loop = AutonomousLoop(data_dir=f"{tmpdir}/loop")
            status = loop.trigger_now()
            assert "next_run_ms" in status
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_schedule_next(self):
        """Next run is scheduled."""
        tmpdir = tempfile.mkdtemp()
        try:
            loop = AutonomousLoop(data_dir=f"{tmpdir}/loop")
            loop._schedule_next(1800)
            status = loop.get_status()
            assert status["seconds_until_next"] > 0
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
