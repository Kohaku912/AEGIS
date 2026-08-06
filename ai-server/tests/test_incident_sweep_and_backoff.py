"""Tests for failed-task incident sweep and no-action exponential backoff."""

from __future__ import annotations

import time

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.task.task_manager import TaskManager, _incident_fingerprint, _is_unrecoverable_incident


def test_incident_fingerprint_collapses_browser_timeouts() -> None:
    a = {"error": "Event handler BrowserSession.on_BrowserStartEvent timed out", "source": "autonomous"}
    b = {"error": "Event handler browser_use.browser.watchdog_base.BrowserSession.on_BrowserStartEvent", "source": "autonomous"}
    assert _incident_fingerprint(a) == _incident_fingerprint(b)
    assert _is_unrecoverable_incident(a["error"])


def test_sweep_stale_incidents_resolves_duplicates_and_unrecoverable(tmp_path) -> None:
    tm = TaskManager(data_dir=str(tmp_path / "tasks"))
    now = int(time.time() * 1000)

    def _fail(title: str, error: str) -> str:
        task = tm.create_task(title=title, goal=title, source="autonomous")
        tm.start_task(task["task_id"])
        tm.fail_task(task["task_id"], error=error)
        return task["task_id"]

    kept = _fail("unique real failure", "User packing list was not completed")
    dup_ids = [
        _fail(f"browser-{index}", "Event handler BrowserSession.on_BrowserStartEvent timed out after 30.0s")
        for index in range(5)
    ]
    stale = _fail("old timeout", "HTTP execution error: timed out")
    with tm._lock:
        tm._tasks[stale]["updated_at"] = now - (2 * 24 * 60 * 60 * 1000)
        tm._save()

    result = tm.sweep_stale_incidents(now_ms=now, max_age_ms=24 * 60 * 60 * 1000)
    assert result["resolved_count"] >= 5
    assert tm.get_task(kept)["incident_status"] == "open"
    open_browser = [task_id for task_id in dup_ids if tm.get_task(task_id)["incident_status"] == "open"]
    assert len(open_browser) <= 1
    assert tm.get_task(stale)["incident_status"] == "resolved"
    assert tm.get_task(stale)["incident_resolution"] == "auto_resolved_stale_age"


def test_no_action_backoff_grows_exponentially(tmp_path) -> None:
    loop = AutonomousLoop(data_dir=str(tmp_path / "auto"))
    assert loop._no_action_backoff_ms() == 0
    loop._consecutive_no_action = 1
    assert loop._no_action_backoff_ms() == 60_000
    loop._consecutive_no_action = 2
    assert loop._no_action_backoff_ms() == 120_000
    loop._consecutive_no_action = 3
    assert loop._no_action_backoff_ms() >= 240_000
    loop._consecutive_no_action = 10
    # Must not inherit AEGIS_MIN_LLM_INTERVAL (30m); cap at 10 minutes.
    assert loop._no_action_backoff_ms() == 600_000


def test_decide_next_interval_uses_no_action_backoff(tmp_path) -> None:
    from aegis_ai.desire.desire_system import DesireSystem

    desire = DesireSystem(data_dir=str(tmp_path / "desire"))
    for name, obj in desire.get_all_desires().items():
        if obj.hidden:
            continue
        obj.pressure = 8.0
        if desire._pressure_engine is not None:
            desire._pressure_engine._pressures[name] = 8.0
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "auto"))
    loop._consecutive_no_action = 4
    interval = loop._decide_next_interval([])
    # Unmet high pressure retries within the unmet-desire cap (default 5m), not 30m.
    assert 60 <= interval <= 300


def test_high_pressure_bypasses_long_next_run_schedule(tmp_path) -> None:
    from aegis_ai.desire.desire_system import DesireSystem

    desire = DesireSystem(data_dir=str(tmp_path / "desire"))
    for name, obj in desire.get_all_desires().items():
        if obj.hidden:
            continue
        obj.pressure = 10.0
        if desire._pressure_engine is not None:
            desire._pressure_engine._pressures[name] = 10.0
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "auto"))
    now = int(time.time() * 1000)
    loop._last_run_ms = now - 400_000  # last cycle > unmet retry window
    loop._next_run_ms = now + 1_500_000  # still blocked by old 30m schedule
    loop._last_skip_reason = "no_valid_tasks"
    assert loop._pressure_due() is True
    assert loop._unmet_desire_retry_due(now) is True
    sleep_s = loop._compute_idle_sleep_seconds(now)
    assert sleep_s <= 5.0



