"""State-sharing regressions for spontaneous observation."""

from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.autonomous.spontaneous_observation import (
    SpontaneousObservationSystem,
)


class FakeStatusManager:
    def __init__(self) -> None:
        self.snapshot = {
            "pc-server": {"status": "online"},
            "browser-server": {"status": "offline"},
            "room-server": {"status": "unconfigured"},
        }

    def get_snapshot(self) -> dict[str, dict[str, str]]:
        return self.snapshot


class FakeDesireSystem:
    def get_all_desires(self) -> dict[str, SimpleNamespace]:
        return {
            "user_support": SimpleNamespace(expected_value=7.0, value=0.0),
        }


def test_capability_observation_uses_shared_status_and_emits_on_change_only(
    tmp_path,
) -> None:
    status = FakeStatusManager()
    observer = SpontaneousObservationSystem(
        status_manager=status,
        data_dir=str(tmp_path),
    )

    first = observer._observe_capabilities()
    second = observer._observe_capabilities()
    status.snapshot["browser-server"] = {"status": "online"}
    recovered = observer._observe_capabilities()
    status.snapshot["browser-server"] = {"status": "degraded"}
    degraded = observer._observe_capabilities()

    assert [item.description for item in first] == [
        "browser-server status changed to offline"
    ]
    assert second == []
    assert recovered == []
    assert [item.description for item in degraded] == [
        "browser-server status changed to degraded"
    ]


def test_desire_observation_does_not_repeat_unchanged_band(tmp_path) -> None:
    observer = SpontaneousObservationSystem(
        desire_system=FakeDesireSystem(),
        data_dir=str(tmp_path),
    )

    first = observer._observe_desires()
    second = observer._observe_desires()

    assert len(first) == 1
    assert first[0].related_desire == "user_support"
    assert second == []
