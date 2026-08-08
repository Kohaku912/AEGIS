from __future__ import annotations

from aegis_ai.net.endpoint_resolver import (
    clear_endpoint_cache,
    normalize_mac,
    read_neighbor_table,
    resolve_by_mac,
    resolve_tcp_endpoint,
)


def test_normalize_mac() -> None:
    assert normalize_mac("20-86-A0-62-98-E0") == "20:86:a0:62:98:e0"
    assert normalize_mac("2086a06298e0") == "20:86:a0:62:98:e0"
    assert normalize_mac("bad") == ""


def test_resolve_tcp_endpoint_tries_candidates_and_caches(monkeypatch, tmp_path) -> None:
    clear_endpoint_cache()
    monkeypatch.setenv("AEGIS_ENDPOINT_CACHE_PATH", str(tmp_path / "endpoints.json"))
    monkeypatch.setenv("PC_SERVER_HOST", "192.168.50.176")
    monkeypatch.setenv("PC_SERVER_HOSTS", "192.168.50.195,pc-host.local")
    monkeypatch.setenv("PC_SERVER_MACS", "")
    monkeypatch.setenv("AEGIS_LAN_SCAN_ENABLED", "0")

    probed: list[str] = []

    def fake_probe(host: str, port: int, timeout: float) -> bool:
        probed.append(host)
        return host == "192.168.50.195"

    monkeypatch.setattr("aegis_ai.net.endpoint_resolver._probe", fake_probe)
    monkeypatch.setattr("aegis_ai.net.endpoint_resolver._resolve_hostnames", lambda xs: xs)
    monkeypatch.setattr("aegis_ai.net.endpoint_resolver.read_neighbor_table", lambda: {})
    monkeypatch.setattr("aegis_ai.net.endpoint_resolver._configured_macs", lambda _sid: [])

    resolved = resolve_tcp_endpoint("pc-server", port=50052, timeout=0.1, allow_lan_scan=False)
    assert resolved == ("192.168.50.195", 50052)
    assert "192.168.50.176" in probed
    assert "192.168.50.195" in probed

    probed.clear()
    resolved2 = resolve_tcp_endpoint("pc-server", port=50052, timeout=0.1, allow_lan_scan=False)
    assert resolved2 == ("192.168.50.195", 50052)
    assert probed[0] == "192.168.50.195"


def test_resolve_by_mac_uses_neighbor_table(monkeypatch, tmp_path) -> None:
    clear_endpoint_cache()
    monkeypatch.setenv("AEGIS_ENDPOINT_CACHE_PATH", str(tmp_path / "endpoints.json"))
    monkeypatch.setenv("ROOM_SERVER_MACS", "20:86:a0:62:98:e0,02:00:50:a7:b0:58")
    monkeypatch.setenv("ROOM_SERVER_HOST", "192.168.50.1")
    monkeypatch.setenv("AEGIS_LAN_SCAN_ENABLED", "0")

    monkeypatch.setattr(
        "aegis_ai.net.endpoint_resolver.read_neighbor_table",
        lambda: {"20:86:a0:62:98:e0": "192.168.50.120"},
    )
    monkeypatch.setattr(
        "aegis_ai.net.endpoint_resolver._probe",
        lambda host, port, timeout: host == "192.168.50.120" and port == 50055,
    )

    resolved = resolve_by_mac("room-server", port=50055, timeout=0.1, refresh_arp=False)
    assert resolved == ("192.168.50.120", 50055)


def test_resolve_tcp_endpoint_falls_back_to_mac(monkeypatch, tmp_path) -> None:
    clear_endpoint_cache()
    monkeypatch.setenv("AEGIS_ENDPOINT_CACHE_PATH", str(tmp_path / "endpoints.json"))
    monkeypatch.setenv("ROOM_SERVER_HOST", "192.168.50.1")
    monkeypatch.setenv("ROOM_SERVER_HOSTS", "")
    monkeypatch.setenv("ROOM_SERVER_MACS", "20:86:a0:62:98:e0")
    monkeypatch.setenv("AEGIS_LAN_SCAN_ENABLED", "0")

    monkeypatch.setattr("aegis_ai.net.endpoint_resolver._resolve_hostnames", lambda xs: xs)
    monkeypatch.setattr(
        "aegis_ai.net.endpoint_resolver.read_neighbor_table",
        lambda: {"20:86:a0:62:98:e0": "192.168.50.120"},
    )

    def fake_probe(host: str, port: int, timeout: float) -> bool:
        return host == "192.168.50.120"

    monkeypatch.setattr("aegis_ai.net.endpoint_resolver._probe", fake_probe)

    resolved = resolve_tcp_endpoint("room-server", port=50055, timeout=0.1, allow_lan_scan=False)
    assert resolved == ("192.168.50.120", 50055)


def test_status_manager_updates_host_when_endpoint_moves(monkeypatch) -> None:
    from aegis_ai.status.status_manager import StatusManager

    monkeypatch.setenv("PC_SERVER_HOST", "192.168.50.176")
    monkeypatch.setenv("ROOM_SERVER_ENABLED", "false")
    monkeypatch.setenv("DEV_SERVER_ENABLED", "false")
    monkeypatch.setenv("AEGIS_DISABLED_SERVERS", "browser-server,android-server,ai-server,dashboard")

    manager = StatusManager(timeout=0.2)
    monkeypatch.setattr(
        manager,
        "_resolve_endpoint",
        lambda server_id, host, port: ("192.168.50.195", 50052) if server_id == "pc-server" else None,
    )
    monkeypatch.setattr(manager, "_check_port", lambda host, port: host == "192.168.50.195" and port == 50052)

    snapshot = manager.check_now()
    assert snapshot["pc-server"]["status"] == "online"
    assert snapshot["pc-server"]["host"] == "192.168.50.195"


def test_read_neighbor_table_from_json(tmp_path, monkeypatch) -> None:
    path = tmp_path / "neighbors.json"
    path.write_text(
        json_dumps(
            {
                "neighbors": [
                    {"ip": "192.168.50.120", "mac": "20-86-A0-62-98-E0", "state": "REACHABLE"},
                    {"ip": "192.168.50.99", "mac": "aa:bb:cc:dd:ee:ff", "state": "FAILED"},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AEGIS_NEIGHBOR_TABLE_PATH", str(path))
    monkeypatch.setattr("aegis_ai.net.endpoint_resolver._parse_proc_arp", lambda _p: {})
    monkeypatch.setattr(
        "aegis_ai.net.endpoint_resolver.subprocess.run",
        lambda *_a, **_k: type("R", (), {"returncode": 1, "stdout": ""})(),
    )
    table = read_neighbor_table()
    assert table["20:86:a0:62:98:e0"] == "192.168.50.120"
    assert "aa:bb:cc:dd:ee:ff" not in table


def json_dumps(obj: object) -> str:
    import json

    return json.dumps(obj)