def test_desire_eta_and_cycle_pressure_release(tmp_path) -> None:
    from aegis_ai.desire.desire_system import DesireSystem

    desire = DesireSystem(data_dir=str(tmp_path / "desire"))
    for name, obj in desire.get_all_desires().items():
        if obj.hidden:
            continue
        obj.pressure = 0.0
        if desire._pressure_engine is not None:
            desire._pressure_engine._pressures[name] = 0.0
    eta = desire.seconds_until_threshold(5.0)
    # 5.0 pressure / 10 per hour = 0.5h = 1800s
    assert 1700 <= eta <= 1900

    for name, obj in desire.get_all_desires().items():
        if obj.hidden:
            continue
        obj.pressure = 9.0
        if desire._pressure_engine is not None:
            desire._pressure_engine._pressures[name] = 9.0
    assert desire.seconds_until_threshold(5.0) == 0.0
    desire.release_cycle_pressure(effectiveness=1.0)
    for name, obj in desire.get_all_desires().items():
        if obj.hidden:
            continue
        assert obj.pressure < 5.0


def test_autonomous_loop_no_60s_idle_poll(tmp_path) -> None:
    from aegis_ai.desire.desire_system import DesireSystem

    desire = DesireSystem(data_dir=str(tmp_path / "desire"))
    for name, obj in desire.get_all_desires().items():
        if obj.hidden:
            continue
        obj.pressure = 0.0
        if desire._pressure_engine is not None:
            desire._pressure_engine._pressures[name] = 0.0
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "auto"))
    now = int(time.time() * 1000)
    loop._next_run_ms = now + 1_800_000
    sleep_s = loop._compute_idle_sleep_seconds(now)
    assert sleep_s >= 60
    assert loop._min_execution_interval_ms < 60_000
    assert loop._observation_interval_ms >= 300_000


def test_desire_trigger_not_blocked_by_llm_gate(tmp_path) -> None:
    from aegis_ai.desire.desire_system import DesireSystem

    desire = DesireSystem(data_dir=str(tmp_path / "desire"))
    for name, obj in desire.get_all_desires().items():
        if obj.hidden:
            continue
        obj.pressure = 6.0
        if desire._pressure_engine is not None:
            desire._pressure_engine._pressures[name] = 6.0
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "auto"))
    now = int(time.time() * 1000)
    loop._last_llm_call_ms = now
    loop._last_skip_reason = "llm_interval_gate (1700s remaining)"
    loop._next_run_ms = now + 1_700_000
    loop._consecutive_no_action = 10
    assert loop._pressure_due() is True
    # Desire fire must proceed; gates are skipped inside execute when pressure due.
    calls: list[bool] = []

    def _fake_generate(low_desires):
        calls.append(True)
        loop._last_decision = "no_action"
        loop._last_llm_call_ms = int(time.time() * 1000)
        return []

    loop._generate_tasks = _fake_generate  # type: ignore[method-assign]
    loop._llm = object()
    loop._execute_cycle(force_desire=True)
    assert calls == [True]
    assert loop._consecutive_no_action == 0 or loop._last_decision == "no_action"


def test_apply_decay_persists_pressure(tmp_path) -> None:
    from aegis_ai.desire.desire_system import DesireSystem

    desire = DesireSystem(data_dir=str(tmp_path / "desire"))
    now = int(time.time() * 1000)
    for name, obj in desire.get_all_desires().items():
        if obj.hidden:
            continue
        obj.pressure = 0.0
        obj.last_updated_at = now - 1_800_000  # 30 minutes ago
        if desire._pressure_engine is not None:
            desire._pressure_engine._pressures[name] = 0.0
    desire.apply_decay(now_ms=now)
    reloaded = DesireSystem(data_dir=str(tmp_path / "desire"))
    pressures = [d.pressure for d in reloaded.get_all_desires().values() if not d.hidden]
    assert pressures
    assert max(pressures) >= 4.5
