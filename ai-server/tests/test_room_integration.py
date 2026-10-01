from __future__ import annotations

import json

from generated.aegis import common_pb2, room_server_pb2

from aegis_ai.capability_catalog import CapabilityCatalog
from aegis_ai.integrations.room.grpc_client import RoomServerGrpcClient


class _FakeRoomStub:
    def __init__(self) -> None:
        self.set_light_requests = []
        self.ir_requests = []

    def SetLight(self, request, timeout=None):
        self.set_light_requests.append(request)
        return room_server_pb2.SetLightResponse(status=common_pb2.Status(code=0, message="ok"))

    def SendIrCommand(self, request, timeout=None):
        self.ir_requests.append(request)
        return room_server_pb2.SendIrCommandResponse(status=common_pb2.Status(code=0, message="ir ok"))

    def GetEnvironment(self, request, timeout=None):
        return room_server_pb2.GetEnvironmentResponse(
            status=common_pb2.Status(
                code=0,
                message="hardcoded fixture: values are constants, not measurements",
            ),
            temperature_c=22.5,
            humidity_pct=45.0,
            brightness_lux=300.0,
            motion_detected=False,
            motion_zone="",
            timestamp_ms=123,
        )

    def GetDeviceStatus(self, request, timeout=None):
        state_json = json.dumps({"power_on": True, "brightness": 90, "provider": "mock"})
        return room_server_pb2.GetDeviceStatusResponse(
            status=common_pb2.Status(code=0, message="ok"),
            devices=[
                room_server_pb2.DeviceStatus(
                    device_id=request.device_ids[0],
                    device_type="light",
                    state_json=state_json,
                    online=True,
                    last_seen_ms=123,
                )
            ],
        )


def test_room_client_maps_set_light_to_grpc_and_optional_ir() -> None:
    client = RoomServerGrpcClient(timeout_seconds=1)
    stub = _FakeRoomStub()

    result = client._set_light(
        stub,
        {
            "device_id": "desk-light",
            "mode": "all",
            "brightness": 90,
            "color_temp_k": 4000,
            "color_rgb": "#AA00FF",
        },
    )

    assert result["success"] is True
    assert result["mode"] == "all"
    assert result["ir_code"] == "0xD001:0x20"
    assert result["device"]["state"]["provider"] == "mock"
    assert stub.set_light_requests[0].device_id == "desk-light"
    assert stub.set_light_requests[0].brightness == 90
    assert stub.set_light_requests[0].mode == "all"
    assert stub.ir_requests == []


def test_room_client_custom_ir_override_sends_ir_command() -> None:
    client = RoomServerGrpcClient(timeout_seconds=1)
    stub = _FakeRoomStub()

    result = client._set_light(
        stub,
        {
            "device_id": "desk-light",
            "power_on": True,
            "ir_code": "0xD001:0x21",
        },
    )

    assert result["success"] is True
    assert result["mode"] == "all"
    assert stub.ir_requests[0].ir_code == "0xD001:0x21"


def test_room_light_manifest_loads_without_approval() -> None:
    catalog = CapabilityCatalog(capabilities_dir="capabilities", apps_dir="apps")
    manifest = catalog.resolve("room-server.light.set_light")

    assert manifest is not None
    assert manifest.server_id == "room-server"
    assert manifest.requires_approval is False

    capabilities = {cap.id: cap for cap in catalog.to_tool_registry_capabilities()}
    assert capabilities["room-server.light.set_light"].requires_approval is False


def test_room_client_surfaces_the_environment_fixture_disclosure() -> None:
    """The fixture note must survive the client mapping — it is the only thing telling the
    agent that the environment values are not measurements.

    room-server puts the disclosure on ``Status.message``; ``_status_dict`` folds that into
    ``result["message"]``. If that folding ever stops, the disclosure dies here even though
    room-server still sends it — the agent would see a plausible 22.5 °C and no caveat.
    """
    client = RoomServerGrpcClient(timeout_seconds=1)

    result = client._get_environment(_FakeRoomStub(), {})

    assert result["success"] is True, "the disclosure is a note, not an error"
    assert "fixture" in result["message"], (
        f"the environment result reads message={result['message']!r} — the room-server "
        "fixture disclosure did not survive the client mapping"
    )
    assert result["temperature_c"] == 22.5

