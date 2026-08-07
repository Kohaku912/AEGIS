"""Resolve TCP endpoints for LAN servers whose DHCP IPs may change.

Candidate order:
1. In-memory last-known-good host for the server
2. Persisted cache (`data/endpoint_cache.json` by default)
3. `*_SERVER_HOST` primary env value
4. `*_SERVER_HOSTS` comma-separated candidates
5. Optional LAN /24 scan for the target port (pc-server / room-server only)

Successful probes update memory + disk cache so subsequent calls stay fast.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import threading
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.net.endpoint_resolver")

_LOCK = threading.RLock()
_MEMORY: dict[str, dict[str, Any]] = {}
_DEFAULT_CACHE = Path("data/endpoint_cache.json")
_SCAN_SERVERS = frozenset({"pc-server", "room-server"})
_LAST_SCAN_MS: dict[str, int] = {}
_SCAN_COOLDOWN_MS = int(os.getenv("AEGIS_LAN_SCAN_COOLDOWN_MS", "300000"))  # 5 minutes


def _cache_path() -> Path:
    raw = os.getenv("AEGIS_ENDPOINT_CACHE_PATH", "").strip()
    return Path(raw) if raw else _DEFAULT_CACHE


def _env_csv(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [part.strip() for part in raw.split(",") if part.strip()]


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _probe(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _resolve_hostnames(candidates: list[str]) -> list[str]:
    """Expand hostnames to IPs while keeping original names first."""
    expanded: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate not in seen:
            expanded.append(candidate)
            seen.add(candidate)
        try:
            infos = socket.getaddrinfo(candidate, None, family=socket.AF_INET, type=socket.SOCK_STREAM)
        except OSError:
            continue
        for info in infos:
            ip = info[4][0]
            if ip not in seen:
                expanded.append(ip)
                seen.add(ip)
    return expanded


def _guess_lan_prefix() -> str | None:
    explicit = os.getenv("AEGIS_LAN_SCAN_PREFIX", "").strip()
    if explicit:
        return explicit.rstrip(".")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
        parts = local_ip.split(".")
        if len(parts) == 4 and not local_ip.startswith("127."):
            return ".".join(parts[:3])
    except OSError:
        return None
    return None


def _scan_lan(port: int, timeout: float) -> list[str]:
    prefix = _guess_lan_prefix()
    if not prefix:
        return []
    found: list[str] = []
    # Keep scan bounded; typical home LAN /24.
    for last in range(1, 255):
        ip = f"{prefix}.{last}"
        if _probe(ip, port, timeout=min(timeout, 0.08)):
            found.append(ip)
    return found


def _load_disk_cache() -> dict[str, Any]:
    path = _cache_path()
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        logger.debug("Failed reading endpoint cache %s", path, exc_info=True)
    return {}


def _save_disk_cache(server_id: str, host: str, port: int) -> None:
    path = _cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = _load_disk_cache()
        data[server_id] = {
            "host": host,
            "port": port,
            "updated_at_ms": int(time.time() * 1000),
        }
        path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    except Exception:
        logger.debug("Failed writing endpoint cache %s", path, exc_info=True)


def _candidate_hosts(server_id: str, host_env: str, hosts_env: str | None) -> list[str]:
    prefix = server_id.upper().replace("-", "_")
    hosts_key = hosts_env or f"{prefix}_HOSTS"
    primary_key = host_env or f"{prefix}_HOST"

    ordered: list[str] = []
    with _LOCK:
        mem = _MEMORY.get(server_id)
        if mem and mem.get("host"):
            ordered.append(str(mem["host"]))

    disk = _load_disk_cache().get(server_id) or {}
    if disk.get("host"):
        ordered.append(str(disk["host"]))

    primary = os.getenv(primary_key, "").strip()
    if primary:
        ordered.append(primary)
    ordered.extend(_env_csv(hosts_key))

    # Stable hostname fallbacks for known devices.
    if server_id == "room-server":
        ordered.extend(["orangepi-room", "orangepi-room.local"])

    # Deduplicate preserving order.
    unique: list[str] = []
    seen: set[str] = set()
    for item in ordered:
        if item and item not in seen:
            unique.append(item)
            seen.add(item)
    return _resolve_hostnames(unique)


def resolve_tcp_endpoint(
    server_id: str,
    *,
    port: int,
    host_env: str | None = None,
    hosts_env: str | None = None,
    timeout: float = 0.4,
    allow_lan_scan: bool | None = None,
) -> tuple[str, int] | None:
    """Return a reachable (host, port) or None if all candidates fail."""
    prefix = server_id.upper().replace("-", "_")
    host_env = host_env or f"{prefix}_HOST"
    hosts_env = hosts_env or f"{prefix}_HOSTS"

    candidates = _candidate_hosts(server_id, host_env, hosts_env)
    for host in candidates:
        if _probe(host, port, timeout=timeout):
            with _LOCK:
                _MEMORY[server_id] = {"host": host, "port": port}
            _save_disk_cache(server_id, host, port)
            if host != os.getenv(host_env, ""):
                logger.info("Resolved %s endpoint to %s:%s", server_id, host, port)
            return host, port

    scan_enabled = (
        allow_lan_scan
        if allow_lan_scan is not None
        else _env_bool("AEGIS_LAN_SCAN_ENABLED", server_id in _SCAN_SERVERS)
    )
    now_ms = int(time.time() * 1000)
    last_scan = _LAST_SCAN_MS.get(server_id, 0)
    scan_due = (now_ms - last_scan) >= _SCAN_COOLDOWN_MS
    if scan_enabled and server_id in _SCAN_SERVERS and scan_due:
        _LAST_SCAN_MS[server_id] = now_ms
        logger.warning("Primary %s candidates unreachable; scanning LAN for :%s", server_id, port)
        for host in _scan_lan(port, timeout=timeout):
            with _LOCK:
                _MEMORY[server_id] = {"host": host, "port": port}
            _save_disk_cache(server_id, host, port)
            logger.info("LAN scan found %s at %s:%s", server_id, host, port)
            return host, port

    return None


def cached_endpoint(server_id: str) -> tuple[str, int] | None:
    with _LOCK:
        item = _MEMORY.get(server_id)
        if not item:
            return None
        return str(item["host"]), int(item["port"])


def clear_endpoint_cache(server_id: str | None = None) -> None:
    with _LOCK:
        if server_id is None:
            _MEMORY.clear()
        else:
            _MEMORY.pop(server_id, None)
