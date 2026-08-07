from generated.aegis import common_pb2, room_server_pb2

import pytest

from aegis_room.providers import MockLightIrProvider, create_light_provider
from aegis_room.server import RoomServer


def test_health_check_returns_online_version() -> None:
    servicer = RoomServer(light_provider=MockLightIrProvider())

    response = servicer.HealthCheck(common_pb2.HealthCheckRequest(server_id="room-server"), None)

    assert response.status.code == 0
    assert response.server_status == common_pb2.SERVER_STATUS_ONLINE
    assert "mock-light" in response.version


def test_set_light_with_mock_provider_records_state() -> None:
    provider = MockLightIrProvider()
    servicer = RoomServer(light_provider=provider)

    response = servicer.SetLight(
        room_server_pb2.SetLightRequest(
            device_id="desk-light",
            power_on=True,
            brightness=128,
            color_temp_k=4200,
            color_rgb="#AA00FF",
        ),
        None,
    )

    assert response.status.code == 0
    state = provider.get_light_state("desk-light")
    assert state is not None
    assert state.power_on is True
    assert state.brightness == 128
    assert state.color_rgb == "#AA00FF"
    assert provider.ir_log[-1]["device_id"] == "desk-light"


def test_invalid_brightness_and_repeat_return_safe_errors() -> None:
    servicer = RoomServer(light_provider=MockLightIrProvider())

    light_response = servicer.SetLight(room_server_pb2.SetLightRequest(power_on=True, brightness=999), None)
    ir_response = servicer.SendIrCommand(
        room_server_pb2.SendIrCommandRequest(device_type="light", ir_code="light_power", repeat=99),
        None,
    )

    assert light_response.status.code == 400
    assert "brightness" in light_response.status.message
    assert ir_response.status.code == 400
    assert "repeat" in ir_response.status.message


def test_production_rejects_disabled_or_mock_room_provider(monkeypatch) -> None:
    monkeypatch.setenv("AEGIS_RUNTIME_MODE", "production")

    monkeypatch.setenv("AEGIS_ROOM_LIGHT_PROVIDER", "disabled")
    with pytest.raises(RuntimeError, match="disabled"):
        create_light_provider()

    monkeypatch.setenv("AEGIS_ROOM_LIGHT_PROVIDER", "mock")
    with pytest.raises(RuntimeError, match="mock"):
        create_light_provider()
