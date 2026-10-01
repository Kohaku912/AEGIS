from generated.aegis import common_pb2, room_server_pb2

import pytest

from aegis_room.providers import MockLightIrProvider, create_light_provider
from aegis_room.server import VERSION, RoomServer


def test_health_check_returns_online_version() -> None:
    servicer = RoomServer(light_provider=MockLightIrProvider())

    response = servicer.HealthCheck(common_pb2.HealthCheckRequest(server_id="room-server"), None)

    assert response.status.code == 0
    assert response.server_status == common_pb2.SERVER_STATUS_ONLINE
    # HealthCheck must report the module build tag (e.g. "0.1.4+pc11-ir-inmp441").
    assert response.version == VERSION
    assert response.version


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
            mode="eco",
        ),
        None,
    )

    assert response.status.code == 0
    state = provider.get_light_state("desk-light")
    assert state is not None
    assert state.power_on is True
    assert state.brightness == 128
    assert state.color_rgb == "#AA00FF"
    assert state.ir_code == "0xD001:0x21"
    assert provider.ir_log[-1]["command"] == 0x21
    assert provider.ir_log[-1]["address"] == 0xD001


def test_light_modes_map_to_expected_ir_codes() -> None:
    from aegis_room.light_ir import format_ir_code

    assert format_ir_code("all") == "0xD001:0x20"
    assert format_ir_code("eco") == "0xD001:0x21"
    assert format_ir_code("night") == "0xD001:0x22"
    assert format_ir_code("off") == "0xD001:0x23"


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


# ── The environment response must disclose that it is a fixture ───────────────


def test_get_environment_declares_that_it_returns_a_fixture() -> None:
    """``GetEnvironment`` returns hardcoded constants — the response must not present them
    as live measurements.

    The values look entirely plausible (22.5 °C, 45 %, 300 lx), so a client has no way to
    tell a fixture from a reading unless the response says so. The disclosure rides on
    ``Status.message``, the only free-text field ``GetEnvironmentResponse`` carries.
    """
    servicer = RoomServer(light_provider=MockLightIrProvider())

    response = servicer.GetEnvironment(room_server_pb2.GetEnvironmentRequest(), None)

    # Still a success: the disclosure is a note, not an error.
    assert response.status.code == 0
    assert response.status.message != "ok", (
        "a bare 'ok' presents the hardcoded fixture as a live environment"
    )
    assert "fixture" in response.status.message, (
        f"GetEnvironment's status reads {response.status.message!r} — it must disclose that "
        "the values are a hardcoded fixture rather than measurements"
    )


def test_get_environment_values_are_the_hardcoded_constants() -> None:
    """The disclosure above is a claim about the code — check it against the code.

    While these five values are constants, ``Status.message`` must call them a fixture. If a
    real environment provider is ever wired, the values stop being constant and this fails,
    forcing the disclosure to be revisited rather than left standing as a stale comfort.
    """
    servicer = RoomServer(light_provider=MockLightIrProvider())

    response = servicer.GetEnvironment(room_server_pb2.GetEnvironmentRequest(), None)

    assert (
        response.temperature_c,
        response.humidity_pct,
        response.brightness_lux,
        response.motion_detected,
        response.motion_zone,
    ) == (22.5, 45.0, 300.0, False, ""), (
        "GetEnvironment no longer returns the hardcoded constants — if a real environment "
        "provider was wired, update Status.message so it stops calling them a fixture"
    )
