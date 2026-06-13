"""Tests for Desire System — frustration, decay, clamping, snapshot, persistence."""

from __future__ import annotations

import json
import shutil
import tempfile
import time

import pytest

from aegis_ai.desire.desire_system import (
    DEFAULT_DESIRE_DIMENSIONS,
    DESIRE_DESCRIPTIONS,
    DesireDimension,
    DesireSnapshot,
    DesireSystem,
    _clamp,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestDesireDimension:
    def test_frustration_when_below_expected(self):
        dim = DesireDimension(name="test", value=3.0, expected_value=7.0)
        assert dim.frustration == pytest.approx(4.0)

    def test_frustration_zero_when_at_expected(self):
        dim = DesireDimension(name="test", value=7.0, expected_value=7.0)
        assert dim.frustration == pytest.approx(0.0)

    def test_frustration_zero_when_above_expected(self):
        dim = DesireDimension(name="test", value=9.0, expected_value=7.0)
        assert dim.frustration == pytest.approx(0.0)


class TestClamp:
    def test_clamp_within_range(self):
        assert _clamp(5.0) == pytest.approx(5.0)

    def test_clamp_below_zero(self):
        assert _clamp(-1.0) == pytest.approx(0.0)

    def test_clamp_above_ten(self):
        assert _clamp(12.0) == pytest.approx(10.0)

    def test_clamp_at_boundaries(self):
        assert _clamp(0.0) == pytest.approx(0.0)
        assert _clamp(10.0) == pytest.approx(10.0)


class TestDesireSystemInit:
    def test_creates_ten_desires(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        assert len(system.get_all_desires()) == 10

    def test_all_expected_names_present(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        expected = set(DEFAULT_DESIRE_DIMENSIONS.keys())
        assert set(system.get_all_desires().keys()) == expected

    def test_custom_initial_values(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir, initial_values={"curiosity": 8.5})
        assert system.get_desire("curiosity").value == pytest.approx(8.5)

    def test_initial_values_clamped(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir, initial_values={"curiosity": -3.0})
        assert system.get_desire("curiosity").value == pytest.approx(0.0)

        system2 = DesireSystem(data_dir=tmpdir, initial_values={"curiosity": 15.0})
        # New instance with fresh dir
        d2 = tempfile.mkdtemp()
        try:
            s2 = DesireSystem(data_dir=d2, initial_values={"curiosity": 15.0})
            assert s2.get_desire("curiosity").value == pytest.approx(10.0)
        finally:
            shutil.rmtree(d2, ignore_errors=True)


class TestFrustration:
    def test_frustration_computed_correctly(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        curiosity = system.get_desire("curiosity")
        assert curiosity is not None
        # Default value=5.0, expected=7.0 → frustration=2.0
        assert curiosity.frustration == pytest.approx(2.0)

    def test_frustration_zero_when_value_exceeds_expected(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir, initial_values={"curiosity": 9.0})
        assert system.get_desire("curiosity").frustration == pytest.approx(0.0)

    def test_frustration_dict(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        frusts = system.get_frustrations()
        assert len(frusts) == 10
        for v in frusts.values():
            assert v >= 0.0


class TestDecay:
    def test_decay_reduces_value(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        curiosity = system.get_desire("curiosity")
        initial_value = curiosity.value
        curiosity.last_updated_at = int(time.time() * 1000) - 3_600_000  # 1 hour ago
        system.apply_decay()
        assert curiosity.value < initial_value

    def test_decay_respects_rate(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        curiosity = system.get_desire("curiosity")
        curiosity.value = 8.0
        curiosity.last_updated_at = int(time.time() * 1000) - 3_600_000  # 1 hour
        rate = curiosity.decay_rate_per_hour
        system.apply_decay()
        assert curiosity.value == pytest.approx(8.0 - rate)

    def test_decay_does_not_go_below_zero(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        curiosity = system.get_desire("curiosity")
        curiosity.value = 0.1
        curiosity.last_updated_at = int(time.time() * 1000) - 360 * 3_600_000  # 360 hours
        system.apply_decay()
        assert curiosity.value == pytest.approx(0.0)

    def test_decay_with_explicit_now(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        curiosity = system.get_desire("curiosity")
        base = 1_000_000_000_000
        curiosity.last_updated_at = base
        curiosity.value = 5.0
        system.apply_decay(now_ms=base + 3_600_000)  # 1 hour later
        assert curiosity.value == pytest.approx(5.0 - curiosity.decay_rate_per_hour)

    def test_decay_skips_hidden(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        curiosity = system.get_desire("curiosity")
        curiosity.hidden = True
        curiosity.value = 5.0
        curiosity.last_updated_at = int(time.time() * 1000) - 10 * 3_600_000
        system.apply_decay()
        assert curiosity.value == pytest.approx(5.0)


class TestUpdateValue:
    def test_update_clamps_value(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        system.update_value("curiosity", 15.0)
        assert system.get_desire("curiosity").value == pytest.approx(10.0)

    def test_update_records_history(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        system.update_value("curiosity", 8.0, reason="test")
        history = system.get_desire("curiosity").update_history
        assert len(history) == 1
        assert history[0]["new"] == pytest.approx(8.0)
        assert history[0]["reason"] == "test"

    def test_update_unknown_desire_raises(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        with pytest.raises(KeyError):
            system.update_value("nonexistent", 5.0)

    def test_history_trimming(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        for i in range(25):
            system.update_value("curiosity", float(i % 10))
        assert len(system.get_desire("curiosity").update_history) <= 20


class TestSnapshot:
    def test_snapshot_has_all_fields(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        snap = system.create_snapshot()
        assert isinstance(snap, DesireSnapshot)
        assert snap.timestamp > 0
        assert snap.average_frustration >= 0
        assert snap.max_frustration >= 0
        assert isinstance(snap.top_unsatisfied_desires, list)
        assert len(snap.desires) == 10

    def test_snapshot_max_frustration_is_correct(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        system.update_value("system_safety", 1.0)  # expected=9 → frustration=8
        snap = system.create_snapshot()
        assert snap.max_frustration == pytest.approx(8.0)
        assert snap.top_unsatisfied_desires[0] == "system_safety"

    def test_snapshot_top_unsorted_descending(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        system.update_value("curiosity", 2.0)
        system.update_value("purpose", 3.0)
        snap = system.create_snapshot()
        frusts = [system.get_desire(n).frustration for n in snap.top_unsatisfied_desires]
        assert frusts == sorted(frusts, reverse=True)

    def test_snapshot_excludes_hidden_from_frustration_stats(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        system.get_desire("maintenance").hidden = True
        system.get_desire("maintenance").value = 0.0
        snap = system.create_snapshot()
        # hidden desires should not appear in top_unsatisfied
        assert "maintenance" not in snap.top_unsatisfied_desires


class TestPersistence:
    def test_save_and_reload_values(self, tmpdir):
        system1 = DesireSystem(data_dir=tmpdir)
        system1.update_value("curiosity", 9.0)
        system1.save()

        system2 = DesireSystem(data_dir=tmpdir)
        assert system2.get_desire("curiosity").value == pytest.approx(9.0)

    def test_save_and_reload_expected_value(self, tmpdir):
        system1 = DesireSystem(data_dir=tmpdir)
        system1.set_expected_value("curiosity", 8.5)
        system1.save()

        system2 = DesireSystem(data_dir=tmpdir)
        assert system2.get_desire("curiosity").expected_value == pytest.approx(8.5)

    def test_save_and_reload_last_updated_at(self, tmpdir):
        system1 = DesireSystem(data_dir=tmpdir)
        specific_ts = 1_700_000_000_000
        system1.get_desire("curiosity").last_updated_at = specific_ts
        system1.save()

        system2 = DesireSystem(data_dir=tmpdir)
        assert system2.get_desire("curiosity").last_updated_at == specific_ts

    def test_save_and_reload_history(self, tmpdir):
        system1 = DesireSystem(data_dir=tmpdir)
        system1.update_value("curiosity", 8.0, reason="learned something")
        system1.save()

        system2 = DesireSystem(data_dir=tmpdir)
        history = system2.get_desire("curiosity").update_history
        assert len(history) >= 1
        assert history[-1]["reason"] == "learned something"

    def test_save_and_reload_hidden_flag(self, tmpdir):
        system1 = DesireSystem(data_dir=tmpdir)
        system1.get_desire("maintenance").hidden = True
        system1.save()

        system2 = DesireSystem(data_dir=tmpdir)
        assert system2.get_desire("maintenance").hidden is True

    def test_save_and_reload_decay_rate(self, tmpdir):
        system1 = DesireSystem(data_dir=tmpdir)
        system1.get_desire("curiosity").decay_rate_per_hour = 0.5
        system1.save()

        system2 = DesireSystem(data_dir=tmpdir)
        assert system2.get_desire("curiosity").decay_rate_per_hour == pytest.approx(0.5)

    def test_persistence_file_is_valid_json(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        system.save()
        path = system._state_path()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert "desires" in data
        assert "saved_at_ms" in data


class TestGetContext:
    def test_context_includes_visible_desires(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        ctx = system.get_context()
        assert "curiosity" in ctx
        assert "system_safety" in ctx

    def test_context_excludes_hidden(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        system.get_desire("maintenance").hidden = True
        ctx = system.get_context()
        assert "maintenance" not in ctx

    def test_context_shows_frustration(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        ctx = system.get_context()
        assert "frustration" in ctx


class TestGenerateTasks:
    def test_tasks_for_desires_below_expected(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir, initial_values={"curiosity": 2.0})
        tasks = system.generate_tasks()
        curiosity_tasks = [t for t in tasks if t["desire"] == "curiosity"]
        assert len(curiosity_tasks) == 1
        assert curiosity_tasks[0]["gap"] == pytest.approx(5.0)

    def test_no_tasks_when_at_expected(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir, initial_values={"curiosity": 7.0})
        tasks = system.generate_tasks()
        assert not any(t["desire"] == "curiosity" for t in tasks)

    def test_tasks_sorted_by_priority(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        tasks = system.generate_tasks()
        priorities = [t["priority"] for t in tasks]
        assert priorities == sorted(priorities, reverse=True)

    def test_tasks_include_frustration(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        tasks = system.generate_tasks()
        for t in tasks:
            assert "frustration" in t
            assert t["frustration"] >= 0


class TestBackwardCompatibility:
    def test_desire_alias(self):
        assert DesireDimension is not None

    def test_desire_descriptions_exported(self):
        assert isinstance(DESIRE_DESCRIPTIONS, dict)
        assert len(DESIRE_DESCRIPTIONS) == 10

    def test_get_stats_has_frustrations(self, tmpdir):
        system = DesireSystem(data_dir=tmpdir)
        stats = system.get_stats()
        assert "frustrations" in stats
        assert "average_frustration" in stats
        assert "max_frustration" in stats
