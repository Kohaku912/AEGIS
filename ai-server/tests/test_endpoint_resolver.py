from __future__ import annotations

from aegis_ai.net.endpoint_resolver import clear_endpoint_cache, resolve_tcp_endpoint


def test_resolve_tcp_endpoint_tries_candidates_and_caches(monkeypatch, tmp_path) -> None:
    clear_endpoint_cache()
    monkeypatch.setenv("AEGIS_ENDPOINT_CACHE_PATH", str(tmp_path / "endpoints.json"))
    monkeypatch.setenv("PC_SERVER_HOST", "192.168.50.176")
    monkeypatch.setenv("PC_SERVER_HOSTS", "192.168.50.195,pc-host.local")
    monkeypatch.setenv("AEGIS_LAN_SCAN_ENABLED", "0")

    probed: list[str] = []

    def fake_probe(host: str, port: int, timeout: float) -> bool:
        probed.append(host)
        return host == "192.168.50.195"

    monkeypatch.setattr("aegis_ai.net.endpoint_resolver._probe", fake_probe)
    monkeypatch.setattr("aegis_ai.net.endpoint_resolver._resolve_hostnames", lambda xs: xs)

    resolved = resolve_tcp_endpoint("pc-server", port=50052, timeout=0.1, allow_lan_scan=False)
    assert resolved == ("192.168.50.195", 50052)
    assert "192.168.50.176" in probed
    assert "192.168.50.195" in probed

    # Second call should prefer memory cache first.
    probed.clear()
    resolved2 = resolve_tcp_endpoint("pc-server", port=50052, timeout=0.1, allow_lan_scan=False)
    assert resolved2 == ("192.168.50.195", 50052)
    assert probed[0] == "192.168.50.195"


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
