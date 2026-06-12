"""Tests for Desire System."""

from __future__ import annotations

import tempfile
import shutil

from aegis_ai.desire.desire_system import DesireSystem, DESIRE_DESCRIPTIONS


class TestDesireSystem:
    """Desire system tests."""

    def test_init(self):
        """System initializes with default desires."""
        tmpdir = tempfile.mkdtemp()
        try:
            system = DesireSystem(data_dir=tmpdir)
            desires = system.get_all_desires()
            assert len(desires) == 8  # 8 non-physiological desires
            assert "social_connectivity" in desires
            assert "curiosity" in desires
            assert "hunger" not in desires  # Excluded
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_initial_values(self):
        """Custom initial values are applied."""
        tmpdir = tempfile.mkdtemp()
        try:
            system = DesireSystem(
                data_dir=tmpdir,
                initial_values={"curiosity": 8.0, "safety": 3.0},
            )
            assert system.get_desire("curiosity").value == 8.0
            assert system.get_desire("safety").value == 3.0
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_get_context(self):
        """Context is generated."""
        tmpdir = tempfile.mkdtemp()
        try:
            system = DesireSystem(data_dir=tmpdir)
            context = system.get_context()
            assert "social_connectivity" in context
            assert "curiosity" in context
            assert "/10" in context
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_generate_tasks(self):
        """Tasks are generated for low desires."""
        tmpdir = tempfile.mkdtemp()
        try:
            system = DesireSystem(
                data_dir=tmpdir,
                initial_values={"curiosity": 2.0, "safety": 8.0},
            )
            tasks = system.generate_tasks()
            # curiosity should have a task (gap = 7-2 = 5)
            curiosity_tasks = [t for t in tasks if t["desire"] == "curiosity"]
            assert len(curiosity_tasks) == 1
            assert curiosity_tasks[0]["gap"] == 5.0
            # safety should not have a task (value >= expected)
            safety_tasks = [t for t in tasks if t["desire"] == "safety"]
            assert len(safety_tasks) == 0
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_save_load(self):
        """State persists across instances."""
        tmpdir = tempfile.mkdtemp()
        try:
            system1 = DesireSystem(data_dir=tmpdir)
            system1.get_desire("curiosity").value = 9.0
            system1._save()

            system2 = DesireSystem(data_dir=tmpdir)
            assert system2.get_desire("curiosity").value == 9.0
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_stats(self):
        """Stats are returned."""
        tmpdir = tempfile.mkdtemp()
        try:
            system = DesireSystem(data_dir=tmpdir)
            stats = system.get_stats()
            assert "average" in stats
            assert "min" in stats
            assert "max" in stats
            assert len(stats["desires"]) == 8
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_desire_descriptions(self):
        """All desires have descriptions."""
        for name in DESIRE_DESCRIPTIONS:
            desc = DESIRE_DESCRIPTIONS[name]
            assert "description" in desc
            assert "scale" in desc
            assert len(desc["scale"]) == 11  # 0-10
